from __future__ import annotations


EXECUTOR_ID = "exec_mock_certificate"


BRANCH_STEPS = {
    "official_online_request": [
        "prepare_request_payload",
        "validate_required_fields",
        "simulate_submission_step",
    ],
    "personal_visit": [
        "prepare_visit_checklist",
        "estimate_visit_requirements",
    ],
    "legal_representative": [
        "prepare_delegation_requirements",
        "validate_authorization_constraints",
    ],
    "fallback_exploration": [
        "gather_missing_requirements",
        "propose_human_review_questions",
    ],
}


def _branch_steps_for_vector(vector_id: str) -> list[str]:
    return BRANCH_STEPS.get(vector_id, ["simulate_result_proposal_for_vector"])


def _kind_for_step(step: str) -> str:
    if step.startswith("validate_"):
        return "validation"
    if step.startswith("gather_"):
        return "retrieval"
    if "human_review" in step:
        return "human_clarification"
    return "tool_or_simulated_action"


def _node_task(step: str, vector_id: str, final_viability: float, soft_mask: float) -> str:
    return (
        f"{step}:{vector_id};"
        f"avf_final_viability={final_viability};"
        f"avf_soft_mask={soft_mask}"
    )


def make_plan_graph(attractor_packet: dict) -> dict:
    packet_id = attractor_packet["packet_id"]
    request_id = attractor_packet.get("request_id")
    time_context = attractor_packet["time_context"]
    candidate_vectors = attractor_packet["candidate_vectors"]
    if not candidate_vectors:
        raise ValueError("AttractorPacket must contain candidate_vectors")

    nodes = []
    edges = []
    for index, vector in enumerate(candidate_vectors, start=1):
        vector_id = vector["vector_id"]
        final_viability = vector["final_viability"]
        soft_mask = vector["soft_mask"]
        previous_node_id = None
        for step_index, step in enumerate(_branch_steps_for_vector(vector_id), start=1):
            node_id = f"node:{packet_id}:{index}:{step_index}:{step}"
            depends_on = [previous_node_id] if previous_node_id is not None else []
            nodes.append(
                {
                    "node_id": node_id,
                    "vector_id": vector_id,
                    "kind": _kind_for_step(step),
                    "task": _node_task(
                        step=step,
                        vector_id=vector_id,
                        final_viability=final_viability,
                        soft_mask=soft_mask,
                    ),
                    "executor_id": EXECUTOR_ID,
                    "depends_on": depends_on,
                    "expected_output": "result_proposal",
                    "branching_mode": vector["branching_mode"],
                }
            )
            if previous_node_id is not None:
                edges.append({"from": previous_node_id, "to": node_id})
            previous_node_id = node_id

    plan_graph = {
        "plan_id": f"plan:{packet_id}",
        "source_packet_id": packet_id,
        "time_assumptions": {
            "as_of": time_context["as_of"],
            "freshness_required": time_context["freshness_required"],
            "assumptions": [
                "executor outputs must be ResultProposal objects",
                "candidate vectors were pre-filtered by AVF",
            ],
        },
        "nodes": nodes,
        "edges": edges,
        "executor_assignments": [
            {
                "executor_id": EXECUTOR_ID,
                "node_ids": [node["node_id"] for node in nodes],
                "mode": "simulate",
            }
        ],
    }
    if request_id is not None:
        plan_graph["request_id"] = request_id
    return plan_graph
