"""Deterministic planning contracts for Gate 2 G2-C1 ExecutionModeRouter.

This module implements only the canonical scalar, type, structural validation,
identity, local-profile, local-snapshot, and router-input surface accepted for
G2-C1. It performs no source semantics, routing, feasibility, Root review,
Transition evaluation, ABI projection, I/O, provider work, or effects.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import math
import re
import types
import unicodedata
from typing import get_args, get_origin, get_type_hints

from hedgehog.action_commit_packet_v02 import (
    ActionCommitPacketRegistryV02,
    ActionDependencyCurrentObservationV01,
    ActionPacketPresentEligibilityInspectionV01,
    ContractFulfillmentCorridorV01,
    CorridorStepV01,
    LogicalTimeBridgeV01,
)
from hedgehog.drs_g2b_compatibility_v01 import LegacyDRSProjectionV01
from hedgehog.drs_memory_resolution_v01 import DRSResolutionReportV01
from hedgehog.evidence.external_anchor_v01 import (
    AnchoredPackageVerificationV01,
    ExternalAnchorPublicationV01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import DomainEvidenceProjectionV01
from hedgehog.evidence.sealed_package_v01 import SealedPackageManifestV01
from hedgehog.evidence.sealed_replay_evidence_v01 import SealedReplayEvidenceV01
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
)
from hedgehog.kernel.transition_registry_v01 import (
    ActionPacketTransitionRegistryProfileV01,
)


MODULE_ID = "kernel_execution_mode_router_v01"
SLICE_ID = "gate2_g2c1_execution_mode_router_structural"
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
    sealed_replay_evidence: SealedReplayEvidenceV01 | None
    replay_source_manifest: SealedPackageManifestV01 | None
    replay_source_domain_projection: DomainEvidenceProjectionV01 | None
    replay_source_safe_file_contents: tuple[bytes, ...]
    replay_anchor_publication: ExternalAnchorPublicationV01 | None
    replay_anchored_verification: AnchoredPackageVerificationV01 | None
    replay_supplied_anchor_publication_id: str | None
    replay_reconstructed_manifest: SealedPackageManifestV01 | None
    replay_reconstructed_domain_projection: DomainEvidenceProjectionV01 | None
    replay_reconstructed_safe_file_contents: tuple[bytes, ...]
    g2a_inspection: ActionPacketPresentEligibilityInspectionV01 | None
    g2a_registry: ActionCommitPacketRegistryV02 | None
    g2a_packet_id: str | None
    g2a_corridor: ContractFulfillmentCorridorV01 | None
    g2a_corridor_step: CorridorStepV01 | None
    g2a_current_dependency_observations: tuple[
        ActionDependencyCurrentObservationV01, ...
    ]
    g2a_logical_time_bridge: LogicalTimeBridgeV01 | None
    g2a_evaluation_time: int | None
    g2a_evaluation_time_source: str | None
    g2a_evaluation_context_id: str | None
    g2a_transition_registry_profile: ActionPacketTransitionRegistryProfileV01 | None
    g2b_resolution_report: DRSResolutionReportV01 | None
    g2b_compatibility_projections: tuple[LegacyDRSProjectionV01, ...]
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
    if value.mode not in CANONICAL_EXECUTION_MODES_V01:
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
    if not set(value.satisfied_evidence_refs).issubset(value.required_evidence_refs):
        errors.append("g2c_feasibility_row_invalid")
    rank_by_mode = dict(EXECUTION_MODE_SAFE_DEPTH_RANKS_V01)
    if value.category == "EXECUTABLE":
        if (
            value.mode not in EXECUTABLE_EXECUTION_MODES_V01
            or value.safe_depth_rank != rank_by_mode.get(value.mode)
            or not _source_identity_valid(value.local_mode_profile_id)
            or not _exact_int_valid(value.cost_units, minimum=0)
            or value.feasibility_status not in {"FEASIBLE", "INFEASIBLE"}
            or value.downstream_compute_class
            not in {
                "NONE",
                "MEMORY_INFORMED",
                "LOCAL_SLM",
                "CLOUD_LLM",
                "FULL_SEMANTIC",
                "FULL_FRACTAL",
            }
        ):
            errors.append("g2c_feasibility_row_invalid")
    elif value.category == "TERMINAL":
        if (
            value.mode not in {"blocked", "needs_user"}
            or value.safe_depth_rank is not None
            or value.local_mode_profile_id is not None
            or value.required_capability_id is not None
            or value.cost_units is not None
            or value.downstream_compute_class != "TERMINAL"
            or value.feasibility_status
            not in {"TERMINAL_SELECTED", "TERMINAL_NOT_SELECTED"}
        ):
            errors.append("g2c_feasibility_row_invalid")
    if value.root_review_required is not True:
        errors.append("g2c_feasibility_row_invalid")
    errors.extend(_fixed_zero_effect_errors(value))
    return _sort_public_reasons(errors) if errors else ()


def _proposal_errors(value: object) -> tuple[str, ...]:
    errors = list(_common_serialized_errors(value, ExecutionModeProposalV01))
    if type(value) is not ExecutionModeProposalV01:
        return tuple(errors)
    if value.selected_mode not in CANONICAL_EXECUTION_MODES_V01:
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
            if item.feasibility_status in {"FEASIBLE", "TERMINAL_SELECTED"}
            and item.feasibility_row_id == value.selected_feasibility_row_id
        )
        if len(selected) != 1 or selected[0].mode != value.selected_mode:
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
    if value.downstream_consumption_class not in {
        "SHORTCUT_RETURN_TO_ROOT",
        "RUNTIME_TOPOLOGY_ELIGIBLE",
        "TERMINAL_NO_CONSUMPTION",
    }:
        errors.append("g2c_proposal_rows_invalid")
    terminal = value.selected_mode in {"blocked", "needs_user"}
    if terminal:
        if (
            value.selected_safe_depth_rank is not None
            or value.selected_local_mode_profile_id is not None
            or value.selected_expected_cost_units is not None
            or value.proposed_scope_ref is not None
            or value.downstream_consumption_class != "TERMINAL_NO_CONSUMPTION"
            or value.downstream_action_packet_required is not False
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
    if value.review_action == "TERMINAL_FROM_PROPOSAL" and (
        value.proposed_mode not in {"blocked", "needs_user"}
        or value.proposed_scope_ref is not None
        or value.accepted_scope_ref is not None
    ):
        errors.append("g2c_terminal_review_mismatch")
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
        type(value.sealed_replay_evidence) is SealedReplayEvidenceV01
        and type(value.replay_source_manifest) is SealedPackageManifestV01
        and type(value.replay_source_domain_projection) is DomainEvidenceProjectionV01
        and type(value.replay_anchor_publication) is ExternalAnchorPublicationV01
        and type(value.replay_anchored_verification) is AnchoredPackageVerificationV01
        and _source_identity_valid(value.replay_supplied_anchor_publication_id)
        and type(value.replay_reconstructed_manifest) is SealedPackageManifestV01
        and type(value.replay_reconstructed_domain_projection) is DomainEvidenceProjectionV01
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
        type(value.g2a_inspection) is ActionPacketPresentEligibilityInspectionV01
        and type(value.g2a_registry) is ActionCommitPacketRegistryV02
        and _source_identity_valid(value.g2a_packet_id)
        and type(value.g2a_corridor) is ContractFulfillmentCorridorV01
        and type(value.g2a_corridor_step) is CorridorStepV01
        and type(value.g2a_current_dependency_observations) is tuple
        and all(
            type(item) is ActionDependencyCurrentObservationV01
            for item in value.g2a_current_dependency_observations
        )
        and type(value.g2a_logical_time_bridge) is LogicalTimeBridgeV01
        and _exact_int_valid(value.g2a_evaluation_time)
        and _project_ref_valid(value.g2a_evaluation_time_source)
        and _project_ref_valid(value.g2a_evaluation_context_id)
        and type(value.g2a_transition_registry_profile)
        is ActionPacketTransitionRegistryProfileV01
    )
    if not (g2a_no_packet or g2a_present):
        errors.append("g2c_source_context_invalid")
    if type(value.g2b_compatibility_projections) is not tuple or any(
        type(item) is not LegacyDRSProjectionV01
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
        type(value.g2b_resolution_report) is DRSResolutionReportV01
        and bool(value.g2b_compatibility_projections)
        and _exact_int_valid(value.g2b_use_time)
        and roots_absent
    )
    g2b_direct = (
        type(value.g2b_resolution_report) is DRSResolutionReportV01
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
