from pi_memory_assistant.brain import extract_agent_text


class Message:
    def __init__(self, content: str) -> None:
        self.content = content


def test_extract_agent_text_from_langchain_message_result() -> None:
    result = {"messages": [Message("ignored"), Message("Done.")]}

    assert extract_agent_text(result) == "Done."
