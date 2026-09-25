from __future__ import annotations

import math


# szczęka mapuje głośność faktycznie odtwarzanego dźwięku na rozwarcie chwytaka, nie tekst odpowiedzi
class JawBehavior:
    # progi w decybelach i stałe czasowe dobierają ruch do sylab bez drgań przy cichym szumie
    def __init__(
        self,
        closed: float = 0.0,
        open_max: float = 0.45,
        floor_db: float = -42.0,
        ceil_db: float = -14.0,
        attack_s: float = 0.03,
        release_s: float = 0.09,
    ) -> None:
        self.closed = closed
        self.open_max = open_max
        self.floor_db = floor_db
        self.ceil_db = ceil_db
        self.attack_s = attack_s
        self.release_s = release_s
        self._y = 0.0

    # rozwarcie w zakresie od zera do jedynki trafia do stanu i do testów synchronizacji
    @property
    def opening(self) -> float:
        return self._y

    # obwiednia z szybkim narastaniem i wolniejszym opadaniem przypomina ruch ust przy mowie
    def target(self, level_rms: float, dt: float) -> float:
        db = 20.0 * math.log10(max(level_rms, 1e-6))
        x = min(max((db - self.floor_db) / (self.ceil_db - self.floor_db), 0.0), 1.0)
        tau = self.attack_s if x > self._y else self.release_s
        self._y += (x - self._y) * (1.0 - math.exp(-dt / tau))
        return self.closed + self.open_max * self._y

    # reset zamyka szczękę natychmiast w obliczeniach, gdy chwytak przejmuje warstwa trzymania
    def reset(self) -> None:
        self._y = 0.0
