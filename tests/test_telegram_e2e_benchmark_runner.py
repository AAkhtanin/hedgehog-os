from demo.run_telegram_e2e_benchmarks import run_telegram_e2e_benchmarks


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
}


def test_telegram_e2e_benchmark_returns_required_default_scenarios(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_general_math_mock" in output
    assert "telegram_l0_reflex_turn_on_tv" in output
    assert "telegram_certificate_request_controlled" in output
    assert "telegram_debug_trace_visible" in output
    assert "telegram_no_secret_leak" in output
    assert "telegram_response_length_safe" in output


def test_telegram_e2e_default_does_not_call_live_gemini(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "live_gemini: false" in output
    assert "telegram_general_math_gemini_optional | SKIPPED" in output


def test_telegram_general_math_mock_scenario_passes(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_general_math_mock | PASS | llm_general | mock | false | success" in output
    assert "execution_mode llm_general" in output
    assert "route llm_general" in output
    assert "debug has llm_status" in output
    assert "debug has llm_provider" in output
    assert "debug has trace_path" in output


def test_telegram_l0_reflex_scenario_passes(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_l0_reflex_turn_on_tv | PASS | deterministic_reflex" in output
    assert "reflex_applied true" in output
    assert "architect_skipped true" in output
    assert "executor_skipped true" in output


def test_telegram_certificate_controlled_scenario_passes(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path, trace_report=True)

    assert "telegram_certificate_request_controlled | PASS | proof_full_pipeline" in output
    assert "AVF selected official_online_request" in output
    assert "illegal_coercion blocked" in output
    assert "GT decision accept" in output
    assert "GT payoff formula gt_payoff_v0_2" in output
    assert "GT winner vector official_online_request" in output
    assert "[GT_PAYOFF]" in output


def test_telegram_debug_trace_fields_are_visible(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_debug_trace_visible | PASS" in output
    assert "debug has request_id" in output
    assert "debug has execution_mode" in output
    assert "debug has route" in output
    assert "debug has final_status" in output
    assert "debug has gt_decision" in output
    assert "debug has trace_path" in output
    assert "debug has llm_status" in output


def test_telegram_e2e_output_does_not_contain_sensitive_terms(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path, trace_report=True)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def test_telegram_live_gemini_scenario_is_skipped_by_default(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_general_math_gemini_optional | SKIPPED" in output
    assert "SKIPPED live Gemini is disabled" in output


def test_telegram_response_length_safety_is_checked(tmp_path):
    output = run_telegram_e2e_benchmarks(drs_root=tmp_path)

    assert "telegram_response_length_safe | PASS" in output
    assert "response length safe" in output
