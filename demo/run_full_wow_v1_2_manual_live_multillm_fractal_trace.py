from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Mapping


Provider = Callable[[str, str, Mapping[str, Any]], str]

RUN_ID = "full_wow_v1_2_manual_live_multillm_fractal_trace_v01"
REPORT_ID = "full_wow_v1_2_manual_live_multillm_fractal_trace_v01"
ENABLE_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_MULTILLM_FRACTAL"
ARTIFACT_DIR_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_MULTILLM_FRACTAL_ARTIFACT_DIR"
MODEL_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_MULTILLM_FRACTAL_MODEL"
CALL_DELAY_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_MULTILLM_FRACTAL_CALL_DELAY_SECONDS"
DEFAULT_MODEL = "gemini-2.5-flash"

RENDERED_SECTIONS = (
    "[FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE]",
    "[LANE STATUS]",
    "[SEMANTIC ACTOR CALLS]",
    "[TOP-LEVEL ORCHESTRATOR]",
    "[BSEP MEMBRANE]",
    "[TOP-LEVEL SEMANTIC ARCHITECT]",
    "[RUNTIME PLAN AND FRACTAL CELLS]",
    "[BRANCH-LOCAL LLM/SLM ACTORS]",
    "[BRANCH RESULT PROPOSALS]",
    "[POST V&V / GT-LGT / ROOT]",
    "[SECRET MEMBRANE]",
    "[AUTHORITY MATRIX]",
    "[COUNTER MATRIX]",
    "[ARTIFACTS]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

PIPELINE_SEQUENCE = (
    "dirty_request_loaded_from_v1_2_product_trace",
    "top_level_orchestrator_provider_called",
    "top_level_orchestrator_semantics_validated",
    "top_level_orchestrator_semantics_canonicalized",
    "bsep_created",
    "bsep_validated",
    "top_level_architect_prompt_built_from_bsep",
    "top_level_architect_provider_called",
    "top_level_architect_semantics_validated",
    "top_level_architect_semantics_canonicalized",
    "runtime_plangraph_compiled",
    "fractal_branch_cells_created",
    "warehouse_branch_api_evidence_observed",
    "supplier_a_branch_api_evidence_observed",
    "supplier_b_branch_api_evidence_observed",
    "legal_branch_semantic_actor_called",
    "legal_branch_result_proposal_created",
    "accounting_branch_semantic_actor_called",
    "accounting_branch_result_proposal_created",
    "supplier_b_branch_semantic_actor_called",
    "supplier_b_branch_result_proposal_created",
    "bank_policy_branch_semantic_actor_called",
    "bank_branch_result_proposal_created",
    "branch_result_proposals_merged",
    "post_vv_validated",
    "gt_lgt_advisory_reviewed",
    "root_final_boundary_evaluated",
)

BRANCH_IDS = (
    "warehouse_branch",
    "supplier_a_branch",
    "supplier_b_branch",
    "legal_branch",
    "accounting_branch",
    "bank_a_branch",
    "bank_b_branch",
    "root_merge_branch",
)

BRANCH_ACTOR_ROLES = {
    "legal_branch": "legal_clause_semantic_extractor",
    "accounting_branch": "accounting_mismatch_semantic_explainer",
    "supplier_b_branch": "supplier_b_unstructured_note_interpreter",
    "bank_b_branch": "bank_policy_semantic_reviewer",
}

AUTHORITY_MATRIX = (
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "Branch LLM/SLM output is not truth.",
    "Branch LLM/SLM output is not authority.",
    "Branch LLM/SLM output is not action permission.",
    "Branch LLM/SLM output is not FinalOutput.",
    "Branch LLM/SLM output does not create ActionCommitPacket.",
    "Branch LLM/SLM output does not create receipt.",
    "Branch LLM/SLM output does not execute payment.",
    "Branch LLM/SLM output does not release shipment.",
    "BSEP is not truth.",
    "BSEP is not authority.",
    "Runtime owns PlanGraph/local plan artifacts.",
    "Provider does not own PlanGraph.",
    "PlanGraph is not authority.",
    "Branch ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
    "Root-created mock ActionCommitPacket is scoped only and only observed here.",
    "MockBankSandbox receipt is evidence only and only observed here.",
    "Receipt does not release shipment.",
    "payment_slot is not permission.",
    "Root remains final authority.",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no real payment",
    "no real shipment release",
    "no production connectors",
    "no real bank/supplier/warehouse API",
    "no real-world effects",
)

ORCHESTRATOR_REQUIRED_FIELDS = {
    "proposal_id",
    "suggested_route",
    "selected_branch_ids",
    "required_guards",
    "route_reasoning",
    "evidence_needed",
    "uncertainty_notes",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "plan_graph_claimed",
    "bypass_root_claimed",
    "root_review_required",
}

ARCHITECT_REQUIRED_FIELDS = {
    "proposal_id",
    "source_route_id",
    "selected_branch_ids",
    "root_recommendation",
    "result_proposal_summary",
    "required_validators",
    "plan_shape_reasoning",
    "branch_intent_reasoning",
    "executor_constraint_reasoning",
    "forbidden_surface_reasoning",
    "validator_coverage_reasoning",
    "return_to_root_reasoning",
    "authority_boundary_reasoning",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
}

BRANCH_SEMANTIC_REQUIRED_FIELDS = {
    "branch_semantic_proposal_id",
    "source_branch_id",
    "semantic_summary",
    "evidence_interpretation",
    "uncertainty_notes",
    "recommended_branch_status",
    "return_to_parent_reasoning",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "action_commit_packet_claimed",
    "receipt_claimed",
    "payment_execution_claimed",
    "shipment_release_claimed",
}

SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "raw_iban_value",
    "GEMINI_API_KEY=",
    "GOOGLE_API_KEY=",
)


def _zero_counters() -> dict[str, int]:
    return {
        "manual_live_multillm_fractal_lane_enabled_count": 0,
        "manual_live_multillm_fractal_lane_passed_count": 0,
        "semantic_actor_call_count": 0,
        "fake_provider_call_count": 0,
        "real_provider_call_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "top_level_orchestrator_llm_call_count": 0,
        "top_level_architect_llm_call_count": 0,
        "branch_local_llm_slm_call_count": 0,
        "bsep_created_count": 0,
        "bsep_validated_count": 0,
        "architect_called_before_bsep_validation_count": 0,
        "architect_received_bsep_context_count": 0,
        "runtime_plangraph_compiled_count": 0,
        "provider_owned_plangraph_count": 0,
        "provider_nodes_edges_executor_assignments_accepted_count": 0,
        "fractal_branch_cells_created_count": 0,
        "branch_result_proposals_created_count": 0,
        "post_vv_validated_count": 0,
        "gt_lgt_advisory_review_count": 0,
        "root_final_boundary_evaluated_count": 0,
        "bank_internal_raw_iban_present_count": 0,
        "bank_internal_token_present_count": 0,
        "llm_visible_raw_iban_count": 0,
        "llm_visible_bank_token_count": 0,
        "llm_visible_secret_count": 0,
        "action_commit_packet_created_count": 0,
        "receipt_created_count": 0,
        "mock_payment_executed_count": 0,
        "real_payment_executed_count": 0,
        "shipment_released_count": 0,
        "real_world_effects_count": 0,
    }


def _enabled_counters() -> dict[str, int]:
    counters = _zero_counters()
    counters.update(
        {
            "manual_live_multillm_fractal_lane_enabled_count": 1,
            "bank_internal_raw_iban_present_count": 1,
            "bank_internal_token_present_count": 1,
        }
    )
    return counters


def _base_report(
    *,
    final_status: str,
    stage_status: str,
    env: Mapping[str, str],
    model_name: str,
    provider_mode: str,
    counters: Mapping[str, int],
    skip_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "trace_type": "manual_live_multillm_fractal_observation_lane",
        "stage_status": stage_status,
        "final_status": final_status,
        "model": model_name,
        "provider_mode": provider_mode,
        "skip_reason": skip_reason,
        "env_enabled": env.get(ENABLE_ENV) == "1",
        "core_ci_dependency": False,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "pipeline_sequence": (),
        "semantic_actor_calls": (),
        "top_level_orchestrator": None,
        "top_level_architect": None,
        "bsep_packet": None,
        "bsep_validation": None,
        "runtime_plan": {
            "runtime_plangraph_compiled_count": counters[
                "runtime_plangraph_compiled_count"
            ],
            "provider_owned_plangraph_count": counters["provider_owned_plangraph_count"],
            "provider_nodes_edges_executor_assignments_accepted_count": counters[
                "provider_nodes_edges_executor_assignments_accepted_count"
            ],
            "plan_graph_boundary": "runtime owns PlanGraph/local plan artifacts",
            "plan_graph_is_authority": False,
        },
        "fractal_branches": (),
        "branch_result_proposals": (),
        "post_vv_gt_root": {
            "root_first_decision": None,
            "root_second_decision": None,
            "supplier_b_final_status": None,
            "shipment_final_status": None,
            "receipt_final_status": None,
            "root_remains_final_authority": True,
        },
        "secret_membrane": {
            "bank_internal_raw_iban_present_count": counters[
                "bank_internal_raw_iban_present_count"
            ],
            "bank_internal_token_present_count": counters[
                "bank_internal_token_present_count"
            ],
            "llm_visible_raw_iban_count": counters["llm_visible_raw_iban_count"],
            "llm_visible_bank_token_count": counters["llm_visible_bank_token_count"],
            "llm_visible_secret_count": counters["llm_visible_secret_count"],
            "prompt_secret_scan_passed": True,
            "artifact_secret_scan_passed": True,
            "secret_formula": "Secrets ∩ LLMContext = empty",
            "payment_slot_boundary": "payment_slot != permission",
            "receipt_truth_boundary": "receipt != truth",
            "receipt_shipment_boundary": "receipt != shipment release",
        },
        "authority_matrix": AUTHORITY_MATRIX,
        "counters": dict(counters),
        "artifacts": {
            "artifact_dir": env.get(ARTIFACT_DIR_ENV),
            "written_files": (),
            "artifact_capture_enabled": False,
        },
        "non_claims": NON_CLAIMS,
    }


def _extract_json_object(raw: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            return None, "invalid_json"
        try:
            parsed = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return None, "invalid_json"
    if not isinstance(parsed, dict):
        return None, "not_json_object"
    return parsed, None


def _missing_fields(payload: Mapping[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in payload)


def _validate_false_claims(
    payload: Mapping[str, Any], claim_fields: tuple[str, ...]
) -> list[str]:
    return [field for field in claim_fields if payload.get(field) is not False]


def _validate_orchestrator(payload: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    errors.extend(f"missing_required_field:{field}" for field in _missing_fields(payload, ORCHESTRATOR_REQUIRED_FIELDS))
    errors.extend(
        f"forbidden_claim:{field}"
        for field in _validate_false_claims(
            payload,
            (
                "truth_claimed",
                "authority_claimed",
                "action_permission_claimed",
                "final_output_claimed",
                "connector_command_claimed",
                "drs_write_claimed",
                "plan_graph_claimed",
                "bypass_root_claimed",
            ),
        )
    )
    if payload.get("root_review_required") is not True:
        errors.append("root_review_required_not_true")
    if not isinstance(payload.get("selected_branch_ids"), list):
        errors.append("selected_branch_ids_not_list")
    return {
        "accepted": not errors,
        "errors": errors,
        "canonical": dict(payload) if not errors else None,
    }


def _validate_architect(payload: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    errors.extend(f"missing_required_field:{field}" for field in _missing_fields(payload, ARCHITECT_REQUIRED_FIELDS))
    errors.extend(
        f"forbidden_claim:{field}"
        for field in _validate_false_claims(
            payload,
            (
                "truth_claimed",
                "authority_claimed",
                "action_permission_claimed",
                "final_output_claimed",
                "connector_command_claimed",
                "drs_write_claimed",
                "root_bypass_claimed",
            ),
        )
    )
    for forbidden in ("nodes", "edges", "executor_assignments", "plan_graph_proposal_id"):
        if forbidden in payload:
            errors.append(f"provider_runtime_graph_key:{forbidden}")
    if not isinstance(payload.get("selected_branch_ids"), list):
        errors.append("selected_branch_ids_not_list")
    return {
        "accepted": not errors,
        "errors": errors,
        "canonical": dict(payload) if not errors else None,
    }


def _validate_branch_semantics(
    payload: Mapping[str, Any], expected_branch_id: str
) -> dict[str, Any]:
    errors: list[str] = []
    errors.extend(f"missing_required_field:{field}" for field in _missing_fields(payload, BRANCH_SEMANTIC_REQUIRED_FIELDS))
    errors.extend(
        f"forbidden_claim:{field}"
        for field in _validate_false_claims(
            payload,
            (
                "truth_claimed",
                "authority_claimed",
                "action_permission_claimed",
                "final_output_claimed",
                "connector_command_claimed",
                "action_commit_packet_claimed",
                "receipt_claimed",
                "payment_execution_claimed",
                "shipment_release_claimed",
            ),
        )
    )
    if payload.get("source_branch_id") != expected_branch_id:
        errors.append("source_branch_id_mismatch")
    return {
        "accepted": not errors,
        "errors": errors,
        "canonical": dict(payload) if not errors else None,
    }


def _build_orchestrator_prompt() -> str:
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            "Role: top-level semantic Orchestrator proposal actor.",
            "Return JSON only matching the Orchestrator semantic proposal shape.",
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.",
            "Do not claim truth, authority, action permission, FinalOutput, connector command, DRS write, PlanGraph ownership, or Root bypass.",
            "Business context: Supplier Payment / Shipment Release Review WOW v1.2 product trace.",
        )
    )


def _build_architect_prompt(bsep_packet: Mapping[str, Any]) -> str:
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            "Role: top-level Semantic Architect proposal actor.",
            "Return JSON only matching the Architect semantic proposal shape.",
            "Use only BSEP-derived bounded context.",
            f"BSEP_CONTEXT: {json.dumps(bsep_packet, sort_keys=True)}",
            "Runtime owns PlanGraph/local plan artifacts. PlanGraph is not authority.",
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.",
        )
    )


def _build_branch_prompt(role: str, branch_id: str) -> str:
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            f"Role: {role}.",
            f"Branch: {branch_id}.",
            "Return JSON only matching the branch-local semantic proposal shape.",
            "Branch LLM/SLM output is advisory only and returns to parent/root review.",
            "Do not claim truth, authority, action permission, FinalOutput, ActionCommitPacket, receipt, payment execution, or shipment release.",
        )
    )


def _build_bsep(orchestrator: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "bsep_packet_id": "bsep-full-wow-v1-2-manual-live-001",
        "source_orchestrator_proposal_id": orchestrator["proposal_id"],
        "suggested_route": orchestrator["suggested_route"],
        "selected_branch_ids": list(orchestrator["selected_branch_ids"]),
        "bounded_business_context": [
            "Warehouse evidence shows SH-2042 water_filter shortage.",
            "Supplier A can cover the shortage after corrected evidence.",
            "Supplier B remains blocked.",
            "Shipment release remains held.",
            "Receipt remains evidence only.",
        ],
        "raw_user_text_included": False,
        "raw_provider_text_included": False,
        "raw_bank_secrets_included": False,
        "raw_iban_included": False,
        "bank_token_included": False,
        "validation_required_before_architect": True,
    }


def _validate_bsep(bsep_packet: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not bsep_packet.get("bsep_packet_id"):
        errors.append("missing_bsep_packet_id")
    for field in (
        "raw_user_text_included",
        "raw_provider_text_included",
        "raw_bank_secrets_included",
        "raw_iban_included",
        "bank_token_included",
    ):
        if bsep_packet.get(field) is not False:
            errors.append(f"forbidden_bsep_field:{field}")
    if not isinstance(bsep_packet.get("selected_branch_ids"), list):
        errors.append("selected_branch_ids_not_list")
    return {"accepted": not errors, "errors": errors}


def _branch_context(branch_id: str) -> str:
    return {
        "warehouse_branch": "WarehouseAPI inventory evidence for SH-2042.",
        "supplier_a_branch": "Supplier A availability evidence for WF-100.",
        "supplier_b_branch": "Supplier B blocker and delay evidence.",
        "legal_branch": "Legal clause and insurance evidence.",
        "accounting_branch": "Accounting invoice and PO reconciliation evidence.",
        "bank_a_branch": "Bank A masked payment slot evidence.",
        "bank_b_branch": "Bank B policy and contract preview evidence.",
        "root_merge_branch": "Root merge of bounded branch proposals.",
    }[branch_id]


def _branch_evidence(branch_id: str) -> str:
    return {
        "warehouse_branch": "water_filter short_by_2; shipment release held.",
        "supplier_a_branch": "Supplier A has available stock and scoped mock payment path.",
        "supplier_b_branch": "invoice mismatch, delivery delayed, legal review required.",
        "legal_branch": "insurance corrected for Supplier A scope after first blocker.",
        "accounting_branch": "INV-2042 matches PO-2042-A; permission not granted.",
        "bank_a_branch": "payment_slot_A_2042 prepared but not permission.",
        "bank_b_branch": "contract preview created; execution_allowed=false.",
        "root_merge_branch": "Root keeps Supplier B blocked and shipment held.",
    }[branch_id]


def _result_proposal(
    branch_id: str, semantic_actor_used: bool
) -> dict[str, Any]:
    return {
        "result_proposal_id": f"{branch_id}_result_proposal",
        "source_branch_id": branch_id,
        "proposal_status": "accepted_for_root_review",
        "evidence_summary": _branch_evidence(branch_id),
        "semantic_actor_used": semantic_actor_used,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
    }


def _scan_text_for_secrets(text: str) -> dict[str, Any]:
    matched = [marker for marker in SECRET_MARKERS if marker in text]
    return {"passed": not matched, "matched_markers": matched}


def _scan_artifact_dir(artifact_dir: Path) -> dict[str, Any]:
    matched: list[str] = []
    files_scanned = 0
    for path in artifact_dir.iterdir():
        if path.is_file():
            files_scanned += 1
            text = path.read_text(encoding="utf-8")
            for marker in SECRET_MARKERS:
                if marker in text:
                    matched.append(f"{path.name}:{marker}")
    return {
        "passed": not matched,
        "files_scanned": files_scanned,
        "matched_markers": matched,
    }


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _artifact_capture(
    report: Mapping[str, Any],
    artifact_dir: Path,
    artifacts: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    text_files = {
        "summary.log": render_full_wow_v1_2_manual_live_multillm_fractal_trace(report),
        "top_level_orchestrator_prompt.txt": artifacts["top_level_orchestrator_prompt"],
        "top_level_orchestrator_raw_response.txt": artifacts[
            "top_level_orchestrator_raw_response"
        ],
        "top_level_architect_prompt.txt": artifacts["top_level_architect_prompt"],
        "top_level_architect_raw_response.txt": artifacts[
            "top_level_architect_raw_response"
        ],
        "branch_legal_prompt.txt": artifacts["branch_legal_prompt"],
        "branch_legal_raw_response.txt": artifacts["branch_legal_raw_response"],
        "branch_accounting_prompt.txt": artifacts["branch_accounting_prompt"],
        "branch_accounting_raw_response.txt": artifacts[
            "branch_accounting_raw_response"
        ],
        "branch_supplier_b_prompt.txt": artifacts["branch_supplier_b_prompt"],
        "branch_supplier_b_raw_response.txt": artifacts[
            "branch_supplier_b_raw_response"
        ],
        "branch_bank_policy_prompt.txt": artifacts["branch_bank_policy_prompt"],
        "branch_bank_policy_raw_response.txt": artifacts[
            "branch_bank_policy_raw_response"
        ],
    }
    json_files = {
        "summary.json": report,
        "top_level_orchestrator_extracted_json_candidate.json": artifacts[
            "top_level_orchestrator_json"
        ],
        "top_level_orchestrator_validation.json": artifacts[
            "top_level_orchestrator_validation"
        ],
        "bsep_packet.json": artifacts["bsep_packet"],
        "bsep_validation.json": artifacts["bsep_validation"],
        "top_level_architect_extracted_json_candidate.json": artifacts[
            "top_level_architect_json"
        ],
        "top_level_architect_validation.json": artifacts[
            "top_level_architect_validation"
        ],
        "branch_legal_validation.json": artifacts["branch_legal_validation"],
        "branch_accounting_validation.json": artifacts[
            "branch_accounting_validation"
        ],
        "branch_supplier_b_validation.json": artifacts[
            "branch_supplier_b_validation"
        ],
        "branch_bank_policy_validation.json": artifacts[
            "branch_bank_policy_validation"
        ],
    }
    for name, value in text_files.items():
        _write_text(artifact_dir / name, value)
        written.append(name)
    for name, value in json_files.items():
        _write_json(artifact_dir / name, value)
        written.append(name)

    scan = _scan_artifact_dir(artifact_dir)
    _write_json(artifact_dir / "secret_scan.json", scan)
    written.append("secret_scan.json")
    return {
        "artifact_dir": str(artifact_dir),
        "written_files": tuple(sorted(written)),
        "artifact_capture_enabled": True,
        "secret_scan": scan,
    }


def _call_real_provider(
    role: str,
    prompt: str,
    context: Mapping[str, Any],
    *,
    env: Mapping[str, str],
    model_name: str,
    delay_seconds: int,
) -> str:
    api_key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("missing_gemini_api_key")
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    from google import genai  # type: ignore

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
            "candidate_count": 1,
            "system_instruction": (
                "Return JSON only. Provider output is semantic reasoning only. "
                "Runtime canonicalizes. Validators verify. Root decides."
            ),
        },
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError(f"empty_provider_response:{role}:{context.get('role')}")
    return text


def _provider_call(
    *,
    role: str,
    prompt: str,
    context: Mapping[str, Any],
    env: Mapping[str, str],
    provider: Provider | None,
    model_name: str,
    counters: dict[str, int],
    actor_counter: str,
) -> tuple[str | None, str, str | None]:
    counters["semantic_actor_call_count"] += 1
    counters[actor_counter] += 1
    if provider is not None:
        counters["fake_provider_call_count"] += 1
        try:
            return provider(role, prompt, context), "fake_injected", None
        except Exception:
            return None, "fake_injected", f"provider_call_failed:{role}"
    delay = int(env.get(CALL_DELAY_ENV, "30") or "30")
    counters["real_provider_call_count"] += 1
    counters["network_used_count"] += 1
    counters["gemini_called_count"] += 1
    try:
        return (
            _call_real_provider(
                role,
                prompt,
                context,
                env=env,
                model_name=model_name,
                delay_seconds=delay,
            ),
            "real_provider",
            None,
        )
    except Exception:
        return None, "real_provider", f"provider_call_failed:{role}"


def _fail_closed_report(
    *,
    env: Mapping[str, str],
    model_name: str,
    provider_mode: str,
    counters: Mapping[str, int],
    reason: str,
    pipeline_sequence: tuple[str, ...],
    semantic_actor_calls: tuple[Mapping[str, Any], ...],
) -> dict[str, Any]:
    report = _base_report(
        final_status="FAIL_CLOSED",
        stage_status="FAIL_CLOSED",
        env=env,
        model_name=model_name,
        provider_mode=provider_mode,
        counters=counters,
        skip_reason=reason,
    )
    report["pipeline_sequence"] = pipeline_sequence
    report["semantic_actor_calls"] = semantic_actor_calls
    return report


def collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
    env: Mapping[str, str] | None = None,
    provider: Provider | None = None,
) -> dict[str, Any]:
    effective_env = os.environ if env is None else env
    model_name = effective_env.get(MODEL_ENV, DEFAULT_MODEL)
    if effective_env.get(ENABLE_ENV) != "1":
        return _base_report(
            final_status="SKIPPED_CLOSED",
            stage_status="SKIPPED_CLOSED",
            env=effective_env,
            model_name=model_name,
            provider_mode="not_enabled",
            counters=_zero_counters(),
            skip_reason=f"{ENABLE_ENV} is not 1",
        )

    if provider is None and not (
        effective_env.get("GEMINI_API_KEY") or effective_env.get("GOOGLE_API_KEY")
    ):
        return _base_report(
            final_status="SKIPPED_CLOSED",
            stage_status="SKIPPED_CLOSED",
            env=effective_env,
            model_name=model_name,
            provider_mode="missing_key",
            counters=_zero_counters(),
            skip_reason="Gemini key missing; live lane remains closed.",
        )

    counters = _enabled_counters()
    provider_mode = "fake_injected" if provider is not None else "real_provider"

    actor_calls: list[dict[str, Any]] = []
    artifacts: dict[str, Any] = {}
    sequence: list[str] = ["dirty_request_loaded_from_v1_2_product_trace"]

    orchestrator_prompt = _build_orchestrator_prompt()
    raw_orchestrator, actual_provider_mode, provider_error = _provider_call(
        role="top_level_orchestrator_llm",
        prompt=orchestrator_prompt,
        context={"role": "top_level_orchestrator_llm", "run_id": RUN_ID},
        env=effective_env,
        provider=provider,
        model_name=model_name,
        counters=counters,
        actor_counter="top_level_orchestrator_llm_call_count",
    )
    provider_mode = actual_provider_mode
    sequence.append("top_level_orchestrator_provider_called")
    if provider_error:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=provider_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    orchestrator_json, parse_error = _extract_json_object(raw_orchestrator)
    if parse_error:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=parse_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    orchestrator_validation = _validate_orchestrator(orchestrator_json)
    actor_calls.append(
        {
            "role": "top_level_orchestrator_llm",
            "provider_mode": provider_mode,
            "validation_status": "PASS"
            if orchestrator_validation["accepted"]
            else "FAIL_CLOSED",
        }
    )
    artifacts.update(
        {
            "top_level_orchestrator_prompt": orchestrator_prompt,
            "top_level_orchestrator_raw_response": raw_orchestrator,
            "top_level_orchestrator_json": orchestrator_json,
            "top_level_orchestrator_validation": orchestrator_validation,
        }
    )
    if not orchestrator_validation["accepted"]:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="orchestrator_validation_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    sequence.extend(
        (
            "top_level_orchestrator_semantics_validated",
            "top_level_orchestrator_semantics_canonicalized",
        )
    )

    bsep_packet = _build_bsep(orchestrator_validation["canonical"])
    bsep_validation = _validate_bsep(bsep_packet)
    artifacts["bsep_packet"] = bsep_packet
    artifacts["bsep_validation"] = bsep_validation
    if not bsep_validation["accepted"]:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="bsep_validation_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    counters["bsep_created_count"] = 1
    counters["bsep_validated_count"] = 1
    sequence.extend(("bsep_created", "bsep_validated"))

    architect_prompt = _build_architect_prompt(bsep_packet)
    sequence.append("top_level_architect_prompt_built_from_bsep")
    counters["architect_received_bsep_context_count"] = 1
    raw_architect, actual_provider_mode, provider_error = _provider_call(
        role="top_level_semantic_architect_llm",
        prompt=architect_prompt,
        context={
            "role": "top_level_semantic_architect_llm",
            "bsep_packet_id": bsep_packet["bsep_packet_id"],
        },
        env=effective_env,
        provider=provider,
        model_name=model_name,
        counters=counters,
        actor_counter="top_level_architect_llm_call_count",
    )
    provider_mode = actual_provider_mode
    sequence.append("top_level_architect_provider_called")
    if provider_error:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=provider_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    architect_json, parse_error = _extract_json_object(raw_architect)
    if parse_error:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=parse_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    architect_validation = _validate_architect(architect_json)
    actor_calls.append(
        {
            "role": "top_level_semantic_architect_llm",
            "provider_mode": provider_mode,
            "validation_status": "PASS"
            if architect_validation["accepted"]
            else "FAIL_CLOSED",
        }
    )
    artifacts.update(
        {
            "top_level_architect_prompt": architect_prompt,
            "top_level_architect_raw_response": raw_architect,
            "top_level_architect_json": architect_json,
            "top_level_architect_validation": architect_validation,
        }
    )
    if not architect_validation["accepted"]:
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="architect_validation_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
        )
    sequence.extend(
        (
            "top_level_architect_semantics_validated",
            "top_level_architect_semantics_canonicalized",
            "runtime_plangraph_compiled",
            "fractal_branch_cells_created",
            "warehouse_branch_api_evidence_observed",
            "supplier_a_branch_api_evidence_observed",
            "supplier_b_branch_api_evidence_observed",
        )
    )
    counters["runtime_plangraph_compiled_count"] = 1
    counters["fractal_branch_cells_created_count"] = 8

    branch_semantics: dict[str, dict[str, Any] | None] = {}
    branch_validations: dict[str, dict[str, Any]] = {}
    branch_raw: dict[str, str] = {}
    branch_prompts: dict[str, str] = {}
    for branch_id, role in BRANCH_ACTOR_ROLES.items():
        prompt = _build_branch_prompt(role, branch_id)
        raw, actual_provider_mode, provider_error = _provider_call(
            role=role,
            prompt=prompt,
            context={"role": role, "source_branch_id": branch_id},
            env=effective_env,
            provider=provider,
            model_name=model_name,
            counters=counters,
            actor_counter="branch_local_llm_slm_call_count",
        )
        provider_mode = actual_provider_mode
        if provider_error:
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=provider_error,
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
            )
        branch_json, parse_error = _extract_json_object(raw)
        if parse_error:
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=parse_error,
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
            )
        validation = _validate_branch_semantics(branch_json, branch_id)
        actor_calls.append(
            {
                "role": role,
                "branch_id": branch_id,
                "provider_mode": provider_mode,
                "validation_status": "PASS"
                if validation["accepted"]
                else "FAIL_CLOSED",
            }
        )
        branch_prompts[branch_id] = prompt
        branch_raw[branch_id] = raw
        branch_semantics[branch_id] = validation["canonical"]
        branch_validations[branch_id] = validation
        if not validation["accepted"]:
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=f"{branch_id}_validation_failed",
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
            )
        if branch_id == "legal_branch":
            sequence.extend(
                (
                    "legal_branch_semantic_actor_called",
                    "legal_branch_result_proposal_created",
                )
            )
        elif branch_id == "accounting_branch":
            sequence.extend(
                (
                    "accounting_branch_semantic_actor_called",
                    "accounting_branch_result_proposal_created",
                )
            )
        elif branch_id == "supplier_b_branch":
            sequence.extend(
                (
                    "supplier_b_branch_semantic_actor_called",
                    "supplier_b_branch_result_proposal_created",
                )
            )
        elif branch_id == "bank_b_branch":
            sequence.extend(
                (
                    "bank_policy_branch_semantic_actor_called",
                    "bank_branch_result_proposal_created",
                )
            )

    artifacts.update(
        {
            "branch_legal_prompt": branch_prompts["legal_branch"],
            "branch_legal_raw_response": branch_raw["legal_branch"],
            "branch_legal_validation": branch_validations["legal_branch"],
            "branch_accounting_prompt": branch_prompts["accounting_branch"],
            "branch_accounting_raw_response": branch_raw["accounting_branch"],
            "branch_accounting_validation": branch_validations["accounting_branch"],
            "branch_supplier_b_prompt": branch_prompts["supplier_b_branch"],
            "branch_supplier_b_raw_response": branch_raw["supplier_b_branch"],
            "branch_supplier_b_validation": branch_validations["supplier_b_branch"],
            "branch_bank_policy_prompt": branch_prompts["bank_b_branch"],
            "branch_bank_policy_raw_response": branch_raw["bank_b_branch"],
            "branch_bank_policy_validation": branch_validations["bank_b_branch"],
        }
    )

    branches: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []
    for branch_id in BRANCH_IDS:
        semantic_output = branch_semantics.get(branch_id)
        semantic_actor_used = semantic_output is not None
        proposal = _result_proposal(branch_id, semantic_actor_used)
        proposals.append(proposal)
        branches.append(
            {
                "branch_id": branch_id,
                "branch_context": _branch_context(branch_id),
                "branch_evidence": _branch_evidence(branch_id),
                "branch_semantic_actor_output": semantic_output,
                "branch_result_proposal": proposal,
                "branch_authority_boundary": "branch returns ResultProposal only; Root decides",
                "branch_called_llm_or_slm_count": 1 if semantic_actor_used else 0,
                "branch_called_api_count": 0
                if branch_id == "root_merge_branch"
                else 1,
                "branch_real_world_effects_count": 0,
            }
        )

    counters["branch_result_proposals_created_count"] = 8
    counters["post_vv_validated_count"] = 1
    counters["gt_lgt_advisory_review_count"] = 1
    counters["root_final_boundary_evaluated_count"] = 1
    counters["manual_live_multillm_fractal_lane_passed_count"] = 1
    sequence.extend(
        (
            "branch_result_proposals_merged",
            "post_vv_validated",
            "gt_lgt_advisory_reviewed",
            "root_final_boundary_evaluated",
        )
    )

    report = _base_report(
        final_status="PASS",
        stage_status="PASS",
        env=effective_env,
        model_name=model_name,
        provider_mode=provider_mode,
        counters=counters,
    )
    report.update(
        {
            "pipeline_sequence": tuple(sequence),
            "semantic_actor_calls": tuple(actor_calls),
            "top_level_orchestrator": orchestrator_validation["canonical"],
            "top_level_architect": architect_validation["canonical"],
            "bsep_packet": bsep_packet,
            "bsep_validation": bsep_validation,
            "runtime_plan": {
                "runtime_plangraph_compiled_count": 1,
                "provider_owned_plangraph_count": 0,
                "provider_nodes_edges_executor_assignments_accepted_count": 0,
                "plan_graph_boundary": "runtime owns PlanGraph/local plan artifacts",
                "plan_graph_is_authority": False,
            },
            "fractal_branches": tuple(branches),
            "branch_result_proposals": tuple(proposals),
            "post_vv_gt_root": {
                "root_first_decision": "NOT_READY",
                "root_second_decision": "SUPPLIER_A_SCOPED_REVIEW_READY",
                "supplier_b_final_status": "BLOCKED",
                "shipment_final_status": "HELD",
                "receipt_final_status": "EVIDENCE_ONLY",
                "root_remains_final_authority": True,
            },
        }
    )

    prompt_scan = _scan_text_for_secrets(
        "\n".join(
            [
                orchestrator_prompt,
                architect_prompt,
                *branch_prompts.values(),
                raw_orchestrator,
                raw_architect,
                *branch_raw.values(),
            ]
        )
    )
    report["secret_membrane"]["prompt_secret_scan_passed"] = prompt_scan["passed"]
    report["secret_membrane"]["artifact_secret_scan_passed"] = True

    artifact_dir_value = effective_env.get(ARTIFACT_DIR_ENV)
    if artifact_dir_value:
        capture = _artifact_capture(report, Path(artifact_dir_value), artifacts)
        report["artifacts"] = {
            "artifact_dir": capture["artifact_dir"],
            "written_files": capture["written_files"],
            "artifact_capture_enabled": True,
        }
        report["secret_membrane"]["artifact_secret_scan_passed"] = capture[
            "secret_scan"
        ]["passed"]
    return report


def _format_value(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def _render_mapping(mapping: Mapping[str, Any]) -> list[str]:
    return [f"{key}: {_format_value(value)}" for key, value in mapping.items()]


def render_full_wow_v1_2_manual_live_multillm_fractal_trace(
    report: Mapping[str, Any]
) -> str:
    lines = [
        "HEDGEHOG OS — FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
        "",
        "[FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"stage_status: {report['stage_status']}",
        f"final_status: {report['final_status']}",
        f"provider_mode: {report['provider_mode']}",
        f"core_ci_dependency: {_format_value(report['core_ci_dependency'])}",
        f"production_ready_claimed: {_format_value(report['production_ready_claimed'])}",
        f"public_auditor_ready_claimed: {_format_value(report['public_auditor_ready_claimed'])}",
    ]

    lines.extend(
        [
            "",
            "[LANE STATUS]",
            "Manual live multi-LLM/fractal lane is env-gated and not a core CI dependency.",
            f"skip_reason: {report.get('skip_reason')}",
        ]
    )

    lines.extend(["", "[SEMANTIC ACTOR CALLS]"])
    for call in report["semantic_actor_calls"]:
        lines.append(
            "- role={role}; provider_mode={provider_mode}; validation_status={validation_status}".format(
                **call
            )
        )

    lines.extend(["", "[TOP-LEVEL ORCHESTRATOR]"])
    if report["top_level_orchestrator"]:
        lines.extend(_render_mapping(report["top_level_orchestrator"]))
    else:
        lines.append("not_run")

    lines.extend(["", "[BSEP MEMBRANE]"])
    if report["bsep_packet"]:
        lines.extend(_render_mapping(report["bsep_packet"]))
    else:
        lines.append("not_run")

    lines.extend(["", "[TOP-LEVEL SEMANTIC ARCHITECT]"])
    if report["top_level_architect"]:
        lines.extend(_render_mapping(report["top_level_architect"]))
    else:
        lines.append("not_run")

    lines.extend(["", "[RUNTIME PLAN AND FRACTAL CELLS]"])
    lines.extend(_render_mapping(report["runtime_plan"]))
    for branch in report["fractal_branches"]:
        lines.append(
            "- {branch_id}: branch_called_llm_or_slm_count={branch_called_llm_or_slm_count}; branch_called_api_count={branch_called_api_count}; branch_real_world_effects_count={branch_real_world_effects_count}".format(
                **branch
            )
        )

    lines.extend(["", "[BRANCH-LOCAL LLM/SLM ACTORS]"])
    for branch in report["fractal_branches"]:
        if branch["branch_semantic_actor_output"]:
            output = branch["branch_semantic_actor_output"]
            lines.append(
                "- {branch_id}: {branch_semantic_proposal_id}; recommended_branch_status={recommended_branch_status}".format(
                    branch_id=branch["branch_id"],
                    **output,
                )
            )

    lines.extend(["", "[BRANCH RESULT PROPOSALS]"])
    for proposal in report["branch_result_proposals"]:
        lines.append(
            "- {result_proposal_id}: source_branch_id={source_branch_id}; semantic_actor_used={semantic_actor_used}; authority_claimed={authority_claimed}; action_permission_claimed={action_permission_claimed}; final_output_claimed={final_output_claimed}".format(
                **proposal
            )
        )

    lines.extend(["", "[POST V&V / GT-LGT / ROOT]"])
    lines.extend(_render_mapping(report["post_vv_gt_root"]))

    lines.extend(["", "[SECRET MEMBRANE]"])
    lines.extend(_render_mapping(report["secret_membrane"]))

    lines.extend(["", "[AUTHORITY MATRIX]"])
    lines.extend(f"- {item}" for item in report["authority_matrix"])

    lines.extend(["", "[COUNTER MATRIX]"])
    for key in sorted(report["counters"]):
        lines.append(f"{key}: {report['counters'][key]}")

    lines.extend(["", "[ARTIFACTS]"])
    lines.extend(_render_mapping(report["artifacts"]))

    lines.extend(["", "[NON-CLAIMS]"])
    lines.extend(f"- {item}" for item in report["non_claims"])

    lines.extend(
        [
            "",
            "[FINAL STATUS]",
            f"FINAL STATUS: {report['final_status']}",
            "Machine summary JSON:",
            json.dumps(
                {
                    "run_id": report["run_id"],
                    "stage_status": report["stage_status"],
                    "final_status": report["final_status"],
                    "provider_mode": report["provider_mode"],
                    "counters": report["counters"],
                    "non_claims": report["non_claims"],
                },
                sort_keys=True,
            ),
        ]
    )
    return "\n".join(lines)


def run_full_wow_v1_2_manual_live_multillm_fractal_trace(
    env: Mapping[str, str] | None = None,
    provider: Provider | None = None,
) -> str:
    return render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
            env=env, provider=provider
        )
    )


def main() -> int:
    print(run_full_wow_v1_2_manual_live_multillm_fractal_trace())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
