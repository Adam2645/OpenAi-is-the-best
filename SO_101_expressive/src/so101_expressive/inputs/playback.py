from __future__ import annotations

import bisect
import threading
import time
from collections import deque

import numpy as np

SILENCE_RMS = 10 ** (-50 / 20)


# bufor mierzy obwiednię dokładnie tych próbek, które wychodzą z głośnika, razem z czasem ich wyjścia
class PlaybackBuffer:
    # historia obwiedni służy zarówno szczęce, jak i bramce echa mikrofonu
    def __init__(self, rate: int = 24000, block_ms: float = 10.0, tail_s: float = 0.15, history_s: float = 4.0) -> None:
        self.rate = rate
        self.sub = max(1, int(rate * block_ms / 1000.0))
        self.tail_s = tail_s
        self._queue: deque[np.ndarray] = deque()
        self._queued = 0
        self._lock = threading.Lock()
        self._env_t: deque[float] = deque(maxlen=int(history_s * 1000.0 / block_ms))
        self._env_v: deque[float] = deque(maxlen=int(history_s * 1000.0 / block_ms))
        self._muted = False
        self._fade = False
        self._last_audio_t = -1e9
        self._dac_end: float | None = None
        self.played_seconds = 0.0
        self.dropped_seconds = 0.0

    # próbki z sieci dopisujemy na koniec kolejki bez kopiowania całego bufora
    def enqueue(self, pcm16: bytes | np.ndarray) -> None:
        data = np.frombuffer(pcm16, dtype="<i2") if isinstance(pcm16, (bytes, bytearray)) else np.asarray(pcm16, dtype=np.int16)
        if data.size == 0:
            return
        with self._lock:
            self._queue.append(data.copy())
            self._queued += data.size

    # przerwanie wyrzuca zaległe próbki i wygasza dźwięk w ciągu kilku milisekund, bez trzasku
    def flush(self) -> None:
        with self._lock:
            self.dropped_seconds += self._queued / self.rate
            self._fade = self._queued > 0
            fade_src = self._take(min(self._queued, int(0.012 * self.rate))) if self._fade else None
            self._queue.clear()
            self._queued = 0
            if fade_src is not None and fade_src.size:
                ramp = np.linspace(1.0, 0.0, fade_src.size)
                self._queue.append((fade_src * ramp).astype(np.int16))
                self._queued = fade_src.size

    # wyciszenie zużywa próbki w normalnym tempie, więc tura kończy się naturalnie, ale głośnik milczy
    def set_muted(self, muted: bool) -> None:
        with self._lock:
            self._muted = bool(muted)

    # stan wyciszenia jest pokazywany w interfejsie i w testach opcji milczenia
    @property
    def muted(self) -> bool:
        return self._muted

    # pobranie zadanej liczby próbek z kolejki, wywoływane pod blokadą
    def _take(self, frames: int) -> np.ndarray:
        out = np.zeros(frames, dtype=np.int16)
        filled = 0
        while filled < frames and self._queue:
            chunk = self._queue[0]
            n = min(frames - filled, chunk.size)
            out[filled : filled + n] = chunk[:n]
            filled += n
            if n == chunk.size:
                self._queue.popleft()
            else:
                self._queue[0] = chunk[n:]
            self._queued -= n
        return out

    # wywołanie z callbacku karty dźwiękowej podaje czas, w którym pierwsza próbka opuści przetwornik
    def pull(self, frames: int, dac_time: float) -> np.ndarray:
        with self._lock:
            out = self._take(frames)
            if self._muted:
                out = np.zeros(frames, dtype=np.int16)
            x = out.astype(np.float32) / 32768.0
            for k in range(0, frames, self.sub):
                seg = x[k : k + self.sub]
                rms = float(np.sqrt(np.mean(seg * seg))) if seg.size else 0.0
                self._env_t.append(dac_time + k / self.rate)
                self._env_v.append(rms)
                if rms > SILENCE_RMS:
                    self._last_audio_t = dac_time + (k + seg.size) / self.rate
                    self.played_seconds += seg.size / self.rate
            self._dac_end = dac_time + frames / self.rate
            if not self._queue:
                self._fade = False
        return out

    # poziom w chwili t pochodzi z historii wyjścia albo z próbek, które dopiero wyjdą z bufora
    def level_at(self, t: float) -> float:
        with self._lock:
            if self._dac_end is not None and t >= self._dac_end:
                if self._muted or not self._queue:
                    return 0.0
                offset = int((t - self._dac_end) * self.rate)
                return self._queued_rms(offset, self.sub)
            if not self._env_t or t < self._env_t[0]:
                return 0.0
            times = list(self._env_t)
            idx = bisect.bisect_right(times, t) - 1
            return float(self._env_v[idx]) if idx >= 0 else 0.0

    # szczęka z wyprzedzeniem patrzy w próbki zaplanowane do odtworzenia, nie w tekst odpowiedzi
    def _queued_rms(self, offset: int, width: int) -> float:
        pos = 0
        parts = []
        need_start, need_end = offset, offset + width
        for chunk in self._queue:
            end = pos + chunk.size
            if end > need_start and pos < need_end:
                a = max(need_start - pos, 0)
                b = min(need_end - pos, chunk.size)
                parts.append(chunk[a:b])
            if end >= need_end:
                break
            pos = end
        if not parts:
            return 0.0
        seg = np.concatenate(parts).astype(np.float32) / 32768.0
        return float(np.sqrt(np.mean(seg * seg)))

    # najwyższy poziom w oknie czasu jest odniesieniem dla bramki echa w mikrofonie
    def peak_level(self, t_from: float, t_to: float) -> float:
        with self._lock:
            best = 0.0
            for tt, vv in zip(self._env_t, self._env_v):
                if t_from <= tt <= t_to and vv > best:
                    best = vv
            return best

    # odtwarzanie trwa, gdy w kolejce są próbki albo przed chwilą wyszedł niecichy dźwięk
    def is_playing(self, t: float) -> bool:
        with self._lock:
            return (self._queued > 0 and not self._muted) or (t - self._last_audio_t) < self.tail_s

    # zaległe próbki oznaczają, że wypowiedź jeszcze trwa, nawet gdy jest wyciszona
    def has_pending(self) -> bool:
        with self._lock:
            return self._queued > 0


# wyjście przez sounddevice przelicza czas przetwornika na zegar monotoniczny pętli ruchu
class SpeakerOutput:
    # strumień ma mały blok, by opóźnienie między dźwiękiem a szczęką było krótkie
    def __init__(self, buffer: PlaybackBuffer, device: int | str | None = None, blocksize: int = 480) -> None:
        import sounddevice as sd

        self.buffer = buffer
        self.stream = sd.OutputStream(
            samplerate=buffer.rate, channels=1, dtype="int16", blocksize=blocksize,
            device=device, latency="low", callback=self._callback,
        )

    # callback nie może blokować, więc robi tylko pobranie próbek i przeliczenie czasu
    def _callback(self, outdata, frames, time_info, status) -> None:
        now = time.monotonic()
        try:
            ahead = float(time_info.outputBufferDacTime - time_info.currentTime)
            if not 0.0 <= ahead < 1.0:
                ahead = float(self.stream.latency)
        except (AttributeError, TypeError):
            ahead = float(self.stream.latency)
        outdata[:, 0] = self.buffer.pull(frames, now + ahead)

    # uruchomienie strumienia rozpoczyna ciągłe pobieranie próbek z bufora
    def start(self) -> None:
        self.stream.start()

    # zamknięcie zatrzymuje kartę dźwiękową przed końcem programu
    def close(self) -> None:
        self.stream.stop()
        self.stream.close()
