from __future__ import annotations

from dataclasses import dataclass

import numpy as np

JOINT_NAMES = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
PAN, LIFT, ELBOW, WRIST_FLEX, WRIST_ROLL, GRIPPER = range(6)
ARM_JOINTS = (PAN, LIFT, ELBOW, WRIST_FLEX, WRIST_ROLL)

MODEL_RANGES = (
    (-1.91986, 1.91986),
    (-1.74533, 1.74533),
    (-1.69, 1.69),
    (-1.65806, 1.65806),
    (-2.74385, 2.74385),
    (-0.17453, 1.74533),
)
EXPRESSIVE_RANGES = (
    (-1.40, 1.40),
    (-1.20, 0.90),
    (-1.20, 1.40),
    (-1.55, 1.55),
    (-2.00, 2.00),
    (-0.17, 0.60),
)
DEFAULT_VMAX = (1.6, 1.3, 1.6, 2.2, 2.8, 4.0)
DEFAULT_AMAX = (6.0, 5.0, 6.0, 9.0, 12.0, 40.0)
NEUTRAL_POSE = np.array([0.0, -0.30, 0.20, -0.25, 0.0, 0.0])


# każdy przegub ma jawny zakres, prędkość i przyspieszenie, których nie może przekroczyć żadna warstwa
@dataclass(frozen=True)
class JointLimit:
    name: str
    lo: float
    hi: float
    vmax: float
    amax: float

    # przycięcie celu do zakresu jest ostatnią linią obrony przed błędnym poleceniem
    def clamp(self, value: float) -> float:
        return min(max(value, self.lo), self.hi)


# limity budujemy z zakresów modelu z marginesem, aby serwo nigdy nie dojeżdżało do twardego ogranicznika
def build_limits(
    ranges: tuple[tuple[float, float], ...] = MODEL_RANGES,
    margin: float = 0.03,
    vmax: tuple[float, ...] = DEFAULT_VMAX,
    amax: tuple[float, ...] = DEFAULT_AMAX,
    speed_scale: float = 1.0,
) -> tuple[JointLimit, ...]:
    out = []
    for i, name in enumerate(JOINT_NAMES):
        lo, hi = ranges[i]
        out.append(JointLimit(name, lo + margin, hi - margin, vmax[i] * speed_scale, amax[i] * speed_scale))
    return tuple(out)


# zakresy z pliku modelu mogą różnić się od domyślnych, gdy użytkownik podmieni plik mjcf
def ranges_from_model(model) -> tuple[tuple[float, float], ...]:
    ranges = []
    for name in JOINT_NAMES:
        jid = model.joint(name).id
        lo, hi = model.jnt_range[jid]
        ranges.append((float(lo), float(hi)))
    return tuple(ranges)


# zachowania ekspresyjne dostają węższy zakres niż manipulacja, żeby gesty nie zbliżały się do skrajnych pozycji
def clamp_expressive(q: np.ndarray) -> tuple[np.ndarray, bool]:
    out = q.copy()
    clipped = False
    for i in ARM_JOINTS:
        lo, hi = EXPRESSIVE_RANGES[i]
        value = min(max(out[i], lo), hi)
        clipped = clipped or value != out[i]
        out[i] = value
    return out, clipped
