from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# tekst z pliku env musi dać się zamienić na wartość logiczną także w polskiej formie tak lub nie
def parse_bool(raw: str) -> bool:
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "tak", "on"}:
        return True
    if value in {"0", "false", "no", "nie", "off", ""}:
        return False
    raise ValueError(f"nieprawidłowa wartość logiczna: {raw!r}")


# pola ustawień mają adnotacje tekstowe, więc konwersję typu wykonujemy według nazwy typu
def _convert(type_name: str, raw: str, name: str) -> object:
    base = type_name.replace(" ", "").replace("|None", "").replace("Optional[", "").rstrip("]")
    try:
        if base == "bool":
            return parse_bool(raw)
        if base == "int":
            return int(raw)
        if base == "float":
            return float(raw)
        return raw.strip()
    except ValueError as exc:
        raise ValueError(f"zmienna {name.upper()}: {exc}") from exc


# jedno miejsce na nastawy sprawia, że progi bezpieczeństwa i kosztów są jawne i testowalne
@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None = field(default=None, repr=False)
    live_model: str = "gemini-3.8-live"
    voice_name: str = "Puck"
    live_transcripts: bool = True
    transcript_language_hint: str = ""
    context_trigger_tokens: int = 12000
    context_target_tokens: int = 4000
    vad_silence_ms: int = 600
    vad_prefix_ms: int = 300
    idle_disconnect_s: float = 90.0
    reconnect_max_backoff_s: float = 30.0
    budget_session_pln: float = 5.0
    budget_total_pln: float = 130.0
    budget_warn_fraction: float = 0.8
    usd_to_pln: float = 3.65
    cost_safety_factor: float = 1.25
    bill_listening_time: bool = True
    price_text_in_usd: float = 0.75
    price_audio_in_usd: float = 3.00
    price_image_in_usd: float = 1.00
    price_text_out_usd: float = 4.50
    price_audio_out_usd: float = 12.00
    image_tokens_per_frame: int = 258
    ledger_path: str = "runtime/usage_ledger.json"
    mic_stream_mode: str = "vad"
    echo_mode: str = "half_duplex"
    barge_in_ratio: float = 3.0
    barge_in_min_ms: int = 120
    mute_speech_while_holding: bool = False
    vision_uplink_interval_s: float = 0.0
    vision_uplink_width: int = 512
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_hfov_deg: float = 70.0
    mirror_preview: bool = True
    face_model_path: str = "assets/models/face_detection_yunet_2026may.onnx"
    face_score_acquire: float = 0.80
    face_score_keep: float = 0.60
    control_hz: int = 100
    speed_scale: float = 1.0
    mjcf_path: str = "assets/so101/so101.xml"
    render_width: int = 640
    render_height: int = 480
    offline_tts_voice: str = "Zosia"
    log_dir: str = "runtime/logs"
    jaw_lead_s: float = 0.11
    person_return_to_neutral_s: float = 0.0

    # walidacja przy tworzeniu zatrzymuje start z konfiguracją, która mogłaby być niebezpieczna lub droga
    def __post_init__(self) -> None:
        problems: list[str] = []
        if self.budget_session_pln < 0 or self.budget_total_pln < 0:
            problems.append("limity budżetu nie mogą być ujemne")
        if not 0.0 < self.budget_warn_fraction <= 1.0:
            problems.append("BUDGET_WARN_FRACTION musi być w przedziale (0, 1]")
        if self.context_target_tokens >= self.context_trigger_tokens:
            problems.append("CONTEXT_TARGET_TOKENS musi być mniejsze niż CONTEXT_TRIGGER_TOKENS")
        if self.mic_stream_mode not in {"vad", "continuous"}:
            problems.append("MIC_STREAM_MODE musi mieć wartość vad albo continuous")
        if self.echo_mode not in {"half_duplex", "off"}:
            problems.append("ECHO_MODE musi mieć wartość half_duplex albo off")
        if not 0.1 <= self.speed_scale <= 1.0:
            problems.append("SPEED_SCALE musi być w przedziale [0.1, 1.0]")
        if self.control_hz < 50 or self.control_hz > 500:
            problems.append("CONTROL_HZ musi być w przedziale [50, 500]")
        if self.cost_safety_factor < 1.0:
            problems.append("COST_SAFETY_FACTOR nie może być mniejszy niż 1.0")
        if problems:
            raise ValueError("; ".join(problems))

    # klucz api pochodzi wyłącznie ze środowiska lub lokalnego pliku env, nigdy z kodu
    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None, dotenv: Path | None = None) -> "Settings":
        if env is None:
            merged: dict[str, str] = {}
            dotenv_file = dotenv if dotenv is not None else PROJECT_ROOT / ".env"
            if dotenv_file.exists():
                from dotenv import dotenv_values

                merged.update({k: v for k, v in dotenv_values(dotenv_file).items() if v is not None})
            merged.update(os.environ)
        else:
            merged = dict(env)
        kwargs: dict[str, object] = {}
        key = (merged.get("GEMINI_API_KEY") or merged.get("GOOGLE_API_KEY") or "").strip()
        kwargs["gemini_api_key"] = key or None
        for item in fields(cls):
            if item.name == "gemini_api_key":
                continue
            raw = merged.get(item.name.upper())
            if raw is None or raw.strip() == "":
                continue
            kwargs[item.name] = _convert(str(item.type), raw, item.name)
        return cls(**kwargs)

    # ścieżki względne liczymy od katalogu projektu, aby start działał z dowolnego katalogu
    def resolve_path(self, value: str) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else PROJECT_ROOT / path

    # opis do logów nie może zawierać klucza, pokazuje tylko czy jest ustawiony
    def describe(self) -> dict[str, object]:
        out: dict[str, object] = {}
        for item in fields(self):
            if item.name == "gemini_api_key":
                out[item.name] = "ustawiony" if self.gemini_api_key else "brak"
            else:
                out[item.name] = getattr(self, item.name)
        return out
