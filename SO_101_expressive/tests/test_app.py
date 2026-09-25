from __future__ import annotations

import numpy as np
import pytest

from so101_expressive.app import LOOK_GRACE_S, RobotApp
from so101_expressive.config import Settings
from so101_expressive.conversation.base import IntentCancelled, IntentRequest, StatusChanged, Transcript
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.inputs.camera import VisionUplink, asks_to_look
from so101_expressive.inputs.virtual import VirtualAudioRig
from so101_expressive.state import ApiStatus, PersonStatus, RobotState

from .test_scenarios import BabbleTTS

FRAME = np.zeros((480, 640, 3), dtype=np.uint8)
PAST_GRACE = int(LOOK_GRACE_S / 0.1) + 2


# atrapa połączonego backendu zapisuje, co i w jakiej kolejności opuściło laptopa
class RecordingBackend:
    status = ApiStatus.CONNECTED

    # listy są puste, dopóki aplikacja niczego nie wyśle do chmury
    def __init__(self) -> None:
        self.frames: list[bytes] = []
        self.sent: list[str] = []

    # wywoływana przez uplink przy każdym wysłaniu klatki jpeg
    def send_image(self, jpeg: bytes) -> None:
        self.frames.append(jpeg)
        self.sent.append("klatka")

    # odpowiedź funkcji zapisuje wynik, żeby sprawdzić jej kolejność względem klatki
    def respond_intent(self, call_id: str, name: str, result: dict) -> None:
        self.sent.append(f"odpowiedź:{result['result']}")

    # komunikaty z czujników nie są badane w tych testach, ale muszą dać się wysłać
    def send_context(self, text: str) -> None:
        self.sent.append("kontekst")


# kamera testowa zwraca stałą klatkę z zadanym znacznikiem czasu, jak prawdziwe źródło obrazu
class FakeCamera:
    # znacznik czasu pozwala sprawdzić odrzucanie przeterminowanych klatek
    def __init__(self, t: float) -> None:
        self.t = t

    # ta sama sygnatura co w prawdziwym źródle kamery
    def latest(self) -> tuple[np.ndarray, float]:
        return FRAME, self.t


# zestaw prowadzi aplikację przez pętlę ciała i obsługę panelu dokładnie tak, jak w działającym programie
class LookRig:
    # rozmówca był słyszany lokalnie chwilę przed prośbą, a kamera domyślnie daje świeże klatki
    def __init__(self, settings, t0: float = 100.0) -> None:
        self.app = RobotApp(settings, virtual=True, backend="gemini", window=False)
        self.sink = RecordingBackend()
        self.app.backend = self.sink
        self.app.pipeline.last_vad_speech_t = t0 - 1.0
        self.frame_age: float | None = 0.05
        self.t = t0

    # rozpoznana wypowiedź rozmówcy albo robota dociera tą samą drogą co z backendu rozmowy
    def say(self, text: str, role: str = "user") -> None:
        self.app._on_event(Transcript(role, text))

    # prośba modelu o spojrzenie trafia do pętli ciała jak wywołanie funkcji z backendu
    def request(self, call_id: str = "c") -> None:
        self.app._on_event(IntentRequest(call_id, "look_at_scene", {}))

    # krok czasu wykonuje pętlę ciała i obsługę panelu z klatką kamery w zadanym wieku
    def tick(self, n: int = 1, dt: float = 0.1) -> None:
        for _ in range(n):
            self.t += dt
            self.app.camera = None if self.frame_age is None else FakeCamera(self.t - self.frame_age)
            self.app.body.step(self.t)
            self.app._housekeeping(self.app.body.snapshot(), FRAME, self.t)


# mowa z osi czasu dema działa także z backendem gemini, który nie ma metody say, więc demo nie przerywa się wyjątkiem
def test_virtual_timeline_speech_works_with_gemini_backend(settings):
    app = RobotApp(settings, virtual=True, backend="gemini", window=False)
    assert isinstance(app.backend, GeminiLiveBackend)
    rig = VirtualAudioRig(app.playback, app.pipeline)
    _, events = app._demo_timeline(BabbleTTS(), rig)
    speak = next(action for _, label, action in events if label == "mowa podczas trzymania")
    speak(43.0)
    assert app.playback.has_pending()


# cykliczne wysyłanie klatek jest domyślnie wyłączone, a po jawnym ustawieniu odstępu działa tylko przy widocznym rozmówcy
def test_periodic_uploads_are_opt_in(settings):
    assert settings.vision_uplink_interval_s == 0.0 and settings.camera_cloud == "on_request"
    sink = RecordingBackend()
    off = VisionUplink(settings.vision_uplink_interval_s)
    assert not any(off.maybe_send(sink, FRAME, float(k), PersonStatus.TRACKED) for k in range(100))
    periodic = VisionUplink(12.0)
    assert sum(periodic.maybe_send(sink, FRAME, float(k), PersonStatus.TRACKED) for k in range(30)) == 3
    assert not periodic.maybe_send(sink, FRAME, 100.0, PersonStatus.ABSENT)


# prośba o spojrzenie jest rozpoznawana z polskimi znakami i bez nich, a zwykła rozmowa czy tekst piosenki jej nie zawiera
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Robo, co widzisz na stole?", True),
        ("spojrz na to", True),
        ("Popatrz, co trzymam!", True),
        ("pokażę ci coś ciekawego", True),
        ("Użyj kamery", True),
        ("Jak wyglądam?", True),
        ("what do you see", True),
        ("Opowiedz mi o pogodzie", False),
        ("la la la kocham cię", False),
        ("", False),
    ],
)
def test_asks_to_look(text, expected):
    assert asks_to_look(text) is expected


# sama energia dźwięku, np. muzyka lub hałas, bez rozpoznanej prośby rozmówcy nigdy nie wysyła klatki
@pytest.mark.parametrize("heard", [None, "la la la kocham cię, la la la"])
def test_music_or_noise_alone_never_sends_a_frame(settings, heard):
    rig = LookRig(settings)
    if heard is not None:
        rig.say(heard)
    rig.request()
    rig.tick(3)
    assert rig.sink.sent == []
    rig.tick(PAST_GRACE)
    assert rig.sink.frames == [] and rig.sink.sent == ["odpowiedź:odrzucono"]
    assert rig.app.consent.pending is None


# rozpoznana prośba rozmówcy odblokowuje dokładnie jedną klatkę, wysłaną przed odpowiedzią funkcji
def test_recognized_request_sends_one_frame_before_response(settings):
    rig = LookRig(settings)
    rig.say("Robo, co widzisz na stole?")
    rig.request("c1")
    rig.tick()
    assert rig.sink.sent == ["klatka", "odpowiedź:ok"] and rig.app.uplink.sent == 1
    rig.request("c2")
    rig.tick(PAST_GRACE)
    assert len(rig.sink.frames) == 1 and rig.sink.sent[-1] == "odpowiedź:odrzucono"


# transkrypcja przychodzi bez gwarancji kolejności, więc prośba modelu krótko czeka na rozpoznaną wypowiedź
def test_transcript_arriving_after_tool_call_is_awaited(settings):
    rig = LookRig(settings)
    rig.request()
    rig.tick(2)
    assert rig.sink.sent == []
    rig.say("spójrz na to")
    rig.tick()
    assert rig.sink.sent == ["klatka", "odpowiedź:ok"]


# nowa wypowiedź z prośbą po odpowiedzi robota daje nową, znów jednorazową zgodę
def test_new_utterance_allows_another_frame(settings):
    rig = LookRig(settings)
    rig.say("co widzisz?")
    rig.request("c1")
    rig.tick()
    turn = rig.app.body.state.user_turn
    rig.say("Widzę pomarańczową kostkę.", role="robot")
    rig.tick()
    rig.say("a teraz popatrz jeszcze raz")
    rig.request("c2")
    rig.tick()
    assert rig.app.body.state.user_turn == turn + 1
    assert len(rig.sink.frames) == 2 and rig.sink.sent.count("odpowiedź:ok") == 2


# anulowanie przez serwer albo rozłączenie usuwa oczekującą prośbę, więc późniejsza wypowiedź niczego nie wysyła
@pytest.mark.parametrize("event", [IntentCancelled(("c",)), StatusChanged(ApiStatus.OFFLINE, "test")])
def test_cancelled_or_disconnected_look_sends_nothing(settings, event):
    rig = LookRig(settings)
    rig.request("c")
    rig.tick()
    rig.app._on_event(event)
    rig.say("co widzisz?")
    rig.tick(PAST_GRACE)
    assert rig.sink.frames == [] and rig.sink.sent == []


# brak lokalnie usłyszanej mowy albo świeżej klatki kończy się odmową, która nie zostawia niczego do wysłania później
def test_refusals_send_nothing_and_leave_nothing_pending(settings):
    quiet = LookRig(settings)
    quiet.app.pipeline.last_vad_speech_t = 50.0
    quiet.say("co widzisz?")
    quiet.request()
    quiet.tick()
    assert quiet.sink.sent == ["odpowiedź:odrzucono"] and quiet.app.consent.pending is None
    stale = LookRig(settings)
    stale.frame_age = 5.0
    stale.say("spójrz")
    stale.request()
    stale.tick()
    assert stale.sink.sent == ["odpowiedź:odrzucono"]
    stale.frame_age = 0.05
    stale.tick(PAST_GRACE)
    assert stale.sink.frames == []


# wyłącznik camera_cloud=off i wyłączona transkrypcja blokują wysyłanie obrazu niezależnie od próśb modelu
@pytest.mark.parametrize("env", [{"CAMERA_CLOUD": "off", "VISION_UPLINK_INTERVAL_S": "5"}, {"LIVE_TRANSCRIPTS": "nie"}])
def test_camera_off_or_no_transcripts_blocks_uploads(tmp_path, env):
    settings = Settings.from_env({"LEDGER_PATH": str(tmp_path / "l.json"), "LOG_DIR": str(tmp_path / "logs"), **env})
    rig = LookRig(settings)
    rig.say("co widzisz?")
    rig.request()
    rig.tick()
    for k in range(30):
        rig.app._housekeeping(RobotState(t=rig.t + k, person=PersonStatus.TRACKED), FRAME, rig.t + k)
    assert rig.sink.frames == [] and rig.sink.sent == ["odpowiedź:odrzucono"]
