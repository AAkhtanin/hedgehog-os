from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedgehog.structured_rationale import (
    build_architect_structured_rationale,
    build_orchestrator_structured_rationale,
)


"""
Semantic reasoning adapter core contracts.

Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.

Provider output is not truth.
Provider output is not authority.
ContextPacket is not truth.
ContextPacket is not authority.
Structured rationale is explanation only.
Root remains final authority.
"""


PROVIDER_SEMANTIC_REASONING_SOURCE = "provider_semantic_reasoning"

SEMANTIC_REASONING_MISSING_FIELD_REASON = "semantic_reasoning_missing_field"
SEMANTIC_REASONING_EMPTY_FIELD_REASON = "semantic_reasoning_empty_field"
SEMANTIC_REASONING_INVALID_TYPE_REASON = "semantic_reasoning_invalid_type"
SEMANTIC_REASONING_EMPTY_ITEM_REASON = "semantic_reasoning_empty_item"
MISSING_REQUIRED_FIELD_REASON = "missing_required_field"
ARCHITECT_PROVIDER_PLAN_NODES_FORBIDDEN_REASON = (
    "architect_provider_plan_nodes_forbidden_in_semantic_mode"
)

ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS = (
    "proposal_id",
    "suggested_route",
    "selected_vector_ids",
    "required_guards",
    "reason",
    "confidence",
    "needs_review",
    "uncertainty_notes",
    "root_review_required",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "plan_graph_claimed",
    "bypass_root_claimed",
    "semantic_observations",
    "route_reasoning",
    "rejected_route_reasoning",
    "guard_reasoning",
    "vector_reasoning",
    "authority_boundary_reasoning",
)

ARCHITECT_SEMANTIC_REASONING_REQUIRED_FIELDS = (
    "proposal_id",
    "source_route_id",
    "selected_vector_ids",
    "root_recommendation",
    "result_proposal_summary",
    "required_validators",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "plan_shape_reasoning",
    "node_intent_reasoning",
    "executor_constraint_reasoning",
    "forbidden_surface_reasoning",
    "validator_coverage_reasoning",
    "return_to_root_reasoning",
    "uncertainty_notes",
    "authority_boundary_reasoning",
)

ORCHESTRATOR_SEMANTIC_REASONING_FIELDS = (
    "semantic_observations",
    "route_reasoning",
    "rejected_route_reasoning",
    "guard_reasoning",
    "vector_reasoning",
    "uncertainty_notes",
    "authority_boundary_reasoning",
)

ARCHITECT_SEMANTIC_REASONING_FIELDS = (
    "plan_shape_reasoning",
    "node_intent_reasoning",
    "executor_constraint_reasoning",
    "forbidden_surface_reasoning",
    "validator_coverage_reasoning",
    "return_to_root_reasoning",
    "uncertainty_notes",
    "authority_boundary_reasoning",
)

_DEFAULT_REVIEW_NODE_ID = "node:semantic_reasoning_review"
_DEFAULT_ROOT_GATE_NODE_ID = "node:root_review_gate"
_DEFAULT_EXECUTOR_ID = "local_semantic_reasoning_review_executor"


def semantic_reasoning_string_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, (list, tuple)):
        items: list[str] = []
        for item in value:
            if not isinstance(item, str):
                return ()
            stripped = item.strip()
            if not stripped:
                return ()
            items.append(stripped)
        return tuple(items)
    return ()


def validate_semantic_reasoning_fields(
    payload: Mapping[str, Any],
    required_reasoning_fields: tuple[str, ...],
) -> tuple[str, ...]:
    errors: list[str] = []
    for field in required_reasoning_fields:
        if field not in payload:
            errors.append(f"{SEMANTIC_REASONING_MISSING_FIELD_REASON}:{field}")
            continue

        value = payload[field]
        if isinstance(value, str):
            if not value.strip():
                errors.append(f"{SEMANTIC_REASONING_EMPTY_FIELD_REASON}:{field}")
            continue

        if isinstance(value, Mapping):
            reason = (
                SEMANTIC_REASONING_EMPTY_FIELD_REASON
                if not value
                else SEMANTIC_REASONING_INVALID_TYPE_REASON
            )
            errors.append(f"{reason}:{field}")
            continue

        if not isinstance(value, (list, tuple)):
            errors.append(f"{SEMANTIC_REASONING_INVALID_TYPE_REASON}:{field}")
            continue

        if not value:
            errors.append(f"{SEMANTIC_REASONING_EMPTY_FIELD_REASON}:{field}")
            continue

        for item in value:
            if isinstance(item, str):
                if not item.strip():
                    errors.append(f"{SEMANTIC_REASONING_EMPTY_ITEM_REASON}:{field}")
            elif isinstance(item, Mapping) and not item:
                errors.append(f"{SEMANTIC_REASONING_EMPTY_ITEM_REASON}:{field}")
            else:
                errors.append(f"{SEMANTIC_REASONING_INVALID_TYPE_REASON}:{field}")
    return tuple(errors)


def semantic_reasoning_entries(
    payload: Mapping[str, Any],
    field: str,
) -> tuple[dict[str, str], ...]:
    return tuple(
        {"text": item, "source": PROVIDER_SEMANTIC_REASONING_SOURCE}
        for item in semantic_reasoning_string_list(payload.get(field))
    )


def semantic_reasoning_fields_present(
    payload: Mapping[str, Any],
    fields: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(field for field in fields if field in payload)


def validate_orchestrator_semantic_reasoning_proposal(
    payload: Mapping[str, Any],
) -> tuple[str, ...]:
    errors = [
        f"{MISSING_REQUIRED_FIELD_REASON}:{field}"
        for field in ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS
        if field not in payload
    ]
    errors.extend(
        validate_semantic_reasoning_fields(
            payload,
            ORCHESTRATOR_SEMANTIC_REASONING_FIELDS,
        )
    )
    return tuple(errors)


def validate_architect_semantic_reasoning_proposal(
    payload: Mapping[str, Any],
) -> tuple[str, ...]:
    errors = [
        f"{MISSING_REQUIRED_FIELD_REASON}:{field}"
        for field in ARCHITECT_SEMANTIC_REASONING_REQUIRED_FIELDS
        if field not in payload
    ]
    errors.extend(
        validate_semantic_reasoning_fields(
            payload,
            ARCHITECT_SEMANTIC_REASONING_FIELDS,
        )
    )
    if "plan_nodes" in payload:
        errors.append(ARCHITECT_PROVIDER_PLAN_NODES_FORBIDDEN_REASON)
    return tuple(errors)


def _first_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (list, tuple)):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return None


def build_safe_local_plan_nodes_from_semantic_reasoning(
    architect_context: Mapping[str, Any],
    *,
    review_node_id: str | None = None,
    root_gate_node_id: str = _DEFAULT_ROOT_GATE_NODE_ID,
) -> tuple[dict[str, Any], ...]:
    resolved_review_node_id = (
        review_node_id
        or _first_string(architect_context.get("semantic_review_node_id"))
        or _DEFAULT_REVIEW_NODE_ID
    )
    executor_id = (
        _first_string(architect_context.get("allowed_executor_ids"))
        or _DEFAULT_EXECUTOR_ID
    )
    source_route_id = architect_context.get("source_route_id")

    return (
        {
            "node_id": resolved_review_node_id,
            "kind": "semantic_reasoning_review",
            "executor_id": executor_id,
            "expected_output": "ResultProposal",
            "advisory_only": True,
            "source_route_id": source_route_id,
        },
        {
            "node_id": root_gate_node_id,
            "kind": "root_review_gate",
            "executor_id": executor_id,
            "expected_output": "ResultProposal",
            "depends_on": (resolved_review_node_id,),
            "advisory_only": True,
            "source_route_id": source_route_id,
            "Root remains final authority": True,
        },
    )


def expand_orchestrator_semantic_reasoning_proposal(
    proposal: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    expanded = dict(proposal)
    expanded["structured_orchestrator_rationale"] = (
        build_orchestrator_structured_rationale(
            observed_semantics=semantic_reasoning_entries(
                proposal,
                "semantic_observations",
            ),
            route_selection_reason=semantic_reasoning_entries(
                proposal,
                "route_reasoning",
            )
            + (
                {
                    "suggested_route": str(proposal.get("suggested_route") or ""),
                    "source": PROVIDER_SEMANTIC_REASONING_SOURCE,
                },
            ),
            rejected_routes=semantic_reasoning_entries(
                proposal,
                "rejected_route_reasoning",
            ),
            required_guards_reasoning=semantic_reasoning_entries(
                proposal,
                "guard_reasoning",
            ),
            selected_vector_reasoning=semantic_reasoning_entries(
                proposal,
                "vector_reasoning",
            ),
            uncertainty_notes=semantic_reasoning_entries(
                proposal,
                "uncertainty_notes",
            ),
            authority_boundary=semantic_reasoning_entries(
                proposal,
                "authority_boundary_reasoning",
            )
            + (
                {
                    "ContextPacket is not truth": True,
                    "ContextPacket is not authority": True,
                    "structured rationale is explanation only": True,
                    "Orchestrator is not Root": True,
                    "Gemini proposes, Root disposes": True,
                    "Root remains final authority": True,
                    "context_available": bool(context),
                },
            ),
            root_review_required=True,
        )
    )
    return expanded


def expand_architect_semantic_reasoning_proposal(
    proposal: Mapping[str, Any],
    architect_context: Mapping[str, Any],
    *,
    review_node_id: str | None = None,
    root_gate_node_id: str = _DEFAULT_ROOT_GATE_NODE_ID,
) -> dict[str, Any]:
    if "plan_nodes" in proposal:
        raise ValueError(ARCHITECT_PROVIDER_PLAN_NODES_FORBIDDEN_REASON)

    expanded = dict(proposal)
    expanded["plan_nodes"] = build_safe_local_plan_nodes_from_semantic_reasoning(
        architect_context,
        review_node_id=review_node_id,
        root_gate_node_id=root_gate_node_id,
    )
    expanded["structured_architect_rationale"] = build_architect_structured_rationale(
        plan_shape_reason=semantic_reasoning_entries(
            proposal,
            "plan_shape_reasoning",
        ),
        node_selection_reasoning=semantic_reasoning_entries(
            proposal,
            "node_intent_reasoning",
        ),
        executor_constraint_reasoning=semantic_reasoning_entries(
            proposal,
            "executor_constraint_reasoning",
        ),
        forbidden_surface_review=semantic_reasoning_entries(
            proposal,
            "forbidden_surface_reasoning",
        ),
        validator_coverage_reasoning=semantic_reasoning_entries(
            proposal,
            "validator_coverage_reasoning",
        ),
        return_to_root_path=semantic_reasoning_entries(
            proposal,
            "return_to_root_reasoning",
        ),
        uncertainty_notes=semantic_reasoning_entries(
            proposal,
            "uncertainty_notes",
        ),
        authority_boundary=semantic_reasoning_entries(
            proposal,
            "authority_boundary_reasoning",
        )
        + (
            {
                "ContextPacket is not truth": True,
                "ContextPacket is not authority": True,
                "structured rationale is explanation only": True,
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
                "ResultProposal is not FinalOutput": True,
                "Gemini proposes, Root disposes": True,
                "Root remains final authority": True,
            },
        ),
        root_review_required=True,
    )
    return expanded


__all__ = (
    "PROVIDER_SEMANTIC_REASONING_SOURCE",
    "SEMANTIC_REASONING_MISSING_FIELD_REASON",
    "SEMANTIC_REASONING_EMPTY_FIELD_REASON",
    "SEMANTIC_REASONING_INVALID_TYPE_REASON",
    "SEMANTIC_REASONING_EMPTY_ITEM_REASON",
    "MISSING_REQUIRED_FIELD_REASON",
    "ARCHITECT_PROVIDER_PLAN_NODES_FORBIDDEN_REASON",
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
)
