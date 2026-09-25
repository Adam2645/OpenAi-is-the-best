from __future__ import annotations

import wave
from pathlib import Path
from typing import Callable

import numpy as np

from .audio_pipeline import AudioPipeline
from .playback import PlaybackBuffer

Source = Callable[[float, int, int], np.ndarray]


# źródło dźwięku z nagrania odtwarzane od zadanej chwili, np. muzyka w pokoju albo głos rozmówcy
def clip_source(samples: np.ndarray, rate: int, t_start: float, gain: float = 1.0) -> Source:
    x = samples.astype(np.float32) / (32768.0 if samples.dtype == np.int16 else 1.0)

    # zwraca fragment nagrania dla przedziału czasu, a poza nim ciszę
    def source(t: float, n: int, out_rate: int) -> np.ndarray:
        start = int(round((t - t_start) * rate))
        idx = start + np.arange(n) * (rate / out_rate)
        valid = (idx >= 0) & (idx < x.size - 1)
        out = np.zeros(n, dtype=np.float32)
        if valid.any():
            out[valid] = np.interp(idx[valid], np.arange(x.size), x)
        return out * gain

    return source


# wirtualny zestaw audio zastępuje głośnik i mikrofon laptopa: miesza echo robota, źródła z pokoju i szum
class VirtualAudioRig:
    # parametry echa odwzorowują sprzężenie głośników i mikrofonu w obudowie laptopa
    def __init__(
        self,
        playback: PlaybackBuffer,
        pipeline: AudioPipeline | None,
        mic_rate: int = 16000,
        block: int = 512,
        echo_gain: float = 0.3,
        echo_delay_s: float = 0.03,
        noise_rms: float = 0.002,
        latency: float = 0.02,
        seed: int = 0,
    ) -> None:
        self.playback = playback
        self.pipeline = pipeline
        self.mic_rate = mic_rate
        self.block = block
        self.echo_gain = echo_gain
        self.latency = latency
        self.noise_rms = noise_rms
        self.sources: list[Source] = []
        self._rng = np.random.default_rng(seed)
        self._echo = np.zeros(int(echo_delay_s * mic_rate), dtype=np.float32)
        self._mic = np.zeros(0, dtype=np.float32)
        self._mic_t = None
        self._spk_frac = 0.0
        self._mic_frac = 0.0
        self._t = 0.0
        self.mic_log: list[tuple[float, np.ndarray]] = []
        self.keep_log = False
        self._track_speaker: list[np.ndarray] | None = None
        self._track_room: list[np.ndarray] | None = None

    # dodanie źródła symuluje dźwięk w pokoju, który słyszy mikrofon
    def add_source(self, source: Source) -> None:
        self.sources.append(source)

    # ścieżka dźwiękowa nagrania dema pozwala usłyszeć mowę robota i pokój razem z obrazem ruchu szczęki
    def enable_soundtrack(self) -> None:
        self._track_speaker = []
        self._track_room = []

    # zapis uwzględnia opóźnienie głośnika, więc dźwięk w nagraniu zgadza się w czasie z ruchem ramienia
    def save_soundtrack(self, path: Path) -> float:
        if not self._track_speaker:
            return 0.0
        rate = self.playback.rate
        room = np.concatenate(self._track_room)
        delay = np.zeros(int(round(self.latency * rate)), dtype=np.float32)
        speaker = np.concatenate([delay] + self._track_speaker)[: room.size]
        mix = room + speaker
        peak = float(np.max(np.abs(mix))) if mix.size else 0.0
        if peak > 0.95:
            mix = mix * (0.95 / peak)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes((np.clip(mix, -1.0, 1.0) * 32767).astype("<i2").tobytes())
        return mix.size / rate

    # krok zestawu pobiera próbki z głośnika i tworzy odpowiadający im sygnał mikrofonu
    def tick(self, t: float, dt: float) -> None:
        exact = dt * self.playback.rate + self._spk_frac
        frames = int(exact)
        self._spk_frac = exact - frames
        out = self.playback.pull(frames, t + self.latency).astype(np.float32) / 32768.0
        if self._track_speaker is not None:
            room = np.zeros(frames, dtype=np.float32)
            for source in self.sources:
                room += source(t, frames, self.playback.rate)
            self._track_speaker.append(out.copy())
            self._track_room.append(room)
        exact_mic = dt * self.mic_rate + self._mic_frac
        n = int(exact_mic)
        self._mic_frac = exact_mic - n
        if out.size and n:
            resampled = np.interp(np.arange(n) * (out.size / n), np.arange(out.size), out)
        else:
            resampled = np.zeros(n, dtype=np.float32)
        line = np.concatenate([self._echo, resampled.astype(np.float32)])
        mic = line[:n] * self.echo_gain
        self._echo = line[n:]
        for source in self.sources:
            mic += source(t, n, self.mic_rate)
        mic += self._rng.normal(0.0, self.noise_rms, n).astype(np.float32)
        if self._mic_t is None:
            self._mic_t = t
        self._mic = np.concatenate([self._mic, mic])
        while self._mic.size >= self.block:
            chunk = (np.clip(self._mic[: self.block], -1.0, 1.0) * 32767).astype(np.int16)
            self._mic = self._mic[self.block :]
            block_t = self._mic_t
            self._mic_t += self.block / self.mic_rate
            if self.keep_log:
                self.mic_log.append((block_t, chunk))
            if self.pipeline is not None:
                self.pipeline.process(chunk, block_t)
