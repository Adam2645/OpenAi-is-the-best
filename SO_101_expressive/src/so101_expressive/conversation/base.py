from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from ..state import ApiStatus


# wspólna baza zdarzeń pozwala dodać później tor stt, llm i tts bez zmian w sterowniku ramienia
@dataclass(frozen=True)
class ConversationEvent:
    pass


# fragment mowy robota w formacie pcm 16 bit, który trafia do bufora odtwarzania
@dataclass(frozen=True)
class AudioChunk(ConversationEvent):
    pcm: bytes
    rate: int = 24000


# początek tury robota ustawia fazę mówienia zanim pojawi się pierwszy dźwięk
@dataclass(frozen=True)
class TurnStarted(ConversationEvent):
    pass


# koniec tury pozwala wrócić do słuchania po odtworzeniu reszty bufora
@dataclass(frozen=True)
class TurnComplete(ConversationEvent):
    pass


# przerwanie wypowiedzi wymaga natychmiastowego opróżnienia bufora i wygaszenia gestu
@dataclass(frozen=True)
class Interrupted(ConversationEvent):
    pass


# transkrypcje służą tylko do podglądu i logów, ruch szczęki ich nie używa
@dataclass(frozen=True)
class Transcript(ConversationEvent):
    role: str
    text: str


# prośba modelu o czynność ciała przechodzi walidację i decyzję planisty, nigdy nie jest pozycją serwa
@dataclass(frozen=True)
class IntentRequest(ConversationEvent):
    call_id: str
    name: str
    args: dict = field(default_factory=dict)


# anulowanie wywołań przez serwer musi przerwać związane z nimi gesty
@dataclass(frozen=True)
class IntentCancelled(ConversationEvent):
    ids: tuple[str, ...]


# zmiana stanu połączenia pozwala robotowi przejść w tryb lokalny zamiast zawiesić się
@dataclass(frozen=True)
class StatusChanged(ConversationEvent):
    status: ApiStatus
    detail: str = ""


EventSink = Callable[[ConversationEvent], None]


# granica interfejsu rozmowy oddziela dostawcę głosu od stanu robota i sterowania ruchem
class ConversationBackend(ABC):
    # zdarzenia są oddawane przez funkcję zwrotną, więc backend nie zna szczegółów robota
    def __init__(self, sink: EventSink) -> None:
        self.sink = sink
        self._status = ApiStatus.DISABLED

    # bieżący status jest czytany przez bramkę mikrofonu, aby nie wysyłać audio w próżnię
    @property
    def status(self) -> ApiStatus:
        return self._status

    # zmiana statusu zawsze trafia też do stanu robota jako zdarzenie
    def _set_status(self, status: ApiStatus, detail: str = "") -> None:
        self._status = status
        self.sink(StatusChanged(status, detail))

    # uruchomienie backendu nie może blokować wątku wywołującego
    @abstractmethod
    def start(self) -> None: ...

    # zatrzymanie musi zamknąć połączenie i przestać naliczać koszty
    @abstractmethod
    def stop(self) -> None: ...

    # dźwięk z mikrofonu po bramce echa w formacie pcm 16 bit mono
    @abstractmethod
    def send_audio(self, pcm16: bytes, rate: int) -> None: ...

    # pauza strumienia audio informuje serwer, że użytkownik skończył mówić
    @abstractmethod
    def end_audio(self) -> None: ...

    # rzadka klatka obrazu daje kontekst wizualny bez udziału w szybkiej pętli śledzenia
    @abstractmethod
    def send_image(self, jpeg: bytes) -> None: ...

    # krótka informacja tekstowa o zdarzeniu z czujników, np. o wykrytej muzyce
    @abstractmethod
    def send_context(self, text: str) -> None: ...

    # odpowiedź na prośbę modelu mówi, czy ciało wykonało czynność i dlaczego nie
    @abstractmethod
    def respond_intent(self, call_id: str, name: str, result: dict) -> None: ...

    # wybudzenie po bezczynności pozwala rozłączać sesję, gdy nikogo nie ma, i oszczędzać budżet
    def wake(self) -> None:
        return None
