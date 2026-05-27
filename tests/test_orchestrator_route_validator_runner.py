from __future__ import annotations

from demo.run_orchestrator_route_validator import run_orchestrator_route_validator


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_route_validator_prints_all_required_scenarios():
    output = run_orchestrator_route_validator()

    assert "validator_allows_reflex_route" in output
    assert "validator_allows_general_route" in output
    assert "validator_allows_full_pipeline_with_guards" in output
    assert "validator_blocks_skip_avf" in output
    assert "validator_blocks_skip_plan_contract" in output
    assert "validator_blocks_orchestrator_final_output" in output
    assert "validator_requires_permission_for_purchase" in output
    assert "validator_allows_permission_after_confirmation_mock" in output
    assert "validator_blocks_direct_reuse_without_gate" in output
    assert "validator_allows_direct_reuse_when_eligible" in output


def test_route_validator_blocks_skip_avf():
    output = run_orchestrator_route_validator()

    assert "validator_blocks_skip_avf | proof_full_pipeline | deny | false" in output
    assert "cannot_skip_avf_when_forbidden_candidate_present" in output


def test_route_validator_blocks_skip_plan_contract():
    output = run_orchestrator_route_validator()

    assert "validator_blocks_skip_plan_contract | proof_full_pipeline | deny | false" in output
    assert "cannot_skip_plan_graph_contract" in output


def test_route_validator_blocks_orchestrator_final_output():
    output = run_orchestrator_route_validator()

    assert "validator_blocks_orchestrator_final_output | llm_general | deny | false" in output
    assert "orchestrator_cannot_create_final_output" in output


def test_route_validator_requires_permission_for_purchase():
    output = run_orchestrator_route_validator()

    assert "validator_requires_permission_for_purchase | permission_required | needs_user | false" in output
    assert "permission_required" in output
    assert "no real external action" in output


def test_route_validator_blocks_direct_reuse_without_gate():
    output = run_orchestrator_route_validator()

    assert "validator_blocks_direct_reuse_without_gate | direct_reuse | fallback_to_deterministic | false" in output
    assert "direct_reuse_requires_eligible_record" in output


def test_route_validator_allows_direct_reuse_when_eligible():
    output = run_orchestrator_route_validator()

    assert "validator_allows_direct_reuse_when_eligible | direct_reuse | allow_with_guards | true" in output
    assert "DirectReuseGate" in output
    assert "Freshness" in output
    assert "PolicyOK" in output
    assert "DRS writeback" in output


def test_route_validator_full_pipeline_requires_core_guards():
    output = run_orchestrator_route_validator()

    assert "validator_allows_full_pipeline_with_guards | proof_full_pipeline | allow_with_guards | true" in output
    assert "AVF" in output
    assert "HardMask" in output
    assert "PlanGraph contract" in output
    assert "Post V&V" in output
    assert "GT" in output


def test_route_validator_says_control_not_delegated():
    output = run_orchestrator_route_validator()

    assert "this does not delegate control yet" in output
    assert "controlled_orchestrator_enabled: false" in output
    assert "next_step: controlled orchestrator only after validator enforcement" in output
    assert "no live Gemini by default" in output


def test_route_validator_summary_counts():
    output = run_orchestrator_route_validator()

    assert "allowed: 1" in output
    assert "allowed_with_guards: 4" in output
    assert "denied: 3" in output
    assert "needs_user: 1" in output
    assert "fallback_to_deterministic: 1" in output


def test_route_validator_does_not_leak_sensitive_terms():
    output = run_orchestrator_route_validator()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
