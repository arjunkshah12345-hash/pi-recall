from __future__ import annotations

import logging
from pathlib import Path

from .audio import record_wav
from .brain import AssistantBrain
from .config import load_settings
from .memory import SupermemoryClient
from .speech import SpeechService
from .tools import ComposioToolRunner, ToolConfig
from .wake import PorcupineWakeWord, WakeWordConfig

LOG = logging.getLogger("pi-assistant")


class PiAssistant:
    def __init__(self) -> None:
        settings = load_settings()
        if not settings.picovoice_access_key:
            raise RuntimeError("PICOVOICE_ACCESS_KEY is required for wake-word mode.")

        self.settings = settings
        self.memory = SupermemoryClient(
            settings.supermemory_local_url,
            settings.supermemory_local_key,
            settings.supermemory_container,
        )
        self.speech = SpeechService(
            api_key=settings.groq_api_key,
            stt_model=settings.stt_model,
            tts_model=settings.tts_model,
            tts_voice=settings.tts_voice,
            output_device=settings.output_device,
        )
        self.tools = ComposioToolRunner(
            ToolConfig(
                api_key=settings.composio_api_key,
                user_id=settings.composio_user_id,
                toolkits=settings.composio_toolkits,
            )
        )
        self.brain = AssistantBrain(
            api_key=settings.groq_api_key,
            model=settings.assistant_model,
            tool_runner=self.tools,
        )
        self.wake = PorcupineWakeWord(
            WakeWordConfig(
                access_key=settings.picovoice_access_key,
                keyword_path=settings.porcupine_keyword_path,
                model_path=settings.porcupine_model_path,
            )
        )

    def run_forever(self) -> None:
        LOG.info("Listening for Hey Pi.")
        try:
            while True:
                self.wake.wait()
                self.handle_turn()
        finally:
            self.wake.close()

    def handle_turn(self) -> None:
        LOG.info("Wake word detected. Recording utterance.")
        wav_path = record_wav(
            seconds=self.settings.record_seconds,
            sample_rate=self.settings.sample_rate,
            input_device=self.settings.input_device,
            silence_rms_threshold=self.settings.silence_rms_threshold,
        )
        if wav_path is None:
            LOG.info("Ignored silent recording.")
            return

        try:
            user_text = self.speech.transcribe(wav_path)
        finally:
            Path(wav_path).unlink(missing_ok=True)

        if not user_text:
            return

        LOG.info("User: %s", user_text)
        self.memory.remember_user_utterance(user_text)
        context = self.memory.recall(user_text)
        answer = self.brain.answer(user_text, context)
        LOG.info("Assistant: %s", answer)
        self.speech.speak(answer)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    PiAssistant().run_forever()


if __name__ == "__main__":
    main()
