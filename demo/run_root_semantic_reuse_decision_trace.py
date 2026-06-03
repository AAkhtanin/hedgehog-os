from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_semantic_reuse_pipeline import SemanticReusePipelineReport
from demo.run_semantic_reuse_pipeline import SemanticReuseScenario
from demo.run_semantic_reuse_pipeline import collect_semantic_reuse_pipeline


ROOT_DECISION_BY_RECOMMENDATION = {
    "direct_reuse_candidate": "root_accepts_direct_reuse_candidate_for_gate_review",
    "needs_full_pipeline": "root_selects_full_pipeline_fallback",
    "needs_conflict_check": "root_requires_conflict_check",
    "blocked": "root_blocks_policy_blocked_route",
    "quarantine": "root_routes_to_quarantine",
    "needs_user": "root_requires_user_input",
    "degraded": "root_marks_degraded_trace",
    "dead_end": "root_rejects_dead_end",
}


@dataclass(frozen=True)
class RootSemanticReuseDecision:
    scenario: str
    record_id: str
    pipeline_recommendation: str
    root_decision: str
    boundary_decision: str
    boundary_reason: str
    root_received_recommendation: bool
    root_boundary_checked: bool
    reuse_gate_required: bool
    reuse_gate_bypassed: bool
    semantic_pipeline_committed: bool
    root_created_final_output: bool
    production_final_output_created: bool
    direct_reuse_executed: bool
    production_action_executed: bool
    fallback_required: bool
    conflict_check_required: bool
    user_input_required: bool
    quarantine_route: bool
    degraded_route: bool
    dead_end_rejected: bool
    unsafe_reuse_candidate: bool


@dataclass(frozen=True)
class RootSemanticReuseDecisionTraceReport:
    source_report: SemanticReusePipelineReport
    decisions: list[RootSemanticReuseDecision]
    input: dict[str, Any]
    boundary_checks: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _root_decision(scenario: SemanticReuseScenario) -> str:
    return ROOT_DECISION_BY_RECOMMENDATION[scenario.pipeline_recommendation]


def _boundary_reason(root_decision: str) -> str:
    return {
        "root_accepts_direct_reuse_candidate_for_gate_review": (
            "candidate_may_proceed_to_reusegate_review_only"
        ),
        "root_selects_full_pipeline_fallback": (
            "context_or_score_is_not_execution_authority"
        ),
        "root_requires_conflict_check": (
            "contradiction_signal_requires_future_conflict_check"
        ),
        "root_blocks_policy_blocked_route": "policy_boundary_blocks_route",
        "root_routes_to_quarantine": "quarantine_is_not_work_or_reuse",
        "root_requires_user_input": "permission_or_human_input_required",
        "root_marks_degraded_trace": "degraded_trace_is_not_stable_success",
        "root_rejects_dead_end": "dead_end_is_not_reusable",
    }[root_decision]


def _boundary_decision(root_decision: str) -> str:
    return {
        "root_accepts_direct_reuse_candidate_for_gate_review": (
            "root_reusegate_review_required"
        ),
        "root_selects_full_pipeline_fallback": (
            "root_full_pipeline_fallback_required"
        ),
        "root_requires_conflict_check": "root_conflict_check_required",
        "root_blocks_policy_blocked_route": "root_policy_block_boundary",
        "root_routes_to_quarantine": "root_quarantine_route_boundary",
        "root_requires_user_input": "root_user_input_boundary",
        "root_marks_degraded_trace": "root_degraded_trace_boundary",
        "root_rejects_dead_end": "root_dead_end_rejection_boundary",
    }[root_decision]


def _decision_from_scenario(
    scenario: SemanticReuseScenario,
) -> RootSemanticReuseDecision:
    root_decision = _root_decision(scenario)
    direct_candidate = scenario.pipeline_recommendation == "direct_reuse_candidate"
    return RootSemanticReuseDecision(
        scenario=scenario.scenario,
        record_id=scenario.record_id,
        pipeline_recommendation=scenario.pipeline_recommendation,
        root_decision=root_decision,
        boundary_decision=_boundary_decision(root_decision),
        boundary_reason=_boundary_reason(root_decision),
        root_received_recommendation=True,
        root_boundary_checked=True,
        reuse_gate_required=direct_candidate,
        reuse_gate_bypassed=False,
        semantic_pipeline_committed=scenario.committed_by_pipeline,
        root_created_final_output=False,
        production_final_output_created=False,
        direct_reuse_executed=False,
        production_action_executed=False,
        fallback_required=scenario.pipeline_recommendation == "needs_full_pipeline",
        conflict_check_required=(
            scenario.pipeline_recommendation == "needs_conflict_check"
        ),
        user_input_required=scenario.pipeline_recommendation == "needs_user",
        quarantine_route=scenario.pipeline_recommendation == "quarantine",
        degraded_route=scenario.pipeline_recommendation == "degraded",
        dead_end_rejected=scenario.pipeline_recommendation == "dead_end",
        unsafe_reuse_candidate=scenario.unsafe_reuse_candidate,
    )


def _input(source_report: SemanticReusePipelineReport) -> dict[str, Any]:
    return {
        "semantic_reuse_pipeline_available": (
            source_report.summary["semantic_reuse_pipeline_status"] == "PASS"
        ),
        "pipeline_status": source_report.summary["semantic_reuse_pipeline_status"],
        "scenarios_received": len(source_report.scenarios),
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
    }


def _boundary_checks(
    source_report: SemanticReusePipelineReport,
    decisions: list[RootSemanticReuseDecision],
) -> dict[str, Any]:
    return {
        "root_received_all_recommendations": all(
            decision.root_received_recommendation for decision in decisions
        )
        and len(decisions) == len(source_report.scenarios),
        "root_boundary_checked_for_all": all(
            decision.root_boundary_checked for decision in decisions
        ),
        "reuse_gate_required_for_direct_reuse_candidate": any(
            decision.root_decision
            == "root_accepts_direct_reuse_candidate_for_gate_review"
            and decision.reuse_gate_required
            for decision in decisions
        ),
        "reuse_gate_bypassed": any(decision.reuse_gate_bypassed for decision in decisions),
        "semantic_pipeline_committed_final_output": source_report.boundary_safety[
            "semantic_pipeline_committed_final_output"
        ],
        "semantic_pipeline_bypassed_root": source_report.boundary_safety[
            "semantic_pipeline_bypassed_root"
        ],
        "semantic_pipeline_bypassed_reuse_gate": source_report.boundary_safety[
            "semantic_pipeline_bypassed_reuse_gate"
        ],
        "root_created_production_final_output": any(
            decision.root_created_final_output for decision in decisions
        ),
        "production_action_executed": any(
            decision.production_action_executed for decision in decisions
        ),
        "direct_reuse_executed_in_trace": any(
            decision.direct_reuse_executed for decision in decisions
        ),
        "context_memory_equals_direct_reuse": source_report.boundary_safety[
            "context_memory_equals_direct_reuse"
        ],
        "high_score_overrode_policy": source_report.boundary_safety[
            "high_score_overrides_policy"
        ],
        "contradiction_auto_reuse": source_report.boundary_safety[
            "contradiction_auto_reuse"
        ],
        "unsafe_reuse_candidates": sum(
            decision.unsafe_reuse_candidate for decision in decisions
        ),
        "quarantine_reused": any(
            decision.quarantine_route and decision.direct_reuse_executed
            for decision in decisions
        ),
        "dead_end_reused": any(
            decision.dead_end_rejected and decision.direct_reuse_executed
            for decision in decisions
        ),
        "blocked_route_reused": any(
            decision.root_decision == "root_blocks_policy_blocked_route"
            and decision.direct_reuse_executed
            for decision in decisions
        ),
        "degraded_trace_reused": any(
            decision.degraded_route and decision.direct_reuse_executed
            for decision in decisions
        ),
        "needs_user_completed_as_action": any(
            decision.user_input_required and decision.production_action_executed
            for decision in decisions
        ),
        "no_real_external_actions": True,
        "no_live_gemini": True,
        "no_telegram_actions": True,
        "no_global_drs": not source_report.summary["global_drs_implemented"],
        "no_external_drs_network": not source_report.summary[
            "external_drs_network_implemented"
        ],
        "production_autonomy_claimed": False,
    }


def _summary(
    decisions: list[RootSemanticReuseDecision],
    boundary_checks: dict[str, Any],
    source_report: SemanticReusePipelineReport,
) -> dict[str, Any]:
    direct_gate_review = [
        decision
        for decision in decisions
        if decision.root_decision
        == "root_accepts_direct_reuse_candidate_for_gate_review"
    ]
    fallbacks = [
        decision
        for decision in decisions
        if decision.root_decision == "root_selects_full_pipeline_fallback"
    ]
    conflicts = [
        decision
        for decision in decisions
        if decision.root_decision == "root_requires_conflict_check"
    ]
    policy_blocked = [
        decision
        for decision in decisions
        if decision.root_decision == "root_blocks_policy_blocked_route"
    ]
    quarantines = [
        decision
        for decision in decisions
        if decision.root_decision == "root_routes_to_quarantine"
    ]
    needs_user = [
        decision
        for decision in decisions
        if decision.root_decision == "root_requires_user_input"
    ]
    degraded = [
        decision
        for decision in decisions
        if decision.root_decision == "root_marks_degraded_trace"
    ]
    dead_ends = [
        decision
        for decision in decisions
        if decision.root_decision == "root_rejects_dead_end"
    ]
    root_boundary_preserved = (
        boundary_checks["root_received_all_recommendations"]
        and boundary_checks["root_boundary_checked_for_all"]
        and not boundary_checks["semantic_pipeline_bypassed_root"]
    )
    reuse_gate_boundary_preserved = (
        boundary_checks["reuse_gate_required_for_direct_reuse_candidate"]
        and not boundary_checks["reuse_gate_bypassed"]
        and not boundary_checks["semantic_pipeline_bypassed_reuse_gate"]
    )
    semantic_pipeline_authority_granted = any(
        decision.semantic_pipeline_committed for decision in decisions
    )
    pass_status = (
        source_report.summary["semantic_reuse_pipeline_status"] == "PASS"
        and len(decisions) == 8
        and len(direct_gate_review) >= 1
        and len(fallbacks) >= 1
        and len(conflicts) >= 1
        and len(policy_blocked) >= 1
        and len(quarantines) >= 1
        and len(needs_user) >= 1
        and len(degraded) >= 1
        and len(dead_ends) >= 1
        and root_boundary_preserved
        and reuse_gate_boundary_preserved
        and not semantic_pipeline_authority_granted
        and not boundary_checks["direct_reuse_executed_in_trace"]
        and not boundary_checks["root_created_production_final_output"]
        and boundary_checks["unsafe_reuse_candidates"] == 0
        and not boundary_checks["production_autonomy_claimed"]
    )
    return {
        "root_semantic_reuse_decision_trace_status": (
            "PASS" if pass_status else "FAIL"
        ),
        "decisions_evaluated": len(decisions),
        "root_decisions_derived_from_pipeline": all(
            decision.root_decision
            == ROOT_DECISION_BY_RECOMMENDATION[decision.pipeline_recommendation]
            for decision in decisions
        ),
        "direct_reuse_candidates_sent_to_reuse_gate_review": len(direct_gate_review),
        "full_pipeline_fallbacks_selected": len(fallbacks),
        "conflict_check_required_cases": len(conflicts),
        "policy_blocked_cases": len(policy_blocked),
        "quarantine_routes": len(quarantines),
        "needs_user_routes": len(needs_user),
        "degraded_routes": len(degraded),
        "dead_end_rejections": len(dead_ends),
        "reuse_gate_boundary_preserved": reuse_gate_boundary_preserved,
        "root_boundary_preserved": root_boundary_preserved,
        "semantic_pipeline_authority_granted": semantic_pipeline_authority_granted,
        "direct_reuse_executed_in_trace": boundary_checks[
            "direct_reuse_executed_in_trace"
        ],
        "production_final_output_created": boundary_checks[
            "root_created_production_final_output"
        ],
        "unsafe_reuse_candidates": boundary_checks["unsafe_reuse_candidates"],
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
        "production_autonomy_claimed": boundary_checks[
            "production_autonomy_claimed"
        ],
    }


def collect_root_semantic_reuse_decision_trace() -> (
    RootSemanticReuseDecisionTraceReport
):
    source_report = collect_semantic_reuse_pipeline()
    decisions = [
        _decision_from_scenario(scenario) for scenario in source_report.scenarios
    ]
    boundary_checks = _boundary_checks(source_report, decisions)
    summary = _summary(decisions, boundary_checks, source_report)
    return RootSemanticReuseDecisionTraceReport(
        source_report=source_report,
        decisions=decisions,
        input=_input(source_report),
        boundary_checks=boundary_checks,
        summary=summary,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def _decision_line(decision: RootSemanticReuseDecision) -> str:
    return " | ".join(
        [
            decision.scenario,
            decision.record_id,
            decision.pipeline_recommendation,
            decision.root_decision,
            decision.boundary_decision,
            decision.boundary_reason,
            _bool_text(decision.root_received_recommendation),
            _bool_text(decision.root_boundary_checked),
            _bool_text(decision.reuse_gate_required),
            _bool_text(decision.reuse_gate_bypassed),
            _bool_text(decision.semantic_pipeline_committed),
            _bool_text(decision.root_created_final_output),
            _bool_text(decision.production_final_output_created),
            _bool_text(decision.direct_reuse_executed),
            _bool_text(decision.production_action_executed),
            _bool_text(decision.fallback_required),
            _bool_text(decision.conflict_check_required),
            _bool_text(decision.user_input_required),
            _bool_text(decision.quarantine_route),
            _bool_text(decision.degraded_route),
            _bool_text(decision.dead_end_rejected),
            _bool_text(decision.unsafe_reuse_candidate),
        ]
    )


def render_root_semantic_reuse_decision_trace(
    report: RootSemanticReuseDecisionTraceReport,
) -> str:
    lines = [
        "[ROOT SEMANTIC REUSE DECISION TRACE]",
        "note: Root-controlled semantic reuse decision dry-run",
        "note: no production RootOrchestrator behavior change",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no real external actions",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: semantic pipeline recommends but does not commit",
        "note: Root decision trace preserves ReuseGate boundary",
        "",
        "[INPUT]",
    ]
    lines.extend(_field_lines(report.input))
    lines.extend(
        [
            "",
            "[ROOT DECISION TABLE]",
            "scenario | record_id | pipeline_recommendation | root_decision | boundary_decision | boundary_reason | root_received_recommendation | root_boundary_checked | reuse_gate_required | reuse_gate_bypassed | semantic_pipeline_committed | root_created_final_output | production_final_output_created | direct_reuse_executed | production_action_executed | fallback_required | conflict_check_required | user_input_required | quarantine_route | degraded_route | dead_end_rejected | unsafe_reuse_candidate",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_decision_line(decision) for decision in report.decisions)
    lines.extend(["", "[BOUNDARY CHECKS]"])
    lines.extend(_field_lines(report.boundary_checks))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_root_semantic_reuse_decision_trace() -> str:
    return render_root_semantic_reuse_decision_trace(
        collect_root_semantic_reuse_decision_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Root-controlled Semantic Reuse Decision Trace proof."
    )
    parser.parse_args()
    print(run_root_semantic_reuse_decision_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
