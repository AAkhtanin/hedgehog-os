"""Deterministic G2-E Continuous Delta Runtime v0.1 contracts through E3.

The module defines frozen data and deterministic structural/currentness proofs.
No G2-E object is truth, Root authority, permission, execution, persistence,
or a real-world effect.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
import hashlib
import re
import unicodedata

import hedgehog.action_commit_packet_v02 as action_commit_packet
import hedgehog.drs_memory_resolution_v01 as drs_memory_resolution
import hedgehog.reuse_certificate_v01 as reuse_certificate
import hedgehog.kernel.fractal_runtime_v02 as g2d_runtime
import hedgehog.kernel.root_decision_v01 as root_runtime
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_runtime
import hedgehog.kernel.trust_model_v01 as trust_model
from hedgehog.gt_validator import validate_gt
from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01,
    KernelArtifactV01,
    build_causal_consumption_ref_v01,
    build_kernel_artifact_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_causal_consumption_ref_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.execution_mode_router_v01 import (
    ExecutionModeSourceContextV01,
    validate_execution_mode_source_context_v01,
)
from hedgehog.kernel.fractal_runtime_v02 import (
    FractalRuntimeExecutionBundleV02,
    validate_fractal_runtime_execution_bundle_v02,
    validate_runtime_topology_source_binding_against_g2c_v02,
)
from hedgehog.kernel.integrity_replay_v01 import (
    ArtifactDependencyEdgeV01,
    ArtifactManifestV01,
    ReplayVerificationResultV01,
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
    verify_artifact_manifest_v01,
    verify_artifact_replay_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    validate_root_decision_kernel_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    TransitionDecisionV01,
    build_continuous_delta_transition_registry_profile_v01 as _build_continuous_delta_transition_registry_profile_v01,
    validate_continuous_delta_transition_decision_v01 as _validate_continuous_delta_transition_decision_v01,
)
from hedgehog.post_vv import validate_result_proposal


MODULE_ID = "continuous_delta_runtime_v01"
SLICE_ID = "gate2_g2e2_dependency_graph_and_affected_closure"
CONTINUOUS_DELTA_RUNTIME_VERSION = "v0.1"
DELTA_SOURCE_BINDING_VERSION_V01 = "v0.1"
WORLD_STATE_DELTA_VERSION_V01 = "v0.1"
WORLD_STATE_DELTA_PROFILE_ID_V01 = "continuous_delta_runtime_v01"
DEPENDENCY_FINGERPRINT_PROFILE_VERSION_V01 = "v0.1"
DEPENDENCY_FINGERPRINT_HASH_ALGORITHM_V01 = "sha256"
DEPENDENCY_FINGERPRINT_CANONICALIZATION_PROFILE_V01 = (
    "integrity_replay_canonical_json_v01"
)
DEPENDENCY_FINGERPRINT_DOMAIN_SEPARATOR_V01 = (
    "HEDGEHOG_CONTINUOUS_DELTA_DEPENDENCY_FINGERPRINT_V01"
)
DEPENDENCY_FINGERPRINT_TYPED_ROLE_V01 = "G2E_DEPENDENCY_CURRENTNESS"
OBSERVED_SUCCESSOR_RELATION_V01 = "OBSERVED_SUCCESSOR_OF_BASELINE"
MAX_CHANGED_BINDINGS_V01 = 64
CONTINUOUS_DELTA_GRAPH_VERSION_V01 = "v0.1"
CONTINUOUS_DELTA_GRAPH_PROFILE_ID_V01 = "continuous_delta_dependency_graph_v01"
MAX_DEPENDENCY_GRAPH_NODES_V01 = 256
MAX_DEPENDENCY_GRAPH_EDGES_V01 = 1024
MAX_AFFECTED_HOPS_V01 = 32
GRAPH_BASIS_DOMAIN_V01 = "HEDGEHOG_CONTINUOUS_DELTA_GRAPH_BASIS_V01"
SOURCE_REPLAY_EDGE_DOMAIN_V01 = (
    "HEDGEHOG_CONTINUOUS_DELTA_SOURCE_REPLAY_EDGE_V01"
)
AFFECTED_CLOSURE_PROOF_DOMAIN_V01 = (
    "HEDGEHOG_CONTINUOUS_DELTA_AFFECTED_CLOSURE_PROOF_V01"
)
NO_CACHE_STATE_DOMAIN_V01 = "HEDGEHOG_G2E_NO_CACHE_STATE_V01"
PRESERVATION_PROOF_DOMAIN_V01 = "HEDGEHOG_G2E_PRESERVATION_PROOF_V01"

G2E_INVALIDATION_REASON_CLASSES_V01 = (
    "DEPENDENCY_FINGERPRINT_CHANGED",
    "SOURCE_FIELD_CHANGED",
    "SOURCE_ARTIFACT_CHANGED",
    "POLICY_VERSION_CHANGED",
    "SCHEMA_VERSION_CHANGED",
    "TEMPORAL_VALIDITY_CHANGED",
    "UPSTREAM_ARTIFACT_INVALIDATED",
    "ROUTE_REVALIDATION_REQUIRED",
    "PACKET_ROOT_REVIEW_REQUIRED",
    "REUSE_CERTIFICATE_STALE",
)
G2E_G2A_PACKET_RELATIONS_V01 = (
    "NOT_APPLICABLE",
    "PACKET_ROOT_REVIEW_REQUIRED",
)
G2E_G2B_REUSE_RELATIONS_V01 = (
    "NOT_APPLICABLE",
    "REUSE_CERTIFICATE_STALE",
)
G2E_G2C_ROUTE_RELATIONS_V01 = (
    "ROUTE_CURRENT",
    "ROUTE_REVALIDATION_REQUIRED",
)
_INVALIDATION_REASON_PRIORITY_V01 = (
    "ROUTE_REVALIDATION_REQUIRED",
    "PACKET_ROOT_REVIEW_REQUIRED",
    "REUSE_CERTIFICATE_STALE",
    "POLICY_VERSION_CHANGED",
    "SCHEMA_VERSION_CHANGED",
    "TEMPORAL_VALIDITY_CHANGED",
    "DEPENDENCY_FINGERPRINT_CHANGED",
    "SOURCE_ARTIFACT_CHANGED",
    "SOURCE_FIELD_CHANGED",
    "UPSTREAM_ARTIFACT_INVALIDATED",
)

VALIDATION_STATUSES_V01 = ("PASS", "FAIL_CLOSED")

PUBLIC_G2E_REASON_CODES_V01 = (
    "g2e_object_invalid",
    "g2e_identity_invalid",
    "g2e_identity_mismatch",
    "g2e_version_unsupported",
    "g2e_status_invalid",
    "g2e_reason_codes_invalid",
    "g2e_zero_operation_boundary_violated",
    "g2e_authority_boundary_violated",
    "g2e_delta_source_invalid",
    "g2e_delta_source_unvalidated",
    "g2e_delta_baseline_stale",
    "g2e_delta_time_invalid",
    "g2e_delta_future_observation",
    "g2e_delta_duplicate_binding",
    "g2e_delta_conflicting_duplicate",
    "g2e_delta_field_path_invalid",
    "g2e_delta_artifact_binding_invalid",
    "g2e_delta_cross_transaction",
    "g2e_delta_cross_domain",
    "g2e_delta_cross_root",
    "g2e_delta_policy_version_mismatch",
    "g2e_delta_schema_version_mismatch",
    "g2e_dependency_fingerprint_profile_invalid",
    "g2e_dependency_fingerprint_preimage_invalid",
    "g2e_dependency_fingerprint_role_collision",
    "g2e_dependency_fingerprint_mismatch",
    "g2e_dependency_fingerprint_forgery",
    "g2e_dependency_source_history_mismatch",
    "g2e_dependency_canonicalization_mismatch",
    "g2e_dependency_edge_invalid",
    "g2e_dependency_edge_direction_invalid",
    "g2e_dependency_edge_duplicate",
    "g2e_dependency_edge_self",
    "g2e_dependency_edge_unknown_source",
    "g2e_dependency_edge_unknown_dependent",
    "g2e_dependency_edge_cross_transaction",
    "g2e_dependency_edge_cross_domain",
    "g2e_dependency_edge_cross_root",
    "g2e_dependency_graph_cycle",
    "g2e_dependency_graph_version_mismatch",
    "g2e_dependency_graph_bounds_exceeded",
    "g2e_dependency_graph_ordering_invalid",
    "g2e_dependency_graph_missing_edge",
    "g2e_affected_request_invalid",
    "g2e_affected_changed_binding_unknown",
    "g2e_affected_closure_incomplete",
    "g2e_affected_reachable_omitted",
    "g2e_affected_unrelated_injected",
    "g2e_affected_ordering_invalid",
    "g2e_affected_hop_bound_exceeded",
    "g2e_affected_node_bound_exceeded",
    "g2e_affected_proof_invalid",
    "g2e_invalidation_record_invalid",
    "g2e_invalidation_reason_invalid",
    "g2e_invalidation_deletion_forbidden",
    "g2e_invalidation_history_mutation",
    "g2e_invalidation_predecessor_mismatch",
    "g2e_invalidation_supersession_mismatch",
    "g2e_invalidation_g2a_root_binding_required",
    "g2e_invalidation_g2b_reuse_still_current",
    "g2e_preservation_proof_invalid",
    "g2e_preserved_artifact_changed",
    "g2e_preserved_identity_changed",
    "g2e_preservation_cache_mutation",
    "g2e_recomputation_plan_invalid",
    "g2e_route_revalidation_required",
    "g2e_topology_binding_mismatch",
    "g2e_recomputation_budget_exceeded",
    "g2e_recomputation_in_place_forbidden",
    "g2e_recomputation_result_invalid",
    "g2e_recomputation_no_progress",
    "g2e_repeated_delta_conflict",
    "g2e_transition_delta_validated",
    "g2e_transition_affected_set_derived",
    "g2e_transition_invalidation_derived",
    "g2e_transition_recomputation_plan_reviewed",
    "g2e_transition_recomputation_plan_accepted",
    "g2e_transition_recomputation_plan_rejected",
    "g2e_transition_selective_recomputation_executed",
    "g2e_transition_selective_recomputation_blocked",
    "g2e_transition_delta_parent_returned",
    "g2e_transition_delta_report_finalized",
    "g2e_delta_binding_set_mismatch",
    "g2e_delta_source_binding_set_mismatch",
    "g2e_dependency_edge_set_mismatch",
    "g2e_dependency_graph_basis_mismatch",
    "g2e_dependency_replay_edge_mismatch",
    "g2e_dependency_source_payload_unavailable",
)

VALIDATION_TARGETS_V01 = (
    "DeltaSourceBindingV01",
    "ChangedFieldBindingV01",
    "ChangedArtifactBindingV01",
    "WorldStateDeltaV01",
    "DependencyFingerprintProfileV01",
    "DeltaDependencyEdgeV01",
    "DependencyGraphIndexV01",
    "AffectedSetRequestV01",
    "AffectedSetResultV01",
    "ArtifactInvalidationRecordV01",
    "InvalidationReportV01",
    "PreservationProofV01",
    "SelectiveRecomputationPlanV01",
    "RecomputedArtifactBindingV01",
    "SelectiveRecomputationResultV01",
    "ContinuousDeltaRuntimeTraceV01",
    "ContinuousDeltaRuntimeReportV01",
    "ContinuousDeltaValidationReportV01",
    "ContinuousDeltaSourceContextV01",
    "ContinuousDeltaExecutionBundleV01",
    "delta_against_source_context",
    "dependency_fingerprint_against_sources",
    "dependency_graph_against_context",
    "affected_set_completeness",
    "invalidation_against_prior_slices",
    "preservation_against_artifacts",
    "selective_plan_against_sources",
    "recomputation_result_against_plan",
    "runtime_report_against_sources",
    "continuous_delta_abi_profile",
    "continuous_delta_transition_profile",
    "continuous_delta_stage_bundle",
)

FAILURE_STAGES_V01 = (
    "delta_source_structure",
    "delta_source_context",
    "changed_binding",
    "delta_time",
    "fingerprint_profile",
    "fingerprint_context",
    "dependency_edge",
    "dependency_graph",
    "graph_bounds",
    "affected_request",
    "affected_closure",
    "affected_completeness",
    "invalidation_record",
    "invalidation_prior_slice",
    "preservation",
    "route_revalidation",
    "topology_binding",
    "recomputation_plan",
    "recomputation_admission",
    "recomputation_execution",
    "post_vv",
    "gt",
    "parent_return",
    "bundle_final",
)


@dataclass(frozen=True)
class DeltaSourceBindingV01:
    source_binding_id: str
    binding_version: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    baseline_source_artifact_id: str
    baseline_source_artifact_type: str
    baseline_source_artifact_sha256: str
    baseline_source_payload_sha256: str
    observed_source_artifact_id: str
    observed_source_artifact_type: str
    observed_source_artifact_sha256: str
    observed_source_payload_sha256: str
    predecessor_relation: str
    baseline_report_id: str
    baseline_graph_id: str
    baseline_graph_version: str
    baseline_policy_version: str
    observed_policy_version: str
    baseline_schema_versions: tuple[str, ...]
    observed_schema_versions: tuple[str, ...]
    baseline_source_history_hash: str
    observed_source_history_hash: str
    valid_from_utc: str
    valid_to_utc: str
    trace_refs: tuple[str, ...]
    authority_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ChangedFieldBindingV01:
    changed_field_binding_id: str
    source_binding_id: str
    json_pointer: str
    prior_value_sha256: str
    observed_value_sha256: str
    change_class: str
    observed_at_utc: str
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class ChangedArtifactBindingV01:
    changed_artifact_binding_id: str
    source_binding_id: str
    baseline_artifact_id: str
    baseline_artifact_type: str
    baseline_payload_sha256: str
    observed_artifact_id: str
    observed_artifact_type: str
    observed_payload_sha256: str
    baseline_dependency_fingerprint: str
    observed_dependency_fingerprint: str
    predecessor_relation: str
    change_class: str
    observed_at_utc: str
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class WorldStateDeltaV01:
    delta_id: str
    delta_version: str
    delta_profile_id: str
    ordered_source_binding_ids: tuple[str, ...]
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    baseline_report_id: str
    baseline_graph_id: str
    baseline_graph_version: str
    delta_sequence: int
    prior_delta_id: str | None
    observed_at_utc: str
    valid_from_utc: str
    valid_to_utc: str
    baseline_policy_version: str
    observed_policy_version: str
    baseline_schema_versions: tuple[str, ...]
    observed_schema_versions: tuple[str, ...]
    baseline_source_history_hash: str
    observed_source_history_hash: str
    ordered_changed_field_binding_ids: tuple[str, ...]
    ordered_changed_artifact_binding_ids: tuple[str, ...]
    dependency_fingerprint_before: str
    dependency_fingerprint_after: str
    trace_refs: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class DependencyFingerprintProfileV01:
    fingerprint_profile_id: str
    fingerprint_profile_version: str
    hash_algorithm: str
    canonicalization_profile_id: str
    domain_separator: str
    typed_role: str
    ordered_preimage_fields: tuple[str, ...]
    cross_role_reuse_forbidden: bool


@dataclass(frozen=True)
class DeltaDependencyEdgeV01:
    edge_id: str
    graph_basis_sha256: str
    graph_version: str
    dependent_artifact_id: str
    dependency_artifact_id: str
    dependency_field_pointers: tuple[str, ...]
    edge_class: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    canonical_order: int
    source_replay_edge_sha256: str
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class DependencyGraphIndexV01:
    graph_id: str
    graph_version: str
    graph_basis_sha256: str
    source_manifest_id: str
    source_manifest_hash: str
    source_replay_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    ordered_node_ids: tuple[str, ...]
    ordered_edge_ids: tuple[str, ...]
    node_count: int
    edge_count: int
    max_nodes: int
    max_edges: int
    max_hops: int
    acyclic: bool
    source_history_hash: str
    policy_version: str
    schema_versions: tuple[str, ...]
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class AffectedSetRequestV01:
    affected_request_id: str
    delta_id: str
    graph_id: str
    graph_version: str
    baseline_report_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    ordered_changed_field_binding_ids: tuple[str, ...]
    ordered_changed_artifact_binding_ids: tuple[str, ...]
    max_nodes: int
    max_edges: int
    max_hops: int
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class AffectedSetResultV01:
    affected_set_id: str
    affected_request_id: str
    delta_id: str
    graph_id: str
    graph_version: str
    ordered_changed_node_ids: tuple[str, ...]
    ordered_directly_affected_ids: tuple[str, ...]
    ordered_transitively_affected_ids: tuple[str, ...]
    ordered_affected_ids: tuple[str, ...]
    ordered_unaffected_ids: tuple[str, ...]
    closure_proof_sha256: str
    visited_node_count: int
    traversed_edge_count: int
    maximum_observed_hops: int
    complete: bool
    minimal: bool
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class ArtifactInvalidationRecordV01:
    invalidation_record_id: str
    affected_set_id: str
    artifact_id: str
    artifact_type: str
    current_eligible_before: bool
    current_eligible_after: bool
    invalidation_reason_class: str
    triggering_delta_id: str
    triggering_binding_ids: tuple[str, ...]
    predecessor_artifact_id: str
    superseded_by_artifact_id: str | None
    g2a_packet_relation: str
    g2b_reuse_relation: str
    g2c_route_relation: str
    root_review_required: bool
    historical_artifact_preserved: bool
    deleted: bool
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class InvalidationReportV01:
    invalidation_report_id: str
    affected_set_id: str
    ordered_invalidation_record_ids: tuple[str, ...]
    ordered_invalidated_artifact_ids: tuple[str, ...]
    ordered_historical_artifact_ids: tuple[str, ...]
    ordered_unresolved_artifact_ids: tuple[str, ...]
    ordered_packet_invalidation_candidate_ids: tuple[str, ...]
    ordered_stale_reuse_certificate_ids: tuple[str, ...]
    ordered_route_revalidation_ids: tuple[str, ...]
    report_status: str
    reason_codes: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class PreservationProofV01:
    preservation_proof_id: str
    baseline_graph_id: str
    affected_set_id: str
    ordered_preserved_artifact_ids: tuple[str, ...]
    ordered_before_artifact_sha256: tuple[str, ...]
    ordered_after_artifact_sha256: tuple[str, ...]
    ordered_before_payload_sha256: tuple[str, ...]
    ordered_after_payload_sha256: tuple[str, ...]
    ordered_before_identity_ids: tuple[str, ...]
    ordered_after_identity_ids: tuple[str, ...]
    before_cache_state_sha256: str
    after_cache_state_sha256: str
    mutable_global_write_count: int
    byte_identity_preserved: bool
    object_identity_used_as_proof: bool
    proof_sha256: str
    status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class SelectiveRecomputationPlanV01:
    recomputation_plan_id: str
    delta_id: str
    affected_set_id: str
    invalidation_report_id: str
    source_route_eligibility_artifact_id: str
    source_topology_id: str
    accepted_mode: str
    accepted_scope_ref: str
    ordered_affected_cell_ids: tuple[str, ...]
    ordered_affected_artifact_ids: tuple[str, ...]
    ordered_work_node_ids: tuple[str, ...]
    ordered_preserved_artifact_ids: tuple[str, ...]
    max_work_items: int
    max_queue_entries: int
    max_wall_time_units: int
    max_token_budget: int
    max_provider_calls: int
    transition_profile_id: str
    root_review_required: bool
    plan_status: str
    reason_codes: tuple[str, ...]
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class RecomputedArtifactBindingV01:
    recomputed_binding_id: str
    recomputation_plan_id: str
    prior_artifact_id: str
    prior_payload_sha256: str
    new_artifact_id: str
    new_payload_sha256: str
    predecessor_relation: str
    supersession_relation: str
    derivation_refs: tuple[str, ...]
    source_cell_id: str
    source_queue_entry_id: str
    g2d_cell_result_ref: str
    g2d_runtime_report_ref: str
    trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class SelectiveRecomputationResultV01:
    recomputation_result_id: str
    recomputation_plan_id: str
    baseline_runtime_report_id: str
    recomputed_runtime_report_id: str
    preservation_proof_id: str
    ordered_recomputed_binding_ids: tuple[str, ...]
    ordered_invalidated_downstream_ids: tuple[str, ...]
    ordered_recomputed_artifact_ids: tuple[str, ...]
    ordered_preserved_artifact_ids: tuple[str, ...]
    ordered_unresolved_artifact_ids: tuple[str, ...]
    ordered_partial_failure_ids: tuple[str, ...]
    parent_return_transition_decision_id: str
    result_status: str
    reason_codes: tuple[str, ...]
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    final_outputs_created: int
    drs_writes: int
    authority_created_count: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ContinuousDeltaRuntimeTraceV01:
    trace_id: str
    delta_id: str
    graph_id: str
    affected_set_id: str
    invalidation_report_id: str
    preservation_proof_id: str
    recomputation_plan_id: str
    recomputation_result_id: str
    plan_root_decision_input_id: str
    plan_root_decision_id: str
    final_root_decision_input_id: str
    final_root_decision_id: str
    ordered_transition_decision_ids: tuple[str, ...]
    ordered_causal_ref_ids: tuple[str, ...]
    ordered_source_artifact_ids: tuple[str, ...]
    ordered_downstream_artifact_ids: tuple[str, ...]
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ContinuousDeltaRuntimeReportV01:
    report_id: str
    report_version: str
    profile_id: str
    ordered_source_binding_ids: tuple[str, ...]
    baseline_report_id: str
    delta_id: str
    graph_id: str
    affected_set_id: str
    invalidation_report_id: str
    preservation_proof_id: str
    recomputation_plan_id: str
    recomputation_result_id: str
    trace_id: str
    plan_root_decision_input_id: str
    plan_root_decision_id: str
    final_root_decision_input_id: str
    final_root_decision_id: str
    changed_count: int
    directly_affected_count: int
    transitively_affected_count: int
    invalidated_count: int
    recomputed_count: int
    preserved_count: int
    unresolved_count: int
    report_status: str
    reason_codes: tuple[str, ...]
    root_review_required: bool
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    final_outputs_created: int
    drs_writes: int
    authority_created_count: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ContinuousDeltaValidationReportV01:
    validation_report_id: str
    validation_target: str
    validated_object_id: str | None
    status: str
    failure_stage: str
    reason_codes: tuple[str, ...]
    source_reason_codes: tuple[str, ...]
    return_to_root_required: bool
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ContinuousDeltaSourceContextV01:
    integrity_manifest: ArtifactManifestV01
    integrity_replay: ReplayVerificationResultV01
    baseline_source_artifacts: tuple[KernelArtifactV01, ...]
    observed_source_artifacts: tuple[KernelArtifactV01, ...]
    g2a_registry: object
    g2a_packet: object
    g2a_dependency_candidate: object
    g2a_current_observations: tuple[object, ...]
    g2a_root_invalidation_material: object
    g2b_resolution_report: object
    g2b_reuse_certificate: object
    g2b_writeback_evidence: object
    g2c_source_context: ExecutionModeSourceContextV01
    baseline_g2c_route_eligibility_artifact: KernelArtifactV01
    baseline_g2d_execution_bundle: FractalRuntimeExecutionBundleV02
    root_kernel: RootDecisionKernelV01
    post_vv_profile: object
    gt_profile: object


@dataclass(frozen=True)
class ContinuousDeltaExecutionBundleV01:
    source_context: ContinuousDeltaSourceContextV01
    source_bindings: tuple[DeltaSourceBindingV01, ...]
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...]
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...]
    delta: WorldStateDeltaV01
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...]
    dependency_graph: DependencyGraphIndexV01
    affected_request: AffectedSetRequestV01
    affected_result: AffectedSetResultV01
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...]
    invalidation_report: InvalidationReportV01
    delta_source_proposed_artifact: KernelArtifactV01
    delta_source_artifact: KernelArtifactV01
    dependency_graph_artifact: KernelArtifactV01
    affected_set_artifact: KernelArtifactV01
    invalidation_report_artifact: KernelArtifactV01
    recomputation_plan: SelectiveRecomputationPlanV01
    plan_proposed_artifact: KernelArtifactV01
    plan_root_decision_input: RootDecisionInputV01
    plan_root_decision_result: RootDecisionResultV01
    plan_root_decision_artifact: KernelArtifactV01
    plan_accepted_artifact: KernelArtifactV01
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...]
    preservation_proof: PreservationProofV01
    preservation_proof_artifact: KernelArtifactV01
    recomputation_result: SelectiveRecomputationResultV01
    g2e_validation_reports: tuple[ContinuousDeltaValidationReportV01, ...]
    g2e_transition_decisions: tuple[TransitionDecisionV01, ...]
    g2e_causal_consumption_refs: tuple[CausalConsumptionRefV01, ...]
    final_root_decision_input: RootDecisionInputV01
    final_root_decision_result: RootDecisionResultV01
    final_root_decision_artifact: KernelArtifactV01
    runtime_trace: ContinuousDeltaRuntimeTraceV01
    runtime_report: ContinuousDeltaRuntimeReportV01
    runtime_report_artifact: KernelArtifactV01


CONTINUOUS_DELTA_TYPES_V01 = (
    DeltaSourceBindingV01,
    ChangedFieldBindingV01,
    ChangedArtifactBindingV01,
    WorldStateDeltaV01,
    DependencyFingerprintProfileV01,
    DeltaDependencyEdgeV01,
    DependencyGraphIndexV01,
    AffectedSetRequestV01,
    AffectedSetResultV01,
    ArtifactInvalidationRecordV01,
    InvalidationReportV01,
    PreservationProofV01,
    SelectiveRecomputationPlanV01,
    RecomputedArtifactBindingV01,
    SelectiveRecomputationResultV01,
    ContinuousDeltaRuntimeTraceV01,
    ContinuousDeltaRuntimeReportV01,
    ContinuousDeltaValidationReportV01,
    ContinuousDeltaSourceContextV01,
    ContinuousDeltaExecutionBundleV01,
)
SERIALIZED_CONTINUOUS_DELTA_TYPES_V01 = CONTINUOUS_DELTA_TYPES_V01[:18]
RUNTIME_ONLY_CONTINUOUS_DELTA_TYPES_V01 = CONTINUOUS_DELTA_TYPES_V01[18:]
CONTINUOUS_DELTA_FIELD_NAMES_V01 = tuple(
    (value_type.__name__, tuple(field.name for field in fields(value_type)))
    for value_type in CONTINUOUS_DELTA_TYPES_V01
)

CONTINUOUS_DELTA_IDENTITY_PROFILES_V01 = (
    ("DeltaSourceBindingV01", "delta_source_binding", "source_binding_id", "g2e_delta_source_binding_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00DeltaSourceBindingV01\x00"),
    ("ChangedFieldBindingV01", "changed_field_binding", "changed_field_binding_id", "g2e_changed_field_binding_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ChangedFieldBindingV01\x00"),
    ("ChangedArtifactBindingV01", "changed_artifact_binding", "changed_artifact_binding_id", "g2e_changed_artifact_binding_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ChangedArtifactBindingV01\x00"),
    ("WorldStateDeltaV01", "world_state_delta", "delta_id", "g2e_world_state_delta_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00WorldStateDeltaV01\x00"),
    ("DependencyFingerprintProfileV01", "dependency_fingerprint_profile", "fingerprint_profile_id", "g2e_dependency_fingerprint_profile_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00DependencyFingerprintProfileV01\x00"),
    ("DeltaDependencyEdgeV01", "delta_dependency_edge", "edge_id", "g2e_delta_dependency_edge_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00DeltaDependencyEdgeV01\x00"),
    ("DependencyGraphIndexV01", "dependency_graph_index", "graph_id", "g2e_dependency_graph_index_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00DependencyGraphIndexV01\x00"),
    ("AffectedSetRequestV01", "affected_set_request", "affected_request_id", "g2e_affected_set_request_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00AffectedSetRequestV01\x00"),
    ("AffectedSetResultV01", "affected_set_result", "affected_set_id", "g2e_affected_set_result_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00AffectedSetResultV01\x00"),
    ("ArtifactInvalidationRecordV01", "artifact_invalidation_record", "invalidation_record_id", "g2e_artifact_invalidation_record_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ArtifactInvalidationRecordV01\x00"),
    ("InvalidationReportV01", "invalidation_report", "invalidation_report_id", "g2e_invalidation_report_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00InvalidationReportV01\x00"),
    ("PreservationProofV01", "preservation_proof", "preservation_proof_id", "g2e_preservation_proof_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00PreservationProofV01\x00"),
    ("SelectiveRecomputationPlanV01", "selective_recomputation_plan", "recomputation_plan_id", "g2e_selective_recomputation_plan_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00SelectiveRecomputationPlanV01\x00"),
    ("RecomputedArtifactBindingV01", "recomputed_artifact_binding", "recomputed_binding_id", "g2e_recomputed_artifact_binding_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00RecomputedArtifactBindingV01\x00"),
    ("SelectiveRecomputationResultV01", "selective_recomputation_result", "recomputation_result_id", "g2e_selective_recomputation_result_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00SelectiveRecomputationResultV01\x00"),
    ("ContinuousDeltaRuntimeTraceV01", "continuous_delta_runtime_trace", "trace_id", "g2e_continuous_delta_runtime_trace_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ContinuousDeltaRuntimeTraceV01\x00"),
    ("ContinuousDeltaRuntimeReportV01", "continuous_delta_runtime_report", "report_id", "g2e_continuous_delta_runtime_report_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ContinuousDeltaRuntimeReportV01\x00"),
    ("ContinuousDeltaValidationReportV01", "continuous_delta_validation_report", "validation_report_id", "g2e_continuous_delta_validation_report_v01:", b"HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00ContinuousDeltaValidationReportV01\x00"),
)

DEPENDENCY_FINGERPRINT_PREIMAGE_FIELDS_V01 = (
    "domain_separator",
    "fingerprint_profile_id",
    "fingerprint_profile_version",
    "typed_role",
    "hash_algorithm",
    "canonicalization_profile_id",
    "graph_id",
    "graph_basis_sha256",
    "graph_version",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "policy_version",
    "schema_versions",
    "source_history_hash",
    "ordered_dependency_rows",
    "ordered_source_artifacts",
)

G2E_ABI_ARTIFACT_TYPES_V01 = (
    "ContinuousDeltaSource",
    "DependencyGraphIndex",
    "AffectedSetResult",
    "ArtifactInvalidationReport",
    "PreservationProof",
    "SelectiveRecomputationPlan",
    "ContinuousDeltaRuntimeReport",
)

G2E_ABI_ARTIFACT_INSTANCE_PROFILES_V01 = (
    ("delta_source_proposed", "ContinuousDeltaSource", "WorldStateDeltaV01", "PROPOSED", "NON_AUTHORITY", "continuous_delta_runtime_v01", "g2eabi_source_proposed_v01:", "HEDGEHOG_G2E_CONTINUOUS_DELTA_SOURCE_PROPOSED_ARTIFACT_V01", "G2-E1"),
    ("delta_source_validated", "ContinuousDeltaSource", "WorldStateDeltaV01", "VALIDATED", "NON_AUTHORITY", "continuous_delta_runtime_v01", "g2eabi_source_validated_v01:", "HEDGEHOG_G2E_CONTINUOUS_DELTA_SOURCE_VALIDATED_ARTIFACT_V01", "G2-E1"),
    ("dependency_graph_validated", "DependencyGraphIndex", "DependencyGraphIndexV01", "VALIDATED", "NON_AUTHORITY", "continuous_delta_runtime_v01", "g2eabi_graph_v01:", "HEDGEHOG_G2E_DEPENDENCY_GRAPH_INDEX_ARTIFACT_V01", "G2-E2"),
    ("affected_set_validated", "AffectedSetResult", "AffectedSetResultV01", "VALIDATED", "NON_AUTHORITY", "continuous_delta_runtime_v01", "g2eabi_affected_v01:", "HEDGEHOG_G2E_AFFECTED_SET_RESULT_ARTIFACT_V01", "G2-E2"),
    ("invalidation_report_validated", "ArtifactInvalidationReport", "InvalidationReportV01", "VALIDATED", "NON_AUTHORITY", "continuous_delta_runtime_v01", "g2eabi_invalidation_v01:", "HEDGEHOG_G2E_ARTIFACT_INVALIDATION_REPORT_ARTIFACT_V01", "G2-E3"),
    ("plan_proposed", "SelectiveRecomputationPlan", "SelectiveRecomputationPlanV01", "PROPOSED", "ADVISORY", "continuous_delta_runtime_v01", "g2eabi_plan_proposed_v01:", "HEDGEHOG_G2E_SELECTIVE_RECOMPUTATION_PLAN_PROPOSED_ARTIFACT_V01", "G2-E4"),
    ("plan_root_accepted", "SelectiveRecomputationPlan", "SelectiveRecomputationPlanV01", "ROOT_ACCEPTED", "ADVISORY", "continuous_delta_runtime_v01", "g2eabi_plan_accepted_v01:", "HEDGEHOG_G2E_SELECTIVE_RECOMPUTATION_PLAN_ACCEPTED_ARTIFACT_V01", "G2-E4"),
    ("preservation_proof_validated", "PreservationProof", "PreservationProofV01", "VALIDATED", "EVIDENCE_ONLY", "continuous_delta_runtime_v01", "g2eabi_preservation_v01:", "HEDGEHOG_G2E_PRESERVATION_PROOF_ARTIFACT_V01", "G2-E3/E4"),
    ("runtime_report_finalized", "ContinuousDeltaRuntimeReport", "ContinuousDeltaRuntimeReportV01", "FINALIZED", "EVIDENCE_ONLY", "continuous_delta_runtime_v01", "g2eabi_report_v01:", "HEDGEHOG_G2E_CONTINUOUS_DELTA_RUNTIME_REPORT_ARTIFACT_V01", "G2-E4"),
)

_G2E_ABI_PAYLOAD_OMISSIONS_V01 = (
    ("delta_source_proposed", ("transaction_id", "trace_refs")),
    ("delta_source_validated", ("transaction_id", "trace_refs")),
    ("dependency_graph_validated", ("transaction_id", "trace_refs")),
    ("affected_set_validated", ("trace_refs",)),
    ("invalidation_report_validated", ()),
    ("plan_proposed", ("trace_refs",)),
    ("plan_root_accepted", ("trace_refs",)),
    ("preservation_proof_validated", ()),
    ("runtime_report_finalized", ()),
)

_DELTA_POLICY_SCHEMA_SOURCE_V01 = (
    ("schema_version", "v0.1"),
    ("policy_version", "delta.observed_policy_version"),
    ("schema_versions", "delta.observed_schema_versions"),
)
_GRAPH_POLICY_SCHEMA_SOURCE_V01 = (
    ("schema_version", "v0.1"),
    ("policy_version", "graph.policy_version"),
    ("schema_versions", "graph.schema_versions"),
)
_BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01 = (
    ("ct_session_anchor", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.ct_session_anchor"),
    ("freshness_class", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.freshness_class"),
    ("kt_asof", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.kt_asof"),
    ("ttl_seconds", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.ttl_seconds"),
    ("et_observed_at", "delta.observed_at_utc"),
    ("pt_created_at", "delta.observed_at_utc"),
    ("valid_from", "delta.valid_from_utc"),
    ("valid_to", "delta.valid_to_utc"),
)
_RECOMPUTED_G2D_REPORT_TIME_ENVELOPE_SOURCE_V01 = (
    ("ct_session_anchor", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.ct_session_anchor"),
    ("freshness_class", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.freshness_class"),
    ("kt_asof", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.kt_asof"),
    ("ttl_seconds", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.ttl_seconds"),
    ("et_observed_at", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.et_observed_at"),
    ("pt_created_at", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.pt_created_at"),
    ("valid_from", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.valid_from"),
    ("valid_to", "recomputed_g2d_execution_bundle.report_artifact.time_envelope.valid_to"),
)

G2E_ABI_ARTIFACT_PROFILES_V01 = (
    ("ContinuousDeltaSource", "WorldStateDeltaV01", ("PROPOSED", "VALIDATED"), "NON_AUTHORITY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(WorldStateDeltaV01)), (("PROPOSED", ("baseline_route_artifact", "baseline_g2d_report_artifact", "baseline_source_artifacts_manifest_order", "observed_source_artifacts_matching_order")), ("VALIDATED", ("proposed_source_artifact", "baseline_route_artifact", "baseline_g2d_report_artifact", "baseline_source_artifacts_manifest_order", "observed_source_artifacts_matching_order"))), (("PROPOSED", ("delta.trace_refs", "ordered_source_binding_ids")), ("VALIDATED", ("proposed_source_artifact_id", "t01_decision_id", "delta.trace_refs", "ordered_source_binding_ids"))), _DELTA_POLICY_SCHEMA_SOURCE_V01, _BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01, "G2-E1", 2),
    ("DependencyGraphIndex", "DependencyGraphIndexV01", ("VALIDATED",), "NON_AUTHORITY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(DependencyGraphIndexV01)), (("VALIDATED", ("validated_delta_source_artifact", "baseline_source_artifacts_manifest_order")),), (("VALIDATED", ("graph.trace_refs", "source_manifest_id", "source_replay_id")),), _GRAPH_POLICY_SCHEMA_SOURCE_V01, _BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01, "G2-E2", 1),
    ("AffectedSetResult", "AffectedSetResultV01", ("VALIDATED",), "NON_AUTHORITY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(AffectedSetResultV01)), (("VALIDATED", ("validated_delta_source_artifact", "dependency_graph_artifact")),), (("VALIDATED", ("affected_result.trace_refs", "t02_decision_id", "delta_id", "graph_id")),), _DELTA_POLICY_SCHEMA_SOURCE_V01, _BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01, "G2-E2", 1),
    ("ArtifactInvalidationReport", "InvalidationReportV01", ("VALIDATED",), "NON_AUTHORITY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(InvalidationReportV01)), (("VALIDATED", ("affected_set_artifact", "validated_delta_source_artifact", "dependency_graph_artifact")),), (("VALIDATED", ("affected_set_id", "t03_decision_id", "ordered_invalidation_record_ids", "reason_codes")),), _DELTA_POLICY_SCHEMA_SOURCE_V01, _BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01, "G2-E3", 1),
    ("PreservationProof", "PreservationProofV01", ("VALIDATED",), "EVIDENCE_ONLY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(PreservationProofV01)), (("VALIDATED", ("root_accepted_plan_artifact", "invalidation_report_artifact", "recomputed_g2d_report_artifact")),), (("VALIDATED", ("affected_set_id", "ordered_preserved_artifact_ids", "recomputed_g2d_runtime_trace_id")),), _DELTA_POLICY_SCHEMA_SOURCE_V01, _RECOMPUTED_G2D_REPORT_TIME_ENVELOPE_SOURCE_V01, "G2-E3/E4", 1),
    ("SelectiveRecomputationPlan", "SelectiveRecomputationPlanV01", ("PROPOSED", "ROOT_ACCEPTED"), "ADVISORY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(SelectiveRecomputationPlanV01)), (("PROPOSED", ("invalidation_report_artifact", "affected_set_artifact", "dependency_graph_artifact", "baseline_route_artifact", "baseline_g2d_report_artifact")), ("ROOT_ACCEPTED", ("proposed_plan_artifact", "plan_root_decision_artifact"))), (("PROPOSED", ("plan.trace_refs", "delta_affected_invalidation_route_topology_ids")), ("ROOT_ACCEPTED", ("proposed_plan_artifact_id", "plan_root_input_id", "plan_root_decision_id", "t04_id", "t05_id"))), _DELTA_POLICY_SCHEMA_SOURCE_V01, _BASELINE_ROUTE_DELTA_TIME_ENVELOPE_SOURCE_V01, "G2-E4", 2),
    ("ContinuousDeltaRuntimeReport", "ContinuousDeltaRuntimeReportV01", ("FINALIZED",), "EVIDENCE_ONLY", "continuous_delta_runtime_v01", tuple(field.name for field in fields(ContinuousDeltaRuntimeReportV01)), (("FINALIZED", ("root_accepted_plan_artifact", "recomputed_g2d_report_artifact", "preservation_proof_artifact", "final_root_decision_artifact", "invalidation_report_artifact")),), (("FINALIZED", ("runtime_trace_id", "plan_root_decision_id", "final_root_decision_id", "recomputed_g2d_runtime_report_id")),), _DELTA_POLICY_SCHEMA_SOURCE_V01, _RECOMPUTED_G2D_REPORT_TIME_ENVELOPE_SOURCE_V01, "G2-E4", 1),
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
_TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{0,255}$")
_ZERO_SHA256 = "0" * 64


def _identity_profile(value_type: type[object]) -> tuple[str, str, str, str, bytes]:
    for row in CONTINUOUS_DELTA_IDENTITY_PROFILES_V01:
        if row[0] == value_type.__name__:
            return row
    raise ValueError("g2e_identity_invalid")


def _plain_value(value: object) -> object:
    if value is None or type(value) in {str, int, bool}:
        return value
    if type(value) is tuple:
        return [_plain_value(item) for item in value]
    raise ValueError("g2e_object_invalid")


def _plain_data_unchecked(value: object, *, omit_identity: bool = False) -> dict[str, object]:
    value_type = type(value)
    if value_type not in SERIALIZED_CONTINUOUS_DELTA_TYPES_V01:
        raise ValueError("g2e_object_invalid")
    _type_name, _stem, identity_field, _prefix, _domain = _identity_profile(value_type)
    output: dict[str, object] = {}
    for field in fields(value_type):
        if omit_identity and field.name == identity_field:
            continue
        output[field.name] = _plain_value(getattr(value, field.name))
    canonical_json_bytes_v01(output)
    return output


def _rebuild_identity_unchecked(value: object) -> str:
    value_type = type(value)
    type_name, _stem, identity_field, prefix, domain_bytes = _identity_profile(value_type)
    ordered_material = []
    for field in fields(value_type):
        if field.name == identity_field:
            continue
        ordered_material.append([field.name, _plain_value(getattr(value, field.name))])
    if type_name != value_type.__name__:
        raise ValueError("g2e_identity_invalid")
    digest = hashlib.sha256(
        domain_bytes + canonical_json_bytes_v01(ordered_material)
    ).hexdigest()
    return prefix + digest


def _finish_identity(value: object) -> object:
    _type_name, _stem, identity_field, _prefix, _domain = _identity_profile(type(value))
    return replace(value, **{identity_field: _rebuild_identity_unchecked(value)})


def _text_valid(value: object, *, allow_empty: bool = False) -> bool:
    if type(value) is not str or len(value) > 512 or (not value and not allow_empty):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return (
        unicodedata.normalize("NFC", value) == value
        and "\x00" not in value
        and not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value)
    )


def _token_valid(value: object) -> bool:
    return _text_valid(value) and _TOKEN_PATTERN.fullmatch(value) is not None


def _sha256_valid(value: object) -> bool:
    return type(value) is str and _SHA256_PATTERN.fullmatch(value) is not None


def _parse_aware_timestamp_v01(value: object) -> datetime:
    if type(value) is not str or _TIMESTAMP_PATTERN.fullmatch(value) is None:
        raise ValueError("g2e_delta_time_invalid")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("g2e_delta_time_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("g2e_delta_time_invalid")
    return parsed


def _timestamp_valid(value: object) -> bool:
    try:
        _parse_aware_timestamp_v01(value)
    except ValueError:
        return False
    return True


def _text_tuple_valid(
    value: object,
    *,
    minimum: int = 0,
    maximum: int = 256,
    unique: bool = True,
) -> bool:
    return (
        type(value) is tuple
        and minimum <= len(value) <= maximum
        and all(_text_valid(item) for item in value)
        and (not unique or len(value) == len(set(value)))
    )


def _prefixed_identity_valid(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and re.fullmatch(re.escape(prefix) + r"[0-9a-f]{64}", value) is not None
    )


def _json_pointer_valid(value: object) -> bool:
    if type(value) is not str or not _text_valid(value, allow_empty=True):
        return False
    if value == "":
        return True
    if not value.startswith("/"):
        return False
    index = 0
    while index < len(value):
        if value[index] == "~":
            if index + 1 >= len(value) or value[index + 1] not in "01":
                return False
            index += 2
        else:
            index += 1
    return True


def _ordered_public_reasons_valid(value: object) -> bool:
    if type(value) is not tuple or len(value) != len(set(value)):
        return False
    try:
        positions = tuple(PUBLIC_G2E_REASON_CODES_V01.index(item) for item in value)
    except (ValueError, TypeError):
        return False
    return positions == tuple(sorted(positions))


def _ordered_reasons(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    present = frozenset(item for item in values if item in PUBLIC_G2E_REASON_CODES_V01)
    return tuple(item for item in PUBLIC_G2E_REASON_CODES_V01 if item in present)


def _identity_errors(value: object) -> tuple[str, ...]:
    try:
        _type_name, _stem, identity_field, prefix, _domain = _identity_profile(type(value))
        identity = getattr(value, identity_field)
        if not _prefixed_identity_valid(identity, prefix):
            return ("g2e_identity_invalid",)
        if identity != _rebuild_identity_unchecked(value):
            return ("g2e_identity_mismatch",)
        return ()
    except Exception:
        return ("g2e_identity_invalid",)


def _zero_boundary_errors(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name in (
        "permission_created",
        "action_commit_packet_created",
        "receipt_created",
        "final_output_created",
        "drs_write_created",
    ):
        if hasattr(value, field_name) and getattr(value, field_name) is not False:
            errors.append("g2e_zero_operation_boundary_violated")
    if hasattr(value, "authority_created") and getattr(value, "authority_created") is not False:
        errors.append("g2e_authority_boundary_violated")
    if hasattr(value, "real_world_effects_count") and (
        type(getattr(value, "real_world_effects_count")) is not int
        or getattr(value, "real_world_effects_count") != 0
    ):
        errors.append("g2e_zero_operation_boundary_violated")
    return _ordered_reasons(errors)


def _delta_source_binding_errors(value: object) -> tuple[str, ...]:
    if type(value) is not DeltaSourceBindingV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    text_fields = (
        value.request_id, value.transaction_id, value.owning_root_id, value.domain_id,
        value.baseline_source_artifact_id, value.baseline_source_artifact_type,
        value.observed_source_artifact_id, value.observed_source_artifact_type,
        value.baseline_report_id, value.baseline_graph_id, value.baseline_graph_version,
        value.baseline_policy_version, value.observed_policy_version,
    )
    if any(not _text_valid(item) for item in text_fields):
        errors.append("g2e_delta_source_invalid")
    if value.binding_version != DELTA_SOURCE_BINDING_VERSION_V01:
        errors.append("g2e_version_unsupported")
    if value.predecessor_relation != OBSERVED_SUCCESSOR_RELATION_V01:
        errors.append("g2e_delta_artifact_binding_invalid")
    if (
        value.baseline_source_artifact_id == value.observed_source_artifact_id
        or value.baseline_source_artifact_sha256 == value.observed_source_artifact_sha256
        or value.baseline_source_artifact_type != value.observed_source_artifact_type
    ):
        errors.append("g2e_delta_artifact_binding_invalid")
    for digest in (
        value.baseline_source_artifact_sha256,
        value.baseline_source_payload_sha256,
        value.observed_source_artifact_sha256,
        value.observed_source_payload_sha256,
        value.baseline_source_history_hash,
        value.observed_source_history_hash,
    ):
        if not _sha256_valid(digest):
            errors.append("g2e_delta_source_invalid")
    if not _text_tuple_valid(value.baseline_schema_versions, minimum=1, maximum=64):
        errors.append("g2e_delta_schema_version_mismatch")
    if not _text_tuple_valid(value.observed_schema_versions, minimum=1, maximum=64):
        errors.append("g2e_delta_schema_version_mismatch")
    if not _text_tuple_valid(value.trace_refs):
        errors.append("g2e_delta_source_invalid")
    if not _timestamp_valid(value.valid_from_utc) or not _timestamp_valid(value.valid_to_utc):
        errors.append("g2e_delta_time_invalid")
    errors.extend(_zero_boundary_errors(value))
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _changed_field_binding_errors(value: object) -> tuple[str, ...]:
    if type(value) is not ChangedFieldBindingV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if not _prefixed_identity_valid(value.source_binding_id, "g2e_delta_source_binding_v01:"):
        errors.append("g2e_delta_source_invalid")
    if not _json_pointer_valid(value.json_pointer):
        errors.append("g2e_delta_field_path_invalid")
    if not _sha256_valid(value.prior_value_sha256) or not _sha256_valid(value.observed_value_sha256):
        errors.append("g2e_delta_artifact_binding_invalid")
    elif value.prior_value_sha256 == value.observed_value_sha256:
        errors.append("g2e_delta_artifact_binding_invalid")
    if not _token_valid(value.change_class):
        errors.append("g2e_delta_artifact_binding_invalid")
    if not _timestamp_valid(value.observed_at_utc):
        errors.append("g2e_delta_time_invalid")
    if not _text_tuple_valid(value.trace_refs):
        errors.append("g2e_delta_artifact_binding_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _changed_artifact_binding_errors(value: object) -> tuple[str, ...]:
    if type(value) is not ChangedArtifactBindingV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if not _prefixed_identity_valid(value.source_binding_id, "g2e_delta_source_binding_v01:"):
        errors.append("g2e_delta_source_invalid")
    if any(
        not _text_valid(item)
        for item in (
            value.baseline_artifact_id, value.baseline_artifact_type,
            value.observed_artifact_id, value.observed_artifact_type,
        )
    ):
        errors.append("g2e_delta_artifact_binding_invalid")
    if (
        value.baseline_artifact_id == value.observed_artifact_id
        or value.baseline_artifact_type != value.observed_artifact_type
        or value.predecessor_relation != OBSERVED_SUCCESSOR_RELATION_V01
    ):
        errors.append("g2e_delta_artifact_binding_invalid")
    for digest in (
        value.baseline_payload_sha256, value.observed_payload_sha256,
        value.baseline_dependency_fingerprint, value.observed_dependency_fingerprint,
    ):
        if not _sha256_valid(digest):
            errors.append("g2e_delta_artifact_binding_invalid")
    if not _token_valid(value.change_class):
        errors.append("g2e_delta_artifact_binding_invalid")
    if not _timestamp_valid(value.observed_at_utc):
        errors.append("g2e_delta_time_invalid")
    if not _text_tuple_valid(value.trace_refs):
        errors.append("g2e_delta_artifact_binding_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _world_state_delta_errors(value: object) -> tuple[str, ...]:
    if type(value) is not WorldStateDeltaV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if value.delta_version != WORLD_STATE_DELTA_VERSION_V01 or value.delta_profile_id != WORLD_STATE_DELTA_PROFILE_ID_V01:
        errors.append("g2e_version_unsupported")
    if (
        type(value.delta_sequence) is not int
        or value.delta_sequence != 1
        or value.prior_delta_id is not None
    ):
        errors.append("g2e_repeated_delta_conflict")
    if not _text_tuple_valid(value.ordered_source_binding_ids, minimum=1, maximum=MAX_CHANGED_BINDINGS_V01):
        errors.append("g2e_delta_source_binding_set_mismatch")
    elif any(not _prefixed_identity_valid(item, "g2e_delta_source_binding_v01:") for item in value.ordered_source_binding_ids):
        errors.append("g2e_delta_source_binding_set_mismatch")
    field_ids_valid = _text_tuple_valid(value.ordered_changed_field_binding_ids, maximum=MAX_CHANGED_BINDINGS_V01)
    artifact_ids_valid = _text_tuple_valid(value.ordered_changed_artifact_binding_ids, maximum=MAX_CHANGED_BINDINGS_V01)
    if not field_ids_valid or not artifact_ids_valid:
        errors.append("g2e_delta_binding_set_mismatch")
    elif (
        any(not _prefixed_identity_valid(item, "g2e_changed_field_binding_v01:") for item in value.ordered_changed_field_binding_ids)
        or any(not _prefixed_identity_valid(item, "g2e_changed_artifact_binding_v01:") for item in value.ordered_changed_artifact_binding_ids)
        or not (value.ordered_changed_field_binding_ids or value.ordered_changed_artifact_binding_ids)
        or len(value.ordered_changed_field_binding_ids) + len(value.ordered_changed_artifact_binding_ids) > MAX_CHANGED_BINDINGS_V01
    ):
        errors.append("g2e_delta_binding_set_mismatch")
    if any(
        not _text_valid(item)
        for item in (
            value.request_id, value.transaction_id, value.owning_root_id, value.domain_id,
            value.baseline_report_id, value.baseline_graph_id, value.baseline_graph_version,
            value.baseline_policy_version, value.observed_policy_version,
        )
    ):
        errors.append("g2e_delta_source_invalid")
    if not all(_timestamp_valid(item) for item in (value.observed_at_utc, value.valid_from_utc, value.valid_to_utc)):
        errors.append("g2e_delta_time_invalid")
    if not _text_tuple_valid(value.baseline_schema_versions, minimum=1, maximum=64) or not _text_tuple_valid(value.observed_schema_versions, minimum=1, maximum=64):
        errors.append("g2e_delta_schema_version_mismatch")
    for digest in (
        value.baseline_source_history_hash, value.observed_source_history_hash,
        value.dependency_fingerprint_before, value.dependency_fingerprint_after,
    ):
        if not _sha256_valid(digest):
            errors.append("g2e_dependency_fingerprint_mismatch")
    if not _text_tuple_valid(value.trace_refs):
        errors.append("g2e_delta_source_invalid")
    errors.extend(_zero_boundary_errors(value))
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _dependency_fingerprint_profile_errors(value: object) -> tuple[str, ...]:
    if type(value) is not DependencyFingerprintProfileV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if (
        value.fingerprint_profile_version != DEPENDENCY_FINGERPRINT_PROFILE_VERSION_V01
        or value.hash_algorithm != DEPENDENCY_FINGERPRINT_HASH_ALGORITHM_V01
        or value.canonicalization_profile_id != DEPENDENCY_FINGERPRINT_CANONICALIZATION_PROFILE_V01
        or value.domain_separator != DEPENDENCY_FINGERPRINT_DOMAIN_SEPARATOR_V01
        or value.typed_role != DEPENDENCY_FINGERPRINT_TYPED_ROLE_V01
        or value.ordered_preimage_fields != DEPENDENCY_FINGERPRINT_PREIMAGE_FIELDS_V01
        or value.cross_role_reuse_forbidden is not True
    ):
        errors.append("g2e_dependency_fingerprint_profile_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _validation_report_errors(value: object) -> tuple[str, ...]:
    if type(value) is not ContinuousDeltaValidationReportV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if value.validation_target not in VALIDATION_TARGETS_V01:
        errors.append("g2e_object_invalid")
    if value.failure_stage not in FAILURE_STAGES_V01:
        errors.append("g2e_status_invalid")
    if value.status not in VALIDATION_STATUSES_V01:
        errors.append("g2e_status_invalid")
    if value.validated_object_id is not None and not _text_valid(value.validated_object_id):
        errors.append("g2e_identity_invalid")
    if not _ordered_public_reasons_valid(value.reason_codes):
        errors.append("g2e_reason_codes_invalid")
    if not _text_tuple_valid(value.source_reason_codes):
        errors.append("g2e_reason_codes_invalid")
    expected_status = "PASS" if not value.reason_codes and not value.source_reason_codes else "FAIL_CLOSED"
    if expected_status == "PASS" and value.validated_object_id is None:
        errors.append("g2e_identity_invalid")
    if value.status != expected_status:
        errors.append("g2e_status_invalid")
    if type(value.return_to_root_required) is not bool or type(value.root_review_required) is not bool:
        errors.append("g2e_status_invalid")
    elif value.return_to_root_required is (value.status == "PASS"):
        errors.append("g2e_status_invalid")
    errors.extend(_zero_boundary_errors(value))
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _make_validation_report(
    *,
    validation_target: str,
    validated_object_id: str | None,
    failure_stage: str,
    reason_codes: tuple[str, ...],
    source_reason_codes: tuple[str, ...],
    return_to_root_required: bool,
    root_review_required: bool,
) -> ContinuousDeltaValidationReportV01:
    if validation_target not in VALIDATION_TARGETS_V01:
        raise ValueError("g2e_object_invalid")
    if failure_stage not in FAILURE_STAGES_V01:
        raise ValueError("g2e_status_invalid")
    if not _ordered_public_reasons_valid(reason_codes) or not _text_tuple_valid(source_reason_codes):
        raise ValueError("g2e_reason_codes_invalid")
    if type(return_to_root_required) is not bool or type(root_review_required) is not bool:
        raise ValueError("g2e_status_invalid")
    status = "PASS" if not reason_codes and not source_reason_codes else "FAIL_CLOSED"
    if (
        validated_object_id is not None
        and not _text_valid(validated_object_id)
    ) or (status == "PASS" and validated_object_id is None):
        raise ValueError("g2e_identity_invalid")
    if return_to_root_required is (status == "PASS"):
        raise ValueError("g2e_status_invalid")
    provisional = ContinuousDeltaValidationReportV01(
        validation_report_id="g2e_continuous_delta_validation_report_v01:" + _ZERO_SHA256,
        validation_target=validation_target,
        validated_object_id=validated_object_id,
        status=status,
        failure_stage=failure_stage,
        reason_codes=reason_codes,
        source_reason_codes=source_reason_codes,
        return_to_root_required=return_to_root_required,
        root_review_required=root_review_required,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)  # type: ignore[return-value]


def _structural_report(
    value: object,
    expected_type: type[object],
    failure_stage: str,
    error_function: object,
) -> ContinuousDeltaValidationReportV01:
    try:
        errors = error_function(value)
    except Exception:
        errors = ("g2e_object_invalid",)
    validated_id = None
    if not errors and type(value) is expected_type:
        _type_name, _stem, identity_field, _prefix, _domain = _identity_profile(expected_type)
        validated_id = getattr(value, identity_field)
    return _make_validation_report(
        validation_target=expected_type.__name__,
        validated_object_id=validated_id,
        failure_stage=failure_stage,
        reason_codes=errors,
        source_reason_codes=(),
        return_to_root_required=bool(errors),
        root_review_required=False,
    )


def _serialize(value: object, expected_type: type[object], error_function: object) -> dict[str, object]:
    errors = error_function(value)
    if errors:
        raise ValueError(errors[0])
    if type(value) is not expected_type:
        raise ValueError("g2e_object_invalid")
    return _plain_data_unchecked(value)


def _rebuild(value: object, expected_type: type[object]) -> str:
    if type(value) is not expected_type:
        raise ValueError("g2e_object_invalid")
    try:
        return _rebuild_identity_unchecked(value)
    except Exception:
        raise ValueError("g2e_identity_invalid") from None


def _require_built_valid(value: object, error_function: object) -> object:
    errors = error_function(value)
    if errors:
        raise ValueError(errors[0])
    return value


def _domain_sha256_v01(domain: str, material: object) -> str:
    return hashlib.sha256(
        domain.encode("ascii") + b"\x00" + canonical_json_bytes_v01(material)
    ).hexdigest()


def _artifact_plain_v01(artifact: KernelArtifactV01) -> dict[str, object]:
    if type(artifact) is not KernelArtifactV01 or validate_kernel_artifact_v01(
        artifact
    ):
        raise ValueError("g2e_delta_source_unvalidated")
    return kernel_artifact_to_plain_dict_v01(artifact)


def _artifact_payload_sha256_v01(artifact: KernelArtifactV01) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(_artifact_plain_v01(artifact)["payload"])
    ).hexdigest()


def _artifact_sha256_v01(artifact: KernelArtifactV01) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(_artifact_plain_v01(artifact))
    ).hexdigest()


def _source_manifest_id_v01(manifest: ArtifactManifestV01) -> str:
    return "integrity_manifest_v01:" + manifest.manifest_hash


def _contextual_report_v01(
    *,
    validation_target: str,
    validated_object_id: str | None,
    failure_stage: str,
    reason_codes: tuple[str, ...],
) -> ContinuousDeltaValidationReportV01:
    reasons = _ordered_reasons(reason_codes)
    return _make_validation_report(
        validation_target=validation_target,
        validated_object_id=validated_object_id if not reasons else None,
        failure_stage=failure_stage,
        reason_codes=reasons,
        source_reason_codes=(),
        return_to_root_required=bool(reasons),
        root_review_required=False,
    )


def _resolve_json_pointer_v01(value: object, pointer: str) -> object:
    if not _json_pointer_valid(pointer):
        raise ValueError("g2e_dependency_source_payload_unavailable")
    current = value
    if pointer == "":
        return current
    for encoded in pointer.split("/")[1:]:
        segment = encoded.replace("~1", "/").replace("~0", "~")
        if type(current) is dict:
            if segment not in current:
                raise ValueError("g2e_dependency_source_payload_unavailable")
            current = current[segment]
        elif type(current) is list:
            if (
                not segment.isdigit()
                or (len(segment) > 1 and segment.startswith("0"))
            ):
                raise ValueError("g2e_dependency_source_payload_unavailable")
            index = int(segment)
            if index >= len(current):
                raise ValueError("g2e_dependency_source_payload_unavailable")
            current = current[index]
        else:
            raise ValueError("g2e_dependency_source_payload_unavailable")
    return current


def _manifest_replay_source_errors_v01(
    *,
    manifest: object,
    replay: object,
    source_artifacts: object,
) -> tuple[str, ...]:
    try:
        if (
            type(manifest) is not ArtifactManifestV01
            or type(replay) is not ReplayVerificationResultV01
            or type(source_artifacts) is not tuple
            or not source_artifacts
            or any(type(item) is not KernelArtifactV01 for item in source_artifacts)
        ):
            return ("g2e_delta_source_unvalidated",)
        if len(source_artifacts) > MAX_DEPENDENCY_GRAPH_NODES_V01:
            return ("g2e_dependency_graph_bounds_exceeded",)
        plains = tuple(_artifact_plain_v01(item) for item in source_artifacts)
        refs = tuple(
            kernel_artifact_to_canonical_ref_v01(item) for item in source_artifacts
        )
        if refs != manifest.artifacts:
            return ("g2e_delta_source_unvalidated",)
        payload_rows = tuple(
            (artifact.artifact_id, plain["payload"])
            for artifact, plain in zip(source_artifacts, plains, strict=True)
        )
        manifest_result = verify_artifact_manifest_v01(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=manifest.manifest_hash,
        )
        expected_replay = verify_artifact_replay_v01(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=manifest.manifest_hash,
        )
        if (
            manifest_result.verification_status != "PASS"
            or expected_replay.replay_status != "PASS"
            or replay != expected_replay
            or replay.reconstructed_dependency_edges != manifest.dependency_edges
        ):
            return ("g2e_delta_source_unvalidated",)
        return ()
    except Exception:
        return ("g2e_delta_source_unvalidated",)


def _edge_descriptor_v01(
    edge: DeltaDependencyEdgeV01,
) -> tuple[str, str, tuple[str, ...], str]:
    return (
        edge.dependent_artifact_id,
        edge.dependency_artifact_id,
        edge.dependency_field_pointers,
        edge.edge_class,
    )


def _normalized_edge_descriptors_v01(
    descriptors: tuple[tuple[str, str, tuple[str, ...], str], ...],
    positions: dict[str, int],
) -> tuple[tuple[str, str, tuple[str, ...], str], ...]:
    return tuple(
        sorted(
            descriptors,
            key=lambda row: (
                positions[row[0]], positions[row[1]], row[2], row[3]
            ),
        )
    )


def _graph_basis_sha256_v01(
    *,
    graph_version: str,
    source_manifest_id: str,
    source_manifest_hash: str,
    source_replay_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    policy_version: str,
    schema_versions: tuple[str, ...],
    source_history_hash: str,
    source_artifacts: tuple[KernelArtifactV01, ...],
    replay_pairs: tuple[tuple[str, str], ...],
    normalized_descriptors: tuple[
        tuple[str, str, tuple[str, ...], str], ...
    ],
) -> str:
    material = (
        CONTINUOUS_DELTA_GRAPH_PROFILE_ID_V01,
        graph_version,
        source_manifest_id,
        source_manifest_hash,
        source_replay_id,
        transaction_id,
        owning_root_id,
        domain_id,
        policy_version,
        schema_versions,
        source_history_hash,
        tuple(
            (artifact.artifact_id, _artifact_payload_sha256_v01(artifact))
            for artifact in source_artifacts
        ),
        replay_pairs,
        normalized_descriptors,
    )
    return _domain_sha256_v01(GRAPH_BASIS_DOMAIN_V01, material)


def _source_replay_edge_sha256_v01(
    *,
    source_manifest_id: str,
    source_manifest_hash: str,
    source_replay_id: str,
    dependent_artifact_id: str,
    dependency_artifact_id: str,
    positions: dict[str, int],
) -> str:
    material = (
        source_manifest_id,
        source_manifest_hash,
        source_replay_id,
        dependent_artifact_id,
        dependency_artifact_id,
        positions[dependent_artifact_id],
        positions[dependency_artifact_id],
    )
    return _domain_sha256_v01(SOURCE_REPLAY_EDGE_DOMAIN_V01, material)


def _graph_has_cycle_v01(
    node_ids: tuple[str, ...],
    descriptors: tuple[tuple[str, str, tuple[str, ...], str], ...],
) -> bool:
    dependencies = {node_id: [] for node_id in node_ids}
    for dependent, dependency, _pointers, _edge_class in descriptors:
        dependencies[dependent].append(dependency)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        try:
            if any(visit(dependency) for dependency in dependencies[node_id]):
                return True
        finally:
            visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node_id) for node_id in node_ids)


def _delta_dependency_edge_errors(value: object) -> tuple[str, ...]:
    if type(value) is not DeltaDependencyEdgeV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if not _sha256_valid(value.graph_basis_sha256):
        errors.append("g2e_dependency_graph_basis_mismatch")
    if value.graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        errors.append("g2e_dependency_graph_version_mismatch")
    if not _text_valid(value.dependent_artifact_id):
        errors.append("g2e_dependency_edge_unknown_dependent")
    if not _text_valid(value.dependency_artifact_id):
        errors.append("g2e_dependency_edge_unknown_source")
    if value.dependent_artifact_id == value.dependency_artifact_id:
        errors.append("g2e_dependency_edge_self")
    if (
        type(value.dependency_field_pointers) is not tuple
        or len(value.dependency_field_pointers) > MAX_DEPENDENCY_GRAPH_NODES_V01
        or len(value.dependency_field_pointers)
        != len(set(value.dependency_field_pointers))
        or any(
            not _json_pointer_valid(pointer)
            for pointer in value.dependency_field_pointers
        )
    ):
        errors.append("g2e_dependency_edge_invalid")
    if not _token_valid(value.edge_class):
        errors.append("g2e_dependency_edge_invalid")
    if any(
        not _text_valid(item)
        for item in (value.transaction_id, value.owning_root_id, value.domain_id)
    ):
        errors.append("g2e_dependency_edge_invalid")
    if (
        type(value.canonical_order) is not int
        or not 1 <= value.canonical_order <= MAX_DEPENDENCY_GRAPH_EDGES_V01
    ):
        errors.append("g2e_dependency_graph_ordering_invalid")
    if not _sha256_valid(value.source_replay_edge_sha256):
        errors.append("g2e_dependency_replay_edge_mismatch")
    if not _text_tuple_valid(value.trace_refs, minimum=1):
        errors.append("g2e_dependency_edge_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _dependency_graph_index_errors(value: object) -> tuple[str, ...]:
    if type(value) is not DependencyGraphIndexV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if value.graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        errors.append("g2e_dependency_graph_version_mismatch")
    if not _sha256_valid(value.graph_basis_sha256):
        errors.append("g2e_dependency_graph_basis_mismatch")
    if not _sha256_valid(value.source_manifest_hash):
        errors.append("g2e_delta_source_unvalidated")
    if not _sha256_valid(value.source_history_hash):
        errors.append("g2e_dependency_source_history_mismatch")
    if any(
        not _text_valid(item)
        for item in (
            value.source_manifest_id, value.source_replay_id,
            value.transaction_id, value.owning_root_id, value.domain_id,
            value.policy_version,
        )
    ):
        errors.append("g2e_object_invalid")
    nodes_valid = _text_tuple_valid(
        value.ordered_node_ids,
        minimum=1,
        maximum=MAX_DEPENDENCY_GRAPH_NODES_V01,
    )
    edges_valid = _text_tuple_valid(
        value.ordered_edge_ids,
        maximum=MAX_DEPENDENCY_GRAPH_EDGES_V01,
    )
    if not nodes_valid or not edges_valid:
        errors.append("g2e_dependency_graph_bounds_exceeded")
    if (
        type(value.node_count) is not int
        or value.node_count != len(value.ordered_node_ids)
        or type(value.edge_count) is not int
        or value.edge_count != len(value.ordered_edge_ids)
    ):
        errors.append("g2e_dependency_graph_bounds_exceeded")
    if (
        value.max_nodes != MAX_DEPENDENCY_GRAPH_NODES_V01
        or value.max_edges != MAX_DEPENDENCY_GRAPH_EDGES_V01
        or value.max_hops != MAX_AFFECTED_HOPS_V01
        or value.acyclic is not True
    ):
        errors.append("g2e_dependency_graph_bounds_exceeded")
    if not _text_tuple_valid(value.schema_versions, minimum=1, maximum=64):
        errors.append("g2e_delta_schema_version_mismatch")
    if not _text_tuple_valid(value.trace_refs, minimum=1):
        errors.append("g2e_object_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _affected_set_request_errors(value: object) -> tuple[str, ...]:
    if type(value) is not AffectedSetRequestV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if value.graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        errors.append("g2e_dependency_graph_version_mismatch")
    for item, prefix in (
        (value.delta_id, "g2e_world_state_delta_v01:"),
        (value.graph_id, "g2e_dependency_graph_index_v01:"),
    ):
        if not _prefixed_identity_valid(item, prefix):
            errors.append("g2e_affected_request_invalid")
    if any(
        not _text_valid(item)
        for item in (
            value.baseline_report_id, value.transaction_id,
            value.owning_root_id, value.domain_id,
        )
    ):
        errors.append("g2e_affected_request_invalid")
    field_ids_valid = _text_tuple_valid(
        value.ordered_changed_field_binding_ids,
        maximum=MAX_CHANGED_BINDINGS_V01,
    )
    artifact_ids_valid = _text_tuple_valid(
        value.ordered_changed_artifact_binding_ids,
        maximum=MAX_CHANGED_BINDINGS_V01,
    )
    if (
        not field_ids_valid
        or not artifact_ids_valid
        or not (
            value.ordered_changed_field_binding_ids
            or value.ordered_changed_artifact_binding_ids
        )
        or len(value.ordered_changed_field_binding_ids)
        + len(value.ordered_changed_artifact_binding_ids)
        > MAX_CHANGED_BINDINGS_V01
    ):
        errors.append("g2e_affected_request_invalid")
    if (
        value.max_nodes != MAX_DEPENDENCY_GRAPH_NODES_V01
        or value.max_edges != MAX_DEPENDENCY_GRAPH_EDGES_V01
        or value.max_hops != MAX_AFFECTED_HOPS_V01
    ):
        errors.append("g2e_affected_request_invalid")
    if not _text_tuple_valid(value.trace_refs, minimum=1):
        errors.append("g2e_affected_request_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _affected_set_result_errors(value: object) -> tuple[str, ...]:
    if type(value) is not AffectedSetResultV01:
        return ("g2e_object_invalid",)
    errors: list[str] = []
    if value.graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        errors.append("g2e_dependency_graph_version_mismatch")
    tuples = (
        value.ordered_changed_node_ids,
        value.ordered_directly_affected_ids,
        value.ordered_transitively_affected_ids,
        value.ordered_affected_ids,
        value.ordered_unaffected_ids,
    )
    if (
        not _text_tuple_valid(
            value.ordered_changed_node_ids,
            minimum=1,
            maximum=MAX_CHANGED_BINDINGS_V01,
        )
        or any(
            not _text_tuple_valid(item, maximum=MAX_DEPENDENCY_GRAPH_NODES_V01)
            for item in tuples[1:]
        )
    ):
        errors.append("g2e_affected_closure_incomplete")
    changed, direct, transitive, affected, unaffected = map(set, tuples)
    if (
        direct & transitive
        or changed & affected
        or changed & unaffected
        or affected & unaffected
        or direct | transitive != affected
    ):
        errors.append("g2e_affected_closure_incomplete")
    if not _sha256_valid(value.closure_proof_sha256):
        errors.append("g2e_affected_proof_invalid")
    if (
        type(value.visited_node_count) is not int
        or value.visited_node_count
        != len(value.ordered_changed_node_ids) + len(value.ordered_affected_ids)
        or not 1 <= value.visited_node_count <= MAX_DEPENDENCY_GRAPH_NODES_V01
        or type(value.traversed_edge_count) is not int
        or not 0 <= value.traversed_edge_count <= MAX_DEPENDENCY_GRAPH_EDGES_V01
        or type(value.maximum_observed_hops) is not int
        or not 0 <= value.maximum_observed_hops <= MAX_AFFECTED_HOPS_V01
    ):
        errors.append("g2e_affected_closure_incomplete")
    if value.complete is not True or value.minimal is not True:
        errors.append("g2e_affected_closure_incomplete")
    if not _text_tuple_valid(value.trace_refs, minimum=1):
        errors.append("g2e_object_invalid")
    errors.extend(_identity_errors(value))
    return _ordered_reasons(errors)


def _closure_proof_sha256_v01(
    *,
    affected_request_id: str,
    delta_id: str,
    graph_id: str,
    graph_version: str,
    graph_basis_sha256: str,
    ordered_changed_node_ids: tuple[str, ...],
    visited_rows: tuple[tuple[str, int, str | None], ...],
    ordered_directly_affected_ids: tuple[str, ...],
    ordered_transitively_affected_ids: tuple[str, ...],
    ordered_affected_ids: tuple[str, ...],
    ordered_unaffected_ids: tuple[str, ...],
    visited_node_count: int,
    traversed_edge_count: int,
    maximum_observed_hops: int,
) -> str:
    material = (
        affected_request_id,
        delta_id,
        graph_id,
        graph_version,
        graph_basis_sha256,
        ordered_changed_node_ids,
        visited_rows,
        ordered_directly_affected_ids,
        ordered_transitively_affected_ids,
        ordered_affected_ids,
        ordered_unaffected_ids,
        visited_node_count,
        traversed_edge_count,
        maximum_observed_hops,
    )
    return _domain_sha256_v01(AFFECTED_CLOSURE_PROOF_DOMAIN_V01, material)


def _build_affected_set_result_internal_v01(
    *,
    affected_request_id: str,
    delta_id: str,
    graph_id: str,
    graph_version: str,
    graph_basis_sha256: str,
    ordered_changed_node_ids: tuple[str, ...],
    ordered_directly_affected_ids: tuple[str, ...],
    ordered_transitively_affected_ids: tuple[str, ...],
    ordered_affected_ids: tuple[str, ...],
    ordered_unaffected_ids: tuple[str, ...],
    visited_rows: tuple[tuple[str, int, str | None], ...],
    traversed_edge_count: int,
    maximum_observed_hops: int,
    trace_refs: tuple[str, ...],
) -> AffectedSetResultV01:
    if (
        type(visited_rows) is not tuple
        or tuple(row[0] for row in visited_rows)
        != ordered_changed_node_ids + ordered_affected_ids
        or len({row[0] for row in visited_rows}) != len(visited_rows)
    ):
        raise ValueError("g2e_affected_closure_incomplete")
    for index, row in enumerate(visited_rows):
        if (
            type(row) is not tuple
            or len(row) != 3
            or not _text_valid(row[0])
            or type(row[1]) is not int
            or not 0 <= row[1] <= MAX_AFFECTED_HOPS_V01
            or (row[2] is not None and not _text_valid(row[2]))
        ):
            raise ValueError("g2e_affected_closure_incomplete")
        if index < len(ordered_changed_node_ids):
            if row[1:] != (0, None):
                raise ValueError("g2e_affected_closure_incomplete")
        elif row[0] in ordered_directly_affected_ids and row[1] != 1:
            raise ValueError("g2e_affected_closure_incomplete")
        elif row[0] in ordered_transitively_affected_ids and row[1] <= 1:
            raise ValueError("g2e_affected_closure_incomplete")
    visited_node_count = len(visited_rows)
    closure_proof = _closure_proof_sha256_v01(
        affected_request_id=affected_request_id,
        delta_id=delta_id,
        graph_id=graph_id,
        graph_version=graph_version,
        graph_basis_sha256=graph_basis_sha256,
        ordered_changed_node_ids=ordered_changed_node_ids,
        visited_rows=visited_rows,
        ordered_directly_affected_ids=ordered_directly_affected_ids,
        ordered_transitively_affected_ids=ordered_transitively_affected_ids,
        ordered_affected_ids=ordered_affected_ids,
        ordered_unaffected_ids=ordered_unaffected_ids,
        visited_node_count=visited_node_count,
        traversed_edge_count=traversed_edge_count,
        maximum_observed_hops=maximum_observed_hops,
    )
    provisional = AffectedSetResultV01(
        affected_set_id="g2e_affected_set_result_v01:" + _ZERO_SHA256,
        affected_request_id=affected_request_id,
        delta_id=delta_id,
        graph_id=graph_id,
        graph_version=graph_version,
        ordered_changed_node_ids=ordered_changed_node_ids,
        ordered_directly_affected_ids=ordered_directly_affected_ids,
        ordered_transitively_affected_ids=ordered_transitively_affected_ids,
        ordered_affected_ids=ordered_affected_ids,
        ordered_unaffected_ids=ordered_unaffected_ids,
        closure_proof_sha256=closure_proof,
        visited_node_count=visited_node_count,
        traversed_edge_count=traversed_edge_count,
        maximum_observed_hops=maximum_observed_hops,
        complete=True,
        minimal=True,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _affected_set_result_errors
    )


def _fingerprint_source_rows_v01(
    source_artifacts: tuple[KernelArtifactV01, ...],
) -> tuple[tuple[object, ...], ...]:
    rows = []
    for artifact in source_artifacts:
        plain = _artifact_plain_v01(artifact)
        rows.append(
            (
                artifact.artifact_id,
                hashlib.sha256(
                    canonical_json_bytes_v01(plain["payload"])
                ).hexdigest(),
                plain["time_envelope"],
                artifact.lifecycle_state,
                artifact.authority_class,
                artifact.schema_version,
            )
        )
    return tuple(rows)


def _fingerprint_context_error_v01(
    *,
    profile: object,
    graph: object,
    dependency_edges: object,
    source_artifacts: object,
    policy_version: object,
    schema_versions: object,
    source_history_hash: object,
) -> str | None:
    if type(profile) is not DependencyFingerprintProfileV01:
        return "g2e_dependency_fingerprint_profile_invalid"
    profile_errors = _dependency_fingerprint_profile_errors(profile)
    if profile_errors:
        if profile.typed_role != DEPENDENCY_FINGERPRINT_TYPED_ROLE_V01:
            return "g2e_dependency_fingerprint_role_collision"
        return profile_errors[0]
    if type(graph) is not DependencyGraphIndexV01:
        return "g2e_object_invalid"
    graph_errors = _dependency_graph_index_errors(graph)
    if graph_errors:
        return graph_errors[0]
    if (
        type(dependency_edges) is not tuple
        or tuple(
            edge.edge_id
            for edge in dependency_edges
            if type(edge) is DeltaDependencyEdgeV01
        )
        != graph.ordered_edge_ids
        or len(dependency_edges) != len(graph.ordered_edge_ids)
        or any(_delta_dependency_edge_errors(edge) for edge in dependency_edges)
    ):
        return "g2e_dependency_edge_set_mismatch"
    if (
        type(source_artifacts) is not tuple
        or len(source_artifacts) != graph.node_count
        or any(type(item) is not KernelArtifactV01 for item in source_artifacts)
    ):
        return "g2e_delta_source_unvalidated"
    try:
        for artifact in source_artifacts:
            _artifact_plain_v01(artifact)
            if (
                artifact.transaction_id != graph.transaction_id
                or artifact.owner_root_id != graph.owning_root_id
            ):
                return "g2e_delta_source_unvalidated"
    except ValueError:
        return "g2e_delta_source_unvalidated"
    if tuple(item.artifact_id for item in source_artifacts) == graph.ordered_node_ids:
        if policy_version != graph.policy_version:
            return "g2e_delta_policy_version_mismatch"
        if schema_versions != graph.schema_versions:
            return "g2e_delta_schema_version_mismatch"
        if source_history_hash != graph.source_history_hash:
            return "g2e_dependency_source_history_mismatch"
        positions = {
            artifact_id: index
            for index, artifact_id in enumerate(graph.ordered_node_ids)
        }
        descriptors = tuple(_edge_descriptor_v01(edge) for edge in dependency_edges)
        replay_pairs = tuple(
            sorted(
                {(row[0], row[1]) for row in descriptors},
                key=lambda pair: (positions[pair[0]], positions[pair[1]]),
            )
        )
        expected_basis = _graph_basis_sha256_v01(
            graph_version=graph.graph_version,
            source_manifest_id=graph.source_manifest_id,
            source_manifest_hash=graph.source_manifest_hash,
            source_replay_id=graph.source_replay_id,
            transaction_id=graph.transaction_id,
            owning_root_id=graph.owning_root_id,
            domain_id=graph.domain_id,
            policy_version=graph.policy_version,
            schema_versions=graph.schema_versions,
            source_history_hash=graph.source_history_hash,
            source_artifacts=source_artifacts,
            replay_pairs=replay_pairs,
            normalized_descriptors=descriptors,
        )
        if expected_basis != graph.graph_basis_sha256:
            return "g2e_dependency_graph_basis_mismatch"
    if not _text_valid(policy_version):
        return "g2e_delta_policy_version_mismatch"
    if not _text_tuple_valid(schema_versions, minimum=1, maximum=64):
        return "g2e_delta_schema_version_mismatch"
    if not _sha256_valid(source_history_hash):
        return "g2e_dependency_source_history_mismatch"
    return None


def _carrier_context_v01(
    *,
    request: AffectedSetRequestV01,
    delta: WorldStateDeltaV01,
    graph: DependencyGraphIndexV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
) -> tuple[tuple[str, ...], dict[str, int]]:
    if _affected_set_request_errors(request):
        raise ValueError("g2e_affected_request_invalid")
    delta_errors = _world_state_delta_errors(delta)
    if "g2e_delta_time_invalid" in delta_errors:
        raise ValueError("g2e_delta_time_invalid")
    if delta_errors:
        raise ValueError("g2e_delta_source_invalid")
    observed_at = _parse_aware_timestamp_v01(delta.observed_at_utc)
    valid_from = _parse_aware_timestamp_v01(delta.valid_from_utc)
    valid_to = _parse_aware_timestamp_v01(delta.valid_to_utc)
    if not valid_from < valid_to or not valid_from <= observed_at < valid_to:
        raise ValueError("g2e_delta_time_invalid")
    if _dependency_graph_index_errors(graph):
        raise ValueError("g2e_dependency_graph_basis_mismatch")
    if (
        request.delta_id != delta.delta_id
        or request.graph_id != graph.graph_id
        or request.graph_version != graph.graph_version
        or request.baseline_report_id != delta.baseline_report_id
        or request.transaction_id != delta.transaction_id
        or request.owning_root_id != delta.owning_root_id
        or request.domain_id != delta.domain_id
        or request.ordered_changed_field_binding_ids
        != delta.ordered_changed_field_binding_ids
        or request.ordered_changed_artifact_binding_ids
        != delta.ordered_changed_artifact_binding_ids
        or delta.baseline_graph_id != graph.graph_id
        or delta.baseline_graph_version != graph.graph_version
        or delta.baseline_policy_version != graph.policy_version
        or delta.baseline_schema_versions != graph.schema_versions
        or delta.baseline_source_history_hash != graph.source_history_hash
    ):
        raise ValueError("g2e_affected_request_invalid")
    if (
        type(source_bindings) is not tuple
        or any(type(item) is not DeltaSourceBindingV01 for item in source_bindings)
        or tuple(item.source_binding_id for item in source_bindings)
        != delta.ordered_source_binding_ids
        or len(source_bindings) != len(delta.ordered_source_binding_ids)
    ):
        raise ValueError("g2e_delta_source_binding_set_mismatch")
    source_binding_errors = tuple(
        _delta_source_binding_errors(item) for item in source_bindings
    )
    if any(
        "g2e_delta_time_invalid" in errors for errors in source_binding_errors
    ):
        raise ValueError("g2e_delta_time_invalid")
    if any(source_binding_errors):
        raise ValueError("g2e_delta_source_binding_set_mismatch")
    if (
        type(changed_field_bindings) is not tuple
        or any(
            type(item) is not ChangedFieldBindingV01
            for item in changed_field_bindings
        )
        or tuple(item.changed_field_binding_id for item in changed_field_bindings)
        != delta.ordered_changed_field_binding_ids
        or len(changed_field_bindings)
        != len(delta.ordered_changed_field_binding_ids)
        or type(changed_artifact_bindings) is not tuple
        or any(
            type(item) is not ChangedArtifactBindingV01
            for item in changed_artifact_bindings
        )
        or tuple(
            item.changed_artifact_binding_id for item in changed_artifact_bindings
        )
        != delta.ordered_changed_artifact_binding_ids
        or len(changed_artifact_bindings)
        != len(delta.ordered_changed_artifact_binding_ids)
    ):
        raise ValueError("g2e_delta_binding_set_mismatch")
    changed_field_errors = tuple(
        _changed_field_binding_errors(item) for item in changed_field_bindings
    )
    changed_artifact_errors = tuple(
        _changed_artifact_binding_errors(item) for item in changed_artifact_bindings
    )
    if any(
        "g2e_delta_time_invalid" in errors
        for errors in changed_field_errors + changed_artifact_errors
    ):
        raise ValueError("g2e_delta_time_invalid")
    if any(changed_field_errors) or any(changed_artifact_errors):
        raise ValueError("g2e_delta_binding_set_mismatch")
    if (
        type(dependency_edges) is not tuple
        or tuple(
            item.edge_id
            for item in dependency_edges
            if type(item) is DeltaDependencyEdgeV01
        )
        != graph.ordered_edge_ids
        or len(dependency_edges) != graph.edge_count
        or any(_delta_dependency_edge_errors(item) for item in dependency_edges)
    ):
        raise ValueError("g2e_dependency_edge_set_mismatch")
    if (
        type(baseline_source_artifacts) is not tuple
        or type(observed_source_artifacts) is not tuple
        or len(baseline_source_artifacts) != graph.node_count
        or len(observed_source_artifacts) != graph.node_count
        or any(
            type(item) is not KernelArtifactV01
            for item in baseline_source_artifacts + observed_source_artifacts
        )
        or tuple(item.artifact_id for item in baseline_source_artifacts)
        != graph.ordered_node_ids
    ):
        raise ValueError("g2e_delta_source_binding_set_mismatch")
    positions = {
        artifact_id: index for index, artifact_id in enumerate(graph.ordered_node_ids)
    }
    baseline_by_id = {
        artifact.artifact_id: artifact for artifact in baseline_source_artifacts
    }
    binding_by_id = {item.source_binding_id: item for item in source_bindings}
    bound_positions: set[int] = set()
    for binding in source_bindings:
        if binding.baseline_source_artifact_id not in positions:
            raise ValueError("g2e_delta_source_binding_set_mismatch")
        position = positions[binding.baseline_source_artifact_id]
        if position in bound_positions:
            raise ValueError("g2e_delta_source_binding_set_mismatch")
        bound_positions.add(position)
        baseline = baseline_source_artifacts[position]
        observed = observed_source_artifacts[position]
        if (
            baseline.artifact_id != binding.baseline_source_artifact_id
            or observed.artifact_id != binding.observed_source_artifact_id
            or baseline.artifact_type != binding.baseline_source_artifact_type
            or observed.artifact_type != binding.observed_source_artifact_type
            or baseline.artifact_type != observed.artifact_type
            or _artifact_sha256_v01(baseline)
            != binding.baseline_source_artifact_sha256
            or _artifact_sha256_v01(observed)
            != binding.observed_source_artifact_sha256
            or _artifact_payload_sha256_v01(baseline)
            != binding.baseline_source_payload_sha256
            or _artifact_payload_sha256_v01(observed)
            != binding.observed_source_payload_sha256
            or binding.predecessor_relation != OBSERVED_SUCCESSOR_RELATION_V01
        ):
            raise ValueError("g2e_delta_source_binding_set_mismatch")
        if (
            binding.request_id != delta.request_id
            or binding.transaction_id != delta.transaction_id
            or binding.owning_root_id != delta.owning_root_id
            or binding.domain_id != delta.domain_id
            or binding.baseline_report_id != delta.baseline_report_id
            or binding.baseline_graph_id != graph.graph_id
            or binding.baseline_graph_version != graph.graph_version
            or binding.baseline_policy_version != delta.baseline_policy_version
            or binding.observed_policy_version != delta.observed_policy_version
            or binding.baseline_schema_versions != delta.baseline_schema_versions
            or binding.observed_schema_versions != delta.observed_schema_versions
            or binding.baseline_source_history_hash
            != delta.baseline_source_history_hash
            or binding.observed_source_history_hash
            != delta.observed_source_history_hash
        ):
            raise ValueError("g2e_delta_source_binding_set_mismatch")
        if (
            binding.valid_from_utc != delta.valid_from_utc
            or binding.valid_to_utc != delta.valid_to_utc
        ):
            raise ValueError("g2e_delta_time_invalid")
    if any(
        changed.source_binding_id not in binding_by_id
        for changed in changed_field_bindings + changed_artifact_bindings
    ):
        raise ValueError("g2e_delta_binding_set_mismatch")
    if any(
        changed.observed_at_utc != delta.observed_at_utc
        for changed in changed_field_bindings + changed_artifact_bindings
    ):
        raise ValueError("g2e_delta_time_invalid")

    field_semantics: dict[tuple[str, str], tuple[object, ...]] = {}
    for changed in changed_field_bindings:
        semantic_key = (changed.source_binding_id, changed.json_pointer)
        semantic_material = (
            changed.prior_value_sha256,
            changed.observed_value_sha256,
            changed.change_class,
            changed.observed_at_utc,
        )
        if semantic_key in field_semantics:
            if field_semantics[semantic_key] == semantic_material:
                raise ValueError("g2e_delta_duplicate_binding")
            raise ValueError("g2e_delta_conflicting_duplicate")
        field_semantics[semantic_key] = semantic_material

    artifact_semantics: dict[tuple[str, str], tuple[object, ...]] = {}
    for changed in changed_artifact_bindings:
        semantic_key = (
            changed.source_binding_id,
            changed.baseline_artifact_id,
        )
        semantic_material = (
            changed.baseline_artifact_type,
            changed.observed_artifact_id,
            changed.observed_artifact_type,
            changed.baseline_payload_sha256,
            changed.observed_payload_sha256,
            changed.baseline_dependency_fingerprint,
            changed.observed_dependency_fingerprint,
            changed.predecessor_relation,
            changed.change_class,
            changed.observed_at_utc,
        )
        if semantic_key in artifact_semantics:
            if artifact_semantics[semantic_key] == semantic_material:
                raise ValueError("g2e_delta_duplicate_binding")
            raise ValueError("g2e_delta_conflicting_duplicate")
        artifact_semantics[semantic_key] = semantic_material
    for index, (baseline, observed) in enumerate(
        zip(baseline_source_artifacts, observed_source_artifacts, strict=True)
    ):
        _artifact_plain_v01(baseline)
        _artifact_plain_v01(observed)
        if (
            baseline.transaction_id != graph.transaction_id
            or observed.transaction_id != graph.transaction_id
            or baseline.owner_root_id != graph.owning_root_id
            or observed.owner_root_id != graph.owning_root_id
            or baseline.artifact_type != observed.artifact_type
            or baseline.schema_version != observed.schema_version
        ):
            raise ValueError("g2e_delta_source_binding_set_mismatch")
        if index not in bound_positions and canonical_json_bytes_v01(
            _artifact_plain_v01(baseline)
        ) != canonical_json_bytes_v01(_artifact_plain_v01(observed)):
            raise ValueError("g2e_delta_source_binding_set_mismatch")
    for changed in changed_field_bindings:
        binding = binding_by_id.get(changed.source_binding_id)
        if binding is None:
            raise ValueError("g2e_delta_binding_set_mismatch")
        position = positions[binding.baseline_source_artifact_id]
        baseline_plain = _artifact_plain_v01(baseline_source_artifacts[position])
        observed_plain = _artifact_plain_v01(observed_source_artifacts[position])
        try:
            prior = _resolve_json_pointer_v01(baseline_plain, changed.json_pointer)
            current = _resolve_json_pointer_v01(observed_plain, changed.json_pointer)
        except ValueError:
            raise ValueError("g2e_dependency_source_payload_unavailable") from None
        if (
            hashlib.sha256(canonical_json_bytes_v01(prior)).hexdigest()
            != changed.prior_value_sha256
            or hashlib.sha256(canonical_json_bytes_v01(current)).hexdigest()
            != changed.observed_value_sha256
            or canonical_json_bytes_v01(prior) == canonical_json_bytes_v01(current)
        ):
            raise ValueError("g2e_delta_artifact_binding_invalid")
    profile = build_dependency_fingerprint_profile_v01()
    baseline_fingerprint = build_dependency_fingerprint_v01(
        profile=profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=baseline_source_artifacts,
        policy_version=delta.baseline_policy_version,
        schema_versions=delta.baseline_schema_versions,
        source_history_hash=delta.baseline_source_history_hash,
    )
    observed_fingerprint = build_dependency_fingerprint_v01(
        profile=profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=observed_source_artifacts,
        policy_version=delta.observed_policy_version,
        schema_versions=delta.observed_schema_versions,
        source_history_hash=delta.observed_source_history_hash,
    )
    if (
        delta.dependency_fingerprint_before != baseline_fingerprint
        or delta.dependency_fingerprint_after != observed_fingerprint
    ):
        raise ValueError("g2e_dependency_fingerprint_forgery")
    for changed in changed_artifact_bindings:
        binding = binding_by_id.get(changed.source_binding_id)
        if binding is None:
            raise ValueError("g2e_delta_binding_set_mismatch")
        if (
            changed.baseline_artifact_id != binding.baseline_source_artifact_id
            or changed.observed_artifact_id != binding.observed_source_artifact_id
            or changed.baseline_artifact_type != binding.baseline_source_artifact_type
            or changed.observed_artifact_type != binding.observed_source_artifact_type
            or changed.baseline_payload_sha256
            != binding.baseline_source_payload_sha256
            or changed.observed_payload_sha256
            != binding.observed_source_payload_sha256
            or changed.baseline_dependency_fingerprint != baseline_fingerprint
            or changed.observed_dependency_fingerprint != observed_fingerprint
        ):
            raise ValueError("g2e_delta_artifact_binding_invalid")
    changed_nodes = tuple(
        sorted(
            {
                binding_by_id[item.source_binding_id].baseline_source_artifact_id
                for item in changed_field_bindings + changed_artifact_bindings
            },
            key=lambda artifact_id: (positions[artifact_id], artifact_id),
        )
    )
    if not changed_nodes:
        raise ValueError("g2e_affected_changed_binding_unknown")
    return changed_nodes, positions


def _affected_walk_v01(
    *,
    changed_nodes: tuple[str, ...],
    graph: DependencyGraphIndexV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    positions: dict[str, int],
) -> dict[str, object]:
    reverse: dict[str, list[DeltaDependencyEdgeV01]] = {
        node_id: [] for node_id in graph.ordered_node_ids
    }
    for edge in dependency_edges:
        reverse[edge.dependency_artifact_id].append(edge)
    for rows in reverse.values():
        rows.sort(key=lambda edge: edge.canonical_order)
    frontier = deque(changed_nodes)
    distance = {node_id: 0 for node_id in changed_nodes}
    cause: dict[str, str | None] = {node_id: None for node_id in changed_nodes}
    traversed_edge_count = 0
    while frontier:
        dependency_id = frontier.popleft()
        for edge in reverse[dependency_id]:
            traversed_edge_count += 1
            dependent_id = edge.dependent_artifact_id
            if dependent_id in distance:
                continue
            next_distance = distance[dependency_id] + 1
            if next_distance > graph.max_hops:
                raise ValueError("g2e_affected_hop_bound_exceeded")
            distance[dependent_id] = next_distance
            cause[dependent_id] = edge.edge_id
            if len(distance) > graph.max_nodes:
                raise ValueError("g2e_affected_node_bound_exceeded")
            frontier.append(dependent_id)
    affected = tuple(
        sorted(
            (node_id for node_id, hops in distance.items() if hops > 0),
            key=lambda node_id: (distance[node_id], positions[node_id], node_id),
        )
    )
    direct = tuple(node_id for node_id in affected if distance[node_id] == 1)
    transitive = tuple(node_id for node_id in affected if distance[node_id] > 1)
    changed_set = set(changed_nodes)
    affected_set = set(affected)
    unaffected = tuple(
        node_id
        for node_id in graph.ordered_node_ids
        if node_id not in changed_set and node_id not in affected_set
    )
    visited_rows = tuple((node_id, 0, None) for node_id in changed_nodes) + tuple(
        (node_id, distance[node_id], cause[node_id]) for node_id in affected
    )
    return {
        "ordered_changed_node_ids": changed_nodes,
        "ordered_directly_affected_ids": direct,
        "ordered_transitively_affected_ids": transitive,
        "ordered_affected_ids": affected,
        "ordered_unaffected_ids": unaffected,
        "visited_rows": visited_rows,
        "traversed_edge_count": traversed_edge_count,
        "maximum_observed_hops": max(distance.values(), default=0),
    }


def _artifact_profile_instance_v01(name: str) -> tuple[object, ...]:
    for row in G2E_ABI_ARTIFACT_INSTANCE_PROFILES_V01:
        if row[0] == name:
            return row
    raise ValueError("g2e_object_invalid")


def _project_g2e_abi_payload_v01(
    *,
    profile_name: str,
    complete_payload: dict[str, object],
) -> dict[str, object]:
    profile = _artifact_profile_instance_v01(profile_name)
    source_type_name = profile[2]
    try:
        expected_field_order = next(
            field_names
            for type_name, field_names in CONTINUOUS_DELTA_FIELD_NAMES_V01
            if type_name == source_type_name
        )
        omitted_fields = next(
            fields
            for name, fields in _G2E_ABI_PAYLOAD_OMISSIONS_V01
            if name == profile_name
        )
    except StopIteration as exc:
        raise ValueError("g2e_object_invalid") from exc
    if type(complete_payload) is not dict:
        raise ValueError("g2e_object_invalid")
    if tuple(complete_payload) != expected_field_order:
        raise ValueError("g2e_object_invalid")
    if any(field_name not in complete_payload for field_name in omitted_fields):
        raise ValueError("g2e_object_invalid")
    projected = {
        field_name: complete_payload[field_name]
        for field_name in expected_field_order
        if field_name not in omitted_fields
    }
    expected_projected_order = tuple(
        field_name
        for field_name in expected_field_order
        if field_name not in omitted_fields
    )
    if tuple(projected) != expected_projected_order:
        raise ValueError("g2e_object_invalid")
    return projected


def _artifact_time_envelope_v01(
    *,
    baseline_route_artifact: KernelArtifactV01,
    delta: WorldStateDeltaV01,
) -> dict[str, object]:
    route_plain = _artifact_plain_v01(baseline_route_artifact)
    route_envelope = route_plain["time_envelope"]
    if type(route_envelope) is not dict:
        raise ValueError("g2e_object_invalid")
    return {
        "ct_session_anchor": route_envelope["ct_session_anchor"],
        "et_observed_at": delta.observed_at_utc,
        "freshness_class": route_envelope["freshness_class"],
        "kt_asof": route_envelope["kt_asof"],
        "pt_created_at": delta.observed_at_utc,
        "ttl_seconds": route_envelope["ttl_seconds"],
        "valid_from": delta.valid_from_utc,
        "valid_to": delta.valid_to_utc,
    }


def _project_g2e_kernel_artifact_v01(
    *,
    profile_name: str,
    transaction_id: str,
    owning_root_id: str,
    payload: dict[str, object],
    trace_refs: tuple[str, ...],
    parent_refs: tuple[str, ...],
    time_envelope: dict[str, object],
) -> KernelArtifactV01:
    profile = _artifact_profile_instance_v01(profile_name)
    (
        _name, artifact_type, _source_type, lifecycle_state, authority_class,
        source_component, prefix, domain, _owner_slice,
    ) = profile
    material = {
        "abi_version": "v1.0",
        "artifact_type": artifact_type,
        "schema_version": "v0.1",
        "transaction_id": transaction_id,
        "owner_root_id": owning_root_id,
        "source_component": source_component,
        "authority_class": authority_class,
        "lifecycle_state": lifecycle_state,
        "payload": payload,
        "trace_refs": list(trace_refs),
        "parent_refs": list(parent_refs),
        "time_envelope": time_envelope,
    }
    artifact_id = str(prefix) + domain_separated_sha256_hex_v01(
        domain=str(domain),
        payload=canonical_json_bytes_v01(material),
    )
    artifact = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type=str(artifact_type),
        schema_version="v0.1",
        transaction_id=transaction_id,
        owner_root_id=owning_root_id,
        source_component=str(source_component),
        authority_class=str(authority_class),
        lifecycle_state=str(lifecycle_state),
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=time_envelope,
    )
    if validate_kernel_artifact_v01(artifact):
        raise ValueError("g2e_object_invalid")
    return artifact


def _project_delta_source_proposed_artifact_v01(
    *,
    delta: WorldStateDeltaV01,
    baseline_route_artifact: KernelArtifactV01,
    baseline_g2d_report_artifact: KernelArtifactV01,
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
) -> KernelArtifactV01:
    if _world_state_delta_errors(delta):
        raise ValueError("g2e_delta_source_invalid")
    for artifact in (
        baseline_route_artifact,
        baseline_g2d_report_artifact,
        *baseline_source_artifacts,
        *observed_source_artifacts,
    ):
        _artifact_plain_v01(artifact)
    return _project_g2e_kernel_artifact_v01(
        profile_name="delta_source_proposed",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="delta_source_proposed",
            complete_payload=world_state_delta_to_plain_data_v01(delta),
        ),
        trace_refs=delta.trace_refs + delta.ordered_source_binding_ids,
        parent_refs=_ordered_unique_v01(
            (
                baseline_route_artifact.artifact_id,
                baseline_g2d_report_artifact.artifact_id,
                *(artifact.artifact_id for artifact in baseline_source_artifacts),
                *(artifact.artifact_id for artifact in observed_source_artifacts),
            )
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
        ),
    )


def _project_delta_source_validated_artifact_v01(
    *,
    delta: WorldStateDeltaV01,
    proposed_source_artifact: KernelArtifactV01,
    t01_decision_id: str,
    baseline_route_artifact: KernelArtifactV01,
    baseline_g2d_report_artifact: KernelArtifactV01,
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
) -> KernelArtifactV01:
    _artifact_plain_v01(proposed_source_artifact)
    if (
        proposed_source_artifact.artifact_type != "ContinuousDeltaSource"
        or proposed_source_artifact.lifecycle_state != "PROPOSED"
        or not _text_valid(t01_decision_id)
    ):
        raise ValueError("g2e_object_invalid")
    return _project_g2e_kernel_artifact_v01(
        profile_name="delta_source_validated",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="delta_source_validated",
            complete_payload=world_state_delta_to_plain_data_v01(delta),
        ),
        trace_refs=(
            proposed_source_artifact.artifact_id,
            t01_decision_id,
            *delta.trace_refs,
            *delta.ordered_source_binding_ids,
        ),
        parent_refs=_ordered_unique_v01(
            (
                proposed_source_artifact.artifact_id,
                baseline_route_artifact.artifact_id,
                baseline_g2d_report_artifact.artifact_id,
                *(artifact.artifact_id for artifact in baseline_source_artifacts),
                *(artifact.artifact_id for artifact in observed_source_artifacts),
            )
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
        ),
    )


def _project_dependency_graph_artifact_v01(
    *,
    graph: DependencyGraphIndexV01,
    delta: WorldStateDeltaV01,
    validated_delta_source_artifact: KernelArtifactV01,
    baseline_route_artifact: KernelArtifactV01,
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
) -> KernelArtifactV01:
    if _dependency_graph_index_errors(graph):
        raise ValueError("g2e_dependency_graph_basis_mismatch")
    return _project_g2e_kernel_artifact_v01(
        profile_name="dependency_graph_validated",
        transaction_id=graph.transaction_id,
        owning_root_id=graph.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="dependency_graph_validated",
            complete_payload=dependency_graph_index_to_plain_data_v01(graph),
        ),
        trace_refs=graph.trace_refs + (
            graph.source_manifest_id,
            graph.source_replay_id,
        ),
        parent_refs=(
            validated_delta_source_artifact.artifact_id,
            *(artifact.artifact_id for artifact in baseline_source_artifacts),
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
        ),
    )


def _project_affected_set_artifact_v01(
    *,
    affected_result: AffectedSetResultV01,
    delta: WorldStateDeltaV01,
    validated_delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    baseline_route_artifact: KernelArtifactV01,
    t02_decision_id: str,
) -> KernelArtifactV01:
    if _affected_set_result_errors(affected_result):
        raise ValueError("g2e_affected_closure_incomplete")
    return _project_g2e_kernel_artifact_v01(
        profile_name="affected_set_validated",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="affected_set_validated",
            complete_payload=affected_set_result_to_plain_data_v01(
                affected_result
            ),
        ),
        trace_refs=(
            *(
                item
                for item in _ordered_unique_v01(affected_result.trace_refs)
                if item
                not in (
                    t02_decision_id,
                    affected_result.delta_id,
                    affected_result.graph_id,
                )
            ),
            t02_decision_id,
            affected_result.delta_id,
            affected_result.graph_id,
        ),
        parent_refs=(
            validated_delta_source_artifact.artifact_id,
            dependency_graph_artifact.artifact_id,
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
        ),
    )


def build_delta_source_binding_v01(
    *,
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    baseline_source_artifact_id: str,
    baseline_source_artifact_type: str,
    baseline_source_artifact_sha256: str,
    baseline_source_payload_sha256: str,
    observed_source_artifact_id: str,
    observed_source_artifact_type: str,
    observed_source_artifact_sha256: str,
    observed_source_payload_sha256: str,
    baseline_report_id: str,
    baseline_graph_id: str,
    baseline_graph_version: str,
    baseline_policy_version: str,
    observed_policy_version: str,
    baseline_schema_versions: tuple[str, ...],
    observed_schema_versions: tuple[str, ...],
    baseline_source_history_hash: str,
    observed_source_history_hash: str,
    valid_from_utc: str,
    valid_to_utc: str,
    trace_refs: tuple[str, ...],
) -> DeltaSourceBindingV01:
    provisional = DeltaSourceBindingV01(
        source_binding_id="g2e_delta_source_binding_v01:" + _ZERO_SHA256,
        binding_version=DELTA_SOURCE_BINDING_VERSION_V01,
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        baseline_source_artifact_id=baseline_source_artifact_id,
        baseline_source_artifact_type=baseline_source_artifact_type,
        baseline_source_artifact_sha256=baseline_source_artifact_sha256,
        baseline_source_payload_sha256=baseline_source_payload_sha256,
        observed_source_artifact_id=observed_source_artifact_id,
        observed_source_artifact_type=observed_source_artifact_type,
        observed_source_artifact_sha256=observed_source_artifact_sha256,
        observed_source_payload_sha256=observed_source_payload_sha256,
        predecessor_relation=OBSERVED_SUCCESSOR_RELATION_V01,
        baseline_report_id=baseline_report_id,
        baseline_graph_id=baseline_graph_id,
        baseline_graph_version=baseline_graph_version,
        baseline_policy_version=baseline_policy_version,
        observed_policy_version=observed_policy_version,
        baseline_schema_versions=baseline_schema_versions,
        observed_schema_versions=observed_schema_versions,
        baseline_source_history_hash=baseline_source_history_hash,
        observed_source_history_hash=observed_source_history_hash,
        valid_from_utc=valid_from_utc,
        valid_to_utc=valid_to_utc,
        trace_refs=trace_refs,
        authority_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(result, _delta_source_binding_errors)  # type: ignore[return-value]


def validate_delta_source_binding_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, DeltaSourceBindingV01, "delta_source_structure", _delta_source_binding_errors)


def delta_source_binding_to_plain_data_v01(value: DeltaSourceBindingV01) -> dict[str, object]:
    return _serialize(value, DeltaSourceBindingV01, _delta_source_binding_errors)


def rebuild_delta_source_binding_identity_v01(value: DeltaSourceBindingV01) -> str:
    return _rebuild(value, DeltaSourceBindingV01)


def build_changed_field_binding_v01(
    *,
    source_binding_id: str,
    json_pointer: str,
    prior_value_sha256: str,
    observed_value_sha256: str,
    change_class: str,
    observed_at_utc: str,
    trace_refs: tuple[str, ...],
) -> ChangedFieldBindingV01:
    provisional = ChangedFieldBindingV01(
        changed_field_binding_id="g2e_changed_field_binding_v01:" + _ZERO_SHA256,
        source_binding_id=source_binding_id,
        json_pointer=json_pointer,
        prior_value_sha256=prior_value_sha256,
        observed_value_sha256=observed_value_sha256,
        change_class=change_class,
        observed_at_utc=observed_at_utc,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(result, _changed_field_binding_errors)  # type: ignore[return-value]


def validate_changed_field_binding_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, ChangedFieldBindingV01, "changed_binding", _changed_field_binding_errors)


def changed_field_binding_to_plain_data_v01(value: ChangedFieldBindingV01) -> dict[str, object]:
    return _serialize(value, ChangedFieldBindingV01, _changed_field_binding_errors)


def rebuild_changed_field_binding_identity_v01(value: ChangedFieldBindingV01) -> str:
    return _rebuild(value, ChangedFieldBindingV01)


def build_changed_artifact_binding_v01(
    *,
    source_binding_id: str,
    baseline_artifact_id: str,
    baseline_artifact_type: str,
    baseline_payload_sha256: str,
    observed_artifact_id: str,
    observed_artifact_type: str,
    observed_payload_sha256: str,
    baseline_dependency_fingerprint: str,
    observed_dependency_fingerprint: str,
    change_class: str,
    observed_at_utc: str,
    trace_refs: tuple[str, ...],
) -> ChangedArtifactBindingV01:
    provisional = ChangedArtifactBindingV01(
        changed_artifact_binding_id="g2e_changed_artifact_binding_v01:" + _ZERO_SHA256,
        source_binding_id=source_binding_id,
        baseline_artifact_id=baseline_artifact_id,
        baseline_artifact_type=baseline_artifact_type,
        baseline_payload_sha256=baseline_payload_sha256,
        observed_artifact_id=observed_artifact_id,
        observed_artifact_type=observed_artifact_type,
        observed_payload_sha256=observed_payload_sha256,
        baseline_dependency_fingerprint=baseline_dependency_fingerprint,
        observed_dependency_fingerprint=observed_dependency_fingerprint,
        predecessor_relation=OBSERVED_SUCCESSOR_RELATION_V01,
        change_class=change_class,
        observed_at_utc=observed_at_utc,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(result, _changed_artifact_binding_errors)  # type: ignore[return-value]


def validate_changed_artifact_binding_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, ChangedArtifactBindingV01, "changed_binding", _changed_artifact_binding_errors)


def changed_artifact_binding_to_plain_data_v01(value: ChangedArtifactBindingV01) -> dict[str, object]:
    return _serialize(value, ChangedArtifactBindingV01, _changed_artifact_binding_errors)


def rebuild_changed_artifact_binding_identity_v01(value: ChangedArtifactBindingV01) -> str:
    return _rebuild(value, ChangedArtifactBindingV01)


def build_world_state_delta_v01(
    *,
    ordered_source_binding_ids: tuple[str, ...],
    request_id: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    baseline_report_id: str,
    baseline_graph_id: str,
    baseline_graph_version: str,
    observed_at_utc: str,
    valid_from_utc: str,
    valid_to_utc: str,
    baseline_policy_version: str,
    observed_policy_version: str,
    baseline_schema_versions: tuple[str, ...],
    observed_schema_versions: tuple[str, ...],
    baseline_source_history_hash: str,
    observed_source_history_hash: str,
    ordered_changed_field_binding_ids: tuple[str, ...],
    ordered_changed_artifact_binding_ids: tuple[str, ...],
    dependency_fingerprint_before: str,
    dependency_fingerprint_after: str,
    trace_refs: tuple[str, ...],
) -> WorldStateDeltaV01:
    provisional = WorldStateDeltaV01(
        delta_id="g2e_world_state_delta_v01:" + _ZERO_SHA256,
        delta_version=WORLD_STATE_DELTA_VERSION_V01,
        delta_profile_id=WORLD_STATE_DELTA_PROFILE_ID_V01,
        ordered_source_binding_ids=ordered_source_binding_ids,
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        baseline_report_id=baseline_report_id,
        baseline_graph_id=baseline_graph_id,
        baseline_graph_version=baseline_graph_version,
        delta_sequence=1,
        prior_delta_id=None,
        observed_at_utc=observed_at_utc,
        valid_from_utc=valid_from_utc,
        valid_to_utc=valid_to_utc,
        baseline_policy_version=baseline_policy_version,
        observed_policy_version=observed_policy_version,
        baseline_schema_versions=baseline_schema_versions,
        observed_schema_versions=observed_schema_versions,
        baseline_source_history_hash=baseline_source_history_hash,
        observed_source_history_hash=observed_source_history_hash,
        ordered_changed_field_binding_ids=ordered_changed_field_binding_ids,
        ordered_changed_artifact_binding_ids=ordered_changed_artifact_binding_ids,
        dependency_fingerprint_before=dependency_fingerprint_before,
        dependency_fingerprint_after=dependency_fingerprint_after,
        trace_refs=trace_refs,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(result, _world_state_delta_errors)  # type: ignore[return-value]


def validate_world_state_delta_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, WorldStateDeltaV01, "delta_source_structure", _world_state_delta_errors)


def world_state_delta_to_plain_data_v01(value: WorldStateDeltaV01) -> dict[str, object]:
    return _serialize(value, WorldStateDeltaV01, _world_state_delta_errors)


def rebuild_world_state_delta_identity_v01(value: WorldStateDeltaV01) -> str:
    return _rebuild(value, WorldStateDeltaV01)


def build_dependency_fingerprint_profile_v01() -> DependencyFingerprintProfileV01:
    provisional = DependencyFingerprintProfileV01(
        fingerprint_profile_id="g2e_dependency_fingerprint_profile_v01:" + _ZERO_SHA256,
        fingerprint_profile_version=DEPENDENCY_FINGERPRINT_PROFILE_VERSION_V01,
        hash_algorithm=DEPENDENCY_FINGERPRINT_HASH_ALGORITHM_V01,
        canonicalization_profile_id=DEPENDENCY_FINGERPRINT_CANONICALIZATION_PROFILE_V01,
        domain_separator=DEPENDENCY_FINGERPRINT_DOMAIN_SEPARATOR_V01,
        typed_role=DEPENDENCY_FINGERPRINT_TYPED_ROLE_V01,
        ordered_preimage_fields=DEPENDENCY_FINGERPRINT_PREIMAGE_FIELDS_V01,
        cross_role_reuse_forbidden=True,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(result, _dependency_fingerprint_profile_errors)  # type: ignore[return-value]


def validate_dependency_fingerprint_profile_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, DependencyFingerprintProfileV01, "fingerprint_profile", _dependency_fingerprint_profile_errors)


def dependency_fingerprint_profile_to_plain_data_v01(value: DependencyFingerprintProfileV01) -> dict[str, object]:
    return _serialize(value, DependencyFingerprintProfileV01, _dependency_fingerprint_profile_errors)


def rebuild_dependency_fingerprint_profile_identity_v01(value: DependencyFingerprintProfileV01) -> str:
    return _rebuild(value, DependencyFingerprintProfileV01)


def build_continuous_delta_validation_report_v01(
    *,
    validation_target: str,
    validated_object_id: str | None,
    failure_stage: str,
    reason_codes: tuple[str, ...],
    source_reason_codes: tuple[str, ...],
    return_to_root_required: bool,
    root_review_required: bool,
) -> ContinuousDeltaValidationReportV01:
    report = _make_validation_report(
        validation_target=validation_target,
        validated_object_id=validated_object_id,
        failure_stage=failure_stage,
        reason_codes=reason_codes,
        source_reason_codes=source_reason_codes,
        return_to_root_required=return_to_root_required,
        root_review_required=root_review_required,
    )
    errors = _validation_report_errors(report)
    if errors:
        raise ValueError(errors[0])
    return report


def validate_continuous_delta_validation_report_v01(value: object) -> ContinuousDeltaValidationReportV01:
    return _structural_report(value, ContinuousDeltaValidationReportV01, "bundle_final", _validation_report_errors)


def continuous_delta_validation_report_to_plain_data_v01(value: ContinuousDeltaValidationReportV01) -> dict[str, object]:
    return _serialize(value, ContinuousDeltaValidationReportV01, _validation_report_errors)


def rebuild_continuous_delta_validation_report_identity_v01(value: ContinuousDeltaValidationReportV01) -> str:
    return _rebuild(value, ContinuousDeltaValidationReportV01)


def build_delta_dependency_edge_v01(
    *,
    graph_basis_sha256: str,
    graph_version: str,
    dependent_artifact_id: str,
    dependency_artifact_id: str,
    dependency_field_pointers: tuple[str, ...],
    edge_class: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    canonical_order: int,
    source_replay_edge_sha256: str,
    trace_refs: tuple[str, ...],
) -> DeltaDependencyEdgeV01:
    provisional = DeltaDependencyEdgeV01(
        edge_id="g2e_delta_dependency_edge_v01:" + _ZERO_SHA256,
        graph_basis_sha256=graph_basis_sha256,
        graph_version=graph_version,
        dependent_artifact_id=dependent_artifact_id,
        dependency_artifact_id=dependency_artifact_id,
        dependency_field_pointers=dependency_field_pointers,
        edge_class=edge_class,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        canonical_order=canonical_order,
        source_replay_edge_sha256=source_replay_edge_sha256,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _delta_dependency_edge_errors
    )


def validate_delta_dependency_edge_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        DeltaDependencyEdgeV01,
        "dependency_edge",
        _delta_dependency_edge_errors,
    )


def delta_dependency_edge_to_plain_data_v01(
    value: DeltaDependencyEdgeV01,
) -> dict[str, object]:
    return _serialize(
        value, DeltaDependencyEdgeV01, _delta_dependency_edge_errors
    )


def rebuild_delta_dependency_edge_identity_v01(
    value: DeltaDependencyEdgeV01,
) -> str:
    return _rebuild(value, DeltaDependencyEdgeV01)


def build_dependency_graph_index_v01(
    *,
    graph_basis_sha256: str,
    graph_version: str,
    manifest: ArtifactManifestV01,
    replay: ReplayVerificationResultV01,
    source_artifacts: tuple[KernelArtifactV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    policy_version: str,
    schema_versions: tuple[str, ...],
    source_history_hash: str,
    trace_refs: tuple[str, ...],
) -> DependencyGraphIndexV01:
    source_errors = _manifest_replay_source_errors_v01(
        manifest=manifest,
        replay=replay,
        source_artifacts=source_artifacts,
    )
    if source_errors:
        raise ValueError(source_errors[0])
    if graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        raise ValueError("g2e_dependency_graph_version_mismatch")
    node_ids = tuple(item.artifact_id for item in manifest.artifacts)
    if len(node_ids) > MAX_DEPENDENCY_GRAPH_NODES_V01:
        raise ValueError("g2e_dependency_graph_bounds_exceeded")
    if (
        transaction_id != manifest.transaction_id
        or any(item.transaction_id != transaction_id for item in source_artifacts)
    ):
        raise ValueError("g2e_dependency_edge_cross_transaction")
    if any(item.owner_root_id != owning_root_id for item in source_artifacts):
        raise ValueError("g2e_dependency_edge_cross_root")
    if (
        not _text_valid(domain_id)
        or not _text_valid(policy_version)
        or not _text_tuple_valid(schema_versions, minimum=1, maximum=64)
        or not _sha256_valid(source_history_hash)
        or not _text_tuple_valid(trace_refs, minimum=1)
    ):
        raise ValueError("g2e_object_invalid")
    if (
        type(dependency_edges) is not tuple
        or len(dependency_edges) > MAX_DEPENDENCY_GRAPH_EDGES_V01
        or any(_delta_dependency_edge_errors(edge) for edge in dependency_edges)
    ):
        raise ValueError("g2e_dependency_edge_set_mismatch")
    positions = {artifact_id: index for index, artifact_id in enumerate(node_ids)}
    descriptors = tuple(_edge_descriptor_v01(edge) for edge in dependency_edges)
    try:
        normalized = _normalized_edge_descriptors_v01(descriptors, positions)
    except KeyError as exc:
        unknown = exc.args[0]
        if any(row[0] == unknown for row in descriptors):
            raise ValueError("g2e_dependency_edge_unknown_dependent") from None
        raise ValueError("g2e_dependency_edge_unknown_source") from None
    if descriptors != normalized or tuple(
        edge.canonical_order for edge in dependency_edges
    ) != tuple(range(1, len(dependency_edges) + 1)):
        raise ValueError("g2e_dependency_graph_ordering_invalid")
    replay_pairs = tuple(
        (edge.artifact_id, edge.depends_on_artifact_id)
        for edge in replay.reconstructed_dependency_edges
    )
    if len(descriptors) != len(set(descriptors)):
        raise ValueError("g2e_dependency_edge_duplicate")
    descriptor_pair_rows = tuple((row[0], row[1]) for row in descriptors)
    if len(descriptor_pair_rows) != len(set(descriptor_pair_rows)):
        raise ValueError("g2e_dependency_edge_duplicate")
    if _graph_has_cycle_v01(node_ids, descriptors):
        raise ValueError("g2e_dependency_graph_cycle")
    descriptor_pairs = set(descriptor_pair_rows)
    replay_pair_set = set(replay_pairs)
    if descriptor_pairs - replay_pair_set:
        raise ValueError("g2e_dependency_edge_unknown_source")
    if replay_pair_set - descriptor_pairs:
        raise ValueError("g2e_dependency_graph_missing_edge")
    source_manifest_id = _source_manifest_id_v01(manifest)
    expected_basis = _graph_basis_sha256_v01(
        graph_version=graph_version,
        source_manifest_id=source_manifest_id,
        source_manifest_hash=manifest.manifest_hash,
        source_replay_id=replay.replay_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        policy_version=policy_version,
        schema_versions=schema_versions,
        source_history_hash=source_history_hash,
        source_artifacts=source_artifacts,
        replay_pairs=replay_pairs,
        normalized_descriptors=normalized,
    )
    if graph_basis_sha256 != expected_basis:
        raise ValueError("g2e_dependency_graph_basis_mismatch")
    for index, edge in enumerate(dependency_edges, start=1):
        expected_replay_edge = _source_replay_edge_sha256_v01(
            source_manifest_id=source_manifest_id,
            source_manifest_hash=manifest.manifest_hash,
            source_replay_id=replay.replay_id,
            dependent_artifact_id=edge.dependent_artifact_id,
            dependency_artifact_id=edge.dependency_artifact_id,
            positions=positions,
        )
        if (
            edge.graph_basis_sha256 != expected_basis
            or edge.graph_version != graph_version
            or edge.transaction_id != transaction_id
            or edge.owning_root_id != owning_root_id
            or edge.domain_id != domain_id
            or edge.canonical_order != index
            or edge.source_replay_edge_sha256 != expected_replay_edge
        ):
            raise ValueError("g2e_dependency_replay_edge_mismatch")
    provisional = DependencyGraphIndexV01(
        graph_id="g2e_dependency_graph_index_v01:" + _ZERO_SHA256,
        graph_version=graph_version,
        graph_basis_sha256=expected_basis,
        source_manifest_id=source_manifest_id,
        source_manifest_hash=manifest.manifest_hash,
        source_replay_id=replay.replay_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        ordered_node_ids=node_ids,
        ordered_edge_ids=tuple(edge.edge_id for edge in dependency_edges),
        node_count=len(node_ids),
        edge_count=len(dependency_edges),
        max_nodes=MAX_DEPENDENCY_GRAPH_NODES_V01,
        max_edges=MAX_DEPENDENCY_GRAPH_EDGES_V01,
        max_hops=MAX_AFFECTED_HOPS_V01,
        acyclic=True,
        source_history_hash=source_history_hash,
        policy_version=policy_version,
        schema_versions=schema_versions,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _dependency_graph_index_errors
    )


def validate_dependency_graph_index_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        DependencyGraphIndexV01,
        "dependency_graph",
        _dependency_graph_index_errors,
    )


def dependency_graph_index_to_plain_data_v01(
    value: DependencyGraphIndexV01,
) -> dict[str, object]:
    return _serialize(
        value, DependencyGraphIndexV01, _dependency_graph_index_errors
    )


def rebuild_dependency_graph_index_identity_v01(
    value: DependencyGraphIndexV01,
) -> str:
    return _rebuild(value, DependencyGraphIndexV01)


def build_affected_set_request_v01(
    *,
    delta: WorldStateDeltaV01,
    graph: DependencyGraphIndexV01,
    trace_refs: tuple[str, ...],
) -> AffectedSetRequestV01:
    if _world_state_delta_errors(delta):
        raise ValueError("g2e_delta_source_invalid")
    if _dependency_graph_index_errors(graph):
        raise ValueError("g2e_dependency_graph_basis_mismatch")
    if (
        delta.baseline_graph_id != graph.graph_id
        or delta.baseline_graph_version != graph.graph_version
        or delta.transaction_id != graph.transaction_id
        or delta.owning_root_id != graph.owning_root_id
        or delta.domain_id != graph.domain_id
    ):
        raise ValueError("g2e_affected_request_invalid")
    provisional = AffectedSetRequestV01(
        affected_request_id="g2e_affected_set_request_v01:" + _ZERO_SHA256,
        delta_id=delta.delta_id,
        graph_id=graph.graph_id,
        graph_version=graph.graph_version,
        baseline_report_id=delta.baseline_report_id,
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        domain_id=delta.domain_id,
        ordered_changed_field_binding_ids=delta.ordered_changed_field_binding_ids,
        ordered_changed_artifact_binding_ids=(
            delta.ordered_changed_artifact_binding_ids
        ),
        max_nodes=MAX_DEPENDENCY_GRAPH_NODES_V01,
        max_edges=MAX_DEPENDENCY_GRAPH_EDGES_V01,
        max_hops=MAX_AFFECTED_HOPS_V01,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _affected_set_request_errors
    )


def validate_affected_set_request_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        AffectedSetRequestV01,
        "affected_request",
        _affected_set_request_errors,
    )


def affected_set_request_to_plain_data_v01(
    value: AffectedSetRequestV01,
) -> dict[str, object]:
    return _serialize(
        value, AffectedSetRequestV01, _affected_set_request_errors
    )


def rebuild_affected_set_request_identity_v01(
    value: AffectedSetRequestV01,
) -> str:
    return _rebuild(value, AffectedSetRequestV01)


def build_affected_set_result_v01(
    *,
    affected_request_id: str,
    delta_id: str,
    graph_id: str,
    graph_version: str,
    ordered_changed_node_ids: tuple[str, ...],
    ordered_directly_affected_ids: tuple[str, ...],
    ordered_transitively_affected_ids: tuple[str, ...],
    ordered_affected_ids: tuple[str, ...],
    ordered_unaffected_ids: tuple[str, ...],
    visited_rows: tuple[tuple[str, int, str | None], ...],
    traversed_edge_count: int,
    maximum_observed_hops: int,
    trace_refs: tuple[str, ...],
) -> AffectedSetResultV01:
    return _build_affected_set_result_internal_v01(
        affected_request_id=affected_request_id,
        delta_id=delta_id,
        graph_id=graph_id,
        graph_version=graph_version,
        graph_basis_sha256=_ZERO_SHA256,
        ordered_changed_node_ids=ordered_changed_node_ids,
        ordered_directly_affected_ids=ordered_directly_affected_ids,
        ordered_transitively_affected_ids=ordered_transitively_affected_ids,
        ordered_affected_ids=ordered_affected_ids,
        ordered_unaffected_ids=ordered_unaffected_ids,
        visited_rows=visited_rows,
        traversed_edge_count=traversed_edge_count,
        maximum_observed_hops=maximum_observed_hops,
        trace_refs=trace_refs,
    )


def validate_affected_set_result_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        AffectedSetResultV01,
        "affected_closure",
        _affected_set_result_errors,
    )


def affected_set_result_to_plain_data_v01(
    value: AffectedSetResultV01,
) -> dict[str, object]:
    return _serialize(
        value, AffectedSetResultV01, _affected_set_result_errors
    )


def rebuild_affected_set_result_identity_v01(
    value: AffectedSetResultV01,
) -> str:
    return _rebuild(value, AffectedSetResultV01)


def build_dependency_fingerprint_v01(
    *,
    profile: DependencyFingerprintProfileV01,
    graph: DependencyGraphIndexV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    source_artifacts: tuple[KernelArtifactV01, ...],
    policy_version: str,
    schema_versions: tuple[str, ...],
    source_history_hash: str,
) -> str:
    error = _fingerprint_context_error_v01(
        profile=profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=source_artifacts,
        policy_version=policy_version,
        schema_versions=schema_versions,
        source_history_hash=source_history_hash,
    )
    if error:
        raise ValueError(error)
    if (
        not _text_valid(policy_version)
        or not _text_tuple_valid(schema_versions, minimum=1, maximum=64)
        or not _sha256_valid(source_history_hash)
    ):
        raise ValueError("g2e_dependency_fingerprint_preimage_invalid")
    dependency_rows = tuple(
        (
            edge.dependent_artifact_id,
            edge.dependency_artifact_id,
            edge.dependency_field_pointers,
            edge.edge_class,
            edge.canonical_order,
            edge.source_replay_edge_sha256,
        )
        for edge in dependency_edges
    )
    material = (
        profile.domain_separator,
        profile.fingerprint_profile_id,
        profile.fingerprint_profile_version,
        profile.typed_role,
        profile.hash_algorithm,
        profile.canonicalization_profile_id,
        (graph.graph_id, graph.graph_basis_sha256),
        (
            graph.graph_version,
            graph.transaction_id,
            graph.owning_root_id,
            graph.domain_id,
        ),
        policy_version,
        schema_versions,
        source_history_hash,
        dependency_rows,
        _fingerprint_source_rows_v01(source_artifacts),
    )
    return hashlib.sha256(canonical_json_bytes_v01(material)).hexdigest()


def validate_dependency_fingerprint_against_sources_v01(
    value: str,
    *,
    profile: DependencyFingerprintProfileV01,
    graph: DependencyGraphIndexV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    source_artifacts: tuple[KernelArtifactV01, ...],
    policy_version: str,
    schema_versions: tuple[str, ...],
    source_history_hash: str,
) -> ContinuousDeltaValidationReportV01:
    reason: str | None = None
    try:
        expected = build_dependency_fingerprint_v01(
            profile=profile,
            graph=graph,
            dependency_edges=dependency_edges,
            source_artifacts=source_artifacts,
            policy_version=policy_version,
            schema_versions=schema_versions,
            source_history_hash=source_history_hash,
        )
        if not _sha256_valid(value) or value != expected:
            reason = "g2e_dependency_fingerprint_mismatch"
    except ValueError as exc:
        candidate = exc.args[0] if len(exc.args) == 1 else None
        reason = (
            candidate
            if candidate in PUBLIC_G2E_REASON_CODES_V01
            else "g2e_dependency_fingerprint_preimage_invalid"
        )
    return _contextual_report_v01(
        validation_target="dependency_fingerprint_against_sources",
        validated_object_id=value if reason is None else None,
        failure_stage="fingerprint_context",
        reason_codes=() if reason is None else (reason,),
    )


def project_integrity_replay_dependency_edges_v01(
    *,
    manifest: ArtifactManifestV01,
    replay: ReplayVerificationResultV01,
    source_artifacts: tuple[KernelArtifactV01, ...],
    graph_version: str,
    transaction_id: str,
    owning_root_id: str,
    domain_id: str,
    policy_version: str,
    schema_versions: tuple[str, ...],
    source_history_hash: str,
    edge_projection_bindings: tuple[
        tuple[str, str, tuple[str, ...], str], ...
    ],
) -> tuple[str, tuple[DeltaDependencyEdgeV01, ...]]:
    source_errors = _manifest_replay_source_errors_v01(
        manifest=manifest,
        replay=replay,
        source_artifacts=source_artifacts,
    )
    if source_errors:
        raise ValueError(source_errors[0])
    if graph_version != CONTINUOUS_DELTA_GRAPH_VERSION_V01:
        raise ValueError("g2e_dependency_graph_version_mismatch")
    if transaction_id != manifest.transaction_id:
        raise ValueError("g2e_dependency_edge_cross_transaction")
    if any(item.owner_root_id != owning_root_id for item in source_artifacts):
        raise ValueError("g2e_dependency_edge_cross_root")
    if (
        not _text_valid(domain_id)
        or not _text_valid(policy_version)
        or not _text_tuple_valid(schema_versions, minimum=1, maximum=64)
        or not _sha256_valid(source_history_hash)
    ):
        raise ValueError("g2e_dependency_edge_invalid")
    if (
        type(edge_projection_bindings) is not tuple
        or len(edge_projection_bindings) > MAX_DEPENDENCY_GRAPH_EDGES_V01
    ):
        raise ValueError("g2e_dependency_graph_bounds_exceeded")
    node_ids = tuple(item.artifact_id for item in manifest.artifacts)
    positions = {artifact_id: index for index, artifact_id in enumerate(node_ids)}
    descriptors: list[tuple[str, str, tuple[str, ...], str]] = []
    payload_by_id = {
        item.artifact_id: _artifact_plain_v01(item)["payload"]
        for item in source_artifacts
    }
    for row in edge_projection_bindings:
        if type(row) is not tuple or len(row) != 4:
            raise ValueError("g2e_dependency_edge_invalid")
        dependent, dependency, pointers, edge_class = row
        if dependent not in positions:
            raise ValueError("g2e_dependency_edge_unknown_dependent")
        if dependency not in positions:
            raise ValueError("g2e_dependency_edge_unknown_source")
        if dependent == dependency:
            raise ValueError("g2e_dependency_edge_self")
        if (
            type(pointers) is not tuple
            or len(pointers) > MAX_DEPENDENCY_GRAPH_NODES_V01
            or len(pointers) != len(set(pointers))
            or any(not _json_pointer_valid(pointer) for pointer in pointers)
            or not _token_valid(edge_class)
        ):
            raise ValueError("g2e_dependency_edge_invalid")
        for pointer in pointers:
            _resolve_json_pointer_v01(payload_by_id[dependency], pointer)
        descriptors.append((dependent, dependency, pointers, edge_class))
    descriptor_tuple = tuple(descriptors)
    if len(descriptor_tuple) != len(set(descriptor_tuple)):
        raise ValueError("g2e_dependency_edge_duplicate")
    descriptor_pair_rows = tuple((row[0], row[1]) for row in descriptor_tuple)
    if len(descriptor_pair_rows) != len(set(descriptor_pair_rows)):
        raise ValueError("g2e_dependency_edge_duplicate")
    replay_pairs = tuple(
        (edge.artifact_id, edge.depends_on_artifact_id)
        for edge in replay.reconstructed_dependency_edges
    )
    if _graph_has_cycle_v01(node_ids, descriptor_tuple):
        raise ValueError("g2e_dependency_graph_cycle")
    descriptor_pairs = set(descriptor_pair_rows)
    replay_pair_set = set(replay_pairs)
    if descriptor_pairs - replay_pair_set:
        raise ValueError("g2e_dependency_edge_unknown_source")
    if replay_pair_set - descriptor_pairs:
        raise ValueError("g2e_dependency_graph_missing_edge")
    normalized = _normalized_edge_descriptors_v01(descriptor_tuple, positions)
    source_manifest_id = _source_manifest_id_v01(manifest)
    graph_basis = _graph_basis_sha256_v01(
        graph_version=graph_version,
        source_manifest_id=source_manifest_id,
        source_manifest_hash=manifest.manifest_hash,
        source_replay_id=replay.replay_id,
        transaction_id=transaction_id,
        owning_root_id=owning_root_id,
        domain_id=domain_id,
        policy_version=policy_version,
        schema_versions=schema_versions,
        source_history_hash=source_history_hash,
        source_artifacts=source_artifacts,
        replay_pairs=replay_pairs,
        normalized_descriptors=normalized,
    )
    edges = []
    for canonical_order, descriptor in enumerate(normalized, start=1):
        dependent, dependency, pointers, edge_class = descriptor
        replay_edge_sha256 = _source_replay_edge_sha256_v01(
            source_manifest_id=source_manifest_id,
            source_manifest_hash=manifest.manifest_hash,
            source_replay_id=replay.replay_id,
            dependent_artifact_id=dependent,
            dependency_artifact_id=dependency,
            positions=positions,
        )
        edges.append(
            build_delta_dependency_edge_v01(
                graph_basis_sha256=graph_basis,
                graph_version=graph_version,
                dependent_artifact_id=dependent,
                dependency_artifact_id=dependency,
                dependency_field_pointers=pointers,
                edge_class=edge_class,
                transaction_id=transaction_id,
                owning_root_id=owning_root_id,
                domain_id=domain_id,
                canonical_order=canonical_order,
                source_replay_edge_sha256=replay_edge_sha256,
                trace_refs=(
                    source_manifest_id,
                    manifest.manifest_hash,
                    replay.replay_id,
                ),
            )
        )
    return graph_basis, tuple(edges)


def compute_affected_set_v01(
    *,
    request: AffectedSetRequestV01,
    delta: WorldStateDeltaV01,
    graph: DependencyGraphIndexV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
) -> AffectedSetResultV01:
    changed_nodes, positions = _carrier_context_v01(
        request=request,
        delta=delta,
        graph=graph,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        baseline_source_artifacts=baseline_source_artifacts,
        observed_source_artifacts=observed_source_artifacts,
    )
    walk = _affected_walk_v01(
        changed_nodes=changed_nodes,
        graph=graph,
        dependency_edges=dependency_edges,
        positions=positions,
    )
    return _build_affected_set_result_internal_v01(
        affected_request_id=request.affected_request_id,
        delta_id=delta.delta_id,
        graph_id=graph.graph_id,
        graph_version=graph.graph_version,
        graph_basis_sha256=graph.graph_basis_sha256,
        ordered_changed_node_ids=walk["ordered_changed_node_ids"],
        ordered_directly_affected_ids=walk["ordered_directly_affected_ids"],
        ordered_transitively_affected_ids=walk[
            "ordered_transitively_affected_ids"
        ],
        ordered_affected_ids=walk["ordered_affected_ids"],
        ordered_unaffected_ids=walk["ordered_unaffected_ids"],
        visited_rows=walk["visited_rows"],
        traversed_edge_count=walk["traversed_edge_count"],
        maximum_observed_hops=walk["maximum_observed_hops"],
        trace_refs=request.trace_refs,
    )


def validate_affected_set_against_graph_v01(
    value: AffectedSetResultV01,
    *,
    request: AffectedSetRequestV01,
    delta: WorldStateDeltaV01,
    graph: DependencyGraphIndexV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
) -> ContinuousDeltaValidationReportV01:
    reason: str | None = None
    expected: AffectedSetResultV01 | None = None
    try:
        if _affected_set_result_errors(value):
            raise ValueError(_affected_set_result_errors(value)[0])
        changed_nodes, positions = _carrier_context_v01(
            request=request,
            delta=delta,
            graph=graph,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            baseline_source_artifacts=baseline_source_artifacts,
            observed_source_artifacts=observed_source_artifacts,
        )
        walk = _affected_walk_v01(
            changed_nodes=changed_nodes,
            graph=graph,
            dependency_edges=dependency_edges,
            positions=positions,
        )
        expected = _build_affected_set_result_internal_v01(
            affected_request_id=request.affected_request_id,
            delta_id=delta.delta_id,
            graph_id=graph.graph_id,
            graph_version=graph.graph_version,
            graph_basis_sha256=graph.graph_basis_sha256,
            ordered_changed_node_ids=walk["ordered_changed_node_ids"],
            ordered_directly_affected_ids=walk["ordered_directly_affected_ids"],
            ordered_transitively_affected_ids=walk[
                "ordered_transitively_affected_ids"
            ],
            ordered_affected_ids=walk["ordered_affected_ids"],
            ordered_unaffected_ids=walk["ordered_unaffected_ids"],
            visited_rows=walk["visited_rows"],
            traversed_edge_count=walk["traversed_edge_count"],
            maximum_observed_hops=walk["maximum_observed_hops"],
            trace_refs=request.trace_refs,
        )
        if value.ordered_changed_node_ids != expected.ordered_changed_node_ids:
            reason = "g2e_delta_binding_set_mismatch"
        elif not set(expected.ordered_affected_ids).issubset(
            value.ordered_affected_ids
        ):
            reason = "g2e_affected_reachable_omitted"
        elif not set(value.ordered_affected_ids).issubset(
            expected.ordered_affected_ids
        ):
            reason = "g2e_affected_unrelated_injected"
        elif (
            value.ordered_directly_affected_ids
            != expected.ordered_directly_affected_ids
            or value.ordered_transitively_affected_ids
            != expected.ordered_transitively_affected_ids
            or value.ordered_affected_ids != expected.ordered_affected_ids
            or value.ordered_unaffected_ids != expected.ordered_unaffected_ids
        ):
            reason = "g2e_affected_ordering_invalid"
        elif value.closure_proof_sha256 != expected.closure_proof_sha256:
            reason = "g2e_affected_proof_invalid"
        elif value != expected:
            reason = "g2e_affected_closure_incomplete"
    except ValueError as exc:
        candidate = exc.args[0] if len(exc.args) == 1 else None
        reason = (
            candidate
            if candidate in PUBLIC_G2E_REASON_CODES_V01
            else "g2e_affected_closure_incomplete"
        )
    return _contextual_report_v01(
        validation_target="affected_set_completeness",
        validated_object_id=(
            value.affected_set_id
            if reason is None and type(value) is AffectedSetResultV01
            else None
        ),
        failure_stage="affected_completeness",
        reason_codes=() if reason is None else (reason,),
    )


def _invalidation_record_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not ArtifactInvalidationRecordV01:
        return ("g2e_invalidation_record_invalid",)
    errors: list[str] = []
    if (
        not _prefixed_identity_valid(
            value.affected_set_id, "g2e_affected_set_result_v01:"
        )
        or not _text_valid(value.artifact_id)
        or not _text_valid(value.artifact_type)
        or not _prefixed_identity_valid(
            value.triggering_delta_id, "g2e_world_state_delta_v01:"
        )
        or not _text_tuple_valid(
            value.triggering_binding_ids, minimum=1, maximum=MAX_CHANGED_BINDINGS_V01
        )
        or not _text_tuple_valid(value.trace_refs, minimum=1)
        or type(value.root_review_required) is not bool
    ):
        errors.append("g2e_invalidation_record_invalid")
    if value.invalidation_reason_class not in G2E_INVALIDATION_REASON_CLASSES_V01:
        errors.append("g2e_invalidation_reason_invalid")
    if value.deleted is not False:
        errors.append("g2e_invalidation_deletion_forbidden")
    if value.historical_artifact_preserved is not True:
        errors.append("g2e_invalidation_history_mutation")
    if value.predecessor_artifact_id != value.artifact_id:
        errors.append("g2e_invalidation_predecessor_mismatch")
    if value.superseded_by_artifact_id is not None:
        errors.append("g2e_invalidation_supersession_mismatch")
    if (
        value.current_eligible_before is not True
        or value.current_eligible_after is not False
        or value.g2a_packet_relation not in G2E_G2A_PACKET_RELATIONS_V01
        or value.g2b_reuse_relation not in G2E_G2B_REUSE_RELATIONS_V01
        or value.g2c_route_relation not in G2E_G2C_ROUTE_RELATIONS_V01
    ):
        errors.append("g2e_invalidation_record_invalid")
    expected_root_review = bool(
        value.g2a_packet_relation == "PACKET_ROOT_REVIEW_REQUIRED"
        or value.g2b_reuse_relation == "REUSE_CERTIFICATE_STALE"
        or value.g2c_route_relation == "ROUTE_REVALIDATION_REQUIRED"
    )
    if value.root_review_required is not expected_root_review:
        errors.append("g2e_invalidation_record_invalid")
    if _identity_errors(value):
        errors.append("g2e_invalidation_history_mutation")
    return _ordered_reasons(errors)


def _report_reason_codes_v01(
    *,
    unresolved: tuple[str, ...],
    packet_ids: tuple[str, ...],
    certificate_ids: tuple[str, ...],
    route_ids: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if unresolved:
        reasons.append("g2e_invalidation_record_invalid")
    if packet_ids:
        reasons.append("g2e_invalidation_g2a_root_binding_required")
    if certificate_ids:
        reasons.append("g2e_invalidation_g2b_reuse_still_current")
    if route_ids:
        reasons.append("g2e_route_revalidation_required")
    return _ordered_reasons(reasons)


def _invalidation_report_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not InvalidationReportV01:
        return ("g2e_invalidation_record_invalid",)
    errors: list[str] = []
    bounded_nonempty = (
        value.ordered_invalidation_record_ids,
        value.ordered_invalidated_artifact_ids,
        value.ordered_historical_artifact_ids,
    )
    bounded_optional = (
        value.ordered_unresolved_artifact_ids,
        value.ordered_packet_invalidation_candidate_ids,
        value.ordered_stale_reuse_certificate_ids,
        value.ordered_route_revalidation_ids,
    )
    if (
        not _prefixed_identity_valid(
            value.affected_set_id, "g2e_affected_set_result_v01:"
        )
        or any(
            not _text_tuple_valid(rows, minimum=1, maximum=256)
            for rows in bounded_nonempty
        )
        or any(
            not _text_tuple_valid(rows, maximum=256)
            for rows in bounded_optional
        )
        or len(value.ordered_invalidation_record_ids)
        != len(value.ordered_invalidated_artifact_ids)
        or value.ordered_historical_artifact_ids
        != value.ordered_invalidated_artifact_ids
    ):
        errors.append("g2e_invalidation_record_invalid")
    expected_reasons = _report_reason_codes_v01(
        unresolved=value.ordered_unresolved_artifact_ids,
        packet_ids=value.ordered_packet_invalidation_candidate_ids,
        certificate_ids=value.ordered_stale_reuse_certificate_ids,
        route_ids=value.ordered_route_revalidation_ids,
    )
    expected_status = "PASS" if not expected_reasons else "FAIL_CLOSED"
    if (
        value.report_status != expected_status
        or value.reason_codes != expected_reasons
        or not _ordered_public_reasons_valid(value.reason_codes)
        or value.root_review_required
        is not bool(
            value.ordered_packet_invalidation_candidate_ids
            or value.ordered_stale_reuse_certificate_ids
            or value.ordered_route_revalidation_ids
        )
    ):
        errors.append("g2e_invalidation_record_invalid")
    errors.extend(_zero_boundary_errors(value))
    if _identity_errors(value):
        errors.append("g2e_invalidation_record_invalid")
    return _ordered_reasons(errors)


def _no_cache_state_sha256_v01() -> str:
    return _domain_sha256_v01(
        NO_CACHE_STATE_DOMAIN_V01,
        ("fixed_empty_cache_profile", ()),
    )


def _preservation_proof_sha256_v01(value: PreservationProofV01) -> str:
    material = tuple(
        (field.name, _plain_value(getattr(value, field.name)))
        for field in fields(PreservationProofV01)
        if field.name not in {"preservation_proof_id", "proof_sha256"}
    )
    return _domain_sha256_v01(PRESERVATION_PROOF_DOMAIN_V01, material)


def _preservation_reason_codes_v01(
    *,
    before_artifact: tuple[str, ...],
    after_artifact: tuple[str, ...],
    before_payload: tuple[str, ...],
    after_payload: tuple[str, ...],
    before_identity: tuple[str, ...],
    after_identity: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if before_artifact != after_artifact or before_payload != after_payload:
        reasons.append("g2e_preserved_artifact_changed")
    if before_identity != after_identity:
        reasons.append("g2e_preserved_identity_changed")
    return _ordered_reasons(reasons)


def _preservation_proof_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not PreservationProofV01:
        return ("g2e_preservation_proof_invalid",)
    errors: list[str] = []
    tuple_rows = (
        value.ordered_preserved_artifact_ids,
        value.ordered_before_artifact_sha256,
        value.ordered_after_artifact_sha256,
        value.ordered_before_payload_sha256,
        value.ordered_after_payload_sha256,
        value.ordered_before_identity_ids,
        value.ordered_after_identity_ids,
    )
    lengths = tuple(len(row) for row in tuple_rows if type(row) is tuple)
    if (
        len(lengths) != len(tuple_rows)
        or len(set(lengths)) != 1
        or not _text_tuple_valid(
            value.ordered_preserved_artifact_ids, maximum=256
        )
        or not _text_tuple_valid(
            value.ordered_before_identity_ids, maximum=256
        )
        or not _text_tuple_valid(
            value.ordered_after_identity_ids, maximum=256
        )
        or any(
            not all(_sha256_valid(item) for item in row)
            for row in (
                value.ordered_before_artifact_sha256,
                value.ordered_after_artifact_sha256,
                value.ordered_before_payload_sha256,
                value.ordered_after_payload_sha256,
            )
        )
        or not _text_valid(value.baseline_graph_id)
        or not _prefixed_identity_valid(
            value.affected_set_id, "g2e_affected_set_result_v01:"
        )
    ):
        errors.append("g2e_preservation_proof_invalid")
    no_cache = _no_cache_state_sha256_v01()
    if (
        value.before_cache_state_sha256 != no_cache
        or value.after_cache_state_sha256 != no_cache
        or value.mutable_global_write_count != 0
    ):
        errors.append("g2e_preservation_cache_mutation")
    if value.object_identity_used_as_proof is not False:
        errors.append("g2e_preservation_proof_invalid")
    expected_reasons = _preservation_reason_codes_v01(
        before_artifact=value.ordered_before_artifact_sha256,
        after_artifact=value.ordered_after_artifact_sha256,
        before_payload=value.ordered_before_payload_sha256,
        after_payload=value.ordered_after_payload_sha256,
        before_identity=value.ordered_before_identity_ids,
        after_identity=value.ordered_after_identity_ids,
    )
    expected_preserved = not expected_reasons
    expected_status = "PASS" if expected_preserved else "FAIL_CLOSED"
    if (
        value.byte_identity_preserved is not expected_preserved
        or value.status != expected_status
        or value.reason_codes != expected_reasons
        or not _ordered_public_reasons_valid(value.reason_codes)
    ):
        errors.append("g2e_preservation_proof_invalid")
    if value.proof_sha256 != _preservation_proof_sha256_v01(value):
        errors.append("g2e_preservation_proof_invalid")
    if _identity_errors(value):
        errors.append("g2e_preservation_proof_invalid")
    return _ordered_reasons(errors)


def _zero_operation_count_errors_v01(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for field_name in (
        "provider_calls",
        "model_calls",
        "network_calls",
        "connector_calls",
        "external_drs_calls",
        "action_commit_packets_created",
        "permissions_created",
        "receipts_created",
        "final_outputs_created",
        "drs_writes",
        "authority_created_count",
        "real_world_effects_count",
    ):
        if hasattr(value, field_name) and (
            type(getattr(value, field_name)) is not int
            or getattr(value, field_name) != 0
        ):
            errors.append("g2e_zero_operation_boundary_violated")
    return _ordered_reasons(errors)


def _selective_recomputation_plan_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not SelectiveRecomputationPlanV01:
        return ("g2e_recomputation_plan_invalid",)
    errors: list[str] = []
    if (
        not _prefixed_identity_valid(value.delta_id, "g2e_world_state_delta_v01:")
        or not _prefixed_identity_valid(
            value.affected_set_id, "g2e_affected_set_result_v01:"
        )
        or not _prefixed_identity_valid(
            value.invalidation_report_id, "g2e_invalidation_report_v01:"
        )
        or any(
            not _text_valid(item)
            for item in (
                value.source_route_eligibility_artifact_id,
                value.source_topology_id,
                value.accepted_mode,
                value.accepted_scope_ref,
                value.transition_profile_id,
            )
        )
    ):
        errors.append("g2e_recomputation_plan_invalid")
    for row in (
        value.ordered_affected_cell_ids,
        value.ordered_affected_artifact_ids,
        value.ordered_work_node_ids,
        value.ordered_preserved_artifact_ids,
        value.trace_refs,
    ):
        if not _text_tuple_valid(row, maximum=1024):
            errors.append("g2e_recomputation_plan_invalid")
    if value.plan_status == "PASS" and (
        not value.ordered_affected_cell_ids or not value.ordered_work_node_ids
    ):
        errors.append("g2e_recomputation_plan_invalid")
    for bound in (
        value.max_work_items,
        value.max_queue_entries,
        value.max_wall_time_units,
        value.max_token_budget,
        value.max_provider_calls,
    ):
        if type(bound) is not int or bound < 0:
            errors.append("g2e_recomputation_budget_exceeded")
    if (
        type(value.max_work_items) is int
        and value.max_work_items > MAX_DEPENDENCY_GRAPH_NODES_V01
    ) or (
        type(value.max_queue_entries) is int
        and value.max_queue_entries > MAX_DEPENDENCY_GRAPH_EDGES_V01
    ):
        errors.append("g2e_recomputation_budget_exceeded")
    if value.max_provider_calls != 0:
        errors.append("g2e_zero_operation_boundary_violated")
    if value.root_review_required is not True:
        errors.append("g2e_authority_boundary_violated")
    if (
        value.plan_status not in VALIDATION_STATUSES_V01
        or not _ordered_public_reasons_valid(value.reason_codes)
        or value.plan_status != ("PASS" if not value.reason_codes else "FAIL_CLOSED")
    ):
        errors.append("g2e_status_invalid")
    if _identity_errors(value):
        errors.append("g2e_recomputation_plan_invalid")
    return _ordered_reasons(errors)


def _recomputed_artifact_binding_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not RecomputedArtifactBindingV01:
        return ("g2e_recomputation_result_invalid",)
    errors: list[str] = []
    if not _prefixed_identity_valid(
        value.recomputation_plan_id, "g2e_selective_recomputation_plan_v01:"
    ):
        errors.append("g2e_recomputation_plan_invalid")
    if any(
        not _text_valid(item)
        for item in (
            value.prior_artifact_id,
            value.new_artifact_id,
            value.predecessor_relation,
            value.supersession_relation,
            value.source_cell_id,
            value.source_queue_entry_id,
            value.g2d_cell_result_ref,
            value.g2d_runtime_report_ref,
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    if not _sha256_valid(value.prior_payload_sha256) or not _sha256_valid(
        value.new_payload_sha256
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        value.prior_artifact_id == value.new_artifact_id
        or value.prior_payload_sha256 == value.new_payload_sha256
    ):
        errors.append("g2e_recomputation_in_place_forbidden")
    if not _text_tuple_valid(value.derivation_refs, minimum=1) or not _text_tuple_valid(
        value.trace_refs
    ):
        errors.append("g2e_recomputation_result_invalid")
    if _identity_errors(value):
        errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def _selective_recomputation_result_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not SelectiveRecomputationResultV01:
        return ("g2e_recomputation_result_invalid",)
    errors: list[str] = []
    if (
        not _prefixed_identity_valid(
            value.recomputation_plan_id, "g2e_selective_recomputation_plan_v01:"
        )
        or not _prefixed_identity_valid(
            value.preservation_proof_id, "g2e_preservation_proof_v01:"
        )
        or any(
            not _text_valid(item)
            for item in (
                value.baseline_runtime_report_id,
                value.recomputed_runtime_report_id,
                value.parent_return_transition_decision_id,
            )
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    if value.baseline_runtime_report_id == value.recomputed_runtime_report_id:
        errors.append("g2e_recomputation_in_place_forbidden")
    for row in (
        value.ordered_recomputed_binding_ids,
        value.ordered_invalidated_downstream_ids,
        value.ordered_recomputed_artifact_ids,
        value.ordered_preserved_artifact_ids,
        value.ordered_unresolved_artifact_ids,
        value.ordered_partial_failure_ids,
    ):
        if not _text_tuple_valid(row, maximum=1024):
            errors.append("g2e_recomputation_result_invalid")
    if (
        value.result_status not in VALIDATION_STATUSES_V01
        or not _ordered_public_reasons_valid(value.reason_codes)
        or value.result_status != ("PASS" if not value.reason_codes else "FAIL_CLOSED")
    ):
        errors.append("g2e_status_invalid")
    if value.result_status == "PASS" and (
        not value.ordered_recomputed_binding_ids
        or not value.ordered_recomputed_artifact_ids
        or value.ordered_unresolved_artifact_ids
        or value.ordered_partial_failure_ids
    ):
        errors.append("g2e_recomputation_result_invalid")
    errors.extend(_zero_operation_count_errors_v01(value))
    if _identity_errors(value):
        errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def _continuous_delta_runtime_trace_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not ContinuousDeltaRuntimeTraceV01:
        return ("g2e_recomputation_result_invalid",)
    errors: list[str] = []
    identity_rows = (
        (value.delta_id, "g2e_world_state_delta_v01:"),
        (value.graph_id, "g2e_dependency_graph_index_v01:"),
        (value.affected_set_id, "g2e_affected_set_result_v01:"),
        (value.invalidation_report_id, "g2e_invalidation_report_v01:"),
        (value.preservation_proof_id, "g2e_preservation_proof_v01:"),
        (value.recomputation_plan_id, "g2e_selective_recomputation_plan_v01:"),
        (value.recomputation_result_id, "g2e_selective_recomputation_result_v01:"),
    )
    if any(not _prefixed_identity_valid(item, prefix) for item, prefix in identity_rows):
        errors.append("g2e_recomputation_result_invalid")
    if any(
        not _text_valid(item)
        for item in (
            value.plan_root_decision_input_id,
            value.plan_root_decision_id,
            value.final_root_decision_input_id,
            value.final_root_decision_id,
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    for row in (
        value.ordered_transition_decision_ids,
        value.ordered_causal_ref_ids,
        value.ordered_source_artifact_ids,
        value.ordered_downstream_artifact_ids,
    ):
        if not _text_tuple_valid(row, minimum=1, maximum=1024):
            errors.append("g2e_recomputation_result_invalid")
    errors.extend(_zero_operation_count_errors_v01(value))
    if _identity_errors(value):
        errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def _continuous_delta_runtime_report_errors_v01(value: object) -> tuple[str, ...]:
    if type(value) is not ContinuousDeltaRuntimeReportV01:
        return ("g2e_recomputation_result_invalid",)
    errors: list[str] = []
    identity_rows = (
        (value.delta_id, "g2e_world_state_delta_v01:"),
        (value.graph_id, "g2e_dependency_graph_index_v01:"),
        (value.affected_set_id, "g2e_affected_set_result_v01:"),
        (value.invalidation_report_id, "g2e_invalidation_report_v01:"),
        (value.preservation_proof_id, "g2e_preservation_proof_v01:"),
        (value.recomputation_plan_id, "g2e_selective_recomputation_plan_v01:"),
        (value.recomputation_result_id, "g2e_selective_recomputation_result_v01:"),
        (value.trace_id, "g2e_continuous_delta_runtime_trace_v01:"),
    )
    if any(not _prefixed_identity_valid(item, prefix) for item, prefix in identity_rows):
        errors.append("g2e_recomputation_result_invalid")
    if any(
        not _text_valid(item)
        for item in (
            value.report_version,
            value.profile_id,
            value.baseline_report_id,
            value.plan_root_decision_input_id,
            value.plan_root_decision_id,
            value.final_root_decision_input_id,
            value.final_root_decision_id,
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    if not _text_tuple_valid(value.ordered_source_binding_ids, minimum=1) or any(
        not _prefixed_identity_valid(item, "g2e_delta_source_binding_v01:")
        for item in value.ordered_source_binding_ids
    ):
        errors.append("g2e_delta_source_binding_set_mismatch")
    for count in (
        value.changed_count,
        value.directly_affected_count,
        value.transitively_affected_count,
        value.invalidated_count,
        value.recomputed_count,
        value.preserved_count,
        value.unresolved_count,
    ):
        if type(count) is not int or count < 0:
            errors.append("g2e_recomputation_result_invalid")
    if (
        value.report_status not in VALIDATION_STATUSES_V01
        or not _ordered_public_reasons_valid(value.reason_codes)
        or value.report_status != ("PASS" if not value.reason_codes else "FAIL_CLOSED")
        or type(value.root_review_required) is not bool
    ):
        errors.append("g2e_status_invalid")
    if value.report_status == "PASS" and (
        not value.root_review_required
        or value.recomputed_count == 0
        or value.unresolved_count != 0
    ):
        errors.append("g2e_recomputation_result_invalid")
    errors.extend(_zero_operation_count_errors_v01(value))
    if _identity_errors(value):
        errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def _timestamp_epoch_microseconds_v01(value: object) -> int:
    parsed = _parse_aware_timestamp_v01(value).astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = parsed - epoch
    return (
        delta.days * 86_400_000_000
        + delta.seconds * 1_000_000
        + delta.microseconds
    )


def _bool_tuple_validation_pass_v01(result: object) -> bool:
    return (
        type(result) is tuple
        and len(result) == 2
        and result[0] is True
        and result[1] == ()
    )


def _source_context_shape_valid_v01(value: object) -> bool:
    return bool(
        type(value) is ContinuousDeltaSourceContextV01
        and type(value.baseline_source_artifacts) is tuple
        and type(value.observed_source_artifacts) is tuple
        and type(value.g2a_current_observations) is tuple
    )


def _source_context_reason_v01(value: object) -> str | None:
    if not _source_context_shape_valid_v01(value):
        return "g2e_delta_source_invalid"
    assert type(value) is ContinuousDeltaSourceContextV01
    if (
        value.g2b_writeback_evidence is not None
        or value.post_vv_profile is not None
        or value.gt_profile is not None
    ):
        return "g2e_delta_source_unvalidated"
    try:
        manifest_errors = _manifest_replay_source_errors_v01(
            manifest=value.integrity_manifest,
            replay=value.integrity_replay,
            source_artifacts=value.baseline_source_artifacts,
        )
        if manifest_errors:
            return "g2e_delta_source_unvalidated"
        if (
            not value.baseline_source_artifacts
            or len(value.baseline_source_artifacts)
            != len(value.observed_source_artifacts)
        ):
            return "g2e_delta_source_unvalidated"
        for baseline, observed in zip(
            value.baseline_source_artifacts,
            value.observed_source_artifacts,
        ):
            baseline_plain = _artifact_plain_v01(baseline)
            observed_plain = _artifact_plain_v01(observed)
            if baseline.artifact_id == observed.artifact_id:
                if canonical_json_bytes_v01(baseline_plain) != canonical_json_bytes_v01(
                    observed_plain
                ):
                    return "g2e_delta_source_unvalidated"
            elif (
                baseline.artifact_type != observed.artifact_type
                or baseline.transaction_id != observed.transaction_id
                or baseline.owner_root_id != observed.owner_root_id
                or baseline.artifact_id not in observed.parent_refs
            ):
                return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_action_commit_packet_registry_v02(
                value.g2a_registry
            )
        ):
            return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                value.g2a_packet
            )
        ):
            return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_mandatory_dependency_local_root_acceptance_v01(
                value.g2a_packet
            )
        ):
            return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_dependency_set_candidate_v01(
                value.g2a_dependency_candidate
            )
        ):
            return "g2e_delta_source_unvalidated"
        if (
            value.g2a_packet.canonical_projection.dependency_candidate
            != value.g2a_dependency_candidate
            or not value.g2a_current_observations
            or any(
                not _bool_tuple_validation_pass_v01(
                    action_commit_packet.validate_action_dependency_current_observation_v01(
                        observation
                    )
                )
                for observation in value.g2a_current_observations
            )
        ):
            return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_action_invalidation_evidence_v01(
                value.g2a_root_invalidation_material
            )
        ) or not _bool_tuple_validation_pass_v01(
            action_commit_packet.validate_action_invalidation_evidence_against_packet_v01(
                value.g2a_root_invalidation_material,
                value.g2a_packet,
            )
        ):
            return "g2e_delta_source_unvalidated"
        if not _bool_tuple_validation_pass_v01(
            drs_memory_resolution.validate_drs_resolution_report_v01(
                value.g2b_resolution_report
            )
        ) or not _bool_tuple_validation_pass_v01(
            reuse_certificate.validate_reuse_certificate_v01(
                value.g2b_reuse_certificate
            )
        ):
            return "g2e_delta_source_unvalidated"
        if (
            value.g2b_resolution_report.reuse_certificate
            != value.g2b_reuse_certificate
        ):
            return "g2e_delta_source_unvalidated"
        g2c_report = validate_execution_mode_source_context_v01(
            value.g2c_source_context
        )
        if g2c_report.validation_status != "PASS":
            return "g2e_delta_source_unvalidated"
        if (
            value.g2c_source_context.g2b_writeback_evidence is not None
            or value.g2c_source_context.g2b_resolution_report
            != value.g2b_resolution_report
        ):
            return "g2e_delta_source_unvalidated"
        if _artifact_plain_v01(value.baseline_g2c_route_eligibility_artifact) is None:
            return "g2e_delta_source_unvalidated"
        if type(value.baseline_g2d_execution_bundle) is not FractalRuntimeExecutionBundleV02:
            return "g2e_delta_source_unvalidated"
        bundle = value.baseline_g2d_execution_bundle
        if validate_fractal_runtime_execution_bundle_v02(bundle).status != "PASS":
            return "g2e_delta_source_unvalidated"
        dedicated_carrier_ids = {
            value.g2a_packet.packet_identity.packet_id,
            value.g2b_reuse_certificate.certificate_id,
            value.baseline_g2c_route_eligibility_artifact.artifact_id,
            bundle.report_artifact.artifact_id,
        }
        if dedicated_carrier_ids.intersection(
            artifact.artifact_id
            for artifact in value.baseline_source_artifacts
            + value.observed_source_artifacts
        ):
            return "g2e_delta_source_unvalidated"
        if validate_root_decision_kernel_v01(value.root_kernel):
            return "g2e_delta_source_unvalidated"
    except Exception:
        return "g2e_delta_source_unvalidated"

    bundle = value.baseline_g2d_execution_bundle
    router_input = bundle.source_context.router_input
    snapshot = router_input.local_routing_snapshot
    packet_projection = value.g2a_packet.canonical_projection
    report = value.g2b_resolution_report
    transaction_id = router_input.transaction_id
    if (
        value.integrity_manifest.transaction_id != transaction_id
        or any(
            artifact.transaction_id != transaction_id
            for artifact in value.baseline_source_artifacts
            + value.observed_source_artifacts
        )
        or packet_projection.transaction_id != transaction_id
        or report.query.query_id != transaction_id
        or value.baseline_g2c_route_eligibility_artifact.transaction_id
        != transaction_id
        or bundle.runtime_report.transaction_id != transaction_id
    ):
        return "g2e_delta_cross_transaction"
    if (
        report.query.domain != snapshot.domain_id
        or bundle.runtime_report.domain_id != snapshot.domain_id
    ):
        return "g2e_delta_cross_domain"
    if (
        packet_projection.owning_local_root_id != router_input.owning_root_id
        or report.query.owning_local_root_id != router_input.owning_root_id
        or value.baseline_g2c_route_eligibility_artifact.owner_root_id
        != router_input.owning_root_id
        or any(
            artifact.owner_root_id != router_input.owning_root_id
            for artifact in value.baseline_source_artifacts
            + value.observed_source_artifacts
        )
    ):
        return "g2e_delta_cross_root"
    if value.g2b_reuse_certificate.policy_version != report.query.policy_version:
        return "g2e_delta_policy_version_mismatch"
    if value.g2b_reuse_certificate.schema_versions != report.query.schema_versions:
        return "g2e_delta_schema_version_mismatch"
    if (
        value.g2b_reuse_certificate.source_history_hash
        != report.query_evaluations[0].source_history_hash
    ):
        return "g2e_dependency_source_history_mismatch"
    report_artifact_payload = _artifact_plain_v01(bundle.report_artifact)["payload"]
    if (
        bundle.runtime_report.report_status != "PASS"
        or type(report_artifact_payload) is not dict
        or report_artifact_payload.get("report_id")
        != bundle.runtime_report.report_id
    ):
        return "g2e_delta_baseline_stale"

    ceiling = snapshot.evaluation_time_epoch_seconds
    if (
        type(ceiling) is not int
        or value.g2c_source_context.g2a_evaluation_time != ceiling
        or value.g2c_source_context.g2b_use_time != ceiling
        or value.g2a_root_invalidation_material.evaluation_time != ceiling
    ):
        return "g2e_delta_source_unvalidated"
    ceiling_microseconds = ceiling * 1_000_000
    try:
        for artifact in value.observed_source_artifacts:
            observed_at = kernel_artifact_to_plain_dict_v01(artifact)[
                "time_envelope"
            ]["et_observed_at"]
            if _timestamp_epoch_microseconds_v01(observed_at) > ceiling_microseconds:
                return "g2e_delta_future_observation"
    except Exception:
        return "g2e_delta_source_unvalidated"

    if (
        value.g2c_source_context
        != bundle.source_context.g2c_source_context
        or canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(
                value.baseline_g2c_route_eligibility_artifact
            )
        )
        != canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(
                bundle.source_context.route_eligibility_artifact
            )
        )
    ):
        return "g2e_route_revalidation_required"
    if (
        validate_runtime_topology_source_binding_against_g2c_v02(
            bundle.source_binding,
            source_context=bundle.source_context,
        ).status
        != "PASS"
        or bundle.source_binding.route_eligibility_artifact_id
        != value.baseline_g2c_route_eligibility_artifact.artifact_id
    ):
        return "g2e_topology_binding_mismatch"
    if value.root_kernel != bundle.source_context.root_kernel:
        return "g2e_topology_binding_mismatch"
    return None


def _source_context_validated_id_v01(
    value: ContinuousDeltaSourceContextV01,
) -> str:
    return value.baseline_g2d_execution_bundle.runtime_report.report_id


def _ordered_unique_v01(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    output: list[str] = []
    present: set[str] = set()
    for value in values:
        if value not in present:
            output.append(value)
            present.add(value)
    return tuple(output)


def _g2d_kernel_artifacts_v01(
    bundle: FractalRuntimeExecutionBundleV02,
) -> tuple[KernelArtifactV01, ...]:
    candidates = (
        bundle.source_context.proposal_artifact,
        bundle.source_context.decision_artifact,
        bundle.source_context.route_eligibility_artifact,
        bundle.topology_artifact,
        *bundle.queue_artifacts,
        *bundle.result_artifacts,
        bundle.report_artifact,
    )
    output: list[KernelArtifactV01] = []
    seen: set[str] = set()
    for artifact in candidates:
        _artifact_plain_v01(artifact)
        if artifact.artifact_id not in seen:
            output.append(artifact)
            seen.add(artifact.artifact_id)
    return tuple(output)


def _binding_reaches_artifact_v01(
    *,
    source_artifact_id: str,
    target_artifact_id: str,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
) -> bool:
    if source_artifact_id == target_artifact_id:
        return True
    reverse: dict[str, list[str]] = {}
    for edge in dependency_edges:
        reverse.setdefault(edge.dependency_artifact_id, []).append(
            edge.dependent_artifact_id
        )
    frontier = deque((source_artifact_id,))
    seen = {source_artifact_id}
    while frontier:
        current = frontier.popleft()
        for dependent in reverse.get(current, ()):
            if dependent == target_artifact_id:
                return True
            if dependent not in seen:
                seen.add(dependent)
                frontier.append(dependent)
    return False


def _e3_contextual_carriers_v01(
    *,
    affected_set: AffectedSetResultV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> AffectedSetRequestV01:
    context_report = validate_continuous_delta_source_context_v01(source_context)
    if context_report.status != "PASS":
        raise ValueError(context_report.reason_codes[0])
    request = build_affected_set_request_v01(
        delta=delta,
        graph=dependency_graph,
        trace_refs=affected_set.trace_refs,
    )
    if request.affected_request_id != affected_set.affected_request_id:
        raise ValueError("g2e_affected_request_invalid")
    report = validate_affected_set_against_graph_v01(
        affected_set,
        request=request,
        delta=delta,
        graph=dependency_graph,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        baseline_source_artifacts=source_context.baseline_source_artifacts,
        observed_source_artifacts=source_context.observed_source_artifacts,
    )
    if report.status != "PASS":
        raise ValueError(report.reason_codes[0])
    if (
        delta.baseline_report_id
        != source_context.baseline_g2d_execution_bundle.runtime_report.report_id
    ):
        raise ValueError("g2e_delta_baseline_stale")
    return request


def _source_pair_payloads_v01(
    binding: DeltaSourceBindingV01,
    *,
    baseline_by_id: dict[str, KernelArtifactV01],
    observed_by_id: dict[str, KernelArtifactV01],
) -> tuple[dict[str, object], dict[str, object]]:
    baseline = baseline_by_id.get(binding.baseline_source_artifact_id)
    observed = observed_by_id.get(binding.observed_source_artifact_id)
    if baseline is None or observed is None:
        raise ValueError("g2e_delta_binding_set_mismatch")
    baseline_payload = _artifact_plain_v01(baseline)["payload"]
    observed_payload = _artifact_plain_v01(observed)["payload"]
    if type(baseline_payload) is not dict or type(observed_payload) is not dict:
        raise ValueError("g2e_delta_source_unvalidated")
    return baseline_payload, observed_payload


def _g2a_packet_binding_changed_v01(
    *,
    baseline_payload: dict[str, object],
    observed_payload: dict[str, object],
    source_context: ContinuousDeltaSourceContextV01,
) -> bool:
    invalidation = source_context.g2a_root_invalidation_material
    observation_by_dependency = {
        item.dependency_id: item for item in source_context.g2a_current_observations
    }
    for record in source_context.g2a_dependency_candidate.dependency_records:
        observation = observation_by_dependency.get(record.dependency_id)
        if observation is None:
            continue
        baseline_material = {
            "dependency_id": record.dependency_id,
            "dependency_class": record.dependency_class,
            "evidence_ref": record.evidence_ref,
            "content_sha256": record.content_sha256,
            "requirement_class": record.requirement_class,
            "time_envelope_id": record.time_envelope_id,
            "freshness_policy_id": record.freshness_policy_id,
            "source_provenance_refs": list(record.source_provenance_refs),
            "expected_accepting_local_root_id": (
                record.expected_accepting_local_root_id
            ),
        }
        if any(
            baseline_payload.get(name) != expected
            for name, expected in baseline_material.items()
        ):
            continue
        if (
            observation.evidence_ref != record.evidence_ref
            or observation.observed_content_sha256 != record.content_sha256
            or observation.time_envelope_id != record.time_envelope_id
            or observation.freshness_policy_id != record.freshness_policy_id
            or observation.source_provenance_refs != record.source_provenance_refs
            or invalidation.dependency_id != record.dependency_id
            or invalidation.evidence_ref != record.evidence_ref
            or invalidation.time_envelope_id != record.time_envelope_id
            or invalidation.freshness_policy_id != record.freshness_policy_id
            or observed_payload.get("dependency_id") != record.dependency_id
            or observed_payload.get("evidence_ref") != record.evidence_ref
            or observed_payload.get("content_sha256")
            != invalidation.evidence_sha256
            or observed_payload.get("observed_status")
            != invalidation.observed_status
            or observed_payload.get("invalidation_evidence_id")
            != invalidation.invalidation_evidence_id
            or observed_payload.get("packet_id") != invalidation.packet_id
            or observed_payload.get("content_sha256")
            == baseline_payload.get("content_sha256")
        ):
            continue
        return True
    return False


def _g2b_reuse_binding_changed_v01(
    *,
    baseline_payload: dict[str, object],
    observed_payload: dict[str, object],
    source_context: ContinuousDeltaSourceContextV01,
) -> bool:
    certificate = source_context.g2b_reuse_certificate
    report = source_context.g2b_resolution_report
    source_refs = {
        source_ref
        for record in report.source_records
        if record.meaning_record_id == certificate.meaning_record_id
        for source_ref in record.source_reference_ids
    }
    baseline_material = {
        "semantic_address_id": certificate.semantic_address_id,
        "meaning_record_id": certificate.meaning_record_id,
        "query_id": certificate.query_id,
        "query_evaluation_id": certificate.query_evaluation_id,
        "required_evidence_classes": list(certificate.required_evidence_classes),
        "observed_evidence_fingerprint": (
            certificate.observed_evidence_fingerprint
        ),
        "forbidden_changes": list(certificate.forbidden_changes),
        "checked_dependency_fingerprint": (
            certificate.checked_dependency_fingerprint
        ),
        "source_history_hash": certificate.source_history_hash,
        "policy_version": certificate.policy_version,
        "schema_versions": list(certificate.schema_versions),
    }
    if (
        baseline_payload.get("source_reference_id") not in source_refs
        or any(
            baseline_payload.get(name) != expected
            for name, expected in baseline_material.items()
        )
    ):
        return False
    stable_fields = tuple(
        name for name in baseline_material if name != "observed_evidence_fingerprint"
    ) + ("source_reference_id",)
    return bool(
        all(
            observed_payload.get(name) == baseline_payload.get(name)
            for name in stable_fields
        )
        and observed_payload.get("observed_evidence_fingerprint")
        != certificate.observed_evidence_fingerprint
    )


def _g2c_route_binding_changed_v01(
    *,
    baseline_payload: dict[str, object],
    observed_payload: dict[str, object],
    source_context: ContinuousDeltaSourceContextV01,
) -> bool:
    binding = source_context.baseline_g2d_execution_bundle.source_binding
    baseline_material = {
        "route_eligibility_artifact_id": binding.route_eligibility_artifact_id,
        "route_eligibility_artifact_sha256": (
            binding.route_eligibility_artifact_sha256
        ),
        "source_decision_artifact_id": binding.source_decision_artifact_id,
        "source_proposal_artifact_id": binding.source_proposal_artifact_id,
        "source_policy_snapshot_id": binding.source_policy_snapshot_id,
        "source_capability_snapshot_id": binding.source_capability_snapshot_id,
        "source_parent_refs": list(binding.source_parent_refs),
        "source_trace_refs": list(binding.source_trace_refs),
    }
    if any(
        baseline_payload.get(name) != expected
        for name, expected in baseline_material.items()
    ):
        return False
    stable_fields = tuple(
        name
        for name in baseline_material
        if name != "route_eligibility_artifact_sha256"
    )
    return bool(
        all(
            observed_payload.get(name) == baseline_payload.get(name)
            for name in stable_fields
        )
        and observed_payload.get("route_eligibility_artifact_sha256")
        != binding.route_eligibility_artifact_sha256
    )


def _record_relation_candidate_ids_v01(
    record: ArtifactInvalidationRecordV01,
) -> tuple[str | None, str | None, str | None]:
    active = (
        record.g2a_packet_relation == "PACKET_ROOT_REVIEW_REQUIRED",
        record.g2b_reuse_relation == "REUSE_CERTIFICATE_STALE",
        record.g2c_route_relation == "ROUTE_REVALIDATION_REQUIRED",
    )
    count = sum(active)
    if count == 0:
        return None, None, None
    if len(record.trace_refs) < count:
        raise ValueError("g2e_invalidation_record_invalid")
    candidates = iter(record.trace_refs[-count:])
    return tuple(  # type: ignore[return-value]
        next(candidates) if present else None for present in active
    )


def _derive_invalidation_rows_v01(
    *,
    affected_set: AffectedSetResultV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
) -> tuple[tuple[ArtifactInvalidationRecordV01, ...], tuple[str, ...]]:
    baseline_by_id = {
        artifact.artifact_id: artifact
        for artifact in source_context.baseline_source_artifacts
    }
    observed_by_id = {
        artifact.artifact_id: artifact
        for artifact in source_context.observed_source_artifacts
    }
    binding_by_id = {
        binding.source_binding_id: binding for binding in source_bindings
    }
    packet_id = source_context.g2a_packet.packet_identity.packet_id
    certificate_id = source_context.g2b_reuse_certificate.certificate_id
    route_id = source_context.baseline_g2c_route_eligibility_artifact.artifact_id
    records: list[ArtifactInvalidationRecordV01] = []
    unresolved: list[str] = []
    ordered_changed = tuple(changed_field_bindings) + tuple(
        changed_artifact_bindings
    )
    for artifact_id in affected_set.ordered_affected_ids:
        artifact = baseline_by_id.get(artifact_id)
        if artifact is None:
            unresolved.append(artifact_id)
            continue
        triggering: list[object] = []
        for changed in ordered_changed:
            binding = binding_by_id.get(changed.source_binding_id)
            if binding is not None and _binding_reaches_artifact_v01(
                source_artifact_id=binding.baseline_source_artifact_id,
                target_artifact_id=artifact_id,
                dependency_edges=dependency_edges,
            ):
                triggering.append(changed)
        if not triggering:
            unresolved.append(artifact_id)
            continue
        reason_candidates: list[str] = []
        g2a_relation = "NOT_APPLICABLE"
        g2b_relation = "NOT_APPLICABLE"
        g2c_relation = "ROUTE_CURRENT"
        source_rows = tuple(
            binding
            for binding in source_bindings
            if any(
                changed.source_binding_id == binding.source_binding_id
                for changed in triggering
            )
        )
        source_pairs = tuple(
            _source_pair_payloads_v01(
                binding,
                baseline_by_id=baseline_by_id,
                observed_by_id=observed_by_id,
            )
            for binding in source_rows
        )
        route_changed = any(
            _g2c_route_binding_changed_v01(
                baseline_payload=baseline_payload,
                observed_payload=observed_payload,
                source_context=source_context,
            )
            for baseline_payload, observed_payload in source_pairs
        )
        packet_changed = any(
            _g2a_packet_binding_changed_v01(
                baseline_payload=baseline_payload,
                observed_payload=observed_payload,
                source_context=source_context,
            )
            for baseline_payload, observed_payload in source_pairs
        )
        certificate_changed = any(
            _g2b_reuse_binding_changed_v01(
                baseline_payload=baseline_payload,
                observed_payload=observed_payload,
                source_context=source_context,
            )
            for baseline_payload, observed_payload in source_pairs
        )
        if route_changed:
            g2c_relation = "ROUTE_REVALIDATION_REQUIRED"
            reason_candidates.append("ROUTE_REVALIDATION_REQUIRED")
        if packet_changed:
            g2a_relation = "PACKET_ROOT_REVIEW_REQUIRED"
            reason_candidates.append("PACKET_ROOT_REVIEW_REQUIRED")
        if certificate_changed:
            g2b_relation = "REUSE_CERTIFICATE_STALE"
            reason_candidates.append("REUSE_CERTIFICATE_STALE")
        if any(
            item.baseline_policy_version != item.observed_policy_version
            for item in source_rows
        ):
            reason_candidates.append("POLICY_VERSION_CHANGED")
        if any(
            item.baseline_schema_versions != item.observed_schema_versions
            for item in source_rows
        ):
            reason_candidates.append("SCHEMA_VERSION_CHANGED")
        if any(
            item.baseline_source_history_hash
            != item.observed_source_history_hash
            for item in source_rows
        ):
            reason_candidates.append("DEPENDENCY_FINGERPRINT_CHANGED")
        if any(
            type(item) is ChangedArtifactBindingV01 for item in triggering
        ):
            reason_candidates.append("SOURCE_ARTIFACT_CHANGED")
        if any(type(item) is ChangedFieldBindingV01 for item in triggering):
            reason_candidates.append("SOURCE_FIELD_CHANGED")
        reason_candidates.append("UPSTREAM_ARTIFACT_INVALIDATED")
        primary_reason = next(
            reason
            for reason in _INVALIDATION_REASON_PRIORITY_V01
            if reason in reason_candidates
        )
        triggering_ids = tuple(
            item.changed_field_binding_id
            if type(item) is ChangedFieldBindingV01
            else item.changed_artifact_binding_id
            for item in triggering
        )
        record = build_artifact_invalidation_record_v01(
            affected_set_id=affected_set.affected_set_id,
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            invalidation_reason_class=primary_reason,
            triggering_delta_id=delta.delta_id,
            triggering_binding_ids=triggering_ids,
            predecessor_artifact_id=artifact.artifact_id,
            g2a_packet_relation=g2a_relation,
            g2b_reuse_relation=g2b_relation,
            g2c_route_relation=g2c_relation,
            root_review_required=bool(
                g2a_relation == "PACKET_ROOT_REVIEW_REQUIRED"
                or g2b_relation == "REUSE_CERTIFICATE_STALE"
                or g2c_relation == "ROUTE_REVALIDATION_REQUIRED"
            ),
            trace_refs=_ordered_unique_v01(
                (
                    delta.delta_id,
                    affected_set.affected_set_id,
                    *triggering_ids,
                    artifact.artifact_id,
                    *((packet_id,) if packet_changed else ()),
                    *((certificate_id,) if certificate_changed else ()),
                    *((route_id,) if route_changed else ()),
                )
            ),
        )
        records.append(record)
    return tuple(records), tuple(unresolved)


def _project_invalidation_report_artifact_v01(
    *,
    report: InvalidationReportV01,
    affected_set_artifact: KernelArtifactV01,
    validated_delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    baseline_route_artifact: KernelArtifactV01,
    delta: WorldStateDeltaV01,
    t03_decision_id: str,
) -> KernelArtifactV01:
    if _invalidation_report_errors_v01(report):
        raise ValueError("g2e_invalidation_record_invalid")
    for artifact in (
        affected_set_artifact,
        validated_delta_source_artifact,
        dependency_graph_artifact,
        baseline_route_artifact,
    ):
        _artifact_plain_v01(artifact)
    if (
        affected_set_artifact.artifact_type != "AffectedSetResult"
        or affected_set_artifact.lifecycle_state != "VALIDATED"
        or validated_delta_source_artifact.artifact_type
        != "ContinuousDeltaSource"
        or dependency_graph_artifact.artifact_type != "DependencyGraphIndex"
        or not _text_valid(t03_decision_id)
    ):
        raise ValueError("g2e_object_invalid")
    return _project_g2e_kernel_artifact_v01(
        profile_name="invalidation_report_validated",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="invalidation_report_validated",
            complete_payload=invalidation_report_to_plain_data_v01(report),
        ),
        trace_refs=(
            report.affected_set_id,
            t03_decision_id,
            *report.ordered_invalidation_record_ids,
            *report.reason_codes,
        ),
        parent_refs=(
            affected_set_artifact.artifact_id,
            validated_delta_source_artifact.artifact_id,
            dependency_graph_artifact.artifact_id,
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
        ),
    )


def _validate_invalidation_report_artifact_against_source_v01(
    artifact: object,
    *,
    report: InvalidationReportV01,
    affected_set_artifact: KernelArtifactV01,
    validated_delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    baseline_route_artifact: KernelArtifactV01,
    delta: WorldStateDeltaV01,
    t03_decision: TransitionDecisionV01,
) -> tuple[str, ...]:
    try:
        if type(artifact) is not KernelArtifactV01:
            raise ValueError("g2e_object_invalid")
        expected = _project_invalidation_report_artifact_v01(
            report=report,
            affected_set_artifact=affected_set_artifact,
            validated_delta_source_artifact=validated_delta_source_artifact,
            dependency_graph_artifact=dependency_graph_artifact,
            baseline_route_artifact=baseline_route_artifact,
            delta=delta,
            t03_decision_id=t03_decision.decision_id,
        )
        registry = _build_continuous_delta_transition_registry_profile_v01()
        if (
            artifact != expected
            or canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(artifact))
            != canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(expected))
            or validate_kernel_artifact_v01(artifact)
            or _validate_continuous_delta_transition_decision_v01(
                t03_decision,
                registry=registry,
                source_artifact=affected_set_artifact,
                target_artifact=artifact,
            )
        ):
            raise ValueError("g2e_object_invalid")
        return ()
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        return (
            reason
            if reason in PUBLIC_G2E_REASON_CODES_V01
            else "g2e_object_invalid",
        )
    except Exception:
        return ("g2e_object_invalid",)


def _project_preservation_proof_artifact_v01(
    *,
    proof: PreservationProofV01,
    root_accepted_plan_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
    recomputed_g2d_report_artifact: KernelArtifactV01,
    delta: WorldStateDeltaV01,
    recomputed_g2d_runtime_trace_id: str,
) -> KernelArtifactV01:
    if _preservation_proof_errors_v01(proof):
        raise ValueError("g2e_preservation_proof_invalid")
    for artifact in (
        root_accepted_plan_artifact,
        invalidation_report_artifact,
        recomputed_g2d_report_artifact,
    ):
        _artifact_plain_v01(artifact)
    if (
        root_accepted_plan_artifact.artifact_type
        != "SelectiveRecomputationPlan"
        or root_accepted_plan_artifact.lifecycle_state != "ROOT_ACCEPTED"
        or invalidation_report_artifact.artifact_type
        != "ArtifactInvalidationReport"
        or invalidation_report_artifact.lifecycle_state != "VALIDATED"
        or recomputed_g2d_report_artifact.artifact_type
        != "FractalRuntimeReport"
        or recomputed_g2d_report_artifact.lifecycle_state != "VALIDATED"
        or not _text_valid(recomputed_g2d_runtime_trace_id)
    ):
        raise ValueError("g2e_preservation_proof_invalid")
    return _project_g2e_kernel_artifact_v01(
        profile_name="preservation_proof_validated",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="preservation_proof_validated",
            complete_payload=preservation_proof_to_plain_data_v01(proof),
        ),
        trace_refs=(
            proof.affected_set_id,
            *proof.ordered_preserved_artifact_ids,
            recomputed_g2d_runtime_trace_id,
        ),
        parent_refs=(
            root_accepted_plan_artifact.artifact_id,
            invalidation_report_artifact.artifact_id,
            recomputed_g2d_report_artifact.artifact_id,
        ),
        time_envelope=kernel_artifact_to_plain_dict_v01(
            recomputed_g2d_report_artifact
        )["time_envelope"],
    )


def build_artifact_invalidation_record_v01(
    *,
    affected_set_id: str,
    artifact_id: str,
    artifact_type: str,
    invalidation_reason_class: str,
    triggering_delta_id: str,
    triggering_binding_ids: tuple[str, ...],
    predecessor_artifact_id: str,
    g2a_packet_relation: str,
    g2b_reuse_relation: str,
    g2c_route_relation: str,
    root_review_required: bool,
    trace_refs: tuple[str, ...],
) -> ArtifactInvalidationRecordV01:
    provisional = ArtifactInvalidationRecordV01(
        invalidation_record_id=(
            "g2e_artifact_invalidation_record_v01:" + _ZERO_SHA256
        ),
        affected_set_id=affected_set_id,
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        current_eligible_before=True,
        current_eligible_after=False,
        invalidation_reason_class=invalidation_reason_class,
        triggering_delta_id=triggering_delta_id,
        triggering_binding_ids=triggering_binding_ids,
        predecessor_artifact_id=predecessor_artifact_id,
        superseded_by_artifact_id=None,
        g2a_packet_relation=g2a_packet_relation,
        g2b_reuse_relation=g2b_reuse_relation,
        g2c_route_relation=g2c_route_relation,
        root_review_required=root_review_required,
        historical_artifact_preserved=True,
        deleted=False,
        trace_refs=trace_refs,
    )
    value = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        value, _invalidation_record_errors_v01
    )


def validate_artifact_invalidation_record_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        ArtifactInvalidationRecordV01,
        "invalidation_record",
        _invalidation_record_errors_v01,
    )


def artifact_invalidation_record_to_plain_data_v01(
    value: ArtifactInvalidationRecordV01,
) -> dict[str, object]:
    return _serialize(
        value,
        ArtifactInvalidationRecordV01,
        _invalidation_record_errors_v01,
    )


def rebuild_artifact_invalidation_record_identity_v01(
    value: ArtifactInvalidationRecordV01,
) -> str:
    return _rebuild(value, ArtifactInvalidationRecordV01)


def build_invalidation_report_v01(
    *,
    affected_set_id: str,
    records: tuple[ArtifactInvalidationRecordV01, ...],
    ordered_unresolved_artifact_ids: tuple[str, ...],
) -> InvalidationReportV01:
    if (
        type(records) is not tuple
        or not records
        or any(_invalidation_record_errors_v01(record) for record in records)
        or any(record.affected_set_id != affected_set_id for record in records)
    ):
        raise ValueError("g2e_invalidation_record_invalid")
    invalidated = tuple(record.artifact_id for record in records)
    relation_candidates = tuple(
        _record_relation_candidate_ids_v01(record) for record in records
    )
    packet_ids = _ordered_unique_v01(
        [
            packet_id
            for packet_id, _certificate_id, _route_id in relation_candidates
            if packet_id is not None
        ]
    )
    certificate_ids = _ordered_unique_v01(
        [
            certificate_id
            for _packet_id, certificate_id, _route_id in relation_candidates
            if certificate_id is not None
        ]
    )
    route_ids = _ordered_unique_v01(
        [
            route_id
            for _packet_id, _certificate_id, route_id in relation_candidates
            if route_id is not None
        ]
    )
    reasons = _report_reason_codes_v01(
        unresolved=ordered_unresolved_artifact_ids,
        packet_ids=packet_ids,
        certificate_ids=certificate_ids,
        route_ids=route_ids,
    )
    provisional = InvalidationReportV01(
        invalidation_report_id="g2e_invalidation_report_v01:" + _ZERO_SHA256,
        affected_set_id=affected_set_id,
        ordered_invalidation_record_ids=tuple(
            record.invalidation_record_id for record in records
        ),
        ordered_invalidated_artifact_ids=invalidated,
        ordered_historical_artifact_ids=invalidated,
        ordered_unresolved_artifact_ids=ordered_unresolved_artifact_ids,
        ordered_packet_invalidation_candidate_ids=packet_ids,
        ordered_stale_reuse_certificate_ids=certificate_ids,
        ordered_route_revalidation_ids=route_ids,
        report_status="PASS" if not reasons else "FAIL_CLOSED",
        reason_codes=reasons,
        root_review_required=bool(packet_ids or certificate_ids or route_ids),
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    value = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        value, _invalidation_report_errors_v01
    )


def validate_invalidation_report_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        InvalidationReportV01,
        "invalidation_record",
        _invalidation_report_errors_v01,
    )


def invalidation_report_to_plain_data_v01(
    value: InvalidationReportV01,
) -> dict[str, object]:
    return _serialize(
        value,
        InvalidationReportV01,
        _invalidation_report_errors_v01,
    )


def rebuild_invalidation_report_identity_v01(
    value: InvalidationReportV01,
) -> str:
    return _rebuild(value, InvalidationReportV01)


def build_preservation_proof_v01(
    *,
    baseline_graph_id: str,
    affected_set_id: str,
    ordered_preserved_artifact_ids: tuple[str, ...],
    ordered_before_artifact_sha256: tuple[str, ...],
    ordered_after_artifact_sha256: tuple[str, ...],
    ordered_before_payload_sha256: tuple[str, ...],
    ordered_after_payload_sha256: tuple[str, ...],
    ordered_before_identity_ids: tuple[str, ...],
    ordered_after_identity_ids: tuple[str, ...],
) -> PreservationProofV01:
    reasons = _preservation_reason_codes_v01(
        before_artifact=ordered_before_artifact_sha256,
        after_artifact=ordered_after_artifact_sha256,
        before_payload=ordered_before_payload_sha256,
        after_payload=ordered_after_payload_sha256,
        before_identity=ordered_before_identity_ids,
        after_identity=ordered_after_identity_ids,
    )
    no_cache = _no_cache_state_sha256_v01()
    provisional = PreservationProofV01(
        preservation_proof_id="g2e_preservation_proof_v01:" + _ZERO_SHA256,
        baseline_graph_id=baseline_graph_id,
        affected_set_id=affected_set_id,
        ordered_preserved_artifact_ids=ordered_preserved_artifact_ids,
        ordered_before_artifact_sha256=ordered_before_artifact_sha256,
        ordered_after_artifact_sha256=ordered_after_artifact_sha256,
        ordered_before_payload_sha256=ordered_before_payload_sha256,
        ordered_after_payload_sha256=ordered_after_payload_sha256,
        ordered_before_identity_ids=ordered_before_identity_ids,
        ordered_after_identity_ids=ordered_after_identity_ids,
        before_cache_state_sha256=no_cache,
        after_cache_state_sha256=no_cache,
        mutable_global_write_count=0,
        byte_identity_preserved=not reasons,
        object_identity_used_as_proof=False,
        proof_sha256=_ZERO_SHA256,
        status="PASS" if not reasons else "FAIL_CLOSED",
        reason_codes=reasons,
    )
    with_proof = replace(
        provisional,
        proof_sha256=_preservation_proof_sha256_v01(provisional),
    )
    value = _finish_identity(with_proof)
    return _require_built_valid(  # type: ignore[return-value]
        value, _preservation_proof_errors_v01
    )


def validate_preservation_proof_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        PreservationProofV01,
        "preservation",
        _preservation_proof_errors_v01,
    )


def preservation_proof_to_plain_data_v01(
    value: PreservationProofV01,
) -> dict[str, object]:
    return _serialize(
        value,
        PreservationProofV01,
        _preservation_proof_errors_v01,
    )


def rebuild_preservation_proof_identity_v01(
    value: PreservationProofV01,
) -> str:
    return _rebuild(value, PreservationProofV01)


def build_continuous_delta_source_context_v01(
    *,
    integrity_manifest,
    integrity_replay,
    baseline_source_artifacts: tuple[KernelArtifactV01, ...],
    observed_source_artifacts: tuple[KernelArtifactV01, ...],
    g2a_registry,
    g2a_packet,
    g2a_dependency_candidate,
    g2a_current_observations,
    g2a_root_invalidation_material,
    g2b_resolution_report,
    g2b_reuse_certificate,
    g2b_writeback_evidence,
    g2c_source_context,
    baseline_g2c_route_eligibility_artifact,
    baseline_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    root_kernel,
    post_vv_profile,
    gt_profile,
) -> ContinuousDeltaSourceContextV01:
    value = ContinuousDeltaSourceContextV01(
        integrity_manifest=integrity_manifest,
        integrity_replay=integrity_replay,
        baseline_source_artifacts=baseline_source_artifacts,
        observed_source_artifacts=observed_source_artifacts,
        g2a_registry=g2a_registry,
        g2a_packet=g2a_packet,
        g2a_dependency_candidate=g2a_dependency_candidate,
        g2a_current_observations=g2a_current_observations,
        g2a_root_invalidation_material=g2a_root_invalidation_material,
        g2b_resolution_report=g2b_resolution_report,
        g2b_reuse_certificate=g2b_reuse_certificate,
        g2b_writeback_evidence=g2b_writeback_evidence,
        g2c_source_context=g2c_source_context,
        baseline_g2c_route_eligibility_artifact=(
            baseline_g2c_route_eligibility_artifact
        ),
        baseline_g2d_execution_bundle=baseline_g2d_execution_bundle,
        root_kernel=root_kernel,
        post_vv_profile=post_vv_profile,
        gt_profile=gt_profile,
    )
    report = validate_continuous_delta_source_context_v01(value)
    if report.status != "PASS":
        raise ValueError(report.reason_codes[0])
    return value


def validate_continuous_delta_source_context_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    reason = _source_context_reason_v01(value)
    return _contextual_report_v01(
        validation_target="ContinuousDeltaSourceContextV01",
        validated_object_id=(
            _source_context_validated_id_v01(value)
            if reason is None and type(value) is ContinuousDeltaSourceContextV01
            else None
        ),
        failure_stage="delta_source_context",
        reason_codes=() if reason is None else (reason,),
    )


def derive_invalidation_report_v01(
    *,
    affected_set: AffectedSetResultV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> tuple[
    tuple[ArtifactInvalidationRecordV01, ...],
    InvalidationReportV01,
]:
    _e3_contextual_carriers_v01(
        affected_set=affected_set,
        delta=delta,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        dependency_graph=dependency_graph,
    )
    records, unresolved = _derive_invalidation_rows_v01(
        affected_set=affected_set,
        delta=delta,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
    )
    if not records:
        raise ValueError("g2e_invalidation_record_invalid")
    report = build_invalidation_report_v01(
        affected_set_id=affected_set.affected_set_id,
        records=records,
        ordered_unresolved_artifact_ids=unresolved,
    )
    return records, report


def validate_invalidation_report_against_sources_v01(
    value: InvalidationReportV01,
    *,
    records: tuple[ArtifactInvalidationRecordV01, ...],
    affected_set: AffectedSetResultV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> ContinuousDeltaValidationReportV01:
    reason: str | None = None
    try:
        expected_records, expected_report = derive_invalidation_report_v01(
            affected_set=affected_set,
            delta=delta,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        if (
            type(records) is not tuple
            or records != expected_records
            or value != expected_report
            or canonical_json_bytes_v01(
                invalidation_report_to_plain_data_v01(value)
            )
            != canonical_json_bytes_v01(
                invalidation_report_to_plain_data_v01(expected_report)
            )
        ):
            reason = "g2e_invalidation_record_invalid"
    except ValueError as exc:
        candidate = exc.args[0] if len(exc.args) == 1 else None
        reason = (
            candidate
            if candidate in PUBLIC_G2E_REASON_CODES_V01
            else "g2e_invalidation_record_invalid"
        )
    except Exception:
        reason = "g2e_invalidation_record_invalid"
    return _contextual_report_v01(
        validation_target="invalidation_against_prior_slices",
        validated_object_id=(
            value.invalidation_report_id
            if reason is None and type(value) is InvalidationReportV01
            else None
        ),
        failure_stage="invalidation_prior_slice",
        reason_codes=() if reason is None else (reason,),
    )


def prove_unaffected_artifact_preservation_v01(
    *,
    affected_set: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    source_context: ContinuousDeltaSourceContextV01,
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
) -> PreservationProofV01:
    context_report = validate_continuous_delta_source_context_v01(source_context)
    if context_report.status != "PASS":
        raise ValueError(context_report.reason_codes[0])
    if (
        _affected_set_result_errors(affected_set)
        or type(invalidation_records) is not tuple
        or any(_invalidation_record_errors_v01(row) for row in invalidation_records)
        or tuple(row.artifact_id for row in invalidation_records)
        != affected_set.ordered_affected_ids
        or type(recomputed_g2d_execution_bundle)
        is not FractalRuntimeExecutionBundleV02
        or validate_fractal_runtime_execution_bundle_v02(
            recomputed_g2d_execution_bundle
        ).status
        != "PASS"
        or type(recomputed_bindings) is not tuple
        or any(
            type(binding) is not RecomputedArtifactBindingV01
            for binding in recomputed_bindings
        )
    ):
        raise ValueError("g2e_preservation_proof_invalid")
    baseline_g2d = _g2d_kernel_artifacts_v01(
        source_context.baseline_g2d_execution_bundle
    )
    recomputed_g2d = _g2d_kernel_artifacts_v01(
        recomputed_g2d_execution_bundle
    )
    affected_ids = set(
        affected_set.ordered_changed_node_ids
        + affected_set.ordered_affected_ids
    )
    route_revalidation_required = any(
        record.g2c_route_relation == "ROUTE_REVALIDATION_REQUIRED"
        for record in invalidation_records
    )
    recomputed_prior_ids = {
        binding.prior_artifact_id for binding in recomputed_bindings
    }
    baseline_g2d_ids = {artifact.artifact_id for artifact in baseline_g2d}
    if (
        affected_ids & baseline_g2d_ids
        or recomputed_bindings
        or route_revalidation_required
    ) and (
        not recomputed_bindings
        or tuple(
            canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
            for item in baseline_g2d
        )
        == tuple(
            canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
            for item in recomputed_g2d
        )
    ):
        raise ValueError("g2e_recomputation_in_place_forbidden")

    before_rows: list[KernelArtifactV01] = []
    after_rows: list[KernelArtifactV01] = []
    observed_by_baseline_position = dict(
        zip(
            (
                artifact.artifact_id
                for artifact in source_context.baseline_source_artifacts
            ),
            source_context.observed_source_artifacts,
        )
    )
    for baseline in source_context.baseline_source_artifacts:
        if (
            baseline.artifact_id not in affected_ids
            and baseline.artifact_id not in recomputed_prior_ids
        ):
            before_rows.append(baseline)
            after_rows.append(observed_by_baseline_position[baseline.artifact_id])
    recomputed_by_id = {
        artifact.artifact_id: artifact for artifact in recomputed_g2d
    }
    already_preserved_ids = {
        artifact.artifact_id for artifact in before_rows
    }
    for baseline in baseline_g2d:
        if (
            baseline.artifact_id not in affected_ids
            and baseline.artifact_id not in recomputed_prior_ids
            and baseline.artifact_id not in already_preserved_ids
        ):
            before_rows.append(baseline)
            after_rows.append(recomputed_by_id.get(baseline.artifact_id, baseline))
            already_preserved_ids.add(baseline.artifact_id)
    before = tuple(before_rows)
    after = tuple(after_rows)
    return build_preservation_proof_v01(
        baseline_graph_id=affected_set.graph_id,
        affected_set_id=affected_set.affected_set_id,
        ordered_preserved_artifact_ids=tuple(
            artifact.artifact_id for artifact in before
        ),
        ordered_before_artifact_sha256=tuple(
            _artifact_sha256_v01(artifact) for artifact in before
        ),
        ordered_after_artifact_sha256=tuple(
            _artifact_sha256_v01(artifact) for artifact in after
        ),
        ordered_before_payload_sha256=tuple(
            _artifact_payload_sha256_v01(artifact) for artifact in before
        ),
        ordered_after_payload_sha256=tuple(
            _artifact_payload_sha256_v01(artifact) for artifact in after
        ),
        ordered_before_identity_ids=tuple(
            artifact.artifact_id for artifact in before
        ),
        ordered_after_identity_ids=tuple(
            artifact.artifact_id for artifact in after
        ),
    )


def build_selective_recomputation_plan_v01(
    *,
    delta_id: str,
    affected_set_id: str,
    invalidation_report_id: str,
    source_route_eligibility_artifact_id: str,
    source_topology_id: str,
    accepted_mode: str,
    accepted_scope_ref: str,
    ordered_affected_cell_ids: tuple[str, ...],
    ordered_affected_artifact_ids: tuple[str, ...],
    ordered_work_node_ids: tuple[str, ...],
    ordered_preserved_artifact_ids: tuple[str, ...],
    max_work_items: int,
    max_queue_entries: int,
    max_wall_time_units: int,
    max_token_budget: int,
    max_provider_calls: int,
    transition_profile_id: str,
    root_review_required: bool,
    plan_status: str,
    reason_codes: tuple[str, ...],
    trace_refs: tuple[str, ...],
) -> SelectiveRecomputationPlanV01:
    provisional = SelectiveRecomputationPlanV01(
        recomputation_plan_id="g2e_selective_recomputation_plan_v01:" + _ZERO_SHA256,
        delta_id=delta_id,
        affected_set_id=affected_set_id,
        invalidation_report_id=invalidation_report_id,
        source_route_eligibility_artifact_id=source_route_eligibility_artifact_id,
        source_topology_id=source_topology_id,
        accepted_mode=accepted_mode,
        accepted_scope_ref=accepted_scope_ref,
        ordered_affected_cell_ids=ordered_affected_cell_ids,
        ordered_affected_artifact_ids=ordered_affected_artifact_ids,
        ordered_work_node_ids=ordered_work_node_ids,
        ordered_preserved_artifact_ids=ordered_preserved_artifact_ids,
        max_work_items=max_work_items,
        max_queue_entries=max_queue_entries,
        max_wall_time_units=max_wall_time_units,
        max_token_budget=max_token_budget,
        max_provider_calls=max_provider_calls,
        transition_profile_id=transition_profile_id,
        root_review_required=root_review_required,
        plan_status=plan_status,
        reason_codes=reason_codes,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _selective_recomputation_plan_errors_v01
    )


def validate_selective_recomputation_plan_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        SelectiveRecomputationPlanV01,
        "recomputation_plan",
        _selective_recomputation_plan_errors_v01,
    )


def selective_recomputation_plan_to_plain_data_v01(
    value: SelectiveRecomputationPlanV01,
) -> dict[str, object]:
    return _serialize(
        value,
        SelectiveRecomputationPlanV01,
        _selective_recomputation_plan_errors_v01,
    )


def rebuild_selective_recomputation_plan_identity_v01(
    value: SelectiveRecomputationPlanV01,
) -> str:
    return _rebuild(value, SelectiveRecomputationPlanV01)


def build_recomputed_artifact_binding_v01(
    *,
    recomputation_plan_id: str,
    prior_artifact_id: str,
    prior_payload_sha256: str,
    new_artifact_id: str,
    new_payload_sha256: str,
    predecessor_relation: str,
    supersession_relation: str,
    derivation_refs: tuple[str, ...],
    source_cell_id: str,
    source_queue_entry_id: str,
    g2d_cell_result_ref: str,
    g2d_runtime_report_ref: str,
    trace_refs: tuple[str, ...],
) -> RecomputedArtifactBindingV01:
    provisional = RecomputedArtifactBindingV01(
        recomputed_binding_id="g2e_recomputed_artifact_binding_v01:" + _ZERO_SHA256,
        recomputation_plan_id=recomputation_plan_id,
        prior_artifact_id=prior_artifact_id,
        prior_payload_sha256=prior_payload_sha256,
        new_artifact_id=new_artifact_id,
        new_payload_sha256=new_payload_sha256,
        predecessor_relation=predecessor_relation,
        supersession_relation=supersession_relation,
        derivation_refs=derivation_refs,
        source_cell_id=source_cell_id,
        source_queue_entry_id=source_queue_entry_id,
        g2d_cell_result_ref=g2d_cell_result_ref,
        g2d_runtime_report_ref=g2d_runtime_report_ref,
        trace_refs=trace_refs,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _recomputed_artifact_binding_errors_v01
    )


def validate_recomputed_artifact_binding_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        RecomputedArtifactBindingV01,
        "recomputation_execution",
        _recomputed_artifact_binding_errors_v01,
    )


def recomputed_artifact_binding_to_plain_data_v01(
    value: RecomputedArtifactBindingV01,
) -> dict[str, object]:
    return _serialize(
        value,
        RecomputedArtifactBindingV01,
        _recomputed_artifact_binding_errors_v01,
    )


def rebuild_recomputed_artifact_binding_identity_v01(
    value: RecomputedArtifactBindingV01,
) -> str:
    return _rebuild(value, RecomputedArtifactBindingV01)


def build_selective_recomputation_result_v01(
    *,
    recomputation_plan_id: str,
    baseline_runtime_report_id: str,
    recomputed_runtime_report_id: str,
    preservation_proof_id: str,
    ordered_recomputed_binding_ids: tuple[str, ...],
    ordered_invalidated_downstream_ids: tuple[str, ...],
    ordered_recomputed_artifact_ids: tuple[str, ...],
    ordered_preserved_artifact_ids: tuple[str, ...],
    ordered_unresolved_artifact_ids: tuple[str, ...],
    ordered_partial_failure_ids: tuple[str, ...],
    parent_return_transition_decision_id: str,
    result_status: str,
    reason_codes: tuple[str, ...],
    provider_calls: int,
    model_calls: int,
    network_calls: int,
    connector_calls: int,
    external_drs_calls: int,
    action_commit_packets_created: int,
    permissions_created: int,
    receipts_created: int,
    final_outputs_created: int,
    drs_writes: int,
    authority_created_count: int,
    real_world_effects_count: int,
) -> SelectiveRecomputationResultV01:
    provisional = SelectiveRecomputationResultV01(
        recomputation_result_id="g2e_selective_recomputation_result_v01:" + _ZERO_SHA256,
        recomputation_plan_id=recomputation_plan_id,
        baseline_runtime_report_id=baseline_runtime_report_id,
        recomputed_runtime_report_id=recomputed_runtime_report_id,
        preservation_proof_id=preservation_proof_id,
        ordered_recomputed_binding_ids=ordered_recomputed_binding_ids,
        ordered_invalidated_downstream_ids=ordered_invalidated_downstream_ids,
        ordered_recomputed_artifact_ids=ordered_recomputed_artifact_ids,
        ordered_preserved_artifact_ids=ordered_preserved_artifact_ids,
        ordered_unresolved_artifact_ids=ordered_unresolved_artifact_ids,
        ordered_partial_failure_ids=ordered_partial_failure_ids,
        parent_return_transition_decision_id=parent_return_transition_decision_id,
        result_status=result_status,
        reason_codes=reason_codes,
        provider_calls=provider_calls,
        model_calls=model_calls,
        network_calls=network_calls,
        connector_calls=connector_calls,
        external_drs_calls=external_drs_calls,
        action_commit_packets_created=action_commit_packets_created,
        permissions_created=permissions_created,
        receipts_created=receipts_created,
        final_outputs_created=final_outputs_created,
        drs_writes=drs_writes,
        authority_created_count=authority_created_count,
        real_world_effects_count=real_world_effects_count,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _selective_recomputation_result_errors_v01
    )


def validate_selective_recomputation_result_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        SelectiveRecomputationResultV01,
        "recomputation_execution",
        _selective_recomputation_result_errors_v01,
    )


def selective_recomputation_result_to_plain_data_v01(
    value: SelectiveRecomputationResultV01,
) -> dict[str, object]:
    return _serialize(
        value,
        SelectiveRecomputationResultV01,
        _selective_recomputation_result_errors_v01,
    )


def rebuild_selective_recomputation_result_identity_v01(
    value: SelectiveRecomputationResultV01,
) -> str:
    return _rebuild(value, SelectiveRecomputationResultV01)


def build_continuous_delta_runtime_trace_v01(
    *,
    delta_id: str,
    graph_id: str,
    affected_set_id: str,
    invalidation_report_id: str,
    preservation_proof_id: str,
    recomputation_plan_id: str,
    recomputation_result_id: str,
    plan_root_decision_input_id: str,
    plan_root_decision_id: str,
    final_root_decision_input_id: str,
    final_root_decision_id: str,
    ordered_transition_decision_ids: tuple[str, ...],
    ordered_causal_ref_ids: tuple[str, ...],
    ordered_source_artifact_ids: tuple[str, ...],
    ordered_downstream_artifact_ids: tuple[str, ...],
    provider_calls: int,
    model_calls: int,
    network_calls: int,
    connector_calls: int,
    external_drs_calls: int,
    real_world_effects_count: int,
) -> ContinuousDeltaRuntimeTraceV01:
    provisional = ContinuousDeltaRuntimeTraceV01(
        trace_id="g2e_continuous_delta_runtime_trace_v01:" + _ZERO_SHA256,
        delta_id=delta_id,
        graph_id=graph_id,
        affected_set_id=affected_set_id,
        invalidation_report_id=invalidation_report_id,
        preservation_proof_id=preservation_proof_id,
        recomputation_plan_id=recomputation_plan_id,
        recomputation_result_id=recomputation_result_id,
        plan_root_decision_input_id=plan_root_decision_input_id,
        plan_root_decision_id=plan_root_decision_id,
        final_root_decision_input_id=final_root_decision_input_id,
        final_root_decision_id=final_root_decision_id,
        ordered_transition_decision_ids=ordered_transition_decision_ids,
        ordered_causal_ref_ids=ordered_causal_ref_ids,
        ordered_source_artifact_ids=ordered_source_artifact_ids,
        ordered_downstream_artifact_ids=ordered_downstream_artifact_ids,
        provider_calls=provider_calls,
        model_calls=model_calls,
        network_calls=network_calls,
        connector_calls=connector_calls,
        external_drs_calls=external_drs_calls,
        real_world_effects_count=real_world_effects_count,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _continuous_delta_runtime_trace_errors_v01
    )


def validate_continuous_delta_runtime_trace_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        ContinuousDeltaRuntimeTraceV01,
        "parent_return",
        _continuous_delta_runtime_trace_errors_v01,
    )


def continuous_delta_runtime_trace_to_plain_data_v01(
    value: ContinuousDeltaRuntimeTraceV01,
) -> dict[str, object]:
    return _serialize(
        value,
        ContinuousDeltaRuntimeTraceV01,
        _continuous_delta_runtime_trace_errors_v01,
    )


def rebuild_continuous_delta_runtime_trace_identity_v01(
    value: ContinuousDeltaRuntimeTraceV01,
) -> str:
    return _rebuild(value, ContinuousDeltaRuntimeTraceV01)


def build_continuous_delta_runtime_report_v01(
    *,
    report_version: str,
    profile_id: str,
    ordered_source_binding_ids: tuple[str, ...],
    baseline_report_id: str,
    delta_id: str,
    graph_id: str,
    affected_set_id: str,
    invalidation_report_id: str,
    preservation_proof_id: str,
    recomputation_plan_id: str,
    recomputation_result_id: str,
    trace_id: str,
    plan_root_decision_input_id: str,
    plan_root_decision_id: str,
    final_root_decision_input_id: str,
    final_root_decision_id: str,
    changed_count: int,
    directly_affected_count: int,
    transitively_affected_count: int,
    invalidated_count: int,
    recomputed_count: int,
    preserved_count: int,
    unresolved_count: int,
    report_status: str,
    reason_codes: tuple[str, ...],
    root_review_required: bool,
    provider_calls: int,
    model_calls: int,
    network_calls: int,
    connector_calls: int,
    external_drs_calls: int,
    action_commit_packets_created: int,
    permissions_created: int,
    receipts_created: int,
    final_outputs_created: int,
    drs_writes: int,
    authority_created_count: int,
    real_world_effects_count: int,
) -> ContinuousDeltaRuntimeReportV01:
    provisional = ContinuousDeltaRuntimeReportV01(
        report_id="g2e_continuous_delta_runtime_report_v01:" + _ZERO_SHA256,
        report_version=report_version,
        profile_id=profile_id,
        ordered_source_binding_ids=ordered_source_binding_ids,
        baseline_report_id=baseline_report_id,
        delta_id=delta_id,
        graph_id=graph_id,
        affected_set_id=affected_set_id,
        invalidation_report_id=invalidation_report_id,
        preservation_proof_id=preservation_proof_id,
        recomputation_plan_id=recomputation_plan_id,
        recomputation_result_id=recomputation_result_id,
        trace_id=trace_id,
        plan_root_decision_input_id=plan_root_decision_input_id,
        plan_root_decision_id=plan_root_decision_id,
        final_root_decision_input_id=final_root_decision_input_id,
        final_root_decision_id=final_root_decision_id,
        changed_count=changed_count,
        directly_affected_count=directly_affected_count,
        transitively_affected_count=transitively_affected_count,
        invalidated_count=invalidated_count,
        recomputed_count=recomputed_count,
        preserved_count=preserved_count,
        unresolved_count=unresolved_count,
        report_status=report_status,
        reason_codes=reason_codes,
        root_review_required=root_review_required,
        provider_calls=provider_calls,
        model_calls=model_calls,
        network_calls=network_calls,
        connector_calls=connector_calls,
        external_drs_calls=external_drs_calls,
        action_commit_packets_created=action_commit_packets_created,
        permissions_created=permissions_created,
        receipts_created=receipts_created,
        final_outputs_created=final_outputs_created,
        drs_writes=drs_writes,
        authority_created_count=authority_created_count,
        real_world_effects_count=real_world_effects_count,
    )
    result = _finish_identity(provisional)
    return _require_built_valid(  # type: ignore[return-value]
        result, _continuous_delta_runtime_report_errors_v01
    )


def validate_continuous_delta_runtime_report_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    return _structural_report(
        value,
        ContinuousDeltaRuntimeReportV01,
        "bundle_final",
        _continuous_delta_runtime_report_errors_v01,
    )


def continuous_delta_runtime_report_to_plain_data_v01(
    value: ContinuousDeltaRuntimeReportV01,
) -> dict[str, object]:
    return _serialize(
        value,
        ContinuousDeltaRuntimeReportV01,
        _continuous_delta_runtime_report_errors_v01,
    )


def rebuild_continuous_delta_runtime_report_identity_v01(
    value: ContinuousDeltaRuntimeReportV01,
) -> str:
    return _rebuild(value, ContinuousDeltaRuntimeReportV01)


def _continuous_delta_execution_bundle_errors_v01(
    value: object,
) -> tuple[str, ...]:
    if type(value) is not ContinuousDeltaExecutionBundleV01:
        return ("g2e_recomputation_result_invalid",)
    errors: list[str] = []
    registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
    structural_families = (
        (value.source_bindings, DeltaSourceBindingV01, _delta_source_binding_errors),
        (value.changed_field_bindings, ChangedFieldBindingV01, _changed_field_binding_errors),
        (
            value.changed_artifact_bindings,
            ChangedArtifactBindingV01,
            _changed_artifact_binding_errors,
        ),
        (value.dependency_edges, DeltaDependencyEdgeV01, _delta_dependency_edge_errors),
        (
            value.invalidation_records,
            ArtifactInvalidationRecordV01,
            _invalidation_record_errors_v01,
        ),
        (
            value.recomputed_bindings,
            RecomputedArtifactBindingV01,
            _recomputed_artifact_binding_errors_v01,
        ),
        (
            value.g2e_validation_reports,
            ContinuousDeltaValidationReportV01,
            _validation_report_errors,
        ),
    )
    for family, item_type, error_function in structural_families:
        if type(family) is not tuple or any(
            type(item) is not item_type or error_function(item) for item in family
        ):
            errors.append("g2e_recomputation_result_invalid")
    for artifact in (
        value.delta_source_proposed_artifact,
        value.delta_source_artifact,
        value.dependency_graph_artifact,
        value.affected_set_artifact,
        value.invalidation_report_artifact,
        value.plan_proposed_artifact,
        value.plan_root_decision_artifact,
        value.plan_accepted_artifact,
        value.preservation_proof_artifact,
        value.final_root_decision_artifact,
        value.runtime_report_artifact,
    ):
        if type(artifact) is not KernelArtifactV01 or validate_kernel_artifact_v01(
            artifact
        ):
            errors.append("g2e_recomputation_result_invalid")
    if (
        validate_continuous_delta_source_context_v01(value.source_context).status
        != "PASS"
        or _world_state_delta_errors(value.delta)
        or _dependency_graph_index_errors(value.dependency_graph)
        or _affected_set_request_errors(value.affected_request)
        or _affected_set_result_errors(value.affected_result)
        or _invalidation_report_errors_v01(value.invalidation_report)
        or _selective_recomputation_plan_errors_v01(value.recomputation_plan)
        or _preservation_proof_errors_v01(value.preservation_proof)
        or _selective_recomputation_result_errors_v01(value.recomputation_result)
        or _continuous_delta_runtime_trace_errors_v01(value.runtime_trace)
        or _continuous_delta_runtime_report_errors_v01(value.runtime_report)
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        type(value.recomputed_g2d_execution_bundle)
        is not FractalRuntimeExecutionBundleV02
        or validate_fractal_runtime_execution_bundle_v02(
            value.recomputed_g2d_execution_bundle
        ).status
        != "PASS"
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        root_runtime.validate_root_decision_input_v01(
            kernel=value.source_context.root_kernel,
            decision_input=value.plan_root_decision_input,
        )
        or root_runtime.validate_root_decision_result_v01(
            kernel=value.source_context.root_kernel,
            decision_input=value.plan_root_decision_input,
            result=value.plan_root_decision_result,
        )
        or root_runtime.validate_root_decision_input_v01(
            kernel=value.source_context.root_kernel,
            decision_input=value.final_root_decision_input,
        )
        or root_runtime.validate_root_decision_result_v01(
            kernel=value.source_context.root_kernel,
            decision_input=value.final_root_decision_input,
            result=value.final_root_decision_result,
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        type(value.g2e_transition_decisions) is not tuple
        or len(value.g2e_transition_decisions) != 10
        or any(
            _continuous_delta_transition_decision_errors_v01(
                decision, registry=registry
            )
            for decision in value.g2e_transition_decisions
        )
        or tuple(decision.rule_id for decision in value.g2e_transition_decisions)
        != tuple(f"g2e_t{index:02d}_{suffix}" for index, suffix in (
            (1, "delta_validate"),
            (2, "affected_set_derive"),
            (3, "invalidation_derive"),
            (4, "plan_root_review"),
            (5, "plan_root_accept"),
            (6, "plan_root_reject"),
            (7, "selective_recompute"),
            (8, "recompute_block"),
            (9, "parent_return"),
            (10, "report_finalize"),
        ))
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        type(value.g2e_causal_consumption_refs) is not tuple
        or any(
            type(item) is not CausalConsumptionRefV01
            or validate_causal_consumption_ref_v01(item)
            for item in value.g2e_causal_consumption_refs
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    artifact_instances = (
        value.delta_source_proposed_artifact,
        value.delta_source_artifact,
        value.dependency_graph_artifact,
        value.affected_set_artifact,
        value.invalidation_report_artifact,
        value.plan_proposed_artifact,
        value.plan_accepted_artifact,
        value.preservation_proof_artifact,
        value.runtime_report_artifact,
    )
    if len({item.artifact_id for item in artifact_instances}) != 9:
        errors.append("g2e_recomputation_result_invalid")
    if (
        value.delta.delta_id != value.recomputation_plan.delta_id
        or value.affected_result.affected_set_id
        != value.recomputation_plan.affected_set_id
        or value.invalidation_report.invalidation_report_id
        != value.recomputation_plan.invalidation_report_id
        or value.recomputation_plan.recomputation_plan_id
        != value.recomputation_result.recomputation_plan_id
        or value.preservation_proof.preservation_proof_id
        != value.recomputation_result.preservation_proof_id
        or value.runtime_trace.recomputation_result_id
        != value.recomputation_result.recomputation_result_id
        or value.runtime_report.trace_id != value.runtime_trace.trace_id
        or value.plan_root_decision_result.decision != "ACCEPT"
        or value.plan_root_decision_result.selected_candidate_id
        != value.recomputation_plan.recomputation_plan_id
        or value.final_root_decision_result.decision != "ACCEPT"
        or value.final_root_decision_result.selected_candidate_id
        != value.recomputation_result.recomputation_result_id
    ):
        errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def build_continuous_delta_execution_bundle_v01(
    *,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    delta: WorldStateDeltaV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
    affected_request: AffectedSetRequestV01,
    affected_result: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
    delta_source_proposed_artifact: KernelArtifactV01,
    delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    affected_set_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
    recomputation_plan: SelectiveRecomputationPlanV01,
    plan_proposed_artifact: KernelArtifactV01,
    plan_root_decision_input: RootDecisionInputV01,
    plan_root_decision_result: RootDecisionResultV01,
    plan_root_decision_artifact: KernelArtifactV01,
    plan_accepted_artifact: KernelArtifactV01,
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    preservation_proof: PreservationProofV01,
    preservation_proof_artifact: KernelArtifactV01,
    recomputation_result: SelectiveRecomputationResultV01,
    g2e_validation_reports: tuple[ContinuousDeltaValidationReportV01, ...],
    g2e_transition_decisions: tuple[TransitionDecisionV01, ...],
    g2e_causal_consumption_refs: tuple[CausalConsumptionRefV01, ...],
    final_root_decision_input: RootDecisionInputV01,
    final_root_decision_result: RootDecisionResultV01,
    final_root_decision_artifact: KernelArtifactV01,
    runtime_trace: ContinuousDeltaRuntimeTraceV01,
    runtime_report: ContinuousDeltaRuntimeReportV01,
    runtime_report_artifact: KernelArtifactV01,
) -> ContinuousDeltaExecutionBundleV01:
    value = ContinuousDeltaExecutionBundleV01(
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        delta=delta,
        dependency_edges=dependency_edges,
        dependency_graph=dependency_graph,
        affected_request=affected_request,
        affected_result=affected_result,
        invalidation_records=invalidation_records,
        invalidation_report=invalidation_report,
        delta_source_proposed_artifact=delta_source_proposed_artifact,
        delta_source_artifact=delta_source_artifact,
        dependency_graph_artifact=dependency_graph_artifact,
        affected_set_artifact=affected_set_artifact,
        invalidation_report_artifact=invalidation_report_artifact,
        recomputation_plan=recomputation_plan,
        plan_proposed_artifact=plan_proposed_artifact,
        plan_root_decision_input=plan_root_decision_input,
        plan_root_decision_result=plan_root_decision_result,
        plan_root_decision_artifact=plan_root_decision_artifact,
        plan_accepted_artifact=plan_accepted_artifact,
        recomputed_g2d_execution_bundle=recomputed_g2d_execution_bundle,
        recomputed_bindings=recomputed_bindings,
        preservation_proof=preservation_proof,
        preservation_proof_artifact=preservation_proof_artifact,
        recomputation_result=recomputation_result,
        g2e_validation_reports=g2e_validation_reports,
        g2e_transition_decisions=g2e_transition_decisions,
        g2e_causal_consumption_refs=g2e_causal_consumption_refs,
        final_root_decision_input=final_root_decision_input,
        final_root_decision_result=final_root_decision_result,
        final_root_decision_artifact=final_root_decision_artifact,
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        runtime_report_artifact=runtime_report_artifact,
    )
    errors = _continuous_delta_execution_bundle_errors_v01(value)
    if errors:
        raise ValueError(errors[0])
    return value


def validate_continuous_delta_execution_bundle_v01(
    value: object,
) -> ContinuousDeltaValidationReportV01:
    errors = _continuous_delta_execution_bundle_errors_v01(value)
    validated_id = None
    if not errors and type(value) is ContinuousDeltaExecutionBundleV01:
        validated_id = value.runtime_report.report_id
    return _contextual_report_v01(
        validation_target="ContinuousDeltaExecutionBundleV01",
        validated_object_id=validated_id,
        failure_stage="bundle_final",
        reason_codes=errors,
    )


def _selective_plan_source_errors_v01(
    *,
    delta: WorldStateDeltaV01,
    affected_set: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> tuple[str, ...]:
    errors: list[str] = []
    if (
        _world_state_delta_errors(delta)
        or _affected_set_result_errors(affected_set)
        or _invalidation_report_errors_v01(invalidation_report)
        or _dependency_graph_index_errors(dependency_graph)
        or type(invalidation_records) is not tuple
        or any(_invalidation_record_errors_v01(item) for item in invalidation_records)
        or type(source_bindings) is not tuple
        or any(_delta_source_binding_errors(item) for item in source_bindings)
        or type(changed_field_bindings) is not tuple
        or any(_changed_field_binding_errors(item) for item in changed_field_bindings)
        or type(changed_artifact_bindings) is not tuple
        or any(_changed_artifact_binding_errors(item) for item in changed_artifact_bindings)
        or type(dependency_edges) is not tuple
        or any(_delta_dependency_edge_errors(item) for item in dependency_edges)
    ):
        errors.append("g2e_recomputation_plan_invalid")
    context_report = validate_continuous_delta_source_context_v01(source_context)
    if context_report.status != "PASS":
        errors.extend(context_report.reason_codes or ("g2e_delta_source_unvalidated",))
    invalidation_report_validation = validate_invalidation_report_against_sources_v01(
        invalidation_report,
        records=invalidation_records,
        affected_set=affected_set,
        delta=delta,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        dependency_graph=dependency_graph,
    )
    if invalidation_report_validation.status != "PASS":
        errors.extend(
            invalidation_report_validation.reason_codes
            or ("g2e_recomputation_plan_invalid",)
        )
    baseline = source_context.baseline_g2d_execution_bundle
    route = source_context.baseline_g2c_route_eligibility_artifact
    if (
        type(baseline) is not FractalRuntimeExecutionBundleV02
        or validate_fractal_runtime_execution_bundle_v02(baseline).status != "PASS"
        or type(route) is not KernelArtifactV01
        or validate_kernel_artifact_v01(route)
    ):
        errors.append("g2e_topology_binding_mismatch")
    elif (
        baseline.topology.source_route_eligibility_artifact_id != route.artifact_id
        or delta.baseline_report_id != baseline.runtime_report.report_id
        or delta.baseline_graph_id != dependency_graph.graph_id
        or affected_set.graph_id != dependency_graph.graph_id
    ):
        errors.append("g2e_topology_binding_mismatch")
    if invalidation_report.ordered_route_revalidation_ids or any(
        item.g2c_route_relation == "ROUTE_REVALIDATION_REQUIRED"
        for item in invalidation_records
    ):
        errors.append("g2e_route_revalidation_required")
    if tuple(item.artifact_id for item in invalidation_records) != (
        affected_set.ordered_affected_ids
    ):
        errors.append("g2e_recomputation_plan_invalid")
    return _ordered_reasons(errors)


def _g2e4_baseline_runtime_artifact_ledger_v01(
    baseline: FractalRuntimeExecutionBundleV02,
) -> dict[str, dict[str, object]]:
    if (
        type(baseline) is not FractalRuntimeExecutionBundleV02
        or validate_fractal_runtime_execution_bundle_v02(baseline).status != "PASS"
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    input_by_cell = {item.cell_id: item for item in baseline.cell_inputs}
    node_by_id = {item.node_id: item for item in baseline.topology_nodes}
    if (
        len(input_by_cell) != len(baseline.cell_inputs)
        or len(node_by_id) != len(baseline.topology_nodes)
        or len(baseline.queue_entries) != len(baseline.queue_artifacts)
        or len(baseline.cell_results) != len(baseline.result_artifacts)
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    ledger: dict[str, dict[str, object]] = {}
    for entry, artifact in zip(
        baseline.queue_entries, baseline.queue_artifacts, strict=True
    ):
        cell_input = input_by_cell.get(entry.cell_id)
        node = node_by_id.get(entry.node_id)
        if (
            cell_input is None
            or node is None
            or entry.node_id not in cell_input.ordered_node_ids
            or artifact.artifact_id in ledger
        ):
            raise ValueError("g2e_topology_binding_mismatch")
        ledger[artifact.artifact_id] = {
            "ownership_class": "CELL_QUEUE",
            "artifact": artifact,
            "queue_entry": entry,
            "cell_input": cell_input,
            "node": node,
        }
    for result, artifact in zip(
        baseline.cell_results, baseline.result_artifacts, strict=True
    ):
        cell_input = input_by_cell.get(result.cell_id)
        if cell_input is None or artifact.artifact_id in ledger:
            raise ValueError("g2e_topology_binding_mismatch")
        ledger[artifact.artifact_id] = {
            "ownership_class": "CELL_RESULT",
            "artifact": artifact,
            "cell_result": result,
            "cell_input": cell_input,
        }
    for ownership_class, artifact in (
        ("WHOLE_RUNTIME_TOPOLOGY", baseline.topology_artifact),
        ("WHOLE_RUNTIME_REPORT", baseline.report_artifact),
    ):
        if artifact.artifact_id in ledger:
            raise ValueError("g2e_topology_binding_mismatch")
        ledger[artifact.artifact_id] = {
            "ownership_class": ownership_class,
            "artifact": artifact,
        }
    return ledger


def _g2e4_resolve_runtime_artifact_projection_v01(
    *,
    source_artifact: KernelArtifactV01,
    ledger: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    direct = ledger.get(source_artifact.artifact_id)
    if direct is not None:
        if source_artifact != direct["artifact"]:
            raise ValueError("g2e_topology_binding_mismatch")
        return direct
    plain = kernel_artifact_to_plain_dict_v01(source_artifact)
    payload = plain["payload"]
    if (
        type(payload) is not dict
        or payload.get("projection_profile_id")
        != "g2e_baseline_runtime_artifact_projection_v01"
    ):
        return None
    if set(payload) != {
        "projection_profile_id",
        "projected_runtime_artifact",
        "projected_runtime_artifact_sha256",
    }:
        raise ValueError("g2e_topology_binding_mismatch")
    projected = payload["projected_runtime_artifact"]
    projected_sha256 = payload["projected_runtime_artifact_sha256"]
    if type(projected) is not dict or type(projected_sha256) is not str:
        raise ValueError("g2e_topology_binding_mismatch")
    projected_bytes = canonical_json_bytes_v01(projected)
    if hashlib.sha256(projected_bytes).hexdigest() != projected_sha256:
        raise ValueError("g2e_topology_binding_mismatch")
    matches = tuple(
        row
        for row in ledger.values()
        if canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(row["artifact"])
        )
        == projected_bytes
    )
    if len(matches) != 1:
        raise ValueError("g2e_topology_binding_mismatch")
    matched_artifact = matches[0]["artifact"]
    if (
        source_artifact.transaction_id != matched_artifact.transaction_id
        or source_artifact.owner_root_id != matched_artifact.owner_root_id
        or source_artifact.parent_refs != (matched_artifact.artifact_id,)
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    return matches[0]


def _g2e4_validate_selected_child_witness_v01(
    baseline: FractalRuntimeExecutionBundleV02,
    cell_input: object,
) -> None:
    if cell_input not in baseline.cell_inputs or cell_input.parent_cell_id is None:
        raise ValueError("g2e_topology_binding_mismatch")
    parent_input = next(
        (
            item
            for item in baseline.cell_inputs
            if item.cell_id == cell_input.parent_cell_id
        ),
        None,
    )
    projection = next(
        (
            item
            for item in baseline.scope_projections
            if item.child_cell_id == cell_input.cell_id
        ),
        None,
    )
    if parent_input is None or projection is None:
        raise ValueError("g2e_topology_binding_mismatch")
    try:
        canonical_child_index = parent_input.ordered_planned_child_cell_ids.index(
            cell_input.cell_id
        )
    except ValueError as error:
        raise ValueError("g2e_topology_binding_mismatch") from error
    expected_cell_id = g2d_runtime.derive_fractal_child_cell_id_v02(
        topology_seed_id=baseline.topology_seed.topology_seed_id,
        parent_cell_id=parent_input.cell_id,
        canonical_child_index=canonical_child_index,
        accepted_mode=baseline.source_binding.accepted_mode,
        selected_local_mode_profile_id=(
            baseline.source_binding.selected_local_mode_profile_id
        ),
        source_mode_profile_set_id=(
            baseline.source_binding.source_mode_profile_set_id
        ),
        child_scope_ref=projection.child_scope_ref,
        runtime_policy_id=baseline.source_binding.runtime_policy_id,
        required_capability_ids=(
            baseline.source_binding.required_downstream_capability_ids
        ),
        forbidden_claims=baseline.source_context.runtime_policy.forbidden_claims,
        child_depth=cell_input.cell_depth,
    )
    if expected_cell_id != cell_input.cell_id:
        raise ValueError("g2e_topology_binding_mismatch")


def _derive_selective_recomputation_plan_v01(
    *,
    delta: WorldStateDeltaV01,
    affected_set: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> SelectiveRecomputationPlanV01:
    errors = _selective_plan_source_errors_v01(
        delta=delta,
        affected_set=affected_set,
        invalidation_records=invalidation_records,
        invalidation_report=invalidation_report,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        dependency_graph=dependency_graph,
    )
    if errors:
        raise ValueError(errors[0])
    baseline = source_context.baseline_g2d_execution_bundle
    topology = baseline.topology
    source_artifact_ids = tuple(
        artifact.artifact_id for artifact in source_context.baseline_source_artifacts
    )
    affected_source_ids = tuple(
        artifact_id
        for artifact_id in affected_set.ordered_affected_ids
        if artifact_id in source_artifact_ids
    )
    if not affected_source_ids:
        raise ValueError("g2e_topology_binding_mismatch")
    source_artifact_by_id = {
        artifact.artifact_id: artifact
        for artifact in source_context.baseline_source_artifacts
    }
    if any(
        artifact_id not in source_artifact_by_id
        for artifact_id in affected_set.ordered_affected_ids
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    ledger = _g2e4_baseline_runtime_artifact_ledger_v01(baseline)
    mapped_rows = tuple(
        row
        for artifact_id in affected_set.ordered_affected_ids
        for row in (
            _g2e4_resolve_runtime_artifact_projection_v01(
                source_artifact=source_artifact_by_id[artifact_id],
                ledger=ledger,
            ),
        )
        if row is not None
    )
    if any(
        str(row["ownership_class"]).startswith("WHOLE_RUNTIME")
        for row in mapped_rows
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    seed_rows = tuple(
        row
        for row in mapped_rows
        if row["ownership_class"] == "CELL_QUEUE"
        and row["queue_entry"].predecessor_queue_entry_id is None
    )
    if len(seed_rows) != 1 or any(
        row["ownership_class"] != "CELL_QUEUE" for row in mapped_rows
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    seed = seed_rows[0]
    selected_input = seed["cell_input"]
    selected_node = seed["node"]
    seed_entry = seed["queue_entry"]
    if (
        seed_entry.queue_entry_id not in selected_input.ordered_initial_queue_entry_ids
        or selected_node.node_id not in selected_input.ordered_node_ids
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    _g2e4_validate_selected_child_witness_v01(baseline, selected_input)
    selected_node_ids = {selected_node.node_id}
    changed = True
    while changed:
        changed = False
        for edge in baseline.topology_edges:
            if (
                edge.cell_projection_class == "FRACTAL_LEAF_PROJECTION"
                and edge.source_node_id in selected_node_ids
                and edge.target_node_id not in selected_node_ids
                and edge.target_node_id in selected_input.ordered_node_ids
            ):
                selected_node_ids.add(edge.target_node_id)
                changed = True
    ordered_work_node_ids = tuple(
        node.node_id
        for node in baseline.topology_nodes
        if node.node_id in selected_node_ids
    )
    if (
        ordered_work_node_ids != selected_input.ordered_node_ids
        or not ordered_work_node_ids
        or len(ordered_work_node_ids) >= len(topology.ordered_node_ids)
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    policy = baseline.source_context.runtime_policy
    registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
    queue_bound = min(
        MAX_DEPENDENCY_GRAPH_EDGES_V01,
        max(1, policy.max_total_cells * len(ordered_work_node_ids) * 5),
    )
    return build_selective_recomputation_plan_v01(
        delta_id=delta.delta_id,
        affected_set_id=affected_set.affected_set_id,
        invalidation_report_id=invalidation_report.invalidation_report_id,
        source_route_eligibility_artifact_id=(
            source_context.baseline_g2c_route_eligibility_artifact.artifact_id
        ),
        source_topology_id=topology.topology_id,
        accepted_mode=topology.accepted_mode,
        accepted_scope_ref=topology.accepted_scope_ref,
        ordered_affected_cell_ids=(selected_input.cell_id,),
        ordered_affected_artifact_ids=affected_set.ordered_affected_ids,
        ordered_work_node_ids=ordered_work_node_ids,
        ordered_preserved_artifact_ids=affected_set.ordered_unaffected_ids,
        max_work_items=len(ordered_work_node_ids),
        max_queue_entries=queue_bound,
        max_wall_time_units=policy.max_wall_time_units,
        max_token_budget=policy.max_token_budget,
        max_provider_calls=0,
        transition_profile_id=registry.registry_id,
        root_review_required=True,
        plan_status="PASS",
        reason_codes=(),
        trace_refs=(
            delta.delta_id,
            affected_set.affected_set_id,
            invalidation_report.invalidation_report_id,
            source_context.baseline_g2c_route_eligibility_artifact.artifact_id,
            topology.topology_id,
            baseline.runtime_report.report_id,
            registry.registry_id,
        ),
    )


def build_selective_recomputation_plan_from_affected_set_v01(
    *,
    delta: WorldStateDeltaV01,
    affected_set: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> SelectiveRecomputationPlanV01:
    return _derive_selective_recomputation_plan_v01(
        delta=delta,
        affected_set=affected_set,
        invalidation_records=invalidation_records,
        invalidation_report=invalidation_report,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        dependency_edges=dependency_edges,
        dependency_graph=dependency_graph,
    )


def validate_selective_recomputation_plan_against_sources_v01(
    value: SelectiveRecomputationPlanV01,
    *,
    delta: WorldStateDeltaV01,
    affected_set: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> ContinuousDeltaValidationReportV01:
    errors = list(_selective_recomputation_plan_errors_v01(value))
    try:
        expected = _derive_selective_recomputation_plan_v01(
            delta=delta,
            affected_set=affected_set,
            invalidation_records=invalidation_records,
            invalidation_report=invalidation_report,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        if type(value) is not SelectiveRecomputationPlanV01 or value != expected:
            errors.append("g2e_recomputation_plan_invalid")
    except ValueError as exc:
        reason = str(exc)
        errors.append(
            reason if reason in PUBLIC_G2E_REASON_CODES_V01 else "g2e_recomputation_plan_invalid"
        )
    reasons = _ordered_reasons(errors)
    return _contextual_report_v01(
        validation_target="selective_plan_against_sources",
        validated_object_id=value.recomputation_plan_id if not reasons else None,
        failure_stage="recomputation_plan",
        reason_codes=reasons,
    )


def _continuous_delta_transition_decision_errors_v01(
    value: object,
    *,
    registry: object,
) -> tuple[str, ...]:
    try:
        if (
            transition_runtime.validate_continuous_delta_transition_registry_profile_v01(
                registry
            )
            or type(value) is not TransitionDecisionV01
        ):
            return ("g2e_object_invalid",)
        transition_runtime.continuous_delta_transition_decision_to_plain_dict_v01(
            value
        )
        if value.registry_id != registry.registry_id:
            return ("g2e_object_invalid",)
        return ()
    except Exception:
        return ("g2e_object_invalid",)


def _g2e4_transition_decisions_v01(
) -> tuple[TransitionDecisionV01, ...]:
    registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
    decisions: list[TransitionDecisionV01] = []
    for rule in registry.rules:
        decisions.append(
            transition_runtime.lookup_transition_v01(
                registry=registry,
                abi_major_version=rule.abi_major_version,
                source_artifact_type=rule.source_artifact_type,
                source_lifecycle_state=rule.source_lifecycle_state,
                actor_role=rule.actor_role,
                attempted_effect=rule.attempted_effect,
                target_artifact_type=rule.target_artifact_type,
                satisfied_guards=rule.required_guards,
                root_commit_present=rule.root_commit_required,
            )
        )
    result = tuple(decisions)
    if len(result) != 10 or any(
        _continuous_delta_transition_decision_errors_v01(
            item, registry=registry
        )
        for item in result
    ):
        raise ValueError("g2e_object_invalid")
    return result


def _g2e4_prefix_arguments_v01(
    state: dict[str, object],
    **overrides: object,
) -> dict[str, object]:
    result = {
        "settled_budget_log": state["budgets"],
        "settled_queue_entry_log": state["queue_entries"],
        "settled_queue_artifact_log": state["queue_artifacts"],
        "settled_cell_inputs": state["cell_inputs"],
        "settled_scope_projections": state["scope_projections"],
        "settled_revise_observations": state["revise_observations"],
        "settled_backpressure_states": state["backpressure_states"],
        "settled_validation_reports": state["prefix_reports"],
        "observed_work_context": state["observed_work_context"],
    }
    result.update(overrides)
    return result


def _g2e4_refresh_prefix_reports_v01(state: dict[str, object]) -> None:
    base_reports = state["base_reports"]
    queue_entries = state["queue_entries"]
    scope_reports = state["scope_reports"]
    input_reports = state["input_reports"]
    if not all(
        type(item) is tuple
        for item in (base_reports, queue_entries, scope_reports, input_reports)
    ):
        raise ValueError("g2d_validation_status_stage_mismatch")
    state["prefix_reports"] = (
        *base_reports,
        *(
            g2d_runtime.validate_fractal_cell_queue_entry_v02(item)
            for item in queue_entries
        ),
        *scope_reports,
        *input_reports,
    )


def _g2e4_latest_queue_entries_v01(
    state: dict[str, object],
) -> tuple[object, ...]:
    queue_entries = state["queue_entries"]
    nodes = state["topology_nodes"]
    if type(queue_entries) is not tuple or type(nodes) is not tuple:
        raise ValueError("g2d_queue_order_mismatch")
    by_key: dict[tuple[str, str], object] = {}
    for entry in queue_entries:
        by_key[(entry.cell_id, entry.node_id)] = entry
    ordered: list[object] = []
    cell_order = tuple(
        dict.fromkeys(entry.cell_id for entry in queue_entries)
    )
    for cell_id in cell_order:
        for node in nodes:
            candidate = by_key.get((cell_id, node.node_id))
            if candidate is not None:
                ordered.append(candidate)
    return tuple(ordered)


def _g2e4_artifact_by_queue_id_v01(
    state: dict[str, object],
) -> dict[str, KernelArtifactV01]:
    entries = state["queue_entries"]
    artifacts = state["queue_artifacts"]
    if type(entries) is not tuple or type(artifacts) is not tuple:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if len(entries) != len(artifacts):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    return {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(entries, artifacts, strict=True)
    }


def _g2e4_budget_by_id_v01(
    state: dict[str, object],
) -> dict[str, object]:
    budgets = state["budgets"]
    if type(budgets) is not tuple:
        raise ValueError("g2d_budget_invalid")
    return {item.budget_id: item for item in budgets}


def _g2e4_dependencies_v01(
    state: dict[str, object],
    entry: object,
) -> tuple[object, ...]:
    edges = state["topology_edges"]
    cell_input = next(
        (item for item in state["cell_inputs"] if item.cell_id == entry.cell_id),
        None,
    )
    latest = {
        (item.cell_id, item.node_id): item
        for item in _g2e4_latest_queue_entries_v01(state)
    }
    if type(edges) is not tuple or cell_input is None:
        raise ValueError("g2d_queue_order_mismatch")
    projected_node_ids = set(cell_input.ordered_node_ids)
    projection_class = (
        "ROOT_CELL_PROJECTION"
        if cell_input.parent_cell_id is None
        else "FRACTAL_LEAF_PROJECTION"
    )
    dependencies: list[object] = []
    for edge in sorted(edges, key=lambda item: item.canonical_index):
        if (
            edge.target_node_id != entry.node_id
            or edge.cell_projection_class != projection_class
            or edge.source_node_id not in projected_node_ids
            or edge.target_node_id not in projected_node_ids
        ):
            continue
        dependency = latest.get((entry.cell_id, edge.source_node_id))
        if dependency is None or dependency.state not in {
            "COMPLETED",
            "DEGRADED",
            "BLOCKED",
            "NEEDS_USER",
            "DEADEND",
        }:
            raise ValueError("g2d_queue_order_mismatch")
        dependencies.append(dependency)
    return tuple(dependencies)


def _g2e4_evaluate_queue_transition_v01(
    state: dict[str, object],
    *,
    source_artifact: KernelArtifactV01,
    node: object,
    current_entry: object | None,
    cell_input: object | None,
    cell_budget: object,
    global_budget: object,
    dependencies: tuple[object, ...] = (),
    queue_reason_codes: tuple[str, ...] = (),
    observed_output_refs: tuple[str, ...] = (),
    observed_evidence_refs: tuple[str, ...] = (),
    advisory_refs: tuple[str, ...] = (),
    local_child_result: object | None = None,
    local_child_result_artifact: KernelArtifactV01 | None = None,
    validation_report: object | None = None,
    parent_return_family: dict[str, object] | None = None,
    cell_id: str | None = None,
    parent_cell_id: str | None = None,
    planned_child_cell_id: str | None = None,
    cell_depth: int | None = None,
    scope_ref: str | None = None,
) -> TransitionDecisionV01:
    topology = state["topology"]
    family = parent_return_family or {}
    decision = g2d_runtime.evaluate_fractal_runtime_state_transition_v02(
        source_context=state["source_context"],
        topology=topology,
        source_artifact=source_artifact,
        current_entry=current_entry,
        node=node,
        cell_input=cell_input,
        cell_id=(
            current_entry.cell_id
            if current_entry is not None and cell_id is None
            else cell_id or topology.root_cell_id
        ),
        parent_cell_id=(
            current_entry.parent_cell_id
            if current_entry is not None and parent_cell_id is None
            else parent_cell_id
        ),
        planned_child_cell_id=(
            current_entry.planned_child_cell_id
            if current_entry is not None and planned_child_cell_id is None
            else planned_child_cell_id
        ),
        cell_depth=(
            current_entry.cell_depth
            if current_entry is not None and cell_depth is None
            else cell_depth or 0
        ),
        scope_ref=(
            current_entry.scope_ref
            if current_entry is not None and scope_ref is None
            else scope_ref or topology.accepted_scope_ref
        ),
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        dependencies=dependencies,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        validation_report=validation_report,
        parent_return_pre_post_vv_terminal_queue_entries=family.get(
            "pre_post_vv_terminal_queue_entries", ()
        ),
        parent_return_child_results=family.get("child_results", ()),
        parent_return_partial_failures=family.get("partial_failures", ()),
        parent_return_result_proposal=family.get("result_proposal"),
        parent_return_post_vv_report=family.get("post_vv_report"),
        parent_return_gt_advisory_report=family.get("gt_advisory_report"),
        parent_return_validation_reports=family.get("validation_reports", ()),
        revise_observation=None,
        backpressure_state=None,
        transition_registry=state["transition_registry"],
        **_g2e4_prefix_arguments_v01(state),
    )
    if type(decision) is not TransitionDecisionV01:
        raise ValueError("g2d_transition_decision_substituted")
    return decision


def _g2e4_build_budget_successor_v01(
    state: dict[str, object],
    predecessor: object,
    *,
    event: str,
    transition_decision: TransitionDecisionV01 | None = None,
    cell_input: object | None = None,
    budget_state: str = "ACTIVE",
    allocation_parent: object | None = None,
    owning_cell_id: str | None = None,
    budget_scope: str = "ROOT_GLOBAL_AND_CELL",
    canonical_child_index: int | None = None,
    allocation_queue_entries: tuple[object, ...] = (),
    paired_cell_budget: object | None = None,
    child_result: object | None = None,
) -> object:
    return g2d_runtime.build_fractal_runtime_budget_v02(
        policy=state["source_context"].runtime_policy,
        topology_seed=state["topology_seed"],
        allocation_parent_budget=allocation_parent,
        predecessor_budget=predecessor,
        owning_cell_id=owning_cell_id or state["topology"].root_cell_id,
        budget_scope=budget_scope,
        budget_state=budget_state,
        budget_event_kind=event,
        budget_context_input=cell_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queue_entries,
        transition_decision=transition_decision,
        paired_cell_budget=paired_cell_budget,
        child_result=child_result,
    )


def _g2e4_live_budget_heads_v01(
    state: dict[str, object],
    cell_id: str,
) -> tuple[object, object]:
    topology = state["topology"]
    budgets = state["budgets"]
    if type(budgets) is not tuple:
        raise ValueError("g2d_budget_invalid")
    global_rows = tuple(
        item
        for item in budgets
        if item.owning_cell_id == topology.root_cell_id
        and item.budget_scope == "ROOT_GLOBAL_AND_CELL"
    )
    local_rows = tuple(item for item in budgets if item.owning_cell_id == cell_id)
    if not global_rows or not local_rows:
        raise ValueError("g2d_budget_invalid")
    return local_rows[-1], global_rows[-1]


def _g2e4_append_budget_pair_v01(
    state: dict[str, object],
    cell_budget: object,
    global_budget: object,
) -> None:
    suffix = (global_budget,) if cell_budget is global_budget else (
        cell_budget,
        global_budget,
    )
    if any(item in state["budgets"] for item in suffix):
        raise ValueError("g2d_budget_double_spend")
    state["budgets"] = (*state["budgets"], *suffix)


def _g2e4_append_queue_target_v01(
    state: dict[str, object],
    *,
    current_entry: object,
    current_artifact: KernelArtifactV01,
    node: object,
    cell_input: object,
    transition_decision: TransitionDecisionV01,
    cell_budget_after: object,
    global_budget_after: object,
    dependencies: tuple[object, ...],
    queue_reason_codes: tuple[str, ...] = (),
    observed_output_refs: tuple[str, ...] = (),
    observed_evidence_refs: tuple[str, ...] = (),
    advisory_refs: tuple[str, ...] = (),
    local_child_result: object | None = None,
    local_child_result_artifact: KernelArtifactV01 | None = None,
) -> tuple[object, KernelArtifactV01]:
    target = g2d_runtime.advance_fractal_cell_queue_v02(
        source_context=state["source_context"],
        topology=state["topology"],
        current_entry=current_entry,
        node=node,
        cell_input=cell_input,
        transition_decision=transition_decision,
        cell_budget_after=cell_budget_after,
        global_budget_after=global_budget_after,
        dependencies=dependencies,
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        cell_instantiation_order=tuple(
            item.cell_id for item in state["cell_inputs"]
        ),
        projected_node_ids=cell_input.ordered_node_ids,
        round_start_queue_entries=_g2e4_latest_queue_entries_v01(state),
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        **_g2e4_prefix_arguments_v01(state),
    )
    next_entries = (*state["queue_entries"], target)
    artifact = g2d_runtime.project_fractal_cell_queue_entry_kernel_artifact_v02(
        target,
        topology_artifact=state["topology_artifact"],
        predecessor_artifact=current_artifact,
        activation_parent_artifact=None,
        local_child_result_artifact=local_child_result_artifact,
        source_context=state["source_context"],
        **_g2e4_prefix_arguments_v01(
            state,
            settled_queue_entry_log=next_entries,
        ),
    )
    state["queue_entries"] = next_entries
    state["queue_artifacts"] = (*state["queue_artifacts"], artifact)
    state["runtime_artifacts"] = (*state["runtime_artifacts"], artifact)
    state["queue_decisions"] = (*state["queue_decisions"], transition_decision)
    _g2e4_refresh_prefix_reports_v01(state)
    return target, artifact


def _g2e4_advance_budget_pair_v01(
    state: dict[str, object],
    *,
    cell_input: object,
    event: str,
    transition_decision: TransitionDecisionV01,
    budget_state: str = "ACTIVE",
) -> tuple[object, object]:
    cell_budget, global_budget = _g2e4_live_budget_heads_v01(
        state, cell_input.cell_id
    )
    budget_by_id = _g2e4_budget_by_id_v01(state)
    allocation_parent = (
        None
        if cell_budget.allocation_parent_budget_id is None
        else budget_by_id.get(cell_budget.allocation_parent_budget_id)
    )
    if (
        cell_budget.allocation_parent_budget_id is not None
        and allocation_parent is None
    ):
        raise ValueError("g2d_budget_predecessor_invalid")
    next_cell = _g2e4_build_budget_successor_v01(
        state,
        cell_budget,
        event=event,
        transition_decision=transition_decision,
        cell_input=cell_input,
        budget_state=budget_state,
        allocation_parent=allocation_parent,
        owning_cell_id=cell_input.cell_id,
        budget_scope=cell_budget.budget_scope,
    )
    next_global = (
        next_cell
        if cell_input.parent_cell_id is None
        else _g2e4_build_budget_successor_v01(
            state,
            global_budget,
            event=event,
            transition_decision=transition_decision,
            cell_input=cell_input,
            paired_cell_budget=next_cell,
        )
    )
    _g2e4_append_budget_pair_v01(state, next_cell, next_global)
    return next_cell, next_global


def _g2e4_ready_and_start_node_v01(
    state: dict[str, object],
    *,
    initial: object,
    node: object,
    cell_input: object,
    dependencies: tuple[object, ...],
) -> tuple[object, KernelArtifactV01]:
    artifact_by_queue = _g2e4_artifact_by_queue_id_v01(state)
    budget_by_id = _g2e4_budget_by_id_v01(state)
    initial_artifact = artifact_by_queue[initial.queue_entry_id]
    cell_anchor = budget_by_id[initial.cell_budget_id]
    global_anchor = budget_by_id[initial.global_budget_id]
    ready_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=initial_artifact,
        node=node,
        current_entry=initial,
        cell_input=cell_input,
        cell_budget=cell_anchor,
        global_budget=global_anchor,
        dependencies=dependencies,
    )
    ready, ready_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=initial,
        current_artifact=initial_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=ready_decision,
        cell_budget_after=cell_anchor,
        global_budget_after=global_anchor,
        dependencies=dependencies,
    )
    start_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=ready_artifact,
        node=node,
        current_entry=ready,
        cell_input=cell_input,
        cell_budget=cell_anchor,
        global_budget=global_anchor,
        dependencies=dependencies,
    )
    start_cell, start_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=cell_input,
        event="START_NODE",
        transition_decision=start_decision,
    )
    return _g2e4_append_queue_target_v01(
        state,
        current_entry=ready,
        current_artifact=ready_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=start_decision,
        cell_budget_after=start_cell,
        global_budget_after=start_global,
        dependencies=dependencies,
    )


def _g2e4_local_observation_v01(
    state: dict[str, object],
    *,
    node: object,
    cell_input: object,
    cell_budget: object,
    global_budget: object,
    dependencies: tuple[object, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    assignment = next(
        item for item in state["runtime_assignments"] if item.node_id == node.node_id
    )
    artifact_by_queue = _g2e4_artifact_by_queue_id_v01(state)
    evidence = (
        tuple(
            artifact_by_queue[item.queue_entry_id].artifact_id
            for item in dependencies
        )
        if dependencies
        else cell_input.evidence_refs
    )
    core = {
        "profile_version": "v0.3.1",
        "topology_id": state["topology"].topology_id,
        "topology_seed_id": state["topology"].topology_seed_id,
        "source_binding_id": state["topology"].source_binding_id,
        "request_id": state["topology"].request_id,
        "transaction_id": state["topology"].transaction_id,
        "owning_root_id": state["topology"].owning_root_id,
        "source_time_envelope_ref": state["topology"].time_envelope_ref,
        "node_id": node.node_id,
        "assignment_id": assignment.assignment_id,
        "node_kind": node.node_kind,
        "expected_output_kind": node.expected_output_kind,
        "cell_input_id": cell_input.cell_input_id,
        "cell_input_evidence_refs": list(cell_input.evidence_refs),
        "cell_id": cell_input.cell_id,
        "parent_cell_id": cell_input.parent_cell_id,
        "scope_ref": cell_input.scope_ref,
        "cell_budget_before_id": cell_budget.budget_id,
        "global_budget_before_id": global_budget.budget_id,
        "dependency_queue_entry_ids": [item.queue_entry_id for item in dependencies],
        "dependency_queue_artifact_ids": [
            artifact_by_queue[item.queue_entry_id].artifact_id
            for item in dependencies
        ],
        "dependency_states": [item.state for item in dependencies],
        "dependency_reason_tuples": [
            list(item.queue_reason_codes) for item in dependencies
        ],
        "dependency_output_tuples": [
            list(item.observed_output_refs) for item in dependencies
        ],
        "dependency_evidence_tuples": [
            list(item.observed_evidence_refs) for item in dependencies
        ],
        "dependency_advisory_tuples": [
            list(item.advisory_refs) for item in dependencies
        ],
        "provider_calls": 0,
        "model_calls": 0,
        "network_calls": 0,
        "connector_calls": 0,
        "external_drs_calls": 0,
        "authority_created": False,
        "permission_created": False,
        "final_output_created": False,
        "drs_write_created": False,
        "real_world_effects_count": 0,
    }
    output = "d3local:output:" + domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_D3_LOCAL_OBSERVATION_MATERIAL",
        payload=canonical_json_bytes_v01(core),
    )
    return (output,), evidence


def _g2e4_complete_local_node_v01(
    state: dict[str, object],
    *,
    initial: object,
    node: object,
    cell_input: object,
) -> tuple[object, KernelArtifactV01]:
    dependencies = _g2e4_dependencies_v01(state, initial)
    running, running_artifact = _g2e4_ready_and_start_node_v01(
        state,
        initial=initial,
        node=node,
        cell_input=cell_input,
        dependencies=dependencies,
    )
    budget_by_id = _g2e4_budget_by_id_v01(state)
    running_cell = budget_by_id[running.cell_budget_id]
    running_global = budget_by_id[running.global_budget_id]
    outputs, evidence = _g2e4_local_observation_v01(
        state,
        node=node,
        cell_input=cell_input,
        cell_budget=running_cell,
        global_budget=running_global,
        dependencies=dependencies,
    )
    finish_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=cell_input,
        cell_budget=running_cell,
        global_budget=running_global,
        dependencies=dependencies,
        observed_output_refs=outputs,
        observed_evidence_refs=evidence,
    )
    finish_cell, finish_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=cell_input,
        event="FINISH_NODE",
        transition_decision=finish_decision,
    )
    validating, validating_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=finish_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=outputs,
        observed_evidence_refs=evidence,
    )
    terminal_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=validating_artifact,
        node=node,
        current_entry=validating,
        cell_input=cell_input,
        cell_budget=finish_cell,
        global_budget=finish_global,
        dependencies=dependencies,
        observed_output_refs=outputs,
        observed_evidence_refs=evidence,
    )
    return _g2e4_append_queue_target_v01(
        state,
        current_entry=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=terminal_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=outputs,
        observed_evidence_refs=evidence,
    )


def _g2e4_finish_report_node_v01(
    state: dict[str, object],
    *,
    initial: object,
    node: object,
    cell_input: object,
    validation_report: object,
    observed_output_ref: str,
    observed_evidence_ref: str,
) -> tuple[object, KernelArtifactV01]:
    dependencies = _g2e4_dependencies_v01(state, initial)
    running, running_artifact = _g2e4_ready_and_start_node_v01(
        state,
        initial=initial,
        node=node,
        cell_input=cell_input,
        dependencies=dependencies,
    )
    budget_by_id = _g2e4_budget_by_id_v01(state)
    running_cell = budget_by_id[running.cell_budget_id]
    running_global = budget_by_id[running.global_budget_id]
    finish_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=cell_input,
        cell_budget=running_cell,
        global_budget=running_global,
        dependencies=dependencies,
        observed_output_refs=(observed_output_ref,),
        observed_evidence_refs=(observed_evidence_ref,),
        validation_report=validation_report,
    )
    finish_cell, finish_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=cell_input,
        event="FINISH_NODE",
        transition_decision=finish_decision,
    )
    validating, validating_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=finish_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=(observed_output_ref,),
        observed_evidence_refs=(observed_evidence_ref,),
    )
    terminal_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=validating_artifact,
        node=node,
        current_entry=validating,
        cell_input=cell_input,
        cell_budget=finish_cell,
        global_budget=finish_global,
        dependencies=dependencies,
        observed_output_refs=(observed_output_ref,),
        observed_evidence_refs=(observed_evidence_ref,),
        validation_report=validation_report,
    )
    return _g2e4_append_queue_target_v01(
        state,
        current_entry=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=terminal_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=(observed_output_ref,),
        observed_evidence_refs=(observed_evidence_ref,),
    )


def _g2e4_finish_parent_slot_v01(
    state: dict[str, object],
    *,
    running: object,
    running_artifact: KernelArtifactV01,
    node: object,
    parent_input: object,
    dependencies: tuple[object, ...],
    child_result: object,
    child_result_artifact: KernelArtifactV01,
) -> tuple[object, KernelArtifactV01]:
    budget_by_id = _g2e4_budget_by_id_v01(state)
    running_cell = budget_by_id[running.cell_budget_id]
    running_global = budget_by_id[running.global_budget_id]
    finish_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=parent_input,
        cell_budget=running_cell,
        global_budget=running_global,
        dependencies=dependencies,
        queue_reason_codes=child_result.reason_codes,
        observed_output_refs=(child_result_artifact.artifact_id,),
        observed_evidence_refs=child_result.evidence_refs,
        advisory_refs=(
            child_result.post_vv_report_ref,
            child_result.gt_advisory_ref,
        ),
        local_child_result=child_result,
        local_child_result_artifact=child_result_artifact,
    )
    finish_cell, finish_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=parent_input,
        event="FINISH_NODE",
        transition_decision=finish_decision,
    )
    validating, validating_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=parent_input,
        transition_decision=finish_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        queue_reason_codes=child_result.reason_codes,
        observed_output_refs=(child_result_artifact.artifact_id,),
        observed_evidence_refs=child_result.evidence_refs,
        advisory_refs=(
            child_result.post_vv_report_ref,
            child_result.gt_advisory_ref,
        ),
        local_child_result=child_result,
        local_child_result_artifact=child_result_artifact,
    )
    terminal_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=validating_artifact,
        node=node,
        current_entry=validating,
        cell_input=parent_input,
        cell_budget=finish_cell,
        global_budget=finish_global,
        dependencies=dependencies,
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
        local_child_result=child_result,
        local_child_result_artifact=child_result_artifact,
    )
    return _g2e4_append_queue_target_v01(
        state,
        current_entry=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=parent_input,
        transition_decision=terminal_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
        local_child_result=child_result,
        local_child_result_artifact=child_result_artifact,
    )


def _g2e4_finish_parent_return_v01(
    state: dict[str, object],
    *,
    initial: object,
    node: object,
    cell_input: object,
    pre_terminals: tuple[object, ...],
    child_results: tuple[object, ...],
    partial_failures: tuple[object, ...],
    proposal: dict[str, object],
    post_vv_report: dict[str, object],
    gt_advisory_report: dict[str, object],
    validation_reports: tuple[object, ...],
) -> tuple[object, KernelArtifactV01, object, object]:
    dependencies = _g2e4_dependencies_v01(state, initial)
    running, running_artifact = _g2e4_ready_and_start_node_v01(
        state,
        initial=initial,
        node=node,
        cell_input=cell_input,
        dependencies=dependencies,
    )
    proposal_evidence = proposal.get("evidence")
    if type(proposal_evidence) is not list:
        raise ValueError("g2d_parent_return_invalid")
    evidence = tuple(item["ref_id"] for item in proposal_evidence)
    family = {
        "pre_post_vv_terminal_queue_entries": pre_terminals,
        "child_results": child_results,
        "partial_failures": partial_failures,
        "result_proposal": proposal,
        "post_vv_report": post_vv_report,
        "gt_advisory_report": gt_advisory_report,
        "validation_reports": validation_reports,
    }
    budget_by_id = _g2e4_budget_by_id_v01(state)
    running_cell = budget_by_id[running.cell_budget_id]
    running_global = budget_by_id[running.global_budget_id]
    finish_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=cell_input,
        cell_budget=running_cell,
        global_budget=running_global,
        dependencies=dependencies,
        observed_output_refs=(proposal["proposal_id"],),
        observed_evidence_refs=evidence,
        advisory_refs=(
            post_vv_report["vv_report_id"],
            gt_advisory_report["gt_report_id"],
        ),
        parent_return_family=family,
    )
    finish_cell, finish_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=cell_input,
        event="FINISH_NODE",
        transition_decision=finish_decision,
    )
    validating, validating_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=finish_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=(proposal["proposal_id"],),
        observed_evidence_refs=evidence,
        advisory_refs=(
            post_vv_report["vv_report_id"],
            gt_advisory_report["gt_report_id"],
        ),
    )
    terminal_decision = _g2e4_evaluate_queue_transition_v01(
        state,
        source_artifact=validating_artifact,
        node=node,
        current_entry=validating,
        cell_input=cell_input,
        cell_budget=finish_cell,
        global_budget=finish_global,
        dependencies=dependencies,
        observed_output_refs=(proposal["proposal_id"],),
        observed_evidence_refs=evidence,
        advisory_refs=(
            post_vv_report["vv_report_id"],
            gt_advisory_report["gt_report_id"],
        ),
        parent_return_family=family,
    )
    terminal, terminal_artifact = _g2e4_append_queue_target_v01(
        state,
        current_entry=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        transition_decision=terminal_decision,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=(proposal["proposal_id"],),
        observed_evidence_refs=evidence,
        advisory_refs=(
            post_vv_report["vv_report_id"],
            gt_advisory_report["gt_report_id"],
        ),
    )
    final_cell, final_global = _g2e4_advance_budget_pair_v01(
        state,
        cell_input=cell_input,
        event="FINALIZE",
        transition_decision=terminal_decision,
        budget_state="FINAL",
    )
    return terminal, terminal_artifact, final_cell, final_global


def _g2e4_result_material_v01(
    *,
    cell_input: object,
    pre_terminals: tuple[object, ...],
    child_results: tuple[object, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if any(item.state != "COMPLETED" for item in pre_terminals) or any(
        item.outcome != "COMPLETED" for item in child_results
    ):
        raise ValueError("g2d_result_proposal_invalid")
    outputs = _ordered_unique_v01(
        tuple(
            ref
            for item in (*pre_terminals, *child_results)
            for ref in (
                item.observed_output_refs
                if hasattr(item, "observed_output_refs")
                else item.accepted_output_refs
            )
        )
    )
    evidence = _ordered_unique_v01(
        (
            *(ref for item in pre_terminals for ref in item.observed_evidence_refs),
            *(ref for item in child_results for ref in item.evidence_refs),
        )
    )
    if cell_input.parent_cell_id is not None:
        activation_parent_id = pre_terminals[0].lineage_refs[7]
        positions = tuple(
            index for index, item in enumerate(evidence) if item == activation_parent_id
        )
        if len(positions) != 1:
            raise ValueError("g2d_result_proposal_invalid")
        position = positions[0]
        evidence = evidence[:position] + evidence[position + 1 :]
    elif child_results and any(
        cell_input.cell_input_id in item.evidence_refs for item in child_results
    ):
        positions = tuple(
            index
            for index, item in enumerate(evidence)
            if item == cell_input.cell_input_id
        )
        if len(positions) != 1:
            raise ValueError("g2d_result_proposal_invalid")
        position = positions[0]
        evidence = evidence[:position] + evidence[position + 1 :]
    if not outputs or not evidence:
        raise ValueError("g2d_result_proposal_invalid")
    return outputs, evidence


def _g2e4_finalize_cell_v01(
    state: dict[str, object],
    *,
    cell_input: object,
    nodes: tuple[object, ...],
    allocated_budget: object,
    child_results: tuple[object, ...],
) -> dict[str, object]:
    initial_by_node = {
        item.node_id: item
        for item in state["queue_entries"]
        if item.queue_entry_id in cell_input.ordered_initial_queue_entry_ids
    }
    if tuple(initial_by_node) != cell_input.ordered_node_ids:
        raise ValueError("g2d_cell_input_invalid")
    post_index = next(
        index for index, node in enumerate(nodes) if node.node_kind == "POST_VV"
    )
    terminal_states = {"COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND"}
    for node in nodes[:post_index]:
        latest = {
            (item.cell_id, item.node_id): item
            for item in _g2e4_latest_queue_entries_v01(state)
        }[(cell_input.cell_id, node.node_id)]
        if latest.state in terminal_states:
            continue
        if node.node_kind not in {
            "SEMANTIC_ACTOR",
            "MEMORY_CONTEXT",
            "FRACTAL_MERGE",
        }:
            raise ValueError("g2d_topology_node_invalid")
        _g2e4_complete_local_node_v01(
            state,
            initial=initial_by_node[node.node_id],
            node=node,
            cell_input=cell_input,
        )
    latest = {
        (item.cell_id, item.node_id): item
        for item in _g2e4_latest_queue_entries_v01(state)
    }
    pre_terminals = tuple(
        latest[(cell_input.cell_id, node.node_id)] for node in nodes[:post_index]
    )
    accepted_outputs, evidence_refs = _g2e4_result_material_v01(
        cell_input=cell_input,
        pre_terminals=pre_terminals,
        child_results=child_results,
    )
    proposal = g2d_runtime.build_fractal_cell_result_proposal_v02(
        source_context=state["source_context"],
        topology=state["topology"],
        cell_input=cell_input,
        pre_post_vv_terminal_queue_entries=pre_terminals,
        child_results=child_results,
        partial_failures=(),
        accepted_output_refs=accepted_outputs,
        evidence_refs=evidence_refs,
    )
    proposal_report = g2d_runtime.validate_fractal_cell_result_proposal_v02(
        proposal,
        source_context=state["source_context"],
        topology=state["topology"],
        cell_input=cell_input,
        pre_post_vv_terminal_queue_entries=pre_terminals,
        child_results=child_results,
        partial_failures=(),
    )
    source_time = (
        state["source_context"].router_input.local_routing_snapshot.kt_asof_utc
    )
    post_vv_report = validate_result_proposal(proposal, checked_at=source_time)
    post_report = g2d_runtime.validate_fractal_post_vv_report_v02(
        post_vv_report,
        result_proposal=proposal,
        source_context=state["source_context"],
    )
    gt_advisory_report = validate_gt([post_vv_report], created_at=source_time)
    gt_report = g2d_runtime.validate_fractal_gt_advisory_v02(
        gt_advisory_report,
        post_vv_report=post_vv_report,
        source_context=state["source_context"],
    )
    transient_reports = (proposal_report, post_report, gt_report)
    if any(item.status != "PASS" for item in transient_reports):
        first = next(item for item in transient_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    node_by_kind = {item.node_kind: item for item in nodes}
    _g2e4_finish_report_node_v01(
        state,
        initial=initial_by_node[node_by_kind["POST_VV"].node_id],
        node=node_by_kind["POST_VV"],
        cell_input=cell_input,
        validation_report=post_report,
        observed_output_ref=post_vv_report["vv_report_id"],
        observed_evidence_ref=proposal["proposal_id"],
    )
    _g2e4_finish_report_node_v01(
        state,
        initial=initial_by_node[node_by_kind["GT_ADVISORY"].node_id],
        node=node_by_kind["GT_ADVISORY"],
        cell_input=cell_input,
        validation_report=gt_report,
        observed_output_ref=gt_advisory_report["gt_report_id"],
        observed_evidence_ref=post_vv_report["vv_report_id"],
    )
    _parent_terminal, _parent_artifact, final_cell, final_global = (
        _g2e4_finish_parent_return_v01(
            state,
            initial=initial_by_node[node_by_kind["PARENT_RETURN"].node_id],
            node=node_by_kind["PARENT_RETURN"],
            cell_input=cell_input,
            pre_terminals=pre_terminals,
            child_results=child_results,
            partial_failures=(),
            proposal=proposal,
            post_vv_report=post_vv_report,
            gt_advisory_report=gt_advisory_report,
            validation_reports=transient_reports,
        )
    )
    latest = {
        (item.cell_id, item.node_id): item
        for item in _g2e4_latest_queue_entries_v01(state)
    }
    terminal_entries = tuple(
        latest[(cell_input.cell_id, node.node_id)] for node in nodes
    )
    artifact_by_queue = _g2e4_artifact_by_queue_id_v01(state)
    terminal_artifacts = tuple(
        artifact_by_queue[item.queue_entry_id] for item in terminal_entries
    )
    pre_result_report = g2d_runtime.validate_fractal_cell_result_against_input_v02(
        source_context=state["source_context"],
        topology=state["topology"],
        cell_input=cell_input,
        terminal_queue_entries=terminal_entries,
        child_results=child_results,
        partial_failures=(),
        result_proposal=proposal,
        post_vv_report=post_vv_report,
        gt_advisory_report=gt_advisory_report,
        cell_budget=final_cell,
        global_budget=final_global,
    )
    if pre_result_report.status != "PASS":
        raise ValueError(pre_result_report.reason_codes[0])
    result = g2d_runtime.build_fractal_cell_result_v02(
        state["topology"],
        cell_input,
        terminal_entries,
        child_results,
        accepted_output_refs=accepted_outputs,
        evidence_refs=evidence_refs,
        pre_result_validation_report=pre_result_report,
        post_vv_report=post_vv_report,
        gt_advisory_report=gt_advisory_report,
        partial_failures=(),
        allocated_cell_budget=allocated_budget,
        final_cell_budget=final_cell,
        global_budget=final_global,
    )
    result_artifact_by_id = {
        item.result_id: artifact
        for item, artifact in zip(
            state["cell_results"], state["result_artifacts"], strict=True
        )
    }
    child_result_artifacts = tuple(
        result_artifact_by_id[item.result_id] for item in child_results
    )
    result_artifact = g2d_runtime.project_fractal_cell_result_kernel_artifact_v02(
        result,
        topology_artifact=state["topology_artifact"],
        terminal_queue_artifacts=terminal_artifacts,
        child_result_artifacts=child_result_artifacts,
        source_context=state["source_context"],
    )
    state["cell_results"] = (*state["cell_results"], result)
    state["result_artifacts"] = (*state["result_artifacts"], result_artifact)
    state["runtime_artifacts"] = (*state["runtime_artifacts"], result_artifact)
    state["result_proposals"] = (*state["result_proposals"], proposal)
    state["post_vv_reports"] = (*state["post_vv_reports"], post_vv_report)
    state["gt_advisory_reports"] = (
        *state["gt_advisory_reports"],
        gt_advisory_report,
    )
    state["pre_result_reports"] = (
        *state["pre_result_reports"],
        pre_result_report,
    )
    return {
        "result": result,
        "result_artifact": result_artifact,
        "final_cell_budget": final_cell,
        "completion_global_budget": final_global,
    }


def _g2e4_observed_work_context_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    execution_scope: str,
    whole_run_escalation_reason: str | None = None,
    whole_run_escalation_policy_id: str | None = None,
) -> object:
    baseline = source_context.baseline_g2d_execution_bundle
    source_by_id = {
        item.artifact_id: item
        for item in (
            *source_context.baseline_source_artifacts,
            *source_context.observed_source_artifacts,
        )
    }
    pointer_by_binding: dict[str, tuple[str, ...]] = {}
    for binding in changed_field_bindings:
        pointer_by_binding.setdefault(binding.source_binding_id, ())
        pointer_by_binding[binding.source_binding_id] = (
            *pointer_by_binding[binding.source_binding_id],
            binding.json_pointer,
        )
    artifact_binding_by_source = {
        item.source_binding_id: item for item in changed_artifact_bindings
    }
    if len(artifact_binding_by_source) != len(changed_artifact_bindings):
        raise ValueError("g2e_delta_binding_set_mismatch")
    selected_node_ids = set(plan.ordered_work_node_ids)
    selected_targets = {
        edge.target_node_id
        for edge in baseline.topology_edges
        if edge.source_node_id in selected_node_ids
        and edge.target_node_id in selected_node_ids
    }
    direct_node_ids = tuple(
        node_id
        for node_id in plan.ordered_work_node_ids
        if node_id not in selected_targets
    )
    if not direct_node_ids:
        raise ValueError("g2e_topology_binding_mismatch")
    ledger = _g2e4_baseline_runtime_artifact_ledger_v01(baseline)
    plan_source_by_id = {
        item.artifact_id: item
        for item in source_context.baseline_source_artifacts
    }
    selected_rows = tuple(
        row
        for item in plan.ordered_affected_artifact_ids
        for row in (
            _g2e4_resolve_runtime_artifact_projection_v01(
                source_artifact=plan_source_by_id[item],
                ledger=ledger,
            ),
        )
        if row is not None
        and row["ownership_class"] == "CELL_QUEUE"
        and row["queue_entry"].predecessor_queue_entry_id is None
    )
    if len(selected_rows) != 1:
        raise ValueError("g2e_topology_binding_mismatch")
    selected_cell_id = selected_rows[0]["cell_input"].cell_id
    if selected_cell_id not in plan.ordered_affected_cell_ids:
        raise ValueError("g2e_topology_binding_mismatch")
    selected_cell_input = next(
        (
            item
            for item in baseline.cell_inputs
            if item.cell_id == selected_cell_id
        ),
        None,
    )
    if selected_cell_input is None:
        raise ValueError("g2e_topology_binding_mismatch")
    binding_artifacts: list[KernelArtifactV01] = []
    for node_id in direct_node_ids:
        node = next(item for item in baseline.topology_nodes if item.node_id == node_id)
        if node_id not in selected_cell_input.ordered_node_ids:
            raise ValueError("g2e_topology_binding_mismatch")
        for source_binding in source_bindings:
            baseline_source_artifact = source_by_id[
                source_binding.baseline_source_artifact_id
            ]
            observed_source_artifact = source_by_id[
                source_binding.observed_source_artifact_id
            ]
            changed_artifact = artifact_binding_by_source.get(
                source_binding.source_binding_id
            )
            if changed_artifact is not None:
                if (
                    changed_artifact.baseline_artifact_id
                    != source_binding.baseline_source_artifact_id
                    or changed_artifact.observed_artifact_id
                    != source_binding.observed_source_artifact_id
                ):
                    raise ValueError("g2e_delta_artifact_binding_invalid")
                pointers = ("",)
            else:
                pointers = pointer_by_binding.get(
                    source_binding.source_binding_id, ()
                )
            if not pointers:
                raise ValueError("g2e_changed_field_set_mismatch")
            provisional_binding = (
                g2d_runtime.project_runtime_observed_work_binding_kernel_artifact_v02(
                    baseline_execution_bundle=baseline,
                    node=node,
                    cell_input=selected_cell_input,
                    baseline_source_artifact=baseline_source_artifact,
                    observed_source_artifact=observed_source_artifact,
                    changed_full_artifact_pointers=pointers,
                    execution_scope=execution_scope,
                    whole_run_escalation_reason=whole_run_escalation_reason,
                    whole_run_escalation_policy_id=whole_run_escalation_policy_id,
                )
            )
            provisional_payload = kernel_artifact_to_plain_dict_v01(
                provisional_binding
            )["payload"]
            provisional_change_proof = provisional_payload.get("change_proof")
            if type(provisional_change_proof) is not dict:
                raise ValueError("g2e_topology_binding_mismatch")
            canonical_pointers_value = provisional_change_proof.get(
                "all_full_artifact_changed_pointers"
            )
            if (
                type(canonical_pointers_value) is not list
                or not canonical_pointers_value
                or any(type(item) is not str for item in canonical_pointers_value)
            ):
                raise ValueError("g2e_topology_binding_mismatch")
            binding_artifacts.append(
                g2d_runtime.project_runtime_observed_work_binding_kernel_artifact_v02(
                    baseline_execution_bundle=baseline,
                    node=node,
                    cell_input=selected_cell_input,
                    baseline_source_artifact=baseline_source_artifact,
                    observed_source_artifact=observed_source_artifact,
                    changed_full_artifact_pointers=tuple(
                        canonical_pointers_value
                    ),
                    execution_scope=execution_scope,
                    whole_run_escalation_reason=whole_run_escalation_reason,
                    whole_run_escalation_policy_id=whole_run_escalation_policy_id,
                )
            )
    direct_sources = tuple(
        source_by_id[item]
        for binding in source_bindings
        for item in (
            binding.baseline_source_artifact_id,
            binding.observed_source_artifact_id,
        )
    )
    context = g2d_runtime.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=direct_sources,
        supporting_artifacts=(),
        binding_artifacts=tuple(binding_artifacts),
        execution_scope=execution_scope,
        whole_run_escalation_reason=whole_run_escalation_reason,
        whole_run_escalation_policy_id=whole_run_escalation_policy_id,
    )
    reports = (
        g2d_runtime.validate_runtime_observed_work_context_v02(context),
        g2d_runtime.validate_runtime_observed_work_context_against_sources_v02(
            context,
            baseline_execution_bundle=baseline,
            direct_source_artifacts=direct_sources,
            supporting_artifacts=(),
            binding_artifacts=tuple(binding_artifacts),
        ),
    )
    if any(item.status != "PASS" for item in reports):
        first = next(item for item in reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    return context


def _g2e4_selective_prefix_state_v01(
    *,
    baseline: FractalRuntimeExecutionBundleV02,
    plan: SelectiveRecomputationPlanV01,
    observed_context: object,
    transition_registry: object,
    required_reports: tuple[object, ...],
) -> dict[str, object]:
    selected_input = next(
        item
        for item in baseline.cell_inputs
        if item.cell_id == plan.ordered_affected_cell_ids[0]
    )
    root_input = next(item for item in baseline.cell_inputs if item.parent_cell_id is None)
    sibling_inputs = tuple(
        item
        for item in baseline.cell_inputs
        if item.parent_cell_id is not None and item.cell_id != selected_input.cell_id
    )
    if len(sibling_inputs) != 1:
        raise ValueError("g2e_topology_binding_mismatch")
    sibling_input = sibling_inputs[0]
    queue_pairs = tuple(
        zip(baseline.queue_entries, baseline.queue_artifacts, strict=True)
    )
    selected_initial_pair = next(
        pair
        for pair in queue_pairs
        if pair[0].queue_entry_id
        == selected_input.ordered_initial_queue_entry_ids[0]
    )
    if len(selected_initial_pair[1].parent_refs) < 2:
        raise ValueError("g2e_topology_binding_mismatch")
    activation_artifact_id = selected_initial_pair[1].parent_refs[1]
    activation_index = next(
        index
        for index, pair in enumerate(queue_pairs)
        if pair[1].artifact_id == activation_artifact_id
    )
    activation_entry, activation_artifact = queue_pairs[activation_index]
    activation_node = next(
        item
        for item in baseline.topology_nodes
        if item.node_id == activation_entry.node_id
    )
    if (
        activation_entry.cell_id != root_input.cell_id
        or activation_entry.state != "RUNNING"
        or activation_entry.planned_child_cell_id != selected_input.cell_id
        or activation_node.node_kind != "FRACTAL_CELL"
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    queue_entries = baseline.queue_entries[: activation_index + 1]
    queue_artifacts = baseline.queue_artifacts[: activation_index + 1]
    budget_index = next(
        index
        for index, item in enumerate(baseline.budgets)
        if item.budget_id == activation_entry.global_budget_id
    )
    budgets = baseline.budgets[: budget_index + 1]
    budget_ids = {item.budget_id for item in budgets}
    if any(
        item.cell_budget_id not in budget_ids or item.global_budget_id not in budget_ids
        for item in queue_entries
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    cell_inputs = tuple(
        item
        for item in baseline.cell_inputs
        if item.cell_id in {root_input.cell_id, sibling_input.cell_id}
    )
    scope_projections = tuple(
        item
        for item in baseline.scope_projections
        if item.child_cell_id == sibling_input.cell_id
    )
    if cell_inputs != (root_input, sibling_input) or len(scope_projections) != 1:
        raise ValueError("g2e_topology_binding_mismatch")
    sibling_result_index = next(
        index
        for index, item in enumerate(baseline.cell_results)
        if item.cell_id == sibling_input.cell_id
    )
    cell_results = (baseline.cell_results[sibling_result_index],)
    result_artifacts = (baseline.result_artifacts[sibling_result_index],)
    result_proposals = (baseline.result_proposals[sibling_result_index],)
    post_vv_reports = (baseline.post_vv_reports[sibling_result_index],)
    gt_advisory_reports = (baseline.gt_advisory_reports[sibling_result_index],)
    proposal_id = result_proposals[0]["proposal_id"]
    pre_result_reports = tuple(
        item
        for item in baseline.validation_reports
        if item.validation_target == "CELL_RESULT_PRECONDITIONS"
        and item.validated_object_id == proposal_id
    )
    if len(pre_result_reports) != 1:
        raise ValueError("g2e_topology_binding_mismatch")
    scope_ids = {item.projection_id for item in scope_projections}
    input_ids = {item.cell_input_id for item in cell_inputs}
    scope_reports = tuple(
        item
        for item in baseline.validation_reports
        if item.validation_target == "SCOPE_PROJECTION_AGAINST_SOURCES"
        and item.validated_object_id in scope_ids
    )
    input_reports = tuple(
        item
        for item in baseline.validation_reports
        if item.validation_target == "CELL_INPUT_AGAINST_SOURCES"
        and item.validated_object_id in input_ids
    )
    if len(scope_reports) != 1 or len(input_reports) != 2:
        raise ValueError("g2e_topology_binding_mismatch")
    trace_artifact_refs = baseline.runtime_trace.abi_artifact_refs
    topology_artifact_id = baseline.topology_artifact.artifact_id
    if (
        not trace_artifact_refs
        or trace_artifact_refs[0] != topology_artifact_id
        or trace_artifact_refs.count(topology_artifact_id) != 1
        or trace_artifact_refs.count(activation_artifact_id) != 1
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    activation_runtime_index = trace_artifact_refs.index(activation_artifact_id)
    if activation_runtime_index < 1:
        raise ValueError("g2e_topology_binding_mismatch")
    runtime_artifact_ids = trace_artifact_refs[
        1 : activation_runtime_index + 1
    ]
    artifact_by_id = {
        item.artifact_id: item
        for item in (*baseline.queue_artifacts, *baseline.result_artifacts)
    }
    if (
        topology_artifact_id in artifact_by_id
        or any(item not in artifact_by_id for item in runtime_artifact_ids)
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    runtime_artifacts = tuple(
        artifact_by_id[item] for item in runtime_artifact_ids
    )
    state: dict[str, object] = {
        "source_context": baseline.source_context,
        "observed_work_context": observed_context,
        "topology": baseline.topology,
        "transition_registry": transition_registry,
        "topology_transition": baseline.transition_decisions[0],
        "topology_artifact": baseline.topology_artifact,
        "source_binding": baseline.source_binding,
        "topology_seed": baseline.topology_seed,
        "topology_nodes": baseline.topology_nodes,
        "topology_edges": baseline.topology_edges,
        "runtime_assignments": baseline.runtime_assignments,
        "base_reports": required_reports,
        "scope_reports": scope_reports,
        "input_reports": input_reports,
        "prefix_reports": (),
        "budgets": budgets,
        "queue_entries": queue_entries,
        "queue_artifacts": queue_artifacts,
        "runtime_artifacts": runtime_artifacts,
        "queue_decisions": baseline.transition_decisions[1 : 1 + len(queue_entries)],
        "cell_inputs": cell_inputs,
        "scope_projections": scope_projections,
        "revise_observations": (),
        "partial_failures": (),
        "backpressure_states": (),
        "cell_results": cell_results,
        "result_artifacts": result_artifacts,
        "result_proposals": result_proposals,
        "post_vv_reports": post_vv_reports,
        "gt_advisory_reports": gt_advisory_reports,
        "pre_result_reports": pre_result_reports,
        "selected_baseline_input": selected_input,
        "sibling_input": sibling_input,
        "root_input": root_input,
        "activation_entry": activation_entry,
        "activation_artifact": activation_artifact,
        "activation_node": activation_node,
    }
    _g2e4_refresh_prefix_reports_v01(state)
    return state


def _g2e4_activate_selected_child_v01(
    state: dict[str, object],
) -> dict[str, object]:
    source = state["source_context"]
    topology = state["topology"]
    parent_input = state["root_input"]
    selected_baseline_input = state["selected_baseline_input"]
    slot_running = state["activation_entry"]
    slot_artifact = state["activation_artifact"]
    canonical_child_index = parent_input.ordered_planned_child_cell_ids.index(
        selected_baseline_input.cell_id
    )
    budget_by_id = _g2e4_budget_by_id_v01(state)
    allocation_parent = budget_by_id[parent_input.cell_budget_id]
    _parent_budget, live_global = _g2e4_live_budget_heads_v01(
        state, parent_input.cell_id
    )
    queue_by_id = {item.queue_entry_id: item for item in state["queue_entries"]}
    allocation_queues = tuple(
        queue_by_id[item] for item in parent_input.ordered_initial_queue_entry_ids
    )
    child_allocated = g2d_runtime.build_fractal_runtime_budget_v02(
        policy=source.runtime_policy,
        topology_seed=state["topology_seed"],
        allocation_parent_budget=allocation_parent,
        predecessor_budget=None,
        owning_cell_id=selected_baseline_input.cell_id,
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queues,
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    projection = g2d_runtime.project_parent_child_scope_v02(
        source_context=source,
        topology=topology,
        parent_input=parent_input,
        child_cell_id=selected_baseline_input.cell_id,
        child_scope_ref=topology.accepted_scope_ref,
        parent_budget=allocation_parent,
        child_budget=child_allocated,
        global_budget=live_global,
    )
    child_active = _g2e4_build_budget_successor_v01(
        state,
        child_allocated,
        event="ACTIVATE",
        cell_input=parent_input,
        allocation_parent=allocation_parent,
        owning_cell_id=selected_baseline_input.cell_id,
        budget_scope="CHILD_CELL_LOCAL",
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queues,
    )
    global_active = _g2e4_build_budget_successor_v01(
        state,
        live_global,
        event="ACTIVATE",
        cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queues,
        paired_cell_budget=child_active,
    )
    child_create = _g2e4_build_budget_successor_v01(
        state,
        child_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        allocation_parent=allocation_parent,
        owning_cell_id=selected_baseline_input.cell_id,
        budget_scope="CHILD_CELL_LOCAL",
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queues,
    )
    global_create = _g2e4_build_budget_successor_v01(
        state,
        global_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queues,
        paired_cell_budget=child_create,
    )
    state["budgets"] = (
        *state["budgets"],
        child_allocated,
        child_active,
        global_active,
        child_create,
        global_create,
    )
    state["scope_projections"] = (*state["scope_projections"], projection)
    scope_report = g2d_runtime.validate_parent_child_scope_against_sources_v02(
        projection,
        source_context=source,
        topology=topology,
        parent_input=parent_input,
        parent_budget=allocation_parent,
        child_budget=child_allocated,
        global_budget=live_global,
    )
    if scope_report.status != "PASS":
        raise ValueError(scope_report.reason_codes[0])
    state["scope_reports"] = (*state["scope_reports"], scope_report)
    _g2e4_refresh_prefix_reports_v01(state)
    child_nodes = tuple(
        item
        for item in state["topology_nodes"]
        if item.node_id in selected_baseline_input.ordered_node_ids
    )
    if tuple(item.node_id for item in child_nodes) != (
        selected_baseline_input.ordered_node_ids
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    admission_decisions = tuple(
        _g2e4_evaluate_queue_transition_v01(
            state,
            source_artifact=state["topology_artifact"],
            node=node,
            current_entry=None,
            cell_input=None,
            cell_budget=child_create,
            global_budget=global_create,
            cell_id=selected_baseline_input.cell_id,
            parent_cell_id=parent_input.cell_id,
            cell_depth=selected_baseline_input.cell_depth,
            scope_ref=projection.child_scope_ref,
        )
        for node in child_nodes
    )
    initial_entries = g2d_runtime.admit_runtime_execution_topology_v02(
        source_context=source,
        topology=topology,
        topology_artifact=state["topology_artifact"],
        topology_transition_decision=state["topology_transition"],
        cell_id=selected_baseline_input.cell_id,
        parent_cell_id=parent_input.cell_id,
        parent_slot_artifact=slot_artifact,
        cell_depth=selected_baseline_input.cell_depth,
        scope_ref=projection.child_scope_ref,
        cell_budget=child_create,
        global_budget=global_create,
        projected_nodes=child_nodes,
        planned_child_cell_ids=(),
        admission_decisions=admission_decisions,
        cell_instantiation_order=(
            *(item.cell_id for item in state["cell_inputs"]),
            selected_baseline_input.cell_id,
        ),
        **_g2e4_prefix_arguments_v01(state),
    )
    initial_artifacts: list[KernelArtifactV01] = []
    for entry, decision in zip(initial_entries, admission_decisions, strict=True):
        next_entries = (*state["queue_entries"], entry)
        artifact = g2d_runtime.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry,
            topology_artifact=state["topology_artifact"],
            predecessor_artifact=None,
            activation_parent_artifact=slot_artifact,
            local_child_result_artifact=None,
            source_context=source,
            **_g2e4_prefix_arguments_v01(
                state,
                settled_queue_entry_log=next_entries,
            ),
        )
        state["queue_entries"] = next_entries
        state["queue_artifacts"] = (*state["queue_artifacts"], artifact)
        state["runtime_artifacts"] = (*state["runtime_artifacts"], artifact)
        state["queue_decisions"] = (*state["queue_decisions"], decision)
        initial_artifacts.append(artifact)
        _g2e4_refresh_prefix_reports_v01(state)
    child_input = g2d_runtime.build_fractal_cell_input_from_queue_v02(
        source_context=source,
        topology=topology,
        topology_artifact=state["topology_artifact"],
        cell_id=selected_baseline_input.cell_id,
        parent_cell_id=parent_input.cell_id,
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        initial_queue_entries=initial_entries,
        initial_queue_artifacts=tuple(initial_artifacts),
        ordered_planned_child_cell_ids=(),
        **_g2e4_prefix_arguments_v01(state),
    )
    input_report = g2d_runtime.validate_fractal_cell_input_against_sources_v02(
        child_input,
        source_context=source,
        topology=topology,
        topology_artifact=state["topology_artifact"],
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        queue_entries=initial_entries,
        queue_artifacts=tuple(initial_artifacts),
        **_g2e4_prefix_arguments_v01(state),
    )
    if input_report.status != "PASS":
        raise ValueError(input_report.reason_codes[0])
    state["cell_inputs"] = (*state["cell_inputs"], child_input)
    state["input_reports"] = (*state["input_reports"], input_report)
    _g2e4_refresh_prefix_reports_v01(state)
    return {
        "cell_input": child_input,
        "nodes": child_nodes,
        "initial_entries": initial_entries,
        "allocated_budget": child_allocated,
        "canonical_child_index": canonical_child_index,
    }


def _g2e4_retired_root_only_executor_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
) -> FractalRuntimeExecutionBundleV02:
    baseline = source_context.baseline_g2d_execution_bundle
    observed_context = _g2e4_observed_work_context_v01(
        plan=plan,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        execution_scope="SELECTIVE",
    )
    source = baseline.source_context
    topology = baseline.topology
    nodes = tuple(
        item for item in baseline.topology_nodes if item.node_id in plan.ordered_work_node_ids
    )
    if (
        tuple(item.node_id for item in nodes) != plan.ordered_work_node_ids
        or observed_context.ordered_execution_node_ids
        != plan.ordered_work_node_ids
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    failure_branch_operations = (
        g2d_runtime.evaluate_fractal_revise_observation_v02,
        g2d_runtime.record_fractal_partial_failure_v02,
        g2d_runtime.evaluate_fractal_backpressure_v02,
    )
    if not all(callable(operation) for operation in failure_branch_operations):
        raise ValueError("g2e_recomputation_result_invalid")
    binding_structure_report = (
        g2d_runtime.validate_runtime_topology_source_binding_v02(
            baseline.source_binding
        )
    )
    required_reports = (
        g2d_runtime.validate_fractal_runtime_source_context_v02(source),
        g2d_runtime.validate_runtime_topology_source_binding_against_g2c_v02(
            baseline.source_binding, source_context=source
        ),
        g2d_runtime.validate_runtime_topology_seed_v02(
            baseline.topology_seed
        ),
        g2d_runtime.validate_runtime_execution_topology_against_sources_v02(
            topology, source_context=source
        ),
    )
    if binding_structure_report.status != "PASS":
        raise ValueError(binding_structure_report.reason_codes[0])
    if any(item.status != "PASS" for item in required_reports):
        first = next(item for item in required_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    topology_transition = baseline.transition_decisions[0]
    transition_registry = (
        transition_runtime.build_fractal_runtime_transition_registry_profile_v02()
    )
    if transition_runtime.validate_fractal_runtime_transition_decision_v02(
        topology_transition,
        registry=transition_registry,
        source_artifact=source.route_eligibility_artifact,
        target_artifact=baseline.topology_artifact,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    root_initial = baseline.budgets[0]
    root_input_baseline = next(
        item for item in baseline.cell_inputs if item.cell_id == topology.root_cell_id
    )
    state: dict[str, object] = {
        "source_context": source,
        "observed_work_context": observed_context,
        "topology": topology,
        "transition_registry": transition_registry,
        "topology_transition": topology_transition,
        "topology_artifact": baseline.topology_artifact,
        "source_binding": baseline.source_binding,
        "topology_seed": baseline.topology_seed,
        "topology_nodes": nodes,
        "topology_edges": baseline.topology_edges,
        "runtime_assignments": baseline.runtime_assignments,
        "base_reports": required_reports,
        "input_reports": (),
        "prefix_reports": required_reports,
        "budgets": (root_initial,),
        "queue_entries": (),
        "queue_artifacts": (),
        "runtime_artifacts": (),
        "queue_decisions": (),
        "cell_inputs": (),
        "scope_projections": (),
        "revise_observations": (),
        "partial_failures": (),
        "backpressure_states": (),
        "cell_results": (),
        "result_artifacts": (),
        "result_proposals": (),
        "post_vv_reports": (),
        "gt_advisory_reports": (),
        "pre_result_reports": (),
    }
    root_active = _g2e4_build_budget_successor_v01(
        state, root_initial, event="ACTIVATE"
    )
    state["budgets"] = (*state["budgets"], root_active)
    root_create = _g2e4_build_budget_successor_v01(
        state, root_active, event="CELL_CREATE"
    )
    state["budgets"] = (*state["budgets"], root_create)
    planned_children = root_input_baseline.ordered_planned_child_cell_ids
    admission_decisions = tuple(
        _g2e4_evaluate_queue_transition_v01(
            state,
            source_artifact=baseline.topology_artifact,
            node=node,
            current_entry=None,
            cell_input=None,
            cell_budget=root_create,
            global_budget=root_create,
        )
        for node in nodes
    )
    initial_entries = g2d_runtime.admit_runtime_execution_topology_v02(
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        topology_transition_decision=topology_transition,
        cell_id=topology.root_cell_id,
        parent_cell_id=None,
        parent_slot_artifact=None,
        cell_depth=0,
        scope_ref=topology.accepted_scope_ref,
        cell_budget=root_create,
        global_budget=root_create,
        projected_nodes=nodes,
        planned_child_cell_ids=planned_children,
        admission_decisions=admission_decisions,
        cell_instantiation_order=(topology.root_cell_id,),
        **_g2e4_prefix_arguments_v01(state),
    )
    initial_artifacts: list[KernelArtifactV01] = []
    for entry, decision in zip(initial_entries, admission_decisions, strict=True):
        next_entries = (*state["queue_entries"], entry)
        artifact = g2d_runtime.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry,
            topology_artifact=baseline.topology_artifact,
            predecessor_artifact=None,
            activation_parent_artifact=None,
            local_child_result_artifact=None,
            source_context=source,
            **_g2e4_prefix_arguments_v01(
                state, settled_queue_entry_log=next_entries
            ),
        )
        state["queue_entries"] = next_entries
        state["queue_artifacts"] = (*state["queue_artifacts"], artifact)
        state["runtime_artifacts"] = (*state["runtime_artifacts"], artifact)
        state["queue_decisions"] = (*state["queue_decisions"], decision)
        initial_artifacts.append(artifact)
        _g2e4_refresh_prefix_reports_v01(state)
    root_input = g2d_runtime.build_fractal_cell_input_from_queue_v02(
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        cell_id=topology.root_cell_id,
        parent_cell_id=None,
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=root_create,
        global_budget=root_create,
        initial_queue_entries=initial_entries,
        initial_queue_artifacts=tuple(initial_artifacts),
        ordered_planned_child_cell_ids=planned_children,
        **_g2e4_prefix_arguments_v01(state),
    )
    input_report = g2d_runtime.validate_fractal_cell_input_against_sources_v02(
        root_input,
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=root_create,
        global_budget=root_create,
        queue_entries=initial_entries,
        queue_artifacts=tuple(initial_artifacts),
        **_g2e4_prefix_arguments_v01(state),
    )
    if input_report.status != "PASS":
        raise ValueError(input_report.reason_codes[0])
    state["cell_inputs"] = (root_input,)
    state["input_reports"] = (input_report,)
    _g2e4_refresh_prefix_reports_v01(state)
    post_index = next(
        index for index, node in enumerate(nodes) if node.node_kind == "POST_VV"
    )
    initial_by_node = {item.node_id: item for item in initial_entries}
    for node in nodes[:post_index]:
        _g2e4_complete_local_node_v01(
            state,
            initial=initial_by_node[node.node_id],
            node=node,
            cell_input=root_input,
        )
    latest = {
        (item.cell_id, item.node_id): item
        for item in _g2e4_latest_queue_entries_v01(state)
    }
    pre_terminals = tuple(
        latest[(root_input.cell_id, node.node_id)] for node in nodes[:post_index]
    )
    accepted_outputs = _ordered_unique_v01(
        tuple(
            ref
            for entry in pre_terminals
            for ref in entry.observed_output_refs
        )
    )
    evidence_refs = _ordered_unique_v01(
        tuple(
            ref
            for entry in pre_terminals
            for ref in entry.observed_evidence_refs
        )
    )
    proposal = g2d_runtime.build_fractal_cell_result_proposal_v02(
        source_context=source,
        topology=topology,
        cell_input=root_input,
        pre_post_vv_terminal_queue_entries=pre_terminals,
        child_results=(),
        partial_failures=(),
        accepted_output_refs=accepted_outputs,
        evidence_refs=evidence_refs,
    )
    proposal_report = g2d_runtime.validate_fractal_cell_result_proposal_v02(
        proposal,
        source_context=source,
        topology=topology,
        cell_input=root_input,
        pre_post_vv_terminal_queue_entries=pre_terminals,
        child_results=(),
        partial_failures=(),
    )
    source_time = source.router_input.local_routing_snapshot.kt_asof_utc
    post_vv_report = validate_result_proposal(proposal, checked_at=source_time)
    post_report = g2d_runtime.validate_fractal_post_vv_report_v02(
        post_vv_report,
        result_proposal=proposal,
        source_context=source,
    )
    gt_advisory_report = validate_gt([post_vv_report], created_at=source_time)
    gt_report = g2d_runtime.validate_fractal_gt_advisory_v02(
        gt_advisory_report,
        post_vv_report=post_vv_report,
        source_context=source,
    )
    transient_reports = (proposal_report, post_report, gt_report)
    if any(item.status != "PASS" for item in transient_reports):
        first = next(item for item in transient_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    node_by_kind = {item.node_kind: item for item in nodes}
    post_node = node_by_kind["POST_VV"]
    gt_node = node_by_kind["GT_ADVISORY"]
    parent_node = node_by_kind["PARENT_RETURN"]
    _g2e4_finish_report_node_v01(
        state,
        initial=initial_by_node[post_node.node_id],
        node=post_node,
        cell_input=root_input,
        validation_report=post_report,
        observed_output_ref=post_vv_report["vv_report_id"],
        observed_evidence_ref=proposal["proposal_id"],
    )
    _g2e4_finish_report_node_v01(
        state,
        initial=initial_by_node[gt_node.node_id],
        node=gt_node,
        cell_input=root_input,
        validation_report=gt_report,
        observed_output_ref=gt_advisory_report["gt_report_id"],
        observed_evidence_ref=post_vv_report["vv_report_id"],
    )
    _parent_terminal, _parent_artifact, final_budget = _g2e4_finish_parent_return_v01(
        state,
        initial=initial_by_node[parent_node.node_id],
        node=parent_node,
        cell_input=root_input,
        pre_terminals=pre_terminals,
        proposal=proposal,
        post_vv_report=post_vv_report,
        gt_advisory_report=gt_advisory_report,
        validation_reports=transient_reports,
    )
    latest = {
        (item.cell_id, item.node_id): item
        for item in _g2e4_latest_queue_entries_v01(state)
    }
    terminal_entries = tuple(
        latest[(root_input.cell_id, node.node_id)] for node in nodes
    )
    artifact_by_queue = _g2e4_artifact_by_queue_id_v01(state)
    terminal_artifacts = tuple(
        artifact_by_queue[item.queue_entry_id] for item in terminal_entries
    )
    pre_result_report = g2d_runtime.validate_fractal_cell_result_against_input_v02(
        source_context=source,
        topology=topology,
        cell_input=root_input,
        terminal_queue_entries=terminal_entries,
        child_results=(),
        partial_failures=(),
        result_proposal=proposal,
        post_vv_report=post_vv_report,
        gt_advisory_report=gt_advisory_report,
        cell_budget=final_budget,
        global_budget=final_budget,
    )
    if pre_result_report.status != "PASS":
        raise ValueError(pre_result_report.reason_codes[0])
    root_result = g2d_runtime.build_fractal_cell_result_v02(
        topology,
        root_input,
        terminal_entries,
        (),
        accepted_output_refs=accepted_outputs,
        evidence_refs=evidence_refs,
        pre_result_validation_report=pre_result_report,
        post_vv_report=post_vv_report,
        gt_advisory_report=gt_advisory_report,
        partial_failures=(),
        allocated_cell_budget=root_initial,
        final_cell_budget=final_budget,
        global_budget=final_budget,
    )
    result_artifact = g2d_runtime.project_fractal_cell_result_kernel_artifact_v02(
        root_result,
        topology_artifact=baseline.topology_artifact,
        terminal_queue_artifacts=terminal_artifacts,
        child_result_artifacts=(),
        source_context=source,
    )
    state["cell_results"] = (root_result,)
    state["result_artifacts"] = (result_artifact,)
    state["runtime_artifacts"] = (*state["runtime_artifacts"], result_artifact)
    state["result_proposals"] = (proposal,)
    state["post_vv_reports"] = (post_vv_report,)
    state["gt_advisory_reports"] = (gt_advisory_report,)
    state["pre_result_reports"] = (pre_result_report,)
    parent_return = g2d_runtime.evaluate_fractal_parent_return_transition_v02(
        source_context=source,
        root_result=root_result,
        root_result_artifact=result_artifact,
        ordered_cell_results=(root_result,),
        transition_registry=transition_registry,
    )
    runtime_trace = g2d_runtime.build_fractal_runtime_trace_v02(
        topology,
        baseline.source_binding,
        topology_artifact=baseline.topology_artifact,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        state_transition_decisions=state["queue_decisions"],
        cell_inputs=(root_input,),
        cell_results=(root_result,),
        result_artifacts=(result_artifact,),
        runtime_abi_artifacts=state["runtime_artifacts"],
        scope_projections=(),
        revise_observations=(),
        partial_failures=(),
        backpressure_states=(),
        budgets=state["budgets"],
        topology_transition_decision=topology_transition,
        parent_return_transition_decision=parent_return,
        root_result_artifact=result_artifact,
    )
    runtime_report = g2d_runtime.aggregate_fractal_runtime_report_v02(
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        source_binding=baseline.source_binding,
        cell_results=(root_result,),
        queue_entries=state["queue_entries"],
        backpressure_states=(),
        runtime_trace=runtime_trace,
        final_global_budget=final_budget,
        parent_return_transition_decision=parent_return,
        root_result_artifact=result_artifact,
    )
    report_artifact = g2d_runtime.project_fractal_runtime_report_kernel_artifact_v02(
        runtime_report,
        topology_artifact=baseline.topology_artifact,
        result_artifacts=(result_artifact,),
        source_context=source,
    )
    if transition_runtime.validate_fractal_runtime_transition_decision_v02(
        parent_return,
        registry=transition_registry,
        source_artifact=result_artifact,
        target_artifact=report_artifact,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    report_validation = g2d_runtime.validate_fractal_runtime_report_against_sources_v02(
        runtime_report,
        source_context=source,
        source_binding=baseline.source_binding,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        cell_results=(root_result,),
        queue_entries=state["queue_entries"],
        backpressure_states=(),
        runtime_trace=runtime_trace,
        final_global_budget=final_budget,
        parent_return_transition_decision=parent_return,
        root_result_artifact=result_artifact,
    )
    artifact_by_id = {
        item.artifact_id: item
        for item in (
            baseline.topology_artifact,
            *state["queue_artifacts"],
            result_artifact,
            report_artifact,
        )
    }
    runtime_artifacts = tuple(
        artifact_by_id[item] for item in runtime_trace.abi_artifact_refs
    )
    stage_a = (
        source.proposal_artifact,
        source.decision_artifact,
        source.route_eligibility_artifact,
        baseline.topology_artifact,
    )
    stage_by_name = {
        "STAGE_D_A": stage_a,
        "STAGE_D_B": (*stage_a[:3], *runtime_artifacts),
        "STAGE_D_C": (*stage_a[:3], *runtime_artifacts, report_artifact),
    }
    stage_reports = tuple(
        g2d_runtime.validate_fractal_runtime_stage_bundle_v02(
            stage=stage,
            artifacts=artifacts,
            source_context=source,
            topology=topology,
            topology_artifact=baseline.topology_artifact,
            runtime_trace=runtime_trace,
            queue_entries=state["queue_entries"],
            queue_artifacts=state["queue_artifacts"],
            cell_results=(root_result,),
            result_artifacts=(result_artifact,),
            runtime_report=runtime_report if stage == "STAGE_D_C" else None,
            report_artifact=report_artifact if stage == "STAGE_D_C" else None,
            observed_work_context=observed_context,
        )
        for stage, artifacts in stage_by_name.items()
    )
    if any(item.status != "PASS" for item in stage_reports):
        first = next(item for item in stage_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    stage_c = stage_by_name["STAGE_D_C"]
    abi_report = g2d_runtime.validate_fractal_runtime_abi_profile_v02(
        stage_c,
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_trace=runtime_trace,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=(root_result,),
        result_artifacts=(result_artifact,),
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        observed_work_context=observed_context,
    )
    if abi_report.status != "PASS":
        raise ValueError(abi_report.reason_codes[0])
    causal_refs = g2d_runtime.build_fractal_runtime_causal_consumption_refs_v02(
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_assignments=baseline.runtime_assignments,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=(root_result,),
        result_artifacts=(result_artifact,),
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        observed_work_context=observed_context,
    )
    causal_report = g2d_runtime.validate_fractal_runtime_causal_consumption_refs_v02(
        causal_refs,
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_assignments=baseline.runtime_assignments,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=(root_result,),
        result_artifacts=(result_artifact,),
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        stage_d_c_artifacts=stage_c,
        observed_work_context=observed_context,
    )
    if causal_report.status != "PASS":
        raise ValueError(causal_report.reason_codes[0])
    retained_reports = (
        *state["prefix_reports"],
        pre_result_report,
        g2d_runtime.validate_fractal_cell_result_v02(root_result),
        report_validation,
        *stage_reports,
    )
    bundle = g2d_runtime.build_fractal_runtime_execution_bundle_v02(
        source_context=source,
        source_binding=baseline.source_binding,
        topology_seed=baseline.topology_seed,
        budgets=state["budgets"],
        topology_nodes=baseline.topology_nodes,
        topology_edges=baseline.topology_edges,
        runtime_assignments=baseline.runtime_assignments,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        scope_projections=(),
        cell_inputs=(root_input,),
        revise_observations=(),
        partial_failures=(),
        backpressure_states=(),
        validation_reports=retained_reports,
        result_proposals=(proposal,),
        post_vv_reports=(post_vv_report,),
        gt_advisory_reports=(gt_advisory_report,),
        cell_results=(root_result,),
        result_artifacts=(result_artifact,),
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        transition_decisions=(
            topology_transition,
            *state["queue_decisions"],
            parent_return,
        ),
        causal_consumption_refs=causal_refs,
        observed_work_context=observed_context,
    )
    final_report = g2d_runtime.validate_fractal_runtime_execution_bundle_v02(bundle)
    if final_report.status != "PASS":
        raise ValueError(final_report.reason_codes[0])
    return bundle


def _g2e4_execute_granular_g2d_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
) -> FractalRuntimeExecutionBundleV02:
    baseline = source_context.baseline_g2d_execution_bundle
    observed_context = _g2e4_observed_work_context_v01(
        plan=plan,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        execution_scope="SELECTIVE",
    )
    if (
        len(plan.ordered_affected_cell_ids) != 1
        or len(plan.ordered_work_node_ids) >= len(baseline.topology.ordered_node_ids)
        or observed_context.ordered_affected_cell_ids
        != plan.ordered_affected_cell_ids
        or observed_context.ordered_execution_node_ids
        != plan.ordered_work_node_ids
    ):
        raise ValueError("g2e_topology_binding_mismatch")
    failure_branch_operations = (
        g2d_runtime.evaluate_fractal_revise_observation_v02,
        g2d_runtime.record_fractal_partial_failure_v02,
        g2d_runtime.evaluate_fractal_backpressure_v02,
    )
    if not all(callable(operation) for operation in failure_branch_operations):
        raise ValueError("g2e_recomputation_result_invalid")
    source = baseline.source_context
    topology = baseline.topology
    binding_structure_report = (
        g2d_runtime.validate_runtime_topology_source_binding_v02(
            baseline.source_binding
        )
    )
    required_reports = (
        g2d_runtime.validate_fractal_runtime_source_context_v02(source),
        g2d_runtime.validate_runtime_topology_source_binding_against_g2c_v02(
            baseline.source_binding,
            source_context=source,
        ),
        g2d_runtime.validate_runtime_topology_seed_v02(baseline.topology_seed),
        g2d_runtime.validate_runtime_execution_topology_against_sources_v02(
            topology,
            source_context=source,
        ),
    )
    if binding_structure_report.status != "PASS":
        raise ValueError(binding_structure_report.reason_codes[0])
    if any(item.status != "PASS" for item in required_reports):
        first = next(item for item in required_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    transition_registry = (
        transition_runtime.build_fractal_runtime_transition_registry_profile_v02()
    )
    topology_transition = baseline.transition_decisions[0]
    if transition_runtime.validate_fractal_runtime_transition_decision_v02(
        topology_transition,
        registry=transition_registry,
        source_artifact=source.route_eligibility_artifact,
        target_artifact=baseline.topology_artifact,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    state = _g2e4_selective_prefix_state_v01(
        baseline=baseline,
        plan=plan,
        observed_context=observed_context,
        transition_registry=transition_registry,
        required_reports=required_reports,
    )
    child_context = _g2e4_activate_selected_child_v01(state)
    selected_completion = _g2e4_finalize_cell_v01(
        state,
        cell_input=child_context["cell_input"],
        nodes=child_context["nodes"],
        allocated_budget=child_context["allocated_budget"],
        child_results=(),
    )
    selected_result = selected_completion["result"]
    selected_result_artifact = selected_completion["result_artifact"]
    aggregate_budget = _g2e4_build_budget_successor_v01(
        state,
        selected_completion["completion_global_budget"],
        event="CHILD_AGGREGATE",
        cell_input=state["root_input"],
        canonical_child_index=child_context["canonical_child_index"],
        paired_cell_budget=selected_completion["final_cell_budget"],
        child_result=selected_result,
    )
    state["budgets"] = (*state["budgets"], aggregate_budget)
    slot_dependencies = _g2e4_dependencies_v01(
        state,
        state["activation_entry"],
    )
    _g2e4_finish_parent_slot_v01(
        state,
        running=state["activation_entry"],
        running_artifact=state["activation_artifact"],
        node=state["activation_node"],
        parent_input=state["root_input"],
        dependencies=slot_dependencies,
        child_result=selected_result,
        child_result_artifact=selected_result_artifact,
    )
    sibling_result = next(
        item
        for item in state["cell_results"]
        if item.cell_id == state["sibling_input"].cell_id
    )
    root_completion = _g2e4_finalize_cell_v01(
        state,
        cell_input=state["root_input"],
        nodes=baseline.topology_nodes,
        allocated_budget=baseline.budgets[0],
        child_results=(sibling_result, selected_result),
    )
    root_result = root_completion["result"]
    root_result_artifact = root_completion["result_artifact"]
    final_global_budget = root_completion["completion_global_budget"]
    parent_return = g2d_runtime.evaluate_fractal_parent_return_transition_v02(
        source_context=source,
        root_result=root_result,
        root_result_artifact=root_result_artifact,
        ordered_cell_results=state["cell_results"],
        transition_registry=transition_registry,
    )
    runtime_trace = g2d_runtime.build_fractal_runtime_trace_v02(
        topology,
        baseline.source_binding,
        topology_artifact=baseline.topology_artifact,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        state_transition_decisions=state["queue_decisions"],
        cell_inputs=state["cell_inputs"],
        cell_results=state["cell_results"],
        result_artifacts=state["result_artifacts"],
        runtime_abi_artifacts=state["runtime_artifacts"],
        scope_projections=state["scope_projections"],
        revise_observations=state["revise_observations"],
        partial_failures=state["partial_failures"],
        backpressure_states=state["backpressure_states"],
        budgets=state["budgets"],
        topology_transition_decision=topology_transition,
        parent_return_transition_decision=parent_return,
        root_result_artifact=root_result_artifact,
    )
    runtime_report = g2d_runtime.aggregate_fractal_runtime_report_v02(
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        source_binding=baseline.source_binding,
        cell_results=state["cell_results"],
        queue_entries=state["queue_entries"],
        backpressure_states=state["backpressure_states"],
        runtime_trace=runtime_trace,
        final_global_budget=final_global_budget,
        parent_return_transition_decision=parent_return,
        root_result_artifact=root_result_artifact,
    )
    report_artifact = g2d_runtime.project_fractal_runtime_report_kernel_artifact_v02(
        runtime_report,
        topology_artifact=baseline.topology_artifact,
        result_artifacts=state["result_artifacts"],
        source_context=source,
    )
    if transition_runtime.validate_fractal_runtime_transition_decision_v02(
        parent_return,
        registry=transition_registry,
        source_artifact=root_result_artifact,
        target_artifact=report_artifact,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    report_validation = g2d_runtime.validate_fractal_runtime_report_against_sources_v02(
        runtime_report,
        source_context=source,
        source_binding=baseline.source_binding,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        cell_results=state["cell_results"],
        queue_entries=state["queue_entries"],
        backpressure_states=state["backpressure_states"],
        runtime_trace=runtime_trace,
        final_global_budget=final_global_budget,
        parent_return_transition_decision=parent_return,
        root_result_artifact=root_result_artifact,
    )
    artifact_by_id = {
        item.artifact_id: item
        for item in (
            baseline.topology_artifact,
            *state["queue_artifacts"],
            *state["result_artifacts"],
            report_artifact,
        )
    }
    runtime_artifacts = tuple(
        artifact_by_id[item] for item in runtime_trace.abi_artifact_refs
    )
    stage_a = (
        source.proposal_artifact,
        source.decision_artifact,
        source.route_eligibility_artifact,
        baseline.topology_artifact,
    )
    stage_by_name = {
        "STAGE_D_A": stage_a,
        "STAGE_D_B": (*stage_a[:3], *runtime_artifacts),
        "STAGE_D_C": (*stage_a[:3], *runtime_artifacts, report_artifact),
    }
    stage_reports = tuple(
        g2d_runtime.validate_fractal_runtime_stage_bundle_v02(
            stage=stage,
            artifacts=artifacts,
            source_context=source,
            topology=topology,
            topology_artifact=baseline.topology_artifact,
            runtime_trace=runtime_trace,
            queue_entries=state["queue_entries"],
            queue_artifacts=state["queue_artifacts"],
            cell_results=state["cell_results"],
            result_artifacts=state["result_artifacts"],
            runtime_report=runtime_report if stage == "STAGE_D_C" else None,
            report_artifact=report_artifact if stage == "STAGE_D_C" else None,
            observed_work_context=observed_context,
        )
        for stage, artifacts in stage_by_name.items()
    )
    if any(item.status != "PASS" for item in stage_reports):
        first = next(item for item in stage_reports if item.status != "PASS")
        raise ValueError(first.reason_codes[0])
    stage_c = stage_by_name["STAGE_D_C"]
    abi_report = g2d_runtime.validate_fractal_runtime_abi_profile_v02(
        stage_c,
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_trace=runtime_trace,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=state["cell_results"],
        result_artifacts=state["result_artifacts"],
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        observed_work_context=observed_context,
    )
    if abi_report.status != "PASS":
        raise ValueError(abi_report.reason_codes[0])
    causal_refs = g2d_runtime.build_fractal_runtime_causal_consumption_refs_v02(
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_assignments=baseline.runtime_assignments,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=state["cell_results"],
        result_artifacts=state["result_artifacts"],
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        observed_work_context=observed_context,
    )
    causal_report = g2d_runtime.validate_fractal_runtime_causal_consumption_refs_v02(
        causal_refs,
        source_context=source,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        runtime_assignments=baseline.runtime_assignments,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        cell_results=state["cell_results"],
        result_artifacts=state["result_artifacts"],
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        stage_d_c_artifacts=stage_c,
        observed_work_context=observed_context,
    )
    if causal_report.status != "PASS":
        raise ValueError(causal_report.reason_codes[0])
    retained_reports = (
        *state["prefix_reports"],
        *state["pre_result_reports"],
        *(
            g2d_runtime.validate_fractal_cell_result_v02(item)
            for item in state["cell_results"]
        ),
        report_validation,
        *stage_reports,
    )
    bundle = g2d_runtime.build_fractal_runtime_execution_bundle_v02(
        source_context=source,
        source_binding=baseline.source_binding,
        topology_seed=baseline.topology_seed,
        budgets=state["budgets"],
        topology_nodes=baseline.topology_nodes,
        topology_edges=baseline.topology_edges,
        runtime_assignments=baseline.runtime_assignments,
        topology=topology,
        topology_artifact=baseline.topology_artifact,
        queue_entries=state["queue_entries"],
        queue_artifacts=state["queue_artifacts"],
        scope_projections=state["scope_projections"],
        cell_inputs=state["cell_inputs"],
        revise_observations=state["revise_observations"],
        partial_failures=state["partial_failures"],
        backpressure_states=state["backpressure_states"],
        validation_reports=retained_reports,
        result_proposals=state["result_proposals"],
        post_vv_reports=state["post_vv_reports"],
        gt_advisory_reports=state["gt_advisory_reports"],
        cell_results=state["cell_results"],
        result_artifacts=state["result_artifacts"],
        runtime_trace=runtime_trace,
        runtime_report=runtime_report,
        report_artifact=report_artifact,
        transition_decisions=(
            topology_transition,
            *state["queue_decisions"],
            parent_return,
        ),
        causal_consumption_refs=causal_refs,
        observed_work_context=observed_context,
    )
    final_report = g2d_runtime.validate_fractal_runtime_execution_bundle_v02(bundle)
    if final_report.status != "PASS":
        raise ValueError(final_report.reason_codes[0])
    return bundle


def _g2e4_execute_whole_run_escalation_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    execution_scope: str,
) -> tuple[FractalRuntimeExecutionBundleV02 | None, object]:
    if execution_scope not in {"SELECTIVE", "WHOLE_RUN_ESCALATION"}:
        raise ValueError("g2e_topology_binding_mismatch")
    reason = (
        "g2e_full_affected_closure_requires_reconstruction"
        if execution_scope == "WHOLE_RUN_ESCALATION"
        else None
    )
    policy_id = (
        "fractal_runtime_whole_run_escalation_v02"
        if execution_scope == "WHOLE_RUN_ESCALATION"
        else None
    )
    context = _g2e4_observed_work_context_v01(
        plan=plan,
        source_context=source_context,
        source_bindings=source_bindings,
        changed_field_bindings=changed_field_bindings,
        changed_artifact_bindings=changed_artifact_bindings,
        execution_scope=execution_scope,
        whole_run_escalation_reason=reason,
        whole_run_escalation_policy_id=policy_id,
    )
    return g2d_runtime.run_fractal_runtime_v02(
        source_context.baseline_g2d_execution_bundle.source_context,
        observed_work_context=context,
    )


def _g2e4_derived_id_v01(
    prefix: str,
    domain: str,
    material: object,
) -> str:
    return prefix + domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(material),
    )


def _g2e4_root_decision_artifact_v01(
    *,
    prefix: str,
    domain: str,
    result: RootDecisionResultV01,
    parent_refs: tuple[str, ...],
    trace_refs: tuple[str, ...],
    time_source_artifact: KernelArtifactV01,
) -> KernelArtifactV01:
    complete_payload = root_runtime.root_decision_result_to_plain_dict_v01(result)
    if complete_payload.get("transaction_id") != result.transaction_id:
        raise ValueError("g2e_root_pair_invalid")
    payload = {
        key: value
        for key, value in complete_payload.items()
        if key != "transaction_id"
    }
    time_envelope = _artifact_plain_v01(time_source_artifact)["time_envelope"]
    material = {
        "abi_version": "v1.0",
        "artifact_type": "RootDecision",
        "schema_version": "v0.1",
        "transaction_id": result.transaction_id,
        "owner_root_id": result.target_root_id,
        "source_component": "root_decision_v01",
        "authority_class": "ROOT_OWNED",
        "lifecycle_state": "ROOT_REVIEWED",
        "payload": payload,
        "trace_refs": list(trace_refs),
        "parent_refs": list(parent_refs),
        "time_envelope": time_envelope,
    }
    artifact = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=_g2e4_derived_id_v01(prefix, domain, material),
        artifact_type="RootDecision",
        schema_version="v0.1",
        transaction_id=result.transaction_id,
        owner_root_id=result.target_root_id,
        source_component="root_decision_v01",
        authority_class="ROOT_OWNED",
        lifecycle_state="ROOT_REVIEWED",
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=time_envelope,
    )
    if validate_kernel_artifact_v01(artifact):
        raise ValueError("g2e_recomputation_result_invalid")
    return artifact


def _g2e4_root_review_v01(
    *,
    phase: str,
    request_id: str,
    candidate_id: str,
    candidate_plain: dict[str, object],
    transaction_id: str,
    target_root_id: str,
    topology_ref: str,
    evidence_refs: tuple[str, ...],
    validator_ids: tuple[str, ...],
    policy_id: str,
    time_source_artifact: KernelArtifactV01,
    root_kernel: RootDecisionKernelV01,
    artifact_parent_refs: tuple[str, ...],
    artifact_trace_refs: tuple[str, ...],
    prior_root_state: dict[str, object],
    requested_outcome: str = "ACCEPT",
) -> dict[str, object]:
    if phase not in {"PLAN", "FINAL"} or requested_outcome not in {
        "ACCEPT",
        "BLOCKED_FAIL_CLOSED",
        "NEEDS_USER",
        "NEEDS_MORE_EVIDENCE",
        "DEFER",
        "REJECT",
        "NO_UPDATE",
    }:
        raise ValueError("g2e_root_pair_invalid")
    if not evidence_refs:
        raise ValueError("g2e_root_pair_invalid")
    subject = (
        "selective_recomputation_plan"
        if phase == "PLAN"
        else "selective_recomputation_result"
    )
    evidence_ids = tuple(
        _g2e4_derived_id_v01(
            "g2e_semantic_evidence_v01:",
            "HEDGEHOG_G2E_SEMANTIC_EVIDENCE_V01",
            {"phase": phase, "candidate_id": candidate_id, "ref": ref},
        )
        for ref in evidence_refs
    )
    bindings = tuple(
        semantic_work.build_evidence_binding_v01(
            evidence_id=evidence_id,
            evidence_ref=ref,
            evidence_class=f"G2E_{phase}_EVIDENCE",
            source_component_id="continuous_delta_runtime_v01",
            provenance_ref=time_source_artifact.artifact_id,
            evidence_state=(
                "MISSING"
                if requested_outcome == "NEEDS_MORE_EVIDENCE" and index == 0
                else "PRESENT"
            ),
        )
        for index, (evidence_id, ref) in enumerate(
            zip(evidence_ids, evidence_refs, strict=True)
        )
    )
    request = semantic_work.build_semantic_work_request_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        target_root_id=target_root_id,
        runtime_topology_ref=topology_ref,
        bounded_context_refs=evidence_refs,
        permitted_actor_ids=("deterministic_runtime",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(subject,),
        required_evidence_classes=(f"G2E_{phase}_EVIDENCE",),
        forbidden_claims=(
            "AUTHORITY",
            "PERMISSION",
            "ACTION_COMMIT_PACKET",
            "RECEIPT",
            "FINAL_OUTPUT",
            "DRS_WRITE",
            "REAL_WORLD_EFFECT",
        ),
    )
    time_envelope_ref = time_source_artifact.artifact_id + ":time_envelope"
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id,
        subject=subject,
        predicate="candidate_profile",
        object_or_value=candidate_plain,
        time_envelope_ref=time_envelope_ref,
        provenance_refs=(time_source_artifact.artifact_id,),
        evidence_refs=evidence_ids,
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    claims = (claim,)
    if requested_outcome == "DEFER":
        claims = (
            claim,
            semantic_work.build_normalized_claim_v01(
                claim_id=_g2e4_derived_id_v01(
                    "g2e_semantic_conflict_claim_v01:",
                    "HEDGEHOG_G2E_SEMANTIC_CONFLICT_CLAIM_V01",
                    {"phase": phase, "candidate_id": candidate_id},
                ),
                subject=subject,
                predicate="candidate_profile",
                object_or_value={"candidate_id": candidate_id, "state": "CONFLICT"},
                time_envelope_ref=time_envelope_ref,
                provenance_refs=(time_source_artifact.artifact_id,),
                evidence_refs=evidence_ids,
                confidence_micros=1_000_000,
                source_role="deterministic_runtime",
                source_mode="DETERMINISTIC",
            ),
        )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=_g2e4_derived_id_v01(
            "g2e_semantic_contribution_v01:",
            "HEDGEHOG_G2E_SEMANTIC_CONTRIBUTION_V01",
            {"phase": phase, "candidate_id": candidate_id, "outcome": requested_outcome},
        ),
        request_id=request.request_id,
        actor_id="deterministic_runtime",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=candidate_id,
        scope=topology_ref,
        bounded_context_refs=evidence_refs,
        claims=claims,
        evidence_bindings=bindings,
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=validator_ids,
        forbidden_claims_observed=(),
    )
    trust_profiles = trust_model.build_default_component_trust_profiles_v01()
    packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=trust_profiles,
    )
    if semantic_work.validate_root_review_packet_v01(
        request=request,
        contributions=(contribution,),
        packet=packet,
        trust_profiles=trust_profiles,
    ):
        raise ValueError("g2e_root_pair_invalid")
    provided_refs = tuple(
        binding.evidence_ref
        for binding in bindings
        if binding.evidence_state == "PRESENT"
    )
    selected_candidate_id = (
        None if requested_outcome == "NO_UPDATE" else candidate_id
    )
    root_input = root_runtime.build_root_decision_input_v01(
        transaction_id=transaction_id,
        target_root_id=target_root_id,
        root_review_packet=packet,
        post_vv_bundle={
            "bundle_id": _g2e4_derived_id_v01(
                "g2e_root_validation_bundle_v01:",
                "HEDGEHOG_G2E_ROOT_VALIDATION_BUNDLE_V01",
                {"phase": phase, "candidate_id": candidate_id, "refs": list(evidence_refs)},
            ),
            "hard_failure_reasons": [],
            "post_vv_passed": True,
            "provided_evidence_refs": list(provided_refs),
            "rejected_candidate_ids": [],
            "required_evidence_refs": list(evidence_refs),
            "validated_candidate_ids": [candidate_id],
        },
        gt_advisory={
            "actor_role": "gt",
            "advisory_id": _g2e4_derived_id_v01(
                "g2e_root_gt_advisory_v01:",
                "HEDGEHOG_G2E_ROOT_GT_ADVISORY_V01",
                {"phase": phase, "candidate_id": candidate_id, "refs": list(evidence_refs)},
            ),
            "advisory_only": True,
            "attempted_effect": "CREATE_ROOT_DECISION",
            "candidate_ids": [candidate_id],
            "creates_final_output": False,
            "requests_effect": False,
            "score_micros_by_candidate": {candidate_id: 1_000_000},
            "selected_candidate_id": selected_candidate_id,
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "target_artifact_type": "RootDecision",
        },
        policy_state={
            "allow_accept": requested_outcome != "REJECT",
            "conflict_policy": "DEFER" if requested_outcome == "DEFER" else "REJECT",
            "hard_policy_passed": True,
            "identity_passed": requested_outcome != "BLOCKED_FAIL_CLOSED",
            "no_candidate_policy": "NO_UPDATE" if requested_outcome == "NO_UPDATE" else "REJECT",
            "policy_id": policy_id,
            "scope_passed": True,
        },
        permission_state={
            "permission_ref": None,
            "permission_required": requested_outcome == "NEEDS_USER",
            "permission_scope_valid": True,
            "user_permission_present": False,
        },
        temporal_state={
            "expired": False,
            "not_before_satisfied": True,
            "temporal_valid": True,
            "time_envelope_ref": time_envelope_ref,
        },
        conflict_state={
            "conflict_set_ids": list(packet.conflict_set_ids),
            "material_unresolved_conflict": requested_outcome == "DEFER",
        },
        prior_root_state=prior_root_state,
    )
    if root_runtime.validate_root_decision_input_v01(
        kernel=root_kernel,
        decision_input=root_input,
    ):
        raise ValueError("g2e_root_pair_invalid")
    result = root_runtime.decide_root_v01(
        kernel=root_kernel,
        decision_input=root_input,
    )
    if (
        root_runtime.validate_root_decision_result_v01(
            kernel=root_kernel,
            decision_input=root_input,
            result=result,
        )
        or result.decision != requested_outcome
        or result.permission_created
        or result.final_output_created
        or result.effect_requested
    ):
        raise ValueError("g2e_root_pair_invalid")
    if phase == "PLAN":
        prefix = "g2e_root_plan_decision_v01:"
        domain = "HEDGEHOG_G2E_PLAN_ROOT_DECISION_ARTIFACT_V01"
    else:
        prefix = "g2e_root_final_decision_v01:"
        domain = "HEDGEHOG_G2E_FINAL_ROOT_DECISION_ARTIFACT_V01"
    artifact = _g2e4_root_decision_artifact_v01(
        prefix=prefix,
        domain=domain,
        result=result,
        parent_refs=artifact_parent_refs,
        trace_refs=(root_input.decision_input_id, packet.packet_id, *artifact_trace_refs),
        time_source_artifact=time_source_artifact,
    )
    return {
        "request": request,
        "contribution": contribution,
        "packet": packet,
        "input": root_input,
        "result": result,
        "artifact": artifact,
    }


def _g2e4_project_plan_proposed_artifact_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
    dependency_graph_artifact: KernelArtifactV01,
    affected_set_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
) -> KernelArtifactV01:
    baseline = source_context.baseline_g2d_execution_bundle
    return _project_g2e_kernel_artifact_v01(
        profile_name="plan_proposed",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="plan_proposed",
            complete_payload=selective_recomputation_plan_to_plain_data_v01(plan),
        ),
        trace_refs=_ordered_unique_v01(
            (
                *plan.trace_refs,
                delta.delta_id,
                plan.affected_set_id,
                plan.invalidation_report_id,
                plan.source_route_eligibility_artifact_id,
                plan.source_topology_id,
            )
        ),
        parent_refs=(
            invalidation_report_artifact.artifact_id,
            affected_set_artifact.artifact_id,
            dependency_graph_artifact.artifact_id,
            source_context.baseline_g2c_route_eligibility_artifact.artifact_id,
            baseline.report_artifact.artifact_id,
        ),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=(
                source_context.baseline_g2c_route_eligibility_artifact
            ),
            delta=delta,
        ),
    )


def _g2e4_project_plan_accepted_artifact_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    proposed_artifact: KernelArtifactV01,
    root_input: RootDecisionInputV01,
    root_result: RootDecisionResultV01,
    root_artifact: KernelArtifactV01,
    t04: TransitionDecisionV01,
    t05: TransitionDecisionV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
) -> KernelArtifactV01:
    if (
        root_result.decision != "ACCEPT"
        or root_result.selected_candidate_id != plan.recomputation_plan_id
    ):
        raise ValueError("g2e_root_pair_invalid")
    return _project_g2e_kernel_artifact_v01(
        profile_name="plan_root_accepted",
        transaction_id=delta.transaction_id,
        owning_root_id=delta.owning_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="plan_root_accepted",
            complete_payload=selective_recomputation_plan_to_plain_data_v01(plan),
        ),
        trace_refs=(
            proposed_artifact.artifact_id,
            root_input.decision_input_id,
            root_result.decision_id,
            t04.decision_id,
            t05.decision_id,
        ),
        parent_refs=(proposed_artifact.artifact_id, root_artifact.artifact_id),
        time_envelope=_artifact_time_envelope_v01(
            baseline_route_artifact=(
                source_context.baseline_g2c_route_eligibility_artifact
            ),
            delta=delta,
        ),
    )


def _g2e4_project_blocked_plan_artifact_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    proposed_artifact: KernelArtifactV01,
    root_result: RootDecisionResultV01,
    root_artifact: KernelArtifactV01,
    t06: TransitionDecisionV01,
    delta: WorldStateDeltaV01,
    source_context: ContinuousDeltaSourceContextV01,
) -> KernelArtifactV01:
    complete_payload = selective_recomputation_plan_to_plain_data_v01(plan)
    if tuple(complete_payload.get("trace_refs", ())) != plan.trace_refs:
        raise ValueError("g2e_root_pair_invalid")
    payload = _project_g2e_abi_payload_v01(
        profile_name="plan_proposed",
        complete_payload=complete_payload,
    )
    payload["root_decision"] = root_result.decision
    payload["root_reason_code"] = root_result.reason_code
    time_envelope = _artifact_time_envelope_v01(
        baseline_route_artifact=(
            source_context.baseline_g2c_route_eligibility_artifact
        ),
        delta=delta,
    )
    material = {
        "abi_version": "v1.0",
        "artifact_type": "SelectiveRecomputationPlan",
        "schema_version": "v0.1",
        "transaction_id": delta.transaction_id,
        "owner_root_id": delta.owning_root_id,
        "source_component": "continuous_delta_runtime_v01",
        "authority_class": "ADVISORY",
        "lifecycle_state": "BLOCKED_FAIL_CLOSED",
        "payload": payload,
        "trace_refs": [root_result.decision_id, root_result.reason_code, t06.decision_id],
        "parent_refs": [proposed_artifact.artifact_id, root_artifact.artifact_id],
        "time_envelope": time_envelope,
    }
    artifact = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=_g2e4_derived_id_v01(
            "g2eabi_plan_blocked_v01:",
            "HEDGEHOG_G2E_SELECTIVE_RECOMPUTATION_PLAN_BLOCKED_ARTIFACT_V01",
            material,
        ),
        artifact_type="SelectiveRecomputationPlan",
        schema_version="v0.1",
        transaction_id=delta.transaction_id,
        owner_root_id=delta.owning_root_id,
        source_component="continuous_delta_runtime_v01",
        authority_class="ADVISORY",
        lifecycle_state="BLOCKED_FAIL_CLOSED",
        payload=payload,
        trace_refs=(root_result.decision_id, root_result.reason_code, t06.decision_id),
        parent_refs=(proposed_artifact.artifact_id, root_artifact.artifact_id),
        time_envelope=time_envelope,
    )
    if validate_kernel_artifact_v01(artifact):
        raise ValueError("g2e_root_pair_invalid")
    return artifact


def _g2e4_project_e3_artifact_family_v01(
    *,
    delta: WorldStateDeltaV01,
    dependency_graph: DependencyGraphIndexV01,
    affected_result: AffectedSetResultV01,
    invalidation_report: InvalidationReportV01,
    source_context: ContinuousDeltaSourceContextV01,
    transitions: tuple[TransitionDecisionV01, ...],
) -> dict[str, KernelArtifactV01]:
    t01, t02, t03 = transitions[:3]
    proposed = _project_delta_source_proposed_artifact_v01(
        delta=delta,
        baseline_route_artifact=source_context.baseline_g2c_route_eligibility_artifact,
        baseline_g2d_report_artifact=(
            source_context.baseline_g2d_execution_bundle.report_artifact
        ),
        baseline_source_artifacts=source_context.baseline_source_artifacts,
        observed_source_artifacts=source_context.observed_source_artifacts,
    )
    validated = _project_delta_source_validated_artifact_v01(
        delta=delta,
        proposed_source_artifact=proposed,
        t01_decision_id=t01.decision_id,
        baseline_route_artifact=source_context.baseline_g2c_route_eligibility_artifact,
        baseline_g2d_report_artifact=(
            source_context.baseline_g2d_execution_bundle.report_artifact
        ),
        baseline_source_artifacts=source_context.baseline_source_artifacts,
        observed_source_artifacts=source_context.observed_source_artifacts,
    )
    graph_artifact = _project_dependency_graph_artifact_v01(
        graph=dependency_graph,
        delta=delta,
        validated_delta_source_artifact=validated,
        baseline_route_artifact=source_context.baseline_g2c_route_eligibility_artifact,
        baseline_source_artifacts=source_context.baseline_source_artifacts,
    )
    affected_artifact = _project_affected_set_artifact_v01(
        affected_result=affected_result,
        delta=delta,
        validated_delta_source_artifact=validated,
        dependency_graph_artifact=graph_artifact,
        baseline_route_artifact=source_context.baseline_g2c_route_eligibility_artifact,
        t02_decision_id=t02.decision_id,
    )
    invalidation_artifact = _project_invalidation_report_artifact_v01(
        report=invalidation_report,
        affected_set_artifact=affected_artifact,
        validated_delta_source_artifact=validated,
        dependency_graph_artifact=graph_artifact,
        baseline_route_artifact=source_context.baseline_g2c_route_eligibility_artifact,
        delta=delta,
        t03_decision_id=t03.decision_id,
    )
    registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
    relations = (
        (t01, proposed, validated),
        (t02, validated, affected_artifact),
        (t03, affected_artifact, invalidation_artifact),
    )
    if any(
        transition_runtime.validate_continuous_delta_transition_decision_v01(
            decision,
            registry=registry,
            source_artifact=source,
            target_artifact=target,
        )
        for decision, source, target in relations
    ):
        raise ValueError("g2e_transition_binding_invalid")
    return {
        "proposed": proposed,
        "validated": validated,
        "graph": graph_artifact,
        "affected": affected_artifact,
        "invalidation": invalidation_artifact,
    }


def _g2e4_causal_ref_v01(
    *,
    producer_actor_id: str,
    source_artifact: KernelArtifactV01,
    output_field: str,
    consumer_component: str,
    downstream_artifact: KernelArtifactV01,
    transition: TransitionDecisionV01,
    disposition: str,
    trace_refs: tuple[str, ...],
) -> CausalConsumptionRefV01:
    reason_prefix = {
        "USED": "used:",
        "REJECTED": "rejected:",
        "IGNORED_WITH_REASON": "ignored:",
        "BLOCKED_BY_GATE": "gate:",
    }.get(disposition)
    if reason_prefix is None:
        raise ValueError("g2e_causal_binding_invalid")
    causal_ref = build_causal_consumption_ref_v01(
        producer_actor_id=producer_actor_id,
        source_artifact_id=source_artifact.artifact_id,
        output_field=output_field,
        consumer_component=consumer_component,
        downstream_artifact_id=downstream_artifact.artifact_id,
        decision_effect=transition.decision,
        disposition=disposition,
        reason_code=reason_prefix + transition.reason_code,
        trace_refs=trace_refs,
    )
    if validate_causal_consumption_ref_v01(causal_ref):
        raise ValueError("g2e_causal_binding_invalid")
    return causal_ref


def _g2e4_causal_ref_id_v01(value: CausalConsumptionRefV01) -> str:
    if validate_causal_consumption_ref_v01(value):
        raise ValueError("g2e_causal_binding_invalid")
    material = {
        field.name: _plain_value(getattr(value, field.name))
        for field in fields(CausalConsumptionRefV01)
    }
    return _g2e4_derived_id_v01(
        "g2e_causal_consumption_ref_v01:",
        "HEDGEHOG_G2E_CAUSAL_CONSUMPTION_REF_V01",
        material,
    )


def _g2e4_recomputed_bindings_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    baseline: FractalRuntimeExecutionBundleV02,
    recomputed: FractalRuntimeExecutionBundleV02,
) -> tuple[RecomputedArtifactBindingV01, ...]:
    root_result = recomputed.cell_results[-1]
    bindings: list[RecomputedArtifactBindingV01] = []
    result_by_cell = {item.cell_id: item for item in recomputed.cell_results}
    pairs: list[
        tuple[KernelArtifactV01, KernelArtifactV01, str, object]
    ] = []
    prior_queue_rows: dict[
        tuple[str, str, str, int, int], KernelArtifactV01
    ] = {}
    for entry, artifact in zip(
        baseline.queue_entries, baseline.queue_artifacts, strict=True
    ):
        key = (
            entry.cell_id,
            entry.node_id,
            entry.state,
            entry.node_instance_sequence,
            entry.snapshot_sequence,
        )
        if key in prior_queue_rows:
            raise ValueError("g2e_recomputation_result_invalid")
        prior_queue_rows[key] = artifact
    for entry, artifact in zip(
        recomputed.queue_entries, recomputed.queue_artifacts, strict=True
    ):
        key = (
            entry.cell_id,
            entry.node_id,
            entry.state,
            entry.node_instance_sequence,
            entry.snapshot_sequence,
        )
        prior = prior_queue_rows.get(key)
        if prior is None:
            raise ValueError("g2e_recomputation_result_invalid")
        owner_result = result_by_cell.get(entry.cell_id)
        if owner_result is None:
            raise ValueError("g2e_recomputation_result_invalid")
        pairs.append((prior, artifact, entry.queue_entry_id, owner_result))
    prior_results = {
        (result.cell_id, result.parent_cell_id, result.outcome): artifact
        for result, artifact in zip(
            baseline.cell_results, baseline.result_artifacts, strict=True
        )
    }
    for result, artifact in zip(
        recomputed.cell_results, recomputed.result_artifacts, strict=True
    ):
        prior = prior_results.get(
            (result.cell_id, result.parent_cell_id, result.outcome)
        )
        if prior is None:
            raise ValueError("g2e_recomputation_result_invalid")
        queue_entry_id = (
            result.ordered_terminal_queue_entry_ids[-1]
            if result.ordered_terminal_queue_entry_ids
            else ""
        )
        if not queue_entry_id:
            raise ValueError("g2e_recomputation_result_invalid")
        pairs.append((prior, artifact, queue_entry_id, result))
    pairs.append(
        (
            baseline.report_artifact,
            recomputed.report_artifact,
            root_result.ordered_terminal_queue_entry_ids[-1],
            root_result,
        )
    )
    seen_prior_ids: set[str] = set()
    seen_new_ids: set[str] = set()
    for prior, new, queue_entry_id, owner_result in pairs:
        prior_payload_sha = _artifact_payload_sha256_v01(prior)
        new_payload_sha = _artifact_payload_sha256_v01(new)
        if prior.artifact_id == new.artifact_id:
            if prior_payload_sha != new_payload_sha:
                raise ValueError("g2e_recomputation_result_invalid")
            continue
        if prior_payload_sha == new_payload_sha:
            continue
        if (
            prior.artifact_id in seen_prior_ids
            or new.artifact_id in seen_new_ids
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        seen_prior_ids.add(prior.artifact_id)
        seen_new_ids.add(new.artifact_id)
        bindings.append(
            build_recomputed_artifact_binding_v01(
                recomputation_plan_id=plan.recomputation_plan_id,
                prior_artifact_id=prior.artifact_id,
                prior_payload_sha256=prior_payload_sha,
                new_artifact_id=new.artifact_id,
                new_payload_sha256=new_payload_sha,
                predecessor_relation="DIRECT_PREDECESSOR",
                supersession_relation="SUPERSEDES",
                derivation_refs=(
                    plan.recomputation_plan_id,
                    recomputed.observed_work_context.observed_work_context_id,
                    owner_result.result_id,
                    recomputed.runtime_report.report_id,
                ),
                source_cell_id=owner_result.cell_id,
                source_queue_entry_id=queue_entry_id,
                g2d_cell_result_ref=owner_result.result_id,
                g2d_runtime_report_ref=recomputed.runtime_report.report_id,
                trace_refs=(
                    recomputed.runtime_trace.trace_id,
                    prior.artifact_id,
                    new.artifact_id,
                ),
            )
        )
    if not bindings:
        raise ValueError("g2e_recomputation_in_place_forbidden")
    return tuple(bindings)


def _g2e4_preservation_family_v01(
    *,
    affected_result: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    source_context: ContinuousDeltaSourceContextV01,
    recomputed_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    accepted_plan_artifact: KernelArtifactV01,
    invalidation_artifact: KernelArtifactV01,
    delta: WorldStateDeltaV01,
) -> tuple[PreservationProofV01, KernelArtifactV01]:
    proof = prove_unaffected_artifact_preservation_v01(
        affected_set=affected_result,
        invalidation_records=invalidation_records,
        source_context=source_context,
        recomputed_g2d_execution_bundle=recomputed_bundle,
        recomputed_bindings=recomputed_bindings,
    )
    artifact = _project_preservation_proof_artifact_v01(
        proof=proof,
        root_accepted_plan_artifact=accepted_plan_artifact,
        invalidation_report_artifact=invalidation_artifact,
        recomputed_g2d_report_artifact=recomputed_bundle.report_artifact,
        delta=delta,
        recomputed_g2d_runtime_trace_id=recomputed_bundle.runtime_trace.trace_id,
    )
    return proof, artifact


def _g2e4_build_recomputation_result_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    invalidation_report: InvalidationReportV01,
    recomputed_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    preservation_proof: PreservationProofV01,
) -> SelectiveRecomputationResultV01:
    unresolved = invalidation_report.ordered_unresolved_artifact_ids
    partial_failures = tuple(
        item.partial_failure_id for item in recomputed_bundle.partial_failures
    )
    reasons: tuple[str, ...] = ()
    if unresolved or partial_failures:
        reasons = ("g2e_recomputation_result_invalid",)
    return build_selective_recomputation_result_v01(
        recomputation_plan_id=plan.recomputation_plan_id,
        baseline_runtime_report_id=(
            source_context.baseline_g2d_execution_bundle.runtime_report.report_id
        ),
        recomputed_runtime_report_id=recomputed_bundle.runtime_report.report_id,
        preservation_proof_id=preservation_proof.preservation_proof_id,
        ordered_recomputed_binding_ids=tuple(
            item.recomputed_binding_id for item in recomputed_bindings
        ),
        ordered_invalidated_downstream_ids=(
            invalidation_report.ordered_invalidated_artifact_ids
        ),
        ordered_recomputed_artifact_ids=tuple(
            item.new_artifact_id for item in recomputed_bindings
        ),
        ordered_preserved_artifact_ids=(
            preservation_proof.ordered_preserved_artifact_ids
        ),
        ordered_unresolved_artifact_ids=unresolved,
        ordered_partial_failure_ids=partial_failures,
        parent_return_transition_decision_id=(
            recomputed_bundle.transition_decisions[-1].decision_id
        ),
        result_status="PASS" if not reasons else "FAIL_CLOSED",
        reason_codes=reasons,
        provider_calls=0,
        model_calls=0,
        network_calls=0,
        connector_calls=0,
        external_drs_calls=0,
        action_commit_packets_created=0,
        permissions_created=0,
        receipts_created=0,
        final_outputs_created=0,
        drs_writes=0,
        authority_created_count=0,
        real_world_effects_count=0,
    )


def _g2e4_recomputation_result_errors_v01(
    value: object,
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    delta_source_proposed_artifact: KernelArtifactV01,
    delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    affected_set_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
    plan_proposed_artifact: KernelArtifactV01,
    plan_root_decision_input: RootDecisionInputV01,
    plan_root_decision_result: RootDecisionResultV01,
    plan_root_decision_artifact: KernelArtifactV01,
    plan_accepted_artifact: KernelArtifactV01,
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    preservation_proof: PreservationProofV01,
    preservation_proof_artifact: KernelArtifactV01,
    g2e_transition_decisions: tuple[TransitionDecisionV01, ...],
    g2e_causal_consumption_refs: tuple[CausalConsumptionRefV01, ...],
) -> tuple[str, ...]:
    errors: list[str] = list(_selective_recomputation_result_errors_v01(value))
    if (
        _selective_recomputation_plan_errors_v01(plan)
        or validate_continuous_delta_source_context_v01(source_context).status
        != "PASS"
        or type(recomputed_g2d_execution_bundle)
        is not FractalRuntimeExecutionBundleV02
        or validate_fractal_runtime_execution_bundle_v02(
            recomputed_g2d_execution_bundle
        ).status
        != "PASS"
    ):
        errors.append("g2e_recomputation_result_invalid")
    artifacts = (
        delta_source_proposed_artifact,
        delta_source_artifact,
        dependency_graph_artifact,
        affected_set_artifact,
        invalidation_report_artifact,
        plan_proposed_artifact,
        plan_root_decision_artifact,
        plan_accepted_artifact,
        preservation_proof_artifact,
        recomputed_g2d_execution_bundle.report_artifact,
    )
    if any(
        type(item) is not KernelArtifactV01 or validate_kernel_artifact_v01(item)
        for item in artifacts
    ):
        errors.append("g2e_recomputation_result_invalid")
    expected_artifact_geometry = (
        (delta_source_proposed_artifact, "ContinuousDeltaSource", "PROPOSED"),
        (delta_source_artifact, "ContinuousDeltaSource", "VALIDATED"),
        (dependency_graph_artifact, "DependencyGraphIndex", "VALIDATED"),
        (affected_set_artifact, "AffectedSetResult", "VALIDATED"),
        (
            invalidation_report_artifact,
            "ArtifactInvalidationReport",
            "VALIDATED",
        ),
        (plan_proposed_artifact, "SelectiveRecomputationPlan", "PROPOSED"),
        (plan_root_decision_artifact, "RootDecision", "ROOT_REVIEWED"),
        (
            plan_accepted_artifact,
            "SelectiveRecomputationPlan",
            "ROOT_ACCEPTED",
        ),
        (preservation_proof_artifact, "PreservationProof", "VALIDATED"),
        (
            recomputed_g2d_execution_bundle.report_artifact,
            "FractalRuntimeReport",
            "VALIDATED",
        ),
    )
    if any(
        item.artifact_type != artifact_type
        or item.lifecycle_state != lifecycle_state
        for item, artifact_type, lifecycle_state in expected_artifact_geometry
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        root_runtime.validate_root_decision_input_v01(
            kernel=source_context.root_kernel,
            decision_input=plan_root_decision_input,
        )
        or root_runtime.validate_root_decision_result_v01(
            kernel=source_context.root_kernel,
            decision_input=plan_root_decision_input,
            result=plan_root_decision_result,
        )
        or plan_root_decision_result.decision != "ACCEPT"
        or plan_root_decision_result.selected_candidate_id
        != plan.recomputation_plan_id
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        type(recomputed_bindings) is not tuple
        or not recomputed_bindings
        or any(_recomputed_artifact_binding_errors_v01(item) for item in recomputed_bindings)
        or tuple(item.recomputation_plan_id for item in recomputed_bindings)
        != (plan.recomputation_plan_id,) * len(recomputed_bindings)
        or len({item.prior_artifact_id for item in recomputed_bindings})
        != len(recomputed_bindings)
        or len({item.new_artifact_id for item in recomputed_bindings})
        != len(recomputed_bindings)
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        _preservation_proof_errors_v01(preservation_proof)
        or preservation_proof_artifact.parent_refs
        != (
            plan_accepted_artifact.artifact_id,
            invalidation_report_artifact.artifact_id,
            recomputed_g2d_execution_bundle.report_artifact.artifact_id,
        )
    ):
        errors.append("g2e_preservation_proof_invalid")
    expected_transitions = _g2e4_transition_decisions_v01()
    registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
    if (
        type(g2e_transition_decisions) is not tuple
        or g2e_transition_decisions != expected_transitions
        or any(
            _continuous_delta_transition_decision_errors_v01(
                item, registry=registry
            )
            for item in g2e_transition_decisions
        )
    ):
        errors.append("g2e_recomputation_result_invalid")
    transition_relations = (
        (expected_transitions[0], delta_source_proposed_artifact, delta_source_artifact),
        (expected_transitions[1], delta_source_artifact, affected_set_artifact),
        (expected_transitions[2], affected_set_artifact, invalidation_report_artifact),
        (expected_transitions[3], plan_proposed_artifact, plan_root_decision_artifact),
        (expected_transitions[4], plan_root_decision_artifact, plan_accepted_artifact),
        (
            expected_transitions[6],
            plan_accepted_artifact,
            recomputed_g2d_execution_bundle.report_artifact,
        ),
    )
    if any(
        transition_runtime.validate_continuous_delta_transition_decision_v01(
            decision,
            registry=registry,
            source_artifact=source,
            target_artifact=target,
        )
        for decision, source, target in transition_relations
    ):
        errors.append("g2e_recomputation_result_invalid")
    if (
        type(g2e_causal_consumption_refs) is not tuple
        or not g2e_causal_consumption_refs
        or any(
            type(item) is not CausalConsumptionRefV01
            or validate_causal_consumption_ref_v01(item)
            for item in g2e_causal_consumption_refs
        )
        or len({_g2e4_causal_ref_id_v01(item) for item in g2e_causal_consumption_refs})
        != len(g2e_causal_consumption_refs)
    ):
        errors.append("g2e_recomputation_result_invalid")
    if type(value) is SelectiveRecomputationResultV01:
        if (
            value.recomputation_plan_id != plan.recomputation_plan_id
            or value.baseline_runtime_report_id
            != source_context.baseline_g2d_execution_bundle.runtime_report.report_id
            or value.recomputed_runtime_report_id
            != recomputed_g2d_execution_bundle.runtime_report.report_id
            or value.preservation_proof_id != preservation_proof.preservation_proof_id
            or value.ordered_recomputed_binding_ids
            != tuple(item.recomputed_binding_id for item in recomputed_bindings)
            or value.ordered_recomputed_artifact_ids
            != tuple(item.new_artifact_id for item in recomputed_bindings)
            or value.ordered_preserved_artifact_ids
            != preservation_proof.ordered_preserved_artifact_ids
            or value.ordered_unresolved_artifact_ids
            or value.ordered_partial_failure_ids
            or value.parent_return_transition_decision_id
            != recomputed_g2d_execution_bundle.transition_decisions[-1].decision_id
            or value.result_status != "PASS"
        ):
            errors.append("g2e_recomputation_result_invalid")
    return _ordered_reasons(errors)


def _validate_selective_recomputation_result_against_plan_impl_v01(
    value: SelectiveRecomputationResultV01,
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    delta_source_proposed_artifact: KernelArtifactV01,
    delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    affected_set_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
    plan_proposed_artifact: KernelArtifactV01,
    plan_root_decision_input: RootDecisionInputV01,
    plan_root_decision_result: RootDecisionResultV01,
    plan_root_decision_artifact: KernelArtifactV01,
    plan_accepted_artifact: KernelArtifactV01,
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    preservation_proof: PreservationProofV01,
    preservation_proof_artifact: KernelArtifactV01,
    g2e_transition_decisions: tuple[TransitionDecisionV01, ...],
    g2e_causal_consumption_refs: tuple[CausalConsumptionRefV01, ...],
) -> ContinuousDeltaValidationReportV01:
    errors = _g2e4_recomputation_result_errors_v01(
        value,
        plan=plan,
        source_context=source_context,
        delta_source_proposed_artifact=delta_source_proposed_artifact,
        delta_source_artifact=delta_source_artifact,
        dependency_graph_artifact=dependency_graph_artifact,
        affected_set_artifact=affected_set_artifact,
        invalidation_report_artifact=invalidation_report_artifact,
        plan_proposed_artifact=plan_proposed_artifact,
        plan_root_decision_input=plan_root_decision_input,
        plan_root_decision_result=plan_root_decision_result,
        plan_root_decision_artifact=plan_root_decision_artifact,
        plan_accepted_artifact=plan_accepted_artifact,
        recomputed_g2d_execution_bundle=recomputed_g2d_execution_bundle,
        recomputed_bindings=recomputed_bindings,
        preservation_proof=preservation_proof,
        preservation_proof_artifact=preservation_proof_artifact,
        g2e_transition_decisions=g2e_transition_decisions,
        g2e_causal_consumption_refs=g2e_causal_consumption_refs,
    )
    return _contextual_report_v01(
        validation_target="recomputation_result_against_plan",
        validated_object_id=value.recomputation_result_id if not errors else None,
        failure_stage="recomputation_execution",
        reason_codes=errors,
    )


def _g2e4_failure_report_v01(
    error: object,
    *,
    failure_stage: str = "bundle_final",
) -> ContinuousDeltaValidationReportV01:
    candidate = (
        error.args[0]
        if isinstance(error, ValueError)
        and len(error.args) == 1
        and type(error.args[0]) is str
        else None
    )
    reason = (
        candidate
        if candidate in PUBLIC_G2E_REASON_CODES_V01
        else "g2e_recomputation_result_invalid"
    )
    return _contextual_report_v01(
        validation_target="ContinuousDeltaExecutionBundleV01",
        validated_object_id=None,
        failure_stage=failure_stage,
        reason_codes=(reason,),
    )


def _g2e4_runtime_report_artifact_v01(
    *,
    report: ContinuousDeltaRuntimeReportV01,
    accepted_plan_artifact: KernelArtifactV01,
    recomputed_report_artifact: KernelArtifactV01,
    preservation_proof_artifact: KernelArtifactV01,
    final_root_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
) -> KernelArtifactV01:
    return _project_g2e_kernel_artifact_v01(
        profile_name="runtime_report_finalized",
        transaction_id=recomputed_report_artifact.transaction_id,
        owning_root_id=recomputed_report_artifact.owner_root_id,
        payload=_project_g2e_abi_payload_v01(
            profile_name="runtime_report_finalized",
            complete_payload=continuous_delta_runtime_report_to_plain_data_v01(report),
        ),
        trace_refs=(
            report.trace_id,
            report.plan_root_decision_id,
            report.final_root_decision_id,
            report.recomputation_result_id,
            report.baseline_report_id,
        ),
        parent_refs=(
            accepted_plan_artifact.artifact_id,
            recomputed_report_artifact.artifact_id,
            preservation_proof_artifact.artifact_id,
            final_root_artifact.artifact_id,
            invalidation_report_artifact.artifact_id,
        ),
        time_envelope=_artifact_plain_v01(recomputed_report_artifact)[
            "time_envelope"
        ],
    )


def execute_selective_recomputation_v01(
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    delta: WorldStateDeltaV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
    affected_request: AffectedSetRequestV01,
    affected_result: AffectedSetResultV01,
    invalidation_records: tuple[ArtifactInvalidationRecordV01, ...],
    invalidation_report: InvalidationReportV01,
) -> tuple[
    ContinuousDeltaExecutionBundleV01 | None,
    ContinuousDeltaValidationReportV01,
]:
    try:
        plan_context_report = validate_selective_recomputation_plan_against_sources_v01(
            plan,
            delta=delta,
            affected_set=affected_result,
            invalidation_records=invalidation_records,
            invalidation_report=invalidation_report,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        if plan_context_report.status != "PASS":
            raise ValueError(plan_context_report.reason_codes[0])
        if (
            type(affected_request) is not AffectedSetRequestV01
            or _affected_set_request_errors(affected_request)
            or affected_request.affected_request_id
            != affected_result.affected_request_id
        ):
            raise ValueError("g2e_affected_request_invalid")
        transitions = _g2e4_transition_decisions_v01()
        e3_artifacts = _g2e4_project_e3_artifact_family_v01(
            delta=delta,
            dependency_graph=dependency_graph,
            affected_result=affected_result,
            invalidation_report=invalidation_report,
            source_context=source_context,
            transitions=transitions,
        )
        plan_proposed_artifact = _g2e4_project_plan_proposed_artifact_v01(
            plan=plan,
            delta=delta,
            source_context=source_context,
            dependency_graph_artifact=e3_artifacts["graph"],
            affected_set_artifact=e3_artifacts["affected"],
            invalidation_report_artifact=e3_artifacts["invalidation"],
        )
        source_context_report = validate_continuous_delta_source_context_v01(
            source_context
        )
        invalidation_context_report = validate_invalidation_report_against_sources_v01(
            invalidation_report,
            records=invalidation_records,
            affected_set=affected_result,
            delta=delta,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        plan_structural_report = validate_selective_recomputation_plan_v01(plan)
        pre_plan_reports = (
            source_context_report,
            invalidation_context_report,
            plan_structural_report,
            plan_context_report,
        )
        if any(item.status != "PASS" for item in pre_plan_reports):
            first = next(item for item in pre_plan_reports if item.status != "PASS")
            raise ValueError(first.reason_codes[0])
        baseline = source_context.baseline_g2d_execution_bundle
        plan_root = _g2e4_root_review_v01(
            phase="PLAN",
            request_id=delta.request_id,
            candidate_id=plan.recomputation_plan_id,
            candidate_plain=selective_recomputation_plan_to_plain_data_v01(plan),
            transaction_id=delta.transaction_id,
            target_root_id=delta.owning_root_id,
            topology_ref=plan.source_topology_id,
            evidence_refs=tuple(
                item.validation_report_id for item in pre_plan_reports
            ),
            validator_ids=("continuous_delta_plan_against_sources_v01",),
            policy_id=delta.observed_policy_version,
            time_source_artifact=plan_proposed_artifact,
            root_kernel=source_context.root_kernel,
            artifact_parent_refs=(
                plan_proposed_artifact.artifact_id,
                source_context.baseline_g2c_route_eligibility_artifact.artifact_id,
                baseline.report_artifact.artifact_id,
            ),
            artifact_trace_refs=(
                plan.recomputation_plan_id,
                delta.delta_id,
                affected_result.affected_set_id,
                invalidation_report.invalidation_report_id,
            ),
            prior_root_state={
                "prior_decision": None,
                "prior_decision_id": None,
                "prior_selected_candidate_id": None,
            },
        )
        plan_root_input = plan_root["input"]
        plan_root_result = plan_root["result"]
        plan_root_artifact = plan_root["artifact"]
        assert type(plan_root_input) is RootDecisionInputV01
        assert type(plan_root_result) is RootDecisionResultV01
        assert type(plan_root_artifact) is KernelArtifactV01
        registry = transition_runtime.build_continuous_delta_transition_registry_profile_v01()
        t04, t05, t06, t07 = (
            transitions[3],
            transitions[4],
            transitions[5],
            transitions[6],
        )
        if transition_runtime.validate_continuous_delta_transition_decision_v01(
            t04,
            registry=registry,
            source_artifact=plan_proposed_artifact,
            target_artifact=plan_root_artifact,
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        if plan_root_result.decision != "ACCEPT":
            blocked = _g2e4_project_blocked_plan_artifact_v01(
                plan=plan,
                proposed_artifact=plan_proposed_artifact,
                root_result=plan_root_result,
                root_artifact=plan_root_artifact,
                t06=t06,
                delta=delta,
                source_context=source_context,
            )
            if transition_runtime.validate_continuous_delta_transition_decision_v01(
                t06,
                registry=registry,
                source_artifact=plan_root_artifact,
                target_artifact=blocked,
            ):
                raise ValueError("g2e_recomputation_result_invalid")
            raise ValueError("g2e_root_rejected_recomputation_plan")
        plan_accepted_artifact = _g2e4_project_plan_accepted_artifact_v01(
            plan=plan,
            proposed_artifact=plan_proposed_artifact,
            root_input=plan_root_input,
            root_result=plan_root_result,
            root_artifact=plan_root_artifact,
            t04=t04,
            t05=t05,
            delta=delta,
            source_context=source_context,
        )
        if transition_runtime.validate_continuous_delta_transition_decision_v01(
            t05,
            registry=registry,
            source_artifact=plan_root_artifact,
            target_artifact=plan_accepted_artifact,
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        recomputed_bundle = _g2e4_execute_granular_g2d_v01(
            plan=plan,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
        )
        if transition_runtime.validate_continuous_delta_transition_decision_v01(
            t07,
            registry=registry,
            source_artifact=plan_accepted_artifact,
            target_artifact=recomputed_bundle.report_artifact,
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        recomputed_bindings = _g2e4_recomputed_bindings_v01(
            plan=plan,
            baseline=baseline,
            recomputed=recomputed_bundle,
        )
        preservation_proof, preservation_artifact = _g2e4_preservation_family_v01(
            affected_result=affected_result,
            invalidation_records=invalidation_records,
            source_context=source_context,
            recomputed_bundle=recomputed_bundle,
            recomputed_bindings=recomputed_bindings,
            accepted_plan_artifact=plan_accepted_artifact,
            invalidation_artifact=e3_artifacts["invalidation"],
            delta=delta,
        )
        recomputation_result = _g2e4_build_recomputation_result_v01(
            plan=plan,
            source_context=source_context,
            invalidation_report=invalidation_report,
            recomputed_bundle=recomputed_bundle,
            recomputed_bindings=recomputed_bindings,
            preservation_proof=preservation_proof,
        )
        pre_final_causal_refs = (
            _g2e4_causal_ref_v01(
                producer_actor_id="continuous_delta_runtime_v01",
                source_artifact=e3_artifacts["proposed"],
                output_field="/payload/delta_id",
                consumer_component="continuous_delta_runtime_v01",
                downstream_artifact=e3_artifacts["validated"],
                transition=transitions[0],
                disposition="USED",
                trace_refs=(transitions[0].decision_id, delta.delta_id),
            ),
            _g2e4_causal_ref_v01(
                producer_actor_id="continuous_delta_runtime_v01",
                source_artifact=e3_artifacts["validated"],
                output_field="/payload/delta_id",
                consumer_component="continuous_delta_runtime_v01",
                downstream_artifact=e3_artifacts["affected"],
                transition=transitions[1],
                disposition="USED",
                trace_refs=(transitions[1].decision_id, affected_result.affected_set_id),
            ),
            _g2e4_causal_ref_v01(
                producer_actor_id="continuous_delta_runtime_v01",
                source_artifact=e3_artifacts["affected"],
                output_field="/payload/affected_set_id",
                consumer_component="continuous_delta_runtime_v01",
                downstream_artifact=e3_artifacts["invalidation"],
                transition=transitions[2],
                disposition="USED",
                trace_refs=(
                    transitions[2].decision_id,
                    invalidation_report.invalidation_report_id,
                ),
            ),
            _g2e4_causal_ref_v01(
                producer_actor_id="continuous_delta_runtime_v01",
                source_artifact=plan_proposed_artifact,
                output_field="/payload/recomputation_plan_id",
                consumer_component="root_decision_v01",
                downstream_artifact=plan_root_artifact,
                transition=t04,
                disposition="USED",
                trace_refs=(
                    plan_root_input.decision_input_id,
                    plan_root["packet"].packet_id,
                    t04.decision_id,
                ),
            ),
            _g2e4_causal_ref_v01(
                producer_actor_id="root_decision_v01",
                source_artifact=plan_root_artifact,
                output_field="/payload/selected_candidate_id",
                consumer_component="continuous_delta_runtime_v01",
                downstream_artifact=plan_accepted_artifact,
                transition=t05,
                disposition="USED",
                trace_refs=(
                    plan_root_result.decision_id,
                    plan_accepted_artifact.artifact_id,
                    t05.decision_id,
                ),
            ),
            _g2e4_causal_ref_v01(
                producer_actor_id="continuous_delta_runtime_v01",
                source_artifact=plan_accepted_artifact,
                output_field="/payload/recomputation_plan_id",
                consumer_component="fractal_runtime_v02",
                downstream_artifact=recomputed_bundle.report_artifact,
                transition=t07,
                disposition="USED",
                trace_refs=(
                    t07.decision_id,
                    recomputed_bundle.runtime_trace.trace_id,
                    recomputed_bundle.runtime_report.report_id,
                ),
            ),
        )
        binding_reports = tuple(
            validate_recomputed_artifact_binding_v01(item)
            for item in recomputed_bindings
        )
        preservation_report = validate_preservation_proof_v01(preservation_proof)
        result_structural_report = validate_selective_recomputation_result_v01(
            recomputation_result
        )
        result_context_report = validate_selective_recomputation_result_against_plan_v01(
            recomputation_result,
            plan=plan,
            source_context=source_context,
            delta_source_proposed_artifact=e3_artifacts["proposed"],
            delta_source_artifact=e3_artifacts["validated"],
            dependency_graph_artifact=e3_artifacts["graph"],
            affected_set_artifact=e3_artifacts["affected"],
            invalidation_report_artifact=e3_artifacts["invalidation"],
            plan_proposed_artifact=plan_proposed_artifact,
            plan_root_decision_input=plan_root_input,
            plan_root_decision_result=plan_root_result,
            plan_root_decision_artifact=plan_root_artifact,
            plan_accepted_artifact=plan_accepted_artifact,
            recomputed_g2d_execution_bundle=recomputed_bundle,
            recomputed_bindings=recomputed_bindings,
            preservation_proof=preservation_proof,
            preservation_proof_artifact=preservation_artifact,
            g2e_transition_decisions=transitions,
            g2e_causal_consumption_refs=pre_final_causal_refs,
        )
        pre_final_reports = (
            *pre_plan_reports,
            *binding_reports,
            preservation_report,
            result_structural_report,
            result_context_report,
        )
        if any(item.status != "PASS" for item in pre_final_reports):
            first = next(item for item in pre_final_reports if item.status != "PASS")
            raise ValueError(first.reason_codes[0])
        vv_refs = tuple(
            str(item["vv_report_id"]) for item in recomputed_bundle.post_vv_reports
        )
        final_evidence_refs = _ordered_unique_v01(
            (*vv_refs, *(item.validation_report_id for item in pre_final_reports))
        )
        final_root = _g2e4_root_review_v01(
            phase="FINAL",
            request_id=delta.request_id,
            candidate_id=recomputation_result.recomputation_result_id,
            candidate_plain=selective_recomputation_result_to_plain_data_v01(
                recomputation_result
            ),
            transaction_id=delta.transaction_id,
            target_root_id=delta.owning_root_id,
            topology_ref=recomputed_bundle.topology.topology_id,
            evidence_refs=final_evidence_refs,
            validator_ids=(
                "continuous_delta_result_against_plan_v01",
                "fractal_runtime_execution_bundle_v02",
                "continuous_delta_preservation_v01",
            ),
            policy_id=delta.observed_policy_version,
            time_source_artifact=recomputed_bundle.report_artifact,
            root_kernel=source_context.root_kernel,
            artifact_parent_refs=(
                plan_root_artifact.artifact_id,
                plan_accepted_artifact.artifact_id,
                recomputed_bundle.report_artifact.artifact_id,
                preservation_artifact.artifact_id,
            ),
            artifact_trace_refs=(
                plan_root_result.decision_id,
                recomputation_result.recomputation_result_id,
                recomputed_bundle.runtime_report.report_id,
                preservation_proof.preservation_proof_id,
            ),
            prior_root_state={
                "prior_decision": "ACCEPT",
                "prior_decision_id": plan_root_result.decision_id,
                "prior_selected_candidate_id": plan.recomputation_plan_id,
            },
        )
        final_root_input = final_root["input"]
        final_root_result = final_root["result"]
        final_root_artifact = final_root["artifact"]
        assert type(final_root_input) is RootDecisionInputV01
        assert type(final_root_result) is RootDecisionResultV01
        assert type(final_root_artifact) is KernelArtifactV01
        if final_root_result.decision != "ACCEPT":
            raise ValueError("g2e_root_rejected_recomputation_result")
        t09, t10 = transitions[8], transitions[9]
        if transition_runtime.validate_continuous_delta_transition_decision_v01(
            t09,
            registry=registry,
            source_artifact=recomputed_bundle.report_artifact,
            target_artifact=final_root_artifact,
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        t09_causal = _g2e4_causal_ref_v01(
            producer_actor_id="fractal_runtime_v02",
            source_artifact=recomputed_bundle.report_artifact,
            output_field="/payload/report_id",
            consumer_component="root_decision_v01",
            downstream_artifact=final_root_artifact,
            transition=t09,
            disposition="USED",
            trace_refs=(
                recomputed_bundle.runtime_report.report_id,
                recomputation_result.recomputation_result_id,
                preservation_proof.preservation_proof_id,
                final_root_input.decision_input_id,
                final_root["packet"].packet_id,
                t09.decision_id,
            ),
        )
        trace_causal_refs = (*pre_final_causal_refs, t09_causal)
        source_artifact_ids = (
            e3_artifacts["proposed"].artifact_id,
            e3_artifacts["validated"].artifact_id,
            e3_artifacts["graph"].artifact_id,
            e3_artifacts["affected"].artifact_id,
            e3_artifacts["invalidation"].artifact_id,
            plan_proposed_artifact.artifact_id,
            plan_accepted_artifact.artifact_id,
            preservation_artifact.artifact_id,
            recomputed_bundle.report_artifact.artifact_id,
        )
        downstream_artifact_ids = (
            plan_root_artifact.artifact_id,
            recomputed_bundle.report_artifact.artifact_id,
            final_root_artifact.artifact_id,
        )
        runtime_trace = build_continuous_delta_runtime_trace_v01(
            delta_id=delta.delta_id,
            graph_id=dependency_graph.graph_id,
            affected_set_id=affected_result.affected_set_id,
            invalidation_report_id=invalidation_report.invalidation_report_id,
            preservation_proof_id=preservation_proof.preservation_proof_id,
            recomputation_plan_id=plan.recomputation_plan_id,
            recomputation_result_id=recomputation_result.recomputation_result_id,
            plan_root_decision_input_id=plan_root_input.decision_input_id,
            plan_root_decision_id=plan_root_result.decision_id,
            final_root_decision_input_id=final_root_input.decision_input_id,
            final_root_decision_id=final_root_result.decision_id,
            ordered_transition_decision_ids=tuple(
                item.decision_id for item in transitions[:9]
            ),
            ordered_causal_ref_ids=tuple(
                _g2e4_causal_ref_id_v01(item) for item in trace_causal_refs
            ),
            ordered_source_artifact_ids=source_artifact_ids,
            ordered_downstream_artifact_ids=downstream_artifact_ids,
            provider_calls=0,
            model_calls=0,
            network_calls=0,
            connector_calls=0,
            external_drs_calls=0,
            real_world_effects_count=0,
        )
        runtime_report = build_continuous_delta_runtime_report_v01(
            report_version="v0.1",
            profile_id="continuous_delta_runtime_v01",
            ordered_source_binding_ids=tuple(
                item.source_binding_id for item in source_bindings
            ),
            baseline_report_id=baseline.runtime_report.report_id,
            delta_id=delta.delta_id,
            graph_id=dependency_graph.graph_id,
            affected_set_id=affected_result.affected_set_id,
            invalidation_report_id=invalidation_report.invalidation_report_id,
            preservation_proof_id=preservation_proof.preservation_proof_id,
            recomputation_plan_id=plan.recomputation_plan_id,
            recomputation_result_id=recomputation_result.recomputation_result_id,
            trace_id=runtime_trace.trace_id,
            plan_root_decision_input_id=plan_root_input.decision_input_id,
            plan_root_decision_id=plan_root_result.decision_id,
            final_root_decision_input_id=final_root_input.decision_input_id,
            final_root_decision_id=final_root_result.decision_id,
            changed_count=(
                len(changed_field_bindings) + len(changed_artifact_bindings)
            ),
            directly_affected_count=len(
                affected_result.ordered_directly_affected_ids
            ),
            transitively_affected_count=len(
                affected_result.ordered_transitively_affected_ids
            ),
            invalidated_count=len(
                invalidation_report.ordered_invalidated_artifact_ids
            ),
            recomputed_count=len(recomputed_bindings),
            preserved_count=len(preservation_proof.ordered_preserved_artifact_ids),
            unresolved_count=0,
            report_status="PASS",
            reason_codes=(),
            root_review_required=True,
            provider_calls=0,
            model_calls=0,
            network_calls=0,
            connector_calls=0,
            external_drs_calls=0,
            action_commit_packets_created=0,
            permissions_created=0,
            receipts_created=0,
            final_outputs_created=0,
            drs_writes=0,
            authority_created_count=0,
            real_world_effects_count=0,
        )
        runtime_report_artifact = _g2e4_runtime_report_artifact_v01(
            report=runtime_report,
            accepted_plan_artifact=plan_accepted_artifact,
            recomputed_report_artifact=recomputed_bundle.report_artifact,
            preservation_proof_artifact=preservation_artifact,
            final_root_artifact=final_root_artifact,
            invalidation_report_artifact=e3_artifacts["invalidation"],
        )
        if transition_runtime.validate_continuous_delta_transition_decision_v01(
            t10,
            registry=registry,
            source_artifact=final_root_artifact,
            target_artifact=runtime_report_artifact,
        ):
            raise ValueError("g2e_recomputation_result_invalid")
        t10_causal = _g2e4_causal_ref_v01(
            producer_actor_id="root_decision_v01",
            source_artifact=final_root_artifact,
            output_field="/payload/selected_candidate_id",
            consumer_component="continuous_delta_runtime_v01",
            downstream_artifact=runtime_report_artifact,
            transition=t10,
            disposition="USED",
            trace_refs=(
                final_root_result.decision_id,
                runtime_report.report_id,
                t10.decision_id,
            ),
        )
        trace_report = validate_continuous_delta_runtime_trace_v01(runtime_trace)
        runtime_report_validation = validate_continuous_delta_runtime_report_v01(
            runtime_report
        )
        final_validation_reports = (
            *pre_final_reports,
            trace_report,
            runtime_report_validation,
        )
        if any(item.status != "PASS" for item in final_validation_reports):
            first = next(
                item for item in final_validation_reports if item.status != "PASS"
            )
            raise ValueError(first.reason_codes[0])
        bundle = build_continuous_delta_execution_bundle_v01(
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            delta=delta,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
            affected_request=affected_request,
            affected_result=affected_result,
            invalidation_records=invalidation_records,
            invalidation_report=invalidation_report,
            delta_source_proposed_artifact=e3_artifacts["proposed"],
            delta_source_artifact=e3_artifacts["validated"],
            dependency_graph_artifact=e3_artifacts["graph"],
            affected_set_artifact=e3_artifacts["affected"],
            invalidation_report_artifact=e3_artifacts["invalidation"],
            recomputation_plan=plan,
            plan_proposed_artifact=plan_proposed_artifact,
            plan_root_decision_input=plan_root_input,
            plan_root_decision_result=plan_root_result,
            plan_root_decision_artifact=plan_root_artifact,
            plan_accepted_artifact=plan_accepted_artifact,
            recomputed_g2d_execution_bundle=recomputed_bundle,
            recomputed_bindings=recomputed_bindings,
            preservation_proof=preservation_proof,
            preservation_proof_artifact=preservation_artifact,
            recomputation_result=recomputation_result,
            g2e_validation_reports=final_validation_reports,
            g2e_transition_decisions=transitions,
            g2e_causal_consumption_refs=(*trace_causal_refs, t10_causal),
            final_root_decision_input=final_root_input,
            final_root_decision_result=final_root_result,
            final_root_decision_artifact=final_root_artifact,
            runtime_trace=runtime_trace,
            runtime_report=runtime_report,
            runtime_report_artifact=runtime_report_artifact,
        )
        final_report = validate_continuous_delta_execution_bundle_v01(bundle)
        if final_report.status != "PASS":
            raise ValueError(final_report.reason_codes[0])
        return bundle, final_report
    except Exception as exc:
        return None, _g2e4_failure_report_v01(exc)


def validate_selective_recomputation_result_against_plan_v01(
    value: SelectiveRecomputationResultV01,
    *,
    plan: SelectiveRecomputationPlanV01,
    source_context: ContinuousDeltaSourceContextV01,
    delta_source_proposed_artifact: KernelArtifactV01,
    delta_source_artifact: KernelArtifactV01,
    dependency_graph_artifact: KernelArtifactV01,
    affected_set_artifact: KernelArtifactV01,
    invalidation_report_artifact: KernelArtifactV01,
    plan_proposed_artifact: KernelArtifactV01,
    plan_root_decision_input: RootDecisionInputV01,
    plan_root_decision_result: RootDecisionResultV01,
    plan_root_decision_artifact: KernelArtifactV01,
    plan_accepted_artifact: KernelArtifactV01,
    recomputed_g2d_execution_bundle: FractalRuntimeExecutionBundleV02,
    recomputed_bindings: tuple[RecomputedArtifactBindingV01, ...],
    preservation_proof: PreservationProofV01,
    preservation_proof_artifact: KernelArtifactV01,
    g2e_transition_decisions: tuple[TransitionDecisionV01, ...],
    g2e_causal_consumption_refs: tuple[CausalConsumptionRefV01, ...],
) -> ContinuousDeltaValidationReportV01:
    return _validate_selective_recomputation_result_against_plan_impl_v01(
        value,
        plan=plan,
        source_context=source_context,
        delta_source_proposed_artifact=delta_source_proposed_artifact,
        delta_source_artifact=delta_source_artifact,
        dependency_graph_artifact=dependency_graph_artifact,
        affected_set_artifact=affected_set_artifact,
        invalidation_report_artifact=invalidation_report_artifact,
        plan_proposed_artifact=plan_proposed_artifact,
        plan_root_decision_input=plan_root_decision_input,
        plan_root_decision_result=plan_root_decision_result,
        plan_root_decision_artifact=plan_root_decision_artifact,
        plan_accepted_artifact=plan_accepted_artifact,
        recomputed_g2d_execution_bundle=recomputed_g2d_execution_bundle,
        recomputed_bindings=recomputed_bindings,
        preservation_proof=preservation_proof,
        preservation_proof_artifact=preservation_proof_artifact,
        g2e_transition_decisions=g2e_transition_decisions,
        g2e_causal_consumption_refs=g2e_causal_consumption_refs,
    )


def run_continuous_delta_runtime_v01(
    *,
    source_context: ContinuousDeltaSourceContextV01,
    source_bindings: tuple[DeltaSourceBindingV01, ...],
    changed_field_bindings: tuple[ChangedFieldBindingV01, ...],
    changed_artifact_bindings: tuple[ChangedArtifactBindingV01, ...],
    delta: WorldStateDeltaV01,
    dependency_edges: tuple[DeltaDependencyEdgeV01, ...],
    dependency_graph: DependencyGraphIndexV01,
) -> tuple[
    ContinuousDeltaExecutionBundleV01 | None,
    ContinuousDeltaValidationReportV01,
]:
    try:
        affected_request = build_affected_set_request_v01(
            delta=delta,
            graph=dependency_graph,
            trace_refs=(delta.delta_id, dependency_graph.graph_id),
        )
        affected_result = compute_affected_set_v01(
            request=affected_request,
            delta=delta,
            graph=dependency_graph,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            baseline_source_artifacts=source_context.baseline_source_artifacts,
            observed_source_artifacts=source_context.observed_source_artifacts,
        )
        invalidation_records, invalidation_report = derive_invalidation_report_v01(
            affected_set=affected_result,
            delta=delta,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        plan = build_selective_recomputation_plan_from_affected_set_v01(
            delta=delta,
            affected_set=affected_result,
            invalidation_records=invalidation_records,
            invalidation_report=invalidation_report,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
        )
        return execute_selective_recomputation_v01(
            plan=plan,
            source_context=source_context,
            source_bindings=source_bindings,
            changed_field_bindings=changed_field_bindings,
            changed_artifact_bindings=changed_artifact_bindings,
            delta=delta,
            dependency_edges=dependency_edges,
            dependency_graph=dependency_graph,
            affected_request=affected_request,
            affected_result=affected_result,
            invalidation_records=invalidation_records,
            invalidation_report=invalidation_report,
        )
    except Exception as exc:
        return None, _g2e4_failure_report_v01(exc)


__all__ = (
    "DeltaSourceBindingV01",
    "ChangedFieldBindingV01",
    "ChangedArtifactBindingV01",
    "WorldStateDeltaV01",
    "DependencyFingerprintProfileV01",
    "DeltaDependencyEdgeV01",
    "DependencyGraphIndexV01",
    "AffectedSetRequestV01",
    "AffectedSetResultV01",
    "ArtifactInvalidationRecordV01",
    "InvalidationReportV01",
    "PreservationProofV01",
    "SelectiveRecomputationPlanV01",
    "RecomputedArtifactBindingV01",
    "SelectiveRecomputationResultV01",
    "ContinuousDeltaRuntimeTraceV01",
    "ContinuousDeltaRuntimeReportV01",
    "ContinuousDeltaValidationReportV01",
    "ContinuousDeltaSourceContextV01",
    "ContinuousDeltaExecutionBundleV01",
    "build_delta_source_binding_v01",
    "validate_delta_source_binding_v01",
    "delta_source_binding_to_plain_data_v01",
    "rebuild_delta_source_binding_identity_v01",
    "build_changed_field_binding_v01",
    "validate_changed_field_binding_v01",
    "changed_field_binding_to_plain_data_v01",
    "rebuild_changed_field_binding_identity_v01",
    "build_changed_artifact_binding_v01",
    "validate_changed_artifact_binding_v01",
    "changed_artifact_binding_to_plain_data_v01",
    "rebuild_changed_artifact_binding_identity_v01",
    "build_world_state_delta_v01",
    "validate_world_state_delta_v01",
    "world_state_delta_to_plain_data_v01",
    "rebuild_world_state_delta_identity_v01",
    "build_dependency_fingerprint_profile_v01",
    "validate_dependency_fingerprint_profile_v01",
    "dependency_fingerprint_profile_to_plain_data_v01",
    "rebuild_dependency_fingerprint_profile_identity_v01",
    "build_continuous_delta_validation_report_v01",
    "validate_continuous_delta_validation_report_v01",
    "continuous_delta_validation_report_to_plain_data_v01",
    "rebuild_continuous_delta_validation_report_identity_v01",
    "build_delta_dependency_edge_v01",
    "validate_delta_dependency_edge_v01",
    "delta_dependency_edge_to_plain_data_v01",
    "rebuild_delta_dependency_edge_identity_v01",
    "build_dependency_graph_index_v01",
    "validate_dependency_graph_index_v01",
    "dependency_graph_index_to_plain_data_v01",
    "rebuild_dependency_graph_index_identity_v01",
    "build_affected_set_request_v01",
    "validate_affected_set_request_v01",
    "affected_set_request_to_plain_data_v01",
    "rebuild_affected_set_request_identity_v01",
    "build_affected_set_result_v01",
    "validate_affected_set_result_v01",
    "affected_set_result_to_plain_data_v01",
    "rebuild_affected_set_result_identity_v01",
    "build_dependency_fingerprint_v01",
    "validate_dependency_fingerprint_against_sources_v01",
    "project_integrity_replay_dependency_edges_v01",
    "compute_affected_set_v01",
    "validate_affected_set_against_graph_v01",
    "build_artifact_invalidation_record_v01",
    "validate_artifact_invalidation_record_v01",
    "artifact_invalidation_record_to_plain_data_v01",
    "rebuild_artifact_invalidation_record_identity_v01",
    "build_invalidation_report_v01",
    "validate_invalidation_report_v01",
    "invalidation_report_to_plain_data_v01",
    "rebuild_invalidation_report_identity_v01",
    "build_preservation_proof_v01",
    "validate_preservation_proof_v01",
    "preservation_proof_to_plain_data_v01",
    "rebuild_preservation_proof_identity_v01",
    "build_continuous_delta_source_context_v01",
    "validate_continuous_delta_source_context_v01",
    "derive_invalidation_report_v01",
    "validate_invalidation_report_against_sources_v01",
    "prove_unaffected_artifact_preservation_v01",
    "build_selective_recomputation_plan_v01",
    "validate_selective_recomputation_plan_v01",
    "selective_recomputation_plan_to_plain_data_v01",
    "rebuild_selective_recomputation_plan_identity_v01",
    "build_recomputed_artifact_binding_v01",
    "validate_recomputed_artifact_binding_v01",
    "recomputed_artifact_binding_to_plain_data_v01",
    "rebuild_recomputed_artifact_binding_identity_v01",
    "build_selective_recomputation_result_v01",
    "validate_selective_recomputation_result_v01",
    "selective_recomputation_result_to_plain_data_v01",
    "rebuild_selective_recomputation_result_identity_v01",
    "build_continuous_delta_runtime_trace_v01",
    "validate_continuous_delta_runtime_trace_v01",
    "continuous_delta_runtime_trace_to_plain_data_v01",
    "rebuild_continuous_delta_runtime_trace_identity_v01",
    "build_continuous_delta_runtime_report_v01",
    "validate_continuous_delta_runtime_report_v01",
    "continuous_delta_runtime_report_to_plain_data_v01",
    "rebuild_continuous_delta_runtime_report_identity_v01",
    "build_continuous_delta_execution_bundle_v01",
    "validate_continuous_delta_execution_bundle_v01",
    "build_selective_recomputation_plan_from_affected_set_v01",
    "validate_selective_recomputation_plan_against_sources_v01",
    "execute_selective_recomputation_v01",
    "validate_selective_recomputation_result_against_plan_v01",
    "run_continuous_delta_runtime_v01",
)
