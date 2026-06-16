import json
from pathlib import Path

import jsonschema

from hedgehog.avf import build_attractor_packet, score_candidate_vector
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SCHEMAS_DIR = ROOT / "schemas"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def attractor_packet_validator():
    common_schema = load_json(SCHEMAS_DIR / "common.schema.json")
    attractor_schema = load_json(SCHEMAS_DIR / "attractor_packet.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        attractor_schema["$id"]: attractor_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(attractor_schema, store=store)
    return jsonschema.Draft202012Validator(attractor_schema, resolver=resolver)


def load_demo_vectors():
    return load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )


def test_illegal_coercion_is_hard_masked():
    vectors = {vector.vector_id: vector for vector in load_demo_vectors()}
    score = score_candidate_vector(vectors["illegal_coercion"])

    assert score["hard_masked"] is True
    assert score["final_viability"] == 0


def test_build_attractor_packet_filters_forbidden_vectors_and_validates_schema():
    packet = build_attractor_packet(
        request_id="req_avf_001",
        intent_id="intent_avf_001",
        world_state_ref="world_state_avf_001",
        goal_id="goal_certificate_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=load_demo_vectors(),
        as_of=utc_now_iso(),
        max_selected=4,
    )

    packet_vectors = packet["candidate_vectors"]
    vector_ids = {vector["vector_id"] for vector in packet_vectors}

    assert "illegal_coercion" not in vector_ids
    assert "official_online_request" in vector_ids
    assert packet["architect_instructions"] == {
        "do_not_expand_forbidden_regions": True,
        "must_return_time_assumptions": True,
        "must_return_plan_graph_only": True,
    }
    assert packet["architect_instructions"]["must_return_plan_graph_only"] is True
    assert "must_return_result_proposals_only" not in packet["architect_instructions"]
    assert "must_return_result_proposals_only" not in json.dumps(packet, sort_keys=True)
    assert all(vector["branching_mode"] != "forbidden" for vector in packet_vectors)

    viabilities = [vector["final_viability"] for vector in packet_vectors]
    assert viabilities == sorted(viabilities, reverse=True)

    attractor_packet_validator().validate(packet)
