from __future__ import annotations

import argparse
import logging
import os
import platform
import sys
import time
from pathlib import Path


# na linuksie bez ekranu renderer mujoco potrzebuje osmesa, a na macos zostawiamy domyślny cgl
def _configure_gl(headless: bool) -> None:
    if sys.platform.startswith("linux") and (headless or not os.environ.get("DISPLAY")):
        os.environ.setdefault("MUJOCO_GL", "osmesa")


# autodiagnostyka sprawdza środowisko przed pierwszym uruchomieniem i nie ujawnia wartości klucza
def run_check(settings, try_devices: bool = True) -> int:
    problems = 0

    # jedna linia raportu z wynikiem sprawdzenia
    def report(ok: bool | None, label: str, detail: str = "") -> None:
        nonlocal problems
        tag = "OK   " if ok else ("INFO " if ok is None else "BŁĄD ")
        if ok is False:
            problems += 1
        print(f"[{tag}] {label}{': ' + detail if detail else ''}")

    report(sys.version_info >= (3, 10), "Python", platform.python_version())
    report(None, "system", f"{platform.system()} {platform.machine()}")
    try:
        import mujoco

        from .sim.mujoco_sim import MujocoSim

        sim = MujocoSim(settings.resolve_path(settings.mjcf_path))
        report(True, "MuJoCo", f"{mujoco.__version__}, model {settings.mjcf_path}, ramię 6 przegubów + kostka w scenie")
        from .sim.render import SimRenderer

        renderer = SimRenderer(sim, 320, 240)
        img = renderer.render()
        renderer.close()
        report(img.mean() > 5, "renderer MuJoCo poza ekranem", f"{img.shape[1]}x{img.shape[0]}, MUJOCO_GL={os.environ.get('MUJOCO_GL', 'domyślny')}")
    except Exception as exc:
        report(False, "MuJoCo", repr(exc))
    try:
        import cv2
        import numpy as np

        from .inputs.face import FaceDetector

        det = FaceDetector(settings.resolve_path(settings.face_model_path))
        report(det.detect(np.zeros((480, 640, 3), np.uint8)) == [], "detektor twarzy YuNet", f"OpenCV {cv2.__version__}")
    except Exception as exc:
        report(False, "detektor twarzy YuNet", repr(exc))
    if try_devices:
        try:
            from .inputs.camera import CameraSource

            cam = CameraSource(settings.camera_index, settings.camera_width, settings.camera_height)
            cam.start()
            deadline = time.monotonic() + 3.0
            while cam.latest() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            item = cam.latest()
            cam.close()
            report(item is not None, "kamera", f"klatka {item[0].shape[1]}x{item[0].shape[0]}" if item else "brak klatek w 3 s")
        except Exception as exc:
            report(False, "kamera", str(exc))
        try:
            import sounddevice as sd

            dev_in = sd.query_devices(kind="input")
            dev_out = sd.query_devices(kind="output")
            report(True, "audio", f"wejście: {dev_in['name']}, wyjście: {dev_out['name']}")
        except Exception as exc:
            report(False, "audio", str(exc))
    report(True if settings.gemini_api_key else None, "GEMINI_API_KEY",
           "ustawiony (wartość ukryta)" if settings.gemini_api_key else "brak - rozmowa działa w trybie lokalnym")
    from .budget import CostMeter

    snap = CostMeter.from_settings(settings).snapshot()
    report(not snap.blocked, "budżet", f"wydano łącznie ok. {snap.total_pln:.2f} z {snap.total_limit_pln:.2f} zł (szacunek)")
    print(f"\nWynik: {'wszystko gotowe' if problems == 0 else f'{problems} problem(y) do rozwiązania'}")
    return 0 if problems == 0 else 1


# jawnie włączany test prawdziwego api kosztuje ułamek grosza i potwierdza klucz, model i dźwięk
def run_api_smoke(settings) -> int:
    import asyncio

    from google import genai
    from google.genai import types

    from .budget import CostMeter
    from .conversation.gemini_live import GeminiLiveBackend, classify_error

    if not settings.gemini_api_key:
        print("brak GEMINI_API_KEY w .env")
        return 1
    meter = CostMeter.from_settings(settings)
    backend = GeminiLiveBackend(settings, meter, lambda e: None)
    config = backend.build_config()

    # jedna krótka tura tekstowa z odpowiedzią głosową i zliczeniem zużycia
    async def once() -> tuple[int, list]:
        client = genai.Client(api_key=settings.gemini_api_key)
        audio_bytes, usages = 0, []
        async with client.aio.live.connect(model=settings.live_model, config=config) as session:
            await session.send_client_content(
                turns=[types.Content(role="user", parts=[types.Part(text="Powiedz krótko po polsku: test połączenia udany.")])],
                turn_complete=True,
            )
            async for msg in session.receive():
                if msg.usage_metadata:
                    usages.append(msg.usage_metadata)
                    meter.record_server_usage(msg.usage_metadata)
                if msg.server_content and msg.server_content.model_turn:
                    for part in msg.server_content.model_turn.parts or []:
                        if part.inline_data and part.inline_data.data:
                            audio_bytes += len(part.inline_data.data)
        return audio_bytes, usages

    try:
        audio_bytes, usages = asyncio.run(asyncio.wait_for(once(), 30))
    except Exception as exc:
        print("test api nieudany:", classify_error(exc)[1])
        return 1
    meter.flush()
    print(f"model {settings.live_model}: {audio_bytes / 2 / 24000:.1f} s odpowiedzi audio, wiadomości zużycia: {len(usages)}")
    print(f"koszt według serwera: {meter.server_usd * settings.usd_to_pln:.4f} zł (szacunek)")
    return 0 if audio_bytes > 0 else 1


# jedna komenda startowa z opcjami trybu wirtualnego, nagrywania i diagnostyki
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="so101-expressive", description="Ekspresyjny robot rozmowny SO-101 w symulacji MuJoCo")
    parser.add_argument("--virtual", action="store_true", help="bez kamery, mikrofonu i głośnika: skryptowane demo")
    parser.add_argument("--headless", action="store_true", help="bez okna, np. do nagrania wideo")
    parser.add_argument("--record", type=Path, help="zapisz panel do pliku mp4")
    parser.add_argument("--duration", type=float, help="czas działania w sekundach")
    parser.add_argument("--backend", choices=["auto", "gemini", "scripted", "none"], default="auto")
    parser.add_argument("--no-camera", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--music-file", type=Path, help="plik muzyki do dema wirtualnego")
    parser.add_argument("--check", action="store_true", help="sprawdź środowisko, kamerę, audio i MuJoCo")
    parser.add_argument("--api-smoke", action="store_true", help="jedna krótka tura z prawdziwym Gemini Live")
    args = parser.parse_args(argv)
    _configure_gl(args.headless or args.check)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from .config import Settings

    settings = Settings.from_env()
    if args.check:
        return run_check(settings)
    if args.api_smoke:
        return run_api_smoke(settings)
    from .app import RobotApp

    app = RobotApp(
        settings, virtual=args.virtual, backend=args.backend, window=not args.headless, record=args.record,
        duration=args.duration, use_camera=not args.no_camera, use_audio=not args.no_audio, music_file=args.music_file,
    )
    if args.virtual:
        result = app.run_virtual()
        for t, label in result["timeline"]:
            print(f"{t:6.2f} s  {label}")
    else:
        app.run_live()
    if app.recording_info:
        print(f"nagranie {args.record}: {app.recording_info}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
