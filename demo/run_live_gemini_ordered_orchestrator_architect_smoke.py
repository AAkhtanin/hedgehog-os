from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Any

from demo.run_live_gemini_orchestrator_smoke import (
    REQUIRED_DOWNSTREAM_ACTORS,
    REQUIRED_FORBIDDEN_VECTOR_CLASSES,
    REQUIRED_GUARDS,
    REQUIRED_MATRIX_FIELDS,
    LIVE_ENV_GATE,
    TASK_TEXT,
    _config_value,
    _deterministic_orchestrator_proposal,
    _extract_json_object,
    _validate_proposal,
)
from demo.run_root_native_full_canonical_e2e_trace import (
    RootNativeFullCanonicalE2EReport,
    collect_root_native_full_canonical_e2e_trace,
)
from hedgehog.architect import _make_deterministic_plan_graph
from hedgehog.llm_architect import make_plan_graph_with_llm
from hedgehog.llm_architect import validate_plan_graph_contract


REPAIRABLE_INVALID_MARKERS = ("missing", "invalid", "bad")
ORCHESTRATOR_SCHEMA_NAME = "orchestrator_proposal_v0_1"
ORCHESTRATOR_PROPOSAL_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": list(REQUIRED_MATRIX_FIELDS),
    "properties": {
        "proposal_id": {"type": "string"},
        "proposal_source": {"type": "string"},
        "input_task": {"type": "string"},
        "intent_classification": {"type": "string"},
        "route_recommendation": {
            "type": "string",
            "enum": ["proof_full_pipeline"],
        },
        "route_confidence": {"type": "number"},
        "temporal_query_required": {"type": "boolean"},
        "drs_retrieval_intent": {"type": "string"},
        "drs_scope": {"type": "string", "enum": ["local_only"]},
        "avf_context": {"type": "string"},
        "candidate_vector_hints": {
            "type": "array",
            "items": {"type": "string"},
        },
        "forbidden_vector_classes": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": sorted(REQUIRED_FORBIDDEN_VECTOR_CLASSES),
            },
        },
        "guard_set": {
            "type": "array",
            "items": {"type": "string", "enum": sorted(REQUIRED_GUARDS)},
        },
        "permission_requirements": {
            "type": "array",
            "items": {"type": "string"},
        },
        "risk_flags": {"type": "array", "items": {"type": "string"}},
        "budget_hints": {"type": "string"},
        "downstream_actors": {
            "type": "array",
            "items": {"type": "string", "enum": sorted(REQUIRED_DOWNSTREAM_ACTORS)},
        },
        "fallback_route": {"type": "string"},
        "audit_tags": {"type": "array", "items": {"type": "string"}},
        "explanation": {"type": "string"},
        "proposal_is_action": {"type": "boolean"},
        "proposal_creates_final_output": {"type": "boolean"},
        "proposal_writes_drs": {"type": "boolean"},
        "proposal_executes_actions": {"type": "boolean"},
    },
}


@dataclass(frozen=True)
class OrderedGeminiSmokeReport:
    source_report: RootNativeFullCanonicalE2EReport
    input: dict[str, Any]
    ordered_role_flow: dict[str, Any]
    orchestrator_stage: dict[str, Any]
    architect_stage: dict[str, Any]
    boundary_checks: dict[str, Any]
    full_canonical_e2e_context: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _live_config_available(*, allow_config: bool = True) -> bool:
    return bool(
        _config_value(
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_GEMINI_API_KEY",
            allow_config=allow_config,
        )
    )


def _input(
    *,
    live_requested: bool,
    live_available: bool,
    live_used: bool,
    skip_reason: str | None,
) -> dict[str, Any]:
    mode = "live_opt_in" if live_requested else "dry_run_default"
    fields: dict[str, Any] = {
        "task_id": "live_gemini_ordered_orchestrator_architect_smoke_certificate",
        "input_text": TASK_TEXT,
        "mode": mode,
        "live_requested": live_requested,
        "live_gemini_available": live_available,
        "live_gemini_used": live_used,
        "network_free": not live_requested,
        "telegram_used": False,
        "real_external_action": False,
    }
    if skip_reason:
        fields["skip_reason"] = skip_reason
    return fields


def _orchestrator_prompt(*, validation_errors: list[str] | None = None) -> dict[str, Any]:
    prompt = {
        "instruction": "Return exactly one JSON object. No markdown. No prose. Do not add unknown keys.",
        "input_task": TASK_TEXT,
        "route_recommendation": "Use route_recommendation exactly: proof_full_pipeline.",
        "drs_scope": "Use drs_scope exactly: local_only.",
        "temporal_query_required": "temporal_query_required MUST be true.",
        "downstream_actors_rule": (
            "downstream_actors MUST contain exactly this list and no other values. "
            "Do not omit any downstream actor. Do not rename downstream actors. "
            "Do not replace Post V&V with PostVV or Post Validation. "
            "Do not replace DRS audit/writeback proof with DRS or Audit."
        ),
        "required_downstream_actors": sorted(REQUIRED_DOWNSTREAM_ACTORS),
        "proposal_flags": {
            "proposal_is_action": False,
            "proposal_creates_final_output": False,
            "proposal_writes_drs": False,
            "proposal_executes_actions": False,
        },
        "required_guard_set": [
            "Root final authority",
            "AVF boundary",
            "PlanGraph contract",
            "Executor boundary",
            "Post V&V",
            "GT",
            "ReuseGate boundary",
            "no real external actions",
            "no production persistence",
            "no global/external DRS",
        ],
        "forbidden_vector_classes": [
            "external_action_without_permission",
            "direct_drs_write_by_llm",
            "final_output_by_llm",
            "global_drs_access",
            "credential_exposure",
            "policy_bypass",
        ],
    }
    if validation_errors:
        prompt["repair_instruction"] = "Return only corrected JSON."
        prompt["validation_errors"] = validation_errors
    return prompt


def _validation_errors(validation: dict[str, Any]) -> list[str]:
    errors = []
    for key in (
        "matrix_fields_present",
        "no_extra_keys",
        "route_allowed_by_validator",
        "guard_set_complete",
        "downstream_actors_complete",
        "forbidden_vector_classes_complete",
        "local_drs_only",
        "proposal_only",
        "confidence_valid",
        "temporal_query_required",
    ):
        if not validation[key]:
            errors.append(key)
    return errors


def _list_diagnostics(values: Any, required: set[str]) -> tuple[list[str], list[str]]:
    actual = set(values) if isinstance(values, list) else set()
    return sorted(required - actual), sorted(actual - required)


def _validate_ordered_proposal(
    proposal: dict[str, Any],
    *,
    active_source: str | None = None,
    active_is_fallback: bool = False,
) -> dict[str, Any]:
    validation = _validate_proposal(
        proposal,
        active_source=active_source,
        active_is_fallback=active_is_fallback,
    )
    extra_keys = sorted(set(proposal) - set(REQUIRED_MATRIX_FIELDS))
    no_extra_keys = not extra_keys
    route_exact = proposal.get("route_recommendation") == "proof_full_pipeline"
    drs_scope_exact = proposal.get("drs_scope") == "local_only"
    valid = (
        validation["orchestrator_proposal_valid"]
        and no_extra_keys
        and route_exact
        and drs_scope_exact
    )
    validation.update(
        {
            "orchestrator_proposal_valid": valid,
            "attempted_proposal_valid": valid,
            "active_proposal_valid": valid,
            "no_extra_keys": no_extra_keys,
            "extra_keys": extra_keys,
            "route_allowed_by_validator": route_exact,
            "local_drs_only": drs_scope_exact,
            "invalid_proposal_caught": not valid,
            "contract_violation_contained": not valid,
            "fallback_to_deterministic_orchestrator": not valid,
        }
    )
    return validation


def _merge_ordered_active_validation(
    *,
    attempted_validation: dict[str, Any],
    active_proposal: dict[str, Any],
    active_is_fallback: bool,
) -> dict[str, Any]:
    active_validation = _validate_ordered_proposal(
        active_proposal,
        active_source=active_proposal.get("proposal_source", "none"),
        active_is_fallback=active_is_fallback,
    )
    return {
        **active_validation,
        "orchestrator_proposal_received": attempted_validation[
            "orchestrator_proposal_received"
        ],
        "orchestrator_proposal_valid": active_validation[
            "orchestrator_proposal_valid"
        ],
        "attempted_proposal_valid": attempted_validation[
            "attempted_proposal_valid"
        ],
        "active_proposal_valid": active_validation["orchestrator_proposal_valid"],
        "active_proposal_source": active_proposal.get("proposal_source", "none"),
        "active_proposal_is_fallback": active_is_fallback,
        "invalid_proposal_caught": not attempted_validation[
            "attempted_proposal_valid"
        ],
        "contract_violation_contained": not attempted_validation[
            "attempted_proposal_valid"
        ],
        "fallback_to_deterministic_orchestrator": active_is_fallback,
        "architect_reached_from_invalid_orchestrator": False,
        "executor_reached_from_invalid_orchestrator": False,
        "root_final_output_created_from_live_orchestrator": False,
    }


def _live_orchestrator_call(
    *, model: str | None, allow_config: bool, validation_errors: list[str] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    diagnostics = {
        "orchestrator_structured_output_requested": True,
        "orchestrator_schema_used": False,
        "orchestrator_schema_name": ORCHESTRATOR_SCHEMA_NAME,
        "orchestrator_schema_config_key": "none",
    }
    api_key = _config_value(
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        allow_config=allow_config,
    )
    if not api_key:
        return {}, False, diagnostics
    try:
        from google import genai  # type: ignore
    except ImportError:
        return {}, False, diagnostics

    model_name = model or _config_value("GEMINI_MODEL", allow_config=allow_config) or "gemini-3.5-flash"
    try:
        client = genai.Client(api_key=api_key)
        base_config = {
            "system_instruction": (
                "You are an Orchestrator proposal actor only. You are not Root. "
                "You do not create FinalOutput. You do not write DRS. "
                "You do not execute actions. Return only the JSON object "
                "matching the schema."
            ),
            "response_mime_type": "application/json",
        }
        contents = json.dumps(
            _orchestrator_prompt(validation_errors=validation_errors),
            sort_keys=True,
        )
        response = None
        for schema_key in ("response_json_schema", "response_schema"):
            config = {**base_config, schema_key: ORCHESTRATOR_PROPOSAL_JSON_SCHEMA}
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
            except Exception:
                continue
            diagnostics["orchestrator_schema_used"] = True
            diagnostics["orchestrator_schema_config_key"] = schema_key
            break
        if response is None:
            return {}, True, diagnostics
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, dict):
            payload = dict(parsed)
        else:
            payload = _extract_json_object(getattr(response, "text", "") or "")
        payload["proposal_source"] = "live_gemini"
        return payload, True, diagnostics
    except Exception:
        return {}, True, diagnostics


def _should_attempt_repair(
    *, live_requested: bool, live_available: bool, validation: dict[str, Any]
) -> bool:
    return live_requested and live_available and not validation["attempted_proposal_valid"]


def _collect_orchestrator_stage(
    *,
    live_requested: bool,
    live_available: bool,
    allow_config: bool,
    model: str | None,
    injected_orchestrator_proposal: dict[str, Any] | None,
) -> tuple[dict[str, Any], bool]:
    live_called = False
    structured_output_requested = live_requested and live_available
    schema_used = False
    schema_config_key = "none"
    initial_validation_errors: list[str] = []
    repair_validation_errors: list[str] = []
    initial_source = "deterministic_mock_orchestrator"
    if injected_orchestrator_proposal is not None:
        initial = dict(injected_orchestrator_proposal)
        initial.setdefault("proposal_source", "injected_invalid")
        initial_source = initial["proposal_source"]
    elif live_requested and live_available:
        initial, live_called, diagnostics = _live_orchestrator_call(
            model=model, allow_config=allow_config
        )
        structured_output_requested = diagnostics[
            "orchestrator_structured_output_requested"
        ]
        schema_used = diagnostics["orchestrator_schema_used"]
        schema_config_key = diagnostics["orchestrator_schema_config_key"]
        initial_source = "live_gemini"
    elif live_requested and not live_available:
        initial = {}
        initial_source = "missing_live_configuration"
    else:
        initial = _deterministic_orchestrator_proposal()

    initial_validation = _validate_ordered_proposal(initial)
    initial_validation_errors = _validation_errors(initial_validation)
    initial_downstream_missing, initial_downstream_extra = _list_diagnostics(
        initial.get("downstream_actors"), REQUIRED_DOWNSTREAM_ACTORS
    )
    repair_attempted = _should_attempt_repair(
        live_requested=live_requested,
        live_available=live_available,
        validation=initial_validation,
    )
    repair_valid = False
    repair_downstream_missing: list[str] = []
    repair_downstream_extra: list[str] = []
    repair_temporal_query_required_value: Any = None
    active = initial
    active_is_fallback = False
    active_source = initial.get("proposal_source", initial_source)

    if repair_attempted:
        repaired, repair_called, repair_diagnostics = _live_orchestrator_call(
            model=model,
            allow_config=allow_config,
            validation_errors=_validation_errors(initial_validation),
        )
        live_called = live_called or repair_called
        structured_output_requested = (
            structured_output_requested
            or repair_diagnostics["orchestrator_structured_output_requested"]
        )
        schema_used = schema_used or repair_diagnostics["orchestrator_schema_used"]
        if repair_diagnostics["orchestrator_schema_config_key"] != "none":
            schema_config_key = repair_diagnostics["orchestrator_schema_config_key"]
        if repaired:
            repaired["proposal_source"] = "live_gemini_repair"
        repair_validation = _validate_ordered_proposal(repaired)
        repair_validation_errors = _validation_errors(repair_validation)
        repair_temporal_query_required_value = repaired.get(
            "temporal_query_required", None
        )
        repair_downstream_missing, repair_downstream_extra = _list_diagnostics(
            repaired.get("downstream_actors"), REQUIRED_DOWNSTREAM_ACTORS
        )
        repair_valid = repair_validation["attempted_proposal_valid"]
        if repair_valid:
            active = repaired
            active_source = "live_gemini_repair"
        else:
            active = _deterministic_orchestrator_proposal()
            active_source = active["proposal_source"]
            active_is_fallback = True
    elif not initial_validation["attempted_proposal_valid"]:
        active = _deterministic_orchestrator_proposal()
        active_source = active["proposal_source"]
        active_is_fallback = True

    if active_is_fallback:
        validation = _merge_ordered_active_validation(
            attempted_validation=initial_validation,
            active_proposal=active,
            active_is_fallback=True,
        )
    else:
        validation = _validate_ordered_proposal(
            active,
            active_source=active_source,
            active_is_fallback=False,
        )
        validation["attempted_proposal_valid"] = initial_validation[
            "attempted_proposal_valid"
        ]
        validation["invalid_proposal_caught"] = not initial_validation[
            "attempted_proposal_valid"
        ]
        validation["contract_violation_contained"] = not initial_validation[
            "attempted_proposal_valid"
        ]

    active_downstream_missing, active_downstream_extra = _list_diagnostics(
        active.get("downstream_actors"), REQUIRED_DOWNSTREAM_ACTORS
    )
    stage = {
        "orchestrator_proposal_source": initial_source,
        "orchestrator_initial_attempt_valid": initial_validation[
            "attempted_proposal_valid"
        ],
        "orchestrator_repair_attempted": repair_attempted,
        "orchestrator_repair_valid": repair_valid,
        "orchestrator_active_proposal_valid": validation["active_proposal_valid"],
        "orchestrator_active_proposal_source": validation["active_proposal_source"],
        "orchestrator_active_proposal_is_fallback": validation[
            "active_proposal_is_fallback"
        ],
        "orchestrator_structured_output_requested": structured_output_requested,
        "orchestrator_schema_used": schema_used,
        "orchestrator_schema_name": ORCHESTRATOR_SCHEMA_NAME,
        "orchestrator_schema_config_key": schema_config_key,
        "orchestrator_initial_validation_errors": initial_validation_errors,
        "orchestrator_repair_validation_errors": repair_validation_errors,
        "temporal_query_required_value": active.get(
            "temporal_query_required", None
        ),
        "downstream_actors_value": active.get("downstream_actors", []),
        "required_downstream_actors": sorted(REQUIRED_DOWNSTREAM_ACTORS),
        "downstream_actors_missing": active_downstream_missing,
        "downstream_actors_extra": active_downstream_extra,
        "orchestrator_initial_temporal_query_required_value": initial.get(
            "temporal_query_required", None
        ),
        "orchestrator_repair_temporal_query_required_value": repair_temporal_query_required_value,
        "orchestrator_initial_downstream_actors_missing": initial_downstream_missing,
        "orchestrator_initial_downstream_actors_extra": initial_downstream_extra,
        "orchestrator_repair_downstream_actors_missing": repair_downstream_missing,
        "orchestrator_repair_downstream_actors_extra": repair_downstream_extra,
        "route_recommendation": active.get("route_recommendation", "none"),
        "drs_scope": active.get("drs_scope", "none"),
        "guard_set_complete": validation["guard_set_complete"],
        "route_allowed_by_validator": validation["route_allowed_by_validator"],
        "local_drs_only": validation["local_drs_only"],
        "proposal_only": validation["proposal_only"],
        "invalid_orchestrator_caught": validation["invalid_proposal_caught"],
        "fallback_to_deterministic_orchestrator": validation[
            "fallback_to_deterministic_orchestrator"
        ],
        "architect_reached_from_invalid_orchestrator": False,
        "_active_proposal": active,
    }
    return stage, live_called


def _collect_architect_stage(
    *,
    source_report: RootNativeFullCanonicalE2EReport,
    orchestrator_stage: dict[str, Any],
    live_requested: bool,
    live_available: bool,
    allow_config: bool,
    model: str | None,
    injected_architect_artifact: dict[str, Any] | None,
) -> tuple[dict[str, Any], bool]:
    attractor_packet = source_report.first_run_source.trace["attractor_packet"]
    fallback_plan = _make_deterministic_plan_graph(attractor_packet)
    validate_plan_graph_contract(fallback_plan, attractor_packet)
    if not orchestrator_stage["orchestrator_active_proposal_valid"]:
        return (
            {
                "architect_artifact_source": "not_run_invalid_orchestrator",
                "architect_artifact_valid": False,
                "plan_graph_contract_checked": False,
                "plan_graph_present": False,
                "invalid_architect_artifact_caught": False,
                "fallback_to_deterministic_architect": False,
                "executor_reached_from_invalid_architect": False,
                "root_final_output_created_from_live_architect": False,
            },
            False,
        )

    live_called = False
    if injected_architect_artifact is not None:
        try:
            validate_plan_graph_contract(injected_architect_artifact, attractor_packet)
        except Exception:
            return (
                {
                    "architect_artifact_source": "injected_invalid",
                    "architect_artifact_valid": True,
                    "plan_graph_contract_checked": True,
                    "plan_graph_present": True,
                    "invalid_architect_artifact_caught": True,
                    "fallback_to_deterministic_architect": True,
                    "executor_reached_from_invalid_architect": False,
                    "root_final_output_created_from_live_architect": False,
                },
                live_called,
            )

    if live_requested and live_available:
        result = make_plan_graph_with_llm(
            attractor_packet=attractor_packet,
            provider="gemini",
            model=model,
            allow_config=allow_config,
        )
        live_called = bool(result.get("used_llm"))
        if result["status"] == "completed" and result["plan_graph"] is not None:
            try:
                validate_plan_graph_contract(result["plan_graph"], attractor_packet)
            except Exception:
                pass
            else:
                return (
                    {
                        "architect_artifact_source": "live_gemini",
                        "architect_artifact_valid": True,
                        "plan_graph_contract_checked": True,
                        "plan_graph_present": True,
                        "invalid_architect_artifact_caught": False,
                        "fallback_to_deterministic_architect": False,
                        "executor_reached_from_invalid_architect": False,
                        "root_final_output_created_from_live_architect": False,
                    },
                    live_called,
                )
        return (
            {
                "architect_artifact_source": "deterministic_mock_architect",
                "architect_artifact_valid": True,
                "plan_graph_contract_checked": True,
                "plan_graph_present": True,
                "invalid_architect_artifact_caught": live_called,
                "fallback_to_deterministic_architect": True,
                "executor_reached_from_invalid_architect": False,
                "root_final_output_created_from_live_architect": False,
            },
            live_called,
        )

    return (
        {
            "architect_artifact_source": "deterministic_mock_architect",
            "architect_artifact_valid": True,
            "plan_graph_contract_checked": True,
            "plan_graph_present": True,
            "invalid_architect_artifact_caught": False,
            "fallback_to_deterministic_architect": False,
            "executor_reached_from_invalid_architect": False,
            "root_final_output_created_from_live_architect": False,
        },
        live_called,
    )


def _full_canonical_context(
    source_report: RootNativeFullCanonicalE2EReport,
) -> dict[str, Any]:
    return {
        "full_canonical_e2e_status": source_report.summary[
            "root_native_full_canonical_e2e_trace_status"
        ],
        "first_run_stages_passed": source_report.summary["first_run_stages_passed"],
        "second_run_stages_passed": source_report.summary[
            "second_run_stages_passed"
        ],
        "production_persistence_claimed": source_report.summary[
            "production_persistence_claimed"
        ],
        "production_reuse_claimed": source_report.summary["production_reuse_claimed"],
        "production_direct_reuse_executed": source_report.summary[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": source_report.summary[
            "production_final_output_created"
        ],
    }


def _ordered_role_flow(
    orchestrator_stage: dict[str, Any],
    architect_stage: dict[str, Any],
) -> dict[str, Any]:
    return {
        "root_boundary_entered": True,
        "orchestrator_runs_before_architect": True,
        "architect_runs_after_valid_orchestrator": orchestrator_stage[
            "orchestrator_active_proposal_valid"
        ]
        and architect_stage["plan_graph_contract_checked"],
        "executor_not_reached_from_invalid_orchestrator": not orchestrator_stage[
            "architect_reached_from_invalid_orchestrator"
        ],
        "root_final_not_created_from_invalid_live_output": not architect_stage[
            "root_final_output_created_from_live_architect"
        ],
    }


def _boundary_checks(
    source_report: RootNativeFullCanonicalE2EReport,
    orchestrator_stage: dict[str, Any],
    architect_stage: dict[str, Any],
    ordered_flow: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    first_sections = source_report.first_run_source.sections
    full_pass = context["full_canonical_e2e_status"] == "PASS"
    avf_preserved = (
        full_pass
        and first_sections["avf_attractor"]["avf_runs_before_architect"]
        and first_sections["avf_attractor"]["attractor_packet_created"]
        and not first_sections["avf_attractor"][
            "architect_received_forbidden_vectors"
        ]
    )
    post_vv_preserved = (
        full_pass
        and first_sections["post_vv_gt"]["post_vv_after_dag_executor"]
        and first_sections["post_vv_gt"]["vv_reports_count"] > 0
    )
    gt_preserved = (
        full_pass
        and first_sections["post_vv_gt"]["gt_after_post_vv"]
        and not first_sections["post_vv_gt"]["gt_committed_final_output"]
    )
    root_preserved = (
        source_report.summary["first_run_root_authority_preserved"]
        and source_report.summary["second_run_root_authority_preserved"]
        and ordered_flow["root_boundary_entered"]
        and not architect_stage["root_final_output_created_from_live_architect"]
    )
    policy_preserved = (
        orchestrator_stage["route_allowed_by_validator"]
        and orchestrator_stage["local_drs_only"]
        and orchestrator_stage["proposal_only"]
    )
    permission_preserved = (
        orchestrator_stage["guard_set_complete"]
        and not architect_stage["executor_reached_from_invalid_architect"]
    )
    return {
        "root_boundary_preserved": root_preserved,
        "orchestrator_boundary_preserved": orchestrator_stage[
            "orchestrator_active_proposal_valid"
        ],
        "avf_boundary_preserved": avf_preserved,
        "architect_contract_boundary_preserved": architect_stage[
            "plan_graph_contract_checked"
        ],
        "executor_boundary_preserved": not architect_stage[
            "executor_reached_from_invalid_architect"
        ],
        "post_vv_boundary_preserved": post_vv_preserved,
        "gt_boundary_preserved": gt_preserved,
        "reuse_gate_boundary_preserved": source_report.authority_safety[
            "reuse_gate_boundary_preserved"
        ],
        "policy_boundary_preserved": policy_preserved,
        "permission_boundary_preserved": permission_preserved,
        "gemini_bypassed_root": False,
        "gemini_bypassed_policy": False,
        "gemini_bypassed_permissions": False,
    }


def _authority_safety(
    source_report: RootNativeFullCanonicalE2EReport,
    architect_stage: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gemini_authority_granted": False,
        "gemini_created_final_output": False,
        "gemini_wrote_drs": False,
        "gemini_executed_action": False,
        "production_external_action_executed": source_report.authority_safety[
            "production_external_action_executed"
        ],
        "production_final_output_created": source_report.summary[
            "production_final_output_created"
        ]
        or architect_stage["root_final_output_created_from_live_architect"],
        "production_work_record_written": source_report.summary[
            "production_work_record_written"
        ],
        "live_telegram_action_executed": False,
        "no_global_drs": source_report.authority_safety["no_global_drs"],
        "no_external_drs_network": source_report.authority_safety[
            "no_external_drs_network"
        ],
        "production_autonomy_claimed": source_report.authority_safety[
            "production_autonomy_claimed"
        ],
    }


def _summary(
    *,
    mode: str,
    live_requested: bool,
    live_available: bool,
    live_used: bool,
    ordered_flow: dict[str, Any],
    orchestrator_stage: dict[str, Any],
    architect_stage: dict[str, Any],
    boundary: dict[str, Any],
    context: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    boundaries_pass = (
        ordered_flow["orchestrator_runs_before_architect"]
        and ordered_flow["architect_runs_after_valid_orchestrator"]
        and boundary["root_boundary_preserved"]
        and boundary["orchestrator_boundary_preserved"]
        and boundary["avf_boundary_preserved"]
        and boundary["architect_contract_boundary_preserved"]
        and boundary["executor_boundary_preserved"]
        and boundary["post_vv_boundary_preserved"]
        and boundary["gt_boundary_preserved"]
        and boundary["reuse_gate_boundary_preserved"]
        and boundary["policy_boundary_preserved"]
        and boundary["permission_boundary_preserved"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["production_work_record_written"]
        and not authority["production_autonomy_claimed"]
    )
    failures_contained = (
        orchestrator_stage["orchestrator_active_proposal_valid"]
        and (
            orchestrator_stage["orchestrator_initial_attempt_valid"]
            or orchestrator_stage["orchestrator_repair_valid"]
            or orchestrator_stage["fallback_to_deterministic_orchestrator"]
        )
        and architect_stage["architect_artifact_valid"]
        and not architect_stage["executor_reached_from_invalid_architect"]
        and not architect_stage["root_final_output_created_from_live_architect"]
    )
    if live_requested and not live_available:
        status = "SKIPPED" if boundaries_pass and failures_contained else "FAIL"
    else:
        status = "PASS" if boundaries_pass and failures_contained else "FAIL"
    return {
        "live_gemini_ordered_orchestrator_architect_smoke_status": status,
        "mode": mode,
        "live_gemini_used": live_used,
        "orchestrator_runs_before_architect": ordered_flow[
            "orchestrator_runs_before_architect"
        ],
        "orchestrator_active_proposal_valid": orchestrator_stage[
            "orchestrator_active_proposal_valid"
        ],
        "architect_artifact_valid": architect_stage["architect_artifact_valid"],
        "ordered_live_roles_preserved": boundaries_pass,
        "full_canonical_e2e_status": context["full_canonical_e2e_status"],
        "root_authority_preserved": boundary["root_boundary_preserved"],
        "production_final_output_created": authority[
            "production_final_output_created"
        ],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "ready_for_future_controlled_orchestrator_integration": boundaries_pass
        and failures_contained,
    }


def collect_live_gemini_ordered_orchestrator_architect_smoke(
    *,
    live_requested: bool = False,
    allow_config: bool = True,
    model: str | None = None,
    injected_orchestrator_proposal: dict[str, Any] | None = None,
    injected_architect_artifact: dict[str, Any] | None = None,
) -> OrderedGeminiSmokeReport:
    source_report = collect_root_native_full_canonical_e2e_trace()
    live_gate_enabled = os.environ.get(LIVE_ENV_GATE) == "1"
    live_available = live_requested and live_gate_enabled and _live_config_available(
        allow_config=allow_config
    )
    skip_reason = (
        "missing_live_gemini_configuration"
        if live_requested and not live_available
        else None
    )
    orchestrator_stage, orchestrator_live_called = _collect_orchestrator_stage(
        live_requested=live_requested,
        live_available=live_available,
        allow_config=allow_config,
        model=model,
        injected_orchestrator_proposal=injected_orchestrator_proposal,
    )
    architect_stage, architect_live_called = _collect_architect_stage(
        source_report=source_report,
        orchestrator_stage=orchestrator_stage,
        live_requested=live_requested,
        live_available=live_available,
        allow_config=allow_config,
        model=model,
        injected_architect_artifact=injected_architect_artifact,
    )
    live_used = live_available and (orchestrator_live_called or architect_live_called)
    input_fields = _input(
        live_requested=live_requested,
        live_available=live_available,
        live_used=live_used,
        skip_reason=skip_reason,
    )
    context = _full_canonical_context(source_report)
    ordered_flow = _ordered_role_flow(orchestrator_stage, architect_stage)
    boundary = _boundary_checks(
        source_report,
        orchestrator_stage,
        architect_stage,
        ordered_flow,
        context,
    )
    authority = _authority_safety(source_report, architect_stage)
    summary = _summary(
        mode=input_fields["mode"],
        live_requested=live_requested,
        live_available=live_available,
        live_used=live_used,
        ordered_flow=ordered_flow,
        orchestrator_stage=orchestrator_stage,
        architect_stage=architect_stage,
        boundary=boundary,
        context=context,
        authority=authority,
    )
    orchestrator_stage = {
        key: value for key, value in orchestrator_stage.items() if key != "_active_proposal"
    }
    return OrderedGeminiSmokeReport(
        source_report=source_report,
        input=input_fields,
        ordered_role_flow=ordered_flow,
        orchestrator_stage=orchestrator_stage,
        architect_stage=architect_stage,
        boundary_checks=boundary,
        full_canonical_e2e_context=context,
        authority_safety=authority,
        summary=summary,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def render_live_gemini_ordered_orchestrator_architect_smoke(
    report: OrderedGeminiSmokeReport,
) -> str:
    lines = [
        "[LIVE GEMINI ORDERED ORCHESTRATOR ARCHITECT SMOKE]",
        "note: opt-in ordered Gemini Orchestrator-to-Architect smoke",
        "note: Orchestrator proposal is validated before Architect runs",
        "note: one bounded Orchestrator repair may run only in live opt-in mode",
        "note: no production RootOrchestrator behavior change",
        "note: no live Telegram action",
        "note: no real external actions except optional Gemini model calls",
        "note: no production FinalOutput created by Gemini",
        "note: no DRS write by Gemini",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "",
        "[INPUT]",
    ]
    lines.extend(_field_lines(report.input))
    lines.extend(["", "[ORDERED ROLE FLOW]"])
    lines.extend(_field_lines(report.ordered_role_flow))
    lines.extend(["", "[ORCHESTRATOR STAGE]"])
    lines.extend(_field_lines(report.orchestrator_stage))
    lines.extend(["", "[ARCHITECT STAGE]"])
    lines.extend(_field_lines(report.architect_stage))
    lines.extend(["", "[BOUNDARY CHECKS]"])
    lines.extend(_field_lines(report.boundary_checks))
    lines.extend(["", "[FULL CANONICAL E2E CONTEXT]"])
    lines.extend(_field_lines(report.full_canonical_e2e_context))
    lines.extend(["", "[AUTHORITY / SAFETY]"])
    lines.extend(_field_lines(report.authority_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_live_gemini_ordered_orchestrator_architect_smoke(
    *, live_requested: bool = False
) -> str:
    return render_live_gemini_ordered_orchestrator_architect_smoke(
        collect_live_gemini_ordered_orchestrator_architect_smoke(
            live_requested=live_requested
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ordered Gemini Orchestrator-to-Architect smoke proof."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Opt in to live Gemini calls when configured.",
    )
    args = parser.parse_args()
    print(
        run_live_gemini_ordered_orchestrator_architect_smoke(
            live_requested=args.live
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
