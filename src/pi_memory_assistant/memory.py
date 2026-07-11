from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests


@dataclass(frozen=True)
class MemoryContext:
    static_profile: str
    dynamic_profile: str
    memories: str

    def as_prompt_block(self) -> str:
        return (
            "Known user profile:\n"
            f"{self.static_profile or '(none)'}\n\n"
            "Recent/derived profile:\n"
            f"{self.dynamic_profile or '(none)'}\n\n"
            "Relevant memories:\n"
            f"{self.memories or '(none)'}"
        )


class SupermemoryClient:
    def __init__(self, base_url: str, api_key: str, container_tag: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.container_tag = container_tag
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def remember_user_utterance(self, text: str) -> None:
        payload = {
            "content": text,
            "containerTag": self.container_tag,
            "metadata": {
                "source": "raspberry-pi-voice",
                "role": "user",
                "capturedAt": datetime.now(timezone.utc).isoformat(),
            },
        }
        response = self.session.post(f"{self.base_url}/v3/documents", json=payload, timeout=20)
        response.raise_for_status()

    def recall(self, query: str) -> MemoryContext:
        payload = {"containerTag": self.container_tag, "q": query}
        response = self.session.post(f"{self.base_url}/v4/profile", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        profile = data.get("profile") or {}
        static = "\n".join(_as_strings(profile.get("static")))
        dynamic = "\n".join(_as_strings(profile.get("dynamic")))
        search_results = data.get("searchResults") or data.get("search_results") or {}
        results = search_results.get("results") if isinstance(search_results, dict) else []
        memories = "\n".join(_memory_text(item) for item in results or [])
        return MemoryContext(static_profile=static, dynamic_profile=dynamic, memories=memories)


def _as_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def _memory_text(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("memory") or item.get("content") or item.get("text") or "")
    return str(item)
