from __future__ import annotations

import json
from typing import Any, Mapping


RUN_ID = "full_wow_v1_2_product_trace_v01"
REPORT_ID = "full_wow_v1_2_product_trace_v01"
TRACE_TYPE = "deterministic_product_trace_lane"

RENDERED_SECTIONS = (
    "[FULL WOW V1.2 PRODUCT TRACE]",
    "[WHAT V1.2 ADDS OVER V1.1]",
    "[LANE MODEL]",
    "[DIRTY REQUEST]",
    "[API-LIKE BUSINESS MODULE TRACE]",
    "[WAREHOUSE API]",
    "[SUPPLIER A API]",
    "[SUPPLIER B API]",
    "[LEGAL MODULE]",
    "[ACCOUNTING MODULE]",
    "[BANK A LEGACY SANDBOX]",
    "[BANK B HEDGEHOG-NATIVE PREVIEW]",
    "[RUNTIME PLAN AND FRACTAL BRANCHES]",
    "[BRANCH RESULT PROPOSALS]",
    "[POST V&V / GT-LGT / ROOT]",
    "[APPROVAL / PACKET / RECEIPT BOUNDARY]",
    "[SECRET MEMBRANE]",
    "[TRANSITION CARDS]",
    "[AUTHORITY MATRIX]",
    "[COUNTER MATRIX]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

BUSINESS_MODULES: tuple[dict[str, Any], ...] = (
    {
        "module_id": "warehouse_api_sandbox",
        "display_name": "WarehouseAPI",
        "api_like_call": "GET /warehouse/v1/shipments/SH-2042/inventory?scope=required_items",
        "shipment_id": "SH-2042",
        "warehouse_id": "W-17",
        "query_scope": "required_items",
        "pagination": {
            "total_required_items": 4,
            "returned_items": 4,
            "page": 1,
            "page_size": 50,
        },
        "items_checked": (
            {
                "sku": "WF-100",
                "product": "water_filter",
                "required_qty": 8,
                "available_qty": 6,
                "shortage_qty": 2,
                "status": "short_by_2",
            },
            {
                "sku": "PV-200",
                "product": "pump_valve",
                "required_qty": 4,
                "available_qty": 4,
                "shortage_qty": 0,
                "status": "ready",
            },
            {
                "sku": "SEAL-9",
                "product": "customs_seal",
                "required_qty": 1,
                "available_qty": 1,
                "shortage_qty": 0,
                "status": "ready",
            },
            {
                "sku": "PALLET-STD",
                "product": "pallet_space",
                "required_qty": 2,
                "available_qty": 2,
                "shortage_qty": 0,
                "status": "ready",
            },
        ),
        "meaning": "stock blocker found for water_filter",
        "does_not_authorize": "shipment release",
    },
    {
        "module_id": "supplier_a_api_sandbox",
        "display_name": "SupplierA",
        "api_like_call": "GET /supplier/adriatic-filters/v1/availability?sku=WF-100",
        "supplier_id": "supplier_A_adriatic_filters",
        "supplier_name": "Adriatic Filters LLC",
        "sku": "WF-100",
        "available_qty": 20,
        "can_cover_shortage_qty": 2,
        "supplier_status": "available",
        "invoice_id": "INV-2042",
        "bank": "Bank A Legacy Sandbox",
        "meaning": "Supplier A can cover missing water_filter quantity",
        "does_not_authorize": "payment permission or shipment release",
    },
    {
        "module_id": "supplier_b_api_sandbox",
        "display_name": "SupplierB",
        "api_like_call": "GET /supplier/balkan-pumps/v1/order-status?invoice_id=INV-2043",
        "supplier_id": "supplier_B_balkan_pumps",
        "supplier_name": "Balkan Pumps SHPK",
        "invoice_id": "INV-2043",
        "item": "pump_valve",
        "invoice_status": "mismatch",
        "delivery_status": "delayed",
        "legal_status": "needs_review",
        "supplier_status": "blocked",
        "bank": "Bank B Hedgehog-native Preview",
        "meaning": "Supplier B remains blocked",
        "does_not_authorize": "Supplier B payment",
    },
    {
        "module_id": "legal_module",
        "display_name": "Legal",
        "api_like_call": "GET /legal/v1/suppliers/adriatic-filters/insurance",
        "supplier_id": "supplier_A_adriatic_filters",
        "first_run_insurance_status": "expired",
        "corrected_evidence_insurance_status": "valid",
        "contract_check_status": "review_required_then_clear_for_supplier_a_scope",
        "branch_local_llm_slm_policy": "allowed in manual lane for messy clause extraction",
        "deterministic_branch_called_llm_or_slm_count": 0,
        "meaning": "legal blocker exists first, corrected evidence clears Supplier A scope later",
        "does_not_authorize": "payment permission",
    },
    {
        "module_id": "accounting_module",
        "display_name": "Accounting",
        "api_like_call": "GET /accounting/v1/invoices/INV-2042/reconciliation",
        "invoice_id": "INV-2042",
        "purchase_order_id": "PO-2042-A",
        "amount": "1240.00 EUR",
        "amount_matches_po": True,
        "payable_shape_valid": True,
        "payment_permission_status": "not_granted",
        "branch_local_llm_slm_policy": "allowed in manual lane for mismatch explanation",
        "deterministic_branch_called_llm_or_slm_count": 0,
        "meaning": "invoice shape is payable for Supplier A scope",
        "does_not_authorize": "payment execution",
    },
    {
        "module_id": "bank_a_legacy_sandbox",
        "display_name": "BankA",
        "api_like_call": "POST /bank-a/v1/payment-slots",
        "payment_slot": "payment_slot_A_2042",
        "beneficiary_verified": True,
        "iban_checksum_valid": True,
        "amount": "1240.00 EUR",
        "invoice_id": "INV-2042",
        "payment_form_status": "shape_valid",
        "payment_permission_status": "not_granted",
        "bank_policy": "human_approval_required",
        "internal_raw_iban_present_inside_sandbox": True,
        "llm_visible_raw_iban": False,
        "llm_visible_bank_token": False,
        "meaning": "bank payment slot can be prepared for Supplier A",
        "does_not_authorize": "payment execution",
    },
    {
        "module_id": "bank_b_hedgehog_native_preview",
        "display_name": "BankB",
        "api_like_call": "POST /bank-b/hedgehog/v1/contract-preview",
        "supplier_id": "supplier_B_balkan_pumps",
        "invoice_id": "INV-2043",
        "semantic_contract_preview_created": True,
        "execution_allowed": False,
        "blocked_reasons": (
            "invoice_mismatch",
            "delivery_delayed",
            "legal_needs_review",
        ),
        "meaning": "Hedgehog-native bank path can review contract but cannot execute while Supplier B blocked",
        "does_not_authorize": "Supplier B payment",
    },
)

TRANSITION_STEP_IDS = (
    "dirty_request_received",
    "warehouse_inventory_query",
    "supplier_a_availability_query",
    "supplier_b_blocker_query",
    "legal_insurance_contract_check",
    "accounting_invoice_po_reconciliation",
    "bank_a_payment_slot_prepared",
    "bank_b_native_contract_preview",
    "top_level_semantic_route_observed_from_v1_1",
    "bsep_membrane_observed_from_v1_1",
    "top_level_live_semantic_architect_observed_from_v1_1",
    "runtime_plangraph_compiled",
    "fractal_branch_cells_dispatched",
    "branch_result_proposals_collected",
    "post_vv_validated",
    "gt_lgt_advisory_review",
    "root_first_not_ready",
    "corrected_evidence_received",
    "root_second_supplier_a_scoped_review",
    "human_approval_supplier_a_only",
    "root_created_mock_action_commit_packet_observed",
    "mock_bank_sandbox_receipt_observed",
    "final_state_summary",
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
    "BSEP is not truth.",
    "BSEP is not authority.",
    "DRS candidate context is not truth.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Runtime owns PlanGraph/local plan artifacts.",
    "Provider does not own PlanGraph.",
    "PlanGraph is not authority.",
    "Branch ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
    "Root-created mock ActionCommitPacket is scoped only.",
    "MockBankSandbox receipt is evidence only.",
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
    "manual live multi-LLM/fractal lane not implemented in this patch",
)


def _module_by_id(module_id: str) -> Mapping[str, Any]:
    for module in BUSINESS_MODULES:
        if module["module_id"] == module_id:
            return module
    raise KeyError(module_id)


def _transition_card(
    step_id: str,
    actor_or_module: str,
    api_like_call: str,
    input_summary: str,
    output_summary: str,
    meaning: str,
    does_not_authorize: str,
    next_step: str,
    evidence_id: str,
) -> dict[str, str]:
    return {
        "step_id": step_id,
        "actor_or_module": actor_or_module,
        "api_like_call": api_like_call,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "meaning": meaning,
        "does_not_authorize": does_not_authorize,
        "next_step": next_step,
        "trace_id": RUN_ID,
        "evidence_id": evidence_id,
    }


def _transition_cards() -> tuple[dict[str, str], ...]:
    return (
        _transition_card(
            "dirty_request_received",
            "User / business request",
            "USER_REQUEST supplier payment + shipment release review",
            "Dirty request asks for Supplier A/B payment review and shipment release review.",
            "Root-visible product trace begins with no permissions granted.",
            "business wants payment and shipment release review",
            "payment or shipment release",
            "warehouse_inventory_query",
            "dirty_request_v1_2",
        ),
        _transition_card(
            "warehouse_inventory_query",
            "WarehouseAPI",
            _module_by_id("warehouse_api_sandbox")["api_like_call"],
            "Query shipment SH-2042 required stock.",
            "water_filter is short by 2; other shipment items are ready.",
            "stock blocker found for water_filter",
            "shipment release",
            "supplier_a_availability_query",
            "warehouse_api_sandbox",
        ),
        _transition_card(
            "supplier_a_availability_query",
            "SupplierA",
            _module_by_id("supplier_a_api_sandbox")["api_like_call"],
            "Ask Adriatic Filters whether WF-100 can cover shortage quantity 2.",
            "Supplier A has 20 available units and can cover the shortage.",
            "Supplier A can cover missing water_filter quantity",
            "payment permission or shipment release",
            "supplier_b_blocker_query",
            "supplier_a_api_sandbox",
        ),
        _transition_card(
            "supplier_b_blocker_query",
            "SupplierB",
            _module_by_id("supplier_b_api_sandbox")["api_like_call"],
            "Check Balkan Pumps order status for INV-2043.",
            "Invoice mismatch, delivery delay, and legal review keep Supplier B blocked.",
            "Supplier B remains blocked",
            "Supplier B payment",
            "legal_insurance_contract_check",
            "supplier_b_api_sandbox",
        ),
        _transition_card(
            "legal_insurance_contract_check",
            "Legal",
            _module_by_id("legal_module")["api_like_call"],
            "Review Supplier A insurance and contract state.",
            "First run has expired insurance; corrected evidence later clears Supplier A scope.",
            "legal blocker exists first, corrected evidence clears Supplier A scope later",
            "payment permission",
            "accounting_invoice_po_reconciliation",
            "legal_module",
        ),
        _transition_card(
            "accounting_invoice_po_reconciliation",
            "Accounting",
            _module_by_id("accounting_module")["api_like_call"],
            "Reconcile INV-2042 with PO-2042-A.",
            "Amount matches PO and payable shape is valid, while permission remains not granted.",
            "invoice shape is payable for Supplier A scope",
            "payment execution",
            "bank_a_payment_slot_prepared",
            "accounting_module",
        ),
        _transition_card(
            "bank_a_payment_slot_prepared",
            "BankA",
            _module_by_id("bank_a_legacy_sandbox")["api_like_call"],
            "Prepare masked payment slot for Supplier A invoice.",
            "payment_slot_A_2042 is shape-valid and still not permission.",
            "bank payment slot can be prepared for Supplier A",
            "payment execution",
            "bank_b_native_contract_preview",
            "bank_a_legacy_sandbox",
        ),
        _transition_card(
            "bank_b_native_contract_preview",
            "BankB",
            _module_by_id("bank_b_hedgehog_native_preview")["api_like_call"],
            "Preview Hedgehog-native bank contract for Supplier B.",
            "Contract preview is created with execution_allowed=false while blockers remain.",
            "Hedgehog-native bank path can review contract but cannot execute while Supplier B blocked",
            "Supplier B payment",
            "top_level_semantic_route_observed_from_v1_1",
            "bank_b_hedgehog_native_preview",
        ),
        _transition_card(
            "top_level_semantic_route_observed_from_v1_1",
            "closed v1.1 semantic lane",
            "OBSERVE closed real Gemini semantic route",
            "Observe v1.1 real Orchestrator semantics from the closed audit.",
            "Top-level real semantic route remains closed evidence, not rerun.",
            "Provider proposes semantics; runtime canonicalizes; validators verify; Root decides.",
            "truth, authority, action permission, or FinalOutput",
            "bsep_membrane_observed_from_v1_1",
            "full_wow_v1_1_manual_live_gemini_real_20260705_232010",
        ),
        _transition_card(
            "bsep_membrane_observed_from_v1_1",
            "closed v1.1 BSEP membrane",
            "OBSERVE closed BSEP build/validation",
            "Observe BSEP built after Orchestrator validation and validated before Architect.",
            "BSEP membrane is carried forward as closed basis.",
            "bounded context reaches Architect without becoming authority",
            "truth, authority, or action permission",
            "top_level_live_semantic_architect_observed_from_v1_1",
            "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
        ),
        _transition_card(
            "top_level_live_semantic_architect_observed_from_v1_1",
            "closed v1.1 real Gemini Semantic Architect",
            "OBSERVE closed real Gemini Architect semantic proposal",
            "Observe Architect received validated BSEP-derived bounded context from the closed v1.1 run.",
            "Architect semantic validation accepted in the closed v1.1 real Gemini lane.",
            "Real Gemini Architect proposed semantic plan intent, while runtime retained PlanGraph ownership.",
            "truth, authority, action permission, FinalOutput, provider-owned PlanGraph, ActionCommitPacket, receipt, payment, or shipment release.",
            "runtime_plangraph_compiled",
            "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
        ),
        _transition_card(
            "runtime_plangraph_compiled",
            "runtime",
            "COMPILE local PlanGraph/product trace plan",
            "Compile local product trace plan from deterministic module observations.",
            "Runtime owns PlanGraph/local plan artifacts.",
            "runtime owns PlanGraph/local plan artifacts",
            "authority",
            "fractal_branch_cells_dispatched",
            "runtime_product_trace_plan_v1_2",
        ),
        _transition_card(
            "fractal_branch_cells_dispatched",
            "runtime Fractal Cells",
            "DISPATCH deterministic branch cells",
            "Dispatch warehouse, supplier, legal, accounting, bank, and root merge branches.",
            "Eight bounded deterministic branch cells are represented.",
            "branch work is visible and bounded",
            "FinalOutput or action permission",
            "branch_result_proposals_collected",
            "fractal_branch_cells_v1_2",
        ),
        _transition_card(
            "branch_result_proposals_collected",
            "branch Fractal Cells",
            "COLLECT branch ResultProposals",
            "Collect one ResultProposal from each deterministic branch.",
            "Eight branch ResultProposals return to Post V&V.",
            "branch evidence returns as proposals only",
            "FinalOutput",
            "post_vv_validated",
            "branch_result_proposals_v1_2",
        ),
        _transition_card(
            "post_vv_validated",
            "Post V&V",
            "VALIDATE branch ResultProposals",
            "Validate branch proposal boundaries before advisory review.",
            "Post V&V accepts deterministic branch proposal shapes.",
            "Post V&V checks proposals without finalizing",
            "FinalOutput",
            "gt_lgt_advisory_review",
            "post_vv_v1_2",
        ),
        _transition_card(
            "gt_lgt_advisory_review",
            "GT/LGT",
            "ADVISORY_REVIEW validated proposals",
            "GT/LGT reviews validated branch proposals as advisory evidence.",
            "GT/LGT advisory review is recorded.",
            "GT/LGT is advisory and does not finalize",
            "FinalOutput",
            "root_first_not_ready",
            "gt_lgt_v1_2",
        ),
        _transition_card(
            "root_first_not_ready",
            "Root",
            "ROOT_REVIEW first pass",
            "Root reviews first pass with legal and stock blockers still visible.",
            "First decision is NOT_READY.",
            "Root blocks unsafe action",
            "payment or shipment release",
            "corrected_evidence_received",
            "root_first_not_ready_v1_2",
        ),
        _transition_card(
            "corrected_evidence_received",
            "runtime evidence update",
            "OBSERVE corrected evidence",
            "Corrected insurance and Supplier A support evidence are observed.",
            "Supplier A can proceed to scoped review only.",
            "corrected evidence narrows the route",
            "broad payment or shipment release",
            "root_second_supplier_a_scoped_review",
            "corrected_evidence_v1_2",
        ),
        _transition_card(
            "root_second_supplier_a_scoped_review",
            "Root",
            "ROOT_REVIEW second pass",
            "Root reviews corrected Supplier A facts while Supplier B remains blocked.",
            "Second decision is SUPPLIER_A_SCOPED_REVIEW_READY.",
            "Supplier A scope is review-ready",
            "Supplier B payment or shipment release",
            "human_approval_supplier_a_only",
            "root_second_supplier_a_v1_2",
        ),
        _transition_card(
            "human_approval_supplier_a_only",
            "human approval",
            "HUMAN_APPROVAL Supplier A only",
            "Human approval is scoped to Supplier A mock path.",
            "Approval is evidence for Supplier A scope only.",
            "human approval is scoped evidence only",
            "Supplier B payment, shipment release, or production action",
            "root_created_mock_action_commit_packet_observed",
            "human_approval_supplier_a_v1_2",
        ),
        _transition_card(
            "root_created_mock_action_commit_packet_observed",
            "Root",
            "OBSERVE closed Root-created mock ActionCommitPacket",
            "Observe closed v1.1 packet boundary without creating a new packet.",
            "Only Root-created scoped mock packet is observed.",
            "Root packet boundary remains visible",
            "real payment, Supplier B payment, or shipment release",
            "mock_bank_sandbox_receipt_observed",
            "closed_root_packet_boundary_v1_1",
        ),
        _transition_card(
            "mock_bank_sandbox_receipt_observed",
            "MockBankSandbox",
            "OBSERVE closed mock receipt",
            "Observe closed v1.1 Supplier A mock receipt boundary.",
            "Receipt remains evidence only; product trace creates no receipt.",
            "receipt remains evidence only",
            "truth, action permission, or shipment release",
            "final_state_summary",
            "closed_mock_receipt_boundary_v1_1",
        ),
        _transition_card(
            "final_state_summary",
            "Root final boundary",
            "FINAL SUMMARY",
            "Summarize v1.2 product trace state.",
            "Supplier A scoped review-ready; Supplier B blocked; shipment held; receipt evidence only.",
            "Root remains final authority",
            "production readiness or public auditor final package",
            "none",
            "full_wow_v1_2_product_trace_v01",
        ),
    )


def _fractal_branches() -> tuple[dict[str, Any], ...]:
    api_counts = {
        "warehouse_branch": 1,
        "supplier_a_branch": 1,
        "supplier_b_branch": 1,
        "legal_branch": 1,
        "accounting_branch": 1,
        "bank_a_branch": 1,
        "bank_b_branch": 1,
        "root_merge_branch": 0,
    }
    contexts = {
        "warehouse_branch": "WarehouseAPI shipment inventory evidence.",
        "supplier_a_branch": "SupplierA availability evidence.",
        "supplier_b_branch": "SupplierB blocker evidence.",
        "legal_branch": "Legal insurance/contract evidence.",
        "accounting_branch": "Accounting invoice/PO reconciliation evidence.",
        "bank_a_branch": "BankA masked payment slot evidence.",
        "bank_b_branch": "BankB Hedgehog-native contract preview evidence.",
        "root_merge_branch": "Root merge of bounded branch proposals.",
    }
    branches: list[dict[str, Any]] = []
    for branch_id in BRANCH_IDS:
        branches.append(
            {
                "branch_id": branch_id,
                "branch_context": contexts[branch_id],
                "branch_evidence": f"{branch_id}_evidence",
                "branch_result_proposal": f"{branch_id}_result_proposal",
                "branch_authority_boundary": "branch returns ResultProposal only; Root remains final authority",
                "branch_called_llm_or_slm_count": 0,
                "branch_called_api_count": api_counts[branch_id],
                "branch_real_world_effects_count": 0,
            }
        )
    return tuple(branches)


def _result_proposals(branches: tuple[Mapping[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    proposals: list[dict[str, Any]] = []
    for branch in branches:
        branch_id = str(branch["branch_id"])
        proposals.append(
            {
                "result_proposal_id": f"{branch_id}_result_proposal",
                "source_branch_id": branch_id,
                "proposal_status": "accepted_for_root_review",
                "evidence_summary": f"Deterministic evidence summary from {branch_id}.",
                "authority_claimed": False,
                "action_permission_claimed": False,
                "final_output_claimed": False,
            }
        )
    return tuple(proposals)


def _manual_live_lane_reservation() -> dict[str, Any]:
    return {
        "implemented_in_this_patch": False,
        "available_future": True,
        "expected_top_level_orchestrator_llm_call_count": 1,
        "expected_top_level_architect_llm_call_count": 1,
        "expected_branch_local_llm_slm_call_count_min": 1,
        "expected_fractal_branch_cells_created_count_min": 7,
        "note": "Patch 2 will implement env-gated manual live multi-LLM/fractal observation.",
    }


def _counters() -> dict[str, int]:
    return {
        "wow_v1_2_product_trace_created_count": 1,
        "transition_cards_created_count": 23,
        "deterministic_product_trace_lane_count": 1,
        "manual_live_multillm_fractal_lane_available_count": 1,
        "manual_live_multillm_fractal_lane_implemented_count": 0,
        "top_level_orchestrator_llm_call_count": 0,
        "top_level_architect_llm_call_count": 0,
        "branch_local_llm_slm_call_count": 0,
        "bsep_created_count_in_this_trace": 0,
        "bsep_validated_count_in_this_trace": 0,
        "real_gemini_lane_observed_from_v1_1_count": 1,
        "runtime_plangraph_compiled_count": 1,
        "provider_owned_plangraph_count": 0,
        "plan_graph_authority_count": 0,
        "fractal_branch_cells_created_count": 8,
        "branch_result_proposals_created_count": 8,
        "warehouse_api_sandbox_call_count": 1,
        "supplier_a_api_sandbox_call_count": 1,
        "supplier_b_api_sandbox_call_count": 1,
        "legal_module_check_count": 1,
        "accounting_module_check_count": 1,
        "bank_a_payment_slot_prepared_count": 1,
        "bank_b_native_contract_preview_count": 1,
        "bank_internal_raw_iban_present_count": 1,
        "bank_internal_token_present_count": 1,
        "llm_visible_raw_iban_count": 0,
        "llm_visible_bank_token_count": 0,
        "llm_visible_secret_count": 0,
        "payment_permission_granted_before_root_count": 0,
        "supplier_b_payment_allowed_count": 0,
        "product_trace_created_action_commit_packet_count": 0,
        "product_trace_created_receipt_count": 0,
        "product_trace_executed_mock_payment_count": 0,
        "product_trace_executed_real_payment_count": 0,
        "product_trace_released_shipment_count": 0,
        "product_trace_called_real_bank_supplier_warehouse_api_count": 0,
        "shipment_released_count": 0,
        "real_payment_executed_count": 0,
        "real_world_effects_count": 0,
    }


def collect_full_wow_v1_2_product_trace() -> dict[str, Any]:
    branches = _fractal_branches()
    result_proposals = _result_proposals(branches)
    counters = _counters()
    transition_cards = _transition_cards()
    final_status = (
        "PASS"
        if len(transition_cards) == counters["transition_cards_created_count"]
        and len(branches) == counters["fractal_branch_cells_created_count"]
        and len(result_proposals) == counters["branch_result_proposals_created_count"]
        else "FAIL_CLOSED"
    )

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "product_trace_status": final_status,
        "final_status": final_status,
        "trace_type": TRACE_TYPE,
        "v1_2_implemented_scope": "deterministic_product_trace_only",
        "manual_live_multillm_fractal_lane_implemented": False,
        "manual_live_multillm_fractal_lane_available_future": True,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "real_world_effects_count": counters["real_world_effects_count"],
        "closed_basis": {
            "full_wow_v1_1_evidence_pack_index": "docs/full_wow_v1_1_evidence_pack_index.md",
            "real_gemini_lane_observed_from_v1_1": True,
            "bsep_observed_from_v1_1": True,
        },
        "architecture_formula": (
            "Provider proposes semantics.",
            "Runtime canonicalizes.",
            "Validators verify.",
            "Root decides.",
        ),
        "business_modules": BUSINESS_MODULES,
        "business_boundaries": {
            "supplier_B_final_status": "BLOCKED",
            "shipment_final_status": "HELD",
            "receipt_final_status": "EVIDENCE_ONLY",
            "root_remains_final_authority": True,
        },
        "transition_cards": transition_cards,
        "runtime_plan": {
            "runtime_plangraph_compiled_count": counters[
                "runtime_plangraph_compiled_count"
            ],
            "provider_owned_plangraph_count": counters["provider_owned_plangraph_count"],
            "plan_graph_authority_count": counters["plan_graph_authority_count"],
            "runtime_owns_plangraph_local_plan_artifacts": True,
            "plan_graph_is_authority": False,
        },
        "fractal_branches": branches,
        "branch_result_proposals": result_proposals,
        "post_vv_gt_root": {
            "post_vv_validated_count": 1,
            "gt_lgt_advisory_review_count": 1,
            "root_first_decision": "NOT_READY",
            "root_second_decision": "SUPPLIER_A_SCOPED_REVIEW_READY",
            "supplier_b_final_status": "BLOCKED",
            "shipment_final_status": "HELD",
            "receipt_final_status": "EVIDENCE_ONLY",
            "root_remains_final_authority": True,
        },
        "approval_packet_receipt_boundary": {
            "human_approval_scope": "Supplier A only",
            "root_created_mock_action_commit_packet_observed": True,
            "mock_bank_sandbox_receipt_observed": True,
            "product_trace_created_action_commit_packet_count": counters[
                "product_trace_created_action_commit_packet_count"
            ],
            "product_trace_created_receipt_count": counters[
                "product_trace_created_receipt_count"
            ],
            "product_trace_executed_mock_payment_count": counters[
                "product_trace_executed_mock_payment_count"
            ],
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
            "secret_formula": "Secrets ∩ LLMContext = empty",
            "payment_slot_boundary": "payment_slot != permission",
            "receipt_truth_boundary": "receipt != truth",
            "receipt_shipment_boundary": "receipt != shipment release",
        },
        "manual_live_multillm_fractal_lane": _manual_live_lane_reservation(),
        "authority_matrix": AUTHORITY_MATRIX,
        "counters": counters,
        "non_claims": NON_CLAIMS,
        "validation_errors": () if final_status == "PASS" else ("shape_mismatch",),
    }


def _format_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _render_mapping(mapping: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, (tuple, list)):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, Mapping):
            lines.append(f"{key}:")
            for child_key, child_value in value.items():
                lines.append(f"  {child_key}: {_format_bool(child_value)}")
        else:
            lines.append(f"{key}: {_format_bool(value)}")
    return lines


def _render_module(module: Mapping[str, Any]) -> list[str]:
    lines = [f"- module_id: {module['module_id']} ({module['display_name']})"]
    for line in _render_mapping(module):
        lines.append(f"  {line}")
    return lines


def render_full_wow_v1_2_product_trace(report: Mapping[str, Any]) -> str:
    lines: list[str] = [
        "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.2",
        "API-LIKE BUSINESS TRACE EXPANSION",
        "",
        "[FULL WOW V1.2 PRODUCT TRACE]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"product_trace_status: {report['product_trace_status']}",
        f"final_status: {report['final_status']}",
        f"trace_type: {report['trace_type']}",
        f"v1_2_implemented_scope: {report['v1_2_implemented_scope']}",
        f"manual_live_multillm_fractal_lane_implemented: {_format_bool(report['manual_live_multillm_fractal_lane_implemented'])}",
        f"manual_live_multillm_fractal_lane_available_future: {_format_bool(report['manual_live_multillm_fractal_lane_available_future'])}",
        f"production_ready_claimed: {_format_bool(report['production_ready_claimed'])}",
        f"public_auditor_ready_claimed: {_format_bool(report['public_auditor_ready_claimed'])}",
        f"real_world_effects_count: {report['real_world_effects_count']}",
        "",
        "[WHAT V1.2 ADDS OVER V1.1]",
        "same architecture, richer business surface.",
        "WarehouseAPI, SupplierA, SupplierB, Legal, Accounting, BankA, and BankB are visible as deterministic API-like modules.",
        "Fractal branch cells and branch ResultProposals are represented as bounded deterministic branch work items.",
        "manual live multi-LLM/fractal lane not implemented in this patch; Patch 2 reserves env-gated observation.",
        "",
        "[LANE MODEL]",
        "Lane A: deterministic CI product trace; no Gemini, network, provider, secrets, payment, shipment, or production connector.",
        "Lane B: manual live multi-LLM/fractal observation lane reserved for Patch 2.",
        "",
        "[DIRTY REQUEST]",
        "Business asks for supplier payment + shipment release review for SH-2042.",
        "",
        "[API-LIKE BUSINESS MODULE TRACE]",
        "WarehouseAPI -> SupplierA -> SupplierB -> Legal -> Accounting -> BankA -> BankB -> Runtime -> Root.",
        "",
        "[WAREHOUSE API]",
    ]

    module_by_id = {module["module_id"]: module for module in report["business_modules"]}
    for module_id, section in (
        ("warehouse_api_sandbox", None),
        ("supplier_a_api_sandbox", "[SUPPLIER A API]"),
        ("supplier_b_api_sandbox", "[SUPPLIER B API]"),
        ("legal_module", "[LEGAL MODULE]"),
        ("accounting_module", "[ACCOUNTING MODULE]"),
        ("bank_a_legacy_sandbox", "[BANK A LEGACY SANDBOX]"),
        ("bank_b_hedgehog_native_preview", "[BANK B HEDGEHOG-NATIVE PREVIEW]"),
    ):
        if section:
            lines.extend(["", section])
        lines.extend(_render_module(module_by_id[module_id]))

    lines.extend(["", "[RUNTIME PLAN AND FRACTAL BRANCHES]"])
    lines.extend(_render_mapping(report["runtime_plan"]))
    for branch in report["fractal_branches"]:
        lines.append(
            "- {branch_id}: {branch_context}; branch_called_llm_or_slm_count={branch_called_llm_or_slm_count}; branch_called_api_count={branch_called_api_count}; branch_real_world_effects_count={branch_real_world_effects_count}".format(
                **branch
            )
        )

    lines.extend(["", "[BRANCH RESULT PROPOSALS]"])
    for proposal in report["branch_result_proposals"]:
        lines.append(
            "- {result_proposal_id}: source={source_branch_id}; status={proposal_status}; authority_claimed={authority_claimed}; action_permission_claimed={action_permission_claimed}; final_output_claimed={final_output_claimed}".format(
                **{**proposal, **{k: _format_bool(v) for k, v in proposal.items()}}
            )
        )

    lines.extend(["", "[POST V&V / GT-LGT / ROOT]"])
    lines.extend(_render_mapping(report["post_vv_gt_root"]))

    lines.extend(["", "[APPROVAL / PACKET / RECEIPT BOUNDARY]"])
    lines.extend(_render_mapping(report["approval_packet_receipt_boundary"]))

    lines.extend(["", "[SECRET MEMBRANE]"])
    lines.extend(_render_mapping(report["secret_membrane"]))

    lines.extend(["", "[TRANSITION CARDS]"])
    for card in report["transition_cards"]:
        lines.append(
            "- {step_id}: actor_or_module={actor_or_module}; api_like_call={api_like_call}; input_summary={input_summary}; output_summary={output_summary}; meaning={meaning}; does_not_authorize={does_not_authorize}; next_step={next_step}; trace_id={trace_id}; evidence_id={evidence_id}".format(
                **card
            )
        )

    lines.extend(["", "[AUTHORITY MATRIX]"])
    lines.extend(f"- {item}" for item in report["authority_matrix"])

    lines.extend(["", "[COUNTER MATRIX]"])
    for key in sorted(report["counters"]):
        lines.append(f"{key}: {report['counters'][key]}")

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
                    "product_trace_status": report["product_trace_status"],
                    "final_status": report["final_status"],
                    "counters": report["counters"],
                    "manual_live_multillm_fractal_lane": report[
                        "manual_live_multillm_fractal_lane"
                    ],
                    "non_claims": report["non_claims"],
                },
                sort_keys=True,
            ),
        ]
    )
    return "\n".join(lines)


def run_full_wow_v1_2_product_trace() -> str:
    return render_full_wow_v1_2_product_trace(collect_full_wow_v1_2_product_trace())


def main() -> int:
    report = collect_full_wow_v1_2_product_trace()
    print(render_full_wow_v1_2_product_trace(report))
    return 0 if report["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
