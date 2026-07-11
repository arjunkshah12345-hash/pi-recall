from __future__ import annotations

import argparse

from .brain import AssistantBrain
from .config import load_settings
from .memory import SupermemoryClient
from .speech import SpeechService
from .tools import ComposioToolRunner, ToolConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pi Recall without wake-word hardware.")
    parser.add_argument("--speak", action="store_true", help="Speak answers through configured audio output.")
    args = parser.parse_args()

    settings = load_settings()
    memory = SupermemoryClient(
        settings.supermemory_local_url,
        settings.supermemory_local_key,
        settings.supermemory_container,
    )
    tools = ComposioToolRunner(
        ToolConfig(
            api_key=settings.composio_api_key,
            user_id=settings.composio_user_id,
            toolkits=settings.composio_toolkits,
        )
    )
    brain = AssistantBrain(
        api_key=settings.groq_api_key,
        model=settings.assistant_model,
        tool_runner=tools,
    )
    speech = SpeechService(
        api_key=settings.groq_api_key,
        stt_model=settings.stt_model,
        tts_model=settings.tts_model,
        tts_voice=settings.tts_voice,
        output_device=settings.output_device,
    )

    while True:
        user_text = input("you> ").strip()
        if user_text.lower() in {"exit", "quit"}:
            return
        if not user_text:
            continue
        memory.remember_user_utterance(user_text)
        context = memory.recall(user_text)
        answer = brain.answer(user_text, context)
        print(f"pi> {answer}")
        if args.speak:
            speech.speak(answer)


if __name__ == "__main__":
    main()
