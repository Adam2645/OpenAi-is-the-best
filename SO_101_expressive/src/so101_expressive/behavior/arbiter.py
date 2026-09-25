from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np

from ..motion.limits import GRIPPER, NEUTRAL_POSE, clamp_expressive
from .expressive import min_jerk


# kolejność warstw odzwierciedla wymagane pierwszeństwo od bezpieczeństwa aż po ruch szczęki
class Layer(IntEnum):
    JAW = 1
    EXPRESSIVE = 2
    TRACKING = 3
    MANIPULATION = 4
    HOLD = 5
    SAFETY = 6


LAYER_LABELS = {
    Layer.JAW: "szczęka",
    Layer.EXPRESSIVE: "gest",
    Layer.TRACKING: "śledzenie",
    Layer.MANIPULATION: "manipulacja",
    Layer.HOLD: "utrzymanie obiektu",
    Layer.SAFETY: "bezpieczeństwo",
}


# prośba warstwy zawiera cele bezwzględne lub przesunięcia, ale nigdy nie trafia do serw bez arbitra
@dataclass
class LayerRequest:
    layer: Layer
    label: str
    targets: dict[int, float] = field(default_factory=dict)
    offsets: dict[int, float] = field(default_factory=dict)
    weight: float = 1.0
    speed_scale: float = 1.0


# decyzja arbitra jest zapisywana w stanie, żeby było widać, kto steruje którą częścią ramienia
@dataclass(frozen=True)
class Decision:
    q_des: np.ndarray
    arm_owner: str
    gripper_owner: str
    suppressed: tuple[str, ...]
    speed_scale: float
    mode: str


# arbiter rozstrzyga konflikty warstw według priorytetów i płynnie przełącza właściciela ramienia
class Arbiter:
    # czas przejścia między właścicielami ramienia usuwa skoki przy zmianie zachowania
    def __init__(self, neutral: np.ndarray = NEUTRAL_POSE, blend_time: float = 0.8) -> None:
        self.neutral = np.asarray(neutral, dtype=float).copy()
        self.blend_time = blend_time
        self._last_q: np.ndarray | None = None
        self._last_key: str | None = None
        self._last_mode = "expressive"
        self._blend_from: np.ndarray | None = None
        self._blend_t0 = 0.0

    # po zwolnieniu awaryjnego stopu przejście zaczyna się od faktycznej pozycji ramienia
    def rebase(self, q_current: np.ndarray, t: float) -> None:
        self._blend_from = np.asarray(q_current, dtype=float)[:5].copy()
        self._blend_t0 = t
        self._last_q = np.asarray(q_current, dtype=float).copy()

    # jedna decyzja na krok sterowania łączy warstwy zgodnie z regułami pierwszeństwa
    def decide(
        self,
        t: float,
        requests: list[LayerRequest],
        *,
        estop: bool,
        gripper_locked: bool,
        hold_value: float,
        q_current: np.ndarray,
    ) -> Decision:
        req = {r.layer: r for r in requests}
        suppressed: list[str] = []
        if estop:
            q = (self._last_q if self._last_q is not None else np.asarray(q_current, dtype=float)).copy()
            suppressed.extend(f"{LAYER_LABELS[r.layer]}: awaryjny stop" for r in requests)
            return Decision(q, "bezpieczeństwo", "bezpieczeństwo", tuple(suppressed), 1.0, self._last_mode)
        manip = req.get(Layer.MANIPULATION)
        speed = 1.0
        if manip is not None:
            q = self.neutral.copy()
            for j, v in manip.targets.items():
                q[j] = v
            arm_owner, mode, speed = "manipulacja", "manipulation", manip.speed_scale
            for layer in (Layer.TRACKING, Layer.EXPRESSIVE):
                if layer in req:
                    suppressed.append(f"{LAYER_LABELS[layer]}: manipulacja ma pierwszeństwo")
        else:
            q = self.neutral.copy()
            arm_owner, mode = "pozycja bazowa", "expressive"
            track = req.get(Layer.TRACKING)
            if track is not None:
                w = float(np.clip(track.weight, 0.0, 1.0))
                for j, v in track.targets.items():
                    q[j] = q[j] + (v - q[j]) * w
                arm_owner = "śledzenie"
                speed = min(speed, track.speed_scale)
            expr = req.get(Layer.EXPRESSIVE)
            if expr is not None:
                if gripper_locked:
                    suppressed.append("gest: chwytak trzyma obiekt")
                else:
                    for j, v in expr.offsets.items():
                        if j != GRIPPER:
                            q[j] += v * expr.weight
                    arm_owner = f"{arm_owner} + {expr.label}"
                    speed = min(speed, expr.speed_scale)
            q, _ = clamp_expressive(q)
        jaw = req.get(Layer.JAW)
        if manip is not None:
            gripper_owner = "manipulacja - trzymanie" if gripper_locked else "manipulacja"
            if jaw is not None:
                reason = "chwytak trzyma obiekt" if gripper_locked else "manipulacja ma pierwszeństwo"
                suppressed.append(f"szczęka: {reason}")
        elif gripper_locked:
            q[GRIPPER] = hold_value
            gripper_owner = "utrzymanie obiektu"
            if jaw is not None:
                suppressed.append("szczęka: chwytak trzyma obiekt")
        elif jaw is not None:
            q[GRIPPER] = jaw.targets.get(GRIPPER, self.neutral[GRIPPER])
            gripper_owner = "szczęka"
        else:
            q[GRIPPER] = self.neutral[GRIPPER]
            gripper_owner = "pozycja bazowa"
        key = "manipulation" if manip is not None else "expressive"
        if self._last_key is not None and key != self._last_key and self._last_q is not None:
            self._blend_from = self._last_q[:5].copy()
            self._blend_t0 = t
        if self._blend_from is not None:
            s = min_jerk((t - self._blend_t0) / self.blend_time)
            q[:5] = self._blend_from + (q[:5] - self._blend_from) * s
            if s >= 1.0:
                self._blend_from = None
        self._last_q = q.copy()
        self._last_key = key
        self._last_mode = mode
        return Decision(q, arm_owner, gripper_owner, tuple(suppressed), speed, mode)
