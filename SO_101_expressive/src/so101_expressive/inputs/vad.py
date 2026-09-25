from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# decyzja vad dla bloku mówi, czy wysyłać dźwięk do chmury i kiedy zaczęła lub skończyła się wypowiedź
@dataclass(frozen=True)
class VadDecision:
    speech: bool
    started: bool
    ended: bool
    rms: float
    floor: float


# lokalny detektor mowy ogranicza wysyłanie ciszy, bo w gemini 3.8 live płaci się za cały strumień wejściowy
class EnergyVad:
    # próg względem adaptacyjnego szumu tła i zwłoka końca mowy co najmniej 500 ms zgodnie z dokumentacją live api
    def __init__(
        self,
        rate: int = 16000,
        ratio: float = 3.2,
        abs_min: float = 10 ** (-52 / 20),
        start_ms: float = 90.0,
        hangover_ms: float = 600.0,
    ) -> None:
        self.rate = rate
        self.ratio = ratio
        self.abs_min = abs_min
        self.start_s = start_ms / 1000.0
        self.hangover_s = hangover_ms / 1000.0
        self.floor = abs_min
        self.speech = False
        self._run = 0.0
        self._quiet = 0.0

    # szum tła opada szybko i rośnie powoli, więc ciągła muzyka z czasem podnosi próg, a mowa nie
    def _update_floor(self, rms: float, dt: float) -> None:
        if rms < self.floor:
            self.floor += (rms - self.floor) * min(1.0, dt / 0.3)
        else:
            self.floor += (rms - self.floor) * min(1.0, dt / 6.0)
        self.floor = max(self.floor, self.abs_min)

    # przetworzenie bloku aktualizuje próg i stan mowy z histerezą startu i końca
    def process(self, block: np.ndarray) -> VadDecision:
        x = block.astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(x * x))) if x.size else 0.0
        dt = block.size / self.rate
        loud = rms > max(self.abs_min, self.floor * self.ratio)
        started = ended = False
        if loud:
            self._run += dt
            self._quiet = 0.0
        else:
            self._run = 0.0
            self._quiet += dt
        if not self.speech and self._run >= self.start_s:
            self.speech = True
            started = True
        elif self.speech and self._quiet >= self.hangover_s:
            self.speech = False
            ended = True
        if not self.speech or not loud:
            self._update_floor(rms, dt)
        return VadDecision(self.speech, started, ended, rms, self.floor)

    # zawieszenie przy zamkniętej bramce echa kończy stan mowy bez uczenia progu na echu robota
    def suspend(self, rms: float = 0.0) -> VadDecision:
        ended = self.speech
        self.speech = False
        self._run = 0.0
        self._quiet = 0.0
        return VadDecision(False, False, ended, rms, self.floor)
