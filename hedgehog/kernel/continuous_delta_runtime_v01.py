"""Deterministic structural contracts for G2-E Continuous Delta Runtime v0.1.

G2-E1 defines frozen data, identities, structural validation, and declarations
only.  A structural PASS is not source acceptance, truth, Root authority,
permission, execution, persistence, or a real-world effect.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime
import hashlib
import re
import unicodedata

from hedgehog.kernel.abi_v01 import CausalConsumptionRefV01, KernelArtifactV01
from hedgehog.kernel.execution_mode_router_v01 import ExecutionModeSourceContextV01
from hedgehog.kernel.fractal_runtime_v02 import FractalRuntimeExecutionBundleV02
from hedgehog.kernel.integrity_replay_v01 import (
    ArtifactManifestV01,
    ReplayVerificationResultV01,
    canonical_json_bytes_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
)
from hedgehog.kernel.transition_registry_v01 import TransitionDecisionV01


MODULE_ID = "continuous_delta_runtime_v01"
SLICE_ID = "gate2_g2e1_structural_contracts"
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


def _timestamp_valid(value: object) -> bool:
    if type(value) is not str or _TIMESTAMP_PATTERN.fullmatch(value) is None:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


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
)
