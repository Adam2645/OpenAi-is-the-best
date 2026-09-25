from __future__ import annotations

import re
import sys
import threading
import time
import unicodedata
from collections import deque
from typing import Callable

import numpy as np

from ..behavior.tracking import PersonObservation
from ..state import ApiStatus, PersonStatus
from ..util import LatestValue

QUOTED = re.compile(r"[„“”\"«»][^„“”\"«»]*[„“”\"«»]")
CLAUSE_SPLIT = re.compile(r"[.,;:!?\n]+|\s+-\s+|\s+(?:ale|lecz|jednak|tylko|but|however)\s+")
NEGATOR = re.compile(r"\b(nie|nigdy|przestan\w*|dont|don't|do not|never|not|stop)\b")
LOOK_REQUESTS = tuple(re.compile(pattern) for pattern in (
    r"\b(spojrz|spojrzcie|popatrz|popatrzcie|patrz|patrzcie|zobacz|zobaczcie|obejrzyj|obejrzyjcie|zerknij|zerknijcie)\b",
    r"\brzuc(cie)?\s+okiem\b",
    r"\b(mozesz|moglbys|moglabys|mozecie|potrafisz|sprobuj|chce zebys|chcialbym zebys|chcialabym zebys)\b"
    r"(\s+\w+){0,2}?\s+(spojrzec|popatrzec|zobaczyc|obejrzec|zerknac|patrzec)\b",
    r"\b(co|czy|kogo|ile)\b(\s+\w+){0,2}?\s+(widzisz|widac)\b",
    r"\bwidzisz\s+(mnie|to|tu|tutaj|go|ja|je|te|ten|ta|cos|kogos)\b",
    r"\b(jak|czy)\b(\s+\w+){0,2}?\s+wygladam\b",
    r"\bco\s+(teraz\s+)?(trzymam|mam\s+w\s+(rece|rekach|dloni))\b",
    r"\b(pokaze|pokazuje)\s+(ci|tobie|wam)\b",
    r"\b(uzyj|wlacz|sprawdz)\s+(swojej\s+|swoja\s+)?kamer\w*",
    r"^(please\s+|now\s+|just\s+|hey\s+)?look\b",
    r"\b(can|could|would|will)\s+you\s+(please\s+)?(take\s+a\s+look|have\s+a\s+look|look)\b",
    r"^(please\s+)?(take|have)\s+a\s+look\b",
    r"\b(what|who)\s+(do|can)\s+you\s+see\b",
    r"\b(can|could|do)\s+you\s+see\b",
    r"\bhow\s+do\s+i\s+look\b",
    r"\bwhat\s+am\s+i\s+holding\b",
    r"\b(let\s+me|i'll|i\s+will|i\s+want\s+to)\s+show\s+you\b",
    r"\buse\s+(the|your)\s+camera\b",
))
LOOK_DENIALS = tuple(re.compile(pattern) for pattern in (
    r"\bnie\s+(\w+\s+)?(nagrywaj\w*|filmuj\w*|fotografuj\w*|rob\w*\s+zdjec\w*|uzywaj\w*\s+kamer\w*|wysylaj\w*"
    r"|pokazuj\w*|ogladaj\w*|spogladaj\w*|zagladaj\w*|podgladaj\w*|obserwuj\w*)",
    r"\b(wylacz|zaslon|zakryj)\s+(\w+\s+)?kamer\w*",
    r"\bbez\s+kamery\b",
    r"\bprzestan\w*\s+(\w+\s+)?(patrzec|obserwowac|nagrywac|filmowac|podgladac)\b",
    r"\b(stop|quit)\s+(looking|watching|recording|filming)\b",
    r"\b(turn\s+off|cover|disable)\s+(the\s+|your\s+)?camera\b",
    r"\bno\s+camera\b",
))
REVOKE_HEADS = frozenset({"nie", "niewazne", "stop", "cancel", "nevermind", "never"})
REVOKE_WORDS = REVOKE_HEADS | frozenset({"a", "zreszta", "wlasciwie", "juz", "trzeba", "potrzeba", "actually", "mind", "oh", "please"})


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
    def send_now(self, backend, frame: np.ndarray | None, t: float, allow: Callable[[], bool] | None = None) -> bool:
        if frame is None or backend is None or backend.status is not ApiStatus.CONNECTED:
            return False
        import cv2

        h, w = frame.shape[:2]
        small = cv2.resize(frame, (self.width, int(h * self.width / w)))
        ok, jpeg = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ok:
            return False
        with self._lock:
            backend.send_image(jpeg.tobytes(), allow=allow)
            self._last = t
            self.sent += 1
        return True

    # wysyłka cykliczna działa tylko po jawnym ustawieniu odstępu i przy widocznym rozmówcy
    def maybe_send(self, backend, frame: np.ndarray | None, t: float, person: PersonStatus) -> bool:
        if self.interval_s <= 0 or person is not PersonStatus.TRACKED or t - self._last < self.interval_s:
            return False
        return self.send_now(backend, frame, t)


# rozpoznany tekst porównujemy bez wielkich liter i polskich znaków, bo zapis transkrypcji mowy bywa niejednolity
def _normalize(text: str) -> str:
    text = text.lower().replace("ł", "l").replace("’", "'").replace("‘", "'")
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))


# przeczenie działa w obrębie zdania składowego, a cytat nie jest prośbą mówiącego, więc tekst dzielimy i usuwamy cytaty
def _clauses(text: str) -> list[str]:
    normalized = _normalize(QUOTED.sub(" . ", text))
    return [part.strip() for part in CLAUSE_SPLIT.split(normalized) if part.strip()]


# kolejne wzmianki o patrzeniu są prośbami albo zakazami, a przeczenie przed końcem prośby zamienia ją w zakaz
def _look_events(clauses: list[str]) -> list[str]:
    events: list[str] = []
    for clause in clauses:
        found: list[tuple[int, str]] = []
        for pattern in LOOK_REQUESTS:
            for match in pattern.finditer(clause):
                negated = NEGATOR.search(clause, 0, match.end()) is not None
                found.append((match.start(), "deny" if negated else "ask"))
        for pattern in LOOK_DENIALS:
            found.extend((match.start(), "deny") for match in pattern.finditer(clause))
        events.extend(kind for _, kind in sorted(found))
    return events


# samo „nie” albo „a zresztą nie” na końcu wypowiedzi odwołuje wcześniejszą prośbę
def _revoked(clauses: list[str]) -> bool:
    words = set(clauses[-1].split()) if clauses else set()
    return bool(words) and words <= REVOKE_WORDS and bool(words & REVOKE_HEADS)


# zgodą jest tylko twierdząca prośba w trybie rozkazującym lub pytającym, która jest ostatnią wzmianką o patrzeniu
def asks_to_look(text: str) -> bool:
    clauses = _clauses(text)
    events = _look_events(clauses)
    return bool(events) and events[-1] == "ask" and not _revoked(clauses)


# zgoda na klatkę pochodzi z rozpoznanych wypowiedzi rozmówcy, jest jednorazowa i do chwili wysłania można ją odwołać
class CameraConsent:
    # okno świeżości wypowiedzi i krótki termin oczekiwania ograniczają, jak długo prośba modelu może czekać na zgodę
    def __init__(self, window_s: float, grace_s: float = 3.0) -> None:
        self.window_s = window_s
        self.grace_s = grace_s
        self._lock = threading.Lock()
        self._heard: list[list] = []
        self._consumed_t = -1e9
        self._pending: tuple[str, float, object] | None = None
        self._in_flight: str | None = None
        self._revoked: deque[str] = deque(maxlen=32)

    # fragment rozpoznanej wypowiedzi rozmówcy trafia do bufora zgody, a czas nadaje mu dopiero pętla panelu
    def hear(self, text: str) -> None:
        with self._lock:
            self._heard.append([text, None])

    # granica wypowiedzi z lokalnego vad oddziela zdania, żeby przeczenie z nowej wypowiedzi nie skleiło się z poprzednią
    def boundary(self) -> None:
        with self._lock:
            if self._heard and self._heard[-1][0] != ". ":
                self._heard.append([". ", None])

    # czas nadawany przy pierwszym odczycie mierzy świeżość zgody zegarem pętli panelu, także w symulacji
    def stamp(self, now: float) -> None:
        with self._lock:
            for entry in self._heard:
                if entry[1] is None:
                    entry[1] = now
            self._heard = [entry for entry in self._heard if now - entry[1] <= self.window_s]

    # ocena świeżych wypowiedzi zwraca zgodę albo powód, dla którego klatka nie może zostać wysłana
    def check(self, now: float) -> tuple[bool, str]:
        with self._lock:
            text = "".join(entry[0] for entry in self._heard if entry[1] is not None and now - entry[1] <= self.window_s)
            recently_used = now - self._consumed_t <= self.window_s
        if not text.strip(" ."):
            if recently_used:
                return False, "do tej prośby wysłałem już jedną klatkę - poproś ponownie, jeśli mam spojrzeć jeszcze raz"
            return False, "nie usłyszałem prośby o spojrzenie - powiedz np. „co widzisz?” albo „spójrz”"
        if not asks_to_look(text):
            return False, "obraz wysyłam tylko, gdy rozmówca wprost o to poprosi, np. „co widzisz?” albo „spójrz”"
        return True, ""

    # wysłanie klatki zużywa usłyszaną prośbę, więc kolejna klatka wymaga nowej wypowiedzi rozmówcy
    def consume(self, now: float) -> None:
        with self._lock:
            self._heard.clear()
            self._consumed_t = now

    # oczekiwać może tylko jedna prośba naraz, z terminem liczonym od jej nadejścia
    def begin(self, call_id: str, t: float, payload: object = None) -> bool:
        with self._lock:
            if self._pending is not None:
                return False
            self._pending = (call_id, t + self.grace_s, payload)
            return True

    # bieżąca oczekująca prośba z terminem i danymi wywołania albo brak
    @property
    def pending(self) -> tuple[str, float, object] | None:
        with self._lock:
            return self._pending

    # przejęcie prośby zapobiega dwóm decyzjom dla jednego wywołania, które do chwili wysłania pozostaje odwoływalne
    def finish(self, call_id: str) -> bool:
        with self._lock:
            if self._pending is None or self._pending[0] != call_id:
                return False
            self._pending = None
            self._in_flight = call_id
            return True

    # odmowa lub nieudane przygotowanie klatki kończy wywołanie bez ujawnienia obrazu
    def release(self, call_id: str) -> None:
        with self._lock:
            if self._in_flight == call_id:
                self._in_flight = None

    # sprawdzenie tuż przed wysłaniem klatki jest punktem ujawnienia, po którym anulowanie niczego już nie cofa
    def disclose(self, call_id: str) -> bool:
        with self._lock:
            if call_id in self._revoked:
                return False
            if self._in_flight == call_id:
                self._in_flight = None
            return True

    # odpowiedź funkcji dla anulowanego wywołania nie jest wysyłana, bo serwer już je odrzucił
    def allows(self, call_id: str) -> bool:
        with self._lock:
            return call_id not in self._revoked

    # anulowanie przez serwer lub rozłączenie usuwa oczekującą prośbę i odwołuje klatkę, która jeszcze nie wyszła
    def cancel(self, ids: tuple[str, ...] | None = None) -> bool:
        with self._lock:
            hit = False
            if self._pending is not None and (ids is None or self._pending[0] in ids):
                self._pending = None
                hit = True
            if self._in_flight is not None and (ids is None or self._in_flight in ids):
                self._revoked.append(self._in_flight)
                self._in_flight = None
                hit = True
            return hit
