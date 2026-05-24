from __future__ import annotations

from hedgehog.time_model import make_time_envelope


def _task_prefix(task: str) -> str:
    return task.split(";", 1)[0].split(":", 1)[0]


def _parse_avf_from_task(task: str) -> dict:
    metadata = {}
    for part in task.split(";")[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        metadata[key] = value
    return {
        "final_viability": float(metadata.get("avf_final_viability", 0.0)),
        "soft_mask": float(metadata.get("avf_soft_mask", 0.0)),
    }


def _avf_payload(node: dict, task: str) -> dict:
    avf = _parse_avf_from_task(task)
    return {
        "final_viability": avf["final_viability"],
        "soft_mask": avf["soft_mask"],
        "vector_id": node["vector_id"],
    }


def _base_payload(node: dict, task: str) -> dict:
    return {
        "status": "simulated_success",
        "node_id": node["node_id"],
        "task_completed": True,
        "artifact_type": "generic_simulated_result",
        "avf": _avf_payload(node, task),
    }


def _result_payload_for_task(node: dict) -> dict:
    task = node["task"]
    prefix = _task_prefix(task)
    payload = _base_payload(node, task)

    if prefix == "prepare_request_payload":
        payload.update(
            {
                "artifact_type": "request_payload",
                "payload_fields": [
                    "applicant_identity_pointer",
                    "service_type",
                    "delivery_preference",
                ],
                "next_requirement": "validate_required_fields",
            }
        )
    elif prefix == "validate_required_fields":
        payload.update(
            {
                "artifact_type": "field_validation",
                "validated_fields": ["service_type", "delivery_preference"],
                "missing_fields": ["applicant_identity_pointer"],
                "requires_human_input": True,
            }
        )
    elif prefix == "simulate_submission_step":
        payload.update(
            {
                "status": "needs_user",
                "task_completed": False,
                "artifact_type": "submission_simulation",
                "blocked_reason": "missing_human_identity_confirmation",
                "requires_human_input": True,
            }
        )
    elif prefix == "prepare_visit_checklist":
        payload.update(
            {
                "artifact_type": "visit_checklist",
                "checklist_items": [
                    "confirm service office",
                    "prepare identity pointer",
                    "bring mock application reference",
                ],
            }
        )
    elif prefix == "estimate_visit_requirements":
        payload.update(
            {
                "artifact_type": "visit_estimate",
                "estimated_time_minutes": 90,
                "requirements": [
                    "appointment window",
                    "identity confirmation",
                    "service fee check",
                ],
            }
        )
    elif prefix == "prepare_delegation_requirements":
        payload.update(
            {
                "artifact_type": "delegation_requirements",
                "required_documents": [
                    "authorization letter",
                    "representative identity pointer",
                    "applicant identity pointer",
                ],
            }
        )
    elif prefix == "validate_authorization_constraints":
        payload.update(
            {
                "artifact_type": "authorization_validation",
                "constraints_checked": [
                    "representative authority",
                    "scope of delegation",
                    "human consent required",
                ],
                "requires_human_input": True,
            }
        )
    elif prefix == "gather_missing_requirements":
        payload.update(
            {
                "artifact_type": "missing_requirements_research",
                "open_questions": [
                    "Which certificate subtype is needed?",
                    "Is delivery online or in-person?",
                    "Is identity confirmation available?",
                ],
            }
        )
    elif prefix == "propose_human_review_questions":
        payload.update(
            {
                "artifact_type": "human_review_questions",
                "questions": [
                    "Confirm certificate subtype.",
                    "Confirm preferred delivery channel.",
                    "Confirm whether identity data may be used from a secure pointer.",
                ],
            }
        )

    return payload


def _risks_for_task(prefix: str) -> list[dict]:
    if prefix != "simulate_submission_step":
        return []
    return [
        {
            "risk_id": "risk:human_confirmation_required",
            "severity": "low",
            "description": "Submission cannot proceed without human confirmation.",
        }
    ]


def execute_node(
    plan_graph: dict, node: dict, session_anchor: str = "demo_session"
) -> dict:
    plan_id = plan_graph["plan_id"]
    node_id = node["node_id"]
    task_prefix = _task_prefix(node["task"])
    proposal = {
        "proposal_id": f"rp:{plan_id}:{node_id}",
        "producer": {
            "executor_id": node["executor_id"],
            "model_id": "stub_executor_v1",
        },
        "vector_id": node["vector_id"],
        "plan_id": plan_id,
        "result_payload": _result_payload_for_task(node),
        "evidence": [
            {
                "kind": "simulated_executor",
                "summary": f"Executed deterministic mock certificate step: {task_prefix}.",
                "ref_id": node_id,
                "confidence": 1.0,
            }
        ],
        "cost": {
            "tokens": 0,
            "walltime_ms": 0,
            "toolcalls": 0,
        },
        "risks": _risks_for_task(task_prefix),
        "time_envelope": make_time_envelope(session_anchor),
        "trace_refs": [
            {
                "trace_id": f"trace:{plan_id}",
                "span_id": node_id,
                "kind": "executor_node",
            }
        ],
    }
    if "request_id" in plan_graph:
        proposal["request_id"] = plan_graph["request_id"]
    return proposal


def execute_plan_graph(plan_graph: dict, session_anchor: str = "demo_session") -> list[dict]:
    nodes = plan_graph["nodes"]
    if not nodes:
        raise ValueError("PlanGraph must contain nodes")
    return [
        execute_node(plan_graph, node, session_anchor=session_anchor)
        for node in nodes
    ]
