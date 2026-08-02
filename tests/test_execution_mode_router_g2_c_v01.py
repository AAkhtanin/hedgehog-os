from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import inspect
import json
from pathlib import Path
import re
from typing import get_args, get_origin, get_type_hints

from jsonschema import Draft202012Validator
import pytest

import hedgehog.action_commit_packet_v02 as action_packet
import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as compatibility
import hedgehog.drs_memory_resolution_v01 as resolution
import hedgehog.drs_semantic_address_v01 as semantic_address
import hedgehog.evidence.external_anchor_v01 as external_anchor
import hedgehog.evidence.sealed_evidence_profile_v01 as evidence_profile
import hedgehog.evidence.sealed_package_v01 as sealed_package
import hedgehog.evidence.sealed_replay_evidence_v01 as sealed_replay
import hedgehog.kernel as kernel
import hedgehog.kernel.execution_mode_router_v01 as router
import hedgehog.kernel.transition_registry_v01 as transition_registry
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
import hedgehog.semantic_reasoning_adapter as semantic_adapter
import hedgehog.structured_rationale as structured_rationale


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

C2_BSEP_BUSINESS_KEYS = (
    "packet_type", "packet_id", "created_by", "source_refs", "domain",
    "root_final_authority_preserved", "truth_claimed", "authority_claimed",
    "action_permission_claimed", "final_output_claimed",
    "connector_command_claimed", "drs_write_claimed", "root_bypass_claimed",
    "real_world_effects_allowed", "Root remains final authority", "request_id",
    "business_subject", "requested_action", "explicit_blockers",
    "user_visible_summary", "forbidden_authority_fields",
    "forbidden_action_fields",
)
C2_BSEP_ROUTE_KEYS = (
    "packet_type", "packet_id", "created_by", "source_refs", "domain",
    "root_final_authority_preserved", "truth_claimed", "authority_claimed",
    "action_permission_claimed", "final_output_claimed",
    "connector_command_claimed", "drs_write_claimed", "root_bypass_claimed",
    "real_world_effects_allowed", "Root remains final authority",
    "allowed_routes", "required_guards", "selected_vector_ids",
    "route_validation_expectations", "orchestrator_is_root",
    "creates_action_commit_packet", "calls_connectors",
)
C2_BSEP_PROPOSAL_KEYS = (
    "proposal_id", "suggested_route", "selected_vector_ids", "required_guards",
    "reason", "confidence", "needs_review", "uncertainty_notes",
    "root_review_required", "truth_claimed", "authority_claimed",
    "action_permission_claimed", "final_output_claimed",
    "connector_command_claimed", "drs_write_claimed", "plan_graph_claimed",
    "bypass_root_claimed", "semantic_observations", "route_reasoning",
    "rejected_route_reasoning", "guard_reasoning", "vector_reasoning",
    "authority_boundary_reasoning",
)
C2_BSEP_RATIONALE_KEYS = (
    "rationale_type", "schema_version", "observed_semantics",
    "route_selection_reason", "rejected_routes", "required_guards_reasoning",
    "selected_vector_reasoning", "uncertainty_notes", "authority_boundary",
    "root_review_required", "orchestrator_is_root",
    "creates_action_commit_packet", "calls_connectors", "truth_claimed",
    "authority_claimed", "action_permission_claimed", "final_output_claimed",
    "connector_command_claimed", "drs_write_claimed",
    "action_commit_packet_claimed", "root_bypass_claimed",
    "root_final_authority_preserved", "Root remains final authority",
)
C2_BSEP_PACKET_KEYS = (
    "packet_type", "packet_id", "created_by", "source_refs", "domain",
    "root_final_authority_preserved", "truth_claimed", "authority_claimed",
    "action_permission_claimed", "final_output_claimed",
    "connector_command_claimed", "drs_write_claimed", "root_bypass_claimed",
    "real_world_effects_allowed", "Root remains final authority", "source_role",
    "target_role", "source_route_id", "source_proposal_id",
    "source_context_packet_id", "source_structured_rationale_ref",
    "schema_version", "action_commit_packet_claimed", "raw_user_text_included",
    "raw_cross_role_text_included", "ContextPacket is not truth",
    "ContextPacket is not authority", "BoundedSemanticEvidencePacket is not truth",
    "BoundedSemanticEvidencePacket is not authority",
    "BoundedSemanticEvidencePacket is not FinalOutput",
    "BoundedSemanticEvidencePacket is not ActionCommitPacket",
    "Evidence packet is not action permission", "Gemini proposes, Root disposes",
    "observed_semantic_facts", "missing_evidence", "uncertainty_notes",
    "risk_boundary_notes", "rejected_action_routes",
    "required_approvals_or_conditions", "authority_boundary_notes",
    "selected_vector_ids", "required_guards",
)
C2_BSEP_EVIDENCE_FIELDS = (
    "observed_semantic_facts", "missing_evidence", "uncertainty_notes",
    "risk_boundary_notes", "rejected_action_routes",
    "required_approvals_or_conditions", "authority_boundary_notes",
)
C2_BSEP_EVIDENCE_ITEM_KEYS = (
    "text", "source", "evidence_kind", "confidence_label", "candidate_only",
    "raw_quote",
)

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

C2_FUNCTIONS = (
    "build_execution_mode_source_context_v01",
    "build_execution_mode_bsep_binding_v01",
    "build_execution_mode_replay_not_applicable_binding_v01",
    "build_execution_mode_replay_binding_v01",
    "build_execution_mode_g2a_no_packet_binding_v01",
    "build_execution_mode_g2a_binding_v01",
    "build_execution_mode_g2b_not_applicable_binding_v01",
    "build_execution_mode_g2b_binding_v01",
    "validate_execution_mode_router_input_against_sources_v01",
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

IMPLEMENTED_FUNCTIONS_AFTER_C2 = tuple(
    name for name in PUBLIC_FUNCTIONS if name in set(C1_FUNCTIONS + C2_FUNCTIONS)
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

C2_SIGNATURES = {
    "build_execution_mode_source_context_v01": "(*, business_request_context_packet: 'dict[str, object]', bsep_packet: 'dict[str, object]', bsep_route_context_packet: 'dict[str, object]', bsep_orchestrator_proposal: 'dict[str, object]', bsep_structured_rationale: 'dict[str, object]', sealed_replay_evidence: 'SealedReplayEvidenceV01 | None', replay_source_manifest: 'SealedPackageManifestV01 | None', replay_source_domain_projection: 'DomainEvidenceProjectionV01 | None', replay_source_safe_file_contents: 'tuple[bytes, ...]', replay_anchor_publication: 'ExternalAnchorPublicationV01 | None', replay_anchored_verification: 'AnchoredPackageVerificationV01 | None', replay_supplied_anchor_publication_id: 'str | None', replay_reconstructed_manifest: 'SealedPackageManifestV01 | None', replay_reconstructed_domain_projection: 'DomainEvidenceProjectionV01 | None', replay_reconstructed_safe_file_contents: 'tuple[bytes, ...]', g2a_inspection: 'ActionPacketPresentEligibilityInspectionV01 | None', g2a_registry: 'ActionCommitPacketRegistryV02 | None', g2a_packet_id: 'str | None', g2a_corridor: 'ContractFulfillmentCorridorV01 | None', g2a_corridor_step: 'CorridorStepV01 | None', g2a_current_dependency_observations: 'tuple[ActionDependencyCurrentObservationV01, ...]', g2a_logical_time_bridge: 'LogicalTimeBridgeV01 | None', g2a_evaluation_time: 'int | None', g2a_evaluation_time_source: 'str | None', g2a_evaluation_context_id: 'str | None', g2a_transition_registry_profile: 'ActionPacketTransitionRegistryProfileV01 | None', g2b_resolution_report: 'DRSResolutionReportV01 | None', g2b_compatibility_projections: 'tuple[LegacyDRSProjectionV01, ...]', g2b_use_time: 'int | None', g2b_root_kernel: 'RootDecisionKernelV01 | None', g2b_root_decision_input: 'RootDecisionInputV01 | None', g2b_root_decision_result: 'RootDecisionResultV01 | None', g2b_writeback_evidence: 'None') -> 'ExecutionModeSourceContextV01'",
    "build_execution_mode_bsep_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', source_context: 'ExecutionModeSourceContextV01') -> 'ExecutionModeBSEPBindingV01'",
    "build_execution_mode_replay_not_applicable_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str') -> 'ExecutionModeReplayBindingV01'",
    "build_execution_mode_replay_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', source_context: 'ExecutionModeSourceContextV01') -> 'ExecutionModeReplayBindingV01'",
    "build_execution_mode_g2a_no_packet_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', evaluation_time: 'int', evaluation_time_source: 'str', evaluation_context_id: 'str') -> 'ExecutionModeG2ABindingV01'",
    "build_execution_mode_g2a_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', source_context: 'ExecutionModeSourceContextV01') -> 'ExecutionModeG2ABindingV01'",
    "build_execution_mode_g2b_not_applicable_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str') -> 'ExecutionModeG2BBindingV01'",
    "build_execution_mode_g2b_binding_v01": "(*, request_id: 'str', transaction_id: 'str', owning_root_id: 'str', domain_id: 'str', source_context: 'ExecutionModeSourceContextV01') -> 'ExecutionModeG2BBindingV01'",
    "validate_execution_mode_router_input_against_sources_v01": "(*, router_input: 'ExecutionModeRouterInputV01', source_context: 'ExecutionModeSourceContextV01') -> 'ExecutionModeValidationReportV01'",
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


def _c2_bsep_family(
    *,
    request_id: str = "request:g2c:c2:test",
    domain_id: str = "G2C_C2_TEST_DOMAIN",
) -> dict[str, dict[str, object]]:
    route_id = "route:g2c:c2:bounded"
    proposal_id = "proposal:g2c:c2:bounded"
    vectors = ("vector:g2c:c2:bounded",)
    guards = ("guard:g2c:c2:root_review",)
    business = context_packets.build_business_request_context_packet(
        packet_id="context_packet:g2c:c2:business",
        created_by="runtime:g2c:c2",
        domain=domain_id,
        request_id=request_id,
        business_subject="certificate_request",
        requested_action="bounded_review",
        user_visible_summary="Bounded certificate request for Root review",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": domain_id,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id="context_packet:g2c:c2:route",
        created_by="runtime:g2c:c2",
        source_refs=(business_ref,),
        domain=domain_id,
        allowed_routes=(route_id,),
        required_guards=guards,
        selected_vector_ids=vectors,
        route_validation_expectations={
            "root_review_required": True,
            "selected_only_allowed_vectors": True,
        },
        orchestrator_is_root=False,
        creates_action_commit_packet=False,
        calls_connectors=False,
    )
    proposal: dict[str, object] = {
        "proposal_id": proposal_id,
        "suggested_route": route_id,
        "selected_vector_ids": vectors,
        "required_guards": guards,
        "reason": "Bounded semantic review is required.",
        "confidence": 0.66,
        "needs_review": True,
        "uncertainty_notes": ("Evidence remains bounded and incomplete.",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "semantic_observations": (
            "A certificate request requires bounded review.",
        ),
        "route_reasoning": ("Use the bounded Root review route.",),
        "rejected_route_reasoning": ("Direct action remains forbidden.",),
        "guard_reasoning": ("Root review is mandatory.",),
        "vector_reasoning": ("The bounded vector is relevant.",),
        "authority_boundary_reasoning": ("Root remains final authority.",),
    }
    rationale = structured_rationale.build_orchestrator_structured_rationale(
        observed_semantics=proposal["semantic_observations"],
        route_selection_reason=proposal["route_reasoning"],
        rejected_routes=proposal["rejected_route_reasoning"],
        required_guards_reasoning=proposal["guard_reasoning"],
        selected_vector_reasoning=proposal["vector_reasoning"],
        uncertainty_notes=proposal["uncertainty_notes"],
        authority_boundary=proposal["authority_boundary_reasoning"],
        root_review_required=True,
    )
    rationale_sha = hashlib.sha256(
        canonical_json_bytes_v01(rationale)
    ).hexdigest()

    def item(text: str, evidence_kind: str) -> dict[str, object]:
        return context_packets.semantic_evidence_item(
            text,
            source="runtime_canonicalization",
            evidence_kind=evidence_kind,
            confidence_label="medium",
        )

    packet = context_packets.build_bounded_semantic_evidence_packet(
        packet_id="context_packet:g2c:c2:bsep",
        source_refs=(business_ref,),
        domain=domain_id,
        source_role="orchestrator",
        target_role="architect",
        source_route_id=route_id,
        source_proposal_id=proposal_id,
        source_context_packet_id=route["packet_id"],
        source_structured_rationale_ref=(
            "structured_rationale_v01:" + rationale_sha
        ),
        observed_semantic_facts=(
            item("A certificate request requires bounded review.", "observed_fact"),
        ),
        missing_evidence=(
            item("Root decision evidence is pending.", "missing_evidence"),
        ),
        uncertainty_notes=(
            item("Evidence remains bounded and incomplete.", "uncertainty"),
        ),
        risk_boundary_notes=(
            item("No action authority is present.", "risk_boundary"),
        ),
        rejected_action_routes=(
            item("Direct action remains forbidden.", "rejected_route"),
        ),
        required_approvals_or_conditions=(
            item("Root review is required.", "approval_condition"),
        ),
        authority_boundary_notes=(
            item("Root remains final authority.", "authority_boundary"),
        ),
        selected_vector_ids=vectors,
        required_guards=guards,
    )
    return {
        "business": business,
        "route": route,
        "proposal": proposal,
        "rationale": rationale,
        "packet": packet,
    }


def _c2_rebind_rationale(
    bsep: dict[str, dict[str, object]],
    rationale: dict[str, object],
) -> dict[str, dict[str, object]]:
    rationale_sha = hashlib.sha256(canonical_json_bytes_v01(rationale)).hexdigest()
    return {
        **bsep,
        "rationale": rationale,
        "packet": {
            **bsep["packet"],
            "source_structured_rationale_ref": (
                "structured_rationale_v01:" + rationale_sha
            ),
        },
    }


def _c2_context_for_bsep(
    bsep: dict[str, dict[str, object]],
) -> router.ExecutionModeSourceContextV01:
    return _c2_source_context(
        bsep=bsep,
        evaluation_time=200,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "a" * 64,
    )


def _c2_assert_bsep_failure(
    bsep: dict[str, dict[str, object]],
    expected_reason: str,
) -> None:
    with pytest.raises(ValueError) as exc:
        router.build_execution_mode_bsep_binding_v01(
            request_id="request:g2c:c2:test",
            transaction_id="transaction:g2c:c2:test",
            owning_root_id="root:g2c:c2:test",
            domain_id="G2C_C2_TEST_DOMAIN",
            source_context=_c2_context_for_bsep(bsep),
        )
    assert str(exc.value) == expected_reason


def _c2_replay_family(domain_id: str) -> dict[str, object]:
    kernel_hash = hashlib.sha256(
        canonical_json_bytes_v01({"domain": domain_id, "slice": "G2-C2"})
    ).hexdigest()
    programme = evidence_profile.build_programme_evidence_identity_v01(
        programme_id="g2c_c2_replay_programme_v01",
        programme_version="v0.1",
    )
    execution = evidence_profile.build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=domain_id,
        execution_head="abcdef1",
        source_task_id="task:g2c:c2:replay",
        run_id="run:g2c:c2:replay",
        report_id="report:g2c:c2:replay",
    )
    attempt = evidence_profile.build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=execution,
        attempt_number=1,
        package_id="package:g2c:c2:replay",
        logical_package_ref="g2c/c2/replay",
        output_directory_ref="g2c/c2/replay/output",
        provider_mode="deterministic_fixture",
        model_id="none",
        expected_actor_count=1,
        provider_call_budget=0,
    )
    source = evidence_profile.build_safe_source_record_v01(
        source_id="source:g2c:c2:replay",
        source_type="g2c_c2_replay_fixture",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        canonical_projection={"domain": domain_id, "hash": kernel_hash},
        media_type="application/json",
        trace_refs=(kernel_hash,),
        contains_raw_prompt=False,
        contains_raw_provider_response=False,
        secret_scan_passed=True,
        observed_provider_call_count=0,
        observed_network_call_count=0,
        observed_gemini_call_count=0,
        real_world_effects_count=0,
    )
    artifact = evidence_profile.build_evidence_artifact_record_v01(
        artifact_id="artifact:g2c:c2:replay",
        artifact_type="g2c_c2_replay_fixture",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,),
        canonical_projection={"domain": domain_id, "hash": kernel_hash},
        authority_class="evidence_only",
        owner_root_id=None,
        trace_refs=(kernel_hash,),
        created_authority_count=0,
        created_permission_count=0,
        real_world_effects_count=0,
    )
    projection = evidence_profile.build_domain_evidence_projection_v01(
        programme_identity=programme,
        domain_execution_identity=execution,
        attempt_identity=attempt,
        source_records=(source,),
        artifact_records=(artifact,),
        kernel_artifact_refs=(),
        causal_consumption_refs=(),
        evidence_refs=("evidence:g2c:c2:replay",),
        limitation_refs=("limitation:g2c:c2:local_only",),
    )
    content = canonical_json_bytes_v01(
        {"domain": domain_id, "hash": kernel_hash}
    ) + b"\n"
    file_record = sealed_package.build_safe_file_record_v01(
        logical_path="evidence/g2c_c2_replay.json",
        media_type="application/json",
        content_bytes=content,
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,),
        terminal_newline_required=True,
        secret_scan_passed=True,
    )
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=(file_record,),
        safe_file_contents=(content,),
        kernel_manifest_hash=kernel_hash,
    )
    publication = external_anchor.build_external_anchor_publication_v01(
        manifest=manifest,
        domain_projection=projection,
        safe_file_contents=(content,),
        publication_base_head="abcdef1",
    )
    verification = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection,
        safe_file_contents=(content,),
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    replay = sealed_replay.build_sealed_replay_evidence_v01(
        source_manifest=manifest,
        source_domain_projection=projection,
        source_safe_file_contents=(content,),
        anchor_publication=publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=publication.anchor_publication_id,
        reconstructed_manifest=manifest,
        reconstructed_domain_projection=projection,
        reconstructed_safe_file_contents=(content,),
        evidence_refs=("evidence:g2c:c2:replay", "anchor:g2c:c2:replay"),
    )
    return {
        "replay": replay,
        "manifest": manifest,
        "projection": projection,
        "contents": (content,),
        "publication": publication,
        "verification": verification,
    }


def _c2_source_context(
    *,
    bsep: dict[str, dict[str, object]],
    evaluation_time: int,
    evaluation_time_source: str,
    evaluation_context_id: str,
    replay: dict[str, object] | None = None,
    g2a: object | None = None,
    g2b: dict[str, object] | None = None,
) -> router.ExecutionModeSourceContextV01:
    replay = replay or {}
    g2b = g2b or {}
    return router.build_execution_mode_source_context_v01(
        business_request_context_packet=bsep["business"],
        bsep_packet=bsep["packet"],
        bsep_route_context_packet=bsep["route"],
        bsep_orchestrator_proposal=bsep["proposal"],
        bsep_structured_rationale=bsep["rationale"],
        sealed_replay_evidence=replay.get("replay"),
        replay_source_manifest=replay.get("manifest"),
        replay_source_domain_projection=replay.get("projection"),
        replay_source_safe_file_contents=replay.get("contents", ()),
        replay_anchor_publication=replay.get("publication"),
        replay_anchored_verification=replay.get("verification"),
        replay_supplied_anchor_publication_id=(
            replay["publication"].anchor_publication_id if replay else None
        ),
        replay_reconstructed_manifest=replay.get("manifest"),
        replay_reconstructed_domain_projection=replay.get("projection"),
        replay_reconstructed_safe_file_contents=replay.get("contents", ()),
        g2a_inspection=getattr(g2a, "inspection", None),
        g2a_registry=getattr(g2a, "registry", None),
        g2a_packet_id=(
            getattr(getattr(g2a, "root_bound", None), "packet_identity", None).packet_id
            if g2a is not None
            else None
        ),
        g2a_corridor=getattr(g2a, "corridor", None),
        g2a_corridor_step=getattr(g2a, "corridor_step", None),
        g2a_current_dependency_observations=getattr(g2a, "observations", ()),
        g2a_logical_time_bridge=getattr(g2a, "logical_time_bridge", None),
        g2a_evaluation_time=evaluation_time,
        g2a_evaluation_time_source=evaluation_time_source,
        g2a_evaluation_context_id=evaluation_context_id,
        g2a_transition_registry_profile=(
            transition_registry.build_action_packet_transition_registry_profile_v01()
            if g2a is not None
            else None
        ),
        g2b_resolution_report=g2b.get("report"),
        g2b_compatibility_projections=g2b.get("projections", ()),
        g2b_use_time=g2b.get("use_time"),
        g2b_root_kernel=g2b.get("root_kernel"),
        g2b_root_decision_input=g2b.get("root_input"),
        g2b_root_decision_result=g2b.get("root_result"),
        g2b_writeback_evidence=None,
    )


def _c2_snapshot(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    evaluation_time: int,
    created_by: str = "runtime:g2c:c2:snapshot",
    action_class: str = "NON_ACTION",
    action_packet_relation: str = "NOT_APPLICABLE",
) -> router.ExecutionModeLocalRoutingSnapshotV01:
    def utc(value: int) -> str:
        return datetime.fromtimestamp(value, timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )

    profiles = []
    for index, mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01):
        not_required = mode in (
            "sealed_replay",
            "direct_informational_reuse",
        )
        profiles.append(
            router.build_execution_mode_local_mode_profile_v01(
                request_id=request_id,
                transaction_id=transaction_id,
                owning_root_id=owning_root_id,
                domain_id=domain_id,
                mode=mode,
                policy_snapshot_id="policy:g2c:c2",
                capability_snapshot_id="capability:g2c:c2",
                cost_model_id="cost:g2c:c2",
                policy_allowed=True,
                scope_allowed=True,
                risk_allowed=True,
                privacy_allowed=True,
                capability_state=("NOT_REQUIRED" if not_required else "AVAILABLE"),
                capability_id=(None if not_required else f"capability:g2c:c2:{mode}"),
                cost_units=index + 1,
            )
        )
    return router.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        request_class="BOUNDED_REVIEW",
        action_class=action_class,
        action_packet_relation=action_packet_relation,
        scope_class="BOUNDED",
        scope_ref="scope:g2c:c2",
        permitted_narrower_scope_refs=(),
        risk_class="LOW",
        policy_snapshot_id="policy:g2c:c2",
        capability_snapshot_id="capability:g2c:c2",
        cost_model_id="cost:g2c:c2",
        required_user_input_state="COMPLETE",
        hard_block_state="CLEAR",
        evaluation_time_epoch_seconds=evaluation_time,
        pt_created_at_utc=utc(evaluation_time - 100),
        et_observed_at_utc=utc(evaluation_time),
        ct_session_anchor=created_by,
        ttl_seconds=1000,
        freshness_class="normal",
        valid_from_utc=utc(evaluation_time - 100),
        valid_to_utc=utc(evaluation_time + 900),
        mode_profiles=tuple(profiles),
    )


def _c2_projection_for_report(
    report: resolution.DRSResolutionReportV01,
) -> compatibility.LegacyDRSProjectionV01:
    import test_drs_semantic_address_reuse_certificate_g2_b_v01 as source_g2b

    return compatibility.build_legacy_drs_projection_v01(
        source_family="LOCAL_DRS_DICT",
        source=source_g2b._legacy_sources()["LOCAL_DRS_DICT"],
        target_semantic_address=report.semantic_address,
    )


def _c2_report_with_projection(
    report: resolution.DRSResolutionReportV01,
) -> resolution.DRSResolutionReportV01:
    projection = _c2_projection_for_report(report)
    return resolution.build_drs_resolution_report_v01(
        semantic_address=report.semantic_address,
        query=report.query,
        source_projections=(projection,),
        source_records=report.source_records,
        query_evaluations=report.query_evaluations,
        eligible_candidates=report.eligible_candidates,
        ranked_candidate_ids=report.ranked_candidate_ids,
        selected_candidate_id=report.selected_candidate_id,
        retrieval_plan=report.retrieval_plan,
        memory_descent_result=report.memory_descent_result,
        root_shortcut_projection=report.root_shortcut_projection,
        reuse_certificate=report.reuse_certificate,
        context_only_record_ids=report.context_only_record_ids,
        historical_only_record_ids=report.historical_only_record_ids,
        warning_only_record_ids=report.warning_only_record_ids,
        rerun_required_record_ids=report.rerun_required_record_ids,
        blocked_record_ids=report.blocked_record_ids,
        provider_calls=report.provider_calls,
        network_calls=report.network_calls,
        gemini_calls=report.gemini_calls,
        external_drs_calls=report.external_drs_calls,
        connector_calls=report.connector_calls,
        real_world_effects_count=report.real_world_effects_count,
        final_status=report.final_status,
        reason_codes=report.reason_codes,
    )


def _c2_g2b_context_family() -> dict[str, object]:
    import test_drs_semantic_address_reuse_certificate_g2_b_v01 as source_g2b

    address = source_g2b._b2_address()
    record = source_g2b._b2_record(
        address=address,
        reuse_policy_class="CONTEXT_ONLY",
    )
    query = source_g2b._b2_query(
        address=address,
        query_mode="MEMORY_CONTEXT_ONLY",
        evaluation_time_source="INJECTED_ANALYSIS_TIME",
        required_time_axes=("KT", "TTL", "VALIDITY"),
        reuse_intent="CONTEXT",
        requested_reuse_classes=("CONTEXT_ONLY",),
    )
    evaluation = source_g2b._b2_evaluate(record, query)
    assert evaluation.query_state == "STALE_CONTEXT_ONLY"
    budget = resolution.build_memory_descent_budget_v01(
        max_depth=0,
        max_records_opened=1,
        max_pointers_opened=0,
        max_artifacts_opened=0,
        max_bytes_opened=0,
        max_lineage_edges=0,
        max_conflict_records=0,
    )
    plan = resolution.build_retrieval_plan_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),
        proposed_memory_pointer_ids=(),
        proposed_artifact_pointer_ids=(),
        requested_descent_class="SUMMARY_ONLY",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(),
        reason_codes=(),
    )
    provisional = resolution.build_drs_resolution_report_v01(
        semantic_address=address,
        query=query,
        source_projections=(),
        source_records=(record,),
        query_evaluations=(evaluation,),
        eligible_candidates=(),
        ranked_candidate_ids=(),
        selected_candidate_id=None,
        retrieval_plan=plan,
        memory_descent_result=None,
        root_shortcut_projection=None,
        reuse_certificate=None,
        context_only_record_ids=(record.meaning_record_id,),
        historical_only_record_ids=(),
        warning_only_record_ids=(),
        rerun_required_record_ids=(),
        blocked_record_ids=(),
        provider_calls=0,
        network_calls=0,
        gemini_calls=0,
        external_drs_calls=0,
        connector_calls=0,
        real_world_effects_count=0,
        final_status="PASS",
        reason_codes=(),
    )
    report = _c2_report_with_projection(provisional)
    return {
        "report": report,
        "projections": report.source_projections,
        "use_time": query.evaluation_time,
    }


def _c2_g2b_direct_family() -> dict[str, object]:
    import test_drs_semantic_address_reuse_certificate_g2_b_v01 as source_g2b

    fixture = source_g2b._b4_fixture()
    report = _c2_report_with_projection(fixture["report"])
    return {
        "report": report,
        "projections": report.source_projections,
        "use_time": fixture["use_time"],
        "root_kernel": fixture["root_kernel"],
        "root_input": fixture["root_input"],
        "root_result": fixture["root_result"],
    }


def _c2_g2a_present_family(
    *,
    evaluation_time: int,
    evaluation_time_source: str,
    evaluation_context_id: str,
) -> object:
    from types import SimpleNamespace
    import test_action_commit_packet_lifecycle_g2_a_v01 as source_g2a

    fixture = source_g2a._g2a4a_fixture_value()
    profile = transition_registry.build_action_packet_transition_registry_profile_v01()
    inspection = action_packet.inspect_action_packet_present_eligibility_v01(
        fixture.registry,
        packet_id=fixture.root_bound.packet_identity.packet_id,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        current_dependency_observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_time_source,
        evaluation_context_id=evaluation_context_id,
        action_packet_transition_registry_profile=profile,
    )
    return SimpleNamespace(
        inspection=inspection,
        registry=fixture.registry,
        root_bound=fixture.root_bound,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
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


def test_exact_public_registries_and_c2_staging():
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
    assert actual == IMPLEMENTED_FUNCTIONS_AFTER_C2
    assert len(actual) == 50
    assert all(not hasattr(router, name) for name in router.PUBLIC_G2C_FUNCTIONS_V01
               if name not in IMPLEMENTED_FUNCTIONS_AFTER_C2)


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


def test_exact_c2_signatures_and_future_surface_absence():
    assert tuple(C2_SIGNATURES) == C2_FUNCTIONS
    for name, expected in C2_SIGNATURES.items():
        assert str(inspect.signature(getattr(router, name))) == expected
    future = tuple(
        name
        for name in router.PUBLIC_G2C_FUNCTIONS_V01
        if name not in IMPLEMENTED_FUNCTIONS_AFTER_C2
    )
    assert len(future) == 24
    assert all(not hasattr(router, name) for name in future)
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "NotImplemented" not in source
    assert "__getattr__" not in source


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
    for name in TYPE_NAMES + IMPLEMENTED_FUNCTIONS_AFTER_C2:
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


def test_c2_source_context_and_actual_bsep_source_family():
    request_id = "request:g2c:c2:test"
    transaction_id = "transaction:g2c:c2:test"
    owning_root_id = "root:g2c:c2:test"
    domain_id = "G2C_C2_TEST_DOMAIN"
    bsep = _c2_bsep_family(request_id=request_id, domain_id=domain_id)
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=200,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "a" * 64,
    )
    assert router.validate_execution_mode_source_context_v01(
        context
    ).validation_status == "PASS"
    rationale_result = (
        structured_rationale.validate_orchestrator_structured_rationale(
            bsep["rationale"]
        )
    )
    assert context_packets.validate_business_request_context_packet(
        bsep["business"]
    )["accepted"] is True
    assert context_packets.validate_orchestrator_route_context_packet(
        bsep["route"]
    )["accepted"] is True
    assert semantic_adapter.validate_orchestrator_semantic_reasoning_proposal(
        bsep["proposal"]
    ) == ()
    assert rationale_result["accepted"] is True
    assert context_packets.validate_bounded_semantic_evidence_packet(
        bsep["packet"],
        route_context_packet=bsep["route"],
        orchestrator_proposal=bsep["proposal"],
        structured_rationale_validation=rationale_result,
    )["accepted"] is True

    binding = router.build_execution_mode_bsep_binding_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        source_context=context,
    )
    expected_hashes = {
        "business_request_packet_sha256": hashlib.sha256(
            canonical_json_bytes_v01(bsep["business"])
        ).hexdigest(),
        "source_route_context_sha256": hashlib.sha256(
            canonical_json_bytes_v01(bsep["route"])
        ).hexdigest(),
        "source_proposal_sha256": hashlib.sha256(
            canonical_json_bytes_v01(bsep["proposal"])
        ).hexdigest(),
        "source_structured_rationale_sha256": hashlib.sha256(
            canonical_json_bytes_v01(bsep["rationale"])
        ).hexdigest(),
        "source_packet_sha256": hashlib.sha256(
            canonical_json_bytes_v01(bsep["packet"])
        ).hexdigest(),
    }
    assert binding.business_request_packet_sha256 == (
        expected_hashes["business_request_packet_sha256"]
    )
    assert binding.source_route_context_sha256 == (
        expected_hashes["source_route_context_sha256"]
    )
    assert binding.source_proposal_sha256 == expected_hashes["source_proposal_sha256"]
    assert binding.source_structured_rationale_sha256 == (
        expected_hashes["source_structured_rationale_sha256"]
    )
    assert binding.source_packet_sha256 == expected_hashes["source_packet_sha256"]
    assert binding.source_family_sha256 == router._bsep_source_family_sha256(
        **expected_hashes
    )
    assert binding.source_structured_rationale_ref == (
        "structured_rationale_v01:"
        + expected_hashes["source_structured_rationale_sha256"]
    )
    assert binding == router.build_execution_mode_bsep_binding_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        source_context=context,
    )
    assert not any(
        (
            binding.authority_created,
            binding.permission_created,
            binding.action_commit_packet_created,
            binding.final_output_created,
            bool(binding.real_world_effects_count),
        )
    )


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    (
        ("request", "g2c_business_request_invalid"),
        ("missing_ref", "g2c_business_request_ref_invalid"),
        ("foreign_ref", "g2c_business_request_ref_invalid"),
        ("route", "g2c_bsep_invalid"),
        ("proposal", "g2c_semantic_proposal_invalid"),
        ("confidence", "g2c_semantic_proposal_invalid"),
        ("authority", "g2c_semantic_proposal_invalid"),
        ("rationale", "g2c_structured_rationale_invalid"),
        ("packet", "g2c_bsep_invalid"),
    ),
)
def test_c2_bsep_substitution_matrix(mutation, expected_reason):
    bsep = _c2_bsep_family()
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=200,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "a" * 64,
    )
    if mutation == "request":
        context = replace(
            context,
            business_request_context_packet={
                **bsep["business"],
                "request_id": "request:g2c:c2:foreign",
            },
        )
    elif mutation == "missing_ref":
        context = replace(
            context,
            bsep_route_context_packet={**bsep["route"], "source_refs": ()},
        )
    elif mutation == "foreign_ref":
        context = replace(
            context,
            bsep_route_context_packet={
                **bsep["route"],
                "source_refs": bsep["route"]["source_refs"]
                + (
                    {
                        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
                        "packet_id": "context_packet:g2c:c2:foreign",
                        "request_id": "request:g2c:c2:foreign",
                        "domain_id": "G2C_C2_TEST_DOMAIN",
                    },
                ),
            },
        )
    elif mutation == "route":
        context = replace(
            context,
            bsep_route_context_packet={
                **bsep["route"],
                "selected_vector_ids": ("vector:g2c:c2:foreign",),
            },
        )
    elif mutation == "proposal":
        changed = dict(bsep["proposal"])
        changed.pop("guard_reasoning")
        context = replace(context, bsep_orchestrator_proposal=changed)
    elif mutation == "confidence":
        context = replace(
            context,
            bsep_orchestrator_proposal={**bsep["proposal"], "confidence": True},
        )
    elif mutation == "authority":
        context = replace(
            context,
            bsep_orchestrator_proposal={
                **bsep["proposal"],
                "authority_claimed": True,
            },
        )
    elif mutation == "rationale":
        context = replace(
            context,
            bsep_structured_rationale={
                **bsep["rationale"],
                "root_review_required": False,
            },
        )
    else:
        context = replace(
            context,
            bsep_packet={
                **bsep["packet"],
                "source_proposal_id": "proposal:g2c:c2:foreign",
            },
        )
    with pytest.raises(ValueError) as exc:
        router.build_execution_mode_bsep_binding_v01(
            request_id="request:g2c:c2:test",
            transaction_id="transaction:g2c:c2:test",
            owning_root_id="root:g2c:c2:test",
            domain_id="G2C_C2_TEST_DOMAIN",
            source_context=context,
        )
    assert str(exc.value) == expected_reason


def test_c2_replay_absent_bound_and_substitution_contract():
    common = {
        "request_id": "request:g2c:c2:replay",
        "transaction_id": "transaction:g2c:c2:replay",
        "owning_root_id": "root:g2c:c2:replay",
        "domain_id": "G2C_C2_REPLAY_DOMAIN",
    }
    absent = router.build_execution_mode_replay_not_applicable_binding_v01(
        **common
    )
    assert absent.binding_state == "NOT_APPLICABLE"
    assert absent.replay_status == "NOT_APPLICABLE"
    assert absent.evidence_refs == ()
    assert not any(
        getattr(absent, name)
        for name in (
            "authority_created",
            "permission_created",
            "action_commit_packet_created",
            "receipt_created",
            "final_output_created",
            "real_world_effects_count",
        )
    )
    family = _c2_replay_family(common["domain_id"])
    bsep = _c2_bsep_family(
        request_id=common["request_id"], domain_id=common["domain_id"]
    )
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=200,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "b" * 64,
        replay=family,
    )
    bound = router.build_execution_mode_replay_binding_v01(
        **common, source_context=context
    )
    assert bound.binding_state == "SEALED_REPLAY_BOUND"
    assert bound.replay_status == "PASS"
    assert bound.integrity_verified is True
    assert bound.continuity_verified is True
    assert bound.anchor_verified is True
    assert bound.source_replay_sha256 == hashlib.sha256(
        canonical_json_bytes_v01(
            sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
                family["replay"],
                source_manifest=family["manifest"],
                source_domain_projection=family["projection"],
                source_safe_file_contents=family["contents"],
                anchor_publication=family["publication"],
                anchored_verification=family["verification"],
                supplied_anchor_publication_id=(
                    family["publication"].anchor_publication_id
                ),
                reconstructed_manifest=family["manifest"],
                reconstructed_domain_projection=family["projection"],
                reconstructed_safe_file_contents=family["contents"],
            )
        )
    ).hexdigest()
    for forged in (
        replace(
            context,
            replay_supplied_anchor_publication_id="f" * 64,
        ),
        replace(context, replay_reconstructed_safe_file_contents=(b"changed\n",)),
    ):
        with pytest.raises(ValueError, match="^g2c_replay_binding_invalid$"):
            router.build_execution_mode_replay_binding_v01(
                **common, source_context=forged
            )
    with pytest.raises(ValueError, match="^g2c_source_context_invalid$"):
        router.build_execution_mode_source_context_v01(
            **{
                **{
                    name: getattr(context, name)
                    for name in FIELD_NAMES["ExecutionModeSourceContextV01"]
                },
                "replay_anchor_publication": None,
            }
        )


def test_c2_g2a_no_packet_and_actual_present_inspection():
    no_packet = router.build_execution_mode_g2a_no_packet_binding_v01(
        request_id="request:g2c:c2:g2a",
        transaction_id="transaction:g2c:c2:g2a",
        owning_root_id="root:g2c:c2:g2a",
        domain_id="G2C_C2_G2A_DOMAIN",
        evaluation_time=1783470602,
        evaluation_time_source="runtime:g2c:c2:g2a",
        evaluation_context_id="emlocal_v01:" + "c" * 64,
    )
    assert no_packet.binding_state == "NO_PACKET"
    assert no_packet.historical_lifecycle_state == "NO_PACKET"
    assert no_packet.idempotency_disposition == "NOT_APPLICABLE"
    assert no_packet.source_reason_codes == ()
    assert no_packet.transition_event_count == no_packet.execution_attempt_count == 0
    assert no_packet.historical_result_unchanged is True

    evaluation_time = 1783470602
    evaluation_source = "runtime:g2c:c2:g2a"
    evaluation_context = "emlocal_v01:" + "d" * 64
    family = _c2_g2a_present_family(
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_source,
        evaluation_context_id=evaluation_context,
    )
    bsep = _c2_bsep_family(domain_id="G2C_C2_G2A_DOMAIN")
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_source,
        evaluation_context_id=evaluation_context,
        g2a=family,
    )
    bound = router.build_execution_mode_g2a_binding_v01(
        request_id="request:g2c:c2:test",
        transaction_id=(
            family.registry.action_packet_lifecycle_entries[0]
            .root_bound_genesis.canonical_projection.transaction_id
        ),
        owning_root_id=(
            family.registry.action_packet_lifecycle_entries[0]
            .root_bound_genesis.canonical_projection.owning_local_root_id
        ),
        domain_id="G2C_C2_G2A_DOMAIN",
        source_context=context,
    )
    assert bound.binding_state == "PRESENT_INSPECTION_BOUND"
    assert bound.present_executable is False
    assert bound.present_eligibility_status == "NON_EXECUTABLE"
    assert bound.source_reason_codes == family.inspection.reason_codes
    assert bound.source_inspection_sha256 is not None
    forged = replace(
        context,
        g2a_inspection=replace(
            family.inspection,
            present_executable=True,
        ),
    )
    with pytest.raises(
        ValueError, match="^g2c_g2a_present_inspection_invalid$"
    ):
        router.build_execution_mode_g2a_binding_v01(
            request_id="request:g2c:c2:test",
            transaction_id=bound.transaction_id,
            owning_root_id=bound.owning_root_id,
            domain_id="G2C_C2_G2A_DOMAIN",
            source_context=forged,
        )


def test_c2_g2b_three_state_query_transaction_and_no_downgrade():
    absent = router.build_execution_mode_g2b_not_applicable_binding_v01(
        request_id="request:g2c:c2:g2b",
        transaction_id="transaction:g2c:c2:g2b",
        owning_root_id="root:g2c:c2:g2b",
        domain_id="G2C_C2_G2B_DOMAIN",
    )
    assert absent.binding_state == "NOT_APPLICABLE"
    assert absent.lineage_state == "NOT_APPLICABLE"
    assert absent.context_available is False

    for maker, expected_state, direct in (
        (_c2_g2b_context_family, "RESOLUTION_CONTEXT_BOUND", False),
        (_c2_g2b_direct_family, "DIRECT_REUSE_BOUND", True),
    ):
        family = maker()
        query = family["report"].query
        bsep = _c2_bsep_family(
            request_id="request:g2c:c2:g2b", domain_id=query.domain
        )
        context = _c2_source_context(
            bsep=bsep,
            evaluation_time=query.evaluation_time,
            evaluation_time_source="runtime:g2c:c2:snapshot",
            evaluation_context_id="emlocal_v01:" + "e" * 64,
            g2b=family,
        )
        binding = router.build_execution_mode_g2b_binding_v01(
            request_id="request:g2c:c2:g2b",
            transaction_id=query.query_id,
            owning_root_id=query.owning_local_root_id,
            domain_id=query.domain,
            source_context=context,
        )
        assert binding.binding_state == expected_state
        assert binding.transaction_id == binding.query_id == query.query_id
        assert binding.context_available is True
        assert binding.direct_informational_reuse_eligible is direct
        assert binding.lineage_state == "VALIDATED"
        assert binding.freshness_state == ("CURRENT" if direct else "STALE")
        assert binding.report_sha256 == hashlib.sha256(
            canonical_json_bytes_v01(
                resolution.drs_resolution_report_to_plain_data_v01(
                    family["report"]
                )
            )
        ).hexdigest()
        with pytest.raises(
            ValueError, match="^g2c_g2b_query_transaction_mismatch$"
        ):
            router.build_execution_mode_g2b_binding_v01(
                request_id="request:g2c:c2:g2b",
                transaction_id="transaction:g2c:c2:foreign",
                owning_root_id=query.owning_local_root_id,
                domain_id=query.domain,
                source_context=context,
            )
        with pytest.raises(ValueError, match="^g2c_g2b_use_time_invalid$"):
            router.build_execution_mode_g2b_binding_v01(
                request_id="request:g2c:c2:g2b",
                transaction_id=query.query_id,
                owning_root_id=query.owning_local_root_id,
                domain_id=query.domain,
                source_context=replace(context, g2b_use_time=query.evaluation_time + 1),
            )

    direct_family = _c2_g2b_direct_family()
    query = direct_family["report"].query
    bsep = _c2_bsep_family(
        request_id="request:g2c:c2:g2b", domain_id=query.domain
    )
    direct_context = _c2_source_context(
        bsep=bsep,
        evaluation_time=query.evaluation_time,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "e" * 64,
        g2b=direct_family,
    )
    with pytest.raises(ValueError, match="^g2c_g2b_binding_state_derivation_mismatch$"):
        router.build_execution_mode_g2b_binding_v01(
            request_id="request:g2c:c2:g2b",
            transaction_id=query.query_id,
            owning_root_id=query.owning_local_root_id,
            domain_id=query.domain,
            source_context=replace(
                direct_context,
                g2b_root_kernel=None,
                g2b_root_decision_input=None,
                g2b_root_decision_result=None,
            ),
        )
    assert "binding_state" not in inspect.signature(
        router.build_execution_mode_g2b_binding_v01
    ).parameters


def _c2_contextual_case(
    source_kind: str,
) -> tuple[router.ExecutionModeRouterInputV01, router.ExecutionModeSourceContextV01]:
    request_id = f"request:g2c:c2:contextual:{source_kind}"
    transaction_id = f"transaction:g2c:c2:contextual:{source_kind}"
    owning_root_id = "root:g2c:c2:contextual"
    domain_id = "G2C_C2_CONTEXTUAL_DOMAIN"
    evaluation_time = 200
    replay_family = None
    g2a_family = None
    g2b_family = None
    action_class = "NON_ACTION"
    action_relation = "NOT_APPLICABLE"
    if source_kind == "replay":
        replay_family = _c2_replay_family(domain_id)
    elif source_kind in {"g2b_context", "g2b_direct"}:
        g2b_family = (
            _c2_g2b_context_family()
            if source_kind == "g2b_context"
            else _c2_g2b_direct_family()
        )
        query = g2b_family["report"].query
        transaction_id = query.query_id
        owning_root_id = query.owning_local_root_id
        domain_id = query.domain
        evaluation_time = query.evaluation_time
    elif source_kind == "g2a":
        evaluation_time = 1783470602
        action_class = "ACTION"
        action_relation = "EXISTING_PACKET_ATTEMPT"
        source_g2a = _c2_g2a_present_family(
            evaluation_time=evaluation_time,
            evaluation_time_source="runtime:g2c:c2:snapshot",
            evaluation_context_id="emlocal_v01:" + "0" * 64,
        )
        canonical = (
            source_g2a.registry.action_packet_lifecycle_entries[0]
            .root_bound_genesis.canonical_projection
        )
        transaction_id = canonical.transaction_id
        owning_root_id = canonical.owning_local_root_id
    snapshot = _c2_snapshot(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        evaluation_time=evaluation_time,
        action_class=action_class,
        action_packet_relation=action_relation,
    )
    if source_kind == "g2a":
        g2a_family = _c2_g2a_present_family(
            evaluation_time=evaluation_time,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        )
    bsep = _c2_bsep_family(request_id=request_id, domain_id=domain_id)
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=evaluation_time,
        evaluation_time_source=snapshot.created_by,
        evaluation_context_id=snapshot.local_routing_snapshot_id,
        replay=replay_family,
        g2a=g2a_family,
        g2b=g2b_family,
    )
    common = {
        "request_id": request_id,
        "transaction_id": transaction_id,
        "owning_root_id": owning_root_id,
        "domain_id": domain_id,
    }
    bsep_binding = router.build_execution_mode_bsep_binding_v01(
        **common, source_context=context
    )
    replay_binding = (
        router.build_execution_mode_replay_binding_v01(
            **common, source_context=context
        )
        if replay_family
        else router.build_execution_mode_replay_not_applicable_binding_v01(**common)
    )
    g2a_binding = (
        router.build_execution_mode_g2a_binding_v01(
            **common, source_context=context
        )
        if g2a_family
        else router.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=evaluation_time,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        )
    )
    g2b_binding = (
        router.build_execution_mode_g2b_binding_v01(
            **common, source_context=context
        )
        if g2b_family
        else router.build_execution_mode_g2b_not_applicable_binding_v01(**common)
    )
    value = router.build_execution_mode_router_input_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        bsep_binding=bsep_binding,
        local_routing_snapshot=snapshot,
        replay_binding=replay_binding,
        g2a_binding=g2a_binding,
        g2b_binding=g2b_binding,
    )
    return value, context


@pytest.mark.parametrize(
    "source_kind",
    ("absent", "replay", "g2b_context", "g2b_direct", "g2a"),
)
def test_c2_contextual_router_input_rebuilds_complete_bindings(source_kind):
    value, context = _c2_contextual_case(source_kind)
    report = router.validate_execution_mode_router_input_against_sources_v01(
        router_input=value,
        source_context=context,
    )
    assert report.validation_status == "PASS"
    assert report.validation_target == "ROUTER_INPUT_AGAINST_SOURCES"
    assert report.validated_artifact_id == value.router_input_id
    assert report.failure_stage == "NONE"
    assert report.return_to_root_required is False
    assert report.reason_codes == report.source_reason_codes == ()
    expected_traces = tuple(
        sorted(
            {
                value.bsep_binding.business_request_packet_id,
                value.bsep_binding.bsep_binding_id,
                value.local_routing_snapshot.local_routing_snapshot_id,
                value.replay_binding.replay_binding_id,
                value.g2a_binding.g2a_binding_id,
                value.g2b_binding.g2b_binding_id,
            }
        )
    )
    assert value.trace_refs == expected_traces
    assert not any(
        (
            report.authority_created,
            report.permission_created,
            bool(report.real_world_effects_count),
        )
    )


def test_c2_contextual_substitution_is_total_and_fail_closed():
    value, context = _c2_contextual_case("absent")
    substituted = replace(
        value,
        bsep_binding=replace(
            value.bsep_binding,
            source_packet_sha256="f" * 64,
        ),
    )
    substituted = replace(
        substituted,
        router_input_id=router.rebuild_execution_mode_router_input_identity_v01(
            substituted
        ),
    )
    report = router.validate_execution_mode_router_input_against_sources_v01(
        router_input=substituted,
        source_context=context,
    )
    assert report.validation_status == "FAIL_CLOSED"
    assert report.failure_stage in {"STRUCTURAL", "BSEP"}
    assert report.return_to_root_required is True
    assert report.reason_codes
    arbitrary = router.validate_execution_mode_router_input_against_sources_v01(
        router_input=object(),  # type: ignore[arg-type]
        source_context=object(),  # type: ignore[arg-type]
    )
    assert arbitrary.validation_status == "FAIL_CLOSED"
    assert arbitrary.validated_artifact_id is None
    assert arbitrary.request_id is None
    assert arbitrary.transaction_id is None
    assert arbitrary.owning_root_id is None
    assert arbitrary.domain_id is None


def test_c2_exact_bsep_source_and_evidence_item_key_sets():
    bsep = _c2_bsep_family()
    expected = {
        "business": C2_BSEP_BUSINESS_KEYS,
        "route": C2_BSEP_ROUTE_KEYS,
        "proposal": C2_BSEP_PROPOSAL_KEYS,
        "rationale": C2_BSEP_RATIONALE_KEYS,
        "packet": C2_BSEP_PACKET_KEYS,
    }
    for family_name, expected_keys in expected.items():
        assert len(bsep[family_name]) == len(expected_keys)
        assert set(bsep[family_name]) == set(expected_keys)
    assert semantic_adapter.ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS == (
        C2_BSEP_PROPOSAL_KEYS
    )
    assert set(router._BSEP_BUSINESS_REQUEST_KEYS) == set(C2_BSEP_BUSINESS_KEYS)
    assert set(router._BSEP_ROUTE_CONTEXT_KEYS) == set(C2_BSEP_ROUTE_KEYS)
    assert set(router._BSEP_STRUCTURED_RATIONALE_KEYS) == set(
        C2_BSEP_RATIONALE_KEYS
    )
    assert set(router._BSEP_PACKET_KEYS) == set(C2_BSEP_PACKET_KEYS)
    assert router._BSEP_EVIDENCE_ITEM_FIELDS == C2_BSEP_EVIDENCE_FIELDS
    assert set(router._BSEP_EVIDENCE_ITEM_KEYS) == set(
        C2_BSEP_EVIDENCE_ITEM_KEYS
    )
    for field_name in C2_BSEP_EVIDENCE_FIELDS:
        items = bsep["packet"][field_name]
        assert type(items) is tuple
        assert items
        for item in items:
            assert type(item) is dict
            assert set(item) == set(C2_BSEP_EVIDENCE_ITEM_KEYS)


def test_c2_bsep_public_source_validator_order_is_preserved(monkeypatch):
    calls: list[str] = []
    validator_names = (
        "validate_business_request_context_packet",
        "validate_orchestrator_route_context_packet",
        "validate_orchestrator_semantic_reasoning_proposal",
        "validate_orchestrator_structured_rationale",
        "validate_bounded_semantic_evidence_packet",
    )
    for name in validator_names:
        original = getattr(router, name)

        def wrapped(*args, _name=name, _original=original, **kwargs):
            calls.append(_name)
            return _original(*args, **kwargs)

        monkeypatch.setattr(router, name, wrapped)
    bsep = _c2_bsep_family()
    binding = router.build_execution_mode_bsep_binding_v01(
        request_id="request:g2c:c2:test",
        transaction_id="transaction:g2c:c2:test",
        owning_root_id="root:g2c:c2:test",
        domain_id="G2C_C2_TEST_DOMAIN",
        source_context=_c2_context_for_bsep(bsep),
    )
    assert binding.binding_state == "BOUNDED_SEMANTIC_EVIDENCE_BOUND"
    assert tuple(calls) == validator_names


_C2_TOP_LEVEL_FOREIGN_FIELDS = (
    ("extra_benign", "bounded"),
    ("accepted", True),
    ("authority_created", True),
    ("permission_created", True),
    ("effect_created", True),
    ("topology_created", True),
    ("execution_authorized", True),
    ("provider_selected_mode", "cloud_llm"),
)


@pytest.mark.parametrize(
    ("family_name", "expected_reason"),
    (
        ("business", "g2c_business_request_invalid"),
        ("route", "g2c_route_context_invalid"),
        ("proposal", "g2c_semantic_proposal_invalid"),
        ("rationale", "g2c_structured_rationale_invalid"),
        ("packet", "g2c_bsep_invalid"),
    ),
)
@pytest.mark.parametrize(("foreign_key", "foreign_value"), _C2_TOP_LEVEL_FOREIGN_FIELDS)
def test_c2_bsep_top_level_foreign_fields_fail_before_digest(
    family_name,
    expected_reason,
    foreign_key,
    foreign_value,
    monkeypatch,
):
    bsep = _c2_bsep_family()
    changed = {**bsep[family_name], foreign_key: foreign_value}
    bsep = (
        _c2_rebind_rationale(bsep, changed)
        if family_name == "rationale"
        else {**bsep, family_name: changed}
    )
    digest_calls: list[object] = []
    original_sha = router._plain_sha256

    def tracked_sha(value):
        digest_calls.append(value)
        return original_sha(value)

    monkeypatch.setattr(router, "_plain_sha256", tracked_sha)
    _c2_assert_bsep_failure(bsep, expected_reason)
    assert digest_calls == []


@pytest.mark.parametrize("field_name", C2_BSEP_EVIDENCE_FIELDS)
@pytest.mark.parametrize(
    ("foreign_key", "foreign_value"),
    (
        ("extra_benign", "bounded"),
        ("accepted", True),
        ("authority_created", True),
        ("effect_created", True),
    ),
)
def test_c2_bsep_evidence_item_foreign_fields_rejected(
    field_name,
    foreign_key,
    foreign_value,
):
    bsep = _c2_bsep_family()
    items = list(bsep["packet"][field_name])
    items[0] = {**items[0], foreign_key: foreign_value}
    bsep = {
        **bsep,
        "packet": {**bsep["packet"], field_name: tuple(items)},
    }
    _c2_assert_bsep_failure(bsep, "g2c_bsep_invalid")


@pytest.mark.parametrize(
    "claim_key",
    (
        "truth_claimed",
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
        "connector_command_claimed",
        "drs_write_claimed",
        "action_commit_packet_claimed",
        "root_bypass_claimed",
        "bypass_root_claimed",
        "plan_graph_claimed",
        "authority_created",
        "permission_created",
        "topology_created",
        "effect_created",
        "execution_authorized",
    ),
)
def test_c2_nested_rationale_authority_claims_rejected(claim_key):
    bsep = _c2_bsep_family()
    rationale = {
        **bsep["rationale"],
        "observed_semantics": (
            {"summary": "Bounded nested explanation.", claim_key: True},
        ),
    }
    _c2_assert_bsep_failure(
        _c2_rebind_rationale(bsep, rationale),
        "g2c_structured_rationale_invalid",
    )


def test_c2_nested_rationale_false_claims_and_zero_counters_are_safe():
    bsep = _c2_bsep_family()
    nested = {
        "summary": "Bounded nested explanation.",
        **{name: False for name in router._SOURCE_FORBIDDEN_TRUE_FIELDS},
        **{
            name: 0 for name in router._SOURCE_ZERO_OPERATION_COUNTER_FIELDS
        },
    }
    rationale = {
        **bsep["rationale"],
        "observed_semantics": (nested,),
    }
    rebound = _c2_rebind_rationale(bsep, rationale)
    binding = router.build_execution_mode_bsep_binding_v01(
        request_id="request:g2c:c2:test",
        transaction_id="transaction:g2c:c2:test",
        owning_root_id="root:g2c:c2:test",
        domain_id="G2C_C2_TEST_DOMAIN",
        source_context=_c2_context_for_bsep(rebound),
    )
    assert binding.binding_state == "BOUNDED_SEMANTIC_EVIDENCE_BOUND"


@pytest.mark.parametrize(
    ("unsafe_key", "unsafe_value"),
    (
        ("authority_claimed", True),
        ("final_output_claimed", True),
        ("authority_created", True),
        ("effect_created", True),
        ("real_world_effects_count", 1),
        ("provider_selected_mode", "cloud_llm"),
    ),
)
def test_c2_business_source_ref_recursive_safety_rejects_unsafe_values(
    unsafe_key,
    unsafe_value,
):
    bsep = _c2_bsep_family()
    source_ref = {
        "source": "G2C_TEST_BUSINESS_SOURCE_V01",
        "packet_id": "context_packet:g2c:c2:upstream",
        unsafe_key: unsafe_value,
    }
    bsep = {
        **bsep,
        "business": {**bsep["business"], "source_refs": (source_ref,)},
    }
    _c2_assert_bsep_failure(bsep, "g2c_business_request_invalid")


def test_c2_business_source_ref_false_and_zero_claims_are_safe():
    bsep = _c2_bsep_family()
    source_ref = {
        "source": "G2C_TEST_BUSINESS_SOURCE_V01",
        "packet_id": "context_packet:g2c:c2:upstream",
        "authority_claimed": False,
        "final_output_claimed": False,
        "authority_created": False,
        "effect_created": False,
        "real_world_effects_count": 0,
    }
    bsep = {
        **bsep,
        "business": {**bsep["business"], "source_refs": (source_ref,)},
    }
    binding = router.build_execution_mode_bsep_binding_v01(
        request_id="request:g2c:c2:test",
        transaction_id="transaction:g2c:c2:test",
        owning_root_id="root:g2c:c2:test",
        domain_id="G2C_C2_TEST_DOMAIN",
        source_context=_c2_context_for_bsep(bsep),
    )
    assert binding.binding_state == "BOUNDED_SEMANTIC_EVIDENCE_BOUND"


@pytest.mark.parametrize(
    "family_maker",
    (_c2_g2b_context_family, _c2_g2b_direct_family),
    ids=("resolution_context", "direct_reuse"),
)
@pytest.mark.parametrize(
    ("mismatch", "expected_reason"),
    (
        ("request_equals_transaction", "g2c_transaction_binding_mismatch"),
        ("foreign_transaction", "g2c_g2b_query_transaction_mismatch"),
        ("foreign_root", "g2c_root_binding_mismatch"),
        ("foreign_domain", "g2c_domain_binding_mismatch"),
        ("wrong_use_time", "g2c_g2b_use_time_invalid"),
        ("bool_use_time", "g2c_g2b_use_time_invalid"),
    ),
)
def test_c2_g2b_bound_state_reason_ownership(
    family_maker,
    mismatch,
    expected_reason,
):
    family = family_maker()
    query = family["report"].query
    bsep = _c2_bsep_family(
        request_id="request:g2c:c2:g2b",
        domain_id=query.domain,
    )
    context = _c2_source_context(
        bsep=bsep,
        evaluation_time=query.evaluation_time,
        evaluation_time_source="runtime:g2c:c2:snapshot",
        evaluation_context_id="emlocal_v01:" + "e" * 64,
        g2b=family,
    )
    arguments = {
        "request_id": "request:g2c:c2:g2b",
        "transaction_id": query.query_id,
        "owning_root_id": query.owning_local_root_id,
        "domain_id": query.domain,
        "source_context": context,
    }
    if mismatch == "request_equals_transaction":
        arguments["request_id"] = query.query_id
    elif mismatch == "foreign_transaction":
        arguments["transaction_id"] = "transaction:g2c:c2:foreign"
    elif mismatch == "foreign_root":
        arguments["owning_root_id"] = "root:g2c:c2:foreign"
    elif mismatch == "foreign_domain":
        arguments["domain_id"] = "G2C_C2_FOREIGN_DOMAIN"
    elif mismatch == "wrong_use_time":
        arguments["source_context"] = replace(
            context,
            g2b_use_time=query.evaluation_time + 1,
        )
    else:
        arguments["source_context"] = replace(context, g2b_use_time=True)
    with pytest.raises(ValueError) as exc:
        router.build_execution_mode_g2b_binding_v01(**arguments)
    assert str(exc.value) == expected_reason


def test_c2_contextual_source_owned_reason_separation():
    router_input, source_context = _c2_contextual_case("absent")
    proposal = dict(source_context.bsep_orchestrator_proposal)
    proposal.pop("guard_reasoning")
    report = router.validate_execution_mode_router_input_against_sources_v01(
        router_input=router_input,
        source_context=replace(
            source_context,
            bsep_orchestrator_proposal=proposal,
        ),
    )
    assert report.validation_status == "FAIL_CLOSED"
    assert report.failure_stage == "BSEP"
    assert report.reason_codes == ("g2c_semantic_proposal_invalid",)
    assert report.source_reason_codes == (
        "missing_required_field:guard_reasoning",
        "semantic_reasoning_missing_field:guard_reasoning",
    )
    assert set(report.reason_codes).isdisjoint(report.source_reason_codes)
    assert report.return_to_root_required is True
    assert report.authority_created is False
    assert report.permission_created is False
    assert report.real_world_effects_count == 0
    assert not hasattr(router, "build_execution_mode_proposal_v01")
