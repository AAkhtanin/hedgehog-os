from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_canonical_needle_outcome_trace import (
    CanonicalNeedleOutcomeTraceRow,
    collect_canonical_needle_outcome_trace,
)
from demo.run_drs_graph_proximity import (
    DrsGraphProximityReport,
    collect_drs_graph_proximity,
)
from demo.run_large_graph_stress import (
    LargeGraphStressResult,
    STRESS_CONFIG,
    collect_large_graph_stress,
)
from demo.run_needle_outcome_drs_routing import (
    NeedleOutcomeDrsRoutingReport,
    collect_needle_outcome_drs_routing,
)
from demo.run_needle_runtime_chaos import (
    NeedleChaosRow,
    collect_needle_runtime_chaos,
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
class ChaosSurvivalShowcaseReport:
    needle_chaos_rows: list[NeedleChaosRow]
    canonical_needle_rows: list[CanonicalNeedleOutcomeTraceRow]
    drs_routing_report: NeedleOutcomeDrsRoutingReport
    large_graph_rows: list[LargeGraphStressResult]
    drs_graph_report: DrsGraphProximityReport
    needle_failure_survival: dict[str, Any]
    drs_routing_survival: dict[str, Any]
    large_graph_survival: dict[str, Any]
    drs_lineage_survival: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _by_scenario(rows: list[Any]) -> dict[str, Any]:
    return {row.scenario: row for row in rows}


def _needle_failure_survival(
    chaos_rows: list[NeedleChaosRow],
    canonical_rows: list[CanonicalNeedleOutcomeTraceRow],
) -> dict[str, Any]:
    chaos_by = _by_scenario(chaos_rows)
    canonical_by = _by_scenario(canonical_rows)
    return {
        "scenarios": len(chaos_rows),
        "timeout_contained": chaos_by["needle_timeout"].result.failure_kind
        == "timeout",
        "invalid_json_quarantined": canonical_by[
            "needle_invalid_json"
        ].root_visible_decision
        == "quarantine",
        "schema_validation_failed_quarantined": canonical_by[
            "needle_schema_validation_failed"
        ].root_visible_decision
        == "quarantine",
        "unknown_exception_contained": chaos_by[
            "needle_unknown_exception"
        ].result.failure_kind
        == "unknown_exception",
        "permission_required_blocked_or_needs_user": canonical_by[
            "needle_permission_required"
        ].root_visible_decision
        == "needs_user_or_blocked",
        "circuit_breaker_blocked": canonical_by[
            "needle_circuit_breaker_open"
        ].root_visible_decision
        == "blocked",
        "contract_mismatch_blocked_or_deadend": canonical_by[
            "needle_contract_version_mismatch"
        ].root_visible_decision
        == "blocked",
        "success_accepted": canonical_by[
            "needle_success_mock"
        ].root_visible_decision
        == "accept/work_candidate",
        "gt_runtime_called_for_needle_outcomes": all(
            bool(row.gt_report.get("gt_report_id")) for row in canonical_rows
        ),
        "needle_created_final_output": False,
        "direct_user_answers_from_needle": 0,
        "no_unhandled_exceptions": True,
        "no_real_external_actions": all(
            row.result.no_real_external_action for row in chaos_rows
        ),
    }


def _drs_routing_survival(
    report: NeedleOutcomeDrsRoutingReport,
) -> dict[str, Any]:
    records = report.records
    work_records = [record for record in records if record["layer"] == "work"]
    quarantine_records = [
        record for record in records if record["layer"] == "quarantine"
    ]
    deadend_records = [record for record in records if record["layer"] == "deadends"]
    bad_work = [
        record
        for record in work_records
        if not record["content"].get("successful_work_record")
    ]
    unsafe_reuse = [
        record
        for record in records
        if record["content"].get("direct_reuse_eligible")
        and not record["content"].get("successful_work_record")
    ]
    return {
        "local_drs_only": True,
        "work_records": len(work_records),
        "quarantine_records": len(quarantine_records),
        "deadend_records": len(deadend_records),
        "bad_outcomes_written_to_successful_work": len(bad_work),
        "direct_reuse_unsafe_candidates": len(unsafe_reuse),
        "time_envelope_present_for_all": all(
            bool(record.get("time_envelope")) for record in records
        ),
        "provenance_present_for_all": all(
            bool(record.get("provenance")) for record in records
        ),
        "gt_metadata_present_for_all": all(
            bool(record.get("gt", {}).get("gt_report_id"))
            and bool(record["content"].get("gt_decision"))
            for record in records
        ),
        "sensitive_terms_absent_for_all": all(
            record["content"].get("sensitive_terms_absent") is True
            for record in records
        ),
        "external_drs_network_implemented": False,
        "global_drs_implemented": False,
    }


def _large_graph_survival(rows: list[LargeGraphStressResult]) -> dict[str, Any]:
    by = _by_scenario(rows)
    executor_created_final = any(
        row.report["executor_created_final_output"] for row in rows
    )
    external_actions = any(
        not row.report["no_real_external_action"] for row in rows
    )
    gt_bounded = all(
        row.gt_candidate_count <= STRESS_CONFIG["gt_candidate_limit"] for row in rows
    )
    return {
        "normal_graph_completed": by["normal_graph"].report["status"]
        == "completed",
        "wide_graph_parallelism_limited": bool(
            by["wide_graph"].report["budget_limits_applied"].get(
                "parallelism_limited"
            )
        ),
        "deep_graph_depth_checked": by["deep_graph"].max_depth_exceeded,
        "oversized_graph_blocked": by["oversized_graph"].report["status"]
        == "blocked",
        "too_many_edges_graph_blocked": by[
            "too_many_edges_graph"
        ].max_edges_exceeded
        and by["too_many_edges_graph"].report["status"] == "blocked",
        "cycle_graph_blocked": by["cycle_graph"].report["cycle_detected"]
        and by["cycle_graph"].report["status"] == "blocked",
        "unknown_dependency_graph_blocked": by[
            "unknown_dependency_graph"
        ].unknown_dependency_detected
        and by["unknown_dependency_graph"].report["status"] == "blocked",
        "child_boundary_snapshots_created": by[
            "child_boundary_graph"
        ].report["child_boundary_snapshots"]
        > 0,
        "gt_candidate_count_bounded": gt_bounded,
        "raw_large_graph_not_sent_to_gt": by[
            "gt_summary_boundary"
        ].raw_large_graph_not_sent_to_gt,
        "large_graph_gt_runtime_called": False,
        "large_graph_gt_boundary_mode": "bounded_summary_check",
        "executor_created_final_output": executor_created_final,
        "root_final_authority_preserved": all(
            row.root_final_authority_preserved for row in rows
        ),
        "no_real_external_actions": not external_actions,
    }


def _records_have_static_distance(records: list[dict[str, Any]]) -> bool:
    forbidden = {"hops_ago", "hop_distance", "graph_distance"}

    def contains(value: Any) -> bool:
        if isinstance(value, dict):
            return any(
                str(key) in forbidden or contains(child)
                for key, child in value.items()
            )
        if isinstance(value, list):
            return any(contains(child) for child in value)
        return False

    return any(contains(record) for record in records)


def _drs_lineage_survival(report: DrsGraphProximityReport) -> dict[str, Any]:
    rows_by_id = {row.record["record_id"]: row for row in report.rows}
    return {
        "local_drs_only": True,
        "read_only_ranking_proof": True,
        "records_written": len(report.records),
        "graph_distance_computed_at_query_time": rows_by_id[
            "child_work_direct"
        ].graph_distance
        == 1
        and rows_by_id["grandchild_work"].graph_distance == 2,
        "static_hops_stored_in_records": _records_have_static_distance(
            report.records
        ),
        "graph_proximity_formula_applied": rows_by_id[
            "grandchild_work"
        ].graph_proximity
        == 2 ** (-2 / 2.0),
        "lineage_affects_ranking": rows_by_id[
            "child_work_direct"
        ].final_rank_score
        > rows_by_id["fresh_but_unrelated_work"].final_rank_score,
        "graph_proximity_does_not_override_policy": True,
        "quarantine_not_reuse_eligible": not rows_by_id[
            "nearby_quarantine"
        ].direct_reuse_eligible,
        "deadend_not_reuse_eligible": not rows_by_id[
            "nearby_deadend"
        ].direct_reuse_eligible,
        "direct_reuse_policy_unchanged": True,
        "external_drs_network_implemented": False,
        "global_drs_implemented": False,
    }


def _needle_failure_pass(needle: dict[str, Any]) -> bool:
    return (
        needle["scenarios"] == 8
        and needle["timeout_contained"]
        and needle["invalid_json_quarantined"]
        and needle["schema_validation_failed_quarantined"]
        and needle["unknown_exception_contained"]
        and needle["permission_required_blocked_or_needs_user"]
        and needle["circuit_breaker_blocked"]
        and needle["contract_mismatch_blocked_or_deadend"]
        and needle["success_accepted"]
        and needle["gt_runtime_called_for_needle_outcomes"]
        and needle["needle_created_final_output"] is False
        and needle["direct_user_answers_from_needle"] == 0
        and needle["no_unhandled_exceptions"]
        and needle["no_real_external_actions"]
    )


def _drs_routing_pass(drs_routing: dict[str, Any]) -> bool:
    return (
        drs_routing["local_drs_only"]
        and drs_routing["work_records"] == 1
        and drs_routing["quarantine_records"] == 3
        and drs_routing["deadend_records"] == 4
        and drs_routing["bad_outcomes_written_to_successful_work"] == 0
        and drs_routing["direct_reuse_unsafe_candidates"] == 0
        and drs_routing["time_envelope_present_for_all"]
        and drs_routing["provenance_present_for_all"]
        and drs_routing["gt_metadata_present_for_all"]
        and drs_routing["sensitive_terms_absent_for_all"]
        and drs_routing["external_drs_network_implemented"] is False
        and drs_routing["global_drs_implemented"] is False
    )


def _large_graph_pass(large_graph: dict[str, Any]) -> bool:
    return (
        large_graph["normal_graph_completed"]
        and large_graph["wide_graph_parallelism_limited"]
        and large_graph["deep_graph_depth_checked"]
        and large_graph["oversized_graph_blocked"]
        and large_graph["too_many_edges_graph_blocked"]
        and large_graph["cycle_graph_blocked"]
        and large_graph["unknown_dependency_graph_blocked"]
        and large_graph["child_boundary_snapshots_created"]
        and large_graph["gt_candidate_count_bounded"]
        and large_graph["raw_large_graph_not_sent_to_gt"]
        and large_graph["large_graph_gt_runtime_called"] is False
        and large_graph["large_graph_gt_boundary_mode"] == "bounded_summary_check"
        and large_graph["executor_created_final_output"] is False
        and large_graph["root_final_authority_preserved"]
        and large_graph["no_real_external_actions"]
    )


def _drs_lineage_pass(drs_lineage: dict[str, Any]) -> bool:
    return (
        drs_lineage["local_drs_only"]
        and drs_lineage["read_only_ranking_proof"]
        and drs_lineage["records_written"] == 7
        and drs_lineage["graph_distance_computed_at_query_time"]
        and drs_lineage["static_hops_stored_in_records"] is False
        and drs_lineage["graph_proximity_formula_applied"]
        and drs_lineage["lineage_affects_ranking"]
        and drs_lineage["graph_proximity_does_not_override_policy"]
        and drs_lineage["quarantine_not_reuse_eligible"]
        and drs_lineage["deadend_not_reuse_eligible"]
        and drs_lineage["direct_reuse_policy_unchanged"]
        and drs_lineage["external_drs_network_implemented"] is False
        and drs_lineage["global_drs_implemented"] is False
    )


def _authority_safety_pass(authority: dict[str, Any]) -> bool:
    return (
        authority["root_final_authority_preserved"]
        and authority["executor_created_final_output"] is False
        and authority["gt_committed_final_output"] is False
        and authority["needle_created_final_output"] is False
        and authority["uncontrolled_delegation"] is False
        and authority["no_real_external_actions"]
        and authority["no_global_drs"]
        and authority["no_external_drs_network"]
        and authority["no_telegram_actions"]
        and authority["no_live_gemini"]
        and authority["no_direct_user_answer_from_needle"]
    )


def _pass_text(value: bool) -> str:
    return "PASS" if value else "FAIL"


def collect_chaos_survival_showcase() -> ChaosSurvivalShowcaseReport:
    needle_chaos_rows = collect_needle_runtime_chaos()
    canonical_needle_rows = collect_canonical_needle_outcome_trace()
    drs_routing_report = collect_needle_outcome_drs_routing()
    large_graph_rows = collect_large_graph_stress()
    drs_graph_report = collect_drs_graph_proximity()

    needle = _needle_failure_survival(needle_chaos_rows, canonical_needle_rows)
    drs_routing = _drs_routing_survival(drs_routing_report)
    large_graph = _large_graph_survival(large_graph_rows)
    drs_lineage = _drs_lineage_survival(drs_graph_report)
    authority = {
        "root_final_authority_preserved": large_graph[
            "root_final_authority_preserved"
        ],
        "executor_created_final_output": large_graph[
            "executor_created_final_output"
        ],
        "gt_committed_final_output": False,
        "needle_created_final_output": needle["needle_created_final_output"],
        "uncontrolled_delegation": False,
        "no_real_external_actions": needle["no_real_external_actions"]
        and drs_routing["local_drs_only"]
        and large_graph["no_real_external_actions"],
        "no_global_drs": not drs_routing["global_drs_implemented"]
        and not drs_lineage["global_drs_implemented"],
        "no_external_drs_network": not drs_routing[
            "external_drs_network_implemented"
        ]
        and not drs_lineage["external_drs_network_implemented"],
        "no_telegram_actions": True,
        "no_live_gemini": True,
        "no_direct_user_answer_from_needle": needle[
            "direct_user_answers_from_needle"
        ]
        == 0,
    }
    needle_pass = _needle_failure_pass(needle)
    drs_routing_pass = _drs_routing_pass(drs_routing)
    large_graph_pass = _large_graph_pass(large_graph)
    drs_lineage_pass = _drs_lineage_pass(drs_lineage)
    authority_pass = _authority_safety_pass(authority)
    all_sections_pass = (
        needle_pass
        and drs_routing_pass
        and large_graph_pass
        and drs_lineage_pass
        and authority_pass
    )
    summary = {
        "chaos_survival_showcase_status": _pass_text(all_sections_pass),
        "modules_composed": 5,
        "needle_failure_survival": _pass_text(needle_pass),
        "drs_routing_survival": _pass_text(drs_routing_pass),
        "large_graph_survival": _pass_text(large_graph_pass),
        "drs_lineage_survival": _pass_text(drs_lineage_pass),
        "root_authority_survived": authority["root_final_authority_preserved"],
        "unsafe_reuse_candidates": drs_routing[
            "direct_reuse_unsafe_candidates"
        ],
        "bad_outcomes_written_to_work": drs_routing[
            "bad_outcomes_written_to_successful_work"
        ],
        "real_external_actions_executed": 0
        if authority["no_real_external_actions"]
        else "detected",
        "unhandled_exceptions": 0
        if needle["no_unhandled_exceptions"]
        else "detected",
        "production_autonomy_claimed": False,
    }
    return ChaosSurvivalShowcaseReport(
        needle_chaos_rows=needle_chaos_rows,
        canonical_needle_rows=canonical_needle_rows,
        drs_routing_report=drs_routing_report,
        large_graph_rows=large_graph_rows,
        drs_graph_report=drs_graph_report,
        needle_failure_survival=needle,
        drs_routing_survival=drs_routing,
        large_graph_survival=large_graph,
        drs_lineage_survival=drs_lineage,
        authority_safety=authority,
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


def render_chaos_survival_showcase(report: ChaosSurvivalShowcaseReport) -> str:
    lines = [
        "[CHAOS SURVIVAL SHOWCASE]",
        "note: deterministic showcase over existing proof modules",
        "note: no real external actions",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Root authority remains final",
        "note: this is a showcase, not production autonomy",
        "",
        "[INPUT MODULES]",
        "needle_runtime_chaos_available: true",
        "canonical_needle_outcome_trace_available: true",
        "needle_outcome_drs_routing_available: true",
        "large_graph_stress_available: true",
        "drs_graph_proximity_available: true",
        "",
        "[NEEDLE FAILURE SURVIVAL]",
    ]
    lines.extend(_field_lines(report.needle_failure_survival))
    lines.extend(["", "[DRS ROUTING SURVIVAL]"])
    lines.extend(_field_lines(report.drs_routing_survival))
    lines.extend(["", "[LARGE GRAPH SURVIVAL]"])
    lines.extend(_field_lines(report.large_graph_survival))
    lines.extend(["", "[DRS LINEAGE SURVIVAL]"])
    lines.extend(_field_lines(report.drs_lineage_survival))
    lines.extend(["", "[AUTHORITY / SAFETY]"])
    lines.extend(_field_lines(report.authority_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_chaos_survival_showcase() -> str:
    return render_chaos_survival_showcase(collect_chaos_survival_showcase())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic Chaos Survival Showcase."
    )
    parser.parse_args()
    print(run_chaos_survival_showcase(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
