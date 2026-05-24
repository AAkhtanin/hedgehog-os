import json
from pathlib import Path

from hedgehog.architect_prompt_compiler import build_plan_graph_response_schema
from hedgehog.architect_prompt_compiler import compile_architect_prompt
from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def build_demo_packet():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    return build_attractor_packet(
        request_id="req_prompt_compiler_001",
        intent_id="intent_prompt_compiler_001",
        world_state_ref="world_state_prompt_compiler_001",
        goal_id="goal_prompt_compiler_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
        as_of=utc_now_iso(),
        max_selected=4,
    )


def test_compile_architect_prompt_preserves_root_boundary_and_json_contract():
    prompt = compile_architect_prompt(build_demo_packet())

    assert "You are not the RootOrchestrator" in prompt["system_prompt"]
    assert "You do not answer the user" in prompt["system_prompt"]
    assert "You do not create FinalOutput" in prompt["system_prompt"]
    assert "return only valid PlanGraph JSON" in prompt["system_prompt"]
    assert prompt["response_contract"] == "plan_graph_json_only"
    assert prompt["schema_name"] == "plan_graph.schema.json"


def test_compile_architect_prompt_includes_allowed_vectors_and_packet_json():
    packet = build_demo_packet()
    prompt = compile_architect_prompt(packet)
    allowed_vector_ids = [vector["vector_id"] for vector in packet["candidate_vectors"]]

    assert "AttractorPacket JSON:" in prompt["user_prompt"]
    assert "Return PlanGraph JSON only" in prompt["user_prompt"]
    assert "Required top-level fields: plan_id" in prompt["user_prompt"]
    assert "Required node fields: node_id" in prompt["user_prompt"]
    for vector_id in allowed_vector_ids:
        assert vector_id in prompt["user_prompt"]
    assert packet["packet_id"] in prompt["user_prompt"]
    assert json.dumps(packet, sort_keys=True, separators=(",", ":")) in prompt["user_prompt"]


def test_compile_architect_prompt_does_not_instruct_final_output_creation():
    prompt = compile_architect_prompt(build_demo_packet())

    assert "You do not create FinalOutput" in prompt["system_prompt"]
    assert "create FinalOutput" not in prompt["user_prompt"]


def test_build_plan_graph_response_schema_contains_required_plan_graph_shape():
    schema = build_plan_graph_response_schema()

    assert "plan_id" in schema["required"]
    assert "source_packet_id" in schema["required"]
    assert "nodes" in schema["required"]
    assert "edges" in schema["required"]
    assert "executor_assignments" in schema["required"]
    node_schema = schema["properties"]["nodes"]["items"]
    assert "node_id" in node_schema["required"]
    assert "vector_id" in node_schema["required"]
    assert "task" in node_schema["required"]
    assert "executor_id" in node_schema["required"]
    assert "depends_on" in node_schema["required"]
