from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ..motion.kinematics import So101Kinematics
from ..motion.limits import PAN, WRIST_FLEX
from ..state import PersonStatus


# obserwacja z lokalnej pętli wizji ma znacznik czasu i status, żeby niepewność blokowała ruch
@dataclass(frozen=True)
class PersonObservation:
    status: PersonStatus
    t: float
    u: float = 0.0
    v: float = 0.0
    size: float = 0.0
    confidence: float = 0.0


# wyjście śledzenia zawiera cele tylko dla obrotu i nadgarstka oraz wagę płynnego włączania
@dataclass(frozen=True)
class TrackingOutput:
    targets: dict[int, float] | None
    weight: float
    gaze_target: tuple[float, float, float] | None
    active: bool


# śledzenie rozmówcy w granicach mechaniki so-101 używa obrotu podstawy i pochylenia chwytaka jako głowy
class TrackingBehavior:
    # geometria kamery laptopa jest przybliżona, dlatego wzmocnienia i strefa martwa są konfigurowalne
    def __init__(
        self,
        kin: So101Kinematics,
        hfov_deg: float = 70.0,
        aspect: float = 4.0 / 3.0,
        head_height: float = 0.30,
        face_width_m: float = 0.16,
        deadband_rad: float = 0.035,
        tau_s: float = 0.25,
        ramp_s: float = 0.6,
        return_to_neutral_s: float = 0.0,
    ) -> None:
        self.kin = kin
        self.tan_h = math.tan(math.radians(hfov_deg) / 2.0)
        self.tan_v = self.tan_h / aspect
        self.head_height = head_height
        self.face_width_m = face_width_m
        self.deadband = deadband_rad
        self.tau_s = tau_s
        self.ramp_s = ramp_s
        self.return_to_neutral_s = return_to_neutral_s
        self._cur: np.ndarray | None = None
        self._following = False
        self._weight = 0.0
        self._paused_until = 0.0
        self._last_seen = -1e9
        self._last_point: tuple[float, float, float] | None = None

    # punkt w przestrzeni robota wyliczamy z pozycji i wielkości twarzy w obrazie
    def target_point(self, obs: PersonObservation) -> np.ndarray:
        size = max(obs.size, 1e-3)
        distance = float(np.clip(self.face_width_m / (2.0 * self.tan_h * size), 0.4, 2.2))
        y = -obs.u * distance * self.tan_h
        z = self.head_height - obs.v * distance * self.tan_v
        return np.array([distance, y, z])

    # pauza uwagi pozwala modelowi poprosić o spojrzenie w bok bez wyłączania śledzenia na stałe
    def pause(self, t: float, duration: float) -> None:
        self._paused_until = t + duration

    # wznowienie przywraca śledzenie przy następnej pewnej detekcji
    def resume(self) -> None:
        self._paused_until = 0.0

    # przy niepewnej detekcji lub braku osoby cel jest zamrażany, więc ramię się nie porusza
    def update(self, obs: PersonObservation, t: float, dt: float, posture: np.ndarray) -> TrackingOutput:
        paused = t < self._paused_until
        tracked = obs.status is PersonStatus.TRACKED and not paused
        if tracked:
            point = self.target_point(obs)
            self._last_point = (float(point[0]), float(point[1]), float(point[2]))
            self._last_seen = t
            goal = np.array(self.kin.gaze(point, posture))
            if self._cur is None:
                self._cur = goal.copy()
            err = float(np.max(np.abs(goal - self._cur)))
            if err > self.deadband:
                self._following = True
            elif err < self.deadband / 3.0:
                self._following = False
            if self._following:
                self._cur = self._cur + (goal - self._cur) * (1.0 - math.exp(-dt / self.tau_s))
            self._weight = min(1.0, self._weight + dt / self.ramp_s)
        else:
            self._following = False
            fade = paused or (
                self.return_to_neutral_s > 0.0 and t - self._last_seen > self.return_to_neutral_s
            )
            if fade:
                self._weight = max(0.0, self._weight - dt / 2.0)
        if self._cur is None or self._weight <= 0.0:
            if self._weight <= 0.0:
                self._cur = None
            return TrackingOutput(None, 0.0, self._last_point if tracked else None, False)
        targets = {PAN: float(self._cur[0]), WRIST_FLEX: float(self._cur[1])}
        gaze = self._last_point if obs.status in (PersonStatus.TRACKED, PersonStatus.UNCERTAIN) else None
        return TrackingOutput(targets, self._weight, gaze, tracked)
