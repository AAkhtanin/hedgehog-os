from demo.run_certificate_demo import run_demo


FORBIDDEN_OUTPUT_TERMS = {
    "raw_user_text",
    "credential",
    "credentials",
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "private_key",
}


def test_certificate_demo_cold_start_output_contains_required_trace(tmp_path):
    output = run_demo("cold_start", drs_root=tmp_path)

    assert "Scenario: cold_start" in output
    assert "FinalOutput created_by: root_orchestrator" in output
    assert "illegal_coercion blocked: true" in output
    assert "GT winner vector id: official_online_request" in output
    assert "GT winner vector id: fallback_exploration" not in output


def test_certificate_demo_reuse_output_uses_context_only_memory(tmp_path):
    output = run_demo("reuse", drs_root=tmp_path)

    assert "Scenario: reuse" in output
    assert "second_run:" in output
    assert "memory_context_applied: true" in output
    assert "reuse_decision: context_only" in output
    assert "reuse_applied: false" in output
    assert "direct reuse implemented: false" in output
    assert "GT winner vector id: official_online_request" in output
    assert "GT winner vector id: fallback_exploration" not in output


def test_certificate_demo_output_does_not_print_raw_text_or_secret_terms(tmp_path):
    output = run_demo("reuse", drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_OUTPUT_TERMS:
        assert term not in lowered
