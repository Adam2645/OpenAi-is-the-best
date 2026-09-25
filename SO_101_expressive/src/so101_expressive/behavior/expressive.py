from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

Offsets = tuple[float, float, float, float, float]
ZERO: Offsets = (0.0, 0.0, 0.0, 0.0, 0.0)


# interpolacja minimalnego szarpnięcia daje zerową prędkość w punktach kluczowych, więc gesty są płynne
def min_jerk(s: float) -> float:
    s = min(max(s, 0.0), 1.0)
    return s * s * s * (10.0 - 15.0 * s + 6.0 * s * s)


# gest to zamknięta sekwencja przesunięć pięciu przegubów ramienia, zaczynająca i kończąca się zerem
@dataclass(frozen=True)
class Gesture:
    name: str
    label_pl: str
    duration: float
    keyframes: tuple[tuple[float, Offsets], ...]


GESTURES: dict[str, Gesture] = {
    "nod": Gesture("nod", "przytaknięcie", 1.3, (
        (0.0, ZERO), (0.25, (0.0, 0.04, 0.0, 0.28, 0.0)), (0.5, (0.0, 0.0, 0.0, -0.03, 0.0)),
        (0.75, (0.0, 0.03, 0.0, 0.22, 0.0)), (1.0, ZERO))),
    "shake_head": Gesture("shake_head", "zaprzeczenie", 1.5, (
        (0.0, ZERO), (0.2, (0.22, 0.0, 0.0, 0.0, 0.05)), (0.45, (-0.22, 0.0, 0.0, 0.0, -0.05)),
        (0.7, (0.18, 0.0, 0.0, 0.0, 0.04)), (0.88, (-0.08, 0.0, 0.0, 0.0, 0.0)), (1.0, ZERO))),
    "wave": Gesture("wave", "machnięcie na powitanie", 2.6, (
        (0.0, ZERO), (0.2, (0.0, -0.35, -0.45, -0.35, 0.0)), (0.35, (0.0, -0.35, -0.45, -0.35, 0.5)),
        (0.5, (0.0, -0.35, -0.45, -0.35, -0.5)), (0.65, (0.0, -0.35, -0.45, -0.35, 0.5)),
        (0.8, (0.0, -0.35, -0.45, -0.35, 0.0)), (1.0, ZERO))),
    "shrug": Gesture("shrug", "wzruszenie ramion", 1.8, (
        (0.0, ZERO), (0.3, (0.0, -0.12, -0.12, -0.10, 0.35)), (0.6, (0.0, -0.12, -0.12, -0.10, 0.35)),
        (1.0, ZERO))),
    "think": Gesture("think", "zastanowienie", 2.4, (
        (0.0, ZERO), (0.35, (0.10, -0.05, 0.0, -0.25, 0.40)), (0.75, (0.12, -0.05, 0.0, -0.28, 0.42)),
        (1.0, ZERO))),
    "happy": Gesture("happy", "radość", 1.8, (
        (0.0, ZERO), (0.15, (0.0, -0.10, 0.0, -0.10, 0.20)), (0.3, (0.0, 0.05, 0.0, 0.05, -0.20)),
        (0.45, (0.0, -0.10, 0.0, -0.10, 0.20)), (0.6, (0.0, 0.05, 0.0, 0.05, -0.20)),
        (0.8, (0.0, -0.06, 0.0, -0.06, 0.10)), (1.0, ZERO))),
    "surprised": Gesture("surprised", "zaskoczenie", 1.8, (
        (0.0, ZERO), (0.2, (0.0, -0.25, -0.10, -0.30, 0.0)), (0.6, (0.0, -0.22, -0.10, -0.28, 0.0)),
        (1.0, ZERO))),
    "bow": Gesture("bow", "ukłon", 2.4, (
        (0.0, ZERO), (0.35, (0.0, 0.30, 0.10, 0.45, 0.0)), (0.65, (0.0, 0.30, 0.10, 0.45, 0.0)),
        (1.0, ZERO))),
    "look_around": Gesture("look_around", "rozglądanie się", 3.2, (
        (0.0, ZERO), (0.3, (0.50, 0.0, 0.0, -0.05, 0.0)), (0.7, (-0.50, 0.0, 0.0, -0.05, 0.0)),
        (1.0, ZERO))),
    "curious": Gesture("curious", "zaciekawienie", 2.0, (
        (0.0, ZERO), (0.4, (0.0, 0.10, 0.0, -0.05, 0.38)), (0.7, (0.0, 0.10, 0.0, -0.05, 0.40)),
        (1.0, ZERO))),
}
INTENSITY = {"subtle": 0.5, "normal": 1.0, "strong": 1.3}


# odtwarzanie gestu z łagodnym przerwaniem chroni przed skokiem, gdy plan zmienia się w połowie ruchu
class GesturePlayback:
    # intensywność skaluje cały gest, a limity i tak nakłada później bezpieczny sterownik
    def __init__(self, gesture: Gesture, t0: float, intensity: float = 1.0) -> None:
        self.gesture = gesture
        self.t0 = t0
        self.intensity = intensity
        self._cancel_t: float | None = None
        self._fade = 0.35

    # nazwa gestu trafia do stanu robota i interfejsu
    @property
    def name(self) -> str:
        return self.gesture.name

    # przesunięcia w danej chwili wynikają z interpolacji między klatkami kluczowymi
    def offsets(self, t: float) -> np.ndarray:
        tau = (t - self.t0) / self.gesture.duration
        frames = self.gesture.keyframes
        value = np.zeros(5)
        if 0.0 < tau < 1.0:
            for (f0, o0), (f1, o1) in zip(frames, frames[1:]):
                if f0 <= tau <= f1:
                    s = min_jerk((tau - f0) / max(f1 - f0, 1e-6))
                    value = np.asarray(o0) + (np.asarray(o1) - np.asarray(o0)) * s
                    break
        value = value * self.intensity
        if self._cancel_t is not None:
            value = value * (1.0 - min_jerk((t - self._cancel_t) / self._fade))
        return value

    # przerwanie wygasza gest zamiast go ucinać, co zapobiega szarpnięciu przy przerwaniu mowy
    def cancel(self, t: float, fade: float = 0.35) -> None:
        if self._cancel_t is None:
            self._cancel_t = t
            self._fade = fade

    # gest kończy się po czasie trwania lub po wygaszeniu przerwania
    def done(self, t: float) -> bool:
        if self._cancel_t is not None and t - self._cancel_t >= self._fade:
            return True
        return t - self.t0 >= self.gesture.duration


# taniec to łagodny rytmiczny ruch w tempie wykrytej muzyki z ograniczoną amplitudą
class DanceBehavior:
    # czas narastania chroni przed gwałtownym startem tańca w środku innego ruchu
    def __init__(self, amplitude: float = 1.0, ramp_s: float = 1.5) -> None:
        self.amplitude = amplitude
        self.ramp_s = ramp_s
        self.bpm = 100.0
        self._active = False
        self._t_start = 0.0
        self._t_stop: float | None = None
        self._phase = 0.0
        self._last_t: float | None = None
        self._end_at: float | None = None

    # start z opcjonalnym czasem trwania obsługuje zarówno muzykę, jak i prośbę z rozmowy
    def start(self, t: float, bpm: float | None = None, duration: float | None = None) -> None:
        if bpm:
            self.set_bpm(bpm)
        if not self._active or self._t_stop is not None:
            self._t_start = t
        self._active = True
        self._t_stop = None
        self._end_at = None if duration is None else t + duration

    # zatrzymanie wygasza taniec, żeby nie było skoku do pozycji bazowej
    def stop(self, t: float) -> None:
        if self._active and self._t_stop is None:
            self._t_stop = t

    # zbyt szybkie tempo dzielimy na pół, bo ramię nie powinno machać w rytmie szybkiej perkusji
    def set_bpm(self, bpm: float) -> None:
        bpm = float(np.clip(bpm, 60.0, 180.0))
        while bpm / 60.0 > 1.8:
            bpm /= 2.0
        self.bpm = bpm

    # stan aktywności obejmuje fazę wygaszania, żeby planista wiedział, że ruch jeszcze trwa
    def running(self, t: float) -> bool:
        if not self._active:
            return False
        if self._t_stop is not None and t - self._t_stop >= self.ramp_s:
            self._active = False
            return False
        return True

    # faza jest całkowana w czasie, więc zmiana tempa nie powoduje skoku pozycji
    def offsets(self, t: float, attenuation: float = 1.0) -> np.ndarray:
        if self._end_at is not None and t >= self._end_at:
            self.stop(t)
        if not self.running(t):
            self._last_t = t
            return np.zeros(5)
        dt = 0.0 if self._last_t is None else max(0.0, t - self._last_t)
        self._last_t = t
        self._phase += 2.0 * math.pi * (self.bpm / 60.0) * dt
        env = min_jerk((t - self._t_start) / self.ramp_s)
        if self._t_stop is not None:
            env *= 1.0 - min_jerk((t - self._t_stop) / self.ramp_s)
        beat = self._phase
        sway = self._phase / 2.0
        pose = np.array([
            0.12 * math.sin(sway),
            0.035 * math.sin(beat),
            0.0,
            0.07 * math.sin(beat),
            0.22 * math.sin(sway + math.pi / 2.0),
        ])
        return pose * env * self.amplitude * attenuation


# mikroruch ożywia robota podczas słuchania i mówienia, ale tylko przy widocznym rozmówcy
class MicroMotion:
    # wygładzanie wyjścia chroni przed przeskokiem przy zmianie trybu słuchania na mówienie
    def __init__(self, tau_s: float = 0.35) -> None:
        self.tau_s = tau_s
        self._y = np.zeros(5)
        self._level = 0.0

    # oddech przy słuchaniu i delikatne kiwanie przy mówieniu mają amplitudy rzędu kilku stopni
    def offsets(self, t: float, dt: float, enabled: bool, listening: bool, speaking: bool, level: float) -> np.ndarray:
        self._level += (level - self._level) * (1.0 - math.exp(-dt / 0.3))
        goal = np.zeros(5)
        if enabled and listening:
            goal[1] = 0.012 * math.sin(2.0 * math.pi * 0.18 * t)
        if enabled and speaking:
            goal[3] = -0.08 * self._level + 0.02 * math.sin(2.0 * math.pi * 0.4 * t)
            goal[4] = 0.04 * math.sin(2.0 * math.pi * 0.23 * t)
        self._y += (goal - self._y) * (1.0 - math.exp(-dt / self.tau_s))
        return self._y.copy()
