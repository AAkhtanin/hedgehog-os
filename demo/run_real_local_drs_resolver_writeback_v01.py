from __future__ import annotations

from dataclasses import asdict
from tempfile import TemporaryDirectory
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.local_drs_resolver import (
    SemanticDRSRecordInput,
    SemanticResolveQuery,
    ResolvedDRSReport,
    resolve_semantic_candidates,
    write_root_final_record,
    write_semantic_record,
)


TITLE = "HEDGEHOG OS - REAL LOCAL DRS RESOLVER / WRITEBACK v0.1"
NOW = "2026-06-22T12:00:00+00:00"
OLD = "2026-01-01T00:00:00+00:00"

SCENARIOS = (
    "write_then_resolve_semantic_record_candidate_only",
    "stale_record_forces_root_review",
    "quarantine_proximity_blocks_direct_reuse",
    "changed_worldstate_blocks_old_reuse",
    "conflicting_provenance_blocks_reuse",
    "duplicate_poisoning_pressure_does_not_create_authority",
    "root_review_required_before_reuse_affects_final_output",
    "writeback_records_root_final_without_action_side_effects",
)

COMPACT_RULE = (
    "write meaning",
    "resolve meaning",
    "reuse under Root review",
    "DRS record is not truth",
    "DRS hit is not authority",
    "DRS reuse candidate is not action permission",
    "stale DRS record cannot silently reuse",
    "quarantined/deadend proximity forces review",
    "conflicting provenance blocks direct ready/reuse",
    "Root remains final authority",
)


def _time_envelope(created_at: str = NOW, freshness_class: str = "normal") -> dict[str, Any]:
    return {
        "pt_created_at": created_at,
        "kt_asof": created_at,
        "et_observed_at": created_at,
        "ct_session_anchor": "sess_real_local_drs_resolver_v01",
        "ttl_seconds": 86_400,
        "freshness_class": freshness_class,
        "valid_from": created_at,
        "valid_to": None,
    }


def _temporal_query(max_age_seconds: int = 86_400) -> dict[str, Any]:
    return {
        "as_of": NOW,
        "time_range": {"from": None, "to": NOW},
        "freshness_bias": "prefer_recent",
        "max_age_seconds": max_age_seconds,
        "freshness_required": "normal",
    }


def _trace(trace_id: str) -> dict[str, str]:
    return {"trace_id": trace_id, "kind": "real_local_drs_resolver_v01"}


def _source(source_id: str, trace_id: str = "trace:resolver") -> dict[str, Any]:
    return {
        "source": "local_drs",
        "source_id": source_id,
        "trace_ref": _trace(trace_id),
    }


def _write_certificate_record(
    drs: LocalDRS,
    *,
    record_id: str,
    summary: str = "Mock certificate renewal was completed after Root review.",
    created_at: str = NOW,
    freshness_class: str = "normal",
    layer: str = "work",
    status: str = "accepted",
    record_type: str = "task_outcome",
    extra_content: dict[str, Any] | None = None,
    source_refs: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    content = {
        "summary": summary,
        "subject_key": "certificate:demo-user",
        "claim_key": "document_readiness",
        "claim_value": "ready",
        "worldstate": {"worldstate_version": "v1"},
        "schema_valid": True,
    }
    if extra_content:
        content.update(extra_content)
    return write_semantic_record(
        drs,
        SemanticDRSRecordInput(
            record_id=record_id,
            layer=layer,
            record_type=record_type,
            domain="mock_government_certificate",
            content=content,
            semantic_keys=("certificate", "renewal", "document_readiness"),
            time_envelope=_time_envelope(created_at, freshness_class),
            trace_refs=(_trace(f"trace:{record_id}"),),
            source_refs=source_refs or (_source(f"source:{record_id}", f"trace:{record_id}"),),
            status=status,
        ),
    )


def _resolve_certificate(drs: LocalDRS, scenario_id: str, **overrides: Any) -> ResolvedDRSReport:
    query = SemanticResolveQuery(
        query_id=f"query:{scenario_id}",
        domain="mock_government_certificate",
        semantic_terms=("certificate", "renewal", "document_readiness"),
        content_filters={"subject_key": "certificate:demo-user"},
        temporal_query=_temporal_query(),
        worldstate=overrides.pop("worldstate", {"worldstate_version": "v1"}),
        require_root_review=True,
        **overrides,
    )
    return resolve_semantic_candidates(drs, query)


def _scenario_result(
    scenario_id: str,
    report: ResolvedDRSReport,
    *,
    records_written: int,
    expected_reason: str,
    extra_pass: bool = True,
) -> dict[str, Any]:
    reasons = set(report.reason_codes)
    passed = (
        report.candidate_count > 0
        and report.direct_reuse_allowed_count == 0
        and report.counters["action_permission_granted_count"] == 0
        and report.root_review_required
        and expected_reason in reasons
        and extra_pass
    )
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if passed else "FAIL",
        "records_written": records_written,
        "resolve_queries": 1,
        "candidate_count": report.candidate_count,
        "root_final_authority_preserved": report.authority_boundary[
            "root_final_authority_preserved"
        ],
        "report": report,
        "reason_codes": tuple(report.reason_codes),
    }


def _run_resolve_scenario(scenario_id: str) -> dict[str, Any]:
    with TemporaryDirectory(prefix="hedgehog_real_local_drs_") as tmpdir:
        drs = LocalDRS(tmpdir)
        records_written = 0

        if scenario_id == "write_then_resolve_semantic_record_candidate_only":
            _write_certificate_record(drs, record_id="record:fresh_candidate")
            records_written = 1
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="candidate_only_root_review_required",
            )

        if scenario_id == "stale_record_forces_root_review":
            _write_certificate_record(
                drs,
                record_id="record:stale_candidate",
                created_at=OLD,
                freshness_class="stale",
            )
            records_written = 1
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="stale_record_forces_root_review",
                extra_pass=report.counters["stale_record_reuse_blocked_count"] > 0,
            )

        if scenario_id == "quarantine_proximity_blocks_direct_reuse":
            _write_certificate_record(
                drs,
                record_id="record:quarantine_candidate",
                layer="quarantine",
                status="quarantined",
                extra_content={"quarantine_proximity": True},
            )
            records_written = 1
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="quarantine_proximity_blocks_direct_reuse",
                extra_pass=report.counters["quarantine_reuse_blocked_count"] > 0,
            )

        if scenario_id == "changed_worldstate_blocks_old_reuse":
            _write_certificate_record(drs, record_id="record:old_worldstate")
            records_written = 1
            report = _resolve_certificate(
                drs,
                scenario_id,
                worldstate={"worldstate_version": "v2"},
            )
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="changed_worldstate_blocks_old_reuse",
                extra_pass=report.counters["changed_worldstate_reuse_blocked_count"] > 0,
            )

        if scenario_id == "conflicting_provenance_blocks_reuse":
            _write_certificate_record(
                drs,
                record_id="record:conflicting_provenance",
                extra_content={"conflicting_provenance": True},
            )
            records_written = 1
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="conflicting_provenance_blocks_reuse",
                extra_pass=report.counters["conflicting_provenance_blocked_count"] > 0,
            )

        if scenario_id == "duplicate_poisoning_pressure_does_not_create_authority":
            for suffix in ("a", "b"):
                _write_certificate_record(
                    drs,
                    record_id=f"record:duplicate_poison:{suffix}",
                    extra_content={
                        "duplicate_group": "poisoned_certificate_reuse",
                        "poisoning_markers": ["duplicate_spam"],
                        "repeated_external_pointer_count": 3,
                    },
                    source_refs=(
                        {
                            "source": "external_drs",
                            "source_id": f"external:pointer:{suffix}",
                            "trace_ref": _trace(f"trace:external_pointer:{suffix}"),
                        },
                    ),
                )
            records_written = 2
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="duplicate_poisoning_pressure_does_not_create_authority",
                extra_pass=(
                    report.counters["duplicate_poisoning_records_seen_count"] == 2
                    and report.counters["poisoning_pressure_authority_claimed_count"] == 0
                ),
            )

        if scenario_id == "root_review_required_before_reuse_affects_final_output":
            _write_certificate_record(
                drs,
                record_id="record:root_review_required",
                extra_content={"accepted_evidence": True},
            )
            records_written = 1
            report = _resolve_certificate(drs, scenario_id)
            return _scenario_result(
                scenario_id,
                report,
                records_written=records_written,
                expected_reason="root_review_required_before_reuse_affects_final_output",
            )

    raise ValueError(f"unknown resolve scenario: {scenario_id}")


def _run_writeback_scenario() -> dict[str, Any]:
    scenario_id = "writeback_records_root_final_without_action_side_effects"
    with TemporaryDirectory(prefix="hedgehog_real_local_drs_writeback_") as tmpdir:
        drs = LocalDRS(tmpdir)
        artifact = {
            "artifact_type": "RootFinal",
            "final_artifact_id": "root_final:semantic_reuse:001",
            "created_by": "root_orchestrator",
            "root_reviewed": True,
            "root_final_status": "accepted",
            "domain": "mock_government_certificate",
            "summary": "Root-reviewed local semantic outcome.",
            "trace_refs": [_trace("trace:root_final_writeback")],
            "production_persistence_claimed": False,
            "real_external_action_executed": False,
            "connector_side_effects": False,
        }
        record = write_root_final_record(drs, artifact)
        loaded = drs.read_record("work", record["record_id"])
        passed = (
            loaded["content"]["local_writeback_only"] is True
            and loaded["content"]["action_side_effects"] is False
            and loaded["content"]["connector_side_effects"] is False
            and loaded["content"]["production_persistence_claimed"] is False
            and loaded["content"]["root_final_authority_preserved"] is True
        )
        return {
            "scenario_id": scenario_id,
            "status": "PASS" if passed else "FAIL",
            "records_written": 1,
            "resolve_queries": 0,
            "candidate_count": 0,
            "root_final_authority_preserved": True,
            "report": None,
            "reason_codes": ("writeback_without_action_side_effects",),
        }


def evaluate_scenario(scenario_id: str) -> dict[str, Any]:
    if scenario_id == "writeback_records_root_final_without_action_side_effects":
        return _run_writeback_scenario()
    return _run_resolve_scenario(scenario_id)


def _empty_counters() -> dict[str, int]:
    return {
        "records_written_count": 0,
        "resolve_queries_count": 0,
        "candidates_returned_count": 0,
        "direct_reuse_allowed_count": 0,
        "root_review_required_count": 0,
        "stale_record_reuse_blocked_count": 0,
        "quarantine_reuse_blocked_count": 0,
        "changed_worldstate_reuse_blocked_count": 0,
        "conflicting_provenance_blocked_count": 0,
        "duplicate_poisoning_records_seen_count": 0,
        "poisoning_pressure_authority_claimed_count": 0,
        "action_permission_granted_count": 0,
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "production_drs_used_count": 0,
        "external_drs_used_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "root_final_authority_preserved_count": 0,
    }


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIOS]
    counters = _empty_counters()
    for scenario in scenarios:
        counters["records_written_count"] += scenario["records_written"]
        counters["resolve_queries_count"] += scenario["resolve_queries"]
        counters["root_final_authority_preserved_count"] += int(
            scenario["root_final_authority_preserved"]
        )
        report = scenario["report"]
        if report is None:
            continue
        for key, value in report.counters.items():
            if key in counters:
                counters[key] += value

    scenarios_passed = sum(1 for scenario in scenarios if scenario["status"] == "PASS")
    pass_conditions = {
        "scenarios_total_is_8": len(scenarios) == 8,
        "scenarios_passed": scenarios_passed == len(scenarios),
        "direct_reuse_allowed_count_zero": counters["direct_reuse_allowed_count"] == 0,
        "poisoning_pressure_authority_claimed_count_zero": (
            counters["poisoning_pressure_authority_claimed_count"] == 0
        ),
        "action_permission_granted_count_zero": counters["action_permission_granted_count"] == 0,
        "manifest_mutation_count_zero": counters["manifest_mutation_count"] == 0,
        "transition_matrix_mutation_count_zero": counters["transition_matrix_mutation_count"] == 0,
        "production_drs_used_count_zero": counters["production_drs_used_count"] == 0,
        "external_drs_used_count_zero": counters["external_drs_used_count"] == 0,
        "network_used_count_zero": counters["network_used_count"] == 0,
        "gemini_used_count_zero": counters["gemini_used_count"] == 0,
        "root_final_authority_preserved": (
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


def _format_report_value(value: Any) -> Any:
    if isinstance(value, ResolvedDRSReport):
        return asdict(value)
    return value


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_all_scenarios()
    lines = [
        TITLE,
        "",
        "compact_rule:",
        *[f"- {line}" for line in COMPACT_RULE],
        "",
        "scenario table:",
        "scenario_id | status | candidates | reasons",
    ]
    for scenario in result["scenarios"]:
        lines.append(
            f"{scenario['scenario_id']} | {scenario['status']} | "
            f"{scenario['candidate_count']} | {', '.join(scenario['reason_codes'])}"
        )
    lines.extend(["", "aggregate counters:"])
    lines.append(f"scenarios_total: {result['scenarios_total']}")
    lines.append(f"scenarios_passed: {result['scenarios_passed']}")
    for key in sorted(result["counters"]):
        lines.append(f"{key}: {result['counters'][key]}")
    lines.extend(
        [
            "",
            "authority boundary summary:",
            "DRS record is not truth",
            "DRS hit is not authority",
            "DRS reuse candidate is not action permission",
            "Root remains final authority",
            "",
            "limitations:",
            "local file-backed DRS only",
            "no production DRS",
            "no external/global DRS",
            "no network",
            "no Gemini",
            "no autonomous action",
            "no connector side effects",
            "no manifest mutation",
            "no transition matrix mutation",
            "",
            f"FINAL STATUS: {result['final_status']}",
        ]
    )
    return "\n".join(str(_format_report_value(line)) for line in lines)


def main() -> int:
    result = run_all_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
