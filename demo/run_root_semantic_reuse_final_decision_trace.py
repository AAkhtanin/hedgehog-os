from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_root_semantic_reuse_gate_trace import (
    RootSemanticReuseGateRow,
    RootSemanticReuseGateTraceReport,
    collect_root_semantic_reuse_gate_trace,
)


ROOT_FINAL_DECISION_BY_GATE_OUTCOME = {
    "gate_review_accepts_candidate_for_root_final_decision": (
        "root_final_accepts_controlled_direct_reuse_trace"
    ),
    "gate_not_applicable_full_pipeline_fallback": (
        "root_final_selects_full_pipeline_fallback"
    ),
    "gate_not_applicable_conflict_check_required": (
        "root_final_requires_conflict_check"
    ),
    "gate_not_applicable_policy_blocked": "root_final_blocks_policy_route",
    "gate_not_applicable_quarantine": "root_final_routes_to_quarantine",
    "gate_not_applicable_needs_user": "root_final_requires_user_input",
    "gate_not_applicable_degraded": "root_final_marks_degraded_trace",
    "gate_not_applicable_dead_end": "root_final_rejects_dead_end",
}


@dataclass(frozen=True)
class RootSemanticReuseFinalDecision:
    scenario: str
    record_id: str
    gate_outcome: str
    root_final_decision: str
    final_decision_reason: str
    root_received_gate_result: bool
    root_final_boundary_checked: bool
    trace_final_decision_artifact_created: bool
    trace_artifact_created_by: str
    production_final_output_created: bool
    production_direct_reuse_executed: bool
    production_action_executed: bool
    production_work_record_written: bool
    semantic_pipeline_authority_granted: bool
    reuse_gate_authority_granted: bool
    full_pipeline_fallback_selected: bool
    conflict_check_required: bool
    policy_blocked: bool
    quarantine_route: bool
    user_input_required: bool
    degraded_route: bool
    dead_end_rejected: bool
    unsafe_reuse_candidate: bool


@dataclass(frozen=True)
class RootSemanticReuseFinalDecisionTraceReport:
    source_report: RootSemanticReuseGateTraceReport
    final_decisions: list[RootSemanticReuseFinalDecision]
    input: dict[str, Any]
    final_authority_checks: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _final_decision_reason(row: RootSemanticReuseGateRow) -> str:
    return {
        "gate_review_accepts_candidate_for_root_final_decision": (
            "gate_approved_candidate_returned_to_root_for_trace_decision"
        ),
        "gate_not_applicable_full_pipeline_fallback": (
            "full_pipeline_fallback_preserved"
        ),
        "gate_not_applicable_conflict_check_required": (
            "conflict_check_required_before_reuse"
        ),
        "gate_not_applicable_policy_blocked": "policy_block_preserved",
        "gate_not_applicable_quarantine": "quarantine_route_preserved",
        "gate_not_applicable_needs_user": "user_input_required",
        "gate_not_applicable_degraded": "degraded_trace_not_stable_success",
        "gate_not_applicable_dead_end": "dead_end_rejected",
    }[row.gate_outcome]


def _final_decision_from_gate_row(
    row: RootSemanticReuseGateRow,
) -> RootSemanticReuseFinalDecision:
    controlled_direct_reuse_trace = (
        row.gate_outcome == "gate_review_accepts_candidate_for_root_final_decision"
    )
    return RootSemanticReuseFinalDecision(
        scenario=row.scenario,
        record_id=row.record_id,
        gate_outcome=row.gate_outcome,
        root_final_decision=ROOT_FINAL_DECISION_BY_GATE_OUTCOME[row.gate_outcome],
        final_decision_reason=_final_decision_reason(row),
        root_received_gate_result=True,
        root_final_boundary_checked=True,
        trace_final_decision_artifact_created=controlled_direct_reuse_trace,
        trace_artifact_created_by=(
            "root_orchestrator" if controlled_direct_reuse_trace else "none"
        ),
        production_final_output_created=False,
        production_direct_reuse_executed=False,
        production_action_executed=False,
        production_work_record_written=False,
        semantic_pipeline_authority_granted=row.semantic_pipeline_committed,
        reuse_gate_authority_granted=False,
        full_pipeline_fallback_selected=row.full_pipeline_fallback_required,
        conflict_check_required=row.conflict_check_required,
        policy_blocked=row.policy_blocked,
        quarantine_route=row.quarantine_route,
        user_input_required=row.user_input_required,
        degraded_route=row.degraded_route,
        dead_end_rejected=row.dead_end_rejected,
        unsafe_reuse_candidate=row.unsafe_reuse_candidate,
    )


def _input(source_report: RootSemanticReuseGateTraceReport) -> dict[str, Any]:
    return {
        "root_semantic_reuse_gate_trace_available": (
            source_report.summary["root_semantic_reuse_gate_trace_status"] == "PASS"
        ),
        "gate_trace_status": source_report.summary[
            "root_semantic_reuse_gate_trace_status"
        ],
        "gate_rows_received": len(source_report.rows),
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
    }


def _final_authority_checks(
    source_report: RootSemanticReuseGateTraceReport,
    rows: list[RootSemanticReuseFinalDecision],
) -> dict[str, Any]:
    trace_artifacts = [
        row for row in rows if row.trace_final_decision_artifact_created
    ]
    return {
        "gate_trace_consumed": (
            source_report.summary["root_semantic_reuse_gate_trace_status"] == "PASS"
        ),
        "root_received_all_gate_results": all(
            row.root_received_gate_result for row in rows
        )
        and len(rows) == len(source_report.rows),
        "root_final_boundary_checked_for_all": all(
            row.root_final_boundary_checked for row in rows
        ),
        "trace_final_decision_artifacts_created": len(trace_artifacts),
        "trace_artifacts_created_only_by_root": all(
            row.trace_artifact_created_by == "root_orchestrator"
            for row in trace_artifacts
        )
        and bool(trace_artifacts),
        "production_final_output_created": any(
            row.production_final_output_created for row in rows
        ),
        "production_direct_reuse_executed": any(
            row.production_direct_reuse_executed for row in rows
        ),
        "production_action_executed": any(
            row.production_action_executed for row in rows
        ),
        "production_work_record_written": any(
            row.production_work_record_written for row in rows
        ),
        "semantic_pipeline_authority_granted": any(
            row.semantic_pipeline_authority_granted for row in rows
        ),
        "reuse_gate_authority_granted": any(
            row.reuse_gate_authority_granted for row in rows
        ),
        "full_pipeline_fallback_preserved": any(
            row.full_pipeline_fallback_selected for row in rows
        ),
        "conflict_check_preserved": any(row.conflict_check_required for row in rows),
        "policy_block_preserved": any(row.policy_blocked for row in rows),
        "quarantine_not_work": all(
            not row.production_work_record_written for row in rows if row.quarantine_route
        ),
        "needs_user_not_completed_action": all(
            not row.production_action_executed for row in rows if row.user_input_required
        ),
        "degraded_not_stable_success": all(
            not row.production_direct_reuse_executed for row in rows if row.degraded_route
        ),
        "dead_end_not_reused": all(
            not row.production_direct_reuse_executed for row in rows if row.dead_end_rejected
        ),
        "high_score_overrode_policy": source_report.authority_checks[
            "high_score_overrode_policy"
        ],
        "contradiction_auto_reuse": source_report.authority_checks[
            "contradiction_auto_reuse"
        ],
        "context_memory_equals_direct_reuse": source_report.authority_checks[
            "context_memory_equals_direct_reuse"
        ],
        "unsafe_reuse_candidates": sum(row.unsafe_reuse_candidate for row in rows),
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
    rows: list[RootSemanticReuseFinalDecision],
    checks: dict[str, Any],
    source_report: RootSemanticReuseGateTraceReport,
) -> dict[str, Any]:
    final_decisions_derived = all(
        row.root_final_decision
        == ROOT_FINAL_DECISION_BY_GATE_OUTCOME[row.gate_outcome]
        for row in rows
    )
    controlled_accepts = sum(
        row.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
        for row in rows
    )
    pass_status = (
        source_report.summary["root_semantic_reuse_gate_trace_status"] == "PASS"
        and len(rows) == 8
        and final_decisions_derived
        and controlled_accepts == 1
        and checks["gate_trace_consumed"]
        and checks["root_received_all_gate_results"]
        and checks["root_final_boundary_checked_for_all"]
        and checks["trace_artifacts_created_only_by_root"]
        and not checks["production_direct_reuse_executed"]
        and not checks["production_final_output_created"]
        and not checks["production_action_executed"]
        and not checks["production_work_record_written"]
        and not checks["semantic_pipeline_authority_granted"]
        and not checks["reuse_gate_authority_granted"]
        and checks["unsafe_reuse_candidates"] == 0
        and source_report.summary["root_authority_preserved"]
        and source_report.summary["reuse_gate_boundary_preserved"]
        and not checks["production_autonomy_claimed"]
    )
    return {
        "root_semantic_reuse_final_decision_trace_status": (
            "PASS" if pass_status else "FAIL"
        ),
        "final_decisions_evaluated": len(rows),
        "final_decisions_derived_from_gate_rows": final_decisions_derived,
        "controlled_direct_reuse_trace_accepts": controlled_accepts,
        "full_pipeline_fallbacks_selected": sum(
            row.full_pipeline_fallback_selected for row in rows
        ),
        "conflict_check_required_cases": sum(
            row.conflict_check_required for row in rows
        ),
        "policy_blocked_cases": sum(row.policy_blocked for row in rows),
        "quarantine_routes": sum(row.quarantine_route for row in rows),
        "needs_user_routes": sum(row.user_input_required for row in rows),
        "degraded_routes": sum(row.degraded_route for row in rows),
        "dead_end_rejections": sum(row.dead_end_rejected for row in rows),
        "root_created_trace_final_decision_artifact": (
            checks["trace_final_decision_artifacts_created"] > 0
        ),
        "trace_artifacts_created_only_by_root": checks[
            "trace_artifacts_created_only_by_root"
        ],
        "production_direct_reuse_executed": checks[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": checks[
            "production_final_output_created"
        ],
        "production_action_executed": checks["production_action_executed"],
        "production_work_record_written": checks["production_work_record_written"],
        "root_authority_preserved": source_report.summary[
            "root_authority_preserved"
        ],
        "reuse_gate_boundary_preserved": source_report.summary[
            "reuse_gate_boundary_preserved"
        ],
        "semantic_pipeline_authority_granted": checks[
            "semantic_pipeline_authority_granted"
        ],
        "reuse_gate_authority_granted": checks["reuse_gate_authority_granted"],
        "unsafe_reuse_candidates": checks["unsafe_reuse_candidates"],
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
        "production_autonomy_claimed": checks["production_autonomy_claimed"],
    }


def collect_root_semantic_reuse_final_decision_trace() -> (
    RootSemanticReuseFinalDecisionTraceReport
):
    source_report = collect_root_semantic_reuse_gate_trace()
    rows = [_final_decision_from_gate_row(row) for row in source_report.rows]
    checks = _final_authority_checks(source_report, rows)
    summary = _summary(rows, checks, source_report)
    return RootSemanticReuseFinalDecisionTraceReport(
        source_report=source_report,
        final_decisions=rows,
        input=_input(source_report),
        final_authority_checks=checks,
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


def _row_line(row: RootSemanticReuseFinalDecision) -> str:
    return " | ".join(
        [
            row.scenario,
            row.record_id,
            row.gate_outcome,
            row.root_final_decision,
            row.final_decision_reason,
            _bool_text(row.root_received_gate_result),
            _bool_text(row.root_final_boundary_checked),
            _bool_text(row.trace_final_decision_artifact_created),
            row.trace_artifact_created_by,
            _bool_text(row.production_final_output_created),
            _bool_text(row.production_direct_reuse_executed),
            _bool_text(row.production_action_executed),
            _bool_text(row.production_work_record_written),
            _bool_text(row.semantic_pipeline_authority_granted),
            _bool_text(row.reuse_gate_authority_granted),
            _bool_text(row.full_pipeline_fallback_selected),
            _bool_text(row.conflict_check_required),
            _bool_text(row.policy_blocked),
            _bool_text(row.quarantine_route),
            _bool_text(row.user_input_required),
            _bool_text(row.degraded_route),
            _bool_text(row.dead_end_rejected),
            _bool_text(row.unsafe_reuse_candidate),
        ]
    )


def render_root_semantic_reuse_final_decision_trace(
    report: RootSemanticReuseFinalDecisionTraceReport,
) -> str:
    lines = [
        "[ROOT SEMANTIC REUSE FINAL DECISION TRACE]",
        "note: Root-controlled final semantic reuse dry-run proof",
        "note: consumes Root Semantic Reuse Gate Trace",
        "note: no production RootOrchestrator behavior change",
        "note: no production direct reuse execution",
        "note: no production external action",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: Root creates trace-level final decision artifact only",
        "note: production FinalOutput is not created",
        "",
        "[INPUT]",
    ]
    lines.extend(_field_lines(report.input))
    lines.extend(
        [
            "",
            "[ROOT FINAL DECISION TABLE]",
            "scenario | record_id | gate_outcome | root_final_decision | final_decision_reason | root_received_gate_result | root_final_boundary_checked | trace_final_decision_artifact_created | trace_artifact_created_by | production_final_output_created | production_direct_reuse_executed | production_action_executed | production_work_record_written | semantic_pipeline_authority_granted | reuse_gate_authority_granted | full_pipeline_fallback_selected | conflict_check_required | policy_blocked | quarantine_route | user_input_required | degraded_route | dead_end_rejected | unsafe_reuse_candidate",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_row_line(row) for row in report.final_decisions)
    lines.extend(["", "[FINAL AUTHORITY CHECKS]"])
    lines.extend(_field_lines(report.final_authority_checks))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_root_semantic_reuse_final_decision_trace() -> str:
    return render_root_semantic_reuse_final_decision_trace(
        collect_root_semantic_reuse_final_decision_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Root-controlled Semantic Reuse Final Decision Trace proof."
    )
    parser.parse_args()
    print(run_root_semantic_reuse_final_decision_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
