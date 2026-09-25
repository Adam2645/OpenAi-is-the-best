from __future__ import annotations

import numpy as np
import pytest

from so101_expressive.budget import CostMeter
from so101_expressive.conversation.base import AudioChunk, Interrupted, TurnComplete, TurnStarted
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.conversation.scripted import ScriptedBackend, babble
from so101_expressive.config import Settings
from so101_expressive.inputs.face import ScriptedPerson
from so101_expressive.inputs.virtual import clip_source
from so101_expressive.motion.limits import GRIPPER, PAN
from so101_expressive.runtime import Command
from so101_expressive.state import ApiStatus, ConversationPhase, GripPhase, PersonStatus

from .conftest import synthetic_speech
from .fake_live import FakeConnector, FakeSession, wait_for
from .test_audio_inputs import speech16, synth_music
from .world import World, assert_motion_limits


# stale widoczny rozmówca na wprost, żeby testy rozmowy nie zależały od śledzenia
def present(u: float = 0.0) -> ScriptedPerson:
    return ScriptedPerson([(0.0, 1e9, PersonStatus.TRACKED, u, -0.1, 0.14, 0.95)])


# lokalna synteza sylab zastępuje tts, żeby test nie zależał od zainstalowanego syntezatora
class BabbleTTS:
    rate = 24000
    engine = "synthetic"

    # długość wypowiedzi zależy od długości tekstu jak w prawdziwym tts
    def synth(self, text: str) -> np.ndarray:
        return babble(len(text) * 0.05, self.rate)


# scenariusz 1: rozmowa z gestem - słucha, mówi z ruchem szczęki i gestem, wraca do słuchania, limity zachowane
def test_scenario_conversation_and_gestures(settings):
    replies = [("Cześć! Miło Cię widzieć, porozmawiajmy chwilę o robotach.", "wave")]
    world = World(settings, lambda sink: ScriptedBackend(sink, BabbleTTS(), replies, threaded=False), present())
    world.backend.start()
    world.run(1.5)
    assert world.body.state.conversation is ConversationPhase.LISTENING
    world.rig.add_source(clip_source(speech16(1.5), 16000, world.t, gain=1.0))
    recs = world.run_until(lambda s: s.conversation is ConversationPhase.ROBOT_SPEAKING, 5.0)
    recs += world.run_until(lambda s: s.conversation is ConversationPhase.LISTENING, 8.0)
    phases = world.body.journal.values("conversation")
    assert ConversationPhase.USER_SPEAKING in phases and ConversationPhase.ROBOT_SPEAKING in phases
    assert "wave" in world.body.journal.values("gesture")
    grip = np.array([r.q_cmd[GRIPPER] for r in world.records])
    assert np.ptp(grip) > 0.15
    accepted = [res.accepted for _, intent, res in world.body.intent_log if intent.name == "perform_gesture"]
    assert accepted == [True]
    assert_motion_limits(world.body, world.records)


# scenariusz 2: przerwanie wypowiedzi - wejście w słowo otwiera bramkę, przerwanie czyści bufor, szczęka zamyka się płynnie
def test_scenario_interruption(settings):
    world = World(settings, lambda sink: ScriptedBackend(sink, BabbleTTS(), threaded=False), present())
    world.backend.start()
    world.run(0.5)
    world.body.post(Command("gesture", {"name": "think"}))
    world.sink(TurnStarted())
    world.sink(AudioChunk(synthetic_speech(6.0).tobytes()))
    world.run(1.5)
    assert world.body.state.conversation is ConversationPhase.ROBOT_SPEAKING and world.body.state.gesture == "think"
    world.rig.add_source(clip_source(speech16(1.5, seed=7), 16000, world.t, gain=2.5))
    world.run_until(lambda s: world.pipeline.barge_ins >= 1, 1.0)
    t_int = world.t
    world.sink(Interrupted())
    after = world.run(1.0)
    assert not world.playback.has_pending()
    assert max(r.state.audio_level for r in after[3:]) < 1e-3
    assert world.body.state.gesture is None
    assert after[-1].q_cmd[GRIPPER] < 0.05
    assert world.body.state.conversation in (ConversationPhase.USER_SPEAKING, ConversationPhase.LISTENING)
    assert_motion_limits(world.body, world.records)
    assert t_int > 0


# scenariusz 3: zniknięcie i powrót rozmówcy - brak ruchu przy niepewności i nieobecności, płynny powrót
def test_scenario_person_lost_and_back(settings):
    person = ScriptedPerson([
        (0.0, 4.0, PersonStatus.TRACKED, -0.5, -0.1, 0.14, 0.95),
        (4.0, 5.5, PersonStatus.UNCERTAIN, -0.5, -0.1, 0.14, 0.4),
        (9.0, 1e9, PersonStatus.TRACKED, 0.5, -0.1, 0.14, 0.95),
    ])
    world = World(settings, None, person)
    world.run(4.0)
    pan_left = world.body.controller.q[PAN]
    assert pan_left < -0.2
    world.run(0.8)
    frozen = world.run(4.1)
    q = np.array([r.q_cmd for r in frozen])
    assert np.max(np.ptp(q, axis=0)) < 1e-4
    assert all(not r.state.tracking for r in frozen)
    back = world.run(4.0)
    assert world.body.controller.q[PAN] > 0.2
    steps = np.abs(np.diff(np.array([r.q_cmd for r in back]), axis=0))
    assert np.all(steps <= world.body.controller.vmax * world.body.dt + 1e-9)
    assert_motion_limits(world.body, world.records)


# scenariusz 4: muzyka - własna mowa robota nie włącza tańca, muzyka włącza bezpieczny taniec, cisza go wygasza
def test_scenario_music_and_safe_dance(settings):
    world = World(settings, None, present())
    for _ in range(2):
        world.playback.enqueue(synthetic_speech(4.0))
        world.run(4.5)
    assert not any(r.state.dancing or r.state.music for r in world.records)
    world.rig.add_source(clip_source(synth_music(16.0), 16000, world.t, gain=1.0))
    world.run_until(lambda s: s.dancing, 12.0)
    dance = world.run(3.0)
    assert all(r.state.music for r in dance)
    world.run_until(lambda s: not s.dancing, 16.0)
    assert_motion_limits(world.body, world.records)
    dance_steps = np.abs(np.diff(np.array([r.q_cmd for r in dance]), axis=0))
    assert np.max(dance_steps) <= np.max(world.body.controller.vmax) * world.body.dt + 1e-9


# scenariusz 5a: chwyt fizyczny podczas mówienia z włączoną opcją milczenia - mowa wyciszona, chwytak stabilny
@pytest.mark.physics
def test_scenario_grasp_while_speaking_with_mute_option(tmp_path):
    settings = Settings.from_env({"LEDGER_PATH": str(tmp_path / "l.json"), "MUTE_SPEECH_WHILE_HOLDING": "tak"})
    world = World(settings, None, present())
    world.body.post(Command("pick"))
    world.run_until(lambda s: s.grip is GripPhase.CLOSING, 8.0)
    assert world.body.state.grip_commanded and not world.body.state.holding_object
    world.run_until(lambda s: s.grip is GripPhase.HOLDING, 8.0)
    world.run(1.5)
    world.sink(TurnStarted())
    world.sink(AudioChunk(synthetic_speech(2.0).tobytes()))
    world.sink(TurnComplete())
    talk = world.run(2.5)
    assert all(r.state.speech_muted for r in talk)
    assert not any(r.state.audio_playing for r in talk)
    assert np.ptp([r.q_cmd[GRIPPER] for r in talk]) == 0.0
    assert world.body.state.grip_evidence.source == "physics" and world.body.sim.cube_position()[2] > 0.06


# scenariusz 5b: pozorowany stan chwytu dla testu logiki jest jawnie oznaczony i nie udaje fizyki
def test_scenario_mock_grip_state_is_labelled(settings):
    world = World(settings, None, present())
    world.body.post(Command("mock_grip", {"phase": GripPhase.HOLDING}))
    world.playback.enqueue(synthetic_speech(2.0))
    recs = world.run(2.0)
    assert world.body.state.grip_evidence.source == "mock"
    assert any("szczęka: chwytak trzyma obiekt" in r.state.suppressed for r in recs)
    res = world.body.planner.request_pick(world.t, world.body.state, world.body.sim.joint_q())
    assert not res.accepted


# scenariusz 6: utrata internetu i przekroczenie budżetu - robot dalej śledzi lokalnie, a api zostaje bezpiecznie wyłączone
def test_scenario_network_loss_and_budget(tmp_path):
    settings = Settings.from_env({
        "LEDGER_PATH": str(tmp_path / "l.json"), "IDLE_DISCONNECT_S": "0", "RECONNECT_MAX_BACKOFF_S": "0.05",
        "BUDGET_SESSION_PLN": "0.05",
    })
    session = FakeSession()
    connector = FakeConnector([OSError("no route"), OSError("no route"), session])

    # backend gemini z fałszywym łącznikiem i krótkim strażnikiem
    def factory(sink):
        return GeminiLiveBackend(settings, CostMeter.from_settings(settings), sink, connect_fn=connector, watchdog_period=0.02)

    world = World(settings, factory, present(-0.3))
    world.backend.start()
    wait_for(lambda: world.backend.status is ApiStatus.OFFLINE, timeout=3.0)
    offline = world.run(1.0)
    assert any(r.state.api is ApiStatus.OFFLINE and r.state.tracking for r in offline)
    assert all(r.state.conversation is not ConversationPhase.ROBOT_SPEAKING for r in offline)
    wait_for(lambda: world.backend.status is ApiStatus.CONNECTED, timeout=5.0)
    world.run(0.5)
    assert world.body.state.api is ApiStatus.CONNECTED and world.body.state.tracking
    session.push({"usage_metadata": {"prompt_token_count": 20000, "prompt_tokens_details": [{"modality": "AUDIO", "token_count": 20000}]}})
    wait_for(lambda: world.backend.status is ApiStatus.BUDGET_EXCEEDED)
    world.rig.add_source(clip_source(speech16(1.5), 16000, world.t, gain=1.0))
    sent_before = len(session.sent)
    world.run(2.5)
    assert world.body.state.api is ApiStatus.BUDGET_EXCEEDED and world.body.state.tracking
    assert len(session.sent) == sent_before and len(connector.configs) == 3
    world.backend.stop()


# scenariusz 7a: awaryjny stop w trakcie gestu hamuje ramię, blokuje nowe gesty i po zwolnieniu wraca płynnie
def test_scenario_estop_during_gesture(settings):
    world = World(settings, None, present(0.2))
    world.run(1.0)
    world.body.post(Command("gesture", {"name": "wave"}))
    world.run(0.8)
    assert np.max(np.abs(world.body.controller.v)) > 0.2
    world.body.post(Command("estop", {"reason": "test"}))
    braking = world.run(1.0)
    assert np.all(braking[-1].v_cmd == 0.0)
    still = world.run(2.0)
    assert np.max(np.ptp(np.array([r.q_cmd for r in still]), axis=0)) == 0.0
    world.body.post(Command("gesture", {"name": "nod"}))
    world.run(0.2)
    assert world.body.command_log[-1][2].accepted is False
    world.body.post(Command("reset"))
    world.run(3.0)
    assert not world.body.state.estop
    assert_motion_limits(world.body, world.records)


# scenariusz 7b: awaryjny stop przy trzymaniu nie otwiera chwytaka, więc obiekt nie spada
@pytest.mark.physics
def test_scenario_estop_while_holding_keeps_object(settings):
    world = World(settings, None, present())
    world.body.post(Command("pick"))
    world.run_until(lambda s: s.grip is GripPhase.HOLDING, 16.0)
    world.run(0.5)
    world.body.post(Command("estop", {"reason": "test"}))
    recs = world.run(3.0)
    assert np.ptp([r.q_cmd[GRIPPER] for r in recs]) == 0.0
    assert world.body.sim.cube_position()[2] > 0.06
    assert world.body.state.grip is GripPhase.HOLDING


# scenariusz 7c: losowe prośby, gesty, taniec i skoki rozmówcy nigdy nie łamią limitów ani prześwitu nad blatem
def test_scenario_random_requests_respect_limits(settings):
    rng = np.random.default_rng(3)
    segs = []
    t = 0.0
    while t < 20.0:
        d = float(rng.uniform(0.5, 2.5))
        status = PersonStatus.TRACKED if rng.random() < 0.7 else PersonStatus.UNCERTAIN
        segs.append((t, t + d, status, float(rng.uniform(-1, 1)), float(rng.uniform(-1, 1)), float(rng.uniform(0.05, 0.3)), 0.95))
        t += d
    world = World(settings, None, ScriptedPerson(segs))
    names = ["nod", "wave", "shrug", "think", "happy", "surprised", "bow", "look_around", "curious", "shake_head"]

    # co pewien czas wysyła losowe polecenie, jak niecierpliwy model językowy
    def poke(tt: float) -> None:
        if rng.random() < 0.02:
            world.body.post(Command("gesture", {"name": str(rng.choice(names)), "intensity": "strong"}))
        if rng.random() < 0.004:
            world.body.post(Command("dance", {"duration": "short"}))
        if rng.random() < 0.01:
            world.playback.enqueue(synthetic_speech(1.0, seed=int(rng.integers(0, 100))))

    recs = world.run(20.0, on_step=poke)
    assert_motion_limits(world.body, recs)
    kin = world.body.kin
    assert min(kin.clearance(r.q_cmd, "expressive") for r in recs[::10]) > -0.01
