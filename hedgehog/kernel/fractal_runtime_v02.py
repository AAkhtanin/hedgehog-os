"""Deterministic contracts for Fractal Runtime v0.2 through G2-D3.

This module owns canonical data, structural and G2-C source validation, and
deterministic topology, queue, budget, scope, and backpressure construction.
It performs no provider, model, network, connector, filesystem, clock, random,
DRS, permission, packet, receipt, FinalOutput, authority, or effect operation.
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
    build_kernel_artifact_v01 as _build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01 as _validate_kernel_artifact_v01,
)
from hedgehog.kernel.execution_mode_router_v01 import (
    ExecutionModeProposalV01,
    ExecutionModeRouterInputV01,
    ExecutionModeSourceContextV01,
    RootExecutionModeDecisionV01,
    RootExecutionModeReviewInputV01,
    evaluate_execution_mode_proposal_to_root_transition_v01 as _evaluate_execution_mode_proposal_to_root_transition_v01,
    evaluate_execution_mode_root_route_transition_v01 as _evaluate_execution_mode_root_route_transition_v01,
    project_execution_mode_proposal_kernel_artifact_v01 as _project_execution_mode_proposal_kernel_artifact_v01,
    project_execution_mode_route_eligibility_kernel_artifact_v01 as _project_execution_mode_route_eligibility_kernel_artifact_v01,
    project_root_execution_mode_decision_kernel_artifact_v01 as _project_root_execution_mode_decision_kernel_artifact_v01,
    validate_execution_mode_abi_profile_v01 as _validate_execution_mode_abi_profile_v01,
    validate_execution_mode_proposal_against_sources_v01 as _validate_execution_mode_proposal_against_sources_v01,
    validate_execution_mode_route_eligibility_against_source_v01 as _validate_execution_mode_route_eligibility_against_source_v01,
    validate_execution_mode_router_input_against_sources_v01 as _validate_execution_mode_router_input_against_sources_v01,
    validate_execution_mode_source_context_v01 as _validate_execution_mode_source_context_v01,
    validate_root_execution_mode_decision_against_source_v01 as _validate_root_execution_mode_decision_against_source_v01,
    validate_root_execution_mode_review_input_against_sources_v01 as _validate_root_execution_mode_review_input_against_sources_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    validate_root_decision_input_v01 as _validate_root_decision_input_v01,
    validate_root_decision_kernel_v01 as _validate_root_decision_kernel_v01,
    validate_root_decision_result_v01 as _validate_root_decision_result_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    TransitionDecisionV01,
    TransitionRegistryV01,
    build_fractal_runtime_transition_registry_profile_v02 as _build_fractal_runtime_transition_registry_profile_v02,
    rebuild_fractal_runtime_transition_decision_identity_v02 as _rebuild_fractal_runtime_transition_decision_identity_v02,
    validate_execution_mode_transition_registry_profile_v01 as _validate_execution_mode_transition_registry_profile_v01,
    validate_fractal_runtime_transition_decision_v02 as _validate_fractal_runtime_transition_decision_v02,
    validate_fractal_runtime_transition_registry_profile_v02 as _validate_fractal_runtime_transition_registry_profile_v02,
)


MODULE_ID = "kernel_fractal_runtime_v02"
SLICE_ID = "gate2_g2d3_fractal_runtime_queue_budget_scope_contracts"
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
            and (value.max_parallelism, value.max_revise_count, value.max_consecutive_no_progress) == (3, 2, 2)
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
        projection_name = (
            "ROOT"
            if value.parent_cell_id is None
            else "STRUCTURAL_DEPTH_2_LEAF"
            if value.cell_depth == 2
            else "REFERENCE_CHILD_SLOT_1"
        )
        projection_row = next(
            (
                row
                for row in CELL_NODE_PROJECTION_ROWS_V02
                if row[0] == value.accepted_mode and row[1] == projection_name
            ),
            None,
        )
        projected_indexes = () if projection_row is None else projection_row[3]
        expected_node_count = len(projected_indexes)
        expected_required_outputs = tuple(
            mode_rows[index][9]
            for index in projected_indexes
            if mode_rows[index][10]
        )
        expected_child_count = 0 if projection_row is None else projection_row[4]
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
        elif (
            value.accepted_mode != "full_fractal"
            or value.cell_depth not in {1, 2}
            or value.scope_projection_id is None
            or not _identity_pattern_valid(value.cell_id, "frchildcell_v02:")
        ):
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
        max_parallelism=3,
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
    if paired_cell_budget is not None:
        _require_valid(paired_cell_budget, FractalRuntimeBudgetV02, "g2d_budget_event_pair_mismatch")
        if (
            not root_axis
            or paired_cell_budget.budget_scope != "CHILD_CELL_LOCAL"
            or paired_cell_budget.policy_id != policy.policy_id
            or paired_cell_budget.topology_seed_id != topology_seed.topology_seed_id
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
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
        paired_global_activation = root_axis and paired_cell_budget is not None
        expected_predecessor_state = "ACTIVE" if paired_global_activation else "ALLOCATED"
        if (
            budget_state != "ACTIVE"
            or predecessor_budget.budget_state != expected_predecessor_state
            or (
                not paired_global_activation
                and predecessor_budget.budget_event_kind != "INITIAL_ALLOCATION"
            )
            or (
                paired_global_activation
                and paired_cell_budget.budget_event_kind != "ACTIVATE"
            )
        ):
            raise ValueError("g2d_budget_state_transition_invalid")
    if budget_event_kind == "CELL_CREATE":
        if budget_state != "ACTIVE" or predecessor_budget.budget_state != "ACTIVE" or predecessor_budget.budget_event_kind != "ACTIVATE":
            raise ValueError("g2d_budget_state_transition_invalid")
    if budget_event_kind in {"ACTIVATE", "CELL_CREATE"}:
        child_event = not root_axis or paired_cell_budget is not None
        if child_event:
            if (
                budget_context_input is None
                or canonical_child_index is None
                or not 0 <= canonical_child_index < len(
                    budget_context_input.ordered_planned_child_cell_ids
                )
                or not allocation_queue_entries
            ):
                raise ValueError("g2d_budget_event_context_invalid")
            if not root_axis and owning_cell_id not in budget_context_input.ordered_planned_child_cell_ids:
                raise ValueError("g2d_child_lineage_mismatch")
            if root_axis and (
                paired_cell_budget is None
                or paired_cell_budget.owning_cell_id
                != budget_context_input.ordered_planned_child_cell_ids[canonical_child_index]
                or paired_cell_budget.budget_event_kind != budget_event_kind
            ):
                raise ValueError("g2d_budget_event_pair_mismatch")
        elif budget_context_input is not None or canonical_child_index is not None or allocation_queue_entries:
            raise ValueError("g2d_budget_event_context_invalid")
    if budget_event_kind in {"START_NODE", "FINISH_NODE", "REVISE", "FINALIZE"}:
        if transition_decision is None or canonical_child_index is not None or allocation_queue_entries or child_result is not None:
            raise ValueError("g2d_budget_event_context_invalid")
        if budget_context_input is None:
            raise ValueError("g2d_budget_event_context_invalid")
        if budget_event_kind != "FINALIZE" and budget_state != "ACTIVE":
            raise ValueError("g2d_budget_state_transition_invalid")
        if paired_cell_budget is not None and (
            paired_cell_budget.owning_cell_id != budget_context_input.cell_id
            or paired_cell_budget.budget_event_kind != budget_event_kind
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
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


def _source_report_v02(
    *,
    public_reason: str | None,
    source_reasons: tuple[str, ...] = (),
) -> FractalRuntimeValidationReportV02:
    return build_fractal_runtime_validation_report_v02(
        validation_target="SOURCE_CONTEXT_STRUCTURAL",
        validated_object_id=None,
        failure_stage="NONE" if public_reason is None and not source_reasons else "SOURCE_CONTEXT",
        reason_codes=() if public_reason is None else (public_reason,),
        source_reason_codes=source_reasons,
    )


def _source_reasons_from_report_v02(value: object) -> tuple[str, ...]:
    reasons: list[str] = []
    for name in ("reason_codes", "source_reason_codes"):
        current = getattr(value, name, ())
        if type(current) is tuple:
            for reason in current:
                if type(reason) is str and not _REASON_PATTERN.fullmatch(reason) and reason not in reasons:
                    reasons.append(reason)
    return tuple(reasons)


def _source_context_failure_v02(
    reason: str,
    report: object | None = None,
) -> tuple[str, tuple[str, ...]]:
    return reason, () if report is None else _source_reasons_from_report_v02(report)


def _validate_source_context_family_v02(
    value: object,
) -> tuple[str | None, tuple[str, ...]]:
    try:
        if type(value) is not FractalRuntimeSourceContextV02:
            return _source_context_failure_v02("g2d_source_context_invalid")
        source_report = _validate_execution_mode_source_context_v01(value.g2c_source_context)
        if source_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_g2c_context_invalid", source_report)
        router_report = _validate_execution_mode_router_input_against_sources_v01(
            router_input=value.router_input,
            source_context=value.g2c_source_context,
        )
        if router_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_g2c_router_input_invalid", router_report)
        proposal_report = _validate_execution_mode_proposal_against_sources_v01(
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
        )
        if proposal_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_g2c_proposal_invalid", proposal_report)
        if _validate_execution_mode_transition_registry_profile_v01(value.transition_registry):
            return _source_context_failure_v02("g2d_g2c_context_invalid")
        expected_proposal_artifact = _project_execution_mode_proposal_kernel_artifact_v01(
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
        )
        if value.proposal_artifact != expected_proposal_artifact:
            return _source_context_failure_v02("g2d_g2c_proposal_artifact_invalid")
        expected_proposal_transition = _evaluate_execution_mode_proposal_to_root_transition_v01(
            registry=value.transition_registry,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
        )
        if value.proposal_transition_decision != expected_proposal_transition:
            return _source_context_failure_v02("g2d_g2c_proposal_transition_invalid")
        review_report = _validate_root_execution_mode_review_input_against_sources_v01(
            review_input=value.review_input,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
        )
        if review_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_g2c_review_input_invalid", review_report)
        if _validate_root_decision_kernel_v01(value.root_kernel):
            return _source_context_failure_v02("g2d_g2c_root_kernel_invalid")
        if _validate_root_decision_input_v01(
            kernel=value.root_kernel,
            decision_input=value.root_decision_input,
        ):
            return _source_context_failure_v02("g2d_g2c_root_input_invalid")
        if _validate_root_decision_result_v01(
            kernel=value.root_kernel,
            decision_input=value.root_decision_input,
            result=value.root_decision_result,
        ):
            return _source_context_failure_v02("g2d_g2c_root_result_invalid")
        decision_report = _validate_root_execution_mode_decision_against_source_v01(
            decision=value.decision,
            review_input=value.review_input,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
        )
        if decision_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_g2c_decision_invalid", decision_report)
        expected_decision_artifact = _project_root_execution_mode_decision_kernel_artifact_v01(
            decision=value.decision,
            review_input=value.review_input,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
        )
        if value.decision_artifact != expected_decision_artifact:
            return _source_context_failure_v02("g2d_g2c_decision_artifact_invalid")
        expected_route_transition = _evaluate_execution_mode_root_route_transition_v01(
            registry=value.transition_registry,
            proposal_transition_decision=value.proposal_transition_decision,
            review_input=value.review_input,
            decision=value.decision,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
            proposal_artifact=value.proposal_artifact,
            decision_artifact=value.decision_artifact,
        )
        if value.root_route_transition_decision != expected_route_transition:
            return _source_context_failure_v02("g2d_g2c_post_root_transition_invalid")
        expected_route_artifact = _project_execution_mode_route_eligibility_kernel_artifact_v01(
            decision=value.decision,
            review_input=value.review_input,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
            decision_artifact=value.decision_artifact,
            root_route_transition_decision=value.root_route_transition_decision,
        )
        if expected_route_artifact is None or value.route_eligibility_artifact != expected_route_artifact:
            return _source_context_failure_v02("g2d_route_eligibility_missing")
        route_report = _validate_execution_mode_route_eligibility_against_source_v01(
            route_eligibility_artifact=value.route_eligibility_artifact,
            decision=value.decision,
            review_input=value.review_input,
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
            decision_artifact=value.decision_artifact,
            root_route_transition_decision=value.root_route_transition_decision,
        )
        if route_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_route_eligibility_invalid", route_report)
        abi_report = _validate_execution_mode_abi_profile_v01(
            proposal=value.proposal,
            router_input=value.router_input,
            source_context=value.g2c_source_context,
            proposal_artifact=value.proposal_artifact,
            proposal_transition_decision=value.proposal_transition_decision,
            review_input=value.review_input,
            decision=value.decision,
            root_kernel=value.root_kernel,
            root_decision_input=value.root_decision_input,
            root_decision_result=value.root_decision_result,
            decision_artifact=value.decision_artifact,
            root_route_transition_decision=value.root_route_transition_decision,
            route_eligibility_artifact=value.route_eligibility_artifact,
        )
        if abi_report.validation_status != "PASS":
            return _source_context_failure_v02("g2d_route_eligibility_invalid", abi_report)
        if value.decision.outcome not in {"ACCEPT", "NARROW"}:
            return _source_context_failure_v02("g2d_terminal_consumption_forbidden")
        if value.decision.accepted_mode not in TOPOLOGY_ELIGIBLE_MODES:
            if value.decision.downstream_consumption_class == "SHORTCUT_RETURN_TO_ROOT":
                return _source_context_failure_v02("g2d_shortcut_consumption_forbidden")
            return _source_context_failure_v02("g2d_mode_not_topology_eligible")
        if value.decision.downstream_consumption_class != "RUNTIME_TOPOLOGY_ELIGIBLE":
            return _source_context_failure_v02(
                "g2d_shortcut_consumption_forbidden"
                if value.decision.downstream_consumption_class == "SHORTCUT_RETURN_TO_ROOT"
                else "g2d_terminal_consumption_forbidden"
            )
        if value.root_decision_result.root_commit_created is not True:
            return _source_context_failure_v02("g2d_g2c_root_result_invalid")
        snapshot = value.router_input.local_routing_snapshot
        expected_policy = build_fractal_runtime_policy_v02(
            required_downstream_capability_ids=value.proposal.required_downstream_capability_ids,
            permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
        )
        if value.runtime_policy != expected_policy:
            return _source_context_failure_v02("g2d_topology_policy_invalid")
        payload = _kernel_artifact_to_plain_dict_v01(
            value.route_eligibility_artifact
        )["payload"]
        assert type(payload) is dict
        if (
            payload.get("downstream_consumption_class") != "RUNTIME_TOPOLOGY_ELIGIBLE"
            or payload.get("accepted_mode") != value.decision.accepted_mode
            or payload.get("accepted_scope_ref") != value.decision.accepted_scope_ref
            or payload.get("downstream_action_packet_required")
            is not value.decision.downstream_action_packet_required
            or value.proposal.downstream_action_packet_required
            is not value.decision.downstream_action_packet_required
        ):
            return _source_context_failure_v02("g2d_route_eligibility_context_mismatch")
        return None, ()
    except Exception:
        return _source_context_failure_v02("g2d_source_context_invalid")


def build_fractal_runtime_source_context_v02(
    *,
    transition_registry: TransitionRegistryV01,
    g2c_source_context: ExecutionModeSourceContextV01,
    router_input: ExecutionModeRouterInputV01,
    proposal: ExecutionModeProposalV01,
    proposal_artifact: KernelArtifactV01,
    proposal_transition_decision: TransitionDecisionV01,
    review_input: RootExecutionModeReviewInputV01,
    decision: RootExecutionModeDecisionV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    decision_artifact: KernelArtifactV01,
    root_route_transition_decision: TransitionDecisionV01,
    route_eligibility_artifact: KernelArtifactV01,
    runtime_policy: FractalRuntimePolicyV02,
) -> FractalRuntimeSourceContextV02:
    value = FractalRuntimeSourceContextV02(
        transition_registry=transition_registry,
        g2c_source_context=g2c_source_context,
        router_input=router_input,
        proposal=proposal,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition_decision,
        review_input=review_input,
        decision=decision,
        root_kernel=root_kernel,
        root_decision_input=root_decision_input,
        root_decision_result=root_decision_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition_decision,
        route_eligibility_artifact=route_eligibility_artifact,
        runtime_policy=runtime_policy,
    )
    report = validate_fractal_runtime_source_context_v02(value)
    if report.status != "PASS":
        raise ValueError(report.reason_codes[0] if report.reason_codes else "g2d_source_context_invalid")
    return value


def validate_fractal_runtime_source_context_v02(
    value: object,
) -> FractalRuntimeValidationReportV02:
    reason, source_reasons = _validate_source_context_family_v02(value)
    return _source_report_v02(public_reason=reason, source_reasons=source_reasons)


def validate_runtime_topology_source_binding_against_g2c_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
) -> FractalRuntimeValidationReportV02:
    try:
        context_report = validate_fractal_runtime_source_context_v02(source_context)
        structural = validate_runtime_topology_source_binding_v02(value)
        valid = context_report.status == structural.status == "PASS"
        expected = build_runtime_topology_source_binding_v02(source_context=source_context) if valid else None
        valid = bool(
            valid
            and type(value) is RuntimeTopologySourceBindingV02
            and value == expected
            and _canonical_json_bytes_v01(runtime_topology_source_binding_to_plain_data_v02(value))
            == _canonical_json_bytes_v01(runtime_topology_source_binding_to_plain_data_v02(expected))
        )
        return build_fractal_runtime_validation_report_v02(
            validation_target="SOURCE_BINDING_AGAINST_G2C",
            validated_object_id=value.source_binding_id if valid else None,
            failure_stage="NONE" if valid else "SOURCE_BINDING",
            reason_codes=() if valid else ("g2d_topology_source_binding_invalid",),
            source_reason_codes=(),
        )
    except Exception:
        return build_fractal_runtime_validation_report_v02(
            validation_target="SOURCE_BINDING_AGAINST_G2C",
            validated_object_id=None,
            failure_stage="SOURCE_BINDING",
            reason_codes=("g2d_topology_source_binding_invalid",),
            source_reason_codes=(),
        )


def _construct_runtime_execution_topology_from_source_v02(
    source_context: FractalRuntimeSourceContextV02,
) -> RuntimeExecutionTopologyV02:
    source_binding = build_runtime_topology_source_binding_v02(source_context=source_context)
    policy = source_context.runtime_policy
    root_cell_id = derive_fractal_root_cell_id_v02(
        source_binding_id=source_binding.source_binding_id,
        runtime_policy_id=policy.policy_id,
        accepted_mode=source_binding.accepted_mode,
        accepted_scope_ref=source_binding.accepted_scope_ref,
    )
    seed = build_runtime_topology_seed_v02(source_binding, policy, root_cell_id=root_cell_id)
    global_budget = build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=None,
        owning_cell_id=root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=None,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    node_rows = dict(MODE_NODE_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    nodes = tuple(
        build_runtime_topology_node_v02(
            seed,
            source_binding,
            policy,
            canonical_index=row[0],
            node_kind=row[1],
            depth=0,
            scope_ref=source_binding.accepted_scope_ref,
            cell_binding_class=row[2],
            scope_binding_class=row[3],
            budget_binding_class=row[4],
            required_capability_ids=(
                source_binding.required_downstream_capability_ids
                if row[5] == ("SRC_CAPS",)
                else row[5]
            ),
            input_ref_derivation_class=row[8],
        )
        for row in node_rows
    )
    edge_rows = dict(MODE_EDGE_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    edges = tuple(
        build_runtime_topology_edge_v02(
            seed,
            nodes[row[2]],
            nodes[row[3]],
            edge_kind=row[4],
            canonical_index=row[0],
            cell_projection_class=row[1],
        )
        for row in edge_rows
    )
    assignment_rows = dict(MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[source_binding.accepted_mode]
    assignments = tuple(
        build_runtime_assignment_v02(
            seed,
            nodes[row[1]],
            assignment_kind=row[2],
            executor_component_id=row[3],
            capability_ids=nodes[row[1]].required_capability_ids if row[4] == ("SRC_CAPS",) else row[4],
            cell_binding_class=row[5],
            scope_binding_class=row[6],
            budget_binding_class=row[7],
        )
        for row in assignment_rows
    )
    return build_runtime_execution_topology_v02(
        source_binding,
        seed,
        policy,
        nodes=nodes,
        edges=edges,
        assignments=assignments,
        root_cell_id=root_cell_id,
        global_budget=global_budget,
        time_envelope_ref=source_binding.source_time_envelope_ref,
    )


def construct_runtime_execution_topology_v02(
    source_context: FractalRuntimeSourceContextV02,
) -> RuntimeExecutionTopologyV02:
    if validate_fractal_runtime_source_context_v02(source_context).status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    topology = _construct_runtime_execution_topology_from_source_v02(source_context)
    if validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    ).status != "PASS":
        raise ValueError("g2d_topology_identity_mismatch")
    return topology


def validate_runtime_execution_topology_against_sources_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
) -> FractalRuntimeValidationReportV02:
    try:
        context_pass = validate_fractal_runtime_source_context_v02(source_context).status == "PASS"
        structural_pass = validate_runtime_execution_topology_v02(value).status == "PASS"
        expected = _construct_runtime_execution_topology_from_source_v02(source_context) if context_pass else None
        valid = bool(
            context_pass
            and structural_pass
            and type(value) is RuntimeExecutionTopologyV02
            and value == expected
            and _canonical_json_bytes_v01(runtime_execution_topology_to_plain_data_v02(value))
            == _canonical_json_bytes_v01(runtime_execution_topology_to_plain_data_v02(expected))
        )
        return build_fractal_runtime_validation_report_v02(
            validation_target="TOPOLOGY_AGAINST_SOURCES",
            validated_object_id=value.topology_id if valid else None,
            failure_stage="NONE" if valid else "TOPOLOGY",
            reason_codes=() if valid else ("g2d_topology_identity_mismatch",),
            source_reason_codes=(),
        )
    except Exception:
        return build_fractal_runtime_validation_report_v02(
            validation_target="TOPOLOGY_AGAINST_SOURCES",
            validated_object_id=None,
            failure_stage="TOPOLOGY",
            reason_codes=("g2d_topology_identity_mismatch",),
            source_reason_codes=(),
        )


def _topology_payload_v02(topology: RuntimeExecutionTopologyV02) -> dict[str, object]:
    return {
        "topology_id": topology.topology_id,
        "topology_version": topology.topology_version,
        "topology_seed_id": topology.topology_seed_id,
        "request_id": topology.request_id,
        "domain_id": topology.domain_id,
        "accepted_mode": topology.accepted_mode,
        "accepted_scope_ref": topology.accepted_scope_ref,
        "source_binding_id": topology.source_binding_id,
        "source_root_decision_artifact_id": topology.source_root_decision_artifact_id,
        "source_proposal_artifact_id": topology.source_proposal_artifact_id,
        "runtime_policy_id": topology.runtime_policy_id,
        "ordered_node_ids": list(topology.ordered_node_ids),
        "ordered_edge_ids": list(topology.ordered_edge_ids),
        "ordered_assignment_ids": list(topology.ordered_assignment_ids),
        "root_cell_id": topology.root_cell_id,
        "global_budget_id": topology.global_budget_id,
        "root_review_required": topology.root_review_required,
        "authority_created": topology.authority_created,
        "permission_created": topology.permission_created,
        "action_commit_packet_created": topology.action_commit_packet_created,
        "receipt_created": topology.receipt_created,
        "final_output_created": topology.final_output_created,
        "drs_write_created": topology.drs_write_created,
        "provider_calls": topology.provider_calls,
        "network_calls": topology.network_calls,
        "real_world_effects_count": topology.real_world_effects_count,
    }


def _build_topology_artifact_v02(
    topology: RuntimeExecutionTopologyV02,
    source_context: FractalRuntimeSourceContextV02,
) -> KernelArtifactV01:
    route_plain = _kernel_artifact_to_plain_dict_v01(source_context.route_eligibility_artifact)
    provisional = _build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id="frabi_topology_v02:" + _ZERO_SHA256,
        artifact_type="RuntimeExecutionTopology",
        schema_version="v0.2",
        transaction_id=topology.transaction_id,
        owner_root_id=topology.owning_root_id,
        source_component="fractal_runtime_v02",
        authority_class="ADVISORY",
        lifecycle_state="VALIDATED",
        payload=_topology_payload_v02(topology),
        trace_refs=topology.trace_refs,
        parent_refs=(source_context.route_eligibility_artifact.artifact_id,),
        time_envelope=route_plain["time_envelope"],
    )
    material = _kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    artifact_id = "frabi_topology_v02:" + _domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_TOPOLOGY_KERNEL_ARTIFACT_V02",
        payload=_canonical_json_bytes_v01(material),
    )
    result = _replace(provisional, artifact_id=artifact_id)
    if _validate_kernel_artifact_v01(result):
        raise ValueError("g2d_abi_projection_substituted")
    return result


def project_runtime_execution_topology_kernel_artifact_v02(
    topology: RuntimeExecutionTopologyV02,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology_transition_decision: TransitionDecisionV01,
) -> KernelArtifactV01:
    if validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    ).status != "PASS":
        raise ValueError("g2d_abi_projection_substituted")
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    expected_decision = evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source_context,
        topology=topology,
        transition_registry=registry,
    )
    if topology_transition_decision != expected_decision:
        raise ValueError("g2d_transition_decision_substituted")
    artifact = _build_topology_artifact_v02(topology, source_context)
    if _validate_fractal_runtime_transition_decision_v02(
        topology_transition_decision,
        registry=registry,
        source_artifact=source_context.route_eligibility_artifact,
        target_artifact=artifact,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    return artifact


def evaluate_route_eligibility_to_topology_transition_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    transition_registry: TransitionRegistryV01,
) -> TransitionDecisionV01:
    if validate_fractal_runtime_source_context_v02(source_context).status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    if validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    ).status != "PASS":
        raise ValueError("g2d_topology_identity_mismatch")
    expected_registry = _build_fractal_runtime_transition_registry_profile_v02()
    if (
        _validate_fractal_runtime_transition_registry_profile_v02(transition_registry)
        or transition_registry != expected_registry
    ):
        raise ValueError("g2d_transition_profile_invalid")
    if source_context.root_decision_result.root_commit_created is not True:
        raise ValueError("g2d_g2c_root_result_invalid")
    rule = transition_registry.rules[0]
    provisional = TransitionDecisionV01(
        decision_id=_ZERO_SHA256,
        registry_id=transition_registry.registry_id,
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
        root_commit_present=True,
        matched=True,
    )
    return _replace(
        provisional,
        decision_id=_rebuild_fractal_runtime_transition_decision_identity_v02(provisional),
    )


def _derive_settled_planned_root_child_ids_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_transition_decision: TransitionDecisionV01,
    topology_artifact: KernelArtifactV01,
) -> tuple[str, ...]:
    if validate_fractal_runtime_source_context_v02(source_context).status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    if validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    ).status != "PASS":
        raise ValueError("g2d_topology_identity_mismatch")
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    expected_decision = evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source_context,
        topology=topology,
        transition_registry=registry,
    )
    if topology_transition_decision != expected_decision:
        raise ValueError("g2d_transition_decision_substituted")
    expected_artifact = project_runtime_execution_topology_kernel_artifact_v02(
        topology,
        source_context=source_context,
        topology_transition_decision=topology_transition_decision,
    )
    if topology_artifact != expected_artifact:
        raise ValueError("g2d_abi_projection_substituted")
    if topology.accepted_mode != "full_fractal":
        return ()
    if CHILD_SLOT_INDEX_ROWS_V02 != (
        (1, "PREDECESSOR_AND_CHILD_SLOT_1", 1, 0, 0),
        (2, "PREDECESSOR_AND_CHILD_SLOT_2", 2, 1, 1),
    ):
        raise ValueError("g2d_child_cell_identity_invalid")
    selected_profile_id = source_context.proposal.selected_local_mode_profile_id
    if type(selected_profile_id) is not str:
        raise ValueError("g2d_child_cell_identity_invalid")
    result = tuple(
        derive_fractal_child_cell_id_v02(
            topology_seed_id=topology.topology_seed_id,
            parent_cell_id=topology.root_cell_id,
            canonical_child_index=row[4],
            accepted_mode=topology.accepted_mode,
            selected_local_mode_profile_id=selected_profile_id,
            source_mode_profile_set_id=(
                source_context.router_input.local_routing_snapshot.mode_profile_set_id
            ),
            child_scope_ref=topology.accepted_scope_ref,
            runtime_policy_id=topology.runtime_policy_id,
            required_capability_ids=(
                source_context.proposal.required_downstream_capability_ids
            ),
            forbidden_claims=source_context.runtime_policy.forbidden_claims,
            child_depth=1,
        )
        for row in CHILD_SLOT_INDEX_ROWS_V02
    )
    if len(result) != 2 or len(set(result)) != 2:
        raise ValueError("g2d_child_cell_identity_invalid")
    return result


_D3_QUEUE_PAYLOAD_FIELDS_V02 = (
    "queue_entry_id",
    "topology_seed_id",
    "cell_id",
    "parent_cell_id",
    "node_id",
    "planned_child_cell_id",
    "cell_depth",
    "scope_ref",
    "cell_budget_id",
    "global_budget_id",
    "state",
    "prior_state",
    "predecessor_relation",
    "canonical_priority",
    "node_instance_sequence",
    "snapshot_sequence",
    "admission_round",
    "queue_reason_codes",
    "observed_output_refs",
    "observed_evidence_refs",
    "advisory_refs",
    "root_review_required",
    "authority_created",
    "permission_created",
    "final_output_created",
    "drs_write_created",
    "real_world_effects_count",
)
_D3_QUEUE_CONTEXT_ONLY_FIELDS_V02 = ("topology_id", "predecessor_queue_entry_id")
_D3_TERMINAL_STATES_V02 = frozenset(NODE_TERMINAL_OUTCOMES)
_D3_RULE_BY_STATE_PAIR_V02 = {
    (None, "PENDING"): "t02",
    ("PENDING", "PENDING"): "t03",
    ("PENDING", "READY"): "t04",
    ("READY", "RUNNING"): "t05",
    ("RUNNING", "VALIDATING"): "t06",
    ("VALIDATING", "READY"): "t07",
    ("VALIDATING", "COMPLETED"): "t08",
    ("VALIDATING", "DEGRADED"): "t09",
    ("VALIDATING", "BLOCKED"): "t10",
    ("VALIDATING", "NEEDS_USER"): "t11",
    ("VALIDATING", "DEADEND"): "t12",
}
_D3_TERMINAL_REASON_ROWS_V02 = (
    ("COMPLETED", ()),
    ("DEGRADED", ("g2d_partial_failure_recorded",)),
    ("BLOCKED", ("g2d_required_child_failure",)),
    ("NEEDS_USER", ("g2d_resolvable_input_needs_user",)),
    ("DEADEND", ("g2d_no_progress_deadend",)),
)
_D3_STATE_CLASS_ORDER_V02 = (
    "READY",
    "RUNNING",
    "VALIDATING_TERMINAL",
    "VALIDATING_REVISE",
    "PENDING_READY",
    "PENDING_DEFERRED",
)


def _d3_reconstruct_topology_parts_v02(
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
) -> tuple[
    RuntimeTopologySourceBindingV02,
    RuntimeTopologySeedV02,
    FractalRuntimeBudgetV02,
    tuple[RuntimeTopologyNodeV02, ...],
]:
    if validate_fractal_runtime_source_context_v02(source_context).status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    if validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    ).status != "PASS":
        raise ValueError("g2d_topology_identity_mismatch")
    source_binding = build_runtime_topology_source_binding_v02(source_context=source_context)
    policy = source_context.runtime_policy
    root_cell_id = derive_fractal_root_cell_id_v02(
        source_binding_id=source_binding.source_binding_id,
        runtime_policy_id=policy.policy_id,
        accepted_mode=source_binding.accepted_mode,
        accepted_scope_ref=source_binding.accepted_scope_ref,
    )
    seed = build_runtime_topology_seed_v02(source_binding, policy, root_cell_id=root_cell_id)
    initial_budget = build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=None,
        owning_cell_id=root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=None,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    rows = dict(MODE_NODE_TEMPLATE_ROWS_V02)[topology.accepted_mode]
    nodes = tuple(
        build_runtime_topology_node_v02(
            seed,
            source_binding,
            policy,
            canonical_index=row[0],
            node_kind=row[1],
            depth=0,
            scope_ref=source_binding.accepted_scope_ref,
            cell_binding_class=row[2],
            scope_binding_class=row[3],
            budget_binding_class=row[4],
            required_capability_ids=(
                source_binding.required_downstream_capability_ids
                if row[5] == ("SRC_CAPS",)
                else row[5]
            ),
            input_ref_derivation_class=row[8],
        )
        for row in rows
    )
    if tuple(item.node_id for item in nodes) != topology.ordered_node_ids:
        raise ValueError("g2d_topology_node_invalid")
    if initial_budget.budget_id != topology.global_budget_id:
        raise ValueError("g2d_global_budget_binding_missing")
    return source_binding, seed, initial_budget, nodes


def _d3_projected_nodes_v02(
    topology: RuntimeExecutionTopologyV02,
    nodes: tuple[RuntimeTopologyNodeV02, ...],
    *,
    cell_depth: int,
    parent_cell_id: str | None,
) -> tuple[RuntimeTopologyNodeV02, ...]:
    if type(cell_depth) is not int or not 0 <= cell_depth < 3:
        raise ValueError("g2d_depth_limit_exceeded")
    if cell_depth == 0:
        if parent_cell_id is not None:
            raise ValueError("g2d_child_lineage_mismatch")
        row = next(
            item
            for item in CELL_NODE_PROJECTION_ROWS_V02
            if item[0] == topology.accepted_mode and item[1] == "ROOT"
        )
    else:
        if parent_cell_id is None or topology.accepted_mode != "full_fractal":
            raise ValueError("g2d_non_fractal_recursion_forbidden")
        projection = "STRUCTURAL_DEPTH_2_LEAF" if cell_depth == 2 else "REFERENCE_CHILD_SLOT_1"
        row = next(
            item
            for item in CELL_NODE_PROJECTION_ROWS_V02
            if item[0] == "full_fractal" and item[1] == projection
        )
    return tuple(nodes[index] for index in row[3])


def _d3_root_cell_create_budget_v02(
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
) -> FractalRuntimeBudgetV02:
    _binding, seed, initial, _nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    active = build_fractal_runtime_budget_v02(
        policy=source_context.runtime_policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=initial,
        owning_cell_id=topology.root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="ACTIVE",
        budget_event_kind="ACTIVATE",
        budget_context_input=None,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    return build_fractal_runtime_budget_v02(
        policy=source_context.runtime_policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=active,
        owning_cell_id=topology.root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="ACTIVE",
        budget_event_kind="CELL_CREATE",
        budget_context_input=None,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )


def _d3_transition_decision_v02(
    registry: TransitionRegistryV01,
    short_rule_id: str,
) -> TransitionDecisionV01:
    expected_registry = _build_fractal_runtime_transition_registry_profile_v02()
    if (
        _validate_fractal_runtime_transition_registry_profile_v02(registry)
        or registry != expected_registry
    ):
        raise ValueError("g2d_transition_profile_invalid")
    try:
        rule = next(
            item
            for item in registry.rules
            if re.search(
                r"(?:^|_)t(0[2-9]|1[0-2])(?:_|$)",
                item.rule_id,
            )
            and "t" + re.search(
                r"(?:^|_)t(0[2-9]|1[0-2])(?:_|$)",
                item.rule_id,
            ).group(1)
            == short_rule_id
        )
    except StopIteration:
        raise ValueError("g2d_queue_transition_unknown") from None
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
        root_commit_required=True,
        root_commit_present=True,
        matched=True,
    )
    return _replace(
        provisional,
        decision_id=_rebuild_fractal_runtime_transition_decision_identity_v02(provisional),
    )


def _d3_queue_rule_id_v02(value: FractalCellQueueEntryV02) -> str:
    try:
        return _D3_RULE_BY_STATE_PAIR_V02[(value.prior_state, value.state)]
    except KeyError:
        raise ValueError("g2d_queue_transition_illegal") from None


def _d3_queue_payload_v02(value: FractalCellQueueEntryV02) -> dict[str, object]:
    payload: dict[str, object] = {}
    for field_name in _D3_QUEUE_PAYLOAD_FIELDS_V02:
        item = getattr(value, field_name)
        payload[field_name] = list(item) if type(item) is tuple else item
    if any(field_name in payload for field_name in _D3_QUEUE_CONTEXT_ONLY_FIELDS_V02):
        raise ValueError("g2d_abi_field_partition_invalid")
    return payload


def _d3_queue_artifact_trace_refs_with_exact_omission_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    parent_refs: tuple[str, ...],
    profile_d_omission_index: int | None,
) -> tuple[str, ...]:
    if (
        validate_fractal_cell_queue_entry_v02(queue_entry).status != "PASS"
        or type(parent_refs) is not tuple
        or not parent_refs
        or any(type(item) is not str or not item for item in parent_refs)
        or any(item in parent_refs[:index] for index, item in enumerate(parent_refs))
        or not _identity_pattern_valid(parent_refs[0], "frabi_topology_v02:")
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    root_entry = queue_entry.parent_cell_id is None
    initial_entry = queue_entry.predecessor_queue_entry_id is None
    invoked_child = len(parent_refs) == 3
    if initial_entry:
        expected_parent_count = 1 if root_entry else 2
        if len(parent_refs) != expected_parent_count or invoked_child:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
    elif len(parent_refs) not in {2, 3}:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if len(parent_refs) >= 2 and not _identity_pattern_valid(
        parent_refs[1],
        "frabi_queue_v02:",
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")

    if root_entry:
        base = (
            queue_entry.topology_id,
            queue_entry.topology_seed_id,
            queue_entry.cell_id,
            queue_entry.node_id,
            queue_entry.cell_budget_id,
            queue_entry.global_budget_id,
        )
        if queue_entry.cell_budget_id != queue_entry.global_budget_id:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        budget_alias_index = 5
    else:
        if queue_entry.cell_budget_id == queue_entry.global_budget_id:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        base = (
            queue_entry.topology_id,
            queue_entry.topology_seed_id,
            queue_entry.cell_id,
            queue_entry.parent_cell_id,
            queue_entry.node_id,
            queue_entry.cell_budget_id,
            queue_entry.global_budget_id,
        )
        budget_alias_index = None
        if initial_entry:
            base += (parent_refs[1],)
        else:
            if len(queue_entry.lineage_refs) < 8:
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            base += (queue_entry.lineage_refs[7],)

    if not initial_entry:
        base += (queue_entry.predecessor_queue_entry_id,)
    result_output_alias_index: int | None = None
    if invoked_child:
        result_artifact_id = parent_refs[2]
        if (
            not _identity_pattern_valid(result_artifact_id, "frabi_result_v02:")
            or queue_entry.planned_child_cell_id is None
            or (queue_entry.prior_state, queue_entry.state)
            not in {
                ("RUNNING", "VALIDATING"),
                ("VALIDATING", "COMPLETED"),
                ("VALIDATING", "DEGRADED"),
                ("VALIDATING", "BLOCKED"),
                ("VALIDATING", "NEEDS_USER"),
                ("VALIDATING", "DEADEND"),
            }
            or queue_entry.observed_output_refs != (result_artifact_id,)
        ):
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        base += (result_artifact_id,)
        result_output_alias_index = len(base)

    expected_lineage = (
        *base,
        *queue_entry.observed_output_refs,
        *queue_entry.observed_evidence_refs,
        *queue_entry.advisory_refs,
    )
    if queue_entry.lineage_refs != expected_lineage:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if budget_alias_index is not None and queue_entry.lineage_refs.count(
        queue_entry.cell_budget_id
    ) != 2:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if invoked_child and queue_entry.lineage_refs.count(parent_refs[2]) != 2:
        raise ValueError("g2d_queue_artifact_lineage_invalid")

    if profile_d_omission_index is not None:
        if (
            type(profile_d_omission_index) is not int
            or queue_entry.parent_cell_id is None
            or queue_entry.predecessor_queue_entry_id is None
            or profile_d_omission_index < 0
            or profile_d_omission_index >= len(queue_entry.lineage_refs)
            or queue_entry.lineage_refs[profile_d_omission_index]
            != queue_entry.lineage_refs[7]
        ):
            raise ValueError("g2d_queue_artifact_lineage_invalid")

    projected_lineage = tuple(
        item
        for index, item in enumerate(queue_entry.lineage_refs)
        if (
            index != budget_alias_index
            and index != result_output_alias_index
            and index != profile_d_omission_index
        )
    )
    result = (queue_entry.transition_decision_id, *projected_lineage)
    if (
        any(type(item) is not str or not item for item in result)
        or any(item in result[:index] for index, item in enumerate(result))
        or result[0] != queue_entry.transition_decision_id
        or len(result) < 2
        or result[1] != queue_entry.topology_id
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    return result


def _d3_queue_artifact_trace_refs_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    parent_refs: tuple[str, ...],
) -> tuple[str, ...]:
    return _d3_queue_artifact_trace_refs_with_exact_omission_v02(
        queue_entry,
        parent_refs=parent_refs,
        profile_d_omission_index=None,
    )


def _d3_build_queue_artifact_with_exact_omission_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    parent_refs: tuple[str, ...],
    source_context: FractalRuntimeSourceContextV02,
    profile_d_omission_index: int | None,
) -> KernelArtifactV01:
    route_plain = _kernel_artifact_to_plain_dict_v01(source_context.route_eligibility_artifact)
    provisional = _build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id="frabi_queue_v02:" + _ZERO_SHA256,
        artifact_type="FractalCellQueueEntry",
        schema_version="v0.2",
        transaction_id=source_context.decision.transaction_id,
        owner_root_id=source_context.decision.owning_root_id,
        source_component="fractal_scheduler_v02",
        authority_class="ADVISORY",
        lifecycle_state="VALIDATED",
        payload=_d3_queue_payload_v02(queue_entry),
        trace_refs=_d3_queue_artifact_trace_refs_with_exact_omission_v02(
            queue_entry,
            parent_refs=parent_refs,
            profile_d_omission_index=profile_d_omission_index,
        ),
        parent_refs=parent_refs,
        time_envelope=route_plain["time_envelope"],
    )
    material = _kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    artifact_id = "frabi_queue_v02:" + _domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02",
        payload=_canonical_json_bytes_v01(material),
    )
    result = _replace(provisional, artifact_id=artifact_id)
    if _validate_kernel_artifact_v01(result):
        raise ValueError("g2d_abi_projection_substituted")
    return result


def _d3_build_queue_artifact_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    parent_refs: tuple[str, ...],
    source_context: FractalRuntimeSourceContextV02,
) -> KernelArtifactV01:
    return _d3_build_queue_artifact_with_exact_omission_v02(
        queue_entry,
        parent_refs=parent_refs,
        source_context=source_context,
        profile_d_omission_index=None,
    )


def _d3_queue_artifact_matches_entry_with_exact_omission_v02(
    artifact: KernelArtifactV01,
    entry: FractalCellQueueEntryV02,
    source_context: FractalRuntimeSourceContextV02,
    *,
    profile_d_omission_index: int | None,
) -> bool:
    try:
        plain = _kernel_artifact_to_plain_dict_v01(artifact)
        payload = plain.get("payload")
        return bool(
            type(artifact) is KernelArtifactV01
            and not _validate_kernel_artifact_v01(artifact)
            and type(payload) is dict
            and artifact.artifact_type == "FractalCellQueueEntry"
            and artifact.trace_refs
            == _d3_queue_artifact_trace_refs_with_exact_omission_v02(
                entry,
                parent_refs=artifact.parent_refs,
                profile_d_omission_index=profile_d_omission_index,
            )
            and artifact == _d3_build_queue_artifact_with_exact_omission_v02(
                entry,
                parent_refs=artifact.parent_refs,
                source_context=source_context,
                profile_d_omission_index=profile_d_omission_index,
            )
            and all(
                key not in payload
                for key in _D3_QUEUE_CONTEXT_ONLY_FIELDS_V02
            )
        )
    except Exception:
        return False


def _d3_queue_artifact_matches_entry_v02(
    artifact: KernelArtifactV01,
    entry: FractalCellQueueEntryV02,
    source_context: FractalRuntimeSourceContextV02,
) -> bool:
    return _d3_queue_artifact_matches_entry_with_exact_omission_v02(
        artifact,
        entry,
        source_context,
        profile_d_omission_index=None,
    )

def _d3_queue_artifact_payload_ref_v02(
    artifact: KernelArtifactV01,
    key: str,
) -> object:
    try:
        payload = _kernel_artifact_to_plain_dict_v01(artifact)["payload"]
    except Exception:
        raise ValueError("g2d_queue_artifact_lineage_invalid") from None
    if type(payload) is not dict or key not in payload:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    return payload[key]


def _d3_validate_parent_slot_artifact_v02(
    artifact: KernelArtifactV01,
    *,
    topology: RuntimeExecutionTopologyV02,
    parent_cell_id: str,
    child_cell_id: str,
) -> None:
    if (
        type(artifact) is not KernelArtifactV01
        or _validate_kernel_artifact_v01(artifact)
        or artifact.artifact_type != "FractalCellQueueEntry"
        or artifact.lifecycle_state != "VALIDATED"
        or type(artifact.trace_refs) is not tuple
        or len(artifact.trace_refs) < 2
        or artifact.trace_refs[1] != topology.topology_id
        or _d3_queue_artifact_payload_ref_v02(artifact, "state") != "RUNNING"
        or _d3_queue_artifact_payload_ref_v02(artifact, "cell_id") != parent_cell_id
        or _d3_queue_artifact_payload_ref_v02(artifact, "planned_child_cell_id") != child_cell_id
    ):
        raise ValueError("g2d_child_slot_activation_invalid")


def _d3_planned_child_ids_from_sources_v02(
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
) -> tuple[str, ...]:
    if topology.accepted_mode != "full_fractal":
        return ()
    profile_id = source_context.proposal.selected_local_mode_profile_id
    if type(profile_id) is not str:
        raise ValueError("g2d_child_cell_identity_invalid")
    result = tuple(
        derive_fractal_child_cell_id_v02(
            topology_seed_id=topology.topology_seed_id,
            parent_cell_id=topology.root_cell_id,
            canonical_child_index=index,
            accepted_mode=topology.accepted_mode,
            selected_local_mode_profile_id=profile_id,
            source_mode_profile_set_id=(
                source_context.router_input.local_routing_snapshot.mode_profile_set_id
            ),
            child_scope_ref=topology.accepted_scope_ref,
            runtime_policy_id=topology.runtime_policy_id,
            required_capability_ids=source_context.proposal.required_downstream_capability_ids,
            forbidden_claims=source_context.runtime_policy.forbidden_claims,
            child_depth=1,
        )
        for index in (0, 1)
    )
    if len(set(result)) != 2:
        raise ValueError("g2d_child_cell_identity_invalid")
    return result


def _d3_queue_dependency_ids_v02(
    topology: RuntimeExecutionTopologyV02,
    node: RuntimeTopologyNodeV02,
    *,
    cell_depth: int,
) -> tuple[str, ...]:
    projection = "ROOT_CELL_PROJECTION" if cell_depth == 0 else "FRACTAL_LEAF_PROJECTION"
    rows = tuple(
        row
        for row in dict(MODE_EDGE_TEMPLATE_ROWS_V02)[topology.accepted_mode]
        if row[1] == projection and row[3] == node.canonical_index
    )
    return tuple(topology.ordered_node_ids[row[2]] for row in rows)


def _d3_dependencies_satisfied_v02(
    topology: RuntimeExecutionTopologyV02,
    node: RuntimeTopologyNodeV02,
    *,
    cell_id: str,
    cell_depth: int,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
) -> bool:
    if type(dependencies) is not tuple or any(
        type(item) is not FractalCellQueueEntryV02 for item in dependencies
    ):
        raise ValueError("g2d_queue_order_mismatch")
    expected_ids = _d3_queue_dependency_ids_v02(topology, node, cell_depth=cell_depth)
    if tuple(item.node_id for item in dependencies) != expected_ids:
        return False
    return all(
        validate_fractal_cell_queue_entry_v02(item).status == "PASS"
        and item.topology_id == topology.topology_id
        and item.cell_id == cell_id
        and item.state in _D3_TERMINAL_STATES_V02
        for item in dependencies
    )


def _d3_parent_return_family_empty_v02(
    *,
    terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    child_results: tuple[FractalCellResultV02, ...],
    partial_failures: tuple[FractalPartialFailureRecordV02, ...],
    result_proposal: dict[str, object] | None,
    post_vv_report: dict[str, object] | None,
    gt_advisory_report: dict[str, object] | None,
    validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> bool:
    tuple_families = (
        (terminal_queue_entries, FractalCellQueueEntryV02),
        (child_results, FractalCellResultV02),
        (partial_failures, FractalPartialFailureRecordV02),
        (validation_reports, FractalRuntimeValidationReportV02),
    )
    if any(
        type(values) is not tuple
        or any(type(item) is not expected for item in values)
        for values, expected in tuple_families
    ):
        raise ValueError("g2d_parent_return_invalid")
    for value in (result_proposal, post_vv_report, gt_advisory_report):
        if value is not None and type(value) is not dict:
            raise ValueError("g2d_parent_return_invalid")
    return bool(
        terminal_queue_entries == ()
        and child_results == ()
        and partial_failures == ()
        and result_proposal is None
        and post_vv_report is None
        and gt_advisory_report is None
        and validation_reports == ()
    )


_D3_SETTLED_PREFIX_ARGUMENT_NAMES_V02 = (
    "settled_budget_log",
    "settled_queue_entry_log",
    "settled_queue_artifact_log",
    "settled_cell_inputs",
    "settled_scope_projections",
    "settled_revise_observations",
    "settled_backpressure_states",
    "settled_validation_reports",
)
_D3_LOCAL_NODE_KINDS_V02 = frozenset(
    {
        "MEMORY_CONTEXT",
        "LOCAL_MODEL_DECLARATION",
        "CLOUD_MODEL_DECLARATION",
        "SEMANTIC_ACTOR",
        "SEMANTIC_MERGE",
        "FRACTAL_MERGE",
    }
)


def _d3_expected_retained_base_reports_v02(
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
) -> tuple[FractalRuntimeValidationReportV02, ...]:
    source_report = validate_fractal_runtime_source_context_v02(source_context)
    if source_report.status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    binding = build_runtime_topology_source_binding_v02(
        source_context=source_context,
    )
    binding_report = validate_runtime_topology_source_binding_against_g2c_v02(
        binding,
        source_context=source_context,
    )
    root_cell_id = derive_fractal_root_cell_id_v02(
        source_binding_id=binding.source_binding_id,
        runtime_policy_id=source_context.runtime_policy.policy_id,
        accepted_mode=binding.accepted_mode,
        accepted_scope_ref=binding.accepted_scope_ref,
    )
    seed = build_runtime_topology_seed_v02(
        binding,
        source_context.runtime_policy,
        root_cell_id=root_cell_id,
    )
    seed_report = validate_runtime_topology_seed_v02(seed)
    topology_report = validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source_context,
    )
    reports = (source_report, binding_report, seed_report, topology_report)
    if any(report.status != "PASS" for report in reports):
        raise ValueError("g2d_validation_target_id_mismatch")
    return reports


def _d3_validation_reports_equal_v02(
    actual: FractalRuntimeValidationReportV02,
    expected: FractalRuntimeValidationReportV02,
) -> bool:
    return bool(
        actual == expected
        and _canonical_json_bytes_v01(
            fractal_runtime_validation_report_to_plain_data_v02(actual)
        )
        == _canonical_json_bytes_v01(
            fractal_runtime_validation_report_to_plain_data_v02(expected)
        )
    )


def _d3_budget_counter_tuple_v02(
    value: FractalRuntimeBudgetV02,
) -> tuple[int, ...]:
    return (
        value.max_depth,
        value.max_fan_out,
        value.max_total_cells,
        value.max_parallelism,
        value.max_revise_count,
        value.max_wall_time_units,
        value.max_token_budget,
        value.max_provider_calls,
        value.consumed_wall_time_units,
        value.consumed_token_budget,
        value.consumed_provider_calls,
        value.consumed_cell_count,
        value.consumed_revise_count,
        value.current_parallelism,
        value.remaining_wall_time_units,
        value.remaining_token_budget,
        value.remaining_provider_calls,
        value.remaining_cell_count,
        value.remaining_revise_count,
        value.remaining_parallel_slots,
    )


def _d3_budget_axis_v02(
    value: FractalRuntimeBudgetV02,
) -> tuple[str, str]:
    return (value.budget_scope, value.owning_cell_id)


def _d3_budget_is_ancestor_v02(
    anchor: FractalRuntimeBudgetV02,
    head: FractalRuntimeBudgetV02,
    *,
    budget_by_id: dict[str, FractalRuntimeBudgetV02],
) -> bool:
    if _d3_budget_axis_v02(anchor) != _d3_budget_axis_v02(head):
        return False
    cursor: FractalRuntimeBudgetV02 | None = head
    seen: set[str] = set()
    while cursor is not None:
        if cursor == anchor:
            return True
        if cursor.budget_id in seen:
            return False
        seen.add(cursor.budget_id)
        cursor = (
            None
            if cursor.predecessor_budget_id is None
            else budget_by_id.get(cursor.predecessor_budget_id)
        )
    return False


def _d3_validate_budget_log_v02(
    budgets: tuple[FractalRuntimeBudgetV02, ...],
    *,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    source_context: FractalRuntimeSourceContextV02 | None,
) -> dict[str, object]:
    if type(budgets) is not tuple or not budgets:
        raise ValueError("g2d_budget_predecessor_invalid")
    by_id: dict[str, FractalRuntimeBudgetV02] = {}
    position_by_id: dict[str, int] = {}
    axis_by_id: dict[str, tuple[str, str]] = {}
    successor_by_id: dict[str, str] = {}
    live_head_by_axis: dict[tuple[str, str], FractalRuntimeBudgetV02] = {}
    for index, budget in enumerate(budgets):
        if (
            type(budget) is not FractalRuntimeBudgetV02
            or validate_fractal_runtime_budget_v02(budget).status != "PASS"
            or budget.policy_id != policy.policy_id
            or budget.topology_seed_id != topology.topology_seed_id
            or budget.budget_id in by_id
        ):
            raise ValueError("g2d_budget_invalid")
        axis = _d3_budget_axis_v02(budget)
        predecessor = None
        if budget.predecessor_budget_id is not None:
            predecessor = by_id.get(budget.predecessor_budget_id)
            if predecessor is None:
                raise ValueError("g2d_budget_predecessor_invalid")
        if budget.allocation_parent_budget_id is not None and (
            budget.allocation_parent_budget_id not in by_id
            or by_id[budget.allocation_parent_budget_id].budget_event_kind != "CELL_CREATE"
        ):
            raise ValueError("g2d_budget_predecessor_invalid")
        if index == 0:
            if (
                budget.owning_cell_id != topology.root_cell_id
                or budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
                or budget.budget_state != "ALLOCATED"
                or budget.budget_event_kind != "INITIAL_ALLOCATION"
                or budget.predecessor_budget_id is not None
                or budget.allocation_parent_budget_id is not None
            ):
                raise ValueError("g2d_budget_event_context_invalid")
        elif predecessor is None:
            if (
                budget.budget_event_kind != "INITIAL_ALLOCATION"
                or budget.budget_scope != "CHILD_CELL_LOCAL"
                or budget.owning_cell_id == topology.root_cell_id
                or budget.budget_state != "ALLOCATED"
                or axis in live_head_by_axis
                or budget.budget_event_ref != budget.owning_cell_id
            ):
                raise ValueError("g2d_budget_predecessor_invalid")
        if predecessor is not None:
            if (
                predecessor.budget_state == "FINAL"
                or predecessor.owning_cell_id != budget.owning_cell_id
                or predecessor.budget_scope != budget.budget_scope
                or live_head_by_axis.get(axis) != predecessor
                or predecessor.budget_id in successor_by_id
            ):
                raise ValueError("g2d_budget_predecessor_invalid")
            expected = list(_d3_budget_counter_tuple_v02(predecessor))
            if budget.budget_event_kind == "CELL_CREATE":
                expected[11] += 1
                expected[17] -= 1
            elif budget.budget_event_kind == "START_NODE":
                expected[8] += 1
                expected[14] -= 1
                if budget.budget_scope == "ROOT_GLOBAL_AND_CELL":
                    expected[13] += 1
                    expected[19] -= 1
            elif budget.budget_event_kind == "FINISH_NODE":
                if budget.budget_scope == "ROOT_GLOBAL_AND_CELL":
                    expected[13] -= 1
                    expected[19] += 1
            elif budget.budget_event_kind == "REVISE":
                expected[8] += 1
                expected[12] += 1
                expected[14] -= 1
                expected[18] -= 1
            if any(item < 0 for item in expected) or tuple(expected) != _d3_budget_counter_tuple_v02(budget):
                raise ValueError("g2d_budget_event_pair_mismatch")
            if budget.budget_event_kind == "ACTIVATE" and (
                budget.budget_state != "ACTIVE"
                or budget.consumed_cell_count != predecessor.consumed_cell_count
            ):
                raise ValueError("g2d_budget_state_transition_invalid")
            if budget.budget_event_kind == "CELL_CREATE" and budget.budget_state != "ACTIVE":
                raise ValueError("g2d_budget_state_transition_invalid")
            if budget.budget_event_kind in {"START_NODE", "FINISH_NODE", "REVISE"} and budget.budget_state != "ACTIVE":
                raise ValueError("g2d_budget_state_transition_invalid")
            rule_for_event = {
                "START_NODE": "t05",
                "FINISH_NODE": "t06",
                "REVISE": "t07",
            }.get(budget.budget_event_kind)
            if rule_for_event is not None and budget.budget_event_ref != (
                _d3_transition_decision_v02(
                    _build_fractal_runtime_transition_registry_profile_v02(),
                    rule_for_event,
                ).decision_id
            ):
                raise ValueError("g2d_budget_event_context_invalid")
            if budget.budget_event_kind == "FINALIZE":
                expected_state = (
                    "FINAL"
                    if budget.budget_scope == "CHILD_CELL_LOCAL"
                    or budget.owning_cell_id == topology.root_cell_id
                    and not any(
                        item.budget_scope == "CHILD_CELL_LOCAL"
                        and item.budget_event_ref == budget.budget_event_ref
                        and item.budget_event_kind == "FINALIZE"
                        for item in budgets[:index]
                    )
                    else "ACTIVE"
                )
                if budget.budget_state != expected_state:
                    raise ValueError("g2d_budget_state_transition_invalid")
            successor_by_id[predecessor.budget_id] = budget.budget_id
        by_id[budget.budget_id] = budget
        position_by_id[budget.budget_id] = index
        axis_by_id[budget.budget_id] = axis
        live_head_by_axis[axis] = budget

    paired_events = {
        "ACTIVATE",
        "CELL_CREATE",
        "START_NODE",
        "FINISH_NODE",
        "REVISE",
        "FINALIZE",
    }
    for index, budget in enumerate(budgets):
        if (
            budget.budget_scope == "CHILD_CELL_LOCAL"
            and budget.budget_event_kind in paired_events
        ):
            if index + 1 >= len(budgets):
                raise ValueError("g2d_budget_event_pair_mismatch")
            paired = budgets[index + 1]
            if (
                paired.budget_scope != "ROOT_GLOBAL_AND_CELL"
                or paired.owning_cell_id != topology.root_cell_id
                or paired.budget_event_kind != budget.budget_event_kind
                or paired.budget_event_ref != budget.budget_event_ref
            ):
                raise ValueError("g2d_budget_event_pair_mismatch")
        if budget.budget_event_kind == "CELL_CREATE":
            same_axis_creates = tuple(
                item
                for item in budgets[: index + 1]
                if _d3_budget_axis_v02(item) == _d3_budget_axis_v02(budget)
                and item.budget_event_kind == "CELL_CREATE"
                and item.budget_event_ref == budget.budget_event_ref
            )
            if len(same_axis_creates) != 1:
                raise ValueError("g2d_total_cell_limit_exceeded")
    expected_initial_counters = (
        policy.max_depth,
        policy.max_fan_out,
        policy.max_total_cells,
        policy.max_parallelism,
        policy.max_revise_count,
        policy.max_wall_time_units,
        policy.max_token_budget,
        policy.max_provider_calls,
        0,
        0,
        0,
        0,
        0,
        0,
        policy.max_wall_time_units,
        policy.max_token_budget,
        policy.max_provider_calls,
        policy.max_total_cells,
        policy.max_revise_count,
        policy.max_parallelism,
    )
    if _d3_budget_counter_tuple_v02(budgets[0]) != expected_initial_counters:
        raise ValueError("g2d_budget_predecessor_invalid")
    return {
        "budget_by_id": by_id,
        "budget_position_by_id": position_by_id,
        "budget_axis_by_id": axis_by_id,
        "budget_successor_by_id": successor_by_id,
        "live_head_by_axis": live_head_by_axis,
    }


def _d3_live_budget_heads_v02(
    *,
    topology: RuntimeExecutionTopologyV02,
    cell_id: str,
    indexes: dict[str, object],
) -> tuple[FractalRuntimeBudgetV02, FractalRuntimeBudgetV02]:
    live_head_by_axis = indexes.get("live_head_by_axis")
    if not isinstance(live_head_by_axis, dict):
        raise ValueError("g2d_budget_predecessor_invalid")
    global_head = live_head_by_axis.get(
        ("ROOT_GLOBAL_AND_CELL", topology.root_cell_id)
    )
    cell_head = (
        global_head
        if cell_id == topology.root_cell_id
        else live_head_by_axis.get(("CHILD_CELL_LOCAL", cell_id))
    )
    if (
        type(cell_head) is not FractalRuntimeBudgetV02
        or type(global_head) is not FractalRuntimeBudgetV02
        or (cell_id == topology.root_cell_id and cell_head is not global_head)
        or (cell_id != topology.root_cell_id and cell_head is global_head)
    ):
        raise ValueError("g2d_budget_predecessor_invalid")
    return cell_head, global_head


def _d3_validate_queue_budget_anchors_v02(
    entry: FractalCellQueueEntryV02,
    *,
    topology: RuntimeExecutionTopologyV02,
    indexes: dict[str, object],
) -> tuple[FractalRuntimeBudgetV02, FractalRuntimeBudgetV02]:
    budget_by_id = indexes.get("budget_by_id")
    if not isinstance(budget_by_id, dict):
        raise ValueError("g2d_budget_predecessor_invalid")
    cell_anchor = budget_by_id.get(entry.cell_budget_id)
    global_anchor = budget_by_id.get(entry.global_budget_id)
    cell_head, global_head = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=entry.cell_id,
        indexes=indexes,
    )
    if (
        type(cell_anchor) is not FractalRuntimeBudgetV02
        or type(global_anchor) is not FractalRuntimeBudgetV02
        or not _d3_budget_is_ancestor_v02(
            cell_anchor,
            cell_head,
            budget_by_id=budget_by_id,
        )
        or not _d3_budget_is_ancestor_v02(
            global_anchor,
            global_head,
            budget_by_id=budget_by_id,
        )
        or (entry.cell_id == topology.root_cell_id and cell_anchor != global_anchor)
        or (entry.cell_id != topology.root_cell_id and cell_anchor == global_anchor)
    ):
        raise ValueError("g2d_budget_predecessor_invalid")
    return cell_anchor, global_anchor


def _d3_validate_queue_advance_budget_frontier_v02(
    *,
    rule_id: str,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    source_context: FractalRuntimeSourceContextV02 | None,
    current_entry: FractalCellQueueEntryV02,
    cell_budget_after: FractalRuntimeBudgetV02,
    global_budget_after: FractalRuntimeBudgetV02,
    transition_decision: TransitionDecisionV01,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    indexes: dict[str, object],
) -> tuple[FractalRuntimeBudgetV02, FractalRuntimeBudgetV02]:
    budget_by_id = indexes.get("budget_by_id")
    if not isinstance(budget_by_id, dict):
        raise ValueError("g2d_budget_predecessor_invalid")
    cell_anchor, global_anchor = _d3_validate_queue_budget_anchors_v02(
        current_entry,
        topology=topology,
        indexes=indexes,
    )
    if rule_id in {"t03", "t04", "t08", "t09", "t10", "t11", "t12"}:
        if (
            cell_budget_after != cell_anchor
            or global_budget_after != global_anchor
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
        return _d3_live_budget_heads_v02(
            topology=topology,
            cell_id=current_entry.cell_id,
            indexes=indexes,
        )

    event_kind = {"t05": "START_NODE", "t06": "FINISH_NODE", "t07": "REVISE"}.get(
        rule_id
    )
    if event_kind is None:
        raise ValueError("g2d_queue_transition_unknown")
    if current_entry.cell_id == topology.root_cell_id:
        if (
            cell_budget_after is not global_budget_after
            or not settled_budget_log
            or settled_budget_log[-1] != global_budget_after
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
        suffix = (global_budget_after,)
    else:
        if (
            cell_budget_after is global_budget_after
            or len(settled_budget_log) < 2
            or settled_budget_log[-2:] != (cell_budget_after, global_budget_after)
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
        suffix = (cell_budget_after, global_budget_after)
    pre_log = settled_budget_log[: -len(suffix)]
    pre_indexes = _d3_validate_budget_log_v02(
        pre_log,
        topology=topology,
        policy=policy,
        source_context=source_context,
    )
    pre_cell_head, pre_global_head = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=current_entry.cell_id,
        indexes=pre_indexes,
    )
    if (
        not _d3_budget_is_ancestor_v02(
            cell_anchor,
            pre_cell_head,
            budget_by_id=pre_indexes["budget_by_id"],
        )
        or not _d3_budget_is_ancestor_v02(
            global_anchor,
            pre_global_head,
            budget_by_id=pre_indexes["budget_by_id"],
        )
        or cell_budget_after.budget_event_kind != event_kind
        or global_budget_after.budget_event_kind != event_kind
        or cell_budget_after.budget_event_ref != transition_decision.decision_id
        or global_budget_after.budget_event_ref != transition_decision.decision_id
        or cell_budget_after.predecessor_budget_id != pre_cell_head.budget_id
        or global_budget_after.predecessor_budget_id != pre_global_head.budget_id
    ):
        raise ValueError("g2d_budget_event_pair_mismatch")
    return pre_cell_head, pre_global_head


def _d3_t03_target_matches_source_v02(
    target: FractalCellQueueEntryV02,
    source: FractalCellQueueEntryV02,
    *,
    state: FractalBackpressureStateV02,
    expected_decision: TransitionDecisionV01,
) -> bool:
    preserved = (
        "topology_id",
        "topology_seed_id",
        "cell_id",
        "parent_cell_id",
        "node_id",
        "planned_child_cell_id",
        "cell_depth",
        "scope_ref",
        "cell_budget_id",
        "global_budget_id",
        "canonical_priority",
        "node_instance_sequence",
        "observed_output_refs",
        "observed_evidence_refs",
        "advisory_refs",
        "root_review_required",
        "authority_created",
        "permission_created",
        "final_output_created",
        "drs_write_created",
        "real_world_effects_count",
    )
    return bool(
        all(getattr(target, name) == getattr(source, name) for name in preserved)
        and target.state == "PENDING"
        and target.prior_state == "PENDING"
        and target.predecessor_queue_entry_id == source.queue_entry_id
        and target.predecessor_relation == "EXACT_IMMEDIATE_PREDECESSOR"
        and target.snapshot_sequence == source.snapshot_sequence + 1
        and target.admission_round == state.evaluated_round
        and target.queue_reason_codes
        == ("g2d_transition_backpressure_deferred",)
        and target.transition_decision_id == expected_decision.decision_id
    )


def _d3_backpressure_state_frontier_v02(
    *,
    state: FractalBackpressureStateV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_by_id: dict[str, FractalCellQueueEntryV02],
    allow_incomplete: bool,
) -> tuple[int, int]:
    expected_t03 = _d3_transition_decision_v02(
        _build_fractal_runtime_transition_registry_profile_v02(),
        "t03",
    )
    positions: list[int] = []
    missing_seen = False
    for source_id in state.deferred_queue_entry_ids:
        source = queue_by_id.get(source_id)
        if type(source) is not FractalCellQueueEntryV02:
            raise ValueError("g2d_backpressure_invalid")
        successors = tuple(
            (index, target)
            for index, target in enumerate(queue_entries)
            if target.predecessor_queue_entry_id == source_id
        )
        if len(successors) > 1:
            raise ValueError("g2d_backpressure_invalid")
        if not successors:
            missing_seen = True
            continue
        if missing_seen:
            raise ValueError("g2d_backpressure_invalid")
        position, target = successors[0]
        if not _d3_t03_target_matches_source_v02(
            target,
            source,
            state=state,
            expected_decision=expected_t03,
        ):
            raise ValueError("g2d_backpressure_invalid")
        positions.append(position)
    completed = len(positions)
    if completed != len(state.deferred_queue_entry_ids) and not allow_incomplete:
        raise ValueError("g2d_backpressure_invalid")
    if positions:
        state_frontier = positions[0] - 1
        if (
            state_frontier < 0
            or tuple(positions)
            != tuple(range(state_frontier + 1, state_frontier + 1 + completed))
            or completed < len(state.deferred_queue_entry_ids)
            and len(queue_entries) != state_frontier + 1 + completed
        ):
            raise ValueError("g2d_backpressure_invalid")
    else:
        state_frontier = len(queue_entries) - 1
    if state_frontier < 0 or any(
        queue_entries.index(queue_by_id[source_id]) > state_frontier
        for source_id in state.deferred_queue_entry_ids
    ):
        raise ValueError("g2d_backpressure_invalid")
    return state_frontier, completed


def _d3_frontier_local_indexes_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
    queue_frontier: int,
    global_budget: FractalRuntimeBudgetV02,
    complete_indexes: dict[str, object],
    prior_states: tuple[FractalBackpressureStateV02, ...],
    closure_frontiers: dict[str, int],
) -> dict[str, object]:
    budget_log = complete_indexes.get("budget_log")
    budget_position_by_id = complete_indexes.get("budget_position_by_id")
    complete_input_by_id = complete_indexes.get("input_by_id")
    complete_projection_by_child = complete_indexes.get("projection_by_child")
    complete_revise_by_id = complete_indexes.get("revise_by_id")
    complete_queue_position_by_id = complete_indexes.get("queue_position_by_id")
    if (
        type(budget_log) is not tuple
        or not all(
            isinstance(item, dict)
            for item in (
                budget_position_by_id,
                complete_input_by_id,
                complete_projection_by_child,
                complete_revise_by_id,
                complete_queue_position_by_id,
            )
        )
        or type(queue_frontier) is not int
        or not 0 <= queue_frontier < len(queue_entries)
        or queue_frontier >= len(queue_artifacts)
    ):
        raise ValueError("g2d_backpressure_invalid")
    budget_frontier = budget_position_by_id.get(global_budget.budget_id)
    if type(budget_frontier) is not int:
        raise ValueError("g2d_backpressure_invalid")
    local_budget_log = budget_log[: budget_frontier + 1]
    local = _d3_validate_budget_log_v02(
        local_budget_log,
        topology=topology,
        policy=policy,
        source_context=source_context,
    )
    _cell_head, live_global = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=topology.root_cell_id,
        indexes=local,
    )
    if live_global != global_budget:
        raise ValueError("g2d_backpressure_invalid")

    local_entries = queue_entries[: queue_frontier + 1]
    local_artifacts = queue_artifacts[: queue_frontier + 1]
    queue_by_id = {item.queue_entry_id: item for item in local_entries}
    queue_position_by_id = {
        item.queue_entry_id: index for index, item in enumerate(local_entries)
    }
    artifact_by_queue_id = {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(local_entries, local_artifacts, strict=True)
    }
    artifact_by_id = {item.artifact_id: item for item in local_artifacts}
    latest_by_key = {
        (item.cell_id, item.node_id): item
        for item in _d3_latest_queue_entries_v02(local_entries)
    }

    visible_inputs: list[FractalCellInputV02] = []
    for cell_input in complete_input_by_id.values():
        positions = tuple(
            complete_queue_position_by_id.get(item)
            for item in cell_input.ordered_initial_queue_entry_ids
        )
        visible = tuple(
            type(position) is int and position <= queue_frontier
            for position in positions
        )
        if any(visible) and not all(visible):
            raise ValueError("g2d_cell_input_build_order_invalid")
        if visible and all(visible):
            visible_inputs.append(cell_input)
    input_by_id = {item.cell_input_id: item for item in visible_inputs}
    input_by_cell = {item.cell_id: item for item in visible_inputs}
    projection_by_child = {
        child_id: projection
        for child_id, projection in complete_projection_by_child.items()
        if child_id in input_by_cell
    }
    if any(
        item.parent_cell_id is not None
        and (
            item.cell_id not in projection_by_child
            or item.scope_projection_id
            != projection_by_child[item.cell_id].projection_id
        )
        for item in visible_inputs
    ):
        raise ValueError("g2d_child_lineage_mismatch")

    local_budget_by_id = local["budget_by_id"]
    revise_by_id: dict[str, FractalReviseObservationV02] = {}
    for observation in complete_revise_by_id.values():
        source_position = complete_queue_position_by_id.get(
            observation.queue_entry_id
        )
        budgets_visible = (
            observation.cell_budget_before_id in local_budget_by_id
            and observation.global_budget_before_id in local_budget_by_id
        )
        if type(source_position) is int and source_position <= queue_frontier:
            if budgets_visible:
                revise_by_id[observation.observation_id] = observation
        elif budgets_visible and observation.queue_entry_id in queue_by_id:
            raise ValueError("g2d_revise_observation_invalid")

    visible_states = tuple(
        state
        for state in prior_states
        if closure_frontiers.get(state.backpressure_id, queue_frontier + 1)
        <= queue_frontier
    )
    local.update(
        budget_log=local_budget_log,
        queue_by_id=queue_by_id,
        queue_position_by_id=queue_position_by_id,
        latest_by_key=latest_by_key,
        artifact_by_queue_id=artifact_by_queue_id,
        artifact_by_id=artifact_by_id,
        input_by_id=input_by_id,
        input_by_cell=input_by_cell,
        projection_by_child=projection_by_child,
        revise_by_id=revise_by_id,
        backpressure_by_id={item.backpressure_id: item for item in visible_states},
        backpressure_closure_frontier_by_id={
            item.backpressure_id: closure_frontiers[item.backpressure_id]
            for item in visible_states
        },
    )
    return local


def _d3_validate_backpressure_closures_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
    states: tuple[FractalBackpressureStateV02, ...],
    indexes: dict[str, object],
    frontier: str,
) -> dict[str, int]:
    allowed_frontiers = {
        "COMPLETED",
        "QUEUE_ADVANCE",
        "T03_DECISION",
        "T03_QUEUE_ADVANCE",
        "T03_ARTIFACT",
    }
    if frontier not in allowed_frontiers:
        raise ValueError("g2d_backpressure_invalid")
    queue_by_id = indexes.get("queue_by_id")
    queue_position_by_id = indexes.get("queue_position_by_id")
    artifact_by_queue_id = indexes.get("artifact_by_queue_id")
    budget_by_id = indexes.get("budget_by_id")
    if not all(
        isinstance(item, dict)
        for item in (
            queue_by_id,
            queue_position_by_id,
            artifact_by_queue_id,
            budget_by_id,
        )
    ):
        raise ValueError("g2d_backpressure_invalid")
    closure_frontiers: dict[str, int] = {}
    for state_index, state in enumerate(states):
        is_current_state = state_index == len(states) - 1
        partial_allowed = frontier != "COMPLETED" and is_current_state
        state_frontier, available_count = _d3_backpressure_state_frontier_v02(
            state=state,
            queue_entries=queue_entries,
            queue_by_id=queue_by_id,
            allow_incomplete=partial_allowed,
        )
        state_entries = queue_entries[: state_frontier + 1]
        state_budget = budget_by_id.get(state.global_budget_id)
        if type(state_budget) is not FractalRuntimeBudgetV02:
            raise ValueError("g2d_backpressure_invalid")
        state_indexes = _d3_frontier_local_indexes_v02(
            source_context=source_context,
            topology=topology,
            policy=policy,
            queue_entries=queue_entries,
            queue_artifacts=queue_artifacts,
            queue_frontier=state_frontier,
            global_budget=state_budget,
            complete_indexes=indexes,
            prior_states=states[:state_index],
            closure_frontiers=closure_frontiers,
        )
        state_material = _d3_round_control_material_v02(
            source_context=source_context,
            topology=topology,
            policy=policy,
            global_budget=state_budget,
            admission_round=state.evaluated_round,
            entries=state_entries,
            indexes=state_indexes,
            prior_backpressure_states=states[:state_index],
        )
        expected_deferred = tuple(
            item.queue_entry_id for item in state_material["deferred"]
        )
        expected_admission_order = tuple(
            item.queue_entry_id for item in state_material["admission_entries"]
        )
        core = state_material["controlling_core"]
        if (
            not isinstance(core, dict)
            or state.deferred_queue_entry_ids != expected_deferred
            or state.admission_order != expected_admission_order
            or state.running_count != core["running_count"]
            or state.ready_count != core["ready_count"]
            or state.pending_count != len(expected_deferred)
            or state.queue_capacity != policy.max_parallelism
            or state.backpressure_reason != "PARALLELISM_CAPACITY_EXHAUSTED"
            or state.reason_codes
            != ("g2d_transition_backpressure_deferred",)
            or state.no_work_dropped is not True
        ):
            raise ValueError("g2d_backpressure_invalid")
        expected_count = len(state.deferred_queue_entry_ids)
        if not partial_allowed and available_count != expected_count:
            raise ValueError("g2d_backpressure_invalid")
        for offset in range(available_count):
            source_id = state.deferred_queue_entry_ids[offset]
            source = queue_by_id[source_id]
            target_index = state_frontier + 1 + offset
            target = queue_entries[target_index]
            if (
                type(source) is not FractalCellQueueEntryV02
                or not _d3_t03_target_matches_source_v02(
                    target, source, state=state,
                    expected_decision=_d3_transition_decision_v02(
                        _build_fractal_runtime_transition_registry_profile_v02(),
                        "t03",
                    ),
                )
            ):
                raise ValueError("g2d_backpressure_invalid")
            artifact_present = target_index < len(queue_artifacts)
            if not artifact_present and not (
                frontier == "T03_ARTIFACT"
                and is_current_state
                and offset == available_count - 1
                and target_index == len(queue_entries) - 1
            ):
                raise ValueError("g2d_backpressure_invalid")
            if artifact_present and target.queue_entry_id not in artifact_by_queue_id:
                raise ValueError("g2d_backpressure_invalid")
        if available_count < expected_count:
            if not partial_allowed:
                raise ValueError("g2d_backpressure_invalid")
            if len(queue_entries) != state_frontier + 1 + available_count:
                raise ValueError("g2d_backpressure_invalid")
        else:
            closure_frontiers[state.backpressure_id] = state_frontier + expected_count
    return closure_frontiers


def _d3_next_t03_source_id_v02(
    *,
    state: FractalBackpressureStateV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_by_id: dict[str, FractalCellQueueEntryV02],
) -> str | None:
    _state_frontier, completed = _d3_backpressure_state_frontier_v02(
        state=state,
        queue_entries=queue_entries,
        queue_by_id=queue_by_id,
        allow_incomplete=True,
    )
    return (
        None
        if completed == len(state.deferred_queue_entry_ids)
        else state.deferred_queue_entry_ids[completed]
    )


def _d3_source_bound_cell_input_from_prefix_v02(
    *,
    cell_id: str,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    budget_by_id: dict[str, FractalRuntimeBudgetV02],
    queue_by_id: dict[str, FractalCellQueueEntryV02],
    artifact_by_queue_id: dict[str, KernelArtifactV01],
    artifact_by_id: dict[str, KernelArtifactV01],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    validated_inputs: dict[str, FractalCellInputV02],
    validating_cells: set[str],
    indexes: dict[str, object],
) -> FractalCellInputV02:
    cached = validated_inputs.get(cell_id)
    if cached is not None:
        return cached
    if cell_id in validating_cells:
        raise ValueError("g2d_cell_input_invalid")
    matches = tuple(item for item in settled_cell_inputs if item.cell_id == cell_id)
    if len(matches) != 1:
        raise ValueError("g2d_cell_input_invalid")
    value = matches[0]
    if (
        type(value) is not FractalCellInputV02
        or validate_fractal_cell_input_v02(value).status != "PASS"
        or value.topology_id != topology.topology_id
    ):
        raise ValueError("g2d_cell_input_invalid")
    validating_cells.add(cell_id)
    try:
        initial_entries = tuple(
            queue_by_id.get(item) for item in value.ordered_initial_queue_entry_ids
        )
        if (
            not initial_entries
            or any(type(item) is not FractalCellQueueEntryV02 for item in initial_entries)
            or tuple(item.node_id for item in initial_entries) != value.ordered_node_ids
            or any(
                item.cell_id != value.cell_id
                or item.parent_cell_id != value.parent_cell_id
                or item.predecessor_queue_entry_id is not None
                or item.prior_state is not None
                or item.state != "PENDING"
                for item in initial_entries
            )
        ):
            raise ValueError("g2d_cell_input_build_order_invalid")
        initial_artifacts = tuple(
            artifact_by_queue_id.get(item.queue_entry_id) for item in initial_entries
        )
        if any(type(item) is not KernelArtifactV01 for item in initial_artifacts):
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        cell_budget = budget_by_id.get(value.cell_budget_id)
        global_budget = budget_by_id.get(value.global_budget_id)
        if (
            type(cell_budget) is not FractalRuntimeBudgetV02
            or type(global_budget) is not FractalRuntimeBudgetV02
        ):
            raise ValueError("g2d_budget_invalid")

        parent_input: FractalCellInputV02 | None = None
        parent_slot_artifact: KernelArtifactV01 | None = None
        scope_projection: ParentChildScopeProjectionV02 | None = None
        if value.parent_cell_id is not None:
            parent_input = _d3_source_bound_cell_input_from_prefix_v02(
                cell_id=value.parent_cell_id,
                source_context=source_context,
                topology=topology,
                topology_artifact=topology_artifact,
                budget_by_id=budget_by_id,
                queue_by_id=queue_by_id,
                artifact_by_queue_id=artifact_by_queue_id,
                artifact_by_id=artifact_by_id,
                settled_cell_inputs=settled_cell_inputs,
                settled_scope_projections=settled_scope_projections,
                validated_inputs=validated_inputs,
                validating_cells=validating_cells,
                indexes=indexes,
            )
            projections = tuple(
                item
                for item in settled_scope_projections
                if item.child_cell_id == value.cell_id
            )
            if len(projections) != 1:
                raise ValueError("g2d_child_lineage_mismatch")
            scope_projection = projections[0]
            if (
                validate_parent_child_scope_against_sources_v02(
                    scope_projection,
                    source_context=source_context,
                    topology=topology,
                    parent_input=parent_input,
                    parent_budget=budget_by_id[scope_projection.parent_budget_id],
                    child_budget=budget_by_id[scope_projection.child_budget_id],
                    global_budget=budget_by_id[scope_projection.global_budget_id],
                ).status
                != "PASS"
            ):
                raise ValueError("g2d_child_lineage_mismatch")
            first_parent_refs = initial_artifacts[0].parent_refs
            if len(first_parent_refs) != 2:
                raise ValueError("g2d_child_slot_activation_invalid")
            parent_slot_artifact = artifact_by_id.get(first_parent_refs[1])
            if type(parent_slot_artifact) is not KernelArtifactV01:
                raise ValueError("g2d_child_slot_activation_invalid")
            _d3_validate_parent_slot_artifact_v02(
                parent_slot_artifact,
                topology=topology,
                parent_cell_id=value.parent_cell_id,
                child_cell_id=value.cell_id,
            )
            _d3_validate_parent_slot_chain_v02(
                parent_slot_artifact=parent_slot_artifact,
                parent_cell_id=value.parent_cell_id,
                child_cell_id=value.cell_id,
                topology=topology,
                indexes=indexes,
            )

        report = _d3_validate_cell_input_against_validated_prefix_v02(
            value,
            source_context=source_context,
            topology=topology,
            topology_artifact=topology_artifact,
            parent_input=parent_input,
            parent_slot_artifact=parent_slot_artifact,
            scope_projection=scope_projection,
            cell_budget=cell_budget,
            global_budget=global_budget,
            queue_entries=tuple(initial_entries),
            queue_artifacts=tuple(initial_artifacts),
        )
        if report.status != "PASS":
            raise ValueError("g2d_cell_input_invalid")
        validated_inputs[cell_id] = value
        return value
    finally:
        validating_cells.remove(cell_id)


def _d3_profile_d_omission_index_v02(
    *,
    queue_entry: FractalCellQueueEntryV02,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    indexes: dict[str, object],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
) -> int | None:
    if (
        type(queue_entry) is not FractalCellQueueEntryV02
        or queue_entry.parent_cell_id is None
        or queue_entry.predecessor_queue_entry_id is None
    ):
        return None
    pair = (queue_entry.prior_state, queue_entry.state)
    if pair not in {
        ("RUNNING", "VALIDATING"),
        ("VALIDATING", "COMPLETED"),
        ("VALIDATING", "DEGRADED"),
        ("VALIDATING", "BLOCKED"),
        ("VALIDATING", "NEEDS_USER"),
        ("VALIDATING", "DEADEND"),
    }:
        return None
    _binding, _seed, _initial, nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    node = next((item for item in nodes if item.node_id == queue_entry.node_id), None)
    if type(node) is not RuntimeTopologyNodeV02:
        raise ValueError("g2d_topology_node_invalid")
    if node.node_kind not in _D3_LOCAL_NODE_KINDS_V02:
        return None

    queue_by_id = indexes.get("queue_by_id")
    queue_position_by_id = indexes.get("queue_position_by_id")
    artifact_by_queue_id = indexes.get("artifact_by_queue_id")
    artifact_by_id = indexes.get("artifact_by_id")
    budget_by_id = indexes.get("budget_by_id")
    if not all(
        isinstance(item, dict)
        for item in (
            queue_by_id,
            queue_position_by_id,
            artifact_by_queue_id,
            artifact_by_id,
            budget_by_id,
        )
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    topology_artifact = _build_topology_artifact_v02(topology, source_context)
    validated_inputs: dict[str, FractalCellInputV02] = {}
    cell_input = _d3_source_bound_cell_input_from_prefix_v02(
        cell_id=queue_entry.cell_id,
        source_context=source_context,
        topology=topology,
        topology_artifact=topology_artifact,
        budget_by_id=budget_by_id,
        queue_by_id=queue_by_id,
        artifact_by_queue_id=artifact_by_queue_id,
        artifact_by_id=artifact_by_id,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        validated_inputs=validated_inputs,
        validating_cells=set(),
        indexes=indexes,
    )
    if (
        cell_input.parent_cell_id != queue_entry.parent_cell_id
        or queue_entry.node_id not in cell_input.ordered_node_ids
    ):
        raise ValueError("g2d_cell_input_invalid")
    node_position = cell_input.ordered_node_ids.index(queue_entry.node_id)
    initial_id = cell_input.ordered_initial_queue_entry_ids[node_position]
    initial_entry = queue_by_id.get(initial_id)
    initial_artifact = artifact_by_queue_id.get(initial_id)
    if (
        type(initial_entry) is not FractalCellQueueEntryV02
        or type(initial_artifact) is not KernelArtifactV01
        or initial_entry.cell_id != queue_entry.cell_id
        or initial_entry.parent_cell_id != queue_entry.parent_cell_id
        or initial_entry.node_id != queue_entry.node_id
        or initial_entry.predecessor_queue_entry_id is not None
        or initial_entry.prior_state is not None
        or initial_entry.state != "PENDING"
        or len(initial_artifact.parent_refs) != 2
        or len(queue_entry.lineage_refs) < 10
    ):
        raise ValueError("g2d_queue_predecessor_invalid")
    activation_parent_id = initial_artifact.parent_refs[1]
    activation_parent_artifact = artifact_by_id.get(activation_parent_id)
    if type(activation_parent_artifact) is not KernelArtifactV01:
        raise ValueError("g2d_child_slot_activation_invalid")
    _d3_validate_parent_slot_artifact_v02(
        activation_parent_artifact,
        topology=topology,
        parent_cell_id=queue_entry.parent_cell_id,
        child_cell_id=queue_entry.cell_id,
    )
    _d3_validate_parent_slot_chain_v02(
        parent_slot_artifact=activation_parent_artifact,
        parent_cell_id=queue_entry.parent_cell_id,
        child_cell_id=queue_entry.cell_id,
        topology=topology,
        indexes=indexes,
    )

    cursor = queue_entry
    seen: set[str] = set()
    while cursor.queue_entry_id != initial_entry.queue_entry_id:
        if cursor.queue_entry_id in seen:
            raise ValueError("g2d_queue_predecessor_invalid")
        seen.add(cursor.queue_entry_id)
        predecessor = queue_by_id.get(cursor.predecessor_queue_entry_id)
        if (
            type(predecessor) is not FractalCellQueueEntryV02
            or predecessor.cell_id != queue_entry.cell_id
            or predecessor.parent_cell_id != queue_entry.parent_cell_id
            or predecessor.node_id != queue_entry.node_id
            or cursor.predecessor_relation != "EXACT_IMMEDIATE_PREDECESSOR"
            or cursor.snapshot_sequence != predecessor.snapshot_sequence + 1
            or cursor.prior_state != predecessor.state
        ):
            raise ValueError("g2d_queue_predecessor_invalid")
        cursor = predecessor
    if queue_entry.lineage_refs[7] != activation_parent_id:
        raise ValueError("g2d_queue_artifact_lineage_invalid")

    if pair == ("RUNNING", "VALIDATING"):
        validating_entry = queue_entry
    else:
        validating_entry = queue_by_id.get(queue_entry.predecessor_queue_entry_id)
        if (
            type(validating_entry) is not FractalCellQueueEntryV02
            or (validating_entry.prior_state, validating_entry.state)
            != ("RUNNING", "VALIDATING")
            or validating_entry.cell_id != queue_entry.cell_id
            or validating_entry.node_id != queue_entry.node_id
            or queue_entry.queue_reason_codes != validating_entry.queue_reason_codes
            or queue_entry.observed_output_refs != validating_entry.observed_output_refs
            or queue_entry.observed_evidence_refs != validating_entry.observed_evidence_refs
            or queue_entry.advisory_refs != validating_entry.advisory_refs
        ):
            raise ValueError("g2d_queue_predecessor_invalid")

    profile_indexes = {
        **indexes,
        "input_by_id": {
            item.cell_input_id: item for item in validated_inputs.values()
        },
        "input_by_cell": dict(validated_inputs),
    }
    origin = _d3_t06_origin_frontier_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        validating_entry=validating_entry,
        node=node,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        indexes=profile_indexes,
    )
    if origin["dependencies"] != ():
        return None
    material = _d3_local_observation_material_v02(
        source_context=source_context,
        topology=topology,
        node=node,
        cell_input=cell_input,
        cell_budget_before=origin["cell_budget_before"],
        global_budget_before=origin["global_budget_before"],
        dependencies=origin["dependencies"],
        indexes=profile_indexes,
    )
    if (
        validating_entry.queue_reason_codes
        != material["derived_queue_reason_codes"]
        or validating_entry.observed_output_refs
        != material["derived_observed_output_refs"]
        or validating_entry.observed_evidence_refs
        != material["derived_observed_evidence_refs"]
        or validating_entry.advisory_refs
        != material["derived_advisory_refs"]
        or validating_entry.observed_evidence_refs != cell_input.evidence_refs
        or (
            pair[1] != "VALIDATING"
            and queue_entry.state != material["allowed_outcome"]
        )
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    evidence_matches = tuple(
        index
        for index, item in enumerate(cell_input.evidence_refs)
        if item == activation_parent_id
    )
    if (
        len(evidence_matches) != 1
        or queue_entry.observed_evidence_refs.count(activation_parent_id) != 1
        or queue_entry.lineage_refs.count(activation_parent_id) != 2
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    omission_index = 9 + len(queue_entry.observed_output_refs) + evidence_matches[0]
    if (
        omission_index >= len(queue_entry.lineage_refs)
        or queue_entry.lineage_refs[omission_index] != activation_parent_id
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    return omission_index


def _d3_expected_queue_artifact_against_prefix_v02(
    entry: FractalCellQueueEntryV02,
    *,
    parent_refs: tuple[str, ...],
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    indexes: dict[str, object],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
) -> KernelArtifactV01:
    omission_index = _d3_profile_d_omission_index_v02(
        queue_entry=entry,
        source_context=source_context,
        topology=topology,
        indexes=indexes,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
    )
    if omission_index is None:
        return _d3_build_queue_artifact_v02(
            entry,
            parent_refs=parent_refs,
            source_context=source_context,
        )
    return _d3_build_queue_artifact_with_exact_omission_v02(
        entry,
        parent_refs=parent_refs,
        source_context=source_context,
        profile_d_omission_index=omission_index,
    )


def _d3_validate_settled_runtime_prefix_v02(
    *,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    source_context: FractalRuntimeSourceContextV02,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
    candidate_queue_entry: FractalCellQueueEntryV02 | None = None,
    frontier: str = "COMPLETED",
) -> dict[str, object]:
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    if (
        type(source_context) is not FractalRuntimeSourceContextV02
        or validate_fractal_runtime_source_context_v02(source_context).status != "PASS"
        or policy != source_context.runtime_policy
        or _canonical_json_bytes_v01(fractal_runtime_policy_to_plain_data_v02(policy))
        != _canonical_json_bytes_v01(
            fractal_runtime_policy_to_plain_data_v02(source_context.runtime_policy)
        )
        or policy.policy_id != topology.runtime_policy_id
        or validate_runtime_execution_topology_against_sources_v02(
            topology,
            source_context=source_context,
        ).status
        != "PASS"
    ):
        raise ValueError("g2d_topology_policy_invalid")
    tuple_rows = (
        (settled_queue_entry_log, FractalCellQueueEntryV02),
        (settled_queue_artifact_log, KernelArtifactV01),
        (settled_cell_inputs, FractalCellInputV02),
        (settled_scope_projections, ParentChildScopeProjectionV02),
        (settled_revise_observations, FractalReviseObservationV02),
        (settled_backpressure_states, FractalBackpressureStateV02),
        (settled_validation_reports, FractalRuntimeValidationReportV02),
    )
    if any(
        type(values) is not tuple or any(type(item) is not expected for item in values)
        for values, expected in tuple_rows
    ):
        raise ValueError("g2d_type_invalid")
    budget_indexes = _d3_validate_budget_log_v02(
        settled_budget_log,
        topology=topology,
        policy=policy,
        source_context=source_context,
    )
    budget_by_id = budget_indexes["budget_by_id"]
    if not isinstance(budget_by_id, dict):
        raise ValueError("g2d_budget_invalid")
    candidate_present = candidate_queue_entry is not None
    if len(settled_queue_entry_log) != len(settled_queue_artifact_log) + int(candidate_present):
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    if candidate_present and (
        not settled_queue_entry_log or settled_queue_entry_log[-1] != candidate_queue_entry
    ):
        raise ValueError("g2d_queue_artifact_lineage_invalid")

    queue_by_id: dict[str, FractalCellQueueEntryV02] = {}
    latest_by_key: dict[tuple[str, str], FractalCellQueueEntryV02] = {}
    artifact_by_queue_id: dict[str, KernelArtifactV01] = {}
    artifact_by_id: dict[str, KernelArtifactV01] = {}
    queue_position_by_id: dict[str, int] = {}
    cell_order: list[str] = []
    for index, entry in enumerate(settled_queue_entry_log):
        if (
            validate_fractal_cell_queue_entry_v02(entry).status != "PASS"
            or entry.topology_id != topology.topology_id
            or entry.topology_seed_id != topology.topology_seed_id
            or entry.queue_entry_id in queue_by_id
            or entry.cell_budget_id not in budget_by_id
            or entry.global_budget_id not in budget_by_id
        ):
            raise ValueError("g2d_queue_entry_invalid")
        _d3_validate_queue_budget_anchors_v02(
            entry,
            topology=topology,
            indexes=budget_indexes,
        )
        key = (entry.cell_id, entry.node_id)
        prior = latest_by_key.get(key)
        if prior is None:
            if (
                entry.prior_state is not None
                or entry.predecessor_queue_entry_id is not None
                or entry.snapshot_sequence != 0
                or entry.admission_round != 0
                or entry.state != "PENDING"
            ):
                raise ValueError("g2d_queue_predecessor_invalid")
        else:
            if (
                prior.state in _D3_TERMINAL_STATES_V02
                or entry.predecessor_queue_entry_id != prior.queue_entry_id
                or entry.prior_state != prior.state
                or entry.snapshot_sequence != prior.snapshot_sequence + 1
                or entry.admission_round <= prior.admission_round
            ):
                raise ValueError("g2d_queue_predecessor_invalid")
        if entry.cell_id not in cell_order:
            cell_order.append(entry.cell_id)
        queue_by_id[entry.queue_entry_id] = entry
        queue_position_by_id[entry.queue_entry_id] = index
        latest_by_key[key] = entry
        if index < len(settled_queue_artifact_log):
            artifact = settled_queue_artifact_log[index]
            if (
                type(artifact) is not KernelArtifactV01
                or _validate_kernel_artifact_v01(artifact)
                or artifact.artifact_type != "FractalCellQueueEntry"
                or artifact.artifact_id in artifact_by_id
            ):
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            if entry.predecessor_queue_entry_id is not None:
                predecessor_artifact = artifact_by_queue_id.get(entry.predecessor_queue_entry_id)
                if (
                    predecessor_artifact is None
                    or len(artifact.parent_refs) not in {2, 3}
                    or artifact.parent_refs[1] != predecessor_artifact.artifact_id
                ):
                    raise ValueError("g2d_queue_predecessor_invalid")
            elif entry.parent_cell_id is None:
                if len(artifact.parent_refs) != 1:
                    raise ValueError("g2d_queue_artifact_lineage_invalid")
            else:
                if len(artifact.parent_refs) != 2:
                    raise ValueError("g2d_queue_artifact_lineage_invalid")
                activation = artifact_by_id.get(artifact.parent_refs[1])
                if activation is None:
                    raise ValueError("g2d_child_slot_activation_invalid")
                activation_entry_id = _d3_queue_artifact_payload_ref_v02(
                    activation,
                    "queue_entry_id",
                )
                activation_entry = queue_by_id.get(activation_entry_id)
                if (
                    activation_entry is None
                    or activation_entry.state != "RUNNING"
                    or activation_entry.cell_id != entry.parent_cell_id
                    or activation_entry.planned_child_cell_id != entry.cell_id
                ):
                    raise ValueError("g2d_child_slot_activation_invalid")
            context_indexes = {
                **budget_indexes,
                "budget_log": settled_budget_log,
                "queue_by_id": queue_by_id,
                "queue_position_by_id": queue_position_by_id,
                "latest_by_key": latest_by_key,
                "artifact_by_queue_id": artifact_by_queue_id,
                "artifact_by_id": artifact_by_id,
            }
            expected_artifact = _d3_expected_queue_artifact_against_prefix_v02(
                entry,
                parent_refs=artifact.parent_refs,
                source_context=source_context,
                topology=topology,
                indexes=context_indexes,
                settled_budget_log=settled_budget_log,
                settled_queue_entry_log=settled_queue_entry_log,
                settled_cell_inputs=settled_cell_inputs,
                settled_scope_projections=settled_scope_projections,
            )
            if (
                artifact != expected_artifact
                or _canonical_json_bytes_v01(
                    _kernel_artifact_to_plain_dict_v01(artifact)
                )
                != _canonical_json_bytes_v01(
                    _kernel_artifact_to_plain_dict_v01(expected_artifact)
                )
            ):
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            artifact_by_queue_id[entry.queue_entry_id] = artifact
            artifact_by_id[artifact.artifact_id] = artifact

    queue_budget_event_state = {
        "START_NODE": "RUNNING",
        "FINISH_NODE": "VALIDATING",
        "REVISE": "READY",
    }
    orphan_event_indexes: list[int] = []
    for budget_index, budget in enumerate(settled_budget_log):
        target_state = queue_budget_event_state.get(budget.budget_event_kind)
        if target_state is None:
            continue
        bound = any(
            entry.state == target_state
            and entry.transition_decision_id == budget.budget_event_ref
            and (
                entry.cell_budget_id == budget.budget_id
                if budget.budget_scope == "CHILD_CELL_LOCAL"
                else entry.global_budget_id == budget.budget_id
            )
            for entry in settled_queue_entry_log
        )
        if not bound:
            orphan_event_indexes.append(budget_index)
    if orphan_event_indexes:
        allowed_tail = tuple(range(orphan_event_indexes[0], len(settled_budget_log)))
        orphan_budgets = tuple(settled_budget_log[index] for index in orphan_event_indexes)
        if (
            frontier != "QUEUE_ADVANCE"
            or tuple(orphan_event_indexes) != allowed_tail
            or len(orphan_budgets) not in (1, 2)
            or any(
                item.budget_event_kind != orphan_budgets[0].budget_event_kind
                for item in orphan_budgets
            )
            or any(
                item.budget_event_ref != orphan_budgets[0].budget_event_ref
                for item in orphan_budgets
            )
        ):
            raise ValueError("g2d_budget_event_context_invalid")

    input_by_id: dict[str, FractalCellInputV02] = {}
    input_by_cell: dict[str, FractalCellInputV02] = {}
    for index, cell_input in enumerate(settled_cell_inputs):
        if (
            validate_fractal_cell_input_v02(cell_input).status != "PASS"
            or cell_input.topology_id != topology.topology_id
            or cell_input.cell_input_id in input_by_id
            or cell_input.cell_id in input_by_cell
            or index >= len(cell_order)
            or cell_input.cell_id != cell_order[index]
            or cell_input.cell_budget_id not in budget_by_id
            or cell_input.global_budget_id not in budget_by_id
        ):
            raise ValueError("g2d_cell_input_invalid")
        initial_entries = tuple(
            queue_by_id.get(item) for item in cell_input.ordered_initial_queue_entry_ids
        )
        required_entries = tuple(
            queue_by_id.get(item) for item in cell_input.ordered_required_queue_entry_ids
        )
        if (
            not initial_entries
            or any(item is None or item.cell_id != cell_input.cell_id for item in initial_entries)
            or required_entries != initial_entries
            or tuple(item.node_id for item in initial_entries) != cell_input.ordered_node_ids
        ):
            raise ValueError("g2d_cell_input_build_order_invalid")
        input_by_id[cell_input.cell_input_id] = cell_input
        input_by_cell[cell_input.cell_id] = cell_input

    projection_by_child: dict[str, ParentChildScopeProjectionV02] = {}
    for projection in settled_scope_projections:
        if (
            validate_parent_child_scope_projection_v02(projection).status != "PASS"
            or projection.topology_id != topology.topology_id
            or projection.child_cell_id in projection_by_child
            or projection.parent_cell_id not in input_by_cell
            or projection.child_budget_id not in budget_by_id
            or projection.global_budget_id not in budget_by_id
        ):
            raise ValueError("g2d_child_lineage_mismatch")
        child_budget = budget_by_id[projection.child_budget_id]
        global_budget = budget_by_id[projection.global_budget_id]
        if (
            child_budget.owning_cell_id != projection.child_cell_id
            or child_budget.budget_scope != "CHILD_CELL_LOCAL"
            or global_budget.owning_cell_id != topology.root_cell_id
            or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
            or not any(
                item.owning_cell_id == projection.child_cell_id
                and item.budget_event_kind == "CELL_CREATE"
                for item in settled_budget_log
            )
        ):
            raise ValueError("g2d_child_lineage_mismatch")
        child_input = input_by_cell.get(projection.child_cell_id)
        if child_input is not None and child_input.scope_projection_id != projection.projection_id:
            raise ValueError("g2d_child_lineage_mismatch")
        projection_by_child[projection.child_cell_id] = projection
    if any(
        cell_input.parent_cell_id is not None
        and cell_input.cell_id not in projection_by_child
        for cell_input in settled_cell_inputs
    ):
        raise ValueError("g2d_child_lineage_mismatch")

    revise_by_id: dict[str, FractalReviseObservationV02] = {}
    for observation in settled_revise_observations:
        entry = queue_by_id.get(observation.queue_entry_id)
        if (
            validate_fractal_revise_observation_v02(observation).status != "PASS"
            or observation.observation_id in revise_by_id
            or observation.topology_id != topology.topology_id
            or entry is None
            or entry.cell_id != observation.cell_id
            or observation.cell_budget_before_id not in budget_by_id
            or observation.global_budget_before_id not in budget_by_id
        ):
            raise ValueError("g2d_revise_observation_invalid")
        revise_by_id[observation.observation_id] = observation

    prior_round = -1
    backpressure_by_id: dict[str, FractalBackpressureStateV02] = {}
    rounds: list[int] = []
    for state in settled_backpressure_states:
        if (
            validate_fractal_backpressure_state_v02(state).status != "PASS"
            or state.backpressure_id in backpressure_by_id
            or state.topology_id != topology.topology_id
            or state.policy_id != policy.policy_id
            or state.global_budget_id not in budget_by_id
            or state.evaluated_round <= prior_round
            or state.evaluated_round in rounds
            or any(item not in queue_by_id for item in state.deferred_queue_entry_ids)
            or any(item not in queue_by_id for item in state.admission_order)
        ):
            raise ValueError("g2d_backpressure_invalid")
        prior_round = state.evaluated_round
        rounds.append(state.evaluated_round)
        backpressure_by_id[state.backpressure_id] = state

    expected_reports: list[FractalRuntimeValidationReportV02] = list(
        _d3_expected_retained_base_reports_v02(source_context, topology)
    )
    expected_reports.extend(
        validate_fractal_cell_queue_entry_v02(entry)
        for entry in settled_queue_entry_log[: len(settled_queue_artifact_log)]
    )
    for projection in settled_scope_projections:
        parent_input = input_by_cell[projection.parent_cell_id]
        expected_reports.append(
            validate_parent_child_scope_against_sources_v02(
                projection,
                source_context=source_context,
                topology=topology,
                parent_input=parent_input,
                parent_budget=budget_by_id[projection.parent_budget_id],
                child_budget=budget_by_id[projection.child_budget_id],
                global_budget=budget_by_id[projection.global_budget_id],
            )
        )
    topology_artifact = _build_topology_artifact_v02(topology, source_context)
    for cell_input in settled_cell_inputs:
        initial_entries = tuple(
            queue_by_id[item]
            for item in cell_input.ordered_initial_queue_entry_ids
        )
        initial_artifacts = tuple(
            artifact_by_queue_id[item.queue_entry_id] for item in initial_entries
        )
        parent_input = (
            None
            if cell_input.parent_cell_id is None
            else input_by_cell[cell_input.parent_cell_id]
        )
        scope_projection = projection_by_child.get(cell_input.cell_id)
        parent_slot_artifact = None
        if cell_input.parent_cell_id is not None:
            first_parent_refs = initial_artifacts[0].parent_refs
            if len(first_parent_refs) != 2:
                raise ValueError("g2d_child_slot_activation_invalid")
            parent_slot_artifact = artifact_by_id.get(first_parent_refs[1])
            if type(parent_slot_artifact) is not KernelArtifactV01:
                raise ValueError("g2d_child_slot_activation_invalid")
        expected_reports.append(
            _d3_validate_cell_input_against_validated_prefix_v02(
                cell_input,
                source_context=source_context,
                topology=topology,
                topology_artifact=topology_artifact,
                parent_input=parent_input,
                parent_slot_artifact=parent_slot_artifact,
                scope_projection=scope_projection,
                cell_budget=budget_by_id[cell_input.cell_budget_id],
                global_budget=budget_by_id[cell_input.global_budget_id],
                queue_entries=initial_entries,
                queue_artifacts=initial_artifacts,
            )
        )
    if (
        len(settled_validation_reports) != len(expected_reports)
        or any(
            validate_fractal_runtime_validation_report_v02(actual)
            or expected.status != "PASS"
            or not _d3_validation_reports_equal_v02(actual, expected)
            for actual, expected in zip(
                settled_validation_reports,
                expected_reports,
                strict=True,
            )
        )
    ):
        raise ValueError("g2d_validation_target_id_mismatch")
    result = {
        **budget_indexes,
        "validated_source_context": source_context,
        "validated_topology": topology,
        "budget_log": settled_budget_log,
        "queue_by_id": queue_by_id,
        "queue_position_by_id": queue_position_by_id,
        "latest_by_key": latest_by_key,
        "artifact_by_queue_id": artifact_by_queue_id,
        "artifact_by_id": artifact_by_id,
        "input_by_id": input_by_id,
        "input_by_cell": input_by_cell,
        "projection_by_child": projection_by_child,
        "revise_by_id": revise_by_id,
        "backpressure_by_id": backpressure_by_id,
    }
    result["backpressure_closure_frontier_by_id"] = (
        _d3_validate_backpressure_closures_v02(
            source_context=source_context,
            topology=topology,
            policy=policy,
            queue_entries=settled_queue_entry_log,
            queue_artifacts=settled_queue_artifact_log,
            states=settled_backpressure_states,
            indexes=result,
            frontier=frontier,
        )
    )
    return result


def _d3_validate_parent_slot_chain_v02(
    *,
    parent_slot_artifact: KernelArtifactV01,
    parent_cell_id: str,
    child_cell_id: str,
    topology: RuntimeExecutionTopologyV02,
    indexes: dict[str, object],
) -> tuple[FractalCellQueueEntryV02, FractalCellQueueEntryV02, FractalCellQueueEntryV02]:
    artifact_by_id = indexes["artifact_by_id"]
    queue_by_id = indexes["queue_by_id"]
    budget_by_id = indexes["budget_by_id"]
    artifact_by_queue_id = indexes["artifact_by_queue_id"]
    if (
        not isinstance(artifact_by_id, dict)
        or not isinstance(artifact_by_queue_id, dict)
        or not isinstance(queue_by_id, dict)
        or not isinstance(budget_by_id, dict)
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    if artifact_by_id.get(parent_slot_artifact.artifact_id) != parent_slot_artifact:
        raise ValueError("g2d_child_slot_activation_invalid")
    running_id = _d3_queue_artifact_payload_ref_v02(parent_slot_artifact, "queue_entry_id")
    running = queue_by_id.get(running_id)
    if type(running) is not FractalCellQueueEntryV02 or running.state != "RUNNING":
        raise ValueError("g2d_child_slot_activation_invalid")
    ready = queue_by_id.get(running.predecessor_queue_entry_id)
    initial = (
        queue_by_id.get(ready.predecessor_queue_entry_id)
        if type(ready) is FractalCellQueueEntryV02
        else None
    )
    if (
        type(ready) is not FractalCellQueueEntryV02
        or type(initial) is not FractalCellQueueEntryV02
        or (initial.prior_state, initial.state) != (None, "PENDING")
        or (ready.prior_state, ready.state) != ("PENDING", "READY")
        or (running.prior_state, running.state) != ("READY", "RUNNING")
        or initial.node_id != running.node_id
        or ready.node_id != running.node_id
        or initial.cell_id != running.cell_id
        or ready.cell_id != running.cell_id
        or initial.planned_child_cell_id != child_cell_id
        or ready.planned_child_cell_id != child_cell_id
        or running.cell_id != parent_cell_id
        or running.planned_child_cell_id != child_cell_id
        or running.topology_id != topology.topology_id
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    if (
        initial.transition_decision_id
        != _d3_transition_decision_v02(registry, "t02").decision_id
        or ready.transition_decision_id
        != _d3_transition_decision_v02(registry, "t04").decision_id
        or running.transition_decision_id
        != _d3_transition_decision_v02(registry, "t05").decision_id
        or artifact_by_queue_id.get(initial.queue_entry_id) is None
        or artifact_by_queue_id.get(ready.queue_entry_id) is None
        or artifact_by_queue_id.get(running.queue_entry_id) != parent_slot_artifact
        or ready.cell_budget_id != initial.cell_budget_id
        or ready.global_budget_id != initial.global_budget_id
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    start_cell = budget_by_id.get(running.cell_budget_id)
    start_global = budget_by_id.get(running.global_budget_id)
    if (
        type(start_cell) is not FractalRuntimeBudgetV02
        or type(start_global) is not FractalRuntimeBudgetV02
        or start_cell.budget_event_kind != "START_NODE"
        or start_global.budget_event_kind != "START_NODE"
        or start_cell.budget_event_ref != running.transition_decision_id
        or start_global.budget_event_ref != running.transition_decision_id
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    return initial, ready, running


def admit_runtime_execution_topology_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    topology_transition_decision: TransitionDecisionV01,
    cell_id: str,
    parent_cell_id: str | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    cell_depth: int,
    scope_ref: str,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    projected_nodes: tuple[RuntimeTopologyNodeV02, ...],
    planned_child_cell_ids: tuple[str, ...],
    admission_decisions: tuple[TransitionDecisionV01, ...],
    cell_instantiation_order: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> tuple[FractalCellQueueEntryV02, ...]:
    source_binding, seed, _initial_budget, all_nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
    )
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    expected_t01 = evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source_context,
        topology=topology,
        transition_registry=registry,
    )
    expected_topology_artifact = _build_topology_artifact_v02(topology, source_context)
    if (
        topology_transition_decision != expected_t01
        or topology_artifact != expected_topology_artifact
        or _validate_fractal_runtime_transition_decision_v02(
            expected_t01,
            registry=registry,
            source_artifact=source_context.route_eligibility_artifact,
            target_artifact=topology_artifact,
        )
    ):
        raise ValueError("g2d_transition_decision_substituted")
    if (
        type(cell_instantiation_order) is not tuple
        or not _unique_tuple(cell_instantiation_order)
        or not cell_instantiation_order
        or cell_instantiation_order[-1] != cell_id
    ):
        raise ValueError("g2d_child_lineage_mismatch")
    expected_nodes = _d3_projected_nodes_v02(
        topology,
        all_nodes,
        cell_depth=cell_depth,
        parent_cell_id=parent_cell_id,
    )
    if type(projected_nodes) is not tuple or projected_nodes != expected_nodes:
        raise ValueError("g2d_node_instance_geometry_invalid")
    if type(planned_child_cell_ids) is not tuple or not _unique_tuple(planned_child_cell_ids):
        raise ValueError("g2d_child_cell_identity_invalid")
    if parent_cell_id is None:
        expected_budget = _d3_root_cell_create_budget_v02(source_context, topology)
        if (
            cell_id != topology.root_cell_id
            or cell_depth != 0
            or scope_ref != topology.accepted_scope_ref
            or parent_slot_artifact is not None
            or cell_instantiation_order != (topology.root_cell_id,)
            or cell_budget != expected_budget
            or global_budget != expected_budget
            or settled_budget_log[-1] != expected_budget
            or len(settled_budget_log) != 3
            or settled_queue_entry_log
            or settled_queue_artifact_log
            or settled_cell_inputs
            or settled_scope_projections
            or settled_revise_observations
            or settled_backpressure_states
            or planned_child_cell_ids
            != _d3_planned_child_ids_from_sources_v02(source_context, topology)
        ):
            raise ValueError("g2d_queue_entry_invalid")
    else:
        if (
            topology.accepted_mode != "full_fractal"
            or cell_id == topology.root_cell_id
            or parent_cell_id not in cell_instantiation_order[:-1]
            or planned_child_cell_ids != ()
            or type(parent_slot_artifact) is not KernelArtifactV01
            or scope_ref not in (
                topology.accepted_scope_ref,
                *source_context.runtime_policy.permitted_child_scope_refs,
            )
        ):
            raise ValueError("g2d_child_slot_activation_invalid")
        _d3_validate_parent_slot_artifact_v02(
            parent_slot_artifact,
            topology=topology,
            parent_cell_id=parent_cell_id,
            child_cell_id=cell_id,
        )
        _d3_validate_parent_slot_chain_v02(
            parent_slot_artifact=parent_slot_artifact,
            parent_cell_id=parent_cell_id,
            child_cell_id=cell_id,
            topology=topology,
            indexes=indexes,
        )
        projection_by_child = indexes["projection_by_child"]
        input_by_cell = indexes["input_by_cell"]
        if (
            not isinstance(projection_by_child, dict)
            or not isinstance(input_by_cell, dict)
            or cell_id not in projection_by_child
            or parent_cell_id not in input_by_cell
            or len(settled_budget_log) < 5
            or tuple(item.budget_event_kind for item in settled_budget_log[-5:])
            != (
                "INITIAL_ALLOCATION",
                "ACTIVATE",
                "ACTIVATE",
                "CELL_CREATE",
                "CELL_CREATE",
            )
            or settled_budget_log[-2] != cell_budget
            or settled_budget_log[-1] != global_budget
        ):
            raise ValueError("g2d_child_slot_activation_invalid")
        for budget in (cell_budget, global_budget):
            if validate_fractal_runtime_budget_v02(budget).status != "PASS":
                raise ValueError("g2d_budget_invalid")
        if (
            cell_budget.owning_cell_id != cell_id
            or cell_budget.budget_scope != "CHILD_CELL_LOCAL"
            or cell_budget.budget_state != "ACTIVE"
            or cell_budget.budget_event_kind != "CELL_CREATE"
            or cell_budget.budget_event_ref != cell_id
            or cell_budget.consumed_cell_count != 1
            or global_budget.owning_cell_id != topology.root_cell_id
            or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
            or global_budget.budget_state != "ACTIVE"
            or global_budget.budget_event_kind != "CELL_CREATE"
            or global_budget.budget_event_ref != cell_id
            or cell_budget.policy_id != source_context.runtime_policy.policy_id
            or global_budget.policy_id != source_context.runtime_policy.policy_id
            or cell_budget.topology_seed_id != topology.topology_seed_id
            or global_budget.topology_seed_id != topology.topology_seed_id
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
    expected_t02 = _d3_transition_decision_v02(
        registry,
        "t02",
    )
    if (
        type(admission_decisions) is not tuple
        or len(admission_decisions) != len(projected_nodes)
        or any(item != expected_t02 for item in admission_decisions)
    ):
        raise ValueError("g2d_transition_decision_substituted")
    projected_node_ids = tuple(item.node_id for item in projected_nodes)
    built: list[FractalCellQueueEntryV02] = []
    cell_ordinal = cell_instantiation_order.index(cell_id)
    for index, (node, decision) in enumerate(zip(projected_nodes, admission_decisions, strict=True)):
        planned_child = None
        if parent_cell_id is None and node.node_kind == "FRACTAL_CELL":
            slot = node.canonical_index - 1
            if not 0 <= slot < len(planned_child_cell_ids):
                raise ValueError("g2d_child_slot_activation_invalid")
            planned_child = planned_child_cell_ids[slot]
        entry = build_fractal_cell_queue_entry_v02(
            topology,
            seed,
            None,
            node,
            cell_budget,
            global_budget,
            cell_id=cell_id,
            parent_cell_id=parent_cell_id,
            planned_child_cell_id=planned_child,
            cell_depth=cell_depth,
            scope_ref=scope_ref,
            predecessor=None,
            transition_decision=decision,
            activation_parent_artifact=parent_slot_artifact,
            local_child_result=None,
            local_child_result_artifact=None,
            cell_instantiation_order=cell_instantiation_order,
            projected_node_ids=projected_node_ids,
            round_start_queue_entries=tuple(built),
            queue_reason_codes=(),
            observed_output_refs=(),
            observed_evidence_refs=(),
            advisory_refs=(),
        )
        expected_sequence = cell_ordinal * len(topology.ordered_node_ids) + index
        if entry.node_instance_sequence != expected_sequence:
            entry = _finish_identity(
                _replace(entry, node_instance_sequence=expected_sequence)
            )
        if validate_fractal_cell_queue_entry_v02(entry).status != "PASS":
            raise ValueError("g2d_queue_entry_invalid")
        built.append(entry)
    return tuple(built)


def advance_fractal_cell_queue_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    current_entry: FractalCellQueueEntryV02,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02,
    transition_decision: TransitionDecisionV01,
    cell_budget_after: FractalRuntimeBudgetV02,
    global_budget_after: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    local_child_result: FractalCellResultV02 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    cell_instantiation_order: tuple[str, ...],
    projected_node_ids: tuple[str, ...],
    round_start_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...],
    observed_output_refs: tuple[str, ...],
    observed_evidence_refs: tuple[str, ...],
    advisory_refs: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalCellQueueEntryV02:
    _binding, seed, _initial, nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    rule = _short_rule_id(transition_decision)
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
        frontier="T03_QUEUE_ADVANCE" if rule == "t03" else "QUEUE_ADVANCE",
    )
    latest_by_key = indexes["latest_by_key"]
    budget_by_id = indexes["budget_by_id"]
    input_by_id = indexes["input_by_id"]
    if (
        not isinstance(latest_by_key, dict)
        or not isinstance(budget_by_id, dict)
        or not isinstance(input_by_id, dict)
        or latest_by_key.get((current_entry.cell_id, current_entry.node_id)) != current_entry
        or input_by_id.get(cell_input.cell_input_id) != cell_input
        or budget_by_id.get(current_entry.cell_budget_id) is None
        or budget_by_id.get(current_entry.global_budget_id) is None
    ):
        raise ValueError("g2d_queue_predecessor_invalid")
    if rule == "t03":
        queue_by_id = indexes["queue_by_id"]
        if (
            not settled_backpressure_states
            or not isinstance(queue_by_id, dict)
            or _d3_next_t03_source_id_v02(
                state=settled_backpressure_states[-1],
                queue_entries=settled_queue_entry_log,
                queue_by_id=queue_by_id,
            )
            != current_entry.queue_entry_id
        ):
            raise ValueError("g2d_backpressure_invalid")
    if (
        validate_fractal_cell_queue_entry_v02(current_entry).status != "PASS"
        or validate_fractal_cell_input_v02(cell_input).status != "PASS"
        or node not in nodes
        or current_entry.node_id != node.node_id
        or current_entry.cell_id != cell_input.cell_id
        or current_entry.topology_id != topology.topology_id
        or cell_input.topology_id != topology.topology_id
        or current_entry not in round_start_queue_entries
        or current_entry.queue_entry_id
        != next(
            (
                item.queue_entry_id
                for item in reversed(round_start_queue_entries)
                if (item.cell_id, item.node_id) == (current_entry.cell_id, current_entry.node_id)
            ),
            None,
        )
    ):
        raise ValueError("g2d_queue_predecessor_invalid")
    expected_rule_id = {
        "t03": ("PENDING", "PENDING"),
        "t04": ("PENDING", "READY"),
        "t05": ("READY", "RUNNING"),
        "t06": ("RUNNING", "VALIDATING"),
        "t07": ("VALIDATING", "READY"),
        "t08": ("VALIDATING", "COMPLETED"),
        "t09": ("VALIDATING", "DEGRADED"),
        "t10": ("VALIDATING", "BLOCKED"),
        "t11": ("VALIDATING", "NEEDS_USER"),
        "t12": ("VALIDATING", "DEADEND"),
    }[rule]
    if current_entry.state != expected_rule_id[0]:
        raise ValueError("g2d_queue_transition_illegal")
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    expected_decision = _d3_transition_decision_v02(
        registry,
        next(
            rule_id
            for (prior, state), rule_id in _D3_RULE_BY_STATE_PAIR_V02.items()
            if (prior, state) == expected_rule_id
        ),
    )
    if transition_decision != expected_decision:
        raise ValueError("g2d_transition_decision_substituted")
    for budget in (cell_budget_after, global_budget_after):
        if validate_fractal_runtime_budget_v02(budget).status != "PASS":
            raise ValueError("g2d_budget_invalid")
        if budget_by_id.get(budget.budget_id) != budget:
            raise ValueError("g2d_budget_predecessor_invalid")
    _d3_validate_queue_advance_budget_frontier_v02(
        rule_id=rule,
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        current_entry=current_entry,
        cell_budget_after=cell_budget_after,
        global_budget_after=global_budget_after,
        transition_decision=transition_decision,
        settled_budget_log=settled_budget_log,
        indexes=indexes,
    )
    if not _d3_dependencies_satisfied_v02(
        topology,
        node,
        cell_id=current_entry.cell_id,
        cell_depth=current_entry.cell_depth,
        dependencies=dependencies,
    ):
        raise ValueError("g2d_queue_order_mismatch")
    result = build_fractal_cell_queue_entry_v02(
        topology,
        seed,
        cell_input,
        node,
        cell_budget_after,
        global_budget_after,
        cell_id=current_entry.cell_id,
        parent_cell_id=current_entry.parent_cell_id,
        planned_child_cell_id=current_entry.planned_child_cell_id,
        cell_depth=current_entry.cell_depth,
        scope_ref=current_entry.scope_ref,
        predecessor=current_entry,
        transition_decision=transition_decision,
        activation_parent_artifact=None,
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        cell_instantiation_order=cell_instantiation_order,
        projected_node_ids=projected_node_ids,
        round_start_queue_entries=round_start_queue_entries,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
    )
    if (
        result.prior_state != current_entry.state
        or result.predecessor_queue_entry_id != current_entry.queue_entry_id
        or result.snapshot_sequence != current_entry.snapshot_sequence + 1
        or result.state != expected_rule_id[1]
        or validate_fractal_cell_queue_entry_v02(result).status != "PASS"
    ):
        raise ValueError("g2d_queue_sequence_invalid")
    if rule == "t03" and not _d3_t03_target_matches_source_v02(
        result,
        current_entry,
        state=settled_backpressure_states[-1],
        expected_decision=transition_decision,
    ):
        raise ValueError("g2d_backpressure_invalid")
    return result


def project_parent_child_scope_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    parent_input: FractalCellInputV02,
    child_cell_id: str,
    child_scope_ref: str,
    parent_budget: FractalRuntimeBudgetV02,
    child_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
) -> ParentChildScopeProjectionV02:
    source_binding, _seed, _initial, _nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    if (
        validate_fractal_cell_input_v02(parent_input).status != "PASS"
        or parent_input.topology_id != topology.topology_id
        or child_cell_id not in parent_input.ordered_planned_child_cell_ids
        or parent_budget.budget_id != parent_input.cell_budget_id
        or validate_fractal_runtime_budget_v02(parent_budget).status != "PASS"
        or validate_fractal_runtime_budget_v02(child_budget).status != "PASS"
        or validate_fractal_runtime_budget_v02(global_budget).status != "PASS"
    ):
        raise ValueError("g2d_child_lineage_mismatch")
    child_depth = parent_input.cell_depth + 1
    if child_depth >= source_context.runtime_policy.max_depth:
        raise ValueError("g2d_depth_limit_exceeded")
    if (
        child_budget.owning_cell_id != child_cell_id
        or child_budget.budget_scope != "CHILD_CELL_LOCAL"
        or child_budget.budget_state != "ALLOCATED"
        or child_budget.budget_event_kind != "INITIAL_ALLOCATION"
        or child_budget.allocation_parent_budget_id != parent_budget.budget_id
        or child_budget.predecessor_budget_id is not None
        or global_budget.owning_cell_id != topology.root_cell_id
        or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
        or global_budget.budget_state != "ACTIVE"
    ):
        raise ValueError("g2d_budget_event_pair_mismatch")
    if child_scope_ref != parent_input.scope_ref and (
        child_scope_ref not in source_binding.permitted_narrower_scope_refs
        or child_scope_ref not in source_context.runtime_policy.permitted_child_scope_refs
    ):
        raise ValueError("g2d_scope_relation_unproven")
    remaining = (
        parent_budget.remaining_cell_count,
        parent_budget.remaining_revise_count,
        parent_budget.remaining_wall_time_units,
        parent_budget.remaining_token_budget,
        parent_budget.remaining_provider_calls,
    )
    child_maxima = (
        child_budget.max_total_cells,
        child_budget.max_revise_count,
        child_budget.max_wall_time_units,
        child_budget.max_token_budget,
        child_budget.max_provider_calls,
    )
    if any(child > parent for child, parent in zip(child_maxima, remaining, strict=True)):
        raise ValueError("g2d_child_budget_widening")
    ttl = source_context.router_input.local_routing_snapshot.ttl_seconds
    result = build_parent_child_scope_projection_v02(
        topology,
        source_binding,
        parent_cell_id=parent_input.cell_id,
        child_cell_id=child_cell_id,
        parent_scope_ref=parent_input.scope_ref,
        child_scope_ref=child_scope_ref,
        parent_allowed_capability_ids=source_context.runtime_policy.allowed_capability_ids,
        child_allowed_capability_ids=source_context.runtime_policy.allowed_capability_ids,
        parent_forbidden_claims=source_context.runtime_policy.forbidden_claims,
        child_forbidden_claims=source_context.runtime_policy.forbidden_claims,
        parent_ttl_units=ttl,
        child_ttl_units=ttl,
        parent_budget=parent_budget,
        child_budget=child_budget,
        global_budget=global_budget,
        child_depth=child_depth,
    )
    if validate_parent_child_scope_projection_v02(result).status != "PASS":
        raise ValueError("g2d_child_lineage_mismatch")
    return result


def validate_parent_child_scope_against_sources_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    parent_input: FractalCellInputV02,
    parent_budget: FractalRuntimeBudgetV02,
    child_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
) -> FractalRuntimeValidationReportV02:
    try:
        structural = validate_parent_child_scope_projection_v02(value).status == "PASS"
        expected = project_parent_child_scope_v02(
            source_context=source_context,
            topology=topology,
            parent_input=parent_input,
            child_cell_id=value.child_cell_id,
            child_scope_ref=value.child_scope_ref,
            parent_budget=parent_budget,
            child_budget=child_budget,
            global_budget=global_budget,
        )
        valid = bool(
            structural
            and type(value) is ParentChildScopeProjectionV02
            and value == expected
            and _canonical_json_bytes_v01(parent_child_scope_projection_to_plain_data_v02(value))
            == _canonical_json_bytes_v01(parent_child_scope_projection_to_plain_data_v02(expected))
        )
        return build_fractal_runtime_validation_report_v02(
            validation_target="SCOPE_PROJECTION_AGAINST_SOURCES",
            validated_object_id=value.projection_id if valid else None,
            failure_stage="NONE" if valid else "SCOPE",
            reason_codes=() if valid else ("g2d_child_lineage_mismatch",),
            source_reason_codes=(),
        )
    except Exception:
        return build_fractal_runtime_validation_report_v02(
            validation_target="SCOPE_PROJECTION_AGAINST_SOURCES",
            validated_object_id=None,
            failure_stage="SCOPE",
            reason_codes=("g2d_child_lineage_mismatch",),
            source_reason_codes=(),
        )


def _d3_expected_cell_input_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    cell_id: str,
    parent_cell_id: str | None,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    initial_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    initial_queue_artifacts: tuple[KernelArtifactV01, ...],
    ordered_planned_child_cell_ids: tuple[str, ...],
) -> FractalCellInputV02:
    source_binding, _seed, _initial, all_nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    if topology_artifact != _build_topology_artifact_v02(topology, source_context):
        raise ValueError("g2d_abi_projection_substituted")
    if (
        type(initial_queue_entries) is not tuple
        or type(initial_queue_artifacts) is not tuple
        or len(initial_queue_entries) != len(initial_queue_artifacts)
        or any(type(item) is not FractalCellQueueEntryV02 for item in initial_queue_entries)
        or any(type(item) is not KernelArtifactV01 for item in initial_queue_artifacts)
    ):
        raise ValueError("g2d_cell_input_build_order_invalid")
    parent = initial_queue_entries[0].parent_cell_id if initial_queue_entries else parent_cell_id
    depth = initial_queue_entries[0].cell_depth if initial_queue_entries else 0
    expected_nodes = _d3_projected_nodes_v02(
        topology,
        all_nodes,
        cell_depth=depth,
        parent_cell_id=parent,
    )
    if (
        not initial_queue_entries
        or tuple(item.node_id for item in initial_queue_entries)
        != tuple(item.node_id for item in expected_nodes)
        or any(
            item.cell_id != cell_id
            or item.parent_cell_id != parent_cell_id
            or item.state != "PENDING"
            or item.prior_state is not None
            or item.predecessor_queue_entry_id is not None
            or item.snapshot_sequence != 0
            or item.admission_round != 0
            for item in initial_queue_entries
        )
    ):
        raise ValueError("g2d_cell_input_build_order_invalid")
    for entry, artifact in zip(initial_queue_entries, initial_queue_artifacts, strict=True):
        parent_refs = (
            (topology_artifact.artifact_id,)
            if parent_cell_id is None
            else (topology_artifact.artifact_id, parent_slot_artifact.artifact_id)
        )
        expected_artifact = _d3_build_queue_artifact_v02(
            entry,
            parent_refs=parent_refs,
            source_context=source_context,
        )
        if artifact != expected_artifact:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
    base_evidence = (
        source_context.proposal_artifact.artifact_id,
        source_context.decision_artifact.artifact_id,
        source_context.route_eligibility_artifact.artifact_id,
    )
    base_context = (
        source_binding.source_binding_id,
        source_context.runtime_policy.policy_id,
        topology.topology_id,
        topology_artifact.artifact_id,
    )
    if parent_cell_id is None:
        if parent_input is not None or parent_slot_artifact is not None or scope_projection is not None:
            raise ValueError("g2d_cell_input_invalid")
        if cell_id != topology.root_cell_id:
            raise ValueError("g2d_cell_input_invalid")
        expected_planned = _d3_planned_child_ids_from_sources_v02(source_context, topology)
        if ordered_planned_child_cell_ids != expected_planned:
            raise ValueError("g2d_child_cell_identity_invalid")
        evidence_refs = base_evidence + tuple(item.artifact_id for item in initial_queue_artifacts)
        context_refs = base_context
        scope_ref = topology.accepted_scope_ref
    else:
        if (
            type(parent_input) is not FractalCellInputV02
            or type(parent_slot_artifact) is not KernelArtifactV01
            or type(scope_projection) is not ParentChildScopeProjectionV02
            or ordered_planned_child_cell_ids != ()
            or scope_projection.parent_cell_id != parent_cell_id
            or scope_projection.child_cell_id != cell_id
            or cell_budget.owning_cell_id != cell_id
            or cell_budget.budget_event_kind != "CELL_CREATE"
            or global_budget.budget_event_kind != "CELL_CREATE"
        ):
            raise ValueError("g2d_cell_input_invalid")
        _d3_validate_parent_slot_artifact_v02(
            parent_slot_artifact,
            topology=topology,
            parent_cell_id=parent_cell_id,
            child_cell_id=cell_id,
        )
        slot_outputs = tuple(_d3_queue_artifact_payload_ref_v02(parent_slot_artifact, "observed_output_refs"))
        slot_evidence = tuple(_d3_queue_artifact_payload_ref_v02(parent_slot_artifact, "observed_evidence_refs"))
        evidence_refs = base_evidence + (
            parent_input.cell_input_id,
            parent_slot_artifact.artifact_id,
            scope_projection.projection_id,
            *slot_outputs,
            *slot_evidence,
            *(item.artifact_id for item in initial_queue_artifacts),
        )
        context_refs = base_context + (
            parent_input.cell_input_id,
            parent_slot_artifact.artifact_id,
            scope_projection.projection_id,
        )
        scope_ref = scope_projection.child_scope_ref
    return build_fractal_cell_input_v02(
        topology,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        scope_projection=scope_projection,
        scope_ref=scope_ref,
        cell_budget=cell_budget,
        global_budget=global_budget,
        initial_queue_entries=initial_queue_entries,
        required_queue_entries=initial_queue_entries,
        cell_depth=depth,
        requested_child_count=len(ordered_planned_child_cell_ids),
        ordered_planned_child_cell_ids=ordered_planned_child_cell_ids,
        ordered_nodes=expected_nodes,
        evidence_refs=evidence_refs,
        context_refs=context_refs,
        time_envelope_ref=topology.time_envelope_ref,
    )


def _d3_validate_cell_input_against_validated_prefix_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
) -> FractalRuntimeValidationReportV02:
    try:
        if type(value) is not FractalCellInputV02:
            raise ValueError("g2d_cell_input_invalid")
        expected = _d3_expected_cell_input_v02(
            source_context=source_context,
            topology=topology,
            topology_artifact=topology_artifact,
            cell_id=value.cell_id,
            parent_cell_id=value.parent_cell_id,
            parent_input=parent_input,
            parent_slot_artifact=parent_slot_artifact,
            scope_projection=scope_projection,
            cell_budget=cell_budget,
            global_budget=global_budget,
            initial_queue_entries=queue_entries,
            initial_queue_artifacts=queue_artifacts,
            ordered_planned_child_cell_ids=value.ordered_planned_child_cell_ids,
        )
        valid = bool(
            validate_fractal_cell_input_v02(value).status == "PASS"
            and value == expected
            and _canonical_json_bytes_v01(
                fractal_cell_input_to_plain_data_v02(value)
            )
            == _canonical_json_bytes_v01(
                fractal_cell_input_to_plain_data_v02(expected)
            )
        )
        return build_fractal_runtime_validation_report_v02(
            validation_target="CELL_INPUT_AGAINST_SOURCES",
            validated_object_id=value.cell_input_id if valid else None,
            failure_stage="NONE" if valid else "CELL_INPUT",
            reason_codes=() if valid else ("g2d_cell_input_invalid",),
            source_reason_codes=(),
        )
    except Exception:
        return build_fractal_runtime_validation_report_v02(
            validation_target="CELL_INPUT_AGAINST_SOURCES",
            validated_object_id=None,
            failure_stage="CELL_INPUT",
            reason_codes=("g2d_cell_input_invalid",),
            source_reason_codes=(),
        )


def build_fractal_cell_input_from_queue_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    cell_id: str,
    parent_cell_id: str | None,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    initial_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    initial_queue_artifacts: tuple[KernelArtifactV01, ...],
    ordered_planned_child_cell_ids: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalCellInputV02:
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
    )
    input_by_cell = indexes["input_by_cell"]
    budget_by_id = indexes["budget_by_id"]
    projection_by_child = indexes["projection_by_child"]
    if (
        not isinstance(input_by_cell, dict)
        or not isinstance(budget_by_id, dict)
        or not isinstance(projection_by_child, dict)
        or cell_id in input_by_cell
        or budget_by_id.get(cell_budget.budget_id) != cell_budget
        or budget_by_id.get(global_budget.budget_id) != global_budget
        or tuple(
            item for item in settled_queue_entry_log if item.cell_id == cell_id
        )
        != initial_queue_entries
        or tuple(
            artifact
            for entry, artifact in zip(
                settled_queue_entry_log,
                settled_queue_artifact_log,
                strict=True,
            )
            if entry.cell_id == cell_id
        )
        != initial_queue_artifacts
    ):
        raise ValueError("g2d_cell_input_build_order_invalid")
    if parent_cell_id is not None:
        if (
            type(parent_slot_artifact) is not KernelArtifactV01
            or projection_by_child.get(cell_id) != scope_projection
        ):
            raise ValueError("g2d_child_lineage_mismatch")
        _d3_validate_parent_slot_chain_v02(
            parent_slot_artifact=parent_slot_artifact,
            parent_cell_id=parent_cell_id,
            child_cell_id=cell_id,
            topology=topology,
            indexes=indexes,
        )
    result = _d3_expected_cell_input_v02(
        source_context=source_context,
        topology=topology,
        topology_artifact=topology_artifact,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        parent_input=parent_input,
        parent_slot_artifact=parent_slot_artifact,
        scope_projection=scope_projection,
        cell_budget=cell_budget,
        global_budget=global_budget,
        initial_queue_entries=initial_queue_entries,
        initial_queue_artifacts=initial_queue_artifacts,
        ordered_planned_child_cell_ids=ordered_planned_child_cell_ids,
    )
    if validate_fractal_cell_input_v02(result).status != "PASS":
        raise ValueError("g2d_cell_input_invalid")
    return result


def validate_fractal_cell_input_against_sources_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalRuntimeValidationReportV02:
    try:
        indexes = _d3_validate_settled_runtime_prefix_v02(
            topology=topology,
            policy=source_context.runtime_policy,
            source_context=source_context,
            settled_budget_log=settled_budget_log,
            settled_queue_entry_log=settled_queue_entry_log,
            settled_queue_artifact_log=settled_queue_artifact_log,
            settled_cell_inputs=settled_cell_inputs,
            settled_scope_projections=settled_scope_projections,
            settled_revise_observations=settled_revise_observations,
            settled_backpressure_states=settled_backpressure_states,
            settled_validation_reports=settled_validation_reports,
        )
        input_by_cell = indexes["input_by_cell"]
        budget_by_id = indexes["budget_by_id"]
        if (
            not isinstance(input_by_cell, dict)
            or not isinstance(budget_by_id, dict)
            or type(value) is not FractalCellInputV02
            or value.cell_id in input_by_cell
            or budget_by_id.get(cell_budget.budget_id) != cell_budget
            or budget_by_id.get(global_budget.budget_id) != global_budget
        ):
            raise ValueError("g2d_cell_input_invalid")
        return _d3_validate_cell_input_against_validated_prefix_v02(
            value,
            source_context=source_context,
            topology=topology,
            topology_artifact=topology_artifact,
            parent_input=parent_input,
            parent_slot_artifact=parent_slot_artifact,
            scope_projection=scope_projection,
            cell_budget=cell_budget,
            global_budget=global_budget,
            queue_entries=queue_entries,
            queue_artifacts=queue_artifacts,
        )
    except Exception:
        return build_fractal_runtime_validation_report_v02(
            validation_target="CELL_INPUT_AGAINST_SOURCES",
            validated_object_id=None,
            failure_stage="CELL_INPUT",
            reason_codes=("g2d_cell_input_invalid",),
            source_reason_codes=(),
        )


def _d3_admission_key_v02(value: FractalCellQueueEntryV02) -> tuple[object, ...]:
    return (
        value.canonical_priority,
        value.cell_depth,
        value.node_instance_sequence,
        value.cell_id,
        value.node_id,
    )


def _d3_latest_queue_entries_v02(
    entries: tuple[FractalCellQueueEntryV02, ...],
    *,
    maximum_round: int | None = None,
) -> tuple[FractalCellQueueEntryV02, ...]:
    latest: dict[tuple[str, str], FractalCellQueueEntryV02] = {}
    for entry in entries:
        if maximum_round is not None and entry.admission_round > maximum_round:
            continue
        latest[(entry.cell_id, entry.node_id)] = entry
    return tuple(
        entry
        for entry in entries
        if latest.get((entry.cell_id, entry.node_id)) == entry
    )


def _d3_dependencies_for_latest_entry_v02(
    entry: FractalCellQueueEntryV02,
    *,
    topology: RuntimeExecutionTopologyV02,
    latest_by_key: dict[tuple[str, str], FractalCellQueueEntryV02],
) -> tuple[FractalCellQueueEntryV02 | None, ...]:
    node_index = topology.ordered_node_ids.index(entry.node_id)
    projection = (
        "ROOT_CELL_PROJECTION"
        if entry.cell_depth == 0
        else "FRACTAL_LEAF_PROJECTION"
    )
    incoming = tuple(
        row
        for row in dict(MODE_EDGE_TEMPLATE_ROWS_V02)[topology.accepted_mode]
        if row[1] == projection and row[3] == node_index
    )
    return tuple(
        latest_by_key.get((entry.cell_id, topology.ordered_node_ids[row[2]]))
        for row in incoming
    )


def _d3_order_classified_scheduler_entries_v02(
    classified: tuple[tuple[str, FractalCellQueueEntryV02], ...],
) -> tuple[tuple[str, FractalCellQueueEntryV02], ...]:
    if (
        type(classified) is not tuple
        or any(
            type(item) is not tuple
            or len(item) != 2
            or item[0] not in _D3_STATE_CLASS_ORDER_V02
            or type(item[1]) is not FractalCellQueueEntryV02
            or item[1].state
            != {
                "READY": "READY",
                "RUNNING": "RUNNING",
                "VALIDATING_TERMINAL": "VALIDATING",
                "VALIDATING_REVISE": "VALIDATING",
                "PENDING_READY": "PENDING",
                "PENDING_DEFERRED": "PENDING",
            }[item[0]]
            for item in classified
        )
        or len({(item[1].cell_id, item[1].node_id) for item in classified})
        != len(classified)
    ):
        raise ValueError("g2d_queue_order_mismatch")
    return tuple(
        sorted(
            classified,
            key=lambda item: (
                _D3_STATE_CLASS_ORDER_V02.index(item[0]),
                *_d3_admission_key_v02(item[1]),
            ),
        )
    )


def _d3_instantiated_child_v02(
    current_entry: FractalCellQueueEntryV02,
    *,
    indexes: dict[str, object],
) -> tuple[ParentChildScopeProjectionV02, FractalCellInputV02] | None:
    child_id = current_entry.planned_child_cell_id
    if child_id is None:
        raise ValueError("g2d_child_slot_activation_invalid")
    projection_by_child = indexes.get("projection_by_child")
    input_by_cell = indexes.get("input_by_cell")
    queue_by_id = indexes.get("queue_by_id")
    if not all(
        isinstance(item, dict)
        for item in (projection_by_child, input_by_cell, queue_by_id)
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    projection = projection_by_child.get(child_id)
    child_input = input_by_cell.get(child_id)
    if (projection is None) != (child_input is None):
        raise ValueError("g2d_child_lineage_mismatch")
    if projection is None:
        return None
    if (
        type(projection) is not ParentChildScopeProjectionV02
        or type(child_input) is not FractalCellInputV02
        or projection.child_cell_id != child_id
        or projection.parent_cell_id != current_entry.cell_id
        or child_input.cell_id != child_id
        or child_input.parent_cell_id != current_entry.cell_id
        or child_input.scope_projection_id != projection.projection_id
        or child_input.scope_ref != projection.child_scope_ref
        or child_input.cell_depth != current_entry.cell_depth + 1
        or any(
            queue_by_id.get(item) is None
            for item in child_input.ordered_initial_queue_entry_ids
        )
    ):
        raise ValueError("g2d_child_lineage_mismatch")
    return projection, child_input


def _d3_scheduler_classification_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    global_budget: FractalRuntimeBudgetV02,
    entries: tuple[FractalCellQueueEntryV02, ...],
    indexes: dict[str, object],
) -> dict[str, object]:
    latest = _d3_latest_queue_entries_v02(entries)
    latest_by_key = {(item.cell_id, item.node_id): item for item in latest}
    queue_by_id = indexes.get("queue_by_id")
    artifact_by_queue_id = indexes.get("artifact_by_queue_id")
    input_by_cell = indexes.get("input_by_cell")
    revise_by_id = indexes.get("revise_by_id")
    if not all(
        isinstance(item, dict)
        for item in (queue_by_id, artifact_by_queue_id, input_by_cell, revise_by_id)
    ):
        raise ValueError("g2d_backpressure_invalid")
    _root_cell_head, indexed_global_head = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=topology.root_cell_id,
        indexes=indexes,
    )
    if (
        tuple(queue_by_id.values()) != entries
        or tuple(artifact_by_queue_id) != tuple(item.queue_entry_id for item in entries)
        or global_budget != indexed_global_head
    ):
        raise ValueError("g2d_backpressure_invalid")
    for entry in entries:
        _d3_validate_queue_budget_anchors_v02(
            entry,
            topology=topology,
            indexes=indexes,
        )
    running = global_budget.current_parallelism
    actual_running = sum(item.state == "RUNNING" for item in latest)
    ready = sum(item.state == "READY" for item in latest)
    occupied = running + ready
    residual = policy.max_parallelism - occupied
    if actual_running != running or residual < 0:
        raise ValueError("g2d_parallelism_limit_exceeded")

    nodes_by_id = {
        node.node_id: node
        for node in _d3_reconstruct_topology_parts_v02(
            source_context,
            topology,
        )[3]
    }
    dependencies_by_id = {
        entry.queue_entry_id: _d3_dependencies_for_latest_entry_v02(
            entry,
            topology=topology,
            latest_by_key=latest_by_key,
        )
        for entry in latest
    }
    pending = tuple(
        sorted(
            (
                entry
                for entry in latest
                if entry.state == "PENDING"
                and nodes_by_id[entry.node_id].node_kind != "PARENT_RETURN"
                and all(
                    dependency is not None
                    and dependency.state in _D3_TERMINAL_STATES_V02
                    for dependency in dependencies_by_id[entry.queue_entry_id]
                )
            ),
            key=_d3_admission_key_v02,
        )
    )
    pending_ready_ids = {
        item.queue_entry_id for item in pending[:residual]
    }
    pending_deferred_ids = {
        item.queue_entry_id for item in pending[residual:]
    }
    classified: list[tuple[str, FractalCellQueueEntryV02]] = []
    future_progress: list[FractalCellQueueEntryV02] = []
    for entry in latest:
        scheduler_class: str | None = None
        node = nodes_by_id[entry.node_id]
        dependencies = tuple(
            dependency
            for dependency in dependencies_by_id[entry.queue_entry_id]
            if dependency is not None
        )
        if entry.state == "READY":
            scheduler_class = "READY"
        elif entry.state == "RUNNING":
            if node.node_kind in _D3_LOCAL_NODE_KINDS_V02:
                live_cell, live_global = _d3_live_budget_heads_v02(
                    topology=topology,
                    cell_id=entry.cell_id,
                    indexes=indexes,
                )
                try:
                    _d3_local_observation_material_v02(
                        source_context=source_context,
                        topology=topology,
                        node=node,
                        cell_input=input_by_cell[entry.cell_id],
                        cell_budget_before=live_cell,
                        global_budget_before=live_global,
                        dependencies=dependencies,
                        indexes=indexes,
                    )
                    scheduler_class = "RUNNING"
                except (KeyError, TypeError, ValueError):
                    scheduler_class = None
            elif node.node_kind == "FRACTAL_CELL":
                try:
                    if _d3_instantiated_child_v02(entry, indexes=indexes) is None:
                        live_cell, live_global = _d3_live_budget_heads_v02(
                            topology=topology,
                            cell_id=entry.cell_id,
                            indexes=indexes,
                        )
                        material = _d3_child_activation_precheck_material_v02(
                            source_context=source_context,
                            topology=topology,
                            source_artifact=artifact_by_queue_id[entry.queue_entry_id],
                            current_entry=entry,
                            node=node,
                            cell_input=input_by_cell[entry.cell_id],
                            cell_budget_before=live_cell,
                            global_budget_before=live_global,
                            dependencies=dependencies,
                            indexes=indexes,
                        )
                        if material["derived_disposition"] != "PASS_FOR_CHILD_ACTIVATION":
                            scheduler_class = "RUNNING"
                except (KeyError, TypeError, ValueError):
                    scheduler_class = None
            if scheduler_class is None:
                future_progress.append(entry)
        elif entry.state == "VALIDATING":
            matching_revise = tuple(
                observation
                for observation in revise_by_id.values()
                if observation.queue_entry_id == entry.queue_entry_id
                and observation.cell_id == entry.cell_id
            )
            if len(matching_revise) > 1:
                raise ValueError("g2d_revise_observation_invalid")
            if matching_revise and matching_revise[0].revise_eligible:
                observation = matching_revise[0]
                report = validate_fractal_revise_observation_v02(observation)
                if (
                    report.status != "PASS"
                    or observation.cell_budget_before_id not in indexes["budget_by_id"]
                    or observation.global_budget_before_id not in indexes["budget_by_id"]
                ):
                    raise ValueError("g2d_revise_observation_invalid")
                if residual > 0:
                    scheduler_class = "VALIDATING_REVISE"
                else:
                    future_progress.append(entry)
                if scheduler_class is not None:
                    classified.append((scheduler_class, entry))
                continue
            try:
                origin = _d3_t06_origin_frontier_v02(
                    topology=topology,
                    policy=policy,
                    source_context=source_context,
                    validating_entry=entry,
                    node=node,
                    settled_budget_log=tuple(indexes["budget_log"]),
                    settled_queue_entry_log=entries,
                    indexes=indexes,
                )
                if origin["dependencies"] != dependencies:
                    raise ValueError("g2d_queue_order_mismatch")
                terminal_available = False
                if node.node_kind in _D3_LOCAL_NODE_KINDS_V02:
                    local_material = _d3_local_observation_material_v02(
                        source_context=source_context,
                        topology=topology,
                        node=node,
                        cell_input=input_by_cell[entry.cell_id],
                        cell_budget_before=origin["cell_budget_before"],
                        global_budget_before=origin["global_budget_before"],
                        dependencies=dependencies,
                        indexes=indexes,
                    )
                    terminal_available = bool(
                        entry.queue_reason_codes
                        == local_material["derived_queue_reason_codes"]
                        and entry.observed_output_refs
                        == local_material["derived_observed_output_refs"]
                        and entry.observed_evidence_refs
                        == local_material["derived_observed_evidence_refs"]
                        and entry.advisory_refs
                        == local_material["derived_advisory_refs"]
                    )
                elif node.node_kind == "FRACTAL_CELL":
                    running_entry = origin["running_entry"]
                    if (
                        type(running_entry) is FractalCellQueueEntryV02
                        and _d3_instantiated_child_v02(
                            running_entry,
                            indexes=indexes,
                        )
                        is None
                    ):
                        gate = _d3_child_activation_precheck_material_v02(
                            source_context=source_context,
                            topology=topology,
                            source_artifact=origin["running_artifact"],
                            current_entry=running_entry,
                            node=node,
                            cell_input=input_by_cell[entry.cell_id],
                            cell_budget_before=origin["cell_budget_before"],
                            global_budget_before=origin["global_budget_before"],
                            dependencies=dependencies,
                            indexes=indexes,
                        )
                        terminal_available = gate["derived_disposition"] != (
                            "PASS_FOR_CHILD_ACTIVATION"
                        )
                if matching_revise and matching_revise[0].derived_terminal_state:
                    terminal_available = True
                if terminal_available:
                    scheduler_class = "VALIDATING_TERMINAL"
            except (KeyError, TypeError, ValueError):
                scheduler_class = None
            if scheduler_class is None:
                future_progress.append(entry)
        elif entry.queue_entry_id in pending_ready_ids:
            scheduler_class = "PENDING_READY"
        elif entry.queue_entry_id in pending_deferred_ids:
            scheduler_class = "PENDING_DEFERRED"
        if scheduler_class is not None:
            classified.append((scheduler_class, entry))
    ordered_classified = _d3_order_classified_scheduler_entries_v02(
        tuple(classified)
    )
    return {
        "latest": latest,
        "latest_by_key": latest_by_key,
        "dependencies_by_id": dependencies_by_id,
        "classified": ordered_classified,
        "admission_entries": tuple(item[1] for item in ordered_classified),
        "deferred": tuple(
            item[1]
            for item in ordered_classified
            if item[0] == "PENDING_DEFERRED"
        ),
        "eligible_pending": pending,
        "future_progress": tuple(
            sorted(future_progress, key=_d3_admission_key_v02)
        ),
        "running": running,
        "ready": ready,
        "occupied": occupied,
        "residual": residual,
    }


def _d3_round_control_material_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    global_budget: FractalRuntimeBudgetV02,
    admission_round: int,
    entries: tuple[FractalCellQueueEntryV02, ...],
    indexes: dict[str, object],
    prior_backpressure_states: tuple[FractalBackpressureStateV02, ...],
) -> dict[str, object]:
    artifact_by_queue_id = indexes["artifact_by_queue_id"]
    input_by_cell = indexes["input_by_cell"]
    projection_by_child = indexes["projection_by_child"]
    if (
        not isinstance(artifact_by_queue_id, dict)
        or not isinstance(input_by_cell, dict)
        or not isinstance(projection_by_child, dict)
    ):
        raise ValueError("g2d_backpressure_invalid")
    scheduler = _d3_scheduler_classification_v02(
        source_context=source_context,
        topology=topology,
        policy=policy,
        global_budget=global_budget,
        entries=entries,
        indexes={**indexes, "budget_log": indexes.get("budget_log", ())},
    )
    latest = scheduler["latest"]
    latest_by_key = scheduler["latest_by_key"]
    admission_entries = scheduler["admission_entries"]
    deferred = scheduler["deferred"]
    if not all(
        isinstance(item, tuple)
        for item in (latest, admission_entries, deferred)
    ) or not isinstance(latest_by_key, dict):
        raise ValueError("g2d_backpressure_invalid")
    future_entries = scheduler["future_progress"]
    if not isinstance(future_entries, tuple):
        raise ValueError("g2d_backpressure_invalid")
    partitioned_keys = {
        (item.cell_id, item.node_id)
        for item in (*admission_entries, *future_entries)
    }
    ordered_latest = (
        *admission_entries,
        *future_entries,
        *tuple(
            sorted(
                (
                    item
                    for item in latest
                    if (item.cell_id, item.node_id) not in partitioned_keys
                ),
                key=_d3_admission_key_v02,
            )
        ),
    )
    dependency_ids_by_key: list[list[object]] = []
    dependency_states_by_key: list[list[object]] = []
    activation_ids: list[str | None] = []
    for entry in ordered_latest:
        dependencies = scheduler["dependencies_by_id"][entry.queue_entry_id]
        dependency_ids_by_key.append(
            [
                None if dependency is None else dependency.queue_entry_id
                for dependency in dependencies
            ]
        )
        dependency_states_by_key.append(
            [None if dependency is None else dependency.state for dependency in dependencies]
        )
        activation_id = None
        if entry.parent_cell_id is not None and len(entry.lineage_refs) >= 8:
            activation_id = entry.lineage_refs[7]
        activation_ids.append(activation_id)
    running = scheduler["running"]
    ready = scheduler["ready"]
    occupied = scheduler["occupied"]
    residual = scheduler["residual"]
    eligible = scheduler["eligible_pending"]
    core: dict[str, object] = {
        "latest_cell_node_keys": [[item.cell_id, item.node_id] for item in ordered_latest],
        "latest_queue_entry_ids": [item.queue_entry_id for item in ordered_latest],
        "latest_queue_artifact_ids": [
            artifact_by_queue_id[item.queue_entry_id].artifact_id for item in ordered_latest
        ],
        "latest_states": [item.state for item in ordered_latest],
        "latest_snapshot_sequences": [item.snapshot_sequence for item in ordered_latest],
        "latest_admission_rounds": [item.admission_round for item in ordered_latest],
        "latest_predecessor_queue_entry_ids": [
            item.predecessor_queue_entry_id for item in ordered_latest
        ],
        "latest_cell_budget_ids": [item.cell_budget_id for item in ordered_latest],
        "latest_global_budget_ids": [item.global_budget_id for item in ordered_latest],
        "latest_cell_input_ids": [
            input_by_cell[item.cell_id].cell_input_id for item in ordered_latest
        ],
        "relevant_scope_projection_ids": [
            projection.projection_id
            for projection in projection_by_child.values()
            if projection.child_cell_id in {item.cell_id for item in ordered_latest}
        ],
        "dependency_occurrence_ids_by_key": dependency_ids_by_key,
        "dependency_states_by_key": dependency_states_by_key,
        "activation_parent_artifact_ids_by_key": activation_ids,
        "observed_output_tuples_by_key": [list(item.observed_output_refs) for item in ordered_latest],
        "observed_evidence_tuples_by_key": [list(item.observed_evidence_refs) for item in ordered_latest],
        "advisory_tuples_by_key": [list(item.advisory_refs) for item in ordered_latest],
        "queue_reason_tuples_by_key": [list(item.queue_reason_codes) for item in ordered_latest],
        "current_global_budget_id": global_budget.budget_id,
        "current_global_budget_counters": list(_d3_budget_counter_tuple_v02(global_budget)),
        "deterministic_admission_order": [item.queue_entry_id for item in admission_entries],
        "running_count": running,
        "ready_count": ready,
        "occupied_admission_slots": occupied,
        "residual_admission_slots": residual,
        "eligible_pending_queue_entry_ids": [item.queue_entry_id for item in eligible],
        "deferred_queue_entry_ids": [item.queue_entry_id for item in deferred],
        "future_progress_source_queue_entry_ids": [
            item.queue_entry_id
            for item in ordered_latest
            if item.state in {"READY", "RUNNING"}
            or item in scheduler["future_progress"]
        ],
    }
    control_core_sha256 = _domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_D3_ROUND_CONTROL_FINGERPRINT_CORE",
        payload=_canonical_json_bytes_v01(core),
    )
    return {
        "audit_envelope": {
            "profile_version": "v0.3.1",
            "topology_id": topology.topology_id,
            "policy_id": policy.policy_id,
            "admission_round": admission_round,
            "prior_backpressure_state_ids": [
                item.backpressure_id for item in prior_backpressure_states
            ],
        },
        "controlling_core": core,
        "control_core_sha256": control_core_sha256,
        "latest": ordered_latest,
        "deferred": deferred,
        "admission_entries": admission_entries,
    }


def evaluate_fractal_backpressure_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    global_budget: FractalRuntimeBudgetV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    admission_round: int,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalBackpressureStateV02 | None:
    if (
        type(source_context) is not FractalRuntimeSourceContextV02
        or validate_fractal_runtime_source_context_v02(source_context).status != "PASS"
        or policy != source_context.runtime_policy
        or _canonical_json_bytes_v01(fractal_runtime_policy_to_plain_data_v02(policy))
        != _canonical_json_bytes_v01(
            fractal_runtime_policy_to_plain_data_v02(source_context.runtime_policy)
        )
        or validate_runtime_execution_topology_against_sources_v02(
            topology,
            source_context=source_context,
        ).status
        != "PASS"
    ):
        raise ValueError("g2d_source_context_invalid")
    _require_valid(topology, RuntimeExecutionTopologyV02, "g2d_topology_identity_mismatch")
    _require_valid(policy, FractalRuntimePolicyV02, "g2d_topology_policy_invalid")
    _require_valid(global_budget, FractalRuntimeBudgetV02, "g2d_budget_invalid")
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
    )
    budget_by_id = indexes["budget_by_id"]
    _live_cell_budget, live_global_budget = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=topology.root_cell_id,
        indexes=indexes,
    )
    if (
        type(queue_entries) is not tuple
        or type(admission_round) is not int
        or admission_round < 0
        or not isinstance(budget_by_id, dict)
        or budget_by_id.get(global_budget.budget_id) != global_budget
        or global_budget != live_global_budget
        or global_budget.policy_id != policy.policy_id
        or global_budget.topology_seed_id != topology.topology_seed_id
        or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
        or global_budget.budget_state != "ACTIVE"
        or queue_entries != _d3_latest_queue_entries_v02(settled_queue_entry_log)
        or any(item.evaluated_round == admission_round for item in settled_backpressure_states)
    ):
        raise ValueError("g2d_backpressure_invalid")
    material = _d3_round_control_material_v02(
        source_context=source_context,
        topology=topology,
        policy=policy,
        global_budget=global_budget,
        admission_round=admission_round,
        entries=settled_queue_entry_log,
        indexes=indexes,
        prior_backpressure_states=settled_backpressure_states,
    )
    core = material["controlling_core"]
    if not isinstance(core, dict):
        raise ValueError("g2d_backpressure_invalid")
    if core["running_count"] != global_budget.current_parallelism:
        raise ValueError("g2d_parallelism_limit_exceeded")
    if core["residual_admission_slots"] > 0:
        return None
    for prior_state in settled_backpressure_states:
        prior_budget = budget_by_id[prior_state.global_budget_id]
        closure_frontiers = indexes["backpressure_closure_frontier_by_id"]
        if not isinstance(closure_frontiers, dict):
            raise ValueError("g2d_backpressure_invalid")
        closure_frontier = closure_frontiers.get(prior_state.backpressure_id)
        if type(closure_frontier) is not int:
            raise ValueError("g2d_backpressure_invalid")
        prior_entries = settled_queue_entry_log[: closure_frontier + 1]
        prior_indexes = _d3_frontier_local_indexes_v02(
            source_context=source_context,
            topology=topology,
            policy=policy,
            queue_entries=settled_queue_entry_log,
            queue_artifacts=settled_queue_artifact_log,
            queue_frontier=closure_frontier,
            global_budget=prior_budget,
            complete_indexes=indexes,
            prior_states=tuple(
                item
                for item in settled_backpressure_states
                if item.evaluated_round < prior_state.evaluated_round
            ),
            closure_frontiers=closure_frontiers,
        )
        prior_material = _d3_round_control_material_v02(
            source_context=source_context,
            topology=topology,
            policy=policy,
            global_budget=prior_budget,
            admission_round=prior_state.evaluated_round,
            entries=prior_entries,
            indexes=prior_indexes,
            prior_backpressure_states=tuple(
                item
                for item in settled_backpressure_states
                if item.evaluated_round < prior_state.evaluated_round
            ),
        )
        if prior_material["control_core_sha256"] == material["control_core_sha256"]:
            return None
    deferred = material["deferred"]
    admission_entries = material["admission_entries"]
    latest = material["latest"]
    if not isinstance(deferred, tuple) or not isinstance(admission_entries, tuple) or not isinstance(latest, tuple):
        raise ValueError("g2d_backpressure_invalid")
    if not deferred:
        if not core["future_progress_source_queue_entry_ids"] and any(
            item.state == "PENDING" for item in latest
        ):
            raise ValueError("g2d_no_progress_deadend")
        return None
    admission_order = tuple(item.queue_entry_id for item in admission_entries)
    provisional = FractalBackpressureStateV02(
        backpressure_id="frbackpressure_v02:" + _ZERO_SHA256,
        topology_id=topology.topology_id,
        policy_id=policy.policy_id,
        evaluated_round=admission_round,
        queue_capacity=policy.max_parallelism,
        running_count=int(core["running_count"]),
        ready_count=int(core["ready_count"]),
        pending_count=len(deferred),
        deferred_queue_entry_ids=tuple(item.queue_entry_id for item in deferred),
        admission_order=admission_order,
        backpressure_reason="PARALLELISM_CAPACITY_EXHAUSTED",
        reason_codes=("g2d_transition_backpressure_deferred",),
        no_work_dropped=True,
        lineage_refs=(
            topology.topology_id,
            policy.policy_id,
            global_budget.budget_id,
            str(admission_round),
            *admission_order,
        ),
        global_budget_id=global_budget.budget_id,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )
    result = _finish_identity(provisional)
    if validate_fractal_backpressure_state_v02(result).status != "PASS":
        raise ValueError("g2d_backpressure_invalid")
    return result


def project_fractal_cell_queue_entry_kernel_artifact_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    topology_artifact: KernelArtifactV01,
    predecessor_artifact: KernelArtifactV01 | None,
    activation_parent_artifact: KernelArtifactV01 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    source_context: FractalRuntimeSourceContextV02,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> KernelArtifactV01:
    if validate_fractal_runtime_source_context_v02(source_context).status != "PASS":
        raise ValueError("g2d_source_context_invalid")
    if validate_fractal_cell_queue_entry_v02(queue_entry).status != "PASS":
        raise ValueError("g2d_queue_entry_invalid")
    topology = construct_runtime_execution_topology_v02(source_context)
    if topology_artifact != _build_topology_artifact_v02(topology, source_context):
        raise ValueError("g2d_abi_projection_substituted")
    rule_id = _d3_queue_rule_id_v02(queue_entry)
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
        candidate_queue_entry=queue_entry,
        frontier="T03_ARTIFACT" if rule_id == "t03" else "COMPLETED",
    )
    if queue_entry.topology_id != topology.topology_id or queue_entry.topology_seed_id != topology.topology_seed_id:
        raise ValueError("g2d_queue_artifact_lineage_invalid")
    initial = queue_entry.predecessor_queue_entry_id is None
    if initial:
        if predecessor_artifact is not None or local_child_result_artifact is not None:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        if queue_entry.parent_cell_id is None:
            if activation_parent_artifact is not None:
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            parent_refs = (topology_artifact.artifact_id,)
        else:
            if type(activation_parent_artifact) is not KernelArtifactV01:
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            _d3_validate_parent_slot_artifact_v02(
                activation_parent_artifact,
                topology=topology,
                parent_cell_id=queue_entry.parent_cell_id,
                child_cell_id=queue_entry.cell_id,
            )
            _d3_validate_parent_slot_chain_v02(
                parent_slot_artifact=activation_parent_artifact,
                parent_cell_id=queue_entry.parent_cell_id,
                child_cell_id=queue_entry.cell_id,
                topology=topology,
                indexes=indexes,
            )
            parent_refs = (topology_artifact.artifact_id, activation_parent_artifact.artifact_id)
        source_artifact = topology_artifact
    else:
        if activation_parent_artifact is not None or type(predecessor_artifact) is not KernelArtifactV01:
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        predecessor_id = _d3_queue_artifact_payload_ref_v02(predecessor_artifact, "queue_entry_id")
        if predecessor_id != queue_entry.predecessor_queue_entry_id:
            raise ValueError("g2d_queue_predecessor_invalid")
        artifact_by_queue_id = indexes["artifact_by_queue_id"]
        if (
            not isinstance(artifact_by_queue_id, dict)
            or artifact_by_queue_id.get(predecessor_id) != predecessor_artifact
        ):
            raise ValueError("g2d_queue_predecessor_invalid")
        if (
            type(predecessor_artifact.trace_refs) is not tuple
            or len(predecessor_artifact.trace_refs) < 2
            or predecessor_artifact.trace_refs[1] != queue_entry.topology_id
        ):
            raise ValueError("g2d_queue_artifact_lineage_invalid")
        parent_refs = (topology_artifact.artifact_id, predecessor_artifact.artifact_id)
        if local_child_result_artifact is not None:
            if (
                queue_entry.state not in {"VALIDATING", *NODE_TERMINAL_OUTCOMES}
                or queue_entry.planned_child_cell_id is None
                or local_child_result_artifact.artifact_type != "FractalCellResult"
                or _validate_kernel_artifact_v01(local_child_result_artifact)
            ):
                raise ValueError("g2d_queue_artifact_lineage_invalid")
            parent_refs += (local_child_result_artifact.artifact_id,)
        source_artifact = predecessor_artifact
    registry = _build_fractal_runtime_transition_registry_profile_v02()
    decision = _d3_transition_decision_v02(registry, rule_id)
    if queue_entry.transition_decision_id != decision.decision_id:
        raise ValueError("g2d_transition_decision_substituted")
    result = _d3_expected_queue_artifact_against_prefix_v02(
        queue_entry,
        parent_refs=parent_refs,
        source_context=source_context,
        topology=topology,
        indexes=indexes,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
    )
    if _validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source_artifact,
        target_artifact=result,
    ):
        raise ValueError("g2d_transition_decision_substituted")
    return result


def _d3_runtime_assignment_for_node_v02(
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    node: RuntimeTopologyNodeV02,
) -> RuntimeAssignmentV02:
    _binding, seed, _initial, _nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    row = dict(MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[topology.accepted_mode][
        node.canonical_index
    ]
    capabilities = node.required_capability_ids if row[4] == ("SRC_CAPS",) else row[4]
    assignment = build_runtime_assignment_v02(
        seed,
        node,
        assignment_kind=row[2],
        executor_component_id=row[3],
        capability_ids=capabilities,
        cell_binding_class=row[5],
        scope_binding_class=row[6],
        budget_binding_class=row[7],
    )
    if assignment.assignment_id != topology.ordered_assignment_ids[node.canonical_index]:
        raise ValueError("g2d_topology_assignment_invalid")
    return assignment


def _d3_local_observation_material_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02,
    cell_budget_before: FractalRuntimeBudgetV02,
    global_budget_before: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    indexes: dict[str, object],
) -> dict[str, object]:
    if node.node_kind not in _D3_LOCAL_NODE_KINDS_V02:
        raise ValueError("g2d_queue_transition_unknown")
    assignment = _d3_runtime_assignment_for_node_v02(source_context, topology, node)
    artifact_by_queue_id = indexes["artifact_by_queue_id"]
    input_by_id = indexes["input_by_id"]
    budget_by_id = indexes["budget_by_id"]
    queue_by_id = indexes["queue_by_id"]
    if (
        not isinstance(artifact_by_queue_id, dict)
        or not isinstance(input_by_id, dict)
        or not isinstance(budget_by_id, dict)
        or not isinstance(queue_by_id, dict)
        or input_by_id.get(cell_input.cell_input_id) != cell_input
        or budget_by_id.get(cell_budget_before.budget_id) != cell_budget_before
        or budget_by_id.get(global_budget_before.budget_id) != global_budget_before
        or any(
            queue_by_id.get(item.queue_entry_id) != item
            or item.queue_entry_id not in artifact_by_queue_id
            for item in dependencies
        )
        or cell_budget_before.owning_cell_id != cell_input.cell_id
        or cell_budget_before.budget_state != "ACTIVE"
        or global_budget_before.budget_scope != "ROOT_GLOBAL_AND_CELL"
        or global_budget_before.owning_cell_id != topology.root_cell_id
        or global_budget_before.budget_state != "ACTIVE"
        or (
            cell_input.cell_id == topology.root_cell_id
            and cell_budget_before != global_budget_before
        )
        or (
            cell_input.cell_id != topology.root_cell_id
            and cell_budget_before == global_budget_before
        )
    ):
        raise ValueError("g2d_queue_entry_invalid")
    states = tuple(item.state for item in dependencies)
    if "BLOCKED" in states:
        outcome = "BLOCKED"
    elif "NEEDS_USER" in states:
        outcome = "NEEDS_USER"
    elif "DEADEND" in states:
        outcome = "DEADEND"
    elif "DEGRADED" in states:
        outcome = "DEGRADED"
    else:
        outcome = "COMPLETED"
    reasons = dict(_D3_TERMINAL_REASON_ROWS_V02)[outcome]
    evidence = (
        tuple(artifact_by_queue_id[item.queue_entry_id].artifact_id for item in dependencies)
        if dependencies
        else cell_input.evidence_refs
    )
    core: dict[str, object] = {
        "profile_version": "v0.3.1",
        "topology_id": topology.topology_id,
        "topology_seed_id": topology.topology_seed_id,
        "source_binding_id": topology.source_binding_id,
        "request_id": topology.request_id,
        "transaction_id": topology.transaction_id,
        "owning_root_id": topology.owning_root_id,
        "source_time_envelope_ref": topology.time_envelope_ref,
        "node_id": node.node_id,
        "assignment_id": assignment.assignment_id,
        "node_kind": node.node_kind,
        "expected_output_kind": node.expected_output_kind,
        "cell_input_id": cell_input.cell_input_id,
        "cell_input_evidence_refs": list(cell_input.evidence_refs),
        "cell_id": cell_input.cell_id,
        "parent_cell_id": cell_input.parent_cell_id,
        "scope_ref": cell_input.scope_ref,
        "cell_budget_before_id": cell_budget_before.budget_id,
        "global_budget_before_id": global_budget_before.budget_id,
        "dependency_queue_entry_ids": [item.queue_entry_id for item in dependencies],
        "dependency_queue_artifact_ids": [
            artifact_by_queue_id[item.queue_entry_id].artifact_id for item in dependencies
        ],
        "dependency_states": list(states),
        "dependency_reason_tuples": [list(item.queue_reason_codes) for item in dependencies],
        "dependency_output_tuples": [list(item.observed_output_refs) for item in dependencies],
        "dependency_evidence_tuples": [list(item.observed_evidence_refs) for item in dependencies],
        "dependency_advisory_tuples": [list(item.advisory_refs) for item in dependencies],
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
    output = (
        (
            "d3local:output:"
            + _domain_separated_sha256_hex_v01(
                domain="HEDGEHOG_FRACTAL_RUNTIME_V02_D3_LOCAL_OBSERVATION_MATERIAL",
                payload=_canonical_json_bytes_v01(core),
            ),
        )
        if outcome in {"COMPLETED", "DEGRADED"}
        else ()
    )
    return {
        **core,
        "derived_observed_output_refs": output,
        "derived_observed_evidence_refs": evidence,
        "derived_advisory_refs": (),
        "derived_queue_reason_codes": reasons,
        "allowed_outcome": outcome,
    }


def _d3_child_activation_precheck_material_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    source_artifact: KernelArtifactV01,
    current_entry: FractalCellQueueEntryV02,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02,
    cell_budget_before: FractalRuntimeBudgetV02,
    global_budget_before: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    indexes: dict[str, object],
) -> dict[str, object]:
    if (
        type(source_context) is not FractalRuntimeSourceContextV02
        or indexes.get("validated_source_context") != source_context
        or type(topology) is not RuntimeExecutionTopologyV02
        or indexes.get("validated_topology") != topology
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    if node.node_kind != "FRACTAL_CELL" or current_entry.planned_child_cell_id is None:
        raise ValueError("g2d_child_slot_activation_invalid")
    initial, ready, running = _d3_validate_parent_slot_chain_v02(
        parent_slot_artifact=source_artifact,
        parent_cell_id=current_entry.cell_id,
        child_cell_id=current_entry.planned_child_cell_id,
        topology=topology,
        indexes=indexes,
    )
    if running != current_entry:
        raise ValueError("g2d_child_slot_activation_invalid")
    artifact_by_queue_id = indexes["artifact_by_queue_id"]
    input_by_id = indexes["input_by_id"]
    revise_by_id = indexes["revise_by_id"]
    projection_by_child = indexes["projection_by_child"]
    budget_by_id = indexes["budget_by_id"]
    if (
        not isinstance(artifact_by_queue_id, dict)
        or not isinstance(input_by_id, dict)
        or not isinstance(revise_by_id, dict)
        or not isinstance(projection_by_child, dict)
        or not isinstance(budget_by_id, dict)
        or input_by_id.get(cell_input.cell_input_id) != cell_input
        or budget_by_id.get(cell_budget_before.budget_id) != cell_budget_before
        or budget_by_id.get(global_budget_before.budget_id) != global_budget_before
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    if _d3_instantiated_child_v02(current_entry, indexes=indexes) is not None:
        raise ValueError("g2d_child_slot_activation_invalid")
    expected_planned = _d3_planned_child_ids_from_sources_v02(source_context, topology)
    canonical_child_index = node.canonical_index - 1
    if (
        topology.accepted_mode != "full_fractal"
        or not 0 <= canonical_child_index < len(expected_planned)
        or expected_planned[canonical_child_index] != current_entry.planned_child_cell_id
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    chain_ids: list[str] = []
    cursor: FractalCellQueueEntryV02 | None = running
    queue_by_id = indexes["queue_by_id"]
    if not isinstance(queue_by_id, dict):
        raise ValueError("g2d_child_slot_activation_invalid")
    while cursor is not None:
        if cursor.queue_entry_id in chain_ids:
            raise ValueError("g2d_queue_predecessor_invalid")
        chain_ids.append(cursor.queue_entry_id)
        cursor = queue_by_id.get(cursor.predecessor_queue_entry_id)
    queue_position_by_id = indexes["queue_position_by_id"]
    if not isinstance(queue_position_by_id, dict):
        raise ValueError("g2d_child_slot_activation_invalid")
    running_position = queue_position_by_id[running.queue_entry_id]
    relevant_revise = tuple(
        observation
        for observation in revise_by_id.values()
        if observation.topology_id == topology.topology_id
        and observation.cell_id == current_entry.cell_id
        and observation.queue_entry_id in chain_ids
        and queue_by_id[observation.queue_entry_id].node_id == current_entry.node_id
        and queue_position_by_id.get(observation.queue_entry_id, running_position)
        < running_position
    )
    if any(
        queue_by_id.get(item.queue_entry_id) != item
        or item.queue_entry_id not in artifact_by_queue_id
        for item in dependencies
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    dependency_artifacts = tuple(
        artifact_by_queue_id[item.queue_entry_id] for item in dependencies
    )
    if tuple(item.node_id for item in dependencies) != _d3_queue_dependency_ids_v02(
        topology,
        node,
        cell_depth=current_entry.cell_depth,
    ):
        raise ValueError("g2d_child_slot_activation_invalid")
    parent_allowed = source_context.runtime_policy.allowed_capability_ids
    child_allowed = tuple(
        capability
        for capability in source_context.runtime_policy.allowed_capability_ids
        if capability in parent_allowed
    )
    parent_forbidden = source_context.runtime_policy.forbidden_claims
    child_forbidden = tuple(
        claim
        for claim in source_context.runtime_policy.forbidden_claims
        if claim in parent_forbidden
    )
    ttl = source_context.router_input.local_routing_snapshot.ttl_seconds
    sibling_count = sum(
        projection.parent_cell_id == current_entry.cell_id
        for projection in projection_by_child.values()
    )
    total_cell_count = len(input_by_id)
    latest_by_key = indexes.get("latest_by_key")
    if not isinstance(latest_by_key, dict):
        raise ValueError("g2d_child_slot_activation_invalid")
    occupied = global_budget_before.current_parallelism + sum(
        item.state == "READY" for item in latest_by_key.values()
    )
    child_depth = cell_input.cell_depth + 1
    hard_denial = bool(
        any(item.state == "BLOCKED" for item in dependencies)
        or child_depth >= source_context.runtime_policy.max_depth
        or total_cell_count >= source_context.runtime_policy.max_total_cells
        or sibling_count >= source_context.runtime_policy.max_fan_out
        or occupied >= source_context.runtime_policy.max_parallelism
        or global_budget_before.remaining_cell_count <= 0
        or source_context.runtime_policy.max_provider_calls != 0
        or global_budget_before.consumed_provider_calls != 0
    )
    if hard_denial:
        disposition = "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
        outcome = "BLOCKED"
    elif any(
        item.state == "NEEDS_USER"
        and item.queue_reason_codes == ("g2d_resolvable_input_needs_user",)
        and bool(item.observed_evidence_refs)
        and artifact_by_queue_id.get(item.queue_entry_id)
        == dependency_artifacts[index]
        for index, item in enumerate(dependencies)
    ):
        disposition = "RESOLVABLE_INPUT_MISSING"
        outcome = "NEEDS_USER"
    elif any(item.state == "DEADEND" for item in dependencies) or any(
        item.derived_terminal_state == "DEADEND" for item in relevant_revise
    ):
        disposition = "NO_PROGRESS_OR_NONRESOLVABLE"
        outcome = "DEADEND"
    else:
        disposition = "PASS_FOR_CHILD_ACTIVATION"
        outcome = None
    evidence_items = [
        source_context.route_eligibility_artifact.artifact_id,
        _build_topology_artifact_v02(topology, source_context).artifact_id,
        cell_input.cell_input_id,
        artifact_by_queue_id[initial.queue_entry_id].artifact_id,
        artifact_by_queue_id[ready.queue_entry_id].artifact_id,
        artifact_by_queue_id[running.queue_entry_id].artifact_id,
        cell_budget_before.budget_id,
    ]
    if global_budget_before.budget_id != cell_budget_before.budget_id:
        evidence_items.append(global_budget_before.budget_id)
    evidence_items.extend(item.artifact_id for item in dependency_artifacts)
    evidence_items.extend(item.observation_id for item in relevant_revise)
    evidence = tuple(evidence_items)
    if not _unique_tuple(evidence):
        raise ValueError("g2d_child_slot_activation_invalid")
    reasons = () if outcome is None else dict(_D3_TERMINAL_REASON_ROWS_V02)[outcome]
    return {
        "profile_version": "v0.3.1",
        "topology_id": topology.topology_id,
        "topology_seed_id": topology.topology_seed_id,
        "source_binding_id": topology.source_binding_id,
        "route_eligibility_artifact_id": source_context.route_eligibility_artifact.artifact_id,
        "topology_artifact_id": _build_topology_artifact_v02(topology, source_context).artifact_id,
        "parent_cell_id": current_entry.cell_id,
        "parent_cell_input_id": cell_input.cell_input_id,
        "parent_scope_ref": cell_input.scope_ref,
        "parent_slot_node_id": node.node_id,
        "parent_slot_assignment_id": topology.ordered_assignment_ids[node.canonical_index],
        "canonical_child_index": canonical_child_index,
        "planned_child_cell_id": current_entry.planned_child_cell_id,
        "candidate_child_scope_ref": cell_input.scope_ref,
        "parent_slot_initial_queue_entry_id": initial.queue_entry_id,
        "parent_slot_initial_artifact_id": artifact_by_queue_id[initial.queue_entry_id].artifact_id,
        "parent_slot_t02_decision_id": initial.transition_decision_id,
        "parent_slot_ready_queue_entry_id": ready.queue_entry_id,
        "parent_slot_ready_artifact_id": artifact_by_queue_id[ready.queue_entry_id].artifact_id,
        "parent_slot_t04_decision_id": ready.transition_decision_id,
        "parent_slot_running_queue_entry_id": running.queue_entry_id,
        "parent_slot_running_artifact_id": artifact_by_queue_id[running.queue_entry_id].artifact_id,
        "parent_slot_t05_decision_id": running.transition_decision_id,
        "parent_cell_budget_id": cell_budget_before.budget_id,
        "global_budget_id": global_budget_before.budget_id,
        "parent_budget_state": cell_budget_before.budget_state,
        "global_budget_state": global_budget_before.budget_state,
        "parent_budget_counters": _d3_budget_counter_tuple_v02(cell_budget_before),
        "global_budget_counters": _d3_budget_counter_tuple_v02(global_budget_before),
        "dependency_queue_entry_ids": tuple(item.queue_entry_id for item in dependencies),
        "dependency_queue_artifact_ids": tuple(item.artifact_id for item in dependency_artifacts),
        "dependency_states": tuple(item.state for item in dependencies),
        "dependency_reason_tuples": tuple(item.queue_reason_codes for item in dependencies),
        "dependency_output_tuples": tuple(item.observed_output_refs for item in dependencies),
        "dependency_evidence_tuples": tuple(item.observed_evidence_refs for item in dependencies),
        "parent_allowed_capability_ids": parent_allowed,
        "child_allowed_capability_ids": child_allowed,
        "parent_forbidden_claims": parent_forbidden,
        "child_forbidden_claims": child_forbidden,
        "parent_ttl_units": ttl,
        "child_ttl_units": ttl,
        "parent_depth": cell_input.cell_depth,
        "child_depth": child_depth,
        "instantiated_sibling_count": sibling_count,
        "instantiated_total_cell_count": total_cell_count,
        "occupied_admission_slots": occupied,
        "max_depth": source_context.runtime_policy.max_depth,
        "max_fan_out": source_context.runtime_policy.max_fan_out,
        "max_total_cells": source_context.runtime_policy.max_total_cells,
        "max_parallelism": source_context.runtime_policy.max_parallelism,
        "max_provider_calls": source_context.runtime_policy.max_provider_calls,
        "relevant_parent_slot_revise_observation_ids": tuple(
            item.observation_id for item in relevant_revise
        ),
        "relevant_parent_slot_revise_terminal_states": tuple(
            item.derived_terminal_state for item in relevant_revise
        ),
        "derived_disposition": disposition,
        "derived_queue_reason_codes": reasons,
        "derived_evidence_refs": evidence if outcome is not None else (),
    }


_D3_CELL_RESULT_PAYLOAD_FIELDS_V02 = (
    "result_id",
    "topology_seed_id",
    "cell_id",
    "parent_cell_id",
    "cell_depth",
    "cell_input_id",
    "outcome",
    "accepted_output_refs",
    "evidence_refs",
    "pre_result_validation_report_id",
    "partial_failure_ids",
    "allocated_cell_budget_id",
    "final_cell_budget_id",
    "global_budget_id",
    "scope_ref",
    "reason_codes",
    "source_reason_codes",
    "parent_return_required",
    "root_review_required",
    "authority_created",
    "permission_created",
    "action_commit_packet_created",
    "receipt_created",
    "final_output_created",
    "drs_write_created",
    "real_world_effects_count",
)


def _d3_expected_child_result_artifact_v02(
    result: FractalCellResultV02,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    current_entry: FractalCellQueueEntryV02,
    indexes: dict[str, object],
) -> KernelArtifactV01:
    if (
        type(result) is not FractalCellResultV02
        or validate_fractal_cell_result_v02(result).status != "PASS"
        or rebuild_fractal_cell_result_identity_v02(result) != result.result_id
        or result.topology_id != topology.topology_id
        or result.topology_seed_id != topology.topology_seed_id
        or result.cell_id != current_entry.planned_child_cell_id
        or result.parent_cell_id != current_entry.cell_id
        or result.cell_depth != current_entry.cell_depth + 1
        or result.ordered_child_result_ids
        or result.partial_failure_ids
        or result.reason_codes != dict(_D3_TERMINAL_REASON_ROWS_V02)[result.outcome]
    ):
        raise ValueError("g2d_cell_result_context_mismatch")
    input_by_id = indexes.get("input_by_id")
    latest_by_key = indexes.get("latest_by_key")
    artifact_by_queue_id = indexes.get("artifact_by_queue_id")
    budget_by_id = indexes.get("budget_by_id")
    if not all(
        isinstance(item, dict)
        for item in (input_by_id, latest_by_key, artifact_by_queue_id, budget_by_id)
    ):
        raise ValueError("g2d_cell_result_context_mismatch")
    cell_input = input_by_id.get(result.cell_input_id)
    if (
        type(cell_input) is not FractalCellInputV02
        or cell_input.cell_id != result.cell_id
        or cell_input.parent_cell_id != result.parent_cell_id
        or cell_input.cell_depth != result.cell_depth
        or cell_input.scope_ref != result.scope_ref
    ):
        raise ValueError("g2d_cell_result_context_mismatch")
    terminal_entries = tuple(
        latest_by_key.get((result.cell_id, node_id))
        for node_id in cell_input.ordered_node_ids
    )
    if (
        any(
            type(item) is not FractalCellQueueEntryV02
            or item.state not in _D3_TERMINAL_STATES_V02
            for item in terminal_entries
        )
        or result.ordered_terminal_queue_entry_ids
        != tuple(item.queue_entry_id for item in terminal_entries)
    ):
        raise ValueError("g2d_cell_result_postorder_invalid")
    terminal_artifacts = tuple(
        artifact_by_queue_id.get(item.queue_entry_id) for item in terminal_entries
    )
    if any(type(item) is not KernelArtifactV01 for item in terminal_artifacts):
        raise ValueError("g2d_cell_result_context_mismatch")
    allocated = budget_by_id.get(result.allocated_cell_budget_id)
    final = budget_by_id.get(result.final_cell_budget_id)
    global_budget = budget_by_id.get(result.global_budget_id)
    if (
        type(allocated) is not FractalRuntimeBudgetV02
        or type(final) is not FractalRuntimeBudgetV02
        or type(global_budget) is not FractalRuntimeBudgetV02
        or allocated.owning_cell_id != result.cell_id
        or allocated.budget_state != "ALLOCATED"
        or allocated.budget_event_kind != "INITIAL_ALLOCATION"
        or final.owning_cell_id != result.cell_id
        or final.budget_state != "FINAL"
        or final.budget_event_kind != "FINALIZE"
        or global_budget.owning_cell_id != topology.root_cell_id
        or global_budget.budget_scope != "ROOT_GLOBAL_AND_CELL"
    ):
        raise ValueError("g2d_cell_result_context_mismatch")
    expected_trace = (
        topology.topology_id,
        cell_input.cell_input_id,
        *result.ordered_terminal_queue_entry_ids,
        result.allocated_cell_budget_id,
        result.final_cell_budget_id,
        result.global_budget_id,
        result.pre_result_validation_report_id,
        result.post_vv_report_ref,
        result.gt_advisory_ref,
    )
    if result.trace_refs != expected_trace:
        raise ValueError("g2d_cell_result_context_mismatch")
    payload = {
        name: list(getattr(result, name))
        if type(getattr(result, name)) is tuple
        else getattr(result, name)
        for name in _D3_CELL_RESULT_PAYLOAD_FIELDS_V02
    }
    topology_artifact = _build_topology_artifact_v02(topology, source_context)
    route_plain = _kernel_artifact_to_plain_dict_v01(
        source_context.route_eligibility_artifact
    )
    provisional = _build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id="frabi_result_v02:" + _ZERO_SHA256,
        artifact_type="FractalCellResult",
        schema_version="v0.2",
        transaction_id=source_context.decision.transaction_id,
        owner_root_id=source_context.decision.owning_root_id,
        source_component="fractal_runtime_v02",
        authority_class="ADVISORY",
        lifecycle_state=(
            "BLOCKED_FAIL_CLOSED" if result.outcome == "BLOCKED" else "VALIDATED"
        ),
        payload=payload,
        trace_refs=result.trace_refs,
        parent_refs=(
            topology_artifact.artifact_id,
            *(item.artifact_id for item in terminal_artifacts),
        ),
        time_envelope=route_plain["time_envelope"],
    )
    material = _kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    expected = _replace(
        provisional,
        artifact_id=(
            "frabi_result_v02:"
            + _domain_separated_sha256_hex_v01(
                domain="HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
                payload=_canonical_json_bytes_v01(material),
            )
        ),
    )
    if _validate_kernel_artifact_v01(expected):
        raise ValueError("g2d_abi_projection_substituted")
    return expected


def _d3_child_result_artifact_pair_valid_v02(
    result: FractalCellResultV02,
    artifact: KernelArtifactV01,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    current_entry: FractalCellQueueEntryV02,
    indexes: dict[str, object],
) -> bool:
    try:
        expected = _d3_expected_child_result_artifact_v02(
            result,
            source_context=source_context,
            topology=topology,
            current_entry=current_entry,
            indexes=indexes,
        )
        return bool(
            type(artifact) is KernelArtifactV01
            and not _validate_kernel_artifact_v01(artifact)
            and artifact == expected
            and _canonical_json_bytes_v01(
                _kernel_artifact_to_plain_dict_v01(artifact)
            )
            == _canonical_json_bytes_v01(
                _kernel_artifact_to_plain_dict_v01(expected)
            )
        )
    except Exception:
        return False


def _d3_terminal_state_from_inputs_v02(
    *,
    node: RuntimeTopologyNodeV02,
    queue_reason_codes: tuple[str, ...],
    local_child_result: FractalCellResultV02 | None,
    revise_observation: FractalReviseObservationV02 | None,
) -> str:
    if local_child_result is not None:
        return local_child_result.outcome
    if revise_observation is not None and revise_observation.derived_terminal_state is not None:
        return revise_observation.derived_terminal_state
    reason_rows = {reasons: state for state, reasons in _D3_TERMINAL_REASON_ROWS_V02}
    if queue_reason_codes in reason_rows:
        return reason_rows[queue_reason_codes]
    if node.node_kind == "FRACTAL_CELL":
        raise ValueError("g2d_terminal_outcome_mapping_invalid")
    raise ValueError("g2d_blocked_reason_selection_invalid")


def _d3_dependencies_at_queue_frontier_v02(
    *,
    topology: RuntimeExecutionTopologyV02,
    node: RuntimeTopologyNodeV02,
    cell_id: str,
    cell_depth: int,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
) -> tuple[FractalCellQueueEntryV02, ...]:
    latest = {
        (item.cell_id, item.node_id): item
        for item in _d3_latest_queue_entries_v02(queue_entries)
    }
    dependencies = tuple(
        latest.get((cell_id, node_id))
        for node_id in _d3_queue_dependency_ids_v02(
            topology,
            node,
            cell_depth=cell_depth,
        )
    )
    if any(type(item) is not FractalCellQueueEntryV02 for item in dependencies):
        raise ValueError("g2d_queue_order_mismatch")
    result = tuple(dependencies)
    if not _d3_dependencies_satisfied_v02(
        topology,
        node,
        cell_id=cell_id,
        cell_depth=cell_depth,
        dependencies=result,
    ):
        raise ValueError("g2d_queue_order_mismatch")
    return result


def _d3_t06_origin_frontier_v02(
    *,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    source_context: FractalRuntimeSourceContextV02,
    validating_entry: FractalCellQueueEntryV02,
    node: RuntimeTopologyNodeV02,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    indexes: dict[str, object],
) -> dict[str, object]:
    queue_by_id = indexes.get("queue_by_id")
    queue_position_by_id = indexes.get("queue_position_by_id")
    artifact_by_queue_id = indexes.get("artifact_by_queue_id")
    budget_by_id = indexes.get("budget_by_id")
    budget_position_by_id = indexes.get("budget_position_by_id")
    if not all(
        isinstance(item, dict)
        for item in (
            queue_by_id,
            queue_position_by_id,
            artifact_by_queue_id,
            budget_by_id,
            budget_position_by_id,
        )
    ):
        raise ValueError("g2d_queue_predecessor_invalid")
    running = queue_by_id.get(validating_entry.predecessor_queue_entry_id)
    if (
        type(running) is not FractalCellQueueEntryV02
        or running.state != "RUNNING"
        or validating_entry.prior_state != "RUNNING"
        or _d3_queue_rule_id_v02(validating_entry) != "t06"
    ):
        raise ValueError("g2d_queue_predecessor_invalid")
    candidate_cell = budget_by_id.get(validating_entry.cell_budget_id)
    candidate_global = budget_by_id.get(validating_entry.global_budget_id)
    if (
        type(candidate_cell) is not FractalRuntimeBudgetV02
        or type(candidate_global) is not FractalRuntimeBudgetV02
        or candidate_cell.budget_event_kind != "FINISH_NODE"
        or candidate_global.budget_event_kind != "FINISH_NODE"
        or candidate_cell.budget_event_ref != validating_entry.transition_decision_id
        or candidate_global.budget_event_ref != validating_entry.transition_decision_id
    ):
        raise ValueError("g2d_budget_event_pair_mismatch")
    if validating_entry.cell_id == topology.root_cell_id:
        if candidate_cell is not candidate_global:
            raise ValueError("g2d_budget_event_pair_mismatch")
        segment_start = budget_position_by_id[candidate_global.budget_id]
        segment = (candidate_global,)
    else:
        cell_position = budget_position_by_id[candidate_cell.budget_id]
        global_position = budget_position_by_id[candidate_global.budget_id]
        if global_position != cell_position + 1:
            raise ValueError("g2d_budget_event_pair_mismatch")
        segment_start = cell_position
        segment = (candidate_cell, candidate_global)
    if settled_budget_log[segment_start : segment_start + len(segment)] != segment:
        raise ValueError("g2d_budget_event_pair_mismatch")
    historical_budget_indexes = _d3_validate_budget_log_v02(
        settled_budget_log[:segment_start],
        topology=topology,
        policy=policy,
        source_context=source_context,
    )
    live_cell, live_global = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=validating_entry.cell_id,
        indexes=historical_budget_indexes,
    )
    historical_budget_by_id = historical_budget_indexes["budget_by_id"]
    running_cell_anchor = budget_by_id.get(running.cell_budget_id)
    running_global_anchor = budget_by_id.get(running.global_budget_id)
    if (
        type(running_cell_anchor) is not FractalRuntimeBudgetV02
        or type(running_global_anchor) is not FractalRuntimeBudgetV02
        or candidate_cell.predecessor_budget_id != live_cell.budget_id
        or candidate_global.predecessor_budget_id != live_global.budget_id
        or not _d3_budget_is_ancestor_v02(
            running_cell_anchor,
            live_cell,
            budget_by_id=historical_budget_by_id,
        )
        or not _d3_budget_is_ancestor_v02(
            running_global_anchor,
            live_global,
            budget_by_id=historical_budget_by_id,
        )
    ):
        raise ValueError("g2d_budget_event_pair_mismatch")
    running_position = queue_position_by_id.get(running.queue_entry_id)
    if type(running_position) is not int:
        raise ValueError("g2d_queue_predecessor_invalid")
    dependencies = _d3_dependencies_at_queue_frontier_v02(
        topology=topology,
        node=node,
        cell_id=running.cell_id,
        cell_depth=running.cell_depth,
        queue_entries=settled_queue_entry_log[: running_position + 1],
    )
    return {
        "running_entry": running,
        "running_artifact": artifact_by_queue_id[running.queue_entry_id],
        "cell_budget_before": live_cell,
        "global_budget_before": live_global,
        "dependencies": dependencies,
        "candidate_segment": segment,
        "historical_budget_prefix": settled_budget_log[:segment_start],
    }


def evaluate_fractal_runtime_state_transition_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    source_artifact: KernelArtifactV01,
    current_entry: FractalCellQueueEntryV02 | None,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02 | None,
    cell_id: str,
    parent_cell_id: str | None,
    planned_child_cell_id: str | None,
    cell_depth: int,
    scope_ref: str,
    cell_budget_before: FractalRuntimeBudgetV02,
    global_budget_before: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...],
    observed_output_refs: tuple[str, ...],
    observed_evidence_refs: tuple[str, ...],
    advisory_refs: tuple[str, ...],
    local_child_result: FractalCellResultV02 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    validation_report: FractalRuntimeValidationReportV02 | None,
    parent_return_pre_post_vv_terminal_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    parent_return_child_results: tuple[FractalCellResultV02, ...],
    parent_return_partial_failures: tuple[FractalPartialFailureRecordV02, ...],
    parent_return_result_proposal: dict[str, object] | None,
    parent_return_post_vv_report: dict[str, object] | None,
    parent_return_gt_advisory_report: dict[str, object] | None,
    parent_return_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
    revise_observation: FractalReviseObservationV02 | None,
    backpressure_state: FractalBackpressureStateV02 | None,
    transition_registry: TransitionRegistryV01,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> TransitionDecisionV01 | None:
    family_empty = _d3_parent_return_family_empty_v02(
        terminal_queue_entries=parent_return_pre_post_vv_terminal_queue_entries,
        child_results=parent_return_child_results,
        partial_failures=parent_return_partial_failures,
        result_proposal=parent_return_result_proposal,
        post_vv_report=parent_return_post_vv_report,
        gt_advisory_report=parent_return_gt_advisory_report,
        validation_reports=parent_return_validation_reports,
    )
    if not family_empty:
        raise ValueError("g2d_parent_return_invalid")
    _binding, _seed, _initial, nodes = _d3_reconstruct_topology_parts_v02(
        source_context,
        topology,
    )
    indexes = _d3_validate_settled_runtime_prefix_v02(
        topology=topology,
        policy=source_context.runtime_policy,
        source_context=source_context,
        settled_budget_log=settled_budget_log,
        settled_queue_entry_log=settled_queue_entry_log,
        settled_queue_artifact_log=settled_queue_artifact_log,
        settled_cell_inputs=settled_cell_inputs,
        settled_scope_projections=settled_scope_projections,
        settled_revise_observations=settled_revise_observations,
        settled_backpressure_states=settled_backpressure_states,
        settled_validation_reports=settled_validation_reports,
        frontier=(
            "T03_DECISION"
            if current_entry is not None
            and current_entry.state == "PENDING"
            and backpressure_state is not None
            else "COMPLETED"
        ),
    )
    budget_by_id = indexes["budget_by_id"]
    latest_by_key = indexes["latest_by_key"]
    artifact_by_queue_id = indexes["artifact_by_queue_id"]
    input_by_id = indexes["input_by_id"]
    projection_by_child = indexes["projection_by_child"]
    revise_by_id = indexes["revise_by_id"]
    if not all(
        isinstance(item, dict)
        for item in (
            budget_by_id,
            latest_by_key,
            artifact_by_queue_id,
            input_by_id,
            projection_by_child,
            revise_by_id,
        )
    ):
        raise ValueError("g2d_queue_entry_invalid")
    if node not in nodes:
        raise ValueError("g2d_topology_node_invalid")
    for budget in (cell_budget_before, global_budget_before):
        if validate_fractal_runtime_budget_v02(budget).status != "PASS":
            raise ValueError("g2d_budget_invalid")
        if budget_by_id.get(budget.budget_id) != budget:
            raise ValueError("g2d_budget_predecessor_invalid")
    live_cell_budget_before, live_global_budget_before = _d3_live_budget_heads_v02(
        topology=topology,
        cell_id=cell_id,
        indexes=indexes,
    )
    reasons = _require_text_tuple(queue_reason_codes, public_reasons=True)
    outputs = _require_text_tuple(observed_output_refs)
    evidence = _require_text_tuple(observed_evidence_refs)
    advisories = _require_text_tuple(advisory_refs)
    if current_entry is None:
        if (
            cell_input is not None
            or dependencies != ()
            or reasons
            or outputs
            or evidence
            or advisories
            or local_child_result is not None
            or local_child_result_artifact is not None
            or validation_report is not None
            or revise_observation is not None
            or backpressure_state is not None
            or not family_empty
            or source_artifact != _build_topology_artifact_v02(topology, source_context)
            or cell_id != topology.root_cell_id and parent_cell_id is None
        ):
            raise ValueError("g2d_queue_entry_invalid")
        if (
            cell_budget_before.budget_event_kind != "CELL_CREATE"
            or global_budget_before.budget_event_kind != "CELL_CREATE"
            or cell_budget_before != live_cell_budget_before
            or global_budget_before != live_global_budget_before
        ):
            raise ValueError("g2d_budget_event_pair_mismatch")
        if parent_cell_id is None:
            if (
                cell_id != topology.root_cell_id
                or cell_depth != 0
                or scope_ref != topology.accepted_scope_ref
                or cell_budget_before != global_budget_before
                or cell_budget_before != _d3_root_cell_create_budget_v02(
                    source_context,
                    topology,
                )
                or settled_queue_entry_log
                or settled_queue_artifact_log
                or settled_cell_inputs
                or settled_scope_projections
            ):
                raise ValueError("g2d_queue_entry_invalid")
        else:
            if (
                topology.accepted_mode != "full_fractal"
                or cell_depth <= 0
                or cell_id not in projection_by_child
                or parent_cell_id not in indexes["input_by_cell"]
                or cell_budget_before.budget_scope != "CHILD_CELL_LOCAL"
                or cell_budget_before.owning_cell_id != cell_id
                or global_budget_before.budget_scope != "ROOT_GLOBAL_AND_CELL"
                or global_budget_before.owning_cell_id != topology.root_cell_id
                or cell_budget_before.budget_event_ref != cell_id
                or global_budget_before.budget_event_ref != cell_id
                or not any(
                    entry.state == "RUNNING"
                    and entry.cell_id == parent_cell_id
                    and entry.planned_child_cell_id == cell_id
                    for entry in latest_by_key.values()
                )
            ):
                raise ValueError("g2d_child_slot_activation_invalid")
        if node not in _d3_projected_nodes_v02(
            topology,
            nodes,
            cell_depth=cell_depth,
            parent_cell_id=parent_cell_id,
        ):
            raise ValueError("g2d_node_instance_geometry_invalid")
        rule_id = "t02"
    else:
        if node.node_kind == "PARENT_RETURN":
            return None
        if (
            validate_fractal_cell_queue_entry_v02(current_entry).status != "PASS"
            or type(cell_input) is not FractalCellInputV02
            or validate_fractal_cell_input_v02(cell_input).status != "PASS"
            or latest_by_key.get((current_entry.cell_id, current_entry.node_id))
            != current_entry
            or artifact_by_queue_id.get(current_entry.queue_entry_id) != source_artifact
            or input_by_id.get(cell_input.cell_input_id) != cell_input
            or (
                current_entry.topology_id,
                current_entry.cell_id,
                current_entry.parent_cell_id,
                current_entry.planned_child_cell_id,
                current_entry.cell_depth,
                current_entry.scope_ref,
            )
            != (
                topology.topology_id,
                cell_id,
                parent_cell_id,
                planned_child_cell_id,
                cell_depth,
                scope_ref,
            )
            or cell_budget_before.policy_id != source_context.runtime_policy.policy_id
            or global_budget_before.policy_id != source_context.runtime_policy.policy_id
            or cell_budget_before.topology_seed_id != topology.topology_seed_id
            or global_budget_before.topology_seed_id != topology.topology_seed_id
            or cell_budget_before.owning_cell_id != cell_id
            or global_budget_before.owning_cell_id != topology.root_cell_id
            or current_entry.cell_budget_id != cell_budget_before.budget_id
            or current_entry.global_budget_id != global_budget_before.budget_id
            or cell_budget_before.budget_state != "ACTIVE"
            or global_budget_before.budget_state != "ACTIVE"
        ):
            raise ValueError("g2d_queue_entry_invalid")
        dependencies_satisfied = _d3_dependencies_satisfied_v02(
            topology,
            node,
            cell_id=cell_id,
            cell_depth=cell_depth,
            dependencies=dependencies,
        )
        if current_entry.state == "PENDING":
            if not dependencies_satisfied:
                return None
            ready_count = sum(
                item.state == "READY" for item in latest_by_key.values()
            )
            residual = (
                source_context.runtime_policy.max_parallelism
                - live_global_budget_before.current_parallelism
                - ready_count
            )
            if backpressure_state is None:
                if reasons or outputs or evidence or advisories or residual <= 0:
                    raise ValueError("g2d_queue_entry_invalid")
                rule_id = "t04"
            else:
                if (
                    validate_fractal_backpressure_state_v02(backpressure_state).status != "PASS"
                    or backpressure_state not in settled_backpressure_states
                    or backpressure_state.topology_id != topology.topology_id
                    or backpressure_state.global_budget_id
                    != live_global_budget_before.budget_id
                    or current_entry.queue_entry_id not in backpressure_state.deferred_queue_entry_ids
                    or residual != 0
                    or reasons != ("g2d_transition_backpressure_deferred",)
                    or outputs
                    or evidence
                    or advisories
                ):
                    raise ValueError("g2d_backpressure_invalid")
                queue_by_id = indexes["queue_by_id"]
                if (
                    backpressure_state != settled_backpressure_states[-1]
                    or not isinstance(queue_by_id, dict)
                    or _d3_next_t03_source_id_v02(
                        state=backpressure_state,
                        queue_entries=settled_queue_entry_log,
                        queue_by_id=queue_by_id,
                    )
                    != current_entry.queue_entry_id
                ):
                    raise ValueError("g2d_backpressure_invalid")
                rule_id = "t03"
        elif current_entry.state == "READY":
            if backpressure_state is not None or reasons or outputs or evidence or advisories:
                raise ValueError("g2d_queue_entry_invalid")
            ready_count = sum(
                item.state == "READY" for item in latest_by_key.values()
            )
            if (
                live_global_budget_before.current_parallelism + ready_count
                > source_context.runtime_policy.max_parallelism
            ):
                raise ValueError("g2d_parallelism_limit_exceeded")
            rule_id = "t05"
        elif current_entry.state == "RUNNING":
            if (
                backpressure_state is not None
                or revise_observation is not None
                or validation_report is not None
            ):
                raise ValueError("g2d_queue_entry_invalid")
            if node.node_kind == "FRACTAL_CELL":
                if (local_child_result is None) != (local_child_result_artifact is None):
                    raise ValueError("g2d_queue_artifact_lineage_invalid")
                instantiated_child = _d3_instantiated_child_v02(
                    current_entry,
                    indexes=indexes,
                )
                if local_child_result is not None:
                    if (
                        type(local_child_result_artifact) is not KernelArtifactV01
                        or not _d3_child_result_artifact_pair_valid_v02(
                            local_child_result,
                            local_child_result_artifact,
                            source_context=source_context,
                            topology=topology,
                            current_entry=current_entry,
                            indexes=indexes,
                        )
                        or outputs != (local_child_result_artifact.artifact_id,)
                        or evidence != local_child_result.evidence_refs
                        or advisories
                        != (local_child_result.post_vv_report_ref, local_child_result.gt_advisory_ref)
                        or reasons != local_child_result.reason_codes
                    ):
                        raise ValueError("g2d_terminal_outcome_mapping_invalid")
                elif instantiated_child is not None:
                    if reasons or outputs or evidence or advisories:
                        raise ValueError("g2d_child_slot_activation_invalid")
                    return None
                else:
                    material = _d3_child_activation_precheck_material_v02(
                        source_context=source_context,
                        topology=topology,
                        source_artifact=source_artifact,
                        current_entry=current_entry,
                        node=node,
                        cell_input=cell_input,
                        cell_budget_before=live_cell_budget_before,
                        global_budget_before=live_global_budget_before,
                        dependencies=dependencies,
                        indexes=indexes,
                    )
                    if material["derived_disposition"] == "PASS_FOR_CHILD_ACTIVATION":
                        if reasons or outputs or evidence or advisories:
                            raise ValueError("g2d_child_slot_activation_invalid")
                        return None
                    if (
                        reasons != material["derived_queue_reason_codes"]
                        or evidence != material["derived_evidence_refs"]
                        or outputs
                        or advisories
                    ):
                        raise ValueError("g2d_child_slot_activation_invalid")
            elif node.node_kind in _D3_LOCAL_NODE_KINDS_V02:
                if local_child_result is not None or local_child_result_artifact is not None:
                    raise ValueError("g2d_queue_artifact_lineage_invalid")
                material = _d3_local_observation_material_v02(
                    source_context=source_context,
                    topology=topology,
                    node=node,
                    cell_input=cell_input,
                    cell_budget_before=live_cell_budget_before,
                    global_budget_before=live_global_budget_before,
                    dependencies=dependencies,
                    indexes=indexes,
                )
                if (
                    reasons != material["derived_queue_reason_codes"]
                    or outputs != material["derived_observed_output_refs"]
                    or evidence != material["derived_observed_evidence_refs"]
                    or advisories != material["derived_advisory_refs"]
                ):
                    raise ValueError("g2d_queue_entry_invalid")
            else:
                if (
                    local_child_result is not None
                    or local_child_result_artifact is not None
                    or reasons
                    or outputs
                    or evidence
                    or advisories
                ):
                    raise ValueError("g2d_queue_entry_invalid")
                return None
            rule_id = "t06"
        elif current_entry.state == "VALIDATING":
            if backpressure_state is not None:
                raise ValueError("g2d_queue_entry_invalid")
            origin = _d3_t06_origin_frontier_v02(
                topology=topology,
                policy=source_context.runtime_policy,
                source_context=source_context,
                validating_entry=current_entry,
                node=node,
                settled_budget_log=settled_budget_log,
                settled_queue_entry_log=settled_queue_entry_log,
                indexes=indexes,
            )
            origin_dependencies = origin["dependencies"]
            if dependencies != origin_dependencies:
                raise ValueError("g2d_queue_order_mismatch")
            if revise_observation is not None and revise_observation.revise_eligible:
                expected_report = validate_fractal_revise_observation_v02(
                    revise_observation
                )
                ready_count = sum(
                    item.state == "READY" for item in latest_by_key.values()
                )
                if (
                    node.node_kind not in _D3_LOCAL_NODE_KINDS_V02
                    or reasons
                    or outputs
                    or evidence
                    or advisories
                    or type(validation_report) is not FractalRuntimeValidationReportV02
                    or validation_report != expected_report
                    or validate_fractal_revise_observation_v02(revise_observation).status != "PASS"
                    or revise_by_id.get(revise_observation.observation_id)
                    != revise_observation
                    or source_context.runtime_policy.max_parallelism
                    - live_global_budget_before.current_parallelism
                    - ready_count
                    <= 0
                ):
                    raise ValueError("g2d_revise_observation_invalid")
                origin_material = _d3_local_observation_material_v02(
                    source_context=source_context,
                    topology=topology,
                    node=node,
                    cell_input=cell_input,
                    cell_budget_before=origin["cell_budget_before"],
                    global_budget_before=origin["global_budget_before"],
                    dependencies=origin_dependencies,
                    indexes=indexes,
                )
                if (
                    current_entry.queue_reason_codes
                    != origin_material["derived_queue_reason_codes"]
                    or current_entry.observed_output_refs
                    != origin_material["derived_observed_output_refs"]
                    or current_entry.observed_evidence_refs
                    != origin_material["derived_observed_evidence_refs"]
                    or current_entry.advisory_refs
                    != origin_material["derived_advisory_refs"]
                ):
                    raise ValueError("g2d_revise_observation_invalid")
                rule_id = "t07"
            else:
                if revise_observation is not None:
                    if (
                        revise_by_id.get(revise_observation.observation_id)
                        != revise_observation
                        or revise_observation.derived_terminal_state != "DEADEND"
                        or validation_report
                        != validate_fractal_revise_observation_v02(revise_observation)
                    ):
                        raise ValueError("g2d_revise_observation_invalid")
                elif validation_report is not None:
                    raise ValueError("g2d_queue_entry_invalid")
                if (
                    outputs != current_entry.observed_output_refs
                    or evidence != current_entry.observed_evidence_refs
                    or advisories != current_entry.advisory_refs
                    or reasons != current_entry.queue_reason_codes
                ):
                    raise ValueError("g2d_queue_entry_invalid")
                if node.node_kind == "FRACTAL_CELL":
                    if local_child_result is not None:
                        if (
                            type(local_child_result_artifact) is not KernelArtifactV01
                            or not _d3_child_result_artifact_pair_valid_v02(
                                local_child_result,
                                local_child_result_artifact,
                                source_context=source_context,
                                topology=topology,
                                current_entry=origin["running_entry"],
                                indexes=indexes,
                            )
                            or outputs != (local_child_result_artifact.artifact_id,)
                            or evidence != local_child_result.evidence_refs
                            or advisories
                            != (
                                local_child_result.post_vv_report_ref,
                                local_child_result.gt_advisory_ref,
                            )
                            or reasons != local_child_result.reason_codes
                        ):
                            raise ValueError("g2d_terminal_outcome_mapping_invalid")
                        terminal_state = local_child_result.outcome
                    else:
                        running = origin["running_entry"]
                        running_artifact = origin["running_artifact"]
                        if (
                            type(running) is not FractalCellQueueEntryV02
                            or type(running_artifact) is not KernelArtifactV01
                        ):
                            raise ValueError("g2d_child_slot_activation_invalid")
                        if _d3_instantiated_child_v02(
                            running,
                            indexes=indexes,
                        ) is not None:
                            return None
                        material = _d3_child_activation_precheck_material_v02(
                            source_context=source_context,
                            topology=topology,
                            source_artifact=running_artifact,
                            current_entry=running,
                            node=node,
                            cell_input=cell_input,
                            cell_budget_before=origin["cell_budget_before"],
                            global_budget_before=origin["global_budget_before"],
                            dependencies=origin_dependencies,
                            indexes=indexes,
                        )
                        outcome_by_disposition = {
                            "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL": "BLOCKED",
                            "RESOLVABLE_INPUT_MISSING": "NEEDS_USER",
                            "NO_PROGRESS_OR_NONRESOLVABLE": "DEADEND",
                        }
                        terminal_state = outcome_by_disposition.get(
                            material["derived_disposition"]
                        )
                        if (
                            terminal_state is None
                            or reasons != material["derived_queue_reason_codes"]
                            or evidence != material["derived_evidence_refs"]
                            or outputs
                            or advisories
                        ):
                            raise ValueError("g2d_terminal_outcome_mapping_invalid")
                elif node.node_kind in _D3_LOCAL_NODE_KINDS_V02:
                    running = origin["running_entry"]
                    if type(running) is not FractalCellQueueEntryV02:
                        raise ValueError("g2d_queue_predecessor_invalid")
                    material = _d3_local_observation_material_v02(
                        source_context=source_context,
                        topology=topology,
                        node=node,
                        cell_input=cell_input,
                        cell_budget_before=origin["cell_budget_before"],
                        global_budget_before=origin["global_budget_before"],
                        dependencies=origin_dependencies,
                        indexes=indexes,
                    )
                    if (
                        reasons != material["derived_queue_reason_codes"]
                        or outputs != material["derived_observed_output_refs"]
                        or evidence != material["derived_observed_evidence_refs"]
                        or advisories != material["derived_advisory_refs"]
                    ):
                        raise ValueError("g2d_terminal_outcome_mapping_invalid")
                    terminal_state = material["allowed_outcome"]
                elif revise_observation is not None:
                    terminal_state = "DEADEND"
                else:
                    return None
                rule_id = dict(
                    (state, rule)
                    for (prior, state), rule in _D3_RULE_BY_STATE_PAIR_V02.items()
                    if prior == "VALIDATING" and state in _D3_TERMINAL_STATES_V02
                )[terminal_state]
        elif current_entry.state in _D3_TERMINAL_STATES_V02:
            raise ValueError("g2d_terminal_queue_reentry_forbidden")
        else:
            raise ValueError("g2d_queue_state_unknown")
    if source_context.root_decision_result.root_commit_created is not True:
        raise ValueError("g2d_g2c_root_result_invalid")
    return _d3_transition_decision_v02(transition_registry, rule_id)
