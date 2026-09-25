from __future__ import annotations

import threading

import pytest

from so101_expressive.budget import CostMeter
from so101_expressive.conversation.base import (
    AudioChunk,
    IntentRequest,
    Interrupted,
    StatusChanged,
    TurnComplete,
    TurnStarted,
)
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.conversation.tools import function_declarations, validate_call
from so101_expressive.config import Settings
from so101_expressive.state import ApiStatus

from .fake_live import FakeConnector, FakeSession, audio_msg, wait_for


# zbiera zdarzenia z wątku backendu w sposób bezpieczny wątkowo
class Sink:
    # lista zdarzeń jest chroniona blokadą, bo pisze do niej wątek asyncio
    def __init__(self) -> None:
        self.events = []
        self._lock = threading.Lock()

    # funkcja zwrotna przekazywana do backendu
    def __call__(self, event) -> None:
        with self._lock:
            self.events.append(event)

    # filtr po typie upraszcza asercje w testach
    def of(self, cls):
        with self._lock:
            return [e for e in self.events if isinstance(e, cls)]

    # sekwencja statusów połączenia pokazuje przejścia przy awariach
    def statuses(self):
        return [e.status for e in self.of(StatusChanged)]


# backend testowy z krótkim strażnikiem i fałszywym łącznikiem
def make_backend(tmp_path, connector, **env):
    base = {"LEDGER_PATH": str(tmp_path / "ledger.json"), "IDLE_DISCONNECT_S": "0", "RECONNECT_MAX_BACKOFF_S": "0.05"}
    base.update({k.upper(): str(v) for k, v in env.items()})
    settings = Settings.from_env(base)
    sink = Sink()
    meter = CostMeter.from_settings(settings)
    backend = GeminiLiveBackend(settings, meter, sink, connect_fn=connector, watchdog_period=0.02)
    return backend, sink, meter


# deklaracje narzędzi nie mają żadnego parametru liczbowego, więc model nie może zadać pozycji ani prędkości serwa
def test_tool_declarations_expose_only_enums():
    for decl in function_declarations():
        for prop in decl.get("parameters", {}).get("properties", {}).values():
            assert prop["type"] == "STRING" and prop["enum"]


# walidacja odrzuca nieznane funkcje, nadmiarowe pola i wartości spoza wyliczeń
@pytest.mark.parametrize(
    "name,args,ok",
    [
        ("perform_gesture", {"gesture": "nod"}, True),
        ("perform_gesture", {"gesture": "fly"}, False),
        ("perform_gesture", {"gesture": "nod", "angle": "1.5"}, False),
        ("perform_gesture", {"gesture": 3}, False),
        ("set_joint_position", {"joint": "gripper"}, False),
        ("manipulate", {}, False),
        ("get_robot_state", {}, True),
    ],
)
def test_validate_call(name, args, ok):
    assert validate_call(name, args)[0] is ok


# konfiguracja sesji przechodzi walidację prawdziwym schematem sdk i ustawia kompresję oraz wznawianie
def test_live_config_is_valid_for_sdk(tmp_path):
    backend, _, _ = make_backend(tmp_path, FakeConnector())
    cfg = backend.build_config()
    assert cfg.context_window_compression.trigger_tokens == 12000
    assert cfg.context_window_compression.sliding_window.target_tokens == 4000
    assert cfg.session_resumption is not None
    decls = cfg.tools[0].function_declarations
    assert {d.name for d in decls} >= {"perform_gesture", "manipulate", "get_robot_state"}
    assert any(str(d.behavior).endswith("NON_BLOCKING") for d in decls)


# tura z audio i wywołaniem gestu zamienia się na zdarzenia, a odpowiedź funkcji wraca z planowaniem silent
def test_turn_audio_and_gesture_intent(tmp_path):
    session = FakeSession()
    backend, sink, _ = make_backend(tmp_path, FakeConnector([session]))
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED)
    session.push(
        audio_msg(),
        {"tool_call": {"function_calls": [{"id": "c1", "name": "perform_gesture", "args": {"gesture": "nod"}}]}},
        audio_msg(),
        {"server_content": {"turn_complete": True}},
    )
    wait_for(lambda: sink.of(TurnComplete))
    assert len(sink.of(TurnStarted)) == 1 and len(sink.of(AudioChunk)) == 2
    intent = sink.of(IntentRequest)[0]
    assert intent.name == "perform_gesture" and intent.args == {"gesture": "nod"}
    backend.respond_intent("c1", "perform_gesture", {"result": "ok", "komunikat": "wykonuję gest"})
    wait_for(lambda: session.tool_responses())
    resp = session.tool_responses()[0]
    assert resp.id == "c1" and str(resp.scheduling).endswith("SILENT")
    backend.stop()


# niepoprawne wywołanie funkcji nie trafia do planisty i dostaje natychmiastową odmowę
def test_invalid_tool_call_is_rejected_before_planner(tmp_path):
    session = FakeSession()
    backend, sink, _ = make_backend(tmp_path, FakeConnector([session]))
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED)
    session.push({"tool_call": {"function_calls": [{"id": "x", "name": "perform_gesture", "args": {"gesture": "fly"}}]}})
    wait_for(lambda: session.tool_responses())
    assert not sink.of(IntentRequest)
    assert session.tool_responses()[0].response["result"] == "odrzucono"
    backend.stop()


# przerwanie przez serwer trafia jako zdarzenie, które opróżnia bufor i wygasza gest
def test_server_interruption_event(tmp_path):
    session = FakeSession()
    backend, sink, _ = make_backend(tmp_path, FakeConnector([session]))
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED)
    session.push(audio_msg(), {"server_content": {"interrupted": True}})
    wait_for(lambda: sink.of(Interrupted))
    backend.stop()


# awaria sieci przechodzi w status offline i ponowne łączenie aż do odzyskania połączenia
def test_network_failure_then_recovery(tmp_path):
    connector = FakeConnector([OSError("network down"), OSError("still down"), FakeSession()])
    backend, sink, _ = make_backend(tmp_path, connector)
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED, timeout=5.0)
    seq = sink.statuses()
    assert seq.count(ApiStatus.OFFLINE) == 2 and ApiStatus.RECONNECTING in seq
    assert len(connector.configs) == 3
    backend.stop()


# odrzucony klucz api jest błędem nienaprawialnym i nie powoduje pętli ponownych prób
def test_auth_error_stops_retrying(tmp_path):
    # błąd z kodem 401 naśladuje wyjątek sdk przy odrzuconym kluczu api
    class AuthError(Exception):
        code = 401

    connector = FakeConnector([AuthError("bad key")])
    backend, sink, _ = make_backend(tmp_path, connector)
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.ERROR)
    wait_for(lambda: len(connector.configs) == 1)
    import time

    time.sleep(0.2)
    assert len(connector.configs) == 1
    backend.stop()


# przekroczenie budżetu zamyka sesję, blokuje wysyłanie audio i nie łączy ponownie
def test_budget_exceeded_disables_api(tmp_path):
    session = FakeSession()
    connector = FakeConnector([session])
    backend, sink, meter = make_backend(tmp_path, connector, budget_session_pln="0.05")
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED)
    session.push({"usage_metadata": {"prompt_token_count": 20000, "prompt_tokens_details": [{"modality": "AUDIO", "token_count": 20000}]}})
    wait_for(lambda: backend.status is ApiStatus.BUDGET_EXCEEDED)
    sent_before = len(session.sent)
    backend.send_audio(b"\x00\x00" * 512, 16000)
    import time

    time.sleep(0.2)
    assert len(session.sent) == sent_before
    assert len(connector.configs) == 1
    assert meter.snapshot().blocked
    backend.stop()


# komunikat goaway kończy połączenie i wznawia sesję z ostatnim uchwytem
def test_goaway_reconnects_with_resumption_handle(tmp_path):
    first = FakeSession()
    connector = FakeConnector([first, FakeSession()])
    backend, sink, _ = make_backend(tmp_path, connector)
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED)
    first.push(
        {"session_resumption_update": {"new_handle": "handle-42", "resumable": True}},
        {"go_away": {"time_left": "5s"}},
    )
    wait_for(lambda: len(connector.configs) == 2)
    assert connector.configs[1].session_resumption.handle == "handle-42"
    backend.stop()


# bezczynność rozłącza sesję, żeby nie płacić za nasłuch, a wybudzenie łączy ponownie
def test_idle_disconnect_and_wake(tmp_path):
    connector = FakeConnector([FakeSession(), FakeSession()])
    backend, sink, _ = make_backend(tmp_path, connector, idle_disconnect_s="0.15")
    backend.start()
    wait_for(lambda: backend.status is ApiStatus.IDLE)
    backend.wake()
    wait_for(lambda: backend.status is ApiStatus.CONNECTED and len(connector.configs) == 2)
    backend.stop()
