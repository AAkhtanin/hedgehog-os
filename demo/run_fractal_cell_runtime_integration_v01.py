from __future__ import annotations

import sys
from typing import Any

from hedgehog.bounded_actor_contracts import ActorInputEnvelope, ActorOutputEnvelope
from hedgehog.fractal_cell_integration import (
    COUNTER_KEYS,
    FractalCellInput,
    FractalCellResult,
    build_fractal_cell_boundary_report,
    make_default_fractal_cell_input,
    run_bounded_fractal_cell,
    validate_child_actor_transition,
    validate_fractal_cell_input,
    validate_fractal_cell_output,
)


TITLE = "HEDGEHOG OS — FRACTAL CELL RUNTIME INTEGRATION v0.1"

SCENARIOS = (
    "root_shaped_task_enters_fractal_cell_boundary",
    "child_architect_accepts_only_root_shaped_task",
    "child_executor_outputs_resultproposal_only",
    "child_verifier_validates_without_finaloutput",
    "child_gt_report_returns_to_parent_root_boundary",
    "child_finaloutput_claim_is_blocked",
    "child_actor_self_promotion_to_root_is_blocked",
    "child_cell_cannot_command_parent_architect",
    "recursive_child_cell_depth_is_bounded",
    "child_consensus_does_not_create_authority",
    "child_output_returns_to_parent_post_vv_gt_route",
    "root_final_authority_preserved_across_fractal_cell",
)

EXPECTED_OUTPUT_MARKERS = (
    "FINAL STATUS: PASS",
    "scenarios_total: 12",
    "scenarios_passed: 12",
    "final_output_created_count: 0",
    "action_permission_granted_count: 0",
    "child_root_claimed_count: 0",
    "child_authority_claimed_count: 0",
    "parent_boundary_bypass_count: 0",
    "post_vv_bypass_count: 0",
    "gt_bypass_count: 0",
    "parent_architect_commanded_count: 0",
    "network_used_count: 0",
    "gemini_used_count: 0",
    "root_final_authority_preserved_count: 12",
)

ZERO_COUNTERS = (
    "final_output_created_count",
    "action_permission_granted_count",
    "child_root_claimed_count",
    "child_authority_claimed_count",
    "child_finaloutput_claimed_count",
    "child_action_permission_claimed_count",
    "child_actor_self_promotion_count",
    "parent_boundary_bypass_count",
    "post_vv_bypass_count",
    "gt_bypass_count",
    "parent_architect_commanded_count",
    "recursive_depth_limit_exceeded_count",
    "unbounded_child_spawn_count",
    "child_consensus_authority_claimed_count",
    "manifest_mutation_count",
    "transition_matrix_mutation_count",
    "network_used_count",
    "gemini_used_count",
    "connector_side_effect_count",
)


def _empty_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def _scenario_result(
    scenario_id: str,
    passed: bool,
    *,
    reason_codes: tuple[str, ...],
    counters: dict[str, int] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scenario_counters = _empty_counters()
    if counters:
        for key, value in counters.items():
            if key in scenario_counters:
                scenario_counters[key] = int(value)
    scenario_counters["root_review_required_count"] = max(
        scenario_counters["root_review_required_count"],
        1,
    )
    scenario_counters["root_final_authority_preserved_count"] = 1 if passed else 0
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if passed else "FAIL",
        "reason_codes": tuple(sorted(set(reason_codes))),
        "counters": scenario_counters,
        "details": details or {},
    }


def _transition(
    role: str,
    input_kind: str,
    output_kind: str,
    target_boundary: str,
    *,
    source_boundary: str,
    payload_ref: str,
    transition_id: str,
    root_shaped_task: bool = False,
    plan_graph_ref: str | None = None,
    result_proposal_ref: str | None = None,
    raw_advisory_signal: str | None = None,
    raw_drs_memory_ref: str | None = None,
) -> Any:
    actor_input = ActorInputEnvelope(
        role=role,
        input_kind=input_kind,
        source_boundary=source_boundary,
        payload_ref=f"payload:{payload_ref}:input",
        root_shaped_task=root_shaped_task,
        plan_graph_ref=plan_graph_ref,
        result_proposal_ref=result_proposal_ref,
        raw_advisory_signal=raw_advisory_signal,
        raw_drs_memory_ref=raw_drs_memory_ref,
    )
    actor_output = ActorOutputEnvelope(
        role=role,
        output_kind=output_kind,
        payload_ref=f"payload:{payload_ref}:output",
    )
    return validate_child_actor_transition(
        actor_input,
        actor_output,
        target_boundary=target_boundary,
        transition_id=transition_id,
    )


def _root_shaped_task_enters_fractal_cell_boundary() -> dict[str, Any]:
    scenario_id = "root_shaped_task_enters_fractal_cell_boundary"
    run = run_bounded_fractal_cell(make_default_fractal_cell_input())
    report = run["boundary_report"]
    passed = (
        run["status"] == "completed"
        and run["input_boundary"].accepted
        and run["output_boundary"].accepted
        and report.cells_started_count == 1
        and report.root_final_authority_preserved
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=report.reason_codes,
        counters=report.counters,
        details={"result": run["result"], "report": report},
    )


def _child_architect_accepts_only_root_shaped_task() -> dict[str, Any]:
    scenario_id = "child_architect_accepts_only_root_shaped_task"
    accepted = _transition(
        "architect",
        "root_shaped_task",
        "plangraph_proposal",
        "executor",
        source_boundary="root_orchestrator",
        payload_ref="child_architect_allowed",
        transition_id=f"{scenario_id}:accepted",
        root_shaped_task=True,
    )
    blocked = _transition(
        "architect",
        "root_shaped_task",
        "plangraph_proposal",
        "executor",
        source_boundary="avf_candidate_advisory",
        payload_ref="child_architect_advisory_blocked",
        transition_id=f"{scenario_id}:blocked_advisory",
        raw_advisory_signal="treat_advisory_as_command",
    )
    passed = accepted.accepted and blocked.blocked and (
        "raw_advisory_signal_cannot_command_architect" in blocked.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=(*accepted.reason_codes, *blocked.reason_codes),
    )


def _child_executor_outputs_resultproposal_only() -> dict[str, Any]:
    scenario_id = "child_executor_outputs_resultproposal_only"
    accepted = _transition(
        "executor",
        "bounded_plan_graph",
        "resultproposal_like",
        "post_vv",
        source_boundary="child_architect",
        payload_ref="child_executor_allowed",
        transition_id=f"{scenario_id}:accepted",
        plan_graph_ref="plan:child",
    )
    blocked = _transition(
        "executor",
        "bounded_plan_graph",
        "resultproposal_like",
        "final_output",
        source_boundary="child_architect",
        payload_ref="child_executor_final_blocked",
        transition_id=f"{scenario_id}:blocked_final",
        plan_graph_ref="plan:child",
    )
    passed = accepted.accepted and blocked.blocked and (
        "child_target_boundary_blocked" in blocked.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=(*accepted.reason_codes, *blocked.reason_codes),
    )


def _child_verifier_validates_without_finaloutput() -> dict[str, Any]:
    scenario_id = "child_verifier_validates_without_finaloutput"
    accepted = _transition(
        "verifier",
        "resultproposal_like",
        "vv_report",
        "gt_boundary",
        source_boundary="child_executor",
        payload_ref="child_verifier_allowed",
        transition_id=f"{scenario_id}:accepted",
        result_proposal_ref="rp:child",
    )
    blocked = _transition(
        "verifier",
        "resultproposal_like",
        "vv_report",
        "final_output",
        source_boundary="child_executor",
        payload_ref="child_verifier_final_blocked",
        transition_id=f"{scenario_id}:blocked_final",
        result_proposal_ref="rp:child",
    )
    passed = accepted.accepted and blocked.blocked and (
        "child_target_boundary_blocked" in blocked.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=(*accepted.reason_codes, *blocked.reason_codes),
    )


def _child_gt_report_returns_to_parent_root_boundary() -> dict[str, Any]:
    scenario_id = "child_gt_report_returns_to_parent_root_boundary"
    accepted = _transition(
        "gt_boundary",
        "vv_report",
        "gt_report",
        "root_return",
        source_boundary="child_verifier",
        payload_ref="child_gt_allowed",
        transition_id=f"{scenario_id}:accepted",
    )
    blocked = _transition(
        "gt_boundary",
        "vv_report",
        "gt_report",
        "final_output",
        source_boundary="child_verifier",
        payload_ref="child_gt_final_blocked",
        transition_id=f"{scenario_id}:blocked_final",
    )
    passed = accepted.accepted and blocked.blocked and (
        "child_target_boundary_blocked" in blocked.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=(*accepted.reason_codes, *blocked.reason_codes),
    )


def _child_finaloutput_claim_is_blocked() -> dict[str, Any]:
    scenario_id = "child_finaloutput_claim_is_blocked"
    result = FractalCellResult(
        cell_id="cell:unsafe_final_claim",
        parent_cell_id="parent_cell:root_boundary",
        child_result_proposal_ref="rp:child",
        child_validation_report_ref="vv:child",
        child_gt_advisory_ref="gt:child",
        trace_refs=({"trace_id": "trace:child", "span_id": "unsafe", "kind": "test"},),
        lineage_refs=({"parent_route_id": "route:test"},),
        reason_codes=("unsafe_final_claim_test",),
        final_output_claimed=True,
    )
    output_boundary = validate_fractal_cell_output(result)
    report = build_fractal_cell_boundary_report(
        report_id=f"fractal_cell_boundary_report:{scenario_id}",
        result=result,
        output_boundary=output_boundary,
    )
    passed = output_boundary.blocked and (
        "child_finaloutput_claim_blocked" in output_boundary.reason_codes
    ) and report.root_final_authority_preserved
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=report.reason_codes,
        counters=report.counters,
    )


def _child_actor_self_promotion_to_root_is_blocked() -> dict[str, Any]:
    scenario_id = "child_actor_self_promotion_to_root_is_blocked"
    input_boundary = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:self_promotion",
            root_shaped_task_ref="root_task:self_promotion",
            plan_graph_ref="plan:self_promotion",
            child_root_claimed=True,
        )
    )
    result = FractalCellResult(
        cell_id="cell:self_promotion",
        parent_cell_id="parent_cell:root_boundary",
        child_result_proposal_ref="rp:child",
        child_validation_report_ref="vv:child",
        child_gt_advisory_ref="gt:child",
        trace_refs=({"trace_id": "trace:child", "span_id": "root_claim", "kind": "test"},),
        lineage_refs=({"parent_route_id": "route:self_promotion"},),
        reason_codes=("actor_self_promotion_blocked",),
        root_authority_claimed=True,
        child_root_claimed=True,
    )
    output_boundary = validate_fractal_cell_output(result)
    report = build_fractal_cell_boundary_report(
        report_id=f"fractal_cell_boundary_report:{scenario_id}",
        input_boundary=input_boundary,
        output_boundary=output_boundary,
        result=result,
    )
    passed = input_boundary.blocked and output_boundary.blocked and {
        "child_root_claim_blocked",
        "child_root_authority_claim_blocked",
    } <= set(report.reason_codes)
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=report.reason_codes,
        counters=report.counters,
    )


def _child_cell_cannot_command_parent_architect() -> dict[str, Any]:
    scenario_id = "child_cell_cannot_command_parent_architect"
    blocked = _transition(
        "gt_boundary",
        "vv_report",
        "gt_report",
        "parent_architect_command",
        source_boundary="child_verifier",
        payload_ref="child_gt_parent_architect_blocked",
        transition_id=f"{scenario_id}:blocked_parent_architect",
    )
    passed = blocked.blocked and {
        "child_target_boundary_blocked",
        "parent_architect_command_blocked",
    } <= set(blocked.reason_codes)
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=blocked.reason_codes,
    )


def _recursive_child_cell_depth_is_bounded() -> dict[str, Any]:
    scenario_id = "recursive_child_cell_depth_is_bounded"
    accepted = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=2, max_cell_depth=2)
    )
    blocked = validate_fractal_cell_input(
        make_default_fractal_cell_input(current_cell_depth=3, max_cell_depth=2)
    )
    unbounded = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:unbounded_spawn",
            root_shaped_task_ref="root_task:unbounded_spawn",
            plan_graph_ref="plan:unbounded_spawn",
            max_cell_depth=2,
            current_cell_depth=1,
            max_child_cells_per_parent=1,
            child_cells_requested=2,
        )
    )
    passed = (
        accepted.accepted
        and blocked.blocked
        and "recursive_depth_limit_exceeded" in blocked.reason_codes
        and unbounded.blocked
        and "unbounded_child_spawn_blocked" in unbounded.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=(
            *accepted.reason_codes,
            *blocked.reason_codes,
            *unbounded.reason_codes,
        ),
    )


def _child_consensus_does_not_create_authority() -> dict[str, Any]:
    scenario_id = "child_consensus_does_not_create_authority"
    consensus = validate_fractal_cell_input(
        FractalCellInput(
            parent_route_id="route:consensus",
            root_shaped_task_ref="root_task:consensus",
            plan_graph_ref="plan:consensus",
            child_consensus_claimed_authority=True,
            child_majority_claimed_authority=True,
            child_compute_volume_claimed_authority=True,
        )
    )
    passed = consensus.blocked and {
        "child_consensus_authority_blocked",
        "child_majority_authority_blocked",
        "child_compute_volume_authority_blocked",
    } <= set(consensus.reason_codes)
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=consensus.reason_codes,
    )


def _child_output_returns_to_parent_post_vv_gt_route() -> dict[str, Any]:
    scenario_id = "child_output_returns_to_parent_post_vv_gt_route"
    run = run_bounded_fractal_cell(
        make_default_fractal_cell_input(parent_route_id="route:parent_return")
    )
    report = run["boundary_report"]
    passed = (
        run["status"] == "completed"
        and report.child_validation_reports_count >= 1
        and report.child_gt_reports_count == 1
        and report.parent_return_reports_count == 1
        and "child_output_returns_to_parent_root_boundary" in report.reason_codes
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=report.reason_codes,
        counters=report.counters,
    )


def _root_final_authority_preserved_across_fractal_cell() -> dict[str, Any]:
    scenario_id = "root_final_authority_preserved_across_fractal_cell"
    run = run_bounded_fractal_cell(
        make_default_fractal_cell_input(parent_route_id="route:root_authority")
    )
    report = run["boundary_report"]
    zero_boundary = all(report.counters[key] == 0 for key in ZERO_COUNTERS)
    passed = (
        run["status"] == "completed"
        and zero_boundary
        and report.root_final_authority_preserved
        and report.counters["root_final_authority_preserved_count"] == 1
    )
    return _scenario_result(
        scenario_id,
        passed,
        reason_codes=report.reason_codes,
        counters=report.counters,
    )


SCENARIO_FUNCTIONS = {
    "root_shaped_task_enters_fractal_cell_boundary": (
        _root_shaped_task_enters_fractal_cell_boundary
    ),
    "child_architect_accepts_only_root_shaped_task": (
        _child_architect_accepts_only_root_shaped_task
    ),
    "child_executor_outputs_resultproposal_only": (
        _child_executor_outputs_resultproposal_only
    ),
    "child_verifier_validates_without_finaloutput": (
        _child_verifier_validates_without_finaloutput
    ),
    "child_gt_report_returns_to_parent_root_boundary": (
        _child_gt_report_returns_to_parent_root_boundary
    ),
    "child_finaloutput_claim_is_blocked": _child_finaloutput_claim_is_blocked,
    "child_actor_self_promotion_to_root_is_blocked": (
        _child_actor_self_promotion_to_root_is_blocked
    ),
    "child_cell_cannot_command_parent_architect": (
        _child_cell_cannot_command_parent_architect
    ),
    "recursive_child_cell_depth_is_bounded": _recursive_child_cell_depth_is_bounded,
    "child_consensus_does_not_create_authority": (
        _child_consensus_does_not_create_authority
    ),
    "child_output_returns_to_parent_post_vv_gt_route": (
        _child_output_returns_to_parent_post_vv_gt_route
    ),
    "root_final_authority_preserved_across_fractal_cell": (
        _root_final_authority_preserved_across_fractal_cell
    ),
}


def evaluate_scenario(scenario_id: str) -> dict[str, Any]:
    return SCENARIO_FUNCTIONS[scenario_id]()


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIOS]
    counters = _empty_counters()
    for scenario in scenarios:
        for key, value in scenario["counters"].items():
            if key in counters:
                counters[key] += int(value)
    scenarios_passed = sum(1 for scenario in scenarios if scenario["status"] == "PASS")
    pass_conditions = {
        "scenarios_total_is_12": len(scenarios) == 12,
        "scenarios_passed": scenarios_passed == len(scenarios),
        "final_output_created_count_zero": counters["final_output_created_count"] == 0,
        "action_permission_granted_count_zero": (
            counters["action_permission_granted_count"] == 0
        ),
        "child_root_claimed_count_zero": counters["child_root_claimed_count"] == 0,
        "child_authority_claimed_count_zero": (
            counters["child_authority_claimed_count"] == 0
        ),
        "child_finaloutput_claimed_count_zero": (
            counters["child_finaloutput_claimed_count"] == 0
        ),
        "child_action_permission_claimed_count_zero": (
            counters["child_action_permission_claimed_count"] == 0
        ),
        "child_actor_self_promotion_count_zero": (
            counters["child_actor_self_promotion_count"] == 0
        ),
        "parent_boundary_bypass_count_zero": (
            counters["parent_boundary_bypass_count"] == 0
        ),
        "post_vv_bypass_count_zero": counters["post_vv_bypass_count"] == 0,
        "gt_bypass_count_zero": counters["gt_bypass_count"] == 0,
        "parent_architect_commanded_count_zero": (
            counters["parent_architect_commanded_count"] == 0
        ),
        "recursive_depth_limit_exceeded_count_zero": (
            counters["recursive_depth_limit_exceeded_count"] == 0
        ),
        "unbounded_child_spawn_count_zero": (
            counters["unbounded_child_spawn_count"] == 0
        ),
        "child_consensus_authority_claimed_count_zero": (
            counters["child_consensus_authority_claimed_count"] == 0
        ),
        "manifest_mutation_count_zero": counters["manifest_mutation_count"] == 0,
        "transition_matrix_mutation_count_zero": (
            counters["transition_matrix_mutation_count"] == 0
        ),
        "network_used_count_zero": counters["network_used_count"] == 0,
        "gemini_used_count_zero": counters["gemini_used_count"] == 0,
        "connector_side_effect_count_zero": (
            counters["connector_side_effect_count"] == 0
        ),
        "root_final_authority_preserved_count": (
            counters["root_final_authority_preserved_count"] == len(scenarios)
        ),
    }
    return {
        "title": TITLE,
        "scenarios": scenarios,
        "scenarios_total": len(scenarios),
        "scenarios_passed": scenarios_passed,
        "counters": counters,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_all_scenarios()
    lines = [
        TITLE,
        "",
        "pipeline:",
        "Real Local DRS Resolver",
        "-> CandidateVectorGenerator",
        "-> AVF scoring",
        "-> AVF Candidate Advisory Evaluator",
        "-> Bounded LLM/SLM Actor Contracts",
        "-> Fractal Cell Runtime Integration",
        "-> parent Root final review",
        "",
        "scenarios:",
    ]
    for scenario in result["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']}")
        lines.append(f"  reason_codes: {', '.join(scenario['reason_codes'])}")
    lines.extend(
        [
            "",
            "aggregate counters:",
            f"scenarios_total: {result['scenarios_total']}",
            f"scenarios_passed: {result['scenarios_passed']}",
        ]
    )
    for key in COUNTER_KEYS:
        lines.append(f"{key}: {result['counters'][key]}")
    lines.extend(
        [
            "",
            "authority boundary summary:",
            "A Fractal Cell is not Root.",
            "A child Orchestrator is not Root.",
            "A child Architect is not Root.",
            "A child Executor is not Root.",
            "A child GT/advisory report is not Root Final.",
            "A child ResultProposal is not FinalOutput.",
            "A child cell output is not action permission.",
            "A child cell output must return to parent/Root boundary.",
            "Parent Root remains final authority.",
            "",
            "target-boundary coverage:",
            "child Architect PlanGraph -> final_output is blocked.",
            "child Executor ResultProposal -> final_output is blocked.",
            "child Verifier VVReport -> final_output is blocked.",
            "child GTReport -> final_output is blocked.",
            "child GTReport -> parent Architect command is blocked.",
            "child Root return -> user FinalOutput is blocked.",
            "reason_code: child_target_boundary_blocked",
            "",
            "recursion and nesting:",
            "recursive_child_cell_depth_is_bounded",
            "child_consensus_does_not_create_authority",
            "max_cell_depth and max_child_cells_per_parent are enforced.",
            "Repeated child cell agreement is not truth.",
            "Child majority vote is not authority.",
            "Child compute volume is not authority.",
            "",
            "limitations:",
            "No production Fractal Cell runtime.",
            "No production distributed runtime.",
            "No external/global DRS.",
            "No network.",
            "No Gemini.",
            "No real model calls.",
            "No autonomous action.",
            "No connector side effects.",
            "No Marennya/UP.",
            "No manifest mutation.",
            "No transition matrix mutation.",
            "No Root behavior modification.",
            "No child Root.",
            "No child FinalOutput authority.",
            "No child action permission.",
            "Real Semantic Runtime MVP is not complete.",
            "",
            f"FINAL STATUS: {result['final_status']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_all_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
