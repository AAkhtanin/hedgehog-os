from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_root_semantic_reuse_decision_trace import (
    RootSemanticReuseDecision,
    RootSemanticReuseDecisionTraceReport,
    collect_root_semantic_reuse_decision_trace,
)


GATE_OUTCOME_BY_ROOT_DECISION = {
    "root_accepts_direct_reuse_candidate_for_gate_review": (
        "gate_review_accepts_candidate_for_root_final_decision"
    ),
    "root_selects_full_pipeline_fallback": (
        "gate_not_applicable_full_pipeline_fallback"
    ),
    "root_requires_conflict_check": "gate_not_applicable_conflict_check_required",
    "root_blocks_policy_blocked_route": "gate_not_applicable_policy_blocked",
    "root_routes_to_quarantine": "gate_not_applicable_quarantine",
    "root_requires_user_input": "gate_not_applicable_needs_user",
    "root_marks_degraded_trace": "gate_not_applicable_degraded",
    "root_rejects_dead_end": "gate_not_applicable_dead_end",
}


@dataclass(frozen=True)
class RootSemanticReuseGateRow:
    scenario: str
    record_id: str
    root_decision: str
    gate_applicable: bool
    gate_review_performed: bool
    gate_outcome: str
    gate_approved_for_root_final_decision: bool
    gate_rejection_reason: str
    root_final_decision_required: bool
    semantic_pipeline_committed: bool
    reuse_gate_created_final_output: bool
    root_created_production_final_output: bool
    direct_reuse_executed: bool
    production_action_executed: bool
    full_pipeline_fallback_required: bool
    conflict_check_required: bool
    policy_blocked: bool
    quarantine_route: bool
    user_input_required: bool
    degraded_route: bool
    dead_end_rejected: bool
    unsafe_reuse_candidate: bool


@dataclass(frozen=True)
class RootSemanticReuseGateTraceReport:
    source_report: RootSemanticReuseDecisionTraceReport
    rows: list[RootSemanticReuseGateRow]
    input: dict[str, Any]
    authority_checks: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _gate_rejection_reason(decision: RootSemanticReuseDecision) -> str:
    return {
        "root_accepts_direct_reuse_candidate_for_gate_review": "none",
        "root_selects_full_pipeline_fallback": "full_pipeline_fallback_required",
        "root_requires_conflict_check": "conflict_check_required",
        "root_blocks_policy_blocked_route": "policy_blocked",
        "root_routes_to_quarantine": "quarantine_route",
        "root_requires_user_input": "user_input_required",
        "root_marks_degraded_trace": "degraded_trace_not_stable_success",
        "root_rejects_dead_end": "dead_end_rejected",
    }[decision.root_decision]


def _row_from_decision(
    decision: RootSemanticReuseDecision,
) -> RootSemanticReuseGateRow:
    gate_applicable = (
        decision.root_decision
        == "root_accepts_direct_reuse_candidate_for_gate_review"
    )
    return RootSemanticReuseGateRow(
        scenario=decision.scenario,
        record_id=decision.record_id,
        root_decision=decision.root_decision,
        gate_applicable=gate_applicable,
        gate_review_performed=gate_applicable,
        gate_outcome=GATE_OUTCOME_BY_ROOT_DECISION[decision.root_decision],
        gate_approved_for_root_final_decision=gate_applicable,
        gate_rejection_reason=_gate_rejection_reason(decision),
        root_final_decision_required=gate_applicable,
        semantic_pipeline_committed=decision.semantic_pipeline_committed,
        reuse_gate_created_final_output=False,
        root_created_production_final_output=False,
        direct_reuse_executed=False,
        production_action_executed=False,
        full_pipeline_fallback_required=decision.fallback_required,
        conflict_check_required=decision.conflict_check_required,
        policy_blocked=(
            decision.root_decision == "root_blocks_policy_blocked_route"
        ),
        quarantine_route=decision.quarantine_route,
        user_input_required=decision.user_input_required,
        degraded_route=decision.degraded_route,
        dead_end_rejected=decision.dead_end_rejected,
        unsafe_reuse_candidate=decision.unsafe_reuse_candidate,
    )


def _input(source_report: RootSemanticReuseDecisionTraceReport) -> dict[str, Any]:
    return {
        "root_semantic_reuse_decision_trace_available": (
            source_report.summary["root_semantic_reuse_decision_trace_status"]
            == "PASS"
        ),
        "decision_trace_status": source_report.summary[
            "root_semantic_reuse_decision_trace_status"
        ],
        "decisions_received": len(source_report.decisions),
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
    }


def _authority_checks(
    source_report: RootSemanticReuseDecisionTraceReport,
    rows: list[RootSemanticReuseGateRow],
) -> dict[str, Any]:
    gate_reviews = [row for row in rows if row.gate_review_performed]
    return {
        "root_decision_trace_consumed": (
            source_report.summary["root_semantic_reuse_decision_trace_status"]
            == "PASS"
        ),
        "gate_review_performed_for_direct_reuse_candidate": any(
            row.gate_review_performed
            and row.root_decision
            == "root_accepts_direct_reuse_candidate_for_gate_review"
            for row in rows
        ),
        "gate_review_only_for_direct_reuse_candidate": all(
            row.root_decision
            == "root_accepts_direct_reuse_candidate_for_gate_review"
            for row in gate_reviews
        ),
        "gate_approved_candidates_return_to_root": all(
            row.root_final_decision_required
            for row in rows
            if row.gate_approved_for_root_final_decision
        ),
        "gate_does_not_create_final_output": all(
            not row.reuse_gate_created_final_output for row in rows
        ),
        "gate_does_not_execute_direct_reuse": all(
            not row.direct_reuse_executed for row in rows
        ),
        "semantic_pipeline_committed_final_output": any(
            row.semantic_pipeline_committed for row in rows
        ),
        "semantic_pipeline_authority_granted": source_report.summary[
            "semantic_pipeline_authority_granted"
        ],
        "root_created_production_final_output": any(
            row.root_created_production_final_output for row in rows
        ),
        "direct_reuse_executed_in_trace": any(
            row.direct_reuse_executed for row in rows
        ),
        "production_action_executed": any(row.production_action_executed for row in rows),
        "full_pipeline_fallback_preserved": any(
            row.full_pipeline_fallback_required for row in rows
        ),
        "conflict_check_preserved": any(row.conflict_check_required for row in rows),
        "policy_block_preserved": any(row.policy_blocked for row in rows),
        "quarantine_not_reused": all(
            not row.direct_reuse_executed for row in rows if row.quarantine_route
        ),
        "needs_user_not_completed_action": all(
            not row.production_action_executed for row in rows if row.user_input_required
        ),
        "degraded_not_stable_success": all(
            not row.direct_reuse_executed for row in rows if row.degraded_route
        ),
        "dead_end_not_reused": all(
            not row.direct_reuse_executed for row in rows if row.dead_end_rejected
        ),
        "high_score_overrode_policy": source_report.boundary_checks[
            "high_score_overrode_policy"
        ],
        "contradiction_auto_reuse": source_report.boundary_checks[
            "contradiction_auto_reuse"
        ],
        "context_memory_equals_direct_reuse": source_report.boundary_checks[
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
    rows: list[RootSemanticReuseGateRow],
    checks: dict[str, Any],
    source_report: RootSemanticReuseDecisionTraceReport,
) -> dict[str, Any]:
    gate_reviews = [row for row in rows if row.gate_review_performed]
    gate_approvals = [
        row for row in rows if row.gate_approved_for_root_final_decision
    ]
    non_applicable = [row for row in rows if not row.gate_applicable]
    pass_status = (
        source_report.summary["root_semantic_reuse_decision_trace_status"] == "PASS"
        and len(rows) == 8
        and len(gate_reviews) == 1
        and len(gate_approvals) == 1
        and len(non_applicable) == 7
        and checks["root_decision_trace_consumed"]
        and checks["gate_review_only_for_direct_reuse_candidate"]
        and checks["gate_approved_candidates_return_to_root"]
        and checks["gate_does_not_create_final_output"]
        and checks["gate_does_not_execute_direct_reuse"]
        and not checks["direct_reuse_executed_in_trace"]
        and not checks["root_created_production_final_output"]
        and checks["unsafe_reuse_candidates"] == 0
        and source_report.summary["root_boundary_preserved"]
        and source_report.summary["reuse_gate_boundary_preserved"]
        and not checks["semantic_pipeline_authority_granted"]
        and not checks["production_autonomy_claimed"]
    )
    return {
        "root_semantic_reuse_gate_trace_status": "PASS" if pass_status else "FAIL",
        "gate_rows_evaluated": len(rows),
        "gate_rows_derived_from_root_decisions": all(
            row.gate_outcome == GATE_OUTCOME_BY_ROOT_DECISION[row.root_decision]
            for row in rows
        ),
        "gate_reviews_performed": len(gate_reviews),
        "gate_approvals_for_root_final_decision": len(gate_approvals),
        "non_applicable_gate_routes": len(non_applicable),
        "full_pipeline_fallbacks_preserved": sum(
            row.full_pipeline_fallback_required for row in rows
        ),
        "conflict_check_required_cases": sum(
            row.conflict_check_required for row in rows
        ),
        "policy_blocked_cases": sum(row.policy_blocked for row in rows),
        "quarantine_routes": sum(row.quarantine_route for row in rows),
        "needs_user_routes": sum(row.user_input_required for row in rows),
        "degraded_routes": sum(row.degraded_route for row in rows),
        "dead_end_rejections": sum(row.dead_end_rejected for row in rows),
        "root_final_decision_required_for_gate_approval": all(
            row.root_final_decision_required for row in gate_approvals
        ),
        "gate_did_not_commit_final_output": checks[
            "gate_does_not_create_final_output"
        ],
        "gate_did_not_execute_direct_reuse": checks[
            "gate_does_not_execute_direct_reuse"
        ],
        "direct_reuse_executed_in_trace": checks["direct_reuse_executed_in_trace"],
        "production_final_output_created": checks[
            "root_created_production_final_output"
        ],
        "unsafe_reuse_candidates": checks["unsafe_reuse_candidates"],
        "root_authority_preserved": source_report.summary["root_boundary_preserved"],
        "reuse_gate_boundary_preserved": source_report.summary[
            "reuse_gate_boundary_preserved"
        ],
        "semantic_pipeline_authority_granted": checks[
            "semantic_pipeline_authority_granted"
        ],
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
        "production_autonomy_claimed": checks["production_autonomy_claimed"],
    }


def collect_root_semantic_reuse_gate_trace() -> RootSemanticReuseGateTraceReport:
    source_report = collect_root_semantic_reuse_decision_trace()
    rows = [_row_from_decision(decision) for decision in source_report.decisions]
    checks = _authority_checks(source_report, rows)
    summary = _summary(rows, checks, source_report)
    return RootSemanticReuseGateTraceReport(
        source_report=source_report,
        rows=rows,
        input=_input(source_report),
        authority_checks=checks,
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


def _row_line(row: RootSemanticReuseGateRow) -> str:
    return " | ".join(
        [
            row.scenario,
            row.record_id,
            row.root_decision,
            _bool_text(row.gate_applicable),
            _bool_text(row.gate_review_performed),
            row.gate_outcome,
            _bool_text(row.gate_approved_for_root_final_decision),
            row.gate_rejection_reason,
            _bool_text(row.root_final_decision_required),
            _bool_text(row.semantic_pipeline_committed),
            _bool_text(row.reuse_gate_created_final_output),
            _bool_text(row.root_created_production_final_output),
            _bool_text(row.direct_reuse_executed),
            _bool_text(row.production_action_executed),
            _bool_text(row.full_pipeline_fallback_required),
            _bool_text(row.conflict_check_required),
            _bool_text(row.policy_blocked),
            _bool_text(row.quarantine_route),
            _bool_text(row.user_input_required),
            _bool_text(row.degraded_route),
            _bool_text(row.dead_end_rejected),
            _bool_text(row.unsafe_reuse_candidate),
        ]
    )


def render_root_semantic_reuse_gate_trace(
    report: RootSemanticReuseGateTraceReport,
) -> str:
    lines = [
        "[ROOT SEMANTIC REUSE GATE TRACE]",
        "note: Root-controlled ReuseGate dry-run proof",
        "note: consumes Root Semantic Reuse Decision Trace",
        "note: no production RootOrchestrator behavior change",
        "note: no production direct reuse execution",
        "note: no production FinalOutput",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no real external actions",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: Root decision sends candidates to ReuseGate review only",
        "note: ReuseGate guards, semantic pipeline does not commit",
        "",
        "[INPUT]",
    ]
    lines.extend(_field_lines(report.input))
    lines.extend(
        [
            "",
            "[REUSEGATE TRACE TABLE]",
            "scenario | record_id | root_decision | gate_applicable | gate_review_performed | gate_outcome | gate_approved_for_root_final_decision | gate_rejection_reason | root_final_decision_required | semantic_pipeline_committed | reuse_gate_created_final_output | root_created_production_final_output | direct_reuse_executed | production_action_executed | full_pipeline_fallback_required | conflict_check_required | policy_blocked | quarantine_route | user_input_required | degraded_route | dead_end_rejected | unsafe_reuse_candidate",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_row_line(row) for row in report.rows)
    lines.extend(["", "[GATE / AUTHORITY CHECKS]"])
    lines.extend(_field_lines(report.authority_checks))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_root_semantic_reuse_gate_trace() -> str:
    return render_root_semantic_reuse_gate_trace(
        collect_root_semantic_reuse_gate_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Root-controlled Semantic Reuse Gate Trace proof."
    )
    parser.parse_args()
    print(run_root_semantic_reuse_gate_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
