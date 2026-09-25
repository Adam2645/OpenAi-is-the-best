from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..behavior.tracking import PersonObservation
from ..state import PersonStatus
from ..util import LatestValue


# wykryta twarz w znormalizowanych współrzędnych obrazu, niezależnych od rozdzielczości kamery
@dataclass(frozen=True)
class Face:
    x: float
    y: float
    w: float
    h: float
    score: float

    # środek twarzy jest punktem, na który robot kieruje chwytak
    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.w / 2.0, self.y + self.h / 2.0


# detektor yunet z opencv działa lokalnie w milisekundach, więc szybka pętla śledzenia nie zależy od chmury
class FaceDetector:
    # obraz jest zmniejszany do stałej szerokości, co stabilizuje czas detekcji
    def __init__(self, model_path: Path, input_width: int = 320, score_threshold: float = 0.5) -> None:
        import cv2

        if not Path(model_path).exists():
            raise FileNotFoundError(f"brak modelu detektora twarzy: {model_path}")
        self._cv2 = cv2
        self.input_width = input_width
        self.det = cv2.FaceDetectorYN.create(str(model_path), "", (input_width, input_width * 3 // 4), score_threshold, 0.3, 20)
        self._size: tuple[int, int] | None = None

    # wynik jest listą twarzy z pewnością detekcji, pusta gdy obraz nie zawiera twarzy
    def detect(self, frame_bgr: np.ndarray) -> list[Face]:
        h, w = frame_bgr.shape[:2]
        sw = self.input_width
        sh = max(1, int(round(h * sw / w)))
        small = self._cv2.resize(frame_bgr, (sw, sh))
        if self._size != (sw, sh):
            self.det.setInputSize((sw, sh))
            self._size = (sw, sh)
        _, faces = self.det.detect(small)
        if faces is None:
            return []
        return [Face(float(f[0]) / sw, float(f[1]) / sh, float(f[2]) / sw, float(f[3]) / sh, float(f[-1])) for f in faces]


# logika czasowa śledzenia wymaga kilku pewnych klatek, zanim ruszy ramieniem, i zamraża ruch przy niepewności
class FaceTracker:
    # progi pewności i czasy utraty są konfigurowalne, bo zależą od oświetlenia i kamery
    def __init__(
        self,
        acquire_score: float = 0.80,
        keep_score: float = 0.60,
        acquire_frames: int = 3,
        uncertain_after_s: float = 0.35,
        absent_after_s: float = 1.5,
        max_jump: float = 0.35,
    ) -> None:
        self.acquire_score = acquire_score
        self.keep_score = keep_score
        self.acquire_frames = acquire_frames
        self.uncertain_after_s = uncertain_after_s
        self.absent_after_s = absent_after_s
        self.max_jump = max_jump
        self.status = PersonStatus.ABSENT
        self._run = 0
        self._last_good_t = -1e9
        self._last: Face | None = None

    # kandydatem jest twarz najbliższa poprzedniej, a przy pierwszej detekcji największa
    def _choose(self, faces: list[Face]) -> Face | None:
        if not faces:
            return None
        if self._last is None:
            return max(faces, key=lambda f: f.w * f.h)
        lx, ly = self._last.center
        return min(faces, key=lambda f: math.hypot(f.center[0] - lx, f.center[1] - ly))

    # aktualizacja zwraca obserwację, która pozwala na ruch tylko przy pewnej i ciągłej detekcji
    def update(self, faces: list[Face], t: float) -> PersonObservation:
        cand = self._choose(faces)
        engaged = self.status in (PersonStatus.TRACKED, PersonStatus.UNCERTAIN)
        threshold = self.keep_score if engaged else self.acquire_score
        good = cand is not None and cand.score >= threshold
        if good and engaged and self._last is not None:
            jump = math.hypot(cand.center[0] - self._last.center[0], cand.center[1] - self._last.center[1])
            if jump > self.max_jump:
                good = False
                self.status = PersonStatus.ACQUIRING
                self._run = 0
                self._last = cand
        if good:
            self._run += 1
            self._last_good_t = t
            self._last = cand
            if self.status in (PersonStatus.ABSENT, PersonStatus.ACQUIRING):
                self.status = PersonStatus.TRACKED if self._run >= self.acquire_frames else PersonStatus.ACQUIRING
            else:
                self.status = PersonStatus.TRACKED
        else:
            self._run = 0
            since = t - self._last_good_t
            if self.status in (PersonStatus.TRACKED, PersonStatus.UNCERTAIN):
                if since >= self.absent_after_s:
                    self.status = PersonStatus.ABSENT
                    self._last = None
                elif since >= self.uncertain_after_s:
                    self.status = PersonStatus.UNCERTAIN
            elif self.status is PersonStatus.ACQUIRING and since >= self.uncertain_after_s:
                self.status = PersonStatus.ABSENT
                self._last = None
        ref = self._last
        if ref is None:
            return PersonObservation(self.status, t)
        cx, cy = ref.center
        conf = cand.score if cand is not None else 0.0
        return PersonObservation(self.status, t, 2.0 * cx - 1.0, 2.0 * cy - 1.0, ref.w, conf)


# pętla wizji działa w osobnym wątku, żeby detekcja nie spowalniała sterowania ani interfejsu
class VisionLoop:
    # częstotliwość detekcji jest ograniczona, bo śledzenie nie potrzebuje więcej niż kilkanaście klatek na sekundę
    def __init__(self, camera, detector: FaceDetector, tracker: FaceTracker, out: LatestValue, hz: float = 15.0) -> None:
        self.camera = camera
        self.detector = detector
        self.tracker = tracker
        self.out = out
        self.period = 1.0 / hz
        self.faces: list[Face] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="vision", daemon=True)
        self.errors = 0

    # każda iteracja bierze najnowszą klatkę, a stare klatki są pomijane
    def _loop(self) -> None:
        last_frame_t = None
        while not self._stop.is_set():
            started = time.monotonic()
            item = self.camera.latest()
            if item is not None and item[1] != last_frame_t:
                frame, frame_t = item
                last_frame_t = frame_t
                try:
                    self.faces = self.detector.detect(frame)
                except Exception:
                    self.errors += 1
                    self.faces = []
                self.out.set(self.tracker.update(self.faces, frame_t))
            time.sleep(max(0.0, self.period - (time.monotonic() - started)))

    # start uruchamia wątek wizji po otwarciu kamery
    def start(self) -> None:
        self._thread.start()

    # zatrzymanie kończy wątek przy zamykaniu aplikacji
    def close(self) -> None:
        self._stop.set()


# skryptowany rozmówca zastępuje kamerę w trybie bez urządzeń i w testach scenariuszy
class ScriptedPerson:
    # oś czasu składa się z odcinków obecności, niepewności i nieobecności z pozycją twarzy
    def __init__(self, segments: list[tuple[float, float, PersonStatus, float, float, float, float]]) -> None:
        self.segments = segments

    # obserwacja w chwili t wynika z aktywnego odcinka, poza nimi osoby nie ma
    def observe(self, t: float) -> PersonObservation:
        for t0, t1, status, u, v, size, conf in self.segments:
            if t0 <= t < t1:
                if callable(u):
                    u = u(t)
                return PersonObservation(status, t, float(u), float(v), size, conf)
        return PersonObservation(PersonStatus.ABSENT, t)
