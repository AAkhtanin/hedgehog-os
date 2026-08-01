from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass, replace
from decimal import Decimal
import hashlib
import inspect
import json
from pathlib import Path
import re
from typing import get_args, get_origin, get_type_hints

from jsonschema import Draft202012Validator
import pytest

import hedgehog.kernel as kernel
import hedgehog.kernel.execution_mode_router_v01 as router
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/execution_mode_router_v01.py"
KERNEL_INIT_PATH = ROOT / "hedgehog/kernel/__init__.py"
ABI_PATH = ROOT / "hedgehog/kernel/abi_v01.py"
TRANSITION_PATH = ROOT / "hedgehog/kernel/transition_registry_v01.py"
ROOT_DECISION_PATH = ROOT / "hedgehog/kernel/root_decision_v01.py"
SCHEMA_PATH = ROOT / "schemas/execution_mode_router_v01.schema.json"

REQUEST_ID = "request:g2c:c1:test"
TRANSACTION_ID = "transaction:g2c:c1:test"
ROOT_ID = "root:g2c:c1:test"
DOMAIN_ID = "G2C_C1_TEST_DOMAIN"
POLICY_ID = "policy:g2c:c1:test"
CAPABILITY_SNAPSHOT_ID = "capability-snapshot:g2c:c1:test"
COST_MODEL_ID = "cost-model:g2c:c1:test"
EVALUATION_TIME = 1767225600
ZERO_HASH = "0" * 64

TYPE_NAMES = (
    "ExecutionModeBSEPBindingV01",
    "ExecutionModeReplayBindingV01",
    "ExecutionModeG2ABindingV01",
    "ExecutionModeG2BBindingV01",
    "ExecutionModeLocalModeProfileV01",
    "ExecutionModeLocalRoutingSnapshotV01",
    "ExecutionModeRouterInputV01",
    "ExecutionModeFeasibilityRowV01",
    "ExecutionModeProposalV01",
    "RootExecutionModeReviewInputV01",
    "RootExecutionModeDecisionV01",
    "ExecutionModeValidationReportV01",
    "ExecutionModeSourceContextV01",
)
FIELD_NAMES = {
    "ExecutionModeBSEPBindingV01": (
        "bsep_binding_id", "binding_state", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "business_request_packet_id",
        "business_request_packet_sha256", "source_packet_id",
        "source_packet_sha256", "source_packet_type", "source_schema_version",
        "source_route_context_packet_id", "source_route_context_sha256",
        "source_route_id", "source_proposal_id", "source_proposal_sha256",
        "source_structured_rationale_ref", "source_structured_rationale_sha256",
        "source_family_sha256", "source_domain", "source_role", "target_role",
        "source_reason_codes", "root_final_authority_preserved",
        "authority_created", "permission_created", "action_commit_packet_created",
        "final_output_created", "real_world_effects_count",
    ),
    "ExecutionModeReplayBindingV01": (
        "replay_binding_id", "binding_state", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "replay_id", "source_replay_sha256",
        "replay_status", "source_manifest_id", "reconstructed_manifest_id",
        "anchor_publication_id", "anchored_verification_id",
        "source_domain_projection_id", "reconstructed_domain_projection_id",
        "package_id", "logical_package_ref", "source_package_content_hash",
        "reconstructed_package_content_hash", "integrity_verified",
        "continuity_verified", "anchor_verified", "evidence_refs",
        "authority_created", "permission_created", "action_commit_packet_created",
        "receipt_created", "final_output_created", "real_world_effects_count",
    ),
    "ExecutionModeG2ABindingV01": (
        "g2a_binding_id", "binding_state", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "source_inspection_sha256",
        "inspection_profile_id", "registry_id", "packet_id", "evaluation_time",
        "evaluation_time_source", "evaluation_context_id",
        "historical_lifecycle_state", "failed_provenance", "transition_event_count",
        "execution_attempt_count", "idempotency_disposition",
        "reservation_owner_packet_id", "terminal_receipt_ref", "lifecycle_terminal",
        "eligible_for_corridor_revalidation", "present_eligibility_status",
        "present_executable", "retry_eligible", "source_reason_codes",
        "transition_history_sha256", "disposition_history_sha256",
        "historical_result_unchanged", "authority_created", "permission_created",
        "packet_created", "receipt_created", "adapter_calls",
        "real_world_effects_count",
    ),
    "ExecutionModeG2BBindingV01": (
        "g2b_binding_id", "binding_state", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "report_id", "report_sha256",
        "semantic_address_id", "query_id", "query_evaluation_ids",
        "eligible_candidate_ids", "ranked_candidate_ids", "selected_candidate_id",
        "retrieval_plan_id", "memory_descent_result_id",
        "root_shortcut_projection_id", "reuse_certificate_id",
        "compatibility_projection_ids", "compatibility_projection_set_sha256",
        "use_time", "source_root_kernel_id", "source_root_decision_input_id",
        "source_root_decision_id", "source_root_decision_sha256", "freshness_state",
        "lineage_state", "quarantine_present", "deadend_present",
        "context_available", "direct_informational_reuse_eligible",
        "source_reason_codes", "persistent_records_unchanged", "authority_created",
        "permission_created", "action_commit_packet_created", "receipt_created",
        "capability_created", "topology_created", "final_output_created",
        "drs_write_created", "real_world_effects_count",
    ),
    "ExecutionModeLocalModeProfileV01": (
        "local_mode_profile_id", "request_id", "transaction_id", "owning_root_id",
        "domain_id", "mode", "policy_snapshot_id", "capability_snapshot_id",
        "cost_model_id", "policy_allowed", "scope_allowed", "risk_allowed",
        "privacy_allowed", "capability_state", "capability_id", "cost_unit",
        "cost_units", "local_reason_codes", "authority_created",
        "permission_created", "real_world_effects_count",
    ),
    "ExecutionModeLocalRoutingSnapshotV01": (
        "local_routing_snapshot_id", "created_by", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "request_class", "action_class",
        "action_packet_relation", "scope_class", "scope_ref",
        "permitted_narrower_scope_refs", "risk_class", "policy_snapshot_id",
        "capability_snapshot_id", "cost_model_id", "required_user_input_state",
        "hard_block_state", "evaluation_time_epoch_seconds", "pt_created_at_utc",
        "kt_asof_utc", "et_observed_at_utc", "ct_session_anchor", "ttl_seconds",
        "freshness_class", "valid_from_utc", "valid_to_utc", "time_envelope_ref",
        "mode_profile_set_id", "mode_profile_set_sha256", "mode_profiles",
        "authority_created", "permission_created", "real_world_effects_count",
    ),
    "ExecutionModeRouterInputV01": (
        "router_input_id", "request_id", "transaction_id", "owning_root_id",
        "bsep_binding", "local_routing_snapshot", "replay_binding", "g2a_binding",
        "g2b_binding", "trace_refs",
    ),
    "ExecutionModeFeasibilityRowV01": (
        "feasibility_row_id", "source_input_id", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "mode", "category", "safe_depth_rank",
        "feasibility_status", "local_mode_profile_id", "required_evidence_refs",
        "satisfied_evidence_refs", "missing_evidence_codes", "reason_codes",
        "required_capability_id", "cost_units", "downstream_compute_class",
        "root_review_required", "authority_created", "permission_created",
        "real_world_effects_count",
    ),
    "ExecutionModeProposalV01": (
        "proposal_id", "source_input_id", "request_id", "transaction_id",
        "owning_root_id", "domain_id", "source_bsep_binding_id",
        "source_bsep_packet_id", "source_bsep_sha256",
        "source_local_routing_snapshot_id", "source_replay_binding_id",
        "source_g2a_binding_id", "source_g2b_binding_id", "selected_mode",
        "selected_safe_depth_rank", "selected_local_mode_profile_id",
        "selected_expected_cost_units", "proposed_scope_ref",
        "ordered_feasibility_rows", "selected_feasibility_row_id", "reason_codes",
        "required_downstream_capability_ids", "downstream_consumption_class",
        "downstream_action_packet_required", "root_review_required",
        "authority_created", "permission_created", "action_commit_packet_created",
        "receipt_created", "topology_created", "final_output_created",
        "drs_write_created", "real_world_effects_count",
    ),
    "RootExecutionModeReviewInputV01": (
        "root_review_input_id", "request_id", "transaction_id", "owning_root_id",
        "domain_id", "proposal_id", "router_input_id", "proposal_artifact_id",
        "proposal_transition_decision_id", "created_by", "review_action",
        "proposed_mode", "proposed_scope_ref", "accepted_scope_ref",
        "scope_narrowing_proof_id", "narrowing_basis_refs", "policy_snapshot_id",
        "evaluation_time_epoch_seconds", "time_envelope_ref",
        "root_local_context_id", "trace_refs",
    ),
    "RootExecutionModeDecisionV01": (
        "decision_id", "root_review_input_id", "proposal_id", "router_input_id",
        "request_id", "transaction_id", "owning_root_id", "domain_id", "outcome",
        "accepted_mode", "accepted_scope_ref", "scope_narrowing_proof_id",
        "downstream_consumption_class", "downstream_action_packet_required",
        "source_root_decision_id", "source_root_decision_input_id",
        "source_root_decision", "source_root_reason_code",
        "source_root_transition_decision_id", "source_root_transition_decision",
        "reason_codes", "route_eligibility_candidate", "authority_created",
        "permission_created", "action_commit_packet_created", "receipt_created",
        "topology_created", "final_output_created", "drs_write_created",
        "real_world_effects_count",
    ),
    "ExecutionModeValidationReportV01": (
        "validation_report_id", "validation_target", "validated_artifact_id",
        "request_id", "transaction_id", "owning_root_id", "domain_id",
        "validation_status", "failure_stage", "return_to_root_required",
        "reason_codes", "source_reason_codes", "authority_created",
        "permission_created", "real_world_effects_count",
    ),
    "ExecutionModeSourceContextV01": (
        "business_request_context_packet", "bsep_packet",
        "bsep_route_context_packet", "bsep_orchestrator_proposal",
        "bsep_structured_rationale", "sealed_replay_evidence",
        "replay_source_manifest", "replay_source_domain_projection",
        "replay_source_safe_file_contents", "replay_anchor_publication",
        "replay_anchored_verification", "replay_supplied_anchor_publication_id",
        "replay_reconstructed_manifest", "replay_reconstructed_domain_projection",
        "replay_reconstructed_safe_file_contents", "g2a_inspection", "g2a_registry",
        "g2a_packet_id", "g2a_corridor", "g2a_corridor_step",
        "g2a_current_dependency_observations", "g2a_logical_time_bridge",
        "g2a_evaluation_time", "g2a_evaluation_time_source",
        "g2a_evaluation_context_id", "g2a_transition_registry_profile",
        "g2b_resolution_report", "g2b_compatibility_projections", "g2b_use_time",
        "g2b_root_kernel", "g2b_root_decision_input", "g2b_root_decision_result",
        "g2b_writeback_evidence",
    ),
}

C1_FUNCTIONS = (
    "validate_execution_mode_source_context_v01",
    "build_execution_mode_local_mode_profile_v01",
    "build_execution_mode_local_routing_snapshot_v01",
    "build_execution_mode_router_input_v01",
    "build_execution_mode_validation_report_v01",
    "validate_execution_mode_bsep_binding_v01",
    "execution_mode_bsep_binding_to_plain_data_v01",
    "rebuild_execution_mode_bsep_binding_identity_v01",
    "validate_execution_mode_replay_binding_v01",
    "execution_mode_replay_binding_to_plain_data_v01",
    "rebuild_execution_mode_replay_binding_identity_v01",
    "validate_execution_mode_g2a_binding_v01",
    "execution_mode_g2a_binding_to_plain_data_v01",
    "rebuild_execution_mode_g2a_binding_identity_v01",
    "validate_execution_mode_g2b_binding_v01",
    "execution_mode_g2b_binding_to_plain_data_v01",
    "rebuild_execution_mode_g2b_binding_identity_v01",
    "validate_execution_mode_local_mode_profile_v01",
    "execution_mode_local_mode_profile_to_plain_data_v01",
    "rebuild_execution_mode_local_mode_profile_identity_v01",
    "validate_execution_mode_local_routing_snapshot_v01",
    "execution_mode_local_routing_snapshot_to_plain_data_v01",
    "rebuild_execution_mode_local_routing_snapshot_identity_v01",
    "validate_execution_mode_router_input_v01",
    "execution_mode_router_input_to_plain_data_v01",
    "rebuild_execution_mode_router_input_identity_v01",
    "validate_execution_mode_feasibility_row_v01",
    "execution_mode_feasibility_row_to_plain_data_v01",
    "rebuild_execution_mode_feasibility_row_identity_v01",
    "validate_execution_mode_proposal_v01",
    "execution_mode_proposal_to_plain_data_v01",
    "rebuild_execution_mode_proposal_identity_v01",
    "validate_root_execution_mode_review_input_v01",
    "root_execution_mode_review_input_to_plain_data_v01",
    "rebuild_root_execution_mode_review_input_identity_v01",
    "validate_root_execution_mode_decision_v01",
    "root_execution_mode_decision_to_plain_data_v01",
    "rebuild_root_execution_mode_decision_identity_v01",
    "validate_execution_mode_validation_report_v01",
    "execution_mode_validation_report_to_plain_data_v01",
    "rebuild_execution_mode_validation_report_identity_v01",
)

PUBLIC_FUNCTIONS = (
    "build_execution_mode_source_context_v01",
    "validate_execution_mode_source_context_v01",
    "build_execution_mode_bsep_binding_v01",
    "build_execution_mode_replay_not_applicable_binding_v01",
    "build_execution_mode_replay_binding_v01",
    "build_execution_mode_g2a_no_packet_binding_v01",
    "build_execution_mode_g2a_binding_v01",
    "build_execution_mode_g2b_not_applicable_binding_v01",
    "build_execution_mode_g2b_binding_v01",
    "build_execution_mode_local_mode_profile_v01",
    "build_execution_mode_local_routing_snapshot_v01",
    "build_execution_mode_router_input_v01",
    "evaluate_execution_mode_feasibility_v01",
    "select_execution_mode_v01",
    "build_execution_mode_proposal_v01",
    "build_execution_mode_validation_report_v01",
    "build_root_execution_mode_review_input_v01",
    "build_execution_mode_root_decision_source_v01",
    "project_root_execution_mode_decision_v01",
    "route_execution_mode_v01",
    "review_execution_mode_proposal_v01",
    "validate_execution_mode_router_input_against_sources_v01",
    "validate_execution_mode_proposal_against_sources_v01",
    "validate_root_execution_mode_review_input_against_sources_v01",
    "validate_root_execution_mode_decision_against_source_v01",
    "validate_execution_mode_route_eligibility_against_source_v01",
    "project_execution_mode_proposal_kernel_artifact_v01",
    "project_root_execution_mode_decision_kernel_artifact_v01",
    "project_execution_mode_route_eligibility_kernel_artifact_v01",
    "validate_execution_mode_abi_profile_v01",
    "build_execution_mode_transition_registry_profile_v01",
    "validate_execution_mode_transition_registry_profile_v01",
    "execution_mode_transition_registry_profile_to_plain_dict_v01",
    "validate_execution_mode_transition_decision_v01",
    "execution_mode_transition_decision_to_plain_dict_v01",
    "rebuild_execution_mode_transition_decision_identity_v01",
    "evaluate_execution_mode_proposal_to_root_transition_v01",
    "evaluate_execution_mode_root_route_transition_v01",
    "validate_execution_mode_bsep_binding_v01",
    "execution_mode_bsep_binding_to_plain_data_v01",
    "rebuild_execution_mode_bsep_binding_identity_v01",
    "validate_execution_mode_replay_binding_v01",
    "execution_mode_replay_binding_to_plain_data_v01",
    "rebuild_execution_mode_replay_binding_identity_v01",
    "validate_execution_mode_g2a_binding_v01",
    "execution_mode_g2a_binding_to_plain_data_v01",
    "rebuild_execution_mode_g2a_binding_identity_v01",
    "validate_execution_mode_g2b_binding_v01",
    "execution_mode_g2b_binding_to_plain_data_v01",
    "rebuild_execution_mode_g2b_binding_identity_v01",
    "validate_execution_mode_local_mode_profile_v01",
    "execution_mode_local_mode_profile_to_plain_data_v01",
    "rebuild_execution_mode_local_mode_profile_identity_v01",
    "validate_execution_mode_local_routing_snapshot_v01",
    "execution_mode_local_routing_snapshot_to_plain_data_v01",
    "rebuild_execution_mode_local_routing_snapshot_identity_v01",
    "validate_execution_mode_router_input_v01",
    "execution_mode_router_input_to_plain_data_v01",
    "rebuild_execution_mode_router_input_identity_v01",
    "validate_execution_mode_feasibility_row_v01",
    "execution_mode_feasibility_row_to_plain_data_v01",
    "rebuild_execution_mode_feasibility_row_identity_v01",
    "validate_execution_mode_proposal_v01",
    "execution_mode_proposal_to_plain_data_v01",
    "rebuild_execution_mode_proposal_identity_v01",
    "validate_root_execution_mode_review_input_v01",
    "root_execution_mode_review_input_to_plain_data_v01",
    "rebuild_root_execution_mode_review_input_identity_v01",
    "validate_root_execution_mode_decision_v01",
    "root_execution_mode_decision_to_plain_data_v01",
    "rebuild_root_execution_mode_decision_identity_v01",
    "validate_execution_mode_validation_report_v01",
    "execution_mode_validation_report_to_plain_data_v01",
    "rebuild_execution_mode_validation_report_identity_v01",
)

PUBLIC_REASONS = (
    "g2c_exact_type_invalid", "g2c_scalar_invalid", "g2c_sequence_invalid",
    "g2c_identity_invalid", "g2c_identity_mismatch",
    "g2c_request_binding_mismatch", "g2c_transaction_binding_mismatch",
    "g2c_root_binding_mismatch", "g2c_domain_binding_mismatch",
    "g2c_time_envelope_invalid", "g2c_time_envelope_ref_identity_mismatch",
    "g2c_source_context_invalid", "g2c_source_context_structural_target_invalid",
    "g2c_source_object_absent", "g2c_source_object_substituted",
    "g2c_source_digest_mismatch", "g2c_source_validator_failed",
    "g2c_business_request_invalid", "g2c_business_request_ref_invalid",
    "g2c_route_context_invalid", "g2c_semantic_proposal_invalid",
    "g2c_structured_rationale_invalid", "g2c_bsep_invalid",
    "g2c_replay_binding_invalid", "g2c_g2a_relation_invalid",
    "g2c_g2a_present_inspection_invalid", "g2c_g2b_binding_invalid",
    "g2c_g2b_binding_state_derivation_mismatch",
    "g2c_g2b_query_transaction_mismatch", "g2c_g2b_shortcut_invalid",
    "g2c_g2b_use_time_invalid", "g2c_local_mode_profile_invalid",
    "g2c_local_mode_profile_set_invalid", "g2c_mode_profile_set_identity_mismatch",
    "g2c_policy_forbidden", "g2c_scope_forbidden", "g2c_risk_forbidden",
    "g2c_privacy_forbidden", "g2c_capability_unavailable", "g2c_cost_invalid",
    "g2c_noncanonical_mode", "g2c_required_evidence_missing",
    "g2c_action_shortcut_forbidden", "g2c_deterministic_feasible",
    "g2c_sealed_replay_feasible", "g2c_direct_informational_reuse_feasible",
    "g2c_memory_informed_feasible", "g2c_local_slm_feasible",
    "g2c_cloud_llm_feasible", "g2c_full_semantic_feasible",
    "g2c_full_fractal_feasible", "g2c_hard_block_present",
    "g2c_user_input_required", "g2c_no_safe_mode",
    "g2c_feasibility_row_invalid", "g2c_selection_invalid",
    "g2c_selection_tie_break_applied", "g2c_proposal_rows_invalid",
    "g2c_proposal_selected_row_mismatch", "g2c_proposal_sources_valid",
    "g2c_review_action_invalid", "g2c_terminal_review_mismatch",
    "g2c_scope_narrowing_invalid", "g2c_root_input_invalid",
    "g2c_root_result_invalid", "g2c_root_mapping_invalid",
    "g2c_policy_snapshot_binding_mismatch", "g2c_terminal_contribution_scope_mismatch",
    "g2c_root_accept_projected", "g2c_root_narrow_projected",
    "g2c_root_reject_projected", "g2c_root_blocked_projected",
    "g2c_root_needs_user_projected", "g2c_abi_profile_invalid",
    "g2c_abi_reserved_payload_key", "g2c_abi_artifact_identity_mismatch",
    "g2c_abi_parent_lineage_mismatch", "g2c_abi_bundle_validation_failed",
    "g2c_abi_projection_substituted", "g2c_transition_profile_invalid",
    "g2c_transition_registry_identity_mismatch", "g2c_transition_decision_invalid",
    "g2c_transition_decision_identity_mismatch",
    "g2c_transition_root_review_required", "g2c_transition_route_accept_allowed",
    "g2c_transition_scope_narrow_allowed", "g2c_transition_reject_recorded",
    "g2c_transition_blocked_recorded", "g2c_transition_needs_user_recorded",
    "g2c_transition_guard_invalid", "g2c_transition_root_commit_required",
    "g2c_transition_substituted", "g2c_proposal_transition_missing",
    "g2c_proposal_transition_substituted", "g2c_post_root_transition_missing",
    "g2c_post_root_transition_substituted", "g2c_route_eligibility_invalid",
    "g2c_route_decision_bypass_forbidden", "g2c_invalid_source_no_proposal",
    "g2c_fail_closed_return_to_root",
)

VALIDATION_TARGETS = (
    "ExecutionModeBSEPBindingV01", "ExecutionModeReplayBindingV01",
    "ExecutionModeG2ABindingV01", "ExecutionModeG2BBindingV01",
    "ExecutionModeLocalModeProfileV01", "ExecutionModeLocalRoutingSnapshotV01",
    "ExecutionModeRouterInputV01", "ExecutionModeFeasibilityRowV01",
    "ExecutionModeProposalV01", "RootExecutionModeReviewInputV01",
    "RootExecutionModeDecisionV01", "ExecutionModeValidationReportV01",
    "SOURCE_CONTEXT_STRUCTURAL", "ROUTER_INPUT_AGAINST_SOURCES",
    "PROPOSAL_AGAINST_SOURCES", "ROOT_REVIEW_AGAINST_SOURCES",
    "ROOT_DECISION_AGAINST_SOURCE", "ROUTE_ELIGIBILITY_AGAINST_SOURCE",
    "ABI_PROFILE", "TRANSITION_PROFILE",
)

FAILURE_STAGES = (
    "NONE", "STRUCTURAL", "SOURCE_CONTEXT", "BUSINESS_REQUEST", "BSEP",
    "REPLAY", "G2A", "G2B", "LOCAL_PROFILE", "TIME_ENVELOPE",
    "FEASIBILITY", "SELECTION", "PROPOSAL", "ROOT_REVIEW", "ROOT_DECISION",
    "ABI", "TRANSITION", "ROUTE_ELIGIBILITY",
)

IDENTITY_PROFILES = (
    ("ExecutionModeBSEPBindingV01", "bsep_binding_id", "HEDGEHOG_EXECUTION_MODE_BSEP_BINDING_V01", "embsep_v01:"),
    ("ExecutionModeReplayBindingV01", "replay_binding_id", "HEDGEHOG_EXECUTION_MODE_REPLAY_BINDING_V01", "emreplay_v01:"),
    ("ExecutionModeG2ABindingV01", "g2a_binding_id", "HEDGEHOG_EXECUTION_MODE_G2A_BINDING_V01", "emg2a_v01:"),
    ("ExecutionModeG2BBindingV01", "g2b_binding_id", "HEDGEHOG_EXECUTION_MODE_G2B_BINDING_V01", "emg2b_v01:"),
    ("ExecutionModeLocalModeProfileV01", "local_mode_profile_id", "HEDGEHOG_EXECUTION_MODE_LOCAL_MODE_PROFILE_V01", "emprofile_v01:"),
    ("ExecutionModeLocalRoutingSnapshotV01", "local_routing_snapshot_id", "HEDGEHOG_EXECUTION_MODE_LOCAL_ROUTING_SNAPSHOT_V01", "emlocal_v01:"),
    ("ExecutionModeRouterInputV01", "router_input_id", "HEDGEHOG_EXECUTION_MODE_ROUTER_INPUT_V01", "eminput_v01:"),
    ("ExecutionModeFeasibilityRowV01", "feasibility_row_id", "HEDGEHOG_EXECUTION_MODE_FEASIBILITY_ROW_V01", "emrow_v01:"),
    ("ExecutionModeProposalV01", "proposal_id", "HEDGEHOG_EXECUTION_MODE_PROPOSAL_V01", "emproposal_v01:"),
    ("RootExecutionModeReviewInputV01", "root_review_input_id", "HEDGEHOG_ROOT_EXECUTION_MODE_REVIEW_INPUT_V01", "emreview_v01:"),
    ("RootExecutionModeDecisionV01", "decision_id", "HEDGEHOG_ROOT_EXECUTION_MODE_DECISION_V01", "emdecision_v01:"),
    ("ExecutionModeValidationReportV01", "validation_report_id", "HEDGEHOG_EXECUTION_MODE_VALIDATION_REPORT_V01", "emvalidation_v01:"),
)

C1_SIGNATURES = {
    "validate_execution_mode_source_context_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "build_execution_mode_local_mode_profile_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', mode: 'str', policy_snapshot_id: 'str', capability_snapshot_id: 'str', cost_model_id: 'str', policy_allowed: 'bool', scope_allowed: 'bool', risk_allowed: 'bool', privacy_allowed: 'bool', capability_state: 'str', capability_id: 'str | None', cost_units: 'int') -> 'ExecutionModeLocalModeProfileV01'",
    "build_execution_mode_local_routing_snapshot_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', request_class: 'str', action_class: 'str', action_packet_relation: 'str', scope_class: 'str', scope_ref: 'str', permitted_narrower_scope_refs: 'tuple[str, ...]', risk_class: 'str', policy_snapshot_id: 'str', capability_snapshot_id: 'str', cost_model_id: 'str', required_user_input_state: 'str', hard_block_state: 'str', evaluation_time_epoch_seconds: 'int', pt_created_at_utc: 'str', et_observed_at_utc: 'str', ct_session_anchor: 'str', ttl_seconds: 'int', freshness_class: 'str', valid_from_utc: 'str', valid_to_utc: 'str', mode_profiles: 'tuple[ExecutionModeLocalModeProfileV01, ...]') -> 'ExecutionModeLocalRoutingSnapshotV01'",
    "build_execution_mode_router_input_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', bsep_binding: 'ExecutionModeBSEPBindingV01', local_routing_snapshot: 'ExecutionModeLocalRoutingSnapshotV01', replay_binding: 'ExecutionModeReplayBindingV01', g2a_binding: 'ExecutionModeG2ABindingV01', g2b_binding: 'ExecutionModeG2BBindingV01') -> 'ExecutionModeRouterInputV01'",
    "build_execution_mode_validation_report_v01": "(*, validation_target: 'str', validated_artifact_id: 'str | None', request_id: 'str | None', transaction_id: 'str | None', owning_root_id: 'str | None', domain_id: 'str | None', validation_status: 'str', failure_stage: 'str', return_to_root_required: 'bool', reason_codes: 'tuple[str, ...]', source_reason_codes: 'tuple[str, ...]') -> 'ExecutionModeValidationReportV01'",
    "validate_execution_mode_bsep_binding_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_bsep_binding_to_plain_data_v01": "(value: 'ExecutionModeBSEPBindingV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_bsep_binding_identity_v01": "(value: 'ExecutionModeBSEPBindingV01') -> 'str'",
    "validate_execution_mode_replay_binding_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_replay_binding_to_plain_data_v01": "(value: 'ExecutionModeReplayBindingV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_replay_binding_identity_v01": "(value: 'ExecutionModeReplayBindingV01') -> 'str'",
    "validate_execution_mode_g2a_binding_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_g2a_binding_to_plain_data_v01": "(value: 'ExecutionModeG2ABindingV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_g2a_binding_identity_v01": "(value: 'ExecutionModeG2ABindingV01') -> 'str'",
    "validate_execution_mode_g2b_binding_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_g2b_binding_to_plain_data_v01": "(value: 'ExecutionModeG2BBindingV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_g2b_binding_identity_v01": "(value: 'ExecutionModeG2BBindingV01') -> 'str'",
    "validate_execution_mode_local_mode_profile_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_local_mode_profile_to_plain_data_v01": "(value: 'ExecutionModeLocalModeProfileV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_local_mode_profile_identity_v01": "(value: 'ExecutionModeLocalModeProfileV01') -> 'str'",
    "validate_execution_mode_local_routing_snapshot_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_local_routing_snapshot_to_plain_data_v01": "(value: 'ExecutionModeLocalRoutingSnapshotV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_local_routing_snapshot_identity_v01": "(value: 'ExecutionModeLocalRoutingSnapshotV01') -> 'str'",
    "validate_execution_mode_router_input_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_router_input_to_plain_data_v01": "(value: 'ExecutionModeRouterInputV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_router_input_identity_v01": "(value: 'ExecutionModeRouterInputV01') -> 'str'",
    "validate_execution_mode_feasibility_row_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_feasibility_row_to_plain_data_v01": "(value: 'ExecutionModeFeasibilityRowV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_feasibility_row_identity_v01": "(value: 'ExecutionModeFeasibilityRowV01') -> 'str'",
    "validate_execution_mode_proposal_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "execution_mode_proposal_to_plain_data_v01": "(value: 'ExecutionModeProposalV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_proposal_identity_v01": "(value: 'ExecutionModeProposalV01') -> 'str'",
    "validate_root_execution_mode_review_input_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "root_execution_mode_review_input_to_plain_data_v01": "(value: 'RootExecutionModeReviewInputV01') -> 'dict[str, object]'",
    "rebuild_root_execution_mode_review_input_identity_v01": "(value: 'RootExecutionModeReviewInputV01') -> 'str'",
    "validate_root_execution_mode_decision_v01": "(value: 'object') -> 'ExecutionModeValidationReportV01'",
    "root_execution_mode_decision_to_plain_data_v01": "(value: 'RootExecutionModeDecisionV01') -> 'dict[str, object]'",
    "rebuild_root_execution_mode_decision_identity_v01": "(value: 'RootExecutionModeDecisionV01') -> 'str'",
    "validate_execution_mode_validation_report_v01": "(value: 'object') -> 'tuple[str, ...]'",
    "execution_mode_validation_report_to_plain_data_v01": "(value: 'ExecutionModeValidationReportV01') -> 'dict[str, object]'",
    "rebuild_execution_mode_validation_report_identity_v01": "(value: 'ExecutionModeValidationReportV01') -> 'str'",
}

TYPE_HINT_LABELS = {
    "ExecutionModeBSEPBindingV01":
        ("str",) * 23 + ("str_tuple",) + ("bool",) * 5 + ("int",),
    "ExecutionModeReplayBindingV01":
        ("str",) * 6 + ("opt_str",) * 2 + ("str",) + ("opt_str",) * 10
        + ("bool",) * 3 + ("str_tuple",) + ("bool",) * 5 + ("int",),
    "ExecutionModeG2ABindingV01":
        ("str",) * 6 + ("opt_str",) * 4 + ("int",) + ("str",) * 3
        + ("opt_str",) + ("int",) * 2 + ("str",) + ("opt_str",) * 2
        + ("bool",) * 2 + ("str",) + ("bool",) * 2 + ("str_tuple",)
        + ("opt_str",) * 2
        + ("bool",) * 5 + ("int",) * 2,
    "ExecutionModeG2BBindingV01":
        ("str",) * 6 + ("opt_str",) * 4 + ("str_tuple",) * 3
        + ("opt_str",) * 5 + ("str_tuple",) + ("opt_str",) + ("opt_int",)
        + ("opt_str",) * 4 + ("str",) * 2 + ("bool",) * 4
        + ("str_tuple",) + ("bool",) * 9 + ("int",),
    "ExecutionModeLocalModeProfileV01":
        ("str",) * 9 + ("bool",) * 4 + ("str", "opt_str", "str", "int",
        "str_tuple") + ("bool",) * 2 + ("int",),
    "ExecutionModeLocalRoutingSnapshotV01":
        ("str",) * 11 + ("str_tuple",) + ("str",) * 6
        + ("int",) + ("str",) * 4 + ("int",)
        + ("str",) * 6 + ("profile_tuple",) + ("bool",) * 2 + ("int",),
    "ExecutionModeRouterInputV01": (
        "str", "str", "str", "str", "bsep", "snapshot", "replay", "g2a",
        "g2b", "str_tuple",
    ),
    "ExecutionModeFeasibilityRowV01":
        ("str",) * 8 + ("opt_int", "str", "opt_str") + ("str_tuple",) * 4
        + ("opt_str", "opt_int", "str") + ("bool",) * 3 + ("int",),
    "ExecutionModeProposalV01":
        ("str",) * 14 + ("opt_int", "opt_str", "opt_int", "opt_str", "row_tuple",
        "str", "str_tuple", "str_tuple", "str") + ("bool",) * 9 + ("int",),
    "RootExecutionModeReviewInputV01":
        ("str",) * 12 + ("opt_str",) * 3 + ("str_tuple", "str", "int", "str",
        "str", "str_tuple"),
    "RootExecutionModeDecisionV01":
        ("str",) * 9 + ("opt_str",) * 3 + ("str", "bool") + ("str",) * 6
        + ("str_tuple",) + ("bool",) * 8 + ("int",),
    "ExecutionModeValidationReportV01":
        ("str",) * 2 + ("opt_str",) * 5 + ("str",) * 2 + ("bool",)
        + ("str_tuple",) * 2 + ("bool",) * 2 + ("int",),
    "ExecutionModeSourceContextV01": (
        "dict", "dict", "dict", "dict", "dict", "opt_sealed_replay",
        "opt_manifest", "opt_projection", "bytes_tuple", "opt_anchor_publication",
        "opt_anchor_verification", "opt_str", "opt_manifest", "opt_projection",
        "bytes_tuple", "opt_g2a_inspection", "opt_g2a_registry", "opt_str",
        "opt_corridor", "opt_corridor_step", "observation_tuple", "opt_time_bridge",
        "opt_int", "opt_str", "opt_str", "opt_action_transition_profile",
        "opt_resolution_report", "compatibility_tuple", "opt_int", "opt_root_kernel",
        "opt_root_input", "opt_root_result", "none_type",
    ),
}

TYPE_HINT_TYPES = {
    "str": str,
    "opt_str": str | None,
    "int": int,
    "opt_int": int | None,
    "bool": bool,
    "str_tuple": tuple[str, ...],
    "bytes_tuple": tuple[bytes, ...],
    "dict": dict[str, object],
    "bsep": router.ExecutionModeBSEPBindingV01,
    "replay": router.ExecutionModeReplayBindingV01,
    "g2a": router.ExecutionModeG2ABindingV01,
    "g2b": router.ExecutionModeG2BBindingV01,
    "snapshot": router.ExecutionModeLocalRoutingSnapshotV01,
    "profile_tuple": tuple[router.ExecutionModeLocalModeProfileV01, ...],
    "row_tuple": tuple[router.ExecutionModeFeasibilityRowV01, ...],
    "opt_sealed_replay": router.SealedReplayEvidenceV01 | None,
    "opt_manifest": router.SealedPackageManifestV01 | None,
    "opt_projection": router.DomainEvidenceProjectionV01 | None,
    "opt_anchor_publication": router.ExternalAnchorPublicationV01 | None,
    "opt_anchor_verification": router.AnchoredPackageVerificationV01 | None,
    "opt_g2a_inspection": router.ActionPacketPresentEligibilityInspectionV01 | None,
    "opt_g2a_registry": router.ActionCommitPacketRegistryV02 | None,
    "opt_corridor": router.ContractFulfillmentCorridorV01 | None,
    "opt_corridor_step": router.CorridorStepV01 | None,
    "observation_tuple": tuple[router.ActionDependencyCurrentObservationV01, ...],
    "opt_time_bridge": router.LogicalTimeBridgeV01 | None,
    "opt_action_transition_profile": router.ActionPacketTransitionRegistryProfileV01 | None,
    "opt_resolution_report": router.DRSResolutionReportV01 | None,
    "compatibility_tuple": tuple[router.LegacyDRSProjectionV01, ...],
    "opt_root_kernel": router.RootDecisionKernelV01 | None,
    "opt_root_input": router.RootDecisionInputV01 | None,
    "opt_root_result": router.RootDecisionResultV01 | None,
    "none_type": type(None),
}


def _with_identity(value: object, field_name: str, rebuilder: object) -> object:
    return replace(value, **{field_name: rebuilder(value)})


def _profiles() -> tuple[router.ExecutionModeLocalModeProfileV01, ...]:
    values = []
    for index, mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01):
        not_required = mode in {"sealed_replay", "direct_informational_reuse"}
        values.append(
            router.build_execution_mode_local_mode_profile_v01(
                request_id=REQUEST_ID,
                transaction_id=TRANSACTION_ID,
                owning_root_id=ROOT_ID,
                domain_id=DOMAIN_ID,
                mode=mode,
                policy_snapshot_id=POLICY_ID,
                capability_snapshot_id=CAPABILITY_SNAPSHOT_ID,
                cost_model_id=COST_MODEL_ID,
                policy_allowed=True,
                scope_allowed=True,
                risk_allowed=True,
                privacy_allowed=True,
                capability_state="NOT_REQUIRED" if not_required else "AVAILABLE",
                capability_id=None if not_required else f"capability:g2c:{mode}",
                cost_units=index + 1,
            )
        )
    return tuple(values)


def _snapshot() -> router.ExecutionModeLocalRoutingSnapshotV01:
    return router.build_execution_mode_local_routing_snapshot_v01(
        request_id=REQUEST_ID,
        transaction_id=TRANSACTION_ID,
        owning_root_id=ROOT_ID,
        domain_id=DOMAIN_ID,
        request_class="INFORMATION",
        action_class="NON_ACTION",
        action_packet_relation="NOT_APPLICABLE",
        scope_class="BOUNDED",
        scope_ref="scope:g2c:c1:test",
        permitted_narrower_scope_refs=("scope:g2c:c1:test:narrow",),
        risk_class="LOW",
        policy_snapshot_id=POLICY_ID,
        capability_snapshot_id=CAPABILITY_SNAPSHOT_ID,
        cost_model_id=COST_MODEL_ID,
        required_user_input_state="COMPLETE",
        hard_block_state="CLEAR",
        evaluation_time_epoch_seconds=EVALUATION_TIME,
        pt_created_at_utc="2026-01-01T00:00:00+00:00",
        et_observed_at_utc="2026-01-01T00:00:00+00:00",
        ct_session_anchor="session:g2c:c1:test",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc="2026-01-01T00:00:00+00:00",
        valid_to_utc="2026-01-01T01:00:00+00:00",
        mode_profiles=_profiles(),
    )


def _bindings(snapshot: router.ExecutionModeLocalRoutingSnapshotV01) -> tuple[object, ...]:
    bsep = router.ExecutionModeBSEPBindingV01(
        "embsep_v01:" + ZERO_HASH, "BOUNDED_SEMANTIC_EVIDENCE_BOUND",
        REQUEST_ID, TRANSACTION_ID, ROOT_ID, DOMAIN_ID, "packet:business:g2c:c1",
        "1" * 64, "packet:bsep:g2c:c1", "2" * 64,
        "BoundedSemanticEvidencePacket", "bounded_semantic_evidence_packet_v0.1",
        "packet:route:g2c:c1", "3" * 64, "route:g2c:c1",
        "proposal:source:g2c:c1", "4" * 64, "rationale:g2c:c1", "5" * 64,
        router._bsep_source_family_sha256(
            business_request_packet_sha256="1" * 64,
            source_route_context_sha256="3" * 64,
            source_proposal_sha256="4" * 64,
            source_structured_rationale_sha256="5" * 64,
            source_packet_sha256="2" * 64,
        ),
        DOMAIN_ID, "orchestrator", "architect", (), True, False,
        False, False, False, 0,
    )
    bsep = _with_identity(
        bsep, "bsep_binding_id", router.rebuild_execution_mode_bsep_binding_identity_v01
    )
    replay = router.ExecutionModeReplayBindingV01(
        "emreplay_v01:" + ZERO_HASH, "NOT_APPLICABLE", REQUEST_ID,
        TRANSACTION_ID, ROOT_ID, DOMAIN_ID, None, None, "NOT_APPLICABLE",
        None, None, None, None, None, None, None, None, None, None, False,
        False, False, (), False, False, False, False, False, 0,
    )
    replay = _with_identity(
        replay, "replay_binding_id", router.rebuild_execution_mode_replay_binding_identity_v01
    )
    g2a = router.ExecutionModeG2ABindingV01(
        "emg2a_v01:" + ZERO_HASH, "NO_PACKET", REQUEST_ID, TRANSACTION_ID,
        ROOT_ID, DOMAIN_ID, None, None, None, None, EVALUATION_TIME,
        "OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01", snapshot.local_routing_snapshot_id,
        "NO_PACKET", None, 0, 0, "NOT_APPLICABLE", None, None, False, False,
        "NOT_APPLICABLE", False, False, (), None, None, True, False, False,
        False, False, 0, 0,
    )
    g2a = _with_identity(g2a, "g2a_binding_id", router.rebuild_execution_mode_g2a_binding_identity_v01)
    g2b = router.ExecutionModeG2BBindingV01(
        g2b_binding_id="emg2b_v01:" + ZERO_HASH,
        binding_state="NOT_APPLICABLE", request_id=REQUEST_ID,
        transaction_id=TRANSACTION_ID, owning_root_id=ROOT_ID, domain_id=DOMAIN_ID,
        report_id=None, report_sha256=None, semantic_address_id=None, query_id=None,
        query_evaluation_ids=(), eligible_candidate_ids=(), ranked_candidate_ids=(),
        selected_candidate_id=None, retrieval_plan_id=None,
        memory_descent_result_id=None, root_shortcut_projection_id=None,
        reuse_certificate_id=None, compatibility_projection_ids=(),
        compatibility_projection_set_sha256=None, use_time=None,
        source_root_kernel_id=None, source_root_decision_input_id=None,
        source_root_decision_id=None, source_root_decision_sha256=None,
        freshness_state="NOT_APPLICABLE", lineage_state="NOT_APPLICABLE",
        quarantine_present=False, deadend_present=False, context_available=False,
        direct_informational_reuse_eligible=False, source_reason_codes=(),
        persistent_records_unchanged=True, authority_created=False,
        permission_created=False, action_commit_packet_created=False,
        receipt_created=False, capability_created=False, topology_created=False,
        final_output_created=False, drs_write_created=False,
        real_world_effects_count=0,
    )
    g2b = _with_identity(g2b, "g2b_binding_id", router.rebuild_execution_mode_g2b_binding_identity_v01)
    return bsep, replay, g2a, g2b


def _serialized_fixtures() -> tuple[object, ...]:
    snapshot = _snapshot()
    bsep, replay, g2a, g2b = _bindings(snapshot)
    router_input = router.build_execution_mode_router_input_v01(
        request_id=REQUEST_ID, transaction_id=TRANSACTION_ID,
        owning_root_id=ROOT_ID, bsep_binding=bsep,
        local_routing_snapshot=snapshot, replay_binding=replay,
        g2a_binding=g2a, g2b_binding=g2b,
    )
    rows = []
    ranks = dict(router.EXECUTION_MODE_SAFE_DEPTH_RANKS_V01)
    computes = ("NONE", "NONE", "NONE", "MEMORY_INFORMED", "LOCAL_SLM",
                "CLOUD_LLM", "FULL_SEMANTIC", "FULL_FRACTAL")
    positive = (
        "g2c_deterministic_feasible", "g2c_sealed_replay_feasible",
        "g2c_direct_informational_reuse_feasible", "g2c_memory_informed_feasible",
        "g2c_local_slm_feasible", "g2c_cloud_llm_feasible",
        "g2c_full_semantic_feasible", "g2c_full_fractal_feasible",
    )
    for index, mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01):
        profile = snapshot.mode_profiles[index]
        feasible = index == 0
        required = (bsep.bsep_binding_id, snapshot.local_routing_snapshot_id,
                    profile.local_mode_profile_id)
        row = router.ExecutionModeFeasibilityRowV01(
            "emrow_v01:" + ZERO_HASH, router_input.router_input_id, REQUEST_ID,
            TRANSACTION_ID, ROOT_ID, DOMAIN_ID, mode, "EXECUTABLE", ranks[mode],
            "FEASIBLE" if feasible else "INFEASIBLE", profile.local_mode_profile_id,
            required, required if feasible else required[:2],
            () if feasible else ("g2c_capability_unavailable",),
            (positive[index],) if feasible else ("g2c_capability_unavailable",),
            profile.capability_id, profile.cost_units, computes[index], True, False,
            False, 0,
        )
        rows.append(_with_identity(row, "feasibility_row_id", router.rebuild_execution_mode_feasibility_row_identity_v01))
    for mode in ("blocked", "needs_user"):
        row = router.ExecutionModeFeasibilityRowV01(
            "emrow_v01:" + ZERO_HASH, router_input.router_input_id, REQUEST_ID,
            TRANSACTION_ID, ROOT_ID, DOMAIN_ID, mode, "TERMINAL", None,
            "TERMINAL_NOT_SELECTED", None, (bsep.bsep_binding_id,
            snapshot.local_routing_snapshot_id), (), (), (), None, None,
            "TERMINAL", True, False, False, 0,
        )
        rows.append(_with_identity(row, "feasibility_row_id", router.rebuild_execution_mode_feasibility_row_identity_v01))
    proposal = router.ExecutionModeProposalV01(
        "emproposal_v01:" + ZERO_HASH, router_input.router_input_id, REQUEST_ID,
        TRANSACTION_ID, ROOT_ID, DOMAIN_ID, bsep.bsep_binding_id,
        bsep.source_packet_id, bsep.source_packet_sha256,
        snapshot.local_routing_snapshot_id, replay.replay_binding_id,
        g2a.g2a_binding_id, g2b.g2b_binding_id, "deterministic", 10,
        snapshot.mode_profiles[0].local_mode_profile_id,
        snapshot.mode_profiles[0].cost_units, snapshot.scope_ref, tuple(rows),
        rows[0].feasibility_row_id, ("g2c_proposal_sources_valid",),
        (snapshot.mode_profiles[0].capability_id,), "SHORTCUT_RETURN_TO_ROOT",
        False, True, False, False, False, False, False, False, False, 0,
    )
    proposal = _with_identity(proposal, "proposal_id", router.rebuild_execution_mode_proposal_identity_v01)
    review_traces = tuple(sorted(("emabi_proposal_v01:" + "7" * 64,
                                  "8" * 64, proposal.proposal_id,
                                  router_input.router_input_id, "emrootctx_v01:" + "9" * 64)))
    review = router.RootExecutionModeReviewInputV01(
        "emreview_v01:" + ZERO_HASH, REQUEST_ID, TRANSACTION_ID, ROOT_ID,
        DOMAIN_ID, proposal.proposal_id, router_input.router_input_id,
        "emabi_proposal_v01:" + "7" * 64, "8" * 64,
        "OWNING_LOCAL_ROOT_EXECUTION_MODE_REVIEW_V01", "ACCEPT",
        "deterministic", snapshot.scope_ref, snapshot.scope_ref, None, (),
        POLICY_ID, EVALUATION_TIME, snapshot.time_envelope_ref,
        "emrootctx_v01:" + "9" * 64, review_traces,
    )
    review = _with_identity(review, "root_review_input_id", router.rebuild_root_execution_mode_review_input_identity_v01)
    decision = router.RootExecutionModeDecisionV01(
        "emdecision_v01:" + ZERO_HASH, review.root_review_input_id,
        proposal.proposal_id, router_input.router_input_id, REQUEST_ID,
        TRANSACTION_ID, ROOT_ID, DOMAIN_ID, "ACCEPT", "deterministic",
        snapshot.scope_ref, None, "SHORTCUT_RETURN_TO_ROOT", False,
        "a" * 64, "b" * 64, "ACCEPT", "validated_candidate_accepted",
        "c" * 64, "RETURN_TO_ROOT", ("g2c_root_accept_projected",), True,
        False, False, False, False, False, False, False, 0,
    )
    decision = _with_identity(decision, "decision_id", router.rebuild_root_execution_mode_decision_identity_v01)
    report = router.build_execution_mode_validation_report_v01(
        validation_target="ExecutionModeBSEPBindingV01",
        validated_artifact_id=bsep.bsep_binding_id, request_id=REQUEST_ID,
        transaction_id=TRANSACTION_ID, owning_root_id=ROOT_ID,
        domain_id=DOMAIN_ID, validation_status="PASS", failure_stage="NONE",
        return_to_root_required=False, reason_codes=(), source_reason_codes=(),
    )
    return (bsep, replay, g2a, g2b, *snapshot.mode_profiles[:1], snapshot,
            router_input, rows[0], proposal, review, decision, report)


def _source_context() -> router.ExecutionModeSourceContextV01:
    return router.ExecutionModeSourceContextV01(
        business_request_context_packet={}, bsep_packet={},
        bsep_route_context_packet={}, bsep_orchestrator_proposal={},
        bsep_structured_rationale={}, sealed_replay_evidence=None,
        replay_source_manifest=None, replay_source_domain_projection=None,
        replay_source_safe_file_contents=(), replay_anchor_publication=None,
        replay_anchored_verification=None, replay_supplied_anchor_publication_id=None,
        replay_reconstructed_manifest=None, replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(), g2a_inspection=None,
        g2a_registry=None, g2a_packet_id=None, g2a_corridor=None,
        g2a_corridor_step=None, g2a_current_dependency_observations=(),
        g2a_logical_time_bridge=None, g2a_evaluation_time=EVALUATION_TIME,
        g2a_evaluation_time_source="OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01",
        g2a_evaluation_context_id="emlocal_v01:" + "1" * 64,
        g2a_transition_registry_profile=None, g2b_resolution_report=None,
        g2b_compatibility_projections=(), g2b_use_time=None,
        g2b_root_kernel=None, g2b_root_decision_input=None,
        g2b_root_decision_result=None, g2b_writeback_evidence=None,
    )


SERIALIZED_STEMS = {
    router.ExecutionModeBSEPBindingV01: "execution_mode_bsep_binding",
    router.ExecutionModeReplayBindingV01: "execution_mode_replay_binding",
    router.ExecutionModeG2ABindingV01: "execution_mode_g2a_binding",
    router.ExecutionModeG2BBindingV01: "execution_mode_g2b_binding",
    router.ExecutionModeLocalModeProfileV01: "execution_mode_local_mode_profile",
    router.ExecutionModeLocalRoutingSnapshotV01: "execution_mode_local_routing_snapshot",
    router.ExecutionModeRouterInputV01: "execution_mode_router_input",
    router.ExecutionModeFeasibilityRowV01: "execution_mode_feasibility_row",
    router.ExecutionModeProposalV01: "execution_mode_proposal",
    router.RootExecutionModeReviewInputV01: "root_execution_mode_review_input",
    router.RootExecutionModeDecisionV01: "root_execution_mode_decision",
    router.ExecutionModeValidationReportV01: "execution_mode_validation_report",
}


def _rebuild_fixture_identity(value: object) -> object:
    stem = SERIALIZED_STEMS[type(value)]
    identity_field = fields(type(value))[0].name
    rebuilder = getattr(router, f"rebuild_{stem}_identity_v01")
    return replace(value, **{identity_field: rebuilder(value)})


def _serialized_result_reasons(value: object) -> tuple[str, ...]:
    stem = SERIALIZED_STEMS[type(value)]
    result = getattr(router, f"validate_{stem}_v01")(value)
    if type(value) is router.ExecutionModeValidationReportV01:
        return result
    return result.reason_codes


def _assert_serialized_passes_python_and_schema(value: object) -> None:
    stem = SERIALIZED_STEMS[type(value)]
    result = getattr(router, f"validate_{stem}_v01")(value)
    if type(value) is router.ExecutionModeValidationReportV01:
        assert result == ()
    else:
        assert result.validation_status == "PASS", result.reason_codes
    plain = getattr(router, f"{stem}_to_plain_data_v01")(value)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["$ref"] = f"#/$defs/{type(value).__name__}"
    Draft202012Validator(schema).validate(plain)
    identity_field = fields(type(value))[0].name
    assert getattr(router, f"rebuild_{stem}_identity_v01")(value) == getattr(
        value, identity_field
    )
    assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
        getattr(router, f"{stem}_to_plain_data_v01")(value)
    )


def _state_variant_fixtures() -> dict[str, object]:
    base = _serialized_fixtures()
    replay_absent = base[1]
    g2a_absent = base[2]
    g2b_absent = base[3]
    review_accept = base[9]
    decision_accept = base[10]

    replay_bound = _rebuild_fixture_identity(
        replace(
            replay_absent,
            binding_state="SEALED_REPLAY_BOUND",
            replay_id="replay:g2c:c1:bound",
            source_replay_sha256="a" * 64,
            replay_status="PASS",
            source_manifest_id="manifest:g2c:c1:source",
            reconstructed_manifest_id="manifest:g2c:c1:reconstructed",
            anchor_publication_id="anchor:g2c:c1:publication",
            anchored_verification_id="anchor:g2c:c1:verification",
            source_domain_projection_id="projection:g2c:c1:source",
            reconstructed_domain_projection_id="projection:g2c:c1:reconstructed",
            package_id="package:g2c:c1:bound",
            logical_package_ref="logical-package:g2c:c1:bound",
            source_package_content_hash="b" * 64,
            reconstructed_package_content_hash="c" * 64,
            integrity_verified=True,
            continuity_verified=True,
            anchor_verified=True,
            evidence_refs=("evidence:g2c:c1:bound",),
        )
    )
    g2a_present = _rebuild_fixture_identity(
        replace(
            g2a_absent,
            binding_state="PRESENT_INSPECTION_BOUND",
            source_inspection_sha256="d" * 64,
            inspection_profile_id="inspection:g2c:c1:present",
            registry_id="registry:g2c:c1:present",
            packet_id="packet:g2c:c1:present",
            historical_lifecycle_state="COMMITTED",
            transition_event_count=2,
            execution_attempt_count=1,
            idempotency_disposition="FIRST_EXECUTION",
            reservation_owner_packet_id="packet:g2c:c1:reservation",
            terminal_receipt_ref="receipt:g2c:c1:terminal",
            lifecycle_terminal=True,
            eligible_for_corridor_revalidation=True,
            present_eligibility_status="ELIGIBLE",
            present_executable=True,
            transition_history_sha256="e" * 64,
            disposition_history_sha256="f" * 64,
        )
    )
    g2b_context = _rebuild_fixture_identity(
        replace(
            g2b_absent,
            binding_state="RESOLUTION_CONTEXT_BOUND",
            report_id="report:g2c:c1:context",
            report_sha256="1" * 64,
            semantic_address_id="semantic-address:g2c:c1:context",
            query_id=TRANSACTION_ID,
            query_evaluation_ids=("query-evaluation:g2c:c1:context",),
            retrieval_plan_id="retrieval-plan:g2c:c1:context",
            memory_descent_result_id="memory-descent:g2c:c1:context",
            compatibility_projection_ids=("compatibility:g2c:c1:context",),
            compatibility_projection_set_sha256="2" * 64,
            use_time=EVALUATION_TIME,
            freshness_state="STALE",
            lineage_state="VALIDATED",
            context_available=True,
        )
    )
    g2b_direct = _rebuild_fixture_identity(
        replace(
            g2b_absent,
            binding_state="DIRECT_REUSE_BOUND",
            report_id="report:g2c:c1:direct",
            report_sha256="3" * 64,
            semantic_address_id="semantic-address:g2c:c1:direct",
            query_id=TRANSACTION_ID,
            query_evaluation_ids=("query-evaluation:g2c:c1:direct",),
            eligible_candidate_ids=("candidate:g2c:c1:direct",),
            ranked_candidate_ids=("candidate:g2c:c1:direct",),
            selected_candidate_id="candidate:g2c:c1:direct",
            retrieval_plan_id="retrieval-plan:g2c:c1:direct",
            memory_descent_result_id="memory-descent:g2c:c1:direct",
            root_shortcut_projection_id="shortcut:g2c:c1:direct",
            reuse_certificate_id="certificate:g2c:c1:direct",
            compatibility_projection_ids=("compatibility:g2c:c1:direct",),
            compatibility_projection_set_sha256="4" * 64,
            use_time=EVALUATION_TIME,
            source_root_kernel_id="5" * 64,
            source_root_decision_input_id="6" * 64,
            source_root_decision_id="7" * 64,
            source_root_decision_sha256="8" * 64,
            freshness_state="CURRENT",
            lineage_state="VALIDATED",
            context_available=True,
            direct_informational_reuse_eligible=True,
        )
    )
    review_narrow = _rebuild_fixture_identity(
        replace(
            review_accept,
            review_action="NARROW",
            accepted_scope_ref="scope:g2c:c1:test:narrow",
            scope_narrowing_proof_id="proof:g2c:c1:narrow",
            narrowing_basis_refs=("basis:g2c:c1:narrow",),
        )
    )
    review_terminal = _rebuild_fixture_identity(
        replace(
            review_accept,
            review_action="TERMINAL_FROM_PROPOSAL",
            proposed_mode="blocked",
            proposed_scope_ref=None,
            accepted_scope_ref=None,
        )
    )

    def decision_variant(**changes: object) -> object:
        return _rebuild_fixture_identity(replace(decision_accept, **changes))

    decision_narrow = decision_variant(
        outcome="NARROW",
        accepted_scope_ref="scope:g2c:c1:test:narrow",
        scope_narrowing_proof_id="proof:g2c:c1:narrow",
        reason_codes=("g2c_root_narrow_projected",),
    )
    decision_reject = decision_variant(
        outcome="REJECT", accepted_mode=None, accepted_scope_ref=None,
        downstream_consumption_class="TERMINAL_NO_CONSUMPTION",
        source_root_decision="REJECT", source_root_reason_code="policy_rejected_candidate",
        reason_codes=("g2c_root_reject_projected",), route_eligibility_candidate=False,
    )
    decision_blocked = decision_variant(
        outcome="BLOCKED", accepted_mode=None, accepted_scope_ref=None,
        downstream_consumption_class="TERMINAL_NO_CONSUMPTION",
        source_root_decision="BLOCKED_FAIL_CLOSED",
        source_root_reason_code="hard_policy_violation",
        reason_codes=("g2c_root_blocked_projected",), route_eligibility_candidate=False,
    )
    decision_needs_user = decision_variant(
        outcome="NEEDS_USER", accepted_mode=None, accepted_scope_ref=None,
        downstream_consumption_class="TERMINAL_NO_CONSUMPTION",
        source_root_decision="NEEDS_USER",
        source_root_reason_code="user_permission_missing",
        reason_codes=("g2c_root_needs_user_projected",), route_eligibility_candidate=False,
    )
    return {
        "replay_not_applicable": replay_absent,
        "replay_bound": replay_bound,
        "g2a_no_packet": g2a_absent,
        "g2a_present": g2a_present,
        "g2b_not_applicable": g2b_absent,
        "g2b_context": g2b_context,
        "g2b_direct": g2b_direct,
        "review_accept": review_accept,
        "review_narrow": review_narrow,
        "review_terminal": review_terminal,
        "decision_accept": decision_accept,
        "decision_narrow": decision_narrow,
        "decision_reject": decision_reject,
        "decision_blocked": decision_blocked,
        "decision_needs_user": decision_needs_user,
    }


PARITY_FIELDS = (
    ("g2a_present", "evaluation_context_id", "invalid identity", "g2c_identity_invalid"),
    ("g2a_present", "reservation_owner_packet_id", "invalid identity", "g2c_identity_invalid"),
    ("g2a_present", "terminal_receipt_ref", "invalid identity", "g2c_identity_invalid"),
    ("g2b_context", "report_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_context", "semantic_address_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_context", "retrieval_plan_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_context", "memory_descent_result_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_direct", "root_shortcut_projection_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_direct", "reuse_certificate_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_direct", "source_root_kernel_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_direct", "source_root_decision_input_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_direct", "source_root_decision_id", "invalid identity", "g2c_identity_invalid"),
    ("g2b_context", "report_sha256", "G" * 64, "g2c_source_digest_mismatch"),
    (
        "g2b_context", "compatibility_projection_set_sha256", "G" * 64,
        "g2c_source_digest_mismatch",
    ),
    ("g2b_direct", "source_root_decision_sha256", "G" * 64, "g2c_source_digest_mismatch"),
    ("g2b_context", "use_time", 2**63, "g2c_g2b_use_time_invalid"),
    ("profile", "policy_snapshot_id", "invalid identity", "g2c_identity_invalid"),
    ("profile", "capability_snapshot_id", "invalid identity", "g2c_identity_invalid"),
    ("profile", "cost_model_id", "invalid identity", "g2c_identity_invalid"),
    ("snapshot", "scope_ref", "invalid identity", "g2c_identity_invalid"),
    ("feasibility", "source_input_id", "invalid identity", "g2c_identity_invalid"),
    ("feasibility", "required_capability_id", "invalid identity", "g2c_identity_invalid"),
    ("proposal", "source_bsep_binding_id", "invalid identity", "g2c_identity_invalid"),
    ("proposal", "source_bsep_packet_id", "invalid identity", "g2c_identity_invalid"),
    (
        "proposal", "source_local_routing_snapshot_id", "invalid identity",
        "g2c_identity_invalid",
    ),
    ("proposal", "source_replay_binding_id", "invalid identity", "g2c_identity_invalid"),
    ("proposal", "source_g2a_binding_id", "invalid identity", "g2c_identity_invalid"),
    ("proposal", "source_g2b_binding_id", "invalid identity", "g2c_identity_invalid"),
    ("review_narrow", "proposal_id", "invalid identity", "g2c_identity_invalid"),
    ("review_narrow", "router_input_id", "invalid identity", "g2c_identity_invalid"),
    ("review_narrow", "proposal_artifact_id", "invalid identity", "g2c_identity_invalid"),
    (
        "review_narrow", "proposal_transition_decision_id", "invalid identity",
        "g2c_identity_invalid",
    ),
    ("review_narrow", "proposed_scope_ref", "invalid identity", "g2c_identity_invalid"),
    ("review_narrow", "accepted_scope_ref", "invalid identity", "g2c_identity_invalid"),
    (
        "review_narrow", "scope_narrowing_proof_id", "invalid identity",
        "g2c_identity_invalid",
    ),
    ("review_narrow", "root_local_context_id", "invalid identity", "g2c_identity_invalid"),
    ("review_narrow", "policy_snapshot_id", "invalid identity", "g2c_identity_invalid"),
    (
        "review_narrow", "time_envelope_ref", "emtime_v01:" + "G" * 64,
        "g2c_time_envelope_ref_identity_mismatch",
    ),
    ("decision_narrow", "root_review_input_id", "invalid identity", "g2c_identity_invalid"),
    ("decision_narrow", "proposal_id", "invalid identity", "g2c_identity_invalid"),
    ("decision_narrow", "router_input_id", "invalid identity", "g2c_identity_invalid"),
    ("decision_narrow", "accepted_scope_ref", "invalid identity", "g2c_identity_invalid"),
    (
        "decision_narrow", "scope_narrowing_proof_id", "invalid identity",
        "g2c_identity_invalid",
    ),
    ("report", "validated_artifact_id", "invalid identity", "g2c_identity_invalid"),
)


def test_exact_type_geometry_and_frozen_dataclasses():
    assert tuple(item.__name__ for item in router.G2C_TYPES_V01) == TYPE_NAMES
    assert tuple(item.__name__ for item in router.SERIALIZED_G2C_TYPES_V01) == TYPE_NAMES[:12]
    assert router.TOTAL_G2C_TYPE_COUNT == 13
    assert router.SERIALIZED_IDENTITY_TYPE_COUNT == 12
    assert router.RUNTIME_ONLY_SOURCE_CONTEXT_TYPE_COUNT == 1
    assert router.ROUTER_INPUT_FIELD_COUNT == 10
    assert router.ROOT_REVIEW_INPUT_FIELD_COUNT == 21
    assert router.ROOT_DECISION_FIELD_COUNT == 30
    for cls in router.G2C_TYPES_V01:
        assert is_dataclass(cls)
        assert cls.__dataclass_params__.frozen is True
        assert tuple(item.name for item in fields(cls)) == FIELD_NAMES[cls.__name__]
        expected = tuple(TYPE_HINT_TYPES[label] for label in TYPE_HINT_LABELS[cls.__name__])
        hints = get_type_hints(cls)
        assert tuple(hints[item.name] for item in fields(cls)) == expected


def test_exact_public_registries_and_c1_staging():
    assert router.PUBLIC_G2C_FUNCTIONS_V01 == PUBLIC_FUNCTIONS
    assert len(router.PUBLIC_G2C_FUNCTIONS_V01) == 74
    assert len(set(router.PUBLIC_G2C_FUNCTIONS_V01)) == 74
    assert router.PUBLIC_G2C_REASON_CODES_V01 == PUBLIC_REASONS
    assert len(router.PUBLIC_G2C_REASON_CODES_V01) == 100
    assert len(set(router.PUBLIC_G2C_REASON_CODES_V01)) == 100
    assert all(re.fullmatch(r"g2c_[a-z0-9_]{1,124}", item) and len(item) <= 128
               for item in router.PUBLIC_G2C_REASON_CODES_V01)
    assert router.CANONICAL_EXECUTION_MODES_V01 == (
        "deterministic", "sealed_replay", "direct_informational_reuse",
        "memory_informed", "local_slm", "cloud_llm", "full_semantic",
        "full_fractal", "blocked", "needs_user",
    )
    assert router.EXECUTABLE_EXECUTION_MODES_V01 == router.CANONICAL_EXECUTION_MODES_V01[:8]
    assert router.VALIDATION_TARGETS_V01 == VALIDATION_TARGETS
    assert router.FAILURE_STAGES_V01 == FAILURE_STAGES
    assert router.G2C_IDENTITY_PROFILES_V01 == IDENTITY_PROFILES
    actual = tuple(name for name in router.PUBLIC_G2C_FUNCTIONS_V01
                   if callable(getattr(router, name, None)))
    assert actual == C1_FUNCTIONS
    assert len(actual) == 41
    assert all(not hasattr(router, name) for name in router.PUBLIC_G2C_FUNCTIONS_V01
               if name not in C1_FUNCTIONS)


def test_bsep_family_digest_recomputed_and_wrong_well_formed_digest_rejected():
    values = tuple(str(index) * 64 for index in range(1, 6))
    kwargs = dict(zip(router.BSEP_SOURCE_FAMILY_SHA256_FIELDS_V01, values, strict=True))
    expected = hashlib.sha256(canonical_json_bytes_v01(kwargs)).hexdigest()
    assert router.BSEP_SOURCE_FAMILY_SHA256_FIELDS_V01 == (
        "business_request_packet_sha256",
        "source_route_context_sha256",
        "source_proposal_sha256",
        "source_structured_rationale_sha256",
        "source_packet_sha256",
    )
    assert router._bsep_source_family_sha256(**kwargs) == expected
    with pytest.raises(ValueError, match="^g2c_source_digest_mismatch$"):
        router._bsep_source_family_sha256(
            **{**kwargs, "source_packet_sha256": "not-a-sha"}
        )
    valid = _serialized_fixtures()[0]
    assert router.validate_execution_mode_bsep_binding_v01(valid).validation_status == "PASS"
    wrong = replace(valid, source_family_sha256="f" * 64)
    wrong = _rebuild_fixture_identity(wrong)
    report = router.validate_execution_mode_bsep_binding_v01(wrong)
    assert report.validation_status == "FAIL_CLOSED"
    assert "g2c_source_digest_mismatch" in report.reason_codes


def test_c1_signatures_are_keyword_bounded_and_derived_fields_are_absent():
    profile = inspect.signature(router.build_execution_mode_local_mode_profile_v01)
    snapshot = inspect.signature(router.build_execution_mode_local_routing_snapshot_v01)
    router_input = inspect.signature(router.build_execution_mode_router_input_v01)
    assert "local_reason_codes" not in profile.parameters
    assert "kt_asof_utc" not in snapshot.parameters
    assert "time_envelope_ref" not in snapshot.parameters
    assert "mode_profile_set_id" not in snapshot.parameters
    assert "mode_profile_set_sha256" not in snapshot.parameters
    assert "trace_refs" not in router_input.parameters
    assert tuple(C1_SIGNATURES) == C1_FUNCTIONS
    for name, expected in C1_SIGNATURES.items():
        assert str(inspect.signature(getattr(router, name))) == expected


def test_all_serialized_fixtures_validate_serialize_rebuild_and_match_schema():
    fixtures = _serialized_fixtures()
    assert len(fixtures) == 12
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert tuple(schema["$defs"]) == TYPE_NAMES[:12]
    assert len(schema["$defs"]) == 12
    assert "ExecutionModeSourceContextV01" not in schema["$defs"]
    for value in fixtures:
        stem = {
            "ExecutionModeBSEPBindingV01": "execution_mode_bsep_binding",
            "ExecutionModeReplayBindingV01": "execution_mode_replay_binding",
            "ExecutionModeG2ABindingV01": "execution_mode_g2a_binding",
            "ExecutionModeG2BBindingV01": "execution_mode_g2b_binding",
            "ExecutionModeLocalModeProfileV01": "execution_mode_local_mode_profile",
            "ExecutionModeLocalRoutingSnapshotV01": "execution_mode_local_routing_snapshot",
            "ExecutionModeRouterInputV01": "execution_mode_router_input",
            "ExecutionModeFeasibilityRowV01": "execution_mode_feasibility_row",
            "ExecutionModeProposalV01": "execution_mode_proposal",
            "RootExecutionModeReviewInputV01": "root_execution_mode_review_input",
            "RootExecutionModeDecisionV01": "root_execution_mode_decision",
            "ExecutionModeValidationReportV01": "execution_mode_validation_report",
        }[type(value).__name__]
        validator = getattr(router, f"validate_{stem}_v01")
        serializer = getattr(router, f"{stem}_to_plain_data_v01")
        rebuilder = getattr(router, f"rebuild_{stem}_identity_v01")
        result = validator(value)
        assert result == () if type(value) is router.ExecutionModeValidationReportV01 else result.validation_status == "PASS"
        plain = serializer(value)
        canonical_json_bytes_v01(plain)
        fixture_schema = dict(schema)
        fixture_schema["$ref"] = f"#/$defs/{type(value).__name__}"
        Draft202012Validator(fixture_schema).validate(plain)
        identity_name = fields(type(value))[0].name
        assert rebuilder(value) == getattr(value, identity_name)
        assert list(plain) == [item.name for item in fields(type(value))]


def test_scalar_exact_type_unicode_integer_and_tuple_rejection():
    profile = _profiles()[0]
    class ProfileSubclass(router.ExecutionModeLocalModeProfileV01):
        pass
    subclass = ProfileSubclass(**{f.name: getattr(profile, f.name) for f in fields(profile)})
    assert router.validate_execution_mode_local_mode_profile_v01(subclass).validation_status == "FAIL_CLOSED"
    for cost in (True, -1, 2**63, 0.5, Decimal("1")):
        with pytest.raises(ValueError):
            router.build_execution_mode_local_mode_profile_v01(
                request_id=REQUEST_ID, transaction_id=TRANSACTION_ID,
                owning_root_id=ROOT_ID, domain_id=DOMAIN_ID, mode="deterministic",
                policy_snapshot_id=POLICY_ID,
                capability_snapshot_id=CAPABILITY_SNAPSHOT_ID,
                cost_model_id=COST_MODEL_ID, policy_allowed=True,
                scope_allowed=True, risk_allowed=True, privacy_allowed=True,
                capability_state="AVAILABLE", capability_id="capability:g2c:test",
                cost_units=cost,
            )
    for bad in ("bad\x00value", "bad\u0085value", "e\u0301", "\ud800"):
        with pytest.raises(ValueError):
            router.build_execution_mode_local_mode_profile_v01(
                request_id=bad, transaction_id=TRANSACTION_ID,
                owning_root_id=ROOT_ID, domain_id=DOMAIN_ID, mode="deterministic",
                policy_snapshot_id=POLICY_ID,
                capability_snapshot_id=CAPABILITY_SNAPSHOT_ID,
                cost_model_id=COST_MODEL_ID, policy_allowed=True,
                scope_allowed=True, risk_allowed=True, privacy_allowed=True,
                capability_state="AVAILABLE", capability_id="capability:g2c:test",
                cost_units=1,
            )
    snapshot = _snapshot()
    assert router.validate_execution_mode_local_routing_snapshot_v01(
        replace(snapshot, permitted_narrower_scope_refs=list(snapshot.permitted_narrower_scope_refs))
    ).validation_status == "FAIL_CLOSED"


def test_local_profile_reason_derivation_and_capability_geometry():
    profile = router.build_execution_mode_local_mode_profile_v01(
        request_id=REQUEST_ID, transaction_id=TRANSACTION_ID,
        owning_root_id=ROOT_ID, domain_id=DOMAIN_ID, mode="local_slm",
        policy_snapshot_id=POLICY_ID,
        capability_snapshot_id=CAPABILITY_SNAPSHOT_ID, cost_model_id=COST_MODEL_ID,
        policy_allowed=False, scope_allowed=False, risk_allowed=False,
        privacy_allowed=False, capability_state="UNAVAILABLE",
        capability_id="capability:g2c:local", cost_units=7,
    )
    assert profile.local_reason_codes == (
        "g2c_policy_forbidden", "g2c_scope_forbidden", "g2c_risk_forbidden",
        "g2c_privacy_forbidden", "g2c_capability_unavailable",
    )
    with pytest.raises(ValueError):
        router.build_execution_mode_local_mode_profile_v01(
            request_id=REQUEST_ID, transaction_id=TRANSACTION_ID,
            owning_root_id=ROOT_ID, domain_id=DOMAIN_ID, mode="local_slm",
            policy_snapshot_id=POLICY_ID,
            capability_snapshot_id=CAPABILITY_SNAPSHOT_ID, cost_model_id=COST_MODEL_ID,
            policy_allowed=True, scope_allowed=True, risk_allowed=True,
            privacy_allowed=True, capability_state="NOT_REQUIRED",
            capability_id=None, cost_units=1,
        )


def test_snapshot_time_profile_set_and_router_trace_derivation():
    first = _snapshot()
    second = _snapshot()
    assert first == second
    assert first.kt_asof_utc == "2026-01-01T00:00:00+00:00"
    assert re.fullmatch(r"emtime_v01:[0-9a-f]{64}", first.time_envelope_ref)
    assert re.fullmatch(r"emprofiles_v01:[0-9a-f]{64}", first.mode_profile_set_id)
    assert re.fullmatch(r"[0-9a-f]{64}", first.mode_profile_set_sha256)
    assert router.validate_execution_mode_local_routing_snapshot_v01(
        replace(first, mode_profiles=tuple(reversed(first.mode_profiles)))
    ).validation_status == "FAIL_CLOSED"
    assert router.validate_execution_mode_local_routing_snapshot_v01(
        replace(first, mode_profiles=(first.mode_profiles[0],) * 8)
    ).validation_status == "FAIL_CLOSED"
    assert router.validate_execution_mode_local_routing_snapshot_v01(
        replace(first, ttl_seconds=3599)
    ).validation_status == "FAIL_CLOSED"
    assert router.validate_execution_mode_local_routing_snapshot_v01(
        replace(first, mode_profile_set_sha256="f" * 64)
    ).validation_status == "FAIL_CLOSED"
    bsep, replay, g2a, g2b = _bindings(first)
    value = router.build_execution_mode_router_input_v01(
        request_id=REQUEST_ID, transaction_id=TRANSACTION_ID,
        owning_root_id=ROOT_ID, bsep_binding=bsep,
        local_routing_snapshot=first, replay_binding=replay,
        g2a_binding=g2a, g2b_binding=g2b,
    )
    expected = tuple(sorted({bsep.business_request_packet_id, bsep.bsep_binding_id,
                             first.local_routing_snapshot_id, replay.replay_binding_id,
                             g2a.g2a_binding_id, g2b.g2b_binding_id}))
    assert value.trace_refs == expected
    with pytest.raises(ValueError):
        router.build_execution_mode_router_input_v01(
            request_id="request:g2c:other", transaction_id=TRANSACTION_ID,
            owning_root_id=ROOT_ID, bsep_binding=bsep,
            local_routing_snapshot=first, replay_binding=replay,
            g2a_binding=g2a, g2b_binding=g2b,
        )


def test_source_context_structural_boundary_and_total_report_geometry():
    value = _source_context()
    report = router.validate_execution_mode_source_context_v01(value)
    assert report.validation_status == "PASS"
    assert report.validation_target == "SOURCE_CONTEXT_STRUCTURAL"
    assert (report.validated_artifact_id, report.request_id, report.transaction_id,
            report.owning_root_id, report.domain_id) == (None, None, None, None, None)
    assert router.validate_execution_mode_source_context_v01(object()).validation_status == "FAIL_CLOSED"
    partial = replace(value, replay_supplied_anchor_publication_id="anchor:g2c:partial")
    assert router.validate_execution_mode_source_context_v01(partial).validation_status == "FAIL_CLOSED"
    partial_root = replace(value, g2b_root_kernel=object())
    assert router.validate_execution_mode_source_context_v01(partial_root).validation_status == "FAIL_CLOSED"
    hostile = replace(value, business_request_context_packet={"client": object()})
    assert router.validate_execution_mode_source_context_v01(hostile).validation_status == "FAIL_CLOSED"


def test_source_context_complete_replay_g2a_and_g2b_structural_shapes():
    value = _source_context()

    class DictSubclass(dict):
        pass

    assert router.validate_execution_mode_source_context_v01(
        replace(value, bsep_packet=DictSubclass())
    ).validation_status == "FAIL_CLOSED"

    replay = replace(
        value,
        sealed_replay_evidence=object.__new__(router.SealedReplayEvidenceV01),
        replay_source_manifest=object.__new__(router.SealedPackageManifestV01),
        replay_source_domain_projection=object.__new__(router.DomainEvidenceProjectionV01),
        replay_source_safe_file_contents=(b"source",),
        replay_anchor_publication=object.__new__(router.ExternalAnchorPublicationV01),
        replay_anchored_verification=object.__new__(router.AnchoredPackageVerificationV01),
        replay_supplied_anchor_publication_id="anchor:g2c:c1:test",
        replay_reconstructed_manifest=object.__new__(router.SealedPackageManifestV01),
        replay_reconstructed_domain_projection=object.__new__(router.DomainEvidenceProjectionV01),
        replay_reconstructed_safe_file_contents=(b"reconstructed",),
    )
    assert router.validate_execution_mode_source_context_v01(replay).validation_status == "PASS"
    assert router.validate_execution_mode_source_context_v01(
        replace(replay, replay_anchor_publication=None)
    ).validation_status == "FAIL_CLOSED"

    g2a = replace(
        value,
        g2a_inspection=object.__new__(router.ActionPacketPresentEligibilityInspectionV01),
        g2a_registry=object.__new__(router.ActionCommitPacketRegistryV02),
        g2a_packet_id="packet:g2c:c1:test",
        g2a_corridor=object.__new__(router.ContractFulfillmentCorridorV01),
        g2a_corridor_step=object.__new__(router.CorridorStepV01),
        g2a_current_dependency_observations=(
            object.__new__(router.ActionDependencyCurrentObservationV01),
        ),
        g2a_logical_time_bridge=object.__new__(router.LogicalTimeBridgeV01),
        g2a_transition_registry_profile=object.__new__(
            router.ActionPacketTransitionRegistryProfileV01
        ),
    )
    assert router.validate_execution_mode_source_context_v01(g2a).validation_status == "PASS"
    assert router.validate_execution_mode_source_context_v01(
        replace(g2a, g2a_corridor_step=None)
    ).validation_status == "FAIL_CLOSED"

    projection = object.__new__(router.LegacyDRSProjectionV01)
    context_bound = replace(
        value,
        g2b_resolution_report=object.__new__(router.DRSResolutionReportV01),
        g2b_compatibility_projections=(projection,),
        g2b_use_time=EVALUATION_TIME,
    )
    assert router.validate_execution_mode_source_context_v01(context_bound).validation_status == "PASS"
    direct_bound = replace(
        context_bound,
        g2b_root_kernel=object.__new__(router.RootDecisionKernelV01),
        g2b_root_decision_input=object.__new__(router.RootDecisionInputV01),
        g2b_root_decision_result=object.__new__(router.RootDecisionResultV01),
    )
    assert router.validate_execution_mode_source_context_v01(direct_bound).validation_status == "PASS"
    assert router.validate_execution_mode_source_context_v01(
        replace(direct_bound, g2b_root_decision_result=None)
    ).validation_status == "FAIL_CLOSED"


def test_validation_report_pass_fail_all_or_none_and_total_validator():
    passed = router.build_execution_mode_validation_report_v01(
        validation_target="SOURCE_CONTEXT_STRUCTURAL", validated_artifact_id=None,
        request_id=None, transaction_id=None, owning_root_id=None, domain_id=None,
        validation_status="PASS", failure_stage="NONE",
        return_to_root_required=False, reason_codes=(), source_reason_codes=(),
    )
    failed = router.build_execution_mode_validation_report_v01(
        validation_target="SOURCE_CONTEXT_STRUCTURAL", validated_artifact_id=None,
        request_id=None, transaction_id=None, owning_root_id=None, domain_id=None,
        validation_status="FAIL_CLOSED", failure_stage="SOURCE_CONTEXT",
        return_to_root_required=True, reason_codes=("g2c_source_context_invalid",),
        source_reason_codes=(),
    )
    assert router.validate_execution_mode_validation_report_v01(passed) == ()
    assert router.validate_execution_mode_validation_report_v01(failed) == ()
    assert router.validate_execution_mode_validation_report_v01(object())
    with pytest.raises(ValueError):
        router.build_execution_mode_validation_report_v01(
            validation_target="ExecutionModeBSEPBindingV01",
            validated_artifact_id="embsep_v01:" + "1" * 64,
            request_id=REQUEST_ID, transaction_id=None, owning_root_id=ROOT_ID,
            domain_id=DOMAIN_ID, validation_status="PASS", failure_stage="NONE",
            return_to_root_required=False, reason_codes=(), source_reason_codes=(),
        )


def test_validation_report_schema_nullability_parity():
    ordinary = _serialized_fixtures()[11]
    source_pass = router.build_execution_mode_validation_report_v01(
        validation_target="SOURCE_CONTEXT_STRUCTURAL", validated_artifact_id=None,
        request_id=None, transaction_id=None, owning_root_id=None, domain_id=None,
        validation_status="PASS", failure_stage="NONE",
        return_to_root_required=False, reason_codes=(), source_reason_codes=(),
    )
    source_fail = router.validate_execution_mode_source_context_v01(object())
    for report in (ordinary, source_pass, source_fail):
        _assert_serialized_passes_python_and_schema(report)
    partial = replace(source_pass, request_id=REQUEST_ID)
    partial = _rebuild_fixture_identity(partial)
    assert "g2c_identity_invalid" in router.validate_execution_mode_validation_report_v01(
        partial
    )


def test_bound_state_serialized_variants_python_schema_parity():
    variants = _state_variant_fixtures()
    assert tuple(variants) == (
        "replay_not_applicable", "replay_bound", "g2a_no_packet", "g2a_present",
        "g2b_not_applicable", "g2b_context", "g2b_direct", "review_accept",
        "review_narrow", "review_terminal", "decision_accept", "decision_narrow",
        "decision_reject", "decision_blocked", "decision_needs_user",
    )
    for value in variants.values():
        _assert_serialized_passes_python_and_schema(value)
    source_pass = router.validate_execution_mode_source_context_v01(_source_context())
    source_fail = router.validate_execution_mode_source_context_v01(object())
    assert source_pass.validation_status == "PASS"
    assert source_fail.validation_status == "FAIL_CLOSED"
    _assert_serialized_passes_python_and_schema(source_pass)
    _assert_serialized_passes_python_and_schema(source_fail)


def test_exact_44_field_python_schema_parity():
    base = _serialized_fixtures()
    variants = _state_variant_fixtures()
    fixtures = {
        **variants,
        "profile": base[4],
        "snapshot": base[5],
        "feasibility": base[7],
        "proposal": base[8],
        "report": base[11],
    }
    assert len(PARITY_FIELDS) == 44
    assert len(router._STRUCTURAL_FIELD_SHAPE_RULES_V01) == 44
    assert tuple((rule[0].__name__, rule[1]) for rule in router._STRUCTURAL_FIELD_SHAPE_RULES_V01) == tuple(
        (type(fixtures[key]).__name__, field_name)
        for key, field_name, _bad_value, _reason in PARITY_FIELDS
    )
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for fixture_key, field_name, bad_value, expected_reason in PARITY_FIELDS:
        value = fixtures[fixture_key]
        mutated = _rebuild_fixture_identity(replace(value, **{field_name: bad_value}))
        reasons = _serialized_result_reasons(mutated)
        assert expected_reason in reasons, (fixture_key, field_name, reasons)
        unchecked_plain = router._plain_data_unchecked(mutated)
        field_schema = dict(schema)
        field_schema["$ref"] = f"#/$defs/{type(mutated).__name__}"
        assert list(Draft202012Validator(field_schema).iter_errors(unchecked_plain)), (
            fixture_key,
            field_name,
        )


def _annotation_valid_mutation(value: object, annotation: object, field_name: str) -> object:
    origin = get_origin(annotation)
    if origin is type(str | None):
        non_none = next(item for item in get_args(annotation) if item is not type(None))
        if value is None:
            return 1 if non_none is int else f"mutation:{field_name}"
        return _annotation_valid_mutation(value, non_none, field_name)
    if annotation is str:
        return f"{value}:mutation"
    if annotation is int:
        return value + 1
    if annotation is bool:
        return not value
    if origin is tuple:
        item_type = get_args(annotation)[0]
        if value:
            if item_type is str:
                return value + (f"mutation:{field_name}",)
            return value + (value[0],)
        if item_type is str:
            return (f"mutation:{field_name}",)
        raise AssertionError((field_name, annotation))
    if is_dataclass(value):
        nested_identity = fields(type(value))[0].name
        return replace(
            value,
            **{nested_identity: f"{getattr(value, nested_identity)}:mutation"},
        )
    raise AssertionError((field_name, annotation, value))


def test_identity_participation_for_every_serialized_field():
    for value in _serialized_fixtures():
        value_type = type(value)
        stem = SERIALIZED_STEMS[value_type]
        rebuilder = getattr(router, f"rebuild_{stem}_identity_v01")
        identity_field = fields(value_type)[0].name
        original_identity = getattr(value, identity_field)
        original_plain = router._plain_data_unchecked(value)
        assert canonical_json_bytes_v01(original_plain) == canonical_json_bytes_v01(
            router._plain_data_unchecked(value)
        )
        assert rebuilder(value) == original_identity == rebuilder(value)
        hints = get_type_hints(value_type)
        for field in fields(value_type):
            if field.name == identity_field:
                continue
            changed = _annotation_valid_mutation(
                getattr(value, field.name), hints[field.name], field.name
            )
            assert router._annotation_valid(changed, hints[field.name])
            mutated = replace(value, **{field.name: changed})
            canonical_json_bytes_v01(router._plain_data_unchecked(mutated))
            assert rebuilder(mutated) != original_identity, (value_type, field.name)


def test_source_context_source_scalar_distinction():
    base = _source_context()
    finite = replace(base, business_request_context_packet={"confidence": 0.66})
    assert router.validate_execution_mode_source_context_v01(finite).validation_status == "PASS"
    first = canonical_json_bytes_v01(finite.business_request_context_packet)
    assert first == canonical_json_bytes_v01(finite.business_request_context_packet)
    for non_finite in (float("nan"), float("inf"), float("-inf")):
        invalid = replace(
            base,
            business_request_context_packet={"confidence": non_finite},
        )
        assert router.validate_execution_mode_source_context_v01(invalid).validation_status == "FAIL_CLOSED"
    for text in ("\ud800", "bad\x00value", "bad\u0085value"):
        invalid = replace(base, business_request_context_packet={"value": text})
        assert router.validate_execution_mode_source_context_v01(invalid).validation_status == "FAIL_CLOSED"
    cyclic: dict[str, object] = {}
    cyclic["cycle"] = cyclic
    assert router.validate_execution_mode_source_context_v01(
        replace(base, business_request_context_packet=cyclic)
    ).validation_status == "FAIL_CLOSED"
    assert router.validate_execution_mode_source_context_v01(
        replace(base, business_request_context_packet={"unsupported": object()})
    ).validation_status == "FAIL_CLOSED"


def test_schema_metadata_required_order_and_closed_objects():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == "https://hedgehog.local/schemas/execution_mode_router_v01.schema.json"
    assert schema["title"] == "Hedgehog ExecutionModeRouter v0.1"
    assert schema["$ref"] == "#/$defs/ExecutionModeRouterInputV01"
    Draft202012Validator.check_schema(schema)
    for name, definition in schema["$defs"].items():
        assert definition["additionalProperties"] is False
        assert definition["required"] == list(FIELD_NAMES[name])
        assert tuple(definition["properties"]) == FIELD_NAMES[name]


def test_identity_substitution_tuple_subclass_and_source_native_raw_hex():
    bsep = _serialized_fixtures()[0]
    substituted = replace(bsep, bsep_binding_id="embsep_v01:" + "f" * 64)
    assert router.validate_execution_mode_bsep_binding_v01(substituted).validation_status == "FAIL_CLOSED"
    class TupleSubclass(tuple):
        pass
    replay = _serialized_fixtures()[1]
    assert router.validate_execution_mode_replay_binding_v01(
        replace(replay, evidence_refs=TupleSubclass())
    ).validation_status == "FAIL_CLOSED"
    decision = _serialized_fixtures()[10]
    assert decision.source_root_decision_id.startswith("a")
    digit_raw = replace(decision, source_root_decision_id="1" * 64,
                        decision_id="emdecision_v01:" + ZERO_HASH)
    digit_raw = replace(digit_raw, decision_id=router.rebuild_root_execution_mode_decision_identity_v01(digit_raw))
    assert router.validate_root_execution_mode_decision_v01(digit_raw).validation_status == "PASS"


def test_import_and_zero_operation_boundary_is_static_and_package_facade_absent():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                calls.append(target.id)
            elif isinstance(target, ast.Attribute):
                calls.append(target.attr)
    assert "hedgehog.kernel" not in imported
    banned_import_fragments = ("demo", "provider", "connector", "socket", "http", "subprocess")
    assert not any(any(fragment in name for fragment in banned_import_fragments) for name in imported)
    banned_calls = {"open", "write_text", "write_bytes", "system", "popen", "time", "now", "utcnow", "random"}
    assert not banned_calls.intersection(calls)
    for path in (ABI_PATH, TRANSITION_PATH, ROOT_DECISION_PATH):
        assert "execution_mode_router_v01" not in path.read_text(encoding="utf-8")
    for name in TYPE_NAMES + C1_FUNCTIONS:
        assert not hasattr(kernel, name)
    assert tuple(kernel.__all__) == (
        "CanonicalArtifactRefV01", "ArtifactDependencyEdgeV01",
        "RootOwnershipBindingV01", "EvidenceClassBindingV01",
        "AuthorityClassBindingV01", "SealProfileV01", "ArtifactManifestV01",
        "SealVerificationResultV01", "ReplayVerificationResultV01",
        "build_default_seal_profile_v01", "canonical_json_bytes_v01",
        "domain_separated_sha256_hex_v01", "build_canonical_artifact_ref_v01",
        "build_artifact_manifest_v01", "verify_artifact_manifest_v01",
        "verify_artifact_replay_v01", "artifact_manifest_to_plain_dict_v01",
        "seal_verification_result_to_plain_dict_v01",
        "replay_verification_result_to_plain_dict_v01",
    )
