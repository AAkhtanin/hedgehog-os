from __future__ import annotations

from demo.run_controlled_orchestrator_integration_gate import (
    run_controlled_orchestrator_integration_gate,
)


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_integration_gate_prints_all_scenarios():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_full_pipeline_complete_eligible" in output
    assert "gate_full_pipeline_incomplete_guards_not_eligible" in output
    assert "gate_wrong_route_not_eligible" in output
    assert "gate_validator_denied_not_eligible" in output
    assert "gate_needs_user_not_eligible" in output
    assert "gate_missing_root_authority_not_eligible" in output
    assert "gate_orchestrator_final_output_not_eligible" in output
    assert "gate_direct_reuse_eligible" in output
    assert "gate_direct_reuse_not_eligible" in output


def test_complete_full_pipeline_is_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert (
        "gate_full_pipeline_complete_eligible | proof_full_pipeline | "
        "allow_with_guards | true | true | 1.00 | true | "
        "eligible_for_controlled_dry_run | true | false"
    ) in output


def test_incomplete_guards_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_full_pipeline_incomplete_guards_not_eligible" in output
    assert "not_eligible_incomplete_guards" in output


def test_wrong_route_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_wrong_route_not_eligible | llm_general" in output
    assert "not_eligible_route_mismatch" in output


def test_validator_denied_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_validator_denied_not_eligible | proof_full_pipeline | deny" in output
    assert "not_eligible_validator_denied" in output


def test_needs_user_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_needs_user_not_eligible | permission_required | needs_user" in output
    assert "not_eligible_needs_user" in output


def test_missing_root_authority_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_missing_root_authority_not_eligible" in output
    assert "false | not_eligible_missing_root_authority | false" in output


def test_orchestrator_final_output_not_eligible():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_orchestrator_final_output_not_eligible" in output
    assert "not_eligible_orchestrator_final_output" in output


def test_direct_reuse_eligible_passes():
    output = run_controlled_orchestrator_integration_gate()

    assert (
        "gate_direct_reuse_eligible | direct_reuse | allow_with_guards | "
        "true | true | 1.00 | true | eligible_for_controlled_dry_run | true | false"
    ) in output


def test_direct_reuse_not_eligible_fails():
    output = run_controlled_orchestrator_integration_gate()

    assert "gate_direct_reuse_not_eligible | direct_reuse | fallback_to_deterministic" in output
    assert "not_eligible_validator_denied" in output
    assert "Direct reuse requires an eligible trusted memory record." in output


def test_controlled_execution_performed_false_for_all_rows():
    output = run_controlled_orchestrator_integration_gate()

    for line in output.splitlines():
        if line.startswith("gate_"):
            assert " | false | " in line or line.endswith(" | false")
    assert "controlled_execution_performed: false" in output


def test_integration_gate_notes_runtime_unchanged():
    output = run_controlled_orchestrator_integration_gate()

    assert "RootOrchestrator runtime is unchanged" in output
    assert "it does not execute controlled Orchestrator routes" in output
    assert "no live Gemini by default" in output
    assert "controlled_orchestrator_enabled: false" in output


def test_integration_gate_does_not_leak_sensitive_terms():
    output = run_controlled_orchestrator_integration_gate()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
