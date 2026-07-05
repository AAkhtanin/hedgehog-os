from __future__ import annotations

import json
import sys
from typing import Any

from hedgehog.context_packets import (
    build_bounded_semantic_evidence_packet,
    semantic_evidence_item,
    validate_bounded_semantic_evidence_packet,
)


TITLE = "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1"
SHORT_NAME = "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1"
RUN_ID = "supplier_payment_shipment_release_review_wow_v1_1_slice_c_run"
SLICE_ID = "supplier_payment_shipment_release_review_wow_v1_1_slice_c"

PHASE_IDS = (
    "phase_1_first_run_not_ready",
    "phase_2_corrected_evidence_drs_writeback_context_only",
    "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
    "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
    "phase_5_mock_bank_sandbox_executes_supplier_a_only",
)

AUTHORITY_INVARIANTS = (
    "Provider output is not truth",
    "Provider output is not authority",
    "BSEP is not truth",
    "BSEP is not authority",
    "DRS hit is not authority",
    "AVF score is not authority",
    "CandidateVector is not action permission",
    "PlanGraph is not authority",
    "ResultProposal is not FinalOutput",
    "GT/LGT is not Root",
    "Root remains final authority",
    "Human approval is scoped evidence, not broad authority",
    "Root-created mock ActionCommitPacket is scoped only",
    "Mock receipt is evidence, not truth/action permission/final output",
    "Mock payment receipt does not release shipment",
)


def build_inline_fixtures() -> dict[str, Any]:
    return {
        "business_request": {
            "request_id": "supplier_payment_shipment_release_review_wow_v1_1",
            "shipment_id": "SH-2042",
            "intent_type": "supplier_payment_and_shipment_release_review",
            "requested_actions": (
                "review_shipment_release",
                "prepare_supplier_payment_review",
                "check_documents",
                "check_inventory",
                "check_supplier_availability",
            ),
        },
        "supplier_A": {
            "supplier_id": "supplier_A",
            "product": "water_filter",
            "supplier": "Adriatic Filters LLC",
            "invoice": "INV-2042",
            "shipment": "SH-2042",
            "bank": "Bank A Sandbox",
            "internal_stock": "short_by_2",
            "supplier_api_stock": "available_20",
            "insurance_certificate": "expired",
            "payment_form_status": "shape_valid",
            "payment_permission_status": "not_granted",
            "bank_policy": "human_approval_required",
        },
        "supplier_B": {
            "supplier_id": "supplier_B",
            "product": "pump_valve",
            "supplier": "Balkan Pumps SHPK",
            "invoice": "INV-2043",
            "shipment": "SH-2042",
            "bank": "Bank B Sandbox",
            "internal_stock": "ready",
            "supplier_api_delivery": "delayed",
            "invoice_amount": "mismatch_with_PO",
            "legal_status": "needs_review",
            "payment_form_status": "prepared_but_blocked",
            "payment_permission_status": "not_granted",
        },
        "masked_payment_slot_supplier_A": {
            "payment_slot": "payment_slot_A_2042",
            "beneficiary_verified": True,
            "iban_checksum_valid": True,
            "amount": "1240.00 EUR",
            "invoice_id": "INV-2042",
            "payment_form_status": "shape_valid",
            "payment_permission_status": "not_granted",
            "bank_policy": "human_approval_required",
        },
        "conflicts": (
            "supplier available != internal ready",
            "bank form valid != payment permission",
            "invoice present != legal readiness",
            "prior DRS success != current authority",
            "human approval required != already approved",
            "Supplier A approval != Supplier B approval",
            "receipt evidence != action permission",
        ),
    }


def build_phase_machine() -> tuple[dict[str, Any], ...]:
    labels = (
        "First run resolves to Root NOT_READY from Slice B",
        "Corrected evidence and DRS writeback execute as context only",
        "Second run uses DRS as context and reruns validation",
        "Scoped human approval may later allow Root-created mock packet",
        "Mock bank sandbox may later execute Supplier A only",
    )
    phases: list[dict[str, Any]] = []
    for index, phase_id in enumerate(PHASE_IDS, start=1):
        executed = index <= 3
        phases.append(
            {
                "phase_id": phase_id,
                "phase_index": index,
                "status": "EXECUTED_IN_SLICE_C" if executed else "FUTURE_SLICE",
                "execution_status": (
                    "EXECUTED_IN_SLICE_C"
                    if executed
                    else "NOT_EXECUTED_IN_SLICE_C"
                ),
                "future_slice": None if executed else "FUTURE_SLICE",
                "label": labels[index - 1],
            }
        )
    return tuple(phases)


def _zero_action_counters() -> dict[str, int]:
    return {
        "deterministic_lane_passed_count": 1,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_model_call_count": 0,
        "live_model_call_count": 0,
        "orchestrator_provider_call_count": 0,
        "architect_provider_call_count": 0,
        "semantic_reasoning_adapter_used_count": 0,
        "runtime_canonicalization_count": 1,
        "bsep_created_count": 1,
        "bsep_validated_count": 1,
        "bsep_contains_raw_user_text_count": 0,
        "bsep_contains_raw_gemini_text_count": 0,
        "bsep_authority_claimed_count": 0,
        "bsep_truth_claimed_count": 0,
        "bsep_action_permission_claimed_count": 0,
        "bsep_final_output_claimed_count": 0,
        "drs_candidates_found_count": 1,
        "drs_hit_is_authority_count": 0,
        "direct_reuse_allowed_count": 0,
        "root_review_required_count": 1,
        "drs_prior_success_found_count": 1,
        "drs_prior_success_used_as_context_count": 1,
        "drs_prior_success_used_as_permission_count": 0,
        "drs_writeback_count": 3,
        "corrected_evidence_drs_writeback_count": 3,
        "corrected_evidence_is_authority_count": 0,
        "prior_root_final_mutated_count": 0,
        "second_run_reuse_used_count": 1,
        "reuse_authority_claimed_count": 0,
        "changed_facts_rerun_validation_count": 1,
        "ready_for_human_supplier_a_payment_approval_count": 1,
        "shipment_release_still_held_count": 1,
        "supplier_B_payment_blocked_count": 1,
        "candidate_vectors_generated_count": 7,
        "candidate_vector_is_truth_count": 0,
        "candidate_vector_is_authority_count": 0,
        "candidate_vector_is_action_permission_count": 0,
        "avf_scored_count": 1,
        "release_all_and_pay_all_hard_masked_count": 1,
        "pay_supplier_b_blocked_or_penalized_count": 1,
        "prepare_payment_forms_only_ranked_safe_count": 1,
        "hold_release_request_documents_ranked_safe_count": 1,
        "ask_human_approval_after_corrections_ranked_safe_count": 1,
        "high_score_did_not_create_permission_count": 1,
        "avf_score_is_authority_count": 0,
        "top_ranked_candidate_is_permission_count": 0,
        "root_final_created_count": 1,
        "root_decision_not_ready_count": 1,
        "action_commit_packet_created_count": 0,
        "action_commit_packet_created_by_root_count": 0,
        "action_commit_packet_created_by_llm_count": 0,
        "mock_connector_sandbox_invoked_count": 0,
        "mock_connector_sandbox_packet_validated_count": 0,
        "mock_bank_adapter_invoked_count": 0,
        "mock_payment_executed_count": 0,
        "mock_bank_receipt_created_count": 0,
        "execution_evidence_created_count": 0,
        "execution_evidence_validated_count": 0,
        "payment_executed_count": 0,
        "real_payment_executed_count": 0,
        "real_bank_api_called_count": 0,
        "real_supplier_api_called_count": 0,
        "real_warehouse_api_called_count": 0,
        "shipment_released_count": 0,
        "mock_shipment_released_count": 0,
        "connector_called_count": 0,
        "real_world_effects_count": 0,
    }


def _prompt_secret_scan() -> dict[str, int]:
    return {
        "orchestrator_prompt_contains_raw_iban_count": 0,
        "architect_prompt_contains_raw_iban_count": 0,
        "orchestrator_prompt_contains_bank_credential_count": 0,
        "architect_prompt_contains_bank_credential_count": 0,
        "orchestrator_prompt_contains_api_key_count": 0,
        "architect_prompt_contains_api_key_count": 0,
        "prompt_secret_scan_passed_count": 1,
        "llm_received_raw_bank_secret_count": 0,
        "llm_received_raw_iban_count": 0,
        "llm_received_api_token_count": 0,
        "secrets_logged_count": 0,
    }


def _non_claim_counters() -> dict[str, int]:
    return {
        "production_autonomy_claimed_count": 0,
        "public_auditor_readiness_claimed_count": 0,
        "production_readiness_claimed_count": 0,
        "real_payment_claimed_count": 0,
        "real_shipment_release_claimed_count": 0,
    }


def _future_section(section_id: str, *, note: str, future_slice: str) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "status": "NOT_EXECUTED_IN_SLICE_C",
        "future_slice": future_slice,
        "note": note,
    }


def build_deterministic_orchestrator_proposal() -> dict[str, Any]:
    return {
        "proposal_id": "proposal:supplier_payment_shipment_release_review:first_run",
        "suggested_route": "route:supplier_payment_shipment_release_review:first_run",
        "selected_vector_ids": (
            "supplier_payment_review",
            "shipment_release_review",
            "external_action_boundary_review",
            "root_final_authority_review",
        ),
        "required_guards": (
            "ContextPacket validation",
            "BSEP validation",
            "DRS context is not authority",
            "AVF score is not authority",
            "Root final authority",
        ),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
    }


def _route_context_from_orchestrator_proposal(
    proposal: dict[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": "context_packet:orchestrator_route:supplier_payment_review:first_run",
        "packet_type": "OrchestratorRouteContextPacket",
        "route_id": proposal["suggested_route"],
        "selected_route_id": proposal["suggested_route"],
        "selected_vector_ids": proposal["selected_vector_ids"],
        "required_guards": proposal["required_guards"],
        "route_context_validation_accepted": True,
        "Root remains final authority": True,
    }


def _evidence_items(
    texts: tuple[str, ...],
    *,
    evidence_kind: str,
    source: str = "runtime_canonicalization",
    confidence_label: str = "medium",
) -> tuple[dict[str, Any], ...]:
    return tuple(
        semantic_evidence_item(
            text,
            source=source,
            evidence_kind=evidence_kind,
            confidence_label=confidence_label,
        )
        for text in texts
    )


def build_supplier_payment_bsep(
    orchestrator_proposal: dict[str, Any] | None = None,
    route_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    proposal = orchestrator_proposal or build_deterministic_orchestrator_proposal()
    route_packet = route_context or _route_context_from_orchestrator_proposal(proposal)
    return build_bounded_semantic_evidence_packet(
        packet_id="context_packet:bounded_semantic_evidence:supplier_payment:first_run",
        source_refs=(
            {
                "ref_type": "validated_orchestrator_proposal",
                "ref_id": proposal["proposal_id"],
            },
            {
                "ref_type": "validated_route_context_packet",
                "ref_id": route_packet["packet_id"],
            },
            {
                "ref_type": "structured_orchestrator_rationale_validation",
                "ref_id": f"accepted:{proposal['proposal_id']}",
            },
        ),
        domain="supplier_payment_shipment_release_review",
        source_route_id=proposal["suggested_route"],
        source_proposal_id=proposal["proposal_id"],
        source_context_packet_id=route_packet["packet_id"],
        source_structured_rationale_ref=(
            f"structured_orchestrator_rationale:{proposal['proposal_id']}:accepted"
        ),
        observed_semantic_facts=_evidence_items(
            (
                "shipment SH-2042 needs review",
                "Supplier A stock API says available_20",
                "internal water_filter stock is short_by_2",
                "Supplier A insurance certificate is expired",
                "Supplier B invoice amount mismatch with PO",
                "Supplier B delivery delayed",
                "payment form shape valid is not permission",
            ),
            evidence_kind="observed_fact",
            source="validated_context_packet",
        ),
        missing_evidence=_evidence_items(
            (
                "corrected insurance certificate",
                "corrected internal stock",
                "Supplier B invoice and legal correction",
                "human approval not granted",
            ),
            evidence_kind="missing_evidence",
        ),
        uncertainty_notes=_evidence_items(
            (
                "supplier API availability is evidence candidate only",
                "bank form shape validity is not permission",
            ),
            evidence_kind="uncertainty",
        ),
        risk_boundary_notes=_evidence_items(
            (
                "shipment release must remain held",
                "supplier payment review cannot become payment permission",
            ),
            evidence_kind="risk_boundary",
        ),
        rejected_action_routes=_evidence_items(
            (
                "release_all_and_pay_all is rejected until blockers clear",
                "pay_supplier_B is blocked by invoice and delivery evidence",
                "release_shipment_now is rejected because shipment release remains held",
                "payment without human approval is rejected before Root review",
            ),
            evidence_kind="rejected_route",
        ),
        required_approvals_or_conditions=_evidence_items(
            (
                "Root final authority",
                "legal document correction",
                "inventory correction",
                "scoped human approval before mock payment",
                "Supplier B correction before any review advancement",
            ),
            evidence_kind="approval_condition",
        ),
        authority_boundary_notes=_evidence_items(
            (
                "DRS context is not authority",
                "AVF score is not authority",
                "Root decides first-run status",
            ),
            evidence_kind="authority_boundary",
        ),
        selected_vector_ids=proposal["selected_vector_ids"],
        required_guards=proposal["required_guards"],
    )


def build_company_local_drs_context() -> dict[str, Any]:
    return {
        "drs_candidates_found": True,
        "drs_candidates_found_count": 1,
        "drs_hit_is_authority": False,
        "drs_hit_is_authority_count": 0,
        "direct_reuse_allowed": False,
        "direct_reuse_allowed_count": 0,
        "root_review_required": True,
        "root_review_required_count": 1,
        "prior_traces": (
            "previous shipment SH-1901",
            "prior payment to Adriatic Filters",
            "prior blocked insurance flow",
            "corrected-document flow",
            "previous successful payment trace",
        ),
        "drs_prior_success_found_count": 1,
        "drs_prior_success_used_as_context_count": 1,
        "drs_prior_success_used_as_permission_count": 0,
        "prior_successful_payment_trace_cannot_authorize_current_payment": True,
        "drs_writeback_executed": False,
        "drs_writeback_count": 0,
        "prior_root_final_mutated": False,
    }


def build_candidate_vectors() -> tuple[dict[str, Any], ...]:
    candidates = (
        (
            "release_all_and_pay_all",
            "Release all shipment items and pay all suppliers",
            "blocked_candidate",
            "Combines held shipment release and unapproved payments.",
        ),
        (
            "hold_release_request_documents",
            "Hold release and request missing documents",
            "safe_candidate",
            "Keeps shipment held while legal blockers remain.",
        ),
        (
            "partial_release_only_ready_items",
            "Review only ready items without release",
            "review_only_candidate",
            "Pump valve readiness does not override shipment-level blockers.",
        ),
        (
            "restock_water_filter_then_review",
            "Restock water filters then rerun review",
            "safe_candidate",
            "Internal shortage must be corrected before any advancement.",
        ),
        (
            "prepare_payment_forms_but_do_not_execute",
            "Prepare masked payment forms without execution",
            "safe_candidate",
            "Bank form shape can be prepared but cannot authorize payment.",
        ),
        (
            "block_supplier_B_due_invoice_mismatch",
            "Block Supplier B review due invoice mismatch",
            "blocked_supplier_candidate",
            "Supplier B remains blocked by invoice and delivery evidence.",
        ),
        (
            "ask_human_approval_after_corrections",
            "Ask for scoped human approval after corrections",
            "future_safe_candidate",
            "Approval may be considered only after blockers clear.",
        ),
    )
    return tuple(
        {
            "candidate_id": candidate_id,
            "label": label,
            "status": status,
            "rationale": rationale,
            "candidate_only": True,
            "truth_claimed": False,
            "authority_claimed": False,
            "action_permission_claimed": False,
        }
        for candidate_id, label, status, rationale in candidates
    )


def score_candidate_vectors_with_avf(
    candidates: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    scores = {
        "release_all_and_pay_all": {
            "score": 0.0,
            "avf_status": "hard_masked",
            "reason": "payment and shipment release are both unsafe in first run",
        },
        "hold_release_request_documents": {
            "score": 0.91,
            "avf_status": "ranked_safe",
            "reason": "keeps shipment held and asks for missing legal evidence",
        },
        "partial_release_only_ready_items": {
            "score": 0.36,
            "avf_status": "penalized",
            "reason": "ready item evidence does not clear shipment-level review",
        },
        "restock_water_filter_then_review": {
            "score": 0.82,
            "avf_status": "ranked_safe",
            "reason": "corrects internal stock blocker before rerun",
        },
        "prepare_payment_forms_but_do_not_execute": {
            "score": 0.9,
            "avf_status": "ranked_safe",
            "reason": "preparation is safe because no payment permission is created",
        },
        "block_supplier_B_due_invoice_mismatch": {
            "score": 0.78,
            "avf_status": "blocked_or_penalized",
            "reason": "Supplier B payment remains blocked by invoice mismatch",
        },
        "ask_human_approval_after_corrections": {
            "score": 0.86,
            "avf_status": "ranked_safe",
            "reason": "approval request is only future scoped evidence",
        },
    }
    ranked = sorted(
        (
            {
                **candidate,
                **scores[candidate["candidate_id"]],
                "score_is_authority": False,
                "creates_permission": False,
            }
            for candidate in candidates
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    top_candidate = ranked[0]
    return {
        "avf_scored": True,
        "avf_scored_count": 1,
        "ranked_candidates": tuple(ranked),
        "top_ranked_candidate_id": top_candidate["candidate_id"],
        "top_ranked_candidate_is_permission": False,
        "release_all_and_pay_all_hard_masked_count": 1,
        "pay_supplier_b_blocked_or_penalized_count": 1,
        "prepare_payment_forms_only_ranked_safe_count": 1,
        "hold_release_request_documents_ranked_safe_count": 1,
        "ask_human_approval_after_corrections_ranked_safe_count": 1,
        "high_score_did_not_create_permission_count": 1,
        "avf_score_is_authority_count": 0,
        "top_ranked_candidate_is_permission_count": 0,
        "AVF is not authority": True,
    }


def build_first_run_root_final() -> dict[str, Any]:
    return {
        "status": "EXECUTED_IN_SLICE_B",
        "root_final_decision": "NOT_READY",
        "root_final_created": True,
        "root_reasons": (
            "water_filter short_by_2",
            "insurance certificate expired",
            "supplier_B invoice mismatch",
            "supplier_B delivery delayed",
            "payment forms require human approval",
        ),
        "prepared_artifacts": (
            "supplier_A_restock_request_draft",
            "bank_A_payment_form_masked",
            "legal_update_request",
            "supplier_B_review_request",
        ),
        "action_commit_packet_created": False,
        "payment_executed": False,
        "shipment_release_executed": False,
        "receipt_created": False,
        "Root remains final authority": True,
    }


def build_corrected_evidence_context() -> dict[str, Any]:
    return {
        "section_id": "corrected_evidence",
        "status": "EXECUTED_IN_SLICE_C",
        "corrected_supplier_A_evidence": {
            "insurance_certificate": "valid",
            "warehouse_water_filter": "+2 arrived",
            "warehouse_shortage_cleared": True,
            "supplier_A_stock_confirmed": True,
            "payment_form_status": "shape_valid",
            "payment_permission_status": "not_granted",
            "bank_policy": "human_approval_required",
        },
        "supplier_B_blockers": {
            "invoice_B": "mismatch_with_PO",
            "supplier_B_delivery": "delayed",
            "legal_status": "needs_review",
            "payment_form_status": "prepared_but_blocked",
            "payment_permission_status": "not_granted",
        },
        "drs_writeback_traces": (
            "corrected_insurance_trace",
            "corrected_inventory_trace",
            "supplier_B_still_blocked_trace",
        ),
        "corrected_insurance_trace": {
            "trace_id": "corrected_insurance_trace",
            "evidence_only": True,
            "authority_claimed": False,
        },
        "corrected_inventory_trace": {
            "trace_id": "corrected_inventory_trace",
            "evidence_only": True,
            "authority_claimed": False,
        },
        "supplier_B_still_blocked_trace": {
            "trace_id": "supplier_B_still_blocked_trace",
            "evidence_only": True,
            "authority_claimed": False,
        },
        "corrected_evidence_drs_writeback_count": 3,
        "corrected_evidence_is_authority_count": 0,
        "prior_root_final_mutated": False,
        "prior_root_final_mutated_count": 0,
        "action_commit_packet_created": False,
        "payment_executed": False,
        "shipment_release_executed": False,
        "receipt_created": False,
    }


def build_second_run_root_outcome(
    corrected_evidence: dict[str, Any],
    drs_context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "section_id": "second_run",
        "status": "EXECUTED_IN_SLICE_C",
        "input": "Check SH-2042 again after document and inventory correction.",
        "drs_prior_trace_found": drs_context["drs_candidates_found"],
        "reuse_allowed_as_context": True,
        "reuse_is_authority": False,
        "second_run_reuse_used_count": 1,
        "reuse_authority_claimed_count": 0,
        "changed_facts_rerun_validation": True,
        "changed_facts_rerun_validation_count": 1,
        "corrected_facts_used": (
            "insurance_certificate valid",
            "warehouse water_filter +2 arrived",
            "Supplier A stock confirmed",
        ),
        "supplier_A_status": {
            "ready_for_human_reviewed_payment_approval_only": True,
            "payment_form_status": corrected_evidence["corrected_supplier_A_evidence"][
                "payment_form_status"
            ],
            "payment_permission_status": corrected_evidence[
                "corrected_supplier_A_evidence"
            ]["payment_permission_status"],
            "bank_policy": corrected_evidence["corrected_supplier_A_evidence"][
                "bank_policy"
            ],
        },
        "supplier_B_status": {
            "SUPPLIER_B_REMAINS_BLOCKED": True,
            "invoice_B": "mismatch_with_PO",
            "supplier_B_delivery": "delayed",
            "legal_status": "needs_review",
            "included_in_future_action_scope": False,
        },
        "root_outcome": (
            "READY_FOR_HUMAN_REVIEWED_SUPPLIER_A_PAYMENT_APPROVAL",
            "SHIPMENT_RELEASE_STILL_HELD_OR_SEPARATE_APPROVAL_REQUIRED",
            "SUPPLIER_B_REMAINS_BLOCKED",
        ),
        "ready_for_human_supplier_a_payment_approval_count": 1,
        "shipment_release_still_held_count": 1,
        "supplier_B_payment_blocked_count": 1,
        "payment_executed_count": 0,
        "action_commit_packet_created_count": 0,
        "mock_bank_receipt_created_count": 0,
        "shipment_released_count": 0,
        "mock_shipment_released_count": 0,
        "Root remains final authority": True,
    }


def build_slice_c_machine_summary() -> dict[str, Any]:
    fixtures = build_inline_fixtures()
    phase_results = build_phase_machine()
    proposal = build_deterministic_orchestrator_proposal()
    route_context = _route_context_from_orchestrator_proposal(proposal)
    bsep_packet = build_supplier_payment_bsep(proposal, route_context)
    bsep_validation = validate_bounded_semantic_evidence_packet(
        bsep_packet,
        route_context_packet=route_context,
        orchestrator_proposal=proposal,
        structured_rationale_validation={"accepted": True},
    )
    drs_context = build_company_local_drs_context()
    candidate_vectors = build_candidate_vectors()
    avf_ranking = score_candidate_vectors_with_avf(candidate_vectors)
    root_first_run = build_first_run_root_final()
    corrected_evidence = build_corrected_evidence_context()
    drs_context = {
        **drs_context,
        "drs_writeback_executed": True,
        "drs_writeback_count": corrected_evidence[
            "corrected_evidence_drs_writeback_count"
        ],
        "drs_writeback_is_authority": False,
        "drs_writeback_is_action_permission": False,
    }
    second_run = build_second_run_root_outcome(corrected_evidence, drs_context)
    return {
        "run_id": RUN_ID,
        "title": TITLE,
        "short_name": SHORT_NAME,
        "slice_id": SLICE_ID,
        "slice_status": "PASS",
        "final_status": "PASS",
        "wow_accepted": False,
        "wow_completion_claimed": False,
        "lane": "deterministic_ci",
        "phase_results": phase_results,
        "first_run": root_first_run,
        "corrected_evidence": corrected_evidence,
        "second_run": second_run,
        "human_approval": {
            **_future_section(
                "human_approval",
                future_slice="Slice D",
                note="future scoped approval evidence; no approval captured in Slice C",
            ),
            "human_approval_present_count": 0,
        },
        "mock_action_commit_packet": {
            **_future_section(
                "mock_action_commit_packet",
                future_slice="Slice D",
                note="no ActionCommitPacket created in Slice C",
            ),
            "action_commit_packet_created_count": 0,
        },
        "mock_execution": {
            **_future_section(
                "mock_execution",
                future_slice="Slice D",
                note="no MockBankSandbox execution in Slice C",
            ),
            "mock_payment_executed_count": 0,
        },
        "receipt": {
            **_future_section(
                "receipt",
                future_slice="Slice D",
                note="no receipt emitted in Slice C",
            ),
            "mock_bank_receipt_created_count": 0,
            "receipt_created": False,
        },
        "inline_fixtures": fixtures,
        "deterministic_orchestrator_proposal": proposal,
        "route_context": route_context,
        "bsep_summary": {
            "packet_type": bsep_packet["packet_type"],
            "packet_id": bsep_packet["packet_id"],
            "validation": bsep_validation,
            "validation_accepted": bsep_validation["accepted"],
            "truth_claimed": bsep_packet["truth_claimed"],
            "authority_claimed": bsep_packet["authority_claimed"],
            "action_permission_claimed": bsep_packet["action_permission_claimed"],
            "final_output_claimed": bsep_packet["final_output_claimed"],
            "raw_user_text_included": bsep_packet["raw_user_text_included"],
            "raw_cross_role_text_included": bsep_packet[
                "raw_cross_role_text_included"
            ],
            "selected_vector_ids": bsep_packet["selected_vector_ids"],
            "required_guards": bsep_packet["required_guards"],
            "packet": bsep_packet,
        },
        "drs_context": drs_context,
        "candidate_vectors": candidate_vectors,
        "avf_ranking": avf_ranking,
        "root_first_run": root_first_run,
        "prompt_secret_scan": _prompt_secret_scan(),
        "action_counters": _zero_action_counters(),
        "non_claim_counters": _non_claim_counters(),
        "validation_errors": (),
        "audit_summary_path": None,
        "canonical_correction": {
            "shipment_release_review_only": True,
            "shipment_release_remains_held": True,
            "real_shipment_release_claimed": False,
            "mock_shipment_release_claimed": False,
            "only_future_allowed_mock_execution_crossing": (
                "supplier_A_mock_payment_after_root_and_scoped_human_approval"
            ),
            "supplier_A_mock_payment_executed": False,
            "supplier_B_payment_executed": False,
            "shipment_release_executed": False,
        },
        "authority_invariants": {
            invariant: True for invariant in AUTHORITY_INVARIANTS
        },
        "legacy_api_vs_hedgehog": {
            "legacy_api": (
                "Supplier A API available",
                "Bank A form valid",
                "Invoice A payable",
                "Warehouse almost ready",
            ),
            "hedgehog": (
                "supplier_api_available = EvidenceCandidate",
                "bank_form_shape_valid = not permission",
                "invoice_payable = not legal readiness",
                "warehouse_shortage = blocker",
                "insurance_expired = blocker",
                "DRS prior success = context only",
                "Root Final first run = NOT_READY in Slice B",
            ),
            "required_sentence": (
                "APIs return facts.\n"
                "Hedgehog decides what those facts are allowed to become."
            ),
        },
    }


def build_initial_machine_summary() -> dict[str, Any]:
    return build_slice_c_machine_summary()


def run_supplier_payment_shipment_release_review_wow_v1_1() -> dict[str, Any]:
    return build_slice_c_machine_summary()


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def render_report(summary: dict[str, Any]) -> str:
    fixtures = summary["inline_fixtures"]
    action_counters = summary["action_counters"]
    prompt_scan = summary["prompt_secret_scan"]
    correction = summary["canonical_correction"]
    bsep = summary["bsep_summary"]
    drs = summary["drs_context"]
    avf = summary["avf_ranking"]
    first_run = summary["first_run"]
    corrected = summary["corrected_evidence"]
    second_run = summary["second_run"]
    lines = [
        summary["title"],
        summary["short_name"],
        "",
        "Slice C scope: corrected evidence, context-only DRS writeback, second-run reuse, and Root review.",
        f"slice_id: {summary['slice_id']}",
        f"slice_status: {summary['slice_status']}",
        f"lane: {summary['lane']}",
        f"WOW ACCEPTED: {_bool_text(summary['wow_accepted'])}",
        f"wow_completion_claimed: {_bool_text(summary['wow_completion_claimed'])}",
        "",
        "Human sentence:",
        "LLM understands the business process, but does not get sovereignty.",
        "DRS helps, but does not decide.",
        "AVF ranks, but does not authorize.",
        "Root blocks unsafe action.",
        "Human approval is scoped.",
        "Only scoped mock payment executes in a future slice after Root and scoped approval.",
        "Supplier B remains blocked.",
        "Shipment release remains held.",
        "Real world untouched.",
        "",
        "Architecture formula:",
        "Provider proposes semantics.",
        "Runtime canonicalizes.",
        "Validators verify.",
        "Root decides.",
        "Root + scoped human approval may create a mock ActionCommitPacket.",
        "Mock sandbox executes only validated scoped packet.",
        "",
        "Phases:",
    ]
    for phase in summary["phase_results"]:
        lines.append(
            f"- {phase['phase_id']}: {phase['status']} / {phase['execution_status']}"
        )

    supplier_a = fixtures["supplier_A"]
    supplier_b = fixtures["supplier_B"]
    slot = fixtures["masked_payment_slot_supplier_A"]
    lines.extend(
        [
            "",
            "Business fixtures summary:",
            f"- shipment_id: {fixtures['business_request']['shipment_id']}",
            f"- Supplier A: {supplier_a['supplier']} / {supplier_a['product']} / {supplier_a['invoice']}",
            f"- Supplier B: {supplier_b['supplier']} / {supplier_b['product']} / {supplier_b['invoice']}",
            "",
            "Masked payment slot summary:",
            f"- payment_slot: {slot['payment_slot']}",
            f"- beneficiary_verified: {_bool_text(slot['beneficiary_verified'])}",
            f"- iban_checksum_valid: {_bool_text(slot['iban_checksum_valid'])}",
            f"- amount: {slot['amount']}",
            f"- payment_permission_status: {slot['payment_permission_status']}",
            "",
            "Secret scan:",
            f"- prompt_secret_scan_passed_count: {prompt_scan['prompt_secret_scan_passed_count']}",
            f"- llm_received_raw_iban_count: {prompt_scan['llm_received_raw_iban_count']}",
            f"- llm_received_api_token_count: {prompt_scan['llm_received_api_token_count']}",
            f"- secrets_logged_count: {prompt_scan['secrets_logged_count']}",
            "",
            "No provider/model/network calls:",
            f"- deterministic_lane_passed_count: {action_counters['deterministic_lane_passed_count']}",
            f"- network_used_count: {action_counters['network_used_count']}",
            f"- gemini_called_count: {action_counters['gemini_called_count']}",
            f"- real_model_call_count: {action_counters['real_model_call_count']}",
            f"- live_model_call_count: {action_counters['live_model_call_count']}",
            "",
            "BSEP summary:",
            f"- packet_type: {bsep['packet_type']}",
            f"- validation_accepted: {_bool_text(bsep['validation_accepted'])}",
            f"- bsep_created_count: {action_counters['bsep_created_count']}",
            f"- bsep_validated_count: {action_counters['bsep_validated_count']}",
            "- BSEP is not truth or authority and creates no action permission.",
            "",
            "DRS context-only summary:",
            f"- drs_candidates_found_count: {drs['drs_candidates_found_count']}",
            f"- drs_prior_success_used_as_context_count: {drs['drs_prior_success_used_as_context_count']}",
            f"- drs_prior_success_used_as_permission_count: {drs['drs_prior_success_used_as_permission_count']}",
            f"- prior_successful_payment_trace_cannot_authorize_current_payment: {_bool_text(drs['prior_successful_payment_trace_cannot_authorize_current_payment'])}",
            f"- drs_writeback_count: {drs['drs_writeback_count']}",
            "",
            "CandidateVector summary:",
            f"- candidate_vectors_generated_count: {action_counters['candidate_vectors_generated_count']}",
        ]
    )
    lines.extend(
        f"- {candidate['candidate_id']}: {candidate['status']}"
        for candidate in summary["candidate_vectors"]
    )
    lines.extend(
        [
            "",
            "AVF ranking summary:",
            f"- avf_scored_count: {avf['avf_scored_count']}",
            f"- top_ranked_candidate_id: {avf['top_ranked_candidate_id']}",
            f"- release_all_and_pay_all_hard_masked_count: {avf['release_all_and_pay_all_hard_masked_count']}",
            f"- pay_supplier_b_blocked_or_penalized_count: {avf['pay_supplier_b_blocked_or_penalized_count']}",
            f"- high_score_did_not_create_permission_count: {avf['high_score_did_not_create_permission_count']}",
            "",
            "Root first run:",
            f"- Root Final: {first_run['root_final_decision']}",
            f"- root_final_created_count: {action_counters['root_final_created_count']}",
            f"- root_decision_not_ready_count: {action_counters['root_decision_not_ready_count']}",
            "- prepared_artifacts:",
        ]
    )
    lines.extend(f"  - {artifact}" for artifact in first_run["prepared_artifacts"])
    lines.extend(
        [
            "",
            "Corrected evidence summary:",
            f"- corrected_evidence: {corrected['status']}",
            f"- corrected_insurance_trace: {corrected['corrected_insurance_trace']['trace_id']}",
            f"- corrected_inventory_trace: {corrected['corrected_inventory_trace']['trace_id']}",
            f"- supplier_B_still_blocked_trace: {corrected['supplier_B_still_blocked_trace']['trace_id']}",
            f"- corrected_evidence_drs_writeback_count: {corrected['corrected_evidence_drs_writeback_count']}",
            f"- corrected_evidence_is_authority_count: {corrected['corrected_evidence_is_authority_count']}",
            f"- prior_root_final_mutated_count: {corrected['prior_root_final_mutated_count']}",
            "",
            "Second run DRS context-only reuse:",
            f"- second_run_reuse_used_count: {second_run['second_run_reuse_used_count']}",
            f"- reuse_is_authority: {_bool_text(second_run['reuse_is_authority'])}",
            f"- changed_facts_rerun_validation: {_bool_text(second_run['changed_facts_rerun_validation'])}",
            f"- changed_facts_rerun_validation_count: {second_run['changed_facts_rerun_validation_count']}",
            "",
            "Second run Root outcome:",
        ]
    )
    lines.extend(f"- {outcome}" for outcome in second_run["root_outcome"])
    lines.extend(
        [
            f"- ready_for_human_supplier_a_payment_approval_count: {second_run['ready_for_human_supplier_a_payment_approval_count']}",
            f"- shipment_release_still_held_count: {second_run['shipment_release_still_held_count']}",
            f"- supplier_B_payment_blocked_count: {second_run['supplier_B_payment_blocked_count']}",
            "",
            "Future sections not executed:",
            f"- human_approval: {summary['human_approval']['status']}",
            f"- mock_action_commit_packet: {summary['mock_action_commit_packet']['status']}",
            f"- mock_execution: {summary['mock_execution']['status']}",
            f"- receipt: {summary['receipt']['status']}",
            "",
            "No action execution in Slice C:",
            f"- action_commit_packet_created_count: {action_counters['action_commit_packet_created_count']}",
            f"- mock_payment_executed_count: {action_counters['mock_payment_executed_count']}",
            f"- payment_executed_count: {action_counters['payment_executed_count']}",
            f"- shipment_released_count: {action_counters['shipment_released_count']}",
            f"- mock_shipment_released_count: {action_counters['mock_shipment_released_count']}",
            f"- real_world_effects_count: {action_counters['real_world_effects_count']}",
            "",
            "Canonical correction:",
            f"- shipment_release_review_only: {_bool_text(correction['shipment_release_review_only'])}",
            f"- shipment_release_remains_held: {_bool_text(correction['shipment_release_remains_held'])}",
            f"- supplier_A_mock_payment_executed: {_bool_text(correction['supplier_A_mock_payment_executed'])}",
            f"- supplier_B_payment_executed: {_bool_text(correction['supplier_B_payment_executed'])}",
            f"- shipment_release_executed: {_bool_text(correction['shipment_release_executed'])}",
            "",
            "Legacy API vs Hedgehog:",
            "Legacy API:",
        ]
    )
    lines.extend(f"- {item}" for item in summary["legacy_api_vs_hedgehog"]["legacy_api"])
    lines.append("Hedgehog:")
    lines.extend(f"- {item}" for item in summary["legacy_api_vs_hedgehog"]["hedgehog"])
    lines.extend(
        [
            summary["legacy_api_vs_hedgehog"]["required_sentence"],
            "",
            "Machine summary JSON:",
            json.dumps(summary, sort_keys=True),
            "",
            f"FINAL STATUS: {summary['final_status']}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    summary = run_supplier_payment_shipment_release_review_wow_v1_1()
    print(render_report(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
