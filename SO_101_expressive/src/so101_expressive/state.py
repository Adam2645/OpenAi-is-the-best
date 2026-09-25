from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, fields, replace
from enum import Enum


# stan połączenia z chmurą musi być jawny, aby robot działał lokalnie gdy api jest niedostępne
class ApiStatus(str, Enum):
    DISABLED = "wyłączone"
    CONNECTING = "łączenie"
    CONNECTED = "połączono"
    LOCAL = "lokalny skrypt bez chmury"
    RECONNECTING = "ponowne łączenie"
    OFFLINE = "brak sieci"
    ERROR = "błąd api"
    IDLE = "uśpione przy bezczynności"
    BUDGET_EXCEEDED = "budżet wyczerpany"


# faza rozmowy oddziela słuchanie od mówienia, co steruje szczęką, bramką echa i gestami
class ConversationPhase(str, Enum):
    INACTIVE = "nieaktywna"
    LISTENING = "słucha"
    USER_SPEAKING = "użytkownik mówi"
    ROBOT_SPEAKING = "robot mówi"


# status osoby w kadrze rozstrzyga, czy wolno wykonywać ruch śledzenia
class PersonStatus(str, Enum):
    ABSENT = "brak osoby"
    ACQUIRING = "wykrywanie"
    TRACKED = "śledzona"
    UNCERTAIN = "niepewna detekcja"


# faza chwytaka odróżnia wydaną komendę chwytu od fizycznie potwierdzonego trzymania
class GripPhase(str, Enum):
    OPEN = "otwarty"
    CLOSING = "komenda chwytu wydana"
    CONTACT = "kontakt obu szczęk"
    HOLDING = "trzyma - potwierdzone"
    RELEASING = "zwalnianie"
    LOST = "obiekt utracony"


# etapy manipulacji muszą być widoczne w stanie, aby arbiter mógł blokować niższe warstwy
class ManipulationPhase(str, Enum):
    IDLE = "brak zadania"
    APPROACH = "dojazd nad obiekt"
    DESCEND = "opuszczanie"
    CLOSE = "zamykanie chwytaka"
    LIFT = "podnoszenie"
    HOLD = "trzymanie"
    PLACE_APPROACH = "dojazd do odłożenia"
    PLACE_DESCEND = "opuszczanie do odłożenia"
    RELEASE = "otwieranie chwytaka"
    RETREAT = "odjazd"
    FAILED = "niepowodzenie"


# czynności wyliczane ze stanu są pokazywane w interfejsie i raportowane modelowi rozmowy
class Activity(str, Enum):
    LISTENING = "słucha"
    SPEAKING = "mówi"
    PLAYING_AUDIO = "odtwarza audio"
    TRACKING = "śledzi rozmówcę"
    GESTURING = "wykonuje gest"
    DANCING = "tańczy"
    REACHING = "sięga po obiekt"
    HOLDING = "trzyma obiekt"
    STOPPED = "zatrzymany"
    OFFLINE = "bez chmury"


GRIP_COMMANDED_PHASES = (GripPhase.CLOSING, GripPhase.CONTACT, GripPhase.HOLDING)


# dowód chwytu zapisuje źródło pomiaru, żeby nie pomylić fizyki symulacji z pozorowaniem w testach
@dataclass(frozen=True)
class GripEvidence:
    source: str
    fixed_jaw_force_n: float = 0.0
    moving_jaw_force_n: float = 0.0
    blocked: bool = False
    lifted: bool = False
    attached: bool = False
    confidence: float = 0.0

    # obie szczęki muszą naciskać obiekt z realną siłą, zanim uznamy kontakt chwytny
    @property
    def both_jaws(self) -> bool:
        return self.fixed_jaw_force_n > 0.5 and self.moving_jaw_force_n > 0.5

    # brak nacisku obu szczęk oznacza, że chwytak niczego już nie dotyka
    @property
    def released(self) -> bool:
        return self.fixed_jaw_force_n < 0.2 and self.moving_jaw_force_n < 0.2


# pojedynczy obserwowalny stan robota jest źródłem prawdy dla arbitra, interfejsu i modelu
@dataclass
class RobotState:
    t: float = 0.0
    api: ApiStatus = ApiStatus.DISABLED
    api_detail: str = ""
    conversation: ConversationPhase = ConversationPhase.INACTIVE
    audio_playing: bool = False
    audio_level: float = 0.0
    speech_muted: bool = False
    user_speaking: bool = False
    person: PersonStatus = PersonStatus.ABSENT
    person_confidence: float = 0.0
    gaze_target: tuple[float, float, float] | None = None
    music: bool = False
    music_score: float = 0.0
    music_bpm: float = 0.0
    gesture: str | None = None
    dancing: bool = False
    tracking: bool = False
    jaw_active: bool = False
    manipulation: ManipulationPhase = ManipulationPhase.IDLE
    grip: GripPhase = GripPhase.OPEN
    grip_evidence: GripEvidence | None = None
    estop: bool = False
    estop_reason: str = ""
    limit_events: int = 0
    workspace_blocks: int = 0
    budget_session_pln: float = 0.0
    budget_total_pln: float = 0.0
    budget_session_limit_pln: float = 0.0
    budget_total_limit_pln: float = 0.0
    budget_warning: bool = False
    budget_blocked: bool = False
    suppressed: tuple[str, ...] = ()
    last_user_text: str = ""
    last_robot_text: str = ""

    # komenda chwytu jest aktywna od wydania polecenia, zanim fizyka potwierdzi trzymanie
    @property
    def grip_commanded(self) -> bool:
        return self.grip in GRIP_COMMANDED_PHASES

    # trzymanie uznajemy tylko po potwierdzeniu, nie po samym wydaniu komendy
    @property
    def holding_object(self) -> bool:
        return self.grip is GripPhase.HOLDING

    # chwytak jest zablokowany dla szczęki od komendy chwytu aż do potwierdzonego zwolnienia
    @property
    def gripper_locked(self) -> bool:
        return self.grip in GRIP_COMMANDED_PHASES or self.grip is GripPhase.RELEASING or (
            self.manipulation not in (ManipulationPhase.IDLE, ManipulationPhase.FAILED)
        )

    # lista czynności pozwala jednoznacznie powiedzieć, co robot robi w danej chwili
    def activities(self) -> tuple[Activity, ...]:
        out: list[Activity] = []
        if self.estop:
            out.append(Activity.STOPPED)
        if self.api in (ApiStatus.OFFLINE, ApiStatus.ERROR, ApiStatus.BUDGET_EXCEEDED):
            out.append(Activity.OFFLINE)
        if self.conversation in (ConversationPhase.LISTENING, ConversationPhase.USER_SPEAKING):
            out.append(Activity.LISTENING)
        if self.conversation is ConversationPhase.ROBOT_SPEAKING:
            out.append(Activity.SPEAKING)
        if self.audio_playing:
            out.append(Activity.PLAYING_AUDIO)
        if self.tracking:
            out.append(Activity.TRACKING)
        if self.gesture:
            out.append(Activity.GESTURING)
        if self.dancing:
            out.append(Activity.DANCING)
        if self.manipulation in (
            ManipulationPhase.APPROACH,
            ManipulationPhase.DESCEND,
            ManipulationPhase.CLOSE,
            ManipulationPhase.LIFT,
        ):
            out.append(Activity.REACHING)
        if self.holding_object:
            out.append(Activity.HOLDING)
        return tuple(out)

    # model językowy dostaje zwięzły opis stanu, by mówił prawdę o tym, co robi ciało
    def summary_pl(self) -> str:
        acts = ", ".join(a.value for a in self.activities()) or "bezczynny"
        grip_source = self.grip_evidence.source if self.grip_evidence else "brak pomiaru"
        parts = [
            f"czynności: {acts}",
            f"osoba: {self.person.value}",
            f"chwytak: {self.grip.value} (źródło: {grip_source})",
            f"manipulacja: {self.manipulation.value}",
            f"muzyka: {'tak' if self.music else 'nie'}",
            f"awaryjny stop: {'aktywny - ' + self.estop_reason if self.estop else 'nie'}",
        ]
        return "; ".join(parts)

    # kopia stanu pozwala innym wątkom czytać spójny obraz bez blokowania pętli ruchu
    def snapshot(self) -> "RobotState":
        return replace(self)


JOURNAL_FIELDS = tuple(
    f.name
    for f in fields(RobotState)
    if f.name
    not in {
        "t",
        "audio_level",
        "person_confidence",
        "gaze_target",
        "music_score",
        "grip_evidence",
        "budget_session_pln",
        "budget_total_pln",
        "limit_events",
        "workspace_blocks",
        "last_user_text",
        "last_robot_text",
        "music_bpm",
    }
)


# dziennik przejść stanu służy do obserwacji zachowania na żywo oraz do asercji w testach scenariuszy
class StateJournal:
    # ograniczona długość dziennika chroni pamięć podczas długich sesji
    def __init__(self, maxlen: int = 5000) -> None:
        self._entries: deque[tuple[float, str, object, object]] = deque(maxlen=maxlen)
        self._last: dict[str, object] | None = None
        self._lock = threading.Lock()
        self._total = 0

    # porównanie z poprzednim stanem zapisuje wyłącznie faktyczne zmiany pól
    def observe(self, state: RobotState) -> list[tuple[float, str, object, object]]:
        current = {name: getattr(state, name) for name in JOURNAL_FIELDS}
        changes: list[tuple[float, str, object, object]] = []
        with self._lock:
            if self._last is not None:
                for name, value in current.items():
                    if self._last[name] != value:
                        changes.append((state.t, name, self._last[name], value))
            self._last = current
            self._entries.extend(changes)
            self._total += len(changes)
        return changes

    # przyrostowy odczyt według licznika wszystkich zmian działa także po zapełnieniu bufora i podaje liczbę utraconych wpisów
    def since(self, seq: int) -> tuple[list[tuple[float, str, object, object]], int, int]:
        with self._lock:
            total = self._total
            items = list(self._entries)
        fresh = total - seq
        if fresh <= 0:
            return [], total, 0
        kept = items[-fresh:] if fresh < len(items) else items
        return kept, total, max(0, fresh - len(items))

    # odczyt kopii wpisów jest bezpieczny wątkowo dla interfejsu i testów
    def entries(self, name: str | None = None) -> list[tuple[float, str, object, object]]:
        with self._lock:
            items = list(self._entries)
        return [e for e in items if name is None or e[1] == name]

    # testy potrzebują sekwencji wartości pola, aby sprawdzić kolejność przejść
    def values(self, name: str) -> list[object]:
        return [e[3] for e in self.entries(name)]
