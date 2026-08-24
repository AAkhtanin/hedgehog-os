from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import hedgehog.semantic_reasoning_adapter as adapter
from hedgehog.structured_rationale import (
    validate_architect_structured_rationale,
    validate_orchestrator_structured_rationale,
)



def _valid_orchestrator_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "proposal_id": "proposal:orchestrator:semantic",
        "suggested_route": "route:root_review",
        "selected_vector_ids": ("vector:semantic_review",),
        "required_guards": (
            "ContextPacket validation",
            "structured rationale validation",
            "route validation",
            "Root final authority",
        ),
        "reason": "request requires bounded Root review",
        "confidence": 0.62,
        "needs_review": True,
        "uncertainty_notes": ("missing or unresolved evidence remains open",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "semantic_observations": ("provider observed an ambiguous request",),
        "route_reasoning": ("Root review route preserves authority",),
        "rejected_route_reasoning": ("direct action route is not allowed",),
        "guard_reasoning": ("validators and Root final authority are required",),
        "vector_reasoning": ("semantic review vector is advisory only",),
        "authority_boundary_reasoning": (
            "Provider proposes semantics; Root decides",
        ),
    }
    payload.update(overrides)
    return payload


def _valid_architect_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "proposal_id": "proposal:architect:semantic",
        "source_route_id": "route:root_review",
        "selected_vector_ids": ("vector:semantic_review",),
        "root_recommendation": "needs_more_evidence",
        "result_proposal_summary": "request needs Root review before action",
        "required_validators": (
            "ArchitectPlanContextPacket validation",
            "structured rationale validation",
            "semantic_work_contract",
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
        "plan_shape_reasoning": ("describe bounded semantic work",),
        "node_intent_reasoning": (
            "identify semantic review obligations and return to Root",
        ),
        "executor_constraint_reasoning": (
            "semantic proposal does not assign runtime executors",
        ),
        "forbidden_surface_reasoning": (
            "no action, connector, or final surface is allowed",
        ),
        "validator_coverage_reasoning": (
            "SemanticWork, ResultProposal, and Root boundaries remain required",
        ),
        "return_to_root_reasoning": ("all proposal artifacts return to Root",),
        "uncertainty_notes": ("evidence gaps remain visible",),
        "authority_boundary_reasoning": (
            "PlanGraph is not authority and Root remains final authority",
        ),
    }
    payload.update(overrides)
    return payload


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(str(key) + " " + _flatten_text(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _walk_strings(value: Any) -> tuple[str, ...]:
    strings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            strings.append(str(key))
            strings.extend(_walk_strings(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            strings.extend(_walk_strings(item))
    elif isinstance(value, str):
        strings.append(value)
    return tuple(strings)


def test_public_api_and_constants_exist() -> None:
    for name in (
        "SEMANTIC_REASONING_MAX_ENTRY_TEXT_CHARS",
        "ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS",
        "ARCHITECT_SEMANTIC_REASONING_REQUIRED_FIELDS",
        "ORCHESTRATOR_SEMANTIC_REASONING_FIELDS",
        "ARCHITECT_SEMANTIC_REASONING_FIELDS",
        "semantic_reasoning_string_list",
        "validate_semantic_reasoning_fields",
        "semantic_reasoning_entries",
        "semantic_reasoning_fields_present",
        "validate_orchestrator_semantic_reasoning_proposal",
        "validate_architect_semantic_reasoning_proposal",
        "build_safe_local_plan_nodes_from_semantic_reasoning",
        "expand_orchestrator_semantic_reasoning_proposal",
        "expand_architect_semantic_reasoning_proposal",
    ):
        assert hasattr(adapter, name)


def test_semantic_reasoning_string_list_normalizes_strings() -> None:
    assert adapter.semantic_reasoning_string_list("  one  ") == ("one",)
    assert adapter.semantic_reasoning_string_list([" one ", "two"]) == ("one", "two")
    assert adapter.semantic_reasoning_string_list((" one ", "two")) == ("one", "two")
    assert adapter.semantic_reasoning_string_list("   ") == ()
    assert adapter.semantic_reasoning_string_list({"text": "one"}) == ()


def test_validate_semantic_reasoning_fields_rejects_missing_empty_invalid() -> None:
    field = "reasoning"

    assert adapter.validate_semantic_reasoning_fields({}, (field,)) == (
        "semantic_reasoning_missing_field:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: ""}, (field,)) == (
        "semantic_reasoning_empty_field:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: []}, (field,)) == (
        "semantic_reasoning_empty_field:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: [" "]}, (field,)) == (
        "semantic_reasoning_empty_item:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: [{}]}, (field,)) == (
        "semantic_reasoning_empty_item:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: [1]}, (field,)) == (
        "semantic_reasoning_invalid_type:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: {}}, (field,)) == (
        "semantic_reasoning_invalid_type:reasoning",
    )
    assert adapter.validate_semantic_reasoning_fields({field: 1}, (field,)) == (
        "semantic_reasoning_invalid_type:reasoning",
    )


def test_semantic_reasoning_entries_wrap_provider_text() -> None:
    entries = adapter.semantic_reasoning_entries(
        {"reasoning": (" first ", "second")},
        "reasoning",
    )

    assert entries == (
        {"text": "first", "source": "provider_semantic_reasoning"},
        {"text": "second", "source": "provider_semantic_reasoning"},
    )


def test_semantic_reasoning_entries_bounds_long_provider_text() -> None:
    long_text = "  " + ("bounded provider reasoning text " * 30) + "  "

    entries = adapter.semantic_reasoning_entries({"reasoning": long_text}, "reasoning")

    assert len(long_text) > 700
    assert len(entries) == 1
    assert entries[0]["source"] == "provider_semantic_reasoning"
    assert len(entries[0]["text"]) <= adapter.SEMANTIC_REASONING_MAX_ENTRY_TEXT_CHARS
    assert entries[0]["text"] == entries[0]["text"].strip()
    assert entries[0]["text"]


def test_validate_orchestrator_semantic_reasoning_proposal_accepts_valid_payload() -> None:
    assert adapter.validate_orchestrator_semantic_reasoning_proposal(
        _valid_orchestrator_payload()
    ) == ()


def test_validate_architect_semantic_reasoning_proposal_accepts_valid_payload_without_plan_nodes() -> None:
    assert adapter.validate_architect_semantic_reasoning_proposal(
        _valid_architect_payload()
    ) == ()


def test_architect_provider_plan_nodes_forbidden_in_semantic_mode() -> None:
    payload = _valid_architect_payload(plan_nodes=({"node_id": "provider_node"},))

    errors = adapter.validate_architect_semantic_reasoning_proposal(payload)

    assert "architect_provider_plan_nodes_forbidden_in_semantic_mode" in errors


def test_expand_architect_semantic_reasoning_rejects_provider_plan_nodes_directly() -> None:
    payload = _valid_architect_payload(plan_nodes=({"node_id": "provider_node"},))

    with pytest.raises(ValueError) as exc_info:
        adapter.expand_architect_semantic_reasoning_proposal(payload, {})

    assert "architect_provider_plan_nodes_forbidden_in_semantic_mode" in str(
        exc_info.value
    )


def test_expand_orchestrator_semantic_reasoning_builds_valid_structured_rationale() -> None:
    expanded = adapter.expand_orchestrator_semantic_reasoning_proposal(
        _valid_orchestrator_payload(authority_claimed=True),
        {"context_packet_type": "OrchestratorRouteContextPacket"},
    )

    validation = validate_orchestrator_structured_rationale(
        expanded["structured_orchestrator_rationale"]
    )

    assert validation["accepted"] is True
    assert expanded["authority_claimed"] is True
    rationale = expanded["structured_orchestrator_rationale"]
    assert rationale["authority_claimed"] is False
    assert rationale["root_final_authority_preserved"] is True
    assert rationale["Root remains final authority"] is True


def test_expand_orchestrator_semantic_reasoning_bounds_long_reasoning_for_structured_rationale() -> None:
    long_text = "Rejected route remains bounded before Root review. " * 20
    expanded = adapter.expand_orchestrator_semantic_reasoning_proposal(
        _valid_orchestrator_payload(
            rejected_route_reasoning=(long_text,),
            authority_claimed=True,
            action_permission_claimed=True,
            final_output_claimed=True,
            connector_command_claimed=True,
        ),
        {"context_packet_type": "OrchestratorRouteContextPacket"},
    )

    rationale = expanded["structured_orchestrator_rationale"]
    validation = validate_orchestrator_structured_rationale(rationale)

    assert len(long_text) > 700
    assert validation["accepted"] is True, validation
    assert max(len(item) for item in _walk_strings(rationale)) <= 512
    assert expanded["authority_claimed"] is True
    assert expanded["action_permission_claimed"] is True
    assert expanded["final_output_claimed"] is True
    assert expanded["connector_command_claimed"] is True
    assert rationale["authority_claimed"] is False
    assert rationale["action_permission_claimed"] is False
    assert rationale["final_output_claimed"] is False
    assert rationale["connector_command_claimed"] is False


def test_expand_architect_semantic_reasoning_builds_valid_structured_rationale_and_safe_nodes() -> None:
    expanded = adapter.expand_architect_semantic_reasoning_proposal(
        _valid_architect_payload(final_output_claimed=True),
        {
            "source_route_id": "route:root_review",
            "allowed_executor_ids": ("executor:semantic_review",),
        },
    )

    validation = validate_architect_structured_rationale(
        expanded["structured_architect_rationale"]
    )

    assert validation["accepted"] is True
    assert expanded["final_output_claimed"] is True
    rationale = expanded["structured_architect_rationale"]
    assert rationale["final_output_claimed"] is False
    assert rationale["root_final_authority_preserved"] is True
    assert rationale["Root remains final authority"] is True
    assert expanded["plan_nodes"]

    flattened = _flatten_text(expanded["plan_nodes"])
    for marker in (
        "action_permission",
        "connector_command",
        "final_output",
        "ActionCommitPacket",
        "FinalOutput",
        "real_world_effect",
    ):
        assert marker not in flattened


def test_expand_architect_semantic_reasoning_bounds_long_validator_reasoning_for_structured_rationale() -> None:
    long_text = "Validator coverage stays bounded before Root review. " * 20
    expanded = adapter.expand_architect_semantic_reasoning_proposal(
        _valid_architect_payload(
            validator_coverage_reasoning=(long_text,),
            action_permission_claimed=True,
            final_output_claimed=True,
            connector_command_claimed=True,
        ),
        {
            "source_route_id": "route:root_review",
            "allowed_executor_ids": ("executor:semantic_review",),
        },
    )

    rationale = expanded["structured_architect_rationale"]
    validation = validate_architect_structured_rationale(rationale)

    assert len(long_text) > 700
    assert validation["accepted"] is True, validation
    assert max(len(item) for item in _walk_strings(rationale)) <= 512
    assert expanded["action_permission_claimed"] is True
    assert expanded["final_output_claimed"] is True
    assert expanded["connector_command_claimed"] is True
    assert rationale["action_permission_claimed"] is False
    assert rationale["final_output_claimed"] is False
    assert rationale["connector_command_claimed"] is False


def test_expand_architect_semantic_reasoning_still_builds_safe_local_nodes_for_valid_payload() -> None:
    expanded = adapter.expand_architect_semantic_reasoning_proposal(
        _valid_architect_payload(),
        {
            "source_route_id": "route:root_review",
            "semantic_review_node_id": "node:review",
            "allowed_executor_ids": ("executor:review",),
        },
    )

    validation = validate_architect_structured_rationale(
        expanded["structured_architect_rationale"]
    )

    assert validation["accepted"] is True
    assert expanded["plan_nodes"]
    assert expanded["plan_nodes"][0]["node_id"] == "node:review"

    flattened = _flatten_text(expanded["plan_nodes"])
    for marker in (
        "action_permission",
        "connector_command",
        "final_output",
        "ActionCommitPacket",
        "FinalOutput",
        "real_world_effect",
    ):
        assert marker not in flattened


def test_safe_local_plan_nodes_are_context_driven() -> None:
    nodes = adapter.build_safe_local_plan_nodes_from_semantic_reasoning(
        {
            "source_route_id": "route:context",
            "semantic_review_node_id": "node:custom_review",
            "allowed_executor_ids": ("executor:custom", "executor:other"),
        }
    )

    assert nodes[0]["node_id"] == "node:custom_review"
    assert nodes[0]["executor_id"] == "executor:custom"
    assert nodes[0]["source_route_id"] == "route:context"
    assert nodes[1]["depends_on"] == ("node:custom_review",)

    flattened = _flatten_text(nodes).lower()
    for marker in ("archive", "hotel", "supplier"):
        assert marker not in flattened


def test_safe_local_plan_nodes_support_backwards_compatible_shape_options() -> None:
    nodes = adapter.build_safe_local_plan_nodes_from_semantic_reasoning(
        {"source_route_id": "route:context"},
        review_node_id="node:unknown_request_semantic_review",
        review_node_kind="semantic_review",
        executor_id="local_unknown_request_review_executor",
        include_source_route_on_root_gate=False,
    )

    assert nodes == (
        {
            "node_id": "node:unknown_request_semantic_review",
            "kind": "semantic_review",
            "executor_id": "local_unknown_request_review_executor",
            "expected_output": "ResultProposal",
            "advisory_only": True,
            "source_route_id": "route:context",
        },
        {
            "node_id": "node:root_review_gate",
            "kind": "root_review_gate",
            "executor_id": "local_unknown_request_review_executor",
            "expected_output": "ResultProposal",
            "depends_on": ("node:unknown_request_semantic_review",),
            "advisory_only": True,
            "Root remains final authority": True,
        },
    )


def test_expand_semantic_reasoning_supports_runner_boundary_options() -> None:
    orchestrator = adapter.expand_orchestrator_semantic_reasoning_proposal(
        _valid_orchestrator_payload(),
        {"context": True},
        include_gemini_proposes_boundary=False,
        include_context_available_boundary=False,
    )
    architect = adapter.expand_architect_semantic_reasoning_proposal(
        _valid_architect_payload(),
        {"source_route_id": "route:root_review"},
        include_gemini_proposes_boundary=False,
    )

    orchestrator_boundary = _flatten_text(
        orchestrator["structured_orchestrator_rationale"]["authority_boundary"]
    )
    architect_boundary = _flatten_text(
        architect["structured_architect_rationale"]["authority_boundary"]
    )

    assert "Gemini proposes, Root disposes" not in orchestrator_boundary
    assert "context_available" not in orchestrator_boundary
    assert "Gemini proposes, Root disposes" not in architect_boundary
    assert "Root remains final authority" in orchestrator_boundary
    assert "Root remains final authority" in architect_boundary


def test_missing_required_top_level_fields_are_reported() -> None:
    missing_top_level = _valid_orchestrator_payload()
    missing_top_level.pop("proposal_id")

    top_level_errors = adapter.validate_orchestrator_semantic_reasoning_proposal(
        missing_top_level
    )

    assert "missing_required_field:proposal_id" in top_level_errors

    missing_reasoning = _valid_orchestrator_payload()
    missing_reasoning.pop("semantic_observations")

    reasoning_errors = adapter.validate_orchestrator_semantic_reasoning_proposal(
        missing_reasoning
    )

    assert "missing_required_field:semantic_observations" in reasoning_errors
    assert "semantic_reasoning_missing_field:semantic_observations" in reasoning_errors


def test_provider_forbidden_booleans_are_preserved_for_validators() -> None:
    orchestrator = adapter.expand_orchestrator_semantic_reasoning_proposal(
        _valid_orchestrator_payload(
            authority_claimed=True,
            action_permission_claimed=True,
            final_output_claimed=True,
            connector_command_claimed=True,
            bypass_root_claimed=True,
        ),
        {},
    )
    architect = adapter.expand_architect_semantic_reasoning_proposal(
        _valid_architect_payload(
            authority_claimed=True,
            action_permission_claimed=True,
            final_output_claimed=True,
            connector_command_claimed=True,
            root_bypass_claimed=True,
        ),
        {},
    )

    for key in (
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
        "connector_command_claimed",
    ):
        assert orchestrator[key] is True
        assert architect[key] is True

    assert orchestrator["bypass_root_claimed"] is True
    assert architect["root_bypass_claimed"] is True

    for rationale in (
        orchestrator["structured_orchestrator_rationale"],
        architect["structured_architect_rationale"],
    ):
        assert rationale["authority_claimed"] is False
        assert rationale["action_permission_claimed"] is False
        assert rationale["final_output_claimed"] is False
        assert rationale["connector_command_claimed"] is False
        assert rationale["root_bypass_claimed"] is False


def test_core_module_has_no_provider_network_runtime_imports() -> None:
    source = Path(adapter.__file__).read_text()

    for forbidden in (
        "google",
        "genai",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "subprocess",
        "provider_adapter",
        "run_live_unknown_request",
        "HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI",
    ):
        assert forbidden not in source


def test_core_module_has_no_fixture_hardcodes() -> None:
    source = Path(adapter.__file__).read_text()

    for forbidden in (
        "city archive",
        "HOTEL-17",
        "R-101",
        "ROBOT-CLEAN-2042",
        "supplier payment",
        "warehouse",
        "certificate",
        "manual-live-unknown-request-real-gemini-007",
        "gemini-2.5-flash",
    ):
        assert forbidden not in source
