# Pi Recall for Alexa+ — Amazon Developer Hackathon (Alexa+ track)

> Devpost fields below. Demo video must show the MCP server running and Alexa+ (or an MCP client like the MCP Inspector) calling `remember` / `recall`. The Alexa+ track requires a self-hosted MCP server on Streamable HTTP, MCP spec 2025-11-25 or later — this server reports protocol `2026-07-28`.

**Tagline:** The memory your home already told the Raspberry Pi, now available to Alexa+ — a self-hosted MCP server for shared household memory.

**Repo:** https://github.com/arjunkshah12345-hash/pi-recall · run `pi-recall-mcp`

---

## Inspiration
Voice assistants forget. Pi Recall already gives a Raspberry Pi assistant long-term memory. Alexa+ is built to use MCP servers — so the household's memory should be one shared brain: what you told the Pi in the kitchen last month should be there when you ask Alexa+ in the living room, and vice versa.

## What it does
`pi-recall-mcp` serves the household's long-term memory as a self-hosted MCP server over Streamable HTTP, with three tools:
- **`remember(note, who?)`** — save a fact, plan, or preference ("the plumber is coming Thursday at 9").
- **`recall(question)`** — answer "what did I say about…" from long-term memory.
- **`household_brief()`** — the standing profile plus the most recent things saved.

Every tool returns structured output and a `speech` field written to be read aloud; `recall` and `household_brief` are marked read-only. It's the same memory the Pi voice assistant reads and writes, so Alexa+ and the Pi share one store.

## How we used the Alexa+ required tech
- A **self-hosted MCP server** built on the official MCP Python SDK, served over **Streamable HTTP** at `/mcp`.
- Protocol version negotiated at **2026-07-28**, meeting the ≥ 2025-11-25 requirement.
- Tools expose structured JSON schemas and tool annotations so an Alexa+-class client can call them directly. The repo's code actually imports and runs the MCP server (entry point `pi-recall-mcp`), not just a mention in the README.

## Security
The server holds a family's private memory, so it refuses to bind beyond localhost without `PI_RECALL_MCP_TOKEN` and checks `Authorization: Bearer <token>` on every request. For Alexa+ you expose it over HTTPS (e.g. a Cloudflare Tunnel) with the token set.

## Built during the hackathon
Pi Recall existed before as a Raspberry Pi voice assistant (an earlier Supermemory hackathon entry) — disclosed per the "new & existing" rule. **New for this hackathon:** the entire MCP server (`mcp_server.py`), a backend-agnostic `MemoryStore` interface, a SQLite FTS5 fallback so it runs with no external services, bearer-token auth, and an end-to-end MCP test suite.

## How to run / test
`pip install -e . && pi-recall-mcp` serves `http://127.0.0.1:8765/mcp`. With no Supermemory install it uses a local SQLite memory, so judges can run it immediately. Point the MCP Inspector (`npx @modelcontextprotocol/inspector`) at it, or wire it into Alexa+. `pytest` → 11 passing tests, including real round-trips through the official MCP client over Streamable HTTP.

## Tech
Python, official MCP SDK (Streamable HTTP), Supermemory Local or SQLite FTS5, uvicorn/Starlette.

## Challenges
Making the tools useful to a voice surface (short `speech` fields, read-only hints) while keeping a private memory store genuinely private (token gate, no bind beyond localhost without it).

## What's next
Per-member memory scoping, an Alexa+ "forget this" tool, and a deploy recipe for the Pi to expose the server over a tunnel automatically.
