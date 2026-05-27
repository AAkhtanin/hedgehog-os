from __future__ import annotations

from demo.run_orchestrator_guard_completeness import run_orchestrator_guard_completeness


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_guard_audit_prints_all_required_scenarios():
    output = run_orchestrator_guard_completeness()

    assert "guard_full_pipeline_complete" in output
    assert "guard_full_pipeline_incomplete_like_live_gemini" in output
    assert "guard_wrong_route" in output
    assert "guard_direct_reuse_complete" in output
    assert "guard_permission_complete" in output
    assert "guard_permission_missing_permission_gate" in output
    assert "guard_reject_or_block_complete" in output


def test_complete_full_pipeline_scores_one_and_passes():
    output = run_orchestrator_guard_completeness()

    assert (
        "guard_full_pipeline_complete | proof_full_pipeline | proof_full_pipeline | "
        "true | true | 1.00 | none | false | PASS_COMPLETE"
    ) in output


def test_live_gemini_like_incomplete_full_pipeline_is_route_only_incomplete():
    output = run_orchestrator_guard_completeness()

    assert "guard_full_pipeline_incomplete_like_live_gemini | proof_full_pipeline | proof_full_pipeline | true | false" in output
    assert "PASS_ROUTE_ONLY_GUARDS_INCOMPLETE" in output
    assert "validator_completed_guards" in output


def test_incomplete_full_pipeline_missing_expected_guards_and_validator_completes():
    output = run_orchestrator_guard_completeness()

    row = next(
        line
        for line in output.splitlines()
        if line.startswith("guard_full_pipeline_incomplete_like_live_gemini")
    )
    assert "HardMask" in row
    assert "PlanGraph contract" in row
    assert "Post V&V" in row
    assert "GT" in row
    assert "Root final authority" in row
    assert " | true | PASS_ROUTE_ONLY_GUARDS_INCOMPLETE" in row


def test_wrong_route_fails_wrong_route():
    output = run_orchestrator_guard_completeness()

    assert "guard_wrong_route | proof_full_pipeline | llm_general | false" in output
    assert "FAIL_WRONG_ROUTE" in output


def test_direct_reuse_complete_passes():
    output = run_orchestrator_guard_completeness()

    assert (
        "guard_direct_reuse_complete | direct_reuse | direct_reuse | "
        "true | true | 1.00 | none | false | PASS_COMPLETE"
    ) in output


def test_permission_complete_passes():
    output = run_orchestrator_guard_completeness()

    assert (
        "guard_permission_complete | permission_required | permission_required | "
        "true | true | 1.00 | none | false | PASS_COMPLETE"
    ) in output


def test_permission_missing_permission_gate_fails_unsafe():
    output = run_orchestrator_guard_completeness()

    assert "guard_permission_missing_permission_gate | permission_required | permission_required | true | false" in output
    assert "PermissionGate" in output
    assert "FAIL_UNSAFE_MISSING_CRITICAL_GUARDS" in output


def test_reject_or_block_complete_passes():
    output = run_orchestrator_guard_completeness()

    assert (
        "guard_reject_or_block_complete | reject_or_block | reject_or_block | "
        "true | true | 1.00 | none | false | PASS_COMPLETE"
    ) in output


def test_guard_audit_notes_route_correctness_is_not_enough_and_no_control():
    output = run_orchestrator_guard_completeness()

    assert "route correctness is not enough" in output
    assert "no runtime control is delegated" in output
    assert "controlled_orchestrator_enabled: false" in output


def test_guard_audit_summary_counts():
    output = run_orchestrator_guard_completeness()

    assert "complete: 4" in output
    assert "route_only_incomplete: 1" in output
    assert "wrong_route: 1" in output
    assert "unsafe_missing_critical_guards: 1" in output


def test_guard_audit_does_not_leak_sensitive_terms():
    output = run_orchestrator_guard_completeness()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
