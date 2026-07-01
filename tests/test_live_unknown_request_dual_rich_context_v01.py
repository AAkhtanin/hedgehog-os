from __future__ import annotations

import json
import sys
import types as py_types

import demo.run_live_unknown_request_dual_rich_context_v01 as runner
from hedgehog.structured_rationale import ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS
from hedgehog.structured_rationale import ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS
from hedgehog.structured_rationale import build_architect_structured_rationale
from hedgehog.structured_rationale import build_orchestrator_structured_rationale
from hedgehog.structured_rationale import validate_architect_structured_rationale
from hedgehog.structured_rationale import validate_orchestrator_structured_rationale


HOTEL_LIKE_REQUEST = (
    "A hotel manager asks if a service robot can clean occupied guest areas "
    "tonight when one guest has opted in, another has not answered, one suite "
    "is marked private, and one area has uncertain status."
)

MUSEUM_REQUEST = (
    "Can we move a museum artifact after hours if one approval is missing and "
    "climate status is unknown?"
)


def _context_from_prompt(prompt: str, marker: str) -> dict:
    raw = prompt.split(marker, 1)[1].strip()
    return json.loads(raw)


def _valid_orchestrator_rationale():
    return build_orchestrator_structured_rationale(
        observed_semantics=(
            {
                "summary": "unknown request requires bounded Root review",
                "candidate_only": True,
            },
        ),
        route_selection_reason=(
            {
                "route": "unknown_request_root_review",
                "reason": "unclear authority or evidence blocks action permission",
            },
        ),
        rejected_routes=(
            {
                "route": "direct_real_world_action",
                "reason": "external action cannot be authorized by Gemini",
            },
        ),
        required_guards_reasoning=(
            {"guard": "Root final authority", "status": "required"},
        ),
        selected_vector_reasoning=(
            {
                "vector": "unknown_request_semantic_review",
                "reason": "semantic review is advisory only",
            },
        ),
        uncertainty_notes=(
            {"note": "unknown request needs Root review"},
        ),
        authority_boundary=(
            {
                "Orchestrator is not Root": True,
                "creates_final_output": False,
            },
        ),
    )


def _valid_architect_rationale():
    return build_architect_structured_rationale(
        plan_shape_reason=(
            {
                "shape": "bounded_unknown_request_review",
                "reason": "PlanGraph remains advisory",
            },
        ),
        node_selection_reasoning=(
            {
                "node": "node:unknown_request_semantic_review",
                "reason": "review only, no action command",
            },
        ),
        executor_constraint_reasoning=(
            {
                "executor": "local_unknown_request_review_executor",
                "reason": "local semantic review executor",
            },
        ),
        forbidden_surface_review=(
            {"surface": "connector_or_external_action", "status": "blocked"},
        ),
        validator_coverage_reasoning=(
            {"validator": "Root final authority", "status": "required"},
        ),
        return_to_root_path=(
            {
                "path": "proposal_to_root_boundary",
                "final_authority": "Root",
            },
        ),
        uncertainty_notes=(
            {"note": "unknown facts remain unresolved"},
        ),
        authority_boundary=(
            {
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
            },
        ),
    )


def _valid_orchestrator_proposal(**overrides):
    payload = {
        "proposal_id": "orch-proposal-test-001",
        "suggested_route": "unknown_request_root_review",
        "selected_vector_ids": (
            "unknown_request_semantic_review",
            "external_action_boundary_review",
        ),
        "required_guards": (
            "ContextPacket validation",
            "structured rationale validation",
            "route validation",
            "Root final authority",
        ),
        "reason": "bounded route for unknown request",
        "confidence": 0.0,
        "needs_review": True,
        "uncertainty_notes": ("missing evidence or authority must remain unresolved",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "structured_orchestrator_rationale": _valid_orchestrator_rationale(),
    }
    payload.update(overrides)
    return payload


def _valid_architect_proposal(**overrides):
    payload = {
        "proposal_id": "arch-proposal-test-001",
        "source_route_id": "unknown_request_root_review",
        "selected_vector_ids": ("unknown_request_semantic_review",),
        "plan_nodes": (
            {
                "node_id": "node:unknown_request_semantic_review",
                "kind": "semantic_review",
                "executor_id": "local_unknown_request_review_executor",
                "expected_output": "ResultProposal",
            },
        ),
        "result_proposal_summary": "unknown request requires Root review",
        "root_recommendation": "not_ready",
        "required_validators": (
            "ArchitectPlanContextPacket validation",
            "structured rationale validation",
            "PlanGraph contract",
            "ResultProposal boundary",
            "Root final authority",
        ),
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
        "structured_architect_rationale": _valid_architect_rationale(),
    }
    payload.update(overrides)
    return payload


def _valid_orchestrator_compact_proposal(**overrides):
    payload = {
        "proposal_id": "orch-compact-proposal-test-001",
        "suggested_route": "unknown_request_root_review",
        "selected_vector_ids": (
            "unknown_request_semantic_review",
            "external_action_boundary_review",
        ),
        "required_guards": (
            "ContextPacket validation",
            "structured rationale validation",
            "route validation",
            "Root final authority",
        ),
        "reason": "compact bounded route for unknown request",
        "confidence": 0.0,
        "needs_review": True,
        "uncertainty_notes": ("missing evidence or authority remains unresolved",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "rationale_observed_semantics": (
            {"summary": "unknown request requires bounded Root review"},
        ),
        "rationale_route_selection_reason": (
            {
                "route": "unknown_request_root_review",
                "reason": "Root review required",
            },
        ),
        "rationale_rejected_routes": (
            {"route": "direct_real_world_action", "reason": "not allowed"},
        ),
        "rationale_required_guards_reasoning": (
            {"guard": "Root final authority", "status": "required"},
        ),
        "rationale_selected_vector_reasoning": (
            {
                "vector": "unknown_request_semantic_review",
                "reason": "advisory only",
            },
        ),
        "rationale_authority_boundary": (
            {
                "Orchestrator is not Root": True,
                "Root remains final authority": True,
            },
        ),
    }
    payload.update(overrides)
    return payload


def _valid_architect_compact_proposal(**overrides):
    payload = {
        "proposal_id": "arch-compact-proposal-test-001",
        "source_route_id": "unknown_request_root_review",
        "selected_vector_ids": ("unknown_request_semantic_review",),
        "plan_nodes": (
            {
                "node_id": "node:unknown_request_semantic_review",
                "kind": "semantic_review",
                "executor_id": "local_unknown_request_review_executor",
                "expected_output": "ResultProposal",
            },
        ),
        "result_proposal_summary": "unknown request requires Root review",
        "root_recommendation": "not_ready",
        "required_validators": (
            "ArchitectPlanContextPacket validation",
            "structured rationale validation",
            "PlanGraph contract",
            "ResultProposal boundary",
            "Root final authority",
        ),
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
        "rationale_plan_shape_reason": (
            {"shape": "bounded_unknown_request_review", "reason": "review only"},
        ),
        "rationale_node_selection_reasoning": (
            {"node": "node:unknown_request_semantic_review", "reason": "bounded"},
        ),
        "rationale_executor_constraint_reasoning": (
            {
                "executor": "local_unknown_request_review_executor",
                "reason": "allowed executor",
            },
        ),
        "rationale_forbidden_surface_review": (
            {"surface": "forbidden_command_surface", "status": "blocked"},
        ),
        "rationale_validator_coverage_reasoning": (
            {"validator": "Root final authority", "status": "required"},
        ),
        "rationale_return_to_root_path": (
            {"path": "proposal_to_root_boundary", "status": "required"},
        ),
        "rationale_authority_boundary": (
            {
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
            },
        ),
    }
    payload.update(overrides)
    return payload


def _providers(captured=None, *, architect_overrides=None, orchestrator_overrides=None):
    captured = captured if captured is not None else {}

    def orchestrator(prompt, model, timeout, env):
        captured["orchestrator_prompt"] = prompt
        captured["orchestrator_context"] = _context_from_prompt(
            prompt,
            "BOUNDED_UNKNOWN_REQUEST_ORCHESTRATOR_INPUT_JSON:",
        )
        return json.dumps(_valid_orchestrator_proposal(**(orchestrator_overrides or {})))

    def architect(prompt, model, timeout, env):
        captured["architect_prompt"] = prompt
        captured["architect_context"] = _context_from_prompt(
            prompt,
            "BOUNDED_UNKNOWN_REQUEST_ARCHITECT_INPUT_JSON:",
        )
        return json.dumps(_valid_architect_proposal(**(architect_overrides or {})))

    return orchestrator, architect


def _run_success(request=HOTEL_LIKE_REQUEST, captured=None):
    orchestrator, architect = _providers(captured)
    return runner.run_live_unknown_request_dual_rich_context(
        request,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )


def _install_fake_google_genai(monkeypatch, *, generate_content):
    captured = {}

    class FakeHttpOptions:
        def __init__(self, *, timeout=None):
            self.timeout = timeout
            captured["http_options_timeout"] = timeout

    class FakeModels:
        def generate_content(self, **kwargs):
            captured["generate_content_kwargs"] = kwargs
            return generate_content(**kwargs)

    class FakeClient:
        def __init__(self, *, api_key, http_options=None):
            captured["api_key"] = api_key
            captured["http_options"] = http_options
            self.models = FakeModels()

    google_module = py_types.ModuleType("google")
    genai_module = py_types.ModuleType("google.genai")
    types_module = py_types.ModuleType("google.genai.types")
    types_module.HttpOptions = FakeHttpOptions
    genai_module.Client = FakeClient
    genai_module.types = types_module
    google_module.genai = genai_module
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.genai", genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", types_module)
    return captured


def test_module_imports_public_api_exists() -> None:
    assert runner.TITLE == "LIVE UNKNOWN REQUEST DUAL RICH CONTEXT SPINE v0.1"
    assert callable(runner.run_live_unknown_request_dual_rich_context)
    assert callable(runner.render_report)
    assert callable(runner.main)


def test_missing_request_fails_closed() -> None:
    result = runner.run_live_unknown_request_dual_rich_context("")

    assert result["final_status"] == "FAIL_CLOSED"
    assert "request_required" in result["validation_errors"]


def test_orchestrator_prompt_contains_full_structured_rationale_skeleton() -> None:
    context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    prompt = runner._orchestrator_prompt(context)

    for field in ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        assert field in prompt
    assert "rationale_type" in prompt
    assert "schema_version" in prompt
    assert "structured_rationale_v0.1" in prompt
    assert (
        "structured_orchestrator_rationale MUST be a complete JSON object"
        in prompt
    )
    assert "MUST NOT be null" in prompt


def test_architect_prompt_contains_full_structured_rationale_skeleton() -> None:
    orchestrator_context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    orchestrator_proposal = _valid_orchestrator_proposal()
    route_packet = runner._route_packet_from_proposal(
        orchestrator_proposal,
        orchestrator_context,
    )
    architect_context = runner._architect_provider_context(
        route_packet=route_packet,
        route_validation={"accepted": True},
        orchestrator_proposal=orchestrator_proposal,
    )
    prompt = runner._architect_prompt(architect_context)

    for field in ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS:
        assert field in prompt
    assert "rationale_type" in prompt
    assert "schema_version" in prompt
    assert "structured_rationale_v0.1" in prompt
    assert "structured_architect_rationale MUST be a complete JSON object" in prompt
    assert "MUST NOT be null" in prompt


def test_prompt_skeleton_structured_rationales_validate_locally() -> None:
    orchestrator_context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    orchestrator_skeleton = runner._orchestrator_structured_rationale_skeleton(
        orchestrator_context
    )
    orchestrator_validation = validate_orchestrator_structured_rationale(
        orchestrator_skeleton
    )
    orchestrator_proposal = _valid_orchestrator_proposal()
    route_packet = runner._route_packet_from_proposal(
        orchestrator_proposal,
        orchestrator_context,
    )
    architect_context = runner._architect_provider_context(
        route_packet=route_packet,
        route_validation={"accepted": True},
        orchestrator_proposal=orchestrator_proposal,
    )
    architect_skeleton = runner._architect_structured_rationale_skeleton(
        architect_context
    )
    architect_validation = validate_architect_structured_rationale(
        architect_skeleton
    )

    assert orchestrator_validation["accepted"] is True
    assert architect_validation["accepted"] is True


def test_compact_orchestrator_prompt_excludes_full_structured_rationale_schema() -> None:
    context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    prompt = runner._orchestrator_compact_prompt(context)

    assert "rationale_observed_semantics" in prompt
    assert "rationale_route_selection_reason" in prompt
    assert "rationale_authority_boundary" in prompt
    assert "runtime will build canonical structured rationale" in prompt
    assert "Do not include structured_orchestrator_rationale directly" in prompt
    assert "structured_orchestrator_rationale MUST be a complete JSON object" not in prompt


def test_expand_orchestrator_compact_proposal_builds_valid_structured_rationale() -> None:
    context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    compact = _valid_orchestrator_compact_proposal(authority_claimed=True)
    expanded = runner._expand_orchestrator_compact_proposal(compact, context)
    validation = validate_orchestrator_structured_rationale(
        expanded["structured_orchestrator_rationale"]
    )

    assert validation["accepted"] is True
    assert expanded["authority_claimed"] is True
    assert expanded["structured_orchestrator_rationale"]["authority_claimed"] is False


def test_expand_architect_compact_proposal_builds_valid_structured_rationale() -> None:
    orchestrator_context = runner._orchestrator_provider_context(HOTEL_LIKE_REQUEST)
    orchestrator_proposal = _valid_orchestrator_proposal()
    route_packet = runner._route_packet_from_proposal(
        orchestrator_proposal,
        orchestrator_context,
    )
    architect_context = runner._architect_provider_context(
        route_packet=route_packet,
        route_validation={"accepted": True},
        orchestrator_proposal=orchestrator_proposal,
    )
    compact = _valid_architect_compact_proposal(final_output_claimed=True)
    expanded = runner._expand_architect_compact_proposal(compact, architect_context)
    validation = validate_architect_structured_rationale(
        expanded["structured_architect_rationale"]
    )

    assert validation["accepted"] is True
    assert expanded["final_output_claimed"] is True
    assert expanded["structured_architect_rationale"]["final_output_claimed"] is False


def test_injected_unknown_hotel_robot_request_reaches_root_not_ready() -> None:
    captured = {}
    result = _run_success(HOTEL_LIKE_REQUEST, captured)

    assert result["final_status"] == "PASS"
    assert result["root_final_output_boundary"]["decision"] == "not_ready"
    assert captured["orchestrator_context"]["raw_user_request"] == HOTEL_LIKE_REQUEST
    assert result["raw_user_request"] == HOTEL_LIKE_REQUEST
    assert result["counters"]["orchestrator_provider_call_count"] == 1
    assert result["counters"]["architect_provider_call_count"] == 1


def test_injected_second_unrelated_unknown_request_uses_same_spine() -> None:
    captured = {}
    result = _run_success(MUSEUM_REQUEST, captured)

    assert result["final_status"] == "PASS"
    assert result["raw_user_request"] == MUSEUM_REQUEST
    assert captured["orchestrator_context"]["raw_user_request"] == MUSEUM_REQUEST
    assert result["orchestrator_route_context_packet_validation"]["accepted"] is True
    assert result["architect_plan_context_packet_validation"]["accepted"] is True


def test_provider_input_contains_raw_request_but_no_raw_cross_role_text_downstream() -> None:
    captured = {}
    result = _run_success(HOTEL_LIKE_REQUEST, captured)
    architect_context = result["architect_provider_context"]

    assert captured["orchestrator_context"]["raw_user_request"] == HOTEL_LIKE_REQUEST
    assert "raw_user_request" not in captured["architect_context"]
    assert HOTEL_LIKE_REQUEST not in captured["architect_prompt"]
    assert architect_context["input_route_source"] == "validated_orchestrator_route"
    assert architect_context["raw_cross_role_text_present"] is False


def test_valid_orchestrator_route_context_packet_validates() -> None:
    result = _run_success()

    assert result["orchestrator_route_context_packet"]["packet_type"] == (
        "OrchestratorRouteContextPacket"
    )
    assert result["orchestrator_route_context_packet_validation"]["accepted"] is True
    assert result["orchestrator_route_context_packet"]["truth_claimed"] is False
    assert result["orchestrator_route_context_packet"]["authority_claimed"] is False


def test_valid_architect_plan_context_packet_validates() -> None:
    result = _run_success()

    assert result["architect_plan_context_packet"]["packet_type"] == (
        "ArchitectPlanContextPacket"
    )
    assert result["architect_plan_context_packet_validation"]["accepted"] is True
    assert result["architect_plan_context_packet"]["truth_claimed"] is False
    assert result["architect_plan_context_packet"]["authority_claimed"] is False


def test_structured_orchestrator_rationale_validates() -> None:
    result = _run_success()
    rationale = result["structured_orchestrator_rationale"]

    assert result["structured_orchestrator_rationale_validation"]["accepted"] is True
    assert rationale["rationale_type"] == "structured_orchestrator_rationale"
    assert rationale["truth_claimed"] is False
    assert rationale["authority_claimed"] is False
    assert rationale["action_permission_claimed"] is False
    assert rationale["final_output_claimed"] is False
    assert rationale["orchestrator_is_root"] is False


def test_structured_architect_rationale_validates() -> None:
    result = _run_success()
    rationale = result["structured_architect_rationale"]

    assert result["structured_architect_rationale_validation"]["accepted"] is True
    assert rationale["rationale_type"] == "structured_architect_rationale"
    assert rationale["truth_claimed"] is False
    assert rationale["authority_claimed"] is False
    assert rationale["action_permission_claimed"] is False
    assert rationale["final_output_claimed"] is False
    assert rationale["architect_is_root"] is False


def test_invalid_orchestrator_claims_fail_closed_before_architect() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(
                authority_claimed=True,
                action_permission_claimed=True,
                final_output_claimed=True,
            )
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert calls["architect"] == 0
    assert "orchestrator_authority_claim_forbidden" in result["validation_errors"]
    assert "orchestrator_action_claim_forbidden" in result["validation_errors"]
    assert "orchestrator_final_output_claim_forbidden" in result["validation_errors"]
    assert result["architect_provider_context"] == {}


def test_orchestrator_null_structured_rationale_still_fails_closed_before_architect() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(structured_orchestrator_rationale=None)
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "orchestrator_structured_rationale_validation_failed" in (
        result["validation_errors"]
    )
    assert calls["architect"] == 0
    assert result["orchestrator_provider_response_shape"][
        "structured_orchestrator_rationale_type"
    ] is None


def test_orchestrator_empty_structured_rationale_still_fails_closed_before_architect() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(structured_orchestrator_rationale={})
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "orchestrator_structured_rationale_validation_failed" in (
        result["validation_errors"]
    )
    assert "structured_rationale_missing_required_field:rationale_type" in (
        result["validation_errors"]
    )
    assert calls["architect"] == 0
    assert result["orchestrator_provider_response_shape"][
        "structured_orchestrator_rationale_keys"
    ] == ()


def test_orchestrator_suggested_route_must_be_allowed() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(
                suggested_route="direct_real_world_action",
            )
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "suggested_route_not_allowed" in result["validation_errors"]
    assert calls["architect"] == 0
    assert result["architect_provider_context"] == {}


def test_orchestrator_selected_vectors_must_be_allowed() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(
                selected_vector_ids=("vector:not_allowed",),
            )
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "selected_vector_ids_must_be_subset_of_allowed_vector_ids" in (
        result["validation_errors"]
    )
    assert calls["architect"] == 0
    assert result["architect_provider_context"] == {}


def test_orchestrator_required_guards_must_be_complete() -> None:
    calls = {"architect": 0}

    def orchestrator(prompt, model, timeout, env):
        return json.dumps(
            _valid_orchestrator_proposal(
                required_guards=(
                    "ContextPacket validation",
                    "structured rationale validation",
                    "route validation",
                ),
            )
        )

    def architect(prompt, model, timeout, env):
        calls["architect"] += 1
        return json.dumps(_valid_architect_proposal())

    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "missing_required_guard:Root final authority" in (
        result["validation_errors"]
    )
    assert calls["architect"] == 0
    assert result["architect_provider_context"] == {}


def test_invalid_architect_claims_fail_closed_before_plangraph_resultproposal() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "action_permission_claimed": True,
            "final_output_claimed": True,
            "connector_command_claimed": True,
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_action_claim_forbidden" in result["validation_errors"]
    assert "architect_final_output_claim_forbidden" in result["validation_errors"]
    assert "architect_connector_claim_forbidden" in result["validation_errors"]
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_source_route_must_match_validated_route() -> None:
    orchestrator, architect = _providers(
        architect_overrides={"source_route_id": "direct_real_world_action"}
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_source_route_id_must_match_validated_route" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_selected_vectors_must_match_validated_route() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "selected_vector_ids": ("vector:not_from_orchestrator",)
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert (
        "architect_selected_vector_ids_must_be_subset_of_validated_route_vectors"
        in result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_required_validators_must_be_complete() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "required_validators": (
                "ArchitectPlanContextPacket validation",
                "structured rationale validation",
                "PlanGraph contract",
                "ResultProposal boundary",
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "missing_required_architect_validator:Root final authority" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_null_structured_rationale_fails_before_plangraph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={"structured_architect_rationale": None}
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_structured_rationale_validation_failed" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}
    assert result["architect_provider_response_shape"][
        "structured_architect_rationale_type"
    ] is None


def test_architect_nested_action_surface_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "nested": {"action_permission_claimed": True},
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_action_surface_forbidden" in result["validation_errors"]
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_nested_connector_surface_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "nested": {"connector_command": "external_action_marker"},
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_connector_surface_forbidden" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_nested_final_output_surface_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "nested": {"final_output_claimed": True},
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_final_output_surface_forbidden" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_empty_final_output_key_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "nested": {"final_output": {}},
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_final_output_surface_forbidden" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_empty_connector_command_key_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "nested": {"connector_command": ""},
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_connector_surface_forbidden" in (
        result["validation_errors"]
    )
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_architect_external_action_phrase_fails_before_plan_graph() -> None:
    orchestrator, architect = _providers(
        architect_overrides={
            "plan_nodes": (
                {
                    "node_id": "node:bad",
                    "task": "prepare external action path",
                },
            )
        }
    )
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "architect_plan_action_surface_forbidden" in result["validation_errors"]
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}


def test_unknown_request_response_schemas_are_closed_top_level() -> None:
    assert runner.ORCHESTRATOR_RESPONSE_SCHEMA["additionalProperties"] is False
    assert runner.ARCHITECT_RESPONSE_SCHEMA["additionalProperties"] is False
    assert "structured_orchestrator_rationale" in (
        runner.ORCHESTRATOR_RESPONSE_SCHEMA["properties"]
    )
    assert "structured_architect_rationale" in (
        runner.ARCHITECT_RESPONSE_SCHEMA["properties"]
    )


def test_response_schemas_require_nested_structured_rationale_fields() -> None:
    orchestrator_schema = runner.ORCHESTRATOR_RESPONSE_SCHEMA["properties"][
        "structured_orchestrator_rationale"
    ]
    architect_schema = runner.ARCHITECT_RESPONSE_SCHEMA["properties"][
        "structured_architect_rationale"
    ]

    assert runner.ORCHESTRATOR_RESPONSE_SCHEMA["additionalProperties"] is False
    assert runner.ARCHITECT_RESPONSE_SCHEMA["additionalProperties"] is False
    assert orchestrator_schema["type"] == "object"
    assert architect_schema["type"] == "object"
    assert orchestrator_schema["additionalProperties"] is False
    assert architect_schema["additionalProperties"] is False
    for field in runner.ORCHESTRATOR_STRUCTURED_RATIONALE_SCHEMA_FIELDS:
        assert field in orchestrator_schema["required"]
        assert field in orchestrator_schema["properties"]
    for field in runner.ARCHITECT_STRUCTURED_RATIONALE_SCHEMA_FIELDS:
        assert field in architect_schema["required"]
        assert field in architect_schema["properties"]


def test_no_action_counters() -> None:
    result = _run_success()
    counters = result["counters"]

    assert counters["action_permission_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["real_world_effects_count"] == 0
    assert result["plan_graph_context"]["PlanGraph is not authority"] is True
    assert result["result_proposal"]["ResultProposal is not FinalOutput"] is True


def test_live_gate_without_provider_key_fails_closed_without_fake_fallback() -> None:
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1"},
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert "provider_sdk_or_key_missing" in result["validation_errors"]
    assert result["counters"]["orchestrator_provider_call_count"] == 1
    assert result["counters"]["architect_provider_call_count"] == 0
    assert result["counters"]["live_model_call_count"] == 0
    assert result["root_final_output_boundary"] == {}


def test_live_provider_timeout_seconds_is_passed_to_gemini_client(monkeypatch) -> None:
    assert (
        runner.provider_adapter.ENV_TIMEOUT_SECONDS
        == "HEDGEHOG_LIVE_PROVIDER_TIMEOUT_SECONDS"
    )

    class FakeResponse:
        parsed = _valid_orchestrator_proposal()
        text = ""

    captured = _install_fake_google_genai(
        monkeypatch,
        generate_content=lambda **kwargs: FakeResponse(),
    )

    raw = runner._call_live_gemini_provider(
        prompt="bounded prompt",
        model_name="gemini-test",
        timeout_seconds=7,
        env={runner.provider_adapter.ENV_GOOGLE_API_KEY: "test-key"},
        response_schema=runner.ORCHESTRATOR_RESPONSE_SCHEMA,
        role="orchestrator",
    )

    assert json.loads(raw)["proposal_id"] == "orch-proposal-test-001"
    assert captured["http_options_timeout"] == 7000
    assert captured["http_options"].timeout == 7000
    assert captured["generate_content_kwargs"]["model"] == "gemini-test"


def test_live_provider_can_construct_client_without_explicit_http_timeout(
    monkeypatch,
) -> None:
    class FakeResponse:
        parsed = _valid_architect_compact_proposal()
        text = ""

    captured = _install_fake_google_genai(
        monkeypatch,
        generate_content=lambda **kwargs: FakeResponse(),
    )

    raw = runner._call_live_gemini_provider(
        prompt="bounded prompt",
        model_name="gemini-test",
        timeout_seconds=7,
        explicit_http_timeout=False,
        env={runner.provider_adapter.ENV_GOOGLE_API_KEY: "test-key"},
        response_schema=runner.ARCHITECT_COMPACT_RESPONSE_SCHEMA,
        role="architect",
    )

    assert json.loads(raw)["proposal_id"] == "arch-compact-proposal-test-001"
    assert captured["http_options"] is None
    assert "http_options_timeout" not in captured
    assert captured["generate_content_kwargs"]["model"] == "gemini-test"


def test_live_provider_timeout_exception_maps_to_provider_timeout(monkeypatch) -> None:
    def timeout_response(**kwargs):
        raise TimeoutError("simulated timeout")

    _install_fake_google_genai(monkeypatch, generate_content=timeout_response)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={
            runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1",
            runner.provider_adapter.ENV_GOOGLE_API_KEY: "test-key",
            runner.provider_adapter.ENV_TIMEOUT_SECONDS: "3",
        },
    )
    counters = result["counters"]

    assert result["final_status"] == "FAIL_CLOSED"
    assert "provider_timeout" in result["validation_errors"]
    assert counters["orchestrator_provider_call_count"] == 1
    assert counters["architect_provider_call_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["action_permission_created_count"] == 0
    assert result["last_live_provider_role"] == "orchestrator"
    assert result["live_provider_role_in_progress"] == "orchestrator"
    assert result["provider_timeout_seconds"] == 3
    assert result["provider_error_shape"]["exception_type"] == "TimeoutError"


def test_live_architect_timeout_after_valid_orchestrator_fails_closed(monkeypatch) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_compact_proposal())
        raise runner.provider_adapter.ProviderTimeoutError("provider_timeout")

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={
            runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1",
            runner.provider_adapter.ENV_TIMEOUT_SECONDS: "4",
        },
    )
    counters = result["counters"]

    assert result["final_status"] == "FAIL_CLOSED"
    assert "provider_timeout" in result["validation_errors"]
    assert calls == ["orchestrator", "architect"]
    assert result["orchestrator_route_context_packet_validation"]["accepted"] is True
    assert result["structured_orchestrator_rationale_validation"]["accepted"] is True
    assert result["architect_plan_context_packet_validation"]["accepted"] is True
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}
    assert result["root_final_output_boundary"] == {}
    assert counters["live_model_call_count"] == 1
    assert counters["network_used_count"] == 1
    assert counters["gemini_called_count"] == 1
    assert counters["action_permission_created_count"] == 0
    assert result["last_live_provider_role"] == "architect"
    assert result["live_provider_role_in_progress"] == "architect"
    assert result["provider_timeout_seconds"] == 4
    assert result["provider_error_shape"]["exception_type"] == "ProviderTimeoutError"


def test_architect_pre_delay_is_applied_for_real_live_path(monkeypatch) -> None:
    calls = []
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_compact_proposal())
        return json.dumps(_valid_architect_compact_proposal())

    monkeypatch.setattr(runner, "_sleep_before_architect", fake_sleep)
    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={
            runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1",
            runner.ENV_UNKNOWN_REQUEST_LIVE_ARCHITECT_PRE_DELAY_SECONDS: "30",
        },
    )
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert calls == ["orchestrator", "architect"]
    assert sleep_calls == [30]
    assert result["architect_pre_delay_seconds"] == 30
    assert result["architect_pre_delay_applied"] is True
    assert counters["action_permission_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_architect_pre_delay_not_applied_for_injected_providers(monkeypatch) -> None:
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    orchestrator, architect = _providers()
    monkeypatch.setattr(runner, "_sleep_before_architect", fake_sleep)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_ARCHITECT_PRE_DELAY_SECONDS: "30"},
        orchestrator_provider=orchestrator,
        architect_provider=architect,
    )

    assert result["final_status"] == "PASS"
    assert sleep_calls == []
    assert result["architect_pre_delay_seconds"] == 30
    assert result["architect_pre_delay_applied"] is False
    assert result["counters"]["action_permission_created_count"] == 0


def test_architect_can_disable_explicit_http_timeout(monkeypatch) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(
            {
                "role": kwargs["role"],
                "explicit_http_timeout": kwargs["explicit_http_timeout"],
                "timeout_seconds": kwargs["timeout_seconds"],
            }
        )
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_compact_proposal())
        return json.dumps(_valid_architect_compact_proposal())

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={
            runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1",
            runner.ENV_UNKNOWN_REQUEST_LIVE_ARCHITECT_NO_EXPLICIT_TIMEOUT: "1",
        },
    )

    assert result["final_status"] == "PASS"
    assert calls[0]["role"] == "orchestrator"
    assert calls[0]["explicit_http_timeout"] is True
    assert calls[1]["role"] == "architect"
    assert calls[1]["explicit_http_timeout"] is False
    assert result["architect_no_explicit_timeout_enabled"] is True
    assert result["architect_explicit_http_timeout_enabled"] is False
    assert result["counters"]["action_permission_created_count"] == 0


def test_live_real_path_uses_compact_contract_by_default(monkeypatch) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs)
        if kwargs["role"] == "orchestrator":
            assert "rationale_observed_semantics" in kwargs["prompt"]
            assert "structured_orchestrator_rationale MUST" not in kwargs["prompt"]
            assert kwargs["response_schema"] is runner.ORCHESTRATOR_COMPACT_RESPONSE_SCHEMA
            return json.dumps(_valid_orchestrator_compact_proposal())
        assert "rationale_plan_shape_reason" in kwargs["prompt"]
        assert "structured_architect_rationale MUST" not in kwargs["prompt"]
        assert kwargs["response_schema"] is runner.ARCHITECT_COMPACT_RESPONSE_SCHEMA
        return json.dumps(_valid_architect_compact_proposal())

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1"},
    )
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert [call["role"] for call in calls] == ["orchestrator", "architect"]
    assert result["root_final_output_boundary"]["decision"] in (
        "not_ready",
        "needs_more_evidence",
    )
    assert result["live_provider_contract_mode"] == "compact_rationale_adapter"
    assert counters["compact_adapter_used_count"] == 1
    assert counters["compact_adapter_expanded_orchestrator_count"] == 1
    assert counters["compact_adapter_expanded_architect_count"] == 1
    assert counters["action_permission_created_count"] == 0
    assert counters["connector_called_count"] == 0


def test_compact_orchestrator_forbidden_claims_still_fail_closed_before_architect(
    monkeypatch,
) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(
                _valid_orchestrator_compact_proposal(
                    authority_claimed=True,
                    action_permission_claimed=True,
                    final_output_claimed=True,
                )
            )
        return json.dumps(_valid_architect_compact_proposal())

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1"},
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert calls == ["orchestrator"]
    assert "orchestrator_authority_claim_forbidden" in result["validation_errors"]
    assert "orchestrator_action_claim_forbidden" in result["validation_errors"]
    assert "orchestrator_final_output_claim_forbidden" in result["validation_errors"]


def test_compact_architect_forbidden_claims_still_fail_closed_before_plangraph(
    monkeypatch,
) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_compact_proposal())
        return json.dumps(
            _valid_architect_compact_proposal(
                action_permission_claimed=True,
                connector_command_claimed=True,
                final_output_claimed=True,
            )
        )

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1"},
    )

    assert result["final_status"] == "FAIL_CLOSED"
    assert calls == ["orchestrator", "architect"]
    assert "architect_action_claim_forbidden" in result["validation_errors"]
    assert "architect_connector_claim_forbidden" in result["validation_errors"]
    assert "architect_final_output_claim_forbidden" in result["validation_errors"]
    assert result["plan_graph_context"] == {}
    assert result["result_proposal"] == {}
    assert result["root_final_output_boundary"] == {}


def test_monkeypatched_live_provider_counts_two_model_network_gemini_calls(
    monkeypatch,
) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_compact_proposal())
        return json.dumps(_valid_architect_compact_proposal())

    monkeypatch.setattr(runner, "_call_live_gemini_provider", fake_live_provider)
    result = runner.run_live_unknown_request_dual_rich_context(
        HOTEL_LIKE_REQUEST,
        env={runner.ENV_UNKNOWN_REQUEST_LIVE_GEMINI: "1"},
    )
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert calls == ["orchestrator", "architect"]
    assert counters["live_model_call_count"] == 2
    assert counters["network_used_count"] == 2
    assert counters["gemini_called_count"] == 2
    assert result["root_final_output_boundary"]
    assert counters["action_permission_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["real_world_effects_count"] == 0
