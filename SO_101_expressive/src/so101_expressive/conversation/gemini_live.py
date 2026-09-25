from __future__ import annotations

import asyncio
import json
import random
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable

from ..budget import CostMeter
from ..config import Settings
from ..state import ApiStatus
from .base import (
    AudioChunk,
    ConversationBackend,
    EventSink,
    IntentCancelled,
    IntentRequest,
    Interrupted,
    Transcript,
    TurnComplete,
    TurnStarted,
)
from .prompt import SYSTEM_PROMPT_PL
from .tools import function_declarations, response_scheduling, validate_call

ConnectFn = Callable[[Any], Any]
IMAGE_MAX_QUEUE_S = 2.0


# klasyfikacja błędu decyduje, czy ponawiać połączenie i jaki komunikat pokazać, bez ujawniania klucza
def classify_error(exc: BaseException) -> tuple[ApiStatus, str, bool]:
    code = getattr(exc, "code", None)
    name = type(exc).__name__
    rcvd = getattr(exc, "rcvd", None)
    close_code = getattr(rcvd, "code", None) if rcvd is not None else None
    if isinstance(code, int):
        if code in (401, 403):
            return ApiStatus.ERROR, f"odrzucony klucz api ({code}) - sprawdź GEMINI_API_KEY", False
        if code == 404:
            return ApiStatus.ERROR, "nieznany model live (404) - sprawdź LIVE_MODEL", False
        if code == 429:
            return ApiStatus.ERROR, "limit zapytań lub brak środków (429)", True
        return ApiStatus.ERROR, f"błąd api ({code})", True
    if close_code in (1007, 1008):
        reason = str(getattr(rcvd, "reason", ""))[:120]
        return ApiStatus.ERROR, f"serwer odrzucił sesję (kod {close_code}) {reason}".strip(), False
    if isinstance(exc, (OSError, TimeoutError, asyncio.TimeoutError)) or "ConnectionClosed" in name or "InvalidStatus" in name:
        return ApiStatus.OFFLINE, f"brak połączenia z api ({name})", True
    return ApiStatus.ERROR, f"nieoczekiwany błąd ({name})", True


# częstotliwość próbkowania odczytujemy z typu mime, bo serwer podaje ją w każdym fragmencie audio
def _rate_from_mime(mime: str | None, default: int = 24000) -> int:
    if mime and "rate=" in mime:
        try:
            return int(mime.split("rate=")[1].split(";")[0])
        except ValueError:
            return default
    return default


# backend gemini live prowadzi strumieniową rozmowę głosową w osobnym wątku z własną pętlą asyncio
class GeminiLiveBackend(ConversationBackend):
    # funkcja łącząca jest wstrzykiwana, dzięki czemu testy symulują serwer, błędy sieci i wyczerpanie budżetu
    def __init__(
        self,
        settings: Settings,
        meter: CostMeter,
        sink: EventSink,
        connect_fn: ConnectFn | None = None,
        clock: Callable[[], float] = time.monotonic,
        usage_log: Path | None = None,
        watchdog_period: float = 1.0,
    ) -> None:
        super().__init__(sink)
        self.settings = settings
        self.meter = meter
        self.clock = clock
        self.usage_log = usage_log
        self.watchdog_period = watchdog_period
        self._connect_fn = connect_fn
        self._client = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._outq: asyncio.Queue | None = None
        self._wake: asyncio.Event | None = None
        self._stopping = threading.Event()
        self._handle: str | None = None
        self._turn_active = False
        self._drop_audio = False
        self._goaway = False
        self._last_activity = clock()
        self.reconnects = 0
        self.dropped_audio = 0
        self.dropped_images = 0
        self.errors: deque[str] = deque(maxlen=50)
        self.sent: dict[str, int] = {"audio": 0, "audio_end": 0, "image": 0, "context": 0, "tool": 0}

    # bez klucza api backend zgłasza tryb wyłączony, a robot działa dalej lokalnie
    def start(self) -> None:
        if self._connect_fn is None and not self.settings.gemini_api_key:
            self._set_status(ApiStatus.DISABLED, "brak GEMINI_API_KEY - rozmowa wyłączona")
            return
        self._thread = threading.Thread(target=self._thread_main, name="gemini-live", daemon=True)
        self._thread.start()
        deadline = time.monotonic() + 2.0
        while self._loop is None and time.monotonic() < deadline:
            time.sleep(0.005)

    # wątek ma własną pętlę zdarzeń, a przy wyjściu zapisuje wydatki do rejestru
    def _thread_main(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._outq = asyncio.Queue()
        self._wake = asyncio.Event()
        self._loop = loop
        try:
            loop.run_until_complete(self._main())
        except asyncio.CancelledError:
            pass
        finally:
            self.meter.flush()
            loop.close()

    # zatrzymanie anuluje zadania sesji i czeka na zamknięcie połączenia
    def stop(self, timeout: float = 3.0) -> None:
        self._stopping.set()
        loop = self._loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(self._cancel_all)
        if self._thread is not None:
            self._thread.join(timeout)
        self.meter.flush()

    # anulowanie wszystkich zadań pętli kończy trwającą sesję websocket
    def _cancel_all(self) -> None:
        if self._wake is not None:
            self._wake.set()
        for task in asyncio.all_tasks(self._loop):
            task.cancel()

    # elementy do wysłania trafiają do kolejki pętli asyncio w sposób bezpieczny wątkowo
    def _post(self, item: tuple) -> None:
        loop = self._loop
        if loop is None or self._outq is None or not loop.is_running():
            return
        loop.call_soon_threadsafe(self._outq.put_nowait, item)

    # dźwięk wysyłamy tylko przy aktywnym połączeniu, a przy zatorze sieci odrzucamy nadmiar zamiast budować opóźnienie
    def send_audio(self, pcm16: bytes, rate: int) -> None:
        if self._status is not ApiStatus.CONNECTED:
            return
        if self._outq is not None and self._outq.qsize() > 150:
            self.dropped_audio += 1
            return
        self._last_activity = self.clock()
        self._post(("audio", pcm16, rate))

    # koniec strumienia audio przyspiesza odpowiedź serwera w trybie hybrydowego vad
    def end_audio(self) -> None:
        if self._status is ApiStatus.CONNECTED:
            self._post(("audio_end",))

    # klatka czeka w kolejce z czasem i warunkiem wysłania, żeby anulowanie lub zator sieci mogły ją jeszcze zatrzymać
    def send_image(self, jpeg: bytes, allow: Callable[[], bool] | None = None) -> None:
        if self._status is ApiStatus.CONNECTED:
            self._post(("image", jpeg, self.clock(), allow))

    # informacja z czujników dopisywana do kontekstu bez kończenia tury rozmówcy
    def send_context(self, text: str) -> None:
        if self._status is ApiStatus.CONNECTED:
            self._post(("context", text))

    # odpowiedź na wywołanie funkcji zawiera wynik planisty, a warunek pozwala pominąć ją, gdy serwer anulował wywołanie
    def respond_intent(self, call_id: str, name: str, result: dict, allow: Callable[[], bool] | None = None) -> None:
        self._post(("tool", call_id, name, result, allow))

    # lokalne przerwanie odrzuca resztę bieżącej tury, gdy użytkownik wciśnie klawisz przerwania
    def interrupt_local(self) -> None:
        if self._turn_active:
            self._drop_audio = True

    # obecność rozmówcy w kadrze podtrzymuje sesję mimo chwilowej ciszy
    def note_activity(self) -> None:
        self._last_activity = self.clock()

    # wybudzenie po rozłączeniu z bezczynności następuje, gdy lokalny vad usłyszy mowę albo pojawi się osoba
    def wake(self) -> None:
        loop = self._loop
        if loop is not None and loop.is_running() and self._wake is not None:
            self._last_activity = self.clock()
            loop.call_soon_threadsafe(self._wake.set)

    # konfiguracja sesji ustawia głos, narzędzia, transkrypcje, vad, kompresję kontekstu i wznawianie
    def build_config(self):
        from google.genai import types

        s = self.settings
        transcription = None
        if s.live_transcripts:
            transcription = types.AudioTranscriptionConfig(
                language_codes=[s.transcript_language_hint] if s.transcript_language_hint else None
            )
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=SYSTEM_PROMPT_PL,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=s.voice_name))
            ),
            tools=[types.Tool(function_declarations=[types.FunctionDeclaration(**d) for d in function_declarations()])],
            input_audio_transcription=transcription,
            output_audio_transcription=types.AudioTranscriptionConfig() if s.live_transcripts else None,
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    silence_duration_ms=s.vad_silence_ms, prefix_padding_ms=s.vad_prefix_ms,
                )
            ),
            context_window_compression=types.ContextWindowCompressionConfig(
                trigger_tokens=s.context_trigger_tokens,
                sliding_window=types.SlidingWindow(target_tokens=s.context_target_tokens),
            ),
            session_resumption=types.SessionResumptionConfig(handle=self._handle),
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
        )

    # otwarcie sesji używa sdk google-genai albo wstrzykniętej funkcji testowej
    def _open(self):
        config = self.build_config()
        if self._connect_fn is not None:
            return self._connect_fn(config)
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client.aio.live.connect(model=self.settings.live_model, config=config)

    # przerywalne czekanie pozwala szybko zamknąć program w trakcie odczekiwania na ponowne połączenie
    async def _sleep(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while not self._stopping.is_set() and time.monotonic() < end:
            await asyncio.sleep(min(0.05, end - time.monotonic()))

    # po błędzie nienaprawialnym backend czeka na zamknięcie programu zamiast ponawiać bez końca
    async def _wait_stop(self) -> None:
        while not self._stopping.is_set():
            await asyncio.sleep(0.05)

    # zerwane połączenie w środku tury kończy ją, żeby robot nie utknął w stanie mówienia
    def _turn_reset(self) -> None:
        if self._turn_active:
            self._turn_active = False
            self._drop_audio = False
            self.sink(TurnComplete())

    # główna pętla łączy, ponawia z wykładniczym odstępem i respektuje budżet oraz bezczynność
    async def _main(self) -> None:
        backoff = 1.0
        first = True
        idle = False
        while not self._stopping.is_set():
            if not self.meter.allow():
                self._set_status(ApiStatus.BUDGET_EXCEEDED, self.meter.snapshot().reason)
                await self._wait_stop()
                return
            if idle:
                self._set_status(ApiStatus.IDLE, "brak rozmowy - sesja rozłączona, koszty nie rosną")
                self._wake.clear()
                while not self._wake.is_set() and not self._stopping.is_set():
                    await asyncio.sleep(0.05)
                idle = False
                if self._stopping.is_set():
                    return
            self._set_status(ApiStatus.CONNECTING if first else ApiStatus.RECONNECTING)
            first = False
            try:
                async with self._open() as session:
                    self._set_status(ApiStatus.CONNECTED, self.settings.live_model)
                    backoff = 1.0
                    self._goaway = False
                    self._last_activity = self.clock()
                    reason = await self._run_session(session)
                self._turn_reset()
                self.meter.flush()
                if reason == "idle":
                    idle = True
                elif reason in ("goaway", "closed"):
                    self.reconnects += 1
                    if reason == "closed":
                        await self._sleep(0.5)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                status, message, retry = classify_error(exc)
                self.errors.append(message)
                self._turn_reset()
                self._set_status(status, message)
                if not retry:
                    await self._wait_stop()
                    return
                await self._sleep(backoff * (0.8 + 0.4 * random.random()))
                backoff = min(backoff * 2.0, self.settings.reconnect_max_backoff_s)

    # sesja trwa, dopóki nadawca, odbiorca i strażnik nie zgłoszą powodu zakończenia albo błędu
    async def _run_session(self, session) -> str:
        tasks = {
            asyncio.create_task(self._sender(session)),
            asyncio.create_task(self._receiver(session)),
            asyncio.create_task(self._watchdog()),
        }
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        for task in done:
            if task.exception() is not None:
                raise task.exception()
        return next(iter(done)).result()

    # nadawca opróżnia kolejkę i przed każdym wysłaniem sprawdza budżet
    async def _sender(self, session) -> str:
        from google.genai import types

        while True:
            try:
                item = await asyncio.wait_for(self._outq.get(), 0.25)
            except asyncio.TimeoutError:
                if self._stopping.is_set():
                    return "stop"
                continue
            if not self.meter.allow():
                return "budget"
            kind = item[0]
            if kind == "audio":
                _, pcm, rate = item
                await session.send_realtime_input(audio=types.Blob(data=pcm, mime_type=f"audio/pcm;rate={rate}"))
                self.meter.add_audio_in(len(pcm) / 2.0 / rate)
            elif kind == "audio_end":
                await session.send_realtime_input(audio_stream_end=True)
            elif kind == "image":
                _, jpeg, queued_t, allow = item
                if self.clock() - queued_t > IMAGE_MAX_QUEUE_S or (allow is not None and not allow()):
                    self.dropped_images += 1
                    continue
                await session.send_realtime_input(video=types.Blob(data=jpeg, mime_type="image/jpeg"))
                self.meter.add_image()
            elif kind == "context":
                text = item[1]
                await session.send_client_content(
                    turns=[types.Content(role="user", parts=[types.Part(text=text)])], turn_complete=False
                )
                self.meter.add_text_in(len(text))
            elif kind == "tool":
                _, call_id, name, result, *rest = item
                allow = rest[0] if rest else None
                if allow is not None and not allow():
                    continue
                accepted = result.get("result") == "ok"
                scheduling = response_scheduling(name, accepted)
                payload = {**result, "scheduling": scheduling}
                await session.send_tool_response(
                    function_responses=[types.FunctionResponse(id=call_id, name=name, response=payload, scheduling=scheduling)]
                )
            self.sent[kind] = self.sent.get(kind, 0) + 1

    # odbiorca wywołuje receive w pętli, bo każda iteracja sdk kończy się wraz z turą modelu
    async def _receiver(self, session) -> str:
        while True:
            got = False
            async for message in session.receive():
                got = True
                self._handle_message(message)
                if self._goaway:
                    return "goaway"
            if not got:
                return "closed"

    # strażnik liczy czas nasłuchu do kosztów, pilnuje budżetu i rozłącza przy bezczynności
    async def _watchdog(self) -> str:
        last = self.clock()
        flushed = last
        while True:
            await asyncio.sleep(self.watchdog_period)
            now = self.clock()
            if self.settings.bill_listening_time:
                self.meter.add_listening_time(max(0.0, now - last))
            last = now
            if self._stopping.is_set():
                return "stop"
            if not self.meter.allow():
                return "budget"
            if self._goaway:
                return "goaway"
            idle_s = self.settings.idle_disconnect_s
            if idle_s > 0 and not self._turn_active and now - self._last_activity > idle_s:
                return "idle"
            if now - flushed > 10.0:
                self.meter.flush()
                flushed = now

    # zapis surowych metadanych zużycia pozwala później porównać szacunek z rachunkiem w ai studio
    def _log_usage(self, usage) -> None:
        if self.usage_log is None:
            return
        self.usage_log.parent.mkdir(parents=True, exist_ok=True)
        with self.usage_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": time.time(), "usage": usage.model_dump(mode="json", exclude_none=True)}) + "\n")

    # obsługa wiadomości serwera zamienia je na zdarzenia niezależne od dostawcy rozmowy
    def _handle_message(self, msg) -> None:
        if msg.usage_metadata is not None:
            self.meter.record_server_usage(msg.usage_metadata)
            self._log_usage(msg.usage_metadata)
        update = msg.session_resumption_update
        if update is not None and update.resumable and update.new_handle:
            self._handle = update.new_handle
        if msg.go_away is not None:
            self._goaway = True
        content = msg.server_content
        if content is not None:
            self._last_activity = self.clock()
            if content.interrupted:
                self._turn_active = False
                self._drop_audio = False
                self.sink(Interrupted())
            turn = content.model_turn
            if turn is not None and turn.parts:
                for part in turn.parts:
                    blob = part.inline_data
                    if blob is not None and blob.data:
                        if not self._turn_active:
                            self._turn_active = True
                            self.sink(TurnStarted())
                        rate = _rate_from_mime(blob.mime_type)
                        self.meter.add_audio_out(len(blob.data) / 2.0 / rate)
                        if not self._drop_audio:
                            self.sink(AudioChunk(blob.data, rate))
            if content.input_transcription is not None and content.input_transcription.text:
                self.meter.add_text_out(len(content.input_transcription.text))
                self.sink(Transcript("user", content.input_transcription.text))
            if content.output_transcription is not None and content.output_transcription.text:
                self.meter.add_text_out(len(content.output_transcription.text))
                self.sink(Transcript("robot", content.output_transcription.text))
            if content.turn_complete:
                self._turn_active = False
                self._drop_audio = False
                self.meter.on_turn_complete()
                self.sink(TurnComplete())
        call = msg.tool_call
        if call is not None and call.function_calls:
            for fc in call.function_calls:
                ok, parsed = validate_call(fc.name or "", fc.args or {})
                if ok:
                    self.sink(IntentRequest(fc.id or "", fc.name, parsed))
                else:
                    self._post(("tool", fc.id or "", fc.name or "", {"result": "odrzucono", "komunikat": parsed}))
        cancel = msg.tool_call_cancellation
        if cancel is not None and cancel.ids:
            self.sink(IntentCancelled(tuple(cancel.ids)))
