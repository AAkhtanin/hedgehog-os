from __future__ import annotations

from hedgehog.time_model import make_time_envelope


def execute_node(
    plan_graph: dict, node: dict, session_anchor: str = "demo_session"
) -> dict:
    plan_id = plan_graph["plan_id"]
    node_id = node["node_id"]
    proposal = {
        "proposal_id": f"rp:{plan_id}:{node_id}",
        "producer": {
            "executor_id": node["executor_id"],
            "model_id": "stub_executor_v1",
        },
        "vector_id": node["vector_id"],
        "plan_id": plan_id,
        "result_payload": {
            "status": "simulated_success",
            "node_id": node_id,
            "task_completed": True,
            "simulated_artifact": "mock_certificate_step_result",
        },
        "evidence": [
            {
                "kind": "simulated_executor",
                "summary": "Executed deterministic mock certificate step.",
                "ref_id": node_id,
                "confidence": 1.0,
            }
        ],
        "cost": {
            "tokens": 0,
            "walltime_ms": 0,
            "toolcalls": 0,
        },
        "risks": [],
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
