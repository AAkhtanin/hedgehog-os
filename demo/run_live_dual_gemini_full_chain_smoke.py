from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from demo.run_live_gemini_orchestrator_smoke import (
    REQUIRED_DOWNSTREAM_ACTORS,
    REQUIRED_FORBIDDEN_VECTOR_CLASSES,
    REQUIRED_GUARDS,
    _config_value,
    _extract_json_object,
)


TASK_TEXT = (
    "Create a safe Root-controlled certificate workflow plan and produce a "
    "trace-level final answer. The system must preserve Root authority, avoid "
    "external actions, avoid DRS writeback, and keep all artifacts bounded."
)
TASK_ID = "live_dual_gemini_full_chain_certificate"
DEFAULT_MODEL = "gemini-2.5-flash"

MATRIX_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "matrix_id",
        "created_by",
        "source",
        "task_id",
        "route_recommendation",
        "temporal_query_required",
        "drs_scope",
        "proposal_only",
        "guard_set",
        "downstream_actors",
        "candidate_vector_hints",
        "forbidden_vector_classes",
        "risk_flags",
        "budget_hints",
        "confidence",
        "no_final_output",
        "no_drs_write",
        "no_action_execution",
    ],
    "properties": {
        "matrix_id": {"type": "string"},
        "created_by": {"type": "string"},
        "source": {"type": "string"},
        "task_id": {"type": "string"},
        "route_recommendation": {"type": "string", "enum": ["proof_full_pipeline"]},
        "temporal_query_required": {"type": "boolean"},
        "drs_scope": {"type": "string", "enum": ["local_only"]},
        "proposal_only": {"type": "boolean"},
        "guard_set": {"type": "array", "items": {"type": "string"}},
        "downstream_actors": {"type": "array", "items": {"type": "string"}},
        "candidate_vector_hints": {"type": "array", "items": {"type": "string"}},
        "forbidden_vector_classes": {"type": "array", "items": {"type": "string"}},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
        "budget_hints": {"type": "object"},
        "confidence": {"type": "number"},
        "no_final_output": {"type": "boolean"},
        "no_drs_write": {"type": "boolean"},
        "no_action_execution": {"type": "boolean"},
    },
}

PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "proposal_id",
        "created_by",
        "source",
        "source_packet_id",
        "source_gate_decision_id",
        "source_matrix_id",
        "input_is_bounded_attractor_packet",
        "raw_orchestrator_matrix_received",
        "raw_user_intent_received",
        "rejected_matrix_received",
        "plan_graph_present",
        "plan_graph_contract_checked",
        "nodes",
        "edges",
        "forbidden_vectors_absent",
        "downstream_actor_scope",
        "architect_creates_final_output",
        "architect_writes_drs",
        "architect_executes_actions",
    ],
    "properties": {
        "proposal_id": {"type": "string"},
        "created_by": {"type": "string"},
        "source": {"type": "string"},
        "source_packet_id": {"type": "string"},
        "source_gate_decision_id": {"type": "string"},
        "source_matrix_id": {"type": "string"},
        "input_is_bounded_attractor_packet": {"type": "boolean"},
        "raw_orchestrator_matrix_received": {"type": "boolean"},
        "raw_user_intent_received": {"type": "boolean"},
        "rejected_matrix_received": {"type": "boolean"},
        "plan_graph_present": {"type": "boolean"},
        "plan_graph_contract_checked": {"type": "boolean"},
        "nodes": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": [
                    "node_id",
                    "node_kind",
                    "task",
                    "depends_on",
                    "executor",
                    "expected_artifact",
                ],
                "properties": {
                    "node_id": {"type": "string"},
                    "node_kind": {"type": "string"},
                    "task": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                    "executor": {"type": "string"},
                    "expected_artifact": {"type": "string"},
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from", "to"],
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                },
            },
        },
        "forbidden_vectors_absent": {"type": "boolean"},
        "downstream_actor_scope": {"type": "array", "items": {"type": "string"}},
        "architect_creates_final_output": {"type": "boolean"},
        "architect_writes_drs": {"type": "boolean"},
        "architect_executes_actions": {"type": "boolean"},
    },
}


@dataclass(frozen=True)
class LiveDualGeminiFullChainSmokeReport:
    input_live_mode: dict[str, Any]
    live_orchestrator: dict[str, Any]
    root_matrix_gate: dict[str, Any]
    avf_attractor: dict[str, Any]
    live_architect: dict[str, Any]
    deterministic_downstream: dict[str, Any]
    linkage_proof: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _required_list_missing_extra(values: Any, required: set[str]) -> tuple[list[str], list[str]]:
    actual = set(values) if isinstance(values, list) else set()
    return sorted(required - actual), sorted(actual - required)


def _raw_shape_summary(value: Any, required_fields: set[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        keys = sorted(str(key) for key in value)
        return {
            "kind": "object",
            "top_level_keys": keys,
            "missing_required_fields": sorted(required_fields - set(value)),
            "extra_fields": sorted(set(value) - required_fields),
            "field_types": {str(key): type(item).__name__ for key, item in value.items()},
        }
    return {
        "kind": type(value).__name__,
        "top_level_keys": [],
        "missing_required_fields": sorted(required_fields),
        "extra_fields": [],
        "field_types": {},
    }


def _node_diagnostics(plan: Any) -> dict[str, Any]:
    nodes = plan.get("nodes") if isinstance(plan, dict) else None
    if not isinstance(nodes, list):
        return {
            "node_count": 0,
            "first_node_keys": [],
            "nodes_missing_node_id_count": 0,
        }
    return {
        "node_count": len(nodes),
        "first_node_keys": sorted(nodes[0].keys())
        if nodes and isinstance(nodes[0], dict)
        else [],
        "nodes_missing_node_id_count": sum(
            1
            for node in nodes
            if not isinstance(node, dict) or not node.get("node_id")
        ),
    }


def _parse_error_summary(error: Exception) -> dict[str, str]:
    return {
        "error_type": type(error).__name__,
        "message": str(error)[:500].replace("\n", " "),
    }


def _call_pause_seconds() -> float:
    raw = os.environ.get("HEDGEHOG_GEMINI_CALL_PAUSE_SECONDS", "5")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 5.0


def fake_live_orchestrator_matrix(*, matrix_id: str = "live_matrix_certificate") -> dict[str, Any]:
    return {
        "matrix_id": matrix_id,
        "created_by": "live_gemini_orchestrator",
        "source": "live_gemini",
        "task_id": TASK_ID,
        "route_recommendation": "proof_full_pipeline",
        "temporal_query_required": True,
        "drs_scope": "local_only",
        "proposal_only": True,
        "guard_set": sorted(REQUIRED_GUARDS),
        "downstream_actors": sorted(REQUIRED_DOWNSTREAM_ACTORS),
        "candidate_vector_hints": [
            "certificate_workflow_plan",
            "root_controlled_trace_artifact",
        ],
        "forbidden_vector_classes": sorted(REQUIRED_FORBIDDEN_VECTOR_CLASSES),
        "risk_flags": ["no_external_action", "no_drs_writeback"],
        "budget_hints": {"max_nodes": 3, "execution_mode": "deterministic_mock"},
        "confidence": 0.82,
        "no_final_output": True,
        "no_drs_write": True,
        "no_action_execution": True,
    }


def _fallback_orchestrator_matrix() -> dict[str, Any]:
    matrix = fake_live_orchestrator_matrix(matrix_id="fallback_matrix_certificate")
    matrix["created_by"] = "deterministic_fallback_orchestrator"
    matrix["source"] = "deterministic_fallback"
    return matrix


def _validate_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    required = set(MATRIX_SCHEMA["required"])
    missing_fields = sorted(required - set(matrix))
    downstream_missing, downstream_extra = _required_list_missing_extra(
        matrix.get("downstream_actors"), REQUIRED_DOWNSTREAM_ACTORS
    )
    guard_missing, guard_extra = _required_list_missing_extra(
        matrix.get("guard_set"), REQUIRED_GUARDS
    )
    no_final = matrix.get("no_final_output") is True
    no_drs = matrix.get("no_drs_write") is True
    no_action = matrix.get("no_action_execution") is True
    valid = (
        not missing_fields
        and matrix.get("source") == "live_gemini"
        and matrix.get("created_by") == "live_gemini_orchestrator"
        and matrix.get("route_recommendation") == "proof_full_pipeline"
        and matrix.get("temporal_query_required") is True
        and matrix.get("drs_scope") == "local_only"
        and matrix.get("proposal_only") is True
        and not downstream_missing
        and not downstream_extra
        and not guard_missing
        and not guard_extra
        and no_final
        and no_drs
        and no_action
    )
    return {
        "valid": valid,
        "missing_fields": missing_fields,
        "downstream_actors_missing": downstream_missing,
        "downstream_actors_extra": downstream_extra,
        "guard_set_complete": not guard_missing and not guard_extra,
        "no_final_output_claim": no_final,
        "no_drs_write_claim": no_drs,
        "no_action_claim": no_action,
        "errors": [
            key
            for key, ok in {
                "schema_valid": not missing_fields,
                "source": matrix.get("source") == "live_gemini",
                "created_by": matrix.get("created_by")
                == "live_gemini_orchestrator",
                "route_recommendation": matrix.get("route_recommendation")
                == "proof_full_pipeline",
                "temporal_query_required": matrix.get("temporal_query_required")
                is True,
                "drs_scope": matrix.get("drs_scope") == "local_only",
                "proposal_only": matrix.get("proposal_only") is True,
                "downstream_actors_complete": not downstream_missing
                and not downstream_extra,
                "guard_set_complete": not guard_missing and not guard_extra,
                "no_final_output_claim": no_final,
                "no_drs_write_claim": no_drs,
                "no_action_claim": no_action,
            }.items()
            if not ok
        ],
    }


def _gemini_json_call(
    *,
    model: str,
    schema: dict[str, Any],
    prompt: dict[str, Any],
    system_instruction: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    diagnostics = {
        "parse_error": None,
        "raw_shape_summary": _raw_shape_summary({}, set(schema["required"])),
    }
    api_key = _config_value(
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        allow_config=True,
    )
    if not api_key:
        diagnostics["parse_error"] = {
            "error_type": "MissingGeminiConfig",
            "message": "Gemini configuration unavailable",
        }
        return {}, False, diagnostics
    try:
        from google import genai  # type: ignore
    except ImportError as exc:
        diagnostics["parse_error"] = _parse_error_summary(exc)
        return {}, False, diagnostics
    client = genai.Client(api_key=api_key)
    response = None
    base_config = {
        "system_instruction": system_instruction,
        "response_mime_type": "application/json",
    }
    for schema_key in ("response_json_schema", "response_schema"):
        try:
            response = client.models.generate_content(
                model=model,
                contents=json.dumps(prompt, sort_keys=True),
                config={**base_config, schema_key: schema},
            )
            break
        except Exception as exc:
            diagnostics["parse_error"] = _parse_error_summary(exc)
            continue
    if response is None:
        return {}, True, diagnostics
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, dict):
        payload = dict(parsed)
        diagnostics["parse_error"] = None
        diagnostics["raw_shape_summary"] = _raw_shape_summary(
            payload, set(schema["required"])
        )
        return payload, True, diagnostics
    text = getattr(response, "text", "") or ""
    try:
        payload = _extract_json_object(text)
        diagnostics["parse_error"] = None if payload else {
            "error_type": "EmptyJSONPayload",
            "message": "Gemini response did not contain a JSON object",
        }
        diagnostics["raw_shape_summary"] = _raw_shape_summary(
            payload, set(schema["required"])
        )
        return payload, True, diagnostics
    except Exception as exc:
        diagnostics["parse_error"] = _parse_error_summary(exc)
        diagnostics["raw_shape_summary"] = _raw_shape_summary({}, set(schema["required"]))
        return {}, True, diagnostics


def _live_orchestrator_prompt(errors: list[str] | None = None) -> dict[str, Any]:
    prompt: dict[str, Any] = {
        "task": TASK_TEXT,
        "required": {
            "source": "live_gemini",
            "created_by": "live_gemini_orchestrator",
            "route_recommendation": "proof_full_pipeline",
            "temporal_query_required": True,
            "drs_scope": "local_only",
            "proposal_only": True,
            "downstream_actors": sorted(REQUIRED_DOWNSTREAM_ACTORS),
            "guard_set": sorted(REQUIRED_GUARDS),
            "no_final_output": True,
            "no_drs_write": True,
            "no_action_execution": True,
        },
        "return": "strict JSON only; no markdown; no prose",
    }
    if errors:
        prompt["repair_errors"] = errors
    return prompt


def _collect_orchestrator(
    *,
    live_requested: bool,
    live_enabled: bool,
    model: str,
    injected_matrix: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], bool, bool]:
    called = False
    repair_attempted = False
    repair_valid = False
    initial_diagnostics = {
        "parse_error": None,
        "raw_shape_summary": _raw_shape_summary({}, set(MATRIX_SCHEMA["required"])),
    }
    repair_diagnostics = {
        "parse_error": None,
        "raw_shape_summary": _raw_shape_summary({}, set(MATRIX_SCHEMA["required"])),
    }
    repair_validation: dict[str, Any] = {"valid": False, "errors": []}
    if injected_matrix is not None:
        initial = dict(injected_matrix)
        called = False
        initial_diagnostics["raw_shape_summary"] = _raw_shape_summary(
            initial, set(MATRIX_SCHEMA["required"])
        )
    elif live_enabled:
        initial, called, initial_diagnostics = _gemini_json_call(
            model=model,
            schema=MATRIX_SCHEMA,
            prompt=_live_orchestrator_prompt(),
            system_instruction=(
                "You are live Gemini Orchestrator proposal actor only. "
                "You are not Root. Return strict JSON only."
            ),
        )
        if initial:
            initial["source"] = "live_gemini"
            initial["created_by"] = "live_gemini_orchestrator"
    else:
        initial = {}

    initial_validation = _validate_matrix(initial) if initial else {
        "valid": False,
        "errors": ["not_live_not_run"],
        "downstream_actors_missing": sorted(REQUIRED_DOWNSTREAM_ACTORS),
        "downstream_actors_extra": [],
        "guard_set_complete": False,
        "no_final_output_claim": False,
        "no_drs_write_claim": False,
        "no_action_claim": False,
    }
    active = initial
    active_validation = initial_validation
    fallback_used = False

    if live_enabled and not initial_validation["valid"] and injected_matrix is None:
        repair_attempted = True
        repaired, repair_called, repair_diagnostics = _gemini_json_call(
            model=model,
            schema=MATRIX_SCHEMA,
            prompt=_live_orchestrator_prompt(initial_validation["errors"]),
            system_instruction=(
                "Repair the Orchestrator matrix as bounded proposal JSON only. "
                "You are not Root."
            ),
        )
        called = called or repair_called
        if repaired:
            repaired["source"] = "live_gemini"
            repaired["created_by"] = "live_gemini_orchestrator"
        repair_validation = _validate_matrix(repaired) if repaired else {
            **initial_validation,
            "valid": False,
        }
        repair_valid = repair_validation["valid"]
        if repair_valid:
            active = repaired
            active_validation = repair_validation

    if not active_validation["valid"]:
        active = _fallback_orchestrator_matrix()
        active_validation = _validate_matrix(active)
        fallback_used = True

    stage = {
        "orchestrator_source": active.get("source", "none"),
        "orchestrator_initial_valid": initial_validation["valid"],
        "orchestrator_repair_attempted": repair_attempted,
        "orchestrator_repair_valid": repair_valid,
        "orchestrator_fallback_used": fallback_used,
        "orchestrator_matrix_valid": active_validation["valid"],
        "orchestrator_initial_validation_errors": initial_validation["errors"],
        "orchestrator_repair_validation_errors": repair_validation["errors"],
        "orchestrator_initial_parse_error": initial_diagnostics["parse_error"],
        "orchestrator_repair_parse_error": repair_diagnostics["parse_error"],
        "orchestrator_initial_raw_shape_summary": initial_diagnostics[
            "raw_shape_summary"
        ],
        "orchestrator_repair_raw_shape_summary": repair_diagnostics[
            "raw_shape_summary"
        ],
        "matrix_id": active.get("matrix_id"),
        "route_recommendation": active.get("route_recommendation"),
        "temporal_query_required": active.get("temporal_query_required"),
        "drs_scope": active.get("drs_scope"),
        "downstream_actors_missing": active_validation["downstream_actors_missing"],
        "downstream_actors_extra": active_validation["downstream_actors_extra"],
        "guard_set_complete": active_validation["guard_set_complete"],
        "no_final_output_claim": active_validation["no_final_output_claim"],
        "no_drs_write_claim": active_validation["no_drs_write_claim"],
        "no_action_claim": active_validation["no_action_claim"],
    }
    return stage, active, called, fallback_used


def _gate_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    validation = _validate_matrix(matrix)
    if validation["valid"]:
        decision = "accept"
        rejection_reasons: list[str] = []
        downgraded_claims: list[str] = []
    elif matrix.get("source") == "deterministic_fallback":
        decision = "accept"
        rejection_reasons = []
        downgraded_claims = ["fallback_matrix_not_live_success"]
    else:
        decision = "reject"
        rejection_reasons = validation["errors"]
        downgraded_claims = []
    return {
        "source_matrix_id": matrix.get("matrix_id"),
        "gate_decision_id": f"root_gate_decision_{matrix.get('matrix_id', 'missing')}",
        "gate_decision": decision,
        "root_created_gate_decision": True,
        "orchestrator_matrix_is_authority": False,
        "accepted_for_avf": decision in {"accept", "downgrade"},
        "downgraded_claims": downgraded_claims,
        "rejected_before_avf": decision == "reject",
        "rejection_reasons": rejection_reasons,
    }


def _make_attractor_packet(matrix: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    if gate["gate_decision"] == "reject":
        return {
            "source_matrix_id": matrix.get("matrix_id"),
            "source_gate_decision_id": gate["gate_decision_id"],
            "packet_id": None,
            "attractor_packet_created": False,
            "architect_input_bounded": False,
            "hardmask_beats_orchestrator_confidence": True,
            "policy_beats_orchestrator_confidence": True,
            "avf_creates_final_output": False,
            "avf_writes_drs": False,
            "avf_executes_actions": False,
        }
    return {
        "source_matrix_id": matrix["matrix_id"],
        "source_gate_decision_id": gate["gate_decision_id"],
        "packet_id": f"attractor_packet_{matrix['matrix_id']}",
        "attractor_packet_created": True,
        "architect_input_bounded": True,
        "hardmask_beats_orchestrator_confidence": True,
        "policy_beats_orchestrator_confidence": True,
        "candidate_vector_hints_used": list(matrix.get("candidate_vector_hints", [])),
        "forbidden_vector_classes": list(matrix.get("forbidden_vector_classes", [])),
        "risk_flags": list(matrix.get("risk_flags", [])),
        "budget_hints": dict(matrix.get("budget_hints", {})),
        "avf_creates_final_output": False,
        "avf_writes_drs": False,
        "avf_executes_actions": False,
    }


def fake_live_architect_plan(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": f"live_plan_{packet['packet_id']}",
        "created_by": "live_gemini_architect",
        "source": "live_gemini",
        "source_packet_id": packet["packet_id"],
        "source_gate_decision_id": packet["source_gate_decision_id"],
        "source_matrix_id": packet["source_matrix_id"],
        "input_is_bounded_attractor_packet": True,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "rejected_matrix_received": False,
        "plan_graph_present": True,
        "plan_graph_contract_checked": True,
        "nodes": [
            {
                "node_id": "node_collect_requirements",
                "node_kind": "analysis",
                "task": (
                    "Collect certificate workflow requirements from the bounded "
                    "AttractorPacket."
                ),
                "depends_on": [],
                "executor": "deterministic_executor",
                "expected_artifact": "requirements_summary",
            },
            {
                "node_id": "node_build_trace_plan",
                "node_kind": "synthesis",
                "task": (
                    "Build a Root-controlled trace plan from bounded requirements "
                    "without external action or DRS writeback."
                ),
                "depends_on": ["node_collect_requirements"],
                "executor": "deterministic_executor",
                "expected_artifact": "trace_plan_summary",
            },
        ],
        "edges": [
            {
                "from": "node_collect_requirements",
                "to": "node_build_trace_plan",
            }
        ],
        "forbidden_vectors_absent": True,
        "downstream_actor_scope": ["Executor", "Post V&V", "GT", "Root"],
        "architect_creates_final_output": False,
        "architect_writes_drs": False,
        "architect_executes_actions": False,
    }


def _fallback_architect_plan(packet: dict[str, Any]) -> dict[str, Any]:
    plan = fake_live_architect_plan(packet)
    plan["proposal_id"] = f"fallback_plan_{packet['packet_id']}"
    plan["created_by"] = "deterministic_fallback_architect"
    plan["source"] = "deterministic_fallback"
    return plan


def _validate_plan(plan: dict[str, Any], packet: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    required = set(PLAN_SCHEMA["required"])
    missing_fields = sorted(required - set(plan))
    nodes = plan.get("nodes")
    nodes_is_list = isinstance(nodes, list)
    nodes_present = nodes_is_list and bool(nodes)
    node_not_object = nodes_is_list and any(not isinstance(node, dict) for node in nodes)
    node_missing_node_id = nodes_is_list and any(
        not isinstance(node, dict) or not node.get("node_id") for node in nodes
    )
    nodes_contract_valid = nodes_present and not node_not_object and not node_missing_node_id
    valid = (
        not missing_fields
        and plan.get("created_by") == "live_gemini_architect"
        and plan.get("source") == "live_gemini"
        and plan.get("source_packet_id") == packet.get("packet_id")
        and plan.get("source_gate_decision_id") == packet.get("source_gate_decision_id")
        and plan.get("source_matrix_id") == matrix.get("matrix_id")
        and plan.get("input_is_bounded_attractor_packet") is True
        and plan.get("raw_orchestrator_matrix_received") is False
        and plan.get("raw_user_intent_received") is False
        and plan.get("rejected_matrix_received") is False
        and plan.get("plan_graph_present") is True
        and plan.get("plan_graph_contract_checked") is True
        and nodes_contract_valid
        and isinstance(plan.get("edges"), list)
        and plan.get("forbidden_vectors_absent") is True
        and plan.get("architect_creates_final_output") is False
        and plan.get("architect_writes_drs") is False
        and plan.get("architect_executes_actions") is False
    )
    return {
        "valid": valid,
        "errors": [
            key
            for key, ok in {
                "schema_valid": not missing_fields,
                "source_packet_id": plan.get("source_packet_id")
                == packet.get("packet_id"),
                "source_gate_decision_id": plan.get("source_gate_decision_id")
                == packet.get("source_gate_decision_id"),
                "source_matrix_id": plan.get("source_matrix_id")
                == matrix.get("matrix_id"),
                "source": plan.get("source") == "live_gemini",
                "created_by": plan.get("created_by") == "live_gemini_architect",
                "bounded_input": plan.get("input_is_bounded_attractor_packet") is True,
                "no_raw_orchestrator_matrix": plan.get(
                    "raw_orchestrator_matrix_received"
                )
                is False,
                "no_raw_user_intent": plan.get("raw_user_intent_received") is False,
                "contract_valid": plan.get("plan_graph_contract_checked") is True
                and nodes_contract_valid,
                "nodes_list": nodes_is_list,
                "nodes_present": nodes_present,
                "node_not_object": not node_not_object,
                "node_missing_node_id": not node_missing_node_id,
                "no_final_output_claim": plan.get("architect_creates_final_output")
                is False,
                "no_drs_write_claim": plan.get("architect_writes_drs") is False,
                "no_action_claim": plan.get("architect_executes_actions") is False,
            }.items()
            if not ok
        ],
    }


def _live_architect_prompt(packet: dict[str, Any], errors: list[str] | None = None) -> dict[str, Any]:
    prompt: dict[str, Any] = {
        "bounded_attractor_packet_only": packet,
        "format_contract": [
            "Return strict JSON only.",
            "Do not wrap in markdown.",
            "nodes must be a non-empty array.",
            "Every node must be an object with node_id, node_kind, task, depends_on, executor, expected_artifact.",
            "Use at least two nodes: node_collect_requirements and node_build_trace_plan.",
            "Edges must reference existing node_id values only.",
        ],
        "minimal_valid_node_shape_example": {
            "node_id": "node_collect_requirements",
            "node_kind": "analysis",
            "task": "Collect certificate workflow requirements from the bounded AttractorPacket.",
            "depends_on": [],
            "executor": "deterministic_executor",
            "expected_artifact": "requirements_summary",
        },
        "required_edges_example": [
            {
                "from": "node_collect_requirements",
                "to": "node_build_trace_plan",
            }
        ],
        "rules": {
            "created_by": "live_gemini_architect",
            "source": "live_gemini",
            "source_packet_id": packet["packet_id"],
            "source_gate_decision_id": packet["source_gate_decision_id"],
            "source_matrix_id": packet["source_matrix_id"],
            "no_raw_orchestrator_matrix": True,
            "no_raw_user_intent": True,
            "no_final_output": True,
            "no_drs_write": True,
            "no_action_execution": True,
        },
        "return": "strict JSON only; no markdown; no prose",
    }
    if errors:
        prompt["repair_errors"] = errors
        if "nodes_present" in errors or "node_missing_node_id" in errors:
            prompt["repair_instruction"] = (
                "Your previous answer failed because nodes was empty or nodes "
                "lacked node_id. Return the full JSON again with a non-empty "
                "nodes array and every node containing node_id."
            )
    return prompt


def _collect_architect(
    *,
    live_enabled: bool,
    model: str,
    packet: dict[str, Any],
    matrix: dict[str, Any],
    injected_plan: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], bool, bool]:
    if not packet["attractor_packet_created"]:
        return (
            {
                "architect_source": "not_run_rejected_matrix",
                "architect_initial_valid": False,
                "architect_repair_attempted": False,
                "architect_repair_valid": False,
                "architect_fallback_used": False,
                "architect_plan_graph_valid": False,
                "architect_initial_validation_errors": ["attractor_packet_not_created"],
                "architect_repair_validation_errors": [],
                "architect_initial_parse_error": None,
                "architect_repair_parse_error": None,
                "architect_initial_raw_shape_summary": _raw_shape_summary(
                    {}, set(PLAN_SCHEMA["required"])
                ),
                "architect_repair_raw_shape_summary": _raw_shape_summary(
                    {}, set(PLAN_SCHEMA["required"])
                ),
                "architect_initial_node_count": 0,
                "architect_initial_first_node_keys": [],
                "architect_initial_nodes_missing_node_id_count": 0,
                "architect_repair_node_count": 0,
                "architect_repair_first_node_keys": [],
                "architect_repair_nodes_missing_node_id_count": 0,
                "plan_graph_contract_errors": ["attractor_packet_not_created"],
                "proposal_id": None,
                "source_packet_id": None,
                "source_matrix_id": None,
                "plan_graph_present": False,
                "plan_graph_contract_valid": False,
                "input_is_bounded_attractor_packet": False,
                "raw_orchestrator_matrix_received": False,
                "raw_user_intent_received": False,
                "architect_creates_final_output": False,
                "architect_writes_drs": False,
                "architect_executes_actions": False,
            },
            {},
            False,
            False,
        )
    called = False
    repair_attempted = False
    repair_valid = False
    initial_diagnostics = {
        "parse_error": None,
        "raw_shape_summary": _raw_shape_summary({}, set(PLAN_SCHEMA["required"])),
    }
    repair_diagnostics = {
        "parse_error": None,
        "raw_shape_summary": _raw_shape_summary({}, set(PLAN_SCHEMA["required"])),
    }
    repair_validation: dict[str, Any] = {"valid": False, "errors": []}
    if injected_plan is not None:
        initial = dict(injected_plan)
        initial_diagnostics["raw_shape_summary"] = _raw_shape_summary(
            initial, set(PLAN_SCHEMA["required"])
        )
    elif live_enabled:
        initial, called, initial_diagnostics = _gemini_json_call(
            model=model,
            schema=PLAN_SCHEMA,
            prompt=_live_architect_prompt(packet),
            system_instruction=(
                "You are live Gemini Architect proposal role only. You are not "
                "Root. Return strict JSON PlanGraph proposal only."
            ),
        )
        if initial:
            initial["source"] = "live_gemini"
            initial["created_by"] = "live_gemini_architect"
            initial.setdefault("source_packet_id", packet["packet_id"])
            initial.setdefault("source_gate_decision_id", packet["source_gate_decision_id"])
            initial.setdefault("source_matrix_id", packet["source_matrix_id"])
    else:
        initial = {}

    initial_validation = _validate_plan(initial, packet, matrix) if initial else {
        "valid": False,
        "errors": ["not_live_not_run"],
    }
    initial_node_diagnostics = _node_diagnostics(initial)
    active = initial
    active_validation = initial_validation
    fallback_used = False
    repair_node_diagnostics = _node_diagnostics({})

    if live_enabled and not initial_validation["valid"] and injected_plan is None:
        repair_attempted = True
        repaired, repair_called, repair_diagnostics = _gemini_json_call(
            model=model,
            schema=PLAN_SCHEMA,
            prompt=_live_architect_prompt(packet, initial_validation["errors"]),
            system_instruction=(
                "Repair the Architect PlanGraph proposal as bounded JSON only. "
                "You are not Root."
            ),
        )
        called = called or repair_called
        if repaired:
            repaired["source"] = "live_gemini"
            repaired["created_by"] = "live_gemini_architect"
            repaired.setdefault("source_packet_id", packet["packet_id"])
            repaired.setdefault("source_gate_decision_id", packet["source_gate_decision_id"])
            repaired.setdefault("source_matrix_id", packet["source_matrix_id"])
        repair_validation = _validate_plan(repaired, packet, matrix) if repaired else {
            **initial_validation,
            "valid": False,
        }
        repair_node_diagnostics = _node_diagnostics(repaired)
        repair_valid = repair_validation["valid"]
        if repair_valid:
            active = repaired
            active_validation = repair_validation

    if not active_validation["valid"]:
        active = _fallback_architect_plan(packet)
        active_validation = _validate_plan(active, packet, matrix)
        fallback_used = True

    stage = {
        "architect_source": active.get("source", "none"),
        "architect_initial_valid": initial_validation["valid"],
        "architect_repair_attempted": repair_attempted,
        "architect_repair_valid": repair_valid,
        "architect_fallback_used": fallback_used,
        "architect_plan_graph_valid": active_validation["valid"],
        "architect_initial_validation_errors": initial_validation["errors"],
        "architect_repair_validation_errors": repair_validation["errors"],
        "architect_initial_parse_error": initial_diagnostics["parse_error"],
        "architect_repair_parse_error": repair_diagnostics["parse_error"],
        "architect_initial_raw_shape_summary": initial_diagnostics[
            "raw_shape_summary"
        ],
        "architect_repair_raw_shape_summary": repair_diagnostics[
            "raw_shape_summary"
        ],
        "architect_initial_node_count": initial_node_diagnostics["node_count"],
        "architect_initial_first_node_keys": initial_node_diagnostics[
            "first_node_keys"
        ],
        "architect_initial_nodes_missing_node_id_count": initial_node_diagnostics[
            "nodes_missing_node_id_count"
        ],
        "architect_repair_node_count": repair_node_diagnostics["node_count"],
        "architect_repair_first_node_keys": repair_node_diagnostics[
            "first_node_keys"
        ],
        "architect_repair_nodes_missing_node_id_count": repair_node_diagnostics[
            "nodes_missing_node_id_count"
        ],
        "plan_graph_contract_errors": sorted(
            set(initial_validation["errors"]) | set(repair_validation["errors"])
        )
        if fallback_used
        else active_validation["errors"],
        "proposal_id": active.get("proposal_id"),
        "source_packet_id": active.get("source_packet_id"),
        "source_matrix_id": active.get("source_matrix_id"),
        "plan_graph_present": active.get("plan_graph_present") is True,
        "plan_graph_contract_valid": active_validation["valid"],
        "input_is_bounded_attractor_packet": active.get(
            "input_is_bounded_attractor_packet"
        )
        is True,
        "raw_orchestrator_matrix_received": active.get(
            "raw_orchestrator_matrix_received"
        )
        is True,
        "raw_user_intent_received": active.get("raw_user_intent_received") is True,
        "architect_creates_final_output": active.get(
            "architect_creates_final_output"
        )
        is True,
        "architect_writes_drs": active.get("architect_writes_drs") is True,
        "architect_executes_actions": active.get("architect_executes_actions") is True,
    }
    return stage, active, called, fallback_used


def _result_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    safe_nodes = [
        node
        for node in plan.get("nodes", [])
        if isinstance(node, dict) and node.get("node_id")
    ]
    malformed_node_count = len(plan.get("nodes", [])) - len(safe_nodes)
    return {
        "result_proposal_id": f"result_from_{plan['proposal_id']}",
        "created_by": "executor",
        "source_plan_graph_proposal_id": plan["proposal_id"],
        "source_packet_id": plan["source_packet_id"],
        "source_gate_decision_id": plan["source_gate_decision_id"],
        "source_matrix_id": plan["source_matrix_id"],
        "node_results": [
            {
                "node_id": node["node_id"],
                "status": "completed",
                "real_external_action_executed": False,
                "final_output_created": False,
                "drs_written": False,
            }
            for node in safe_nodes
        ],
        "execution_mode": "deterministic_mock",
        "result_status": "blocked" if malformed_node_count else "completed",
        "evidence": ["live_architect_plan_graph_consumed"],
        "risks": ["malformed_plan_node_blocked"] if malformed_node_count else [],
        "executor_creates_final_output": False,
        "executor_writes_drs": False,
        "executor_executes_real_action": False,
    }


def _validation_from_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "validation_report_id": f"validation_from_{result['result_proposal_id']}",
        "created_by": "post_vv",
        "source_result_proposal_id": result["result_proposal_id"],
        "source_plan_graph_proposal_id": result["source_plan_graph_proposal_id"],
        "source_packet_id": result["source_packet_id"],
        "source_matrix_id": result["source_matrix_id"],
        "validation_status": "accepted",
        "validation_findings": ["result_proposal_shape_valid"],
        "validation_risks": [],
        "post_vv_creates_final_output": False,
        "post_vv_writes_drs": False,
        "post_vv_executes_actions": False,
    }


def _gt_from_validation(validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "gt_decision_id": f"gt_from_{validation['validation_report_id']}",
        "created_by": "gt_validator",
        "source_validation_report_id": validation["validation_report_id"],
        "source_result_proposal_id": validation["source_result_proposal_id"],
        "gt_decision": "accept",
        "selection_reason": "validation_report_accepted",
        "gt_creates_final_output": False,
        "gt_writes_drs": False,
        "gt_executes_actions": False,
    }


def _root_final_from_gt(gt_decision: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "root_final_artifact_id": f"root_final_from_{gt_decision['gt_decision_id']}",
        "created_by": "root_orchestrator",
        "source_gt_decision_id": gt_decision["gt_decision_id"],
        "source_validation_report_id": validation["validation_report_id"],
        "source_result_proposal_id": validation["source_result_proposal_id"],
        "root_final_status": "accepted",
        "root_created_final_output": True,
        "gt_created_final_output": False,
        "root_writes_drs": False,
        "drs_writeback_invoked": False,
        "root_executes_actions": False,
        "production_external_action_executed": False,
        "production_persistence_claimed": False,
    }


def _downstream(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    result = _result_from_plan(plan)
    validation = _validation_from_result(result)
    gt_decision = _gt_from_validation(validation)
    root_final = _root_final_from_gt(gt_decision, validation)
    section = {
        "result_proposal_id": result["result_proposal_id"],
        "validation_report_id": validation["validation_report_id"],
        "gt_decision_id": gt_decision["gt_decision_id"],
        "root_final_artifact_id": root_final["root_final_artifact_id"],
        "executor_status": result["result_status"],
        "validation_status": validation["validation_status"],
        "gt_decision": gt_decision["gt_decision"],
        "root_final_status": root_final["root_final_status"],
        "root_created_final_output": root_final["root_created_final_output"],
        "root_is_only_final_output_authority": True,
        "drs_writeback_invoked": False,
        "production_persistence_claimed": False,
        "production_external_action_executed": False,
    }
    return section, result, validation, gt_decision, root_final


def _linkage(
    matrix: dict[str, Any],
    gate: dict[str, Any],
    packet: dict[str, Any],
    plan: dict[str, Any],
    result: dict[str, Any],
    validation: dict[str, Any],
    gt_decision: dict[str, Any],
    root_final: dict[str, Any],
) -> dict[str, Any]:
    active_links = {
        "gate_uses_active_matrix": gate["source_matrix_id"] == matrix.get("matrix_id"),
        "packet_uses_gate_decision": (
            packet["source_matrix_id"] == matrix.get("matrix_id")
            and packet["source_gate_decision_id"] == gate["gate_decision_id"]
        ),
        "architect_uses_packet": (
            plan.get("source_packet_id") == packet.get("packet_id")
            and plan.get("source_matrix_id") == matrix.get("matrix_id")
        ),
        "result_uses_active_architect_plan": result.get(
            "source_plan_graph_proposal_id"
        )
        == plan.get("proposal_id"),
        "validation_uses_result": validation.get("source_result_proposal_id")
        == result.get("result_proposal_id"),
        "gt_uses_validation": gt_decision.get("source_validation_report_id")
        == validation.get("validation_report_id"),
        "root_final_uses_gt": root_final.get("source_gt_decision_id")
        == gt_decision.get("gt_decision_id"),
    }
    proof = {
        "gate_uses_live_matrix": active_links["gate_uses_active_matrix"]
        and matrix.get("source") == "live_gemini",
        "packet_uses_gate_decision": active_links["packet_uses_gate_decision"],
        "architect_uses_packet": active_links["architect_uses_packet"],
        "result_uses_live_architect_plan": active_links[
            "result_uses_active_architect_plan"
        ]
        and plan.get("source") == "live_gemini",
        "validation_uses_result": active_links["validation_uses_result"],
        "gt_uses_validation": active_links["gt_uses_validation"],
        "root_final_uses_gt": active_links["root_final_uses_gt"],
        "gate_uses_active_matrix": active_links["gate_uses_active_matrix"],
        "result_uses_active_architect_plan": active_links[
            "result_uses_active_architect_plan"
        ],
        "active_artifacts_linked": all(active_links.values()),
    }
    required_live_links = (
        "gate_uses_live_matrix",
        "packet_uses_gate_decision",
        "architect_uses_packet",
        "result_uses_live_architect_plan",
        "validation_uses_result",
        "gt_uses_validation",
        "root_final_uses_gt",
    )
    proof["one_continuous_chain"] = all(proof[key] for key in required_live_links)
    return proof


def _authority(
    orchestrator: dict[str, Any],
    architect: dict[str, Any],
    downstream: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gemini_authority_granted": False,
        "live_orchestrator_created_final_output": not orchestrator[
            "no_final_output_claim"
        ],
        "live_architect_created_final_output": architect[
            "architect_creates_final_output"
        ],
        "executor_created_final_output": False,
        "post_vv_created_final_output": False,
        "gt_created_final_output": False,
        "root_created_final_output": downstream["root_created_final_output"],
        "root_is_only_final_output_authority": downstream[
            "root_is_only_final_output_authority"
        ],
        "gemini_wrote_drs": (not orchestrator["no_drs_write_claim"])
        or architect["architect_writes_drs"],
        "executor_wrote_drs": False,
        "post_vv_wrote_drs": False,
        "gt_wrote_drs": False,
        "root_wrote_drs": False,
        "drs_writeback_invoked": downstream["drs_writeback_invoked"],
        "gemini_executed_action": (not orchestrator["no_action_claim"])
        or architect["architect_executes_actions"],
        "production_external_action_executed": downstream[
            "production_external_action_executed"
        ],
        "live_telegram_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _input(
    *,
    live_requested: bool,
    live_env_allowed: bool,
    model: str,
    pause: float,
    network_required: bool,
) -> dict[str, Any]:
    return {
        "live_requested": live_requested,
        "live_env_allowed": live_env_allowed,
        "gemini_model": model,
        "gemini_call_pause_seconds": pause,
        "network_required": network_required,
        "telegram_used": False,
        "real_external_action": False,
    }


def _summary(
    *,
    live_requested: bool,
    live_enabled: bool,
    orchestrator: dict[str, Any],
    architect: dict[str, Any],
    linkage: dict[str, Any],
    authority: dict[str, Any],
    root_final_reached: bool,
) -> dict[str, Any]:
    orchestrator_live_no_fallback = (
        orchestrator["orchestrator_source"] == "live_gemini"
        and orchestrator["orchestrator_matrix_valid"]
        and not orchestrator["orchestrator_fallback_used"]
    )
    architect_live_no_fallback = (
        architect["architect_source"] == "live_gemini"
        and architect["architect_plan_graph_valid"]
        and not architect["architect_fallback_used"]
    )
    both_live = orchestrator_live_no_fallback and architect_live_no_fallback
    boundaries_safe = (
        not authority["gemini_authority_granted"]
        and not authority["live_orchestrator_created_final_output"]
        and not authority["live_architect_created_final_output"]
        and not authority["executor_created_final_output"]
        and not authority["post_vv_created_final_output"]
        and not authority["gt_created_final_output"]
        and authority["root_created_final_output"]
        and authority["root_is_only_final_output_authority"]
        and not authority["gemini_wrote_drs"]
        and not authority["drs_writeback_invoked"]
        and not authority["gemini_executed_action"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
    )
    fallback_used = (
        orchestrator["orchestrator_fallback_used"]
        or architect["architect_fallback_used"]
    )
    if not live_requested or not live_enabled:
        status = "NOT_LIVE_NOT_RUN"
    elif both_live and linkage["one_continuous_chain"] and root_final_reached and boundaries_safe:
        status = "PASS"
    elif fallback_used and linkage["active_artifacts_linked"] and boundaries_safe:
        status = "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    else:
        status = "FAIL"
    return {
        "live_dual_gemini_full_chain_smoke_status": status,
        "both_gemini_roles_live": both_live,
        "orchestrator_live_no_fallback": orchestrator_live_no_fallback,
        "architect_live_no_fallback": architect_live_no_fallback,
        "one_continuous_chain": linkage["one_continuous_chain"],
        "root_final_reached": root_final_reached,
        "root_is_only_final_output_authority": authority[
            "root_is_only_final_output_authority"
        ],
        "drs_writeback_invoked": authority["drs_writeback_invoked"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_persistence_claimed": False,
        "production_autonomy_claimed": False,
    }


def collect_live_dual_gemini_full_chain_smoke(
    *,
    live_requested: bool = False,
    injected_orchestrator_matrix: dict[str, Any] | None = None,
    injected_architect_plan: dict[str, Any] | None = None,
    break_linkage: bool = False,
) -> LiveDualGeminiFullChainSmokeReport:
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    pause = _call_pause_seconds()
    live_env_allowed = os.environ.get("HEDGEHOG_ALLOW_LIVE_GEMINI") == "1"
    injection_mode = (
        injected_orchestrator_matrix is not None or injected_architect_plan is not None
    )
    live_enabled = live_requested and (live_env_allowed or injection_mode)
    network_required = live_requested and live_env_allowed and not injection_mode
    input_fields = _input(
        live_requested=live_requested,
        live_env_allowed=live_env_allowed,
        model=model,
        pause=pause,
        network_required=network_required,
    )

    if not live_requested or not live_enabled:
        empty = {
            "orchestrator_source": "not_run",
            "orchestrator_initial_valid": False,
            "orchestrator_repair_attempted": False,
            "orchestrator_repair_valid": False,
            "orchestrator_fallback_used": False,
            "orchestrator_matrix_valid": False,
            "orchestrator_initial_validation_errors": ["not_live_not_run"],
            "orchestrator_repair_validation_errors": [],
            "orchestrator_initial_parse_error": None,
            "orchestrator_repair_parse_error": None,
            "orchestrator_initial_raw_shape_summary": _raw_shape_summary(
                {}, set(MATRIX_SCHEMA["required"])
            ),
            "orchestrator_repair_raw_shape_summary": _raw_shape_summary(
                {}, set(MATRIX_SCHEMA["required"])
            ),
            "matrix_id": None,
            "route_recommendation": None,
            "temporal_query_required": False,
            "drs_scope": None,
            "downstream_actors_missing": sorted(REQUIRED_DOWNSTREAM_ACTORS),
            "downstream_actors_extra": [],
            "guard_set_complete": False,
            "no_final_output_claim": True,
            "no_drs_write_claim": True,
            "no_action_claim": True,
        }
        gate = {
            "source_matrix_id": None,
            "gate_decision_id": None,
            "gate_decision": "not_run",
            "root_created_gate_decision": False,
            "orchestrator_matrix_is_authority": False,
            "accepted_for_avf": False,
            "downgraded_claims": [],
            "rejected_before_avf": True,
        }
        packet = {
            "source_matrix_id": None,
            "source_gate_decision_id": None,
            "packet_id": None,
            "attractor_packet_created": False,
            "architect_input_bounded": False,
            "hardmask_beats_orchestrator_confidence": True,
            "policy_beats_orchestrator_confidence": True,
            "avf_creates_final_output": False,
            "avf_writes_drs": False,
            "avf_executes_actions": False,
        }
        architect = {
            "architect_source": "not_run",
            "architect_initial_valid": False,
            "architect_repair_attempted": False,
            "architect_repair_valid": False,
            "architect_fallback_used": False,
            "architect_plan_graph_valid": False,
            "architect_initial_validation_errors": ["not_live_not_run"],
            "architect_repair_validation_errors": [],
            "architect_initial_parse_error": None,
            "architect_repair_parse_error": None,
            "architect_initial_raw_shape_summary": _raw_shape_summary(
                {}, set(PLAN_SCHEMA["required"])
            ),
            "architect_repair_raw_shape_summary": _raw_shape_summary(
                {}, set(PLAN_SCHEMA["required"])
            ),
            "architect_initial_node_count": 0,
            "architect_initial_first_node_keys": [],
            "architect_initial_nodes_missing_node_id_count": 0,
            "architect_repair_node_count": 0,
            "architect_repair_first_node_keys": [],
            "architect_repair_nodes_missing_node_id_count": 0,
            "plan_graph_contract_errors": ["not_live_not_run"],
            "proposal_id": None,
            "source_packet_id": None,
            "source_matrix_id": None,
            "plan_graph_present": False,
            "plan_graph_contract_valid": False,
            "input_is_bounded_attractor_packet": False,
            "raw_orchestrator_matrix_received": False,
            "raw_user_intent_received": False,
            "architect_creates_final_output": False,
            "architect_writes_drs": False,
            "architect_executes_actions": False,
        }
        downstream = {
            "result_proposal_id": None,
            "validation_report_id": None,
            "gt_decision_id": None,
            "root_final_artifact_id": None,
            "executor_status": "not_run",
            "validation_status": "not_run",
            "gt_decision": "not_run",
            "root_final_status": "not_run",
            "root_created_final_output": False,
            "root_is_only_final_output_authority": True,
            "drs_writeback_invoked": False,
            "production_persistence_claimed": False,
            "production_external_action_executed": False,
        }
        linkage = {
            "gate_uses_live_matrix": False,
            "packet_uses_gate_decision": False,
            "architect_uses_packet": False,
            "result_uses_live_architect_plan": False,
            "validation_uses_result": False,
            "gt_uses_validation": False,
            "root_final_uses_gt": False,
            "one_continuous_chain": False,
        }
        authority = _authority(empty, architect, downstream)
        summary = _summary(
            live_requested=live_requested,
            live_enabled=live_enabled,
            orchestrator=empty,
            architect=architect,
            linkage=linkage,
            authority=authority,
            root_final_reached=False,
        )
        return LiveDualGeminiFullChainSmokeReport(
            input_live_mode=input_fields,
            live_orchestrator=empty,
            root_matrix_gate=gate,
            avf_attractor=packet,
            live_architect=architect,
            deterministic_downstream=downstream,
            linkage_proof=linkage,
            authority_safety=authority,
            summary=summary,
        )

    orchestrator, matrix, _, orch_fallback = _collect_orchestrator(
        live_requested=live_requested,
        live_enabled=live_enabled,
        model=model,
        injected_matrix=injected_orchestrator_matrix,
    )
    gate = _gate_matrix(matrix)
    packet = _make_attractor_packet(matrix, gate)
    if network_required and pause:
        time.sleep(pause)
    architect, plan, _, arch_fallback = _collect_architect(
        live_enabled=live_enabled,
        model=model,
        packet=packet,
        matrix=matrix,
        injected_plan=injected_architect_plan,
    )
    downstream, result, validation, gt_decision, root_final = _downstream(plan)
    if break_linkage:
        result["source_plan_graph_proposal_id"] = "broken_plan_ref"
    linkage = _linkage(
        matrix,
        gate,
        packet,
        plan,
        result,
        validation,
        gt_decision,
        root_final,
    )
    authority = _authority(orchestrator, architect, downstream)
    summary = _summary(
        live_requested=live_requested,
        live_enabled=live_enabled,
        orchestrator=orchestrator,
        architect=architect,
        linkage=linkage,
        authority=authority,
        root_final_reached=bool(root_final.get("root_final_artifact_id")),
    )
    return LiveDualGeminiFullChainSmokeReport(
        input_live_mode=input_fields,
        live_orchestrator=orchestrator,
        root_matrix_gate=gate,
        avf_attractor=packet,
        live_architect=architect,
        deterministic_downstream=downstream,
        linkage_proof=linkage,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_live_dual_gemini_full_chain_smoke(
    report: LiveDualGeminiFullChainSmokeReport,
) -> str:
    lines = ["[LIVE DUAL-GEMINI FULL CHAIN SMOKE]"]
    _section(lines, "[INPUT]", report.input_live_mode)
    _section(lines, "[LIVE ORCHESTRATOR]", report.live_orchestrator)
    _section(lines, "[ROOT MATRIX GATE]", report.root_matrix_gate)
    _section(lines, "[AVF ATTRACTOR]", report.avf_attractor)
    _section(lines, "[LIVE ARCHITECT]", report.live_architect)
    _section(lines, "[DETERMINISTIC DOWNSTREAM]", report.deterministic_downstream)
    _section(lines, "[LINKAGE PROOF]", report.linkage_proof)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines)


def run_live_dual_gemini_full_chain_smoke(*, live_requested: bool = False) -> str:
    return render_live_dual_gemini_full_chain_smoke(
        collect_live_dual_gemini_full_chain_smoke(live_requested=live_requested)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run live dual-Gemini full chain smoke.")
    parser.add_argument("--live", action="store_true", help="Opt into live Gemini calls.")
    args = parser.parse_args()
    print(run_live_dual_gemini_full_chain_smoke(live_requested=args.live))


if __name__ == "__main__":
    main()
