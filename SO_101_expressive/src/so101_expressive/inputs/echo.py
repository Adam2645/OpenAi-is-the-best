from __future__ import annotations

from dataclasses import dataclass

SILENT_REF = 10 ** (-50 / 20)


# decyzja bramki mówi, czy blok mikrofonu może trafić do chmury i czy wykryto przerwanie użytkownika
@dataclass(frozen=True)
class GateDecision:
    pass_audio: bool
    barge_in: bool
    expected_echo: float
    ratio: float


# głośniki laptopa bez usuwania echa sprawiają, że model słyszy sam siebie, więc w czasie mowy robota mikrofon jest bramkowany
class EchoGate:
    # sprzężenie głośnik-mikrofon jest estymowane w trakcie mowy robota, a przerwanie wymaga wyraźnie głośniejszego głosu
    def __init__(
        self,
        mode: str = "half_duplex",
        barge_in_ratio: float = 3.0,
        barge_in_min_ms: float = 120.0,
        min_open_ms: float = 500.0,
        coupling_init: float = 0.35,
    ) -> None:
        self.mode = mode
        self.barge_in_ratio = barge_in_ratio
        self.barge_in_min_s = barge_in_min_ms / 1000.0
        self.min_open_s = min_open_ms / 1000.0
        self.coupling = coupling_init
        self._run = 0.0
        self._open_left = 0.0
        self.open = False

    # półdupleks obejmuje całą turę robota razem z pauzami między słowami, a nie tylko chwile słyszalnego dźwięku
    def process(self, mic_rms: float, ref_peak: float, dt: float, noise_floor: float, robot_active: bool | None = None) -> GateDecision:
        if self.mode == "off":
            return GateDecision(True, False, 0.0, 0.0)
        active = ref_peak >= SILENT_REF if robot_active is None else robot_active
        if not active:
            self._run = 0.0
            self._open_left = 0.0
            self.open = False
            return GateDecision(True, False, 0.0, 0.0)
        expected = self.coupling * ref_peak + noise_floor
        ratio = mic_rms / max(expected, 1e-6)
        barge = False
        if self.open:
            self._open_left -= dt
            if ratio < 1.5 and self._open_left <= 0.0:
                self.open = False
        else:
            if ratio > self.barge_in_ratio:
                self._run += dt
                if self._run >= self.barge_in_min_s:
                    self.open = True
                    barge = True
                    self._open_left = self.min_open_s
            else:
                self._run = 0.0
                if ref_peak >= SILENT_REF:
                    measured = mic_rms / max(ref_peak, 1e-6)
                    self.coupling += (min(max(measured, 0.02), 2.0) - self.coupling) * min(1.0, dt / 2.0)
        return GateDecision(self.open, barge, expected, ratio)
