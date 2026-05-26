from demo.run_scenario_benchmarks import run_benchmarks


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
}


def test_benchmark_runner_returns_required_scenarios(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "l0_reflex_turn_on_tv" in output
    assert "l1_direct_reuse_certificate" in output
    assert "l3_l4_controlled_architect_certificate" in output
    assert "gt_v02_primary_beats_fallback" in output
    assert "safety_forbidden_vector_blocked" in output
    assert "memory_first_reuse_second_run" in output
    assert "memory_first_direct_reuse_second_run" in output
    assert "permissioned_mock_action_blocked_without_confirm" in output
    assert "permissioned_mock_action_success_after_confirm" in output
    assert "architect_contract_violation_recovered" in output
    assert "economics_routing_simulation" in output


def test_benchmark_controlled_scenarios_pass_without_live_gemini(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "l0_reflex_turn_on_tv | PASS" in output
    assert "l1_direct_reuse_certificate | PASS" in output
    assert "l3_l4_controlled_architect_certificate | PASS" in output
    assert "gt_v02_primary_beats_fallback | PASS" in output
    assert "safety_forbidden_vector_blocked | PASS" in output
    assert "memory_first_reuse_second_run | PASS" in output
    assert "memory_first_direct_reuse_second_run | PASS" in output
    assert "permissioned_mock_action_blocked_without_confirm | PASS" in output
    assert "permissioned_mock_action_success_after_confirm | PASS" in output
    assert "architect_contract_violation_recovered | PASS" in output
    assert "economics_routing_simulation | PASS" in output
    assert "gemini_architect_live_smoke | SKIPPED" in output


def test_benchmark_output_includes_compact_table(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "[SCENARIO BENCHMARKS]" in output
    assert "scenario | status | route | llm_used | reuse_applied | permission_required | forbidden_blocked | gt_winner | drs_write | trace_path | key_assertions" in output
    assert "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---" in output


def test_benchmark_output_includes_gt_v02_and_primary_beats_fallback(tmp_path):
    output = run_benchmarks(drs_root=tmp_path, trace_report=True)

    assert "gt_payoff_v0_2" in output
    assert "official payoff beats fallback" in output
    assert "fallback penalty present" in output
    assert "official vector bonus present" in output
    assert "official_online_request" in output
    assert "fallback_exploration" in output


def test_benchmark_output_confirms_forbidden_vector_blocked(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "illegal_coercion blocked" in output
    assert "illegal_coercion not winner" in output
    assert "FinalOutput root only" in output


def test_benchmark_output_does_not_contain_sensitive_terms(tmp_path):
    output = run_benchmarks(drs_root=tmp_path, trace_report=True)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def test_live_gemini_scenario_is_skipped_by_default(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "gemini_architect_live_smoke | SKIPPED" in output
    assert "live_gemini: false" in output


def test_benchmark_trace_report_adds_trace_sections(tmp_path):
    output = run_benchmarks(drs_root=tmp_path, trace_report=True)

    assert "[ROOT]" in output
    assert "[GT_PAYOFF]" in output
    assert "[FINAL]" in output


def test_benchmark_output_includes_memory_and_permission_wow_scenarios(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "memory_first_reuse_second_run | PASS | context_only" in output
    assert "memory_first_direct_reuse_second_run | PASS | direct_reuse | false | true" in output
    assert "direct reuse eligible" in output
    assert "direct_reuse_applied true" in output
    assert "architect skipped" in output
    assert "executor skipped" in output
    assert "reused prior work record" in output
    assert "compute saved" in output
    assert "permissioned_mock_action_blocked_without_confirm | PASS | deterministic_reflex | false | false | true" in output
    assert "permission reason confirmation_required" in output
    assert "permissioned_mock_action_success_after_confirm | PASS | deterministic_reflex | false | false | true" in output
    assert "permission reason allowed" in output


def test_benchmark_output_includes_contract_recovery_and_economics(tmp_path):
    output = run_benchmarks(drs_root=tmp_path, trace_report=True)

    assert "architect_contract_violation_recovered | PASS" in output
    assert "invalid contract rejected" in output
    assert "deterministic recovery ran" in output
    assert "economics_routing_simulation | PASS | adaptive_simulation" in output
    assert "L0 cheapest deterministic path" in output
    assert "L1 direct reuse skips plan" in output
    assert "L3L4 pays planning cost only when needed" in output


def test_benchmark_distinguishes_context_memory_from_direct_reuse(tmp_path):
    output = run_benchmarks(drs_root=tmp_path)

    assert "memory_first_reuse_second_run | PASS | context_only | false | false" in output
    assert "memory_first_direct_reuse_second_run | PASS | direct_reuse | false | true" in output
