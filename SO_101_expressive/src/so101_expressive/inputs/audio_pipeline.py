from __future__ import annotations

import queue
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable

import numpy as np

from ..config import Settings
from ..conversation.base import ConversationBackend
from ..state import ApiStatus
from ..util import LatestValue
from .echo import SILENT_REF, EchoGate
from .music import MusicDetector
from .playback import PlaybackBuffer
from .vad import EnergyVad


# statystyki bloku mikrofonu są pokazywane w interfejsie i używane w testach bramkowania
@dataclass(frozen=True)
class PipelineStats:
    mic_rms: float = 0.0
    floor: float = 0.0
    gate_open: bool = True
    own_audio: bool = False
    streaming: bool = False
    music_score: float = 0.0


# potok mikrofonu łączy vad, bramkę echa i detektor muzyki oraz decyduje, co trafia do chmury
class AudioPipeline:
    # przetwarzanie jest synchroniczne, więc ten sam kod działa w wątku aplikacji i w testach
    def __init__(
        self,
        settings: Settings,
        playback: PlaybackBuffer,
        status_out: LatestValue,
        backend: ConversationBackend | None = None,
        rate: int = 16000,
    ) -> None:
        from ..runtime import AudioStatus

        self._status_cls = AudioStatus
        self.rate = rate
        self.playback = playback
        self.status_out = status_out
        self.backend = backend
        self.mode = settings.mic_stream_mode
        self.vad = EnergyVad(rate, hangover_ms=max(800.0, float(settings.vad_silence_ms) + 200.0))
        self.gate = EchoGate(settings.echo_mode, settings.barge_in_ratio, settings.barge_in_min_ms)
        self.music = MusicDetector(rate)
        self._ring: deque[np.ndarray] = deque()
        self._ring_len = 0
        self._ring_max = int(rate * settings.vad_prefix_ms / 1000.0)
        self._streaming = False
        self.sent_seconds = 0.0
        self.barge_ins = 0
        self.last_vad_speech_t = -1e9
        self.on_barge_in: Callable[[float], None] | None = None
        self.stats = PipelineStats()

    # bufor ostatnich bloków pozwala wysłać początek wypowiedzi sprzed decyzji vad lub bramki
    def _remember(self, block: np.ndarray) -> None:
        self._ring.append(block)
        self._ring_len += block.size
        while self._ring and self._ring_len - self._ring[0].size >= self._ring_max:
            self._ring_len -= self._ring.popleft().size

    # backend jest gotowy na audio tylko przy aktywnym połączeniu lub lokalnym skrypcie
    def _backend_ready(self) -> bool:
        return self.backend is not None and self.backend.status in (ApiStatus.CONNECTED, ApiStatus.LOCAL)

    # jeden blok z mikrofonu przechodzi przez vad, bramkę echa i detektor muzyki
    def process(self, block: np.ndarray, t: float) -> None:
        dt = block.size / self.rate
        self._remember(block)
        x = block.astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(x * x))) if x.size else 0.0
        ref = self.playback.peak_level(t - 0.35, t + 0.05)
        own = (self.playback.has_pending() and not self.playback.muted) or self.playback.is_playing(t) or ref > SILENT_REF
        gate = self.gate.process(rms, ref, dt, self.vad.floor, robot_active=own)
        if gate.barge_in:
            self.barge_ins += 1
            if self.on_barge_in is not None:
                self.on_barge_in(t)
        vad = self.vad.process(block) if gate.pass_audio else self.vad.suspend(rms)
        ms = self.music.update(block, own_playback=own)
        user_speaking = vad.speech and gate.pass_audio
        if user_speaking:
            self.last_vad_speech_t = t
        want = gate.pass_audio and (self.mode == "continuous" or vad.speech)
        if want and self._backend_ready():
            data = np.concatenate(list(self._ring)) if not self._streaming else block
            self.backend.send_audio(data.astype("<i2").tobytes(), self.rate)
            self.sent_seconds += data.size / self.rate
            self._streaming = True
        elif self._streaming:
            self._streaming = False
            if self.backend is not None:
                self.backend.end_audio()
        if vad.started and self.backend is not None and self.backend.status is ApiStatus.IDLE:
            self.backend.wake()
        self.stats = PipelineStats(vad.rms, vad.floor, gate.pass_audio, own, self._streaming, ms.score)
        self.status_out.set(self._status_cls(user_speaking, ms.music, ms.score, ms.bpm))


# wejście mikrofonu przez sounddevice oddaje bloki do kolejki, bo callback karty nie może liczyć cech
class MicInput:
    # blok 32 ms przy 16 khz jest kompromisem między opóźnieniem a kosztem obliczeń
    def __init__(self, pipeline: AudioPipeline, device: int | str | None = None, blocksize: int = 512) -> None:
        import sounddevice as sd

        self.pipeline = pipeline
        self._queue: queue.Queue = queue.Queue(maxsize=200)
        self._stop = threading.Event()
        self.overflows = 0
        self.stream = sd.InputStream(
            samplerate=pipeline.rate, channels=1, dtype="int16", blocksize=blocksize,
            device=device, callback=self._callback,
        )
        self._thread = threading.Thread(target=self._worker, name="audio-pipeline", daemon=True)

    # callback tylko kopiuje dane i znacznik czasu przetwornika, reszta dzieje się w wątku roboczym
    def _callback(self, indata, frames, time_info, status) -> None:
        now = time.monotonic()
        try:
            age = float(time_info.currentTime - time_info.inputBufferAdcTime)
            if not 0.0 <= age < 1.0:
                age = 0.0
        except (AttributeError, TypeError):
            age = 0.0
        try:
            self._queue.put_nowait((indata[:, 0].copy(), now - age))
        except queue.Full:
            self.overflows += 1

    # wątek roboczy przetwarza bloki po kolei, żeby cechy muzyki i vad miały ciągłość
    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                block, t = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            self.pipeline.process(block, t)

    # start uruchamia najpierw wątek, potem strumień, żeby nie zgubić pierwszych bloków
    def start(self) -> None:
        self._thread.start()
        self.stream.start()

    # zamknięcie zatrzymuje mikrofon i wątek roboczy
    def close(self) -> None:
        self._stop.set()
        self.stream.stop()
        self.stream.close()
