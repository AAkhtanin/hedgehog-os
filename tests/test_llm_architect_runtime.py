import json
import sys
import types
from copy import deepcopy
from pathlib import Path

import jsonschema

from hedgehog.architect import make_plan_graph
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


def install_fake_google_genai(monkeypatch, fake_client):
    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = fake_client
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)


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

    class FakeModels:
        def generate_content(self, **_kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        models = FakeModels()

    install_fake_google_genai(monkeypatch, FakeClient)
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


def test_gemini_architect_retries_invalid_first_response_and_completes(monkeypatch):
    packet = build_demo_packet()
    valid_plan_graph = make_plan_graph(packet)
    responses = [
        '{"plan_id":"bad","source_packet_id":"x","time_assumptions":{"as_of":"x","freshness_required":"normal","assumptions":["x"]},"nodes":[{"node_id":"n1","vector_id":"official_online_request","task":"t","executor_id":"e","depends_on":[],"expected_output":"result_proposal"}],"edges":[{"source":"n1","target":"n2"}],"executor_assignments":[{"executor_id":"e","node_ids":["n1"],"mode":"simulate"}]}',
        json.dumps(valid_plan_graph),
    ]
    calls = []

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return FakeResponse(responses.pop(0))

    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        models = FakeModels()

    install_fake_google_genai(monkeypatch, FakeClient)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    result = make_plan_graph_with_llm(
        attractor_packet=packet,
        provider="gemini",
        allow_config=False,
    )

    assert result["status"] == "completed"
    assert result["provider"] == "gemini"
    assert result["used_llm"] is True
    assert "retry_applied" in result["warnings"]
    assert result["plan_graph"] is not None
    assert len(calls) == 2
    assert "response_json_schema" in calls[0]["config"]
    assert "Validation error:" in calls[1]["contents"]
    validate_plan_graph_contract(result["plan_graph"], packet)


def test_gemini_architect_retry_failure_returns_error_and_fallback(monkeypatch):
    responses = ['{"nodes":[]}', '{"nodes":[]}']

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def generate_content(self, **_kwargs):
            return FakeResponse(responses.pop(0))

    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        models = FakeModels()

    install_fake_google_genai(monkeypatch, FakeClient)
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
    assert "retry_failed" in result["warnings"]
    assert "invalid_plan_graph_contract" in result["error"]


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


def _base_plan_graph(packet, nodes, edges):
    return {
        "plan_id": "plan:test",
        "request_id": packet["request_id"],
        "source_packet_id": packet["packet_id"],
        "time_assumptions": {
            "as_of": packet["time_context"]["as_of"],
            "freshness_required": packet["time_context"]["freshness_required"],
            "assumptions": ["test"],
        },
        "nodes": nodes,
        "edges": edges,
        "executor_assignments": [
            {
                "executor_id": "exec_mock_certificate",
                "node_ids": [node["node_id"] for node in nodes],
                "mode": "simulate",
            }
        ],
    }


def _node(node_id, vector_id="official_online_request"):
    return {
        "node_id": node_id,
        "vector_id": vector_id,
        "task": f"task:{node_id}",
        "executor_id": "exec_mock_certificate",
        "depends_on": [],
        "expected_output": "result_proposal",
    }


def _valid_control_graph(packet):
    return _base_plan_graph(
        packet,
        [_node("a"), _node("b")],
        [{"from": "a", "to": "b"}],
    )


def _assert_invalid_plan_graph_rejected(graph, packet):
    try:
        validate_plan_graph_contract(graph, packet)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("invalid PlanGraph was accepted")

    assert message.startswith("invalid_plan_graph_contract:")
    return message


def _contract_violation_cases(packet):
    cases = []

    graph = _valid_control_graph(packet)
    graph.pop("plan_id")
    cases.append(("missing plan_id", graph, "plan_id"))

    graph = _valid_control_graph(packet)
    graph.pop("source_packet_id")
    cases.append(("missing source_packet_id", graph, "source_packet_id"))

    graph = _valid_control_graph(packet)
    graph.pop("time_assumptions")
    cases.append(("missing time_assumptions", graph, "time_assumptions"))

    graph = _valid_control_graph(packet)
    graph.pop("nodes")
    cases.append(("missing nodes", graph, "nodes"))

    graph = _valid_control_graph(packet)
    graph["nodes"] = []
    graph["edges"] = []
    graph["executor_assignments"][0]["node_ids"] = []
    cases.append(("empty nodes", graph, "nodes must be a non-empty array"))

    graph = _valid_control_graph(packet)
    graph["nodes"][0].pop("node_id")
    cases.append(("node missing node_id", graph, "node_id"))

    graph = _valid_control_graph(packet)
    graph["nodes"][0].pop("vector_id")
    cases.append(("node missing vector_id", graph, "vector_id"))

    graph = _valid_control_graph(packet)
    graph["nodes"][0]["vector_id"] = "not_in_attractor_packet"
    cases.append(("node vector_id not in packet", graph, "disallowed vector_id"))

    graph = _valid_control_graph(packet)
    graph["nodes"][0]["depends_on"] = "a"
    cases.append(("node depends_on not array", graph, "depends_on must be an array"))

    graph = _valid_control_graph(packet)
    graph["edges"][0].pop("from")
    cases.append(("edge missing from", graph, "edge must include from and to"))

    graph = _valid_control_graph(packet)
    graph["edges"][0].pop("to")
    cases.append(("edge missing to", graph, "edge must include from and to"))

    graph = _valid_control_graph(packet)
    graph["edges"][0]["to"] = "unknown_node"
    cases.append(("edge references unknown node", graph, "edge references unknown node"))

    graph = _valid_control_graph(packet)
    graph["executor_assignments"][0]["node_ids"].append("unknown_node")
    cases.append(("executor_assignment references unknown node", graph, "assignment references unknown node"))

    graph = _valid_control_graph(packet)
    graph["final_output"] = {"status": "forbidden"}
    cases.append(("forbidden final_output", graph, "final_output"))

    graph = _valid_control_graph(packet)
    graph["answer"] = "forbidden"
    cases.append(("forbidden answer", graph, "answer"))

    graph = _valid_control_graph(packet)
    graph["raw_user_text"] = "forbidden"
    cases.append(("forbidden raw_user_text", graph, "raw_user_text"))

    graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b")],
        [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
    )
    cases.append(("cyclic graph A -> B -> A", graph, "DAG"))

    graph = _base_plan_graph(packet, [_node("a")], [{"from": "a", "to": "a"}])
    cases.append(("self-loop A -> A", graph, "DAG"))

    return cases


def test_validate_plan_graph_contract_rejects_violation_matrix():
    packet = build_demo_packet()
    for name, graph, expected_message in _contract_violation_cases(packet):
        message = _assert_invalid_plan_graph_rejected(deepcopy(graph), packet)
        assert expected_message in message, name


def test_validate_plan_graph_contract_accepts_deterministic_control_graph():
    packet = build_demo_packet()
    plan_graph = make_plan_graph(packet)

    validate_plan_graph_contract(plan_graph, packet)


def test_validate_plan_graph_contract_accepts_horizontal_branching():
    packet = build_demo_packet()
    graph = _base_plan_graph(packet, [_node("a"), _node("b"), _node("c")], [])

    validate_plan_graph_contract(graph, packet)


def test_validate_plan_graph_contract_accepts_vertical_chain():
    packet = build_demo_packet()
    graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b"), _node("c")],
        [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}],
    )

    validate_plan_graph_contract(graph, packet)


def test_validate_plan_graph_contract_accepts_hybrid_dag():
    packet = build_demo_packet()
    graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b"), _node("c"), _node("d")],
        [
            {"from": "a", "to": "b"},
            {"from": "a", "to": "c"},
            {"from": "b", "to": "d"},
            {"from": "c", "to": "d"},
        ],
    )

    validate_plan_graph_contract(graph, packet)


def _assert_cycle_rejected(graph, packet):
    try:
        validate_plan_graph_contract(graph, packet)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("cyclic PlanGraph was accepted")

    assert "invalid_plan_graph_contract" in message
    assert "cycle" in message or "DAG" in message


def test_validate_plan_graph_contract_rejects_self_loop():
    packet = build_demo_packet()
    graph = _base_plan_graph(
        packet,
        [_node("a")],
        [{"from": "a", "to": "a"}],
    )

    _assert_cycle_rejected(graph, packet)


def test_validate_plan_graph_contract_rejects_two_node_cycle():
    packet = build_demo_packet()
    graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b")],
        [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
    )

    _assert_cycle_rejected(graph, packet)


def test_validate_plan_graph_contract_rejects_three_node_cycle():
    packet = build_demo_packet()
    graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b"), _node("c")],
        [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
            {"from": "c", "to": "a"},
        ],
    )

    _assert_cycle_rejected(graph, packet)


def test_gemini_architect_cyclic_plan_graph_returns_error_and_fallback(monkeypatch):
    packet = build_demo_packet()
    cyclic_graph = _base_plan_graph(
        packet,
        [_node("a"), _node("b")],
        [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}],
    )
    responses = [json.dumps(cyclic_graph), json.dumps(cyclic_graph)]

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def generate_content(self, **_kwargs):
            return FakeResponse(responses.pop(0))

    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        models = FakeModels()

    install_fake_google_genai(monkeypatch, FakeClient)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    result = make_plan_graph_with_llm(
        attractor_packet=packet,
        provider="gemini",
        allow_config=False,
    )

    assert result["status"] == "error"
    assert result["used_llm"] is True
    assert result["fallback"] == "deterministic"
    assert "cycle" in result["error"] or "DAG" in result["error"]
