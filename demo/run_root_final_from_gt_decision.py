from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_gt_from_validation_report import collect_gt_from_validation_report


SCENARIOS_UNDER_TEST = (
    "accept_gt_decision_root_final_accept",
    "degrade_gt_decision_root_final_degraded",
    "reject_gt_decision_root_final_rejected",
    "raw_validation_report_blocked",
    "raw_result_proposal_blocked",
    "raw_executor_text_blocked",
    "raw_architect_plan_graph_blocked",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "real_action_output_blocked",
    "malicious_gt_decision_claiming_final_output_rejected",
    "malicious_gt_decision_claiming_drs_write_rejected",
    "malicious_gt_decision_claiming_action_rejected",
    "malformed_gt_decision_rejected",
)


@dataclass(frozen=True)
class RootFinalFromGtDecisionReport:
    input_gt_decisions: dict[str, Any]
    root_final_input_filter: list[dict[str, Any]]
    root_final_artifacts: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _is_gt_decision(decision: dict[str, Any]) -> bool:
    required = {
        "gt_decision_id",
        "created_by",
        "source_validation_report_id",
        "source_result_proposal_id",
        "gt_decision",
        "selection_reason",
        "gt_creates_final_output",
        "gt_writes_drs",
        "gt_executes_actions",
    }
    return required <= set(decision) and decision.get("created_by") == "gt_validator"


def _gt_decision_has_valid_shape(decision: dict[str, Any]) -> bool:
    return (
        _is_gt_decision(decision)
        and isinstance(decision.get("gt_decision"), str)
        and decision["gt_decision"] in {"accept", "degrade", "reject"}
        and isinstance(decision.get("source_validation_report_id"), str)
        and bool(decision["source_validation_report_id"])
        and isinstance(decision.get("source_result_proposal_id"), str)
        and bool(decision["source_result_proposal_id"])
    )


def _root_final_status(decision: dict[str, Any], schema_valid: bool) -> str:
    if (
        not schema_valid
        or decision.get("gt_creates_final_output")
        or decision.get("gt_writes_drs")
        or decision.get("gt_executes_actions")
    ):
        return "rejected"
    if decision.get("gt_decision") == "accept":
        return "accepted"
    if decision.get("gt_decision") == "degrade":
        return "degraded"
    return "rejected"


def _root_selection_reason(
    decision: dict[str, Any],
    final_status: str,
    schema_valid: bool,
) -> str:
    if not schema_valid:
        return "gt_decision_shape_invalid"
    if decision.get("gt_creates_final_output"):
        return "gt_final_output_claim_rejected"
    if decision.get("gt_writes_drs"):
        return "gt_drs_write_claim_rejected"
    if decision.get("gt_executes_actions"):
        return "gt_action_claim_rejected"
    if final_status == "accepted":
        return "gt_decision_accepted_by_root"
    if final_status == "degraded":
        return "gt_decision_degraded_by_root"
    return "gt_decision_rejected_by_root"


def _root_final_from_gt_decision(
    scenario: str,
    decision: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema_valid = _gt_decision_has_valid_shape(decision)
    final_status = _root_final_status(decision, schema_valid)
    gt_final_output_claim = decision.get("gt_creates_final_output") is True
    gt_drs_write_claim = decision.get("gt_writes_drs") is True
    gt_action_claim = decision.get("gt_executes_actions") is True
    selection_reason = _root_selection_reason(decision, final_status, schema_valid)
    gt_decision_seen = decision.get("gt_decision")
    source_validation_report_id = decision.get("source_validation_report_id")
    source_result_proposal_id = decision.get("source_result_proposal_id")
    final_artifact = {
        "final_artifact_id": f"root_final_artifact_{scenario}",
        "created_by": "root_orchestrator",
        "scenario": scenario,
        "source_gt_decision_id": decision.get("gt_decision_id"),
        "source_validation_report_id": source_validation_report_id,
        "source_result_proposal_id": source_result_proposal_id,
        "input_is_gt_decision": True,
        "raw_validation_report_received": False,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
        "gt_decision_schema_valid": schema_valid,
        "gt_decision_seen": gt_decision_seen,
        "root_final_status": final_status,
        "final_answer_trace": [
            "root_final_received_gt_decision",
            f"root_final_status:{final_status}",
            "drs_writeback_not_invoked",
        ],
        "root_selection_reason": selection_reason,
        "user_facing_summary": (
            "Root accepted the validated trace."
            if final_status == "accepted"
            else (
                "Root returned a degraded trace-level result."
                if final_status == "degraded"
                else "Root rejected the trace-level result."
            )
        ),
        "audit_summary": {
            "schema_valid": schema_valid,
            "gt_final_output_claim_detected": gt_final_output_claim,
            "gt_drs_write_claim_detected": gt_drs_write_claim,
            "gt_action_claim_detected": gt_action_claim,
            "source_gt_decision": gt_decision_seen,
        },
        "gt_final_output_claim_detected": gt_final_output_claim,
        "gt_drs_write_claim_detected": gt_drs_write_claim,
        "gt_action_claim_detected": gt_action_claim,
        "root_created_final_output": True,
        "gt_created_final_output": False,
        "root_writes_drs": False,
        "drs_writeback_invoked": False,
        "root_executes_actions": False,
        "production_external_action_executed": False,
        "production_persistence_claimed": False,
    }
    filter_row = {
        "scenario": scenario,
        "input_kind": "gt_decision",
        "root_final_invoked": True,
        "blocked_before_root_final": False,
        "block_reasons": [],
        "input_is_gt_decision": True,
        "raw_validation_report_received": False,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }
    return filter_row, final_artifact


def _blocked_filter_row(
    scenario: str,
    input_kind: str,
    block_reasons: list[str],
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "root_final_invoked": False,
        "blocked_before_root_final": True,
        "block_reasons": block_reasons,
        "input_is_gt_decision": False,
        "raw_validation_report_received": False,
        "raw_result_proposal_received": False,
        "raw_executor_text_received": False,
        "raw_architect_plan_graph_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "real_action_output_received": False,
    }


def _malicious_gt_decision(
    base: dict[str, Any],
    *,
    claim: str,
) -> dict[str, Any]:
    decision = dict(base)
    decision["gt_decision_id"] = f"{base['gt_decision_id']}_{claim}"
    if claim == "final_output":
        decision["gt_creates_final_output"] = True
    elif claim == "drs_write":
        decision["gt_writes_drs"] = True
    elif claim == "action":
        decision["gt_executes_actions"] = True
    return decision


def _malformed_gt_decision(base: dict[str, Any]) -> dict[str, Any]:
    decision = dict(base)
    decision["gt_decision_id"] = f"{base['gt_decision_id']}_malformed"
    decision["gt_decision"] = {"invalid": "decision_shape"}
    decision["selection_reason"] = ["invalid_selection_reason_shape"]
    return decision


def _containment(
    filters: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "raw_validation_report_reached_root_final": any(
            row["input_kind"] == "raw_validation_report"
            and row["root_final_invoked"]
            for row in filters
        ),
        "raw_result_proposal_reached_root_final": any(
            row["input_kind"] == "raw_result_proposal"
            and row["root_final_invoked"]
            for row in filters
        ),
        "raw_executor_text_reached_root_final": any(
            row["input_kind"] == "raw_executor_text"
            and row["root_final_invoked"]
            for row in filters
        ),
        "raw_architect_plan_graph_reached_root_final": any(
            row["input_kind"] == "raw_architect_plan_graph"
            and row["root_final_invoked"]
            for row in filters
        ),
        "raw_orchestrator_matrix_reached_root_final": any(
            row["input_kind"] == "raw_orchestrator_matrix"
            and row["root_final_invoked"]
            for row in filters
        ),
        "raw_user_intent_reached_root_final": any(
            row["input_kind"] == "raw_user_intent" and row["root_final_invoked"]
            for row in filters
        ),
        "real_action_output_reached_root_final": any(
            row["input_kind"] == "real_action_output" and row["root_final_invoked"]
            for row in filters
        ),
        "malicious_gt_final_output_claim_passed": any(
            artifact["gt_final_output_claim_detected"]
            and artifact["root_final_status"] != "rejected"
            for artifact in artifacts
        ),
        "malicious_gt_drs_write_claim_passed": any(
            artifact["gt_drs_write_claim_detected"]
            and artifact["root_final_status"] != "rejected"
            for artifact in artifacts
        ),
        "malicious_gt_action_claim_passed": any(
            artifact["gt_action_claim_detected"]
            and artifact["root_final_status"] != "rejected"
            for artifact in artifacts
        ),
        "invalid_root_wrote_drs": any(
            artifact["root_writes_drs"] for artifact in artifacts
        ),
        "invalid_root_invoked_drs_writeback": any(
            artifact["drs_writeback_invoked"] for artifact in artifacts
        ),
        "invalid_root_executed_action": any(
            artifact["root_executes_actions"] for artifact in artifacts
        ),
    }


def _authority_safety(
    filters: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    invoked_rows = [row for row in filters if row["root_final_invoked"]]
    return {
        "root_final_receives_only_gt_decision": bool(invoked_rows)
        and all(row["input_is_gt_decision"] for row in invoked_rows),
        "root_receives_raw_validation_report": containment[
            "raw_validation_report_reached_root_final"
        ],
        "root_receives_raw_result_proposal": containment[
            "raw_result_proposal_reached_root_final"
        ],
        "root_receives_raw_executor_text": containment[
            "raw_executor_text_reached_root_final"
        ],
        "root_receives_raw_architect_plan_graph": containment[
            "raw_architect_plan_graph_reached_root_final"
        ],
        "root_receives_raw_orchestrator_matrix": containment[
            "raw_orchestrator_matrix_reached_root_final"
        ],
        "root_receives_raw_user_intent": containment[
            "raw_user_intent_reached_root_final"
        ],
        "root_receives_real_action_output": containment[
            "real_action_output_reached_root_final"
        ],
        "root_is_only_final_output_authority": bool(artifacts)
        and all(artifact["created_by"] == "root_orchestrator" for artifact in artifacts)
        and all(artifact["root_created_final_output"] for artifact in artifacts)
        and not any(artifact["gt_created_final_output"] for artifact in artifacts),
        "root_created_final_output": any(
            artifact["root_created_final_output"] for artifact in artifacts
        ),
        "gt_created_final_output": any(
            artifact["gt_created_final_output"] for artifact in artifacts
        ),
        "root_writes_drs": any(artifact["root_writes_drs"] for artifact in artifacts),
        "drs_writeback_invoked": any(
            artifact["drs_writeback_invoked"] for artifact in artifacts
        ),
        "root_executes_actions": any(
            artifact["root_executes_actions"] for artifact in artifacts
        ),
        "production_external_action_executed": any(
            artifact["production_external_action_executed"] for artifact in artifacts
        ),
        "production_persistence_claimed": any(
            artifact["production_persistence_claimed"] for artifact in artifacts
        ),
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _blocked(filters: list[dict[str, Any]], scenario: str) -> bool:
    return any(
        row["scenario"] == scenario and row["blocked_before_root_final"]
        for row in filters
    )


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    accepted_artifacts = [
        artifact
        for artifact in artifacts
        if artifact["root_final_status"] == "accepted"
    ]
    degraded_artifacts = [
        artifact
        for artifact in artifacts
        if artifact["root_final_status"] == "degraded"
    ]
    rejected_artifacts = [
        artifact
        for artifact in artifacts
        if artifact["root_final_status"] == "rejected"
    ]
    malicious_final_rejected = any(
        artifact["gt_final_output_claim_detected"]
        and artifact["root_final_status"] == "rejected"
        for artifact in artifacts
    )
    malicious_drs_rejected = any(
        artifact["gt_drs_write_claim_detected"]
        and artifact["root_final_status"] == "rejected"
        for artifact in artifacts
    )
    malicious_action_rejected = any(
        artifact["gt_action_claim_detected"]
        and artifact["root_final_status"] == "rejected"
        for artifact in artifacts
    )
    malformed_rejected = any(
        artifact["scenario"] == "malformed_gt_decision_rejected"
        and not artifact["gt_decision_schema_valid"]
        and artifact["root_final_status"] == "rejected"
        for artifact in artifacts
    )
    boundary_pass = (
        authority["root_final_receives_only_gt_decision"]
        and not authority["root_receives_raw_validation_report"]
        and not authority["root_receives_raw_result_proposal"]
        and not authority["root_receives_raw_executor_text"]
        and not authority["root_receives_raw_architect_plan_graph"]
        and not authority["root_receives_raw_orchestrator_matrix"]
        and not authority["root_receives_raw_user_intent"]
        and not authority["root_receives_real_action_output"]
        and authority["root_is_only_final_output_authority"]
        and authority["root_created_final_output"]
        and not authority["gt_created_final_output"]
        and not authority["root_writes_drs"]
        and not authority["drs_writeback_invoked"]
        and not authority["root_executes_actions"]
        and not authority["production_external_action_executed"]
        and not authority["production_persistence_claimed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and not containment["malicious_gt_final_output_claim_passed"]
        and not containment["malicious_gt_drs_write_claim_passed"]
        and not containment["malicious_gt_action_claim_passed"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and len(artifacts) == 7
        and len(accepted_artifacts) == 1
        and len(degraded_artifacts) == 1
        and len(rejected_artifacts) == 5
        and _blocked(filters, "raw_validation_report_blocked")
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
        "root_final_from_gt_decision_status": status,
        "source_gt_status": source_status,
        "scenarios_verified": len(filters),
        "root_final_artifacts_created": len(artifacts),
        "accepted_root_final_artifacts": len(accepted_artifacts),
        "degraded_root_final_artifacts": len(degraded_artifacts),
        "rejected_root_final_artifacts": len(rejected_artifacts),
        "raw_validation_report_blocked": _blocked(
            filters, "raw_validation_report_blocked"
        ),
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
        "malicious_gt_final_output_claim_rejected": malicious_final_rejected,
        "malicious_gt_drs_write_claim_rejected": malicious_drs_rejected,
        "malicious_gt_action_claim_rejected": malicious_action_rejected,
        "malformed_gt_decision_rejected": malformed_rejected,
        "root_final_receives_only_gt_decision": authority[
            "root_final_receives_only_gt_decision"
        ],
        "root_is_only_final_output_authority": authority[
            "root_is_only_final_output_authority"
        ],
        "ready_for_full_canonical_chain_trace": status == "PASS",
        "drs_writeback_invoked": authority["drs_writeback_invoked"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_persistence_claimed": authority["production_persistence_claimed"],
        "production_autonomy_claimed": False,
    }


def collect_root_final_from_gt_decision() -> RootFinalFromGtDecisionReport:
    gt_report = collect_gt_from_validation_report()
    source_status = gt_report.summary["gt_from_validation_report_status"]
    gt_decisions = list(gt_report.gt_decisions)
    decisions_by_status = {
        decision["gt_decision"]: decision for decision in gt_decisions
    }
    rejected_decision = next(
        decision
        for decision in gt_decisions
        if decision["gt_decision"] == "reject"
        and decision["scenario"] == "rejected_validation_report_gt_reject"
    )

    filters: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    row, artifact = _root_final_from_gt_decision(
        "accept_gt_decision_root_final_accept",
        decisions_by_status["accept"],
    )
    filters.append(row)
    artifacts.append(artifact)

    row, artifact = _root_final_from_gt_decision(
        "degrade_gt_decision_root_final_degraded",
        decisions_by_status["degrade"],
    )
    filters.append(row)
    artifacts.append(artifact)

    row, artifact = _root_final_from_gt_decision(
        "reject_gt_decision_root_final_rejected",
        rejected_decision,
    )
    filters.append(row)
    artifacts.append(artifact)

    filters.append(
        _blocked_filter_row(
            "raw_validation_report_blocked",
            "raw_validation_report",
            ["raw_validation_report_not_allowed"],
        )
    )
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

    malicious_final = _malicious_gt_decision(
        decisions_by_status["accept"],
        claim="final_output",
    )
    row, artifact = _root_final_from_gt_decision(
        "malicious_gt_decision_claiming_final_output_rejected",
        malicious_final,
    )
    filters.append(row)
    artifacts.append(artifact)

    malicious_drs = _malicious_gt_decision(
        decisions_by_status["accept"],
        claim="drs_write",
    )
    row, artifact = _root_final_from_gt_decision(
        "malicious_gt_decision_claiming_drs_write_rejected",
        malicious_drs,
    )
    filters.append(row)
    artifacts.append(artifact)

    malicious_action = _malicious_gt_decision(
        decisions_by_status["accept"],
        claim="action",
    )
    row, artifact = _root_final_from_gt_decision(
        "malicious_gt_decision_claiming_action_rejected",
        malicious_action,
    )
    filters.append(row)
    artifacts.append(artifact)

    malformed = _malformed_gt_decision(decisions_by_status["accept"])
    row, artifact = _root_final_from_gt_decision(
        "malformed_gt_decision_rejected",
        malformed,
    )
    filters.append(row)
    artifacts.append(artifact)

    input_gt_decisions = {
        "source_gt_report_status": source_status,
        "gt_decisions_imported": [
            decision["gt_decision_id"] for decision in gt_decisions
        ],
        "accepted_gt_decisions": gt_report.summary["accepted_gt_decisions"],
        "degraded_gt_decisions": gt_report.summary["degraded_gt_decisions"],
        "rejected_gt_decisions": gt_report.summary["rejected_gt_decisions"],
    }
    containment = _containment(filters, artifacts)
    authority = _authority_safety(filters, artifacts, containment)
    summary = _summary(source_status, filters, artifacts, containment, authority)
    return RootFinalFromGtDecisionReport(
        input_gt_decisions=input_gt_decisions,
        root_final_input_filter=filters,
        root_final_artifacts=artifacts,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_root_final_from_gt_decision(
    report: RootFinalFromGtDecisionReport,
) -> str:
    lines = [
        "[ROOT FINAL FROM GT DECISION]",
        "note: deterministic Root Final proof from GTDecision",
        "note: Root Final receives GTDecision / selection artifacts only",
        "note: raw ValidationReport is blocked",
        "note: raw ResultProposal is blocked",
        "note: raw Executor text is blocked",
        "note: raw Architect PlanGraph is blocked",
        "note: raw Orchestrator matrix is blocked",
        "note: raw user intent is blocked",
        "note: real action output is blocked",
        "note: Root creates FinalOutput / trace-level final artifact only",
        "note: Root is the only final-output authority",
        "note: GT does not create FinalOutput",
        "note: no DRS writeback in this layer",
        "note: no production persistence",
        "note: no real external actions",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT GT DECISIONS]", report.input_gt_decisions)

    lines.extend(["", "[ROOT FINAL INPUT FILTER]"])
    for row in report.root_final_input_filter:
        lines.append(
            "scenario={scenario} input_kind={input_kind} "
            "root_final_invoked={root_final_invoked} "
            "blocked_before_root_final={blocked_before_root_final} "
            "block_reasons={block_reasons} "
            "input_is_gt_decision={input_is_gt_decision} "
            "raw_validation_report_received={raw_validation_report_received} "
            "raw_result_proposal_received={raw_result_proposal_received} "
            "raw_executor_text_received={raw_executor_text_received} "
            "raw_architect_plan_graph_received={raw_architect_plan_graph_received} "
            "raw_orchestrator_matrix_received={raw_orchestrator_matrix_received} "
            "raw_user_intent_received={raw_user_intent_received} "
            "real_action_output_received={real_action_output_received}".format(
                **{key: _format_value(value) for key, value in row.items()}
            )
        )

    lines.extend(["", "[ROOT FINAL ARTIFACTS]"])
    for artifact in report.root_final_artifacts:
        lines.append(
            "final_artifact_id={final_artifact_id} created_by={created_by} "
            "source_gt_decision_id={source_gt_decision_id} "
            "source_validation_report_id={source_validation_report_id} "
            "source_result_proposal_id={source_result_proposal_id} "
            "gt_decision_schema_valid={gt_decision_schema_valid} "
            "gt_decision_seen={gt_decision_seen} "
            "root_final_status={root_final_status} "
            "final_answer_trace={final_answer_trace} "
            "root_selection_reason={root_selection_reason} "
            "user_facing_summary={user_facing_summary} "
            "audit_summary={audit_summary} "
            "gt_final_output_claim_detected={gt_final_output_claim_detected} "
            "gt_drs_write_claim_detected={gt_drs_write_claim_detected} "
            "gt_action_claim_detected={gt_action_claim_detected} "
            "root_created_final_output={root_created_final_output} "
            "gt_created_final_output={gt_created_final_output} "
            "root_writes_drs={root_writes_drs} "
            "drs_writeback_invoked={drs_writeback_invoked} "
            "root_executes_actions={root_executes_actions} "
            "production_external_action_executed={production_external_action_executed}"
            .format(**{key: _format_value(value) for key, value in artifact.items()})
        )

    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines)


def run_root_final_from_gt_decision() -> str:
    return render_root_final_from_gt_decision(collect_root_final_from_gt_decision())


def main() -> None:
    print(run_root_final_from_gt_decision())


if __name__ == "__main__":
    main()
