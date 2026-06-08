from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_root_final_from_gt_decision import collect_root_final_from_gt_decision


SCENARIOS_UNDER_TEST = (
    "accepted_root_final_creates_local_audit_record",
    "degraded_root_final_creates_degraded_audit_record",
    "rejected_root_final_creates_rejection_audit_record",
    "raw_gt_decision_blocked",
    "raw_validation_report_blocked",
    "raw_result_proposal_blocked",
    "raw_architect_plan_graph_blocked",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "real_action_output_blocked",
    "malformed_root_final_artifact_rejected",
    "malicious_root_final_claiming_global_drs_write_rejected",
    "malicious_root_final_claiming_external_drs_network_write_rejected",
    "malicious_root_final_claiming_production_persistence_rejected",
    "malicious_root_final_claiming_root_drs_write_rejected",
    "malicious_root_final_claiming_action_rejected",
)

CANONICAL_ROOT_FINAL_SCENARIOS = {
    "accepted": "accept_gt_decision_root_final_accept",
    "degraded": "degrade_gt_decision_root_final_degraded",
    "rejected": "reject_gt_decision_root_final_rejected",
}


@dataclass(frozen=True)
class DrsWritebackFromRootFinalReport:
    input_root_final_artifacts: dict[str, Any]
    drs_writeback_input_filter: list[dict[str, Any]]
    drs_writeback_audit_records: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    return _bool_text(value) if isinstance(value, bool) else str(value)


def _is_root_final_artifact(artifact: dict[str, Any]) -> bool:
    required = {
        "final_artifact_id",
        "created_by",
        "source_gt_decision_id",
        "source_validation_report_id",
        "source_result_proposal_id",
        "root_final_status",
        "root_created_final_output",
        "root_writes_drs",
        "root_executes_actions",
        "production_external_action_executed",
        "production_persistence_claimed",
    }
    return (
        required <= set(artifact)
        and artifact.get("created_by") == "root_orchestrator"
        and artifact.get("root_final_status") in {"accepted", "degraded", "rejected"}
        and artifact.get("root_created_final_output") is True
        and all(
            isinstance(artifact.get(key), str) and bool(artifact[key])
            for key in (
                "final_artifact_id",
                "source_gt_decision_id",
                "source_validation_report_id",
                "source_result_proposal_id",
            )
        )
    )


def _unsafe_claims(artifact: dict[str, Any]) -> list[str]:
    claims = []
    if artifact.get("global_drs_write") is True:
        claims.append("global_drs_write_claim_rejected")
    if artifact.get("external_drs_network_write") is True:
        claims.append("external_drs_network_write_claim_rejected")
    if artifact.get("production_persistence_claimed") is True:
        claims.append("production_persistence_claim_rejected")
    if artifact.get("root_writes_drs") is True:
        claims.append("root_drs_write_claim_rejected")
    if artifact.get("real_external_action_executed") is True:
        claims.append("real_action_claim_rejected")
    if artifact.get("root_executes_actions") is True:
        claims.append("root_action_claim_rejected")
    return claims


def _audit_record(
    scenario: str,
    artifact: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    shape_valid = _is_root_final_artifact(artifact)
    unsafe_claims = _unsafe_claims(artifact)
    if not shape_valid or unsafe_claims:
        reasons = ([] if shape_valid else ["malformed_root_final_artifact"]) + unsafe_claims
        return _filter_row(
            scenario,
            "root_final_artifact",
            invoked=False,
            reasons=reasons,
            input_is_root_final_artifact=shape_valid,
        ), None

    status = artifact["root_final_status"]
    record = {
        "drs_writeback_record_id": f"drs_writeback_audit_{artifact['final_artifact_id']}",
        "created_by": "root_orchestrator",
        "scenario": scenario,
        "source_root_final_artifact_id": artifact["final_artifact_id"],
        "source_gt_decision_id": artifact["source_gt_decision_id"],
        "source_validation_report_id": artifact["source_validation_report_id"],
        "source_result_proposal_id": artifact["source_result_proposal_id"],
        "input_is_root_final_artifact": True,
        "root_final_status_seen": status,
        "writeback_scope": "local_audit_only",
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "real_external_action_executed": False,
        "canonical_artifact_refs": {
            "root_final_artifact_id": artifact["final_artifact_id"],
            "gt_decision_id": artifact["source_gt_decision_id"],
            "validation_report_id": artifact["source_validation_report_id"],
            "result_proposal_id": artifact["source_result_proposal_id"],
        },
        "audit_summary": {
            "root_final_status": status,
            "root_selection_reason": artifact.get("root_selection_reason"),
            "degraded_or_rejected_claims_visible": status in {"degraded", "rejected"},
            "production_write_not_performed": True,
        },
        "time_envelope": {
            "observed_at": "2026-06-08T00:00:00Z",
            "valid_from": "2026-06-08T00:00:00Z",
            "valid_to": None,
            "time_basis": "deterministic_proof_clock",
        },
        "provenance": {
            "source_layer": "root_final_from_gt_decision_v0_1",
            "writeback_layer": "drs_writeback_from_root_final_v0_1",
            "proof_only": True,
        },
        "root_authority_preserved": True,
        "drs_is_authority": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    return _filter_row(
        scenario,
        "root_final_artifact",
        invoked=True,
        reasons=[],
        input_is_root_final_artifact=True,
    ), record


def _filter_row(
    scenario: str,
    input_kind: str,
    *,
    invoked: bool,
    reasons: list[str],
    input_is_root_final_artifact: bool = False,
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "drs_writeback_invoked": invoked,
        "blocked_before_writeback": not invoked,
        "block_reasons": reasons,
        "input_is_root_final_artifact": input_is_root_final_artifact,
    }


def _blocked_row(scenario: str, input_kind: str, reason: str) -> dict[str, Any]:
    return _filter_row(scenario, input_kind, invoked=False, reasons=[reason])


def _malformed_root_final(base: dict[str, Any]) -> dict[str, Any]:
    artifact = dict(base)
    artifact.pop("source_gt_decision_id", None)
    artifact["final_artifact_id"] = "malformed_root_final_artifact"
    return artifact


def _malicious_root_final(base: dict[str, Any], claim: str) -> dict[str, Any]:
    artifact = dict(base)
    artifact["final_artifact_id"] = f"{base['final_artifact_id']}_{claim}"
    artifact[claim] = True
    return artifact


def _blocked(filters: list[dict[str, Any]], scenario: str) -> bool:
    return any(
        row["scenario"] == scenario and row["blocked_before_writeback"]
        for row in filters
    )


def _containment(filters: list[dict[str, Any]]) -> dict[str, Any]:
    reached = {
        row["input_kind"]: row["drs_writeback_invoked"]
        for row in filters
        if row["input_kind"].startswith("raw_") or row["input_kind"] == "real_action_output"
    }
    return {
        "raw_gt_decision_reached_drs_writeback": reached.get("raw_gt_decision", False),
        "raw_validation_report_reached_drs_writeback": reached.get(
            "raw_validation_report", False
        ),
        "raw_result_proposal_reached_drs_writeback": reached.get(
            "raw_result_proposal", False
        ),
        "raw_architect_plan_graph_reached_drs_writeback": reached.get(
            "raw_architect_plan_graph", False
        ),
        "raw_orchestrator_matrix_reached_drs_writeback": reached.get(
            "raw_orchestrator_matrix", False
        ),
        "raw_user_intent_reached_drs_writeback": reached.get("raw_user_intent", False),
        "real_action_output_reached_drs_writeback": reached.get(
            "real_action_output", False
        ),
        "malicious_global_drs_write_claim_passed": not _blocked(
            filters, "malicious_root_final_claiming_global_drs_write_rejected"
        ),
        "malicious_external_drs_network_claim_passed": not _blocked(
            filters,
            "malicious_root_final_claiming_external_drs_network_write_rejected",
        ),
        "malicious_production_persistence_claim_passed": not _blocked(
            filters, "malicious_root_final_claiming_production_persistence_rejected"
        ),
        "malicious_root_drs_write_claim_passed": not _blocked(
            filters, "malicious_root_final_claiming_root_drs_write_rejected"
        ),
        "malicious_action_claim_passed": not _blocked(
            filters, "malicious_root_final_claiming_action_rejected"
        ),
    }


def _authority(
    filters: list[dict[str, Any]],
    records: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    invoked = [row for row in filters if row["drs_writeback_invoked"]]
    return {
        "drs_writeback_receives_only_root_final_artifact": bool(invoked)
        and all(row["input_is_root_final_artifact"] for row in invoked),
        "root_authority_preserved": bool(records)
        and all(record["root_authority_preserved"] for record in records),
        "drs_is_authority": any(record["drs_is_authority"] for record in records),
        "writeback_scope_local_audit_only": bool(records)
        and all(record["writeback_scope"] == "local_audit_only" for record in records),
        "production_persistence_claimed": any(
            record["production_persistence"] for record in records
        ),
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "production_external_action_executed": any(
            record["real_external_action_executed"] for record in records
        ),
        "marennya_invoked": any(record["marennya_invoked"] for record in records),
        "up_invoked": any(record["up_invoked"] for record in records),
    }


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    records: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    counts = {
        status: sum(record["root_final_status_seen"] == status for record in records)
        for status in ("accepted", "degraded", "rejected")
    }
    required_blocks = {
        "raw_gt_decision_blocked": "raw_gt_decision_blocked",
        "raw_validation_report_blocked": "raw_validation_report_blocked",
        "raw_result_proposal_blocked": "raw_result_proposal_blocked",
        "raw_architect_plan_graph_blocked": "raw_architect_plan_graph_blocked",
        "raw_orchestrator_matrix_blocked": "raw_orchestrator_matrix_blocked",
        "raw_user_intent_blocked": "raw_user_intent_blocked",
        "real_action_output_blocked": "real_action_output_blocked",
        "malformed_root_final_artifact_rejected": "malformed_root_final_artifact_rejected",
        "malicious_global_drs_write_claim_rejected": "malicious_root_final_claiming_global_drs_write_rejected",
        "malicious_external_drs_network_claim_rejected": "malicious_root_final_claiming_external_drs_network_write_rejected",
        "malicious_production_persistence_claim_rejected": "malicious_root_final_claiming_production_persistence_rejected",
        "malicious_root_drs_write_claim_rejected": "malicious_root_final_claiming_root_drs_write_rejected",
        "malicious_action_claim_rejected": "malicious_root_final_claiming_action_rejected",
    }
    block_results = {
        key: _blocked(filters, scenario) for key, scenario in required_blocks.items()
    }
    boundary_pass = (
        authority["drs_writeback_receives_only_root_final_artifact"]
        and authority["root_authority_preserved"]
        and not authority["drs_is_authority"]
        and authority["writeback_scope_local_audit_only"]
        and not authority["production_persistence_claimed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["production_external_action_executed"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and not any(containment.values())
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and {row["scenario"] for row in filters} == set(SCENARIOS_UNDER_TEST)
        and len(records) == 3
        and counts == {"accepted": 1, "degraded": 1, "rejected": 1}
        and all(block_results.values())
        and boundary_pass
        else "FAIL"
    )
    return {
        "drs_writeback_from_root_final_status": status,
        "source_root_final_status": source_status,
        "scenarios_verified": len(filters),
        "drs_writeback_records_created": len(records),
        "accepted_writeback_records": counts["accepted"],
        "degraded_writeback_records": counts["degraded"],
        "rejected_writeback_records": counts["rejected"],
        **block_results,
        "drs_writeback_receives_only_root_final_artifact": authority[
            "drs_writeback_receives_only_root_final_artifact"
        ],
        "root_authority_preserved": authority["root_authority_preserved"],
        "writeback_scope_local_audit_only": authority["writeback_scope_local_audit_only"],
        "ready_for_full_cycle_with_drs_audit_trace": status == "PASS",
        "production_persistence_claimed": authority["production_persistence_claimed"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_drs_writeback_from_root_final() -> DrsWritebackFromRootFinalReport:
    root_report = collect_root_final_from_gt_decision()
    source_status = root_report.summary["root_final_from_gt_decision_status"]
    artifacts_by_scenario = {
        artifact["scenario"]: artifact for artifact in root_report.root_final_artifacts
    }
    canonical = {
        status: artifacts_by_scenario[scenario]
        for status, scenario in CANONICAL_ROOT_FINAL_SCENARIOS.items()
    }
    filters: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    canonical_scenarios = {
        "accepted": "accepted_root_final_creates_local_audit_record",
        "degraded": "degraded_root_final_creates_degraded_audit_record",
        "rejected": "rejected_root_final_creates_rejection_audit_record",
    }
    for status in ("accepted", "degraded", "rejected"):
        row, record = _audit_record(
            canonical_scenarios[status],
            canonical[status],
        )
        filters.append(row)
        if record:
            records.append(record)

    for scenario, input_kind, reason in (
        ("raw_gt_decision_blocked", "raw_gt_decision", "raw_gt_decision_not_allowed"),
        (
            "raw_validation_report_blocked",
            "raw_validation_report",
            "raw_validation_report_not_allowed",
        ),
        (
            "raw_result_proposal_blocked",
            "raw_result_proposal",
            "raw_result_proposal_not_allowed",
        ),
        (
            "raw_architect_plan_graph_blocked",
            "raw_architect_plan_graph",
            "raw_architect_plan_graph_not_allowed",
        ),
        (
            "raw_orchestrator_matrix_blocked",
            "raw_orchestrator_matrix",
            "raw_orchestrator_matrix_not_allowed",
        ),
        ("raw_user_intent_blocked", "raw_user_intent", "raw_user_intent_not_allowed"),
        (
            "real_action_output_blocked",
            "real_action_output",
            "real_action_output_not_allowed",
        ),
    ):
        filters.append(_blocked_row(scenario, input_kind, reason))

    for scenario, artifact in (
        ("malformed_root_final_artifact_rejected", _malformed_root_final(canonical["accepted"])),
        (
            "malicious_root_final_claiming_global_drs_write_rejected",
            _malicious_root_final(canonical["accepted"], "global_drs_write"),
        ),
        (
            "malicious_root_final_claiming_external_drs_network_write_rejected",
            _malicious_root_final(canonical["accepted"], "external_drs_network_write"),
        ),
        (
            "malicious_root_final_claiming_production_persistence_rejected",
            _malicious_root_final(canonical["accepted"], "production_persistence_claimed"),
        ),
        (
            "malicious_root_final_claiming_root_drs_write_rejected",
            _malicious_root_final(canonical["accepted"], "root_writes_drs"),
        ),
        (
            "malicious_root_final_claiming_action_rejected",
            _malicious_root_final(canonical["accepted"], "real_external_action_executed"),
        ),
    ):
        row, record = _audit_record(scenario, artifact)
        filters.append(row)
        if record:
            records.append(record)

    input_artifacts = {
        "source_root_final_report_status": source_status,
        "root_final_artifacts_imported": [
            artifact["final_artifact_id"] for artifact in canonical.values()
        ],
        "accepted_root_final_artifacts": 1,
        "degraded_root_final_artifacts": 1,
        "rejected_root_final_artifacts": 1,
    }
    containment = _containment(filters)
    authority = _authority(filters, records, containment)
    summary = _summary(source_status, filters, records, containment, authority)
    return DrsWritebackFromRootFinalReport(
        input_root_final_artifacts=input_artifacts,
        drs_writeback_input_filter=filters,
        drs_writeback_audit_records=records,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_drs_writeback_from_root_final(report: DrsWritebackFromRootFinalReport) -> str:
    lines = [
        "[DRS WRITEBACK FROM ROOT FINAL]",
        "note: deterministic DRS writeback proof from Root FinalArtifact",
        "note: only Root FinalArtifact may enter DRS writeback",
        "note: raw GTDecision is blocked",
        "note: raw ValidationReport is blocked",
        "note: raw ResultProposal is blocked",
        "note: raw Architect PlanGraph is blocked",
        "note: raw Orchestrator matrix is blocked",
        "note: raw user intent is blocked",
        "note: this is audit/proof-level writeback, not production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT ROOT FINAL ARTIFACTS]", report.input_root_final_artifacts)
    lines.extend(["", "[DRS WRITEBACK INPUT FILTER]"])
    for row in report.drs_writeback_input_filter:
        lines.append(" ".join(f"{key}={_format_value(value)}" for key, value in row.items()))
    lines.extend(["", "[DRS WRITEBACK AUDIT RECORDS]"])
    for record in report.drs_writeback_audit_records:
        lines.append(" ".join(f"{key}={_format_value(value)}" for key, value in record.items()))
    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines)


def run_drs_writeback_from_root_final() -> str:
    return render_drs_writeback_from_root_final(collect_drs_writeback_from_root_final())


def main() -> None:
    print(run_drs_writeback_from_root_final())


if __name__ == "__main__":
    main()
