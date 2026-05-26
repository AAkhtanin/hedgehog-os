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
    assert "/math" in output
    assert "/certificate_mock" in output


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
    math = map_smoke_command("/math x + y = 110")
    certificate = map_smoke_command("/certificate_mock")

    assert reflex.allow_reflex is True
    assert reflex.force_full_pipeline is False
    assert math.force_full_pipeline is False
    assert certificate.force_full_pipeline is True


def test_smoke_output_redacts_sensitive_terms():
    output = render_dry_run(provider="mock", debug=True).lower()

    for term in FORBIDDEN_TERMS:
        assert term not in output
