from pi_memory_assistant.memory import MemoryContext, _memory_text


def test_memory_context_prompt_handles_empty_values() -> None:
    context = MemoryContext(static_profile="", dynamic_profile="", memories="")
    prompt = context.as_prompt_block()
    assert "Known user profile" in prompt
    assert prompt.count("(none)") == 3


def test_memory_text_prefers_memory_field() -> None:
    assert _memory_text({"memory": "likes late workouts", "content": "ignored"}) == "likes late workouts"


def test_memory_text_falls_back_to_content() -> None:
    assert _memory_text({"content": "called the garage sensor flaky"}) == (
        "called the garage sensor flaky"
    )
