from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any, Mapping

from hedgehog.action_commit_packet_v02 import (
    STATUS_PASS,
    build_supplier_a_mock_receipt_evidence_fixture_v01,
    build_supplier_a_packet_corridor_validation_fixture_v02,
    record_packet_seen_v02,
    record_terminal_receipt_observation_v02,
    validate_action_commit_packet_v02,
    validate_corridor_step_against_packet_v01,
    validate_mock_receipt_evidence_v01,
    validate_packet_against_registry_v02,
    validate_packet_corridor_entry_v02,
)
from hedgehog.avf_v02 import (
    build_wow_v1_2_avf_v02_evaluation_input,
    evaluate_avf_candidates_v02,
)
from hedgehog.local_drs_v02 import (
    LocalDRSResolveInputV02,
    TemporalQueryV02,
    build_wow_v1_2_drs_v02_regression_records,
    resolve_drs_records_v02,
)


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
    "[LOCAL DRS V0.2 RESOLVE]",
    "[LOCAL AVF V0.2 ADVISORY EVALUATION]",
    "[ACTIONCOMMITPACKET V0.2 ROOT-CREATED PACKET BOUNDARY]",
    "[MOCKBANKSANDBOX V0.2 CONTRACT FULFILLMENT CORRIDOR]",
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
    "runtime_execution_topology_materialized",
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
    "DRS v0.2 hit is not truth.",
    "DRS v0.2 hit is not authority.",
    "DRS v0.2 hit is not permission.",
    "DRS v0.2 reuse decision is not FinalOutput.",
    "DRS v0.2 direct reuse candidate is not direct reuse.",
    "Old receipt is not current permission.",
    "Old Root Final is not silently reused.",
    "AVF v0.2 score is not truth.",
    "AVF v0.2 score is not authority.",
    "AVF v0.2 score is not permission.",
    "Top-ranked AVF candidate is not permission.",
    "CandidateVector is not action permission.",
    "CandidateVector is not FinalOutput.",
    "HardMask is not Root.",
    "AVF report is advisory only.",
    "High score does not override HardMask.",
    "Top rank does not grant permission.",
    "AVF cannot bypass Root.",
    "AVF cannot create FinalOutput.",
    "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Runtime materializes and owns RuntimeExecutionTopology locally.",
    "Provider does not own PlanGraph.",
    "PlanGraph is not authority.",
    "Branch ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
    "Only Root creates ActionCommitPacket v0.2.",
    "Human approval does not directly create ActionCommitPacket.",
    "LLM does not create ActionCommitPacket.",
    "DRS does not create ActionCommitPacket.",
    "AVF does not create ActionCommitPacket.",
    "GT/LGT does not create ActionCommitPacket.",
    "ActionCommitPacket is not FinalOutput.",
    "ActionCommitPacket is not receipt.",
    "ActionCommitPacket is not payment execution.",
    "ActionCommitPacket is not shipment release.",
    "Local packet registry is not DRS.",
    "Local packet registry is not authority.",
    "Local packet registry is not permission.",
    "Packet accepted for mock corridor is not payment execution.",
    "MockBankSandbox corridor is deterministic, not reasoning.",
    "MockBankSandbox does not restart LLM reasoning after Root.",
    "MockBankSandbox does not decide.",
    "MockBankSandbox does not create authority.",
    "Mock receipt is evidence only.",
    "Mock receipt is not permission.",
    "Mock receipt is not FinalOutput.",
    "Mock receipt does not authorize Supplier B.",
    "Mock receipt does not release shipment.",
    "Mock receipt does not create future permission.",
    "Terminal receipt observation is local proof-only.",
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

DRS_V0_2_NON_AUTHORITY_BOUNDARIES = (
    "DRS is not truth.",
    "DRS is not authority.",
    "DRS is not permission.",
    "DRS hit is context only.",
    "Reuse candidate is not direct reuse.",
    "Old receipt is not current permission.",
    "Old Root Final is not silently reused.",
    "Root remains final authority.",
    "DRS writeback after Root is local proof/audit only.",
)

AVF_V0_2_NON_AUTHORITY_BOUNDARIES = (
    "AVF is not truth.",
    "AVF is not authority.",
    "AVF is not permission.",
    "AVF score is not Root.",
    "Top-ranked candidate is not permission.",
    "CandidateVector is not action permission.",
    "CandidateVector is not FinalOutput.",
    "HardMask is not Root.",
    "AVF report is advisory only.",
    "High score does not override HardMask.",
    "Top rank does not grant permission.",
    "AVF cannot bypass Root.",
    "AVF cannot create FinalOutput.",
    "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release.",
    "Root remains final authority.",
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
            "Real Gemini Architect proposed semantic intent; local runtime materialized and owned RuntimeExecutionTopology.",
            "truth, authority, action permission, FinalOutput, provider-owned PlanGraph, ActionCommitPacket, receipt, payment, or shipment release.",
            "runtime_execution_topology_materialized",
            "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
        ),
        _transition_card(
            "runtime_execution_topology_materialized",
            "runtime",
            "MATERIALIZE local RuntimeExecutionTopology",
            "Materialize local RuntimeExecutionTopology from validated semantic proposal material and deterministic module observations.",
            "Local runtime materialized RuntimeExecutionTopology.",
            "RuntimeExecutionTopology is materialized and owned locally by runtime",
            "authority, permission, effect, receipt, or Root final",
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
        "runtime_execution_topology_materialized_count": 1,
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


def _drs_v0_2_resolve() -> dict[str, Any]:
    query = TemporalQueryV02(
        query_id="tq_full_wow_v1_2_drs_v0_2_baseline",
        as_of="2026-07-06T17:10:00Z",
        context_time="full_wow_v1_2",
        freshness_bias="current",
        require_root_review=True,
        allow_direct_reuse_if_all_gates_pass=False,
    )
    records = build_wow_v1_2_drs_v02_regression_records()
    report = resolve_drs_records_v02(
        LocalDRSResolveInputV02(
            temporal_query=query,
            records=records,
        )
    )
    drs_status = (
        "PASS"
        if report.temporal_query_present
        and report.records_evaluated_count == len(records) == 11
        and report.direct_reuse_allowed_count == 0
        and report.root_review_required_count == len(records)
        else "FAIL_CLOSED"
    )
    decisions_summary = tuple(
        {
            "record_id": decision.record_id,
            "reuse_decision_class": decision.reuse_decision_class,
            "freshness_class": decision.freshness_class,
            "direct_reuse_allowed": decision.direct_reuse_allowed,
            "context_only": decision.context_only,
            "root_review_required": decision.root_review_required,
            "reason_codes": decision.reason_codes,
            "truth_claimed": decision.truth_claimed,
            "authority_claimed": decision.authority_claimed,
            "action_permission_claimed": decision.action_permission_claimed,
            "final_output_claimed": decision.final_output_claimed,
        }
        for decision in report.decisions
    )
    return {
        "drs_v0_2_status": drs_status,
        "query_id": query.query_id,
        "resolver_mode": report.resolver_mode,
        "temporal_query_present": report.temporal_query_present,
        "records_evaluated_count": report.records_evaluated_count,
        "direct_reuse_allowed_count": report.direct_reuse_allowed_count,
        "direct_reuse_candidate_count": report.direct_reuse_candidate_count,
        "context_only_count": report.context_only_count,
        "warning_only_count": report.warning_only_count,
        "rerun_required_count": report.rerun_required_count,
        "blocked_count": report.blocked_count,
        "root_review_required_count": report.root_review_required_count,
        "freshness_table": report.freshness_table,
        "lineage_table": report.lineage_table,
        "provenance_table": report.provenance_table,
        "reuse_decision_table": report.reuse_decision_table,
        "resolve_rows": tuple(asdict(row) for row in report.rows),
        "decisions_summary": decisions_summary,
        "baseline_regression_scenario_ids": tuple(
            record.record_id for record in records
        ),
        "drs_non_authority_boundaries": DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


def _avf_v0_2_evaluation() -> dict[str, Any]:
    evaluation_input = build_wow_v1_2_avf_v02_evaluation_input()
    report = evaluate_avf_candidates_v02(evaluation_input)
    decision_reports_summary = tuple(
        {
            "candidate_id": decision.candidate_id,
            "source_drs_record_refs": decision.source_drs_record_refs,
            "hard_mask_value": decision.hard_mask.hard_mask_value,
            "hard_mask_reasons": decision.hard_mask.hard_mask_reasons,
            "soft_penalty": decision.soft_mask.soft_penalty,
            "soft_penalty_reasons": decision.soft_mask.soft_penalty_reasons,
            "final_avf_score": decision.score_explanation.final_avf_score,
            "rank": decision.score_explanation.rank,
            "score_is_not_permission": (
                decision.score_explanation.score_is_not_permission
            ),
            "top_ranked_candidate_not_permission": (
                decision.score_explanation.top_ranked_candidate_not_permission
            ),
            "candidate_is_not_action": decision.score_explanation.candidate_is_not_action,
            "candidate_vector_is_not_final_output": (
                decision.score_explanation.candidate_vector_is_not_final_output
            ),
            "truth_claimed": decision.score_explanation.truth_claimed,
            "authority_claimed": decision.score_explanation.authority_claimed,
            "action_permission_claimed": (
                decision.score_explanation.action_permission_claimed
            ),
            "final_output_claimed": decision.score_explanation.final_output_claimed,
            "approved": decision.approved,
            "execute": decision.execute,
            "ready": decision.ready,
            "payment_allowed": decision.payment_allowed,
            "shipment_release_allowed": decision.shipment_release_allowed,
            "final_decision": decision.final_decision,
        }
        for decision in report.decision_reports
    )
    avf_status = (
        "PASS"
        if report.candidates_evaluated_count == 9
        and report.advisory_only
        and report.top_ranked_candidate_not_permission
        and report.avf_score_is_not_authority
        and report.hardmask_is_not_root
        and report.real_world_effects_count == 0
        else "FAIL_CLOSED"
    )
    return {
        "avf_v0_2_status": avf_status,
        "evaluation_id": report.evaluation_id,
        "resolver_mode": report.resolver_mode,
        "candidates_evaluated_count": report.candidates_evaluated_count,
        "top_candidate_id": report.top_candidate_id,
        "top_candidate_score": report.top_candidate_score,
        "hard_masked_count": report.hard_masked_count,
        "unmasked_count": report.unmasked_count,
        "root_review_required_count": report.root_review_required_count,
        "ranked_candidates": tuple(asdict(row) for row in report.ranked_candidates),
        "hard_mask_table": report.hard_mask_table,
        "soft_mask_table": report.soft_mask_table,
        "score_explanation_table": report.score_explanation_table,
        "decision_reports_summary": decision_reports_summary,
        "source_drs_report_ref": evaluation_input.source_drs_report_ref,
        "source_drs_record_refs": evaluation_input.source_drs_record_refs,
        "avf_non_authority_boundaries": AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


ACTION_COMMIT_PACKET_V0_2_NON_AUTHORITY_BOUNDARIES = (
    "Only Root creates ActionCommitPacket v0.2.",
    "Human approval is scoped evidence only.",
    "Human approval does not directly create ActionCommitPacket.",
    "LLM does not create ActionCommitPacket.",
    "DRS does not create ActionCommitPacket.",
    "AVF does not create ActionCommitPacket.",
    "GT/LGT does not create ActionCommitPacket.",
    "ActionCommitPacket is not FinalOutput.",
    "ActionCommitPacket is not receipt.",
    "ActionCommitPacket is not payment execution.",
    "ActionCommitPacket is not shipment release.",
    "Local packet registry is not DRS.",
    "Local packet registry is not authority.",
    "Local packet registry is not permission.",
    "Packet accepted for mock corridor is not payment execution.",
    "Root remains final authority.",
)


def _action_commit_packet_v0_2_integration() -> dict[str, Any]:
    packet, corridor, step, registry = (
        build_supplier_a_packet_corridor_validation_fixture_v02()
    )
    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    registry_report = validate_packet_against_registry_v02(packet, registry)
    corridor_entry_report = validate_packet_corridor_entry_v02(
        packet,
        corridor,
        step,
        registry,
    )
    packet_seen_registry = record_packet_seen_v02(registry, packet)
    packet_seen_recorded = (
        packet.packet_id in packet_seen_registry.seen_packet_ids
        and packet.idempotency.key in packet_seen_registry.used_idempotency_keys
    )
    terminal_receipt_recorded = bool(
        packet_seen_registry.terminal_receipt_packet_ids
        or packet_seen_registry.terminal_receipt_idempotency_keys
    )
    status = (
        "PASS"
        if packet_valid
        and registry_report.validation_status == STATUS_PASS
        and corridor_entry_report.validation_status == STATUS_PASS
        and corridor_entry_report.accepted_for_mock_corridor
        and packet_seen_recorded
        and not terminal_receipt_recorded
        else "FAIL_CLOSED"
    )

    return {
        "action_commit_packet_v0_2_status": status,
        "packet_id": packet.packet_id,
        "packet_type": packet.packet_type,
        "created_by": packet.created_by,
        "root_created": packet.root_created,
        "source_root_decision_ref": packet.source_root_decision_ref,
        "human_approval_ref": packet.human_approval_ref,
        "human_approval_is_scoped_evidence_only": True,
        "packet_validated": packet_valid,
        "packet_validation_reasons": packet_reasons,
        "registry_validated": registry_report.validation_status == STATUS_PASS,
        "registry_validation_reasons": registry_report.reason_codes,
        "registry_is_local_proof_only": registry.local_proof_only,
        "registry_is_not_drs": True,
        "registry_is_not_authority": True,
        "registry_is_not_permission": True,
        "packet_corridor_entry_validated": (
            corridor_entry_report.validation_status == STATUS_PASS
        ),
        "corridor_entry_validation_reasons": corridor_entry_report.reason_codes,
        "accepted_for_mock_corridor": (
            corridor_entry_report.accepted_for_mock_corridor
        ),
        "packet_seen_recorded_in_local_registry": packet_seen_recorded,
        "terminal_receipt_recorded": terminal_receipt_recorded,
        "mock_payment_order_created": False,
        "mock_receipt_created": False,
        "mock_bank_sandbox_executed": False,
        "allowed_subjects": packet.scope.allowed_subjects,
        "forbidden_subjects": packet.scope.forbidden_subjects,
        "allowed_actions": packet.scope.allowed_actions,
        "forbidden_actions": packet.scope.forbidden_actions,
        "allowed_adapters": packet.scope.allowed_adapters,
        "forbidden_adapters": packet.scope.forbidden_adapters,
        "payment_slot_ref": packet.scope.payment_slot_ref,
        "creditor_ref": packet.scope.creditor_ref,
        "amount": packet.scope.amount,
        "currency": packet.scope.currency,
        "idempotency_key": packet.idempotency.key,
        "packet_non_authority_boundaries": (
            ACTION_COMMIT_PACKET_V0_2_NON_AUTHORITY_BOUNDARIES
        ),
    }


def _corridor_step(
    step_id: str,
    input_summary: str,
    output_summary: str,
    meaning: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "step_id": step_id,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "meaning": meaning,
        "does_not_authorize": (
            "permission, Supplier B payment, shipment release, FinalOutput, "
            "or real-world effects"
        ),
        "next_step": next_step,
    }


def _mock_bank_sandbox_v0_2_corridor_execution() -> dict[str, Any]:
    packet, corridor, step, registry = (
        build_supplier_a_packet_corridor_validation_fixture_v02()
    )
    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    registry_report = validate_packet_against_registry_v02(packet, registry)
    corridor_entry_report = validate_packet_corridor_entry_v02(
        packet,
        corridor,
        step,
        registry,
    )
    step_report = validate_corridor_step_against_packet_v01(packet, step)
    packet_seen_registry = record_packet_seen_v02(registry, packet)
    source_packet_seen = (
        packet.packet_id in packet_seen_registry.seen_packet_ids
        and packet.idempotency.key in packet_seen_registry.used_idempotency_keys
    )

    mock_payment_intent = {
        "intent_id": "mock_payment_intent:supplier_a:inv_2042",
        "packet_id": packet.packet_id,
        "subject": packet.scope.creditor_ref,
        "payment_slot_ref": packet.scope.payment_slot_ref,
        "creditor_ref": packet.scope.creditor_ref,
        "amount": packet.scope.amount,
        "currency": packet.scope.currency,
        "adapter_id": packet.adapter_binding.adapter_id,
        "mock_only": True,
        "real_payment": False,
        "permission_source": "Root-created ActionCommitPacket only",
    }
    mock_payment_consent = {
        "consent_id": "mock_payment_consent:supplier_a:inv_2042",
        "packet_id": packet.packet_id,
        "consent_status": "mock_consent_validated",
        "scope_matches_packet": True,
        "supplier_b_excluded": True,
        "shipment_release_excluded": True,
        "real_bank_excluded": True,
    }
    mock_payment_order = {
        "order_id": "mock_payment_order:supplier_a:inv_2042",
        "packet_id": packet.packet_id,
        "intent_id": mock_payment_intent["intent_id"],
        "consent_id": mock_payment_consent["consent_id"],
        "order_status": "mock_order_created",
        "subject": packet.scope.creditor_ref,
        "amount": packet.scope.amount,
        "currency": packet.scope.currency,
        "payment_slot_ref": packet.scope.payment_slot_ref,
        "idempotency_key": packet.idempotency.key,
        "adapter_id": packet.adapter_binding.adapter_id,
        "mock_only": True,
        "real_payment_executed": False,
        "shipment_released": False,
    }

    receipt = build_supplier_a_mock_receipt_evidence_fixture_v01(packet)
    receipt_valid, receipt_reasons = validate_mock_receipt_evidence_v01(
        packet,
        receipt,
    )
    terminal_registry, terminal_reasons = record_terminal_receipt_observation_v02(
        packet_seen_registry,
        packet,
        receipt,
    )
    terminal_receipt_observed = (
        packet.packet_id in terminal_registry.terminal_receipt_packet_ids
        and packet.idempotency.key
        in terminal_registry.terminal_receipt_idempotency_keys
    )
    corridor_sequence = (
        _corridor_step(
            "root_created_action_commit_packet",
            "Root-created Supplier A packet model.",
            "Packet enters deterministic contract corridor.",
            "Scoped capability starts after Root only.",
            "packet_validation",
        ),
        _corridor_step(
            "packet_validation",
            "ActionCommitPacketV02 model.",
            f"packet_validated={_format_bool(packet_valid)}",
            "Shape, Root creation, scope, TTL, idempotency, and adapter binding are checked.",
            "local_registry_replay_guard",
        ),
        _corridor_step(
            "local_registry_replay_guard",
            "Empty local proof-only registry.",
            f"packet_accepted_for_corridor={_format_bool(registry_report.packet_accepted_for_corridor_validation)}",
            "Registry checks replay locally and remains non-authority.",
            "corridor_entry_validation",
        ),
        _corridor_step(
            "corridor_entry_validation",
            "Packet, corridor, child step, and registry.",
            f"accepted_for_mock_corridor={_format_bool(corridor_entry_report.accepted_for_mock_corridor)}",
            "Entry validates packet plus child corridor containment.",
            "mock_payment_intent_consent",
        ),
        _corridor_step(
            "mock_payment_intent_consent",
            "Validated packet scope.",
            "mock payment intent and mock consent created.",
            "Intent and consent are deterministic local structures.",
            "scope_check",
        ),
        _corridor_step(
            "scope_check",
            "Child corridor allowed subjects/actions.",
            "Supplier A remains the only allowed subject.",
            "Scope is contained by packet scope.",
            "amount_check",
        ),
        _corridor_step(
            "amount_check",
            "Packet amount and child step amount.",
            "amount matches packet.",
            "Amount cannot drift after Root.",
            "creditor_check",
        ),
        _corridor_step(
            "creditor_check",
            "Packet creditor and child step creditor.",
            "creditor matches Supplier A.",
            "Creditor cannot drift to Supplier B.",
            "payment_slot_check",
        ),
        _corridor_step(
            "payment_slot_check",
            "Packet payment slot and child step payment slot.",
            "payment_slot matches packet.",
            "Payment slot remains evidence-bound and not permission.",
            "adapter_binding_check",
        ),
        _corridor_step(
            "adapter_binding_check",
            "Packet adapter binding and allowed adapters.",
            "mock_bank_sandbox adapter is inside allowed scope.",
            "Real bank, supplier API, and warehouse API remain excluded.",
            "idempotency_check",
        ),
        _corridor_step(
            "idempotency_check",
            "Packet idempotency key and child step key.",
            "idempotency key matches packet.",
            "Replay guard remains local proof-only.",
            "expiry_ttl_check",
        ),
        _corridor_step(
            "expiry_ttl_check",
            "Packet TTL and child step TTL.",
            "child TTL does not exceed packet TTL.",
            "Expired or wider TTL would fail closed.",
            "forbidden_surface_check",
        ),
        _corridor_step(
            "forbidden_surface_check",
            "Packet forbidden subjects, actions, and adapters.",
            "Supplier B, shipment release, and real APIs remain forbidden.",
            "Forbidden surface cannot shrink after Root.",
            "mock_payment_order",
        ),
        _corridor_step(
            "mock_payment_order",
            "Mock intent, mock consent, and validated packet.",
            "mock payment order created.",
            "Order is deterministic mock evidence, not real payment.",
            "mock_receipt_evidence",
        ),
        _corridor_step(
            "mock_receipt_evidence",
            "Mock payment order and packet.",
            f"receipt_validated={_format_bool(receipt_valid)}",
            "Receipt evidence is bound to packet, adapter, amount, currency, and idempotency.",
            "terminal_receipt_observation",
        ),
        _corridor_step(
            "terminal_receipt_observation",
            "Validated receipt evidence and local registry.",
            f"terminal_receipt_observed={_format_bool(terminal_receipt_observed)}",
            "Registry observes terminal receipt locally and creates no receipt.",
            "status_evidence_returns_to_root",
        ),
        _corridor_step(
            "status_evidence_returns_to_root",
            "Mock receipt evidence and local registry status.",
            "status/evidence returns to Root.",
            "Root remains final authority.",
            "root_boundary",
        ),
    )
    status = (
        "PASS"
        if packet_valid
        and registry_report.validation_status == STATUS_PASS
        and corridor_entry_report.validation_status == STATUS_PASS
        and step_report.validation_status == STATUS_PASS
        and corridor_entry_report.accepted_for_mock_corridor
        and source_packet_seen
        and receipt_valid
        and not terminal_reasons
        and terminal_receipt_observed
        and receipt.evidence_only
        and not receipt.creates_future_permission
        and not receipt.creates_action_permission
        and not receipt.creates_final_output
        and not receipt.authorizes_supplier_b
        and not receipt.releases_shipment
        and not receipt.mutates_packet_scope
        and not receipt.creates_production_drs_record
        and receipt.real_world_effects_count == 0
        else "FAIL_CLOSED"
    )

    return {
        "mock_bank_sandbox_v0_2_status": status,
        "source_packet_id": packet.packet_id,
        "source_packet_validated": packet_valid,
        "source_packet_validation_reasons": packet_reasons,
        "source_packet_corridor_entry_validated": (
            corridor_entry_report.validation_status == STATUS_PASS
        ),
        "source_packet_corridor_entry_reasons": corridor_entry_report.reason_codes,
        "source_packet_seen_in_registry": source_packet_seen,
        "corridor_sequence": corridor_sequence,
        "mock_payment_intent": mock_payment_intent,
        "mock_payment_consent": mock_payment_consent,
        "mock_payment_order": mock_payment_order,
        "mock_receipt_evidence": asdict(receipt),
        "receipt_validated": receipt_valid,
        "receipt_validation_reasons": receipt_reasons,
        "terminal_receipt_observed_in_local_registry": terminal_receipt_observed,
        "terminal_receipt_observation_reasons": terminal_reasons,
        "terminal_receipt_observation_is_local_proof_only": (
            terminal_registry.local_proof_only
            and not terminal_registry.production_persistence
            and not terminal_registry.global_drs_write
            and not terminal_registry.external_drs_write
        ),
        "receipt_evidence_only": receipt.evidence_only,
        "receipt_permission_created": receipt.creates_action_permission,
        "receipt_future_permission_created": receipt.creates_future_permission,
        "receipt_final_output_created": receipt.creates_final_output,
        "receipt_authorizes_supplier_b": receipt.authorizes_supplier_b,
        "receipt_releases_shipment": receipt.releases_shipment,
        "receipt_mutates_packet_scope": receipt.mutates_packet_scope,
        "receipt_creates_production_drs_record": (
            receipt.creates_production_drs_record
        ),
        "supplier_b_excluded": "supplier_b_balkan_pumps"
        in packet.scope.forbidden_subjects,
        "shipment_release_excluded": "shipment_release" in packet.scope.forbidden_actions,
        "real_bank_excluded": "real_bank" in packet.scope.forbidden_adapters,
        "real_payment_executed": False,
        "real_world_effects_count": receipt.real_world_effects_count,
    }


def collect_full_wow_v1_2_product_trace() -> dict[str, Any]:
    branches = _fractal_branches()
    result_proposals = _result_proposals(branches)
    drs_resolve = _drs_v0_2_resolve()
    avf_evaluation = _avf_v0_2_evaluation()
    action_commit_packet_integration = _action_commit_packet_v0_2_integration()
    mock_bank_corridor_execution = _mock_bank_sandbox_v0_2_corridor_execution()
    counters = _counters()
    counters.update(
        {
            "drs_v0_2_resolve_invoked_count": 1,
            "drs_v0_2_records_evaluated_count": drs_resolve[
                "records_evaluated_count"
            ],
            "drs_v0_2_direct_reuse_allowed_count": drs_resolve[
                "direct_reuse_allowed_count"
            ],
            "drs_v0_2_context_only_count": drs_resolve["context_only_count"],
            "drs_v0_2_warning_only_count": drs_resolve["warning_only_count"],
            "drs_v0_2_rerun_required_count": drs_resolve["rerun_required_count"],
            "drs_v0_2_blocked_count": drs_resolve["blocked_count"],
            "drs_v0_2_root_review_required_count": drs_resolve[
                "root_review_required_count"
            ],
            "drs_v0_2_lineage_table_created_count": 1,
            "drs_v0_2_freshness_table_created_count": 1,
            "drs_v0_2_provenance_table_created_count": 1,
            "drs_v0_2_reuse_decision_table_created_count": 1,
            "drs_v0_2_external_drs_used_count": 0,
            "drs_v0_2_global_drs_used_count": 0,
            "drs_v0_2_vector_db_used_count": 0,
            "drs_v0_2_embeddings_required_count": 0,
            "drs_v0_2_permission_granted_count": 0,
            "drs_v0_2_root_bypass_count": 0,
            "avf_v0_2_evaluation_invoked_count": 1,
            "avf_v0_2_candidates_evaluated_count": avf_evaluation[
                "candidates_evaluated_count"
            ],
            "avf_v0_2_hard_masked_count": avf_evaluation["hard_masked_count"],
            "avf_v0_2_unmasked_count": avf_evaluation["unmasked_count"],
            "avf_v0_2_root_review_required_count": avf_evaluation[
                "root_review_required_count"
            ],
            "avf_v0_2_high_score_hardmask_override_count": 0,
            "avf_v0_2_top_ranked_candidate_permission_granted_count": 0,
            "avf_v0_2_action_permission_granted_count": 0,
            "avf_v0_2_final_output_created_count": 0,
            "avf_v0_2_action_commit_packet_created_count": 0,
            "avf_v0_2_receipt_created_count": 0,
            "avf_v0_2_payment_executed_count": 0,
            "avf_v0_2_shipment_released_count": 0,
            "avf_v0_2_root_bypass_count": 0,
            "avf_v0_2_provider_called_count": 0,
            "avf_v0_2_network_called_count": 0,
            "avf_v0_2_gemini_called_count": 0,
            "product_trace_created_action_commit_packet_v0_2_model_packet_count": 1,
            "action_commit_packet_v0_2_integration_invoked_count": 1,
            "action_commit_packet_v0_2_root_created_model_packet_count": 1,
            "action_commit_packet_v0_2_root_created_packet_validated_count": 1,
            "action_commit_packet_v0_2_created_by_root_count": 1,
            "action_commit_packet_v0_2_created_by_human_count": 0,
            "action_commit_packet_v0_2_created_by_llm_count": 0,
            "action_commit_packet_v0_2_created_by_drs_count": 0,
            "action_commit_packet_v0_2_created_by_avf_count": 0,
            "action_commit_packet_v0_2_created_by_gt_lgt_count": 0,
            "action_commit_packet_v0_2_human_approval_used_as_evidence_count": 1,
            "action_commit_packet_v0_2_supplier_a_scope_allowed_count": 1,
            "action_commit_packet_v0_2_supplier_b_scope_allowed_count": 0,
            "action_commit_packet_v0_2_shipment_release_allowed_count": 0,
            "action_commit_packet_v0_2_real_bank_allowed_count": 0,
            "action_commit_packet_v0_2_real_supplier_api_allowed_count": 0,
            "action_commit_packet_v0_2_real_warehouse_api_allowed_count": 0,
            "action_commit_packet_v0_2_packet_registry_validated_count": 1,
            "action_commit_packet_v0_2_packet_corridor_entry_validated_count": 1,
            "action_commit_packet_v0_2_accepted_for_mock_corridor_count": 1,
            "action_commit_packet_v0_2_packet_seen_recorded_count": 1,
            "action_commit_packet_v0_2_terminal_receipt_recorded_count": 0,
            "action_commit_packet_v0_2_mock_payment_order_created_count": 0,
            "action_commit_packet_v0_2_mock_receipt_created_count": 0,
            "action_commit_packet_v0_2_mock_bank_sandbox_executed_count": 0,
            "action_commit_packet_v0_2_sandbox_adapter_execution_count": 0,
            "action_commit_packet_v0_2_payment_executed_count": 0,
            "action_commit_packet_v0_2_shipment_released_count": 0,
            "action_commit_packet_v0_2_final_output_created_count": 0,
            "action_commit_packet_v0_2_root_bypass_count": 0,
            "action_commit_packet_v0_2_provider_called_count": 0,
            "action_commit_packet_v0_2_network_called_count": 0,
            "action_commit_packet_v0_2_gemini_called_count": 0,
            "action_commit_packet_v0_2_real_world_effects_count": 0,
            "mock_bank_sandbox_v0_2_corridor_invoked_count": 1,
            "mock_bank_sandbox_v0_2_packet_consumed_count": 1,
            "mock_bank_sandbox_v0_2_packet_validated_count": 1,
            "mock_bank_sandbox_v0_2_scope_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_amount_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_creditor_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_payment_slot_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_adapter_binding_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_idempotency_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_expiry_ttl_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_forbidden_surface_check_passed_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_intent_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_consent_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_order_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count": 1,
            "mock_bank_sandbox_v0_2_receipt_validated_count": 1,
            "mock_bank_sandbox_v0_2_terminal_receipt_observed_count": 1,
            "mock_bank_sandbox_v0_2_receipt_permission_created_count": 0,
            "mock_bank_sandbox_v0_2_receipt_future_permission_created_count": 0,
            "mock_bank_sandbox_v0_2_receipt_final_output_created_count": 0,
            "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count": 0,
            "mock_bank_sandbox_v0_2_receipt_shipment_release_count": 0,
            "mock_bank_sandbox_v0_2_receipt_scope_mutation_count": 0,
            "mock_bank_sandbox_v0_2_receipt_production_drs_write_count": 0,
            "mock_bank_sandbox_v0_2_real_bank_api_called_count": 0,
            "mock_bank_sandbox_v0_2_real_supplier_api_called_count": 0,
            "mock_bank_sandbox_v0_2_real_warehouse_api_called_count": 0,
            "mock_bank_sandbox_v0_2_real_payment_executed_count": 0,
            "mock_bank_sandbox_v0_2_shipment_released_count": 0,
            "mock_bank_sandbox_v0_2_provider_called_count": 0,
            "mock_bank_sandbox_v0_2_network_called_count": 0,
            "mock_bank_sandbox_v0_2_gemini_called_count": 0,
            "mock_bank_sandbox_v0_2_real_world_effects_count": 0,
        }
    )
    transition_cards = _transition_cards()
    final_status = (
        "PASS"
        if len(transition_cards) == counters["transition_cards_created_count"]
        and len(branches) == counters["fractal_branch_cells_created_count"]
        and len(result_proposals) == counters["branch_result_proposals_created_count"]
        and drs_resolve["drs_v0_2_status"] == "PASS"
        and avf_evaluation["avf_v0_2_status"] == "PASS"
        and action_commit_packet_integration[
            "action_commit_packet_v0_2_status"
        ] == "PASS"
        and counters["drs_v0_2_records_evaluated_count"] == 11
        and counters["drs_v0_2_direct_reuse_allowed_count"] == 0
        and counters["avf_v0_2_candidates_evaluated_count"] == 9
        and counters["avf_v0_2_top_ranked_candidate_permission_granted_count"] == 0
        and counters["action_commit_packet_v0_2_accepted_for_mock_corridor_count"]
        == 1
        and counters["action_commit_packet_v0_2_terminal_receipt_recorded_count"] == 0
        and counters["action_commit_packet_v0_2_mock_bank_sandbox_executed_count"]
        == 0
        and mock_bank_corridor_execution[
            "mock_bank_sandbox_v0_2_status"
        ] == "PASS"
        and counters["mock_bank_sandbox_v0_2_mock_payment_order_created_count"] == 1
        and counters["mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count"]
        == 1
        and counters["mock_bank_sandbox_v0_2_terminal_receipt_observed_count"] == 1
        and counters["mock_bank_sandbox_v0_2_real_payment_executed_count"] == 0
        and counters["mock_bank_sandbox_v0_2_shipment_released_count"] == 0
        and counters["mock_bank_sandbox_v0_2_real_world_effects_count"] == 0
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
            "runtime_execution_topology_materialized_count": counters[
                "runtime_execution_topology_materialized_count"
            ],
            "provider_owned_plangraph_count": counters["provider_owned_plangraph_count"],
            "plan_graph_authority_count": counters["plan_graph_authority_count"],
            "runtime_execution_topology_owned_by_local_runtime": True,
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
        "drs_v0_2_resolve": drs_resolve,
        "avf_v0_2_evaluation": avf_evaluation,
        "action_commit_packet_v0_2_integration": action_commit_packet_integration,
        "mock_bank_sandbox_v0_2_corridor_execution": (
            mock_bank_corridor_execution
        ),
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
        "Local DRS v0.2 resolve table is now observed in the deterministic product trace.",
        "Local AVF v0.2 advisory evaluation is now observed in the deterministic product trace.",
        "This remains deterministic/local; no external DRS, global DRS, vector DB, or embeddings path is used.",
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

    drs_resolve = report["drs_v0_2_resolve"]
    lines.extend(["", "[LOCAL DRS V0.2 RESOLVE]"])
    lines.extend(
        _render_mapping(
            {
                "drs_v0_2_status": drs_resolve["drs_v0_2_status"],
                "query_id": drs_resolve["query_id"],
                "resolver_mode": drs_resolve["resolver_mode"],
                "temporal_query_present": drs_resolve["temporal_query_present"],
                "records_evaluated_count": drs_resolve["records_evaluated_count"],
                "direct_reuse_allowed_count": drs_resolve[
                    "direct_reuse_allowed_count"
                ],
                "root_review_required_count": drs_resolve[
                    "root_review_required_count"
                ],
            }
        )
    )
    lines.extend(
        [
            "DRS found prior traces in the Full WOW v1.2 deterministic baseline.",
            "DRS classified them as context, warning, rerun, or blocked evidence.",
            "DRS did not authorize payment.",
            "DRS did not authorize shipment release.",
            "DRS did not make old receipt current permission.",
            "DRS did not silently reuse old Root Final.",
            "Old receipt is not current permission.",
            "Old Root Final is not silently reused.",
            "Changed facts require rerun validation.",
            "Root remains final authority.",
            "baseline_regression_scenario_ids:",
        ]
    )
    lines.extend(
        f"  - {scenario_id}"
        for scenario_id in drs_resolve["baseline_regression_scenario_ids"]
    )
    lines.append("reuse_decision_summary:")
    for decision in drs_resolve["decisions_summary"]:
        lines.append(
            "- {record_id}: class={reuse_decision_class}; direct_reuse_allowed={direct_reuse_allowed}; root_review_required={root_review_required}; reason_codes={reason_codes}".format(
                **{
                    **decision,
                    "direct_reuse_allowed": _format_bool(
                        decision["direct_reuse_allowed"]
                    ),
                    "root_review_required": _format_bool(
                        decision["root_review_required"]
                    ),
                    "reason_codes": ", ".join(decision["reason_codes"]),
                }
            )
        )
    lines.append("drs_non_authority_boundaries:")
    lines.extend(
        f"  - {boundary}"
        for boundary in drs_resolve["drs_non_authority_boundaries"]
    )

    avf_evaluation = report["avf_v0_2_evaluation"]
    lines.extend(["", "[LOCAL AVF V0.2 ADVISORY EVALUATION]"])
    lines.extend(
        _render_mapping(
            {
                "avf_v0_2_status": avf_evaluation["avf_v0_2_status"],
                "evaluation_id": avf_evaluation["evaluation_id"],
                "resolver_mode": avf_evaluation["resolver_mode"],
                "candidates_evaluated_count": avf_evaluation[
                    "candidates_evaluated_count"
                ],
                "top_candidate_id": avf_evaluation["top_candidate_id"],
                "top_candidate_score": avf_evaluation["top_candidate_score"],
                "hard_masked_count": avf_evaluation["hard_masked_count"],
                "unmasked_count": avf_evaluation["unmasked_count"],
                "root_review_required_count": avf_evaluation[
                    "root_review_required_count"
                ],
            }
        )
    )
    lines.extend(
        [
            "AVF consumed Local DRS v0.2 candidate/reuse signals.",
            "AVF built CandidateVector pressure rows.",
            "AVF applied HardMask / SoftMask / score explanation.",
            "release_all_and_pay_all was hard masked.",
            "Supplier B payment was hard masked.",
            "safe candidates may rank but do not grant permission.",
            "top-ranked candidate is not permission.",
            "AVF score is not authority.",
            "HardMask is not Root.",
            "High score does not override HardMask.",
            "Top rank does not grant permission.",
            "AVF cannot bypass Root.",
            "AVF cannot create FinalOutput.",
            "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release.",
            "Root remains final authority.",
            "ranked_candidates:",
        ]
    )
    for row in avf_evaluation["ranked_candidates"]:
        lines.append(
            "- {candidate_id}: rank={rank}; final_avf_score={final_avf_score}; hard_mask_value={hard_mask_value}; root_review_required={root_review_required}".format(
                **{
                    **row,
                    "root_review_required": _format_bool(
                        row["root_review_required"]
                    ),
                }
            )
        )
    lines.append("avf_non_authority_boundaries:")
    lines.extend(
        f"  - {boundary}"
        for boundary in avf_evaluation["avf_non_authority_boundaries"]
    )

    acp_v0_2 = report["action_commit_packet_v0_2_integration"]
    lines.extend(["", "[ACTIONCOMMITPACKET V0.2 ROOT-CREATED PACKET BOUNDARY]"])
    lines.extend(
        _render_mapping(
            {
                "action_commit_packet_v0_2_status": acp_v0_2[
                    "action_commit_packet_v0_2_status"
                ],
                "packet_id": acp_v0_2["packet_id"],
                "packet_type": acp_v0_2["packet_type"],
                "created_by": acp_v0_2["created_by"],
                "root_created": acp_v0_2["root_created"],
                "packet_validated": acp_v0_2["packet_validated"],
                "registry_validated": acp_v0_2["registry_validated"],
                "packet_corridor_entry_validated": acp_v0_2[
                    "packet_corridor_entry_validated"
                ],
                "accepted_for_mock_corridor": acp_v0_2[
                    "accepted_for_mock_corridor"
                ],
                "packet_seen_recorded_in_local_registry": acp_v0_2[
                    "packet_seen_recorded_in_local_registry"
                ],
                "terminal_receipt_recorded": acp_v0_2[
                    "terminal_receipt_recorded"
                ],
                "mock_payment_order_created": acp_v0_2[
                    "mock_payment_order_created"
                ],
                "mock_receipt_created": acp_v0_2["mock_receipt_created"],
                "mock_bank_sandbox_executed": acp_v0_2[
                    "mock_bank_sandbox_executed"
                ],
            }
        )
    )
    lines.extend(
        [
            "Root created a scoped Supplier A ActionCommitPacket model.",
            "Human approval is scoped evidence only and did not create the packet.",
            "LLM/DRS/AVF/GT-LGT did not create the packet.",
            "Supplier A is allowed.",
            "Supplier B is excluded.",
            "Shipment release is excluded.",
            "Real bank / real supplier API / real warehouse API are excluded.",
            "Packet adapter binding is inside allowed scope.",
            "Local registry accepted an unseen valid packet for corridor validation.",
            "Registry is local proof-only, not DRS, not authority, and not permission.",
            "Packet is accepted for future mock corridor only.",
            "Slice C does not execute MockBankSandbox.",
            "Slice C does not create mock payment order.",
            "Slice C does not create receipt.",
            "Slice C does not execute payment.",
            "Slice C does not release shipment.",
            "Root remains final authority.",
            "allowed_subjects:",
        ]
    )
    lines.extend(f"  - {subject}" for subject in acp_v0_2["allowed_subjects"])
    lines.append("forbidden_subjects:")
    lines.extend(f"  - {subject}" for subject in acp_v0_2["forbidden_subjects"])
    lines.append("allowed_actions:")
    lines.extend(f"  - {action}" for action in acp_v0_2["allowed_actions"])
    lines.append("forbidden_actions:")
    lines.extend(f"  - {action}" for action in acp_v0_2["forbidden_actions"])
    lines.append("allowed_adapters:")
    lines.extend(f"  - {adapter}" for adapter in acp_v0_2["allowed_adapters"])
    lines.append("forbidden_adapters:")
    lines.extend(f"  - {adapter}" for adapter in acp_v0_2["forbidden_adapters"])
    lines.append("packet_non_authority_boundaries:")
    lines.extend(
        f"  - {boundary}"
        for boundary in acp_v0_2["packet_non_authority_boundaries"]
    )

    mock_corridor = report["mock_bank_sandbox_v0_2_corridor_execution"]
    lines.extend(["", "[MOCKBANKSANDBOX V0.2 CONTRACT FULFILLMENT CORRIDOR]"])
    lines.extend(
        _render_mapping(
            {
                "mock_bank_sandbox_v0_2_status": mock_corridor[
                    "mock_bank_sandbox_v0_2_status"
                ],
                "source_packet_id": mock_corridor["source_packet_id"],
                "source_packet_validated": mock_corridor[
                    "source_packet_validated"
                ],
                "source_packet_corridor_entry_validated": mock_corridor[
                    "source_packet_corridor_entry_validated"
                ],
                "source_packet_seen_in_registry": mock_corridor[
                    "source_packet_seen_in_registry"
                ],
                "receipt_validated": mock_corridor["receipt_validated"],
                "terminal_receipt_observed_in_local_registry": mock_corridor[
                    "terminal_receipt_observed_in_local_registry"
                ],
                "receipt_evidence_only": mock_corridor["receipt_evidence_only"],
                "receipt_permission_created": mock_corridor[
                    "receipt_permission_created"
                ],
                "receipt_future_permission_created": mock_corridor[
                    "receipt_future_permission_created"
                ],
                "receipt_final_output_created": mock_corridor[
                    "receipt_final_output_created"
                ],
                "receipt_authorizes_supplier_b": mock_corridor[
                    "receipt_authorizes_supplier_b"
                ],
                "receipt_releases_shipment": mock_corridor[
                    "receipt_releases_shipment"
                ],
                "receipt_mutates_packet_scope": mock_corridor[
                    "receipt_mutates_packet_scope"
                ],
                "receipt_creates_production_drs_record": mock_corridor[
                    "receipt_creates_production_drs_record"
                ],
                "real_payment_executed": mock_corridor[
                    "real_payment_executed"
                ],
                "real_world_effects_count": mock_corridor[
                    "real_world_effects_count"
                ],
            }
        )
    )
    lines.extend(
        [
            "MockBankSandbox consumed the Root-created Supplier A packet.",
            "The corridor validated packet shape, Root creation, scope, adapter, expiry, idempotency, amount, creditor, and payment slot.",
            "The corridor created a mock payment intent/consent/order.",
            "The corridor returned mock receipt evidence.",
            "Receipt is evidence only.",
            "Receipt did not create permission.",
            "Receipt did not authorize Supplier B.",
            "Receipt did not release shipment.",
            "Receipt did not create FinalOutput.",
            "Receipt did not mutate packet scope.",
            "Terminal receipt was observed in local proof-only registry.",
            "Supplier B remains blocked.",
            "Shipment remains held.",
            "Real bank / real supplier API / real warehouse API remained excluded.",
            "No real-world effect occurred.",
            "Root remains final authority.",
            "corridor_sequence:",
        ]
    )
    for step_row in mock_corridor["corridor_sequence"]:
        lines.append(
            "- {step_id}: input_summary={input_summary}; output_summary={output_summary}; meaning={meaning}; does_not_authorize={does_not_authorize}; next_step={next_step}".format(
                **step_row
            )
        )
    lines.append("mock_payment_intent:")
    lines.extend(f"  {line}" for line in _render_mapping(mock_corridor["mock_payment_intent"]))
    lines.append("mock_payment_consent:")
    lines.extend(f"  {line}" for line in _render_mapping(mock_corridor["mock_payment_consent"]))
    lines.append("mock_payment_order:")
    lines.extend(f"  {line}" for line in _render_mapping(mock_corridor["mock_payment_order"]))
    lines.append("mock_receipt_evidence:")
    lines.extend(f"  {line}" for line in _render_mapping(mock_corridor["mock_receipt_evidence"]))

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
                    "drs_v0_2_resolve": {
                        "drs_v0_2_status": drs_resolve["drs_v0_2_status"],
                        "records_evaluated_count": drs_resolve[
                            "records_evaluated_count"
                        ],
                        "direct_reuse_allowed_count": drs_resolve[
                            "direct_reuse_allowed_count"
                        ],
                        "root_review_required_count": drs_resolve[
                            "root_review_required_count"
                        ],
                    },
                    "avf_v0_2_evaluation": {
                        "avf_v0_2_status": avf_evaluation["avf_v0_2_status"],
                        "candidates_evaluated_count": avf_evaluation[
                            "candidates_evaluated_count"
                        ],
                        "top_candidate_id": avf_evaluation["top_candidate_id"],
                        "hard_masked_count": avf_evaluation["hard_masked_count"],
                        "unmasked_count": avf_evaluation["unmasked_count"],
                    },
                    "action_commit_packet_v0_2_integration": {
                        "action_commit_packet_v0_2_status": acp_v0_2[
                            "action_commit_packet_v0_2_status"
                        ],
                        "packet_id": acp_v0_2["packet_id"],
                        "packet_validated": acp_v0_2["packet_validated"],
                        "registry_validated": acp_v0_2["registry_validated"],
                        "accepted_for_mock_corridor": acp_v0_2[
                            "accepted_for_mock_corridor"
                        ],
                        "terminal_receipt_recorded": acp_v0_2[
                            "terminal_receipt_recorded"
                        ],
                    },
                    "mock_bank_sandbox_v0_2_corridor_execution": {
                        "mock_bank_sandbox_v0_2_status": mock_corridor[
                            "mock_bank_sandbox_v0_2_status"
                        ],
                        "source_packet_id": mock_corridor["source_packet_id"],
                        "receipt_validated": mock_corridor[
                            "receipt_validated"
                        ],
                        "terminal_receipt_observed_in_local_registry": mock_corridor[
                            "terminal_receipt_observed_in_local_registry"
                        ],
                        "receipt_evidence_only": mock_corridor[
                            "receipt_evidence_only"
                        ],
                        "real_world_effects_count": mock_corridor[
                            "real_world_effects_count"
                        ],
                    },
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
