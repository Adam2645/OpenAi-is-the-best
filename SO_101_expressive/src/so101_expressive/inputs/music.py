from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


# stan muzyki zawiera wynik i tempo, żeby planista mógł dopasować taniec do rytmu
@dataclass(frozen=True)
class MusicState:
    music: bool
    score: float
    bpm: float
    evaluated: bool


# prosty, testowalny detektor muzyki na cechach rytmu, ciągłości i tonalności, bez obietnicy rozumienia utworu
class MusicDetector:
    # okno kilku sekund i histereza chronią przed przełączaniem tańca przy krótkich dźwiękach
    def __init__(
        self,
        rate: int = 16000,
        frame: int = 512,
        window_s: float = 6.0,
        eval_every_s: float = 0.5,
        on_score: float = 0.6,
        off_score: float = 0.4,
        on_evals: int = 2,
        off_evals: int = 4,
        min_valid_s: float = 4.0,
    ) -> None:
        self.rate = rate
        self.frame = frame
        self.hop_s = frame / rate
        self.window = int(window_s / self.hop_s)
        self.eval_every = max(1, int(eval_every_s / self.hop_s))
        self.on_score, self.off_score = on_score, off_score
        self.on_evals, self.off_evals = on_evals, off_evals
        self.min_valid = int(min_valid_s / self.hop_s)
        freqs = np.fft.rfftfreq(frame, 1.0 / rate)
        self.band = (freqs >= 60.0) & (freqs <= 5000.0)
        self.hann = np.hanning(frame).astype(np.float32)
        self.smooth_kernel = np.ones(9) / 9.0
        self._leftover = np.zeros(0, dtype=np.float32)
        self._rms: deque[float] = deque(maxlen=self.window)
        self._flux: deque[float] = deque(maxlen=self.window)
        self._persist: deque[float] = deque(maxlen=self.window)
        self._valid: deque[bool] = deque(maxlen=self.window)
        self._prev_log: np.ndarray | None = None
        self._prev_peaks: np.ndarray | None = None
        self._count = 0
        self._on = 0
        self._off = 0
        self.music = False
        self.score = 0.0
        self.bpm = 0.0
        self.last_features: dict[str, float] = {}

    # cechy ramki: głośność, nowość widma i trwałość wyraźnych pików tonalnych względem lokalnego tła widma
    def _frame_features(self, x: np.ndarray) -> tuple[float, float, float]:
        rms = float(np.sqrt(np.mean(x * x)))
        spec = np.abs(np.fft.rfft(x * self.hann))[self.band]
        logmag = np.log10(spec + 1e-5)
        flux = 0.0 if self._prev_log is None else float(np.sum(np.maximum(logmag - self._prev_log, 0.0)))
        db = 20.0 * np.log10(spec + 1e-9)
        padded = np.pad(db, 4, mode="edge")
        prominence = db - np.convolve(padded, self.smooth_kernel, mode="valid")
        gate = db > (db.max() - 50.0)
        peaks = np.zeros(spec.size, dtype=bool)
        peaks[1:-1] = (spec[1:-1] > spec[:-2]) & (spec[1:-1] >= spec[2:]) & (prominence[1:-1] > 8.0) & gate[1:-1]
        persistence = 0.0
        if self._prev_peaks is not None and peaks.any():
            prev = self._prev_peaks.copy()
            prev[1:] |= self._prev_peaks[:-1]
            prev[:-1] |= self._prev_peaks[1:]
            energy = spec * spec
            persistence = float(energy[peaks & prev].sum() / max(energy[peaks].sum(), 1e-12))
        self._prev_log = logmag
        self._prev_peaks = peaks
        return rms, flux, persistence

    # blok z mikrofonu jest dzielony na ramki, a ramki nakładające się na mowę robota są oznaczane jako niewiarygodne
    def update(self, block: np.ndarray, own_playback: bool) -> MusicState:
        x = np.concatenate([self._leftover, block.astype(np.float32) / 32768.0])
        n = x.size // self.frame
        evaluated = False
        for i in range(n):
            rms, flux, persistence = self._frame_features(x[i * self.frame : (i + 1) * self.frame])
            self._rms.append(rms)
            self._flux.append(flux)
            self._persist.append(persistence)
            self._valid.append(not own_playback)
            self._count += 1
            if self._count % self.eval_every == 0:
                self._evaluate()
                evaluated = True
        self._leftover = x[n * self.frame :]
        return MusicState(self.music, self.score, self.bpm, evaluated)

    # ocena okna łączy trzy cechy w wynik z histerezą i pomija okna zdominowane przez własny dźwięk robota
    def _evaluate(self) -> None:
        valid = np.array(self._valid, dtype=bool)
        if valid.size < self.min_valid or valid.mean() < 0.7:
            return
        rms = np.array(self._rms)[valid]
        persist = np.array(self._persist)[valid]
        flux = np.array(self._flux)
        flux = np.where(valid, flux, np.mean(flux[valid]))
        active = float(np.mean(rms > 10 ** (-48 / 20)))
        low_energy = float(np.mean(rms < 0.5 * np.mean(rms))) if rms.size else 1.0
        env = flux - flux.mean()
        denom = float(np.dot(env, env)) + 1e-9
        lo_lag = int(round(0.33 / self.hop_s))
        hi_lag = min(int(round(1.0 / self.hop_s)), env.size - 2)
        pulse, lag = 0.0, 0
        for L in range(lo_lag, hi_lag + 1):
            c = float(np.dot(env[:-L], env[L:])) / denom
            if c > pulse:
                pulse, lag = c, L
        tonal = float(np.mean(persist))
        s_energy = 1.0 - min(max(low_energy / 0.35, 0.0), 1.0)
        s_pulse = min(max((pulse - 0.12) / 0.33, 0.0), 1.0)
        s_tonal = min(max((tonal - 0.25) / 0.35, 0.0), 1.0)
        score = 0.35 * s_energy + 0.35 * s_pulse + 0.30 * s_tonal
        rhythm = min(max((pulse - 0.20) / 0.20, 0.0), 1.0)
        score = max(score, 0.9 * rhythm)
        if active < 0.6:
            score = 0.0
        self.score = score
        self.last_features = {
            "active": active, "low_energy": low_energy, "pulse": pulse, "tonal": tonal, "score": score,
        }
        if lag:
            self.bpm = 60.0 / (lag * self.hop_s)
        if score > self.on_score:
            self._on += 1
            self._off = 0
        elif score < self.off_score:
            self._off += 1
            self._on = 0
        if not self.music and self._on >= self.on_evals:
            self.music = True
        elif self.music and self._off >= self.off_evals:
            self.music = False
