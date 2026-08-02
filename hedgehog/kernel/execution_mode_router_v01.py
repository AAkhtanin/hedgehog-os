"""Deterministic contracts for Gate 2 G2-C ExecutionModeRouter.

G2-C1 owns canonical types and structural validation. G2-C2 adds actual source
binding and contextual input validation. G2-C3 adds feasibility, deterministic
selection, terminal handling, and bounded proposal construction. G2-C4 adds
existing-Root projection, contextual ABI artifacts, Transition-profile use,
and bounded RouteEligibility. The module creates no topology or effect.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import math
import re
import types
import unicodedata
from typing import get_args, get_origin, get_type_hints

import hedgehog
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.abi_v01 import (
    KernelArtifactV01,
    build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_bundle_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    build_root_decision_input_v01,
    build_root_decision_kernel_v01,
    decide_root_v01,
    root_decision_result_to_plain_dict_v01,
    validate_root_decision_input_v01,
    validate_root_decision_kernel_v01,
    validate_root_decision_result_v01,
)
from hedgehog.kernel.semantic_work_v01 import (
    ActorContributionV01,
    NormalizedClaimV01,
    RootReviewPacketV01,
    SemanticWorkRequestV01,
    build_actor_contribution_v01,
    build_evidence_binding_v01,
    build_normalized_claim_v01,
    build_root_review_packet_from_contributions_v01,
    build_semantic_work_request_v01,
    validate_actor_contribution_v01,
    validate_root_review_packet_v01,
    validate_semantic_work_request_v01,
)
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
    validate_component_trust_profiles_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    ActionPacketTransitionRegistryProfileV01,
    TransitionDecisionV01,
    TransitionRegistryV01,
    build_execution_mode_transition_registry_profile_v01 as _build_execution_mode_transition_registry_profile_v01,
    rebuild_execution_mode_transition_decision_identity_v01 as _rebuild_execution_mode_transition_decision_identity_v01,
    validate_execution_mode_transition_decision_v01 as _validate_execution_mode_transition_decision_v01,
    validate_execution_mode_transition_registry_profile_v01 as _validate_execution_mode_transition_registry_profile_v01,
)


MODULE_ID = "kernel_execution_mode_router_v01"
SLICE_ID = "gate2_g2c4_execution_mode_router_root_abi_transition_route_eligibility"
EXECUTION_MODE_ROUTER_VERSION = "v0.1"

TOTAL_G2C_TYPE_COUNT = 13
SERIALIZED_IDENTITY_TYPE_COUNT = 12
RUNTIME_ONLY_SOURCE_CONTEXT_TYPE_COUNT = 1
LOCAL_MODE_PROFILE_COUNT = 8
ROUTER_INPUT_FIELD_COUNT = 10
ROOT_REVIEW_INPUT_FIELD_COUNT = 21
ROOT_DECISION_FIELD_COUNT = 30
CANONICAL_MODE_COUNT = 10
PUBLIC_G2C_FUNCTION_COUNT = 74
PUBLIC_G2C_REASON_COUNT = 100
VALIDATION_TARGET_COUNT = 20

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1
MIN_EPOCH_SECONDS = -62135596800
MAX_EPOCH_SECONDS = 253402300799
MAX_TUPLE_MEMBERS = 64

CANONICAL_EXECUTION_MODES_V01 = (
    "deterministic",
    "sealed_replay",
    "direct_informational_reuse",
    "memory_informed",
    "local_slm",
    "cloud_llm",
    "full_semantic",
    "full_fractal",
    "blocked",
    "needs_user",
)
EXECUTABLE_EXECUTION_MODES_V01 = CANONICAL_EXECUTION_MODES_V01[:8]
EXECUTION_MODE_SAFE_DEPTH_RANKS_V01 = (
    ("deterministic", 10),
    ("sealed_replay", 20),
    ("direct_informational_reuse", 30),
    ("memory_informed", 40),
    ("local_slm", 50),
    ("cloud_llm", 50),
    ("full_semantic", 60),
    ("full_fractal", 70),
)

_MODE_POSITIVE_REASONS_V01 = {
    "deterministic": "g2c_deterministic_feasible",
    "sealed_replay": "g2c_sealed_replay_feasible",
    "direct_informational_reuse": "g2c_direct_informational_reuse_feasible",
    "memory_informed": "g2c_memory_informed_feasible",
    "local_slm": "g2c_local_slm_feasible",
    "cloud_llm": "g2c_cloud_llm_feasible",
    "full_semantic": "g2c_full_semantic_feasible",
    "full_fractal": "g2c_full_fractal_feasible",
}
_MODE_DOWNSTREAM_COMPUTE_CLASSES_V01 = {
    "deterministic": "NONE",
    "sealed_replay": "NONE",
    "direct_informational_reuse": "NONE",
    "memory_informed": "MEMORY_INFORMED",
    "local_slm": "LOCAL_SLM",
    "cloud_llm": "CLOUD_LLM",
    "full_semantic": "FULL_SEMANTIC",
    "full_fractal": "FULL_FRACTAL",
    "blocked": "TERMINAL",
    "needs_user": "TERMINAL",
}
_MODE_DOWNSTREAM_CONSUMPTION_CLASSES_V01 = {
    "deterministic": "SHORTCUT_RETURN_TO_ROOT",
    "sealed_replay": "SHORTCUT_RETURN_TO_ROOT",
    "direct_informational_reuse": "SHORTCUT_RETURN_TO_ROOT",
    "memory_informed": "RUNTIME_TOPOLOGY_ELIGIBLE",
    "local_slm": "RUNTIME_TOPOLOGY_ELIGIBLE",
    "cloud_llm": "RUNTIME_TOPOLOGY_ELIGIBLE",
    "full_semantic": "RUNTIME_TOPOLOGY_ELIGIBLE",
    "full_fractal": "RUNTIME_TOPOLOGY_ELIGIBLE",
    "blocked": "TERMINAL_NO_CONSUMPTION",
    "needs_user": "TERMINAL_NO_CONSUMPTION",
}
_CAPABILITY_REQUIRED_MODES_V01 = (
    "deterministic",
    "memory_informed",
    "local_slm",
    "cloud_llm",
    "full_semantic",
    "full_fractal",
)
_NO_CAPABILITY_MODES_V01 = (
    "sealed_replay",
    "direct_informational_reuse",
    "blocked",
    "needs_user",
)
_TERMINAL_MODES_V01 = ("blocked", "needs_user")
_CANONICAL_MODE_INDEX_V01 = {
    mode: index for index, mode in enumerate(CANONICAL_EXECUTION_MODES_V01)
}
_ALLOWED_MISSING_EVIDENCE_CODES_V01 = (
    "g2c_required_evidence_missing",
    "g2c_capability_unavailable",
)
_LOCAL_NEGATIVE_REASONS_V01 = (
    "g2c_policy_forbidden",
    "g2c_scope_forbidden",
    "g2c_risk_forbidden",
    "g2c_privacy_forbidden",
    "g2c_capability_unavailable",
)
_EXECUTABLE_NEGATIVE_REASONS_V01 = (
    *_LOCAL_NEGATIVE_REASONS_V01,
    "g2c_required_evidence_missing",
    "g2c_action_shortcut_forbidden",
    "g2c_hard_block_present",
    "g2c_user_input_required",
)
_PROPOSAL_FEASIBILITY_FIELDS_V01 = ("ordered_feasibility_rows",)
_PROPOSAL_SELECTION_FIELDS_V01 = (
    "selected_mode",
    "selected_safe_depth_rank",
    "selected_local_mode_profile_id",
    "selected_expected_cost_units",
    "selected_feasibility_row_id",
)
_PROPOSAL_GEOMETRY_FIELDS_V01 = (
    "proposal_id",
    "source_input_id",
    "request_id",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "source_bsep_binding_id",
    "source_bsep_packet_id",
    "source_bsep_sha256",
    "source_local_routing_snapshot_id",
    "source_replay_binding_id",
    "source_g2a_binding_id",
    "source_g2b_binding_id",
    "proposed_scope_ref",
    "reason_codes",
    "required_downstream_capability_ids",
    "downstream_consumption_class",
    "downstream_action_packet_required",
    "root_review_required",
    "authority_created",
    "permission_created",
    "action_commit_packet_created",
    "receipt_created",
    "topology_created",
    "final_output_created",
    "drs_write_created",
    "real_world_effects_count",
)
_PROPOSAL_SOURCE_FIELDS_V01 = (
    "source_input_id",
    "source_bsep_binding_id",
    "source_bsep_packet_id",
    "source_bsep_sha256",
    "source_local_routing_snapshot_id",
    "source_replay_binding_id",
    "source_g2a_binding_id",
    "source_g2b_binding_id",
)

_G2C_ABI_PROFILE_ID_V01 = "execution_mode_router_g2c_abi_profile_v01"
_G2C_ABI_VERSION_V01 = "v1.0"
_G2C_SCHEMA_VERSION_V01 = "v0.1"
_G2C_ROOT_SOURCE_SUPPORT_DOMAIN_V01 = (
    "HEDGEHOG_EXECUTION_MODE_ROOT_SOURCE_SUPPORT_V01"
)
_G2C_ABI_RESERVED_KEYS_V01 = frozenset(
    {
        "abi_version", "artifact_id", "artifact_type", "schema_version",
        "transaction_id", "owner_root_id", "source_component",
        "authority_class", "lifecycle_state", "payload", "trace_refs",
        "parent_refs", "time_envelope",
    }
)
_G2C_PROPOSAL_ARTIFACT_DOMAIN_V01 = (
    "HEDGEHOG_EXECUTION_MODE_PROPOSAL_KERNEL_ARTIFACT_V01"
)
_G2C_DECISION_ARTIFACT_DOMAIN_V01 = (
    "HEDGEHOG_EXECUTION_MODE_DECISION_KERNEL_ARTIFACT_V01"
)
_G2C_ROUTE_ARTIFACT_DOMAIN_V01 = (
    "HEDGEHOG_EXECUTION_MODE_ROUTE_ELIGIBILITY_KERNEL_ARTIFACT_V01"
)

VALIDATION_TARGETS_V01 = (
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
    "SOURCE_CONTEXT_STRUCTURAL",
    "ROUTER_INPUT_AGAINST_SOURCES",
    "PROPOSAL_AGAINST_SOURCES",
    "ROOT_REVIEW_AGAINST_SOURCES",
    "ROOT_DECISION_AGAINST_SOURCE",
    "ROUTE_ELIGIBILITY_AGAINST_SOURCE",
    "ABI_PROFILE",
    "TRANSITION_PROFILE",
)
FAILURE_STAGES_V01 = (
    "NONE",
    "STRUCTURAL",
    "SOURCE_CONTEXT",
    "BUSINESS_REQUEST",
    "BSEP",
    "REPLAY",
    "G2A",
    "G2B",
    "LOCAL_PROFILE",
    "TIME_ENVELOPE",
    "FEASIBILITY",
    "SELECTION",
    "PROPOSAL",
    "ROOT_REVIEW",
    "ROOT_DECISION",
    "ABI",
    "TRANSITION",
    "ROUTE_ELIGIBILITY",
)

PUBLIC_G2C_REASON_CODES_V01 = (
    "g2c_exact_type_invalid",
    "g2c_scalar_invalid",
    "g2c_sequence_invalid",
    "g2c_identity_invalid",
    "g2c_identity_mismatch",
    "g2c_request_binding_mismatch",
    "g2c_transaction_binding_mismatch",
    "g2c_root_binding_mismatch",
    "g2c_domain_binding_mismatch",
    "g2c_time_envelope_invalid",
    "g2c_time_envelope_ref_identity_mismatch",
    "g2c_source_context_invalid",
    "g2c_source_context_structural_target_invalid",
    "g2c_source_object_absent",
    "g2c_source_object_substituted",
    "g2c_source_digest_mismatch",
    "g2c_source_validator_failed",
    "g2c_business_request_invalid",
    "g2c_business_request_ref_invalid",
    "g2c_route_context_invalid",
    "g2c_semantic_proposal_invalid",
    "g2c_structured_rationale_invalid",
    "g2c_bsep_invalid",
    "g2c_replay_binding_invalid",
    "g2c_g2a_relation_invalid",
    "g2c_g2a_present_inspection_invalid",
    "g2c_g2b_binding_invalid",
    "g2c_g2b_binding_state_derivation_mismatch",
    "g2c_g2b_query_transaction_mismatch",
    "g2c_g2b_shortcut_invalid",
    "g2c_g2b_use_time_invalid",
    "g2c_local_mode_profile_invalid",
    "g2c_local_mode_profile_set_invalid",
    "g2c_mode_profile_set_identity_mismatch",
    "g2c_policy_forbidden",
    "g2c_scope_forbidden",
    "g2c_risk_forbidden",
    "g2c_privacy_forbidden",
    "g2c_capability_unavailable",
    "g2c_cost_invalid",
    "g2c_noncanonical_mode",
    "g2c_required_evidence_missing",
    "g2c_action_shortcut_forbidden",
    "g2c_deterministic_feasible",
    "g2c_sealed_replay_feasible",
    "g2c_direct_informational_reuse_feasible",
    "g2c_memory_informed_feasible",
    "g2c_local_slm_feasible",
    "g2c_cloud_llm_feasible",
    "g2c_full_semantic_feasible",
    "g2c_full_fractal_feasible",
    "g2c_hard_block_present",
    "g2c_user_input_required",
    "g2c_no_safe_mode",
    "g2c_feasibility_row_invalid",
    "g2c_selection_invalid",
    "g2c_selection_tie_break_applied",
    "g2c_proposal_rows_invalid",
    "g2c_proposal_selected_row_mismatch",
    "g2c_proposal_sources_valid",
    "g2c_review_action_invalid",
    "g2c_terminal_review_mismatch",
    "g2c_scope_narrowing_invalid",
    "g2c_root_input_invalid",
    "g2c_root_result_invalid",
    "g2c_root_mapping_invalid",
    "g2c_policy_snapshot_binding_mismatch",
    "g2c_terminal_contribution_scope_mismatch",
    "g2c_root_accept_projected",
    "g2c_root_narrow_projected",
    "g2c_root_reject_projected",
    "g2c_root_blocked_projected",
    "g2c_root_needs_user_projected",
    "g2c_abi_profile_invalid",
    "g2c_abi_reserved_payload_key",
    "g2c_abi_artifact_identity_mismatch",
    "g2c_abi_parent_lineage_mismatch",
    "g2c_abi_bundle_validation_failed",
    "g2c_abi_projection_substituted",
    "g2c_transition_profile_invalid",
    "g2c_transition_registry_identity_mismatch",
    "g2c_transition_decision_invalid",
    "g2c_transition_decision_identity_mismatch",
    "g2c_transition_root_review_required",
    "g2c_transition_route_accept_allowed",
    "g2c_transition_scope_narrow_allowed",
    "g2c_transition_reject_recorded",
    "g2c_transition_blocked_recorded",
    "g2c_transition_needs_user_recorded",
    "g2c_transition_guard_invalid",
    "g2c_transition_root_commit_required",
    "g2c_transition_substituted",
    "g2c_proposal_transition_missing",
    "g2c_proposal_transition_substituted",
    "g2c_post_root_transition_missing",
    "g2c_post_root_transition_substituted",
    "g2c_route_eligibility_invalid",
    "g2c_route_decision_bypass_forbidden",
    "g2c_invalid_source_no_proposal",
    "g2c_fail_closed_return_to_root",
)

PUBLIC_G2C_FUNCTIONS_V01 = (
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


@dataclass(frozen=True)
class ExecutionModeBSEPBindingV01:
    bsep_binding_id: str
    binding_state: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    business_request_packet_id: str
    business_request_packet_sha256: str
    source_packet_id: str
    source_packet_sha256: str
    source_packet_type: str
    source_schema_version: str
    source_route_context_packet_id: str
    source_route_context_sha256: str
    source_route_id: str
    source_proposal_id: str
    source_proposal_sha256: str
    source_structured_rationale_ref: str
    source_structured_rationale_sha256: str
    source_family_sha256: str
    source_domain: str
    source_role: str
    target_role: str
    source_reason_codes: tuple[str, ...]
    root_final_authority_preserved: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    final_output_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeReplayBindingV01:
    replay_binding_id: str
    binding_state: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    replay_id: str | None
    source_replay_sha256: str | None
    replay_status: str
    source_manifest_id: str | None
    reconstructed_manifest_id: str | None
    anchor_publication_id: str | None
    anchored_verification_id: str | None
    source_domain_projection_id: str | None
    reconstructed_domain_projection_id: str | None
    package_id: str | None
    logical_package_ref: str | None
    source_package_content_hash: str | None
    reconstructed_package_content_hash: str | None
    integrity_verified: bool
    continuity_verified: bool
    anchor_verified: bool
    evidence_refs: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeG2ABindingV01:
    g2a_binding_id: str
    binding_state: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    source_inspection_sha256: str | None
    inspection_profile_id: str | None
    registry_id: str | None
    packet_id: str | None
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    historical_lifecycle_state: str
    failed_provenance: str | None
    transition_event_count: int
    execution_attempt_count: int
    idempotency_disposition: str
    reservation_owner_packet_id: str | None
    terminal_receipt_ref: str | None
    lifecycle_terminal: bool
    eligible_for_corridor_revalidation: bool
    present_eligibility_status: str
    present_executable: bool
    retry_eligible: bool
    source_reason_codes: tuple[str, ...]
    transition_history_sha256: str | None
    disposition_history_sha256: str | None
    historical_result_unchanged: bool
    authority_created: bool
    permission_created: bool
    packet_created: bool
    receipt_created: bool
    adapter_calls: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeG2BBindingV01:
    g2b_binding_id: str
    binding_state: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    report_id: str | None
    report_sha256: str | None
    semantic_address_id: str | None
    query_id: str | None
    query_evaluation_ids: tuple[str, ...]
    eligible_candidate_ids: tuple[str, ...]
    ranked_candidate_ids: tuple[str, ...]
    selected_candidate_id: str | None
    retrieval_plan_id: str | None
    memory_descent_result_id: str | None
    root_shortcut_projection_id: str | None
    reuse_certificate_id: str | None
    compatibility_projection_ids: tuple[str, ...]
    compatibility_projection_set_sha256: str | None
    use_time: int | None
    source_root_kernel_id: str | None
    source_root_decision_input_id: str | None
    source_root_decision_id: str | None
    source_root_decision_sha256: str | None
    freshness_state: str
    lineage_state: str
    quarantine_present: bool
    deadend_present: bool
    context_available: bool
    direct_informational_reuse_eligible: bool
    source_reason_codes: tuple[str, ...]
    persistent_records_unchanged: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    capability_created: bool
    topology_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeLocalModeProfileV01:
    local_mode_profile_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    mode: str
    policy_snapshot_id: str
    capability_snapshot_id: str
    cost_model_id: str
    policy_allowed: bool
    scope_allowed: bool
    risk_allowed: bool
    privacy_allowed: bool
    capability_state: str
    capability_id: str | None
    cost_unit: str
    cost_units: int
    local_reason_codes: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeLocalRoutingSnapshotV01:
    local_routing_snapshot_id: str
    created_by: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    request_class: str
    action_class: str
    action_packet_relation: str
    scope_class: str
    scope_ref: str
    permitted_narrower_scope_refs: tuple[str, ...]
    risk_class: str
    policy_snapshot_id: str
    capability_snapshot_id: str
    cost_model_id: str
    required_user_input_state: str
    hard_block_state: str
    evaluation_time_epoch_seconds: int
    pt_created_at_utc: str
    kt_asof_utc: str
    et_observed_at_utc: str
    ct_session_anchor: str
    ttl_seconds: int
    freshness_class: str
    valid_from_utc: str
    valid_to_utc: str
    time_envelope_ref: str
    mode_profile_set_id: str
    mode_profile_set_sha256: str
    mode_profiles: tuple[ExecutionModeLocalModeProfileV01, ...]
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeRouterInputV01:
    router_input_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    bsep_binding: ExecutionModeBSEPBindingV01
    local_routing_snapshot: ExecutionModeLocalRoutingSnapshotV01
    replay_binding: ExecutionModeReplayBindingV01
    g2a_binding: ExecutionModeG2ABindingV01
    g2b_binding: ExecutionModeG2BBindingV01
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionModeFeasibilityRowV01:
    feasibility_row_id: str
    source_input_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    mode: str
    category: str
    safe_depth_rank: int | None
    feasibility_status: str
    local_mode_profile_id: str | None
    required_evidence_refs: tuple[str, ...]
    satisfied_evidence_refs: tuple[str, ...]
    missing_evidence_codes: tuple[str, ...]
    reason_codes: tuple[str, ...]
    required_capability_id: str | None
    cost_units: int | None
    downstream_compute_class: str
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeProposalV01:
    proposal_id: str
    source_input_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    source_bsep_binding_id: str
    source_bsep_packet_id: str
    source_bsep_sha256: str
    source_local_routing_snapshot_id: str
    source_replay_binding_id: str
    source_g2a_binding_id: str
    source_g2b_binding_id: str
    selected_mode: str
    selected_safe_depth_rank: int | None
    selected_local_mode_profile_id: str | None
    selected_expected_cost_units: int | None
    proposed_scope_ref: str | None
    ordered_feasibility_rows: tuple[ExecutionModeFeasibilityRowV01, ...]
    selected_feasibility_row_id: str
    reason_codes: tuple[str, ...]
    required_downstream_capability_ids: tuple[str, ...]
    downstream_consumption_class: str
    downstream_action_packet_required: bool
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    topology_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class RootExecutionModeReviewInputV01:
    root_review_input_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    proposal_id: str
    router_input_id: str
    proposal_artifact_id: str
    proposal_transition_decision_id: str
    created_by: str
    review_action: str
    proposed_mode: str
    proposed_scope_ref: str | None
    accepted_scope_ref: str | None
    scope_narrowing_proof_id: str | None
    narrowing_basis_refs: tuple[str, ...]
    policy_snapshot_id: str
    evaluation_time_epoch_seconds: int
    time_envelope_ref: str
    root_local_context_id: str
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class RootExecutionModeDecisionV01:
    decision_id: str
    root_review_input_id: str
    proposal_id: str
    router_input_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    outcome: str
    accepted_mode: str | None
    accepted_scope_ref: str | None
    scope_narrowing_proof_id: str | None
    downstream_consumption_class: str
    downstream_action_packet_required: bool
    source_root_decision_id: str
    source_root_decision_input_id: str
    source_root_decision: str
    source_root_reason_code: str
    source_root_transition_decision_id: str
    source_root_transition_decision: str
    reason_codes: tuple[str, ...]
    route_eligibility_candidate: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    topology_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeValidationReportV01:
    validation_report_id: str
    validation_target: str
    validated_artifact_id: str | None
    request_id: str | None
    transaction_id: str | None
    owning_root_id: str | None
    domain_id: str | None
    validation_status: str
    failure_stage: str
    return_to_root_required: bool
    reason_codes: tuple[str, ...]
    source_reason_codes: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ExecutionModeSourceContextV01:
    business_request_context_packet: dict[str, object]
    bsep_packet: dict[str, object]
    bsep_route_context_packet: dict[str, object]
    bsep_orchestrator_proposal: dict[str, object]
    bsep_structured_rationale: dict[str, object]
    sealed_replay_evidence: hedgehog.evidence.sealed_replay_evidence_v01.SealedReplayEvidenceV01 | None
    replay_source_manifest: hedgehog.evidence.sealed_package_v01.SealedPackageManifestV01 | None
    replay_source_domain_projection: hedgehog.evidence.sealed_evidence_profile_v01.DomainEvidenceProjectionV01 | None
    replay_source_safe_file_contents: tuple[bytes, ...]
    replay_anchor_publication: hedgehog.evidence.external_anchor_v01.ExternalAnchorPublicationV01 | None
    replay_anchored_verification: hedgehog.evidence.external_anchor_v01.AnchoredPackageVerificationV01 | None
    replay_supplied_anchor_publication_id: str | None
    replay_reconstructed_manifest: hedgehog.evidence.sealed_package_v01.SealedPackageManifestV01 | None
    replay_reconstructed_domain_projection: hedgehog.evidence.sealed_evidence_profile_v01.DomainEvidenceProjectionV01 | None
    replay_reconstructed_safe_file_contents: tuple[bytes, ...]
    g2a_inspection: hedgehog.action_commit_packet_v02.ActionPacketPresentEligibilityInspectionV01 | None
    g2a_registry: hedgehog.action_commit_packet_v02.ActionCommitPacketRegistryV02 | None
    g2a_packet_id: str | None
    g2a_corridor: hedgehog.action_commit_packet_v02.ContractFulfillmentCorridorV01 | None
    g2a_corridor_step: hedgehog.action_commit_packet_v02.CorridorStepV01 | None
    g2a_current_dependency_observations: tuple[
        hedgehog.action_commit_packet_v02.ActionDependencyCurrentObservationV01, ...
    ]
    g2a_logical_time_bridge: hedgehog.action_commit_packet_v02.LogicalTimeBridgeV01 | None
    g2a_evaluation_time: int | None
    g2a_evaluation_time_source: str | None
    g2a_evaluation_context_id: str | None
    g2a_transition_registry_profile: ActionPacketTransitionRegistryProfileV01 | None
    g2b_resolution_report: hedgehog.drs_memory_resolution_v01.DRSResolutionReportV01 | None
    g2b_compatibility_projections: tuple[hedgehog.drs_g2b_compatibility_v01.LegacyDRSProjectionV01, ...]
    g2b_use_time: int | None
    g2b_root_kernel: RootDecisionKernelV01 | None
    g2b_root_decision_input: RootDecisionInputV01 | None
    g2b_root_decision_result: RootDecisionResultV01 | None
    g2b_writeback_evidence: None


G2C_TYPES_V01 = (
    ExecutionModeBSEPBindingV01,
    ExecutionModeReplayBindingV01,
    ExecutionModeG2ABindingV01,
    ExecutionModeG2BBindingV01,
    ExecutionModeLocalModeProfileV01,
    ExecutionModeLocalRoutingSnapshotV01,
    ExecutionModeRouterInputV01,
    ExecutionModeFeasibilityRowV01,
    ExecutionModeProposalV01,
    RootExecutionModeReviewInputV01,
    RootExecutionModeDecisionV01,
    ExecutionModeValidationReportV01,
    ExecutionModeSourceContextV01,
)
SERIALIZED_G2C_TYPES_V01 = G2C_TYPES_V01[:12]

_IDENTITY_PROFILES = {
    ExecutionModeBSEPBindingV01: (
        "bsep_binding_id",
        "HEDGEHOG_EXECUTION_MODE_BSEP_BINDING_V01",
        "embsep_v01:",
    ),
    ExecutionModeReplayBindingV01: (
        "replay_binding_id",
        "HEDGEHOG_EXECUTION_MODE_REPLAY_BINDING_V01",
        "emreplay_v01:",
    ),
    ExecutionModeG2ABindingV01: (
        "g2a_binding_id",
        "HEDGEHOG_EXECUTION_MODE_G2A_BINDING_V01",
        "emg2a_v01:",
    ),
    ExecutionModeG2BBindingV01: (
        "g2b_binding_id",
        "HEDGEHOG_EXECUTION_MODE_G2B_BINDING_V01",
        "emg2b_v01:",
    ),
    ExecutionModeLocalModeProfileV01: (
        "local_mode_profile_id",
        "HEDGEHOG_EXECUTION_MODE_LOCAL_MODE_PROFILE_V01",
        "emprofile_v01:",
    ),
    ExecutionModeLocalRoutingSnapshotV01: (
        "local_routing_snapshot_id",
        "HEDGEHOG_EXECUTION_MODE_LOCAL_ROUTING_SNAPSHOT_V01",
        "emlocal_v01:",
    ),
    ExecutionModeRouterInputV01: (
        "router_input_id",
        "HEDGEHOG_EXECUTION_MODE_ROUTER_INPUT_V01",
        "eminput_v01:",
    ),
    ExecutionModeFeasibilityRowV01: (
        "feasibility_row_id",
        "HEDGEHOG_EXECUTION_MODE_FEASIBILITY_ROW_V01",
        "emrow_v01:",
    ),
    ExecutionModeProposalV01: (
        "proposal_id",
        "HEDGEHOG_EXECUTION_MODE_PROPOSAL_V01",
        "emproposal_v01:",
    ),
    RootExecutionModeReviewInputV01: (
        "root_review_input_id",
        "HEDGEHOG_ROOT_EXECUTION_MODE_REVIEW_INPUT_V01",
        "emreview_v01:",
    ),
    RootExecutionModeDecisionV01: (
        "decision_id",
        "HEDGEHOG_ROOT_EXECUTION_MODE_DECISION_V01",
        "emdecision_v01:",
    ),
    ExecutionModeValidationReportV01: (
        "validation_report_id",
        "HEDGEHOG_EXECUTION_MODE_VALIDATION_REPORT_V01",
        "emvalidation_v01:",
    ),
}
G2C_IDENTITY_PROFILES_V01 = tuple(
    (cls.__name__, *profile) for cls, profile in _IDENTITY_PROFILES.items()
)

G2C_FIELD_NAMES_V01 = tuple(
    (cls.__name__, tuple(field.name for field in fields(cls)))
    for cls in G2C_TYPES_V01
)

_PROJECT_REF_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{0,255}$")
_MACHINE_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
_G2C_REASON_PATTERN = re.compile(r"^g2c_[a-z0-9_]{1,124}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_UTC_TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}\+00:00$"
)
_REASON_POSITION = {
    reason: position for position, reason in enumerate(PUBLIC_G2C_REASON_CODES_V01)
}
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_TIME_ENVELOPE_DOMAIN = "HEDGEHOG_EXECUTION_MODE_TIME_ENVELOPE_REF_V01"
_TIME_ENVELOPE_PREFIX = "emtime_v01:"
_MODE_PROFILE_SET_DOMAIN = "HEDGEHOG_EXECUTION_MODE_LOCAL_MODE_PROFILE_SET_V01"
_MODE_PROFILE_SET_PREFIX = "emprofiles_v01:"
_ZERO_SHA256 = "0" * 64
BSEP_SOURCE_FAMILY_SHA256_FIELDS_V01 = (
    "business_request_packet_sha256",
    "source_route_context_sha256",
    "source_proposal_sha256",
    "source_structured_rationale_sha256",
    "source_packet_sha256",
)
G2A_SOURCE_INSPECTION_SHA256_FIELDS_V01 = (
    "inspection_profile_id",
    "registry_id",
    "packet_id",
    "evaluation_time",
    "evaluation_time_source",
    "evaluation_context_id",
    "historical_state",
    "present_eligibility_status",
    "present_executable",
    "retry_eligible",
    "reason_codes",
    "transition_history_sha256",
    "disposition_history_sha256",
    "historical_result_unchanged",
    "creates_authority",
    "creates_permission",
    "creates_packet",
    "creates_receipt",
    "adapter_calls",
    "real_world_effects_count",
)

_STRUCTURAL_FIELD_SHAPE_RULES_V01 = (
    (ExecutionModeG2ABindingV01, "evaluation_context_id", "source_identity", False),
    (ExecutionModeG2ABindingV01, "reservation_owner_packet_id", "source_identity", True),
    (ExecutionModeG2ABindingV01, "terminal_receipt_ref", "source_identity", True),
    (ExecutionModeG2BBindingV01, "report_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "semantic_address_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "retrieval_plan_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "memory_descent_result_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "root_shortcut_projection_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "reuse_certificate_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "source_root_kernel_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "source_root_decision_input_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "source_root_decision_id", "source_identity", True),
    (ExecutionModeG2BBindingV01, "report_sha256", "sha256", True),
    (
        ExecutionModeG2BBindingV01,
        "compatibility_projection_set_sha256",
        "sha256",
        True,
    ),
    (ExecutionModeG2BBindingV01, "source_root_decision_sha256", "sha256", True),
    (ExecutionModeG2BBindingV01, "use_time", "signed_int64", True),
    (ExecutionModeLocalModeProfileV01, "policy_snapshot_id", "project_ref", False),
    (
        ExecutionModeLocalModeProfileV01,
        "capability_snapshot_id",
        "project_ref",
        False,
    ),
    (ExecutionModeLocalModeProfileV01, "cost_model_id", "project_ref", False),
    (ExecutionModeLocalRoutingSnapshotV01, "scope_ref", "source_identity", False),
    (ExecutionModeFeasibilityRowV01, "source_input_id", "source_identity", False),
    (
        ExecutionModeFeasibilityRowV01,
        "required_capability_id",
        "source_identity",
        True,
    ),
    (ExecutionModeProposalV01, "source_bsep_binding_id", "source_identity", False),
    (ExecutionModeProposalV01, "source_bsep_packet_id", "source_identity", False),
    (
        ExecutionModeProposalV01,
        "source_local_routing_snapshot_id",
        "source_identity",
        False,
    ),
    (ExecutionModeProposalV01, "source_replay_binding_id", "source_identity", False),
    (ExecutionModeProposalV01, "source_g2a_binding_id", "source_identity", False),
    (ExecutionModeProposalV01, "source_g2b_binding_id", "source_identity", False),
    (RootExecutionModeReviewInputV01, "proposal_id", "source_identity", False),
    (RootExecutionModeReviewInputV01, "router_input_id", "source_identity", False),
    (
        RootExecutionModeReviewInputV01,
        "proposal_artifact_id",
        "source_identity",
        False,
    ),
    (
        RootExecutionModeReviewInputV01,
        "proposal_transition_decision_id",
        "source_identity",
        False,
    ),
    (RootExecutionModeReviewInputV01, "proposed_scope_ref", "source_identity", True),
    (RootExecutionModeReviewInputV01, "accepted_scope_ref", "source_identity", True),
    (
        RootExecutionModeReviewInputV01,
        "scope_narrowing_proof_id",
        "source_identity",
        True,
    ),
    (
        RootExecutionModeReviewInputV01,
        "root_local_context_id",
        "source_identity",
        False,
    ),
    (RootExecutionModeReviewInputV01, "policy_snapshot_id", "project_ref", False),
    (RootExecutionModeReviewInputV01, "time_envelope_ref", "time_envelope_ref", False),
    (RootExecutionModeDecisionV01, "root_review_input_id", "source_identity", False),
    (RootExecutionModeDecisionV01, "proposal_id", "source_identity", False),
    (RootExecutionModeDecisionV01, "router_input_id", "source_identity", False),
    (RootExecutionModeDecisionV01, "accepted_scope_ref", "source_identity", True),
    (
        RootExecutionModeDecisionV01,
        "scope_narrowing_proof_id",
        "source_identity",
        True,
    ),
    (
        ExecutionModeValidationReportV01,
        "validated_artifact_id",
        "source_identity",
        True,
    ),
)


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _ordered_public_reasons(values: object) -> tuple[str, ...]:
    if type(values) is not tuple:
        raise ValueError("g2c_sequence_invalid")
    if any(
        type(value) is not str
        or value not in _REASON_POSITION
        or _G2C_REASON_PATTERN.fullmatch(value) is None
        or len(value) > 128
        for value in values
    ):
        raise ValueError("g2c_scalar_invalid")
    if len(values) != len(set(values)):
        raise ValueError("g2c_sequence_invalid")
    if tuple(sorted(values, key=_REASON_POSITION.__getitem__)) != values:
        raise ValueError("g2c_sequence_invalid")
    return values


def _sort_public_reasons(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    known = {value for value in values if value in _REASON_POSITION}
    if not known:
        known = {"g2c_scalar_invalid"}
    return tuple(sorted(known, key=_REASON_POSITION.__getitem__))


def _is_order_preserving_subset(
    subset: tuple[str, ...],
    sequence: tuple[str, ...],
) -> bool:
    positions = iter(sequence)
    return all(any(candidate == item for candidate in positions) for item in subset)


def _text_valid(value: object, *, maximum: int = 512, allow_empty: bool = False) -> bool:
    if type(value) is not str or len(value) > maximum:
        return False
    if not value and not allow_empty:
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    if unicodedata.normalize("NFC", value) != value:
        return False
    return not any(ord(char) <= 31 or 127 <= ord(char) <= 159 for char in value)


def _project_ref_valid(value: object) -> bool:
    return (
        _text_valid(value, maximum=256)
        and _PROJECT_REF_PATTERN.fullmatch(value) is not None
    )


def _source_identity_valid(value: object) -> bool:
    return _project_ref_valid(value) or (
        type(value) is str and _SHA256_PATTERN.fullmatch(value) is not None
    )


def _sha256_valid(value: object) -> bool:
    return type(value) is str and _SHA256_PATTERN.fullmatch(value) is not None


def _time_envelope_ref_valid(value: object) -> bool:
    return (
        type(value) is str
        and re.fullmatch(r"emtime_v01:[0-9a-f]{64}", value) is not None
    )


def _plain_sha256(material: object) -> str:
    return hashlib.sha256(canonical_json_bytes_v01(material)).hexdigest()


def _bsep_source_family_sha256(
    *,
    business_request_packet_sha256: str,
    source_route_context_sha256: str,
    source_proposal_sha256: str,
    source_structured_rationale_sha256: str,
    source_packet_sha256: str,
) -> str:
    values = (
        business_request_packet_sha256,
        source_route_context_sha256,
        source_proposal_sha256,
        source_structured_rationale_sha256,
        source_packet_sha256,
    )
    if any(not _sha256_valid(value) for value in values):
        raise ValueError("g2c_source_digest_mismatch")
    material = dict(zip(BSEP_SOURCE_FAMILY_SHA256_FIELDS_V01, values, strict=True))
    return _plain_sha256(material)


def _exact_int_valid(
    value: object,
    *,
    minimum: int = INT64_MIN,
    maximum: int = INT64_MAX,
) -> bool:
    return type(value) is int and minimum <= value <= maximum


def _exact_bool_valid(value: object) -> bool:
    return type(value) is bool


def _structural_field_shape_errors(value: object) -> tuple[str, ...]:
    validators = {
        "project_ref": (_project_ref_valid, "g2c_identity_invalid"),
        "source_identity": (_source_identity_valid, "g2c_identity_invalid"),
        "sha256": (_sha256_valid, "g2c_source_digest_mismatch"),
        "signed_int64": (_exact_int_valid, "g2c_g2b_use_time_invalid"),
        "time_envelope_ref": (
            _time_envelope_ref_valid,
            "g2c_time_envelope_ref_identity_mismatch",
        ),
    }
    errors: list[str] = []
    for expected_type, field_name, shape, optional in _STRUCTURAL_FIELD_SHAPE_RULES_V01:
        if type(value) is not expected_type:
            continue
        field_value = getattr(value, field_name)
        if optional and field_value is None:
            continue
        validator, reason = validators[shape]
        if not validator(field_value):
            errors.append(reason)
    return _sort_public_reasons(errors) if errors else ()


def _tuple_valid(
    value: object,
    *,
    item_validator: object,
    minimum: int = 0,
    maximum: int = MAX_TUPLE_MEMBERS,
    unique: bool = False,
    lexical: bool = False,
) -> bool:
    if type(value) is not tuple or not minimum <= len(value) <= maximum:
        return False
    try:
        if not all(item_validator(item) for item in value):
            return False
        if unique and len(value) != len(set(value)):
            return False
        if lexical and tuple(sorted(value)) != value:
            return False
        return True
    except Exception:
        return False


def _annotation_valid(value: object, annotation: object) -> bool:
    origin = get_origin(annotation)
    if origin is types.UnionType:
        return any(_annotation_valid(value, member) for member in get_args(annotation))
    if origin is tuple:
        if type(value) is not tuple or len(value) > MAX_TUPLE_MEMBERS:
            return False
        members = get_args(annotation)
        if len(members) == 2 and members[1] is Ellipsis:
            return all(_annotation_valid(item, members[0]) for item in value)
        return len(value) == len(members) and all(
            _annotation_valid(item, member)
            for item, member in zip(value, members, strict=True)
        )
    if origin is dict:
        key_type, value_type = get_args(annotation)
        return type(value) is dict and all(
            _annotation_valid(key, key_type) and _annotation_valid(item, value_type)
            for key, item in value.items()
        )
    if annotation is object:
        return True
    if annotation is None or annotation is type(None):
        return value is None
    if annotation in {str, int, bool, bytes}:
        return type(value) is annotation
    if isinstance(annotation, type):
        return type(value) is annotation
    return False


def _annotation_errors(value: object, expected_type: type[object]) -> tuple[str, ...]:
    if type(value) is not expected_type:
        return ("g2c_exact_type_invalid",)
    hints = get_type_hints(expected_type)
    errors: list[str] = []
    for field in fields(expected_type):
        field_value = getattr(value, field.name)
        if _annotation_valid(field_value, hints[field.name]):
            continue
        if get_origin(hints[field.name]) is tuple:
            errors.append("g2c_sequence_invalid")
        elif isinstance(hints[field.name], type) and hints[field.name] in G2C_TYPES_V01:
            errors.append("g2c_exact_type_invalid")
        else:
            errors.append("g2c_scalar_invalid")
    return _sort_public_reasons(errors) if errors else ()


def _plain_value(value: object) -> object:
    if value is None or type(value) in {str, int, bool}:
        return value
    if type(value) is tuple:
        return [_plain_value(item) for item in value]
    if type(value) in SERIALIZED_G2C_TYPES_V01:
        return _plain_data_unchecked(value)
    raise ValueError("g2c_scalar_invalid")


def _plain_data_unchecked(value: object, *, omit_identity: bool = False) -> dict[str, object]:
    value_type = type(value)
    if value_type not in SERIALIZED_G2C_TYPES_V01:
        raise ValueError("g2c_exact_type_invalid")
    identity_field = _IDENTITY_PROFILES[value_type][0]
    output: dict[str, object] = {}
    for field in fields(value_type):
        if omit_identity and field.name == identity_field:
            continue
        output[field.name] = _plain_value(getattr(value, field.name))
    canonical_json_bytes_v01(output)
    return output


def _rebuild_identity(value: object) -> str:
    value_type = type(value)
    if value_type not in SERIALIZED_G2C_TYPES_V01:
        raise ValueError("g2c_exact_type_invalid")
    if _annotation_errors(value, value_type) or _all_text_errors(value):
        raise ValueError("g2c_scalar_invalid")
    if (
        value_type is not ExecutionModeValidationReportV01
        and _identity_binding_errors(value)
    ):
        raise ValueError("g2c_identity_invalid")
    _identity_field, domain, prefix = _IDENTITY_PROFILES[value_type]
    material = _plain_data_unchecked(value, omit_identity=True)
    return prefix + domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(material),
    )


def _identity_valid(value: object, expected_type: type[object]) -> bool:
    identity_field, _domain, prefix = _IDENTITY_PROFILES[expected_type]
    identity = getattr(value, identity_field, None)
    return (
        type(identity) is str
        and re.fullmatch(re.escape(prefix) + r"[0-9a-f]{64}", identity) is not None
    )


def _identity_binding_errors(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name, reason in (
        ("request_id", "g2c_request_binding_mismatch"),
        ("transaction_id", "g2c_transaction_binding_mismatch"),
        ("owning_root_id", "g2c_root_binding_mismatch"),
        ("domain_id", "g2c_domain_binding_mismatch"),
    ):
        if hasattr(value, field_name) and not _project_ref_valid(
            getattr(value, field_name)
        ):
            errors.append(reason)
    if (
        hasattr(value, "request_id")
        and hasattr(value, "transaction_id")
        and type(getattr(value, "request_id")) is str
        and getattr(value, "request_id") == getattr(value, "transaction_id")
    ):
        errors.append("g2c_transaction_binding_mismatch")
    return _sort_public_reasons(errors) if errors else ()


def _all_text_errors(value: object) -> tuple[str, ...]:
    try:
        for field in fields(type(value)):
            item = getattr(value, field.name)
            if type(item) is str and not _text_valid(item):
                return ("g2c_scalar_invalid",)
            if type(item) is tuple and any(
                type(member) is str and not _text_valid(member) for member in item
            ):
                return ("g2c_scalar_invalid",)
        return ()
    except Exception:
        return ("g2c_scalar_invalid",)


def _common_serialized_errors(
    value: object,
    expected_type: type[object],
    *,
    check_identity: bool = True,
) -> tuple[str, ...]:
    annotation_errors = _annotation_errors(value, expected_type)
    if annotation_errors:
        return annotation_errors
    errors = list(_all_text_errors(value))
    errors.extend(_structural_field_shape_errors(value))
    if expected_type is not ExecutionModeValidationReportV01:
        errors.extend(_identity_binding_errors(value))
    if check_identity:
        if not _identity_valid(value, expected_type):
            errors.append("g2c_identity_invalid")
        else:
            try:
                if getattr(value, _IDENTITY_PROFILES[expected_type][0]) != _rebuild_identity(value):
                    errors.append("g2c_identity_mismatch")
            except Exception:
                errors.append("g2c_identity_invalid")
    return _sort_public_reasons(errors) if errors else ()


def _fixed_zero_effect_errors(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name in (
        "authority_created",
        "permission_created",
        "action_commit_packet_created",
        "packet_created",
        "receipt_created",
        "capability_created",
        "topology_created",
        "final_output_created",
        "drs_write_created",
    ):
        if hasattr(value, field_name) and getattr(value, field_name) is not False:
            errors.append("g2c_scalar_invalid")
    if hasattr(value, "real_world_effects_count") and getattr(
        value, "real_world_effects_count"
    ) != 0:
        errors.append("g2c_scalar_invalid")
    return _sort_public_reasons(errors) if errors else ()


def _valid_source_reason_tuple(value: object) -> bool:
    return _tuple_valid(
        value,
        item_validator=lambda item: _text_valid(item, maximum=512),
        unique=True,
    )


def _valid_ref_tuple(value: object, *, lexical: bool = False) -> bool:
    return _tuple_valid(
        value,
        item_validator=_source_identity_valid,
        unique=True,
        lexical=lexical,
    )


def _parse_utc_timestamp(value: object) -> datetime | None:
    if type(value) is not str or _UTC_TIMESTAMP_PATTERN.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo == timezone.utc else None


def _epoch_to_utc(value: object) -> str:
    if not _exact_int_valid(
        value, minimum=MIN_EPOCH_SECONDS, maximum=MAX_EPOCH_SECONDS
    ):
        raise ValueError("g2c_time_envelope_invalid")
    try:
        return (_EPOCH + timedelta(seconds=value)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except Exception:
        raise ValueError("g2c_time_envelope_invalid") from None


def _time_envelope_plain(snapshot: ExecutionModeLocalRoutingSnapshotV01) -> dict[str, object]:
    return {
        "ct_session_anchor": snapshot.ct_session_anchor,
        "et_observed_at": snapshot.et_observed_at_utc,
        "freshness_class": snapshot.freshness_class,
        "kt_asof": snapshot.kt_asof_utc,
        "pt_created_at": snapshot.pt_created_at_utc,
        "ttl_seconds": snapshot.ttl_seconds,
        "valid_from": snapshot.valid_from_utc,
        "valid_to": snapshot.valid_to_utc,
    }


def _rebuild_time_envelope_ref(snapshot: ExecutionModeLocalRoutingSnapshotV01) -> str:
    return _TIME_ENVELOPE_PREFIX + domain_separated_sha256_hex_v01(
        domain=_TIME_ENVELOPE_DOMAIN,
        payload=canonical_json_bytes_v01(_time_envelope_plain(snapshot)),
    )


def _mode_profile_set_sha256(
    profiles: tuple[ExecutionModeLocalModeProfileV01, ...],
) -> str:
    material = [execution_mode_local_mode_profile_to_plain_data_v01(item) for item in profiles]
    return _plain_sha256(material)


def _rebuild_mode_profile_set_id(snapshot: ExecutionModeLocalRoutingSnapshotV01) -> str:
    material = {
        "request_id": snapshot.request_id,
        "transaction_id": snapshot.transaction_id,
        "owning_root_id": snapshot.owning_root_id,
        "domain_id": snapshot.domain_id,
        "policy_snapshot_id": snapshot.policy_snapshot_id,
        "capability_snapshot_id": snapshot.capability_snapshot_id,
        "cost_model_id": snapshot.cost_model_id,
        "mode_profile_set_sha256": snapshot.mode_profile_set_sha256,
        "local_mode_profile_ids": [
            item.local_mode_profile_id for item in snapshot.mode_profiles
        ],
    }
    return _MODE_PROFILE_SET_PREFIX + domain_separated_sha256_hex_v01(
        domain=_MODE_PROFILE_SET_DOMAIN,
        payload=canonical_json_bytes_v01(material),
    )


def _ids_valid(value: object, names: tuple[str, ...], *, optional: bool = False) -> bool:
    for name in names:
        item = getattr(value, name)
        if optional and item is None:
            continue
        if not _source_identity_valid(item):
            return False
    return True


def _hashes_valid(value: object, names: tuple[str, ...], *, optional: bool = False) -> bool:
    for name in names:
        item = getattr(value, name)
        if optional and item is None:
            continue
        if not _sha256_valid(item):
            return False
    return True


def _bsep_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeBSEPBindingV01))
    if type(value) is not ExecutionModeBSEPBindingV01:
        return tuple(errors)
    if value.binding_state != "BOUNDED_SEMANTIC_EVIDENCE_BOUND":
        errors.append("g2c_bsep_invalid")
    if not _ids_valid(
        value,
        (
            "business_request_packet_id",
            "source_packet_id",
            "source_route_context_packet_id",
            "source_route_id",
            "source_proposal_id",
            "source_structured_rationale_ref",
        ),
    ):
        errors.append("g2c_bsep_invalid")
    constituent_hashes_valid = _hashes_valid(
        value,
        (
            "business_request_packet_sha256",
            "source_packet_sha256",
            "source_route_context_sha256",
            "source_proposal_sha256",
            "source_structured_rationale_sha256",
        ),
    )
    if not constituent_hashes_valid or not _sha256_valid(value.source_family_sha256):
        errors.append("g2c_source_digest_mismatch")
    elif value.source_family_sha256 != _bsep_source_family_sha256(
        business_request_packet_sha256=value.business_request_packet_sha256,
        source_route_context_sha256=value.source_route_context_sha256,
        source_proposal_sha256=value.source_proposal_sha256,
        source_structured_rationale_sha256=value.source_structured_rationale_sha256,
        source_packet_sha256=value.source_packet_sha256,
    ):
        errors.append("g2c_source_digest_mismatch")
    if (
        value.source_packet_type != "BoundedSemanticEvidencePacket"
        or value.source_schema_version != "bounded_semantic_evidence_packet_v0.1"
        or value.source_domain != value.domain_id
        or value.source_role != "orchestrator"
        or value.target_role != "architect"
        or value.source_reason_codes != ()
        or value.root_final_authority_preserved is not True
    ):
        errors.append("g2c_bsep_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _replay_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeReplayBindingV01))
    if type(value) is not ExecutionModeReplayBindingV01:
        return tuple(errors)
    if value.binding_state not in {"NOT_APPLICABLE", "SEALED_REPLAY_BOUND"}:
        errors.append("g2c_replay_binding_invalid")
    nullable_names = (
        "replay_id",
        "source_replay_sha256",
        "source_manifest_id",
        "reconstructed_manifest_id",
        "anchor_publication_id",
        "anchored_verification_id",
        "source_domain_projection_id",
        "reconstructed_domain_projection_id",
        "package_id",
        "logical_package_ref",
        "source_package_content_hash",
        "reconstructed_package_content_hash",
    )
    if value.binding_state == "NOT_APPLICABLE":
        if (
            value.replay_status != "NOT_APPLICABLE"
            or any(getattr(value, name) is not None for name in nullable_names)
            or value.integrity_verified is not False
            or value.continuity_verified is not False
            or value.anchor_verified is not False
            or value.evidence_refs != ()
        ):
            errors.append("g2c_replay_binding_invalid")
    elif value.binding_state == "SEALED_REPLAY_BOUND":
        if (
            value.replay_status != "PASS"
            or any(getattr(value, name) is None for name in nullable_names)
            or not _hashes_valid(
                value,
                (
                    "source_replay_sha256",
                    "source_package_content_hash",
                    "reconstructed_package_content_hash",
                ),
            )
            or not _ids_valid(
                value,
                tuple(name for name in nullable_names if "sha256" not in name and "hash" not in name),
            )
            or value.integrity_verified is not True
            or value.continuity_verified is not True
            or value.anchor_verified is not True
            or not _valid_ref_tuple(value.evidence_refs)
        ):
            errors.append("g2c_replay_binding_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _g2a_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeG2ABindingV01))
    if type(value) is not ExecutionModeG2ABindingV01:
        return tuple(errors)
    if value.binding_state not in {"NO_PACKET", "PRESENT_INSPECTION_BOUND"}:
        errors.append("g2c_g2a_relation_invalid")
    if not _exact_int_valid(value.evaluation_time):
        errors.append("g2c_scalar_invalid")
    if not _exact_int_valid(value.transition_event_count, minimum=0) or not _exact_int_valid(
        value.execution_attempt_count, minimum=0
    ):
        errors.append("g2c_scalar_invalid")
    if not _valid_source_reason_tuple(value.source_reason_codes):
        errors.append("g2c_sequence_invalid")
    if value.binding_state == "NO_PACKET":
        expected = (
            value.source_inspection_sha256 is None,
            value.inspection_profile_id is None,
            value.registry_id is None,
            value.packet_id is None,
            value.historical_lifecycle_state == "NO_PACKET",
            value.failed_provenance is None,
            value.transition_event_count == 0,
            value.execution_attempt_count == 0,
            value.idempotency_disposition == "NOT_APPLICABLE",
            value.reservation_owner_packet_id is None,
            value.terminal_receipt_ref is None,
            value.lifecycle_terminal is False,
            value.eligible_for_corridor_revalidation is False,
            value.present_eligibility_status == "NOT_APPLICABLE",
            value.present_executable is False,
            value.retry_eligible is False,
            value.source_reason_codes == (),
            value.transition_history_sha256 is None,
            value.disposition_history_sha256 is None,
            value.historical_result_unchanged is True,
            value.adapter_calls == 0,
        )
        if not all(expected):
            errors.append("g2c_g2a_relation_invalid")
    elif value.binding_state == "PRESENT_INSPECTION_BOUND":
        if (
            not _hashes_valid(
                value,
                (
                    "source_inspection_sha256",
                    "transition_history_sha256",
                    "disposition_history_sha256",
                ),
            )
            or not _ids_valid(value, ("inspection_profile_id", "registry_id", "packet_id"))
            or value.historical_lifecycle_state == "NO_PACKET"
            or value.idempotency_disposition == "NOT_APPLICABLE"
            or value.present_eligibility_status == "NOT_APPLICABLE"
            or value.historical_result_unchanged is not True
            or value.adapter_calls != 0
        ):
            errors.append("g2c_g2a_present_inspection_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _g2b_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeG2BBindingV01))
    if type(value) is not ExecutionModeG2BBindingV01:
        return tuple(errors)
    if value.binding_state not in {
        "NOT_APPLICABLE",
        "RESOLUTION_CONTEXT_BOUND",
        "DIRECT_REUSE_BOUND",
    }:
        errors.append("g2c_g2b_binding_invalid")
    if value.freshness_state not in {"NOT_APPLICABLE", "CURRENT", "STALE"}:
        errors.append("g2c_g2b_binding_invalid")
    if value.lineage_state not in {"NOT_APPLICABLE", "VALIDATED"}:
        errors.append("g2c_g2b_binding_invalid")
    for tuple_name in (
        "query_evaluation_ids",
        "eligible_candidate_ids",
        "ranked_candidate_ids",
        "compatibility_projection_ids",
    ):
        if not _valid_ref_tuple(getattr(value, tuple_name)):
            errors.append("g2c_sequence_invalid")
    nullable_names = (
        "report_id",
        "report_sha256",
        "semantic_address_id",
        "query_id",
        "selected_candidate_id",
        "retrieval_plan_id",
        "memory_descent_result_id",
        "root_shortcut_projection_id",
        "reuse_certificate_id",
        "compatibility_projection_set_sha256",
        "use_time",
        "source_root_kernel_id",
        "source_root_decision_input_id",
        "source_root_decision_id",
        "source_root_decision_sha256",
    )
    root_names = (
        "source_root_kernel_id",
        "source_root_decision_input_id",
        "source_root_decision_id",
        "source_root_decision_sha256",
    )
    if value.binding_state == "NOT_APPLICABLE":
        if (
            any(getattr(value, name) is not None for name in nullable_names)
            or any(
                getattr(value, name) != ()
                for name in (
                    "query_evaluation_ids",
                    "eligible_candidate_ids",
                    "ranked_candidate_ids",
                    "compatibility_projection_ids",
                )
            )
            or value.freshness_state != "NOT_APPLICABLE"
            or value.lineage_state != "NOT_APPLICABLE"
            or value.quarantine_present is not False
            or value.deadend_present is not False
            or value.context_available is not False
            or value.direct_informational_reuse_eligible is not False
            or value.source_reason_codes != ()
        ):
            errors.append("g2c_g2b_binding_invalid")
    elif value.binding_state == "RESOLUTION_CONTEXT_BOUND":
        required = (
            "report_id",
            "report_sha256",
            "semantic_address_id",
            "query_id",
            "retrieval_plan_id",
            "compatibility_projection_set_sha256",
            "use_time",
        )
        if (
            any(getattr(value, name) is None for name in required)
            or any(getattr(value, name) is not None for name in root_names)
            or value.root_shortcut_projection_id is not None
            or value.reuse_certificate_id is not None
            or value.eligible_candidate_ids != ()
            or value.ranked_candidate_ids != ()
            or value.selected_candidate_id is not None
            or not value.query_evaluation_ids
            or not value.compatibility_projection_ids
            or value.query_id != value.transaction_id
            or value.freshness_state != "STALE"
            or value.lineage_state != "VALIDATED"
            or value.context_available is not True
            or value.direct_informational_reuse_eligible is not False
            or value.source_reason_codes != ()
        ):
            errors.append("g2c_g2b_binding_invalid")
    elif value.binding_state == "DIRECT_REUSE_BOUND":
        required = tuple(name for name in nullable_names if name != "memory_descent_result_id")
        if (
            any(getattr(value, name) is None for name in required)
            or not value.query_evaluation_ids
            or not value.eligible_candidate_ids
            or not value.ranked_candidate_ids
            or not value.compatibility_projection_ids
            or value.selected_candidate_id not in value.eligible_candidate_ids
            or value.selected_candidate_id not in value.ranked_candidate_ids
            or value.query_id != value.transaction_id
            or value.freshness_state != "CURRENT"
            or value.lineage_state != "VALIDATED"
            or value.quarantine_present is not False
            or value.deadend_present is not False
            or value.context_available is not True
            or value.direct_informational_reuse_eligible is not True
            or value.source_reason_codes != ()
        ):
            errors.append("g2c_g2b_shortcut_invalid")
    if value.persistent_records_unchanged is not True:
        errors.append("g2c_g2b_binding_invalid")
    if not _valid_source_reason_tuple(value.source_reason_codes):
        errors.append("g2c_sequence_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _derived_local_reasons(value: ExecutionModeLocalModeProfileV01) -> tuple[str, ...]:
    reasons: list[str] = []
    if value.policy_allowed is False:
        reasons.append("g2c_policy_forbidden")
    if value.scope_allowed is False:
        reasons.append("g2c_scope_forbidden")
    if value.risk_allowed is False:
        reasons.append("g2c_risk_forbidden")
    if value.privacy_allowed is False:
        reasons.append("g2c_privacy_forbidden")
    if value.capability_state == "UNAVAILABLE":
        reasons.append("g2c_capability_unavailable")
    return tuple(reasons)


def _local_profile_errors(value: object) -> tuple[str, ...]:
    if type(value) is not ExecutionModeLocalModeProfileV01:
        return ("g2c_exact_type_invalid",)
    errors: list[str] = []
    if not _exact_int_valid(value.cost_units, minimum=0):
        errors.append("g2c_cost_invalid")
    errors.extend(_common_serialized_errors(value, ExecutionModeLocalModeProfileV01))
    if value.mode not in EXECUTABLE_EXECUTION_MODES_V01:
        errors.append("g2c_noncanonical_mode")
    if value.capability_state not in {"NOT_REQUIRED", "AVAILABLE", "UNAVAILABLE"}:
        errors.append("g2c_local_mode_profile_invalid")
    no_compute_modes = {"sealed_replay", "direct_informational_reuse"}
    if value.mode in no_compute_modes:
        if value.capability_state != "NOT_REQUIRED" or value.capability_id is not None:
            errors.append("g2c_local_mode_profile_invalid")
    elif (
        value.capability_state == "NOT_REQUIRED"
        or not _source_identity_valid(value.capability_id)
    ):
        errors.append("g2c_local_mode_profile_invalid")
    if value.cost_unit != "normalized_cost_units_v01":
        errors.append("g2c_cost_invalid")
    if value.local_reason_codes != _derived_local_reasons(value):
        errors.append("g2c_local_mode_profile_invalid")
    try:
        _ordered_public_reasons(value.local_reason_codes)
    except ValueError:
        errors.append("g2c_sequence_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _snapshot_errors(value: object) -> tuple[str, ...]:
    errors = list(
        _common_serialized_errors(value, ExecutionModeLocalRoutingSnapshotV01)
    )
    if type(value) is not ExecutionModeLocalRoutingSnapshotV01:
        return tuple(errors)
    if value.created_by != "OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01":
        errors.append("g2c_local_mode_profile_set_invalid")
    if _MACHINE_CODE_PATTERN.fullmatch(value.request_class) is None or _MACHINE_CODE_PATTERN.fullmatch(
        value.scope_class
    ) is None:
        errors.append("g2c_scalar_invalid")
    if value.action_class not in {"ACTION", "NON_ACTION"}:
        errors.append("g2c_scalar_invalid")
    if value.action_packet_relation not in {
        "NOT_APPLICABLE",
        "NEW_ACTION_NO_PACKET",
        "EXISTING_PACKET_ATTEMPT",
    }:
        errors.append("g2c_scalar_invalid")
    if (
        (value.action_class == "NON_ACTION" and value.action_packet_relation != "NOT_APPLICABLE")
        or (
            value.action_class == "ACTION"
            and value.action_packet_relation == "NOT_APPLICABLE"
        )
    ):
        errors.append("g2c_scalar_invalid")
    if value.risk_class not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        errors.append("g2c_scalar_invalid")
    if value.required_user_input_state not in {"COMPLETE", "MISSING_RESOLVABLE"}:
        errors.append("g2c_scalar_invalid")
    if value.hard_block_state not in {"CLEAR", "BLOCKED"}:
        errors.append("g2c_scalar_invalid")
    if not _valid_ref_tuple(value.permitted_narrower_scope_refs, lexical=True):
        errors.append("g2c_sequence_invalid")
    if (
        type(value.mode_profiles) is not tuple
        or len(value.mode_profiles) != LOCAL_MODE_PROFILE_COUNT
        or tuple(type(item) for item in value.mode_profiles)
        != (ExecutionModeLocalModeProfileV01,) * LOCAL_MODE_PROFILE_COUNT
        or tuple(item.mode for item in value.mode_profiles) != EXECUTABLE_EXECUTION_MODES_V01
    ):
        errors.append("g2c_local_mode_profile_set_invalid")
    else:
        for profile in value.mode_profiles:
            if _local_profile_errors(profile):
                errors.append("g2c_local_mode_profile_set_invalid")
            if profile.request_id != value.request_id:
                errors.append("g2c_request_binding_mismatch")
            if profile.transaction_id != value.transaction_id:
                errors.append("g2c_transaction_binding_mismatch")
            if profile.owning_root_id != value.owning_root_id:
                errors.append("g2c_root_binding_mismatch")
            if profile.domain_id != value.domain_id:
                errors.append("g2c_domain_binding_mismatch")
            if (
                profile.policy_snapshot_id != value.policy_snapshot_id
                or profile.capability_snapshot_id != value.capability_snapshot_id
                or profile.cost_model_id != value.cost_model_id
            ):
                errors.append("g2c_local_mode_profile_set_invalid")
        try:
            expected_sha = _mode_profile_set_sha256(value.mode_profiles)
            if value.mode_profile_set_sha256 != expected_sha:
                errors.append("g2c_mode_profile_set_identity_mismatch")
            if value.mode_profile_set_id != _rebuild_mode_profile_set_id(value):
                errors.append("g2c_mode_profile_set_identity_mismatch")
        except Exception:
            errors.append("g2c_local_mode_profile_set_invalid")
    parsed = tuple(
        _parse_utc_timestamp(item)
        for item in (
            value.pt_created_at_utc,
            value.kt_asof_utc,
            value.et_observed_at_utc,
            value.valid_from_utc,
            value.valid_to_utc,
        )
    )
    if (
        any(item is None for item in parsed)
        or not _exact_int_valid(
            value.evaluation_time_epoch_seconds,
            minimum=MIN_EPOCH_SECONDS,
            maximum=MAX_EPOCH_SECONDS,
        )
        or not _exact_int_valid(value.ttl_seconds, minimum=0)
        or value.freshness_class
        not in {"static", "slow_changing", "normal", "fast_changing", "real_time"}
    ):
        errors.append("g2c_time_envelope_invalid")
    else:
        pt, kt, et, valid_from, valid_to = parsed
        assert pt is not None and kt is not None and et is not None
        assert valid_from is not None and valid_to is not None
        if (
            value.kt_asof_utc != _epoch_to_utc(value.evaluation_time_epoch_seconds)
            or not (pt <= kt and et <= kt and valid_from <= kt < valid_to)
            or value.ttl_seconds != int((valid_to - valid_from).total_seconds())
        ):
            errors.append("g2c_time_envelope_invalid")
        try:
            if value.time_envelope_ref != _rebuild_time_envelope_ref(value):
                errors.append("g2c_time_envelope_ref_identity_mismatch")
        except Exception:
            errors.append("g2c_time_envelope_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _router_input_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeRouterInputV01))
    if type(value) is not ExecutionModeRouterInputV01:
        return tuple(errors)
    nested = (
        (value.bsep_binding, _bsep_errors),
        (value.local_routing_snapshot, _snapshot_errors),
        (value.replay_binding, _replay_errors),
        (value.g2a_binding, _g2a_errors),
        (value.g2b_binding, _g2b_errors),
    )
    if any(validator(item) for item, validator in nested):
        errors.append("g2c_source_context_invalid")
    domain = value.bsep_binding.domain_id
    for item in (
        value.bsep_binding,
        value.local_routing_snapshot,
        value.replay_binding,
        value.g2a_binding,
        value.g2b_binding,
    ):
        if item.request_id != value.request_id:
            errors.append("g2c_request_binding_mismatch")
        if item.transaction_id != value.transaction_id:
            errors.append("g2c_transaction_binding_mismatch")
        if item.owning_root_id != value.owning_root_id:
            errors.append("g2c_root_binding_mismatch")
        if item.domain_id != domain:
            errors.append("g2c_domain_binding_mismatch")
    expected_trace = tuple(
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
    if value.trace_refs != expected_trace or not _valid_ref_tuple(
        value.trace_refs, lexical=True
    ):
        errors.append("g2c_sequence_invalid")
    return _sort_public_reasons(errors) if errors else ()


def _feasibility_row_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeFeasibilityRowV01))
    if type(value) is not ExecutionModeFeasibilityRowV01:
        return tuple(errors)
    mode = value.mode
    if mode not in CANONICAL_EXECUTION_MODES_V01:
        errors.append("g2c_noncanonical_mode")
    if value.category not in {"EXECUTABLE", "TERMINAL"}:
        errors.append("g2c_feasibility_row_invalid")
    if value.feasibility_status not in {
        "FEASIBLE",
        "INFEASIBLE",
        "TERMINAL_SELECTED",
        "TERMINAL_NOT_SELECTED",
    }:
        errors.append("g2c_feasibility_row_invalid")
    for tuple_name in ("required_evidence_refs", "satisfied_evidence_refs"):
        if not _valid_ref_tuple(getattr(value, tuple_name)):
            errors.append("g2c_sequence_invalid")
    try:
        _ordered_public_reasons(value.missing_evidence_codes)
        _ordered_public_reasons(value.reason_codes)
    except ValueError:
        errors.append("g2c_sequence_invalid")
    if (
        any(
            reason not in _ALLOWED_MISSING_EVIDENCE_CODES_V01
            for reason in value.missing_evidence_codes
        )
        or not _is_order_preserving_subset(
            value.satisfied_evidence_refs,
            value.required_evidence_refs,
        )
    ):
        errors.append("g2c_feasibility_row_invalid")
    rank_by_mode = dict(EXECUTION_MODE_SAFE_DEPTH_RANKS_V01)
    if value.category == "EXECUTABLE":
        if (
            mode not in EXECUTABLE_EXECUTION_MODES_V01
            or value.safe_depth_rank != rank_by_mode.get(mode)
            or not _source_identity_valid(value.local_mode_profile_id)
            or not _exact_int_valid(value.cost_units, minimum=0)
            or value.feasibility_status not in {"FEASIBLE", "INFEASIBLE"}
            or value.downstream_compute_class
            != _MODE_DOWNSTREAM_COMPUTE_CLASSES_V01.get(mode)
            or len(value.required_evidence_refs) < 3
        ):
            errors.append("g2c_feasibility_row_invalid")
        if mode in _CAPABILITY_REQUIRED_MODES_V01:
            if (
                not _source_identity_valid(value.required_capability_id)
                or value.required_capability_id not in value.required_evidence_refs
            ):
                errors.append("g2c_feasibility_row_invalid")
        elif value.required_capability_id is not None:
            errors.append("g2c_feasibility_row_invalid")
        positive_reasons = set(_MODE_POSITIVE_REASONS_V01.values())
        if value.feasibility_status == "FEASIBLE":
            if (
                value.reason_codes != (_MODE_POSITIVE_REASONS_V01.get(mode),)
                or value.missing_evidence_codes != ()
                or value.satisfied_evidence_refs != value.required_evidence_refs
            ):
                errors.append("g2c_feasibility_row_invalid")
        elif (
            not value.reason_codes
            or any(reason in positive_reasons for reason in value.reason_codes)
            or any(
                reason not in _EXECUTABLE_NEGATIVE_REASONS_V01
                for reason in value.reason_codes
            )
        ):
            errors.append("g2c_feasibility_row_invalid")
    elif value.category == "TERMINAL":
        if (
            mode not in _TERMINAL_MODES_V01
            or value.safe_depth_rank is not None
            or value.local_mode_profile_id is not None
            or value.required_capability_id is not None
            or value.cost_units is not None
            or value.downstream_compute_class
            != _MODE_DOWNSTREAM_COMPUTE_CLASSES_V01.get(mode)
            or value.feasibility_status
            not in {"TERMINAL_SELECTED", "TERMINAL_NOT_SELECTED"}
            or len(value.required_evidence_refs) != 2
            or value.satisfied_evidence_refs != value.required_evidence_refs
            or value.missing_evidence_codes != ()
        ):
            errors.append("g2c_feasibility_row_invalid")
        if value.feasibility_status == "TERMINAL_NOT_SELECTED":
            if value.reason_codes != ():
                errors.append("g2c_feasibility_row_invalid")
        elif mode == "blocked":
            if value.reason_codes not in {
                ("g2c_hard_block_present",),
                ("g2c_no_safe_mode",),
            }:
                errors.append("g2c_feasibility_row_invalid")
        elif value.reason_codes != ("g2c_user_input_required",):
            errors.append("g2c_feasibility_row_invalid")
    if value.root_review_required is not True:
        errors.append("g2c_feasibility_row_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _proposal_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeProposalV01))
    if type(value) is not ExecutionModeProposalV01:
        return tuple(errors)
    mode = value.selected_mode
    if mode not in CANONICAL_EXECUTION_MODES_V01:
        errors.append("g2c_noncanonical_mode")
    if not _sha256_valid(value.source_bsep_sha256):
        errors.append("g2c_source_digest_mismatch")
    if (
        type(value.ordered_feasibility_rows) is not tuple
        or len(value.ordered_feasibility_rows) != CANONICAL_MODE_COUNT
        or tuple(type(item) for item in value.ordered_feasibility_rows)
        != (ExecutionModeFeasibilityRowV01,) * CANONICAL_MODE_COUNT
        or tuple(item.mode for item in value.ordered_feasibility_rows)
        != CANONICAL_EXECUTION_MODES_V01
        or any(_feasibility_row_errors(item) for item in value.ordered_feasibility_rows)
    ):
        errors.append("g2c_proposal_rows_invalid")
    else:
        selected = tuple(
            item
            for item in value.ordered_feasibility_rows
            if item.feasibility_row_id == value.selected_feasibility_row_id
        )
        if (
            len(selected) != 1
            or selected[0].mode != mode
            or selected[0].feasibility_status
            not in {"FEASIBLE", "TERMINAL_SELECTED"}
        ):
            errors.append("g2c_proposal_selected_row_mismatch")
        else:
            selected_row = selected[0]
            if (
                value.selected_safe_depth_rank != selected_row.safe_depth_rank
                or value.selected_local_mode_profile_id
                != selected_row.local_mode_profile_id
                or value.selected_expected_cost_units != selected_row.cost_units
            ):
                errors.append("g2c_proposal_selected_row_mismatch")
            feasible_rows = tuple(
                row
                for row in value.ordered_feasibility_rows
                if row.feasibility_status == "FEASIBLE"
            )
            selected_terminals = tuple(
                row
                for row in value.ordered_feasibility_rows
                if row.feasibility_status == "TERMINAL_SELECTED"
            )
            if selected_row.category == "TERMINAL":
                if len(selected_terminals) != 1 or feasible_rows:
                    errors.append("g2c_proposal_selected_row_mismatch")
            elif selected_terminals:
                errors.append("g2c_proposal_selected_row_mismatch")
            elif feasible_rows:
                expected_selected = min(
                    feasible_rows,
                    key=lambda row: (
                        row.safe_depth_rank,
                        row.cost_units,
                        _CANONICAL_MODE_INDEX_V01[row.mode],
                    ),
                )
                if selected_row != expected_selected:
                    errors.append("g2c_proposal_selected_row_mismatch")
        for row in value.ordered_feasibility_rows:
            if (
                row.source_input_id != value.source_input_id
                or row.request_id != value.request_id
                or row.transaction_id != value.transaction_id
                or row.owning_root_id != value.owning_root_id
                or row.domain_id != value.domain_id
            ):
                errors.append("g2c_proposal_rows_invalid")
                break
    try:
        _ordered_public_reasons(value.reason_codes)
    except ValueError:
        errors.append("g2c_sequence_invalid")
    if not _valid_ref_tuple(value.required_downstream_capability_ids):
        errors.append("g2c_sequence_invalid")
    if value.downstream_consumption_class != (
        _MODE_DOWNSTREAM_CONSUMPTION_CLASSES_V01.get(mode)
    ):
        errors.append("g2c_proposal_rows_invalid")
    expected_capabilities: tuple[str, ...] = ()
    if mode in _CAPABILITY_REQUIRED_MODES_V01:
        selected_capability = None
        if "selected_row" in locals():
            selected_capability = selected_row.required_capability_id
        if not _source_identity_valid(selected_capability):
            errors.append("g2c_proposal_selected_row_mismatch")
        else:
            expected_capabilities = (selected_capability,)
    if value.required_downstream_capability_ids != expected_capabilities:
        errors.append("g2c_proposal_selected_row_mismatch")
    tie_break_applied = False
    if "selected_row" in locals() and selected_row.category == "EXECUTABLE":
        feasible_rows = tuple(
            row
            for row in value.ordered_feasibility_rows
            if row.feasibility_status == "FEASIBLE"
        )
        if feasible_rows:
            minimum_rank = min(row.safe_depth_rank for row in feasible_rows)
            rank_rows = tuple(
                row for row in feasible_rows if row.safe_depth_rank == minimum_rank
            )
            minimum_cost = min(row.cost_units for row in rank_rows)
            tie_break_applied = sum(
                row.cost_units == minimum_cost for row in rank_rows
            ) >= 2
    expected_reasons = (
        (
            "g2c_selection_tie_break_applied",
            "g2c_proposal_sources_valid",
        )
        if tie_break_applied
        else ("g2c_proposal_sources_valid",)
    )
    if value.reason_codes != expected_reasons:
        errors.append("g2c_proposal_rows_invalid")
    terminal = mode in _TERMINAL_MODES_V01
    if terminal:
        if (
            value.selected_safe_depth_rank is not None
            or value.selected_local_mode_profile_id is not None
            or value.selected_expected_cost_units is not None
            or value.proposed_scope_ref is not None
            or value.downstream_consumption_class != "TERMINAL_NO_CONSUMPTION"
            or value.downstream_action_packet_required is not False
            or value.required_downstream_capability_ids != ()
        ):
            errors.append("g2c_terminal_review_mismatch")
    elif (
        not _exact_int_valid(value.selected_safe_depth_rank, minimum=0)
        or not _source_identity_valid(value.selected_local_mode_profile_id)
        or not _exact_int_valid(value.selected_expected_cost_units, minimum=0)
        or not _source_identity_valid(value.proposed_scope_ref)
    ):
        errors.append("g2c_proposal_selected_row_mismatch")
    if value.root_review_required is not True:
        errors.append("g2c_proposal_rows_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _root_review_errors(value: object) -> tuple[str, ...]:
    errors = list(
        _common_serialized_errors(value, RootExecutionModeReviewInputV01)
    )
    if type(value) is not RootExecutionModeReviewInputV01:
        return tuple(errors)
    if value.created_by != "OWNING_LOCAL_ROOT_EXECUTION_MODE_REVIEW_V01":
        errors.append("g2c_review_action_invalid")
    if value.review_action not in {"ACCEPT", "NARROW", "REJECT", "TERMINAL_FROM_PROPOSAL"}:
        errors.append("g2c_review_action_invalid")
    if value.proposed_mode not in CANONICAL_EXECUTION_MODES_V01:
        errors.append("g2c_noncanonical_mode")
    if not _exact_int_valid(
        value.evaluation_time_epoch_seconds,
        minimum=MIN_EPOCH_SECONDS,
        maximum=MAX_EPOCH_SECONDS,
    ):
        errors.append("g2c_time_envelope_invalid")
    if not _valid_ref_tuple(value.narrowing_basis_refs, lexical=True):
        errors.append("g2c_sequence_invalid")
    if not _valid_ref_tuple(value.trace_refs, lexical=True):
        errors.append("g2c_sequence_invalid")
    if value.review_action == "NARROW":
        if (
            value.proposed_scope_ref is None
            or value.accepted_scope_ref is None
            or value.accepted_scope_ref == value.proposed_scope_ref
            or value.scope_narrowing_proof_id is None
            or not value.narrowing_basis_refs
        ):
            errors.append("g2c_scope_narrowing_invalid")
    elif value.scope_narrowing_proof_id is not None or value.narrowing_basis_refs != ():
        errors.append("g2c_scope_narrowing_invalid")
    if value.review_action == "ACCEPT" and (
        value.proposed_mode in _TERMINAL_MODES_V01
        or value.proposed_scope_ref is None
        or value.accepted_scope_ref != value.proposed_scope_ref
    ):
        errors.append("g2c_review_action_invalid")
    if value.review_action == "REJECT" and (
        value.proposed_mode in _TERMINAL_MODES_V01
        or value.proposed_scope_ref is None
        or value.accepted_scope_ref is not None
    ):
        errors.append("g2c_review_action_invalid")
    if value.review_action == "NARROW" and value.proposed_mode in _TERMINAL_MODES_V01:
        errors.append("g2c_terminal_review_mismatch")
    if value.review_action == "TERMINAL_FROM_PROPOSAL" and (
        value.proposed_mode not in {"blocked", "needs_user"}
        or value.proposed_scope_ref is not None
        or value.accepted_scope_ref is not None
    ):
        errors.append("g2c_terminal_review_mismatch")
    if value.review_action != "TERMINAL_FROM_PROPOSAL" and value.proposed_mode in _TERMINAL_MODES_V01:
        errors.append("g2c_terminal_review_mismatch")
    if not all(
        _source_identity_valid(item)
        for item in (
            value.policy_snapshot_id,
            value.time_envelope_ref,
            value.root_local_context_id,
        )
    ):
        errors.append("g2c_scalar_invalid")
    return _sort_public_reasons(errors) if errors else ()


_ROOT_PROJECTION_REASON = {
    "ACCEPT": "g2c_root_accept_projected",
    "NARROW": "g2c_root_narrow_projected",
    "REJECT": "g2c_root_reject_projected",
    "BLOCKED": "g2c_root_blocked_projected",
    "NEEDS_USER": "g2c_root_needs_user_projected",
}


def _root_decision_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, RootExecutionModeDecisionV01))
    if type(value) is not RootExecutionModeDecisionV01:
        return tuple(errors)
    if value.outcome not in _ROOT_PROJECTION_REASON:
        errors.append("g2c_root_mapping_invalid")
    else:
        if value.reason_codes != (_ROOT_PROJECTION_REASON[value.outcome],):
            errors.append("g2c_root_mapping_invalid")
    if value.accepted_mode is not None and value.accepted_mode not in EXECUTABLE_EXECUTION_MODES_V01:
        errors.append("g2c_noncanonical_mode")
    try:
        _ordered_public_reasons(value.reason_codes)
    except ValueError:
        errors.append("g2c_sequence_invalid")
    if value.downstream_consumption_class not in {
        "SHORTCUT_RETURN_TO_ROOT",
        "RUNTIME_TOPOLOGY_ELIGIBLE",
        "TERMINAL_NO_CONSUMPTION",
    }:
        errors.append("g2c_root_mapping_invalid")
    accepted = value.outcome in {"ACCEPT", "NARROW"}
    if accepted:
        if (
            value.accepted_mode is None
            or value.accepted_scope_ref is None
            or value.route_eligibility_candidate is not True
            or value.downstream_consumption_class == "TERMINAL_NO_CONSUMPTION"
        ):
            errors.append("g2c_root_mapping_invalid")
    elif (
        value.accepted_mode is not None
        or value.accepted_scope_ref is not None
        or value.scope_narrowing_proof_id is not None
        or value.route_eligibility_candidate is not False
        or value.downstream_consumption_class != "TERMINAL_NO_CONSUMPTION"
        or value.downstream_action_packet_required is not False
    ):
        errors.append("g2c_terminal_review_mismatch")
    if value.outcome == "NARROW" and value.scope_narrowing_proof_id is None:
        errors.append("g2c_scope_narrowing_invalid")
    if value.outcome != "NARROW" and value.scope_narrowing_proof_id is not None:
        errors.append("g2c_scope_narrowing_invalid")
    source_decision = {
        "ACCEPT": "ACCEPT",
        "NARROW": "ACCEPT",
        "REJECT": "REJECT",
        "BLOCKED": "BLOCKED_FAIL_CLOSED",
        "NEEDS_USER": "NEEDS_USER",
    }.get(value.outcome)
    if source_decision is not None and value.source_root_decision != source_decision:
        errors.append("g2c_root_mapping_invalid")
    expected_source_reason = {
        "ACCEPT": "validated_candidate_accepted",
        "NARROW": "validated_candidate_accepted",
        "REJECT": "policy_rejected_candidate",
        "BLOCKED": "hard_policy_violation",
        "NEEDS_USER": "user_permission_missing",
    }.get(value.outcome)
    if expected_source_reason is not None and value.source_root_reason_code != expected_source_reason:
        errors.append("g2c_root_mapping_invalid")
    if value.source_root_transition_decision != "RETURN_TO_ROOT":
        errors.append("g2c_root_mapping_invalid")
    if not _source_identity_valid(value.source_root_decision_id) or not _source_identity_valid(
        value.source_root_decision_input_id
    ) or not _source_identity_valid(value.source_root_transition_decision_id):
        errors.append("g2c_root_result_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _validation_report_errors(value: object) -> tuple[str, ...]:
    errors = list(
        _common_serialized_errors(value, ExecutionModeValidationReportV01)
    )
    if type(value) is not ExecutionModeValidationReportV01:
        return tuple(errors)
    if value.validation_target not in VALIDATION_TARGETS_V01:
        errors.append("g2c_scalar_invalid")
    if value.validation_status not in {"PASS", "FAIL_CLOSED"}:
        errors.append("g2c_scalar_invalid")
    if value.failure_stage not in FAILURE_STAGES_V01:
        errors.append("g2c_scalar_invalid")
    identity_values = (
        value.request_id,
        value.transaction_id,
        value.owning_root_id,
        value.domain_id,
    )
    if not (all(item is None for item in identity_values) or all(item is not None for item in identity_values)):
        errors.append("g2c_identity_invalid")
    if all(item is not None for item in identity_values):
        if any(not _project_ref_valid(item) for item in identity_values):
            errors.append("g2c_identity_invalid")
        if value.request_id == value.transaction_id:
            errors.append("g2c_transaction_binding_mismatch")
    try:
        _ordered_public_reasons(value.reason_codes)
    except ValueError:
        errors.append("g2c_sequence_invalid")
    if not _valid_source_reason_tuple(value.source_reason_codes):
        errors.append("g2c_sequence_invalid")
    if value.validation_status == "PASS":
        if (
            value.failure_stage != "NONE"
            or value.return_to_root_required is not False
            or value.reason_codes != ()
            or value.source_reason_codes != ()
        ):
            errors.append("g2c_scalar_invalid")
        if value.validation_target == "SOURCE_CONTEXT_STRUCTURAL":
            if value.validated_artifact_id is not None or any(
                item is not None for item in identity_values
            ):
                errors.append("g2c_source_context_structural_target_invalid")
        elif value.validated_artifact_id is None or any(
            item is None for item in identity_values
        ):
            errors.append("g2c_identity_invalid")
    elif value.validation_status == "FAIL_CLOSED":
        if (
            value.failure_stage == "NONE"
            or value.return_to_root_required is not True
            or not value.reason_codes
        ):
            errors.append("g2c_fail_closed_return_to_root")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


_STRUCTURAL_ERROR_FUNCTIONS = {
    ExecutionModeBSEPBindingV01: _bsep_errors,
    ExecutionModeReplayBindingV01: _replay_errors,
    ExecutionModeG2ABindingV01: _g2a_errors,
    ExecutionModeG2BBindingV01: _g2b_errors,
    ExecutionModeLocalModeProfileV01: _local_profile_errors,
    ExecutionModeLocalRoutingSnapshotV01: _snapshot_errors,
    ExecutionModeRouterInputV01: _router_input_errors,
    ExecutionModeFeasibilityRowV01: _feasibility_row_errors,
    ExecutionModeProposalV01: _proposal_errors,
    RootExecutionModeReviewInputV01: _root_review_errors,
    RootExecutionModeDecisionV01: _root_decision_errors,
    ExecutionModeValidationReportV01: _validation_report_errors,
}


def _source_plain_value_valid(value: object, active: set[int]) -> bool:
    if value is None or type(value) in {bool, int, str}:
        return type(value) is not str or _text_valid(value, allow_empty=True)
    if type(value) is float:
        return math.isfinite(value)
    if type(value) not in {dict, list, tuple}:
        return False
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    try:
        if type(value) is dict:
            return all(
                type(key) is str
                and _text_valid(key)
                and _source_plain_value_valid(item, active)
                for key, item in value.items()
            )
        return all(_source_plain_value_valid(item, active) for item in value)
    finally:
        active.remove(identity)


def _source_context_errors(value: object) -> tuple[str, ...]:
    import hedgehog.action_commit_packet_v02 as _action_packet
    import hedgehog.drs_g2b_compatibility_v01 as _compatibility
    import hedgehog.drs_memory_resolution_v01 as _resolution
    import hedgehog.evidence.external_anchor_v01 as _external_anchor
    import hedgehog.evidence.sealed_evidence_profile_v01 as _evidence_profile
    import hedgehog.evidence.sealed_package_v01 as _sealed_package
    import hedgehog.evidence.sealed_replay_evidence_v01 as _sealed_replay

    if type(value) is not ExecutionModeSourceContextV01:
        return ("g2c_exact_type_invalid",)
    errors: list[str] = []
    for name in (
        "business_request_context_packet",
        "bsep_packet",
        "bsep_route_context_packet",
        "bsep_orchestrator_proposal",
        "bsep_structured_rationale",
    ):
        item = getattr(value, name)
        if type(item) is not dict or not _source_plain_value_valid(item, set()):
            errors.append("g2c_source_context_invalid")
    replay_optional = (
        value.sealed_replay_evidence,
        value.replay_source_manifest,
        value.replay_source_domain_projection,
        value.replay_anchor_publication,
        value.replay_anchored_verification,
        value.replay_supplied_anchor_publication_id,
        value.replay_reconstructed_manifest,
        value.replay_reconstructed_domain_projection,
    )
    replay_absent = all(item is None for item in replay_optional)
    replay_tuples_empty = (
        value.replay_source_safe_file_contents == ()
        and value.replay_reconstructed_safe_file_contents == ()
    )
    replay_present = (
        type(value.sealed_replay_evidence) is _sealed_replay.SealedReplayEvidenceV01
        and type(value.replay_source_manifest) is _sealed_package.SealedPackageManifestV01
        and type(value.replay_source_domain_projection)
        is _evidence_profile.DomainEvidenceProjectionV01
        and type(value.replay_anchor_publication)
        is _external_anchor.ExternalAnchorPublicationV01
        and type(value.replay_anchored_verification)
        is _external_anchor.AnchoredPackageVerificationV01
        and _source_identity_valid(value.replay_supplied_anchor_publication_id)
        and type(value.replay_reconstructed_manifest)
        is _sealed_package.SealedPackageManifestV01
        and type(value.replay_reconstructed_domain_projection)
        is _evidence_profile.DomainEvidenceProjectionV01
        and type(value.replay_source_safe_file_contents) is tuple
        and bool(value.replay_source_safe_file_contents)
        and all(type(item) is bytes for item in value.replay_source_safe_file_contents)
        and type(value.replay_reconstructed_safe_file_contents) is tuple
        and bool(value.replay_reconstructed_safe_file_contents)
        and all(
            type(item) is bytes
            for item in value.replay_reconstructed_safe_file_contents
        )
    )
    if not ((replay_absent and replay_tuples_empty) or replay_present):
        errors.append("g2c_source_context_invalid")
    g2a_source_values = (
        value.g2a_inspection,
        value.g2a_registry,
        value.g2a_packet_id,
        value.g2a_corridor,
        value.g2a_corridor_step,
        value.g2a_logical_time_bridge,
        value.g2a_transition_registry_profile,
    )
    g2a_no_packet = (
        all(item is None for item in g2a_source_values)
        and value.g2a_current_dependency_observations == ()
        and _exact_int_valid(value.g2a_evaluation_time)
        and _project_ref_valid(value.g2a_evaluation_time_source)
        and _project_ref_valid(value.g2a_evaluation_context_id)
    )
    g2a_present = (
        type(value.g2a_inspection)
        is _action_packet.ActionPacketPresentEligibilityInspectionV01
        and type(value.g2a_registry) is _action_packet.ActionCommitPacketRegistryV02
        and _source_identity_valid(value.g2a_packet_id)
        and type(value.g2a_corridor)
        is _action_packet.ContractFulfillmentCorridorV01
        and type(value.g2a_corridor_step) is _action_packet.CorridorStepV01
        and type(value.g2a_current_dependency_observations) is tuple
        and all(
            type(item) is _action_packet.ActionDependencyCurrentObservationV01
            for item in value.g2a_current_dependency_observations
        )
        and type(value.g2a_logical_time_bridge) is _action_packet.LogicalTimeBridgeV01
        and _exact_int_valid(value.g2a_evaluation_time)
        and _project_ref_valid(value.g2a_evaluation_time_source)
        and _project_ref_valid(value.g2a_evaluation_context_id)
        and type(value.g2a_transition_registry_profile)
        is ActionPacketTransitionRegistryProfileV01
    )
    if not (g2a_no_packet or g2a_present):
        errors.append("g2c_source_context_invalid")
    if type(value.g2b_compatibility_projections) is not tuple or any(
        type(item) is not _compatibility.LegacyDRSProjectionV01
        for item in value.g2b_compatibility_projections
    ):
        errors.append("g2c_source_context_invalid")
    root_triple = (
        value.g2b_root_kernel,
        value.g2b_root_decision_input,
        value.g2b_root_decision_result,
    )
    roots_absent = all(item is None for item in root_triple)
    roots_present = (
        type(value.g2b_root_kernel) is RootDecisionKernelV01
        and type(value.g2b_root_decision_input) is RootDecisionInputV01
        and type(value.g2b_root_decision_result) is RootDecisionResultV01
    )
    g2b_absent = (
        value.g2b_resolution_report is None
        and value.g2b_compatibility_projections == ()
        and value.g2b_use_time is None
        and roots_absent
    )
    g2b_context = (
        type(value.g2b_resolution_report) is _resolution.DRSResolutionReportV01
        and bool(value.g2b_compatibility_projections)
        and _exact_int_valid(value.g2b_use_time)
        and roots_absent
    )
    g2b_direct = (
        type(value.g2b_resolution_report) is _resolution.DRSResolutionReportV01
        and bool(value.g2b_compatibility_projections)
        and _exact_int_valid(value.g2b_use_time)
        and roots_present
    )
    if value.g2b_writeback_evidence is not None or not (
        g2b_absent or g2b_context or g2b_direct
    ):
        errors.append("g2c_source_context_invalid")
    return _sort_public_reasons(errors) if errors else ()


def build_execution_mode_validation_report_v01(
    *,
    validation_target: str,
    validated_artifact_id: str | None,
    request_id: str | None,
    transaction_id: str | None,
    owning_root_id: str | None,
    domain_id: str | None,
    validation_status: str,
    failure_stage: str,
    return_to_root_required: bool,
    reason_codes: tuple[str, ...],
    source_reason_codes: tuple[str, ...],
) -> ExecutionModeValidationReportV01:
    try:
        provisional = ExecutionModeValidationReportV01(
            validation_report_id="emvalidation_v01:" + _ZERO_SHA256,
            validation_target=validation_target,
            validated_artifact_id=validated_artifact_id,
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            validation_status=validation_status,
            failure_stage=failure_stage,
            return_to_root_required=return_to_root_required,
            reason_codes=reason_codes,
            source_reason_codes=source_reason_codes,
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )
        report = replace(
            provisional,
            validation_report_id=_rebuild_identity(provisional),
        )
        errors = _validation_report_errors(report)
        if errors:
            raise ValueError(errors[0])
        return report
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_scalar_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_scalar_invalid") from None


def _structural_report(
    *,
    target: str,
    value: object,
    errors: tuple[str, ...],
) -> ExecutionModeValidationReportV01:
    if errors:
        return build_execution_mode_validation_report_v01(
            validation_target=target,
            validated_artifact_id=None,
            request_id=None,
            transaction_id=None,
            owning_root_id=None,
            domain_id=None,
            validation_status="FAIL_CLOSED",
            failure_stage=(
                "SOURCE_CONTEXT" if target == "SOURCE_CONTEXT_STRUCTURAL" else "STRUCTURAL"
            ),
            return_to_root_required=True,
            reason_codes=errors,
            source_reason_codes=(),
        )
    if target == "SOURCE_CONTEXT_STRUCTURAL":
        return build_execution_mode_validation_report_v01(
            validation_target=target,
            validated_artifact_id=None,
            request_id=None,
            transaction_id=None,
            owning_root_id=None,
            domain_id=None,
            validation_status="PASS",
            failure_stage="NONE",
            return_to_root_required=False,
            reason_codes=(),
            source_reason_codes=(),
        )
    domain_id = getattr(value, "domain_id", None)
    if type(value) is ExecutionModeRouterInputV01:
        domain_id = value.local_routing_snapshot.domain_id
    identity_field = _IDENTITY_PROFILES[type(value)][0]
    return build_execution_mode_validation_report_v01(
        validation_target=target,
        validated_artifact_id=getattr(value, identity_field),
        request_id=getattr(value, "request_id"),
        transaction_id=getattr(value, "transaction_id"),
        owning_root_id=getattr(value, "owning_root_id"),
        domain_id=domain_id,
        validation_status="PASS",
        failure_stage="NONE",
        return_to_root_required=False,
        reason_codes=(),
        source_reason_codes=(),
    )


def validate_execution_mode_source_context_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    try:
        return _structural_report(
            target="SOURCE_CONTEXT_STRUCTURAL",
            value=value,
            errors=_source_context_errors(value),
        )
    except Exception:
        return _structural_report(
            target="SOURCE_CONTEXT_STRUCTURAL",
            value=value,
            errors=("g2c_source_context_invalid",),
        )


class _C2SourceFailure(Exception):
    def __init__(
        self,
        reason: str,
        stage: str,
        source_reasons: tuple[str, ...] = (),
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.stage = stage
        self.source_reasons = _dedupe(source_reasons)


def _raise_c2(
    reason: str,
    stage: str,
    source_reasons: object = (),
) -> None:
    normalized = (
        tuple(item for item in source_reasons if type(item) is str)
        if type(source_reasons) in {tuple, list}
        else ()
    )
    raise _C2SourceFailure(reason, stage, normalized)


def _source_acceptance(
    result: object,
    *,
    reason: str,
    stage: str,
) -> None:
    if type(result) is not dict:
        _raise_c2(reason, stage)
    source_reasons = result.get("reasons")
    if type(source_reasons) is not tuple:
        source_reasons = ()
    if result.get("accepted") is not True or source_reasons:
        _raise_c2(reason, stage, source_reasons)


def _boolean_source_acceptance(
    result: object,
    *,
    reason: str,
    stage: str,
) -> None:
    if (
        type(result) is not tuple
        or len(result) != 2
        or type(result[0]) is not bool
        or type(result[1]) is not tuple
        or result != (True, ())
    ):
        source_reasons = result[1] if type(result) is tuple and len(result) == 2 else ()
        _raise_c2(reason, stage, source_reasons)


def _empty_reason_source_acceptance(
    result: object,
    *,
    reason: str,
    stage: str,
) -> None:
    if type(result) is not tuple or result:
        _raise_c2(reason, stage, result)


def _source_plain_data(value: object) -> object:
    if value is None or type(value) in {bool, int, float, str}:
        return value
    if type(value) is tuple:
        return [_source_plain_data(item) for item in value]
    if type(value) is list:
        return [_source_plain_data(item) for item in value]
    if type(value) is dict:
        return {key: _source_plain_data(item) for key, item in value.items()}
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _source_plain_data(getattr(value, field.name))
            for field in fields(type(value))
        }
    raise ValueError("g2c_source_validator_failed")


def _finish_c2_binding(value: object, identity_field: str) -> object:
    result = replace(value, **{identity_field: _rebuild_identity(value)})
    errors = _STRUCTURAL_ERROR_FUNCTIONS[type(result)](result)
    if errors:
        raise _C2SourceFailure(errors[0], "STRUCTURAL")
    return result


def _public_c2_builder(call: object, fallback: str) -> object:
    try:
        return call()
    except _C2SourceFailure as exc:
        raise ValueError(exc.reason) from None
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = fallback
        raise ValueError(reason) from None
    except Exception:
        raise ValueError(fallback) from None


def build_execution_mode_source_context_v01(
    *,
    business_request_context_packet: dict[str, object],
    bsep_packet: dict[str, object],
    bsep_route_context_packet: dict[str, object],
    bsep_orchestrator_proposal: dict[str, object],
    bsep_structured_rationale: dict[str, object],
    sealed_replay_evidence: SealedReplayEvidenceV01 | None,
    replay_source_manifest: SealedPackageManifestV01 | None,
    replay_source_domain_projection: DomainEvidenceProjectionV01 | None,
    replay_source_safe_file_contents: tuple[bytes, ...],
    replay_anchor_publication: ExternalAnchorPublicationV01 | None,
    replay_anchored_verification: AnchoredPackageVerificationV01 | None,
    replay_supplied_anchor_publication_id: str | None,
    replay_reconstructed_manifest: SealedPackageManifestV01 | None,
    replay_reconstructed_domain_projection: DomainEvidenceProjectionV01 | None,
    replay_reconstructed_safe_file_contents: tuple[bytes, ...],
    g2a_inspection: ActionPacketPresentEligibilityInspectionV01 | None,
    g2a_registry: ActionCommitPacketRegistryV02 | None,
    g2a_packet_id: str | None,
    g2a_corridor: ContractFulfillmentCorridorV01 | None,
    g2a_corridor_step: CorridorStepV01 | None,
    g2a_current_dependency_observations: tuple[
        ActionDependencyCurrentObservationV01, ...
    ],
    g2a_logical_time_bridge: LogicalTimeBridgeV01 | None,
    g2a_evaluation_time: int | None,
    g2a_evaluation_time_source: str | None,
    g2a_evaluation_context_id: str | None,
    g2a_transition_registry_profile: ActionPacketTransitionRegistryProfileV01 | None,
    g2b_resolution_report: DRSResolutionReportV01 | None,
    g2b_compatibility_projections: tuple[LegacyDRSProjectionV01, ...],
    g2b_use_time: int | None,
    g2b_root_kernel: RootDecisionKernelV01 | None,
    g2b_root_decision_input: RootDecisionInputV01 | None,
    g2b_root_decision_result: RootDecisionResultV01 | None,
    g2b_writeback_evidence: None,
) -> ExecutionModeSourceContextV01:
    def build() -> ExecutionModeSourceContextV01:
        value = ExecutionModeSourceContextV01(
            business_request_context_packet=business_request_context_packet,
            bsep_packet=bsep_packet,
            bsep_route_context_packet=bsep_route_context_packet,
            bsep_orchestrator_proposal=bsep_orchestrator_proposal,
            bsep_structured_rationale=bsep_structured_rationale,
            sealed_replay_evidence=sealed_replay_evidence,
            replay_source_manifest=replay_source_manifest,
            replay_source_domain_projection=replay_source_domain_projection,
            replay_source_safe_file_contents=replay_source_safe_file_contents,
            replay_anchor_publication=replay_anchor_publication,
            replay_anchored_verification=replay_anchored_verification,
            replay_supplied_anchor_publication_id=(
                replay_supplied_anchor_publication_id
            ),
            replay_reconstructed_manifest=replay_reconstructed_manifest,
            replay_reconstructed_domain_projection=(
                replay_reconstructed_domain_projection
            ),
            replay_reconstructed_safe_file_contents=(
                replay_reconstructed_safe_file_contents
            ),
            g2a_inspection=g2a_inspection,
            g2a_registry=g2a_registry,
            g2a_packet_id=g2a_packet_id,
            g2a_corridor=g2a_corridor,
            g2a_corridor_step=g2a_corridor_step,
            g2a_current_dependency_observations=(
                g2a_current_dependency_observations
            ),
            g2a_logical_time_bridge=g2a_logical_time_bridge,
            g2a_evaluation_time=g2a_evaluation_time,
            g2a_evaluation_time_source=g2a_evaluation_time_source,
            g2a_evaluation_context_id=g2a_evaluation_context_id,
            g2a_transition_registry_profile=g2a_transition_registry_profile,
            g2b_resolution_report=g2b_resolution_report,
            g2b_compatibility_projections=g2b_compatibility_projections,
            g2b_use_time=g2b_use_time,
            g2b_root_kernel=g2b_root_kernel,
            g2b_root_decision_input=g2b_root_decision_input,
            g2b_root_decision_result=g2b_root_decision_result,
            g2b_writeback_evidence=g2b_writeback_evidence,
        )
        report = validate_execution_mode_source_context_v01(value)
        if report.validation_status != "PASS":
            raise _C2SourceFailure(report.reason_codes[0], "SOURCE_CONTEXT")
        return value

    return _public_c2_builder(build, "g2c_source_context_invalid")  # type: ignore[return-value]


_BSEP_BUSINESS_REQUEST_KEYS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_refs",
    "domain",
    "root_final_authority_preserved",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "real_world_effects_allowed",
    "Root remains final authority",
    "request_id",
    "business_subject",
    "requested_action",
    "explicit_blockers",
    "user_visible_summary",
    "forbidden_authority_fields",
    "forbidden_action_fields",
)

_BSEP_ROUTE_CONTEXT_KEYS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_refs",
    "domain",
    "root_final_authority_preserved",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "real_world_effects_allowed",
    "Root remains final authority",
    "allowed_routes",
    "required_guards",
    "selected_vector_ids",
    "route_validation_expectations",
    "orchestrator_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
)

_BSEP_STRUCTURED_RATIONALE_KEYS = (
    "rationale_type",
    "schema_version",
    "observed_semantics",
    "route_selection_reason",
    "rejected_routes",
    "required_guards_reasoning",
    "selected_vector_reasoning",
    "uncertainty_notes",
    "authority_boundary",
    "root_review_required",
    "orchestrator_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
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

_BSEP_PACKET_KEYS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_refs",
    "domain",
    "root_final_authority_preserved",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "drs_write_claimed",
    "root_bypass_claimed",
    "real_world_effects_allowed",
    "Root remains final authority",
    "source_role",
    "target_role",
    "source_route_id",
    "source_proposal_id",
    "source_context_packet_id",
    "source_structured_rationale_ref",
    "schema_version",
    "action_commit_packet_claimed",
    "raw_user_text_included",
    "raw_cross_role_text_included",
    "ContextPacket is not truth",
    "ContextPacket is not authority",
    "BoundedSemanticEvidencePacket is not truth",
    "BoundedSemanticEvidencePacket is not authority",
    "BoundedSemanticEvidencePacket is not FinalOutput",
    "BoundedSemanticEvidencePacket is not ActionCommitPacket",
    "Evidence packet is not action permission",
    "Gemini proposes, Root disposes",
    "observed_semantic_facts",
    "missing_evidence",
    "uncertainty_notes",
    "risk_boundary_notes",
    "rejected_action_routes",
    "required_approvals_or_conditions",
    "authority_boundary_notes",
    "selected_vector_ids",
    "required_guards",
)

_BSEP_EVIDENCE_ITEM_FIELDS = (
    "observed_semantic_facts",
    "missing_evidence",
    "uncertainty_notes",
    "risk_boundary_notes",
    "rejected_action_routes",
    "required_approvals_or_conditions",
    "authority_boundary_notes",
)

_BSEP_EVIDENCE_ITEM_KEYS = (
    "text",
    "source",
    "evidence_kind",
    "confidence_label",
    "candidate_only",
    "raw_quote",
)

_SOURCE_FORBIDDEN_TRUE_FIELDS = (
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
    "real_world_effects_allowed",
    "orchestrator_is_root",
    "creates_action_commit_packet",
    "calls_connectors",
    "authority_created",
    "permission_created",
    "action_permission_created",
    "packet_created",
    "receipt_created",
    "topology_created",
    "final_output_created",
    "drs_write_created",
    "effect_created",
    "creates_authority",
    "creates_permission",
    "creates_packet",
    "creates_receipt",
    "creates_topology",
    "creates_final_output",
    "creates_effect",
    "execution_authorized",
    "route_authorized",
    "root_final_created",
    "effect_allowed",
)


_SOURCE_ZERO_OPERATION_COUNTER_FIELDS = (
    "real_world_effects_count",
    "provider_calls",
    "network_calls",
    "gemini_calls",
    "external_drs_calls",
    "connector_calls",
)


def _exact_source_key_set(value: dict[str, object], expected: tuple[str, ...]) -> bool:
    return all(type(key) is str for key in value) and set(value) == set(expected)


def _exact_bsep_evidence_item_shapes(value: dict[str, object]) -> bool:
    for field_name in _BSEP_EVIDENCE_ITEM_FIELDS:
        items = value.get(field_name)
        if type(items) is not tuple:
            return False
        for item in items:
            if type(item) is not dict or not _exact_source_key_set(
                item, _BSEP_EVIDENCE_ITEM_KEYS
            ):
                return False
    return True


def _safe_source_claims(value: dict[str, object]) -> bool:
    def visit(item: object, active: set[int]) -> bool:
        if item is None or type(item) in {bool, int, float, str}:
            return True
        if type(item) not in {dict, tuple, list}:
            return False
        marker = id(item)
        if marker in active:
            return False
        active.add(marker)
        try:
            if type(item) is dict:
                for key, nested in item.items():
                    if type(key) is not str or key == "provider_selected_mode":
                        return False
                    if key in _SOURCE_FORBIDDEN_TRUE_FIELDS and nested is not False:
                        return False
                    if key in _SOURCE_ZERO_OPERATION_COUNTER_FIELDS and (
                        type(nested) is not int or nested != 0
                    ):
                        return False
                    if not visit(nested, active):
                        return False
                return True
            return all(visit(nested, active) for nested in item)
        finally:
            active.remove(marker)

    return visit(value, set())


def _validated_bsep_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeBSEPBindingV01:
    import hedgehog.context_packets as _context_packets
    import hedgehog.semantic_reasoning_adapter as _semantic_adapter
    import hedgehog.structured_rationale as _structured_rationale

    if type(source_context) is not ExecutionModeSourceContextV01:
        _raise_c2("g2c_source_context_invalid", "SOURCE_CONTEXT")
    context_report = validate_execution_mode_source_context_v01(source_context)
    if context_report.validation_status != "PASS":
        _raise_c2("g2c_source_context_invalid", "SOURCE_CONTEXT")
    business = source_context.business_request_context_packet
    route = source_context.bsep_route_context_packet
    proposal = source_context.bsep_orchestrator_proposal
    rationale = source_context.bsep_structured_rationale
    packet = source_context.bsep_packet

    business_result = _context_packets.validate_business_request_context_packet(
        business
    )
    _source_acceptance(
        business_result,
        reason="g2c_business_request_invalid",
        stage="BUSINESS_REQUEST",
    )
    if (
        not _exact_source_key_set(business, _BSEP_BUSINESS_REQUEST_KEYS)
        or business.get("request_id") != request_id
        or business.get("domain") != domain_id
        or not _source_identity_valid(business.get("packet_id"))
        or not _safe_source_claims(business)
        or business.get("root_final_authority_preserved") is not True
    ):
        _raise_c2("g2c_business_request_invalid", "BUSINESS_REQUEST")

    route_result = _context_packets.validate_orchestrator_route_context_packet(route)
    _source_acceptance(
        route_result,
        reason="g2c_route_context_invalid",
        stage="BSEP",
    )
    if (
        not _exact_source_key_set(route, _BSEP_ROUTE_CONTEXT_KEYS)
        or not _safe_source_claims(route)
    ):
        _raise_c2("g2c_route_context_invalid", "BSEP")
    expected_source_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": domain_id,
    }
    for source_refs in (route.get("source_refs"), packet.get("source_refs")):
        if type(source_refs) is not tuple or source_refs != (expected_source_ref,):
            _raise_c2("g2c_business_request_ref_invalid", "BSEP")

    proposal_reasons = _semantic_adapter.validate_orchestrator_semantic_reasoning_proposal(
        proposal
    )
    _empty_reason_source_acceptance(
        proposal_reasons,
        reason="g2c_semantic_proposal_invalid",
        stage="BSEP",
    )
    if not _exact_source_key_set(
        proposal, _semantic_adapter.ORCHESTRATOR_SEMANTIC_REASONING_REQUIRED_FIELDS
    ):
        _raise_c2("g2c_semantic_proposal_invalid", "BSEP")
    confidence = proposal.get("confidence")
    if (
        type(confidence) not in {int, float}
        or type(confidence) is bool
        or not math.isfinite(confidence)
        or not 0.0 <= confidence <= 1.0
        or proposal.get("needs_review") is not True
        or proposal.get("root_review_required") is not True
        or not _safe_source_claims(proposal)
    ):
        _raise_c2("g2c_semantic_proposal_invalid", "BSEP")

    rationale_result = _structured_rationale.validate_orchestrator_structured_rationale(
        rationale
    )
    _source_acceptance(
        rationale_result,
        reason="g2c_structured_rationale_invalid",
        stage="BSEP",
    )
    if (
        not _exact_source_key_set(rationale, _BSEP_STRUCTURED_RATIONALE_KEYS)
        or rationale.get("root_review_required") is not True
        or rationale.get("root_final_authority_preserved") is not True
        or not _safe_source_claims(rationale)
    ):
        _raise_c2("g2c_structured_rationale_invalid", "BSEP")

    packet_result = _context_packets.validate_bounded_semantic_evidence_packet(
        packet,
        route_context_packet=route,
        orchestrator_proposal=proposal,
        structured_rationale_validation=rationale_result,
    )
    _source_acceptance(packet_result, reason="g2c_bsep_invalid", stage="BSEP")
    if (
        not _exact_source_key_set(packet, _BSEP_PACKET_KEYS)
        or not _exact_bsep_evidence_item_shapes(packet)
        or not _safe_source_claims(packet)
    ):
        _raise_c2("g2c_bsep_invalid", "BSEP")
    expected_route = packet.get("source_route_id")
    expected_vectors = packet.get("selected_vector_ids")
    expected_guards = packet.get("required_guards")
    rationale_sha = _plain_sha256(rationale)
    rationale_ref = "structured_rationale_v01:" + rationale_sha
    route_expectations = route.get("route_validation_expectations")
    if (
        packet.get("domain") != domain_id
        or packet.get("source_context_packet_id") != route.get("packet_id")
        or packet.get("source_proposal_id") != proposal.get("proposal_id")
        or packet.get("source_structured_rationale_ref") != rationale_ref
        or packet.get("source_role") != "orchestrator"
        or packet.get("target_role") != "architect"
        or packet.get("root_final_authority_preserved") is not True
        or route.get("domain") != domain_id
        or route.get("allowed_routes") != (expected_route,)
        or route.get("selected_vector_ids") != expected_vectors
        or route.get("required_guards") != expected_guards
        or route_expectations
        != {
            "root_review_required": True,
            "selected_only_allowed_vectors": True,
        }
        or proposal.get("proposal_id") != packet.get("source_proposal_id")
        or proposal.get("suggested_route") != expected_route
        or tuple(proposal.get("selected_vector_ids", ())) != expected_vectors
        or tuple(proposal.get("required_guards", ())) != expected_guards
    ):
        _raise_c2("g2c_bsep_invalid", "BSEP")

    business_sha = _plain_sha256(business)
    route_sha = _plain_sha256(route)
    proposal_sha = _plain_sha256(proposal)
    packet_sha = _plain_sha256(packet)
    family_sha = _bsep_source_family_sha256(
        business_request_packet_sha256=business_sha,
        source_route_context_sha256=route_sha,
        source_proposal_sha256=proposal_sha,
        source_structured_rationale_sha256=rationale_sha,
        source_packet_sha256=packet_sha,
    )
    provisional = ExecutionModeBSEPBindingV01(
        bsep_binding_id="embsep_v01:" + _ZERO_SHA256,
        binding_state="BOUNDED_SEMANTIC_EVIDENCE_BOUND",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        business_request_packet_id=business["packet_id"],
        business_request_packet_sha256=business_sha,
        source_packet_id=packet["packet_id"],
        source_packet_sha256=packet_sha,
        source_packet_type=packet["packet_type"],
        source_schema_version=packet["schema_version"],
        source_route_context_packet_id=route["packet_id"],
        source_route_context_sha256=route_sha,
        source_route_id=expected_route,
        source_proposal_id=packet["source_proposal_id"],
        source_proposal_sha256=proposal_sha,
        source_structured_rationale_ref=rationale_ref,
        source_structured_rationale_sha256=rationale_sha,
        source_family_sha256=family_sha,
        source_domain=packet["domain"],
        source_role=packet["source_role"],
        target_role=packet["target_role"],
        source_reason_codes=(),
        root_final_authority_preserved=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "bsep_binding_id")  # type: ignore[return-value]


def build_execution_mode_bsep_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeBSEPBindingV01:
    return _public_c2_builder(
        lambda: _validated_bsep_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            source_context=source_context,
        ),
        "g2c_bsep_invalid",
    )  # type: ignore[return-value]


def _replay_not_applicable_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
) -> ExecutionModeReplayBindingV01:
    provisional = ExecutionModeReplayBindingV01(
        replay_binding_id="emreplay_v01:" + _ZERO_SHA256,
        binding_state="NOT_APPLICABLE",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        replay_id=None,
        source_replay_sha256=None,
        replay_status="NOT_APPLICABLE",
        source_manifest_id=None,
        reconstructed_manifest_id=None,
        anchor_publication_id=None,
        anchored_verification_id=None,
        source_domain_projection_id=None,
        reconstructed_domain_projection_id=None,
        package_id=None,
        logical_package_ref=None,
        source_package_content_hash=None,
        reconstructed_package_content_hash=None,
        integrity_verified=False,
        continuity_verified=False,
        anchor_verified=False,
        evidence_refs=(),
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "replay_binding_id")  # type: ignore[return-value]


def build_execution_mode_replay_not_applicable_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
) -> ExecutionModeReplayBindingV01:
    return _public_c2_builder(
        lambda: _replay_not_applicable_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
        ),
        "g2c_replay_binding_invalid",
    )  # type: ignore[return-value]


def _validated_replay_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeReplayBindingV01:
    import hedgehog.evidence.external_anchor_v01 as _external_anchor
    import hedgehog.evidence.sealed_evidence_profile_v01 as _evidence_profile
    import hedgehog.evidence.sealed_package_v01 as _sealed_package
    import hedgehog.evidence.sealed_replay_evidence_v01 as _sealed_replay

    replay = source_context.sealed_replay_evidence
    source_manifest = source_context.replay_source_manifest
    source_projection = source_context.replay_source_domain_projection
    source_contents = source_context.replay_source_safe_file_contents
    publication = source_context.replay_anchor_publication
    verification = source_context.replay_anchored_verification
    supplied_anchor_id = source_context.replay_supplied_anchor_publication_id
    rebuilt_manifest = source_context.replay_reconstructed_manifest
    rebuilt_projection = source_context.replay_reconstructed_domain_projection
    rebuilt_contents = source_context.replay_reconstructed_safe_file_contents
    if not all(
        (
            type(replay) is _sealed_replay.SealedReplayEvidenceV01,
            type(source_manifest) is _sealed_package.SealedPackageManifestV01,
            type(source_projection)
            is _evidence_profile.DomainEvidenceProjectionV01,
            type(publication) is _external_anchor.ExternalAnchorPublicationV01,
            type(verification)
            is _external_anchor.AnchoredPackageVerificationV01,
            type(supplied_anchor_id) is str,
            type(rebuilt_manifest) is _sealed_package.SealedPackageManifestV01,
            type(rebuilt_projection)
            is _evidence_profile.DomainEvidenceProjectionV01,
        )
    ):
        _raise_c2("g2c_replay_binding_invalid", "REPLAY")
    for result in (
        _evidence_profile.validate_domain_evidence_projection_v01(source_projection),
        _evidence_profile.validate_domain_evidence_projection_v01(rebuilt_projection),
        _sealed_package.validate_sealed_package_manifest_v01(
            source_manifest,
            domain_projection=source_projection,
            safe_file_contents=source_contents,
        ),
        _sealed_package.validate_sealed_package_manifest_v01(
            rebuilt_manifest,
            domain_projection=rebuilt_projection,
            safe_file_contents=rebuilt_contents,
        ),
        _external_anchor.validate_external_anchor_publication_v01(
            publication,
            manifest=source_manifest,
            domain_projection=source_projection,
            safe_file_contents=source_contents,
        ),
        _external_anchor.validate_anchored_package_verification_v01(
            verification,
            anchor_publication=publication,
            manifest=source_manifest,
            domain_projection=source_projection,
            safe_file_contents=source_contents,
            supplied_anchor_publication_id=supplied_anchor_id,
        ),
    ):
        _empty_reason_source_acceptance(
            result,
            reason="g2c_replay_binding_invalid",
            stage="REPLAY",
        )
    replay_reasons = _sealed_replay.validate_sealed_replay_evidence_v01(
        replay,
        source_manifest=source_manifest,
        source_domain_projection=source_projection,
        source_safe_file_contents=source_contents,
        anchor_publication=publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=supplied_anchor_id,
        reconstructed_manifest=rebuilt_manifest,
        reconstructed_domain_projection=rebuilt_projection,
        reconstructed_safe_file_contents=rebuilt_contents,
    )
    _empty_reason_source_acceptance(
        replay_reasons,
        reason="g2c_replay_binding_invalid",
        stage="REPLAY",
    )
    if (
        replay.domain_id != domain_id
        or replay.replay_status != "PASS"
        or not all(
            (replay.integrity_verified, replay.continuity_verified, replay.anchor_verified)
        )
    ):
        _raise_c2("g2c_replay_binding_invalid", "REPLAY")
    replay_plain = _sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
        replay,
        source_manifest=source_manifest,
        source_domain_projection=source_projection,
        source_safe_file_contents=source_contents,
        anchor_publication=publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=supplied_anchor_id,
        reconstructed_manifest=rebuilt_manifest,
        reconstructed_domain_projection=rebuilt_projection,
        reconstructed_safe_file_contents=rebuilt_contents,
    )
    provisional = ExecutionModeReplayBindingV01(
        replay_binding_id="emreplay_v01:" + _ZERO_SHA256,
        binding_state="SEALED_REPLAY_BOUND",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        replay_id=replay.replay_id,
        source_replay_sha256=_plain_sha256(replay_plain),
        replay_status=replay.replay_status,
        source_manifest_id=replay.source_manifest_id,
        reconstructed_manifest_id=replay.reconstructed_manifest_id,
        anchor_publication_id=replay.anchor_publication_id,
        anchored_verification_id=replay.anchored_verification_id,
        source_domain_projection_id=replay.source_domain_projection_id,
        reconstructed_domain_projection_id=(
            replay.reconstructed_domain_projection_id
        ),
        package_id=replay.package_id,
        logical_package_ref=replay.logical_package_ref,
        source_package_content_hash=replay.source_package_content_hash,
        reconstructed_package_content_hash=(
            replay.reconstructed_package_content_hash
        ),
        integrity_verified=replay.integrity_verified,
        continuity_verified=replay.continuity_verified,
        anchor_verified=replay.anchor_verified,
        evidence_refs=replay.evidence_refs,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "replay_binding_id")  # type: ignore[return-value]


def build_execution_mode_replay_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeReplayBindingV01:
    return _public_c2_builder(
        lambda: _validated_replay_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            source_context=source_context,
        ),
        "g2c_replay_binding_invalid",
    )  # type: ignore[return-value]


def _g2a_no_packet_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    evaluation_time: int,
    evaluation_time_source: str,
    evaluation_context_id: str,
) -> ExecutionModeG2ABindingV01:
    provisional = ExecutionModeG2ABindingV01(
        g2a_binding_id="emg2a_v01:" + _ZERO_SHA256,
        binding_state="NO_PACKET",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        source_inspection_sha256=None,
        inspection_profile_id=None,
        registry_id=None,
        packet_id=None,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_time_source,
        evaluation_context_id=evaluation_context_id,
        historical_lifecycle_state="NO_PACKET",
        failed_provenance=None,
        transition_event_count=0,
        execution_attempt_count=0,
        idempotency_disposition="NOT_APPLICABLE",
        reservation_owner_packet_id=None,
        terminal_receipt_ref=None,
        lifecycle_terminal=False,
        eligible_for_corridor_revalidation=False,
        present_eligibility_status="NOT_APPLICABLE",
        present_executable=False,
        retry_eligible=False,
        source_reason_codes=(),
        transition_history_sha256=None,
        disposition_history_sha256=None,
        historical_result_unchanged=True,
        authority_created=False,
        permission_created=False,
        packet_created=False,
        receipt_created=False,
        adapter_calls=0,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "g2a_binding_id")  # type: ignore[return-value]


def build_execution_mode_g2a_no_packet_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    evaluation_time: int,
    evaluation_time_source: str,
    evaluation_context_id: str,
) -> ExecutionModeG2ABindingV01:
    return _public_c2_builder(
        lambda: _g2a_no_packet_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id,
        ),
        "g2c_g2a_relation_invalid",
    )  # type: ignore[return-value]


def _validated_g2a_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeG2ABindingV01:
    import hedgehog.action_commit_packet_v02 as _action_packet

    inspection = source_context.g2a_inspection
    validation = _action_packet.validate_action_packet_present_eligibility_inspection_v01(
        inspection,
        source_context.g2a_registry,
        packet_id=source_context.g2a_packet_id,
        corridor=source_context.g2a_corridor,
        corridor_step=source_context.g2a_corridor_step,
        current_dependency_observations=(
            source_context.g2a_current_dependency_observations
        ),
        logical_time_bridge=source_context.g2a_logical_time_bridge,
        evaluation_time=source_context.g2a_evaluation_time,
        evaluation_time_source=source_context.g2a_evaluation_time_source,
        evaluation_context_id=source_context.g2a_evaluation_context_id,
        action_packet_transition_registry_profile=(
            source_context.g2a_transition_registry_profile
        ),
    )
    _boolean_source_acceptance(
        validation,
        reason="g2c_g2a_present_inspection_invalid",
        stage="G2A",
    )
    if type(inspection) is not _action_packet.ActionPacketPresentEligibilityInspectionV01:
        _raise_c2("g2c_g2a_present_inspection_invalid", "G2A")
    entries = tuple(
        item
        for item in source_context.g2a_registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == inspection.packet_id
    )
    if len(entries) != 1:
        _raise_c2("g2c_g2a_present_inspection_invalid", "G2A")
    canonical = entries[0].root_bound_genesis.canonical_projection
    if canonical.transaction_id != transaction_id:
        _raise_c2("g2c_transaction_binding_mismatch", "G2A")
    if canonical.owning_local_root_id != owning_root_id:
        _raise_c2("g2c_root_binding_mismatch", "G2A")
    historical = inspection.historical_state
    inspection_plain = {
        field_name: _source_plain_data(getattr(inspection, field_name))
        for field_name in G2A_SOURCE_INSPECTION_SHA256_FIELDS_V01
    }
    provisional = ExecutionModeG2ABindingV01(
        g2a_binding_id="emg2a_v01:" + _ZERO_SHA256,
        binding_state="PRESENT_INSPECTION_BOUND",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        source_inspection_sha256=_plain_sha256(inspection_plain),
        inspection_profile_id=inspection.inspection_profile_id,
        registry_id=inspection.registry_id,
        packet_id=inspection.packet_id,
        evaluation_time=inspection.evaluation_time,
        evaluation_time_source=inspection.evaluation_time_source,
        evaluation_context_id=inspection.evaluation_context_id,
        historical_lifecycle_state=historical.lifecycle_state,
        failed_provenance=historical.failed_provenance,
        transition_event_count=historical.transition_event_count,
        execution_attempt_count=historical.execution_attempt_count,
        idempotency_disposition=historical.idempotency_disposition,
        reservation_owner_packet_id=historical.reservation_owner_packet_id,
        terminal_receipt_ref=historical.terminal_receipt_ref,
        lifecycle_terminal=historical.lifecycle_terminal,
        eligible_for_corridor_revalidation=(
            historical.eligible_for_corridor_revalidation
        ),
        present_eligibility_status=inspection.present_eligibility_status,
        present_executable=inspection.present_executable,
        retry_eligible=inspection.retry_eligible,
        source_reason_codes=inspection.reason_codes,
        transition_history_sha256=inspection.transition_history_sha256,
        disposition_history_sha256=inspection.disposition_history_sha256,
        historical_result_unchanged=inspection.historical_result_unchanged,
        authority_created=False,
        permission_created=False,
        packet_created=False,
        receipt_created=False,
        adapter_calls=0,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "g2a_binding_id")  # type: ignore[return-value]


def build_execution_mode_g2a_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeG2ABindingV01:
    return _public_c2_builder(
        lambda: _validated_g2a_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            source_context=source_context,
        ),
        "g2c_g2a_present_inspection_invalid",
    )  # type: ignore[return-value]


def _g2b_not_applicable_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
) -> ExecutionModeG2BBindingV01:
    provisional = ExecutionModeG2BBindingV01(
        g2b_binding_id="emg2b_v01:" + _ZERO_SHA256,
        binding_state="NOT_APPLICABLE",
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        report_id=None,
        report_sha256=None,
        semantic_address_id=None,
        query_id=None,
        query_evaluation_ids=(),
        eligible_candidate_ids=(),
        ranked_candidate_ids=(),
        selected_candidate_id=None,
        retrieval_plan_id=None,
        memory_descent_result_id=None,
        root_shortcut_projection_id=None,
        reuse_certificate_id=None,
        compatibility_projection_ids=(),
        compatibility_projection_set_sha256=None,
        use_time=None,
        source_root_kernel_id=None,
        source_root_decision_input_id=None,
        source_root_decision_id=None,
        source_root_decision_sha256=None,
        freshness_state="NOT_APPLICABLE",
        lineage_state="NOT_APPLICABLE",
        quarantine_present=False,
        deadend_present=False,
        context_available=False,
        direct_informational_reuse_eligible=False,
        source_reason_codes=(),
        persistent_records_unchanged=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        capability_created=False,
        topology_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "g2b_binding_id")  # type: ignore[return-value]


def build_execution_mode_g2b_not_applicable_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
) -> ExecutionModeG2BBindingV01:
    return _public_c2_builder(
        lambda: _g2b_not_applicable_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
        ),
        "g2c_g2b_binding_invalid",
    )  # type: ignore[return-value]


def _validate_g2b_report_family(
    report: hedgehog.drs_memory_resolution_v01.DRSResolutionReportV01,
) -> None:
    import hedgehog.drs_memory_resolution_v01 as _resolution
    import hedgehog.drs_semantic_address_v01 as _semantic_address
    import hedgehog.reuse_certificate_v01 as _reuse_certificate

    checks = (
        _semantic_address.validate_semantic_address_v01(report.semantic_address),
        _resolution.validate_drs_temporal_query_v01(report.query),
        *(
            _semantic_address.validate_meaning_record_v01(item)
            for item in report.source_records
        ),
        *(
            _resolution.validate_query_evaluation_state_v01(item)
            for item in report.query_evaluations
        ),
        *(
            _resolution.validate_resolution_candidate_v01(item)
            for item in report.eligible_candidates
        ),
        _resolution.validate_retrieval_plan_v01(report.retrieval_plan),
        *(
            (
                _resolution.validate_memory_descent_result_v01(
                    report.memory_descent_result
                ),
            )
            if report.memory_descent_result is not None
            else ()
        ),
        *(
            (
                _reuse_certificate.validate_root_shortcut_authorization_projection_v01(
                    report.root_shortcut_projection
                ),
            )
            if report.root_shortcut_projection is not None
            else ()
        ),
        *(
            (
                _reuse_certificate.validate_reuse_certificate_v01(
                    report.reuse_certificate
                ),
            )
            if report.reuse_certificate is not None
            else ()
        ),
        _resolution.validate_drs_resolution_report_v01(report),
    )
    for result in checks:
        _boolean_source_acceptance(
            result,
            reason="g2c_g2b_binding_invalid",
            stage="G2B",
        )


def _validated_g2b_binding(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeG2BBindingV01:
    import hedgehog.drs_g2b_compatibility_v01 as _compatibility
    import hedgehog.drs_memory_resolution_v01 as _resolution
    import hedgehog.reuse_certificate_v01 as _reuse_certificate

    report = source_context.g2b_resolution_report
    projections = source_context.g2b_compatibility_projections
    use_time = source_context.g2b_use_time
    if type(report) is not _resolution.DRSResolutionReportV01:
        _raise_c2("g2c_g2b_binding_invalid", "G2B")
    _validate_g2b_report_family(report)
    if type(projections) is not tuple or projections != report.source_projections:
        _raise_c2("g2c_source_object_substituted", "G2B")
    projection_plain: list[dict[str, object]] = []
    for projection in projections:
        _boolean_source_acceptance(
            _compatibility.validate_legacy_drs_projection_v01(projection),
            reason="g2c_g2b_binding_invalid",
            stage="G2B",
        )
        projection_plain.append(
            _compatibility.legacy_drs_projection_to_plain_data_v01(projection)
        )
    query = report.query
    if request_id == transaction_id:
        _raise_c2("g2c_transaction_binding_mismatch", "G2B")
    if transaction_id != query.query_id:
        _raise_c2("g2c_g2b_query_transaction_mismatch", "G2B")
    if query.owning_local_root_id != owning_root_id:
        _raise_c2("g2c_root_binding_mismatch", "G2B")
    if query.domain != domain_id:
        _raise_c2("g2c_domain_binding_mismatch", "G2B")
    if not _exact_int_valid(use_time) or use_time != query.evaluation_time:
        _raise_c2("g2c_g2b_use_time_invalid", "G2B")
    roots = (
        source_context.g2b_root_kernel,
        source_context.g2b_root_decision_input,
        source_context.g2b_root_decision_result,
    )
    roots_absent = all(item is None for item in roots)
    roots_present = (
        type(roots[0]) is RootDecisionKernelV01
        and type(roots[1]) is RootDecisionInputV01
        and type(roots[2]) is RootDecisionResultV01
    )
    if not (roots_absent or roots_present):
        _raise_c2("g2c_g2b_shortcut_invalid", "G2B")

    if roots_absent:
        if (
            query.query_mode != "MEMORY_CONTEXT_ONLY"
            or query.reuse_intent != "CONTEXT"
            or query.requested_reuse_classes != ("CONTEXT_ONLY",)
            or report.root_shortcut_projection is not None
            or report.reuse_certificate is not None
            or report.eligible_candidates != ()
            or report.ranked_candidate_ids != ()
            or report.selected_candidate_id is not None
            or not report.context_only_record_ids
        ):
            _raise_c2("g2c_g2b_binding_state_derivation_mismatch", "G2B")
        binding_state = "RESOLUTION_CONTEXT_BOUND"
        freshness = "STALE"
        direct = False
    else:
        kernel, decision_input, decision_result = roots
        if (
            query.query_mode != "DIRECT_REUSE_CANDIDATE"
            or query.reuse_intent != "INFORMATIONAL_SHORTCUT_CONSIDERATION"
            or report.selected_candidate_id is None
            or report.selected_candidate_id
            not in tuple(item.resolution_candidate_id for item in report.eligible_candidates)
            or report.selected_candidate_id not in report.ranked_candidate_ids
            or report.root_shortcut_projection is None
            or report.reuse_certificate is None
            or decision_input.transaction_id != query.query_id
            or decision_result.transaction_id != query.query_id
        ):
            _raise_c2("g2c_g2b_shortcut_invalid", "G2B")
        for result in (
            validate_root_decision_kernel_v01(kernel),
            validate_root_decision_input_v01(kernel=kernel, decision_input=decision_input),
            validate_root_decision_result_v01(
                kernel=kernel,
                decision_input=decision_input,
                result=decision_result,
            ),
        ):
            _empty_reason_source_acceptance(
                result,
                reason="g2c_g2b_shortcut_invalid",
                stage="G2B",
            )
        _boolean_source_acceptance(
            _reuse_certificate.validate_existing_root_shortcut_decision_v01(
                resolution_report=report,
                root_kernel=kernel,
                root_decision_input=decision_input,
                root_decision_result=decision_result,
                use_time=use_time,
            ),
            reason="g2c_g2b_shortcut_invalid",
            stage="G2B",
        )
        binding_state = "DIRECT_REUSE_BOUND"
        freshness = "CURRENT"
        direct = True

    quarantine = any(
        item.query_state == "BLOCKED_BY_QUARANTINE"
        for item in report.query_evaluations
    )
    deadend = any(
        item.query_state == "BLOCKED_BY_DEADEND"
        for item in report.query_evaluations
    )
    if direct and (quarantine or deadend):
        _raise_c2("g2c_g2b_shortcut_invalid", "G2B")
    root_kernel, root_input, root_result = roots
    provisional = ExecutionModeG2BBindingV01(
        g2b_binding_id="emg2b_v01:" + _ZERO_SHA256,
        binding_state=binding_state,
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        report_id=report.report_id,
        report_sha256=_plain_sha256(
            _resolution.drs_resolution_report_to_plain_data_v01(report)
        ),
        semantic_address_id=report.semantic_address.semantic_address_id,
        query_id=query.query_id,
        query_evaluation_ids=tuple(
            item.query_evaluation_id for item in report.query_evaluations
        ),
        eligible_candidate_ids=tuple(
            item.resolution_candidate_id for item in report.eligible_candidates
        ),
        ranked_candidate_ids=report.ranked_candidate_ids,
        selected_candidate_id=report.selected_candidate_id,
        retrieval_plan_id=report.retrieval_plan.retrieval_plan_id,
        memory_descent_result_id=(
            report.memory_descent_result.memory_descent_result_id
            if report.memory_descent_result is not None
            else None
        ),
        root_shortcut_projection_id=(
            report.root_shortcut_projection.root_shortcut_projection_id
            if report.root_shortcut_projection is not None
            else None
        ),
        reuse_certificate_id=(
            report.reuse_certificate.certificate_id
            if report.reuse_certificate is not None
            else None
        ),
        compatibility_projection_ids=tuple(item.projection_id for item in projections),
        compatibility_projection_set_sha256=_plain_sha256(projection_plain),
        use_time=use_time,
        source_root_kernel_id=(root_kernel.kernel_id if roots_present else None),
        source_root_decision_input_id=(
            root_input.decision_input_id if roots_present else None
        ),
        source_root_decision_id=(root_result.decision_id if roots_present else None),
        source_root_decision_sha256=(
            _plain_sha256(root_decision_result_to_plain_dict_v01(root_result))
            if roots_present
            else None
        ),
        freshness_state=freshness,
        lineage_state="VALIDATED",
        quarantine_present=quarantine,
        deadend_present=deadend,
        context_available=True,
        direct_informational_reuse_eligible=direct,
        source_reason_codes=(),
        persistent_records_unchanged=report.persistent_records_unchanged,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        capability_created=False,
        topology_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    return _finish_c2_binding(provisional, "g2b_binding_id")  # type: ignore[return-value]


def build_execution_mode_g2b_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeG2BBindingV01:
    return _public_c2_builder(
        lambda: _validated_g2b_binding(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            source_context=source_context,
        ),
        "g2c_g2b_binding_invalid",
    )  # type: ignore[return-value]


def _contextual_input_report(
    *,
    router_input: object,
    status: str,
    stage: str,
    reasons: tuple[str, ...],
    source_reasons: tuple[str, ...] = (),
) -> ExecutionModeValidationReportV01:
    identified = False
    validated_artifact_id: str | None = None
    request_id: str | None = None
    transaction_id: str | None = None
    owning_root_id: str | None = None
    domain_id: str | None = None
    if (
        type(router_input) is ExecutionModeRouterInputV01
        and type(router_input.local_routing_snapshot)
        is ExecutionModeLocalRoutingSnapshotV01
    ):
        candidate_values = (
            router_input.router_input_id,
            router_input.request_id,
            router_input.transaction_id,
            router_input.owning_root_id,
        )
        snapshot = router_input.local_routing_snapshot
        if (
            all(_project_ref_valid(item) for item in candidate_values)
            and type(snapshot) is ExecutionModeLocalRoutingSnapshotV01
            and _project_ref_valid(snapshot.domain_id)
        ):
            identified = True
            (
                validated_artifact_id,
                request_id,
                transaction_id,
                owning_root_id,
            ) = candidate_values
            domain_id = snapshot.domain_id
    return build_execution_mode_validation_report_v01(
        validation_target="ROUTER_INPUT_AGAINST_SOURCES",
        validated_artifact_id=(validated_artifact_id if identified else None),
        request_id=(request_id if identified else None),
        transaction_id=(transaction_id if identified else None),
        owning_root_id=(owning_root_id if identified else None),
        domain_id=(domain_id if identified else None),
        validation_status=status,
        failure_stage=stage,
        return_to_root_required=status != "PASS",
        reason_codes=reasons,
        source_reason_codes=_dedupe(source_reasons),
    )


def validate_execution_mode_router_input_against_sources_v01(
    *,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeValidationReportV01:
    try:
        source_report = validate_execution_mode_source_context_v01(source_context)
        if source_report.validation_status != "PASS":
            raise _C2SourceFailure(
                "g2c_source_context_invalid",
                "SOURCE_CONTEXT",
            )
        input_report = validate_execution_mode_router_input_v01(router_input)
        if input_report.validation_status != "PASS":
            raise _C2SourceFailure(input_report.reason_codes[0], "STRUCTURAL")
        domain_id = router_input.local_routing_snapshot.domain_id
        common = {
            "request_id": router_input.request_id,
            "transaction_id": router_input.transaction_id,
            "owning_root_id": router_input.owning_root_id,
            "domain_id": domain_id,
        }
        expected_bsep = _validated_bsep_binding(
            **common,
            source_context=source_context,
        )
        replay_values = (
            source_context.sealed_replay_evidence,
            source_context.replay_source_manifest,
            source_context.replay_source_domain_projection,
            source_context.replay_anchor_publication,
            source_context.replay_anchored_verification,
            source_context.replay_supplied_anchor_publication_id,
            source_context.replay_reconstructed_manifest,
            source_context.replay_reconstructed_domain_projection,
        )
        expected_replay = (
            _replay_not_applicable_binding(**common)
            if all(item is None for item in replay_values)
            else _validated_replay_binding(**common, source_context=source_context)
        )
        snapshot = router_input.local_routing_snapshot
        if (
            source_context.g2a_evaluation_time
            != snapshot.evaluation_time_epoch_seconds
            or source_context.g2a_evaluation_time_source != snapshot.created_by
            or source_context.g2a_evaluation_context_id
            != snapshot.local_routing_snapshot_id
        ):
            raise _C2SourceFailure("g2c_g2a_relation_invalid", "G2A")
        expected_g2a = (
            _g2a_no_packet_binding(
                **common,
                evaluation_time=snapshot.evaluation_time_epoch_seconds,
                evaluation_time_source=snapshot.created_by,
                evaluation_context_id=snapshot.local_routing_snapshot_id,
            )
            if source_context.g2a_inspection is None
            else _validated_g2a_binding(**common, source_context=source_context)
        )
        if snapshot.action_class == "NON_ACTION":
            g2a_relation_valid = (
                snapshot.action_packet_relation == "NOT_APPLICABLE"
                and expected_g2a.binding_state == "NO_PACKET"
            )
        elif snapshot.action_class == "ACTION":
            g2a_relation_valid = (
                snapshot.action_packet_relation == "NEW_ACTION_NO_PACKET"
                and expected_g2a.binding_state == "NO_PACKET"
            ) or (
                snapshot.action_packet_relation == "EXISTING_PACKET_ATTEMPT"
                and expected_g2a.binding_state == "PRESENT_INSPECTION_BOUND"
            )
        else:
            g2a_relation_valid = False
        if not g2a_relation_valid:
            raise _C2SourceFailure("g2c_g2a_relation_invalid", "G2A")
        expected_g2b = (
            _g2b_not_applicable_binding(**common)
            if source_context.g2b_resolution_report is None
            else _validated_g2b_binding(**common, source_context=source_context)
        )
        if expected_g2b.use_time is not None and (
            expected_g2b.use_time != snapshot.evaluation_time_epoch_seconds
        ):
            raise _C2SourceFailure("g2c_g2b_use_time_invalid", "G2B")
        expected = (expected_bsep, expected_replay, expected_g2a, expected_g2b)
        actual = (
            router_input.bsep_binding,
            router_input.replay_binding,
            router_input.g2a_binding,
            router_input.g2b_binding,
        )
        if actual != expected:
            reasons = (
                "g2c_source_object_substituted",
                "g2c_source_digest_mismatch",
                "g2c_g2a_relation_invalid",
                "g2c_g2b_binding_state_derivation_mismatch",
            )
            index = next(
                position
                for position, pair in enumerate(zip(actual, expected, strict=True))
                if pair[0] != pair[1]
            )
            stages = ("BSEP", "REPLAY", "G2A", "G2B")
            raise _C2SourceFailure(reasons[index], stages[index])
        expected_traces = tuple(
            sorted(
                {
                    expected_bsep.business_request_packet_id,
                    expected_bsep.bsep_binding_id,
                    snapshot.local_routing_snapshot_id,
                    expected_replay.replay_binding_id,
                    expected_g2a.g2a_binding_id,
                    expected_g2b.g2b_binding_id,
                }
            )
        )
        if router_input.trace_refs != expected_traces:
            raise _C2SourceFailure("g2c_source_object_substituted", "STRUCTURAL")
        return _contextual_input_report(
            router_input=router_input,
            status="PASS",
            stage="NONE",
            reasons=(),
        )
    except _C2SourceFailure as exc:
        return _contextual_input_report(
            router_input=router_input,
            status="FAIL_CLOSED",
            stage=exc.stage,
            reasons=(exc.reason,),
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return _contextual_input_report(
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="STRUCTURAL",
            reasons=("g2c_source_validator_failed",),
        )


def build_execution_mode_local_mode_profile_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    mode: str,
    policy_snapshot_id: str,
    capability_snapshot_id: str,
    cost_model_id: str,
    policy_allowed: bool,
    scope_allowed: bool,
    risk_allowed: bool,
    privacy_allowed: bool,
    capability_state: str,
    capability_id: str | None,
    cost_units: int,
) -> ExecutionModeLocalModeProfileV01:
    try:
        if not _exact_int_valid(cost_units, minimum=0):
            raise ValueError("g2c_cost_invalid")
        provisional = ExecutionModeLocalModeProfileV01(
            local_mode_profile_id="emprofile_v01:" + _ZERO_SHA256,
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            mode=mode,
            policy_snapshot_id=policy_snapshot_id,
            capability_snapshot_id=capability_snapshot_id,
            cost_model_id=cost_model_id,
            policy_allowed=policy_allowed,
            scope_allowed=scope_allowed,
            risk_allowed=risk_allowed,
            privacy_allowed=privacy_allowed,
            capability_state=capability_state,
            capability_id=capability_id,
            cost_unit="normalized_cost_units_v01",
            cost_units=cost_units,
            local_reason_codes=(),
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )
        provisional = replace(
            provisional,
            local_reason_codes=_derived_local_reasons(provisional),
        )
        profile = replace(
            provisional,
            local_mode_profile_id=_rebuild_identity(provisional),
        )
        errors = _local_profile_errors(profile)
        if errors:
            raise ValueError(errors[0])
        return profile
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_local_mode_profile_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_local_mode_profile_invalid") from None


def build_execution_mode_local_routing_snapshot_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    request_class: str,
    action_class: str,
    action_packet_relation: str,
    scope_class: str,
    scope_ref: str,
    permitted_narrower_scope_refs: tuple[str, ...],
    risk_class: str,
    policy_snapshot_id: str,
    capability_snapshot_id: str,
    cost_model_id: str,
    required_user_input_state: str,
    hard_block_state: str,
    evaluation_time_epoch_seconds: int,
    pt_created_at_utc: str,
    et_observed_at_utc: str,
    ct_session_anchor: str,
    ttl_seconds: int,
    freshness_class: str,
    valid_from_utc: str,
    valid_to_utc: str,
    mode_profiles: tuple[ExecutionModeLocalModeProfileV01, ...],
) -> ExecutionModeLocalRoutingSnapshotV01:
    try:
        if type(mode_profiles) is not tuple or len(mode_profiles) != LOCAL_MODE_PROFILE_COUNT:
            raise ValueError("g2c_local_mode_profile_set_invalid")
        if any(_local_profile_errors(item) for item in mode_profiles):
            raise ValueError("g2c_local_mode_profile_set_invalid")
        kt_asof_utc = _epoch_to_utc(evaluation_time_epoch_seconds)
        profile_sha = _mode_profile_set_sha256(mode_profiles)
        provisional = ExecutionModeLocalRoutingSnapshotV01(
            local_routing_snapshot_id="emlocal_v01:" + _ZERO_SHA256,
            created_by="OWNING_LOCAL_ROOT_ROUTING_SNAPSHOT_V01",
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            domain_id=domain_id,
            request_class=request_class,
            action_class=action_class,
            action_packet_relation=action_packet_relation,
            scope_class=scope_class,
            scope_ref=scope_ref,
            permitted_narrower_scope_refs=permitted_narrower_scope_refs,
            risk_class=risk_class,
            policy_snapshot_id=policy_snapshot_id,
            capability_snapshot_id=capability_snapshot_id,
            cost_model_id=cost_model_id,
            required_user_input_state=required_user_input_state,
            hard_block_state=hard_block_state,
            evaluation_time_epoch_seconds=evaluation_time_epoch_seconds,
            pt_created_at_utc=pt_created_at_utc,
            kt_asof_utc=kt_asof_utc,
            et_observed_at_utc=et_observed_at_utc,
            ct_session_anchor=ct_session_anchor,
            ttl_seconds=ttl_seconds,
            freshness_class=freshness_class,
            valid_from_utc=valid_from_utc,
            valid_to_utc=valid_to_utc,
            time_envelope_ref=_TIME_ENVELOPE_PREFIX + _ZERO_SHA256,
            mode_profile_set_id=_MODE_PROFILE_SET_PREFIX + _ZERO_SHA256,
            mode_profile_set_sha256=profile_sha,
            mode_profiles=mode_profiles,
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )
        provisional = replace(
            provisional,
            time_envelope_ref=_rebuild_time_envelope_ref(provisional),
        )
        provisional = replace(
            provisional,
            mode_profile_set_id=_rebuild_mode_profile_set_id(provisional),
        )
        snapshot = replace(
            provisional,
            local_routing_snapshot_id=_rebuild_identity(provisional),
        )
        errors = _snapshot_errors(snapshot)
        if errors:
            raise ValueError(errors[0])
        return snapshot
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_local_mode_profile_set_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_local_mode_profile_set_invalid") from None


def build_execution_mode_router_input_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    bsep_binding: ExecutionModeBSEPBindingV01,
    local_routing_snapshot: ExecutionModeLocalRoutingSnapshotV01,
    replay_binding: ExecutionModeReplayBindingV01,
    g2a_binding: ExecutionModeG2ABindingV01,
    g2b_binding: ExecutionModeG2BBindingV01,
) -> ExecutionModeRouterInputV01:
    try:
        expected_types = (
            (bsep_binding, ExecutionModeBSEPBindingV01),
            (local_routing_snapshot, ExecutionModeLocalRoutingSnapshotV01),
            (replay_binding, ExecutionModeReplayBindingV01),
            (g2a_binding, ExecutionModeG2ABindingV01),
            (g2b_binding, ExecutionModeG2BBindingV01),
        )
        if any(type(item) is not expected for item, expected in expected_types):
            raise ValueError("g2c_exact_type_invalid")
        trace_refs = tuple(
            sorted(
                {
                    bsep_binding.business_request_packet_id,
                    bsep_binding.bsep_binding_id,
                    local_routing_snapshot.local_routing_snapshot_id,
                    replay_binding.replay_binding_id,
                    g2a_binding.g2a_binding_id,
                    g2b_binding.g2b_binding_id,
                }
            )
        )
        provisional = ExecutionModeRouterInputV01(
            router_input_id="eminput_v01:" + _ZERO_SHA256,
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=owning_root_id,
            bsep_binding=bsep_binding,
            local_routing_snapshot=local_routing_snapshot,
            replay_binding=replay_binding,
            g2a_binding=g2a_binding,
            g2b_binding=g2b_binding,
            trace_refs=trace_refs,
        )
        router_input = replace(
            provisional,
            router_input_id=_rebuild_identity(provisional),
        )
        errors = _router_input_errors(router_input)
        if errors:
            raise ValueError(errors[0])
        return router_input
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_source_context_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_source_context_invalid") from None


class _C3Failure(Exception):
    def __init__(
        self,
        reason: str,
        stage: str,
        source_reasons: tuple[str, ...] = (),
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.stage = stage
        self.source_reasons = _dedupe(source_reasons)


def _public_reason_union(*groups: tuple[str, ...]) -> tuple[str, ...]:
    present = {
        reason
        for group in groups
        for reason in group
        if reason in _REASON_POSITION
    }
    return tuple(
        reason for reason in PUBLIC_G2C_REASON_CODES_V01 if reason in present
    )


def _require_c3_context(
    router_input: object,
    source_context: object,
) -> None:
    report = validate_execution_mode_router_input_against_sources_v01(
        router_input=router_input,  # type: ignore[arg-type]
        source_context=source_context,  # type: ignore[arg-type]
    )
    if report.validation_status != "PASS":
        reason = (
            report.reason_codes[0]
            if report.reason_codes
            else "g2c_source_validator_failed"
        )
        raise _C3Failure(reason, report.failure_stage, report.source_reason_codes)


def _present_g2a_usable(binding: ExecutionModeG2ABindingV01) -> bool:
    return (
        binding.binding_state == "PRESENT_INSPECTION_BOUND"
        and binding.present_eligibility_status
        == "ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT"
        and binding.present_executable is True
        and binding.retry_eligible is False
        and binding.source_reason_codes == ()
        and binding.failed_provenance is None
        and binding.historical_result_unchanged is True
        and binding.source_inspection_sha256 is not None
        and binding.transition_history_sha256 is not None
        and binding.disposition_history_sha256 is not None
    )


def _mode_action_allowed(
    mode: str,
    snapshot: ExecutionModeLocalRoutingSnapshotV01,
    g2a_binding: ExecutionModeG2ABindingV01,
) -> bool:
    relation = snapshot.action_packet_relation
    if mode == "direct_informational_reuse":
        return (
            snapshot.action_class == "NON_ACTION"
            and relation == "NOT_APPLICABLE"
            and g2a_binding.binding_state == "NO_PACKET"
        )
    if mode == "sealed_replay":
        return relation in {"NOT_APPLICABLE", "NEW_ACTION_NO_PACKET"}
    if relation == "EXISTING_PACKET_ATTEMPT":
        return _present_g2a_usable(g2a_binding)
    return relation in {"NOT_APPLICABLE", "NEW_ACTION_NO_PACKET"}


def _replay_available(binding: ExecutionModeReplayBindingV01) -> bool:
    return (
        binding.binding_state == "SEALED_REPLAY_BOUND"
        and binding.replay_id is not None
        and binding.source_replay_sha256 is not None
        and binding.replay_status == "PASS"
        and binding.integrity_verified is True
        and binding.continuity_verified is True
        and binding.anchor_verified is True
    )


def _direct_reuse_available(binding: ExecutionModeG2BBindingV01) -> bool:
    return (
        binding.binding_state == "DIRECT_REUSE_BOUND"
        and binding.context_available is True
        and binding.direct_informational_reuse_eligible is True
        and binding.freshness_state == "CURRENT"
        and binding.lineage_state == "VALIDATED"
        and binding.quarantine_present is False
        and binding.deadend_present is False
        and binding.report_id is not None
        and binding.reuse_certificate_id is not None
        and binding.source_root_decision_id is not None
    )


def _memory_context_available(binding: ExecutionModeG2BBindingV01) -> bool:
    return (
        binding.binding_state
        in {"RESOLUTION_CONTEXT_BOUND", "DIRECT_REUSE_BOUND"}
        and binding.context_available is True
        and binding.lineage_state == "VALIDATED"
        and binding.report_id is not None
    )


def _append_unique_ref(values: list[str], value: str | None) -> None:
    if value is not None and value not in values:
        values.append(value)


def _row_evidence(
    *,
    mode: str,
    router_input: ExecutionModeRouterInputV01,
    profile: ExecutionModeLocalModeProfileV01,
    capability_available: bool,
    mode_source_available: bool,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    required = [
        router_input.bsep_binding.bsep_binding_id,
        router_input.local_routing_snapshot.local_routing_snapshot_id,
        profile.local_mode_profile_id,
    ]
    satisfied = list(required)
    replay = router_input.replay_binding
    g2b = router_input.g2b_binding
    g2a = router_input.g2a_binding
    if mode == "sealed_replay":
        _append_unique_ref(required, replay.replay_binding_id)
        _append_unique_ref(satisfied, replay.replay_binding_id)
        _append_unique_ref(required, replay.replay_id)
        if mode_source_available:
            _append_unique_ref(satisfied, replay.replay_id)
    elif mode == "direct_informational_reuse":
        for item in (
            g2b.g2b_binding_id,
            g2b.report_id,
            g2b.reuse_certificate_id,
            g2b.source_root_decision_id,
        ):
            _append_unique_ref(required, item)
            _append_unique_ref(satisfied, item)
    elif mode == "memory_informed":
        _append_unique_ref(required, g2b.g2b_binding_id)
        _append_unique_ref(satisfied, g2b.g2b_binding_id)
        _append_unique_ref(required, g2b.report_id)
        if g2b.report_id is not None:
            _append_unique_ref(satisfied, g2b.report_id)
    if mode in _CAPABILITY_REQUIRED_MODES_V01:
        _append_unique_ref(required, profile.capability_id)
        if capability_available:
            _append_unique_ref(satisfied, profile.capability_id)
    if (
        router_input.local_routing_snapshot.action_packet_relation
        == "EXISTING_PACKET_ATTEMPT"
    ):
        for item in (
            g2a.g2a_binding_id,
            g2a.packet_id,
            g2a.source_inspection_sha256,
        ):
            _append_unique_ref(required, item)
            _append_unique_ref(satisfied, item)
    return tuple(required), tuple(satisfied)


def _finish_c3_row(
    provisional: ExecutionModeFeasibilityRowV01,
) -> ExecutionModeFeasibilityRowV01:
    row = replace(provisional, feasibility_row_id=_rebuild_identity(provisional))
    errors = _feasibility_row_errors(row)
    if errors:
        raise _C3Failure(errors[0], "FEASIBILITY")
    return row


def _build_feasibility_rows(
    router_input: ExecutionModeRouterInputV01,
) -> tuple[ExecutionModeFeasibilityRowV01, ...]:
    snapshot = router_input.local_routing_snapshot
    rank_by_mode = dict(EXECUTION_MODE_SAFE_DEPTH_RANKS_V01)
    executable_rows: list[ExecutionModeFeasibilityRowV01] = []
    hard_block = snapshot.hard_block_state == "BLOCKED"
    user_missing = (
        not hard_block
        and snapshot.required_user_input_state == "MISSING_RESOLVABLE"
    )
    for mode, profile in zip(
        EXECUTABLE_EXECUTION_MODES_V01,
        snapshot.mode_profiles,
        strict=True,
    ):
        if profile.mode != mode or _local_profile_errors(profile):
            raise _C3Failure("g2c_local_mode_profile_invalid", "LOCAL_PROFILE")
        capability_available = (
            profile.capability_state == "AVAILABLE"
            and profile.capability_id is not None
        )
        mode_source_available = True
        if mode == "sealed_replay":
            mode_source_available = _replay_available(router_input.replay_binding)
        elif mode == "direct_informational_reuse":
            mode_source_available = _direct_reuse_available(router_input.g2b_binding)
        elif mode == "memory_informed":
            mode_source_available = _memory_context_available(router_input.g2b_binding)
        local_reasons = list(profile.local_reason_codes)
        source_reason_needed = not mode_source_available
        if source_reason_needed:
            local_reasons.append("g2c_required_evidence_missing")
        if not _mode_action_allowed(mode, snapshot, router_input.g2a_binding):
            local_reasons.append("g2c_action_shortcut_forbidden")
        missing_codes: list[str] = []
        if source_reason_needed:
            missing_codes.append("g2c_required_evidence_missing")
        if (
            mode in _CAPABILITY_REQUIRED_MODES_V01
            and not capability_available
        ):
            missing_codes.append("g2c_capability_unavailable")
        if hard_block:
            local_reasons.append("g2c_hard_block_present")
        elif user_missing:
            local_reasons.append("g2c_user_input_required")
            missing_codes.append("g2c_required_evidence_missing")
        reasons = _public_reason_union(tuple(local_reasons))
        missing = _public_reason_union(tuple(missing_codes))
        required, satisfied = _row_evidence(
            mode=mode,
            router_input=router_input,
            profile=profile,
            capability_available=capability_available,
            mode_source_available=mode_source_available,
        )
        feasible = not reasons
        if feasible:
            reasons = (_MODE_POSITIVE_REASONS_V01[mode],)
            missing = ()
            satisfied = required
        provisional = ExecutionModeFeasibilityRowV01(
            feasibility_row_id="emrow_v01:" + _ZERO_SHA256,
            source_input_id=router_input.router_input_id,
            request_id=router_input.request_id,
            transaction_id=router_input.transaction_id,
            owning_root_id=router_input.owning_root_id,
            domain_id=snapshot.domain_id,
            mode=mode,
            category="EXECUTABLE",
            safe_depth_rank=rank_by_mode[mode],
            feasibility_status="FEASIBLE" if feasible else "INFEASIBLE",
            local_mode_profile_id=profile.local_mode_profile_id,
            required_evidence_refs=required,
            satisfied_evidence_refs=satisfied,
            missing_evidence_codes=missing,
            reason_codes=reasons,
            required_capability_id=(
                profile.capability_id
                if mode in _CAPABILITY_REQUIRED_MODES_V01
                else None
            ),
            cost_units=profile.cost_units,
            downstream_compute_class=_MODE_DOWNSTREAM_COMPUTE_CLASSES_V01[mode],
            root_review_required=True,
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )
        executable_rows.append(_finish_c3_row(provisional))
    any_feasible = any(
        row.feasibility_status == "FEASIBLE" for row in executable_rows
    )
    blocked_selected = hard_block or (
        not user_missing and not hard_block and not any_feasible
    )
    needs_user_selected = user_missing
    universal = (
        router_input.bsep_binding.bsep_binding_id,
        snapshot.local_routing_snapshot_id,
    )
    terminal_rows: list[ExecutionModeFeasibilityRowV01] = []
    for mode in _TERMINAL_MODES_V01:
        selected = (
            blocked_selected if mode == "blocked" else needs_user_selected
        )
        if not selected:
            reasons = ()
        elif mode == "needs_user":
            reasons = ("g2c_user_input_required",)
        elif hard_block:
            reasons = ("g2c_hard_block_present",)
        else:
            reasons = ("g2c_no_safe_mode",)
        terminal_rows.append(
            _finish_c3_row(
                ExecutionModeFeasibilityRowV01(
                    feasibility_row_id="emrow_v01:" + _ZERO_SHA256,
                    source_input_id=router_input.router_input_id,
                    request_id=router_input.request_id,
                    transaction_id=router_input.transaction_id,
                    owning_root_id=router_input.owning_root_id,
                    domain_id=snapshot.domain_id,
                    mode=mode,
                    category="TERMINAL",
                    safe_depth_rank=None,
                    feasibility_status=(
                        "TERMINAL_SELECTED"
                        if selected
                        else "TERMINAL_NOT_SELECTED"
                    ),
                    local_mode_profile_id=None,
                    required_evidence_refs=universal,
                    satisfied_evidence_refs=universal,
                    missing_evidence_codes=(),
                    reason_codes=reasons,
                    required_capability_id=None,
                    cost_units=None,
                    downstream_compute_class="TERMINAL",
                    root_review_required=True,
                    authority_created=False,
                    permission_created=False,
                    real_world_effects_count=0,
                )
            )
        )
    return (*executable_rows, *terminal_rows)


def _select_c3_row(
    rows: tuple[ExecutionModeFeasibilityRowV01, ...],
) -> ExecutionModeFeasibilityRowV01:
    selected_terminals = tuple(
        row for row in rows if row.feasibility_status == "TERMINAL_SELECTED"
    )
    if len(selected_terminals) == 1:
        return selected_terminals[0]
    if selected_terminals:
        raise _C3Failure("g2c_selection_invalid", "SELECTION")
    feasible = tuple(
        row
        for row in rows
        if row.category == "EXECUTABLE" and row.feasibility_status == "FEASIBLE"
    )
    if not feasible:
        raise _C3Failure("g2c_selection_invalid", "SELECTION")
    return min(
        feasible,
        key=lambda row: (
            row.safe_depth_rank,
            row.cost_units,
            _CANONICAL_MODE_INDEX_V01[row.mode],
        ),
    )


def _tie_break_applied(
    rows: tuple[ExecutionModeFeasibilityRowV01, ...],
) -> bool:
    feasible = tuple(row for row in rows if row.feasibility_status == "FEASIBLE")
    if not feasible:
        return False
    minimum_rank = min(row.safe_depth_rank for row in feasible)
    rank_rows = tuple(row for row in feasible if row.safe_depth_rank == minimum_rank)
    minimum_cost = min(row.cost_units for row in rank_rows)
    return sum(row.cost_units == minimum_cost for row in rank_rows) >= 2


def _build_c3_proposal(
    *,
    router_input: ExecutionModeRouterInputV01,
    rows: tuple[ExecutionModeFeasibilityRowV01, ...],
    selected: ExecutionModeFeasibilityRowV01,
) -> ExecutionModeProposalV01:
    mode = selected.mode
    tie_break = selected.category == "EXECUTABLE" and _tie_break_applied(rows)
    reason_codes = (
        (
            "g2c_selection_tie_break_applied",
            "g2c_proposal_sources_valid",
        )
        if tie_break
        else ("g2c_proposal_sources_valid",)
    )
    capabilities = (
        (selected.required_capability_id,)
        if mode in _CAPABILITY_REQUIRED_MODES_V01
        else ()
    )
    snapshot = router_input.local_routing_snapshot
    provisional = ExecutionModeProposalV01(
        proposal_id="emproposal_v01:" + _ZERO_SHA256,
        source_input_id=router_input.router_input_id,
        request_id=router_input.request_id,
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        domain_id=snapshot.domain_id,
        source_bsep_binding_id=router_input.bsep_binding.bsep_binding_id,
        source_bsep_packet_id=router_input.bsep_binding.source_packet_id,
        source_bsep_sha256=router_input.bsep_binding.source_packet_sha256,
        source_local_routing_snapshot_id=snapshot.local_routing_snapshot_id,
        source_replay_binding_id=router_input.replay_binding.replay_binding_id,
        source_g2a_binding_id=router_input.g2a_binding.g2a_binding_id,
        source_g2b_binding_id=router_input.g2b_binding.g2b_binding_id,
        selected_mode=mode,
        selected_safe_depth_rank=selected.safe_depth_rank,
        selected_local_mode_profile_id=selected.local_mode_profile_id,
        selected_expected_cost_units=selected.cost_units,
        proposed_scope_ref=(snapshot.scope_ref if selected.category == "EXECUTABLE" else None),
        ordered_feasibility_rows=rows,
        selected_feasibility_row_id=selected.feasibility_row_id,
        reason_codes=reason_codes,
        required_downstream_capability_ids=capabilities,
        downstream_consumption_class=_MODE_DOWNSTREAM_CONSUMPTION_CLASSES_V01[mode],
        downstream_action_packet_required=(
            selected.category == "EXECUTABLE"
            and snapshot.action_class == "ACTION"
            and snapshot.action_packet_relation == "NEW_ACTION_NO_PACKET"
        ),
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        topology_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    proposal = replace(provisional, proposal_id=_rebuild_identity(provisional))
    errors = _proposal_errors(proposal)
    if errors:
        raise _C3Failure(errors[0], "PROPOSAL")
    return proposal


def _proposal_context_report(
    *,
    proposal: object,
    router_input: object,
    status: str,
    stage: str,
    reasons: tuple[str, ...],
    source_reasons: tuple[str, ...] = (),
) -> ExecutionModeValidationReportV01:
    artifact_id: str | None = None
    request_id: str | None = None
    transaction_id: str | None = None
    owning_root_id: str | None = None
    domain_id: str | None = None
    if (
        type(router_input) is ExecutionModeRouterInputV01
        and type(router_input.local_routing_snapshot)
        is ExecutionModeLocalRoutingSnapshotV01
    ):
        candidate = (
            router_input.request_id,
            router_input.transaction_id,
            router_input.owning_root_id,
            router_input.local_routing_snapshot.domain_id,
        )
        if all(_project_ref_valid(item) for item in candidate):
            request_id, transaction_id, owning_root_id, domain_id = candidate
    if type(proposal) is ExecutionModeProposalV01 and _source_identity_valid(
        proposal.proposal_id
    ):
        artifact_id = proposal.proposal_id
    return build_execution_mode_validation_report_v01(
        validation_target="PROPOSAL_AGAINST_SOURCES",
        validated_artifact_id=artifact_id,
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        validation_status=status,
        failure_stage=stage,
        return_to_root_required=status != "PASS",
        reason_codes=reasons,
        source_reason_codes=_dedupe(source_reasons),
    )


def _proposal_c3_failure_report(
    *,
    proposal: object,
    router_input: object,
    failure: _C3Failure,
) -> ExecutionModeValidationReportV01:
    return _proposal_context_report(
        proposal=proposal,
        router_input=router_input,
        status="FAIL_CLOSED",
        stage=failure.stage,
        reasons=(failure.reason,),
        source_reasons=failure.source_reasons,
    )


def _proposal_rows_have_invalid_geometry(
    proposal: ExecutionModeProposalV01,
) -> bool:
    rows = proposal.ordered_feasibility_rows
    return (
        type(rows) is not tuple
        or len(rows) != CANONICAL_MODE_COUNT
        or tuple(type(row) for row in rows)
        != (ExecutionModeFeasibilityRowV01,) * CANONICAL_MODE_COUNT
        or tuple(row.mode for row in rows) != CANONICAL_EXECUTION_MODES_V01
        or any(_feasibility_row_errors(row) for row in rows)
    )


def _proposal_source_fields_differ(
    proposal: ExecutionModeProposalV01,
    expected: ExecutionModeProposalV01,
) -> bool:
    return any(
        getattr(proposal, field_name) != getattr(expected, field_name)
        for field_name in _PROPOSAL_SOURCE_FIELDS_V01
    )


def _route_c3_failure_report(
    *,
    router_input: object,
    stage: str,
    reason: str,
    source_reasons: tuple[str, ...] = (),
) -> ExecutionModeValidationReportV01:
    return _proposal_context_report(
        proposal=None,
        router_input=router_input,
        status="FAIL_CLOSED",
        stage=stage,
        reasons=_public_reason_union(
            (reason,),
            ("g2c_fail_closed_return_to_root",),
        ),
        source_reasons=source_reasons,
    )


def evaluate_execution_mode_feasibility_v01(
    *,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
) -> tuple[ExecutionModeFeasibilityRowV01, ...]:
    try:
        _require_c3_context(router_input, source_context)
        return _build_feasibility_rows(router_input)
    except _C3Failure as exc:
        raise ValueError(exc.reason) from None
    except Exception:
        raise ValueError("g2c_feasibility_row_invalid") from None


def select_execution_mode_v01(
    *,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    ordered_rows: tuple[ExecutionModeFeasibilityRowV01, ...],
) -> ExecutionModeFeasibilityRowV01:
    try:
        _require_c3_context(router_input, source_context)
        expected = _build_feasibility_rows(router_input)
        if type(ordered_rows) is not tuple or ordered_rows != expected:
            raise _C3Failure("g2c_selection_invalid", "SELECTION")
        return _select_c3_row(expected)
    except _C3Failure as exc:
        raise ValueError(exc.reason) from None
    except Exception:
        raise ValueError("g2c_selection_invalid") from None


def build_execution_mode_proposal_v01(
    *,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    ordered_rows: tuple[ExecutionModeFeasibilityRowV01, ...],
    selected_row: ExecutionModeFeasibilityRowV01,
) -> ExecutionModeProposalV01:
    try:
        _require_c3_context(router_input, source_context)
        expected_rows = _build_feasibility_rows(router_input)
        if type(ordered_rows) is not tuple or ordered_rows != expected_rows:
            raise _C3Failure("g2c_proposal_rows_invalid", "FEASIBILITY")
        expected_selected = _select_c3_row(expected_rows)
        if selected_row != expected_selected:
            raise _C3Failure("g2c_proposal_selected_row_mismatch", "SELECTION")
        return _build_c3_proposal(
            router_input=router_input,
            rows=expected_rows,
            selected=expected_selected,
        )
    except _C3Failure as exc:
        raise ValueError(exc.reason) from None
    except Exception:
        raise ValueError("g2c_proposal_rows_invalid") from None


def validate_execution_mode_proposal_against_sources_v01(
    *,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
) -> ExecutionModeValidationReportV01:
    try:
        input_report = validate_execution_mode_router_input_against_sources_v01(
            router_input=router_input,
            source_context=source_context,
        )
        if input_report.validation_status != "PASS":
            return _proposal_context_report(
                proposal=proposal,
                router_input=router_input,
                status="FAIL_CLOSED",
                stage=input_report.failure_stage,
                reasons=input_report.reason_codes,
                source_reasons=input_report.source_reason_codes,
            )
    except Exception:
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="STRUCTURAL",
            reasons=("g2c_source_validator_failed",),
        )

    if type(proposal) is not ExecutionModeProposalV01:
        structural = validate_execution_mode_proposal_v01(proposal)
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="PROPOSAL",
            reasons=structural.reason_codes,
        )

    try:
        expected_rows = _build_feasibility_rows(router_input)
    except _C3Failure as exc:
        return _proposal_c3_failure_report(
            proposal=proposal,
            router_input=router_input,
            failure=exc,
        )
    except Exception:
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="FEASIBILITY",
            reasons=("g2c_proposal_rows_invalid",),
        )

    if _proposal_rows_have_invalid_geometry(proposal):
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="FEASIBILITY",
            reasons=("g2c_proposal_rows_invalid",),
        )

    try:
        selected = _select_c3_row(expected_rows)
    except _C3Failure as exc:
        return _proposal_c3_failure_report(
            proposal=proposal,
            router_input=router_input,
            failure=exc,
        )
    except Exception:
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="SELECTION",
            reasons=("g2c_proposal_selected_row_mismatch",),
        )

    if proposal.ordered_feasibility_rows != expected_rows:
        differing_indexes = tuple(
            index
            for index, (supplied_row, expected_row) in enumerate(
                zip(proposal.ordered_feasibility_rows, expected_rows)
            )
            if supplied_row != expected_row
        )
        selected_index = next(
            index
            for index, row in enumerate(expected_rows)
            if row.feasibility_row_id == selected.feasibility_row_id
        )
        selected_row_substituted = differing_indexes == (selected_index,)
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage=("SELECTION" if selected_row_substituted else "FEASIBILITY"),
            reasons=(
                (
                    "g2c_proposal_selected_row_mismatch"
                    if selected_row_substituted
                    else "g2c_proposal_rows_invalid"
                ),
            ),
        )

    if any(
        getattr(proposal, field_name) != getattr(selected, selected_field_name)
        for field_name, selected_field_name in (
            ("selected_mode", "mode"),
            ("selected_safe_depth_rank", "safe_depth_rank"),
            ("selected_local_mode_profile_id", "local_mode_profile_id"),
            ("selected_expected_cost_units", "cost_units"),
            ("selected_feasibility_row_id", "feasibility_row_id"),
        )
    ):
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="SELECTION",
            reasons=("g2c_proposal_selected_row_mismatch",),
        )

    try:
        expected = _build_c3_proposal(
            router_input=router_input,
            rows=expected_rows,
            selected=selected,
        )
    except _C3Failure as exc:
        return _proposal_c3_failure_report(
            proposal=proposal,
            router_input=router_input,
            failure=exc,
        )
    except Exception:
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="PROPOSAL",
            reasons=("g2c_proposal_rows_invalid",),
        )

    try:
        structural = validate_execution_mode_proposal_v01(proposal)
    except Exception:
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="PROPOSAL",
            reasons=("g2c_proposal_rows_invalid",),
        )
    if structural.validation_status != "PASS":
        reasons = structural.reason_codes
        if _proposal_source_fields_differ(proposal, expected):
            reasons = _public_reason_union(
                reasons,
                ("g2c_source_object_substituted",),
            )
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="PROPOSAL",
            reasons=reasons,
        )

    if proposal != expected:
        reason = (
            "g2c_source_object_substituted"
            if _proposal_source_fields_differ(proposal, expected)
            else "g2c_proposal_rows_invalid"
        )
        return _proposal_context_report(
            proposal=proposal,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="PROPOSAL",
            reasons=(reason,),
        )
    return _proposal_context_report(
        proposal=proposal,
        router_input=router_input,
        status="PASS",
        stage="NONE",
        reasons=(),
    )


def route_execution_mode_v01(
    *,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
) -> tuple[
    ExecutionModeProposalV01 | None,
    ExecutionModeValidationReportV01,
]:
    try:
        input_report = validate_execution_mode_router_input_against_sources_v01(
            router_input=router_input,
            source_context=source_context,
        )
        if input_report.validation_status != "PASS":
            reasons = _public_reason_union(
                input_report.reason_codes,
                (
                    "g2c_invalid_source_no_proposal",
                    "g2c_fail_closed_return_to_root",
                ),
            )
            return None, _proposal_context_report(
                proposal=None,
                router_input=router_input,
                status="FAIL_CLOSED",
                stage=input_report.failure_stage,
                reasons=reasons,
                source_reasons=input_report.source_reason_codes,
            )
    except _C3Failure as exc:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage=exc.stage,
            reason=exc.reason,
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return None, _proposal_context_report(
            proposal=None,
            router_input=router_input,
            status="FAIL_CLOSED",
            stage="STRUCTURAL",
            reasons=_public_reason_union(
                ("g2c_source_validator_failed",),
                (
                    "g2c_invalid_source_no_proposal",
                    "g2c_fail_closed_return_to_root",
                ),
            ),
        )

    try:
        rows = _build_feasibility_rows(router_input)
    except _C3Failure as exc:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage=exc.stage,
            reason=exc.reason,
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage="FEASIBILITY",
            reason="g2c_feasibility_row_invalid",
        )

    try:
        selected = _select_c3_row(rows)
    except _C3Failure as exc:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage=exc.stage,
            reason=exc.reason,
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage="SELECTION",
            reason="g2c_selection_invalid",
        )

    try:
        proposal = _build_c3_proposal(
            router_input=router_input,
            rows=rows,
            selected=selected,
        )
    except _C3Failure as exc:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage=exc.stage,
            reason=exc.reason,
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage="PROPOSAL",
            reason="g2c_proposal_rows_invalid",
        )

    try:
        report = validate_execution_mode_proposal_against_sources_v01(
            proposal=proposal,
            router_input=router_input,
            source_context=source_context,
        )
        if report.validation_status != "PASS":
            return None, _proposal_context_report(
                proposal=None,
                router_input=router_input,
                status="FAIL_CLOSED",
                stage=report.failure_stage,
                reasons=_public_reason_union(
                    report.reason_codes,
                    ("g2c_fail_closed_return_to_root",),
                ),
                source_reasons=report.source_reason_codes,
            )
        return proposal, report
    except _C3Failure as exc:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage=exc.stage,
            reason=exc.reason,
            source_reasons=exc.source_reasons,
        )
    except Exception:
        return None, _route_c3_failure_report(
            router_input=router_input,
            stage="PROPOSAL",
            reason="g2c_proposal_rows_invalid",
        )


def _c4_identity(*, domain: str, prefix: str, material: object) -> str:
    return prefix + domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(material),
    )


def _lexical_refs(*values: str) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _c4_report(
    *, target: str, artifact_id: str | None, router_input: object,
    status: str, stage: str, reasons: tuple[str, ...] = (),
    source_reasons: tuple[str, ...] = (),
) -> ExecutionModeValidationReportV01:
    recognized = type(router_input) is ExecutionModeRouterInputV01
    return build_execution_mode_validation_report_v01(
        validation_target=target,
        validated_artifact_id=artifact_id if recognized else None,
        request_id=router_input.request_id if recognized else None,
        transaction_id=router_input.transaction_id if recognized else None,
        owning_root_id=router_input.owning_root_id if recognized else None,
        domain_id=(router_input.local_routing_snapshot.domain_id if recognized else None),
        validation_status=status,
        failure_stage=stage,
        return_to_root_required=status != "PASS",
        reason_codes=_sort_public_reasons(reasons) if reasons else (),
        source_reason_codes=source_reasons,
    )


def _require_c4_proposal(
    *, proposal: object, router_input: object, source_context: object,
) -> None:
    report = validate_execution_mode_proposal_against_sources_v01(
        proposal=proposal, router_input=router_input, source_context=source_context
    )
    if report.validation_status != "PASS":
        raise ValueError(
            report.reason_codes[0]
            if report.reason_codes else "g2c_source_object_substituted"
        )


def _payload_has_reserved_key(value: object, active: set[int]) -> bool:
    if type(value) not in {dict, list, tuple}:
        return False
    marker = id(value)
    if marker in active:
        return True
    active.add(marker)
    try:
        if type(value) is dict:
            if any(
                type(key) is not str or key in _G2C_ABI_RESERVED_KEYS_V01
                for key in value
            ):
                return True
            return any(
                _payload_has_reserved_key(item, active) for item in value.values()
            )
        return any(_payload_has_reserved_key(item, active) for item in value)
    finally:
        active.remove(marker)


def _artifact_identity(
    artifact: KernelArtifactV01, *, domain: str, prefix: str,
) -> str:
    material = kernel_artifact_to_plain_dict_v01(artifact)
    material.pop("artifact_id")
    return _c4_identity(domain=domain, prefix=prefix, material=material)


def _finish_c4_artifact(
    *, artifact_type: str, transaction_id: str, owning_root_id: str,
    source_component: str, authority_class: str, lifecycle_state: str,
    payload: dict[str, object], trace_refs: tuple[str, ...],
    parent_refs: tuple[str, ...], snapshot: ExecutionModeLocalRoutingSnapshotV01,
    domain: str, prefix: str,
) -> KernelArtifactV01:
    if _payload_has_reserved_key(payload, set()):
        raise ValueError("g2c_abi_reserved_payload_key")
    provisional = build_kernel_artifact_v01(
        abi_version=_G2C_ABI_VERSION_V01,
        artifact_id=prefix + _ZERO_SHA256,
        artifact_type=artifact_type,
        schema_version=_G2C_SCHEMA_VERSION_V01,
        transaction_id=transaction_id,
        owner_root_id=owning_root_id,
        source_component=source_component,
        authority_class=authority_class,
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=_time_envelope_plain(snapshot),
    )
    artifact = replace(
        provisional,
        artifact_id=_artifact_identity(provisional, domain=domain, prefix=prefix),
    )
    if validate_kernel_artifact_v01(artifact):
        raise ValueError("g2c_abi_profile_invalid")
    return artifact


def _proposal_payload(proposal: ExecutionModeProposalV01) -> dict[str, object]:
    return {
        "proposal_id": proposal.proposal_id,
        "source_input_id": proposal.source_input_id,
        "request_id": proposal.request_id,
        "domain_id": proposal.domain_id,
        "source_bsep_binding_id": proposal.source_bsep_binding_id,
        "source_bsep_packet_id": proposal.source_bsep_packet_id,
        "source_bsep_sha256": proposal.source_bsep_sha256,
        "source_local_routing_snapshot_id": proposal.source_local_routing_snapshot_id,
        "source_replay_binding_id": proposal.source_replay_binding_id,
        "source_g2a_binding_id": proposal.source_g2a_binding_id,
        "source_g2b_binding_id": proposal.source_g2b_binding_id,
        "selected_mode": proposal.selected_mode,
        "selected_safe_depth_rank": proposal.selected_safe_depth_rank,
        "selected_local_mode_profile_id": proposal.selected_local_mode_profile_id,
        "selected_expected_cost_units": proposal.selected_expected_cost_units,
        "proposed_scope_ref": proposal.proposed_scope_ref,
        "ordered_feasibility_row_ids": [
            row.feasibility_row_id for row in proposal.ordered_feasibility_rows
        ],
        "selected_feasibility_row_id": proposal.selected_feasibility_row_id,
        "reason_codes": list(proposal.reason_codes),
        "required_downstream_capability_ids": list(proposal.required_downstream_capability_ids),
        "downstream_consumption_class": proposal.downstream_consumption_class,
        "downstream_action_packet_required": proposal.downstream_action_packet_required,
        "root_review_required": proposal.root_review_required,
        "authority_created": proposal.authority_created,
        "permission_created": proposal.permission_created,
        "action_commit_packet_created": proposal.action_commit_packet_created,
        "receipt_created": proposal.receipt_created,
        "topology_created": proposal.topology_created,
        "final_output_created": proposal.final_output_created,
        "drs_write_created": proposal.drs_write_created,
        "real_world_effects_count": proposal.real_world_effects_count,
    }


def _expected_proposal_artifact(
    *, proposal: ExecutionModeProposalV01, router_input: ExecutionModeRouterInputV01,
) -> KernelArtifactV01:
    return _finish_c4_artifact(
        artifact_type="ExecutionModeProposal",
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        source_component="execution_mode_router_v01",
        authority_class="ADVISORY",
        lifecycle_state="VALIDATED",
        payload=_proposal_payload(proposal),
        trace_refs=_lexical_refs(
            router_input.bsep_binding.business_request_packet_id,
            router_input.bsep_binding.bsep_binding_id,
            router_input.router_input_id,
            router_input.local_routing_snapshot.local_routing_snapshot_id,
            router_input.replay_binding.replay_binding_id,
            router_input.g2a_binding.g2a_binding_id,
            router_input.g2b_binding.g2b_binding_id,
            proposal.proposal_id,
        ),
        parent_refs=(),
        snapshot=router_input.local_routing_snapshot,
        domain=_G2C_PROPOSAL_ARTIFACT_DOMAIN_V01,
        prefix="emabi_proposal_v01:",
    )


def _require_proposal_artifact(
    *, proposal_artifact: object, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
) -> None:
    if type(proposal_artifact) is not KernelArtifactV01:
        raise ValueError("g2c_abi_profile_invalid")
    if proposal_artifact != _expected_proposal_artifact(
        proposal=proposal, router_input=router_input
    ):
        raise ValueError("g2c_abi_projection_substituted")
    if validate_kernel_artifact_bundle_v01(artifacts=(proposal_artifact,)):
        raise ValueError("g2c_abi_bundle_validation_failed")


def project_execution_mode_proposal_kernel_artifact_v01(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
) -> KernelArtifactV01:
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        artifact = _expected_proposal_artifact(
            proposal=proposal, router_input=router_input
        )
        _require_proposal_artifact(
            proposal_artifact=artifact, proposal=proposal, router_input=router_input
        )
        return artifact
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_abi_profile_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_abi_profile_invalid") from None


def _build_profile_transition(
    *, registry: TransitionRegistryV01, rule_id: str,
) -> TransitionDecisionV01:
    errors = _validate_execution_mode_transition_registry_profile_v01(registry)
    if errors:
        raise ValueError(errors[0])
    rule = next((item for item in registry.rules if item.rule_id == rule_id), None)
    if rule is None:
        raise ValueError("g2c_transition_decision_invalid")
    provisional = TransitionDecisionV01(
        decision_id=_ZERO_SHA256,
        registry_id=registry.registry_id,
        rule_id=rule.rule_id,
        abi_major_version=rule.abi_major_version,
        source_artifact_type=rule.source_artifact_type,
        source_lifecycle_state=rule.source_lifecycle_state,
        actor_role=rule.actor_role,
        attempted_effect=rule.attempted_effect,
        target_artifact_type=rule.target_artifact_type,
        required_guards=rule.required_guards,
        satisfied_guards=rule.required_guards,
        missing_guards=(),
        decision=rule.decision,
        reason_code=rule.reason_code,
        root_commit_required=rule.root_commit_required,
        root_commit_present=rule.root_commit_required,
        matched=True,
    )
    decision = replace(
        provisional,
        decision_id=_rebuild_execution_mode_transition_decision_identity_v01(provisional),
    )
    if _validate_execution_mode_transition_decision_v01(
        registry=registry, decision=decision
    ):
        raise ValueError("g2c_transition_decision_invalid")
    return decision


def _require_pre_root_transition(
    *, transition: object, registry: TransitionRegistryV01,
) -> None:
    if type(transition) is not TransitionDecisionV01:
        raise ValueError("g2c_proposal_transition_missing")
    if transition != _build_profile_transition(
        registry=registry,
        rule_id="g2c_transition:proposal_to_root_review:v01",
    ):
        raise ValueError("g2c_proposal_transition_substituted")


def evaluate_execution_mode_proposal_to_root_transition_v01(
    *, registry: TransitionRegistryV01, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
) -> TransitionDecisionV01:
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        _require_proposal_artifact(
            proposal_artifact=proposal_artifact, proposal=proposal,
            router_input=router_input,
        )
        decision = _build_profile_transition(
            registry=registry,
            rule_id="g2c_transition:proposal_to_root_review:v01",
        )
        _require_pre_root_transition(transition=decision, registry=registry)
        return decision
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_transition_substituted"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_transition_substituted") from None


def _root_support_material(
    *, kind: str, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    specific: tuple[tuple[str, object], ...],
) -> dict[str, object]:
    material: dict[str, object] = {
        "kind": kind,
        "request_id": router_input.request_id,
        "transaction_id": router_input.transaction_id,
        "owning_root_id": router_input.owning_root_id,
        "domain_id": router_input.local_routing_snapshot.domain_id,
        "proposal_id": proposal.proposal_id,
        "router_input_id": router_input.router_input_id,
        "proposal_artifact_id": proposal_artifact.artifact_id,
        "proposal_transition_decision_id": proposal_transition_decision.decision_id,
    }
    material.update(specific)
    return material


def _root_support_identity(
    *, kind: str, prefix: str, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    specific: tuple[tuple[str, object], ...],
) -> str:
    return _c4_identity(
        domain=_G2C_ROOT_SOURCE_SUPPORT_DOMAIN_V01,
        prefix=prefix,
        material=_root_support_material(
            kind=kind, proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            specific=specific,
        ),
    )


def _scope_narrowing_identity(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    accepted_scope_ref: str,
    narrowing_basis_refs: tuple[str, ...],
) -> str:
    snapshot = router_input.local_routing_snapshot
    return _c4_identity(
        domain="HEDGEHOG_EXECUTION_MODE_SCOPE_NARROWING_V01",
        prefix="emnarrow_v01:",
        material={
            "request_id": router_input.request_id,
            "transaction_id": router_input.transaction_id,
            "owning_root_id": router_input.owning_root_id,
            "proposal_id": proposal.proposal_id,
            "proposed_scope_ref": proposal.proposed_scope_ref,
            "accepted_scope_ref": accepted_scope_ref,
            "policy_snapshot_id": snapshot.policy_snapshot_id,
            "evaluation_time_epoch_seconds": snapshot.evaluation_time_epoch_seconds,
            "narrowing_basis_refs": list(narrowing_basis_refs),
        },
    )


def _review_geometry(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    review_action: str,
    accepted_scope_ref: str | None,
    narrowing_basis_refs: tuple[str, ...],
) -> tuple[str | None, tuple[str, ...]]:
    if (
        type(narrowing_basis_refs) is not tuple
        or tuple(sorted(narrowing_basis_refs)) != narrowing_basis_refs
        or len(narrowing_basis_refs) != len(set(narrowing_basis_refs))
        or any(not _source_identity_valid(item) for item in narrowing_basis_refs)
    ):
        raise ValueError("g2c_scope_narrowing_invalid")
    executable = proposal.selected_mode in EXECUTABLE_EXECUTION_MODES_V01
    if executable and review_action == "ACCEPT":
        if accepted_scope_ref != proposal.proposed_scope_ref or narrowing_basis_refs:
            raise ValueError("g2c_review_action_invalid")
        return None, ()
    if executable and review_action == "NARROW":
        permitted = router_input.local_routing_snapshot.permitted_narrower_scope_refs
        if (
            accepted_scope_ref is None
            or accepted_scope_ref == proposal.proposed_scope_ref
            or permitted.count(accepted_scope_ref) != 1
            or not narrowing_basis_refs
        ):
            raise ValueError("g2c_scope_narrowing_invalid")
        return _scope_narrowing_identity(
            proposal=proposal, router_input=router_input,
            accepted_scope_ref=accepted_scope_ref,
            narrowing_basis_refs=narrowing_basis_refs,
        ), narrowing_basis_refs
    if executable and review_action == "REJECT":
        if accepted_scope_ref is not None or narrowing_basis_refs:
            raise ValueError("g2c_review_action_invalid")
        return None, ()
    if (
        not executable
        and review_action == "TERMINAL_FROM_PROPOSAL"
        and proposal.selected_mode in _TERMINAL_MODES_V01
        and accepted_scope_ref is None
        and not narrowing_basis_refs
    ):
        return None, ()
    raise ValueError(
        "g2c_review_action_invalid" if executable else "g2c_terminal_review_mismatch"
    )


def _build_review_input(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    review_action: str,
    accepted_scope_ref: str | None,
    narrowing_basis_refs: tuple[str, ...],
) -> RootExecutionModeReviewInputV01:
    proof_id, exact_basis = _review_geometry(
        proposal=proposal, router_input=router_input, review_action=review_action,
        accepted_scope_ref=accepted_scope_ref,
        narrowing_basis_refs=narrowing_basis_refs,
    )
    snapshot = router_input.local_routing_snapshot
    context_id = _root_support_identity(
        kind="ROOT_LOCAL_CONTEXT", prefix="emrootctx_v01:",
        proposal=proposal, router_input=router_input,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
        specific=(
            ("policy_snapshot_id", snapshot.policy_snapshot_id),
            ("time_envelope_ref", snapshot.time_envelope_ref),
            ("proposed_scope_ref", proposal.proposed_scope_ref),
            ("accepted_scope_ref", accepted_scope_ref),
            ("scope_narrowing_proof_id", proof_id),
            ("narrowing_basis_refs", list(exact_basis)),
        ),
    )
    provisional = RootExecutionModeReviewInputV01(
        root_review_input_id="emrootreview_v01:" + _ZERO_SHA256,
        request_id=router_input.request_id,
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        domain_id=snapshot.domain_id,
        proposal_id=proposal.proposal_id,
        router_input_id=router_input.router_input_id,
        proposal_artifact_id=proposal_artifact.artifact_id,
        proposal_transition_decision_id=proposal_transition_decision.decision_id,
        created_by="OWNING_LOCAL_ROOT_EXECUTION_MODE_REVIEW_V01",
        review_action=review_action,
        proposed_mode=proposal.selected_mode,
        proposed_scope_ref=proposal.proposed_scope_ref,
        accepted_scope_ref=accepted_scope_ref,
        scope_narrowing_proof_id=proof_id,
        narrowing_basis_refs=exact_basis,
        policy_snapshot_id=snapshot.policy_snapshot_id,
        evaluation_time_epoch_seconds=snapshot.evaluation_time_epoch_seconds,
        time_envelope_ref=snapshot.time_envelope_ref,
        root_local_context_id=context_id,
        trace_refs=_lexical_refs(
            proposal_artifact.artifact_id,
            proposal_transition_decision.decision_id,
            proposal.proposal_id,
            router_input.router_input_id,
            context_id,
        ),
    )
    result = replace(provisional, root_review_input_id=_rebuild_identity(provisional))
    errors = _root_review_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def build_root_execution_mode_review_input_v01(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    review_action: str,
    accepted_scope_ref: str | None,
    narrowing_basis_refs: tuple[str, ...],
) -> RootExecutionModeReviewInputV01:
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        _require_proposal_artifact(
            proposal_artifact=proposal_artifact, proposal=proposal,
            router_input=router_input,
        )
        _require_pre_root_transition(
            transition=proposal_transition_decision,
            registry=_build_execution_mode_transition_registry_profile_v01(),
        )
        result = _build_review_input(
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            review_action=review_action, accepted_scope_ref=accepted_scope_ref,
            narrowing_basis_refs=narrowing_basis_refs,
        )
        report = validate_root_execution_mode_review_input_against_sources_v01(
            review_input=result, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
        )
        if report.validation_status != "PASS":
            raise ValueError(report.reason_codes[0])
        return result
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_review_action_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_review_action_invalid") from None


def validate_root_execution_mode_review_input_against_sources_v01(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
) -> ExecutionModeValidationReportV01:
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        _require_proposal_artifact(
            proposal_artifact=proposal_artifact, proposal=proposal,
            router_input=router_input,
        )
        _require_pre_root_transition(
            transition=proposal_transition_decision,
            registry=_build_execution_mode_transition_registry_profile_v01(),
        )
        structural = validate_root_execution_mode_review_input_v01(review_input)
        if structural.validation_status != "PASS":
            return _c4_report(
                target="ROOT_REVIEW_AGAINST_SOURCES", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED", stage="ROOT_REVIEW",
                reasons=structural.reason_codes,
            )
        expected = _build_review_input(
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            review_action=review_input.review_action,
            accepted_scope_ref=review_input.accepted_scope_ref,
            narrowing_basis_refs=review_input.narrowing_basis_refs,
        )
        if review_input != expected:
            raise ValueError("g2c_source_object_substituted")
        return _c4_report(
            target="ROOT_REVIEW_AGAINST_SOURCES",
            artifact_id=review_input.root_review_input_id,
            router_input=router_input, status="PASS", stage="NONE",
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_source_object_substituted"
        return _c4_report(
            target="ROOT_REVIEW_AGAINST_SOURCES", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage="ROOT_REVIEW",
            reasons=(reason,),
        )
    except Exception:
        return _c4_report(
            target="ROOT_REVIEW_AGAINST_SOURCES", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage="ROOT_REVIEW",
            reasons=("g2c_review_action_invalid",),
        )


def _root_source_family(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
) -> tuple[
    SemanticWorkRequestV01, NormalizedClaimV01, ActorContributionV01,
    RootReviewPacketV01, RootDecisionInputV01, RootDecisionResultV01,
]:
    if root_kernel != build_root_decision_kernel_v01() or validate_root_decision_kernel_v01(
        root_kernel
    ):
        raise ValueError("g2c_root_input_invalid")
    snapshot = router_input.local_routing_snapshot
    common = dict(
        proposal=proposal,
        router_input=router_input,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
    )
    bsep_evidence_id = _root_support_identity(
        kind="BSEP_EVIDENCE", prefix="emrootev_v01:",
        specific=(
            ("bsep_binding_id", router_input.bsep_binding.bsep_binding_id),
            ("source_family_sha256", router_input.bsep_binding.source_family_sha256),
        ),
        **common,
    )
    feasibility_evidence_id = _root_support_identity(
        kind="FEASIBILITY_EVIDENCE", prefix="emrootev_v01:",
        specific=(
            ("selected_feasibility_row_id", proposal.selected_feasibility_row_id),
            ("selected_mode", proposal.selected_mode),
            ("ordered_feasibility_row_ids", [
                row.feasibility_row_id for row in proposal.ordered_feasibility_rows
            ]),
        ),
        **common,
    )
    evidence_ids = (bsep_evidence_id, feasibility_evidence_id)
    request = build_semantic_work_request_v01(
        request_id=router_input.request_id,
        transaction_id=router_input.transaction_id,
        target_root_id=router_input.owning_root_id,
        runtime_topology_ref="g2c:runtime_topology:not_created_before_root_review:v01",
        bounded_context_refs=(
            router_input.bsep_binding.business_request_packet_id,
            router_input.bsep_binding.bsep_binding_id,
            router_input.router_input_id,
            proposal.proposal_id,
        ),
        permitted_actor_ids=("execution_mode_router_v01",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=("execution_mode_route",),
        required_evidence_classes=("BSEP", "EXECUTION_MODE_FEASIBILITY"),
        forbidden_claims=("AUTHORITY", "PERMISSION", "EFFECT", "TOPOLOGY", "FINAL_OUTPUT"),
    )
    bindings = (
        build_evidence_binding_v01(
            evidence_id=bsep_evidence_id,
            evidence_ref=router_input.bsep_binding.bsep_binding_id,
            evidence_class="BSEP",
            source_component_id="execution_mode_router_v01",
            provenance_ref=router_input.bsep_binding.source_family_sha256,
            evidence_state="PRESENT",
        ),
        build_evidence_binding_v01(
            evidence_id=feasibility_evidence_id,
            evidence_ref=proposal.selected_feasibility_row_id,
            evidence_class="EXECUTION_MODE_FEASIBILITY",
            source_component_id="execution_mode_router_v01",
            provenance_ref=proposal.proposal_id,
            evidence_state="PRESENT",
        ),
    )
    claim = build_normalized_claim_v01(
        claim_id=proposal.proposal_id,
        subject="execution_mode_route",
        predicate="selected_mode",
        object_or_value=proposal.selected_mode,
        time_envelope_ref=snapshot.time_envelope_ref,
        provenance_refs=(router_input.bsep_binding.bsep_binding_id, router_input.router_input_id),
        evidence_refs=evidence_ids,
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution_scope = proposal.proposed_scope_ref or snapshot.scope_ref
    contribution_id = _root_support_identity(
        kind="ACTOR_CONTRIBUTION", prefix="emrootcontrib_v01:",
        specific=(
            ("bsep_evidence_id", bsep_evidence_id),
            ("feasibility_evidence_id", feasibility_evidence_id),
            ("contribution_scope", contribution_scope),
            ("selected_mode", proposal.selected_mode),
        ),
        **common,
    )
    contribution = build_actor_contribution_v01(
        contribution_id=contribution_id,
        request_id=router_input.request_id,
        actor_id="execution_mode_router_v01",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=router_input.bsep_binding.bsep_binding_id,
        scope=contribution_scope,
        bounded_context_refs=request.bounded_context_refs,
        claims=(claim,),
        evidence_bindings=bindings,
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("execution_mode_proposal_sources_v01",),
        forbidden_claims_observed=(),
    )
    trust_profiles = build_default_component_trust_profiles_v01()
    if validate_component_trust_profiles_v01(profiles=trust_profiles):
        raise ValueError("g2c_root_input_invalid")
    if validate_semantic_work_request_v01(request) or validate_actor_contribution_v01(
        request=request, contribution=contribution, trust_profiles=trust_profiles
    ):
        raise ValueError("g2c_root_input_invalid")
    packet = build_root_review_packet_from_contributions_v01(
        request=request, contributions=(contribution,), trust_profiles=trust_profiles
    )
    if validate_root_review_packet_v01(
        request=request, contributions=(contribution,), packet=packet,
        trust_profiles=trust_profiles,
    ) or packet.conflict_set_ids != () or packet.missing_evidence_refs != ():
        raise ValueError("g2c_root_input_invalid")

    post_id = _root_support_identity(
        kind="POST_VV_BUNDLE", prefix="emrootpostvv_v01:",
        specific=(
            ("bsep_evidence_id", bsep_evidence_id),
            ("feasibility_evidence_id", feasibility_evidence_id),
            ("contribution_id", contribution_id),
            ("review_action", review_input.review_action),
            ("validated_candidate_ids", [proposal.proposal_id]),
            ("rejected_candidate_ids", []),
        ),
        **common,
    )
    gt_transition = (
        "GTAdvisoryReport", "VALIDATED", "gt", "CREATE_ROOT_DECISION",
        "RootDecision",
    )
    gt_id = _root_support_identity(
        kind="GT_ADVISORY", prefix="emrootgt_v01:",
        specific=(
            ("contribution_id", contribution_id),
            ("review_action", review_input.review_action),
            ("candidate_ids", [proposal.proposal_id]),
            ("selected_candidate_id", proposal.proposal_id),
            ("score_micros_by_candidate", [[proposal.proposal_id, 1_000_000]]),
            ("transition_fields", list(gt_transition)),
        ),
        **common,
    )
    post_vv = {
        "bundle_id": post_id,
        "hard_failure_reasons": [],
        "post_vv_passed": True,
        "provided_evidence_refs": list(evidence_ids),
        "rejected_candidate_ids": [],
        "required_evidence_refs": list(evidence_ids),
        "validated_candidate_ids": [proposal.proposal_id],
    }
    gt_advisory = {
        "actor_role": "gt",
        "advisory_id": gt_id,
        "advisory_only": True,
        "attempted_effect": "CREATE_ROOT_DECISION",
        "candidate_ids": [proposal.proposal_id],
        "creates_final_output": False,
        "requests_effect": False,
        "score_micros_by_candidate": {proposal.proposal_id: 1_000_000},
        "selected_candidate_id": proposal.proposal_id,
        "source_artifact_type": "GTAdvisoryReport",
        "source_lifecycle_state": "VALIDATED",
        "target_artifact_type": "RootDecision",
    }
    action = review_input.review_action
    policy = {
        "allow_accept": action not in {"REJECT"},
        "conflict_policy": "REJECT",
        "hard_policy_passed": proposal.selected_mode != "blocked",
        "identity_passed": True,
        "no_candidate_policy": "REJECT",
        "policy_id": snapshot.policy_snapshot_id,
        "scope_passed": True,
    }
    permission = {
        "permission_ref": None,
        "permission_required": proposal.selected_mode == "needs_user",
        "permission_scope_valid": True,
        "user_permission_present": False,
    }
    decision_input = build_root_decision_input_v01(
        transaction_id=router_input.transaction_id,
        target_root_id=router_input.owning_root_id,
        root_review_packet=packet,
        post_vv_bundle=post_vv,
        gt_advisory=gt_advisory,
        policy_state=policy,
        permission_state=permission,
        temporal_state={
            "expired": False,
            "not_before_satisfied": True,
            "temporal_valid": True,
            "time_envelope_ref": snapshot.time_envelope_ref,
        },
        conflict_state={
            "conflict_set_ids": [],
            "material_unresolved_conflict": False,
        },
        prior_root_state={
            "prior_decision": None,
            "prior_decision_id": None,
            "prior_selected_candidate_id": None,
        },
    )
    input_errors = validate_root_decision_input_v01(
        kernel=root_kernel, decision_input=decision_input
    )
    if input_errors:
        error = ValueError("g2c_root_input_invalid")
        error.__cause__ = None
        setattr(error, "source_reasons", input_errors)
        raise error
    result = decide_root_v01(kernel=root_kernel, decision_input=decision_input)
    result_errors = validate_root_decision_result_v01(
        kernel=root_kernel, decision_input=decision_input, result=result
    )
    if result_errors or not result.root_commit_created or result.conflict_set_ids != ():
        error = ValueError("g2c_root_result_invalid")
        setattr(error, "source_reasons", result_errors)
        raise error
    return request, claim, contribution, packet, decision_input, result


def build_execution_mode_root_decision_source_v01(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
) -> tuple[
    SemanticWorkRequestV01, NormalizedClaimV01, ActorContributionV01,
    RootReviewPacketV01, RootDecisionInputV01, RootDecisionResultV01,
]:
    try:
        report = validate_root_execution_mode_review_input_against_sources_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
        )
        if report.validation_status != "PASS":
            raise ValueError(report.reason_codes[0])
        return _root_source_family(
            review_input=review_input, proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel,
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_root_input_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_root_input_invalid") from None


def _expected_root_source(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> None:
    family = _root_source_family(
        review_input=review_input, proposal=proposal, router_input=router_input,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
        root_kernel=root_kernel,
    )
    if root_decision_input != family[4] or root_decision_result != family[5]:
        raise ValueError("g2c_source_object_substituted")


def _project_root_decision(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    root_decision_result: RootDecisionResultV01,
) -> RootExecutionModeDecisionV01:
    action = review_input.review_action
    if action == "ACCEPT":
        outcome, expected_source, expected_reason = (
            "ACCEPT", "ACCEPT", "validated_candidate_accepted"
        )
    elif action == "NARROW":
        outcome, expected_source, expected_reason = (
            "NARROW", "ACCEPT", "validated_candidate_accepted"
        )
    elif action == "REJECT":
        outcome, expected_source, expected_reason = (
            "REJECT", "REJECT", "policy_rejected_candidate"
        )
    elif proposal.selected_mode == "blocked":
        outcome, expected_source, expected_reason = (
            "BLOCKED", "BLOCKED_FAIL_CLOSED", "hard_policy_violation"
        )
    elif proposal.selected_mode == "needs_user":
        outcome, expected_source, expected_reason = (
            "NEEDS_USER", "NEEDS_USER", "user_permission_missing"
        )
    else:
        raise ValueError("g2c_root_mapping_invalid")
    if (
        root_decision_result.decision != expected_source
        or root_decision_result.reason_code != expected_reason
        or root_decision_result.root_commit_created is not True
        or root_decision_result.permission_created is not False
        or root_decision_result.final_output_created is not False
        or root_decision_result.effect_requested is not False
    ):
        raise ValueError("g2c_root_mapping_invalid")
    accepted = outcome in {"ACCEPT", "NARROW"}
    provisional = RootExecutionModeDecisionV01(
        decision_id="emrootdecision_v01:" + _ZERO_SHA256,
        root_review_input_id=review_input.root_review_input_id,
        proposal_id=proposal.proposal_id,
        router_input_id=router_input.router_input_id,
        request_id=router_input.request_id,
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        domain_id=router_input.local_routing_snapshot.domain_id,
        outcome=outcome,
        accepted_mode=proposal.selected_mode if accepted else None,
        accepted_scope_ref=review_input.accepted_scope_ref if accepted else None,
        scope_narrowing_proof_id=(
            review_input.scope_narrowing_proof_id if outcome == "NARROW" else None
        ),
        downstream_consumption_class=(
            proposal.downstream_consumption_class
            if accepted else "TERMINAL_NO_CONSUMPTION"
        ),
        downstream_action_packet_required=(
            proposal.downstream_action_packet_required if accepted else False
        ),
        source_root_decision_id=root_decision_result.decision_id,
        source_root_decision_input_id=root_decision_result.decision_input_id,
        source_root_decision=root_decision_result.decision,
        source_root_reason_code=root_decision_result.reason_code,
        source_root_transition_decision_id=(
            root_decision_result.transition_decision.decision_id
        ),
        source_root_transition_decision=(
            root_decision_result.transition_decision.decision
        ),
        reason_codes=(_ROOT_PROJECTION_REASON[outcome],),
        route_eligibility_candidate=accepted,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        topology_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    decision = replace(provisional, decision_id=_rebuild_identity(provisional))
    errors = _root_decision_errors(decision)
    if errors:
        raise ValueError(errors[0])
    return decision


def project_root_execution_mode_decision_v01(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> RootExecutionModeDecisionV01:
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        proposal_artifact = _expected_proposal_artifact(
            proposal=proposal, router_input=router_input
        )
        proposal_transition = _build_profile_transition(
            registry=_build_execution_mode_transition_registry_profile_v01(),
            rule_id="g2c_transition:proposal_to_root_review:v01",
        )
        expected_review = _build_review_input(
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
            review_action=review_input.review_action,
            accepted_scope_ref=review_input.accepted_scope_ref,
            narrowing_basis_refs=review_input.narrowing_basis_refs,
        )
        if review_input != expected_review:
            raise ValueError("g2c_source_object_substituted")
        _expected_root_source(
            review_input=review_input, proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        return _project_root_decision(
            review_input=review_input, proposal=proposal, router_input=router_input,
            root_decision_result=root_decision_result,
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_root_mapping_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_root_mapping_invalid") from None


def validate_root_execution_mode_decision_against_source_v01(
    *, decision: RootExecutionModeDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> ExecutionModeValidationReportV01:
    try:
        review_report = validate_root_execution_mode_review_input_against_sources_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
        )
        if review_report.validation_status != "PASS":
            return _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED", stage="ROOT_REVIEW",
                reasons=review_report.reason_codes,
                source_reasons=review_report.source_reason_codes,
            )
        kernel_reasons = validate_root_decision_kernel_v01(root_kernel)
        if kernel_reasons:
            return _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED",
                stage="ROOT_DECISION", reasons=("g2c_root_input_invalid",),
                source_reasons=kernel_reasons,
            )
        input_reasons = validate_root_decision_input_v01(
            kernel=root_kernel, decision_input=root_decision_input
        )
        if input_reasons:
            return _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED",
                stage="ROOT_DECISION", reasons=("g2c_root_input_invalid",),
                source_reasons=input_reasons,
            )
        result_reasons = validate_root_decision_result_v01(
            kernel=root_kernel, decision_input=root_decision_input,
            result=root_decision_result,
        )
        if result_reasons:
            return _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED",
                stage="ROOT_DECISION", reasons=("g2c_root_result_invalid",),
                source_reasons=result_reasons,
            )
        _expected_root_source(
            review_input=review_input, proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        structural = validate_root_execution_mode_decision_v01(decision)
        if structural.validation_status != "PASS":
            return _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED", stage="ROOT_DECISION",
                reasons=structural.reason_codes,
            )
        expected = _project_root_decision(
            review_input=review_input, proposal=proposal, router_input=router_input,
            root_decision_result=root_decision_result,
        )
        if decision != expected:
            raise ValueError("g2c_source_object_substituted")
        return _c4_report(
            target="ROOT_DECISION_AGAINST_SOURCE",
            artifact_id=decision.decision_id, router_input=router_input,
            status="PASS", stage="NONE",
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_root_result_invalid"
        stage = "ROOT_REVIEW" if reason in {
            "g2c_review_action_invalid", "g2c_terminal_review_mismatch",
            "g2c_scope_narrowing_invalid", "g2c_policy_snapshot_binding_mismatch",
            "g2c_terminal_contribution_scope_mismatch",
        } else "ROOT_DECISION"
        return _c4_report(
            target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage=stage,
            reasons=(reason,), source_reasons=getattr(exc, "source_reasons", ()),
        )
    except Exception:
        return _c4_report(
            target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage="ROOT_DECISION",
            reasons=("g2c_root_result_invalid",),
        )


def review_execution_mode_proposal_v01(
    *, review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
) -> tuple[
    RootExecutionModeDecisionV01 | None, RootDecisionKernelV01 | None,
    RootDecisionInputV01 | None, RootDecisionResultV01 | None,
    ExecutionModeValidationReportV01,
]:
    kernel: RootDecisionKernelV01 | None = None
    decision_input: RootDecisionInputV01 | None = None
    result: RootDecisionResultV01 | None = None
    try:
        review_report = validate_root_execution_mode_review_input_against_sources_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
        )
        if review_report.validation_status != "PASS":
            return None, None, None, None, _c4_report(
                target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED", stage="ROOT_REVIEW",
                reasons=_public_reason_union(
                    review_report.reason_codes, ("g2c_fail_closed_return_to_root",)
                ), source_reasons=review_report.source_reason_codes,
            )
        kernel = build_root_decision_kernel_v01()
        family = build_execution_mode_root_decision_source_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=kernel,
        )
        decision_input, result = family[4], family[5]
        decision = _project_root_decision(
            review_input=review_input, proposal=proposal, router_input=router_input,
            root_decision_result=result,
        )
        report = validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=kernel, root_decision_input=decision_input,
            root_decision_result=result,
        )
        if report.validation_status != "PASS":
            return None, kernel, decision_input, result, report
        return decision, kernel, decision_input, result, report
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_root_input_invalid"
        return None, kernel, decision_input, result, _c4_report(
            target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage="ROOT_DECISION",
            reasons=_public_reason_union((reason,), ("g2c_fail_closed_return_to_root",)),
            source_reasons=getattr(exc, "source_reasons", ()),
        )
    except Exception:
        return None, kernel, decision_input, result, _c4_report(
            target="ROOT_DECISION_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage="ROOT_DECISION",
            reasons=_public_reason_union(
                ("g2c_root_result_invalid",), ("g2c_fail_closed_return_to_root",)
            ),
        )


def _decision_payload(decision: RootExecutionModeDecisionV01) -> dict[str, object]:
    return {
        "decision_id": decision.decision_id,
        "root_review_input_id": decision.root_review_input_id,
        "proposal_id": decision.proposal_id,
        "router_input_id": decision.router_input_id,
        "request_id": decision.request_id,
        "domain_id": decision.domain_id,
        "outcome": decision.outcome,
        "accepted_mode": decision.accepted_mode,
        "accepted_scope_ref": decision.accepted_scope_ref,
        "scope_narrowing_proof_id": decision.scope_narrowing_proof_id,
        "downstream_consumption_class": decision.downstream_consumption_class,
        "downstream_action_packet_required": decision.downstream_action_packet_required,
        "source_root_decision_id": decision.source_root_decision_id,
        "source_root_decision_input_id": decision.source_root_decision_input_id,
        "source_root_decision": decision.source_root_decision,
        "source_root_reason_code": decision.source_root_reason_code,
        "source_root_transition_decision_id": decision.source_root_transition_decision_id,
        "source_root_transition_decision": decision.source_root_transition_decision,
        "reason_codes": list(decision.reason_codes),
        "route_eligibility_candidate": decision.route_eligibility_candidate,
        "authority_created": decision.authority_created,
        "permission_created": decision.permission_created,
        "action_commit_packet_created": decision.action_commit_packet_created,
        "receipt_created": decision.receipt_created,
        "topology_created": decision.topology_created,
        "final_output_created": decision.final_output_created,
        "drs_write_created": decision.drs_write_created,
        "real_world_effects_count": decision.real_world_effects_count,
    }


def _expected_decision_artifact(
    *, decision: RootExecutionModeDecisionV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
) -> KernelArtifactV01:
    lifecycle = {
        "ACCEPT": "ROOT_ACCEPTED", "NARROW": "ROOT_ACCEPTED",
        "REJECT": "ROOT_REJECTED", "BLOCKED": "BLOCKED_FAIL_CLOSED",
        "NEEDS_USER": "ROOT_REVIEWED",
    }[decision.outcome]
    return _finish_c4_artifact(
        artifact_type="RootExecutionModeDecision",
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        source_component="root_decision_v01",
        authority_class="ROOT_OWNED",
        lifecycle_state=lifecycle,
        payload=_decision_payload(decision),
        trace_refs=_lexical_refs(
            proposal_artifact.artifact_id,
            proposal.proposal_id,
            decision.root_review_input_id,
            decision.source_root_decision_id,
            decision.source_root_transition_decision_id,
            decision.decision_id,
        ),
        parent_refs=(proposal_artifact.artifact_id,),
        snapshot=router_input.local_routing_snapshot,
        domain=_G2C_DECISION_ARTIFACT_DOMAIN_V01,
        prefix="emabi_decision_v01:",
    )


def _require_decision_artifact(
    *, decision_artifact: object, decision: RootExecutionModeDecisionV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    proposal_artifact: KernelArtifactV01,
) -> None:
    if type(decision_artifact) is not KernelArtifactV01:
        raise ValueError("g2c_abi_profile_invalid")
    expected = _expected_decision_artifact(
        decision=decision, proposal=proposal, router_input=router_input,
        proposal_artifact=proposal_artifact,
    )
    if decision_artifact != expected:
        raise ValueError("g2c_abi_projection_substituted")
    if validate_kernel_artifact_bundle_v01(
        artifacts=(proposal_artifact, decision_artifact)
    ):
        raise ValueError("g2c_abi_bundle_validation_failed")


def project_root_execution_mode_decision_kernel_artifact_v01(
    *, decision: RootExecutionModeDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
) -> KernelArtifactV01:
    try:
        report = validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        if report.validation_status != "PASS":
            raise ValueError(report.reason_codes[0])
        artifact = _expected_decision_artifact(
            decision=decision, proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
        )
        _require_decision_artifact(
            decision_artifact=artifact, decision=decision, proposal=proposal,
            router_input=router_input, proposal_artifact=proposal_artifact,
        )
        return artifact
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_abi_profile_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_abi_profile_invalid") from None


def _post_root_rule_id(decision: RootExecutionModeDecisionV01) -> str:
    return {
        "ACCEPT": "g2c_transition:root_accept_to_route:v01",
        "NARROW": "g2c_transition:root_narrow_to_route:v01",
        "REJECT": "g2c_transition:root_reject_record:v01",
        "BLOCKED": "g2c_transition:root_block_record:v01",
        "NEEDS_USER": "g2c_transition:root_needs_user_record:v01",
    }[decision.outcome]


def _require_post_root_transition(
    *, transition: object, registry: TransitionRegistryV01,
    decision: RootExecutionModeDecisionV01,
) -> None:
    if type(transition) is not TransitionDecisionV01:
        raise ValueError("g2c_post_root_transition_missing")
    if transition != _build_profile_transition(
        registry=registry, rule_id=_post_root_rule_id(decision)
    ):
        raise ValueError("g2c_post_root_transition_substituted")


def evaluate_execution_mode_root_route_transition_v01(
    *, registry: TransitionRegistryV01,
    proposal_transition_decision: TransitionDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    decision: RootExecutionModeDecisionV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    proposal_artifact: KernelArtifactV01,
    decision_artifact: KernelArtifactV01,
) -> TransitionDecisionV01:
    try:
        _require_pre_root_transition(
            transition=proposal_transition_decision, registry=registry
        )
        report = validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        if report.validation_status != "PASS":
            raise ValueError(report.reason_codes[0])
        _require_decision_artifact(
            decision_artifact=decision_artifact, decision=decision,
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
        )
        if root_decision_result.root_commit_created is not True:
            raise ValueError("g2c_transition_root_commit_required")
        transition = _build_profile_transition(
            registry=registry, rule_id=_post_root_rule_id(decision)
        )
        _require_post_root_transition(
            transition=transition, registry=registry, decision=decision
        )
        return transition
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_transition_substituted"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_transition_substituted") from None


def _route_payload(
    *, decision: RootExecutionModeDecisionV01,
    registry: TransitionRegistryV01,
    transition: TransitionDecisionV01,
) -> dict[str, object]:
    return {
        "request_id": decision.request_id,
        "domain_id": decision.domain_id,
        "decision_id": decision.decision_id,
        "accepted_mode": decision.accepted_mode,
        "accepted_scope_ref": decision.accepted_scope_ref,
        "downstream_consumption_class": decision.downstream_consumption_class,
        "downstream_action_packet_required": decision.downstream_action_packet_required,
        "abi_profile_id": _G2C_ABI_PROFILE_ID_V01,
        "transition_registry_id": registry.registry_id,
        "root_route_transition_decision_id": transition.decision_id,
        "topology_created": False,
        "permission_created": False,
        "action_commit_packet_created": False,
        "final_output_created": False,
        "real_world_effects_count": 0,
    }


def _expected_route_artifact(
    *, decision: RootExecutionModeDecisionV01,
    router_input: ExecutionModeRouterInputV01,
    decision_artifact: KernelArtifactV01,
    registry: TransitionRegistryV01,
    transition: TransitionDecisionV01,
) -> KernelArtifactV01 | None:
    if decision.outcome not in {"ACCEPT", "NARROW"}:
        return None
    return _finish_c4_artifact(
        artifact_type="ExecutionModeRouteEligibility",
        transaction_id=router_input.transaction_id,
        owning_root_id=router_input.owning_root_id,
        source_component="root_decision_v01",
        authority_class="ROOT_AUTHORIZED",
        lifecycle_state="ROOT_ACCEPTED",
        payload=_route_payload(
            decision=decision, registry=registry, transition=transition
        ),
        trace_refs=_lexical_refs(
            decision_artifact.artifact_id, decision.decision_id,
            registry.registry_id, transition.decision_id,
        ),
        parent_refs=(decision_artifact.artifact_id,),
        snapshot=router_input.local_routing_snapshot,
        domain=_G2C_ROUTE_ARTIFACT_DOMAIN_V01,
        prefix="emabi_route_v01:",
    )


def _require_route_artifact(
    *, route_artifact: object, expected: KernelArtifactV01 | None,
    proposal_artifact: KernelArtifactV01,
    decision_artifact: KernelArtifactV01,
) -> None:
    if expected is None:
        if route_artifact is not None:
            raise ValueError("g2c_route_eligibility_invalid")
        bundle = (proposal_artifact, decision_artifact)
    else:
        if type(route_artifact) is RootExecutionModeDecisionV01:
            raise ValueError("g2c_route_decision_bypass_forbidden")
        if type(route_artifact) is not KernelArtifactV01 or route_artifact != expected:
            raise ValueError("g2c_route_eligibility_invalid")
        bundle = (proposal_artifact, decision_artifact, route_artifact)
    if validate_kernel_artifact_bundle_v01(artifacts=bundle):
        raise ValueError("g2c_abi_bundle_validation_failed")


def project_execution_mode_route_eligibility_kernel_artifact_v01(
    *, decision: RootExecutionModeDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    decision_artifact: KernelArtifactV01,
    root_route_transition_decision: TransitionDecisionV01,
) -> KernelArtifactV01 | None:
    try:
        registry = _build_execution_mode_transition_registry_profile_v01()
        _require_post_root_transition(
            transition=root_route_transition_decision,
            registry=registry, decision=decision,
        )
        report = validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        if report.validation_status != "PASS":
            raise ValueError(report.reason_codes[0])
        _require_decision_artifact(
            decision_artifact=decision_artifact, decision=decision,
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
        )
        artifact = _expected_route_artifact(
            decision=decision, router_input=router_input,
            decision_artifact=decision_artifact, registry=registry,
            transition=root_route_transition_decision,
        )
        _require_route_artifact(
            route_artifact=artifact, expected=artifact,
            proposal_artifact=proposal_artifact,
            decision_artifact=decision_artifact,
        )
        return artifact
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_route_eligibility_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_route_eligibility_invalid") from None


def validate_execution_mode_route_eligibility_against_source_v01(
    *, route_eligibility_artifact: KernelArtifactV01,
    decision: RootExecutionModeDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    decision_artifact: KernelArtifactV01,
    root_route_transition_decision: TransitionDecisionV01,
) -> ExecutionModeValidationReportV01:
    try:
        if type(route_eligibility_artifact) is RootExecutionModeDecisionV01:
            raise ValueError("g2c_route_decision_bypass_forbidden")
        decision_report = validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition_decision,
            root_kernel=root_kernel, root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
        )
        if decision_report.validation_status != "PASS":
            return _c4_report(
                target="ROUTE_ELIGIBILITY_AGAINST_SOURCE", artifact_id=None,
                router_input=router_input, status="FAIL_CLOSED",
                stage=decision_report.failure_stage,
                reasons=decision_report.reason_codes,
                source_reasons=decision_report.source_reason_codes,
            )
        _require_decision_artifact(
            decision_artifact=decision_artifact, decision=decision,
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
        )
        registry = _build_execution_mode_transition_registry_profile_v01()
        _require_post_root_transition(
            transition=root_route_transition_decision,
            registry=registry, decision=decision,
        )
        expected = _expected_route_artifact(
            decision=decision, router_input=router_input,
            decision_artifact=decision_artifact, registry=registry,
            transition=root_route_transition_decision,
        )
        if expected is None:
            raise ValueError("g2c_route_eligibility_invalid")
        _require_route_artifact(
            route_artifact=route_eligibility_artifact, expected=expected,
            proposal_artifact=proposal_artifact,
            decision_artifact=decision_artifact,
        )
        return _c4_report(
            target="ROUTE_ELIGIBILITY_AGAINST_SOURCE",
            artifact_id=route_eligibility_artifact.artifact_id,
            router_input=router_input, status="PASS", stage="NONE",
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_route_eligibility_invalid"
        stage = "ABI" if reason.startswith("g2c_abi_") else (
            "TRANSITION" if "transition" in reason else "ROUTE_ELIGIBILITY"
        )
        return _c4_report(
            target="ROUTE_ELIGIBILITY_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED", stage=stage,
            reasons=(reason,),
        )
    except Exception:
        return _c4_report(
            target="ROUTE_ELIGIBILITY_AGAINST_SOURCE", artifact_id=None,
            router_input=router_input, status="FAIL_CLOSED",
            stage="ROUTE_ELIGIBILITY",
            reasons=("g2c_route_eligibility_invalid",),
        )


def validate_execution_mode_abi_profile_v01(
    *, proposal: ExecutionModeProposalV01,
    router_input: ExecutionModeRouterInputV01,
    source_context: ExecutionModeSourceContextV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    decision: RootExecutionModeDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    decision_artifact: KernelArtifactV01,
    root_route_transition_decision: TransitionDecisionV01,
    route_eligibility_artifact: KernelArtifactV01 | None,
) -> ExecutionModeValidationReportV01:
    target = "ABI_PROFILE"
    try:
        _require_c4_proposal(
            proposal=proposal, router_input=router_input, source_context=source_context
        )
        _require_proposal_artifact(
            proposal_artifact=proposal_artifact, proposal=proposal,
            router_input=router_input,
        )
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else "g2c_abi_profile_invalid"
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_abi_profile_invalid"
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ABI", reasons=(reason,),
        )
    registry = _build_execution_mode_transition_registry_profile_v01()
    try:
        _require_pre_root_transition(
            transition=proposal_transition_decision, registry=registry
        )
    except ValueError as exc:
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="TRANSITION",
            reasons=(exc.args[0],),
        )
    review_report = validate_root_execution_mode_review_input_against_sources_v01(
        review_input=review_input, proposal=proposal, router_input=router_input,
        source_context=source_context, proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
    )
    if review_report.validation_status != "PASS":
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ROOT_REVIEW",
            reasons=review_report.reason_codes,
            source_reasons=review_report.source_reason_codes,
        )
    decision_report = validate_root_execution_mode_decision_against_source_v01(
        decision=decision, review_input=review_input, proposal=proposal,
        router_input=router_input, source_context=source_context,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
        root_kernel=root_kernel, root_decision_input=root_decision_input,
        root_decision_result=root_decision_result,
    )
    if decision_report.validation_status != "PASS":
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ROOT_DECISION",
            reasons=decision_report.reason_codes,
            source_reasons=decision_report.source_reason_codes,
        )
    try:
        _require_decision_artifact(
            decision_artifact=decision_artifact, decision=decision,
            proposal=proposal, router_input=router_input,
            proposal_artifact=proposal_artifact,
        )
    except ValueError as exc:
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ABI", reasons=(exc.args[0],),
        )
    try:
        _require_post_root_transition(
            transition=root_route_transition_decision,
            registry=registry, decision=decision,
        )
    except ValueError as exc:
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="TRANSITION", reasons=(exc.args[0],),
        )
    try:
        expected_route = _expected_route_artifact(
            decision=decision, router_input=router_input,
            decision_artifact=decision_artifact, registry=registry,
            transition=root_route_transition_decision,
        )
        _require_route_artifact(
            route_artifact=route_eligibility_artifact, expected=expected_route,
            proposal_artifact=proposal_artifact,
            decision_artifact=decision_artifact,
        )
    except ValueError as exc:
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ROUTE_ELIGIBILITY",
            reasons=(exc.args[0],),
        )
    except Exception:
        return _c4_report(
            target=target, artifact_id=None, router_input=router_input,
            status="FAIL_CLOSED", stage="ABI",
            reasons=("g2c_abi_profile_invalid",),
        )
    return _c4_report(
        target=target,
        artifact_id=(
            route_eligibility_artifact.artifact_id
            if route_eligibility_artifact is not None else decision_artifact.artifact_id
        ),
        router_input=router_input, status="PASS", stage="NONE",
    )


def _validate_serialized(
    value: object,
    expected_type: type[object],
) -> ExecutionModeValidationReportV01:
    try:
        errors = _STRUCTURAL_ERROR_FUNCTIONS[expected_type](value)
        return _structural_report(
            target=expected_type.__name__,
            value=value,
            errors=errors,
        )
    except Exception:
        return _structural_report(
            target=expected_type.__name__,
            value=value,
            errors=("g2c_scalar_invalid",),
        )


def _serialize_serialized(value: object, expected_type: type[object]) -> dict[str, object]:
    try:
        errors = _STRUCTURAL_ERROR_FUNCTIONS[expected_type](value)
        if errors:
            raise ValueError(errors[0])
        return _plain_data_unchecked(value)
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_scalar_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_scalar_invalid") from None


def _rebuild_serialized(value: object, expected_type: type[object]) -> str:
    try:
        if type(value) is not expected_type:
            raise ValueError("g2c_exact_type_invalid")
        return _rebuild_identity(value)
    except ValueError as exc:
        reason = str(exc)
        if reason not in PUBLIC_G2C_REASON_CODES_V01:
            reason = "g2c_identity_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_identity_invalid") from None


def validate_execution_mode_bsep_binding_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeBSEPBindingV01)


def execution_mode_bsep_binding_to_plain_data_v01(
    value: ExecutionModeBSEPBindingV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeBSEPBindingV01)


def rebuild_execution_mode_bsep_binding_identity_v01(
    value: ExecutionModeBSEPBindingV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeBSEPBindingV01)


def validate_execution_mode_replay_binding_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeReplayBindingV01)


def execution_mode_replay_binding_to_plain_data_v01(
    value: ExecutionModeReplayBindingV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeReplayBindingV01)


def rebuild_execution_mode_replay_binding_identity_v01(
    value: ExecutionModeReplayBindingV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeReplayBindingV01)


def validate_execution_mode_g2a_binding_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeG2ABindingV01)


def execution_mode_g2a_binding_to_plain_data_v01(
    value: ExecutionModeG2ABindingV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeG2ABindingV01)


def rebuild_execution_mode_g2a_binding_identity_v01(
    value: ExecutionModeG2ABindingV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeG2ABindingV01)


def validate_execution_mode_g2b_binding_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeG2BBindingV01)


def execution_mode_g2b_binding_to_plain_data_v01(
    value: ExecutionModeG2BBindingV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeG2BBindingV01)


def rebuild_execution_mode_g2b_binding_identity_v01(
    value: ExecutionModeG2BBindingV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeG2BBindingV01)


def validate_execution_mode_local_mode_profile_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeLocalModeProfileV01)


def execution_mode_local_mode_profile_to_plain_data_v01(
    value: ExecutionModeLocalModeProfileV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeLocalModeProfileV01)


def rebuild_execution_mode_local_mode_profile_identity_v01(
    value: ExecutionModeLocalModeProfileV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeLocalModeProfileV01)


def validate_execution_mode_local_routing_snapshot_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeLocalRoutingSnapshotV01)


def execution_mode_local_routing_snapshot_to_plain_data_v01(
    value: ExecutionModeLocalRoutingSnapshotV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeLocalRoutingSnapshotV01)


def rebuild_execution_mode_local_routing_snapshot_identity_v01(
    value: ExecutionModeLocalRoutingSnapshotV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeLocalRoutingSnapshotV01)


def validate_execution_mode_router_input_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeRouterInputV01)


def execution_mode_router_input_to_plain_data_v01(
    value: ExecutionModeRouterInputV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeRouterInputV01)


def rebuild_execution_mode_router_input_identity_v01(
    value: ExecutionModeRouterInputV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeRouterInputV01)


def validate_execution_mode_feasibility_row_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeFeasibilityRowV01)


def execution_mode_feasibility_row_to_plain_data_v01(
    value: ExecutionModeFeasibilityRowV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeFeasibilityRowV01)


def rebuild_execution_mode_feasibility_row_identity_v01(
    value: ExecutionModeFeasibilityRowV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeFeasibilityRowV01)


def validate_execution_mode_proposal_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, ExecutionModeProposalV01)


def execution_mode_proposal_to_plain_data_v01(
    value: ExecutionModeProposalV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeProposalV01)


def rebuild_execution_mode_proposal_identity_v01(
    value: ExecutionModeProposalV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeProposalV01)


def validate_root_execution_mode_review_input_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, RootExecutionModeReviewInputV01)


def root_execution_mode_review_input_to_plain_data_v01(
    value: RootExecutionModeReviewInputV01,
) -> dict[str, object]:
    return _serialize_serialized(value, RootExecutionModeReviewInputV01)


def rebuild_root_execution_mode_review_input_identity_v01(
    value: RootExecutionModeReviewInputV01,
) -> str:
    return _rebuild_serialized(value, RootExecutionModeReviewInputV01)


def validate_root_execution_mode_decision_v01(
    value: object,
) -> ExecutionModeValidationReportV01:
    return _validate_serialized(value, RootExecutionModeDecisionV01)


def root_execution_mode_decision_to_plain_data_v01(
    value: RootExecutionModeDecisionV01,
) -> dict[str, object]:
    return _serialize_serialized(value, RootExecutionModeDecisionV01)


def rebuild_root_execution_mode_decision_identity_v01(
    value: RootExecutionModeDecisionV01,
) -> str:
    return _rebuild_serialized(value, RootExecutionModeDecisionV01)


def validate_execution_mode_validation_report_v01(
    value: object,
) -> tuple[str, ...]:
    try:
        return _validation_report_errors(value)
    except Exception:
        return ("g2c_scalar_invalid",)


def execution_mode_validation_report_to_plain_data_v01(
    value: ExecutionModeValidationReportV01,
) -> dict[str, object]:
    return _serialize_serialized(value, ExecutionModeValidationReportV01)


def rebuild_execution_mode_validation_report_identity_v01(
    value: ExecutionModeValidationReportV01,
) -> str:
    return _rebuild_serialized(value, ExecutionModeValidationReportV01)
