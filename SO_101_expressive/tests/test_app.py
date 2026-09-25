from __future__ import annotations

import numpy as np
import pytest

from so101_expressive.app import LOOK_GRACE_S, RobotApp
from so101_expressive.config import Settings
from so101_expressive.conversation.base import IntentCancelled, IntentRequest, StatusChanged, Transcript
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.inputs.camera import VisionUplink, asks_to_look
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.inputs.virtual import VirtualAudioRig
from so101_expressive.runtime import AudioStatus, create_body
from so101_expressive.state import ApiStatus, PersonStatus, RobotState
from so101_expressive.util import LatestValue

from .test_scenarios import BabbleTTS

FRAME = np.zeros((480, 640, 3), dtype=np.uint8)
PAST_GRACE = int(LOOK_GRACE_S / 0.1) + 2
ACCEPTED = [
    "Robo, co widzisz na stole?",
    "spójrz na to",
    "Popatrz, co trzymam!",
    "pokażę ci coś ciekawego",
    "Użyj kamery i powiedz, co jest na biurku",
    "Jak wyglądam?",
    "Czy możesz spojrzeć na biurko?",
    "zerknij tutaj",
    "Czy widzisz mnie?",
    "Nie, spójrz!",
    "Nie patrz teraz. Dobra, już możesz, spójrz.",
    "what do you see",
    "Look at this.",
    "Can you take a look?",
]
REJECTED = [
    "nie patrz",
    "Nie patrz na mnie, proszę.",
    "patrzę na ciebie",
    "Widzisz, problem polega na tym",
    "Widać, że jesteś zmęczony",
    "Wyglądasz dziś świetnie",
    "Kamera jest wyłączona?",
    "Pokaż mi taniec",
    "Spójrz... a zresztą nie",
    "Spójrz, nie!",
    "Czy możesz nie patrzeć?",
    "Nie nagrywaj mnie",
    "Wyłącz kamerę",
    "don't look at me",
    "I look tired",
    "Mój brat mówi „spójrz na to”",
    "rozpoznawanie mowy działa",
    "zobaczymy",
    "chcę zobaczyć",
    "Opowiedz mi o pogodzie",
    "la la la kocham cię",
    "",
]


# atrapa połączonego backendu kolejkuje wysyłki z warunkami, a flush odgrywa nadawcę w punkcie ujawnienia danych
class RecordingBackend:
    status = ApiStatus.CONNECTED

    # kolejka i lista ujawnionych danych są puste, dopóki aplikacja niczego nie wyśle do chmury
    def __init__(self) -> None:
        self.queue: list[tuple[str, object]] = []
        self.sent: list[str] = []
        self.frames = 0

    # klatka trafia do kolejki razem z warunkiem sprawdzanym dopiero przy wysyłaniu
    def send_image(self, jpeg: bytes, allow=None) -> None:
        self.queue.append(("klatka", allow))

    # odpowiedź funkcji trafia do tej samej kolejki, więc zachowana jest kolejność względem klatki
    def respond_intent(self, call_id: str, name: str, result: dict, allow=None) -> None:
        self.queue.append((f"odpowiedź:{result['result']}", allow))

    # komunikaty z czujników nie są badane w tych testach, ale muszą dać się wysłać
    def send_context(self, text: str) -> None:
        self.queue.append(("kontekst", None))

    # nadawca sprawdza warunek każdego elementu tuż przed wysłaniem, jak prawdziwy backend
    def flush(self) -> None:
        for label, allow in self.queue:
            if allow is None or allow():
                self.sent.append(label)
                if label == "klatka":
                    self.frames += 1
        self.queue.clear()


# kamera testowa zwraca stałą klatkę z zadanym znacznikiem czasu, jak prawdziwe źródło obrazu
class FakeCamera:
    # znacznik czasu pozwala sprawdzić odrzucanie przeterminowanych klatek
    def __init__(self, t: float) -> None:
        self.t = t

    # ta sama sygnatura co w prawdziwym źródle kamery
    def latest(self) -> tuple[np.ndarray, float]:
        return FRAME, self.t


# zestaw prowadzi aplikację przez pętlę ciała, obsługę panelu i nadawcę dokładnie tak, jak w działającym programie
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

    # początek nowej wypowiedzi zgłasza potok audio, tak jak robi to lokalny vad
    def boundary(self) -> None:
        self.app.pipeline.on_utterance_start(self.t)

    # prośba modelu o spojrzenie trafia do pętli ciała jak wywołanie funkcji z backendu
    def request(self, call_id: str = "c") -> None:
        self.app._on_event(IntentRequest(call_id, "look_at_scene", {}))

    # krok czasu wykonuje pętlę ciała i obsługę panelu, a opcjonalnie także nadawcę kolejki
    def tick(self, n: int = 1, dt: float = 0.1, flush: bool = True) -> None:
        for _ in range(n):
            self.t += dt
            self.app.camera = None if self.frame_age is None else FakeCamera(self.t - self.frame_age)
            self.app.body.step(self.t)
            self.app._housekeeping(self.app.body.snapshot(), FRAME, self.t)
            if flush:
                self.sink.flush()


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


# twierdzące prośby w trybie rozkazującym lub pytającym są zgodą, a przeczenia, oznajmienia i cytaty nie
@pytest.mark.parametrize("text,expected", [(t, True) for t in ACCEPTED] + [(t, False) for t in REJECTED])
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
    assert rig.sink.frames == 0 and rig.sink.sent == ["odpowiedź:odrzucono"]
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
    assert rig.sink.frames == 1 and rig.sink.sent[-1] == "odpowiedź:odrzucono"


# transkrypcja przychodzi bez gwarancji kolejności, więc prośba modelu krótko czeka na rozpoznaną wypowiedź
def test_transcript_arriving_after_tool_call_is_awaited(settings):
    rig = LookRig(settings)
    rig.request()
    rig.tick(2)
    assert rig.sink.sent == []
    rig.say("spójrz na to")
    rig.tick()
    assert rig.sink.sent == ["klatka", "odpowiedź:ok"]


# kolejne wypowiedzi bez odpowiedzi robota pomiędzy nimi są osobnymi prośbami, bo granice wyznacza lokalny vad
def test_consecutive_utterances_each_allow_one_frame(settings):
    rig = LookRig(settings)
    rig.say("co widzisz?")
    rig.request("c1")
    rig.tick()
    rig.boundary()
    rig.say("a teraz spójrz tutaj")
    rig.request("c2")
    rig.tick()
    assert rig.sink.frames == 2 and rig.sink.sent.count("odpowiedź:ok") == 2


# zużyta prośba nie przechodzi na następną wypowiedź, więc stare „spójrz” nie odblokuje kolejnej klatki
def test_consent_is_not_reused_by_a_later_utterance(settings):
    rig = LookRig(settings)
    rig.say("spójrz")
    rig.request("c1")
    rig.tick()
    rig.boundary()
    rig.say("opowiedz mi o pogodzie")
    rig.request("c2")
    rig.tick(PAST_GRACE)
    assert rig.sink.frames == 1 and rig.sink.sent[-1] == "odpowiedź:odrzucono"


# późniejsze „nie patrz” w nowej wypowiedzi cofa wcześniejszą prośbę, zanim model zdąży o obraz poprosić
def test_later_refusal_revokes_earlier_request(settings):
    rig = LookRig(settings)
    rig.say("spójrz na to")
    rig.boundary()
    rig.say("nie, nie patrz")
    rig.request()
    rig.tick(PAST_GRACE)
    assert rig.sink.frames == 0 and rig.sink.sent == ["odpowiedź:odrzucono"]


# anulowanie przez serwer albo rozłączenie usuwa oczekującą prośbę, więc późniejsza wypowiedź niczego nie wysyła
@pytest.mark.parametrize("event", [IntentCancelled(("c",)), StatusChanged(ApiStatus.OFFLINE, "test")])
def test_cancelled_or_disconnected_look_sends_nothing(settings, event):
    rig = LookRig(settings)
    rig.request("c")
    rig.tick()
    rig.app._on_event(event)
    rig.say("co widzisz?")
    rig.tick(PAST_GRACE)
    assert rig.sink.frames == 0 and rig.sink.sent == []


# anulowanie po decyzji, ale przed wysłaniem, odwołuje klatkę i odpowiedź, a po ujawnieniu niczego już nie zmienia
@pytest.mark.parametrize("event", [IntentCancelled(("c",)), StatusChanged(ApiStatus.OFFLINE, "test")])
def test_cancel_after_decision_revokes_queued_frame(settings, event):
    rig = LookRig(settings)
    rig.say("co widzisz?")
    rig.request("c")
    rig.tick(flush=False)
    assert [label for label, _ in rig.sink.queue] == ["klatka", "odpowiedź:ok"]
    rig.app._on_event(event)
    rig.sink.flush()
    assert rig.sink.frames == 0 and rig.sink.sent == []
    sent = LookRig(settings)
    sent.say("co widzisz?")
    sent.request("c")
    sent.tick()
    sent.app._on_event(event)
    assert sent.sink.frames == 1 and sent.sink.sent == ["klatka", "odpowiedź:ok"]


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
    assert stale.sink.frames == 0


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
    rig.sink.flush()
    assert rig.sink.frames == 0 and rig.sink.sent == ["odpowiedź:odrzucono"]


# numer wypowiedzi pochodzi z granic vad, a tekst wyświetlany na pasku zaczyna się od nowa z każdą wypowiedzią
def test_user_turn_follows_vad_utterances_and_resets_text(settings):
    audio = LatestValue(AudioStatus(utterance=1))
    body = create_body(settings, PlaybackBuffer(), audio=audio)
    body.step(0.0)
    body.post(Transcript("user", "spójrz "))
    body.post(Transcript("user", "na to"))
    body.step(0.01)
    assert body.state.user_turn == 1 and body.state.last_user_text == "spójrz na to"
    audio.set(AudioStatus(utterance=2))
    body.step(0.02)
    body.post(Transcript("user", "hej"))
    body.step(0.03)
    assert body.state.user_turn == 2 and body.state.last_user_text == "hej"
