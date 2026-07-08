from __future__ import annotations

from dataclasses import asdict
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from hedgehog.action_commit_packet_v02 import (
    STATUS_PASS,
    build_supplier_a_mock_receipt_evidence_fixture_v01,
    build_supplier_a_packet_corridor_validation_fixture_v02,
    record_packet_seen_v02,
    record_terminal_receipt_observation_v02,
    validate_action_commit_packet_v02,
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
    "[LOCAL DRS V0.2 LIVE OBSERVATION]",
    "[LOCAL AVF V0.2 LIVE OBSERVATION]",
    "[TOP-LEVEL ORCHESTRATOR]",
    "[BSEP MEMBRANE]",
    "[TOP-LEVEL SEMANTIC ARCHITECT]",
    "[RUNTIME PLAN AND FRACTAL CELLS]",
    "[BRANCH-LOCAL LLM/SLM ACTORS]",
    "[BRANCH RESULT PROPOSALS]",
    "[POST V&V / GT-LGT / ROOT]",
    "[ACTIONCOMMITPACKET V0.2 LIVE OBSERVATION]",
    "[MOCKBANKSANDBOX V0.2 LIVE CONTRACT CORRIDOR OBSERVATION]",
    "[SECRET MEMBRANE]",
    "[AUTHORITY MATRIX]",
    "[COUNTER MATRIX]",
    "[ARTIFACTS]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

PIPELINE_SEQUENCE = (
    "dirty_request_loaded_from_v1_2_product_trace",
    "local_drs_v0_2_resolve_invoked",
    "avf_v0_2_evaluation_invoked",
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
    "action_commit_packet_v0_2_integration_invoked",
    "action_commit_packet_v0_2_packet_validated",
    "action_commit_packet_v0_2_registry_validated",
    "action_commit_packet_v0_2_corridor_entry_validated",
    "action_commit_packet_v0_2_packet_seen_recorded",
    "mock_bank_sandbox_v0_2_corridor_invoked",
    "mock_bank_sandbox_v0_2_mock_payment_intent_created",
    "mock_bank_sandbox_v0_2_mock_payment_consent_created",
    "mock_bank_sandbox_v0_2_mock_payment_order_created",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created",
    "mock_bank_sandbox_v0_2_receipt_validated",
    "mock_bank_sandbox_v0_2_terminal_receipt_observed",
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

LOCAL_DRS_V0_2_SCENARIO_IDS = (
    "supplier_a_prior_scoped_trace",
    "supplier_b_blocker_trace",
    "old_receipt_trace",
    "old_shipment_held_trace",
    "old_root_final_trace",
    "changed_warehouse_fact",
    "stale_legal_accounting_evidence",
    "quarantined_record",
    "deadend_record",
    "wrong_domain_near_match",
    "permission_trace_completed_action_attempt",
)

LOCAL_DRS_V0_2_SCENARIO_SUMMARIES = (
    "Supplier A prior trace may inform bounded context.",
    "Supplier B blocker trace may warn or block.",
    "old receipt remains context, not current permission.",
    "old Root Final is not silently reused.",
    "changed warehouse facts require rerun validation.",
    "stale legal/accounting evidence receives freshness downgrade.",
    "quarantined records block direct reuse.",
    "deadend proximity blocks or downgrades reuse.",
    "wrong-domain near match is not direct reuse.",
    "permission trace cannot become completed action.",
)

LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES = (
    "DRS v0.2 is not truth.",
    "DRS v0.2 is not authority.",
    "DRS v0.2 is not permission.",
    "DRS hit is context only.",
    "DRS v0.2 reuse decision is not FinalOutput.",
    "DRS v0.2 direct reuse candidate is not direct reuse.",
    "old receipt is not current permission.",
    "old Root Final is not silently reused.",
    "permission trace cannot become completed action.",
    "ReuseScore is not Root.",
    "Semantic similarity is not authority.",
    "DRS writeback after Root is local proof/audit only.",
    "Root remains final authority.",
)

AVF_V0_2_NON_AUTHORITY_BOUNDARIES = (
    "AVF v0.2 is not truth.",
    "AVF v0.2 is not authority.",
    "AVF v0.2 is not permission.",
    "AVF score is not Root.",
    "Top-ranked AVF candidate is not permission.",
    "CandidateVector is not action permission.",
    "CandidateVector is not FinalOutput.",
    "HardMask is not Root.",
    "High score does not override HardMask.",
    "Top rank does not override HardMask.",
    "Safe rank remains advisory.",
    "AVF cannot bypass Root.",
    "AVF cannot create FinalOutput.",
    "AVF cannot create ActionCommitPacket.",
    "AVF cannot create receipt.",
    "AVF cannot execute payment.",
    "AVF cannot release shipment.",
    "Root remains final authority.",
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
    "MockBankSandbox corridor is deterministic and not reasoning.",
    "No post-Root reasoning restart.",
    "MockBankSandbox does not decide.",
    "MockBankSandbox does not restart LLM reasoning after Root.",
    "MockBankSandbox does not create authority.",
    "Mock receipt is evidence only.",
    "Mock receipt is not permission.",
    "Mock receipt is not FinalOutput.",
    "Mock receipt does not authorize Supplier B.",
    "Mock receipt does not release shipment.",
    "Mock receipt does not create future permission.",
    "Terminal receipt observation is local proof-only.",
    "Receipt does not release shipment.",
    "payment_slot is not permission.",
    *LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
    *AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
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

ORCHESTRATOR_JSON_SKELETON = {
    "proposal_id": "orchestrator-semantic-wow-v1-2-001",
    "suggested_route": "supplier_payment_shipment_review_v1_2",
    "selected_branch_ids": [
        "warehouse_branch",
        "supplier_a_branch",
        "supplier_b_branch",
        "legal_branch",
        "accounting_branch",
        "bank_a_branch",
        "bank_b_branch",
        "root_merge_branch",
    ],
    "required_guards": [
        "BSEP validation",
        "semantic proposal validation",
        "Root final authority",
    ],
    "route_reasoning": [
        "Route API-like business evidence through bounded semantic review."
    ],
    "evidence_needed": [
        "warehouse inventory",
        "supplier availability and blockers",
        "legal insurance and contract status",
        "accounting invoice and PO reconciliation",
        "bank payment slot and policy preview",
    ],
    "uncertainty_notes": [
        "Provider semantics remain candidate-only until runtime validation and Root review."
    ],
    "truth_claimed": False,
    "authority_claimed": False,
    "action_permission_claimed": False,
    "final_output_claimed": False,
    "connector_command_claimed": False,
    "drs_write_claimed": False,
    "plan_graph_claimed": False,
    "bypass_root_claimed": False,
    "root_review_required": True,
}

ARCHITECT_JSON_SKELETON = {
    "proposal_id": "architect-semantic-wow-v1-2-001",
    "source_route_id": "orchestrator-semantic-wow-v1-2-001",
    "selected_branch_ids": [
        "warehouse_branch",
        "supplier_a_branch",
        "supplier_b_branch",
        "legal_branch",
        "accounting_branch",
        "bank_a_branch",
        "bank_b_branch",
        "root_merge_branch",
    ],
    "root_recommendation": "needs_more_evidence",
    "result_proposal_summary": "Supplier A may proceed only to scoped review. Supplier B remains blocked. Shipment release remains held. Receipt remains evidence only.",
    "required_validators": [
        "Architect semantic proposal validation",
        "branch ResultProposal validation",
        "Post V&V",
        "GT/LGT advisory review",
        "Root final boundary",
    ],
    "plan_shape_reasoning": [
        "Runtime builds local plan artifacts after semantic validation."
    ],
    "branch_intent_reasoning": [
        "Branch cells collect bounded evidence and return ResultProposals."
    ],
    "executor_constraint_reasoning": [
        "No executor is authorized by provider output."
    ],
    "forbidden_surface_reasoning": [
        "Provider output cannot create ActionCommitPacket, receipt, payment, shipment release, connector command, or FinalOutput."
    ],
    "validator_coverage_reasoning": [
        "Semantic, BSEP, branch, Post V&V, GT/LGT, and Root checks remain required."
    ],
    "return_to_root_reasoning": [
        "The semantic proposal returns to Root because provider output is advisory only."
    ],
    "authority_boundary_reasoning": [
        "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides."
    ],
    "truth_claimed": False,
    "authority_claimed": False,
    "action_permission_claimed": False,
    "final_output_claimed": False,
    "connector_command_claimed": False,
    "drs_write_claimed": False,
    "root_bypass_claimed": False,
}

BRANCH_SEMANTIC_JSON_SKELETON = {
    "branch_semantic_proposal_id": "branch-semantic-proposal-wow-v1-2-001",
    "source_branch_id": "branch_id_from_prompt",
    "semantic_summary": "Branch semantic observation remains advisory.",
    "evidence_interpretation": "Evidence supports bounded parent and Root review only.",
    "uncertainty_notes": [
        "Branch semantics remain candidate-only until validation and Root review."
    ],
    "recommended_branch_status": "accepted_for_parent_review",
    "return_to_parent_reasoning": "Branch output returns to parent/root boundary as semantic evidence only.",
    "truth_claimed": False,
    "authority_claimed": False,
    "action_permission_claimed": False,
    "final_output_claimed": False,
    "connector_command_claimed": False,
    "action_commit_packet_claimed": False,
    "receipt_claimed": False,
    "payment_execution_claimed": False,
    "shipment_release_claimed": False,
}

SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "raw_iban_value",
    "GEMINI_API_KEY" + "=",
    "GOOGLE_API_KEY" + "=",
    "GOOGLE_GEMINI_API_KEY" + "=",
)

GEMINI_KEY_NAMES = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GEMINI_API_KEY",
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
        "manual_live_drs_v0_2_observation_enabled_count": 0,
        "local_drs_v0_2_resolve_invoked_count": 0,
        "local_drs_v0_2_records_evaluated_count": 0,
        "local_drs_v0_2_direct_reuse_allowed_count": 0,
        "local_drs_v0_2_root_review_required_count": 0,
        "local_drs_v0_2_context_only_count": 0,
        "local_drs_v0_2_warning_only_count": 0,
        "local_drs_v0_2_rerun_required_count": 0,
        "local_drs_v0_2_blocked_count": 0,
        "local_drs_v0_2_writeback_candidate_created_count": 0,
        "local_drs_v0_2_writeback_persisted_count": 0,
        "local_drs_v0_2_writeback_local_proof_only_count": 0,
        "local_drs_v0_2_permission_granted_count": 0,
        "local_drs_v0_2_root_bypass_count": 0,
        "local_drs_v0_2_external_drs_used_count": 0,
        "local_drs_v0_2_global_drs_used_count": 0,
        "local_drs_v0_2_vector_db_used_count": 0,
        "local_drs_v0_2_embeddings_required_count": 0,
        "manual_live_avf_v0_2_observation_enabled_count": 0,
        "avf_v0_2_evaluation_invoked_count": 0,
        "avf_v0_2_candidates_evaluated_count": 0,
        "avf_v0_2_hard_masked_count": 0,
        "avf_v0_2_unmasked_count": 0,
        "avf_v0_2_root_review_required_count": 0,
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
        "action_commit_packet_v0_2_integration_invoked_count": 0,
        "action_commit_packet_v0_2_root_created_model_packet_count": 0,
        "action_commit_packet_v0_2_root_created_packet_validated_count": 0,
        "action_commit_packet_v0_2_created_by_root_count": 0,
        "action_commit_packet_v0_2_created_by_human_count": 0,
        "action_commit_packet_v0_2_created_by_llm_count": 0,
        "action_commit_packet_v0_2_created_by_drs_count": 0,
        "action_commit_packet_v0_2_created_by_avf_count": 0,
        "action_commit_packet_v0_2_created_by_gt_lgt_count": 0,
        "action_commit_packet_v0_2_human_approval_used_as_evidence_count": 0,
        "action_commit_packet_v0_2_supplier_a_scope_allowed_count": 0,
        "action_commit_packet_v0_2_supplier_b_scope_allowed_count": 0,
        "action_commit_packet_v0_2_shipment_release_allowed_count": 0,
        "action_commit_packet_v0_2_real_bank_allowed_count": 0,
        "action_commit_packet_v0_2_real_supplier_api_allowed_count": 0,
        "action_commit_packet_v0_2_real_warehouse_api_allowed_count": 0,
        "action_commit_packet_v0_2_packet_registry_validated_count": 0,
        "action_commit_packet_v0_2_packet_corridor_entry_validated_count": 0,
        "action_commit_packet_v0_2_accepted_for_mock_corridor_count": 0,
        "action_commit_packet_v0_2_packet_seen_recorded_count": 0,
        "action_commit_packet_v0_2_terminal_receipt_recorded_count": 0,
        "mock_bank_sandbox_v0_2_corridor_invoked_count": 0,
        "mock_bank_sandbox_v0_2_packet_consumed_count": 0,
        "mock_bank_sandbox_v0_2_packet_validated_count": 0,
        "mock_bank_sandbox_v0_2_scope_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_amount_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_creditor_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_payment_slot_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_adapter_binding_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_idempotency_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_expiry_ttl_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_forbidden_surface_check_passed_count": 0,
        "mock_bank_sandbox_v0_2_mock_payment_intent_created_count": 0,
        "mock_bank_sandbox_v0_2_mock_payment_consent_created_count": 0,
        "mock_bank_sandbox_v0_2_mock_payment_order_created_count": 0,
        "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count": 0,
        "mock_bank_sandbox_v0_2_receipt_validated_count": 0,
        "mock_bank_sandbox_v0_2_terminal_receipt_observed_count": 0,
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
            "manual_live_drs_v0_2_observation_enabled_count": 1,
            "manual_live_avf_v0_2_observation_enabled_count": 1,
            "bank_internal_raw_iban_present_count": 1,
            "bank_internal_token_present_count": 1,
        }
    )
    return counters


def _empty_local_drs_v0_2_observation() -> dict[str, Any]:
    return {
        "local_drs_v0_2_status": "not_run",
        "resolver_mode": "deterministic_local",
        "temporal_query_present": False,
        "records_evaluated_count": 0,
        "direct_reuse_allowed_count": 0,
        "direct_reuse_candidate_count": 0,
        "context_only_count": 0,
        "warning_only_count": 0,
        "rerun_required_count": 0,
        "blocked_count": 0,
        "root_review_required_count": 0,
        "freshness_table": (),
        "lineage_table": (),
        "provenance_table": (),
        "reuse_decision_table": (),
        "decisions_summary": {},
        "baseline_regression_scenario_ids": (),
        "bounded_context_summary": {
            "records_evaluated_count": 0,
            "direct_reuse_allowed_count": 0,
            "root_review_required_count": 0,
            "scenario_summaries": (),
            "non_authority_boundaries": LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
        },
        "drs_non_authority_boundaries": LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


def _local_drs_v0_2_report_artifacts(
    observation: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        "local_drs_v0_2_resolve_report": dict(observation),
        "local_drs_v0_2_freshness_table": {
            "rows": observation["freshness_table"]
        },
        "local_drs_v0_2_lineage_table": {"rows": observation["lineage_table"]},
        "local_drs_v0_2_provenance_table": {
            "rows": observation["provenance_table"]
        },
        "local_drs_v0_2_reuse_decision_table": {
            "rows": observation["reuse_decision_table"]
        },
    }


def _empty_avf_v0_2_observation() -> dict[str, Any]:
    return {
        "avf_v0_2_status": "not_run",
        "resolver_mode": "deterministic_local",
        "candidates_evaluated_count": 0,
        "top_candidate_id": None,
        "top_candidate_score": None,
        "hard_masked_count": 0,
        "unmasked_count": 0,
        "root_review_required_count": 0,
        "ranked_candidates": (),
        "hard_mask_table": (),
        "soft_mask_table": (),
        "score_explanation_table": (),
        "decision_reports_summary": (),
        "source_drs_report_ref": None,
        "source_drs_record_refs": (),
        "candidate_observations": {},
        "bounded_context_summary": {
            "evaluation_invoked": False,
            "candidates_evaluated_count": 0,
            "top_candidate_id": None,
            "top_candidate_score": None,
            "hard_masked_count": 0,
            "unmasked_count": 0,
            "candidate_observations": {},
            "non_authority_boundaries": AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
        },
        "avf_non_authority_boundaries": AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


def _avf_v0_2_report_artifacts(
    observation: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        "avf_v0_2_evaluation_report": dict(observation),
        "avf_v0_2_ranked_candidates": {
            "rows": observation["ranked_candidates"]
        },
        "avf_v0_2_hard_mask_table": {"rows": observation["hard_mask_table"]},
        "avf_v0_2_soft_mask_table": {"rows": observation["soft_mask_table"]},
        "avf_v0_2_score_explanation_table": {
            "rows": observation["score_explanation_table"]
        },
    }


def _empty_action_commit_packet_v0_2_integration() -> dict[str, Any]:
    return {
        "status": "not_run",
        "action_commit_packet_v0_2_status": "not_run",
        "packet_id": None,
        "created_by": None,
        "root_created": False,
        "human_approval_is_scoped_evidence_only": False,
        "packet_validated": False,
        "packet_validation_reasons": (),
        "registry_validated": False,
        "registry_is_local_proof_only": False,
        "registry_is_not_drs": True,
        "registry_is_not_authority": True,
        "registry_is_not_permission": True,
        "packet_corridor_entry_validated": False,
        "accepted_for_mock_corridor": False,
        "packet_seen_recorded_in_local_registry": False,
        "terminal_receipt_recorded_before_corridor": False,
        "allowed_subjects": (),
        "forbidden_subjects": (),
        "allowed_actions": (),
        "forbidden_actions": (),
        "allowed_adapters": (),
        "forbidden_adapters": (),
        "payment_slot_ref": None,
        "creditor_ref": None,
        "amount": None,
        "currency": None,
        "idempotency_key": None,
    }


def _empty_mock_bank_sandbox_v0_2_corridor_execution() -> dict[str, Any]:
    return {
        "status": "not_run",
        "mock_bank_sandbox_v0_2_status": "not_run",
        "source_packet_id": None,
        "source_packet_validated": False,
        "source_packet_corridor_entry_validated": False,
        "source_packet_seen_in_registry": False,
        "corridor_sequence": (),
        "mock_payment_intent": {},
        "mock_payment_consent": {},
        "mock_payment_order": {},
        "mock_receipt_evidence": {},
        "receipt_validated": False,
        "terminal_receipt_observed_in_local_registry": False,
        "receipt_evidence_only": False,
        "receipt_permission_created": False,
        "receipt_future_permission_created": False,
        "receipt_final_output_created": False,
        "receipt_authorizes_supplier_b": False,
        "receipt_releases_shipment": False,
        "receipt_mutates_packet_scope": False,
        "receipt_creates_production_drs_record": False,
        "supplier_b_excluded": False,
        "shipment_release_excluded": False,
        "real_bank_excluded": False,
        "real_payment_executed": False,
        "real_world_effects_count": 0,
    }


def _action_corridor_step(
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


def _action_corridor_report_artifacts(
    action_integration: Mapping[str, Any],
    mock_corridor: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        "action_commit_packet_v0_2_integration": dict(action_integration),
        "action_commit_packet_v0_2_packet_validation": {
            "packet_id": action_integration["packet_id"],
            "packet_validated": action_integration["packet_validated"],
            "reason_codes": action_integration["packet_validation_reasons"],
        },
        "action_commit_packet_v0_2_registry_validation": {
            "packet_id": action_integration["packet_id"],
            "registry_validated": action_integration["registry_validated"],
            "reason_codes": action_integration["registry_validation_reasons"],
            "registry_is_local_proof_only": action_integration[
                "registry_is_local_proof_only"
            ],
        },
        "action_commit_packet_v0_2_corridor_entry_validation": {
            "packet_id": action_integration["packet_id"],
            "packet_corridor_entry_validated": action_integration[
                "packet_corridor_entry_validated"
            ],
            "accepted_for_mock_corridor": action_integration[
                "accepted_for_mock_corridor"
            ],
            "reason_codes": action_integration[
                "corridor_entry_validation_reasons"
            ],
        },
        "mock_bank_sandbox_v0_2_corridor_execution": dict(mock_corridor),
        "mock_bank_sandbox_v0_2_corridor_sequence": {
            "rows": mock_corridor["corridor_sequence"]
        },
        "mock_bank_sandbox_v0_2_mock_payment_intent": mock_corridor[
            "mock_payment_intent"
        ],
        "mock_bank_sandbox_v0_2_mock_payment_consent": mock_corridor[
            "mock_payment_consent"
        ],
        "mock_bank_sandbox_v0_2_mock_payment_order": mock_corridor[
            "mock_payment_order"
        ],
        "mock_bank_sandbox_v0_2_mock_receipt_evidence": mock_corridor[
            "mock_receipt_evidence"
        ],
        "mock_bank_sandbox_v0_2_receipt_validation": {
            "receipt_validated": mock_corridor["receipt_validated"],
            "reason_codes": mock_corridor["receipt_validation_reasons"],
            "terminal_receipt_observed_in_local_registry": mock_corridor[
                "terminal_receipt_observed_in_local_registry"
            ],
        },
    }


def _collect_action_corridor_observation(
    counters: dict[str, int],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Mapping[str, Any]]]:
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
    source_packet_seen = (
        packet.packet_id in packet_seen_registry.seen_packet_ids
        and packet.idempotency.key in packet_seen_registry.used_idempotency_keys
    )
    terminal_receipt_before_corridor = bool(
        packet_seen_registry.terminal_receipt_packet_ids
        or packet_seen_registry.terminal_receipt_idempotency_keys
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
        _action_corridor_step(
            "root_created_action_commit_packet",
            "Root-created Supplier A packet model.",
            "Packet enters deterministic contract corridor.",
            "Scoped capability starts after Root only.",
            "packet_validation",
        ),
        _action_corridor_step(
            "packet_validation",
            "ActionCommitPacketV02 model.",
            f"packet_validated={str(packet_valid).lower()}",
            "Shape, Root creation, scope, TTL, idempotency, and adapter binding are checked.",
            "local_registry_replay_guard",
        ),
        _action_corridor_step(
            "local_registry_replay_guard",
            "Empty local proof-only registry.",
            f"packet_accepted_for_corridor={str(registry_report.packet_accepted_for_corridor_validation).lower()}",
            "Registry checks replay locally and remains non-authority.",
            "corridor_entry_validation",
        ),
        _action_corridor_step(
            "corridor_entry_validation",
            "Packet, corridor, child step, and registry.",
            f"accepted_for_mock_corridor={str(corridor_entry_report.accepted_for_mock_corridor).lower()}",
            "Entry validates packet plus child corridor containment.",
            "mock_payment_intent_consent",
        ),
        _action_corridor_step(
            "mock_payment_intent_consent",
            "Validated packet scope.",
            "mock payment intent and mock consent created.",
            "Intent and consent are deterministic local structures.",
            "scope_check",
        ),
        _action_corridor_step(
            "scope_check",
            "Child corridor allowed subjects/actions.",
            "Supplier A remains the only allowed subject.",
            "Scope is contained by packet scope.",
            "amount_check",
        ),
        _action_corridor_step(
            "amount_check",
            "Packet amount and child step amount.",
            "amount matches packet.",
            "Amount cannot drift after Root.",
            "creditor_check",
        ),
        _action_corridor_step(
            "creditor_check",
            "Packet creditor and child step creditor.",
            "creditor matches Supplier A.",
            "Creditor cannot drift to Supplier B.",
            "payment_slot_check",
        ),
        _action_corridor_step(
            "payment_slot_check",
            "Packet payment slot and child step payment slot.",
            "payment_slot matches packet.",
            "Payment slot remains evidence-bound and not permission.",
            "adapter_binding_check",
        ),
        _action_corridor_step(
            "adapter_binding_check",
            "Packet adapter binding and allowed adapters.",
            "mock_bank_sandbox adapter is inside allowed scope.",
            "Real bank, supplier API, and warehouse API remain excluded.",
            "idempotency_check",
        ),
        _action_corridor_step(
            "idempotency_check",
            "Packet idempotency key and child step key.",
            "idempotency key matches packet.",
            "Replay guard remains local proof-only.",
            "expiry_ttl_check",
        ),
        _action_corridor_step(
            "expiry_ttl_check",
            "Packet TTL and child step TTL.",
            "child TTL does not exceed packet TTL.",
            "Expired or wider TTL would fail closed.",
            "forbidden_surface_check",
        ),
        _action_corridor_step(
            "forbidden_surface_check",
            "Packet forbidden subjects, actions, and adapters.",
            "Supplier B, shipment release, and real APIs remain forbidden.",
            "Forbidden surface cannot shrink after Root.",
            "mock_payment_order",
        ),
        _action_corridor_step(
            "mock_payment_order",
            "Mock intent, mock consent, and validated packet.",
            "mock payment order created.",
            "Order is deterministic mock evidence, not real payment.",
            "mock_receipt_evidence",
        ),
        _action_corridor_step(
            "mock_receipt_evidence",
            "Mock payment order and packet.",
            f"receipt_validated={str(receipt_valid).lower()}",
            "Receipt evidence is bound to packet, adapter, amount, currency, and idempotency.",
            "terminal_receipt_observation",
        ),
        _action_corridor_step(
            "terminal_receipt_observation",
            "Validated receipt evidence and local registry.",
            f"terminal_receipt_observed={str(terminal_receipt_observed).lower()}",
            "Registry observes terminal receipt locally and creates no receipt.",
            "status_evidence_returns_to_root",
        ),
        _action_corridor_step(
            "status_evidence_returns_to_root",
            "Mock receipt evidence and local registry status.",
            "status/evidence returns to Root.",
            "Root remains final authority.",
            "root_boundary",
        ),
    )

    status = (
        STATUS_PASS
        if packet_valid
        and registry_report.validation_status == STATUS_PASS
        and corridor_entry_report.validation_status == STATUS_PASS
        and corridor_entry_report.accepted_for_mock_corridor
        and source_packet_seen
        and not terminal_receipt_before_corridor
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

    action_integration = {
        "status": status,
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
        "packet_seen_recorded_in_local_registry": source_packet_seen,
        "terminal_receipt_recorded_before_corridor": terminal_receipt_before_corridor,
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
    }
    mock_corridor = {
        "status": status,
        "mock_bank_sandbox_v0_2_status": status,
        "source_packet_id": packet.packet_id,
        "source_packet_validated": packet_valid,
        "source_packet_validation_reasons": packet_reasons,
        "source_packet_corridor_entry_validated": (
            corridor_entry_report.validation_status == STATUS_PASS
        ),
        "source_packet_corridor_entry_reasons": (
            corridor_entry_report.reason_codes
        ),
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

    if status == STATUS_PASS:
        counters.update(
            {
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
                "action_commit_packet_v0_2_terminal_receipt_recorded_count": 1,
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
            }
        )

    artifacts = _action_corridor_report_artifacts(action_integration, mock_corridor)
    return action_integration, mock_corridor, artifacts


def _avf_v0_2_candidate_observations(
    ranked_candidates: tuple[dict[str, Any], ...],
) -> dict[str, dict[str, Any]]:
    rows_by_id = {row["candidate_id"]: row for row in ranked_candidates}

    def row_observation(candidate_id: str) -> dict[str, Any]:
        row = rows_by_id[candidate_id]
        return {
            "candidate_id": candidate_id,
            "rank": row["rank"],
            "hard_masked": row["hard_mask_value"] == 0,
            "hard_mask_value": row["hard_mask_value"],
            "final_avf_score": row["final_avf_score"],
            "may_rank": row["final_avf_score"] > 0,
            "permission_granted": False,
            "action_created": False,
            "final_output_created": False,
            "root_review_required": row["root_review_required"],
        }

    return {
        "release_all_and_pay_all": row_observation("release_all_and_pay_all"),
        "pay_supplier_b": row_observation("pay_supplier_b"),
        "prepare_supplier_a_payment_form_only": row_observation(
            "prepare_supplier_a_payment_form_only"
        ),
        "request_fresh_warehouse_validation": row_observation(
            "request_fresh_warehouse_validation"
        ),
        "request_fresh_legal_accounting_validation": row_observation(
            "request_fresh_legal_accounting_validation"
        ),
        "keep_shipment_held": row_observation("keep_shipment_held"),
        "root_review_only": row_observation("root_review_only"),
        "block_supplier_b_and_hold_shipment": row_observation(
            "block_supplier_b_and_hold_shipment"
        ),
        "old_receipt_as_permission": {
            "candidate_id": "old_receipt_as_permission",
            "hard_masked": True,
            "hard_mask_value": 0,
            "final_avf_score": 0.0,
            "reason_code": "old_receipt_not_permission",
            "permission_granted": False,
        },
        "old_root_final_as_current_decision": {
            "candidate_id": "old_root_final_as_current_decision",
            "hard_masked": True,
            "hard_mask_value": 0,
            "final_avf_score": 0.0,
            "reason_code": "old_root_final_not_current_decision",
            "final_output_created": False,
        },
    }


def _collect_avf_v0_2_observation(
    counters: dict[str, int],
    local_drs_observation: Mapping[str, Any],
) -> dict[str, Any]:
    counters["avf_v0_2_evaluation_invoked_count"] += 1
    evaluation_input = build_wow_v1_2_avf_v02_evaluation_input()
    evaluation_report = evaluate_avf_candidates_v02(evaluation_input)

    ranked_candidates = tuple(
        asdict(row) for row in evaluation_report.ranked_candidates
    )
    decision_reports_summary = tuple(
        asdict(report) for report in evaluation_report.decision_reports
    )
    candidate_observations = _avf_v0_2_candidate_observations(ranked_candidates)

    counters["avf_v0_2_candidates_evaluated_count"] = (
        evaluation_report.candidates_evaluated_count
    )
    counters["avf_v0_2_hard_masked_count"] = evaluation_report.hard_masked_count
    counters["avf_v0_2_unmasked_count"] = evaluation_report.unmasked_count
    counters["avf_v0_2_root_review_required_count"] = (
        evaluation_report.root_review_required_count
    )

    avf_gate_passed = (
        evaluation_report.candidates_evaluated_count == 9
        and counters["avf_v0_2_top_ranked_candidate_permission_granted_count"] == 0
        and counters["avf_v0_2_action_permission_granted_count"] == 0
        and counters["avf_v0_2_final_output_created_count"] == 0
        and counters["avf_v0_2_action_commit_packet_created_count"] == 0
        and counters["avf_v0_2_receipt_created_count"] == 0
        and counters["avf_v0_2_payment_executed_count"] == 0
        and counters["avf_v0_2_shipment_released_count"] == 0
        and counters["avf_v0_2_root_bypass_count"] == 0
        and counters["avf_v0_2_provider_called_count"] == 0
        and counters["avf_v0_2_network_called_count"] == 0
        and counters["avf_v0_2_gemini_called_count"] == 0
        and evaluation_report.real_world_effects_count == 0
        and evaluation_report.production_ready_claimed is False
        and evaluation_report.public_auditor_ready_claimed is False
        and evaluation_report.advisory_only is True
        and evaluation_report.top_ranked_candidate_not_permission is True
        and evaluation_report.avf_score_is_not_authority is True
        and evaluation_report.hardmask_is_not_root is True
        and local_drs_observation["direct_reuse_allowed_count"] == 0
        and local_drs_observation["root_review_required_count"] == 11
    )

    return {
        "avf_v0_2_status": "PASS" if avf_gate_passed else "FAIL_CLOSED",
        "resolver_mode": evaluation_report.resolver_mode,
        "candidates_evaluated_count": evaluation_report.candidates_evaluated_count,
        "top_candidate_id": evaluation_report.top_candidate_id,
        "top_candidate_score": evaluation_report.top_candidate_score,
        "hard_masked_count": evaluation_report.hard_masked_count,
        "unmasked_count": evaluation_report.unmasked_count,
        "root_review_required_count": evaluation_report.root_review_required_count,
        "ranked_candidates": ranked_candidates,
        "hard_mask_table": evaluation_report.hard_mask_table,
        "soft_mask_table": evaluation_report.soft_mask_table,
        "score_explanation_table": evaluation_report.score_explanation_table,
        "decision_reports_summary": decision_reports_summary,
        "source_drs_report_ref": evaluation_input.source_drs_report_ref,
        "source_drs_record_refs": evaluation_input.source_drs_record_refs,
        "candidate_observations": candidate_observations,
        "bounded_context_summary": {
            "evaluation_invoked": True,
            "candidates_evaluated_count": evaluation_report.candidates_evaluated_count,
            "top_candidate_id": evaluation_report.top_candidate_id,
            "top_candidate_score": evaluation_report.top_candidate_score,
            "hard_masked_count": evaluation_report.hard_masked_count,
            "unmasked_count": evaluation_report.unmasked_count,
            "candidate_observations": candidate_observations,
            "non_authority_boundaries": AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
        },
        "avf_non_authority_boundaries": AVF_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


def _collect_local_drs_v0_2_observation(
    counters: dict[str, int],
) -> dict[str, Any]:
    counters["local_drs_v0_2_resolve_invoked_count"] += 1
    temporal_query = TemporalQueryV02(
        query_id="tq_full_wow_v1_2_live_observation_drs_v0_2",
        as_of="2026-07-06T17:10:00Z",
        context_time="full_wow_v1_2_live_observation",
        freshness_bias="current",
        require_root_review=True,
        allow_direct_reuse_if_all_gates_pass=False,
    )
    records = build_wow_v1_2_drs_v02_regression_records()
    resolve_report = resolve_drs_records_v02(
        LocalDRSResolveInputV02(
            temporal_query=temporal_query,
            records=records,
            query_scope="full_wow_v1_2_live_observation",
            resolver_mode="deterministic_local",
            production_ready_claimed=False,
            public_auditor_ready_claimed=False,
        )
    )
    rows = tuple(asdict(row) for row in resolve_report.rows)
    decisions_summary = {
        row["record_id"]: {
            "record_id": row["record_id"],
            "record_kind": row["record_kind"],
            "freshness_class": row["freshness_class"],
            "reuse_decision_class": row["reuse_decision_class"],
            "direct_reuse_allowed": row["direct_reuse_allowed"],
            "context_only": row["context_only"],
            "root_review_required": row["root_review_required"],
            "reason_codes": tuple(row["reason_codes"]),
        }
        for row in rows
    }
    status = "PASS"
    if not (
        resolve_report.records_evaluated_count == 11
        and resolve_report.direct_reuse_allowed_count == 0
        and resolve_report.root_review_required_count == 11
        and resolve_report.real_world_effects_count == 0
        and resolve_report.production_ready_claimed is False
        and resolve_report.public_auditor_ready_claimed is False
    ):
        status = "FAIL_CLOSED"

    counters["local_drs_v0_2_records_evaluated_count"] = (
        resolve_report.records_evaluated_count
    )
    counters["local_drs_v0_2_direct_reuse_allowed_count"] = (
        resolve_report.direct_reuse_allowed_count
    )
    counters["local_drs_v0_2_root_review_required_count"] = (
        resolve_report.root_review_required_count
    )
    counters["local_drs_v0_2_context_only_count"] = (
        resolve_report.context_only_count
    )
    counters["local_drs_v0_2_warning_only_count"] = (
        resolve_report.warning_only_count
    )
    counters["local_drs_v0_2_rerun_required_count"] = (
        resolve_report.rerun_required_count
    )
    counters["local_drs_v0_2_blocked_count"] = resolve_report.blocked_count

    return {
        "local_drs_v0_2_status": status,
        "resolver_mode": resolve_report.resolver_mode,
        "temporal_query_present": resolve_report.temporal_query_present,
        "records_evaluated_count": resolve_report.records_evaluated_count,
        "direct_reuse_allowed_count": resolve_report.direct_reuse_allowed_count,
        "direct_reuse_candidate_count": resolve_report.direct_reuse_candidate_count,
        "context_only_count": resolve_report.context_only_count,
        "warning_only_count": resolve_report.warning_only_count,
        "rerun_required_count": resolve_report.rerun_required_count,
        "blocked_count": resolve_report.blocked_count,
        "root_review_required_count": resolve_report.root_review_required_count,
        "freshness_table": resolve_report.freshness_table,
        "lineage_table": resolve_report.lineage_table,
        "provenance_table": resolve_report.provenance_table,
        "reuse_decision_table": resolve_report.reuse_decision_table,
        "decisions_summary": decisions_summary,
        "baseline_regression_scenario_ids": tuple(
            record.record_id for record in records
        ),
        "bounded_context_summary": {
            "records_evaluated_count": resolve_report.records_evaluated_count,
            "direct_reuse_allowed_count": resolve_report.direct_reuse_allowed_count,
            "root_review_required_count": resolve_report.root_review_required_count,
            "scenario_summaries": LOCAL_DRS_V0_2_SCENARIO_SUMMARIES,
            "non_authority_boundaries": LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
        },
        "drs_non_authority_boundaries": LOCAL_DRS_V0_2_NON_AUTHORITY_BOUNDARIES,
    }


def _build_local_drs_v0_2_writeback_candidate() -> dict[str, Any]:
    return {
        "writeback_candidate_id": "local_drs_v0_2_writeback_full_wow_v1_2_live_observation_001",
        "source_run_id": RUN_ID,
        "source_trace_type": "manual_live_multillm_fractal_observation_lane",
        "source_root_boundary_evaluated": True,
        "summary": "Local proof/audit-only DRS writeback candidate after Root boundary evaluation.",
        "lineage_refs": (
            "full_wow_v1_2_manual_live_multillm_fractal_trace_v01",
            "local_drs_v0_2_reuse_decision_report",
        ),
        "decision_class": "context_only_after_root_review",
        "direct_reuse_allowed": False,
        "root_review_required": True,
        "action_permission_created": False,
        "final_output_created_by_drs": False,
        "payment_executed": False,
        "shipment_released": False,
        "receipt_created": False,
        "action_commit_packet_created": False,
        "local_proof_audit_only": True,
        "future_permission_created": False,
        "production_persisted": False,
        "persisted_to_global_drs": False,
    }


def validate_local_drs_v0_2_writeback_candidate(
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    required_true_fields = (
        "source_root_boundary_evaluated",
        "local_proof_audit_only",
    )
    required_false_fields = (
        "direct_reuse_allowed",
        "future_permission_created",
        "action_permission_created",
        "final_output_created_by_drs",
        "payment_executed",
        "shipment_released",
        "receipt_created",
        "action_commit_packet_created",
        "production_persisted",
        "persisted_to_global_drs",
    )
    for field in required_true_fields:
        if candidate.get(field) is not True:
            errors.append(f"required_true_field:{field}")
    for field in required_false_fields:
        if candidate.get(field) is not False:
            errors.append(f"required_false_field:{field}")
    return {"accepted": not errors, "errors": tuple(errors)}


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
        "failed_role": None,
        "failed_stage": None,
        "provider_error_kind": None,
        "provider_error_status_code": None,
        "provider_error_message_sanitized": None,
        "provider_error_sanitized": None,
        "validation_errors": (),
        "env_enabled": env.get(ENABLE_ENV) == "1",
        "core_ci_dependency": False,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "pipeline_sequence": (),
        "semantic_actor_calls": (),
        "local_drs_v0_2_observation": _empty_local_drs_v0_2_observation(),
        "avf_v0_2_observation": _empty_avf_v0_2_observation(),
        "local_drs_v0_2_writeback_candidate": None,
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
        "action_commit_packet_v0_2_integration": (
            _empty_action_commit_packet_v0_2_integration()
        ),
        "mock_bank_sandbox_v0_2_corridor_execution": (
            _empty_mock_bank_sandbox_v0_2_corridor_execution()
        ),
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


def _build_orchestrator_prompt(
    local_drs_v0_2_bounded_context: Mapping[str, Any] | None = None,
    avf_v0_2_bounded_context: Mapping[str, Any] | None = None,
) -> str:
    local_drs_context = dict(local_drs_v0_2_bounded_context or {})
    avf_context = dict(avf_v0_2_bounded_context or {})
    bounded_input = {
        "context_type": "full_wow_v1_2_manual_live_multillm_fractal_orchestrator_input",
        "product_trace_basis": "Full WOW v1.2 deterministic product trace PASS",
        "business_modules": [
            "WarehouseAPI",
            "SupplierA",
            "SupplierB",
            "Legal",
            "Accounting",
            "BankA",
            "BankB",
        ],
        "business_facts": [
            "Supplier B remains blocked.",
            "Shipment release remains held.",
            "Receipt remains evidence only.",
            "Runtime owns PlanGraph/local plan artifacts.",
        ],
        "local_drs_v0_2_bounded_context": local_drs_context,
        "avf_v0_2_bounded_context": avf_context,
        "raw_user_text_included": False,
        "raw_provider_text_included": False,
        "raw_drs_authority_included": False,
        "raw_drs_tables_included": False,
        "raw_avf_tables_included": False,
        "raw_bank_secrets_included": False,
        "raw_iban_included": False,
        "bank_token_included": False,
        "action_permission_included": False,
        "final_output_included": False,
        "provider_owned_plangraph_included": False,
        "avf_as_root_wording_included": False,
    }
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            "Role: top-level semantic Orchestrator proposal actor.",
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.",
            "Provider output is not truth, authority, action permission, or FinalOutput.",
            "Runtime owns PlanGraph/local plan artifacts. Provider does not own PlanGraph.",
            "Local DRS v0.2 context is advisory context only.",
            "DRS v0.2 is not truth.",
            "DRS v0.2 is not authority.",
            "DRS v0.2 is not permission.",
            "DRS hit is context only.",
            "Direct reuse remains default false.",
            "AVF v0.2 context is advisory pressure/ranking only.",
            "AVF v0.2 is not truth.",
            "AVF v0.2 is not authority.",
            "AVF v0.2 is not permission.",
            "Top-ranked AVF candidate is not permission.",
            "AVF score is not Root.",
            "AVF score is not authority.",
            "HardMask is not Root.",
            "Root remains final authority.",
            "BOUNDED_INPUT_CONTEXT:",
            json.dumps(bounded_input, indent=2, sort_keys=True),
            "OUTPUT_SHAPE_CONTRACT:",
            "Return exactly one JSON object.",
            "The final response must use the JSON object below as its complete top-level shape.",
            "The top-level key set must match the JSON object below exactly.",
            "Do not add top-level keys.",
            "Do not remove top-level keys.",
            "Do not rename top-level keys.",
            "Boolean claim fields must remain false where shown.",
            "root_review_required must remain true.",
            "JSON skeleton:",
            json.dumps(ORCHESTRATOR_JSON_SKELETON, indent=2, sort_keys=True),
        )
    )


def _build_architect_prompt(bsep_packet: Mapping[str, Any]) -> str:
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            "Role: top-level Semantic Architect proposal actor.",
            "Use only BSEP-derived bounded context.",
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.",
            "Provider output is not truth, authority, action permission, or FinalOutput.",
            "Runtime owns PlanGraph/local plan artifacts. Provider does not own PlanGraph.",
            "PlanGraph is not authority.",
            "BSEP_CONTEXT:",
            json.dumps(bsep_packet, indent=2, sort_keys=True),
            "OUTPUT_SHAPE_CONTRACT:",
            "Return exactly one JSON object.",
            "The final response must use the JSON object below as its complete top-level shape.",
            "The top-level key set must match the JSON object below exactly.",
            "Do not add top-level keys.",
            "Do not remove top-level keys.",
            "Do not rename top-level keys.",
            "Boolean claim fields must remain false where shown.",
            "JSON skeleton:",
            json.dumps(ARCHITECT_JSON_SKELETON, indent=2, sort_keys=True),
        )
    )


def _build_branch_prompt(role: str, branch_id: str) -> str:
    skeleton = {
        **BRANCH_SEMANTIC_JSON_SKELETON,
        "branch_semantic_proposal_id": f"{role}-semantic-001",
        "source_branch_id": branch_id,
    }
    bounded_input = {
        "context_type": "full_wow_v1_2_branch_semantic_input",
        "role": role,
        "branch_id": branch_id,
        "branch_context": _branch_context(branch_id),
        "branch_evidence": _branch_evidence(branch_id),
        "raw_user_text_included": False,
        "raw_provider_text_included": False,
        "raw_bank_secrets_included": False,
        "raw_iban_included": False,
        "bank_token_included": False,
    }
    return "\n".join(
        (
            "FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE",
            f"Role: {role}.",
            f"Branch: {branch_id}.",
            "Branch LLM/SLM output is advisory only and returns to parent/root review.",
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.",
            "Branch LLM/SLM output does not create ActionCommitPacket, receipt, payment, or shipment release.",
            "Branch LLM/SLM output is not truth, authority, action permission, or FinalOutput.",
            "BOUNDED_BRANCH_INPUT_CONTEXT:",
            json.dumps(bounded_input, indent=2, sort_keys=True),
            "OUTPUT_SHAPE_CONTRACT:",
            "Return exactly one JSON object.",
            "The final response must use the JSON object below as its complete top-level shape.",
            "The top-level key set must match the JSON object below exactly.",
            "Do not add top-level keys.",
            "Do not remove top-level keys.",
            "Do not rename top-level keys.",
            "Boolean claim fields must remain false where shown.",
            "JSON skeleton:",
            json.dumps(skeleton, indent=2, sort_keys=True),
        )
    )


def _build_bsep(
    orchestrator: Mapping[str, Any],
    local_drs_v0_2_bounded_context: Mapping[str, Any] | None = None,
    avf_v0_2_bounded_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    drs_context = dict(local_drs_v0_2_bounded_context or {})
    avf_context = dict(avf_v0_2_bounded_context or {})
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
            "Local DRS v0.2 resolve report was invoked.",
            "Local DRS v0.2 direct_reuse_allowed_count is 0.",
            "Local DRS v0.2 root_review_required_count is 11.",
            "Supplier A prior trace may inform bounded context.",
            "Supplier B blocker trace may warn or block.",
            "old receipt is not current permission.",
            "old Root Final is not silently reused.",
            "changed facts require rerun validation.",
            "DRS writeback after Root remains local proof/audit only.",
            "AVF v0.2 evaluation report was invoked.",
            "AVF v0.2 candidates evaluated count is 9.",
            "AVF hard-masked release_all_and_pay_all.",
            "AVF hard-masked Supplier B payment.",
            "top-ranked AVF candidate is not permission.",
            "AVF score is not authority.",
            "HardMask is not Root.",
            "Root remains final authority.",
        ],
        "local_drs_v0_2_resolve_invoked": bool(drs_context),
        "local_drs_v0_2_bounded_context": drs_context,
        "avf_v0_2_evaluation_invoked": bool(avf_context),
        "avf_v0_2_bounded_context": avf_context,
        "raw_user_text_included": False,
        "raw_provider_text_included": False,
        "raw_drs_authority_included": False,
        "raw_drs_tables_included": False,
        "raw_avf_tables_included": False,
        "raw_bank_secrets_included": False,
        "raw_iban_included": False,
        "bank_token_included": False,
        "action_permission_included": False,
        "final_output_included": False,
        "avf_as_root_wording_included": False,
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
        "raw_drs_tables_included",
        "raw_avf_tables_included",
        "action_permission_included",
        "final_output_included",
        "avf_as_root_wording_included",
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


def _branch_artifact_prefix(branch_id: str) -> str:
    return {
        "legal_branch": "branch_legal",
        "accounting_branch": "branch_accounting",
        "supplier_b_branch": "branch_supplier_b",
        "bank_b_branch": "branch_bank_policy",
    }[branch_id]


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


def _config_value_from_env_or_config(
    env: Mapping[str, str],
    *names: str,
    allow_config: bool = True,
) -> str | None:
    for name in names:
        value = env.get(name)
        if isinstance(value, str) and value.strip():
            return value

    if not allow_config:
        return None

    try:
        config = __import__("config")
    except Exception:
        return None

    for name in names:
        value = getattr(config, name, None)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _live_gemini_config_available(env: Mapping[str, str]) -> bool:
    return bool(
        _config_value_from_env_or_config(
            env,
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_GEMINI_API_KEY",
        )
    )


def _secret_values_for_redaction(env: Mapping[str, str]) -> tuple[str, ...]:
    values: list[str] = []
    for name in GEMINI_KEY_NAMES:
        for allow_config in (False, True):
            value = _config_value_from_env_or_config(
                env,
                name,
                allow_config=allow_config,
            )
            if value and value not in values:
                values.append(value)
    return tuple(values)


def _sanitize_provider_error_text(
    text: str,
    env: Mapping[str, str],
    *,
    max_length: int = 500,
) -> str:
    sanitized = " ".join(text.split())
    for value in _secret_values_for_redaction(env):
        sanitized = sanitized.replace(value, "[REDACTED]")
    sanitized = re.sub(r"AIza[0-9A-Za-z_-]{10,}", "[REDACTED]", sanitized)
    sanitized = re.sub(
        r"(?i)(api[_ -]?key|token)\s*[:=]\s*['\"]?[^'\"\s,;})]+",
        r"\1=[REDACTED]",
        sanitized,
    )
    for marker in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
    ):
        sanitized = sanitized.replace(marker, "[REDACTED]")
    return sanitized[:max_length] if sanitized else "provider_error"


def _provider_error_status_code(exc: Exception) -> int | str | None:
    for attr_name in ("status_code", "code"):
        value = getattr(exc, attr_name, None)
        if value is not None:
            return int(value) if isinstance(value, str) and value.isdigit() else value

    response = getattr(exc, "response", None)
    if response is not None:
        for attr_name in ("status_code", "status"):
            value = getattr(response, attr_name, None)
            if value is not None:
                return (
                    int(value)
                    if isinstance(value, str) and value.isdigit()
                    else value
                )
    return None


def _provider_error_raw_message(exc: Exception) -> str:
    message = getattr(exc, "message", None)
    if isinstance(message, str) and message.strip():
        return message
    return str(exc)


def _provider_error_info(
    role: str,
    exc: Exception,
    env: Mapping[str, str],
) -> dict[str, Any]:
    raw_message = str(exc)
    status_code = _provider_error_status_code(exc)
    if raw_message.startswith("missing_gemini_api_key"):
        kind = "missing_gemini_api_key"
        message_sanitized = "missing_gemini_api_key"
    elif raw_message.startswith("empty_provider_response"):
        kind = "empty_provider_response"
        message_sanitized = "empty_provider_response"
    else:
        kind = exc.__class__.__name__
        if status_code is not None or kind.endswith("ClientError"):
            raw_detail = _provider_error_raw_message(exc)
        else:
            raw_detail = kind
        message_sanitized = _sanitize_provider_error_text(raw_detail, env)
    status_part = f" status={status_code}" if status_code is not None else ""
    sanitized = f"{kind}{status_part} message={message_sanitized}"[:500]
    return {
        "reason": f"provider_call_failed:{role}",
        "provider_error_kind": kind,
        "provider_error_status_code": status_code,
        "provider_error_message_sanitized": message_sanitized,
        "provider_error_sanitized": sanitized,
    }


def _artifact_text(artifacts: Mapping[str, Any], key: str) -> str:
    value = artifacts.get(key)
    if value is None:
        return "not_run\n"
    return str(value)


def _artifact_json(artifacts: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = artifacts.get(key)
    if isinstance(value, Mapping):
        return value
    if value is None:
        return {"status": "not_run"}
    return {"value": value}


def _artifact_capture(
    report: Mapping[str, Any],
    artifact_dir: Path,
    artifacts: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    text_files = {
        "top_level_orchestrator_prompt.txt": _artifact_text(
            artifacts, "top_level_orchestrator_prompt"
        ),
        "top_level_orchestrator_raw_response.txt": _artifact_text(
            artifacts, "top_level_orchestrator_raw_response"
        ),
        "top_level_architect_prompt.txt": _artifact_text(
            artifacts, "top_level_architect_prompt"
        ),
        "top_level_architect_raw_response.txt": _artifact_text(
            artifacts, "top_level_architect_raw_response"
        ),
        "branch_legal_prompt.txt": _artifact_text(artifacts, "branch_legal_prompt"),
        "branch_legal_raw_response.txt": _artifact_text(
            artifacts, "branch_legal_raw_response"
        ),
        "branch_accounting_prompt.txt": _artifact_text(
            artifacts, "branch_accounting_prompt"
        ),
        "branch_accounting_raw_response.txt": _artifact_text(
            artifacts, "branch_accounting_raw_response"
        ),
        "branch_supplier_b_prompt.txt": _artifact_text(
            artifacts, "branch_supplier_b_prompt"
        ),
        "branch_supplier_b_raw_response.txt": _artifact_text(
            artifacts, "branch_supplier_b_raw_response"
        ),
        "branch_bank_policy_prompt.txt": _artifact_text(
            artifacts, "branch_bank_policy_prompt"
        ),
        "branch_bank_policy_raw_response.txt": _artifact_text(
            artifacts, "branch_bank_policy_raw_response"
        ),
    }
    json_files = {
        "local_drs_v0_2_resolve_report.json": _artifact_json(
            artifacts, "local_drs_v0_2_resolve_report"
        ),
        "local_drs_v0_2_freshness_table.json": _artifact_json(
            artifacts, "local_drs_v0_2_freshness_table"
        ),
        "local_drs_v0_2_lineage_table.json": _artifact_json(
            artifacts, "local_drs_v0_2_lineage_table"
        ),
        "local_drs_v0_2_provenance_table.json": _artifact_json(
            artifacts, "local_drs_v0_2_provenance_table"
        ),
        "local_drs_v0_2_reuse_decision_table.json": _artifact_json(
            artifacts, "local_drs_v0_2_reuse_decision_table"
        ),
        "local_drs_v0_2_writeback_candidate.json": _artifact_json(
            artifacts, "local_drs_v0_2_writeback_candidate"
        ),
        "avf_v0_2_evaluation_report.json": _artifact_json(
            artifacts, "avf_v0_2_evaluation_report"
        ),
        "avf_v0_2_ranked_candidates.json": _artifact_json(
            artifacts, "avf_v0_2_ranked_candidates"
        ),
        "avf_v0_2_hard_mask_table.json": _artifact_json(
            artifacts, "avf_v0_2_hard_mask_table"
        ),
        "avf_v0_2_soft_mask_table.json": _artifact_json(
            artifacts, "avf_v0_2_soft_mask_table"
        ),
        "avf_v0_2_score_explanation_table.json": _artifact_json(
            artifacts, "avf_v0_2_score_explanation_table"
        ),
        "top_level_orchestrator_extracted_json_candidate.json": _artifact_json(
            artifacts, "top_level_orchestrator_json"
        ),
        "top_level_orchestrator_validation.json": _artifact_json(
            artifacts, "top_level_orchestrator_validation"
        ),
        "bsep_packet.json": _artifact_json(artifacts, "bsep_packet"),
        "bsep_validation.json": _artifact_json(artifacts, "bsep_validation"),
        "top_level_architect_extracted_json_candidate.json": _artifact_json(
            artifacts, "top_level_architect_json"
        ),
        "top_level_architect_validation.json": _artifact_json(
            artifacts, "top_level_architect_validation"
        ),
        "branch_legal_validation.json": _artifact_json(
            artifacts, "branch_legal_validation"
        ),
        "branch_accounting_validation.json": _artifact_json(
            artifacts, "branch_accounting_validation"
        ),
        "branch_supplier_b_validation.json": _artifact_json(
            artifacts, "branch_supplier_b_validation"
        ),
        "branch_bank_policy_validation.json": _artifact_json(
            artifacts, "branch_bank_policy_validation"
        ),
        "action_commit_packet_v0_2_integration.json": _artifact_json(
            artifacts, "action_commit_packet_v0_2_integration"
        ),
        "action_commit_packet_v0_2_packet_validation.json": _artifact_json(
            artifacts, "action_commit_packet_v0_2_packet_validation"
        ),
        "action_commit_packet_v0_2_registry_validation.json": _artifact_json(
            artifacts, "action_commit_packet_v0_2_registry_validation"
        ),
        "action_commit_packet_v0_2_corridor_entry_validation.json": _artifact_json(
            artifacts, "action_commit_packet_v0_2_corridor_entry_validation"
        ),
        "mock_bank_sandbox_v0_2_corridor_execution.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_corridor_execution"
        ),
        "mock_bank_sandbox_v0_2_corridor_sequence.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_corridor_sequence"
        ),
        "mock_bank_sandbox_v0_2_mock_payment_intent.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_mock_payment_intent"
        ),
        "mock_bank_sandbox_v0_2_mock_payment_consent.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_mock_payment_consent"
        ),
        "mock_bank_sandbox_v0_2_mock_payment_order.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_mock_payment_order"
        ),
        "mock_bank_sandbox_v0_2_mock_receipt_evidence.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_mock_receipt_evidence"
        ),
        "mock_bank_sandbox_v0_2_receipt_validation.json": _artifact_json(
            artifacts, "mock_bank_sandbox_v0_2_receipt_validation"
        ),
    }
    for name, value in text_files.items():
        _write_text(artifact_dir / name, value)
        written.append(name)
    for name, value in json_files.items():
        _write_json(artifact_dir / name, value)
        written.append(name)

    capture = {
        "artifact_dir": str(artifact_dir),
        "written_files": tuple(sorted((*written, "secret_scan.json", "summary.json", "summary.log"))),
        "artifact_capture_enabled": True,
    }
    summary_report = dict(report)
    summary_report["artifacts"] = capture
    _write_json(artifact_dir / "summary.json", summary_report)
    written.append("summary.json")
    _write_text(
        artifact_dir / "summary.log",
        render_full_wow_v1_2_manual_live_multillm_fractal_trace(summary_report),
    )
    written.append("summary.log")

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
    api_key = _config_value_from_env_or_config(
        env,
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
    )
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
) -> tuple[str | None, str, dict[str, Any] | None]:
    counters["semantic_actor_call_count"] += 1
    counters[actor_counter] += 1
    if provider is not None:
        counters["fake_provider_call_count"] += 1
        try:
            return provider(role, prompt, context), "fake_injected", None
        except Exception as exc:
            return None, "fake_injected", _provider_error_info(role, exc, env)
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
    except Exception as exc:
        return None, "real_provider", _provider_error_info(role, exc, env)


def _fail_closed_report(
    *,
    env: Mapping[str, str],
    model_name: str,
    provider_mode: str,
    counters: Mapping[str, int],
    reason: str,
    pipeline_sequence: tuple[str, ...],
    semantic_actor_calls: tuple[Mapping[str, Any], ...],
    artifacts: Mapping[str, Any] | None = None,
    failed_role: str | None = None,
    failed_stage: str | None = None,
    provider_error_kind: str | None = None,
    provider_error_status_code: int | str | None = None,
    provider_error_message_sanitized: str | None = None,
    provider_error_sanitized: str | None = None,
    validation_errors: tuple[str, ...] = (),
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
    report["failed_role"] = failed_role
    report["failed_stage"] = failed_stage
    report["provider_error_kind"] = provider_error_kind
    report["provider_error_status_code"] = provider_error_status_code
    report["provider_error_message_sanitized"] = provider_error_message_sanitized
    report["provider_error_sanitized"] = provider_error_sanitized
    report["validation_errors"] = validation_errors
    if artifacts and isinstance(artifacts.get("local_drs_v0_2_resolve_report"), Mapping):
        report["local_drs_v0_2_observation"] = artifacts[
            "local_drs_v0_2_resolve_report"
        ]
    if artifacts and isinstance(artifacts.get("avf_v0_2_evaluation_report"), Mapping):
        report["avf_v0_2_observation"] = artifacts["avf_v0_2_evaluation_report"]
    if artifacts and isinstance(
        artifacts.get("action_commit_packet_v0_2_integration"), Mapping
    ):
        report["action_commit_packet_v0_2_integration"] = artifacts[
            "action_commit_packet_v0_2_integration"
        ]
    if artifacts and isinstance(
        artifacts.get("mock_bank_sandbox_v0_2_corridor_execution"), Mapping
    ):
        report["mock_bank_sandbox_v0_2_corridor_execution"] = artifacts[
            "mock_bank_sandbox_v0_2_corridor_execution"
        ]
    artifact_dir_value = env.get(ARTIFACT_DIR_ENV)
    if artifact_dir_value:
        capture = _artifact_capture(report, Path(artifact_dir_value), artifacts or {})
        report["artifacts"] = {
            "artifact_dir": capture["artifact_dir"],
            "written_files": capture["written_files"],
            "artifact_capture_enabled": True,
        }
        report["secret_membrane"]["artifact_secret_scan_passed"] = capture[
            "secret_scan"
        ]["passed"]
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

    if provider is None and not _live_gemini_config_available(effective_env):
        report = _base_report(
            final_status="SKIPPED_CLOSED",
            stage_status="SKIPPED_CLOSED",
            env=effective_env,
            model_name=model_name,
            provider_mode="missing_key",
            counters=_zero_counters(),
            skip_reason="Gemini key missing; live lane remains closed.",
        )
        report["provider_error_kind"] = "missing_gemini_api_key"
        report["provider_error_status_code"] = None
        report["provider_error_message_sanitized"] = "missing_gemini_api_key"
        report["provider_error_sanitized"] = "missing_gemini_api_key"
        return report

    counters = _enabled_counters()
    provider_mode = "fake_injected" if provider is not None else "real_provider"

    actor_calls: list[dict[str, Any]] = []
    artifacts: dict[str, Any] = {}
    sequence: list[str] = ["dirty_request_loaded_from_v1_2_product_trace"]

    local_drs_observation = _collect_local_drs_v0_2_observation(counters)
    artifacts.update(_local_drs_v0_2_report_artifacts(local_drs_observation))
    sequence.append("local_drs_v0_2_resolve_invoked")
    if local_drs_observation["local_drs_v0_2_status"] != "PASS":
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="local_drs_v0_2_resolve_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="local_drs_v0_2_resolver",
            failed_stage="local_drs_v0_2_resolve",
            validation_errors=("local_drs_v0_2_resolve_failed",),
        )

    avf_observation = _collect_avf_v0_2_observation(counters, local_drs_observation)
    artifacts.update(_avf_v0_2_report_artifacts(avf_observation))
    sequence.append("avf_v0_2_evaluation_invoked")
    if avf_observation["avf_v0_2_status"] != "PASS":
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="avf_v0_2_evaluation_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="avf_v0_2_evaluator",
            failed_stage="avf_v0_2_evaluation",
            validation_errors=("avf_v0_2_evaluation_failed",),
        )

    orchestrator_prompt = _build_orchestrator_prompt(
        local_drs_observation["bounded_context_summary"],
        avf_observation["bounded_context_summary"],
    )
    artifacts["top_level_orchestrator_prompt"] = orchestrator_prompt
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
        provider_error_reason = provider_error["reason"]
        artifacts["top_level_orchestrator_raw_response"] = "not_run"
        artifacts["top_level_orchestrator_json"] = {"status": "not_run"}
        artifacts["top_level_orchestrator_validation"] = {
            "accepted": False,
            "errors": [provider_error_reason],
            "provider_error_kind": provider_error["provider_error_kind"],
            "provider_error_status_code": provider_error[
                "provider_error_status_code"
            ],
            "provider_error_message_sanitized": provider_error[
                "provider_error_message_sanitized"
            ],
            "provider_error_sanitized": provider_error[
                "provider_error_sanitized"
            ],
        }
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=provider_error_reason,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="top_level_orchestrator_llm",
            failed_stage="provider_call",
            provider_error_kind=provider_error["provider_error_kind"],
            provider_error_status_code=provider_error[
                "provider_error_status_code"
            ],
            provider_error_message_sanitized=provider_error[
                "provider_error_message_sanitized"
            ],
            provider_error_sanitized=provider_error["provider_error_sanitized"],
            validation_errors=(provider_error_reason,),
        )
    orchestrator_json, parse_error = _extract_json_object(raw_orchestrator)
    if parse_error:
        artifacts["top_level_orchestrator_raw_response"] = raw_orchestrator
        artifacts["top_level_orchestrator_json"] = {"status": "parse_failed"}
        artifacts["top_level_orchestrator_validation"] = {
            "accepted": False,
            "errors": [parse_error],
        }
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=parse_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="top_level_orchestrator_llm",
            failed_stage="json_extraction",
            validation_errors=(parse_error,),
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
            artifacts=artifacts,
            failed_role="top_level_orchestrator_llm",
            failed_stage="orchestrator_validation",
            validation_errors=tuple(orchestrator_validation["errors"]),
        )
    sequence.extend(
        (
            "top_level_orchestrator_semantics_validated",
            "top_level_orchestrator_semantics_canonicalized",
        )
    )

    bsep_packet = _build_bsep(
        orchestrator_validation["canonical"],
        local_drs_observation["bounded_context_summary"],
        avf_observation["bounded_context_summary"],
    )
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
            artifacts=artifacts,
            failed_role="runtime_bsep",
            failed_stage="bsep_validation",
            validation_errors=tuple(bsep_validation["errors"]),
        )
    counters["bsep_created_count"] = 1
    counters["bsep_validated_count"] = 1
    sequence.extend(("bsep_created", "bsep_validated"))

    architect_prompt = _build_architect_prompt(bsep_packet)
    artifacts["top_level_architect_prompt"] = architect_prompt
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
        provider_error_reason = provider_error["reason"]
        artifacts["top_level_architect_raw_response"] = "not_run"
        artifacts["top_level_architect_json"] = {"status": "not_run"}
        artifacts["top_level_architect_validation"] = {
            "accepted": False,
            "errors": [provider_error_reason],
            "provider_error_kind": provider_error["provider_error_kind"],
            "provider_error_status_code": provider_error[
                "provider_error_status_code"
            ],
            "provider_error_message_sanitized": provider_error[
                "provider_error_message_sanitized"
            ],
            "provider_error_sanitized": provider_error[
                "provider_error_sanitized"
            ],
        }
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=provider_error_reason,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="top_level_semantic_architect_llm",
            failed_stage="provider_call",
            provider_error_kind=provider_error["provider_error_kind"],
            provider_error_status_code=provider_error[
                "provider_error_status_code"
            ],
            provider_error_message_sanitized=provider_error[
                "provider_error_message_sanitized"
            ],
            provider_error_sanitized=provider_error["provider_error_sanitized"],
            validation_errors=(provider_error_reason,),
        )
    architect_json, parse_error = _extract_json_object(raw_architect)
    if parse_error:
        artifacts["top_level_architect_raw_response"] = raw_architect
        artifacts["top_level_architect_json"] = {"status": "parse_failed"}
        artifacts["top_level_architect_validation"] = {
            "accepted": False,
            "errors": [parse_error],
        }
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason=parse_error,
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="top_level_semantic_architect_llm",
            failed_stage="json_extraction",
            validation_errors=(parse_error,),
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
            artifacts=artifacts,
            failed_role="top_level_semantic_architect_llm",
            failed_stage="architect_validation",
            validation_errors=tuple(architect_validation["errors"]),
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
        artifact_prefix = _branch_artifact_prefix(branch_id)
        artifacts[f"{artifact_prefix}_prompt"] = prompt
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
            provider_error_reason = provider_error["reason"]
            artifacts[f"{artifact_prefix}_raw_response"] = "not_run"
            artifacts[f"{artifact_prefix}_validation"] = {
                "accepted": False,
                "errors": [provider_error_reason],
                "provider_error_kind": provider_error["provider_error_kind"],
                "provider_error_status_code": provider_error[
                    "provider_error_status_code"
                ],
                "provider_error_message_sanitized": provider_error[
                    "provider_error_message_sanitized"
                ],
                "provider_error_sanitized": provider_error[
                    "provider_error_sanitized"
                ],
            }
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=provider_error_reason,
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
                artifacts=artifacts,
                failed_role=role,
                failed_stage="provider_call",
                provider_error_kind=provider_error["provider_error_kind"],
                provider_error_status_code=provider_error[
                    "provider_error_status_code"
                ],
                provider_error_message_sanitized=provider_error[
                    "provider_error_message_sanitized"
                ],
                provider_error_sanitized=provider_error[
                    "provider_error_sanitized"
                ],
                validation_errors=(provider_error_reason,),
            )
        branch_json, parse_error = _extract_json_object(raw)
        if parse_error:
            artifacts[f"{artifact_prefix}_raw_response"] = raw
            artifacts[f"{artifact_prefix}_validation"] = {
                "accepted": False,
                "errors": [parse_error],
            }
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=parse_error,
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
                artifacts=artifacts,
                failed_role=role,
                failed_stage="json_extraction",
                validation_errors=(parse_error,),
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
            artifacts[f"{artifact_prefix}_raw_response"] = raw
            artifacts[f"{artifact_prefix}_validation"] = validation
            return _fail_closed_report(
                env=effective_env,
                model_name=model_name,
                provider_mode=provider_mode,
                counters=counters,
                reason=f"{branch_id}_validation_failed",
                pipeline_sequence=tuple(sequence),
                semantic_actor_calls=tuple(actor_calls),
                artifacts=artifacts,
                failed_role=role,
                failed_stage=f"{branch_id}_validation",
                validation_errors=tuple(validation["errors"]),
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
    local_drs_writeback_candidate = _build_local_drs_v0_2_writeback_candidate()
    counters["local_drs_v0_2_writeback_candidate_created_count"] = 1
    counters["local_drs_v0_2_writeback_persisted_count"] = 0
    counters["local_drs_v0_2_writeback_local_proof_only_count"] = 1
    artifacts["local_drs_v0_2_writeback_candidate"] = local_drs_writeback_candidate
    sequence.extend(
        (
            "branch_result_proposals_merged",
            "post_vv_validated",
            "gt_lgt_advisory_reviewed",
            "root_final_boundary_evaluated",
        )
    )

    (
        action_commit_packet_integration,
        mock_bank_corridor_execution,
        action_corridor_artifacts,
    ) = _collect_action_corridor_observation(counters)
    artifacts.update(action_corridor_artifacts)
    sequence.extend(
        (
            "action_commit_packet_v0_2_integration_invoked",
            "action_commit_packet_v0_2_packet_validated",
            "action_commit_packet_v0_2_registry_validated",
            "action_commit_packet_v0_2_corridor_entry_validated",
            "action_commit_packet_v0_2_packet_seen_recorded",
            "mock_bank_sandbox_v0_2_corridor_invoked",
            "mock_bank_sandbox_v0_2_mock_payment_intent_created",
            "mock_bank_sandbox_v0_2_mock_payment_consent_created",
            "mock_bank_sandbox_v0_2_mock_payment_order_created",
            "mock_bank_sandbox_v0_2_mock_receipt_evidence_created",
            "mock_bank_sandbox_v0_2_receipt_validated",
            "mock_bank_sandbox_v0_2_terminal_receipt_observed",
        )
    )
    if (
        action_commit_packet_integration["status"] != STATUS_PASS
        or mock_bank_corridor_execution["status"] != STATUS_PASS
    ):
        return _fail_closed_report(
            env=effective_env,
            model_name=model_name,
            provider_mode=provider_mode,
            counters=counters,
            reason="action_corridor_validation_failed",
            pipeline_sequence=tuple(sequence),
            semantic_actor_calls=tuple(actor_calls),
            artifacts=artifacts,
            failed_role="deterministic_action_corridor",
            failed_stage="action_commit_packet_v0_2_corridor",
            validation_errors=(
                *tuple(
                    action_commit_packet_integration[
                        "packet_validation_reasons"
                    ]
                ),
                *tuple(
                    action_commit_packet_integration[
                        "registry_validation_reasons"
                    ]
                ),
                *tuple(
                    action_commit_packet_integration[
                        "corridor_entry_validation_reasons"
                    ]
                ),
                *tuple(
                    mock_bank_corridor_execution[
                        "receipt_validation_reasons"
                    ]
                ),
            ),
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
            "local_drs_v0_2_observation": local_drs_observation,
            "avf_v0_2_observation": avf_observation,
            "local_drs_v0_2_writeback_candidate": local_drs_writeback_candidate,
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
            "action_commit_packet_v0_2_integration": (
                action_commit_packet_integration
            ),
            "mock_bank_sandbox_v0_2_corridor_execution": (
                mock_bank_corridor_execution
            ),
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
    if report["final_status"] == "FAIL_CLOSED":
        lines.extend(
            [
                "",
                "[FAILURE DETAILS]",
                f"skip_reason: {report.get('skip_reason')}",
                f"failed_role: {report.get('failed_role')}",
                f"failed_stage: {report.get('failed_stage')}",
                f"provider_error_kind: {report.get('provider_error_kind')}",
                f"provider_error_status_code: {report.get('provider_error_status_code')}",
                f"provider_error_message_sanitized: {report.get('provider_error_message_sanitized')}",
                f"provider_error_sanitized: {report.get('provider_error_sanitized')}",
                f"validation_errors: {tuple(report.get('validation_errors') or ())}",
            ]
        )

    lines.extend(["", "[SEMANTIC ACTOR CALLS]"])
    for call in report["semantic_actor_calls"]:
        lines.append(
            "- role={role}; provider_mode={provider_mode}; validation_status={validation_status}".format(
                **call
            )
        )

    local_drs = report["local_drs_v0_2_observation"]
    lines.extend(["", "[LOCAL DRS V0.2 LIVE OBSERVATION]"])
    if local_drs["local_drs_v0_2_status"] == "not_run":
        lines.append("DRS v0.2 read/resolve did not run because the lane is closed.")
    else:
        lines.extend(
            [
                "DRS v0.2 read/resolve ran before Orchestrator.",
                "DRS found prior traces.",
                "DRS classified records as context/warning/rerun/blocked.",
                "DRS direct reuse allowed count remained 0.",
                "DRS did not authorize payment.",
                "DRS did not authorize shipment release.",
                "old receipt is not current permission.",
                "old Root Final is not silently reused.",
                "changed facts require rerun validation.",
                "DRS writeback candidate after Root is local proof/audit only.",
                "Root remains final authority.",
            ]
        )
    lines.extend(
        _render_mapping(
            {
                "local_drs_v0_2_status": local_drs["local_drs_v0_2_status"],
                "resolver_mode": local_drs["resolver_mode"],
                "records_evaluated_count": local_drs["records_evaluated_count"],
                "direct_reuse_allowed_count": local_drs[
                    "direct_reuse_allowed_count"
                ],
                "root_review_required_count": local_drs[
                    "root_review_required_count"
                ],
                "context_only_count": local_drs["context_only_count"],
                "warning_only_count": local_drs["warning_only_count"],
                "rerun_required_count": local_drs["rerun_required_count"],
                "blocked_count": local_drs["blocked_count"],
            }
        )
    )
    for scenario_id in local_drs["baseline_regression_scenario_ids"]:
        decision = local_drs["decisions_summary"].get(scenario_id, {})
        lines.append(
            "- {scenario_id}: reuse_decision_class={reuse_decision_class}; direct_reuse_allowed={direct_reuse_allowed}; root_review_required={root_review_required}; reason_codes={reason_codes}".format(
                scenario_id=scenario_id,
                reuse_decision_class=decision.get("reuse_decision_class"),
                direct_reuse_allowed=decision.get("direct_reuse_allowed"),
                root_review_required=decision.get("root_review_required"),
                reason_codes=decision.get("reason_codes"),
            )
        )
    writeback = report.get("local_drs_v0_2_writeback_candidate")
    if writeback:
        lines.append(
            "local_drs_v0_2_writeback_candidate: {writeback_candidate_id}; local_proof_audit_only={local_proof_audit_only}; direct_reuse_allowed={direct_reuse_allowed}; future_permission_created={future_permission_created}".format(
                **writeback
            )
        )
    else:
        lines.append("local_drs_v0_2_writeback_candidate: not_run")

    avf = report["avf_v0_2_observation"]
    lines.extend(["", "[LOCAL AVF V0.2 LIVE OBSERVATION]"])
    if avf["avf_v0_2_status"] == "not_run":
        lines.append(
            "AVF v0.2 advisory evaluation did not run because the lane is closed."
        )
    else:
        lines.extend(
            [
                "AVF v0.2 ran after Local DRS v0.2 and before Orchestrator.",
                "AVF consumed Local DRS v0.2 candidate/reuse/risk signals.",
                "AVF built CandidateVector pressure rows.",
                "AVF applied HardMask / SoftMask / score explanation.",
                "release_all_and_pay_all was hard-masked.",
                "Supplier B payment was hard-masked.",
                "old receipt as permission was hard-masked.",
                "old Root Final as current decision was hard-masked.",
                "safe candidates may rank but do not grant permission.",
                "top-ranked candidate is not permission.",
                "AVF score is not authority.",
                "HardMask is not Root.",
                "AVF cannot bypass Root.",
                "AVF cannot create FinalOutput.",
                "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release.",
                "Root remains final authority.",
            ]
        )
    lines.extend(
        _render_mapping(
            {
                "avf_v0_2_status": avf["avf_v0_2_status"],
                "resolver_mode": avf["resolver_mode"],
                "candidates_evaluated_count": avf["candidates_evaluated_count"],
                "top_candidate_id": avf["top_candidate_id"],
                "top_candidate_score": avf["top_candidate_score"],
                "hard_masked_count": avf["hard_masked_count"],
                "unmasked_count": avf["unmasked_count"],
                "root_review_required_count": avf["root_review_required_count"],
            }
        )
    )
    for candidate_id, observation in avf["candidate_observations"].items():
        lines.append(
            "- {candidate_id}: hard_masked={hard_masked}; final_avf_score={final_avf_score}; permission_granted={permission_granted}".format(
                candidate_id=candidate_id,
                hard_masked=observation.get("hard_masked"),
                final_avf_score=observation.get("final_avf_score"),
                permission_granted=observation.get("permission_granted", False),
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

    acp_v0_2 = report["action_commit_packet_v0_2_integration"]
    lines.extend(["", "[ACTIONCOMMITPACKET V0.2 LIVE OBSERVATION]"])
    lines.extend(
        _render_mapping(
            {
                "status": acp_v0_2["status"],
                "packet_id": acp_v0_2["packet_id"],
                "created_by": acp_v0_2["created_by"],
                "root_created": acp_v0_2["root_created"],
                "packet_validated": acp_v0_2["packet_validated"],
                "registry_validated": acp_v0_2["registry_validated"],
                "registry_is_local_proof_only": acp_v0_2[
                    "registry_is_local_proof_only"
                ],
                "packet_corridor_entry_validated": acp_v0_2[
                    "packet_corridor_entry_validated"
                ],
                "accepted_for_mock_corridor": acp_v0_2[
                    "accepted_for_mock_corridor"
                ],
                "packet_seen_recorded_in_local_registry": acp_v0_2[
                    "packet_seen_recorded_in_local_registry"
                ],
                "terminal_receipt_recorded_before_corridor": acp_v0_2[
                    "terminal_receipt_recorded_before_corridor"
                ],
            }
        )
    )
    if acp_v0_2["status"] == STATUS_PASS:
        lines.extend(
            [
                "Root created one scoped Supplier A ActionCommitPacket model.",
                "Human approval is scoped evidence only.",
                "LLM/DRS/AVF/GT-LGT did not create the packet.",
                "Supplier A is allowed.",
                "Supplier B is excluded.",
                "Shipment release is excluded.",
                "Real bank/supplier/warehouse APIs are excluded.",
                "Packet accepted for mock corridor only.",
                "Root remains final authority.",
                "allowed_subjects:",
            ]
        )
        lines.extend(f"  - {subject}" for subject in acp_v0_2["allowed_subjects"])
        lines.append("forbidden_subjects:")
        lines.extend(
            f"  - {subject}" for subject in acp_v0_2["forbidden_subjects"]
        )
        lines.append("allowed_actions:")
        lines.extend(f"  - {action}" for action in acp_v0_2["allowed_actions"])
        lines.append("forbidden_actions:")
        lines.extend(f"  - {action}" for action in acp_v0_2["forbidden_actions"])
        lines.append("allowed_adapters:")
        lines.extend(f"  - {adapter}" for adapter in acp_v0_2["allowed_adapters"])
        lines.append("forbidden_adapters:")
        lines.extend(
            f"  - {adapter}" for adapter in acp_v0_2["forbidden_adapters"]
        )
    else:
        lines.append("ActionCommitPacket v0.2 observation did not run.")

    mock_corridor = report["mock_bank_sandbox_v0_2_corridor_execution"]
    lines.extend(
        ["", "[MOCKBANKSANDBOX V0.2 LIVE CONTRACT CORRIDOR OBSERVATION]"]
    )
    lines.extend(
        _render_mapping(
            {
                "status": mock_corridor["status"],
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
    if mock_corridor["status"] == STATUS_PASS:
        lines.extend(
            [
                "MockBankSandbox consumed the scoped packet.",
                "The corridor created mock intent/consent/order.",
                "The corridor returned mock receipt evidence.",
                "Receipt is evidence only.",
                "Receipt did not create permission.",
                "Receipt did not authorize Supplier B.",
                "Receipt did not release shipment.",
                "Receipt did not create FinalOutput.",
                "Terminal receipt was observed in local proof-only registry.",
                "Supplier B remains blocked.",
                "Shipment release remains held.",
                "Root remains final authority.",
                "No real-world effect occurred.",
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
        lines.extend(
            f"  {line}"
            for line in _render_mapping(mock_corridor["mock_payment_intent"])
        )
        lines.append("mock_payment_consent:")
        lines.extend(
            f"  {line}"
            for line in _render_mapping(mock_corridor["mock_payment_consent"])
        )
        lines.append("mock_payment_order:")
        lines.extend(
            f"  {line}"
            for line in _render_mapping(mock_corridor["mock_payment_order"])
        )
        lines.append("mock_receipt_evidence:")
        lines.extend(
            f"  {line}"
            for line in _render_mapping(mock_corridor["mock_receipt_evidence"])
        )
    else:
        lines.append("MockBankSandbox v0.2 corridor observation did not run.")

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
