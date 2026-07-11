from __future__ import annotations

from typing import Any

from groq import Groq

from .memory import MemoryContext
from .tools import ComposioToolRunner


class AssistantBrain:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        tool_runner: ComposioToolRunner | None = None,
    ) -> None:
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        self.model = model
        self.tool_runner = tool_runner

    def answer(self, user_text: str, memory_context: MemoryContext) -> str:
        if self.tool_runner and self.tool_runner.enabled:
            return self._answer_with_composio(user_text, memory_context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Hey Pi, a concise home voice assistant on a Raspberry Pi. "
                        "Use memory context when it helps. Do not mention implementation details. "
                        "For voice, answer in short spoken paragraphs."
                    ),
                },
                {"role": "system", "content": memory_context.as_prompt_block()},
                {"role": "user", "content": user_text},
            ],
            temperature=0.3,
            max_completion_tokens=450,
        )
        return response.choices[0].message.content.strip()

    def _answer_with_composio(self, user_text: str, memory_context: MemoryContext) -> str:
        try:
            from langchain.agents import create_agent
            from langchain_groq import ChatGroq
        except ImportError as exc:
            raise RuntimeError("Install Pi dependencies with: pip install -e '.[pi]'") from exc

        llm = ChatGroq(model=self.model, api_key=self.api_key, temperature=0.2)
        agent: Any = create_agent(
            model=llm,
            tools=self.tool_runner.langchain_tools,
            system_prompt=(
                "You are Hey Pi, a concise home voice assistant. Use tools only when needed. "
                "Answer briefly for spoken audio."
            ),
        )
        task = (
            f"{memory_context.as_prompt_block()}\n\n"
            f"User request: {user_text}\n\n"
            "Answer briefly for spoken audio."
        )
        result = agent.invoke({"messages": [{"role": "user", "content": task}]})
        return extract_agent_text(result)


def extract_agent_text(result: Any) -> str:
    if isinstance(result, dict) and result.get("messages"):
        message = result["messages"][-1]
        content = getattr(message, "content", None)
        if content:
            return str(content).strip()
    return str(result).strip()
