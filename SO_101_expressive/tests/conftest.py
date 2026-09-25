from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    os.environ.setdefault("MUJOCO_GL", "osmesa")

import numpy as np
import pytest

from so101_expressive.config import Settings
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.runtime import create_body


# ustawienia testowe odcinają lokalny plik env, żeby wynik testów nie zależał od klucza użytkownika
@pytest.fixture
def settings(tmp_path):
    return Settings.from_env({"LEDGER_PATH": str(tmp_path / "ledger.json"), "LOG_DIR": str(tmp_path / "logs")})


# wirtualny głośnik pobiera próbki tak jak callback karty dźwiękowej, ale według zegara testu
class VirtualSpeaker:
    # stałe opóźnienie wyjścia odwzorowuje bufor sprzętowy głośnika
    def __init__(self, buffer: PlaybackBuffer, latency: float = 0.02) -> None:
        self.buffer = buffer
        self.latency = latency
        self._frac = 0.0

    # każdy krok pętli pobiera tyle próbek, ile trwa krok, z czasem wyjścia przesuniętym o opóźnienie
    def tick(self, t: float, dt: float) -> np.ndarray:
        exact = dt * self.buffer.rate + self._frac
        frames = int(exact)
        self._frac = exact - frames
        return self.buffer.pull(frames, t + self.latency)


# ciało robota z wirtualnym głośnikiem jest wspólnym punktem startu testów fizyki i scenariuszy
@pytest.fixture
def body(settings):
    playback = PlaybackBuffer()
    runtime = create_body(settings, playback)
    runtime.speaker = VirtualSpeaker(playback)
    return runtime


# pomocnik przesuwa czas testu krok po kroku i zbiera zapisy kroków do asercji
def run_for(runtime, t0: float, duration: float, on_step=None) -> tuple[float, list]:
    records = []
    t = t0
    steps = int(round(duration / runtime.dt))
    for _ in range(steps):
        if on_step is not None:
            on_step(t)
        runtime.speaker.tick(t, runtime.dt)
        records.append(runtime.step(t))
        t += runtime.dt
    return t, records


# syntetyczna mowa z sylabami i przerwami ma realną obwiednię amplitudy do testów szczęki
def synthetic_speech(seconds: float, rate: int = 24000, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * rate)) / rate
    f0 = 140 + 30 * np.sin(2 * np.pi * 0.7 * t)
    phase = 2 * np.pi * np.cumsum(f0) / rate
    voiced = sum(np.sin(k * phase) / k for k in range(1, 8))
    syllables = 0.5 * (1 + np.sin(2 * np.pi * 4.0 * t)) ** 2
    gaps = (np.sin(2 * np.pi * 0.45 * t + rng.uniform(0, 3)) > -0.6).astype(float)
    x = 0.25 * voiced * syllables * gaps
    return (np.clip(x, -1, 1) * 32767).astype(np.int16)
