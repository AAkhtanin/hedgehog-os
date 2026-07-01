from __future__ import annotations

import json

import demo.run_live_unknown_request_dual_rich_context_v01 as runner
from hedgehog.structured_rationale import build_architect_structured_rationale
from hedgehog.structured_rationale import build_orchestrator_structured_rationale


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


def test_module_imports_public_api_exists() -> None:
    assert runner.TITLE == "LIVE UNKNOWN REQUEST DUAL RICH CONTEXT SPINE v0.1"
    assert callable(runner.run_live_unknown_request_dual_rich_context)
    assert callable(runner.render_report)
    assert callable(runner.main)


def test_missing_request_fails_closed() -> None:
    result = runner.run_live_unknown_request_dual_rich_context("")

    assert result["final_status"] == "FAIL_CLOSED"
    assert "request_required" in result["validation_errors"]


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


def test_monkeypatched_live_provider_counts_two_model_network_gemini_calls(
    monkeypatch,
) -> None:
    calls = []

    def fake_live_provider(**kwargs):
        calls.append(kwargs["role"])
        if kwargs["role"] == "orchestrator":
            return json.dumps(_valid_orchestrator_proposal())
        return json.dumps(_valid_architect_proposal())

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
    assert counters["action_permission_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["real_world_effects_count"] == 0
