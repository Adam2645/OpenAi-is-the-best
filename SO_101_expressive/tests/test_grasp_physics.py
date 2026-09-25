from __future__ import annotations

import numpy as np
import pytest

from so101_expressive.behavior.manipulation import PickPlaceSkill
from so101_expressive.motion.limits import GRIPPER
from so101_expressive.runtime import Command
from so101_expressive.state import GripPhase, ManipulationPhase

from .conftest import run_for, synthetic_speech

pytestmark = pytest.mark.physics


# czeka na warunek stanu, zwracając czas i zapisy kroków, aby testy nie zależały od stałych opóźnień
def run_until(body, t, predicate, timeout):
    records = []
    end = t + timeout
    while t < end:
        t, recs = run_for(body, t, 0.1)
        records.extend(recs)
        if predicate(body.state):
            return t, records
    raise AssertionError(f"warunek nie spełniony w {timeout} s, stan: {body.state.summary_pl()}")


# pełny cykl chwytu w fizyce mujoco: komenda, potwierdzenie kontaktem, uniesienie i odłożenie
def test_physical_pick_hold_and_place(body):
    t = 0.0
    t, _ = run_for(body, t, 0.5)
    body.post(Command("pick"))
    t, recs = run_until(body, t, lambda s: s.grip is GripPhase.CLOSING, 8.0)
    assert body.state.grip_commanded and not body.state.holding_object
    t, recs = run_until(body, t, lambda s: s.grip is GripPhase.HOLDING, 8.0)
    ev = body.state.grip_evidence
    assert ev.source == "physics" and ev.both_jaws and ev.lifted and ev.attached
    t, _ = run_for(body, t, 1.5)
    assert body.sim.cube_position()[2] > 0.06
    grip_seq = body.journal.values("grip")
    assert grip_seq[:3] == [GripPhase.CLOSING, GripPhase.CONTACT, GripPhase.HOLDING]
    body.post(Command("place"))
    t, _ = run_until(body, t, lambda s: s.manipulation is ManipulationPhase.IDLE and s.grip is GripPhase.OPEN, 12.0)
    cube = body.sim.cube_position()
    assert cube[2] < 0.03
    assert np.linalg.norm(cube[:2] - body.sim.place_pos[:2]) < 0.03


# mowa podczas trzymania nie porusza chwytakiem, a szczęka jest wstrzymana z jawnym powodem
def test_speaking_while_holding_keeps_gripper_still(body):
    t = 0.0
    body.post(Command("pick"))
    t, _ = run_until(body, t, lambda s: s.grip is GripPhase.HOLDING, 16.0)
    t, _ = run_for(body, t, 1.5)
    body.playback.enqueue(synthetic_speech(3.0))
    t, recs = run_for(body, t, 3.0)
    grip_cmd = np.array([r.q_cmd[GRIPPER] for r in recs])
    assert np.ptp(grip_cmd) == 0.0
    assert all(r.state.audio_playing for r in recs[20:250])
    assert any("szczęka: chwytak trzyma obiekt" in r.state.suppressed for r in recs)
    assert not any(r.state.jaw_active for r in recs)
    assert body.state.grip is GripPhase.HOLDING and body.sim.cube_position()[2] > 0.06


# plan chwytu zachowuje gałąź obrotu nadgarstka, więc opuszczanie nad kostką nie wymaga pół obrotu
@pytest.mark.parametrize("start_roll", [-2.0, -1.0, 0.0, 1.0, 2.0])
def test_pick_plan_keeps_wrist_branch_continuous(body, start_roll):
    skill: PickPlaceSkill = body.planner.skill
    q_now = body.sim.joint_q()
    q_now[4] = start_roll
    ok, msg = skill.request_pick(0.0, q_now)
    assert ok, msg
    assert np.max(np.abs(skill._plan["pre"] - skill._plan["grasp"])) < 0.8


# chwyt udaje się z różnych póz startowych i przy przesuniętej kostce, a nie tylko w jednym dopracowanym przypadku
@pytest.mark.parametrize(
    "start,offset",
    [
        ([0.3, -0.3, 0.2, -0.25, 1.2, 0.2], (0.0, 0.0)),
        ([-0.4, -0.6, 0.6, -0.3, -1.5, 0.0], (0.01, -0.01)),
        ([0.0, -0.2, 0.1, 0.3, 2.2, 0.3], (-0.01, 0.015)),
    ],
)
def test_pick_succeeds_from_various_start_poses(body, start, offset):
    body.sim.reset(np.array(start))
    body.controller.reset(np.array(start))
    body.sim.reset_cube(body.sim.initial_cube_pos + np.array([offset[0], offset[1], 0.0]))
    t, _ = run_for(body, 0.0, 0.3)
    body.post(Command("pick"))
    run_until(body, t, lambda s: s.grip is GripPhase.HOLDING, 14.0)
    assert body.state.grip_evidence.source == "physics" and body.sim.cube_position()[2] > 0.05


# awaryjny stop podczas zamykania chwytaka nie psuje chwytu po zwolnieniu, bo czas zatrzymania nie liczy się do limitów faz
def test_estop_during_closing_then_grasp_completes(body):
    body.post(Command("pick"))
    t, _ = run_until(body, 0.0, lambda s: s.grip is GripPhase.CLOSING, 8.0)
    body.post(Command("estop", {"reason": "test"}))
    t, _ = run_for(body, t, 3.0)
    assert body.state.manipulation is ManipulationPhase.CLOSE and body.state.grip is GripPhase.CLOSING
    body.post(Command("reset"))
    run_until(body, t, lambda s: s.grip is GripPhase.HOLDING, 8.0)
    assert ManipulationPhase.FAILED not in body.journal.values("manipulation")
    assert body.sim.cube_position()[2] > 0.05


# bez obiektu szczęka w fizyce nadąża za obwiednią dźwięku w chwili jego wyjścia z głośnika
def test_jaw_moves_with_played_audio_when_gripper_free(body):
    t, _ = run_for(body, 0.0, 0.3)
    body.playback.enqueue(synthetic_speech(3.0))
    sound_out = []
    t, recs = run_for(body, t, 3.0, on_step=lambda tt: sound_out.append(body.playback.level_at(tt)))
    jaw = np.array([r.q_meas[GRIPPER] for r in recs])
    mapped = np.clip((20 * np.log10(np.maximum(np.array(sound_out), 1e-6)) + 42.0) / 28.0, 0.0, 1.0)
    assert np.ptp(jaw) > 0.2

    # korelacja z przesunięciem pozwala znaleźć faktyczne opóźnienie szczęki względem dźwięku
    def corr_at(lag: int) -> float:
        a = jaw[max(lag, 0) : len(jaw) + min(lag, 0)]
        b = mapped[max(-lag, 0) : len(mapped) - max(lag, 0)]
        return float(np.corrcoef(a, b)[0, 1])

    best = max(range(-10, 16), key=corr_at)
    assert abs(best) <= 4
    assert corr_at(best) > 0.6
    assert corr_at(0) > 0.6
