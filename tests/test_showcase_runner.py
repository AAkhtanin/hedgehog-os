from demo.run_showcase import run_showcase


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
}


def test_showcase_controlled_architect_default_sections(tmp_path):
    output = run_showcase("controlled_architect", drs_root=tmp_path)

    assert "[SHOWCASE]" in output
    assert "scenario: controlled_architect" in output
    assert "[L0 REFLEX]" in output
    assert "[L1 DIRECT_REUSE]" in output
    assert "[L3_L4 ARCHITECT]" in output
    assert "[SAFETY]" in output
    assert "[STOCHASTIC ROLE TOPOLOGY]" in output
    assert "[SUMMARY]" in output


def test_showcase_default_is_mock_and_no_expensive_llm_calls(tmp_path):
    output = run_showcase("controlled_architect", drs_root=tmp_path)

    assert "architect_provider: mock_llm" in output
    assert "llm_architect used_llm: false" in output
    assert "- expensive_llm_calls: 0" in output
    assert "- deterministic_paths: 2" in output


def test_showcase_reports_safety_and_success(tmp_path):
    output = run_showcase("controlled_architect", drs_root=tmp_path)

    assert "illegal_coercion blocked: true" in output
    assert "executor_received_forbidden_vector: false" in output
    assert "sensitive_input_persisted: false" in output
    assert "FinalOutput status: success" in output
    assert "final_created_by: root_orchestrator" in output
    assert "- root_authority: true" in output
    assert "stochastic_roles_supported:" in output
    assert "current_demo_stochastic_roles_used:" in output
    assert "final_output_authority: RootOrchestrator only" in output
    assert "root_orchestrator_cognition:" in output
    assert "executor_cognition:" in output
    assert "nested_fractal_cells:" in output


def test_showcase_output_does_not_contain_sensitive_terms(tmp_path):
    output = run_showcase("controlled_architect", drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def test_showcase_trace_report_adds_trace_sections(tmp_path):
    output = run_showcase(
        "controlled_architect",
        drs_root=tmp_path,
        trace_report=True,
    )

    assert "[L0 REFLEX]" in output
    assert "[ROOT]" in output
    assert "[ARCHITECT]" in output
    assert "[FINAL]" in output
