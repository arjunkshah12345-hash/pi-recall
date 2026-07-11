from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import requests
import sounddevice as sd

from .config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Pi Recall runtime configuration.")
    parser.parse_args()

    settings = load_settings(require_required=False)
    checks = [
        ("GROQ_API_KEY", bool(settings.groq_api_key)),
        ("SUPERMEMORY_LOCAL_KEY", bool(settings.supermemory_local_key)),
        ("PICOVOICE_ACCESS_KEY", bool(settings.picovoice_access_key)),
        ("wake word file", Path(settings.porcupine_keyword_path).exists()),
        ("audio input devices", _has_input_device(settings.input_device)),
        ("audio output devices", _has_output_device(settings.output_device)),
        ("supermemory local reachable", _supermemory_reachable(settings.supermemory_local_url)),
        ("composio configured", bool(settings.composio_api_key) or not settings.composio_toolkits),
        ("ffmpeg optional", bool(shutil.which("ffmpeg"))),
    ]

    failed = False
    for name, ok in checks:
        marker = "ok" if ok else "missing"
        print(f"{marker:7} {name}")
        failed = failed or not ok

    if failed:
        raise SystemExit(1)


def _has_input_device(device_index: int | None) -> bool:
    return _has_device(device_index, "max_input_channels")


def _has_output_device(device_index: int | None) -> bool:
    return _has_device(device_index, "max_output_channels")


def _has_device(device_index: int | None, key: str) -> bool:
    try:
        if device_index is not None:
            return int(sd.query_devices(device_index)[key]) > 0
        return any(int(device[key]) > 0 for device in sd.query_devices())
    except Exception:
        return False


def _supermemory_reachable(base_url: str) -> bool:
    try:
        response = requests.get(base_url, timeout=3)
    except requests.RequestException:
        return False
    return response.status_code < 500
