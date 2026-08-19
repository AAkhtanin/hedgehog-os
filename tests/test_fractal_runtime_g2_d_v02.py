from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib
import inspect
from itertools import permutations
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, ValidationError

import demo.run_fractal_runtime_g2_d_v02 as d5_runner
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
    validate_kernel_artifact_bundle_v01,
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
ADDENDUM_PATH = (
    ROOT / "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md"
)
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


def _kernel_payload(artifact: KernelArtifactV01) -> dict[str, object]:
    payload = kernel_artifact_to_plain_dict_v01(artifact)["payload"]
    assert type(payload) is dict
    return payload


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
            "frcellin_v02:" + "2" * 64,
            terminal_entries[0].queue_entry_id,
            "evidence:child",
            pre_result.validation_report_id,
            child_allocated.budget_id,
            child_final.budget_id,
            child_global.budget_id,
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
    assert len(fr.RUNTIME_ONLY_G2D_TYPES_V02) == 3
    assert len(fr.G2D_TYPES_V02) == 21
    assert fr.G2D_TYPES_V02[:20] == fr.SERIALIZED_G2D_TYPES_V02 + (
        fr.FractalRuntimeSourceContextV02,
        fr.FractalRuntimeExecutionBundleV02,
    )
    assert fr.G2D_TYPES_V02[-1] is fr.RuntimeObservedWorkContextV02
    assert all(item.__dataclass_params__.frozen for item in fr.G2D_TYPES_V02)
    public_functions = [
        name for name, value in vars(fr).items()
        if not name.startswith("_") and inspect.isfunction(value) and value.__module__ == fr.__name__
    ]
    assert len(public_functions) == 116
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
    future_names = re.findall(r"^\|\s*(?:9[1-9]|10\d|110)\s*\|\s*D4\s*\|\s*`([a-z0-9_]+)\(", preflight, re.MULTILINE)
    assert future_names and all(callable(getattr(fr, name, None)) for name in future_names)
    package = importlib.import_module("hedgehog.kernel")
    assert all(hasattr(package, name) for name in public_functions)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert len(schema["$defs"]) == 18
    assert "FractalRuntimeSourceContextV02" not in schema["$defs"]
    assert "FractalRuntimeExecutionBundleV02" not in schema["$defs"]


def test_d1_canonical_types_fields_enums() -> None:
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    for cls in fr.G2D_TYPES_V02[:20]:
        expected_rows = _preflight_annotation_rows(cls.__name__)
        actual_fields = [item.name for item in fields(cls)]
        actual_annotations = tuple(
            (name, re.sub(r"\s+", "", annotation))
            for name, annotation in cls.__annotations__.items()
        )
        if cls is fr.FractalRuntimeExecutionBundleV02:
            assert actual_fields[:-1] == [
                name for name, _annotation in expected_rows
            ]
            assert actual_fields[-1] == "observed_work_context"
            assert actual_annotations[:-1] == expected_rows
            assert actual_annotations[-1] == (
                "observed_work_context",
                "RuntimeObservedWorkContextV02|None",
            )
        else:
            assert actual_fields == [
                name for name, _annotation in expected_rows
            ]
            assert actual_annotations == expected_rows
    assert tuple(fr.RuntimeObservedWorkContextV02.__annotations__) == (
        "observed_work_context_id",
        "context_version",
        "context_profile_id",
        "baseline_execution_bundle",
        "baseline_bundle_anchor_sha256",
        "runtime_source_binding_id",
        "topology_id",
        "topology_artifact_id",
        "baseline_runtime_trace_id",
        "baseline_runtime_report_id",
        "baseline_report_artifact_id",
        "execution_scope",
        "whole_run_escalation_reason",
        "whole_run_escalation_policy_id",
        "ordered_direct_affected_node_ids",
        "ordered_execution_node_ids",
        "ordered_affected_cell_ids",
        "ordered_direct_source_artifacts",
        "ordered_supporting_artifacts",
        "ordered_binding_artifacts",
        "root_review_required",
        "provider_calls",
        "model_calls",
        "network_calls",
        "connector_calls",
        "external_drs_calls",
        "authority_created",
        "permission_created",
        "action_commit_packet_created",
        "receipt_created",
        "final_output_created",
        "drs_write_created",
        "real_world_effects_count",
    )
    assert tuple(fr.FractalRuntimeExecutionBundleV02.__annotations__)[-1] == (
        "observed_work_context"
    )
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
        actual = getattr(fr, name)
        if name == "VALIDATION_TARGETS":
            assert actual == (*expected, "OBSERVED_WORK_BINDINGS_AGAINST_SOURCES")
        elif name == "CAUSAL_DECISION_EFFECTS":
            assert actual == (
                *expected,
                "OBSERVED_WORK_INPUT",
                "OBSERVED_WORK_CELL_BINDING",
            )
        else:
            assert actual == expected
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
    assert len(fr.VALIDATION_TARGETS) == 35
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
    contract_non_reason_literals = {"g2d_runtime"}
    assert contract_non_reason_literals.issubset(module_reason_literals)
    assert contract_non_reason_literals.isdisjoint(fr.PUBLIC_G2D_REASON_CODES)
    assert (module_reason_literals - contract_non_reason_literals).issubset(
        fr.PUBLIC_G2D_REASON_CODES
    )
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


def test_private_g2d_finalize_pair_and_validation_hot_path_v02(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixtures = _fixture_family()
    policy = fixtures[fr.FractalRuntimePolicyV02]
    topology_seed = fixtures[fr.RuntimeTopologySeedV02]
    topology = fixtures[fr.RuntimeExecutionTopologyV02]
    cell_input = fixtures[fr.FractalCellInputV02]
    queue_template = fixtures[fr.FractalCellQueueEntryV02]
    root_allocated = fixtures[fr.FractalRuntimeBudgetV02]
    assert isinstance(policy, fr.FractalRuntimePolicyV02)
    assert isinstance(topology_seed, fr.RuntimeTopologySeedV02)
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(cell_input, fr.FractalCellInputV02)
    assert isinstance(queue_template, fr.FractalCellQueueEntryV02)
    assert isinstance(root_allocated, fr.FractalRuntimeBudgetV02)

    root_active = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=None,
        predecessor_budget=root_allocated,
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
    root_created = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=None,
        predecessor_budget=root_active,
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
    allocation_entries = tuple(
        replace(queue_template, queue_entry_id=queue_entry_id)
        for queue_entry_id in cell_input.ordered_initial_queue_entry_ids
    )
    child_id = cell_input.ordered_planned_child_cell_ids[0]
    child_allocated = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=root_created,
        predecessor_budget=None,
        owning_cell_id=child_id,
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=cell_input,
        canonical_child_index=0,
        allocation_queue_entries=allocation_entries,
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    finalize_decision = _decision("t08", "shared-finalize")
    child_final = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=root_created,
        predecessor_budget=child_allocated,
        owning_cell_id=child_id,
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="FINAL",
        budget_event_kind="FINALIZE",
        budget_context_input=cell_input,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=finalize_decision,
        paired_cell_budget=None,
        child_result=None,
    )
    child_context = replace(cell_input, cell_id=child_id)
    paired_global = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=None,
        predecessor_budget=root_created,
        owning_cell_id=topology.root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="ACTIVE",
        budget_event_kind="FINALIZE",
        budget_context_input=child_context,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=finalize_decision,
        paired_cell_budget=child_final,
        child_result=None,
    )
    standalone_root_final = fr.build_fractal_runtime_budget_v02(
        policy=policy,
        topology_seed=topology_seed,
        allocation_parent_budget=None,
        predecessor_budget=paired_global,
        owning_cell_id=topology.root_cell_id,
        budget_scope="ROOT_GLOBAL_AND_CELL",
        budget_state="FINAL",
        budget_event_kind="FINALIZE",
        budget_context_input=cell_input,
        canonical_child_index=None,
        allocation_queue_entries=(),
        transition_decision=finalize_decision,
        paired_cell_budget=None,
        child_result=None,
    )
    budgets = (
        root_allocated,
        root_active,
        root_created,
        child_allocated,
        child_final,
        paired_global,
        standalone_root_final,
    )
    assert child_final.budget_state == "FINAL"
    assert paired_global.budget_state == "ACTIVE"
    assert standalone_root_final.budget_state == "FINAL"
    assert child_final.budget_event_ref == standalone_root_final.budget_event_ref
    assert fr._d3_is_adjacent_child_finalize_global_pair_v02(budgets, 5)
    assert not fr._d3_is_adjacent_child_finalize_global_pair_v02(budgets, 6)
    fr._d3_validate_budget_log_v02(
        budgets,
        topology=topology,
        policy=policy,
        source_context=None,
    )
    invalid_standalone = _seal(
        replace(standalone_root_final, budget_state="ACTIVE")
    )
    with pytest.raises(ValueError, match="g2d_budget_state_transition_invalid"):
        fr._d3_validate_budget_log_v02(
            (*budgets[:-1], invalid_standalone),
            topology=topology,
            policy=policy,
            source_context=None,
        )
    invalid_paired = _seal(replace(paired_global, budget_state="FINAL"))
    with pytest.raises(ValueError, match="g2d_budget_state_transition_invalid"):
        fr._d3_validate_budget_log_v02(
            (*budgets[:5], invalid_paired, standalone_root_final),
            topology=topology,
            policy=policy,
            source_context=None,
        )

    original_get_type_hints = fr._get_type_hints
    resolved_types: list[type[object]] = []

    def counted_get_type_hints(expected_type: type[object]) -> dict[str, object]:
        resolved_types.append(expected_type)
        return original_get_type_hints(expected_type)

    monkeypatch.setattr(fr, "_get_type_hints", counted_get_type_hints)
    fr._clear_structural_validation_caches_v02()
    first_policy_report = fr.validate_fractal_runtime_policy_v02(policy)
    second_policy_report = fr.validate_fractal_runtime_policy_v02(policy)
    assert first_policy_report.status == second_policy_report.status == "PASS"
    assert resolved_types == [fr.FractalRuntimePolicyV02]
    budget_report = fr.validate_fractal_runtime_budget_v02(root_allocated)
    assert budget_report.status == "PASS"
    assert resolved_types == [
        fr.FractalRuntimePolicyV02,
        fr.FractalRuntimeBudgetV02,
    ]

    fr._SERIALIZED_VALIDATION_SUCCESS_CACHE_V02.clear()
    original_annotation_errors = fr._annotation_errors
    annotation_types: list[type[object]] = []

    def counted_annotation_errors(
        value: object,
        expected_type: type[object],
    ) -> tuple[str, ...]:
        annotation_types.append(expected_type)
        return original_annotation_errors(value, expected_type)

    monkeypatch.setattr(fr, "_annotation_errors", counted_annotation_errors)
    assert fr.validate_fractal_runtime_policy_v02(policy).status == "PASS"
    assert annotation_types == [fr.FractalRuntimePolicyV02]
    monkeypatch.setattr(fr, "_annotation_errors", original_annotation_errors)

    original_canonical_json = fr._canonical_json_bytes_v01
    canonicalized_material: list[object] = []

    def counted_canonical_json(value: object) -> bytes:
        canonicalized_material.append(value)
        return original_canonical_json(value)

    monkeypatch.setattr(fr, "_canonical_json_bytes_v01", counted_canonical_json)
    assert fr.rebuild_fractal_runtime_policy_identity_v02(policy) == policy.policy_id
    assert len(canonicalized_material) == 1
    monkeypatch.setattr(fr, "_canonical_json_bytes_v01", original_canonical_json)

    fr._clear_structural_validation_caches_v02()
    original_uncached = fr._serialized_errors_uncached_v02
    uncached_types: list[type[object]] = []

    def counted_uncached(
        value: object,
        expected_type: type[object],
    ) -> tuple[str, ...]:
        uncached_types.append(expected_type)
        return original_uncached(value, expected_type)

    monkeypatch.setattr(fr, "_serialized_errors_uncached_v02", counted_uncached)
    first = fr.validate_fractal_runtime_policy_v02(policy)
    second = fr.validate_fractal_runtime_policy_v02(policy)
    assert first == second and first is not second
    assert uncached_types.count(fr.FractalRuntimePolicyV02) == 1
    first_bytes = canonical_json_bytes_v01(
        fr.fractal_runtime_validation_report_to_plain_data_v02(first)
    )
    second_bytes = canonical_json_bytes_v01(
        fr.fractal_runtime_validation_report_to_plain_data_v02(second)
    )
    assert first_bytes == second_bytes
    mutated_policy = _seal(replace(policy, root_review_required=False))
    assert fr.validate_fractal_runtime_policy_v02(mutated_policy).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_policy_v02(mutated_policy).status == "FAIL_CLOSED"
    assert uncached_types.count(fr.FractalRuntimePolicyV02) == 3
    wrong = object()
    wrong_first = fr.validate_fractal_runtime_policy_v02(wrong)
    wrong_second = fr.validate_fractal_runtime_policy_v02(wrong)
    assert wrong_first == wrong_second
    assert wrong_first.status == "FAIL_CLOSED"
    assert wrong_first.reason_codes == ("g2d_type_invalid",)
    assert uncached_types.count(fr.FractalRuntimePolicyV02) == 5
    assert len(fr._SERIALIZED_VALIDATION_SUCCESS_CACHE_V02) <= (
        fr._SERIALIZED_VALIDATION_SUCCESS_CACHE_MAX_V02
    )
    monkeypatch.setattr(fr, "_serialized_errors_uncached_v02", original_uncached)

    fr._clear_structural_validation_caches_v02()
    for cls, value in fixtures.items():
        validator, serializer, rebuilder = FUNCTION_FAMILIES[cls]
        first_validation = validator(value)
        second_validation = validator(value)
        assert first_validation == second_validation
        first_plain = serializer(value)
        second_plain = serializer(value)
        assert first_plain is not second_plain
        assert canonical_json_bytes_v01(first_plain) == canonical_json_bytes_v01(
            second_plain
        )
        identity_field = next(
            row[1] for row in fr.IDENTITY_PROFILE_ROWS_V02 if row[0] is cls
        )
        assert rebuilder(value) == getattr(value, identity_field)
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert len(fr.PUBLIC_G2D_REASON_CODES) == 220
    assert len(fr.VALIDATION_TARGETS) == 35
    assert len(fr.FAILURE_STAGES) == 30


def test_private_g2d_source_topology_canonical_cache_v02(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _d2_g2c_family("full_fractal")["source"]
    assert type(source) is fr.FractalRuntimeSourceContextV02
    with pytest.raises(TypeError, match="unhashable type: 'dict'"):
        hash(source)
    assert fr.validate_fractal_runtime_source_context_v02(source).status == "PASS"

    first_key = fr._source_context_success_cache_key_v02(source)
    second_key = fr._source_context_success_cache_key_v02(source)
    assert type(first_key) is tuple
    assert first_key == second_key
    hash(first_key)
    assert first_key[0] == "source_context_family"
    frozen_source = first_key[1]
    assert type(frozen_source) is tuple
    assert frozen_source[:2] == (
        "dataclass",
        "hedgehog.kernel.fractal_runtime_v02.FractalRuntimeSourceContextV02",
    )
    top_level_fields = tuple(name for name, _value in frozen_source[2])
    assert top_level_fields == tuple(field.name for field in fields(type(source)))
    assert len(top_level_fields) == 15

    def key_contains_reference(value: object, target: object) -> bool:
        return value is target or (
            type(value) is tuple
            and any(key_contains_reference(item, target) for item in value)
        )

    def key_leaf_types(value: object) -> set[type[object]]:
        if type(value) is tuple:
            result: set[type[object]] = {tuple}
            for item in value:
                result.update(key_leaf_types(item))
            return result
        return {type(value)}

    assert not key_contains_reference(first_key, source)
    assert key_leaf_types(first_key).issubset(
        {tuple, str, int, bool, bytes, type(None)}
    )

    packet = dict(source.g2c_source_context.business_request_context_packet)
    packet["business_subject"] = (
        packet["business_subject"] + ":cache-key-mutation"
    )
    invalid_g2c_source = replace(
        source.g2c_source_context,
        business_request_context_packet=packet,
    )
    invalid_source = replace(source, g2c_source_context=invalid_g2c_source)
    assert type(invalid_source) is fr.FractalRuntimeSourceContextV02
    invalid_key = fr._source_context_success_cache_key_v02(invalid_source)
    assert type(invalid_key) is tuple
    assert invalid_key != first_key
    initial_invalid_report = fr.validate_fractal_runtime_source_context_v02(
        invalid_source
    )
    assert initial_invalid_report.status == "FAIL_CLOSED"

    fr._clear_structural_validation_caches_v02()
    assert not fr._SOURCE_CONTEXT_FAMILY_SUCCESS_CACHE_V02
    assert not fr._TOPOLOGY_CONSTRUCTION_SUCCESS_CACHE_V02
    assert not fr._TOPOLOGY_PARTS_SUCCESS_CACHE_V02
    assert not fr._RETAINED_BASE_REPORTS_SUCCESS_CACHE_V02

    counts = {
        "source": 0,
        "topology": 0,
        "parts": 0,
        "reports": 0,
    }
    original_source = fr._validate_source_context_family_uncached_v02
    original_topology = (
        fr._construct_runtime_execution_topology_from_source_uncached_v02
    )
    original_parts = fr._d3_reconstruct_topology_parts_uncached_v02
    original_reports = fr._d3_expected_retained_base_reports_uncached_v02

    def counted_source(value: object) -> tuple[str | None, tuple[str, ...]]:
        counts["source"] += 1
        return original_source(value)

    def counted_topology(
        source_context: fr.FractalRuntimeSourceContextV02,
    ) -> fr.RuntimeExecutionTopologyV02:
        counts["topology"] += 1
        return original_topology(source_context)

    def counted_parts(
        source_context: fr.FractalRuntimeSourceContextV02,
        topology: fr.RuntimeExecutionTopologyV02,
    ) -> tuple[
        fr.RuntimeTopologySourceBindingV02,
        fr.RuntimeTopologySeedV02,
        fr.FractalRuntimeBudgetV02,
        tuple[fr.RuntimeTopologyNodeV02, ...],
    ]:
        counts["parts"] += 1
        return original_parts(source_context, topology)

    def counted_reports(
        source_context: fr.FractalRuntimeSourceContextV02,
        topology: fr.RuntimeExecutionTopologyV02,
    ) -> tuple[fr.FractalRuntimeValidationReportV02, ...]:
        counts["reports"] += 1
        return original_reports(source_context, topology)

    monkeypatch.setattr(
        fr,
        "_validate_source_context_family_uncached_v02",
        counted_source,
    )
    monkeypatch.setattr(
        fr,
        "_construct_runtime_execution_topology_from_source_uncached_v02",
        counted_topology,
    )
    monkeypatch.setattr(
        fr,
        "_d3_reconstruct_topology_parts_uncached_v02",
        counted_parts,
    )
    monkeypatch.setattr(
        fr,
        "_d3_expected_retained_base_reports_uncached_v02",
        counted_reports,
    )

    source_reports = tuple(
        fr.validate_fractal_runtime_source_context_v02(source)
        for _index in range(3)
    )
    assert all(report.status == "PASS" for report in source_reports)
    assert source_reports[0] == source_reports[1] == source_reports[2]
    assert source_reports[0] is not source_reports[1]
    assert source_reports[1] is not source_reports[2]
    assert counts["source"] == 1

    topology = fr.construct_runtime_execution_topology_v02(source)
    topology_reports = tuple(
        fr.validate_runtime_execution_topology_against_sources_v02(
            topology,
            source_context=source,
        )
        for _index in range(2)
    )
    assert all(report.status == "PASS" for report in topology_reports)
    assert topology_reports[0] == topology_reports[1]
    assert topology_reports[0] is not topology_reports[1]
    assert counts["topology"] <= 1

    topology_parts = tuple(
        fr._d3_reconstruct_topology_parts_v02(source, topology)
        for _index in range(3)
    )
    assert topology_parts[0] == topology_parts[1] == topology_parts[2]
    assert all(type(parts) is tuple for parts in topology_parts)
    assert all(
        item.__dataclass_params__.frozen
        for item in (*topology_parts[0][:-1], *topology_parts[0][-1])
    )
    assert counts["parts"] == 1

    retained_reports = tuple(
        fr._d3_expected_retained_base_reports_v02(source, topology)
        for _index in range(3)
    )
    assert retained_reports[0] == retained_reports[1] == retained_reports[2]
    assert all(type(reports) is tuple for reports in retained_reports)
    assert all(report.status == "PASS" for report in retained_reports[0])
    assert counts["reports"] == 1

    source_count_before_failures = counts["source"]
    first_failure = fr.validate_fractal_runtime_source_context_v02(invalid_source)
    second_failure = fr.validate_fractal_runtime_source_context_v02(invalid_source)
    assert first_failure.status == second_failure.status == "FAIL_CLOSED"
    assert first_failure.reason_codes == second_failure.reason_codes
    assert first_failure.source_reason_codes == second_failure.source_reason_codes
    assert counts["source"] == source_count_before_failures + 2
    assert len(fr._SOURCE_CONTEXT_FAMILY_SUCCESS_CACHE_V02) == 1

    source_count_before_clear = counts["source"]
    fr._clear_structural_validation_caches_v02()
    assert not fr._SOURCE_CONTEXT_FAMILY_SUCCESS_CACHE_V02
    assert not fr._TOPOLOGY_CONSTRUCTION_SUCCESS_CACHE_V02
    assert not fr._TOPOLOGY_PARTS_SUCCESS_CACHE_V02
    assert not fr._RETAINED_BASE_REPORTS_SUCCESS_CACHE_V02
    assert fr.validate_fractal_runtime_source_context_v02(source).status == "PASS"
    assert counts["source"] == source_count_before_clear + 1
    assert len(fr._SOURCE_CONTEXT_FAMILY_SUCCESS_CACHE_V02) == 1

    assert fr._SOURCE_CONTEXT_FAMILY_SUCCESS_CACHE_MAX_V02 == 16
    assert fr._TOPOLOGY_CONSTRUCTION_SUCCESS_CACHE_MAX_V02 == 16
    assert fr._TOPOLOGY_PARTS_SUCCESS_CACHE_MAX_V02 == 32
    assert fr._RETAINED_BASE_REPORTS_SUCCESS_CACHE_MAX_V02 == 32
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert len(fr.PUBLIC_G2D_REASON_CODES) == 220
    assert len(fr.VALIDATION_TARGETS) == 35
    assert len(fr.FAILURE_STAGES) == 30
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_d4_")
        for node in ast.walk(test_tree)
    ) == 16


def test_private_g2d_root_result_structural_evidence_partition_v02() -> None:
    fixtures = _fixture_family()
    root_input = fixtures[fr.FractalCellInputV02]
    root_result = fixtures[fr.FractalCellResultV02]
    partial_failure = fixtures[fr.FractalPartialFailureRecordV02]
    assert type(root_input) is fr.FractalCellInputV02
    assert type(root_result) is fr.FractalCellResultV02
    assert type(partial_failure) is fr.FractalPartialFailureRecordV02

    child_input_id = "frcellin_v02:" + "3" * 64
    child_evidence = (root_input.cell_input_id, "evidence:child-retained")
    child_result = _seal(fr.FractalCellResultV02(
        result_id="frcellresult_v02:" + "0" * 64,
        topology_id=root_result.topology_id,
        topology_seed_id=root_result.topology_seed_id,
        cell_id=partial_failure.child_cell_id,
        parent_cell_id=root_input.cell_id,
        cell_depth=1,
        cell_input_id=child_input_id,
        ordered_terminal_queue_entry_ids=(
            root_result.ordered_terminal_queue_entry_ids[0],
        ),
        ordered_child_result_ids=(),
        outcome="BLOCKED",
        accepted_output_refs=(),
        evidence_refs=child_evidence,
        pre_result_validation_report_id=(
            root_result.pre_result_validation_report_id
        ),
        post_vv_report_ref="vv:root-evidence-partition:child",
        gt_advisory_ref="gt:root-evidence-partition:child",
        partial_failure_ids=(),
        allocated_cell_budget_id=partial_failure.allocated_cell_budget_id,
        final_cell_budget_id=partial_failure.final_cell_budget_id,
        global_budget_id=partial_failure.global_budget_id,
        scope_ref=root_result.scope_ref,
        reason_codes=("g2d_required_child_failure",),
        source_reason_codes=(),
        trace_refs=(
            child_input_id,
            root_result.ordered_terminal_queue_entry_ids[0],
            *child_evidence,
            root_result.pre_result_validation_report_id,
            partial_failure.allocated_cell_budget_id,
            partial_failure.final_cell_budget_id,
            partial_failure.global_budget_id,
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
    assert type(child_result) is fr.FractalCellResultV02
    assert fr.validate_fractal_cell_result_v02(child_result).status == "PASS"
    child_before = canonical_json_bytes_v01(
        fr.fractal_cell_result_to_plain_data_v02(child_result)
    )

    aggregated_evidence = (
        "evidence:root-before",
        root_input.cell_input_id,
        "evidence:child-retained",
        "evidence:root-after",
    )
    partitioned_evidence = fr._d4_partition_root_structural_evidence_v02(
        cell_input=root_input,
        child_results=(child_result,),
        evidence_refs=aggregated_evidence,
    )
    assert partitioned_evidence == (
        "evidence:root-before",
        "evidence:child-retained",
        "evidence:root-after",
    )
    assert child_result.evidence_refs == child_evidence
    assert canonical_json_bytes_v01(
        fr.fractal_cell_result_to_plain_data_v02(child_result)
    ) == child_before

    root_trace = (
        root_input.cell_input_id,
        *root_result.ordered_terminal_queue_entry_ids,
        child_result.result_id,
        *root_result.accepted_output_refs,
        *partitioned_evidence,
        root_result.pre_result_validation_report_id,
        *root_result.partial_failure_ids,
        root_result.allocated_cell_budget_id,
        root_result.final_cell_budget_id,
        root_result.global_budget_id,
    )
    partitioned_root = _seal(replace(
        root_result,
        result_id="frcellresult_v02:" + "0" * 64,
        ordered_child_result_ids=(child_result.result_id,),
        evidence_refs=partitioned_evidence,
        trace_refs=root_trace,
    ))
    assert type(partitioned_root) is fr.FractalCellResultV02
    assert fr.validate_fractal_cell_result_v02(partitioned_root).status == "PASS"
    assert partitioned_root.trace_refs.count(root_input.cell_input_id) == 1

    artifact_trace_before_profile_c = (
        partitioned_root.post_vv_report_ref,
        partitioned_root.gt_advisory_ref,
        *partitioned_root.trace_refs,
    )
    assert artifact_trace_before_profile_c[-2:] == (
        partitioned_root.final_cell_budget_id,
        partitioned_root.global_budget_id,
    )
    assert (
        partitioned_root.final_cell_budget_id
        == partitioned_root.global_budget_id
    )
    artifact_trace = artifact_trace_before_profile_c[:-1]
    assert artifact_trace[:2] == (
        partitioned_root.post_vv_report_ref,
        partitioned_root.gt_advisory_ref,
    )
    assert all(artifact_trace.count(item) == 1 for item in artifact_trace)
    assert artifact_trace.count(partitioned_root.global_budget_id) == 1
    payload = fr.fractal_cell_result_to_plain_data_v02(partitioned_root)
    assert payload["final_cell_budget_id"] == partitioned_root.final_cell_budget_id
    assert payload["global_budget_id"] == partitioned_root.global_budget_id

    non_root_input = replace(root_input, parent_cell_id=root_input.cell_id)
    assert fr._d4_partition_root_structural_evidence_v02(
        cell_input=non_root_input,
        child_results=(child_result,),
        evidence_refs=aggregated_evidence,
    ) is aggregated_evidence

    child_without_root_input = _seal(replace(
        child_result,
        result_id="frcellresult_v02:" + "0" * 64,
        evidence_refs=("evidence:child-retained",),
        trace_refs=(
            child_result.cell_input_id,
            *child_result.ordered_terminal_queue_entry_ids,
            "evidence:child-retained",
            child_result.pre_result_validation_report_id,
            child_result.allocated_cell_budget_id,
            child_result.final_cell_budget_id,
            child_result.global_budget_id,
        ),
    ))
    assert type(child_without_root_input) is fr.FractalCellResultV02
    assert (
        fr.validate_fractal_cell_result_v02(child_without_root_input).status
        == "PASS"
    )
    no_carrier_evidence = ("evidence:root-before", "evidence:child-retained")
    assert fr._d4_partition_root_structural_evidence_v02(
        cell_input=root_input,
        child_results=(child_without_root_input,),
        evidence_refs=no_carrier_evidence,
    ) is no_carrier_evidence
    no_child_evidence = ("evidence:root-only",)
    assert fr._d4_partition_root_structural_evidence_v02(
        cell_input=root_input,
        child_results=(),
        evidence_refs=no_child_evidence,
    ) is no_child_evidence

    with pytest.raises(ValueError, match="g2d_result_proposal_invalid"):
        fr._d4_partition_root_structural_evidence_v02(
            cell_input=root_input,
            child_results=(child_result,),
            evidence_refs=("evidence:child-retained",),
        )
    with pytest.raises(ValueError, match="g2d_result_proposal_invalid"):
        fr._d4_partition_root_structural_evidence_v02(
            cell_input=root_input,
            child_results=(replace(child_result, parent_cell_id="cell:foreign"),),
            evidence_refs=aggregated_evidence,
        )

    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert len(fr.G2D_TYPES_V02) == 21
    assert len(fr.PUBLIC_G2D_REASON_CODES) == 220
    assert len(fr.VALIDATION_TARGETS) == 35
    assert len(fr.FAILURE_STAGES) == 30
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_d4_")
        for node in ast.walk(test_tree)
    ) == 16


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
    policy = fixtures[fr.FractalRuntimePolicyV02]
    policy_schema = Draft202012Validator(schema["$defs"]["FractalRuntimePolicyV02"])
    canonical_policy_data = fr.fractal_runtime_policy_to_plain_data_v02(policy)
    assert policy.max_parallelism == 3
    assert schema["$defs"]["FractalRuntimePolicyV02"]["properties"]["max_parallelism"]["const"] == 3
    assert fr.validate_fractal_runtime_policy_v02(policy).status == "PASS"
    policy_schema.validate(canonical_policy_data)
    rebuilt_policy = fr.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=("capability:source:semantic",),
        permitted_child_scope_refs=(),
    )
    assert rebuilt_policy == policy
    assert fr.fractal_runtime_policy_to_plain_data_v02(rebuilt_policy) == canonical_policy_data
    assert rebuilt_policy.policy_id == policy.policy_id
    legacy_policy = replace(policy, max_parallelism=4)
    legacy_report = fr.validate_fractal_runtime_policy_v02(legacy_policy)
    assert legacy_report.status == "FAIL_CLOSED"
    assert "g2d_identity_mismatch" in legacy_report.reason_codes
    assert "g2d_topology_policy_invalid" in legacy_report.reason_codes
    legacy_policy_id = fr.rebuild_fractal_runtime_policy_identity_v02(legacy_policy)
    resealed_legacy_policy = replace(legacy_policy, policy_id=legacy_policy_id)
    assert resealed_legacy_policy.policy_id != policy.policy_id
    resealed_report = fr.validate_fractal_runtime_policy_v02(resealed_legacy_policy)
    assert resealed_report.status == "FAIL_CLOSED"
    assert "g2d_topology_policy_invalid" in resealed_report.reason_codes
    legacy_policy_data = dict(canonical_policy_data)
    legacy_policy_data["policy_id"] = legacy_policy_id
    legacy_policy_data["max_parallelism"] = 4
    with pytest.raises(ValidationError):
        policy_schema.validate(legacy_policy_data)
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
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert fr.D1_MODULE_PUBLIC_FUNCTION_COUNT == 74
    assert fr.TOTAL_G2D_TYPE_COUNT == 21
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
    assert len(public_functions) == 116
    assert not callable(getattr(fr, "execute_fractal_runtime_v02", None))
    assert callable(getattr(fr, "build_fractal_runtime_execution_bundle_v02", None))
    module_source = MODULE_PATH.read_text(encoding="utf-8")
    assert "import hedgehog.kernel\n" not in module_source
    assert "demo." not in module_source and "tests." not in module_source


def _d3_topology_parts(
    source: fr.FractalRuntimeSourceContextV02,
    topology: fr.RuntimeExecutionTopologyV02,
) -> tuple[
    fr.RuntimeTopologySourceBindingV02,
    fr.RuntimeTopologySeedV02,
    fr.FractalRuntimeBudgetV02,
    tuple[fr.RuntimeTopologyNodeV02, ...],
]:
    return fr._d3_reconstruct_topology_parts_v02(source, topology)


def _d3_budget_successor(
    env: dict[str, object],
    predecessor: fr.FractalRuntimeBudgetV02,
    *,
    event: str,
    decision: TransitionDecisionV01 | None = None,
    cell_input: fr.FractalCellInputV02 | None = None,
    allocation_parent: fr.FractalRuntimeBudgetV02 | None = None,
    owning_cell_id: str | None = None,
    scope: str = "ROOT_GLOBAL_AND_CELL",
    canonical_child_index: int | None = None,
    allocation_queue_entries: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    paired_cell_budget: fr.FractalRuntimeBudgetV02 | None = None,
    state: str = "ACTIVE",
) -> fr.FractalRuntimeBudgetV02:
    source = env["source"]
    topology = env["topology"]
    seed = env["seed"]
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(seed, fr.RuntimeTopologySeedV02)
    return fr.build_fractal_runtime_budget_v02(
        policy=source.runtime_policy,
        topology_seed=seed,
        allocation_parent_budget=allocation_parent,
        predecessor_budget=predecessor,
        owning_cell_id=owning_cell_id or topology.root_cell_id,
        budget_scope=scope,
        budget_state=state,
        budget_event_kind=event,
        budget_context_input=cell_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=allocation_queue_entries,
        transition_decision=decision,
        paired_cell_budget=paired_cell_budget,
        child_result=None,
    )


def _d3_prefix_kwargs(
    env: dict[str, object],
    **overrides: object,
) -> dict[str, object]:
    result = {
        "settled_budget_log": env.get("budget_log", ()),
        "settled_queue_entry_log": env.get("queue_log", ()),
        "settled_queue_artifact_log": env.get("artifact_log", ()),
        "settled_cell_inputs": env.get("cell_inputs", ()),
        "settled_scope_projections": env.get("scope_projections", ()),
        "settled_revise_observations": env.get("revise_observations", ()),
        "settled_backpressure_states": env.get("backpressure_states", ()),
        "settled_validation_reports": env.get("validation_reports", ()),
    }
    result.update(overrides)
    return result


def _d3_clone_environment(env: dict[str, object]) -> dict[str, object]:
    return dict(env)


def _d3_retained_reports(
    env: dict[str, object],
    queue_log: tuple[fr.FractalCellQueueEntryV02, ...],
) -> tuple[fr.FractalRuntimeValidationReportV02, ...]:
    reports = env["validation_reports"]
    assert isinstance(reports, tuple) and len(reports) >= 4
    scope_reports = tuple(
        item
        for item in reports[4:]
        if item.validation_target == "SCOPE_PROJECTION_AGAINST_SOURCES"
    )
    input_reports = tuple(
        item
        for item in reports[4:]
        if item.validation_target == "CELL_INPUT_AGAINST_SOURCES"
    )
    return (
        *reports[:4],
        *(fr.validate_fractal_cell_queue_entry_v02(item) for item in queue_log),
        *scope_reports,
        *input_reports,
    )


def _d3_eval(
    env: dict[str, object],
    *,
    source_artifact: KernelArtifactV01,
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
    local_child_result: fr.FractalCellResultV02 | None = None,
    local_child_result_artifact: KernelArtifactV01 | None = None,
    validation_report: fr.FractalRuntimeValidationReportV02 | None = None,
    revise_observation: fr.FractalReviseObservationV02 | None = None,
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
    cell_id: str | None = None,
    parent_cell_id: str | None = None,
    planned_child_cell_id: str | None = None,
    cell_depth: int | None = None,
    scope_ref: str | None = None,
    parent_return_pre_post_vv_terminal_queue_entries: object = (),
    parent_return_child_results: object = (),
    parent_return_partial_failures: object = (),
    parent_return_result_proposal: object = None,
    parent_return_post_vv_report: object = None,
    parent_return_gt_advisory_report: object = None,
    parent_return_validation_reports: object = (),
) -> TransitionDecisionV01 | None:
    source = env["source"]
    topology = env["topology"]
    registry = env["registry"]
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(registry, transition_registry.TransitionRegistryV01)
    if current_entry is not None:
        cell_id = current_entry.cell_id if cell_id is None else cell_id
        parent_cell_id = current_entry.parent_cell_id if parent_cell_id is None else parent_cell_id
        planned_child_cell_id = (
            current_entry.planned_child_cell_id
            if planned_child_cell_id is None
            else planned_child_cell_id
        )
        cell_depth = current_entry.cell_depth if cell_depth is None else cell_depth
        scope_ref = current_entry.scope_ref if scope_ref is None else scope_ref
    else:
        cell_id = topology.root_cell_id if cell_id is None else cell_id
        cell_depth = 0 if cell_depth is None else cell_depth
        scope_ref = topology.accepted_scope_ref if scope_ref is None else scope_ref
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
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        validation_report=validation_report,
        parent_return_pre_post_vv_terminal_queue_entries=parent_return_pre_post_vv_terminal_queue_entries,
        parent_return_child_results=parent_return_child_results,
        parent_return_partial_failures=parent_return_partial_failures,
        parent_return_result_proposal=parent_return_result_proposal,
        parent_return_post_vv_report=parent_return_post_vv_report,
        parent_return_gt_advisory_report=parent_return_gt_advisory_report,
        parent_return_validation_reports=parent_return_validation_reports,
        revise_observation=revise_observation,
        backpressure_state=backpressure_state,
        transition_registry=registry,
        **_d3_prefix_kwargs(env),
    )


def _d3_root_environment(case: dict[str, object]) -> dict[str, object]:
    source = case["source"]
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    topology = fr.construct_runtime_execution_topology_v02(source)
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    t01 = fr.evaluate_route_eligibility_to_topology_transition_v02(
        source_context=source,
        topology=topology,
        transition_registry=registry,
    )
    topology_artifact = fr.project_runtime_execution_topology_kernel_artifact_v02(
        topology,
        source_context=source,
        topology_transition_decision=t01,
    )
    binding, seed, root_initial, nodes = _d3_topology_parts(source, topology)
    env: dict[str, object] = {
        "source": source,
        "topology": topology,
        "registry": registry,
        "t01": t01,
        "topology_artifact": topology_artifact,
        "binding": binding,
        "seed": seed,
        "root_initial": root_initial,
        "nodes": nodes,
        "budget_log": (),
        "queue_log": (),
        "artifact_log": (),
        "cell_inputs": (),
        "scope_projections": (),
        "revise_observations": (),
        "backpressure_states": (),
        "validation_reports": fr._d3_expected_retained_base_reports_v02(
            source,
            topology,
        ),
    }
    root_active = _d3_budget_successor(env, root_initial, event="ACTIVATE")
    root_create = _d3_budget_successor(env, root_active, event="CELL_CREATE")
    env["root_active"] = root_active
    env["root_create"] = root_create
    env["budget_log"] = (root_initial, root_active, root_create)
    planned = fr._derive_settled_planned_root_child_ids_v02(
        source_context=source,
        topology=topology,
        topology_transition_decision=t01,
        topology_artifact=topology_artifact,
    )
    t02 = tuple(
        _d3_eval(
            env,
            source_artifact=topology_artifact,
            node=node,
            current_entry=None,
            cell_input=None,
            cell_budget=root_create,
            global_budget=root_create,
        )
        for node in nodes
    )
    assert all(isinstance(item, TransitionDecisionV01) for item in t02)
    queues = fr.admit_runtime_execution_topology_v02(
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        topology_transition_decision=t01,
        cell_id=topology.root_cell_id,
        parent_cell_id=None,
        parent_slot_artifact=None,
        cell_depth=0,
        scope_ref=topology.accepted_scope_ref,
        cell_budget=root_create,
        global_budget=root_create,
        projected_nodes=nodes,
        planned_child_cell_ids=planned,
        admission_decisions=t02,
        cell_instantiation_order=(topology.root_cell_id,),
        **_d3_prefix_kwargs(env),
    )
    queue_log: tuple[fr.FractalCellQueueEntryV02, ...] = ()
    artifact_log: tuple[KernelArtifactV01, ...] = ()
    retained_reports = env["validation_reports"]
    assert isinstance(retained_reports, tuple)
    for entry in queues:
        artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry,
            topology_artifact=topology_artifact,
            predecessor_artifact=None,
            activation_parent_artifact=None,
            local_child_result_artifact=None,
            source_context=source,
            **_d3_prefix_kwargs(
                env,
                settled_queue_entry_log=queue_log + (entry,),
                settled_queue_artifact_log=artifact_log,
                settled_validation_reports=retained_reports,
            ),
        )
        queue_log += (entry,)
        artifact_log += (artifact,)
        retained_reports = (
            *retained_reports[:4],
            *(fr.validate_fractal_cell_queue_entry_v02(item) for item in queue_log),
        )
    queue_artifacts = artifact_log
    env["queue_log"] = queue_log
    env["artifact_log"] = artifact_log
    env["validation_reports"] = retained_reports
    cell_input = fr.build_fractal_cell_input_from_queue_v02(
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        cell_id=topology.root_cell_id,
        parent_cell_id=None,
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=root_create,
        global_budget=root_create,
        initial_queue_entries=queues,
        initial_queue_artifacts=queue_artifacts,
        ordered_planned_child_cell_ids=planned,
        **_d3_prefix_kwargs(env),
    )
    input_report = fr.validate_fractal_cell_input_against_sources_v02(
        cell_input,
        source_context=source,
        topology=topology,
        topology_artifact=topology_artifact,
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=root_create,
        global_budget=root_create,
        queue_entries=queues,
        queue_artifacts=queue_artifacts,
        **_d3_prefix_kwargs(env),
    )
    assert input_report.status == "PASS"
    env["cell_inputs"] = (cell_input,)
    env["validation_reports"] = retained_reports + (input_report,)
    env.update(
        planned=planned,
        t02=t02,
        queues=queues,
        queue_artifacts=queue_artifacts,
        cell_input=cell_input,
    )
    return env


@pytest.fixture(scope="module")
def d3_memory_informed_environment() -> dict[str, object]:
    return _d3_root_environment(_d2_g2c_family("memory_informed"))


@pytest.fixture(scope="module")
def d3_local_slm_environment() -> dict[str, object]:
    return _d3_root_environment(
        _d2_g2c_family(
            "local_slm",
            action_packet_required=True,
        )
    )


@pytest.fixture(scope="module")
def d3_cloud_llm_environment() -> dict[str, object]:
    return _d3_root_environment(
        _d2_g2c_family(
            "cloud_llm",
            narrow=True,
        )
    )


@pytest.fixture(scope="module")
def d3_full_semantic_environment() -> dict[str, object]:
    return _d3_root_environment(_d2_g2c_family("full_semantic"))


@pytest.fixture(scope="module")
def d3_full_fractal_micro_environment() -> dict[str, object]:
    return _d3_root_environment(_d2_g2c_family("full_fractal"))


@pytest.fixture(scope="module")
def d3_mode_environments(
    d3_memory_informed_environment: dict[str, object],
    d3_local_slm_environment: dict[str, object],
    d3_cloud_llm_environment: dict[str, object],
    d3_full_semantic_environment: dict[str, object],
    d3_full_fractal_micro_environment: dict[str, object],
) -> dict[str, dict[str, object]]:
    return {
        "memory_informed": d3_memory_informed_environment,
        "local_slm": d3_local_slm_environment,
        "cloud_llm": d3_cloud_llm_environment,
        "full_semantic": d3_full_semantic_environment,
        "full_fractal": d3_full_fractal_micro_environment,
    }


def _d3_advance(
    env: dict[str, object],
    *,
    current: fr.FractalCellQueueEntryV02,
    current_artifact: KernelArtifactV01,
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
    local_child_result: fr.FractalCellResultV02 | None = None,
    local_child_result_artifact: KernelArtifactV01 | None = None,
    revise_observation: fr.FractalReviseObservationV02 | None = None,
    validation_report: fr.FractalRuntimeValidationReportV02 | None = None,
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01, TransitionDecisionV01]:
    decision = _d3_eval(
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
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        validation_report=validation_report,
        revise_observation=revise_observation,
        backpressure_state=backpressure_state,
    )
    assert isinstance(decision, TransitionDecisionV01)
    topology = env["topology"]
    source = env["source"]
    topology_artifact = env["topology_artifact"]
    nodes = env["nodes"]
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    assert isinstance(topology_artifact, KernelArtifactV01)
    assert isinstance(nodes, tuple)
    budget_log = env["budget_log"]
    assert isinstance(budget_log, tuple)
    if (cell_budget_after, global_budget_after) != (
        cell_budget_before,
        global_budget_before,
    ):
        candidate_suffix = (
            (global_budget_after,)
            if cell_budget_after is global_budget_after
            else (cell_budget_after, global_budget_after)
        )
        assert all(item not in budget_log for item in candidate_suffix)
        budget_log += candidate_suffix
    env["budget_log"] = budget_log
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
        local_child_result=local_child_result,
        local_child_result_artifact=local_child_result_artifact,
        cell_instantiation_order=tuple(
            item.cell_id for item in env["cell_inputs"]
        ),
        projected_node_ids=cell_input.ordered_node_ids,
        round_start_queue_entries=round_entries,
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        **_d3_prefix_kwargs(env),
    )
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    reports = env["validation_reports"]
    assert isinstance(queue_log, tuple)
    assert isinstance(artifact_log, tuple)
    assert isinstance(reports, tuple)
    artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
        target,
        topology_artifact=topology_artifact,
        predecessor_artifact=current_artifact,
        activation_parent_artifact=None,
        local_child_result_artifact=local_child_result_artifact,
        source_context=source,
        **_d3_prefix_kwargs(
            env,
            settled_queue_entry_log=queue_log + (target,),
            settled_validation_reports=reports,
        ),
    )
    env["queue_log"] = queue_log + (target,)
    env["artifact_log"] = artifact_log + (artifact,)
    env["validation_reports"] = _d3_retained_reports(
        env,
        queue_log + (target,),
    )
    return target, artifact, decision


def _d3_indexes(
    env: dict[str, object],
    *,
    frontier: str = "COMPLETED",
) -> dict[str, object]:
    return fr._d3_validate_settled_runtime_prefix_v02(
        topology=env["topology"],
        policy=env["source"].runtime_policy,
        source_context=env["source"],
        frontier=frontier,
        **_d3_prefix_kwargs(env),
    )


def _d3_latest(env: dict[str, object]) -> tuple[fr.FractalCellQueueEntryV02, ...]:
    queue_log = env["queue_log"]
    assert isinstance(queue_log, tuple)
    return fr._d3_latest_queue_entries_v02(queue_log)


def _d3_start_node(
    env: dict[str, object],
    *,
    node_index: int,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
) -> tuple[
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
]:
    nodes = env["nodes"]
    cell_input = env["cell_input"]
    assert isinstance(nodes, tuple)
    assert isinstance(cell_input, fr.FractalCellInputV02)
    node = nodes[node_index]
    indexes = _d3_indexes(env)
    current = indexes["latest_by_key"][(cell_input.cell_id, node.node_id)]
    current_artifact = indexes["artifact_by_queue_id"][current.queue_entry_id]
    cell_budget = indexes["budget_by_id"][current.cell_budget_id]
    global_budget = indexes["budget_by_id"][current.global_budget_id]
    ready, ready_artifact, _ = _d3_advance(
        env,
        current=current,
        current_artifact=current_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        cell_budget_after=cell_budget,
        global_budget_after=global_budget,
        dependencies=dependencies,
        round_entries=_d3_latest(env),
    )
    t05 = _d3_eval(
        env,
        source_artifact=ready_artifact,
        node=node,
        current_entry=ready,
        cell_input=cell_input,
        cell_budget=cell_budget,
        global_budget=global_budget,
        dependencies=dependencies,
    )
    assert isinstance(t05, TransitionDecisionV01)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=current.cell_id,
        indexes=_d3_indexes(env),
    )
    start_cell = _d3_budget_successor(
        env,
        live_cell,
        event="START_NODE",
        decision=t05,
        cell_input=cell_input,
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=current.cell_id,
        scope=live_cell.budget_scope,
    )
    start_global = (
        start_cell
        if current.cell_id == env["topology"].root_cell_id
        else _d3_budget_successor(
            env,
            live_global,
            event="START_NODE",
            decision=t05,
            cell_input=cell_input,
            paired_cell_budget=start_cell,
        )
    )
    running, running_artifact, _ = _d3_advance(
        env,
        current=ready,
        current_artifact=ready_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        cell_budget_after=start_cell,
        global_budget_after=start_global,
        dependencies=dependencies,
        round_entries=_d3_latest(env),
    )
    return running, running_artifact, start_global


def _d3_make_ready(
    env: dict[str, object],
    *,
    current: fr.FractalCellQueueEntryV02,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    backpressure_state: fr.FractalBackpressureStateV02 | None = None,
    round_start_queue_entries: tuple[fr.FractalCellQueueEntryV02, ...] | None = None,
) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]:
    indexes = _d3_indexes(
        env,
        frontier="T03_DECISION" if backpressure_state is not None else "COMPLETED",
    )
    current_artifact = indexes["artifact_by_queue_id"][current.queue_entry_id]
    cell_anchor = indexes["budget_by_id"][current.cell_budget_id]
    global_anchor = indexes["budget_by_id"][current.global_budget_id]
    ready, ready_artifact, _decision = _d3_advance(
        env,
        current=current,
        current_artifact=current_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=cell_anchor,
        global_budget_before=global_anchor,
        cell_budget_after=cell_anchor,
        global_budget_after=global_anchor,
        dependencies=dependencies,
        round_entries=(
            _d3_latest(env)
            if round_start_queue_entries is None
            else round_start_queue_entries
        ),
        backpressure_state=backpressure_state,
        queue_reason_codes=(
            ("g2d_transition_backpressure_deferred",)
            if backpressure_state is not None
            else ()
        ),
    )
    if backpressure_state is not None:
        completed_indexes = _d3_indexes(env)
        assert completed_indexes["backpressure_closure_frontier_by_id"][
            backpressure_state.backpressure_id
        ] == len(env["queue_log"]) - 1
    return ready, ready_artifact


def _d3_start_ready_entry(
    env: dict[str, object],
    *,
    ready: fr.FractalCellQueueEntryV02,
    ready_artifact: KernelArtifactV01,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    round_start_queue_entries: tuple[fr.FractalCellQueueEntryV02, ...] | None = None,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
    fr.FractalRuntimeBudgetV02,
]:
    indexes = _d3_indexes(env)
    cell_anchor = indexes["budget_by_id"][ready.cell_budget_id]
    global_anchor = indexes["budget_by_id"][ready.global_budget_id]
    decision = _d3_eval(
        env,
        source_artifact=ready_artifact,
        node=node,
        current_entry=ready,
        cell_input=cell_input,
        cell_budget=cell_anchor,
        global_budget=global_anchor,
        dependencies=dependencies,
    )
    assert isinstance(decision, TransitionDecisionV01)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"], cell_id=ready.cell_id, indexes=indexes
    )
    start_cell = _d3_budget_successor(
        env,
        live_cell,
        event="START_NODE",
        decision=decision,
        cell_input=cell_input,
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=ready.cell_id,
        scope=live_cell.budget_scope,
    )
    start_global = (
        start_cell
        if ready.cell_id == env["topology"].root_cell_id
        else _d3_budget_successor(
            env,
            live_global,
            event="START_NODE",
            decision=decision,
            cell_input=cell_input,
            paired_cell_budget=start_cell,
        )
    )
    running, running_artifact, _ = _d3_advance(
        env,
        current=ready,
        current_artifact=ready_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=cell_anchor,
        global_budget_before=global_anchor,
        cell_budget_after=start_cell,
        global_budget_after=start_global,
        dependencies=dependencies,
        round_entries=(
            _d3_latest(env)
            if round_start_queue_entries is None
            else round_start_queue_entries
        ),
    )
    return running, running_artifact, start_cell, start_global


def _d3_activate_child(
    env: dict[str, object],
    *,
    slot_running: fr.FractalCellQueueEntryV02,
    slot_artifact: KernelArtifactV01,
    dependency: fr.FractalCellQueueEntryV02,
) -> dict[str, object]:
    source = env["source"]
    topology = env["topology"]
    parent_input = env["cell_input"]
    root_create = env["root_create"]
    nodes = env["nodes"]
    child_id = slot_running.planned_child_cell_id
    assert isinstance(child_id, str)
    canonical_child_index = nodes.index(
        next(item for item in nodes if item.node_id == slot_running.node_id)
    ) - 1
    indexes = _d3_indexes(env)
    _live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=topology, cell_id=topology.root_cell_id, indexes=indexes
    )
    material = fr._d3_child_activation_precheck_material_v02(
        source_context=source,
        topology=topology,
        source_artifact=slot_artifact,
        current_entry=slot_running,
        node=nodes[canonical_child_index + 1],
        cell_input=parent_input,
        cell_budget_before=live_global,
        global_budget_before=live_global,
        dependencies=(dependency,),
        indexes=indexes,
    )
    assert material["derived_disposition"] == "PASS_FOR_CHILD_ACTIVATION"
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
        allocation_queue_entries=env["queues"],
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
    child_active = _d3_budget_successor(
        env, child_allocated, event="ACTIVATE", cell_input=parent_input,
        allocation_parent=root_create, owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL", canonical_child_index=canonical_child_index,
        allocation_queue_entries=env["queues"],
    )
    global_active = _d3_budget_successor(
        env, live_global, event="ACTIVATE", cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=env["queues"], paired_cell_budget=child_active,
    )
    child_create = _d3_budget_successor(
        env, child_active, event="CELL_CREATE", cell_input=parent_input,
        allocation_parent=root_create, owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL", canonical_child_index=canonical_child_index,
        allocation_queue_entries=env["queues"],
    )
    global_create = _d3_budget_successor(
        env, global_active, event="CELL_CREATE", cell_input=parent_input,
        canonical_child_index=canonical_child_index,
        allocation_queue_entries=env["queues"], paired_cell_budget=child_create,
    )
    env["budget_log"] = env["budget_log"] + (
        child_allocated, child_active, global_active, child_create, global_create,
    )
    env["scope_projections"] = (*env["scope_projections"], projection)
    budget_by_id = {item.budget_id: item for item in env["budget_log"]}
    scope_reports = tuple(
        fr.validate_parent_child_scope_against_sources_v02(
            item,
            source_context=source,
            topology=topology,
            parent_input=env["cell_inputs"][0],
            parent_budget=root_create,
            child_budget=budget_by_id[item.child_budget_id],
            global_budget=budget_by_id[item.global_budget_id],
        )
        for item in env["scope_projections"]
    )
    input_reports = tuple(
        item
        for item in env["validation_reports"][4:]
        if item.validation_target == "CELL_INPUT_AGAINST_SOURCES"
    )
    env["validation_reports"] = (
        *env["validation_reports"][:4],
        *(fr.validate_fractal_cell_queue_entry_v02(item) for item in env["queue_log"]),
        *scope_reports,
        *input_reports,
    )
    leaf_nodes = tuple(nodes[index] for index in (0, 4, 5, 6))
    decisions = tuple(
        _d3_eval(
            env, source_artifact=env["topology_artifact"], node=node,
            current_entry=None, cell_input=None, cell_budget=child_create,
            global_budget=global_create, cell_id=child_id,
            parent_cell_id=topology.root_cell_id, cell_depth=1,
            scope_ref=projection.child_scope_ref,
        )
        for node in leaf_nodes
    )
    child_queues = fr.admit_runtime_execution_topology_v02(
        source_context=source, topology=topology,
        topology_artifact=env["topology_artifact"],
        topology_transition_decision=env["t01"], cell_id=child_id,
        parent_cell_id=topology.root_cell_id, parent_slot_artifact=slot_artifact,
        cell_depth=1, scope_ref=projection.child_scope_ref,
        cell_budget=child_create, global_budget=global_create,
        projected_nodes=leaf_nodes, planned_child_cell_ids=(),
        admission_decisions=decisions,
        cell_instantiation_order=tuple(item.cell_id for item in env["cell_inputs"]) + (child_id,),
        **_d3_prefix_kwargs(env),
    )
    child_artifacts: list[KernelArtifactV01] = []
    for entry in child_queues:
        artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry, topology_artifact=env["topology_artifact"],
            predecessor_artifact=None, activation_parent_artifact=slot_artifact,
            local_child_result_artifact=None, source_context=source,
            **_d3_prefix_kwargs(
                env,
                settled_queue_entry_log=env["queue_log"] + (entry,),
                settled_queue_artifact_log=env["artifact_log"],
            ),
        )
        env["queue_log"] = env["queue_log"] + (entry,)
        env["artifact_log"] = env["artifact_log"] + (artifact,)
        env["validation_reports"] = _d3_retained_reports(env, env["queue_log"])
        child_artifacts.append(artifact)
    child_input = fr.build_fractal_cell_input_from_queue_v02(
        source_context=source, topology=topology,
        topology_artifact=env["topology_artifact"], cell_id=child_id,
        parent_cell_id=topology.root_cell_id, parent_input=parent_input,
        parent_slot_artifact=slot_artifact, scope_projection=projection,
        cell_budget=child_create, global_budget=global_create,
        initial_queue_entries=child_queues,
        initial_queue_artifacts=tuple(child_artifacts),
        ordered_planned_child_cell_ids=(), **_d3_prefix_kwargs(env),
    )
    input_report = fr.validate_fractal_cell_input_against_sources_v02(
        child_input, source_context=source, topology=topology,
        topology_artifact=env["topology_artifact"], parent_input=parent_input,
        parent_slot_artifact=slot_artifact, scope_projection=projection,
        cell_budget=child_create, global_budget=global_create,
        queue_entries=child_queues, queue_artifacts=tuple(child_artifacts),
        **_d3_prefix_kwargs(env),
    )
    assert input_report.status == "PASS"
    env["cell_inputs"] = (*env["cell_inputs"], child_input)
    env["validation_reports"] = (*env["validation_reports"], input_report)
    return {
        "cell_id": child_id,
        "projection": projection,
        "allocated_budget": child_allocated,
        "cell_budget": child_create,
        "global_budget": global_create,
        "nodes": leaf_nodes,
        "queues": child_queues,
        "artifacts": tuple(child_artifacts),
        "input": child_input,
    }


def _d3_finish_running_local(
    env: dict[str, object],
    *,
    running: fr.FractalCellQueueEntryV02,
    running_artifact: KernelArtifactV01,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
    round_start_queue_entries: tuple[fr.FractalCellQueueEntryV02, ...] | None = None,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
]:
    indexes = _d3_indexes(env)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"], cell_id=running.cell_id, indexes=indexes
    )
    material = fr._d3_local_observation_material_v02(
        source_context=env["source"], topology=env["topology"], node=node,
        cell_input=cell_input, cell_budget_before=live_cell,
        global_budget_before=live_global, dependencies=dependencies,
        indexes=indexes,
    )
    decision = _d3_eval(
        env, source_artifact=running_artifact, node=node,
        current_entry=running, cell_input=cell_input,
        cell_budget=indexes["budget_by_id"][running.cell_budget_id],
        global_budget=indexes["budget_by_id"][running.global_budget_id],
        dependencies=dependencies,
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    assert isinstance(decision, TransitionDecisionV01)
    finish_cell = _d3_budget_successor(
        env, live_cell, event="FINISH_NODE", decision=decision,
        cell_input=cell_input,
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=running.cell_id, scope=live_cell.budget_scope,
    )
    finish_global = (
        finish_cell
        if running.cell_id == env["topology"].root_cell_id
        else _d3_budget_successor(
            env, live_global, event="FINISH_NODE", decision=decision,
            cell_input=cell_input, paired_cell_budget=finish_cell,
        )
    )
    validating, artifact, _ = _d3_advance(
        env, current=running, current_artifact=running_artifact, node=node,
        cell_input=cell_input,
        cell_budget_before=indexes["budget_by_id"][running.cell_budget_id],
        global_budget_before=indexes["budget_by_id"][running.global_budget_id],
        cell_budget_after=finish_cell, global_budget_after=finish_global,
        dependencies=dependencies,
        round_entries=(
            _d3_latest(env)
            if round_start_queue_entries is None
            else round_start_queue_entries
        ),
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    return validating, artifact, finish_global


def _d3_finish_no_child_gate(
    env: dict[str, object],
    *,
    running: fr.FractalCellQueueEntryV02,
    running_artifact: KernelArtifactV01,
    node: fr.RuntimeTopologyNodeV02,
    dependency: fr.FractalCellQueueEntryV02,
) -> tuple[
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
]:
    indexes = _d3_indexes(env)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=running.cell_id,
        indexes=indexes,
    )
    material = fr._d3_child_activation_precheck_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        source_artifact=running_artifact,
        current_entry=running,
        node=node,
        cell_input=env["cell_input"],
        cell_budget_before=live_cell,
        global_budget_before=live_global,
        dependencies=(dependency,),
        indexes=indexes,
    )
    anchor_cell = indexes["budget_by_id"][running.cell_budget_id]
    anchor_global = indexes["budget_by_id"][running.global_budget_id]
    t06 = _d3_eval(
        env,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=env["cell_input"],
        cell_budget=anchor_cell,
        global_budget=anchor_global,
        dependencies=(dependency,),
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_evidence_refs=material["derived_evidence_refs"],
    )
    assert isinstance(t06, TransitionDecisionV01)
    finish_cell = _d3_budget_successor(
        env,
        live_cell,
        event="FINISH_NODE",
        decision=t06,
        cell_input=env["cell_input"],
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=running.cell_id,
        scope=live_cell.budget_scope,
    )
    finish_global = (
        finish_cell
        if running.cell_id == env["topology"].root_cell_id
        else _d3_budget_successor(
            env,
            live_global,
            event="FINISH_NODE",
            decision=t06,
            cell_input=env["cell_input"],
            paired_cell_budget=finish_cell,
        )
    )
    validating, validating_artifact, _ = _d3_advance(
        env,
        current=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=env["cell_input"],
        cell_budget_before=anchor_cell,
        global_budget_before=anchor_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=(dependency,),
        round_entries=_d3_latest(env),
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_evidence_refs=material["derived_evidence_refs"],
    )
    terminal, terminal_artifact, terminal_decision = _d3_advance(
        env,
        current=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=env["cell_input"],
        cell_budget_before=finish_cell,
        global_budget_before=finish_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=(dependency,),
        round_entries=_d3_latest(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_evidence_refs=validating.observed_evidence_refs,
    )
    assert terminal_decision == fr._d3_transition_decision_v02(
        env["registry"],
        "t10" if terminal.state == "BLOCKED" else "t12",
    )
    return validating, validating_artifact, terminal, terminal_artifact


def _d3_child_result_boundary_environment(
    base: dict[str, object],
) -> tuple[
    dict[str, object],
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
]:
    env = _d3_clone_environment(base)
    dependency, _ = _d3_complete_local_node(env, node_index=0)
    slot, slot_artifact, _ = _d3_start_node(
        env, node_index=1, dependencies=(dependency,)
    )
    child = _d3_activate_child(
        env, slot_running=slot, slot_artifact=slot_artifact,
        dependency=dependency,
    )
    base_indexes = _d3_indexes(env)
    decision = fr._d3_transition_decision_v02(env["registry"], "t08")
    terminal_entries: list[fr.FractalCellQueueEntryV02] = []
    terminal_artifacts: list[KernelArtifactV01] = []
    for initial, initial_artifact in zip(
        child["queues"], child["artifacts"], strict=True
    ):
        predecessor_id = initial.queue_entry_id
        output_ref = f"output:boundary:{initial.node_instance_sequence}"
        evidence_ref = f"evidence:boundary:{initial.node_instance_sequence}"
        lineage = (
            initial.topology_id,
            initial.topology_seed_id,
            initial.cell_id,
            initial.parent_cell_id,
            initial.node_id,
            initial.cell_budget_id,
            initial.global_budget_id,
            initial.lineage_refs[7],
            predecessor_id,
            output_ref,
            evidence_ref,
        )
        terminal = _seal(replace(
            initial,
            queue_entry_id=(
                "frqueue_v02:"
                + f"{initial.node_instance_sequence + 1000:064x}"
            ),
            state="COMPLETED",
            prior_state="VALIDATING",
            predecessor_queue_entry_id=predecessor_id,
            predecessor_relation="EXACT_IMMEDIATE_PREDECESSOR",
            transition_decision_id=decision.decision_id,
            snapshot_sequence=initial.snapshot_sequence + 1,
            admission_round=initial.admission_round + 1,
            observed_output_refs=(output_ref,),
            observed_evidence_refs=(evidence_ref,),
            queue_reason_codes=(),
            advisory_refs=(),
            lineage_refs=lineage,
        ))
        assert isinstance(terminal, fr.FractalCellQueueEntryV02)
        assert terminal.prior_state == "VALIDATING"
        assert terminal.state == "COMPLETED"
        assert terminal.transition_decision_id == decision.decision_id
        artifact = fr._d3_build_queue_artifact_v02(
            terminal,
            parent_refs=(env["topology_artifact"].artifact_id, initial_artifact.artifact_id),
            source_context=env["source"],
        )
        terminal_entries.append(terminal)
        terminal_artifacts.append(artifact)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"], cell_id=child["cell_id"], indexes=base_indexes
    )
    final_decision = fr._d3_transition_decision_v02(env["registry"], "t12")
    final_cell = _d3_budget_successor(
        env, live_cell, event="FINALIZE", decision=final_decision,
        cell_input=child["input"], allocation_parent=env["root_create"],
        owning_cell_id=child["cell_id"], scope="CHILD_CELL_LOCAL",
        state="FINAL",
    )
    final_global = _d3_budget_successor(
        env, live_global, event="FINALIZE", decision=final_decision,
        cell_input=child["input"], paired_cell_budget=final_cell,
    )
    boundary_indexes = dict(base_indexes)
    boundary_indexes["latest_by_key"] = {
        **base_indexes["latest_by_key"],
        **{
            (entry.cell_id, entry.node_id): entry
            for entry in terminal_entries
        },
    }
    boundary_indexes["artifact_by_queue_id"] = {
        **base_indexes["artifact_by_queue_id"],
        **{
            entry.queue_entry_id: artifact
            for entry, artifact in zip(
                terminal_entries, terminal_artifacts, strict=True
            )
        },
    }
    boundary_indexes["budget_by_id"] = {
        **base_indexes["budget_by_id"],
        final_cell.budget_id: final_cell,
        final_global.budget_id: final_global,
    }
    boundary_indexes["queue_by_id"] = {
        **base_indexes["queue_by_id"],
        **{
            entry.queue_entry_id: entry
            for entry in terminal_entries
        },
    }
    env["child_result_boundary"] = {
        **child,
        "terminal_entries": tuple(terminal_entries),
        "terminal_artifacts": tuple(terminal_artifacts),
        "final_cell_budget": final_cell,
        "final_global_budget": final_global,
        "indexes": boundary_indexes,
    }
    assert all(item not in env["queue_log"] for item in terminal_entries)
    assert all(item not in env["artifact_log"] for item in terminal_artifacts)
    return env, slot, slot_artifact


_TEST_ONLY_EXTERNAL_D4_BOUNDARY = "TEST_ONLY_EXTERNAL_D4_BOUNDARY"
_TEST_ONLY_EXTERNAL_D4_NODE_KINDS = ("POST_VV", "GT_ADVISORY", "PARENT_RETURN")


def _d3_external_d4_structural_advance(
    env: dict[str, object],
    *,
    current: fr.FractalCellQueueEntryV02,
    current_artifact: KernelArtifactV01,
    node: fr.RuntimeTopologyNodeV02,
    cell_input: fr.FractalCellInputV02,
    decision: TransitionDecisionV01,
    cell_budget_before: fr.FractalRuntimeBudgetV02,
    global_budget_before: fr.FractalRuntimeBudgetV02,
    cell_budget_after: fr.FractalRuntimeBudgetV02,
    global_budget_after: fr.FractalRuntimeBudgetV02,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...] = (),
    observed_output_refs: tuple[str, ...] = (),
    observed_evidence_refs: tuple[str, ...] = (),
    advisory_refs: tuple[str, ...] = (),
) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]:
    assert node.node_kind in _TEST_ONLY_EXTERNAL_D4_NODE_KINDS
    assert node.node_kind not in fr._D3_LOCAL_NODE_KINDS_V02
    assert current.node_id == node.node_id
    assert current.cell_id == cell_input.cell_id
    assert all(item.state in fr._D3_TERMINAL_STATES_V02 for item in dependencies)
    budget_log = env["budget_log"]
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    reports = env["validation_reports"]
    assert isinstance(budget_log, tuple)
    assert isinstance(queue_log, tuple)
    assert isinstance(artifact_log, tuple)
    assert isinstance(reports, tuple)

    if (cell_budget_after, global_budget_after) != (
        cell_budget_before,
        global_budget_before,
    ):
        candidate_suffix = (
            (global_budget_after,)
            if cell_budget_after is global_budget_after
            else (cell_budget_after, global_budget_after)
        )
        assert all(item not in budget_log for item in candidate_suffix)
        budget_log += candidate_suffix
    env["budget_log"] = budget_log

    target = fr.advance_fractal_cell_queue_v02(
        source_context=env["source"],
        topology=env["topology"],
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
        round_start_queue_entries=_d3_latest(env),
        queue_reason_codes=queue_reason_codes,
        observed_output_refs=observed_output_refs,
        observed_evidence_refs=observed_evidence_refs,
        advisory_refs=advisory_refs,
        **_d3_prefix_kwargs(env),
    )
    artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
        target,
        topology_artifact=env["topology_artifact"],
        predecessor_artifact=current_artifact,
        activation_parent_artifact=None,
        local_child_result_artifact=None,
        source_context=env["source"],
        **_d3_prefix_kwargs(
            env,
            settled_queue_entry_log=queue_log + (target,),
            settled_validation_reports=reports,
        ),
    )
    env["queue_log"] = queue_log + (target,)
    env["artifact_log"] = artifact_log + (artifact,)
    env["validation_reports"] = _d3_retained_reports(
        env,
        env["queue_log"],
    )
    return target, artifact


def _d3_complete_external_d4_boundary_node(
    env: dict[str, object],
    *,
    node: fr.RuntimeTopologyNodeV02,
    initial: fr.FractalCellQueueEntryV02,
    initial_artifact: KernelArtifactV01,
    cell_input: fr.FractalCellInputV02,
) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]:
    assert node.node_kind in _TEST_ONLY_EXTERNAL_D4_NODE_KINDS
    indexes = _d3_indexes(env)
    dependencies = tuple(
        item
        for item in fr._d3_dependencies_for_latest_entry_v02(
            initial,
            topology=env["topology"],
            latest_by_key=indexes["latest_by_key"],
        )
        if item is not None
    )
    assert len(dependencies) == 1
    assert dependencies[0].state in fr._D3_TERMINAL_STATES_V02

    initial_cell = indexes["budget_by_id"][initial.cell_budget_id]
    initial_global = indexes["budget_by_id"][initial.global_budget_id]
    ready, ready_artifact = _d3_external_d4_structural_advance(
        env,
        current=initial,
        current_artifact=initial_artifact,
        node=node,
        cell_input=cell_input,
        decision=fr._d3_transition_decision_v02(env["registry"], "t04"),
        cell_budget_before=initial_cell,
        global_budget_before=initial_global,
        cell_budget_after=initial_cell,
        global_budget_after=initial_global,
        dependencies=dependencies,
    )

    indexes = _d3_indexes(env)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=ready.cell_id,
        indexes=indexes,
    )
    start_decision = fr._d3_transition_decision_v02(env["registry"], "t05")
    start_cell = _d3_budget_successor(
        env,
        live_cell,
        event="START_NODE",
        decision=start_decision,
        cell_input=cell_input,
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=ready.cell_id,
        scope=live_cell.budget_scope,
    )
    start_global = _d3_budget_successor(
        env,
        live_global,
        event="START_NODE",
        decision=start_decision,
        cell_input=cell_input,
        paired_cell_budget=start_cell,
    )
    ready_cell = indexes["budget_by_id"][ready.cell_budget_id]
    ready_global = indexes["budget_by_id"][ready.global_budget_id]
    running, running_artifact = _d3_external_d4_structural_advance(
        env,
        current=ready,
        current_artifact=ready_artifact,
        node=node,
        cell_input=cell_input,
        decision=start_decision,
        cell_budget_before=ready_cell,
        global_budget_before=ready_global,
        cell_budget_after=start_cell,
        global_budget_after=start_global,
        dependencies=dependencies,
    )

    indexes = _d3_indexes(env)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=running.cell_id,
        indexes=indexes,
    )
    finish_decision = fr._d3_transition_decision_v02(env["registry"], "t06")
    finish_cell = _d3_budget_successor(
        env,
        live_cell,
        event="FINISH_NODE",
        decision=finish_decision,
        cell_input=cell_input,
        allocation_parent=(
            None
            if live_cell.allocation_parent_budget_id is None
            else indexes["budget_by_id"][live_cell.allocation_parent_budget_id]
        ),
        owning_cell_id=running.cell_id,
        scope=live_cell.budget_scope,
    )
    finish_global = _d3_budget_successor(
        env,
        live_global,
        event="FINISH_NODE",
        decision=finish_decision,
        cell_input=cell_input,
        paired_cell_budget=finish_cell,
    )
    observation_suffix = f"{node.node_kind.lower()}:{initial.node_instance_sequence}"
    observed_outputs = (f"output:test-only-external-d4:{observation_suffix}",)
    observed_evidence = (f"evidence:test-only-external-d4:{observation_suffix}",)
    running_cell = indexes["budget_by_id"][running.cell_budget_id]
    running_global = indexes["budget_by_id"][running.global_budget_id]
    validating, validating_artifact = _d3_external_d4_structural_advance(
        env,
        current=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        decision=finish_decision,
        cell_budget_before=running_cell,
        global_budget_before=running_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        observed_output_refs=observed_outputs,
        observed_evidence_refs=observed_evidence,
    )

    terminal, terminal_artifact = _d3_external_d4_structural_advance(
        env,
        current=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        decision=fr._d3_transition_decision_v02(env["registry"], "t08"),
        cell_budget_before=finish_cell,
        global_budget_before=finish_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
    )
    assert terminal.state == "COMPLETED"
    return terminal, terminal_artifact


def _d3_child_result_runtime_environment(
    bundle: dict[str, object],
) -> tuple[
    dict[str, object],
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
]:
    base_env = bundle["env"]
    child = bundle["child"]
    assert isinstance(base_env, dict)
    assert isinstance(child, dict)
    env = _d3_clone_environment(base_env)
    slot = bundle["slot"]
    slot_artifact = bundle["slot_artifact"]
    local_terminal = bundle["terminal"]
    local_terminal_artifact = bundle["terminal_artifact"]
    child_input = bundle["child_input"]
    assert isinstance(slot, fr.FractalCellQueueEntryV02)
    assert isinstance(slot_artifact, KernelArtifactV01)
    assert isinstance(local_terminal, fr.FractalCellQueueEntryV02)
    assert isinstance(local_terminal_artifact, KernelArtifactV01)
    assert isinstance(child_input, fr.FractalCellInputV02)
    assert child["nodes"][0].node_kind == "SEMANTIC_ACTOR"
    external_nodes = child["nodes"][1:]
    external_initials = child["queues"][1:]
    external_initial_artifacts = child["artifacts"][1:]
    assert tuple(item.node_kind for item in external_nodes) == _TEST_ONLY_EXTERNAL_D4_NODE_KINDS

    terminal_entries: list[fr.FractalCellQueueEntryV02] = [local_terminal]
    terminal_artifacts: list[KernelArtifactV01] = [local_terminal_artifact]
    for node, initial, initial_artifact in zip(
        external_nodes,
        external_initials,
        external_initial_artifacts,
        strict=True,
    ):
        terminal, terminal_artifact = _d3_complete_external_d4_boundary_node(
            env,
            node=node,
            initial=initial,
            initial_artifact=initial_artifact,
            cell_input=child_input,
        )
        terminal_entries.append(terminal)
        terminal_artifacts.append(terminal_artifact)

    assert tuple(item.node_id for item in terminal_entries) == child_input.ordered_node_ids
    assert all(item.state == "COMPLETED" for item in terminal_entries)
    indexes = _d3_indexes(env)
    live_cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=child["cell_id"],
        indexes=indexes,
    )
    final_decision = fr._d3_transition_decision_v02(env["registry"], "t12")
    final_cell = _d3_budget_successor(
        env,
        live_cell,
        event="FINALIZE",
        decision=final_decision,
        cell_input=child_input,
        allocation_parent=env["root_create"],
        owning_cell_id=child["cell_id"],
        scope="CHILD_CELL_LOCAL",
        state="FINAL",
    )
    final_global = _d3_budget_successor(
        env,
        live_global,
        event="FINALIZE",
        decision=final_decision,
        cell_input=child_input,
        paired_cell_budget=final_cell,
    )
    env["budget_log"] = (*env["budget_log"], final_cell, final_global)
    strict_indexes = _d3_indexes(env)
    env["child_result_boundary"] = {
        **child,
        "boundary_kind": _TEST_ONLY_EXTERNAL_D4_BOUNDARY,
        "actual_d3_terminal_entry": local_terminal,
        "actual_d3_terminal_artifact": local_terminal_artifact,
        "external_tail_kinds": _TEST_ONLY_EXTERNAL_D4_NODE_KINDS,
        "terminal_entries": tuple(terminal_entries),
        "terminal_artifacts": tuple(terminal_artifacts),
        "final_cell_budget": final_cell,
        "final_global_budget": final_global,
        "indexes": strict_indexes,
    }
    return env, slot, slot_artifact

def _d3_complete_local_node(
    env: dict[str, object],
    *,
    node_index: int,
    dependencies: tuple[fr.FractalCellQueueEntryV02, ...] = (),
) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]:
    running, running_artifact, start = _d3_start_node(
        env,
        node_index=node_index,
        dependencies=dependencies,
    )
    node = env["nodes"][node_index]
    cell_input = env["cell_input"]
    material = fr._d3_local_observation_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        node=node,
        cell_input=cell_input,
        cell_budget_before=start,
        global_budget_before=start,
        dependencies=dependencies,
        indexes=_d3_indexes(env),
    )
    t06 = _d3_eval(
        env,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=cell_input,
        cell_budget=start,
        global_budget=start,
        dependencies=dependencies,
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    assert isinstance(t06, TransitionDecisionV01)
    finish = _d3_budget_successor(
        env,
        start,
        event="FINISH_NODE",
        decision=t06,
        cell_input=cell_input,
    )
    validating, validating_artifact, _ = _d3_advance(
        env,
        current=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=start,
        global_budget_before=start,
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=dependencies,
        round_entries=_d3_latest(env),
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    terminal, terminal_artifact, _ = _d3_advance(
        env,
        current=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=finish,
        global_budget_before=finish,
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=dependencies,
        round_entries=_d3_latest(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
    )
    return terminal, terminal_artifact


_D3_RESULT_PAYLOAD_FIELDS = (
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


def _d3_child_result_fixture(
    env: dict[str, object],
    *,
    outcome: str,
    ordinal: int,
) -> tuple[fr.FractalCellResultV02, KernelArtifactV01]:
    topology = env["topology"]
    source = env["source"]
    planned = env["planned"]
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    assert isinstance(planned, tuple) and planned
    boundary = env.get("child_result_boundary")
    suffixes = tuple(f"{ordinal * 16 + index + 1:064x}" for index in range(7))
    reasons_by_outcome = {
        "COMPLETED": (),
        "DEGRADED": ("g2d_partial_failure_recorded",),
        "BLOCKED": ("g2d_required_child_failure",),
        "NEEDS_USER": ("g2d_resolvable_input_needs_user",),
        "DEADEND": ("g2d_no_progress_deadend",),
    }
    cell_input_id = (
        boundary["input"].cell_input_id
        if isinstance(boundary, dict)
        else "frcellin_v02:" + suffixes[0]
    )
    terminal_queue_ids = (
        tuple(item.queue_entry_id for item in boundary["terminal_entries"])
        if isinstance(boundary, dict)
        else ("frqueue_v02:" + suffixes[1],)
    )
    allocated_budget_id = (
        boundary["allocated_budget"].budget_id
        if isinstance(boundary, dict)
        else "frbudget_v02:" + suffixes[2]
    )
    final_budget_id = (
        boundary["final_cell_budget"].budget_id
        if isinstance(boundary, dict)
        else "frbudget_v02:" + suffixes[3]
    )
    global_budget_id = (
        boundary["final_global_budget"].budget_id
        if isinstance(boundary, dict)
        else "frbudget_v02:" + suffixes[4]
    )
    validation_report_id = "frvalidation_v02:" + suffixes[5]
    post_vv_ref = f"vv:g2d3:child:{ordinal}"
    gt_ref = f"gt:g2d3:child:{ordinal}"
    result = _seal(fr.FractalCellResultV02(
        result_id="frcellresult_v02:" + "0" * 64,
        topology_id=topology.topology_id,
        topology_seed_id=topology.topology_seed_id,
        cell_id=boundary["cell_id"] if isinstance(boundary, dict) else planned[0],
        parent_cell_id=topology.root_cell_id,
        cell_depth=1,
        cell_input_id=cell_input_id,
        ordered_terminal_queue_entry_ids=terminal_queue_ids,
        ordered_child_result_ids=(),
        outcome=outcome,
        accepted_output_refs=(f"output:g2d3:child:{ordinal}",),
        evidence_refs=(f"evidence:g2d3:child:{ordinal}",),
        pre_result_validation_report_id=validation_report_id,
        post_vv_report_ref=post_vv_ref,
        gt_advisory_ref=gt_ref,
        partial_failure_ids=(),
        allocated_cell_budget_id=allocated_budget_id,
        final_cell_budget_id=final_budget_id,
        global_budget_id=global_budget_id,
        scope_ref=topology.accepted_scope_ref,
        reason_codes=reasons_by_outcome[outcome],
        source_reason_codes=(),
        trace_refs=(
            cell_input_id,
            *terminal_queue_ids,
            f"output:g2d3:child:{ordinal}",
            f"evidence:g2d3:child:{ordinal}",
            validation_report_id,
            allocated_budget_id,
            final_budget_id,
            global_budget_id,
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
    assert isinstance(result, fr.FractalCellResultV02)
    assert fr.validate_fractal_cell_result_v02(result).status == "PASS"
    payload = {
        name: list(getattr(result, name))
        if type(getattr(result, name)) is tuple
        else getattr(result, name)
        for name in _D3_RESULT_PAYLOAD_FIELDS
    }
    route_plain = kernel_artifact_to_plain_dict_v01(source.route_eligibility_artifact)
    provisional = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id="frabi_result_v02:" + "0" * 64,
        artifact_type="FractalCellResult",
        schema_version="v0.2",
        transaction_id=source.decision.transaction_id,
        owner_root_id=source.decision.owning_root_id,
        source_component="fractal_runtime_v02",
        authority_class="ADVISORY",
        lifecycle_state=("BLOCKED_FAIL_CLOSED" if outcome == "BLOCKED" else "VALIDATED"),
        payload=payload,
        trace_refs=(
            result.post_vv_report_ref,
            result.gt_advisory_ref,
            *result.trace_refs,
        ),
        parent_refs=(
            env["topology_artifact"].artifact_id,
            *(
                tuple(item.artifact_id for item in boundary["terminal_artifacts"])
                if isinstance(boundary, dict)
                else (env["queue_artifacts"][0].artifact_id,)
            ),
        ),
        time_envelope=route_plain["time_envelope"],
    )
    material = kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    artifact = replace(
        provisional,
        artifact_id=(
            "frabi_result_v02:"
            + domain_separated_sha256_hex_v01(
                domain="HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
                payload=canonical_json_bytes_v01(material),
            )
        ),
    )
    assert validate_kernel_artifact_v01(artifact) == ()
    return result, artifact


def _d3_reseal_result_artifact(
    artifact: KernelArtifactV01,
    **changes: object,
) -> KernelArtifactV01:
    material = kernel_artifact_to_plain_dict_v01(artifact)
    for name, value in changes.items():
        material[name] = list(value) if type(value) is tuple else value
    material.pop("artifact_id")
    new_id = (
        "frabi_result_v02:"
        + domain_separated_sha256_hex_v01(
            domain="HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
            payload=canonical_json_bytes_v01(material),
        )
    )
    return replace(
        artifact,
        artifact_id=new_id,
        **changes,
    )


def _d3_terminal_dependency_fixture(
    env: dict[str, object],
) -> fr.FractalCellQueueEntryV02:
    queues = env["queues"]
    topology = env["topology"]
    root_create = env["root_create"]
    assert isinstance(queues, tuple)
    decision = fr._d3_transition_decision_v02(env["registry"], "t08")
    predecessor_id = "frqueue_v02:" + "e" * 64
    result = _seal(replace(
        queues[0],
        state="COMPLETED",
        prior_state="VALIDATING",
        predecessor_queue_entry_id=predecessor_id,
        predecessor_relation="EXACT_IMMEDIATE_PREDECESSOR",
        transition_decision_id=decision.decision_id,
        snapshot_sequence=4,
        admission_round=4,
        lineage_refs=(
            topology.topology_id,
            topology.topology_seed_id,
            topology.root_cell_id,
            queues[0].node_id,
            root_create.budget_id,
            root_create.budget_id,
            predecessor_id,
        ),
    ))
    assert isinstance(result, fr.FractalCellQueueEntryV02)
    assert fr.validate_fractal_cell_queue_entry_v02(result).status == "PASS"
    return result


def test_d3_exact_public_surface_and_preserved_geometry() -> None:
    expected_signatures = {
        "admit_runtime_execution_topology_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', topology_artifact: 'KernelArtifactV01', topology_transition_decision: 'TransitionDecisionV01', cell_id: 'str', parent_cell_id: 'str | None', parent_slot_artifact: 'KernelArtifactV01 | None', cell_depth: 'int', scope_ref: 'str', cell_budget: 'FractalRuntimeBudgetV02', global_budget: 'FractalRuntimeBudgetV02', projected_nodes: 'tuple[RuntimeTopologyNodeV02, ...]', planned_child_cell_ids: 'tuple[str, ...]', admission_decisions: 'tuple[TransitionDecisionV01, ...]', cell_instantiation_order: 'tuple[str, ...]') -> 'tuple[FractalCellQueueEntryV02, ...]'",
        "advance_fractal_cell_queue_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', current_entry: 'FractalCellQueueEntryV02', node: 'RuntimeTopologyNodeV02', cell_input: 'FractalCellInputV02', transition_decision: 'TransitionDecisionV01', cell_budget_after: 'FractalRuntimeBudgetV02', global_budget_after: 'FractalRuntimeBudgetV02', dependencies: 'tuple[FractalCellQueueEntryV02, ...]', local_child_result: 'FractalCellResultV02 | None', local_child_result_artifact: 'KernelArtifactV01 | None', cell_instantiation_order: 'tuple[str, ...]', projected_node_ids: 'tuple[str, ...]', round_start_queue_entries: 'tuple[FractalCellQueueEntryV02, ...]', queue_reason_codes: 'tuple[str, ...]', observed_output_refs: 'tuple[str, ...]', observed_evidence_refs: 'tuple[str, ...]', advisory_refs: 'tuple[str, ...]') -> 'FractalCellQueueEntryV02'",
        "project_parent_child_scope_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', parent_input: 'FractalCellInputV02', child_cell_id: 'str', child_scope_ref: 'str', parent_budget: 'FractalRuntimeBudgetV02', child_budget: 'FractalRuntimeBudgetV02', global_budget: 'FractalRuntimeBudgetV02') -> 'ParentChildScopeProjectionV02'",
        "validate_parent_child_scope_against_sources_v02": "(value: 'object', *, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', parent_input: 'FractalCellInputV02', parent_budget: 'FractalRuntimeBudgetV02', child_budget: 'FractalRuntimeBudgetV02', global_budget: 'FractalRuntimeBudgetV02') -> 'FractalRuntimeValidationReportV02'",
        "build_fractal_cell_input_from_queue_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', topology_artifact: 'KernelArtifactV01', cell_id: 'str', parent_cell_id: 'str | None', parent_input: 'FractalCellInputV02 | None', parent_slot_artifact: 'KernelArtifactV01 | None', scope_projection: 'ParentChildScopeProjectionV02 | None', cell_budget: 'FractalRuntimeBudgetV02', global_budget: 'FractalRuntimeBudgetV02', initial_queue_entries: 'tuple[FractalCellQueueEntryV02, ...]', initial_queue_artifacts: 'tuple[KernelArtifactV01, ...]', ordered_planned_child_cell_ids: 'tuple[str, ...]') -> 'FractalCellInputV02'",
        "validate_fractal_cell_input_against_sources_v02": "(value: 'object', *, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', topology_artifact: 'KernelArtifactV01', parent_input: 'FractalCellInputV02 | None', parent_slot_artifact: 'KernelArtifactV01 | None', scope_projection: 'ParentChildScopeProjectionV02 | None', cell_budget: 'FractalRuntimeBudgetV02', global_budget: 'FractalRuntimeBudgetV02', queue_entries: 'tuple[FractalCellQueueEntryV02, ...]', queue_artifacts: 'tuple[KernelArtifactV01, ...]') -> 'FractalRuntimeValidationReportV02'",
        "evaluate_fractal_backpressure_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', policy: 'FractalRuntimePolicyV02', global_budget: 'FractalRuntimeBudgetV02', queue_entries: 'tuple[FractalCellQueueEntryV02, ...]', admission_round: 'int') -> 'FractalBackpressureStateV02 | None'",
        "project_fractal_cell_queue_entry_kernel_artifact_v02": "(queue_entry: 'FractalCellQueueEntryV02', *, topology_artifact: 'KernelArtifactV01', predecessor_artifact: 'KernelArtifactV01 | None', activation_parent_artifact: 'KernelArtifactV01 | None', local_child_result_artifact: 'KernelArtifactV01 | None', source_context: 'FractalRuntimeSourceContextV02') -> 'KernelArtifactV01'",
        "evaluate_fractal_runtime_state_transition_v02": "(*, source_context: 'FractalRuntimeSourceContextV02', topology: 'RuntimeExecutionTopologyV02', source_artifact: 'KernelArtifactV01', current_entry: 'FractalCellQueueEntryV02 | None', node: 'RuntimeTopologyNodeV02', cell_input: 'FractalCellInputV02 | None', cell_id: 'str', parent_cell_id: 'str | None', planned_child_cell_id: 'str | None', cell_depth: 'int', scope_ref: 'str', cell_budget_before: 'FractalRuntimeBudgetV02', global_budget_before: 'FractalRuntimeBudgetV02', dependencies: 'tuple[FractalCellQueueEntryV02, ...]', queue_reason_codes: 'tuple[str, ...]', observed_output_refs: 'tuple[str, ...]', observed_evidence_refs: 'tuple[str, ...]', advisory_refs: 'tuple[str, ...]', local_child_result: 'FractalCellResultV02 | None', local_child_result_artifact: 'KernelArtifactV01 | None', validation_report: 'FractalRuntimeValidationReportV02 | None', parent_return_pre_post_vv_terminal_queue_entries: 'tuple[FractalCellQueueEntryV02, ...]', parent_return_child_results: 'tuple[FractalCellResultV02, ...]', parent_return_partial_failures: 'tuple[FractalPartialFailureRecordV02, ...]', parent_return_result_proposal: 'dict[str, object] | None', parent_return_post_vv_report: 'dict[str, object] | None', parent_return_gt_advisory_report: 'dict[str, object] | None', parent_return_validation_reports: 'tuple[FractalRuntimeValidationReportV02, ...]', revise_observation: 'FractalReviseObservationV02 | None', backpressure_state: 'FractalBackpressureStateV02 | None', transition_registry: 'TransitionRegistryV01') -> 'TransitionDecisionV01 | None'",
    }
    settled_suffix = ", settled_budget_log: 'tuple[FractalRuntimeBudgetV02, ...]', settled_queue_entry_log: 'tuple[FractalCellQueueEntryV02, ...]', settled_queue_artifact_log: 'tuple[KernelArtifactV01, ...]', settled_cell_inputs: 'tuple[FractalCellInputV02, ...]', settled_scope_projections: 'tuple[ParentChildScopeProjectionV02, ...]', settled_revise_observations: 'tuple[FractalReviseObservationV02, ...]', settled_backpressure_states: 'tuple[FractalBackpressureStateV02, ...]', settled_validation_reports: 'tuple[FractalRuntimeValidationReportV02, ...]'"
    amended = {
        "admit_runtime_execution_topology_v02",
        "advance_fractal_cell_queue_v02",
        "build_fractal_cell_input_from_queue_v02",
        "validate_fractal_cell_input_against_sources_v02",
        "evaluate_fractal_backpressure_v02",
        "project_fractal_cell_queue_entry_kernel_artifact_v02",
        "evaluate_fractal_runtime_state_transition_v02",
    }
    for name in amended:
        expected_signatures[name] = expected_signatures[name].replace(
            ") -> ",
            settled_suffix
            + ", observed_work_context: 'RuntimeObservedWorkContextV02 | None' = None) -> ",
        )
    for name, signature in expected_signatures.items():
        assert str(inspect.signature(getattr(fr, name))) == signature
    public_functions = tuple(
        name
        for name, value in vars(fr).items()
        if inspect.isfunction(value) and value.__module__ == fr.__name__ and not name.startswith("_")
    )
    assert len(public_functions) == 116
    assert len(fr.G2D_TYPES_V02) == 21
    assert len(fr.SERIALIZED_G2D_TYPES_V02) == 18
    assert len(fr.RUNTIME_ONLY_G2D_TYPES_V02) == 3
    assert len(fr.PUBLIC_G2D_REASON_CODES) == 220
    assert len(fr.VALIDATION_TARGETS) == 35
    assert fr.VALIDATION_TARGETS[-1] == (
        "OBSERVED_WORK_BINDINGS_AGAINST_SOURCES"
    )
    assert len(fr.FAILURE_STAGES) == 30
    for activated in (
        "build_fractal_runtime_execution_bundle_v02",
        "build_fractal_cell_result_proposal_v02",
        "run_fractal_runtime_v02",
    ):
        assert callable(getattr(fr, activated, None))


def _d3_reseal_profile_d_queue_entry_v036(
    entry: fr.FractalCellQueueEntryV02,
    **changes: object,
) -> fr.FractalCellQueueEntryV02:
    candidate = replace(entry, **changes)
    assert candidate.parent_cell_id is not None
    assert candidate.predecessor_queue_entry_id is not None
    lineage_refs = (
        candidate.topology_id,
        candidate.topology_seed_id,
        candidate.cell_id,
        candidate.parent_cell_id,
        candidate.node_id,
        candidate.cell_budget_id,
        candidate.global_budget_id,
        candidate.lineage_refs[7],
        candidate.predecessor_queue_entry_id,
        *candidate.observed_output_refs,
        *candidate.observed_evidence_refs,
        *candidate.advisory_refs,
    )
    result = _seal(replace(candidate, lineage_refs=lineage_refs))
    assert isinstance(result, fr.FractalCellQueueEntryV02)
    return result


@pytest.fixture(scope="module")
def d3_profile_d_contextual_micro_bundle(
    d3_full_fractal_micro_environment: dict[str, object],
) -> dict[str, object]:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    dependency, dependency_artifact = _d3_complete_local_node(env, node_index=0)
    slot, slot_artifact, _slot_start = _d3_start_node(
        env,
        node_index=1,
        dependencies=(dependency,),
    )
    child = _d3_activate_child(
        env,
        slot_running=slot,
        slot_artifact=slot_artifact,
        dependency=dependency,
    )
    node = child["nodes"][0]
    initial = child["queues"][0]
    initial_artifact = child["artifacts"][0]
    child_input = child["input"]
    assert isinstance(node, fr.RuntimeTopologyNodeV02)
    assert isinstance(initial, fr.FractalCellQueueEntryV02)
    assert isinstance(initial_artifact, KernelArtifactV01)
    assert isinstance(child_input, fr.FractalCellInputV02)
    assert node.node_kind == "SEMANTIC_ACTOR"
    assert node.node_kind in fr._D3_LOCAL_NODE_KINDS_V02
    assert tuple(item.node_kind for item in child["nodes"][1:]) == (
        "POST_VV",
        "GT_ADVISORY",
        "PARENT_RETURN",
    )

    initial_indexes = _d3_indexes(env)
    dependencies = tuple(
        item
        for item in fr._d3_dependencies_for_latest_entry_v02(
            initial,
            topology=env["topology"],
            latest_by_key=initial_indexes["latest_by_key"],
        )
        if item is not None
    )
    assert dependencies == ()
    ready, ready_artifact = _d3_make_ready(
        env,
        current=initial,
        node=node,
        cell_input=child_input,
        dependencies=dependencies,
    )
    running, running_artifact, start_cell, start_global = _d3_start_ready_entry(
        env,
        ready=ready,
        ready_artifact=ready_artifact,
        node=node,
        cell_input=child_input,
        dependencies=dependencies,
    )
    pre_t06_indexes = _d3_indexes(env)
    validating, validating_artifact, _finish_global = _d3_finish_running_local(
        env,
        running=running,
        running_artifact=running_artifact,
        node=node,
        cell_input=child_input,
        dependencies=dependencies,
    )
    t06_indexes = _d3_indexes(env)
    finish_cell = t06_indexes["budget_by_id"][validating.cell_budget_id]
    finish_global = t06_indexes["budget_by_id"][validating.global_budget_id]
    terminal, terminal_artifact, terminal_decision = _d3_advance(
        env,
        current=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=child_input,
        cell_budget_before=finish_cell,
        global_budget_before=finish_global,
        cell_budget_after=finish_cell,
        global_budget_after=finish_global,
        dependencies=dependencies,
        round_entries=_d3_latest(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
    )
    assert terminal.state == "COMPLETED"
    assert terminal_decision == fr._d3_transition_decision_v02(
        env["registry"],
        "t08",
    )
    final_indexes = _d3_indexes(env)
    activation_parent_id = initial_artifact.parent_refs[1]
    assert activation_parent_id == slot_artifact.artifact_id
    return {
        "env": env,
        "dependency": dependency,
        "dependency_artifact": dependency_artifact,
        "slot": slot,
        "slot_artifact": slot_artifact,
        "child": child,
        "child_input": child_input,
        "initial": initial,
        "initial_artifact": initial_artifact,
        "node": node,
        "dependencies": dependencies,
        "ready": ready,
        "ready_artifact": ready_artifact,
        "running": running,
        "running_artifact": running_artifact,
        "start_cell": start_cell,
        "start_global": start_global,
        "pre_t06_indexes": pre_t06_indexes,
        "validating": validating,
        "validating_artifact": validating_artifact,
        "t06_indexes": t06_indexes,
        "terminal": terminal,
        "terminal_artifact": terminal_artifact,
        "terminal_decision": terminal_decision,
        "activation_parent_id": activation_parent_id,
        "final_indexes": final_indexes,
    }


def test_d3_post_acceptance_contract_addendum_v039_accepted() -> None:
    raw = ADDENDUM_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445'
    assert len(raw) == 212148
    assert raw.count(b"\n") == 4185
    v039_separator = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.8 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted v0.3.8 addendum.\n"
        b"It remains immutable historical contract and evidence context for v0.3.8. Its\n"
        b"embedded present-tense lifecycle statements do not override the active v0.3.9\n"
        b"metadata and clarification above.\n"
        b"\n"
    )
    assert raw.count(v039_separator) == 1
    active_v039, historical_v038 = raw.split(v039_separator, 1)
    assert hashlib.sha256(historical_v038).hexdigest() == (
        "09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6"
    )
    assert len(historical_v038) == 197537
    assert historical_v038.count(b"\n") == 3828
    assert raw.count(historical_v038) == 1
    active_text_v039 = active_v039.decode("ascii")
    required_rows_v039 = (
        "document_revision: v0.3.9",
        "guardian_review_status: ACCEPTED_WITH_MANDATORY_OVERLAY",
        "guardian_ruling: APPROVE_WITH_MANDATORY_OVERLAY",
        "accepted_v038_basis_sha256: 09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6",
        "repository_basis_head: 4cf427f82a096383ae5873024787c19e56ac0fb5",
        "V038_IMPLEMENTATION_NONCONFORMANCE: YES",
        "V039_CONTRACT_SEMANTICS_CHANGED: NO",
        "V039_ROLE: EXPLICIT_IMPLEMENTATION_NONCONFORMANCE_CLARIFICATION_AND_LIFECYCLE_REOPENING",
        "implementation_authorized: false",
        "implementation_started: false",
        "isolated_worktree_strategy_approved: true",
        "e4_two_path_only_implementation_sufficient: false",
        "e4_public_end_to_end_carrier_overlay_required: true",
        "revised_guardian_decision_required: false",
        "current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING",
        "historical_v038_g2d_status: CLOSED_PASS_ON_V038_BYTES",
        "current_g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D",
        "post_v039_implementation_g2e3_status: REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "current_g2e4_anti_gaming_acceptance: BLOCKED_PENDING_G2D_V039_RECLOSURE",
        "E4_PAIR_CALL_ACCOUNTING=2/2",
        "E4_FOCUSED_CALL_ACCOUNTING=2/2",
        "E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3",
        "GATE2_STATUS=NOT_CLOSED",
    )
    assert all(row in active_text_v039 for row in required_rows_v039)
    for row in (
        "evaluate_fractal_revise_observation_v02",
        "evaluate_fractal_runtime_state_transition_v02",
        "g2d_t12_validating_to_deadend",
        "advance_fractal_cell_queue_v02",
        "rule_id = g2d_t12_validating_to_deadend",
        "decision = RETURN_TO_ROOT",
        "reason_code = g2d_transition_deadend_recorded",
        "revise.reason_codes = (\"g2d_no_progress_deadend\",)",
        "run_continuous_delta_runtime_v01",
        "execute_selective_recomputation_v01",
        "bundle = None",
        "report.status = FAIL_CLOSED",
    ):
        assert row in active_text_v039
    contract_paths = (
        "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md",
        "tests/test_fractal_runtime_g2_d_v02.py",
        "AGENTS.md",
        "README.md",
        "specs/machine_manifest_v0_25.json",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "tests/test_repository_release_spine_v01.py",
    )
    contract_scope = active_text_v039.split(
        "This contract-only candidate modifies exactly these ten", 1
    )[1].split("The active contract-only lifecycle is exact:", 1)[0]
    offsets = tuple(contract_scope.index("`" + path + "`") for path in contract_paths)
    assert offsets == tuple(sorted(offsets))
    future_paths = (
        "hedgehog/kernel/fractal_runtime_v02.py",
        "tests/test_fractal_runtime_g2_d_v02.py",
    )
    future_scope = active_text_v039.split(
        "A later separately owner-authorized implementation may modify exactly:", 1
    )[1].split("No schema, Transition Registry", 1)[0]
    assert tuple(
        path for path in future_paths if "`" + path + "`" in future_scope
    ) == future_paths
    operational = active_text_v039.split(
        "The complete operational order is frozen:", 1
    )[1].split("The forbidden order is", 1)[0]
    assert operational.index("one fresh unchanged logical G2-E3 V06") < operational.index(
        "guarded fast-forward of the original dirty primary"
    )
    assert "This contract-only hop authorizes no implementation." in active_text_v039
    assert "Root remains the only final authority." in active_text_v039

    raw = historical_v038
    assert hashlib.sha256(raw).hexdigest() == (
        "09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6"
    )
    assert len(raw) == 197537
    assert raw.count(b"\n") == 3828
    v038_separator = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.7 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted v0.3.7 addendum.\n"
        b"It remains immutable historical contract and evidence context for v0.3.7. Its\n"
        b"embedded present-tense lifecycle statements do not override the active v0.3.8\n"
        b"metadata and clarification above.\n"
        b"\n"
    )
    assert raw.count(v038_separator) == 1
    active_v038, historical_v037 = raw.split(v038_separator, 1)
    assert hashlib.sha256(historical_v037).hexdigest() == (
        "29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511"
    )
    assert len(historical_v037) == 185220
    assert historical_v037.count(b"\n") == 3532
    assert raw.count(historical_v037) == 1
    active_text = active_v038.decode("utf-8")
    active_rows = (
        "document_status: POST_ACCEPTANCE_CORRECTION_ADDENDUM",
        "document_revision: v0.3.8",
        "guardian_review_status: ACCEPTED",
        "directional_draft_sha256: "
        "91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454",
        "directional_draft_review: APPROVE_WITH_MANDATORY_OVERLAY",
        "mandatory_overlay_integrated: true",
        "controlling_design_v03_sha256: "
        "7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe",
        "repository_basis_head: 0a741d20ebe9092685a1e1117da01438499168e5",
        "repository_basis_origin_main: "
        "0a741d20ebe9092685a1e1117da01438499168e5",
        "repository_basis_subject: Correct G2-E4 strict selective subtree execution",
        "V037_IMPLEMENTATION_NONCONFORMANCE: YES",
        "V038_CONTRACT_SEMANTICS_CHANGED: NO",
        "V038_ROLE: EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING",
        "current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING",
        "implementation_authorized: false",
        "implementation_started: false",
        "current_g2e3_status: "
        "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D",
        "current_g2e4_status: "
        "IMPLEMENTED_COMMITTED_STRICT_SUBTREE_PASS_ANTI_GAMING_ACCEPTANCE_BLOCKED",
        "g2e5_status: NOT_STARTED_NOT_AUTHORIZED",
        "g2e6_status: NOT_STARTED_NOT_AUTHORIZED",
        "g2f_status: NOT_STARTED_NOT_AUTHORIZED",
        "gate2_status: NOT_CLOSED",
    )
    assert all(row in active_text for row in active_rows)
    triad_rows = (
        "execution_scope = SELECTIVE",
        "execution_scope = WHOLE_RUN_ESCALATION",
        "whole_run_escalation_reason = None",
        "whole_run_escalation_reason = "
        "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK",
        "whole_run_escalation_reason = "
        "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
        "whole_run_escalation_policy_id = None",
        "whole_run_escalation_policy_id = an explicitly accepted policy ID",
        "The accepted named-policy inventory is empty in v0.3.8.",
    )
    assert all(row in active_text for row in triad_rows)
    negative_rows = (
        "named-policy reason plus any nonempty but unapproved policy ID",
        "arbitrary or substituted reason",
        "arbitrary or substituted policy",
        "empty, whitespace, sentinel, or foreign policy ID",
        "forged closure",
        "missing closure member",
        "foreign node, cell, or artifact in the closure",
        "strict subset with WHOLE_RUN_ESCALATION",
        "full closure with SELECTIVE",
        "proof reason plus non-null policy",
        "named-policy reason plus null policy",
        "binding or context identity substitution",
        "a full ID inventory unsupported by actual source and binding evidence",
    )
    assert all(row in active_text for row in negative_rows)
    implementation_paths = (
        "hedgehog/kernel/fractal_runtime_v02.py",
        "tests/test_fractal_runtime_g2_d_v02.py",
        "AGENTS.md",
        "README.md",
        "specs/machine_manifest_v0_25.json",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "tests/test_repository_release_spine_v01.py",
    )
    path_offsets = [active_text.index(f"`{path}`") for path in implementation_paths]
    assert path_offsets == sorted(path_offsets)
    lifecycle_rows = (
        "G2-D = REAUDIT_PENDING",
        "G2-D corrected closure claimed = false",
        "G2-D independent re-audit passed = false",
        "G2-E3 = REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "G2-E4 anti-gaming acceptance = BLOCKED_PENDING_G2D_RECLOSURE",
        "G2D_IMPLEMENTATION_AUTHORIZED=false",
        "G2D_IMPLEMENTATION_STARTED=false",
        "G2E5_STATUS=NOT_STARTED_NOT_AUTHORIZED",
        "G2E6_STATUS=NOT_STARTED_NOT_AUTHORIZED",
        "G2F_STATUS=NOT_STARTED_NOT_AUTHORIZED",
        "GATE2_STATUS=NOT_CLOSED",
    )
    assert all(row in active_text for row in lifecycle_rows)
    execution_scope = active_text.split(
        "The complete execution order is frozen:",
        1,
    )[1].split("No reset, revert, amend, rebase, squash, or force-push", 1)[0]
    execution_steps = tuple(
        " ".join(match.group(1).split()).rstrip(";.")
        for match in re.finditer(
            r"(?ms)^\d+\. (.*?)(?=^\d+\. |\Z)",
            execution_scope,
        )
    )
    assert execution_steps == (
        "v0.3.8 clarification and lifecycle-reopening contract hop",
        "owner contract review and separate contract commit and push",
        "separately authorized G2-D implementation correction",
        "complete bounded and cumulative evidence",
        "implementation commit with REAUDIT_PENDING status",
        "independent read-only re-audit on committed v0.3.8 bytes",
        "additive successor checkpoint, reclosure, and release synchronization",
        "corrected G2-D returns to CLOSED_PASS",
        "one fresh unchanged G2-E3 V06",
        "real G2-E4 whole-run anti-gaming correction",
        "real G2-E4 revise, exact-repeat/no-progress, partial-failure, and "
        "backpressure correction",
        "final separate G2-E4 corrective commit",
        "only then may G2-E5 be considered",
    )
    assert "No new public dataclass, serialized type, schema definition" in active_text
    assert "Root remains the only final authority." in active_text
    assert "G2-D imports no G2-E type or module." in active_text
    assert "This contract-only hop authorizes no implementation." in active_text

    text = historical_v037.decode("utf-8")
    separator = (
        b"\n===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.6 CONTENT - EXACT PRE-CORRECTION REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The following byte sequence is retained verbatim as immutable historical\n"
        b"accepted content. Its embedded present-tense lifecycle statements are historical\n"
        b"to v0.3.6 and do not override the active v0.3.7 metadata above.\n"
        b"\n"
    )
    assert raw.count(separator) == 1
    _, historical_v036 = raw.split(separator, 1)
    assert hashlib.sha256(historical_v036).hexdigest() == (
        "7e3a9039e04a7ef2b20cd69ac442ad62c073e88d7d3b93c26f35b48b18d67570"
    )
    assert len(historical_v036) == 133145
    assert historical_v036.count(b"\n") == 2212
    current_rows = (
        "document_revision: v0.3.7",
        "guardian_review_status: ACCEPTED",
        "guardian_accepted_v037_pending_draft_sha256: "
        "8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d",
        "current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING",
        "current_g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_PRECORRECTION_G2D",
        "g2e4_status: NOT_STARTED_NOT_AUTHORIZED",
        "gate2_status: NOT_CLOSED",
        "implementation_authorized: false",
        "G2D_V037_GUARDIAN_REVIEW_STATUS=ACCEPTED",
        "G2D_V037_ACCEPTED=true",
        "G2D_V037_IMPLEMENTATION_AUTHORIZED=false",
        "G2D_V037_CURRENT_G2D_STATUS=CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING",
        "G2D_V037_CURRENT_G2E3_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_PRECORRECTION_G2D",
        "G2D_V037_G2E4_STATUS=NOT_STARTED_NOT_AUTHORIZED",
        "G2D_V037_GATE2_STATUS=NOT_CLOSED",
        "G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_PREFIX=frcounterfactual_v02:",
        "G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_DOMAIN="
        "HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_COUNTERFACTUAL",
        "G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_MATERIAL_FROZEN=true",
    )
    assert all(row in text for row in current_rows)
    required_rows = (
        "document_revision: v0.3.6",
        "guardian_review_status: ACCEPTED",
        "G2D3_V036_CONTRACT_DRAFT=false",
        "G2D3_V036_CONTRACT_ACCEPTED=true",
        "G2D3_V036_GUARDIAN_REVIEW_STATUS=ACCEPTED",
        "G2D3_ADDENDUM_GUARDIAN_STATUS=ACCEPTED",
        "G2D3_V035_REMAINS_HISTORICAL_ACCEPTED=true",
        "PROFILE_D_DRAFTED=true",
        "PROFILE_D_ACCEPTED=true",
        "PROFILE_D_IMPLEMENTATION_CANDIDATE_PRESENT=true",
        "PROFILE_D_IMPLEMENTATION_PROVEN=true",
        "PROFILE_D_INTEGRATION_SENTINEL_PASS=true",
        "ACTIVE_G2D3_QUEUE_ROLE_ALIAS_PROFILE_COUNT=3",
        "PRIVATE_CANONICAL_MATERIAL_PROFILE_COUNT=3",
        "FUTURE_DOCUMENTED_ROLE_ALIAS_PROFILE_COUNT=1",
        "CURRENT_RUNTIME_REFERENCE_MAX_PARALLELISM=3",
        "CURRENT_SCHEMA_REFERENCE_MAX_PARALLELISM=3",
        "G2D3_IMPLEMENTATION_AUTHORIZED=true",
        "G2D3_IMPLEMENTATION_RESUMED=true",
        "G2D3_IMPLEMENTATION_COMPLETED=true",
        "G2D3_IMPLEMENTATION_COMMITTED=false",
        "G2D3_FINAL_COMPLETE_DFILE_EXECUTED=true",
        "G2D3_FINAL_COMPLETE_DFILE_COLLECTION=57",
        "G2D3_FINAL_COMPLETE_DFILE_PASSED=57",
        "G2D3_FINAL_COMPLETE_DFILE_FAILED=0",
        "G2D3_FINAL_COMPLETE_DFILE_SKIPPED=0",
        "G2D3_FINAL_COMPLETE_DFILE_XFAIL=0",
        "G2D3_FINAL_COMPLETE_DFILE_DURATION_SECONDS=19385.32",
        "G2D3_FINAL_COMPLETE_DFILE_REPORTED_DURATION=5:23:05",
        "G2D3_FINAL_COMPLETE_DFILE_WRAPPER_ELAPSED=5:23:06",
        "G2D3_FINAL_COMPLETE_DFILE_EXIT_CODE=0",
        "G2D3_FINAL_COMPLETE_DFILE_RUN_RESULT=G2D3_FINAL_COMPLETE_DFILE_PASS",
        "G2D3_FINAL_COMPLETE_DFILE_REPOSITORY_GUARD=PASS",
        "G2D3_FINAL_COMPLETE_DFILE_LOG_SHA256="
        "17003824f527e8ca1adbf9e256ca61d9cbc085939fe0badb02ec3535f0c90628",
        "G2D3_FINAL_COMPLETE_DFILE_LOG_BYTES=47840",
        "G2D3_FINAL_COMPLETE_DFILE_LOG_LF_LINES=575",
        "G2D3_ACCEPTED_RUNTIME_SHA256="
        "dcfee5bef674c8b90e875e04fa64312df3db021bafdd0c6e476f2bb01fe4a386",
        "G2D3_ACCEPTED_SCHEMA_SHA256="
        "e62f693cc24a0562ca2955b011530916a85598dd00026f6dbadb80b6b9eb94ac",
        "G2D3_ACCEPTED_PREFLIGHT_SHA256="
        "8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79",
        "G2D3_PRE_ACCEPTANCE_TEST_SHA256="
        "ae7d3e5438ff51c1269b2c11c6b9e28beb85792d644847f25230a12b789058b1",
        "RUNTIME_CHANGED=true",
        "TESTS_CHANGED=true",
        "TESTS_EXECUTED=true",
        "PYTHON_EXECUTED=true",
        "READY_FOR_OWNER_GUARDIAN_REVIEW=true",
        "READY_FOR_OWNER_COMMIT_REVIEW=true",
        "G2D4_IMPLEMENTATION_AUTHORIZED=false",
        "G2D4_STARTED=false",
        "G2E_STARTED=false",
        "G2F_STARTED=false",
        "G2D_CLOSED=false",
        "GATE2_CLOSED=false",
        "STAGING_CHANGED=false",
        "COMMIT_CREATED=false",
        "PUSH_PERFORMED=false",
        "PROVIDER_CALLS=0",
        "MODEL_CALLS=0",
        "NETWORK_CALLS=0",
        "CONNECTOR_CALLS=0",
        "EXTERNAL_DRS_CALLS=0",
        "AUTHORITY_CREATED_COUNT=0",
        "REAL_WORLD_EFFECTS_COUNT=0",
        "PUBLIC_RELEASE_CLAIMED=false",
    )
    assert all(row in text for row in required_rows)
    normalized = " ".join(text.split())
    assert (
        "v0.3.6 is the controlling accepted addendum only for Profile D "
        "`CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS`, the "
        "accepted active queue-role-alias count of three, its identity-impact "
        "register, its proof ledger, and its final closing flags."
        in normalized
    )
    assert (
        "Accepted v0.3.5 remains historical accepted authority for CTC-01, "
        "CTC-02, CTC-03, and every unaffected ruling."
        in normalized
    )
    assert "## 4A. Accepted Active Profile D:" in text
    for row in (
        "PENDING_REVIEW",
        "POST_ACCEPTANCE_CORRECTION_ADDENDUM_DRAFT",
        "draft_is_accepted_contract: false",
        "external_draft_only: true",
        "G2D_V037_ACCEPTED=false",
        "G2D_V037_READY_FOR_GUARDIAN_REVIEW=true",
        "Pending v0.3.6",
        "pending narrow Profile D",
        "pending Profile D",
        "proposed active",
        "V036_PROPOSED_ACTIVE_G2D3_QUEUE_ROLE_ALIAS_PROFILE_COUNT",
        "G2D3_V035_REMAINS_CONTROLLING_ACCEPTED",
    ):
        assert row not in text
    assert text.count("ACTIVE_G2D3_QUEUE_ROLE_ALIAS_PROFILE_COUNT=3") == 1
    assert text.count("V036_NEW_PUBLIC_PARAMETER_COUNT=0") == 1
    machine_keys = re.findall(r"(?m)^([A-Z][A-Z0-9_]+)=", text)
    assert len(machine_keys) == len(set(machine_keys))
    assert "g2d3_implementation_authorized: true" in text
    assert "g2d3_implementation_resumed: true" in text
    assert "g2d3_implementation_completed: true" in text
    assert "g2d4_implementation_authorized: false" in text
    assert "gate2_closed: false" in text


def test_d3_profile_d_raw_path_rejects_context_free_alias_micro(
    d3_profile_d_contextual_micro_bundle: dict[str, object],
) -> None:
    bundle = d3_profile_d_contextual_micro_bundle
    env = bundle["env"]
    assert isinstance(env, dict)
    for entry, artifact in (
        (bundle["validating"], bundle["validating_artifact"]),
        (bundle["terminal"], bundle["terminal_artifact"]),
    ):
        assert isinstance(entry, fr.FractalCellQueueEntryV02)
        assert isinstance(artifact, KernelArtifactV01)
        assert entry.lineage_refs.count(bundle["activation_parent_id"]) == 2
        with pytest.raises(ValueError, match="g2d_queue_artifact_lineage_invalid"):
            fr._d3_queue_artifact_trace_refs_v02(
                entry,
                parent_refs=artifact.parent_refs,
            )
        with pytest.raises(ValueError, match="g2d_queue_artifact_lineage_invalid"):
            fr._d3_build_queue_artifact_v02(
                entry,
                parent_refs=artifact.parent_refs,
                source_context=env["source"],
            )
        assert not fr._d3_queue_artifact_matches_entry_v02(
            artifact,
            entry,
            env["source"],
        )
    for helper in (
        fr._d3_queue_artifact_trace_refs_v02,
        fr._d3_build_queue_artifact_v02,
        fr._d3_queue_artifact_matches_entry_v02,
    ):
        assert "profile_d_omission_index" not in inspect.signature(helper).parameters


def test_d3_profile_d_contextual_child_t06_t08_micro(
    d3_profile_d_contextual_micro_bundle: dict[str, object],
) -> None:
    bundle = d3_profile_d_contextual_micro_bundle
    env = bundle["env"]
    child_input = bundle["child_input"]
    activation_parent_id = bundle["activation_parent_id"]
    final_indexes = bundle["final_indexes"]
    assert isinstance(env, dict)
    assert isinstance(child_input, fr.FractalCellInputV02)
    assert isinstance(activation_parent_id, str)
    assert isinstance(final_indexes, dict)
    pairs = (
        (
            bundle["validating"],
            bundle["validating_artifact"],
            bundle["running_artifact"],
            "t06",
        ),
        (
            bundle["terminal"],
            bundle["terminal_artifact"],
            bundle["validating_artifact"],
            "t08",
        ),
    )
    for entry, artifact, source_artifact, rule_id in pairs:
        assert isinstance(entry, fr.FractalCellQueueEntryV02)
        assert isinstance(artifact, KernelArtifactV01)
        assert isinstance(source_artifact, KernelArtifactV01)
        assert entry.cell_id == child_input.cell_id
        assert entry.parent_cell_id == child_input.parent_cell_id
        assert entry.node_id == bundle["node"].node_id
        assert entry.observed_evidence_refs == child_input.evidence_refs
        assert entry.observed_evidence_refs.count(activation_parent_id) == 1
        assert entry.lineage_refs.count(activation_parent_id) == 2
        assert _kernel_payload(artifact)["observed_evidence_refs"] == list(
            child_input.evidence_refs
        )
        assert artifact.trace_refs.count(activation_parent_id) == 1
        assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
        other_evidence = tuple(
            item for item in child_input.evidence_refs if item != activation_parent_id
        )
        evidence_positions = tuple(
            artifact.trace_refs.index(item) for item in other_evidence
        )
        assert evidence_positions == tuple(sorted(evidence_positions))
        assert artifact.trace_refs[0] == entry.transition_decision_id
        assert artifact.trace_refs[1] == entry.topology_id
        assert validate_kernel_artifact_v01(artifact) == ()
        omission_index = fr._d3_profile_d_omission_index_v02(
            queue_entry=entry,
            source_context=env["source"],
            topology=env["topology"],
            indexes=final_indexes,
            settled_budget_log=env["budget_log"],
            settled_queue_entry_log=env["queue_log"],
            settled_cell_inputs=env["cell_inputs"],
            settled_scope_projections=env["scope_projections"],
            observed_work_context=None,
        )
        assert type(omission_index) is int
        assert entry.lineage_refs[omission_index] == activation_parent_id
        expected = fr._d3_expected_queue_artifact_against_prefix_v02(
            entry,
            parent_refs=artifact.parent_refs,
            source_context=env["source"],
            topology=env["topology"],
            indexes=final_indexes,
            settled_budget_log=env["budget_log"],
            settled_queue_entry_log=env["queue_log"],
            settled_cell_inputs=env["cell_inputs"],
            settled_scope_projections=env["scope_projections"],
            observed_work_context=None,
        )
        assert artifact == expected
        assert canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(artifact)
        ) == canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(expected))
        decision = fr._d3_transition_decision_v02(env["registry"], rule_id)
        assert transition_registry.validate_fractal_runtime_transition_decision_v02(
            decision,
            registry=env["registry"],
            source_artifact=source_artifact,
            target_artifact=artifact,
        ) == ()
        payload = _kernel_payload(artifact)
        assert not entry.authority_created
        assert not entry.permission_created
        assert not entry.final_output_created
        assert not entry.drs_write_created
        assert entry.real_world_effects_count == 0
        assert "action_commit_packet_created" not in payload
        assert "receipt_created" not in payload

    validating = bundle["validating"]
    terminal = bundle["terminal"]
    assert (validating.prior_state, validating.state) == ("RUNNING", "VALIDATING")
    assert (terminal.prior_state, terminal.state) == ("VALIDATING", "COMPLETED")
    assert validating.predecessor_queue_entry_id == bundle["running"].queue_entry_id
    assert terminal.predecessor_queue_entry_id == validating.queue_entry_id
    assert terminal.queue_reason_codes == validating.queue_reason_codes
    assert terminal.observed_output_refs == validating.observed_output_refs
    assert terminal.observed_evidence_refs == validating.observed_evidence_refs
    assert terminal.advisory_refs == validating.advisory_refs
    assert _d3_indexes(env) == final_indexes


def test_d3_profile_d_contextual_mutation_matrix_micro(
    d3_profile_d_contextual_micro_bundle: dict[str, object],
) -> None:
    bundle = d3_profile_d_contextual_micro_bundle
    env = bundle["env"]
    child = bundle["child"]
    child_input = bundle["child_input"]
    validating = bundle["validating"]
    terminal = bundle["terminal"]
    activation_parent_id = bundle["activation_parent_id"]
    indexes = bundle["final_indexes"]
    assert isinstance(env, dict)
    assert isinstance(child, dict)
    assert isinstance(child_input, fr.FractalCellInputV02)
    assert isinstance(validating, fr.FractalCellQueueEntryV02)
    assert isinstance(terminal, fr.FractalCellQueueEntryV02)
    assert isinstance(activation_parent_id, str)
    assert isinstance(indexes, dict)

    def omission(
        entry: fr.FractalCellQueueEntryV02,
        *,
        candidate_indexes: dict[str, object] = indexes,
        cell_inputs: tuple[fr.FractalCellInputV02, ...] = env["cell_inputs"],
    ) -> int | None:
        return fr._d3_profile_d_omission_index_v02(
            queue_entry=entry,
            source_context=env["source"],
            topology=env["topology"],
            indexes=candidate_indexes,
            settled_budget_log=env["budget_log"],
            settled_queue_entry_log=env["queue_log"],
            settled_cell_inputs=cell_inputs,
            settled_scope_projections=env["scope_projections"],
            observed_work_context=None,
        )

    labels: list[str] = []

    def reject(label: str, callback: object) -> None:
        assert callable(callback)
        with pytest.raises(ValueError):
            callback()
        labels.append(label)

    root_input = env["cell_inputs"][0]
    assert isinstance(root_input, fr.FractalCellInputV02)
    reject(
        "foreign_same_type_child_input",
        lambda: omission(validating, cell_inputs=(root_input,)),
    )

    evidence_index = child_input.evidence_refs.index(activation_parent_id)
    evidence_without_activation = (
        child_input.evidence_refs[:evidence_index]
        + child_input.evidence_refs[evidence_index + 1:]
    )
    input_without_activation = _seal(
        replace(child_input, evidence_refs=evidence_without_activation)
    )
    assert isinstance(input_without_activation, fr.FractalCellInputV02)
    reject(
        "child_input_activation_parent_evidence_removed",
        lambda: omission(
            validating,
            cell_inputs=(root_input, input_without_activation),
        ),
    )

    duplicated_evidence = (
        child_input.evidence_refs[:evidence_index + 1]
        + (activation_parent_id,)
        + child_input.evidence_refs[evidence_index + 1:]
    )
    input_with_duplicate = _seal(
        replace(child_input, evidence_refs=duplicated_evidence)
    )
    assert isinstance(input_with_duplicate, fr.FractalCellInputV02)
    reject(
        "child_input_activation_parent_evidence_duplicated",
        lambda: omission(
            validating,
            cell_inputs=(root_input, input_with_duplicate),
        ),
    )

    reordered_evidence = tuple(reversed(child_input.evidence_refs))
    assert reordered_evidence != child_input.evidence_refs
    reordered_input = _seal(replace(child_input, evidence_refs=reordered_evidence))
    assert isinstance(reordered_input, fr.FractalCellInputV02)
    reject(
        "child_input_evidence_reordered",
        lambda: omission(validating, cell_inputs=(root_input, reordered_input)),
    )

    foreign_indexes = dict(indexes)
    foreign_artifact_by_id = dict(indexes["artifact_by_id"])
    foreign_artifact_by_id[activation_parent_id] = bundle["initial_artifact"]
    foreign_indexes["artifact_by_id"] = foreign_artifact_by_id
    reject(
        "foreign_activation_parent_artifact",
        lambda: omission(validating, candidate_indexes=foreign_indexes),
    )

    broken_predecessor = _d3_reseal_profile_d_queue_entry_v036(
        validating,
        predecessor_queue_entry_id=bundle["ready"].queue_entry_id,
    )
    reject("broken_predecessor_queue_entry_id", lambda: omission(broken_predecessor))

    skipped_snapshot = _d3_reseal_profile_d_queue_entry_v036(
        validating,
        snapshot_sequence=validating.snapshot_sequence + 1,
    )
    reject("skipped_snapshot_sequence", lambda: omission(skipped_snapshot))

    wrong_parent = _d3_reseal_profile_d_queue_entry_v036(
        validating,
        parent_cell_id=child_input.cell_id,
    )
    reject("wrong_parent_cell_id", lambda: omission(wrong_parent))

    wrong_node = _d3_reseal_profile_d_queue_entry_v036(
        validating,
        node_id=child["nodes"][1].node_id,
    )
    assert child["nodes"][1].node_kind == "POST_VV"
    assert omission(wrong_node) is None
    labels.append("wrong_node_id_nonlocal_node_kind")

    assert omission(bundle["ready"]) is None
    labels.append("wrong_t_state_pair")

    arbitrary_duplicate = _d3_reseal_profile_d_queue_entry_v036(
        validating,
        observed_output_refs=(validating.topology_id,),
    )
    reject("arbitrary_duplicate_outside_evidence_role", lambda: omission(arbitrary_duplicate))

    mismatched_terminal = _d3_reseal_profile_d_queue_entry_v036(
        terminal,
        observed_evidence_refs=tuple(reversed(terminal.observed_evidence_refs)),
    )
    reject("mismatched_terminal_copy_of_t06_evidence", lambda: omission(mismatched_terminal))

    assert tuple(labels) == (
        "foreign_same_type_child_input",
        "child_input_activation_parent_evidence_removed",
        "child_input_activation_parent_evidence_duplicated",
        "child_input_evidence_reordered",
        "foreign_activation_parent_artifact",
        "broken_predecessor_queue_entry_id",
        "skipped_snapshot_sequence",
        "wrong_parent_cell_id",
        "wrong_node_id_nonlocal_node_kind",
        "wrong_t_state_pair",
        "arbitrary_duplicate_outside_evidence_role",
        "mismatched_terminal_copy_of_t06_evidence",
    )



def test_d3_external_d4_boundary_strict_prefix_micro(
    d3_profile_d_contextual_micro_bundle: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forbidden_calls: list[str] = []

    def forbidden_eval(*args: object, **kwargs: object) -> object:
        forbidden_calls.append("_d3_eval")
        raise AssertionError("external D4 boundary invoked D3 semantic evaluator")

    def forbidden_finish(*args: object, **kwargs: object) -> object:
        forbidden_calls.append("_d3_finish_running_local")
        raise AssertionError("external D4 boundary invoked D3 local finish helper")

    monkeypatch.setattr(sys.modules[__name__], "_d3_eval", forbidden_eval)
    monkeypatch.setattr(
        sys.modules[__name__],
        "_d3_finish_running_local",
        forbidden_finish,
    )
    env, slot, _slot_artifact = _d3_child_result_runtime_environment(
        d3_profile_d_contextual_micro_bundle
    )
    assert forbidden_calls == []
    boundary = env["child_result_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["boundary_kind"] == _TEST_ONLY_EXTERNAL_D4_BOUNDARY
    assert boundary["external_tail_kinds"] == _TEST_ONLY_EXTERNAL_D4_NODE_KINDS
    assert boundary["actual_d3_terminal_entry"] == (
        d3_profile_d_contextual_micro_bundle["terminal"]
    )
    assert boundary["actual_d3_terminal_artifact"] == (
        d3_profile_d_contextual_micro_bundle["terminal_artifact"]
    )
    terminal_entries = boundary["terminal_entries"]
    terminal_artifacts = boundary["terminal_artifacts"]
    assert isinstance(terminal_entries, tuple)
    assert isinstance(terminal_artifacts, tuple)
    assert tuple(item.node_id for item in terminal_entries) == (
        boundary["input"].ordered_node_ids
    )
    assert tuple(item.node_kind for item in boundary["nodes"][1:]) == (
        _TEST_ONLY_EXTERNAL_D4_NODE_KINDS
    )
    assert all(item.state == "COMPLETED" for item in terminal_entries)
    assert all(validate_kernel_artifact_v01(item) == () for item in terminal_artifacts)
    assert _d3_indexes(env) == boundary["indexes"]

    result, artifact = _d3_child_result_fixture(
        env,
        outcome="COMPLETED",
        ordinal=63,
    )
    assert fr._d3_child_result_artifact_pair_valid_v02(
        result,
        artifact,
        source_context=env["source"],
        topology=env["topology"],
        current_entry=slot,
        indexes=boundary["indexes"],
    )


def test_d3_root_t02_queue_artifact_and_input_five_modes(
    d3_mode_environments: dict[str, dict[str, object]],
    ) -> None:
    queue_payload_fields = (
        "queue_entry_id", "topology_seed_id", "cell_id", "parent_cell_id",
        "node_id", "planned_child_cell_id", "cell_depth", "scope_ref",
        "cell_budget_id", "global_budget_id", "state", "prior_state",
        "predecessor_relation", "canonical_priority", "node_instance_sequence",
        "snapshot_sequence", "admission_round", "queue_reason_codes",
        "observed_output_refs", "observed_evidence_refs", "advisory_refs",
        "root_review_required", "authority_created", "permission_created",
        "final_output_created", "drs_write_created", "real_world_effects_count",
    )
    for mode, env in d3_mode_environments.items():
        topology = env["topology"]
        queues = env["queues"]
        artifacts = env["queue_artifacts"]
        cell_input = env["cell_input"]
        planned = env["planned"]
        assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
        assert isinstance(queues, tuple) and isinstance(artifacts, tuple)
        assert isinstance(cell_input, fr.FractalCellInputV02)
        assert len(queues) == len(dict(fr.MODE_NODE_TEMPLATE_ROWS_V02)[mode])
        assert tuple(item.node_id for item in queues) == topology.ordered_node_ids
        assert tuple(item.node_instance_sequence for item in queues) == tuple(range(len(queues)))
        assert all(
            item.state == "PENDING"
            and item.prior_state is None
            and item.predecessor_queue_entry_id is None
            and item.snapshot_sequence == item.admission_round == 0
            and item.queue_reason_codes == ()
            and item.observed_output_refs == item.observed_evidence_refs == item.advisory_refs == ()
            for item in queues
        )
        for index, (entry, artifact) in enumerate(zip(queues, artifacts, strict=True)):
            payload = _kernel_payload(artifact)
            assert tuple(payload) == tuple(sorted(queue_payload_fields))
            assert "topology_id" not in payload
            assert "predecessor_queue_entry_id" not in payload
            assert entry.cell_budget_id == entry.global_budget_id
            assert entry.lineage_refs[4:6] == (
                entry.cell_budget_id,
                entry.global_budget_id,
            )
            assert entry.lineage_refs.count(entry.cell_budget_id) == 2
            assert payload["cell_budget_id"] == entry.cell_budget_id
            assert payload["global_budget_id"] == entry.global_budget_id
            assert artifact.trace_refs.count(entry.cell_budget_id) == 1
            assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
            assert artifact.trace_refs == fr._d3_queue_artifact_trace_refs_v02(
                entry,
                parent_refs=artifact.parent_refs,
            )
            assert artifact.trace_refs[0] == entry.transition_decision_id
            assert artifact.trace_refs[1] == entry.topology_id == topology.topology_id
            assert payload["topology_seed_id"] == topology.topology_seed_id
            assert artifact.parent_refs == (env["topology_artifact"].artifact_id,)
            assert validate_kernel_artifact_v01(artifact) == ()
            assert transition_registry.validate_fractal_runtime_transition_decision_v02(
                env["t02"][index],
                registry=env["registry"],
                source_artifact=env["topology_artifact"],
                target_artifact=artifact,
            ) == ()
        assert cell_input.ordered_initial_queue_entry_ids == tuple(item.queue_entry_id for item in queues)
        assert cell_input.ordered_required_queue_entry_ids == cell_input.ordered_initial_queue_entry_ids
        assert cell_input.ordered_planned_child_cell_ids == planned
        assert (len(planned) == 2) is (mode == "full_fractal")
        assert cell_input.authority_created is cell_input.permission_created is False
        assert cell_input.action_commit_packet_created is cell_input.final_output_created is False
        assert cell_input.real_world_effects_count == 0
        with pytest.raises(ValueError):
            fr.admit_runtime_execution_topology_v02(
                source_context=env["source"],
                topology=topology,
                topology_artifact=env["topology_artifact"],
                topology_transition_decision=env["t01"],
                cell_id=topology.root_cell_id,
                parent_cell_id=None,
                parent_slot_artifact=None,
                cell_depth=0,
                scope_ref=topology.accepted_scope_ref,
                cell_budget=env["root_create"],
                global_budget=env["root_create"],
                projected_nodes=tuple(reversed(env["nodes"])),
                planned_child_cell_ids=planned,
                admission_decisions=env["t02"],
                cell_instantiation_order=(topology.root_cell_id,),
                **_d3_prefix_kwargs(env),
            )


def test_d3_queue_state_chain_latest_budget_and_ctx_trace(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    initial_budget_log = env["budget_log"]
    completed, completed_artifact = _d3_complete_local_node(env, node_index=0)
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    assert isinstance(queue_log, tuple) and isinstance(artifact_log, tuple)
    chain = tuple(
        item
        for item in queue_log
        if item.cell_id == completed.cell_id and item.node_id == completed.node_id
    )
    assert tuple(item.state for item in chain) == (
        "PENDING", "READY", "RUNNING", "VALIDATING", "COMPLETED",
    )
    assert tuple(item.snapshot_sequence for item in chain) == (0, 1, 2, 3, 4)
    assert chain[3].observed_evidence_refs == env["cell_input"].evidence_refs
    assert chain[4].observed_output_refs == chain[3].observed_output_refs
    artifact_by_queue = {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(queue_log, artifact_log, strict=True)
    }
    for entry in chain[1:]:
        artifact = artifact_by_queue[entry.queue_entry_id]
        payload = _kernel_payload(artifact)
        assert entry.cell_budget_id == entry.global_budget_id
        assert entry.lineage_refs.count(entry.cell_budget_id) == 2
        assert payload["cell_budget_id"] == payload["global_budget_id"]
        assert artifact.trace_refs.count(entry.cell_budget_id) == 1
        assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
        assert artifact.trace_refs == fr._d3_queue_artifact_trace_refs_v02(
            entry,
            parent_refs=artifact.parent_refs,
        )
        if entry.predecessor_queue_entry_id is not None:
            assert artifact.trace_refs.index(entry.predecessor_queue_entry_id) < min(
                (
                    artifact.trace_refs.index(item)
                    for item in (
                        *entry.observed_output_refs,
                        *entry.observed_evidence_refs,
                        *entry.advisory_refs,
                    )
                ),
                default=len(artifact.trace_refs),
            )
    assert completed_artifact.trace_refs[0] == completed.transition_decision_id
    assert completed_artifact.trace_refs[1] == env["topology"].topology_id
    predecessor = artifact_by_queue[completed.predecessor_queue_entry_id]
    assert completed_artifact.parent_refs == (env["topology_artifact"].artifact_id, predecessor.artifact_id)
    completed_payload = _kernel_payload(completed_artifact)
    validating_payload = _kernel_payload(predecessor)
    assert completed_payload["topology_seed_id"] == validating_payload["topology_seed_id"]
    assert completed_payload["cell_id"] == validating_payload["cell_id"]
    assert completed_payload["node_id"] == validating_payload["node_id"]
    assert "topology_id" not in completed_payload
    assert "predecessor_queue_entry_id" not in completed_payload
    assert len(env["budget_log"]) == len(initial_budget_log) + 2
    base = _d3_clone_environment(d3_full_fractal_micro_environment)
    indexes = _d3_indexes(base)
    blocked_node = base["nodes"][3]
    blocked_entry = indexes["latest_by_key"][(base["topology"].root_cell_id, blocked_node.node_id)]
    assert _d3_eval(
        base,
        source_artifact=indexes["artifact_by_queue_id"][blocked_entry.queue_entry_id],
        node=blocked_node,
        current_entry=blocked_entry,
        cell_input=base["cell_input"],
        cell_budget=base["root_create"],
        global_budget=base["root_create"],
        dependencies=(),
    ) is None
    foreign = _seal(replace(base["root_create"], budget_event_ref="foreign:g2d3"))
    with pytest.raises(ValueError):
        _d3_eval(
            base,
            source_artifact=base["queue_artifacts"][0],
            node=base["nodes"][0],
            current_entry=base["queues"][0],
            cell_input=base["cell_input"],
            cell_budget=foreign,
            global_budget=foreign,
        )
    with pytest.raises(ValueError):
        fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            _seal(replace(completed, topology_id="frtopology_v02:" + "f" * 64)),
            topology_artifact=env["topology_artifact"],
            predecessor_artifact=predecessor,
            activation_parent_artifact=None,
            local_child_result_artifact=None,
            source_context=env["source"],
            **_d3_prefix_kwargs(
                env,
                settled_queue_entry_log=queue_log + (
                    _seal(replace(completed, topology_id="frtopology_v02:" + "f" * 64)),
                ),
            ),
        )


def test_d3_invoked_child_result_observation_alias_matrix(
    d3_profile_d_contextual_micro_bundle: dict[str, object],
) -> None:
    env, running, running_artifact = _d3_child_result_runtime_environment(
        d3_profile_d_contextual_micro_bundle
    )
    indexes = _d3_indexes(env)
    dependency = indexes["latest_by_key"][(
        env["topology"].root_cell_id,
        env["nodes"][0].node_id,
    )]
    _live_cell, start = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=env["topology"].root_cell_id,
        indexes=indexes,
    )
    anchor = indexes["budget_by_id"][running.cell_budget_id]
    node = env["nodes"][1]
    cell_input = env["cell_input"]
    assert node.node_kind == "FRACTAL_CELL"
    expected_terminal_rules = {
        "COMPLETED": "g2d_t08_validating_to_completed",
        "DEGRADED": "g2d_t09_validating_to_degraded",
        "BLOCKED": "g2d_t10_validating_to_blocked",
        "NEEDS_USER": "g2d_t11_validating_to_needs_user",
        "DEADEND": "g2d_t12_validating_to_deadend",
    }
    first_validating: tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01, KernelArtifactV01] | None = None
    for ordinal, outcome in enumerate(expected_terminal_rules, start=1):
        branch = _d3_clone_environment(env)
        child_result, result_artifact = _d3_child_result_fixture(
            branch,
            outcome=outcome,
            ordinal=ordinal,
        )
        outputs = (result_artifact.artifact_id,)
        evidence = child_result.evidence_refs
        advisories = (child_result.post_vv_report_ref, child_result.gt_advisory_ref)
        t06 = _d3_eval(
            branch,
            source_artifact=running_artifact,
            node=node,
            current_entry=running,
            cell_input=cell_input,
            cell_budget=anchor,
            global_budget=anchor,
            dependencies=(dependency,),
            queue_reason_codes=child_result.reason_codes,
            observed_output_refs=outputs,
            observed_evidence_refs=evidence,
            advisory_refs=advisories,
            local_child_result=child_result,
            local_child_result_artifact=result_artifact,
        )
        assert isinstance(t06, TransitionDecisionV01)
        finish = _d3_budget_successor(
            branch,
            start,
            event="FINISH_NODE",
            decision=t06,
            cell_input=cell_input,
        )
        validating, validating_artifact, validating_decision = _d3_advance(
            branch,
            current=running,
            current_artifact=running_artifact,
            node=node,
            cell_input=cell_input,
            cell_budget_before=anchor,
            global_budget_before=anchor,
            cell_budget_after=finish,
            global_budget_after=finish,
            dependencies=(dependency,),
            round_entries=_d3_latest(branch),
            queue_reason_codes=child_result.reason_codes,
            observed_output_refs=outputs,
            observed_evidence_refs=evidence,
            advisory_refs=advisories,
            local_child_result=child_result,
            local_child_result_artifact=result_artifact,
        )
        terminal, terminal_artifact, terminal_decision = _d3_advance(
            branch,
            current=validating,
            current_artifact=validating_artifact,
            node=node,
            cell_input=cell_input,
            cell_budget_before=finish,
            global_budget_before=finish,
            cell_budget_after=finish,
            global_budget_after=finish,
            dependencies=(dependency,),
            round_entries=_d3_latest(branch),
            queue_reason_codes=validating.queue_reason_codes,
            observed_output_refs=validating.observed_output_refs,
            observed_evidence_refs=validating.observed_evidence_refs,
            advisory_refs=validating.advisory_refs,
            local_child_result=child_result,
            local_child_result_artifact=result_artifact,
        )
        assert validating_decision.rule_id == "g2d_t06_running_to_validating"
        assert terminal_decision.rule_id == expected_terminal_rules[outcome]
        assert terminal.state == outcome
        if outcome == "DEGRADED":
            assert terminal.queue_reason_codes == ("g2d_partial_failure_recorded",)
            assert terminal_decision.reason_code == "g2d_transition_degraded_recorded"
        for entry, artifact in (
            (validating, validating_artifact),
            (terminal, terminal_artifact),
        ):
            payload = _kernel_payload(artifact)
            assert entry.cell_budget_id == entry.global_budget_id
            assert entry.lineage_refs.count(entry.cell_budget_id) == 2
            assert entry.lineage_refs.count(result_artifact.artifact_id) == 2
            assert entry.observed_output_refs == (result_artifact.artifact_id,)
            assert payload["observed_output_refs"] == [result_artifact.artifact_id]
            assert artifact.parent_refs[2] == result_artifact.artifact_id
            assert artifact.trace_refs.count(entry.cell_budget_id) == 1
            assert artifact.trace_refs.count(result_artifact.artifact_id) == 1
            assert artifact.trace_refs.index(result_artifact.artifact_id) < artifact.trace_refs.index(
                entry.observed_evidence_refs[0]
            )
            assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
            assert artifact.trace_refs == fr._d3_queue_artifact_trace_refs_v02(
                entry,
                parent_refs=artifact.parent_refs,
            )
            assert validate_kernel_artifact_v01(artifact) == ()
        assert transition_registry.validate_fractal_runtime_transition_decision_v02(
            validating_decision,
            registry=branch["registry"],
            source_artifact=running_artifact,
            target_artifact=validating_artifact,
        ) == ()
        assert transition_registry.validate_fractal_runtime_transition_decision_v02(
            terminal_decision,
            registry=branch["registry"],
            source_artifact=validating_artifact,
            target_artifact=terminal_artifact,
        ) == ()
        if first_validating is None:
            first_validating = (validating, validating_artifact, result_artifact)

    assert first_validating is not None
    validating, validating_artifact, result_artifact = first_validating
    raw_trace = (validating.transition_decision_id, *validating.lineage_refs)
    assert raw_trace.count(validating.cell_budget_id) == 2
    assert raw_trace.count(result_artifact.artifact_id) == 2
    assert validate_kernel_artifact_v01(replace(validating_artifact, trace_refs=raw_trace))
    with pytest.raises(ValueError):
        fr._d3_queue_artifact_trace_refs_v02(
            _seal(replace(
                validating,
                global_budget_id="frbudget_v02:" + "f" * 64,
                lineage_refs=(
                    *validating.lineage_refs[:5],
                    "frbudget_v02:" + "f" * 64,
                    *validating.lineage_refs[6:],
                ),
            )),
            parent_refs=validating_artifact.parent_refs,
        )
    with pytest.raises(ValueError):
        fr._d3_queue_artifact_trace_refs_v02(
            _seal(replace(
                validating,
                observed_evidence_refs=(result_artifact.artifact_id,),
                lineage_refs=(
                    *validating.lineage_refs[:-3],
                    result_artifact.artifact_id,
                    *validating.lineage_refs[-2:],
                ),
            )),
            parent_refs=validating_artifact.parent_refs,
        )
    assert not fr._d3_queue_artifact_matches_entry_v02(
        replace(
            validating_artifact,
            trace_refs=tuple(
                item
                for index, item in enumerate(validating_artifact.trace_refs)
                if index != 2
            ),
        ),
        validating,
        env["source"],
    )
    child_result, result_artifact = _d3_child_result_fixture(
        env,
        outcome="COMPLETED",
        ordinal=15,
    )
    with pytest.raises(ValueError):
        _d3_eval(
            env,
            source_artifact=running_artifact,
            node=node,
            current_entry=running,
            cell_input=cell_input,
            cell_budget=start,
            global_budget=start,
            dependencies=(dependency,),
            queue_reason_codes=child_result.reason_codes,
            observed_output_refs=(result_artifact.artifact_id,),
            observed_evidence_refs=child_result.evidence_refs,
            advisory_refs=(child_result.post_vv_report_ref, child_result.gt_advisory_ref),
            local_child_result=child_result,
            local_child_result_artifact=None,
        )


def test_d3_child_result_artifact_exact_pair_positive_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env, slot, _slot_artifact = _d3_child_result_boundary_environment(
        d3_full_fractal_micro_environment
    )
    boundary = env["child_result_boundary"]
    indexes = boundary["indexes"]
    assert all(item not in env["queue_log"] for item in boundary["terminal_entries"])
    assert all(item not in env["artifact_log"] for item in boundary["terminal_artifacts"])
    for ordinal, outcome in enumerate(
        ("COMPLETED", "DEGRADED", "BLOCKED", "NEEDS_USER", "DEADEND"),
        start=40,
    ):
        result, artifact = _d3_child_result_fixture(
            env, outcome=outcome, ordinal=ordinal
        )
        assert fr._d3_child_result_artifact_pair_valid_v02(
            result, artifact, source_context=env["source"],
            topology=env["topology"], current_entry=slot, indexes=indexes,
        )
        expected = fr._d3_expected_child_result_artifact_v02(
            result, source_context=env["source"], topology=env["topology"],
            current_entry=slot, indexes=indexes,
        )
        assert artifact == expected
        assert canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(artifact)) == (
            canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(expected))
        )


def test_d3_child_result_artifact_full_field_mutation_matrix_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env, slot, _slot_artifact = _d3_child_result_boundary_environment(
        d3_full_fractal_micro_environment
    )
    boundary = env["child_result_boundary"]
    indexes = boundary["indexes"]
    result, artifact = _d3_child_result_fixture(
        env, outcome="COMPLETED", ordinal=51
    )
    for item in fields(fr.FractalCellResultV02):
        if item.name == "result_id":
            mutated_result = replace(result, result_id="frcellresult_v02:" + "f" * 64)
        else:
            mutated_result = _seal(replace(
                result,
                **{item.name: _same_type_alternate(result, item.name)},
            ))
        assert not fr._d3_child_result_artifact_pair_valid_v02(
            mutated_result, artifact, source_context=env["source"],
            topology=env["topology"], current_entry=slot, indexes=indexes,
        )
        if item.name in _D3_RESULT_PAYLOAD_FIELDS:
            payload = dict(_kernel_payload(artifact))
            value = payload[item.name]
            payload[item.name] = (
                not value if type(value) is bool else
                value + 1 if type(value) is int else
                value + ":foreign" if type(value) is str else
                [*value, "ref:foreign"]
            )
            mutated_artifact = _d3_reseal_result_artifact(
                artifact, payload=payload
            )
            assert not fr._d3_child_result_artifact_pair_valid_v02(
                result, mutated_artifact, source_context=env["source"],
                topology=env["topology"], current_entry=slot, indexes=indexes,
            )
    top_level_mutations = {
        "abi_version": "v9.9",
        "artifact_type": "FractalRuntimeReport",
        "schema_version": "v9.9",
        "transaction_id": artifact.transaction_id + ":foreign",
        "owner_root_id": artifact.owner_root_id + ":foreign",
        "source_component": "foreign_component",
        "authority_class": "ROOT",
        "lifecycle_state": "PENDING",
        "parent_refs": tuple(reversed(artifact.parent_refs)),
        "trace_refs": tuple(reversed(artifact.trace_refs)),
        "time_envelope": {
            **dict(kernel_artifact_to_plain_dict_v01(artifact)["time_envelope"]),
            "ttl_seconds": 1,
        },
    }
    for name, value in top_level_mutations.items():
        mutated = _d3_reseal_result_artifact(artifact, **{name: value})
        assert not fr._d3_child_result_artifact_pair_valid_v02(
            result, mutated, source_context=env["source"],
            topology=env["topology"], current_entry=slot, indexes=indexes,
        )
    for payload in (
        {key: value for key, value in _kernel_payload(artifact).items() if key != "scope_ref"},
        {**_kernel_payload(artifact), "unexpected": "value"},
    ):
        mutated = _d3_reseal_result_artifact(artifact, payload=payload)
        assert not fr._d3_child_result_artifact_pair_valid_v02(
            result, mutated, source_context=env["source"],
            topology=env["topology"], current_entry=slot, indexes=indexes,
        )


def test_d3_child_activation_scope_budget_and_initial_family(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    nodes = env["nodes"]
    parent_input = env["cell_input"]
    root_create = env["root_create"]
    planned = env["planned"]
    assert isinstance(nodes, tuple)
    assert isinstance(parent_input, fr.FractalCellInputV02)
    assert isinstance(root_create, fr.FractalRuntimeBudgetV02)
    dependency, _ = _d3_complete_local_node(env, node_index=0)
    slot_running, slot_artifact, start = _d3_start_node(
        env,
        node_index=1,
        dependencies=(dependency,),
    )
    child_id = planned[0]
    precheck = fr._d3_child_activation_precheck_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        source_artifact=slot_artifact,
        current_entry=slot_running,
        node=nodes[1],
        cell_input=parent_input,
        cell_budget_before=start,
        global_budget_before=start,
        dependencies=(dependency,),
        indexes=_d3_indexes(env),
    )
    assert precheck["derived_disposition"] == "PASS_FOR_CHILD_ACTIVATION"
    child_allocated = fr.build_fractal_runtime_budget_v02(
        policy=env["source"].runtime_policy,
        topology_seed=env["seed"],
        allocation_parent_budget=root_create,
        predecessor_budget=None,
        owning_cell_id=child_id,
        budget_scope="CHILD_CELL_LOCAL",
        budget_state="ALLOCATED",
        budget_event_kind="INITIAL_ALLOCATION",
        budget_context_input=parent_input,
        canonical_child_index=0,
        allocation_queue_entries=env["queues"],
        transition_decision=None,
        paired_cell_budget=None,
        child_result=None,
    )
    projection = fr.project_parent_child_scope_v02(
        source_context=env["source"],
        topology=env["topology"],
        parent_input=parent_input,
        child_cell_id=child_id,
        child_scope_ref=env["topology"].accepted_scope_ref,
        parent_budget=root_create,
        child_budget=child_allocated,
        global_budget=start,
    )
    assert projection.scope_relation == "EQUAL"
    assert projection.child_depth == parent_input.cell_depth + 1 == 1
    assert set(projection.child_allowed_capability_ids).issubset(projection.parent_allowed_capability_ids)
    assert set(projection.parent_forbidden_claims).issubset(projection.child_forbidden_claims)
    assert projection.child_ttl_units <= projection.parent_ttl_units
    assert fr.validate_parent_child_scope_against_sources_v02(
        projection,
        source_context=env["source"],
        topology=env["topology"],
        parent_input=parent_input,
        parent_budget=root_create,
        child_budget=child_allocated,
        global_budget=start,
    ).status == "PASS"
    child_active = _d3_budget_successor(
        env,
        child_allocated,
        event="ACTIVATE",
        cell_input=parent_input,
        allocation_parent=root_create,
        owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL",
        canonical_child_index=0,
        allocation_queue_entries=env["queues"],
    )
    global_active = _d3_budget_successor(
        env,
        start,
        event="ACTIVATE",
        cell_input=parent_input,
        canonical_child_index=0,
        allocation_queue_entries=env["queues"],
        paired_cell_budget=child_active,
    )
    child_create = _d3_budget_successor(
        env,
        child_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        allocation_parent=root_create,
        owning_cell_id=child_id,
        scope="CHILD_CELL_LOCAL",
        canonical_child_index=0,
        allocation_queue_entries=env["queues"],
    )
    global_create = _d3_budget_successor(
        env,
        global_active,
        event="CELL_CREATE",
        cell_input=parent_input,
        canonical_child_index=0,
        allocation_queue_entries=env["queues"],
        paired_cell_budget=child_create,
    )
    assert child_allocated.consumed_cell_count == child_active.consumed_cell_count == 0
    assert child_create.consumed_cell_count == 1
    assert global_create.consumed_cell_count == start.consumed_cell_count + 1
    env["budget_log"] = env["budget_log"] + (
        child_allocated,
        child_active,
        global_active,
        child_create,
        global_create,
    )
    env["scope_projections"] = (projection,)
    scope_report = fr.validate_parent_child_scope_against_sources_v02(
        projection,
        source_context=env["source"],
        topology=env["topology"],
        parent_input=parent_input,
        parent_budget=root_create,
        child_budget=child_allocated,
        global_budget=start,
    )
    existing_reports = env["validation_reports"]
    env["validation_reports"] = (
        *existing_reports[:4],
        *(fr.validate_fractal_cell_queue_entry_v02(item) for item in env["queue_log"]),
        scope_report,
        *(
            item
            for item in existing_reports[4:]
            if item.validation_target == "CELL_INPUT_AGAINST_SOURCES"
        ),
    )
    leaf_nodes = tuple(nodes[index] for index in (0, 4, 5, 6))
    child_t02 = tuple(
        _d3_eval(
            env,
            source_artifact=env["topology_artifact"],
            node=node,
            current_entry=None,
            cell_input=None,
            cell_budget=child_create,
            global_budget=global_create,
            cell_id=child_id,
            parent_cell_id=env["topology"].root_cell_id,
            planned_child_cell_id=None,
            cell_depth=1,
            scope_ref=projection.child_scope_ref,
        )
        for node in leaf_nodes
    )
    child_queues = fr.admit_runtime_execution_topology_v02(
        source_context=env["source"],
        topology=env["topology"],
        topology_artifact=env["topology_artifact"],
        topology_transition_decision=env["t01"],
        cell_id=child_id,
        parent_cell_id=env["topology"].root_cell_id,
        parent_slot_artifact=slot_artifact,
        cell_depth=1,
        scope_ref=projection.child_scope_ref,
        cell_budget=child_create,
        global_budget=global_create,
        projected_nodes=leaf_nodes,
        planned_child_cell_ids=(),
        admission_decisions=child_t02,
        cell_instantiation_order=(env["topology"].root_cell_id, child_id),
        **_d3_prefix_kwargs(env),
    )
    queue_log = env["queue_log"]
    artifact_log = env["artifact_log"]
    reports = env["validation_reports"]
    assert isinstance(queue_log, tuple) and isinstance(artifact_log, tuple) and isinstance(reports, tuple)
    child_artifacts_list: list[KernelArtifactV01] = []
    for entry in child_queues:
        artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            entry,
            topology_artifact=env["topology_artifact"],
            predecessor_artifact=None,
            activation_parent_artifact=slot_artifact,
            local_child_result_artifact=None,
            source_context=env["source"],
            **_d3_prefix_kwargs(
                env,
                settled_queue_entry_log=queue_log + (entry,),
                settled_queue_artifact_log=artifact_log,
                settled_validation_reports=reports,
            ),
        )
        queue_log += (entry,)
        artifact_log += (artifact,)
        reports = _d3_retained_reports(env, queue_log)
        child_artifacts_list.append(artifact)
    child_artifacts = tuple(child_artifacts_list)
    env["queue_log"] = queue_log
    env["artifact_log"] = artifact_log
    env["validation_reports"] = reports
    assert all(
        artifact.parent_refs == (env["topology_artifact"].artifact_id, slot_artifact.artifact_id)
        for artifact in child_artifacts
    )
    for entry, artifact in zip(child_queues, child_artifacts, strict=True):
        payload = _kernel_payload(artifact)
        assert entry.cell_budget_id != entry.global_budget_id
        assert entry.lineage_refs[5:7] == (
            entry.cell_budget_id,
            entry.global_budget_id,
        )
        assert payload["cell_budget_id"] == entry.cell_budget_id
        assert payload["global_budget_id"] == entry.global_budget_id
        assert artifact.trace_refs == (
            entry.transition_decision_id,
            *entry.lineage_refs,
        )
        assert artifact.trace_refs == fr._d3_queue_artifact_trace_refs_v02(
            entry,
            parent_refs=artifact.parent_refs,
        )
        assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
    child_input = fr.build_fractal_cell_input_from_queue_v02(
        source_context=env["source"],
        topology=env["topology"],
        topology_artifact=env["topology_artifact"],
        cell_id=child_id,
        parent_cell_id=env["topology"].root_cell_id,
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        initial_queue_entries=child_queues,
        initial_queue_artifacts=child_artifacts,
        ordered_planned_child_cell_ids=(),
        **_d3_prefix_kwargs(env),
    )
    assert child_input.parent_cell_id == env["topology"].root_cell_id
    assert child_input.scope_projection_id == projection.projection_id
    child_input_report = fr.validate_fractal_cell_input_against_sources_v02(
        child_input,
        source_context=env["source"],
        topology=env["topology"],
        topology_artifact=env["topology_artifact"],
        parent_input=parent_input,
        parent_slot_artifact=slot_artifact,
        scope_projection=projection,
        cell_budget=child_create,
        global_budget=global_create,
        queue_entries=child_queues,
        queue_artifacts=child_artifacts,
        **_d3_prefix_kwargs(env),
    )
    assert child_input_report.status == "PASS"
    env["cell_inputs"] = env["cell_inputs"] + (child_input,)
    env["validation_reports"] = reports + (child_input_report,)
    child_indexes = _d3_indexes(env)
    assert child_indexes["latest_by_key"][(
        env["topology"].root_cell_id,
        leaf_nodes[0].node_id,
    )].cell_id == env["topology"].root_cell_id
    assert child_indexes["latest_by_key"][(
        child_id,
        leaf_nodes[0].node_id,
    )].cell_id == child_id
    child_ready, child_ready_artifact, _ = _d3_advance(
        env,
        current=child_queues[0],
        current_artifact=child_artifacts[0],
        node=leaf_nodes[0],
        cell_input=child_input,
        cell_budget_before=child_create,
        global_budget_before=global_create,
        cell_budget_after=child_create,
        global_budget_after=global_create,
        dependencies=(),
        round_entries=_d3_latest(env),
    )
    assert child_ready_artifact.parent_refs == (env["topology_artifact"].artifact_id, child_artifacts[0].artifact_id)
    assert child_ready.cell_budget_id != child_ready.global_budget_id
    assert child_ready_artifact.trace_refs == (child_ready.transition_decision_id, *child_ready.lineage_refs)
    with pytest.raises(ValueError):
        fr._d3_queue_artifact_trace_refs_v02(
            _seal(replace(
                child_ready,
                global_budget_id=child_ready.cell_budget_id,
                lineage_refs=(
                    *child_ready.lineage_refs[:6],
                    child_ready.cell_budget_id,
                    *child_ready.lineage_refs[7:],
                ),
            )),
            parent_refs=child_ready_artifact.parent_refs,
        )
    with pytest.raises(ValueError):
        fr.admit_runtime_execution_topology_v02(
            source_context=env["source"],
            topology=env["topology"],
            topology_artifact=env["topology_artifact"],
            topology_transition_decision=env["t01"],
            cell_id=child_id,
            parent_cell_id=env["topology"].root_cell_id,
            parent_slot_artifact=slot_artifact,
            cell_depth=1,
            scope_ref=projection.child_scope_ref,
            cell_budget=child_active,
            global_budget=global_active,
            projected_nodes=leaf_nodes,
            planned_child_cell_ids=(),
            admission_decisions=child_t02,
            cell_instantiation_order=(env["topology"].root_cell_id, child_id),
            **_d3_prefix_kwargs(env),
        )
    forged_running = _seal(replace(
        slot_running,
        predecessor_queue_entry_id="frqueue_v02:" + "f" * 64,
    ))
    with pytest.raises(ValueError):
        fr._d3_build_queue_artifact_v02(
            forged_running,
            parent_refs=(
                env["topology_artifact"].artifact_id,
                env["queue_artifacts"][1].artifact_id,
            ),
            source_context=env["source"],
        )


_D3_ACTIVATION_MATERIAL_KEYS_V035 = (
    "profile_version", "topology_id", "topology_seed_id", "source_binding_id",
    "route_eligibility_artifact_id", "topology_artifact_id", "parent_cell_id",
    "parent_cell_input_id", "parent_scope_ref", "parent_slot_node_id",
    "parent_slot_assignment_id", "canonical_child_index", "planned_child_cell_id",
    "candidate_child_scope_ref", "parent_slot_initial_queue_entry_id",
    "parent_slot_initial_artifact_id", "parent_slot_t02_decision_id",
    "parent_slot_ready_queue_entry_id", "parent_slot_ready_artifact_id",
    "parent_slot_t04_decision_id", "parent_slot_running_queue_entry_id",
    "parent_slot_running_artifact_id", "parent_slot_t05_decision_id",
    "parent_cell_budget_id", "global_budget_id", "parent_budget_state",
    "global_budget_state", "parent_budget_counters", "global_budget_counters",
    "dependency_queue_entry_ids", "dependency_queue_artifact_ids",
    "dependency_states", "dependency_reason_tuples", "dependency_output_tuples",
    "dependency_evidence_tuples", "parent_allowed_capability_ids",
    "child_allowed_capability_ids", "parent_forbidden_claims",
    "child_forbidden_claims", "parent_ttl_units", "child_ttl_units",
    "parent_depth", "child_depth", "instantiated_sibling_count",
    "instantiated_total_cell_count", "occupied_admission_slots", "max_depth",
    "max_fan_out", "max_total_cells", "max_parallelism", "max_provider_calls",
    "relevant_parent_slot_revise_observation_ids",
    "relevant_parent_slot_revise_terminal_states", "derived_disposition",
    "derived_queue_reason_codes", "derived_evidence_refs",
)


def _d3_parent_slot_precheck_fixture(
    base: dict[str, object],
) -> tuple[
    dict[str, object],
    fr.FractalCellQueueEntryV02,
    KernelArtifactV01,
    fr.FractalRuntimeBudgetV02,
    fr.FractalCellQueueEntryV02,
]:
    env = _d3_clone_environment(base)
    dependency, _ = _d3_complete_local_node(env, node_index=0)
    running, artifact, budget = _d3_start_node(
        env,
        node_index=1,
        dependencies=(dependency,),
    )
    return env, running, artifact, budget, dependency


def _d3_expected_activation_material(
    env: dict[str, object],
    running: fr.FractalCellQueueEntryV02,
    artifact: KernelArtifactV01,
    budget: fr.FractalRuntimeBudgetV02,
    dependency: fr.FractalCellQueueEntryV02,
) -> dict[str, object]:
    indexes = _d3_indexes(env)
    queue_by_id = indexes["queue_by_id"]
    artifact_by_queue = indexes["artifact_by_queue_id"]
    ready = queue_by_id[running.predecessor_queue_entry_id]
    initial = queue_by_id[ready.predecessor_queue_entry_id]
    policy = env["source"].runtime_policy
    ttl = env["source"].router_input.local_routing_snapshot.ttl_seconds
    counters = lambda value: (
        value.max_depth, value.max_fan_out, value.max_total_cells,
        value.max_parallelism, value.max_revise_count, value.max_wall_time_units,
        value.max_token_budget, value.max_provider_calls,
        value.consumed_wall_time_units, value.consumed_token_budget,
        value.consumed_provider_calls, value.consumed_cell_count,
        value.consumed_revise_count, value.current_parallelism,
        value.remaining_wall_time_units, value.remaining_token_budget,
        value.remaining_provider_calls, value.remaining_cell_count,
        value.remaining_revise_count, value.remaining_parallel_slots,
    )
    evidence = (
        env["source"].route_eligibility_artifact.artifact_id,
        env["topology_artifact"].artifact_id,
        env["cell_input"].cell_input_id,
        artifact_by_queue[initial.queue_entry_id].artifact_id,
        artifact_by_queue[ready.queue_entry_id].artifact_id,
        artifact.artifact_id,
        budget.budget_id,
        artifact_by_queue[dependency.queue_entry_id].artifact_id,
    )
    return {
        "profile_version": "v0.3.1",
        "topology_id": env["topology"].topology_id,
        "topology_seed_id": env["topology"].topology_seed_id,
        "source_binding_id": env["topology"].source_binding_id,
        "route_eligibility_artifact_id": env["source"].route_eligibility_artifact.artifact_id,
        "topology_artifact_id": env["topology_artifact"].artifact_id,
        "parent_cell_id": running.cell_id,
        "parent_cell_input_id": env["cell_input"].cell_input_id,
        "parent_scope_ref": env["cell_input"].scope_ref,
        "parent_slot_node_id": running.node_id,
        "parent_slot_assignment_id": env["topology"].ordered_assignment_ids[1],
        "canonical_child_index": 0,
        "planned_child_cell_id": running.planned_child_cell_id,
        "candidate_child_scope_ref": env["cell_input"].scope_ref,
        "parent_slot_initial_queue_entry_id": initial.queue_entry_id,
        "parent_slot_initial_artifact_id": artifact_by_queue[initial.queue_entry_id].artifact_id,
        "parent_slot_t02_decision_id": initial.transition_decision_id,
        "parent_slot_ready_queue_entry_id": ready.queue_entry_id,
        "parent_slot_ready_artifact_id": artifact_by_queue[ready.queue_entry_id].artifact_id,
        "parent_slot_t04_decision_id": ready.transition_decision_id,
        "parent_slot_running_queue_entry_id": running.queue_entry_id,
        "parent_slot_running_artifact_id": artifact.artifact_id,
        "parent_slot_t05_decision_id": running.transition_decision_id,
        "parent_cell_budget_id": budget.budget_id,
        "global_budget_id": budget.budget_id,
        "parent_budget_state": budget.budget_state,
        "global_budget_state": budget.budget_state,
        "parent_budget_counters": counters(budget),
        "global_budget_counters": counters(budget),
        "dependency_queue_entry_ids": (dependency.queue_entry_id,),
        "dependency_queue_artifact_ids": (artifact_by_queue[dependency.queue_entry_id].artifact_id,),
        "dependency_states": (dependency.state,),
        "dependency_reason_tuples": (dependency.queue_reason_codes,),
        "dependency_output_tuples": (dependency.observed_output_refs,),
        "dependency_evidence_tuples": (dependency.observed_evidence_refs,),
        "parent_allowed_capability_ids": policy.allowed_capability_ids,
        "child_allowed_capability_ids": policy.allowed_capability_ids,
        "parent_forbidden_claims": policy.forbidden_claims,
        "child_forbidden_claims": policy.forbidden_claims,
        "parent_ttl_units": ttl,
        "child_ttl_units": ttl,
        "parent_depth": 0,
        "child_depth": 1,
        "instantiated_sibling_count": 0,
        "instantiated_total_cell_count": 1,
        "occupied_admission_slots": 1,
        "max_depth": policy.max_depth,
        "max_fan_out": policy.max_fan_out,
        "max_total_cells": policy.max_total_cells,
        "max_parallelism": policy.max_parallelism,
        "max_provider_calls": policy.max_provider_calls,
        "relevant_parent_slot_revise_observation_ids": (),
        "relevant_parent_slot_revise_terminal_states": (),
        "derived_disposition": "PASS_FOR_CHILD_ACTIVATION",
        "derived_queue_reason_codes": (),
        "derived_evidence_refs": (),
    }


def test_d3_child_activation_precheck_exact_material_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env, running, artifact, budget, dependency = _d3_parent_slot_precheck_fixture(
        d3_full_fractal_micro_environment
    )
    actual = fr._d3_child_activation_precheck_material_v02(
        source_context=env["source"], topology=env["topology"],
        source_artifact=artifact, current_entry=running, node=env["nodes"][1],
        cell_input=env["cell_input"], cell_budget_before=budget,
        global_budget_before=budget, dependencies=(dependency,),
        indexes=_d3_indexes(env),
    )
    expected = _d3_expected_activation_material(
        env, running, artifact, budget, dependency
    )
    assert tuple(actual) == _D3_ACTIVATION_MATERIAL_KEYS_V035
    assert actual == expected
    assert canonical_json_bytes_v01(actual) == canonical_json_bytes_v01(expected)
    assert actual["profile_version"] == "v0.3.1"


def test_d3_child_activation_precheck_56_field_mutation_matrix_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env, running, artifact, budget, dependency = _d3_parent_slot_precheck_fixture(
        d3_full_fractal_micro_environment
    )
    actual = fr._d3_child_activation_precheck_material_v02(
        source_context=env["source"], topology=env["topology"],
        source_artifact=artifact, current_entry=running, node=env["nodes"][1],
        cell_input=env["cell_input"], cell_budget_before=budget,
        global_budget_before=budget, dependencies=(dependency,),
        indexes=_d3_indexes(env),
    )
    assert len(actual) == 56
    source_bound_family = {
        name: (
            "SOURCE_CONTEXT"
            if name in {
                "profile_version", "source_binding_id",
                "route_eligibility_artifact_id", "max_depth", "max_fan_out",
                "max_total_cells", "max_parallelism", "max_provider_calls",
                "parent_allowed_capability_ids", "child_allowed_capability_ids",
                "parent_forbidden_claims", "child_forbidden_claims",
                "parent_ttl_units", "child_ttl_units",
            }
            else "TOPOLOGY"
            if name in {
                "topology_id", "topology_seed_id", "topology_artifact_id",
                "parent_cell_id", "parent_scope_ref", "parent_slot_node_id",
                "parent_slot_assignment_id", "canonical_child_index",
                "planned_child_cell_id", "candidate_child_scope_ref",
                "parent_depth", "child_depth",
            }
            else "PARENT_CHAIN"
            if name.startswith("parent_slot_")
            else "LIVE_BUDGET"
            if name in {
                "parent_cell_budget_id", "global_budget_id",
                "parent_budget_state", "global_budget_state",
                "parent_budget_counters", "global_budget_counters",
                "occupied_admission_slots", "instantiated_sibling_count",
                "instantiated_total_cell_count",
            }
            else "DEPENDENCY"
            if name.startswith("dependency_")
            else "REVISE_HISTORY"
            if name.startswith("relevant_parent_slot_revise_")
            else "DERIVED_GATE"
        )
        for name in _D3_ACTIVATION_MATERIAL_KEYS_V035
    }
    assert tuple(source_bound_family) == _D3_ACTIVATION_MATERIAL_KEYS_V035
    assert set(source_bound_family.values()) == {
        "SOURCE_CONTEXT", "TOPOLOGY", "PARENT_CHAIN", "LIVE_BUDGET",
        "DEPENDENCY", "REVISE_HISTORY", "DERIVED_GATE",
    }
    for name, value in actual.items():
        alternate = (
            not value if type(value) is bool else
            value + 1 if type(value) is int else
            value + ":foreign" if type(value) is str else
            (*value, "ref:foreign")
        )
        mutated = {**actual, name: alternate}
        assert mutated != actual
        assert canonical_json_bytes_v01(mutated) != canonical_json_bytes_v01(actual)
        if type(value) is tuple and value:
            candidates = (
                value[:-1],
                (*value, value[-1]),
                tuple(reversed(value)),
                (*value[:-1], "ref:foreign"),
            )
            variants = tuple(variant for variant in candidates if variant != value)
            assert variants
            assert all(
                canonical_json_bytes_v01({**actual, name: variant})
                != canonical_json_bytes_v01(actual)
                for variant in variants
            )

    invalid_calls = (
        ("source_context_nested_artifact", {"source_context": replace(
            env["source"],
            route_eligibility_artifact=replace(
                env["source"].route_eligibility_artifact,
                transaction_id="transaction:foreign",
            ),
        )}),
        ("topology_identity", {"topology": replace(
            env["topology"], topology_id="frtopology_v02:" + "f" * 64
        )}),
        ("source_artifact", {"source_artifact": replace(
            artifact, transaction_id="transaction:foreign"
        )}),
        ("cell_budget_identity", {"cell_budget_before": replace(
            budget, budget_id="frbudget_v02:" + "f" * 64
        )}),
        ("dependency_absence", {"dependencies": ()}),
    )
    base_call = {
        "source_context": env["source"], "topology": env["topology"],
        "source_artifact": artifact, "current_entry": running,
        "node": env["nodes"][1], "cell_input": env["cell_input"],
        "cell_budget_before": budget, "global_budget_before": budget,
        "dependencies": (dependency,), "indexes": _d3_indexes(env),
    }
    for label, override in invalid_calls:
        try:
            fr._d3_child_activation_precheck_material_v02(
                **{**base_call, **override}
            )
        except ValueError:
            continue
        pytest.fail(f"{label} substitution was accepted")
    with pytest.raises(ValueError):
        _d3_eval(
            env, source_artifact=artifact, node=env["nodes"][1],
            current_entry=running, cell_input=env["cell_input"],
            cell_budget=budget, global_budget=budget,
            dependencies=(dependency,),
            queue_reason_codes=("g2d_required_child_failure",),
            observed_evidence_refs=("evidence:stale",),
        )


def test_d3_no_child_blocked_and_deadend_positive_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    blocked_env = _d3_clone_environment(d3_full_fractal_micro_environment)
    dependency, _ = _d3_complete_local_node(blocked_env, node_index=0)
    p1, p1_artifact, _ = _d3_start_node(
        blocked_env, node_index=1, dependencies=(dependency,)
    )
    p2, p2_artifact, _ = _d3_start_node(
        blocked_env, node_index=2, dependencies=(dependency,)
    )
    c1 = _d3_activate_child(
        blocked_env, slot_running=p1, slot_artifact=p1_artifact,
        dependency=dependency,
    )
    c1_ready, c1_ready_artifact = _d3_make_ready(
        blocked_env, current=c1["queues"][0], node=c1["nodes"][0],
        cell_input=c1["input"],
    )
    _c1_running, _c1_artifact, _cell_start, global_start = _d3_start_ready_entry(
        blocked_env, ready=c1_ready, ready_artifact=c1_ready_artifact,
        node=c1["nodes"][0], cell_input=c1["input"],
    )
    assert global_start.current_parallelism == 3
    blocked_validating, blocked_validating_artifact, blocked, blocked_artifact = (
        _d3_finish_no_child_gate(
            blocked_env, running=p2, running_artifact=p2_artifact,
            node=blocked_env["nodes"][2], dependency=dependency,
        )
    )
    assert blocked_validating.state == "VALIDATING"
    assert blocked.state == "BLOCKED"
    assert blocked.predecessor_queue_entry_id == blocked_validating.queue_entry_id
    assert blocked_artifact.parent_refs[1] == blocked_validating_artifact.artifact_id
    assert fr.validate_fractal_cell_queue_entry_v02(blocked).status == "PASS"

    deadend_env, running, artifact, budget, dependency = (
        _d3_parent_slot_precheck_fixture(d3_full_fractal_micro_environment)
    )
    indexes = _d3_indexes(deadend_env)
    ready = indexes["queue_by_id"][running.predecessor_queue_entry_id]
    observation = fr.build_fractal_revise_observation_v02(
        deadend_env["topology"], deadend_env["cell_input"], ready,
        fr.validate_fractal_cell_queue_entry_v02(ready),
        revision_index=2, newly_validated_evidence_count=0,
        newly_resolved_constraints_count=0, newly_accepted_outputs_count=0,
        newly_introduced_conflicts_count=0, consecutive_non_positive_count=2,
        max_consecutive_non_positive_count=2, cell_budget_before=budget,
        global_budget_before=budget,
    )
    deadend_env["revise_observations"] = (observation,)
    deadend_validating, deadend_validating_artifact, deadend, deadend_artifact = (
        _d3_finish_no_child_gate(
            deadend_env, running=running, running_artifact=artifact,
            node=deadend_env["nodes"][1], dependency=dependency,
        )
    )
    assert deadend_validating.state == "VALIDATING"
    assert deadend.state == "DEADEND"
    assert deadend.predecessor_queue_entry_id == deadend_validating.queue_entry_id
    assert deadend_artifact.parent_refs[1] == deadend_validating_artifact.artifact_id
    assert fr.validate_fractal_cell_queue_entry_v02(deadend).status == "PASS"


def test_d3_no_child_needs_user_unreachable_and_caller_labels_rejected_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env, running, artifact, budget, dependency = _d3_parent_slot_precheck_fixture(
        d3_full_fractal_micro_environment
    )
    with pytest.raises(ValueError):
        _d3_eval(
            env, source_artifact=artifact, node=env["nodes"][1],
            current_entry=running, cell_input=env["cell_input"],
            cell_budget=budget, global_budget=budget,
            dependencies=(dependency,),
            queue_reason_codes=("g2d_resolvable_input_needs_user",),
            observed_evidence_refs=("evidence:invented",),
        )
    synthetic_dependency = _d3_terminal_dependency_fixture(env)
    with pytest.raises(ValueError):
        fr._d3_child_activation_precheck_material_v02(
            source_context=env["source"], topology=env["topology"],
            source_artifact=artifact, current_entry=running,
            node=env["nodes"][1], cell_input=env["cell_input"],
            cell_budget_before=budget, global_budget_before=budget,
            dependencies=(synthetic_dependency,), indexes=_d3_indexes(env),
        )
    branch = _d3_clone_environment(env)
    branch["queue_log"] = (
        synthetic_dependency,
        *branch["queue_log"][1:],
    )
    with pytest.raises(ValueError):
        _d3_indexes(branch)
    with pytest.raises(ValueError):
        _d3_eval(
            env, source_artifact=artifact, node=env["nodes"][1],
            current_entry=running, cell_input=env["cell_input"],
            cell_budget=budget, global_budget=budget,
            dependencies=(dependency,),
            local_child_result=SimpleNamespace(outcome="NEEDS_USER"),
            local_child_result_artifact=env["topology_artifact"],
        )


def test_d3_historical_t06_origin_replay_ignores_later_live_head(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    running, running_artifact, start = _d3_start_node(env, node_index=0)
    node = env["nodes"][0]
    cell_input = env["cell_input"]
    material = fr._d3_local_observation_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        node=node,
        cell_input=cell_input,
        cell_budget_before=start,
        global_budget_before=start,
        dependencies=(),
        indexes=_d3_indexes(env),
    )
    t06 = _d3_eval(
        env,
        source_artifact=running_artifact,
        node=node,
        current_entry=running,
        cell_input=cell_input,
        cell_budget=start,
        global_budget=start,
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    assert isinstance(t06, TransitionDecisionV01)
    finish = _d3_budget_successor(
        env,
        start,
        event="FINISH_NODE",
        decision=t06,
        cell_input=cell_input,
    )
    validating, validating_artifact, _ = _d3_advance(
        env,
        current=running,
        current_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=start,
        global_budget_before=start,
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=(),
        round_entries=_d3_latest(env),
        queue_reason_codes=material["derived_queue_reason_codes"],
        observed_output_refs=material["derived_observed_output_refs"],
        observed_evidence_refs=material["derived_observed_evidence_refs"],
        advisory_refs=material["derived_advisory_refs"],
    )
    _running_2, _artifact_2, later_live_head = _d3_start_node(env, node_index=1)
    assert later_live_head != finish
    later_material = fr._d3_local_observation_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        node=node,
        cell_input=cell_input,
        cell_budget_before=later_live_head,
        global_budget_before=later_live_head,
        dependencies=(),
        indexes=_d3_indexes(env),
    )
    assert (
        later_material["derived_observed_output_refs"]
        != validating.observed_output_refs
    )
    terminal, _artifact, _decision = _d3_advance(
        env,
        current=validating,
        current_artifact=validating_artifact,
        node=node,
        cell_input=cell_input,
        cell_budget_before=finish,
        global_budget_before=finish,
        cell_budget_after=finish,
        global_budget_after=finish,
        dependencies=(),
        round_entries=_d3_latest(env),
        queue_reason_codes=validating.queue_reason_codes,
        observed_output_refs=validating.observed_output_refs,
        observed_evidence_refs=validating.observed_evidence_refs,
        advisory_refs=validating.advisory_refs,
    )
    assert terminal.observed_output_refs == validating.observed_output_refs
    assert terminal.observed_evidence_refs == env["cell_input"].evidence_refs


def test_d3_complete_prefix_rejects_missing_duplicate_reordered_and_foreign(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    _d3_indexes(env)
    mutations = (
        {"settled_budget_log": env["budget_log"][:-1]},
        {"settled_budget_log": (*env["budget_log"], env["budget_log"][-1])},
        {"settled_queue_entry_log": tuple(reversed(env["queue_log"]))},
        {"settled_queue_artifact_log": tuple(reversed(env["artifact_log"]))},
        {"settled_cell_inputs": (*env["cell_inputs"], env["cell_inputs"][0])},
        {"settled_validation_reports": env["validation_reports"][:-1]},
    )
    for mutation in mutations:
        with pytest.raises(ValueError):
            fr._d3_validate_settled_runtime_prefix_v02(
                topology=env["topology"],
                policy=env["source"].runtime_policy,
                source_context=env["source"],
                **_d3_prefix_kwargs(env, **mutation),
            )
    foreign_queue = _seal(replace(
        env["queue_log"][0],
        topology_id="frtopology_v02:" + "f" * 64,
    ))
    with pytest.raises(ValueError):
        fr._d3_validate_settled_runtime_prefix_v02(
            topology=env["topology"],
            policy=env["source"].runtime_policy,
            source_context=env["source"],
            **_d3_prefix_kwargs(
                env,
                settled_queue_entry_log=(foreign_queue, *env["queue_log"][1:]),
            ),
        )


def _d3_evaluate_backpressure(
    env: dict[str, object],
    *,
    source_context: fr.FractalRuntimeSourceContextV02 | None = None,
    admission_round: int = 1,
) -> fr.FractalBackpressureStateV02 | None:
    source = env["source"] if source_context is None else source_context
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    indexes = _d3_indexes(env)
    live_global = indexes["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL",
        env["topology"].root_cell_id,
    )]
    return fr.evaluate_fractal_backpressure_v02(
        source_context=source,
        topology=env["topology"],
        policy=env["source"].runtime_policy,
        global_budget=live_global,
        queue_entries=_d3_latest(env),
        admission_round=admission_round,
        **_d3_prefix_kwargs(env),
    )


def test_d3_function88_actual_source_context_positive_v035(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    assert _d3_evaluate_backpressure(env) is None


def test_d3_function88_source_context_substitution_matrix_v035(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    source = env["source"]
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    for source_field in fields(fr.FractalRuntimeSourceContextV02):
        component = getattr(source, source_field.name)
        component_fields = fields(type(component))
        mutable_field = next(
            item
            for item in component_fields
            if type(getattr(component, item.name))
            in {bool, int, str, tuple, type(None)}
            and item.name not in {"real_world_effects_count"}
        )
        foreign_component = replace(
            component,
            **{
                mutable_field.name: _same_type_alternate(
                    component,
                    mutable_field.name,
                )
            },
        )
        foreign_source = replace(
            source,
            **{source_field.name: foreign_component},
        )
        with pytest.raises(ValueError):
            _d3_evaluate_backpressure(
                env,
                source_context=foreign_source,
            )


def test_d3_function88_rejects_copied_and_constructed_pass_v035(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    reports = env["validation_reports"]
    assert isinstance(reports, tuple)
    copied = replace(
        reports[1],
        validation_report_id=reports[0].validation_report_id,
    )
    for mutated in (
        (reports[0], copied, *reports[2:]),
        tuple(reversed(reports)),
        reports[:-1],
        (*reports, reports[-1]),
    ):
        branch = _d3_clone_environment(env)
        branch["validation_reports"] = mutated
        with pytest.raises(ValueError):
            _d3_evaluate_backpressure(branch)
    artifact = env["artifact_log"][0]
    forged_artifact = replace(
        artifact,
        transaction_id=artifact.transaction_id + ":foreign",
    )
    branch = _d3_clone_environment(env)
    branch["artifact_log"] = (forged_artifact, *env["artifact_log"][1:])
    with pytest.raises(ValueError):
        _d3_evaluate_backpressure(branch)
    foreign_input = _seal(replace(
        env["cell_input"],
        evidence_refs=(*env["cell_input"].evidence_refs, "evidence:foreign"),
    ))
    branch = _d3_clone_environment(env)
    branch["cell_inputs"] = (foreign_input,)
    with pytest.raises(ValueError):
        _d3_evaluate_backpressure(branch)


def _d3_parent_return_eval(
    env: dict[str, object],
    **overrides: object,
) -> TransitionDecisionV01 | None:
    node = next(item for item in env["nodes"] if item.node_kind == "PARENT_RETURN")
    current = next(
        item
        for item in reversed(env["queue_log"])
        if item.cell_id == env["topology"].root_cell_id
        and item.node_id == node.node_id
    )
    artifact = next(
        artifact
        for entry, artifact in zip(
            reversed(env["queue_log"]),
            reversed(env["artifact_log"]),
            strict=True,
        )
        if entry.queue_entry_id == current.queue_entry_id
    )
    return _d3_eval(
        env,
        source_artifact=artifact,
        node=node,
        current_entry=current,
        cell_input=env["cell_input"],
        cell_budget=env["root_create"],
        global_budget=env["root_create"],
        **overrides,
    )


def test_d3_parent_return_wholly_absent_is_unavailable_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    assert _d3_parent_return_eval(env) is None


def test_d3_parent_return_future_family_fail_closed_127_mask_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    result, _artifact = _d3_child_result_fixture(env, outcome="COMPLETED", ordinal=31)
    partial = _fixture_family()[fr.FractalPartialFailureRecordV02]
    reports = env["validation_reports"]
    rows = (
        ("parent_return_pre_post_vv_terminal_queue_entries", (env["queues"][0],)),
        ("parent_return_child_results", (result,)),
        ("parent_return_partial_failures", (partial,)),
        ("parent_return_result_proposal", {"proposal_id": "proposal:test"}),
        ("parent_return_post_vv_report", {"vv_report_id": "vv:test"}),
        ("parent_return_gt_advisory_report", {"gt_report_id": "gt:test"}),
        ("parent_return_validation_reports", (reports[0],)),
    )
    for mask in range(1, 128):
        kwargs = {
            name: value
            for index, (name, value) in enumerate(rows)
            if mask & (1 << index)
        }
        with pytest.raises(ValueError, match="g2d_parent_return_invalid"):
            _d3_parent_return_eval(env, **kwargs)
    malformed = (
        {rows[0][0]: [env["queues"][0]]},
        {rows[1][0]: (env["queues"][0],)},
        {rows[2][0]: (result,)},
        {rows[3][0]: []},
        {rows[4][0]: "vv:test"},
        {rows[5][0]: ()},
        {rows[6][0]: (env["queues"][0],)},
    )
    for kwargs in malformed:
        with pytest.raises(ValueError, match="g2d_parent_return_invalid"):
            _d3_parent_return_eval(env, **kwargs)


def _d3_classifier_pair(
    env: dict[str, object],
    entry: fr.FractalCellQueueEntryV02,
) -> tuple[str, fr.FractalCellQueueEntryV02]:
    indexes = _d3_indexes(env)
    _cell, live_global = fr._d3_live_budget_heads_v02(
        topology=env["topology"],
        cell_id=env["topology"].root_cell_id,
        indexes=indexes,
    )
    material = fr._d3_scheduler_classification_v02(
        source_context=env["source"],
        topology=env["topology"],
        policy=env["source"].runtime_policy,
        global_budget=live_global,
        entries=env["queue_log"],
        indexes=indexes,
    )
    matches = tuple(
        item for item in material["classified"] if item[1] == entry
    )
    assert len(matches) == 1
    return matches[0]


@pytest.fixture(scope="module")
def d3_six_class_pairs(
    d3_mode_environments: dict[str, dict[str, object]],
) -> tuple[tuple[str, fr.FractalCellQueueEntryV02], ...]:
    pending_env = _d3_clone_environment(d3_mode_environments["memory_informed"])
    pending = pending_env["queues"][0]

    ready_env = _d3_clone_environment(d3_mode_environments["full_fractal"])
    ready, _ready_artifact = _d3_make_ready(
        ready_env,
        current=ready_env["queues"][0],
        node=ready_env["nodes"][0],
        cell_input=ready_env["cell_input"],
    )

    running_env = _d3_clone_environment(d3_mode_environments["full_semantic"])
    running, _running_artifact, _running_budget = _d3_start_node(
        running_env,
        node_index=0,
    )

    terminal_env = _d3_clone_environment(d3_mode_environments["cloud_llm"])
    terminal_running, terminal_running_artifact, _ = _d3_start_node(
        terminal_env,
        node_index=0,
    )
    terminal, _terminal_artifact, _ = _d3_finish_running_local(
        terminal_env,
        running=terminal_running,
        running_artifact=terminal_running_artifact,
        node=terminal_env["nodes"][0],
        cell_input=terminal_env["cell_input"],
    )

    revise_env = _d3_clone_environment(d3_mode_environments["local_slm"])
    revise_running, revise_running_artifact, _ = _d3_start_node(
        revise_env,
        node_index=0,
    )
    revise_entry, _revise_artifact, _ = _d3_finish_running_local(
        revise_env,
        running=revise_running,
        running_artifact=revise_running_artifact,
        node=revise_env["nodes"][0],
        cell_input=revise_env["cell_input"],
    )
    revise_indexes = _d3_indexes(revise_env)
    revise_cell, revise_global = fr._d3_live_budget_heads_v02(
        topology=revise_env["topology"],
        cell_id=revise_entry.cell_id,
        indexes=revise_indexes,
    )
    observation = fr.build_fractal_revise_observation_v02(
        revise_env["topology"],
        revise_env["cell_input"],
        revise_entry,
        fr.validate_fractal_cell_queue_entry_v02(revise_entry),
        revision_index=1,
        newly_validated_evidence_count=1,
        newly_resolved_constraints_count=0,
        newly_accepted_outputs_count=0,
        newly_introduced_conflicts_count=0,
        consecutive_non_positive_count=0,
        max_consecutive_non_positive_count=2,
        cell_budget_before=revise_cell,
        global_budget_before=revise_global,
    )
    revise_env["revise_observations"] = (observation,)

    deferred_env = _d3_clone_environment(d3_mode_environments["full_fractal"])
    dependency, _ = _d3_complete_local_node(deferred_env, node_index=0)
    p1, p1_artifact, _ = _d3_start_node(
        deferred_env, node_index=1, dependencies=(dependency,)
    )
    p2, p2_artifact, _ = _d3_start_node(
        deferred_env, node_index=2, dependencies=(dependency,)
    )
    c1 = _d3_activate_child(
        deferred_env, slot_running=p1, slot_artifact=p1_artifact,
        dependency=dependency,
    )
    c2 = _d3_activate_child(
        deferred_env, slot_running=p2, slot_artifact=p2_artifact,
        dependency=dependency,
    )
    _c1_ready, _ = _d3_make_ready(
        deferred_env,
        current=c1["queues"][0],
        node=c1["nodes"][0],
        cell_input=c1["input"],
    )
    deferred = c2["queues"][0]

    pairs = (
        _d3_classifier_pair(ready_env, ready),
        _d3_classifier_pair(running_env, running),
        _d3_classifier_pair(terminal_env, terminal),
        _d3_classifier_pair(revise_env, revise_entry),
        _d3_classifier_pair(pending_env, pending),
        _d3_classifier_pair(deferred_env, deferred),
    )
    assert tuple(item[0] for item in pairs) == fr._D3_STATE_CLASS_ORDER_V02
    assert len({(item[1].cell_id, item[1].node_id) for item in pairs}) == 6
    return pairs


def test_d3_exact_six_class_scheduler_order_v035(
    d3_six_class_pairs: tuple[tuple[str, fr.FractalCellQueueEntryV02], ...],
) -> None:
    assert fr._D3_STATE_CLASS_ORDER_V02 == (
        "READY", "RUNNING", "VALIDATING_TERMINAL", "VALIDATING_REVISE",
        "PENDING_READY", "PENDING_DEFERRED",
    )
    assert tuple(item[0] for item in d3_six_class_pairs) == (
        fr._D3_STATE_CLASS_ORDER_V02
    )


def test_d3_six_class_order_permutation_and_substitution_matrix_v035(
    d3_six_class_pairs: tuple[tuple[str, fr.FractalCellQueueEntryV02], ...],
) -> None:
    expected = fr._d3_order_classified_scheduler_entries_v02(
        d3_six_class_pairs
    )
    assert tuple(name for name, _entry in expected) == fr._D3_STATE_CLASS_ORDER_V02
    for permutation in permutations(d3_six_class_pairs):
        assert fr._d3_order_classified_scheduler_entries_v02(permutation) == expected
    with pytest.raises(ValueError, match="g2d_queue_order_mismatch"):
        fr._d3_order_classified_scheduler_entries_v02((expected[0], expected[0]))
    with pytest.raises(ValueError, match="g2d_queue_order_mismatch"):
        fr._d3_order_classified_scheduler_entries_v02(
            (("PENDING", expected[0][1]),)
        )
    with pytest.raises(ValueError, match="g2d_queue_order_mismatch"):
        fr._d3_order_classified_scheduler_entries_v02(
            (("RUNNING", expected[0][1]),)
        )


def test_d3_budget_axis_serialization_fork_rejection_and_bounds_v035(
    d3_full_semantic_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_semantic_environment)
    topology = env["topology"]
    policy = env["source"].runtime_policy
    root_create = env["root_create"]
    cell_input = env["cell_input"]
    t05 = fr._d3_transition_decision_v02(env["registry"], "t05")
    heads = [root_create]
    for _ in range(3):
        heads.append(_d3_budget_successor(
            env,
            heads[-1],
            event="START_NODE",
            decision=t05,
            cell_input=cell_input,
        ))
    budget_log = (*env["budget_log"], *heads[1:])
    indexes = fr._d3_validate_budget_log_v02(
        budget_log,
        topology=topology,
        policy=policy,
        source_context=env["source"],
    )
    assert tuple(item.current_parallelism for item in heads) == (0, 1, 2, 3)
    assert indexes["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL",
        topology.root_cell_id,
    )] == heads[-1]
    assert all(
        fr._d3_budget_is_ancestor_v02(
            root_create,
            item,
            budget_by_id=indexes["budget_by_id"],
        )
        for item in heads
    )
    assert heads[-1].current_parallelism == 3
    assert heads[-1].remaining_parallel_slots == 0
    with pytest.raises(ValueError, match="g2d_budget_overflow"):
        _d3_budget_successor(
            env,
            heads[-1],
            event="START_NODE",
            decision=t05,
            cell_input=cell_input,
        )
    fork = _d3_budget_successor(
        env,
        root_create,
        event="REVISE",
        decision=fr._d3_transition_decision_v02(env["registry"], "t07"),
        cell_input=cell_input,
    )
    with pytest.raises(ValueError, match="g2d_budget_predecessor_invalid"):
        fr._d3_validate_budget_log_v02(
            (*env["budget_log"], heads[1], fork),
            topology=topology,
            policy=policy,
            source_context=env["source"],
        )
    assert (
        policy.max_depth,
        policy.max_fan_out,
        policy.max_total_cells,
        policy.max_parallelism,
        policy.max_provider_calls,
    ) == (3, 4, 21, 3, 0)


def _d3_prior_postclosure_core(
    env: dict[str, object],
    state: fr.FractalBackpressureStateV02,
) -> dict[str, object]:
    indexes = _d3_indexes(env)
    closure_frontiers = indexes["backpressure_closure_frontier_by_id"]
    closure_frontier = closure_frontiers[state.backpressure_id]
    state_budget = indexes["budget_by_id"][state.global_budget_id]
    prior_states = tuple(
        item
        for item in env["backpressure_states"]
        if item.evaluated_round < state.evaluated_round
    )
    local_indexes = fr._d3_frontier_local_indexes_v02(
        source_context=env["source"],
        topology=env["topology"],
        policy=env["source"].runtime_policy,
        queue_entries=env["queue_log"],
        queue_artifacts=env["artifact_log"],
        queue_frontier=closure_frontier,
        global_budget=state_budget,
        complete_indexes=indexes,
        prior_states=prior_states,
        closure_frontiers=closure_frontiers,
    )
    assert len(local_indexes["queue_by_id"]) == closure_frontier + 1
    assert local_indexes["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL", env["topology"].root_cell_id,
    )] == state_budget
    return fr._d3_round_control_material_v02(
        source_context=env["source"],
        topology=env["topology"],
        policy=env["source"].runtime_policy,
        global_budget=state_budget,
        admission_round=state.evaluated_round,
        entries=env["queue_log"][: closure_frontier + 1],
        indexes=local_indexes,
        prior_backpressure_states=prior_states,
    )


def test_d3_s0_t03_postclosure_suppression_s1_no_spin_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    dependency, _ = _d3_complete_local_node(env, node_index=0)
    p1, p1_artifact, _ = _d3_start_node(
        env, node_index=1, dependencies=(dependency,)
    )
    p2, p2_artifact, _ = _d3_start_node(
        env, node_index=2, dependencies=(dependency,)
    )
    assert _d3_indexes(env)["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL", env["topology"].root_cell_id,
    )].current_parallelism == 2
    c1 = _d3_activate_child(
        env, slot_running=p1, slot_artifact=p1_artifact, dependency=dependency
    )
    c2 = _d3_activate_child(
        env, slot_running=p2, slot_artifact=p2_artifact, dependency=dependency
    )
    indexes = _d3_indexes(env)
    live_global = indexes["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL", env["topology"].root_cell_id,
    )]
    assert live_global.current_parallelism == 2
    r1_round_start = _d3_latest(env)
    c1_ready, c1_ready_artifact = _d3_make_ready(
        env, current=c1["queues"][0], node=c1["nodes"][0],
        cell_input=c1["input"], round_start_queue_entries=r1_round_start,
    )
    latest = _d3_latest(env)
    assert sum(item.state == "READY" for item in latest) == 1
    assert live_global.current_parallelism + 1 == 3
    s0 = _d3_evaluate_backpressure(
        env, admission_round=c1_ready.admission_round,
    )
    assert isinstance(s0, fr.FractalBackpressureStateV02)
    assert s0.deferred_queue_entry_ids == (c2["queues"][0].queue_entry_id,)
    env["backpressure_states"] = (s0,)
    before_t03 = len(env["queue_log"])
    c2_deferred, _c2_deferred_artifact = _d3_make_ready(
        env, current=c2["queues"][0], node=c2["nodes"][0],
        cell_input=c2["input"], backpressure_state=s0,
        round_start_queue_entries=r1_round_start,
    )
    assert c2_deferred.state == "PENDING"
    assert c2_deferred.queue_reason_codes == (
        "g2d_transition_backpressure_deferred",
    )
    assert len(env["queue_log"]) == before_t03 + 1
    assert len(env["artifact_log"]) == len(env["queue_log"])
    assert len(env["budget_log"]) == len(_d3_indexes(env)["budget_log"])
    assert c1_ready.admission_round == s0.evaluated_round
    assert c2_deferred.admission_round == s0.evaluated_round
    s0_core_before_r2 = _d3_prior_postclosure_core(env, s0)

    r2_round_start = _d3_latest(env)
    c1_running, c1_running_artifact, _c1_cell_start, c1_global_start = (
        _d3_start_ready_entry(
            env, ready=c1_ready, ready_artifact=c1_ready_artifact,
            node=c1["nodes"][0], cell_input=c1["input"],
            round_start_queue_entries=r2_round_start,
        )
    )
    assert c1_global_start.current_parallelism == 3
    s1 = _d3_evaluate_backpressure(
        env, admission_round=c1_running.admission_round,
    )
    assert isinstance(s1, fr.FractalBackpressureStateV02)
    assert s1 != s0
    assert s1.deferred_queue_entry_ids == (c2_deferred.queue_entry_id,)
    env["backpressure_states"] = (s0, s1)
    c2_deferred_2, _artifact_2 = _d3_make_ready(
        env, current=c2_deferred, node=c2["nodes"][0],
        cell_input=c2["input"], backpressure_state=s1,
        round_start_queue_entries=r2_round_start,
    )
    assert c2_deferred_2.predecessor_queue_entry_id == c2_deferred.queue_entry_id
    assert c1_running.admission_round == s1.evaluated_round
    assert c2_deferred_2.admission_round == s1.evaluated_round
    s0_core_after_r2 = _d3_prior_postclosure_core(env, s0)
    assert s0_core_after_r2["control_core_sha256"] == (
        s0_core_before_r2["control_core_sha256"]
    )
    assert canonical_json_bytes_v01(s0_core_after_r2["controlling_core"]) == (
        canonical_json_bytes_v01(s0_core_before_r2["controlling_core"])
    )
    s1_core_before_suppression = _d3_prior_postclosure_core(env, s1)
    queue_count = len(env["queue_log"])
    artifact_count = len(env["artifact_log"])
    report_count = len(env["validation_reports"])
    budget_count = len(env["budget_log"])
    assert _d3_evaluate_backpressure(env, admission_round=3) is None
    s1_core_after_suppression = _d3_prior_postclosure_core(env, s1)
    assert s1_core_after_suppression["control_core_sha256"] == (
        s1_core_before_suppression["control_core_sha256"]
    )
    assert (
        len(env["queue_log"]), len(env["artifact_log"]),
        len(env["validation_reports"]), len(env["budget_log"]),
    ) == (queue_count, artifact_count, report_count, budget_count)
    assert c2_deferred in env["queue_log"] and c2_deferred_2 in env["queue_log"]

    release_round_start = _d3_latest(env)
    _validating, _validating_artifact, released_global = _d3_finish_running_local(
        env, running=c1_running, running_artifact=c1_running_artifact,
        node=c1["nodes"][0], cell_input=c1["input"],
        round_start_queue_entries=release_round_start,
    )
    assert released_global.current_parallelism == 2
    later_round_start = _d3_latest(env)
    c2_ready, _ = _d3_make_ready(
        env, current=c2_deferred_2, node=c2["nodes"][0],
        cell_input=c2["input"], round_start_queue_entries=later_round_start,
    )
    assert c2_ready.state == "READY"
    assert sum(item.state == "READY" for item in _d3_latest(env)) == 1


def test_d3_activated_child_waits_for_exact_result_v035(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    dependency, _ = _d3_complete_local_node(env, node_index=0)
    p1, p1_artifact, _ = _d3_start_node(
        env, node_index=1, dependencies=(dependency,)
    )
    p2, _p2_artifact, _ = _d3_start_node(
        env, node_index=2, dependencies=(dependency,)
    )
    child = _d3_activate_child(
        env, slot_running=p1, slot_artifact=p1_artifact,
        dependency=dependency,
    )
    child_ready, child_ready_artifact = _d3_make_ready(
        env, current=child["queues"][0], node=child["nodes"][0],
        cell_input=child["input"],
    )
    _child_running, _child_artifact, _cell_start, global_start = (
        _d3_start_ready_entry(
            env, ready=child_ready, ready_artifact=child_ready_artifact,
            node=child["nodes"][0], cell_input=child["input"],
        )
    )
    assert global_start.current_parallelism == 3
    indexes = _d3_indexes(env)
    assert fr._d3_instantiated_child_v02(p1, indexes=indexes) is not None
    with pytest.raises(ValueError, match="g2d_child_slot_activation_invalid"):
        fr._d3_child_activation_precheck_material_v02(
            source_context=env["source"], topology=env["topology"],
            source_artifact=p1_artifact, current_entry=p1,
            node=env["nodes"][1], cell_input=env["cell_input"],
            cell_budget_before=global_start, global_budget_before=global_start,
            dependencies=(dependency,), indexes=indexes,
        )
    p1_anchor = indexes["budget_by_id"][p1.cell_budget_id]
    assert _d3_eval(
        env, source_artifact=p1_artifact, node=env["nodes"][1],
        current_entry=p1, cell_input=env["cell_input"],
        cell_budget=p1_anchor, global_budget=p1_anchor,
        dependencies=(dependency,),
    ) is None
    with pytest.raises(ValueError, match="g2d_child_slot_activation_invalid"):
        _d3_eval(
            env, source_artifact=p1_artifact, node=env["nodes"][1],
            current_entry=p1, cell_input=env["cell_input"],
            cell_budget=p1_anchor, global_budget=p1_anchor,
            dependencies=(dependency,),
            queue_reason_codes=("g2d_required_child_failure",),
            observed_evidence_refs=("evidence:forged",),
        )
    classified = fr._d3_scheduler_classification_v02(
        source_context=env["source"], topology=env["topology"],
        policy=env["source"].runtime_policy, global_budget=global_start,
        entries=env["queue_log"], indexes=indexes,
    )
    assert p1 not in tuple(item[1] for item in classified["classified"])
    assert p1 in classified["future_progress"]
    assert ("RUNNING", p2) in classified["classified"]
    assert p2.global_budget_id != global_start.budget_id
    with pytest.raises(ValueError, match="g2d_backpressure_invalid"):
        fr._d3_scheduler_classification_v02(
            source_context=env["source"], topology=env["topology"],
            policy=env["source"].runtime_policy,
            global_budget=indexes["budget_by_id"][p2.global_budget_id],
            entries=env["queue_log"], indexes=indexes,
        )


def test_d3_scope_input_queue_negative_and_d4_boundary(
    d3_cloud_llm_environment: dict[str, object],
) -> None:
    env = d3_cloud_llm_environment
    cell_input = env["cell_input"]
    topology = env["topology"]
    queues = env["queues"]
    artifacts = env["queue_artifacts"]
    assert isinstance(cell_input, fr.FractalCellInputV02)
    assert fr.validate_fractal_cell_input_against_sources_v02(
        _seal(replace(cell_input, evidence_refs=tuple(reversed(cell_input.evidence_refs)))),
        source_context=env["source"],
        topology=topology,
        topology_artifact=env["topology_artifact"],
        parent_input=None,
        parent_slot_artifact=None,
        scope_projection=None,
        cell_budget=env["root_create"],
        global_budget=env["root_create"],
        queue_entries=queues,
        queue_artifacts=artifacts,
        **_d3_prefix_kwargs(env),
    ).status == "FAIL_CLOSED"
    with pytest.raises(ValueError):
        fr.build_fractal_cell_input_from_queue_v02(
            source_context=env["source"],
            topology=topology,
            topology_artifact=env["topology_artifact"],
            cell_id=topology.root_cell_id,
            parent_cell_id=None,
            parent_input=None,
            parent_slot_artifact=None,
            scope_projection=None,
            cell_budget=env["root_create"],
            global_budget=env["root_create"],
            initial_queue_entries=tuple(reversed(queues)),
            initial_queue_artifacts=tuple(reversed(artifacts)),
            ordered_planned_child_cell_ids=(),
            **_d3_prefix_kwargs(env),
        )
    module_source = MODULE_PATH.read_text(encoding="utf-8")
    assert "import hedgehog.kernel\n" not in module_source
    assert "demo." not in module_source and "tests." not in module_source
    for token in ("provider_calls=0", "network_calls=0", "real_world_effects_count=0"):
        assert token in module_source
    for activated in (
        "build_fractal_cell_result_proposal_v02",
        "aggregate_fractal_runtime_report_v02",
        "run_fractal_runtime_v02",
        "validate_fractal_runtime_stage_bundle_v02",
    ):
        assert callable(getattr(fr, activated, None))
    package = importlib.import_module("hedgehog.kernel")
    assert hasattr(package, "admit_runtime_execution_topology_v02")


_D4_PUBLIC_FUNCTION_NAMES_V02 = (
    "build_fractal_runtime_execution_bundle_v02",
    "validate_fractal_runtime_execution_bundle_v02",
    "build_fractal_cell_result_proposal_v02",
    "validate_fractal_cell_result_proposal_v02",
    "validate_fractal_post_vv_report_v02",
    "validate_fractal_gt_advisory_v02",
    "evaluate_fractal_revise_observation_v02",
    "record_fractal_partial_failure_v02",
    "validate_fractal_cell_result_against_input_v02",
    "aggregate_fractal_runtime_report_v02",
    "run_fractal_runtime_v02",
    "validate_fractal_runtime_report_against_sources_v02",
    "project_fractal_cell_result_kernel_artifact_v02",
    "project_fractal_runtime_report_kernel_artifact_v02",
    "validate_fractal_runtime_stage_bundle_v02",
    "validate_fractal_runtime_abi_profile_v02",
    "evaluate_fractal_parent_return_transition_v02",
    "build_fractal_runtime_causal_consumption_refs_v02",
    "validate_fractal_runtime_causal_consumption_refs_v02",
    "validate_fractal_runtime_causal_counterfactual_v02",
)

_E4C001_PUBLIC_FUNCTION_NAMES_V02 = (
    "project_runtime_observed_work_binding_kernel_artifact_v02",
    "build_runtime_observed_work_context_v02",
    "validate_runtime_observed_work_context_v02",
    "runtime_observed_work_context_to_plain_data_v02",
    "validate_runtime_observed_work_context_against_sources_v02",
    "validate_runtime_observed_work_counterfactual_v02",
)

_E4C001_CORRECTED_SIGNATURE_NAMES_V02 = (
    "admit_runtime_execution_topology_v02",
    "advance_fractal_cell_queue_v02",
    "build_fractal_cell_input_from_queue_v02",
    "validate_fractal_cell_input_against_sources_v02",
    "evaluate_fractal_backpressure_v02",
    "project_fractal_cell_queue_entry_kernel_artifact_v02",
    "evaluate_fractal_runtime_state_transition_v02",
    "validate_fractal_runtime_stage_bundle_v02",
    "validate_fractal_runtime_abi_profile_v02",
    "build_fractal_runtime_causal_consumption_refs_v02",
    "validate_fractal_runtime_causal_consumption_refs_v02",
    "build_fractal_runtime_execution_bundle_v02",
    "run_fractal_runtime_v02",
)

_D4_TRANSITION_FUNCTION_NAMES_V02 = (
    "build_fractal_runtime_transition_registry_profile_v02",
    "validate_fractal_runtime_transition_registry_profile_v02",
    "fractal_runtime_transition_registry_profile_to_plain_dict_v02",
    "validate_fractal_runtime_transition_decision_v02",
    "fractal_runtime_transition_decision_to_plain_dict_v02",
    "rebuild_fractal_runtime_transition_decision_identity_v02",
)

_HISTORICAL_KERNEL_DUNDER_ALL_V02 = (
    "CanonicalArtifactRefV01",
    "ArtifactDependencyEdgeV01",
    "RootOwnershipBindingV01",
    "EvidenceClassBindingV01",
    "AuthorityClassBindingV01",
    "SealProfileV01",
    "ArtifactManifestV01",
    "SealVerificationResultV01",
    "ReplayVerificationResultV01",
    "build_default_seal_profile_v01",
    "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01",
    "build_canonical_artifact_ref_v01",
    "build_artifact_manifest_v01",
    "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01",
    "artifact_manifest_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "replay_verification_result_to_plain_dict_v01",
)


def _d4_bundle_artifacts(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> tuple[tuple[KernelArtifactV01, ...], tuple[KernelArtifactV01, ...], tuple[KernelArtifactV01, ...]]:
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


def _d4_cell_contract_material(
    bundle: fr.FractalRuntimeExecutionBundleV02,
    result_index: int,
) -> dict[str, object]:
    result = bundle.cell_results[result_index]
    cell_input = next(
        item for item in bundle.cell_inputs if item.cell_input_id == result.cell_input_id
    )
    queue_by_id = {item.queue_entry_id: item for item in bundle.queue_entries}
    terminal_entries = tuple(
        queue_by_id[item] for item in result.ordered_terminal_queue_entry_ids
    )
    _binding, _seed, _initial, topology_nodes = fr._d3_reconstruct_topology_parts_v02(
        bundle.source_context,
        bundle.topology,
    )
    projected = fr._d3_projected_nodes_v02(
        bundle.topology,
        topology_nodes,
        cell_depth=cell_input.cell_depth,
        parent_cell_id=cell_input.parent_cell_id,
    )
    post_position = next(
        index for index, node in enumerate(projected) if node.node_kind == "POST_VV"
    )
    result_by_id = {item.result_id: item for item in bundle.cell_results}
    child_results = tuple(result_by_id[item] for item in result.ordered_child_result_ids)
    partial_by_id = {
        item.partial_failure_id: item for item in bundle.partial_failures
    }
    partial_failures = tuple(partial_by_id[item] for item in result.partial_failure_ids)
    budget_by_id = {item.budget_id: item for item in bundle.budgets}
    return {
        "result": result,
        "cell_input": cell_input,
        "terminal_entries": terminal_entries,
        "pre_post_vv_terminal_queue_entries": terminal_entries[:post_position],
        "child_results": child_results,
        "partial_failures": partial_failures,
        "proposal": bundle.result_proposals[result_index],
        "post_vv_report": bundle.post_vv_reports[result_index],
        "gt_advisory_report": bundle.gt_advisory_reports[result_index],
        "allocated_budget": budget_by_id[result.allocated_cell_budget_id],
        "final_budget": budget_by_id[result.final_cell_budget_id],
        "global_budget": budget_by_id[result.global_budget_id],
    }


def _d4_validation_kwargs(
    bundle: fr.FractalRuntimeExecutionBundleV02,
) -> dict[str, object]:
    return {
        "source_context": bundle.source_context,
        "topology": bundle.topology,
        "topology_artifact": bundle.topology_artifact,
        "runtime_assignments": bundle.runtime_assignments,
        "queue_entries": bundle.queue_entries,
        "queue_artifacts": bundle.queue_artifacts,
        "cell_results": bundle.cell_results,
        "result_artifacts": bundle.result_artifacts,
        "runtime_trace": bundle.runtime_trace,
        "runtime_report": bundle.runtime_report,
        "report_artifact": bundle.report_artifact,
    }


def _d4_mutated_kernel_payload_artifact(
    artifact: KernelArtifactV01,
    *,
    pointer: str,
    replacement: object,
) -> KernelArtifactV01:
    plain = kernel_artifact_to_plain_dict_v01(artifact)
    payload = plain["payload"]
    assert isinstance(payload, dict)
    tokens = pointer.lstrip("/").split("/")
    cursor: object = payload
    for token in tokens[:-1]:
        if isinstance(cursor, dict):
            cursor = cursor[token]
        else:
            assert isinstance(cursor, list)
            cursor = cursor[int(token)]
    leaf = tokens[-1]
    if isinstance(cursor, dict):
        cursor[leaf] = replacement
    else:
        assert isinstance(cursor, list)
        cursor[int(leaf)] = replacement
    provisional = build_kernel_artifact_v01(
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
    identity_material = kernel_artifact_to_plain_dict_v01(provisional)
    identity_material.pop("artifact_id")
    prefixes = {
        "FractalCellQueueEntry": (
            "frabi_queue_v02:",
            "HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02",
        ),
        "FractalCellResult": (
            "frabi_result_v02:",
            "HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
        ),
    }
    prefix, domain = prefixes[artifact.artifact_type]
    return replace(
        provisional,
        artifact_id=prefix
        + domain_separated_sha256_hex_v01(
            domain=domain,
            payload=canonical_json_bytes_v01(identity_material),
        ),
    )


@pytest.fixture(scope="module")
def d4_full_fractal_source_context_v02() -> fr.FractalRuntimeSourceContextV02:
    source = _d2_g2c_family("full_fractal")["source"]
    assert isinstance(source, fr.FractalRuntimeSourceContextV02)
    assert fr.validate_fractal_runtime_source_context_v02(source).status == "PASS"
    return source


@pytest.fixture(scope="module")
def d4_complete_full_fractal_bundle(
    d4_full_fractal_source_context_v02: fr.FractalRuntimeSourceContextV02,
) -> dict[str, object]:
    source = d4_full_fractal_source_context_v02
    bundle, complete_report = fr.run_fractal_runtime_v02(source)
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02), complete_report
    assert complete_report.status == "PASS"
    assert complete_report.validation_target == "COMPLETE_PROFILE"
    stage_a, stage_b, stage_c = _d4_bundle_artifacts(bundle)
    return {
        "source": source,
        "bundle": bundle,
        "complete_report": complete_report,
        "stage_a": stage_a,
        "stage_b": stage_b,
        "stage_c": stage_c,
    }


def _e4c001_source_artifact_v02(
    bundle: fr.FractalRuntimeExecutionBundleV02,
    *,
    payload: dict[str, object],
    trace_ref: str,
    predecessor: KernelArtifactV01 | None = None,
    lifecycle_state: str = "VALIDATED",
    source_component: str = "continuous_delta_runtime_v01",
) -> KernelArtifactV01:
    route_plain = kernel_artifact_to_plain_dict_v01(
        bundle.source_context.route_eligibility_artifact
    )
    trace_refs = (trace_ref,) if predecessor is None else predecessor.trace_refs
    parent_refs = (
        ()
        if predecessor is None
        else (predecessor.artifact_id, *predecessor.parent_refs)
    )
    provisional = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id="g2dobservedsource_v02:" + "0" * 64,
        artifact_type="SemanticEvidence",
        schema_version="v1",
        transaction_id=bundle.topology.transaction_id,
        owner_root_id=bundle.topology.owning_root_id,
        source_component=source_component,
        authority_class="EVIDENCE_ONLY",
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=route_plain["time_envelope"],
    )
    material = kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    result = replace(
        provisional,
        artifact_id=(
            "g2dobservedsource_v02:"
            + domain_separated_sha256_hex_v01(
                domain="HEDGEHOG_G2D_E4C001_SOURCE_ARTIFACT_V02",
                payload=canonical_json_bytes_v01(material),
            )
        ),
    )
    assert validate_kernel_artifact_v01(result) == ()
    return result


@pytest.fixture(scope="module")
def e4c001_observed_work_family_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> dict[str, object]:
    baseline = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    child_inputs = tuple(
        item for item in baseline.cell_inputs if item.parent_cell_id is not None
    )
    assert len(child_inputs) == 2
    selected_input = child_inputs[-1]
    selected_node = next(
        item
        for item in baseline.topology_nodes
        if item.node_id == selected_input.ordered_node_ids[0]
    )
    payload_baseline = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "payload", "value": 0},
        trace_ref="trace:e4c001:payload",
    )
    payload_observed = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "payload", "value": 1},
        trace_ref="trace:e4c001:payload",
        predecessor=payload_baseline,
    )
    lifecycle_baseline = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "lifecycle", "value": "stable"},
        trace_ref="trace:e4c001:lifecycle",
    )
    lifecycle_observed = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "lifecycle", "value": "stable"},
        trace_ref="trace:e4c001:lifecycle",
        predecessor=lifecycle_baseline,
        lifecycle_state="ROOT_ACCEPTED",
    )
    direct_sources = (
        payload_baseline,
        payload_observed,
        lifecycle_baseline,
        lifecycle_observed,
    )

    def bindings_for_scope(
        execution_scope: str,
    ) -> tuple[KernelArtifactV01, ...]:
        kwargs = (
            {}
            if execution_scope == "SELECTIVE"
            else {
                "whole_run_escalation_reason": (
                    "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
                ),
                "whole_run_escalation_policy_id": None,
            }
        )
        return (
            fr.project_runtime_observed_work_binding_kernel_artifact_v02(
                baseline_execution_bundle=baseline,
                node=selected_node,
                cell_input=selected_input,
                baseline_source_artifact=payload_baseline,
                observed_source_artifact=payload_observed,
                changed_full_artifact_pointers=("/payload/value",),
                execution_scope=execution_scope,
                **kwargs,
            ),
            fr.project_runtime_observed_work_binding_kernel_artifact_v02(
                baseline_execution_bundle=baseline,
                node=selected_node,
                cell_input=selected_input,
                baseline_source_artifact=lifecycle_baseline,
                observed_source_artifact=lifecycle_observed,
                changed_full_artifact_pointers=("/lifecycle_state",),
                execution_scope=execution_scope,
                **kwargs,
            ),
        )

    selective_bindings = bindings_for_scope("SELECTIVE")
    selective_context = fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=tuple(reversed(direct_sources)),
        supporting_artifacts=(),
        binding_artifacts=tuple(reversed(selective_bindings)),
        execution_scope="SELECTIVE",
    )
    selective_bundle = fr._d4_run_runtime_v02(
        baseline.source_context,
        observed_work_context=selective_context,
    )
    assert fr.validate_fractal_runtime_execution_bundle_v02(
        selective_bundle
    ).status == "PASS"

    subset_whole_bindings = bindings_for_scope("WHOLE_RUN_ESCALATION")
    node_by_id = {item.node_id: item for item in baseline.topology_nodes}
    full_direct_sources: list[KernelArtifactV01] = []
    full_bindings: list[KernelArtifactV01] = []
    full_source_pairs: list[
        tuple[
            fr.FractalCellInputV02,
            fr.RuntimeTopologyNodeV02,
            KernelArtifactV01,
            KernelArtifactV01,
        ]
    ] = []
    source_index = 0
    for cell_input in baseline.cell_inputs:
        for node_id in cell_input.ordered_node_ids:
            node = node_by_id[node_id]
            source_index += 1
            source_baseline = _e4c001_source_artifact_v02(
                baseline,
                payload={
                    "source_class": "full_closure",
                    "source_index": source_index,
                    "value": 0,
                },
                trace_ref=f"trace:e4c001:full:{source_index}",
            )
            source_observed = _e4c001_source_artifact_v02(
                baseline,
                payload={
                    "source_class": "full_closure",
                    "source_index": source_index,
                    "value": 1,
                },
                trace_ref=f"trace:e4c001:full:{source_index}",
                predecessor=source_baseline,
            )
            full_direct_sources.extend((source_baseline, source_observed))
            full_source_pairs.append(
                (
                    cell_input,
                    node,
                    source_baseline,
                    source_observed,
                )
            )
            full_bindings.append(
                fr.project_runtime_observed_work_binding_kernel_artifact_v02(
                    baseline_execution_bundle=baseline,
                    node=node,
                    cell_input=cell_input,
                    baseline_source_artifact=source_baseline,
                    observed_source_artifact=source_observed,
                    changed_full_artifact_pointers=("/payload/value",),
                    execution_scope="WHOLE_RUN_ESCALATION",
                    whole_run_escalation_reason=(
                        "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
                    ),
                    whole_run_escalation_policy_id=None,
                )
            )
    whole_bindings = tuple(full_bindings)
    whole_context = fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=tuple(reversed(full_direct_sources)),
        supporting_artifacts=(),
        binding_artifacts=tuple(reversed(whole_bindings)),
        execution_scope="WHOLE_RUN_ESCALATION",
        whole_run_escalation_reason=(
            "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
        ),
        whole_run_escalation_policy_id=None,
    )
    return {
        "baseline": baseline,
        "selected_input": selected_input,
        "selected_node": selected_node,
        "payload_baseline": payload_baseline,
        "payload_observed": payload_observed,
        "lifecycle_baseline": lifecycle_baseline,
        "lifecycle_observed": lifecycle_observed,
        "direct_sources": direct_sources,
        "selective_bindings": selective_bindings,
        "selective_context": selective_context,
        "selective_bundle": selective_bundle,
        "subset_whole_bindings": subset_whole_bindings,
        "full_direct_sources": tuple(full_direct_sources),
        "full_source_pairs": tuple(full_source_pairs),
        "whole_bindings": whole_bindings,
        "whole_context": whole_context,
    }


def test_d4_exact_public_surface_and_facade_v02() -> None:
    public_functions = tuple(
        name
        for name, value in vars(fr).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == fr.__name__
    )
    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    rows = tuple(
        (number, signature)
        for number, signature in re.findall(
            r"^\|\s*(\d+)\s*\|\s*D[1-4]\s*\|\s*`([^`]+)`\s*\|$",
            preflight,
            re.MULTILINE,
        )
        if int(number) <= 110
    )
    assert len(rows) == 110
    historical_names = tuple(row.split("(", 1)[0] for _number, row in rows)
    assert public_functions[:110] == historical_names
    assert public_functions[90:110] == _D4_PUBLIC_FUNCTION_NAMES_V02
    assert public_functions[110:] == _E4C001_PUBLIC_FUNCTION_NAMES_V02
    module_tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    actual = {
        node.name: node
        for node in module_tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }
    d4_rows = tuple(row for row in rows if 91 <= int(row[0]) <= 110)
    assert tuple(signature.split("(", 1)[0] for _number, signature in d4_rows) == (
        _D4_PUBLIC_FUNCTION_NAMES_V02
    )
    for _number, signature in d4_rows:
        expected = ast.parse("def " + signature + ":\n pass").body[0]
        current = actual[signature.split("(", 1)[0]]
        if current.name in _E4C001_CORRECTED_SIGNATURE_NAMES_V02:
            assert current.args.kwonlyargs[-1].arg == "observed_work_context"
            assert ast.unparse(current.args.kwonlyargs[-1].annotation) == (
                "RuntimeObservedWorkContextV02 | None"
            )
            assert isinstance(current.args.kw_defaults[-1], ast.Constant)
            assert current.args.kw_defaults[-1].value is None
            historical_args = ast.arguments(
                posonlyargs=current.args.posonlyargs,
                args=current.args.args,
                vararg=current.args.vararg,
                kwonlyargs=current.args.kwonlyargs[:-1],
                kw_defaults=current.args.kw_defaults[:-1],
                kwarg=current.args.kwarg,
                defaults=current.args.defaults,
            )
            assert ast.dump(historical_args, include_attributes=False) == ast.dump(
                expected.args,
                include_attributes=False,
            )
        else:
            assert ast.dump(current.args, include_attributes=False) == ast.dump(
                expected.args,
                include_attributes=False,
            )
        assert ast.dump(current.returns, include_attributes=False) == ast.dump(
            expected.returns,
            include_attributes=False,
        )
    for name in public_functions:
        current = actual[name]
        assert not any(
            isinstance(item, (ast.Pass, ast.AsyncFunctionDef))
            or (
                isinstance(item, ast.Raise)
                and isinstance(item.exc, ast.Call)
                and getattr(item.exc.func, "id", None) == "NotImplementedError"
            )
            for item in ast.walk(current)
        )
    package = importlib.import_module("hedgehog.kernel")
    g2d_names = tuple(item.__name__ for item in fr.G2D_TYPES_V02) + public_functions
    assert len(g2d_names) == 137 and len(set(g2d_names)) == 137
    assert fr.__all__ == g2d_names
    for name in g2d_names:
        assert getattr(package, name) is getattr(fr, name)
    for name in _D4_TRANSITION_FUNCTION_NAMES_V02:
        assert getattr(package, name) is getattr(transition_registry, name)
    assert len(set((*g2d_names, *_D4_TRANSITION_FUNCTION_NAMES_V02))) == 143
    assert package.__all__ == _HISTORICAL_KERNEL_DUNDER_ALL_V02
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert fr.TOTAL_G2D_PUBLIC_FUNCTION_COUNT == 122
    assert fr.DIRECT_PACKAGE_G2D_ATTRIBUTE_COUNT == 143


def test_d4_revise_retry_and_no_progress_v02(
    d3_full_fractal_micro_environment: dict[str, object],
) -> None:
    env = _d3_clone_environment(d3_full_fractal_micro_environment)
    topology = env["topology"]
    cell_input = env["cell_input"]
    nodes = env["nodes"]
    assert isinstance(topology, fr.RuntimeExecutionTopologyV02)
    assert isinstance(cell_input, fr.FractalCellInputV02)
    assert isinstance(nodes, tuple)
    node = nodes[0]
    assert isinstance(node, fr.RuntimeTopologyNodeV02)
    assert node.node_kind in fr._D3_LOCAL_NODE_KINDS_V02

    running, running_artifact, _start_budget = _d3_start_node(
        env,
        node_index=0,
    )
    validating, validating_artifact, _finish_global = _d3_finish_running_local(
        env,
        running=running,
        running_artifact=running_artifact,
        node=node,
        cell_input=cell_input,
    )
    indexes = _d3_indexes(env)
    cell_budget = indexes["budget_by_id"][validating.cell_budget_id]
    global_budget = indexes["budget_by_id"][validating.global_budget_id]
    queue_validation = fr.validate_fractal_cell_queue_entry_v02(validating)
    assert queue_validation.status == "PASS"
    observation = fr.evaluate_fractal_revise_observation_v02(
        topology=topology,
        cell_input=cell_input,
        queue_entry=validating,
        validation_report=queue_validation,
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        revision_index=cell_input.initial_revise_count,
        newly_validated_evidence_count=0,
        newly_resolved_constraints_count=0,
        newly_accepted_outputs_count=0,
        newly_introduced_conflicts_count=0,
        consecutive_non_positive_count=cell_budget.max_revise_count,
    )
    observation_report = fr.validate_fractal_revise_observation_v02(observation)
    assert observation_report.status == "PASS"
    assert observation_report.validation_target == "FractalReviseObservationV02"
    assert observation_report.validated_object_id == observation.observation_id
    assert observation.revise_eligible is False
    assert observation.derived_terminal_state == "DEADEND"
    assert observation.reason_codes == ("g2d_no_progress_deadend",)
    assert observation.trace_refs[-3:-1] == (
        cell_budget.budget_id,
        global_budget.budget_id,
    )
    assert observation.authority_created is False
    assert observation.real_world_effects_count == 0
    assert env["revise_observations"] == ()

    def evaluate_transition(
        branch: dict[str, object],
        *,
        revise: fr.FractalReviseObservationV02 | None = observation,
        report: fr.FractalRuntimeValidationReportV02 | None = observation_report,
        source_artifact: KernelArtifactV01 = validating_artifact,
        selected_node: fr.RuntimeTopologyNodeV02 = node,
        selected_cell_budget: fr.FractalRuntimeBudgetV02 = cell_budget,
        selected_global_budget: fr.FractalRuntimeBudgetV02 = global_budget,
        queue_reason_codes: tuple[str, ...] = validating.queue_reason_codes,
        observed_output_refs: tuple[str, ...] = validating.observed_output_refs,
        observed_evidence_refs: tuple[str, ...] = validating.observed_evidence_refs,
        advisory_refs: tuple[str, ...] = validating.advisory_refs,
    ) -> TransitionDecisionV01 | None:
        return fr.evaluate_fractal_runtime_state_transition_v02(
            source_context=branch["source"],
            topology=branch["topology"],
            source_artifact=source_artifact,
            current_entry=validating,
            node=selected_node,
            cell_input=cell_input,
            cell_id=validating.cell_id,
            parent_cell_id=validating.parent_cell_id,
            planned_child_cell_id=validating.planned_child_cell_id,
            cell_depth=validating.cell_depth,
            scope_ref=validating.scope_ref,
            cell_budget_before=selected_cell_budget,
            global_budget_before=selected_global_budget,
            dependencies=(),
            queue_reason_codes=queue_reason_codes,
            observed_output_refs=observed_output_refs,
            observed_evidence_refs=observed_evidence_refs,
            advisory_refs=advisory_refs,
            local_child_result=None,
            local_child_result_artifact=None,
            validation_report=report,
            parent_return_pre_post_vv_terminal_queue_entries=(),
            parent_return_child_results=(),
            parent_return_partial_failures=(),
            parent_return_result_proposal=None,
            parent_return_post_vv_report=None,
            parent_return_gt_advisory_report=None,
            parent_return_validation_reports=(),
            revise_observation=revise,
            backpressure_state=None,
            transition_registry=branch["registry"],
            **_d3_prefix_kwargs(branch),
        )

    def advance_transition(
        branch: dict[str, object],
        decision: TransitionDecisionV01,
    ) -> tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]:
        queue_log = branch["queue_log"]
        artifact_log = branch["artifact_log"]
        reports = branch["validation_reports"]
        assert isinstance(queue_log, tuple)
        assert isinstance(artifact_log, tuple)
        assert isinstance(reports, tuple)
        target = fr.advance_fractal_cell_queue_v02(
            source_context=branch["source"],
            topology=branch["topology"],
            current_entry=validating,
            node=node,
            cell_input=cell_input,
            transition_decision=decision,
            cell_budget_after=cell_budget,
            global_budget_after=global_budget,
            dependencies=(),
            local_child_result=None,
            local_child_result_artifact=None,
            cell_instantiation_order=tuple(
                item.cell_id for item in branch["cell_inputs"]
            ),
            projected_node_ids=cell_input.ordered_node_ids,
            round_start_queue_entries=_d3_latest(branch),
            queue_reason_codes=validating.queue_reason_codes,
            observed_output_refs=validating.observed_output_refs,
            observed_evidence_refs=validating.observed_evidence_refs,
            advisory_refs=validating.advisory_refs,
            **_d3_prefix_kwargs(branch),
        )
        artifact = fr.project_fractal_cell_queue_entry_kernel_artifact_v02(
            target,
            topology_artifact=branch["topology_artifact"],
            predecessor_artifact=validating_artifact,
            activation_parent_artifact=None,
            local_child_result_artifact=None,
            source_context=branch["source"],
            **_d3_prefix_kwargs(
                branch,
                settled_queue_entry_log=queue_log + (target,),
                settled_validation_reports=reports,
            ),
        )
        branch["queue_log"] = queue_log + (target,)
        branch["artifact_log"] = artifact_log + (artifact,)
        branch["validation_reports"] = _d3_retained_reports(
            branch,
            branch["queue_log"],
        )
        return target, artifact

    base_branch = _d3_clone_environment(env)
    base_branch["revise_observations"] = (observation,)
    budget_log_before = base_branch["budget_log"]
    decision = evaluate_transition(base_branch)
    repeated_decision = evaluate_transition(base_branch)
    assert isinstance(decision, TransitionDecisionV01)
    assert decision == repeated_decision
    assert canonical_json_bytes_v01(
        transition_registry.fractal_runtime_transition_decision_to_plain_dict_v02(
            decision
        )
    ) == canonical_json_bytes_v01(
        transition_registry.fractal_runtime_transition_decision_to_plain_dict_v02(
            repeated_decision
        )
    )
    assert decision.rule_id == "g2d_t12_validating_to_deadend"
    assert decision.decision == "RETURN_TO_ROOT"
    assert decision.reason_code == "g2d_transition_deadend_recorded"

    first_branch = _d3_clone_environment(base_branch)
    repeated_branch = _d3_clone_environment(base_branch)
    terminal, terminal_artifact = advance_transition(first_branch, decision)
    repeated_terminal, repeated_artifact = advance_transition(
        repeated_branch,
        repeated_decision,
    )
    assert terminal == repeated_terminal
    assert terminal_artifact == repeated_artifact
    assert canonical_json_bytes_v01(
        fr.fractal_cell_queue_entry_to_plain_data_v02(terminal)
    ) == canonical_json_bytes_v01(
        fr.fractal_cell_queue_entry_to_plain_data_v02(repeated_terminal)
    )
    assert canonical_json_bytes_v01(
        kernel_artifact_to_plain_dict_v01(terminal_artifact)
    ) == canonical_json_bytes_v01(
        kernel_artifact_to_plain_dict_v01(repeated_artifact)
    )
    assert terminal.state == "DEADEND"
    assert terminal.prior_state == "VALIDATING"
    assert terminal.predecessor_queue_entry_id == validating.queue_entry_id
    assert terminal.transition_decision_id == decision.decision_id
    assert terminal.queue_reason_codes == validating.queue_reason_codes
    assert terminal.observed_output_refs == validating.observed_output_refs
    assert terminal.observed_evidence_refs == validating.observed_evidence_refs
    assert terminal.advisory_refs == validating.advisory_refs
    assert terminal.cell_budget_id == validating.cell_budget_id
    assert terminal.global_budget_id == validating.global_budget_id
    assert terminal_artifact.parent_refs[:2] == (
        first_branch["topology_artifact"].artifact_id,
        validating_artifact.artifact_id,
    )
    assert validate_kernel_artifact_v01(terminal_artifact) == ()
    assert fr.validate_fractal_cell_queue_entry_v02(terminal).status == "PASS"
    assert transition_registry.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=first_branch["registry"],
        source_artifact=validating_artifact,
        target_artifact=terminal_artifact,
    ) == ()
    terminal_indexes = _d3_indexes(first_branch)
    assert terminal_indexes["latest_by_key"][(terminal.cell_id, terminal.node_id)] == terminal
    assert terminal_indexes["artifact_by_queue_id"][terminal.queue_entry_id] == terminal_artifact
    assert terminal_indexes["revise_by_id"] == {
        observation.observation_id: observation
    }
    assert first_branch["budget_log"] == budget_log_before
    assert repeated_branch["budget_log"] == budget_log_before
    assert terminal.authority_created is False
    assert terminal.permission_created is False
    assert terminal.final_output_created is False
    assert terminal.drs_write_created is False
    assert terminal.real_world_effects_count == 0
    assert "g2d_no_progress_deadend" not in terminal.queue_reason_codes
    assert observation.reason_codes == ("g2d_no_progress_deadend",)

    with pytest.raises(ValueError, match="g2d_terminal_queue_reentry_forbidden"):
        fr.evaluate_fractal_runtime_state_transition_v02(
            source_context=first_branch["source"],
            topology=first_branch["topology"],
            source_artifact=terminal_artifact,
            current_entry=terminal,
            node=node,
            cell_input=cell_input,
            cell_id=terminal.cell_id,
            parent_cell_id=terminal.parent_cell_id,
            planned_child_cell_id=terminal.planned_child_cell_id,
            cell_depth=terminal.cell_depth,
            scope_ref=terminal.scope_ref,
            cell_budget_before=cell_budget,
            global_budget_before=global_budget,
            dependencies=(),
            queue_reason_codes=terminal.queue_reason_codes,
            observed_output_refs=terminal.observed_output_refs,
            observed_evidence_refs=terminal.observed_evidence_refs,
            advisory_refs=terminal.advisory_refs,
            local_child_result=None,
            local_child_result_artifact=None,
            validation_report=None,
            parent_return_pre_post_vv_terminal_queue_entries=(),
            parent_return_child_results=(),
            parent_return_partial_failures=(),
            parent_return_result_proposal=None,
            parent_return_post_vv_report=None,
            parent_return_gt_advisory_report=None,
            parent_return_validation_reports=(),
            revise_observation=None,
            backpressure_state=None,
            transition_registry=first_branch["registry"],
            **_d3_prefix_kwargs(first_branch),
        )

    ordinary_branch = _d3_clone_environment(env)
    ordinary_decision = evaluate_transition(
        ordinary_branch,
        revise=None,
        report=None,
    )
    assert isinstance(ordinary_decision, TransitionDecisionV01)
    assert ordinary_decision.rule_id == "g2d_t08_validating_to_completed"
    ordinary_terminal, _ordinary_artifact = advance_transition(
        ordinary_branch,
        ordinary_decision,
    )
    assert ordinary_terminal.state == "COMPLETED"
    assert ordinary_terminal.queue_reason_codes == validating.queue_reason_codes
    assert ordinary_branch["budget_log"] == budget_log_before

    eligible = fr.evaluate_fractal_revise_observation_v02(
        topology=topology,
        cell_input=cell_input,
        queue_entry=validating,
        validation_report=queue_validation,
        cell_budget_before=cell_budget,
        global_budget_before=global_budget,
        revision_index=cell_input.initial_revise_count,
        newly_validated_evidence_count=1,
        newly_resolved_constraints_count=0,
        newly_accepted_outputs_count=0,
        newly_introduced_conflicts_count=0,
        consecutive_non_positive_count=0,
    )
    eligible_report = fr.validate_fractal_revise_observation_v02(eligible)
    eligible_branch = _d3_clone_environment(env)
    eligible_branch["revise_observations"] = (eligible,)
    eligible_decision = evaluate_transition(
        eligible_branch,
        revise=eligible,
        report=eligible_report,
        queue_reason_codes=(),
        observed_output_refs=(),
        observed_evidence_refs=(),
        advisory_refs=(),
    )
    assert isinstance(eligible_decision, TransitionDecisionV01)
    assert eligible.revise_eligible is True
    assert eligible_decision.rule_id == "g2d_t07_validating_to_revise"
    assert eligible_decision.rule_id != decision.rule_id

    def assert_revise_rejected(candidate: fr.FractalReviseObservationV02) -> None:
        branch = _d3_clone_environment(env)
        branch["revise_observations"] = (candidate,)
        with pytest.raises(ValueError):
            evaluate_transition(
                branch,
                revise=candidate,
                report=fr.validate_fractal_revise_observation_v02(candidate),
            )

    manually_forged = replace(
        observation,
        observation_id="frrevise_v02:" + "f" * 64,
    )
    invalid_observations = (
        manually_forged,
        _seal(replace(observation, derived_terminal_state=None)),
        _seal(replace(observation, reason_codes=("g2d_revise_progress_valid",))),
        _seal(replace(observation, revision_index=observation.revision_index + 1)),
        _seal(replace(observation, cell_id="frrootcell_v02:" + "f" * 64)),
        _seal(replace(observation, queue_entry_id="frqueue_v02:" + "f" * 64)),
        _seal(replace(observation, cell_budget_before_id="frbudget_v02:" + "e" * 64)),
        _seal(replace(observation, global_budget_before_id="frbudget_v02:" + "d" * 64)),
        _seal(
            replace(
                observation,
                newly_validated_evidence_count=1,
            )
        ),
    )
    for candidate in invalid_observations:
        assert isinstance(candidate, fr.FractalReviseObservationV02)
        assert_revise_rejected(candidate)

    with pytest.raises(ValueError):
        evaluate_transition(_d3_clone_environment(env))
    stale_report_branch = _d3_clone_environment(base_branch)
    with pytest.raises(ValueError):
        evaluate_transition(stale_report_branch, report=queue_validation)
    with pytest.raises(ValueError):
        evaluate_transition(
            base_branch,
            selected_cell_budget=env["root_create"],
        )
    with pytest.raises(ValueError):
        evaluate_transition(
            base_branch,
            selected_global_budget=env["root_create"],
        )
    non_local_node = next(item for item in nodes if item.node_kind == "POST_VV")
    with pytest.raises(ValueError):
        evaluate_transition(base_branch, selected_node=non_local_node)

    for field_name, changed in (
        (
            "queue_reason_codes",
            (*validating.queue_reason_codes, "g2d_no_progress_deadend"),
        ),
        ("observed_output_refs", (*validating.observed_output_refs, "output:foreign")),
        (
            "observed_evidence_refs",
            (*validating.observed_evidence_refs, "evidence:foreign"),
        ),
        ("advisory_refs", (*validating.advisory_refs, "advisory:foreign")),
    ):
        with pytest.raises(ValueError):
            evaluate_transition(base_branch, **{field_name: changed})

    wrong_origin_branch = _d3_clone_environment(base_branch)
    queue_log = wrong_origin_branch["queue_log"]
    running_index = queue_log.index(running)
    wrong_running = _seal(
        replace(
            running,
            observed_evidence_refs=(*running.observed_evidence_refs, "evidence:foreign"),
        )
    )
    wrong_origin_branch["queue_log"] = (
        *queue_log[:running_index],
        wrong_running,
        *queue_log[running_index + 1 :],
    )
    with pytest.raises(ValueError):
        evaluate_transition(wrong_origin_branch)

    budget_attack = _d3_clone_environment(base_branch)
    budget_successor = _d3_budget_successor(
        budget_attack,
        cell_budget,
        event="REVISE",
        decision=eligible_decision,
        cell_input=cell_input,
    )
    budget_attack["budget_log"] = (*budget_attack["budget_log"], budget_successor)
    with pytest.raises(ValueError, match="g2d_budget_event_pair_mismatch"):
        fr.advance_fractal_cell_queue_v02(
            source_context=budget_attack["source"],
            topology=budget_attack["topology"],
            current_entry=validating,
            node=node,
            cell_input=cell_input,
            transition_decision=decision,
            cell_budget_after=budget_successor,
            global_budget_after=budget_successor,
            dependencies=(),
            local_child_result=None,
            local_child_result_artifact=None,
            cell_instantiation_order=tuple(
                item.cell_id for item in budget_attack["cell_inputs"]
            ),
            projected_node_ids=cell_input.ordered_node_ids,
            round_start_queue_entries=_d3_latest(budget_attack),
            queue_reason_codes=validating.queue_reason_codes,
            observed_output_refs=validating.observed_output_refs,
            observed_evidence_refs=validating.observed_evidence_refs,
            advisory_refs=validating.advisory_refs,
            **_d3_prefix_kwargs(budget_attack),
        )

    with pytest.raises(ValueError, match="g2d_revise_observation_invalid"):
        fr.evaluate_fractal_revise_observation_v02(
            topology=topology,
            cell_input=cell_input,
            queue_entry=validating,
            validation_report=queue_validation,
            cell_budget_before=cell_budget,
            global_budget_before=global_budget,
            revision_index=validating.snapshot_sequence + 1,
            newly_validated_evidence_count=0,
            newly_resolved_constraints_count=0,
            newly_accepted_outputs_count=0,
            newly_introduced_conflicts_count=0,
            consecutive_non_positive_count=0,
        )


def test_d4_partial_failure_and_parent_return_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    result_ids = {item.result_id for item in bundle.cell_results}
    assert all(item.child_result_id in result_ids for item in bundle.partial_failures)
    assert all(item.retry_eligible is False for item in bundle.partial_failures)
    root = bundle.cell_results[-1]
    assert root.ordered_child_result_ids == tuple(
        item.result_id for item in bundle.cell_results if item.parent_cell_id == root.cell_id
    )
    parent_return_nodes = {
        item.node_id for item in bundle.topology_nodes if item.node_kind == "PARENT_RETURN"
    }
    chains = tuple(
        item
        for item in bundle.queue_entries
        if item.node_id in parent_return_nodes
    )
    assert {item.state for item in chains} >= {"PENDING", "READY", "RUNNING", "VALIDATING", "COMPLETED"}
    assert all(
        item.advisory_refs
        for item in chains
        if item.state in {"VALIDATING", "COMPLETED"}
    )
    node_by_id = {item.node_id: item for item in bundle.topology_nodes}
    queue_artifact_by_entry_id = {
        _kernel_payload(artifact)["queue_entry_id"]: artifact
        for artifact in bundle.queue_artifacts
    }
    for result, proposal in zip(
        bundle.cell_results,
        bundle.result_proposals,
        strict=True,
    ):
        if result.parent_cell_id is None:
            continue
        initial = next(
            item for item in bundle.queue_entries
            if item.cell_id == result.cell_id
            and item.predecessor_queue_entry_id is None
        )
        activation_parent_id = queue_artifact_by_entry_id[
            initial.queue_entry_id
        ].parent_refs[1]
        local_terminal = next(
            item for item in bundle.queue_entries
            if item.cell_id == result.cell_id
            and node_by_id[item.node_id].node_kind == "SEMANTIC_ACTOR"
            and item.state in fr._D3_TERMINAL_STATES_V02
        )
        assert local_terminal.observed_evidence_refs.count(activation_parent_id) == 1
        proposal_evidence = tuple(proposal["result_payload"]["evidence_refs"])
        assert activation_parent_id not in proposal_evidence
        parent_return_observations = tuple(
            item for item in chains
            if item.cell_id == result.cell_id
            and item.state in {"VALIDATING", *fr._D3_TERMINAL_STATES_V02}
        )
        assert len(parent_return_observations) == 2
        assert all(
            item.observed_evidence_refs == proposal_evidence
            for item in parent_return_observations
        )
        assert all(
            activation_parent_id not in item.observed_evidence_refs
            and len(queue_artifact_by_entry_id[item.queue_entry_id].trace_refs)
            == len(set(queue_artifact_by_entry_id[item.queue_entry_id].trace_refs))
            for item in parent_return_observations
        )
    child = bundle.cell_results[0]
    parent_input = next(item for item in bundle.cell_inputs if item.cell_id == child.parent_cell_id)
    budget_by_id = {item.budget_id: item for item in bundle.budgets}
    with pytest.raises(ValueError, match="g2d_success_laundering_forbidden"):
        fr.record_fractal_partial_failure_v02(
            topology=bundle.topology,
            parent_input=parent_input,
            child_result=child,
            failure_stage="CELL_RESULT_PRECONDITIONS",
            reason_codes=("g2d_required_child_failure",),
            source_reason_codes=(),
            evidence_refs=child.evidence_refs,
            allocated_cell_budget=budget_by_id[child.allocated_cell_budget_id],
            final_cell_budget=budget_by_id[child.final_cell_budget_id],
            global_budget=budget_by_id[child.global_budget_id],
            required_child=True,
            sibling_independent=True,
        )


def test_d4_transition_abi_facade_and_stage_bundles_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    for stage, artifacts in zip(
        ("STAGE_D_A", "STAGE_D_B", "STAGE_D_C"),
        (
            d4_complete_full_fractal_bundle["stage_a"],
            d4_complete_full_fractal_bundle["stage_b"],
            d4_complete_full_fractal_bundle["stage_c"],
        ),
        strict=True,
    ):
        report = fr.validate_fractal_runtime_stage_bundle_v02(
            stage=stage,
            artifacts=artifacts,
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
        assert report.status == "PASS"
    assert fr.validate_fractal_runtime_abi_profile_v02(
        d4_complete_full_fractal_bundle["stage_c"],
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
    ).status == "PASS"
    assert bundle.transition_decisions[-1].rule_id.endswith("t13_completed_to_parent_return")


def test_d4_causal_consumption_and_complete_profile_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    report = fr.validate_fractal_runtime_causal_consumption_refs_v02(
        bundle.causal_consumption_refs,
        **_d4_validation_kwargs(bundle),
        stage_d_c_artifacts=d4_complete_full_fractal_bundle["stage_c"],
    )
    assert report.status == "PASS"
    effects = tuple(item.decision_effect for item in bundle.causal_consumption_refs)
    assert effects[:3] == ("TOPOLOGY_SELECTION", "TOPOLOGY_SCOPE", "TOPOLOGY_SELECTION")
    child_initial_pairs = tuple(
        (entry, artifact)
        for entry, artifact in zip(
            bundle.queue_entries,
            bundle.queue_artifacts,
            strict=True,
        )
        if entry.parent_cell_id is not None
        and entry.predecessor_queue_entry_id is None
    )
    first_child_initial_pairs: list[
        tuple[fr.FractalCellQueueEntryV02, KernelArtifactV01]
    ] = []
    later_child_initial_artifact_ids: list[str] = []
    activated_child_cell_ids: list[str] = []
    for entry, artifact in child_initial_pairs:
        assert len(artifact.parent_refs) == 2
        parent_entry = next(
            candidate_entry
            for candidate_entry, candidate_artifact in zip(
                bundle.queue_entries,
                bundle.queue_artifacts,
                strict=True,
            )
            if candidate_artifact.artifact_id == artifact.parent_refs[1]
        )
        assert parent_entry.state == "RUNNING"
        assert parent_entry.planned_child_cell_id == entry.cell_id
        if entry.cell_id in activated_child_cell_ids:
            later_child_initial_artifact_ids.append(artifact.artifact_id)
            continue
        activated_child_cell_ids.append(entry.cell_id)
        first_child_initial_pairs.append((entry, artifact))
    assert len(activated_child_cell_ids) == 2
    assert len(first_child_initial_pairs) == 2
    activation_refs = tuple(
        item
        for item in bundle.causal_consumption_refs
        if item.decision_effect == "CHILD_ACTIVATION"
    )
    assert len(activation_refs) == 2
    assert bundle.causal_consumption_refs[3:5] == activation_refs
    assert tuple(item.downstream_artifact_id for item in activation_refs) == tuple(
        artifact.artifact_id for _entry, artifact in first_child_initial_pairs
    )
    for causal_ref, (_entry, child_artifact) in zip(
        activation_refs,
        first_child_initial_pairs,
        strict=True,
    ):
        assert causal_ref.source_artifact_id == child_artifact.parent_refs[1]
        assert causal_ref.output_field == "/planned_child_cell_id"
        assert causal_ref.disposition == "USED"
        assert causal_ref.reason_code == "used:g2d_planned_child_activation"
    assert all(
        artifact_id not in tuple(
            item.downstream_artifact_id for item in activation_refs
        )
        for artifact_id in later_child_initial_artifact_ids
    )
    assert effects.count("CHILD_ACTIVATION") == 2
    assert effects.count("CHILD_RESULT_RETURN_BINDING") == 6
    assert effects.count("CHILD_RESULT_TERMINAL_MAPPING") == 2
    assert effects.count("RUNTIME_OUTCOME_SELECTION") == 2
    assert fr.validate_fractal_runtime_execution_bundle_v02(bundle).status == "PASS"


def test_d4_run_fractal_runtime_complete_profile_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    complete = d4_complete_full_fractal_bundle["complete_report"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(complete, fr.FractalRuntimeValidationReportV02)
    assert complete.status == "PASS"
    assert complete.validation_target == "COMPLETE_PROFILE"
    assert fr.validate_fractal_runtime_execution_bundle_v02(bundle) == complete
    assert all(
        getattr(bundle.runtime_report, field) == 0
        for field in (
            "provider_calls",
            "model_calls",
            "network_calls",
            "connector_calls",
            "external_drs_calls",
            "real_world_effects_count",
        )
    )
    run_tree = next(
        item
        for item in ast.parse(MODULE_PATH.read_text(encoding="utf-8")).body
        if isinstance(item, ast.FunctionDef) and item.name == "run_fractal_runtime_v02"
    )
    assert "validate_fractal_runtime_causal_counterfactual_v02" not in ast.unparse(run_tree)


def test_d4_parent_return_five_outcome_and_substitution_matrix_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert fr.PARENT_RETURN_PROPOSAL_OUTCOME_ROWS_V02 == (
        ("completed", "t06", "t08", "COMPLETED"),
        ("degraded", "t06", "t09", "DEGRADED"),
        ("blocked", "t06", "t10", "BLOCKED"),
        ("needs_user", "t06", "t11", "NEEDS_USER"),
        ("deadend", "t06", "t12", "DEADEND"),
    )
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    expected = fr._d3_transition_decision_v02(registry, "t13")
    assert fr.evaluate_fractal_parent_return_transition_v02(
        source_context=bundle.source_context,
        root_result=bundle.cell_results[-1],
        root_result_artifact=bundle.result_artifacts[-1],
        ordered_cell_results=bundle.cell_results,
        transition_registry=registry,
    ) == expected
    with pytest.raises(ValueError, match="g2d_root_result_required_for_parent_return"):
        fr.evaluate_fractal_parent_return_transition_v02(
            source_context=bundle.source_context,
            root_result=bundle.cell_results[0],
            root_result_artifact=bundle.result_artifacts[0],
            ordered_cell_results=bundle.cell_results,
            transition_registry=registry,
        )
    with pytest.raises(ValueError, match="g2d_transition_profile_invalid"):
        fr.evaluate_fractal_parent_return_transition_v02(
            source_context=bundle.source_context,
            root_result=bundle.cell_results[-1],
            root_result_artifact=bundle.result_artifacts[-1],
            ordered_cell_results=bundle.cell_results,
            transition_registry=bundle.source_context.transition_registry,
        )
    with pytest.raises(ValueError, match="g2d_root_result_required_for_parent_return"):
        fr.evaluate_fractal_parent_return_transition_v02(
            source_context=bundle.source_context,
            root_result=bundle.cell_results[-1],
            root_result_artifact=bundle.result_artifacts[0],
            ordered_cell_results=bundle.cell_results,
            transition_registry=registry,
        )


def test_d4_result_report_artifact_and_bundle_mutation_matrix_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert all(validate_kernel_artifact_v01(item) == () for item in bundle.result_artifacts)
    assert validate_kernel_artifact_v01(bundle.report_artifact) == ()
    root = bundle.cell_results[-1]
    root_artifact = bundle.result_artifacts[-1]
    assert root.final_cell_budget_id == root.global_budget_id
    assert _kernel_payload(root_artifact)["final_cell_budget_id"] == root.final_cell_budget_id
    assert _kernel_payload(root_artifact)["global_budget_id"] == root.global_budget_id
    assert root_artifact.trace_refs.count(root.global_budget_id) == 1
    for result, artifact in zip(
        bundle.cell_results,
        bundle.result_artifacts,
        strict=True,
    ):
        expected_result_trace = (
            result.cell_input_id,
            *result.ordered_terminal_queue_entry_ids,
            *result.ordered_child_result_ids,
            *result.accepted_output_refs,
            *result.evidence_refs,
            result.pre_result_validation_report_id,
            *result.partial_failure_ids,
            result.allocated_cell_budget_id,
            result.final_cell_budget_id,
            result.global_budget_id,
        )
        assert result.trace_refs == expected_result_trace
        expected_artifact_trace = (
            result.post_vv_report_ref,
            result.gt_advisory_ref,
            *expected_result_trace,
        )
        if result.parent_cell_id is None:
            assert result.final_cell_budget_id == result.global_budget_id
            expected_artifact_trace = expected_artifact_trace[:-1]
        assert artifact.trace_refs == expected_artifact_trace
        assert len(artifact.trace_refs) == len(set(artifact.trace_refs))
    mutations = (
        replace(bundle, queue_entries=bundle.queue_entries[:-1]),
        replace(bundle, queue_artifacts=tuple(reversed(bundle.queue_artifacts))),
        replace(bundle, result_artifacts=(*bundle.result_artifacts, bundle.result_artifacts[-1])),
        replace(bundle, report_artifact=bundle.result_artifacts[-1]),
        replace(bundle, transition_decisions=bundle.transition_decisions[:-1]),
        replace(bundle, causal_consumption_refs=bundle.causal_consumption_refs[:-1]),
    )
    for candidate in mutations:
        assert fr.validate_fractal_runtime_execution_bundle_v02(candidate).status == "FAIL_CLOSED"
    assert fr.validate_fractal_runtime_stage_bundle_v02(
        stage="STAGE_D_C",
        artifacts=tuple(reversed(d4_complete_full_fractal_bundle["stage_c"])),
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
    ).status == "FAIL_CLOSED"


def test_d4_causal_counterfactual_contract_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    causal_ref = next(
        item
        for item in bundle.causal_consumption_refs
        if item.disposition == "IGNORED_WITH_REASON"
    )
    source_artifact = next(
        item
        for item in bundle.queue_artifacts
        if item.artifact_id == causal_ref.source_artifact_id
    )
    payload = _kernel_payload(source_artifact)
    tokens = causal_ref.output_field.rsplit("/", 1)
    replacement = payload[tokens[0].lstrip("/")][int(tokens[1])] + ":counterfactual"
    mutated = _d4_mutated_kernel_payload_artifact(
        source_artifact,
        pointer=causal_ref.output_field,
        replacement=replacement,
    )
    assert validate_kernel_artifact_v01(mutated) == ()
    report = fr.validate_fractal_runtime_causal_counterfactual_v02(
        execution_bundle=bundle,
        causal_ref=causal_ref,
        mutated_source_artifact=mutated,
    )
    assert report.status == "PASS"
    assert report.validation_target == "CAUSAL_COUNTERFACTUAL"
    assert fr.validate_fractal_runtime_causal_counterfactual_v02(
        execution_bundle=bundle,
        causal_ref=causal_ref,
        mutated_source_artifact=source_artifact,
    ).status == "FAIL_CLOSED"
    foreign_ref = replace(causal_ref, source_artifact_id=bundle.report_artifact.artifact_id)
    assert fr.validate_fractal_runtime_causal_counterfactual_v02(
        execution_bundle=bundle,
        causal_ref=foreign_ref,
        mutated_source_artifact=mutated,
    ).status == "FAIL_CLOSED"


def test_d4_build_fractal_cell_result_proposal_contract_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    material = _d4_cell_contract_material(bundle, -1)
    proposal = fr.build_fractal_cell_result_proposal_v02(
        source_context=bundle.source_context,
        topology=bundle.topology,
        cell_input=material["cell_input"],
        pre_post_vv_terminal_queue_entries=material["pre_post_vv_terminal_queue_entries"],
        child_results=material["child_results"],
        partial_failures=material["partial_failures"],
        accepted_output_refs=material["result"].accepted_output_refs,
        evidence_refs=material["result"].evidence_refs,
    )
    assert canonical_json_bytes_v01(proposal) == canonical_json_bytes_v01(material["proposal"])
    assert tuple(proposal) == (
        "proposal_id", "request_id", "producer", "vector_id", "plan_id",
        "result_payload", "evidence", "cost", "risks", "time_envelope", "trace_refs",
    )
    assert tuple(proposal["result_payload"]) == (
        "artifact_type", "status", "task_completed", "requires_human_input",
        "blocked_reason", "cell_id", "parent_cell_id", "cell_depth",
        "ordered_child_result_ids", "accepted_output_refs", "evidence_refs",
        "partial_failure_ids", "dependency_depth", "authority_created",
        "permission_created", "action_commit_packet_created", "receipt_created",
        "final_output_created", "drs_write_created", "real_world_effects_count",
    )


def test_d4_validate_fractal_cell_result_proposal_contract_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    material = _d4_cell_contract_material(bundle, 0)
    kwargs = {
        "source_context": bundle.source_context,
        "topology": bundle.topology,
        "cell_input": material["cell_input"],
        "pre_post_vv_terminal_queue_entries": material["pre_post_vv_terminal_queue_entries"],
        "child_results": material["child_results"],
        "partial_failures": material["partial_failures"],
    }
    assert fr.validate_fractal_cell_result_proposal_v02(material["proposal"], **kwargs).status == "PASS"
    mutated = dict(material["proposal"])
    mutated["request_id"] = mutated["request_id"] + ":foreign"
    assert fr.validate_fractal_cell_result_proposal_v02(mutated, **kwargs).status == "FAIL_CLOSED"
    assert fr.validate_fractal_cell_result_proposal_v02(dict(material["proposal"]), **{
        **kwargs,
        "cell_input": _seal(replace(material["cell_input"], scope_ref="scope:foreign")),
    }).status == "FAIL_CLOSED"


def test_d4_validate_fractal_post_vv_report_contract_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    for proposal, report in zip(bundle.result_proposals, bundle.post_vv_reports, strict=True):
        validation = fr.validate_fractal_post_vv_report_v02(
            report,
            result_proposal=proposal,
            source_context=bundle.source_context,
        )
        assert validation.status == "PASS"
        assert report["checked_at"] == bundle.source_context.router_input.local_routing_snapshot.kt_asof_utc
    mutated = dict(bundle.post_vv_reports[0])
    mutated["proposal_id"] = "frproposal_v02:" + "0" * 64
    assert fr.validate_fractal_post_vv_report_v02(
        mutated,
        result_proposal=bundle.result_proposals[0],
        source_context=bundle.source_context,
    ).status == "FAIL_CLOSED"


def test_d4_validate_fractal_gt_advisory_contract_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    for vv_report, gt_report in zip(bundle.post_vv_reports, bundle.gt_advisory_reports, strict=True):
        validation = fr.validate_fractal_gt_advisory_v02(
            gt_report,
            post_vv_report=vv_report,
            source_context=bundle.source_context,
        )
        assert validation.status == "PASS"
        assert gt_report["created_at"] == bundle.source_context.router_input.local_routing_snapshot.kt_asof_utc
        assert vv_report["proposal_id"] in gt_report["gt_report_id"]
    mutated = dict(bundle.gt_advisory_reports[0])
    mutated["created_at"] = "2026-08-08T12:34:55+00:00"
    assert fr.validate_fractal_gt_advisory_v02(
        mutated,
        post_vv_report=bundle.post_vv_reports[0],
        source_context=bundle.source_context,
    ).status == "FAIL_CLOSED"


def test_d4_post_vv_gt_explicit_time_repeated_bytes_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    kt = bundle.source_context.router_input.local_routing_snapshot.kt_asof_utc
    for proposal, expected_vv, expected_gt in zip(
        bundle.result_proposals,
        bundle.post_vv_reports,
        bundle.gt_advisory_reports,
        strict=True,
    ):
        first_vv = fr._validate_result_proposals([proposal], checked_at=kt)[0]
        second_vv = fr._validate_result_proposals([proposal], checked_at=kt)[0]
        assert canonical_json_bytes_v01(first_vv) == canonical_json_bytes_v01(second_vv)
        assert canonical_json_bytes_v01(first_vv) == canonical_json_bytes_v01(expected_vv)
        first_gt = fr._validate_gt([first_vv], created_at=kt)
        second_gt = fr._validate_gt([second_vv], created_at=kt)
        assert canonical_json_bytes_v01(first_gt) == canonical_json_bytes_v01(second_gt)
        assert canonical_json_bytes_v01(first_gt) == canonical_json_bytes_v01(expected_gt)


def test_d4_context_unique_report_ref_alignment_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    proposal_ids = tuple(item["proposal_id"] for item in bundle.result_proposals)
    vv_ids = tuple(item["vv_report_id"] for item in bundle.post_vv_reports)
    gt_ids = tuple(item["gt_report_id"] for item in bundle.gt_advisory_reports)
    assert all(len(values) == len(set(values)) for values in (proposal_ids, vv_ids, gt_ids))
    assert tuple(item["proposal_id"] for item in bundle.post_vv_reports) == proposal_ids
    assert tuple(item.post_vv_report_ref for item in bundle.cell_results) == vv_ids
    assert tuple(item.gt_advisory_ref for item in bundle.cell_results) == gt_ids
    assert all(proposal_id in gt_id for proposal_id, gt_id in zip(proposal_ids, gt_ids, strict=True))


def test_d4_root_report_status_and_outcome_projection_v02(
    d4_complete_full_fractal_bundle: dict[str, object],
) -> None:
    bundle = d4_complete_full_fractal_bundle["bundle"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    report = bundle.runtime_report
    root = bundle.cell_results[-1]
    assert root.parent_cell_id is None
    assert report.runtime_outcome == root.outcome
    assert report.reason_codes == root.reason_codes
    assert report.report_status == "PASS"
    assert report.ordered_cell_result_ids == tuple(item.result_id for item in bundle.cell_results)
    assert report.parent_return_refs == (bundle.result_artifacts[-1].artifact_id,)
    assert report.parent_return_transition_decision_id == bundle.transition_decisions[-1].decision_id
    assert report.root_review_required is True
    assert all(
        getattr(report, field) == 0
        for field in (
            "provider_calls", "model_calls", "network_calls", "connector_calls",
            "external_drs_calls", "action_commit_packets_created", "permissions_created",
            "receipts_created", "final_outputs_created", "drs_writes",
            "authority_created_count", "real_world_effects_count",
        )
    )


def test_e4c001_v03_runtime_observed_work_context_surface_geometry_schema_and_facade_v02(
    e4c001_observed_work_family_v02: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family = e4c001_observed_work_family_v02
    context = family["selective_context"]
    baseline = family["baseline"]
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert baseline.observed_work_context is None
    assert len(fr.G2D_TYPES_V02) == 21
    assert len(fr.SERIALIZED_G2D_TYPES_V02) == 18
    assert len(fr.RUNTIME_ONLY_G2D_TYPES_V02) == 3
    assert fr.RUNTIME_ONLY_G2D_TYPES_V02[-1] is fr.RuntimeObservedWorkContextV02
    assert len(fields(fr.FractalRuntimeExecutionBundleV02)) == 28
    assert fields(fr.FractalRuntimeExecutionBundleV02)[-1].name == (
        "observed_work_context"
    )
    public_functions = tuple(
        name
        for name, value in vars(fr).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == fr.__name__
    )
    assert len(public_functions) == 116
    assert public_functions[-6:] == _E4C001_PUBLIC_FUNCTION_NAMES_V02
    for name in _E4C001_CORRECTED_SIGNATURE_NAMES_V02:
        parameter = tuple(inspect.signature(getattr(fr, name)).parameters.values())[-1]
        assert parameter.name == "observed_work_context"
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is None
        assert str(parameter.annotation) == "RuntimeObservedWorkContextV02 | None"
    package = importlib.import_module("hedgehog.kernel")
    for name in (
        "RuntimeObservedWorkContextV02",
        *_E4C001_PUBLIC_FUNCTION_NAMES_V02,
    ):
        assert getattr(package, name) is getattr(fr, name)
    assert package.__all__ == _HISTORICAL_KERNEL_DUNDER_ALL_V02
    assert fr.FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT == 116
    assert fr.TOTAL_G2D_PUBLIC_FUNCTION_COUNT == 122
    assert fr.DIRECT_PACKAGE_G2D_ATTRIBUTE_COUNT == 143
    assert len(fr.PUBLIC_G2D_REASON_CODES) == 220
    assert len(fr.VALIDATION_TARGETS) == 35
    assert fr.VALIDATION_TARGETS[-1] == (
        "OBSERVED_WORK_BINDINGS_AGAINST_SOURCES"
    )
    assert len(fr.FAILURE_STAGES) == 30
    assert len(fr.CAUSAL_DECISION_EFFECTS) == 14
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert len(schema["$defs"]) == 18
    assert "RuntimeObservedWorkContextV02" not in schema["$defs"]
    assert SCHEMA_PATH.read_text(encoding="utf-8").count(
        '"OBSERVED_WORK_BINDINGS_AGAINST_SOURCES"'
    ) == 1
    assert fr.validate_runtime_observed_work_context_v02(context).status == "PASS"
    selected_node = family["selected_node"]
    selected_input = family["selected_input"]
    assert isinstance(selected_node, fr.RuntimeTopologyNodeV02)
    assert isinstance(selected_input, fr.FractalCellInputV02)
    validator_calls = 0
    original_context_validator = fr.validate_runtime_observed_work_context_v02

    def counted_context_validator(value: object) -> object:
        nonlocal validator_calls
        validator_calls += 1
        return original_context_validator(value)

    monkeypatch.setattr(
        fr,
        "validate_runtime_observed_work_context_v02",
        counted_context_validator,
    )
    assert fr._observed_work_bindings_for_cell_node_v02(
        context,
        topology=baseline.topology,
        cell_id=selected_input.cell_id,
        node_id=selected_node.node_id,
    ) == context.ordered_binding_artifacts
    assert validator_calls == 0
    plain = fr.runtime_observed_work_context_to_plain_data_v02(context)
    assert "baseline_execution_bundle" not in plain
    assert plain["baseline_bundle_anchor_sha256"] == (
        context.baseline_bundle_anchor_sha256
    )
    assert tuple(plain) == tuple(sorted(plain))
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    test_names = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )
    assert len(test_names) == 83
    assert sum(name.startswith("test_e4c001_v03_") for name in test_names) == 8


def test_e4c001_v03_binding_payload_full_artifact_pointer_and_canonical_order_v02(
    e4c001_observed_work_family_v02: dict[str, object],
) -> None:
    family = e4c001_observed_work_family_v02
    baseline = family["baseline"]
    selected_node = family["selected_node"]
    selected_input = family["selected_input"]
    payload_baseline = family["payload_baseline"]
    payload_observed = family["payload_observed"]
    context = family["selective_context"]
    bindings = family["selective_bindings"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(selected_node, fr.RuntimeTopologyNodeV02)
    assert isinstance(selected_input, fr.FractalCellInputV02)
    assert isinstance(payload_baseline, KernelArtifactV01)
    assert isinstance(payload_observed, KernelArtifactV01)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(bindings, tuple)
    payload_binding = next(
        item
        for item in bindings
        if _kernel_payload(item)["source_pair"]["baseline_identity_ref"]
        == payload_baseline.artifact_id
    )
    payload = _kernel_payload(payload_binding)
    assert tuple(payload) == (
        "change_proof",
        "execution",
        "profile",
        "safety",
        "source_pair",
        "topology_binding",
    )
    assert tuple(payload["change_proof"]) == (
        "all_full_artifact_changed_pointers",
        "consumed_changed_material_rows",
        "whole_artifact_expanded",
        "whole_payload_expanded",
    )
    assert payload["change_proof"]["all_full_artifact_changed_pointers"] == [
        "/payload/value"
    ]
    assert payload["change_proof"]["consumed_changed_material_rows"] == [
        {
            "baseline_present": True,
            "baseline_value_sha256": hashlib.sha256(b"0").hexdigest(),
            "full_artifact_pointer": "/payload/value",
            "observed_present": True,
            "observed_value_sha256": hashlib.sha256(b"1").hexdigest(),
            "payload_pointer": "/value",
        }
    ]
    assert tuple(payload["safety"]) == tuple(sorted(payload["safety"]))
    assert all(value in {False, 0} for value in payload["safety"].values())
    canonical = fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=family["direct_sources"],
        supporting_artifacts=(),
        binding_artifacts=bindings,
        execution_scope="SELECTIVE",
    )
    assert canonical == context
    proof_binding = family["subset_whole_bindings"][0]
    assert isinstance(proof_binding, KernelArtifactV01)
    proof_execution = _kernel_payload(proof_binding)["execution"]
    assert proof_execution == {
        "execution_scope": "WHOLE_RUN_ESCALATION",
        "whole_run_escalation_policy_id": None,
        "whole_run_escalation_reason": (
            "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
        ),
    }
    assert validate_kernel_artifact_v01(proof_binding) == ()
    assert proof_binding.artifact_id != payload_binding.artifact_id
    assert proof_binding == (
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=selected_node,
            cell_input=selected_input,
            baseline_source_artifact=payload_baseline,
            observed_source_artifact=payload_observed,
            changed_full_artifact_pointers=("/payload/value",),
            execution_scope="WHOLE_RUN_ESCALATION",
            whole_run_escalation_reason=(
                "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
            ),
            whole_run_escalation_policy_id=None,
        )
    )
    invalid_triads = (
        (
            "SELECTIVE",
            "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK",
            None,
        ),
        ("SELECTIVE", None, "foreign_policy_v02"),
        (
            "WHOLE_RUN_ESCALATION",
            "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK",
            "foreign_policy_v02",
        ),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            None,
        ),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            "accepted_shape_but_unapproved_policy_v02",
        ),
        ("WHOLE_RUN_ESCALATION", "ARBITRARY_SUBSTITUTED_REASON", None),
        ("WHOLE_RUN_ESCALATION", "ARBITRARY_SUBSTITUTED_REASON", "foreign"),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            "",
        ),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            "   ",
        ),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            "NONE",
        ),
        (
            "WHOLE_RUN_ESCALATION",
            "FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION",
            "foreign:policy:v02",
        ),
        ("UNKNOWN_SCOPE", None, None),
    )
    for execution_scope, reason, policy_id in invalid_triads:
        with pytest.raises(
            ValueError,
            match="g2d_topology_source_binding_invalid",
        ):
            fr.project_runtime_observed_work_binding_kernel_artifact_v02(
                baseline_execution_bundle=baseline,
                node=selected_node,
                cell_input=selected_input,
                baseline_source_artifact=payload_baseline,
                observed_source_artifact=payload_observed,
                changed_full_artifact_pointers=("/payload/value",),
                execution_scope=execution_scope,
                whole_run_escalation_reason=reason,
                whole_run_escalation_policy_id=policy_id,
            )
    whole_payload_binding = (
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=selected_node,
            cell_input=selected_input,
            baseline_source_artifact=payload_baseline,
            observed_source_artifact=payload_observed,
            changed_full_artifact_pointers=("/payload",),
            execution_scope="SELECTIVE",
        )
    )
    whole_artifact_binding = (
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=selected_node,
            cell_input=selected_input,
            baseline_source_artifact=payload_baseline,
            observed_source_artifact=payload_observed,
            changed_full_artifact_pointers=("",),
            execution_scope="SELECTIVE",
        )
    )
    assert _kernel_payload(whole_payload_binding)["change_proof"] == {
        "all_full_artifact_changed_pointers": ["/payload/value"],
        "consumed_changed_material_rows": payload["change_proof"][
            "consumed_changed_material_rows"
        ],
        "whole_artifact_expanded": False,
        "whole_payload_expanded": True,
    }
    assert _kernel_payload(whole_artifact_binding)["change_proof"][
        "whole_artifact_expanded"
    ] is True
    envelope_observed = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "payload", "value": 0},
        trace_ref="trace:e4c001:payload",
        predecessor=payload_baseline,
        source_component="observed_delta_source_v01",
    )
    envelope_binding = fr.project_runtime_observed_work_binding_kernel_artifact_v02(
        baseline_execution_bundle=baseline,
        node=selected_node,
        cell_input=selected_input,
        baseline_source_artifact=payload_baseline,
        observed_source_artifact=envelope_observed,
        changed_full_artifact_pointers=("/source_component",),
        execution_scope="SELECTIVE",
    )
    envelope_row = _kernel_payload(envelope_binding)["change_proof"][
        "consumed_changed_material_rows"
    ][0]
    assert envelope_row["full_artifact_pointer"] == "/source_component"
    assert envelope_row["payload_pointer"] is None
    assert validate_kernel_artifact_v01(envelope_binding) == ()


def test_e4c001_v03_root_and_child_stable_witness_mapping_v02(
    e4c001_observed_work_family_v02: dict[str, object],
) -> None:
    family = e4c001_observed_work_family_v02
    baseline = family["baseline"]
    selected_input = family["selected_input"]
    selected_node = family["selected_node"]
    payload_baseline = family["payload_baseline"]
    payload_observed = family["payload_observed"]
    child_binding = family["selective_bindings"][0]
    context = family["selective_context"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(selected_input, fr.FractalCellInputV02)
    assert isinstance(selected_node, fr.RuntimeTopologyNodeV02)
    assert isinstance(payload_baseline, KernelArtifactV01)
    assert isinstance(payload_observed, KernelArtifactV01)
    assert isinstance(child_binding, KernelArtifactV01)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    child_witness = _kernel_payload(child_binding)["topology_binding"]
    parent_input = next(
        item for item in baseline.cell_inputs if item.cell_id == selected_input.parent_cell_id
    )
    projection = next(
        item
        for item in baseline.scope_projections
        if item.child_cell_id == selected_input.cell_id
    )
    canonical_child_index = parent_input.ordered_planned_child_cell_ids.index(
        selected_input.cell_id
    )
    expected_child_id = fr.derive_fractal_child_cell_id_v02(
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
        child_depth=selected_input.cell_depth,
    )
    assert expected_child_id == selected_input.cell_id
    assert child_witness["witness_class"] == "BASELINE_CHILD_ACTIVATION_INPUT"
    assert child_witness["canonical_child_index"] == canonical_child_index
    assert child_binding.parent_refs == (
        baseline.topology_artifact.artifact_id,
        payload_baseline.artifact_id,
        payload_observed.artifact_id,
        child_witness["activation_parent_queue_artifact_ref"],
    )
    baseline_artifact_by_id = {
        item.artifact_id: item
        for item in (
            *baseline.queue_artifacts,
            *baseline.result_artifacts,
            baseline.report_artifact,
        )
    }
    support_by_id = {
        item.artifact_id: item for item in context.ordered_supporting_artifacts
    }
    activation_parent_id = child_witness[
        "activation_parent_queue_artifact_ref"
    ]
    assert activation_parent_id in support_by_id
    assert support_by_id[activation_parent_id] == baseline_artifact_by_id[
        activation_parent_id
    ]
    assert set(support_by_id).issubset(baseline_artifact_by_id)
    support_positions = {
        item.artifact_id: index
        for index, item in enumerate(context.ordered_supporting_artifacts)
    }
    carried_baseline_ids = {
        baseline.source_context.proposal_artifact.artifact_id,
        baseline.source_context.decision_artifact.artifact_id,
        baseline.source_context.route_eligibility_artifact.artifact_id,
        baseline.topology_artifact.artifact_id,
    }
    assert all(
        parent_id in carried_baseline_ids
        or support_positions[parent_id] < support_positions[artifact.artifact_id]
        for artifact in context.ordered_supporting_artifacts
        for parent_id in artifact.parent_refs
    )
    assert fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=family["direct_sources"],
        supporting_artifacts=context.ordered_supporting_artifacts,
        binding_artifacts=family["selective_bindings"],
        execution_scope="SELECTIVE",
    ) == context
    assert fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=family["direct_sources"],
        supporting_artifacts=(
            *context.ordered_supporting_artifacts,
            context.ordered_supporting_artifacts[0],
        ),
        binding_artifacts=family["selective_bindings"],
        execution_scope="SELECTIVE",
    ) == context
    root_input = next(item for item in baseline.cell_inputs if item.parent_cell_id is None)
    root_node = next(
        item
        for item in baseline.topology_nodes
        if item.node_id == root_input.ordered_node_ids[0]
    )
    expected_root_id = fr.derive_fractal_root_cell_id_v02(
        source_binding_id=baseline.source_binding.source_binding_id,
        runtime_policy_id=baseline.source_binding.runtime_policy_id,
        accepted_mode=baseline.source_binding.accepted_mode,
        accepted_scope_ref=baseline.source_binding.accepted_scope_ref,
    )
    assert expected_root_id == root_input.cell_id
    root_binding = fr.project_runtime_observed_work_binding_kernel_artifact_v02(
        baseline_execution_bundle=baseline,
        node=root_node,
        cell_input=root_input,
        baseline_source_artifact=payload_baseline,
        observed_source_artifact=payload_observed,
        changed_full_artifact_pointers=("/payload/value",),
        execution_scope="SELECTIVE",
    )
    root_witness = _kernel_payload(root_binding)["topology_binding"]
    assert root_witness["witness_class"] == "BASELINE_ROOT_CELL_INPUT"
    assert root_witness["activation_parent_queue_artifact_ref"] is None
    assert root_witness["canonical_child_index"] is None
    assert root_binding.parent_refs == (
        baseline.topology_artifact.artifact_id,
        payload_baseline.artifact_id,
        payload_observed.artifact_id,
    )
    foreign_node = next(
        item
        for item in baseline.topology_nodes
        if item.node_id not in selected_input.ordered_node_ids
    )
    with pytest.raises(ValueError, match="g2d_topology_source_binding_invalid"):
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=foreign_node,
            cell_input=selected_input,
            baseline_source_artifact=payload_baseline,
            observed_source_artifact=payload_observed,
            changed_full_artifact_pointers=("/payload/value",),
            execution_scope="SELECTIVE",
        )
    with pytest.raises(ValueError, match="g2d_topology_source_binding_invalid"):
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=selected_node,
            cell_input=replace(selected_input, cell_id="frcell_v02:" + "0" * 64),
            baseline_source_artifact=payload_baseline,
            observed_source_artifact=payload_observed,
            changed_full_artifact_pointers=("/payload/value",),
            execution_scope="SELECTIVE",
        )
    with pytest.raises(ValueError, match="g2d_topology_source_binding_invalid"):
        fr.build_runtime_observed_work_context_v02(
            baseline_execution_bundle=baseline,
            direct_source_artifacts=family["direct_sources"],
            supporting_artifacts=(),
            binding_artifacts=family["subset_whole_bindings"],
            execution_scope="WHOLE_RUN_ESCALATION",
            whole_run_escalation_reason=(
                "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
            ),
            whole_run_escalation_policy_id=None,
        )
    full_selective_bindings = tuple(
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=node,
            cell_input=cell_input,
            baseline_source_artifact=source_baseline,
            observed_source_artifact=source_observed,
            changed_full_artifact_pointers=("/payload/value",),
            execution_scope="SELECTIVE",
        )
        for cell_input, node, source_baseline, source_observed in family[
            "full_source_pairs"
        ]
    )
    with pytest.raises(ValueError, match="g2d_topology_source_binding_invalid"):
        fr.build_runtime_observed_work_context_v02(
            baseline_execution_bundle=baseline,
            direct_source_artifacts=family["full_direct_sources"],
            supporting_artifacts=(),
            binding_artifacts=full_selective_bindings,
            execution_scope="SELECTIVE",
        )
    whole_context = family["whole_context"]
    selective_context = family["selective_context"]
    assert isinstance(whole_context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(selective_context, fr.RuntimeObservedWorkContextV02)
    all_node_ids = tuple(item.node_id for item in baseline.topology_nodes)
    all_cell_ids = tuple(item.cell_id for item in baseline.cell_inputs)
    invalid_contexts = (
        replace(
            selective_context,
            ordered_direct_affected_node_ids=all_node_ids,
            ordered_execution_node_ids=all_node_ids,
            ordered_affected_cell_ids=all_cell_ids,
        ),
        replace(
            whole_context,
            ordered_direct_affected_node_ids=(
                *whole_context.ordered_direct_affected_node_ids,
                "frnode_v02:" + "f" * 64,
            ),
        ),
        replace(
            whole_context,
            ordered_execution_node_ids=(
                whole_context.ordered_execution_node_ids[:-1]
            ),
        ),
        replace(
            whole_context,
            ordered_affected_cell_ids=(
                *whole_context.ordered_affected_cell_ids,
                "frcell_v02:" + "f" * 64,
            ),
        ),
        replace(
            whole_context,
            ordered_binding_artifacts=(
                *whole_context.ordered_binding_artifacts[:-1],
                baseline.topology_artifact,
            ),
        ),
        replace(
            whole_context,
            observed_work_context_id=selective_context.observed_work_context_id,
        ),
        replace(
            whole_context,
            ordered_binding_artifacts=(
                replace(
                    whole_context.ordered_binding_artifacts[0],
                    artifact_id=(
                        whole_context.ordered_binding_artifacts[1].artifact_id
                    ),
                ),
                *whole_context.ordered_binding_artifacts[1:],
            ),
        ),
    )
    for invalid_context in invalid_contexts:
        assert fr.validate_runtime_observed_work_context_v02(
            invalid_context
        ).status == "FAIL_CLOSED"


def test_e4c001_v03_t02_parent_envelope_and_settled_prefix_context_reconstruction_v02(
    e4c001_observed_work_family_v02: dict[str, object],
) -> None:
    family = e4c001_observed_work_family_v02
    baseline = family["baseline"]
    bundle = family["selective_bundle"]
    context = family["selective_context"]
    selected_input = family["selected_input"]
    selected_node = family["selected_node"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(selected_input, fr.FractalCellInputV02)
    assert isinstance(selected_node, fr.RuntimeTopologyNodeV02)
    binding_ids = tuple(item.artifact_id for item in context.ordered_binding_artifacts)
    initial_index = next(
        index
        for index, entry in enumerate(bundle.queue_entries)
        if entry.cell_id == selected_input.cell_id
        and entry.node_id == selected_node.node_id
        and entry.predecessor_queue_entry_id is None
    )
    initial_entry = bundle.queue_entries[initial_index]
    initial_artifact = bundle.queue_artifacts[initial_index]
    assert initial_artifact.parent_refs == (
        bundle.topology_artifact.artifact_id,
        initial_artifact.parent_refs[1],
        *binding_ids,
    )
    baseline_initial = next(
        artifact
        for entry, artifact in zip(
            baseline.queue_entries,
            baseline.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == selected_input.cell_id
        and entry.node_id == selected_node.node_id
        and entry.predecessor_queue_entry_id is None
    )
    assert len(baseline_initial.parent_refs) == 2
    registry = transition_registry.build_fractal_runtime_transition_registry_profile_v02()
    decision = bundle.transition_decisions[initial_index + 1]
    assert decision.rule_id.endswith("t02_topology_to_pending")
    assert transition_registry.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=bundle.topology_artifact,
        target_artifact=initial_artifact,
    ) == ()
    successor_index = next(
        index
        for index, entry in enumerate(bundle.queue_entries)
        if entry.cell_id == initial_entry.cell_id
        and entry.node_id == initial_entry.node_id
        and entry.predecessor_queue_entry_id == initial_entry.queue_entry_id
    )
    successor_artifact = bundle.queue_artifacts[successor_index]
    assert successor_artifact.parent_refs[:2] == (
        bundle.topology_artifact.artifact_id,
        initial_artifact.artifact_id,
    )
    assert not set(binding_ids) & set(successor_artifact.parent_refs)
    mutated_artifact = replace(
        initial_artifact,
        parent_refs=(
            *initial_artifact.parent_refs[:2],
            *reversed(initial_artifact.parent_refs[2:]),
        ),
    )
    mutated_queue_artifacts = (
        *bundle.queue_artifacts[:initial_index],
        mutated_artifact,
        *bundle.queue_artifacts[initial_index + 1:],
    )
    assert fr.validate_fractal_runtime_execution_bundle_v02(
        replace(bundle, queue_artifacts=mutated_queue_artifacts)
    ).status == "FAIL_CLOSED"
    helper = next(
        node
        for node in ast.parse(
            Path(transition_registry.__file__).read_text(encoding="utf-8")
        ).body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_fractal_runtime_initial_queue_parent_form_valid_v02"
    )
    payload_get_keys = {
        call.args[0].value
        for call in ast.walk(helper)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "get"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "payload"
        and call.args
        and isinstance(call.args[0], ast.Constant)
        and isinstance(call.args[0].value, str)
    }
    assert {"state", "prior_state", "predecessor_relation", "parent_cell_id"}.issubset(
        payload_get_keys
    )
    prefix_state = fr._d4_initialize_runtime_state_v02(
        baseline.source_context,
        observed_work_context=context,
    )
    prefix_indexes = fr._d4_indexes_v02(prefix_state)
    live_global = prefix_indexes["live_head_by_axis"][(
        "ROOT_GLOBAL_AND_CELL",
        baseline.topology.root_cell_id,
    )]
    backpressure = fr.evaluate_fractal_backpressure_v02(
        source_context=baseline.source_context,
        topology=baseline.topology,
        policy=baseline.source_context.runtime_policy,
        global_budget=live_global,
        queue_entries=fr._d4_latest_v02(prefix_state),
        admission_round=1,
        settled_budget_log=prefix_state["budgets"],
        settled_queue_entry_log=prefix_state["queue_entries"],
        settled_queue_artifact_log=prefix_state["queue_artifacts"],
        settled_cell_inputs=prefix_state["cell_inputs"],
        settled_scope_projections=prefix_state["scope_projections"],
        settled_revise_observations=prefix_state["revise_observations"],
        settled_backpressure_states=prefix_state["backpressure_states"],
        settled_validation_reports=prefix_state["prefix_reports"],
        observed_work_context=context,
    )
    assert backpressure is None or (
        fr.validate_fractal_backpressure_state_v02(backpressure).status
        == "PASS"
    )


def test_e4c001_v03_selective_granular_identity_propagation_and_unaffected_exclusion_v02(
    e4c001_observed_work_family_v02: dict[str, object],
) -> None:
    family = e4c001_observed_work_family_v02
    baseline = family["baseline"]
    candidate = family["selective_bundle"]
    context = family["selective_context"]
    selected_input = family["selected_input"]
    selected_node = family["selected_node"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(candidate, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(selected_input, fr.FractalCellInputV02)
    assert isinstance(selected_node, fr.RuntimeTopologyNodeV02)
    assert context.execution_scope == "SELECTIVE"
    assert context.ordered_direct_affected_node_ids == (selected_node.node_id,)
    assert context.ordered_affected_cell_ids == (selected_input.cell_id,)
    selected = {selected_node.node_id}
    changed = True
    while changed:
        changed = False
        for edge in baseline.topology_edges:
            if (
                edge.cell_projection_class == "FRACTAL_LEAF_PROJECTION"
                and edge.source_node_id in selected
                and edge.target_node_id not in selected
            ):
                selected.add(edge.target_node_id)
                changed = True
    assert context.ordered_execution_node_ids == tuple(
        node.node_id for node in baseline.topology_nodes if node.node_id in selected
    )
    assert candidate.source_context == baseline.source_context
    assert candidate.source_binding == baseline.source_binding
    assert candidate.topology_seed == baseline.topology_seed
    assert candidate.topology_nodes == baseline.topology_nodes
    assert candidate.topology_edges == baseline.topology_edges
    assert candidate.runtime_assignments == baseline.runtime_assignments
    assert candidate.topology == baseline.topology
    assert candidate.topology_artifact == baseline.topology_artifact
    baseline_input_by_cell = {item.cell_id: item for item in baseline.cell_inputs}
    candidate_input_by_cell = {item.cell_id: item for item in candidate.cell_inputs}
    assert candidate_input_by_cell[selected_input.cell_id] != selected_input
    unselected_input = next(
        item
        for item in baseline.cell_inputs
        if item.parent_cell_id is not None and item.cell_id != selected_input.cell_id
    )
    assert candidate_input_by_cell[unselected_input.cell_id] == unselected_input
    baseline_queue_by_key = {
        (entry.cell_id, entry.node_id, entry.snapshot_sequence): artifact
        for entry, artifact in zip(
            baseline.queue_entries,
            baseline.queue_artifacts,
            strict=True,
        )
    }
    candidate_queue_by_key = {
        (entry.cell_id, entry.node_id, entry.snapshot_sequence): artifact
        for entry, artifact in zip(
            candidate.queue_entries,
            candidate.queue_artifacts,
            strict=True,
        )
    }
    unselected_keys = tuple(
        key for key in baseline_queue_by_key if key[0] == unselected_input.cell_id
    )
    assert unselected_keys
    assert all(
        candidate_queue_by_key[key] == baseline_queue_by_key[key]
        for key in unselected_keys
    )
    baseline_result_by_cell = {
        result.cell_id: artifact
        for result, artifact in zip(
            baseline.cell_results,
            baseline.result_artifacts,
            strict=True,
        )
    }
    candidate_result_by_cell = {
        result.cell_id: artifact
        for result, artifact in zip(
            candidate.cell_results,
            candidate.result_artifacts,
            strict=True,
        )
    }
    assert candidate_result_by_cell[unselected_input.cell_id] == (
        baseline_result_by_cell[unselected_input.cell_id]
    )
    assert candidate_result_by_cell[selected_input.cell_id] != (
        baseline_result_by_cell[selected_input.cell_id]
    )
    assert candidate.runtime_trace.trace_id != baseline.runtime_trace.trace_id
    assert candidate.runtime_report.report_id != baseline.runtime_report.report_id
    assert candidate.report_artifact.artifact_id != baseline.report_artifact.artifact_id
    assert context.baseline_execution_bundle == baseline
    assert context.baseline_execution_bundle.observed_work_context is None
    unselected_initial_artifacts = tuple(
        artifact
        for entry, artifact in zip(
            candidate.queue_entries,
            candidate.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == unselected_input.cell_id
        and entry.predecessor_queue_entry_id is None
    )
    binding_ids = {item.artifact_id for item in context.ordered_binding_artifacts}
    assert all(
        not binding_ids.intersection(artifact.parent_refs)
        for artifact in unselected_initial_artifacts
    )


def test_e4c001_v03_parent_closed_stage_causal_and_complete_bundle_v02(
    e4c001_observed_work_family_v02: dict[str, object],
) -> None:
    family = e4c001_observed_work_family_v02
    bundle = family["selective_bundle"]
    context = family["selective_context"]
    baseline = family["baseline"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    stage_a, stage_b, stage_c = _d4_bundle_artifacts(bundle)
    baseline_stages = _d4_bundle_artifacts(baseline)
    assert tuple(map(len, (stage_a, stage_b, stage_c))) == tuple(
        map(len, baseline_stages)
    )
    for stage, artifacts in zip(
        ("STAGE_D_A", "STAGE_D_B", "STAGE_D_C"),
        (stage_a, stage_b, stage_c),
        strict=True,
    ):
        report = fr.validate_fractal_runtime_stage_bundle_v02(
            stage=stage,
            artifacts=artifacts,
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
            observed_work_context=context,
        )
        assert report.status == "PASS"
    assert fr.validate_fractal_runtime_abi_profile_v02(
        stage_c,
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
        observed_work_context=context,
    ).status == "PASS"
    assert fr.validate_fractal_runtime_causal_consumption_refs_v02(
        bundle.causal_consumption_refs,
        **_d4_validation_kwargs(bundle),
        stage_d_c_artifacts=stage_c,
        observed_work_context=context,
    ).status == "PASS"
    parent_closed = fr._observed_work_parent_closed_union_v02(
        stage_artifacts=stage_c,
        observed_work_context=context,
    )
    assert validate_kernel_artifact_bundle_v01(artifacts=parent_closed) == ()
    positions = {item.artifact_id: index for index, item in enumerate(parent_closed)}
    assert all(
        positions[parent_id] < positions[artifact.artifact_id]
        for artifact in parent_closed
        for parent_id in artifact.parent_refs
    )
    observed_refs = tuple(
        item
        for item in bundle.causal_consumption_refs
        if item.decision_effect
        in {"OBSERVED_WORK_INPUT", "OBSERVED_WORK_CELL_BINDING"}
    )
    assert len(observed_refs) == 6
    initial_artifact_ids = {
        artifact.artifact_id
        for entry, artifact in zip(
            bundle.queue_entries,
            bundle.queue_artifacts,
            strict=True,
        )
        if entry.predecessor_queue_entry_id is None
    }
    binding_by_id = {
        item.artifact_id: item for item in context.ordered_binding_artifacts
    }
    assert all(item.source_artifact_id in binding_by_id for item in observed_refs)
    assert all(item.downstream_artifact_id in initial_artifact_ids for item in observed_refs)
    queue_by_id = {item.artifact_id: item for item in bundle.queue_artifacts}
    assert all(
        item.source_artifact_id
        in queue_by_id[item.downstream_artifact_id].parent_refs
        for item in observed_refs
    )
    observed_input_ids = {
        item.artifact_id
        for item in (
            *context.ordered_direct_source_artifacts,
            *context.ordered_binding_artifacts,
        )
    }
    support_by_id = {
        item.artifact_id: item for item in context.ordered_supporting_artifacts
    }
    stage_by_id = {
        item.artifact_id: item
        for stage in (stage_a, stage_b, stage_c)
        for item in stage
    }
    assert not observed_input_ids.intersection(bundle.runtime_trace.abi_artifact_refs)
    assert all(
        not observed_input_ids.intersection(item.artifact_id for item in stage)
        for stage in (stage_a, stage_b, stage_c)
    )
    support_stage_overlap = set(support_by_id).intersection(stage_by_id)
    assert support_stage_overlap
    assert all(
        support_by_id[artifact_id] == stage_by_id[artifact_id]
        for artifact_id in support_stage_overlap
    )
    assert fr.validate_fractal_runtime_execution_bundle_v02(bundle).status == "PASS"


def test_e4c001_v03_counterfactual_rebuild_payload_and_envelope_changes_v02(
    e4c001_observed_work_family_v02: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family = e4c001_observed_work_family_v02
    bundle = family["selective_bundle"]
    context = family["selective_context"]
    baseline = family["baseline"]
    assert isinstance(bundle, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    captured_material: list[dict[str, object]] = []
    original_counterfactual_identity = fr._observed_work_counterfactual_id_v02

    def capture_counterfactual_identity(
        material: dict[str, object],
    ) -> str:
        captured_material.append(material)
        return original_counterfactual_identity(material)

    monkeypatch.setattr(
        fr,
        "_observed_work_counterfactual_id_v02",
        capture_counterfactual_identity,
    )
    binding_pairs = {
        _kernel_payload(item)["source_pair"]["baseline_identity_ref"]: item
        for item in context.ordered_binding_artifacts
    }
    payload_binding = binding_pairs[family["payload_baseline"].artifact_id]
    lifecycle_binding = binding_pairs[family["lifecycle_baseline"].artifact_id]
    payload_ref = next(
        item
        for item in bundle.causal_consumption_refs
        if item.source_artifact_id == payload_binding.artifact_id
        and item.reason_code == "used:g2d_observed_work_input"
    )
    lifecycle_ref = next(
        item
        for item in bundle.causal_consumption_refs
        if item.source_artifact_id == lifecycle_binding.artifact_id
        and item.reason_code == "used:g2d_observed_work_input"
    )
    payload_mutation = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "payload", "value": 2},
        trace_ref="trace:e4c001:payload",
        predecessor=family["payload_baseline"],
    )
    used = fr.validate_runtime_observed_work_counterfactual_v02(
        execution_bundle=bundle,
        observed_work_causal_ref=payload_ref,
        mutated_observed_source_artifact=payload_mutation,
    )
    assert used.status == "PASS"
    assert used.validation_target == "CAUSAL_COUNTERFACTUAL"
    assert used.failure_stage == "NONE"
    assert used.validated_object_id is not None
    assert used.validated_object_id.startswith("frcounterfactual_v02:")
    used_material = captured_material[-1]
    assert tuple(used_material) == (
        "baseline",
        "candidate",
        "preserved",
        "profile",
    )
    assert tuple(used_material["baseline"]) == (
        "affected_cell_input_ids",
        "affected_result_artifact_ids",
        "binding_artifact_ids",
        "direct_initial_queue_artifact_ids",
        "observed_work_context_id",
        "report_artifact_id",
        "runtime_report_id",
        "runtime_trace_id",
    )
    assert tuple(used_material["candidate"]) == (
        "affected_cell_input_ids",
        "affected_result_artifact_ids",
        "binding_artifact_ids",
        "blocked_by_gate_causal_refs",
        "counterfactual_disposition",
        "direct_initial_queue_artifact_ids",
        "mutated_observed_source_artifact",
        "observed_work_causal_ref",
        "observed_work_context_id",
        "report_artifact_id",
        "runtime_report_id",
        "runtime_trace_id",
    )
    assert tuple(used_material["preserved"]) == (
        "ordered_unaffected_artifact_ids",
        "route_eligibility_artifact_id",
        "runtime_source_binding_id",
        "topology_artifact_id",
        "topology_id",
    )
    assert used_material["profile"] == {
        "counterfactual_profile_id": (
            "fractal_runtime_observed_work_counterfactual_v02"
        ),
        "counterfactual_profile_version": "v0.2",
        "validation_target": "CAUSAL_COUNTERFACTUAL",
    }
    assert used_material["candidate"]["counterfactual_disposition"] == "USED"
    assert used_material["candidate"]["blocked_by_gate_causal_refs"] == []
    assert all(
        used_material["candidate"][key] is not None
        for key in (
            "runtime_trace_id",
            "runtime_report_id",
            "report_artifact_id",
        )
    )
    assert used.validated_object_id == (
        "frcounterfactual_v02:"
        + domain_separated_sha256_hex_v01(
            domain=(
                "HEDGEHOG_FRACTAL_RUNTIME_V02_"
                "OBSERVED_WORK_COUNTERFACTUAL"
            ),
            payload=canonical_json_bytes_v01(used_material),
        )
    )
    assert fr.validate_runtime_observed_work_counterfactual_v02(
        execution_bundle=bundle,
        observed_work_causal_ref=payload_ref,
        mutated_observed_source_artifact=payload_mutation,
    ) == used
    blocked_mutation = _e4c001_source_artifact_v02(
        baseline,
        payload={"source_class": "lifecycle", "value": "stable"},
        trace_ref="trace:e4c001:lifecycle",
        predecessor=family["lifecycle_baseline"],
        lifecycle_state="BLOCKED_FAIL_CLOSED",
    )
    blocked = fr.validate_runtime_observed_work_counterfactual_v02(
        execution_bundle=bundle,
        observed_work_causal_ref=lifecycle_ref,
        mutated_observed_source_artifact=blocked_mutation,
    )
    assert blocked.status == "PASS"
    assert blocked.validated_object_id is not None
    assert blocked.validated_object_id.startswith("frcounterfactual_v02:")
    assert blocked.validated_object_id != used.validated_object_id
    blocked_material = captured_material[-1]
    assert blocked_material["candidate"]["counterfactual_disposition"] == (
        "BLOCKED_BY_GATE"
    )
    blocked_refs = blocked_material["candidate"][
        "blocked_by_gate_causal_refs"
    ]
    assert len(blocked_refs) == 1
    blocked_ref = blocked_refs[0]
    assert blocked_ref["source_artifact_id"] in blocked_material[
        "candidate"
    ]["binding_artifact_ids"]
    assert blocked_ref["source_artifact_id"] not in blocked_material[
        "baseline"
    ]["binding_artifact_ids"]
    assert (
        blocked_ref["downstream_artifact_id"]
        == lifecycle_ref.downstream_artifact_id
    )
    assert blocked_ref["output_field"] == lifecycle_ref.output_field
    assert blocked_ref["decision_effect"] == "OBSERVED_WORK_INPUT"
    assert blocked_ref["disposition"] == "BLOCKED_BY_GATE"
    assert blocked_ref["reason_code"] == "gate:g2d_observed_work_input"
    assert all(
        blocked_material["candidate"][key] is None
        for key in (
            "runtime_trace_id",
            "runtime_report_id",
            "report_artifact_id",
        )
    )
    assert blocked.validated_object_id == (
        "frcounterfactual_v02:"
        + domain_separated_sha256_hex_v01(
            domain=(
                "HEDGEHOG_FRACTAL_RUNTIME_V02_"
                "OBSERVED_WORK_COUNTERFACTUAL"
            ),
            payload=canonical_json_bytes_v01(blocked_material),
        )
    )
    assert fr.validate_fractal_runtime_causal_counterfactual_v02(
        execution_bundle=bundle,
        causal_ref=payload_ref,
        mutated_source_artifact=payload_mutation,
    ).status == "FAIL_CLOSED"
    assert fr.validate_runtime_observed_work_counterfactual_v02(
        execution_bundle=bundle,
        observed_work_causal_ref=replace(
            payload_ref,
            decision_effect="OBSERVED_WORK_CELL_BINDING",
        ),
        mutated_observed_source_artifact=payload_mutation,
    ).status == "FAIL_CLOSED"

    selected_input = family["selected_input"]
    assert isinstance(selected_input, fr.FractalCellInputV02)
    second_node = next(
        item
        for item in baseline.topology_nodes
        if item.node_id == selected_input.ordered_node_ids[1]
    )
    second_payload_binding = (
        fr.project_runtime_observed_work_binding_kernel_artifact_v02(
            baseline_execution_bundle=baseline,
            node=second_node,
            cell_input=selected_input,
            baseline_source_artifact=family["payload_baseline"],
            observed_source_artifact=family["payload_observed"],
            changed_full_artifact_pointers=("/payload/value",),
            execution_scope="SELECTIVE",
        )
    )
    shared_source_context = fr.build_runtime_observed_work_context_v02(
        baseline_execution_bundle=baseline,
        direct_source_artifacts=family["direct_sources"],
        supporting_artifacts=(),
        binding_artifacts=(
            *context.ordered_binding_artifacts,
            second_payload_binding,
        ),
        execution_scope="SELECTIVE",
    )
    shared_source_bundle = fr._d4_run_runtime_v02(
        baseline.source_context,
        observed_work_context=shared_source_context,
    )
    shared_payload_ref = next(
        item
        for item in shared_source_bundle.causal_consumption_refs
        if item.source_artifact_id == payload_binding.artifact_id
        and item.reason_code == "used:g2d_observed_work_input"
    )
    assert fr.validate_runtime_observed_work_counterfactual_v02(
        execution_bundle=shared_source_bundle,
        observed_work_causal_ref=shared_payload_ref,
        mutated_observed_source_artifact=payload_mutation,
    ).status == "PASS"


def test_e4c001_v03_historical_none_and_whole_run_escalation_call_accounting_v02(
    e4c001_observed_work_family_v02: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family = e4c001_observed_work_family_v02
    baseline = family["baseline"]
    whole_context = family["whole_context"]
    selective_context = family["selective_context"]
    assert isinstance(baseline, fr.FractalRuntimeExecutionBundleV02)
    assert isinstance(whole_context, fr.RuntimeObservedWorkContextV02)
    assert isinstance(selective_context, fr.RuntimeObservedWorkContextV02)
    assert baseline.observed_work_context is None
    assert whole_context.execution_scope == "WHOLE_RUN_ESCALATION"
    assert whole_context.whole_run_escalation_reason == (
        "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
    )
    assert whole_context.whole_run_escalation_policy_id is None
    assert fr.validate_runtime_observed_work_context_v02(
        whole_context
    ).status == "PASS"
    assert fr.validate_runtime_observed_work_context_against_sources_v02(
        whole_context,
        baseline_execution_bundle=baseline,
        direct_source_artifacts=family["full_direct_sources"],
        supporting_artifacts=(),
        binding_artifacts=family["whole_bindings"],
    ).status == "PASS"
    baseline_work_rows = tuple(
        (node_id, cell_input.cell_id)
        for cell_input in baseline.cell_inputs
        for node_id in cell_input.ordered_node_ids
    )
    binding_rows = tuple(
        (
            _kernel_payload(binding)["topology_binding"]["node_ref"],
            _kernel_payload(binding)["topology_binding"]["cell_ref"],
        )
        for binding in whole_context.ordered_binding_artifacts
    )
    assert len(binding_rows) == len(baseline_work_rows)
    assert set(binding_rows) == set(baseline_work_rows)
    assert whole_context.ordered_direct_affected_node_ids == tuple(
        item.node_id for item in baseline.topology_nodes
    )
    assert whole_context.ordered_execution_node_ids == tuple(
        item.node_id for item in baseline.topology_nodes
    )
    assert whole_context.ordered_affected_cell_ids == tuple(
        item.cell_id for item in baseline.cell_inputs
    )
    whole_plain = fr.runtime_observed_work_context_to_plain_data_v02(
        whole_context
    )
    assert whole_plain["whole_run_escalation_reason"] == (
        "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
    )
    assert whole_plain["whole_run_escalation_policy_id"] is None
    identity_material = dict(whole_plain)
    identity_material.pop("observed_work_context_id")
    assert whole_context.observed_work_context_id == (
        "frobservedctx_v02:"
        + domain_separated_sha256_hex_v01(
            domain="HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_CONTEXT",
            payload=canonical_json_bytes_v01(identity_material),
        )
    )
    for binding in whole_context.ordered_binding_artifacts:
        execution = _kernel_payload(binding)["execution"]
        assert execution == {
            "execution_scope": "WHOLE_RUN_ESCALATION",
            "whole_run_escalation_policy_id": None,
            "whole_run_escalation_reason": (
                "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
            ),
        }
        assert validate_kernel_artifact_v01(binding) == ()
    whole_support_by_id = {
        item.artifact_id: item
        for item in whole_context.ordered_supporting_artifacts
    }
    baseline_support_by_id = {
        item.artifact_id: item
        for item in (
            *baseline.queue_artifacts,
            *baseline.result_artifacts,
            baseline.report_artifact,
        )
    }
    child_activation_parent_ids = {
        _kernel_payload(binding)["topology_binding"][
            "activation_parent_queue_artifact_ref"
        ]
        for binding in whole_context.ordered_binding_artifacts
        if _kernel_payload(binding)["topology_binding"][
            "activation_parent_queue_artifact_ref"
        ]
        is not None
    }
    assert child_activation_parent_ids
    assert child_activation_parent_ids.issubset(whole_support_by_id)
    assert set(whole_support_by_id).issubset(baseline_support_by_id)
    assert all(
        artifact == baseline_support_by_id[artifact.artifact_id]
        for artifact in whole_context.ordered_supporting_artifacts
    )
    internal_runtime_calls = 0
    original_runtime = fr._d4_run_runtime_v02

    def counted_internal_runtime(
        source_context: fr.FractalRuntimeSourceContextV02,
        *,
        observed_work_context: fr.RuntimeObservedWorkContextV02 | None = None,
    ) -> fr.FractalRuntimeExecutionBundleV02:
        nonlocal internal_runtime_calls
        internal_runtime_calls += 1
        return original_runtime(
            source_context,
            observed_work_context=observed_work_context,
        )

    monkeypatch.setattr(fr, "_d4_run_runtime_v02", counted_internal_runtime)
    whole_bundle, whole_report = fr.run_fractal_runtime_v02(
        baseline.source_context,
        observed_work_context=whole_context,
    )
    assert isinstance(whole_bundle, fr.FractalRuntimeExecutionBundleV02)
    assert whole_report.status == "PASS"
    assert whole_bundle.observed_work_context == whole_context
    rejected_bundle, rejected_report = fr.run_fractal_runtime_v02(
        baseline.source_context,
        observed_work_context=selective_context,
    )
    assert rejected_bundle is None
    assert rejected_report.status == "FAIL_CLOSED"
    assert rejected_report.reason_codes == (
        "g2d_topology_source_binding_invalid",
    )
    assert internal_runtime_calls == 1
    initial_rows = tuple(
        (entry, artifact)
        for entry, artifact in zip(
            whole_bundle.queue_entries,
            whole_bundle.queue_artifacts,
            strict=True,
        )
        if entry.predecessor_queue_entry_id is None
    )
    initial_artifact_ids = {artifact.artifact_id for _entry, artifact in initial_rows}
    for binding in whole_context.ordered_binding_artifacts:
        topology_binding = _kernel_payload(binding)["topology_binding"]
        matching = tuple(
            artifact
            for entry, artifact in initial_rows
            if entry.node_id == topology_binding["node_ref"]
            and entry.cell_id == topology_binding["cell_ref"]
            and binding.artifact_id in artifact.parent_refs
        )
        assert len(matching) == 1
        assert all(
            binding.artifact_id not in artifact.parent_refs
            for entry, artifact in initial_rows
            if (
                entry.node_id,
                entry.cell_id,
            )
            != (
                topology_binding["node_ref"],
                topology_binding["cell_ref"],
            )
        )
    assert all(
        whole_context.observed_work_context_id in item.context_refs
        for item in whole_bundle.cell_inputs
    )
    assert initial_artifact_ids.issubset(
        set(whole_bundle.runtime_trace.abi_artifact_refs)
    )
    assert whole_bundle.runtime_report.runtime_trace_id == (
        whole_bundle.runtime_trace.trace_id
    )
    assert whole_bundle.report_artifact.trace_refs[0] == (
        whole_bundle.runtime_trace.trace_id
    )
    assert whole_bundle.report_artifact.parent_refs == (
        whole_bundle.topology_artifact.artifact_id,
        *(item.artifact_id for item in whole_bundle.result_artifacts),
    )
    observed_refs = tuple(
        item
        for item in whole_bundle.causal_consumption_refs
        if item.decision_effect
        in {"OBSERVED_WORK_INPUT", "OBSERVED_WORK_CELL_BINDING"}
    )
    assert observed_refs
    assert {
        item.artifact_id for item in whole_context.ordered_binding_artifacts
    } == {item.source_artifact_id for item in observed_refs}
    assert all(
        item.downstream_artifact_id in initial_artifact_ids
        and item.trace_refs[-1] == whole_bundle.runtime_trace.trace_id
        for item in observed_refs
    )
    stage_c = _d4_bundle_artifacts(whole_bundle)[2]
    assert fr.validate_fractal_runtime_causal_consumption_refs_v02(
        whole_bundle.causal_consumption_refs,
        **_d4_validation_kwargs(whole_bundle),
        stage_d_c_artifacts=stage_c,
        observed_work_context=whole_context,
    ).status == "PASS"
    assert whole_context.root_review_required is True
    assert all(
        getattr(whole_context, name) == 0
        for name in (
            "provider_calls",
            "model_calls",
            "network_calls",
            "connector_calls",
            "external_drs_calls",
            "real_world_effects_count",
        )
    )
    assert all(
        getattr(whole_context, name) is False
        for name in (
            "authority_created",
            "permission_created",
            "action_commit_packet_created",
            "receipt_created",
            "final_output_created",
            "drs_write_created",
        )
    )
    assert fr.validate_fractal_runtime_execution_bundle_v02(
        whole_bundle
    ).status == "PASS"
    invalid_complete_contexts = (
        replace(
            whole_context,
            ordered_execution_node_ids=(
                whole_context.ordered_execution_node_ids[:-1]
            ),
        ),
        replace(
            whole_context,
            whole_run_escalation_policy_id="foreign_policy_v02",
        ),
    )
    for invalid_context in invalid_complete_contexts:
        assert fr.validate_fractal_runtime_execution_bundle_v02(
            replace(whole_bundle, observed_work_context=invalid_context)
        ).status == "FAIL_CLOSED"


D5_CASE_ORDER_V02 = (
    "g2d_case:travel:memory_informed:v02",
    "g2d_case:travel:local_slm:v02",
    "g2d_case:travel:cloud_llm_narrow:v02",
    "g2d_case:travel:full_semantic:v02",
    "g2d_case:travel:full_fractal:v02",
    "g2d_case:warehouse:memory_informed:v02",
    "g2d_case:warehouse:local_slm:v02",
    "g2d_case:warehouse:cloud_llm:v02",
    "g2d_case:warehouse:full_semantic:v02",
    "g2d_case:warehouse:full_fractal:v02",
    "g2d_case:negative:deterministic_shortcut:v02",
    "g2d_case:negative:sealed_replay_shortcut:v02",
    "g2d_case:negative:direct_reuse_shortcut:v02",
    "g2d_case:negative:blocked_terminal:v02",
    "g2d_case:negative:needs_user_terminal:v02",
    "g2d_case:negative:root_reject_terminal:v02",
    "g2d_case:negative:direct_root_decision:v02",
    "g2d_case:negative:route_substitution:v02",
    "g2d_case:negative:cross_domain_source:v02",
    "g2d_case:negative:foreign_id_only:v02",
    "g2d_case:negative:scope_widening:v02",
    "g2d_case:negative:capability_widening:v02",
    "g2d_case:negative:fractal_capability_missing:v02",
    "g2d_case:negative:mode_upgrade:v02",
    "g2d_case:negative:mode_downgrade:v02",
    "g2d_case:negative:g2b_instruction_authority:v02",
    "g2d_case:negative:g2a_history_authority:v02",
    "g2d_case:negative:depth_overflow:v02",
    "g2d_case:negative:fan_out_overflow:v02",
    "g2d_case:negative:total_cell_overflow:v02",
    "g2d_case:parallelism_backpressure:v02",
    "g2d_case:negative:token_budget_overflow:v02",
    "g2d_case:negative:time_budget_overflow:v02",
    "g2d_case:negative:provider_budget_overflow:v02",
    "g2d_case:negative:scope_budget_monotonic_matrix:v02",
    "g2d_case:negative:revise_count_overflow:v02",
    "g2d_case:no_progress_deadend:v02",
    "g2d_case:resolvable_missing_input:v02",
    "g2d_case:required_child_partial:v02",
    "g2d_case:required_child_hard_failure:v02",
    "g2d_case:negative:child_authority_claims:v02",
    "g2d_case:repeated_canonical_equality:v02",
    "g2d_case:identity:acyclic_graph_rebuild:v02",
    "g2d_case:negative:queue_predecessor_substitution:v02",
    "g2d_case:deterministic:post_vv_gt_injected_time:v02",
    "g2d_case:causal:used_field_counterfactual:v02",
    "g2d_case:causal:blocked_and_ignored_dispositions:v02",
    "g2d_case:identity:child_result_partial_failure_postorder:v02",
    "g2d_case:identity:pre_result_validation_no_cycle:v02",
    "g2d_case:runtime:node_work_queue_cell_aggregation:v02",
    "g2d_case:runtime:five_mode_exact_template_rows:v02",
    "g2d_case:source:selected_profile_capability_scope_binding:v02",
    "g2d_case:budget:allocation_predecessor_debit_matrix:v02",
    "g2d_case:validation:resultproposal_postvv_gt_outcome_matrix:v02",
    "g2d_case:transition:root_only_parent_return:v02",
    "g2d_case:abi:complete_field_partition_and_trace:v02",
    "g2d_case:causal:exact_pointer_reason_bundle:v02",
    "g2d_case:queue:backpressure_precedence:v02",
    "g2d_case:identity:policy_profile_separation:v02",
    "g2d_case:runtime:full_fractal_leaf_edge_projection:v02",
    "g2d_case:budget:cell_global_event_pairing:v02",
    "g2d_case:abi:pre_root_lifecycle_boundary:v02",
    "g2d_case:validation:context_unique_gt_report_ids:v02",
    "g2d_case:validation:pass_none_stage_contract:v02",
    "g2d_case:queue:instance_snapshot_round_and_blocked_reason:v02",
    "g2d_case:runtime:child_slot_input_node_outcome_order:v02",
    "g2d_case:validation:root_result_report_and_slice_surface:v02",
    "g2d_case:budget:typed_event_and_child_allocation_context:v02",
    "g2d_case:runtime:planned_child_activation_boundary:v02",
    "g2d_case:transition:prestate_decision_budget_queue_order:v02",
    "g2d_case:revise:observation_before_t07_and_budget:v02",
    "g2d_case:bundle:prebundle_validation_causal_final_assembly:v02",
)

D5_CONSTRUCTIVE_CASE_NUMBERS_V02 = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 42, 43, 45, 46, 48, 49, 50, 51,
    52, 53, 54, 55, 56, 57, 59, 60, 61, 63, 64, 66, 67, 68, 69, 70,
    71, 72,
)

D5_NEGATIVE_CASE_NUMBERS_V02 = (
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 44,
    47, 58, 62, 65,
)


@pytest.fixture(scope="module")
def d5_fractal_runtime_report_v02() -> d5_runner.FractalRuntimeG2DReportV02:
    report = d5_runner.collect_fractal_runtime_g2_d_v02()
    assert d5_runner.validate_fractal_runtime_g2_d_report_v02(report) == ()
    return report


def _d5_material_v02(
    row: d5_runner.FractalRuntimeG2DCaseResultV02,
) -> dict[str, object]:
    value = json.loads(row.evidence_material_json)
    assert type(value) is dict
    return value


def _d5_proof_v02(
    row: d5_runner.FractalRuntimeG2DCaseResultV02,
) -> dict[str, object]:
    value = _d5_material_v02(row)["proof"]
    assert type(value) is dict
    return value


def _d5_details_v02(
    row: d5_runner.FractalRuntimeG2DCaseResultV02,
) -> dict[str, object]:
    value = _d5_proof_v02(row)["details"]
    assert type(value) is dict
    return value


def _d5_json_value_v02(value: object) -> bool:
    if value is None or type(value) in {bool, int, float, str}:
        return True
    if type(value) is list:
        return all(_d5_json_value_v02(item) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and _d5_json_value_v02(item)
            for key, item in value.items()
        )
    return False


def _d5_coherently_tampered_report_v02(
    report: d5_runner.FractalRuntimeG2DReportV02,
    *,
    case_number: int,
    mutate: object,
) -> d5_runner.FractalRuntimeG2DReportV02:
    if not callable(mutate):
        raise TypeError("d5_tamper_callback_invalid")
    position = case_number - 1
    row = report.case_results[position]
    material = _d5_material_v02(row)
    proof = material["proof"]
    assert type(proof) is dict and type(proof["details"]) is dict
    mutate(proof["details"])
    proof["details_sha256"] = d5_runner._sha256_plain_v02(proof["details"])
    material["proof"] = proof
    evidence_bytes = canonical_json_bytes_v01(material)
    changed_row = replace(
        row,
        evidence_material_json=evidence_bytes.decode("ascii"),
        evidence_sha256=hashlib.sha256(evidence_bytes).hexdigest(),
    )
    rows = (
        *report.case_results[:position],
        changed_row,
        *report.case_results[position + 1:],
    )
    changed_report = replace(report, report_id="", case_results=rows)
    return replace(
        changed_report,
        report_id=d5_runner._report_identity_v02(changed_report),
    )


def test_d5_public_runner_surface_and_exact_case_order_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    assert d5_runner.__all__ == (
        "FractalRuntimeG2DCaseResultV02",
        "FractalRuntimeG2DReportV02",
        "collect_fractal_runtime_g2_d_v02",
        "validate_fractal_runtime_g2_d_report_v02",
        "fractal_runtime_g2_d_report_to_plain_data_v02",
        "render_fractal_runtime_g2_d_v02",
        "main",
    )
    assert inspect.isclass(d5_runner.FractalRuntimeG2DCaseResultV02)
    assert inspect.isclass(d5_runner.FractalRuntimeG2DReportV02)
    assert all(
        inspect.isfunction(getattr(d5_runner, name))
        for name in d5_runner.__all__[2:]
    )
    assert report.case_order == D5_CASE_ORDER_V02
    assert tuple(item.case_id for item in report.case_results) == D5_CASE_ORDER_V02
    assert len(report.case_results) == len(set(report.case_order)) == 72
    assert tuple(
        index + 1
        for index, item in enumerate(report.case_results)
        if item.case_class == "CONSTRUCTIVE"
    ) == D5_CONSTRUCTIVE_CASE_NUMBERS_V02
    assert tuple(
        index + 1
        for index, item in enumerate(report.case_results)
        if item.case_class == "NEGATIVE"
    ) == D5_NEGATIVE_CASE_NUMBERS_V02
    assert len(d5_runner._PROOF_CONTRACTS_V02) == 72
    assert len(d5_runner._DETAIL_KEY_CONTRACTS_V02) == 72
    for position, row in enumerate(report.case_results):
        proof = _d5_proof_v02(row)
        contract = d5_runner._PROOF_CONTRACTS_V02[row.case_id]
        assert set(proof) == {
            "proof_kind", "axis", "executor", "observed_source",
            "matrix_cardinality", "accepted_bundle_required", "details",
            "details_sha256",
        }
        assert proof["proof_kind"] == contract.proof_kind
        assert proof["axis"] == contract.axis
        assert proof["executor"] == contract.executor
        assert proof["observed_source"] == contract.observed_source
        assert proof["matrix_cardinality"] == contract.matrix_cardinality
        assert set(_d5_details_v02(row)) == d5_runner._DETAIL_KEY_CONTRACTS_V02[row.case_id]
        assert d5_runner._proof_contract_valid_v02(
            case_result=row,
            proof=proof,
            position=position,
        )

    runner_source = Path(d5_runner.__file__).read_text(encoding="utf-8")
    runner_tree = ast.parse(runner_source)
    forbidden_assignments = tuple(
        item
        for item in ast.walk(runner_tree)
        if (
            isinstance(item, ast.keyword)
            and item.arg == "observed_outcome"
            or isinstance(item, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name)
                and target.id in {"observed", "observed_outcome"}
                for target in (
                    item.targets if isinstance(item, ast.Assign) else (item.target,)
                )
            )
        )
        and any(
            isinstance(child, ast.Attribute)
            and isinstance(child.value, ast.Name)
            and child.value.id == "spec"
            and child.attr == "expected_outcome"
            for child in ast.walk(item)
        )
    )
    assert forbidden_assignments == ()
    assert "_SOURCE_SUBSTITUTION_FIELDS" not in runner_source
    assert "structural_corruption_created" not in runner_source
    matrix_function = next(
        item
        for item in runner_tree.body
        if isinstance(item, ast.FunctionDef)
        and item.name == "_populate_accepted_matrix_proof_v02"
    )
    assert any(
        isinstance(item, ast.Attribute)
        and item.attr == "cell_projection_class"
        for item in ast.walk(matrix_function)
    )


def test_d5_two_domain_positive_determinism_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    positive = report.case_results[:10]
    assert report.domain_order == (
        "TRAVEL_POLICY_INFORMATION",
        "WAREHOUSE_MAINTENANCE_INFORMATION",
    )
    assert tuple((item.domain_id, item.accepted_mode) for item in positive) == (
        *((report.domain_order[0], mode) for mode in fr.TOPOLOGY_ELIGIBLE_MODES),
        *((report.domain_order[1], mode) for mode in fr.TOPOLOGY_ELIGIBLE_MODES),
    )
    assert all(item.observed_outcome == "COMPLETED" for item in positive)
    assert all(item.final_status == "PASS" and item.reason_codes == () for item in positive)
    assert all(item.topology_created_count == 1 for item in positive)
    assert len({item.topology_id for item in positive}) == 10
    assert len({item.runtime_report_id for item in positive}) == 10
    assert len({item.source_family_sha256 for item in positive}) == 10
    travel_cloud = positive[2]
    warehouse_cloud = positive[7]
    assert _d5_details_v02(travel_cloud)["root_outcome"] == "NARROW"
    assert _d5_details_v02(warehouse_cloud)["root_outcome"] == "ACCEPT"
    assert len(_d5_details_v02(positive[4])["child_cell_input_ids"]) == 2
    assert len(_d5_details_v02(positive[9])["child_cell_input_ids"]) == 2
    assert all(
        _d5_details_v02(item)["child_cell_input_ids"] == []
        for item in (*positive[:4], *positive[5:9])
    )
    assert all(
        _d5_details_v02(item)["zero_runtime_counters"] == [0] * 12
        for item in positive
    )


def test_d5_complete_negative_matrix_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    negative_rows = tuple(
        item for item in report.case_results if item.case_class == "NEGATIVE"
    )
    assert len(negative_rows) == 36
    assert all(item.observed_outcome == item.expected_outcome for item in negative_rows)
    assert all(item.final_status == "PASS" and item.reason_codes == () for item in negative_rows)
    for case_number in range(11, 28):
        row = report.case_results[case_number - 1]
        proof = _d5_proof_v02(row)
        details = _d5_details_v02(row)
        assert proof["proof_kind"] == "SOURCE_EXACT_AXIS_FAIL_CLOSED"
        assert proof["axis"] == d5_runner._SOURCE_NEGATIVE_AXIS_ROWS_V02[case_number - 11][1]
        assert details["case_number"] == case_number
        assert details["mutated_path"] == d5_runner._SOURCE_NEGATIVE_MUTATED_PATHS_V02[case_number - 11]
        assert details["baseline_sha256"] != details["attempted_sha256"]
        assert details["validation_target"] == "SOURCE_CONTEXT_STRUCTURAL"
        assert details["failure_stage"] == "SOURCE_CONTEXT"
        assert details["validation_report_id"] in row.evidence_refs
        assert details["external_validation_report_id"] in row.evidence_refs
        assert details["reason_codes"] and details["external_reason_codes"]
        assert details["topology_created_delta"] == 0
        assert details["bundle_created_delta"] == 0
        assert details["created_before"] == details["created_after"] == {
            "bundle_report_ids": [], "topology_ids": [],
        }
    for case_number in range(28, 42):
        row = report.case_results[case_number - 1]
        proof = _d5_proof_v02(row)
        details = _d5_details_v02(row)
        assert proof["proof_kind"] == "BOUNDED_ACTUAL_EXECUTION"
        assert proof["executor"] == d5_runner._BOUNDED_NEGATIVE_AXIS_ROWS_V02[case_number - 28][2]
        assert details["case_number"] == case_number
        assert details["policy_id"] in row.evidence_refs
        assert details["accepted_bundle_validation_id"] in row.evidence_refs
        if case_number == 28:
            assert details["accepted_depths"] == [0, 1, 2]
            assert [item["depth"] for item in details["accepted_depth_rows"]] == [
                0, 1, 2,
            ]
            assert all(
                item["status"] == "PASS"
                and item["cell_input_id"] in row.evidence_refs
                and item["validation_report_id"] in row.evidence_refs
                for item in details["accepted_depth_rows"]
            )
            assert details["accepted_depth_rows"][0]["parent_cell_id"] is None
            assert (
                details["accepted_depth_rows"][1]["parent_cell_id"]
                == details["accepted_depth_rows"][0]["cell_id"]
            )
            assert (
                details["accepted_depth_rows"][2]["parent_cell_id"]
                == details["accepted_depth_rows"][1]["cell_id"]
            )
            assert details["rejected_depth"] == 3
            assert (
                details["rejected_parent_cell_id"]
                == details["accepted_depth_rows"][2]["cell_id"]
            )
            assert details["rejected_input_id"] in row.evidence_refs
            assert details["rejected_validation_report_id"] in row.evidence_refs
            assert details["rejected_reason_codes"]
            assert details["rejected_runtime_object_delta"]["created_count"] == 0
        elif case_number == 30:
            assert details["max_total_cells"] == 21
            assert details["tree_shape"] == [1, 4, 16]
            assert details["depth_counts"] == {"0": 1, "1": 4, "2": 16}
            assert len(details["cell_rows"]) == 21
            assert [item["cell_depth"] for item in details["cell_rows"]].count(0) == 1
            assert [item["cell_depth"] for item in details["cell_rows"]].count(1) == 4
            assert [item["cell_depth"] for item in details["cell_rows"]].count(2) == 16
            assert details["cell_rows"][0]["cell_id"] == details["root_cell_id"]
            assert details["cell_rows"][0]["parent_cell_id"] is None
            assert [
                item["cell_id"]
                for item in details["cell_rows"]
                if item["cell_depth"] == 1
            ] == details["depth_1_cell_ids"]
            assert [
                item["cell_id"]
                for item in details["cell_rows"]
                if item["cell_depth"] == 2
            ] == details["depth_2_cell_ids"]
            assert {
                item["parent_cell_id"]
                for item in details["parent_child_rows"]
                if item["child_depth"] == 1
            } == {details["root_cell_id"]}
            assert {
                item["parent_cell_id"]
                for item in details["parent_child_rows"]
                if item["child_depth"] == 2
            } == set(details["depth_1_cell_ids"])
            for parent_id in (
                details["root_cell_id"],
                *details["depth_1_cell_ids"],
            ):
                assert sorted(
                    item["canonical_child_index"]
                    for item in details["parent_child_rows"]
                    if item["parent_cell_id"] == parent_id
                ) == [0, 1, 2, 3]
            assert all(
                item["cell_input_validation_status"] == "PASS"
                and item["cell_input_id"] in row.evidence_refs
                and item["cell_input_validation_report_id"] in row.evidence_refs
                for item in details["cell_rows"]
            )
            assert [item[0] for item in details["root_budget_event_rows"]] == [
                "INITIAL_ALLOCATION", "ACTIVATE", "CELL_CREATE",
            ]
            assert [item[2] for item in details["root_budget_event_rows"]] == [0, 0, 1]
            assert len(details["accepted_cell_rows"]) == 20
            assert [item["cell_number"] for item in details["accepted_cell_rows"]] == list(
                range(2, 22)
            )
            assert len(details["accepted_cell_ids"]) == 21
            assert len(set(details["accepted_cell_ids"])) == 21
            assert details["accepted_cell_ids"] == [
                item["cell_id"] for item in details["cell_rows"]
            ]
            assert details["planning_debit_count"] == 0
            assert details["allocation_debit_count"] == 0
            assert details["activate_debit_count"] == 0
            assert details["cell_create_debit_count"] == 21
            assert all(
                item["planning_validation_status"] == "FAIL_CLOSED"
                and item["planning_reason_codes"]
                and item["global_activate_consumed_cell_count"]
                == item["global_before_consumed_cell_count"]
                and item["global_create_consumed_cell_count"]
                == item["global_activate_consumed_cell_count"] + 1
                for item in details["accepted_cell_rows"]
            )
            assert details["twenty_first_consumed_cell_count"] == 21
            assert details["twenty_first_remaining_cell_count"] == 0
            assert details["attempted_twenty_second_error"] == "g2d_budget_overflow"
            assert (
                details["attempted_twenty_second_parent_id"]
                == details["root_cell_id"]
            )
            assert details["attempted_twenty_second_global_budget_created"] is False
            assert details["rejected_budget_id"] in row.evidence_refs
            assert details["rejected_validation_report_id"] in row.evidence_refs
            assert details["rejected_reason_codes"]
            assert details["rejected_runtime_object_delta"]["created_count"] == 0
        elif case_number in {29, 32, 33, 34}:
            assert details["validation_report_id"] in row.evidence_refs
            assert details["reason_codes"]
            assert details["created_objects"]["created_count"] == 0
        elif case_number == 31:
            assert details["validation_report_id"] in row.evidence_refs
            assert details["queue_capacity"] == (
                details["running_count"] + details["ready_count"]
            )
            assert details["deferred_queue_entry_ids"] == [
                details["deferred_source_queue_id"]
            ]
            assert details["deferred_state"] == "PENDING"
            assert details["predecessor_queue_id"] == details["deferred_source_queue_id"]
            assert details["queue_reason_codes"] == [
                "g2d_transition_backpressure_deferred"
            ]
            assert details["t03_decision_id"] in row.evidence_refs
            assert details["deferred_successor_queue_id"] in row.evidence_refs
            assert details["deferred_successor_artifact_id"] in row.evidence_refs
            assert details["created_objects"]["created_count"] == 2
            assert details["no_work_dropped"] is True
        elif case_number == 35:
            assert details["mutation_count"] == len(details["mutation_rows"]) == 12
            assert details["baseline_context_validation_id"] in row.evidence_refs
            assert all(item[1] in row.evidence_refs and item[2] for item in details["mutation_rows"])
            assert details["created_objects"]["created_count"] == 0
        elif case_number in {36, 37, 38}:
            assert details["queue_validation_report_id"] in row.evidence_refs
            assert details["observation_id"] in row.evidence_refs
            assert details["observation_validation_report_id"] in row.evidence_refs
            assert details["derived_terminal_state"] == row.observed_outcome
            assert details["reason_codes"]
            if case_number == 36:
                assert details["revision_index"] == details["max_revise_count"] + 1
                assert details["consecutive_non_positive_count"] == 0
            elif case_number == 37:
                assert details["revision_index"] <= details["max_revise_count"]
                assert (
                    details["consecutive_non_positive_count"]
                    == details["max_revise_count"]
                )
        elif case_number in {39, 40}:
            expected_outcome = "DEGRADED" if case_number == 39 else "BLOCKED"
            expected_reason = (
                "g2d_partial_failure_recorded"
                if case_number == 39
                else "g2d_required_child_failure"
            )
            assert details["child_input_id"] in row.evidence_refs
            assert details["attempted_outcome"] == expected_outcome
            assert len(details["terminal_queue_rows"]) == 4
            assert details["terminal_queue_rows"][0][1:] == [
                expected_outcome,
                [expected_reason],
            ]
            assert details["terminal_queue_rows"][-1][1:] == [
                expected_outcome,
                [expected_reason],
            ]
            assert details["result_proposal_id"] in row.evidence_refs
            assert details["post_vv_report_id"] in row.evidence_refs
            assert details["gt_report_id"] in row.evidence_refs
            assert details["proposal_validation_report_id"] in row.evidence_refs
            assert details["post_vv_validation_report_id"] in row.evidence_refs
            assert details["gt_validation_report_id"] in row.evidence_refs
            assert details["child_validation_report_id"] in row.evidence_refs
            assert details["child_structural_validation_report_id"] in row.evidence_refs
            assert details["result_artifact_id"] in row.evidence_refs
            assert details["activation_causal_row"][2] == "/planned_child_cell_id"
            assert details["activation_causal_row"][5:] == [
                "CHILD_ACTIVATION",
                "USED",
                "used:g2d_planned_child_activation",
            ]
            assert details["partial_failure_validation_report_id"] in row.evidence_refs
            assert details["parent_disposition"] == row.observed_outcome
            assert details["created_result_delta"]["created_ids"] == [
                details["attempted_child_result_id"]
            ]
            assert details["created_result_delta"]["created_count"] == 1
            assert details["created_partial_failure_delta"]["created_ids"] == [
                details["partial_failure_id"]
            ]
            assert details["created_partial_failure_delta"]["created_count"] == 1
            assert details["created_causal_delta"]["created_count"] == 0
            if case_number == 39:
                assert details["safe_sibling_result_id"] != details[
                    "attempted_child_result_id"
                ]
                assert details["safe_sibling_input_id"] in row.evidence_refs
                assert details["safe_sibling_result_id"] in row.evidence_refs
                assert details["safe_sibling_result_artifact_id"] in row.evidence_refs
                assert details["safe_sibling_outcome"] == "COMPLETED"
                assert details["safe_sibling_evidence_refs"]
                assert all(
                    item in row.evidence_refs
                    for item in details["safe_sibling_evidence_refs"]
                )
                assert details["safe_sibling_before_sha256"] == details[
                    "safe_sibling_after_sha256"
                ]
                assert details["safe_sibling_unchanged"] is True
                assert details["safe_sibling_result_delta"]["created_count"] == 0
                assert details["safe_sibling_causal_delta"]["created_count"] == 0
                assert details["partial_failure_sibling_independent"] is True
            else:
                assert details["gate_disposition"] == (
                    "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
                )
                assert details["gate_reason_codes"] == [
                    "g2d_required_child_failure"
                ]
                assert details["blocked_queue_id"] in row.evidence_refs
                assert details["blocked_artifact_id"] in row.evidence_refs
                assert details["blocked_validation_id"] in row.evidence_refs
                assert details["no_child_invocation_delta"]["created_count"] == 0
                assert details["no_child_result_delta"]["created_count"] == 0
                assert details["no_child_partial_failure_delta"]["created_count"] == 0
                assert details["no_child_terminal_delta"]["created_ids"] == [
                    details["blocked_queue_id"]
                ]
                assert details["merge_decision_is_none"] is True
                assert details["malformed_axis"] == (
                    "/current_entry/planned_child_cell_id"
                )
                assert details["malformed_reason_codes"]
                assert details["malformed_error"]
                assert details["malformed_terminal_delta"]["created_count"] == 0
                assert details["malformed_causal_delta"]["created_count"] == 0
                assert details["malformed_bundle_delta"]["created_count"] == 0
        else:
            assert details["mutation_count"] == len(details["mutation_rows"]) == 6
            assert all(item[1] in row.evidence_refs and item[2] for item in details["mutation_rows"])
            assert details["no_created_objects"]["created_count"] == 0


def test_d5_repeated_report_value_id_and_render_bytes_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    plain = d5_runner.fractal_runtime_g2_d_report_to_plain_data_v02(report)
    rebuilt = d5_runner._fractal_runtime_g2_d_report_from_plain_data_v02(plain)
    assert rebuilt == report
    assert rebuilt is not report
    assert d5_runner.validate_fractal_runtime_g2_d_report_v02(rebuilt) == ()
    assert d5_runner._report_identity_v02(replace(report, report_id="")) == report.report_id
    first = d5_runner.render_fractal_runtime_g2_d_v02(report)
    second = d5_runner.render_fractal_runtime_g2_d_v02(rebuilt)
    assert first == second
    assert first.endswith("\n") and not first.endswith("\n\n")
    rendered = json.loads(first)
    assert isinstance(rendered, dict)
    assert len(rendered["case_results"]) == 72
    assert _d5_json_value_v02(rendered)
    for item in report.case_results:
        material = json.loads(item.evidence_material_json)
        assert hashlib.sha256(canonical_json_bytes_v01(material)).hexdigest() == item.evidence_sha256
        proof = _d5_proof_v02(item)
        assert proof["details_sha256"] == d5_runner._sha256_plain_v02(proof["details"])
    repeated = _d5_details_v02(report.case_results[41])
    assert repeated["construction_call_count"] == 2
    assert repeated["first_report_id"] == repeated["second_report_id"]
    assert repeated["first_sha256"] == repeated["second_sha256"]
    assert repeated["repeated_value_equal"] is True
    assert repeated["repeated_id_equal"] is True
    assert repeated["repeated_bytes_equal"] is True


def test_d5_identity_postorder_template_queue_budget_time_abi_causal_matrices_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    required_numbers = (42, 43, 44, 45, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72)
    for case_number in required_numbers:
        row = report.case_results[case_number - 1]
        proof = _d5_proof_v02(row)
        details = _d5_details_v02(row)
        assert proof["proof_kind"] == "ACCEPTED_RUNTIME_EXECUTABLE_MATRIX"
        assert details["case_number"] == case_number
        assert details["complete_profile_validation_id"] in row.evidence_refs
        assert d5_runner._matrix_proof_valid_v02(
            number=case_number,
            details=details,
            evidence_refs=row.evidence_refs,
        )
    assert len(_d5_details_v02(report.case_results[43])["mutation_rows"]) == 10
    assert len(_d5_details_v02(report.case_results[50])["five_mode_template_rows"]) == 5
    assert _d5_details_v02(report.case_results[51])["total_substitution_count"] == 40
    assert len(_d5_details_v02(report.case_results[52])["mutation_rows"]) == 8
    assert _d5_details_v02(report.case_results[53])["outcome_count"] == 5
    assert _d5_details_v02(report.case_results[55])["field_partitions"] == [32, 31, 32, 42]
    assert len(_d5_details_v02(report.case_results[55])["queue_parent_form_names"]) == 6
    causal = _d5_details_v02(report.case_results[56])
    assert causal["activation_causal_row_count"] == 2
    assert causal["child_return_causal_row_count"] == 6
    backpressure = _d5_details_v02(report.case_results[57])
    assert len(backpressure["backpressure_precedence_rows"]) == 2
    assert len(backpressure["deferred_successor_rows"]) == 2
    assert backpressure["dependency_wait_row"][2:] == ["PENDING", [], True]
    assert backpressure["budget_blocked_row"][3:5] == [
        "BLOCKED",
        ["g2d_required_child_failure"],
    ]
    assert backpressure["budget_exhaustion_resource"] == "remaining_cell_count"
    assert backpressure["budget_exhaustion_tree_shape"] == [1, 4, 16]
    assert backpressure["budget_exhaustion_depth_counts"] == {
        "0": 1,
        "1": 4,
        "2": 16,
    }
    assert len(backpressure["budget_exhaustion_accepted_cell_ids"]) == 21
    assert len(set(backpressure["budget_exhaustion_accepted_cell_ids"])) == 21
    assert backpressure["budget_before_consumed_cell_count"] == 1
    assert backpressure["budget_before_remaining_cell_count"] == 20
    assert backpressure["exhausted_consumed_cell_count"] == 21
    assert backpressure["exhausted_remaining_cell_count"] == 0
    assert backpressure["budget_blocked_row"][6:] == [
        backpressure["exhausted_budget_id"],
        backpressure["exhausted_budget_validation_id"],
        backpressure["budget_exhaustion_t06_decision_id"],
    ]
    assert backpressure["budget_exhaustion_queue_delta"]["created_count"] == 2
    assert backpressure["budget_exhaustion_queue_delta"]["created_ids"][-1] == (
        backpressure["budget_blocked_row"][0]
    )
    assert backpressure["budget_exhaustion_budget_delta"]["created_count"] > 0
    assert backpressure["budget_exhaustion_no_drop"] is True
    assert backpressure["suppression_created_objects"]["created_count"] == 0
    assert backpressure["queue_order_error"]
    denied = _d5_details_v02(report.case_results[65])
    assert denied["denied_slot_state"] == "BLOCKED"
    assert denied["denied_gate_disposition"] == (
        "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
    )
    assert denied["denied_terminal_delta"]["created_ids"] == [
        denied["denied_slot_terminal_id"]
    ]
    assert denied["denied_invocation_delta"]["created_count"] == 0
    assert denied["denied_result_delta"]["created_count"] == 0
    assert denied["denied_partial_failure_delta"]["created_count"] == 0
    assert denied["merge_decision_is_none"] is True
    leaf = _d5_details_v02(report.case_results[59])
    assert [item[:5] for item in leaf["full_fractal_leaf_edges"]] == [
        [7, 0, 4, "VALIDATION", "FRACTAL_LEAF_PROJECTION"],
        [8, 4, 5, "VALIDATION", "FRACTAL_LEAF_PROJECTION"],
        [9, 5, 6, "RETURN", "FRACTAL_LEAF_PROJECTION"],
    ]
    four_child = _d5_details_v02(report.case_results[67])["four_child_structural_rows"]
    four_child_details = _d5_details_v02(report.case_results[67])
    assert len(four_child) == 4
    assert len({item["budget_id"] for item in four_child}) == 4
    assert all(item["budget_validation_id"] in report.case_results[67].evidence_refs for item in four_child)
    assert four_child_details["four_child_context_validation_status"] == "FAIL_CLOSED"
    assert "g2d_node_instance_geometry_invalid" in four_child_details["four_child_context_reason_codes"]
    assert four_child_details["four_child_runtime_projection_count"] == 0
    assert four_child_details["four_child_derivation_rows"] == [
        [0, 1], [1, 1], [0, 2], [1, 2],
    ]
    activation = _d5_details_v02(report.case_results[68])
    assert len(activation["activation_rows"]) == 2
    assert activation["valid_denial_disposition"] == (
        "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
    )
    assert activation["valid_denial_invocation_delta"]["created_count"] == 0
    assert activation["malformed_candidate_created_terminals"]["created_count"] == 0
    prestate = _d5_details_v02(report.case_results[69])
    assert prestate["parent_return_decision_rule_id"] == (
        "g2d_t08_validating_to_completed"
    )
    assert prestate["construction_dependency_rows"][0][0] == "DECISION"
    assert prestate["construction_dependency_rows"][1][0] == "QUEUE"
    assert prestate["construction_dependency_rows"][2][0] == "ARTIFACT"
    assert all(
        item[0] == "BUDGET"
        for item in prestate["construction_dependency_rows"][3:]
    )
    assert prestate["root_return_decision_position"] == (
        len(prestate["transition_decision_ids"]) - 1
    )
    assert prestate["post_hoc_mapping_count"] == 0
    assert len(_d5_details_v02(report.case_results[70])["mutation_rows"]) == 4


def test_d5_actual_artifact_counterfactual_profiles_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    used = d5_fractal_runtime_report_v02.case_results[45]
    ignored = d5_fractal_runtime_report_v02.case_results[46]
    used_proof = _d5_details_v02(used)
    ignored_proof = _d5_details_v02(ignored)
    assert used_proof["causal_ref"]["disposition"] == "USED"
    assert used_proof["changed_pointer"] == used_proof["causal_ref"]["output_field"]
    assert used_proof["counterfactual_validation_id"] in used.evidence_refs
    assert ignored_proof["ignored_causal_ref"]["disposition"] == "IGNORED_WITH_REASON"
    assert ignored_proof["ignored_counterfactual_validation_id"] in ignored.evidence_refs
    assert ignored_proof["admission_mutation_axis"] == (
        "/source_artifact/planned_child_cell_id"
    )
    assert ignored_proof["admission_accepted_causal_ref"]["decision_effect"] == (
        "CHILD_ACTIVATION"
    )
    assert ignored_proof["admission_accepted_causal_ref"]["disposition"] == "USED"
    assert ignored_proof["admission_profile_status"] == "PASS"
    assert ignored_proof["admission_profile_validation_id"] in ignored.evidence_refs
    assert ignored_proof["admission_error"]
    assert ignored_proof["admission_expected_downstream_artifact_id"] is None
    assert ignored_proof["admission_child_input_delta"]["created_count"] == 0
    assert ignored_proof["admission_initial_queue_delta"]["created_count"] == 0
    assert ignored_proof["admission_initial_artifact_delta"]["created_count"] == 0
    assert ignored_proof["actual_gate_disposition"] == (
        "VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL"
    )
    assert ignored_proof["actual_gate_reason_codes"] == [
        "g2d_required_child_failure"
    ]
    assert ignored_proof["actual_gate_t06_decision_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_validating_queue_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_validating_artifact_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_terminal_decision_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_blocked_queue_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_blocked_artifact_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_validation_id"] in ignored.evidence_refs
    assert ignored_proof["actual_gate_terminal_delta"]["created_ids"] == [
        ignored_proof["actual_gate_blocked_queue_id"]
    ]
    assert ignored_proof["actual_gate_invocation_delta"]["created_count"] == 0
    assert ignored_proof["actual_gate_downstream_delta"]["created_count"] == 0
    assert ignored_proof["blocked_gate_causal_ref"]["disposition"] == (
        "BLOCKED_BY_GATE"
    )
    assert ignored_proof["blocked_gate_causal_ref"]["output_field"] == (
        "/observed_output_refs/0"
    )
    assert ignored_proof["blocked_gate_causal_ref"]["decision_effect"] == (
        "CELL_RESULT_OUTPUT"
    )
    assert ignored_proof["blocked_gate_causal_ref"]["reason_code"] == (
        "gate:g2d_child_output"
    )
    assert ignored_proof["blocked_gate_causal_ref"]["source_artifact_id"] == (
        ignored_proof["blocked_gate_source_artifact_id"]
    )
    assert ignored_proof["blocked_gate_causal_ref"]["downstream_artifact_id"] == (
        ignored_proof["blocked_gate_downstream_artifact_id"]
    )
    assert ignored_proof["blocked_gate_causal_ref"]["consumer_component"] == (
        "fractal_scheduler_v02"
    )
    assert ignored_proof["blocked_gate_causal_ref"]["trace_refs"][:2] == [
        ignored_proof["blocked_gate_source_artifact_id"],
        ignored_proof["blocked_gate_downstream_artifact_id"],
    ]
    assert ignored_proof["blocked_gate_causal_validation_reasons"] == []
    assert ignored_proof["blocked_gate_artifact_validation_reasons"] == []
    assert ignored_proof["blocked_gate_bundle_validation_reasons"] == []
    assert ignored_proof["blocked_gate_counterfactual_validation_reasons"] == []
    assert ignored_proof["blocked_gate_generic_diagnostic_scope"] == (
        "SUPPLEMENTAL_NON_EXECUTABLE_STABLE_ID"
    )
    assert ignored_proof["blocked_gate_row_in_accepted_runtime"] is False
    assert used_proof["accepted_bundle_ref"] == ignored_proof["accepted_bundle_ref"]
    assert d5_fractal_runtime_report_v02.counterfactual_case_count == 2


def test_d5_zero_operation_and_non_authority_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
) -> None:
    report = d5_fractal_runtime_report_v02
    zero_fields = (
        "provider_calls", "model_calls", "gemini_calls", "network_calls",
        "connector_calls", "external_drs_calls", "action_commit_packets_created",
        "permissions_created", "receipts_created", "final_outputs_created",
        "drs_writes", "authority_created_count", "real_world_effects_count",
    )
    assert all(getattr(report, name) == 0 for name in zero_fields)
    assert all(
        all(getattr(item, name) == 0 for name in zero_fields)
        for item in report.case_results
    )
    assert report.accepted_bundle_count == report.topology_created_count == 10
    assert sum(item.topology_created_count for item in report.case_results) == 10
    source = Path(d5_runner.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = tuple(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    ) + tuple(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert not any(name == "tests" or name.startswith("tests.") for name in imports)
    assert "_d4_run_runtime_v02" not in source
    assert "ActionCommitPacket(" not in source
    assert "FinalOutput(" not in source
    assert "requests." not in source
    assert "subprocess" not in imports
    assert len(d5_runner._SOURCE_NEGATIVE_AXIS_ROWS_V02) == 17
    assert len(d5_runner._BOUNDED_NEGATIVE_AXIS_ROWS_V02) == 14
    assert len(d5_runner._PROOF_CONTRACTS_V02) == 72


def test_d5_runner_main_and_json_projection_contract_v02(
    d5_fractal_runtime_report_v02: d5_runner.FractalRuntimeG2DReportV02,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = d5_fractal_runtime_report_v02
    monkeypatch.setattr(d5_runner, "collect_fractal_runtime_g2_d_v02", lambda: report)
    assert d5_runner.main() == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == d5_runner.render_fractal_runtime_g2_d_v02(report)
    assert json.loads(captured.out)["report_id"] == report.report_id

    rows = report.case_results
    extra = replace(rows[-1], case_id="g2d_case:extra:v02")
    mutations = (
        replace(report, case_results=rows[:-1]),
        replace(report, case_results=(rows[1], rows[0], *rows[2:])),
        replace(report, case_results=(rows[0], rows[0], *rows[2:])),
        replace(report, case_results=(replace(rows[0], case_id=rows[1].case_id), *rows[1:])),
        replace(report, case_results=(replace(rows[0], evidence_sha256="0" * 64), *rows[1:])),
        replace(report, report_id=d5_runner.REPORT_ID_PREFIX + "0" * 64),
        replace(report, provider_calls=1),
        replace(report, case_results=(replace(rows[0], case_class="NEGATIVE"), *rows[1:])),
        replace(report, case_results=(replace(rows[0], observed_outcome="FAIL_CLOSED"), *rows[1:])),
        replace(report, case_results=(*rows, extra), case_order=(*report.case_order, extra.case_id)),
        replace(report, domain_order=tuple(reversed(report.domain_order))),
    )
    assert all(d5_runner.validate_fractal_runtime_g2_d_report_v02(item) for item in mutations)

    coherent = (
        _d5_coherently_tampered_report_v02(
            report,
            case_number=28,
            mutate=lambda details: details["accepted_depth_rows"][2].__setitem__(
                "status", "FAIL_CLOSED"
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=30,
            mutate=lambda details: details["accepted_cell_rows"][-1].__setitem__(
                "global_create_consumed_cell_count", 20
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=39,
            mutate=lambda details: details.__setitem__(
                "safe_sibling_after_sha256", "0" * 64
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=35,
            mutate=lambda details: details["mutation_rows"][0].__setitem__(
                0, "scope_axis_renamed"
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=47,
            mutate=lambda details: details["blocked_gate_causal_ref"].__setitem__(
                "disposition", "REJECTED"
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=58,
            mutate=lambda details: details.__setitem__(
                "exhausted_remaining_cell_count", 1
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=60,
            mutate=lambda details: details["full_fractal_leaf_edges"][0].__setitem__(
                0, 6
            ),
        ),
        _d5_coherently_tampered_report_v02(
            report,
            case_number=72,
            mutate=lambda details: details.__setitem__(
                "stage_d_c_artifact_count", details["stage_d_b_artifact_count"]
            ),
        ),
    )
    assert all(
        item.report_id == d5_runner._report_identity_v02(replace(item, report_id=""))
        for item in coherent
    )
    assert all(
        d5_runner.validate_fractal_runtime_g2_d_report_v02(item)
        == ("g2d5_report_invalid",)
        for item in coherent
    )
