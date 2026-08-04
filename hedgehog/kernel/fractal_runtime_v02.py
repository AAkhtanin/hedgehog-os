"""Deterministic structural contracts for Fractal Runtime v0.2 G2-D1.

This module owns canonical data, identity, serialization, and structural
validation only.  It performs no scheduling, provider, model, network,
connector, filesystem, clock, random, DRS, permission, packet, receipt,
FinalOutput, authority, or effect operation.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass, fields as _fields, replace as _replace
import hashlib
import re
import types
import unicodedata
from typing import get_args as _get_args, get_origin as _get_origin, get_type_hints as _get_type_hints

from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01,
    KernelArtifactV01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_to_plain_dict_v01,
)
from hedgehog.kernel.execution_mode_router_v01 import (
    ExecutionModeProposalV01,
    ExecutionModeRouterInputV01,
    ExecutionModeSourceContextV01,
    RootExecutionModeDecisionV01,
    RootExecutionModeReviewInputV01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
)
from hedgehog.kernel.transition_registry_v01 import (
    TransitionDecisionV01,
    TransitionRegistryV01,
)


MODULE_ID = "kernel_fractal_runtime_v02"
SLICE_ID = "gate2_g2d1_fractal_runtime_canonical_structural_contracts"
FRACTAL_RUNTIME_VERSION = "v0.2"

TOTAL_G2D_TYPE_COUNT = 20
SERIALIZED_IDENTITY_TYPE_COUNT = 18
RUNTIME_ONLY_CONTEXT_TYPE_COUNT = 2
SCHEMA_DEFINITION_COUNT = 18
FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT = 110
FRACTAL_RUNTIME_TRANSITION_PUBLIC_FUNCTION_COUNT = 6
TOTAL_G2D_PUBLIC_FUNCTION_COUNT = 116
PUBLIC_G2D_REASON_COUNT = 220
VALIDATION_TARGET_COUNT = 34
FAILURE_STAGE_COUNT = 30
DIRECT_PACKAGE_G2D_ATTRIBUTE_COUNT = 136
D1_MODULE_PUBLIC_FUNCTION_COUNT = 74
D2_MODULE_PUBLIC_FUNCTION_COUNT = 81
D3_MODULE_PUBLIC_FUNCTION_COUNT = 90
D4_MODULE_PUBLIC_FUNCTION_COUNT = 110

TOPOLOGY_ELIGIBLE_MODES = (
    "memory_informed",
    "local_slm",
    "cloud_llm",
    "full_semantic",
    "full_fractal",
)
NODE_KINDS = (
    "MEMORY_CONTEXT",
    "LOCAL_MODEL_DECLARATION",
    "CLOUD_MODEL_DECLARATION",
    "SEMANTIC_ACTOR",
    "SEMANTIC_MERGE",
    "FRACTAL_CELL",
    "FRACTAL_MERGE",
    "POST_VV",
    "GT_ADVISORY",
    "PARENT_RETURN",
)
EDGE_KINDS = (
    "DATA_DEPENDENCY",
    "CONTROL_DEPENDENCY",
    "PARENT_CHILD",
    "VALIDATION",
    "RETURN",
)
ASSIGNMENT_KINDS = (
    "LOCAL_DETERMINISTIC",
    "LOCAL_MODEL_DECLARED",
    "CLOUD_MODEL_DECLARED",
    "SEMANTIC_ACTOR",
    "FRACTAL_CHILD",
    "VALIDATOR",
    "ADVISORY",
    "PARENT_RETURN",
)
CELL_BINDING_CLASSES = ("CURRENT_CELL", "CURRENT_CELL_CHILD_SLOT")
SCOPE_BINDING_CLASSES = ("CURRENT_CELL_SCOPE", "PERMITTED_CHILD_SCOPE")
BUDGET_BINDING_CLASSES = ("CURRENT_CELL_BUDGET", "CHILD_ALLOCATION_BUDGET")
BUDGET_STATES = ("ALLOCATED", "ACTIVE", "FINAL")
BUDGET_SCOPES = ("ROOT_GLOBAL_AND_CELL", "CHILD_CELL_LOCAL")
BUDGET_EVENT_KINDS = (
    "INITIAL_ALLOCATION",
    "ACTIVATE",
    "CELL_CREATE",
    "START_NODE",
    "FINISH_NODE",
    "REVISE",
    "CHILD_AGGREGATE",
    "FINALIZE",
)
INPUT_REF_DERIVATION_CLASSES = (
    "SOURCE_CONTEXT",
    "PREDECESSOR_OUTPUTS",
    "FAN_IN_OUTPUTS_0_1_2",
    "PREDECESSOR_AND_CHILD_SLOT_1",
    "PREDECESSOR_AND_CHILD_SLOT_2",
    "FAN_IN_CHILD_SLOT_RETURNS_1_2",
)
CELL_PROJECTION_CLASSES = ("ROOT_CELL_PROJECTION", "FRACTAL_LEAF_PROJECTION")
QUEUE_STATES = (
    "PENDING",
    "READY",
    "RUNNING",
    "VALIDATING",
    "COMPLETED",
    "DEGRADED",
    "BLOCKED",
    "NEEDS_USER",
    "DEADEND",
)
NODE_TERMINAL_OUTCOMES = ("COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND")
CELL_OUTCOMES = ("COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND")
VALIDATION_STATUSES = ("PASS", "FAIL_CLOSED")
POLICY_PROFILE_IDS = ("fractal_runtime_policy_g2d_v02",)
PROFILE_IDS = ("fractal_runtime_g2d_profile_v02",)
TOPOLOGY_VERSIONS = ("v0.2",)
REPORT_VERSIONS = ("v0.2",)
EXPECTED_OUTPUT_KINDS = (
    "MEMORY_CONTEXT_OUTPUT",
    "LOCAL_MODEL_DECLARATION_OUTPUT",
    "CLOUD_MODEL_DECLARATION_OUTPUT",
    "SEMANTIC_ACTOR_OUTPUT",
    "SEMANTIC_MERGE_OUTPUT",
    "FRACTAL_CELL_OUTPUT",
    "FRACTAL_MERGE_OUTPUT",
    "POST_VV_REPORT",
    "GT_ADVISORY_REPORT",
    "PARENT_RETURN_EVIDENCE",
)
FORBIDDEN_OUTPUT_KINDS = (
    "FINAL_OUTPUT",
    "ROOT_FINAL_OUTPUT",
    "ACTION_PERMISSION",
    "ACTION_COMMIT_PACKET",
    "EVIDENCE_RECEIPT",
    "EFFECT_REQUEST",
    "CONNECTOR_COMMAND",
    "DRS_WRITE",
    "PARENT_ARCHITECT_COMMAND",
    "ROOT_AUTHORITY_CLAIM",
)
FAILURE_STAGES = (
    "NONE",
    "SOURCE_CONTEXT",
    "POLICY",
    "SOURCE_BINDING",
    "ROOT_CELL_ID",
    "TOPOLOGY_SEED",
    "BUDGET",
    "NODE",
    "EDGE",
    "ASSIGNMENT",
    "TOPOLOGY",
    "QUEUE",
    "SCOPE",
    "CELL_INPUT",
    "RESULT_PROPOSAL",
    "CELL_RESULT_PRECONDITIONS",
    "POST_VV",
    "GT",
    "CELL_RESULT",
    "REVISE",
    "PARTIAL_FAILURE",
    "BACKPRESSURE",
    "RUNTIME_TRACE",
    "ABI",
    "TRANSITION",
    "CAUSAL_CONSUMPTION",
    "CAUSAL_COUNTERFACTUAL",
    "PARENT_RETURN",
    "REPORT",
    "COMPLETE_PROFILE",
)
PARENT_DISPOSITIONS = ("COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND")
BACKPRESSURE_REASONS = ("PARALLELISM_CAPACITY_EXHAUSTED",)
VALIDATION_TARGETS = (
    "FractalRuntimePolicyV02",
    "FractalRuntimeBudgetV02",
    "RuntimeTopologySourceBindingV02",
    "RuntimeTopologySeedV02",
    "RuntimeTopologyNodeV02",
    "RuntimeTopologyEdgeV02",
    "RuntimeAssignmentV02",
    "RuntimeExecutionTopologyV02",
    "ParentChildScopeProjectionV02",
    "FractalCellInputV02",
    "FractalCellQueueEntryV02",
    "FractalReviseObservationV02",
    "FractalPartialFailureRecordV02",
    "FractalBackpressureStateV02",
    "FractalCellResultV02",
    "FractalRuntimeTraceV02",
    "FractalRuntimeReportV02",
    "SOURCE_CONTEXT_STRUCTURAL",
    "SOURCE_BINDING_AGAINST_G2C",
    "TOPOLOGY_AGAINST_SOURCES",
    "SCOPE_PROJECTION_AGAINST_SOURCES",
    "CELL_INPUT_AGAINST_SOURCES",
    "RESULT_PROPOSAL",
    "POST_VV_REPORT",
    "GT_ADVISORY_REPORT",
    "CELL_RESULT_PRECONDITIONS",
    "RUNTIME_REPORT_AGAINST_SOURCES",
    "STAGE_D_A",
    "STAGE_D_B",
    "STAGE_D_C",
    "ABI_PROFILE",
    "CAUSAL_CONSUMPTION",
    "CAUSAL_COUNTERFACTUAL",
    "COMPLETE_PROFILE",
)
RUNTIME_OUTCOMES = ("COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND")
REPORT_STATUSES = ("PASS",)
EXECUTOR_COMPONENT_IDS = (
    "fractal_runtime_v02",
    "fractal_scheduler_v02",
    "post_vv_v01",
    "gt_validator_v01",
    "parent_return_v02",
)
SCOPE_RELATIONS = ("EQUAL", "NARROWER")
BUDGET_RELATIONS = ("ROOT_BUDGET", "CHILD_BUDGET")
QUEUE_PREDECESSOR_RELATIONS = ("INITIAL_NONE", "EXACT_IMMEDIATE_PREDECESSOR")
CAUSAL_DECISION_EFFECTS = (
    "TOPOLOGY_SELECTION",
    "TOPOLOGY_SCOPE",
    "CHILD_ACTIVATION",
    "CELL_RESULT_OUTPUT",
    "CELL_RESULT_EVIDENCE",
    "PARENT_CELL_AGGREGATION",
    "RUNTIME_REPORT_AGGREGATION",
    "RUNTIME_OUTCOME_SELECTION",
    "UNUSED_ADVISORY",
    "CHILD_RESULT_RETURN_BINDING",
    "CHILD_RESULT_TERMINAL_MAPPING",
    "CELL_TERMINAL_OUTCOME",
)
CAUSAL_DISPOSITIONS = ("USED", "REJECTED", "IGNORED_WITH_REASON", "BLOCKED_BY_GATE")

NODE_OUTPUT_KIND_ROWS_V02 = (
    ("MEMORY_CONTEXT", "MEMORY_CONTEXT_OUTPUT"),
    ("LOCAL_MODEL_DECLARATION", "LOCAL_MODEL_DECLARATION_OUTPUT"),
    ("CLOUD_MODEL_DECLARATION", "CLOUD_MODEL_DECLARATION_OUTPUT"),
    ("SEMANTIC_ACTOR", "SEMANTIC_ACTOR_OUTPUT"),
    ("SEMANTIC_MERGE", "SEMANTIC_MERGE_OUTPUT"),
    ("FRACTAL_CELL", "FRACTAL_CELL_OUTPUT"),
    ("FRACTAL_MERGE", "FRACTAL_MERGE_OUTPUT"),
    ("POST_VV", "POST_VV_REPORT"),
    ("GT_ADVISORY", "GT_ADVISORY_REPORT"),
    ("PARENT_RETURN", "PARENT_RETURN_EVIDENCE"),
)
NODE_OUTPUT_KIND_BY_NODE_KIND_V02 = dict(NODE_OUTPUT_KIND_ROWS_V02)

CAP_RUNTIME = "capability:g2d:local_runtime:v02"
CAP_POST_VV = "capability:g2d:post_vv:v02"
CAP_GT = "capability:g2d:gt_advisory:v02"
CAP_PARENT_RETURN = "capability:g2d:parent_return:v02"
CAP_FRACTAL_CHILD = "capability:g2d:fractal_child:v02"
LOCAL_CAPS = (CAP_RUNTIME, CAP_POST_VV, CAP_GT, CAP_PARENT_RETURN, CAP_FRACTAL_CHILD)


@_dataclass(frozen=True)
class FractalRuntimePolicyV02:
    policy_id: str
    policy_profile_id: str
    policy_version: str
    allowed_modes: tuple[str, ...]
    allowed_node_kinds: tuple[str, ...]
    allowed_edge_kinds: tuple[str, ...]
    allowed_assignment_kinds: tuple[str, ...]
    recursive_mode: str
    recursive_capability_id: str
    allowed_capability_ids: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    permitted_child_scope_refs: tuple[str, ...]
    reference_child_count: int
    queue_profile_id: str
    budget_profile_id: str
    max_depth: int
    max_fan_out: int
    max_total_cells: int
    max_parallelism: int
    max_revise_count: int
    max_consecutive_no_progress: int
    max_wall_time_units: int
    max_token_budget: int
    max_provider_calls: int
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalRuntimeBudgetV02:
    budget_id: str
    policy_id: str
    topology_seed_id: str
    allocation_parent_budget_id: str | None
    predecessor_budget_id: str | None
    owning_cell_id: str
    budget_scope: str
    budget_state: str
    budget_event_kind: str
    budget_event_ref: str
    max_depth: int
    max_fan_out: int
    max_total_cells: int
    max_parallelism: int
    max_revise_count: int
    max_wall_time_units: int
    max_token_budget: int
    max_provider_calls: int
    consumed_wall_time_units: int
    consumed_token_budget: int
    consumed_provider_calls: int
    consumed_cell_count: int
    consumed_revise_count: int
    current_parallelism: int
    remaining_wall_time_units: int
    remaining_token_budget: int
    remaining_provider_calls: int
    remaining_cell_count: int
    remaining_revise_count: int
    remaining_parallel_slots: int
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class RuntimeTopologySourceBindingV02:
    source_binding_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    accepted_mode: str
    accepted_scope_ref: str
    route_eligibility_artifact_id: str
    route_eligibility_artifact_sha256: str
    source_decision_artifact_id: str
    source_proposal_artifact_id: str
    selected_local_mode_profile_id: str
    selected_feasibility_row_id: str
    selected_safe_depth_rank: int
    selected_expected_cost_units: int
    required_downstream_capability_ids: tuple[str, ...]
    source_mode_profile_set_id: str
    source_policy_snapshot_id: str
    source_capability_snapshot_id: str
    permitted_narrower_scope_refs: tuple[str, ...]
    source_root_decision_result_id: str
    source_root_transition_decision_id: str
    proposal_transition_decision_id: str
    post_root_transition_decision_id: str
    transition_registry_id: str
    g2c_abi_profile_id: str
    downstream_action_packet_required: bool
    runtime_policy_id: str
    source_time_envelope_ref: str
    source_trace_refs: tuple[str, ...]
    source_parent_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class RuntimeTopologySeedV02:
    topology_seed_id: str
    seed_version: str
    profile_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    accepted_mode: str
    accepted_scope_ref: str
    source_binding_id: str
    runtime_policy_id: str
    root_cell_id: str
    source_time_envelope_ref: str
    trace_refs: tuple[str, ...]
    parent_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class RuntimeTopologyNodeV02:
    node_id: str
    topology_seed_id: str
    accepted_mode: str
    node_kind: str
    canonical_index: int
    depth: int
    scope_ref: str
    cell_binding_class: str
    scope_binding_class: str
    budget_binding_class: str
    required_capability_ids: tuple[str, ...]
    allowed_capability_ids: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    input_ref_derivation_class: str
    input_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    expected_output_kind: str
    required: bool
    recursive_expansion_allowed: bool
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class RuntimeTopologyEdgeV02:
    edge_id: str
    topology_seed_id: str
    source_node_id: str
    target_node_id: str
    edge_kind: str
    canonical_index: int
    cell_projection_class: str
    required: bool
    evidence_flow_allowed: bool
    authority_flow_allowed: bool
    trace_refs: tuple[str, ...]
    root_review_required: bool


@_dataclass(frozen=True)
class RuntimeAssignmentV02:
    assignment_id: str
    topology_seed_id: str
    node_id: str
    canonical_index: int
    assignment_kind: str
    executor_component_id: str
    capability_ids: tuple[str, ...]
    cell_binding_class: str
    scope_binding_class: str
    budget_binding_class: str
    provider_call_allowed: bool
    network_call_allowed: bool
    connector_call_allowed: bool
    trace_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    effect_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class RuntimeExecutionTopologyV02:
    topology_id: str
    topology_version: str
    topology_seed_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    accepted_mode: str
    accepted_scope_ref: str
    source_binding_id: str
    source_route_eligibility_artifact_id: str
    source_root_decision_artifact_id: str
    source_proposal_artifact_id: str
    runtime_policy_id: str
    ordered_node_ids: tuple[str, ...]
    ordered_edge_ids: tuple[str, ...]
    ordered_assignment_ids: tuple[str, ...]
    root_cell_id: str
    global_budget_id: str
    time_envelope_ref: str
    trace_refs: tuple[str, ...]
    parent_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    provider_calls: int
    network_calls: int
    real_world_effects_count: int


@_dataclass(frozen=True)
class ParentChildScopeProjectionV02:
    projection_id: str
    topology_id: str
    parent_cell_id: str
    child_cell_id: str
    parent_scope_ref: str
    child_scope_ref: str
    scope_relation: str
    budget_relation: str
    parent_allowed_capability_ids: tuple[str, ...]
    child_allowed_capability_ids: tuple[str, ...]
    parent_forbidden_claims: tuple[str, ...]
    child_forbidden_claims: tuple[str, ...]
    parent_ttl_units: int
    child_ttl_units: int
    parent_budget_id: str
    child_budget_id: str
    global_budget_id: str
    child_depth: int
    parent_lineage_refs: tuple[str, ...]
    child_lineage_refs: tuple[str, ...]
    proof_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    final_output_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalCellInputV02:
    cell_input_id: str
    topology_id: str
    cell_id: str
    parent_cell_id: str | None
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    accepted_mode: str
    scope_projection_id: str | None
    scope_ref: str
    cell_budget_id: str
    global_budget_id: str
    ordered_initial_queue_entry_ids: tuple[str, ...]
    ordered_required_queue_entry_ids: tuple[str, ...]
    cell_depth: int
    requested_child_count: int
    ordered_planned_child_cell_ids: tuple[str, ...]
    ordered_node_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    context_refs: tuple[str, ...]
    required_output_kinds: tuple[str, ...]
    forbidden_output_kinds: tuple[str, ...]
    initial_revise_count: int
    time_envelope_ref: str
    trace_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    final_output_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalCellQueueEntryV02:
    queue_entry_id: str
    topology_id: str
    topology_seed_id: str
    cell_id: str
    parent_cell_id: str | None
    node_id: str
    planned_child_cell_id: str | None
    cell_depth: int
    scope_ref: str
    cell_budget_id: str
    global_budget_id: str
    state: str
    prior_state: str | None
    predecessor_queue_entry_id: str | None
    predecessor_relation: str
    transition_decision_id: str
    canonical_priority: int
    node_instance_sequence: int
    snapshot_sequence: int
    admission_round: int
    queue_reason_codes: tuple[str, ...]
    observed_output_refs: tuple[str, ...]
    observed_evidence_refs: tuple[str, ...]
    advisory_refs: tuple[str, ...]
    lineage_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalReviseObservationV02:
    observation_id: str
    topology_id: str
    cell_id: str
    queue_entry_id: str
    revision_index: int
    newly_validated_evidence_count: int
    newly_resolved_constraints_count: int
    newly_accepted_outputs_count: int
    newly_introduced_conflicts_count: int
    progress_units: int
    consecutive_non_positive_count: int
    max_consecutive_non_positive_count: int
    revise_eligible: bool
    derived_terminal_state: str | None
    reason_codes: tuple[str, ...]
    cell_budget_before_id: str
    global_budget_before_id: str
    trace_refs: tuple[str, ...]
    root_review_required: bool
    authority_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalPartialFailureRecordV02:
    partial_failure_id: str
    topology_id: str
    parent_cell_id: str
    child_cell_id: str
    child_result_id: str
    failure_stage: str
    reason_codes: tuple[str, ...]
    source_reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    allocated_cell_budget_id: str
    final_cell_budget_id: str
    global_budget_id: str
    retry_eligible: bool
    revise_eligible: bool
    required_child: bool
    sibling_independent: bool
    parent_disposition: str
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    final_output_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalBackpressureStateV02:
    backpressure_id: str
    topology_id: str
    policy_id: str
    evaluated_round: int
    queue_capacity: int
    running_count: int
    ready_count: int
    pending_count: int
    deferred_queue_entry_ids: tuple[str, ...]
    admission_order: tuple[str, ...]
    backpressure_reason: str
    reason_codes: tuple[str, ...]
    no_work_dropped: bool
    lineage_refs: tuple[str, ...]
    global_budget_id: str
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalCellResultV02:
    result_id: str
    topology_id: str
    topology_seed_id: str
    cell_id: str
    parent_cell_id: str | None
    cell_depth: int
    cell_input_id: str
    ordered_terminal_queue_entry_ids: tuple[str, ...]
    ordered_child_result_ids: tuple[str, ...]
    outcome: str
    accepted_output_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    pre_result_validation_report_id: str
    post_vv_report_ref: str
    gt_advisory_ref: str
    partial_failure_ids: tuple[str, ...]
    allocated_cell_budget_id: str
    final_cell_budget_id: str
    global_budget_id: str
    scope_ref: str
    reason_codes: tuple[str, ...]
    source_reason_codes: tuple[str, ...]
    trace_refs: tuple[str, ...]
    parent_return_required: bool
    root_review_required: bool
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalRuntimeTraceV02:
    trace_id: str
    topology_id: str
    topology_seed_id: str
    source_binding_id: str
    ordered_queue_entry_ids: tuple[str, ...]
    state_transition_decision_ids: tuple[str, ...]
    cell_input_ids: tuple[str, ...]
    cell_result_ids: tuple[str, ...]
    scope_projection_ids: tuple[str, ...]
    revise_observation_ids: tuple[str, ...]
    partial_failure_ids: tuple[str, ...]
    backpressure_state_ids: tuple[str, ...]
    budget_ids: tuple[str, ...]
    abi_artifact_refs: tuple[str, ...]
    transition_refs: tuple[str, ...]
    parent_return_refs: tuple[str, ...]
    root_review_required: bool
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalRuntimeReportV02:
    report_id: str
    report_version: str
    profile_id: str
    topology_id: str
    topology_seed_id: str
    topology_artifact_id: str
    source_binding_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    accepted_mode: str
    accepted_scope_ref: str
    runtime_outcome: str
    ordered_cell_result_ids: tuple[str, ...]
    completed_cell_count: int
    degraded_cell_count: int
    blocked_cell_count: int
    needs_user_cell_count: int
    deadend_cell_count: int
    queue_entry_ids: tuple[str, ...]
    backpressure_state_ids: tuple[str, ...]
    runtime_trace_id: str
    final_budget_id: str
    parent_return_transition_decision_id: str
    parent_return_refs: tuple[str, ...]
    report_status: str
    reason_codes: tuple[str, ...]
    topology_created_count: int
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
    root_review_required: bool


@_dataclass(frozen=True)
class FractalRuntimeValidationReportV02:
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
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class FractalRuntimeSourceContextV02:
    transition_registry: TransitionRegistryV01
    g2c_source_context: ExecutionModeSourceContextV01
    router_input: ExecutionModeRouterInputV01
    proposal: ExecutionModeProposalV01
    proposal_artifact: KernelArtifactV01
    proposal_transition_decision: TransitionDecisionV01
    review_input: RootExecutionModeReviewInputV01
    decision: RootExecutionModeDecisionV01
    root_kernel: RootDecisionKernelV01
    root_decision_input: RootDecisionInputV01
    root_decision_result: RootDecisionResultV01
    decision_artifact: KernelArtifactV01
    root_route_transition_decision: TransitionDecisionV01
    route_eligibility_artifact: KernelArtifactV01
    runtime_policy: FractalRuntimePolicyV02


@_dataclass(frozen=True)
class FractalRuntimeExecutionBundleV02:
    source_context: FractalRuntimeSourceContextV02
    source_binding: RuntimeTopologySourceBindingV02
    topology_seed: RuntimeTopologySeedV02
    budgets: tuple[FractalRuntimeBudgetV02, ...]
    topology_nodes: tuple[RuntimeTopologyNodeV02, ...]
    topology_edges: tuple[RuntimeTopologyEdgeV02, ...]
    runtime_assignments: tuple[RuntimeAssignmentV02, ...]
    topology: RuntimeExecutionTopologyV02
    topology_artifact: KernelArtifactV01
    queue_entries: tuple[FractalCellQueueEntryV02, ...]
    queue_artifacts: tuple[KernelArtifactV01, ...]
    scope_projections: tuple[ParentChildScopeProjectionV02, ...]
    cell_inputs: tuple[FractalCellInputV02, ...]
    revise_observations: tuple[FractalReviseObservationV02, ...]
    partial_failures: tuple[FractalPartialFailureRecordV02, ...]
    backpressure_states: tuple[FractalBackpressureStateV02, ...]
    validation_reports: tuple[FractalRuntimeValidationReportV02, ...]
    result_proposals: tuple[dict[str, object], ...]
    post_vv_reports: tuple[dict[str, object], ...]
    gt_advisory_reports: tuple[dict[str, object], ...]
    cell_results: tuple[FractalCellResultV02, ...]
    result_artifacts: tuple[KernelArtifactV01, ...]
    runtime_trace: FractalRuntimeTraceV02
    runtime_report: FractalRuntimeReportV02
    report_artifact: KernelArtifactV01
    transition_decisions: tuple[TransitionDecisionV01, ...]
    causal_consumption_refs: tuple[CausalConsumptionRefV01, ...]


SERIALIZED_G2D_TYPES_V02 = (
    FractalRuntimePolicyV02,
    FractalRuntimeBudgetV02,
    RuntimeTopologySourceBindingV02,
    RuntimeTopologySeedV02,
    RuntimeTopologyNodeV02,
    RuntimeTopologyEdgeV02,
    RuntimeAssignmentV02,
    RuntimeExecutionTopologyV02,
    ParentChildScopeProjectionV02,
    FractalCellInputV02,
    FractalCellQueueEntryV02,
    FractalReviseObservationV02,
    FractalPartialFailureRecordV02,
    FractalBackpressureStateV02,
    FractalCellResultV02,
    FractalRuntimeTraceV02,
    FractalRuntimeReportV02,
    FractalRuntimeValidationReportV02,
)
RUNTIME_ONLY_G2D_TYPES_V02 = (
    FractalRuntimeSourceContextV02,
    FractalRuntimeExecutionBundleV02,
)
G2D_TYPES_V02 = SERIALIZED_G2D_TYPES_V02 + RUNTIME_ONLY_G2D_TYPES_V02

CHILD_SLOT_INDEX_ROWS_V02 = (
    (1, "PREDECESSOR_AND_CHILD_SLOT_1", 1, 0, 0),
    (2, "PREDECESSOR_AND_CHILD_SLOT_2", 2, 1, 1),
)
QUEUE_TRANSITION_INPUT_COLUMNS_V02 = (
    "rule_id",
    "current_entry_mode",
    "cell_input_mode",
    "dependency_mode",
    "target_observation_mode",
    "target_queue_reason_mode",
    "local_child_result_mode",
    "validation_report_mode",
    "revise_observation_mode",
    "backpressure_mode",
    "parent_return_family_mode",
)
QUEUE_TRANSITION_INPUT_ROWS_V02 = (
    ("t02", "ABSENT", "ABSENT", "EMPTY", "EMPTY", "EMPTY", "ABSENT", "ABSENT", "ABSENT", "ABSENT", "ABSENT"),
    ("t03", "PENDING", "REQUIRED", "SATISFIED", "EMPTY", "BACKPRESSURE_DERIVED", "ABSENT", "ABSENT", "ABSENT", "REQUIRED", "ABSENT"),
    ("t04", "PENDING", "REQUIRED", "SATISFIED", "EMPTY", "EMPTY", "ABSENT", "ABSENT", "ABSENT", "ABSENT", "ABSENT"),
    ("t05", "READY", "REQUIRED", "CURRENT_EXACT", "EMPTY", "EMPTY", "ABSENT", "ABSENT", "ABSENT", "ABSENT", "ABSENT"),
    ("t06", "RUNNING", "REQUIRED", "CURRENT_EXACT", "NEW_ATTEMPT_OBSERVATION", "NEW_ATTEMPT_DERIVED", "RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL_ELSE_ABSENT", "ABSENT", "ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
    ("t07", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "CLEAR_TO_EMPTY", "CLEAR_TO_EMPTY", "ABSENT", "REVISE_OBSERVATION_STRUCTURAL_REPORT", "REQUIRED", "ABSENT", "ABSENT"),
    ("t08", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "COPY_VALIDATING_OBSERVATION", "COPY_VALIDATING_REASONS", "REQUIRED_RESULT_IF_FRACTAL_CELL", "NODE_KIND_EXACT_OR_ABSENT", "ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
    ("t09", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "COPY_VALIDATING_OBSERVATION", "COPY_VALIDATING_REASONS", "REQUIRED_RESULT_IF_FRACTAL_CELL", "NODE_KIND_EXACT_OR_ABSENT", "ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
    ("t10", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "COPY_VALIDATING_OBSERVATION", "COPY_VALIDATING_REASONS", "RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL", "NODE_KIND_EXACT_OR_GATE_TERMINAL", "ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
    ("t11", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "COPY_VALIDATING_OBSERVATION", "COPY_VALIDATING_REASONS", "RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL", "NODE_KIND_EXACT_OR_GATE_TERMINAL", "ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
    ("t12", "VALIDATING", "REQUIRED", "CURRENT_EXACT", "COPY_VALIDATING_OBSERVATION", "COPY_VALIDATING_REASONS", "RESULT_OR_NO_CHILD_GATE_OUTCOME_IF_FRACTAL_CELL", "NODE_KIND_EXACT_OR_GATE_OR_REVISE_TERMINAL", "REQUIRED_IFF_REVISE_NO_PROGRESS_BRANCH_ELSE_ABSENT", "ABSENT", "REQUIRED_IF_PARENT_RETURN_ELSE_ABSENT"),
)
CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02 = (
    ("COMPLETED", "t06", "t08", "COMPLETED"),
    ("DEGRADED", "t06", "t09", "DEGRADED"),
    ("BLOCKED", "t06", "t10", "BLOCKED"),
    ("NEEDS_USER", "t06", "t11", "NEEDS_USER"),
    ("DEADEND", "t06", "t12", "DEADEND"),
)
CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02 = (
    ("VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL", "t06", "t10", "BLOCKED"),
    ("RESOLVABLE_INPUT_MISSING", "t06", "t11", "NEEDS_USER"),
    ("NO_PROGRESS_OR_NONRESOLVABLE", "t06", "t12", "DEADEND"),
)
PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02 = (
    ("completed", "t06", "t08", "COMPLETED"),
    ("degraded", "t06", "t09", "DEGRADED"),
    ("blocked", "t06", "t10", "BLOCKED"),
    ("needs_user", "t06", "t11", "NEEDS_USER"),
    ("deadend", "t06", "t12", "DEADEND"),
)
PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02 = (
    "parent_return_pre_post_vv_terminal_queue_entries",
    "parent_return_child_results",
    "parent_return_partial_failures",
    "parent_return_result_proposal",
    "parent_return_post_vv_report",
    "parent_return_gt_advisory_report",
    "parent_return_validation_reports",
)

MODE_NODE_TEMPLATE_ROWS_V02 = (
    ("memory_informed", (
        (0, "MEMORY_CONTEXT", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_RUNTIME,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "MEMORY_CONTEXT_OUTPUT", True, False, True, False, False, 0),
        (1, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (2, "POST_VV", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_POST_VV,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "POST_VV_REPORT", True, False, True, False, False, 0),
        (3, "GT_ADVISORY", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_GT,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "GT_ADVISORY_REPORT", True, False, True, False, False, 0),
        (4, "PARENT_RETURN", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_PARENT_RETURN,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "PARENT_RETURN_EVIDENCE", True, False, True, False, False, 0),
    )),
    ("local_slm", (
        (0, "LOCAL_MODEL_DECLARATION", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_RUNTIME,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "LOCAL_MODEL_DECLARATION_OUTPUT", True, False, True, False, False, 0),
        (1, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (2, "POST_VV", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_POST_VV,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "POST_VV_REPORT", True, False, True, False, False, 0),
        (3, "GT_ADVISORY", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_GT,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "GT_ADVISORY_REPORT", True, False, True, False, False, 0),
        (4, "PARENT_RETURN", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_PARENT_RETURN,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "PARENT_RETURN_EVIDENCE", True, False, True, False, False, 0),
    )),
    ("cloud_llm", (
        (0, "CLOUD_MODEL_DECLARATION", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_RUNTIME,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "CLOUD_MODEL_DECLARATION_OUTPUT", True, False, True, False, False, 0),
        (1, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (2, "POST_VV", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_POST_VV,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "POST_VV_REPORT", True, False, True, False, False, 0),
        (3, "GT_ADVISORY", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_GT,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "GT_ADVISORY_REPORT", True, False, True, False, False, 0),
        (4, "PARENT_RETURN", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_PARENT_RETURN,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "PARENT_RETURN_EVIDENCE", True, False, True, False, False, 0),
    )),
    ("full_semantic", (
        (0, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (1, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (2, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (3, "SEMANTIC_MERGE", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_RUNTIME,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "FAN_IN_OUTPUTS_0_1_2", "SEMANTIC_MERGE_OUTPUT", True, False, True, False, False, 0),
        (4, "POST_VV", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_POST_VV,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "POST_VV_REPORT", True, False, True, False, False, 0),
        (5, "GT_ADVISORY", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_GT,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "GT_ADVISORY_REPORT", True, False, True, False, False, 0),
        (6, "PARENT_RETURN", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_PARENT_RETURN,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "PARENT_RETURN_EVIDENCE", True, False, True, False, False, 0),
    )),
    ("full_fractal", (
        (0, "SEMANTIC_ACTOR", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", ("SRC_CAPS",), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "SOURCE_CONTEXT", "SEMANTIC_ACTOR_OUTPUT", True, False, True, False, False, 0),
        (1, "FRACTAL_CELL", "CURRENT_CELL_CHILD_SLOT", "PERMITTED_CHILD_SCOPE", "CHILD_ALLOCATION_BUDGET", (CAP_FRACTAL_CHILD,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_AND_CHILD_SLOT_1", "FRACTAL_CELL_OUTPUT", True, True, True, False, False, 0),
        (2, "FRACTAL_CELL", "CURRENT_CELL_CHILD_SLOT", "PERMITTED_CHILD_SCOPE", "CHILD_ALLOCATION_BUDGET", (CAP_FRACTAL_CHILD,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_AND_CHILD_SLOT_2", "FRACTAL_CELL_OUTPUT", True, True, True, False, False, 0),
        (3, "FRACTAL_MERGE", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_RUNTIME,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "FAN_IN_CHILD_SLOT_RETURNS_1_2", "FRACTAL_MERGE_OUTPUT", True, False, True, False, False, 0),
        (4, "POST_VV", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_POST_VV,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "POST_VV_REPORT", True, False, True, False, False, 0),
        (5, "GT_ADVISORY", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_GT,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "GT_ADVISORY_REPORT", True, False, True, False, False, 0),
        (6, "PARENT_RETURN", "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", (CAP_PARENT_RETURN,), ("ALL_CAPS",), FORBIDDEN_OUTPUT_KINDS, "PREDECESSOR_OUTPUTS", "PARENT_RETURN_EVIDENCE", True, False, True, False, False, 0),
    )),
)

MODE_EDGE_TEMPLATE_ROWS_V02 = (
    ("memory_informed", ((0, "ROOT_CELL_PROJECTION", 0, 1, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (1, "ROOT_CELL_PROJECTION", 1, 2, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (2, "ROOT_CELL_PROJECTION", 2, 3, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (3, "ROOT_CELL_PROJECTION", 3, 4, "RETURN", True, True, False, True, "EDGE_TRACE"))),
    ("local_slm", ((0, "ROOT_CELL_PROJECTION", 0, 1, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (1, "ROOT_CELL_PROJECTION", 1, 2, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (2, "ROOT_CELL_PROJECTION", 2, 3, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (3, "ROOT_CELL_PROJECTION", 3, 4, "RETURN", True, True, False, True, "EDGE_TRACE"))),
    ("cloud_llm", ((0, "ROOT_CELL_PROJECTION", 0, 1, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (1, "ROOT_CELL_PROJECTION", 1, 2, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (2, "ROOT_CELL_PROJECTION", 2, 3, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (3, "ROOT_CELL_PROJECTION", 3, 4, "RETURN", True, True, False, True, "EDGE_TRACE"))),
    ("full_semantic", ((0, "ROOT_CELL_PROJECTION", 0, 3, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (1, "ROOT_CELL_PROJECTION", 1, 3, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (2, "ROOT_CELL_PROJECTION", 2, 3, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (3, "ROOT_CELL_PROJECTION", 3, 4, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (4, "ROOT_CELL_PROJECTION", 4, 5, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (5, "ROOT_CELL_PROJECTION", 5, 6, "RETURN", True, True, False, True, "EDGE_TRACE"))),
    ("full_fractal", ((0, "ROOT_CELL_PROJECTION", 0, 1, "PARENT_CHILD", True, True, False, True, "EDGE_TRACE"), (1, "ROOT_CELL_PROJECTION", 0, 2, "PARENT_CHILD", True, True, False, True, "EDGE_TRACE"), (2, "ROOT_CELL_PROJECTION", 1, 3, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (3, "ROOT_CELL_PROJECTION", 2, 3, "DATA_DEPENDENCY", True, True, False, True, "EDGE_TRACE"), (4, "ROOT_CELL_PROJECTION", 3, 4, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (5, "ROOT_CELL_PROJECTION", 4, 5, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (6, "ROOT_CELL_PROJECTION", 5, 6, "RETURN", True, True, False, True, "EDGE_TRACE"), (7, "FRACTAL_LEAF_PROJECTION", 0, 4, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (8, "FRACTAL_LEAF_PROJECTION", 4, 5, "VALIDATION", True, True, False, True, "EDGE_TRACE"), (9, "FRACTAL_LEAF_PROJECTION", 5, 6, "RETURN", True, True, False, True, "EDGE_TRACE"))),
)

ASSIGNMENT_KIND_ROWS_V02 = (
    ("MEMORY_CONTEXT", "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("LOCAL_MODEL_DECLARATION", "LOCAL_MODEL_DECLARED", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("CLOUD_MODEL_DECLARATION", "CLOUD_MODEL_DECLARED", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("SEMANTIC_ACTOR", "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("SEMANTIC_MERGE", "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("FRACTAL_CELL", "FRACTAL_CHILD", "fractal_runtime_v02", (CAP_FRACTAL_CHILD,), "CURRENT_CELL_CHILD_SLOT", "PERMITTED_CHILD_SCOPE", "CHILD_ALLOCATION_BUDGET"),
    ("FRACTAL_MERGE", "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("POST_VV", "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("GT_ADVISORY", "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
    ("PARENT_RETURN", "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET"),
)
MODE_ASSIGNMENT_TEMPLATE_ROWS_V02 = (
    ("memory_informed", (
        (0, 0, "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (1, 1, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (2, 2, "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (3, 3, "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (4, 4, "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
    )),
    ("local_slm", (
        (0, 0, "LOCAL_MODEL_DECLARED", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (1, 1, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (2, 2, "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (3, 3, "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (4, 4, "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
    )),
    ("cloud_llm", (
        (0, 0, "CLOUD_MODEL_DECLARED", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (1, 1, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (2, 2, "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (3, 3, "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (4, 4, "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
    )),
    ("full_semantic", (
        (0, 0, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (1, 1, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (2, 2, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (3, 3, "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (4, 4, "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (5, 5, "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (6, 6, "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
    )),
    ("full_fractal", (
        (0, 0, "SEMANTIC_ACTOR", "fractal_runtime_v02", ("SRC_CAPS",), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (1, 1, "FRACTAL_CHILD", "fractal_runtime_v02", (CAP_FRACTAL_CHILD,), "CURRENT_CELL_CHILD_SLOT", "PERMITTED_CHILD_SCOPE", "CHILD_ALLOCATION_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (2, 2, "FRACTAL_CHILD", "fractal_runtime_v02", (CAP_FRACTAL_CHILD,), "CURRENT_CELL_CHILD_SLOT", "PERMITTED_CHILD_SCOPE", "CHILD_ALLOCATION_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (3, 3, "LOCAL_DETERMINISTIC", "fractal_runtime_v02", (CAP_RUNTIME,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (4, 4, "VALIDATOR", "post_vv_v01", (CAP_POST_VV,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (5, 5, "ADVISORY", "gt_validator_v01", (CAP_GT,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
        (6, 6, "PARENT_RETURN", "parent_return_v02", (CAP_PARENT_RETURN,), "CURRENT_CELL", "CURRENT_CELL_SCOPE", "CURRENT_CELL_BUDGET", False, False, False, "ASSIGNMENT_TRACE", True, False, False, False, 0),
    )),
)

CELL_NODE_PROJECTION_ROWS_V02 = (
    ("memory_informed", "ROOT", 0, (0, 1, 2, 3, 4), 0, ()),
    ("local_slm", "ROOT", 0, (0, 1, 2, 3, 4), 0, ()),
    ("cloud_llm", "ROOT", 0, (0, 1, 2, 3, 4), 0, ()),
    ("full_semantic", "ROOT", 0, (0, 1, 2, 3, 4, 5, 6), 0, ()),
    ("full_fractal", "ROOT", 0, (0, 1, 2, 3, 4, 5, 6), 2, (0, 1)),
    ("full_fractal", "REFERENCE_CHILD_SLOT_1", 1, (0, 4, 5, 6), 0, ()),
    ("full_fractal", "REFERENCE_CHILD_SLOT_2", 1, (0, 4, 5, 6), 0, ()),
    ("full_fractal", "STRUCTURAL_DEPTH_2_LEAF", 2, (0, 4, 5, 6), 0, ()),
)
CELL_EDGE_PROJECTION_ROWS_V02 = (
    ("memory_informed", "ROOT", (0, 1, 2, 3)),
    ("local_slm", "ROOT", (0, 1, 2, 3)),
    ("cloud_llm", "ROOT", (0, 1, 2, 3)),
    ("full_semantic", "ROOT", (0, 1, 2, 3, 4, 5)),
    ("full_fractal", "ROOT", (0, 1, 2, 3, 4, 5, 6)),
    ("full_fractal", "REFERENCE_CHILD_SLOT_1", (7, 8, 9)),
    ("full_fractal", "REFERENCE_CHILD_SLOT_2", (7, 8, 9)),
    ("full_fractal", "STRUCTURAL_DEPTH_2_LEAF", (7, 8, 9)),
)
NODE_WORK_QUEUE_V02 = "ONE_IMMUTABLE_QUEUE_CHAIN_PER_INSTANTIATED_NODE"

PUBLIC_G2D_REASON_CODES = (
    "g2d_type_invalid",
    "g2d_field_count_invalid",
    "g2d_field_type_invalid",
    "g2d_identity_invalid",
    "g2d_identity_mismatch",
    "g2d_serialization_invalid",
    "g2d_tuple_order_invalid",
    "g2d_tuple_duplicate",
    "g2d_text_invalid",
    "g2d_integer_invalid",
    "g2d_boolean_is_not_integer",
    "g2d_float_forbidden",
    "g2d_decimal_forbidden",
    "g2d_nonfinite_forbidden",
    "g2d_wall_clock_forbidden",
    "g2d_randomness_forbidden",
    "g2d_caller_identity_forbidden",
    "g2d_caller_pass_forbidden",
    "g2d_secret_material_forbidden",
    "g2d_callback_forbidden",
    "g2d_client_handle_forbidden",
    "g2d_effect_handle_forbidden",
    "g2d_raw_provider_output_forbidden",
    "g2d_unknown_enum",
    "g2d_source_context_invalid",
    "g2d_g2c_context_invalid",
    "g2d_g2c_router_input_invalid",
    "g2d_g2c_proposal_invalid",
    "g2d_g2c_proposal_artifact_invalid",
    "g2d_g2c_proposal_transition_invalid",
    "g2d_g2c_review_input_invalid",
    "g2d_g2c_root_kernel_invalid",
    "g2d_g2c_root_input_invalid",
    "g2d_g2c_root_result_invalid",
    "g2d_g2c_decision_invalid",
    "g2d_g2c_decision_artifact_invalid",
    "g2d_g2c_post_root_transition_invalid",
    "g2d_route_eligibility_missing",
    "g2d_route_eligibility_invalid",
    "g2d_route_eligibility_substituted",
    "g2d_route_eligibility_context_mismatch",
    "g2d_route_class_not_topology_eligible",
    "g2d_shortcut_consumption_forbidden",
    "g2d_terminal_consumption_forbidden",
    "g2d_direct_root_decision_consumption_forbidden",
    "g2d_mode_not_topology_eligible",
    "g2d_mode_upgrade_forbidden",
    "g2d_mode_downgrade_forbidden",
    "g2d_mode_profile_mismatch",
    "g2d_full_fractal_capability_missing",
    "g2d_non_fractal_recursion_forbidden",
    "g2d_topology_policy_invalid",
    "g2d_topology_source_binding_invalid",
    "g2d_topology_identity_mismatch",
    "g2d_topology_lineage_mismatch",
    "g2d_topology_time_mismatch",
    "g2d_topology_node_invalid",
    "g2d_topology_edge_invalid",
    "g2d_topology_assignment_invalid",
    "g2d_topology_order_invalid",
    "g2d_topology_cycle",
    "g2d_topology_unknown_node",
    "g2d_topology_duplicate_edge",
    "g2d_topology_orphan_node",
    "g2d_topology_parent_mismatch",
    "g2d_topology_provider_owned_forbidden",
    "g2d_topology_authority_claim_forbidden",
    "g2d_queue_entry_invalid",
    "g2d_queue_state_unknown",
    "g2d_queue_transition_unknown",
    "g2d_queue_transition_illegal",
    "g2d_queue_caller_state_forbidden",
    "g2d_queue_order_mismatch",
    "g2d_queue_priority_source_forbidden",
    "g2d_terminal_queue_reentry_forbidden",
    "g2d_backpressure_invalid",
    "g2d_backpressure_work_drop_forbidden",
    "g2d_backpressure_lineage_missing",
    "g2d_depth_limit_exceeded",
    "g2d_fan_out_limit_exceeded",
    "g2d_total_cell_limit_exceeded",
    "g2d_parallelism_limit_exceeded",
    "g2d_revise_limit_exceeded",
    "g2d_wall_time_budget_exceeded",
    "g2d_token_budget_exceeded",
    "g2d_provider_budget_exceeded",
    "g2d_budget_invalid",
    "g2d_budget_negative",
    "g2d_budget_overflow",
    "g2d_budget_double_spend",
    "g2d_budget_hidden_reset",
    "g2d_sibling_budget_borrowing_forbidden",
    "g2d_child_budget_widening",
    "g2d_child_depth_mismatch",
    "g2d_child_scope_widening",
    "g2d_child_capability_widening",
    "g2d_child_forbidden_narrowing",
    "g2d_child_ttl_widening",
    "g2d_child_lineage_mismatch",
    "g2d_revise_observation_invalid",
    "g2d_revise_progress_mismatch",
    "g2d_revise_hidden_retry_forbidden",
    "g2d_revise_terminal_caller_selection_forbidden",
    "g2d_no_progress_deadend",
    "g2d_resolvable_input_needs_user",
    "g2d_partial_failure_invalid",
    "g2d_required_child_failure",
    "g2d_sibling_evidence_erasure_forbidden",
    "g2d_success_laundering_forbidden",
    "g2d_parent_disposition_mismatch",
    "g2d_cell_input_invalid",
    "g2d_cell_result_invalid",
    "g2d_cell_result_context_mismatch",
    "g2d_cell_root_claim_forbidden",
    "g2d_cell_final_output_claim_forbidden",
    "g2d_cell_permission_claim_forbidden",
    "g2d_cell_packet_claim_forbidden",
    "g2d_cell_receipt_claim_forbidden",
    "g2d_cell_effect_claim_forbidden",
    "g2d_runtime_trace_invalid",
    "g2d_runtime_report_invalid",
    "g2d_runtime_report_identity_mismatch",
    "g2d_abi_profile_invalid",
    "g2d_abi_bundle_invalid",
    "g2d_abi_projection_substituted",
    "g2d_transition_profile_invalid",
    "g2d_transition_decision_substituted",
    "g2d_parent_return_invalid",
    "g2d_sources_valid",
    "g2d_route_eligibility_valid",
    "g2d_topology_constructed",
    "g2d_topology_valid",
    "g2d_queue_admitted",
    "g2d_queue_state_advanced",
    "g2d_scope_projection_valid",
    "g2d_budget_accounting_valid",
    "g2d_revise_progress_valid",
    "g2d_partial_failure_recorded",
    "g2d_backpressure_recorded",
    "g2d_cell_result_valid",
    "g2d_runtime_trace_valid",
    "g2d_runtime_report_valid",
    "g2d_abi_profile_valid",
    "g2d_transition_topology_construction_allowed",
    "g2d_transition_queue_admission_allowed",
    "g2d_transition_backpressure_deferred",
    "g2d_transition_pending_ready_allowed",
    "g2d_transition_ready_running_allowed",
    "g2d_transition_running_validating_allowed",
    "g2d_transition_bounded_revise_allowed",
    "g2d_transition_completed_recorded",
    "g2d_transition_degraded_recorded",
    "g2d_transition_blocked_recorded",
    "g2d_transition_needs_user_recorded",
    "g2d_transition_deadend_recorded",
    "g2d_transition_completed_parent_return",
    "g2d_transition_degraded_parent_return",
    "g2d_transition_blocked_parent_return",
    "g2d_transition_needs_user_parent_return",
    "g2d_transition_deadend_parent_return",
    "g2d_identity_dependency_cycle",
    "g2d_topology_seed_invalid",
    "g2d_root_cell_identity_invalid",
    "g2d_child_cell_identity_invalid",
    "g2d_queue_predecessor_invalid",
    "g2d_queue_artifact_lineage_invalid",
    "g2d_post_vv_time_source_invalid",
    "g2d_gt_time_source_invalid",
    "g2d_post_vv_fallback_forbidden",
    "g2d_causal_consumption_invalid",
    "g2d_causal_consumption_missing",
    "g2d_causal_counterfactual_mismatch",
    "g2d_unused_field_disposition_missing",
    "g2d_partial_failure_result_cycle",
    "g2d_validation_report_identity_cycle",
    "g2d_node_instance_geometry_invalid",
    "g2d_cell_result_postorder_invalid",
    "g2d_child_result_direct_parent_return_forbidden",
    "g2d_mode_template_matrix_invalid",
    "g2d_source_profile_binding_mismatch",
    "g2d_scope_relation_unproven",
    "g2d_budget_predecessor_invalid",
    "g2d_budget_allocation_oversubscribed",
    "g2d_budget_debit_mismatch",
    "g2d_result_proposal_invalid",
    "g2d_post_vv_report_invalid",
    "g2d_gt_advisory_invalid",
    "g2d_terminal_outcome_mapping_invalid",
    "g2d_abi_field_partition_invalid",
    "g2d_trace_lineage_invalid",
    "g2d_backpressure_reason_invalid",
    "g2d_root_result_required_for_parent_return",
    "g2d_runtime_bundle_report_missing",
    "g2d_causal_json_pointer_invalid",
    "g2d_causal_reason_prefix_invalid",
    "g2d_policy_profile_identity_mismatch",
    "g2d_cell_edge_projection_invalid",
    "g2d_leaf_projection_unexecutable",
    "g2d_static_input_derivation_invalid",
    "g2d_assignment_trace_invalid",
    "g2d_global_budget_binding_missing",
    "g2d_budget_event_pair_mismatch",
    "g2d_budget_state_transition_invalid",
    "g2d_pre_root_lifecycle_escalation_forbidden",
    "g2d_gt_report_identity_collision",
    "g2d_gt_report_context_id_invalid",
    "g2d_validation_status_stage_mismatch",
    "g2d_validation_target_id_mismatch",
    "g2d_queue_sequence_invalid",
    "g2d_blocked_reason_selection_invalid",
    "g2d_result_report_ref_mismatch",
    "g2d_child_slot_activation_invalid",
    "g2d_cell_input_build_order_invalid",
    "g2d_node_cell_outcome_conflation",
    "g2d_runtime_report_status_outcome_mismatch",
    "g2d_runtime_outcome_root_result_mismatch",
    "g2d_budget_event_context_invalid",
    "g2d_transition_target_dependency_cycle",
    "g2d_revise_budget_dependency_cycle",
    "g2d_execution_bundle_dependency_cycle",
)
PUBLIC_G2D_REASON_CODES_V02 = PUBLIC_G2D_REASON_CODES

IDENTITY_PROFILE_ROWS_V02 = (
    (FractalRuntimePolicyV02, "policy_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_POLICY", "frpolicy_v02:"),
    (FractalRuntimeBudgetV02, "budget_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_BUDGET", "frbudget_v02:"),
    (RuntimeTopologySourceBindingV02, "source_binding_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_SOURCE_BINDING", "frsource_v02:"),
    (RuntimeTopologySeedV02, "topology_seed_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_TOPOLOGY_SEED", "frseed_v02:"),
    (RuntimeTopologyNodeV02, "node_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_NODE", "frnode_v02:"),
    (RuntimeTopologyEdgeV02, "edge_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_EDGE", "fredge_v02:"),
    (RuntimeAssignmentV02, "assignment_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_ASSIGNMENT", "frassign_v02:"),
    (RuntimeExecutionTopologyV02, "topology_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_TOPOLOGY", "frtopology_v02:"),
    (ParentChildScopeProjectionV02, "projection_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_SCOPE_PROJECTION", "frscope_v02:"),
    (FractalCellInputV02, "cell_input_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_CELL_INPUT", "frcellin_v02:"),
    (FractalCellQueueEntryV02, "queue_entry_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_QUEUE_ENTRY", "frqueue_v02:"),
    (FractalReviseObservationV02, "observation_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_REVISE", "frrevise_v02:"),
    (FractalPartialFailureRecordV02, "partial_failure_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_PARTIAL_FAILURE", "frfailure_v02:"),
    (FractalBackpressureStateV02, "backpressure_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_BACKPRESSURE", "frbackpressure_v02:"),
    (FractalCellResultV02, "result_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_CELL_RESULT", "frcellresult_v02:"),
    (FractalRuntimeTraceV02, "trace_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_TRACE", "frtrace_v02:"),
    (FractalRuntimeReportV02, "report_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_REPORT", "frreport_v02:"),
    (FractalRuntimeValidationReportV02, "validation_report_id", "HEDGEHOG_FRACTAL_RUNTIME_V02_VALIDATION", "frvalidation_v02:"),
)

STRUCTURAL_VALIDATION_TARGET_ROWS_V02 = (
    (FractalRuntimePolicyV02, "FractalRuntimePolicyV02", "policy_id", "POLICY"),
    (FractalRuntimeBudgetV02, "FractalRuntimeBudgetV02", "budget_id", "BUDGET"),
    (RuntimeTopologySourceBindingV02, "RuntimeTopologySourceBindingV02", "source_binding_id", "SOURCE_BINDING"),
    (RuntimeTopologySeedV02, "RuntimeTopologySeedV02", "topology_seed_id", "TOPOLOGY_SEED"),
    (RuntimeTopologyNodeV02, "RuntimeTopologyNodeV02", "node_id", "NODE"),
    (RuntimeTopologyEdgeV02, "RuntimeTopologyEdgeV02", "edge_id", "EDGE"),
    (RuntimeAssignmentV02, "RuntimeAssignmentV02", "assignment_id", "ASSIGNMENT"),
    (RuntimeExecutionTopologyV02, "RuntimeExecutionTopologyV02", "topology_id", "TOPOLOGY"),
    (ParentChildScopeProjectionV02, "ParentChildScopeProjectionV02", "projection_id", "SCOPE"),
    (FractalCellInputV02, "FractalCellInputV02", "cell_input_id", "CELL_INPUT"),
    (FractalCellQueueEntryV02, "FractalCellQueueEntryV02", "queue_entry_id", "QUEUE"),
    (FractalReviseObservationV02, "FractalReviseObservationV02", "observation_id", "REVISE"),
    (FractalPartialFailureRecordV02, "FractalPartialFailureRecordV02", "partial_failure_id", "PARTIAL_FAILURE"),
    (FractalBackpressureStateV02, "FractalBackpressureStateV02", "backpressure_id", "BACKPRESSURE"),
    (FractalCellResultV02, "FractalCellResultV02", "result_id", "CELL_RESULT"),
    (FractalRuntimeTraceV02, "FractalRuntimeTraceV02", "trace_id", "RUNTIME_TRACE"),
    (FractalRuntimeReportV02, "FractalRuntimeReportV02", "report_id", "REPORT"),
)
CONTEXTUAL_VALIDATION_TARGET_ROWS_V02 = (
    ("SOURCE_CONTEXT_STRUCTURAL", None, "SOURCE_CONTEXT"),
    ("SOURCE_BINDING_AGAINST_G2C", "frsource_v02:", "SOURCE_BINDING"),
    ("TOPOLOGY_AGAINST_SOURCES", "frtopology_v02:", "TOPOLOGY"),
    ("SCOPE_PROJECTION_AGAINST_SOURCES", "frscope_v02:", "SCOPE"),
    ("CELL_INPUT_AGAINST_SOURCES", "frcellin_v02:", "CELL_INPUT"),
    ("RESULT_PROPOSAL", "proposal", "RESULT_PROPOSAL"),
    ("POST_VV_REPORT", "vv_report", "POST_VV"),
    ("GT_ADVISORY_REPORT", "gt_report", "GT"),
    ("CELL_RESULT_PRECONDITIONS", "proposal", "CELL_RESULT_PRECONDITIONS"),
    ("RUNTIME_REPORT_AGAINST_SOURCES", "frreport_v02:", "REPORT"),
    ("STAGE_D_A", "frstage_v02:", "ABI"),
    ("STAGE_D_B", "frstage_v02:", "ABI"),
    ("STAGE_D_C", "frstage_v02:", "ABI"),
    ("ABI_PROFILE", "frstage_v02:", "ABI"),
    ("CAUSAL_CONSUMPTION", "frcausalprofile_v02:", "CAUSAL_CONSUMPTION"),
    ("CAUSAL_COUNTERFACTUAL", "frcounterfactual_v02:", "CAUSAL_COUNTERFACTUAL"),
    ("COMPLETE_PROFILE", "artifact", "COMPLETE_PROFILE"),
)

BUILDER_FIELD_DERIVATION_ROWS_V02 = (
    ("FractalRuntimePolicyV02", (
        ("DI", ("policy_id",)),
        ("FL", ("policy_profile_id", "policy_version", "allowed_modes", "allowed_node_kinds", "allowed_edge_kinds", "allowed_assignment_kinds", "recursive_mode", "recursive_capability_id", "forbidden_claims", "reference_child_count", "queue_profile_id", "budget_profile_id", "max_depth", "max_fan_out", "max_total_cells", "max_parallelism", "max_revise_count", "max_consecutive_no_progress", "max_wall_time_units", "max_token_budget", "max_provider_calls", "root_review_required")),
        ("SD", ("allowed_capability_ids", "permitted_child_scope_refs")),
        ("ZN", ("authority_created", "permission_created", "real_world_effects_count")),
    )),
    ("FractalRuntimeBudgetV02", (
        ("DI", ("budget_id",)),
        ("CD", ("policy_id", "topology_seed_id", "allocation_parent_budget_id", "predecessor_budget_id", "owning_cell_id", "budget_scope", "budget_state", "budget_event_kind")),
        ("TE", ("budget_event_ref",)),
        ("SD", ("max_depth", "max_fan_out", "max_total_cells", "max_parallelism", "max_revise_count", "max_wall_time_units", "max_token_budget", "max_provider_calls")),
        ("KD", ("consumed_wall_time_units", "consumed_token_budget", "consumed_provider_calls", "consumed_cell_count", "consumed_revise_count", "current_parallelism", "remaining_wall_time_units", "remaining_token_budget", "remaining_provider_calls", "remaining_cell_count", "remaining_revise_count", "remaining_parallel_slots")),
        ("FL", ("root_review_required",)),
        ("ZN", ("authority_created", "permission_created", "action_commit_packet_created", "receipt_created", "final_output_created", "drs_write_created", "real_world_effects_count")),
    )),
    ("RuntimeTopologySourceBindingV02", (
        ("DI", ("source_binding_id",)),
        ("SD", ("request_id", "transaction_id", "owning_root_id", "domain_id", "accepted_mode", "accepted_scope_ref", "route_eligibility_artifact_id", "route_eligibility_artifact_sha256", "source_decision_artifact_id", "source_proposal_artifact_id", "selected_local_mode_profile_id", "selected_feasibility_row_id", "selected_safe_depth_rank", "selected_expected_cost_units", "required_downstream_capability_ids", "source_mode_profile_set_id", "source_policy_snapshot_id", "source_capability_snapshot_id", "permitted_narrower_scope_refs", "source_root_decision_result_id", "source_root_transition_decision_id", "proposal_transition_decision_id", "post_root_transition_decision_id", "transition_registry_id", "g2c_abi_profile_id", "downstream_action_packet_required", "source_time_envelope_ref", "source_trace_refs", "source_parent_refs")),
        ("CD", ("runtime_policy_id",)),
        ("FL", ("root_review_required",)),
        ("ZN", ("authority_created", "permission_created", "real_world_effects_count")),
    )),
    ("RuntimeTopologySeedV02", (("DI", ("topology_seed_id",)), ("FL", ("seed_version", "profile_id", "root_review_required")), ("CD", ("request_id", "transaction_id", "owning_root_id", "domain_id", "accepted_mode", "accepted_scope_ref", "source_binding_id", "runtime_policy_id", "root_cell_id", "source_time_envelope_ref", "trace_refs", "parent_refs")), ("ZN", ("authority_created", "permission_created", "real_world_effects_count")))),
    ("RuntimeTopologyNodeV02", (("DI", ("node_id",)), ("CD", ("topology_seed_id", "accepted_mode", "scope_ref", "allowed_capability_ids", "forbidden_claims", "input_refs", "trace_refs", "expected_output_kind")), ("IP", ("node_kind", "canonical_index", "depth", "cell_binding_class", "scope_binding_class", "budget_binding_class", "required_capability_ids", "input_ref_derivation_class")), ("FL", ("required", "recursive_expansion_allowed", "root_review_required")), ("ZN", ("authority_created", "permission_created", "real_world_effects_count")))),
    ("RuntimeTopologyEdgeV02", (("DI", ("edge_id",)), ("CD", ("topology_seed_id", "source_node_id", "target_node_id", "trace_refs")), ("IP", ("edge_kind", "canonical_index", "cell_projection_class")), ("FL", ("required", "evidence_flow_allowed", "authority_flow_allowed", "root_review_required")))),
    ("RuntimeAssignmentV02", (("DI", ("assignment_id",)), ("CD", ("topology_seed_id", "node_id", "canonical_index", "trace_refs")), ("IP", ("assignment_kind", "executor_component_id", "capability_ids", "cell_binding_class", "scope_binding_class", "budget_binding_class")), ("FL", ("provider_call_allowed", "network_call_allowed", "connector_call_allowed", "root_review_required")), ("ZN", ("authority_created", "permission_created", "effect_created", "real_world_effects_count")))),
    ("RuntimeExecutionTopologyV02", (("DI", ("topology_id",)), ("FL", ("topology_version", "root_review_required")), ("CD", ("topology_seed_id", "request_id", "transaction_id", "owning_root_id", "domain_id", "accepted_mode", "accepted_scope_ref", "source_binding_id", "source_route_eligibility_artifact_id", "source_root_decision_artifact_id", "source_proposal_artifact_id", "runtime_policy_id", "ordered_node_ids", "ordered_edge_ids", "ordered_assignment_ids", "root_cell_id", "global_budget_id", "time_envelope_ref", "trace_refs", "parent_refs")), ("ZN", ("authority_created", "permission_created", "action_commit_packet_created", "receipt_created", "final_output_created", "drs_write_created", "provider_calls", "network_calls", "real_world_effects_count")))),
    ("ParentChildScopeProjectionV02", (("DI", ("projection_id",)), ("CD", ("topology_id", "parent_cell_id", "child_cell_id", "parent_scope_ref", "child_scope_ref", "parent_allowed_capability_ids", "child_allowed_capability_ids", "parent_forbidden_claims", "child_forbidden_claims", "parent_ttl_units", "child_ttl_units", "parent_budget_id", "child_budget_id", "global_budget_id", "child_depth", "parent_lineage_refs", "child_lineage_refs", "proof_refs")), ("KD", ("scope_relation", "budget_relation")), ("FL", ("root_review_required",)), ("ZN", ("authority_created", "permission_created", "final_output_created", "real_world_effects_count")))),
    ("FractalCellInputV02", (("DI", ("cell_input_id",)), ("CD", ("topology_id", "cell_id", "parent_cell_id", "request_id", "transaction_id", "owning_root_id", "domain_id", "accepted_mode", "scope_projection_id", "scope_ref", "cell_budget_id", "global_budget_id", "ordered_initial_queue_entry_ids", "ordered_required_queue_entry_ids", "cell_depth", "requested_child_count", "ordered_planned_child_cell_ids", "ordered_node_ids", "evidence_refs", "context_refs", "required_output_kinds", "forbidden_output_kinds", "time_envelope_ref", "trace_refs")), ("FL", ("initial_revise_count", "root_review_required")), ("ZN", ("authority_created", "permission_created", "action_commit_packet_created", "final_output_created", "real_world_effects_count")))),
    ("FractalCellQueueEntryV02", (("DI", ("queue_entry_id",)), ("CD", ("topology_id", "topology_seed_id", "cell_id", "parent_cell_id", "node_id", "planned_child_cell_id", "cell_depth", "scope_ref", "cell_budget_id", "global_budget_id", "predecessor_queue_entry_id", "transition_decision_id", "observed_output_refs", "observed_evidence_refs", "advisory_refs", "lineage_refs")), ("IP", ("queue_reason_codes",)), ("KD", ("state", "prior_state", "predecessor_relation", "canonical_priority", "node_instance_sequence", "snapshot_sequence", "admission_round")), ("FL", ("root_review_required",)), ("ZN", ("authority_created", "permission_created", "final_output_created", "drs_write_created", "real_world_effects_count")))),
    ("FractalReviseObservationV02", (("DI", ("observation_id",)), ("CD", ("topology_id", "cell_id", "queue_entry_id", "cell_budget_before_id", "global_budget_before_id", "trace_refs")), ("IP", ("revision_index", "newly_validated_evidence_count", "newly_resolved_constraints_count", "newly_accepted_outputs_count", "newly_introduced_conflicts_count", "consecutive_non_positive_count", "max_consecutive_non_positive_count")), ("KD", ("progress_units", "revise_eligible", "derived_terminal_state", "reason_codes")), ("FL", ("root_review_required",)), ("ZN", ("authority_created", "real_world_effects_count")))),
    ("FractalPartialFailureRecordV02", (("DI", ("partial_failure_id",)), ("CD", ("topology_id", "parent_cell_id", "child_cell_id", "child_result_id", "evidence_refs", "trace_refs", "allocated_cell_budget_id", "final_cell_budget_id", "global_budget_id")), ("IP", ("failure_stage", "reason_codes", "source_reason_codes", "required_child", "sibling_independent")), ("KD", ("revise_eligible", "parent_disposition")), ("FL", ("retry_eligible", "root_review_required")), ("ZN", ("authority_created", "permission_created", "final_output_created", "real_world_effects_count")))),
    ("FractalBackpressureStateV02", (("DI", ("backpressure_id",)), ("CD", ("topology_id", "policy_id", "deferred_queue_entry_ids", "admission_order", "lineage_refs", "global_budget_id")), ("IP", ("evaluated_round",)), ("KD", ("queue_capacity", "running_count", "ready_count", "pending_count", "backpressure_reason", "reason_codes")), ("FL", ("no_work_dropped", "root_review_required")), ("ZN", ("authority_created", "permission_created", "real_world_effects_count")))),
    ("FractalCellResultV02", (("DI", ("result_id",)), ("CD", ("topology_id", "topology_seed_id", "cell_id", "parent_cell_id", "cell_depth", "cell_input_id", "ordered_terminal_queue_entry_ids", "ordered_child_result_ids", "accepted_output_refs", "evidence_refs", "pre_result_validation_report_id", "post_vv_report_ref", "gt_advisory_ref", "partial_failure_ids", "allocated_cell_budget_id", "final_cell_budget_id", "global_budget_id", "scope_ref", "trace_refs")), ("KD", ("outcome", "reason_codes", "source_reason_codes")), ("FL", ("parent_return_required", "root_review_required")), ("ZN", ("authority_created", "permission_created", "action_commit_packet_created", "receipt_created", "final_output_created", "drs_write_created", "real_world_effects_count")))),
    ("FractalRuntimeTraceV02", (("DI", ("trace_id",)), ("CD", ("topology_id", "topology_seed_id", "source_binding_id", "ordered_queue_entry_ids", "state_transition_decision_ids", "cell_input_ids", "cell_result_ids", "scope_projection_ids", "revise_observation_ids", "partial_failure_ids", "backpressure_state_ids", "budget_ids", "abi_artifact_refs", "transition_refs", "parent_return_refs")), ("FL", ("root_review_required",)), ("ZN", ("provider_calls", "model_calls", "network_calls", "connector_calls", "external_drs_calls", "real_world_effects_count")))),
    ("FractalRuntimeReportV02", (("DI", ("report_id",)), ("FL", ("report_version", "profile_id", "report_status", "root_review_required")), ("CD", ("topology_id", "topology_seed_id", "topology_artifact_id", "source_binding_id", "request_id", "transaction_id", "owning_root_id", "domain_id", "accepted_mode", "accepted_scope_ref", "ordered_cell_result_ids", "queue_entry_ids", "backpressure_state_ids", "runtime_trace_id", "final_budget_id", "parent_return_transition_decision_id", "parent_return_refs")), ("KD", ("runtime_outcome", "completed_cell_count", "degraded_cell_count", "blocked_cell_count", "needs_user_cell_count", "deadend_cell_count", "reason_codes", "topology_created_count")), ("ZN", ("provider_calls", "model_calls", "network_calls", "connector_calls", "external_drs_calls", "action_commit_packets_created", "permissions_created", "receipts_created", "final_outputs_created", "drs_writes", "authority_created_count", "real_world_effects_count")))),
    ("FractalRuntimeValidationReportV02", (("DI", ("validation_report_id",)), ("IP", ("validation_target", "validated_object_id", "failure_stage", "reason_codes", "source_reason_codes")), ("KD", ("status", "return_to_root_required")), ("FL", ("root_review_required",)), ("ZN", ("authority_created", "permission_created", "action_commit_packet_created", "final_output_created", "drs_write_created", "real_world_effects_count")))),
)

_STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02 = (
    ("FractalRuntimePolicyV02", ("allowed_capability_ids", "permitted_child_scope_refs")),
    ("RuntimeTopologySourceBindingV02", ("required_downstream_capability_ids", "permitted_narrower_scope_refs", "source_trace_refs", "source_parent_refs")),
    ("RuntimeTopologySeedV02", ("trace_refs", "parent_refs")),
    ("RuntimeTopologyNodeV02", ("required_capability_ids", "allowed_capability_ids", "forbidden_claims", "input_refs", "trace_refs")),
    ("RuntimeTopologyEdgeV02", ("trace_refs",)),
    ("RuntimeAssignmentV02", ("capability_ids", "trace_refs")),
    ("RuntimeExecutionTopologyV02", ("ordered_node_ids", "ordered_edge_ids", "ordered_assignment_ids", "trace_refs", "parent_refs")),
    ("ParentChildScopeProjectionV02", ("parent_allowed_capability_ids", "child_allowed_capability_ids", "parent_forbidden_claims", "child_forbidden_claims")),
    ("FractalCellInputV02", ("ordered_initial_queue_entry_ids", "ordered_required_queue_entry_ids", "ordered_planned_child_cell_ids", "ordered_node_ids", "evidence_refs", "context_refs")),
    ("FractalCellQueueEntryV02", ("queue_reason_codes", "observed_output_refs", "observed_evidence_refs", "advisory_refs")),
    ("FractalReviseObservationV02", ("reason_codes",)),
    ("FractalPartialFailureRecordV02", ("reason_codes", "source_reason_codes", "evidence_refs")),
    ("FractalBackpressureStateV02", ("deferred_queue_entry_ids", "admission_order", "reason_codes")),
    ("FractalCellResultV02", ("ordered_terminal_queue_entry_ids", "ordered_child_result_ids", "accepted_output_refs", "evidence_refs", "partial_failure_ids", "reason_codes", "source_reason_codes")),
    ("FractalRuntimeTraceV02", ("ordered_queue_entry_ids", "cell_input_ids", "cell_result_ids", "scope_projection_ids", "revise_observation_ids", "partial_failure_ids", "backpressure_state_ids", "budget_ids", "abi_artifact_refs", "parent_return_refs")),
    ("FractalRuntimeReportV02", ("ordered_cell_result_ids", "queue_entry_ids", "backpressure_state_ids", "parent_return_refs", "reason_codes")),
    ("FractalRuntimeValidationReportV02", ("reason_codes", "source_reason_codes")),
)

_IDENTITY_PROFILES = {row[0]: row[1:] for row in IDENTITY_PROFILE_ROWS_V02}
_STRUCTURAL_TARGETS = {row[0]: row[1:] for row in STRUCTURAL_VALIDATION_TARGET_ROWS_V02}
_TARGET_STAGES = {row[1]: row[3] for row in STRUCTURAL_VALIDATION_TARGET_ROWS_V02}
_TARGET_STAGES.update({row[0]: row[2] for row in CONTEXTUAL_VALIDATION_TARGET_ROWS_V02})
_CONTEXTUAL_TARGET_ID_KINDS = {row[0]: row[1] for row in CONTEXTUAL_VALIDATION_TARGET_ROWS_V02}
_REASON_POSITION = {reason: index for index, reason in enumerate(PUBLIC_G2D_REASON_CODES)}
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_REF_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{0,511}$")
_REASON_PATTERN = re.compile(r"^g2d_[a-z0-9_]+$")
_MAX_TUPLE_MEMBERS = 4096
_ZERO_SHA256 = "0" * 64


def _sort_reasons(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    known = {value for value in values if value in _REASON_POSITION}
    if not known:
        known = {"g2d_type_invalid"}
    return tuple(sorted(known, key=_REASON_POSITION.__getitem__))


def _text_valid(value: object, *, allow_empty: bool = False) -> bool:
    if type(value) is not str or len(value) > 512 or (not value and not allow_empty):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    if unicodedata.normalize("NFC", value) != value:
        return False
    return not any(ord(char) <= 31 or 127 <= ord(char) <= 159 for char in value)


def _ref_valid(value: object) -> bool:
    return type(value) is str and _REF_PATTERN.fullmatch(value) is not None


def _identity_pattern_valid(value: object, prefix: str) -> bool:
    return type(value) is str and re.fullmatch(re.escape(prefix) + r"[0-9a-f]{64}", value) is not None


def _tuple_valid(value: object, *, unique: bool = False) -> bool:
    if type(value) is not tuple or len(value) > _MAX_TUPLE_MEMBERS:
        return False
    if unique:
        try:
            return len(value) == len(set(value))
        except Exception:
            return False
    return True


def _annotation_valid(value: object, annotation: object) -> bool:
    origin = _get_origin(annotation)
    if origin is types.UnionType:
        return any(_annotation_valid(value, member) for member in _get_args(annotation))
    if origin is tuple:
        if type(value) is not tuple or len(value) > _MAX_TUPLE_MEMBERS:
            return False
        members = _get_args(annotation)
        if len(members) == 2 and members[1] is Ellipsis:
            return all(_annotation_valid(item, members[0]) for item in value)
        return len(value) == len(members) and all(_annotation_valid(item, member) for item, member in zip(value, members, strict=True))
    if origin is dict:
        key_type, item_type = _get_args(annotation)
        return type(value) is dict and all(_annotation_valid(key, key_type) and _annotation_valid(item, item_type) for key, item in value.items())
    if annotation is object:
        return True
    if annotation is None or annotation is type(None):
        return value is None
    if annotation in {str, int, bool, bytes}:
        return type(value) is annotation
    if isinstance(annotation, type):
        return type(value) is annotation
    return False


def _plain_value(value: object, active: set[int]) -> object:
    if value is None or type(value) in {str, int, bool}:
        return value
    if type(value) is float and value == 1.0:
        return value
    if type(value) is tuple:
        marker = id(value)
        if marker in active:
            raise ValueError("g2d_serialization_invalid")
        active.add(marker)
        try:
            return [_plain_value(item, active) for item in value]
        finally:
            active.remove(marker)
    if type(value) is dict:
        marker = id(value)
        if marker in active:
            raise ValueError("g2d_serialization_invalid")
        active.add(marker)
        try:
            if any(type(key) is not str or not _text_valid(key) for key in value):
                raise ValueError("g2d_serialization_invalid")
            return {key: _plain_value(item, active) for key, item in value.items()}
        finally:
            active.remove(marker)
    if type(value) in SERIALIZED_G2D_TYPES_V02:
        return _plain_data_unchecked(value)
    raise ValueError("g2d_serialization_invalid")


def _plain_data_unchecked(value: object, *, omit_identity: bool = False) -> dict[str, object]:
    value_type = type(value)
    if value_type not in SERIALIZED_G2D_TYPES_V02:
        raise ValueError("g2d_type_invalid")
    identity_field = _IDENTITY_PROFILES[value_type][0]
    output: dict[str, object] = {}
    for field in _fields(value_type):
        if omit_identity and field.name == identity_field:
            continue
        output[field.name] = _plain_value(getattr(value, field.name), set())
    _canonical_json_bytes_v01(output)
    return output


def _rebuild_identity(value: object) -> str:
    value_type = type(value)
    if value_type not in SERIALIZED_G2D_TYPES_V02:
        raise ValueError("g2d_type_invalid")
    errors = _annotation_errors(value, value_type)
    if errors:
        raise ValueError(errors[0])
    _identity_field, domain, prefix = _IDENTITY_PROFILES[value_type]
    return prefix + _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(_plain_data_unchecked(value, omit_identity=True)),
    )


def _finish_identity(value: object) -> object:
    identity_field = _IDENTITY_PROFILES[type(value)][0]
    return _replace(value, **{identity_field: _rebuild_identity(value)})


def _annotation_errors(value: object, expected_type: type[object]) -> tuple[str, ...]:
    if type(value) is not expected_type:
        return ("g2d_type_invalid",)
    hints = _get_type_hints(expected_type)
    errors: list[str] = []
    for field in _fields(expected_type):
        item = getattr(value, field.name)
        if _annotation_valid(item, hints[field.name]):
            continue
        if type(item) is bool and hints[field.name] is int:
            errors.append("g2d_boolean_is_not_integer")
        elif type(item) is float:
            errors.append("g2d_float_forbidden")
        elif type(item).__name__ == "Decimal":
            errors.append("g2d_decimal_forbidden")
        elif hints[field.name] is int:
            errors.append("g2d_integer_invalid")
        else:
            errors.append("g2d_field_type_invalid")
    return _sort_reasons(errors) if errors else ()


def _common_errors(value: object, expected_type: type[object]) -> tuple[str, ...]:
    errors = list(_annotation_errors(value, expected_type))
    if errors:
        return _sort_reasons(errors)
    if len(_fields(type(value))) != len(_fields(expected_type)):
        errors.append("g2d_field_count_invalid")
    for field in _fields(expected_type):
        item = getattr(value, field.name)
        if type(item) is str and not _text_valid(item):
            errors.append("g2d_text_invalid")
        elif type(item) is tuple:
            if not _tuple_valid(item):
                errors.append("g2d_field_type_invalid")
            if any(type(member) is str and not _text_valid(member) for member in item):
                errors.append("g2d_text_invalid")
    identity_field, _domain, prefix = _IDENTITY_PROFILES[expected_type]
    identity = getattr(value, identity_field)
    if not _identity_pattern_valid(identity, prefix):
        errors.append("g2d_identity_invalid")
    else:
        try:
            if identity != _rebuild_identity(value):
                errors.append("g2d_identity_mismatch")
        except Exception:
            errors.append("g2d_identity_invalid")
    return _sort_reasons(errors) if errors else ()


def _nonclaim_errors(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for name in (
        "authority_created", "permission_created", "action_commit_packet_created",
        "receipt_created", "final_output_created", "drs_write_created", "effect_created",
    ):
        if hasattr(value, name) and getattr(value, name) is not False:
            errors.append("g2d_topology_authority_claim_forbidden")
    for name in (
        "provider_calls", "model_calls", "network_calls", "connector_calls",
        "external_drs_calls", "action_commit_packets_created", "permissions_created",
        "receipts_created", "final_outputs_created", "drs_writes",
        "authority_created_count", "real_world_effects_count",
    ):
        if hasattr(value, name) and getattr(value, name) != 0:
            errors.append("g2d_topology_authority_claim_forbidden")
    return _sort_reasons(errors) if errors else ()


def _public_reason_tuple_valid(value: object) -> bool:
    return type(value) is tuple and len(value) == len(set(value)) and all(type(item) is str and item in _REASON_POSITION for item in value) and tuple(sorted(value, key=_REASON_POSITION.__getitem__)) == value


def _source_reason_tuple_valid(value: object) -> bool:
    return (
        type(value) is tuple
        and len(value) == len(set(value))
        and all(
            _text_valid(item) and _REASON_PATTERN.fullmatch(item) is None
            for item in value
        )
    )


def _unique_tuple(value: tuple[str, ...]) -> bool:
    return len(value) == len(set(value))


def _identity_tuple(value: tuple[str, ...], prefix: str) -> bool:
    return all(_identity_pattern_valid(item, prefix) for item in value)


def _has_own_identity(value: object, *field_names: str) -> bool:
    identity_name = _IDENTITY_PROFILES[type(value)][0]
    identity = getattr(value, identity_name)
    return any(identity in getattr(value, field_name) for field_name in field_names)


_ENUM_FIELDS = {
    "policy_profile_id": POLICY_PROFILE_IDS,
    "accepted_mode": TOPOLOGY_ELIGIBLE_MODES,
    "node_kind": NODE_KINDS,
    "edge_kind": EDGE_KINDS,
    "assignment_kind": ASSIGNMENT_KINDS,
    "cell_binding_class": CELL_BINDING_CLASSES,
    "scope_binding_class": SCOPE_BINDING_CLASSES,
    "budget_binding_class": BUDGET_BINDING_CLASSES,
    "budget_state": BUDGET_STATES,
    "budget_scope": BUDGET_SCOPES,
    "budget_event_kind": BUDGET_EVENT_KINDS,
    "input_ref_derivation_class": INPUT_REF_DERIVATION_CLASSES,
    "cell_projection_class": CELL_PROJECTION_CLASSES,
    "state": QUEUE_STATES,
    "prior_state": QUEUE_STATES,
    "derived_terminal_state": NODE_TERMINAL_OUTCOMES,
    "outcome": CELL_OUTCOMES,
    "status": VALIDATION_STATUSES,
    "failure_stage": FAILURE_STAGES,
    "parent_disposition": PARENT_DISPOSITIONS,
    "backpressure_reason": BACKPRESSURE_REASONS,
    "validation_target": VALIDATION_TARGETS,
    "runtime_outcome": RUNTIME_OUTCOMES,
    "report_status": REPORT_STATUSES,
    "executor_component_id": EXECUTOR_COMPONENT_IDS,
    "scope_relation": SCOPE_RELATIONS,
    "budget_relation": BUDGET_RELATIONS,
    "predecessor_relation": QUEUE_PREDECESSOR_RELATIONS,
    "topology_version": TOPOLOGY_VERSIONS,
    "report_version": REPORT_VERSIONS,
    "profile_id": PROFILE_IDS,
    "expected_output_kind": EXPECTED_OUTPUT_KINDS,
}


def _specific_errors(value: object) -> tuple[str, ...]:
    errors: list[str] = []
    for field in _fields(type(value)):
        item = getattr(value, field.name)
        if field.name in _ENUM_FIELDS and item is not None and item not in _ENUM_FIELDS[field.name]:
            errors.append("g2d_unknown_enum")
        if type(item) is int and field.name != "progress_units" and item < 0:
            errors.append("g2d_integer_invalid")
    errors.extend(_nonclaim_errors(value))
    for field_name in ("reason_codes", "queue_reason_codes"):
        if hasattr(value, field_name) and not _public_reason_tuple_valid(getattr(value, field_name)):
            errors.append("g2d_serialization_invalid")
    if hasattr(value, "source_reason_codes") and not _source_reason_tuple_valid(value.source_reason_codes):
        if type(value.source_reason_codes) is tuple and any(
            type(item) is str and _REASON_PATTERN.fullmatch(item) is not None
            for item in value.source_reason_codes
        ):
            errors.append("g2d_success_laundering_forbidden")
        else:
            errors.append("g2d_serialization_invalid")
    unique_fields = next(
        (
            field_names
            for type_name, field_names in _STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02
            if type_name == type(value).__name__
        ),
        (),
    )
    if any(not _unique_tuple(getattr(value, field_name)) for field_name in unique_fields):
        errors.append("g2d_tuple_duplicate")

    if type(value) is FractalRuntimePolicyV02:
        fixed = (
            value.policy_profile_id == POLICY_PROFILE_IDS[0]
            and value.policy_version == "v0.2"
            and value.allowed_modes == TOPOLOGY_ELIGIBLE_MODES
            and value.allowed_node_kinds == NODE_KINDS
            and value.allowed_edge_kinds == EDGE_KINDS
            and value.allowed_assignment_kinds == ASSIGNMENT_KINDS
            and value.recursive_mode == "full_fractal"
            and value.recursive_capability_id == CAP_FRACTAL_CHILD
            and value.forbidden_claims == FORBIDDEN_OUTPUT_KINDS
            and value.reference_child_count == 2
            and value.queue_profile_id == "node_work_queue_v02"
            and value.budget_profile_id == "fractal_runtime_budget_g2d_v02"
            and (value.max_depth, value.max_fan_out, value.max_total_cells) == (3, 4, 21)
            and (value.max_parallelism, value.max_revise_count, value.max_consecutive_no_progress) == (4, 2, 2)
            and (value.max_wall_time_units, value.max_token_budget, value.max_provider_calls) == (1000, 100000, 0)
            and value.root_review_required is True
            and len(value.allowed_capability_ids) == len(set(value.allowed_capability_ids))
            and _unique_tuple(value.permitted_child_scope_refs)
            and all(capability in value.allowed_capability_ids for capability in LOCAL_CAPS)
        )
        if not fixed:
            errors.append("g2d_topology_policy_invalid")
    elif type(value) is FractalRuntimeBudgetV02:
        maxima = (
            value.max_wall_time_units,
            value.max_token_budget,
            value.max_provider_calls,
            value.max_total_cells,
            value.max_revise_count,
            value.max_parallelism,
        )
        consumed = (
            value.consumed_wall_time_units,
            value.consumed_token_budget,
            value.consumed_provider_calls,
            value.consumed_cell_count,
            value.consumed_revise_count,
            value.current_parallelism,
        )
        remaining = (
            value.remaining_wall_time_units,
            value.remaining_token_budget,
            value.remaining_provider_calls,
            value.remaining_cell_count,
            value.remaining_revise_count,
            value.remaining_parallel_slots,
        )
        if any(part < 0 for part in maxima + consumed + remaining):
            errors.append("g2d_budget_negative")
        if any(used + left != maximum for used, left, maximum in zip(consumed, remaining, maxima, strict=True)):
            errors.append("g2d_budget_debit_mismatch")
        if value.budget_scope == "ROOT_GLOBAL_AND_CELL" and value.allocation_parent_budget_id is not None:
            errors.append("g2d_budget_predecessor_invalid")
        if value.budget_scope == "CHILD_CELL_LOCAL" and value.allocation_parent_budget_id is None:
            errors.append("g2d_budget_predecessor_invalid")
        if value.budget_event_kind == "INITIAL_ALLOCATION" and (value.budget_state != "ALLOCATED" or value.predecessor_budget_id is not None or value.consumed_cell_count != 0):
            errors.append("g2d_budget_predecessor_invalid")
        if value.budget_event_kind != "INITIAL_ALLOCATION" and value.predecessor_budget_id is None:
            errors.append("g2d_budget_predecessor_invalid")
        if value.budget_state == "ALLOCATED" and value.budget_event_kind != "INITIAL_ALLOCATION":
            errors.append("g2d_budget_state_transition_invalid")
        if value.budget_state == "FINAL" and value.budget_event_kind != "FINALIZE":
            errors.append("g2d_budget_state_transition_invalid")
        if value.budget_event_kind in {"ACTIVATE", "CELL_CREATE", "START_NODE", "FINISH_NODE", "REVISE", "CHILD_AGGREGATE"} and value.budget_state != "ACTIVE":
            errors.append("g2d_budget_state_transition_invalid")
        if value.root_review_required is not True:
            errors.append("g2d_budget_invalid")
    elif type(value) is RuntimeTopologySourceBindingV02:
        if value.accepted_mode not in TOPOLOGY_ELIGIBLE_MODES or value.root_review_required is not True:
            errors.append("g2d_topology_source_binding_invalid")
        if _SHA256_PATTERN.fullmatch(value.route_eligibility_artifact_sha256) is None:
            errors.append("g2d_identity_invalid")
        known_trace_refs = (
            value.source_decision_artifact_id,
            value.transition_registry_id,
            value.post_root_transition_decision_id,
        )
        residual_trace_refs = tuple(
            item for item in value.source_trace_refs if item not in known_trace_refs
        )
        raw_g2c_ids = (
            value.source_root_decision_result_id,
            value.source_root_transition_decision_id,
            value.proposal_transition_decision_id,
            value.post_root_transition_decision_id,
            value.transition_registry_id,
        )
        exact_identifier_envelope = (
            _identity_pattern_valid(value.route_eligibility_artifact_id, "emabi_route_v01:")
            and _identity_pattern_valid(value.source_decision_artifact_id, "emabi_decision_v01:")
            and _identity_pattern_valid(value.source_proposal_artifact_id, "emabi_proposal_v01:")
            and _identity_pattern_valid(value.selected_local_mode_profile_id, "emprofile_v01:")
            and _identity_pattern_valid(value.selected_feasibility_row_id, "emrow_v01:")
            and _identity_pattern_valid(value.source_mode_profile_set_id, "emprofiles_v01:")
            and _identity_pattern_valid(value.source_time_envelope_ref, "emtime_v01:")
            and all(_SHA256_PATTERN.fullmatch(item) is not None for item in raw_g2c_ids)
            and value.g2c_abi_profile_id == "execution_mode_router_g2c_abi_profile_v01"
        )
        exact_route_trace = (
            len(set(known_trace_refs)) == 3
            and len(value.source_trace_refs) == 4
            and _unique_tuple(value.source_trace_refs)
            and value.source_trace_refs == tuple(sorted(value.source_trace_refs))
            and all(item in value.source_trace_refs for item in known_trace_refs)
            and len(residual_trace_refs) == 1
            and _identity_pattern_valid(residual_trace_refs[0], "emdecision_v01:")
            and sum(
                _identity_pattern_valid(item, "emdecision_v01:")
                for item in value.source_trace_refs
            ) == 1
            and not any(
                _identity_pattern_valid(item, "emdecision_v01:")
                for item in known_trace_refs
            )
            and value.route_eligibility_artifact_id not in value.source_trace_refs
            and value.source_proposal_artifact_id not in value.source_trace_refs
        )
        if (
            not exact_identifier_envelope
            or not _identity_pattern_valid(value.runtime_policy_id, "frpolicy_v02:")
            or not _unique_tuple(value.required_downstream_capability_ids)
            or not _unique_tuple(value.permitted_narrower_scope_refs)
            or not exact_route_trace
            or value.source_parent_refs != (value.source_decision_artifact_id,)
            or value.source_binding_id in value.source_trace_refs
            or value.source_binding_id in value.source_parent_refs
        ):
            errors.append("g2d_topology_source_binding_invalid")
    elif type(value) is RuntimeTopologySeedV02:
        if value.seed_version != "v0.2" or value.profile_id != PROFILE_IDS[0] or value.root_review_required is not True:
            errors.append("g2d_topology_seed_invalid")
        try:
            expected_root_cell_id = derive_fractal_root_cell_id_v02(
                source_binding_id=value.source_binding_id,
                runtime_policy_id=value.runtime_policy_id,
                accepted_mode=value.accepted_mode,
                accepted_scope_ref=value.accepted_scope_ref,
            )
        except (TypeError, ValueError):
            expected_root_cell_id = None
        expected_trace_suffix = (
            value.source_binding_id,
            value.runtime_policy_id,
            value.root_cell_id,
            value.source_time_envelope_ref,
        )
        parents = value.parent_refs
        exact_parents = (
            len(parents) == 4
            and _unique_tuple(parents)
            and _identity_pattern_valid(parents[0], "emabi_route_v01:")
            and _identity_pattern_valid(parents[1], "emabi_decision_v01:")
            and _identity_pattern_valid(parents[2], "emabi_proposal_v01:")
            and parents[3] == value.source_binding_id
            and _identity_pattern_valid(parents[3], "frsource_v02:")
        )
        source_trace = value.trace_refs[:4] if len(value.trace_refs) == 8 else ()
        excluded_source_trace_refs = (
            *((parents[0], parents[2]) if exact_parents else ()),
            value.source_binding_id,
            value.runtime_policy_id,
            value.root_cell_id,
            value.source_time_envelope_ref,
        )
        exact_source_trace = (
            len(source_trace) == 4
            and _unique_tuple(source_trace)
            and source_trace == tuple(sorted(source_trace))
            and exact_parents
            and source_trace.count(parents[1]) == 1
            and sum(
                _identity_pattern_valid(item, "emdecision_v01:")
                for item in source_trace
            ) == 1
            and sum(_SHA256_PATTERN.fullmatch(item) is not None for item in source_trace) == 2
            and all(
                _identity_pattern_valid(item, "emabi_decision_v01:")
                or _identity_pattern_valid(item, "emdecision_v01:")
                or _SHA256_PATTERN.fullmatch(item) is not None
                for item in source_trace
            )
            and not any(item in source_trace for item in excluded_source_trace_refs)
        )
        if value.root_cell_id != expected_root_cell_id:
            errors.append("g2d_root_cell_identity_invalid")
        if (
            not _identity_pattern_valid(value.source_binding_id, "frsource_v02:")
            or not _identity_pattern_valid(value.runtime_policy_id, "frpolicy_v02:")
            or not _identity_pattern_valid(value.root_cell_id, "frrootcell_v02:")
            or not _identity_pattern_valid(value.source_time_envelope_ref, "emtime_v01:")
            or len(value.trace_refs) != 8
            or value.trace_refs[4:] != expected_trace_suffix
            or not exact_source_trace
            or not exact_parents
        ):
            errors.append("g2d_topology_lineage_mismatch")
        if _has_own_identity(value, "trace_refs", "parent_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is RuntimeTopologyNodeV02:
        mode_rows = dict(MODE_NODE_TEMPLATE_ROWS_V02).get(value.accepted_mode, ())
        row = mode_rows[value.canonical_index] if 0 <= value.canonical_index < len(mode_rows) else None
        expected_required_caps = None if row is None or row[5] == ("SRC_CAPS",) else row[5]
        exact_row = row is not None and (
            value.node_kind,
            value.cell_binding_class,
            value.scope_binding_class,
            value.budget_binding_class,
            value.input_ref_derivation_class,
            value.expected_output_kind,
            value.required,
            value.recursive_expansion_allowed,
            value.root_review_required,
        ) == (row[1], row[2], row[3], row[4], row[8], row[9], row[10], row[11], row[12])
        if not exact_row or value.depth != 0 or not _ref_valid(value.scope_ref):
            errors.append("g2d_topology_node_invalid")
        if expected_required_caps is not None and value.required_capability_ids != expected_required_caps:
            errors.append("g2d_mode_template_matrix_invalid")
        if (
            not value.required_capability_ids
            or not _unique_tuple(value.required_capability_ids)
            or not _unique_tuple(value.allowed_capability_ids)
            or not set(value.required_capability_ids).issubset(value.allowed_capability_ids)
            or not set(LOCAL_CAPS).issubset(value.allowed_capability_ids)
            or value.forbidden_claims != FORBIDDEN_OUTPUT_KINDS
        ):
            errors.append("g2d_topology_node_invalid")
        source_binding_ref = value.trace_refs[1] if len(value.trace_refs) == 4 else None
        expected_trace = (
            value.topology_seed_id,
            source_binding_ref,
            str(value.canonical_index),
            value.node_kind,
        )
        if (
            value.trace_refs != expected_trace
            or not _identity_pattern_valid(value.topology_seed_id, "frseed_v02:")
            or not _identity_pattern_valid(source_binding_ref, "frsource_v02:")
        ):
            errors.append("g2d_topology_lineage_mismatch")
        if value.input_ref_derivation_class == "SOURCE_CONTEXT":
            if (
                len(value.input_refs) != 3
                or value.input_refs[0] != source_binding_ref
                or not _identity_pattern_valid(value.input_refs[0], "frsource_v02:")
                or not _identity_pattern_valid(value.input_refs[1], "frpolicy_v02:")
                or not _ref_valid(value.input_refs[2])
            ):
                errors.append("g2d_static_input_derivation_invalid")
        elif value.input_refs:
            errors.append("g2d_static_input_derivation_invalid")
        if _has_own_identity(value, "input_refs", "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is RuntimeTopologyEdgeV02:
        if value.required is not True or value.evidence_flow_allowed is not True or value.authority_flow_allowed is not False or value.root_review_required is not True or value.source_node_id == value.target_node_id:
            errors.append("g2d_topology_edge_invalid")
        expected_trace = (
            value.topology_seed_id,
            value.source_node_id,
            value.target_node_id,
            str(value.canonical_index),
            value.cell_projection_class,
        )
        if (
            value.trace_refs != expected_trace
            or not _identity_pattern_valid(value.topology_seed_id, "frseed_v02:")
            or not _identity_pattern_valid(value.source_node_id, "frnode_v02:")
            or not _identity_pattern_valid(value.target_node_id, "frnode_v02:")
        ):
            errors.append("g2d_topology_lineage_mismatch")
        if _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is RuntimeAssignmentV02:
        if value.provider_call_allowed is not False or value.network_call_allowed is not False or value.connector_call_allowed is not False or value.root_review_required is not True:
            errors.append("g2d_topology_assignment_invalid")
        expected_trace = (
            value.topology_seed_id,
            value.node_id,
            str(value.canonical_index),
            value.executor_component_id,
        )
        if (
            value.trace_refs != expected_trace
            or not _identity_pattern_valid(value.topology_seed_id, "frseed_v02:")
            or not _identity_pattern_valid(value.node_id, "frnode_v02:")
        ):
            errors.append("g2d_assignment_trace_invalid")
        if not value.capability_ids or not _unique_tuple(value.capability_ids):
            errors.append("g2d_topology_assignment_invalid")
        if _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is RuntimeExecutionTopologyV02:
        if value.topology_version != "v0.2" or value.root_review_required is not True:
            errors.append("g2d_topology_identity_mismatch")
        if any(len(items) != len(set(items)) for items in (value.ordered_node_ids, value.ordered_edge_ids, value.ordered_assignment_ids)):
            errors.append("g2d_tuple_duplicate")
        mode_counts = {
            mode: (len(nodes), len(dict(MODE_EDGE_TEMPLATE_ROWS_V02)[mode]), len(dict(MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[mode]))
            for mode, nodes in MODE_NODE_TEMPLATE_ROWS_V02
        }
        if (len(value.ordered_node_ids), len(value.ordered_edge_ids), len(value.ordered_assignment_ids)) != mode_counts.get(value.accepted_mode):
            errors.append("g2d_mode_template_matrix_invalid")
        if (
            not _identity_tuple(value.ordered_node_ids, "frnode_v02:")
            or not _identity_tuple(value.ordered_edge_ids, "fredge_v02:")
            or not _identity_tuple(value.ordered_assignment_ids, "frassign_v02:")
            or not _identity_pattern_valid(value.topology_seed_id, "frseed_v02:")
            or not _identity_pattern_valid(value.source_binding_id, "frsource_v02:")
            or not _identity_pattern_valid(value.runtime_policy_id, "frpolicy_v02:")
            or not _identity_pattern_valid(value.root_cell_id, "frrootcell_v02:")
            or not _identity_pattern_valid(value.global_budget_id, "frbudget_v02:")
        ):
            errors.append("g2d_topology_identity_mismatch")
        expected_trace = (
            value.source_binding_id,
            value.root_cell_id,
            value.topology_seed_id,
            value.global_budget_id,
            *value.ordered_node_ids,
            *value.ordered_edge_ids,
            *value.ordered_assignment_ids,
        )
        expected_parents = (
            value.source_route_eligibility_artifact_id,
            value.source_root_decision_artifact_id,
            value.source_proposal_artifact_id,
            value.source_binding_id,
            value.topology_seed_id,
            value.global_budget_id,
        )
        if value.trace_refs != expected_trace or value.parent_refs != expected_parents:
            errors.append("g2d_topology_lineage_mismatch")
        if _has_own_identity(value, "trace_refs", "parent_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is ParentChildScopeProjectionV02:
        if value.child_depth < 1 or value.child_ttl_units > value.parent_ttl_units or value.root_review_required is not True:
            errors.append("g2d_child_depth_mismatch")
        if not set(value.child_allowed_capability_ids).issubset(value.parent_allowed_capability_ids):
            errors.append("g2d_child_capability_widening")
        if not set(value.parent_forbidden_claims).issubset(value.child_forbidden_claims):
            errors.append("g2d_child_forbidden_narrowing")
        expected_scope_relation = "EQUAL" if value.parent_scope_ref == value.child_scope_ref else "NARROWER"
        if value.scope_relation != expected_scope_relation:
            errors.append("g2d_scope_relation_unproven")
        if (
            value.budget_relation != "CHILD_BUDGET"
            or value.parent_cell_id == value.child_cell_id
            or value.child_budget_id in {value.parent_budget_id, value.global_budget_id}
            or not _unique_tuple(value.parent_allowed_capability_ids)
            or not _unique_tuple(value.child_allowed_capability_ids)
            or not _unique_tuple(value.parent_forbidden_claims)
            or not _unique_tuple(value.child_forbidden_claims)
        ):
            errors.append("g2d_child_lineage_mismatch")
        if len(value.parent_lineage_refs) != 6:
            errors.append("g2d_child_lineage_mismatch")
        else:
            expected_parent_lineage = (
                value.topology_id,
                value.parent_lineage_refs[1],
                value.parent_cell_id,
                value.parent_budget_id,
                value.global_budget_id,
                value.parent_scope_ref,
            )
            expected_child_lineage = expected_parent_lineage + (
                value.child_cell_id,
                value.child_budget_id,
                value.child_scope_ref,
                str(value.child_depth),
            )
            if (
                value.parent_lineage_refs != expected_parent_lineage
                or value.child_lineage_refs != expected_child_lineage
                or not _identity_pattern_valid(value.parent_lineage_refs[1], "frseed_v02:")
            ):
                errors.append("g2d_child_lineage_mismatch")
        if len(value.proof_refs) != 5 or _has_own_identity(value, "parent_lineage_refs", "child_lineage_refs", "proof_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalCellInputV02:
        mode_rows = dict(MODE_NODE_TEMPLATE_ROWS_V02).get(value.accepted_mode, ())
        expected_node_count = len(mode_rows)
        expected_required_outputs = tuple(row[9] for row in mode_rows if row[10])
        expected_child_count = 2 if value.accepted_mode == "full_fractal" else 0
        if value.initial_revise_count != 0 or value.root_review_required is not True:
            errors.append("g2d_cell_input_invalid")
        if (
            value.requested_child_count != expected_child_count
            or len(value.ordered_planned_child_cell_ids) != expected_child_count
            or len(value.ordered_node_ids) != expected_node_count
            or len(value.ordered_initial_queue_entry_ids) != expected_node_count
            or len(value.ordered_required_queue_entry_ids) != expected_node_count
            or value.required_output_kinds != expected_required_outputs
        ):
            errors.append("g2d_node_instance_geometry_invalid")
        if value.ordered_initial_queue_entry_ids != value.ordered_required_queue_entry_ids:
            errors.append("g2d_cell_input_build_order_invalid")
        if value.forbidden_output_kinds != FORBIDDEN_OUTPUT_KINDS:
            errors.append("g2d_cell_input_invalid")
        if any(
            not _unique_tuple(items)
            for items in (
                value.ordered_initial_queue_entry_ids,
                value.ordered_required_queue_entry_ids,
                value.ordered_planned_child_cell_ids,
                value.ordered_node_ids,
                value.evidence_refs,
                value.context_refs,
            )
        ):
            errors.append("g2d_tuple_duplicate")
        if value.parent_cell_id is None:
            if value.cell_depth != 0 or value.scope_projection_id is not None or not _identity_pattern_valid(value.cell_id, "frrootcell_v02:"):
                errors.append("g2d_cell_input_invalid")
        elif value.cell_depth < 1 or value.scope_projection_id is None or not _identity_pattern_valid(value.cell_id, "frchildcell_v02:"):
            errors.append("g2d_cell_input_invalid")
        expected_trace = (
            value.topology_id,
            value.cell_id,
            *((value.scope_projection_id,) if value.scope_projection_id is not None else ()),
            value.cell_budget_id,
            value.global_budget_id,
            *value.ordered_node_ids,
            *value.ordered_initial_queue_entry_ids,
            *value.ordered_required_queue_entry_ids,
        )
        if value.trace_refs != expected_trace or _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalCellQueueEntryV02:
        if value.root_review_required is not True:
            errors.append("g2d_queue_entry_invalid")
        initial = value.predecessor_queue_entry_id is None
        if initial != (value.predecessor_relation == "INITIAL_NONE"):
            errors.append("g2d_queue_predecessor_invalid")
        if initial != (value.prior_state is None):
            errors.append("g2d_queue_predecessor_invalid")
        if value.state in {"PENDING", "READY", "RUNNING"} and (value.observed_output_refs or value.observed_evidence_refs or value.advisory_refs):
            errors.append("g2d_queue_entry_invalid")
        if value.state in {"READY", "RUNNING"} and value.queue_reason_codes:
            errors.append("g2d_queue_entry_invalid")
        if initial and (value.state != "PENDING" or value.snapshot_sequence != 0 or value.admission_round != 0):
            errors.append("g2d_queue_sequence_invalid")
        if not initial and value.snapshot_sequence == 0:
            errors.append("g2d_queue_sequence_invalid")
        if _has_own_identity(value, "lineage_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalReviseObservationV02:
        progress = value.newly_validated_evidence_count + value.newly_resolved_constraints_count + value.newly_accepted_outputs_count - value.newly_introduced_conflicts_count
        if value.progress_units != progress or value.root_review_required is not True:
            errors.append("g2d_revise_progress_mismatch")
        terminal = value.derived_terminal_state in {"DEADEND", "NEEDS_USER"}
        if terminal == value.revise_eligible:
            errors.append("g2d_revise_observation_invalid")
        expected_reasons = (
            ("g2d_resolvable_input_needs_user",)
            if value.derived_terminal_state == "NEEDS_USER"
            else ("g2d_no_progress_deadend",)
            if value.derived_terminal_state == "DEADEND"
            else ()
        )
        expected_trace = (
            value.topology_id,
            value.cell_id,
            value.queue_entry_id,
            value.cell_budget_before_id,
            value.global_budget_before_id,
            str(value.revision_index),
        )
        if value.reason_codes != expected_reasons or value.trace_refs != expected_trace or value.max_consecutive_non_positive_count < 1:
            errors.append("g2d_revise_observation_invalid")
        if _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalPartialFailureRecordV02:
        expected_revise = value.parent_disposition == "DEGRADED" and "g2d_revise_progress_valid" in value.reason_codes
        expected_trace = (
            value.topology_id,
            value.parent_cell_id,
            value.child_cell_id,
            value.child_result_id,
            value.allocated_cell_budget_id,
            value.final_cell_budget_id,
            value.global_budget_id,
        )
        if (
            value.retry_eligible is not False
            or value.root_review_required is not True
            or value.parent_disposition == "COMPLETED"
            or value.revise_eligible is not expected_revise
            or value.parent_cell_id == value.child_cell_id
            or value.allocated_cell_budget_id == value.final_cell_budget_id
            or value.final_cell_budget_id == value.global_budget_id
            or not _unique_tuple(value.evidence_refs)
            or value.trace_refs != expected_trace
        ):
            errors.append("g2d_partial_failure_invalid")
        if _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalBackpressureStateV02:
        if value.running_count + value.ready_count != value.queue_capacity or value.pending_count != len(value.deferred_queue_entry_ids) or value.pending_count < 1:
            errors.append("g2d_backpressure_invalid")
        expected_lineage = (
            value.topology_id,
            value.policy_id,
            value.global_budget_id,
            str(value.evaluated_round),
            *value.admission_order,
        )
        if (
            value.no_work_dropped is not True
            or value.root_review_required is not True
            or value.backpressure_reason != "PARALLELISM_CAPACITY_EXHAUSTED"
            or value.reason_codes != ("g2d_transition_backpressure_deferred",)
            or not _unique_tuple(value.deferred_queue_entry_ids)
            or not _unique_tuple(value.admission_order)
            or not set(value.deferred_queue_entry_ids).issubset(value.admission_order)
            or value.lineage_refs != expected_lineage
        ):
            errors.append("g2d_backpressure_work_drop_forbidden")
        if _has_own_identity(value, "lineage_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalCellResultV02:
        if value.parent_return_required is not True or value.root_review_required is not True:
            errors.append("g2d_root_result_required_for_parent_return")
        if any(
            not _unique_tuple(items)
            for items in (
                value.ordered_child_result_ids,
                value.partial_failure_ids,
                value.accepted_output_refs,
                value.evidence_refs,
            )
        ):
            errors.append("g2d_cell_result_postorder_invalid")
        if not _unique_tuple(value.ordered_terminal_queue_entry_ids):
            errors.append("g2d_cell_result_postorder_invalid")
        if value.result_id in value.ordered_child_result_ids:
            errors.append("g2d_partial_failure_result_cycle")
        if value.parent_cell_id is None:
            if value.cell_depth != 0 or not _identity_pattern_valid(value.cell_id, "frrootcell_v02:") or value.final_cell_budget_id != value.global_budget_id:
                errors.append("g2d_cell_result_context_mismatch")
        elif value.cell_depth < 1 or not _identity_pattern_valid(value.cell_id, "frchildcell_v02:") or value.final_cell_budget_id == value.global_budget_id:
            errors.append("g2d_cell_result_context_mismatch")
        expected_trace = (
            value.topology_id,
            value.cell_input_id,
            *value.ordered_terminal_queue_entry_ids,
            *value.ordered_child_result_ids,
            *value.partial_failure_ids,
            value.allocated_cell_budget_id,
            value.final_cell_budget_id,
            value.global_budget_id,
            value.pre_result_validation_report_id,
            value.post_vv_report_ref,
            value.gt_advisory_ref,
        )
        if value.trace_refs != expected_trace or _has_own_identity(value, "trace_refs"):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalRuntimeTraceV02:
        if value.root_review_required is not True or len(value.ordered_queue_entry_ids) != len(value.state_transition_decision_ids):
            errors.append("g2d_runtime_trace_invalid")
        unique_inventories = (
            value.ordered_queue_entry_ids,
            value.cell_input_ids,
            value.cell_result_ids,
            value.scope_projection_ids,
            value.revise_observation_ids,
            value.partial_failure_ids,
            value.backpressure_state_ids,
            value.budget_ids,
            value.abi_artifact_refs,
        )
        if any(not _unique_tuple(items) for items in unique_inventories):
            errors.append("g2d_tuple_duplicate")
        if (
            len(value.transition_refs) != len(value.state_transition_decision_ids) + 2
            or value.transition_refs[1:-1] != value.state_transition_decision_ids
            or len(value.parent_return_refs) != 1
        ):
            errors.append("g2d_trace_lineage_invalid")
        if any(value.trace_id in items for items in (*unique_inventories, value.transition_refs, value.parent_return_refs)):
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalRuntimeReportV02:
        counts = value.completed_cell_count + value.degraded_cell_count + value.blocked_cell_count + value.needs_user_cell_count + value.deadend_cell_count
        outcome_counts = {
            "COMPLETED": value.completed_cell_count,
            "DEGRADED": value.degraded_cell_count,
            "BLOCKED": value.blocked_cell_count,
            "NEEDS_USER": value.needs_user_cell_count,
            "DEADEND": value.deadend_cell_count,
        }
        if (
            value.report_version != "v0.2"
            or value.profile_id != PROFILE_IDS[0]
            or value.report_status != "PASS"
            or value.root_review_required is not True
            or value.topology_created_count != 1
            or counts != len(value.ordered_cell_result_ids)
            or not value.ordered_cell_result_ids
            or outcome_counts.get(value.runtime_outcome, 0) < 1
            or len(value.parent_return_refs) != 1
            or any(
                not _unique_tuple(items)
                for items in (
                    value.ordered_cell_result_ids,
                    value.queue_entry_ids,
                    value.backpressure_state_ids,
                )
            )
        ):
            errors.append("g2d_runtime_report_invalid")
        if value.report_id in value.parent_return_refs:
            errors.append("g2d_identity_dependency_cycle")
    elif type(value) is FractalRuntimeValidationReportV02:
        errors.extend(_validation_report_semantic_errors(value))
    return _sort_reasons(errors) if errors else ()


def _validation_report_semantic_errors(value: FractalRuntimeValidationReportV02) -> tuple[str, ...]:
    errors: list[str] = []
    if value.validation_target not in VALIDATION_TARGETS:
        errors.append("g2d_validation_target_id_mismatch")
    expected_stage = _TARGET_STAGES.get(value.validation_target)
    if value.status == "PASS":
        if value.failure_stage != "NONE" or value.return_to_root_required is not False or value.reason_codes or value.source_reason_codes:
            errors.append("g2d_validation_status_stage_mismatch")
        if value.validation_target == "SOURCE_CONTEXT_STRUCTURAL":
            if value.validated_object_id is not None:
                errors.append("g2d_validation_target_id_mismatch")
        elif value.validated_object_id is None:
            errors.append("g2d_validation_target_id_mismatch")
        else:
            kind = _CONTEXTUAL_TARGET_ID_KINDS.get(value.validation_target)
            if kind is not None and kind.endswith(":") and not _identity_pattern_valid(value.validated_object_id, kind):
                errors.append("g2d_validation_target_id_mismatch")
            structural = next((row for row in STRUCTURAL_VALIDATION_TARGET_ROWS_V02 if row[1] == value.validation_target), None)
            if structural is not None:
                prefix = _IDENTITY_PROFILES[structural[0]][2]
                if not _identity_pattern_valid(value.validated_object_id, prefix):
                    errors.append("g2d_validation_target_id_mismatch")
    elif value.status == "FAIL_CLOSED":
        if value.failure_stage == "NONE" or value.validated_object_id is not None or value.return_to_root_required is not True or (not value.reason_codes and not value.source_reason_codes):
            errors.append("g2d_validation_status_stage_mismatch")
        if expected_stage is not None and value.failure_stage != expected_stage:
            errors.append("g2d_validation_status_stage_mismatch")
    else:
        errors.append("g2d_validation_status_stage_mismatch")
    if value.root_review_required is not True:
        errors.append("g2d_validation_status_stage_mismatch")
    return _sort_reasons(errors) if errors else ()


def _serialized_errors(value: object, expected_type: type[object]) -> tuple[str, ...]:
    common = list(_common_errors(value, expected_type))
    if type(value) is expected_type and not _annotation_errors(value, expected_type):
        common.extend(_specific_errors(value))
    return _sort_reasons(common) if common else ()


def _structural_report(value: object, expected_type: type[object]) -> FractalRuntimeValidationReportV02:
    _target, identity_field, stage = _STRUCTURAL_TARGETS[expected_type]
    errors = _serialized_errors(value, expected_type)
    return build_fractal_runtime_validation_report_v02(
        validation_target=expected_type.__name__,
        validated_object_id=None if errors else getattr(value, identity_field),
        failure_stage=stage if errors else "NONE",
        reason_codes=errors,
        source_reason_codes=(),
    )


def _validate_serialized(value: object, expected_type: type[object]) -> FractalRuntimeValidationReportV02:
    try:
        return _structural_report(value, expected_type)
    except Exception:
        _target, _identity_field, stage = _STRUCTURAL_TARGETS[expected_type]
        return build_fractal_runtime_validation_report_v02(
            validation_target=expected_type.__name__,
            validated_object_id=None,
            failure_stage=stage,
            reason_codes=("g2d_type_invalid",),
            source_reason_codes=(),
        )


def _serialize_serialized(value: object, expected_type: type[object]) -> dict[str, object]:
    errors = _serialized_errors(value, expected_type)
    if errors:
        raise ValueError(errors[0])
    return _plain_data_unchecked(value)


def _rebuild_serialized(value: object, expected_type: type[object]) -> str:
    if type(value) is not expected_type:
        raise ValueError("g2d_type_invalid")
    return _rebuild_identity(value)


def _require_valid(value: object, expected_type: type[object], reason: str) -> None:
    if _serialized_errors(value, expected_type):
        raise ValueError(reason)


def _require_text_tuple(value: object, *, public_reasons: bool = False) -> tuple[str, ...]:
    if type(value) is not tuple or len(value) > _MAX_TUPLE_MEMBERS or len(value) != len(set(value)):
        raise ValueError("g2d_tuple_duplicate")
    if public_reasons:
        if not _public_reason_tuple_valid(value):
            raise ValueError("g2d_serialization_invalid")
    elif any(not _text_valid(item) for item in value):
        raise ValueError("g2d_text_invalid")
    return value


def _require_source_reason_tuple(value: object) -> tuple[str, ...]:
    source_reasons = _require_text_tuple(value)
    if not _source_reason_tuple_valid(source_reasons):
        raise ValueError("g2d_success_laundering_forbidden")
    return source_reasons


def _plain_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes_v01(value)).hexdigest()


def build_fractal_runtime_policy_v02(
    *,
    required_downstream_capability_ids: tuple[str, ...],
    permitted_child_scope_refs: tuple[str, ...],
) -> FractalRuntimePolicyV02:
    required = _require_text_tuple(required_downstream_capability_ids)
    scopes = _require_text_tuple(permitted_child_scope_refs)
    allowed = required + tuple(item for item in LOCAL_CAPS if item not in required)
    provisional = FractalRuntimePolicyV02(
        policy_id="frpolicy_v02:" + _ZERO_SHA256,
        policy_profile_id="fractal_runtime_policy_g2d_v02",
        policy_version="v0.2",
        allowed_modes=TOPOLOGY_ELIGIBLE_MODES,
        allowed_node_kinds=NODE_KINDS,
        allowed_edge_kinds=EDGE_KINDS,
        allowed_assignment_kinds=ASSIGNMENT_KINDS,
        recursive_mode="full_fractal",
        recursive_capability_id=CAP_FRACTAL_CHILD,
        allowed_capability_ids=allowed,
        forbidden_claims=FORBIDDEN_OUTPUT_KINDS,
        permitted_child_scope_refs=scopes,
        reference_child_count=2,
        queue_profile_id="node_work_queue_v02",
        budget_profile_id="fractal_runtime_budget_g2d_v02",
        max_depth=3,
        max_fan_out=4,
        max_total_cells=21,
        max_parallelism=4,
        max_revise_count=2,
        max_consecutive_no_progress=2,
        max_wall_time_units=1000,
        max_token_budget=100000,
        max_provider_calls=0,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_runtime_policy_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalRuntimePolicyV02)


def fractal_runtime_policy_to_plain_data_v02(value: FractalRuntimePolicyV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalRuntimePolicyV02)


def rebuild_fractal_runtime_policy_identity_v02(value: FractalRuntimePolicyV02) -> str:
    return _rebuild_serialized(value, FractalRuntimePolicyV02)


def _budget_counter_values(
    *,
    policy: FractalRuntimePolicyV02,
    allocation_parent_budget: FractalRuntimeBudgetV02 | None,
    predecessor_budget: FractalRuntimeBudgetV02 | None,
    budget_scope: str,
    budget_event_kind: str,
    budget_context_input: FractalCellInputV02 | None,
    canonical_child_index: int | None,
    paired_cell_budget: FractalRuntimeBudgetV02 | None,
) -> tuple[int, ...]:
    if budget_event_kind == "INITIAL_ALLOCATION":
        if budget_scope == "ROOT_GLOBAL_AND_CELL":
            maxima = (
                policy.max_depth,
                policy.max_fan_out,
                policy.max_total_cells,
                policy.max_parallelism,
                policy.max_revise_count,
                policy.max_wall_time_units,
                policy.max_token_budget,
                policy.max_provider_calls,
            )
        else:
            if allocation_parent_budget is None or budget_context_input is None or canonical_child_index is None:
                raise ValueError("g2d_budget_event_context_invalid")
            sibling_count = budget_context_input.requested_child_count
            if sibling_count <= 0 or not 0 <= canonical_child_index < sibling_count:
                raise ValueError("g2d_budget_allocation_oversubscribed")
            remaining = (
                allocation_parent_budget.remaining_cell_count,
                allocation_parent_budget.remaining_revise_count,
                allocation_parent_budget.remaining_wall_time_units,
                allocation_parent_budget.remaining_token_budget,
                allocation_parent_budget.remaining_provider_calls,
            )
            shares = tuple(total // sibling_count + (1 if canonical_child_index < total % sibling_count else 0) for total in remaining)
            subtree_cap = sum(policy.max_fan_out**index for index in range(policy.max_depth - budget_context_input.cell_depth - 1))
            maxima = (
                policy.max_depth,
                policy.max_fan_out,
                min(shares[0], subtree_cap),
                0,
                shares[1],
                shares[2],
                shares[3],
                shares[4],
            )
        max_depth, max_fan_out, max_cells, max_parallelism, max_revise, max_wall, max_token, max_provider = maxima
        return (
            max_depth, max_fan_out, max_cells, max_parallelism, max_revise, max_wall, max_token, max_provider,
            0, 0, 0, 0, 0, 0,
            max_wall, max_token, max_provider, max_cells, max_revise, max_parallelism,
        )
    if predecessor_budget is None:
        raise ValueError("g2d_budget_predecessor_invalid")
    values = [
        predecessor_budget.max_depth,
        predecessor_budget.max_fan_out,
        predecessor_budget.max_total_cells,
        predecessor_budget.max_parallelism,
        predecessor_budget.max_revise_count,
        predecessor_budget.max_wall_time_units,
        predecessor_budget.max_token_budget,
        predecessor_budget.max_provider_calls,
        predecessor_budget.consumed_wall_time_units,
        predecessor_budget.consumed_token_budget,
        predecessor_budget.consumed_provider_calls,
        predecessor_budget.consumed_cell_count,
        predecessor_budget.consumed_revise_count,
        predecessor_budget.current_parallelism,
        predecessor_budget.remaining_wall_time_units,
        predecessor_budget.remaining_token_budget,
        predecessor_budget.remaining_provider_calls,
        predecessor_budget.remaining_cell_count,
        predecessor_budget.remaining_revise_count,
        predecessor_budget.remaining_parallel_slots,
    ]
    if budget_event_kind == "CELL_CREATE":
        values[11] += 1
        values[17] -= 1
    elif budget_event_kind == "START_NODE":
        values[8] += 1
        values[14] -= 1
        if budget_scope == "ROOT_GLOBAL_AND_CELL":
            values[13] += 1
            values[19] -= 1
    elif budget_event_kind == "FINISH_NODE":
        if budget_scope == "ROOT_GLOBAL_AND_CELL":
            values[13] -= 1
            values[19] += 1
    elif budget_event_kind == "REVISE":
        values[8] += 1
        values[12] += 1
        values[14] -= 1
        values[18] -= 1
    if any(item < 0 for item in values):
        raise ValueError("g2d_budget_overflow")
    return tuple(values)


def build_fractal_runtime_budget_v02(
    *,
    policy: FractalRuntimePolicyV02,
    topology_seed: RuntimeTopologySeedV02,
    allocation_parent_budget: FractalRuntimeBudgetV02 | None,
    predecessor_budget: FractalRuntimeBudgetV02 | None,
    owning_cell_id: str,
    budget_scope: str,
    budget_state: str,
    budget_event_kind: str,
    budget_context_input: FractalCellInputV02 | None,
    canonical_child_index: int | None,
    allocation_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    transition_decision: TransitionDecisionV01 | None,
    paired_cell_budget: FractalRuntimeBudgetV02 | None,
    child_result: FractalCellResultV02 | None,
) -> FractalRuntimeBudgetV02:
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    _require_valid(topology_seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    if not _ref_valid(owning_cell_id) or budget_scope not in BUDGET_SCOPES or budget_state not in BUDGET_STATES or budget_event_kind not in BUDGET_EVENT_KINDS:
        raise ValueError("g2d_budget_event_context_invalid")
    if type(allocation_queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in allocation_queue_entries):
        raise ValueError("g2d_budget_event_context_invalid")
    root_axis = budget_scope == "ROOT_GLOBAL_AND_CELL"
    if root_axis and allocation_parent_budget is not None:
        raise ValueError("g2d_budget_predecessor_invalid")
    if not root_axis and allocation_parent_budget is None:
        raise ValueError("g2d_budget_predecessor_invalid")
    if root_axis and owning_cell_id != topology_seed.root_cell_id:
        raise ValueError("g2d_budget_event_context_invalid")
    if predecessor_budget is not None:
        _require_valid(predecessor_budget, FractalRuntimeBudgetV02, "g2d_budget_predecessor_invalid")
        if predecessor_budget.budget_state == "FINAL" or predecessor_budget.owning_cell_id != owning_cell_id or predecessor_budget.budget_scope != budget_scope:
            raise ValueError("g2d_budget_predecessor_invalid")
    if allocation_parent_budget is not None:
        _require_valid(allocation_parent_budget, FractalRuntimeBudgetV02, "g2d_budget_predecessor_invalid")
        if allocation_parent_budget.budget_state != "ACTIVE" or allocation_parent_budget.budget_event_kind != "CELL_CREATE":
            raise ValueError("g2d_budget_predecessor_invalid")
        if budget_context_input is None:
            raise ValueError("g2d_budget_event_context_invalid")
        if budget_event_kind in {"INITIAL_ALLOCATION", "ACTIVATE", "CELL_CREATE"} and allocation_parent_budget.budget_id != budget_context_input.cell_budget_id:
            raise ValueError("g2d_budget_event_context_invalid")
    if budget_event_kind == "INITIAL_ALLOCATION":
        if predecessor_budget is not None or transition_decision is not None or paired_cell_budget is not None or child_result is not None:
            raise ValueError("g2d_budget_event_context_invalid")
        if root_axis and (budget_context_input is not None or canonical_child_index is not None or allocation_queue_entries):
            raise ValueError("g2d_budget_event_context_invalid")
        if not root_axis:
            if budget_state != "ALLOCATED" or budget_context_input is None or canonical_child_index is None:
                raise ValueError("g2d_budget_event_context_invalid")
            if owning_cell_id not in budget_context_input.ordered_planned_child_cell_ids:
                raise ValueError("g2d_child_lineage_mismatch")
            if tuple(item.queue_entry_id for item in allocation_queue_entries) != budget_context_input.ordered_initial_queue_entry_ids:
                raise ValueError("g2d_budget_event_context_invalid")
        elif budget_state != "ALLOCATED":
            raise ValueError("g2d_budget_state_transition_invalid")
    elif predecessor_budget is None:
        raise ValueError("g2d_budget_predecessor_invalid")
    if budget_event_kind == "ACTIVATE":
        if budget_state != "ACTIVE" or predecessor_budget.budget_state != "ALLOCATED" or predecessor_budget.budget_event_kind != "INITIAL_ALLOCATION":
            raise ValueError("g2d_budget_state_transition_invalid")
    if budget_event_kind == "CELL_CREATE":
        if budget_state != "ACTIVE" or predecessor_budget.budget_state != "ACTIVE" or predecessor_budget.budget_event_kind != "ACTIVATE":
            raise ValueError("g2d_budget_state_transition_invalid")
    if budget_event_kind in {"ACTIVATE", "CELL_CREATE"}:
        child_event = not root_axis or paired_cell_budget is not None
        if child_event:
            if budget_context_input is None or canonical_child_index is None or not allocation_queue_entries:
                raise ValueError("g2d_budget_event_context_invalid")
            if not root_axis and owning_cell_id not in budget_context_input.ordered_planned_child_cell_ids:
                raise ValueError("g2d_child_lineage_mismatch")
        elif budget_context_input is not None or canonical_child_index is not None or allocation_queue_entries:
            raise ValueError("g2d_budget_event_context_invalid")
    if budget_event_kind in {"START_NODE", "FINISH_NODE", "REVISE", "FINALIZE"}:
        if transition_decision is None or canonical_child_index is not None or allocation_queue_entries or child_result is not None:
            raise ValueError("g2d_budget_event_context_invalid")
        if budget_context_input is None:
            raise ValueError("g2d_budget_event_context_invalid")
        if budget_event_kind != "FINALIZE" and budget_state != "ACTIVE":
            raise ValueError("g2d_budget_state_transition_invalid")
        if budget_event_kind == "FINALIZE":
            expected_state = "FINAL" if not root_axis or paired_cell_budget is None else "ACTIVE"
            if budget_state != expected_state:
                raise ValueError("g2d_budget_state_transition_invalid")
        event_ref = transition_decision.decision_id
    elif budget_event_kind == "CHILD_AGGREGATE":
        if child_result is None or paired_cell_budget is None or canonical_child_index is None or budget_context_input is None or allocation_queue_entries or transition_decision is not None or not root_axis or budget_state != "ACTIVE":
            raise ValueError("g2d_budget_event_context_invalid")
        event_ref = child_result.result_id
    else:
        event_ref = paired_cell_budget.owning_cell_id if root_axis and paired_cell_budget is not None else owning_cell_id
    counters = _budget_counter_values(
        policy=policy,
        allocation_parent_budget=allocation_parent_budget,
        predecessor_budget=predecessor_budget,
        budget_scope=budget_scope,
        budget_event_kind=budget_event_kind,
        budget_context_input=budget_context_input,
        canonical_child_index=canonical_child_index,
        paired_cell_budget=paired_cell_budget,
    )
    provisional = FractalRuntimeBudgetV02(
        budget_id="frbudget_v02:" + _ZERO_SHA256,
        policy_id=policy.policy_id,
        topology_seed_id=topology_seed.topology_seed_id,
        allocation_parent_budget_id=None if allocation_parent_budget is None else allocation_parent_budget.budget_id,
        predecessor_budget_id=None if predecessor_budget is None else predecessor_budget.budget_id,
        owning_cell_id=owning_cell_id,
        budget_scope=budget_scope,
        budget_state=budget_state,
        budget_event_kind=budget_event_kind,
        budget_event_ref=event_ref,
        max_depth=counters[0], max_fan_out=counters[1], max_total_cells=counters[2], max_parallelism=counters[3],
        max_revise_count=counters[4], max_wall_time_units=counters[5], max_token_budget=counters[6], max_provider_calls=counters[7],
        consumed_wall_time_units=counters[8], consumed_token_budget=counters[9], consumed_provider_calls=counters[10], consumed_cell_count=counters[11],
        consumed_revise_count=counters[12], current_parallelism=counters[13], remaining_wall_time_units=counters[14], remaining_token_budget=counters[15],
        remaining_provider_calls=counters[16], remaining_cell_count=counters[17], remaining_revise_count=counters[18], remaining_parallel_slots=counters[19],
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_fractal_runtime_budget_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalRuntimeBudgetV02)


def fractal_runtime_budget_to_plain_data_v02(value: FractalRuntimeBudgetV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalRuntimeBudgetV02)


def rebuild_fractal_runtime_budget_identity_v02(value: FractalRuntimeBudgetV02) -> str:
    return _rebuild_serialized(value, FractalRuntimeBudgetV02)


def build_runtime_topology_source_binding_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
) -> RuntimeTopologySourceBindingV02:
    if type(source_context) is not FractalRuntimeSourceContextV02:
        raise ValueError("g2d_source_context_invalid")
    proposal = source_context.proposal
    decision = source_context.decision
    snapshot = source_context.router_input.local_routing_snapshot
    route = source_context.route_eligibility_artifact
    values = (
        proposal.selected_local_mode_profile_id,
        proposal.selected_safe_depth_rank,
        proposal.selected_expected_cost_units,
        decision.accepted_mode,
        decision.accepted_scope_ref,
    )
    if values[0] is None or values[1] is None or values[2] is None or values[3] not in TOPOLOGY_ELIGIBLE_MODES or values[4] is None:
        raise ValueError("g2d_route_class_not_topology_eligible")
    route_plain = _kernel_artifact_to_plain_dict_v01(route)
    provisional = RuntimeTopologySourceBindingV02(
        source_binding_id="frsource_v02:" + _ZERO_SHA256,
        request_id=decision.request_id,
        transaction_id=decision.transaction_id,
        owning_root_id=decision.owning_root_id,
        domain_id=decision.domain_id,
        accepted_mode=decision.accepted_mode,
        accepted_scope_ref=decision.accepted_scope_ref,
        route_eligibility_artifact_id=route.artifact_id,
        route_eligibility_artifact_sha256=_plain_sha256(route_plain),
        source_decision_artifact_id=source_context.decision_artifact.artifact_id,
        source_proposal_artifact_id=source_context.proposal_artifact.artifact_id,
        selected_local_mode_profile_id=proposal.selected_local_mode_profile_id,
        selected_feasibility_row_id=proposal.selected_feasibility_row_id,
        selected_safe_depth_rank=proposal.selected_safe_depth_rank,
        selected_expected_cost_units=proposal.selected_expected_cost_units,
        required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        source_mode_profile_set_id=snapshot.mode_profile_set_id,
        source_policy_snapshot_id=snapshot.policy_snapshot_id,
        source_capability_snapshot_id=snapshot.capability_snapshot_id,
        permitted_narrower_scope_refs=snapshot.permitted_narrower_scope_refs,
        source_root_decision_result_id=source_context.root_decision_result.decision_id,
        source_root_transition_decision_id=decision.source_root_transition_decision_id,
        proposal_transition_decision_id=source_context.proposal_transition_decision.decision_id,
        post_root_transition_decision_id=source_context.root_route_transition_decision.decision_id,
        transition_registry_id=source_context.transition_registry.registry_id,
        g2c_abi_profile_id="execution_mode_router_g2c_abi_profile_v01",
        downstream_action_packet_required=decision.downstream_action_packet_required,
        runtime_policy_id=source_context.runtime_policy.policy_id,
        source_time_envelope_ref=snapshot.time_envelope_ref,
        source_trace_refs=route.trace_refs,
        source_parent_refs=route.parent_refs,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    report = validate_runtime_topology_source_binding_v02(result)
    if report.status != "PASS":
        raise ValueError(report.reason_codes[0])
    return result


def validate_runtime_topology_source_binding_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeTopologySourceBindingV02)


def runtime_topology_source_binding_to_plain_data_v02(value: RuntimeTopologySourceBindingV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeTopologySourceBindingV02)


def rebuild_runtime_topology_source_binding_identity_v02(value: RuntimeTopologySourceBindingV02) -> str:
    return _rebuild_serialized(value, RuntimeTopologySourceBindingV02)


def _source_policy_bindings_match(
    source_binding: RuntimeTopologySourceBindingV02,
    policy: FractalRuntimePolicyV02,
) -> bool:
    expected_capabilities = source_binding.required_downstream_capability_ids + tuple(
        capability
        for capability in LOCAL_CAPS
        if capability not in source_binding.required_downstream_capability_ids
    )
    return (
        source_binding.runtime_policy_id == policy.policy_id
        and source_binding.accepted_mode in policy.allowed_modes
        and source_binding.permitted_narrower_scope_refs == policy.permitted_child_scope_refs
        and policy.allowed_capability_ids == expected_capabilities
    )


def _seed_source_policy_bindings_match(
    seed: RuntimeTopologySeedV02,
    source_binding: RuntimeTopologySourceBindingV02,
    policy: FractalRuntimePolicyV02,
) -> bool:
    return _source_policy_bindings_match(source_binding, policy) and (
        seed.request_id == source_binding.request_id
        and seed.transaction_id == source_binding.transaction_id
        and seed.owning_root_id == source_binding.owning_root_id
        and seed.domain_id == source_binding.domain_id
        and seed.accepted_mode == source_binding.accepted_mode
        and seed.accepted_scope_ref == source_binding.accepted_scope_ref
        and seed.source_binding_id == source_binding.source_binding_id
        and seed.runtime_policy_id == policy.policy_id
        and seed.source_time_envelope_ref == source_binding.source_time_envelope_ref
        and seed.root_cell_id
        == derive_fractal_root_cell_id_v02(
            source_binding_id=source_binding.source_binding_id,
            runtime_policy_id=policy.policy_id,
            accepted_mode=source_binding.accepted_mode,
            accepted_scope_ref=source_binding.accepted_scope_ref,
        )
        and seed.trace_refs
        == source_binding.source_trace_refs
        + (
            source_binding.source_binding_id,
            policy.policy_id,
            seed.root_cell_id,
            source_binding.source_time_envelope_ref,
        )
        and seed.parent_refs
        == (
            source_binding.route_eligibility_artifact_id,
            source_binding.source_decision_artifact_id,
            source_binding.source_proposal_artifact_id,
            source_binding.source_binding_id,
        )
    )


def build_runtime_topology_seed_v02(
    source_binding: RuntimeTopologySourceBindingV02,
    policy: FractalRuntimePolicyV02,
    *,
    root_cell_id: str,
) -> RuntimeTopologySeedV02:
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    if not _source_policy_bindings_match(source_binding, policy):
        raise ValueError("g2d_source_profile_binding_mismatch")
    expected_root_cell_id = derive_fractal_root_cell_id_v02(
        source_binding_id=source_binding.source_binding_id,
        runtime_policy_id=policy.policy_id,
        accepted_mode=source_binding.accepted_mode,
        accepted_scope_ref=source_binding.accepted_scope_ref,
    )
    if root_cell_id != expected_root_cell_id:
        raise ValueError("g2d_root_cell_identity_invalid")
    trace_refs = source_binding.source_trace_refs + (
        source_binding.source_binding_id,
        policy.policy_id,
        root_cell_id,
        source_binding.source_time_envelope_ref,
    )
    parent_refs = (
        source_binding.route_eligibility_artifact_id,
        source_binding.source_decision_artifact_id,
        source_binding.source_proposal_artifact_id,
        source_binding.source_binding_id,
    )
    provisional = RuntimeTopologySeedV02(
        topology_seed_id="frseed_v02:" + _ZERO_SHA256,
        seed_version="v0.2",
        profile_id=PROFILE_IDS[0],
        request_id=source_binding.request_id,
        transaction_id=source_binding.transaction_id,
        owning_root_id=source_binding.owning_root_id,
        domain_id=source_binding.domain_id,
        accepted_mode=source_binding.accepted_mode,
        accepted_scope_ref=source_binding.accepted_scope_ref,
        source_binding_id=source_binding.source_binding_id,
        runtime_policy_id=policy.policy_id,
        root_cell_id=root_cell_id,
        source_time_envelope_ref=source_binding.source_time_envelope_ref,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    if not _seed_source_policy_bindings_match(result, source_binding, policy):
        raise ValueError("g2d_topology_lineage_mismatch")
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_runtime_topology_seed_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeTopologySeedV02)


def runtime_topology_seed_to_plain_data_v02(value: RuntimeTopologySeedV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeTopologySeedV02)


def rebuild_runtime_topology_seed_identity_v02(value: RuntimeTopologySeedV02) -> str:
    return _rebuild_serialized(value, RuntimeTopologySeedV02)


def build_runtime_topology_node_v02(
    seed: RuntimeTopologySeedV02,
    source_binding: RuntimeTopologySourceBindingV02,
    policy: FractalRuntimePolicyV02,
    *,
    canonical_index: int,
    node_kind: str,
    depth: int,
    scope_ref: str,
    cell_binding_class: str,
    scope_binding_class: str,
    budget_binding_class: str,
    required_capability_ids: tuple[str, ...],
    input_ref_derivation_class: str,
) -> RuntimeTopologyNodeV02:
    _require_valid(seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    if not _seed_source_policy_bindings_match(seed, source_binding, policy):
        raise ValueError("g2d_topology_lineage_mismatch")
    required_caps = _require_text_tuple(required_capability_ids)
    if type(canonical_index) is not int or canonical_index < 0 or type(depth) is not int or depth < 0 or node_kind not in NODE_KINDS or input_ref_derivation_class not in INPUT_REF_DERIVATION_CLASSES:
        raise ValueError("g2d_topology_node_invalid")
    if cell_binding_class not in CELL_BINDING_CLASSES or scope_binding_class not in SCOPE_BINDING_CLASSES or budget_binding_class not in BUDGET_BINDING_CLASSES or not set(required_caps).issubset(policy.allowed_capability_ids):
        raise ValueError("g2d_topology_node_invalid")
    mode_rows = dict(MODE_NODE_TEMPLATE_ROWS_V02)[seed.accepted_mode]
    if canonical_index >= len(mode_rows):
        raise ValueError("g2d_mode_template_matrix_invalid")
    row = mode_rows[canonical_index]
    row_required_caps = source_binding.required_downstream_capability_ids if row[5] == ("SRC_CAPS",) else row[5]
    expected_inputs = (
        row[1], row[2], row[3], row[4], row_required_caps, row[8],
    )
    supplied_inputs = (
        node_kind, cell_binding_class, scope_binding_class, budget_binding_class,
        required_caps, input_ref_derivation_class,
    )
    if supplied_inputs != expected_inputs or depth != 0 or scope_ref != seed.accepted_scope_ref:
        raise ValueError("g2d_mode_template_matrix_invalid")
    input_refs = (source_binding.source_binding_id, policy.policy_id, source_binding.source_time_envelope_ref) if input_ref_derivation_class == "SOURCE_CONTEXT" else ()
    provisional = RuntimeTopologyNodeV02(
        node_id="frnode_v02:" + _ZERO_SHA256,
        topology_seed_id=seed.topology_seed_id,
        accepted_mode=seed.accepted_mode,
        node_kind=node_kind,
        canonical_index=canonical_index,
        depth=depth,
        scope_ref=scope_ref,
        cell_binding_class=cell_binding_class,
        scope_binding_class=scope_binding_class,
        budget_binding_class=budget_binding_class,
        required_capability_ids=required_caps,
        allowed_capability_ids=policy.allowed_capability_ids,
        forbidden_claims=policy.forbidden_claims,
        input_ref_derivation_class=input_ref_derivation_class,
        input_refs=input_refs,
        trace_refs=(seed.topology_seed_id, source_binding.source_binding_id, str(canonical_index), node_kind),
        expected_output_kind=NODE_OUTPUT_KIND_BY_NODE_KIND_V02[node_kind],
        required=True,
        recursive_expansion_allowed=seed.accepted_mode == "full_fractal" and node_kind == "FRACTAL_CELL",
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_runtime_topology_node_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeTopologyNodeV02)


def runtime_topology_node_to_plain_data_v02(value: RuntimeTopologyNodeV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeTopologyNodeV02)


def rebuild_runtime_topology_node_identity_v02(value: RuntimeTopologyNodeV02) -> str:
    return _rebuild_serialized(value, RuntimeTopologyNodeV02)


def build_runtime_topology_edge_v02(
    seed: RuntimeTopologySeedV02,
    source_node: RuntimeTopologyNodeV02,
    target_node: RuntimeTopologyNodeV02,
    *,
    edge_kind: str,
    canonical_index: int,
    cell_projection_class: str,
) -> RuntimeTopologyEdgeV02:
    _require_valid(seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    _require_valid(source_node, RuntimeTopologyNodeV02, "g2d_topology_node_invalid")
    _require_valid(target_node, RuntimeTopologyNodeV02, "g2d_topology_node_invalid")
    if edge_kind not in EDGE_KINDS or cell_projection_class not in CELL_PROJECTION_CLASSES or type(canonical_index) is not int or canonical_index < 0 or source_node.topology_seed_id != seed.topology_seed_id or target_node.topology_seed_id != seed.topology_seed_id or source_node.node_id == target_node.node_id:
        raise ValueError("g2d_topology_edge_invalid")
    mode_rows = dict(MODE_EDGE_TEMPLATE_ROWS_V02)[seed.accepted_mode]
    if canonical_index >= len(mode_rows):
        raise ValueError("g2d_mode_template_matrix_invalid")
    row = mode_rows[canonical_index]
    if (source_node.canonical_index, target_node.canonical_index, edge_kind, cell_projection_class) != (row[2], row[3], row[4], row[1]):
        raise ValueError("g2d_mode_template_matrix_invalid")
    provisional = RuntimeTopologyEdgeV02(
        edge_id="fredge_v02:" + _ZERO_SHA256,
        topology_seed_id=seed.topology_seed_id,
        source_node_id=source_node.node_id,
        target_node_id=target_node.node_id,
        edge_kind=edge_kind,
        canonical_index=canonical_index,
        cell_projection_class=cell_projection_class,
        required=True,
        evidence_flow_allowed=True,
        authority_flow_allowed=False,
        trace_refs=(seed.topology_seed_id, source_node.node_id, target_node.node_id, str(canonical_index), cell_projection_class),
        root_review_required=True,
    )
    return _finish_identity(provisional)


def validate_runtime_topology_edge_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeTopologyEdgeV02)


def runtime_topology_edge_to_plain_data_v02(value: RuntimeTopologyEdgeV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeTopologyEdgeV02)


def rebuild_runtime_topology_edge_identity_v02(value: RuntimeTopologyEdgeV02) -> str:
    return _rebuild_serialized(value, RuntimeTopologyEdgeV02)


def build_runtime_assignment_v02(
    seed: RuntimeTopologySeedV02,
    node: RuntimeTopologyNodeV02,
    *,
    assignment_kind: str,
    executor_component_id: str,
    capability_ids: tuple[str, ...],
    cell_binding_class: str,
    scope_binding_class: str,
    budget_binding_class: str,
) -> RuntimeAssignmentV02:
    _require_valid(seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    _require_valid(node, RuntimeTopologyNodeV02, "g2d_topology_node_invalid")
    caps = _require_text_tuple(capability_ids)
    if assignment_kind not in ASSIGNMENT_KINDS or executor_component_id not in EXECUTOR_COMPONENT_IDS or cell_binding_class not in CELL_BINDING_CLASSES or scope_binding_class not in SCOPE_BINDING_CLASSES or budget_binding_class not in BUDGET_BINDING_CLASSES or node.topology_seed_id != seed.topology_seed_id:
        raise ValueError("g2d_topology_assignment_invalid")
    mode_rows = dict(MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[seed.accepted_mode]
    if node.canonical_index >= len(mode_rows):
        raise ValueError("g2d_mode_template_matrix_invalid")
    row = mode_rows[node.canonical_index]
    row_caps = node.required_capability_ids if row[4] == ("SRC_CAPS",) else row[4]
    expected = (row[2], row[3], row_caps, row[5], row[6], row[7])
    supplied = (assignment_kind, executor_component_id, caps, cell_binding_class, scope_binding_class, budget_binding_class)
    if row[1] != node.canonical_index or supplied != expected:
        raise ValueError("g2d_mode_template_matrix_invalid")
    provisional = RuntimeAssignmentV02(
        assignment_id="frassign_v02:" + _ZERO_SHA256,
        topology_seed_id=seed.topology_seed_id,
        node_id=node.node_id,
        canonical_index=node.canonical_index,
        assignment_kind=assignment_kind,
        executor_component_id=executor_component_id,
        capability_ids=caps,
        cell_binding_class=cell_binding_class,
        scope_binding_class=scope_binding_class,
        budget_binding_class=budget_binding_class,
        provider_call_allowed=False,
        network_call_allowed=False,
        connector_call_allowed=False,
        trace_refs=(seed.topology_seed_id, node.node_id, str(node.canonical_index), executor_component_id),
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        effect_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_runtime_assignment_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeAssignmentV02)


def runtime_assignment_to_plain_data_v02(value: RuntimeAssignmentV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeAssignmentV02)


def rebuild_runtime_assignment_identity_v02(value: RuntimeAssignmentV02) -> str:
    return _rebuild_serialized(value, RuntimeAssignmentV02)


def build_runtime_execution_topology_v02(
    source_binding: RuntimeTopologySourceBindingV02,
    seed: RuntimeTopologySeedV02,
    policy: FractalRuntimePolicyV02,
    *,
    nodes: tuple[RuntimeTopologyNodeV02, ...],
    edges: tuple[RuntimeTopologyEdgeV02, ...],
    assignments: tuple[RuntimeAssignmentV02, ...],
    root_cell_id: str,
    global_budget: FractalRuntimeBudgetV02,
    time_envelope_ref: str,
) -> RuntimeExecutionTopologyV02:
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    _require_valid(seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    if not _seed_source_policy_bindings_match(seed, source_binding, policy):
        raise ValueError("g2d_topology_lineage_mismatch")
    if root_cell_id != seed.root_cell_id:
        raise ValueError("g2d_root_cell_identity_invalid")
    if time_envelope_ref != seed.source_time_envelope_ref or time_envelope_ref != source_binding.source_time_envelope_ref:
        raise ValueError("g2d_topology_time_mismatch")
    if (
        global_budget.policy_id != policy.policy_id
        or global_budget.topology_seed_id != seed.topology_seed_id
        or global_budget.owning_cell_id != seed.root_cell_id
        or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
        or global_budget.budget_state != "ALLOCATED"
        or global_budget.budget_event_kind != "INITIAL_ALLOCATION"
        or global_budget.allocation_parent_budget_id is not None
        or global_budget.predecessor_budget_id is not None
        or global_budget.budget_event_ref != seed.root_cell_id
    ):
        raise ValueError("g2d_global_budget_binding_missing")
    if type(nodes) is not tuple or not nodes or any(type(item) is not RuntimeTopologyNodeV02 for item in nodes):
        raise ValueError("g2d_topology_node_invalid")
    if type(edges) is not tuple or any(type(item) is not RuntimeTopologyEdgeV02 for item in edges):
        raise ValueError("g2d_topology_edge_invalid")
    if type(assignments) is not tuple or len(assignments) != len(nodes) or any(type(item) is not RuntimeAssignmentV02 for item in assignments):
        raise ValueError("g2d_topology_assignment_invalid")
    node_rows = dict(MODE_NODE_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    edge_rows = dict(MODE_EDGE_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    assignment_rows = dict(MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    if len(nodes) != len(node_rows) or len(edges) != len(edge_rows) or len(assignments) != len(assignment_rows):
        raise ValueError("g2d_mode_template_matrix_invalid")
    if tuple(item.canonical_index for item in nodes) != tuple(range(len(node_rows))):
        raise ValueError("g2d_topology_order_invalid")
    if tuple(item.canonical_index for item in edges) != tuple(range(len(edge_rows))):
        raise ValueError("g2d_topology_order_invalid")
    if tuple(item.canonical_index for item in assignments) != tuple(range(len(assignment_rows))):
        raise ValueError("g2d_topology_order_invalid")
    if any(item.topology_seed_id != seed.topology_seed_id for item in nodes + edges + assignments):
        raise ValueError("g2d_topology_lineage_mismatch")
    if tuple(item.node_id for item in assignments) != tuple(item.node_id for item in nodes):
        raise ValueError("g2d_topology_assignment_invalid")
    for node, row in zip(nodes, node_rows, strict=True):
        expected_required = source_binding.required_downstream_capability_ids if row[5] == ("SRC_CAPS",) else row[5]
        expected_inputs = (
            source_binding.source_binding_id,
            policy.policy_id,
            source_binding.source_time_envelope_ref,
        ) if row[8] == "SOURCE_CONTEXT" else ()
        if (
            node.accepted_mode != seed.accepted_mode
            or node.scope_ref != seed.accepted_scope_ref
            or node.required_capability_ids != expected_required
            or node.allowed_capability_ids != policy.allowed_capability_ids
            or node.forbidden_claims != policy.forbidden_claims
            or node.input_refs != expected_inputs
            or node.trace_refs
            != (
                seed.topology_seed_id,
                source_binding.source_binding_id,
                str(node.canonical_index),
                node.node_kind,
            )
        ):
            raise ValueError("g2d_topology_lineage_mismatch")
    for edge, row in zip(edges, edge_rows, strict=True):
        if (
            edge.source_node_id != nodes[row[2]].node_id
            or edge.target_node_id != nodes[row[3]].node_id
            or (edge.edge_kind, edge.cell_projection_class) != (row[4], row[1])
        ):
            raise ValueError("g2d_topology_edge_invalid")
    for assignment, node, row in zip(assignments, nodes, assignment_rows, strict=True):
        expected_capabilities = node.required_capability_ids if row[4] == ("SRC_CAPS",) else row[4]
        if (
            assignment.node_id != node.node_id
            or assignment.capability_ids != expected_capabilities
            or (
                assignment.assignment_kind,
                assignment.executor_component_id,
                assignment.cell_binding_class,
                assignment.scope_binding_class,
                assignment.budget_binding_class,
            )
            != (row[2], row[3], row[5], row[6], row[7])
        ):
            raise ValueError("g2d_topology_assignment_invalid")
    ordered_node_ids = tuple(item.node_id for item in nodes)
    ordered_edge_ids = tuple(item.edge_id for item in edges)
    ordered_assignment_ids = tuple(item.assignment_id for item in assignments)
    trace_refs = (
        source_binding.source_binding_id,
        root_cell_id,
        seed.topology_seed_id,
        global_budget.budget_id,
        *ordered_node_ids,
        *ordered_edge_ids,
        *ordered_assignment_ids,
    )
    parent_refs = seed.parent_refs + (seed.topology_seed_id, global_budget.budget_id)
    provisional = RuntimeExecutionTopologyV02(
        topology_id="frtopology_v02:" + _ZERO_SHA256,
        topology_version="v0.2",
        topology_seed_id=seed.topology_seed_id,
        request_id=source_binding.request_id,
        transaction_id=source_binding.transaction_id,
        owning_root_id=source_binding.owning_root_id,
        domain_id=source_binding.domain_id,
        accepted_mode=source_binding.accepted_mode,
        accepted_scope_ref=source_binding.accepted_scope_ref,
        source_binding_id=source_binding.source_binding_id,
        source_route_eligibility_artifact_id=source_binding.route_eligibility_artifact_id,
        source_root_decision_artifact_id=source_binding.source_decision_artifact_id,
        source_proposal_artifact_id=source_binding.source_proposal_artifact_id,
        runtime_policy_id=policy.policy_id,
        ordered_node_ids=ordered_node_ids,
        ordered_edge_ids=ordered_edge_ids,
        ordered_assignment_ids=ordered_assignment_ids,
        root_cell_id=root_cell_id,
        global_budget_id=global_budget.budget_id,
        time_envelope_ref=time_envelope_ref,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        provider_calls=0,
        network_calls=0,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_runtime_execution_topology_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, RuntimeExecutionTopologyV02)


def runtime_execution_topology_to_plain_data_v02(value: RuntimeExecutionTopologyV02) -> dict[str, object]:
    return _serialize_serialized(value, RuntimeExecutionTopologyV02)


def rebuild_runtime_execution_topology_identity_v02(value: RuntimeExecutionTopologyV02) -> str:
    return _rebuild_serialized(value, RuntimeExecutionTopologyV02)


def build_parent_child_scope_projection_v02(
    topology: RuntimeExecutionTopologyV02,
    source_binding: RuntimeTopologySourceBindingV02,
    *,
    parent_cell_id: str,
    child_cell_id: str,
    parent_scope_ref: str,
    child_scope_ref: str,
    parent_allowed_capability_ids: tuple[str, ...],
    child_allowed_capability_ids: tuple[str, ...],
    parent_forbidden_claims: tuple[str, ...],
    child_forbidden_claims: tuple[str, ...],
    parent_ttl_units: int,
    child_ttl_units: int,
    parent_budget: FractalRuntimeBudgetV02,
    child_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    child_depth: int,
) -> ParentChildScopeProjectionV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    _require_valid(parent_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_valid(child_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    parent_caps = _require_text_tuple(parent_allowed_capability_ids)
    child_caps = _require_text_tuple(child_allowed_capability_ids)
    parent_forbidden = _require_text_tuple(parent_forbidden_claims)
    child_forbidden = _require_text_tuple(child_forbidden_claims)
    if type(parent_ttl_units) is not int or type(child_ttl_units) is not int or type(child_depth) is not int or min(parent_ttl_units, child_ttl_units, child_depth) < 0:
        raise ValueError("g2d_child_lineage_mismatch")
    if parent_scope_ref == child_scope_ref:
        relation = "EQUAL"
    elif child_scope_ref in source_binding.permitted_narrower_scope_refs:
        relation = "NARROWER"
    else:
        raise ValueError("g2d_scope_relation_unproven")
    parent_lineage = (
        topology.topology_id,
        topology.topology_seed_id,
        parent_cell_id,
        parent_budget.budget_id,
        global_budget.budget_id,
        parent_scope_ref,
    )
    child_lineage = parent_lineage + (
        child_cell_id,
        child_budget.budget_id,
        child_scope_ref,
        str(child_depth),
    )
    proof_refs = (
        source_binding.source_binding_id,
        source_binding.route_eligibility_artifact_id,
        source_binding.runtime_policy_id,
        source_binding.source_policy_snapshot_id,
        source_binding.source_capability_snapshot_id,
    )
    provisional = ParentChildScopeProjectionV02(
        projection_id="frscope_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        parent_cell_id=parent_cell_id,
        child_cell_id=child_cell_id,
        parent_scope_ref=parent_scope_ref,
        child_scope_ref=child_scope_ref,
        scope_relation=relation,
        budget_relation="CHILD_BUDGET",
        parent_allowed_capability_ids=parent_caps,
        child_allowed_capability_ids=child_caps,
        parent_forbidden_claims=parent_forbidden,
        child_forbidden_claims=child_forbidden,
        parent_ttl_units=parent_ttl_units,
        child_ttl_units=child_ttl_units,
        parent_budget_id=parent_budget.budget_id,
        child_budget_id=child_budget.budget_id,
        global_budget_id=global_budget.budget_id,
        child_depth=child_depth,
        parent_lineage_refs=parent_lineage,
        child_lineage_refs=child_lineage,
        proof_refs=proof_refs,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_parent_child_scope_projection_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, ParentChildScopeProjectionV02)


def parent_child_scope_projection_to_plain_data_v02(value: ParentChildScopeProjectionV02) -> dict[str, object]:
    return _serialize_serialized(value, ParentChildScopeProjectionV02)


def rebuild_parent_child_scope_projection_identity_v02(value: ParentChildScopeProjectionV02) -> str:
    return _rebuild_serialized(value, ParentChildScopeProjectionV02)


def build_fractal_cell_input_v02(
    topology: RuntimeExecutionTopologyV02,
    *,
    cell_id: str,
    parent_cell_id: str | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    scope_ref: str,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    initial_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    required_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    cell_depth: int,
    requested_child_count: int,
    ordered_planned_child_cell_ids: tuple[str, ...],
    ordered_nodes: tuple[RuntimeTopologyNodeV02, ...],
    evidence_refs: tuple[str, ...],
    context_refs: tuple[str, ...],
    time_envelope_ref: str,
) -> FractalCellInputV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(cell_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    if type(initial_queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in initial_queue_entries):
        raise ValueError("g2d_cell_input_build_order_invalid")
    if type(required_queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in required_queue_entries):
        raise ValueError("g2d_cell_input_build_order_invalid")
    if type(ordered_nodes) is not tuple or any(type(item) is not RuntimeTopologyNodeV02 for item in ordered_nodes):
        raise ValueError("g2d_node_instance_geometry_invalid")
    planned = _require_text_tuple(ordered_planned_child_cell_ids)
    evidence = _require_text_tuple(evidence_refs)
    context = _require_text_tuple(context_refs)
    if type(cell_depth) is not int or type(requested_child_count) is not int or cell_depth < 0 or requested_child_count < 0 or requested_child_count != len(planned):
        raise ValueError("g2d_node_instance_geometry_invalid")
    if parent_cell_id is None:
        if scope_projection is not None or cell_id != topology.root_cell_id:
            raise ValueError("g2d_cell_input_invalid")
        projection_id = None
    else:
        if type(scope_projection) is not ParentChildScopeProjectionV02 or scope_projection.child_cell_id != cell_id:
            raise ValueError("g2d_cell_input_invalid")
        projection_id = scope_projection.projection_id
    initial_ids = tuple(item.queue_entry_id for item in initial_queue_entries)
    required_ids = tuple(item.queue_entry_id for item in required_queue_entries)
    node_ids = tuple(item.node_id for item in ordered_nodes)
    required_outputs = tuple(item.expected_output_kind for item in ordered_nodes if item.required)
    trace_refs = (
        topology.topology_id,
        cell_id,
        *((projection_id,) if projection_id is not None else ()),
        cell_budget.budget_id,
        global_budget.budget_id,
        *node_ids,
        *initial_ids,
        *required_ids,
    )
    provisional = FractalCellInputV02(
        cell_input_id="frcellin_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        request_id=topology.request_id,
        transaction_id=topology.transaction_id,
        owning_root_id=topology.owning_root_id,
        domain_id=topology.domain_id,
        accepted_mode=topology.accepted_mode,
        scope_projection_id=projection_id,
        scope_ref=scope_ref,
        cell_budget_id=cell_budget.budget_id,
        global_budget_id=global_budget.budget_id,
        ordered_initial_queue_entry_ids=initial_ids,
        ordered_required_queue_entry_ids=required_ids,
        cell_depth=cell_depth,
        requested_child_count=requested_child_count,
        ordered_planned_child_cell_ids=planned,
        ordered_node_ids=node_ids,
        evidence_refs=evidence,
        context_refs=context,
        required_output_kinds=required_outputs,
        forbidden_output_kinds=FORBIDDEN_OUTPUT_KINDS,
        initial_revise_count=0,
        time_envelope_ref=time_envelope_ref,
        trace_refs=trace_refs,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _specific_errors(result)
    if errors:
        raise ValueError(errors[0])
    report = validate_fractal_cell_input_v02(result)
    if report.status != "PASS":
        raise ValueError(report.reason_codes[0])
    return result


def validate_fractal_cell_input_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalCellInputV02)


def fractal_cell_input_to_plain_data_v02(value: FractalCellInputV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalCellInputV02)


def rebuild_fractal_cell_input_identity_v02(value: FractalCellInputV02) -> str:
    return _rebuild_serialized(value, FractalCellInputV02)


_QUEUE_RULE_STATE = {
    "t02": "PENDING", "t03": "PENDING", "t04": "READY", "t05": "RUNNING",
    "t06": "VALIDATING", "t07": "READY", "t08": "COMPLETED", "t09": "DEGRADED",
    "t10": "BLOCKED", "t11": "NEEDS_USER", "t12": "DEADEND",
}
_NODE_PRIORITIES = {
    "MEMORY_CONTEXT": 0, "LOCAL_MODEL_DECLARATION": 0, "CLOUD_MODEL_DECLARATION": 0,
    "SEMANTIC_ACTOR": 0, "FRACTAL_CELL": 0, "SEMANTIC_MERGE": 1, "FRACTAL_MERGE": 1,
    "POST_VV": 2, "GT_ADVISORY": 3, "PARENT_RETURN": 4,
}


def _short_rule_id(decision: TransitionDecisionV01) -> str:
    match = re.search(r"(?:^|_)t(0[2-9]|1[0-2])(?:_|$)", decision.rule_id)
    if match is None:
        raise ValueError("g2d_queue_transition_unknown")
    return "t" + match.group(1)


def build_fractal_cell_queue_entry_v02(
    topology: RuntimeExecutionTopologyV02,
    seed: RuntimeTopologySeedV02,
    cell_input: FractalCellInputV02 | None,
    node: RuntimeTopologyNodeV02,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    *,
    cell_id: str,
    parent_cell_id: str | None,
    planned_child_cell_id: str | None,
    cell_depth: int,
    scope_ref: str,
    predecessor: FractalCellQueueEntryV02 | None,
    transition_decision: TransitionDecisionV01,
    activation_parent_artifact: KernelArtifactV01 | None,
    local_child_result: FractalCellResultV02 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    cell_instantiation_order: tuple[str, ...],
    projected_node_ids: tuple[str, ...],
    round_start_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...],
    observed_output_refs: tuple[str, ...],
    observed_evidence_refs: tuple[str, ...],
    advisory_refs: tuple[str, ...],
) -> FractalCellQueueEntryV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(seed, RuntimeTopologySeedV02, "g2d_topology_seed_invalid")
    _require_valid(node, RuntimeTopologyNodeV02, "g2d_topology_node_invalid")
    _require_valid(cell_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    if type(transition_decision) is not TransitionDecisionV01:
        raise ValueError("g2d_transition_decision_substituted")
    if type(cell_instantiation_order) is not tuple or cell_id not in cell_instantiation_order or type(projected_node_ids) is not tuple or node.node_id not in projected_node_ids:
        raise ValueError("g2d_node_instance_geometry_invalid")
    if type(round_start_queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in round_start_queue_entries):
        raise ValueError("g2d_queue_order_mismatch")
    reasons = _require_text_tuple(queue_reason_codes, public_reasons=True)
    outputs = _require_text_tuple(observed_output_refs)
    evidence = _require_text_tuple(observed_evidence_refs)
    advisories = _require_text_tuple(advisory_refs)
    rule = _short_rule_id(transition_decision)
    state = _QUEUE_RULE_STATE[rule]
    initial = rule == "t02"
    if initial != (predecessor is None):
        raise ValueError("g2d_queue_predecessor_invalid")
    if initial and cell_input is not None:
        raise ValueError("g2d_queue_entry_invalid")
    if not initial and type(cell_input) is not FractalCellInputV02:
        raise ValueError("g2d_cell_input_invalid")
    if initial:
        snapshot_sequence = 0
        admission_round = 0
        prior_state = None
        predecessor_id = None
        predecessor_relation = "INITIAL_NONE"
        node_sequence = len({(item.cell_id, item.node_id) for item in round_start_queue_entries})
    else:
        snapshot_sequence = predecessor.snapshot_sequence + 1
        admission_round = max((item.admission_round for item in round_start_queue_entries), default=predecessor.admission_round) + 1
        prior_state = predecessor.state
        predecessor_id = predecessor.queue_entry_id
        predecessor_relation = "EXACT_IMMEDIATE_PREDECESSOR"
        node_sequence = predecessor.node_instance_sequence
    if state in {"PENDING", "READY", "RUNNING"} and (outputs or evidence or advisories or (state != "PENDING" and reasons)):
        raise ValueError("g2d_queue_entry_invalid")
    if (local_child_result is None) != (local_child_result_artifact is None):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if activation_parent_artifact is not None and not initial:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if initial and parent_cell_id is None and activation_parent_artifact is not None:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if initial and parent_cell_id is not None and activation_parent_artifact is None:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if initial:
        base = (topology.topology_id, seed.topology_seed_id, cell_id)
        if parent_cell_id is not None:
            base += (parent_cell_id,)
        base += (node.node_id, cell_budget.budget_id, global_budget.budget_id)
        if activation_parent_artifact is not None:
            base += (activation_parent_artifact.artifact_id,)
    else:
        base = (topology.topology_id, seed.topology_seed_id, cell_id)
        if parent_cell_id is not None:
            base += (parent_cell_id,)
        base += (node.node_id, cell_budget.budget_id, global_budget.budget_id)
        if parent_cell_id is not None:
            if len(predecessor.lineage_refs) < 8:
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            base += (predecessor.lineage_refs[7],)
        base += (predecessor.queue_entry_id,)
        if local_child_result_artifact is not None:
            base += (local_child_result_artifact.artifact_id,)
    lineage = base + outputs + evidence + advisories
    provisional = FractalCellQueueEntryV02(
        queue_entry_id="frqueue_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        topology_seed_id=seed.topology_seed_id,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        node_id=node.node_id,
        planned_child_cell_id=planned_child_cell_id,
        cell_depth=cell_depth,
        scope_ref=scope_ref,
        cell_budget_id=cell_budget.budget_id,
        global_budget_id=global_budget.budget_id,
        state=state,
        prior_state=prior_state,
        predecessor_queue_entry_id=predecessor_id,
        predecessor_relation=predecessor_relation,
        transition_decision_id=transition_decision.decision_id,
        canonical_priority=_NODE_PRIORITIES[node.node_kind],
        node_instance_sequence=node_sequence,
        snapshot_sequence=snapshot_sequence,
        admission_round=admission_round,
        queue_reason_codes=reasons,
        observed_output_refs=outputs,
        observed_evidence_refs=evidence,
        advisory_refs=advisories,
        lineage_refs=lineage,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_cell_queue_entry_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalCellQueueEntryV02)


def fractal_cell_queue_entry_to_plain_data_v02(value: FractalCellQueueEntryV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalCellQueueEntryV02)


def rebuild_fractal_cell_queue_entry_identity_v02(value: FractalCellQueueEntryV02) -> str:
    return _rebuild_serialized(value, FractalCellQueueEntryV02)


def build_fractal_revise_observation_v02(
    topology: RuntimeExecutionTopologyV02,
    cell_input: FractalCellInputV02,
    queue_entry: FractalCellQueueEntryV02,
    validation_report: FractalRuntimeValidationReportV02,
    *,
    revision_index: int,
    newly_validated_evidence_count: int,
    newly_resolved_constraints_count: int,
    newly_accepted_outputs_count: int,
    newly_introduced_conflicts_count: int,
    consecutive_non_positive_count: int,
    max_consecutive_non_positive_count: int,
    cell_budget_before: FractalRuntimeBudgetV02,
    global_budget_before: FractalRuntimeBudgetV02,
) -> FractalReviseObservationV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(cell_input, FractalCellInputV02, "g2d_cell_input_invalid")
    _require_valid(queue_entry, FractalCellQueueEntryV02, "g2d_queue_entry_invalid")
    if validate_fractal_runtime_validation_report_v02(validation_report):
        raise ValueError("g2d_revise_observation_invalid")
    _require_valid(cell_budget_before, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_valid(global_budget_before, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    integer_values = (revision_index, newly_validated_evidence_count, newly_resolved_constraints_count, newly_accepted_outputs_count, newly_introduced_conflicts_count, consecutive_non_positive_count, max_consecutive_non_positive_count)
    if any(type(item) is not int or item < 0 for item in integer_values):
        raise ValueError("g2d_integer_invalid")
    progress = newly_validated_evidence_count + newly_resolved_constraints_count + newly_accepted_outputs_count - newly_introduced_conflicts_count
    needs_user = "g2d_resolvable_input_needs_user" in validation_report.reason_codes
    terminal = "NEEDS_USER" if needs_user else "DEADEND" if consecutive_non_positive_count >= max_consecutive_non_positive_count or revision_index >= cell_budget_before.max_revise_count else None
    reasons = ("g2d_resolvable_input_needs_user",) if terminal == "NEEDS_USER" else ("g2d_no_progress_deadend",) if terminal == "DEADEND" else ()
    trace = (topology.topology_id, cell_input.cell_id, queue_entry.queue_entry_id, cell_budget_before.budget_id, global_budget_before.budget_id, str(revision_index))
    provisional = FractalReviseObservationV02(
        observation_id="frrevise_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        cell_id=cell_input.cell_id,
        queue_entry_id=queue_entry.queue_entry_id,
        revision_index=revision_index,
        newly_validated_evidence_count=newly_validated_evidence_count,
        newly_resolved_constraints_count=newly_resolved_constraints_count,
        newly_accepted_outputs_count=newly_accepted_outputs_count,
        newly_introduced_conflicts_count=newly_introduced_conflicts_count,
        progress_units=progress,
        consecutive_non_positive_count=consecutive_non_positive_count,
        max_consecutive_non_positive_count=max_consecutive_non_positive_count,
        revise_eligible=terminal is None,
        derived_terminal_state=terminal,
        reason_codes=reasons,
        cell_budget_before_id=cell_budget_before.budget_id,
        global_budget_before_id=global_budget_before.budget_id,
        trace_refs=trace,
        root_review_required=True,
        authority_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_revise_observation_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalReviseObservationV02)


def fractal_revise_observation_to_plain_data_v02(value: FractalReviseObservationV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalReviseObservationV02)


def rebuild_fractal_revise_observation_identity_v02(value: FractalReviseObservationV02) -> str:
    return _rebuild_serialized(value, FractalReviseObservationV02)


def build_fractal_partial_failure_record_v02(
    topology: RuntimeExecutionTopologyV02,
    parent_input: FractalCellInputV02,
    child_result: FractalCellResultV02,
    *,
    failure_stage: str,
    reason_codes: tuple[str, ...],
    source_reason_codes: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    allocated_cell_budget: FractalRuntimeBudgetV02,
    final_cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    required_child: bool,
    sibling_independent: bool,
) -> FractalPartialFailureRecordV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(parent_input, FractalCellInputV02, "g2d_cell_input_invalid")
    _require_valid(child_result, FractalCellResultV02, "g2d_cell_result_invalid")
    for budget in (allocated_cell_budget, final_cell_budget, global_budget):
        _require_valid(budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    public_reasons = _require_text_tuple(reason_codes, public_reasons=True)
    source_reasons = _require_source_reason_tuple(source_reason_codes)
    evidence = _require_text_tuple(evidence_refs)
    if failure_stage not in FAILURE_STAGES or failure_stage == "NONE":
        raise ValueError("g2d_partial_failure_invalid")
    if type(required_child) is not bool or type(sibling_independent) is not bool:
        raise ValueError("g2d_field_type_invalid")
    if child_result.parent_cell_id != parent_input.cell_id or child_result.result_id not in parent_input.context_refs + parent_input.evidence_refs:
        # The parent input need not predict a result ID, but it must own the child slot.
        if child_result.cell_id not in parent_input.ordered_planned_child_cell_ids:
            raise ValueError("g2d_partial_failure_invalid")
    expected_budgets = (
        child_result.allocated_cell_budget_id,
        child_result.final_cell_budget_id,
        child_result.global_budget_id,
    )
    supplied_budgets = (
        allocated_cell_budget.budget_id,
        final_cell_budget.budget_id,
        global_budget.budget_id,
    )
    if expected_budgets != supplied_budgets:
        raise ValueError("g2d_budget_predecessor_invalid")
    if allocated_cell_budget.budget_state != "ALLOCATED" or final_cell_budget.budget_state != "FINAL":
        raise ValueError("g2d_budget_state_transition_invalid")
    if child_result.outcome == "COMPLETED":
        raise ValueError("g2d_success_laundering_forbidden")
    disposition = child_result.outcome
    revise_eligible = child_result.outcome == "DEGRADED" and "g2d_revise_progress_valid" in public_reasons
    trace_refs = (
        topology.topology_id,
        parent_input.cell_id,
        child_result.cell_id,
        child_result.result_id,
        allocated_cell_budget.budget_id,
        final_cell_budget.budget_id,
        global_budget.budget_id,
    )
    provisional = FractalPartialFailureRecordV02(
        partial_failure_id="frfailure_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        parent_cell_id=parent_input.cell_id,
        child_cell_id=child_result.cell_id,
        child_result_id=child_result.result_id,
        failure_stage=failure_stage,
        reason_codes=public_reasons,
        source_reason_codes=source_reasons,
        evidence_refs=evidence,
        trace_refs=trace_refs,
        allocated_cell_budget_id=allocated_cell_budget.budget_id,
        final_cell_budget_id=final_cell_budget.budget_id,
        global_budget_id=global_budget.budget_id,
        retry_eligible=False,
        revise_eligible=revise_eligible,
        required_child=required_child,
        sibling_independent=sibling_independent,
        parent_disposition=disposition,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        final_output_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_partial_failure_record_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalPartialFailureRecordV02)


def fractal_partial_failure_record_to_plain_data_v02(value: FractalPartialFailureRecordV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalPartialFailureRecordV02)


def rebuild_fractal_partial_failure_record_identity_v02(value: FractalPartialFailureRecordV02) -> str:
    return _rebuild_serialized(value, FractalPartialFailureRecordV02)


def build_fractal_backpressure_state_v02(
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    global_budget: FractalRuntimeBudgetV02,
    *,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    evaluated_round: int,
) -> FractalBackpressureStateV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    if type(queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in queue_entries):
        raise ValueError("g2d_backpressure_invalid")
    if type(evaluated_round) is not int or evaluated_round < 0:
        raise ValueError("g2d_backpressure_invalid")
    running = sum(item.state == "RUNNING" for item in queue_entries)
    ready = sum(item.state == "READY" for item in queue_entries)
    deferred = tuple(
        item.queue_entry_id
        for item in queue_entries
        if item.state == "PENDING" and "g2d_transition_backpressure_deferred" in item.queue_reason_codes
    )
    pending = len(deferred)
    if running != global_budget.current_parallelism or running + ready != policy.max_parallelism or not deferred:
        raise ValueError("g2d_backpressure_invalid")
    admission_order = tuple(item.queue_entry_id for item in queue_entries if item.state in {"READY", "RUNNING", "VALIDATING", "PENDING"})
    lineage_refs = (topology.topology_id, policy.policy_id, global_budget.budget_id, str(evaluated_round), *admission_order)
    provisional = FractalBackpressureStateV02(
        backpressure_id="frbackpressure_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        policy_id=policy.policy_id,
        evaluated_round=evaluated_round,
        queue_capacity=policy.max_parallelism,
        running_count=running,
        ready_count=ready,
        pending_count=pending,
        deferred_queue_entry_ids=deferred,
        admission_order=admission_order,
        backpressure_reason="PARALLELISM_CAPACITY_EXHAUSTED",
        reason_codes=("g2d_transition_backpressure_deferred",),
        no_work_dropped=True,
        lineage_refs=lineage_refs,
        global_budget_id=global_budget.budget_id,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_backpressure_state_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalBackpressureStateV02)


def fractal_backpressure_state_to_plain_data_v02(value: FractalBackpressureStateV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalBackpressureStateV02)


def rebuild_fractal_backpressure_state_identity_v02(value: FractalBackpressureStateV02) -> str:
    return _rebuild_serialized(value, FractalBackpressureStateV02)


def _exact_dict_ref(value: object, key: str, reason: str) -> str:
    if type(value) is not dict or type(value.get(key)) is not str or not _ref_valid(value[key]):
        raise ValueError(reason)
    try:
        _plain_value(value, set())
    except (TypeError, ValueError, RecursionError):
        raise ValueError(reason) from None
    return value[key]


def _derive_result_outcome(
    terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    child_results: tuple[FractalCellResultV02, ...],
    partial_failures: tuple[FractalPartialFailureRecordV02, ...],
) -> str:
    states = {entry.state for entry in terminal_queue_entries}
    states.update(result.outcome for result in child_results)
    states.update(failure.parent_disposition for failure in partial_failures)
    for state in ("BLOCKED", "NEEDS_USER", "DEADEND", "DEGRADED"):
        if state in states:
            return state
    return "COMPLETED"


def _ordered_public_reason_union(*families: tuple[str, ...]) -> tuple[str, ...]:
    values: set[str] = set()
    for family in families:
        if not _public_reason_tuple_valid(family):
            raise ValueError("g2d_serialization_invalid")
        values.update(family)
    return tuple(reason for reason in PUBLIC_G2D_REASON_CODES if reason in values)


def _ordered_source_reason_union(*families: tuple[str, ...]) -> tuple[str, ...]:
    output: list[str] = []
    for family in families:
        if not _source_reason_tuple_valid(family):
            raise ValueError("g2d_success_laundering_forbidden")
        for reason in family:
            if reason not in output:
                output.append(reason)
    return tuple(output)


def build_fractal_cell_result_v02(
    topology: RuntimeExecutionTopologyV02,
    cell_input: FractalCellInputV02,
    terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    child_results: tuple[FractalCellResultV02, ...],
    *,
    accepted_output_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    pre_result_validation_report: FractalRuntimeValidationReportV02,
    post_vv_report: dict[str, object],
    gt_advisory_report: dict[str, object],
    partial_failures: tuple[FractalPartialFailureRecordV02, ...],
    allocated_cell_budget: FractalRuntimeBudgetV02,
    final_cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
) -> FractalCellResultV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(cell_input, FractalCellInputV02, "g2d_cell_input_invalid")
    for budget in (allocated_cell_budget, final_cell_budget, global_budget):
        _require_valid(budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    if type(terminal_queue_entries) is not tuple or any(type(item) is not FractalCellQueueEntryV02 for item in terminal_queue_entries):
        raise ValueError("g2d_cell_result_invalid")
    if type(child_results) is not tuple or any(type(item) is not FractalCellResultV02 for item in child_results):
        raise ValueError("g2d_cell_result_invalid")
    if type(partial_failures) is not tuple or any(type(item) is not FractalPartialFailureRecordV02 for item in partial_failures):
        raise ValueError("g2d_partial_failure_invalid")
    outputs = _require_text_tuple(accepted_output_refs)
    evidence = _require_text_tuple(evidence_refs)
    if validate_fractal_runtime_validation_report_v02(pre_result_validation_report):
        raise ValueError("g2d_cell_result_invalid")
    if pre_result_validation_report.status != "PASS" or pre_result_validation_report.validation_target != "CELL_RESULT_PRECONDITIONS":
        raise ValueError("g2d_cell_result_context_mismatch")
    post_vv_ref = _exact_dict_ref(post_vv_report, "vv_report_id", "g2d_post_vv_report_invalid")
    gt_ref = _exact_dict_ref(gt_advisory_report, "gt_report_id", "g2d_gt_advisory_invalid")
    if not terminal_queue_entries or len(terminal_queue_entries) != len(cell_input.ordered_required_queue_entry_ids):
        raise ValueError("g2d_cell_result_postorder_invalid")
    if tuple(item.node_id for item in terminal_queue_entries) != cell_input.ordered_node_ids:
        raise ValueError("g2d_cell_result_postorder_invalid")
    if any(item.cell_id != cell_input.cell_id or item.state not in NODE_TERMINAL_OUTCOMES for item in terminal_queue_entries):
        raise ValueError("g2d_cell_result_context_mismatch")
    actual_children = tuple(item.result_id for item in child_results)
    if len(actual_children) != len(set(actual_children)) or any(item.parent_cell_id != cell_input.cell_id for item in child_results):
        raise ValueError("g2d_cell_result_postorder_invalid")
    if any(item.child_result_id not in actual_children or item.parent_cell_id != cell_input.cell_id for item in partial_failures):
        raise ValueError("g2d_partial_failure_invalid")
    if allocated_cell_budget.owning_cell_id != cell_input.cell_id or allocated_cell_budget.budget_state != "ALLOCATED" or allocated_cell_budget.predecessor_budget_id is not None:
        raise ValueError("g2d_budget_predecessor_invalid")
    if final_cell_budget.owning_cell_id != cell_input.cell_id or final_cell_budget.budget_state != "FINAL" or final_cell_budget.budget_event_kind != "FINALIZE":
        raise ValueError("g2d_budget_state_transition_invalid")
    root_result = cell_input.parent_cell_id is None
    if root_result != (final_cell_budget.budget_id == global_budget.budget_id):
        raise ValueError("g2d_cell_result_context_mismatch")
    outcome = _derive_result_outcome(terminal_queue_entries, child_results, partial_failures)
    public_reasons = _ordered_public_reason_union(
        *(entry.queue_reason_codes for entry in terminal_queue_entries),
        *(failure.reason_codes for failure in partial_failures),
    )
    source_reasons = _ordered_source_reason_union(*(failure.source_reason_codes for failure in partial_failures))
    trace_refs = (
        topology.topology_id,
        cell_input.cell_input_id,
        *(entry.queue_entry_id for entry in terminal_queue_entries),
        *actual_children,
        *(failure.partial_failure_id for failure in partial_failures),
        allocated_cell_budget.budget_id,
        final_cell_budget.budget_id,
        global_budget.budget_id,
        pre_result_validation_report.validation_report_id,
        post_vv_ref,
        gt_ref,
    )
    provisional = FractalCellResultV02(
        result_id="frcellresult_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        topology_seed_id=topology.topology_seed_id,
        cell_id=cell_input.cell_id,
        parent_cell_id=cell_input.parent_cell_id,
        cell_depth=cell_input.cell_depth,
        cell_input_id=cell_input.cell_input_id,
        ordered_terminal_queue_entry_ids=tuple(item.queue_entry_id for item in terminal_queue_entries),
        ordered_child_result_ids=actual_children,
        outcome=outcome,
        accepted_output_refs=outputs,
        evidence_refs=evidence,
        pre_result_validation_report_id=pre_result_validation_report.validation_report_id,
        post_vv_report_ref=post_vv_ref,
        gt_advisory_ref=gt_ref,
        partial_failure_ids=tuple(item.partial_failure_id for item in partial_failures),
        allocated_cell_budget_id=allocated_cell_budget.budget_id,
        final_cell_budget_id=final_cell_budget.budget_id,
        global_budget_id=global_budget.budget_id,
        scope_ref=cell_input.scope_ref,
        reason_codes=public_reasons,
        source_reason_codes=source_reasons,
        trace_refs=trace_refs,
        parent_return_required=True,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_cell_result_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalCellResultV02)


def fractal_cell_result_to_plain_data_v02(value: FractalCellResultV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalCellResultV02)


def rebuild_fractal_cell_result_identity_v02(value: FractalCellResultV02) -> str:
    return _rebuild_serialized(value, FractalCellResultV02)


def _require_exact_tuple_type(values: object, item_type: type[object], reason: str) -> tuple[object, ...]:
    if type(values) is not tuple or any(type(item) is not item_type for item in values):
        raise ValueError(reason)
    return values


def build_fractal_runtime_trace_v02(
    topology: RuntimeExecutionTopologyV02,
    source_binding: RuntimeTopologySourceBindingV02,
    *,
    topology_artifact: KernelArtifactV01,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
    state_transition_decisions: tuple[TransitionDecisionV01, ...],
    cell_inputs: tuple[FractalCellInputV02, ...],
    cell_results: tuple[FractalCellResultV02, ...],
    result_artifacts: tuple[KernelArtifactV01, ...],
    runtime_abi_artifacts: tuple[KernelArtifactV01, ...],
    scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    revise_observations: tuple[FractalReviseObservationV02, ...],
    partial_failures: tuple[FractalPartialFailureRecordV02, ...],
    backpressure_states: tuple[FractalBackpressureStateV02, ...],
    budgets: tuple[FractalRuntimeBudgetV02, ...],
    topology_transition_decision: TransitionDecisionV01,
    parent_return_transition_decision: TransitionDecisionV01,
    root_result_artifact: KernelArtifactV01,
) -> FractalRuntimeTraceV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    families = (
        (queue_entries, FractalCellQueueEntryV02),
        (queue_artifacts, KernelArtifactV01),
        (state_transition_decisions, TransitionDecisionV01),
        (cell_inputs, FractalCellInputV02),
        (cell_results, FractalCellResultV02),
        (result_artifacts, KernelArtifactV01),
        (runtime_abi_artifacts, KernelArtifactV01),
        (scope_projections, ParentChildScopeProjectionV02),
        (revise_observations, FractalReviseObservationV02),
        (partial_failures, FractalPartialFailureRecordV02),
        (backpressure_states, FractalBackpressureStateV02),
        (budgets, FractalRuntimeBudgetV02),
    )
    for values, item_type in families:
        _require_exact_tuple_type(values, item_type, "g2d_runtime_trace_invalid")
    for item in (topology_artifact, root_result_artifact):
        if type(item) is not KernelArtifactV01:
            raise ValueError("g2d_runtime_trace_invalid")
    for item in (topology_transition_decision, parent_return_transition_decision):
        if type(item) is not TransitionDecisionV01:
            raise ValueError("g2d_transition_decision_substituted")
    if len(queue_entries) != len(queue_artifacts) or len(queue_entries) != len(state_transition_decisions):
        raise ValueError("g2d_runtime_trace_invalid")
    runtime_ids = tuple(item.artifact_id for item in runtime_abi_artifacts)
    queue_artifact_ids = tuple(item.artifact_id for item in queue_artifacts)
    result_artifact_ids = tuple(item.artifact_id for item in result_artifacts)
    if len(runtime_ids) != len(set(runtime_ids)) or set(runtime_ids) != set(queue_artifact_ids + result_artifact_ids):
        raise ValueError("g2d_trace_lineage_invalid")
    if not result_artifacts or root_result_artifact.artifact_id != result_artifacts[-1].artifact_id:
        raise ValueError("g2d_root_result_required_for_parent_return")
    if tuple(item.decision_id for item in state_transition_decisions) != tuple(item.transition_decision_id for item in queue_entries):
        raise ValueError("g2d_transition_decision_substituted")
    if any(a.evaluated_round >= b.evaluated_round for a, b in zip(backpressure_states, backpressure_states[1:])):
        raise ValueError("g2d_backpressure_invalid")
    provisional = FractalRuntimeTraceV02(
        trace_id="frtrace_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        topology_seed_id=topology.topology_seed_id,
        source_binding_id=source_binding.source_binding_id,
        ordered_queue_entry_ids=tuple(item.queue_entry_id for item in queue_entries),
        state_transition_decision_ids=tuple(item.decision_id for item in state_transition_decisions),
        cell_input_ids=tuple(item.cell_input_id for item in cell_inputs),
        cell_result_ids=tuple(item.result_id for item in cell_results),
        scope_projection_ids=tuple(item.projection_id for item in scope_projections),
        revise_observation_ids=tuple(item.observation_id for item in revise_observations),
        partial_failure_ids=tuple(item.partial_failure_id for item in partial_failures),
        backpressure_state_ids=tuple(item.backpressure_id for item in backpressure_states),
        budget_ids=tuple(item.budget_id for item in budgets),
        abi_artifact_refs=(topology_artifact.artifact_id, *runtime_ids),
        transition_refs=(topology_transition_decision.decision_id, *(item.decision_id for item in state_transition_decisions), parent_return_transition_decision.decision_id),
        parent_return_refs=(root_result_artifact.artifact_id,),
        root_review_required=True,
        provider_calls=0,
        model_calls=0,
        network_calls=0,
        connector_calls=0,
        external_drs_calls=0,
        real_world_effects_count=0,
    )
    return _finish_identity(provisional)


def validate_fractal_runtime_trace_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalRuntimeTraceV02)


def fractal_runtime_trace_to_plain_data_v02(value: FractalRuntimeTraceV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalRuntimeTraceV02)


def rebuild_fractal_runtime_trace_identity_v02(value: FractalRuntimeTraceV02) -> str:
    return _rebuild_serialized(value, FractalRuntimeTraceV02)


def build_fractal_runtime_report_v02(
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    source_binding: RuntimeTopologySourceBindingV02,
    *,
    ordered_cell_results: tuple[FractalCellResultV02, ...],
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    backpressure_states: tuple[FractalBackpressureStateV02, ...],
    runtime_trace: FractalRuntimeTraceV02,
    final_budget: FractalRuntimeBudgetV02,
    parent_return_transition_decision: TransitionDecisionV01,
    root_result_artifact: KernelArtifactV01,
) -> FractalRuntimeReportV02:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(source_binding, RuntimeTopologySourceBindingV02, "g2d_topology_source_binding_invalid")
    _require_valid(runtime_trace, FractalRuntimeTraceV02, "g2d_runtime_trace_invalid")
    _require_valid(final_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    _require_exact_tuple_type(ordered_cell_results, FractalCellResultV02, "g2d_runtime_report_invalid")
    _require_exact_tuple_type(queue_entries, FractalCellQueueEntryV02, "g2d_runtime_report_invalid")
    _require_exact_tuple_type(backpressure_states, FractalBackpressureStateV02, "g2d_runtime_report_invalid")
    if type(topology_artifact) is not KernelArtifactV01 or type(root_result_artifact) is not KernelArtifactV01:
        raise ValueError("g2d_runtime_report_invalid")
    if type(parent_return_transition_decision) is not TransitionDecisionV01:
        raise ValueError("g2d_transition_decision_substituted")
    if not ordered_cell_results:
        raise ValueError("g2d_root_result_required_for_parent_return")
    root_result = ordered_cell_results[-1]
    if root_result.parent_cell_id is not None or root_result.cell_id != topology.root_cell_id:
        raise ValueError("g2d_root_result_required_for_parent_return")
    if root_result_artifact.artifact_id not in runtime_trace.parent_return_refs or runtime_trace.parent_return_refs != (root_result_artifact.artifact_id,):
        raise ValueError("g2d_parent_return_invalid")
    if final_budget.budget_state != "FINAL" or final_budget.budget_scope != "ROOT_GLOBAL_AND_CELL" or final_budget.owning_cell_id != topology.root_cell_id:
        raise ValueError("g2d_budget_state_transition_invalid")
    if tuple(item.result_id for item in ordered_cell_results) != runtime_trace.cell_result_ids:
        raise ValueError("g2d_result_report_ref_mismatch")
    if tuple(item.queue_entry_id for item in queue_entries) != runtime_trace.ordered_queue_entry_ids:
        raise ValueError("g2d_queue_order_mismatch")
    if tuple(item.backpressure_id for item in backpressure_states) != runtime_trace.backpressure_state_ids:
        raise ValueError("g2d_runtime_trace_invalid")
    counts = {outcome: sum(item.outcome == outcome for item in ordered_cell_results) for outcome in CELL_OUTCOMES}
    provisional = FractalRuntimeReportV02(
        report_id="frreport_v02:" + _ZERO_SHA256,
        report_version="v0.2",
        profile_id=PROFILE_IDS[0],
        topology_id=topology.topology_id,
        topology_seed_id=topology.topology_seed_id,
        topology_artifact_id=topology_artifact.artifact_id,
        source_binding_id=source_binding.source_binding_id,
        request_id=topology.request_id,
        transaction_id=topology.transaction_id,
        owning_root_id=topology.owning_root_id,
        domain_id=topology.domain_id,
        accepted_mode=topology.accepted_mode,
        accepted_scope_ref=topology.accepted_scope_ref,
        runtime_outcome=root_result.outcome,
        ordered_cell_result_ids=tuple(item.result_id for item in ordered_cell_results),
        completed_cell_count=counts["COMPLETED"],
        degraded_cell_count=counts["DEGRADED"],
        blocked_cell_count=counts["BLOCKED"],
        needs_user_cell_count=counts["NEEDS_USER"],
        deadend_cell_count=counts["DEADEND"],
        queue_entry_ids=tuple(item.queue_entry_id for item in queue_entries),
        backpressure_state_ids=tuple(item.backpressure_id for item in backpressure_states),
        runtime_trace_id=runtime_trace.trace_id,
        final_budget_id=final_budget.budget_id,
        parent_return_transition_decision_id=parent_return_transition_decision.decision_id,
        parent_return_refs=(root_result_artifact.artifact_id,),
        report_status="PASS",
        reason_codes=root_result.reason_codes,
        topology_created_count=1,
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
        root_review_required=True,
    )
    return _finish_identity(provisional)


def validate_fractal_runtime_report_v02(value: object) -> FractalRuntimeValidationReportV02:
    return _validate_serialized(value, FractalRuntimeReportV02)


def fractal_runtime_report_to_plain_data_v02(value: FractalRuntimeReportV02) -> dict[str, object]:
    return _serialize_serialized(value, FractalRuntimeReportV02)


def rebuild_fractal_runtime_report_identity_v02(value: FractalRuntimeReportV02) -> str:
    return _rebuild_serialized(value, FractalRuntimeReportV02)


def build_fractal_runtime_validation_report_v02(
    *,
    validation_target: str,
    validated_object_id: str | None,
    failure_stage: str,
    reason_codes: tuple[str, ...],
    source_reason_codes: tuple[str, ...],
) -> FractalRuntimeValidationReportV02:
    public_reasons = _require_text_tuple(reason_codes, public_reasons=True)
    source_reasons = _require_source_reason_tuple(source_reason_codes)
    if validation_target not in VALIDATION_TARGETS or failure_stage not in FAILURE_STAGES:
        raise ValueError("g2d_validation_status_stage_mismatch")
    passed = failure_stage == "NONE" and not public_reasons and not source_reasons
    if passed:
        if validation_target == "SOURCE_CONTEXT_STRUCTURAL":
            if validated_object_id is not None:
                raise ValueError("g2d_validation_target_id_mismatch")
        elif type(validated_object_id) is not str:
            raise ValueError("g2d_validation_target_id_mismatch")
        status = "PASS"
        return_to_root = False
    else:
        if failure_stage == "NONE" or (not public_reasons and not source_reasons):
            raise ValueError("g2d_validation_status_stage_mismatch")
        if validated_object_id is not None:
            raise ValueError("g2d_validation_target_id_mismatch")
        status = "FAIL_CLOSED"
        return_to_root = True
    provisional = FractalRuntimeValidationReportV02(
        validation_report_id="frvalidation_v02:" + _ZERO_SHA256,
        validation_target=validation_target,
        validated_object_id=validated_object_id,
        status=status,
        failure_stage=failure_stage,
        reason_codes=public_reasons,
        source_reason_codes=source_reasons,
        return_to_root_required=return_to_root,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    errors = _validation_report_semantic_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def validate_fractal_runtime_validation_report_v02(value: object) -> tuple[str, ...]:
    try:
        if type(value) is not FractalRuntimeValidationReportV02:
            return ("g2d_type_invalid",)
        errors = list(_common_errors(value, FractalRuntimeValidationReportV02))
        errors.extend(_specific_errors(value))
        return _sort_reasons(errors) if errors else ()
    except Exception:
        return ("g2d_serialization_invalid",)


def fractal_runtime_validation_report_to_plain_data_v02(value: FractalRuntimeValidationReportV02) -> dict[str, object]:
    errors = validate_fractal_runtime_validation_report_v02(value)
    if errors:
        raise ValueError(errors[0])
    return _plain_data_unchecked(value)


def rebuild_fractal_runtime_validation_report_identity_v02(value: FractalRuntimeValidationReportV02) -> str:
    if type(value) is not FractalRuntimeValidationReportV02:
        raise TypeError("g2d_type_invalid")
    return _rebuild_identity(value)


def derive_fractal_root_cell_id_v02(
    *,
    source_binding_id: str,
    runtime_policy_id: str,
    accepted_mode: str,
    accepted_scope_ref: str,
) -> str:
    if not _identity_pattern_valid(source_binding_id, "frsource_v02:") or not _identity_pattern_valid(runtime_policy_id, "frpolicy_v02:"):
        raise ValueError("g2d_root_cell_identity_invalid")
    if accepted_mode not in TOPOLOGY_ELIGIBLE_MODES or not _ref_valid(accepted_scope_ref):
        raise ValueError("g2d_root_cell_identity_invalid")
    material = [source_binding_id, runtime_policy_id, accepted_mode, accepted_scope_ref, "ROOT_CELL"]
    digest = _domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_ROOT_CELL",
        payload=_canonical_json_bytes_v01(material),
    )
    return "frrootcell_v02:" + digest


def derive_fractal_child_cell_id_v02(
    *,
    topology_seed_id: str,
    parent_cell_id: str,
    canonical_child_index: int,
    accepted_mode: str,
    selected_local_mode_profile_id: str,
    source_mode_profile_set_id: str,
    child_scope_ref: str,
    runtime_policy_id: str,
    required_capability_ids: tuple[str, ...],
    forbidden_claims: tuple[str, ...],
    child_depth: int,
) -> str:
    if not _identity_pattern_valid(topology_seed_id, "frseed_v02:") or not (_identity_pattern_valid(parent_cell_id, "frrootcell_v02:") or _identity_pattern_valid(parent_cell_id, "frchildcell_v02:")):
        raise ValueError("g2d_child_cell_identity_invalid")
    if type(canonical_child_index) is not int or canonical_child_index not in {0, 1} or type(child_depth) is not int or child_depth < 1:
        raise ValueError("g2d_child_cell_identity_invalid")
    if accepted_mode not in TOPOLOGY_ELIGIBLE_MODES or not all(_ref_valid(item) for item in (selected_local_mode_profile_id, source_mode_profile_set_id, child_scope_ref)):
        raise ValueError("g2d_child_cell_identity_invalid")
    if not _identity_pattern_valid(runtime_policy_id, "frpolicy_v02:"):
        raise ValueError("g2d_child_cell_identity_invalid")
    capabilities = _require_text_tuple(required_capability_ids)
    forbidden = _require_text_tuple(forbidden_claims)
    material = [
        topology_seed_id,
        parent_cell_id,
        canonical_child_index,
        accepted_mode,
        selected_local_mode_profile_id,
        source_mode_profile_set_id,
        child_scope_ref,
        runtime_policy_id,
        list(capabilities),
        list(forbidden),
        child_depth,
    ]
    digest = _domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_CHILD_CELL",
        payload=_canonical_json_bytes_v01(material),
    )
    return "frchildcell_v02:" + digest
