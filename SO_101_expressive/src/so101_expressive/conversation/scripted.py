from __future__ import annotations

import itertools
import queue
import shutil
import subprocess
import tempfile
import threading
import wave
from pathlib import Path
from typing import Callable

import numpy as np

from ..state import ApiStatus
from .base import AudioChunk, ConversationBackend, EventSink, IntentRequest, TurnComplete, TurnStarted

CANNED_REPLIES = [
    ("Cześć! Jestem Robo. Działam teraz w trybie lokalnym, bez chmury.", "wave"),
    ("Słyszę Cię, ale bez klucza Gemini odpowiadam tylko przygotowanymi zdaniami.", "shrug"),
    ("Mogę za to patrzeć na Ciebie i zatańczyć, gdy włączysz muzykę.", "happy"),
    ("Hmm, daj mi chwilę do namysłu.", "think"),
    ("Tak, zgadzam się z Tobą!", "nod"),
]


# lokalna synteza mowy pozwala pokazać szczękę i gesty bez api: say na macos, espeak-ng na linuksie
class LocalTTS:
    # zosia to polski głos systemowy macos, a częstotliwość 24 khz odpowiada wyjściu gemini live
    def __init__(self, voice: str = "Zosia", rate: int = 24000) -> None:
        self.voice = voice
        self.rate = rate
        self.engine = "say" if shutil.which("say") else ("espeak-ng" if shutil.which("espeak-ng") else "synthetic")

    # plik wav jest czytany i przeliczany do 24 khz mono int16
    def _read_wav(self, path: Path) -> np.ndarray:
        with wave.open(str(path)) as wf:
            sr = wf.getframerate()
            data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="<i2").astype(np.float32)
            if wf.getnchannels() > 1:
                data = data.reshape(-1, wf.getnchannels()).mean(axis=1)
        if sr != self.rate and data.size:
            idx = np.arange(int(data.size * self.rate / sr)) * (sr / self.rate)
            data = np.interp(idx, np.arange(data.size), data)
        return np.clip(data, -32768, 32767).astype(np.int16)

    # synteza zwraca próbki gotowe do bufora odtwarzania, a przy braku silnika tworzy sztuczne sylaby
    def synth(self, text: str) -> np.ndarray:
        if self.engine != "synthetic":
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "tts.wav"
                if self.engine == "say":
                    cmd = ["say", "-v", self.voice, "-o", str(out), f"--data-format=LEI16@{self.rate}", text]
                else:
                    cmd = ["espeak-ng", "-v", "pl", "-s", "160", "-w", str(out), text]
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                if result.returncode == 0 and out.exists():
                    return self._read_wav(out)
        return babble(len(text) * 0.06, self.rate)


# sztuczne sylaby zastępują mowę, gdy w systemie nie ma żadnego syntezatora
def babble(seconds: float, rate: int = 24000, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * rate)) / rate
    f0 = 150 + 25 * np.sin(2 * np.pi * 0.8 * t)
    phase = 2 * np.pi * np.cumsum(f0) / rate
    voiced = sum(np.sin(k * phase) / k for k in range(1, 8))
    syllables = np.clip(np.sin(2 * np.pi * 4.2 * t + rng.uniform(0, 3)), 0, None) ** 1.5
    return (0.25 * voiced * syllables / 1.6 * 32767).astype(np.int16)


# lokalny backend skryptowy pokazuje przepływ rozmowy bez chmury i jest jawnie oznaczony w stanie
class ScriptedBackend(ConversationBackend):
    # odpowiedzi są wybierane cyklicznie po wykryciu końca wypowiedzi użytkownika przez lokalny vad
    def __init__(
        self,
        sink: EventSink,
        tts: LocalTTS | None = None,
        replies: list[tuple[str, str | None]] | None = None,
        min_user_s: float = 0.6,
        threaded: bool = True,
        should_reply: Callable[[], bool] | None = None,
    ) -> None:
        super().__init__(sink)
        self.tts = tts or LocalTTS()
        self.replies = itertools.cycle(replies or CANNED_REPLIES)
        self.min_user_s = min_user_s
        self.threaded = threaded
        self.should_reply = should_reply
        self._user_s = 0.0
        self._n = 0
        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.intent_results: list[tuple[str, str, dict]] = []

    # start ustawia status lokalny, który odróżnia skrypt od prawdziwej rozmowy z modelem
    def start(self) -> None:
        self._set_status(ApiStatus.LOCAL, f"odpowiedzi z listy, synteza: {self.tts.engine}")
        if self.threaded:
            self._thread = threading.Thread(target=self._worker, name="scripted-tts", daemon=True)
            self._thread.start()

    # zatrzymanie kończy wątek syntezy mowy przy zamykaniu aplikacji
    def stop(self) -> None:
        self._stop.set()

    # czas mowy użytkownika sumuje się, aby odpowiadać tylko na dłuższe wypowiedzi
    def send_audio(self, pcm16: bytes, rate: int) -> None:
        self._user_s += len(pcm16) / 2.0 / rate

    # koniec wypowiedzi użytkownika uruchamia kolejną przygotowaną odpowiedź
    def end_audio(self) -> None:
        allowed = self.should_reply is None or self.should_reply()
        if self._user_s >= self.min_user_s and allowed:
            text, gesture = next(self.replies)
            self.say(text, gesture)
        self._user_s = 0.0

    # obraz nie jest analizowany w trybie lokalnym
    def send_image(self, jpeg: bytes) -> None:
        return None

    # kontekst z czujników nie ma odbiorcy w trybie lokalnym
    def send_context(self, text: str) -> None:
        return None

    # wyniki próśb są zapamiętywane, żeby testy mogły sprawdzić decyzje planisty
    def respond_intent(self, call_id: str, name: str, result: dict) -> None:
        self.intent_results.append((call_id, name, result))

    # wypowiedź z opcjonalnym gestem może być wywołana także z osi czasu dema bez urządzeń
    def say(self, text: str, gesture: str | None = None) -> None:
        if self.threaded:
            self._queue.put((text, gesture))
        else:
            self._emit(text, gesture)

    # wątek syntezy nie blokuje potoku mikrofonu podczas generowania mowy
    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                text, gesture = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            self._emit(text, gesture)

    # zdarzenia tury są takie same jak z gemini live, więc reszta systemu nie rozróżnia źródła
    def _emit(self, text: str, gesture: str | None) -> None:
        pcm = self.tts.synth(text)
        self._n += 1
        self.sink(TurnStarted())
        if gesture:
            self.sink(IntentRequest(f"local-{self._n}", "perform_gesture", {"gesture": gesture, "intensity": "normal"}))
        step = int(0.1 * self.tts.rate)
        for i in range(0, pcm.size, step):
            self.sink(AudioChunk(pcm[i : i + step].tobytes(), self.tts.rate))
        self.sink(TurnComplete())
