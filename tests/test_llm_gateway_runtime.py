from hedgehog.llm_gateway import (
    GENERAL_RESPONDER_SYSTEM_PROMPT,
    generate_general_answer,
)


def test_mock_provider_returns_deterministic_completed_math_result():
    result = generate_general_answer(
        text="x + y = 110\nx - y = 100",
        request_id="req_llm_mock_math",
        provider="mock",
    )

    assert result["status"] == "completed"
    assert result["provider"] == "mock"
    assert result["model"] == "mock_general_responder_v1"
    assert result["used_llm"] is False
    assert result["answer"] == "x = 105\ny = 5"
    assert result["error"] is None


def test_mock_provider_returns_general_response_for_unknown_text():
    result = generate_general_answer(
        text="Explain the idea in one sentence.",
        request_id="req_llm_mock_general",
        provider="mock",
    )

    assert result["status"] == "completed"
    assert "GeneralResponder" in result["answer"]
    assert result["used_llm"] is False


def test_gemini_provider_without_key_or_dependency_returns_error_not_crash(monkeypatch):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    result = generate_general_answer(
        text="hello",
        request_id="req_llm_gemini_missing",
        provider="gemini",
        allow_config=False,
    )

    assert result["status"] == "error"
    assert result["provider"] == "gemini"
    assert result["used_llm"] is False
    assert result["error"]
    assert "missing" in result["error"].lower() or "unavailable" in result["error"].lower()


def test_general_responder_system_prompt_preserves_root_authority():
    assert "You are not the RootOrchestrator" in GENERAL_RESPONDER_SYSTEM_PROMPT
    assert "You do not create FinalOutput" in GENERAL_RESPONDER_SYSTEM_PROMPT
