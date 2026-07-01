from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


"""
Dual Rich Context Structured Rationale core contracts.

Structured rationale is JSON explanation, bounded, auditable,
user-readable, and machine-validatable.

Structured rationale is not truth.
Structured rationale is not authority.
Structured rationale is not action permission.
Structured rationale is not FinalOutput.
Structured rationale is not ActionCommitPacket.
Root remains final authority.
"""


STRUCTURED_RATIONALE_SCHEMA_VERSION = "structured_rationale_v0.1"
ORCHESTRATOR_STRUCTURED_RATIONALE_TYPE = "structured_orchestrator_rationale"
ARCHITECT_STRUCTURED_RATIONALE_TYPE = "structured_architect_rationale"

ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS = (
    "observed_semantics",
    "route_selection_reason",
    "rejected_routes",
    "required_guards_reasoning",
    "selected_vector_reasoning",
    "uncertainty_notes",
    "authority_boundary",
    "root_review_required",
)

ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS = (
    "plan_shape_reason",
    "node_selection_reasoning",
    "executor_constraint_reasoning",
    "forbidden_surface_review",
    "validator_coverage_reasoning",
    "return_to_root_path",
    "uncertainty_notes",
    "authority_boundary",
    "root_review_required",
)

ORCHESTRATOR_STRUCTURED_RATIONALE_ROLE_BOUNDARY_FIELDS = (
    "orchestrator_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
)

ARCHITECT_STRUCTURED_RATIONALE_ROLE_BOUNDARY_FIELDS = (
    "architect_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
)

_COMMON_REQUIRED_FIELDS = (
    "rationale_type",
    "schema_version",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "action_commit_packet_claimed",
    "root_bypass_claimed",
    "root_final_authority_preserved",
    "Root remains final authority",
)

_COMMON_FORBIDDEN_CLAIMS = {
    "truth_claimed": "structured_rationale_truth_claim_forbidden",
    "authority_claimed": "structured_rationale_authority_claim_forbidden",
    "action_permission_claimed": (
        "structured_rationale_action_permission_claim_forbidden"
    ),
    "final_output_claimed": "structured_rationale_final_output_claim_forbidden",
    "connector_command_claimed": "structured_rationale_connector_command_forbidden",
    "drs_write_claimed": "structured_rationale_drs_write_forbidden",
    "action_commit_packet_claimed": (
        "structured_rationale_action_commit_packet_forbidden"
    ),
    "root_bypass_claimed": "structured_rationale_root_bypass_forbidden",
}

_RAW_TEXT_MARKERS = (
    "raw_user_text",
    "raw_" + "ge" + "mini_text",
    "raw_cross_role_text",
    "hidden_chain_of_thought",
    "chain_of_thought",
    "private_reasoning",
    "internal_monologue",
)

_UNBOUNDED_DUMP_MARKERS = (
    "full_runner_state_dump",
    "unbounded_context_dump",
    "raw_plan_graph_context",
    "raw_plangraph_context",
)

_SECRET_MARKERS = (
    "api_key",
    "secret",
    "token",
    "password",
    "private_key",
)

_MAX_STRING_LENGTH = 512
_MAX_COLLECTION_LENGTH = 50
_MAX_DEPTH = 8


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _as_bounded_field(value: Any, default: Any) -> Any:
    if value is None:
        value = default
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(value)
    return (value,)


def _default_claims() -> dict[str, Any]:
    return {
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "action_commit_packet_claimed": False,
        "root_bypass_claimed": False,
        "root_final_authority_preserved": True,
        "Root remains final authority": True,
    }


def _validation_result(
    reasons: Iterable[str],
    rationale_type: str | None,
) -> dict[str, Any]:
    reason_tuple = tuple(reasons)
    return {
        "accepted": not reason_tuple,
        "reasons": reason_tuple,
        "rationale_type": rationale_type,
    }


def _rationale_type_value(rationale: Mapping[str, Any]) -> str | None:
    rationale_type = rationale.get("rationale_type")
    if isinstance(rationale_type, str):
        return rationale_type
    return None


def _walk_key_values(
    value: Any,
    *,
    depth: int = 0,
) -> Iterable[tuple[str | None, Any, int]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item, depth
            yield from _walk_key_values(item, depth=depth + 1)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield None, item, depth
            yield from _walk_key_values(item, depth=depth + 1)


def _add_raw_or_secret_reasons(value: Mapping[str, Any], reasons: list[str]) -> None:
    for key, item, _depth in _walk_key_values(value):
        key_text = (key or "").lower()
        value_text = item.lower() if isinstance(item, str) else ""
        for marker in _RAW_TEXT_MARKERS:
            if marker in key_text or marker in value_text:
                _append_reason(reasons, "structured_rationale_raw_text_forbidden")
        for marker in _UNBOUNDED_DUMP_MARKERS:
            if marker in key_text or marker in value_text:
                _append_reason(
                    reasons,
                    "structured_rationale_unbounded_dump_forbidden",
                )
        for marker in _SECRET_MARKERS:
            if marker in key_text or marker in value_text:
                _append_reason(
                    reasons,
                    f"structured_rationale_secret_marker_forbidden:{marker}",
                )


def _add_unbounded_reasons(value: Any, reasons: list[str], *, depth: int = 0) -> None:
    if depth > _MAX_DEPTH:
        _append_reason(reasons, "structured_rationale_unbounded_dump_forbidden")
        return
    if isinstance(value, str):
        if len(value) > _MAX_STRING_LENGTH:
            _append_reason(reasons, "structured_rationale_unbounded_dump_forbidden")
        return
    if isinstance(value, Mapping):
        if len(value) > _MAX_COLLECTION_LENGTH:
            _append_reason(reasons, "structured_rationale_unbounded_dump_forbidden")
        for item in value.values():
            _add_unbounded_reasons(item, reasons, depth=depth + 1)
        return
    if isinstance(value, (list, tuple, set, frozenset)):
        if len(value) > _MAX_COLLECTION_LENGTH:
            _append_reason(reasons, "structured_rationale_unbounded_dump_forbidden")
        for item in value:
            _add_unbounded_reasons(item, reasons, depth=depth + 1)


def _add_common_validation_reasons(
    rationale: Mapping[str, Any],
    *,
    expected_type: str,
    required_fields: Iterable[str],
    explanation_fields: Iterable[str],
) -> list[str]:
    reasons: list[str] = []
    for field in (*_COMMON_REQUIRED_FIELDS, *tuple(required_fields)):
        if field not in rationale:
            _append_reason(
                reasons,
                f"structured_rationale_missing_required_field:{field}",
            )

    rationale_type = rationale.get("rationale_type")
    if rationale_type != expected_type:
        _append_reason(
            reasons,
            f"structured_rationale_unexpected_type:{rationale_type}",
        )
    if rationale.get("schema_version") != STRUCTURED_RATIONALE_SCHEMA_VERSION:
        _append_reason(reasons, "structured_rationale_schema_version_invalid")

    for field, reason in _COMMON_FORBIDDEN_CLAIMS.items():
        if bool(rationale.get(field)):
            _append_reason(reasons, reason)

    if rationale.get("root_review_required") is not True:
        _append_reason(reasons, "root_review_required_must_be_true")
    if rationale.get("root_final_authority_preserved") is not True:
        _append_reason(reasons, "root_final_authority_must_be_preserved")
    if rationale.get("Root remains final authority") is not True:
        _append_reason(reasons, "root_final_authority_must_be_preserved")

    for field in explanation_fields:
        if field == "root_review_required" or field not in rationale:
            continue
        value = rationale[field]
        if isinstance(value, str):
            _append_reason(reasons, "structured_rationale_raw_text_forbidden")
        elif not isinstance(value, (Mapping, list, tuple)):
            _append_reason(reasons, "structured_rationale_unbounded_dump_forbidden")

    _add_raw_or_secret_reasons(rationale, reasons)
    _add_unbounded_reasons(rationale, reasons)
    return reasons


def build_orchestrator_structured_rationale(
    *,
    observed_semantics: Any = None,
    route_selection_reason: Any = None,
    rejected_routes: Any = None,
    required_guards_reasoning: Any = None,
    selected_vector_reasoning: Any = None,
    uncertainty_notes: Any = None,
    authority_boundary: Any = None,
    root_review_required: bool = True,
) -> dict[str, Any]:
    rationale = {
        "rationale_type": ORCHESTRATOR_STRUCTURED_RATIONALE_TYPE,
        "schema_version": STRUCTURED_RATIONALE_SCHEMA_VERSION,
        "observed_semantics": _as_bounded_field(
            observed_semantics,
            (
                {
                    "summary": "bounded semantic observations require Root review",
                    "truth_claimed": False,
                },
            ),
        ),
        "route_selection_reason": _as_bounded_field(
            route_selection_reason,
            (
                {
                    "route": "bounded_review_route",
                    "reason": "route remains advisory until Root review",
                },
            ),
        ),
        "rejected_routes": _as_bounded_field(
            rejected_routes,
            (
                {
                    "route": "direct_action_route",
                    "reason": "direct action is outside bounded proposal authority",
                },
            ),
        ),
        "required_guards_reasoning": _as_bounded_field(
            required_guards_reasoning,
            (
                {
                    "guard": "root_review_required",
                    "reason": "Root remains final authority",
                },
            ),
        ),
        "selected_vector_reasoning": _as_bounded_field(
            selected_vector_reasoning,
            (
                {
                    "vector_scope": "allowed_context_vectors",
                    "reason": "selection is advisory only",
                },
            ),
        ),
        "uncertainty_notes": _as_bounded_field(
            uncertainty_notes,
            (
                {
                    "note": "unresolved facts require bounded review",
                },
            ),
        ),
        "authority_boundary": _as_bounded_field(
            authority_boundary,
            (
                {
                    "role": "orchestrator",
                    "is_root": False,
                    "creates_final_output": False,
                },
            ),
        ),
        "root_review_required": root_review_required,
        "orchestrator_is_root": False,
        "creates_action_commit_packet": False,
        "calls_connectors": False,
        **_default_claims(),
    }
    return rationale


def validate_orchestrator_structured_rationale(rationale: Any) -> dict[str, Any]:
    if not isinstance(rationale, Mapping):
        return _validation_result(
            ("structured_rationale_must_be_mapping",),
            None,
        )

    reasons = _add_common_validation_reasons(
        rationale,
        expected_type=ORCHESTRATOR_STRUCTURED_RATIONALE_TYPE,
        required_fields=(
            *ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
            *ORCHESTRATOR_STRUCTURED_RATIONALE_ROLE_BOUNDARY_FIELDS,
        ),
        explanation_fields=ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
    )
    if bool(rationale.get("orchestrator_is_root")):
        _append_reason(reasons, "orchestrator_is_not_root")
    if bool(rationale.get("creates_action_commit_packet")):
        _append_reason(reasons, "orchestrator_cannot_create_action_commit_packet")
    if bool(rationale.get("calls_connectors")):
        _append_reason(reasons, "orchestrator_cannot_call_connectors")

    return _validation_result(reasons, _rationale_type_value(rationale))


def build_architect_structured_rationale(
    *,
    plan_shape_reason: Any = None,
    node_selection_reasoning: Any = None,
    executor_constraint_reasoning: Any = None,
    forbidden_surface_review: Any = None,
    validator_coverage_reasoning: Any = None,
    return_to_root_path: Any = None,
    uncertainty_notes: Any = None,
    authority_boundary: Any = None,
    root_review_required: bool = True,
) -> dict[str, Any]:
    rationale = {
        "rationale_type": ARCHITECT_STRUCTURED_RATIONALE_TYPE,
        "schema_version": STRUCTURED_RATIONALE_SCHEMA_VERSION,
        "plan_shape_reason": _as_bounded_field(
            plan_shape_reason,
            (
                {
                    "shape": "bounded_plan_graph",
                    "reason": "PlanGraph remains advisory until validated",
                },
            ),
        ),
        "node_selection_reasoning": _as_bounded_field(
            node_selection_reasoning,
            (
                {
                    "node_scope": "allowed_node_kinds",
                    "reason": "nodes must pass contract validation",
                },
            ),
        ),
        "executor_constraint_reasoning": _as_bounded_field(
            executor_constraint_reasoning,
            (
                {
                    "executor_scope": "allowed_executor_ids",
                    "reason": "executor choices are constrained metadata",
                },
            ),
        ),
        "forbidden_surface_review": _as_bounded_field(
            forbidden_surface_review,
            (
                {
                    "surface": "connector_or_action_or_final_output",
                    "status": "blocked",
                },
            ),
        ),
        "validator_coverage_reasoning": _as_bounded_field(
            validator_coverage_reasoning,
            (
                {
                    "validators": (
                        "PlanGraph contract",
                        "Post V&V",
                        "GT/LGT",
                        "Root final authority",
                    ),
                    "reason": "proposal must return upward through validators",
                },
            ),
        ),
        "return_to_root_path": _as_bounded_field(
            return_to_root_path,
            (
                {
                    "path": "proposal_to_validation_to_root",
                    "final_authority": "root_only",
                },
            ),
        ),
        "uncertainty_notes": _as_bounded_field(
            uncertainty_notes,
            (
                {
                    "note": "unresolved facts require Root review",
                },
            ),
        ),
        "authority_boundary": _as_bounded_field(
            authority_boundary,
            (
                {
                    "role": "architect",
                    "is_root": False,
                    "creates_final_output": False,
                },
            ),
        ),
        "root_review_required": root_review_required,
        "architect_is_root": False,
        "creates_action_commit_packet": False,
        "calls_connectors": False,
        **_default_claims(),
    }
    return rationale


def validate_architect_structured_rationale(rationale: Any) -> dict[str, Any]:
    if not isinstance(rationale, Mapping):
        return _validation_result(
            ("structured_rationale_must_be_mapping",),
            None,
        )

    reasons = _add_common_validation_reasons(
        rationale,
        expected_type=ARCHITECT_STRUCTURED_RATIONALE_TYPE,
        required_fields=(
            *ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
            *ARCHITECT_STRUCTURED_RATIONALE_ROLE_BOUNDARY_FIELDS,
        ),
        explanation_fields=ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
    )
    if bool(rationale.get("architect_is_root")):
        _append_reason(reasons, "architect_is_not_root")
    if bool(rationale.get("creates_action_commit_packet")):
        _append_reason(reasons, "architect_cannot_create_action_commit_packet")
    if bool(rationale.get("calls_connectors")):
        _append_reason(reasons, "architect_cannot_call_connectors")

    return _validation_result(reasons, _rationale_type_value(rationale))
