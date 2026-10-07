"""End-to-end: the MCP server over real Streamable HTTP, driven by the official MCP client."""

from __future__ import annotations

import asyncio
import socket
import threading
import time

import httpx2
import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from pi_memory_assistant.mcp_server import BearerAuth, _as_clause, build_server
from pi_memory_assistant.memory_store import SqliteStore

TOKEN = "test-token"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    store = SqliteStore(":memory:")
    app = BearerAuth(build_server(store).streamable_http_app(), TOKEN)
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}/mcp"
    server.should_exit = True
    thread.join(timeout=5)


async def _session_call(url, fn):
    async with (
        httpx2.AsyncClient(headers={"Authorization": f"Bearer {TOKEN}"}) as http,
        streamable_http_client(url, http_client=http) as (read, write, *_),
        ClientSession(read, write) as session,
    ):
        init = await session.initialize()
        return await fn(session, init)


def test_protocol_version_meets_alexa_requirement(server_url):
    async def check(_session, init):
        return init.protocol_version

    version = asyncio.run(_session_call(server_url, check))
    assert version >= "2025-11-25"


def test_tools_are_listed_with_annotations(server_url):
    async def check(session, _init):
        return (await session.list_tools()).tools

    tools = {t.name: t for t in asyncio.run(_session_call(server_url, check))}
    assert set(tools) == {"remember", "recall", "household_brief"}
    assert tools["recall"].annotations.read_only_hint is True
    assert tools["remember"].annotations.read_only_hint is False
    assert tools["recall"].output_schema is not None


def test_remember_then_recall_round_trip(server_url):
    async def check(session, _init):
        stored = await session.call_tool("remember", {"note": "The plumber is coming Thursday at 9", "who": "Maya"})
        await session.call_tool("remember", {"note": "Leo is allergic to peanuts"})
        found = await session.call_tool("recall", {"question": "when is the plumber coming?"})
        missing = await session.call_tool("recall", {"question": "what's the wifi password?"})
        return stored, found, missing

    stored, found, missing = asyncio.run(_session_call(server_url, check))
    assert stored.structured_content["stored"] is True
    assert "the plumber is coming thursday" in stored.structured_content["speech"].lower()
    assert found.structured_content["found"] is True
    assert "plumber" in found.structured_content["memories"][0].lower()
    assert found.structured_content["memories"][0].startswith("Maya:")
    assert missing.structured_content["found"] is False


def test_requests_without_token_are_rejected(server_url):
    response = httpx2.post(server_url, json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
    assert response.status_code == 401


def test_clause_keeps_names_capitalised():
    assert _as_clause("The plumber is coming") == "the plumber is coming."
    assert _as_clause("Maya likes oat milk") == "Maya likes oat milk."
