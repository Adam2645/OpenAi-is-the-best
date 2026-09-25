from __future__ import annotations

import numpy as np

from so101_expressive.app import RobotApp
from so101_expressive.conversation.gemini_live import GeminiLiveBackend
from so101_expressive.inputs.camera import VisionUplink
from so101_expressive.inputs.virtual import VirtualAudioRig
from so101_expressive.state import ApiStatus, PersonStatus

from .test_scenarios import BabbleTTS


# atrapa połączonego backendu zapisuje wysłane klatki, żeby sprawdzić, kiedy obraz opuszcza laptopa
class FrameSink:
    status = ApiStatus.CONNECTED

    # lista klatek jest pusta, dopóki uplink niczego nie wyśle
    def __init__(self) -> None:
        self.frames: list[bytes] = []

    # wywoływana przez uplink przy każdym wysłaniu klatki jpeg
    def send_image(self, jpeg: bytes) -> None:
        self.frames.append(jpeg)


# mowa z osi czasu dema działa także z backendem gemini, który nie ma metody say, więc demo nie przerywa się wyjątkiem
def test_virtual_timeline_speech_works_with_gemini_backend(settings):
    app = RobotApp(settings, virtual=True, backend="gemini", window=False)
    assert isinstance(app.backend, GeminiLiveBackend)
    rig = VirtualAudioRig(app.playback, app.pipeline)
    _, events = app._demo_timeline(BabbleTTS(), rig)
    speak = next(action for _, label, action in events if label == "mowa podczas trzymania")
    speak(43.0)
    assert app.playback.has_pending()


# domyślnie obraz trafia do chmury tylko na prośbę modelu, a cykliczne wysyłanie trzeba świadomie włączyć
def test_camera_frames_leave_laptop_only_on_request_by_default(settings):
    assert settings.vision_uplink_interval_s == 0.0
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    sink = FrameSink()
    uplink = VisionUplink(settings.vision_uplink_interval_s)
    assert not any(uplink.maybe_send(sink, frame, float(k), PersonStatus.TRACKED) for k in range(100))
    uplink.request()
    assert uplink.maybe_send(sink, frame, 100.0, PersonStatus.ABSENT)
    assert not uplink.maybe_send(sink, frame, 101.0, PersonStatus.TRACKED)
    assert len(sink.frames) == 1
    periodic = VisionUplink(12.0)
    assert sum(periodic.maybe_send(sink, frame, float(k), PersonStatus.TRACKED) for k in range(30)) == 3
