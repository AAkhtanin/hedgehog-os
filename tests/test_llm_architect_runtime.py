import json
import sys
import types
from pathlib import Path

import jsonschema

from hedgehog.avf import build_attractor_packet
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.llm_architect import make_plan_graph_with_llm, validate_plan_graph_contract
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


def build_demo_packet():
    vectors = load_candidate_vectors_from_needles(
        [
            NEEDLES_DIR / "government_services.json",
            NEEDLES_DIR / "fallback_exploration.json",
        ]
    )
    return build_attractor_packet(
        request_id="req_llm_architect_001",
        intent_id="intent_llm_architect_001",
        world_state_ref="world_state_llm_architect_001",
        goal_id="goal_llm_architect_001",
        desired_state="Prepare a mock government certificate request plan.",
        candidate_vectors=vectors,
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


def test_mock_llm_architect_returns_valid_plan_graph():
    packet = build_demo_packet()
    result = make_plan_graph_with_llm(attractor_packet=packet, provider="mock")
    plan_graph = result["plan_graph"]

    assert result["status"] == "completed"
    assert result["provider"] == "mock"
    assert result["model"] == "mock_architect_v1"
    assert result["used_llm"] is False
    assert plan_graph is not None
    plan_graph_validator().validate(plan_graph)


def test_mock_llm_architect_uses_only_packet_vector_ids_and_no_forbidden_output():
    packet = build_demo_packet()
    result = make_plan_graph_with_llm(attractor_packet=packet, provider="mock")
    plan_graph = result["plan_graph"]
    allowed = {vector["vector_id"] for vector in packet["candidate_vectors"]}
    node_vector_ids = {node["vector_id"] for node in plan_graph["nodes"]}

    assert node_vector_ids <= allowed
    assert not contains_key(plan_graph, "final_output")
    assert not contains_key(plan_graph, "answer")
    assert not contains_key(plan_graph, "raw_user_text")


def test_unsupported_architect_provider_returns_error():
    result = make_plan_graph_with_llm(
        attractor_packet=build_demo_packet(),
        provider="unsupported",
    )

    assert result["status"] == "error"
    assert result["plan_graph"] is None
    assert result["used_llm"] is False
    assert result["error"]


def test_gemini_architect_without_key_and_config_disabled_returns_error(monkeypatch):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    result = make_plan_graph_with_llm(
        attractor_packet=build_demo_packet(),
        provider="gemini",
        allow_config=False,
    )

    assert result["status"] == "error"
    assert result["provider"] == "gemini"
    assert result["used_llm"] is False
    assert result["plan_graph"] is None
    assert result["error"]


def test_gemini_architect_invalid_response_after_api_call_marks_used_llm_true(monkeypatch):
    class FakeResponse:
        text = '{"nodes":[]}'

    class FakeModel:
        def __init__(self, *_args, **_kwargs):
            pass

        def generate_content(self, _prompt):
            return FakeResponse()

    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = lambda **_kwargs: None
    fake_genai.GenerativeModel = FakeModel
    fake_google.generativeai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    result = make_plan_graph_with_llm(
        attractor_packet=build_demo_packet(),
        provider="gemini",
        allow_config=False,
    )

    assert result["status"] == "error"
    assert result["provider"] == "gemini"
    assert result["used_llm"] is True
    assert result["plan_graph"] is None
    assert result["fallback"] == "deterministic"
    assert "invalid_plan_graph_contract" in result["error"]
    assert "plan_id" in result["error"]


def test_validate_plan_graph_contract_rejects_missing_plan_id():
    packet = build_demo_packet()
    invalid_plan_graph = {
        "request_id": packet["request_id"],
        "source_packet_id": packet["packet_id"],
        "time_assumptions": {
            "as_of": packet["time_context"]["as_of"],
            "freshness_required": packet["time_context"]["freshness_required"],
            "assumptions": ["test"],
        },
        "nodes": [
            {
                "node_id": "node_invalid_001",
                "vector_id": packet["candidate_vectors"][0]["vector_id"],
                "task": "simulate",
                "executor_id": "exec_mock_certificate",
                "depends_on": [],
                "expected_output": "result_proposal",
            }
        ],
        "edges": [],
        "executor_assignments": [
            {
                "executor_id": "exec_mock_certificate",
                "node_ids": ["node_invalid_001"],
                "mode": "simulate",
            }
        ],
    }

    try:
        validate_plan_graph_contract(invalid_plan_graph, packet)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("invalid PlanGraph was accepted")

    assert "invalid_plan_graph_contract" in message
    assert "plan_id" in message
