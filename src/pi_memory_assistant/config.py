from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _optional_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value)


def _optional_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    supermemory_local_url: str
    supermemory_local_key: str
    supermemory_container: str
    composio_api_key: str | None
    composio_user_id: str
    composio_toolkits: tuple[str, ...]
    picovoice_access_key: str | None
    porcupine_keyword_path: str
    porcupine_model_path: str | None
    input_device: int | None
    output_device: int | None
    record_seconds: int
    sample_rate: int
    silence_rms_threshold: float
    assistant_model: str
    stt_model: str
    tts_model: str
    tts_voice: str


def load_settings(*, require_required: bool = True) -> Settings:
    load_dotenv()
    toolkits = tuple(
        item.strip()
        for item in os.getenv("COMPOSIO_TOOLKITS", "").split(",")
        if item.strip()
    )
    return Settings(
        groq_api_key=_env("GROQ_API_KEY", require=require_required),
        supermemory_local_url=os.getenv(
            "SUPERMEMORY_LOCAL_URL",
            "http://localhost:6767",
        ).rstrip("/"),
        supermemory_local_key=_env("SUPERMEMORY_LOCAL_KEY", require=require_required),
        supermemory_container=os.getenv("SUPERMEMORY_CONTAINER", "default-pi-user"),
        composio_api_key=os.getenv("COMPOSIO_API_KEY") or None,
        composio_user_id=os.getenv("COMPOSIO_USER_ID", "local-user"),
        composio_toolkits=toolkits,
        picovoice_access_key=os.getenv("PICOVOICE_ACCESS_KEY") or None,
        porcupine_keyword_path=os.getenv("PORCUPINE_KEYWORD_PATH", "./wakewords/hey-pi.ppn"),
        porcupine_model_path=os.getenv("PORCUPINE_MODEL_PATH") or None,
        input_device=_optional_int(os.getenv("INPUT_DEVICE")),
        output_device=_optional_int(os.getenv("OUTPUT_DEVICE")),
        record_seconds=int(os.getenv("RECORD_SECONDS", "8")),
        sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
        silence_rms_threshold=_optional_float(os.getenv("SILENCE_RMS_THRESHOLD")) or 0.012,
        assistant_model=os.getenv("ASSISTANT_MODEL", "llama-3.3-70b-versatile"),
        stt_model=os.getenv("STT_MODEL", "whisper-large-v3-turbo"),
        tts_model=os.getenv("TTS_MODEL", "canopylabs/orpheus-v1-english"),
        tts_voice=os.getenv("TTS_VOICE", "troy"),
    )


def _env(name: str, *, require: bool) -> str:
    value = os.getenv(name, "")
    if require and not value:
        raise RuntimeError(f"{name} is required. Copy .env.example to .env and fill it in.")
    return value
