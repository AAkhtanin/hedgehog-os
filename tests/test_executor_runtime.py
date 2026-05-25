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


def proposals_by_task_prefix(plan_graph, proposals):
    nodes_by_id = {node["node_id"]: node for node in plan_graph["nodes"]}
    proposals_by_prefix = {}
    for proposal in proposals:
        node = nodes_by_id[proposal["result_payload"]["node_id"]]
        prefix = node["task"].split(";", 1)[0].split(":", 1)[0]
        proposals_by_prefix[prefix] = proposal
    return proposals_by_prefix


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
        assert "artifact_type" in proposal["result_payload"]
        assert "avf" in proposal["result_payload"]
        assert proposal["result_payload"]["node_id"]
        assert proposal["result_payload"]["vector_id"] == proposal["vector_id"]
        assert proposal["result_payload"]["executor_id"] == proposal["producer"]["executor_id"]
        assert proposal["result_payload"]["task_short"]
        assert proposal["result_payload"]["depends_on_count"] >= 0
        assert proposal["result_payload"]["dependency_depth"] >= 0
        assert proposal["result_payload"]["avf"]["vector_id"] == proposal["vector_id"]
        assert 0.0 <= proposal["result_payload"]["avf"]["final_viability"] <= 1.0
        assert 0.0 <= proposal["result_payload"]["avf"]["soft_mask"] <= 1.0
        assert not contains_key(proposal, "final_output")
        assert not contains_key(proposal, "answer")
        assert not contains_key(proposal, "raw_user_text")
        validator.validate(proposal)

    viability_by_vector = {}
    for proposal in proposals:
        viability_by_vector.setdefault(
            proposal["vector_id"],
            proposal["result_payload"]["avf"]["final_viability"],
        )
    assert viability_by_vector["official_online_request"] > viability_by_vector["fallback_exploration"]


def test_execute_plan_graph_returns_task_aware_payloads():
    plan_graph = build_demo_plan_graph()
    proposals = execute_plan_graph(plan_graph, session_anchor="sess_executor_002")
    by_task = proposals_by_task_prefix(plan_graph, proposals)

    prepare_payload = by_task["prepare_request_payload"]["result_payload"]
    assert prepare_payload["artifact_type"] == "request_payload"
    assert prepare_payload["payload_fields"] == [
        "applicant_identity_pointer",
        "service_type",
        "delivery_preference",
    ]
    assert prepare_payload["next_requirement"] == "validate_required_fields"

    validation_payload = by_task["validate_required_fields"]["result_payload"]
    assert validation_payload["artifact_type"] == "field_validation"
    assert validation_payload["missing_fields"] == ["applicant_identity_pointer"]
    assert validation_payload["requires_human_input"] is True

    submission = by_task["simulate_submission_step"]
    submission_payload = submission["result_payload"]
    assert submission_payload["status"] == "needs_user"
    assert submission_payload["task_completed"] is False
    assert submission_payload["artifact_type"] == "submission_simulation"
    assert submission_payload["blocked_reason"] == "missing_human_identity_confirmation"
    assert submission["risks"] == [
        {
            "risk_id": "risk:human_confirmation_required",
            "severity": "low",
            "description": "Submission cannot proceed without human confirmation.",
        }
    ]


def test_execute_plan_graph_rejects_empty_nodes():
    plan_graph = build_demo_plan_graph()
    plan_graph["nodes"] = []

    with pytest.raises(ValueError):
        execute_plan_graph(plan_graph)
