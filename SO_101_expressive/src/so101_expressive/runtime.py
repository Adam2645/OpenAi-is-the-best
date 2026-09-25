from __future__ import annotations

import queue
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Protocol

import numpy as np

from .behavior.arbiter import Arbiter, Decision
from .behavior.jaw import JawBehavior
from .behavior.manipulation import PickPlaceSkill
from .behavior.planner import BehaviorPlanner, IntentResult
from .behavior.tracking import PersonObservation, TrackingBehavior
from .config import Settings
from .conversation.base import (
    AudioChunk,
    IntentCancelled,
    IntentRequest,
    Interrupted,
    StatusChanged,
    Transcript,
    TurnComplete,
    TurnStarted,
)
from .conversation.tools import validate_call
from .motion.controller import ControllerReport, SafeMotionController
from .motion.kinematics import So101Kinematics
from .motion.limits import GRIPPER, NEUTRAL_POSE, build_limits, ranges_from_model
from .sim.mujoco_sim import MujocoSim
from .state import ApiStatus, ConversationPhase, GripEvidence, PersonStatus, RobotState, StateJournal
from .util import LatestValue


# stan audio z wątku mikrofonu trafia do pętli ruchu jako jedna spójna wartość
@dataclass(frozen=True)
class AudioStatus:
    user_speaking: bool = False
    music: bool = False
    music_score: float = 0.0
    music_bpm: float = 0.0
    utterance: int = 0


# polecenia z klawiatury i testów idą tą samą kolejką co zdarzenia rozmowy, więc kolejność jest zachowana
@dataclass(frozen=True)
class Command:
    name: str
    args: dict = field(default_factory=dict)


# minimalny kontrakt bufora odtwarzania, dzięki któremu testy mogą użyć wirtualnego głośnika
class PlaybackLike(Protocol):
    # poziom dźwięku w chwili wyjścia z głośnika steruje szczęką
    def level_at(self, t: float) -> float: ...

    # informacja o trwającym odtwarzaniu rozdziela mówienie od słuchania
    def is_playing(self, t: float) -> bool: ...

    # zaległe próbki oznaczają, że wypowiedź jeszcze się nie skończyła
    def has_pending(self) -> bool: ...

    # wyciszenie realizuje opcję milczenia przy trzymaniu obiektu
    def set_muted(self, muted: bool) -> None: ...

    # opróżnienie bufora obsługuje przerwanie wypowiedzi
    def flush(self) -> None: ...


# zapis jednego kroku pętli pozwala testom sprawdzać limity ruchu i decyzje arbitra
@dataclass(frozen=True)
class TickRecord:
    t: float
    q_cmd: np.ndarray
    v_cmd: np.ndarray
    q_meas: np.ndarray
    decision: Decision
    report: ControllerReport
    state: RobotState


# pętla ciała łączy stan, planistę, arbitra, bezpieczny sterownik i symulację w jednym deterministycznym kroku
class BodyRuntime:
    # wszystkie zależności są wstrzykiwane, więc ta sama pętla działa w aplikacji i w testach scenariuszy
    def __init__(
        self,
        settings: Settings,
        sim: MujocoSim,
        kin: So101Kinematics,
        planner: BehaviorPlanner,
        arbiter: Arbiter,
        controller: SafeMotionController,
        playback: PlaybackLike,
        person: LatestValue[PersonObservation] | None = None,
        audio: LatestValue[AudioStatus] | None = None,
        journal: StateJournal | None = None,
        budget_fn: Callable[[], object] | None = None,
        intent_responder: Callable[[IntentRequest, IntentResult], None] | None = None,
        special_intents: dict[str, Callable[[IntentRequest, RobotState], IntentResult | None]] | None = None,
    ) -> None:
        self.settings = settings
        self.sim = sim
        self.kin = kin
        self.planner = planner
        self.arbiter = arbiter
        self.controller = controller
        self.playback = playback
        self.person = person or LatestValue()
        self.audio = audio or LatestValue(AudioStatus())
        self.journal = journal or StateJournal()
        self.budget_fn = budget_fn
        self.intent_responder = intent_responder
        self.special_intents = dict(special_intents or {})
        self.dt = 1.0 / settings.control_hz
        self.state = RobotState()
        self._inbox: queue.Queue = queue.Queue()
        self._turn_open = False
        self._last_role = ""
        self._text_turn = -1
        self._evidence: GripEvidence = sim.grasp_evidence(float(controller.q[GRIPPER]))
        self._snapshot = self.state.snapshot()
        self._snap_lock = threading.Lock()
        self.intent_log: deque[tuple[float, IntentRequest, IntentResult]] = deque(maxlen=200)
        self.command_log: deque[tuple[float, Command, IntentResult | None]] = deque(maxlen=200)
        self.last_record: TickRecord | None = None
        self.overruns = 0

    # wątki rozmowy, audio i interfejsu przekazują zdarzenia wyłącznie przez tę kolejkę
    def post(self, item: object) -> None:
        self._inbox.put(item)

    # interfejs i testy czytają kopię stanu z ostatniego pełnego kroku
    def snapshot(self) -> RobotState:
        with self._snap_lock:
            return self._snapshot

    # przeterminowana obserwacja z kamery jest traktowana jako niepewna, więc śledzenie nie rusza ramieniem
    def _observation(self, t: float) -> PersonObservation:
        obs = self.person.get()
        if obs is None:
            return PersonObservation(PersonStatus.ABSENT, t)
        if t - obs.t > 0.5:
            status = PersonStatus.ABSENT if obs.status is PersonStatus.ABSENT else PersonStatus.UNCERTAIN
            return PersonObservation(status, t, obs.u, obs.v, obs.size, 0.0)
        return obs

    # awaryjny stop jest zatrzaskiwany i zwalniany wyłącznie jawnym poleceniem użytkownika
    def _trigger_estop(self, t: float, reason: str) -> None:
        self.state.estop = True
        self.state.estop_reason = reason
        self.planner.on_estop(t)

    # polecenia lokalne mają te same reguły co prośby modelu, bo przechodzą przez planistę
    def _command(self, cmd: Command, t: float) -> None:
        st = self.state
        result: IntentResult | None = None
        if cmd.name == "estop":
            self._trigger_estop(t, str(cmd.args.get("reason", "polecenie użytkownika")))
        elif cmd.name == "reset":
            if st.estop:
                st.estop = False
                st.estop_reason = ""
                self.arbiter.rebase(self.controller.q, t)
        elif cmd.name == "pick":
            result = self.planner.request_pick(t, st, self.sim.joint_q())
        elif cmd.name == "place":
            result = self.planner.request_place(t, st, self.sim.joint_q())
        elif cmd.name == "gesture":
            result = self.planner.request_gesture(str(cmd.args.get("name", "")), str(cmd.args.get("intensity", "normal")), t, st)
        elif cmd.name == "dance":
            result = self.planner.request_dance(str(cmd.args.get("duration", "short")), t, st)
        elif cmd.name == "stop_motion":
            result = self.planner.soft_stop(t)
        elif cmd.name == "mock_grip":
            self.planner.set_mock_grip(cmd.args.get("phase"))
        elif cmd.name == "reset_cube":
            if self.planner.skill is None or not self.planner.skill.active:
                self.sim.reset_cube()
        self.command_log.append((t, cmd, result))

    # prośby modelu są walidowane w jednym miejscu, a wynik wraca od razu albo później, gdy obsługa specjalna odroczy decyzję
    def _intent(self, item: IntentRequest, t: float) -> None:
        ok, parsed = validate_call(item.name, item.args)
        if not ok:
            result = IntentResult(False, str(parsed))
        elif item.name in self.special_intents:
            result = self.special_intents[item.name](item, self.state.snapshot())
            if result is None:
                return
        else:
            result = self.planner.handle_intent(item.name, parsed, t, self.state, self.sim.joint_q(), item.call_id)
        self.intent_log.append((t, item, result))
        if self.intent_responder is not None:
            self.intent_responder(item, result)

    # opróżnienie skrzynki na początku kroku daje spójny stan dla całego planowania
    def _drain(self, t: float) -> None:
        st = self.state
        while True:
            try:
                item = self._inbox.get_nowait()
            except queue.Empty:
                return
            if isinstance(item, Command):
                self._command(item, t)
            elif isinstance(item, (TurnStarted, AudioChunk)):
                self._turn_open = True
            elif isinstance(item, TurnComplete):
                self._turn_open = False
            elif isinstance(item, Interrupted):
                self._turn_open = False
                self.playback.flush()
                self.planner.on_interrupted(t)
            elif isinstance(item, Transcript):
                if item.role == "user":
                    if self._last_role != "user" or self._text_turn != st.user_turn:
                        st.last_user_text = ""
                        self._text_turn = st.user_turn
                    st.last_user_text = (st.last_user_text + item.text)[-200:]
                else:
                    if self._last_role != item.role:
                        st.last_robot_text = ""
                    st.last_robot_text = (st.last_robot_text + item.text)[-200:]
                self._last_role = item.role
            elif isinstance(item, IntentRequest):
                self._intent(item, t)
            elif isinstance(item, IntentCancelled):
                self.planner.cancel_calls(item.ids, t)
            elif isinstance(item, StatusChanged):
                st.api = item.status
                st.api_detail = item.detail

    # jeden krok sterowania od odczytu wejść po ruch symulacji, wywoływany w czasie rzeczywistym lub w testach
    def step(self, t: float) -> TickRecord:
        st = self.state
        dt = self.dt
        st.t = t
        self._drain(t)
        obs = self._observation(t)
        aud = self.audio.get() or AudioStatus()
        st.user_speaking = aud.user_speaking
        st.music = aud.music
        st.music_score = aud.music_score
        st.music_bpm = aud.music_bpm
        st.user_turn = aud.utterance
        muted = self.settings.mute_speech_while_holding and st.gripper_locked
        st.speech_muted = muted
        self.playback.set_muted(muted)
        playing = self.playback.is_playing(t)
        pending = self.playback.has_pending()
        st.audio_playing = playing and not muted
        level = 0.0 if muted else float(self.playback.level_at(t + self.settings.jaw_lead_s))
        st.audio_level = level
        available = st.api in (ApiStatus.CONNECTED, ApiStatus.LOCAL)
        if self._turn_open or pending or playing:
            st.conversation = ConversationPhase.ROBOT_SPEAKING
        elif not available:
            st.conversation = ConversationPhase.INACTIVE
        elif st.user_speaking:
            st.conversation = ConversationPhase.USER_SPEAKING
        else:
            st.conversation = ConversationPhase.LISTENING
        q_meas = self.sim.joint_q()
        plan = self.planner.plan(t, dt, st, obs, level, q_meas, self._evidence)
        st.grip = plan.grip
        st.manipulation = plan.manipulation
        st.grip_evidence = plan.evidence
        st.gesture = plan.gesture
        st.dancing = plan.dancing
        st.tracking = plan.tracking
        st.jaw_active = plan.jaw_active
        st.gaze_target = plan.gaze_target
        st.person = obs.status
        st.person_confidence = obs.confidence
        decision = self.arbiter.decide(
            t, plan.requests, estop=st.estop, gripper_locked=st.gripper_locked,
            hold_value=plan.hold_value, q_current=self.controller.q,
        )
        report = self.controller.step(decision.q_des, decision.speed_scale, estop=st.estop, mode=decision.mode)
        if report.clamped or report.nonfinite:
            st.limit_events += 1
        if report.workspace_blocked:
            st.workspace_blocks += 1
        st.suppressed = decision.suppressed
        self.sim.apply(self.controller.q)
        try:
            self.sim.step(dt)
        except FloatingPointError:
            self._trigger_estop(t, "niestabilna symulacja")
            self.sim.reset(self.controller.q)
        self._evidence = self.sim.grasp_evidence(float(self.controller.q[GRIPPER]))
        self.sim.set_person_marker(plan.gaze_target, obs.status)
        if self.budget_fn is not None:
            budget = self.budget_fn()
            st.budget_session_pln = budget.session_pln
            st.budget_total_pln = budget.total_pln
            st.budget_session_limit_pln = budget.session_limit_pln
            st.budget_total_limit_pln = budget.total_limit_pln
            st.budget_warning = budget.warning
            st.budget_blocked = budget.blocked
        self.journal.observe(st)
        snap = st.snapshot()
        with self._snap_lock:
            self._snapshot = snap
        record = TickRecord(t, self.controller.q.copy(), self.controller.v.copy(), q_meas, decision, report, snap)
        self.last_record = record
        return record

    # pętla czasu rzeczywistego nadrabia opóźnienia krokami o stałym dt i liczy przekroczenia
    def run(self, stop: threading.Event, clock: Callable[[], float] = time.monotonic) -> None:
        next_t = clock()
        while not stop.is_set():
            now = clock()
            if now < next_t:
                time.sleep(min(next_t - now, self.dt))
                continue
            self.step(next_t)
            next_t += self.dt
            if clock() - next_t > 0.25:
                self.overruns += 1
                next_t = clock()


# fabryka składa ciało robota z domyślnymi zachowaniami, wspólna dla aplikacji i testów
def create_body(
    settings: Settings,
    playback: PlaybackLike,
    person: LatestValue[PersonObservation] | None = None,
    audio: LatestValue[AudioStatus] | None = None,
    budget_fn: Callable[[], object] | None = None,
    intent_responder: Callable[[IntentRequest, IntentResult], None] | None = None,
    special_intents: dict[str, Callable[[IntentRequest, RobotState], IntentResult | None]] | None = None,
) -> BodyRuntime:
    sim = MujocoSim(settings.resolve_path(settings.mjcf_path))
    kin = So101Kinematics(sim.model)
    limits = build_limits(ranges_from_model(sim.model), speed_scale=settings.speed_scale)
    controller = SafeMotionController(limits, 1.0 / settings.control_hz, pose_clearance=kin.clearance)
    sim.reset(NEUTRAL_POSE)
    controller.reset(NEUTRAL_POSE)
    tracking = TrackingBehavior(
        kin,
        hfov_deg=settings.camera_hfov_deg,
        aspect=settings.camera_width / settings.camera_height,
        return_to_neutral_s=settings.person_return_to_neutral_s,
    )
    skill = PickPlaceSkill(kin, sim.cube_position, sim.place_pos)
    planner = BehaviorPlanner(tracking, JawBehavior(), skill)
    return BodyRuntime(
        settings, sim, kin, planner, Arbiter(NEUTRAL_POSE), controller, playback,
        person=person, audio=audio, budget_fn=budget_fn,
        intent_responder=intent_responder, special_intents=special_intents,
    )
