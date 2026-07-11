from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


def record_wav(
    *,
    seconds: int,
    sample_rate: int,
    input_device: int | None,
    silence_rms_threshold: float,
) -> Path | None:
    frames = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=input_device,
    )
    sd.wait()
    rms = float(np.sqrt(np.mean(np.square(frames))))
    if rms < silence_rms_threshold:
        return None

    path = Path(tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name)
    sf.write(path, frames, sample_rate)
    return path


def play_audio_file(path: Path, *, output_device: int | None = None) -> None:
    data, sample_rate = sf.read(path, dtype="float32")
    sd.play(data, sample_rate, device=output_device)
    sd.wait()


def write_pcm16_wav(path: Path, pcm: bytes, sample_rate: int) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)
