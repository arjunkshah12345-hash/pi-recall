"""Memory backends behind one small interface.

The Pi assistant and the Alexa+ MCP server both talk to a ``MemoryStore``:

* ``SupermemoryStore`` wraps the existing Supermemory Local client (the default
  on the Pi).
* ``SqliteStore`` keeps memories in a local SQLite FTS5 index, so the MCP
  server runs anywhere with no extra services. Useful for development and for
  anyone trying the project without a Supermemory Local install.
"""

from __future__ import annotations

import re
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from .memory import SupermemoryClient


@dataclass(frozen=True)
class Recall:
    profile: list[str] = field(default_factory=list)
    memories: list[str] = field(default_factory=list)


class MemoryStore(Protocol):
    name: str

    def remember(self, text: str, *, source: str, speaker: str | None = None) -> None: ...

    def recall(self, query: str, *, limit: int = 5) -> Recall: ...


class SupermemoryStore:
    name = "supermemory-local"

    def __init__(self, client: SupermemoryClient) -> None:
        self.client = client

    def remember(self, text: str, *, source: str, speaker: str | None = None) -> None:
        self.client.remember(text, source=source, speaker=speaker)

    def recall(self, query: str, *, limit: int = 5) -> Recall:
        ctx = self.client.recall(query)
        profile = [line for line in (ctx.static_profile + "\n" + ctx.dynamic_profile).splitlines() if line]
        memories = [line for line in ctx.memories.splitlines() if line][:limit]
        return Recall(profile=profile, memories=memories)


_WORD = re.compile(r"[a-z0-9']+")
_STOP = {
    "the", "a", "an", "is", "are", "was", "what", "when", "where", "who", "how", "do", "does",
    "did", "to", "of", "and", "or", "for", "in", "on", "at", "my", "our", "we", "i", "you",
    "me", "it", "that", "this", "with", "about", "be", "can", "should", "tell", "remember",
}


class SqliteStore:
    name = "sqlite"

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.executescript(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS memories USING fts5(
                text, speaker UNINDEXED, source UNINDEXED, created_at UNINDEXED,
                tokenize = 'porter unicode61'
            );
            """
        )

    def remember(self, text: str, *, source: str, speaker: str | None = None) -> None:
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO memories (text, speaker, source, created_at) VALUES (?, ?, ?, ?)",
                (text, speaker or "", source, datetime.now(UTC).isoformat()),
            )

    def recall(self, query: str, *, limit: int = 5) -> Recall:
        terms = [w for w in _WORD.findall(query.lower()) if w not in _STOP and len(w) > 1]
        with self._lock:
            if terms:
                match = " OR ".join(f'"{t}"' for t in terms)
                rows = self._db.execute(
                    "SELECT text, speaker FROM memories WHERE memories MATCH ? ORDER BY rank LIMIT ?",
                    (match, limit),
                ).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT text, speaker FROM memories ORDER BY rowid DESC LIMIT ?", (limit,)
                ).fetchall()
        return Recall(memories=[_attributed(text, speaker) for text, speaker in rows])

    def count(self) -> int:
        with self._lock:
            return self._db.execute("SELECT count(*) FROM memories").fetchone()[0]


def _attributed(text: str, speaker: str) -> str:
    return f"{speaker}: {text}" if speaker else text
