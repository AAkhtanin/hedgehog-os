from __future__ import annotations


EXECUTOR_ID = "exec_mock_certificate"


def make_plan_graph(attractor_packet: dict) -> dict:
    packet_id = attractor_packet["packet_id"]
    request_id = attractor_packet.get("request_id")
    time_context = attractor_packet["time_context"]
    candidate_vectors = attractor_packet["candidate_vectors"]
    if not candidate_vectors:
        raise ValueError("AttractorPacket must contain candidate_vectors")

    nodes = []
    for index, vector in enumerate(candidate_vectors, start=1):
        vector_id = vector["vector_id"]
        nodes.append(
            {
                "node_id": f"node:{packet_id}:{index}",
                "vector_id": vector_id,
                "kind": "tool_or_simulated_action",
                "task": f"simulate_result_proposal_for_vector:{vector_id}",
                "executor_id": EXECUTOR_ID,
                "depends_on": [],
                "expected_output": "result_proposal",
                "branching_mode": vector["branching_mode"],
            }
        )

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
        "edges": [],
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
