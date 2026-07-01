from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Callable, Mapping

from demo import run_live_provider_adapter_response_capture_v01 as provider_adapter
from hedgehog.context_packets import build_architect_plan_context_packet
from hedgehog.context_packets import build_orchestrator_route_context_packet
from hedgehog.context_packets import validate_architect_plan_context_packet
from hedgehog.context_packets import validate_orchestrator_route_context_packet
from hedgehog.structured_rationale import ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS
from hedgehog.structured_rationale import ARCHITECT_STRUCTURED_RATIONALE_TYPE
from hedgehog.structured_rationale import ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS
from hedgehog.structured_rationale import ORCHESTRATOR_STRUCTURED_RATIONALE_TYPE
from hedgehog.structured_rationale import STRUCTURED_RATIONALE_SCHEMA_VERSION
from hedgehog.structured_rationale import build_architect_structured_rationale
from hedgehog.structured_rationale import build_orchestrator_structured_rationale
from hedgehog.structured_rationale import validate_architect_structured_rationale
from hedgehog.structured_rationale import validate_orchestrator_structured_rationale


TITLE = "LIVE UNKNOWN REQUEST DUAL RICH CONTEXT SPINE v0.1"
ENV_UNKNOWN_REQUEST_LIVE_GEMINI = "HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI"
ENV_UNKNOWN_REQUEST_LIVE_COMPACT_RATIONALE = (
    "HEDGEHOG_UNKNOWN_REQUEST_LIVE_COMPACT_RATIONALE"
)
DEFAULT_MODEL = "gemini-2.5-flash"

ProviderCallable = Callable[[str, str, int, Mapping[str, str]], Any]

UNKNOWN_REQUEST_ALLOWED_ROUTES = (
    "unknown_request_root_review",
    "unknown_request_needs_more_evidence",
    "unknown_request_not_ready",
)

UNKNOWN_REQUEST_ALLOWED_VECTOR_IDS = (
    "unknown_request_semantic_review",
    "external_action_boundary_review",
    "root_final_authority_review",
)

UNKNOWN_REQUEST_REQUIRED_ORCHESTRATOR_GUARDS = (
    "ContextPacket validation",
    "structured rationale validation",
    "route validation",
    "Root final authority",
)

UNKNOWN_REQUEST_REQUIRED_ARCHITECT_VALIDATORS = (
    "ArchitectPlanContextPacket validation",
    "structured rationale validation",
    "PlanGraph contract",
    "ResultProposal boundary",
    "Root final authority",
)

ORCHESTRATOR_REQUIRED_FIELDS = (
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
    "structured_orchestrator_rationale",
)

ARCHITECT_REQUIRED_FIELDS = (
    "proposal_id",
    "source_route_id",
    "selected_vector_ids",
    "plan_nodes",
    "result_proposal_summary",
    "root_recommendation",
    "required_validators",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "structured_architect_rationale",
)

ORCHESTRATOR_COMPACT_REQUIRED_FIELDS = (
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
    "rationale_observed_semantics",
    "rationale_route_selection_reason",
    "rationale_rejected_routes",
    "rationale_required_guards_reasoning",
    "rationale_selected_vector_reasoning",
    "rationale_authority_boundary",
)

ARCHITECT_COMPACT_REQUIRED_FIELDS = (
    "proposal_id",
    "source_route_id",
    "selected_vector_ids",
    "plan_nodes",
    "result_proposal_summary",
    "root_recommendation",
    "required_validators",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "rationale_plan_shape_reason",
    "rationale_node_selection_reasoning",
    "rationale_executor_constraint_reasoning",
    "rationale_forbidden_surface_review",
    "rationale_validator_coverage_reasoning",
    "rationale_return_to_root_path",
    "rationale_authority_boundary",
)

COUNTER_KEYS = (
    "orchestrator_provider_call_count",
    "architect_provider_call_count",
    "live_model_call_count",
    "network_used_count",
    "gemini_called_count",
    "action_permission_created_count",
    "action_commit_packet_created_count",
    "connector_called_count",
    "real_world_effects_count",
    "final_output_created_by_root_count",
    "final_output_created_by_non_root_count",
    "context_packet_validated_count",
    "structured_rationale_validated_count",
    "compact_adapter_used_count",
    "compact_adapter_expanded_orchestrator_count",
    "compact_adapter_expanded_architect_count",
    "root_final_authority_preserved_count",
)

FORBIDDEN_ORCHESTRATOR_CLAIMS = {
    "truth_claimed": "orchestrator_truth_claim_forbidden",
    "authority_claimed": "orchestrator_authority_claim_forbidden",
    "action_permission_claimed": "orchestrator_action_claim_forbidden",
    "final_output_claimed": "orchestrator_final_output_claim_forbidden",
    "connector_command_claimed": "orchestrator_connector_claim_forbidden",
    "drs_write_claimed": "orchestrator_drs_write_claim_forbidden",
    "plan_graph_claimed": "orchestrator_plan_graph_claim_forbidden",
    "bypass_root_claimed": "orchestrator_root_bypass_claim_forbidden",
}

FORBIDDEN_ARCHITECT_CLAIMS = {
    "truth_claimed": "architect_truth_claim_forbidden",
    "authority_claimed": "architect_authority_claim_forbidden",
    "action_permission_claimed": "architect_action_claim_forbidden",
    "final_output_claimed": "architect_final_output_claim_forbidden",
    "connector_command_claimed": "architect_connector_claim_forbidden",
    "drs_write_claimed": "architect_drs_write_claim_forbidden",
    "root_bypass_claimed": "architect_root_bypass_claim_forbidden",
}

STRUCTURED_RATIONALE_COMMON_SCHEMA_FIELDS = (
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

ORCHESTRATOR_STRUCTURED_RATIONALE_SCHEMA_FIELDS = (
    *STRUCTURED_RATIONALE_COMMON_SCHEMA_FIELDS,
    *ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
    "orchestrator_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
)

ARCHITECT_STRUCTURED_RATIONALE_SCHEMA_FIELDS = (
    *STRUCTURED_RATIONALE_COMMON_SCHEMA_FIELDS,
    *ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
    "architect_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
)


def _structured_rationale_schema(
    required_fields: tuple[str, ...],
    explanation_fields: tuple[str, ...],
    role_boolean_fields: tuple[str, ...],
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "rationale_type": {"type": "string"},
        "schema_version": {"type": "string"},
        "root_review_required": {"type": "boolean"},
    }
    for field in STRUCTURED_RATIONALE_COMMON_SCHEMA_FIELDS:
        if field not in ("rationale_type", "schema_version"):
            properties[field] = {"type": "boolean"}
    for field in explanation_fields:
        if field != "root_review_required":
            properties[field] = {"type": "array", "items": {"type": "object"}}
    for field in role_boolean_fields:
        properties[field] = {"type": "boolean"}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(required_fields),
        "properties": properties,
    }


def _compact_rationale_array_schema() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "object"}}

ORCHESTRATOR_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": list(ORCHESTRATOR_REQUIRED_FIELDS),
    "properties": {
        "proposal_id": {"type": "string"},
        "suggested_route": {"type": "string"},
        "selected_vector_ids": {"type": "array", "items": {"type": "string"}},
        "required_guards": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
        "confidence": {"type": "number"},
        "needs_review": {"type": "boolean"},
        "uncertainty_notes": {"type": "array", "items": {"type": "string"}},
        "root_review_required": {"type": "boolean"},
        "truth_claimed": {"type": "boolean"},
        "authority_claimed": {"type": "boolean"},
        "action_permission_claimed": {"type": "boolean"},
        "final_output_claimed": {"type": "boolean"},
        "connector_command_claimed": {"type": "boolean"},
        "drs_write_claimed": {"type": "boolean"},
        "plan_graph_claimed": {"type": "boolean"},
        "bypass_root_claimed": {"type": "boolean"},
        "structured_orchestrator_rationale": _structured_rationale_schema(
            ORCHESTRATOR_STRUCTURED_RATIONALE_SCHEMA_FIELDS,
            ORCHESTRATOR_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
            (
                "orchestrator_is_root",
                "creates_action_commit_packet",
                "calls_connectors",
            ),
        ),
    },
}

ORCHESTRATOR_COMPACT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": list(ORCHESTRATOR_COMPACT_REQUIRED_FIELDS),
    "properties": {
        "proposal_id": {"type": "string"},
        "suggested_route": {"type": "string"},
        "selected_vector_ids": {"type": "array", "items": {"type": "string"}},
        "required_guards": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
        "confidence": {"type": "number"},
        "needs_review": {"type": "boolean"},
        "uncertainty_notes": {"type": "array", "items": {"type": "string"}},
        "root_review_required": {"type": "boolean"},
        "truth_claimed": {"type": "boolean"},
        "authority_claimed": {"type": "boolean"},
        "action_permission_claimed": {"type": "boolean"},
        "final_output_claimed": {"type": "boolean"},
        "connector_command_claimed": {"type": "boolean"},
        "drs_write_claimed": {"type": "boolean"},
        "plan_graph_claimed": {"type": "boolean"},
        "bypass_root_claimed": {"type": "boolean"},
        "rationale_observed_semantics": _compact_rationale_array_schema(),
        "rationale_route_selection_reason": _compact_rationale_array_schema(),
        "rationale_rejected_routes": _compact_rationale_array_schema(),
        "rationale_required_guards_reasoning": _compact_rationale_array_schema(),
        "rationale_selected_vector_reasoning": _compact_rationale_array_schema(),
        "rationale_authority_boundary": _compact_rationale_array_schema(),
    },
}

ARCHITECT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": list(ARCHITECT_REQUIRED_FIELDS),
    "properties": {
        "proposal_id": {"type": "string"},
        "source_route_id": {"type": "string"},
        "selected_vector_ids": {"type": "array", "items": {"type": "string"}},
        "plan_nodes": {"type": "array"},
        "result_proposal_summary": {"type": "string"},
        "root_recommendation": {"type": "string"},
        "required_validators": {"type": "array", "items": {"type": "string"}},
        "truth_claimed": {"type": "boolean"},
        "authority_claimed": {"type": "boolean"},
        "action_permission_claimed": {"type": "boolean"},
        "final_output_claimed": {"type": "boolean"},
        "connector_command_claimed": {"type": "boolean"},
        "drs_write_claimed": {"type": "boolean"},
        "root_bypass_claimed": {"type": "boolean"},
        "structured_architect_rationale": _structured_rationale_schema(
            ARCHITECT_STRUCTURED_RATIONALE_SCHEMA_FIELDS,
            ARCHITECT_STRUCTURED_RATIONALE_REQUIRED_FIELDS,
            (
                "architect_is_root",
                "creates_action_commit_packet",
                "calls_connectors",
            ),
        ),
    },
}

ARCHITECT_COMPACT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": list(ARCHITECT_COMPACT_REQUIRED_FIELDS),
    "properties": {
        "proposal_id": {"type": "string"},
        "source_route_id": {"type": "string"},
        "selected_vector_ids": {"type": "array", "items": {"type": "string"}},
        "plan_nodes": {"type": "array", "items": {"type": "object"}},
        "result_proposal_summary": {"type": "string"},
        "root_recommendation": {"type": "string"},
        "required_validators": {"type": "array", "items": {"type": "string"}},
        "truth_claimed": {"type": "boolean"},
        "authority_claimed": {"type": "boolean"},
        "action_permission_claimed": {"type": "boolean"},
        "final_output_claimed": {"type": "boolean"},
        "connector_command_claimed": {"type": "boolean"},
        "drs_write_claimed": {"type": "boolean"},
        "root_bypass_claimed": {"type": "boolean"},
        "rationale_plan_shape_reason": _compact_rationale_array_schema(),
        "rationale_node_selection_reasoning": _compact_rationale_array_schema(),
        "rationale_executor_constraint_reasoning": _compact_rationale_array_schema(),
        "rationale_forbidden_surface_review": _compact_rationale_array_schema(),
        "rationale_validator_coverage_reasoning": _compact_rationale_array_schema(),
        "rationale_return_to_root_path": _compact_rationale_array_schema(),
        "rationale_authority_boundary": _compact_rationale_array_schema(),
    },
}


def _empty_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def _observed_env(env: Mapping[str, str] | None) -> dict[str, str]:
    if env is None:
        return dict(os.environ)
    return dict(env)


def _live_enabled(env: Mapping[str, str]) -> bool:
    return env.get(ENV_UNKNOWN_REQUEST_LIVE_GEMINI) == "1"


def _compact_rationale_enabled(
    env: Mapping[str, str],
    *,
    real_live_provider_path: bool,
) -> bool:
    raw = env.get(ENV_UNKNOWN_REQUEST_LIVE_COMPACT_RATIONALE, "").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    if raw in ("1", "true", "yes", "on"):
        return True
    return real_live_provider_path and _live_enabled(env)


def _provider_model(env: Mapping[str, str]) -> str:
    return env.get(provider_adapter.ENV_PROVIDER_MODEL, "").strip() or DEFAULT_MODEL


def _provider_name(env: Mapping[str, str]) -> str:
    return env.get(provider_adapter.ENV_PROVIDER_NAME, "gemini").strip().lower() or "gemini"


def _provider_reason(exc: provider_adapter.ProviderCaptureError) -> str:
    reason = str(exc).strip()
    if reason in (
        "provider_sdk_or_key_missing",
        "provider_empty_response",
        "provider_timeout_not_supported",
    ):
        return reason
    return getattr(exc, "reason_code", "provider_call_failed")


def _json_response(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("provider_empty_response")
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("provider_response_must_be_object")
    return parsed


def _provider_response_shape(
    response: Mapping[str, Any] | None,
    *,
    rationale_key: str,
) -> dict[str, Any]:
    if not isinstance(response, Mapping):
        return {
            "top_level_keys": (),
            f"{rationale_key}_type": None,
            f"{rationale_key}_keys": (),
        }
    rationale = response.get(rationale_key)
    rationale_type = type(rationale).__name__ if rationale is not None else None
    rationale_keys: tuple[str, ...] = ()
    if isinstance(rationale, Mapping):
        rationale_keys = tuple(sorted(str(key) for key in rationale.keys()))
    return {
        "top_level_keys": tuple(sorted(str(key) for key in response.keys())),
        f"{rationale_key}_type": rationale_type,
        f"{rationale_key}_keys": rationale_keys,
    }


def _provider_error_shape(exc: BaseException | None) -> dict[str, Any]:
    if exc is None:
        return {}
    source = exc.__cause__ if exc.__cause__ is not None else exc
    message = str(source).replace("\n", " ").strip()
    lower_message = message.lower()
    if any(marker in lower_message for marker in ("api_key", "token", "secret")):
        message = "[redacted_provider_error_message]"
    return {
        "exception_type": source.__class__.__name__,
        "exception_module": source.__class__.__module__,
        "message_prefix": message[:200],
    }


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _system_instruction(role: str) -> str:
    return (
        f"Return JSON only for the bounded {role} proposal. "
        "The proposal is not truth, not authority, not action permission, "
        "not FinalOutput, not ActionCommitPacket, and not a connector command. "
        "Gemini proposes, Root disposes. Root remains final authority."
    )


def _gemini_http_options(timeout_seconds: int) -> object | None:
    try:
        from google.genai import types
    except ImportError as exc:
        raise provider_adapter.ProviderCaptureError(
            "provider_timeout_not_supported"
        ) from exc

    http_options_cls = getattr(types, "HttpOptions", None)
    if http_options_cls is None:
        raise provider_adapter.ProviderCaptureError("provider_timeout_not_supported")
    try:
        return http_options_cls(timeout=max(1, int(timeout_seconds)) * 1000)
    except Exception as exc:
        raise provider_adapter.ProviderCaptureError(
            "provider_timeout_not_supported"
        ) from exc


def _timeout_exception_types() -> tuple[type[BaseException], ...]:
    exception_types: list[type[BaseException]] = [TimeoutError]
    try:
        import httpx

        exception_types.append(httpx.TimeoutException)
    except Exception:
        pass
    try:
        import httpcore

        exception_types.append(httpcore.TimeoutException)
    except Exception:
        pass
    return tuple(exception_types)


def _is_timeout_exception(
    exc: BaseException,
    *,
    timeout_seconds: int | None = None,
    elapsed_seconds: float | None = None,
) -> bool:
    if isinstance(exc, _timeout_exception_types()):
        return True
    class_name = exc.__class__.__name__.lower()
    module_name = exc.__class__.__module__.lower()
    message = str(exc).lower()
    descriptor = f"{class_name} {module_name} {message}"
    timeout_markers = ("timeout", "timed out", "deadline", "read timeout")
    if "timeout" in class_name and ("google" in module_name or "genai" in module_name):
        return True
    return (
        timeout_seconds is not None
        and elapsed_seconds is not None
        and elapsed_seconds >= max(1, timeout_seconds) * 0.9
        and any(marker in descriptor for marker in timeout_markers)
    )


def _call_live_gemini_provider(
    *,
    prompt: str,
    model_name: str,
    timeout_seconds: int,
    env: Mapping[str, str],
    response_schema: Mapping[str, Any],
    role: str,
) -> str:
    api_key = provider_adapter._gemini_api_key(env)
    if not api_key:
        raise provider_adapter.ProviderCaptureError("provider_sdk_or_key_missing")
    started_at = time.monotonic()
    try:
        from google import genai
    except ImportError as exc:
        raise provider_adapter.ProviderCaptureError("provider_sdk_or_key_missing") from exc

    http_options = _gemini_http_options(timeout_seconds)
    if http_options is None:
        raise provider_adapter.ProviderCaptureError("provider_timeout_not_supported")

    def generation_config(schema_key: str | None) -> dict[str, Any]:
        config: dict[str, Any] = {
            "response_mime_type": "application/json",
            "temperature": 0,
            "candidate_count": 1,
            "system_instruction": _system_instruction(role),
        }
        if schema_key is not None:
            config[schema_key] = dict(response_schema)
        return config

    try:
        try:
            client = genai.Client(api_key=api_key, http_options=http_options)
        except TypeError as exc:
            raise provider_adapter.ProviderCaptureError(
                "provider_timeout_not_supported"
            ) from exc
        response = None
        for schema_key in ("response_json_schema", "response_schema", None):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=generation_config(schema_key),
                )
                break
            except (TypeError, ValueError):
                if schema_key is None:
                    raise
                continue
        if response is None:
            raise provider_adapter.ProviderCaptureError("provider_call_failed")
    except provider_adapter.ProviderCaptureError:
        raise
    except Exception as exc:  # pragma: no cover - real provider path only
        elapsed = time.monotonic() - started_at
        if _is_timeout_exception(
            exc,
            timeout_seconds=timeout_seconds,
            elapsed_seconds=elapsed,
        ):
            raise provider_adapter.ProviderTimeoutError("provider_timeout") from exc
        raise provider_adapter.ProviderCaptureError("provider_call_failed") from exc

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, dict):
        return json.dumps(parsed, sort_keys=True)
    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        raise provider_adapter.ProviderCaptureError("provider_empty_response")
    return text


def _semantic_intake_context(request_text: str) -> dict[str, Any]:
    return {
        "context_type": "semantic_intake_context",
        "raw_user_request": request_text,
        "request_length": len(request_text),
        "unknown_request": True,
        "root_review_required": True,
        "external_action_permission_created": False,
        "ContextPacket is not truth": True,
        "ContextPacket is not authority": True,
        "Gemini proposes, Root disposes": True,
        "Root remains final authority": True,
    }


def _orchestrator_provider_context(request_text: str) -> dict[str, Any]:
    return {
        "context_type": "bounded_unknown_request_orchestrator_input",
        "raw_user_request": request_text,
        "allowed_routes": UNKNOWN_REQUEST_ALLOWED_ROUTES,
        "allowed_vector_ids": UNKNOWN_REQUEST_ALLOWED_VECTOR_IDS,
        "required_guards": UNKNOWN_REQUEST_REQUIRED_ORCHESTRATOR_GUARDS,
        "ContextPacket is not truth": True,
        "ContextPacket is not authority": True,
        "structured rationale is explanation only": True,
        "Gemini proposes, Root disposes": True,
        "Root remains final authority": True,
    }


def _orchestrator_structured_rationale_skeleton(
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return build_orchestrator_structured_rationale(
        observed_semantics=(
            {
                "summary": "raw unknown request requires bounded semantic review",
                "candidate_only": True,
                "rationale_type": ORCHESTRATOR_STRUCTURED_RATIONALE_TYPE,
                "schema_version": STRUCTURED_RATIONALE_SCHEMA_VERSION,
            },
        ),
        route_selection_reason=(
            {
                "allowed_routes": tuple(context.get("allowed_routes") or ()),
                "selected_route": "unknown_request_root_review",
                "reason": "Gemini may propose only an allowed route for Root review",
            },
        ),
        rejected_routes=(
            {
                "route": "direct_real_world_action",
                "reason": "external action is outside Orchestrator authority",
            },
        ),
        required_guards_reasoning=tuple(
            {"guard": guard, "status": "required"}
            for guard in tuple(context.get("required_guards") or ())
        ),
        selected_vector_reasoning=(
            {
                "allowed_vector_ids": tuple(context.get("allowed_vector_ids") or ()),
                "selected_vector_ids": ("unknown_request_semantic_review",),
                "reason": "vectors are advisory and must remain allowed",
            },
        ),
        uncertainty_notes=(
            {"note": "unknown request remains subject to Root review"},
        ),
        authority_boundary=(
            {
                "ContextPacket is not truth": True,
                "ContextPacket is not authority": True,
                "structured rationale is explanation only": True,
                "Orchestrator is not Root": True,
                "Gemini proposes, Root disposes": True,
                "Root remains final authority": True,
            },
        ),
    )


def _orchestrator_prompt(context: Mapping[str, Any]) -> str:
    skeleton = {
        "proposal_id": "orchestrator-proposal-unknown-request-001",
        "suggested_route": "unknown_request_root_review",
        "selected_vector_ids": ["unknown_request_semantic_review"],
        "required_guards": list(context["required_guards"]),
        "reason": "bounded route proposal only",
        "confidence": 0.0,
        "needs_review": True,
        "uncertainty_notes": [],
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "structured_orchestrator_rationale": (
            _orchestrator_structured_rationale_skeleton(context)
        ),
    }
    return "\n".join(
        (
            TITLE,
            "Role: bounded Gemini Orchestrator.",
            "Return one JSON object matching the skeleton.",
            "structured_orchestrator_rationale MUST be a complete JSON object.",
            "structured_orchestrator_rationale MUST NOT be null.",
            "structured_orchestrator_rationale MUST include every field shown in the skeleton.",
            "Structured rationale is explanation only, not hidden chain-of-thought.",
            "Structured rationale is not truth, not authority, not action permission, not FinalOutput, not ActionCommitPacket, and not connector command.",
            "Do not create a PlanGraph, FinalOutput, ActionCommitPacket, or connector command.",
            "Gemini proposes, Root disposes.",
            "Root remains final authority.",
            "",
            "JSON skeleton:",
            json.dumps(skeleton, indent=2, sort_keys=True),
            "",
            "BOUNDED_UNKNOWN_REQUEST_ORCHESTRATOR_INPUT_JSON:",
            json.dumps(context, indent=2, sort_keys=True),
        )
    )


def _orchestrator_compact_prompt(context: Mapping[str, Any]) -> str:
    skeleton = {
        "proposal_id": "orchestrator-proposal-unknown-request-001",
        "suggested_route": "unknown_request_root_review",
        "selected_vector_ids": ["unknown_request_semantic_review"],
        "required_guards": list(context["required_guards"]),
        "reason": "bounded route proposal only",
        "confidence": 0.0,
        "needs_review": True,
        "uncertainty_notes": ["unknown request requires Root review"],
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "rationale_observed_semantics": [
            {"summary": "bounded semantic observation only"}
        ],
        "rationale_route_selection_reason": [
            {"route": "unknown_request_root_review", "reason": "requires Root review"}
        ],
        "rationale_rejected_routes": [
            {"route": "direct_real_world_action", "reason": "not allowed"}
        ],
        "rationale_required_guards_reasoning": [
            {"guard": guard, "status": "required"}
            for guard in tuple(context.get("required_guards") or ())
        ],
        "rationale_selected_vector_reasoning": [
            {
                "vector": "unknown_request_semantic_review",
                "reason": "allowed advisory vector",
            }
        ],
        "rationale_authority_boundary": [
            {
                "Orchestrator is not Root": True,
                "Gemini proposes, Root disposes": True,
                "Root remains final authority": True,
            }
        ],
    }
    return "\n".join(
        (
            TITLE,
            "Role: bounded Gemini Orchestrator.",
            "Return compact JSON only matching the skeleton.",
            "Do not include structured_orchestrator_rationale directly.",
            "The runtime will build canonical structured rationale envelope locally.",
            "No action permission, no connector command, no FinalOutput.",
            "Gemini proposes, Root disposes.",
            "Root remains final authority.",
            "",
            "JSON skeleton:",
            json.dumps(skeleton, indent=2, sort_keys=True),
            "",
            "BOUNDED_UNKNOWN_REQUEST_ORCHESTRATOR_INPUT_JSON:",
            json.dumps(context, indent=2, sort_keys=True),
        )
    )


def _architect_provider_context(
    *,
    route_packet: Mapping[str, Any],
    route_validation: Mapping[str, Any],
    orchestrator_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    selected = tuple(orchestrator_proposal.get("selected_vector_ids") or ())
    return {
        "context_type": "bounded_unknown_request_architect_input",
        "input_route_source": "validated_orchestrator_route",
        "source_route_id": str(orchestrator_proposal.get("suggested_route") or ""),
        "selected_vector_ids": selected,
        "route_packet_type": route_packet.get("packet_type"),
        "route_packet_validation_accepted": bool(route_validation.get("accepted")),
        "orchestrator_proposal_id": orchestrator_proposal.get("proposal_id"),
        "allowed_executor_ids": ("local_unknown_request_review_executor",),
        "allowed_node_kinds": ("semantic_review", "root_review_gate"),
        "required_validators": UNKNOWN_REQUEST_REQUIRED_ARCHITECT_VALIDATORS,
        "raw_user_request_present": False,
        "raw_cross_role_text_present": False,
        "PlanGraph is not authority": True,
        "ResultProposal is not FinalOutput": True,
        "Gemini proposes, Root disposes": True,
        "Root remains final authority": True,
    }


def _architect_structured_rationale_skeleton(
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return build_architect_structured_rationale(
        plan_shape_reason=(
            {
                "shape": "bounded_unknown_request_plan_graph",
                "source_route_id": context.get("source_route_id"),
                "reason": "PlanGraph remains non-authority and bounded",
            },
        ),
        node_selection_reasoning=(
            {
                "allowed_node_kinds": tuple(context.get("allowed_node_kinds") or ()),
                "selected_vector_ids": tuple(context.get("selected_vector_ids") or ()),
                "reason": "nodes must stay inside validated route context",
            },
        ),
        executor_constraint_reasoning=(
            {
                "allowed_executor_ids": tuple(context.get("allowed_executor_ids") or ()),
                "reason": "executor selection is constrained metadata only",
            },
        ),
        forbidden_surface_review=(
            {
                "forbidden_surfaces": (
                    "action_permission",
                    "connector_command",
                    "final_output",
                ),
                "status": "blocked",
            },
        ),
        validator_coverage_reasoning=tuple(
            {"validator": validator, "status": "required"}
            for validator in tuple(context.get("required_validators") or ())
        ),
        return_to_root_path=(
            {
                "path": "Architect proposal to validation to Root boundary",
                "ResultProposal is not FinalOutput": True,
                "Root remains final authority": True,
            },
        ),
        uncertainty_notes=(
            {"note": "unknown request remains subject to Root review"},
        ),
        authority_boundary=(
            {
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
                "structured rationale is explanation only": True,
                "Gemini proposes, Root disposes": True,
                "Root remains final authority": True,
            },
        ),
    )


def _architect_prompt(context: Mapping[str, Any]) -> str:
    skeleton = {
        "proposal_id": "architect-proposal-unknown-request-001",
        "source_route_id": context["source_route_id"],
        "selected_vector_ids": list(context["selected_vector_ids"]),
        "plan_nodes": [
            {
                "node_id": "node:unknown_request_semantic_review",
                "kind": "semantic_review",
                "executor_id": "local_unknown_request_review_executor",
                "expected_output": "ResultProposal",
            }
        ],
        "result_proposal_summary": "Return a non-final ResultProposal for Root review.",
        "root_recommendation": "needs_more_evidence",
        "required_validators": list(context["required_validators"]),
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
        "structured_architect_rationale": (
            _architect_structured_rationale_skeleton(context)
        ),
    }
    return "\n".join(
        (
            TITLE,
            "Role: bounded Gemini Architect.",
            "Return one JSON object matching the skeleton.",
            "structured_architect_rationale MUST be a complete JSON object.",
            "structured_architect_rationale MUST NOT be null.",
            "structured_architect_rationale MUST include every field shown in the skeleton.",
            "Structured rationale is explanation only, not hidden chain-of-thought.",
            "Structured rationale is not truth, not authority, not action permission, not FinalOutput, not ActionCommitPacket, and not connector command.",
            "Do not create FinalOutput, ActionCommitPacket, action permission, or connector command.",
            "PlanGraph is not authority.",
            "ResultProposal is not FinalOutput.",
            "Gemini proposes, Root disposes.",
            "Root remains final authority.",
            "",
            "JSON skeleton:",
            json.dumps(skeleton, indent=2, sort_keys=True),
            "",
            "BOUNDED_UNKNOWN_REQUEST_ARCHITECT_INPUT_JSON:",
            json.dumps(context, indent=2, sort_keys=True),
        )
    )


def _architect_compact_prompt(context: Mapping[str, Any]) -> str:
    skeleton = {
        "proposal_id": "architect-proposal-unknown-request-001",
        "source_route_id": context["source_route_id"],
        "selected_vector_ids": list(context["selected_vector_ids"]),
        "plan_nodes": [
            {
                "node_id": "node:unknown_request_semantic_review",
                "kind": "semantic_review",
                "executor_id": "local_unknown_request_review_executor",
                "expected_output": "ResultProposal",
            }
        ],
        "result_proposal_summary": "Return a non-final ResultProposal for Root review.",
        "root_recommendation": "needs_more_evidence",
        "required_validators": list(context["required_validators"]),
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
        "rationale_plan_shape_reason": [
            {"shape": "bounded_unknown_request_plan_graph", "reason": "review only"}
        ],
        "rationale_node_selection_reasoning": [
            {"node": "node:unknown_request_semantic_review", "reason": "bounded review"}
        ],
        "rationale_executor_constraint_reasoning": [
            {
                "executor": "local_unknown_request_review_executor",
                "reason": "allowed executor only",
            }
        ],
        "rationale_forbidden_surface_review": [
            {"surface": "action_or_connector_or_final", "status": "blocked"}
        ],
        "rationale_validator_coverage_reasoning": [
            {"validator": validator, "status": "required"}
            for validator in tuple(context.get("required_validators") or ())
        ],
        "rationale_return_to_root_path": [
            {"path": "proposal_to_root_boundary", "status": "required"}
        ],
        "rationale_authority_boundary": [
            {
                "Architect is not Root": True,
                "PlanGraph is not authority": True,
                "Root remains final authority": True,
            }
        ],
    }
    return "\n".join(
        (
            TITLE,
            "Role: bounded Gemini Architect.",
            "Return compact JSON only matching the skeleton.",
            "Do not include structured_architect_rationale directly.",
            "The runtime will build canonical structured rationale envelope locally.",
            "No action permission, no connector command, no FinalOutput.",
            "PlanGraph is not authority.",
            "ResultProposal is not FinalOutput.",
            "Gemini proposes, Root disposes.",
            "Root remains final authority.",
            "",
            "JSON skeleton:",
            json.dumps(skeleton, indent=2, sort_keys=True),
            "",
            "BOUNDED_UNKNOWN_REQUEST_ARCHITECT_INPUT_JSON:",
            json.dumps(context, indent=2, sort_keys=True),
        )
    )


def _expand_orchestrator_compact_proposal(
    compact: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    expanded = dict(compact)
    expanded["structured_orchestrator_rationale"] = (
        build_orchestrator_structured_rationale(
            observed_semantics=compact.get("rationale_observed_semantics"),
            route_selection_reason=compact.get("rationale_route_selection_reason"),
            rejected_routes=compact.get("rationale_rejected_routes"),
            required_guards_reasoning=compact.get(
                "rationale_required_guards_reasoning"
            ),
            selected_vector_reasoning=compact.get(
                "rationale_selected_vector_reasoning"
            ),
            uncertainty_notes=compact.get("uncertainty_notes"),
            authority_boundary=compact.get("rationale_authority_boundary"),
            root_review_required=True,
        )
    )
    expanded["structured_orchestrator_rationale"]["authority_boundary"] = tuple(
        expanded["structured_orchestrator_rationale"].get("authority_boundary") or ()
    ) + (
        {
            "ContextPacket is not truth": True,
            "ContextPacket is not authority": True,
            "runtime_expanded_compact_rationale": True,
            "Root remains final authority": True,
            "allowed_routes": tuple(context.get("allowed_routes") or ()),
        },
    )
    return expanded


def _expand_architect_compact_proposal(
    compact: Mapping[str, Any],
    architect_context: Mapping[str, Any],
) -> dict[str, Any]:
    expanded = dict(compact)
    expanded["structured_architect_rationale"] = build_architect_structured_rationale(
        plan_shape_reason=compact.get("rationale_plan_shape_reason"),
        node_selection_reasoning=compact.get("rationale_node_selection_reasoning"),
        executor_constraint_reasoning=compact.get(
            "rationale_executor_constraint_reasoning"
        ),
        forbidden_surface_review=compact.get("rationale_forbidden_surface_review"),
        validator_coverage_reasoning=compact.get(
            "rationale_validator_coverage_reasoning"
        ),
        return_to_root_path=compact.get("rationale_return_to_root_path"),
        uncertainty_notes=(
            {
                "note": "compact Architect proposal remains subject to Root review",
                "source_route_id": architect_context.get("source_route_id"),
            },
        ),
        authority_boundary=compact.get("rationale_authority_boundary"),
        root_review_required=True,
    )
    expanded["structured_architect_rationale"]["authority_boundary"] = tuple(
        expanded["structured_architect_rationale"].get("authority_boundary") or ()
    ) + (
        {
            "PlanGraph is not authority": True,
            "ResultProposal is not FinalOutput": True,
            "runtime_expanded_compact_rationale": True,
            "Root remains final authority": True,
        },
    )
    return expanded


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"missing_required_field:{field}" for field in required if field not in payload)


def _claim_errors(
    payload: Mapping[str, Any],
    forbidden: Mapping[str, str],
) -> tuple[str, ...]:
    return tuple(reason for field, reason in forbidden.items() if bool(payload.get(field)))


def _validate_orchestrator_semantic_contract(
    proposal: Mapping[str, Any],
    context: Mapping[str, Any],
) -> tuple[str, ...]:
    errors: list[str] = []
    allowed_routes = set(context.get("allowed_routes") or ())
    if proposal.get("suggested_route") not in allowed_routes:
        errors.append("suggested_route_not_allowed")

    allowed_vector_ids = set(context.get("allowed_vector_ids") or ())
    selected_vector_ids = set(proposal.get("selected_vector_ids") or ())
    if not selected_vector_ids.issubset(allowed_vector_ids):
        errors.append("selected_vector_ids_must_be_subset_of_allowed_vector_ids")

    guards = set(proposal.get("required_guards") or ())
    for guard in UNKNOWN_REQUEST_REQUIRED_ORCHESTRATOR_GUARDS:
        if guard not in guards:
            errors.append(f"missing_required_guard:{guard}")

    if proposal.get("root_review_required") is not True:
        errors.append("root_review_required_must_be_true")
    return tuple(errors)


_ACTION_SURFACE_MARKERS = (
    "action_permission",
    "action_permission_claimed",
    "real_world_effect",
    "external_action",
    "action " + "permission",
    "real " + "world " + "effect",
    "external " + "action",
    "door " + "access",
    "dispatch " + "robot",
)

_CONNECTOR_SURFACE_MARKERS = (
    "connector_command",
    "connector_command_claimed",
    "connector " + "command",
    "robot_api",
)

_FINAL_OUTPUT_SURFACE_MARKERS = (
    "final_output",
    "final_output_claimed",
    "final " + "output",
)


def _walk_surface_values(value: Any) -> tuple[tuple[str | None, Any], ...]:
    pairs: list[tuple[str | None, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key == "structured_architect_rationale":
                continue
            pairs.append((str(key), item))
            pairs.extend(_walk_surface_values(item))
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            pairs.extend(_walk_surface_values(item))
    return tuple(pairs)


def _surface_marker_present(
    key: str | None,
    value: Any,
    markers: tuple[str, ...],
) -> bool:
    key_text = (key or "").lower()
    value_text = value.lower() if isinstance(value, str) else ""
    if isinstance(value, bool) and value is False:
        value_text = ""
    for marker in markers:
        marker_text = marker.lower()
        if marker_text in value_text:
            return True
        if marker_text in key_text and value is not False:
            return True
    return False


def _contains_forbidden_plan_surface(
    value: Any,
    markers: tuple[str, ...],
) -> bool:
    return any(
        _surface_marker_present(key, item, markers)
        for key, item in _walk_surface_values(value)
    )


def _validate_architect_plan_surface(proposal: Mapping[str, Any]) -> tuple[str, ...]:
    inspected = {
        "plan_nodes": proposal.get("plan_nodes", ()),
        "result_proposal_summary": proposal.get("result_proposal_summary"),
        "root_recommendation": proposal.get("root_recommendation"),
    }
    errors: list[str] = []
    if _contains_forbidden_plan_surface(inspected, _ACTION_SURFACE_MARKERS):
        errors.append("architect_plan_action_surface_forbidden")
    if _contains_forbidden_plan_surface(inspected, _CONNECTOR_SURFACE_MARKERS):
        errors.append("architect_plan_connector_surface_forbidden")
    if _contains_forbidden_plan_surface(inspected, _FINAL_OUTPUT_SURFACE_MARKERS):
        errors.append("architect_plan_final_output_surface_forbidden")
    return tuple(errors)


def _validate_architect_semantic_contract(
    proposal: Mapping[str, Any],
    architect_context: Mapping[str, Any],
) -> tuple[str, ...]:
    errors: list[str] = []
    if proposal.get("source_route_id") != architect_context.get("source_route_id"):
        errors.append("architect_source_route_id_must_match_validated_route")

    validated_vector_ids = set(architect_context.get("selected_vector_ids") or ())
    proposal_vector_ids = set(proposal.get("selected_vector_ids") or ())
    if not proposal_vector_ids.issubset(validated_vector_ids):
        errors.append(
            "architect_selected_vector_ids_must_be_subset_of_validated_route_vectors"
        )

    validators = set(proposal.get("required_validators") or ())
    for validator in UNKNOWN_REQUEST_REQUIRED_ARCHITECT_VALIDATORS:
        if validator not in validators:
            errors.append(f"missing_required_architect_validator:{validator}")
    return tuple(errors)


def _call_provider(
    *,
    prompt: str,
    role: str,
    env: Mapping[str, str],
    provider: ProviderCallable | None,
    response_schema: Mapping[str, Any],
    counters: dict[str, int],
) -> dict[str, Any]:
    model = _provider_model(env)
    timeout = provider_adapter._timeout_seconds(env)
    if provider is not None:
        raw = provider(prompt, model, timeout, env)
    else:
        if not _live_enabled(env):
            raise provider_adapter.ProviderCaptureError(
                "provider_injection_or_live_gate_required"
            )
        if _provider_name(env) != "gemini":
            raise provider_adapter.ProviderCaptureError("provider_unsupported")
        raw = _call_live_gemini_provider(
            prompt=prompt,
            model_name=model,
            timeout_seconds=timeout,
            env=env,
            response_schema=response_schema,
            role=role,
        )
        counters["live_model_call_count"] += 1
        counters["network_used_count"] += 1
        counters["gemini_called_count"] += 1
    return _json_response(raw)


def _fail_result(
    *,
    request_text: str,
    semantic_context: Mapping[str, Any] | None,
    counters: dict[str, int],
    validation_errors: tuple[str, ...],
    orchestrator_provider_context: Mapping[str, Any] | None = None,
    architect_provider_context: Mapping[str, Any] | None = None,
    orchestrator_route_context_packet: Mapping[str, Any] | None = None,
    orchestrator_route_context_packet_validation: Mapping[str, Any] | None = None,
    structured_orchestrator_rationale: Mapping[str, Any] | None = None,
    structured_orchestrator_rationale_validation: Mapping[str, Any] | None = None,
    architect_plan_context_packet: Mapping[str, Any] | None = None,
    architect_plan_context_packet_validation: Mapping[str, Any] | None = None,
    structured_architect_rationale: Mapping[str, Any] | None = None,
    structured_architect_rationale_validation: Mapping[str, Any] | None = None,
    orchestrator_provider_response_shape: Mapping[str, Any] | None = None,
    architect_provider_response_shape: Mapping[str, Any] | None = None,
    live_provider_stage: str = "not_started",
    last_live_provider_role: str | None = None,
    live_provider_role_in_progress: str | None = None,
    provider_timeout_seconds: int | None = None,
    live_provider_contract_mode: str = "full_structured_rationale",
    provider_error_shape: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "title": TITLE,
        "final_status": "FAIL_CLOSED",
        "raw_user_request": request_text,
        "semantic_intake_context": dict(semantic_context or {}),
        "orchestrator_provider_context": dict(orchestrator_provider_context or {}),
        "orchestrator_route_context_packet": dict(orchestrator_route_context_packet or {}),
        "orchestrator_route_context_packet_validation": dict(
            orchestrator_route_context_packet_validation or {}
        ),
        "structured_orchestrator_rationale": dict(structured_orchestrator_rationale or {}),
        "structured_orchestrator_rationale_validation": dict(
            structured_orchestrator_rationale_validation or {}
        ),
        "architect_provider_context": dict(architect_provider_context or {}),
        "architect_plan_context_packet": dict(architect_plan_context_packet or {}),
        "architect_plan_context_packet_validation": dict(
            architect_plan_context_packet_validation or {}
        ),
        "structured_architect_rationale": dict(structured_architect_rationale or {}),
        "structured_architect_rationale_validation": dict(
            structured_architect_rationale_validation or {}
        ),
        "orchestrator_provider_response_shape": dict(
            orchestrator_provider_response_shape or {}
        ),
        "architect_provider_response_shape": dict(
            architect_provider_response_shape or {}
        ),
        "live_provider_stage": live_provider_stage,
        "last_live_provider_role": last_live_provider_role,
        "live_provider_role_in_progress": live_provider_role_in_progress,
        "provider_timeout_seconds": provider_timeout_seconds,
        "live_provider_contract_mode": live_provider_contract_mode,
        "provider_error_shape": dict(provider_error_shape or {}),
        "plan_graph_context": {},
        "result_proposal": {},
        "root_final_output_boundary": {},
        "counters": counters,
        "validation_errors": validation_errors,
        "pass_conditions": {},
    }


def _route_packet_from_proposal(
    proposal: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    route = str(proposal.get("suggested_route") or "unknown_request_root_review")
    return build_orchestrator_route_context_packet(
        packet_id=f"context_packet:unknown_request:orchestrator:{proposal.get('proposal_id', 'proposal')}",
        created_by="live_unknown_request_dual_rich_context_spine",
        source_refs=({"source": "raw_user_request", "source_id": "unknown_request"},),
        domain="unknown_request",
        allowed_routes=tuple(context.get("allowed_routes") or ()),
        required_guards=tuple(context.get("required_guards") or ()),
        selected_vector_ids=tuple(proposal.get("selected_vector_ids") or ()),
        route_validation_expectations={
            "root_review_required": True,
            "suggested_route": route,
            "suggested_route_allowed": route in tuple(context.get("allowed_routes") or ()),
            "Gemini proposes, Root disposes": True,
        },
    )


def _architect_packet_from_context(
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return build_architect_plan_context_packet(
        packet_id=f"context_packet:unknown_request:architect:{context.get('orchestrator_proposal_id', 'proposal')}",
        created_by="live_unknown_request_dual_rich_context_spine",
        source_refs=(
            {
                "source": "validated_orchestrator_route",
                "source_id": str(context.get("orchestrator_proposal_id") or ""),
            },
        ),
        domain="unknown_request",
        source_route_id=str(context.get("source_route_id") or "unknown_request_root_review"),
        allowed_executor_ids=tuple(context.get("allowed_executor_ids") or ()),
        allowed_node_kinds=tuple(context.get("allowed_node_kinds") or ()),
        required_validators=tuple(context.get("required_validators") or ()),
        forbidden_connector_claims=("connector_command", "external_system_command"),
        forbidden_action_claims=("action_permission", "real_world_effect"),
        forbidden_final_output_claims=("FinalOutput", "root_final_boundary"),
    )


def _plan_graph_from_architect(proposal: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "plan_graph_id": f"plan_graph:{proposal.get('proposal_id', 'unknown_request')}",
        "created_by": "bounded_gemini_architect_proposal",
        "source_route_id": proposal.get("source_route_id"),
        "nodes": tuple(proposal.get("plan_nodes") or ()),
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "creates_final_output": False,
        "PlanGraph is not authority": True,
        "Root remains final authority": True,
    }


def _result_proposal_from_architect(proposal: Mapping[str, Any]) -> dict[str, Any]:
    recommendation = str(proposal.get("root_recommendation") or "needs_more_evidence")
    if recommendation not in ("not_ready", "needs_more_evidence"):
        recommendation = "needs_more_evidence"
    return {
        "proposal_id": f"result_proposal:{proposal.get('proposal_id', 'unknown_request')}",
        "created_by": "bounded_gemini_architect_proposal_adapter",
        "proposal_status": recommendation,
        "summary": str(proposal.get("result_proposal_summary") or ""),
        "is_final_output": False,
        "action_permission_claimed": False,
        "connector_command_claimed": False,
        "ResultProposal is not FinalOutput": True,
        "Root remains final authority": True,
    }


def _root_boundary(
    *,
    request_text: str,
    result_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    decision = str(result_proposal.get("proposal_status") or "needs_more_evidence")
    if decision not in ("not_ready", "needs_more_evidence"):
        decision = "needs_more_evidence"
    return {
        "boundary_id": "root_final_boundary:unknown_request",
        "created_by": "Root",
        "decision": decision,
        "safe_human_summary": (
            "Root reviewed the unknown request through bounded Gemini proposal "
            "roles. No real-world action permission was created."
        ),
        "request_ref_length": len(request_text),
        "action_permission_created": False,
        "action_commit_packet_created": False,
        "connector_called": False,
        "real_world_effects_allowed": False,
        "ResultProposal is not FinalOutput": True,
        "Gemini proposes, Root disposes": True,
        "Root remains final authority": True,
    }


def _pass_conditions(result: Mapping[str, Any]) -> dict[str, bool]:
    counters = result["counters"]
    return {
        "orchestrator_packet_validated": result[
            "orchestrator_route_context_packet_validation"
        ].get("accepted")
        is True,
        "architect_packet_validated": result[
            "architect_plan_context_packet_validation"
        ].get("accepted")
        is True,
        "orchestrator_rationale_validated": result[
            "structured_orchestrator_rationale_validation"
        ].get("accepted")
        is True,
        "architect_rationale_validated": result[
            "structured_architect_rationale_validation"
        ].get("accepted")
        is True,
        "architect_consumes_validated_route": result["architect_provider_context"].get(
            "route_packet_validation_accepted"
        )
        is True,
        "plan_graph_not_authority": result["plan_graph_context"].get(
            "PlanGraph is not authority"
        )
        is True,
        "result_proposal_not_final_output": result["result_proposal"].get(
            "ResultProposal is not FinalOutput"
        )
        is True,
        "root_final_authority": result["root_final_output_boundary"].get(
            "Root remains final authority"
        )
        is True,
        "action_counters_zero": all(
            counters[key] == 0
            for key in (
                "action_permission_created_count",
                "action_commit_packet_created_count",
                "connector_called_count",
                "real_world_effects_count",
            )
        ),
    }


def run_live_unknown_request_dual_rich_context(
    request_text: str,
    env: Mapping[str, str] | None = None,
    orchestrator_provider: ProviderCallable | None = None,
    architect_provider: ProviderCallable | None = None,
) -> dict[str, Any]:
    observed_env = _observed_env(env)
    counters = _empty_counters()
    request = (request_text or "").strip()
    semantic_context = _semantic_intake_context(request) if request else {}
    orchestrator_response_shape: dict[str, Any] = {}
    architect_response_shape: dict[str, Any] = {}
    provider_timeout_seconds = provider_adapter._timeout_seconds(observed_env)
    live_provider_stage = "not_started"
    last_live_provider_role: str | None = None
    live_provider_role_in_progress: str | None = None
    provider_error_shape: dict[str, Any] = {}
    compact_mode = _compact_rationale_enabled(
        observed_env,
        real_live_provider_path=(
            orchestrator_provider is None or architect_provider is None
        ),
    )
    live_provider_contract_mode = (
        "compact_rationale_adapter" if compact_mode else "full_structured_rationale"
    )
    if compact_mode:
        counters["compact_adapter_used_count"] = 1

    def fail(**kwargs: Any) -> dict[str, Any]:
        return _fail_result(
            provider_timeout_seconds=provider_timeout_seconds,
            live_provider_stage=live_provider_stage,
            last_live_provider_role=last_live_provider_role,
            live_provider_role_in_progress=live_provider_role_in_progress,
            live_provider_contract_mode=live_provider_contract_mode,
            provider_error_shape=provider_error_shape,
            **kwargs,
        )

    if not request:
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            counters=counters,
            validation_errors=("request_required",),
        )
    if not _live_enabled(observed_env) and (
        orchestrator_provider is None or architect_provider is None
    ):
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            counters=counters,
            validation_errors=("provider_injection_or_live_gate_required",),
        )

    orchestrator_context = _orchestrator_provider_context(request)
    orchestrator_prompt = (
        _orchestrator_compact_prompt(orchestrator_context)
        if compact_mode
        else _orchestrator_prompt(orchestrator_context)
    )
    orchestrator_response_schema = (
        ORCHESTRATOR_COMPACT_RESPONSE_SCHEMA
        if compact_mode
        else ORCHESTRATOR_RESPONSE_SCHEMA
    )
    try:
        live_provider_stage = "orchestrator_provider_call"
        last_live_provider_role = "orchestrator"
        live_provider_role_in_progress = "orchestrator"
        counters["orchestrator_provider_call_count"] = 1
        orchestrator_proposal = _call_provider(
            prompt=orchestrator_prompt,
            role="orchestrator",
            env=observed_env,
            provider=orchestrator_provider,
            response_schema=orchestrator_response_schema,
            counters=counters,
        )
        live_provider_stage = "orchestrator_provider_returned"
        live_provider_role_in_progress = None
    except provider_adapter.ProviderCaptureError as exc:
        provider_error_shape = _provider_error_shape(exc)
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            counters=counters,
            validation_errors=(_provider_reason(exc),),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        provider_error_shape = _provider_error_shape(exc)
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            counters=counters,
            validation_errors=(str(exc),),
        )

    orchestrator_response_shape = _provider_response_shape(
        orchestrator_proposal,
        rationale_key="structured_orchestrator_rationale",
    )
    if compact_mode:
        compact_errors = _missing_fields(
            orchestrator_proposal,
            ORCHESTRATOR_COMPACT_REQUIRED_FIELDS,
        )
        if compact_errors:
            return fail(
                request_text=request,
                semantic_context=semantic_context,
                orchestrator_provider_context=orchestrator_context,
                counters=counters,
                validation_errors=tuple(compact_errors),
                orchestrator_provider_response_shape=orchestrator_response_shape,
            )
        orchestrator_proposal = _expand_orchestrator_compact_proposal(
            orchestrator_proposal,
            orchestrator_context,
        )
        counters["compact_adapter_expanded_orchestrator_count"] += 1
    orchestrator_errors = (
        *_missing_fields(orchestrator_proposal, ORCHESTRATOR_REQUIRED_FIELDS),
        *_claim_errors(orchestrator_proposal, FORBIDDEN_ORCHESTRATOR_CLAIMS),
        *_validate_orchestrator_semantic_contract(
            orchestrator_proposal,
            orchestrator_context,
        ),
    )
    orchestrator_rationale = _mapping_or_empty(
        orchestrator_proposal.get("structured_orchestrator_rationale")
    )
    orchestrator_rationale_validation = validate_orchestrator_structured_rationale(
        orchestrator_rationale
    )
    if not orchestrator_rationale_validation["accepted"]:
        orchestrator_errors = (
            *orchestrator_errors,
            "orchestrator_structured_rationale_validation_failed",
            *tuple(orchestrator_rationale_validation["reasons"]),
    )
    if orchestrator_errors:
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            counters=counters,
            validation_errors=tuple(orchestrator_errors),
            orchestrator_provider_response_shape=orchestrator_response_shape,
        )

    route_packet = _route_packet_from_proposal(
        orchestrator_proposal,
        orchestrator_context,
    )
    route_packet_validation = validate_orchestrator_route_context_packet(route_packet)
    if not route_packet_validation["accepted"]:
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            orchestrator_route_context_packet=route_packet,
            orchestrator_route_context_packet_validation=route_packet_validation,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            counters=counters,
            validation_errors=(
                "orchestrator_route_context_packet_validation_failed",
                *tuple(route_packet_validation["reasons"]),
            ),
            orchestrator_provider_response_shape=orchestrator_response_shape,
        )
    counters["context_packet_validated_count"] += 1
    counters["structured_rationale_validated_count"] += 1

    architect_context = _architect_provider_context(
        route_packet=route_packet,
        route_validation=route_packet_validation,
        orchestrator_proposal=orchestrator_proposal,
    )
    architect_packet = _architect_packet_from_context(architect_context)
    architect_packet_validation = validate_architect_plan_context_packet(
        architect_packet
    )
    if not architect_packet_validation["accepted"]:
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            orchestrator_route_context_packet=route_packet,
            orchestrator_route_context_packet_validation=route_packet_validation,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            architect_provider_context=architect_context,
            architect_plan_context_packet=architect_packet,
            architect_plan_context_packet_validation=architect_packet_validation,
            counters=counters,
            validation_errors=(
                "architect_plan_context_packet_validation_failed",
                *tuple(architect_packet_validation["reasons"]),
            ),
            orchestrator_provider_response_shape=orchestrator_response_shape,
        )
    counters["context_packet_validated_count"] += 1

    architect_prompt = (
        _architect_compact_prompt(architect_context)
        if compact_mode
        else _architect_prompt(architect_context)
    )
    architect_response_schema = (
        ARCHITECT_COMPACT_RESPONSE_SCHEMA
        if compact_mode
        else ARCHITECT_RESPONSE_SCHEMA
    )
    try:
        live_provider_stage = "architect_provider_call"
        last_live_provider_role = "architect"
        live_provider_role_in_progress = "architect"
        counters["architect_provider_call_count"] = 1
        architect_proposal = _call_provider(
            prompt=architect_prompt,
            role="architect",
            env=observed_env,
            provider=architect_provider,
            response_schema=architect_response_schema,
            counters=counters,
        )
        live_provider_stage = "architect_provider_returned"
        live_provider_role_in_progress = None
    except provider_adapter.ProviderCaptureError as exc:
        provider_error_shape = _provider_error_shape(exc)
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            orchestrator_route_context_packet=route_packet,
            orchestrator_route_context_packet_validation=route_packet_validation,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            architect_provider_context=architect_context,
            architect_plan_context_packet=architect_packet,
            architect_plan_context_packet_validation=architect_packet_validation,
            counters=counters,
            validation_errors=(_provider_reason(exc),),
            orchestrator_provider_response_shape=orchestrator_response_shape,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        provider_error_shape = _provider_error_shape(exc)
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            orchestrator_route_context_packet=route_packet,
            orchestrator_route_context_packet_validation=route_packet_validation,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            architect_provider_context=architect_context,
            architect_plan_context_packet=architect_packet,
            architect_plan_context_packet_validation=architect_packet_validation,
            counters=counters,
            validation_errors=(str(exc),),
            orchestrator_provider_response_shape=orchestrator_response_shape,
        )

    architect_response_shape = _provider_response_shape(
        architect_proposal,
        rationale_key="structured_architect_rationale",
    )
    if compact_mode:
        compact_errors = _missing_fields(
            architect_proposal,
            ARCHITECT_COMPACT_REQUIRED_FIELDS,
        )
        if compact_errors:
            return fail(
                request_text=request,
                semantic_context=semantic_context,
                orchestrator_provider_context=orchestrator_context,
                orchestrator_route_context_packet=route_packet,
                orchestrator_route_context_packet_validation=route_packet_validation,
                structured_orchestrator_rationale=orchestrator_rationale,
                structured_orchestrator_rationale_validation=(
                    orchestrator_rationale_validation
                ),
                architect_provider_context=architect_context,
                architect_plan_context_packet=architect_packet,
                architect_plan_context_packet_validation=architect_packet_validation,
                counters=counters,
                validation_errors=tuple(compact_errors),
                orchestrator_provider_response_shape=orchestrator_response_shape,
                architect_provider_response_shape=architect_response_shape,
            )
        architect_proposal = _expand_architect_compact_proposal(
            architect_proposal,
            architect_context,
        )
        counters["compact_adapter_expanded_architect_count"] += 1
    architect_errors = (
        *_missing_fields(architect_proposal, ARCHITECT_REQUIRED_FIELDS),
        *_claim_errors(architect_proposal, FORBIDDEN_ARCHITECT_CLAIMS),
        *_validate_architect_semantic_contract(
            architect_proposal,
            architect_context,
        ),
        *_validate_architect_plan_surface(architect_proposal),
    )
    architect_rationale = _mapping_or_empty(
        architect_proposal.get("structured_architect_rationale")
    )
    architect_rationale_validation = validate_architect_structured_rationale(
        architect_rationale
    )
    if not architect_rationale_validation["accepted"]:
        architect_errors = (
            *architect_errors,
            "architect_structured_rationale_validation_failed",
            *tuple(architect_rationale_validation["reasons"]),
    )
    if architect_errors:
        return fail(
            request_text=request,
            semantic_context=semantic_context,
            orchestrator_provider_context=orchestrator_context,
            orchestrator_route_context_packet=route_packet,
            orchestrator_route_context_packet_validation=route_packet_validation,
            structured_orchestrator_rationale=orchestrator_rationale,
            structured_orchestrator_rationale_validation=(
                orchestrator_rationale_validation
            ),
            architect_provider_context=architect_context,
            architect_plan_context_packet=architect_packet,
            architect_plan_context_packet_validation=architect_packet_validation,
            structured_architect_rationale=architect_rationale,
            structured_architect_rationale_validation=architect_rationale_validation,
            counters=counters,
            validation_errors=tuple(architect_errors),
            orchestrator_provider_response_shape=orchestrator_response_shape,
            architect_provider_response_shape=architect_response_shape,
        )
    counters["structured_rationale_validated_count"] += 1

    plan_graph = _plan_graph_from_architect(architect_proposal)
    result_proposal = _result_proposal_from_architect(architect_proposal)
    root_boundary = _root_boundary(
        request_text=request,
        result_proposal=result_proposal,
    )
    counters["final_output_created_by_root_count"] = 1
    counters["root_final_authority_preserved_count"] = 1
    live_provider_stage = "completed"
    live_provider_role_in_progress = None

    result: dict[str, Any] = {
        "title": TITLE,
        "final_status": "PASS",
        "raw_user_request": request,
        "semantic_intake_context": semantic_context,
        "orchestrator_provider_context": orchestrator_context,
        "orchestrator_route_context_packet": route_packet,
        "orchestrator_route_context_packet_validation": route_packet_validation,
        "structured_orchestrator_rationale": orchestrator_rationale,
        "structured_orchestrator_rationale_validation": (
            orchestrator_rationale_validation
        ),
        "architect_provider_context": architect_context,
        "architect_plan_context_packet": architect_packet,
        "architect_plan_context_packet_validation": architect_packet_validation,
        "structured_architect_rationale": architect_rationale,
        "structured_architect_rationale_validation": architect_rationale_validation,
        "orchestrator_provider_response_shape": orchestrator_response_shape,
        "architect_provider_response_shape": architect_response_shape,
        "live_provider_stage": live_provider_stage,
        "last_live_provider_role": last_live_provider_role,
        "live_provider_role_in_progress": live_provider_role_in_progress,
        "provider_timeout_seconds": provider_timeout_seconds,
        "live_provider_contract_mode": live_provider_contract_mode,
        "provider_error_shape": provider_error_shape,
        "plan_graph_context": plan_graph,
        "result_proposal": result_proposal,
        "root_final_output_boundary": root_boundary,
        "counters": counters,
        "validation_errors": (),
    }
    result["pass_conditions"] = _pass_conditions(result)
    if not all(result["pass_conditions"].values()):
        result["final_status"] = "FAIL_CLOSED"
        result["validation_errors"] = tuple(
            key for key, passed in result["pass_conditions"].items() if not passed
        )
    return result


def render_report(result: dict[str, Any] | None = None) -> str:
    if result is None:
        result = run_live_unknown_request_dual_rich_context("")
    lines = [
        TITLE,
        "",
        f"final_status: {result['final_status']}",
        f"raw_user_request: {result.get('raw_user_request', '')}",
        "",
        "Pipeline:",
        "- raw request -> Gemini Orchestrator -> validated route/context packet/rationale",
        "- Gemini Architect -> validated plan/context packet/rationale",
        "- ResultProposal -> Root final boundary",
        "",
        "Validation:",
        "- OrchestratorRouteContextPacket accepted: "
        f"{result.get('orchestrator_route_context_packet_validation', {}).get('accepted')}",
        "- ArchitectPlanContextPacket accepted: "
        f"{result.get('architect_plan_context_packet_validation', {}).get('accepted')}",
        "- structured_orchestrator_rationale accepted: "
        f"{result.get('structured_orchestrator_rationale_validation', {}).get('accepted')}",
        "- structured_architect_rationale accepted: "
        f"{result.get('structured_architect_rationale_validation', {}).get('accepted')}",
        "",
        "Boundaries:",
        "- ContextPacket is not truth",
        "- ContextPacket is not authority",
        "- PlanGraph is not authority",
        "- ResultProposal is not FinalOutput",
        "- Gemini proposes, Root disposes",
        "- Root remains final authority",
        "",
        "Counters:",
        f"- live_model_call_count: {result['counters']['live_model_call_count']}",
        f"- network_used_count: {result['counters']['network_used_count']}",
        f"- gemini_called_count: {result['counters']['gemini_called_count']}",
        "- action_permission_created_count: "
        f"{result['counters']['action_permission_created_count']}",
        f"- connector_called_count: {result['counters']['connector_called_count']}",
        f"- real_world_effects_count: {result['counters']['real_world_effects_count']}",
        "",
        "validation_errors:",
        json.dumps(tuple(result.get("validation_errors", ())), sort_keys=True),
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--request", default="", help="Raw natural-language request")
    args = parser.parse_args()
    result = run_live_unknown_request_dual_rich_context(args.request)
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
