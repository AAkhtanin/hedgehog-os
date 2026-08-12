"""Deterministic G2-E Continuous Delta Runtime v0.1 contracts through E2.

The module defines frozen data and deterministic structural/currentness proofs.
No G2-E object is truth, Root authority, permission, execution, persistence,
or a real-world effect.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, fields, replace
from datetime import datetime
import hashlib
import re
import unicodedata

from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01,
    KernelArtifactV01,
    build_kernel_artifact_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.execution_mode_router_v01 import ExecutionModeSourceContextV01
from hedgehog.kernel.fractal_runtime_v02 import FractalRuntimeExecutionBundleV02
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
)
from hedgehog.kernel.transition_registry_v01 import TransitionDecisionV01


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
        parent_refs=(
            baseline_route_artifact.artifact_id,
            baseline_g2d_report_artifact.artifact_id,
            *(artifact.artifact_id for artifact in baseline_source_artifacts),
            *(artifact.artifact_id for artifact in observed_source_artifacts),
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
        parent_refs=(
            proposed_source_artifact.artifact_id,
            baseline_route_artifact.artifact_id,
            baseline_g2d_report_artifact.artifact_id,
            *(artifact.artifact_id for artifact in baseline_source_artifacts),
            *(artifact.artifact_id for artifact in observed_source_artifacts),
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
        trace_refs=affected_result.trace_refs + (
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
)
