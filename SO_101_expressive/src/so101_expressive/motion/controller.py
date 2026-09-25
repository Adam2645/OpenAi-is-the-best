from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .limits import JOINT_NAMES, JointLimit

PoseClearance = Callable[[np.ndarray, str], float]


# raport z każdego kroku pozwala zliczać interwencje bezpieczeństwa i pokazywać je w stanie robota
@dataclass(frozen=True)
class ControllerReport:
    clamped: tuple[str, ...] = ()
    nonfinite: tuple[str, ...] = ()
    workspace_blocked: bool = False
    estop: bool = False
    stopped: bool = False


# jedyna droga do serw prowadzi przez ten sterownik, który egzekwuje limity niezależnie od źródła polecenia
class SafeMotionController:
    # sterownik trzyma własny stan pozycji i prędkości zadanej, aby trajektoria była ciągła
    def __init__(
        self,
        limits: tuple[JointLimit, ...],
        dt: float,
        pose_clearance: PoseClearance | None = None,
        estop_decel_factor: float = 2.0,
    ) -> None:
        if len(limits) != len(JOINT_NAMES):
            raise ValueError("wymagane są limity dla wszystkich przegubów")
        self.limits = limits
        self.dt = float(dt)
        self.pose_clearance = pose_clearance
        self.estop_decel_factor = estop_decel_factor
        self.lo = np.array([lim.lo for lim in limits])
        self.hi = np.array([lim.hi for lim in limits])
        self.vmax = np.array([lim.vmax for lim in limits])
        self.amax = np.array([lim.amax for lim in limits])
        self.q = np.zeros(len(limits))
        self.v = np.zeros(len(limits))
        self._initialized = False

    # start od zmierzonej pozycji zapobiega skokowi przy pierwszym poleceniu
    def reset(self, q_measured: np.ndarray) -> None:
        self.q = np.clip(np.asarray(q_measured, dtype=float).copy(), self.lo, self.hi)
        self.v = np.zeros_like(self.q)
        self._initialized = True

    # pojedynczy krok przelicza cel na bezpieczną pozycję zadaną z ograniczeniem prędkości i przyspieszenia
    def step(
        self,
        q_des: np.ndarray,
        speed_scale: float = 1.0,
        estop: bool = False,
        mode: str = "expressive",
    ) -> ControllerReport:
        if not self._initialized:
            raise RuntimeError("sterownik wymaga reset() przed pierwszym krokiem")
        dt = self.dt
        target = np.asarray(q_des, dtype=float).copy()
        nonfinite = tuple(JOINT_NAMES[i] for i in range(len(target)) if not np.isfinite(target[i]))
        target = np.where(np.isfinite(target), target, self.q)
        clipped_target = np.clip(target, self.lo, self.hi)
        clamped = tuple(JOINT_NAMES[i] for i in range(len(target)) if abs(clipped_target[i] - target[i]) > 1e-9)
        if estop:
            v_goal = np.zeros_like(self.v)
            accel = self.amax * self.estop_decel_factor
        else:
            scale = float(np.clip(speed_scale, 0.05, 1.0))
            err = clipped_target - self.q
            half = 0.5 * self.amax * dt
            v_brake = np.sqrt(half * half + 2.0 * self.amax * np.abs(err)) - half
            v_goal = np.sign(err) * np.minimum.reduce([self.vmax * scale, v_brake, np.abs(err) / dt])
            accel = self.amax
        v_new, q_new = self._integrate(v_goal, accel, clipped_target, estop)
        blocked = False
        if not estop and self.pose_clearance is not None:
            stop_dist = v_new * np.abs(v_new) / (2.0 * self.amax)
            ahead = self.pose_clearance(np.clip(q_new + stop_dist, self.lo, self.hi), mode)
            if ahead < 0.0 and ahead < self.pose_clearance(self.q, mode) - 1e-4:
                blocked = True
                v_new, q_new = self._integrate(np.zeros_like(self.v), self.amax, clipped_target, True)
        self.v = v_new
        self.q = np.clip(q_new, self.lo, self.hi)
        stopped = bool(np.all(np.abs(self.v) < 1e-6))
        return ControllerReport(clamped, nonfinite, blocked, estop, stopped)

    # całkowanie jest wydzielone, bo ten sam krok hamowania służy do stopu i do blokady przestrzeni roboczej
    def _integrate(
        self, v_goal: np.ndarray, accel: np.ndarray, target: np.ndarray, braking: bool
    ) -> tuple[np.ndarray, np.ndarray]:
        dt = self.dt
        dv = np.clip(v_goal - self.v, -accel * dt, accel * dt)
        v_new = self.v + dv
        q_new = self.q + v_new * dt
        if not braking:
            before = target - self.q
            after = target - q_new
            can_stop = np.abs(self.v) <= accel * dt + 1e-12
            crossed = np.sign(before) != np.sign(after)
            settle = np.abs(after) < 1e-6
            snap = (crossed | settle) & can_stop
            q_new = np.where(snap, target, q_new)
            v_new = np.where(snap, 0.0, v_new)
        return v_new, q_new
