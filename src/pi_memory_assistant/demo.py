from __future__ import annotations

import argparse
import time

from .brain import AssistantBrain
from .config import load_settings
from .memory import SupermemoryClient


DEMO_MEMORY = (
    "My garage door sensor has been flaky since the storm, and if I ask about it later, "
    "remind me to check the battery before replacing the sensor."
)
DEMO_QUESTION = (
    "What did I say about the garage door sensor, and what should I try first?"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a no-hardware memory demo for judges.")
    parser.add_argument("--wait", type=int, default=4, help="Seconds to wait after ingesting demo memory.")
    args = parser.parse_args()

    settings = load_settings()
    memory = SupermemoryClient(
        settings.supermemory_local_url,
        settings.supermemory_local_key,
        settings.supermemory_container,
    )
    brain = AssistantBrain(api_key=settings.groq_api_key, model=settings.assistant_model)

    print("Seeding Supermemory with a spoken-style user memory:")
    print(f'  "{DEMO_MEMORY}"')
    memory.remember_user_utterance(DEMO_MEMORY)

    if args.wait > 0:
        print(f"Waiting {args.wait}s for local memory processing...")
        time.sleep(args.wait)

    print("\nAsking a later question:")
    print(f'  "{DEMO_QUESTION}"')
    context = memory.recall(DEMO_QUESTION)
    answer = brain.answer(DEMO_QUESTION, context)

    print("\nPi Recall:")
    print(answer)
