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
    assert "reuse_gate decision: none" in output
    assert "reuse_gate reason: none" in output
    assert "reuse_applied:" in output
    assert "GT winner vector id: official_online_request" in output
    assert "GT winner vector id: fallback_exploration" not in output


def test_certificate_demo_reuse_output_uses_context_only_memory(tmp_path):
    output = run_demo("reuse", drs_root=tmp_path)

    assert "Scenario: reuse" in output
    assert "second_run:" in output
    assert "memory_context_applied: true" in output
    assert "reuse_decision: context_only" in output
    assert "reuse_gate decision: context_only" in output
    assert "reuse_gate reason:" in output
    assert "reuse_applied: false" in output
    assert "reuse_applied:" in output
    assert "direct reuse implemented: false" in output
    assert "GT winner vector id: official_online_request" in output
    assert "GT winner vector id: fallback_exploration" not in output


def test_certificate_demo_direct_reuse_output_shows_shortcut(tmp_path):
    output = run_demo("direct_reuse", drs_root=tmp_path)

    assert "Scenario: direct_reuse" in output
    assert "retrieved_record_count: 1" in output
    assert "memory_context_applied: true" in output
    assert "reuse_decision: direct_reuse" in output
    assert "reuse_applied: true" in output
    assert "reuse_gate decision: direct_reuse_candidate" in output
    assert "reuse_candidate_record_id: work:demo_direct_reuse_source" in output
    assert "reused_record_ids: work:demo_direct_reuse_source" in output
    assert "architect_skipped: true" in output
    assert "executor_skipped: true" in output
    assert "PlanGraph node count: 0" in output
    assert "ResultProposal count: 0" in output
    assert "FinalOutput created_by: root_orchestrator" in output
    assert "FinalOutput status: success" in output
    assert "DRS writes: work:demo_direct_reuse_001" in output


def test_certificate_demo_mock_llm_architect_output_shows_safe_architect_path(tmp_path):
    output = run_demo("mock_llm_architect", drs_root=tmp_path)

    assert "Scenario: mock_llm_architect" in output
    assert "architect_provider: mock" in output
    assert "llm_architect status: completed" in output
    assert "llm_architect used_llm: false" in output
    assert "PlanGraph node count:" in output
    assert "ResultProposal count:" in output
    assert "FinalOutput created_by: root_orchestrator" in output
    assert "FinalOutput status:" in output


def test_certificate_demo_gemini_architect_scenario_is_registered_with_safe_failure(tmp_path):
    output = run_demo("gemini_architect", drs_root=tmp_path)

    assert "Scenario: gemini_architect" in output
    assert "architect_provider: gemini" in output
    assert "llm_architect status:" in output
    assert "FinalOutput created_by: root_orchestrator" in output
    if "llm_architect status: error" in output:
        assert "llm_architect fallback: deterministic" in output
        assert "llm_architect error:" in output
    assert "api_key" not in output.lower()
    assert "token" not in output.lower()


def test_certificate_demo_output_does_not_print_raw_text_or_secret_terms(tmp_path):
    output = run_demo("reuse", drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_OUTPUT_TERMS:
        assert term not in lowered


def test_certificate_demo_trace_report_flag_appends_human_report(tmp_path):
    output = run_demo("cold_start", drs_root=tmp_path, trace_report=True)

    assert "Scenario: cold_start" in output
    assert "[ROOT]" in output
    assert "[ARCHITECT]" in output
    assert "[FINAL]" in output
