from __future__ import annotations

import numpy as np

from so101_expressive.behavior.manipulation import GRIPPER_CLOSED, GRIPPER_OPEN, PickPlaceSkill
from so101_expressive.behavior.planner import IntentResult
from so101_expressive.conversation.base import IntentCancelled, IntentRequest
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.runtime import create_body
from so101_expressive.state import GripEvidence, GripPhase, ManipulationPhase

from .conftest import run_for

GRASP = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
NO_CONTACT = GripEvidence("test")
CONTACT = GripEvidence("test", 5.0, 5.0, blocked=True)


# zadanie ustawione na początku zamykania chwytaka bez fizyki pozwala badać same liczniki czasu automatu faz
def closing_skill() -> PickPlaceSkill:
    skill = PickPlaceSkill(None, lambda: np.zeros(3), np.zeros(3))
    skill._plan = {"pre": GRASP, "grasp": GRASP, "lift": GRASP, "hold": GRASP}
    skill._last = np.r_[GRASP, GRIPPER_OPEN]
    skill.grip = GripPhase.CLOSING
    skill._enter(ManipulationPhase.CLOSE, 0.0, np.r_[GRASP, GRIPPER_CLOSED], duration=0.6)
    return skill


# przesuwa czas zadania krokami z tym samym dowodem chwytu i stanem awaryjnego stopu
def advance(skill: PickPlaceSkill, t0: float, t1: float, evidence: GripEvidence, estop: bool, dt: float = 0.05) -> float:
    t = t0
    while t < t1 - 1e-9:
        skill.update(t, skill._last.copy(), evidence, estop)
        t += dt
    return t


# czas awaryjnego stopu nie liczy się do limitu potwierdzenia chwytu, więc zwolnienie stopu nie kończy chwytu porażką
def test_estop_time_is_excluded_from_grasp_timeout():
    skill = closing_skill()
    t = advance(skill, 0.0, 0.2, NO_CONTACT, False)
    t = advance(skill, t, 3.2, NO_CONTACT, True)
    skill.update(t, skill._last.copy(), NO_CONTACT, False)
    assert skill.phase is ManipulationPhase.CLOSE and skill.grip is GripPhase.CLOSING
    t = advance(skill, t, 4.9, NO_CONTACT, False)
    assert skill.phase is ManipulationPhase.CLOSE
    advance(skill, t, 5.8, NO_CONTACT, False)
    assert skill.phase is ManipulationPhase.FAILED and skill.message == "brak potwierdzenia chwytu"


# kontakt szczęk musi trwać przez obserwowany czas po wznowieniu, a nie dzięki czasowi spędzonemu w stopie
def test_contact_confirmation_ignores_time_spent_stopped():
    skill = closing_skill()
    skill.update(0.1, skill._last.copy(), CONTACT, False)
    advance(skill, 0.2, 2.2, CONTACT, True)
    skill.update(2.2, skill._last.copy(), CONTACT, False)
    assert skill.grip is GripPhase.CLOSING
    advance(skill, 2.25, 2.33, CONTACT, False)
    assert skill.grip is GripPhase.CLOSING
    skill.update(2.36, skill._last.copy(), CONTACT, False)
    assert skill.grip is GripPhase.CONTACT and skill.phase is ManipulationPhase.LIFT


# anulowanie przez serwer wywołania, które rozpoczęło chwyt, przerywa go bezpieczną ścieżką, a obce anulowanie nie
def test_server_cancellation_aborts_owned_manipulation(body):
    t, _ = run_for(body, 0.0, 0.2)
    body.post(IntentRequest("call-1", "manipulate", {"action": "pick_cube"}))
    t, _ = run_for(body, t, 0.5)
    assert body.state.manipulation is ManipulationPhase.APPROACH
    body.post(IntentCancelled(("other-call",)))
    t, _ = run_for(body, t, 0.2)
    assert body.state.manipulation is ManipulationPhase.APPROACH
    body.post(IntentCancelled(("call-1",)))
    run_for(body, t, 0.2)
    assert body.state.manipulation is ManipulationPhase.FAILED
    assert body.planner.skill.message == "przerwano zadanie" and body.state.grip is GripPhase.OPEN


# walidacja w pętli ciała odrzuca niepoprawne prośby z każdego źródła, zanim dotrą do planisty lub obsługi specjalnej
def test_runtime_validates_intents_before_any_handler(settings):
    calls = []
    body = create_body(
        settings, PlaybackBuffer(),
        special_intents={"look_at_scene": lambda item, state: calls.append(item.call_id) or IntentResult(True, "ok")},
    )
    body.post(IntentRequest("a", "look_at_scene", {"extra": "1"}))
    body.post(IntentRequest("b", "manipulate", {"action": "throw_cube"}))
    body.post(IntentRequest("c", "set_joint_position", {}))
    body.post(IntentRequest("d", "look_at_scene", {}))
    body.step(0.0)
    accepted = {item.call_id: res.accepted for _, item, res in body.intent_log}
    assert accepted == {"a": False, "b": False, "c": False, "d": True}
    assert calls == ["d"] and body.state.manipulation is ManipulationPhase.IDLE
