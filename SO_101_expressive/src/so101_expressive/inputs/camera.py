from __future__ import annotations

import sys
import threading
import time

import numpy as np

from ..behavior.tracking import PersonObservation
from ..state import ApiStatus, PersonStatus
from ..util import LatestValue


# brak kamery lub uprawnień ma dać zrozumiały komunikat zamiast cichego braku obrazu
class CameraUnavailable(RuntimeError):
    pass


# kamera laptopa czytana w osobnym wątku udostępnia zawsze najnowszą klatkę bez kolejki opóźnień
class CameraSource:
    # na macos używamy avfoundation, a brak obrazu zwykle oznacza brak zgody na kamerę dla terminala
    def __init__(self, index: int = 0, width: int = 640, height: int = 480) -> None:
        import cv2

        backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(index, backend)
        if not self.cap.isOpened():
            raise CameraUnavailable(
                "nie można otworzyć kamery - na macos nadaj uprawnienie Kamera dla aplikacji terminala "
                "(Ustawienia systemowe > Prywatność i ochrona > Kamera)"
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._latest: LatestValue[tuple[np.ndarray, float]] = LatestValue()
        self._stop = threading.Event()
        self.failures = 0
        self._thread = threading.Thread(target=self._loop, name="camera", daemon=True)

    # pętla odczytu liczy błędy, aby interfejs mógł pokazać zanik obrazu
    def _loop(self) -> None:
        while not self._stop.is_set():
            ok, frame = self.cap.read()
            if ok and frame is not None:
                self._latest.set((frame, time.monotonic()))
            else:
                self.failures += 1
                time.sleep(0.05)

    # najnowsza klatka ze znacznikiem czasu albo brak, gdy kamera jeszcze nic nie dała
    def latest(self) -> tuple[np.ndarray, float] | None:
        return self._latest.get()

    # start wątku odczytu po poprawnym otwarciu urządzenia
    def start(self) -> None:
        self._thread.start()

    # zwolnienie urządzenia pozwala innym aplikacjom użyć kamery po zamknięciu programu
    def close(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)
        self.cap.release()


# sztuczny podgląd kamery w trybie bez urządzeń rysuje twarz tam, gdzie jest skryptowany rozmówca
def synthetic_frame(obs: PersonObservation | None, width: int = 640, height: int = 480) -> np.ndarray:
    import cv2

    frame = np.full((height, width, 3), 48, dtype=np.uint8)
    cv2.putText(frame, "KAMERA WIRTUALNA", (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (160, 160, 160), 2)
    if obs is not None and obs.status in (PersonStatus.TRACKED, PersonStatus.UNCERTAIN, PersonStatus.ACQUIRING):
        cx = int((obs.u + 1.0) / 2.0 * width)
        cy = int((obs.v + 1.0) / 2.0 * height)
        r = max(12, int(obs.size * width / 2))
        cv2.circle(frame, (cx, cy + int(2.4 * r)), int(1.6 * r), (90, 90, 120), -1)
        cv2.circle(frame, (cx, cy), r, (170, 190, 220), -1)
    return frame


# klatki dla chmury są oddzielone od szybkiej pętli śledzenia i wysyłane od razu albo wcale, bez oczekujących żądań
class VisionUplink:
    # zero wyłącza wysyłanie cykliczne, bo przesyłanie kadrów do chmury w tle wymaga świadomego włączenia
    def __init__(self, interval_s: float, width: int = 512) -> None:
        self.interval_s = interval_s
        self.width = width
        self._last = -1e9
        self._lock = threading.Lock()
        self.sent = 0

    # natychmiastowe wysłanie jednej klatki nie zostawia żądania, które mógłby później spełnić inny kadr
    def send_now(self, backend, frame: np.ndarray | None, t: float) -> bool:
        if frame is None or backend is None or backend.status is not ApiStatus.CONNECTED:
            return False
        import cv2

        h, w = frame.shape[:2]
        small = cv2.resize(frame, (self.width, int(h * self.width / w)))
        ok, jpeg = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ok:
            return False
        with self._lock:
            backend.send_image(jpeg.tobytes())
            self._last = t
            self.sent += 1
        return True

    # wysyłka cykliczna działa tylko po jawnym ustawieniu odstępu i przy widocznym rozmówcy
    def maybe_send(self, backend, frame: np.ndarray | None, t: float, person: PersonStatus) -> bool:
        if self.interval_s <= 0 or person is not PersonStatus.TRACKED or t - self._last < self.interval_s:
            return False
        return self.send_now(backend, frame, t)
