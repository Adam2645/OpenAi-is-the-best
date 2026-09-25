from __future__ import annotations

import numpy as np

from so101_expressive.motion.controller import SafeMotionController
from so101_expressive.motion.kinematics import So101Kinematics
from so101_expressive.motion.limits import GRIPPER, NEUTRAL_POSE, build_limits
from so101_expressive.sim.mujoco_sim import MujocoSim

DT = 0.01


# każdy test startuje od tego samego sterownika w pozycji neutralnej
def make_controller(clearance=None) -> SafeMotionController:
    ctrl = SafeMotionController(build_limits(), DT, pose_clearance=clearance)
    ctrl.reset(NEUTRAL_POSE)
    return ctrl


# losowe, także skrajne cele nie mogą złamać limitów pozycji, prędkości ani przyspieszenia
def test_random_targets_respect_all_limits():
    ctrl = make_controller()
    rng = np.random.default_rng(0)
    target = NEUTRAL_POSE.copy()
    prev_v = ctrl.v.copy()
    for k in range(3000):
        if k % 40 == 0:
            target = rng.uniform(-4.0, 4.0, size=6)
        ctrl.step(target)
        assert np.all(ctrl.q >= ctrl.lo - 1e-9) and np.all(ctrl.q <= ctrl.hi + 1e-9)
        assert np.all(np.abs(ctrl.v) <= ctrl.vmax + 1e-9)
        assert np.all(np.abs(ctrl.v - prev_v) <= ctrl.amax * DT + 1e-9)
        prev_v = ctrl.v.copy()


# cel z wartością nan lub nieskończoną jest odrzucany, a przegub trzyma pozycję
def test_nonfinite_target_is_held_and_reported():
    ctrl = make_controller()
    target = NEUTRAL_POSE.copy()
    target[1] = np.nan
    target[2] = np.inf
    before = ctrl.q.copy()
    report = ctrl.step(target)
    assert set(report.nonfinite) == {"shoulder_lift", "elbow_flex"}
    assert np.allclose(ctrl.q, before)


# awaryjny stop wyhamowuje wszystkie przeguby z ograniczonym opóźnieniem i dalej nic się nie rusza
def test_estop_decelerates_to_standstill_and_holds():
    ctrl = make_controller()
    target = NEUTRAL_POSE.copy()
    target[0] = 1.3
    for _ in range(40):
        ctrl.step(target)
    assert abs(ctrl.v[0]) > 0.5
    v0 = abs(ctrl.v[0])
    steps = 0
    while np.any(np.abs(ctrl.v) > 0):
        ctrl.step(target, estop=True)
        steps += 1
        assert steps < 200
    assert steps * DT <= v0 / (2 * ctrl.amax[0]) + 3 * DT
    frozen = ctrl.q.copy()
    for _ in range(100):
        ctrl.step(np.zeros(6), estop=True)
    assert np.allclose(ctrl.q, frozen)


# cel spoza zakresu jest przycinany do limitu z marginesem, a raport odnotowuje interwencję
def test_out_of_range_target_is_clamped():
    ctrl = make_controller()
    target = NEUTRAL_POSE.copy()
    target[GRIPPER] = 5.0
    report = ctrl.step(target)
    assert "gripper" in report.clamped
    for _ in range(500):
        ctrl.step(target)
    assert abs(ctrl.q[GRIPPER] - ctrl.hi[GRIPPER]) < 1e-6


# gest skierowany w blat zostaje zatrzymany przed naruszeniem prześwitu w trybie ekspresyjnym
def test_workspace_clearance_blocks_motion_into_table(settings):
    sim = MujocoSim(settings.resolve_path(settings.mjcf_path))
    kin = So101Kinematics(sim.model)
    ctrl = make_controller(kin.clearance)
    target = NEUTRAL_POSE.copy()
    target[1], target[2], target[3] = 1.2, 1.2, 1.2
    blocked = False
    for _ in range(600):
        report = ctrl.step(target, mode="expressive")
        blocked = blocked or report.workspace_blocked
        assert kin.clearance(ctrl.q, "expressive") > -0.01
    assert blocked
