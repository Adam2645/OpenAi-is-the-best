from __future__ import annotations

import json
import shutil
import subprocess
import wave

import numpy as np
import pytest

from so101_expressive import app as app_module
from so101_expressive.app import finalize_recording
from so101_expressive.inputs.playback import PlaybackBuffer
from so101_expressive.inputs.virtual import VirtualAudioRig, clip_source


# odczyt pliku wav do tablicy ułatwia sprawdzanie położenia dźwięków w czasie
def read_wav(path):
    with wave.open(str(path)) as wf:
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
        return wf.getframerate(), data


# ścieżka dema zawiera mowę robota przesuniętą o opóźnienie głośnika oraz dźwięki pokoju dokładnie w ich czasie
def test_soundtrack_is_aligned_with_simulation_time(tmp_path):
    playback = PlaybackBuffer()
    rig = VirtualAudioRig(playback, None, latency=0.02)
    rig.enable_soundtrack()
    tone = (np.sin(2 * np.pi * 440 * np.arange(24000) / 24000) * 0.5 * 32767).astype(np.int16)
    room = np.zeros(16000 * 3, dtype=np.int16)
    room[32000:40000] = 12000
    rig.add_source(clip_source(room, 16000, t_start=0.0))
    playback.enqueue(tone)
    t = 0.0
    for _ in range(300):
        rig.tick(t, 0.01)
        t += 0.01
    duration = rig.save_soundtrack(tmp_path / "demo.wav")
    rate, data = read_wav(tmp_path / "demo.wav")
    assert rate == 24000 and abs(duration - 3.0) < 0.01
    loud = np.flatnonzero(np.abs(data) > 0.1)
    assert abs(loud[0] / rate - 0.02) < 0.002
    later = loud[loud > int(1.5 * rate)]
    assert abs(later[0] / rate - 2.0) < 0.002
    assert np.all(np.abs(data[int(1.1 * rate) : int(1.9 * rate)]) < 0.01)


# bez włączonego nagrywania ścieżki nic nie jest zapisywane, więc zwykły tryb wirtualny nie tworzy plików
def test_soundtrack_disabled_writes_nothing(tmp_path):
    rig = VirtualAudioRig(PlaybackBuffer(), None)
    rig.tick(0.0, 0.01)
    assert rig.save_soundtrack(tmp_path / "x.wav") == 0.0
    assert not (tmp_path / "x.wav").exists()


# bez ffmpeg surowe nagranie opencv zostaje zachowane pod docelową nazwą zamiast przepaść
def test_finalize_without_ffmpeg_keeps_raw(tmp_path, monkeypatch):
    raw = tmp_path / "demo.raw.mp4"
    raw.write_bytes(b"surowe")
    monkeypatch.setattr(app_module.shutil, "which", lambda name: None)
    info = finalize_recording(raw, tmp_path / "demo.mp4", None)
    assert (tmp_path / "demo.mp4").read_bytes() == b"surowe" and not raw.exists()
    assert "mp4v" in info


# z ffmpeg powstaje plik h.264 z dźwiękiem aac, który odtwarzają przeglądarki i komunikatory
@pytest.mark.skipif(shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None, reason="brak ffmpeg")
def test_finalize_with_ffmpeg_produces_h264_and_aac(tmp_path):
    import cv2

    raw = tmp_path / "demo.raw.mp4"
    writer = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), 25, (64, 48))
    for i in range(25):
        writer.write(np.full((48, 64, 3), i * 10, dtype=np.uint8))
    writer.release()
    wav = tmp_path / "demo.wav"
    with wave.open(str(wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes((np.sin(np.arange(24000) * 0.1) * 8000).astype("<i2").tobytes())
    info = finalize_recording(raw, tmp_path / "demo.mp4", wav)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(tmp_path / "demo.mp4")],
        capture_output=True, text=True, check=True,
    )
    streams = {s["codec_type"]: s for s in json.loads(probe.stdout)["streams"]}
    assert streams["video"]["codec_name"] == "h264" and streams["video"]["pix_fmt"] == "yuv420p"
    assert streams["audio"]["codec_name"] == "aac"
    assert not raw.exists() and "h.264" in info
