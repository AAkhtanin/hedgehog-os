from __future__ import annotations

from demo.run_telegram_polling_smoke import (
    handle_smoke_text,
    map_smoke_command,
    render_dry_run,
)


FORBIDDEN_TERMS = {"api_key", "token", "raw_user_text"}


def _fake_shell(**kwargs):
    return {
        "reply_text": "reply",
        "debug_text": "[debug]\nexecution_mode: fake",
        "captured_kwargs": kwargs,
    }


def test_dry_run_prints_command_mappings_without_network():
    output = render_dry_run(provider="mock", debug=True)

    assert "[TELEGRAM POLLING SMOKE]" in output
    assert "dry_run: true" in output
    assert "network_called: false" in output
    assert "/reflex" in output
    assert "/ask" in output
    assert "/math" in output
    assert "/certificate_mock" in output
    assert "/certificate_gemini" in output
    assert "/controlled_gemini" in output


def test_dry_run_gemini_debug_shows_certificate_gemini_mapping():
    output = render_dry_run(provider="gemini", debug=True)

    assert "command | shell_text | force_full_pipeline | allow_reflex | llm_provider | architect_provider" in output
    assert "/certificate_gemini | mock certificate request | true | false | gemini | gemini" in output
    assert "/controlled_gemini | I need a government certificate. | true | false | gemini | gemini" in output
    assert "/ask | Explain why bicycles are useful for short city trips. | false | false | gemini | deterministic" in output
    assert "network_called: false" in output


def test_reflex_command_passes_allow_reflex_true():
    result = handle_smoke_text(
        text="/reflex turn on tv",
        provider="mock",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert result["shell_called"] is True
    assert kwargs["text"] == "turn on tv"
    assert kwargs["force_full_pipeline"] is False
    assert kwargs["allow_reflex"] is True
    assert kwargs["llm_provider"] == "mock"
    assert kwargs["architect_provider"] == "deterministic"


def test_math_command_uses_non_full_pipeline_and_selected_provider():
    result = handle_smoke_text(
        text="/math x + y = 110 / x - y = 100",
        provider="gemini",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert kwargs["text"] == "x + y = 110 / x - y = 100"
    assert kwargs["force_full_pipeline"] is False
    assert kwargs["allow_reflex"] is False
    assert kwargs["llm_provider"] == "gemini"
    assert kwargs["architect_provider"] == "deterministic"


def test_ask_command_uses_general_route_with_selected_provider():
    result = handle_smoke_text(
        text="/ask Explain in one paragraph why bicycles are useful.",
        provider="gemini",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert result["shell_called"] is True
    assert kwargs["text"] == "Explain in one paragraph why bicycles are useful."
    assert kwargs["force_full_pipeline"] is False
    assert kwargs["allow_reflex"] is False
    assert kwargs["llm_provider"] == "gemini"
    assert kwargs["architect_provider"] == "deterministic"


def test_ask_command_uses_mock_provider_when_selected():
    result = handle_smoke_text(
        text="/ask Explain a local concept.",
        provider="mock",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert kwargs["text"] == "Explain a local concept."
    assert kwargs["llm_provider"] == "mock"
    assert kwargs["force_full_pipeline"] is False


def test_empty_ask_returns_usage_without_shell_call():
    result = handle_smoke_text(
        text="/ask",
        provider="gemini",
        debug=True,
        shell_handler=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("shell called")),
    )

    assert result["shell_called"] is False
    assert result["reply_text"] == "Usage: /ask <general question or request>"
    assert "network_called: false" in result["debug_text"]


def test_certificate_mock_uses_full_pipeline_and_mock_provider():
    result = handle_smoke_text(
        text="/certificate_mock",
        provider="gemini",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert kwargs["text"] == "mock certificate request"
    assert kwargs["force_full_pipeline"] is True
    assert kwargs["allow_reflex"] is False
    assert kwargs["llm_provider"] == "mock"
    assert kwargs["architect_provider"] == "deterministic"


def test_certificate_gemini_uses_full_pipeline_with_gemini_architect_only():
    result = handle_smoke_text(
        text="/certificate_gemini",
        provider="mock",
        debug=True,
        shell_handler=_fake_shell,
    )
    kwargs = result["captured_kwargs"]

    assert kwargs["text"] == "mock certificate request"
    assert kwargs["force_full_pipeline"] is True
    assert kwargs["allow_reflex"] is False
    assert kwargs["llm_provider"] == "gemini"
    assert kwargs["architect_provider"] == "gemini"


def test_controlled_gemini_mapping_uses_selected_provider():
    mapping = map_smoke_command("/controlled_gemini", provider="gemini")

    assert mapping.command == "/controlled_gemini"
    assert mapping.shell_text == "I need a government certificate."
    assert mapping.force_full_pipeline is True
    assert mapping.allow_reflex is False
    assert mapping.llm_provider == "gemini"
    assert mapping.architect_provider == "gemini"
    assert mapping.controlled_smoke is True


def test_full_controlled_gemini_alias_maps_to_controlled_smoke():
    mapping = map_smoke_command("/full_controlled_gemini", provider="mock")

    assert mapping.command == "/full_controlled_gemini"
    assert mapping.shell_text == "I need a government certificate."
    assert mapping.llm_provider == "mock"
    assert mapping.architect_provider == "mock"
    assert mapping.controlled_smoke is True


def test_controlled_gemini_mock_mode_returns_controlled_debug():
    result = handle_smoke_text(
        text="/controlled_gemini",
        provider="mock",
        debug=True,
        shell_handler=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("shell called")),
    )

    assert result["shell_called"] is False
    assert result["controlled_smoke_called"] is True
    assert result["reply_text"] == "Controlled Gemini smoke completed."
    debug_text = result["debug_text"]
    assert "execution_mode: proof_full_pipeline" in debug_text
    assert "route: proof_full_pipeline" in debug_text
    assert "orchestrator_provider: mock" in debug_text
    assert "orchestrator_proposal_valid: true" in debug_text
    assert "suggested_route: proof_full_pipeline" in debug_text
    assert "guard_completeness_score: 1.00" in debug_text
    assert "guards_complete: true" in debug_text
    assert "integration_gate_decision: eligible_for_controlled_dry_run" in debug_text
    assert "controlled_execution_performed: true" in debug_text
    assert "architect_provider: mock" in debug_text
    assert "architect_llm_used: false" in debug_text
    assert "gt_decision: accept" in debug_text
    assert "final_status: success" in debug_text
    assert "root_final_authority: true" in debug_text
    assert "root_created_final_output: true" in debug_text
    assert "uncontrolled_delegation: false" in debug_text
    assert "no_real_external_action: true" in debug_text
    assert "drs_writes: 1" in debug_text
    assert "trace_path: none" in debug_text


def test_full_gemini_certificate_alias_maps_to_gemini_architect():
    mapping = map_smoke_command("/full_gemini certificate", provider="mock")

    assert mapping.command == "/full_gemini"
    assert mapping.shell_text == "mock certificate request"
    assert mapping.force_full_pipeline is True
    assert mapping.allow_reflex is False
    assert mapping.llm_provider == "gemini"
    assert mapping.architect_provider == "gemini"


def test_local_commands_do_not_call_shell():
    result = handle_smoke_text(
        text="/ping",
        provider="mock",
        debug=True,
        shell_handler=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("shell called")),
    )

    assert result["shell_called"] is False
    assert result["reply_text"] == "pong"
    assert "network_called: false" in result["debug_text"]


def test_mapping_keeps_root_transport_agnostic_flags_explicit():
    reflex = map_smoke_command("/reflex turn on tv")
    ask = map_smoke_command("/ask Explain this", provider="gemini")
    math = map_smoke_command("/math x + y = 110")
    certificate = map_smoke_command("/certificate_mock")
    certificate_gemini = map_smoke_command("/certificate_gemini")

    assert reflex.allow_reflex is True
    assert reflex.force_full_pipeline is False
    assert ask.force_full_pipeline is False
    assert ask.allow_reflex is False
    assert ask.llm_provider == "gemini"
    assert math.force_full_pipeline is False
    assert certificate.force_full_pipeline is True
    assert certificate_gemini.force_full_pipeline is True
    assert certificate_gemini.architect_provider == "gemini"


def test_smoke_output_redacts_sensitive_terms():
    output = render_dry_run(provider="mock", debug=True).lower()

    for term in FORBIDDEN_TERMS:
        assert term not in output
