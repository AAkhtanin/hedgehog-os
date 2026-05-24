from __future__ import annotations

import json


ARCHITECT_SYSTEM_PROMPT = """You are a subordinate Architect inside Hedgehog OS.
You are not the RootOrchestrator.
You do not answer the user.
You do not create FinalOutput.
You receive an AttractorPacket.
You must return only valid PlanGraph JSON.
Do not include markdown.
Do not include explanations outside JSON.
Do not invent candidate vectors that are not in the AttractorPacket.
Do not use forbidden vectors.
Every PlanGraph node must reference an allowed vector_id from the AttractorPacket.
Respect branch_budget, dependencies, time_assumptions, and executor assignment.
If a candidate is insufficient, create a conservative needs_user or validation node rather than inventing external facts."""


def compile_architect_prompt(attractor_packet: dict) -> dict:
    candidate_vectors = attractor_packet.get("candidate_vectors", [])
    allowed_vector_ids = [vector["vector_id"] for vector in candidate_vectors]
    compact_packet = json.dumps(
        attractor_packet,
        sort_keys=True,
        separators=(",", ":"),
    )
    goal = attractor_packet.get("goal", {})
    metadata = {
        "request_id": attractor_packet.get("request_id"),
        "intent_id": attractor_packet.get("intent_id"),
        "goal_id": goal.get("goal_id"),
        "allowed_vector_ids": allowed_vector_ids,
    }
    user_prompt = (
        "Return PlanGraph JSON only. Do not include markdown or prose.\n"
        f"Planner metadata: {json.dumps(metadata, sort_keys=True, separators=(',', ':'))}\n"
        f"Allowed vector ids: {json.dumps(allowed_vector_ids, separators=(',', ':'))}\n"
        f"AttractorPacket JSON: {compact_packet}"
    )
    return {
        "system_prompt": ARCHITECT_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "response_contract": "plan_graph_json_only",
        "schema_name": "plan_graph.schema.json",
    }
