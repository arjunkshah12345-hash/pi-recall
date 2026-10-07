"""Pi Recall for Alexa+: the household memory as a self-hosted MCP server.

Alexa+ (or any MCP client) connects over Streamable HTTP and gets three tools:

* ``remember``        save something about the household ("the plumber comes Thursday")
* ``recall``          answer "what did I say about ..." from long-term memory
* ``household_brief`` the standing profile: people, preferences, routines

The same memory the Raspberry Pi assistant writes to by voice, so what you
told the Pi in the kitchen last month is available to Alexa+ in the living room.

Run:  pi-recall-mcp            (serves http://127.0.0.1:8765/mcp)
"""

from __future__ import annotations

import argparse
import hmac
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .memory import SupermemoryClient
from .memory_store import MemoryStore, SqliteStore, SupermemoryStore

INSTRUCTIONS = """\
Pi Recall is this household's long-term memory, shared with the Raspberry Pi voice assistant.
Call `recall` before answering any question about the household's people, plans, preferences,
appointments or things someone asked to be remembered. Call `remember` when someone asks you to
remember something, or states a lasting fact about the household. Answers are meant to be spoken:
keep what you say short."""


class RememberResult(BaseModel):
    stored: bool
    speech: str = Field(description="One short sentence to say back to the person.")


class RecallResult(BaseModel):
    found: bool
    memories: list[str] = Field(description="Most relevant memories, best first.")
    profile: list[str] = Field(description="Standing facts about the household, if any.")
    speech: str = Field(description="A short spoken summary of what was found.")


class BriefResult(BaseModel):
    profile: list[str]
    recent: list[str]
    speech: str


def build_store() -> MemoryStore:
    load_dotenv()
    backend = os.getenv("MEMORY_BACKEND", "sqlite" if not os.getenv("SUPERMEMORY_LOCAL_KEY") else "supermemory")
    if backend == "supermemory":
        return SupermemoryStore(
            SupermemoryClient(
                base_url=os.getenv("SUPERMEMORY_LOCAL_URL", "http://localhost:6767"),
                api_key=os.environ["SUPERMEMORY_LOCAL_KEY"],
                container_tag=os.getenv("SUPERMEMORY_CONTAINER", "default-pi-user"),
            )
        )
    return SqliteStore(os.getenv("PI_RECALL_DB", str(Path.home() / ".pi-recall" / "memories.db")))


def build_server(store: MemoryStore) -> MCPServer:
    mcp = MCPServer(
        name="pi-recall",
        title="Pi Recall",
        description="Long-term household memory shared between a Raspberry Pi voice assistant and Alexa+.",
        instructions=INSTRUCTIONS,
        website_url="https://pi-recall.vercel.app",
        version="0.2.0",
    )

    @mcp.tool(
        title="Remember something",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False),
    )
    def remember(note: str, who: str | None = None) -> RememberResult:
        """Save a fact, plan or preference about the household so it can be recalled later.

        Args:
            note: What to remember, as a complete sentence. Example: "The plumber is coming Thursday at 9."
            who: Who said it, if known. Example: "Maya".
        """
        note = note.strip()
        if not note:
            return RememberResult(stored=False, speech="I didn't catch anything to remember.")
        store.remember(note, source="alexa-plus-mcp", speaker=(who or "").strip() or None)
        return RememberResult(stored=True, speech=f"Got it. I'll remember that {_as_clause(note)}")

    @mcp.tool(
        title="Recall from household memory",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    def recall(question: str) -> RecallResult:
        """Look up what the household has told the assistant before.

        Args:
            question: What to look up, in plain words. Example: "when is the plumber coming?"
        """
        result = store.recall(question, limit=5)
        if not result.memories and not result.profile:
            return RecallResult(found=False, memories=[], profile=[], speech="I don't have anything saved about that yet.")
        top = result.memories[:2] or result.profile[:2]
        return RecallResult(
            found=True,
            memories=result.memories,
            profile=result.profile,
            speech="Here's what I have: " + " ".join(_sentence(m) for m in top),
        )

    @mcp.tool(
        title="Household brief",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
    )
    def household_brief() -> BriefResult:
        """The standing picture of the household: people, preferences and the most recent things saved."""
        result = store.recall("", limit=8)
        recent = result.memories
        speech = (
            f"I know {len(result.profile)} standing facts and here are the latest {len(recent)} things I was told."
            if recent or result.profile
            else "Nothing has been saved yet."
        )
        return BriefResult(profile=result.profile, recent=recent, speech=speech)

    return mcp


class BearerAuth:
    """Rejects requests without ``Authorization: Bearer <PI_RECALL_MCP_TOKEN>``.

    The server holds a family's private memories, so it refuses to start on a
    non-loopback address without a token (see main()).
    """

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            supplied = dict(scope.get("headers") or []).get(b"authorization", b"")
            if not hmac.compare_digest(supplied, self.expected):
                await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
                return
        await self.app(scope, receive, send)


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


_LOWERCASE_LEADS = {"the", "a", "an", "our", "my", "we", "it", "there", "this", "that", "every", "next"}


def _as_clause(note: str) -> str:
    """'The plumber...' -> 'the plumber...', but leave names like 'Maya...' alone."""
    clause = _sentence(note)
    first = clause.split(" ", 1)[0]
    return clause[0].lower() + clause[1:] if first.lower() in _LOWERCASE_LEADS else clause


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Pi Recall's memory to Alexa+ over MCP (Streamable HTTP).")
    parser.add_argument("--host", default=os.getenv("PI_RECALL_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PI_RECALL_MCP_PORT", "8765")))
    args = parser.parse_args()

    import uvicorn

    store = build_store()
    server = build_server(store)
    token = os.getenv("PI_RECALL_MCP_TOKEN", "")
    loopback = args.host in {"127.0.0.1", "localhost", "::1"}
    if not token and not loopback:
        raise SystemExit("Set PI_RECALL_MCP_TOKEN before serving household memory beyond localhost.")
    app = server.streamable_http_app(host=args.host)
    if token:
        app = BearerAuth(app, token)
    print(f"Pi Recall MCP on http://{args.host}:{args.port}/mcp  (memory: {store.name}, auth: {'bearer' if token else 'none, localhost only'})", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
