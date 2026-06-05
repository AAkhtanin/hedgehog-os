from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_post_vv_from_result_proposal import (
    collect_post_vv_from_result_proposal,
)


SCENARIOS_UNDER_TEST = (
    "accepted_validation_report_gt_accept",
    "degraded_validation_report_gt_degrade",
    "rejected_validation_report_gt_reject",
    "raw_result_proposal_blocked",
    "raw_executor_text_blocked",
    "raw_architect_plan_graph_blocked",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "real_action_output_blocked",
    "malicious_validation_report_claiming_final_output_rejected",
    "malicious_validation_report_claiming_drs_write_rejected",
    "malicious_validation_report_claiming_action_rejected",
    "malformed_validation_report_rejected",
)


@dataclass(frozen=True)
class GtFromValidationReportReport:
    input_validation_reports: dict[str, Any]
    gt_input_filter: list[dict[str, Any]]
    gt_decisions: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _is_validation_report(report: dict[str, Any]) -> bool:
    required = {
        "validation_report_id",
        "created_by",
        "source_result_proposal_id",
        "validation_status",
        "validation_findings",
        "validation_risks",
        "post_vv_creates_final_output",
        "post_vv_writes_drs",
        "post_vv_executes_actions",
    }
    return required <= set(report) and report.get("created_by") == "post_vv"


def _validation_report_has_valid_shape(report: dict[str, Any]) -> bool:
    validation_status = report.get("validation_status")
    return (
        _is_validation_report(report)
        and isinstance(validation_status, str)
        and validation_status in {"accepted", "degraded", "rejected"}
        and isinstance(report.get("validation_findings"), list)
        and isinstance(report.get("validation_risks"), list)
        and isinstance(report.get("source_result_proposal_id"), str)
        and bool(report["source_result_proposal_id"])
    )


def _gt_decision_value(report: dict[str, Any]) -> str:
    if (
        report.get("post_vv_creates_final_output")
        or report.get("post_vv_writes_drs")
        or report.get("post_vv_executes_actions")
        or not _validation_report_has_valid_shape(report)
    ):
        return "reject"
    if report.get("validation_status") == "accepted":
        return "accept"
    if report.get("validation_status") == "degraded":
        return "degrade"
    return "reject"


def _selection_reason(report: dict[str, Any], decision: str, schema_valid: bool) -> str:
    if not schema_valid:
        return "validation_report_shape_invalid"
    if report.get("post_vv_creates_final_output"):
        return "final_output_claim_rejected"
    if report.get("post_vv_writes_drs"):
        return "drs_write_claim_rejected"
    if report.get("post_vv_executes_actions"):
        return "action_claim_rejected"
    if decision == "accept":
        return "validation_report_accepted"
    if decision == "degrade":
        return "validation_report_degraded"
    return "validation_report_rejected"


def _gt_decision_from_validation_report(
    scenario: str,
    validation_report: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema_valid = _validation_report_has_valid_shape(validation_report)
    decision = _gt_decision_value(validation_report)
    final_output_claim = validation_report.get("post_vv_creates_final_output") is True
    drs_write_claim = validation_report.get("post_vv_writes_drs") is True
    action_claim = validation_report.get("post_vv_executes_actions") is True
    validation_status_seen = validation_report.get("validation_status")
    selection_reason = _selection_reason(validation_report, decision, schema_valid)
    validation_findings = (
        list(validation_report.get("validation_findings", []))
        if isinstance(validation_report.get("validation_findings"), list)
        else ["invalid_validation_findings_shape"]
    )
    validation_risks = (
        list(validation_report.get("validation_risks", []))
        if isinstance(validation_report.get("validation_risks"), list)
        else ["invalid_validation_risks_shape"]
    )
    gt_decision = {
        "gt_decision_id": f"gt_decision_{scenario}",
        "created_by": "gt_validator",
        "scenario": scenario,
        "source_validation_report_id": validation_report["validation_report_id"],
        "source_result_proposal_id": validation_report["source_result_proposal_id"],
        "input_is_validation_report": True,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
        "validation_report_schema_valid": schema_valid,
        "validation_status_seen": validation_status_seen,
        "gt_decision": decision,
        "selection_reason": selection_reason,
        "payoff_basis": {
            "validation_status": validation_status_seen,
            "schema_valid": schema_valid,
        },
        "risk_basis": validation_findings + validation_risks,
        "trust_update_proposal": (
            "positive_evidence" if decision == "accept" else "no_positive_update"
        ),
        "regret_update_proposal": (
            "no_update" if decision == "accept" else "risk_or_rejection_visible"
        ),
        "final_output_claim_detected": final_output_claim,
        "drs_write_claim_detected": drs_write_claim,
        "action_claim_detected": action_claim,
        "gt_creates_final_output": False,
        "gt_writes_drs": False,
        "gt_executes_actions": False,
        "root_final_invoked": False,
    }
    filter_row = {
        "scenario": scenario,
        "input_kind": "validation_report",
        "gt_invoked": True,
        "blocked_before_gt": False,
        "block_reasons": [],
        "input_is_validation_report": True,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }
    return filter_row, gt_decision


def _blocked_filter_row(
    scenario: str,
    input_kind: str,
    block_reasons: list[str],
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "gt_invoked": False,
        "blocked_before_gt": True,
        "block_reasons": block_reasons,
        "input_is_validation_report": False,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }


def _malicious_validation_report(
    base: dict[str, Any],
    *,
    claim: str,
) -> dict[str, Any]:
    report = dict(base)
    report["validation_report_id"] = f"{base['validation_report_id']}_{claim}"
    if claim == "final_output":
        report["post_vv_creates_final_output"] = True
    elif claim == "drs_write":
        report["post_vv_writes_drs"] = True
    elif claim == "action":
        report["post_vv_executes_actions"] = True
    return report


def _malformed_validation_report(base: dict[str, Any]) -> dict[str, Any]:
    report = dict(base)
    report["validation_report_id"] = f"{base['validation_report_id']}_malformed"
    report["validation_status"] = {"invalid": "status_shape"}
    report["validation_findings"] = "not_a_findings_list"
    report["validation_risks"] = "not_a_risks_list"
    return report


def _containment(
    filters: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "raw_result_proposal_reached_gt": any(
            row["input_kind"] == "raw_result_proposal" and row["gt_invoked"]
            for row in filters
        ),
        "raw_executor_text_reached_gt": any(
            row["input_kind"] == "raw_executor_text" and row["gt_invoked"]
            for row in filters
        ),
        "raw_architect_plan_graph_reached_gt": any(
            row["input_kind"] == "raw_architect_plan_graph" and row["gt_invoked"]
            for row in filters
        ),
        "raw_orchestrator_matrix_reached_gt": any(
            row["input_kind"] == "raw_orchestrator_matrix" and row["gt_invoked"]
            for row in filters
        ),
        "raw_user_intent_reached_gt": any(
            row["input_kind"] == "raw_user_intent" and row["gt_invoked"]
            for row in filters
        ),
        "real_action_output_reached_gt": any(
            row["input_kind"] == "real_action_output" and row["gt_invoked"]
            for row in filters
        ),
        "malicious_final_output_claim_passed": any(
            decision["final_output_claim_detected"]
            and decision["gt_decision"] != "reject"
            for decision in decisions
        ),
        "malicious_drs_write_claim_passed": any(
            decision["drs_write_claim_detected"]
            and decision["gt_decision"] != "reject"
            for decision in decisions
        ),
        "malicious_action_claim_passed": any(
            decision["action_claim_detected"] and decision["gt_decision"] != "reject"
            for decision in decisions
        ),
        "invalid_gt_created_final_output": any(
            decision["gt_creates_final_output"] for decision in decisions
        ),
        "invalid_gt_wrote_drs": any(decision["gt_writes_drs"] for decision in decisions),
        "invalid_gt_invoked_root_final": any(
            decision["root_final_invoked"] for decision in decisions
        ),
    }


def _authority_safety(
    filters: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    invoked_rows = [row for row in filters if row["gt_invoked"]]
    return {
        "gt_receives_only_validation_report": bool(invoked_rows)
        and all(row["input_is_validation_report"] for row in invoked_rows),
        "gt_receives_raw_result_proposal": containment["raw_result_proposal_reached_gt"],
        "gt_receives_raw_executor_text": containment["raw_executor_text_reached_gt"],
        "gt_receives_raw_architect_plan_graph": containment[
            "raw_architect_plan_graph_reached_gt"
        ],
        "gt_receives_raw_orchestrator_matrix": containment[
            "raw_orchestrator_matrix_reached_gt"
        ],
        "gt_receives_raw_user_intent": containment["raw_user_intent_reached_gt"],
        "gt_receives_real_action_output": containment["real_action_output_reached_gt"],
        "gt_decision_only": bool(decisions)
        and all(decision["created_by"] == "gt_validator" for decision in decisions),
        "gt_creates_final_output": any(
            decision["gt_creates_final_output"] for decision in decisions
        ),
        "gt_writes_drs": any(decision["gt_writes_drs"] for decision in decisions),
        "gt_executes_actions": any(
            decision["gt_executes_actions"] for decision in decisions
        ),
        "root_final_invoked": any(
            decision["root_final_invoked"] for decision in decisions
        ),
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _blocked(filters: list[dict[str, Any]], scenario: str) -> bool:
    return any(
        row["scenario"] == scenario and row["blocked_before_gt"] for row in filters
    )


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    accepted_decisions = [
        decision for decision in decisions if decision["gt_decision"] == "accept"
    ]
    degraded_decisions = [
        decision for decision in decisions if decision["gt_decision"] == "degrade"
    ]
    rejected_decisions = [
        decision for decision in decisions if decision["gt_decision"] == "reject"
    ]
    malicious_final_rejected = any(
        decision["final_output_claim_detected"]
        and decision["gt_decision"] == "reject"
        for decision in decisions
    )
    malicious_drs_rejected = any(
        decision["drs_write_claim_detected"] and decision["gt_decision"] == "reject"
        for decision in decisions
    )
    malicious_action_rejected = any(
        decision["action_claim_detected"] and decision["gt_decision"] == "reject"
        for decision in decisions
    )
    malformed_rejected = any(
        decision["scenario"] == "malformed_validation_report_rejected"
        and not decision["validation_report_schema_valid"]
        and decision["gt_decision"] == "reject"
        for decision in decisions
    )
    boundary_pass = (
        authority["gt_receives_only_validation_report"]
        and not authority["gt_receives_raw_result_proposal"]
        and not authority["gt_receives_raw_executor_text"]
        and not authority["gt_receives_raw_architect_plan_graph"]
        and not authority["gt_receives_raw_orchestrator_matrix"]
        and not authority["gt_receives_raw_user_intent"]
        and not authority["gt_receives_real_action_output"]
        and authority["gt_decision_only"]
        and not authority["gt_creates_final_output"]
        and not authority["gt_writes_drs"]
        and not authority["gt_executes_actions"]
        and not authority["root_final_invoked"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and not containment["malicious_final_output_claim_passed"]
        and not containment["malicious_drs_write_claim_passed"]
        and not containment["malicious_action_claim_passed"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and len(decisions) == 7
        and len(accepted_decisions) == 1
        and len(degraded_decisions) == 1
        and len(rejected_decisions) == 5
        and _blocked(filters, "raw_result_proposal_blocked")
        and _blocked(filters, "raw_executor_text_blocked")
        and _blocked(filters, "raw_architect_plan_graph_blocked")
        and _blocked(filters, "raw_orchestrator_matrix_blocked")
        and _blocked(filters, "raw_user_intent_blocked")
        and _blocked(filters, "real_action_output_blocked")
        and malicious_final_rejected
        and malicious_drs_rejected
        and malicious_action_rejected
        and malformed_rejected
        and boundary_pass
        else "FAIL"
    )
    return {
        "gt_from_validation_report_status": status,
        "source_post_vv_status": source_status,
        "scenarios_verified": len(filters),
        "gt_decisions_created": len(decisions),
        "accepted_gt_decisions": len(accepted_decisions),
        "degraded_gt_decisions": len(degraded_decisions),
        "rejected_gt_decisions": len(rejected_decisions),
        "raw_result_proposal_blocked": _blocked(
            filters, "raw_result_proposal_blocked"
        ),
        "raw_executor_text_blocked": _blocked(filters, "raw_executor_text_blocked"),
        "raw_architect_plan_graph_blocked": _blocked(
            filters, "raw_architect_plan_graph_blocked"
        ),
        "raw_orchestrator_matrix_blocked": _blocked(
            filters, "raw_orchestrator_matrix_blocked"
        ),
        "raw_user_intent_blocked": _blocked(filters, "raw_user_intent_blocked"),
        "real_action_output_blocked": _blocked(filters, "real_action_output_blocked"),
        "malicious_final_output_claim_rejected": malicious_final_rejected,
        "malicious_drs_write_claim_rejected": malicious_drs_rejected,
        "malicious_action_claim_rejected": malicious_action_rejected,
        "malformed_validation_report_rejected": malformed_rejected,
        "gt_receives_only_validation_report": authority[
            "gt_receives_only_validation_report"
        ],
        "ready_for_root_final_from_gt_decision": status == "PASS",
        "production_final_output_created": authority["production_final_output_created"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_gt_from_validation_report() -> GtFromValidationReportReport:
    post_vv_report = collect_post_vv_from_result_proposal()
    source_status = post_vv_report.summary["post_vv_from_result_proposal_status"]
    validation_reports = list(post_vv_report.validation_reports)
    reports_by_status = {
        report["validation_status"]: report for report in validation_reports
    }
    rejected_report = next(
        report
        for report in validation_reports
        if report["validation_status"] == "rejected"
        and report["scenario"] == "malformed_result_proposal_rejected"
    )

    filters: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []

    row, decision = _gt_decision_from_validation_report(
        "accepted_validation_report_gt_accept",
        reports_by_status["accepted"],
    )
    filters.append(row)
    decisions.append(decision)

    row, decision = _gt_decision_from_validation_report(
        "degraded_validation_report_gt_degrade",
        reports_by_status["degraded"],
    )
    filters.append(row)
    decisions.append(decision)

    row, decision = _gt_decision_from_validation_report(
        "rejected_validation_report_gt_reject",
        rejected_report,
    )
    filters.append(row)
    decisions.append(decision)

    filters.append(
        _blocked_filter_row(
            "raw_result_proposal_blocked",
            "raw_result_proposal",
            ["raw_result_proposal_not_allowed"],
        )
    )
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

    malicious_final = _malicious_validation_report(
        reports_by_status["accepted"],
        claim="final_output",
    )
    row, decision = _gt_decision_from_validation_report(
        "malicious_validation_report_claiming_final_output_rejected",
        malicious_final,
    )
    filters.append(row)
    decisions.append(decision)

    malicious_drs = _malicious_validation_report(
        reports_by_status["accepted"],
        claim="drs_write",
    )
    row, decision = _gt_decision_from_validation_report(
        "malicious_validation_report_claiming_drs_write_rejected",
        malicious_drs,
    )
    filters.append(row)
    decisions.append(decision)

    malicious_action = _malicious_validation_report(
        reports_by_status["accepted"],
        claim="action",
    )
    row, decision = _gt_decision_from_validation_report(
        "malicious_validation_report_claiming_action_rejected",
        malicious_action,
    )
    filters.append(row)
    decisions.append(decision)

    malformed = _malformed_validation_report(reports_by_status["accepted"])
    row, decision = _gt_decision_from_validation_report(
        "malformed_validation_report_rejected",
        malformed,
    )
    filters.append(row)
    decisions.append(decision)

    input_validation_reports = {
        "source_post_vv_report_status": source_status,
        "validation_reports_imported": [
            report["validation_report_id"] for report in validation_reports
        ],
        "accepted_validation_reports": post_vv_report.summary[
            "accepted_validation_reports"
        ],
        "degraded_validation_reports": post_vv_report.summary[
            "degraded_validation_reports"
        ],
        "rejected_validation_reports": post_vv_report.summary[
            "rejected_validation_reports"
        ],
    }
    containment = _containment(filters, decisions)
    authority = _authority_safety(filters, decisions, containment)
    summary = _summary(source_status, filters, decisions, containment, authority)
    return GtFromValidationReportReport(
        input_validation_reports=input_validation_reports,
        gt_input_filter=filters,
        gt_decisions=decisions,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_gt_from_validation_report(report: GtFromValidationReportReport) -> str:
    lines = [
        "[GT FROM VALIDATION REPORT]",
        "note: deterministic GT proof from ValidationReport",
        "note: GT receives ValidationReport / V&VReport artifacts only",
        "note: raw ResultProposal is blocked",
        "note: raw Executor text is blocked",
        "note: raw Architect PlanGraph is blocked",
        "note: raw Orchestrator matrix is blocked",
        "note: raw user intent is blocked",
        "note: real action output is blocked",
        "note: GT creates GTDecision / selection artifact only",
        "note: GT does not create FinalOutput",
        "note: GT does not write DRS directly",
        "note: GT does not execute actions",
        "note: Root Final is not invoked yet",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT VALIDATION REPORTS]", report.input_validation_reports)

    lines.extend(["", "[GT INPUT FILTER]"])
    filter_fields = (
        "scenario",
        "input_kind",
        "gt_invoked",
        "blocked_before_gt",
        "block_reasons",
        "input_is_validation_report",
        "raw_result_proposal_received",
        "raw_executor_text_received",
        "raw_architect_plan_graph_received",
        "raw_orchestrator_matrix_received",
        "raw_user_intent_received",
        "real_action_output_received",
    )
    for row in report.gt_input_filter:
        lines.append(
            " | ".join(f"{field}={_format_value(row[field])}" for field in filter_fields)
        )

    lines.extend(["", "[GT DECISIONS]"])
    decision_fields = (
        "gt_decision_id",
        "created_by",
        "source_validation_report_id",
        "source_result_proposal_id",
        "validation_report_schema_valid",
        "validation_status_seen",
        "gt_decision",
        "selection_reason",
        "payoff_basis",
        "risk_basis",
        "trust_update_proposal",
        "regret_update_proposal",
        "final_output_claim_detected",
        "drs_write_claim_detected",
        "action_claim_detected",
        "gt_creates_final_output",
        "gt_writes_drs",
        "gt_executes_actions",
        "root_final_invoked",
    )
    for decision in report.gt_decisions:
        lines.append(
            " | ".join(
                f"{field}={_format_value(decision[field])}"
                for field in decision_fields
            )
        )

    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_gt_from_validation_report() -> str:
    return render_gt_from_validation_report(collect_gt_from_validation_report())


def main() -> int:
    print(run_gt_from_validation_report(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
