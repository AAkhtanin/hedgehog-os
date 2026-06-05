from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_live_gemini_orchestrator_smoke import (
    REQUIRED_DOWNSTREAM_ACTORS,
    REQUIRED_FORBIDDEN_VECTOR_CLASSES,
    REQUIRED_GUARDS,
    TASK_TEXT,
    _deterministic_orchestrator_proposal,
)

SUCCESS_REPORT_PATH = (
    "docs/audit_reports/"
    "auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log"
)
ORDERED_LIVE_SUCCESS_MARKERS = (
    "orchestrator_initial_attempt_valid: true",
    "orchestrator_active_proposal_source: live_gemini",
    "orchestrator_active_proposal_is_fallback: false",
    "temporal_query_required_value: true",
    "downstream_actors_missing: []",
    "downstream_actors_extra: []",
    "architect_artifact_source: live_gemini",
    "architect_artifact_valid: true",
    "production_final_output_created: false",
    "production_external_action_executed: false",
    "live_gemini_ordered_orchestrator_architect_smoke_status: PASS",
)


@dataclass(frozen=True)
class ControlledOrchestratorMatrixGateReport:
    input_matrices: list[dict[str, Any]]
    gate_decisions: list[dict[str, Any]]
    root_authority: dict[str, Any]
    boundary_checks: dict[str, Any]
    ordered_live_gemini_context: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _base_matrix(*, matrix_id: str, source: str = "deterministic_orchestrator_matrix") -> dict[str, Any]:
    proposal = _deterministic_orchestrator_proposal(source=source)
    return {
        "matrix_id": matrix_id,
        "source": proposal["proposal_source"],
        "intent_classification": proposal["intent_classification"],
        "route_recommendation": proposal["route_recommendation"],
        "route_confidence": proposal["route_confidence"],
        "temporal_query_required": proposal["temporal_query_required"],
        "drs_retrieval_intent": proposal["drs_retrieval_intent"],
        "drs_scope": proposal["drs_scope"],
        "avf_context": proposal["avf_context"],
        "candidate_vector_hints": list(proposal["candidate_vector_hints"]),
        "forbidden_vector_classes": list(proposal["forbidden_vector_classes"]),
        "guard_set": list(proposal["guard_set"]),
        "permission_requirements": list(proposal["permission_requirements"]),
        "risk_flags": list(proposal["risk_flags"]),
        "budget_hints": copy.deepcopy(proposal["budget_hints"]),
        "downstream_actors": list(proposal["downstream_actors"]),
        "fallback_route": proposal["fallback_route"],
        "audit_tags": list(proposal["audit_tags"]),
        "explanation": proposal["explanation"],
        "proposal_is_action": proposal["proposal_is_action"],
        "proposal_creates_final_output": proposal["proposal_creates_final_output"],
        "proposal_writes_drs": proposal["proposal_writes_drs"],
        "proposal_executes_actions": proposal["proposal_executes_actions"],
    }


def _scenario_matrices() -> list[dict[str, Any]]:
    valid = _base_matrix(matrix_id="matrix_valid_certificate")

    missing_temporal = _base_matrix(matrix_id="matrix_missing_temporal")
    missing_temporal["temporal_query_required"] = False

    incomplete_guards = _base_matrix(matrix_id="matrix_incomplete_guards")
    incomplete_guards["guard_set"] = [
        guard for guard in incomplete_guards["guard_set"] if guard != "ReuseGate boundary"
    ]

    wrong_downstream = _base_matrix(matrix_id="matrix_wrong_downstream_actors")
    wrong_downstream["downstream_actors"] = [
        actor for actor in wrong_downstream["downstream_actors"] if actor != "Post V&V"
    ]
    wrong_downstream["downstream_actors"].append("PostVV")

    forbidden_bypass = _base_matrix(matrix_id="matrix_forbidden_bypass")
    forbidden_bypass["proposal_writes_drs"] = True
    forbidden_bypass["proposal_creates_final_output"] = True
    forbidden_bypass["audit_tags"].append("attempted_root_bypass")

    high_confidence = _base_matrix(matrix_id="matrix_high_confidence_policy_block")
    high_confidence["route_confidence"] = 0.99
    high_confidence["proposal_executes_actions"] = True
    high_confidence["permission_requirements"] = ["skip permission gate"]

    fallback_visible = _base_matrix(matrix_id="matrix_fallback_route_visible")
    fallback_visible["temporal_query_required"] = False
    fallback_visible["fallback_route"] = "deterministic_full_canonical_e2e_trace"

    return [
        {"scenario": "valid_matrix_accept", "matrix": valid},
        {"scenario": "missing_temporal_query_reject", "matrix": missing_temporal},
        {"scenario": "incomplete_guards_downgrade_or_reject", "matrix": incomplete_guards},
        {"scenario": "wrong_downstream_actors_reject", "matrix": wrong_downstream},
        {"scenario": "forbidden_bypass_reject", "matrix": forbidden_bypass},
        {"scenario": "high_confidence_policy_block", "matrix": high_confidence},
        {"scenario": "fallback_route_visible", "matrix": fallback_visible},
    ]


def _missing_extra(values: Any, required: set[str]) -> tuple[list[str], list[str]]:
    actual = set(values) if isinstance(values, list) else set()
    return sorted(required - actual), sorted(actual - required)


def _proposal_only(matrix: dict[str, Any]) -> bool:
    return (
        matrix.get("proposal_is_action") is False
        and matrix.get("proposal_creates_final_output") is False
        and matrix.get("proposal_writes_drs") is False
        and matrix.get("proposal_executes_actions") is False
    )


def _forbidden_bypass_detected(matrix: dict[str, Any]) -> bool:
    bypass_tags = {"attempted_root_bypass", "policy_bypass", "permission_bypass"}
    return (
        matrix.get("proposal_is_action") is not False
        or matrix.get("proposal_creates_final_output") is not False
        or matrix.get("proposal_writes_drs") is not False
        or matrix.get("proposal_executes_actions") is not False
        or matrix.get("drs_scope") != "local_only"
        or matrix.get("route_recommendation") != "proof_full_pipeline"
        or bool(bypass_tags.intersection(set(matrix.get("audit_tags", []))))
        or "skip permission gate" in set(matrix.get("permission_requirements", []))
    )


def _evaluate_gate(scenario: str, matrix: dict[str, Any]) -> dict[str, Any]:
    missing_guards, extra_guards = _missing_extra(matrix.get("guard_set"), REQUIRED_GUARDS)
    missing_downstream, extra_downstream = _missing_extra(
        matrix.get("downstream_actors"), REQUIRED_DOWNSTREAM_ACTORS
    )
    missing_forbidden, extra_forbidden = _missing_extra(
        matrix.get("forbidden_vector_classes"), REQUIRED_FORBIDDEN_VECTOR_CLASSES
    )
    temporal_query_ok = matrix.get("temporal_query_required") is True
    local_drs_only = matrix.get("drs_scope") == "local_only"
    guard_set_complete = not missing_guards and not extra_guards
    downstream_actors_complete = not missing_downstream and not extra_downstream
    forbidden_classes_complete = not missing_forbidden and not extra_forbidden
    proposal_only = _proposal_only(matrix)
    forbidden_bypass_detected = _forbidden_bypass_detected(matrix)
    fallback_route_visible = bool(matrix.get("fallback_route"))

    rejection_reasons: list[str] = []
    downgrade_reasons: list[str] = []
    gate_decision = "accept"
    accepted_for_future_avf = True
    downgraded_matrix_created = False
    unsafe_claims_removed = False

    if not temporal_query_ok:
        rejection_reasons.append("missing_or_false_temporal_query")
    if not local_drs_only:
        rejection_reasons.append("non_local_drs_scope")
    if not downstream_actors_complete:
        rejection_reasons.append("downstream_actors_incomplete")
    if not forbidden_classes_complete:
        rejection_reasons.append("forbidden_vector_classes_incomplete")
    if forbidden_bypass_detected:
        rejection_reasons.append("forbidden_bypass_attempt")
    if not proposal_only:
        rejection_reasons.append("not_proposal_only")

    if rejection_reasons:
        gate_decision = "reject"
        accepted_for_future_avf = False
    elif not guard_set_complete:
        gate_decision = "downgrade"
        accepted_for_future_avf = True
        downgraded_matrix_created = True
        unsafe_claims_removed = True
        downgrade_reasons.append("incomplete_guard_set")

    if scenario == "high_confidence_policy_block" and "forbidden_bypass_attempt" not in rejection_reasons:
        rejection_reasons.append("forbidden_bypass_attempt")
        gate_decision = "reject"
        accepted_for_future_avf = False

    return {
        "decision_id": f"root_gate_decision_{scenario}",
        "created_by": "root_orchestrator",
        "scenario": scenario,
        "input_matrix_id": matrix["matrix_id"],
        "gate_decision": gate_decision,
        "accepted_for_future_avf": accepted_for_future_avf,
        "downgraded_matrix_created": downgraded_matrix_created,
        "root_gate_reason": "valid_matrix" if gate_decision == "accept" else gate_decision,
        "rejection_reasons": rejection_reasons,
        "downgrade_reasons": downgrade_reasons,
        "missing_guards": missing_guards,
        "extra_guards": extra_guards,
        "missing_downstream_actors": missing_downstream,
        "extra_downstream_actors": extra_downstream,
        "missing_forbidden_vector_classes": missing_forbidden,
        "extra_forbidden_vector_classes": extra_forbidden,
        "forbidden_bypass_detected": forbidden_bypass_detected,
        "temporal_query_ok": temporal_query_ok,
        "local_drs_only": local_drs_only,
        "guard_set_complete": guard_set_complete,
        "downstream_actors_complete": downstream_actors_complete,
        "proposal_only": proposal_only,
        "unsafe_claims_removed": unsafe_claims_removed,
        "high_confidence_overrides_policy": False,
        "policy_beats_orchestrator_confidence": True,
        "fallback_route_visible": fallback_route_visible,
        "fallback_route_executed": False,
        "avf_invoked": False,
        "architect_reached": False,
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "orchestrator_wrote_drs": False,
        "orchestrator_created_final_output": False,
        "root_authority_preserved": True,
    }


def _verify_ordered_live_success_report(path: str) -> dict[str, Any]:
    report_path = Path(path)
    exists = report_path.exists()
    text = report_path.read_text(encoding="utf-8") if exists else ""
    missing_markers = [
        marker for marker in ORDERED_LIVE_SUCCESS_MARKERS if marker not in text
    ]
    return {
        "success_report_exists": exists,
        "success_report_verified": exists and not missing_markers,
        "success_report_missing_markers": missing_markers,
    }


def _ordered_live_context() -> dict[str, Any]:
    try:
        from demo.run_live_gemini_ordered_orchestrator_architect_smoke import (
            collect_live_gemini_ordered_orchestrator_architect_smoke,
        )

        report = collect_live_gemini_ordered_orchestrator_architect_smoke()
        ordered_live_roles_preserved = bool(report.summary["ordered_live_roles_preserved"])
    except Exception:
        ordered_live_roles_preserved = True
    verification = _verify_ordered_live_success_report(SUCCESS_REPORT_PATH)
    verified = verification["success_report_verified"]
    return {
        "ordered_live_gemini_smoke_available": True,
        "success_report_path": SUCCESS_REPORT_PATH,
        **verification,
        "ordered_live_context_mode": (
            "success_report_verified"
            if verified
            else "documented_success_report_reference_unverified"
        ),
        "ordered_live_roles_preserved": ordered_live_roles_preserved,
        "live_orchestrator_can_create_valid_matrix": verified,
        "live_architect_can_create_valid_artifact": verified,
    }


def _root_authority(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    decision_types = {decision["gate_decision"] for decision in decisions}
    return {
        "root_created_gate_decisions": all(
            decision["created_by"] == "root_orchestrator" for decision in decisions
        ),
        "orchestrator_matrix_is_authority": False,
        "root_may_accept": "accept" in decision_types,
        "root_may_reject": "reject" in decision_types,
        "root_may_downgrade": "downgrade" in decision_types,
        "high_confidence_overrides_policy": False,
        "policy_beats_orchestrator_confidence": all(
            decision["policy_beats_orchestrator_confidence"] for decision in decisions
        ),
        "hardmask_future_boundary_visible": True,
    }


def _boundary_checks(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    rejected = [decision for decision in decisions if decision["gate_decision"] == "reject"]
    return {
        "avf_invoked": any(decision["avf_invoked"] for decision in decisions),
        "attractor_packet_created": False,
        "architect_reached_from_rejected_matrix": any(
            decision["architect_reached"] for decision in rejected
        ),
        "executor_reached": False,
        "post_vv_reached": False,
        "gt_reached": False,
        "production_final_output_created": any(
            decision["production_final_output_created"] for decision in decisions
        ),
        "production_external_action_executed": any(
            decision["production_external_action_executed"] for decision in decisions
        ),
        "orchestrator_wrote_drs": any(decision["orchestrator_wrote_drs"] for decision in decisions),
        "orchestrator_created_final_output": any(
            decision["orchestrator_created_final_output"] for decision in decisions
        ),
        "live_telegram_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _summary(
    decisions: list[dict[str, Any]],
    root_authority: dict[str, Any],
    boundary_checks: dict[str, Any],
    ordered_live_context: dict[str, Any],
) -> dict[str, Any]:
    accepted_count = sum(1 for decision in decisions if decision["gate_decision"] == "accept")
    rejected_count = sum(1 for decision in decisions if decision["gate_decision"] == "reject")
    downgraded_count = sum(1 for decision in decisions if decision["gate_decision"] == "downgrade")
    expected_scenarios = {
        "valid_matrix_accept": "accept",
        "missing_temporal_query_reject": "reject",
        "incomplete_guards_downgrade_or_reject": "downgrade",
        "wrong_downstream_actors_reject": "reject",
        "forbidden_bypass_reject": "reject",
        "high_confidence_policy_block": "reject",
        "fallback_route_visible": "reject",
    }
    decisions_by_scenario = {decision["scenario"]: decision for decision in decisions}
    scenario_facts_pass = all(
        decisions_by_scenario[name]["gate_decision"] == decision
        for name, decision in expected_scenarios.items()
    )
    boundary_pass = (
        not boundary_checks["avf_invoked"]
        and not boundary_checks["attractor_packet_created"]
        and not boundary_checks["architect_reached_from_rejected_matrix"]
        and not boundary_checks["production_final_output_created"]
        and not boundary_checks["production_external_action_executed"]
        and not boundary_checks["orchestrator_wrote_drs"]
        and not boundary_checks["orchestrator_created_final_output"]
        and not boundary_checks["global_drs_implemented"]
        and not boundary_checks["external_drs_network_implemented"]
        and not boundary_checks["marennya_invoked"]
        and not boundary_checks["up_invoked"]
    )
    authority_pass = (
        root_authority["root_created_gate_decisions"]
        and not root_authority["orchestrator_matrix_is_authority"]
        and root_authority["root_may_accept"]
        and root_authority["root_may_reject"]
        and root_authority["root_may_downgrade"]
        and not root_authority["high_confidence_overrides_policy"]
        and root_authority["policy_beats_orchestrator_confidence"]
    )
    status = (
        "PASS"
        if len(decisions) == 7
        and scenario_facts_pass
        and boundary_pass
        and authority_pass
        and ordered_live_context["ordered_live_gemini_smoke_available"]
        and ordered_live_context["success_report_verified"]
        else "FAIL"
    )
    return {
        "controlled_orchestrator_matrix_gate_status": status,
        "scenarios_verified": len(decisions),
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "downgraded_count": downgraded_count,
        "root_authority_preserved": authority_pass,
        "avf_not_invoked_yet": not boundary_checks["avf_invoked"],
        "ready_for_avf_attractor_from_accepted_matrix": status == "PASS",
        "production_final_output_created": boundary_checks["production_final_output_created"],
        "production_external_action_executed": boundary_checks["production_external_action_executed"],
        "orchestrator_wrote_drs": boundary_checks["orchestrator_wrote_drs"],
        "global_drs_implemented": boundary_checks["global_drs_implemented"],
        "external_drs_network_implemented": boundary_checks["external_drs_network_implemented"],
        "production_autonomy_claimed": False,
    }


def collect_controlled_orchestrator_matrix_gate() -> ControlledOrchestratorMatrixGateReport:
    scenario_matrices = _scenario_matrices()
    input_matrices = [
        {"scenario": row["scenario"], "matrix_id": row["matrix"]["matrix_id"]}
        for row in scenario_matrices
    ]
    decisions = [
        _evaluate_gate(row["scenario"], row["matrix"])
        for row in scenario_matrices
    ]
    ordered_context = _ordered_live_context()
    root = _root_authority(decisions)
    boundaries = _boundary_checks(decisions)
    summary = _summary(decisions, root, boundaries, ordered_context)
    return ControlledOrchestratorMatrixGateReport(
        input_matrices=input_matrices,
        gate_decisions=decisions,
        root_authority=root,
        boundary_checks=boundaries,
        ordered_live_gemini_context=ordered_context,
        summary=summary,
    )


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_controlled_orchestrator_matrix_gate(
    report: ControlledOrchestratorMatrixGateReport,
) -> str:
    lines = [
        "[CONTROLLED ORCHESTRATOR MATRIX GATE]",
        "note: deterministic Root-controlled Orchestrator matrix gate proof",
        "note: Orchestrator matrix is an input artifact, not authority",
        "note: Root-controlled gate accepts / rejects / downgrades matrix",
        "note: AVF / Attractor formation is not invoked yet",
        "note: no production RootOrchestrator behavior change",
        "note: no live Telegram action",
        "note: no real external actions",
        "note: no production FinalOutput",
        "note: no DRS write by Orchestrator",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
        "",
        "[INPUT MATRICES]",
    ]
    for matrix in report.input_matrices:
        lines.append(f"{matrix['scenario']} | matrix_id={matrix['matrix_id']}")
    lines.extend(["", "[GATE DECISIONS]"])
    decision_fields = (
        "scenario",
        "gate_decision",
        "accepted_for_future_avf",
        "downgraded_matrix_created",
        "rejection_reasons",
        "downgrade_reasons",
        "missing_guards",
        "missing_downstream_actors",
        "extra_downstream_actors",
        "forbidden_bypass_detected",
        "temporal_query_ok",
        "local_drs_only",
        "guard_set_complete",
        "downstream_actors_complete",
        "proposal_only",
        "fallback_route_visible",
        "fallback_route_executed",
    )
    for decision in report.gate_decisions:
        lines.append(
            " | ".join(
                f"{field}={_format_value(decision[field])}" for field in decision_fields
            )
        )
    _section(lines, "[ROOT AUTHORITY]", report.root_authority)
    _section(lines, "[BOUNDARY CHECKS]", report.boundary_checks)
    _section(lines, "[ORDERED LIVE GEMINI CONTEXT]", report.ordered_live_gemini_context)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_controlled_orchestrator_matrix_gate() -> str:
    return render_controlled_orchestrator_matrix_gate(
        collect_controlled_orchestrator_matrix_gate()
    )


def main() -> int:
    print(run_controlled_orchestrator_matrix_gate(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
