from __future__ import annotations

import subprocess
import sys

import demo.run_fractal_cell_runtime_integration_v01 as runner
import hedgehog.fractal_cell_integration as integration
from hedgehog.bounded_actor_contracts import ActorInputEnvelope, ActorOutputEnvelope
from hedgehog.fractal_cell_integration import (
    FractalCellBoundary,
    FractalCellBoundaryReport,
    FractalCellInput,
    FractalCellResult,
    FractalCellTrace,
    build_fractal_cell_boundary_report,
    make_default_fractal_cell_input,
    run_bounded_fractal_cell,
    validate_child_actor_transition,
    validate_fractal_cell_input,
    validate_fractal_cell_output,
)


def _child_transition(
    role: str,
    input_kind: str,
    output_kind: str,
    target_boundary: str,
    *,
    source_boundary: str,
    root_shaped_task: bool = False,
    plan_graph_ref: str | None = None,
    result_proposal_ref: str | None = None,
):
    return validate_child_actor_transition(
        ActorInputEnvelope(
            role=role,
            input_kind=input_kind,
            source_boundary=source_boundary,
            payload_ref=f"payload:test:{role}:input",
            root_shaped_task=root_shaped_task,
            plan_graph_ref=plan_graph_ref,
            result_proposal_ref=result_proposal_ref,
        ),
        ActorOutputEnvelope(
            role=role,
            output_kind=output_kind,
            payload_ref=f"payload:test:{role}:output",
        ),
        target_boundary=target_boundary,
        transition_id=f"test:{role}:{target_boundary}",
    )


def test_module_imports_and_api_symbols_exist() -> None:
    assert integration.FractalCellInput is FractalCellInput
    assert integration.FractalCellBoundary is FractalCellBoundary
    assert integration.FractalCellResult is FractalCellResult
    assert integration.FractalCellTrace is FractalCellTrace
    assert integration.FractalCellBoundaryReport is FractalCellBoundaryReport
    assert callable(integration.validate_fractal_cell_input)
    assert callable(integration.run_bounded_fractal_cell)
    assert callable(integration.validate_fractal_cell_output)
    assert callable(integration.build_fractal_cell_boundary_report)


def test_validate_fractal_cell_input_rejects_child_root_claimed() -> None:
    check = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:test",
            root_shaped_task_ref="root_task:test",
            plan_graph_ref="plan:test",
            child_root_claimed=True,
        )
    )

    assert check.blocked is True
    assert "child_root_claim_blocked" in check.reason_codes


def test_validate_fractal_cell_input_rejects_network_gemini_external_action() -> None:
    check = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:test",
            root_shaped_task_ref="root_task:test",
            plan_graph_ref="plan:test",
            network_allowed=True,
            gemini_allowed=True,
            external_action_allowed=True,
        )
    )

    assert check.blocked is True
    assert "network_forbidden" in check.reason_codes
    assert "gemini_forbidden" in check.reason_codes
    assert "external_action_forbidden" in check.reason_codes


def test_validate_fractal_cell_input_enforces_depth_limits() -> None:
    too_deep = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=3, max_cell_depth=2)
    )
    invalid_max = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=1, max_cell_depth=0)
    )
    invalid_children = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:test",
            root_shaped_task_ref="root_task:test",
            plan_graph_ref="plan:test",
            max_child_cells_per_parent=0,
        )
    )

    assert too_deep.blocked is True
    assert "recursive_depth_limit_exceeded" in too_deep.reason_codes
    assert "max_cell_depth_invalid" in invalid_max.reason_codes
    assert "max_child_cells_invalid" in invalid_children.reason_codes


def test_validate_fractal_cell_output_rejects_finaloutput_action_root_claims() -> None:
    result = FractalCellResult(
        cell_id="cell:test",
        parent_cell_id="parent_cell:test",
        child_result_proposal_ref="rp:test",
        child_validation_report_ref="vv:test",
        child_gt_advisory_ref="gt:test",
        trace_refs=({"trace_id": "trace:test", "span_id": "span:test", "kind": "test"},),
        lineage_refs=({"parent_route_id": "route:test"},),
        reason_codes=("unsafe_claim_test",),
        final_output_claimed=True,
        action_permission_claimed=True,
        root_authority_claimed=True,
        child_root_claimed=True,
    )
    check = validate_fractal_cell_output(result)

    assert check.blocked is True
    assert "child_finaloutput_claim_blocked" in check.reason_codes
    assert "child_action_permission_claim_blocked" in check.reason_codes
    assert "child_root_authority_claim_blocked" in check.reason_codes
    assert "child_root_claim_blocked" in check.reason_codes


def test_run_bounded_fractal_cell_returns_bounded_result_and_report() -> None:
    run = run_bounded_fractal_cell(make_default_fractal_cell_input())
    result = run["result"]
    report = run["boundary_report"]

    assert run["status"] == "completed"
    assert isinstance(result, FractalCellResult)
    assert isinstance(report, FractalCellBoundaryReport)
    assert result.child_result_proposal_ref
    assert result.final_output_claimed is False
    assert result.action_permission_claimed is False
    assert result.root_authority_claimed is False
    assert report.final_output_created_count == 0
    assert report.action_permission_granted_count == 0
    assert report.root_final_authority_preserved is True


def test_forced_post_vv_fallback_is_review_required_not_accepted_authority(monkeypatch) -> None:
    monkeypatch.setattr(integration, "_runtime_validate_result_proposals", None)

    run = integration.run_bounded_fractal_cell(make_default_fractal_cell_input())
    fallback_report = run["vv_reports"][0]
    boundary_report = run["boundary_report"]

    assert fallback_report["status"] == "needs_revision"
    assert fallback_report["decision"] == "revise"
    assert "post_vv_runtime_unavailable_review_required" in {
        violation["violation_id"] for violation in fallback_report["violations"]
    }
    assert "post_vv_fallback_not_authority" in fallback_report["notes"]
    assert "child_output_requires_real_post_vv_or_root_review" in fallback_report["notes"]
    assert "post_vv_fallback_used_review_required" in boundary_report.reason_codes
    assert boundary_report.counters["post_vv_fallback_used_count"] == 1
    assert boundary_report.counters["final_output_created_count"] == 0
    assert boundary_report.counters["action_permission_granted_count"] == 0
    assert boundary_report.counters["child_authority_claimed_count"] == 0
    assert boundary_report.counters["child_finaloutput_claimed_count"] == 0
    assert boundary_report.counters["root_review_required_count"] >= 1
    assert boundary_report.counters["root_final_authority_preserved_count"] == 1
    assert boundary_report.root_final_authority_preserved is True


def test_normal_real_post_vv_path_still_passes() -> None:
    assert integration._runtime_validate_result_proposals is not None

    run = integration.run_bounded_fractal_cell(make_default_fractal_cell_input())
    boundary_report = run["boundary_report"]

    assert run["status"] == "completed"
    assert boundary_report.counters["post_vv_fallback_used_count"] == 0
    assert "post_vv_fallback_used_review_required" not in boundary_report.reason_codes
    assert boundary_report.root_final_authority_preserved is True


def test_child_actor_boundary_report_is_present_or_referenced() -> None:
    run = run_bounded_fractal_cell(make_default_fractal_cell_input())
    report = run["boundary_report"]

    assert run["actor_boundary_report"] is not None
    assert report.actor_boundary_report is not None
    assert report.actor_boundary_report_ref == run["actor_boundary_report"].report_id


def test_child_resultproposal_like_output_is_not_finaloutput() -> None:
    run = run_bounded_fractal_cell(make_default_fractal_cell_input())

    assert run["dag_runner_report"]["executor_created_final_output"] is False
    for proposal in run["dag_runner_report"]["result_proposals"]:
        assert "final_output" not in proposal
        assert "answer" not in proposal["result_payload"]


def test_child_output_returns_to_parent_root_boundary() -> None:
    run = run_bounded_fractal_cell(make_default_fractal_cell_input())
    report = run["boundary_report"]
    accepted_targets = {
        transition.target_boundary
        for transition in report.actor_boundary_report.accepted_transitions
    }

    assert "root_return" in accepted_targets
    assert "root_orchestrator" in accepted_targets
    assert report.parent_return_reports_count == 1


def test_child_architect_plangraph_to_final_output_is_blocked() -> None:
    check = _child_transition(
        "architect",
        "root_shaped_task",
        "plangraph_proposal",
        "final_output",
        source_boundary="root_orchestrator",
        root_shaped_task=True,
    )

    assert check.blocked is True
    assert "child_target_boundary_blocked" in check.reason_codes
    assert "final_output_target_boundary_blocked" in check.reason_codes


def test_child_executor_resultproposal_to_final_output_is_blocked() -> None:
    check = _child_transition(
        "executor",
        "bounded_plan_graph",
        "resultproposal_like",
        "final_output",
        source_boundary="child_architect",
        plan_graph_ref="plan:test",
    )

    assert check.blocked is True
    assert "child_target_boundary_blocked" in check.reason_codes
    assert "final_output_target_boundary_blocked" in check.reason_codes


def test_child_verifier_vvreport_to_final_output_is_blocked() -> None:
    check = _child_transition(
        "verifier",
        "resultproposal_like",
        "vv_report",
        "final_output",
        source_boundary="child_executor",
        result_proposal_ref="rp:test",
    )

    assert check.blocked is True
    assert "child_target_boundary_blocked" in check.reason_codes
    assert "final_output_target_boundary_blocked" in check.reason_codes


def test_child_gtreport_to_final_output_is_blocked() -> None:
    check = _child_transition(
        "gt_boundary",
        "vv_report",
        "gt_report",
        "final_output",
        source_boundary="child_verifier",
    )

    assert check.blocked is True
    assert "child_target_boundary_blocked" in check.reason_codes
    assert "final_output_target_boundary_blocked" in check.reason_codes


def test_child_gtreport_to_parent_architect_command_is_blocked() -> None:
    check = _child_transition(
        "gt_boundary",
        "vv_report",
        "gt_report",
        "parent_architect_command",
        source_boundary="child_verifier",
    )

    assert check.blocked is True
    assert "child_target_boundary_blocked" in check.reason_codes
    assert "parent_architect_command_blocked" in check.reason_codes


def test_recursive_depth_guard_works() -> None:
    accepted = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=2, max_cell_depth=2)
    )
    blocked = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=3, max_cell_depth=2)
    )

    assert accepted.accepted is True
    assert blocked.blocked is True
    assert "recursive_depth_limit_exceeded" in blocked.reason_codes


def test_child_consensus_does_not_create_authority() -> None:
    check = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:consensus",
            root_shaped_task_ref="root_task:consensus",
            plan_graph_ref="plan:consensus",
            child_consensus_claimed_authority=True,
            child_majority_claimed_authority=True,
            child_compute_volume_claimed_authority=True,
        )
    )

    assert check.blocked is True
    assert "child_consensus_authority_blocked" in check.reason_codes
    assert "child_majority_authority_blocked" in check.reason_codes
    assert "child_compute_volume_authority_blocked" in check.reason_codes


def test_runner_main_returns_zero() -> None:
    assert runner.main() == 0


def test_runner_command_exits_zero_and_outputs_required_markers() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_fractal_cell_runtime_integration_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    output = completed.stdout
    assert "FINAL STATUS: PASS" in output
    assert "scenarios_total: 12" in output
    assert "scenarios_passed: 12" in output
    assert "root_final_authority_preserved_count: 12" in output
    for scenario_id in runner.SCENARIOS:
        assert scenario_id in output


def test_runner_output_does_not_claim_production_public_or_complete_readiness() -> None:
    output = runner.render_report(runner.run_all_scenarios())
    blocked_phrases = (
        "production " + "ready",
        "public auditor " + "ready",
        "production Fractal Cell " + "implemented",
        "distributed runtime " + "implemented",
        "network used: " + "true",
        "Gemini " + "activated",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "public launch " + "ready",
        "whitepaper " + "ready",
    )

    for phrase in blocked_phrases:
        assert phrase not in output
