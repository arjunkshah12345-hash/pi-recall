from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolConfig:
    api_key: str | None
    user_id: str
    toolkits: tuple[str, ...]


class ComposioToolRunner:
    def __init__(self, config: ToolConfig) -> None:
        self.enabled = bool(config.api_key and config.toolkits)
        self._tools: list[Any] = []
        if not self.enabled:
            return

        try:
            from composio import Composio
            from composio_langchain import LangchainProvider
        except ImportError as exc:
            raise RuntimeError("Install Pi dependencies with: pip install -e '.[pi]'") from exc

        os.environ.setdefault("COMPOSIO_API_KEY", config.api_key or "")
        self._composio = Composio(provider=LangchainProvider(), api_key=config.api_key)
        self._tools = self._composio.tools.get(
            user_id=config.user_id,
            toolkits=list(config.toolkits),
        )

    @property
    def langchain_tools(self) -> list[Any]:
        return self._tools
