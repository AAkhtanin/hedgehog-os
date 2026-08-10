"""Deterministic two-domain G2-D Fractal Runtime proof."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
import hashlib
import json
from unittest.mock import patch

import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as drs_compatibility
import hedgehog.drs_memory_resolution_v01 as drs_resolution
import hedgehog.drs_semantic_address_v01 as drs_semantic
import hedgehog.reuse_certificate_v01 as reuse_certificate
import hedgehog.structured_rationale as structured_rationale
from hedgehog.evidence import external_anchor_v01 as external_anchor
from hedgehog.evidence import sealed_evidence_profile_v01 as evidence_profile
from hedgehog.evidence import sealed_package_v01 as sealed_package
from hedgehog.evidence import sealed_replay_evidence_v01 as sealed_replay
import hedgehog.kernel.abi_v01 as abi
import hedgehog.kernel.execution_mode_router_v01 as g2c
import hedgehog.kernel.fractal_runtime_v02 as fr
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel.integrity_replay_v01 import (
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.transition_registry_v01 as transition_registry
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)
import hedgehog.gt_validator as gt_validator
import hedgehog.post_vv as post_vv


__all__ = (
    "FractalRuntimeG2DCaseResultV02",
    "FractalRuntimeG2DReportV02",
    "collect_fractal_runtime_g2_d_v02",
    "validate_fractal_runtime_g2_d_report_v02",
    "fractal_runtime_g2_d_report_to_plain_data_v02",
    "render_fractal_runtime_g2_d_v02",
    "main",
)


MODULE_ID = "fractal_runtime_g2_d_v02"
REPORT_VERSION = "v0.2"
PROFILE_ID = "fractal_runtime_g2d_two_domain_proof_v02"
REPORT_ID_PREFIX = "frg2dproof_v02:"
REPORT_ID_DOMAIN = "HEDGEHOG_FRACTAL_RUNTIME_G2D_TWO_DOMAIN_PROOF_V02"

EVALUATION_TIME = 1785542400
VALID_TO_TIME = 1785546000
EVALUATION_UTC = "2026-08-01T00:00:00+00:00"
VALID_TO_UTC = "2026-08-01T01:00:00+00:00"

DOMAIN_ORDER = (
    "TRAVEL_POLICY_INFORMATION",
    "WAREHOUSE_MAINTENANCE_INFORMATION",
)

_POSITIVE_MODE_ROWS = (
    (DOMAIN_ORDER[0], "memory_informed", False, False),
    (DOMAIN_ORDER[0], "local_slm", False, True),
    (DOMAIN_ORDER[0], "cloud_llm", True, False),
    (DOMAIN_ORDER[0], "full_semantic", False, False),
    (DOMAIN_ORDER[0], "full_fractal", False, False),
    (DOMAIN_ORDER[1], "memory_informed", False, False),
    (DOMAIN_ORDER[1], "local_slm", False, True),
    (DOMAIN_ORDER[1], "cloud_llm", False, False),
    (DOMAIN_ORDER[1], "full_semantic", False, False),
    (DOMAIN_ORDER[1], "full_fractal", False, False),
)

_CONSTRUCTIVE_CASE_NUMBERS = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 42, 43, 45, 46, 48, 49, 50, 51,
    52, 53, 54, 55, 56, 57, 59, 60, 61, 63, 64, 66, 67, 68, 69, 70,
    71, 72,
)

_NEGATIVE_CASE_NUMBERS = (
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 44,
    47, 58, 62, 65,
)


@dataclass(frozen=True)
class _CaseSpecV02:
    case_id: str
    case_class: str
    expected_outcome: str


@dataclass(frozen=True)
class _ProofContractV02:
    proof_kind: str
    axis: str
    executor: str
    observed_source: str
    matrix_cardinality: int
    accepted_bundle_required: bool


_CASE_SPECS = (
    _CaseSpecV02("g2d_case:travel:memory_informed:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:travel:local_slm:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:travel:cloud_llm_narrow:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:travel:full_semantic:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:travel:full_fractal:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:warehouse:memory_informed:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:warehouse:local_slm:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:warehouse:cloud_llm:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:warehouse:full_semantic:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:warehouse:full_fractal:v02", "CONSTRUCTIVE", "COMPLETED"),
    _CaseSpecV02("g2d_case:negative:deterministic_shortcut:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:sealed_replay_shortcut:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:direct_reuse_shortcut:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:blocked_terminal:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:needs_user_terminal:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:root_reject_terminal:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:direct_root_decision:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:route_substitution:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:cross_domain_source:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:foreign_id_only:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:scope_widening:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:capability_widening:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:fractal_capability_missing:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:mode_upgrade:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:mode_downgrade:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:g2b_instruction_authority:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:g2a_history_authority:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:depth_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:fan_out_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:total_cell_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:parallelism_backpressure:v02", "NEGATIVE", "PENDING"),
    _CaseSpecV02("g2d_case:negative:token_budget_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:time_budget_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:provider_budget_overflow:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:scope_budget_monotonic_matrix:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:negative:revise_count_overflow:v02", "NEGATIVE", "DEADEND"),
    _CaseSpecV02("g2d_case:no_progress_deadend:v02", "NEGATIVE", "DEADEND"),
    _CaseSpecV02("g2d_case:resolvable_missing_input:v02", "NEGATIVE", "NEEDS_USER"),
    _CaseSpecV02("g2d_case:required_child_partial:v02", "NEGATIVE", "DEGRADED"),
    _CaseSpecV02("g2d_case:required_child_hard_failure:v02", "NEGATIVE", "BLOCKED"),
    _CaseSpecV02("g2d_case:negative:child_authority_claims:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:repeated_canonical_equality:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:identity:acyclic_graph_rebuild:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:negative:queue_predecessor_substitution:v02", "NEGATIVE", "FAIL_CLOSED"),
    _CaseSpecV02("g2d_case:deterministic:post_vv_gt_injected_time:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:causal:used_field_counterfactual:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:causal:blocked_and_ignored_dispositions:v02", "NEGATIVE", "PASS"),
    _CaseSpecV02("g2d_case:identity:child_result_partial_failure_postorder:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:identity:pre_result_validation_no_cycle:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:runtime:node_work_queue_cell_aggregation:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:runtime:five_mode_exact_template_rows:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:source:selected_profile_capability_scope_binding:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:budget:allocation_predecessor_debit_matrix:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:validation:resultproposal_postvv_gt_outcome_matrix:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:transition:root_only_parent_return:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:abi:complete_field_partition_and_trace:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:causal:exact_pointer_reason_bundle:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:queue:backpressure_precedence:v02", "NEGATIVE", "PASS"),
    _CaseSpecV02("g2d_case:identity:policy_profile_separation:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:runtime:full_fractal_leaf_edge_projection:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:budget:cell_global_event_pairing:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:abi:pre_root_lifecycle_boundary:v02", "NEGATIVE", "PASS"),
    _CaseSpecV02("g2d_case:validation:context_unique_gt_report_ids:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:validation:pass_none_stage_contract:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:queue:instance_snapshot_round_and_blocked_reason:v02", "NEGATIVE", "PASS"),
    _CaseSpecV02("g2d_case:runtime:child_slot_input_node_outcome_order:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:validation:root_result_report_and_slice_surface:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:budget:typed_event_and_child_allocation_context:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:runtime:planned_child_activation_boundary:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:transition:prestate_decision_budget_queue_order:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:revise:observation_before_t07_and_budget:v02", "CONSTRUCTIVE", "PASS"),
    _CaseSpecV02("g2d_case:bundle:prebundle_validation_causal_final_assembly:v02", "CONSTRUCTIVE", "PASS"),
)


_SOURCE_NEGATIVE_AXIS_ROWS_V02 = (
    (11, "deterministic_shortcut", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (12, "sealed_replay_shortcut", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (13, "direct_informational_reuse", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (14, "blocked_terminal", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (15, "needs_user_terminal", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (16, "root_reject_terminal", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (17, "direct_root_decision_without_route_eligibility", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (18, "foreign_route_eligibility_artifact", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (19, "cross_domain_g2c_source_context", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (20, "foreign_route_eligibility_id_only", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (21, "accepted_scope_widening", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (22, "required_capability_widening", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (23, "recursive_capability_missing", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (24, "source_bound_mode_upgrade", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (25, "source_bound_mode_downgrade", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (26, "g2b_context_as_instruction_authority", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
    (27, "g2a_history_as_topology_authority", "validate_fractal_runtime_source_context_v02", "validation_report.status"),
)

_SOURCE_NEGATIVE_MUTATED_PATHS_V02 = (
    "/proposal/selected_mode=deterministic",
    "/proposal/selected_mode=sealed_replay",
    "/proposal/selected_mode=direct_informational_reuse",
    "/decision/downstream_consumption_class=TERMINAL_NO_CONSUMPTION",
    "/decision/downstream_consumption_class=TERMINAL_NO_CONSUMPTION",
    "/decision/outcome=REJECT",
    "/route_eligibility_artifact",
    "/route_eligibility_artifact",
    "/g2c_source_context/domain_id",
    "/route_eligibility_artifact/artifact_id",
    "/decision/accepted_scope_ref",
    "/proposal/required_downstream_capability_ids",
    "/runtime_policy/allowed_capability_ids/-recursive",
    "/proposal/selected_mode:upgrade",
    "/proposal/selected_mode:downgrade",
    "/router_input/g2b_binding:instruction_authority",
    "/router_input/g2a_binding:history_authority",
)

_BOUNDED_NEGATIVE_AXIS_ROWS_V02 = (
    (28, "depth_0_1_2_then_3", "validate_fractal_cell_input_v02", "validation_report.reason_codes"),
    (29, "fan_out_max_plus_one", "validate_fractal_cell_input_v02", "validation_report.reason_codes"),
    (30, "accepted_cell_create_21_then_22", "validate_fractal_runtime_budget_v02", "validation_report.reason_codes"),
    (31, "ready_running_parallelism_deferral", "advance_fractal_cell_queue_v02", "deferred_successor.state"),
    (32, "token_budget_max_plus_one", "validate_fractal_runtime_budget_v02", "validation_report.reason_codes"),
    (33, "wall_time_max_plus_one", "validate_fractal_runtime_budget_v02", "validation_report.reason_codes"),
    (34, "provider_budget_max_plus_one", "validate_fractal_runtime_budget_v02", "validation_report.reason_codes"),
    (35, "scope_ttl_capability_forbidden_budget_owner_predecessor_event_borrowing", "validate_parent_child_scope_projection_v02", "validation_report.status"),
    (36, "revise_limit_plus_one", "evaluate_fractal_revise_observation_v02", "revise_observation.derived_terminal_state"),
    (37, "two_non_positive_revisions", "evaluate_fractal_revise_observation_v02", "revise_observation.derived_terminal_state"),
    (38, "resolvable_missing_input", "evaluate_fractal_revise_observation_v02", "revise_observation.derived_terminal_state"),
    (39, "required_child_partial", "record_fractal_partial_failure_v02", "partial_failure.parent_disposition"),
    (40, "required_child_hard_failure_and_denial", "evaluate_fractal_runtime_state_transition_v02", "blocked_successor.state"),
    (41, "child_root_permission_packet_receipt_effect_claims", "validate_fractal_cell_input_v02", "validation_report.status"),
)

_MATRIX_AXIS_ROWS_V02 = (
    (42, "repeated_value_id_render", 3),
    (43, "acyclic_complete_postorder", 8),
    (44, "queue_predecessor_complete_substitution", 10),
    (45, "explicit_time_post_vv_gt", 3),
    (46, "actual_used_field_counterfactual", 1),
    (47, "blocked_and_ignored_counterfactual", 2),
    (48, "child_result_partial_failure_postorder", 3),
    (49, "pre_result_validation_no_cycle", 7),
    (50, "zero_one_two_child_aggregation", 3),
    (51, "five_mode_exact_templates", 5),
    (52, "profile_capability_cost_policy_scope_substitutions", 5),
    (53, "budget_allocation_debit_finalize_pairing", 8),
    (54, "five_parent_return_outcomes", 5),
    (55, "root_only_t13_t17", 5),
    (56, "six_queue_abi_parent_forms", 6),
    (57, "causal_pointer_reason_and_corruption_absence", 2),
    (58, "backpressure_precedence_and_no_drop", 5),
    (59, "policy_profile_source_identity_separation", 3),
    (60, "full_fractal_leaf_edges_7_8_9", 3),
    (61, "cell_global_budget_event_pairing", 6),
    (62, "pre_root_result_report_lifecycle", 5),
    (63, "context_unique_gt_ids", 2),
    (64, "validation_34_target_30_stage_contract", 34),
    (65, "queue_instance_snapshot_round_reason", 6),
    (66, "child_slot_result_merge_order", 3),
    (67, "public_surface_root_report_slice", 4),
    (68, "two_and_four_child_allocation", 6),
    (69, "planned_vs_accepted_child_activation", 3),
    (70, "prestate_parent_return_order", 4),
    (71, "revise_observation_budget_order_mutations", 6),
    (72, "prebundle_final_assembly", 8),
)


def _build_proof_contracts_v02() -> dict[str, _ProofContractV02]:
    contracts: dict[str, _ProofContractV02] = {}
    for number, spec in enumerate(_CASE_SPECS, start=1):
        if number <= 10:
            domain, mode, _narrow, _action = _POSITIVE_MODE_ROWS[number - 1]
            contract = _ProofContractV02(
                proof_kind="DOMAIN_POSITIVE_RUNTIME",
                axis=f"domain_positive:{domain}:{mode}",
                executor="run_fractal_runtime_v02",
                observed_source="runtime_report.runtime_outcome",
                matrix_cardinality=1,
                accepted_bundle_required=True,
            )
        elif number <= 27:
            row = next(item for item in _SOURCE_NEGATIVE_AXIS_ROWS_V02 if item[0] == number)
            contract = _ProofContractV02(
                proof_kind="SOURCE_EXACT_AXIS_FAIL_CLOSED",
                axis=row[1],
                executor=row[2],
                observed_source=row[3],
                matrix_cardinality=1,
                accepted_bundle_required=False,
            )
        elif number <= 41:
            row = next(item for item in _BOUNDED_NEGATIVE_AXIS_ROWS_V02 if item[0] == number)
            contract = _ProofContractV02(
                proof_kind="BOUNDED_ACTUAL_EXECUTION",
                axis=row[1],
                executor=row[2],
                observed_source=row[3],
                matrix_cardinality=(
                    4
                    if number == 28
                    else 22
                    if number == 30
                    else 12
                    if number == 35
                    else 6
                    if number == 41
                    else 1
                ),
                accepted_bundle_required=True,
            )
        else:
            row = next(item for item in _MATRIX_AXIS_ROWS_V02 if item[0] == number)
            contract = _ProofContractV02(
                proof_kind="ACCEPTED_RUNTIME_EXECUTABLE_MATRIX",
                axis=row[1],
                executor="public_runtime_object_validation",
                observed_source="actual_validation_or_object_field",
                matrix_cardinality=row[2],
                accepted_bundle_required=True,
            )
        contracts[spec.case_id] = contract
    if len(contracts) != 72:
        raise RuntimeError("g2d5_proof_contract_count_invalid")
    return contracts


_PROOF_CONTRACTS_V02 = _build_proof_contracts_v02()


def _detail_keys_for_case_v02(number: int) -> frozenset[str]:
    if 1 <= number <= 10:
        return frozenset({
            "domain_id", "accepted_mode", "root_outcome", "accepted_scope_ref",
            "selected_profile_id", "required_capability_ids", "topology_node_ids",
            "child_cell_input_ids", "runtime_outcome", "runtime_report_status",
            "complete_profile_status", "zero_runtime_counters",
        })
    if 11 <= number <= 27:
        return frozenset({
            "case_number", "mutated_path", "baseline_sha256", "attempted_sha256",
            "validation_report_id", "validation_target", "failure_stage", "reason_codes",
            "external_validation_report_id", "external_validation_target",
            "external_reason_codes", "created_before", "created_after",
            "topology_created_delta", "bundle_created_delta",
        })
    bounded_common = {
        "case_number", "policy_id", "accepted_bundle_validation_id",
    }
    if number == 28:
        return frozenset(bounded_common | {
            "accepted_depth_rows", "accepted_depths", "rejected_depth",
            "rejected_parent_cell_id", "rejected_input_id",
            "rejected_validation_report_id", "rejected_validation_target",
            "rejected_reason_codes", "rejected_runtime_object_delta",
        })
    if number == 29:
        return frozenset(bounded_common | {
            "attempted_value", "accepted_value", "baseline_input_id",
            "mutated_input_id", "validation_report_id", "validation_target",
            "reason_codes", "created_objects",
        })
    if number == 30:
        return frozenset(bounded_common | {
            "max_total_cells", "tree_shape", "depth_counts", "cell_rows",
            "parent_child_rows", "root_cell_id", "depth_1_cell_ids",
            "depth_2_cell_ids", "root_budget_event_rows", "accepted_cell_rows",
            "accepted_cell_ids", "accepted_cell_count", "planning_debit_count",
            "allocation_debit_count", "activate_debit_count",
            "cell_create_debit_count", "root_create_budget_id",
            "twenty_first_global_budget_id", "twenty_first_validation_report_id",
            "twenty_first_consumed_cell_count", "twenty_first_remaining_cell_count",
            "attempted_twenty_second_cell_id", "attempted_twenty_second_error",
            "attempted_twenty_second_parent_id",
            "attempted_twenty_second_global_budget_created",
            "rejected_budget_id", "rejected_validation_report_id",
            "rejected_validation_target", "rejected_reason_codes",
            "rejected_runtime_object_delta",
        })
    if number in {32, 33, 34}:
        return frozenset(bounded_common | {
            "attempted_value", "baseline_budget_id", "mutated_budget_id",
            "mutated_counter_fields", "validation_report_id", "validation_target",
            "reason_codes", "created_objects",
        })
    if number == 31:
        return frozenset(bounded_common | {
            "backpressure_id", "validation_report_id", "source_context_id",
            "topology_id", "topology_artifact_id", "queue_capacity",
            "running_count", "ready_count", "pending_count",
            "admission_order", "deferred_source_queue_id",
            "deferred_queue_entry_ids", "t03_decision_id",
            "deferred_successor_queue_id", "deferred_successor_artifact_id",
            "predecessor_queue_id", "admission_round", "deferred_state",
            "queue_reason_codes", "no_work_dropped", "created_objects",
        })
    if number == 35:
        return frozenset(bounded_common | {
            "mutation_rows", "mutation_count", "baseline_projection_id",
            "baseline_budget_id", "baseline_context_validation_id", "created_objects",
        })
    if number in {36, 37, 38}:
        return frozenset(bounded_common | {
            "queue_entry_id", "queue_validation_report_id",
            "source_validation_report_id", "observation_id",
            "observation_validation_report_id", "revision_index", "max_revise_count",
            "consecutive_non_positive_count", "derived_terminal_state", "reason_codes",
        })
    if number == 39:
        return frozenset(bounded_common | {
            "child_cell_id", "child_input_id", "baseline_child_result_id",
            "attempted_child_result_id", "attempted_outcome", "terminal_queue_rows",
            "result_proposal_id", "post_vv_report_id", "gt_report_id",
            "proposal_validation_report_id", "post_vv_validation_report_id",
            "gt_validation_report_id", "child_validation_report_id",
            "child_structural_validation_report_id", "result_artifact_id",
            "activation_causal_row", "child_reason_codes", "partial_failure_id",
            "partial_failure_validation_report_id", "parent_disposition", "required_child",
            "created_result_delta", "created_partial_failure_delta", "created_causal_delta",
            "safe_sibling_input_id", "safe_sibling_result_id",
            "safe_sibling_result_artifact_id", "safe_sibling_outcome",
            "safe_sibling_evidence_refs", "safe_sibling_report_refs",
            "safe_sibling_structural_validation_id",
            "safe_sibling_context_validation_id", "safe_sibling_before_sha256",
            "safe_sibling_after_sha256", "safe_sibling_unchanged",
            "safe_sibling_result_delta", "safe_sibling_causal_delta",
            "partial_failure_sibling_independent",
        })
    if number == 40:
        return frozenset(bounded_common | {
            "child_cell_id", "child_input_id", "baseline_child_result_id",
            "attempted_child_result_id", "attempted_outcome", "terminal_queue_rows",
            "result_proposal_id", "post_vv_report_id", "gt_report_id",
            "proposal_validation_report_id", "post_vv_validation_report_id",
            "gt_validation_report_id", "child_validation_report_id",
            "child_structural_validation_report_id", "result_artifact_id",
            "activation_causal_row", "child_reason_codes", "partial_failure_id",
            "partial_failure_validation_report_id", "parent_disposition", "required_child",
            "created_result_delta", "created_partial_failure_delta", "created_causal_delta",
            "gate_disposition", "gate_reason_codes",
            "gate_evidence_refs", "t06_decision_id", "validating_queue_id",
            "validating_artifact_id", "terminal_decision_id", "blocked_queue_id",
            "blocked_artifact_id", "blocked_validation_id", "no_child_invocation_delta",
            "no_child_result_delta", "no_child_partial_failure_delta",
            "no_child_terminal_delta",
            "merge_queue_id", "merge_validation_id", "merge_decision_is_none",
            "malformed_axis", "malformed_queue_id", "malformed_validation_id",
            "malformed_reason_codes", "malformed_error", "malformed_terminal_delta",
            "malformed_causal_delta", "malformed_bundle_delta",
        })
    if number == 41:
        return frozenset(bounded_common | {
            "mutation_rows", "mutation_count", "baseline_child_result_id",
            "no_created_objects",
        })
    matrix_common = {"case_number", "complete_profile_validation_id"}
    matrix_keys: dict[int, set[str]] = {
        42: {"construction_call_count", "first_report_id", "second_report_id", "first_sha256", "second_sha256", "repeated_value_equal", "repeated_id_equal", "repeated_bytes_equal"},
        43: {"result_postorder", "phase_rows", "parent_return_decision_id", "terminal_validation_ids", "causal_ref_sha256", "final_bundle_report_id", "cycle_validation_id", "cycle_reason_codes"},
        44: {"baseline_queue_ids", "baseline_artifact_ids", "mutation_rows", "mutation_count"},
        45: {"proposal_id", "expected_injected_time", "first_vv_report_id", "second_vv_report_id", "first_gt_report_id", "second_gt_report_id", "first_vv_sha256", "second_vv_sha256", "first_gt_sha256", "second_gt_sha256", "vv_validation_id", "gt_validation_id", "post_wall_clock_call_count", "gt_wall_clock_call_count"},
        46: {"counterfactual_validation_id", "causal_ref", "mutated_artifact_id", "changed_pointer", "accepted_bundle_ref"},
        47: {"ignored_counterfactual_validation_id", "ignored_causal_ref", "ignored_mutated_artifact_id", "accepted_bundle_ref", "admission_mutation_axis", "admission_baseline_source_artifact_id", "admission_mutated_source_artifact_id", "admission_accepted_causal_ref", "admission_profile_validation_id", "admission_profile_status", "admission_error", "admission_expected_downstream_artifact_id", "admission_child_input_delta", "admission_initial_queue_delta", "admission_initial_artifact_delta", "actual_gate_disposition", "actual_gate_reason_codes", "actual_gate_evidence_refs", "actual_gate_t06_decision_id", "actual_gate_validating_queue_id", "actual_gate_validating_artifact_id", "actual_gate_terminal_decision_id", "actual_gate_blocked_queue_id", "actual_gate_blocked_artifact_id", "actual_gate_validation_id", "actual_gate_terminal_delta", "actual_gate_invocation_delta", "actual_gate_downstream_delta", "blocked_gate_source_queue_id", "blocked_gate_source_artifact_id", "blocked_gate_downstream_queue_id", "blocked_gate_downstream_artifact_id", "blocked_gate_output_index", "blocked_gate_causal_ref", "blocked_gate_source_validation_id", "blocked_gate_downstream_validation_id", "blocked_gate_causal_validation_reasons", "blocked_gate_artifact_validation_reasons", "blocked_gate_bundle_validation_reasons", "blocked_gate_counterfactual_validation_reasons", "blocked_gate_mutated_source_sha256", "blocked_gate_generic_diagnostic_scope", "blocked_gate_row_in_accepted_runtime"},
        48: {"actual_child_result_rows", "no_child_result_ids", "no_child_partial_failure_ids", "invalid_child_ref_validation_id", "invalid_child_ref_reason_codes"},
        49: {"validation_chain_rows", "cycle_validation_id", "cycle_reason_codes"},
        50: {"aggregation_rows", "one_child_validation_id", "queue_entry_count", "budget_count", "runtime_abi_ref_count"},
        51: {"five_mode_template_rows", "mutation_axis", "mutated_node_id", "mutation_validation_id", "mutation_reason_codes"},
        52: {"source_binding_rows", "per_mode_substitution_count", "total_substitution_count"},
        53: {"allocation_predecessor_debit_rows", "event_counts", "mutation_rows", "mutation_count"},
        54: {"outcome_rows", "outcome_mapping_rows", "outcome_count"},
        55: {"root_result_id", "parent_return_decision_ids", "evaluated_root_decision_id", "root_final_budget_ids", "root_return_rule_ids", "child_rejection_reason"},
        56: {"artifact_ids", "artifact_types", "trace_unique", "field_partitions", "stage_artifact_counts", "stage_validation_ids", "queue_parent_form_names", "queue_parent_form_rows", "queue_reason_field_exact"},
        57: {"causal_pointer_reason_rows", "causal_validation_id", "terminal_causal_row_count", "activation_causal_row_count", "child_return_causal_row_count", "corruption_validation_id", "corruption_reason_codes", "corruption_causal_delta"},
        58: {"backpressure_precedence_rows", "backpressure_validation_ids", "deferred_successor_rows", "dependency_wait_row", "budget_blocked_row", "budget_exhaustion_resource", "budget_exhaustion_tree_shape", "budget_exhaustion_depth_counts", "budget_exhaustion_accepted_cell_ids", "budget_before_id", "budget_before_consumed_cell_count", "budget_before_remaining_cell_count", "exhausted_budget_id", "exhausted_budget_validation_id", "exhausted_consumed_cell_count", "exhausted_remaining_cell_count", "budget_exhaustion_t06_decision_id", "budget_exhaustion_terminal_decision_id", "budget_exhaustion_queue_delta", "budget_exhaustion_budget_delta", "budget_exhaustion_no_drop", "unique_state_per_round", "unchanged_t03_suppressed", "suppression_created_objects", "no_work_dropped", "runtime_queue_order", "queue_order_error"},
        59: {"policy_profile_separation", "profile_count", "policy_identity_count", "source_binding_identity_count", "substitution_validation_id", "substitution_reason_codes"},
        60: {"full_fractal_root_edges", "full_fractal_leaf_edges", "leaf_source_target_indexes", "leaf_edge_kinds", "topology_validation_id"},
        61: {"cell_global_event_pairing", "paired_event_rows", "budget_validation_ids", "create_only_debit_rows", "zero_delta_aggregate_rows", "mutation_rows"},
        62: {"pre_root_lifecycle", "outcome_lifecycle_rows", "forbidden_root_lifecycles", "final_output_created"},
        63: {"context_unique_gt_rows", "gt_validation_ids", "substitution_validation_id", "substitution_reason_codes", "result_gt_refs"},
        64: {"validation_status_stage_rows", "validation_targets", "failure_stages", "validation_target_count", "failure_stage_count", "explicit_pass_report_id", "explicit_failure_report_id", "explicit_failure_reason_codes", "causal_profile_sha256"},
        65: {"instance_snapshot_round_reason_rows", "queue_validation_ids", "blocked_reason_rows", "copied_queue_reason_validation_id", "copied_queue_reason_codes", "copied_proposal_status_validation_id", "copied_proposal_status_reason_codes", "rejected_copied_signal_count"},
        66: {"child_slot_input_node_order", "cell_result_order", "child_results_before_root", "parent_slot_rows", "merge_rows", "denied_slot_terminal_id", "denied_slot_artifact_id", "denied_slot_validation_id", "denied_slot_state", "denied_gate_disposition", "denied_gate_reason_codes", "denied_gate_evidence_refs", "denied_t06_decision_id", "denied_terminal_decision_id", "denied_terminal_delta", "denied_invocation_delta", "denied_result_delta", "denied_partial_failure_delta", "merge_validation_id", "merge_decision_is_none", "child_invocation_count"},
        67: {"root_result_id", "runtime_report_id", "report_artifact_id", "runtime_outcome", "public_return_bundle_type", "terminal_report_target", "terminal_report_status", "root_owned_outcome", "staged_public_function_counts", "module_public_function_count"},
        68: {"two_child_runtime_rows", "four_child_structural_rows", "four_child_parent_basis_id", "four_child_index_order", "four_child_cell_share_sum", "four_child_revise_share_sum", "four_child_context_validation_id", "four_child_context_validation_status", "four_child_context_reason_codes", "four_child_runtime_projection_count", "four_child_derivation_rows"},
        69: {"planned_child_ids", "planned_basis_consumed_cell_count", "activated_child_ids", "activation_rows", "first_initial_downstreams", "accepted_cell_create_rows", "valid_denial_disposition", "valid_denial_queue_id", "valid_denial_artifact_id", "valid_denial_validation_id", "valid_denial_invocation_delta", "malformed_candidate_validation_id", "malformed_candidate_reason_codes", "malformed_candidate_created_terminals"},
        70: {"transition_decision_ids", "runtime_trace_transition_refs", "budget_order", "queue_order", "parent_return_decision_id", "parent_return_decision_position", "parent_return_decision_rule_id", "paired_budget_positions", "parent_return_queue_positions", "parent_return_terminal_queue_id", "parent_return_terminal_artifact_id", "construction_dependency_rows", "signature_90_validation_ids", "root_return_decision_id", "root_return_decision_position", "parent_return_result_id", "post_hoc_mapping_count"},
        71: {"ordered_revise_ids", "observation_validation_id", "transition_rule_id", "revised_cell_budget_id", "revised_global_budget_id", "revised_queue_entry_id", "revised_queue_validation_id", "future_revision_error", "mutation_rows"},
        72: {"prebundle_validation_ids", "retained_result_report_rows", "actual_child_result_ids", "causal_ref_count", "causal_validation_id", "stage_d_a_artifact_count", "stage_d_b_artifact_count", "stage_d_c_artifact_count", "stage_d_c_validation_id", "reconstructed_runtime_report_id", "reconstructed_report_validation_id", "final_runtime_trace_id", "final_runtime_report_id", "final_report_artifact_id", "complete_profile_status"},
    }
    if number not in matrix_keys:
        raise RuntimeError("g2d5_detail_contract_unmapped")
    return frozenset(matrix_common | matrix_keys[number])


_DETAIL_KEY_CONTRACTS_V02 = {
    spec.case_id: _detail_keys_for_case_v02(number)
    for number, spec in enumerate(_CASE_SPECS, start=1)
}
if len(_DETAIL_KEY_CONTRACTS_V02) != 72:
    raise RuntimeError("g2d5_detail_contract_count_invalid")


@dataclass(frozen=True)
class FractalRuntimeG2DCaseResultV02:
    case_id: str
    case_class: str
    domain_id: str | None
    accepted_mode: str | None
    expected_outcome: str
    observed_outcome: str
    source_family_sha256: str | None
    topology_id: str | None
    runtime_report_id: str | None
    external_validation_report_id: str | None
    evidence_refs: tuple[str, ...]
    evidence_material_json: str
    evidence_sha256: str
    topology_created_count: int
    provider_calls: int
    model_calls: int
    gemini_calls: int
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
    final_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class FractalRuntimeG2DReportV02:
    report_version: str
    report_id: str
    profile_id: str
    domain_order: tuple[str, ...]
    case_order: tuple[str, ...]
    case_results: tuple[FractalRuntimeG2DCaseResultV02, ...]
    constructive_case_count: int
    negative_case_count: int
    domain_positive_case_count: int
    accepted_bundle_count: int
    counterfactual_case_count: int
    topology_created_count: int
    provider_calls: int
    model_calls: int
    gemini_calls: int
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
    final_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class _AcceptedRunV02:
    domain_id: str
    mode: str
    source_family_sha256: str
    source_context: fr.FractalRuntimeSourceContextV02
    bundle: fr.FractalRuntimeExecutionBundleV02
    external_report: fr.FractalRuntimeValidationReportV02


@dataclass(frozen=True)
class _BackpressureWitnessV02:
    source_context: fr.FractalRuntimeSourceContextV02
    topology: fr.RuntimeExecutionTopologyV02
    topology_artifact_id: str
    policy_id: str
    s0: fr.FractalBackpressureStateV02
    s0_validation: fr.FractalRuntimeValidationReportV02
    s1: fr.FractalBackpressureStateV02
    s1_validation: fr.FractalRuntimeValidationReportV02
    deferred_source: fr.FractalCellQueueEntryV02
    first_deferred: fr.FractalCellQueueEntryV02
    first_deferred_artifact: abi.KernelArtifactV01
    first_t03_decision: transition_registry.TransitionDecisionV01
    second_deferred: fr.FractalCellQueueEntryV02
    second_deferred_artifact: abi.KernelArtifactV01
    second_t03_decision: transition_registry.TransitionDecisionV01
    suppression_before_ids: tuple[str, ...]
    suppression_after_ids: tuple[str, ...]
    dependency_wait: fr.FractalCellQueueEntryV02
    dependency_wait_validation: fr.FractalRuntimeValidationReportV02
    dependency_wait_decision_is_none: bool
    queue_order: tuple[str, ...]
    queue_order_error: str


@dataclass(frozen=True)
class _GateBoundaryWitnessV02:
    source_context: fr.FractalRuntimeSourceContextV02
    topology: fr.RuntimeExecutionTopologyV02
    gate_disposition: str
    gate_reason_codes: tuple[str, ...]
    gate_evidence_refs: tuple[str, ...]
    t06_decision: transition_registry.TransitionDecisionV01
    validating_entry: fr.FractalCellQueueEntryV02
    validating_artifact: abi.KernelArtifactV01
    terminal_decision: transition_registry.TransitionDecisionV01
    blocked_entry: fr.FractalCellQueueEntryV02
    blocked_artifact: abi.KernelArtifactV01
    blocked_validation: fr.FractalRuntimeValidationReportV02
    merge_entry: fr.FractalCellQueueEntryV02
    merge_validation: fr.FractalRuntimeValidationReportV02
    merge_decision_is_none: bool
    invocation_before_ids: tuple[str, ...]
    invocation_after_ids: tuple[str, ...]
    result_before_ids: tuple[str, ...]
    result_after_ids: tuple[str, ...]
    partial_before_ids: tuple[str, ...]
    partial_after_ids: tuple[str, ...]
    denial_terminal_before_ids: tuple[str, ...]
    denial_terminal_after_ids: tuple[str, ...]
    malformed_axis: str
    malformed_entry: fr.FractalCellQueueEntryV02
    malformed_validation: fr.FractalRuntimeValidationReportV02
    malformed_error: str
    malformed_terminal_before_ids: tuple[str, ...]
    malformed_terminal_after_ids: tuple[str, ...]
    malformed_causal_before_ids: tuple[str, ...]
    malformed_causal_after_ids: tuple[str, ...]
    malformed_bundle_before_ids: tuple[str, ...]
    malformed_bundle_after_ids: tuple[str, ...]
    admission_mutation_axis: str
    admission_baseline_source_artifact: abi.KernelArtifactV01
    admission_mutated_source_artifact: abi.KernelArtifactV01
    admission_accepted_causal_ref: abi.CausalConsumptionRefV01
    admission_profile_validation: fr.FractalRuntimeValidationReportV02
    admission_error: str
    admission_expected_downstream_artifact_id: None
    admission_child_input_before_ids: tuple[str, ...]
    admission_child_input_after_ids: tuple[str, ...]
    admission_initial_queue_before_ids: tuple[str, ...]
    admission_initial_queue_after_ids: tuple[str, ...]
    admission_initial_artifact_before_ids: tuple[str, ...]
    admission_initial_artifact_after_ids: tuple[str, ...]


@dataclass(frozen=True)
class _BlockedGateCausalProofV02:
    source_entry: fr.FractalCellQueueEntryV02
    source_artifact: abi.KernelArtifactV01
    source_validation: fr.FractalRuntimeValidationReportV02
    downstream_entry: fr.FractalCellQueueEntryV02
    downstream_artifact: abi.KernelArtifactV01
    downstream_validation: fr.FractalRuntimeValidationReportV02
    output_index: int
    causal_ref: abi.CausalConsumptionRefV01
    causal_validation_reasons: tuple[str, ...]
    artifact_validation_reasons: tuple[str, ...]
    bundle_validation_reasons: tuple[str, ...]
    generic_counterfactual_validation_reasons: tuple[str, ...]
    generic_mutated_source_sha256: str


@dataclass(frozen=True)
class _DepthBoundaryWitnessV02:
    accepted_inputs: tuple[fr.FractalCellInputV02, ...]
    accepted_validations: tuple[fr.FractalRuntimeValidationReportV02, ...]
    rejected_input: fr.FractalCellInputV02
    rejected_validation: fr.FractalRuntimeValidationReportV02
    runtime_objects_before: tuple[str, ...]
    runtime_objects_after: tuple[str, ...]


@dataclass(frozen=True)
class _CellTreeBuildV02:
    budget_suffix: tuple[fr.FractalRuntimeBudgetV02, ...]
    accepted_cell_rows: tuple[dict[str, object], ...]
    cell_rows: tuple[dict[str, object], ...]
    parent_child_rows: tuple[dict[str, object], ...]
    accepted_cell_ids: tuple[str, ...]
    depth_1_cell_ids: tuple[str, ...]
    depth_2_cell_ids: tuple[str, ...]
    final_global_budget: fr.FractalRuntimeBudgetV02
    final_global_validation: fr.FractalRuntimeValidationReportV02
    attempted_cell_id: str
    attempted_parent_id: str
    attempted_error: str
    attempted_global_budget: fr.FractalRuntimeBudgetV02 | None


@dataclass(frozen=True)
class _CellBoundaryWitnessV02:
    tree_shape: tuple[int, int, int]
    depth_counts: tuple[tuple[int, int], ...]
    cell_rows: tuple[dict[str, object], ...]
    parent_child_rows: tuple[dict[str, object], ...]
    root_cell_id: str
    depth_1_cell_ids: tuple[str, ...]
    depth_2_cell_ids: tuple[str, ...]
    root_budget_event_rows: tuple[tuple[object, ...], ...]
    accepted_cell_rows: tuple[dict[str, object], ...]
    accepted_cell_ids: tuple[str, ...]
    budget_suffix: tuple[fr.FractalRuntimeBudgetV02, ...]
    final_global_budget: fr.FractalRuntimeBudgetV02
    final_global_validation: fr.FractalRuntimeValidationReportV02
    attempted_cell_id: str
    attempted_parent_id: str
    attempted_error: str
    attempted_global_budget: fr.FractalRuntimeBudgetV02 | None
    rejected_budget: fr.FractalRuntimeBudgetV02
    rejected_validation: fr.FractalRuntimeValidationReportV02
    runtime_objects_before: tuple[str, ...]
    runtime_objects_after: tuple[str, ...]


@dataclass(frozen=True)
class _BudgetExhaustionWitnessV02:
    tree_shape: tuple[int, int, int]
    depth_counts: tuple[tuple[int, int], ...]
    accepted_cell_ids: tuple[str, ...]
    budget_before: fr.FractalRuntimeBudgetV02
    exhausted_budget: fr.FractalRuntimeBudgetV02
    exhausted_validation: fr.FractalRuntimeValidationReportV02
    t06_decision: transition_registry.TransitionDecisionV01
    blocked_entry: fr.FractalCellQueueEntryV02
    blocked_artifact: abi.KernelArtifactV01
    blocked_validation: fr.FractalRuntimeValidationReportV02
    terminal_decision: transition_registry.TransitionDecisionV01
    budget_before_ids: tuple[str, ...]
    budget_after_ids: tuple[str, ...]
    queue_before_ids: tuple[str, ...]
    queue_after_ids: tuple[str, ...]


@dataclass(frozen=True)
class _InvokedChildFailureWitnessV02:
    source_context: fr.FractalRuntimeSourceContextV02
    topology: fr.RuntimeExecutionTopologyV02
    child_input: fr.FractalCellInputV02
    baseline_result: fr.FractalCellResultV02
    terminal_entries: tuple[fr.FractalCellQueueEntryV02, ...]
    result_proposal_id: str
    post_vv_report_id: str
    gt_report_id: str
    proposal_validation: fr.FractalRuntimeValidationReportV02
    post_vv_validation: fr.FractalRuntimeValidationReportV02
    gt_validation: fr.FractalRuntimeValidationReportV02
    result_validation: fr.FractalRuntimeValidationReportV02
    result: fr.FractalCellResultV02
    result_artifact: abi.KernelArtifactV01
    partial_failure: fr.FractalPartialFailureRecordV02
    partial_validation: fr.FractalRuntimeValidationReportV02
    activation_causal_row: tuple[str, ...]
    result_before_ids: tuple[str, ...]
    result_after_ids: tuple[str, ...]
    partial_before_ids: tuple[str, ...]
    partial_after_ids: tuple[str, ...]
    causal_before_ids: tuple[str, ...]
    causal_after_ids: tuple[str, ...]
    safe_sibling_input: fr.FractalCellInputV02
    safe_sibling_result: fr.FractalCellResultV02
    safe_sibling_result_artifact: abi.KernelArtifactV01
    safe_sibling_structural_validation: fr.FractalRuntimeValidationReportV02
    safe_sibling_context_validation: fr.FractalRuntimeValidationReportV02
    safe_sibling_before_sha256: str
    safe_sibling_after_sha256: str
    safe_sibling_result_before_ids: tuple[str, ...]
    safe_sibling_result_after_ids: tuple[str, ...]
    safe_sibling_causal_before_ids: tuple[str, ...]
    safe_sibling_causal_after_ids: tuple[str, ...]


def _plain_value_v02(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _plain_value_v02(getattr(value, item.name))
            for item in fields(value)
        }
    if type(value) is dict:
        return {
            str(key): _plain_value_v02(item)
            for key, item in sorted(value.items(), key=lambda row: str(row[0]))
        }
    if type(value) is tuple:
        return [_plain_value_v02(item) for item in value]
    if type(value) is list:
        return [_plain_value_v02(item) for item in value]
    if type(value) is bytes:
        return {"bytes_hex": value.hex()}
    if value is None or type(value) in {bool, int, float, str}:
        return value
    raise TypeError(type(value).__name__)


def _sha256_plain_v02(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes_v01(_plain_value_v02(value))).hexdigest()


def _domain_slug_v02(domain_id: str) -> str:
    return "travel" if domain_id == DOMAIN_ORDER[0] else "warehouse"


def _build_bsep_family_v02(
    *,
    mode: str,
    request_id: str,
    domain_id: str,
) -> dict[str, dict[str, object]]:
    label = f"{_domain_slug_v02(domain_id)}:{mode.replace('_', '-')}"
    route_id = f"route:g2d5:{label}"
    proposal_id = f"proposal:g2d5:{label}"
    vector_ids = (f"vector:g2d5:{label}",)
    guards = ("guard:g2d5:root-review",)
    business = context_packets.build_business_request_context_packet(
        packet_id=f"context_packet:g2d5:{label}:business",
        created_by="runtime:g2d5:proof",
        domain=domain_id,
        request_id=request_id,
        business_subject="bounded_runtime_topology",
        requested_action="root_review",
        user_visible_summary="Bounded topology source review.",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": domain_id,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id=f"context_packet:g2d5:{label}:route",
        created_by="runtime:g2d5:proof",
        source_refs=(business_ref,),
        domain=domain_id,
        allowed_routes=(route_id,),
        required_guards=guards,
        selected_vector_ids=vector_ids,
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
        "selected_vector_ids": vector_ids,
        "required_guards": guards,
        "reason": "Bounded deterministic topology review is required.",
        "confidence": 0.66,
        "needs_review": True,
        "uncertainty_notes": ("Source evidence remains advisory.",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "semantic_observations": ("A bounded topology route is available.",),
        "route_reasoning": ("Use deterministic mode selection.",),
        "rejected_route_reasoning": ("Unsupported action remains forbidden.",),
        "guard_reasoning": ("Root review remains mandatory.",),
        "vector_reasoning": ("The bounded vector matches the request.",),
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
    rationale_sha = hashlib.sha256(canonical_json_bytes_v01(rationale)).hexdigest()

    def item(text: str, kind: str) -> dict[str, object]:
        return context_packets.semantic_evidence_item(
            text,
            source="runtime_canonicalization",
            evidence_kind=kind,
            confidence_label="medium",
        )

    packet = context_packets.build_bounded_semantic_evidence_packet(
        packet_id=f"context_packet:g2d5:{label}:bsep",
        source_refs=(business_ref,),
        domain=domain_id,
        source_role="orchestrator",
        target_role="architect",
        source_route_id=route_id,
        source_proposal_id=proposal_id,
        source_context_packet_id=route["packet_id"],
        source_structured_rationale_ref="structured_rationale_v01:" + rationale_sha,
        observed_semantic_facts=(item("A bounded route is present.", "observed_fact"),),
        missing_evidence=(item("Root review is pending.", "missing_evidence"),),
        uncertainty_notes=(item("Source evidence remains advisory.", "uncertainty"),),
        risk_boundary_notes=(item("No action authority is present.", "risk_boundary"),),
        rejected_action_routes=(item("Unsupported action is forbidden.", "rejected_route"),),
        required_approvals_or_conditions=(item("Root review is required.", "approval_condition"),),
        authority_boundary_notes=(item("Root remains final authority.", "authority_boundary"),),
        selected_vector_ids=vector_ids,
        required_guards=guards,
    )
    return {
        "business": business,
        "route": route,
        "proposal": proposal,
        "rationale": rationale,
        "packet": packet,
    }


def _build_memory_family_v02(
    *,
    request_id: str,
    domain_id: str,
    root_id: str,
    scope_ref: str,
    direct: bool = False,
) -> dict[str, object]:
    label = _domain_slug_v02(domain_id)
    address = drs_semantic.build_semantic_address_v01(
        namespace="g2d5_v02",
        domain=domain_id,
        subject_class="bounded_information",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    scope_sha256 = hashlib.sha256(scope_ref.encode("utf-8")).hexdigest()
    envelope = drs_semantic.build_drs_time_envelope_v01(
        pt_created_at=EVALUATION_TIME,
        kt_as_of=EVALUATION_TIME,
        et_observed_at=EVALUATION_TIME,
        ct_context_anchor=EVALUATION_TIME,
        ttl_seconds=3600,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        source_observed_at=EVALUATION_TIME,
        source_reported_at=EVALUATION_TIME,
        system_ingested_at=EVALUATION_TIME,
        system_verified_at=EVALUATION_TIME,
        freshness_policy_id="freshness:g2d5:v02",
    )
    authority = drs_semantic.build_drs_authority_envelope_v01(
        authority_class="ROOT_ACCEPTED_WORK" if direct else "ROOT_ACCEPTED_CONTEXT",
        owning_local_root_id=root_id,
        source_root_decision_input_id=f"root-input:g2d5:{label}:memory",
        source_root_decision_id=f"root-decision:g2d5:{label}:memory",
        source_root_decision_hash=hashlib.sha256(
            f"g2d5:{label}:memory-root".encode("utf-8")
        ).hexdigest(),
        authority_scope_fingerprint=scope_sha256,
        root_acceptance_state="ACCEPTED_WORK" if direct else "ACCEPTED_CONTEXT",
        recording_component=MODULE_ID,
    )
    record = drs_semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Bounded deterministic context for topology routing.",
        semantic_tags=("bounded", "g2d5"),
        resonance_reason="Exact deterministic semantic-address match.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=(f"source:g2d5:{label}:memory",),
        lineage_edges=(),
        time_envelope=envelope,
        authority_envelope=authority,
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT" if direct else "CONTEXT_ONLY",
        policy_version="policy:g2d5:memory:v02",
        schema_versions=("v0.1",),
        content_fingerprint=hashlib.sha256(
            f"g2d5:{label}:memory-record".encode("utf-8")
        ).hexdigest(),
        recording_component=MODULE_ID,
    )
    query = drs_resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE" if direct else "MEMORY_CONTEXT_ONLY",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_sha256,
        as_of=EVALUATION_TIME,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=(
            "INJECTED_CURRENT_DECISION_TIME" if direct else "INJECTED_ANALYSIS_TIME"
        ),
        time_range_start=EVALUATION_TIME,
        time_range_end=VALID_TO_TIME,
        required_time_axes=(
            ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")
            if direct
            else ("KT", "TTL", "VALIDITY")
        ),
        freshness_policy_id="freshness:g2d5:v02",
        max_age_seconds=3600,
        domain=domain_id,
        risk_class="LOW",
        reuse_intent=(
            "INFORMATIONAL_SHORTCUT_CONSIDERATION" if direct else "CONTEXT"
        ),
        requested_reuse_classes=(
            ("ANSWER_SHORTCUT",) if direct else ("CONTEXT_ONLY",)
        ),
        required_evidence_classes=(
            "SOURCE_IDENTITY",
            "SOURCE_INTEGRITY",
            "PROVENANCE_CHAIN",
            "TIME_FITNESS",
            "POLICY_COMPATIBILITY",
            "SCHEMA_COMPATIBILITY",
            "CONFLICT_CLEARANCE",
            "ROOT_DECISION",
            "SOURCE_HISTORY",
        ),
        forbidden_changes=("POLICY_CHANGED",),
        policy_version="policy:g2d5:memory:v02",
        schema_versions=("v0.1",),
        owning_local_root_id=root_id,
    )
    evaluation = drs_resolution.evaluate_drs_candidate_v01(
        semantic_address=address,
        query=query,
        meaning_record=record,
        action_history_binding=None,
    )
    legacy = {
        "record_id": f"legacy:g2d5:{label}:memory",
        "layer": "work",
        "type": "generic",
        "domain": domain_id,
        "content": {"summary": "Bounded deterministic memory context."},
        "time_envelope": {
            "pt_created_at": "2026-08-01T00:00:00Z",
            "kt_asof": "2026-08-01T00:00:00Z",
            "et_observed_at": "2026-08-01T00:00:00Z",
            "ct_session_anchor": f"case:g2d5:{label}:memory",
            "ttl_seconds": 3600,
            "freshness_class": "static",
            "valid_from": "2026-08-01T00:00:00Z",
            "valid_to": "2026-08-01T01:00:00Z",
        },
        "provenance": {
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "status": "active",
    }
    projection = drs_compatibility.build_legacy_drs_projection_v01(
        source_family="LOCAL_DRS_DICT",
        source=legacy,
        target_semantic_address=address,
    )
    budget = drs_resolution.build_memory_descent_budget_v01(
        max_depth=0,
        max_records_opened=1,
        max_pointers_opened=0,
        max_artifacts_opened=0,
        max_bytes_opened=0,
        max_lineage_edges=0,
        max_conflict_records=0,
    )
    plan = drs_resolution.build_retrieval_plan_v01(
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
    report_arguments = dict(
        semantic_address=address,
        query=query,
        source_projections=(projection,),
        source_records=(record,),
        query_evaluations=(evaluation,),
        retrieval_plan=plan,
        memory_descent_result=None,
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
    if not direct:
        report = drs_resolution.build_drs_resolution_report_v01(
            **report_arguments,
            eligible_candidates=(),
            ranked_candidate_ids=(),
            selected_candidate_id=None,
            root_shortcut_projection=None,
            reuse_certificate=None,
            context_only_record_ids=(record.meaning_record_id,),
        )
        return {
            "transaction_id": query.query_id,
            "report": report,
            "projections": (projection,),
            "use_time": EVALUATION_TIME,
        }

    candidate = drs_resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        semantic_similarity_units=9000,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=9000,
        lineage_proximity_units=7000,
        historical_utility_units=6000,
        gt_advisory_prior_units=1000,
        conflict_penalty_units=0,
        risk_penalty_units=0,
        retrieval_cost_units=100,
    )
    ranked = drs_resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=(evaluation,),
        candidates=(candidate,),
    )
    claim_preimage = {
        "profile_version": "v0.1",
        "semantic_address_id": address.semantic_address_id,
        "meaning_record_id": record.meaning_record_id,
        "query_id": query.query_id,
        "query_evaluation_id": evaluation.query_evaluation_id,
        "resolution_candidate_id": candidate.resolution_candidate_id,
        "reuse_class": "ANSWER_SHORTCUT",
        "case_type": "NON_ACTION_INFORMATIONAL",
        "scope_fingerprint": query.scope_fingerprint,
        "policy_version": query.policy_version,
        "schema_versions": list(query.schema_versions),
        "required_evidence_classes": list(query.required_evidence_classes),
        "observed_evidence_fingerprint": evaluation.observed_evidence_fingerprint,
        "forbidden_changes": list(query.forbidden_changes),
        "checked_dependency_fingerprint": evaluation.checked_dependency_fingerprint,
        "source_history_hash": evaluation.source_history_hash,
        "action_history_binding_id": None,
        "valid_from": EVALUATION_TIME,
        "valid_to": VALID_TO_TIME,
        "issued_at": EVALUATION_TIME,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": "policy:drs_answer_shortcut:v0.1",
    }
    actor_id = f"actor:g2d5:{label}:direct-reuse"
    work_request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic-work-request:g2d5:{label}:direct-reuse",
        transaction_id=query.query_id,
        target_root_id=root_id,
        runtime_topology_ref="g2d5:runtime_topology:not_created",
        bounded_context_refs=(f"context:g2d5:{label}:direct-reuse",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence-binding:g2d5:{label}:direct-reuse",
        evidence_ref=f"evidence:g2d5:{label}:direct-reuse",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id=actor_id,
        provenance_ref=f"provenance:g2d5:{label}:direct-reuse",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id,
        predicate="authorize_non_action_informational_answer_shortcut_v01",
        object_or_value=claim_preimage,
        time_envelope_ref=f"time-envelope:g2d5:{label}:direct-reuse",
        provenance_refs=(f"provenance:g2d5:{label}:direct-reuse",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1000000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2d5:{label}:direct-reuse",
        request_id=work_request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:g2d5:{label}:direct-reuse",
        scope=address.semantic_address_id,
        bounded_context_refs=(f"context:g2d5:{label}:direct-reuse",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    review_packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=work_request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    root_kernel = root_decision.build_root_decision_kernel_v01()
    root_input = root_decision.build_root_decision_input_v01(
        transaction_id=query.query_id,
        target_root_id=root_id,
        root_review_packet=review_packet,
        post_vv_bundle={
            "bundle_id": f"post-vv:g2d5:{label}:direct-reuse",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate.resolution_candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": f"gt:g2d5:{label}:direct-reuse",
            "candidate_ids": [candidate.resolution_candidate_id],
            "selected_candidate_id": candidate.resolution_candidate_id,
            "score_micros_by_candidate": {candidate.resolution_candidate_id: 500000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        policy_state={
            "policy_id": f"policy:g2d5:{label}:direct-reuse",
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": False,
            "user_permission_present": False,
            "permission_scope_valid": True,
            "permission_ref": None,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": f"time-envelope:g2d5:{label}:direct-reuse",
        },
        conflict_state={"material_unresolved_conflict": False, "conflict_set_ids": []},
        prior_root_state={
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    )
    root_result = root_decision.decide_root_v01(
        kernel=root_kernel,
        decision_input=root_input,
    )
    _require_v02(root_result.decision == "ACCEPT", "g2d5_direct_reuse_root_reject")
    root_hash = domain_separated_sha256_hex_v01(
        domain="hedgehog:drs:root_shortcut_root_result_binding:v01",
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(root_result)
        ),
    )
    root_projection = reuse_certificate.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id=root_id,
        root_kernel_id=root_kernel.kernel_id,
        root_decision_input_id=root_input.decision_input_id,
        root_decision_id=root_result.decision_id,
        root_decision_hash=root_hash,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT",
        scope_fingerprint=scope_sha256,
        policy_version=query.policy_version,
        schema_versions=query.schema_versions,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        root_shortcut_policy_ref="policy:drs_answer_shortcut:v0.1",
    )
    certificate = reuse_certificate.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=root_projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluation.observed_evidence_fingerprint,
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluation.checked_dependency_fingerprint,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=EVALUATION_TIME,
        evaluated_at=evaluation.evaluated_at,
    )
    report = drs_resolution.build_drs_resolution_report_v01(
        **report_arguments,
        eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(item.resolution_candidate_id for item in ranked),
        selected_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_projection=root_projection,
        reuse_certificate=certificate,
        context_only_record_ids=(),
    )
    _require_v02(
        reuse_certificate.validate_existing_root_shortcut_decision_v01(
            resolution_report=report,
            root_kernel=root_kernel,
            root_decision_input=root_input,
            root_decision_result=root_result,
            use_time=EVALUATION_TIME,
        ) == (True, ()),
        "g2d5_direct_reuse_certificate_invalid",
    )
    return {
        "transaction_id": query.query_id,
        "report": report,
        "projections": (projection,),
        "use_time": EVALUATION_TIME,
        "root_kernel": root_kernel,
        "root_input": root_input,
        "root_result": root_result,
    }


def _build_replay_family_v02(
    *,
    mode: str,
    request_id: str,
    domain_id: str,
) -> dict[str, object]:
    label = f"g2d5-{_domain_slug_v02(domain_id)}-{mode.replace('_', '-')}"
    kernel_hash = hashlib.sha256(
        canonical_json_bytes_v01((domain_id, request_id, "sealed_replay"))
    ).hexdigest()
    programme = evidence_profile.build_programme_evidence_identity_v01(
        programme_id=f"{label}_programme_v01",
        programme_version="v0.1",
    )
    execution = evidence_profile.build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=domain_id,
        execution_head="abcdef1",
        source_task_id=f"task:{label}",
        run_id=f"run:{label}",
        report_id=f"report:{label}",
    )
    attempt = evidence_profile.build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=execution,
        attempt_number=1,
        package_id=f"package:{label}",
        logical_package_ref=f"g2d5/{label}",
        output_directory_ref=f"g2d5/{label}/output",
        provider_mode="deterministic_fixture",
        model_id="none",
        expected_actor_count=1,
        provider_call_budget=0,
    )
    source = evidence_profile.build_safe_source_record_v01(
        source_id=f"source:{label}:replay",
        source_type="g2d5_replay_fixture",
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
        artifact_id=f"artifact:{label}:replay",
        artifact_type="g2d5_replay_fixture",
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
        evidence_refs=(f"evidence:{label}:replay",),
        limitation_refs=("limitation:g2d5:local-only",),
    )
    content = canonical_json_bytes_v01(
        {"domain": domain_id, "hash": kernel_hash}
    ) + b"\n"
    file_record = sealed_package.build_safe_file_record_v01(
        logical_path=f"evidence/{label}.json",
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
        evidence_refs=(f"evidence:{label}:replay", f"anchor:{label}"),
    )
    return {
        "replay": replay,
        "manifest": manifest,
        "projection": projection,
        "contents": (content,),
        "publication": publication,
        "verification": verification,
    }


def _build_execution_mode_source_context_v02(
    *,
    bsep: dict[str, dict[str, object]],
    snapshot: g2c.ExecutionModeLocalRoutingSnapshotV01,
    memory: dict[str, object] | None,
    replay: dict[str, object] | None = None,
) -> g2c.ExecutionModeSourceContextV01:
    memory = memory or {}
    replay = replay or {}
    return g2c.build_execution_mode_source_context_v01(
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
        g2a_inspection=None,
        g2a_registry=None,
        g2a_packet_id=None,
        g2a_corridor=None,
        g2a_corridor_step=None,
        g2a_current_dependency_observations=(),
        g2a_logical_time_bridge=None,
        g2a_evaluation_time=snapshot.evaluation_time_epoch_seconds,
        g2a_evaluation_time_source=snapshot.created_by,
        g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2a_transition_registry_profile=None,
        g2b_resolution_report=memory.get("report"),
        g2b_compatibility_projections=memory.get("projections", ()),
        g2b_use_time=memory.get("use_time"),
        g2b_root_kernel=memory.get("root_kernel"),
        g2b_root_decision_input=memory.get("root_input"),
        g2b_root_decision_result=memory.get("root_result"),
        g2b_writeback_evidence=None,
    )


def _require_pass_v02(report: object, *, label: str) -> None:
    status = getattr(report, "validation_status", getattr(report, "status", None))
    reasons = getattr(report, "reason_codes", ())
    if status != "PASS" or reasons != ():
        raise ValueError(f"{label}:{status}:{reasons}")


def _build_runtime_source_family_v02(
    *,
    domain_id: str,
    mode: str,
    narrow: bool,
    action_packet_required: bool,
) -> fr.FractalRuntimeSourceContextV02:
    slug = _domain_slug_v02(domain_id)
    request_id = f"request:g2d5:{slug}:{mode}:v02"
    root_id = f"root:g2d5:{slug}:v02"
    scope_ref = f"scope:g2d5:{slug}:{mode}:v02"
    memory = (
        _build_memory_family_v02(
            request_id=request_id,
            domain_id=domain_id,
            root_id=root_id,
            scope_ref=scope_ref,
        )
        if mode == "memory_informed"
        else None
    )
    transaction_id = (
        str(memory["transaction_id"])
        if memory is not None
        else f"transaction:g2d5:{slug}:{mode}:v02"
    )
    selected_index = (
        g2c.EXECUTABLE_EXECUTION_MODES_V01.index(mode)
        if mode in g2c.EXECUTABLE_EXECUTION_MODES_V01
        else 0
    )
    profiles = tuple(
        g2c.build_execution_mode_local_mode_profile_v01(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=root_id,
            domain_id=domain_id,
            mode=candidate,
            policy_snapshot_id=f"policy:g2d5:{slug}:{mode}:v02",
            capability_snapshot_id=f"capabilities:g2d5:{slug}:{mode}:v02",
            cost_model_id="cost:g2d5:v02",
            policy_allowed=index >= selected_index,
            scope_allowed=True,
            risk_allowed=True,
            privacy_allowed=True,
            capability_state=(
                "NOT_REQUIRED"
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else "AVAILABLE"
            ),
            capability_id=(
                None
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else f"capability:g2d5:{slug}:{candidate}:v02"
            ),
            cost_units=index + 1,
        )
        for index, candidate in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01)
    )
    accepted_scope_ref = f"{scope_ref}:narrow"
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        request_class=(
            "BOUNDED_FRACTAL_REQUIRED"
            if mode == "full_fractal"
            else "BOUNDED_REVIEW"
        ),
        action_class="ACTION" if action_packet_required else "NON_ACTION",
        action_packet_relation=(
            "NEW_ACTION_NO_PACKET"
            if action_packet_required
            else "NOT_APPLICABLE"
        ),
        scope_class="BOUNDED",
        scope_ref=scope_ref,
        permitted_narrower_scope_refs=(accepted_scope_ref,) if narrow else (),
        risk_class="LOW",
        policy_snapshot_id=f"policy:g2d5:{slug}:{mode}:v02",
        capability_snapshot_id=f"capabilities:g2d5:{slug}:{mode}:v02",
        cost_model_id="cost:g2d5:v02",
        required_user_input_state="COMPLETE",
        hard_block_state="CLEAR",
        evaluation_time_epoch_seconds=EVALUATION_TIME,
        pt_created_at_utc=EVALUATION_UTC,
        et_observed_at_utc=EVALUATION_UTC,
        ct_session_anchor=f"ct:g2d5:{slug}:{mode}:v02",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC,
        mode_profiles=profiles,
    )
    bsep = _build_bsep_family_v02(
        mode=mode,
        request_id=request_id,
        domain_id=domain_id,
    )
    source = _build_execution_mode_source_context_v02(
        bsep=bsep,
        snapshot=snapshot,
        memory=memory,
    )
    _require_pass_v02(
        g2c.validate_execution_mode_source_context_v01(source),
        label="g2c_source",
    )
    common = {
        "request_id": request_id,
        "transaction_id": transaction_id,
        "owning_root_id": root_id,
        "domain_id": domain_id,
    }
    router_input = g2c.build_execution_mode_router_input_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(
            **common,
            source_context=source,
        ),
        local_routing_snapshot=snapshot,
        replay_binding=g2c.build_execution_mode_replay_not_applicable_binding_v01(
            **common,
        ),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=EVALUATION_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        ),
        g2b_binding=(
            g2c.build_execution_mode_g2b_binding_v01(
                **common,
                source_context=source,
            )
            if memory is not None
            else g2c.build_execution_mode_g2b_not_applicable_binding_v01(**common)
        ),
    )
    _require_pass_v02(
        g2c.validate_execution_mode_router_input_against_sources_v01(
            router_input=router_input,
            source_context=source,
        ),
        label="g2c_router_input",
    )
    proposal, route_report = g2c.route_execution_mode_v01(
        router_input=router_input,
        source_context=source,
    )
    _require_pass_v02(route_report, label="g2c_route")
    if proposal is None or proposal.selected_mode != mode:
        raise ValueError("g2c_selected_mode_mismatch")
    _require_pass_v02(
        g2c.validate_execution_mode_proposal_against_sources_v01(
            proposal=proposal,
            router_input=router_input,
            source_context=source,
        ),
        label="g2c_proposal",
    )
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    )
    registry = transition_registry.build_execution_mode_transition_registry_profile_v01()
    proposal_transition = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
    )
    review_action = "NARROW" if narrow else "ACCEPT"
    narrowing_basis_refs = (
        tuple(
            sorted(
                (
                    router_input.bsep_binding.bsep_binding_id,
                    proposal_artifact.artifact_id,
                    proposal.selected_feasibility_row_id,
                )
            )
        )
        if narrow
        else ()
    )
    review = g2c.build_root_execution_mode_review_input_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_action=review_action,
        accepted_scope_ref=(accepted_scope_ref if narrow else proposal.proposed_scope_ref),
        narrowing_basis_refs=narrowing_basis_refs,
    )
    _require_pass_v02(
        g2c.validate_root_execution_mode_review_input_against_sources_v01(
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
        ),
        label="g2c_review_input",
    )
    decision, root_kernel, root_input, root_result, review_report = (
        g2c.review_execution_mode_proposal_v01(
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
        )
    )
    _require_pass_v02(review_report, label="g2c_root_review")
    if any(
        item is None
        for item in (decision, root_kernel, root_input, root_result)
    ):
        raise ValueError("g2c_root_review_missing")
    decision_artifact = g2c.project_root_execution_mode_decision_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    root_route_transition = g2c.evaluate_execution_mode_root_route_transition_v01(
        registry=registry,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        proposal_artifact=proposal_artifact,
        decision_artifact=decision_artifact,
    )
    route_eligibility = g2c.project_execution_mode_route_eligibility_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
    )
    if route_eligibility is None:
        raise ValueError("g2c_route_eligibility_missing")
    runtime_policy = fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=(
            proposal.required_downstream_capability_ids
        ),
        permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
    )
    runtime_source = fr.build_fractal_runtime_source_context_v02(
        transition_registry=registry,
        g2c_source_context=source,
        router_input=router_input,
        proposal=proposal,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
        route_eligibility_artifact=route_eligibility,
        runtime_policy=runtime_policy,
    )
    _require_pass_v02(
        fr.validate_fractal_runtime_source_context_v02(runtime_source),
        label="g2d_source",
    )
    return runtime_source


def _build_non_runtime_g2c_family_v02(
    *,
    mode: str,
    review_action: str | None = None,
) -> dict[str, object]:
    domain_id = DOMAIN_ORDER[0]
    slug = _domain_slug_v02(domain_id)
    request_id = f"request:g2d5:{slug}:{mode}:negative:v02"
    root_id = f"root:g2d5:{slug}:negative:v02"
    scope_ref = f"scope:g2d5:{slug}:{mode}:negative:v02"
    memory = (
        _build_memory_family_v02(
            request_id=request_id,
            domain_id=domain_id,
            root_id=root_id,
            scope_ref=scope_ref,
            direct=True,
        )
        if mode == "direct_informational_reuse"
        else None
    )
    replay = (
        _build_replay_family_v02(
            mode=mode,
            request_id=request_id,
            domain_id=domain_id,
        )
        if mode == "sealed_replay"
        else None
    )
    transaction_id = (
        str(memory["transaction_id"])
        if memory is not None
        else f"transaction:g2d5:{slug}:{mode}:negative:v02"
    )
    selected_index = (
        g2c.EXECUTABLE_EXECUTION_MODES_V01.index(mode)
        if mode in g2c.EXECUTABLE_EXECUTION_MODES_V01
        else 0
    )
    profiles = tuple(
        g2c.build_execution_mode_local_mode_profile_v01(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=root_id,
            domain_id=domain_id,
            mode=candidate,
            policy_snapshot_id=f"policy:g2d5:{slug}:{mode}:negative:v02",
            capability_snapshot_id=f"capabilities:g2d5:{slug}:{mode}:negative:v02",
            cost_model_id="cost:g2d5:v02",
            policy_allowed=index >= selected_index,
            scope_allowed=True,
            risk_allowed=True,
            privacy_allowed=True,
            capability_state=(
                "NOT_REQUIRED"
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else "AVAILABLE"
            ),
            capability_id=(
                None
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else f"capability:g2d5:{slug}:{candidate}:negative:v02"
            ),
            cost_units=index + 1,
        )
        for index, candidate in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01)
    )
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        request_class="BOUNDED_REVIEW",
        action_class="NON_ACTION",
        action_packet_relation="NOT_APPLICABLE",
        scope_class="BOUNDED",
        scope_ref=scope_ref,
        permitted_narrower_scope_refs=(),
        risk_class="LOW",
        policy_snapshot_id=f"policy:g2d5:{slug}:{mode}:negative:v02",
        capability_snapshot_id=f"capabilities:g2d5:{slug}:{mode}:negative:v02",
        cost_model_id="cost:g2d5:v02",
        required_user_input_state=(
            "MISSING_RESOLVABLE" if mode == "needs_user" else "COMPLETE"
        ),
        hard_block_state="BLOCKED" if mode == "blocked" else "CLEAR",
        evaluation_time_epoch_seconds=EVALUATION_TIME,
        pt_created_at_utc=EVALUATION_UTC,
        et_observed_at_utc=EVALUATION_UTC,
        ct_session_anchor=f"ct:g2d5:{slug}:{mode}:negative:v02",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC,
        mode_profiles=profiles,
    )
    bsep = _build_bsep_family_v02(
        mode=mode,
        request_id=request_id,
        domain_id=domain_id,
    )
    source = _build_execution_mode_source_context_v02(
        bsep=bsep,
        snapshot=snapshot,
        memory=memory,
        replay=replay,
    )
    _require_pass_v02(
        g2c.validate_execution_mode_source_context_v01(source),
        label="g2d5_negative_g2c_source",
    )
    common = {
        "request_id": request_id,
        "transaction_id": transaction_id,
        "owning_root_id": root_id,
        "domain_id": domain_id,
    }
    router_input = g2c.build_execution_mode_router_input_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(
            **common,
            source_context=source,
        ),
        local_routing_snapshot=snapshot,
        replay_binding=(
            g2c.build_execution_mode_replay_binding_v01(
                **common,
                source_context=source,
            )
            if replay is not None
            else g2c.build_execution_mode_replay_not_applicable_binding_v01(**common)
        ),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=EVALUATION_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        ),
        g2b_binding=(
            g2c.build_execution_mode_g2b_binding_v01(
                **common,
                source_context=source,
            )
            if memory is not None
            else g2c.build_execution_mode_g2b_not_applicable_binding_v01(**common)
        ),
    )
    proposal, route_report = g2c.route_execution_mode_v01(
        router_input=router_input,
        source_context=source,
    )
    _require_pass_v02(route_report, label="g2d5_negative_g2c_route")
    if proposal is None or proposal.selected_mode != mode:
        raise ValueError("g2d5_negative_selected_mode_mismatch")
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    )
    registry = transition_registry.build_execution_mode_transition_registry_profile_v01()
    proposal_transition = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
    )
    action = review_action or (
        "TERMINAL_FROM_PROPOSAL" if mode in {"blocked", "needs_user"} else "ACCEPT"
    )
    review = g2c.build_root_execution_mode_review_input_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_action=action,
        accepted_scope_ref=proposal.proposed_scope_ref if action == "ACCEPT" else None,
        narrowing_basis_refs=(),
    )
    decision, root_kernel, root_input, root_result, review_report = (
        g2c.review_execution_mode_proposal_v01(
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
        )
    )
    _require_pass_v02(review_report, label="g2d5_negative_root_review")
    if any(item is None for item in (decision, root_kernel, root_input, root_result)):
        raise ValueError("g2d5_negative_root_review_missing")
    decision_artifact = g2c.project_root_execution_mode_decision_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    root_route_transition = g2c.evaluate_execution_mode_root_route_transition_v01(
        registry=registry,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        proposal_artifact=proposal_artifact,
        decision_artifact=decision_artifact,
    )
    route_eligibility = g2c.project_execution_mode_route_eligibility_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
    )
    runtime_policy = fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
    )
    runtime_source = fr.FractalRuntimeSourceContextV02(
        transition_registry=registry,
        g2c_source_context=source,
        router_input=router_input,
        proposal=proposal,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
        route_eligibility_artifact=route_eligibility,
        runtime_policy=runtime_policy,
    )
    report = fr.validate_fractal_runtime_source_context_v02(runtime_source)
    _require_v02(report.status == "FAIL_CLOSED", "g2d5_negative_source_accepted")
    return {
        "runtime_source": runtime_source,
        "g2c_source": source,
        "router_input": router_input,
        "proposal": proposal,
        "proposal_artifact": proposal_artifact,
        "decision": decision,
        "decision_artifact": decision_artifact,
        "route_eligibility": route_eligibility,
        "report": report,
    }


def _collect_accepted_runs_v02() -> tuple[_AcceptedRunV02, ...]:
    accepted: list[_AcceptedRunV02] = []
    for domain_id, mode, narrow, action_packet_required in _POSITIVE_MODE_ROWS:
        source = _build_runtime_source_family_v02(
            domain_id=domain_id,
            mode=mode,
            narrow=narrow,
            action_packet_required=action_packet_required,
        )
        source_sha = _sha256_plain_v02(source)
        bundle, external_report = fr.run_fractal_runtime_v02(source)
        _require_pass_v02(external_report, label="g2d_complete_profile")
        if type(bundle) is not fr.FractalRuntimeExecutionBundleV02:
            raise ValueError("g2d_bundle_missing")
        if (
            bundle.runtime_report.runtime_outcome != "COMPLETED"
            or bundle.runtime_report.domain_id != domain_id
            or bundle.runtime_report.accepted_mode != mode
            or bundle.runtime_report.topology_created_count != 1
        ):
            raise ValueError("g2d_positive_geometry_mismatch")
        accepted.append(
            _AcceptedRunV02(
                domain_id=domain_id,
                mode=mode,
                source_family_sha256=source_sha,
                source_context=source,
                bundle=bundle,
                external_report=external_report,
            )
        )
    return tuple(accepted)


def _accepted_run_v02(
    accepted: tuple[_AcceptedRunV02, ...],
    *,
    domain_id: str,
    mode: str,
) -> _AcceptedRunV02:
    rows = tuple(
        item
        for item in accepted
        if item.domain_id == domain_id and item.mode == mode
    )
    if len(rows) != 1:
        raise ValueError("g2d_accepted_run_lookup_mismatch")
    return rows[0]


def _require_v02(condition: bool, reason: str) -> None:
    if condition is not True:
        raise ValueError(reason)


def _exactly_one_v02(values: tuple[object, ...], *, label: str) -> object:
    if len(values) != 1:
        raise ValueError(f"{label}:{len(values)}")
    return values[0]


def _exact_evidence_identity_inventory_v02(
    values: tuple[str, ...],
) -> tuple[str, ...]:
    inventory: list[str] = []
    for value in values:
        if type(value) is not str or not value:
            raise ValueError("g2d5_evidence_ref_invalid")
        if value not in inventory:
            inventory.append(value)
    return tuple(inventory)


def _case_result_v02(
    *,
    spec: _CaseSpecV02,
    observed_outcome: str,
    evidence_refs: tuple[str, ...],
    proof: dict[str, object],
    accepted_run: _AcceptedRunV02 | None = None,
) -> FractalRuntimeG2DCaseResultV02:
    _require_v02(observed_outcome == spec.expected_outcome, "g2d5_outcome_mismatch")
    evidence_inventory = _exact_evidence_identity_inventory_v02(evidence_refs)
    _require_v02(bool(evidence_inventory), "g2d5_evidence_refs_invalid")
    contract = _PROOF_CONTRACTS_V02[spec.case_id]
    details = dict(proof)
    details.pop("proof_kind", None)
    detail_plain = _plain_value_v02(details)
    sealed_proof = {
        "proof_kind": contract.proof_kind,
        "axis": contract.axis,
        "executor": contract.executor,
        "observed_source": contract.observed_source,
        "matrix_cardinality": contract.matrix_cardinality,
        "accepted_bundle_required": contract.accepted_bundle_required,
        "details": detail_plain,
        "details_sha256": _sha256_plain_v02(detail_plain),
    }
    evidence_material = {
        "case_id": spec.case_id,
        "case_class": spec.case_class,
        "expected_outcome": spec.expected_outcome,
        "observed_outcome": observed_outcome,
        "evidence_refs": list(evidence_inventory),
        "proof": sealed_proof,
    }
    evidence_bytes = canonical_json_bytes_v01(evidence_material)
    evidence_json = evidence_bytes.decode("ascii")
    evidence_sha = hashlib.sha256(evidence_bytes).hexdigest()
    bundle = accepted_run.bundle if accepted_run is not None else None
    external_report = (
        accepted_run.external_report if accepted_run is not None else None
    )
    runtime_counters = (
        {
            "provider_calls": bundle.runtime_report.provider_calls,
            "model_calls": bundle.runtime_report.model_calls,
            "network_calls": bundle.runtime_report.network_calls,
            "connector_calls": bundle.runtime_report.connector_calls,
            "external_drs_calls": bundle.runtime_report.external_drs_calls,
            "action_commit_packets_created": (
                bundle.runtime_report.action_commit_packets_created
            ),
            "permissions_created": bundle.runtime_report.permissions_created,
            "receipts_created": bundle.runtime_report.receipts_created,
            "final_outputs_created": bundle.runtime_report.final_outputs_created,
            "drs_writes": bundle.runtime_report.drs_writes,
            "authority_created_count": bundle.runtime_report.authority_created_count,
            "real_world_effects_count": bundle.runtime_report.real_world_effects_count,
        }
        if bundle is not None
        else {name: 0 for name in _ZERO_COUNTER_FIELD_NAMES if name != "gemini_calls"}
    )
    _require_v02(
        all(value == 0 for value in runtime_counters.values()),
        "g2d5_case_runtime_counter_nonzero",
    )
    return FractalRuntimeG2DCaseResultV02(
        case_id=spec.case_id,
        case_class=spec.case_class,
        domain_id=accepted_run.domain_id if accepted_run is not None else None,
        accepted_mode=accepted_run.mode if accepted_run is not None else None,
        expected_outcome=spec.expected_outcome,
        observed_outcome=observed_outcome,
        source_family_sha256=(
            accepted_run.source_family_sha256
            if accepted_run is not None
            else None
        ),
        topology_id=bundle.topology.topology_id if bundle is not None else None,
        runtime_report_id=(
            bundle.runtime_report.report_id if bundle is not None else None
        ),
        external_validation_report_id=(
            external_report.validation_report_id
            if external_report is not None
            else None
        ),
        evidence_refs=evidence_inventory,
        evidence_material_json=evidence_json,
        evidence_sha256=evidence_sha,
        topology_created_count=1 if accepted_run is not None else 0,
        provider_calls=runtime_counters["provider_calls"],
        model_calls=runtime_counters["model_calls"],
        gemini_calls=0,
        network_calls=runtime_counters["network_calls"],
        connector_calls=runtime_counters["connector_calls"],
        external_drs_calls=runtime_counters["external_drs_calls"],
        action_commit_packets_created=runtime_counters[
            "action_commit_packets_created"
        ],
        permissions_created=runtime_counters["permissions_created"],
        receipts_created=runtime_counters["receipts_created"],
        final_outputs_created=runtime_counters["final_outputs_created"],
        drs_writes=runtime_counters["drs_writes"],
        authority_created_count=runtime_counters["authority_created_count"],
        real_world_effects_count=runtime_counters["real_world_effects_count"],
        final_status="PASS",
        reason_codes=(),
    )


def _positive_case_result_v02(
    *,
    spec: _CaseSpecV02,
    accepted_run: _AcceptedRunV02,
) -> FractalRuntimeG2DCaseResultV02:
    bundle = accepted_run.bundle
    source = accepted_run.source_context
    _require_pass_v02(
        fr.validate_fractal_runtime_source_context_v02(source),
        label="d5_positive_source",
    )
    _require_pass_v02(
        fr.validate_runtime_execution_topology_against_sources_v02(
            bundle.topology,
            source_context=source,
        ),
        label="d5_positive_topology",
    )
    report = bundle.runtime_report
    zero_runtime_counters = (
        report.provider_calls,
        report.model_calls,
        report.network_calls,
        report.connector_calls,
        report.external_drs_calls,
        report.action_commit_packets_created,
        report.permissions_created,
        report.receipts_created,
        report.final_outputs_created,
        report.drs_writes,
        report.authority_created_count,
        report.real_world_effects_count,
    )
    _require_v02(zero_runtime_counters == (0,) * 12, "g2d5_runtime_effect_counter")
    child_inputs = tuple(
        item for item in bundle.cell_inputs if item.parent_cell_id is not None
    )
    expected_child_count = 2 if accepted_run.mode == "full_fractal" else 0
    _require_v02(
        len(child_inputs) == expected_child_count,
        "g2d5_recursive_geometry_mismatch",
    )
    if accepted_run.domain_id == DOMAIN_ORDER[0] and accepted_run.mode == "cloud_llm":
        _require_v02(source.decision.outcome == "NARROW", "g2d5_travel_narrow_missing")
    if accepted_run.domain_id == DOMAIN_ORDER[1] and accepted_run.mode == "cloud_llm":
        _require_v02(source.decision.outcome == "ACCEPT", "g2d5_warehouse_accept_missing")
    proof = {
        "proof_kind": "DOMAIN_POSITIVE_RUNTIME",
        "domain_id": accepted_run.domain_id,
        "accepted_mode": accepted_run.mode,
        "root_outcome": source.decision.outcome,
        "accepted_scope_ref": bundle.topology.accepted_scope_ref,
        "selected_profile_id": source.proposal.selected_local_mode_profile_id,
        "required_capability_ids": source.proposal.required_downstream_capability_ids,
        "topology_node_ids": bundle.topology.ordered_node_ids,
        "child_cell_input_ids": tuple(item.cell_input_id for item in child_inputs),
        "runtime_outcome": report.runtime_outcome,
        "runtime_report_status": report.report_status,
        "complete_profile_status": accepted_run.external_report.status,
        "zero_runtime_counters": zero_runtime_counters,
    }
    refs = (
        source.proposal.proposal_id,
        source.route_eligibility_artifact.artifact_id,
        bundle.topology.topology_id,
        bundle.runtime_trace.trace_id,
        report.report_id,
        accepted_run.external_report.validation_report_id,
    )
    return _case_result_v02(
        spec=spec,
        observed_outcome=report.runtime_outcome,
        evidence_refs=refs,
        proof=proof,
        accepted_run=accepted_run,
    )


def _source_axis_mutation_v02(
    *,
    case_number: int,
    accepted: tuple[_AcceptedRunV02, ...],
) -> tuple[object, fr.FractalRuntimeSourceContextV02, str, tuple[str, ...]]:
    if 11 <= case_number <= 16:
        mode = {
            11: "deterministic",
            12: "sealed_replay",
            13: "direct_informational_reuse",
            14: "blocked",
            15: "needs_user",
            16: "full_semantic",
        }[case_number]
        family = _build_non_runtime_g2c_family_v02(
            mode=mode,
            review_action="REJECT" if case_number == 16 else None,
        )
        source = family["runtime_source"]
        if type(source) is not fr.FractalRuntimeSourceContextV02:
            raise TypeError("g2d5_non_runtime_source_type_invalid")
        decision = family["decision"]
        path = {
            11: "/proposal/selected_mode=deterministic",
            12: "/proposal/selected_mode=sealed_replay",
            13: "/proposal/selected_mode=direct_informational_reuse",
            14: "/decision/downstream_consumption_class=TERMINAL_NO_CONSUMPTION",
            15: "/decision/downstream_consumption_class=TERMINAL_NO_CONSUMPTION",
            16: "/decision/outcome=REJECT",
        }[case_number]
        refs = tuple(
            item
            for item in (
                family["proposal"].proposal_id,
                family["decision"].decision_id,
                family["decision_artifact"].artifact_id,
                getattr(family["route_eligibility"], "artifact_id", None),
            )
            if type(item) is str
        )
        return family["g2c_source"], source, path, refs

    travel_memory = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="memory_informed",
    )
    travel_semantic = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_semantic",
    )
    travel_fractal = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_fractal",
    )
    warehouse_memory = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[1],
        mode="memory_informed",
    )

    base = travel_fractal.source_context
    refs: tuple[str, ...]
    if case_number == 17:
        invalid = replace(base, route_eligibility_artifact=None)
        return base, invalid, "/route_eligibility_artifact", (
            base.decision.decision_id,
            base.decision_artifact.artifact_id,
        )
    if case_number == 18:
        donor = warehouse_memory.source_context
        invalid = replace(base, route_eligibility_artifact=donor.route_eligibility_artifact)
        return base, invalid, "/route_eligibility_artifact", (
            base.route_eligibility_artifact.artifact_id,
            donor.route_eligibility_artifact.artifact_id,
        )
    if case_number == 19:
        donor = warehouse_memory.source_context
        invalid = replace(base, g2c_source_context=donor.g2c_source_context)
        return base, invalid, "/g2c_source_context/domain_id", (
            base.router_input.router_input_id,
            donor.router_input.router_input_id,
        )
    if case_number == 20:
        route = base.route_eligibility_artifact
        prefix = route.artifact_id.split(":", 1)[0] + ":"
        foreign = replace(route, artifact_id=prefix + "0" * 64)
        invalid = replace(base, route_eligibility_artifact=foreign)
        return base, invalid, "/route_eligibility_artifact/artifact_id", (
            route.artifact_id,
            foreign.artifact_id,
        )
    if case_number == 21:
        widened = replace(base.decision, accepted_scope_ref=base.decision.accepted_scope_ref + ":widened")
        invalid = replace(base, decision=widened)
        return base, invalid, "/decision/accepted_scope_ref", (
            base.decision.decision_id,
            base.review_input.root_review_input_id,
        )
    if case_number == 22:
        widened = replace(
            base.proposal,
            required_downstream_capability_ids=(
                *base.proposal.required_downstream_capability_ids,
                "capability:g2d5:foreign-authority",
            ),
        )
        invalid = replace(base, proposal=widened)
        return base, invalid, "/proposal/required_downstream_capability_ids", (
            base.proposal.proposal_id,
            base.router_input.router_input_id,
        )
    if case_number == 23:
        missing = _reidentified_v02(
            replace(
                base.runtime_policy,
                allowed_capability_ids=tuple(
                    item
                    for item in base.runtime_policy.allowed_capability_ids
                    if item != fr.CAP_FRACTAL_CHILD
                ),
            ),
            identity_field="policy_id",
            rebuild=fr.rebuild_fractal_runtime_policy_identity_v02,
        )
        invalid = replace(base, runtime_policy=missing)
        return base, invalid, "/runtime_policy/allowed_capability_ids/-recursive", (
            base.runtime_policy.policy_id,
            missing.policy_id,
        )
    if case_number == 24:
        invalid = replace(
            travel_memory.source_context,
            proposal=travel_semantic.source_context.proposal,
        )
        return travel_memory.source_context, invalid, "/proposal/selected_mode:upgrade", (
            travel_memory.source_context.proposal.proposal_id,
            travel_semantic.source_context.proposal.proposal_id,
        )
    if case_number == 25:
        invalid = replace(
            travel_semantic.source_context,
            proposal=travel_memory.source_context.proposal,
        )
        return travel_semantic.source_context, invalid, "/proposal/selected_mode:downgrade", (
            travel_semantic.source_context.proposal.proposal_id,
            travel_memory.source_context.proposal.proposal_id,
        )
    if case_number == 26:
        base = travel_semantic.source_context
        donor_binding = travel_memory.source_context.router_input.g2b_binding
        changed_router = replace(base.router_input, g2b_binding=donor_binding)
        invalid = replace(base, router_input=changed_router)
        return base, invalid, "/router_input/g2b_binding:instruction_authority", (
            base.router_input.g2b_binding.g2b_binding_id,
            donor_binding.g2b_binding_id,
        )
    if case_number == 27:
        base = travel_semantic.source_context
        donor_binding = warehouse_memory.source_context.router_input.g2a_binding
        changed_router = replace(base.router_input, g2a_binding=donor_binding)
        invalid = replace(base, router_input=changed_router)
        return base, invalid, "/router_input/g2a_binding:history_authority", (
            base.router_input.g2a_binding.g2a_binding_id,
            donor_binding.g2a_binding_id,
        )
    raise ValueError(f"g2d5_source_axis_unmapped:{case_number}")


def _source_negative_case_result_v02(
    *,
    case_number: int,
    spec: _CaseSpecV02,
    accepted: tuple[_AcceptedRunV02, ...],
) -> FractalRuntimeG2DCaseResultV02:
    baseline, invalid_source, mutated_path, source_refs = _source_axis_mutation_v02(
        case_number=case_number,
        accepted=accepted,
    )
    report = fr.validate_fractal_runtime_source_context_v02(invalid_source)
    _require_v02(report.status == "FAIL_CLOSED", "g2d5_source_axis_accepted")
    _require_v02(bool(report.reason_codes), "g2d5_source_axis_reason_missing")
    bundle, external_report = fr.run_fractal_runtime_v02(invalid_source)
    _require_v02(bundle is None, "g2d5_invalid_source_bundle_created")
    _require_v02(
        external_report.status == "FAIL_CLOSED",
        "g2d5_invalid_source_external_pass",
    )
    baseline_sha = _sha256_plain_v02(baseline)
    attempted_sha = _sha256_plain_v02(invalid_source)
    _require_v02(baseline_sha != attempted_sha, "g2d5_source_axis_not_changed")
    proof = {
        "case_number": case_number,
        "mutated_path": mutated_path,
        "baseline_sha256": baseline_sha,
        "attempted_sha256": attempted_sha,
        "validation_report_id": report.validation_report_id,
        "validation_target": report.validation_target,
        "failure_stage": report.failure_stage,
        "reason_codes": report.reason_codes,
        "external_validation_report_id": external_report.validation_report_id,
        "external_validation_target": external_report.validation_target,
        "external_reason_codes": external_report.reason_codes,
        "created_before": {
            "topology_ids": (),
            "bundle_report_ids": (),
        },
        "created_after": {
            "topology_ids": (),
            "bundle_report_ids": (),
        },
        "topology_created_delta": 0,
        "bundle_created_delta": 0,
    }
    refs = (*source_refs, report.validation_report_id, external_report.validation_report_id)
    return _case_result_v02(
        spec=spec,
        observed_outcome=report.status,
        evidence_refs=refs,
        proof=proof,
    )


def _reidentified_v02(
    value: object,
    *,
    identity_field: str,
    rebuild: object,
) -> object:
    if not callable(rebuild):
        raise TypeError("g2d5_rebuild_not_callable")
    return replace(value, **{identity_field: rebuild(value)})


def _bounded_outcome_from_report_v02(
    report: fr.FractalRuntimeValidationReportV02,
) -> str:
    _require_v02(report.status == "FAIL_CLOSED", "g2d5_bounded_report_not_failure")
    bounded_reasons = {
        "g2d_cell_input_invalid",
        "g2d_node_instance_geometry_invalid",
        "g2d_budget_negative",
        "g2d_budget_debit_mismatch",
        "g2d_budget_overflow",
        "g2d_depth_limit_exceeded",
        "g2d_fan_out_limit_exceeded",
        "g2d_total_cell_limit_exceeded",
        "g2d_token_budget_exceeded",
        "g2d_wall_time_budget_exceeded",
        "g2d_provider_budget_exceeded",
    }
    _require_v02(
        bool(set(report.reason_codes).intersection(bounded_reasons)),
        "g2d5_bounded_reason_missing",
    )
    return "BLOCKED"


def _validating_context_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> tuple[
    fr.FractalCellInputV02,
    fr.FractalCellQueueEntryV02,
    fr.FractalRuntimeBudgetV02,
    fr.FractalRuntimeBudgetV02,
]:
    validating_rows = tuple(
        item for item in bundle.queue_entries if item.state == "VALIDATING"
    )
    _require_v02(bool(validating_rows), "g2d5_validating_context_missing")
    queue = validating_rows[0]
    cell_input = _exactly_one_v02(
        tuple(item for item in bundle.cell_inputs if item.cell_id == queue.cell_id),
        label="g2d5_validating_input",
    )
    cell_budget = _exactly_one_v02(
        tuple(item for item in bundle.budgets if item.budget_id == queue.cell_budget_id),
        label="g2d5_validating_cell_budget",
    )
    global_budget = _exactly_one_v02(
        tuple(item for item in bundle.budgets if item.budget_id == queue.global_budget_id),
        label="g2d5_validating_global_budget",
    )
    if (
        type(cell_input) is not fr.FractalCellInputV02
        or type(cell_budget) is not fr.FractalRuntimeBudgetV02
        or type(global_budget) is not fr.FractalRuntimeBudgetV02
    ):
        raise TypeError("g2d5_validating_context_type_invalid")
    return cell_input, queue, cell_budget, global_budget


def _mutated_budget_report_v02(
    budget: fr.FractalRuntimeBudgetV02,
    **changes: object,
) -> tuple[fr.FractalRuntimeBudgetV02, fr.FractalRuntimeValidationReportV02]:
    provisional = replace(budget, **changes)
    mutated = _reidentified_v02(
        provisional,
        identity_field="budget_id",
        rebuild=fr.rebuild_fractal_runtime_budget_identity_v02,
    )
    if type(mutated) is not fr.FractalRuntimeBudgetV02:
        raise TypeError("g2d5_mutated_budget_type_invalid")
    return mutated, fr.validate_fractal_runtime_budget_v02(mutated)


def _created_set_delta_v02(
    before: tuple[str, ...],
    after: tuple[str, ...],
) -> dict[str, object]:
    created = tuple(item for item in after if item not in before)
    return {
        "before_ids": before,
        "after_ids": after,
        "created_ids": created,
        "created_count": len(created),
    }


def _witness_prefix_kwargs_v02(env: dict[str, object]) -> dict[str, object]:
    return {
        "settled_budget_log": env["budget_log"],
        "settled_queue_entry_log": env["queue_log"],
        "settled_queue_artifact_log": env["artifact_log"],
        "settled_cell_inputs": env["cell_inputs"],
        "settled_scope_projections": env["scope_projections"],
        "settled_revise_observations": env["revise_observations"],
        "settled_backpressure_states": env["backpressure_states"],
        "settled_validation_reports": env["validation_reports"],
    }


def _witness_latest_queue_v02(
    env: dict[str, object],
) -> tuple[fr.FractalCellQueueEntryV02, ...]:
    queue_log = env["queue_log"]
    if type(queue_log) is not tuple:
        raise TypeError("g2d5_witness_queue_log_invalid")
    latest: dict[tuple[str, str], fr.FractalCellQueueEntryV02] = {}
    for entry in queue_log:
        if type(entry) is not fr.FractalCellQueueEntryV02:
            raise TypeError("g2d5_witness_queue_entry_invalid")
        latest[(entry.cell_id, entry.node_id)] = entry
    return tuple(
        entry
        for entry in queue_log
        if latest.get((entry.cell_id, entry.node_id)) == entry
    )


def _witness_artifact_for_queue_v02(
    env: dict[str, object],
    queue_entry_id: str,
) -> abi.KernelArtifactV01:
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    if type(queue_log) is not tuple or type(artifact_log) is not tuple:
        raise TypeError("g2d5_witness_artifact_log_invalid")
    rows = tuple(
        artifact
        for entry, artifact in zip(queue_log, artifact_log, strict=True)
        if entry.queue_entry_id == queue_entry_id
    )
    result = _exactly_one_v02(rows, label="g2d5_witness_artifact_lookup")
    if type(result) is not abi.KernelArtifactV01:
        raise TypeError("g2d5_witness_artifact_type_invalid")
    return result


def _witness_budget_by_id_v02(
    env: dict[str, object],
) -> dict[str, fr.FractalRuntimeBudgetV02]:
    budget_log = env["budget_log"]
    if type(budget_log) is not tuple:
        raise TypeError("g2d5_witness_budget_log_invalid")
    return {item.budget_id: item for item in budget_log}


def _witness_local_observation_material_v02(
    env: dict[str, object],
    *,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    cell_budget_before: fr.FractalRuntimeBudgetV02,
    global_budget_before: fr.FractalRuntimeBudgetV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...],
) -> dict[str, tuple[str, ...]]:
    source = env["source"]
    topology = env["topology"]
    reference_bundle = env["reference_bundle"]
    if (
        type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(reference_bundle) is not fr.FractalRuntimeExecutionBundleV02
    ):
        raise TypeError("g2d5_witness_local_material_context_invalid")
    assignment = _exactly_one_v02(
        tuple(
            item
            for item in reference_bundle.runtime_assignments
            if item.node_id == node.node_id
        ),
        label="g2d5_witness_local_assignment",
    )
    artifact_by_queue_id = {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(
            env["queue_log"],
            env["artifact_log"],
            strict=True,
        )
    }
    dependency_artifacts = tuple(
        artifact_by_queue_id[item.queue_entry_id] for item in dependencies
    )
    dependency_states = tuple(item.state for item in dependencies)
    if "BLOCKED" in dependency_states:
        outcome = "BLOCKED"
    elif "NEEDS_USER" in dependency_states:
        outcome = "NEEDS_USER"
    elif "DEADEND" in dependency_states:
        outcome = "DEADEND"
    elif "DEGRADED" in dependency_states:
        outcome = "DEGRADED"
    else:
        outcome = "COMPLETED"
    reason_rows = {
        "COMPLETED": (),
        "DEGRADED": ("g2d_dependency_degraded",),
        "BLOCKED": ("g2d_dependency_blocked",),
        "NEEDS_USER": ("g2d_dependency_needs_user",),
        "DEADEND": ("g2d_dependency_deadend",),
    }
    evidence = (
        tuple(item.artifact_id for item in dependency_artifacts)
        if dependencies
        else cell_input.evidence_refs
    )
    core = {
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
        "dependency_queue_entry_ids": [
            item.queue_entry_id for item in dependencies
        ],
        "dependency_queue_artifact_ids": [
            item.artifact_id for item in dependency_artifacts
        ],
        "dependency_states": list(dependency_states),
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
    outputs = (
        (
            "d3local:output:"
            + domain_separated_sha256_hex_v01(
                domain="HEDGEHOG_FRACTAL_RUNTIME_V02_D3_LOCAL_OBSERVATION_MATERIAL",
                payload=canonical_json_bytes_v01(core),
            ),
        )
        if outcome in {"COMPLETED", "DEGRADED"}
        else ()
    )
    return {
        "queue_reason_codes": reason_rows[outcome],
        "observed_output_refs": outputs,
        "observed_evidence_refs": evidence,
        "advisory_refs": (),
    }


def _witness_live_budget_heads_v02(
    env: dict[str, object],
    *,
    cell_id: str,
) -> tuple[fr.FractalRuntimeBudgetV02, fr.FractalRuntimeBudgetV02]:
    topology = env["topology"]
    budget_log = env["budget_log"]
    if (
        type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(budget_log) is not tuple
    ):
        raise TypeError("g2d5_witness_budget_geometry_invalid")
    heads: dict[tuple[str, str], fr.FractalRuntimeBudgetV02] = {}
    for budget in budget_log:
        heads[(budget.budget_scope, budget.owning_cell_id)] = budget
    global_head = heads.get(("ROOT_GLOBAL_AND_CELL", topology.root_cell_id))
    cell_head = (
        global_head
        if cell_id == topology.root_cell_id
        else heads.get(("CHILD_CELL_LOCAL", cell_id))
    )
    if (
        type(cell_head) is not fr.FractalRuntimeBudgetV02
        or type(global_head) is not fr.FractalRuntimeBudgetV02
    ):
        raise ValueError("g2d5_witness_live_budget_missing")
    return cell_head, global_head


def _witness_refresh_reports_v02(env: dict[str, object]) -> None:
    base_reports = env["base_reports"]
    queue_log = env["queue_log"]
    scope_reports = env["scope_reports"]
    input_reports = env["input_reports"]
    if not all(
        type(value) is tuple
        for value in (base_reports, queue_log, scope_reports, input_reports)
    ):
        raise TypeError("g2d5_witness_report_geometry_invalid")
    env["validation_reports"] = (
        *base_reports,
        *(fr.validate_fractal_cell_queue_entry_v02(item) for item in queue_log),
        *scope_reports,
        *input_reports,
    )


def _witness_initial_environment_v02(
    run: _AcceptedRunV02,
) -> dict[str, object]:
    source = run.source_context
    bundle = run.bundle
    topology = bundle.topology
    root_inputs = tuple(
        item for item in bundle.cell_inputs if item.parent_cell_id is None
    )
    root_input = _exactly_one_v02(
        root_inputs,
        label="g2d5_witness_root_input",
    )
    if type(root_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_witness_root_input_type_invalid")
    initial_queues = tuple(
        item
        for item in bundle.queue_entries
        if item.parent_cell_id is None and item.predecessor_queue_entry_id is None
    )
    _require_v02(
        tuple(item.queue_entry_id for item in initial_queues)
        == root_input.ordered_initial_queue_entry_ids,
        "g2d5_witness_initial_queue_order",
    )
    artifact_by_queue_id = {
        abi.kernel_artifact_to_plain_dict_v01(item)["payload"]["queue_entry_id"]: item
        for item in bundle.queue_artifacts
    }
    initial_artifacts = tuple(
        artifact_by_queue_id[item.queue_entry_id] for item in initial_queues
    )
    initial_budgets = bundle.budgets[:3]
    _require_v02(
        tuple(item.budget_event_kind for item in initial_budgets)
        == ("INITIAL_ALLOCATION", "ACTIVATE", "CELL_CREATE"),
        "g2d5_witness_initial_budget_order",
    )
    topology_decision = _exactly_one_v02(
        tuple(
            item
            for item in bundle.transition_decisions
            if item.rule_id == "g2d_t01_route_eligibility_to_topology"
        ),
        label="g2d5_witness_topology_decision",
    )
    if type(topology_decision) is not transition_registry.TransitionDecisionV01:
        raise TypeError("g2d5_witness_topology_decision_type_invalid")
    source_report = fr.validate_fractal_runtime_source_context_v02(source)
    binding_report = fr.validate_runtime_topology_source_binding_against_g2c_v02(
        bundle.source_binding,
        source_context=source,
    )
    seed_report = fr.validate_runtime_topology_seed_v02(bundle.topology_seed)
    topology_report = fr.validate_runtime_execution_topology_against_sources_v02(
        topology,
        source_context=source,
    )
    base_reports = (
        source_report,
        binding_report,
        seed_report,
        topology_report,
    )
    _require_v02(
        all(item.status == "PASS" for item in base_reports),
        "g2d5_witness_base_report_invalid",
    )
    env: dict[str, object] = {
        "source": source,
        "topology": topology,
        "topology_artifact": bundle.topology_artifact,
        "topology_decision": topology_decision,
        "registry": transition_registry.build_fractal_runtime_transition_registry_profile_v02(),
        "seed": bundle.topology_seed,
        "nodes": bundle.topology_nodes,
        "root_input": root_input,
        "root_create": initial_budgets[-1],
        "root_initial_queues": initial_queues,
        "budget_log": initial_budgets,
        "queue_log": initial_queues,
        "artifact_log": initial_artifacts,
        "cell_inputs": (),
        "scope_projections": (),
        "backpressure_states": (),
        "revise_observations": (),
        "base_reports": base_reports,
        "scope_reports": (),
        "input_reports": (),
        "validation_reports": (),
        "reference_bundle": bundle,
    }
    _witness_refresh_reports_v02(env)
    input_report = fr.validate_fractal_cell_input_against_sources_v02(
        root_input,
        source_context=source,
        topology=topology,
        topology_artifact=bundle.topology_artifact,
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=initial_budgets[-1],
        global_budget=initial_budgets[-1],
        queue_entries=initial_queues,
        queue_artifacts=initial_artifacts,
        **_witness_prefix_kwargs_v02(env),
    )
    _require_pass_v02(input_report, label="g2d5_witness_root_input")
    env["cell_inputs"] = (root_input,)
    env["input_reports"] = (input_report,)
    _witness_refresh_reports_v02(env)
    return env


def _witness_eval_v02(
    env: dict[str, object],
    *,
    source_artifact: abi.KernelArtifactV01,
    node: fr.RuntimeTopologyNodeV02,
    current_entry: fr.FractalCellQueueEntryV02 | None,
    cell_input: fr.FractalCellInputV02 | None,
    cell_budget: fr.FractalRuntimeBudgetV02,
    global_budget: fr.FractalRuntimeBudgetV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    queue_reason_codes: tuple[str, ...] = (),
    observed_output_refs: tuple[str, ...] = (),
    observed_evidence_refs: tuple[str, ...] = (),
    advisory_refs: tuple[str, ...] = (),
    validation_report: fr.FractalRuntimeValidationReportV02 | None = None,
    revise_observation: fr.FractalReviseObservationV02 | None = None,
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
    cell_id: str | None = None,
    parent_cell_id: str | None = None,
    cell_depth: int | None = None,
    scope_ref: str | None = None,
) -> transition_registry.TransitionDecisionV01 | None:
    source = env["source"]
    topology = env["topology"]
    registry = env["registry"]
    if (
        type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(registry) is not transition_registry.TransitionRegistryV01
    ):
        raise TypeError("g2d5_witness_eval_context_invalid")
    if current_entry is not None:
        cell_id = current_entry.cell_id
        parent_cell_id = current_entry.parent_cell_id
        planned_child_cell_id = current_entry.planned_child_cell_id
        cell_depth = current_entry.cell_depth
        scope_ref = current_entry.scope_ref
    else:
        planned_child_cell_id = None
    if type(cell_id) is not str or type(cell_depth) is not int or type(scope_ref) is not str:
        raise TypeError("g2d5_witness_eval_axis_invalid")
    return fr.evaluate_fractal_runtime_state_transition_v02(
        source_context=source,
        topology=topology,
        source_artifact=source_artifact,
        current_entry=current_entry,
        node=node,
        cell_input=cell_input,
        cell_id=cell_id,
        parent_cell_id=parent_cell_id,
        planned_child_cell_id=planned_child_cell_id,
        cell_depth=cell_depth,
        scope_ref=scope_ref,
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        dependencies=dependencies,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        local_child_result=None,
        local_child_result_artifact=None,
        validation_report=validation_report,
        parent_return_pre_post_vv_terminal_queue_entries=(),
        parent_return_child_results=(),
        parent_return_partial_failures=(),
        parent_return_result_proposal=None,
        parent_return_post_vv_report=None,
        parent_return_gt_advisory_report=None,
        parent_return_validation_reports=(),
        revise_observation=revise_observation,
        backpressure_state=backpressure_state,
        transition_registry=registry,
        **_witness_prefix_kwargs_v02(env),
    )


def _witness_budget_successor_v02(
    env: dict[str, object],
    predecessor: fr.FractalRuntimeBudgetV02,
    *,
    event: str,
    decision: transition_registry.TransitionDecisionV01 | None = None,
    cell_input: fr.FractalCellInputV02 | None = None,
    allocation_parent: fr.FractalRuntimeBudgetV02 | None = None,
    owning_cell_id: str | None = None,
    scope: str = "ROOT_GLOBAL_AND_CELL",
    canonical_child_index: int | None = None,
    allocation_queue_entries: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    paired_cell_budget: fr.FractalRuntimeBudgetV02 | None = None,
) -> fr.FractalRuntimeBudgetV02:
    source = env["source"]
    topology = env["topology"]
    seed = env["seed"]
    if (
        type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(seed) is not fr.RuntimeTopologySeedV02
    ):
        raise TypeError("g2d5_witness_budget_context_invalid")
    return fr.build_fractal_runtime_budget_v02(
        policy=source.runtime_policy,
        topology_seed=seed,
        allocation_parent_budget=allocation_parent,
        predecessor_budget=predecessor,
        owning_cell_id=owning_cell_id or topology.root_cell_id,
        budget_scope=scope,
        budget_state="ACTIVE",
        budget_event_kind=event,
        budget_context_input=cell_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queue_entries,
        transition_decision=decision,
        paired_cell_budget=paired_cell_budget,
        child_result=None,
    )


def _witness_advance_v02(
    env: dict[str, object],
    *,
    current: fr.FractalCellQueueEntryV02,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    cell_budget_before: fr.FractalRuntimeBudgetV02,
    global_budget_before: fr.FractalRuntimeBudgetV02,
    cell_budget_after: fr.FractalRuntimeBudgetV02,
    global_budget_after: fr.FractalRuntimeBudgetV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...],
    round_entries: tuple[fr.FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...] = (),
    observed_output_refs: tuple[str, ...] = (),
    observed_evidence_refs: tuple[str, ...] = (),
    advisory_refs: tuple[str, ...] = (),
    validation_report: fr.FractalRuntimeValidationReportV02 | None = None,
    revise_observation: fr.FractalReviseObservationV02 | None = None,
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    abi.KernelArtifactV01,
    transition_registry.TransitionDecisionV01,
]:
    current_artifact = _witness_artifact_for_queue_v02(
        env,
        current.queue_entry_id,
    )
    decision = _witness_eval_v02(
        env,
        source_artifact=current_artifact,
        node=node,
        current_entry=current,
        cell_input=cell_input,
        cell_budget=cell_budget_before,
        global_budget=global_budget_before,
        dependencies=dependencies,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        validation_report=validation_report,
        revise_observation=revise_observation,
        backpressure_state=backpressure_state,
    )
    if type(decision) is not transition_registry.TransitionDecisionV01:
        raise ValueError("g2d5_witness_transition_missing")
    budget_log = env["budget_log"]
    if type(budget_log) is not tuple:
        raise TypeError("g2d5_witness_budget_log_invalid")
    suffix = (
        (global_budget_after,)
        if cell_budget_after == global_budget_after
        else (cell_budget_after, global_budget_after)
    )
    for budget in suffix:
        if budget not in budget_log:
            budget_log = (*budget_log, budget)
    env["budget_log"] = budget_log
    source = env["source"]
    topology = env["topology"]
    topology_artifact = env["topology_artifact"]
    if (
        type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(topology_artifact) is not abi.KernelArtifactV01
    ):
        raise TypeError("g2d5_witness_advance_context_invalid")
    target = fr.advance_fractal_cell_queue_v02(
        source_context=source,
        topology=topology,
        current_entry=current,
        node=node,
        cell_input=cell_input,
        transition_decision=decision,
        cell_budget_after=cell_budget_after,
        global_budget_after=global_budget_after,
        dependencies=dependencies,
        local_child_result=None,
        local_child_result_artifact=None,
        cell_instantiation_order=tuple(item.cell_id for item in env["cell_inputs"]),
        projected_node_ids=cell_input.ordered_node_ids,
        round_start_queue_entries=round_entries,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        **_witness_prefix_kwargs_v02(env),
    )
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    if type(queue_log) is not tuple or type(artifact_log) is not tuple:
        raise TypeError("g2d5_witness_queue_log_invalid")
    artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
        target,
        topology_artifact=topology_artifact,
        predecessor_artifact=current_artifact,
        activation_parent_artifact=None,
        local_child_result_artifact=None,
        source_context=source,
        **{
            **_witness_prefix_kwargs_v02(env),
            "settled_queue_entry_log": (*queue_log, target),
        },
    )
    env["queue_log"] = (*queue_log, target)
    env["artifact_log"] = (*artifact_log, artifact)
    _witness_refresh_reports_v02(env)
    return target, artifact, decision


def _witness_make_ready_v02(
    env: dict[str, object],
    *,
    current: fr.FractalCellQueueEntryV02,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
    round_entries: tuple[fr.FractalCellQueueEntryV02, ...] | None = None,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    abi.KernelArtifactV01,
    transition_registry.TransitionDecisionV01,
]:
    budgets = _witness_budget_by_id_v02(env)
    return _witness_advance_v02(
        env,
        current=current,
        node=node,
        cell_input=cell_input,
        cell_budget_before=budgets[current.cell_budget_id],
        global_budget_before=budgets[current.global_budget_id],
        cell_budget_after=budgets[current.cell_budget_id],
        global_budget_after=budgets[current.global_budget_id],
        dependencies=dependencies,
        round_entries=(
            _witness_latest_queue_v02(env)
            if round_entries is None
            else round_entries
        ),
        queue_reason_codes=(
            ("g2d_transition_backpressure_deferred",)
            if backpressure_state is not None
            else ()
        ),
        backpressure_state=backpressure_state,
    )


def _witness_start_ready_v02(
    env: dict[str, object],
    *,
    ready: fr.FractalCellQueueEntryV02,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    round_entries: tuple[fr.FractalCellQueueEntryV02, ...] | None = None,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    abi.KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
    fr.FractalRuntimeBudgetV02,
]:
    budgets = _witness_budget_by_id_v02(env)
    ready_artifact = _witness_artifact_for_queue_v02(env, ready.queue_entry_id)
    decision = _witness_eval_v02(
        env,
        source_artifact=ready_artifact,
        node=node,
        current_entry=ready,
        cell_input=cell_input,
        cell_budget=budgets[ready.cell_budget_id],
        global_budget=budgets[ready.global_budget_id],
        dependencies=dependencies,
    )
    if type(decision) is not transition_registry.TransitionDecisionV01:
        raise ValueError("g2d5_witness_start_decision_missing")
    live_cell, live_global = _witness_live_budget_heads_v02(
        env,
        cell_id=ready.cell_id,
    )
    allocation_parent = (
        budgets[live_cell.allocation_parent_budget_id]
        if live_cell.allocation_parent_budget_id is not None
        else None
    )
    start_cell = _witness_budget_successor_v02(
        env,
        live_cell,
        event="START_NODE",
        decision=decision,
        cell_input=cell_input,
        allocation_parent=allocation_parent,
        owning_cell_id=ready.cell_id,
        scope=live_cell.budget_scope,
    )
    start_global = (
        start_cell
        if ready.cell_id == env["topology"].root_cell_id
        else _witness_budget_successor_v02(
            env,
            live_global,
            event="START_NODE",
            decision=decision,
            cell_input=cell_input,
            paired_cell_budget=start_cell,
        )
    )
    running, running_artifact, _ = _witness_advance_v02(
        env,
        current=ready,
        node=node,
        cell_input=cell_input,
        cell_budget_before=budgets[ready.cell_budget_id],
        global_budget_before=budgets[ready.global_budget_id],
        cell_budget_after=start_cell,
        global_budget_after=start_global,
        dependencies=dependencies,
        round_entries=(
            _witness_latest_queue_v02(env)
            if round_entries is None
            else round_entries
        ),
    )
    return running, running_artifact, start_cell, start_global


def _witness_start_node_v02(
    env: dict[str, object],
    *,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
) -> tuple[
    fr.FractalCellQueueEntryV02,
    abi.KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
]:
    current_rows = tuple(
        item
        for item in _witness_latest_queue_v02(env)
        if item.cell_id == cell_input.cell_id and item.node_id == node.node_id
    )
    current = _exactly_one_v02(
        current_rows,
        label="g2d5_witness_current_queue",
    )
    if type(current) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_witness_current_queue_type_invalid")
    ready, _artifact, _ = _witness_make_ready_v02(
        env,
        current=current,
        node=node,
        cell_input=cell_input,
        dependencies=dependencies,
    )
    running, artifact, _cell_budget, global_budget = _witness_start_ready_v02(
        env,
        ready=ready,
        node=node,
        cell_input=cell_input,
        dependencies=dependencies,
    )
    return running, artifact, global_budget


def _witness_complete_root_dependency_v02(
    env: dict[str, object],
) -> tuple[fr.FractalCellQueueEntryV02, abi.KernelArtifactV01]:
    nodes = env["nodes"]
    root_input = env["root_input"]
    reference = env["reference_bundle"]
    if (
        type(nodes) is not tuple
        or type(root_input) is not fr.FractalCellInputV02
        or type(reference) is not fr.FractalRuntimeExecutionBundleV02
    ):
        raise TypeError("g2d5_witness_dependency_context_invalid")
    node = nodes[0]
    running, _artifact, start_budget = _witness_start_node_v02(
        env,
        node=node,
        cell_input=root_input,
    )
    donor = _exactly_one_v02(
        tuple(
            item
            for item in reference.queue_entries
            if item.cell_id == root_input.cell_id
            and item.node_id == node.node_id
            and item.state == "VALIDATING"
        ),
        label="g2d5_witness_observation_donor",
    )
    if type(donor) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_witness_observation_donor_type_invalid")
    running_artifact = _witness_artifact_for_queue_v02(env, running.queue_entry_id)
    t06 = _witness_eval_v02(
        env,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=root_input,
        cell_budget=start_budget,
        global_budget=start_budget,
        queue_reason_codes=donor.queue_reason_codes,
        observed_output_refs=donor.observed_output_refs,
        observed_evidence_refs=donor.observed_evidence_refs,
        advisory_refs=donor.advisory_refs,
    )
    if type(t06) is not transition_registry.TransitionDecisionV01:
        raise ValueError("g2d5_witness_finish_decision_missing")
    finish_budget = _witness_budget_successor_v02(
        env,
        start_budget,
        event="FINISH_NODE",
        decision=t06,
        cell_input=root_input,
    )
    validating, _validating_artifact, _ = _witness_advance_v02(
        env,
        current=running,
        node=node,
        cell_input=root_input,
        cell_budget_before=start_budget,
        global_budget_before=start_budget,
        cell_budget_after=finish_budget,
        global_budget_after=finish_budget,
        dependencies=(),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=donor.queue_reason_codes,
        observed_output_refs=donor.observed_output_refs,
        observed_evidence_refs=donor.observed_evidence_refs,
        advisory_refs=donor.advisory_refs,
    )
    terminal, terminal_artifact, _ = _witness_advance_v02(
        env,
        current=validating,
        node=node,
        cell_input=root_input,
        cell_budget_before=finish_budget,
        global_budget_before=finish_budget,
        cell_budget_after=finish_budget,
        global_budget_after=finish_budget,
        dependencies=(),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
    )
    _require_v02(terminal.state == "COMPLETED", "g2d5_witness_dependency_incomplete")
    return terminal, terminal_artifact


def _witness_activate_child_v02(
    env: dict[str, object],
    *,
    slot_running: fr.FractalCellQueueEntryV02,
    dependency: fr.FractalCellQueueEntryV02,
) -> dict[str, object]:
    source = env["source"]
    topology = env["topology"]
    topology_artifact = env["topology_artifact"]
    parent_input = env["root_input"]
    root_create = env["root_create"]
    nodes = env["nodes"]
    initial_root_queues = env["root_initial_queues"]
    if (
        type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(topology_artifact) is not abi.KernelArtifactV01
        or type(parent_input) is not fr.FractalCellInputV02
        or type(root_create) is not fr.FractalRuntimeBudgetV02
        or type(nodes) is not tuple
        or type(initial_root_queues) is not tuple
    ):
        raise TypeError("g2d5_witness_child_context_invalid")
    child_id = slot_running.planned_child_cell_id
    if type(child_id) is not str:
        raise ValueError("g2d5_witness_planned_child_missing")
    node_rows = tuple(item for item in nodes if item.node_id == slot_running.node_id)
    slot_node = _exactly_one_v02(node_rows, label="g2d5_witness_slot_node")
    if type(slot_node) is not fr.RuntimeTopologyNodeV02:
        raise TypeError("g2d5_witness_slot_node_type_invalid")
    canonical_child_index = slot_node.canonical_index - 1
    slot_artifact = _witness_artifact_for_queue_v02(
        env,
        slot_running.queue_entry_id,
    )
    budgets = _witness_budget_by_id_v02(env)
    gate_result = _witness_eval_v02(
        env,
        source_artifact=slot_artifact,
        node=slot_node,
        current_entry=slot_running,
        cell_input=parent_input,
        cell_budget=budgets[slot_running.cell_budget_id],
        global_budget=budgets[slot_running.global_budget_id],
        dependencies=(dependency,),
    )
    _require_v02(gate_result is None, "g2d5_witness_child_gate_not_open")
    _cell_head, live_global = _witness_live_budget_heads_v02(
        env,
        cell_id=topology.root_cell_id,
    )
    child_allocated = fr.build_fractal_runtime_budget_v02(
        policy=source.runtime_policy,
        topology_seed=env["seed"],
        allocation_parent_budget=root_create,
        predecessor_budget=None,
        owning_cell_id=child_id,
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=initial_root_queues,
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    projection = fr.project_parent_child_scope_v02(
        source_context=source,
        topology=topology,
        parent_input=parent_input,
        child_cell_id=child_id,
        child_scope_ref=topology.accepted_scope_ref,
        parent_budget=root_create,
        child_budget=child_allocated,
        global_budget=live_global,
    )
    child_active = _witness_budget_successor_v02(
        env,
        child_allocated,
        event="ACTIVATE",
        cell_input=parent_input,
        allocation_parent=root_create,
        owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL",
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=initial_root_queues,
    )
    global_active = _witness_budget_successor_v02(
        env,
        live_global,
        event="ACTIVATE",
        cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=initial_root_queues,
        paired_cell_budget=child_active,
    )
    child_create = _witness_budget_successor_v02(
        env,
        child_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        allocation_parent=root_create,
        owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL",
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=initial_root_queues,
    )
    global_create = _witness_budget_successor_v02(
        env,
        global_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=initial_root_queues,
        paired_cell_budget=child_create,
    )
    env["budget_log"] = (
        *env["budget_log"],
        child_allocated,
        child_active,
        global_active,
        child_create,
        global_create,
    )
    scope_report = fr.validate_parent_child_scope_against_sources_v02(
        projection,
        source_context=source,
        topology=topology,
        parent_input=parent_input,
        parent_budget=root_create,
        child_budget=child_allocated,
        global_budget=live_global,
    )
    _require_pass_v02(scope_report, label="g2d5_witness_scope")
    env["scope_projections"] = (*env["scope_projections"], projection)
    env["scope_reports"] = (*env["scope_reports"], scope_report)
    _witness_refresh_reports_v02(env)
    leaf_nodes = tuple(
        item for item in nodes if item.canonical_index in {0, 4, 5, 6}
    )
    _require_v02(
        tuple(item.canonical_index for item in leaf_nodes) == (0, 4, 5, 6),
        "g2d5_witness_leaf_node_geometry",
    )
    admission_decisions: list[transition_registry.TransitionDecisionV01] = []
    for node in leaf_nodes:
        decision = _witness_eval_v02(
            env,
            source_artifact=topology_artifact,
            node=node,
            current_entry=None,
            cell_input=None,
            cell_budget=child_create,
            global_budget=global_create,
            cell_id=child_id,
            parent_cell_id=topology.root_cell_id,
            cell_depth=1,
            scope_ref=projection.child_scope_ref,
        )
        if type(decision) is not transition_registry.TransitionDecisionV01:
            raise ValueError("g2d5_witness_child_admission_decision_missing")
        admission_decisions.append(decision)
    child_queues = fr.admit_runtime_execution_topology_v02(
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        topology_transition_decision=env["topology_decision"],
        cell_id=child_id,
        parent_cell_id=topology.root_cell_id,
        parent_slot_artifact=slot_artifact,
        cell_depth=1,
        scope_ref=projection.child_scope_ref,
        cell_budget=child_create,
        global_budget=global_create,
        projected_nodes=leaf_nodes,
        planned_child_cell_ids=(),
        admission_decisions=tuple(admission_decisions),
        cell_instantiation_order=tuple(item.cell_id for item in env["cell_inputs"]) + (child_id,),
        **_witness_prefix_kwargs_v02(env),
    )
    child_artifacts: list[abi.KernelArtifactV01] = []
    for entry in child_queues:
        queue_log = env["queue_log"]
        artifact_log = env["artifact_log"]
        artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry,
            topology_artifact=topology_artifact,
            predecessor_artifact=None,
            activation_parent_artifact=slot_artifact,
            local_child_result_artifact=None,
            source_context=source,
            **{
                **_witness_prefix_kwargs_v02(env),
                "settled_queue_entry_log": (*queue_log, entry),
            },
        )
        env["queue_log"] = (*queue_log, entry)
        env["artifact_log"] = (*artifact_log, artifact)
        child_artifacts.append(artifact)
        _witness_refresh_reports_v02(env)
    child_input = fr.build_fractal_cell_input_from_queue_v02(
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        cell_id=child_id,
        parent_cell_id=topology.root_cell_id,
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        initial_queue_entries=child_queues,
        initial_queue_artifacts=tuple(child_artifacts),
        ordered_planned_child_cell_ids=(),
        **_witness_prefix_kwargs_v02(env),
    )
    input_report = fr.validate_fractal_cell_input_against_sources_v02(
        child_input,
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        queue_entries=child_queues,
        queue_artifacts=tuple(child_artifacts),
        **_witness_prefix_kwargs_v02(env),
    )
    _require_pass_v02(input_report, label="g2d5_witness_child_input")
    env["cell_inputs"] = (*env["cell_inputs"], child_input)
    env["input_reports"] = (*env["input_reports"], input_report)
    _witness_refresh_reports_v02(env)
    return {
        "cell_id": child_id,
        "input": child_input,
        "nodes": leaf_nodes,
        "queues": child_queues,
        "artifacts": tuple(child_artifacts),
    }


def _witness_object_ids_v02(env: dict[str, object]) -> tuple[str, ...]:
    return (
        *(item.budget_id for item in env["budget_log"]),
        *(item.queue_entry_id for item in env["queue_log"]),
        *(item.artifact_id for item in env["artifact_log"]),
        *(item.cell_input_id for item in env["cell_inputs"]),
        *(item.projection_id for item in env["scope_projections"]),
        *(item.backpressure_id for item in env["backpressure_states"]),
        *(item.validation_report_id for item in env["validation_reports"]),
    )


def _build_backpressure_witness_v02(
    run: _AcceptedRunV02,
) -> _BackpressureWitnessV02:
    env = _witness_initial_environment_v02(run)
    nodes = env["nodes"]
    root_input = env["root_input"]
    source = env["source"]
    topology = env["topology"]
    if (
        type(nodes) is not tuple
        or type(root_input) is not fr.FractalCellInputV02
        or type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
    ):
        raise TypeError("g2d5_backpressure_context_invalid")
    dependency, _dependency_artifact = _witness_complete_root_dependency_v02(env)
    p1, _p1_artifact, _ = _witness_start_node_v02(
        env,
        node=nodes[1],
        cell_input=root_input,
        dependencies=(dependency,),
    )
    p2, _p2_artifact, _ = _witness_start_node_v02(
        env,
        node=nodes[2],
        cell_input=root_input,
        dependencies=(dependency,),
    )
    _require_v02(
        _witness_live_budget_heads_v02(
            env,
            cell_id=topology.root_cell_id,
        )[1].current_parallelism
        == 2,
        "g2d5_backpressure_parent_parallelism",
    )
    c1 = _witness_activate_child_v02(
        env,
        slot_running=p1,
        dependency=dependency,
    )
    c2 = _witness_activate_child_v02(
        env,
        slot_running=p2,
        dependency=dependency,
    )
    c1_input = c1["input"]
    c2_input = c2["input"]
    c1_nodes = c1["nodes"]
    c2_nodes = c2["nodes"]
    c1_queues = c1["queues"]
    c2_queues = c2["queues"]
    if (
        type(c1_input) is not fr.FractalCellInputV02
        or type(c2_input) is not fr.FractalCellInputV02
        or type(c1_nodes) is not tuple
        or type(c2_nodes) is not tuple
        or type(c1_queues) is not tuple
        or type(c2_queues) is not tuple
    ):
        raise TypeError("g2d5_backpressure_child_geometry_invalid")
    round_one_start = _witness_latest_queue_v02(env)
    c1_ready, _c1_ready_artifact, _ = _witness_make_ready_v02(
        env,
        current=c1_queues[0],
        node=c1_nodes[0],
        cell_input=c1_input,
        round_entries=round_one_start,
    )
    live_global = _witness_live_budget_heads_v02(
        env,
        cell_id=topology.root_cell_id,
    )[1]
    s0 = fr.evaluate_fractal_backpressure_v02(
        source_context=source,
        topology=topology,
        policy=source.runtime_policy,
        global_budget=live_global,
        queue_entries=_witness_latest_queue_v02(env),
        admission_round=c1_ready.admission_round,
        **_witness_prefix_kwargs_v02(env),
    )
    if type(s0) is not fr.FractalBackpressureStateV02:
        raise ValueError("g2d5_backpressure_s0_missing")
    s0_validation = fr.validate_fractal_backpressure_state_v02(s0)
    _require_pass_v02(s0_validation, label="g2d5_backpressure_s0")
    _require_v02(
        s0.deferred_queue_entry_ids == (c2_queues[0].queue_entry_id,),
        "g2d5_backpressure_s0_deferred_geometry",
    )
    env["backpressure_states"] = (s0,)
    first_deferred, first_deferred_artifact, first_t03 = _witness_make_ready_v02(
        env,
        current=c2_queues[0],
        node=c2_nodes[0],
        cell_input=c2_input,
        backpressure_state=s0,
        round_entries=round_one_start,
    )
    _require_v02(
        first_deferred.state == "PENDING"
        and first_deferred.queue_reason_codes
        == ("g2d_transition_backpressure_deferred",),
        "g2d5_backpressure_t03_invalid",
    )
    round_two_start = _witness_latest_queue_v02(env)
    c1_running, _c1_running_artifact, _c1_start, c1_global_start = (
        _witness_start_ready_v02(
            env,
            ready=c1_ready,
            node=c1_nodes[0],
            cell_input=c1_input,
            round_entries=round_two_start,
        )
    )
    _require_v02(
        c1_global_start.current_parallelism == source.runtime_policy.max_parallelism,
        "g2d5_backpressure_capacity_not_filled",
    )
    s1 = fr.evaluate_fractal_backpressure_v02(
        source_context=source,
        topology=topology,
        policy=source.runtime_policy,
        global_budget=c1_global_start,
        queue_entries=_witness_latest_queue_v02(env),
        admission_round=c1_running.admission_round,
        **_witness_prefix_kwargs_v02(env),
    )
    if type(s1) is not fr.FractalBackpressureStateV02:
        raise ValueError("g2d5_backpressure_s1_missing")
    s1_validation = fr.validate_fractal_backpressure_state_v02(s1)
    _require_pass_v02(s1_validation, label="g2d5_backpressure_s1")
    _require_v02(
        s1 != s0
        and s1.deferred_queue_entry_ids == (first_deferred.queue_entry_id,),
        "g2d5_backpressure_s1_geometry",
    )
    env["backpressure_states"] = (s0, s1)
    second_deferred, second_deferred_artifact, second_t03 = (
        _witness_make_ready_v02(
            env,
            current=first_deferred,
            node=c2_nodes[0],
            cell_input=c2_input,
            backpressure_state=s1,
            round_entries=round_two_start,
        )
    )
    suppression_before = _witness_object_ids_v02(env)
    suppressed = fr.evaluate_fractal_backpressure_v02(
        source_context=source,
        topology=topology,
        policy=source.runtime_policy,
        global_budget=c1_global_start,
        queue_entries=_witness_latest_queue_v02(env),
        admission_round=s1.evaluated_round + 1,
        **_witness_prefix_kwargs_v02(env),
    )
    suppression_after = _witness_object_ids_v02(env)
    _require_v02(
        suppressed is None and suppression_before == suppression_after,
        "g2d5_backpressure_suppression_failed",
    )
    merge_entry = _exactly_one_v02(
        tuple(
            item
            for item in _witness_latest_queue_v02(env)
            if item.cell_id == topology.root_cell_id
            and item.node_id == nodes[3].node_id
        ),
        label="g2d5_backpressure_dependency_wait",
    )
    if type(merge_entry) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_dependency_wait_type_invalid")
    dependency_wait_decision = _witness_eval_v02(
        env,
        source_artifact=_witness_artifact_for_queue_v02(
            env,
            merge_entry.queue_entry_id,
        ),
        node=nodes[3],
        current_entry=merge_entry,
        cell_input=root_input,
        cell_budget=_witness_budget_by_id_v02(env)[merge_entry.cell_budget_id],
        global_budget=_witness_budget_by_id_v02(env)[merge_entry.global_budget_id],
        dependencies=(p1, p2),
    )
    dependency_wait_validation = fr.validate_fractal_cell_queue_entry_v02(
        merge_entry
    )
    _require_v02(
        dependency_wait_decision is None
        and merge_entry.state == "PENDING"
        and merge_entry.queue_reason_codes == (),
        "g2d5_dependency_wait_invalid",
    )
    queue_order = tuple(item.queue_entry_id for item in env["queue_log"])
    reordered_log = (
        *env["queue_log"][:-2],
        env["queue_log"][-1],
        env["queue_log"][-2],
    )
    queue_order_error = ""
    try:
        fr.evaluate_fractal_backpressure_v02(
            source_context=source,
            topology=topology,
            policy=source.runtime_policy,
            global_budget=c1_global_start,
            queue_entries=_witness_latest_queue_v02(env),
            admission_round=s1.evaluated_round + 1,
            **{
                **_witness_prefix_kwargs_v02(env),
                "settled_queue_entry_log": reordered_log,
            },
        )
    except ValueError as exc:
        queue_order_error = str(exc)
    _require_v02(bool(queue_order_error), "g2d5_backpressure_reorder_accepted")
    return _BackpressureWitnessV02(
        source_context=source,
        topology=topology,
        topology_artifact_id=env["topology_artifact"].artifact_id,
        policy_id=source.runtime_policy.policy_id,
        s0=s0,
        s0_validation=s0_validation,
        s1=s1,
        s1_validation=s1_validation,
        deferred_source=c2_queues[0],
        first_deferred=first_deferred,
        first_deferred_artifact=first_deferred_artifact,
        first_t03_decision=first_t03,
        second_deferred=second_deferred,
        second_deferred_artifact=second_deferred_artifact,
        second_t03_decision=second_t03,
        suppression_before_ids=suppression_before,
        suppression_after_ids=suppression_after,
        dependency_wait=merge_entry,
        dependency_wait_validation=dependency_wait_validation,
        dependency_wait_decision_is_none=dependency_wait_decision is None,
        queue_order=queue_order,
        queue_order_error=queue_order_error,
    )


def _build_gate_boundary_witness_v02(
    run: _AcceptedRunV02,
) -> _GateBoundaryWitnessV02:
    env = _witness_initial_environment_v02(run)
    nodes = env["nodes"]
    root_input = env["root_input"]
    topology = env["topology"]
    source = env["source"]
    if (
        type(nodes) is not tuple
        or type(root_input) is not fr.FractalCellInputV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
        or type(source) is not fr.FractalRuntimeSourceContextV02
    ):
        raise TypeError("g2d5_gate_context_invalid")
    dependency, _ = _witness_complete_root_dependency_v02(env)
    p1, _p1_artifact, _ = _witness_start_node_v02(
        env,
        node=nodes[1],
        cell_input=root_input,
        dependencies=(dependency,),
    )
    p2, p2_artifact, _ = _witness_start_node_v02(
        env,
        node=nodes[2],
        cell_input=root_input,
        dependencies=(dependency,),
    )
    accepted_artifact_by_id = {
        item.artifact_id: item for item in run.bundle.queue_artifacts
    }
    admission_ref = _exactly_one_v02(
        tuple(
            item
            for item in run.bundle.causal_consumption_refs
            if item.decision_effect == "CHILD_ACTIVATION"
            and abi.kernel_artifact_to_plain_dict_v01(
                accepted_artifact_by_id[item.source_artifact_id]
            )["payload"]["planned_child_cell_id"]
            == p2.planned_child_cell_id
        ),
        label="g2d5_admission_causal_ref",
    )
    if type(admission_ref) is not abi.CausalConsumptionRefV01:
        raise TypeError("g2d5_admission_causal_ref_invalid")
    accepted_admission_source = accepted_artifact_by_id[
        admission_ref.source_artifact_id
    ]
    mutated_admission_source = _mutated_kernel_payload_artifact_v02(
        accepted_admission_source,
        pointer="/planned_child_cell_id",
        replacement=p1.planned_child_cell_id,
    )
    mutated_witness_admission_source = _mutated_kernel_payload_artifact_v02(
        p2_artifact,
        pointer="/planned_child_cell_id",
        replacement=p1.planned_child_cell_id,
    )
    admission_profile_validation = (
        fr.validate_fractal_runtime_causal_counterfactual_v02(
            execution_bundle=run.bundle,
            causal_ref=admission_ref,
            mutated_source_artifact=mutated_admission_source,
        )
    )
    _require_pass_v02(
        admission_profile_validation,
        label="g2d5_admission_profile_counterfactual",
    )
    admission_child_before = tuple(
        item.cell_input_id
        for item in env["cell_inputs"]
        if item.parent_cell_id is not None
    )
    admission_queue_before = tuple(
        item.queue_entry_id
        for item in env["queue_log"]
        if item.parent_cell_id is not None
        and item.predecessor_queue_entry_id is None
    )
    admission_artifact_before = tuple(
        _witness_artifact_for_queue_v02(env, item)
        .artifact_id
        for item in admission_queue_before
    )
    admission_error = ""
    admission_budgets = _witness_budget_by_id_v02(env)
    try:
        _witness_eval_v02(
            env,
            source_artifact=mutated_witness_admission_source,
            node=nodes[2],
            current_entry=p2,
            cell_input=root_input,
            cell_budget=admission_budgets[p2.cell_budget_id],
            global_budget=admission_budgets[p2.global_budget_id],
            dependencies=(dependency,),
        )
    except ValueError as exc:
        admission_error = str(exc)
    admission_child_after = tuple(
        item.cell_input_id
        for item in env["cell_inputs"]
        if item.parent_cell_id is not None
    )
    admission_queue_after = tuple(
        item.queue_entry_id
        for item in env["queue_log"]
        if item.parent_cell_id is not None
        and item.predecessor_queue_entry_id is None
    )
    admission_artifact_after = tuple(
        _witness_artifact_for_queue_v02(env, item)
        .artifact_id
        for item in admission_queue_after
    )
    _require_v02(
        bool(admission_error)
        and admission_child_before == admission_child_after
        and admission_queue_before == admission_queue_after
        and admission_artifact_before == admission_artifact_after,
        "g2d5_admission_mutation_created_child",
    )
    c1 = _witness_activate_child_v02(
        env,
        slot_running=p1,
        dependency=dependency,
    )
    c1_input = c1["input"]
    c1_nodes = c1["nodes"]
    c1_queues = c1["queues"]
    if (
        type(c1_input) is not fr.FractalCellInputV02
        or type(c1_nodes) is not tuple
        or type(c1_queues) is not tuple
    ):
        raise TypeError("g2d5_gate_child_geometry_invalid")
    c1_ready, _ready_artifact, _ = _witness_make_ready_v02(
        env,
        current=c1_queues[0],
        node=c1_nodes[0],
        cell_input=c1_input,
    )
    _c1_running, _c1_artifact, _c1_cell_start, global_start = (
        _witness_start_ready_v02(
            env,
            ready=c1_ready,
            node=c1_nodes[0],
            cell_input=c1_input,
        )
    )
    _require_v02(
        global_start.current_parallelism == source.runtime_policy.max_parallelism,
        "g2d5_gate_capacity_not_filled",
    )
    malformed_env = dict(env)
    malformed_entry = replace(
        p2,
        planned_child_cell_id="frchildcell_v02:" + "0" * 64,
    )
    malformed_validation = fr.validate_fractal_cell_queue_entry_v02(
        malformed_entry
    )
    _require_v02(
        malformed_validation.status == "FAIL_CLOSED",
        "g2d5_malformed_gate_candidate_accepted",
    )
    terminal_before = tuple(
        item.queue_entry_id
        for item in malformed_env["queue_log"]
        if item.state in fr.NODE_TERMINAL_OUTCOMES
    )
    causal_before: tuple[str, ...] = ()
    bundle_before: tuple[str, ...] = ()
    malformed_error = ""
    try:
        _witness_eval_v02(
            malformed_env,
            source_artifact=p2_artifact,
            node=nodes[2],
            current_entry=malformed_entry,
            cell_input=root_input,
            cell_budget=_witness_budget_by_id_v02(malformed_env)[p2.cell_budget_id],
            global_budget=_witness_budget_by_id_v02(malformed_env)[p2.global_budget_id],
            dependencies=(dependency,),
        )
    except ValueError as exc:
        malformed_error = str(exc)
    terminal_after = tuple(
        item.queue_entry_id
        for item in malformed_env["queue_log"]
        if item.state in fr.NODE_TERMINAL_OUTCOMES
    )
    causal_after: tuple[str, ...] = ()
    bundle_after: tuple[str, ...] = ()
    _require_v02(
        bool(malformed_error)
        and terminal_before == terminal_after
        and causal_before == causal_after
        and bundle_before == bundle_after,
        "g2d5_malformed_gate_created_output",
    )
    budgets = _witness_budget_by_id_v02(env)
    ready = _exactly_one_v02(
        tuple(
            item
            for item in env["queue_log"]
            if item.queue_entry_id == p2.predecessor_queue_entry_id
        ),
        label="g2d5_gate_ready_entry",
    )
    if type(ready) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_gate_ready_type_invalid")
    initial_entry = _exactly_one_v02(
        tuple(
            item
            for item in env["queue_log"]
            if item.queue_entry_id == ready.predecessor_queue_entry_id
        ),
        label="g2d5_gate_initial_entry",
    )
    if type(initial_entry) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_gate_initial_type_invalid")
    live_cell, live_global = _witness_live_budget_heads_v02(
        env,
        cell_id=p2.cell_id,
    )
    gate_evidence = (
        source.route_eligibility_artifact.artifact_id,
        env["topology_artifact"].artifact_id,
        root_input.cell_input_id,
        _witness_artifact_for_queue_v02(env, initial_entry.queue_entry_id).artifact_id,
        _witness_artifact_for_queue_v02(env, ready.queue_entry_id).artifact_id,
        p2_artifact.artifact_id,
        live_cell.budget_id,
        *(
            (live_global.budget_id,)
            if live_global.budget_id != live_cell.budget_id
            else ()
        ),
        _witness_artifact_for_queue_v02(env, dependency.queue_entry_id).artifact_id,
    )
    gate_reasons = ("g2d_required_child_failure",)
    invocation_before = tuple(
        item.cell_input_id
        for item in env["cell_inputs"]
        if item.parent_cell_id is not None
    )
    result_before: tuple[str, ...] = ()
    partial_before: tuple[str, ...] = ()
    denial_terminal_before = tuple(
        item.queue_entry_id
        for item in env["queue_log"]
        if item.state in fr.NODE_TERMINAL_OUTCOMES
    )
    anchor_cell = budgets[p2.cell_budget_id]
    anchor_global = budgets[p2.global_budget_id]
    t06 = _witness_eval_v02(
        env,
        source_artifact=p2_artifact,
        node=nodes[2],
        current_entry=p2,
        cell_input=root_input,
        cell_budget=anchor_cell,
        global_budget=anchor_global,
        dependencies=(dependency,),
        queue_reason_codes=gate_reasons,
        observed_evidence_refs=gate_evidence,
    )
    if type(t06) is not transition_registry.TransitionDecisionV01:
        raise ValueError("g2d5_gate_t06_missing")
    finish_cell = _witness_budget_successor_v02(
        env,
        live_cell,
        event="FINISH_NODE",
        decision=t06,
        cell_input=root_input,
        allocation_parent=(
            budgets[live_cell.allocation_parent_budget_id]
            if live_cell.allocation_parent_budget_id is not None
            else None
        ),
        owning_cell_id=p2.cell_id,
        scope=live_cell.budget_scope,
    )
    finish_global = (
        finish_cell
        if p2.cell_id == topology.root_cell_id
        else _witness_budget_successor_v02(
            env,
            live_global,
            event="FINISH_NODE",
            decision=t06,
            cell_input=root_input,
            paired_cell_budget=finish_cell,
        )
    )
    validating, validating_artifact, _ = _witness_advance_v02(
        env,
        current=p2,
        node=nodes[2],
        cell_input=root_input,
        cell_budget_before=anchor_cell,
        global_budget_before=anchor_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=(dependency,),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=gate_reasons,
        observed_evidence_refs=gate_evidence,
    )
    blocked, blocked_artifact, terminal_decision = _witness_advance_v02(
        env,
        current=validating,
        node=nodes[2],
        cell_input=root_input,
        cell_budget_before=finish_cell,
        global_budget_before=finish_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=(dependency,),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_evidence_refs=validating.observed_evidence_refs,
    )
    blocked_validation = fr.validate_fractal_cell_queue_entry_v02(blocked)
    _require_v02(
        blocked.state == "BLOCKED"
        and terminal_decision.rule_id == "g2d_t10_validating_to_blocked"
        and blocked_validation.status == "PASS",
        "g2d5_gate_blocked_terminal_invalid",
    )
    invocation_after = tuple(
        item.cell_input_id
        for item in env["cell_inputs"]
        if item.parent_cell_id is not None
    )
    result_after: tuple[str, ...] = ()
    partial_after: tuple[str, ...] = ()
    denial_terminal_after = tuple(
        item.queue_entry_id
        for item in env["queue_log"]
        if item.state in fr.NODE_TERMINAL_OUTCOMES
    )
    _require_v02(
        _created_set_delta_v02(
            denial_terminal_before,
            denial_terminal_after,
        )["created_ids"]
        == (blocked.queue_entry_id,),
        "g2d5_gate_terminal_delta_invalid",
    )
    merge_entry = _exactly_one_v02(
        tuple(
            item
            for item in _witness_latest_queue_v02(env)
            if item.cell_id == topology.root_cell_id
            and item.node_id == nodes[3].node_id
        ),
        label="g2d5_gate_merge_entry",
    )
    if type(merge_entry) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_gate_merge_type_invalid")
    merge_validation = fr.validate_fractal_cell_queue_entry_v02(merge_entry)
    merge_decision = _witness_eval_v02(
        env,
        source_artifact=_witness_artifact_for_queue_v02(
            env,
            merge_entry.queue_entry_id,
        ),
        node=nodes[3],
        current_entry=merge_entry,
        cell_input=root_input,
        cell_budget=_witness_budget_by_id_v02(env)[merge_entry.cell_budget_id],
        global_budget=_witness_budget_by_id_v02(env)[merge_entry.global_budget_id],
        dependencies=(p1, blocked),
    )
    _require_v02(
        merge_validation.status == "PASS" and merge_decision is None,
        "g2d5_gate_merge_not_constructible",
    )
    return _GateBoundaryWitnessV02(
        source_context=source,
        topology=topology,
        gate_disposition="VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL",
        gate_reason_codes=gate_reasons,
        gate_evidence_refs=gate_evidence,
        t06_decision=t06,
        validating_entry=validating,
        validating_artifact=validating_artifact,
        terminal_decision=terminal_decision,
        blocked_entry=blocked,
        blocked_artifact=blocked_artifact,
        blocked_validation=blocked_validation,
        merge_entry=merge_entry,
        merge_validation=merge_validation,
        merge_decision_is_none=merge_decision is None,
        invocation_before_ids=invocation_before,
        invocation_after_ids=invocation_after,
        result_before_ids=result_before,
        result_after_ids=result_after,
        partial_before_ids=partial_before,
        partial_after_ids=partial_after,
        denial_terminal_before_ids=denial_terminal_before,
        denial_terminal_after_ids=denial_terminal_after,
        malformed_axis="/current_entry/planned_child_cell_id",
        malformed_entry=malformed_entry,
        malformed_validation=malformed_validation,
        malformed_error=malformed_error,
        malformed_terminal_before_ids=terminal_before,
        malformed_terminal_after_ids=terminal_after,
        malformed_causal_before_ids=causal_before,
        malformed_causal_after_ids=causal_after,
        malformed_bundle_before_ids=bundle_before,
        malformed_bundle_after_ids=bundle_after,
        admission_mutation_axis="/source_artifact/planned_child_cell_id",
        admission_baseline_source_artifact=accepted_admission_source,
        admission_mutated_source_artifact=mutated_admission_source,
        admission_accepted_causal_ref=admission_ref,
        admission_profile_validation=admission_profile_validation,
        admission_error=admission_error,
        admission_expected_downstream_artifact_id=None,
        admission_child_input_before_ids=admission_child_before,
        admission_child_input_after_ids=admission_child_after,
        admission_initial_queue_before_ids=admission_queue_before,
        admission_initial_queue_after_ids=admission_queue_after,
        admission_initial_artifact_before_ids=admission_artifact_before,
        admission_initial_artifact_after_ids=admission_artifact_after,
    )


def _bundle_runtime_object_ids_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> tuple[str, ...]:
    return (
        *(item.budget_id for item in bundle.budgets),
        *(item.queue_entry_id for item in bundle.queue_entries),
        *(item.artifact_id for item in bundle.queue_artifacts),
        *(item.cell_input_id for item in bundle.cell_inputs),
        *(item.projection_id for item in bundle.scope_projections),
        *(item.observation_id for item in bundle.revise_observations),
        *(item.backpressure_id for item in bundle.backpressure_states),
        *(item.validation_report_id for item in bundle.validation_reports),
        *(item.result_id for item in bundle.cell_results),
        *(item.artifact_id for item in bundle.result_artifacts),
        *(item.partial_failure_id for item in bundle.partial_failures),
        *(_sha256_plain_v02(item) for item in bundle.causal_consumption_refs),
        bundle.runtime_trace.trace_id,
        bundle.runtime_report.report_id,
        bundle.report_artifact.artifact_id,
    )


def _derived_structural_child_id_v02(
    run: _AcceptedRunV02,
    *,
    parent_cell_id: str,
    canonical_child_index: int,
    child_scope_ref: str,
    child_depth: int,
) -> str:
    binding = run.bundle.source_binding
    return fr.derive_fractal_child_cell_id_v02(
        topology_seed_id=run.bundle.topology_seed.topology_seed_id,
        parent_cell_id=parent_cell_id,
        canonical_child_index=canonical_child_index,
        accepted_mode=binding.accepted_mode,
        selected_local_mode_profile_id=binding.selected_local_mode_profile_id,
        source_mode_profile_set_id=binding.source_mode_profile_set_id,
        child_scope_ref=child_scope_ref,
        runtime_policy_id=run.source_context.runtime_policy.policy_id,
        required_capability_ids=binding.required_downstream_capability_ids,
        forbidden_claims=run.source_context.runtime_policy.forbidden_claims,
        child_depth=child_depth,
    )


def _depth_input_variant_v02(
    run: _AcceptedRunV02,
    basis: fr.FractalCellInputV02,
    *,
    parent_cell_id: str,
    child_depth: int,
    canonical_child_index: int,
) -> fr.FractalCellInputV02:
    cell_id = _derived_structural_child_id_v02(
        run,
        parent_cell_id=parent_cell_id,
        canonical_child_index=canonical_child_index,
        child_scope_ref=f"{basis.scope_ref}:depth:{child_depth}",
        child_depth=child_depth,
    )
    trace_refs = tuple(
        cell_id if index == 1 else value
        for index, value in enumerate(basis.trace_refs)
    )
    result = _reidentified_v02(
        replace(
            basis,
            cell_id=cell_id,
            parent_cell_id=parent_cell_id,
            cell_depth=child_depth,
            trace_refs=trace_refs,
        ),
        identity_field="cell_input_id",
        rebuild=fr.rebuild_fractal_cell_input_identity_v02,
    )
    if type(result) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_depth_input_type_invalid")
    return result


def _build_depth_boundary_witness_v02(
    run: _AcceptedRunV02,
) -> _DepthBoundaryWitnessV02:
    bundle = run.bundle
    root_input = _exactly_one_v02(
        tuple(item for item in bundle.cell_inputs if item.parent_cell_id is None),
        label="g2d5_depth_root_input",
    )
    child_inputs = tuple(
        item for item in bundle.cell_inputs if item.parent_cell_id is not None
    )
    if (
        type(root_input) is not fr.FractalCellInputV02
        or not child_inputs
        or type(child_inputs[0]) is not fr.FractalCellInputV02
    ):
        raise TypeError("g2d5_depth_input_basis_invalid")
    depth_one = child_inputs[0]
    depth_two = _depth_input_variant_v02(
        run,
        depth_one,
        parent_cell_id=depth_one.cell_id,
        child_depth=2,
        canonical_child_index=0,
    )
    depth_three = _depth_input_variant_v02(
        run,
        depth_two,
        parent_cell_id=depth_two.cell_id,
        child_depth=3,
        canonical_child_index=1,
    )
    accepted_inputs = (root_input, depth_one, depth_two)
    accepted_validations = tuple(
        fr.validate_fractal_cell_input_v02(item) for item in accepted_inputs
    )
    rejected_validation = fr.validate_fractal_cell_input_v02(depth_three)
    _require_v02(
        tuple(item.cell_depth for item in accepted_inputs) == (0, 1, 2)
        and all(item.status == "PASS" for item in accepted_validations)
        and rejected_validation.status == "FAIL_CLOSED"
        and bool(rejected_validation.reason_codes),
        "g2d5_depth_boundary_invalid",
    )
    runtime_ids = _bundle_runtime_object_ids_v02(bundle)
    return _DepthBoundaryWitnessV02(
        accepted_inputs=accepted_inputs,
        accepted_validations=accepted_validations,
        rejected_input=depth_three,
        rejected_validation=rejected_validation,
        runtime_objects_before=runtime_ids,
        runtime_objects_after=runtime_ids,
    )


def _isolated_structural_child_cell_id_v02(
    run: _AcceptedRunV02,
    *,
    parent_cell_id: str,
    canonical_child_index: int,
    child_scope_ref: str,
    child_depth: int,
) -> str:
    if type(canonical_child_index) is not int or not 0 <= canonical_child_index <= 4:
        raise ValueError("g2d5_isolated_child_index_invalid")
    binding = run.bundle.source_binding
    material = [
        run.bundle.topology_seed.topology_seed_id,
        parent_cell_id,
        canonical_child_index,
        binding.accepted_mode,
        binding.selected_local_mode_profile_id,
        binding.source_mode_profile_set_id,
        child_scope_ref,
        run.source_context.runtime_policy.policy_id,
        list(binding.required_downstream_capability_ids),
        list(run.source_context.runtime_policy.forbidden_claims),
        child_depth,
    ]
    result = "frchildcell_v02:" + domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_CHILD_CELL",
        payload=canonical_json_bytes_v01(material),
    )
    if canonical_child_index in {0, 1}:
        _require_v02(
            result
            == _derived_structural_child_id_v02(
                run,
                parent_cell_id=parent_cell_id,
                canonical_child_index=canonical_child_index,
                child_scope_ref=child_scope_ref,
                child_depth=child_depth,
            ),
            "g2d5_isolated_child_derivation_mismatch",
        )
    return result


def _isolated_parent_planning_input_v02(
    parent_input: fr.FractalCellInputV02,
    planned_child_ids: tuple[str, ...],
) -> tuple[fr.FractalCellInputV02, fr.FractalRuntimeValidationReportV02]:
    planning_input = _reidentified_v02(
        replace(
            parent_input,
            requested_child_count=len(planned_child_ids),
            ordered_planned_child_cell_ids=planned_child_ids,
        ),
        identity_field="cell_input_id",
        rebuild=fr.rebuild_fractal_cell_input_identity_v02,
    )
    if type(planning_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_cell_tree_planning_input_invalid")
    report = fr.validate_fractal_cell_input_v02(planning_input)
    _require_v02(
        report.status == "FAIL_CLOSED" and bool(report.reason_codes),
        "g2d5_isolated_planning_carrier_accepted",
    )
    return planning_input, report


def _build_cell_create_budget_chain_v02(
    run: _AcceptedRunV02,
    *,
    predecessor_global: fr.FractalRuntimeBudgetV02,
    label: str,
) -> _CellTreeBuildV02:
    bundle = run.bundle
    policy = run.source_context.runtime_policy
    root_input = _exactly_one_v02(
        tuple(item for item in bundle.cell_inputs if item.parent_cell_id is None),
        label="g2d5_cell_boundary_root_input",
    )
    if type(root_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_cell_boundary_root_input_invalid")
    entry_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
    node_by_id = {item.node_id: item for item in bundle.topology_nodes}
    child_basis = _exactly_one_v02(
        tuple(
            item
            for item in bundle.cell_inputs
            if item.parent_cell_id is not None
        )[:1],
        label="g2d5_cell_tree_child_basis",
    )
    if type(child_basis) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_cell_tree_child_basis_invalid")
    child_initial_entries = tuple(
        entry_by_id[item] for item in child_basis.ordered_initial_queue_entry_ids
    )
    child_nodes = tuple(node_by_id[item] for item in child_basis.ordered_node_ids)
    root_create = bundle.budgets[2]
    _require_v02(
        root_create.budget_event_kind == "CELL_CREATE"
        and root_create.consumed_cell_count == 1
        and predecessor_global.consumed_cell_count == 1,
        "g2d5_cell_boundary_root_create_invalid",
    )
    suffix: list[fr.FractalRuntimeBudgetV02] = []
    rows: list[dict[str, object]] = []
    parent_child_rows: list[dict[str, object]] = []
    root_input_validation = fr.validate_fractal_cell_input_v02(root_input)
    _require_pass_v02(root_input_validation, label="g2d5_cell_tree_root_input")
    cell_rows: list[dict[str, object]] = [{
        "cell_number": 1,
        "cell_id": root_input.cell_id,
        "parent_cell_id": None,
        "cell_depth": 0,
        "canonical_child_index": None,
        "scope_projection_id": None,
        "scope_validation_report_id": None,
        "cell_input_id": root_input.cell_input_id,
        "cell_input_validation_report_id": root_input_validation.validation_report_id,
        "cell_input_validation_status": root_input_validation.status,
        "cell_create_budget_id": root_create.budget_id,
        "global_create_budget_id": root_create.budget_id,
        "global_consumed_cell_count": 1,
    }]
    accepted_ids: list[str] = [root_input.cell_id]
    accepted_input_by_cell: dict[str, fr.FractalCellInputV02] = {
        root_input.cell_id: root_input,
    }
    create_budget_by_cell: dict[str, fr.FractalRuntimeBudgetV02] = {
        root_input.cell_id: root_create,
    }
    global_before = predecessor_global
    planned_by_parent: dict[str, tuple[str, ...]] = {}
    depth_1_ids = tuple(
        _isolated_structural_child_cell_id_v02(
            run,
            parent_cell_id=root_input.cell_id,
            canonical_child_index=index,
            child_scope_ref=root_input.scope_ref,
            child_depth=1,
        )
        for index in range(4)
    )
    planned_by_parent[root_input.cell_id] = depth_1_ids
    depth_2_ids_by_parent = {
        parent_id: tuple(
            _isolated_structural_child_cell_id_v02(
                run,
                parent_cell_id=parent_id,
                canonical_child_index=index,
                child_scope_ref=root_input.scope_ref,
                child_depth=2,
            )
            for index in range(4)
        )
        for parent_id in depth_1_ids
    }
    depth_2_ids = tuple(
        child_id
        for parent_id in depth_1_ids
        for child_id in depth_2_ids_by_parent[parent_id]
    )
    planned_by_parent.update(depth_2_ids_by_parent)

    def build_accepted_child(
        *,
        parent_cell_id: str,
        child_id: str,
        child_depth: int,
        child_index: int,
    ) -> None:
        nonlocal global_before
        parent_input = accepted_input_by_cell[parent_cell_id]
        parent_create = create_budget_by_cell[parent_cell_id]
        planning_input, planning_validation = _isolated_parent_planning_input_v02(
            parent_input,
            planned_by_parent[parent_cell_id],
        )
        allocation_entries = tuple(
            entry_by_id[item]
            for item in parent_input.ordered_initial_queue_entry_ids
        )
        before = global_before
        child_allocation = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=parent_create,
            predecessor_budget=None,
            owning_cell_id=child_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ALLOCATED",
            budget_event_kind="INITIAL_ALLOCATION",
            budget_context_input=planning_input,
            canonical_child_index=child_index,
            allocation_queue_entries=allocation_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        child_activate = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=parent_create,
            predecessor_budget=child_allocation,
            owning_cell_id=child_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ACTIVE",
            budget_event_kind="ACTIVATE",
            budget_context_input=planning_input,
            canonical_child_index=child_index,
            allocation_queue_entries=allocation_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        global_activate = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=None,
            predecessor_budget=global_before,
            owning_cell_id=bundle.topology.root_cell_id,
            budget_scope="ROOT_GLOBAL_AND_CELL",
            budget_state="ACTIVE",
            budget_event_kind="ACTIVATE",
            budget_context_input=planning_input,
            canonical_child_index=child_index,
            allocation_queue_entries=allocation_entries,
            transition_decision=None,
            paired_cell_budget=child_activate,
            child_result=None,
        )
        child_create = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=parent_create,
            predecessor_budget=child_activate,
            owning_cell_id=child_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ACTIVE",
            budget_event_kind="CELL_CREATE",
            budget_context_input=planning_input,
            canonical_child_index=child_index,
            allocation_queue_entries=allocation_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        global_create = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=None,
            predecessor_budget=global_activate,
            owning_cell_id=bundle.topology.root_cell_id,
            budget_scope="ROOT_GLOBAL_AND_CELL",
            budget_state="ACTIVE",
            budget_event_kind="CELL_CREATE",
            budget_context_input=planning_input,
            canonical_child_index=child_index,
            allocation_queue_entries=allocation_entries,
            transition_decision=None,
            paired_cell_budget=child_create,
            child_result=None,
        )
        budgets = (
            child_allocation, child_activate, global_activate,
            child_create, global_create,
        )
        validations = tuple(
            fr.validate_fractal_runtime_budget_v02(item) for item in budgets
        )
        _require_v02(
            all(item.status == "PASS" for item in validations)
            and child_allocation.consumed_cell_count == 0
            and child_activate.consumed_cell_count == 0
            and global_activate.consumed_cell_count == before.consumed_cell_count
            and child_create.consumed_cell_count == 1
            and global_create.consumed_cell_count
            == before.consumed_cell_count + 1,
            "g2d5_cell_boundary_debit_invalid",
        )
        projection = fr.build_parent_child_scope_projection_v02(
            bundle.topology,
            bundle.source_binding,
            parent_cell_id=parent_cell_id,
            child_cell_id=child_id,
            parent_scope_ref=parent_input.scope_ref,
            child_scope_ref=parent_input.scope_ref,
            parent_allowed_capability_ids=policy.allowed_capability_ids,
            child_allowed_capability_ids=policy.allowed_capability_ids,
            parent_forbidden_claims=policy.forbidden_claims,
            child_forbidden_claims=policy.forbidden_claims,
            parent_ttl_units=run.source_context.router_input.local_routing_snapshot.ttl_seconds,
            child_ttl_units=run.source_context.router_input.local_routing_snapshot.ttl_seconds,
            parent_budget=parent_create,
            child_budget=child_allocation,
            global_budget=before,
            child_depth=child_depth,
        )
        projection_validation = fr.validate_parent_child_scope_projection_v02(
            projection
        )
        _require_pass_v02(
            projection_validation,
            label="g2d5_cell_tree_scope_projection",
        )
        child_input = fr.build_fractal_cell_input_v02(
            bundle.topology,
            cell_id=child_id,
            parent_cell_id=parent_cell_id,
            scope_projection=projection,
            scope_ref=projection.child_scope_ref,
            cell_budget=child_create,
            global_budget=global_create,
            initial_queue_entries=child_initial_entries,
            required_queue_entries=child_initial_entries,
            cell_depth=child_depth,
            requested_child_count=0,
            ordered_planned_child_cell_ids=(),
            ordered_nodes=child_nodes,
            evidence_refs=(
                projection.projection_id,
                child_allocation.budget_id,
                child_create.budget_id,
            ),
            context_refs=(
                bundle.source_binding.source_binding_id,
                parent_input.cell_input_id,
            ),
            time_envelope_ref=root_input.time_envelope_ref,
        )
        child_input_validation = fr.validate_fractal_cell_input_v02(child_input)
        _require_pass_v02(
            child_input_validation,
            label="g2d5_cell_tree_input",
        )
        suffix.extend(budgets)
        accepted_ids.append(child_id)
        accepted_input_by_cell[child_id] = child_input
        create_budget_by_cell[child_id] = child_create
        cell_number = len(accepted_ids)
        rows.append({
            "cell_number": cell_number,
            "cell_id": child_id,
            "parent_cell_id": parent_cell_id,
            "cell_depth": child_depth,
            "canonical_child_index": child_index,
            "planning_input_id": planning_input.cell_input_id,
            "planning_validation_id": planning_validation.validation_report_id,
            "planning_validation_status": planning_validation.status,
            "planning_reason_codes": planning_validation.reason_codes,
            "global_before_budget_id": before.budget_id,
            "global_before_consumed_cell_count": before.consumed_cell_count,
            "child_allocation_budget_id": child_allocation.budget_id,
            "child_allocation_validation_id": validations[0].validation_report_id,
            "child_allocation_consumed_cell_count": child_allocation.consumed_cell_count,
            "child_activate_budget_id": child_activate.budget_id,
            "child_activate_validation_id": validations[1].validation_report_id,
            "child_activate_consumed_cell_count": child_activate.consumed_cell_count,
            "global_activate_budget_id": global_activate.budget_id,
            "global_activate_validation_id": validations[2].validation_report_id,
            "global_activate_consumed_cell_count": global_activate.consumed_cell_count,
            "child_create_budget_id": child_create.budget_id,
            "child_create_validation_id": validations[3].validation_report_id,
            "child_create_consumed_cell_count": child_create.consumed_cell_count,
            "global_create_budget_id": global_create.budget_id,
            "global_create_validation_id": validations[4].validation_report_id,
            "global_create_consumed_cell_count": global_create.consumed_cell_count,
            "global_create_remaining_cell_count": global_create.remaining_cell_count,
            "scope_projection_id": projection.projection_id,
            "scope_validation_id": projection_validation.validation_report_id,
            "cell_input_id": child_input.cell_input_id,
            "cell_input_validation_id": child_input_validation.validation_report_id,
        })
        parent_child_rows.append({
            "parent_cell_id": parent_cell_id,
            "child_cell_id": child_id,
            "child_depth": child_depth,
            "canonical_child_index": child_index,
            "scope_projection_id": projection.projection_id,
            "scope_validation_report_id": projection_validation.validation_report_id,
            "cell_input_id": child_input.cell_input_id,
            "cell_input_validation_report_id": child_input_validation.validation_report_id,
            "cell_create_budget_id": child_create.budget_id,
            "global_create_budget_id": global_create.budget_id,
        })
        cell_rows.append({
            "cell_number": cell_number,
            "cell_id": child_id,
            "parent_cell_id": parent_cell_id,
            "cell_depth": child_depth,
            "canonical_child_index": child_index,
            "scope_projection_id": projection.projection_id,
            "scope_validation_report_id": projection_validation.validation_report_id,
            "cell_input_id": child_input.cell_input_id,
            "cell_input_validation_report_id": child_input_validation.validation_report_id,
            "cell_input_validation_status": child_input_validation.status,
            "cell_create_budget_id": child_create.budget_id,
            "global_create_budget_id": global_create.budget_id,
            "global_consumed_cell_count": global_create.consumed_cell_count,
        })
        global_before = global_create

    for index, child_id in enumerate(depth_1_ids):
        build_accepted_child(
            parent_cell_id=root_input.cell_id,
            child_id=child_id,
            child_depth=1,
            child_index=index,
        )
    for parent_id in depth_1_ids:
        for index, child_id in enumerate(depth_2_ids_by_parent[parent_id]):
            build_accepted_child(
                parent_cell_id=parent_id,
                child_id=child_id,
                child_depth=2,
                child_index=index,
            )

    attempted_parent_id = root_input.cell_id
    attempted_cell_id = _isolated_structural_child_cell_id_v02(
        run,
        parent_cell_id=attempted_parent_id,
        canonical_child_index=4,
        child_scope_ref=root_input.scope_ref,
        child_depth=1,
    )
    attempted_error = ""
    attempted_global: fr.FractalRuntimeBudgetV02 | None = None
    attempted_planning, _attempted_planning_report = (
        _isolated_parent_planning_input_v02(
            root_input,
            (*depth_1_ids, attempted_cell_id),
        )
    )
    root_initial_entries = tuple(
        entry_by_id[item] for item in root_input.ordered_initial_queue_entry_ids
    )
    try:
        attempted_allocation = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=root_create,
            predecessor_budget=None,
            owning_cell_id=attempted_cell_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ALLOCATED",
            budget_event_kind="INITIAL_ALLOCATION",
            budget_context_input=attempted_planning,
            canonical_child_index=4,
            allocation_queue_entries=root_initial_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        attempted_activate = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=root_create,
            predecessor_budget=attempted_allocation,
            owning_cell_id=attempted_cell_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ACTIVE",
            budget_event_kind="ACTIVATE",
            budget_context_input=attempted_planning,
            canonical_child_index=4,
            allocation_queue_entries=root_initial_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        attempted_global_activate = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=None,
            predecessor_budget=global_before,
            owning_cell_id=bundle.topology.root_cell_id,
            budget_scope="ROOT_GLOBAL_AND_CELL",
            budget_state="ACTIVE",
            budget_event_kind="ACTIVATE",
            budget_context_input=attempted_planning,
            canonical_child_index=4,
            allocation_queue_entries=root_initial_entries,
            transition_decision=None,
            paired_cell_budget=attempted_activate,
            child_result=None,
        )
        attempted_create = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=root_create,
            predecessor_budget=attempted_activate,
            owning_cell_id=attempted_cell_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ACTIVE",
            budget_event_kind="CELL_CREATE",
            budget_context_input=attempted_planning,
            canonical_child_index=4,
            allocation_queue_entries=root_initial_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        attempted_global = fr.build_fractal_runtime_budget_v02(
            policy=policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=None,
            predecessor_budget=attempted_global_activate,
            owning_cell_id=bundle.topology.root_cell_id,
            budget_scope="ROOT_GLOBAL_AND_CELL",
            budget_state="ACTIVE",
            budget_event_kind="CELL_CREATE",
            budget_context_input=attempted_planning,
            canonical_child_index=4,
            allocation_queue_entries=root_initial_entries,
            transition_decision=None,
            paired_cell_budget=attempted_create,
            child_result=None,
        )
    except ValueError as exc:
        attempted_error = str(exc)
    final_validation = fr.validate_fractal_runtime_budget_v02(global_before)
    _require_v02(
        label in {"case30", "case58-budget-exhaustion"}
        and tuple(len(planned_by_parent[item]) for item in (root_input.cell_id, *depth_1_ids))
        == (4, 4, 4, 4, 4)
        and tuple(item["cell_depth"] for item in cell_rows).count(0) == 1
        and tuple(item["cell_depth"] for item in cell_rows).count(1) == 4
        and tuple(item["cell_depth"] for item in cell_rows).count(2) == 16
        and len(accepted_ids) == policy.max_total_cells
        and len(set(accepted_ids)) == policy.max_total_cells
        and global_before.consumed_cell_count == policy.max_total_cells
        and global_before.remaining_cell_count == 0
        and final_validation.status == "PASS"
        and attempted_global is None
        and attempted_error == "g2d_budget_overflow",
        "g2d5_cell_boundary_limit_invalid",
    )
    return _CellTreeBuildV02(
        budget_suffix=tuple(suffix),
        accepted_cell_rows=tuple(rows),
        cell_rows=tuple(cell_rows),
        parent_child_rows=tuple(parent_child_rows),
        accepted_cell_ids=tuple(accepted_ids),
        depth_1_cell_ids=depth_1_ids,
        depth_2_cell_ids=depth_2_ids,
        final_global_budget=global_before,
        final_global_validation=final_validation,
        attempted_cell_id=attempted_cell_id,
        attempted_parent_id=attempted_parent_id,
        attempted_error=attempted_error,
        attempted_global_budget=attempted_global,
    )


def _build_cell_boundary_witness_v02(
    run: _AcceptedRunV02,
) -> _CellBoundaryWitnessV02:
    bundle = run.bundle
    root_budgets = bundle.budgets[:3]
    root_validations = tuple(
        fr.validate_fractal_runtime_budget_v02(item) for item in root_budgets
    )
    _require_v02(
        tuple(item.budget_event_kind for item in root_budgets)
        == ("INITIAL_ALLOCATION", "ACTIVATE", "CELL_CREATE")
        and all(item.status == "PASS" for item in root_validations)
        and tuple(item.consumed_cell_count for item in root_budgets) == (0, 0, 1),
        "g2d5_cell_boundary_root_events_invalid",
    )
    tree = _build_cell_create_budget_chain_v02(
        run,
        predecessor_global=root_budgets[-1],
        label="case30",
    )
    rejected_budget, rejected_validation = _mutated_budget_report_v02(
        tree.final_global_budget,
        consumed_cell_count=run.source_context.runtime_policy.max_total_cells + 1,
        remaining_cell_count=-1,
    )
    _require_v02(
        rejected_validation.status == "FAIL_CLOSED"
        and bool(rejected_validation.reason_codes),
        "g2d5_cell_boundary_rejected_validation_invalid",
    )
    runtime_ids = _bundle_runtime_object_ids_v02(bundle)
    return _CellBoundaryWitnessV02(
        tree_shape=(1, 4, 16),
        depth_counts=((0, 1), (1, 4), (2, 16)),
        cell_rows=tree.cell_rows,
        parent_child_rows=tree.parent_child_rows,
        root_cell_id=tree.accepted_cell_ids[0],
        depth_1_cell_ids=tree.depth_1_cell_ids,
        depth_2_cell_ids=tree.depth_2_cell_ids,
        root_budget_event_rows=tuple(
            (
                item.budget_event_kind,
                item.budget_id,
                item.consumed_cell_count,
                item.remaining_cell_count,
                report.validation_report_id,
                report.status,
            )
            for item, report in zip(root_budgets, root_validations, strict=True)
        ),
        accepted_cell_rows=tree.accepted_cell_rows,
        accepted_cell_ids=tree.accepted_cell_ids,
        budget_suffix=tree.budget_suffix,
        final_global_budget=tree.final_global_budget,
        final_global_validation=tree.final_global_validation,
        attempted_cell_id=tree.attempted_cell_id,
        attempted_parent_id=tree.attempted_parent_id,
        attempted_error=tree.attempted_error,
        attempted_global_budget=tree.attempted_global_budget,
        rejected_budget=rejected_budget,
        rejected_validation=rejected_validation,
        runtime_objects_before=runtime_ids,
        runtime_objects_after=runtime_ids,
    )


def _build_budget_exhaustion_witness_v02(
    run: _AcceptedRunV02,
    cell_boundary: _CellBoundaryWitnessV02,
) -> _BudgetExhaustionWitnessV02:
    env = _witness_initial_environment_v02(run)
    nodes = env["nodes"]
    root_input = env["root_input"]
    source = env["source"]
    topology = env["topology"]
    if (
        type(nodes) is not tuple
        or type(root_input) is not fr.FractalCellInputV02
        or type(source) is not fr.FractalRuntimeSourceContextV02
        or type(topology) is not fr.RuntimeExecutionTopologyV02
    ):
        raise TypeError("g2d5_budget_exhaustion_context_invalid")
    dependency, _ = _witness_complete_root_dependency_v02(env)
    slot, slot_artifact, budget_before = _witness_start_node_v02(
        env,
        node=nodes[1],
        cell_input=root_input,
        dependencies=(dependency,),
    )
    budget_before_ids = tuple(item.budget_id for item in env["budget_log"])
    queue_before_ids = tuple(item.queue_entry_id for item in env["queue_log"])
    tree = _build_cell_create_budget_chain_v02(
        run,
        predecessor_global=budget_before,
        label="case58-budget-exhaustion",
    )
    exhausted = tree.final_global_budget
    exhausted_validation = tree.final_global_validation
    env["budget_log"] = (*env["budget_log"], *tree.budget_suffix)
    _require_v02(
        tree.accepted_cell_ids == cell_boundary.accepted_cell_ids
        and tree.depth_1_cell_ids == cell_boundary.depth_1_cell_ids
        and tree.depth_2_cell_ids == cell_boundary.depth_2_cell_ids
        and exhausted.remaining_cell_count == 0
        and exhausted.consumed_cell_count == source.runtime_policy.max_total_cells,
        "g2d5_budget_exhaustion_head_invalid",
    )
    budgets = _witness_budget_by_id_v02(env)
    ready = _exactly_one_v02(
        tuple(
            item
            for item in env["queue_log"]
            if item.queue_entry_id == slot.predecessor_queue_entry_id
        ),
        label="g2d5_budget_exhaustion_ready",
    )
    initial = _exactly_one_v02(
        tuple(
            item
            for item in env["queue_log"]
            if type(ready) is fr.FractalCellQueueEntryV02
            and item.queue_entry_id == ready.predecessor_queue_entry_id
        ),
        label="g2d5_budget_exhaustion_initial",
    )
    if (
        type(ready) is not fr.FractalCellQueueEntryV02
        or type(initial) is not fr.FractalCellQueueEntryV02
    ):
        raise TypeError("g2d5_budget_exhaustion_slot_chain_invalid")
    evidence = (
        source.route_eligibility_artifact.artifact_id,
        env["topology_artifact"].artifact_id,
        root_input.cell_input_id,
        _witness_artifact_for_queue_v02(env, initial.queue_entry_id).artifact_id,
        _witness_artifact_for_queue_v02(env, ready.queue_entry_id).artifact_id,
        slot_artifact.artifact_id,
        exhausted.budget_id,
        _witness_artifact_for_queue_v02(env, dependency.queue_entry_id).artifact_id,
    )
    reasons = ("g2d_required_child_failure",)
    t06 = _witness_eval_v02(
        env,
        source_artifact=slot_artifact,
        node=nodes[1],
        current_entry=slot,
        cell_input=root_input,
        cell_budget=budgets[slot.cell_budget_id],
        global_budget=budgets[slot.global_budget_id],
        dependencies=(dependency,),
        queue_reason_codes=reasons,
        observed_evidence_refs=evidence,
    )
    if type(t06) is not transition_registry.TransitionDecisionV01:
        raise ValueError("g2d5_budget_exhaustion_t06_missing")
    finish = _witness_budget_successor_v02(
        env,
        exhausted,
        event="FINISH_NODE",
        decision=t06,
        cell_input=root_input,
    )
    validating, _validating_artifact, _ = _witness_advance_v02(
        env,
        current=slot,
        node=nodes[1],
        cell_input=root_input,
        cell_budget_before=budgets[slot.cell_budget_id],
        global_budget_before=budgets[slot.global_budget_id],
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=(dependency,),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=reasons,
        observed_evidence_refs=evidence,
    )
    blocked, blocked_artifact, terminal = _witness_advance_v02(
        env,
        current=validating,
        node=nodes[1],
        cell_input=root_input,
        cell_budget_before=finish,
        global_budget_before=finish,
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=(dependency,),
        round_entries=_witness_latest_queue_v02(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_evidence_refs=validating.observed_evidence_refs,
    )
    blocked_validation = fr.validate_fractal_cell_queue_entry_v02(blocked)
    budget_after_ids = tuple(item.budget_id for item in env["budget_log"])
    queue_after_ids = tuple(item.queue_entry_id for item in env["queue_log"])
    _require_v02(
        blocked.state == "BLOCKED"
        and blocked.queue_reason_codes == reasons
        and terminal.rule_id == "g2d_t10_validating_to_blocked"
        and blocked_validation.status == "PASS"
        and abi.validate_kernel_artifact_v01(blocked_artifact) == ()
        and queue_after_ids[: len(queue_before_ids)] == queue_before_ids
        and set(queue_before_ids).issubset(queue_after_ids),
        "g2d5_budget_exhaustion_blocked_invalid",
    )
    return _BudgetExhaustionWitnessV02(
        tree_shape=(1, 4, 16),
        depth_counts=((0, 1), (1, 4), (2, 16)),
        accepted_cell_ids=tree.accepted_cell_ids,
        budget_before=budget_before,
        exhausted_budget=exhausted,
        exhausted_validation=exhausted_validation,
        t06_decision=t06,
        blocked_entry=blocked,
        blocked_artifact=blocked_artifact,
        blocked_validation=blocked_validation,
        terminal_decision=terminal,
        budget_before_ids=budget_before_ids,
        budget_after_ids=budget_after_ids,
        queue_before_ids=queue_before_ids,
        queue_after_ids=queue_after_ids,
    )


def _build_shared_boundary_witnesses_v02(
    accepted: tuple[_AcceptedRunV02, ...],
) -> tuple[
    _BackpressureWitnessV02,
    _GateBoundaryWitnessV02,
    _InvokedChildFailureWitnessV02,
    _InvokedChildFailureWitnessV02,
    _DepthBoundaryWitnessV02,
    _CellBoundaryWitnessV02,
    _BudgetExhaustionWitnessV02,
]:
    run = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_fractal",
    )
    cell_boundary = _build_cell_boundary_witness_v02(run)
    return (
        _build_backpressure_witness_v02(run),
        _build_gate_boundary_witness_v02(run),
        _build_invoked_child_failure_witness_v02(
            run,
            outcome="DEGRADED",
            reason_code="g2d_partial_failure_recorded",
        ),
        _build_invoked_child_failure_witness_v02(
            run,
            outcome="BLOCKED",
            reason_code="g2d_required_child_failure",
        ),
        _build_depth_boundary_witness_v02(run),
        cell_boundary,
        _build_budget_exhaustion_witness_v02(run, cell_boundary),
    )


def _bounded_negative_case_result_v02(
    *,
    case_number: int,
    spec: _CaseSpecV02,
    accepted: tuple[_AcceptedRunV02, ...],
    shared: dict[str, object],
) -> FractalRuntimeG2DCaseResultV02:
    run = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_fractal",
    )
    bundle = run.bundle
    policy = run.source_context.runtime_policy
    _require_pass_v02(
        fr.validate_fractal_runtime_policy_v02(policy),
        label="d5_negative_policy_basis",
    )
    root_input = _exactly_one_v02(
        tuple(item for item in bundle.cell_inputs if item.parent_cell_id is None),
        label="g2d5_bounded_root_input",
    )
    child_inputs = tuple(
        item for item in bundle.cell_inputs if item.parent_cell_id is not None
    )
    _require_v02(len(child_inputs) == 2, "g2d5_bounded_child_input_count")
    child_input = child_inputs[0]
    active_budgets = tuple(
        item for item in bundle.budgets if item.budget_state != "FINAL"
    )
    _require_v02(bool(active_budgets), "g2d5_bounded_budget_basis_missing")
    budget_basis = active_budgets[-1]
    if (
        type(root_input) is not fr.FractalCellInputV02
        or type(child_input) is not fr.FractalCellInputV02
    ):
        raise TypeError("g2d5_bounded_input_type_invalid")
    proof: dict[str, object] = {
        "case_number": case_number,
        "policy_id": policy.policy_id,
        "accepted_bundle_validation_id": run.external_report.validation_report_id,
    }
    refs: tuple[str, ...] = (
        policy.policy_id,
        bundle.topology.topology_id,
        bundle.runtime_report.report_id,
        run.external_report.validation_report_id,
    )

    if case_number == 28:
        witness = shared["depth_boundary_witness"]
        if type(witness) is not _DepthBoundaryWitnessV02:
            raise TypeError("g2d5_depth_boundary_witness_invalid")
        accepted_rows = tuple(
            {
                "depth": cell_input.cell_depth,
                "cell_input_id": cell_input.cell_input_id,
                "cell_id": cell_input.cell_id,
                "parent_cell_id": cell_input.parent_cell_id,
                "validation_report_id": report.validation_report_id,
                "validation_target": report.validation_target,
                "status": report.status,
            }
            for cell_input, report in zip(
                witness.accepted_inputs,
                witness.accepted_validations,
                strict=True,
            )
        )
        report = witness.rejected_validation
        observed = _bounded_outcome_from_report_v02(report)
        proof.update(
            accepted_depth_rows=accepted_rows,
            accepted_depths=tuple(item["depth"] for item in accepted_rows),
            rejected_depth=witness.rejected_input.cell_depth,
            rejected_parent_cell_id=witness.rejected_input.parent_cell_id,
            rejected_input_id=witness.rejected_input.cell_input_id,
            rejected_validation_report_id=report.validation_report_id,
            rejected_validation_target=report.validation_target,
            rejected_reason_codes=report.reason_codes,
            rejected_runtime_object_delta=_created_set_delta_v02(
                witness.runtime_objects_before,
                witness.runtime_objects_after,
            ),
        )
        refs = (
            *refs,
            *(item.cell_input_id for item in witness.accepted_inputs),
            *(item.validation_report_id for item in witness.accepted_validations),
            witness.rejected_input.cell_input_id,
            report.validation_report_id,
        )
    elif case_number == 29:
        attempted_count = policy.max_fan_out + 1
        changes = {
            "requested_child_count": attempted_count,
            "ordered_planned_child_cell_ids": tuple(
                f"frchildcell_v02:{index:064x}" for index in range(attempted_count)
            ),
        }
        provisional = replace(root_input, **changes)
        mutated = _reidentified_v02(
            provisional,
            identity_field="cell_input_id",
            rebuild=fr.rebuild_fractal_cell_input_identity_v02,
        )
        report = fr.validate_fractal_cell_input_v02(mutated)
        observed = _bounded_outcome_from_report_v02(report)
        proof.update(
            attempted_value=attempted_count,
            accepted_value=policy.max_fan_out,
            baseline_input_id=root_input.cell_input_id,
            mutated_input_id=mutated.cell_input_id,
            validation_report_id=report.validation_report_id,
            validation_target=report.validation_target,
            reason_codes=report.reason_codes,
            created_objects=_created_set_delta_v02(
                tuple(item.cell_input_id for item in bundle.cell_inputs),
                tuple(item.cell_input_id for item in bundle.cell_inputs),
            ),
        )
        refs = (*refs, report.validation_report_id)
    elif case_number == 30:
        witness = shared["cell_boundary_witness"]
        if type(witness) is not _CellBoundaryWitnessV02:
            raise TypeError("g2d5_cell_boundary_witness_invalid")
        proof.update(
            max_total_cells=policy.max_total_cells,
            tree_shape=witness.tree_shape,
            depth_counts=dict(witness.depth_counts),
            cell_rows=witness.cell_rows,
            parent_child_rows=witness.parent_child_rows,
            root_cell_id=witness.root_cell_id,
            depth_1_cell_ids=witness.depth_1_cell_ids,
            depth_2_cell_ids=witness.depth_2_cell_ids,
            root_budget_event_rows=witness.root_budget_event_rows,
            accepted_cell_rows=witness.accepted_cell_rows,
            accepted_cell_ids=witness.accepted_cell_ids,
            accepted_cell_count=len(witness.accepted_cell_ids),
            planning_debit_count=0,
            allocation_debit_count=sum(
                item["child_allocation_consumed_cell_count"]
                for item in witness.accepted_cell_rows
            ),
            activate_debit_count=sum(
                item["global_activate_consumed_cell_count"]
                - item["global_before_consumed_cell_count"]
                for item in witness.accepted_cell_rows
            ),
            cell_create_debit_count=1 + sum(
                item["global_create_consumed_cell_count"]
                - item["global_activate_consumed_cell_count"]
                for item in witness.accepted_cell_rows
            ),
            root_create_budget_id=witness.root_budget_event_rows[-1][1],
            twenty_first_global_budget_id=witness.final_global_budget.budget_id,
            twenty_first_validation_report_id=(
                witness.final_global_validation.validation_report_id
            ),
            twenty_first_consumed_cell_count=(
                witness.final_global_budget.consumed_cell_count
            ),
            twenty_first_remaining_cell_count=(
                witness.final_global_budget.remaining_cell_count
            ),
            attempted_twenty_second_cell_id=witness.attempted_cell_id,
            attempted_twenty_second_parent_id=witness.attempted_parent_id,
            attempted_twenty_second_error=witness.attempted_error,
            attempted_twenty_second_global_budget_created=(
                witness.attempted_global_budget is not None
            ),
            rejected_budget_id=witness.rejected_budget.budget_id,
            rejected_validation_report_id=(
                witness.rejected_validation.validation_report_id
            ),
            rejected_validation_target=witness.rejected_validation.validation_target,
            rejected_reason_codes=witness.rejected_validation.reason_codes,
            rejected_runtime_object_delta=_created_set_delta_v02(
                witness.runtime_objects_before,
                witness.runtime_objects_after,
            ),
        )
        observed = _bounded_outcome_from_report_v02(witness.rejected_validation)
        row_refs = tuple(
            str(item[key])
            for item in witness.accepted_cell_rows
            for key in (
                "cell_id",
                "parent_cell_id",
                "planning_input_id",
                "planning_validation_id",
                "child_allocation_budget_id",
                "child_allocation_validation_id",
                "child_activate_budget_id",
                "child_activate_validation_id",
                "global_activate_budget_id",
                "global_activate_validation_id",
                "child_create_budget_id",
                "child_create_validation_id",
                "global_create_budget_id",
                "global_create_validation_id",
                "scope_projection_id",
                "scope_validation_id",
                "cell_input_id",
                "cell_input_validation_id",
            )
        )
        refs = (
            *refs,
            *(str(row[1]) for row in witness.root_budget_event_rows),
            *(str(row[4]) for row in witness.root_budget_event_rows),
            *witness.accepted_cell_ids,
            *(
                str(item[key])
                for item in witness.cell_rows
                for key in (
                    "cell_input_id",
                    "cell_input_validation_report_id",
                    "cell_create_budget_id",
                )
            ),
            *row_refs,
            witness.attempted_cell_id,
            witness.rejected_budget.budget_id,
            witness.rejected_validation.validation_report_id,
        )
    elif case_number in {32, 33, 34}:
        if case_number == 32:
            changes = {
                "consumed_token_budget": budget_basis.max_token_budget + 1,
                "remaining_token_budget": -1,
            }
            attempted_value = budget_basis.max_token_budget + 1
        elif case_number == 33:
            changes = {
                "consumed_wall_time_units": budget_basis.max_wall_time_units + 1,
                "remaining_wall_time_units": -1,
            }
            attempted_value = budget_basis.max_wall_time_units + 1
        else:
            changes = {
                "consumed_provider_calls": budget_basis.max_provider_calls + 1,
                "remaining_provider_calls": -1,
            }
            attempted_value = budget_basis.max_provider_calls + 1
        mutated, report = _mutated_budget_report_v02(budget_basis, **changes)
        observed = _bounded_outcome_from_report_v02(report)
        proof.update(
            attempted_value=attempted_value,
            baseline_budget_id=budget_basis.budget_id,
            mutated_budget_id=mutated.budget_id,
            mutated_counter_fields=tuple(changes),
            validation_report_id=report.validation_report_id,
            validation_target=report.validation_target,
            reason_codes=report.reason_codes,
            created_objects=_created_set_delta_v02(
                tuple(item.budget_id for item in bundle.budgets),
                tuple(item.budget_id for item in bundle.budgets),
            ),
        )
        refs = (*refs, report.validation_report_id)
    elif case_number == 31:
        witness = shared["backpressure_witness"]
        if type(witness) is not _BackpressureWitnessV02:
            raise TypeError("g2d5_backpressure_witness_invalid")
        state = witness.s0
        state_report = witness.s0_validation
        successor = witness.first_deferred
        observed = successor.state
        proof.update(
            backpressure_id=state.backpressure_id,
            validation_report_id=state_report.validation_report_id,
            source_context_id=witness.source_context.router_input.router_input_id,
            topology_id=witness.topology.topology_id,
            topology_artifact_id=witness.topology_artifact_id,
            queue_capacity=state.queue_capacity,
            running_count=state.running_count,
            ready_count=state.ready_count,
            pending_count=state.pending_count,
            admission_order=state.admission_order,
            deferred_source_queue_id=witness.deferred_source.queue_entry_id,
            deferred_queue_entry_ids=state.deferred_queue_entry_ids,
            t03_decision_id=witness.first_t03_decision.decision_id,
            deferred_successor_queue_id=successor.queue_entry_id,
            deferred_successor_artifact_id=witness.first_deferred_artifact.artifact_id,
            predecessor_queue_id=successor.predecessor_queue_entry_id,
            admission_round=successor.admission_round,
            deferred_state=successor.state,
            queue_reason_codes=successor.queue_reason_codes,
            no_work_dropped=state.no_work_dropped,
            created_objects=_created_set_delta_v02(
                (witness.deferred_source.queue_entry_id,),
                (
                    witness.deferred_source.queue_entry_id,
                    successor.queue_entry_id,
                    witness.first_deferred_artifact.artifact_id,
                ),
            ),
        )
        refs = (
            *refs,
            witness.source_context.router_input.router_input_id,
            witness.topology_artifact_id,
            state.backpressure_id,
            state_report.validation_report_id,
            witness.first_t03_decision.decision_id,
            successor.queue_entry_id,
            witness.first_deferred_artifact.artifact_id,
        )
    elif case_number == 35:
        projection = bundle.scope_projections[0]
        budget_by_id = {item.budget_id: item for item in bundle.budgets}
        budget = _exactly_one_v02(
            tuple(
                item
                for item in bundle.budgets
                if item.budget_id == projection.child_budget_id
            ),
            label="g2d5_scope_budget",
        )
        if type(budget) is not fr.FractalRuntimeBudgetV02:
            raise TypeError("g2d5_scope_budget_type_invalid")
        parent_input = _exactly_one_v02(
            tuple(
                item
                for item in bundle.cell_inputs
                if item.cell_id == projection.parent_cell_id
            ),
            label="g2d5_scope_parent_input",
        )
        if type(parent_input) is not fr.FractalCellInputV02:
            raise TypeError("g2d5_scope_parent_input_type_invalid")
        parent_budget = budget_by_id[projection.parent_budget_id]
        global_budget = budget_by_id[projection.global_budget_id]
        baseline_context_report = fr.validate_parent_child_scope_against_sources_v02(
            projection,
            source_context=run.source_context,
            topology=bundle.topology,
            parent_input=parent_input,
            parent_budget=parent_budget,
            child_budget=budget,
            global_budget=global_budget,
        )
        _require_pass_v02(
            baseline_context_report,
            label="g2d5_scope_context_basis",
        )
        scope_mutations = (
            ("child_scope_ref", {"child_scope_ref": projection.child_scope_ref + ":widened"}),
            ("child_allowed_capability_ids", {"child_allowed_capability_ids": (*projection.child_allowed_capability_ids, "capability:g2d5:foreign")}),
            ("child_forbidden_claims", {"child_forbidden_claims": ()}),
            ("child_ttl_units", {"child_ttl_units": projection.parent_ttl_units + 1}),
            ("parent_scope_ref", {"parent_scope_ref": projection.parent_scope_ref + ":foreign"}),
            ("parent_budget_id", {"parent_budget_id": "frbudget_v02:" + "0" * 64}),
        )
        matrix_rows: list[tuple[object, ...]] = []
        matrix_reports: list[fr.FractalRuntimeValidationReportV02] = []
        report_ids: list[str] = []
        for axis, changes in scope_mutations:
            provisional = replace(projection, **changes)
            mutated = _reidentified_v02(
                provisional,
                identity_field="projection_id",
                rebuild=fr.rebuild_parent_child_scope_projection_identity_v02,
            )
            report = fr.validate_parent_child_scope_against_sources_v02(
                mutated,
                source_context=run.source_context,
                topology=bundle.topology,
                parent_input=parent_input,
                parent_budget=parent_budget,
                child_budget=budget,
                global_budget=global_budget,
            )
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_scope_mutation_passed")
            matrix_rows.append((axis, report.validation_report_id, report.reason_codes))
            matrix_reports.append(report)
            report_ids.append(report.validation_report_id)
        budget_mutations = (
            ("budget_owner", {"owning_cell_id": bundle.topology.root_cell_id}),
            ("budget_predecessor", {"predecessor_budget_id": "frbudget_v02:" + "0" * 64}),
            ("budget_event", {"budget_event_kind": "REVISE"}),
            ("budget_state", {"budget_state": "FINAL"}),
            ("budget_borrowing", {"remaining_token_budget": budget.remaining_token_budget + 1}),
            ("budget_allocation_parent", {"allocation_parent_budget_id": None}),
        )
        budget_position = bundle.budgets.index(budget)
        for axis, changes in budget_mutations:
            mutated, _structural_report = _mutated_budget_report_v02(
                budget,
                **changes,
            )
            report = fr.validate_fractal_runtime_execution_bundle_v02(
                replace(
                    bundle,
                    budgets=(
                        *bundle.budgets[:budget_position],
                        mutated,
                        *bundle.budgets[budget_position + 1:],
                    ),
                )
            )
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_budget_mutation_passed")
            matrix_rows.append((axis, report.validation_report_id, report.reason_codes))
            matrix_reports.append(report)
            report_ids.append(report.validation_report_id)
        observed = matrix_reports[0].status
        proof.update(
            mutation_rows=tuple(matrix_rows),
            mutation_count=len(matrix_rows),
            baseline_projection_id=projection.projection_id,
            baseline_budget_id=budget.budget_id,
            baseline_context_validation_id=(
                baseline_context_report.validation_report_id
            ),
            created_objects=_created_set_delta_v02(
                tuple(item.projection_id for item in bundle.scope_projections),
                tuple(item.projection_id for item in bundle.scope_projections),
            ),
        )
        refs = (
            *refs,
            baseline_context_report.validation_report_id,
            *report_ids,
        )
    elif case_number in {36, 37, 38}:
        cell_input, queue, cell_budget, global_budget = _validating_context_v02(bundle)
        reason_codes = ("g2d_resolvable_input_needs_user",) if case_number == 38 else ()
        revision_index = min(cell_budget.max_revise_count, queue.snapshot_sequence)
        if case_number == 36:
            revision_index = cell_budget.max_revise_count + 1
            queue = _reidentified_v02(
                replace(
                    queue,
                    snapshot_sequence=max(queue.snapshot_sequence, revision_index),
                ),
                identity_field="queue_entry_id",
                rebuild=fr.rebuild_fractal_cell_queue_entry_identity_v02,
            )
            if type(queue) is not fr.FractalCellQueueEntryV02:
                raise TypeError("g2d5_revise_queue_type_invalid")
        queue_report = fr.validate_fractal_cell_queue_entry_v02(queue)
        _require_pass_v02(queue_report, label="g2d5_revise_queue")
        validation = fr.build_fractal_runtime_validation_report_v02(
            validation_target="CELL_RESULT_PRECONDITIONS",
            validated_object_id=(None if reason_codes else queue.queue_entry_id),
            failure_stage=(
                "CELL_RESULT_PRECONDITIONS" if reason_codes else "NONE"
            ),
            reason_codes=reason_codes,
            source_reason_codes=(),
        )
        consecutive = cell_budget.max_revise_count if case_number == 37 else 0
        observation = fr.evaluate_fractal_revise_observation_v02(
            topology=bundle.topology,
            cell_input=cell_input,
            queue_entry=queue,
            validation_report=validation,
            cell_budget_before=cell_budget,
            global_budget_before=global_budget,
            revision_index=revision_index,
            newly_validated_evidence_count=0,
            newly_resolved_constraints_count=0,
            newly_accepted_outputs_count=0,
            newly_introduced_conflicts_count=0,
            consecutive_non_positive_count=consecutive,
        )
        observation_report = fr.validate_fractal_revise_observation_v02(observation)
        _require_pass_v02(observation_report, label="g2d5_revise_observation")
        observed = observation.derived_terminal_state
        if type(observed) is not str:
            raise ValueError("g2d5_revise_terminal_missing")
        proof.update(
            queue_entry_id=queue.queue_entry_id,
            queue_validation_report_id=queue_report.validation_report_id,
            source_validation_report_id=validation.validation_report_id,
            observation_id=observation.observation_id,
            observation_validation_report_id=observation_report.validation_report_id,
            revision_index=observation.revision_index,
            max_revise_count=cell_budget.max_revise_count,
            consecutive_non_positive_count=observation.consecutive_non_positive_count,
            derived_terminal_state=observation.derived_terminal_state,
            reason_codes=observation.reason_codes,
        )
        refs = (
            *refs,
            queue_report.validation_report_id,
            validation.validation_report_id,
            observation.observation_id,
            observation_report.validation_report_id,
        )
    elif case_number in {39, 40}:
        witness_name = (
            "degraded_child_witness"
            if case_number == 39
            else "blocked_child_witness"
        )
        child_witness = shared[witness_name]
        if type(child_witness) is not _InvokedChildFailureWitnessV02:
            raise TypeError("g2d5_child_failure_witness_invalid")
        child_structural_report = fr.validate_fractal_cell_result_v02(
            child_witness.result
        )
        _require_pass_v02(
            child_structural_report,
            label="g2d5_child_failure_structural",
        )
        observed = child_witness.partial_failure.parent_disposition
        proof.update(
            child_cell_id=child_witness.child_input.cell_id,
            child_input_id=child_witness.child_input.cell_input_id,
            baseline_child_result_id=child_witness.baseline_result.result_id,
            attempted_child_result_id=child_witness.result.result_id,
            attempted_outcome=child_witness.result.outcome,
            terminal_queue_rows=tuple(
                (
                    item.queue_entry_id,
                    item.state,
                    item.queue_reason_codes,
                )
                for item in child_witness.terminal_entries
            ),
            result_proposal_id=child_witness.result_proposal_id,
            post_vv_report_id=child_witness.post_vv_report_id,
            gt_report_id=child_witness.gt_report_id,
            proposal_validation_report_id=(
                child_witness.proposal_validation.validation_report_id
            ),
            post_vv_validation_report_id=(
                child_witness.post_vv_validation.validation_report_id
            ),
            gt_validation_report_id=child_witness.gt_validation.validation_report_id,
            child_validation_report_id=(
                child_witness.result_validation.validation_report_id
            ),
            child_structural_validation_report_id=(
                child_structural_report.validation_report_id
            ),
            result_artifact_id=child_witness.result_artifact.artifact_id,
            activation_causal_row=child_witness.activation_causal_row,
            child_reason_codes=child_witness.result.reason_codes,
            partial_failure_id=child_witness.partial_failure.partial_failure_id,
            partial_failure_validation_report_id=(
                child_witness.partial_validation.validation_report_id
            ),
            parent_disposition=child_witness.partial_failure.parent_disposition,
            required_child=child_witness.partial_failure.required_child,
            created_result_delta=_created_set_delta_v02(
                child_witness.result_before_ids,
                child_witness.result_after_ids,
            ),
            created_partial_failure_delta=_created_set_delta_v02(
                child_witness.partial_before_ids,
                child_witness.partial_after_ids,
            ),
            created_causal_delta=_created_set_delta_v02(
                child_witness.causal_before_ids,
                child_witness.causal_after_ids,
            ),
        )
        refs = (
            *refs,
            child_witness.child_input.cell_input_id,
            child_witness.result_proposal_id,
            child_witness.post_vv_report_id,
            child_witness.gt_report_id,
            child_witness.proposal_validation.validation_report_id,
            child_witness.post_vv_validation.validation_report_id,
            child_witness.gt_validation.validation_report_id,
            child_witness.result_validation.validation_report_id,
            child_structural_report.validation_report_id,
            child_witness.result.result_id,
            child_witness.result_artifact.artifact_id,
            child_witness.partial_failure.partial_failure_id,
            child_witness.partial_validation.validation_report_id,
            child_witness.activation_causal_row[1],
            child_witness.activation_causal_row[4],
        )
        if case_number == 39:
            safe = child_witness.safe_sibling_result
            proof.update(
                safe_sibling_input_id=(
                    child_witness.safe_sibling_input.cell_input_id
                ),
                safe_sibling_result_id=safe.result_id,
                safe_sibling_result_artifact_id=(
                    child_witness.safe_sibling_result_artifact.artifact_id
                ),
                safe_sibling_outcome=safe.outcome,
                safe_sibling_evidence_refs=safe.evidence_refs,
                safe_sibling_report_refs=(
                    safe.pre_result_validation_report_id,
                    safe.post_vv_report_ref,
                    safe.gt_advisory_ref,
                ),
                safe_sibling_structural_validation_id=(
                    child_witness.safe_sibling_structural_validation.validation_report_id
                ),
                safe_sibling_context_validation_id=(
                    child_witness.safe_sibling_context_validation.validation_report_id
                ),
                safe_sibling_before_sha256=(
                    child_witness.safe_sibling_before_sha256
                ),
                safe_sibling_after_sha256=(
                    child_witness.safe_sibling_after_sha256
                ),
                safe_sibling_unchanged=(
                    child_witness.safe_sibling_before_sha256
                    == child_witness.safe_sibling_after_sha256
                ),
                safe_sibling_result_delta=_created_set_delta_v02(
                    child_witness.safe_sibling_result_before_ids,
                    child_witness.safe_sibling_result_after_ids,
                ),
                safe_sibling_causal_delta=_created_set_delta_v02(
                    child_witness.safe_sibling_causal_before_ids,
                    child_witness.safe_sibling_causal_after_ids,
                ),
                partial_failure_sibling_independent=(
                    child_witness.partial_failure.sibling_independent
                ),
            )
            refs = (
                *refs,
                child_witness.safe_sibling_input.cell_input_id,
                safe.result_id,
                child_witness.safe_sibling_result_artifact.artifact_id,
                *safe.evidence_refs,
                safe.pre_result_validation_report_id,
                safe.post_vv_report_ref,
                safe.gt_advisory_ref,
                child_witness.safe_sibling_structural_validation.validation_report_id,
                child_witness.safe_sibling_context_validation.validation_report_id,
            )
        else:
            witness = shared["gate_witness"]
            if type(witness) is not _GateBoundaryWitnessV02:
                raise TypeError("g2d5_gate_witness_invalid")
            _require_v02(
                observed == witness.blocked_entry.state == "BLOCKED",
                "g2d5_case40_branch_outcome_mismatch",
            )
            proof.update(
                gate_disposition=witness.gate_disposition,
                gate_reason_codes=witness.gate_reason_codes,
                gate_evidence_refs=witness.gate_evidence_refs,
                t06_decision_id=witness.t06_decision.decision_id,
                validating_queue_id=witness.validating_entry.queue_entry_id,
                validating_artifact_id=witness.validating_artifact.artifact_id,
                terminal_decision_id=witness.terminal_decision.decision_id,
                blocked_queue_id=witness.blocked_entry.queue_entry_id,
                blocked_artifact_id=witness.blocked_artifact.artifact_id,
                blocked_validation_id=witness.blocked_validation.validation_report_id,
                no_child_invocation_delta=_created_set_delta_v02(
                    witness.invocation_before_ids,
                    witness.invocation_after_ids,
                ),
                no_child_result_delta=_created_set_delta_v02(
                    witness.result_before_ids,
                    witness.result_after_ids,
                ),
                no_child_partial_failure_delta=_created_set_delta_v02(
                    witness.partial_before_ids,
                    witness.partial_after_ids,
                ),
                no_child_terminal_delta=_created_set_delta_v02(
                    witness.denial_terminal_before_ids,
                    witness.denial_terminal_after_ids,
                ),
                merge_queue_id=witness.merge_entry.queue_entry_id,
                merge_validation_id=witness.merge_validation.validation_report_id,
                merge_decision_is_none=witness.merge_decision_is_none,
                malformed_axis=witness.malformed_axis,
                malformed_queue_id=witness.malformed_entry.queue_entry_id,
                malformed_validation_id=witness.malformed_validation.validation_report_id,
                malformed_reason_codes=witness.malformed_validation.reason_codes,
                malformed_error=witness.malformed_error,
                malformed_terminal_delta=_created_set_delta_v02(
                    witness.malformed_terminal_before_ids,
                    witness.malformed_terminal_after_ids,
                ),
                malformed_causal_delta=_created_set_delta_v02(
                    witness.malformed_causal_before_ids,
                    witness.malformed_causal_after_ids,
                ),
                malformed_bundle_delta=_created_set_delta_v02(
                    witness.malformed_bundle_before_ids,
                    witness.malformed_bundle_after_ids,
                ),
            )
            refs = (
                *refs,
                *witness.gate_evidence_refs,
                witness.t06_decision.decision_id,
                witness.validating_entry.queue_entry_id,
                witness.validating_artifact.artifact_id,
                witness.terminal_decision.decision_id,
                witness.blocked_entry.queue_entry_id,
                witness.blocked_artifact.artifact_id,
                witness.blocked_validation.validation_report_id,
                witness.merge_entry.queue_entry_id,
                witness.merge_validation.validation_report_id,
                witness.malformed_validation.validation_report_id,
            )
    elif case_number == 41:
        child_results = tuple(
            item for item in bundle.cell_results if item.parent_cell_id is not None
        )
        _require_v02(len(child_results) == 2, "g2d5_authority_child_count")
        child = child_results[0]
        mutations = (
            ("authority_created", {"authority_created": True}),
            ("permission_created", {"permission_created": True}),
            ("action_commit_packet_created", {"action_commit_packet_created": True}),
            ("receipt_created", {"receipt_created": True}),
            ("final_output_created", {"final_output_created": True}),
            ("real_world_effects_count", {"real_world_effects_count": 1}),
        )
        matrix_rows: list[tuple[object, ...]] = []
        report_ids: list[str] = []
        for axis, changes in mutations:
            provisional = replace(child, **changes)
            mutated = _reidentified_v02(
                provisional,
                identity_field="result_id",
                rebuild=fr.rebuild_fractal_cell_result_identity_v02,
            )
            report = fr.validate_fractal_cell_result_v02(mutated)
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_child_authority_claim_accepted")
            matrix_rows.append((axis, report.validation_report_id, report.reason_codes))
            report_ids.append(report.validation_report_id)
        observed = fr.validate_fractal_cell_result_v02(
            _reidentified_v02(
                replace(child, authority_created=True),
                identity_field="result_id",
                rebuild=fr.rebuild_fractal_cell_result_identity_v02,
            )
        ).status
        proof.update(
            mutation_rows=tuple(matrix_rows),
            mutation_count=len(matrix_rows),
            baseline_child_result_id=child.result_id,
            no_created_objects=_created_set_delta_v02(
                tuple(item.result_id for item in bundle.cell_results),
                tuple(item.result_id for item in bundle.cell_results),
            ),
        )
        refs = (*refs, *report_ids)
    else:
        raise ValueError(f"g2d5_bounded_axis_unmapped:{case_number}")

    return _case_result_v02(
        spec=spec,
        observed_outcome=observed,
        evidence_refs=refs,
        proof=proof,
    )


def _pointer_leaf_v02(payload: object, pointer: str) -> object:
    current = payload
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if type(current) is dict:
            current = current[token]
        elif type(current) is list:
            current = current[int(token)]
        else:
            raise ValueError("g2d5_counterfactual_pointer_invalid")
    return current


def _counterfactual_replacement_v02(value: object) -> object:
    if type(value) is str:
        return value + ":counterfactual"
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if value is None:
        return "counterfactual:none"
    raise ValueError("g2d5_counterfactual_leaf_unsupported")


def _mutated_kernel_payload_artifact_v02(
    artifact: abi.KernelArtifactV01,
    *,
    pointer: str,
    replacement: object,
) -> abi.KernelArtifactV01:
    plain = abi.kernel_artifact_to_plain_dict_v01(artifact)
    payload = plain["payload"]
    if type(payload) is not dict:
        raise ValueError("g2d5_counterfactual_payload_invalid")
    tokens = pointer.lstrip("/").split("/")
    cursor: object = payload
    for raw in tokens[:-1]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if type(cursor) is dict:
            cursor = cursor[token]
        elif type(cursor) is list:
            cursor = cursor[int(token)]
        else:
            raise ValueError("g2d5_counterfactual_pointer_invalid")
    leaf = tokens[-1].replace("~1", "/").replace("~0", "~")
    if type(cursor) is dict:
        cursor[leaf] = replacement
    elif type(cursor) is list:
        cursor[int(leaf)] = replacement
    else:
        raise ValueError("g2d5_counterfactual_pointer_invalid")
    provisional = abi.build_kernel_artifact_v01(
        abi_version=artifact.abi_version,
        artifact_id="counterfactual:" + "0" * 64,
        artifact_type=artifact.artifact_type,
        schema_version=artifact.schema_version,
        transaction_id=artifact.transaction_id,
        owner_root_id=artifact.owner_root_id,
        source_component=artifact.source_component,
        authority_class=artifact.authority_class,
        lifecycle_state=artifact.lifecycle_state,
        payload=payload,
        trace_refs=artifact.trace_refs,
        parent_refs=artifact.parent_refs,
        time_envelope=plain["time_envelope"],
    )
    identity_material = abi.kernel_artifact_to_plain_dict_v01(provisional)
    identity_material.pop("artifact_id")
    identity_profiles = {
        "FractalCellQueueEntry": (
            "frabi_queue_v02:",
            "HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02",
        ),
        "FractalCellResult": (
            "frabi_result_v02:",
            "HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
        ),
    }
    prefix, domain = identity_profiles[artifact.artifact_type]
    mutated = replace(
        provisional,
        artifact_id=prefix
        + domain_separated_sha256_hex_v01(
            domain=domain,
            payload=canonical_json_bytes_v01(identity_material),
        ),
    )
    _require_v02(
        abi.validate_kernel_artifact_v01(mutated) == (),
        "g2d5_counterfactual_artifact_invalid",
    )
    return mutated


def _actual_counterfactual_v02(
    *,
    run: _AcceptedRunV02,
    disposition: str,
) -> tuple[fr.FractalRuntimeValidationReportV02, object, abi.KernelArtifactV01]:
    artifact_by_id = {item.artifact_id: item for item in run.bundle.queue_artifacts}
    rows = tuple(
        item
        for item in run.bundle.causal_consumption_refs
        if item.disposition == disposition
        and item.source_artifact_id in artifact_by_id
    )
    _require_v02(bool(rows), "g2d5_counterfactual_ref_missing")
    causal_ref = rows[0]
    source_artifact = artifact_by_id[causal_ref.source_artifact_id]
    payload = abi.kernel_artifact_to_plain_dict_v01(source_artifact)["payload"]
    original = _pointer_leaf_v02(payload, causal_ref.output_field)
    mutated = _mutated_kernel_payload_artifact_v02(
        source_artifact,
        pointer=causal_ref.output_field,
        replacement=_counterfactual_replacement_v02(original),
    )
    report = fr.validate_fractal_runtime_causal_counterfactual_v02(
        execution_bundle=run.bundle,
        causal_ref=causal_ref,
        mutated_source_artifact=mutated,
    )
    _require_pass_v02(report, label="d5_actual_counterfactual")
    return report, causal_ref, mutated


def _blocked_gate_causal_proof_v02(
    *,
    run: _AcceptedRunV02,
    gate: _GateBoundaryWitnessV02,
) -> _BlockedGateCausalProofV02:
    node_by_id = {item.node_id: item for item in run.bundle.topology_nodes}
    queue_rows = tuple(zip(
        run.bundle.queue_entries,
        run.bundle.queue_artifacts,
        strict=True,
    ))
    source_entry, source_artifact = _exactly_one_v02(
        tuple(
            row
            for row in queue_rows
            if row[0].state == "VALIDATING"
            and node_by_id[row[0].node_id].node_kind == "FRACTAL_CELL"
            and bool(row[0].observed_output_refs)
        )[:1],
        label="g2d5_blocked_gate_validating_source",
    )
    if (
        type(source_entry) is not fr.FractalCellQueueEntryV02
        or type(source_artifact) is not abi.KernelArtifactV01
    ):
        raise TypeError("g2d5_blocked_gate_source_invalid")
    baseline_terminal, baseline_terminal_artifact = _exactly_one_v02(
        tuple(
            row
            for row in queue_rows
            if row[0].cell_id == source_entry.cell_id
            and row[0].node_id == source_entry.node_id
            and row[0].predecessor_queue_entry_id == source_entry.queue_entry_id
            and row[0].state == "COMPLETED"
        ),
        label="g2d5_blocked_gate_terminal_basis",
    )
    if (
        type(baseline_terminal) is not fr.FractalCellQueueEntryV02
        or type(baseline_terminal_artifact) is not abi.KernelArtifactV01
    ):
        raise TypeError("g2d5_blocked_gate_terminal_basis_invalid")
    downstream_entry = _reidentified_v02(
        replace(
            baseline_terminal,
            state="BLOCKED",
            transition_decision_id=gate.terminal_decision.decision_id,
            queue_reason_codes=("g2d_required_child_failure",),
        ),
        identity_field="queue_entry_id",
        rebuild=fr.rebuild_fractal_cell_queue_entry_identity_v02,
    )
    if type(downstream_entry) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_blocked_gate_downstream_invalid")
    source_validation = fr.validate_fractal_cell_queue_entry_v02(source_entry)
    downstream_validation = fr.validate_fractal_cell_queue_entry_v02(
        downstream_entry
    )
    _require_pass_v02(source_validation, label="g2d5_blocked_gate_source")
    _require_pass_v02(
        downstream_validation,
        label="g2d5_blocked_gate_downstream",
    )
    downstream_artifact = baseline_terminal_artifact
    for pointer, replacement in (
        ("/queue_entry_id", downstream_entry.queue_entry_id),
        ("/state", downstream_entry.state),
        ("/transition_decision_id", downstream_entry.transition_decision_id),
        ("/queue_reason_codes", list(downstream_entry.queue_reason_codes)),
    ):
        downstream_artifact = _mutated_kernel_payload_artifact_v02(
            downstream_artifact,
            pointer=pointer,
            replacement=replacement,
        )
    _require_v02(
        source_artifact.artifact_id in downstream_artifact.parent_refs
        and source_entry.observed_output_refs[0] in downstream_artifact.parent_refs
        and downstream_artifact.source_component == "fractal_scheduler_v02",
        "g2d5_blocked_gate_parent_geometry_invalid",
    )
    assignment = _exactly_one_v02(
        tuple(
            item
            for item in run.bundle.runtime_assignments
            if item.node_id == source_entry.node_id
        ),
        label="g2d5_blocked_gate_assignment",
    )
    if type(assignment) is not fr.RuntimeAssignmentV02:
        raise TypeError("g2d5_blocked_gate_assignment_invalid")
    causal_ref = abi.build_causal_consumption_ref_v01(
        producer_actor_id=assignment.executor_component_id,
        source_artifact_id=source_artifact.artifact_id,
        output_field="/observed_output_refs/0",
        consumer_component="fractal_scheduler_v02",
        downstream_artifact_id=downstream_artifact.artifact_id,
        decision_effect="CELL_RESULT_OUTPUT",
        disposition="BLOCKED_BY_GATE",
        reason_code="gate:g2d_child_output",
        trace_refs=(
            source_artifact.artifact_id,
            downstream_artifact.artifact_id,
            run.bundle.runtime_trace.trace_id,
        ),
    )
    causal_validation = abi.validate_causal_consumption_ref_v01(causal_ref)
    artifact_validation = (
        *abi.validate_kernel_artifact_v01(source_artifact),
        *abi.validate_kernel_artifact_v01(downstream_artifact),
    )
    available_artifacts = (
        run.source_context.proposal_artifact,
        run.source_context.decision_artifact,
        run.source_context.route_eligibility_artifact,
        run.bundle.topology_artifact,
        *run.bundle.queue_artifacts,
        *run.bundle.result_artifacts,
        run.bundle.report_artifact,
        downstream_artifact,
    )
    artifact_by_id = {item.artifact_id: item for item in available_artifacts}
    closure_ids: list[str] = []

    def add_closure(artifact_id: str) -> None:
        if artifact_id in closure_ids:
            return
        artifact = artifact_by_id.get(artifact_id)
        if artifact is None:
            raise ValueError("g2d5_blocked_gate_parent_artifact_missing")
        for parent_id in artifact.parent_refs:
            add_closure(parent_id)
        closure_ids.append(artifact_id)

    add_closure(downstream_artifact.artifact_id)
    closure = tuple(artifact_by_id[item] for item in closure_ids)
    bundle_validation = abi.validate_causal_consumption_bundle_v01(
        artifacts=closure,
        causal_refs=(causal_ref,),
    )
    source_plain = abi.kernel_artifact_to_plain_dict_v01(source_artifact)
    source_payload = source_plain["payload"]
    if type(source_payload) is not dict:
        raise TypeError("g2d5_blocked_gate_payload_invalid")
    mutated_payload = dict(source_payload)
    observed_outputs = list(mutated_payload["observed_output_refs"])
    if not observed_outputs or type(observed_outputs[0]) is not str:
        raise TypeError("g2d5_blocked_gate_output_invalid")
    observed_outputs[0] = observed_outputs[0] + ":counterfactual"
    mutated_payload["observed_output_refs"] = observed_outputs
    counterfactual_source = abi.build_kernel_artifact_v01(
        abi_version=source_artifact.abi_version,
        artifact_id=source_artifact.artifact_id,
        artifact_type=source_artifact.artifact_type,
        schema_version=source_artifact.schema_version,
        transaction_id=source_artifact.transaction_id,
        owner_root_id=source_artifact.owner_root_id,
        source_component=source_artifact.source_component,
        authority_class=source_artifact.authority_class,
        lifecycle_state=source_artifact.lifecycle_state,
        payload=mutated_payload,
        trace_refs=source_artifact.trace_refs,
        parent_refs=source_artifact.parent_refs,
        time_envelope=source_plain["time_envelope"],
    )
    authority_state = {
        "owning_root_id": run.bundle.topology.owning_root_id,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }
    counterfactual_validation = abi.validate_causal_counterfactual_v01(
        causal_ref=causal_ref,
        baseline_source_artifact=source_artifact,
        mutated_source_artifact=counterfactual_source,
        baseline_downstream_artifact=downstream_artifact,
        mutated_downstream_artifact=downstream_artifact,
        baseline_authority_state=authority_state,
        mutated_authority_state=authority_state,
    )
    _require_v02(
        causal_validation == ()
        and artifact_validation == ()
        and bundle_validation == ()
        and counterfactual_validation == (),
        "g2d5_blocked_gate_causal_invalid",
    )
    return _BlockedGateCausalProofV02(
        source_entry=source_entry,
        source_artifact=source_artifact,
        source_validation=source_validation,
        downstream_entry=downstream_entry,
        downstream_artifact=downstream_artifact,
        downstream_validation=downstream_validation,
        output_index=0,
        causal_ref=causal_ref,
        causal_validation_reasons=causal_validation,
        artifact_validation_reasons=artifact_validation,
        bundle_validation_reasons=bundle_validation,
        generic_counterfactual_validation_reasons=counterfactual_validation,
        generic_mutated_source_sha256=_sha256_plain_v02(counterfactual_source),
    )


def _accepted_matrix_case_result_v02(
    *,
    case_number: int,
    spec: _CaseSpecV02,
    accepted: tuple[_AcceptedRunV02, ...],
    shared: dict[str, object],
) -> FractalRuntimeG2DCaseResultV02:
    run = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_fractal",
    )
    bundle = run.bundle
    complete = run.external_report
    _require_pass_v02(complete, label="d5_matrix_bundle")
    refs: tuple[str, ...] = (
        bundle.topology.topology_id,
        bundle.runtime_trace.trace_id,
        bundle.runtime_report.report_id,
        complete.validation_report_id,
    )
    proof: dict[str, object] = {
        "case_number": case_number,
        "complete_profile_validation_id": complete.validation_report_id,
    }
    observed = complete.status

    if case_number == 42:
        first_report = fr.aggregate_fractal_runtime_report_v02(
            topology=bundle.topology,
            topology_artifact=bundle.topology_artifact,
            source_binding=bundle.source_binding,
            cell_results=bundle.cell_results,
            queue_entries=bundle.queue_entries,
            backpressure_states=bundle.backpressure_states,
            runtime_trace=bundle.runtime_trace,
            final_global_budget=bundle.budgets[-1],
            parent_return_transition_decision=bundle.transition_decisions[-1],
            root_result_artifact=bundle.result_artifacts[-1],
        )
        second_report = fr.aggregate_fractal_runtime_report_v02(
            topology=bundle.topology,
            topology_artifact=bundle.topology_artifact,
            source_binding=bundle.source_binding,
            cell_results=bundle.cell_results,
            queue_entries=bundle.queue_entries,
            backpressure_states=bundle.backpressure_states,
            runtime_trace=bundle.runtime_trace,
            final_global_budget=bundle.budgets[-1],
            parent_return_transition_decision=bundle.transition_decisions[-1],
            root_result_artifact=bundle.result_artifacts[-1],
        )
        first = fr.fractal_runtime_report_to_plain_data_v02(first_report)
        second = fr.fractal_runtime_report_to_plain_data_v02(second_report)
        first_bytes = canonical_json_bytes_v01(first)
        second_bytes = canonical_json_bytes_v01(second)
        _require_v02(
            first_report == second_report == bundle.runtime_report
            and first_report.report_id == second_report.report_id
            and first_bytes == second_bytes,
            "g2d5_repeated_report_mismatch",
        )
        proof.update(
            construction_call_count=2,
            first_report_id=first_report.report_id,
            second_report_id=second_report.report_id,
            first_sha256=hashlib.sha256(first_bytes).hexdigest(),
            second_sha256=hashlib.sha256(second_bytes).hexdigest(),
            repeated_value_equal=first == second,
            repeated_id_equal=first_report.report_id == second_report.report_id,
            repeated_bytes_equal=first_bytes == second_bytes,
        )
    elif case_number == 43:
        result_position = {
            item.result_id: index for index, item in enumerate(bundle.cell_results)
        }
        postorder = tuple(
            (
                item.result_id,
                item.ordered_child_result_ids,
                all(result_position[child] < result_position[item.result_id]
                    for child in item.ordered_child_result_ids),
            )
            for item in bundle.cell_results
        )
        _require_v02(all(row[2] for row in postorder), "g2d5_result_cycle")
        phase_rows = tuple(
            (
                result.result_id,
                result.ordered_child_result_ids,
                proposal["proposal_id"],
                post_vv_report["vv_report_id"],
                gt_report["gt_report_id"],
                result.pre_result_validation_report_id,
                result.post_vv_report_ref,
                result.gt_advisory_ref,
            )
            for result, proposal, post_vv_report, gt_report in zip(
                bundle.cell_results,
                bundle.result_proposals,
                bundle.post_vv_reports,
                bundle.gt_advisory_reports,
                strict=True,
            )
        )
        root = bundle.cell_results[-1]
        cyclic = _reidentified_v02(
            replace(root, ordered_child_result_ids=(*root.ordered_child_result_ids, root.result_id)),
            identity_field="result_id",
            rebuild=fr.rebuild_fractal_cell_result_identity_v02,
        )
        cycle_report = fr.validate_fractal_runtime_execution_bundle_v02(
            replace(bundle, cell_results=(*bundle.cell_results[:-1], cyclic))
        )
        _require_v02(
            cycle_report.status == "FAIL_CLOSED",
            "g2d5_acyclic_cycle_accepted",
        )
        terminal_validation_ids = tuple(
            item.validation_report_id
            for item in bundle.validation_reports
            if item.validation_target == "CELL_RESULT_PRECONDITIONS"
        )
        parent_return_decision_id = bundle.transition_decisions[-1].decision_id
        proof.update(
            result_postorder=postorder,
            phase_rows=phase_rows,
            parent_return_decision_id=parent_return_decision_id,
            terminal_validation_ids=terminal_validation_ids,
            causal_ref_sha256=_sha256_plain_v02(bundle.causal_consumption_refs),
            final_bundle_report_id=bundle.runtime_report.report_id,
            cycle_validation_id=cycle_report.validation_report_id,
            cycle_reason_codes=cycle_report.reason_codes,
        )
        refs = (
            *refs,
            parent_return_decision_id,
            *terminal_validation_ids,
            cycle_report.validation_report_id,
        )
    elif case_number == 44:
        entries = bundle.queue_entries
        artifacts = bundle.queue_artifacts
        _require_v02(len(entries) >= 3, "g2d5_queue_matrix_too_small")
        foreign_run = _accepted_run_v02(
            accepted,
            domain_id=DOMAIN_ORDER[1],
            mode="full_fractal",
        )
        predecessor_positions = tuple(
            index
            for index, item in enumerate(entries)
            if item.predecessor_queue_entry_id is not None
        )
        _require_v02(bool(predecessor_positions), "g2d5_queue_predecessor_missing")
        predecessor_position = predecessor_positions[0]
        predecessor_id = entries[predecessor_position].predecessor_queue_entry_id
        predecessor_index = _exactly_one_v02(
            tuple(
                index
                for index, item in enumerate(entries)
                if item.queue_entry_id == predecessor_id
            ),
            label="g2d5_queue_predecessor_index",
        )
        if type(predecessor_index) is not int:
            raise TypeError("g2d5_queue_predecessor_index_type_invalid")
        mutations = (
            ("entry_missing", replace(bundle, queue_entries=entries[1:])),
            ("entry_duplicate", replace(bundle, queue_entries=(entries[0], entries[0], *entries[2:]))),
            ("entry_reordered", replace(bundle, queue_entries=(entries[1], entries[0], *entries[2:]))),
            ("entry_skipped_predecessor", replace(bundle, queue_entries=entries[:predecessor_index] + entries[predecessor_index + 1:])),
            ("entry_foreign", replace(bundle, queue_entries=(foreign_run.bundle.queue_entries[0], *entries[1:]))),
            ("artifact_missing", replace(bundle, queue_artifacts=artifacts[1:])),
            ("artifact_duplicate", replace(bundle, queue_artifacts=(artifacts[0], artifacts[0], *artifacts[2:]))),
            ("artifact_reordered", replace(bundle, queue_artifacts=(artifacts[1], artifacts[0], *artifacts[2:]))),
            ("artifact_skipped_predecessor", replace(bundle, queue_artifacts=artifacts[:predecessor_index] + artifacts[predecessor_index + 1:])),
            ("artifact_foreign", replace(bundle, queue_artifacts=(foreign_run.bundle.queue_artifacts[0], *artifacts[1:]))),
        )
        matrix_rows: list[tuple[object, ...]] = []
        reports: list[fr.FractalRuntimeValidationReportV02] = []
        for axis, mutated_bundle in mutations:
            report = fr.validate_fractal_runtime_execution_bundle_v02(mutated_bundle)
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_queue_substitution_passed")
            matrix_rows.append((axis, report.validation_report_id, report.failure_stage, report.reason_codes))
            reports.append(report)
        observed = reports[0].status
        proof.update(
            baseline_queue_ids=tuple(item.queue_entry_id for item in bundle.queue_entries),
            baseline_artifact_ids=tuple(item.artifact_id for item in bundle.queue_artifacts),
            mutation_rows=tuple(matrix_rows),
            mutation_count=len(matrix_rows),
        )
        refs = (*refs, *(item.validation_report_id for item in reports))
    elif case_number == 45:
        expected_time = (
            bundle.source_context.router_input.local_routing_snapshot.kt_asof_utc
        )
        proposal = bundle.result_proposals[-1]
        with (
            patch.object(post_vv, "utc_now_iso", side_effect=AssertionError("wall_clock_used")) as post_clock,
            patch.object(gt_validator, "utc_now_iso", side_effect=AssertionError("wall_clock_used")) as gt_clock,
        ):
            first_vv = post_vv.validate_result_proposals(
                [proposal],
                checked_at=expected_time,
            )[0]
            second_vv = post_vv.validate_result_proposals(
                [proposal],
                checked_at=expected_time,
            )[0]
            first_gt = gt_validator.validate_gt([first_vv], created_at=expected_time)
            second_gt = gt_validator.validate_gt([second_vv], created_at=expected_time)
        vv_validation = fr.validate_fractal_post_vv_report_v02(
            first_vv,
            result_proposal=proposal,
            source_context=bundle.source_context,
        )
        gt_validation = fr.validate_fractal_gt_advisory_v02(
            first_gt,
            post_vv_report=first_vv,
            source_context=bundle.source_context,
        )
        _require_v02(
            first_vv == second_vv
            and first_gt == second_gt
            and canonical_json_bytes_v01(first_vv) == canonical_json_bytes_v01(second_vv)
            and canonical_json_bytes_v01(first_gt) == canonical_json_bytes_v01(second_gt)
            and post_clock.call_count == gt_clock.call_count == 0
            and vv_validation.status == gt_validation.status == "PASS",
            "g2d5_post_vv_injected_time_mismatch",
        )
        proof.update(
            proposal_id=proposal["proposal_id"],
            expected_injected_time=expected_time,
            first_vv_report_id=first_vv["vv_report_id"],
            second_vv_report_id=second_vv["vv_report_id"],
            first_gt_report_id=first_gt["gt_report_id"],
            second_gt_report_id=second_gt["gt_report_id"],
            first_vv_sha256=_sha256_plain_v02(first_vv),
            second_vv_sha256=_sha256_plain_v02(second_vv),
            first_gt_sha256=_sha256_plain_v02(first_gt),
            second_gt_sha256=_sha256_plain_v02(second_gt),
            vv_validation_id=vv_validation.validation_report_id,
            gt_validation_id=gt_validation.validation_report_id,
            post_wall_clock_call_count=post_clock.call_count,
            gt_wall_clock_call_count=gt_clock.call_count,
        )
        observed = vv_validation.status
        refs = (
            *refs,
            first_vv["vv_report_id"],
            first_gt["gt_report_id"],
            vv_validation.validation_report_id,
            gt_validation.validation_report_id,
        )
    elif case_number == 46:
        report, causal_ref, mutated = _actual_counterfactual_v02(
            run=run,
            disposition="USED",
        )
        proof.update(
            counterfactual_validation_id=report.validation_report_id,
            causal_ref=causal_ref,
            mutated_artifact_id=mutated.artifact_id,
            changed_pointer=causal_ref.output_field,
            accepted_bundle_ref=bundle.runtime_report.report_id,
        )
        observed = report.status
        refs = (*refs, causal_ref.source_artifact_id, mutated.artifact_id, report.validation_report_id)
    elif case_number == 47:
        report, causal_ref, mutated = _actual_counterfactual_v02(
            run=run,
            disposition="IGNORED_WITH_REASON",
        )
        gate = shared["gate_witness"]
        if type(gate) is not _GateBoundaryWitnessV02:
            raise TypeError("g2d5_gate_witness_invalid")
        blocked_proof = _blocked_gate_causal_proof_v02(run=run, gate=gate)
        proof.update(
            ignored_counterfactual_validation_id=report.validation_report_id,
            ignored_causal_ref=causal_ref,
            ignored_mutated_artifact_id=mutated.artifact_id,
            accepted_bundle_ref=bundle.runtime_report.report_id,
            admission_mutation_axis=gate.admission_mutation_axis,
            admission_baseline_source_artifact_id=(
                gate.admission_baseline_source_artifact.artifact_id
            ),
            admission_mutated_source_artifact_id=(
                gate.admission_mutated_source_artifact.artifact_id
            ),
            admission_accepted_causal_ref=gate.admission_accepted_causal_ref,
            admission_profile_validation_id=(
                gate.admission_profile_validation.validation_report_id
            ),
            admission_profile_status=gate.admission_profile_validation.status,
            admission_error=gate.admission_error,
            admission_expected_downstream_artifact_id=(
                gate.admission_expected_downstream_artifact_id
            ),
            admission_child_input_delta=_created_set_delta_v02(
                gate.admission_child_input_before_ids,
                gate.admission_child_input_after_ids,
            ),
            admission_initial_queue_delta=_created_set_delta_v02(
                gate.admission_initial_queue_before_ids,
                gate.admission_initial_queue_after_ids,
            ),
            admission_initial_artifact_delta=_created_set_delta_v02(
                gate.admission_initial_artifact_before_ids,
                gate.admission_initial_artifact_after_ids,
            ),
            actual_gate_disposition=gate.gate_disposition,
            actual_gate_reason_codes=gate.gate_reason_codes,
            actual_gate_evidence_refs=gate.gate_evidence_refs,
            actual_gate_t06_decision_id=gate.t06_decision.decision_id,
            actual_gate_validating_queue_id=gate.validating_entry.queue_entry_id,
            actual_gate_validating_artifact_id=gate.validating_artifact.artifact_id,
            actual_gate_terminal_decision_id=gate.terminal_decision.decision_id,
            actual_gate_blocked_queue_id=gate.blocked_entry.queue_entry_id,
            actual_gate_blocked_artifact_id=gate.blocked_artifact.artifact_id,
            actual_gate_validation_id=gate.blocked_validation.validation_report_id,
            actual_gate_terminal_delta=_created_set_delta_v02(
                gate.denial_terminal_before_ids,
                gate.denial_terminal_after_ids,
            ),
            actual_gate_invocation_delta=_created_set_delta_v02(
                gate.invocation_before_ids,
                gate.invocation_after_ids,
            ),
            actual_gate_downstream_delta=_created_set_delta_v02(
                gate.result_before_ids,
                gate.result_after_ids,
            ),
            blocked_gate_source_queue_id=blocked_proof.source_entry.queue_entry_id,
            blocked_gate_source_artifact_id=blocked_proof.source_artifact.artifact_id,
            blocked_gate_downstream_queue_id=(
                blocked_proof.downstream_entry.queue_entry_id
            ),
            blocked_gate_downstream_artifact_id=(
                blocked_proof.downstream_artifact.artifact_id
            ),
            blocked_gate_output_index=blocked_proof.output_index,
            blocked_gate_causal_ref=blocked_proof.causal_ref,
            blocked_gate_source_validation_id=(
                blocked_proof.source_validation.validation_report_id
            ),
            blocked_gate_downstream_validation_id=(
                blocked_proof.downstream_validation.validation_report_id
            ),
            blocked_gate_causal_validation_reasons=(
                blocked_proof.causal_validation_reasons
            ),
            blocked_gate_artifact_validation_reasons=(
                blocked_proof.artifact_validation_reasons
            ),
            blocked_gate_bundle_validation_reasons=(
                blocked_proof.bundle_validation_reasons
            ),
            blocked_gate_counterfactual_validation_reasons=(
                blocked_proof.generic_counterfactual_validation_reasons
            ),
            blocked_gate_mutated_source_sha256=(
                blocked_proof.generic_mutated_source_sha256
            ),
            blocked_gate_generic_diagnostic_scope=(
                "SUPPLEMENTAL_NON_EXECUTABLE_STABLE_ID"
            ),
            blocked_gate_row_in_accepted_runtime=False,
        )
        observed = report.status
        refs = (
            *refs,
            causal_ref.source_artifact_id,
            mutated.artifact_id,
            report.validation_report_id,
            gate.admission_baseline_source_artifact.artifact_id,
            gate.admission_mutated_source_artifact.artifact_id,
            gate.admission_profile_validation.validation_report_id,
            *gate.gate_evidence_refs,
            gate.t06_decision.decision_id,
            gate.validating_entry.queue_entry_id,
            gate.validating_artifact.artifact_id,
            gate.terminal_decision.decision_id,
            gate.blocked_entry.queue_entry_id,
            gate.blocked_artifact.artifact_id,
            gate.blocked_validation.validation_report_id,
            blocked_proof.source_entry.queue_entry_id,
            blocked_proof.source_artifact.artifact_id,
            blocked_proof.source_validation.validation_report_id,
            blocked_proof.downstream_entry.queue_entry_id,
            blocked_proof.downstream_artifact.artifact_id,
            blocked_proof.downstream_validation.validation_report_id,
        )
    else:
        extra_refs = _populate_accepted_matrix_proof_v02(
            case_number=case_number,
            accepted=accepted,
            run=run,
            proof=proof,
            shared=shared,
        )
        refs = (*refs, *extra_refs)

    return _case_result_v02(
        spec=spec,
        observed_outcome=observed,
        evidence_refs=refs,
        proof=proof,
    )


def _result_context_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
    result: fr.FractalCellResultV02,
) -> dict[str, object]:
    cell_input = _exactly_one_v02(
        tuple(
            item
            for item in bundle.cell_inputs
            if item.cell_input_id == result.cell_input_id
        ),
        label="g2d5_result_context_input",
    )
    if type(cell_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_result_context_input_type_invalid")
    queue_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
    terminal_entries = tuple(
        queue_by_id[item] for item in result.ordered_terminal_queue_entry_ids
    )
    node_by_id = {item.node_id: item for item in bundle.topology_nodes}
    post_position = _exactly_one_v02(
        tuple(
            index
            for index, item in enumerate(terminal_entries)
            if node_by_id[item.node_id].node_kind == "POST_VV"
        ),
        label="g2d5_result_context_post_vv",
    )
    if type(post_position) is not int:
        raise TypeError("g2d5_result_context_post_vv_type_invalid")
    result_by_id = {item.result_id: item for item in bundle.cell_results}
    partial_by_id = {
        item.partial_failure_id: item for item in bundle.partial_failures
    }
    budget_by_id = {item.budget_id: item for item in bundle.budgets}
    return {
        "cell_input": cell_input,
        "terminal_entries": terminal_entries,
        "pre_post_vv_entries": terminal_entries[:post_position],
        "child_results": tuple(
            result_by_id[item] for item in result.ordered_child_result_ids
        ),
        "partial_failures": tuple(
            partial_by_id[item] for item in result.partial_failure_ids
        ),
        "allocated_budget": budget_by_id[result.allocated_cell_budget_id],
        "final_budget": budget_by_id[result.final_cell_budget_id],
        "global_budget": budget_by_id[result.global_budget_id],
    }


def _queue_outcome_variant_v02(
    entry: fr.FractalCellQueueEntryV02,
    *,
    state: str,
    reason_codes: tuple[str, ...],
) -> fr.FractalCellQueueEntryV02:
    provisional = replace(
        entry,
        state=state,
        queue_reason_codes=reason_codes,
    )
    result = _reidentified_v02(
        provisional,
        identity_field="queue_entry_id",
        rebuild=fr.rebuild_fractal_cell_queue_entry_identity_v02,
    )
    if type(result) is not fr.FractalCellQueueEntryV02:
        raise TypeError("g2d5_queue_outcome_variant_type_invalid")
    _require_pass_v02(
        fr.validate_fractal_cell_queue_entry_v02(result),
        label="g2d5_queue_outcome_variant",
    )
    return result


def _build_invoked_child_failure_witness_v02(
    run: _AcceptedRunV02,
    *,
    outcome: str,
    reason_code: str,
) -> _InvokedChildFailureWitnessV02:
    bundle = run.bundle
    child_results = tuple(
        item for item in bundle.cell_results if item.parent_cell_id is not None
    )
    _require_v02(len(child_results) == 2, "g2d5_child_failure_result_count")
    baseline_result = child_results[0]
    safe_sibling_result = child_results[1]
    safe_sibling_index = bundle.cell_results.index(safe_sibling_result)
    safe_sibling_context = _result_context_v02(bundle, safe_sibling_result)
    safe_sibling_input = safe_sibling_context["cell_input"]
    safe_sibling_terminal = safe_sibling_context["terminal_entries"]
    safe_sibling_children = safe_sibling_context["child_results"]
    safe_sibling_partials = safe_sibling_context["partial_failures"]
    safe_sibling_allocated = safe_sibling_context["allocated_budget"]
    safe_sibling_final = safe_sibling_context["final_budget"]
    safe_sibling_global = safe_sibling_context["global_budget"]
    if (
        type(safe_sibling_input) is not fr.FractalCellInputV02
        or type(safe_sibling_terminal) is not tuple
        or type(safe_sibling_children) is not tuple
        or type(safe_sibling_partials) is not tuple
        or type(safe_sibling_allocated) is not fr.FractalRuntimeBudgetV02
        or type(safe_sibling_final) is not fr.FractalRuntimeBudgetV02
        or type(safe_sibling_global) is not fr.FractalRuntimeBudgetV02
    ):
        raise TypeError("g2d5_safe_sibling_context_invalid")
    safe_sibling_structural = fr.validate_fractal_cell_result_v02(
        safe_sibling_result
    )
    safe_sibling_contextual = fr.validate_fractal_cell_result_against_input_v02(
        source_context=run.source_context,
        topology=bundle.topology,
        cell_input=safe_sibling_input,
        terminal_queue_entries=safe_sibling_terminal,
        child_results=safe_sibling_children,
        partial_failures=safe_sibling_partials,
        result_proposal=bundle.result_proposals[safe_sibling_index],
        post_vv_report=bundle.post_vv_reports[safe_sibling_index],
        gt_advisory_report=bundle.gt_advisory_reports[safe_sibling_index],
        cell_budget=safe_sibling_final,
        global_budget=safe_sibling_global,
    )
    safe_sibling_artifact = bundle.result_artifacts[safe_sibling_index]
    _require_v02(
        safe_sibling_structural.status == "PASS"
        and safe_sibling_contextual.status == "PASS"
        and safe_sibling_result.pre_result_validation_report_id
        == safe_sibling_contextual.validation_report_id
        and abi.validate_kernel_artifact_v01(safe_sibling_artifact) == (),
        "g2d5_safe_sibling_validation_invalid",
    )
    safe_sibling_causal_before = tuple(
        _sha256_plain_v02(item)
        for item in bundle.causal_consumption_refs
        if safe_sibling_artifact.artifact_id
        in {item.source_artifact_id, item.downstream_artifact_id}
    )
    safe_sibling_before_sha256 = _sha256_plain_v02((
        safe_sibling_input,
        safe_sibling_result,
        safe_sibling_artifact,
        safe_sibling_structural,
        safe_sibling_contextual,
        safe_sibling_causal_before,
    ))
    context = _result_context_v02(bundle, baseline_result)
    child_input = context["cell_input"]
    baseline_terminal = context["terminal_entries"]
    baseline_prefix = context["pre_post_vv_entries"]
    child_results_context = context["child_results"]
    partial_failures_context = context["partial_failures"]
    allocated_budget = context["allocated_budget"]
    final_budget = context["final_budget"]
    global_budget = context["global_budget"]
    if (
        type(child_input) is not fr.FractalCellInputV02
        or type(baseline_terminal) is not tuple
        or type(baseline_prefix) is not tuple
        or type(child_results_context) is not tuple
        or type(partial_failures_context) is not tuple
        or type(allocated_budget) is not fr.FractalRuntimeBudgetV02
        or type(final_budget) is not fr.FractalRuntimeBudgetV02
        or type(global_budget) is not fr.FractalRuntimeBudgetV02
    ):
        raise TypeError("g2d5_child_failure_context_invalid")
    _require_v02(
        not child_results_context and not partial_failures_context,
        "g2d5_child_failure_leaf_context_invalid",
    )
    changed_prefix = _queue_outcome_variant_v02(
        baseline_prefix[0],
        state=outcome,
        reason_codes=(reason_code,),
    )
    changed_parent_return = _queue_outcome_variant_v02(
        baseline_terminal[-1],
        state=outcome,
        reason_codes=(reason_code,),
    )
    terminal_entries = (
        changed_prefix,
        *baseline_terminal[1:-1],
        changed_parent_return,
    )
    prefix = terminal_entries[: len(baseline_prefix)]
    baseline_index = bundle.cell_results.index(baseline_result)
    baseline_proposal = bundle.result_proposals[baseline_index]
    payload = baseline_proposal["result_payload"]
    if type(payload) is not dict:
        raise TypeError("g2d5_child_failure_proposal_payload_invalid")
    output_refs = tuple(payload["accepted_output_refs"])
    evidence_refs = tuple(payload["evidence_refs"])
    proposal = fr.build_fractal_cell_result_proposal_v02(
        source_context=run.source_context,
        topology=bundle.topology,
        cell_input=child_input,
        pre_post_vv_terminal_queue_entries=prefix,
        child_results=(),
        partial_failures=(),
        accepted_output_refs=output_refs,
        evidence_refs=evidence_refs,
    )
    source_time = run.source_context.router_input.local_routing_snapshot.kt_asof_utc
    vv_report = post_vv.validate_result_proposals(
        [proposal],
        checked_at=source_time,
    )[0]
    gt_report = gt_validator.validate_gt(
        [vv_report],
        created_at=source_time,
    )
    proposal_validation = fr.validate_fractal_cell_result_proposal_v02(
        proposal,
        source_context=run.source_context,
        topology=bundle.topology,
        cell_input=child_input,
        pre_post_vv_terminal_queue_entries=prefix,
        child_results=(),
        partial_failures=(),
    )
    post_vv_validation = fr.validate_fractal_post_vv_report_v02(
        vv_report,
        result_proposal=proposal,
        source_context=run.source_context,
    )
    gt_validation = fr.validate_fractal_gt_advisory_v02(
        gt_report,
        post_vv_report=vv_report,
        source_context=run.source_context,
    )
    result_validation = fr.validate_fractal_cell_result_against_input_v02(
        source_context=run.source_context,
        topology=bundle.topology,
        cell_input=child_input,
        terminal_queue_entries=terminal_entries,
        child_results=(),
        partial_failures=(),
        result_proposal=proposal,
        post_vv_report=vv_report,
        gt_advisory_report=gt_report,
        cell_budget=final_budget,
        global_budget=global_budget,
    )
    for label, report in (
        ("proposal", proposal_validation),
        ("post_vv", post_vv_validation),
        ("gt", gt_validation),
        ("result", result_validation),
    ):
        _require_pass_v02(report, label=f"g2d5_child_failure_{label}")
    result = fr.build_fractal_cell_result_v02(
        bundle.topology,
        child_input,
        terminal_entries,
        (),
        accepted_output_refs=output_refs,
        evidence_refs=evidence_refs,
        pre_result_validation_report=result_validation,
        post_vv_report=vv_report,
        gt_advisory_report=gt_report,
        partial_failures=(),
        allocated_cell_budget=allocated_budget,
        final_cell_budget=final_budget,
        global_budget=global_budget,
    )
    _require_v02(
        result.outcome == outcome and result.parent_cell_id is not None,
        "g2d5_child_failure_outcome_invalid",
    )
    queue_artifact_by_entry_id = {
        abi.kernel_artifact_to_plain_dict_v01(item)["payload"]["queue_entry_id"]: item
        for item in bundle.queue_artifacts
    }
    terminal_artifacts: list[abi.KernelArtifactV01] = []
    for baseline_entry, entry in zip(
        baseline_terminal,
        terminal_entries,
        strict=True,
    ):
        artifact = queue_artifact_by_entry_id[baseline_entry.queue_entry_id]
        if entry != baseline_entry:
            artifact = _mutated_kernel_payload_artifact_v02(
                artifact,
                pointer="/queue_entry_id",
                replacement=entry.queue_entry_id,
            )
            artifact = _mutated_kernel_payload_artifact_v02(
                artifact,
                pointer="/state",
                replacement=entry.state,
            )
            artifact = _mutated_kernel_payload_artifact_v02(
                artifact,
                pointer="/queue_reason_codes",
                replacement=list(entry.queue_reason_codes),
            )
        terminal_artifacts.append(artifact)
    result_artifact = fr.project_fractal_cell_result_kernel_artifact_v02(
        result,
        topology_artifact=bundle.topology_artifact,
        terminal_queue_artifacts=tuple(terminal_artifacts),
        child_result_artifacts=(),
        source_context=run.source_context,
    )
    _require_v02(
        abi.validate_kernel_artifact_v01(result_artifact) == (),
        "g2d5_child_failure_artifact_invalid",
    )
    parent_input = _exactly_one_v02(
        tuple(
            item
            for item in bundle.cell_inputs
            if item.cell_id == child_input.parent_cell_id
        ),
        label="g2d5_child_failure_parent_input",
    )
    if type(parent_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_child_failure_parent_input_invalid")
    partial_failure = fr.record_fractal_partial_failure_v02(
        topology=bundle.topology,
        parent_input=parent_input,
        child_result=result,
        failure_stage="CELL_RESULT",
        reason_codes=(reason_code,),
        source_reason_codes=(),
        evidence_refs=result.evidence_refs,
        allocated_cell_budget=allocated_budget,
        final_cell_budget=final_budget,
        global_budget=global_budget,
        required_child=True,
        sibling_independent=True,
    )
    partial_validation = fr.validate_fractal_partial_failure_record_v02(
        partial_failure
    )
    _require_pass_v02(
        partial_validation,
        label="g2d5_child_failure_partial",
    )
    initial_queue_id = child_input.ordered_initial_queue_entry_ids[0]
    initial_artifact = queue_artifact_by_entry_id[initial_queue_id]
    activation = _exactly_one_v02(
        tuple(
            item
            for item in bundle.causal_consumption_refs
            if item.decision_effect == "CHILD_ACTIVATION"
            and item.downstream_artifact_id == initial_artifact.artifact_id
        ),
        label="g2d5_child_failure_activation",
    )
    if type(activation) is not abi.CausalConsumptionRefV01:
        raise TypeError("g2d5_child_failure_activation_invalid")
    activation_row = (
        activation.producer_actor_id,
        activation.source_artifact_id,
        activation.output_field,
        activation.consumer_component,
        activation.downstream_artifact_id,
        activation.decision_effect,
        activation.disposition,
        activation.reason_code,
    )
    result_before = tuple(item.result_id for item in bundle.cell_results)
    result_after = (*result_before, result.result_id)
    partial_before = tuple(
        item.partial_failure_id for item in bundle.partial_failures
    )
    partial_after = (*partial_before, partial_failure.partial_failure_id)
    causal_before = tuple(
        _sha256_plain_v02(item) for item in bundle.causal_consumption_refs
    )
    causal_after = causal_before
    _require_v02(
        _created_set_delta_v02(result_before, result_after)["created_count"] == 1
        and _created_set_delta_v02(partial_before, partial_after)["created_count"] == 1
        and _created_set_delta_v02(causal_before, causal_after)["created_count"] == 0,
        "g2d5_child_failure_created_geometry_invalid",
    )
    safe_sibling_after = _exactly_one_v02(
        tuple(
            item
            for item in bundle.cell_results
            if item.result_id == safe_sibling_result.result_id
        ),
        label="g2d5_safe_sibling_after",
    )
    if type(safe_sibling_after) is not fr.FractalCellResultV02:
        raise TypeError("g2d5_safe_sibling_after_invalid")
    safe_sibling_causal_after = tuple(
        _sha256_plain_v02(item)
        for item in bundle.causal_consumption_refs
        if safe_sibling_artifact.artifact_id
        in {item.source_artifact_id, item.downstream_artifact_id}
    )
    safe_sibling_after_sha256 = _sha256_plain_v02((
        safe_sibling_input,
        safe_sibling_after,
        safe_sibling_artifact,
        safe_sibling_structural,
        safe_sibling_contextual,
        safe_sibling_causal_after,
    ))
    _require_v02(
        safe_sibling_before_sha256 == safe_sibling_after_sha256
        and safe_sibling_causal_before == safe_sibling_causal_after,
        "g2d5_safe_sibling_changed",
    )
    return _InvokedChildFailureWitnessV02(
        source_context=run.source_context,
        topology=bundle.topology,
        child_input=child_input,
        baseline_result=baseline_result,
        terminal_entries=terminal_entries,
        result_proposal_id=proposal["proposal_id"],
        post_vv_report_id=vv_report["vv_report_id"],
        gt_report_id=gt_report["gt_report_id"],
        proposal_validation=proposal_validation,
        post_vv_validation=post_vv_validation,
        gt_validation=gt_validation,
        result_validation=result_validation,
        result=result,
        result_artifact=result_artifact,
        partial_failure=partial_failure,
        partial_validation=partial_validation,
        activation_causal_row=activation_row,
        result_before_ids=result_before,
        result_after_ids=result_after,
        partial_before_ids=partial_before,
        partial_after_ids=partial_after,
        causal_before_ids=causal_before,
        causal_after_ids=causal_after,
        safe_sibling_input=safe_sibling_input,
        safe_sibling_result=safe_sibling_result,
        safe_sibling_result_artifact=safe_sibling_artifact,
        safe_sibling_structural_validation=safe_sibling_structural,
        safe_sibling_context_validation=safe_sibling_contextual,
        safe_sibling_before_sha256=safe_sibling_before_sha256,
        safe_sibling_after_sha256=safe_sibling_after_sha256,
        safe_sibling_result_before_ids=(safe_sibling_result.result_id,),
        safe_sibling_result_after_ids=(safe_sibling_after.result_id,),
        safe_sibling_causal_before_ids=safe_sibling_causal_before,
        safe_sibling_causal_after_ids=safe_sibling_causal_after,
    )


def _outcome_witness_rows_v02(
    accepted: tuple[_AcceptedRunV02, ...],
) -> tuple[dict[str, object], ...]:
    run = _accepted_run_v02(
        accepted,
        domain_id=DOMAIN_ORDER[0],
        mode="full_semantic",
    )
    bundle = run.bundle
    root_result = _exactly_one_v02(
        tuple(item for item in bundle.cell_results if item.parent_cell_id is None),
        label="g2d5_outcome_root_result",
    )
    if type(root_result) is not fr.FractalCellResultV02:
        raise TypeError("g2d5_outcome_root_result_type_invalid")
    context = _result_context_v02(bundle, root_result)
    cell_input = context["cell_input"]
    baseline_terminal = context["terminal_entries"]
    baseline_prefix = context["pre_post_vv_entries"]
    allocated_budget = context["allocated_budget"]
    final_budget = context["final_budget"]
    global_budget = context["global_budget"]
    if (
        type(cell_input) is not fr.FractalCellInputV02
        or type(baseline_terminal) is not tuple
        or type(baseline_prefix) is not tuple
        or type(allocated_budget) is not fr.FractalRuntimeBudgetV02
        or type(final_budget) is not fr.FractalRuntimeBudgetV02
        or type(global_budget) is not fr.FractalRuntimeBudgetV02
    ):
        raise TypeError("g2d5_outcome_context_invalid")
    baseline_proposal = bundle.result_proposals[
        bundle.cell_results.index(root_result)
    ]
    output_refs = tuple(baseline_proposal["result_payload"]["accepted_output_refs"])
    evidence_refs = tuple(baseline_proposal["result_payload"]["evidence_refs"])
    source_time = (
        run.source_context.router_input.local_routing_snapshot.kt_asof_utc
    )
    state_rows = (
        ("completed", "COMPLETED", ()),
        ("degraded", "DEGRADED", ("g2d_partial_failure_recorded",)),
        ("blocked", "BLOCKED", ("g2d_required_child_failure",)),
        ("needs_user", "NEEDS_USER", ("g2d_resolvable_input_needs_user",)),
        ("deadend", "DEADEND", ("g2d_no_progress_deadend",)),
    )
    queue_artifact_by_entry_id = {
        abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"]["queue_entry_id"]: artifact
        for artifact in bundle.queue_artifacts
    }
    rows: list[dict[str, object]] = []
    for proposal_status, terminal_state, reasons in state_rows:
        terminal_entries = baseline_terminal
        if terminal_state != "COMPLETED":
            changed_prefix = _queue_outcome_variant_v02(
                baseline_prefix[0],
                state=terminal_state,
                reason_codes=reasons,
            )
            changed_parent_return = _queue_outcome_variant_v02(
                baseline_terminal[-1],
                state=terminal_state,
                reason_codes=reasons,
            )
            terminal_entries = (
                changed_prefix,
                *baseline_terminal[1:-1],
                changed_parent_return,
            )
        prefix = terminal_entries[: len(baseline_prefix)]
        proposal = fr.build_fractal_cell_result_proposal_v02(
            source_context=run.source_context,
            topology=bundle.topology,
            cell_input=cell_input,
            pre_post_vv_terminal_queue_entries=prefix,
            child_results=(),
            partial_failures=(),
            accepted_output_refs=output_refs,
            evidence_refs=evidence_refs,
        )
        vv_report = post_vv.validate_result_proposals(
            [proposal],
            checked_at=source_time,
        )[0]
        gt_report = gt_validator.validate_gt(
            [vv_report],
            created_at=source_time,
        )
        proposal_report = fr.validate_fractal_cell_result_proposal_v02(
            proposal,
            source_context=run.source_context,
            topology=bundle.topology,
            cell_input=cell_input,
            pre_post_vv_terminal_queue_entries=prefix,
            child_results=(),
            partial_failures=(),
        )
        vv_validation = fr.validate_fractal_post_vv_report_v02(
            vv_report,
            result_proposal=proposal,
            source_context=run.source_context,
        )
        gt_validation = fr.validate_fractal_gt_advisory_v02(
            gt_report,
            post_vv_report=vv_report,
            source_context=run.source_context,
        )
        result_validation = fr.validate_fractal_cell_result_against_input_v02(
            source_context=run.source_context,
            topology=bundle.topology,
            cell_input=cell_input,
            terminal_queue_entries=terminal_entries,
            child_results=(),
            partial_failures=(),
            result_proposal=proposal,
            post_vv_report=vv_report,
            gt_advisory_report=gt_report,
            cell_budget=final_budget,
            global_budget=global_budget,
        )
        for label, report in (
            ("proposal", proposal_report),
            ("post_vv", vv_validation),
            ("gt", gt_validation),
            ("result", result_validation),
        ):
            _require_pass_v02(report, label=f"g2d5_outcome_{label}")
        result = fr.build_fractal_cell_result_v02(
            bundle.topology,
            cell_input,
            terminal_entries,
            (),
            accepted_output_refs=output_refs,
            evidence_refs=evidence_refs,
            pre_result_validation_report=result_validation,
            post_vv_report=vv_report,
            gt_advisory_report=gt_report,
            partial_failures=(),
            allocated_cell_budget=allocated_budget,
            final_cell_budget=final_budget,
            global_budget=global_budget,
        )
        _require_v02(
            result.outcome == terminal_state,
            "g2d5_outcome_result_mismatch",
        )
        terminal_artifacts: list[abi.KernelArtifactV01] = []
        for baseline_entry, entry in zip(
            baseline_terminal,
            terminal_entries,
            strict=True,
        ):
            artifact = queue_artifact_by_entry_id[baseline_entry.queue_entry_id]
            if entry != baseline_entry:
                artifact = _mutated_kernel_payload_artifact_v02(
                    artifact,
                    pointer="/queue_entry_id",
                    replacement=entry.queue_entry_id,
                )
                artifact = _mutated_kernel_payload_artifact_v02(
                    artifact,
                    pointer="/state",
                    replacement=entry.state,
                )
                artifact = _mutated_kernel_payload_artifact_v02(
                    artifact,
                    pointer="/queue_reason_codes",
                    replacement=list(entry.queue_reason_codes),
                )
            terminal_artifacts.append(artifact)
        result_artifact = fr.project_fractal_cell_result_kernel_artifact_v02(
            result,
            topology_artifact=bundle.topology_artifact,
            terminal_queue_artifacts=tuple(terminal_artifacts),
            child_result_artifacts=(),
            source_context=run.source_context,
        )
        _require_v02(
            abi.validate_kernel_artifact_v01(result_artifact) == (),
            "g2d5_outcome_result_artifact_invalid",
        )
        rows.append(
            {
                "proposal_status": proposal_status,
                "terminal_state": terminal_state,
                "proposal_id": proposal["proposal_id"],
                "vv_report_id": vv_report["vv_report_id"],
                "gt_report_id": gt_report["gt_report_id"],
                "proposal_validation_id": proposal_report.validation_report_id,
                "vv_validation_id": vv_validation.validation_report_id,
                "gt_validation_id": gt_validation.validation_report_id,
                "result_validation_id": result_validation.validation_report_id,
                "result_id": result.result_id,
                "result_artifact_id": result_artifact.artifact_id,
                "result_artifact_lifecycle": result_artifact.lifecycle_state,
            }
        )
    return tuple(rows)


def _result_proposal_ref_material_v02(
    *,
    cell_input: fr.FractalCellInputV02,
    prefix: tuple[fr.FractalCellQueueEntryV02, ...],
    child_results: tuple[fr.FractalCellResultV02, ...],
    partial_failures: tuple[fr.FractalPartialFailureRecordV02, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    outputs: list[str] = []
    evidence: list[str] = []
    for values in (
        *(item.observed_output_refs for item in prefix),
        *(item.accepted_output_refs for item in child_results),
    ):
        for value in values:
            if value not in outputs:
                outputs.append(value)
    for values in (
        *(item.observed_evidence_refs for item in prefix),
        *(item.evidence_refs for item in child_results),
        *(item.evidence_refs for item in partial_failures),
    ):
        for value in values:
            if value not in evidence:
                evidence.append(value)
    if (
        cell_input.parent_cell_id is None
        and child_results
        and any(cell_input.cell_input_id in item.evidence_refs for item in child_results)
    ):
        positions = tuple(
            index
            for index, value in enumerate(evidence)
            if value == cell_input.cell_input_id
        )
        _require_v02(
            len(positions) == 1,
            "g2d5_result_structural_evidence_geometry",
        )
        evidence.pop(positions[0])
    return tuple(outputs), tuple(evidence)


def _stage_artifacts_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> tuple[
    tuple[abi.KernelArtifactV01, ...],
    tuple[abi.KernelArtifactV01, ...],
    tuple[abi.KernelArtifactV01, ...],
]:
    by_id = {
        item.artifact_id: item
        for item in (
            bundle.topology_artifact,
            *bundle.queue_artifacts,
            *bundle.result_artifacts,
            bundle.report_artifact,
        )
    }
    stage_a = (
        bundle.source_context.proposal_artifact,
        bundle.source_context.decision_artifact,
        bundle.source_context.route_eligibility_artifact,
        bundle.topology_artifact,
    )
    stage_b = (
        *stage_a[:3],
        *(by_id[item] for item in bundle.runtime_trace.abi_artifact_refs),
    )
    return stage_a, stage_b, (*stage_b, bundle.report_artifact)


def _causal_validation_report_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> fr.FractalRuntimeValidationReportV02:
    _stage_a, _stage_b, stage_c = _stage_artifacts_v02(bundle)
    return fr.validate_fractal_runtime_causal_consumption_refs_v02(
        bundle.causal_consumption_refs,
        source_context=bundle.source_context,
        topology=bundle.topology,
        topology_artifact=bundle.topology_artifact,
        runtime_assignments=bundle.runtime_assignments,
        queue_entries=bundle.queue_entries,
        queue_artifacts=bundle.queue_artifacts,
        cell_results=bundle.cell_results,
        result_artifacts=bundle.result_artifacts,
        runtime_trace=bundle.runtime_trace,
        runtime_report=bundle.runtime_report,
        report_artifact=bundle.report_artifact,
        stage_d_c_artifacts=stage_c,
    )


def _isolated_four_child_allocations_v02(
    run: _AcceptedRunV02,
) -> tuple[
    tuple[dict[str, object], ...],
    fr.FractalRuntimeValidationReportV02,
    tuple[tuple[int, int], ...],
]:
    bundle = run.bundle
    root_input = _exactly_one_v02(
        tuple(item for item in bundle.cell_inputs if item.parent_cell_id is None),
        label="g2d5_four_child_root_input",
    )
    if type(root_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_four_child_root_input_type_invalid")
    budget_by_id = {item.budget_id: item for item in bundle.budgets}
    basis = budget_by_id[root_input.cell_budget_id]
    _require_v02(
        basis.budget_state == "ACTIVE"
        and basis.budget_event_kind == "CELL_CREATE"
        and root_input.cell_budget_id == basis.budget_id,
        "g2d5_four_child_basis_invalid",
    )
    entry_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
    node_by_id = {item.node_id: item for item in bundle.topology_nodes}
    initial_entries = tuple(
        entry_by_id[item] for item in root_input.ordered_initial_queue_entry_ids
    )
    required_entries = tuple(
        entry_by_id[item] for item in root_input.ordered_required_queue_entry_ids
    )
    ordered_nodes = tuple(node_by_id[item] for item in root_input.ordered_node_ids)
    sibling_count = 4
    derivation_rows = ((0, 1), (1, 1), (0, 2), (1, 2))
    planned_ids = tuple(
        fr.derive_fractal_child_cell_id_v02(
            topology_seed_id=bundle.topology_seed.topology_seed_id,
            parent_cell_id=root_input.cell_id,
            canonical_child_index=canonical_child_index,
            accepted_mode=bundle.source_binding.accepted_mode,
            selected_local_mode_profile_id=(
                bundle.source_binding.selected_local_mode_profile_id
            ),
            source_mode_profile_set_id=bundle.source_binding.source_mode_profile_set_id,
            child_scope_ref=bundle.source_binding.accepted_scope_ref,
            runtime_policy_id=run.source_context.runtime_policy.policy_id,
            required_capability_ids=(
                bundle.source_binding.required_downstream_capability_ids
            ),
            forbidden_claims=run.source_context.runtime_policy.forbidden_claims,
            child_depth=child_depth,
        )
        for canonical_child_index, child_depth in derivation_rows
    )
    four_child_input = _reidentified_v02(
        replace(
            root_input,
            requested_child_count=sibling_count,
            ordered_planned_child_cell_ids=planned_ids,
        ),
        identity_field="cell_input_id",
        rebuild=fr.rebuild_fractal_cell_input_identity_v02,
    )
    if type(four_child_input) is not fr.FractalCellInputV02:
        raise TypeError("g2d5_four_child_structural_context_type_invalid")
    input_report = fr.validate_fractal_cell_input_v02(four_child_input)
    _require_v02(
        input_report.status == "FAIL_CLOSED"
        and "g2d_node_instance_geometry_invalid" in input_report.reason_codes,
        "g2d5_four_child_structural_context_projection_accepted",
    )
    rows: list[dict[str, object]] = []
    for index, child_id in enumerate(planned_ids):
        budget = fr.build_fractal_runtime_budget_v02(
            policy=run.source_context.runtime_policy,
            topology_seed=bundle.topology_seed,
            allocation_parent_budget=basis,
            predecessor_budget=None,
            owning_cell_id=child_id,
            budget_scope="CHILD_CELL_LOCAL",
            budget_state="ALLOCATED",
            budget_event_kind="INITIAL_ALLOCATION",
            budget_context_input=four_child_input,
            canonical_child_index=index,
            allocation_queue_entries=initial_entries,
            transition_decision=None,
            paired_cell_budget=None,
            child_result=None,
        )
        budget_report = fr.validate_fractal_runtime_budget_v02(budget)
        _require_pass_v02(budget_report, label="g2d5_four_child_budget")
        rows.append(
            {
                "canonical_child_index": index,
                "budget_id": budget.budget_id,
                "budget_validation_id": budget_report.validation_report_id,
                "allocation_parent_budget_id": budget.allocation_parent_budget_id,
                "parent_input_id": four_child_input.cell_input_id,
                "child_cell_id": budget.owning_cell_id,
                "requested_sibling_count": sibling_count,
                "max_total_cells": budget.max_total_cells,
                "max_revise_count": budget.max_revise_count,
                "max_wall_time_units": budget.max_wall_time_units,
                "max_token_budget": budget.max_token_budget,
                "max_provider_calls": budget.max_provider_calls,
                "structural_row_sha256": _sha256_plain_v02(budget),
            }
        )
    return tuple(rows), input_report, derivation_rows


def _populate_accepted_matrix_proof_v02(
    *,
    case_number: int,
    accepted: tuple[_AcceptedRunV02, ...],
    run: _AcceptedRunV02,
    proof: dict[str, object],
    shared: dict[str, object],
) -> tuple[str, ...]:
    bundle = run.bundle
    extra_refs: tuple[str, ...] = ()
    if case_number == 48:
        position = {item.result_id: index for index, item in enumerate(bundle.cell_results)}
        actual_rows = tuple(
            (
                item.result_id,
                item.ordered_child_result_ids,
                item.partial_failure_ids,
                item.allocated_cell_budget_id,
                item.final_cell_budget_id,
                item.global_budget_id,
                all(position[child] < position[item.result_id]
                    for child in item.ordered_child_result_ids),
            )
            for item in bundle.cell_results
        )
        _require_v02(all(row[6] for row in actual_rows), "g2d5_child_result_postorder")
        no_child = _accepted_run_v02(
            accepted,
            domain_id=DOMAIN_ORDER[0],
            mode="full_semantic",
        ).bundle
        no_child_rows = tuple(
            item.result_id
            for item in no_child.cell_results
            if item.parent_cell_id is not None
        )
        _require_v02(
            no_child_rows == () and no_child.partial_failures == (),
            "g2d5_no_child_failure_fabricated",
        )
        root = bundle.cell_results[-1]
        invalid_root = _reidentified_v02(
            replace(
                root,
                ordered_child_result_ids=(
                    *root.ordered_child_result_ids,
                    "frcellresult_v02:" + "0" * 64,
                ),
            ),
            identity_field="result_id",
            rebuild=fr.rebuild_fractal_cell_result_identity_v02,
        )
        invalid_report = fr.validate_fractal_runtime_execution_bundle_v02(
            replace(bundle, cell_results=(*bundle.cell_results[:-1], invalid_root))
        )
        _require_v02(
            invalid_report.status == "FAIL_CLOSED",
            "g2d5_invalid_child_result_ref_accepted",
        )
        proof.update(
            actual_child_result_rows=actual_rows,
            no_child_result_ids=no_child_rows,
            no_child_partial_failure_ids=tuple(
                item.partial_failure_id for item in no_child.partial_failures
            ),
            invalid_child_ref_validation_id=invalid_report.validation_report_id,
            invalid_child_ref_reason_codes=invalid_report.reason_codes,
        )
        extra_refs = (invalid_report.validation_report_id,)
    elif case_number == 49:
        result_ids = {item.result_id for item in bundle.cell_results}
        rows: list[tuple[object, ...]] = []
        validation_ids: list[str] = []
        for index, result in enumerate(bundle.cell_results):
            context = _result_context_v02(bundle, result)
            proposal = bundle.result_proposals[index]
            vv_report = bundle.post_vv_reports[index]
            gt_report = bundle.gt_advisory_reports[index]
            proposal_validation = fr.validate_fractal_cell_result_proposal_v02(
                proposal,
                source_context=bundle.source_context,
                topology=bundle.topology,
                cell_input=context["cell_input"],
                pre_post_vv_terminal_queue_entries=context["pre_post_vv_entries"],
                child_results=context["child_results"],
                partial_failures=context["partial_failures"],
            )
            vv_validation = fr.validate_fractal_post_vv_report_v02(
                vv_report,
                result_proposal=proposal,
                source_context=bundle.source_context,
            )
            gt_validation = fr.validate_fractal_gt_advisory_v02(
                gt_report,
                post_vv_report=vv_report,
                source_context=bundle.source_context,
            )
            result_validation = fr.validate_fractal_cell_result_against_input_v02(
                source_context=bundle.source_context,
                topology=bundle.topology,
                cell_input=context["cell_input"],
                terminal_queue_entries=context["terminal_entries"],
                child_results=context["child_results"],
                partial_failures=context["partial_failures"],
                result_proposal=proposal,
                post_vv_report=vv_report,
                gt_advisory_report=gt_report,
                cell_budget=context["final_budget"],
                global_budget=context["global_budget"],
            )
            reports = (
                proposal_validation,
                vv_validation,
                gt_validation,
                result_validation,
            )
            _require_v02(
                all(item.status == "PASS" for item in reports),
                "g2d5_result_validation_chain_invalid",
            )
            validation_ids.extend(item.validation_report_id for item in reports)
            rows.append(
                (
                    result.result_id,
                    result.pre_result_validation_report_id,
                    proposal["proposal_id"],
                    vv_report["vv_report_id"],
                    gt_report["gt_report_id"],
                    tuple(item.validation_report_id for item in reports),
                )
            )
        _require_v02(
            all(row[1] not in result_ids for row in rows),
            "g2d5_pre_result_cycle",
        )
        root = bundle.cell_results[-1]
        cyclic = _reidentified_v02(
            replace(root, ordered_child_result_ids=(*root.ordered_child_result_ids, root.result_id)),
            identity_field="result_id",
            rebuild=fr.rebuild_fractal_cell_result_identity_v02,
        )
        cycle_report = fr.validate_fractal_runtime_execution_bundle_v02(
            replace(bundle, cell_results=(*bundle.cell_results[:-1], cyclic))
        )
        _require_v02(cycle_report.status == "FAIL_CLOSED", "g2d5_result_cycle_accepted")
        proof.update(
            validation_chain_rows=tuple(rows),
            cycle_validation_id=cycle_report.validation_report_id,
            cycle_reason_codes=cycle_report.reason_codes,
        )
        extra_refs = (*validation_ids, cycle_report.validation_report_id)
    elif case_number == 50:
        no_child_run = _accepted_run_v02(
            accepted,
            domain_id=DOMAIN_ORDER[0],
            mode="full_semantic",
        )
        root_result = bundle.cell_results[-1]
        context = _result_context_v02(bundle, root_result)
        one_child = (context["child_results"][0],)
        output_refs, evidence_refs = _result_proposal_ref_material_v02(
            cell_input=context["cell_input"],
            prefix=context["pre_post_vv_entries"],
            child_results=one_child,
            partial_failures=(),
        )
        one_child_proposal = fr.build_fractal_cell_result_proposal_v02(
            source_context=bundle.source_context,
            topology=bundle.topology,
            cell_input=context["cell_input"],
            pre_post_vv_terminal_queue_entries=context["pre_post_vv_entries"],
            child_results=one_child,
            partial_failures=(),
            accepted_output_refs=output_refs,
            evidence_refs=evidence_refs,
        )
        one_child_report = fr.validate_fractal_cell_result_proposal_v02(
            one_child_proposal,
            source_context=bundle.source_context,
            topology=bundle.topology,
            cell_input=context["cell_input"],
            pre_post_vv_terminal_queue_entries=context["pre_post_vv_entries"],
            child_results=one_child,
            partial_failures=(),
        )
        _require_pass_v02(one_child_report, label="g2d5_one_child_aggregation")
        proof.update(
            aggregation_rows=(
                (
                    0,
                    no_child_run.bundle.cell_results[-1].result_id,
                    no_child_run.bundle.result_proposals[-1]["proposal_id"],
                ),
                (1, one_child[0].result_id, one_child_proposal["proposal_id"]),
                (
                    2,
                    root_result.result_id,
                    bundle.result_proposals[-1]["proposal_id"],
                ),
            ),
            one_child_validation_id=one_child_report.validation_report_id,
            queue_entry_count=len(bundle.queue_entries),
            budget_count=len(bundle.budgets),
            runtime_abi_ref_count=len(bundle.runtime_trace.abi_artifact_refs),
        )
        extra_refs = (one_child_report.validation_report_id,)
    elif case_number == 51:
        rows: list[dict[str, object]] = []
        for item in accepted[:5]:
            constructed = fr.construct_runtime_execution_topology_v02(
                item.source_context
            )
            contextual = fr.validate_runtime_execution_topology_against_sources_v02(
                constructed,
                source_context=item.source_context,
            )
            _require_pass_v02(contextual, label="g2d5_template_context")
            node_template = dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)[item.mode]
            edge_template = dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)[item.mode]
            assignment_template = dict(fr.MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[item.mode]
            _require_v02(
                constructed == item.bundle.topology
                and tuple(node.canonical_index for node in item.bundle.topology_nodes)
                == tuple(row[0] for row in node_template)
                and tuple(edge.canonical_index for edge in item.bundle.topology_edges)
                == tuple(row[0] for row in edge_template)
                and tuple(assignment.canonical_index for assignment in item.bundle.runtime_assignments)
                == tuple(row[0] for row in assignment_template),
                "g2d5_template_geometry_mismatch",
            )
            rows.append(
                {
                    "mode": item.mode,
                    "topology_id": constructed.topology_id,
                    "context_validation_id": contextual.validation_report_id,
                    "node_template_sha256": _sha256_plain_v02(node_template),
                    "node_rows_sha256": _sha256_plain_v02(item.bundle.topology_nodes),
                    "edge_template_sha256": _sha256_plain_v02(edge_template),
                    "edge_rows_sha256": _sha256_plain_v02(item.bundle.topology_edges),
                    "assignment_template_sha256": _sha256_plain_v02(assignment_template),
                    "assignment_rows_sha256": _sha256_plain_v02(item.bundle.runtime_assignments),
                    "node_count": len(node_template),
                    "edge_count": len(edge_template),
                    "assignment_count": len(assignment_template),
                }
            )
        baseline_node = bundle.topology_nodes[0]
        mutated_node = _reidentified_v02(
            replace(baseline_node, required=not baseline_node.required),
            identity_field="node_id",
            rebuild=fr.rebuild_runtime_topology_node_identity_v02,
        )
        mutated_topology = _reidentified_v02(
            replace(
                bundle.topology,
                ordered_node_ids=(
                    mutated_node.node_id,
                    *bundle.topology.ordered_node_ids[1:],
                ),
            ),
            identity_field="topology_id",
            rebuild=fr.rebuild_runtime_execution_topology_identity_v02,
        )
        mutation_report = fr.validate_runtime_execution_topology_against_sources_v02(
            mutated_topology,
            source_context=bundle.source_context,
        )
        _require_v02(
            mutation_report.status == "FAIL_CLOSED",
            "g2d5_template_mutation_accepted",
        )
        proof.update(
            five_mode_template_rows=tuple(rows),
            mutation_axis="topology_nodes[0].required",
            mutated_node_id=mutated_node.node_id,
            mutation_validation_id=mutation_report.validation_report_id,
            mutation_reason_codes=mutation_report.reason_codes,
        )
        extra_refs = (mutation_report.validation_report_id,)
    elif case_number == 52:
        rows: list[dict[str, object]] = []
        mutation_report_ids: list[str] = []
        for item in accepted[:5]:
            binding = item.bundle.source_binding
            source_report = fr.validate_runtime_topology_source_binding_against_g2c_v02(
                binding,
                source_context=item.source_context,
            )
            _require_pass_v02(source_report, label="g2d5_source_binding")
            mutations = (
                ("selected_local_mode_profile_id", binding.selected_local_mode_profile_id + ":foreign"),
                ("selected_feasibility_row_id", binding.selected_feasibility_row_id + ":foreign"),
                ("selected_safe_depth_rank", binding.selected_safe_depth_rank + 1),
                ("selected_expected_cost_units", binding.selected_expected_cost_units + 1),
                ("required_downstream_capability_ids", (*binding.required_downstream_capability_ids, "capability:g2d5:foreign")),
                ("source_policy_snapshot_id", binding.source_policy_snapshot_id + ":foreign"),
                ("source_capability_snapshot_id", binding.source_capability_snapshot_id + ":foreign"),
                ("accepted_scope_ref", binding.accepted_scope_ref + ":widened"),
            )
            mutation_rows: list[tuple[object, ...]] = []
            for axis, replacement in mutations:
                mutated = _reidentified_v02(
                    replace(binding, **{axis: replacement}),
                    identity_field="source_binding_id",
                    rebuild=fr.rebuild_runtime_topology_source_binding_identity_v02,
                )
                report = fr.validate_runtime_topology_source_binding_against_g2c_v02(
                    mutated,
                    source_context=item.source_context,
                )
                _require_v02(
                    report.status == "FAIL_CLOSED",
                    "g2d5_source_binding_substitution_accepted",
                )
                mutation_rows.append(
                    (axis, mutated.source_binding_id, report.validation_report_id, report.reason_codes)
                )
                mutation_report_ids.append(report.validation_report_id)
            rows.append(
                {
                    "mode": item.mode,
                    "source_binding_id": binding.source_binding_id,
                    "selected_profile_id": binding.selected_local_mode_profile_id,
                    "selected_feasibility_row_id": binding.selected_feasibility_row_id,
                    "selected_safe_depth_rank": binding.selected_safe_depth_rank,
                    "selected_expected_cost_units": binding.selected_expected_cost_units,
                    "required_capability_ids": binding.required_downstream_capability_ids,
                    "runtime_policy_id": binding.runtime_policy_id,
                    "accepted_scope_ref": binding.accepted_scope_ref,
                    "positive_validation_id": source_report.validation_report_id,
                    "mutation_rows": tuple(mutation_rows),
                }
            )
        proof.update(
            source_binding_rows=tuple(rows),
            per_mode_substitution_count=8,
            total_substitution_count=len(mutation_report_ids),
        )
        extra_refs = tuple(mutation_report_ids)
    elif case_number == 53:
        budget_ids = {item.budget_id for item in bundle.budgets}
        rows = tuple(
            (
                item.budget_id,
                item.allocation_parent_budget_id,
                item.predecessor_budget_id,
                item.budget_event_kind,
                item.budget_event_ref,
                item.consumed_cell_count,
                item.remaining_cell_count,
                item.consumed_revise_count,
            )
            for item in bundle.budgets
        )
        _require_v02(
            all(
                (parent is None or parent in budget_ids)
                and (predecessor is None or predecessor in budget_ids)
                for _, parent, predecessor, *_rest in rows
            ),
            "g2d5_budget_lineage_missing",
        )
        baseline_rows = tuple(
            item
            for item in bundle.budgets
            if item.predecessor_budget_id is not None and item.budget_state == "ACTIVE"
        )
        _require_v02(bool(baseline_rows), "g2d5_budget_matrix_basis_missing")
        baseline = baseline_rows[0]
        mutations = (
            ("allocation_parent", {"allocation_parent_budget_id": "frbudget_v02:" + "0" * 64}, True),
            ("predecessor", {"predecessor_budget_id": "frbudget_v02:" + "0" * 64}, True),
            ("event", {"budget_event_kind": "REVISE"}, True),
            ("state", {"budget_state": "FINAL"}, True),
            ("counter", {"consumed_cell_count": baseline.consumed_cell_count + 1}, True),
            ("remaining", {"remaining_cell_count": baseline.remaining_cell_count + 1}, True),
            ("event_ref", {"budget_event_ref": "frtransition_v02:" + "0" * 64}, True),
            ("identity", {"budget_id": "frbudget_v02:" + "0" * 64}, False),
        )
        mutation_rows: list[tuple[object, ...]] = []
        reports: list[fr.FractalRuntimeValidationReportV02] = []
        budget_position = bundle.budgets.index(baseline)
        for axis, changes, reseal in mutations:
            mutated = replace(baseline, **changes)
            if reseal:
                mutated = _reidentified_v02(
                    mutated,
                    identity_field="budget_id",
                    rebuild=fr.rebuild_fractal_runtime_budget_identity_v02,
                )
            mutated_budgets = (
                *bundle.budgets[:budget_position],
                mutated,
                *bundle.budgets[budget_position + 1:],
            )
            report = fr.validate_fractal_runtime_execution_bundle_v02(
                replace(bundle, budgets=mutated_budgets)
            )
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_budget_mutation_accepted")
            mutation_rows.append(
                (axis, mutated.budget_id, report.validation_report_id, report.reason_codes)
            )
            reports.append(report)
        event_counts = tuple(
            (event, sum(item.budget_event_kind == event for item in bundle.budgets))
            for event in fr.BUDGET_EVENT_KINDS
        )
        proof.update(
            allocation_predecessor_debit_rows=rows,
            event_counts=event_counts,
            mutation_rows=tuple(mutation_rows),
            mutation_count=len(mutation_rows),
        )
        extra_refs = tuple(item.validation_report_id for item in reports)
    elif case_number == 54:
        outcome_rows = shared["outcome_rows"]
        if type(outcome_rows) is not tuple:
            raise TypeError("g2d5_outcome_rows_invalid")
        expected_rows = tuple(
            (proposal_status, terminal)
            for proposal_status, _t06, _rule, terminal
            in fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02
        )
        actual_rows = tuple(
            (item["proposal_status"], item["terminal_state"])
            for item in outcome_rows
        )
        _require_v02(actual_rows == expected_rows, "g2d5_outcome_matrix_mismatch")
        validation_ids = tuple(
            item[key]
            for item in outcome_rows
            for key in (
                "proposal_validation_id",
                "vv_validation_id",
                "gt_validation_id",
                "result_validation_id",
            )
        )
        proof.update(
            outcome_rows=outcome_rows,
            outcome_mapping_rows=fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02,
            outcome_count=len(outcome_rows),
        )
        extra_refs = validation_ids
    elif case_number == 55:
        root_results = tuple(item for item in bundle.cell_results if item.parent_cell_id is None)
        parent_returns = tuple(
            item for item in bundle.transition_decisions
            if item.rule_id == "g2d_t13_completed_to_parent_return"
        )
        _require_v02(len(root_results) == 1 and bool(parent_returns), "g2d5_parent_return_geometry")
        registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
        root_decision = fr.evaluate_fractal_parent_return_transition_v02(
            source_context=bundle.source_context,
            root_result=root_results[0],
            root_result_artifact=bundle.result_artifacts[-1],
            ordered_cell_results=bundle.cell_results,
            transition_registry=registry,
        )
        child_rejection = ""
        try:
            fr.evaluate_fractal_parent_return_transition_v02(
                source_context=bundle.source_context,
                root_result=bundle.cell_results[0],
                root_result_artifact=bundle.result_artifacts[0],
                ordered_cell_results=bundle.cell_results,
                transition_registry=registry,
            )
        except ValueError as exc:
            child_rejection = str(exc)
        _require_v02(
            child_rejection == "g2d_root_result_required_for_parent_return",
            "g2d5_child_parent_return_not_rejected",
        )
        root_final_budgets = tuple(
            item
            for item in bundle.budgets
            if item.owning_cell_id == bundle.topology.root_cell_id
            and item.budget_scope == "ROOT_GLOBAL_AND_CELL"
            and item.budget_state == "FINAL"
        )
        return_rule_ids = tuple(
            item.rule_id
            for item in registry.rules
            if item.rule_id[4:7] in {"t13", "t14", "t15", "t16", "t17"}
        )
        _require_v02(
            len(root_final_budgets) == 1
            and root_decision == parent_returns[-1]
            and len(return_rule_ids) == 5,
            "g2d5_root_return_family_invalid",
        )
        proof.update(
            root_result_id=root_results[0].result_id,
            parent_return_decision_ids=tuple(item.decision_id for item in parent_returns),
            evaluated_root_decision_id=root_decision.decision_id,
            root_final_budget_ids=tuple(item.budget_id for item in root_final_budgets),
            root_return_rule_ids=return_rule_ids,
            child_rejection_reason=child_rejection,
        )
        extra_refs = (root_decision.decision_id,)
    elif case_number == 56:
        artifacts = (
            bundle.topology_artifact,
            *bundle.queue_artifacts,
            *bundle.result_artifacts,
            bundle.report_artifact,
        )
        _require_v02(
            all(abi.validate_kernel_artifact_v01(item) == () for item in artifacts),
            "g2d5_abi_artifact_invalid",
        )
        stage_a, stage_b, stage_c = _stage_artifacts_v02(bundle)
        stage_reports = tuple(
            fr.validate_fractal_runtime_stage_bundle_v02(
                stage=stage,
                artifacts=stage_artifacts,
                source_context=bundle.source_context,
                topology=bundle.topology,
                topology_artifact=bundle.topology_artifact,
                runtime_trace=bundle.runtime_trace,
                queue_entries=bundle.queue_entries,
                queue_artifacts=bundle.queue_artifacts,
                cell_results=bundle.cell_results,
                result_artifacts=bundle.result_artifacts,
                runtime_report=bundle.runtime_report if stage == "STAGE_D_C" else None,
                report_artifact=bundle.report_artifact if stage == "STAGE_D_C" else None,
            )
            for stage, stage_artifacts in zip(
                ("STAGE_D_A", "STAGE_D_B", "STAGE_D_C"),
                (stage_a, stage_b, stage_c),
                strict=True,
            )
        )
        _require_v02(
            all(item.status == "PASS" for item in stage_reports),
            "g2d5_stage_bundle_invalid",
        )
        node_by_id = {item.node_id: item for item in bundle.topology_nodes}
        entry_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
        queue_artifact_by_entry_id = {
            abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"]["queue_entry_id"]: artifact
            for artifact in bundle.queue_artifacts
        }
        form_rows: list[tuple[object, ...]] = []
        for entry in bundle.queue_entries:
            artifact = queue_artifact_by_entry_id[entry.queue_entry_id]
            if entry.predecessor_queue_entry_id is None:
                form = "ROOT_INITIAL" if entry.parent_cell_id is None else "CHILD_INITIAL"
            else:
                node_kind = node_by_id[entry.node_id].node_kind
                if node_kind == "FRACTAL_CELL" and len(artifact.parent_refs) == 3:
                    form = (
                        "INVOKED_CHILD_T06_VALIDATING"
                        if entry.state == "VALIDATING"
                        else "INVOKED_CHILD_T08_T12_TERMINAL"
                    )
                else:
                    predecessor = entry_by_id[entry.predecessor_queue_entry_id]
                    form = (
                        "ORDINARY_ROOT_SUCCESSOR"
                        if predecessor.parent_cell_id is None
                        else "ORDINARY_CHILD_SUCCESSOR"
                    )
            form_rows.append(
                (form, entry.queue_entry_id, artifact.artifact_id, artifact.parent_refs)
            )
        form_names = tuple(
            name
            for name in (
                "ROOT_INITIAL",
                "CHILD_INITIAL",
                "ORDINARY_ROOT_SUCCESSOR",
                "ORDINARY_CHILD_SUCCESSOR",
                "INVOKED_CHILD_T06_VALIDATING",
                "INVOKED_CHILD_T08_T12_TERMINAL",
            )
            if any(row[0] == name for row in form_rows)
        )
        _require_v02(len(form_names) == 6, "g2d5_queue_parent_forms_missing")
        proof.update(
            artifact_ids=tuple(item.artifact_id for item in artifacts),
            artifact_types=tuple(item.artifact_type for item in artifacts),
            trace_unique=all(len(item.trace_refs) == len(set(item.trace_refs)) for item in artifacts),
            field_partitions=(
                len(fields(fr.FractalCellInputV02)),
                len(fields(fr.FractalCellQueueEntryV02)),
                len(fields(fr.FractalCellResultV02)),
                len(fields(fr.FractalRuntimeReportV02)),
            ),
            stage_artifact_counts=(len(stage_a), len(stage_b), len(stage_c)),
            stage_validation_ids=tuple(item.validation_report_id for item in stage_reports),
            queue_parent_form_names=form_names,
            queue_parent_form_rows=tuple(form_rows),
            queue_reason_field_exact=all(
                "queue_reason_codes" in abi.kernel_artifact_to_plain_dict_v01(item)["payload"]
                and "reason_codes" not in abi.kernel_artifact_to_plain_dict_v01(item)["payload"]
                for item in bundle.queue_artifacts
            ),
        )
        extra_refs = tuple(item.validation_report_id for item in stage_reports)
    elif case_number == 57:
        rows = tuple(
            (
                item.source_artifact_id,
                item.output_field,
                item.downstream_artifact_id,
                item.disposition,
                item.reason_code,
            )
            for item in bundle.causal_consumption_refs
        )
        _require_v02(
            all(pointer.startswith("/") and ":" in reason for _, pointer, _, _, reason in rows),
            "g2d5_causal_pointer_reason_invalid",
        )
        causal_report = _causal_validation_report_v02(bundle)
        _require_pass_v02(causal_report, label="g2d5_causal_rows")
        corrupt_entry = replace(bundle.queue_entries[0], queue_entry_id="frqueue_v02:" + "0" * 64)
        corrupt_report = fr.validate_fractal_runtime_execution_bundle_v02(
            replace(bundle, queue_entries=(corrupt_entry, *bundle.queue_entries[1:]))
        )
        _require_v02(
            corrupt_report.status == "FAIL_CLOSED",
            "g2d5_causal_corruption_accepted",
        )
        proof.update(
            causal_pointer_reason_rows=rows,
            causal_validation_id=causal_report.validation_report_id,
            terminal_causal_row_count=sum(
                item.decision_effect == "CELL_TERMINAL_OUTCOME"
                for item in bundle.causal_consumption_refs
            ),
            activation_causal_row_count=sum(
                item.decision_effect == "CHILD_ACTIVATION"
                for item in bundle.causal_consumption_refs
            ),
            child_return_causal_row_count=sum(
                item.decision_effect == "CHILD_RESULT_RETURN_BINDING"
                for item in bundle.causal_consumption_refs
            ),
            corruption_validation_id=corrupt_report.validation_report_id,
            corruption_reason_codes=corrupt_report.reason_codes,
            corruption_causal_delta=_created_set_delta_v02(
                tuple(_sha256_plain_v02(item) for item in bundle.causal_consumption_refs),
                tuple(_sha256_plain_v02(item) for item in bundle.causal_consumption_refs),
            ),
        )
        extra_refs = (
            causal_report.validation_report_id,
            corrupt_report.validation_report_id,
        )
    elif case_number == 58:
        witness = shared["backpressure_witness"]
        budget_witness = shared["budget_exhaustion_witness"]
        if (
            type(witness) is not _BackpressureWitnessV02
            or type(budget_witness) is not _BudgetExhaustionWitnessV02
        ):
            raise TypeError("g2d5_shared_boundary_witness_invalid")
        rows = tuple(
            (
                item.backpressure_id,
                item.evaluated_round,
                item.queue_capacity,
                item.running_count,
                item.ready_count,
                item.pending_count,
                item.admission_order,
                item.deferred_queue_entry_ids,
                item.backpressure_reason,
            )
            for item in (witness.s0, witness.s1)
        )
        state_reports = (witness.s0_validation, witness.s1_validation)
        successor_rows = (
            (
                witness.first_t03_decision.decision_id,
                witness.deferred_source.queue_entry_id,
                witness.first_deferred.queue_entry_id,
                witness.first_deferred_artifact.artifact_id,
                witness.first_deferred.admission_round,
                witness.first_deferred.state,
                witness.first_deferred.queue_reason_codes,
            ),
            (
                witness.second_t03_decision.decision_id,
                witness.first_deferred.queue_entry_id,
                witness.second_deferred.queue_entry_id,
                witness.second_deferred_artifact.artifact_id,
                witness.second_deferred.admission_round,
                witness.second_deferred.state,
                witness.second_deferred.queue_reason_codes,
            ),
        )
        _require_v02(
            all(item.status == "PASS" for item in state_reports)
            and len({row[1] for row in rows}) == 2
            and all(item.no_work_dropped for item in (witness.s0, witness.s1))
            and all(row[5] == "PENDING" for row in successor_rows),
            "g2d5_backpressure_witness_invalid",
        )
        proof.update(
            backpressure_precedence_rows=rows,
            backpressure_validation_ids=tuple(
                item.validation_report_id for item in state_reports
            ),
            deferred_successor_rows=successor_rows,
            dependency_wait_row=(
                witness.dependency_wait.queue_entry_id,
                witness.dependency_wait_validation.validation_report_id,
                witness.dependency_wait.state,
                witness.dependency_wait.queue_reason_codes,
                witness.dependency_wait_decision_is_none,
            ),
            budget_blocked_row=(
                budget_witness.blocked_entry.queue_entry_id,
                budget_witness.blocked_artifact.artifact_id,
                budget_witness.blocked_validation.validation_report_id,
                budget_witness.blocked_entry.state,
                budget_witness.blocked_entry.queue_reason_codes,
                budget_witness.terminal_decision.decision_id,
                budget_witness.exhausted_budget.budget_id,
                budget_witness.exhausted_validation.validation_report_id,
                budget_witness.t06_decision.decision_id,
            ),
            budget_exhaustion_resource="remaining_cell_count",
            budget_exhaustion_tree_shape=budget_witness.tree_shape,
            budget_exhaustion_depth_counts=dict(budget_witness.depth_counts),
            budget_exhaustion_accepted_cell_ids=(
                budget_witness.accepted_cell_ids
            ),
            budget_before_id=budget_witness.budget_before.budget_id,
            budget_before_consumed_cell_count=(
                budget_witness.budget_before.consumed_cell_count
            ),
            budget_before_remaining_cell_count=(
                budget_witness.budget_before.remaining_cell_count
            ),
            exhausted_budget_id=budget_witness.exhausted_budget.budget_id,
            exhausted_budget_validation_id=(
                budget_witness.exhausted_validation.validation_report_id
            ),
            exhausted_consumed_cell_count=(
                budget_witness.exhausted_budget.consumed_cell_count
            ),
            exhausted_remaining_cell_count=(
                budget_witness.exhausted_budget.remaining_cell_count
            ),
            budget_exhaustion_t06_decision_id=(
                budget_witness.t06_decision.decision_id
            ),
            budget_exhaustion_terminal_decision_id=(
                budget_witness.terminal_decision.decision_id
            ),
            budget_exhaustion_queue_delta=_created_set_delta_v02(
                budget_witness.queue_before_ids,
                budget_witness.queue_after_ids,
            ),
            budget_exhaustion_budget_delta=_created_set_delta_v02(
                budget_witness.budget_before_ids,
                budget_witness.budget_after_ids,
            ),
            budget_exhaustion_no_drop=(
                budget_witness.queue_after_ids[
                    : len(budget_witness.queue_before_ids)
                ]
                == budget_witness.queue_before_ids
            ),
            unique_state_per_round=(
                len({item.evaluated_round for item in (witness.s0, witness.s1)})
                == 2
            ),
            unchanged_t03_suppressed=(
                witness.suppression_before_ids == witness.suppression_after_ids
            ),
            suppression_created_objects=_created_set_delta_v02(
                witness.suppression_before_ids,
                witness.suppression_after_ids,
            ),
            no_work_dropped=(witness.s0.no_work_dropped and witness.s1.no_work_dropped),
            runtime_queue_order=witness.queue_order,
            queue_order_error=witness.queue_order_error,
        )
        extra_refs = (
            *(item.validation_report_id for item in state_reports),
            witness.s0.backpressure_id,
            witness.s1.backpressure_id,
            *(row[0] for row in successor_rows),
            *(row[2] for row in successor_rows),
            *(row[3] for row in successor_rows),
            witness.dependency_wait.queue_entry_id,
            witness.dependency_wait_validation.validation_report_id,
            budget_witness.budget_before.budget_id,
            *budget_witness.accepted_cell_ids,
            budget_witness.exhausted_budget.budget_id,
            budget_witness.exhausted_validation.validation_report_id,
            budget_witness.t06_decision.decision_id,
            budget_witness.blocked_entry.queue_entry_id,
            budget_witness.blocked_artifact.artifact_id,
            budget_witness.blocked_validation.validation_report_id,
            budget_witness.terminal_decision.decision_id,
        )
    elif case_number == 59:
        policy_rows = tuple(
            (
                item.mode,
                item.source_context.runtime_policy.policy_profile_id,
                item.source_context.runtime_policy.policy_id,
                item.bundle.source_binding.source_binding_id,
                item.bundle.source_binding.runtime_policy_id,
            )
            for item in accepted[:5]
        )
        _require_v02(
            len({row[1] for row in policy_rows}) == 1
            and len({row[2] for row in policy_rows}) == 5,
            "g2d5_policy_identity_alias",
        )
        base = accepted[0]
        donor = accepted[1]
        invalid_source = replace(
            base.source_context,
            runtime_policy=donor.source_context.runtime_policy,
        )
        substitution_report = fr.validate_fractal_runtime_source_context_v02(
            invalid_source
        )
        _require_v02(
            substitution_report.status == "FAIL_CLOSED",
            "g2d5_policy_substitution_accepted",
        )
        proof.update(
            policy_profile_separation=policy_rows,
            profile_count=len({row[1] for row in policy_rows}),
            policy_identity_count=len({row[2] for row in policy_rows}),
            source_binding_identity_count=len({row[3] for row in policy_rows}),
            substitution_validation_id=substitution_report.validation_report_id,
            substitution_reason_codes=substitution_report.reason_codes,
        )
        extra_refs = (substitution_report.validation_report_id,)
    elif case_number == 60:
        node_index = {
            item.node_id: item.canonical_index for item in bundle.topology_nodes
        }
        edge_rows = tuple(
            (
                item.canonical_index,
                node_index[item.source_node_id],
                node_index[item.target_node_id],
                item.edge_kind,
                item.cell_projection_class,
                item.edge_id,
            )
            for item in bundle.topology_edges
            if item.cell_projection_class == "FRACTAL_LEAF_PROJECTION"
        )
        _require_v02(
            tuple(row[:5] for row in edge_rows)
            == (
                (7, 0, 4, "VALIDATION", "FRACTAL_LEAF_PROJECTION"),
                (8, 4, 5, "VALIDATION", "FRACTAL_LEAF_PROJECTION"),
                (9, 5, 6, "RETURN", "FRACTAL_LEAF_PROJECTION"),
            ),
            "g2d5_leaf_edge_projection_geometry",
        )
        root_rows = tuple(
            (
                item.canonical_index,
                node_index[item.source_node_id],
                node_index[item.target_node_id],
                item.edge_kind,
                item.cell_projection_class,
            )
            for item in bundle.topology_edges
            if item.cell_projection_class == "ROOT_CELL_PROJECTION"
        )
        topology_report = fr.validate_runtime_execution_topology_against_sources_v02(
            bundle.topology,
            source_context=bundle.source_context,
        )
        _require_v02(
            tuple(row[0] for row in root_rows) == tuple(range(7))
            and topology_report.status == "PASS",
            "g2d5_root_edge_projection_geometry",
        )
        proof.update(
            full_fractal_root_edges=root_rows,
            full_fractal_leaf_edges=edge_rows,
            leaf_source_target_indexes=((0, 4), (4, 5), (5, 6)),
            leaf_edge_kinds=("VALIDATION", "VALIDATION", "RETURN"),
            topology_validation_id=topology_report.validation_report_id,
        )
        extra_refs = (topology_report.validation_report_id,)
    elif case_number == 61:
        rows = tuple(
            (
                item.budget_id,
                item.budget_scope,
                item.budget_state,
                item.budget_event_kind,
                item.budget_event_ref,
            )
            for item in bundle.budgets
        )
        event_refs = {row[4] for row in rows}
        budget_reports = tuple(
            fr.validate_fractal_runtime_budget_v02(item) for item in bundle.budgets
        )
        paired_rows = tuple(
            (
                cell.budget_id,
                global_budget.budget_id,
                cell.budget_event_kind,
                cell.budget_event_ref,
                cell.owning_cell_id,
            )
            for index, cell in enumerate(bundle.budgets[:-1])
            for global_budget in bundle.budgets[index + 1:index + 2]
            if cell.budget_scope == "CHILD_CELL_LOCAL"
            and global_budget.budget_scope == "ROOT_GLOBAL_AND_CELL"
            and cell.budget_event_kind == global_budget.budget_event_kind
            and cell.budget_event_ref == global_budget.budget_event_ref
        )
        baseline_rows = tuple(
            item for item in bundle.budgets if item.predecessor_budget_id is not None
        )
        _require_v02(bool(baseline_rows), "g2d5_budget_pair_basis_missing")
        baseline = baseline_rows[0]
        mutations = (
            ("stale_pair", {"budget_event_ref": "frtransition_v02:" + "0" * 64}),
            ("missing_pair", {"predecessor_budget_id": None}),
            ("forged_pair", {"allocation_parent_budget_id": "frbudget_v02:" + "0" * 64}),
        )
        mutation_rows: list[tuple[object, ...]] = []
        mutation_reports: list[fr.FractalRuntimeValidationReportV02] = []
        position = bundle.budgets.index(baseline)
        for axis, changes in mutations:
            mutated = _reidentified_v02(
                replace(baseline, **changes),
                identity_field="budget_id",
                rebuild=fr.rebuild_fractal_runtime_budget_identity_v02,
            )
            report = fr.validate_fractal_runtime_execution_bundle_v02(
                replace(
                    bundle,
                    budgets=(
                        *bundle.budgets[:position],
                        mutated,
                        *bundle.budgets[position + 1:],
                    ),
                )
            )
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_budget_pair_mutation_accepted")
            mutation_rows.append((axis, report.validation_report_id, report.reason_codes))
            mutation_reports.append(report)
        _require_v02(
            bool(event_refs)
            and bool(paired_rows)
            and all(item.status == "PASS" for item in budget_reports),
            "g2d5_budget_events_missing",
        )
        proof.update(
            cell_global_event_pairing=rows,
            paired_event_rows=paired_rows,
            budget_validation_ids=tuple(
                item.validation_report_id for item in budget_reports
            ),
            create_only_debit_rows=tuple(
                (item.budget_id, item.consumed_cell_count)
                for item in bundle.budgets
                if item.budget_event_kind == "CELL_CREATE"
            ),
            zero_delta_aggregate_rows=tuple(
                (item.budget_id, item.budget_event_ref, item.consumed_cell_count)
                for item in bundle.budgets
                if item.budget_event_kind == "CHILD_AGGREGATE"
            ),
            mutation_rows=tuple(mutation_rows),
        )
        extra_refs = (
            *(item.validation_report_id for item in budget_reports),
            *(item.validation_report_id for item in mutation_reports),
        )
    elif case_number == 62:
        outcome_rows = shared["outcome_rows"]
        if type(outcome_rows) is not tuple:
            raise TypeError("g2d5_outcome_rows_invalid")
        outcome_lifecycles = tuple(
            (
                item["terminal_state"],
                item["result_id"],
                item["result_artifact_id"],
                item["result_artifact_lifecycle"],
            )
            for item in outcome_rows
        )
        _require_v02(
            tuple((row[0], row[3]) for row in outcome_lifecycles)
            == (
                ("COMPLETED", "VALIDATED"),
                ("DEGRADED", "VALIDATED"),
                ("BLOCKED", "BLOCKED_FAIL_CLOSED"),
                ("NEEDS_USER", "VALIDATED"),
                ("DEADEND", "VALIDATED"),
            ),
            "g2d5_pre_root_lifecycle_invalid",
        )
        pre_root_rows = tuple(
            (item.artifact_id, item.artifact_type, item.lifecycle_state, item.authority_class)
            for item in bundle.result_artifacts
        )
        forbidden_lifecycles = {"ROOT_REVIEWED", "ACCEPTED", "REJECTED"}
        _require_v02(
            all(row[2] not in forbidden_lifecycles for row in pre_root_rows),
            "g2d5_root_lifecycle_leak",
        )
        proof.update(
            pre_root_lifecycle=pre_root_rows,
            outcome_lifecycle_rows=outcome_lifecycles,
            forbidden_root_lifecycles=tuple(sorted(forbidden_lifecycles)),
            final_output_created=bundle.runtime_report.final_outputs_created,
        )
        extra_refs = tuple(item["result_artifact_id"] for item in outcome_rows)
    elif case_number == 63:
        gt_rows = tuple(
            (
                proposal["proposal_id"],
                vv_report["vv_report_id"],
                gt_report["gt_report_id"],
                gt_report["decision"],
                gt_report["created_at"],
            )
            for proposal, vv_report, gt_report in zip(
                bundle.result_proposals,
                bundle.post_vv_reports,
                bundle.gt_advisory_reports,
                strict=True,
            )
        )
        gt_ids = tuple(row[2] for row in gt_rows)
        _require_v02(len(gt_ids) == len(set(gt_ids)), "g2d5_gt_id_collision")
        gt_validations = tuple(
            fr.validate_fractal_gt_advisory_v02(
                gt_report,
                post_vv_report=vv_report,
                source_context=bundle.source_context,
            )
            for vv_report, gt_report in zip(
                bundle.post_vv_reports,
                bundle.gt_advisory_reports,
                strict=True,
            )
        )
        _require_v02(
            all(item.status == "PASS" for item in gt_validations),
            "g2d5_gt_context_invalid",
        )
        substitution = fr.validate_fractal_gt_advisory_v02(
            bundle.gt_advisory_reports[0],
            post_vv_report=bundle.post_vv_reports[-1],
            source_context=bundle.source_context,
        )
        _require_v02(
            substitution.status == "FAIL_CLOSED",
            "g2d5_gt_context_substitution_accepted",
        )
        proof.update(
            context_unique_gt_rows=gt_rows,
            gt_validation_ids=tuple(
                item.validation_report_id for item in gt_validations
            ),
            substitution_validation_id=substitution.validation_report_id,
            substitution_reason_codes=substitution.reason_codes,
            result_gt_refs=tuple(item.gt_advisory_ref for item in bundle.cell_results),
        )
        extra_refs = (
            *(item.validation_report_id for item in gt_validations),
            substitution.validation_report_id,
        )
    elif case_number == 64:
        rows = tuple(
            (item.validation_report_id, item.status, item.failure_stage, item.reason_codes)
            for item in bundle.validation_reports
        )
        _require_v02(
            all(status != "PASS" or (stage == "NONE" and reasons == ())
                for _, status, stage, reasons in rows),
            "g2d5_pass_none_stage_contract",
        )
        pass_report = fr.build_fractal_runtime_validation_report_v02(
            validation_target="FractalRuntimePolicyV02",
            validated_object_id=bundle.source_context.runtime_policy.policy_id,
            failure_stage="NONE",
            reason_codes=(),
            source_reason_codes=(),
        )
        failure_report = fr.build_fractal_runtime_validation_report_v02(
            validation_target="FractalRuntimePolicyV02",
            validated_object_id=None,
            failure_stage="POLICY",
            reason_codes=("g2d_topology_policy_invalid",),
            source_reason_codes=(),
        )
        _require_v02(
            fr.validate_fractal_runtime_validation_report_v02(pass_report) == ()
            and fr.validate_fractal_runtime_validation_report_v02(failure_report) == ()
            and len(fr.VALIDATION_TARGETS) == 34
            and len(fr.FAILURE_STAGES) == 30,
            "g2d5_validation_geometry_invalid",
        )
        proof.update(
            validation_status_stage_rows=rows,
            validation_targets=fr.VALIDATION_TARGETS,
            failure_stages=fr.FAILURE_STAGES,
            validation_target_count=len(fr.VALIDATION_TARGETS),
            failure_stage_count=len(fr.FAILURE_STAGES),
            explicit_pass_report_id=pass_report.validation_report_id,
            explicit_failure_report_id=failure_report.validation_report_id,
            explicit_failure_reason_codes=failure_report.reason_codes,
            causal_profile_sha256=_sha256_plain_v02(bundle.causal_consumption_refs),
        )
        extra_refs = (
            pass_report.validation_report_id,
            failure_report.validation_report_id,
        )
    elif case_number == 65:
        rows = tuple(
            (
                item.queue_entry_id,
                item.node_instance_sequence,
                item.snapshot_sequence,
                item.admission_round,
                item.state,
                item.queue_reason_codes,
            )
            for item in bundle.queue_entries
        )
        _require_v02(
            all(snapshot >= 0 and round_value >= 0 for _, _, snapshot, round_value, _, _ in rows),
            "g2d5_queue_snapshot_invalid",
        )
        queue_reports = tuple(
            fr.validate_fractal_cell_queue_entry_v02(item)
            for item in bundle.queue_entries
        )
        _require_v02(
            all(item.status == "PASS" for item in queue_reports),
            "g2d5_queue_row_invalid",
        )
        completed_positions = tuple(
            index
            for index, item in enumerate(bundle.queue_entries)
            if item.state == "COMPLETED"
        )
        _require_v02(bool(completed_positions), "g2d5_completed_queue_missing")
        queue_position = completed_positions[0]
        queue = bundle.queue_entries[queue_position]
        copied_reason = _reidentified_v02(
            replace(queue, queue_reason_codes=("g2d_required_child_failure",)),
            identity_field="queue_entry_id",
            rebuild=fr.rebuild_fractal_cell_queue_entry_identity_v02,
        )
        reason_report = fr.validate_fractal_runtime_execution_bundle_v02(
            replace(
                bundle,
                queue_entries=(
                    *bundle.queue_entries[:queue_position],
                    copied_reason,
                    *bundle.queue_entries[queue_position + 1:],
                ),
            )
        )
        proposal_mutation = json.loads(
            canonical_json_bytes_v01(bundle.result_proposals[0]).decode("ascii")
        )
        proposal_mutation["result_payload"]["status"] = "blocked"
        proposal_context = _result_context_v02(bundle, bundle.cell_results[0])
        proposal_report = fr.validate_fractal_cell_result_proposal_v02(
            proposal_mutation,
            source_context=run.source_context,
            topology=bundle.topology,
            cell_input=proposal_context["cell_input"],
            pre_post_vv_terminal_queue_entries=(
                proposal_context["pre_post_vv_entries"]
            ),
            child_results=proposal_context["child_results"],
            partial_failures=proposal_context["partial_failures"],
        )
        _require_v02(
            reason_report.status == proposal_report.status == "FAIL_CLOSED",
            "g2d5_copied_terminal_signal_accepted",
        )
        proof.update(
            instance_snapshot_round_reason_rows=rows,
            queue_validation_ids=tuple(
                item.validation_report_id for item in queue_reports
            ),
            blocked_reason_rows=tuple(
                (item.queue_entry_id, item.queue_reason_codes)
                for item in bundle.queue_entries
                if item.state == "BLOCKED"
            ),
            copied_queue_reason_validation_id=reason_report.validation_report_id,
            copied_queue_reason_codes=reason_report.reason_codes,
            copied_proposal_status_validation_id=proposal_report.validation_report_id,
            copied_proposal_status_reason_codes=proposal_report.reason_codes,
            rejected_copied_signal_count=sum(
                item.status == "FAIL_CLOSED"
                for item in (reason_report, proposal_report)
            ),
        )
        extra_refs = (
            *(item.validation_report_id for item in queue_reports),
            reason_report.validation_report_id,
            proposal_report.validation_report_id,
        )
    elif case_number == 66:
        input_rows = tuple(
            (
                item.cell_input_id,
                item.parent_cell_id,
                item.ordered_planned_child_cell_ids,
                item.ordered_node_ids,
            )
            for item in bundle.cell_inputs
        )
        result_position = {
            item.result_id: index for index, item in enumerate(bundle.cell_results)
        }
        root_result = bundle.cell_results[-1]
        child_before_root = tuple(
            result_position[item] < result_position[root_result.result_id]
            for item in root_result.ordered_child_result_ids
        )
        node_by_id = {item.node_id: item for item in bundle.topology_nodes}
        slot_rows = tuple(
            (
                item.queue_entry_id,
                item.cell_id,
                item.planned_child_cell_id,
                item.state,
                item.snapshot_sequence,
            )
            for item in bundle.queue_entries
            if node_by_id[item.node_id].node_kind == "FRACTAL_CELL"
        )
        merge_rows = tuple(
            (item.queue_entry_id, item.state, item.snapshot_sequence)
            for item in bundle.queue_entries
            if node_by_id[item.node_id].node_kind == "FRACTAL_MERGE"
        )
        gate = shared["gate_witness"]
        if type(gate) is not _GateBoundaryWitnessV02:
            raise TypeError("g2d5_case66_gate_witness_invalid")
        _require_v02(
            all(child_before_root)
            and bool(slot_rows)
            and bool(merge_rows)
            and gate.blocked_entry.state == "BLOCKED"
            and gate.blocked_validation.status == "PASS"
            and gate.merge_validation.status == "PASS"
            and gate.merge_decision_is_none,
            "g2d5_child_merge_order_invalid",
        )
        proof.update(
            child_slot_input_node_order=input_rows,
            cell_result_order=tuple(item.result_id for item in bundle.cell_results),
            child_results_before_root=child_before_root,
            parent_slot_rows=slot_rows,
            merge_rows=merge_rows,
            denied_slot_terminal_id=gate.blocked_entry.queue_entry_id,
            denied_slot_artifact_id=gate.blocked_artifact.artifact_id,
            denied_slot_validation_id=gate.blocked_validation.validation_report_id,
            denied_slot_state=gate.blocked_entry.state,
            denied_gate_disposition=gate.gate_disposition,
            denied_gate_reason_codes=gate.gate_reason_codes,
            denied_gate_evidence_refs=gate.gate_evidence_refs,
            denied_t06_decision_id=gate.t06_decision.decision_id,
            denied_terminal_decision_id=gate.terminal_decision.decision_id,
            denied_terminal_delta=_created_set_delta_v02(
                gate.denial_terminal_before_ids,
                gate.denial_terminal_after_ids,
            ),
            denied_invocation_delta=_created_set_delta_v02(
                gate.invocation_before_ids,
                gate.invocation_after_ids,
            ),
            denied_result_delta=_created_set_delta_v02(
                gate.result_before_ids,
                gate.result_after_ids,
            ),
            denied_partial_failure_delta=_created_set_delta_v02(
                gate.partial_before_ids,
                gate.partial_after_ids,
            ),
            merge_validation_id=gate.merge_validation.validation_report_id,
            merge_decision_is_none=gate.merge_decision_is_none,
            child_invocation_count=len(
                tuple(item for item in bundle.cell_inputs if item.parent_cell_id is not None)
            ),
        )
        extra_refs = (
            *gate.gate_evidence_refs,
            gate.t06_decision.decision_id,
            gate.terminal_decision.decision_id,
            gate.blocked_entry.queue_entry_id,
            gate.blocked_artifact.artifact_id,
            gate.blocked_validation.validation_report_id,
            gate.merge_entry.queue_entry_id,
            gate.merge_validation.validation_report_id,
        )
    elif case_number == 67:
        root_result = _exactly_one_v02(
            tuple(item for item in bundle.cell_results if item.parent_cell_id is None),
            label="g2d5_surface_root_result",
        )
        if type(root_result) is not fr.FractalCellResultV02:
            raise TypeError("g2d5_surface_root_result_type_invalid")
        _require_v02(
            bundle.runtime_report.ordered_cell_result_ids[-1] == root_result.result_id,
            "g2d5_root_report_result_mismatch",
        )
        proof.update(
            root_result_id=root_result.result_id,
            runtime_report_id=bundle.runtime_report.report_id,
            report_artifact_id=bundle.report_artifact.artifact_id,
            runtime_outcome=bundle.runtime_report.runtime_outcome,
            public_return_bundle_type=type(bundle).__name__,
            terminal_report_target=run.external_report.validation_target,
            terminal_report_status=run.external_report.status,
            root_owned_outcome=(
                bundle.runtime_report.runtime_outcome == root_result.outcome
            ),
            staged_public_function_counts=(
                fr.D1_MODULE_PUBLIC_FUNCTION_COUNT,
                fr.D2_MODULE_PUBLIC_FUNCTION_COUNT,
                fr.D3_MODULE_PUBLIC_FUNCTION_COUNT,
                fr.D4_MODULE_PUBLIC_FUNCTION_COUNT,
            ),
            module_public_function_count=fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT,
        )
        extra_refs = (bundle.report_artifact.artifact_id,)
    elif case_number == 68:
        two_child_rows = tuple(
            (
                item.projection_id,
                item.child_cell_id,
                item.parent_budget_id,
                item.child_budget_id,
                item.global_budget_id,
                item.child_depth,
            )
            for item in bundle.scope_projections
        )
        (
            four_child_rows,
            four_child_context_report,
            four_child_derivation_rows,
        ) = _isolated_four_child_allocations_v02(run)
        _require_v02(
            len(two_child_rows) == 2
            and len(four_child_rows) == 4
            and len({item["allocation_parent_budget_id"] for item in four_child_rows}) == 1,
            "g2d5_child_allocation_missing",
        )
        basis_id = four_child_rows[0]["allocation_parent_budget_id"]
        proof.update(
            two_child_runtime_rows=two_child_rows,
            four_child_structural_rows=four_child_rows,
            four_child_parent_basis_id=basis_id,
            four_child_index_order=tuple(
                item["canonical_child_index"] for item in four_child_rows
            ),
            four_child_cell_share_sum=sum(
                item["max_total_cells"] for item in four_child_rows
            ),
            four_child_revise_share_sum=sum(
                item["max_revise_count"] for item in four_child_rows
            ),
            four_child_context_validation_id=(
                four_child_context_report.validation_report_id
            ),
            four_child_context_validation_status=four_child_context_report.status,
            four_child_context_reason_codes=four_child_context_report.reason_codes,
            four_child_runtime_projection_count=int(
                four_child_context_report.status == "PASS"
            ),
            four_child_derivation_rows=four_child_derivation_rows,
        )
        extra_refs = tuple(
            value
            for item in four_child_rows
            for value in (item["budget_id"], item["budget_validation_id"])
        ) + (four_child_context_report.validation_report_id,)
    elif case_number == 69:
        rows = tuple(
            item for item in bundle.causal_consumption_refs
            if item.decision_effect == "CHILD_ACTIVATION"
        )
        child_ids = tuple(
            item.cell_id for item in bundle.cell_inputs if item.parent_cell_id is not None
        )
        _require_v02(len(rows) == len(child_ids) == 2, "g2d5_child_activation_count")
        root_input = _exactly_one_v02(
            tuple(item for item in bundle.cell_inputs if item.parent_cell_id is None),
            label="g2d5_activation_root_input",
        )
        if type(root_input) is not fr.FractalCellInputV02:
            raise TypeError("g2d5_activation_root_input_type_invalid")
        budget_by_id = {item.budget_id: item for item in bundle.budgets}
        planning_basis = budget_by_id[root_input.cell_budget_id]
        create_rows = tuple(
            (
                item.budget_id,
                item.budget_event_ref,
                item.consumed_cell_count,
                item.remaining_cell_count,
            )
            for item in bundle.budgets
            if item.budget_event_kind == "CELL_CREATE"
        )
        gate = shared["gate_witness"]
        if type(gate) is not _GateBoundaryWitnessV02:
            raise TypeError("g2d5_case69_gate_witness_invalid")
        malformed = _reidentified_v02(
            replace(
                root_input,
                requested_child_count=root_input.requested_child_count + 1,
            ),
            identity_field="cell_input_id",
            rebuild=fr.rebuild_fractal_cell_input_identity_v02,
        )
        malformed_report = fr.validate_fractal_cell_input_v02(malformed)
        _require_v02(
            malformed_report.status == "FAIL_CLOSED",
            "g2d5_malformed_activation_candidate_accepted",
        )
        proof.update(
            planned_child_ids=root_input.ordered_planned_child_cell_ids,
            planned_basis_consumed_cell_count=planning_basis.consumed_cell_count,
            activated_child_ids=child_ids,
            activation_rows=rows,
            first_initial_downstreams=tuple(item.downstream_artifact_id for item in rows),
            accepted_cell_create_rows=create_rows,
            valid_denial_disposition=gate.gate_disposition,
            valid_denial_queue_id=gate.blocked_entry.queue_entry_id,
            valid_denial_artifact_id=gate.blocked_artifact.artifact_id,
            valid_denial_validation_id=gate.blocked_validation.validation_report_id,
            valid_denial_invocation_delta=_created_set_delta_v02(
                gate.invocation_before_ids,
                gate.invocation_after_ids,
            ),
            malformed_candidate_validation_id=malformed_report.validation_report_id,
            malformed_candidate_reason_codes=malformed_report.reason_codes,
            malformed_candidate_created_terminals=_created_set_delta_v02(
                tuple(item.queue_entry_id for item in bundle.queue_entries if item.state in fr.NODE_TERMINAL_OUTCOMES),
                tuple(item.queue_entry_id for item in bundle.queue_entries if item.state in fr.NODE_TERMINAL_OUTCOMES),
            ),
        )
        extra_refs = (
            *gate.gate_evidence_refs,
            gate.blocked_entry.queue_entry_id,
            gate.blocked_artifact.artifact_id,
            gate.blocked_validation.validation_report_id,
            malformed_report.validation_report_id,
        )
    elif case_number == 70:
        decision_ids = tuple(item.decision_id for item in bundle.transition_decisions)
        _require_v02(
            bundle.runtime_trace.transition_refs == decision_ids,
            "g2d5_transition_trace_order",
        )
        registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
        root_return = fr.evaluate_fractal_parent_return_transition_v02(
            source_context=bundle.source_context,
            root_result=bundle.cell_results[-1],
            root_result_artifact=bundle.result_artifacts[-1],
            ordered_cell_results=bundle.cell_results,
            transition_registry=registry,
        )
        root_result = bundle.cell_results[-1]
        context = _result_context_v02(bundle, root_result)
        result_index = bundle.cell_results.index(root_result)
        proposal = bundle.result_proposals[result_index]
        post_vv_report = bundle.post_vv_reports[result_index]
        gt_report = bundle.gt_advisory_reports[result_index]
        signature_90_reports = (
            fr.validate_fractal_cell_result_proposal_v02(
                proposal,
                source_context=run.source_context,
                topology=bundle.topology,
                cell_input=context["cell_input"],
                pre_post_vv_terminal_queue_entries=context["pre_post_vv_entries"],
                child_results=context["child_results"],
                partial_failures=context["partial_failures"],
            ),
            fr.validate_fractal_post_vv_report_v02(
                post_vv_report,
                result_proposal=proposal,
                source_context=run.source_context,
            ),
            fr.validate_fractal_gt_advisory_v02(
                gt_report,
                post_vv_report=post_vv_report,
                source_context=run.source_context,
            ),
        )
        _require_v02(
            all(item.status == "PASS" for item in signature_90_reports),
            "g2d5_parent_return_typed_family_invalid",
        )
        terminal_queue_id = root_result.ordered_terminal_queue_entry_ids[-1]
        queue_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
        terminal_queue = queue_by_id[terminal_queue_id]
        decision_by_id = {
            item.decision_id: item for item in bundle.transition_decisions
        }
        parent_return = decision_by_id[terminal_queue.transition_decision_id]
        decision_position = bundle.transition_decisions.index(parent_return)
        root_return_position = bundle.transition_decisions.index(root_return)
        root_completion_budget_ids = {
            root_result.final_cell_budget_id,
            root_result.global_budget_id,
        }
        paired_budget_positions = tuple(
            index
            for index, item in enumerate(bundle.budgets)
            if item.budget_id in root_completion_budget_ids
            and item.budget_event_ref == parent_return.decision_id
        )
        queue_positions = tuple(
            index
            for index, item in enumerate(bundle.queue_entries)
            if item.queue_entry_id == terminal_queue.queue_entry_id
        )
        queue_artifact_by_id = {
            abi.kernel_artifact_to_plain_dict_v01(item)["payload"]["queue_entry_id"]: item
            for item in bundle.queue_artifacts
        }
        terminal_artifact = queue_artifact_by_id[terminal_queue_id]
        completion_budgets = tuple(
            bundle.budgets[index] for index in paired_budget_positions
        )
        _require_v02(
            parent_return.rule_id == "g2d_t08_validating_to_completed",
            "g2d5_parent_return_prestate_rule_invalid",
        )
        _require_v02(
            tuple(queue_positions) == (bundle.queue_entries.index(terminal_queue),),
            "g2d5_parent_return_prestate_queue_invalid",
        )
        _require_v02(
            bool(paired_budget_positions),
            "g2d5_parent_return_prestate_budget_missing",
        )
        _require_v02(
            all(
                item.budget_event_ref == parent_return.decision_id
                for item in completion_budgets
            ),
            "g2d5_parent_return_prestate_budget_event_invalid",
        )
        _require_v02(
            terminal_queue.transition_decision_id == parent_return.decision_id,
            "g2d5_parent_return_prestate_decision_binding_invalid",
        )
        _require_v02(
            root_result.final_cell_budget_id
            in {item.budget_id for item in completion_budgets},
            "g2d5_parent_return_prestate_cell_budget_invalid",
        )
        _require_v02(
            root_result.global_budget_id
            in {item.budget_id for item in completion_budgets},
            "g2d5_parent_return_prestate_global_budget_invalid",
        )
        _require_v02(
            root_return_position == len(bundle.transition_decisions) - 1,
            "g2d5_parent_return_root_return_order_invalid",
        )
        construction_dependency_rows = (
            ("DECISION", parent_return.decision_id, parent_return.rule_id),
            (
                "QUEUE",
                terminal_queue.queue_entry_id,
                terminal_queue.transition_decision_id,
            ),
            (
                "ARTIFACT",
                terminal_artifact.artifact_id,
                abi.kernel_artifact_to_plain_dict_v01(terminal_artifact)["payload"][
                    "queue_entry_id"
                ],
            ),
            *(
                ("BUDGET", item.budget_id, item.budget_event_ref)
                for item in completion_budgets
            ),
        )
        proof.update(
            transition_decision_ids=decision_ids,
            runtime_trace_transition_refs=bundle.runtime_trace.transition_refs,
            budget_order=tuple(item.budget_id for item in bundle.budgets),
            queue_order=tuple(item.queue_entry_id for item in bundle.queue_entries),
            parent_return_decision_id=parent_return.decision_id,
            parent_return_decision_position=decision_position,
            parent_return_decision_rule_id=parent_return.rule_id,
            paired_budget_positions=paired_budget_positions,
            parent_return_queue_positions=queue_positions,
            parent_return_terminal_queue_id=terminal_queue.queue_entry_id,
            parent_return_terminal_artifact_id=terminal_artifact.artifact_id,
            construction_dependency_rows=construction_dependency_rows,
            signature_90_validation_ids=tuple(
                item.validation_report_id for item in signature_90_reports
            ),
            root_return_decision_id=root_return.decision_id,
            root_return_decision_position=root_return_position,
            parent_return_result_id=root_result.result_id,
            post_hoc_mapping_count=len(
                bundle.transition_decisions[root_return_position + 1:]
            ),
        )
        extra_refs = (
            parent_return.decision_id,
            *(item.budget_id for item in completion_budgets),
            terminal_queue.queue_entry_id,
            terminal_artifact.artifact_id,
            *(item.validation_report_id for item in signature_90_reports),
            root_return.decision_id,
        )
    elif case_number == 71:
        revise_env = _witness_initial_environment_v02(run)
        nodes = revise_env["nodes"]
        cell_input = revise_env["root_input"]
        if type(nodes) is not tuple or type(cell_input) is not fr.FractalCellInputV02:
            raise TypeError("g2d5_revise_witness_context_invalid")
        node = nodes[0]
        running, _running_artifact, start_budget = _witness_start_node_v02(
            revise_env,
            node=node,
            cell_input=cell_input,
        )
        running_artifact = _witness_artifact_for_queue_v02(
            revise_env,
            running.queue_entry_id,
        )
        local_material = _witness_local_observation_material_v02(
            revise_env,
            node=node,
            cell_input=cell_input,
            cell_budget_before=start_budget,
            global_budget_before=start_budget,
            dependencies=(),
        )
        t06 = _witness_eval_v02(
            revise_env,
            source_artifact=running_artifact,
            node=node,
            current_entry=running,
            cell_input=cell_input,
            cell_budget=start_budget,
            global_budget=start_budget,
            queue_reason_codes=local_material["queue_reason_codes"],
            observed_output_refs=local_material["observed_output_refs"],
            observed_evidence_refs=local_material["observed_evidence_refs"],
            advisory_refs=local_material["advisory_refs"],
        )
        if type(t06) is not transition_registry.TransitionDecisionV01:
            raise ValueError("g2d5_revise_t06_missing")
        finish_budget = _witness_budget_successor_v02(
            revise_env,
            start_budget,
            event="FINISH_NODE",
            decision=t06,
            cell_input=cell_input,
        )
        validating, validating_artifact, _ = _witness_advance_v02(
            revise_env,
            current=running,
            node=node,
            cell_input=cell_input,
            cell_budget_before=start_budget,
            global_budget_before=start_budget,
            cell_budget_after=finish_budget,
            global_budget_after=finish_budget,
            dependencies=(),
            round_entries=_witness_latest_queue_v02(revise_env),
            queue_reason_codes=local_material["queue_reason_codes"],
            observed_output_refs=local_material["observed_output_refs"],
            observed_evidence_refs=local_material["observed_evidence_refs"],
            advisory_refs=local_material["advisory_refs"],
        )
        cell_before = finish_budget
        global_before = finish_budget
        source_validation = fr.validate_fractal_cell_queue_entry_v02(validating)
        _require_pass_v02(source_validation, label="g2d5_revise_source")
        observation = fr.evaluate_fractal_revise_observation_v02(
            topology=bundle.topology,
            cell_input=cell_input,
            queue_entry=validating,
            validation_report=source_validation,
            cell_budget_before=cell_before,
            global_budget_before=global_before,
            revision_index=cell_input.initial_revise_count,
            newly_validated_evidence_count=1,
            newly_resolved_constraints_count=0,
            newly_accepted_outputs_count=0,
            newly_introduced_conflicts_count=0,
            consecutive_non_positive_count=0,
        )
        observation_report = fr.validate_fractal_revise_observation_v02(observation)
        _require_pass_v02(observation_report, label="g2d5_revise_observation")
        revise_env["revise_observations"] = (observation,)
        t07 = _witness_eval_v02(
            revise_env,
            source_artifact=validating_artifact,
            node=node,
            current_entry=validating,
            cell_input=cell_input,
            cell_budget=cell_before,
            global_budget=global_before,
            dependencies=(),
            validation_report=observation_report,
            revise_observation=observation,
        )
        if type(t07) is not transition_registry.TransitionDecisionV01:
            raise ValueError("g2d5_t07_decision_missing")
        revised_cell = _witness_budget_successor_v02(
            revise_env,
            cell_before,
            event="REVISE",
            decision=t07,
            cell_input=cell_input,
        )
        revised_global = revised_cell
        revised_queue, revised_artifact, repeated_t07 = _witness_advance_v02(
            revise_env,
            current=validating,
            node=node,
            cell_input=cell_input,
            cell_budget_before=cell_before,
            global_budget_before=global_before,
            cell_budget_after=revised_cell,
            global_budget_after=revised_global,
            dependencies=(),
            round_entries=_witness_latest_queue_v02(revise_env),
            validation_report=observation_report,
            revise_observation=observation,
        )
        _require_v02(repeated_t07 == t07, "g2d5_t07_decision_nondeterministic")
        registry = revise_env["registry"]
        if type(registry) is not transition_registry.TransitionRegistryV01:
            raise TypeError("g2d5_revise_registry_invalid")
        _require_v02(
            transition_registry.validate_fractal_runtime_transition_decision_v02(
                t07,
                registry=registry,
                source_artifact=validating_artifact,
                target_artifact=revised_artifact,
            ) == (),
            "g2d5_t07_decision_invalid",
        )
        revised_queue_report = fr.validate_fractal_cell_queue_entry_v02(revised_queue)
        _require_pass_v02(revised_queue_report, label="g2d5_revise_ready_queue")
        future_error = ""
        try:
            fr.evaluate_fractal_revise_observation_v02(
                topology=bundle.topology,
                cell_input=cell_input,
                queue_entry=validating,
                validation_report=source_validation,
                cell_budget_before=cell_before,
                global_budget_before=global_before,
                revision_index=validating.snapshot_sequence + 1,
                newly_validated_evidence_count=0,
                newly_resolved_constraints_count=0,
                newly_accepted_outputs_count=0,
                newly_introduced_conflicts_count=0,
                consecutive_non_positive_count=0,
            )
        except ValueError as exc:
            future_error = str(exc)
        _require_v02(
            future_error == "g2d_revise_observation_invalid",
            "g2d5_future_revise_not_rejected",
        )
        mutations = (
            ("circular_observation", replace(observation, trace_refs=(*observation.trace_refs, observation.observation_id))),
            ("wrong_cell_budget", replace(observation, cell_budget_before_id=global_before.budget_id + ":wrong")),
            ("wrong_revise_debit", replace(revised_cell, consumed_revise_count=revised_cell.consumed_revise_count + 1)),
            ("event_mismatch", replace(revised_cell, budget_event_kind="START_NODE")),
        )
        mutation_rows: list[tuple[object, ...]] = []
        mutation_reports: list[fr.FractalRuntimeValidationReportV02] = []
        for axis, mutated in mutations:
            if type(mutated) is fr.FractalReviseObservationV02:
                candidate = _reidentified_v02(
                    mutated,
                    identity_field="observation_id",
                    rebuild=fr.rebuild_fractal_revise_observation_identity_v02,
                )
                candidate_bundle = replace(
                    bundle,
                    revise_observations=(*bundle.revise_observations, candidate),
                )
            else:
                candidate = _reidentified_v02(
                    mutated,
                    identity_field="budget_id",
                    rebuild=fr.rebuild_fractal_runtime_budget_identity_v02,
                )
                candidate_bundle = replace(
                    bundle,
                    budgets=(*bundle.budgets, candidate),
                )
            report = fr.validate_fractal_runtime_execution_bundle_v02(candidate_bundle)
            _require_v02(report.status == "FAIL_CLOSED", "g2d5_revise_mutation_accepted")
            mutation_rows.append((axis, report.validation_report_id, report.reason_codes))
            mutation_reports.append(report)
        proof.update(
            ordered_revise_ids=(
                observation.observation_id,
                t07.decision_id,
                revised_cell.budget_id,
                revised_global.budget_id,
                revised_queue.queue_entry_id,
            ),
            observation_validation_id=observation_report.validation_report_id,
            transition_rule_id=t07.rule_id,
            revised_cell_budget_id=revised_cell.budget_id,
            revised_global_budget_id=revised_global.budget_id,
            revised_queue_entry_id=revised_queue.queue_entry_id,
            revised_queue_validation_id=revised_queue_report.validation_report_id,
            future_revision_error=future_error,
            mutation_rows=tuple(mutation_rows),
        )
        extra_refs = (
            observation.observation_id,
            observation_report.validation_report_id,
            t07.decision_id,
            revised_cell.budget_id,
            *((revised_global.budget_id,) if revised_global != revised_cell else ()),
            revised_queue.queue_entry_id,
            revised_queue_report.validation_report_id,
            *(item.validation_report_id for item in mutation_reports),
        )
    elif case_number == 72:
        retained_rows = tuple(
            (
                result.result_id,
                proposal["proposal_id"],
                post_vv_report["vv_report_id"],
                gt_report["gt_report_id"],
                result.pre_result_validation_report_id,
                result.post_vv_report_ref,
                result.gt_advisory_ref,
                result.ordered_child_result_ids,
            )
            for result, proposal, post_vv_report, gt_report in zip(
                bundle.cell_results,
                bundle.result_proposals,
                bundle.post_vv_reports,
                bundle.gt_advisory_reports,
                strict=True,
            )
        )
        _require_v02(
            all(row[5] == row[2] and row[6] == row[3] for row in retained_rows),
            "g2d5_retained_report_family_mismatch",
        )
        rebuilt_report = fr.aggregate_fractal_runtime_report_v02(
            topology=bundle.topology,
            topology_artifact=bundle.topology_artifact,
            source_binding=bundle.source_binding,
            cell_results=bundle.cell_results,
            queue_entries=bundle.queue_entries,
            backpressure_states=bundle.backpressure_states,
            runtime_trace=bundle.runtime_trace,
            final_global_budget=bundle.budgets[-1],
            parent_return_transition_decision=bundle.transition_decisions[-1],
            root_result_artifact=bundle.result_artifacts[-1],
        )
        report_validation = fr.validate_fractal_runtime_report_against_sources_v02(
            rebuilt_report,
            source_context=bundle.source_context,
            source_binding=bundle.source_binding,
            topology=bundle.topology,
            topology_artifact=bundle.topology_artifact,
            cell_results=bundle.cell_results,
            queue_entries=bundle.queue_entries,
            backpressure_states=bundle.backpressure_states,
            runtime_trace=bundle.runtime_trace,
            final_global_budget=bundle.budgets[-1],
            parent_return_transition_decision=bundle.transition_decisions[-1],
            root_result_artifact=bundle.result_artifacts[-1],
        )
        causal_report = _causal_validation_report_v02(bundle)
        stage_a, stage_b, stage_c = _stage_artifacts_v02(bundle)
        stage_report = fr.validate_fractal_runtime_stage_bundle_v02(
            stage="STAGE_D_C",
            artifacts=stage_c,
            source_context=bundle.source_context,
            topology=bundle.topology,
            topology_artifact=bundle.topology_artifact,
            runtime_trace=bundle.runtime_trace,
            queue_entries=bundle.queue_entries,
            queue_artifacts=bundle.queue_artifacts,
            cell_results=bundle.cell_results,
            result_artifacts=bundle.result_artifacts,
            runtime_report=bundle.runtime_report,
            report_artifact=bundle.report_artifact,
        )
        _require_v02(
            rebuilt_report == bundle.runtime_report
            and report_validation.status == causal_report.status == stage_report.status == "PASS",
            "g2d5_final_assembly_mismatch",
        )
        proof.update(
            prebundle_validation_ids=tuple(
                item.validation_report_id for item in bundle.validation_reports
            ),
            retained_result_report_rows=retained_rows,
            actual_child_result_ids=tuple(
                item.result_id for item in bundle.cell_results if item.parent_cell_id is not None
            ),
            causal_ref_count=len(bundle.causal_consumption_refs),
            causal_validation_id=causal_report.validation_report_id,
            stage_d_a_artifact_count=len(stage_a),
            stage_d_b_artifact_count=len(stage_b),
            stage_d_c_artifact_count=len(stage_c),
            stage_d_c_validation_id=stage_report.validation_report_id,
            reconstructed_runtime_report_id=rebuilt_report.report_id,
            reconstructed_report_validation_id=report_validation.validation_report_id,
            final_runtime_trace_id=bundle.runtime_trace.trace_id,
            final_runtime_report_id=bundle.runtime_report.report_id,
            final_report_artifact_id=bundle.report_artifact.artifact_id,
            complete_profile_status=run.external_report.status,
        )
        extra_refs = (
            causal_report.validation_report_id,
            stage_report.validation_report_id,
            report_validation.validation_report_id,
        )
    else:
        raise ValueError(f"g2d5_unmapped_case:{case_number}")
    return extra_refs


_ZERO_COUNTER_FIELD_NAMES = (
    "provider_calls",
    "model_calls",
    "gemini_calls",
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
)


def _report_identity_v02(report: FractalRuntimeG2DReportV02) -> str:
    material = fractal_runtime_g2_d_report_to_plain_data_v02(report)
    material.pop("report_id")
    return REPORT_ID_PREFIX + domain_separated_sha256_hex_v01(
        domain=REPORT_ID_DOMAIN,
        payload=canonical_json_bytes_v01(material),
    )


def collect_fractal_runtime_g2_d_v02() -> FractalRuntimeG2DReportV02:
    accepted = _collect_accepted_runs_v02()
    _require_v02(len(accepted) == 10, "g2d5_accepted_bundle_count")
    (
        backpressure_witness,
        gate_witness,
        degraded_child_witness,
        blocked_child_witness,
        depth_boundary_witness,
        cell_boundary_witness,
        budget_exhaustion_witness,
    ) = _build_shared_boundary_witnesses_v02(accepted)
    shared: dict[str, object] = {
        "outcome_rows": _outcome_witness_rows_v02(accepted),
        "backpressure_witness": backpressure_witness,
        "gate_witness": gate_witness,
        "degraded_child_witness": degraded_child_witness,
        "blocked_child_witness": blocked_child_witness,
        "depth_boundary_witness": depth_boundary_witness,
        "cell_boundary_witness": cell_boundary_witness,
        "budget_exhaustion_witness": budget_exhaustion_witness,
    }
    results: list[FractalRuntimeG2DCaseResultV02] = []
    for case_number, spec in enumerate(_CASE_SPECS, start=1):
        if case_number <= 10:
            results.append(
                _positive_case_result_v02(
                    spec=spec,
                    accepted_run=accepted[case_number - 1],
                )
            )
        elif case_number <= 27:
            results.append(
                _source_negative_case_result_v02(
                    case_number=case_number,
                    spec=spec,
                    accepted=accepted,
                )
            )
        elif case_number <= 41:
            results.append(
                _bounded_negative_case_result_v02(
                    case_number=case_number,
                    spec=spec,
                    accepted=accepted,
                    shared=shared,
                )
            )
        else:
            results.append(
                _accepted_matrix_case_result_v02(
                    case_number=case_number,
                    spec=spec,
                    accepted=accepted,
                    shared=shared,
                )
            )
    provisional = FractalRuntimeG2DReportV02(
        report_version=REPORT_VERSION,
        report_id="",
        profile_id=PROFILE_ID,
        domain_order=DOMAIN_ORDER,
        case_order=tuple(item.case_id for item in _CASE_SPECS),
        case_results=tuple(results),
        constructive_case_count=36,
        negative_case_count=36,
        domain_positive_case_count=10,
        accepted_bundle_count=10,
        counterfactual_case_count=2,
        topology_created_count=10,
        provider_calls=0,
        model_calls=0,
        gemini_calls=0,
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
        final_status="PASS",
        reason_codes=(),
    )
    report = replace(provisional, report_id=_report_identity_v02(provisional))
    reasons = validate_fractal_runtime_g2_d_report_v02(report)
    if reasons:
        raise ValueError(f"g2d5_collected_report_invalid:{reasons}")
    return report


def _case_result_types_valid_v02(value: object) -> bool:
    if type(value) is not FractalRuntimeG2DCaseResultV02:
        return False
    string_fields = (
        "case_id",
        "case_class",
        "expected_outcome",
        "observed_outcome",
        "evidence_material_json",
        "evidence_sha256",
        "final_status",
    )
    optional_string_fields = (
        "domain_id",
        "accepted_mode",
        "source_family_sha256",
        "topology_id",
        "runtime_report_id",
        "external_validation_report_id",
    )
    if any(type(getattr(value, name)) is not str for name in string_fields):
        return False
    if any(
        getattr(value, name) is not None
        and type(getattr(value, name)) is not str
        for name in optional_string_fields
    ):
        return False
    if (
        type(value.evidence_refs) is not tuple
        or any(type(item) is not str for item in value.evidence_refs)
        or type(value.reason_codes) is not tuple
        or any(type(item) is not str for item in value.reason_codes)
    ):
        return False
    integer_fields = ("topology_created_count", *_ZERO_COUNTER_FIELD_NAMES)
    return all(type(getattr(value, name)) is int for name in integer_fields)


def _sha256_text_valid_v02(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _prefixed_sha256_valid_v02(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and value.startswith(prefix)
        and _sha256_text_valid_v02(value[len(prefix):])
    )


def _empty_created_delta_valid_v02(value: object) -> bool:
    return (
        type(value) is dict
        and set(value) == {"before_ids", "after_ids", "created_ids", "created_count"}
        and value["before_ids"] == value["after_ids"]
        and value["created_ids"] == []
        and value["created_count"] == 0
    )


def _single_created_delta_valid_v02(value: object, created_id: object) -> bool:
    return (
        type(value) is dict
        and set(value) == {"before_ids", "after_ids", "created_ids", "created_count"}
        and type(created_id) is str
        and value["after_ids"] == [*value["before_ids"], created_id]
        and value["created_ids"] == [created_id]
        and value["created_count"] == 1
    )


def _matrix_proof_valid_v02(
    *,
    number: int,
    details: dict[str, object],
    evidence_refs: tuple[str, ...],
) -> bool:
    if number == 42:
        return (
            details["construction_call_count"] == 2
            and details["first_report_id"] == details["second_report_id"]
            and details["first_report_id"] in evidence_refs
            and details["first_sha256"] == details["second_sha256"]
            and _sha256_text_valid_v02(details["first_sha256"])
            and details["repeated_value_equal"] is True
            and details["repeated_id_equal"] is True
            and details["repeated_bytes_equal"] is True
        )
    if number == 43:
        postorder = details["result_postorder"]
        phases = details["phase_rows"]
        return (
            type(postorder) is list
            and len(postorder) == 3
            and all(type(row) is list and len(row) == 3 and row[2] is True for row in postorder)
            and type(phases) is list
            and len(phases) == len(postorder)
            and all(type(row) is list and len(row) == 8 and row[0] in {item[0] for item in postorder} for row in phases)
            and details["parent_return_decision_id"] in evidence_refs
            and type(details["terminal_validation_ids"]) is list
            and bool(details["terminal_validation_ids"])
            and all(item in evidence_refs for item in details["terminal_validation_ids"])
            and _sha256_text_valid_v02(details["causal_ref_sha256"])
            and details["final_bundle_report_id"] in evidence_refs
            and details["cycle_validation_id"] in evidence_refs
            and bool(details["cycle_reason_codes"])
        )
    if number == 44:
        rows = details["mutation_rows"]
        return (
            type(rows) is list
            and details["mutation_count"] == len(rows) == 10
            and [row[0] for row in rows]
            == [
                "entry_missing", "entry_duplicate", "entry_reordered",
                "entry_skipped_predecessor", "entry_foreign", "artifact_missing",
                "artifact_duplicate", "artifact_reordered",
                "artifact_skipped_predecessor", "artifact_foreign",
            ]
            and all(
                type(row) is list
                and len(row) == 4
                and row[1] in evidence_refs
                and row[2] != "NONE"
                and bool(row[3])
                for row in rows
            )
        )
    if number == 45:
        return (
            details["first_vv_report_id"] == details["second_vv_report_id"]
            and details["first_gt_report_id"] == details["second_gt_report_id"]
            and details["first_vv_sha256"] == details["second_vv_sha256"]
            and details["first_gt_sha256"] == details["second_gt_sha256"]
            and details["first_vv_report_id"] in evidence_refs
            and details["first_gt_report_id"] in evidence_refs
            and details["vv_validation_id"] in evidence_refs
            and details["gt_validation_id"] in evidence_refs
            and details["post_wall_clock_call_count"] == 0
            and details["gt_wall_clock_call_count"] == 0
        )
    if number == 46:
        causal = details["causal_ref"]
        return (
            type(causal) is dict
            and causal.get("disposition") == "USED"
            and details["changed_pointer"] == causal.get("output_field")
            and details["counterfactual_validation_id"] in evidence_refs
            and details["mutated_artifact_id"] in evidence_refs
            and details["accepted_bundle_ref"] in evidence_refs
        )
    if number == 47:
        ignored = details["ignored_causal_ref"]
        admission = details["admission_accepted_causal_ref"]
        blocked = details["blocked_gate_causal_ref"]
        return (
            type(ignored) is dict
            and ignored.get("disposition") == "IGNORED_WITH_REASON"
            and details["ignored_counterfactual_validation_id"] in evidence_refs
            and details["ignored_mutated_artifact_id"] in evidence_refs
            and details["accepted_bundle_ref"] in evidence_refs
            and details["admission_mutation_axis"]
            == "/source_artifact/planned_child_cell_id"
            and type(admission) is dict
            and admission.get("decision_effect") == "CHILD_ACTIVATION"
            and admission.get("disposition") == "USED"
            and admission.get("output_field") == "/planned_child_cell_id"
            and admission.get("source_artifact_id")
            == details["admission_baseline_source_artifact_id"]
            and details["admission_baseline_source_artifact_id"]
            in evidence_refs
            and details["admission_mutated_source_artifact_id"]
            in evidence_refs
            and details["admission_mutated_source_artifact_id"]
            != details["admission_baseline_source_artifact_id"]
            and details["admission_profile_validation_id"] in evidence_refs
            and details["admission_profile_status"] == "PASS"
            and type(details["admission_error"]) is str
            and bool(details["admission_error"])
            and details["admission_expected_downstream_artifact_id"] is None
            and _empty_created_delta_valid_v02(
                details["admission_child_input_delta"]
            )
            and _empty_created_delta_valid_v02(
                details["admission_initial_queue_delta"]
            )
            and _empty_created_delta_valid_v02(
                details["admission_initial_artifact_delta"]
            )
            and details["actual_gate_disposition"]
            == "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
            and details["actual_gate_reason_codes"]
            == ["g2d_required_child_failure"]
            and bool(details["actual_gate_evidence_refs"])
            and all(item in evidence_refs for item in details["actual_gate_evidence_refs"])
            and details["actual_gate_t06_decision_id"] in evidence_refs
            and details["actual_gate_validating_queue_id"] in evidence_refs
            and details["actual_gate_validating_artifact_id"] in evidence_refs
            and details["actual_gate_terminal_decision_id"] in evidence_refs
            and details["actual_gate_blocked_queue_id"] in evidence_refs
            and details["actual_gate_blocked_artifact_id"] in evidence_refs
            and details["actual_gate_validation_id"] in evidence_refs
            and _single_created_delta_valid_v02(
                details["actual_gate_terminal_delta"],
                details["actual_gate_blocked_queue_id"],
            )
            and _empty_created_delta_valid_v02(details["actual_gate_invocation_delta"])
            and _empty_created_delta_valid_v02(details["actual_gate_downstream_delta"])
            and type(blocked) is dict
            and blocked.get("disposition") == "BLOCKED_BY_GATE"
            and blocked.get("decision_effect") == "CELL_RESULT_OUTPUT"
            and blocked.get("output_field")
            == f"/observed_output_refs/{details['blocked_gate_output_index']}"
            and details["blocked_gate_output_index"] == 0
            and blocked.get("reason_code") == "gate:g2d_child_output"
            and blocked.get("consumer_component") == "fractal_scheduler_v02"
            and blocked.get("source_artifact_id")
            == details["blocked_gate_source_artifact_id"]
            and blocked.get("downstream_artifact_id")
            == details["blocked_gate_downstream_artifact_id"]
            and type(blocked.get("trace_refs")) is list
            and len(blocked["trace_refs"]) == 3
            and blocked["trace_refs"][:2]
            == [
                details["blocked_gate_source_artifact_id"],
                details["blocked_gate_downstream_artifact_id"],
            ]
            and all(item in evidence_refs for item in blocked.get("trace_refs", []))
            and details["blocked_gate_source_queue_id"] in evidence_refs
            and details["blocked_gate_source_artifact_id"] in evidence_refs
            and details["blocked_gate_downstream_queue_id"] in evidence_refs
            and details["blocked_gate_downstream_artifact_id"] in evidence_refs
            and details["blocked_gate_source_validation_id"] in evidence_refs
            and details["blocked_gate_downstream_validation_id"] in evidence_refs
            and details["blocked_gate_causal_validation_reasons"] == []
            and details["blocked_gate_artifact_validation_reasons"] == []
            and details["blocked_gate_bundle_validation_reasons"] == []
            and details["blocked_gate_counterfactual_validation_reasons"] == []
            and _sha256_text_valid_v02(
                details["blocked_gate_mutated_source_sha256"]
            )
            and details["blocked_gate_generic_diagnostic_scope"]
            == "SUPPLEMENTAL_NON_EXECUTABLE_STABLE_ID"
            and details["blocked_gate_row_in_accepted_runtime"] is False
        )
    if number == 48:
        rows = details["actual_child_result_rows"]
        return (
            type(rows) is list
            and len(rows) == 3
            and all(type(row) is list and len(row) == 7 and row[6] is True for row in rows)
            and details["no_child_result_ids"] == []
            and details["no_child_partial_failure_ids"] == []
            and details["invalid_child_ref_validation_id"] in evidence_refs
            and bool(details["invalid_child_ref_reason_codes"])
        )
    if number == 49:
        rows = details["validation_chain_rows"]
        return (
            type(rows) is list
            and len(rows) == 3
            and all(type(row) is list and len(row) == 6 and len(row[5]) == 4 for row in rows)
            and details["cycle_validation_id"] in evidence_refs
            and bool(details["cycle_reason_codes"])
        )
    if number == 50:
        rows = details["aggregation_rows"]
        return (
            type(rows) is list
            and [row[0] for row in rows] == [0, 1, 2]
            and details["one_child_validation_id"] in evidence_refs
            and details["queue_entry_count"] > 0
            and details["budget_count"] > 0
            and details["runtime_abi_ref_count"] > 0
        )
    if number == 51:
        rows = details["five_mode_template_rows"]
        return (
            type(rows) is list
            and [row.get("mode") for row in rows] == list(fr.TOPOLOGY_ELIGIBLE_MODES)
            and all(
                type(row) is dict
                and row["node_count"] > 0
                and row["edge_count"] >= 0
                and row["assignment_count"] > 0
                and all(
                    _sha256_text_valid_v02(row[key])
                    for key in (
                        "node_template_sha256", "node_rows_sha256",
                        "edge_template_sha256", "edge_rows_sha256",
                        "assignment_template_sha256", "assignment_rows_sha256",
                    )
                )
                for row in rows
            )
            and details["mutation_axis"] == "topology_nodes[0].required"
            and details["mutation_validation_id"] in evidence_refs
            and bool(details["mutation_reason_codes"])
        )
    if number == 52:
        rows = details["source_binding_rows"]
        expected_axes = {
            "selected_local_mode_profile_id", "selected_feasibility_row_id",
            "selected_safe_depth_rank", "selected_expected_cost_units",
            "required_downstream_capability_ids", "source_policy_snapshot_id",
            "source_capability_snapshot_id", "accepted_scope_ref",
        }
        return (
            type(rows) is list
            and [row.get("mode") for row in rows] == list(fr.TOPOLOGY_ELIGIBLE_MODES)
            and details["per_mode_substitution_count"] == 8
            and details["total_substitution_count"] == 40
            and all(
                type(row.get("mutation_rows")) is list
                and len(row["mutation_rows"]) == 8
                and {item[0] for item in row["mutation_rows"]} == expected_axes
                and all(bool(item[3]) for item in row["mutation_rows"])
                for row in rows
            )
        )
    if number == 53:
        rows = details["mutation_rows"]
        return (
            type(details["allocation_predecessor_debit_rows"]) is list
            and bool(details["allocation_predecessor_debit_rows"])
            and type(details["event_counts"]) is list
            and len(details["event_counts"]) == len(fr.BUDGET_EVENT_KINDS)
            and type(rows) is list
            and details["mutation_count"] == len(rows) == 8
            and [row[0] for row in rows]
            == ["allocation_parent", "predecessor", "event", "state", "counter", "remaining", "event_ref", "identity"]
            and all(row[2] in evidence_refs and bool(row[3]) for row in rows)
        )
    if number == 54:
        rows = details["outcome_rows"]
        return (
            type(rows) is list
            and details["outcome_count"] == len(rows) == 5
            and [(row["proposal_status"], row["terminal_state"]) for row in rows]
            == [(item[0], item[3]) for item in fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02]
            and details["outcome_mapping_rows"]
            == _plain_value_v02(fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02)
            and all(
                row[key] in evidence_refs
                for row in rows
                for key in (
                    "proposal_validation_id", "vv_validation_id",
                    "gt_validation_id", "result_validation_id",
                )
            )
        )
    if number == 55:
        return (
            len(details["root_final_budget_ids"]) == 1
            and details["evaluated_root_decision_id"] in details["parent_return_decision_ids"]
            and details["evaluated_root_decision_id"] in evidence_refs
            and details["root_return_rule_ids"]
            == [
                "g2d_t13_completed_to_parent_return",
                "g2d_t14_degraded_to_parent_return",
                "g2d_t15_blocked_to_parent_return",
                "g2d_t16_needs_user_to_parent_return",
                "g2d_t17_deadend_to_parent_return",
            ]
            and details["child_rejection_reason"]
            == "g2d_root_result_required_for_parent_return"
        )
    if number == 56:
        expected_forms = [
            "ROOT_INITIAL", "CHILD_INITIAL", "ORDINARY_ROOT_SUCCESSOR",
            "ORDINARY_CHILD_SUCCESSOR", "INVOKED_CHILD_T06_VALIDATING",
            "INVOKED_CHILD_T08_T12_TERMINAL",
        ]
        return (
            details["field_partitions"] == [32, 31, 32, 42]
            and details["queue_parent_form_names"] == expected_forms
            and {row[0] for row in details["queue_parent_form_rows"]} == set(expected_forms)
            and len(details["stage_artifact_counts"]) == 3
            and len(details["stage_validation_ids"]) == 3
            and all(item in evidence_refs for item in details["stage_validation_ids"])
            and details["trace_unique"] is True
            and details["queue_reason_field_exact"] is True
        )
    if number == 57:
        return (
            type(details["causal_pointer_reason_rows"]) is list
            and bool(details["causal_pointer_reason_rows"])
            and all(row[1].startswith("/") and ":" in row[4] for row in details["causal_pointer_reason_rows"])
            and details["causal_validation_id"] in evidence_refs
            and details["corruption_validation_id"] in evidence_refs
            and bool(details["corruption_reason_codes"])
            and _empty_created_delta_valid_v02(details["corruption_causal_delta"])
            and details["activation_causal_row_count"] == 2
            and details["child_return_causal_row_count"] == 6
        )
    if number == 58:
        rows = details["backpressure_precedence_rows"]
        successors = details["deferred_successor_rows"]
        dependency = details["dependency_wait_row"]
        blocked = details["budget_blocked_row"]
        return (
            type(rows) is list
            and len(rows) == 2
            and len(details["backpressure_validation_ids"]) == len(rows)
            and len({row[1] for row in rows}) == len(rows)
            and all(row[2] == row[3] + row[4] for row in rows)
            and all(row[0] in evidence_refs for row in rows)
            and all(item in evidence_refs for item in details["backpressure_validation_ids"])
            and type(successors) is list
            and len(successors) == 2
            and all(
                row[0] in evidence_refs
                and row[2] in evidence_refs
                and row[3] in evidence_refs
                and row[5] == "PENDING"
                and row[6] == ["g2d_transition_backpressure_deferred"]
                for row in successors
            )
            and dependency[0] in evidence_refs
            and dependency[1] in evidence_refs
            and dependency[2:] == ["PENDING", [], True]
            and blocked[0] in evidence_refs
            and blocked[1] in evidence_refs
            and blocked[2] in evidence_refs
            and len(blocked) == 9
            and blocked[3] == "BLOCKED"
            and blocked[4] == ["g2d_required_child_failure"]
            and blocked[5] in evidence_refs
            and blocked[6] == details["exhausted_budget_id"]
            and blocked[7] == details["exhausted_budget_validation_id"]
            and blocked[8] == details["budget_exhaustion_t06_decision_id"]
            and details["budget_exhaustion_resource"] == "remaining_cell_count"
            and details["budget_exhaustion_tree_shape"] == [1, 4, 16]
            and details["budget_exhaustion_depth_counts"]
            == {"0": 1, "1": 4, "2": 16}
            and len(details["budget_exhaustion_accepted_cell_ids"]) == 21
            and len(set(details["budget_exhaustion_accepted_cell_ids"])) == 21
            and all(
                item in evidence_refs
                for item in details["budget_exhaustion_accepted_cell_ids"]
            )
            and details["budget_before_id"] in evidence_refs
            and details["budget_before_consumed_cell_count"] == 1
            and details["budget_before_remaining_cell_count"] == 20
            and details["exhausted_budget_id"] in evidence_refs
            and details["exhausted_budget_validation_id"] in evidence_refs
            and details["exhausted_consumed_cell_count"] == 21
            and details["exhausted_remaining_cell_count"] == 0
            and details["budget_exhaustion_t06_decision_id"] in evidence_refs
            and details["budget_exhaustion_terminal_decision_id"] in evidence_refs
            and type(details["budget_exhaustion_queue_delta"]) is dict
            and details["budget_exhaustion_queue_delta"]["created_count"] == 2
            and details["budget_exhaustion_queue_delta"]["created_ids"][-1]
            == blocked[0]
            and type(details["budget_exhaustion_budget_delta"]) is dict
            and details["budget_exhaustion_budget_delta"]["created_count"] > 0
            and details["exhausted_budget_id"]
            in details["budget_exhaustion_budget_delta"]["created_ids"]
            and details["budget_exhaustion_no_drop"] is True
            and details["unique_state_per_round"] is True
            and details["unchanged_t03_suppressed"] is True
            and _empty_created_delta_valid_v02(details["suppression_created_objects"])
            and details["no_work_dropped"] is True
            and bool(details["runtime_queue_order"])
            and bool(details["queue_order_error"])
        )
    if number == 59:
        return (
            len(details["policy_profile_separation"]) == 5
            and details["profile_count"] == 1
            and details["policy_identity_count"] == 5
            and details["source_binding_identity_count"] == 5
            and details["substitution_validation_id"] in evidence_refs
            and bool(details["substitution_reason_codes"])
        )
    if number == 60:
        return (
            [row[0] for row in details["full_fractal_root_edges"]] == list(range(7))
            and [row[:5] for row in details["full_fractal_leaf_edges"]]
            == [
                [7, 0, 4, "VALIDATION", "FRACTAL_LEAF_PROJECTION"],
                [8, 4, 5, "VALIDATION", "FRACTAL_LEAF_PROJECTION"],
                [9, 5, 6, "RETURN", "FRACTAL_LEAF_PROJECTION"],
            ]
            and details["leaf_source_target_indexes"] == [[0, 4], [4, 5], [5, 6]]
            and details["leaf_edge_kinds"] == ["VALIDATION", "VALIDATION", "RETURN"]
            and details["topology_validation_id"] in evidence_refs
        )
    if number == 61:
        return (
            bool(details["cell_global_event_pairing"])
            and bool(details["paired_event_rows"])
            and bool(details["budget_validation_ids"])
            and bool(details["create_only_debit_rows"])
            and bool(details["zero_delta_aggregate_rows"])
            and len(details["mutation_rows"]) == 3
            and [row[0] for row in details["mutation_rows"]]
            == ["stale_pair", "missing_pair", "forged_pair"]
            and all(row[1] in evidence_refs and bool(row[2]) for row in details["mutation_rows"])
        )
    if number == 62:
        return (
            bool(details["pre_root_lifecycle"])
            and [[row[0], row[3]] for row in details["outcome_lifecycle_rows"]]
            == [
                ["COMPLETED", "VALIDATED"], ["DEGRADED", "VALIDATED"],
                ["BLOCKED", "BLOCKED_FAIL_CLOSED"],
                ["NEEDS_USER", "VALIDATED"], ["DEADEND", "VALIDATED"],
            ]
            and details["forbidden_root_lifecycles"] == ["ACCEPTED", "REJECTED", "ROOT_REVIEWED"]
            and details["final_output_created"] == 0
        )
    if number == 63:
        rows = details["context_unique_gt_rows"]
        return (
            type(rows) is list
            and len(rows) == 3
            and len({row[2] for row in rows}) == len(rows)
            and len(details["gt_validation_ids"]) == len(rows)
            and details["substitution_validation_id"] in evidence_refs
            and bool(details["substitution_reason_codes"])
            and details["result_gt_refs"] == [row[2] for row in rows]
        )
    if number == 64:
        rows = details["validation_status_stage_rows"]
        return (
            details["validation_targets"] == list(fr.VALIDATION_TARGETS)
            and details["failure_stages"] == list(fr.FAILURE_STAGES)
            and details["validation_target_count"] == 34
            and details["failure_stage_count"] == 30
            and type(rows) is list
            and bool(rows)
            and all(row[1] != "PASS" or (row[2] == "NONE" and row[3] == []) for row in rows)
            and details["explicit_pass_report_id"] in evidence_refs
            and details["explicit_failure_report_id"] in evidence_refs
            and bool(details["explicit_failure_reason_codes"])
            and _sha256_text_valid_v02(details["causal_profile_sha256"])
        )
    if number == 65:
        return (
            bool(details["instance_snapshot_round_reason_rows"])
            and len(details["queue_validation_ids"])
            == len(details["instance_snapshot_round_reason_rows"])
            and details["copied_queue_reason_validation_id"] in evidence_refs
            and details["copied_proposal_status_validation_id"] in evidence_refs
            and bool(details["copied_queue_reason_codes"])
            and bool(details["copied_proposal_status_reason_codes"])
            and details["rejected_copied_signal_count"] == 2
        )
    if number == 66:
        return (
            len(details["child_slot_input_node_order"]) == 3
            and len(details["cell_result_order"]) == 3
            and details["child_results_before_root"] == [True, True]
            and bool(details["parent_slot_rows"])
            and bool(details["merge_rows"])
            and details["denied_slot_terminal_id"] in evidence_refs
            and details["denied_slot_artifact_id"] in evidence_refs
            and details["denied_slot_validation_id"] in evidence_refs
            and details["denied_slot_state"] == "BLOCKED"
            and details["denied_gate_disposition"]
            == "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
            and details["denied_gate_reason_codes"]
            == ["g2d_required_child_failure"]
            and all(item in evidence_refs for item in details["denied_gate_evidence_refs"])
            and details["denied_t06_decision_id"] in evidence_refs
            and details["denied_terminal_decision_id"] in evidence_refs
            and _single_created_delta_valid_v02(
                details["denied_terminal_delta"],
                details["denied_slot_terminal_id"],
            )
            and _empty_created_delta_valid_v02(details["denied_invocation_delta"])
            and _empty_created_delta_valid_v02(details["denied_result_delta"])
            and _empty_created_delta_valid_v02(
                details["denied_partial_failure_delta"]
            )
            and details["merge_validation_id"] in evidence_refs
            and details["merge_decision_is_none"] is True
            and details["child_invocation_count"] == 2
        )
    if number == 67:
        return (
            details["runtime_report_id"] in evidence_refs
            and details["report_artifact_id"] in evidence_refs
            and details["runtime_outcome"] == "COMPLETED"
            and details["public_return_bundle_type"] == "FractalRuntimeExecutionBundleV02"
            and details["terminal_report_target"] == "COMPLETE_PROFILE"
            and details["terminal_report_status"] == "PASS"
            and details["root_owned_outcome"] is True
            and details["staged_public_function_counts"] == [74, 81, 90, 110]
            and details["module_public_function_count"] == 110
        )
    if number == 68:
        rows = details["four_child_structural_rows"]
        return (
            len(details["two_child_runtime_rows"]) == 2
            and type(rows) is list
            and len(rows) == 4
            and details["four_child_index_order"] == [0, 1, 2, 3]
            and len({row["allocation_parent_budget_id"] for row in rows}) == 1
            and details["four_child_parent_basis_id"] == rows[0]["allocation_parent_budget_id"]
            and all(row["requested_sibling_count"] == 4 for row in rows)
            and len({row["parent_input_id"] for row in rows}) == 1
            and len({row["child_cell_id"] for row in rows}) == 4
            and all(
                row["budget_id"] in evidence_refs
                and row["budget_validation_id"] in evidence_refs
                for row in rows
            )
            and details["four_child_cell_share_sum"] == sum(row["max_total_cells"] for row in rows)
            and details["four_child_revise_share_sum"] == sum(row["max_revise_count"] for row in rows)
            and details["four_child_context_validation_id"] in evidence_refs
            and details["four_child_context_validation_status"] == "FAIL_CLOSED"
            and "g2d_node_instance_geometry_invalid"
            in details["four_child_context_reason_codes"]
            and details["four_child_runtime_projection_count"] == 0
            and details["four_child_derivation_rows"]
            == [[0, 1], [1, 1], [0, 2], [1, 2]]
            and all(_sha256_text_valid_v02(row["structural_row_sha256"]) for row in rows)
        )
    if number == 69:
        return (
            len(details["planned_child_ids"]) == 2
            and len(details["activated_child_ids"]) == 2
            and len(details["activation_rows"]) == 2
            and len(details["first_initial_downstreams"]) == 2
            and bool(details["accepted_cell_create_rows"])
            and details["valid_denial_disposition"]
            == "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
            and details["valid_denial_queue_id"] in evidence_refs
            and details["valid_denial_artifact_id"] in evidence_refs
            and details["valid_denial_validation_id"] in evidence_refs
            and _empty_created_delta_valid_v02(
                details["valid_denial_invocation_delta"]
            )
            and details["malformed_candidate_validation_id"] in evidence_refs
            and bool(details["malformed_candidate_reason_codes"])
            and _empty_created_delta_valid_v02(details["malformed_candidate_created_terminals"])
        )
    if number == 70:
        return (
            details["transition_decision_ids"] == details["runtime_trace_transition_refs"]
            and details["parent_return_decision_id"] in evidence_refs
            and details["transition_decision_ids"][details["parent_return_decision_position"]]
            == details["parent_return_decision_id"]
            and details["parent_return_decision_rule_id"]
            == "g2d_t08_validating_to_completed"
            and bool(details["paired_budget_positions"])
            and details["parent_return_terminal_queue_id"] in evidence_refs
            and details["parent_return_terminal_artifact_id"] in evidence_refs
            and all(item in evidence_refs for item in details["signature_90_validation_ids"])
            and details["construction_dependency_rows"][0]
            == [
                "DECISION",
                details["parent_return_decision_id"],
                details["parent_return_decision_rule_id"],
            ]
            and details["construction_dependency_rows"][1][2]
            == details["parent_return_decision_id"]
            and details["construction_dependency_rows"][2][2]
            == details["parent_return_terminal_queue_id"]
            and all(
                row[0] == "BUDGET"
                and row[2] == details["parent_return_decision_id"]
                for row in details["construction_dependency_rows"][3:]
            )
            and details["transition_decision_ids"][details["root_return_decision_position"]]
            == details["root_return_decision_id"]
            and details["root_return_decision_position"]
            == len(details["transition_decision_ids"]) - 1
            and details["post_hoc_mapping_count"] == 0
        )
    if number == 71:
        rows = details["mutation_rows"]
        return (
            len(details["ordered_revise_ids"]) == 5
            and details["transition_rule_id"] == "g2d_t07_validating_to_revise"
            and details["revised_queue_entry_id"] == details["ordered_revise_ids"][-1]
            and details["observation_validation_id"] in evidence_refs
            and details["revised_queue_validation_id"] in evidence_refs
            and details["future_revision_error"] == "g2d_revise_observation_invalid"
            and type(rows) is list
            and [row[0] for row in rows]
            == ["circular_observation", "wrong_cell_budget", "wrong_revise_debit", "event_mismatch"]
            and all(row[1] in evidence_refs and bool(row[2]) for row in rows)
        )
    if number == 72:
        return (
            bool(details["prebundle_validation_ids"])
            and len(details["retained_result_report_rows"]) == 3
            and len(details["actual_child_result_ids"]) == 2
            and details["causal_ref_count"] > 0
            and details["causal_validation_id"] in evidence_refs
            and details["stage_d_a_artifact_count"] > 0
            and details["stage_d_a_artifact_count"] < details["stage_d_b_artifact_count"] < details["stage_d_c_artifact_count"]
            and details["stage_d_c_validation_id"] in evidence_refs
            and details["reconstructed_runtime_report_id"] == details["final_runtime_report_id"]
            and details["reconstructed_report_validation_id"] in evidence_refs
            and details["complete_profile_status"] == "PASS"
        )
    return False


def _proof_contract_valid_v02(
    *,
    case_result: FractalRuntimeG2DCaseResultV02,
    proof: object,
    position: int,
) -> bool:
    if type(proof) is not dict:
        return False
    required_keys = {
        "proof_kind",
        "axis",
        "executor",
        "observed_source",
        "matrix_cardinality",
        "accepted_bundle_required",
        "details",
        "details_sha256",
    }
    if set(proof) != required_keys:
        return False
    contract = _PROOF_CONTRACTS_V02[case_result.case_id]
    if (
        proof["proof_kind"] != contract.proof_kind
        or proof["axis"] != contract.axis
        or proof["executor"] != contract.executor
        or proof["observed_source"] != contract.observed_source
        or proof["matrix_cardinality"] != contract.matrix_cardinality
        or proof["accepted_bundle_required"] is not contract.accepted_bundle_required
        or type(proof["details"]) is not dict
        or not _sha256_text_valid_v02(proof["details_sha256"])
        or proof["details_sha256"] != _sha256_plain_v02(proof["details"])
    ):
        return False
    details = proof["details"]
    number = position + 1
    if set(details) != _DETAIL_KEY_CONTRACTS_V02[case_result.case_id]:
        return False
    if number <= 10:
        return (
            details["domain_id"] == case_result.domain_id
            and details["accepted_mode"] == case_result.accepted_mode
            and details["runtime_outcome"] == case_result.observed_outcome
            and details["runtime_report_status"] == "PASS"
            and details["complete_profile_status"] == "PASS"
            and details["zero_runtime_counters"] == [0] * 12
            and details["root_outcome"]
            == (
                "NARROW"
                if case_result.domain_id == DOMAIN_ORDER[0]
                and case_result.accepted_mode == "cloud_llm"
                else "ACCEPT"
            )
            and type(details["topology_node_ids"]) is list
            and bool(details["topology_node_ids"])
            and len(details["child_cell_input_ids"])
            == (2 if case_result.accepted_mode == "full_fractal" else 0)
        )
    if number <= 27:
        return (
            details["case_number"] == number
            and details["mutated_path"]
            == _SOURCE_NEGATIVE_MUTATED_PATHS_V02[number - 11]
            and _sha256_text_valid_v02(details["baseline_sha256"])
            and _sha256_text_valid_v02(details["attempted_sha256"])
            and details["baseline_sha256"] != details["attempted_sha256"]
            and _prefixed_sha256_valid_v02(
                details["validation_report_id"], "frvalidation_v02:"
            )
            and details["validation_report_id"] in case_result.evidence_refs
            and details["validation_target"] == "SOURCE_CONTEXT_STRUCTURAL"
            and details["failure_stage"] == "SOURCE_CONTEXT"
            and _prefixed_sha256_valid_v02(
                details["external_validation_report_id"], "frvalidation_v02:"
            )
            and details["external_validation_report_id"] in case_result.evidence_refs
            and details["external_validation_report_id"]
            == details["validation_report_id"]
            and details["external_validation_target"]
            == details["validation_target"]
            and type(details["reason_codes"]) is list
            and bool(details["reason_codes"])
            and type(details["external_reason_codes"]) is list
            and bool(details["external_reason_codes"])
            and details["external_reason_codes"] == details["reason_codes"]
            and details["topology_created_delta"] == 0
            and details["bundle_created_delta"] == 0
            and details["created_before"]
            == {"bundle_report_ids": [], "topology_ids": []}
            and details["created_after"]
            == {"bundle_report_ids": [], "topology_ids": []}
        )
    if number <= 41:
        if (
            details["case_number"] != number
            or details["policy_id"] not in case_result.evidence_refs
            or details["accepted_bundle_validation_id"]
            not in case_result.evidence_refs
        ):
            return False
        if number == 28:
            rows = details["accepted_depth_rows"]
            return (
                type(rows) is list
                and len(rows) == 3
                and details["accepted_depths"] == [0, 1, 2]
                and [row["depth"] for row in rows] == [0, 1, 2]
                and all(
                    set(row)
                    == {
                        "depth", "cell_input_id", "cell_id", "parent_cell_id",
                        "validation_report_id", "validation_target", "status",
                    }
                    and row["cell_input_id"] in case_result.evidence_refs
                    and row["validation_report_id"] in case_result.evidence_refs
                    and row["validation_target"] == "FractalCellInputV02"
                    and row["status"] == "PASS"
                    for row in rows
                )
                and rows[0]["parent_cell_id"] is None
                and rows[1]["parent_cell_id"] == rows[0]["cell_id"]
                and rows[2]["parent_cell_id"] == rows[1]["cell_id"]
                and details["rejected_depth"] == 3
                and details["rejected_parent_cell_id"] == rows[2]["cell_id"]
                and details["rejected_input_id"] in case_result.evidence_refs
                and details["rejected_validation_report_id"]
                in case_result.evidence_refs
                and details["rejected_validation_target"]
                == "FractalCellInputV02"
                and bool(details["rejected_reason_codes"])
                and _empty_created_delta_valid_v02(
                    details["rejected_runtime_object_delta"]
                )
            )
        if number == 29:
            return (
                details["attempted_value"] == details["accepted_value"] + 1
                and details["baseline_input_id"] != details["mutated_input_id"]
                and details["validation_report_id"] in case_result.evidence_refs
                and details["validation_target"] == "FractalCellInputV02"
                and type(details["reason_codes"]) is list
                and bool(details["reason_codes"])
                and _empty_created_delta_valid_v02(details["created_objects"])
            )
        if number == 30:
            root_rows = details["root_budget_event_rows"]
            rows = details["accepted_cell_rows"]
            cell_rows = details["cell_rows"]
            parent_rows = details["parent_child_rows"]
            expected_row_keys = {
                "cell_number", "cell_id", "parent_cell_id", "cell_depth",
                "canonical_child_index", "planning_input_id",
                "planning_validation_id", "planning_validation_status",
                "planning_reason_codes",
                "global_before_budget_id", "global_before_consumed_cell_count",
                "child_allocation_budget_id", "child_allocation_validation_id",
                "child_allocation_consumed_cell_count", "child_activate_budget_id",
                "child_activate_validation_id", "child_activate_consumed_cell_count",
                "global_activate_budget_id", "global_activate_validation_id",
                "global_activate_consumed_cell_count", "child_create_budget_id",
                "child_create_validation_id", "child_create_consumed_cell_count",
                "global_create_budget_id", "global_create_validation_id",
                "global_create_consumed_cell_count",
                "global_create_remaining_cell_count",
                "scope_projection_id", "scope_validation_id", "cell_input_id",
                "cell_input_validation_id",
            }
            expected_cell_row_keys = {
                "cell_number", "cell_id", "parent_cell_id", "cell_depth",
                "canonical_child_index", "scope_projection_id",
                "scope_validation_report_id", "cell_input_id",
                "cell_input_validation_report_id", "cell_input_validation_status",
                "cell_create_budget_id", "global_create_budget_id",
                "global_consumed_cell_count",
            }
            expected_parent_row_keys = {
                "parent_cell_id", "child_cell_id", "child_depth",
                "canonical_child_index", "scope_projection_id",
                "scope_validation_report_id", "cell_input_id",
                "cell_input_validation_report_id", "cell_create_budget_id",
                "global_create_budget_id",
            }
            return (
                details["max_total_cells"] == 21
                and details["tree_shape"] == [1, 4, 16]
                and details["depth_counts"] == {"0": 1, "1": 4, "2": 16}
                and type(cell_rows) is list
                and len(cell_rows) == 21
                and all(set(row) == expected_cell_row_keys for row in cell_rows)
                and [row["cell_number"] for row in cell_rows] == list(range(1, 22))
                and [row["cell_depth"] for row in cell_rows].count(0) == 1
                and [row["cell_depth"] for row in cell_rows].count(1) == 4
                and [row["cell_depth"] for row in cell_rows].count(2) == 16
                and cell_rows[0]["cell_id"] == details["root_cell_id"]
                and cell_rows[0]["parent_cell_id"] is None
                and cell_rows[0]["canonical_child_index"] is None
                and cell_rows[0]["scope_projection_id"] is None
                and cell_rows[0]["cell_input_validation_status"] == "PASS"
                and all(
                    row["cell_id"] in case_result.evidence_refs
                    and row["cell_input_id"] in case_result.evidence_refs
                    and row["cell_input_validation_report_id"]
                    in case_result.evidence_refs
                    and row["cell_create_budget_id"] in case_result.evidence_refs
                    and row["cell_input_validation_status"] == "PASS"
                    for row in cell_rows
                )
                and [row["cell_id"] for row in cell_rows if row["cell_depth"] == 1]
                == details["depth_1_cell_ids"]
                and [row["cell_id"] for row in cell_rows if row["cell_depth"] == 2]
                == details["depth_2_cell_ids"]
                and type(parent_rows) is list
                and len(parent_rows) == 20
                and all(set(row) == expected_parent_row_keys for row in parent_rows)
                and {row["parent_cell_id"] for row in parent_rows if row["child_depth"] == 1}
                == {details["root_cell_id"]}
                and {row["parent_cell_id"] for row in parent_rows if row["child_depth"] == 2}
                == set(details["depth_1_cell_ids"])
                and all(
                    sorted(
                        row["canonical_child_index"]
                        for row in parent_rows
                        if row["parent_cell_id"] == parent_id
                    )
                    == [0, 1, 2, 3]
                    for parent_id in (
                        details["root_cell_id"],
                        *details["depth_1_cell_ids"],
                    )
                )
                and all(
                    row["scope_projection_id"] in case_result.evidence_refs
                    and row["scope_validation_report_id"] in case_result.evidence_refs
                    and row["cell_input_id"] in case_result.evidence_refs
                    and row["cell_input_validation_report_id"]
                    in case_result.evidence_refs
                    for row in parent_rows
                )
                and type(root_rows) is list
                and [row[0] for row in root_rows]
                == ["INITIAL_ALLOCATION", "ACTIVATE", "CELL_CREATE"]
                and [row[2] for row in root_rows] == [0, 0, 1]
                and all(
                    len(row) == 6
                    and row[1] in case_result.evidence_refs
                    and row[4] in case_result.evidence_refs
                    and row[5] == "PASS"
                    for row in root_rows
                )
                and type(rows) is list
                and len(rows) == 20
                and [row["cell_number"] for row in rows]
                == list(range(2, 22))
                and all(set(row) == expected_row_keys for row in rows)
                and all(
                    row[key] in case_result.evidence_refs
                    for row in rows
                    for key in (
                        "cell_id", "parent_cell_id", "planning_input_id",
                        "planning_validation_id", "child_allocation_budget_id",
                        "child_allocation_validation_id", "child_activate_budget_id",
                        "child_activate_validation_id", "global_activate_budget_id",
                        "global_activate_validation_id", "child_create_budget_id",
                        "child_create_validation_id", "global_create_budget_id",
                        "global_create_validation_id", "scope_projection_id",
                        "scope_validation_id", "cell_input_id",
                        "cell_input_validation_id",
                    )
                )
                and all(
                    row["planning_validation_status"] == "FAIL_CLOSED"
                    and bool(row["planning_reason_codes"])
                    and row["child_allocation_consumed_cell_count"] == 0
                    and row["child_activate_consumed_cell_count"] == 0
                    and row["global_activate_consumed_cell_count"]
                    == row["global_before_consumed_cell_count"]
                    and row["child_create_consumed_cell_count"] == 1
                    and row["global_create_consumed_cell_count"]
                    == row["global_activate_consumed_cell_count"] + 1
                    and row["global_create_consumed_cell_count"]
                    == row["cell_number"]
                    and row["global_create_remaining_cell_count"]
                    == 21 - row["cell_number"]
                    for row in rows
                )
                and type(details["accepted_cell_ids"]) is list
                and len(details["accepted_cell_ids"])
                == details["accepted_cell_count"] == 21
                and len(set(details["accepted_cell_ids"])) == 21
                and all(
                    item in case_result.evidence_refs
                    for item in details["accepted_cell_ids"]
                )
                and details["accepted_cell_ids"]
                == [row["cell_id"] for row in cell_rows]
                and details["planning_debit_count"] == 0
                and details["allocation_debit_count"] == 0
                and details["activate_debit_count"] == 0
                and details["cell_create_debit_count"] == 21
                and details["root_create_budget_id"] == root_rows[-1][1]
                and details["twenty_first_global_budget_id"]
                == rows[-1]["global_create_budget_id"]
                and details["twenty_first_validation_report_id"]
                == rows[-1]["global_create_validation_id"]
                and details["twenty_first_consumed_cell_count"] == 21
                and details["twenty_first_remaining_cell_count"] == 0
                and details["attempted_twenty_second_cell_id"]
                in case_result.evidence_refs
                and details["attempted_twenty_second_parent_id"]
                == details["root_cell_id"]
                and details["attempted_twenty_second_error"]
                == "g2d_budget_overflow"
                and details["attempted_twenty_second_global_budget_created"]
                is False
                and details["rejected_budget_id"] in case_result.evidence_refs
                and details["rejected_validation_report_id"]
                in case_result.evidence_refs
                and details["rejected_validation_target"]
                == "FractalRuntimeBudgetV02"
                and bool(details["rejected_reason_codes"])
                and _empty_created_delta_valid_v02(
                    details["rejected_runtime_object_delta"]
                )
            )
        if number in {32, 33, 34}:
            expected_field = {
                30: "consumed_cell_count",
                32: "consumed_token_budget",
                33: "consumed_wall_time_units",
                34: "consumed_provider_calls",
            }[number]
            return (
                details["baseline_budget_id"] != details["mutated_budget_id"]
                and expected_field in details["mutated_counter_fields"]
                and details["validation_report_id"] in case_result.evidence_refs
                and details["validation_target"] == "FractalRuntimeBudgetV02"
                and bool(details["reason_codes"])
                and _empty_created_delta_valid_v02(details["created_objects"])
            )
        if number == 31:
            created = details["created_objects"]
            return (
                details["validation_report_id"] in case_result.evidence_refs
                and details["source_context_id"] in case_result.evidence_refs
                and details["topology_id"] in case_result.evidence_refs
                and details["topology_artifact_id"] in case_result.evidence_refs
                and details["queue_capacity"]
                == details["running_count"] + details["ready_count"]
                and details["pending_count"] >= 1
                and details["deferred_queue_entry_ids"]
                == [details["deferred_source_queue_id"]]
                and details["predecessor_queue_id"]
                == details["deferred_source_queue_id"]
                and details["t03_decision_id"] in case_result.evidence_refs
                and details["deferred_successor_queue_id"] in case_result.evidence_refs
                and details["deferred_successor_artifact_id"] in case_result.evidence_refs
                and details["admission_round"] > 0
                and details["deferred_state"] == "PENDING"
                and details["queue_reason_codes"]
                == ["g2d_transition_backpressure_deferred"]
                and details["no_work_dropped"] is True
                and type(created) is dict
                and created["before_ids"] == [details["deferred_source_queue_id"]]
                and created["created_ids"]
                == [
                    details["deferred_successor_queue_id"],
                    details["deferred_successor_artifact_id"],
                ]
                and created["created_count"] == 2
            )
        if number == 35:
            rows = details["mutation_rows"]
            return (
                type(rows) is list
                and len(rows) == 12
                and details["mutation_count"] == 12
                and details["baseline_context_validation_id"] in case_result.evidence_refs
                and [row[0] for row in rows]
                == [
                    "child_scope_ref", "child_allowed_capability_ids",
                    "child_forbidden_claims", "child_ttl_units",
                    "parent_scope_ref", "parent_budget_id", "budget_owner",
                    "budget_predecessor", "budget_event", "budget_state",
                    "budget_borrowing", "budget_allocation_parent",
                ]
                and all(row[1] in case_result.evidence_refs and bool(row[2]) for row in rows)
                and _empty_created_delta_valid_v02(details["created_objects"])
            )
        if number in {36, 37, 38}:
            expected_reason = {
                36: "g2d_no_progress_deadend",
                37: "g2d_no_progress_deadend",
                38: "g2d_resolvable_input_needs_user",
            }[number]
            return (
                details["queue_validation_report_id"] in case_result.evidence_refs
                and details["source_validation_report_id"] in case_result.evidence_refs
                and details["observation_id"] in case_result.evidence_refs
                and details["observation_validation_report_id"] in case_result.evidence_refs
                and details["derived_terminal_state"] == case_result.observed_outcome
                and (
                    details["revision_index"] == details["max_revise_count"] + 1
                    if number == 36
                    else details["revision_index"] <= details["max_revise_count"]
                )
                and (
                    details["consecutive_non_positive_count"]
                    == details["max_revise_count"]
                    if number == 37
                    else details["consecutive_non_positive_count"] == 0
                )
                and expected_reason in details["reason_codes"]
            )
        if number in {39, 40}:
            expected_child = "DEGRADED" if number == 39 else "BLOCKED"
            expected_reason = (
                "g2d_partial_failure_recorded"
                if number == 39
                else "g2d_required_child_failure"
            )
            terminal_rows = details["terminal_queue_rows"]
            activation_row = details["activation_causal_row"]
            common_valid = (
                _prefixed_sha256_valid_v02(details["child_input_id"], "frcellin_v02:")
                and details["baseline_child_result_id"] != details["attempted_child_result_id"]
                and details["attempted_child_result_id"] in case_result.evidence_refs
                and details["attempted_outcome"] == expected_child
                and type(terminal_rows) is list
                and len(terminal_rows) == 4
                and terminal_rows[0][1:] == [expected_child, [expected_reason]]
                and terminal_rows[-1][1:] == [expected_child, [expected_reason]]
                and all(row[0] and row[1] in fr.NODE_TERMINAL_OUTCOMES for row in terminal_rows)
                and details["result_proposal_id"] in case_result.evidence_refs
                and details["post_vv_report_id"] in case_result.evidence_refs
                and details["gt_report_id"] in case_result.evidence_refs
                and details["proposal_validation_report_id"] in case_result.evidence_refs
                and details["post_vv_validation_report_id"] in case_result.evidence_refs
                and details["gt_validation_report_id"] in case_result.evidence_refs
                and details["child_validation_report_id"] in case_result.evidence_refs
                and details["child_structural_validation_report_id"] in case_result.evidence_refs
                and details["result_artifact_id"] in case_result.evidence_refs
                and type(activation_row) is list
                and len(activation_row) == 8
                and activation_row[1] in case_result.evidence_refs
                and activation_row[2] == "/planned_child_cell_id"
                and activation_row[4] in case_result.evidence_refs
                and activation_row[5:] == [
                    "CHILD_ACTIVATION",
                    "USED",
                    "used:g2d_planned_child_activation",
                ]
                and details["child_reason_codes"] == [expected_reason]
                and details["partial_failure_id"] in case_result.evidence_refs
                and details["partial_failure_validation_report_id"] in case_result.evidence_refs
                and details["parent_disposition"] == case_result.observed_outcome
                and details["required_child"] is True
                and _single_created_delta_valid_v02(
                    details["created_result_delta"],
                    details["attempted_child_result_id"],
                )
                and _single_created_delta_valid_v02(
                    details["created_partial_failure_delta"],
                    details["partial_failure_id"],
                )
                and _empty_created_delta_valid_v02(details["created_causal_delta"])
            )
            if number == 39:
                return (
                    common_valid
                    and details["safe_sibling_input_id"]
                    in case_result.evidence_refs
                    and details["safe_sibling_result_id"]
                    in case_result.evidence_refs
                    and details["safe_sibling_result_id"]
                    != details["attempted_child_result_id"]
                    and details["safe_sibling_result_artifact_id"]
                    in case_result.evidence_refs
                    and details["safe_sibling_outcome"] == "COMPLETED"
                    and bool(details["safe_sibling_evidence_refs"])
                    and all(
                        item in case_result.evidence_refs
                        for item in details["safe_sibling_evidence_refs"]
                    )
                    and len(details["safe_sibling_report_refs"]) == 3
                    and all(
                        item in case_result.evidence_refs
                        for item in details["safe_sibling_report_refs"]
                    )
                    and details["safe_sibling_structural_validation_id"]
                    in case_result.evidence_refs
                    and details["safe_sibling_context_validation_id"]
                    in case_result.evidence_refs
                    and _sha256_text_valid_v02(
                        details["safe_sibling_before_sha256"]
                    )
                    and details["safe_sibling_before_sha256"]
                    == details["safe_sibling_after_sha256"]
                    and details["safe_sibling_unchanged"] is True
                    and _empty_created_delta_valid_v02(
                        details["safe_sibling_result_delta"]
                    )
                    and _empty_created_delta_valid_v02(
                        details["safe_sibling_causal_delta"]
                    )
                    and details["partial_failure_sibling_independent"] is True
                )
            return (
                common_valid
                and details["gate_disposition"]
                == "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
                and details["gate_reason_codes"] == ["g2d_required_child_failure"]
                and bool(details["gate_evidence_refs"])
                and all(
                    item in case_result.evidence_refs
                    for item in details["gate_evidence_refs"]
                )
                and details["t06_decision_id"] in case_result.evidence_refs
                and details["validating_queue_id"] in case_result.evidence_refs
                and details["validating_artifact_id"] in case_result.evidence_refs
                and details["terminal_decision_id"] in case_result.evidence_refs
                and details["blocked_queue_id"] in case_result.evidence_refs
                and details["blocked_artifact_id"] in case_result.evidence_refs
                and details["blocked_validation_id"] in case_result.evidence_refs
                and _empty_created_delta_valid_v02(details["no_child_invocation_delta"])
                and _empty_created_delta_valid_v02(details["no_child_result_delta"])
                and _empty_created_delta_valid_v02(
                    details["no_child_partial_failure_delta"]
                )
                and _single_created_delta_valid_v02(
                    details["no_child_terminal_delta"],
                    details["blocked_queue_id"],
                )
                and details["merge_queue_id"] in case_result.evidence_refs
                and details["merge_validation_id"] in case_result.evidence_refs
                and details["merge_decision_is_none"] is True
                and details["malformed_axis"]
                == "/current_entry/planned_child_cell_id"
                and details["malformed_validation_id"] in case_result.evidence_refs
                and bool(details["malformed_reason_codes"])
                and bool(details["malformed_error"])
                and _empty_created_delta_valid_v02(details["malformed_terminal_delta"])
                and _empty_created_delta_valid_v02(details["malformed_causal_delta"])
                and _empty_created_delta_valid_v02(details["malformed_bundle_delta"])
            )
        rows = details["mutation_rows"]
        return (
            number == 41
            and type(rows) is list
            and len(rows) == 6
            and details["mutation_count"] == 6
            and [row[0] for row in rows]
            == [
                "authority_created",
                "permission_created",
                "action_commit_packet_created",
                "receipt_created",
                "final_output_created",
                "real_world_effects_count",
            ]
            and all(row[1] in case_result.evidence_refs and bool(row[2]) for row in rows)
            and _empty_created_delta_valid_v02(details["no_created_objects"])
        )
    if details["case_number"] != number:
        return False
    if details["complete_profile_validation_id"] not in case_result.evidence_refs:
        return False
    return _matrix_proof_valid_v02(
        number=number,
        details=details,
        evidence_refs=case_result.evidence_refs,
    )


def _case_result_valid_v02(
    value: object,
    *,
    spec: _CaseSpecV02,
    position: int,
) -> bool:
    if not _case_result_types_valid_v02(value):
        return False
    assert type(value) is FractalRuntimeG2DCaseResultV02
    if (
        value.case_id != spec.case_id
        or value.case_class != spec.case_class
        or value.expected_outcome != spec.expected_outcome
        or value.observed_outcome != value.expected_outcome
        or value.final_status != "PASS"
        or value.reason_codes != ()
        or any(getattr(value, name) != 0 for name in _ZERO_COUNTER_FIELD_NAMES)
        or not value.evidence_refs
        or len(value.evidence_refs) != len(set(value.evidence_refs))
    ):
        return False
    positive = position < 10
    if positive:
        expected_domain, expected_mode, _narrow, _action = _POSITIVE_MODE_ROWS[position]
        if (
            value.domain_id != expected_domain
            or value.accepted_mode != expected_mode
            or value.source_family_sha256 is None
            or len(value.source_family_sha256) != 64
            or value.topology_id is None
            or value.runtime_report_id is None
            or value.external_validation_report_id is None
            or value.topology_created_count != 1
        ):
            return False
    elif (
        value.domain_id is not None
        or value.accepted_mode is not None
        or value.source_family_sha256 is not None
        or value.topology_id is not None
        or value.runtime_report_id is not None
        or value.external_validation_report_id is not None
        or value.topology_created_count != 0
    ):
        return False
    try:
        material = json.loads(value.evidence_material_json)
    except (TypeError, ValueError):
        return False
    if type(material) is not dict:
        return False
    if canonical_json_bytes_v01(material).decode("ascii") != value.evidence_material_json:
        return False
    if hashlib.sha256(canonical_json_bytes_v01(material)).hexdigest() != value.evidence_sha256:
        return False
    if (
        material.get("case_id") != value.case_id
        or material.get("case_class") != value.case_class
        or material.get("expected_outcome") != value.expected_outcome
        or material.get("observed_outcome") != value.observed_outcome
        or material.get("evidence_refs") != list(value.evidence_refs)
        or not _proof_contract_valid_v02(
            case_result=value,
            proof=material.get("proof"),
            position=position,
        )
    ):
        return False
    return True


def validate_fractal_runtime_g2_d_report_v02(
    value: object,
) -> tuple[str, ...]:
    try:
        if type(value) is not FractalRuntimeG2DReportV02:
            raise ValueError
        if (
            value.report_version != REPORT_VERSION
            or value.profile_id != PROFILE_ID
            or value.domain_order != DOMAIN_ORDER
            or value.case_order != tuple(item.case_id for item in _CASE_SPECS)
            or type(value.case_results) is not tuple
            or len(value.case_results) != 72
            or tuple(item.case_id for item in value.case_results) != value.case_order
            or len(set(value.case_order)) != 72
            or value.constructive_case_count != 36
            or value.negative_case_count != 36
            or value.domain_positive_case_count != 10
            or value.accepted_bundle_count != 10
            or value.counterfactual_case_count != 2
            or value.topology_created_count != 10
            or value.final_status != "PASS"
            or value.reason_codes != ()
            or any(getattr(value, name) != 0 for name in _ZERO_COUNTER_FIELD_NAMES)
        ):
            raise ValueError
        if any(
            not _case_result_valid_v02(item, spec=spec, position=position)
            for position, (item, spec) in enumerate(
                zip(value.case_results, _CASE_SPECS, strict=True)
            )
        ):
            raise ValueError
        constructive = tuple(
            index + 1
            for index, item in enumerate(value.case_results)
            if item.case_class == "CONSTRUCTIVE"
        )
        negative = tuple(
            index + 1
            for index, item in enumerate(value.case_results)
            if item.case_class == "NEGATIVE"
        )
        if (
            constructive != _CONSTRUCTIVE_CASE_NUMBERS
            or negative != _NEGATIVE_CASE_NUMBERS
            or sum(item.topology_created_count for item in value.case_results) != 10
            or value.report_id != _report_identity_v02(value)
        ):
            raise ValueError
        return ()
    except Exception:
        return ("g2d5_report_invalid",)


def fractal_runtime_g2_d_report_to_plain_data_v02(
    report: FractalRuntimeG2DReportV02,
) -> dict[str, object]:
    if type(report) is not FractalRuntimeG2DReportV02:
        raise TypeError("report_type_invalid")
    plain = _plain_value_v02(report)
    if type(plain) is not dict:
        raise TypeError("report_projection_invalid")
    return plain


def _fractal_runtime_g2_d_report_from_plain_data_v02(
    value: object,
) -> FractalRuntimeG2DReportV02:
    if type(value) is not dict:
        raise TypeError("report_plain_type_invalid")
    report_fields = {item.name for item in fields(FractalRuntimeG2DReportV02)}
    case_fields = {item.name for item in fields(FractalRuntimeG2DCaseResultV02)}
    if set(value) != report_fields or type(value.get("case_results")) is not list:
        raise ValueError("report_plain_geometry_invalid")
    cases: list[FractalRuntimeG2DCaseResultV02] = []
    for row in value["case_results"]:
        if type(row) is not dict or set(row) != case_fields:
            raise ValueError("case_plain_geometry_invalid")
        case_data = dict(row)
        case_data["evidence_refs"] = tuple(case_data["evidence_refs"])
        case_data["reason_codes"] = tuple(case_data["reason_codes"])
        cases.append(FractalRuntimeG2DCaseResultV02(**case_data))
    report_data = dict(value)
    report_data["domain_order"] = tuple(report_data["domain_order"])
    report_data["case_order"] = tuple(report_data["case_order"])
    report_data["case_results"] = tuple(cases)
    report_data["reason_codes"] = tuple(report_data["reason_codes"])
    return FractalRuntimeG2DReportV02(**report_data)


def render_fractal_runtime_g2_d_v02(
    report: FractalRuntimeG2DReportV02,
) -> str:
    if validate_fractal_runtime_g2_d_report_v02(report):
        raise ValueError("g2d5_report_invalid")
    return json.dumps(
        fractal_runtime_g2_d_report_to_plain_data_v02(report),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"


def main() -> int:
    try:
        report = collect_fractal_runtime_g2_d_v02()
        if validate_fractal_runtime_g2_d_report_v02(report):
            return 1
        print(render_fractal_runtime_g2_d_v02(report), end="")
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
