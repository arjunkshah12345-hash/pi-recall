from pi_memory_assistant.config import load_settings


def test_load_settings_parses_defaults(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")
    monkeypatch.setenv("SUPERMEMORY_LOCAL_KEY", "sm-local-key")
    monkeypatch.setenv("COMPOSIO_TOOLKITS", "GITHUB, Gmail,")
    monkeypatch.delenv("INPUT_DEVICE", raising=False)
    monkeypatch.delenv("OUTPUT_DEVICE", raising=False)

    settings = load_settings()

    assert settings.groq_api_key == "groq-key"
    assert settings.supermemory_local_key == "sm-local-key"
    assert settings.supermemory_local_url == "http://localhost:6767"
    assert settings.composio_toolkits == ("GITHUB", "Gmail")
    assert settings.input_device is None
    assert settings.output_device is None


def test_load_settings_can_skip_required_env_for_doctor(monkeypatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("SUPERMEMORY_LOCAL_KEY", raising=False)

    settings = load_settings(require_required=False)

    assert settings.groq_api_key == ""
    assert settings.supermemory_local_key == ""
