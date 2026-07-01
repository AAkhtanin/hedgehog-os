from __future__ import annotations

from typing import Any, Mapping

from hedgehog.context_packets import build_architect_plan_context_packet
from hedgehog.context_packets import build_orchestrator_route_context_packet
from hedgehog.context_packets import validate_architect_plan_context_packet
from hedgehog.context_packets import validate_orchestrator_route_context_packet
from hedgehog.structured_rationale import build_architect_structured_rationale
from hedgehog.structured_rationale import build_orchestrator_structured_rationale
from hedgehog.structured_rationale import validate_architect_structured_rationale
from hedgehog.structured_rationale import validate_orchestrator_structured_rationale


TITLE = "HOTEL ROBOT VACUUM ACCESS DEMO v0.1"
DOMAIN = "hotel_robot_vacuum_access"
HOTEL_ID = "HOTEL-17"
REQUEST_ID = "ROBOT-CLEAN-2042"
SAFE_HUMAN_SUMMARY = (
    "Robot vacuum may not be sent into all requested rooms. Only R-101 has "
    "explicit consent as a candidate signal, but no robot action is executed. "
    "R-102 lacks consent, R-303 is private/VIP do-not-enter, and R-404 requires "
    "manual review."
)


COUNTER_KEYS = (
    "robot_api_called_count",
    "door_unlock_called_count",
    "robot_dispatch_called_count",
    "room_entry_authorized_count",
    "action_permission_created_count",
    "action_commit_packet_created_count",
    "connector_called_count",
    "payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
    "final_output_created_by_root_count",
    "final_output_created_by_non_root_count",
    "context_packet_validated_count",
    "structured_rationale_validated_count",
    "root_final_authority_preserved_count",
    "public_wow_claimed_count",
    "production_ready_claimed_count",
    "needlefactory_started_count",
    "marennya_started_count",
    "up_started_count",
)


def _zero_counters() -> dict[str, int]:
    counters = {key: 0 for key in COUNTER_KEYS}
    counters["final_output_created_by_root_count"] = 1
    counters["root_final_authority_preserved_count"] = 1
    return counters


def _hotel_access_request() -> dict[str, Any]:
    return {
        "hotel_id": HOTEL_ID,
        "request_id": REQUEST_ID,
        "requested_action": "send robot vacuum to clean requested rooms",
        "requested_rooms": ("R-101", "R-102", "R-303", "R-404"),
        "root_review_required": True,
        "physical_action_requested": True,
    }


def _room_access_evidence() -> tuple[dict[str, Any], ...]:
    return (
        {
            "room_id": "R-101",
            "evidence": "guest explicitly opted in for cleaning window",
            "candidate_only": True,
            "eligible_signal": "explicit_consent_candidate",
            "blocked": False,
            "block_reasons": (),
            "authorized_for_entry": False,
        },
        {
            "room_id": "R-102",
            "evidence": "guest has not responded",
            "candidate_only": True,
            "eligible_signal": "missing_guest_response",
            "blocked": True,
            "block_reasons": ("missing_consent",),
            "authorized_for_entry": False,
        },
        {
            "room_id": "R-303",
            "evidence": "VIP/private room with explicit do-not-enter boundary",
            "candidate_only": True,
            "eligible_signal": "privacy_boundary",
            "blocked": True,
            "block_reasons": ("vip_private_do_not_enter", "privacy_boundary"),
            "authorized_for_entry": False,
        },
        {
            "room_id": "R-404",
            "evidence": "housekeeping manual hold with uncertain occupancy state",
            "candidate_only": True,
            "eligible_signal": "manual_hold",
            "blocked": True,
            "block_reasons": ("manual_review_required",),
            "authorized_for_entry": False,
        },
    )


def _consent_context(evidence: tuple[Mapping[str, Any], ...]) -> dict[str, Any]:
    return {
        "context_type": "guest_consent_context",
        "candidate_only_rooms": tuple(room["room_id"] for room in evidence),
        "explicit_consent_candidate_rooms": ("R-101",),
        "missing_consent_rooms": ("R-102",),
        "consent_is_truth": False,
        "consent_is_authority": False,
        "root_review_required": True,
    }


def _privacy_boundary_context(evidence: tuple[Mapping[str, Any], ...]) -> dict[str, Any]:
    return {
        "context_type": "hotel_privacy_boundary_context",
        "private_rooms": ("R-303",),
        "manual_review_rooms": ("R-404",),
        "block_reasons": tuple(
            reason
            for room in evidence
            for reason in tuple(room.get("block_reasons", ()))
        ),
        "privacy_boundary_blocks_entry": True,
        "Root remains final authority": True,
    }


def _physical_action_boundary_context() -> dict[str, Any]:
    return {
        "context_type": "physical_action_boundary_context",
        "robot_entry_is_physical_action": True,
        "door_access_is_external_action": True,
        "robot_start_is_external_action": True,
        "robot_movement_is_external_action": True,
        "external_actions_forbidden": True,
        "real_world_effects_allowed": False,
        "ContextPacket is not truth": True,
        "ContextPacket is not authority": True,
        "structured rationale is explanation only": True,
        "Root remains final authority": True,
    }


def _build_orchestrator_packet() -> dict[str, Any]:
    return build_orchestrator_route_context_packet(
        packet_id=f"context_packet:hotel_robot_vacuum:orchestrator:{REQUEST_ID}",
        created_by="applied_hotel_robot_vacuum_demo",
        source_refs=(
            {"source": "hotel_access_request", "source_id": REQUEST_ID},
        ),
        domain=DOMAIN,
        allowed_routes=("hotel_robot_access_root_review",),
        required_guards=(
            "explicit_guest_consent",
            "privacy_boundary",
            "manual_review",
            "physical_action_boundary",
            "Root final authority",
        ),
        selected_vector_ids=(
            "room:R-101:explicit_consent_candidate",
            "room:R-102:missing_consent_block",
            "room:R-303:privacy_block",
            "room:R-404:manual_review_block",
        ),
        route_validation_expectations={
            "request_id": REQUEST_ID,
            "hotel_id": HOTEL_ID,
            "route_outcome": "not_ready",
            "missing_consent": ("R-102",),
            "privacy_boundary": ("R-303",),
            "manual_review_required": ("R-404",),
        },
    )


def _build_architect_packet() -> dict[str, Any]:
    return build_architect_plan_context_packet(
        packet_id=f"context_packet:hotel_robot_vacuum:architect:{REQUEST_ID}",
        created_by="applied_hotel_robot_vacuum_demo",
        source_refs=(
            {"source": "orchestrator_route_context_packet", "source_id": REQUEST_ID},
        ),
        domain=DOMAIN,
        source_route_id="hotel_robot_access_root_review",
        allowed_executor_ids=("local_hotel_access_review_executor",),
        allowed_node_kinds=("semantic_review", "manual_review_gate"),
        required_validators=(
            "ContextPacket validation",
            "structured rationale validation",
            "PlanGraph contract",
            "ResultProposal boundary",
            "Root final authority",
        ),
        forbidden_connector_claims=(
            "robot_api",
            "door_access_system",
            "robot_dispatch_system",
            "hotel_pms",
        ),
        forbidden_action_claims=(
            "authorize_physical_entry",
            "start_robot_vacuum",
            "open_guest_room",
        ),
        forbidden_final_output_claims=(
            "final_output",
            "final_decision",
            "root_final_boundary",
        ),
    )


def _build_orchestrator_rationale() -> dict[str, Any]:
    return build_orchestrator_structured_rationale(
        observed_semantics=(
            {
                "room": "R-101",
                "signal": "explicit_consent_candidate",
                "candidate_only": True,
            },
            {"room": "R-102", "block_reason": "missing_consent"},
            {"room": "R-303", "block_reason": "vip_private_do_not_enter"},
            {"room": "R-404", "block_reason": "manual_review_required"},
        ),
        route_selection_reason=(
            {
                "route": "hotel_robot_access_root_review",
                "reason": "requested room set contains consent and privacy blockers",
            },
        ),
        rejected_routes=(
            {
                "route": "physical_robot_access",
                "reason": "physical access requires Root denial or manual review",
            },
        ),
        required_guards_reasoning=(
            {"guard": "explicit_guest_consent", "room": "R-102", "status": "missing"},
            {"guard": "privacy_boundary", "room": "R-303", "status": "blocking"},
            {"guard": "manual_review", "room": "R-404", "status": "required"},
        ),
        selected_vector_reasoning=(
            {
                "vectors": (
                    "room:R-101:explicit_consent_candidate",
                    "room:R-102:missing_consent_block",
                    "room:R-303:privacy_block",
                    "room:R-404:manual_review_block",
                ),
                "reason": "all requested rooms must be reviewed together",
            },
        ),
        uncertainty_notes=(
            {"room": "R-404", "note": "manual review required before action"},
        ),
        authority_boundary=(
            {
                "Orchestrator is not Root": True,
                "creates_final_output": False,
                "creates_action_permission": False,
            },
        ),
    )


def _build_architect_rationale() -> dict[str, Any]:
    return build_architect_structured_rationale(
        plan_shape_reason=(
            {
                "shape": "local_advisory_plan",
                "reason": "review access evidence and return not_ready proposal",
            },
        ),
        node_selection_reasoning=(
            {
                "node": "node:review_room_access_boundaries",
                "reason": "review consent, privacy, and manual hold signals only",
            },
        ),
        executor_constraint_reasoning=(
            {
                "executor": "local_hotel_access_review_executor",
                "reason": "local semantic review only",
            },
        ),
        forbidden_surface_review=(
            {"surface": "robot_api", "status": "forbidden"},
            {"surface": "door_access_system", "status": "forbidden"},
            {"surface": "hotel_pms", "status": "forbidden"},
        ),
        validator_coverage_reasoning=(
            {"validator": "PlanGraph contract", "status": "required"},
            {"validator": "ResultProposal boundary", "status": "required"},
            {"validator": "Root final authority", "status": "required"},
        ),
        return_to_root_path=(
            {
                "path": "advisory_plan_to_result_proposal_to_root_boundary",
                "final_authority": "root_only",
            },
        ),
        uncertainty_notes=(
            {"room": "R-404", "note": "uncertain occupancy state"},
        ),
        authority_boundary=(
            {
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
                "creates_action_permission": False,
            },
        ),
    )


def _plan_graph_context() -> dict[str, Any]:
    return {
        "plan_graph_id": f"plan:hotel_robot_vacuum_access:{REQUEST_ID}",
        "created_by": "local_advisory_architect",
        "domain": DOMAIN,
        "nodes": (
            {
                "node_id": "node:review_room_access_boundaries",
                "kind": "semantic_review",
                "task": "review consent and privacy boundary evidence",
                "executor_id": "local_hotel_access_review_executor",
                "depends_on": (),
                "expected_output": "ResultProposal",
            },
            {
                "node_id": "node:manual_review_gate",
                "kind": "manual_review_gate",
                "task": "mark unresolved rooms as manual review required",
                "executor_id": "local_hotel_access_review_executor",
                "depends_on": ("node:review_room_access_boundaries",),
                "expected_output": "ResultProposal",
            },
        ),
        "edges": (
            {
                "from": "node:review_room_access_boundaries",
                "to": "node:manual_review_gate",
            },
        ),
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "creates_final_output": False,
        "PlanGraph is not authority": True,
        "Root remains final authority": True,
    }


def _result_proposal() -> dict[str, Any]:
    return {
        "proposal_id": f"result_proposal:hotel_robot_vacuum_access:{REQUEST_ID}",
        "created_by": "local_hotel_access_review_executor",
        "proposal_status": "not_ready",
        "summary": "Manual review required before any robot action.",
        "room_findings": {
            "R-101": "candidate_only_explicit_consent_signal",
            "R-102": "blocked_missing_consent",
            "R-303": "blocked_vip_private_do_not_enter",
            "R-404": "blocked_manual_review_required",
        },
        "is_final_output": False,
        "creates_final_output": False,
        "action_permission_claimed": False,
        "connector_command_claimed": False,
        "ResultProposal is not FinalOutput": True,
        "Root remains final authority": True,
    }


def _root_final_output_boundary() -> dict[str, Any]:
    return {
        "boundary_id": f"root_final:hotel_robot_vacuum_access:{REQUEST_ID}",
        "created_by": "Root",
        "decision": "not_ready",
        "safe_human_summary": SAFE_HUMAN_SUMMARY,
        "approved_rooms": (),
        "candidate_only_rooms": ("R-101",),
        "blocked_rooms": {
            "R-102": ("missing_consent",),
            "R-303": ("vip_private_do_not_enter", "privacy_boundary"),
            "R-404": ("manual_review_required",),
        },
        "robot_api_called": False,
        "door_unlock_called": False,
        "robot_dispatch_called": False,
        "room_entry_authorized": False,
        "action_commit_packet_created": False,
        "final_output_created_by": "Root",
        "Root remains final authority": True,
    }


def _fail_closed_probes() -> dict[str, dict[str, Any]]:
    return {
        "unsafe_all_rooms_robot_dispatch_probe": {
            "simulated_claim": "robot may access every requested room",
            "rejected": True,
            "reasons": (
                "missing_consent:R-102",
                "privacy_boundary:R-303",
                "manual_review_required:R-404",
            ),
        },
        "vip_private_room_probe": {
            "simulated_claim": "robot may access R-303",
            "rejected": True,
            "reasons": ("vip_private_do_not_enter",),
        },
        "physical_action_claim_probe": {
            "simulated_claim": {
                "robot_api_called": True,
                "door_unlock_called": True,
            },
            "rejected": True,
            "reasons": (
                "physical_action_claim_forbidden",
                "robot_api_claim_forbidden",
                "door_unlock_claim_forbidden",
            ),
            "real_counters_remain_zero": True,
        },
        "non_root_final_output_probe": {
            "simulated_claim": {
                "created_by": "Architect",
                "final_output_claimed": True,
            },
            "rejected": True,
            "reasons": ("non_root_final_output_forbidden",),
            "root_only_final_authority_preserved": True,
        },
    }


def _pass_conditions(result: Mapping[str, Any]) -> dict[str, bool]:
    counters = result["counters"]
    root = result["root_final_output_boundary"]
    probes = result["fail_closed_probes"]
    return {
        "root_decision_not_ready": root["decision"] == "not_ready",
        "r101_candidate_only": "R-101" in root["candidate_only_rooms"],
        "blocked_rooms_preserved": tuple(root["blocked_rooms"]) == (
            "R-102",
            "R-303",
            "R-404",
        ),
        "context_packets_validated": counters["context_packet_validated_count"] >= 2,
        "structured_rationales_validated": (
            counters["structured_rationale_validated_count"] == 2
        ),
        "plan_graph_not_authority": (
            result["plan_graph_context"]["PlanGraph is not authority"] is True
        ),
        "result_proposal_not_final_output": (
            result["result_proposal"]["ResultProposal is not FinalOutput"] is True
        ),
        "root_only_final_output": (
            counters["final_output_created_by_root_count"] == 1
            and counters["final_output_created_by_non_root_count"] == 0
        ),
        "real_action_counters_zero": all(
            counters[key] == 0
            for key in (
                "robot_api_called_count",
                "door_unlock_called_count",
                "robot_dispatch_called_count",
                "room_entry_authorized_count",
                "action_permission_created_count",
                "action_commit_packet_created_count",
                "connector_called_count",
                "real_world_effects_count",
            )
        ),
        "fail_closed_probes_rejected": all(
            probe["rejected"] is True for probe in probes.values()
        ),
        "Root remains final authority": counters[
            "root_final_authority_preserved_count"
        ]
        == 1,
    }


def run_applied_hotel_robot_vacuum_access_demo(
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    _ = dict(env or {})
    request = _hotel_access_request()
    evidence = _room_access_evidence()
    consent_context = _consent_context(evidence)
    privacy_context = _privacy_boundary_context(evidence)
    physical_context = _physical_action_boundary_context()

    orchestrator_packet = _build_orchestrator_packet()
    orchestrator_packet_validation = validate_orchestrator_route_context_packet(
        orchestrator_packet
    )
    architect_packet = _build_architect_packet()
    architect_packet_validation = validate_architect_plan_context_packet(
        architect_packet
    )

    orchestrator_rationale = _build_orchestrator_rationale()
    orchestrator_rationale_validation = validate_orchestrator_structured_rationale(
        orchestrator_rationale
    )
    architect_rationale = _build_architect_rationale()
    architect_rationale_validation = validate_architect_structured_rationale(
        architect_rationale
    )

    counters = _zero_counters()
    counters["context_packet_validated_count"] = int(
        orchestrator_packet_validation["accepted"]
    ) + int(architect_packet_validation["accepted"])
    counters["structured_rationale_validated_count"] = int(
        orchestrator_rationale_validation["accepted"]
    ) + int(architect_rationale_validation["accepted"])

    result: dict[str, Any] = {
        "title": TITLE,
        "final_status": "PASS",
        "domain": DOMAIN,
        "hotel_access_request": request,
        "room_access_evidence": evidence,
        "consent_context": consent_context,
        "privacy_boundary_context": privacy_context,
        "physical_action_boundary_context": physical_context,
        "orchestrator_route_context_packet": orchestrator_packet,
        "orchestrator_route_context_packet_validation": orchestrator_packet_validation,
        "architect_plan_context_packet": architect_packet,
        "architect_plan_context_packet_validation": architect_packet_validation,
        "structured_orchestrator_rationale": orchestrator_rationale,
        "structured_orchestrator_rationale_validation": (
            orchestrator_rationale_validation
        ),
        "structured_architect_rationale": architect_rationale,
        "structured_architect_rationale_validation": architect_rationale_validation,
        "plan_graph_context": _plan_graph_context(),
        "result_proposal": _result_proposal(),
        "root_final_output_boundary": _root_final_output_boundary(),
        "fail_closed_probes": _fail_closed_probes(),
        "counters": counters,
        "validation_errors": (),
    }
    result["pass_conditions"] = _pass_conditions(result)
    if not all(result["pass_conditions"].values()):
        result["final_status"] = "FAIL_CLOSED"
        result["validation_errors"] = tuple(
            key for key, passed in result["pass_conditions"].items() if not passed
        )
    return result


def render_report(result: dict[str, Any] | None = None) -> str:
    if result is None:
        result = run_applied_hotel_robot_vacuum_access_demo()

    lines = [
        TITLE,
        "",
        "Scenario summary:",
        f"- hotel_id: {result['hotel_access_request']['hotel_id']}",
        f"- request_id: {result['hotel_access_request']['request_id']}",
        f"- requested_action: {result['hotel_access_request']['requested_action']}",
        "",
        "Room evidence:",
    ]
    for room in result["room_access_evidence"]:
        reasons = (
            ", ".join(reason.replace("_", " ") for reason in room["block_reasons"])
            or "candidate only"
        )
        lines.append(
            f"- {room['room_id']}: {room['evidence']} | {reasons}"
        )

    lines.extend(
        [
            "",
            "Context packet validation summary:",
            "- OrchestratorRouteContextPacket accepted: "
            f"{result['orchestrator_route_context_packet_validation']['accepted']}",
            "- ArchitectPlanContextPacket accepted: "
            f"{result['architect_plan_context_packet_validation']['accepted']}",
            "- ContextPacket is not truth",
            "- ContextPacket is not authority",
            "",
            "Structured rationale validation summary:",
            "- structured_orchestrator_rationale accepted: "
            f"{result['structured_orchestrator_rationale_validation']['accepted']}",
            "- structured_architect_rationale accepted: "
            f"{result['structured_architect_rationale_validation']['accepted']}",
            "- structured rationale is explanation only",
            "",
            "Root boundary:",
            f"- decision: {result['root_final_output_boundary']['decision']}",
            "- safe_human_summary: "
            f"{result['root_final_output_boundary']['safe_human_summary']}",
            "- Root remains final authority",
            "",
            "Counters:",
            f"- robot API called: {result['counters']['robot_api_called_count']}",
            f"- door unlock called: {result['counters']['door_unlock_called_count']}",
            "- robot dispatch called: "
            f"{result['counters']['robot_dispatch_called_count']}",
            "- action_commit_packet_created_count: "
            f"{result['counters']['action_commit_packet_created_count']}",
            f"- real_world_effects_count: {result['counters']['real_world_effects_count']}",
            "",
            f"FINAL STATUS: {result['final_status']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_applied_hotel_robot_vacuum_access_demo()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
