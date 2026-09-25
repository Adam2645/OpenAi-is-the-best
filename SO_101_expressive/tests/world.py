from __future__ import annotations

import numpy as np

from so101_expressive.conversation.base import AudioChunk, Interrupted
from so101_expressive.inputs.audio_pipeline import AudioPipeline
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.inputs.virtual import VirtualAudioRig
from so101_expressive.runtime import AudioStatus, create_body
from so101_expressive.util import LatestValue


# świat testowy składa ciało, wirtualny głośnik z mikrofonem, potok audio i opcjonalny backend jak w aplikacji
class World:
    # fabryka backendu dostaje funkcję zwrotną świata, dzięki czemu zdarzenia płyną tą samą drogą co w aplikacji
    def __init__(self, settings, backend_factory=None, person=None, echo_gain: float = 0.3) -> None:
        self.playback = PlaybackBuffer()
        self.person_value: LatestValue = LatestValue()
        self.audio: LatestValue = LatestValue(AudioStatus())
        self.backend = backend_factory(self.sink) if backend_factory else None
        self.body = create_body(settings, self.playback, self.person_value, self.audio, intent_responder=self._respond)
        self.pipeline = AudioPipeline(settings, self.playback, self.audio, self.backend)
        self.rig = VirtualAudioRig(self.playback, self.pipeline, echo_gain=echo_gain)
        self.person = person
        self.records: list = []
        self.t = 0.0

    # ta sama logika co w aplikacji: dźwięk do bufora, przerwanie opróżnia bufor, reszta do pętli ciała
    def sink(self, event) -> None:
        if isinstance(event, AudioChunk):
            self.playback.enqueue(np.frombuffer(event.pcm, dtype="<i2"))
            return
        if isinstance(event, Interrupted):
            self.playback.flush()
        self.body.post(event)

    # wynik planisty wraca do backendu jak odpowiedź funkcji
    def _respond(self, intent, result) -> None:
        if self.backend is not None:
            self.backend.respond_intent(intent.call_id, intent.name, result.as_response())

    # przesunięcie świata o zadany czas zwraca zapisy kroków z tego odcinka
    def run(self, seconds: float, on_step=None) -> list:
        out = []
        dt = self.body.dt
        for _ in range(int(round(seconds / dt))):
            if on_step is not None:
                on_step(self.t)
            if self.person is not None:
                self.person_value.set(self.person.observe(self.t))
            self.rig.tick(self.t, dt)
            rec = self.body.step(self.t)
            out.append(rec)
            self.t += dt
        self.records.extend(out)
        return out

    # czekanie na warunek stanu z limitem czasu symulacji
    def run_until(self, predicate, timeout: float) -> list:
        out = []
        end = self.t + timeout
        while self.t < end:
            out.extend(self.run(0.1))
            if predicate(self.body.state):
                return out
        raise AssertionError(f"warunek nie spełniony w {timeout} s: {self.body.state.summary_pl()}")


# sprawdza, że żaden krok nie złamał limitów pozycji, prędkości i przyspieszenia bezpiecznego sterownika
def assert_motion_limits(body, records, estop_factor: float = 2.0) -> None:
    ctrl = body.controller
    prev_v = None
    for rec in records:
        assert np.all(rec.q_cmd >= ctrl.lo - 1e-9) and np.all(rec.q_cmd <= ctrl.hi + 1e-9)
        assert np.all(np.abs(rec.v_cmd) <= ctrl.vmax + 1e-9)
        if prev_v is not None:
            factor = estop_factor if rec.state.estop else 1.0
            assert np.all(np.abs(rec.v_cmd - prev_v) <= ctrl.amax * factor * body.dt + 1e-9)
        prev_v = rec.v_cmd
