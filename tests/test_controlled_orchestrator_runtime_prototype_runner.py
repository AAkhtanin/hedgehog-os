from __future__ import annotations

from demo.run_controlled_orchestrator_runtime_prototype import (
    run_controlled_orchestrator_runtime_prototype,
)


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_runtime_prototype_prints_all_required_scenarios():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_full_pipeline_eligible_executes" in output
    assert "controlled_full_pipeline_incomplete_guards_blocked" in output
    assert "controlled_wrong_route_blocked" in output
    assert "controlled_permission_needs_user_blocked" in output
    assert "controlled_direct_reuse_eligible_executes_reuse" in output
    assert "controlled_direct_reuse_not_eligible_blocked_or_fallback" in output
    assert "controlled_orchestrator_final_output_blocked" in output


def test_eligible_full_pipeline_executes_through_root():
    output = run_controlled_orchestrator_runtime_prototype()

    assert (
        "controlled_full_pipeline_eligible_executes | proof_full_pipeline | "
        "eligible_for_controlled_dry_run | true | true | true | "
        "proof_full_pipeline | proof_full_pipeline | success | true"
    ) in output


def test_eligible_full_pipeline_does_not_skip_architect_or_executor():
    output = run_controlled_orchestrator_runtime_prototype()

    row = next(
        line
        for line in output.splitlines()
        if line.startswith("controlled_full_pipeline_eligible_executes")
    )
    assert " | false | false | false | " in row


def test_incomplete_guards_are_blocked():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_full_pipeline_incomplete_guards_blocked | proof_full_pipeline | not_eligible_incomplete_guards | false | false | false" in output
    assert "required guards are incomplete" in output


def test_wrong_route_blocked():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_wrong_route_blocked | llm_general | not_eligible_route_mismatch | false | false | false" in output


def test_permission_needs_user_blocked_without_external_action():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_permission_needs_user_blocked | permission_required | not_eligible_needs_user | false | false | false" in output
    assert "no real external actions" in output


def test_direct_reuse_eligible_executes_reuse():
    output = run_controlled_orchestrator_runtime_prototype()

    assert (
        "controlled_direct_reuse_eligible_executes_reuse | direct_reuse | "
        "eligible_for_controlled_dry_run | true | true | true | "
        "direct_reuse | direct_reuse | success | true | true | true | true"
    ) in output


def test_direct_reuse_not_eligible_does_not_apply_reuse():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_direct_reuse_not_eligible_blocked_or_fallback | direct_reuse | not_eligible_validator_denied | false | false | false" in output
    row = next(
        line
        for line in output.splitlines()
        if line.startswith("controlled_direct_reuse_not_eligible_blocked_or_fallback")
    )
    assert row.split(" | ")[12] == "false"


def test_orchestrator_final_output_blocked():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "controlled_orchestrator_final_output_blocked | llm_general | not_eligible_orchestrator_final_output | false | false | false" in output
    assert "Orchestrator may not create FinalOutput" in output


def test_every_executed_scenario_has_root_final_authority():
    output = run_controlled_orchestrator_runtime_prototype()

    for line in output.splitlines():
        if line.startswith("controlled_") and " | true | true | true | " in line:
            assert " | success | true | " in line
    assert "root_final_authority_all_executed: true" in output


def test_runtime_prototype_notes_control_boundaries():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "Orchestrator does not directly control runtime" in output
    assert "Orchestrator cannot create FinalOutput" in output
    assert "no live Gemini by default" in output
    assert "uncontrolled_delegation: false" in output
    assert "controlled_orchestrator_enabled: prototype_only" in output


def test_runtime_prototype_summary_counts():
    output = run_controlled_orchestrator_runtime_prototype()

    assert "eligible: 2" in output
    assert "executed: 2" in output
    assert "blocked: 5" in output
    assert "fallback_or_skipped: 5" in output


def test_runtime_prototype_does_not_leak_sensitive_terms():
    output = run_controlled_orchestrator_runtime_prototype()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
