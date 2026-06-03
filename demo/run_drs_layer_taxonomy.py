from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_needle_outcome_drs_routing import (
    NeedleOutcomeDrsRoutingReport,
    NeedleOutcomeRoutingRow,
    collect_needle_outcome_drs_routing,
)


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


@dataclass(frozen=True)
class DrsTaxonomyRow:
    scenario: str
    original_layer: str
    original_type: str
    needle_status: str
    failure_kind: str
    gt_decision: str
    root_visible_decision: str
    taxonomy_kind: str
    routing_class: str
    successful_work_record: bool
    direct_reuse_eligible: bool
    reuse_policy: str
    work_allowed: bool
    quarantine_allowed: bool
    deadend_layer_allowed: bool
    needs_user: bool
    degraded: bool
    blocked: bool
    stable_dead_end: bool


@dataclass(frozen=True)
class DrsLayerTaxonomyReport:
    source_report: NeedleOutcomeDrsRoutingReport
    rows: list[DrsTaxonomyRow]
    safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _taxonomy_for(row: NeedleOutcomeRoutingRow) -> tuple[str, str]:
    content = row.persisted_record["content"]
    failure_kind = content["failure_kind"]
    if row.successful_work_record:
        return "work_candidate", "successful_work"
    if failure_kind == "invalid_json":
        return "quarantine", "invalid_payload"
    if failure_kind == "schema_validation_failed":
        return "quarantine", "schema_failed"
    if failure_kind == "unknown_exception":
        return "quarantine", "unknown_exception"
    if failure_kind == "timeout":
        return "degraded_trace", "timeout"
    if failure_kind == "permission_required":
        return "needs_user_trace", "permission_required"
    if failure_kind == "contract_version_mismatch":
        return "dead_end", "contract_boundary"
    if failure_kind == "circuit_breaker_open":
        return "blocked_trace", "circuit_breaker"
    return "blocked_trace", failure_kind


def _classify_row(row: NeedleOutcomeRoutingRow) -> DrsTaxonomyRow:
    record = row.persisted_record
    content = record["content"]
    taxonomy_kind, routing_class = _taxonomy_for(row)
    successful_work = bool(content["successful_work_record"])
    direct_reuse_eligible = bool(content["direct_reuse_eligible"])
    blocked = taxonomy_kind in {"blocked_trace", "dead_end", "needs_user_trace"} or bool(
        content["deadend_or_blocked"]
    )
    stable_dead_end = taxonomy_kind == "dead_end"
    return DrsTaxonomyRow(
        scenario=row.scenario,
        original_layer=record["layer"],
        original_type=record["type"],
        needle_status=content["needle_status"],
        failure_kind=content["failure_kind"],
        gt_decision=content["gt_decision"],
        root_visible_decision=content["root_visible_decision"],
        taxonomy_kind=taxonomy_kind,
        routing_class=routing_class,
        successful_work_record=successful_work,
        direct_reuse_eligible=direct_reuse_eligible,
        reuse_policy=(
            "eligible_work_only" if direct_reuse_eligible else "not_reuse_eligible"
        ),
        work_allowed=record["layer"] == "work" and successful_work,
        quarantine_allowed=record["layer"] == "quarantine" and not successful_work,
        deadend_layer_allowed=record["layer"] == "deadends" and not successful_work,
        needs_user=taxonomy_kind == "needs_user_trace",
        degraded=taxonomy_kind == "degraded_trace",
        blocked=blocked,
        stable_dead_end=stable_dead_end,
    )


def _taxonomy_does_not_override_policy(rows: list[DrsTaxonomyRow]) -> bool:
    unsafe_taxonomy_kinds = {
        "quarantine",
        "dead_end",
        "blocked_trace",
        "degraded_trace",
        "needs_user_trace",
    }
    direct_reuse_rows = [row for row in rows if row.direct_reuse_eligible]
    return (
        all(row.successful_work_record for row in direct_reuse_rows)
        and all(row.taxonomy_kind == "work_candidate" for row in direct_reuse_rows)
        and not any(
            row.direct_reuse_eligible and row.taxonomy_kind in unsafe_taxonomy_kinds
            for row in rows
        )
    )


def _broad_deadends_semantics_clarified(
    rows: list[DrsTaxonomyRow],
    *,
    degraded_trace_records: int,
    needs_user_trace_records: int,
    dead_end_or_blocked_records: int,
) -> bool:
    rows_by_failure = {row.failure_kind: row for row in rows}
    timeout_row = rows_by_failure.get("timeout")
    permission_row = rows_by_failure.get("permission_required")
    return (
        degraded_trace_records >= 1
        and needs_user_trace_records >= 1
        and dead_end_or_blocked_records >= 2
        and timeout_row is not None
        and timeout_row.taxonomy_kind == "degraded_trace"
        and permission_row is not None
        and permission_row.taxonomy_kind == "needs_user_trace"
    )


def _direct_reuse_policy_unchanged(
    rows: list[DrsTaxonomyRow], safety: dict[str, Any]
) -> bool:
    direct_reuse_rows = [row for row in rows if row.direct_reuse_eligible]
    return (
        safety["direct_reuse_candidates"] == 1
        and safety["unsafe_direct_reuse_candidates"] == 0
        and len(direct_reuse_rows) == 1
        and direct_reuse_rows[0].scenario == "needle_success_mock"
        and direct_reuse_rows[0].taxonomy_kind == "work_candidate"
        and direct_reuse_rows[0].successful_work_record
    )


def _safety(rows: list[DrsTaxonomyRow]) -> dict[str, Any]:
    successful_work = [row for row in rows if row.successful_work_record]
    direct_reuse = [row for row in rows if row.direct_reuse_eligible]
    unsafe_direct_reuse = [
        row
        for row in direct_reuse
        if not row.successful_work_record or row.taxonomy_kind != "work_candidate"
    ]
    return {
        "taxonomy_does_not_override_policy": _taxonomy_does_not_override_policy(rows),
        "successful_work_records": len(successful_work),
        "direct_reuse_candidates": len(direct_reuse),
        "unsafe_direct_reuse_candidates": len(unsafe_direct_reuse),
        "quarantine_direct_reuse_candidates": sum(
            row.direct_reuse_eligible for row in rows if row.taxonomy_kind == "quarantine"
        ),
        "deadend_direct_reuse_candidates": sum(
            row.direct_reuse_eligible for row in rows if row.stable_dead_end
        ),
        "blocked_direct_reuse_candidates": sum(
            row.direct_reuse_eligible for row in rows if row.blocked
        ),
        "degraded_direct_reuse_candidates": sum(
            row.direct_reuse_eligible for row in rows if row.degraded
        ),
        "needs_user_direct_reuse_candidates": sum(
            row.direct_reuse_eligible for row in rows if row.needs_user
        ),
        "degraded_trace_not_successful_work": all(
            not row.successful_work_record for row in rows if row.degraded
        ),
        "needs_user_trace_not_completed_action": all(
            not row.successful_work_record for row in rows if row.needs_user
        ),
        "blocked_trace_not_success": all(
            not row.successful_work_record
            for row in rows
            if row.taxonomy_kind == "blocked_trace"
        ),
        "quarantine_not_work": all(
            row.original_layer == "quarantine" and not row.successful_work_record
            for row in rows
            if row.taxonomy_kind == "quarantine"
        ),
    }


def _summary(rows: list[DrsTaxonomyRow], safety: dict[str, Any]) -> dict[str, Any]:
    quarantine_records = sum(row.taxonomy_kind == "quarantine" for row in rows)
    dead_or_blocked = sum(
        row.taxonomy_kind in {"dead_end", "blocked_trace"} for row in rows
    )
    degraded = sum(row.taxonomy_kind == "degraded_trace" for row in rows)
    needs_user = sum(row.taxonomy_kind == "needs_user_trace" for row in rows)
    broad_deadends_semantics_clarified = _broad_deadends_semantics_clarified(
        rows,
        degraded_trace_records=degraded,
        needs_user_trace_records=needs_user,
        dead_end_or_blocked_records=dead_or_blocked,
    )
    direct_reuse_policy_unchanged = _direct_reuse_policy_unchanged(rows, safety)
    pass_status = (
        len(rows) == 8
        and safety["successful_work_records"] == 1
        and safety["direct_reuse_candidates"] == 1
        and safety["unsafe_direct_reuse_candidates"] == 0
        and quarantine_records >= 3
        and dead_or_blocked >= 2
        and degraded >= 1
        and needs_user >= 1
        and broad_deadends_semantics_clarified
        and direct_reuse_policy_unchanged
        and safety["taxonomy_does_not_override_policy"]
        and safety["degraded_trace_not_successful_work"]
        and safety["needs_user_trace_not_completed_action"]
        and safety["blocked_trace_not_success"]
        and safety["quarantine_not_work"]
    )
    return {
        "drs_layer_taxonomy_status": "PASS" if pass_status else "FAIL",
        "records_classified": len(rows),
        "work_candidates": safety["successful_work_records"],
        "quarantine_records": quarantine_records,
        "dead_end_or_blocked_records": dead_or_blocked,
        "degraded_trace_records": degraded,
        "needs_user_trace_records": needs_user,
        "broad_deadends_semantics_clarified": broad_deadends_semantics_clarified,
        "direct_reuse_policy_unchanged": direct_reuse_policy_unchanged,
        "unsafe_direct_reuse_candidates": safety["unsafe_direct_reuse_candidates"],
        "local_drs_only": True,
        "external_drs_network_implemented": False,
        "global_drs_implemented": False,
        "schema_refactor_performed": False,
    }


def collect_drs_layer_taxonomy() -> DrsLayerTaxonomyReport:
    source_report = collect_needle_outcome_drs_routing()
    rows = [_classify_row(row) for row in source_report.rows]
    safety = _safety(rows)
    summary = _summary(rows, safety)
    return DrsLayerTaxonomyReport(
        source_report=source_report,
        rows=rows,
        safety=safety,
        summary=summary,
    )


def _row_line(row: DrsTaxonomyRow) -> str:
    return " | ".join(
        [
            row.scenario,
            row.original_layer,
            row.original_type,
            row.needle_status,
            row.failure_kind,
            row.gt_decision,
            row.root_visible_decision,
            row.taxonomy_kind,
            row.routing_class,
            _bool_text(row.successful_work_record),
            _bool_text(row.direct_reuse_eligible),
            row.reuse_policy,
            _bool_text(row.work_allowed),
            _bool_text(row.quarantine_allowed),
            _bool_text(row.deadend_layer_allowed),
            _bool_text(row.needs_user),
            _bool_text(row.degraded),
            _bool_text(row.blocked),
            _bool_text(row.stable_dead_end),
        ]
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def render_drs_layer_taxonomy(report: DrsLayerTaxonomyReport) -> str:
    lines = [
        "[DRS LAYER TAXONOMY]",
        "note: LocalDRS taxonomy proof only",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no schema refactor in v0.1 unless explicitly needed",
        "note: taxonomy clarifies broad deadends semantics",
        "note: taxonomy does not change direct reuse policy",
        "",
        "[INPUT]",
        "source: needle outcome DRS routing records",
        f"records_loaded: {len(report.source_report.records)}",
        "local_drs_only: true",
        "external_drs_network_implemented: false",
        "global_drs_implemented: false",
        "",
        "[TAXONOMY TABLE]",
        "scenario | original_layer | original_type | needle_status | failure_kind | gt_decision | root_visible_decision | taxonomy_kind | routing_class | successful_work_record | direct_reuse_eligible | reuse_policy | work_allowed | quarantine_allowed | deadend_layer_allowed | needs_user | degraded | blocked | stable_dead_end",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_row_line(row) for row in report.rows)
    lines.extend(["", "[SAFETY]"])
    lines.extend(_field_lines(report.safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_drs_layer_taxonomy() -> str:
    return render_drs_layer_taxonomy(collect_drs_layer_taxonomy())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DRS Layer Taxonomy demo.")
    parser.parse_args()
    print(run_drs_layer_taxonomy(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
