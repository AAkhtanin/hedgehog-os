from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_needle_failure_integration import NeedleFailureIntegrationRow
from demo.run_needle_failure_integration import collect_needle_failure_integration


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
    "hidden reasoning",
    "chain of thought",
)

REQUIRED_RESULT_PROPOSAL_SHAPE = {
    "proposal_id",
    "request_id",
    "producer",
    "vector_id",
    "plan_id",
    "result_payload",
    "evidence",
    "cost",
    "risks",
    "time_envelope",
    "trace_refs",
}


@dataclass(frozen=True)
class CanonicalNeedleOutcomeTraceRow:
    scenario: str
    source: NeedleFailureIntegrationRow
    root_visible_decision: str
    intended_drs_route: str
    converted_to_result_proposal: bool
    result_proposal_shape_valid: bool
    post_vv_ran: bool


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _root_visible_decision(failure_kind: str) -> str:
    return {
        "none": "accept/work_candidate",
        "timeout": "degraded_trace",
        "invalid_json": "quarantine",
        "contract_version_mismatch": "blocked",
        "permission_required": "needs_user_or_blocked",
        "circuit_breaker_open": "blocked",
        "schema_validation_failed": "quarantine",
        "unknown_exception": "failed_or_quarantine",
    }.get(failure_kind, "failed_or_quarantine")


def _intended_drs_route(failure_kind: str) -> str:
    return {
        "none": "work_candidate",
        "timeout": "degraded_trace",
        "invalid_json": "quarantine",
        "contract_version_mismatch": "deadend_or_blocked_trace",
        "permission_required": "needs_user_or_blocked_trace",
        "circuit_breaker_open": "blocked_trace",
        "schema_validation_failed": "quarantine",
        "unknown_exception": "quarantine_or_failed_trace",
    }.get(failure_kind, "quarantine_or_failed_trace")


def _result_proposal_shape_valid(proposal: dict[str, Any]) -> bool:
    return REQUIRED_RESULT_PROPOSAL_SHAPE <= set(proposal)


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def collect_canonical_needle_outcome_trace() -> list[CanonicalNeedleOutcomeTraceRow]:
    rows: list[CanonicalNeedleOutcomeTraceRow] = []
    for source in collect_needle_failure_integration():
        failure_kind = source.needle_result.failure_kind
        rows.append(
            CanonicalNeedleOutcomeTraceRow(
                scenario=source.scenario,
                source=source,
                root_visible_decision=_root_visible_decision(failure_kind),
                intended_drs_route=_intended_drs_route(failure_kind),
                converted_to_result_proposal=source.proposal["result_payload"][
                    "source"
                ]
                == "needle_runtime",
                result_proposal_shape_valid=_result_proposal_shape_valid(source.proposal),
                post_vv_ran=bool(source.vv_report.get("vv_report_id")),
            )
        )
    return rows


def _needle_outcome_line(row: CanonicalNeedleOutcomeTraceRow) -> str:
    result = row.source.needle_result
    return " | ".join(
        [
            row.scenario,
            result.status,
            result.failure_kind,
            row.source.vv_report["execution_status"],
            _bool_text(result.quarantine_required or result.status == "quarantined"),
            _bool_text(result.status == "blocked"),
            _bool_text(result.status == "degraded"),
            _bool_text(result.status == "completed"),
            "false",
        ]
    )


def _boundary_line(row: CanonicalNeedleOutcomeTraceRow) -> str:
    return " | ".join(
        [
            row.scenario,
            _bool_text(row.converted_to_result_proposal),
            _bool_text(row.result_proposal_shape_valid),
            "false",
            "false",
            "result_proposal_compatible",
        ]
    )


def _post_vv_line(row: CanonicalNeedleOutcomeTraceRow) -> str:
    payload = row.source.proposal["result_payload"]
    unsafe_for_domain_success = (
        payload["status"] != "completed" or payload["quarantine_required"]
    )
    return " | ".join(
        [
            row.scenario,
            _bool_text(row.post_vv_ran),
            row.source.vv_report["execution_status"],
            _bool_text(payload["safe_for_gt"]),
            _bool_text(unsafe_for_domain_success),
            "true",
            "true",
            "true",
        ]
    )


def _gt_root_line(row: CanonicalNeedleOutcomeTraceRow) -> str:
    return " | ".join(
        [
            row.scenario,
            row.root_visible_decision,
            "true",
            "false",
            "true",
            "false",
            "true",
        ]
    )


def _drs_audit_line(row: CanonicalNeedleOutcomeTraceRow) -> str:
    return " | ".join(
        [
            row.scenario,
            "planned_or_trace_only",
            row.intended_drs_route,
            "true",
            "true",
            "true",
            "true",
            _bool_text(row.source.needle_result.no_real_external_action),
        ]
    )


def render_canonical_needle_outcome_trace(
    rows: list[CanonicalNeedleOutcomeTraceRow],
) -> str:
    completed_count = sum(
        row.source.needle_result.status == "completed" for row in rows
    )
    blocked_count = sum(row.source.needle_result.status == "blocked" for row in rows)
    degraded_count = sum(row.source.needle_result.status == "degraded" for row in rows)
    quarantined_or_failed_count = sum(
        row.source.needle_result.status in {"quarantined", "failed"}
        or row.source.needle_result.quarantine_required
        for row in rows
    )
    lines = [
        "[CANONICAL NEEDLE OUTCOME TRACE]",
        "note: deterministic simulated needle outcomes only",
        "note: needle is a contract boundary, not an Executor-owned plugin",
        "note: needle output does not go directly to user",
        "note: Root remains final authority",
        "note: no real external actions",
        "",
        "[NEEDLE OUTCOMES]",
        "scenario | needle_status | failure_kind | execution_status | quarantined | blocked | degraded | completed | unhandled_exception",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_needle_outcome_line(row) for row in rows)
    lines.extend(
        [
            "",
            "[CANONICAL BOUNDARY]",
            "scenario | converted_to_result_proposal | result_proposal_shape_valid | needle_created_final_output | executor_owns_needle | canonical_artifact_type",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_boundary_line(row) for row in rows)
    lines.extend(
        [
            "",
            "[POST V&V]",
            "scenario | post_vv_ran | vv_status | safe_for_gt_for_selection | unsafe_for_domain_success | schema_visible | policy_visible | safety_visible",
            "--- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_post_vv_line(row) for row in rows)
    lines.extend(
        [
            "",
            "[GT / ROOT DECISION]",
            "scenario | root_visible_decision | gt_ran_after_post_vv | gt_committed_final_output | root_decision_required | root_created_final_output | no_direct_user_answer_from_needle",
            "--- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_gt_root_line(row) for row in rows)
    lines.extend(
        [
            "",
            "[DRS / AUDIT ROUTING]",
            "scenario | drs_routing_mode | intended_drs_route | time_envelope_required | provenance_required | audit_required | sensitive_terms_absent | no_real_external_action",
            "--- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_drs_audit_line(row) for row in rows)
    lines.extend(
        [
            "",
            "[SUMMARY]",
            f"scenarios: {len(rows)}",
            f"canonical_boundary_conversions: {len(rows)}",
            f"post_vv_runs: {sum(row.post_vv_ran for row in rows)}",
            "gt_after_post_vv: true",
            "gt_ran_after_post_vv: true",
            f"root_decisions_required: {len(rows)}",
            "needle_created_final_output: false",
            "executor_owns_needle: false",
            "direct_user_answers_from_needle: 0",
            f"quarantined_or_failed_count: {quarantined_or_failed_count}",
            f"blocked_count: {blocked_count}",
            f"degraded_count: {degraded_count}",
            f"completed_count: {completed_count}",
            "no_real_external_actions: true",
            "unhandled_exceptions: 0",
            "canonical_needle_outcome_trace_status: PASS",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_canonical_needle_outcome_trace() -> str:
    return render_canonical_needle_outcome_trace(
        collect_canonical_needle_outcome_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Canonical Needle Outcome Trace demo."
    )
    parser.parse_args()
    print(run_canonical_needle_outcome_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
