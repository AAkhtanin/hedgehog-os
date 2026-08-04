from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, ValidationError

from hedgehog.kernel.abi_v01 import KernelArtifactV01, build_kernel_artifact_v01
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.transition_registry_v01 import TransitionDecisionV01


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/fractal_runtime_v02.py"
SCHEMA_PATH = ROOT / "schemas/fractal_runtime_v02.schema.json"
PREFLIGHT_PATH = ROOT / "docs/fractal_runtime_v0_2_g2_d_preflight_v01.md"
fr = importlib.import_module("hedgehog.kernel.fractal_runtime_v02")


def _plain(value: object, identity_name: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for item in fields(type(value)):
        if item.name == identity_name:
            continue
        current = getattr(value, item.name)
        result[item.name] = list(current) if type(current) is tuple else current
    return result


def _seal(value: object) -> object:
    row = next(item for item in fr.IDENTITY_PROFILE_ROWS_V02 if item[0] is type(value))
    _cls, identity_name, domain, prefix = row
    digest = domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(_plain(value, identity_name)),
    )
    return replace(value, **{identity_name: prefix + digest})


def _validation_reasons(value: object) -> tuple[str, ...]:
    validator = FUNCTION_FAMILIES[type(value)][0]
    result = validator(value)
    return result if type(value) is fr.FractalRuntimeValidationReportV02 else result.reason_codes


def _preflight_annotation_rows(class_name: str) -> tuple[tuple[str, str], ...]:
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    match = re.search(rf"\n{class_name}\((.*?)\n\)", preflight, re.DOTALL)
    assert match is not None
    body = match.group(1)
    starts = list(re.finditer(r"\b([a-z][a-z0-9_]*)\s*:\s*", body))
    rows: list[tuple[str, str]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(body)
        annotation = body[start.end():end].strip().rstrip(",").strip()
        rows.append((start.group(1), re.sub(r"\s+", "", annotation)))
    return tuple(rows)


def _same_type_alternate(value: object, field_name: str) -> object:
    current = getattr(value, field_name)
    if type(current) is bool:
        return not current
    if type(current) is int:
        return current + 1
    if type(current) is str:
        return current + ":alternate"
    if current is None:
        annotation = type(value).__annotations__[field_name]
        return 1 if "int" in annotation else "ref:alternate"
    if type(current) is tuple:
        return current + ("ref:alternate",)
    raise AssertionError((type(value).__name__, field_name, type(current).__name__))


ENUM_CONSTANT_NAMES = (
    "TOPOLOGY_ELIGIBLE_MODES", "NODE_KINDS", "EDGE_KINDS",
    "ASSIGNMENT_KINDS", "CELL_BINDING_CLASSES", "SCOPE_BINDING_CLASSES",
    "BUDGET_BINDING_CLASSES", "BUDGET_STATES", "BUDGET_SCOPES",
    "BUDGET_EVENT_KINDS", "INPUT_REF_DERIVATION_CLASSES",
    "CELL_PROJECTION_CLASSES", "QUEUE_STATES", "NODE_TERMINAL_OUTCOMES",
    "CELL_OUTCOMES", "VALIDATION_STATUSES", "POLICY_PROFILE_IDS",
    "PROFILE_IDS", "TOPOLOGY_VERSIONS", "REPORT_VERSIONS",
    "EXPECTED_OUTPUT_KINDS", "FORBIDDEN_OUTPUT_KINDS", "FAILURE_STAGES",
    "PARENT_DISPOSITIONS", "BACKPRESSURE_REASONS", "VALIDATION_TARGETS",
    "RUNTIME_OUTCOMES", "REPORT_STATUSES", "EXECUTOR_COMPONENT_IDS",
    "SCOPE_RELATIONS", "BUDGET_RELATIONS", "QUEUE_PREDECESSOR_RELATIONS",
    "CAUSAL_DECISION_EFFECTS", "CAUSAL_DISPOSITIONS",
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


def _decision(rule: str, suffix: str) -> TransitionDecisionV01:
    return TransitionDecisionV01(
        decision_id=f"decision:{suffix}",
        registry_id="registry:g2d:test",
        rule_id=f"g2d_{rule}_structural",
        abi_major_version=1,
        source_artifact_type="RuntimeExecutionTopology",
        source_lifecycle_state="VALIDATED",
        actor_role="fractal_runtime_v02",
        attempted_effect="CREATE_TARGET_ARTIFACT",
        target_artifact_type="RuntimeExecutionTopology",
        required_guards=("artifact_valid",),
        satisfied_guards=("artifact_valid",),
        missing_guards=(),
        decision="ALLOW",
        reason_code="g2d_transition_queue_admission_allowed",
        root_commit_required=False,
        root_commit_present=False,
        matched=True,
    )


def _artifact(artifact_id: str, payload: object, parents: tuple[str, ...] = ()) -> KernelArtifactV01:
    return KernelArtifactV01(
        abi_version="1.0",
        artifact_id=artifact_id,
        artifact_type="RuntimeExecutionTopology",
        schema_version="v0.2",
        transaction_id="transaction:test",
        owner_root_id="root:test",
        source_component="fractal_runtime_v02",
        authority_class="NON_AUTHORITY",
        lifecycle_state="VALIDATED",
        payload=payload,
        trace_refs=(artifact_id,),
        parent_refs=parents,
        time_envelope={"time_ref": "time:test"},
    )


def _source_binding(
    policy: fr.FractalRuntimePolicyV02,
    downstream_action_packet_required: bool = False,
) -> fr.RuntimeTopologySourceBindingV02:
    source_decision_artifact_id = "emabi_decision_v01:" + "2" * 64
    post_root_transition_decision_id = "3" * 64
    transition_registry_id = "4" * 64
    route_decision_id = "emdecision_v01:" + "5" * 64
    source_trace_refs = tuple(sorted((
        source_decision_artifact_id,
        route_decision_id,
        transition_registry_id,
        post_root_transition_decision_id,
    )))
    return _seal(fr.RuntimeTopologySourceBindingV02(
        source_binding_id="frsource_v02:" + "0" * 64,
        request_id="request:test",
        transaction_id="transaction:test",
        owning_root_id="root:test",
        domain_id="domain:test",
        accepted_mode="full_fractal",
        accepted_scope_ref="scope:root",
        route_eligibility_artifact_id="emabi_route_v01:" + "6" * 64,
        route_eligibility_artifact_sha256="7" * 64,
        source_decision_artifact_id=source_decision_artifact_id,
        source_proposal_artifact_id="emabi_proposal_v01:" + "8" * 64,
        selected_local_mode_profile_id="emprofile_v01:" + "9" * 64,
        selected_feasibility_row_id="emrow_v01:" + "a" * 64,
        selected_safe_depth_rank=1,
        selected_expected_cost_units=10,
        required_downstream_capability_ids=("capability:source:semantic",),
        source_mode_profile_set_id="emprofiles_v01:" + "b" * 64,
        source_policy_snapshot_id="policy-snapshot:test",
        source_capability_snapshot_id="capability-snapshot:test",
        permitted_narrower_scope_refs=policy.permitted_child_scope_refs,
        source_root_decision_result_id="c" * 64,
        source_root_transition_decision_id="d" * 64,
        proposal_transition_decision_id="e" * 64,
        post_root_transition_decision_id=post_root_transition_decision_id,
        transition_registry_id=transition_registry_id,
        g2c_abi_profile_id="execution_mode_router_g2c_abi_profile_v01",
        downstream_action_packet_required=downstream_action_packet_required,
        runtime_policy_id=policy.policy_id,
        source_time_envelope_ref="emtime_v01:" + "f" * 64,
        source_trace_refs=source_trace_refs,
        source_parent_refs=(source_decision_artifact_id,),
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    ))


def _source_context_for_binding(
    policy: fr.FractalRuntimePolicyV02,
    source: fr.RuntimeTopologySourceBindingV02,
) -> fr.FractalRuntimeSourceContextV02:
    route_artifact = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=source.route_eligibility_artifact_id,
        artifact_type="ExecutionModeRouteEligibility",
        schema_version="v0.1",
        transaction_id=source.transaction_id,
        owner_root_id=source.owning_root_id,
        source_component="root_decision_v01",
        authority_class="ROOT_AUTHORIZED",
        lifecycle_state="ROOT_ACCEPTED",
        payload={"accepted_mode": source.accepted_mode},
        trace_refs=source.source_trace_refs,
        parent_refs=source.source_parent_refs,
        time_envelope={
            "ct_session_anchor": "ct:test",
            "et_observed_at": "2025-01-01T00:00:00Z",
            "freshness_class": "static",
            "kt_asof": "2025-01-01T00:00:00Z",
            "pt_created_at": "2025-01-01T00:00:00Z",
            "ttl_seconds": 3600,
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_to": "2025-01-02T00:00:00Z",
        },
    )
    return fr.FractalRuntimeSourceContextV02(
        transition_registry=SimpleNamespace(registry_id=source.transition_registry_id),
        g2c_source_context=SimpleNamespace(),
        router_input=SimpleNamespace(local_routing_snapshot=SimpleNamespace(
            mode_profile_set_id=source.source_mode_profile_set_id,
            policy_snapshot_id=source.source_policy_snapshot_id,
            capability_snapshot_id=source.source_capability_snapshot_id,
            permitted_narrower_scope_refs=source.permitted_narrower_scope_refs,
            time_envelope_ref=source.source_time_envelope_ref,
        )),
        proposal=SimpleNamespace(
            selected_local_mode_profile_id=source.selected_local_mode_profile_id,
            selected_feasibility_row_id=source.selected_feasibility_row_id,
            selected_safe_depth_rank=source.selected_safe_depth_rank,
            selected_expected_cost_units=source.selected_expected_cost_units,
            required_downstream_capability_ids=source.required_downstream_capability_ids,
        ),
        proposal_artifact=_artifact(source.source_proposal_artifact_id, {}),
        proposal_transition_decision=SimpleNamespace(
            decision_id=source.proposal_transition_decision_id,
        ),
        review_input=SimpleNamespace(),
        decision=SimpleNamespace(
            request_id=source.request_id,
            transaction_id=source.transaction_id,
            owning_root_id=source.owning_root_id,
            domain_id=source.domain_id,
            accepted_mode=source.accepted_mode,
            accepted_scope_ref=source.accepted_scope_ref,
            source_root_transition_decision_id=source.source_root_transition_decision_id,
            downstream_action_packet_required=source.downstream_action_packet_required,
        ),
        root_kernel=SimpleNamespace(),
        root_decision_input=SimpleNamespace(),
        root_decision_result=SimpleNamespace(
            decision_id=source.source_root_decision_result_id,
        ),
        decision_artifact=_artifact(source.source_decision_artifact_id, {}),
        root_route_transition_decision=SimpleNamespace(
            decision_id=source.post_root_transition_decision_id,
        ),
        route_eligibility_artifact=route_artifact,
        runtime_policy=policy,
    )


def _fixture_family(
    *,
    permitted_child_scope_refs: tuple[str, ...] = (),
    downstream_action_packet_required: bool = False,
) -> dict[type[object], object]:
    policy = fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=("capability:source:semantic",),
        permitted_child_scope_refs=permitted_child_scope_refs,
    )
    source = _source_binding(policy, downstream_action_packet_required)
    root_cell_id = fr.derive_fractal_root_cell_id_v02(
        source_binding_id=source.source_binding_id,
        runtime_policy_id=policy.policy_id,
        accepted_mode=source.accepted_mode,
        accepted_scope_ref=source.accepted_scope_ref,
    )
    seed = fr.build_runtime_topology_seed_v02(source, policy, root_cell_id=root_cell_id)
    allocated = fr.build_fractal_runtime_budget_v02(
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
    active = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=allocated,
        owning_cell_id=root_cell_id,
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
    created = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=active,
        owning_cell_id=root_cell_id,
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
    node_rows = dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)[source.accepted_mode]
    nodes = tuple(
        fr.build_runtime_topology_node_v02(
            seed,
            source,
            policy,
            canonical_index=row[0],
            node_kind=row[1],
            depth=0,
            scope_ref=source.accepted_scope_ref,
            cell_binding_class=row[2],
            scope_binding_class=row[3],
            budget_binding_class=row[4],
            required_capability_ids=source.required_downstream_capability_ids if row[5] == ("SRC_CAPS",) else row[5],
            input_ref_derivation_class=row[8],
        )
        for row in node_rows
    )
    edge_rows = dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)[source.accepted_mode]
    edges = tuple(
        fr.build_runtime_topology_edge_v02(
            seed,
            nodes[row[2]],
            nodes[row[3]],
            edge_kind=row[4],
            canonical_index=row[0],
            cell_projection_class=row[1],
        )
        for row in edge_rows
    )
    assignment_rows = dict(fr.MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[source.accepted_mode]
    assignments = tuple(
        fr.build_runtime_assignment_v02(
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
    topology = fr.build_runtime_execution_topology_v02(
        source,
        seed,
        policy,
        nodes=nodes,
        edges=edges,
        assignments=assignments,
        root_cell_id=root_cell_id,
        global_budget=allocated,
        time_envelope_ref=source.source_time_envelope_ref,
    )
    child_ids = tuple(
        fr.derive_fractal_child_cell_id_v02(
            topology_seed_id=seed.topology_seed_id,
            parent_cell_id=root_cell_id,
            canonical_child_index=index,
            accepted_mode=source.accepted_mode,
            selected_local_mode_profile_id=source.selected_local_mode_profile_id,
            source_mode_profile_set_id=source.source_mode_profile_set_id,
            child_scope_ref=source.accepted_scope_ref,
            runtime_policy_id=policy.policy_id,
            required_capability_ids=source.required_downstream_capability_ids,
            forbidden_claims=policy.forbidden_claims,
            child_depth=1,
        )
        for index in (0, 1)
    )
    initial_decisions = tuple(_decision("t02", f"t02-{index}") for index in range(len(nodes)))
    initial_entries = tuple(
        fr.build_fractal_cell_queue_entry_v02(
            topology,
            seed,
            None,
            node,
            created,
            created,
            cell_id=root_cell_id,
            parent_cell_id=None,
            planned_child_cell_id=child_ids[index - 1] if index in {1, 2} else None,
            cell_depth=0,
            scope_ref=source.accepted_scope_ref,
            predecessor=None,
            transition_decision=initial_decisions[index],
            activation_parent_artifact=None,
            local_child_result=None,
            local_child_result_artifact=None,
            cell_instantiation_order=(root_cell_id,),
            projected_node_ids=tuple(item.node_id for item in nodes),
            round_start_queue_entries=(),
            queue_reason_codes=(),
            observed_output_refs=(),
            observed_evidence_refs=(),
            advisory_refs=(),
        )
        for index, node in enumerate(nodes)
    )
    cell_input = fr.build_fractal_cell_input_v02(
        topology,
        cell_id=root_cell_id,
        parent_cell_id=None,
        scope_projection=None,
        scope_ref=source.accepted_scope_ref,
        cell_budget=created,
        global_budget=created,
        initial_queue_entries=initial_entries,
        required_queue_entries=initial_entries,
        cell_depth=0,
        requested_child_count=2,
        ordered_planned_child_cell_ids=child_ids,
        ordered_nodes=nodes,
        evidence_refs=("evidence:source",),
        context_refs=("context:source",),
        time_envelope_ref=source.source_time_envelope_ref,
    )
    child_allocated = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=created,
        predecessor_budget=None,
        owning_cell_id=child_ids[0],
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=cell_input,
        canonical_child_index=0,
        allocation_queue_entries=initial_entries,
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    scope = fr.build_parent_child_scope_projection_v02(
        topology,
        source,
        parent_cell_id=root_cell_id,
        child_cell_id=child_ids[0],
        parent_scope_ref="scope:root",
        child_scope_ref="scope:root",
        parent_allowed_capability_ids=policy.allowed_capability_ids,
        child_allowed_capability_ids=policy.allowed_capability_ids,
        parent_forbidden_claims=policy.forbidden_claims,
        child_forbidden_claims=policy.forbidden_claims,
        parent_ttl_units=10,
        child_ttl_units=9,
        parent_budget=created,
        child_budget=child_allocated,
        global_budget=created,
        child_depth=1,
    )
    queue_pass = fr.build_fractal_runtime_validation_report_v02(
        validation_target="FractalCellQueueEntryV02",
        validated_object_id=initial_entries[0].queue_entry_id,
        failure_stage="NONE",
        reason_codes=(),
        source_reason_codes=(),
    )
    revise = fr.build_fractal_revise_observation_v02(
        topology,
        cell_input,
        initial_entries[0],
        queue_pass,
        revision_index=1,
        newly_validated_evidence_count=1,
        newly_resolved_constraints_count=0,
        newly_accepted_outputs_count=0,
        newly_introduced_conflicts_count=0,
        consecutive_non_positive_count=0,
        max_consecutive_non_positive_count=2,
        cell_budget_before=created,
        global_budget_before=created,
    )
    deferred = _seal(replace(
        initial_entries[0],
        queue_entry_id="frqueue_v02:" + "0" * 64,
        queue_reason_codes=("g2d_transition_backpressure_deferred",),
    ))
    ready_entries = tuple(
        _seal(replace(
            initial_entries[index],
            queue_entry_id="frqueue_v02:" + "0" * 64,
            state="READY",
            prior_state="PENDING",
            predecessor_queue_entry_id=initial_entries[index].queue_entry_id,
            predecessor_relation="EXACT_IMMEDIATE_PREDECESSOR",
            transition_decision_id=f"decision:t04-{index}",
            snapshot_sequence=1,
            admission_round=1,
            lineage_refs=initial_entries[index].lineage_refs + (initial_entries[index].queue_entry_id,),
        ))
        for index in range(policy.max_parallelism)
    )
    backpressure = fr.build_fractal_backpressure_state_v02(
        topology,
        policy,
        created,
        queue_entries=(*ready_entries, deferred),
        evaluated_round=1,
    )
    terminal_decisions = tuple(_decision("t08", f"t08-{index}") for index in range(len(nodes)))
    terminal_entries = tuple(
        _seal(replace(
            entry,
            queue_entry_id="frqueue_v02:" + "0" * 64,
            state="COMPLETED",
            prior_state="VALIDATING",
            predecessor_queue_entry_id=entry.queue_entry_id,
            predecessor_relation="EXACT_IMMEDIATE_PREDECESSOR",
            transition_decision_id=terminal_decisions[index].decision_id,
            snapshot_sequence=1,
            admission_round=1,
            observed_output_refs=(f"output:{index}",),
            observed_evidence_refs=(f"evidence:{index}",),
            lineage_refs=entry.lineage_refs + (entry.queue_entry_id, f"output:{index}", f"evidence:{index}"),
        ))
        for index, entry in enumerate(initial_entries)
    )
    final_decision = _decision("t08", "root-finalize")
    final_budget = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=seed,
        allocation_parent_budget=None,
        predecessor_budget=created,
        owning_cell_id=root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="FINAL",
        budget_event_kind="FINALIZE",
        budget_context_input=cell_input,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=final_decision,
        paired_cell_budget=None,
        child_result=None,
    )
    pre_result = fr.build_fractal_runtime_validation_report_v02(
        validation_target="CELL_RESULT_PRECONDITIONS",
        validated_object_id="proposal:test",
        failure_stage="NONE",
        reason_codes=(),
        source_reason_codes=(),
    )
    result = fr.build_fractal_cell_result_v02(
        topology,
        cell_input,
        terminal_entries,
        (),
        accepted_output_refs=("output:root",),
        evidence_refs=("evidence:root",),
        pre_result_validation_report=pre_result,
        post_vv_report={"vv_report_id": "vv:test"},
        gt_advisory_report={"gt_report_id": "gt:test", "confidence": 1.0},
        partial_failures=(),
        allocated_cell_budget=allocated,
        final_cell_budget=final_budget,
        global_budget=final_budget,
    )
    child_final = _seal(replace(
        child_allocated,
        budget_id="frbudget_v02:" + "0" * 64,
        predecessor_budget_id=created.budget_id,
        budget_state="FINAL",
        budget_event_kind="FINALIZE",
        budget_event_ref="decision:child-finalize",
    ))
    child_global = _seal(replace(
        created,
        budget_id="frbudget_v02:" + "0" * 64,
        predecessor_budget_id=created.budget_id,
        budget_event_kind="FINALIZE",
        budget_event_ref="decision:child-finalize",
    ))
    child_result = _seal(fr.FractalCellResultV02(
        result_id="frcellresult_v02:" + "0" * 64,
        topology_id=topology.topology_id,
        topology_seed_id=seed.topology_seed_id,
        cell_id=child_ids[0],
        parent_cell_id=root_cell_id,
        cell_depth=1,
        cell_input_id="frcellin_v02:" + "2" * 64,
        ordered_terminal_queue_entry_ids=(terminal_entries[0].queue_entry_id,),
        ordered_child_result_ids=(),
        outcome="BLOCKED",
        accepted_output_refs=(),
        evidence_refs=("evidence:child",),
        pre_result_validation_report_id=pre_result.validation_report_id,
        post_vv_report_ref="vv:child",
        gt_advisory_ref="gt:child",
        partial_failure_ids=(),
        allocated_cell_budget_id=child_allocated.budget_id,
        final_cell_budget_id=child_final.budget_id,
        global_budget_id=child_global.budget_id,
        scope_ref="scope:root",
        reason_codes=("g2d_required_child_failure",),
        source_reason_codes=(),
        trace_refs=(
            topology.topology_id,
            "frcellin_v02:" + "2" * 64,
            terminal_entries[0].queue_entry_id,
            child_allocated.budget_id,
            child_final.budget_id,
            child_global.budget_id,
            pre_result.validation_report_id,
            "vv:child",
            "gt:child",
        ),
        parent_return_required=True,
        root_review_required=True,
        authority_created=False,
        permission_created=False,
        action_commit_packet_created=False,
        receipt_created=False,
        final_output_created=False,
        drs_write_created=False,
        real_world_effects_count=0,
    ))
    partial = fr.build_fractal_partial_failure_record_v02(
        topology,
        cell_input,
        child_result,
        failure_stage="CELL_RESULT",
        reason_codes=("g2d_required_child_failure",),
        source_reason_codes=(),
        evidence_refs=child_result.evidence_refs,
        allocated_cell_budget=child_allocated,
        final_cell_budget=child_final,
        global_budget=child_global,
        required_child=True,
        sibling_independent=True,
    )
    topology_artifact = _artifact("artifact:topology", fr.runtime_execution_topology_to_plain_data_v02(topology))
    queue_artifacts = tuple(
        _artifact(f"artifact:queue:{index}", fr.fractal_cell_queue_entry_to_plain_data_v02(entry), (topology_artifact.artifact_id,))
        for index, entry in enumerate(terminal_entries)
    )
    result_artifact = _artifact("artifact:result:root", fr.fractal_cell_result_to_plain_data_v02(result), tuple(item.artifact_id for item in queue_artifacts))
    trace = fr.build_fractal_runtime_trace_v02(
        topology,
        source,
        topology_artifact=topology_artifact,
        queue_entries=terminal_entries,
        queue_artifacts=queue_artifacts,
        state_transition_decisions=terminal_decisions,
        cell_inputs=(cell_input,),
        cell_results=(result,),
        result_artifacts=(result_artifact,),
        runtime_abi_artifacts=(*queue_artifacts, result_artifact),
        scope_projections=(scope,),
        revise_observations=(revise,),
        partial_failures=(),
        backpressure_states=(backpressure,),
        budgets=(allocated, active, created, child_allocated, final_budget),
        topology_transition_decision=_decision("t01", "topology"),
        parent_return_transition_decision=_decision("t13", "parent-return"),
        root_result_artifact=result_artifact,
    )
    report = fr.build_fractal_runtime_report_v02(
        topology,
        topology_artifact,
        source,
        ordered_cell_results=(result,),
        queue_entries=terminal_entries,
        backpressure_states=(backpressure,),
        runtime_trace=trace,
        final_budget=final_budget,
        parent_return_transition_decision=_decision("t13", "parent-return"),
        root_result_artifact=result_artifact,
    )
    fixtures = {
        fr.FractalRuntimePolicyV02: policy,
        fr.FractalRuntimeBudgetV02: allocated,
        fr.RuntimeTopologySourceBindingV02: source,
        fr.RuntimeTopologySeedV02: seed,
        fr.RuntimeTopologyNodeV02: nodes[0],
        fr.RuntimeTopologyEdgeV02: edges[0],
        fr.RuntimeAssignmentV02: assignments[0],
        fr.RuntimeExecutionTopologyV02: topology,
        fr.ParentChildScopeProjectionV02: scope,
        fr.FractalCellInputV02: cell_input,
        fr.FractalCellQueueEntryV02: initial_entries[0],
        fr.FractalReviseObservationV02: revise,
        fr.FractalPartialFailureRecordV02: partial,
        fr.FractalBackpressureStateV02: backpressure,
        fr.FractalCellResultV02: result,
        fr.FractalRuntimeTraceV02: trace,
        fr.FractalRuntimeReportV02: report,
        fr.FractalRuntimeValidationReportV02: pre_result,
    }
    for cls, value in fixtures.items():
        validation = FUNCTION_FAMILIES[cls][0](value)
        if cls is fr.FractalRuntimeValidationReportV02:
            assert validation == ()
        else:
            assert validation.status == "PASS", (cls.__name__, validation.reason_codes)
    return fixtures


def _topology_components(fixtures: dict[type[object], object]) -> tuple[tuple[object, ...], tuple[object, ...], tuple[object, ...]]:
    policy = fixtures[fr.FractalRuntimePolicyV02]
    source = fixtures[fr.RuntimeTopologySourceBindingV02]
    seed = fixtures[fr.RuntimeTopologySeedV02]
    node_rows = dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)[source.accepted_mode]
    nodes = tuple(
        fr.build_runtime_topology_node_v02(
            seed,
            source,
            policy,
            canonical_index=row[0],
            node_kind=row[1],
            depth=0,
            scope_ref=source.accepted_scope_ref,
            cell_binding_class=row[2],
            scope_binding_class=row[3],
            budget_binding_class=row[4],
            required_capability_ids=source.required_downstream_capability_ids if row[5] == ("SRC_CAPS",) else row[5],
            input_ref_derivation_class=row[8],
        )
        for row in node_rows
    )
    edge_rows = dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)[source.accepted_mode]
    edges = tuple(
        fr.build_runtime_topology_edge_v02(
            seed,
            nodes[row[2]],
            nodes[row[3]],
            edge_kind=row[4],
            canonical_index=row[0],
            cell_projection_class=row[1],
        )
        for row in edge_rows
    )
    assignment_rows = dict(fr.MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[source.accepted_mode]
    assignments = tuple(
        fr.build_runtime_assignment_v02(
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
    return nodes, edges, assignments


FUNCTION_FAMILIES = {
    fr.FractalRuntimePolicyV02: (fr.validate_fractal_runtime_policy_v02, fr.fractal_runtime_policy_to_plain_data_v02, fr.rebuild_fractal_runtime_policy_identity_v02),
    fr.FractalRuntimeBudgetV02: (fr.validate_fractal_runtime_budget_v02, fr.fractal_runtime_budget_to_plain_data_v02, fr.rebuild_fractal_runtime_budget_identity_v02),
    fr.RuntimeTopologySourceBindingV02: (fr.validate_runtime_topology_source_binding_v02, fr.runtime_topology_source_binding_to_plain_data_v02, fr.rebuild_runtime_topology_source_binding_identity_v02),
    fr.RuntimeTopologySeedV02: (fr.validate_runtime_topology_seed_v02, fr.runtime_topology_seed_to_plain_data_v02, fr.rebuild_runtime_topology_seed_identity_v02),
    fr.RuntimeTopologyNodeV02: (fr.validate_runtime_topology_node_v02, fr.runtime_topology_node_to_plain_data_v02, fr.rebuild_runtime_topology_node_identity_v02),
    fr.RuntimeTopologyEdgeV02: (fr.validate_runtime_topology_edge_v02, fr.runtime_topology_edge_to_plain_data_v02, fr.rebuild_runtime_topology_edge_identity_v02),
    fr.RuntimeAssignmentV02: (fr.validate_runtime_assignment_v02, fr.runtime_assignment_to_plain_data_v02, fr.rebuild_runtime_assignment_identity_v02),
    fr.RuntimeExecutionTopologyV02: (fr.validate_runtime_execution_topology_v02, fr.runtime_execution_topology_to_plain_data_v02, fr.rebuild_runtime_execution_topology_identity_v02),
    fr.ParentChildScopeProjectionV02: (fr.validate_parent_child_scope_projection_v02, fr.parent_child_scope_projection_to_plain_data_v02, fr.rebuild_parent_child_scope_projection_identity_v02),
    fr.FractalCellInputV02: (fr.validate_fractal_cell_input_v02, fr.fractal_cell_input_to_plain_data_v02, fr.rebuild_fractal_cell_input_identity_v02),
    fr.FractalCellQueueEntryV02: (fr.validate_fractal_cell_queue_entry_v02, fr.fractal_cell_queue_entry_to_plain_data_v02, fr.rebuild_fractal_cell_queue_entry_identity_v02),
    fr.FractalReviseObservationV02: (fr.validate_fractal_revise_observation_v02, fr.fractal_revise_observation_to_plain_data_v02, fr.rebuild_fractal_revise_observation_identity_v02),
    fr.FractalPartialFailureRecordV02: (fr.validate_fractal_partial_failure_record_v02, fr.fractal_partial_failure_record_to_plain_data_v02, fr.rebuild_fractal_partial_failure_record_identity_v02),
    fr.FractalBackpressureStateV02: (fr.validate_fractal_backpressure_state_v02, fr.fractal_backpressure_state_to_plain_data_v02, fr.rebuild_fractal_backpressure_state_identity_v02),
    fr.FractalCellResultV02: (fr.validate_fractal_cell_result_v02, fr.fractal_cell_result_to_plain_data_v02, fr.rebuild_fractal_cell_result_identity_v02),
    fr.FractalRuntimeTraceV02: (fr.validate_fractal_runtime_trace_v02, fr.fractal_runtime_trace_to_plain_data_v02, fr.rebuild_fractal_runtime_trace_identity_v02),
    fr.FractalRuntimeReportV02: (fr.validate_fractal_runtime_report_v02, fr.fractal_runtime_report_to_plain_data_v02, fr.rebuild_fractal_runtime_report_identity_v02),
    fr.FractalRuntimeValidationReportV02: (fr.validate_fractal_runtime_validation_report_v02, fr.fractal_runtime_validation_report_to_plain_data_v02, fr.rebuild_fractal_runtime_validation_report_identity_v02),
}


def test_d1_static_surface_schema_import() -> None:
    assert MODULE_PATH.is_file() and SCHEMA_PATH.is_file()
    assert len(fr.SERIALIZED_G2D_TYPES_V02) == 18
    assert len(fr.RUNTIME_ONLY_G2D_TYPES_V02) == 2
    assert len(fr.G2D_TYPES_V02) == 20
    assert all(item.__dataclass_params__.frozen for item in fr.G2D_TYPES_V02)
    public_functions = [
        name for name, value in vars(fr).items()
        if not name.startswith("_") and inspect.isfunction(value) and value.__module__ == fr.__name__
    ]
    assert len(public_functions) == 74
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    expected_rows = re.findall(r"^\|\s*(\d+)\s*\|\s*D1\s*\|\s*`([^`]+)`\s*\|$", preflight, re.MULTILINE)
    assert len(expected_rows) == 74
    module_tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    actual = {node.name: node for node in module_tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")}
    for _number, signature in expected_rows:
        expected = ast.parse("def " + signature + ":\n pass").body[0]
        current = actual[signature.split("(", 1)[0]]
        assert ast.dump(current.args, include_attributes=False) == ast.dump(expected.args, include_attributes=False)
        assert ast.dump(current.returns, include_attributes=False) == ast.dump(expected.returns, include_attributes=False)
    future_names = re.findall(r"^\|\s*(?:7[5-9]|[89]\d|1(?:0\d|1[0-6]))\s*\|\s*D[2-4T]\s*\|\s*`([a-z0-9_]+)\(", preflight, re.MULTILINE)
    assert future_names and not any(callable(getattr(fr, name, None)) for name in future_names)
    assert not any(hasattr(importlib.import_module("hedgehog.kernel"), name) for name in public_functions)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert len(schema["$defs"]) == 18
    assert "FractalRuntimeSourceContextV02" not in schema["$defs"]
    assert "FractalRuntimeExecutionBundleV02" not in schema["$defs"]


def test_d1_canonical_types_fields_enums() -> None:
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    for cls in fr.G2D_TYPES_V02:
        expected_rows = _preflight_annotation_rows(cls.__name__)
        assert [item.name for item in fields(cls)] == [name for name, _annotation in expected_rows]
        actual_annotations = tuple(
            (name, re.sub(r"\s+", "", annotation))
            for name, annotation in cls.__annotations__.items()
        )
        assert actual_annotations == expected_rows
    assert len(fields(fr.FractalRuntimeBudgetV02)) == 38
    assert len(fields(fr.FractalPartialFailureRecordV02)) == 23
    assert len(fields(fr.FractalBackpressureStateV02)) == 19
    assert len(fields(fr.FractalCellResultV02)) == 32
    assert len(fields(fr.FractalRuntimeTraceV02)) == 23
    assert len(fields(fr.FractalRuntimeReportV02)) == 42
    assert len(fields(fr.FractalCellQueueEntryV02)) == 31
    assert "queue_reason_codes" in fr.FractalCellQueueEntryV02.__annotations__
    assert "deferred_reason_codes" not in fr.FractalCellQueueEntryV02.__annotations__
    assert "allocated_cell_budget_id" in fr.FractalCellResultV02.__annotations__
    assert "final_cell_budget_id" in fr.FractalCellResultV02.__annotations__
    assert "consumed_cell_budget_id" not in MODULE_PATH.read_text(encoding="utf-8")
    assert "FAN_IN_CHILD_SLOT_RETURNS_1_2" in fr.INPUT_REF_DERIVATION_CLASSES
    assert "FAN_IN_CHILD_RESULTS_1_2" not in MODULE_PATH.read_text(encoding="utf-8")
    assert "CELL_TERMINAL_OUTCOME" in fr.CAUSAL_DECISION_EFFECTS
    for name in ENUM_CONSTANT_NAMES:
        match = re.search(rf"^{name}=\(([^)]*)\)$", preflight, re.MULTILINE)
        assert match is not None, name
        expected = tuple(item for item in match.group(1).split(",") if item)
        assert getattr(fr, name) == expected
    module_tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    assignments_by_name = {
        target.id: node.value
        for node in module_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    for name in ("CELL_OUTCOMES", "PARENT_DISPOSITIONS", "RUNTIME_OUTCOMES"):
        assert isinstance(assignments_by_name[name], ast.Tuple)
        assert all(isinstance(item, ast.Constant) for item in assignments_by_name[name].elts)
    assert fr.NODE_OUTPUT_KIND_ROWS_V02 == (
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
    assert fr.CHILD_SLOT_INDEX_ROWS_V02 == (
        (1, "PREDECESSOR_AND_CHILD_SLOT_1", 1, 0, 0),
        (2, "PREDECESSOR_AND_CHILD_SLOT_2", 2, 1, 1),
    )
    assert len(fr.QUEUE_TRANSITION_INPUT_COLUMNS_V02) == 11
    assert fr.QUEUE_TRANSITION_INPUT_ROWS_V02 == (
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
    assert fr.CHILD_RESULT_PARENT_SLOT_OUTCOME_ROWS_V02 == (
        ("COMPLETED", "t06", "t08", "COMPLETED"),
        ("DEGRADED", "t06", "t09", "DEGRADED"),
        ("BLOCKED", "t06", "t10", "BLOCKED"),
        ("NEEDS_USER", "t06", "t11", "NEEDS_USER"),
        ("DEADEND", "t06", "t12", "DEADEND"),
    )
    assert fr.CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02 == (
        ("VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL", "t06", "t10", "BLOCKED"),
        ("RESOLVABLE_INPUT_MISSING", "t06", "t11", "NEEDS_USER"),
        ("NO_PROGRESS_OR_NONRESOLVABLE", "t06", "t12", "DEADEND"),
    )
    assert fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02 == (
        ("completed", "t06", "t08", "COMPLETED"),
        ("degraded", "t06", "t09", "DEGRADED"),
        ("blocked", "t06", "t10", "BLOCKED"),
        ("needs_user", "t06", "t11", "NEEDS_USER"),
        ("deadend", "t06", "t12", "DEADEND"),
    )
    assert fr.PARENT_RETURN_TYPED_INPUT_COMPONENTS_V02 == (
        "parent_return_pre_post_vv_terminal_queue_entries",
        "parent_return_child_results",
        "parent_return_partial_failures",
        "parent_return_result_proposal",
        "parent_return_post_vv_report",
        "parent_return_gt_advisory_report",
        "parent_return_validation_reports",
    )
    assert fr.CHILD_ACTIVATION_GATE_TERMINAL_ROWS_V02[0][0] == "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
    assert "HARD_POLICY_AUTHORITY_SCOPE_IDENTITY_OR_BUDGET_FAILURE" not in MODULE_PATH.read_text(encoding="utf-8")
    assert len(fr.MODE_NODE_TEMPLATE_ROWS_V02) == 5
    assert len(dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)["full_fractal"]) == 7
    assert len(dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)["full_fractal"]) == 10
    assert len(dict(fr.MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)["full_fractal"]) == 7
    assignment_table = next(
        node for node in module_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "MODE_ASSIGNMENT_TEMPLATE_ROWS_V02" for target in node.targets)
    )
    assert not any(isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for node in ast.walk(assignment_table.value))
    for cls_name, groups in fr.BUILDER_FIELD_DERIVATION_ROWS_V02:
        expected = {item.name for item in fields(getattr(fr, cls_name))}
        classified = [name for _kind, names in groups for name in names]
        assert len(classified) == len(set(classified))
        assert set(classified) == expected


def test_d1_acyclic_identity_and_serialization() -> None:
    fixtures = _fixture_family()
    assert set(fixtures) == set(fr.SERIALIZED_G2D_TYPES_V02)
    for cls, value in fixtures.items():
        validator, serializer, rebuilder = FUNCTION_FAMILIES[cls]
        report_or_reasons = validator(value)
        if cls is fr.FractalRuntimeValidationReportV02:
            assert report_or_reasons == ()
        else:
            assert report_or_reasons.status == "PASS"
            assert report_or_reasons.failure_stage == "NONE"
            assert report_or_reasons.validated_object_id == getattr(value, fields(cls)[0].name)
        plain = serializer(value)
        assert list(plain) == [item.name for item in fields(cls)]
        assert json.loads(json.dumps(plain, allow_nan=False)) == plain
        assert rebuilder(value) == getattr(value, fields(cls)[0].name)
        assert _seal(replace(value, **{fields(cls)[0].name: "x"})) == value
        with pytest.raises(FrozenInstanceError):
            setattr(value, fields(cls)[-1].name, getattr(value, fields(cls)[-1].name))
        wrong_identity = replace(value, **{fields(cls)[0].name: "bad"})
        failure = validator(wrong_identity)
        reasons = failure if cls is fr.FractalRuntimeValidationReportV02 else failure.reason_codes
        assert "g2d_identity_invalid" in reasons or "g2d_identity_mismatch" in reasons
        identity_name = fields(cls)[0].name
        original_identity = getattr(value, identity_name)
        for item in fields(cls)[1:]:
            alternate = _same_type_alternate(value, item.name)
            changed = replace(value, **{item.name: alternate})
            resealed = _seal(replace(changed, **{identity_name: "x"}))
            assert getattr(resealed, identity_name) != original_identity, (cls.__name__, item.name)
            assert "g2d_identity_mismatch" in _validation_reasons(changed), (cls.__name__, item.name)
    policy = fixtures[fr.FractalRuntimePolicyV02]
    assert fr.validate_fractal_runtime_policy_v02(replace(policy, max_depth=True)).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_policy_v02(replace(policy, max_depth=1.0)).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_policy_v02(replace(policy, max_depth=Decimal("1"))).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_policy_v02(replace(policy, policy_version="bad\x00text")).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_policy_v02(replace(policy, allowed_modes=list(policy.allowed_modes))).status == "FAIL_CLOSED"
    class PolicySubclass(fr.FractalRuntimePolicyV02):
        pass
    subclass = PolicySubclass(**{item.name: getattr(policy, item.name) for item in fields(policy)})
    assert fr.validate_fractal_runtime_policy_v02(subclass).status == "FAIL_CLOSED"
    root_expected = "frrootcell_v02:" + domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_ROOT_CELL",
        payload=canonical_json_bytes_v01([
            fixtures[fr.RuntimeTopologySourceBindingV02].source_binding_id,
            policy.policy_id,
            "full_fractal",
            "scope:root",
            "ROOT_CELL",
        ]),
    )
    assert fixtures[fr.RuntimeTopologySeedV02].root_cell_id == root_expected
    child_0 = fr.derive_fractal_child_cell_id_v02(
        topology_seed_id=fixtures[fr.RuntimeTopologySeedV02].topology_seed_id,
        parent_cell_id=root_expected,
        canonical_child_index=0,
        accepted_mode="full_fractal",
        selected_local_mode_profile_id=fixtures[fr.RuntimeTopologySourceBindingV02].selected_local_mode_profile_id,
        source_mode_profile_set_id=fixtures[fr.RuntimeTopologySourceBindingV02].source_mode_profile_set_id,
        child_scope_ref="scope:root",
        runtime_policy_id=policy.policy_id,
        required_capability_ids=("capability:source:semantic",),
        forbidden_claims=policy.forbidden_claims,
        child_depth=1,
    )
    child_1 = fr.derive_fractal_child_cell_id_v02(
        topology_seed_id=fixtures[fr.RuntimeTopologySeedV02].topology_seed_id,
        parent_cell_id=root_expected,
        canonical_child_index=1,
        accepted_mode="full_fractal",
        selected_local_mode_profile_id=fixtures[fr.RuntimeTopologySourceBindingV02].selected_local_mode_profile_id,
        source_mode_profile_set_id=fixtures[fr.RuntimeTopologySourceBindingV02].source_mode_profile_set_id,
        child_scope_ref="scope:root",
        runtime_policy_id=policy.policy_id,
        required_capability_ids=("capability:source:semantic",),
        forbidden_claims=policy.forbidden_claims,
        child_depth=1,
    )
    assert child_0 != child_1
    with pytest.raises(ValueError):
        fr.derive_fractal_child_cell_id_v02(
            topology_seed_id=fixtures[fr.RuntimeTopologySeedV02].topology_seed_id,
            parent_cell_id=root_expected,
            canonical_child_index=2,
            accepted_mode="full_fractal",
            selected_local_mode_profile_id=fixtures[fr.RuntimeTopologySourceBindingV02].selected_local_mode_profile_id,
            source_mode_profile_set_id=fixtures[fr.RuntimeTopologySourceBindingV02].source_mode_profile_set_id,
            child_scope_ref="scope:root",
            runtime_policy_id=policy.policy_id,
            required_capability_ids=("capability:source:semantic",),
            forbidden_claims=policy.forbidden_claims,
            child_depth=1,
        )


def test_d1_guardian_seed_and_topology_cross_bindings() -> None:
    fixtures = _fixture_family()
    policy = fixtures[fr.FractalRuntimePolicyV02]
    source = fixtures[fr.RuntimeTopologySourceBindingV02]
    seed = fixtures[fr.RuntimeTopologySeedV02]
    budget = fixtures[fr.FractalRuntimeBudgetV02]
    topology = fixtures[fr.RuntimeExecutionTopologyV02]
    nodes, edges, assignments = _topology_components(fixtures)
    expected_root = fr.derive_fractal_root_cell_id_v02(
        source_binding_id=source.source_binding_id,
        runtime_policy_id=policy.policy_id,
        accepted_mode=source.accepted_mode,
        accepted_scope_ref=source.accepted_scope_ref,
    )
    assert expected_root == seed.root_cell_id
    assert fr.build_runtime_topology_seed_v02(source, policy, root_cell_id=expected_root) == seed

    forged_root = "frrootcell_v02:" + "f" * 64
    with pytest.raises(ValueError):
        fr.build_runtime_topology_seed_v02(source, policy, root_cell_id=forged_root)
    forged_seed = _seal(replace(
        seed,
        root_cell_id=forged_root,
        trace_refs=seed.trace_refs[:-2] + (forged_root, seed.source_time_envelope_ref),
    ))
    forged_report = fr.validate_runtime_topology_seed_v02(forged_seed)
    assert forged_report.status == "FAIL_CLOSED"
    assert "g2d_root_cell_identity_invalid" in forged_report.reason_codes

    build_kwargs = {
        "nodes": nodes,
        "edges": edges,
        "assignments": assignments,
        "root_cell_id": expected_root,
        "global_budget": budget,
        "time_envelope_ref": source.source_time_envelope_ref,
    }
    rebuilt = fr.build_runtime_execution_topology_v02(source, seed, policy, **build_kwargs)
    assert rebuilt == topology
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(source, seed, policy, **{**build_kwargs, "root_cell_id": forged_root})
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(source, seed, policy, **{**build_kwargs, "time_envelope_ref": "time:foreign"})
    foreign_source = _seal(replace(source, runtime_policy_id="frpolicy_v02:" + "e" * 64))
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(foreign_source, seed, policy, **build_kwargs)
    foreign_policy = _seal(replace(policy, permitted_child_scope_refs=policy.permitted_child_scope_refs + ("scope:foreign",)))
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(source, seed, foreign_policy, **build_kwargs)
    foreign_budget = _seal(replace(budget, topology_seed_id="frseed_v02:" + "e" * 64))
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(source, seed, policy, **{**build_kwargs, "global_budget": foreign_budget})
    with pytest.raises(ValueError):
        fr.build_runtime_execution_topology_v02(source, seed, policy, **{**build_kwargs, "nodes": tuple(reversed(nodes))})


def test_d1_actual_g2c_source_seam_accept_narrow_and_builder_closure() -> None:
    fixtures = _fixture_family()
    policy = fixtures[fr.FractalRuntimePolicyV02]
    source = fixtures[fr.RuntimeTopologySourceBindingV02]
    seed = fixtures[fr.RuntimeTopologySeedV02]
    topology = fixtures[fr.RuntimeExecutionTopologyV02]
    budget = fixtures[fr.FractalRuntimeBudgetV02]
    nodes, edges, assignments = _topology_components(fixtures)

    assert source.accepted_scope_ref == "scope:root"
    assert source.permitted_narrower_scope_refs == ()
    assert policy.permitted_child_scope_refs == ()
    assert source.source_parent_refs == (source.source_decision_artifact_id,)
    assert len(source.source_trace_refs) == 4
    assert source.source_trace_refs == tuple(sorted(set(source.source_trace_refs)))
    assert source.source_decision_artifact_id in source.source_trace_refs
    assert source.transition_registry_id in source.source_trace_refs
    assert source.post_root_transition_decision_id in source.source_trace_refs
    residual = tuple(item for item in source.source_trace_refs if item not in {
        source.source_decision_artifact_id,
        source.transition_registry_id,
        source.post_root_transition_decision_id,
    })
    assert len(residual) == 1
    assert re.fullmatch(r"emdecision_v01:[0-9a-f]{64}", residual[0])
    assert fr.validate_runtime_topology_source_binding_v02(source).status == "PASS"
    assert fr.build_runtime_topology_seed_v02(source, policy, root_cell_id=seed.root_cell_id) == seed
    assert fr.build_runtime_execution_topology_v02(
        source,
        seed,
        policy,
        nodes=nodes,
        edges=edges,
        assignments=assignments,
        root_cell_id=seed.root_cell_id,
        global_budget=budget,
        time_envelope_ref=source.source_time_envelope_ref,
    ) == topology

    built_source = fr.build_runtime_topology_source_binding_v02(
        source_context=_source_context_for_binding(policy, source),
    )
    assert built_source.permitted_narrower_scope_refs == ()
    assert built_source.source_parent_refs == (source.source_decision_artifact_id,)
    assert built_source.source_trace_refs == source.source_trace_refs
    assert fr.validate_runtime_topology_source_binding_v02(built_source).status == "PASS"

    narrow_fixtures = _fixture_family(permitted_child_scope_refs=("scope:root",))
    narrow_policy = narrow_fixtures[fr.FractalRuntimePolicyV02]
    narrow_source = narrow_fixtures[fr.RuntimeTopologySourceBindingV02]
    narrow_seed = narrow_fixtures[fr.RuntimeTopologySeedV02]
    narrow_topology = narrow_fixtures[fr.RuntimeExecutionTopologyV02]
    narrow_budget = narrow_fixtures[fr.FractalRuntimeBudgetV02]
    narrow_nodes, narrow_edges, narrow_assignments = _topology_components(narrow_fixtures)
    assert narrow_source.permitted_narrower_scope_refs == (narrow_source.accepted_scope_ref,)
    assert narrow_policy.permitted_child_scope_refs == narrow_source.permitted_narrower_scope_refs
    assert fr.build_runtime_topology_seed_v02(
        narrow_source,
        narrow_policy,
        root_cell_id=narrow_seed.root_cell_id,
    ) == narrow_seed
    assert fr.build_runtime_execution_topology_v02(
        narrow_source,
        narrow_seed,
        narrow_policy,
        nodes=narrow_nodes,
        edges=narrow_edges,
        assignments=narrow_assignments,
        root_cell_id=narrow_seed.root_cell_id,
        global_budget=narrow_budget,
        time_envelope_ref=narrow_source.source_time_envelope_ref,
    ) == narrow_topology

    def rejected(**changes: object) -> None:
        candidate = _seal(replace(source, **changes))
        assert fr.validate_runtime_topology_source_binding_v02(candidate).status == "FAIL_CLOSED"

    old_three_parents = (
        source.route_eligibility_artifact_id,
        source.source_decision_artifact_id,
        source.source_proposal_artifact_id,
    )
    rejected(source_parent_refs=old_three_parents)
    rejected(source_parent_refs=())
    rejected(source_parent_refs=(source.source_decision_artifact_id, source.source_proposal_artifact_id))
    rejected(source_parent_refs=old_three_parents + ("artifact:extra",))
    rejected(source_trace_refs=source.source_trace_refs[:-1])
    rejected(source_trace_refs=(source.source_trace_refs[0],) * 4)
    rejected(source_trace_refs=tuple(reversed(source.source_trace_refs)))
    no_route_decision = tuple(sorted((
        source.source_decision_artifact_id,
        source.transition_registry_id,
        source.post_root_transition_decision_id,
        "decision:foreign",
    )))
    rejected(source_trace_refs=no_route_decision)
    two_route_decisions = tuple(sorted((
        source.source_decision_artifact_id,
        source.transition_registry_id,
        "emdecision_v01:" + "3" * 64,
        "emdecision_v01:" + "4" * 64,
    )))
    rejected(source_trace_refs=two_route_decisions)
    rejected(source_trace_refs=tuple(sorted(source.source_trace_refs + (source.route_eligibility_artifact_id,))))
    rejected(source_trace_refs=tuple(sorted(source.source_trace_refs + (source.source_proposal_artifact_id,))))
    self_referencing = replace(source, source_trace_refs=tuple(sorted(source.source_trace_refs + (source.source_binding_id,))))
    assert fr.validate_runtime_topology_source_binding_v02(self_referencing).status == "FAIL_CLOSED"

    forced_scope = _seal(replace(source, permitted_narrower_scope_refs=(source.accepted_scope_ref,)))
    assert fr.validate_runtime_topology_source_binding_v02(forced_scope).status == "PASS"
    with pytest.raises(ValueError):
        fr.build_runtime_topology_seed_v02(forced_scope, policy, root_cell_id=seed.root_cell_id)
    foreign_capability = _seal(replace(
        source,
        required_downstream_capability_ids=("capability:foreign",),
    ))
    assert fr.validate_runtime_topology_source_binding_v02(foreign_capability).status == "PASS"
    with pytest.raises(ValueError):
        fr.build_runtime_topology_seed_v02(foreign_capability, policy, root_cell_id=seed.root_cell_id)


def test_d1_action_packet_declaration_preservation() -> None:
    false_fixtures = _fixture_family()
    true_fixtures = _fixture_family(downstream_action_packet_required=True)
    assert true_fixtures == _fixture_family(downstream_action_packet_required=True)

    policy = false_fixtures[fr.FractalRuntimePolicyV02]
    false_source = false_fixtures[fr.RuntimeTopologySourceBindingV02]
    true_source = true_fixtures[fr.RuntimeTopologySourceBindingV02]
    source_schema = Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"][
            "RuntimeTopologySourceBindingV02"
        ]
    )
    assert type(false_source.downstream_action_packet_required) is bool
    assert type(true_source.downstream_action_packet_required) is bool
    assert false_source.downstream_action_packet_required is False
    assert true_source.downstream_action_packet_required is True
    assert true_source == _seal(replace(
        false_source,
        downstream_action_packet_required=True,
    ))
    assert true_source.source_binding_id != false_source.source_binding_id
    for item in fields(fr.RuntimeTopologySourceBindingV02):
        if item.name not in {"source_binding_id", "downstream_action_packet_required"}:
            assert getattr(true_source, item.name) == getattr(false_source, item.name)

    for fixtures, expected in ((false_fixtures, False), (true_fixtures, True)):
        source = fixtures[fr.RuntimeTopologySourceBindingV02]
        seed = fixtures[fr.RuntimeTopologySeedV02]
        topology = fixtures[fr.RuntimeExecutionTopologyV02]
        assert source.downstream_action_packet_required is expected
        assert fr.validate_runtime_topology_source_binding_v02(source).status == "PASS"
        source_schema.validate(fr.runtime_topology_source_binding_to_plain_data_v02(source))
        assert fr.validate_runtime_topology_seed_v02(seed).status == "PASS"
        assert fr.validate_runtime_execution_topology_v02(topology).status == "PASS"
        assert source.authority_created is source.permission_created is False
        assert source.real_world_effects_count == 0
        assert topology.action_commit_packet_created is False
        assert topology.permission_created is False
        assert topology.receipt_created is False
        assert topology.final_output_created is False
        assert topology.drs_write_created is False
        assert topology.authority_created is False
        assert topology.provider_calls == topology.network_calls == 0
        assert topology.real_world_effects_count == 0

        built_source = fr.build_runtime_topology_source_binding_v02(
            source_context=_source_context_for_binding(policy, source),
        )
        assert built_source.downstream_action_packet_required is expected
        assert fr.validate_runtime_topology_source_binding_v02(built_source).status == "PASS"
        source_schema.validate(fr.runtime_topology_source_binding_to_plain_data_v02(built_source))
        built_root_cell_id = fr.derive_fractal_root_cell_id_v02(
            source_binding_id=built_source.source_binding_id,
            runtime_policy_id=policy.policy_id,
            accepted_mode=built_source.accepted_mode,
            accepted_scope_ref=built_source.accepted_scope_ref,
        )
        built_seed = fr.build_runtime_topology_seed_v02(
            built_source,
            policy,
            root_cell_id=built_root_cell_id,
        )
        assert fr.validate_runtime_topology_seed_v02(built_seed).status == "PASS"

    false_plain = fr.runtime_topology_source_binding_to_plain_data_v02(false_source)
    for non_bool in (0, 1, "false", None):
        candidate = _seal(replace(
            false_source,
            downstream_action_packet_required=non_bool,
        ))
        assert fr.validate_runtime_topology_source_binding_v02(candidate).status == "FAIL_CLOSED"
        bad_plain = dict(false_plain)
        bad_plain["downstream_action_packet_required"] = non_bool
        with pytest.raises(ValidationError):
            source_schema.validate(bad_plain)
        with pytest.raises(ValueError):
            fr.build_runtime_topology_source_binding_v02(
                source_context=_source_context_for_binding(policy, candidate),
            )


def test_d1_g2c_identifier_envelope_and_seed_lineage_geometry() -> None:
    fixtures = _fixture_family()
    source = fixtures[fr.RuntimeTopologySourceBindingV02]
    seed = fixtures[fr.RuntimeTopologySeedV02]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    source_schema = Draft202012Validator(schema["$defs"]["RuntimeTopologySourceBindingV02"])
    seed_schema = Draft202012Validator(schema["$defs"]["RuntimeTopologySeedV02"])

    prefixed_fields = {
        "route_eligibility_artifact_id": r"emabi_route_v01:[0-9a-f]{64}",
        "source_decision_artifact_id": r"emabi_decision_v01:[0-9a-f]{64}",
        "source_proposal_artifact_id": r"emabi_proposal_v01:[0-9a-f]{64}",
        "selected_local_mode_profile_id": r"emprofile_v01:[0-9a-f]{64}",
        "selected_feasibility_row_id": r"emrow_v01:[0-9a-f]{64}",
        "source_mode_profile_set_id": r"emprofiles_v01:[0-9a-f]{64}",
        "source_time_envelope_ref": r"emtime_v01:[0-9a-f]{64}",
    }
    raw_fields = (
        "source_root_decision_result_id",
        "source_root_transition_decision_id",
        "proposal_transition_decision_id",
        "post_root_transition_decision_id",
        "transition_registry_id",
    )
    for field_name, pattern in prefixed_fields.items():
        assert re.fullmatch(pattern, getattr(source, field_name))
    for field_name in raw_fields:
        assert re.fullmatch(r"[0-9a-f]{64}", getattr(source, field_name))
    assert source.g2c_abi_profile_id == "execution_mode_router_g2c_abi_profile_v01"
    assert len(source.source_trace_refs) == 4
    assert source.source_trace_refs == tuple(sorted(source.source_trace_refs))
    assert len(set(source.source_trace_refs)) == 4
    assert sum(bool(re.fullmatch(r"emdecision_v01:[0-9a-f]{64}", item)) for item in source.source_trace_refs) == 1
    assert source.source_parent_refs == (source.source_decision_artifact_id,)
    source_schema.validate(fr.runtime_topology_source_binding_to_plain_data_v02(source))

    bad_source_fields = {
        **{field_name: "artifact:wrong" for field_name in prefixed_fields},
        **{field_name: "decision:wrong" for field_name in raw_fields},
        "g2c_abi_profile_id": "execution_mode_router_g2c_abi_profile_wrong",
    }
    for field_name, bad_value in bad_source_fields.items():
        candidate = _seal(replace(source, **{field_name: bad_value}))
        assert fr.validate_runtime_topology_source_binding_v02(candidate).status == "FAIL_CLOSED"
        data = fr.runtime_topology_source_binding_to_plain_data_v02(source)
        data[field_name] = bad_value
        with pytest.raises(ValidationError):
            source_schema.validate(data)

    second_emdecision = "emdecision_v01:" + "1" * 64
    two_emdecision_trace = tuple(sorted((
        source.source_decision_artifact_id,
        source.post_root_transition_decision_id,
        "emdecision_v01:" + "5" * 64,
        second_emdecision,
    )))
    candidate = _seal(replace(source, source_trace_refs=two_emdecision_trace))
    assert fr.validate_runtime_topology_source_binding_v02(candidate).status == "FAIL_CLOSED"
    data = fr.runtime_topology_source_binding_to_plain_data_v02(source)
    data["source_trace_refs"] = list(two_emdecision_trace)
    with pytest.raises(ValidationError):
        source_schema.validate(data)

    assert len(seed.trace_refs) == 8
    assert seed.trace_refs[:4] == source.source_trace_refs
    assert seed.trace_refs[4:] == (
        source.source_binding_id,
        source.runtime_policy_id,
        seed.root_cell_id,
        source.source_time_envelope_ref,
    )
    assert seed.parent_refs == (
        source.route_eligibility_artifact_id,
        source.source_decision_artifact_id,
        source.source_proposal_artifact_id,
        source.source_binding_id,
    )
    assert len(seed.parent_refs) == 4
    seed_schema.validate(fr.runtime_topology_seed_to_plain_data_v02(seed))

    trace_mutations = (
        ("extra_prefix", ("0" * 64, *seed.trace_refs)),
        ("extra_suffix", (*seed.trace_refs, "0" * 64)),
        ("missing", seed.trace_refs[:-1]),
        ("duplicate", (seed.trace_refs[1], *seed.trace_refs[1:])),
        ("reordered", (*seed.trace_refs[:3], seed.source_binding_id, seed.trace_refs[3], *seed.trace_refs[5:])),
    )
    for label, mutation in trace_mutations:
        candidate = _seal(replace(seed, trace_refs=tuple(mutation)))
        assert fr.validate_runtime_topology_seed_v02(candidate).status == "FAIL_CLOSED", label
        data = fr.runtime_topology_seed_to_plain_data_v02(seed)
        data["trace_refs"] = list(mutation)
        with pytest.raises(ValidationError):
            seed_schema.validate(data)

    parent_mutations = (
        ("missing", seed.parent_refs[:-1]),
        ("duplicate", (seed.parent_refs[0], seed.parent_refs[0], *seed.parent_refs[2:])),
        ("reordered", (seed.parent_refs[1], seed.parent_refs[0], *seed.parent_refs[2:])),
        ("wrong_role", ("emabi_proposal_v01:" + "1" * 64, *seed.parent_refs[1:])),
    )
    for label, mutation in parent_mutations:
        candidate = _seal(replace(seed, parent_refs=tuple(mutation)))
        assert fr.validate_runtime_topology_seed_v02(candidate).status == "FAIL_CLOSED", label
        data = fr.runtime_topology_seed_to_plain_data_v02(seed)
        data["parent_refs"] = list(mutation)
        with pytest.raises(ValidationError):
            seed_schema.validate(data)


def test_d1_structural_unique_tuple_python_schema_matrix() -> None:
    fixtures = _fixture_family()
    narrow_fixtures = _fixture_family(permitted_child_scope_refs=("scope:root",))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert fr._STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02 == _STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02
    assert sum(len(field_names) for _type_name, field_names in _STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02) == 66

    for type_name, field_names in _STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02:
        cls = getattr(fr, type_name)
        base = fixtures[cls]
        for field_name in field_names:
            if field_name == "permitted_child_scope_refs" and cls is fr.FractalRuntimePolicyV02:
                base = narrow_fixtures[cls]
            elif field_name == "permitted_narrower_scope_refs" and cls is fr.RuntimeTopologySourceBindingV02:
                base = narrow_fixtures[cls]
            original = getattr(base, field_name)
            if original:
                duplicated = original + (original[0],)
            elif field_name in {"reason_codes", "queue_reason_codes"}:
                duplicated = ("g2d_type_invalid", "g2d_type_invalid")
            elif field_name == "source_reason_codes":
                duplicated = ("external_source:duplicate", "external_source:duplicate")
            else:
                duplicated = ("ref:duplicate", "ref:duplicate")
            candidate = _seal(replace(base, **{field_name: duplicated}))
            reasons = _validation_reasons(candidate)
            assert "g2d_tuple_duplicate" in reasons, (type_name, field_name, reasons)
            property_schema = schema["$defs"][type_name]["properties"][field_name]
            assert property_schema.get("uniqueItems") is True, (type_name, field_name)
            data = FUNCTION_FAMILIES[cls][1](base)
            data[field_name] = list(duplicated)
            with pytest.raises(ValidationError):
                Draft202012Validator(schema["$defs"][type_name]).validate(data)

    repeatable = (
        ("FractalCellInputV02", "required_output_kinds"),
        ("FractalRuntimeTraceV02", "state_transition_decision_ids"),
        ("FractalRuntimeTraceV02", "transition_refs"),
    )
    for type_name, field_name in repeatable:
        assert field_name not in dict(_STRUCTURAL_UNIQUE_TUPLE_FIELDS_V02).get(type_name, ())
        assert "uniqueItems" not in schema["$defs"][type_name]["properties"][field_name]

    for cls, value in fixtures.items():
        result = FUNCTION_FAMILIES[cls][0](value)
        assert result == () if cls is fr.FractalRuntimeValidationReportV02 else result.status == "PASS"
        Draft202012Validator(schema["$defs"][cls.__name__]).validate(FUNCTION_FAMILIES[cls][1](value))


def test_d1_semantic_tuple_cell_input_and_source_reason_parity() -> None:
    fixtures = _fixture_family()
    narrow_fixtures = _fixture_family(permitted_child_scope_refs=("scope:root",))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    duplicate_fields = (
        (fr.FractalRuntimePolicyV02, narrow_fixtures[fr.FractalRuntimePolicyV02], "permitted_child_scope_refs"),
        (fr.RuntimeTopologySourceBindingV02, fixtures[fr.RuntimeTopologySourceBindingV02], "source_trace_refs"),
        (fr.FractalCellInputV02, fixtures[fr.FractalCellInputV02], "evidence_refs"),
        (fr.FractalCellInputV02, fixtures[fr.FractalCellInputV02], "context_refs"),
        (fr.FractalPartialFailureRecordV02, fixtures[fr.FractalPartialFailureRecordV02], "evidence_refs"),
        (fr.FractalCellResultV02, fixtures[fr.FractalCellResultV02], "accepted_output_refs"),
        (fr.FractalCellResultV02, fixtures[fr.FractalCellResultV02], "evidence_refs"),
    )
    for cls, value, field_name in duplicate_fields:
        original = getattr(value, field_name)
        assert original
        duplicate = original + (original[0],)
        candidate = _seal(replace(value, **{field_name: duplicate}))
        report = FUNCTION_FAMILIES[cls][0](candidate)
        assert report.status == "FAIL_CLOSED", (cls.__name__, field_name)
        data = FUNCTION_FAMILIES[cls][1](value)
        data[field_name] = list(duplicate)
        with pytest.raises(ValidationError):
            Draft202012Validator(schema["$defs"][cls.__name__]).validate(data)

    cell_input = fixtures[fr.FractalCellInputV02]
    full_fractal_outputs = tuple(
        row[9] for row in dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)["full_fractal"] if row[10]
    )
    assert cell_input.required_output_kinds == full_fractal_outputs
    invalid_outputs = (
        full_fractal_outputs + ("POST_VV_REPORT",),
        full_fractal_outputs[:-1],
        (full_fractal_outputs[1], full_fractal_outputs[0], *full_fractal_outputs[2:]),
    )
    for outputs in invalid_outputs:
        candidate = _seal(replace(cell_input, required_output_kinds=outputs))
        assert fr.validate_fractal_cell_input_v02(candidate).status == "FAIL_CLOSED"
    for field_name in (
        "ordered_node_ids",
        "ordered_initial_queue_entry_ids",
        "ordered_required_queue_entry_ids",
    ):
        candidate = _seal(replace(cell_input, **{field_name: getattr(cell_input, field_name)[:-1]}))
        assert fr.validate_fractal_cell_input_v02(candidate).status == "FAIL_CLOSED"
    child_ids = cell_input.ordered_planned_child_cell_ids
    for count, planned in (
        (0, ()),
        (1, child_ids[:1]),
        (3, child_ids + ("frchildcell_v02:" + "f" * 64,)),
    ):
        candidate = _seal(replace(
            cell_input,
            requested_child_count=count,
            ordered_planned_child_cell_ids=planned,
        ))
        assert fr.validate_fractal_cell_input_v02(candidate).status == "FAIL_CLOSED"

    semantic_outputs = tuple(
        row[9] for row in dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)["full_semantic"] if row[10]
    )
    assert len(semantic_outputs) > len(set(semantic_outputs))
    semantic_input = _seal(replace(
        cell_input,
        accepted_mode="full_semantic",
        requested_child_count=0,
        ordered_planned_child_cell_ids=(),
        required_output_kinds=semantic_outputs,
    ))
    assert fr.validate_fractal_cell_input_v02(semantic_input).status == "PASS"
    semantic_with_child = _seal(replace(
        semantic_input,
        requested_child_count=1,
        ordered_planned_child_cell_ids=(child_ids[0],),
    ))
    assert fr.validate_fractal_cell_input_v02(semantic_with_child).status == "FAIL_CLOSED"
    assert cell_input.trace_refs.count(cell_input.cell_budget_id) >= 2

    trace = fixtures[fr.FractalRuntimeTraceV02]
    repeated_decisions = (trace.state_transition_decision_ids[0],) * len(trace.state_transition_decision_ids)
    repeated_transition_trace = _seal(replace(
        trace,
        state_transition_decision_ids=repeated_decisions,
        transition_refs=(trace.transition_refs[0], *repeated_decisions, trace.transition_refs[-1]),
    ))
    assert fr.validate_fractal_runtime_trace_v02(repeated_transition_trace).status == "PASS"

    topology = fixtures[fr.RuntimeExecutionTopologyV02]
    nodes, _edges, _assignments = _topology_components(fixtures)
    queue_entry = fixtures[fr.FractalCellQueueEntryV02]
    with pytest.raises(ValueError):
        fr.build_fractal_cell_input_v02(
            topology,
            cell_id=cell_input.cell_id,
            parent_cell_id=None,
            scope_projection=None,
            scope_ref=cell_input.scope_ref,
            cell_budget=fixtures[fr.FractalRuntimeBudgetV02],
            global_budget=fixtures[fr.FractalRuntimeBudgetV02],
            initial_queue_entries=(queue_entry,) * len(nodes),
            required_queue_entries=(queue_entry,) * len(nodes),
            cell_depth=0,
            requested_child_count=1,
            ordered_planned_child_cell_ids=child_ids[:1],
            ordered_nodes=nodes,
            evidence_refs=cell_input.evidence_refs,
            context_refs=cell_input.context_refs,
            time_envelope_ref=cell_input.time_envelope_ref,
        )

    external_reason = "external_source:reason"
    failed_report = fr.build_fractal_runtime_validation_report_v02(
        validation_target="FractalRuntimePolicyV02",
        validated_object_id=None,
        failure_stage="POLICY",
        reason_codes=(),
        source_reason_codes=(external_reason,),
    )
    source_reason_values = (
        _seal(replace(fixtures[fr.FractalPartialFailureRecordV02], source_reason_codes=(external_reason,))),
        _seal(replace(fixtures[fr.FractalCellResultV02], source_reason_codes=(external_reason,))),
        failed_report,
    )
    for value in source_reason_values:
        cls = type(value)
        result = FUNCTION_FAMILIES[cls][0](value)
        if cls is fr.FractalRuntimeValidationReportV02:
            assert result == ()
        else:
            assert result.status == "PASS"
        Draft202012Validator(schema["$defs"][cls.__name__]).validate(
            FUNCTION_FAMILIES[cls][1](value)
        )
        for forbidden_reason in ("g2d_type_invalid", "g2d_external_source_reason"):
            candidate = _seal(replace(value, source_reason_codes=(forbidden_reason,)))
            reasons = _validation_reasons(candidate)
            assert "g2d_success_laundering_forbidden" in reasons
            data = FUNCTION_FAMILIES[cls][1](value)
            data["source_reason_codes"] = [forbidden_reason]
            with pytest.raises(ValidationError):
                Draft202012Validator(schema["$defs"][cls.__name__]).validate(data)


def test_d1_guardian_object_local_acyclic_validation_matrix() -> None:
    fixtures = _fixture_family()
    seed = fixtures[fr.RuntimeTopologySeedV02]
    node = fixtures[fr.RuntimeTopologyNodeV02]
    edge = fixtures[fr.RuntimeTopologyEdgeV02]
    assignment = fixtures[fr.RuntimeAssignmentV02]
    topology = fixtures[fr.RuntimeExecutionTopologyV02]
    trace = fixtures[fr.FractalRuntimeTraceV02]
    duplicate_nodes = (topology.ordered_node_ids[0], topology.ordered_node_ids[0], *topology.ordered_node_ids[2:])
    corrupt_topology = _seal(replace(
        topology,
        ordered_node_ids=duplicate_nodes,
        trace_refs=(
            topology.source_binding_id,
            topology.root_cell_id,
            topology.topology_seed_id,
            topology.global_budget_id,
            *duplicate_nodes,
            *topology.ordered_edge_ids,
            *topology.ordered_assignment_ids,
        ),
    ))
    corrupt_trace_queue_ids = (trace.ordered_queue_entry_ids[0], trace.ordered_queue_entry_ids[0], *trace.ordered_queue_entry_ids[2:])
    corruptions = {
        fr.FractalRuntimePolicyV02: _seal(replace(fixtures[fr.FractalRuntimePolicyV02], root_review_required=False)),
        fr.FractalRuntimeBudgetV02: _seal(replace(fixtures[fr.FractalRuntimeBudgetV02], remaining_cell_count=fixtures[fr.FractalRuntimeBudgetV02].remaining_cell_count + 1)),
        fr.RuntimeTopologySourceBindingV02: _seal(replace(
            fixtures[fr.RuntimeTopologySourceBindingV02],
            source_parent_refs=(
                fixtures[fr.RuntimeTopologySourceBindingV02].route_eligibility_artifact_id,
                fixtures[fr.RuntimeTopologySourceBindingV02].source_decision_artifact_id,
                fixtures[fr.RuntimeTopologySourceBindingV02].source_proposal_artifact_id,
            ),
        )),
        fr.RuntimeTopologySeedV02: _seal(replace(seed, root_cell_id="frrootcell_v02:" + "e" * 64, trace_refs=seed.trace_refs[:-2] + ("frrootcell_v02:" + "e" * 64, seed.source_time_envelope_ref))),
        fr.RuntimeTopologyNodeV02: _seal(replace(node, trace_refs=node.trace_refs + ("frqueue_v02:" + "e" * 64,))),
        fr.RuntimeTopologyEdgeV02: _seal(replace(edge, trace_refs=(edge.topology_seed_id, edge.target_node_id, edge.source_node_id, str(edge.canonical_index), edge.cell_projection_class))),
        fr.RuntimeAssignmentV02: _seal(replace(assignment, trace_refs=(assignment.topology_seed_id, assignment.node_id, str(assignment.canonical_index + 1), assignment.executor_component_id))),
        fr.RuntimeExecutionTopologyV02: corrupt_topology,
        fr.ParentChildScopeProjectionV02: _seal(replace(fixtures[fr.ParentChildScopeProjectionV02], root_review_required=False)),
        fr.FractalCellInputV02: _seal(replace(fixtures[fr.FractalCellInputV02], initial_revise_count=1)),
        fr.FractalCellQueueEntryV02: _seal(replace(fixtures[fr.FractalCellQueueEntryV02], root_review_required=False)),
        fr.FractalReviseObservationV02: _seal(replace(fixtures[fr.FractalReviseObservationV02], progress_units=fixtures[fr.FractalReviseObservationV02].progress_units + 1)),
        fr.FractalPartialFailureRecordV02: _seal(replace(fixtures[fr.FractalPartialFailureRecordV02], retry_eligible=True)),
        fr.FractalBackpressureStateV02: _seal(replace(fixtures[fr.FractalBackpressureStateV02], queue_capacity=fixtures[fr.FractalBackpressureStateV02].queue_capacity + 1)),
        fr.FractalCellResultV02: _seal(replace(fixtures[fr.FractalCellResultV02], parent_return_required=False)),
        fr.FractalRuntimeTraceV02: _seal(replace(trace, ordered_queue_entry_ids=corrupt_trace_queue_ids)),
        fr.FractalRuntimeReportV02: _seal(replace(fixtures[fr.FractalRuntimeReportV02], topology_created_count=2)),
        fr.FractalRuntimeValidationReportV02: _seal(replace(fixtures[fr.FractalRuntimeValidationReportV02], root_review_required=False)),
    }
    owned_stages = {row[0]: row[3] for row in fr.STRUCTURAL_VALIDATION_TARGET_ROWS_V02}
    for cls, corruption in corruptions.items():
        reasons = _validation_reasons(corruption)
        assert reasons and set(reasons).issubset(fr.PUBLIC_G2D_REASON_CODES), cls.__name__
        if cls is not fr.FractalRuntimeValidationReportV02:
            report = FUNCTION_FAMILIES[cls][0](corruption)
            assert report.status == "FAIL_CLOSED"
            assert report.failure_stage == owned_stages[cls]

    self_cycle = replace(
        fixtures[fr.FractalCellResultV02],
        ordered_child_result_ids=(fixtures[fr.FractalCellResultV02].result_id,),
    )
    assert fr.validate_fractal_cell_result_v02(self_cycle).status == "FAIL_CLOSED"
    reverse_node = _seal(replace(
        node,
        input_refs=node.input_refs + ("frtopology_v02:" + "e" * 64,),
    ))
    assert fr.validate_runtime_topology_node_v02(reverse_node).status == "FAIL_CLOSED"


def test_d1_structural_validators_and_reasons() -> None:
    preflight_reasons = tuple(re.findall(r"^g2d_[a-z0-9_]+$", PREFLIGHT_PATH.read_text(encoding="utf-8"), re.MULTILINE))
    assert fr.PUBLIC_G2D_REASON_CODES == preflight_reasons
    assert len(fr.PUBLIC_G2D_REASON_CODES) == len(set(fr.PUBLIC_G2D_REASON_CODES)) == 220
    assert len(fr.VALIDATION_TARGETS) == 34
    assert len(fr.FAILURE_STAGES) == 30
    module_tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    registry_node = next(
        node.value
        for node in module_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PUBLIC_G2D_REASON_CODES" for target in node.targets)
    )
    assert isinstance(registry_node, ast.Tuple)
    assert tuple(item.value for item in registry_node.elts) == fr.PUBLIC_G2D_REASON_CODES
    public_literal_pattern = re.compile(r"^g2d_[a-z0-9_]+$")
    module_reason_literals = {
        node.value
        for node in ast.walk(module_tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and public_literal_pattern.fullmatch(node.value)
    }
    assert module_reason_literals.issubset(fr.PUBLIC_G2D_REASON_CODES)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def schema_strings(value: object) -> set[str]:
        if type(value) is str:
            return {value}
        if type(value) is list:
            return set().union(*(schema_strings(item) for item in value)) if value else set()
        if type(value) is dict:
            return set().union(*(schema_strings(key) | schema_strings(item) for key, item in value.items())) if value else set()
        return set()

    schema_reason_literals = {item for item in schema_strings(schema) if public_literal_pattern.fullmatch(item)}
    assert schema_reason_literals.issubset(fr.PUBLIC_G2D_REASON_CODES)
    fixtures = _fixture_family()
    for cls, value in fixtures.items():
        if cls is fr.FractalRuntimeValidationReportV02:
            continue
        report = FUNCTION_FAMILIES[cls][0](value)
        assert report.status == "PASS"
        assert report.reason_codes == report.source_reason_codes == ()
        assert report.return_to_root_required is False
        assert report.root_review_required is True
        assert report.authority_created is report.permission_created is False
        assert report.action_commit_packet_created is report.final_output_created is report.drs_write_created is False
        assert report.real_world_effects_count == 0
        failed = FUNCTION_FAMILIES[cls][0](object())
        assert failed.status == "FAIL_CLOSED"
        assert failed.validated_object_id is None
        assert failed.failure_stage != "NONE"
        assert failed.reason_codes
        assert failed.return_to_root_required is True
    valid = fixtures[fr.FractalRuntimeValidationReportV02]
    assert fr.validate_fractal_runtime_validation_report_v02(valid) == ()
    assert "g2d_validation_status_stage_mismatch" in fr.validate_fractal_runtime_validation_report_v02(_seal(replace(valid, status="FAIL_CLOSED")))
    assert "g2d_validation_status_stage_mismatch" in fr.validate_fractal_runtime_validation_report_v02(_seal(replace(valid, failure_stage="REPORT")))
    assert "g2d_validation_target_id_mismatch" in fr.validate_fractal_runtime_validation_report_v02(_seal(replace(valid, validated_object_id=None)))
    with pytest.raises(ValueError):
        fr.build_fractal_runtime_validation_report_v02(
            validation_target="FractalRuntimePolicyV02",
            validated_object_id="frpolicy_v02:" + "1" * 64,
            failure_stage="NONE",
            reason_codes=("g2d_type_invalid",),
            source_reason_codes=(),
        )
    with pytest.raises(ValueError):
        fr.build_fractal_runtime_validation_report_v02(
            validation_target="FractalRuntimePolicyV02",
            validated_object_id=None,
            failure_stage="POLICY",
            reason_codes=(),
            source_reason_codes=("g2d_type_invalid",),
        )
    laundered = _seal(replace(
        valid,
        status="FAIL_CLOSED",
        validated_object_id=None,
        failure_stage="CELL_RESULT_PRECONDITIONS",
        source_reason_codes=("g2d_type_invalid",),
        return_to_root_required=True,
    ))
    laundering_reasons = fr.validate_fractal_runtime_validation_report_v02(laundered)
    assert "g2d_success_laundering_forbidden" in laundering_reasons
    assert set(laundering_reasons).issubset(fr.PUBLIC_G2D_REASON_CODES)
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL" in source
    assert "IDENTITY_OR_BUDGET_FAILURE" not in source
    assert "synthetic_child_result" not in source
    for retired in (
        "g2d_reason_code_invalid",
        "g2d_source_reason_laundering_forbidden",
        "g2d_pre_result_validation_failed",
        "g2d_validation_report_invalid",
    ):
        assert retired not in source


def test_d1_schema_valid_and_negative_mutations() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    fixtures = _fixture_family()
    assert list(schema["$defs"]) == [item.__name__ for item in fr.SERIALIZED_G2D_TYPES_V02]
    for cls, value in fixtures.items():
        data = FUNCTION_FAMILIES[cls][1](value)
        validator = Draft202012Validator(schema["$defs"][cls.__name__])
        validator.validate(data)
        missing = dict(data)
        missing.pop(next(iter(missing)))
        with pytest.raises(ValidationError):
            validator.validate(missing)
        extra = dict(data)
        extra["unexpected"] = True
        with pytest.raises(ValidationError):
            validator.validate(extra)
    policy_data = fr.fractal_runtime_policy_to_plain_data_v02(fixtures[fr.FractalRuntimePolicyV02])
    policy_data["policy_id"] = "bad"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema["$defs"]["FractalRuntimePolicyV02"]).validate(policy_data)
    report_data = fr.fractal_runtime_validation_report_to_plain_data_v02(fixtures[fr.FractalRuntimeValidationReportV02])
    report_data["status"] = "FAIL_CLOSED"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema["$defs"]["FractalRuntimeValidationReportV02"]).validate(report_data)
    for cls in (
        fr.FractalPartialFailureRecordV02,
        fr.FractalCellResultV02,
        fr.FractalRuntimeValidationReportV02,
    ):
        data = FUNCTION_FAMILIES[cls][1](fixtures[cls])
        data["source_reason_codes"] = ["g2d_type_invalid"]
        with pytest.raises(ValidationError):
            Draft202012Validator(schema["$defs"][cls.__name__]).validate(data)
    fixed_mutations = (
        (fr.ParentChildScopeProjectionV02, "root_review_required", False),
        (fr.FractalCellResultV02, "parent_return_required", False),
        (fr.FractalRuntimeReportV02, "topology_created_count", 2),
    )
    for cls, field_name, replacement in fixed_mutations:
        data = FUNCTION_FAMILIES[cls][1](fixtures[cls])
        data[field_name] = replacement
        with pytest.raises(ValidationError):
            Draft202012Validator(schema["$defs"][cls.__name__]).validate(data)


def test_d1_import_and_zero_operation_boundary() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert "hedgehog.kernel" not in imported
    assert not any(name.startswith(("hedgehog.fractal_", "hedgehog.root_orchestrator")) for name in imported)
    assert not any(name.split(".")[0] in {"os", "pathlib", "random", "uuid", "time", "subprocess", "socket", "requests", "httpx"} for name in imported)
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not calls.intersection({"open", "exec", "eval", "compile", "__import__"})
    source = MODULE_PATH.read_text(encoding="utf-8")
    for forbidden in ("FinalOutput(", "DRS write", "provider_call(", "network_call(", "connector_call("):
        assert forbidden not in source
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 110
    assert fr.D1_MODULE_PUBLIC_FUNCTION_COUNT == 74
    assert fr.TOTAL_G2D_TYPE_COUNT == 20
    assert fr.SCHEMA_DEFINITION_COUNT == 18
