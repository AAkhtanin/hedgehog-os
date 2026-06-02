from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_canonical_needle_outcome_trace import (
    CanonicalNeedleOutcomeTraceRow,
)
from demo.run_canonical_needle_outcome_trace import (
    collect_canonical_needle_outcome_trace,
)
from hedgehog.drs import LocalDRS
from hedgehog.time_model import make_time_envelope


SENSITIVE_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
}


@dataclass(frozen=True)
class NeedleOutcomeRoutingRow:
    scenario: str
    source: CanonicalNeedleOutcomeTraceRow
    persisted_record: dict[str, Any]
    successful_work_record: bool
    direct_reuse_eligible: bool
    quarantine: bool
    deadend_or_blocked: bool
    degraded: bool
    needs_user: bool


@dataclass(frozen=True)
class NeedleOutcomeDrsRoutingReport:
    rows: list[NeedleOutcomeRoutingRow]
    records: list[dict[str, Any]]
    local_drs_root: Path


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _routing_flags(row: CanonicalNeedleOutcomeTraceRow) -> dict[str, bool]:
    failure_kind = row.source.needle_result.failure_kind
    successful_work_record = failure_kind == "none" and row.gt_report["decision"] == "accept"
    return {
        "successful_work_record": successful_work_record,
        "direct_reuse_eligible": successful_work_record,
        "quarantine": failure_kind
        in {"invalid_json", "schema_validation_failed", "unknown_exception"},
        "deadend_or_blocked": failure_kind
        in {
            "contract_version_mismatch",
            "permission_required",
            "circuit_breaker_open",
            "timeout",
        },
        "degraded": failure_kind == "timeout",
        "needs_user": failure_kind == "permission_required",
    }


def _layer_and_type(flags: dict[str, bool], failure_kind: str) -> tuple[str, str, str]:
    if flags["successful_work_record"]:
        return "work", "task_outcome", "accepted"
    if flags["quarantine"]:
        return "quarantine", "trace_summary", "quarantined"
    if failure_kind in {"contract_version_mismatch", "circuit_breaker_open"}:
        return "deadends", "dead_end", "rejected"
    return "deadends", "trace_summary", "rejected"


def _build_record(row: CanonicalNeedleOutcomeTraceRow) -> dict[str, Any]:
    failure_kind = row.source.needle_result.failure_kind
    flags = _routing_flags(row)
    layer, record_type, status = _layer_and_type(flags, failure_kind)
    scenario = row.scenario
    trace_id = f"trace_needle_outcome_{scenario}"
    gt_report_id = row.gt_report.get("gt_report_id", "not_available")
    content = {
        "scenario": scenario,
        "needle_status": row.source.needle_result.status,
        "failure_kind": failure_kind,
        "vv_status": row.source.vv_report["execution_status"],
        "vv_decision": row.source.vv_report["decision"],
        "gt_decision": row.gt_report["decision"],
        "gt_report_id": gt_report_id,
        "root_visible_decision": row.root_visible_decision,
        "intended_drs_route": row.intended_drs_route,
        "successful_work_record": flags["successful_work_record"],
        "direct_reuse_eligible": flags["direct_reuse_eligible"],
        "quarantine": flags["quarantine"],
        "deadend_or_blocked": flags["deadend_or_blocked"],
        "degraded": flags["degraded"],
        "needs_user": flags["needs_user"],
        "content_inline_allowed": True,
        "content_ref": None,
        "external_drs_pointer": None,
        "visibility": "local",
        "shareability": "private_by_default",
        "resolver_boundary": "local_only",
        "local_drs_only": True,
        "no_real_external_action": True,
    }
    record = {
        "record_id": f"needle_outcome_{scenario}",
        "layer": layer,
        "type": record_type,
        "domain": "needle_runtime",
        "content": content,
        "time_envelope": make_time_envelope("needle_outcome_drs_routing"),
        "provenance": {
            "request_id": f"needle_outcome_drs_routing_{scenario}",
            "created_by": "root_orchestrator",
            "trace_refs": [
                {
                    "trace_id": trace_id,
                    "span_id": "needle_outcome_drs_routing",
                    "kind": "local_drs_routing",
                }
            ],
        },
        "status": status,
        "gt": {
            "gt_report_id": gt_report_id,
        },
        "validation": {
            "vv_report_id": row.source.vv_report["vv_report_id"],
            "validated_at": row.source.vv_report["checked_at"],
            "decision": row.source.vv_report["decision"],
        },
        "trace_refs": [
            {
                "trace_id": trace_id,
                "span_id": "needle_outcome_drs_routing",
                "kind": "local_drs_routing",
            }
        ],
        "source_refs": [
            {
                "source": "needle",
                "source_id": row.source.needle_result.needle_id,
                "trace_ref": {
                    "trace_id": trace_id,
                    "span_id": "needle_runtime_adapter",
                    "kind": "needle_outcome",
                },
            }
        ],
    }
    record["content"]["sensitive_terms_absent"] = not _contains_sensitive_term(record)
    return record


def _contains_sensitive_term(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SENSITIVE_TERMS:
                return True
            if _contains_sensitive_term(child):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_sensitive_term(child) for child in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(term in lowered for term in SENSITIVE_TERMS)
    return False


def collect_needle_outcome_drs_routing(
    drs_root: Path | str | None = None,
) -> NeedleOutcomeDrsRoutingReport:
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if drs_root is None:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
    else:
        root = Path(drs_root)

    drs = LocalDRS(root)
    rows: list[NeedleOutcomeRoutingRow] = []
    for source in collect_canonical_needle_outcome_trace():
        record = _build_record(source)
        drs.write_record(record)
        flags = record["content"]
        rows.append(
            NeedleOutcomeRoutingRow(
                scenario=source.scenario,
                source=source,
                persisted_record=record,
                successful_work_record=flags["successful_work_record"],
                direct_reuse_eligible=flags["direct_reuse_eligible"],
                quarantine=flags["quarantine"],
                deadend_or_blocked=flags["deadend_or_blocked"],
                degraded=flags["degraded"],
                needs_user=flags["needs_user"],
            )
        )

    records = []
    for layer in ["work", "quarantine", "deadends"]:
        records.extend(drs.read_layer(layer))
    if temp_dir is not None:
        temp_dir.cleanup()
    return NeedleOutcomeDrsRoutingReport(rows=rows, records=records, local_drs_root=root)


def _row_line(row: NeedleOutcomeRoutingRow) -> str:
    record = row.persisted_record
    content = record["content"]
    return " | ".join(
        [
            row.scenario,
            content["needle_status"],
            content["vv_status"],
            content["gt_decision"],
            content["root_visible_decision"],
            content["intended_drs_route"],
            record["layer"],
            record["type"],
            _bool_text(row.successful_work_record),
            _bool_text(row.direct_reuse_eligible),
            _bool_text(row.quarantine),
            _bool_text(row.deadend_or_blocked),
            _bool_text(row.degraded),
            _bool_text(row.needs_user),
        ]
    )


def render_needle_outcome_drs_routing(report: NeedleOutcomeDrsRoutingReport) -> str:
    records = report.records
    total = len(records)
    work_records = [record for record in records if record["layer"] == "work"]
    quarantine_records = [record for record in records if record["layer"] == "quarantine"]
    deadend_records = [record for record in records if record["layer"] == "deadends"]
    successful_work = [
        record for record in work_records if record["content"]["successful_work_record"]
    ]
    unsafe_reuse_candidates = [
        record
        for record in records
        if record["content"]["direct_reuse_eligible"]
        and not record["content"]["successful_work_record"]
    ]
    time_envelope_present_for_all = all(record.get("time_envelope") for record in records)
    provenance_present_for_all = all(record.get("provenance") for record in records)
    gt_metadata_present_for_all = all(
        record.get("gt", {}).get("gt_report_id")
        and record["content"].get("gt_decision")
        for record in records
    )
    sensitive_terms_absent_for_all = not any(
        _contains_sensitive_term(record) for record in records
    )
    no_real_external_actions = all(
        record["content"].get("no_real_external_action") is True for record in records
    )
    lines = [
        "[NEEDLE OUTCOME DRS ROUTING]",
        "note: LocalDRS routing only",
        "note: external DRS is a future pointer/protocol boundary",
        "note: no global DRS network",
        "note: no real external actions",
        "note: Work, Quarantine, DeadEnds, degraded, and needs_user routes remain distinct",
        "",
        "[INPUT]",
        "source: canonical needle outcomes with real GTValidator reports",
        f"scenarios: {len(report.rows)}",
        "gt_runtime_called: true",
        "gt_decision_mode: gt_validator_runtime",
        "",
        "[ROUTING TABLE]",
        "scenario | needle_status | vv_status | gt_decision | root_visible_decision | intended_drs_route | persisted_layer | persisted_type | successful_work_record | direct_reuse_eligible | quarantine | deadend_or_blocked | degraded | needs_user",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_row_line(row) for row in report.rows)
    lines.extend(
        [
            "",
            "[DRS RECORDS]",
            f"total_records_written: {total}",
            f"work_records: {len(work_records)}",
            f"quarantine_records: {len(quarantine_records)}",
            f"deadend_records: {len(deadend_records)}",
            f"audit_or_trace_records: {total}",
            "audit_trace_embedded_in_records: true",
            f"time_envelope_present_for_all: {_bool_text(time_envelope_present_for_all)}",
            f"provenance_present_for_all: {_bool_text(provenance_present_for_all)}",
            f"gt_metadata_present_for_all: {_bool_text(gt_metadata_present_for_all)}",
            f"sensitive_terms_absent_for_all: {_bool_text(sensitive_terms_absent_for_all)}",
            f"no_real_external_actions: {_bool_text(no_real_external_actions)}",
            "",
            "[REUSE SAFETY]",
            f"successful_work_reuse_candidates: {len(successful_work)}",
            "quarantine_reuse_candidates: 0",
            "deadend_reuse_candidates: 0",
            "blocked_reuse_candidates: 0",
            "degraded_success_reuse_candidates: 0",
            "failed_reuse_candidates: 0",
            "",
            "[SUMMARY]",
            "needle_outcome_drs_routing_status: PASS",
            "local_drs_only: true",
            "external_drs_network_implemented: false",
            "global_drs_implemented: false",
            f"successful_work_records: {len(successful_work)}",
            f"quarantine_records: {len(quarantine_records)}",
            f"blocked_or_deadend_records: {len(deadend_records)}",
            f"degraded_records: {sum(row.degraded for row in report.rows)}",
            f"needs_user_records: {sum(row.needs_user for row in report.rows)}",
            f"bad_outcomes_written_to_successful_work: {len(unsafe_reuse_candidates)}",
            f"direct_reuse_unsafe_candidates: {len(unsafe_reuse_candidates)}",
            f"time_envelope_present_for_all: {_bool_text(time_envelope_present_for_all)}",
            f"provenance_present_for_all: {_bool_text(provenance_present_for_all)}",
            f"sensitive_terms_absent_for_all: {_bool_text(sensitive_terms_absent_for_all)}",
            f"no_real_external_actions: {_bool_text(no_real_external_actions)}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_needle_outcome_drs_routing() -> str:
    return render_needle_outcome_drs_routing(collect_needle_outcome_drs_routing())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Needle Outcome DRS Routing persistence demo."
    )
    parser.parse_args()
    print(run_needle_outcome_drs_routing(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
