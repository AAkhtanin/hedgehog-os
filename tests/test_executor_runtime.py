import json
from pathlib import Path

import jsonschema
import pytest

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.executor import execute_plan_graph
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_proposal_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    time_envelope_schema = load_json(SCHEMAS_DIR / "time_envelope.schema.json")
    result_proposal_schema = load_json(SCHEMAS_DIR / "result_proposal.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        result_proposal_schema["$id"]: result_proposal_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(result_proposal_schema, store=store)
    return jsonschema.Draft202012Validator(
        result_proposal_schema, resolver=resolver
    )


def contains_key(value, forbidden_key):
    if isinstance(value, dict):
        return forbidden_key in value or any(
            contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden_key) for item in value)
    return False


def build_demo_plan_graph():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    packet = build_attractor_packet(
        request_id="req_executor_001",
        intent_id="intent_executor_001",
        world_state_ref="world_state_executor_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
        as_of=utc_now_iso(),
        max_selected=4,
    )
    return make_plan_graph(packet)


def test_execute_plan_graph_returns_schema_valid_result_proposals():
    plan_graph = build_demo_plan_graph()
    proposals = execute_plan_graph(plan_graph, session_anchor="sess_executor_001")
    validator = result_proposal_validator()

    assert len(proposals) == len(plan_graph["nodes"])

    node_vector_ids = {node["vector_id"] for node in plan_graph["nodes"]}
    proposal_vector_ids = {proposal["vector_id"] for proposal in proposals}
    assert proposal_vector_ids == node_vector_ids
    assert "illegal_coercion" not in proposal_vector_ids

    required_fields = {
        "proposal_id",
        "producer",
        "vector_id",
        "plan_id",
        "result_payload",
        "evidence",
        "cost",
        "risks",
        "time_envelope",
        "trace_refs",
    }
    time_fields = {
        "pt_created_at",
        "kt_asof",
        "ct_session_anchor",
        "ttl_seconds",
    }

    for proposal in proposals:
        assert required_fields <= set(proposal)
        assert time_fields <= set(proposal["time_envelope"])
        assert not contains_key(proposal, "final_output")
        assert not contains_key(proposal, "answer")
        assert not contains_key(proposal, "raw_user_text")
        validator.validate(proposal)


def test_execute_plan_graph_rejects_empty_nodes():
    plan_graph = build_demo_plan_graph()
    plan_graph["nodes"] = []

    with pytest.raises(ValueError):
        execute_plan_graph(plan_graph)
