from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_dag_executor_from_valid_plan_graph import (
    collect_dag_executor_from_valid_plan_graph,
)


SCENARIOS_UNDER_TEST = (
    "completed_result_proposal_validated",
    "degraded_result_proposal_validated_as_degraded",
    "raw_executor_text_blocked",
    "raw_architect_plan_graph_blocked",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "real_action_output_blocked",
    "malformed_result_proposal_rejected",
    "malicious_result_proposal_claiming_final_output_rejected",
    "malicious_result_proposal_claiming_drs_write_rejected",
)


@dataclass(frozen=True)
class PostVvFromResultProposalReport:
    input_result_proposals: dict[str, Any]
    post_vv_input_filter: list[dict[str, Any]]
    validation_reports: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _is_result_proposal(result: dict[str, Any]) -> bool:
    required = {
        "result_proposal_id",
        "created_by",
        "source_plan_graph_proposal_id",
        "source_packet_id",
        "node_results",
        "evidence",
        "risks",
        "result_status",
    }
    return required <= set(result) and result.get("created_by") == "executor"


def _result_has_valid_shape(result: dict[str, Any]) -> bool:
    return (
        _is_result_proposal(result)
        and isinstance(result.get("node_results"), list)
        and bool(result["node_results"])
        and isinstance(result.get("evidence"), list)
        and bool(result["evidence"])
        and isinstance(result.get("risks"), list)
    )


def _validation_status(result: dict[str, Any]) -> str:
    if (
        result.get("executor_creates_final_output")
        or result.get("executor_writes_drs")
        or result.get("executor_executes_real_action")
        or not _result_has_valid_shape(result)
    ):
        return "rejected"
    if result.get("result_status") == "degraded":
        return "degraded"
    return "accepted"


def _validation_report_from_result(
    scenario: str,
    result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema_valid = _result_has_valid_shape(result)
    node_results_checked = isinstance(result.get("node_results"), list)
    evidence_checked = isinstance(result.get("evidence"), list)
    risks_checked = isinstance(result.get("risks"), list)
    final_output_claim = result.get("executor_creates_final_output") is True
    drs_write_claim = result.get("executor_writes_drs") is True
    real_action_claim = result.get("executor_executes_real_action") is True
    status = _validation_status(result)
    findings: list[str] = []
    if schema_valid:
        findings.append("result_proposal_shape_valid")
    else:
        findings.append("result_proposal_shape_invalid")
        findings.append("malformed_result_proposal_rejected")
    if final_output_claim:
        findings.append("final_output_claim_rejected")
    if drs_write_claim:
        findings.append("drs_write_claim_rejected")
    if real_action_claim:
        findings.append("real_action_claim_rejected")
    if status == "degraded":
        findings.append("degraded_result_preserved")
    validation_report = {
        "validation_report_id": f"validation_report_{scenario}",
        "created_by": "post_vv",
        "scenario": scenario,
        "source_result_proposal_id": result["result_proposal_id"],
        "source_plan_graph_proposal_id": result["source_plan_graph_proposal_id"],
        "source_packet_id": result["source_packet_id"],
        "input_is_result_proposal": True,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
        "result_proposal_schema_valid": schema_valid,
        "node_results_checked": node_results_checked,
        "evidence_checked": evidence_checked,
        "risks_checked": risks_checked,
        "safety_flags_checked": True,
        "result_status": result["result_status"],
        "validation_status": status,
        "validation_findings": findings,
        "validation_risks": (
            list(result.get("risks", []))
            if isinstance(result.get("risks"), list)
            else ["invalid_risks_shape"]
        ),
        "downgraded_claims_visible": list(result.get("downgraded_claims_visible", [])),
        "final_output_claim_detected": final_output_claim,
        "drs_write_claim_detected": drs_write_claim,
        "real_action_claim_detected": real_action_claim,
        "post_vv_creates_final_output": False,
        "post_vv_writes_drs": False,
        "post_vv_executes_actions": False,
        "gt_invoked": False,
        "root_final_invoked": False,
    }
    filter_row = {
        "scenario": scenario,
        "input_kind": "result_proposal",
        "post_vv_invoked": True,
        "blocked_before_post_vv": False,
        "block_reasons": [],
        "input_is_result_proposal": True,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }
    return filter_row, validation_report


def _blocked_filter_row(
    scenario: str,
    input_kind: str,
    block_reasons: list[str],
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "post_vv_invoked": False,
        "blocked_before_post_vv": True,
        "block_reasons": block_reasons,
        "input_is_result_proposal": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }


def _malicious_result(base: dict[str, Any], *, claim: str) -> dict[str, Any]:
    result = dict(base)
    result["result_proposal_id"] = f"{base['result_proposal_id']}_{claim}"
    if claim == "final_output":
        result["executor_creates_final_output"] = True
    elif claim == "drs_write":
        result["executor_writes_drs"] = True
    return result


def _malformed_result(base: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    result["result_proposal_id"] = f"{base['result_proposal_id']}_malformed"
    result["node_results"] = "not_a_node_result_list"
    result.pop("evidence", None)
    result["risks"] = "not_a_risk_list"
    return result


def _containment(
    filters: list[dict[str, Any]],
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "raw_executor_text_reached_post_vv": any(
            row["input_kind"] == "raw_executor_text" and row["post_vv_invoked"]
            for row in filters
        ),
        "raw_architect_plan_graph_reached_post_vv": any(
            row["input_kind"] == "raw_architect_plan_graph" and row["post_vv_invoked"]
            for row in filters
        ),
        "raw_orchestrator_matrix_reached_post_vv": any(
            row["input_kind"] == "raw_orchestrator_matrix" and row["post_vv_invoked"]
            for row in filters
        ),
        "raw_user_intent_reached_post_vv": any(
            row["input_kind"] == "raw_user_intent" and row["post_vv_invoked"]
            for row in filters
        ),
        "real_action_output_reached_post_vv": any(
            row["input_kind"] == "real_action_output" and row["post_vv_invoked"]
            for row in filters
        ),
        "malicious_final_output_claim_passed": any(
            report["final_output_claim_detected"]
            and report["validation_status"] != "rejected"
            for report in reports
        ),
        "malicious_drs_write_claim_passed": any(
            report["drs_write_claim_detected"]
            and report["validation_status"] != "rejected"
            for report in reports
        ),
        "invalid_post_vv_created_final_output": any(
            report["post_vv_creates_final_output"] for report in reports
        ),
        "invalid_post_vv_wrote_drs": any(
            report["post_vv_writes_drs"] for report in reports
        ),
        "invalid_post_vv_invoked_gt": any(report["gt_invoked"] for report in reports),
        "invalid_post_vv_invoked_root_final": any(
            report["root_final_invoked"] for report in reports
        ),
    }


def _authority_safety(
    filters: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    invoked_rows = [row for row in filters if row["post_vv_invoked"]]
    return {
        "post_vv_receives_only_result_proposal": bool(invoked_rows)
        and all(row["input_is_result_proposal"] for row in invoked_rows),
        "post_vv_receives_raw_executor_text": containment[
            "raw_executor_text_reached_post_vv"
        ],
        "post_vv_receives_raw_architect_plan_graph": containment[
            "raw_architect_plan_graph_reached_post_vv"
        ],
        "post_vv_receives_raw_orchestrator_matrix": containment[
            "raw_orchestrator_matrix_reached_post_vv"
        ],
        "post_vv_receives_raw_user_intent": containment[
            "raw_user_intent_reached_post_vv"
        ],
        "post_vv_receives_real_action_output": containment[
            "real_action_output_reached_post_vv"
        ],
        "validation_report_only": bool(reports)
        and all(report["created_by"] == "post_vv" for report in reports),
        "post_vv_creates_final_output": any(
            report["post_vv_creates_final_output"] for report in reports
        ),
        "post_vv_writes_drs": any(report["post_vv_writes_drs"] for report in reports),
        "post_vv_executes_actions": any(
            report["post_vv_executes_actions"] for report in reports
        ),
        "gt_invoked": any(report["gt_invoked"] for report in reports),
        "root_final_invoked": any(report["root_final_invoked"] for report in reports),
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _blocked(filters: list[dict[str, Any]], scenario: str) -> bool:
    return any(
        row["scenario"] == scenario and row["blocked_before_post_vv"]
        for row in filters
    )


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    accepted_reports = [
        report for report in reports if report["validation_status"] == "accepted"
    ]
    degraded_reports = [
        report for report in reports if report["validation_status"] == "degraded"
    ]
    rejected_reports = [
        report for report in reports if report["validation_status"] == "rejected"
    ]
    malicious_final_rejected = any(
        report["final_output_claim_detected"]
        and report["validation_status"] == "rejected"
        for report in reports
    )
    malicious_drs_rejected = any(
        report["drs_write_claim_detected"]
        and report["validation_status"] == "rejected"
        for report in reports
    )
    malformed_rejected = any(
        report["scenario"] == "malformed_result_proposal_rejected"
        and not report["result_proposal_schema_valid"]
        and report["validation_status"] == "rejected"
        for report in reports
    )
    boundary_pass = (
        authority["post_vv_receives_only_result_proposal"]
        and not authority["post_vv_receives_raw_executor_text"]
        and not authority["post_vv_receives_raw_architect_plan_graph"]
        and not authority["post_vv_receives_raw_orchestrator_matrix"]
        and not authority["post_vv_receives_raw_user_intent"]
        and not authority["post_vv_receives_real_action_output"]
        and authority["validation_report_only"]
        and not authority["post_vv_creates_final_output"]
        and not authority["post_vv_writes_drs"]
        and not authority["post_vv_executes_actions"]
        and not authority["gt_invoked"]
        and not authority["root_final_invoked"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and not containment["malicious_final_output_claim_passed"]
        and not containment["malicious_drs_write_claim_passed"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and len(reports) == 5
        and len(accepted_reports) == 1
        and len(degraded_reports) == 1
        and len(rejected_reports) == 3
        and _blocked(filters, "raw_executor_text_blocked")
        and _blocked(filters, "raw_architect_plan_graph_blocked")
        and _blocked(filters, "raw_orchestrator_matrix_blocked")
        and _blocked(filters, "raw_user_intent_blocked")
        and _blocked(filters, "real_action_output_blocked")
        and malformed_rejected
        and malicious_final_rejected
        and malicious_drs_rejected
        and boundary_pass
        else "FAIL"
    )
    return {
        "post_vv_from_result_proposal_status": status,
        "source_dag_executor_status": source_status,
        "scenarios_verified": len(filters),
        "validation_reports_created": len(reports),
        "accepted_validation_reports": len(accepted_reports),
        "degraded_validation_reports": len(degraded_reports),
        "rejected_validation_reports": len(rejected_reports),
        "raw_executor_text_blocked": _blocked(filters, "raw_executor_text_blocked"),
        "raw_architect_plan_graph_blocked": _blocked(
            filters, "raw_architect_plan_graph_blocked"
        ),
        "raw_orchestrator_matrix_blocked": _blocked(
            filters, "raw_orchestrator_matrix_blocked"
        ),
        "raw_user_intent_blocked": _blocked(filters, "raw_user_intent_blocked"),
        "real_action_output_blocked": _blocked(filters, "real_action_output_blocked"),
        "malformed_result_proposal_rejected": malformed_rejected,
        "malicious_final_output_claim_rejected": malicious_final_rejected,
        "malicious_drs_write_claim_rejected": malicious_drs_rejected,
        "post_vv_receives_only_result_proposal": authority[
            "post_vv_receives_only_result_proposal"
        ],
        "ready_for_gt_from_validation_report": status == "PASS",
        "production_final_output_created": authority["production_final_output_created"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_post_vv_from_result_proposal() -> PostVvFromResultProposalReport:
    dag_report = collect_dag_executor_from_valid_plan_graph()
    source_status = dag_report.summary["dag_executor_from_valid_plan_graph_status"]
    results_by_scenario = {
        result["scenario"]: result for result in dag_report.result_proposals
    }
    imported_results = list(dag_report.result_proposals)

    filters: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []

    row, report = _validation_report_from_result(
        "completed_result_proposal_validated",
        results_by_scenario["accepted_plan_graph_executor_result_proposal"],
    )
    filters.append(row)
    reports.append(report)

    row, report = _validation_report_from_result(
        "degraded_result_proposal_validated_as_degraded",
        results_by_scenario["downgraded_plan_graph_executor_limited_result_proposal"],
    )
    filters.append(row)
    reports.append(report)

    filters.append(
        _blocked_filter_row(
            "raw_executor_text_blocked",
            "raw_executor_text",
            ["raw_executor_text_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_architect_plan_graph_blocked",
            "raw_architect_plan_graph",
            ["raw_architect_plan_graph_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_orchestrator_matrix_blocked",
            "raw_orchestrator_matrix",
            ["raw_orchestrator_matrix_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_user_intent_blocked",
            "raw_user_intent",
            ["raw_user_intent_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "real_action_output_blocked",
            "real_action_output",
            ["real_action_output_not_allowed"],
        )
    )

    malformed = _malformed_result(imported_results[0])
    row, report = _validation_report_from_result(
        "malformed_result_proposal_rejected",
        malformed,
    )
    filters.append(row)
    reports.append(report)

    malicious_final = _malicious_result(imported_results[0], claim="final_output")
    row, report = _validation_report_from_result(
        "malicious_result_proposal_claiming_final_output_rejected",
        malicious_final,
    )
    filters.append(row)
    reports.append(report)

    malicious_drs = _malicious_result(imported_results[0], claim="drs_write")
    row, report = _validation_report_from_result(
        "malicious_result_proposal_claiming_drs_write_rejected",
        malicious_drs,
    )
    filters.append(row)
    reports.append(report)

    input_result_proposals = {
        "source_dag_executor_report_status": source_status,
        "result_proposals_imported": [
            result["result_proposal_id"] for result in imported_results
        ],
        "accepted_plan_result_proposals": dag_report.summary[
            "accepted_plan_result_proposals"
        ],
        "downgraded_plan_result_proposals": dag_report.summary[
            "downgraded_plan_result_proposals"
        ],
    }
    containment = _containment(filters, reports)
    authority = _authority_safety(filters, reports, containment)
    summary = _summary(source_status, filters, reports, containment, authority)
    return PostVvFromResultProposalReport(
        input_result_proposals=input_result_proposals,
        post_vv_input_filter=filters,
        validation_reports=reports,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_post_vv_from_result_proposal(
    report: PostVvFromResultProposalReport,
) -> str:
    lines = [
        "[POST V&V FROM RESULT PROPOSAL]",
        "note: deterministic Post V&V proof from ResultProposal",
        "note: Post V&V receives ResultProposal artifacts only",
        "note: raw Executor text is blocked",
        "note: raw Architect PlanGraph is blocked",
        "note: raw Orchestrator matrix is blocked",
        "note: raw user intent is blocked",
        "note: real action output is blocked",
        "note: Post V&V creates ValidationReport / V&VReport only",
        "note: Post V&V does not create FinalOutput",
        "note: Post V&V does not write DRS directly",
        "note: Post V&V does not execute actions",
        "note: GT is not invoked yet",
        "note: Root Final is not invoked yet",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT RESULT PROPOSALS]", report.input_result_proposals)

    lines.extend(["", "[POST V&V INPUT FILTER]"])
    filter_fields = (
        "scenario",
        "input_kind",
        "post_vv_invoked",
        "blocked_before_post_vv",
        "block_reasons",
        "input_is_result_proposal",
        "raw_executor_text_received",
        "raw_architect_plan_graph_received",
        "raw_orchestrator_matrix_received",
        "raw_user_intent_received",
        "real_action_output_received",
    )
    for row in report.post_vv_input_filter:
        lines.append(
            " | ".join(f"{field}={_format_value(row[field])}" for field in filter_fields)
        )

    lines.extend(["", "[VALIDATION REPORTS]"])
    report_fields = (
        "validation_report_id",
        "created_by",
        "source_result_proposal_id",
        "source_plan_graph_proposal_id",
        "source_packet_id",
        "result_proposal_schema_valid",
        "node_results_checked",
        "evidence_checked",
        "risks_checked",
        "safety_flags_checked",
        "result_status",
        "validation_status",
        "validation_findings",
        "validation_risks",
        "final_output_claim_detected",
        "drs_write_claim_detected",
        "real_action_claim_detected",
        "post_vv_creates_final_output",
        "post_vv_writes_drs",
        "post_vv_executes_actions",
        "gt_invoked",
        "root_final_invoked",
    )
    for validation_report in report.validation_reports:
        lines.append(
            " | ".join(
                f"{field}={_format_value(validation_report[field])}"
                for field in report_fields
            )
        )

    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_post_vv_from_result_proposal() -> str:
    return render_post_vv_from_result_proposal(
        collect_post_vv_from_result_proposal()
    )


def main() -> int:
    print(run_post_vv_from_result_proposal(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
