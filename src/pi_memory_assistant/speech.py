from __future__ import annotations

import tempfile
from pathlib import Path

from groq import Groq

from .audio import play_audio_file


class SpeechService:
    def __init__(
        self,
        *,
        api_key: str,
        stt_model: str,
        tts_model: str,
        tts_voice: str,
        output_device: int | None,
    ) -> None:
        self.client = Groq(api_key=api_key)
        self.stt_model = stt_model
        self.tts_model = tts_model
        self.tts_voice = tts_voice
        self.output_device = output_device

    def transcribe(self, wav_path: Path) -> str:
        with wav_path.open("rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.stt_model,
                file=audio_file,
                response_format="json",
                language="en",
                temperature=0.0,
            )
        return transcript.text.strip()

    def speak(self, text: str) -> None:
        output_path = Path(tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name)
        response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=self.tts_voice,
            input=text,
            response_format="wav",
        )
        response.write_to_file(output_path)
        play_audio_file(output_path, output_device=self.output_device)
