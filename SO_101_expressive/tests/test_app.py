from __future__ import annotations

import numpy as np

from so101_expressive.app import RobotApp
from so101_expressive.config import Settings
from so101_expressive.conversation.base import IntentRequest
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.inputs.camera import VisionUplink
from so101_expressive.inputs.virtual import VirtualAudioRig
from so101_expressive.state import ApiStatus, PersonStatus, RobotState

from .test_scenarios import BabbleTTS

FRAME = np.zeros((480, 640, 3), dtype=np.uint8)


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


# aplikacja w trybie wirtualnym z podmienionym backendem pozwala badać ścieżkę wysyłania obrazu bez sieci
def looking_app(settings) -> tuple[RobotApp, RecordingBackend]:
    app = RobotApp(settings, virtual=True, backend="gemini", window=False)
    sink = RecordingBackend()
    app.backend = sink
    return app, sink


# prośba modelu o spojrzenie w chwili t, taka sama jak z backendu rozmowy
def look(app: RobotApp, t: float):
    return app._look(IntentRequest("c", "look_at_scene", {}), RobotState(t=t))


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


# prośba modelu wysyła klatkę tylko tuż po lokalnie usłyszanej wypowiedzi i tylko gdy obraz jest świeży
def test_look_requires_recent_user_speech_and_fresh_frame(settings):
    app, sink = looking_app(settings)
    app.camera = FakeCamera(99.8)
    assert not look(app, 100.0).accepted
    app.pipeline.last_user_speech_t = 75.0
    assert not look(app, 100.0).accepted
    app.pipeline.last_user_speech_t = 97.0
    app.camera = FakeCamera(95.0)
    assert not look(app, 100.0).accepted
    app.camera = None
    assert not look(app, 100.0).accepted
    assert sink.frames == []
    app.camera = FakeCamera(99.8)
    result = look(app, 100.0)
    assert result.accepted and len(sink.frames) == 1 and app.uplink.sent == 1


# odmowa nie zostawia oczekującego żądania, więc późniejsza klatka nie zostanie wysłana bez nowej prośby
def test_refused_look_leaves_no_pending_upload(settings):
    app, sink = looking_app(settings)
    app.pipeline.last_user_speech_t = 99.0
    assert not look(app, 100.0).accepted
    for k in range(50):
        app._housekeeping(RobotState(t=100.0 + k, person=PersonStatus.TRACKED), FRAME, 100.0 + k)
    assert sink.frames == []


# klatka trafia do modelu przed odpowiedzią funkcji, więc model nie opisuje sceny, zanim ją zobaczy
def test_frame_is_sent_before_tool_response(settings):
    app, sink = looking_app(settings)
    app.pipeline.last_user_speech_t = 0.5
    app.camera = FakeCamera(0.9)
    app.body.post(IntentRequest("c1", "look_at_scene", {}))
    app.body.step(1.0)
    assert sink.sent == ["klatka", "odpowiedź:ok"]


# przełącznik camera_cloud=off blokuje zarówno prośby modelu, jak i ustawioną wysyłkę cykliczną
def test_camera_cloud_off_blocks_all_uploads(tmp_path):
    settings = Settings.from_env({
        "LEDGER_PATH": str(tmp_path / "l.json"), "LOG_DIR": str(tmp_path / "logs"),
        "CAMERA_CLOUD": "off", "VISION_UPLINK_INTERVAL_S": "5",
    })
    app, sink = looking_app(settings)
    app.pipeline.last_user_speech_t = 99.0
    app.camera = FakeCamera(99.9)
    assert not look(app, 100.0).accepted
    for k in range(30):
        app._housekeeping(RobotState(t=100.0 + k, person=PersonStatus.TRACKED), FRAME, 100.0 + k)
    assert sink.frames == []
