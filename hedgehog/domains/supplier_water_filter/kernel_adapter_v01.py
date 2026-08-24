"""Deterministic pure in-memory Supplier / Water Filter domain adapter.

The adapter consumes one explicit already-collected source report and maps it
into existing Kernel contracts. It does not import or call the product-trace
collector and performs no provider, network, Gemini, filesystem, environment,
clock, randomness, real supplier, warehouse, bank, payment, shipment, or
connector operation. It changes no authority or permission law, has no Effect
Firewall access, and creates no Root, permission, FinalOutput, or effect. This
module makes no production claim.
"""

from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass, replace as _replace

from hedgehog.kernel import abi_v01 as _abi
from hedgehog.kernel import integrity_replay_v01 as _integrity
from hedgehog.kernel import multiroot_v01 as _multiroot

globals().pop("annotations", None)


MODULE_ID = "supplier_water_filter_kernel_adapter_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1d2"
ADAPTER_VERSION = "v0.1"

SOURCE_RUN_ID = "full_wow_v1_2_product_trace_v01"
SOURCE_REPORT_ID = "full_wow_v1_2_product_trace_v01"
SOURCE_TRACE_TYPE = "deterministic_product_trace_lane"
TRANSACTION_ID = "supplier_water_filter:SH-2042:INV-2042"
OWNER_ROOT_ID = "root:supplier_water_filter_business_owner"

SUPPLIER_A_STATUS = "SUPPLIER_A_SCOPED_REVIEW_READY"
SUPPLIER_B_STATUS = "BLOCKED"
SHIPMENT_STATUS = "HELD"
RECEIPT_STATUS = "EVIDENCE_ONLY"

BUSINESS_MODULE_COUNT = 7
TRANSITION_CARD_COUNT = 23
DEPENDENCY_EDGE_COUNT = 22
FRACTAL_BRANCH_COUNT = 8
RESULT_PROPOSAL_COUNT = 8
ROOT_DECISION_COUNT = 1
CROSS_ROOT_EVIDENCE_COUNT = 0

STATUS_PASS = "PASS"

_ADAPTER_ID_DOMAIN = "hedgehog.domains.supplier_water_filter.kernel_adapter.v01"
_SOURCE_REPORT_HASH_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.source_report.v01"
)
_EXPECTED_SOURCE_REPORT_HASH = (
    "4c72d34880b959928499fe1917556f29f42351a05d6cdc7a8844ced3059bbc3a"
)
_SOURCE_CARD_HASH_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.source_transition_card.v01"
)
_CAUSAL_OUTPUT_FIELD = "/source_card_hash"
_CAUSAL_EFFECT = "ordered_transition_card_continuity"
_CAUSAL_REASON = "used:supplier_water_filter_ordered_trace_hash"
_KERNEL_TIME_ENVELOPE = {
    "pt_created_at": "2026-01-01T00:00:00+00:00",
    "kt_asof": "2026-01-01T00:00:00+00:00",
    "et_observed_at": None,
    "ct_session_anchor": "session:fixture:supplier_water_filter_adapter:001",
    "ttl_seconds": 3600,
    "freshness_class": "static",
    "valid_from": "2026-01-01T00:00:00+00:00",
    "valid_to": "2026-01-01T01:00:00+00:00",
}
_BUSINESS_MODULE_IDS = (
    "warehouse_api_sandbox",
    "supplier_a_api_sandbox",
    "supplier_b_api_sandbox",
    "legal_module",
    "accounting_module",
    "bank_a_legacy_sandbox",
    "bank_b_hedgehog_native_preview",
)
_STEP_IDS = (
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
_EXPECTED_SOURCE_CARD_HASHES = (
    "7cb32b17bb7c0c1f5579c8962dc27f1c1b5ea9e5488aa86c7e50f2ec1f0a4cdf",
    "575cf0c5c8eb92c67f9d60b489f2d843175b6a4373a0f4945fbb9b46a39ef608",
    "46e04c450620adbe501a932253d605b430bc4802f52f3cdb31efc827be78a0a3",
    "3d9ad8444657bb0611824c5fdcb495d41c3ed946bf22a2d720ff5ce083a4bac5",
    "70c97fc96238d17ed8b66dc89889860f92db27014ade5a09bf52a9419a683e4a",
    "38d6e779896293c27de7d144794a1d26a7c0f16390beabd02a0164b684ecb0ab",
    "055f56fb81d58a905e542d296469a4f033a8612de48c24936b7ebc77fc89f484",
    "898d6c78765af8eab21eb73e11083195e8ce252fc721a98149c679024fd0d247",
    "b6a3a284928e1b9a3be7ed97b17c0eab06d4cbb1fc972a9483354601bb2c04da",
    "5e42f65023fd468b3369c06c5812c8f69435dd637cfe3703cd3e8ac7f9a65f66",
    "87f36e3c9e54297e17e99dc96098555f366b8a57d818150190ba82464ad3bf85",
    "118ca3fe32e9cc6fcf39b9a8bec5084a378b0213ed340ec5b21132c2a1d83db7",
    "d093609dd8c6246c367d263f05d3d352335b4892aea5d8e0bdf637c3e0c48a30",
    "48a0ecd610dac237d0f4d4602efca340c293dddd75338a235a384f85016f3198",
    "8743886df64328c33a2509b56324689c2f6c756d6be3617a6083a5685aaf77b9",
    "67126ccf123a281126efac6abf396f9e014f332a06b3f3280ac9adcb173bdcd0",
    "574fabc6bba8f4bab047d5fbdd8e36a437b059a50fd9e59ed3141ae33db31b94",
    "312bc4a6e5f9acf14281aa2f76d2ea7c2cbf71b83da34e3d425f1d669287ab91",
    "4d2bda39db74274d0a00f8940873ce2d658d430410f3209ebe8ed61af9e296d8",
    "97867054a9c0bef450d5422e01357c313a30d63371431e67b2e1a772e23d094d",
    "49911093aad0e065684a161eda30ff1971b3ede55dcf3a2c6547998f4cecde2f",
    "0eff2ba33bf08547122e29465fb66c33ca7495d9f7d439cde8728c7c173e989a",
    "6c609dfab06021acb78f2a28e3421d388af1b3a421cbc312d2a878da2fb2c3df",
)
_EXPECTED_EVIDENCE_IDS = (
    "dirty_request_v1_2",
    "warehouse_api_sandbox",
    "supplier_a_api_sandbox",
    "supplier_b_api_sandbox",
    "legal_module",
    "accounting_module",
    "bank_a_legacy_sandbox",
    "bank_b_hedgehog_native_preview",
    "full_wow_v1_1_manual_live_gemini_real_20260705_232010",
    "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
    "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
    "runtime_product_trace_plan_v1_2",
    "fractal_branch_cells_v1_2",
    "branch_result_proposals_v1_2",
    "post_vv_v1_2",
    "gt_lgt_v1_2",
    "root_first_not_ready_v1_2",
    "corrected_evidence_v1_2",
    "root_second_supplier_a_v1_2",
    "human_approval_supplier_a_v1_2",
    "closed_root_packet_boundary_v1_1",
    "closed_mock_receipt_boundary_v1_1",
    "full_wow_v1_2_product_trace_v01",
)
_BRANCH_IDS = (
    "warehouse_branch",
    "supplier_a_branch",
    "supplier_b_branch",
    "legal_branch",
    "accounting_branch",
    "bank_a_branch",
    "bank_b_branch",
    "root_merge_branch",
)
_EXPECTED_BRANCH_RESULT_PROPOSAL_IDS = tuple(
    f"{branch_id}_result_proposal" for branch_id in _BRANCH_IDS
)
_EXPECTED_RESULT_PROPOSAL_IDS = _EXPECTED_BRANCH_RESULT_PROPOSAL_IDS
_EXPECTED_PROPOSAL_SOURCE_BRANCH_IDS = _BRANCH_IDS
_EXPECTED_BRANCH_EVIDENCE_IDS = tuple(
    f"{branch_id}_evidence" for branch_id in _BRANCH_IDS
)
_EXPECTED_BRANCH_API_COUNTS = (1, 1, 1, 1, 1, 1, 1, 0)
_BRANCH_KEYS = frozenset(
    {
        "branch_id",
        "branch_context",
        "branch_evidence",
        "branch_result_proposal",
        "branch_authority_boundary",
        "branch_called_llm_or_slm_count",
        "branch_called_api_count",
        "branch_real_world_effects_count",
    }
)
_PROPOSAL_KEYS = frozenset(
    {
        "result_proposal_id",
        "source_branch_id",
        "proposal_status",
        "evidence_summary",
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
    }
)
_EXPECTED_PACKET_ALLOWED_SUBJECTS = ("supplier_a_adriatic_filters",)
_EXPECTED_PACKET_FORBIDDEN_SUBJECTS = (
    "supplier_b_balkan_pumps",
    "shipment_sh_2042",
)
_EXPECTED_PACKET_ALLOWED_ACTIONS = (
    "mock_supplier_a_payment_intent",
    "mock_supplier_a_payment_order",
)
_EXPECTED_PACKET_FORBIDDEN_ACTIONS = (
    "supplier_b_payment",
    "shipment_release",
    "real_payment",
    "real_bank_transfer",
)
_EXPECTED_PACKET_ALLOWED_ADAPTERS = ("mock_bank_sandbox", "bank_a_mock")
_EXPECTED_PACKET_FORBIDDEN_ADAPTERS = (
    "real_bank",
    "real_supplier_api",
    "real_warehouse_api",
)
_EXPECTED_PAYMENT_SLOT_REF = "payment_slot:bank_a_mock:inv_2042"
_EXPECTED_CREDITOR_REF = "supplier_a_adriatic_filters"
_EXPECTED_AMOUNT = "1250.00"
_EXPECTED_CURRENCY = "EUR"
_STEP_MAPPING = (
    ("dirty_request_received", "SemanticEvidence", "NON_AUTHORITY", "VALIDATED"),
    ("warehouse_inventory_query", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("supplier_a_availability_query", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("supplier_b_blocker_query", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("legal_insurance_contract_check", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("accounting_invoice_po_reconciliation", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("bank_a_payment_slot_prepared", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("bank_b_native_contract_preview", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("top_level_semantic_route_observed_from_v1_1", "SemanticEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("bsep_membrane_observed_from_v1_1", "BSEPProjection", "EVIDENCE_ONLY", "VALIDATED"),
    ("top_level_live_semantic_architect_observed_from_v1_1", "SemanticArchitectProposal", "ADVISORY", "VALIDATED"),
    (
        "runtime_execution_topology_materialized",
        "RuntimeExecutionTopology",
        "NON_AUTHORITY",
        "VALIDATED",
    ),
    ("fractal_branch_cells_dispatched", "RuntimeExecutionTopology", "NON_AUTHORITY", "VALIDATED"),
    ("branch_result_proposals_collected", "ResultProposal", "ADVISORY", "VALIDATED"),
    ("post_vv_validated", "PostVVReport", "ADVISORY", "VALIDATED"),
    ("gt_lgt_advisory_review", "GTAdvisoryReport", "ADVISORY", "VALIDATED"),
    ("root_first_not_ready", "RootDecision", "ROOT_OWNED", "ROOT_REJECTED"),
    ("corrected_evidence_received", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("root_second_supplier_a_scoped_review", "RootDecision", "ROOT_OWNED", "ROOT_REVIEWED"),
    ("human_approval_supplier_a_only", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("root_created_mock_action_commit_packet_observed", "RootOwnedIntent", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("mock_bank_sandbox_receipt_observed", "EvidenceReceipt", "EVIDENCE_ONLY", "RECEIPT_RECORDED"),
    ("final_state_summary", "TransactionOutcomeEnvelope", "NON_AUTHORITY", "FINALIZED"),
)
_CARD_KEYS = frozenset(
    {
        "step_id",
        "actor_or_module",
        "api_like_call",
        "input_summary",
        "output_summary",
        "meaning",
        "does_not_authorize",
        "next_step",
        "trace_id",
        "evidence_id",
    }
)
_PAYLOAD_KEYS = frozenset(
    {
        "source_index",
        "step_id",
        "actor_or_module",
        "api_like_call",
        "input_summary",
        "output_summary",
        "meaning",
        "does_not_authorize",
        "next_step",
        "trace_id",
        "evidence_id",
        "source_card_hash",
    }
)
_GENERIC_ZERO_COUNTER_FIELDS = (
    "provider_call_count",
    "network_call_count",
    "semantic_rerun_count",
    "transaction_rerun_count",
    "corridor_rerun_count",
    "ledger_recollection_count",
    "crypto_recollection_count",
    "root_decision_created_count",
    "authority_created_count",
    "permission_created_count",
    "action_created_count",
    "action_commit_packet_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
)
_ZERO_SOURCE_COUNTERS = (
    "top_level_orchestrator_llm_call_count",
    "top_level_architect_llm_call_count",
    "branch_local_llm_slm_call_count",
    "payment_permission_granted_before_root_count",
    "supplier_b_payment_allowed_count",
    "product_trace_created_action_commit_packet_count",
    "product_trace_created_receipt_count",
    "product_trace_executed_mock_payment_count",
    "product_trace_executed_real_payment_count",
    "product_trace_released_shipment_count",
    "product_trace_called_real_bank_supplier_warehouse_api_count",
    "shipment_released_count",
    "real_payment_executed_count",
    "avf_v0_2_top_ranked_candidate_permission_granted_count",
    "avf_v0_2_action_permission_granted_count",
    "avf_v0_2_final_output_created_count",
    "avf_v0_2_action_commit_packet_created_count",
    "avf_v0_2_receipt_created_count",
    "avf_v0_2_payment_executed_count",
    "avf_v0_2_shipment_released_count",
    "avf_v0_2_provider_called_count",
    "avf_v0_2_network_called_count",
    "avf_v0_2_gemini_called_count",
    "action_commit_packet_v0_2_created_by_human_count",
    "action_commit_packet_v0_2_created_by_llm_count",
    "action_commit_packet_v0_2_created_by_drs_count",
    "action_commit_packet_v0_2_created_by_avf_count",
    "action_commit_packet_v0_2_created_by_gt_lgt_count",
    "action_commit_packet_v0_2_supplier_b_scope_allowed_count",
    "action_commit_packet_v0_2_shipment_release_allowed_count",
    "action_commit_packet_v0_2_real_bank_allowed_count",
    "action_commit_packet_v0_2_real_supplier_api_allowed_count",
    "action_commit_packet_v0_2_real_warehouse_api_allowed_count",
    "action_commit_packet_v0_2_terminal_receipt_recorded_count",
    "action_commit_packet_v0_2_mock_payment_order_created_count",
    "action_commit_packet_v0_2_mock_receipt_created_count",
    "action_commit_packet_v0_2_mock_bank_sandbox_executed_count",
    "action_commit_packet_v0_2_sandbox_adapter_execution_count",
    "action_commit_packet_v0_2_payment_executed_count",
    "action_commit_packet_v0_2_shipment_released_count",
    "action_commit_packet_v0_2_final_output_created_count",
    "action_commit_packet_v0_2_root_bypass_count",
    "action_commit_packet_v0_2_provider_called_count",
    "action_commit_packet_v0_2_network_called_count",
    "action_commit_packet_v0_2_gemini_called_count",
    "action_commit_packet_v0_2_real_world_effects_count",
    "mock_bank_sandbox_v0_2_receipt_permission_created_count",
    "mock_bank_sandbox_v0_2_receipt_future_permission_created_count",
    "mock_bank_sandbox_v0_2_receipt_final_output_created_count",
    "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count",
    "mock_bank_sandbox_v0_2_receipt_shipment_release_count",
    "mock_bank_sandbox_v0_2_receipt_scope_mutation_count",
    "mock_bank_sandbox_v0_2_receipt_production_drs_write_count",
    "mock_bank_sandbox_v0_2_real_bank_api_called_count",
    "mock_bank_sandbox_v0_2_real_supplier_api_called_count",
    "mock_bank_sandbox_v0_2_real_warehouse_api_called_count",
    "mock_bank_sandbox_v0_2_real_payment_executed_count",
    "mock_bank_sandbox_v0_2_shipment_released_count",
    "mock_bank_sandbox_v0_2_provider_called_count",
    "mock_bank_sandbox_v0_2_network_called_count",
    "mock_bank_sandbox_v0_2_gemini_called_count",
    "mock_bank_sandbox_v0_2_real_world_effects_count",
    "real_world_effects_count",
)
_ONE_SOURCE_COUNTERS = (
    "product_trace_created_action_commit_packet_v0_2_model_packet_count",
    "action_commit_packet_v0_2_root_created_model_packet_count",
    "action_commit_packet_v0_2_created_by_root_count",
    "action_commit_packet_v0_2_supplier_a_scope_allowed_count",
    "mock_bank_sandbox_v0_2_mock_payment_order_created_count",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count",
    "mock_bank_sandbox_v0_2_terminal_receipt_observed_count",
)


@_dataclass(frozen=True, slots=True)
class SupplierWaterFilterKernelAdapterResultV01:
    adapter_id: str
    adapter_version: str
    source_run_id: str
    source_report_id: str
    source_trace_type: str
    transaction_id: str
    owner_root_id: str
    supplier_a_status: str
    supplier_b_status: str
    shipment_status: str
    receipt_status: str
    kernel_artifacts: tuple[_abi.KernelArtifactV01, ...]
    kernel_manifest: _integrity.ArtifactManifestV01
    kernel_unanchored_verification: _integrity.SealVerificationResultV01
    kernel_anchored_verification: _integrity.SealVerificationResultV01
    kernel_replay: _integrity.ReplayVerificationResultV01
    causal_consumption_refs: tuple[_abi.CausalConsumptionRefV01, ...]
    multiroot_outcome: _multiroot.TransactionOutcomeEnvelopeV01
    multiroot_validation: _multiroot.MultiRootValidationResultV01
    business_module_count: int
    transition_card_count: int
    dependency_edge_count: int
    fractal_branch_count: int
    result_proposal_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int


def _mapping(value: object) -> dict[str, object] | None:
    return value if type(value) is dict else None


def _source_report_hash(source_report: object) -> str:
    return _integrity.domain_separated_sha256_hex_v01(
        domain=_SOURCE_REPORT_HASH_DOMAIN,
        payload=_integrity.canonical_json_bytes_v01(source_report),
    )


def _source_report_errors(source_report: object) -> tuple[str, ...]:
    if type(source_report) is not dict:
        return ("supplier_water_filter_source_report_invalid",)
    try:
        errors: list[str] = []
        if (
            source_report.get("run_id") != SOURCE_RUN_ID
            or source_report.get("report_id") != SOURCE_REPORT_ID
            or source_report.get("trace_type") != SOURCE_TRACE_TYPE
        ):
            errors.append("supplier_water_filter_source_identity_mismatch")
        if (
            source_report.get("product_trace_status") != STATUS_PASS
            or source_report.get("final_status") != STATUS_PASS
            or source_report.get("v1_2_implemented_scope")
            != "deterministic_product_trace_only"
            or source_report.get("manual_live_multillm_fractal_lane_implemented")
            is not False
            or source_report.get("production_ready_claimed") is not False
            or source_report.get("public_auditor_ready_claimed") is not False
            or source_report.get("real_world_effects_count") != 0
            or source_report.get("validation_errors") != ()
        ):
            errors.append("supplier_water_filter_source_report_invalid")

        modules = source_report.get("business_modules")
        if (
            type(modules) is not tuple
            or len(modules) != BUSINESS_MODULE_COUNT
            or any(type(row) is not dict for row in modules)
            or tuple(row.get("module_id") for row in modules) != _BUSINESS_MODULE_IDS
        ):
            errors.append("supplier_water_filter_source_geometry_mismatch")
            modules_by_id: dict[str, dict[str, object]] = {}
        else:
            modules_by_id = {row["module_id"]: row for row in modules}
        if modules_by_id:
            warehouse = modules_by_id["warehouse_api_sandbox"]
            items = warehouse.get("items_checked")
            wf_rows = (
                tuple(row for row in items if type(row) is dict and row.get("sku") == "WF-100")
                if type(items) is tuple
                else ()
            )
            supplier_a = modules_by_id["supplier_a_api_sandbox"]
            supplier_b = modules_by_id["supplier_b_api_sandbox"]
            accounting = modules_by_id["accounting_module"]
            bank_a = modules_by_id["bank_a_legacy_sandbox"]
            bank_b = modules_by_id["bank_b_hedgehog_native_preview"]
            if (
                len(wf_rows) != 1
                or wf_rows[0].get("shortage_qty") != 2
                or supplier_a.get("can_cover_shortage_qty") != 2
                or supplier_b.get("supplier_status") != "blocked"
                or supplier_b.get("invoice_status") != "mismatch"
                or supplier_b.get("delivery_status") != "delayed"
                or supplier_b.get("legal_status") != "needs_review"
                or accounting.get("payment_permission_status") != "not_granted"
                or bank_a.get("payment_permission_status") != "not_granted"
                or bank_b.get("execution_allowed") is not False
                or bank_b.get("blocked_reasons")
                != ("invoice_mismatch", "delivery_delayed", "legal_needs_review")
                or any(
                    type(row.get("does_not_authorize")) is not str
                    or not row["does_not_authorize"]
                    for row in modules
                )
            ):
                errors.append("supplier_water_filter_source_business_outcome_mismatch")

        boundaries = _mapping(source_report.get("business_boundaries"))
        root = _mapping(source_report.get("post_vv_gt_root"))
        approval = _mapping(source_report.get("approval_packet_receipt_boundary"))
        if (
            boundaries is None
            or root is None
            or approval is None
            or boundaries.get("supplier_B_final_status") != SUPPLIER_B_STATUS
            or boundaries.get("shipment_final_status") != SHIPMENT_STATUS
            or boundaries.get("receipt_final_status") != RECEIPT_STATUS
            or boundaries.get("root_remains_final_authority") is not True
            or root.get("root_first_decision") != "NOT_READY"
            or root.get("root_second_decision") != SUPPLIER_A_STATUS
            or root.get("supplier_b_final_status") != SUPPLIER_B_STATUS
            or root.get("shipment_final_status") != SHIPMENT_STATUS
            or root.get("receipt_final_status") != RECEIPT_STATUS
            or root.get("root_remains_final_authority") is not True
            or approval.get("human_approval_scope") != "Supplier A only"
            or approval.get("root_created_mock_action_commit_packet_observed") is not True
            or approval.get("mock_bank_sandbox_receipt_observed") is not True
            or approval.get("product_trace_created_action_commit_packet_count") != 0
            or approval.get("product_trace_created_receipt_count") != 0
            or approval.get("product_trace_executed_mock_payment_count") != 0
        ):
            errors.append("supplier_water_filter_source_business_outcome_mismatch")

        cards = source_report.get("transition_cards")
        cards_valid = (
            type(cards) is tuple
            and len(cards) == TRANSITION_CARD_COUNT
            and all(type(card) is dict and frozenset(card) == _CARD_KEYS for card in cards)
            and all(
                all(type(card[key]) is str and bool(card[key]) for key in _CARD_KEYS)
                for card in cards
            )
        )
        if cards_valid:
            step_ids = tuple(card["step_id"] for card in cards)
            expected_next = (*_STEP_IDS[1:], "none")
            if (
                step_ids != _STEP_IDS
                or len(set(step_ids)) != TRANSITION_CARD_COUNT
                or tuple(card["next_step"] for card in cards) != expected_next
                or any(card["trace_id"] != SOURCE_RUN_ID for card in cards)
                or tuple(card["evidence_id"] for card in cards)
                != _EXPECTED_EVIDENCE_IDS
                or tuple(_source_card_hash(card) for card in cards)
                != _EXPECTED_SOURCE_CARD_HASHES
                or any(
                    type(card["does_not_authorize"]) is not str
                    or not card["does_not_authorize"]
                    for card in cards
                )
            ):
                cards_valid = False
        if not cards_valid:
            errors.append("supplier_water_filter_source_geometry_mismatch")

        branches = source_report.get("fractal_branches")
        proposals = source_report.get("branch_result_proposals")
        if (
            type(branches) is not tuple
            or len(branches) != FRACTAL_BRANCH_COUNT
            or any(type(row) is not dict or frozenset(row) != _BRANCH_KEYS for row in branches)
            or tuple(row.get("branch_id") for row in branches) != _BRANCH_IDS
            or len({row.get("branch_id") for row in branches}) != FRACTAL_BRANCH_COUNT
            or tuple(row.get("branch_result_proposal") for row in branches)
            != _EXPECTED_BRANCH_RESULT_PROPOSAL_IDS
            or tuple(row.get("branch_evidence") for row in branches)
            != _EXPECTED_BRANCH_EVIDENCE_IDS
            or tuple(row.get("branch_called_api_count") for row in branches)
            != _EXPECTED_BRANCH_API_COUNTS
            or any(
                row.get("branch_called_llm_or_slm_count") != 0
                or row.get("branch_real_world_effects_count") != 0
                for row in branches
            )
            or type(proposals) is not tuple
            or len(proposals) != RESULT_PROPOSAL_COUNT
            or any(type(row) is not dict or frozenset(row) != _PROPOSAL_KEYS for row in proposals)
            or tuple(row.get("result_proposal_id") for row in proposals)
            != _EXPECTED_RESULT_PROPOSAL_IDS
            or tuple(row.get("source_branch_id") for row in proposals)
            != _EXPECTED_PROPOSAL_SOURCE_BRANCH_IDS
            or any(
                row.get("result_proposal_id")
                != f"{row.get('source_branch_id')}_result_proposal"
                or row.get("proposal_status") != "accepted_for_root_review"
                or row.get("authority_claimed") is not False
                or row.get("action_permission_claimed") is not False
                or row.get("final_output_claimed") is not False
                for row in proposals
            )
        ):
            errors.append("supplier_water_filter_source_geometry_mismatch")

        drs = _mapping(source_report.get("drs_v0_2_resolve"))
        avf = _mapping(source_report.get("avf_v0_2_evaluation"))
        packet = _mapping(source_report.get("action_commit_packet_v0_2_integration"))
        corridor = _mapping(source_report.get("mock_bank_sandbox_v0_2_corridor_execution"))
        avf_decisions = avf.get("decision_reports_summary") if avf else None
        top_avf_rows = (
            tuple(
                row
                for row in avf_decisions
                if type(row) is dict and row.get("rank") == 1
            )
            if type(avf_decisions) is tuple
            else ()
        )
        if (
            drs is None
            or drs.get("drs_v0_2_status") != STATUS_PASS
            or drs.get("records_evaluated_count") != 11
            or drs.get("direct_reuse_allowed_count") != 0
            or drs.get("root_review_required_count") != 11
            or avf is None
            or avf.get("avf_v0_2_status") != STATUS_PASS
            or avf.get("candidates_evaluated_count") != 9
            or len(top_avf_rows) != 1
            or top_avf_rows[0].get("top_ranked_candidate_not_permission")
            is not True
            or any(
                type(row) is not dict
                or row.get("action_permission_claimed") is not False
                or row.get("final_output_claimed") is not False
                for row in avf_decisions or ()
            )
        ):
            errors.append("supplier_water_filter_source_business_outcome_mismatch")
        if (
            packet is None
            or packet.get("action_commit_packet_v0_2_status") != STATUS_PASS
            or packet.get("root_created") is not True
            or packet.get("packet_validated") is not True
            or packet.get("registry_validated") is not True
            or packet.get("packet_corridor_entry_validated") is not True
            or packet.get("accepted_for_mock_corridor") is not True
            or packet.get("terminal_receipt_recorded") is not False
            or packet.get("mock_payment_order_created") is not False
            or packet.get("mock_receipt_created") is not False
            or packet.get("mock_bank_sandbox_executed") is not False
            or packet.get("allowed_subjects") != _EXPECTED_PACKET_ALLOWED_SUBJECTS
            or packet.get("forbidden_subjects")
            != _EXPECTED_PACKET_FORBIDDEN_SUBJECTS
            or packet.get("allowed_actions") != _EXPECTED_PACKET_ALLOWED_ACTIONS
            or packet.get("forbidden_actions")
            != _EXPECTED_PACKET_FORBIDDEN_ACTIONS
            or packet.get("allowed_adapters") != _EXPECTED_PACKET_ALLOWED_ADAPTERS
            or packet.get("forbidden_adapters")
            != _EXPECTED_PACKET_FORBIDDEN_ADAPTERS
            or packet.get("payment_slot_ref") != _EXPECTED_PAYMENT_SLOT_REF
            or packet.get("creditor_ref") != _EXPECTED_CREDITOR_REF
            or packet.get("amount") != _EXPECTED_AMOUNT
            or packet.get("currency") != _EXPECTED_CURRENCY
        ):
            errors.append("supplier_water_filter_source_business_outcome_mismatch")
        if (
            corridor is None
            or corridor.get("mock_bank_sandbox_v0_2_status") != STATUS_PASS
            or corridor.get("source_packet_validated") is not True
            or corridor.get("source_packet_seen_in_registry") is not True
            or corridor.get("receipt_validated") is not True
            or corridor.get("terminal_receipt_observed_in_local_registry") is not True
            or corridor.get("receipt_evidence_only") is not True
            or corridor.get("receipt_permission_created") is not False
            or corridor.get("receipt_future_permission_created") is not False
            or corridor.get("receipt_final_output_created") is not False
            or corridor.get("receipt_authorizes_supplier_b") is not False
            or corridor.get("receipt_releases_shipment") is not False
            or corridor.get("receipt_mutates_packet_scope") is not False
            or corridor.get("receipt_creates_production_drs_record") is not False
            or corridor.get("supplier_b_excluded") is not True
            or corridor.get("shipment_release_excluded") is not True
            or corridor.get("real_bank_excluded") is not True
            or corridor.get("real_payment_executed") is not False
            or corridor.get("real_world_effects_count") != 0
        ):
            errors.append("supplier_water_filter_source_business_outcome_mismatch")

        counters = _mapping(source_report.get("counters"))
        if counters is None:
            errors.append("supplier_water_filter_source_report_invalid")
        else:
            if any(counters.get(name) != 0 for name in _ZERO_SOURCE_COUNTERS):
                errors.append("supplier_water_filter_effect_creation_forbidden")
            if any(counters.get(name) != 1 for name in _ONE_SOURCE_COUNTERS):
                errors.append("supplier_water_filter_source_business_outcome_mismatch")
            if (
                counters.get("transition_cards_created_count") != TRANSITION_CARD_COUNT
                or counters.get("fractal_branch_cells_created_count")
                != FRACTAL_BRANCH_COUNT
                or counters.get("branch_result_proposals_created_count")
                != RESULT_PROPOSAL_COUNT
                or counters.get("drs_v0_2_records_evaluated_count") != 11
                or counters.get("drs_v0_2_direct_reuse_allowed_count") != 0
                or counters.get("drs_v0_2_root_review_required_count") != 11
                or counters.get("avf_v0_2_candidates_evaluated_count") != 9
                or packet is None
                or packet.get("allowed_subjects")
                != _EXPECTED_PACKET_ALLOWED_SUBJECTS
                or packet.get("forbidden_subjects")
                != _EXPECTED_PACKET_FORBIDDEN_SUBJECTS
                or packet.get("allowed_actions")
                != _EXPECTED_PACKET_ALLOWED_ACTIONS
                or packet.get("forbidden_actions")
                != _EXPECTED_PACKET_FORBIDDEN_ACTIONS
                or packet.get("allowed_adapters")
                != _EXPECTED_PACKET_ALLOWED_ADAPTERS
                or packet.get("forbidden_adapters")
                != _EXPECTED_PACKET_FORBIDDEN_ADAPTERS
                or counters.get("action_commit_packet_v0_2_supplier_a_scope_allowed_count")
                != 1
                or counters.get("action_commit_packet_v0_2_supplier_b_scope_allowed_count")
                != 0
                or counters.get("action_commit_packet_v0_2_shipment_release_allowed_count")
                != 0
                or counters.get("action_commit_packet_v0_2_real_bank_allowed_count")
                != 0
                or counters.get("action_commit_packet_v0_2_real_supplier_api_allowed_count")
                != 0
                or counters.get("action_commit_packet_v0_2_real_warehouse_api_allowed_count")
                != 0
                or corridor is None
                or corridor.get("supplier_b_excluded") is not True
                or corridor.get("shipment_release_excluded") is not True
                or corridor.get("real_bank_excluded") is not True
                or counters.get("mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count")
                != 0
                or counters.get("mock_bank_sandbox_v0_2_receipt_shipment_release_count")
                != 0
                or counters.get("mock_bank_sandbox_v0_2_real_bank_api_called_count")
                != 0
            ):
                errors.append("supplier_water_filter_source_geometry_mismatch")
        try:
            source_report_hash = _source_report_hash(source_report)
        except Exception:
            errors.append("supplier_water_filter_source_report_invalid")
        else:
            if source_report_hash != _EXPECTED_SOURCE_REPORT_HASH:
                errors.append("supplier_water_filter_source_report_hash_mismatch")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("supplier_water_filter_source_report_invalid",)


def _source_card_plain(card: dict[str, object]) -> dict[str, object]:
    return {key: card[key] for key in (
        "step_id", "actor_or_module", "api_like_call", "input_summary",
        "output_summary", "meaning", "does_not_authorize", "next_step",
        "trace_id", "evidence_id",
    )}


def _source_card_hash(card: dict[str, object]) -> str:
    return _integrity.domain_separated_sha256_hex_v01(
        domain=_SOURCE_CARD_HASH_DOMAIN,
        payload=_integrity.canonical_json_bytes_v01(_source_card_plain(card)),
    )


def _artifact_id(index: int, step_id: str) -> str:
    return f"supplier_water_filter_artifact:{index + 1:02d}:{step_id}"


def _build_manifest_from_artifacts(
    kernel_artifacts: tuple[_abi.KernelArtifactV01, ...],
) -> _integrity.ArtifactManifestV01:
    canonical_refs = tuple(
        _abi.kernel_artifact_to_canonical_ref_v01(artifact)
        for artifact in kernel_artifacts
    )
    dependency_edges = tuple(
        _integrity.ArtifactDependencyEdgeV01(
            artifact.artifact_id, artifact.parent_refs[0]
        )
        for artifact in kernel_artifacts[1:]
    )
    return _integrity.build_artifact_manifest_v01(
        transaction_id=TRANSACTION_ID,
        profile=_integrity.build_default_seal_profile_v01(
            timeline_order_required=True
        ),
        artifacts=canonical_refs,
        dependency_edges=dependency_edges,
        root_ownership_bindings=tuple(
            _integrity.RootOwnershipBindingV01(
                artifact.artifact_id, artifact.owner_root_id
            )
            for artifact in kernel_artifacts
        ),
        evidence_class_bindings=tuple(
            _integrity.EvidenceClassBindingV01(
                artifact.artifact_id, artifact.authority_class
            )
            for artifact in kernel_artifacts
        ),
        authority_class_bindings=tuple(
            _integrity.AuthorityClassBindingV01(
                artifact.artifact_id, artifact.authority_class
            )
            for artifact in kernel_artifacts
        ),
    )


def _build_kernel_projection(source_report: dict[str, object]) -> tuple[
    tuple[_abi.KernelArtifactV01, ...],
    _integrity.ArtifactManifestV01,
    _integrity.SealVerificationResultV01,
    _integrity.SealVerificationResultV01,
    _integrity.ReplayVerificationResultV01,
    tuple[_abi.CausalConsumptionRefV01, ...],
]:
    cards = source_report["transition_cards"]
    artifacts: list[_abi.KernelArtifactV01] = []
    for index, (card, mapping) in enumerate(zip(cards, _STEP_MAPPING, strict=True)):
        step_id, artifact_type, authority_class, lifecycle_state = mapping
        if card["step_id"] != step_id:
            raise ValueError("supplier_water_filter_artifact_projection_invalid")
        artifact_id = _artifact_id(index, step_id)
        parent_refs = () if index == 0 else (artifacts[-1].artifact_id,)
        payload = {
            "source_index": index,
            **_source_card_plain(card),
            "source_card_hash": _source_card_hash(card),
        }
        artifacts.append(
            _abi.build_kernel_artifact_v01(
                abi_version="v1.0",
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                schema_version="v1",
                transaction_id=TRANSACTION_ID,
                owner_root_id=OWNER_ROOT_ID,
                source_component=f"{MODULE_ID}:{step_id}",
                authority_class=authority_class,
                lifecycle_state=lifecycle_state,
                payload=payload,
                trace_refs=(
                    f"source_run:{SOURCE_RUN_ID}",
                    f"source_report:{SOURCE_REPORT_ID}",
                    f"source_evidence:{card['evidence_id']}",
                ),
                parent_refs=parent_refs,
                time_envelope=_KERNEL_TIME_ENVELOPE,
            )
        )
    kernel_artifacts = tuple(artifacts)
    if _abi.validate_kernel_artifact_bundle_v01(artifacts=kernel_artifacts):
        raise ValueError("supplier_water_filter_artifact_projection_invalid")
    manifest = _build_manifest_from_artifacts(kernel_artifacts)
    payload_rows = tuple(
        (
            artifact.artifact_id,
            _abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"],
        )
        for artifact in kernel_artifacts
    )
    unanchored = _integrity.verify_artifact_manifest_v01(
        manifest=manifest, payload_rows=payload_rows
    )
    anchored = _integrity.verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    replay = _integrity.verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    causal_refs = tuple(
        _abi.build_causal_consumption_ref_v01(
            producer_actor_id=source.source_component,
            source_artifact_id=source.artifact_id,
            output_field=_CAUSAL_OUTPUT_FIELD,
            consumer_component=downstream.source_component,
            downstream_artifact_id=downstream.artifact_id,
            decision_effect=_CAUSAL_EFFECT,
            disposition="USED",
            reason_code=_CAUSAL_REASON,
            trace_refs=(SOURCE_REPORT_ID, source.artifact_id, downstream.artifact_id),
        )
        for source, downstream in zip(kernel_artifacts, kernel_artifacts[1:])
    )
    if _abi.validate_causal_consumption_bundle_v01(
        artifacts=kernel_artifacts, causal_refs=causal_refs
    ):
        raise ValueError("supplier_water_filter_causal_projection_invalid")
    return kernel_artifacts, manifest, unanchored, anchored, replay, causal_refs


def _build_multiroot(
    artifacts: tuple[_abi.KernelArtifactV01, ...],
) -> tuple[
    _multiroot.TransactionOutcomeEnvelopeV01,
    _multiroot.MultiRootValidationResultV01,
]:
    by_step = {
        artifact.source_component.removeprefix(f"{MODULE_ID}:"): artifact.artifact_id
        for artifact in artifacts
    }
    decision = _multiroot.build_root_decision_envelope_v01(
        transaction_id=TRANSACTION_ID,
        root_id=OWNER_ROOT_ID,
        root_decision_id="supplier_water_filter_root_decision:scoped_review_held",
        source_decision_ref="root_second_supplier_a_scoped_review",
        outcome_class="HELD",
        reason_code=(
            "held:supplier_a_scoped_review_ready_supplier_b_blocked_shipment_held"
        ),
        selected_subject_id=None,
        evidence_refs=tuple(
            by_step[step_id]
            for step_id in (
                "root_first_not_ready",
                "root_second_supplier_a_scoped_review",
                "root_created_mock_action_commit_packet_observed",
                "mock_bank_sandbox_receipt_observed",
                "final_state_summary",
            )
        ),
        cross_root_input_refs=(),
    )
    outcome = _multiroot.build_transaction_outcome_envelope_v01(
        transaction_id=TRANSACTION_ID,
        expected_root_ids=(OWNER_ROOT_ID,),
        root_decisions=(decision,),
        cross_root_evidence_refs=(),
    )
    validation = _multiroot.validate_multiroot_v01(outcome)
    if (
        outcome.outcome_status != _multiroot.STATUS_MIXED
        or outcome.mixed_outcomes_visible is not True
        or outcome.accepted_root_ids != ()
        or outcome.non_accepted_root_ids != (OWNER_ROOT_ID,)
        or validation.final_status != _multiroot.STATUS_MIXED
        or validation.errors
    ):
        raise ValueError("supplier_water_filter_multiroot_invalid")
    return outcome, validation


def _result_plain(
    result: SupplierWaterFilterKernelAdapterResultV01,
) -> dict[str, object]:
    return {
        "adapter_id": result.adapter_id,
        "adapter_version": result.adapter_version,
        "source_run_id": result.source_run_id,
        "source_report_id": result.source_report_id,
        "source_trace_type": result.source_trace_type,
        "transaction_id": result.transaction_id,
        "owner_root_id": result.owner_root_id,
        "supplier_a_status": result.supplier_a_status,
        "supplier_b_status": result.supplier_b_status,
        "shipment_status": result.shipment_status,
        "receipt_status": result.receipt_status,
        "kernel_artifacts": _abi.kernel_artifacts_to_plain_list_v01(
            result.kernel_artifacts
        ),
        "kernel_manifest": _integrity.artifact_manifest_to_plain_dict_v01(
            result.kernel_manifest
        ),
        "kernel_unanchored_verification": (
            _integrity.seal_verification_result_to_plain_dict_v01(
                result.kernel_unanchored_verification
            )
        ),
        "kernel_anchored_verification": (
            _integrity.seal_verification_result_to_plain_dict_v01(
                result.kernel_anchored_verification
            )
        ),
        "kernel_replay": _integrity.replay_verification_result_to_plain_dict_v01(
            result.kernel_replay
        ),
        "causal_consumption_refs": _abi.causal_consumption_refs_to_plain_list_v01(
            result.causal_consumption_refs
        ),
        "multiroot_outcome": _multiroot.transaction_outcome_envelope_to_plain_dict_v01(
            result.multiroot_outcome
        ),
        "multiroot_validation": _multiroot.multiroot_validation_result_to_plain_dict_v01(
            result.multiroot_validation
        ),
        "business_module_count": result.business_module_count,
        "transition_card_count": result.transition_card_count,
        "dependency_edge_count": result.dependency_edge_count,
        "fractal_branch_count": result.fractal_branch_count,
        "result_proposal_count": result.result_proposal_count,
        "provider_call_count": result.provider_call_count,
        "network_call_count": result.network_call_count,
        "gemini_call_count": result.gemini_call_count,
        "real_world_effects_count": result.real_world_effects_count,
    }


def _adapter_id(result: SupplierWaterFilterKernelAdapterResultV01) -> str:
    material = _result_plain(result)
    material.pop("adapter_id")
    return _integrity.domain_separated_sha256_hex_v01(
        domain=_ADAPTER_ID_DOMAIN,
        payload=_integrity.canonical_json_bytes_v01(material),
    )


def _result_structure_errors(result: object) -> tuple[str, ...]:
    if type(result) is not SupplierWaterFilterKernelAdapterResultV01:
        return ("supplier_water_filter_kernel_adapter_invalid",)
    try:
        errors: list[str] = []
        if (
            result.adapter_version != ADAPTER_VERSION
            or result.source_run_id != SOURCE_RUN_ID
            or result.source_report_id != SOURCE_REPORT_ID
            or result.source_trace_type != SOURCE_TRACE_TYPE
            or result.transaction_id != TRANSACTION_ID
            or result.owner_root_id != OWNER_ROOT_ID
            or result.supplier_a_status != SUPPLIER_A_STATUS
            or result.supplier_b_status != SUPPLIER_B_STATUS
            or result.shipment_status != SHIPMENT_STATUS
            or result.receipt_status != RECEIPT_STATUS
        ):
            errors.append("supplier_water_filter_kernel_adapter_invalid")
        artifacts_valid = (
            type(result.kernel_artifacts) is tuple
            and len(result.kernel_artifacts) == TRANSITION_CARD_COUNT
            and not _abi.validate_kernel_artifact_bundle_v01(
                artifacts=result.kernel_artifacts
            )
        )
        if artifacts_valid:
            for index, (artifact, mapping) in enumerate(
                zip(result.kernel_artifacts, _STEP_MAPPING, strict=True)
            ):
                plain = _abi.kernel_artifact_to_plain_dict_v01(artifact)
                payload = plain["payload"]
                expected_parent = () if index == 0 else (
                    result.kernel_artifacts[index - 1].artifact_id,
                )
                source_card = {
                    key: payload[key]
                    for key in (
                        "step_id",
                        "actor_or_module",
                        "api_like_call",
                        "input_summary",
                        "output_summary",
                        "meaning",
                        "does_not_authorize",
                        "next_step",
                        "trace_id",
                        "evidence_id",
                    )
                }
                recomputed_source_hash = _source_card_hash(source_card)
                expected_trace_refs = (
                    f"source_run:{SOURCE_RUN_ID}",
                    f"source_report:{SOURCE_REPORT_ID}",
                    f"source_evidence:{payload['evidence_id']}",
                )
                if (
                    artifact.artifact_id != _artifact_id(index, mapping[0])
                    or artifact.abi_version != "v1.0"
                    or artifact.schema_version != "v1"
                    or artifact.transaction_id != TRANSACTION_ID
                    or artifact.owner_root_id != OWNER_ROOT_ID
                    or artifact.source_component != f"{MODULE_ID}:{mapping[0]}"
                    or artifact.artifact_type != mapping[1]
                    or artifact.authority_class != mapping[2]
                    or artifact.lifecycle_state != mapping[3]
                    or artifact.parent_refs != expected_parent
                    or artifact.trace_refs != expected_trace_refs
                    or plain["time_envelope"] != _KERNEL_TIME_ENVELOPE
                    or frozenset(payload) != _PAYLOAD_KEYS
                    or type(payload["source_index"]) is not int
                    or payload["source_index"] != index
                    or payload["step_id"] != mapping[0]
                    or payload["evidence_id"] != _EXPECTED_EVIDENCE_IDS[index]
                    or payload["source_card_hash"] != recomputed_source_hash
                    or recomputed_source_hash != _EXPECTED_SOURCE_CARD_HASHES[index]
                ):
                    artifacts_valid = False
                    break
        if not artifacts_valid:
            errors.append("supplier_water_filter_artifact_projection_invalid")

        manifest = result.kernel_manifest
        if (
            type(manifest) is not _integrity.ArtifactManifestV01
            or manifest.artifact_count != TRANSITION_CARD_COUNT
            or manifest.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or manifest.root_ownership_binding_count != TRANSITION_CARD_COUNT
            or manifest.evidence_class_binding_count != TRANSITION_CARD_COUNT
            or manifest.authority_class_binding_count != TRANSITION_CARD_COUNT
        ):
            errors.append("supplier_water_filter_manifest_invalid")
        if artifacts_valid and type(manifest) is _integrity.ArtifactManifestV01:
            try:
                expected_manifest = _build_manifest_from_artifacts(
                    result.kernel_artifacts
                )
                if _integrity.canonical_json_bytes_v01(
                    _integrity.artifact_manifest_to_plain_dict_v01(manifest)
                ) != _integrity.canonical_json_bytes_v01(
                    _integrity.artifact_manifest_to_plain_dict_v01(expected_manifest)
                ):
                    errors.append("supplier_water_filter_manifest_invalid")
            except Exception:
                errors.append("supplier_water_filter_manifest_invalid")
        if (
            type(result.kernel_unanchored_verification)
            is not _integrity.SealVerificationResultV01
            or type(result.kernel_anchored_verification)
            is not _integrity.SealVerificationResultV01
            or type(result.kernel_replay) is not _integrity.ReplayVerificationResultV01
            or result.kernel_unanchored_verification.verification_status
            != _integrity.STATUS_SELF_CONSISTENT_UNANCHORED
            or result.kernel_anchored_verification.verification_status != STATUS_PASS
            or result.kernel_replay.replay_status != STATUS_PASS
            or result.kernel_replay.artifact_count != TRANSITION_CARD_COUNT
            or result.kernel_replay.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or any(
                getattr(result.kernel_replay, name) != 0
                for name in _GENERIC_ZERO_COUNTER_FIELDS
            )
        ):
            errors.append("supplier_water_filter_replay_invalid")
        if artifacts_valid and type(manifest) is _integrity.ArtifactManifestV01:
            payload_rows = tuple(
                (
                    artifact.artifact_id,
                    _abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"],
                )
                for artifact in result.kernel_artifacts
            )
            expected_unanchored = _integrity.verify_artifact_manifest_v01(
                manifest=manifest, payload_rows=payload_rows
            )
            expected_anchored = _integrity.verify_artifact_manifest_v01(
                manifest=manifest,
                payload_rows=payload_rows,
                expected_manifest_hash=manifest.manifest_hash,
            )
            expected_replay = _integrity.verify_artifact_replay_v01(
                manifest=manifest,
                payload_rows=payload_rows,
                expected_manifest_hash=manifest.manifest_hash,
            )
            for supplied, expected, project in (
                (result.kernel_unanchored_verification, expected_unanchored, _integrity.seal_verification_result_to_plain_dict_v01),
                (result.kernel_anchored_verification, expected_anchored, _integrity.seal_verification_result_to_plain_dict_v01),
                (result.kernel_replay, expected_replay, _integrity.replay_verification_result_to_plain_dict_v01),
            ):
                if _integrity.canonical_json_bytes_v01(project(supplied)) != _integrity.canonical_json_bytes_v01(project(expected)):
                    errors.append("supplier_water_filter_replay_invalid")
                    break

        causal_valid = (
            artifacts_valid
            and type(result.causal_consumption_refs) is tuple
            and len(result.causal_consumption_refs) == DEPENDENCY_EDGE_COUNT
            and not _abi.validate_causal_consumption_bundle_v01(
                artifacts=result.kernel_artifacts,
                causal_refs=result.causal_consumption_refs,
            )
        )
        if causal_valid:
            expected_pairs = tuple(
                (source.artifact_id, downstream.artifact_id)
                for source, downstream in zip(
                    result.kernel_artifacts, result.kernel_artifacts[1:]
                )
            )
            actual_pairs = tuple(
                (ref.source_artifact_id, ref.downstream_artifact_id)
                for ref in result.causal_consumption_refs
            )
            causal_valid = actual_pairs == expected_pairs and all(
                ref.producer_actor_id == source.source_component
                and ref.consumer_component == downstream.source_component
                and ref.output_field == _CAUSAL_OUTPUT_FIELD
                and ref.decision_effect == _CAUSAL_EFFECT
                and ref.disposition == "USED"
                and ref.reason_code == _CAUSAL_REASON
                and ref.trace_refs
                == (SOURCE_REPORT_ID, source.artifact_id, downstream.artifact_id)
                for ref, source, downstream in zip(
                    result.causal_consumption_refs,
                    result.kernel_artifacts[:-1],
                    result.kernel_artifacts[1:],
                    strict=True,
                )
            )
        if not causal_valid:
            errors.append("supplier_water_filter_causal_projection_invalid")

        multiroot_valid = artifacts_valid
        if multiroot_valid:
            try:
                expected_outcome, expected_validation = _build_multiroot(
                    result.kernel_artifacts
                )
                supplied_outcome_plain = (
                    _multiroot.transaction_outcome_envelope_to_plain_dict_v01(
                        result.multiroot_outcome
                    )
                )
                expected_outcome_plain = (
                    _multiroot.transaction_outcome_envelope_to_plain_dict_v01(
                        expected_outcome
                    )
                )
                supplied_validation_plain = (
                    _multiroot.multiroot_validation_result_to_plain_dict_v01(
                        result.multiroot_validation
                    )
                )
                expected_validation_plain = (
                    _multiroot.multiroot_validation_result_to_plain_dict_v01(
                        expected_validation
                    )
                )
                multiroot_valid = (
                    _integrity.canonical_json_bytes_v01(supplied_outcome_plain)
                    == _integrity.canonical_json_bytes_v01(expected_outcome_plain)
                    and _integrity.canonical_json_bytes_v01(
                        supplied_validation_plain
                    )
                    == _integrity.canonical_json_bytes_v01(
                        expected_validation_plain
                    )
                )
            except Exception:
                multiroot_valid = False
        if not multiroot_valid:
            errors.append("supplier_water_filter_multiroot_invalid")

        geometry = (
            result.business_module_count,
            result.transition_card_count,
            result.dependency_edge_count,
            result.fractal_branch_count,
            result.result_proposal_count,
        )
        if any(type(value) is not int for value in geometry) or geometry != (
            BUSINESS_MODULE_COUNT,
            TRANSITION_CARD_COUNT,
            DEPENDENCY_EDGE_COUNT,
            FRACTAL_BRANCH_COUNT,
            RESULT_PROPOSAL_COUNT,
        ):
            errors.append("supplier_water_filter_source_geometry_mismatch")
        if any(
            type(value) is not int or value != 0
            for value in (
                result.provider_call_count,
                result.network_call_count,
                result.gemini_call_count,
            )
        ):
            errors.append("supplier_water_filter_authority_law_change_forbidden")
        if type(result.real_world_effects_count) is not int or result.real_world_effects_count != 0:
            errors.append("supplier_water_filter_effect_creation_forbidden")
        try:
            expected_id = _adapter_id(result)
        except Exception:
            expected_id = None
        if expected_id is not None and result.adapter_id != expected_id:
            errors.append("supplier_water_filter_adapter_id_mismatch")
        try:
            _integrity.canonical_json_bytes_v01(_result_plain(result))
        except Exception:
            if not errors:
                errors.append("supplier_water_filter_kernel_adapter_invalid")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("supplier_water_filter_kernel_adapter_invalid",)


def _build_exact_result(
    source_report: dict[str, object],
) -> SupplierWaterFilterKernelAdapterResultV01:
    source_errors = _source_report_errors(source_report)
    if source_errors:
        raise ValueError(source_errors[0])
    artifacts, manifest, unanchored, anchored, replay, causal_refs = (
        _build_kernel_projection(source_report)
    )
    outcome, validation = _build_multiroot(artifacts)
    if (
        unanchored.verification_status
        != _integrity.STATUS_SELF_CONSISTENT_UNANCHORED
        or anchored.verification_status != STATUS_PASS
        or replay.replay_status != STATUS_PASS
        or len(artifacts) != TRANSITION_CARD_COUNT
        or manifest.dependency_edge_count != DEPENDENCY_EDGE_COUNT
        or len(causal_refs) != DEPENDENCY_EDGE_COUNT
    ):
        raise ValueError("supplier_water_filter_replay_invalid")
    result = SupplierWaterFilterKernelAdapterResultV01(
        adapter_id="",
        adapter_version=ADAPTER_VERSION,
        source_run_id=SOURCE_RUN_ID,
        source_report_id=SOURCE_REPORT_ID,
        source_trace_type=SOURCE_TRACE_TYPE,
        transaction_id=TRANSACTION_ID,
        owner_root_id=OWNER_ROOT_ID,
        supplier_a_status=SUPPLIER_A_STATUS,
        supplier_b_status=SUPPLIER_B_STATUS,
        shipment_status=SHIPMENT_STATUS,
        receipt_status=RECEIPT_STATUS,
        kernel_artifacts=artifacts,
        kernel_manifest=manifest,
        kernel_unanchored_verification=unanchored,
        kernel_anchored_verification=anchored,
        kernel_replay=replay,
        causal_consumption_refs=causal_refs,
        multiroot_outcome=outcome,
        multiroot_validation=validation,
        business_module_count=BUSINESS_MODULE_COUNT,
        transition_card_count=TRANSITION_CARD_COUNT,
        dependency_edge_count=DEPENDENCY_EDGE_COUNT,
        fractal_branch_count=FRACTAL_BRANCH_COUNT,
        result_proposal_count=RESULT_PROPOSAL_COUNT,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
    )
    return _replace(result, adapter_id=_adapter_id(result))


def build_supplier_water_filter_kernel_adapter_result_v01(
    *,
    source_report: _Mapping[str, object],
) -> SupplierWaterFilterKernelAdapterResultV01:
    try:
        if type(source_report) is not dict:
            raise ValueError("supplier_water_filter_source_report_invalid")
        result = _build_exact_result(source_report)
        if _result_structure_errors(result):
            raise ValueError("supplier_water_filter_kernel_adapter_invalid")
        return result
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 and type(exc.args[0]) is str else ""
        allowed = {
            "supplier_water_filter_kernel_adapter_invalid",
            "supplier_water_filter_source_report_invalid",
            "supplier_water_filter_source_identity_mismatch",
            "supplier_water_filter_source_business_outcome_mismatch",
            "supplier_water_filter_source_geometry_mismatch",
            "supplier_water_filter_source_report_hash_mismatch",
            "supplier_water_filter_artifact_projection_invalid",
            "supplier_water_filter_manifest_invalid",
            "supplier_water_filter_replay_invalid",
            "supplier_water_filter_causal_projection_invalid",
            "supplier_water_filter_multiroot_invalid",
            "supplier_water_filter_authority_law_change_forbidden",
            "supplier_water_filter_effect_creation_forbidden",
        }
        raise ValueError(reason if reason in allowed else "supplier_water_filter_kernel_adapter_invalid") from None
    except Exception:
        raise ValueError("supplier_water_filter_unexpected_exception") from None


def validate_supplier_water_filter_kernel_adapter_result_v01(
    *,
    source_report: object,
    result: object,
) -> tuple[str, ...]:
    try:
        source_errors = _source_report_errors(source_report)
        if source_errors:
            return source_errors
        structure_errors = _result_structure_errors(result)
        if type(result) is not SupplierWaterFilterKernelAdapterResultV01:
            return structure_errors
        expected = _build_exact_result(source_report)
        errors = list(structure_errors)
        try:
            projections_differ = _integrity.canonical_json_bytes_v01(
                _result_plain(result)
            ) != _integrity.canonical_json_bytes_v01(_result_plain(expected))
        except Exception:
            projections_differ = True
        if projections_differ:
            errors.append("supplier_water_filter_kernel_adapter_invalid")
            if result.adapter_id != expected.adapter_id:
                errors.append("supplier_water_filter_adapter_id_mismatch")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("supplier_water_filter_unexpected_exception",)


def supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(
    result: SupplierWaterFilterKernelAdapterResultV01,
) -> dict[str, object]:
    try:
        if _result_structure_errors(result):
            raise ValueError("supplier_water_filter_kernel_adapter_invalid")
        projection = _result_plain(result)
        _integrity.canonical_json_bytes_v01(projection)
        return projection
    except Exception:
        raise ValueError("supplier_water_filter_kernel_adapter_invalid") from None
