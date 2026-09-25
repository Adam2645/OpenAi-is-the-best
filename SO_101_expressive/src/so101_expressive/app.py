from __future__ import annotations

import dataclasses
import json
import logging
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

from .behavior.planner import IntentResult
from .budget import CostMeter
from .config import Settings
from .conversation.base import AudioChunk, ConversationBackend, IntentRequest, Interrupted
from .conversation.gemini_live import GeminiLiveBackend
from .conversation.scripted import LocalTTS, ScriptedBackend, speech_events
from .inputs.audio_pipeline import AudioPipeline
from .inputs.camera import VisionUplink, synthetic_frame
from .inputs.face import ScriptedPerson
from .inputs.playback import PlaybackBuffer
from .inputs.virtual import VirtualAudioRig, clip_source
from .runtime import AudioStatus, Command, create_body
from .ui import PANEL_H
from .state import ApiStatus, GripPhase, PersonStatus, RobotState, StateJournal
from .util import LatestValue

log = logging.getLogger("so101")
GESTURE_CYCLE = ("nod", "wave", "shrug", "think", "happy", "curious", "shake_head", "surprised", "bow", "look_around")


# przeglądarki i komunikatory nie odtwarzają kodeka mp4v z opencv, więc przy dostępnym ffmpeg nagranie jest kodowane do h.264
def finalize_recording(raw: Path, final: Path, audio: Path | None) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        os.replace(raw, final)
        return "zapisano kodekiem mp4v bez dźwięku - dla wersji h.264 z dźwiękiem zainstaluj ffmpeg (brew install ffmpeg)"
    with_audio = audio is not None and Path(audio).exists()
    cmd = [ffmpeg, "-loglevel", "error", "-y", "-i", str(raw)]
    if with_audio:
        cmd += ["-i", str(audio)]
    cmd += ["-map", "0:v:0", "-c:v", "libx264", "-profile:v", "main", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-crf", "24", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-movflags", "+faststart"]
    if with_audio:
        cmd += ["-map", "1:a:0", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "-shortest"]
    cmd.append(str(final))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        os.replace(raw, final)
        return f"ffmpeg zwrócił błąd, zostawiono mp4v: {result.stderr.strip()[:200]}"
    raw.unlink(missing_ok=True)
    return "zapisano jako h.264" + (" z dźwiękiem aac" if with_audio else " bez dźwięku")


# krótkie wpisy z czujników informują model o zmianach stanu ciała bez kosztownego strumienia danych
class SensorNarrator:
    # poprzedni stan pozwala zgłaszać tylko przejścia, a nie każdą klatkę
    def __init__(self) -> None:
        self._prev: RobotState | None = None

    # lista komunikatów dla modelu po polsku, z prefiksem odróżniającym je od słów rozmówcy
    def update(self, state: RobotState) -> list[str]:
        prev, self._prev = self._prev, state
        if prev is None:
            return []
        out = []
        if state.music and not prev.music:
            out.append("[czujnik] W otoczeniu słychać muzykę.")
        if prev.music and not state.music:
            out.append("[czujnik] Muzyka ucichła.")
        if state.grip is GripPhase.HOLDING and prev.grip is not GripPhase.HOLDING:
            out.append("[czujnik] Trzymasz teraz kostkę - potwierdzone przez czujniki chwytaka.")
        if prev.grip is GripPhase.HOLDING and state.grip is not GripPhase.HOLDING:
            out.append(f"[czujnik] Chwytak nie trzyma już kostki ({state.grip.value}).")
        if state.estop and not prev.estop:
            out.append("[czujnik] Włączono awaryjny stop - Twoje ramię się nie rusza.")
        if prev.estop and not state.estop:
            out.append("[czujnik] Awaryjny stop zwolniony.")
        return out


# dziennik przejść stanu trafia do pliku jsonl, żeby po sesji dało się odtworzyć zachowanie robota
class StateLogWriter:
    # plik powstaje w katalogu logów z datą w nazwie
    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / time.strftime("state-%Y%m%d-%H%M%S.jsonl")
        self._written = 0

    # postęp liczony monotonicznym licznikiem zmian nie zatrzymuje zapisu po zapełnieniu dziennika i odnotowuje utracone wpisy
    def write(self, journal: StateJournal) -> None:
        new, total, dropped = journal.since(self._written)
        if not new and not dropped:
            return
        with self.path.open("a", encoding="utf-8") as fh:
            if dropped:
                first_t = round(new[0][0], 3) if new else None
                fh.write(json.dumps({"t": first_t, "pole": "pominięte wpisy", "z": "", "na": str(dropped)}, ensure_ascii=False) + "\n")
            for t, name, old, value in new:
                fh.write(json.dumps({"t": round(t, 3), "pole": name, "z": str(old), "na": str(value)}, ensure_ascii=False) + "\n")
        self._written = total


# aplikacja łączy wszystkie warstwy i prowadzi pętlę interfejsu w głównym wątku, czego wymaga macos
class RobotApp:
    # tryb wirtualny zastępuje kamerę, mikrofon i głośnik, zachowując całą resztę systemu bez zmian
    def __init__(
        self,
        settings: Settings,
        *,
        virtual: bool = False,
        backend: str = "auto",
        window: bool = True,
        record: Path | None = None,
        duration: float | None = None,
        use_camera: bool = True,
        use_audio: bool = True,
        music_file: Path | None = None,
    ) -> None:
        self.settings = settings
        self.virtual = virtual
        self.window = window
        self.record = record
        self.duration = duration
        self.use_camera = use_camera and not virtual
        self.use_audio = use_audio and not virtual
        self.music_file = music_file
        self.playback = PlaybackBuffer()
        self.person: LatestValue = LatestValue()
        self.audio: LatestValue = LatestValue(AudioStatus())
        self.meter = CostMeter.from_settings(settings)
        self.backend = self._make_backend(backend)
        self.body = create_body(
            settings, self.playback, self.person, self.audio, budget_fn=self.meter.snapshot,
            intent_responder=self._respond, special_intents={"look_at_scene": self._look},
        )
        self.pipeline = AudioPipeline(settings, self.playback, self.audio, self.backend)
        self.uplink = VisionUplink(settings.vision_uplink_interval_s, settings.vision_uplink_width)
        self.narrator = SensorNarrator()
        self.state_log = StateLogWriter(settings.resolve_path(settings.log_dir))
        self.message = ""
        self._gesture_i = 0
        self._stop = threading.Event()
        self._raw_record: Path | None = None
        self.recording_info = ""

    # wybór backendu: gemini przy kluczu, lokalny skrypt bez klucza albo brak rozmowy
    def _make_backend(self, kind: str) -> ConversationBackend | None:
        if kind == "none":
            return None
        if kind == "gemini" or (kind == "auto" and self.settings.gemini_api_key and not self.virtual):
            usage_log = self.settings.resolve_path(self.settings.log_dir) / "gemini_usage.jsonl"
            return GeminiLiveBackend(self.settings, self.meter, self._on_event, usage_log=usage_log)
        return ScriptedBackend(
            self._on_event, LocalTTS(self.settings.offline_tts_voice), threaded=not self.virtual,
            should_reply=self._not_music,
        )

    # lokalny skrypt nie rozumie mowy, więc przy wykrytej muzyce nie odpowiada na dźwięk z pokoju
    def _not_music(self) -> bool:
        status = self.audio.get()
        return not (status is not None and (status.music or status.music_score > 0.5))

    # zdarzenia rozmowy: dźwięk idzie prosto do bufora, reszta do kolejki pętli ciała
    def _on_event(self, event) -> None:
        if isinstance(event, AudioChunk):
            pcm = np.frombuffer(event.pcm, dtype="<i2")
            if event.rate != self.playback.rate and pcm.size:
                idx = np.arange(int(pcm.size * self.playback.rate / event.rate)) * (event.rate / self.playback.rate)
                pcm = np.interp(idx, np.arange(pcm.size), pcm).astype(np.int16)
            self.playback.enqueue(pcm)
            return
        if isinstance(event, Interrupted):
            self.playback.flush()
        self.body.post(event)

    # wynik planisty wraca do modelu jako odpowiedź funkcji
    def _respond(self, intent: IntentRequest, result: IntentResult) -> None:
        if self.backend is not None:
            self.backend.respond_intent(intent.call_id, intent.name, result.as_response())
        self.message = f"{intent.name}: {result.message}"

    # prośba modelu o spojrzenie wysyła najbliższą klatkę z kamery do chmury
    def _look(self, intent: IntentRequest, state: RobotState) -> IntentResult:
        if self.backend is None or self.backend.status is not ApiStatus.CONNECTED:
            return IntentResult(False, "brak połączenia z chmurą - nie mogę pokazać obrazu")
        self.uplink.request()
        return IntentResult(True, "wysłałem aktualną klatkę z kamery")

    # dodatkowe pola panelu pochodzą z potoku audio i ostatniej decyzji arbitra
    def _extra(self) -> dict:
        rec = self.body.last_record
        stats = self.pipeline.stats
        return {
            "mic_rms": stats.mic_rms,
            "gate_open": stats.gate_open,
            "arm_owner": rec.decision.arm_owner if rec else "-",
            "gripper_owner": rec.decision.gripper_owner if rec else "-",
            "message": self.message,
        }

    # obsługa klawiszy zamienia je na polecenia, które przechodzą przez te same reguły co prośby modelu
    def handle_key(self, key: int) -> bool:
        if key in (ord("q"), 27):
            return False
        if key in (ord(" "), ord("e")):
            self.body.post(Command("estop", {"reason": "klawisz"}))
        elif key == ord("r"):
            self.body.post(Command("reset"))
        elif key == ord("i"):
            self.playback.flush()
            if hasattr(self.backend, "interrupt_local"):
                self.backend.interrupt_local()
            self.body.post(Interrupted())
        elif key == ord("p"):
            self.body.post(Command("pick"))
        elif key == ord("o"):
            self.body.post(Command("place"))
        elif key == ord("c"):
            self.body.post(Command("reset_cube"))
        elif key == ord("t"):
            self.body.post(Command("dance", {"duration": "short"}))
        elif key == ord("g"):
            self.body.post(Command("gesture", {"name": GESTURE_CYCLE[self._gesture_i % len(GESTURE_CYCLE)]}))
            self._gesture_i += 1
        elif key == ord("m"):
            flag = not self.body.settings.mute_speech_while_holding
            self.body.settings = dataclasses.replace(self.body.settings, mute_speech_while_holding=flag)
            self.message = f"milczenie przy trzymaniu: {'włączone' if flag else 'wyłączone'}"
        return True

    # zadania okresowe: klatki dla chmury, podtrzymanie sesji, komunikaty czujników i zapis dziennika
    def _housekeeping(self, state: RobotState, frame: np.ndarray | None, now: float) -> None:
        if self.backend is not None:
            self.uplink.maybe_send(self.backend, frame, now, state.person)
            if state.person is PersonStatus.TRACKED:
                if hasattr(self.backend, "note_activity"):
                    self.backend.note_activity()
                if self.backend.status is ApiStatus.IDLE:
                    self.backend.wake()
            for text in self.narrator.update(state):
                self.backend.send_context(text)
        self.state_log.write(self.body.journal)

    # zamknięcie w odwrotnej kolejności startu kończy połączenie przed zapisem wydatków i domknięciem nagrania
    def _shutdown(self, closers: list, audio: Path | None = None) -> None:
        self._stop.set()
        if self.backend is not None:
            self.backend.stop()
        self.meter.flush()
        for close in reversed(closers):
            try:
                close()
            except Exception as exc:
                log.warning("błąd przy zamykaniu: %s", exc)
        self.state_log.write(self.body.journal)
        if self.record is not None and self._raw_record is not None and self._raw_record.exists():
            self.recording_info = finalize_recording(self._raw_record, self.record, audio)
            log.info("nagranie %s: %s", self.record, self.recording_info)

    # tryb na żywo używa kamery, mikrofonu i głośników laptopa oraz pętli ciała w czasie rzeczywistym
    def run_live(self) -> None:
        from .inputs.audio_pipeline import MicInput
        from .inputs.camera import CameraSource, CameraUnavailable
        from .inputs.face import FaceDetector, FaceTracker, VisionLoop
        from .inputs.playback import SpeakerOutput
        from .ui import Dashboard

        closers: list = []
        camera = vision = None
        try:
            if self.use_camera:
                try:
                    camera = CameraSource(self.settings.camera_index, self.settings.camera_width, self.settings.camera_height)
                    camera.start()
                    closers.append(camera.close)
                    detector = FaceDetector(self.settings.resolve_path(self.settings.face_model_path))
                    tracker = FaceTracker(self.settings.face_score_acquire, self.settings.face_score_keep)
                    vision = VisionLoop(camera, detector, tracker, self.person)
                    vision.start()
                    closers.append(vision.close)
                except CameraUnavailable as exc:
                    self.message = str(exc)
                    log.error("%s", exc)
            if self.use_audio:
                speaker = SpeakerOutput(self.playback)
                speaker.start()
                closers.append(speaker.close)
                mic = MicInput(self.pipeline)
                mic.start()
                closers.append(mic.close)
            if self.backend is not None:
                self.backend.start()
            body_thread = threading.Thread(target=self.body.run, args=(self._stop,), name="body", daemon=True)
            body_thread.start()
            dashboard = Dashboard(self.body.sim, self.settings.render_width, self.settings.render_height, window=self.window,
                                  mode_label="kamera + mikrofon + głośniki")
            closers.append(dashboard.close)
            writer = self._writer(2 * self.settings.render_width, self.settings.render_height + PANEL_H, 30)
            if writer is not None:
                closers.append(writer.release)
            started = time.monotonic()
            while True:
                frame_start = time.monotonic()
                item = camera.latest() if camera is not None else None
                frame = item[0] if item is not None else None
                state = self.body.snapshot()
                self._housekeeping(state, frame, frame_start)
                img = dashboard.compose(frame, vision.faces if vision else [], state, self._extra(), self.settings.mirror_preview)
                if writer is not None:
                    writer.write(img)
                key = dashboard.show(img)
                if key not in (-1, 255) and not dashboard.handle_view_key(key) and not self.handle_key(key):
                    break
                if self.duration is not None and frame_start - started > self.duration:
                    break
                time.sleep(max(0.0, 1.0 / 30.0 - (time.monotonic() - frame_start)))
        finally:
            self._shutdown(closers)

    # surowe klatki trafiają do pliku tymczasowego, z którego po zakończeniu powstaje docelowe nagranie
    def _writer(self, width: int, height: int, fps: float):
        if self.record is None:
            return None
        import cv2

        self.record.parent.mkdir(parents=True, exist_ok=True)
        self._raw_record = self.record.with_name(self.record.stem + ".raw.mp4")
        return cv2.VideoWriter(str(self._raw_record), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    # oś czasu dema wirtualnego sprawdza po kolei rozmowę, śledzenie, muzykę, chwyt przy mowie i awaryjny stop
    def _demo_timeline(self, tts: LocalTTS, rig: VirtualAudioRig) -> tuple[ScriptedPerson, list]:
        person = ScriptedPerson([
            (2.0, 2.3, PersonStatus.ACQUIRING, -0.45, -0.1, 0.13, 0.9),
            (2.3, 9.0, PersonStatus.TRACKED, -0.45, -0.1, 0.13, 0.95),
            (9.0, 13.0, PersonStatus.TRACKED, lambda t: -0.45 + 0.9 * (t - 9.0) / 4.0, -0.1, 0.13, 0.95),
            (13.0, 14.5, PersonStatus.UNCERTAIN, 0.45, -0.1, 0.13, 0.4),
            (18.0, 18.3, PersonStatus.ACQUIRING, 0.1, -0.2, 0.15, 0.9),
            (18.3, 1e9, PersonStatus.TRACKED, 0.1, -0.2, 0.15, 0.95),
        ])
        user = tts.synth("Cześć robocie! Jak się dzisiaj czujesz?").astype(np.float32)
        user16 = np.interp(np.arange(int(user.size * 16000 / 24000)) * 1.5, np.arange(user.size), user).astype(np.int16)
        music = self._music_clip()
        events = [
            (3.0, "użytkownik mówi", lambda t: rig.add_source(clip_source(user16, 16000, t, gain=1.0))),
            (20.0, "muzyka w pokoju", lambda t: rig.add_source(clip_source(music, 16000, t, gain=1.0))),
            (34.0, "chwyć kostkę", lambda t: self.body.post(Command("pick"))),
            (43.0, "mowa podczas trzymania", lambda t: self._speak_locally(tts, "Trzymam teraz kostkę. Mówię, ale chwytak pozostaje nieruchomy.")),
            (50.0, "odłóż kostkę", lambda t: self.body.post(Command("place"))),
            (59.0, "gest radości", lambda t: self.body.post(Command("gesture", {"name": "happy"}))),
            (59.6, "awaryjny stop", lambda t: self.body.post(Command("estop", {"reason": "test w demie"}))),
            (62.0, "zwolnienie stopu", lambda t: self.body.post(Command("reset"))),
        ]
        return person, events

    # mowa z osi czasu dema jest syntezowana lokalnie, więc działa z każdym backendem rozmowy, także z gemini i bez backendu
    def _speak_locally(self, tts, text: str) -> None:
        for event in speech_events(tts.synth(text), tts.rate):
            self._on_event(event)

    # muzyka do dema pochodzi z pliku użytkownika albo z syntezy perkusji i akordów
    def _music_clip(self) -> np.ndarray:
        if self.music_file is not None and self.music_file.exists():
            import soundfile as sf

            data, sr = sf.read(str(self.music_file), dtype="float32")
            data = data.mean(axis=1) if data.ndim > 1 else data
            data = data[: int(12 * sr)]
            y = np.interp(np.arange(int(data.size * 16000 / sr)) * (sr / 16000), np.arange(data.size), data)
        else:
            rng = np.random.default_rng(0)
            t = np.arange(int(12 * 16000)) / 16000
            beat = 60.0 / 118.0
            y = np.zeros_like(t)
            for k in range(int(12 / beat)):
                s, n = int(k * beat * 16000), int(0.25 * 16000)
                tt = np.arange(n) / 16000
                if s + n < y.size:
                    y[s : s + n] += 0.8 * np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 12)
                    if k % 2:
                        y[s : s + n] += 0.3 * rng.standard_normal(n) * np.exp(-tt * 30)
            for k in range(int(12 / (4 * beat))):
                s, e = int(k * 4 * beat * 16000), min(y.size, int((k + 1) * 4 * beat * 16000))
                tt = np.arange(e - s) / 16000
                for f in ((220, 277, 330), (196, 247, 294), (175, 220, 262), (196, 247, 294))[k % 4]:
                    y[s:e] += 0.15 * np.sin(2 * np.pi * f * tt)
        return (y / (np.max(np.abs(y)) + 1e-9) * 0.3 * 32767).astype(np.int16)

    # tryb wirtualny taktuje wszystko zegarem symulacji, więc przebieg i nagranie są powtarzalne
    def run_virtual(self) -> dict:
        from .ui import Dashboard

        closers: list = []
        rig = VirtualAudioRig(self.playback, self.pipeline)
        if self.record is not None:
            rig.enable_soundtrack()
        tts = self.backend.tts if isinstance(self.backend, ScriptedBackend) else LocalTTS(self.settings.offline_tts_voice)
        person, events = self._demo_timeline(tts, rig)
        duration = self.duration if self.duration is not None else 66.0
        if self.backend is not None:
            self.backend.start()
        dashboard = Dashboard(self.body.sim, self.settings.render_width, self.settings.render_height, window=self.window,
                              mode_label="TRYB WIRTUALNY (skrypt)")
        closers.append(dashboard.close)
        writer = self._writer(2 * self.settings.render_width, self.settings.render_height + PANEL_H, 25)
        if writer is not None:
            closers.append(writer.release)
        dt = self.body.dt
        render_every = max(1, int(round(1.0 / (25 * dt))))
        pending = list(events)
        t, tick = 0.0, 0
        timeline_log = []
        try:
            while t < duration:
                while pending and pending[0][0] <= t:
                    at, label, action = pending.pop(0)
                    action(t)
                    timeline_log.append((round(t, 2), label))
                    self.message = f"oś czasu: {label}"
                obs = person.observe(t)
                self.person.set(obs)
                rig.tick(t, dt)
                record = self.body.step(t)
                if tick % render_every == 0:
                    state = record.state
                    self._housekeeping(state, None, t)
                    if writer is not None or self.window:
                        img = dashboard.compose(synthetic_frame(obs), [], state, self._extra(), mirror=False)
                    if writer is not None:
                        writer.write(img)
                    if self.window:
                        key = dashboard.show(img)
                        if key not in (-1, 255) and not dashboard.handle_view_key(key) and not self.handle_key(key):
                            break
                        time.sleep(max(0.0, render_every * dt - 0.001))
                t += dt
                tick += 1
        finally:
            audio = None
            if self.record is not None:
                audio = self.record.with_suffix(".wav")
                if rig.save_soundtrack(audio) <= 0.0:
                    audio = None
            self._shutdown(closers, audio)
        return {"timeline": timeline_log, "journal": self.body.journal.entries(), "intents": list(self.body.intent_log)}
