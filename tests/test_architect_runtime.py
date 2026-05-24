import json
from pathlib import Path

import jsonschema
import pytest

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def plan_graph_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    plan_graph_schema = load_json(SCHEMAS_DIR / "plan_graph.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        plan_graph_schema["$id"]: plan_graph_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(plan_graph_schema, store=store)
    return jsonschema.Draft202012Validator(plan_graph_schema, resolver=resolver)


def load_demo_vectors():
    return load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )


def build_demo_packet():
    return build_attractor_packet(
        request_id="req_architect_001",
        intent_id="intent_architect_001",
        world_state_ref="world_state_architect_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=load_demo_vectors(),
        as_of=utc_now_iso(),
        max_selected=4,
    )


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def test_make_plan_graph_from_attractor_packet_validates_schema():
    packet = build_demo_packet()
    plan_graph = make_plan_graph(packet)

    packet_vector_ids = {vector["vector_id"] for vector in packet["candidate_vectors"]}
    node_vector_ids = {node["vector_id"] for node in plan_graph["nodes"]}

    assert plan_graph["source_packet_id"] == packet["packet_id"]
    assert "time_assumptions" in plan_graph
    assert plan_graph["nodes"]
    assert len(plan_graph["nodes"]) > len(packet["candidate_vectors"])
    assert node_vector_ids <= packet_vector_ids
    assert "illegal_coercion" not in node_vector_ids
    assert all(node["branching_mode"] != "forbidden" for node in plan_graph["nodes"])
    assert all("avf_final_viability=" in node["task"] for node in plan_graph["nodes"])
    assert all("avf_soft_mask=" in node["task"] for node in plan_graph["nodes"])
    assert not contains_key(plan_graph, "final_output")
    assert not contains_key(plan_graph, "answer")
    assert not contains_key(plan_graph, "raw_user_text")

    plan_graph_validator().validate(plan_graph)


def test_make_plan_graph_official_online_request_branch_has_ordered_dependencies():
    packet = build_demo_packet()
    plan_graph = make_plan_graph(packet)

    official_nodes = [
        node
        for node in plan_graph["nodes"]
        if node["vector_id"] == "official_online_request"
    ]
    official_tasks = [node["task"].split(":", 1)[0] for node in official_nodes]

    assert official_tasks == [
        "prepare_request_payload",
        "validate_required_fields",
        "simulate_submission_step",
    ]
    assert official_nodes[0]["depends_on"] == []
    assert official_nodes[1]["depends_on"] == [official_nodes[0]["node_id"]]
    assert official_nodes[2]["depends_on"] == [official_nodes[1]["node_id"]]


def test_make_plan_graph_edges_and_executor_assignments_cover_nodes():
    packet = build_demo_packet()
    plan_graph = make_plan_graph(packet)

    node_ids = {node["node_id"] for node in plan_graph["nodes"]}
    edge_refs = {
        ref
        for edge in plan_graph["edges"]
        for ref in (edge["from"], edge["to"])
    }
    assigned_node_ids = {
        node_id
        for assignment in plan_graph["executor_assignments"]
        for node_id in assignment["node_ids"]
    }

    assert edge_refs <= node_ids
    assert assigned_node_ids == node_ids


def test_make_plan_graph_rejects_empty_candidate_vectors():
    packet = build_demo_packet()
    packet["candidate_vectors"] = []

    with pytest.raises(ValueError):
        make_plan_graph(packet)
