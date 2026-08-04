from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
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
import hedgehog.kernel.execution_mode_router_v01 as g2c
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)
from hedgehog.kernel.abi_v01 import (
    KernelArtifactV01,
    build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01,
)
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
    assert len(public_functions) == 81
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
    future_names = re.findall(r"^\|\s*(?:8[2-9]|9\d|1(?:0\d|1[0]))\s*\|\s*D[3-4]\s*\|\s*`([a-z0-9_]+)\(", preflight, re.MULTILINE)
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


_D2_TIME = 1785542400
_D2_VALID_TO = 1785546000
_D2_UTC = "2026-08-01T00:00:00+00:00"
_D2_VALID_TO_UTC = "2026-08-01T01:00:00+00:00"


def _d2_bsep(mode: str, request_id: str, domain_id: str) -> dict[str, dict[str, object]]:
    label = mode.replace("_", "-")
    route_id = f"route:g2d2:{label}"
    proposal_id = f"proposal:g2d2:{label}"
    vector_ids = (f"vector:g2d2:{label}",)
    guards = ("guard:g2d2:root-review",)
    business = context_packets.build_business_request_context_packet(
        packet_id=f"context_packet:g2d2:{label}:business",
        created_by="runtime:g2d2:test",
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
        packet_id=f"context_packet:g2d2:{label}:route",
        created_by="runtime:g2d2:test",
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
        packet_id=f"context_packet:g2d2:{label}:bsep",
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


def _d2_replay_family(
    *,
    mode: str,
    request_id: str,
    domain_id: str,
) -> dict[str, object]:
    label = mode.replace("_", "-")
    kernel_hash = hashlib.sha256(
        canonical_json_bytes_v01((domain_id, request_id, "sealed_replay"))
    ).hexdigest()
    programme = evidence_profile.build_programme_evidence_identity_v01(
        programme_id=f"g2d2_{label}_programme_v01",
        programme_version="v0.1",
    )
    execution = evidence_profile.build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=domain_id,
        execution_head="abcdef1",
        source_task_id=f"task:g2d2:{label}",
        run_id=f"run:g2d2:{label}",
        report_id=f"report:g2d2:{label}",
    )
    attempt = evidence_profile.build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=execution,
        attempt_number=1,
        package_id=f"package:g2d2:{label}",
        logical_package_ref=f"g2d2/{label}",
        output_directory_ref=f"g2d2/{label}/output",
        provider_mode="deterministic_fixture",
        model_id="none",
        expected_actor_count=1,
        provider_call_budget=0,
    )
    source = evidence_profile.build_safe_source_record_v01(
        source_id=f"source:g2d2:{label}:replay",
        source_type="g2d2_replay_fixture",
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
        artifact_id=f"artifact:g2d2:{label}:replay",
        artifact_type="g2d2_replay_fixture",
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
        evidence_refs=(f"evidence:g2d2:{label}:replay",),
        limitation_refs=("limitation:g2d2:local-only",),
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
        evidence_refs=(
            f"evidence:g2d2:{label}:replay",
            f"anchor:g2d2:{label}",
        ),
    )
    return {
        "replay": replay,
        "manifest": manifest,
        "projection": projection,
        "contents": (content,),
        "publication": publication,
        "verification": verification,
    }


def _d2_memory_family(
    *,
    request_id: str,
    domain_id: str,
    root_id: str,
    scope_ref: str,
    direct: bool = False,
) -> dict[str, object]:
    address = drs_semantic.build_semantic_address_v01(
        namespace="g2d2_v02",
        domain=domain_id,
        subject_class="bounded_information",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    scope_sha256 = hashlib.sha256(scope_ref.encode("utf-8")).hexdigest()
    envelope = drs_semantic.build_drs_time_envelope_v01(
        pt_created_at=_D2_TIME,
        kt_as_of=_D2_TIME,
        et_observed_at=_D2_TIME,
        ct_context_anchor=_D2_TIME,
        ttl_seconds=3600,
        valid_from=_D2_TIME,
        valid_to=_D2_VALID_TO,
        source_observed_at=_D2_TIME,
        source_reported_at=_D2_TIME,
        system_ingested_at=_D2_TIME,
        system_verified_at=_D2_TIME,
        freshness_policy_id="freshness:g2d2:v01",
    )
    authority = drs_semantic.build_drs_authority_envelope_v01(
        authority_class="ROOT_ACCEPTED_WORK" if direct else "ROOT_ACCEPTED_CONTEXT",
        owning_local_root_id=root_id,
        source_root_decision_input_id="root-input:g2d2:memory",
        source_root_decision_id="root-decision:g2d2:memory",
        source_root_decision_hash=hashlib.sha256(b"g2d2-memory-root").hexdigest(),
        authority_scope_fingerprint=scope_sha256,
        root_acceptance_state="ACCEPTED_WORK" if direct else "ACCEPTED_CONTEXT",
        recording_component="fractal_runtime_g2d2_test",
    )
    record = drs_semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Bounded deterministic context for topology routing.",
        semantic_tags=("bounded", "g2d2"),
        resonance_reason="Exact deterministic semantic-address match.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=("source:g2d2:memory",),
        lineage_edges=(),
        time_envelope=envelope,
        authority_envelope=authority,
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT" if direct else "CONTEXT_ONLY",
        policy_version="policy:g2d2:memory:v01",
        schema_versions=("v0.1",),
        content_fingerprint=hashlib.sha256(b"g2d2-memory-record").hexdigest(),
        recording_component="fractal_runtime_g2d2_test",
    )
    query = drs_resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE" if direct else "MEMORY_CONTEXT_ONLY",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_sha256,
        as_of=_D2_TIME,
        evaluation_time=_D2_TIME,
        evaluation_time_source=(
            "INJECTED_CURRENT_DECISION_TIME" if direct else "INJECTED_ANALYSIS_TIME"
        ),
        time_range_start=_D2_TIME,
        time_range_end=_D2_VALID_TO,
        required_time_axes=(
            ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")
            if direct else ("KT", "TTL", "VALIDITY")
        ),
        freshness_policy_id="freshness:g2d2:v01",
        max_age_seconds=3600,
        domain=domain_id,
        risk_class="LOW",
        reuse_intent=(
            "INFORMATIONAL_SHORTCUT_CONSIDERATION" if direct else "CONTEXT"
        ),
        requested_reuse_classes=("ANSWER_SHORTCUT",) if direct else ("CONTEXT_ONLY",),
        required_evidence_classes=(
            "SOURCE_IDENTITY", "SOURCE_INTEGRITY", "PROVENANCE_CHAIN",
            "TIME_FITNESS", "POLICY_COMPATIBILITY", "SCHEMA_COMPATIBILITY",
            "CONFLICT_CLEARANCE", "ROOT_DECISION", "SOURCE_HISTORY",
        ),
        forbidden_changes=("POLICY_CHANGED",),
        policy_version="policy:g2d2:memory:v01",
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
        "record_id": "legacy:g2d2:memory",
        "layer": "work",
        "type": "generic",
        "domain": domain_id,
        "content": {"summary": "Bounded deterministic memory context."},
        "time_envelope": {
            "pt_created_at": "2026-08-01T00:00:00Z",
            "kt_asof": "2026-08-01T00:00:00Z",
            "et_observed_at": "2026-08-01T00:00:00Z",
            "ct_session_anchor": "case:g2d2:memory",
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
    common_report = {
        "semantic_address": address,
        "query": query,
        "source_projections": (projection,),
        "source_records": (record,),
        "query_evaluations": (evaluation,),
        "retrieval_plan": plan,
        "memory_descent_result": None,
        "historical_only_record_ids": (),
        "warning_only_record_ids": (),
        "rerun_required_record_ids": (),
        "blocked_record_ids": (),
        "provider_calls": 0,
        "network_calls": 0,
        "gemini_calls": 0,
        "external_drs_calls": 0,
        "connector_calls": 0,
        "real_world_effects_count": 0,
        "final_status": "PASS",
        "reason_codes": (),
    }
    if not direct:
        report = drs_resolution.build_drs_resolution_report_v01(
            **common_report,
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
            "use_time": _D2_TIME,
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
        "valid_from": _D2_TIME,
        "valid_to": _D2_VALID_TO,
        "issued_at": _D2_TIME,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": "policy:drs_answer_shortcut:v0.1",
    }
    actor_id = "actor:g2d2:direct-reuse"
    work_request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic-work-request:g2d2:direct-reuse",
        transaction_id=query.query_id,
        target_root_id=root_id,
        runtime_topology_ref="g2d2:runtime_topology:not_created",
        bounded_context_refs=("context:g2d2:direct-reuse",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence-binding:g2d2:direct-reuse",
        evidence_ref="evidence:g2d2:direct-reuse",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id=actor_id,
        provenance_ref="provenance:g2d2:direct-reuse",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id,
        predicate="authorize_non_action_informational_answer_shortcut_v01",
        object_or_value=claim_preimage,
        time_envelope_ref="time-envelope:g2d2:direct-reuse",
        provenance_refs=("provenance:g2d2:direct-reuse",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1000000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2d2:direct-reuse",
        request_id=work_request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2d2:direct-reuse",
        scope=address.semantic_address_id,
        bounded_context_refs=("context:g2d2:direct-reuse",),
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
            "bundle_id": "post-vv:g2d2:direct-reuse",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate.resolution_candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:g2d2:direct-reuse",
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
            "policy_id": "policy:g2d2:direct-reuse",
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
            "time_envelope_ref": "time-envelope:g2d2:direct-reuse",
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": [],
        },
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
    assert root_result.decision == "ACCEPT"
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
        valid_from=_D2_TIME,
        valid_to=_D2_VALID_TO,
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
        valid_from=_D2_TIME,
        valid_to=_D2_VALID_TO,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=_D2_TIME,
        evaluated_at=evaluation.evaluated_at,
    )
    report = drs_resolution.build_drs_resolution_report_v01(
        **common_report,
        eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(
            item.resolution_candidate_id for item in ranked
        ),
        selected_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_projection=root_projection,
        reuse_certificate=certificate,
        context_only_record_ids=(),
    )
    assert reuse_certificate.validate_existing_root_shortcut_decision_v01(
        resolution_report=report,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        use_time=_D2_TIME,
    ) == (True, ())
    return {
        "transaction_id": query.query_id,
        "report": report,
        "projections": (projection,),
        "use_time": _D2_TIME,
        "root_kernel": root_kernel,
        "root_input": root_input,
        "root_result": root_result,
    }


def _d2_source_context(
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


def _d2_g2c_family(
    mode: str,
    *,
    narrow: bool = False,
    action_packet_required: bool = False,
    review_action: str | None = None,
    reject_for_g2d: bool = False,
    root_id_override: str | None = None,
    domain_id_override: str | None = None,
) -> dict[str, object]:
    request_id = f"request:g2d2:{mode}"
    domain_id = domain_id_override or "G2D2_RUNTIME_TOPOLOGY"
    root_id = root_id_override or "root:g2d2"
    scope_ref = f"scope:g2d2:{mode}"
    memory = (
        _d2_memory_family(
            request_id=request_id,
            domain_id=domain_id,
            root_id=root_id,
            scope_ref=scope_ref,
            direct=mode == "direct_informational_reuse",
        )
        if mode in {"memory_informed", "direct_informational_reuse"}
        else None
    )
    replay = (
        _d2_replay_family(
            mode=mode,
            request_id=request_id,
            domain_id=domain_id,
        )
        if mode == "sealed_replay"
        else None
    )
    transaction_id = memory["transaction_id"] if memory else f"transaction:g2d2:{mode}"
    profiles = []
    selected_index = (
        g2c.EXECUTABLE_EXECUTION_MODES_V01.index(mode)
        if mode in g2c.EXECUTABLE_EXECUTION_MODES_V01
        else 0
    )
    for index, candidate in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01):
        not_required = candidate in {"sealed_replay", "direct_informational_reuse"}
        profiles.append(g2c.build_execution_mode_local_mode_profile_v01(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=root_id,
            domain_id=domain_id,
            mode=candidate,
            policy_snapshot_id=f"policy:g2d2:{mode}",
            capability_snapshot_id=f"capabilities:g2d2:{mode}",
            cost_model_id="cost:g2d2:v01",
            policy_allowed=index >= selected_index,
            scope_allowed=True,
            risk_allowed=True,
            privacy_allowed=True,
            capability_state="NOT_REQUIRED" if not_required else "AVAILABLE",
            capability_id=None if not_required else f"capability:g2d2:{candidate}",
            cost_units=index + 1,
        ))
    accepted_scope = f"{scope_ref}:narrow"
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        request_class="BOUNDED_FRACTAL_REQUIRED" if mode == "full_fractal" else "BOUNDED_REVIEW",
        action_class="ACTION" if action_packet_required else "NON_ACTION",
        action_packet_relation="NEW_ACTION_NO_PACKET" if action_packet_required else "NOT_APPLICABLE",
        scope_class="BOUNDED",
        scope_ref=scope_ref,
        permitted_narrower_scope_refs=(accepted_scope,) if narrow else (),
        risk_class="LOW",
        policy_snapshot_id=f"policy:g2d2:{mode}",
        capability_snapshot_id=f"capabilities:g2d2:{mode}",
        cost_model_id="cost:g2d2:v01",
        required_user_input_state=(
            "MISSING_RESOLVABLE" if mode == "needs_user" else "COMPLETE"
        ),
        hard_block_state="BLOCKED" if mode == "blocked" else "CLEAR",
        evaluation_time_epoch_seconds=_D2_TIME,
        pt_created_at_utc=_D2_UTC,
        et_observed_at_utc=_D2_UTC,
        ct_session_anchor=f"ct:g2d2:{mode}",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc=_D2_UTC,
        valid_to_utc=_D2_VALID_TO_UTC,
        mode_profiles=tuple(profiles),
    )
    bsep = _d2_bsep(mode, request_id, domain_id)
    source = _d2_source_context(
        bsep=bsep,
        snapshot=snapshot,
        memory=memory,
        replay=replay,
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
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(**common, source_context=source),
        local_routing_snapshot=snapshot,
        replay_binding=(
            g2c.build_execution_mode_replay_binding_v01(
                **common,
                source_context=source,
            )
            if replay
            else g2c.build_execution_mode_replay_not_applicable_binding_v01(**common)
        ),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=_D2_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        ),
        g2b_binding=(
            g2c.build_execution_mode_g2b_binding_v01(**common, source_context=source)
            if memory
            else g2c.build_execution_mode_g2b_not_applicable_binding_v01(**common)
        ),
    )
    proposal, route_report = g2c.route_execution_mode_v01(
        router_input=router_input,
        source_context=source,
    )
    assert route_report.validation_status == "PASS" and proposal is not None
    assert proposal.selected_mode == mode
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    )
    registry = transition_registry.build_execution_mode_transition_registry_profile_v01()
    pre = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
    )
    effective_review_action = review_action or (
        "TERMINAL_FROM_PROPOSAL" if mode in {"blocked", "needs_user"}
        else "NARROW" if narrow else "ACCEPT"
    )
    basis = tuple(sorted((
        router_input.bsep_binding.bsep_binding_id,
        proposal_artifact.artifact_id,
        proposal.selected_feasibility_row_id,
    ))) if effective_review_action == "NARROW" else ()
    review = g2c.build_root_execution_mode_review_input_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        review_action=effective_review_action,
        accepted_scope_ref=(
            accepted_scope if effective_review_action == "NARROW"
            else proposal.proposed_scope_ref
            if effective_review_action == "ACCEPT"
            else None
        ),
        narrowing_basis_refs=basis,
    )
    decision, root_kernel, root_input, root_result, review_report = g2c.review_execution_mode_proposal_v01(
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
    )
    assert review_report.validation_status == "PASS"
    assert decision is not None and root_kernel is not None
    assert root_input is not None and root_result is not None
    decision_artifact = g2c.project_root_execution_mode_decision_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    post = g2c.evaluate_execution_mode_root_route_transition_v01(
        registry=registry,
        proposal_transition_decision=pre,
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
    route = g2c.project_execution_mode_route_eligibility_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=post,
    )
    assert (route is not None) is (decision.outcome in {"ACCEPT", "NARROW"})
    policy = fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
    )
    source_kwargs = {
        "transition_registry": registry,
        "g2c_source_context": source,
        "router_input": router_input,
        "proposal": proposal,
        "proposal_artifact": proposal_artifact,
        "proposal_transition_decision": pre,
        "review_input": review,
        "decision": decision,
        "root_kernel": root_kernel,
        "root_decision_input": root_input,
        "root_decision_result": root_result,
        "decision_artifact": decision_artifact,
        "root_route_transition_decision": post,
        "route_eligibility_artifact": route,
        "runtime_policy": policy,
    }
    runtime_source = (
        fr.FractalRuntimeSourceContextV02(**source_kwargs)
        if reject_for_g2d
        else fr.build_fractal_runtime_source_context_v02(**source_kwargs)
    )
    return {
        "source": runtime_source,
        "g2c_source": source,
        "router_input": router_input,
        "proposal": proposal,
        "proposal_artifact": proposal_artifact,
        "proposal_transition_decision": pre,
        "review_input": review,
        "decision": decision,
        "root_kernel": root_kernel,
        "root_decision_input": root_input,
        "root_decision_result": root_result,
        "decision_artifact": decision_artifact,
        "root_route_transition_decision": post,
        "route": route,
        "policy": policy,
    }


@pytest.mark.parametrize(
    ("mode", "narrow", "packet_required"),
    (
        ("memory_informed", False, False),
        ("local_slm", False, True),
        ("cloud_llm", True, False),
        ("full_semantic", False, False),
        ("full_fractal", False, False),
    ),
)
def test_d2_complete_g2c_source_and_five_mode_topologies(
    mode: str,
    narrow: bool,
    packet_required: bool,
) -> None:
    case = _d2_g2c_family(mode, narrow=narrow, action_packet_required=packet_required)
    source = case["source"]
    assert fr.validate_fractal_runtime_source_context_v02(source).status == "PASS"
    binding = fr.build_runtime_topology_source_binding_v02(source_context=source)
    assert fr.validate_runtime_topology_source_binding_v02(binding).status == "PASS"
    assert fr.validate_runtime_topology_source_binding_against_g2c_v02(
        binding,
        source_context=source,
    ).status == "PASS"
    assert binding.downstream_action_packet_required is packet_required
    first = fr.construct_runtime_execution_topology_v02(source)
    second = fr.construct_runtime_execution_topology_v02(source)
    assert first == second
    assert canonical_json_bytes_v01(fr.runtime_execution_topology_to_plain_data_v02(first)) == canonical_json_bytes_v01(fr.runtime_execution_topology_to_plain_data_v02(second))
    assert fr.validate_runtime_execution_topology_against_sources_v02(
        first,
        source_context=source,
    ).status == "PASS"
    node_rows = dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)[mode]
    edge_rows = dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)[mode]
    assignment_rows = dict(fr.MODE_ASSIGNMENT_TEMPLATE_ROWS_V02)[mode]
    assert len(first.ordered_node_ids) == len(node_rows)
    assert len(first.ordered_edge_ids) == len(edge_rows)
    assert len(first.ordered_assignment_ids) == len(assignment_rows)
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    decision = fr.evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source,
        topology=first,
        transition_registry=registry,
    )
    assert decision.rule_id == "g2d_t01_route_eligibility_to_topology"
    artifact = fr.project_runtime_execution_topology_kernel_artifact_v02(
        first,
        source_context=source,
        topology_transition_decision=decision,
    )
    assert validate_kernel_artifact_v01(artifact) == ()
    assert artifact.parent_refs == (source.route_eligibility_artifact.artifact_id,)
    assert artifact.artifact_type == "RuntimeExecutionTopology"
    assert artifact.lifecycle_state == "VALIDATED"
    assert artifact.authority_class == "ADVISORY"
    planned_ids = fr._derive_settled_planned_root_child_ids_v02(
        source_context=source,
        topology=first,
        topology_transition_decision=decision,
        topology_artifact=artifact,
    )
    if mode == "full_fractal":
        expected_planned_ids = tuple(
            fr.derive_fractal_child_cell_id_v02(
                topology_seed_id=first.topology_seed_id,
                parent_cell_id=first.root_cell_id,
                canonical_child_index=canonical_index,
                accepted_mode="full_fractal",
                selected_local_mode_profile_id=(
                    source.proposal.selected_local_mode_profile_id
                ),
                source_mode_profile_set_id=(
                    source.router_input.local_routing_snapshot.mode_profile_set_id
                ),
                child_scope_ref=first.accepted_scope_ref,
                runtime_policy_id=first.runtime_policy_id,
                required_capability_ids=(
                    source.proposal.required_downstream_capability_ids
                ),
                forbidden_claims=source.runtime_policy.forbidden_claims,
                child_depth=1,
            )
            for canonical_index in (0, 1)
        )
        assert planned_ids == expected_planned_ids
        assert len(planned_ids) == len(set(planned_ids)) == 2
    else:
        assert planned_ids == ()
    assert first.authority_created is first.permission_created is False
    assert first.action_commit_packet_created is first.receipt_created is False
    assert first.final_output_created is first.drs_write_created is False
    assert first.provider_calls == first.network_calls == first.real_world_effects_count == 0


def test_d2_full_fractal_geometry_t01_order_and_partition() -> None:
    source = _d2_g2c_family("full_fractal")["source"]
    topology = fr.construct_runtime_execution_topology_v02(source)
    assert (len(topology.ordered_node_ids), len(topology.ordered_edge_ids), len(topology.ordered_assignment_ids)) == (7, 10, 7)
    edge_rows = dict(fr.MODE_EDGE_TEMPLATE_ROWS_V02)["full_fractal"]
    assert tuple(row[0] for row in edge_rows if row[1] == "ROOT_CELL_PROJECTION") == tuple(range(7))
    assert tuple(row[0] for row in edge_rows if row[1] == "FRACTAL_LEAF_PROJECTION") == (7, 8, 9)
    assert dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)["full_fractal"][3][8] == "FAN_IN_CHILD_SLOT_RETURNS_1_2"
    assert fr.CHILD_SLOT_INDEX_ROWS_V02 == (
        (1, "PREDECESSOR_AND_CHILD_SLOT_1", 1, 0, 0),
        (2, "PREDECESSOR_AND_CHILD_SLOT_2", 2, 1, 1),
    )
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    decision = fr.evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source,
        topology=topology,
        transition_registry=registry,
    )
    artifact = fr.project_runtime_execution_topology_kernel_artifact_v02(
        topology,
        source_context=source,
        topology_transition_decision=decision,
    )
    payload = kernel_artifact_to_plain_dict_v01(artifact)["payload"]
    expected_payload_fields = (
        "topology_id", "topology_version", "topology_seed_id", "request_id",
        "domain_id", "accepted_mode", "accepted_scope_ref", "source_binding_id",
        "source_root_decision_artifact_id", "source_proposal_artifact_id",
        "runtime_policy_id", "ordered_node_ids", "ordered_edge_ids",
        "ordered_assignment_ids", "root_cell_id", "global_budget_id",
        "root_review_required", "authority_created", "permission_created",
        "action_commit_packet_created", "receipt_created", "final_output_created",
        "drs_write_created", "provider_calls", "network_calls",
        "real_world_effects_count",
    )
    assert tuple(payload) == tuple(sorted(expected_payload_fields))
    assert len(payload) == 26
    assert artifact.artifact_id.startswith("frabi_topology_v02:")
    planned = fr._derive_settled_planned_root_child_ids_v02(
        source_context=source,
        topology=topology,
        topology_transition_decision=decision,
        topology_artifact=artifact,
    )
    assert planned == fr._derive_settled_planned_root_child_ids_v02(
        source_context=source,
        topology=topology,
        topology_transition_decision=decision,
        topology_artifact=artifact,
    )
    assert len(planned) == 2
    assert all(type(item) is str and item.startswith("frchildcell_v02:") for item in planned)
    assert not any(
        type(item) in fr.G2D_TYPES_V02
        for item in planned
    )
    with pytest.raises(ValueError):
        fr._derive_settled_planned_root_child_ids_v02(
            source_context=source,
            topology=topology,
            topology_transition_decision=replace(decision, decision_id="0" * 64),
            topology_artifact=artifact,
        )
    with pytest.raises(ValueError):
        fr._derive_settled_planned_root_child_ids_v02(
            source_context=source,
            topology=topology,
            topology_transition_decision=decision,
            topology_artifact=replace(artifact, artifact_id="frabi_topology_v02:" + "0" * 64),
        )


def _assert_d2_g2c_family_publicly_valid(case: dict[str, object]) -> None:
    source = case["g2c_source"]
    router_input = case["router_input"]
    proposal = case["proposal"]
    proposal_artifact = case["proposal_artifact"]
    pre = case["proposal_transition_decision"]
    review = case["review_input"]
    decision = case["decision"]
    root_kernel = case["root_kernel"]
    root_input = case["root_decision_input"]
    root_result = case["root_decision_result"]
    decision_artifact = case["decision_artifact"]
    post = case["root_route_transition_decision"]
    route = case["route"]
    assert g2c.validate_execution_mode_source_context_v01(
        source
    ).validation_status == "PASS"
    assert g2c.validate_execution_mode_router_input_against_sources_v01(
        router_input=router_input,
        source_context=source,
    ).validation_status == "PASS"
    assert g2c.validate_execution_mode_proposal_against_sources_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    ).validation_status == "PASS"
    assert g2c.validate_root_execution_mode_review_input_against_sources_v01(
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
    ).validation_status == "PASS"
    assert g2c.validate_root_execution_mode_decision_against_source_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    ).validation_status == "PASS"
    assert g2c.validate_execution_mode_abi_profile_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        review_input=review,
        decision=decision,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=post,
        route_eligibility_artifact=route,
    ).validation_status == "PASS"
    if route is not None:
        assert g2c.validate_execution_mode_route_eligibility_against_source_v01(
            route_eligibility_artifact=route,
            decision=decision,
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre,
            root_kernel=root_kernel,
            root_decision_input=root_input,
            root_decision_result=root_result,
            decision_artifact=decision_artifact,
            root_route_transition_decision=post,
        ).validation_status == "PASS"


@pytest.mark.parametrize(
    ("mode", "review_action", "expected_class"),
    (
        ("deterministic", "ACCEPT", "SHORTCUT_RETURN_TO_ROOT"),
        ("sealed_replay", "ACCEPT", "SHORTCUT_RETURN_TO_ROOT"),
        ("direct_informational_reuse", "ACCEPT", "SHORTCUT_RETURN_TO_ROOT"),
        ("full_semantic", "REJECT", "TERMINAL_NO_CONSUMPTION"),
        ("blocked", "TERMINAL_FROM_PROPOSAL", "TERMINAL_NO_CONSUMPTION"),
        ("needs_user", "TERMINAL_FROM_PROPOSAL", "TERMINAL_NO_CONSUMPTION"),
    ),
)
def test_d2_actual_shortcut_and_terminal_source_families_fail_consumption(
    mode: str,
    review_action: str,
    expected_class: str,
) -> None:
    case = _d2_g2c_family(
        mode,
        review_action=review_action,
        reject_for_g2d=True,
    )
    _assert_d2_g2c_family_publicly_valid(case)
    assert case["decision"].downstream_consumption_class == expected_class
    assert fr.validate_fractal_runtime_source_context_v02(
        case["source"]
    ).status == "FAIL_CLOSED"
    with pytest.raises(ValueError):
        fr.build_runtime_topology_source_binding_v02(
            source_context=case["source"]
        )
    with pytest.raises(ValueError):
        fr.construct_runtime_execution_topology_v02(case["source"])
    assert case["decision"].topology_created is False
    assert case["decision"].authority_created is False
    assert case["decision"].permission_created is False
    assert case["decision"].action_commit_packet_created is False
    assert case["decision"].final_output_created is False
    assert case["decision"].drs_write_created is False
    assert case["decision"].real_world_effects_count == 0


def test_d2_complete_runtime_source_context_cross_object_substitution_matrix() -> None:
    first = _d2_g2c_family("local_slm")["source"]
    second = _d2_g2c_family(
        "cloud_llm",
        narrow=True,
        root_id_override="root:g2d2:foreign",
        domain_id_override="G2D2_RUNTIME_TOPOLOGY_FOREIGN",
    )["source"]
    assert fr.validate_fractal_runtime_source_context_v02(first).status == "PASS"
    assert fr.validate_fractal_runtime_source_context_v02(second).status == "PASS"
    for field_name in fr.FractalRuntimeSourceContextV02.__annotations__:
        replacement = getattr(second, field_name)
        if replacement == getattr(first, field_name):
            identity_field = {
                "transition_registry": "registry_id",
                "proposal_transition_decision": "decision_id",
                "root_kernel": "kernel_id",
            }[field_name]
            replacement = replace(replacement, **{identity_field: "0" * 64})
        substituted = replace(first, **{field_name: replacement})
        assert fr.validate_fractal_runtime_source_context_v02(
            substituted
        ).status == "FAIL_CLOSED", field_name


def test_d2_source_topology_transition_and_artifact_substitutions_fail_closed() -> None:
    case = _d2_g2c_family("cloud_llm", narrow=True)
    source = case["source"]
    for direct_or_id_only in (
        source.decision,
        source.proposal,
        source.route_eligibility_artifact.artifact_id,
        source.decision_artifact.artifact_id,
    ):
        assert fr.validate_fractal_runtime_source_context_v02(
            direct_or_id_only
        ).status == "FAIL_CLOSED"
    topology = fr.construct_runtime_execution_topology_v02(source)
    foreign_source = replace(source, runtime_policy=fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=("capability:g2d2:foreign",),
        permitted_child_scope_refs=source.runtime_policy.permitted_child_scope_refs,
    ))
    assert fr.validate_fractal_runtime_source_context_v02(foreign_source).status == "FAIL_CLOSED"
    binding = fr.build_runtime_topology_source_binding_v02(source_context=source)
    assert fr.validate_runtime_topology_source_binding_against_g2c_v02(
        replace(binding, runtime_policy_id=foreign_source.runtime_policy.policy_id),
        source_context=source,
    ).status == "FAIL_CLOSED"
    forged_topology = _seal(replace(topology, accepted_scope_ref="scope:g2d2:foreign"))
    assert fr.validate_runtime_execution_topology_against_sources_v02(
        forged_topology,
        source_context=source,
    ).status == "FAIL_CLOSED"
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    decision = fr.evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source,
        topology=topology,
        transition_registry=registry,
    )
    with pytest.raises(ValueError):
        fr.evaluate_route_eligibility_to_topology_transition_v02(
            source_context=source,
            topology=topology,
            transition_registry=replace(registry, registry_id="0" * 64),
        )
    with pytest.raises(ValueError):
        fr.project_runtime_execution_topology_kernel_artifact_v02(
            topology,
            source_context=source,
            topology_transition_decision=replace(decision, rule_id=registry.rules[1].rule_id),
        )


def test_d2_surface_staging_and_import_boundaries() -> None:
    expected = (
        "build_fractal_runtime_source_context_v02",
        "validate_fractal_runtime_source_context_v02",
        "validate_runtime_topology_source_binding_against_g2c_v02",
        "construct_runtime_execution_topology_v02",
        "validate_runtime_execution_topology_against_sources_v02",
        "project_runtime_execution_topology_kernel_artifact_v02",
        "evaluate_route_eligibility_to_topology_transition_v02",
    )
    for name in expected:
        assert inspect.isfunction(getattr(fr, name))
    signatures = {
        "build_fractal_runtime_source_context_v02": "(*, transition_registry: 'TransitionRegistryV01', g2c_source_context: 'ExecutionModeSourceContextV01', router_input: 'ExecutionModeRouterInputV01', proposal: 'ExecutionModeProposalV01', proposal_artifact: 'KernelArtifactV01', proposal_transition_decision: 'TransitionDecisionV01', review_input: 'RootExecutionModeReviewInputV01', decision: 'RootExecutionModeDecisionV01', root_kernel: 'RootDecisionKernelV01', root_decision_input: 'RootDecisionInputV01', root_decision_result: 'RootDecisionResultV01', decision_artifact: 'KernelArtifactV01', root_route_transition_decision: 'TransitionDecisionV01', route_eligibility_artifact: 'KernelArtifactV01', runtime_policy: 'FractalRuntimePolicyV02') -> 'FractalRuntimeSourceContextV02'",
        "validate_fractal_runtime_source_context_v02": "(value: 'object') -> 'FractalRuntimeValidationReportV02'",
        "validate_runtime_topology_source_binding_against_g2c_v02": "(value: 'object', *, source_context: 'FractalRuntimeSourceContextV02') -> 'FractalRuntimeValidationReportV02'",
        "construct_runtime_execution_topology_v02": "(source_context: 'FractalRuntimeSourceContextV02') -> 'RuntimeExecutionTopologyV02'",
        "validate_runtime_execution_topology_against_sources_v02": "(value: 'object', *, source_context: 'FractalRuntimeSourceContextV02') -> 'FractalRuntimeValidationReportV02'",
        "project_runtime_execution_topology_kernel_artifact_v02": "(topology: 'RuntimeExecutionTopologyV02', *, source_context: 'FractalRuntimeSourceContextV02', topology_transition_decision: 'TransitionDecisionV01') -> 'KernelArtifactV01'",
        "evaluate_route_eligibility_to_topology_transition_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', transition_registry: 'TransitionRegistryV01') -> 'TransitionDecisionV01'",
    }
    assert set(signatures) == set(expected)
    for name, signature in signatures.items():
        assert str(inspect.signature(getattr(fr, name))) == signature
    public_functions = tuple(
        name
        for name, value in vars(fr).items()
        if inspect.isfunction(value) and value.__module__ == fr.__name__ and not name.startswith("_")
    )
    assert len(public_functions) == 81
    for forbidden in (
        "evaluate_fractal_runtime_state_transition_v02",
        "execute_fractal_runtime_v02",
        "build_fractal_runtime_execution_bundle_v02",
    ):
        assert not callable(getattr(fr, forbidden, None))
    module_source = MODULE_PATH.read_text(encoding="utf-8")
    assert "import hedgehog.kernel\n" not in module_source
    assert "demo." not in module_source and "tests." not in module_source
