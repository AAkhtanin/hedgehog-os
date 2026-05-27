from __future__ import annotations

from demo.run_controlled_orchestrator_dry_run import run_controlled_orchestrator_dry_run


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_controlled_dry_run_prints_all_required_scenarios():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_reflex_allowed" in output
    assert "dryrun_general_allowed_with_guards" in output
    assert "dryrun_full_pipeline_allowed_with_guards" in output
    assert "dryrun_permission_needs_user" in output
    assert "dryrun_direct_reuse_allowed" in output
    assert "dryrun_direct_reuse_not_eligible_fallback" in output
    assert "dryrun_skip_avf_blocked" in output
    assert "dryrun_orchestrator_final_output_blocked" in output
    assert "dryrun_forbidden_reject_or_block" in output


def test_allow_maps_to_suggested_route():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_reflex_allowed | deterministic_reflex | allow | true | deterministic_reflex | false" in output


def test_allow_with_guards_maps_to_suggested_route():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_general_allowed_with_guards | llm_general | allow_with_guards | true | llm_general | false" in output
    assert "dryrun_full_pipeline_allowed_with_guards | proof_full_pipeline | allow_with_guards | true | proof_full_pipeline | false" in output
    assert "AVF" in output
    assert "HardMask" in output
    assert "PlanGraph contract" in output
    assert "Post V&V" in output
    assert "GT" in output


def test_needs_user_maps_to_needs_user():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_permission_needs_user | permission_required | needs_user | false | needs_user | false" in output
    assert "permission_required" in output


def test_fallback_maps_to_deterministic_route():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_direct_reuse_not_eligible_fallback | direct_reuse | fallback_to_deterministic | false | proof_full_pipeline | false" in output
    assert "Direct reuse not eligible" in output


def test_deny_maps_to_blocked():
    output = run_controlled_orchestrator_dry_run()

    assert "dryrun_skip_avf_blocked | proof_full_pipeline | deny | false | blocked | false" in output
    assert "cannot_skip_avf_when_forbidden_candidate_present" in output
    assert "dryrun_orchestrator_final_output_blocked | llm_general | deny | false | blocked | false" in output
    assert "orchestrator_cannot_create_final_output" in output
    assert "dryrun_forbidden_reject_or_block | reject_or_block | deny | false | blocked | false" in output
    assert "Safety block / no execution route" in output


def test_controlled_execution_performed_false_for_all_rows():
    output = run_controlled_orchestrator_dry_run()

    assert "controlled_execution_performed: false" in output
    assert " | true | " not in "\n".join(
        line for line in output.splitlines() if line.startswith("dryrun_") and "controlled_execution_performed" in line
    )
    assert output.count(" | false | ") >= 9


def test_dry_run_notes_runtime_unchanged_and_no_live_gemini():
    output = run_controlled_orchestrator_dry_run()

    assert "RootOrchestrator runtime is unchanged" in output
    assert "no live Gemini by default" in output
    assert "does not execute Orchestrator-selected routes" in output


def test_dry_run_summary_counts():
    output = run_controlled_orchestrator_dry_run()

    assert "would_execute_allowed: 4" in output
    assert "would_needs_user: 1" in output
    assert "would_fallback: 1" in output
    assert "would_block: 3" in output
    assert "next_step: controlled Orchestrator requires runtime integration and additional safety review" in output


def test_controlled_dry_run_does_not_leak_sensitive_terms():
    output = run_controlled_orchestrator_dry_run()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
