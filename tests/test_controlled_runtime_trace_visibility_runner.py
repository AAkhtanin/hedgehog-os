from __future__ import annotations

from demo.run_controlled_runtime_trace_visibility import (
    run_controlled_runtime_trace_visibility,
)


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_trace_visibility_prints_all_required_scenarios():
    output = run_controlled_runtime_trace_visibility()

    assert "[CONTROLLED RUNTIME TRACE VISIBILITY]" in output
    assert "[TRACE] controlled_full_pipeline_eligible_executes" in output
    assert "[TRACE] controlled_full_pipeline_incomplete_guards_blocked" in output
    assert "[TRACE] controlled_wrong_route_blocked" in output
    assert "[TRACE] controlled_permission_needs_user_blocked" in output
    assert "[TRACE] controlled_direct_reuse_eligible_executes_reuse" in output
    assert "[TRACE] controlled_direct_reuse_not_eligible_blocked_or_fallback" in output
    assert "[TRACE] controlled_orchestrator_final_output_blocked" in output


def test_full_pipeline_eligible_verdict_executed_by_root():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_full_pipeline_eligible_executes")

    assert "PROPOSAL: proposed_route=proof_full_pipeline; expected_route=proof_full_pipeline" in block
    assert "VALIDATOR: allow_with_guards; allowed=true" in block
    assert "GUARDS: route_correct=true; guards_complete=true; score=1.00" in block
    assert "GATE: eligible_for_controlled_dry_run; eligible=true" in block
    assert "ROOT: executed=true; mode=proof_full_pipeline; route=proof_full_pipeline; final_status=success; root_final_authority=true" in block
    assert "VERDICT: PASS_EXECUTED_BY_ROOT" in block


def test_incomplete_guards_verdict_blocked_by_gate():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_full_pipeline_incomplete_guards_blocked")

    assert "guards_complete=false" in block
    assert "missing=HardMask, PlanGraph contract, Post V&V, GT, Root final authority" in block
    assert "GATE: not_eligible_incomplete_guards; eligible=false" in block
    assert "ROOT: executed=false" in block
    assert "VERDICT: PASS_BLOCKED_BY_GATE" in block


def test_wrong_route_verdict_blocked_by_gate():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_wrong_route_blocked")

    assert "route_correct=false" in block
    assert "GATE: not_eligible_route_mismatch; eligible=false" in block
    assert "VERDICT: PASS_BLOCKED_BY_GATE" in block


def test_needs_user_verdict_blocked():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_permission_needs_user_blocked")

    assert "VALIDATOR: needs_user; allowed=false" in block
    assert "GATE: not_eligible_needs_user; eligible=false" in block
    assert "VERDICT: PASS_NEEDS_USER_BLOCKED" in block
    assert "no_real_external_action=true" in block


def test_direct_reuse_eligible_verdict_executed_by_root():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_direct_reuse_eligible_executes_reuse")

    assert "ROOT: executed=true; mode=direct_reuse; route=direct_reuse; final_status=success; root_final_authority=true" in block
    assert "reuse_applied=true" in block
    assert "direct_reuse_applied=true" in block
    assert "VERDICT: PASS_DIRECT_REUSE_EXECUTED_BY_ROOT" in block


def test_direct_reuse_not_eligible_is_blocked_and_does_not_apply_reuse():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_direct_reuse_not_eligible_blocked_or_fallback")

    assert "GATE: not_eligible_validator_denied; eligible=false" in block
    assert "ROOT: executed=false" in block
    assert "reuse_applied=false" in block
    assert "direct_reuse_applied=false" in block
    assert "VERDICT: PASS_BLOCKED_BY_GATE" in block


def test_orchestrator_final_output_blocked():
    output = run_controlled_runtime_trace_visibility()
    block = _block(output, "controlled_orchestrator_final_output_blocked")

    assert "authority=orchestrator" in block
    assert "GATE: not_eligible_orchestrator_final_output; eligible=false" in block
    assert "ROOT: executed=false" in block
    assert "VERDICT: PASS_BLOCKED_BY_GATE" in block


def test_trace_visibility_summary():
    output = run_controlled_runtime_trace_visibility()

    assert "traces: 7" in output
    assert "executed_by_root: 1" in output
    assert "blocked_by_gate: 4" in output
    assert "needs_user_blocked: 1" in output
    assert "direct_reuse_executed: 1" in output
    assert "unexpected_execution: 0" in output
    assert "root_authority_failures: 0" in output
    assert "uncontrolled_delegation: false" in output
    assert "controlled_orchestrator_enabled: prototype_only" in output


def test_trace_visibility_does_not_leak_sensitive_terms():
    output = run_controlled_runtime_trace_visibility()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def _block(output: str, scenario: str) -> str:
    marker = f"[TRACE] {scenario}"
    start = output.index(marker)
    next_start = output.find("[TRACE] ", start + len(marker))
    if next_start == -1:
        next_start = output.index("SUMMARY:")
    return output[start:next_start]
