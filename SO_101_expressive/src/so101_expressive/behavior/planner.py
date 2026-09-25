from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..motion.limits import GRIPPER, NEUTRAL_POSE
from ..state import ConversationPhase, GripEvidence, GripPhase, ManipulationPhase, PersonStatus, RobotState
from .arbiter import Layer, LayerRequest
from .expressive import GESTURES, INTENSITY, DanceBehavior, GesturePlayback, MicroMotion
from .jaw import JawBehavior
from .manipulation import GRIPPER_CLOSED, PickPlaceSkill
from .tracking import PersonObservation, TrackingBehavior

DANCE_DURATIONS = {"short": 6.0, "medium": 12.0, "long": 20.0}
LOCKING_GRIP = (GripPhase.CLOSING, GripPhase.CONTACT, GripPhase.HOLDING, GripPhase.RELEASING)


# wynik prośby wraca do modelu, żeby rozmowa odzwierciedlała to, co ciało naprawdę zrobiło
@dataclass(frozen=True)
class IntentResult:
    accepted: bool
    message: str
    data: dict = field(default_factory=dict)

    # odpowiedź funkcji dla modelu ma stałą, prostą strukturę po polsku
    def as_response(self) -> dict:
        return {"result": "ok" if self.accepted else "odrzucono", "komunikat": self.message, **self.data}


# wynik planowania zbiera prośby warstw oraz pola stanu wyliczone w tym kroku
@dataclass(frozen=True)
class PlanOutput:
    requests: list[LayerRequest]
    grip: GripPhase
    manipulation: ManipulationPhase
    hold_value: float
    evidence: GripEvidence | None
    gesture: str | None
    dancing: bool
    tracking: bool
    jaw_active: bool
    gaze_target: tuple[float, float, float] | None
    message: str


# planista zamienia stan i prośby na warstwy ruchu, a zakazy wynikające ze stanu egzekwuje przed arbitrem
class BehaviorPlanner:
    # zachowania są osobnymi obiektami, dzięki czemu każde da się testować niezależnie
    def __init__(
        self,
        tracking: TrackingBehavior,
        jaw: JawBehavior,
        skill: PickPlaceSkill | None = None,
        neutral: np.ndarray = NEUTRAL_POSE,
    ) -> None:
        self.tracking = tracking
        self.jaw = jaw
        self.skill = skill
        self.neutral = np.asarray(neutral, dtype=float).copy()
        self.dance = DanceBehavior()
        self.micro = MicroMotion()
        self.gesture: GesturePlayback | None = None
        self._gesture_call: str | None = None
        self._manip_call: str | None = None
        self._pending: tuple[str, float, str | None] | None = None
        self._music_dance = False
        self._mock_grip: GripPhase | None = None

    # pozorowany stan chwytu istnieje wyłącznie dla testów logiki i jest oznaczany źródłem mock
    def set_mock_grip(self, phase: GripPhase | None) -> None:
        self._mock_grip = phase

    # faza chwytu pochodzi z zadania manipulacji albo z jawnie pozorowanego stanu testowego
    def grip_phase(self) -> GripPhase:
        if self._mock_grip is not None:
            return self._mock_grip
        return self.skill.grip if self.skill is not None else GripPhase.OPEN

    # blokada chwytaka obejmuje całą manipulację oraz każdy etap od komendy chwytu do zwolnienia
    def _locked(self) -> bool:
        manip_active = self.skill is not None and self.skill.active
        return self.grip_phase() in LOCKING_GRIP or manip_active

    # gest z rozmowy jest wykonywany tylko wtedy, gdy stan ciała na to pozwala
    def request_gesture(
        self, name: str, intensity: str, t: float, state: RobotState, call_id: str | None = None
    ) -> IntentResult:
        if name not in GESTURES:
            return IntentResult(False, f"nieznany gest: {name}")
        if state.estop:
            return IntentResult(False, "awaryjny stop jest aktywny")
        if self._locked():
            return IntentResult(False, "trzymam obiekt lub manipuluję - gesty są wyłączone, chwytak pozostaje stabilny")
        scale = INTENSITY.get(intensity, 1.0)
        label = GESTURES[name].label_pl
        if self.gesture is not None and not self.gesture.done(t):
            self._pending = (name, scale, call_id)
            return IntentResult(True, f"gest {label} zaplanowany po bieżącym")
        self.gesture = GesturePlayback(GESTURES[name], t, scale)
        self._gesture_call = call_id
        return IntentResult(True, f"wykonuję gest: {label}")

    # taniec na prośbę działa przez ograniczony czas i nie startuje przy zajętym chwytaku
    def request_dance(self, duration_key: str, t: float, state: RobotState) -> IntentResult:
        if state.estop:
            return IntentResult(False, "awaryjny stop jest aktywny")
        if self._locked():
            return IntentResult(False, "trzymam obiekt - nie tańczę")
        self.dance.start(t, state.music_bpm or None, DANCE_DURATIONS.get(duration_key, 12.0))
        return IntentResult(True, "tańczę spokojnie w granicach bezpiecznego ruchu")

    # model może poprosić o odwrócenie uwagi od rozmówcy bez wyłączania śledzenia na stałe
    def request_attention(self, target: str, t: float) -> IntentResult:
        if target == "rest":
            self.tracking.pause(t, 10.0)
            return IntentResult(True, "odpoczywam wzrokiem przez 10 sekund")
        self.tracking.resume()
        return IntentResult(True, "patrzę na rozmówcę")

    # chwyt jest prośbą do zadania manipulacji, które samo sprawdzi zasięg i stan chwytaka
    def request_pick(self, t: float, state: RobotState, q_meas: np.ndarray, call_id: str | None = None) -> IntentResult:
        if state.estop:
            return IntentResult(False, "awaryjny stop jest aktywny")
        if self.skill is None:
            return IntentResult(False, "manipulacja jest niedostępna w tym trybie")
        if self._mock_grip is not None:
            return IntentResult(False, "aktywny jest pozorowany stan chwytu testowego")
        self._cancel_expressive(t)
        ok, msg = self.skill.request_pick(t, q_meas)
        if ok:
            self._manip_call = call_id
        return IntentResult(ok, msg)

    # odłożenie przechodzi przez to samo zadanie, które potwierdziło trzymanie
    def request_place(self, t: float, state: RobotState, q_meas: np.ndarray, call_id: str | None = None) -> IntentResult:
        if state.estop:
            return IntentResult(False, "awaryjny stop jest aktywny")
        if self.skill is None:
            return IntentResult(False, "manipulacja jest niedostępna w tym trybie")
        ok, msg = self.skill.request_place(t, q_meas)
        if ok:
            self._manip_call = call_id
        return IntentResult(ok, msg)

    # łagodny stop z rozmowy tylko zmniejsza ruch, a trzymany obiekt pozostaje w chwytaku
    def soft_stop(self, t: float) -> IntentResult:
        self._cancel_expressive(t)
        self.tracking.pause(t, 5.0)
        if self.skill is not None and self.skill.active and self.skill.phase is not ManipulationPhase.HOLD:
            self.skill.abort(t)
        return IntentResult(True, "zatrzymuję gesty i śledzenie")

    # wszystkie prośby modelu przechodzą przez jedną funkcję z walidacją nazw i argumentów
    def handle_intent(
        self, name: str, args: dict, t: float, state: RobotState, q_meas: np.ndarray, call_id: str | None = None
    ) -> IntentResult:
        if name == "perform_gesture":
            return self.request_gesture(str(args.get("gesture", "")), str(args.get("intensity", "normal")), t, state, call_id)
        if name == "dance":
            return self.request_dance(str(args.get("duration", "medium")), t, state)
        if name == "set_attention":
            return self.request_attention(str(args.get("target", "person")), t)
        if name == "manipulate":
            action = str(args.get("action", ""))
            if action == "pick_cube":
                return self.request_pick(t, state, q_meas, call_id)
            if action == "place_cube":
                return self.request_place(t, state, q_meas, call_id)
            return IntentResult(False, f"nieznana akcja manipulacji: {action}")
        if name == "stop_motion":
            return self.soft_stop(t)
        if name == "get_robot_state":
            return IntentResult(True, "aktualny stan robota", {"stan": state.summary_pl()})
        return IntentResult(False, f"nieznana czynność: {name}")

    # anulowanie wywołania przez serwer wygasza wynikający z niego gest i bezpiecznie przerywa rozpoczęte przez nie zadanie chwytu
    def cancel_calls(self, ids: tuple[str, ...], t: float) -> None:
        if self.gesture is not None and self._gesture_call in ids:
            self.gesture.cancel(t)
        if self._pending is not None and self._pending[2] in ids:
            self._pending = None
        if self._manip_call is not None and self._manip_call in ids:
            self._manip_call = None
            if self.skill is not None and self.skill.active:
                self.skill.abort(t)

    # przerwanie wypowiedzi kończy gest towarzyszący mowie zamiast dograć go do końca
    def on_interrupted(self, t: float) -> None:
        if self.gesture is not None:
            self.gesture.cancel(t, 0.3)
        self._pending = None

    # awaryjny stop kasuje plany ekspresyjne, żeby po zwolnieniu nie wróciły niespodziewanie
    def on_estop(self, t: float) -> None:
        self.gesture = None
        self._pending = None
        self._gesture_call = None
        self.dance.stop(t)
        self._music_dance = False
        self.jaw.reset()

    # wspólne wygaszenie gestów i tańca przed manipulacją lub łagodnym stopem
    def _cancel_expressive(self, t: float) -> None:
        if self.gesture is not None:
            self.gesture.cancel(t)
        self._pending = None
        self.dance.stop(t)
        self._music_dance = False

    # jeden krok planowania wylicza prośby wszystkich warstw na podstawie aktualnego stanu
    def plan(
        self,
        t: float,
        dt: float,
        state: RobotState,
        obs: PersonObservation,
        level: float,
        q_meas: np.ndarray,
        evidence: GripEvidence | None,
    ) -> PlanOutput:
        requests: list[LayerRequest] = []
        manip_phase = ManipulationPhase.IDLE
        message = ""
        if self.skill is not None and evidence is not None:
            out = self.skill.update(t, q_meas, evidence, state.estop)
            manip_phase, message = out.phase, out.message
            if out.targets is not None:
                requests.append(LayerRequest(
                    Layer.MANIPULATION, "manipulacja",
                    targets={i: float(out.targets[i]) for i in range(6)}, speed_scale=out.speed_scale,
                ))
        grip = self.grip_phase()
        locked = self._locked()
        trk = self.tracking.update(obs, t, dt, self.neutral)
        if trk.targets is not None:
            requests.append(LayerRequest(Layer.TRACKING, "śledzenie", targets=trk.targets, weight=trk.weight, speed_scale=0.8))
        if self.gesture is not None and self.gesture.done(t):
            self.gesture = None
            self._gesture_call = None
            if self._pending is not None and not locked and not state.estop:
                name, scale, cid = self._pending
                self.gesture = GesturePlayback(GESTURES[name], t, scale)
                self._gesture_call = cid
            self._pending = None
        if locked and self.gesture is not None:
            self.gesture.cancel(t)
        allow_dance = not locked and not state.estop
        if state.music_bpm:
            self.dance.set_bpm(state.music_bpm)
        if state.music and allow_dance and not self._music_dance:
            self.dance.start(t, state.music_bpm or None)
            self._music_dance = True
        elif self._music_dance and (not state.music or not allow_dance):
            self.dance.stop(t)
            self._music_dance = False
        if not allow_dance:
            self.dance.stop(t)
        talking = state.conversation in (ConversationPhase.ROBOT_SPEAKING, ConversationPhase.USER_SPEAKING)
        attenuation = (0.35 if talking else 1.0) * (0.3 if self.gesture is not None else 1.0)
        offsets = np.zeros(5)
        labels: list[str] = []
        if self.gesture is not None:
            offsets += self.gesture.offsets(t)
            labels.append(self.gesture.gesture.label_pl)
        dancing = self.dance.running(t)
        if dancing:
            offsets += self.dance.offsets(t, attenuation)
            labels.append("taniec")
        person_visible = obs.status is PersonStatus.TRACKED
        offsets += self.micro.offsets(
            t, dt,
            enabled=person_visible and not dancing and self.gesture is None and not locked and not state.estop,
            listening=state.conversation in (ConversationPhase.LISTENING, ConversationPhase.USER_SPEAKING),
            speaking=state.audio_playing,
            level=self.jaw.opening,
        )
        if np.any(np.abs(offsets) > 1e-6):
            requests.append(LayerRequest(
                Layer.EXPRESSIVE, " + ".join(labels) or "mikroruch", offsets={i: float(offsets[i]) for i in range(5)},
            ))
        jaw_active = False
        if locked or state.estop:
            self.jaw.reset()
            if level > 1e-4:
                requests.append(LayerRequest(Layer.JAW, "szczęka", targets={GRIPPER: float(self.neutral[GRIPPER])}))
        else:
            target = self.jaw.target(level, dt)
            jaw_active = self.jaw.opening > 0.05
            requests.append(LayerRequest(Layer.JAW, "szczęka", targets={GRIPPER: target}))
        if self._mock_grip is not None:
            holding = self._mock_grip is GripPhase.HOLDING
            evidence = GripEvidence("mock", 1.0 if holding else 0.0, 1.0 if holding else 0.0, holding, holding, holding, 1.0)
        hold_value = self.skill.hold_value if self.skill is not None else GRIPPER_CLOSED
        return PlanOutput(
            requests, grip, manip_phase, hold_value, evidence,
            self.gesture.name if self.gesture is not None else None,
            dancing, trk.active, jaw_active, trk.gaze_target, message,
        )
