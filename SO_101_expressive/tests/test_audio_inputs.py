from __future__ import annotations

import numpy as np

from so101_expressive.config import Settings
from so101_expressive.conversation.base import ConversationBackend
from so101_expressive.inputs.audio_pipeline import AudioPipeline
from so101_expressive.inputs.echo import EchoGate
from so101_expressive.inputs.music import MusicDetector
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.inputs.vad import EnergyVad
from so101_expressive.inputs.virtual import VirtualAudioRig, clip_source
from so101_expressive.state import ApiStatus
from so101_expressive.util import LatestValue

from .conftest import synthetic_speech

R = 16000


# backend nagrywający pokazuje dokładnie, co potok mikrofonu wysłałby do chmury
class RecordingBackend(ConversationBackend):
    # status połączony sprawia, że potok traktuje backend jako gotowy
    def __init__(self) -> None:
        super().__init__(lambda e: None)
        self._status = ApiStatus.CONNECTED
        self.audio: list[bytes] = []
        self.ends = 0

    # start nie jest potrzebny w testach potoku
    def start(self) -> None:
        return None

    # stop nie jest potrzebny w testach potoku
    def stop(self) -> None:
        return None

    # wysłane audio jest zapisywane do asercji
    def send_audio(self, pcm16: bytes, rate: int) -> None:
        self.audio.append(pcm16)

    # liczba końców strumienia pokazuje działanie hybrydowego vad
    def end_audio(self) -> None:
        self.ends += 1

    # obraz nie jest używany w tych testach
    def send_image(self, jpeg: bytes, allow=None) -> None:
        return None

    # kontekst nie jest używany w tych testach
    def send_context(self, text: str) -> None:
        return None

    # odpowiedzi funkcji nie są używane w tych testach
    def respond_intent(self, call_id: str, name: str, result: dict, allow=None) -> None:
        return None

    # sekundy wysłanego dźwięku ułatwiają porównania
    def seconds(self) -> float:
        return sum(len(a) for a in self.audio) / 2.0 / R


# syntetyczna muzyka z perkusją i akordami, tą samą co w ewaluacji detektora
def synth_music(sec: float = 14.0, bpm: float = 118.0) -> np.ndarray:
    rng = np.random.default_rng(0)
    t = np.arange(int(sec * R)) / R
    beat = 60.0 / bpm
    y = np.zeros_like(t)
    for k in range(int(sec / beat)):
        s = int(k * beat * R)
        n = int(0.25 * R)
        tt = np.arange(n) / R
        if s + n < y.size:
            y[s : s + n] += 0.8 * np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 12)
            if k % 2:
                y[s : s + n] += 0.3 * rng.standard_normal(n) * np.exp(-tt * 30)
    for k in range(int(sec / (4 * beat))):
        s, e = int(k * 4 * beat * R), min(y.size, int((k + 1) * 4 * beat * R))
        tt = np.arange(e - s) / R
        for f in ((220, 277, 330), (196, 247, 294), (175, 220, 262), (196, 247, 294))[k % 4]:
            y[s:e] += 0.15 * np.sin(2 * np.pi * f * tt)
    return (y / np.max(np.abs(y)) * 0.3 * 32767).astype(np.int16)


# mowa syntetyczna przeliczona na 16 khz dla wejścia mikrofonu
def speech16(sec: float, seed: int = 1) -> np.ndarray:
    x = synthetic_speech(sec, rate=24000, seed=seed).astype(np.float32)
    idx = np.arange(int(x.size * R / 24000)) * (24000 / R)
    return np.interp(idx, np.arange(x.size), x).astype(np.int16)


# potok z wirtualnym zestawem audio i backendem nagrywającym
def rig(tmp_path, **env):
    settings = Settings.from_env({"LEDGER_PATH": str(tmp_path / "l.json"), **{k.upper(): str(v) for k, v in env.items()}})
    playback = PlaybackBuffer()
    status = LatestValue()
    backend = RecordingBackend()
    pipeline = AudioPipeline(settings, playback, status, backend)
    return VirtualAudioRig(playback, pipeline), playback, pipeline, backend, status


# przesuwa wirtualny czas o zadany odcinek krokami pętli sterowania
def advance(r, t, seconds, dt=0.01):
    for _ in range(int(round(seconds / dt))):
        r.tick(t, dt)
        t += dt
    return t


# vad wykrywa początek mowy po krótkiej zwłoce i koniec dopiero po co najmniej pół sekundy ciszy
def test_vad_start_and_hangover():
    vad = EnergyVad(R)
    silence = np.zeros(512, dtype=np.int16)
    loud = (np.sin(np.arange(512) * 0.2) * 8000).astype(np.int16)
    for _ in range(20):
        assert not vad.process(silence).speech
    starts = [vad.process(loud).started for _ in range(5)]
    assert any(starts) and not starts[0]
    quiet = [vad.process(silence) for _ in range(30)]
    ended_at = next(i for i, d in enumerate(quiet) if d.ended)
    assert ended_at * 512 / R >= 0.5


# samo echo robota nie otwiera bramki, a wyraźnie głośniejszy głos użytkownika otwiera ją jako przerwanie
def test_echo_gate_blocks_echo_and_detects_barge_in():
    gate = EchoGate("half_duplex", barge_in_ratio=3.0, barge_in_min_ms=120)
    for _ in range(60):
        assert not gate.process(mic_rms=0.03, ref_peak=0.1, dt=0.032, noise_floor=0.002).pass_audio
    opened = [gate.process(mic_rms=0.3, ref_peak=0.1, dt=0.032, noise_floor=0.002) for _ in range(6)]
    first = next(i for i, d in enumerate(opened) if d.barge_in)
    assert 0.1 <= (first + 1) * 0.032 <= 0.2
    assert EchoGate("off").process(0.03, 0.1, 0.032, 0.002).pass_audio


# gdy robot mówi przez głośnik, do chmury nie trafia nic, a mowa użytkownika po ciszy trafia z buforem wstępnym
def test_pipeline_sends_user_speech_but_not_robot_echo(tmp_path):
    r, playback, pipeline, backend, status = rig(tmp_path)
    starts: list[float] = []
    pipeline.on_utterance_start = starts.append
    t = advance(r, 0.0, 1.0)
    playback.enqueue(synthetic_speech(3.0))
    t = advance(r, t, 3.5)
    assert backend.seconds() == 0.0 and status.get().user_speaking is False
    assert pipeline.last_vad_speech_t < 0 and pipeline.utterances == 0 and starts == []
    t_user = t + 0.2
    r.add_source(clip_source(speech16(2.0), R, t_start=t_user, gain=1.0))
    t = advance(r, t, 3.5)
    assert 1.8 <= backend.seconds() <= 3.2
    assert backend.ends == 1
    assert t_user < pipeline.last_vad_speech_t <= t
    assert pipeline.utterances == 1 and status.get().utterance == 1 and t_user <= starts[0] <= t_user + 0.5


# każda wypowiedź oddzielona ciszą jest osobną granicą, którą liczy lokalny vad, a nie kolejność transkrypcji
def test_pipeline_counts_separate_utterances(tmp_path):
    r, playback, pipeline, backend, status = rig(tmp_path)
    t = advance(r, 0.0, 1.0)
    r.add_source(clip_source(speech16(1.2, seed=2), R, t_start=t, gain=1.0))
    r.add_source(clip_source(speech16(1.2, seed=3), R, t_start=t + 3.0, gain=1.0))
    advance(r, t, 5.5)
    assert pipeline.utterances == 2 and status.get().utterance == 2 and backend.ends == 2


# głośne wejście w słowo podczas mowy robota zostaje wykryte i przepuszczone do serwera
def test_pipeline_barge_in_while_robot_speaks(tmp_path):
    r, playback, pipeline, backend, status = rig(tmp_path)
    t = advance(r, 0.0, 0.5)
    playback.enqueue(synthetic_speech(4.0))
    t = advance(r, t, 1.5)
    r.add_source(clip_source(speech16(1.5, seed=5), R, t_start=t, gain=2.5))
    t = advance(r, t, 1.0)
    assert pipeline.barge_ins >= 1 and backend.seconds() > 0.3


# muzyka w pokoju jest wykrywana, a własna mowa robota z głośnika nie jest mylona z muzyką
def test_music_detected_but_not_robot_speech(tmp_path):
    r, playback, pipeline, backend, status = rig(tmp_path)
    t = 0.0
    for _ in range(3):
        playback.enqueue(synthetic_speech(4.0))
        t = advance(r, t, 4.3)
    assert status.get().music is False
    r.add_source(clip_source(synth_music(14.0), R, t_start=t, gain=1.0))
    t = advance(r, t, 12.0)
    assert status.get().music is True and status.get().music_bpm > 0


# ramki oznaczone jako własny dźwięk robota nie są oceniane, nawet gdy zawierają muzykę
def test_music_detector_ignores_own_playback_frames():
    det = MusicDetector(R)
    music = synth_music(12.0)
    for i in range(0, music.size - 512, 512):
        det.update(music[i : i + 512], own_playback=True)
    assert det.music is False
