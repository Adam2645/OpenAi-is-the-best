from __future__ import annotations

import numpy as np

from so101_expressive.behavior.arbiter import Arbiter, Layer, LayerRequest
from so101_expressive.motion.limits import GRIPPER, NEUTRAL_POSE, PAN


# pomocnik buduje typowy zestaw próśb, w którym wszystkie warstwy chcą jednocześnie sterować
def all_layers(pan_track=0.5, jaw=0.4, manip=None):
    reqs = [
        LayerRequest(Layer.TRACKING, "śledzenie", targets={PAN: pan_track}),
        LayerRequest(Layer.EXPRESSIVE, "gest", offsets={1: 0.1, 3: 0.2}),
        LayerRequest(Layer.JAW, "szczęka", targets={GRIPPER: jaw}),
    ]
    if manip is not None:
        reqs.append(LayerRequest(Layer.MANIPULATION, "manipulacja", targets={i: float(manip[i]) for i in range(6)}, speed_scale=0.5))
    return reqs


# manipulacja przejmuje całe ramię i chwytak, a niższe warstwy są jawnie wstrzymane
def test_manipulation_overrides_tracking_gesture_and_jaw():
    arb = Arbiter(NEUTRAL_POSE)
    manip = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.9])
    d = arb.decide(0.0, all_layers(manip=manip), estop=False, gripper_locked=False, hold_value=-0.14, q_current=NEUTRAL_POSE)
    assert np.allclose(d.q_des, manip)
    assert d.arm_owner == "manipulacja" and d.mode == "manipulation" and d.speed_scale == 0.5
    assert any(s.startswith("śledzenie") for s in d.suppressed)
    assert any(s.startswith("gest") for s in d.suppressed)
    assert "szczęka: manipulacja ma pierwszeństwo" in d.suppressed


# zablokowany chwytak trzyma wartość utrzymania, a szczęka i gesty są wstrzymane z podaniem powodu
def test_holding_lock_beats_jaw_and_gestures():
    arb = Arbiter(NEUTRAL_POSE)
    d = arb.decide(0.0, all_layers(), estop=False, gripper_locked=True, hold_value=-0.14, q_current=NEUTRAL_POSE)
    assert d.q_des[GRIPPER] == -0.14
    assert d.gripper_owner == "utrzymanie obiektu"
    assert "szczęka: chwytak trzyma obiekt" in d.suppressed
    assert "gest: chwytak trzyma obiekt" in d.suppressed
    assert abs(d.q_des[PAN] - 0.5) < 1e-9


# bez blokady szczęka steruje chwytakiem, a gest dodaje przesunięcia do śledzenia
def test_jaw_and_gesture_compose_when_gripper_free():
    arb = Arbiter(NEUTRAL_POSE)
    d = arb.decide(0.0, all_layers(jaw=0.3), estop=False, gripper_locked=False, hold_value=-0.14, q_current=NEUTRAL_POSE)
    assert d.q_des[GRIPPER] == 0.3 and d.gripper_owner == "szczęka"
    assert abs(d.q_des[1] - (NEUTRAL_POSE[1] + 0.1)) < 1e-9


# awaryjny stop zamraża ostatni cel i wstrzymuje wszystkie warstwy
def test_estop_freezes_decision():
    arb = Arbiter(NEUTRAL_POSE)
    first = arb.decide(0.0, all_layers(), estop=False, gripper_locked=False, hold_value=-0.14, q_current=NEUTRAL_POSE)
    d = arb.decide(0.01, all_layers(pan_track=-1.0), estop=True, gripper_locked=False, hold_value=-0.14, q_current=NEUTRAL_POSE)
    assert np.allclose(d.q_des, first.q_des)
    assert d.arm_owner == "bezpieczeństwo" and len(d.suppressed) == 3


# zmiana właściciela ramienia z manipulacji na śledzenie przebiega płynnie, bez skoku celu
def test_owner_change_is_blended_without_jump():
    arb = Arbiter(NEUTRAL_POSE, blend_time=0.8)
    manip = np.array([1.0, 0.8, 0.8, 1.2, 1.0, 0.9])
    t = 0.0
    prev = arb.decide(t, all_layers(manip=manip), estop=False, gripper_locked=False, hold_value=-0.14, q_current=manip).q_des
    max_step = 0.0
    for _ in range(120):
        t += 0.01
        q = arb.decide(t, all_layers(), estop=False, gripper_locked=False, hold_value=-0.14, q_current=prev).q_des
        max_step = max(max_step, float(np.max(np.abs(q[:5] - prev[:5]))))
        prev = q
    assert max_step < 0.05
    assert abs(prev[PAN] - 0.5) < 1e-6
