from __future__ import annotations

import asyncio
import contextlib
import threading
import time
from collections import deque

from google.genai import types


# fałszywa sesja live odtwarza zachowanie sdk: receive kończy się wraz z turą, a wysłane elementy są zapisywane
class FakeSession:
    # tury to listy słowników wiadomości serwera walidowane prawdziwym schematem sdk
    def __init__(self, turns: list[list[dict]] | None = None) -> None:
        self.turns: deque[list[dict]] = deque(turns or [])
        self.sent: list[tuple[str, dict]] = []
        self.closed = False

    # zapis wysłanych danych czasu rzeczywistego pozwala sprawdzić audio i klatki obrazu
    async def send_realtime_input(self, **kw) -> None:
        self.sent.append(("realtime", kw))

    # zapis treści klienta pozwala sprawdzić informacje z czujników
    async def send_client_content(self, **kw) -> None:
        self.sent.append(("client", kw))

    # zapis odpowiedzi funkcji pozwala sprawdzić decyzje planisty i sposób ogłoszenia wyniku
    async def send_tool_response(self, **kw) -> None:
        self.sent.append(("tool", kw))

    # iteracja zwraca wiadomości jednej tury, a zamknięta sesja bez tur kończy się pustą iteracją
    async def receive(self):
        while not self.turns and not self.closed:
            await asyncio.sleep(0.005)
        if not self.turns:
            return
        for message in self.turns.popleft():
            yield types.LiveServerMessage.model_validate(message)

    # test dopisuje nową turę serwera z innego wątku
    def push(self, *messages: dict) -> None:
        self.turns.append(list(messages))

    # odpowiedzi funkcji wysłane przez backend w kolejności
    def tool_responses(self) -> list:
        return [kw["function_responses"][0] for kind, kw in self.sent if kind == "tool"]


# łącznik zwraca kolejne sesje lub wyjątki, co pozwala symulować awarie sieci i api
class FakeConnector:
    # elementy są zużywane po kolei, a po ich wyczerpaniu powstają puste sesje
    def __init__(self, items: list | None = None) -> None:
        self.items = deque(items or [])
        self.configs: list = []
        self.sessions: list[FakeSession] = []
        self._lock = threading.Lock()

    # wywołanie zachowuje się jak client.aio.live.connect i zwraca asynchroniczny menedżer kontekstu
    def __call__(self, config):
        with self._lock:
            self.configs.append(config)
            item = self.items.popleft() if self.items else FakeSession()
        if isinstance(item, FakeSession):
            self.sessions.append(item)
        return _context(item)


# menedżer kontekstu zgłasza wyjątek przy otwarciu albo oddaje sesję
@contextlib.asynccontextmanager
async def _context(item):
    if isinstance(item, BaseException):
        raise item
    yield item


# czeka na warunek w wątku testu, bo backend działa we własnym wątku asyncio
def wait_for(predicate, timeout: float = 3.0) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return
        time.sleep(0.005)
    raise AssertionError("warunek nie został spełniony w czasie")


# wiadomość z fragmentem audio w formacie gemini live
def audio_msg(n_samples: int = 2400, value: int = 3000) -> dict:
    pcm = (value).to_bytes(2, "little", signed=True) * n_samples
    return {"server_content": {"model_turn": {"parts": [{"inline_data": {"data": pcm, "mime_type": "audio/pcm;rate=24000"}}]}}}
