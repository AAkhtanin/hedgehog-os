from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import types
from typing import get_args, get_origin, get_type_hints

from jsonschema import Draft202012Validator, ValidationError
import pytest

import hedgehog.action_commit_packet_v02 as action_commit_packet
import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as drs_compatibility
import hedgehog.drs_memory_resolution_v01 as drs_resolution
import hedgehog.drs_semantic_address_v01 as drs_semantic
import hedgehog.reuse_certificate_v01 as reuse_certificate
import hedgehog.structured_rationale as structured_rationale
import hedgehog.kernel as kernel
import hedgehog.kernel.continuous_delta_runtime_v01 as g2e
import hedgehog.kernel.execution_mode_router_v01 as g2c
import hedgehog.kernel.fractal_runtime_v02 as g2d
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)
from hedgehog.kernel.abi_v01 import (
    build_kernel_artifact_v01,
    causal_consumption_ref_to_plain_dict_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_causal_consumption_ref_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    ArtifactDependencyEdgeV01,
    AuthorityClassBindingV01,
    EvidenceClassBindingV01,
    RootOwnershipBindingV01,
    build_artifact_manifest_v01,
    build_default_seal_profile_v01,
    canonical_json_bytes_v01,
    verify_artifact_replay_v01,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/continuous_delta_runtime_v01.py"
SCHEMA_PATH = ROOT / "schemas/continuous_delta_runtime_v01.schema.json"
PREFLIGHT_PATH = ROOT / "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md"
ADDENDUM_PATH = ROOT / (
    "docs/continuous_delta_runtime_v0_1_g2_e_"
    "post_acceptance_contract_addendum_v01.md"
)
ACCEPTED_ADDENDUM_SHA256 = (
    "2b982ecaed9dc5cea2373676d816840ca683c8190b69516c14688cbba9e452f8"
)
ACCEPTED_V012_ADDENDUM_SHA256 = (
    "1041dbf3da320557d5eca948a13d0c4737e4e9b9ffac64c9453c97503527ca4c"
)
ACCEPTED_V013_DONOR_SHA256 = (
    "17b9384db812d5078301a9b3d4335dd3351481e117929b6b04c1ff6a137f4a56"
)
E4_PUBLIC_FUNCTIONS = (
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

TYPE_NAMES = (
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
)

QUARTET_FUNCTIONS = (
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

E2_QUARTET_FUNCTIONS = (
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
)

E2_BEHAVIORAL_FUNCTIONS = (
    "build_dependency_fingerprint_v01",
    "validate_dependency_fingerprint_against_sources_v01",
    "project_integrity_replay_dependency_edges_v01",
    "compute_affected_set_v01",
    "validate_affected_set_against_graph_v01",
)
E2_PUBLIC_FUNCTIONS = E2_QUARTET_FUNCTIONS + E2_BEHAVIORAL_FUNCTIONS

E3_QUARTET_FUNCTIONS = (
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
)
E3_BEHAVIORAL_FUNCTIONS = (
    "build_continuous_delta_source_context_v01",
    "validate_continuous_delta_source_context_v01",
    "derive_invalidation_report_v01",
    "validate_invalidation_report_against_sources_v01",
    "prove_unaffected_artifact_preservation_v01",
)
E3_PUBLIC_FUNCTIONS = E3_QUARTET_FUNCTIONS + E3_BEHAVIORAL_FUNCTIONS


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _source_binding() -> g2e.DeltaSourceBindingV01:
    return g2e.build_delta_source_binding_v01(
        request_id="request:g2e:001",
        transaction_id="transaction:g2e:001",
        owning_root_id="root:g2e:001",
        domain_id="TRAVEL_POLICY_INFORMATION",
        baseline_source_artifact_id="artifact:baseline:001",
        baseline_source_artifact_type="SemanticEvidence",
        baseline_source_artifact_sha256=_sha("baseline-artifact"),
        baseline_source_payload_sha256=_sha("baseline-payload"),
        observed_source_artifact_id="artifact:observed:001",
        observed_source_artifact_type="SemanticEvidence",
        observed_source_artifact_sha256=_sha("observed-artifact"),
        observed_source_payload_sha256=_sha("observed-payload"),
        baseline_report_id="frreport_v02:baseline",
        baseline_graph_id="g2e_dependency_graph_index_v01:" + _sha("graph"),
        baseline_graph_version="v0.1",
        baseline_policy_version="policy:v1",
        observed_policy_version="policy:v2",
        baseline_schema_versions=("v1",),
        observed_schema_versions=("v1",),
        baseline_source_history_hash=_sha("history-before"),
        observed_source_history_hash=_sha("history-after"),
        valid_from_utc="2026-08-11T00:00:00+00:00",
        valid_to_utc="2026-08-12T00:00:00+00:00",
        trace_refs=("trace:g2e:source",),
    )


def _changed_field(
    source: g2e.DeltaSourceBindingV01 | None = None,
) -> g2e.ChangedFieldBindingV01:
    source = source or _source_binding()
    return g2e.build_changed_field_binding_v01(
        source_binding_id=source.source_binding_id,
        json_pointer="/payload/hold_status",
        prior_value_sha256=_sha("old-field-value"),
        observed_value_sha256=_sha("new-field-value"),
        change_class="FIELD_VALUE_CHANGE",
        observed_at_utc="2026-08-11T01:00:00+00:00",
        trace_refs=("trace:g2e:field",),
    )


def _changed_artifact(
    source: g2e.DeltaSourceBindingV01 | None = None,
) -> g2e.ChangedArtifactBindingV01:
    source = source or _source_binding()
    return g2e.build_changed_artifact_binding_v01(
        source_binding_id=source.source_binding_id,
        baseline_artifact_id="artifact:baseline:001",
        baseline_artifact_type="SemanticEvidence",
        baseline_payload_sha256=_sha("baseline-payload"),
        observed_artifact_id="artifact:observed:001",
        observed_artifact_type="SemanticEvidence",
        observed_payload_sha256=_sha("observed-payload"),
        baseline_dependency_fingerprint=_sha("dependency-before"),
        observed_dependency_fingerprint=_sha("dependency-after"),
        change_class="ARTIFACT_SUCCESSOR",
        observed_at_utc="2026-08-11T01:00:00+00:00",
        trace_refs=("trace:g2e:artifact",),
    )


def _delta(
    source: g2e.DeltaSourceBindingV01 | None = None,
    changed_field: g2e.ChangedFieldBindingV01 | None = None,
    changed_artifact: g2e.ChangedArtifactBindingV01 | None = None,
) -> g2e.WorldStateDeltaV01:
    source = source or _source_binding()
    changed_field = changed_field or _changed_field(source)
    changed_artifact = changed_artifact or _changed_artifact(source)
    return g2e.build_world_state_delta_v01(
        ordered_source_binding_ids=(source.source_binding_id,),
        request_id=source.request_id,
        transaction_id=source.transaction_id,
        owning_root_id=source.owning_root_id,
        domain_id=source.domain_id,
        baseline_report_id=source.baseline_report_id,
        baseline_graph_id=source.baseline_graph_id,
        baseline_graph_version=source.baseline_graph_version,
        observed_at_utc="2026-08-11T01:00:00+00:00",
        valid_from_utc=source.valid_from_utc,
        valid_to_utc=source.valid_to_utc,
        baseline_policy_version=source.baseline_policy_version,
        observed_policy_version=source.observed_policy_version,
        baseline_schema_versions=source.baseline_schema_versions,
        observed_schema_versions=source.observed_schema_versions,
        baseline_source_history_hash=source.baseline_source_history_hash,
        observed_source_history_hash=source.observed_source_history_hash,
        ordered_changed_field_binding_ids=(
            changed_field.changed_field_binding_id,
        ),
        ordered_changed_artifact_binding_ids=(
            changed_artifact.changed_artifact_binding_id,
        ),
        dependency_fingerprint_before=_sha("dependency-before"),
        dependency_fingerprint_after=_sha("dependency-after"),
        trace_refs=("trace:g2e:delta",),
    )


def _validation_report() -> g2e.ContinuousDeltaValidationReportV01:
    return g2e.build_continuous_delta_validation_report_v01(
        validation_target="WorldStateDeltaV01",
        validated_object_id=_delta().delta_id,
        failure_stage="delta_source_structure",
        reason_codes=(),
        source_reason_codes=(),
        return_to_root_required=False,
        root_review_required=False,
    )


def _six_instances() -> tuple[object, ...]:
    source = _source_binding()
    field = _changed_field(source)
    artifact = _changed_artifact(source)
    return (
        source,
        field,
        artifact,
        _delta(source, field, artifact),
        g2e.build_dependency_fingerprint_profile_v01(),
        _validation_report(),
    )


def _preflight_type_rows() -> tuple[tuple[str, tuple[str, ...]], ...]:
    text = PREFLIGHT_PATH.read_text(encoding="utf-8")
    section = text.split("Canonical type table:\n", 1)[1].split(
        "\nRuntime carrier types are exact:", 1
    )[0]
    rows = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0] in TYPE_NAMES:
            rows.append((cells[0], tuple(item.strip() for item in cells[3].split(","))))
    return tuple(rows)


def _preflight_identity_rows() -> tuple[tuple[str, str, str, bytes], ...]:
    text = PREFLIGHT_PATH.read_text(encoding="utf-8")
    section = text.split("All concrete stems, prefixes, and domains are unique:\n", 1)[1]
    section = section.split("\nNo prefix/domain is caller-selected", 1)[0]
    rows = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] not in TYPE_NAMES[:18]:
            continue
        rows.append(
            (
                cells[0],
                cells[1],
                cells[2],
                (
                    "HEDGEHOG_CONTINUOUS_DELTA_RUNTIME_V01\x00"
                    + cells[0]
                    + "\x00"
                ).encode("utf-8"),
            )
        )
    return tuple(rows)


def _schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _alternate(value: object) -> object:
    if value is None:
        return "prior:g2e:001"
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is tuple:
        return value + ("alternate:g2e",)
    if type(value) is str:
        if len(value) == 64 and all(char in "0123456789abcdef" for char in value):
            return _sha("alternate-digest")
        if value.startswith("2026-"):
            return "2026-08-13T00:00:00+00:00"
        return value + ":alternate"
    raise AssertionError(type(value))


def _e2_time_envelope() -> dict[str, object]:
    return {
        "ct_session_anchor": "session:g2e:e2",
        "et_observed_at": "2026-08-11T01:00:00+00:00",
        "freshness_class": "normal",
        "kt_asof": "2026-08-11T01:00:00+00:00",
        "pt_created_at": "2026-08-11T01:00:00+00:00",
        "ttl_seconds": 3600,
        "valid_from": "2026-08-11T00:00:00+00:00",
        "valid_to": "2026-08-12T00:00:00+00:00",
    }


def _e2_kernel_artifact(
    artifact_id: str,
    payload: dict[str, object],
    *,
    artifact_type: str = "SemanticEvidence",
    schema_version: str = "v1",
    lifecycle_state: str = "VALIDATED",
    authority_class: str = "EVIDENCE_ONLY",
    source_component: str = "g2e_e2_test_fixture",
    trace_refs: tuple[str, ...] | None = None,
    parent_refs: tuple[str, ...] = (),
) -> g2e.KernelArtifactV01:
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        schema_version=schema_version,
        transaction_id="transaction:g2e:e2",
        owner_root_id="root:g2e:e2",
        source_component=source_component,
        authority_class=authority_class,
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=trace_refs or ("trace:" + artifact_id,),
        parent_refs=parent_refs,
        time_envelope=_e2_time_envelope(),
    )


def _e2_artifact_sha(artifact: g2e.KernelArtifactV01) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(artifact))
    ).hexdigest()


def _e2_payload_sha(artifact: g2e.KernelArtifactV01) -> str:
    plain = kernel_artifact_to_plain_dict_v01(artifact)
    return hashlib.sha256(canonical_json_bytes_v01(plain["payload"])).hexdigest()


def _e2_fixture(
    *,
    source_pointer: tuple[str, ...] = ("/hold_status",),
    source_edge_class: str = "FIELD_CAUSAL",
) -> dict[str, object]:
    baseline = (
        _e2_kernel_artifact(
            "artifact:e2:source:baseline",
            {"hold_status": "OLD", "label": "changed-source"},
        ),
        _e2_kernel_artifact("artifact:e2:direct", {"label": "direct"}),
        _e2_kernel_artifact("artifact:e2:transitive", {"label": "transitive"}),
        _e2_kernel_artifact("artifact:e2:unrelated", {"label": "unrelated"}),
        _e2_kernel_artifact("artifact:e2:sibling", {"label": "sibling"}),
    )
    observed_source = _e2_kernel_artifact(
        "artifact:e2:source:observed",
        {"hold_status": "NEW", "label": "changed-source"},
    )
    observed = (observed_source, *baseline[1:])
    profile = build_default_seal_profile_v01()
    refs = tuple(kernel_artifact_to_canonical_ref_v01(item) for item in baseline)
    replay_edges = (
        ArtifactDependencyEdgeV01(
            artifact_id=baseline[1].artifact_id,
            depends_on_artifact_id=baseline[0].artifact_id,
        ),
        ArtifactDependencyEdgeV01(
            artifact_id=baseline[2].artifact_id,
            depends_on_artifact_id=baseline[1].artifact_id,
        ),
        ArtifactDependencyEdgeV01(
            artifact_id=baseline[4].artifact_id,
            depends_on_artifact_id=baseline[0].artifact_id,
        ),
    )
    manifest = build_artifact_manifest_v01(
        transaction_id="transaction:g2e:e2",
        profile=profile,
        artifacts=refs,
        dependency_edges=replay_edges,
        root_ownership_bindings=tuple(
            RootOwnershipBindingV01(item.artifact_id, "root:g2e:e2")
            for item in baseline
        ),
        evidence_class_bindings=tuple(
            EvidenceClassBindingV01(item.artifact_id, "TEST_EVIDENCE")
            for item in baseline
        ),
        authority_class_bindings=tuple(
            AuthorityClassBindingV01(item.artifact_id, item.authority_class)
            for item in baseline
        ),
    )
    payload_rows = tuple(
        (
            item.artifact_id,
            kernel_artifact_to_plain_dict_v01(item)["payload"],
        )
        for item in baseline
    )
    replay = verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    edge_projection_bindings = (
        (
            baseline[4].artifact_id,
            baseline[0].artifact_id,
            (),
            "ARTIFACT_DEPENDENCY",
        ),
        (
            baseline[2].artifact_id,
            baseline[1].artifact_id,
            (),
            "ARTIFACT_DEPENDENCY",
        ),
        (
            baseline[1].artifact_id,
            baseline[0].artifact_id,
            source_pointer,
            source_edge_class,
        ),
    )
    graph_basis, dependency_edges = (
        g2e.project_integrity_replay_dependency_edges_v01(
            manifest=manifest,
            replay=replay,
            source_artifacts=baseline,
            graph_version="v0.1",
            transaction_id="transaction:g2e:e2",
            owning_root_id="root:g2e:e2",
            domain_id="TRAVEL_POLICY_INFORMATION",
            policy_version="policy:v1",
            schema_versions=("v1",),
            source_history_hash=_sha("e2-history-before"),
            edge_projection_bindings=edge_projection_bindings,
        )
    )
    graph = g2e.build_dependency_graph_index_v01(
        graph_basis_sha256=graph_basis,
        graph_version="v0.1",
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline,
        dependency_edges=dependency_edges,
        transaction_id="transaction:g2e:e2",
        owning_root_id="root:g2e:e2",
        domain_id="TRAVEL_POLICY_INFORMATION",
        policy_version="policy:v1",
        schema_versions=("v1",),
        source_history_hash=_sha("e2-history-before"),
        trace_refs=("trace:g2e:e2:graph",),
    )
    fingerprint_profile = g2e.build_dependency_fingerprint_profile_v01()
    before = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=baseline,
        policy_version="policy:v1",
        schema_versions=("v1",),
        source_history_hash=_sha("e2-history-before"),
    )
    after = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=observed,
        policy_version="policy:v2",
        schema_versions=("v1",),
        source_history_hash=_sha("e2-history-after"),
    )
    source_binding = g2e.build_delta_source_binding_v01(
        request_id="request:g2e:e2",
        transaction_id="transaction:g2e:e2",
        owning_root_id="root:g2e:e2",
        domain_id="TRAVEL_POLICY_INFORMATION",
        baseline_source_artifact_id=baseline[0].artifact_id,
        baseline_source_artifact_type=baseline[0].artifact_type,
        baseline_source_artifact_sha256=_e2_artifact_sha(baseline[0]),
        baseline_source_payload_sha256=_e2_payload_sha(baseline[0]),
        observed_source_artifact_id=observed[0].artifact_id,
        observed_source_artifact_type=observed[0].artifact_type,
        observed_source_artifact_sha256=_e2_artifact_sha(observed[0]),
        observed_source_payload_sha256=_e2_payload_sha(observed[0]),
        baseline_report_id="frreport_v02:e2:baseline",
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        baseline_policy_version="policy:v1",
        observed_policy_version="policy:v2",
        baseline_schema_versions=("v1",),
        observed_schema_versions=("v1",),
        baseline_source_history_hash=_sha("e2-history-before"),
        observed_source_history_hash=_sha("e2-history-after"),
        valid_from_utc="2026-08-11T00:00:00+00:00",
        valid_to_utc="2026-08-12T00:00:00+00:00",
        trace_refs=("trace:g2e:e2:source-binding",),
    )
    changed_field = g2e.build_changed_field_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        json_pointer="/payload/hold_status",
        prior_value_sha256=hashlib.sha256(
            canonical_json_bytes_v01("OLD")
        ).hexdigest(),
        observed_value_sha256=hashlib.sha256(
            canonical_json_bytes_v01("NEW")
        ).hexdigest(),
        change_class="FIELD_VALUE_CHANGE",
        observed_at_utc="2026-08-11T01:00:00+00:00",
        trace_refs=("trace:g2e:e2:field",),
    )
    changed_artifact = g2e.build_changed_artifact_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        baseline_artifact_id=baseline[0].artifact_id,
        baseline_artifact_type=baseline[0].artifact_type,
        baseline_payload_sha256=_e2_payload_sha(baseline[0]),
        observed_artifact_id=observed[0].artifact_id,
        observed_artifact_type=observed[0].artifact_type,
        observed_payload_sha256=_e2_payload_sha(observed[0]),
        baseline_dependency_fingerprint=before,
        observed_dependency_fingerprint=after,
        change_class="ARTIFACT_SUCCESSOR",
        observed_at_utc="2026-08-11T01:00:00+00:00",
        trace_refs=("trace:g2e:e2:artifact",),
    )
    delta = g2e.build_world_state_delta_v01(
        ordered_source_binding_ids=(source_binding.source_binding_id,),
        request_id=source_binding.request_id,
        transaction_id=source_binding.transaction_id,
        owning_root_id=source_binding.owning_root_id,
        domain_id=source_binding.domain_id,
        baseline_report_id=source_binding.baseline_report_id,
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        observed_at_utc="2026-08-11T01:00:00+00:00",
        valid_from_utc=source_binding.valid_from_utc,
        valid_to_utc=source_binding.valid_to_utc,
        baseline_policy_version="policy:v1",
        observed_policy_version="policy:v2",
        baseline_schema_versions=("v1",),
        observed_schema_versions=("v1",),
        baseline_source_history_hash=_sha("e2-history-before"),
        observed_source_history_hash=_sha("e2-history-after"),
        ordered_changed_field_binding_ids=(
            changed_field.changed_field_binding_id,
        ),
        ordered_changed_artifact_binding_ids=(
            changed_artifact.changed_artifact_binding_id,
        ),
        dependency_fingerprint_before=before,
        dependency_fingerprint_after=after,
        trace_refs=("trace:g2e:e2:delta",),
    )
    request = g2e.build_affected_set_request_v01(
        delta=delta,
        graph=graph,
        trace_refs=("trace:g2e:e2:request",),
    )
    result = g2e.compute_affected_set_v01(
        request=request,
        delta=delta,
        graph=graph,
        source_bindings=(source_binding,),
        changed_field_bindings=(changed_field,),
        changed_artifact_bindings=(changed_artifact,),
        dependency_edges=dependency_edges,
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
    )
    return {
        "baseline": baseline,
        "observed": observed,
        "manifest": manifest,
        "replay": replay,
        "edge_projection_bindings": edge_projection_bindings,
        "graph_basis": graph_basis,
        "dependency_edges": dependency_edges,
        "graph": graph,
        "fingerprint_profile": fingerprint_profile,
        "before": before,
        "after": after,
        "source_binding": source_binding,
        "changed_field": changed_field,
        "changed_artifact": changed_artifact,
        "delta": delta,
        "request": request,
        "result": result,
    }


def _e2_context_kwargs(fixture: dict[str, object]) -> dict[str, object]:
    return {
        "request": fixture["request"],
        "delta": fixture["delta"],
        "graph": fixture["graph"],
        "source_bindings": (fixture["source_binding"],),
        "changed_field_bindings": (fixture["changed_field"],),
        "changed_artifact_bindings": (fixture["changed_artifact"],),
        "dependency_edges": fixture["dependency_edges"],
        "baseline_source_artifacts": fixture["baseline"],
        "observed_source_artifacts": fixture["observed"],
    }


def _e2_reseal(value: object, **changes: object) -> object:
    profiles = {
        g2e.DeltaSourceBindingV01: (
            "source_binding_id",
            g2e.rebuild_delta_source_binding_identity_v01,
        ),
        g2e.ChangedFieldBindingV01: (
            "changed_field_binding_id",
            g2e.rebuild_changed_field_binding_identity_v01,
        ),
        g2e.ChangedArtifactBindingV01: (
            "changed_artifact_binding_id",
            g2e.rebuild_changed_artifact_binding_identity_v01,
        ),
        g2e.WorldStateDeltaV01: (
            "delta_id",
            g2e.rebuild_world_state_delta_identity_v01,
        ),
        g2e.AffectedSetRequestV01: (
            "affected_request_id",
            g2e.rebuild_affected_set_request_identity_v01,
        ),
    }
    identity_field, rebuilder = profiles[type(value)]
    candidate = replace(value, **changes)
    return replace(candidate, **{identity_field: rebuilder(candidate)})


def _e2_rewired_context(
    fixture: dict[str, object],
    *,
    source_bindings: tuple[g2e.DeltaSourceBindingV01, ...] | None = None,
    changed_field_bindings: tuple[g2e.ChangedFieldBindingV01, ...] | None = None,
    changed_artifact_bindings: tuple[g2e.ChangedArtifactBindingV01, ...]
    | None = None,
    delta_changes: dict[str, object] | None = None,
) -> dict[str, object]:
    sources = source_bindings or (fixture["source_binding"],)
    changed_fields = changed_field_bindings or (fixture["changed_field"],)
    changed_artifacts = changed_artifact_bindings or (
        fixture["changed_artifact"],
    )
    delta_updates = {
        "ordered_source_binding_ids": tuple(
            item.source_binding_id for item in sources
        ),
        "ordered_changed_field_binding_ids": tuple(
            item.changed_field_binding_id for item in changed_fields
        ),
        "ordered_changed_artifact_binding_ids": tuple(
            item.changed_artifact_binding_id for item in changed_artifacts
        ),
        **(delta_changes or {}),
    }
    delta = _e2_reseal(fixture["delta"], **delta_updates)
    assert type(delta) is g2e.WorldStateDeltaV01
    request = _e2_reseal(
        fixture["request"],
        delta_id=delta.delta_id,
        ordered_changed_field_binding_ids=delta.ordered_changed_field_binding_ids,
        ordered_changed_artifact_binding_ids=(
            delta.ordered_changed_artifact_binding_ids
        ),
    )
    return {
        **_e2_context_kwargs(fixture),
        "request": request,
        "delta": delta,
        "source_bindings": sources,
        "changed_field_bindings": changed_fields,
        "changed_artifact_bindings": changed_artifacts,
    }


def _e2_artifact_chain(
    fixture: dict[str, object],
) -> tuple[object, ...]:
    delta = fixture["delta"]
    graph = fixture["graph"]
    result = fixture["result"]
    baseline = fixture["baseline"]
    observed = fixture["observed"]
    assert type(delta) is g2e.WorldStateDeltaV01
    assert type(graph) is g2e.DependencyGraphIndexV01
    assert type(result) is g2e.AffectedSetResultV01
    assert type(baseline) is tuple and type(observed) is tuple
    route = _e2_kernel_artifact(
        "artifact:e2:route",
        {"accepted_mode": "BOUNDED"},
        artifact_type="ExecutionModeRouteEligibility",
        schema_version="v0.1",
        lifecycle_state="ROOT_ACCEPTED",
        authority_class="ROOT_AUTHORIZED",
        source_component="execution_mode_router_v01",
    )
    g2d_report = _e2_kernel_artifact(
        "artifact:e2:g2d-report",
        {"report_status": "PASS"},
        artifact_type="FractalRuntimeReport",
        schema_version="v0.1",
        lifecycle_state="VALIDATED",
        authority_class="EVIDENCE_ONLY",
        source_component="fractal_runtime_v02",
    )
    proposed = g2e._project_delta_source_proposed_artifact_v01(
        delta=delta,
        baseline_route_artifact=route,
        baseline_g2d_report_artifact=g2d_report,
        baseline_source_artifacts=(baseline[0],),
        observed_source_artifacts=(observed[0],),
    )
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    t01_rule = registry.rules[0]
    t01 = transition.lookup_transition_v01(
        registry=registry,
        abi_major_version=t01_rule.abi_major_version,
        source_artifact_type=t01_rule.source_artifact_type,
        source_lifecycle_state=t01_rule.source_lifecycle_state,
        actor_role=t01_rule.actor_role,
        attempted_effect=t01_rule.attempted_effect,
        target_artifact_type=t01_rule.target_artifact_type,
        satisfied_guards=t01_rule.required_guards,
        root_commit_present=False,
    )
    validated = g2e._project_delta_source_validated_artifact_v01(
        delta=delta,
        proposed_source_artifact=proposed,
        t01_decision_id=t01.decision_id,
        baseline_route_artifact=route,
        baseline_g2d_report_artifact=g2d_report,
        baseline_source_artifacts=(baseline[0],),
        observed_source_artifacts=(observed[0],),
    )
    graph_artifact = g2e._project_dependency_graph_artifact_v01(
        graph=graph,
        delta=delta,
        validated_delta_source_artifact=validated,
        baseline_route_artifact=route,
        baseline_source_artifacts=baseline,
    )
    t02_rule = registry.rules[1]
    t02 = transition.lookup_transition_v01(
        registry=registry,
        abi_major_version=t02_rule.abi_major_version,
        source_artifact_type=t02_rule.source_artifact_type,
        source_lifecycle_state=t02_rule.source_lifecycle_state,
        actor_role=t02_rule.actor_role,
        attempted_effect=t02_rule.attempted_effect,
        target_artifact_type=t02_rule.target_artifact_type,
        satisfied_guards=t02_rule.required_guards,
        root_commit_present=False,
    )
    affected_artifact = g2e._project_affected_set_artifact_v01(
        affected_result=result,
        delta=delta,
        validated_delta_source_artifact=validated,
        dependency_graph_artifact=graph_artifact,
        baseline_route_artifact=route,
        t02_decision_id=t02.decision_id,
    )
    assert transition.validate_continuous_delta_transition_decision_v01(
        t01,
        registry=registry,
        source_artifact=proposed,
        target_artifact=validated,
    ) == ()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t02,
        registry=registry,
        source_artifact=validated,
        target_artifact=affected_artifact,
    ) == ()
    return (
        proposed,
        validated,
        graph_artifact,
        affected_artifact,
        t01,
        t02,
        route,
        g2d_report,
    )


_E3_TIME = 1783470600
_E3_VALID_FROM = 1783468800
_E3_VALID_TO = 1783472400
_E3_UTC = "2026-07-08T00:30:00+00:00"
_E3_VALID_FROM_UTC = "2026-07-08T00:00:00+00:00"
_E3_VALID_TO_UTC = "2026-07-08T01:00:00+00:00"
_E3_ROOT = "root:g2e:e3"
_E3_DOMAIN = "G2E3_CONTINUOUS_DELTA"
_E3_BASELINE_OBSERVATION_DOMAIN = "HEDGEHOG_G2E3_BASELINE_OBSERVATION_V01"
_E3_EXPECTED_DIGEST_ENV = (
    "HEDGEHOG_G2E3_EXPECTED_BASELINE_SOURCE_OBSERVATION_SHA256",
    "HEDGEHOG_G2E3_EXPECTED_BASELINE_MEMBER_OBSERVATION_SHA256",
    "HEDGEHOG_G2E3_EXPECTED_BASELINE_MEMBER_IDENTITIES_SHA256",
)


def _e3_g2a_dependency() -> action_commit_packet.DependencySetCandidateV01:
    content_sha256 = _sha("g2e-e3-g2a-dependency")
    provenance = ("source:g2e:e3:g2a-dependency",)
    envelope_id = action_commit_packet.build_action_dependency_time_envelope_id_v01(
        dependency_id="dependency:g2e:e3:invoice",
        evidence_ref="evidence:g2e:e3:invoice",
        content_sha256=content_sha256,
        freshness_policy_id="freshness:g2e:e3:v01",
        source_provenance_refs=provenance,
        valid_from_utc=_E3_VALID_FROM,
        valid_to_utc=_E3_VALID_TO,
    )
    record = action_commit_packet.build_dependency_set_candidate_record_v01(
        dependency_id="dependency:g2e:e3:invoice",
        dependency_class="INVOICE_EVIDENCE",
        evidence_ref="evidence:g2e:e3:invoice",
        content_sha256=content_sha256,
        requirement_class="MANDATORY",
        time_envelope_id=envelope_id,
        freshness_policy_id="freshness:g2e:e3:v01",
        source_provenance_refs=provenance,
        expected_accepting_local_root_id=_E3_ROOT,
    )
    return action_commit_packet.build_dependency_set_candidate_v01(
        dependency_records=(record,)
    )


def _e3_g2a_policy(
) -> action_commit_packet.ActionAuthorityPolicyProfileV01:
    return action_commit_packet.build_action_authority_policy_profile_v01(
        policy_version="policy:g2e:e3:g2a:v01",
        owning_local_root_id=_E3_ROOT,
        authority_rule_refs=("authority_rule:g2e:e3",),
        kill_switch_condition_refs=("kill_switch:g2e:e3",),
        retry_policy="NON_CONSUMING_RETRY",
        supersession_policy="ROOT_DECISION_ONLY",
        logical_effect_namespace="supplier.payment.v01",
        allowed_logical_effect_classes=("PAYMENT",),
        allowed_business_object_namespaces=("supplier.payment_slot.v01",),
        allowed_corridor_classes=("supplier_a_mock_payment_corridor",),
    )


def _e3_g2a_root_evidence(
    canonical: action_commit_packet.SupplierActionCommitPacketCanonicalProjectionV01,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    candidate_id = (
        canonical.authorization_candidate.root_packet_authorization_candidate_id
    )
    actor_id = "runtime:g2e:e3:g2a"
    request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic_request:g2e:e3:g2a",
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        runtime_topology_ref="runtime_topology:g2e:e3:g2a",
        bounded_context_refs=("context:g2e:e3:g2a",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=("action_commit_packet:g2e:e3",),
        required_evidence_classes=("DEPENDENCY_EVIDENCE",),
        forbidden_claims=("authority_creation",),
    )
    dependency_record = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence_binding:g2e:e3:g2a",
        evidence_ref=dependency_record.evidence_ref,
        evidence_class="DEPENDENCY_EVIDENCE",
        source_component_id=actor_id,
        provenance_ref=dependency_record.source_provenance_refs[0],
        evidence_state="PRESENT",
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id,
        subject="action_commit_packet:g2e:e3",
        predicate="root_packet_authorization_candidate",
        object_or_value={
            "candidate_id": candidate_id,
            "candidate_kind": "PACKET_AUTHORIZATION",
        },
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=("provenance:g2e:e3:g2a",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2e:e3:g2a",
        request_id=request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2e:e3:g2a",
        scope="scope:g2e:e3:g2a",
        bounded_context_refs=("context:g2e:e3:g2a",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:g2e:e3:g2a",),
        forbidden_claims_observed=(),
    )
    review_packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    mandatory_refs = tuple(
        record.evidence_ref
        for record in canonical.dependency_candidate.dependency_records
        if record.requirement_class == "MANDATORY"
    )
    root_kernel = root_decision.build_root_decision_kernel_v01()
    root_input = root_decision.build_root_decision_input_v01(
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        root_review_packet=review_packet,
        post_vv_bundle={
            "bundle_id": "post_vv:g2e:e3:g2a",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": list(mandatory_refs),
            "provided_evidence_refs": list(mandatory_refs),
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:g2e:e3:g2a",
            "candidate_ids": [candidate_id],
            "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 1_000_000},
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
            "policy_id": canonical.authority_policy_fingerprint,
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": True,
            "user_permission_present": True,
            "permission_scope_valid": True,
            "permission_ref": canonical.canonical_permission_ref,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": canonical.temporal_authority_fingerprint,
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(review_packet.conflict_set_ids),
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
    return root_kernel, root_input, root_result


def _e3_g2a_family(transaction_id: str) -> dict[str, object]:
    source = action_commit_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    dependency = _e3_g2a_dependency()
    canonical = action_commit_packet.build_supplier_action_commit_packet_canonical_projection_v01(
        source,
        transaction_id=transaction_id,
        owning_local_root_id=_E3_ROOT,
        canonical_permission_ref="permission:g2e:e3:g2a",
        selected_legacy_action=(
            action_commit_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER
        ),
        logical_effect_namespace="supplier.payment.v01",
        business_object_namespace="supplier.payment_slot.v01",
        corridor_class="supplier_a_mock_payment_corridor",
        adapter_version=action_commit_packet.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version="packet_ttl_v01",
        authority_policy=_e3_g2a_policy(),
        dependency_candidate=dependency,
        evaluation_time=_E3_TIME,
        evaluation_time_source="g2e_e3_trusted_ceiling",
        evaluation_context_id="evaluation_context:g2e:e3:g2a",
        predecessor_packet_id=None,
        supersession_reason_class=None,
    )
    root_kernel, root_input, root_result = _e3_g2a_root_evidence(canonical)
    root_projection = action_commit_packet.build_root_decision_candidate_projection_v01(
        candidate_kind=(
            action_commit_packet.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
        ),
        projected_candidate_id=(
            canonical.authorization_candidate.root_packet_authorization_candidate_id
        ),
        root_decision_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    packet = action_commit_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
        canonical_projection=canonical,
        root_decision_projection=root_projection,
    )
    transition_profile = (
        transition.build_action_packet_transition_registry_profile_v01()
    )
    registry = action_commit_packet.record_action_packet_genesis_v01(
        action_commit_packet.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=packet,
        action_packet_transition_registry_profile=transition_profile,
    )
    observations = tuple(
        action_commit_packet.build_action_dependency_current_observation_v01(
            dependency_id=record.dependency_id,
            evidence_ref=record.evidence_ref,
            observed_content_sha256=record.content_sha256,
            time_envelope_id=record.time_envelope_id,
            freshness_policy_id=record.freshness_policy_id,
            source_provenance_refs=record.source_provenance_refs,
            valid_from_utc=_E3_VALID_FROM,
            valid_to_utc=_E3_VALID_TO,
            observed_at_utc=_E3_TIME,
            observation_context_id="evaluation_context:g2e:e3:g2a",
        )
        for record in dependency.dependency_records
    )
    record = dependency.dependency_records[0]
    invalidation = action_commit_packet.build_action_invalidation_evidence_v01(
        source_invalidation_event_ref="event:g2e:e3:dependency-change",
        packet_id=packet.packet_identity.packet_id,
        dependency_id=record.dependency_id,
        invalidation_class="DEPENDENCY_CHANGED",
        evidence_ref=record.evidence_ref,
        evidence_sha256=_sha("g2e-e3-updated-dependency"),
        observed_status="CHANGED",
        time_envelope_id=record.time_envelope_id,
        freshness_policy_id=record.freshness_policy_id,
        owning_local_root_id=_E3_ROOT,
        accepted_by_local_root_id=_E3_ROOT,
        authority_effect="DETERMINISTIC_BLOCK",
        evaluation_time=_E3_TIME,
        evaluation_time_source="g2e_e3_trusted_ceiling",
        evaluation_context_id="evaluation_context:g2e:e3:g2a",
    )
    assert action_commit_packet.validate_action_invalidation_evidence_against_packet_v01(
        invalidation,
        packet,
    ) == (True, ())
    return {
        "registry": registry,
        "packet": packet,
        "dependency": dependency,
        "observations": observations,
        "invalidation": invalidation,
    }


def _e3_g2b_family() -> dict[str, object]:
    address = drs_semantic.build_semantic_address_v01(
        namespace="g2e3_v01",
        domain=_E3_DOMAIN,
        subject_class="bounded_information",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    scope_ref = "scope:g2e:e3"
    scope_sha256 = _sha(scope_ref)
    envelope = drs_semantic.build_drs_time_envelope_v01(
        pt_created_at=_E3_VALID_FROM,
        kt_as_of=_E3_TIME,
        et_observed_at=_E3_TIME,
        ct_context_anchor=_E3_TIME,
        ttl_seconds=3600,
        valid_from=_E3_VALID_FROM,
        valid_to=_E3_VALID_TO,
        source_observed_at=_E3_TIME,
        source_reported_at=_E3_TIME,
        system_ingested_at=_E3_TIME,
        system_verified_at=_E3_TIME,
        freshness_policy_id="freshness:g2e:e3:v01",
    )
    authority = drs_semantic.build_drs_authority_envelope_v01(
        authority_class="ROOT_ACCEPTED_WORK",
        owning_local_root_id=_E3_ROOT,
        source_root_decision_input_id="root-input:g2e:e3:g2b",
        source_root_decision_id="root-decision:g2e:e3:g2b",
        source_root_decision_hash=_sha("g2e-e3-g2b-root"),
        authority_scope_fingerprint=scope_sha256,
        root_acceptance_state="ACCEPTED_WORK",
        recording_component="continuous_delta_runtime_g2e3_test",
    )
    record = drs_semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Bounded deterministic G2-E3 baseline context.",
        semantic_tags=("bounded", "g2e3"),
        resonance_reason="Exact deterministic semantic-address match.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=("source:g2e:e3:g2b",),
        lineage_edges=(),
        time_envelope=envelope,
        authority_envelope=authority,
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT",
        policy_version="policy:g2e:e3:v01",
        schema_versions=("v0.1",),
        content_fingerprint=_sha("g2e-e3-meaning-record"),
        recording_component="continuous_delta_runtime_g2e3_test",
    )
    query = drs_resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_sha256,
        as_of=_E3_TIME,
        evaluation_time=_E3_TIME,
        evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        time_range_start=_E3_VALID_FROM,
        time_range_end=_E3_VALID_TO,
        required_time_axes=("PT", "KT", "ET", "CT", "TTL", "VALIDITY"),
        freshness_policy_id="freshness:g2e:e3:v01",
        max_age_seconds=3600,
        domain=_E3_DOMAIN,
        risk_class="LOW",
        reuse_intent="INFORMATIONAL_SHORTCUT_CONSIDERATION",
        requested_reuse_classes=("ANSWER_SHORTCUT",),
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
        policy_version="policy:g2e:e3:v01",
        schema_versions=("v0.1",),
        owning_local_root_id=_E3_ROOT,
    )
    evaluation = drs_resolution.evaluate_drs_candidate_v01(
        semantic_address=address,
        query=query,
        meaning_record=record,
        action_history_binding=None,
    )
    legacy = {
        "record_id": "legacy:g2e:e3:g2b",
        "layer": "work",
        "type": "generic",
        "domain": _E3_DOMAIN,
        "content": {"summary": "Bounded deterministic memory context."},
        "time_envelope": {
            "pt_created_at": "2026-07-08T00:00:00Z",
            "kt_asof": "2026-07-08T00:30:00Z",
            "et_observed_at": "2026-07-08T00:30:00Z",
            "ct_session_anchor": "case:g2e:e3:g2b",
            "ttl_seconds": 3600,
            "freshness_class": "static",
            "valid_from": "2026-07-08T00:00:00Z",
            "valid_to": "2026-07-08T01:00:00Z",
        },
        "provenance": {
            "request_id": "request:g2e:e3",
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
        "valid_from": _E3_VALID_FROM,
        "valid_to": _E3_VALID_TO,
        "issued_at": _E3_TIME,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": "policy:drs_answer_shortcut:v0.1",
    }
    actor_id = "actor:g2e:e3:g2b"
    work_request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic-work-request:g2e:e3:g2b",
        transaction_id=query.query_id,
        target_root_id=_E3_ROOT,
        runtime_topology_ref="g2e:e3:runtime_topology:not_created",
        bounded_context_refs=("context:g2e:e3:g2b",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence-binding:g2e:e3:g2b",
        evidence_ref="evidence:g2e:e3:g2b",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id=actor_id,
        provenance_ref="provenance:g2e:e3:g2b",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id,
        predicate="authorize_non_action_informational_answer_shortcut_v01",
        object_or_value=claim_preimage,
        time_envelope_ref="time-envelope:g2e:e3:g2b",
        provenance_refs=("provenance:g2e:e3:g2b",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2e:e3:g2b",
        request_id=work_request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2e:e3:g2b",
        scope=address.semantic_address_id,
        bounded_context_refs=("context:g2e:e3:g2b",),
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
        target_root_id=_E3_ROOT,
        root_review_packet=review_packet,
        post_vv_bundle={
            "bundle_id": "post-vv:g2e:e3:g2b",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate.resolution_candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:g2e:e3:g2b",
            "candidate_ids": [candidate.resolution_candidate_id],
            "selected_candidate_id": candidate.resolution_candidate_id,
            "score_micros_by_candidate": {
                candidate.resolution_candidate_id: 500000
            },
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
            "policy_id": "policy:g2e:e3:g2b",
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
            "time_envelope_ref": "time-envelope:g2e:e3:g2b",
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
    root_hash = g2e.domain_separated_sha256_hex_v01(
        domain="hedgehog:drs:root_shortcut_root_result_binding:v01",
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(root_result)
        ),
    )
    root_projection = reuse_certificate.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id=_E3_ROOT,
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
        valid_from=_E3_VALID_FROM,
        valid_to=_E3_VALID_TO,
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
        valid_from=_E3_VALID_FROM,
        valid_to=_E3_VALID_TO,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=_E3_TIME,
        evaluated_at=evaluation.evaluated_at,
    )
    report = drs_resolution.build_drs_resolution_report_v01(
        semantic_address=address,
        query=query,
        source_projections=(projection,),
        source_records=(record,),
        query_evaluations=(evaluation,),
        eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(
            item.resolution_candidate_id for item in ranked
        ),
        selected_candidate_id=candidate.resolution_candidate_id,
        retrieval_plan=plan,
        memory_descent_result=None,
        root_shortcut_projection=root_projection,
        reuse_certificate=certificate,
        context_only_record_ids=(),
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
    assert drs_resolution.validate_drs_resolution_report_v01(report) == (
        True,
        (),
    )
    assert reuse_certificate.validate_reuse_certificate_v01(certificate) == (
        True,
        (),
    )
    return {
        "transaction_id": query.query_id,
        "report": report,
        "certificate": certificate,
        "projections": (projection,),
        "root_kernel": root_kernel,
        "root_input": root_input,
        "root_result": root_result,
    }


def _e3_bsep(request_id: str) -> dict[str, dict[str, object]]:
    route_id = "route:g2e:e3:memory-informed"
    proposal_id = "proposal:g2e:e3:memory-informed"
    vector_ids = ("vector:g2e:e3:memory-informed",)
    guards = ("guard:g2e:e3:root-review",)
    business = context_packets.build_business_request_context_packet(
        packet_id="context_packet:g2e:e3:business",
        created_by="runtime:g2e:e3:test",
        domain=_E3_DOMAIN,
        request_id=request_id,
        business_subject="bounded_runtime_topology",
        requested_action="root_review",
        user_visible_summary="Bounded topology source review.",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": _E3_DOMAIN,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id="context_packet:g2e:e3:route",
        created_by="runtime:g2e:e3:test",
        source_refs=(business_ref,),
        domain=_E3_DOMAIN,
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
        "semantic_observations": ("A bounded route is present.",),
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
        packet_id="context_packet:g2e:e3:bsep",
        source_refs=(business_ref,),
        domain=_E3_DOMAIN,
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


def _e3_g2d_source_family(
    g2b: dict[str, object],
    *,
    selected_mode: str = "memory_informed",
) -> dict[str, object]:
    request_id = "request:g2e:e3"
    transaction_id = str(g2b["transaction_id"])
    bsep = _e3_bsep(request_id)
    profiles = []
    selected_index = g2c.EXECUTABLE_EXECUTION_MODES_V01.index(selected_mode)
    for index, candidate in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01):
        not_required = candidate in {"sealed_replay", "direct_informational_reuse"}
        profiles.append(
            g2c.build_execution_mode_local_mode_profile_v01(
                request_id=request_id,
                transaction_id=transaction_id,
                owning_root_id=_E3_ROOT,
                domain_id=_E3_DOMAIN,
                mode=candidate,
                policy_snapshot_id="policy:g2e:e3:route",
                capability_snapshot_id="capabilities:g2e:e3:route",
                cost_model_id="cost:g2e:e3:v01",
                policy_allowed=index >= selected_index,
                scope_allowed=True,
                risk_allowed=True,
                privacy_allowed=True,
                capability_state="NOT_REQUIRED" if not_required else "AVAILABLE",
                capability_id=None if not_required else f"capability:g2e:e3:{candidate}",
                cost_units=index + 1,
            )
        )
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        domain_id=_E3_DOMAIN,
        request_class="BOUNDED_REVIEW",
        action_class="NON_ACTION",
        action_packet_relation="NOT_APPLICABLE",
        scope_class="BOUNDED",
        scope_ref="scope:g2e:e3",
        permitted_narrower_scope_refs=(),
        risk_class="LOW",
        policy_snapshot_id="policy:g2e:e3:route",
        capability_snapshot_id="capabilities:g2e:e3:route",
        cost_model_id="cost:g2e:e3:v01",
        required_user_input_state="COMPLETE",
        hard_block_state="CLEAR",
        evaluation_time_epoch_seconds=_E3_TIME,
        pt_created_at_utc=_E3_UTC,
        et_observed_at_utc=_E3_UTC,
        ct_session_anchor="ct:g2e:e3",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc=_E3_VALID_FROM_UTC,
        valid_to_utc=_E3_VALID_TO_UTC,
        mode_profiles=tuple(profiles),
    )
    source = g2c.build_execution_mode_source_context_v01(
        business_request_context_packet=bsep["business"],
        bsep_packet=bsep["packet"],
        bsep_route_context_packet=bsep["route"],
        bsep_orchestrator_proposal=bsep["proposal"],
        bsep_structured_rationale=bsep["rationale"],
        sealed_replay_evidence=None,
        replay_source_manifest=None,
        replay_source_domain_projection=None,
        replay_source_safe_file_contents=(),
        replay_anchor_publication=None,
        replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,
        replay_reconstructed_manifest=None,
        replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),
        g2a_inspection=None,
        g2a_registry=None,
        g2a_packet_id=None,
        g2a_corridor=None,
        g2a_corridor_step=None,
        g2a_current_dependency_observations=(),
        g2a_logical_time_bridge=None,
        g2a_evaluation_time=_E3_TIME,
        g2a_evaluation_time_source=snapshot.created_by,
        g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2a_transition_registry_profile=None,
        g2b_resolution_report=g2b["report"],
        g2b_compatibility_projections=g2b["projections"],
        g2b_use_time=_E3_TIME,
        g2b_root_kernel=g2b["root_kernel"],
        g2b_root_decision_input=g2b["root_input"],
        g2b_root_decision_result=g2b["root_result"],
        g2b_writeback_evidence=None,
    )
    common = {
        "request_id": request_id,
        "transaction_id": transaction_id,
        "owning_root_id": _E3_ROOT,
        "domain_id": _E3_DOMAIN,
    }
    router_input = g2c.build_execution_mode_router_input_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(
            **common,
            source_context=source,
        ),
        local_routing_snapshot=snapshot,
        replay_binding=g2c.build_execution_mode_replay_not_applicable_binding_v01(
            **common
        ),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=_E3_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        ),
        g2b_binding=g2c.build_execution_mode_g2b_binding_v01(
            **common,
            source_context=source,
        ),
    )
    proposal, route_report = g2c.route_execution_mode_v01(
        router_input=router_input,
        source_context=source,
    )
    assert route_report.validation_status == "PASS" and proposal is not None
    assert proposal.selected_mode == selected_mode
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    )
    registry = transition.build_execution_mode_transition_registry_profile_v01()
    pre = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
    )
    review = g2c.build_root_execution_mode_review_input_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre,
        review_action="ACCEPT",
        accepted_scope_ref=proposal.proposed_scope_ref,
        narrowing_basis_refs=(),
    )
    decision, root_kernel, root_input, root_result, review_report = (
        g2c.review_execution_mode_proposal_v01(
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre,
        )
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
    assert route is not None
    policy = g2d.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
    )
    runtime_source = g2d.build_fractal_runtime_source_context_v02(
        transition_registry=registry,
        g2c_source_context=source,
        router_input=router_input,
        proposal=proposal,
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
        runtime_policy=policy,
    )
    assert g2d.validate_fractal_runtime_source_context_v02(runtime_source).status == "PASS"
    return {
        "source": runtime_source,
        "g2c_source": source,
        "route": route,
        "root_kernel": root_kernel,
        "route_report": route_report,
        "review_report": review_report,
    }


def _e3_time_envelope() -> dict[str, object]:
    return {
        "ct_session_anchor": "ct:g2e:e3",
        "et_observed_at": _E3_UTC,
        "freshness_class": "static",
        "kt_asof": _E3_UTC,
        "pt_created_at": _E3_UTC,
        "ttl_seconds": 3600,
        "valid_from": _E3_VALID_FROM_UTC,
        "valid_to": _E3_VALID_TO_UTC,
    }


def _e3_kernel_artifact(
    *,
    artifact_id: str,
    transaction_id: str,
    payload: dict[str, object],
    parent_refs: tuple[str, ...] = (),
    time_envelope: dict[str, object] | None = None,
) -> g2e.KernelArtifactV01:
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type="SemanticEvidence",
        schema_version="v1",
        transaction_id=transaction_id,
        owner_root_id=_E3_ROOT,
        source_component="continuous_delta_runtime_g2e3_test",
        authority_class="EVIDENCE_ONLY",
        lifecycle_state="VALIDATED",
        payload=payload,
        trace_refs=("trace:" + artifact_id,),
        parent_refs=parent_refs,
        time_envelope=time_envelope or _e3_time_envelope(),
    )


def _e4_runtime_artifact_projection(
    artifact: g2e.KernelArtifactV01,
) -> g2e.KernelArtifactV01:
    projected = kernel_artifact_to_plain_dict_v01(artifact)
    projected_sha256 = hashlib.sha256(
        canonical_json_bytes_v01(projected)
    ).hexdigest()
    return _e3_kernel_artifact(
        artifact_id="artifact:g2e:e4:runtime-projection:" + projected_sha256,
        transaction_id=artifact.transaction_id,
        payload={
            "projection_profile_id": (
                "g2e_baseline_runtime_artifact_projection_v01"
            ),
            "projected_runtime_artifact": projected,
            "projected_runtime_artifact_sha256": projected_sha256,
        },
        parent_refs=(artifact.artifact_id,),
    )


def _e3_g2d_serialization_seams() -> dict[type[object], tuple[object, object]]:
    return {
        g2d.FractalRuntimePolicyV02: (
            g2d.fractal_runtime_policy_to_plain_data_v02,
            g2d.rebuild_fractal_runtime_policy_identity_v02,
        ),
        g2d.FractalRuntimeBudgetV02: (
            g2d.fractal_runtime_budget_to_plain_data_v02,
            g2d.rebuild_fractal_runtime_budget_identity_v02,
        ),
        g2d.RuntimeTopologySourceBindingV02: (
            g2d.runtime_topology_source_binding_to_plain_data_v02,
            g2d.rebuild_runtime_topology_source_binding_identity_v02,
        ),
        g2d.RuntimeTopologySeedV02: (
            g2d.runtime_topology_seed_to_plain_data_v02,
            g2d.rebuild_runtime_topology_seed_identity_v02,
        ),
        g2d.RuntimeTopologyNodeV02: (
            g2d.runtime_topology_node_to_plain_data_v02,
            g2d.rebuild_runtime_topology_node_identity_v02,
        ),
        g2d.RuntimeTopologyEdgeV02: (
            g2d.runtime_topology_edge_to_plain_data_v02,
            g2d.rebuild_runtime_topology_edge_identity_v02,
        ),
        g2d.RuntimeAssignmentV02: (
            g2d.runtime_assignment_to_plain_data_v02,
            g2d.rebuild_runtime_assignment_identity_v02,
        ),
        g2d.RuntimeExecutionTopologyV02: (
            g2d.runtime_execution_topology_to_plain_data_v02,
            g2d.rebuild_runtime_execution_topology_identity_v02,
        ),
        g2d.ParentChildScopeProjectionV02: (
            g2d.parent_child_scope_projection_to_plain_data_v02,
            g2d.rebuild_parent_child_scope_projection_identity_v02,
        ),
        g2d.FractalCellInputV02: (
            g2d.fractal_cell_input_to_plain_data_v02,
            g2d.rebuild_fractal_cell_input_identity_v02,
        ),
        g2d.FractalCellQueueEntryV02: (
            g2d.fractal_cell_queue_entry_to_plain_data_v02,
            g2d.rebuild_fractal_cell_queue_entry_identity_v02,
        ),
        g2d.FractalReviseObservationV02: (
            g2d.fractal_revise_observation_to_plain_data_v02,
            g2d.rebuild_fractal_revise_observation_identity_v02,
        ),
        g2d.FractalPartialFailureRecordV02: (
            g2d.fractal_partial_failure_record_to_plain_data_v02,
            g2d.rebuild_fractal_partial_failure_record_identity_v02,
        ),
        g2d.FractalBackpressureStateV02: (
            g2d.fractal_backpressure_state_to_plain_data_v02,
            g2d.rebuild_fractal_backpressure_state_identity_v02,
        ),
        g2d.FractalCellResultV02: (
            g2d.fractal_cell_result_to_plain_data_v02,
            g2d.rebuild_fractal_cell_result_identity_v02,
        ),
        g2d.FractalRuntimeTraceV02: (
            g2d.fractal_runtime_trace_to_plain_data_v02,
            g2d.rebuild_fractal_runtime_trace_identity_v02,
        ),
        g2d.FractalRuntimeReportV02: (
            g2d.fractal_runtime_report_to_plain_data_v02,
            g2d.rebuild_fractal_runtime_report_identity_v02,
        ),
        g2d.FractalRuntimeValidationReportV02: (
            g2d.fractal_runtime_validation_report_to_plain_data_v02,
            g2d.rebuild_fractal_runtime_validation_report_identity_v02,
        ),
    }


def _e3_g2c_serialization_seams() -> dict[type[object], tuple[object, object]]:
    seams = {
        g2c.ExecutionModeBSEPBindingV01: (
            g2c.execution_mode_bsep_binding_to_plain_data_v01,
            g2c.rebuild_execution_mode_bsep_binding_identity_v01,
        ),
        g2c.ExecutionModeReplayBindingV01: (
            g2c.execution_mode_replay_binding_to_plain_data_v01,
            g2c.rebuild_execution_mode_replay_binding_identity_v01,
        ),
        g2c.ExecutionModeG2ABindingV01: (
            g2c.execution_mode_g2a_binding_to_plain_data_v01,
            g2c.rebuild_execution_mode_g2a_binding_identity_v01,
        ),
        g2c.ExecutionModeG2BBindingV01: (
            g2c.execution_mode_g2b_binding_to_plain_data_v01,
            g2c.rebuild_execution_mode_g2b_binding_identity_v01,
        ),
        g2c.ExecutionModeLocalModeProfileV01: (
            g2c.execution_mode_local_mode_profile_to_plain_data_v01,
            g2c.rebuild_execution_mode_local_mode_profile_identity_v01,
        ),
        g2c.ExecutionModeLocalRoutingSnapshotV01: (
            g2c.execution_mode_local_routing_snapshot_to_plain_data_v01,
            g2c.rebuild_execution_mode_local_routing_snapshot_identity_v01,
        ),
        g2c.ExecutionModeRouterInputV01: (
            g2c.execution_mode_router_input_to_plain_data_v01,
            g2c.rebuild_execution_mode_router_input_identity_v01,
        ),
        g2c.ExecutionModeFeasibilityRowV01: (
            g2c.execution_mode_feasibility_row_to_plain_data_v01,
            g2c.rebuild_execution_mode_feasibility_row_identity_v01,
        ),
        g2c.ExecutionModeProposalV01: (
            g2c.execution_mode_proposal_to_plain_data_v01,
            g2c.rebuild_execution_mode_proposal_identity_v01,
        ),
        g2c.RootExecutionModeReviewInputV01: (
            g2c.root_execution_mode_review_input_to_plain_data_v01,
            g2c.rebuild_root_execution_mode_review_input_identity_v01,
        ),
        g2c.RootExecutionModeDecisionV01: (
            g2c.root_execution_mode_decision_to_plain_data_v01,
            g2c.rebuild_root_execution_mode_decision_identity_v01,
        ),
        g2c.ExecutionModeValidationReportV01: (
            g2c.execution_mode_validation_report_to_plain_data_v01,
            g2c.rebuild_execution_mode_validation_report_identity_v01,
        ),
    }
    assert tuple(seams) == g2c.SERIALIZED_G2C_TYPES_V01
    return seams


def _e3_transition_profiles() -> tuple[
    transition.TransitionRegistryV01,
    transition.TransitionRegistryV01,
    transition.TransitionRegistryV01,
]:
    g2c_registry = transition.build_execution_mode_transition_registry_profile_v01()
    g2d_registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    default_registry = transition.build_default_transition_registry_v01()
    assert len(
        {
            g2c_registry.registry_id,
            g2d_registry.registry_id,
            default_registry.registry_id,
        }
    ) == 3
    return g2c_registry, g2d_registry, default_registry


def _e3_transition_registry_plain(
    value: transition.TransitionRegistryV01,
) -> dict[str, object]:
    if type(value) is not transition.TransitionRegistryV01:
        raise TypeError("transition registry observation type invalid")
    g2c_registry, g2d_registry, _default_registry = _e3_transition_profiles()
    if value.registry_id == g2c_registry.registry_id:
        if (
            value != g2c_registry
            or transition.validate_execution_mode_transition_registry_profile_v01(
                value
            )
            != ()
        ):
            raise ValueError("G2-C transition registry observation invalid")
        return transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
            value
        )
    if value.registry_id == g2d_registry.registry_id:
        if (
            value != g2d_registry
            or transition.validate_fractal_runtime_transition_registry_profile_v02(
                value
            )
            != ()
        ):
            raise ValueError("G2-D transition registry observation invalid")
        return transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
            value
        )
    raise ValueError("foreign transition registry observation forbidden")


def _e3_transition_decision_plain(
    value: transition.TransitionDecisionV01,
) -> dict[str, object]:
    if type(value) is not transition.TransitionDecisionV01:
        raise TypeError("transition decision observation type invalid")
    g2c_registry, g2d_registry, _default_registry = _e3_transition_profiles()
    if value.registry_id == g2c_registry.registry_id:
        if (
            transition.validate_execution_mode_transition_decision_v01(
                registry=g2c_registry,
                decision=value,
            )
            != ()
            or transition.rebuild_execution_mode_transition_decision_identity_v01(
                value
            )
            != value.decision_id
        ):
            raise ValueError("G2-C transition decision observation invalid")
        return transition.execution_mode_transition_decision_to_plain_dict_v01(
            registry=g2c_registry,
            decision=value,
        )
    if value.registry_id == g2d_registry.registry_id:
        if (
            transition.rebuild_fractal_runtime_transition_decision_identity_v02(
                value
            )
            != value.decision_id
        ):
            raise ValueError("G2-D transition decision observation invalid")
        return transition.fractal_runtime_transition_decision_to_plain_dict_v02(value)
    raise ValueError("foreign transition decision observation forbidden")


def _e3_transition_decision_identity(
    value: transition.TransitionDecisionV01,
) -> str:
    g2c_registry, g2d_registry, _default_registry = _e3_transition_profiles()
    if value.registry_id == g2c_registry.registry_id:
        identity = transition.rebuild_execution_mode_transition_decision_identity_v01(
            value
        )
    elif value.registry_id == g2d_registry.registry_id:
        identity = transition.rebuild_fractal_runtime_transition_decision_identity_v02(
            value
        )
    else:
        raise ValueError("foreign transition decision observation forbidden")
    if identity != value.decision_id:
        raise ValueError("transition decision observation identity mismatch")
    return identity


def _e3_public_plain(value: object) -> object:
    if value is None:
        return value
    if type(value) is bool:
        return value
    if type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("non-finite public observation")
        canonical_json_bytes_v01(value)
        return value
    if type(value) is str:
        return value
    if type(value) in {tuple, list}:
        return [_e3_public_plain(item) for item in value]
    if type(value) is dict:
        return {
            str(key): _e3_public_plain(item)
            for key, item in value.items()
        }
    if type(value) is g2e.KernelArtifactV01:
        return kernel_artifact_to_plain_dict_v01(value)
    g2c_seams = _e3_g2c_serialization_seams()
    if type(value) in g2c_seams:
        serializer, _rebuilder = g2c_seams[type(value)]
        return serializer(value)  # type: ignore[operator]
    seams = _e3_g2d_serialization_seams()
    if type(value) in seams:
        serializer, _rebuilder = seams[type(value)]
        return serializer(value)  # type: ignore[operator]
    if type(value) is transition.TransitionRegistryV01:
        return _e3_transition_registry_plain(value)
    if type(value) is transition.TransitionDecisionV01:
        return _e3_transition_decision_plain(value)
    if type(value) is g2e.CausalConsumptionRefV01:
        return causal_consumption_ref_to_plain_dict_v01(value)
    if type(value) is root_decision.RootDecisionKernelV01:
        return root_decision.root_decision_kernel_to_plain_dict_v01(value)
    if type(value) is root_decision.RootDecisionInputV01:
        return root_decision.root_decision_input_to_plain_dict_v01(value)
    if type(value) is root_decision.RootDecisionResultV01:
        return root_decision.root_decision_result_to_plain_dict_v01(value)
    if is_dataclass(value):
        return {
            field.name: _e3_public_plain(getattr(value, field.name))
            for field in fields(value)
        }
    raise TypeError(f"unsupported public observation type: {type(value)!r}")


def _e3_public_identity(value: object) -> str | None:
    if type(value) is g2e.KernelArtifactV01:
        return value.artifact_id
    g2c_seams = _e3_g2c_serialization_seams()
    if type(value) in g2c_seams:
        _serializer, rebuilder = g2c_seams[type(value)]
        return rebuilder(value)  # type: ignore[operator]
    seams = _e3_g2d_serialization_seams()
    if type(value) in seams:
        _serializer, rebuilder = seams[type(value)]
        return rebuilder(value)  # type: ignore[operator]
    if type(value) is transition.TransitionRegistryV01:
        _e3_transition_registry_plain(value)
        return value.registry_id
    if type(value) is transition.TransitionDecisionV01:
        return _e3_transition_decision_identity(value)
    for field_name in (
        "decision_id",
        "causal_ref_id",
        "kernel_id",
        "decision_input_id",
        "report_id",
        "trace_id",
        "topology_id",
        "source_binding_id",
    ):
        candidate = getattr(value, field_name, None)
        if type(candidate) is str and candidate:
            return candidate
    return None


def _e3_observation_digest(role: str, value: object) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(
            {
                "domain": _E3_BASELINE_OBSERVATION_DOMAIN,
                "typed_role": role,
                "value": _e3_public_plain(value),
            }
        )
    ).hexdigest()


def _e3_observation_members(
    value: object,
) -> tuple[tuple[int | None, object], ...]:
    if type(value) is tuple:
        indexed = tuple(enumerate(value))
        return indexed if indexed else ((None, value),)
    return ((None, value),)


def _e3_bundle_observations(
    bundle: g2d.FractalRuntimeExecutionBundleV02,
) -> tuple[tuple[dict[str, object], ...], tuple[tuple[object, ...], ...]]:
    rows: list[dict[str, object]] = []
    identities: list[tuple[object, ...]] = []
    for bundle_field in fields(g2d.FractalRuntimeExecutionBundleV02):
        field_value = getattr(bundle, bundle_field.name)
        for tuple_index, member in _e3_observation_members(field_value):
            identity = _e3_public_identity(member)
            rows.append(
                {
                    "field_name": bundle_field.name,
                    "tuple_index_or_none": tuple_index,
                    "exact_type_name": type(member).__name__,
                    "public_semantic_identity_or_none": identity,
                    "canonical_member_sha256": hashlib.sha256(
                        canonical_json_bytes_v01(_e3_public_plain(member))
                    ).hexdigest(),
                }
            )
            identities.append(
                (bundle_field.name, tuple_index, type(member).__name__, identity)
            )
    assert {row["field_name"] for row in rows} == {
        field.name for field in fields(g2d.FractalRuntimeExecutionBundleV02)
    }
    assert len(identities) == len(rows)
    return tuple(rows), tuple(identities)


def _e3_complete_observation_errors(
    source: g2d.FractalRuntimeSourceContextV02,
    bundle: g2d.FractalRuntimeExecutionBundleV02,
) -> tuple[tuple[str, str, str, str], ...]:
    candidates: list[tuple[str, object]] = [("source_context", source)]
    for bundle_field in fields(g2d.FractalRuntimeExecutionBundleV02):
        field_value = getattr(bundle, bundle_field.name)
        for tuple_index, member in _e3_observation_members(field_value):
            path = (
                f"bundle.{bundle_field.name}"
                if tuple_index is None
                else f"bundle.{bundle_field.name}[{tuple_index}]"
            )
            candidates.append((path, member))

    errors: list[tuple[str, str, str, str]] = []
    for path, value in candidates:
        try:
            plain = _e3_public_plain(value)
            canonical_json_bytes_v01(plain)
            _e3_public_identity(value)
        except Exception as exc:
            errors.append(
                (
                    path,
                    type(value).__name__,
                    type(exc).__name__,
                    str(exc),
                )
            )
    return tuple(errors)


def _e3_baseline_digests(
    source: g2d.FractalRuntimeSourceContextV02,
    bundle: g2d.FractalRuntimeExecutionBundleV02,
) -> tuple[str, str, str]:
    rows, identities = _e3_bundle_observations(bundle)
    return (
        _e3_observation_digest("G2E3_BASELINE_SOURCE_OBSERVATION", source),
        _e3_observation_digest("G2E3_BASELINE_MEMBER_OBSERVATION", rows),
        _e3_observation_digest("G2E3_BASELINE_MEMBER_IDENTITIES", identities),
    )


def _e3_expected_digest_mode(
    environment: dict[str, str],
    actual: tuple[str, str, str] | None = None,
) -> str:
    supplied = tuple(environment.get(name) for name in _E3_EXPECTED_DIGEST_ENV)
    if not any(item is not None for item in supplied):
        return "FOCUSED"
    if not all(item is not None for item in supplied):
        raise AssertionError("partial expected baseline observation")
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", item or "") is not None
        for item in supplied
    ), "malformed expected baseline observation"
    if actual is not None:
        assert supplied == actual, "baseline observation mismatch"
    return "ACCEPTANCE"


@pytest.fixture(scope="module")
def e3_baseline_fixture() -> dict[str, object]:
    environment = dict(os.environ)
    mode = _e3_expected_digest_mode(environment)
    g2b = _e3_g2b_family()
    source_family = _e3_g2d_source_family(g2b)
    source = source_family["source"]
    assert type(source) is g2d.FractalRuntimeSourceContextV02
    bundle, report = g2d.run_fractal_runtime_v02(source)
    assert report.status == "PASS" and bundle is not None
    assert g2d.validate_fractal_runtime_execution_bundle_v02(bundle).status == "PASS"
    if mode == "FOCUSED":
        print("G2E3_FOCUSED_BASELINE_PUBLIC_CALL_COMPLETED=1")
    else:
        print("\nG2E3_ACCEPTANCE_BASELINE_PUBLIC_CALL_COMPLETED=1")
    observation_errors = _e3_complete_observation_errors(source, bundle)
    if observation_errors:
        print(
            "G2E3_COMPLETE_OBSERVATION_ERRORS="
            + json.dumps(observation_errors, separators=(",", ":"))
        )
    assert observation_errors == (), observation_errors
    digests = _e3_baseline_digests(source, bundle)
    assert _e3_expected_digest_mode(environment, digests) == mode
    if mode == "FOCUSED":
        for label, digest in zip(
            (
                "G2E3_BASELINE_SOURCE_OBSERVATION_SHA256",
                "G2E3_BASELINE_MEMBER_OBSERVATION_SHA256",
                "G2E3_BASELINE_MEMBER_IDENTITIES_SHA256",
            ),
            digests,
        ):
            print(f"{label}={digest}")
        print("G2E3_FOCUSED_BASELINE_CALL_OBSERVED=1")
    else:
        print("G2E3_ACCEPTANCE_BASELINE_CALL_OBSERVED=1")
    g2a = _e3_g2a_family(str(g2b["transaction_id"]))
    return {
        "g2a": g2a,
        "g2b": g2b,
        "source_family": source_family,
        "source": source,
        "bundle": bundle,
        "digests": digests,
    }


@pytest.fixture(scope="module")
def e4_full_fractal_baseline_fixture() -> dict[str, object]:
    g2b = _e3_g2b_family()
    source_family = _e3_g2d_source_family(
        g2b,
        selected_mode="full_fractal",
    )
    source = source_family["source"]
    assert type(source) is g2d.FractalRuntimeSourceContextV02
    bundle, report = g2d.run_fractal_runtime_v02(source)
    assert report.status == "PASS" and bundle is not None
    assert g2d.validate_fractal_runtime_execution_bundle_v02(bundle).status == "PASS"
    child_inputs = tuple(
        item for item in bundle.cell_inputs if item.parent_cell_id is not None
    )
    assert len(child_inputs) == 2
    selected_input = child_inputs[-1]
    sibling_input = child_inputs[0]
    initial_queue_id = selected_input.ordered_initial_queue_entry_ids[0]
    seed_artifact = next(
        artifact
        for entry, artifact in zip(
            bundle.queue_entries,
            bundle.queue_artifacts,
            strict=True,
        )
        if entry.queue_entry_id == initial_queue_id
    )
    seed_projection = _e4_runtime_artifact_projection(seed_artifact)
    queue_artifact_by_entry_id = {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(
            bundle.queue_entries,
            bundle.queue_artifacts,
            strict=True,
        )
    }
    full_seed_artifacts = tuple(
        queue_artifact_by_entry_id[queue_entry_id]
        for cell_input in bundle.cell_inputs
        for queue_entry_id in cell_input.ordered_initial_queue_entry_ids
    )
    full_seed_projections = tuple(
        _e4_runtime_artifact_projection(artifact)
        for artifact in full_seed_artifacts
    )
    assert len(full_seed_artifacts) == sum(
        len(item.ordered_node_ids) for item in bundle.cell_inputs
    )
    g2a = _e3_g2a_family(str(g2b["transaction_id"]))
    return {
        "g2a": g2a,
        "g2b": g2b,
        "source_family": source_family,
        "source": source,
        "bundle": bundle,
        "selected_input": selected_input,
        "sibling_input": sibling_input,
        "selected_seed_artifact": seed_artifact,
        "selected_seed_projection": seed_projection,
        "full_seed_artifacts": full_seed_artifacts,
        "full_seed_projections": full_seed_projections,
    }


def _e3_changed_source_payloads(
    *,
    target_roles: tuple[str, ...],
    g2a: dict[str, object] | None,
    g2b: dict[str, object] | None,
    bundle: g2d.FractalRuntimeExecutionBundleV02 | None,
) -> tuple[dict[str, object], dict[str, object]]:
    if (
        len(target_roles) != 1
        or target_roles[0] not in {"ordinary", "packet", "certificate", "route"}
    ):
        raise ValueError("unsupported E3 source role")
    role = target_roles[0]
    baseline: dict[str, object] = {
        "hold_status": "OLD",
        "source_role": role,
    }
    observed: dict[str, object] = {
        "hold_status": "NEW",
        "source_role": role,
    }
    if role == "ordinary":
        return baseline, observed
    if g2a is None or g2b is None or bundle is None:
        raise ValueError("typed E3 source carrier required")
    if role == "packet":
        record = g2a["dependency"].dependency_records[0]
        invalidation = g2a["invalidation"]
        material = {
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
        baseline.update(material)
        observed.update(material)
        observed.update(
            {
                "content_sha256": invalidation.evidence_sha256,
                "observed_status": invalidation.observed_status,
                "invalidation_evidence_id": invalidation.invalidation_evidence_id,
                "packet_id": invalidation.packet_id,
            }
        )
        return baseline, observed
    if role == "certificate":
        certificate = g2b["certificate"]
        report = g2b["report"]
        source_record = next(
            item
            for item in report.source_records
            if item.meaning_record_id == certificate.meaning_record_id
        )
        material = {
            "source_reference_id": source_record.source_reference_ids[0],
            "semantic_address_id": certificate.semantic_address_id,
            "meaning_record_id": certificate.meaning_record_id,
            "query_id": certificate.query_id,
            "query_evaluation_id": certificate.query_evaluation_id,
            "required_evidence_classes": list(
                certificate.required_evidence_classes
            ),
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
        baseline.update(material)
        observed.update(material)
        observed["observed_evidence_fingerprint"] = _sha(
            "g2e-e3-observed-certificate-evidence"
        )
        return baseline, observed
    binding = bundle.source_binding
    material = {
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
    baseline.update(material)
    observed.update(material)
    observed["route_eligibility_artifact_sha256"] = _sha(
        "g2e-e3-observed-route-binding"
    )
    return baseline, observed


def _e3_manifest_source_family(
    *,
    transaction_id: str,
    target_roles: tuple[str, ...] = ("ordinary",),
    g2a: dict[str, object] | None = None,
    g2b: dict[str, object] | None = None,
    bundle: g2d.FractalRuntimeExecutionBundleV02 | None = None,
    runtime_seed_projection: g2e.KernelArtifactV01 | None = None,
    runtime_seed_projections: tuple[g2e.KernelArtifactV01, ...] = (),
) -> dict[str, object]:
    if runtime_seed_projection is not None and runtime_seed_projections:
        raise ValueError("runtime projection family is ambiguous")
    projections = (
        (runtime_seed_projection,)
        if runtime_seed_projection is not None
        else runtime_seed_projections
    )
    if len({item.artifact_id for item in projections}) != len(projections):
        raise ValueError("runtime projection family contains duplicates")
    baseline_payload, observed_payload = _e3_changed_source_payloads(
        target_roles=target_roles,
        g2a=g2a,
        g2b=g2b,
        bundle=bundle,
    )
    changed = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e3:source:baseline",
        transaction_id=transaction_id,
        payload=baseline_payload,
    )
    by_role = {
        role: _e3_kernel_artifact(
            artifact_id=f"artifact:g2e:e3:dependent:{role}",
            transaction_id=transaction_id,
            payload={"dependent_role": role},
        )
        for role in ("ordinary", "packet", "certificate", "route")
    }
    unrelated = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e3:unrelated",
        transaction_id=transaction_id,
        payload={"dependent_role": "unrelated"},
    )
    baseline = (
        changed,
        *by_role.values(),
        unrelated,
        *projections,
    )
    observed_changed = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e3:source:observed",
        transaction_id=transaction_id,
        payload=observed_payload,
        parent_refs=(changed.artifact_id,),
    )
    observed = (observed_changed, *baseline[1:])
    replay_edges = (
        *(
            ArtifactDependencyEdgeV01(
                artifact_id=by_role[role].artifact_id,
                depends_on_artifact_id=changed.artifact_id,
            )
            for role in target_roles
        ),
        *(
            ArtifactDependencyEdgeV01(
                artifact_id=projection.artifact_id,
                depends_on_artifact_id=changed.artifact_id,
            )
            for projection in projections
        ),
    )
    profile = build_default_seal_profile_v01()
    manifest = build_artifact_manifest_v01(
        transaction_id=transaction_id,
        profile=profile,
        artifacts=tuple(
            kernel_artifact_to_canonical_ref_v01(item) for item in baseline
        ),
        dependency_edges=replay_edges,
        root_ownership_bindings=tuple(
            RootOwnershipBindingV01(item.artifact_id, _E3_ROOT)
            for item in baseline
        ),
        evidence_class_bindings=tuple(
            EvidenceClassBindingV01(item.artifact_id, "TEST_EVIDENCE")
            for item in baseline
        ),
        authority_class_bindings=tuple(
            AuthorityClassBindingV01(item.artifact_id, item.authority_class)
            for item in baseline
        ),
    )
    replay = verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=tuple(
            (item.artifact_id, kernel_artifact_to_plain_dict_v01(item)["payload"])
            for item in baseline
        ),
        expected_manifest_hash=manifest.manifest_hash,
    )
    return {
        "baseline": baseline,
        "observed": observed,
        "manifest": manifest,
        "replay": replay,
        "replay_edges": replay_edges,
        "by_role": by_role,
    }


def _e3_delta_family(
    baseline_fixture: dict[str, object],
    *,
    target_roles: tuple[str, ...] = ("ordinary",),
    runtime_seed_projection: g2e.KernelArtifactV01 | None = None,
    runtime_seed_projections: tuple[g2e.KernelArtifactV01, ...] = (),
) -> dict[str, object]:
    bundle = baseline_fixture["bundle"]
    g2a = baseline_fixture["g2a"]
    g2b = baseline_fixture["g2b"]
    source_family = baseline_fixture["source_family"]
    assert type(bundle) is g2d.FractalRuntimeExecutionBundleV02
    transaction_id = bundle.source_context.router_input.transaction_id
    route = source_family["route"]
    assert type(route) is g2e.KernelArtifactV01
    source_rows = _e3_manifest_source_family(
        transaction_id=transaction_id,
        target_roles=target_roles,
        g2a=g2a,
        g2b=g2b,
        bundle=bundle,
        runtime_seed_projection=runtime_seed_projection,
        runtime_seed_projections=runtime_seed_projections,
    )
    baseline = source_rows["baseline"]
    observed = source_rows["observed"]
    manifest = source_rows["manifest"]
    replay = source_rows["replay"]
    replay_edges = source_rows["replay_edges"]
    by_role = source_rows["by_role"]
    changed = baseline[0]
    observed_changed = observed[0]
    edge_projection_bindings = tuple(
        (
            edge.artifact_id,
            edge.depends_on_artifact_id,
            ("/hold_status",) if edge.depends_on_artifact_id == changed.artifact_id else (),
            "FIELD_CAUSAL" if edge.depends_on_artifact_id == changed.artifact_id else "ARTIFACT_DEPENDENCY",
        )
        for edge in replay_edges
    )
    history = g2b["report"].query_evaluations[0].source_history_hash
    policy = g2b["report"].query.policy_version
    schema_versions = g2b["report"].query.schema_versions
    graph_basis, dependency_edges = g2e.project_integrity_replay_dependency_edges_v01(
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline,
        graph_version="v0.1",
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        domain_id=_E3_DOMAIN,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
        edge_projection_bindings=edge_projection_bindings,
    )
    graph = g2e.build_dependency_graph_index_v01(
        graph_basis_sha256=graph_basis,
        graph_version="v0.1",
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline,
        dependency_edges=dependency_edges,
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        domain_id=_E3_DOMAIN,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
        trace_refs=("trace:g2e:e3:graph",),
    )
    fingerprint_profile = g2e.build_dependency_fingerprint_profile_v01()
    before = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=baseline,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
    )
    after = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=observed,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
    )
    source_binding = g2e.build_delta_source_binding_v01(
        request_id="request:g2e:e3",
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        domain_id=_E3_DOMAIN,
        baseline_source_artifact_id=changed.artifact_id,
        baseline_source_artifact_type=changed.artifact_type,
        baseline_source_artifact_sha256=_e2_artifact_sha(changed),
        baseline_source_payload_sha256=_e2_payload_sha(changed),
        observed_source_artifact_id=observed_changed.artifact_id,
        observed_source_artifact_type=observed_changed.artifact_type,
        observed_source_artifact_sha256=_e2_artifact_sha(observed_changed),
        observed_source_payload_sha256=_e2_payload_sha(observed_changed),
        baseline_report_id=bundle.runtime_report.report_id,
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        baseline_policy_version=policy,
        observed_policy_version=policy,
        baseline_schema_versions=schema_versions,
        observed_schema_versions=schema_versions,
        baseline_source_history_hash=history,
        observed_source_history_hash=history,
        valid_from_utc=_E3_VALID_FROM_UTC,
        valid_to_utc=_E3_VALID_TO_UTC,
        trace_refs=("trace:g2e:e3:source-binding",),
    )
    changed_field = g2e.build_changed_field_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        json_pointer="/payload/hold_status",
        prior_value_sha256=hashlib.sha256(canonical_json_bytes_v01("OLD")).hexdigest(),
        observed_value_sha256=hashlib.sha256(canonical_json_bytes_v01("NEW")).hexdigest(),
        change_class="FIELD_VALUE_CHANGE",
        observed_at_utc=_E3_UTC,
        trace_refs=("trace:g2e:e3:changed-field",),
    )
    changed_artifact = g2e.build_changed_artifact_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        baseline_artifact_id=changed.artifact_id,
        baseline_artifact_type=changed.artifact_type,
        baseline_payload_sha256=_e2_payload_sha(changed),
        observed_artifact_id=observed_changed.artifact_id,
        observed_artifact_type=observed_changed.artifact_type,
        observed_payload_sha256=_e2_payload_sha(observed_changed),
        baseline_dependency_fingerprint=before,
        observed_dependency_fingerprint=after,
        change_class="ARTIFACT_SUCCESSOR",
        observed_at_utc=_E3_UTC,
        trace_refs=("trace:g2e:e3:changed-artifact",),
    )
    delta = g2e.build_world_state_delta_v01(
        ordered_source_binding_ids=(source_binding.source_binding_id,),
        request_id=source_binding.request_id,
        transaction_id=transaction_id,
        owning_root_id=_E3_ROOT,
        domain_id=_E3_DOMAIN,
        baseline_report_id=bundle.runtime_report.report_id,
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        observed_at_utc=_E3_UTC,
        valid_from_utc=_E3_VALID_FROM_UTC,
        valid_to_utc=_E3_VALID_TO_UTC,
        baseline_policy_version=policy,
        observed_policy_version=policy,
        baseline_schema_versions=schema_versions,
        observed_schema_versions=schema_versions,
        baseline_source_history_hash=history,
        observed_source_history_hash=history,
        ordered_changed_field_binding_ids=(changed_field.changed_field_binding_id,),
        ordered_changed_artifact_binding_ids=(changed_artifact.changed_artifact_binding_id,),
        dependency_fingerprint_before=before,
        dependency_fingerprint_after=after,
        trace_refs=("trace:g2e:e3:delta",),
    )
    request = g2e.build_affected_set_request_v01(
        delta=delta,
        graph=graph,
        trace_refs=("trace:g2e:e3:request",),
    )
    affected = g2e.compute_affected_set_v01(
        request=request,
        delta=delta,
        graph=graph,
        source_bindings=(source_binding,),
        changed_field_bindings=(changed_field,),
        changed_artifact_bindings=(changed_artifact,),
        dependency_edges=dependency_edges,
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
    )
    context = g2e.build_continuous_delta_source_context_v01(
        integrity_manifest=manifest,
        integrity_replay=replay,
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
        g2a_registry=g2a["registry"],
        g2a_packet=g2a["packet"],
        g2a_dependency_candidate=g2a["dependency"],
        g2a_current_observations=g2a["observations"],
        g2a_root_invalidation_material=g2a["invalidation"],
        g2b_resolution_report=g2b["report"],
        g2b_reuse_certificate=g2b["certificate"],
        g2b_writeback_evidence=None,
        g2c_source_context=source_family["g2c_source"],
        baseline_g2c_route_eligibility_artifact=route,
        baseline_g2d_execution_bundle=bundle,
        root_kernel=source_family["root_kernel"],
        post_vv_profile=None,
        gt_profile=None,
    )
    return {
        "baseline": baseline,
        "observed": observed,
        "manifest": manifest,
        "replay": replay,
        "dependency_edges": dependency_edges,
        "graph": graph,
        "source_binding": source_binding,
        "changed_field": changed_field,
        "changed_artifact": changed_artifact,
        "delta": delta,
        "request": request,
        "affected": affected,
        "context": context,
        "roles": by_role,
    }


def test_e1_exact_static_surface_and_zero_operation_boundary_v01() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    )
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )
    assert public_functions == (
        QUARTET_FUNCTIONS
        + E2_PUBLIC_FUNCTIONS
        + E3_PUBLIC_FUNCTIONS
        + E4_PUBLIC_FUNCTIONS
    )
    assert g2e.__all__ == (
        TYPE_NAMES
        + QUARTET_FUNCTIONS
        + E2_PUBLIC_FUNCTIONS
        + E3_PUBLIC_FUNCTIONS
        + E4_PUBLIC_FUNCTIONS
    )
    assert len(g2e.PUBLIC_G2E_REASON_CODES_V01) == 88
    assert len(g2e.VALIDATION_TARGETS_V01) == 32
    assert len(g2e.FAILURE_STAGES_V01) == 24
    assert g2e.VALIDATION_STATUSES_V01 == ("PASS", "FAIL_CLOSED")
    assert not imports.intersection(
        {"os", "pathlib", "time", "random", "socket", "requests", "subprocess"}
    )
    assert not any("tests" in item or "demo" in item for item in imports)
    assert kernel.WorldStateDeltaV01 is g2e.WorldStateDeltaV01
    global_names = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert {name for name in global_names if "CACHE" in name} == {
        "NO_CACHE_STATE_DOMAIN_V01"
    }


def test_e1_exact_twenty_type_field_order_and_frozen_geometry_v01() -> None:
    expected = _preflight_type_rows()
    actual = tuple(
        (value_type.__name__, tuple(field.name for field in fields(value_type)))
        for value_type in g2e.CONTINUOUS_DELTA_TYPES_V01
    )
    assert expected == actual
    assert tuple(value_type.__name__ for value_type in g2e.CONTINUOUS_DELTA_TYPES_V01) == TYPE_NAMES
    assert len(actual) == 20
    for value_type in g2e.CONTINUOUS_DELTA_TYPES_V01:
        assert is_dataclass(value_type)
        assert value_type.__dataclass_params__.frozen is True
    source = _source_binding()
    with pytest.raises(FrozenInstanceError):
        source.request_id = "request:mutated"  # type: ignore[misc]


def test_e1_exact_eighteen_serialized_identity_prefix_domain_registry_v01() -> None:
    expected = _preflight_identity_rows()
    actual = tuple(
        (type_name, stem, prefix, domain)
        for type_name, stem, _identity_field, prefix, domain
        in g2e.CONTINUOUS_DELTA_IDENTITY_PROFILES_V01
    )
    assert actual == expected
    assert len(actual) == 18
    assert len({row[2] for row in actual}) == 18
    assert len({row[3] for row in actual}) == 18
    assert g2e.RUNTIME_ONLY_CONTINUOUS_DELTA_TYPES_V01 == (
        g2e.ContinuousDeltaSourceContextV01,
        g2e.ContinuousDeltaExecutionBundleV01,
    )


def test_e1_exact_schema_definitions_and_python_parity_v01() -> None:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["version"] == "v0.1"
    assert schema["$ref"] == "#/$defs/WorldStateDeltaV01"
    definitions = schema["$defs"]
    assert tuple(definitions) == TYPE_NAMES[:18]
    assert len(definitions) == 18
    for value_type in g2e.SERIALIZED_CONTINUOUS_DELTA_TYPES_V01:
        definition = definitions[value_type.__name__]
        expected_fields = tuple(field.name for field in fields(value_type))
        assert tuple(definition["properties"]) == expected_fields
        assert tuple(definition["required"]) == expected_fields
        assert definition["additionalProperties"] is False
        annotations = get_type_hints(value_type)
        for field_name, annotation in annotations.items():
            property_schema = definition["properties"][field_name]
            origin = get_origin(annotation)
            if origin is tuple:
                assert property_schema.get("type") == "array" or type(
                    property_schema.get("const")
                ) is list
                continue
            if origin is types.UnionType:
                assert set(get_args(annotation)) == {str, type(None)}
                if field_name in {"prior_delta_id", "superseded_by_artifact_id"}:
                    assert property_schema == {"type": "null"}
                else:
                    assert set(property_schema["type"]) == {"string", "null"}
                continue
            expected_json_type = {str: "string", int: "integer", bool: "boolean"}[
                annotation
            ]
            if "type" in property_schema:
                schema_types = property_schema["type"]
                if type(schema_types) is str:
                    schema_types = [schema_types]
                assert expected_json_type in schema_types
            elif "const" in property_schema:
                assert {
                    str: "string",
                    int: "integer",
                    bool: "boolean",
                    list: "array",
                }[type(property_schema["const"])] == expected_json_type
            else:
                assert "enum" in property_schema
                assert all(type(item) is annotation for item in property_schema["enum"])
    assert TYPE_NAMES[18] not in definitions and TYPE_NAMES[19] not in definitions

    hash_pattern = "^[0-9a-f]{64}$"
    preservation = definitions["PreservationProofV01"]["properties"]
    for field_name in (
        "ordered_before_artifact_sha256",
        "ordered_after_artifact_sha256",
        "ordered_before_payload_sha256",
        "ordered_after_payload_sha256",
    ):
        assert preservation[field_name]["type"] == "array"
        assert preservation[field_name]["items"] == {
            "type": "string",
            "pattern": hash_pattern,
        }
    assert "uniqueItems" not in preservation["ordered_before_payload_sha256"]
    assert "uniqueItems" not in preservation["ordered_after_payload_sha256"]

    for type_name, field_name in (
        ("DeltaSourceBindingV01", "baseline_source_history_hash"),
        ("DeltaSourceBindingV01", "observed_source_history_hash"),
        ("WorldStateDeltaV01", "baseline_source_history_hash"),
        ("WorldStateDeltaV01", "observed_source_history_hash"),
        ("DependencyGraphIndexV01", "source_manifest_hash"),
        ("DependencyGraphIndexV01", "source_history_hash"),
    ):
        assert definitions[type_name]["properties"][field_name] == {
            "type": "string",
            "pattern": hash_pattern,
        }

    timestamp_patterns = tuple(
        property_schema["pattern"]
        for definition in definitions.values()
        for field_name, property_schema in definition["properties"].items()
        if field_name.endswith("_utc")
    )
    expected_timestamp_pattern = (
        r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
        r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
    )
    assert len(timestamp_patterns) == 7
    assert set(timestamp_patterns) == {expected_timestamp_pattern}
    for pattern in timestamp_patterns:
        assert re.fullmatch(pattern, "2026-08-11T01:00:00.123+00:00")
        assert re.fullmatch(pattern, "2026-08-11T01:00:00\\x123+00:00") is None

    change_pattern = "^[A-Za-z][A-Za-z0-9_.:/-]{0,255}$"
    assert definitions["ChangedFieldBindingV01"]["properties"]["change_class"] == {
        "type": "string",
        "pattern": change_pattern,
    }
    assert definitions["ChangedArtifactBindingV01"]["properties"]["change_class"] == {
        "type": "string",
        "pattern": change_pattern,
    }

    report_definition = definitions["ContinuousDeltaValidationReportV01"]
    assert report_definition["allOf"] == [
        {
            "if": {
                "properties": {"status": {"const": "PASS"}},
                "required": ["status"],
            },
            "then": {
                "properties": {
                    "validated_object_id": {"type": "string", "minLength": 1}
                }
            },
        }
    ]
    invalid_pass = g2e.continuous_delta_validation_report_to_plain_data_v01(
        _validation_report()
    )
    invalid_pass["validated_object_id"] = None
    with pytest.raises(ValidationError):
        Draft202012Validator(report_definition).validate(invalid_pass)
    serializers = (
        g2e.delta_source_binding_to_plain_data_v01,
        g2e.changed_field_binding_to_plain_data_v01,
        g2e.changed_artifact_binding_to_plain_data_v01,
        g2e.world_state_delta_to_plain_data_v01,
        g2e.dependency_fingerprint_profile_to_plain_data_v01,
        g2e.continuous_delta_validation_report_to_plain_data_v01,
    )
    for value, serializer in zip(_six_instances(), serializers, strict=True):
        Draft202012Validator(definitions[type(value).__name__]).validate(serializer(value))


def test_e1_exact_six_quartet_surface_and_signatures_v01() -> None:
    assert len(QUARTET_FUNCTIONS) == 24
    for name in QUARTET_FUNCTIONS:
        assert inspect.isfunction(getattr(g2e, name))
    assert tuple(inspect.signature(g2e.build_dependency_fingerprint_profile_v01).parameters) == ()
    report_parameters = inspect.signature(
        g2e.build_continuous_delta_validation_report_v01
    ).parameters
    assert "status" not in report_parameters
    assert tuple(report_parameters) == (
        "validation_target",
        "validated_object_id",
        "failure_stage",
        "reason_codes",
        "source_reason_codes",
        "return_to_root_required",
        "root_review_required",
    )
    source_parameters = inspect.signature(g2e.build_delta_source_binding_v01).parameters
    assert "source_binding_id" not in source_parameters
    assert "predecessor_relation" not in source_parameters
    assert "authority_created" not in source_parameters


def test_e1_identity_rebuild_plain_data_and_repeated_bytes_v01() -> None:
    serializers = (
        g2e.delta_source_binding_to_plain_data_v01,
        g2e.changed_field_binding_to_plain_data_v01,
        g2e.changed_artifact_binding_to_plain_data_v01,
        g2e.world_state_delta_to_plain_data_v01,
        g2e.dependency_fingerprint_profile_to_plain_data_v01,
        g2e.continuous_delta_validation_report_to_plain_data_v01,
    )
    rebuilders = (
        g2e.rebuild_delta_source_binding_identity_v01,
        g2e.rebuild_changed_field_binding_identity_v01,
        g2e.rebuild_changed_artifact_binding_identity_v01,
        g2e.rebuild_world_state_delta_identity_v01,
        g2e.rebuild_dependency_fingerprint_profile_identity_v01,
        g2e.rebuild_continuous_delta_validation_report_identity_v01,
    )
    validators = (
        g2e.validate_delta_source_binding_v01,
        g2e.validate_changed_field_binding_v01,
        g2e.validate_changed_artifact_binding_v01,
        g2e.validate_world_state_delta_v01,
        g2e.validate_dependency_fingerprint_profile_v01,
        g2e.validate_continuous_delta_validation_report_v01,
    )
    for value, serializer, rebuilder, validator in zip(
        _six_instances(), serializers, rebuilders, validators, strict=True
    ):
        identity_field = fields(type(value))[0].name
        identity = getattr(value, identity_field)
        assert rebuilder(value) == identity
        plain_a = serializer(value)
        plain_b = serializer(value)
        assert canonical_json_bytes_v01(plain_a) == canonical_json_bytes_v01(plain_b)
        first_key = next(iter(plain_a))
        plain_a[first_key] = "caller:mutation"
        assert serializer(value) == plain_b
        for field in fields(type(value))[1:]:
            candidate = replace(value, **{field.name: _alternate(getattr(value, field.name))})
            rebuilt = rebuilder(candidate)
            assert rebuilt != identity
            assert validator(candidate).status == "FAIL_CLOSED"


def test_e1_validation_report_status_reason_derivation_v01() -> None:
    passed = _validation_report()
    failed = g2e.build_continuous_delta_validation_report_v01(
        validation_target="WorldStateDeltaV01",
        validated_object_id=None,
        failure_stage="delta_source_structure",
        reason_codes=("g2e_object_invalid",),
        source_reason_codes=(),
        return_to_root_required=True,
        root_review_required=False,
    )
    assert passed.status == "PASS" and passed.reason_codes == ()
    assert failed.status == "FAIL_CLOSED"
    assert failed.reason_codes == ("g2e_object_invalid",)
    for report in (passed, failed):
        assert report.authority_created is False
        assert report.permission_created is False
        assert report.action_commit_packet_created is False
        assert report.receipt_created is False
        assert report.final_output_created is False
        assert report.drs_write_created is False
        assert report.real_world_effects_count == 0
    forged = replace(passed, status="FAIL_CLOSED")
    forged = replace(
        forged,
        validation_report_id=g2e.rebuild_continuous_delta_validation_report_identity_v01(forged),
    )
    assert g2e.validate_continuous_delta_validation_report_v01(forged).status == "FAIL_CLOSED"
    with pytest.raises(ValueError, match="^g2e_identity_invalid$"):
        g2e.build_continuous_delta_validation_report_v01(
            validation_target="WorldStateDeltaV01",
            validated_object_id=None,
            failure_stage="delta_source_structure",
            reason_codes=(),
            source_reason_codes=(),
            return_to_root_required=False,
            root_review_required=False,
        )
    pass_without_id = replace(passed, validated_object_id=None)
    pass_without_id = replace(
        pass_without_id,
        validation_report_id=g2e.rebuild_continuous_delta_validation_report_identity_v01(
            pass_without_id
        ),
    )
    rejected = g2e.validate_continuous_delta_validation_report_v01(pass_without_id)
    assert rejected.status == "FAIL_CLOSED"
    assert rejected.reason_codes == ("g2e_identity_invalid",)
    with pytest.raises(ValueError, match="^g2e_status_invalid$"):
        g2e.build_continuous_delta_validation_report_v01(
            validation_target="WorldStateDeltaV01",
            validated_object_id=passed.validated_object_id,
            failure_stage="delta_source_structure",
            reason_codes=(),
            source_reason_codes=(),
            return_to_root_required=True,
            root_review_required=False,
        )


def test_e1_delta_source_binding_immutable_pair_and_no_dangling_reports_v01() -> None:
    source = _source_binding()
    names = tuple(field.name for field in fields(g2e.DeltaSourceBindingV01))
    assert "baseline_source_validation_report_id" not in names
    assert "observed_source_validation_report_id" not in names
    assert "baseline_source_status" not in names
    assert "observed_source_status" not in names
    assert source.baseline_source_artifact_id != source.observed_source_artifact_id
    assert source.predecessor_relation == "OBSERVED_SUCCESSOR_OF_BASELINE"
    assert source.authority_created is False and source.real_world_effects_count == 0
    assert g2e.validate_delta_source_binding_v01(source).status == "PASS"
    for changes in (
        {"baseline_source_artifact_id": source.observed_source_artifact_id},
        {"baseline_source_artifact_type": "ResultProposal"},
        {"predecessor_relation": "MUTATED"},
        {"binding_version": "v9.9"},
    ):
        assert g2e.validate_delta_source_binding_v01(replace(source, **changes)).status == "FAIL_CLOSED"
    fractional = replace(source, valid_from_utc="2026-08-11T00:00:00.123+00:00")
    fractional = replace(
        fractional,
        source_binding_id=g2e.rebuild_delta_source_binding_identity_v01(fractional),
    )
    assert g2e.validate_delta_source_binding_v01(fractional).status == "PASS"
    impossible = replace(source, valid_from_utc="2026-02-30T00:00:00+00:00")
    impossible = replace(
        impossible,
        source_binding_id=g2e.rebuild_delta_source_binding_identity_v01(impossible),
    )
    invalid = g2e.validate_delta_source_binding_v01(impossible)
    assert invalid.status == "FAIL_CLOSED"
    assert invalid.reason_codes == ("g2e_delta_time_invalid",)


def test_e1_changed_field_binding_structural_mutation_matrix_v01() -> None:
    value = _changed_field()
    assert g2e.validate_changed_field_binding_v01(value).status == "PASS"
    for changes in (
        {"json_pointer": "payload/not-a-pointer"},
        {"json_pointer": "/payload/~2invalid"},
        {"observed_value_sha256": value.prior_value_sha256},
        {"prior_value_sha256": "A" * 64},
        {"change_class": "contains whitespace"},
        {"source_binding_id": "source:untyped"},
        {"changed_field_binding_id": "g2e_changed_field_binding_v01:" + _sha("copied")},
    ):
        assert g2e.validate_changed_field_binding_v01(replace(value, **changes)).status == "FAIL_CLOSED"
    impossible = replace(value, observed_at_utc="2026-13-11T01:00:00+00:00")
    impossible = replace(
        impossible,
        changed_field_binding_id=g2e.rebuild_changed_field_binding_identity_v01(
            impossible
        ),
    )
    invalid = g2e.validate_changed_field_binding_v01(impossible)
    assert invalid.status == "FAIL_CLOSED"
    assert invalid.reason_codes == ("g2e_delta_time_invalid",)


def test_e1_changed_artifact_binding_structural_mutation_matrix_v01() -> None:
    value = _changed_artifact()
    assert g2e.validate_changed_artifact_binding_v01(value).status == "PASS"
    for changes in (
        {"observed_artifact_id": value.baseline_artifact_id},
        {"observed_artifact_type": "ResultProposal"},
        {"predecessor_relation": "IN_PLACE_MUTATION"},
        {"observed_payload_sha256": "not-a-digest"},
        {"source_binding_id": "source:untyped"},
        {"changed_artifact_binding_id": "g2e_changed_artifact_binding_v01:" + _sha("copied")},
    ):
        assert g2e.validate_changed_artifact_binding_v01(replace(value, **changes)).status == "FAIL_CLOSED"
    impossible = replace(value, observed_at_utc="2026-08-11T25:00:00+00:00")
    impossible = replace(
        impossible,
        changed_artifact_binding_id=g2e.rebuild_changed_artifact_binding_identity_v01(
            impossible
        ),
    )
    invalid = g2e.validate_changed_artifact_binding_v01(impossible)
    assert invalid.status == "FAIL_CLOSED"
    assert invalid.reason_codes == ("g2e_delta_time_invalid",)


def test_e1_world_state_delta_single_baseline_zero_operation_matrix_v01() -> None:
    value = _delta()
    assert value.delta_sequence == 1 and value.prior_delta_id is None
    assert value.ordered_source_binding_ids
    assert value.ordered_changed_field_binding_ids or value.ordered_changed_artifact_binding_ids
    assert g2e.validate_world_state_delta_v01(value).status == "PASS"
    for changes in (
        {"delta_sequence": 2},
        {"prior_delta_id": "g2e_world_state_delta_v01:" + _sha("prior")},
        {"ordered_source_binding_ids": ()},
        {"ordered_source_binding_ids": value.ordered_source_binding_ids * 2},
        {"ordered_changed_field_binding_ids": (), "ordered_changed_artifact_binding_ids": ()},
        {"permission_created": True},
        {"action_commit_packet_created": True},
        {"receipt_created": True},
        {"final_output_created": True},
        {"drs_write_created": True},
        {"authority_created": True},
        {"real_world_effects_count": 1},
    ):
        assert g2e.validate_world_state_delta_v01(replace(value, **changes)).status == "FAIL_CLOSED"
    boolean_sequence = replace(value, delta_sequence=True)
    boolean_sequence = replace(
        boolean_sequence,
        delta_id=g2e.rebuild_world_state_delta_identity_v01(boolean_sequence),
    )
    rejected_boolean = g2e.validate_world_state_delta_v01(boolean_sequence)
    assert rejected_boolean.status == "FAIL_CLOSED"
    assert rejected_boolean.reason_codes == ("g2e_repeated_delta_conflict",)
    impossible = replace(value, observed_at_utc="2026-08-11T01:00:00+24:00")
    impossible = replace(
        impossible,
        delta_id=g2e.rebuild_world_state_delta_identity_v01(impossible),
    )
    rejected_time = g2e.validate_world_state_delta_v01(impossible)
    assert rejected_time.status == "FAIL_CLOSED"
    assert rejected_time.reason_codes == ("g2e_delta_time_invalid",)


def test_e1_dependency_fingerprint_profile_typed_role_structure_v01() -> None:
    profile = g2e.build_dependency_fingerprint_profile_v01()
    assert profile.hash_algorithm == "sha256"
    assert profile.canonicalization_profile_id == "integrity_replay_canonical_json_v01"
    assert profile.domain_separator == "HEDGEHOG_CONTINUOUS_DELTA_DEPENDENCY_FINGERPRINT_V01"
    assert profile.typed_role == "G2E_DEPENDENCY_CURRENTNESS"
    assert profile.cross_role_reuse_forbidden is True
    assert profile.ordered_preimage_fields == g2e.DEPENDENCY_FINGERPRINT_PREIMAGE_FIELDS_V01
    assert g2e.validate_dependency_fingerprint_profile_v01(profile).status == "PASS"
    for field_name in (
        "hash_algorithm",
        "canonicalization_profile_id",
        "domain_separator",
        "typed_role",
    ):
        assert g2e.validate_dependency_fingerprint_profile_v01(
            replace(profile, **{field_name: "caller_preimage"})
        ).status == "FAIL_CLOSED"
    assert hasattr(g2e, "build_dependency_fingerprint_v01")


def test_e1_runtime_only_context_and_bundle_declarations_v01() -> None:
    assert tuple(value_type.__name__ for value_type in g2e.RUNTIME_ONLY_CONTINUOUS_DELTA_TYPES_V01) == TYPE_NAMES[18:]
    assert tuple(field.name for field in fields(g2e.ContinuousDeltaSourceContextV01)) == _preflight_type_rows()[18][1]
    assert tuple(field.name for field in fields(g2e.ContinuousDeltaExecutionBundleV01)) == _preflight_type_rows()[19][1]
    schema_defs = _schema()["$defs"]
    assert "ContinuousDeltaSourceContextV01" not in schema_defs
    assert "ContinuousDeltaExecutionBundleV01" not in schema_defs
    context_annotations = get_type_hints(g2e.ContinuousDeltaSourceContextV01)
    assert {
        field_name: context_annotations[field_name]
        for field_name in (
            "integrity_manifest",
            "integrity_replay",
            "baseline_source_artifacts",
            "observed_source_artifacts",
            "g2c_source_context",
            "baseline_g2c_route_eligibility_artifact",
            "baseline_g2d_execution_bundle",
            "root_kernel",
        )
    } == {
        "integrity_manifest": g2e.ArtifactManifestV01,
        "integrity_replay": g2e.ReplayVerificationResultV01,
        "baseline_source_artifacts": tuple[g2e.KernelArtifactV01, ...],
        "observed_source_artifacts": tuple[g2e.KernelArtifactV01, ...],
        "g2c_source_context": g2e.ExecutionModeSourceContextV01,
        "baseline_g2c_route_eligibility_artifact": g2e.KernelArtifactV01,
        "baseline_g2d_execution_bundle": g2e.FractalRuntimeExecutionBundleV02,
        "root_kernel": g2e.RootDecisionKernelV01,
    }
    bundle_annotations = get_type_hints(g2e.ContinuousDeltaExecutionBundleV01)
    artifact_fields = (
        "delta_source_proposed_artifact",
        "delta_source_artifact",
        "dependency_graph_artifact",
        "affected_set_artifact",
        "invalidation_report_artifact",
        "plan_proposed_artifact",
        "plan_root_decision_artifact",
        "plan_accepted_artifact",
        "preservation_proof_artifact",
        "final_root_decision_artifact",
        "runtime_report_artifact",
    )
    assert all(
        bundle_annotations[field_name] is g2e.KernelArtifactV01
        for field_name in artifact_fields
    )
    assert bundle_annotations["plan_root_decision_input"] is g2e.RootDecisionInputV01
    assert bundle_annotations["plan_root_decision_result"] is g2e.RootDecisionResultV01
    assert bundle_annotations["final_root_decision_input"] is g2e.RootDecisionInputV01
    assert bundle_annotations["final_root_decision_result"] is g2e.RootDecisionResultV01
    assert (
        bundle_annotations["recomputed_g2d_execution_bundle"]
        is g2e.FractalRuntimeExecutionBundleV02
    )
    assert bundle_annotations["g2e_transition_decisions"] == tuple[
        g2e.TransitionDecisionV01, ...
    ]
    assert bundle_annotations["g2e_causal_consumption_refs"] == tuple[
        g2e.CausalConsumptionRefV01, ...
    ]
    assert all(bundle_annotations[field_name] is not object for field_name in artifact_fields)
    assert hasattr(g2e, "build_continuous_delta_source_context_v01")
    assert hasattr(g2e, "validate_continuous_delta_source_context_v01")
    assert hasattr(g2e, "build_continuous_delta_execution_bundle_v01")
    assert hasattr(g2e, "validate_continuous_delta_execution_bundle_v01")


def test_e1_abi_profile_declarations_and_future_slice_behavior_absent_v01() -> None:
    assert g2e.G2E_ABI_ARTIFACT_TYPES_V01 == (
        "ContinuousDeltaSource",
        "DependencyGraphIndex",
        "AffectedSetResult",
        "ArtifactInvalidationReport",
        "PreservationProof",
        "SelectiveRecomputationPlan",
        "ContinuousDeltaRuntimeReport",
    )
    instances = g2e.G2E_ABI_ARTIFACT_INSTANCE_PROFILES_V01
    assert len(g2e.G2E_ABI_ARTIFACT_PROFILES_V01) == 7
    assert len(instances) == 9
    assert len({row[0] for row in instances}) == 9
    assert len({row[6] for row in instances}) == 9
    assert len({row[7] for row in instances}) == 9
    source_rows = tuple(row for row in instances if row[1] == "ContinuousDeltaSource")
    plan_rows = tuple(row for row in instances if row[1] == "SelectiveRecomputationPlan")
    assert tuple(row[3] for row in source_rows) == ("PROPOSED", "VALIDATED")
    assert tuple(row[3] for row in plan_rows) == ("PROPOSED", "ROOT_ACCEPTED")
    assert tuple(row[-1] for row in g2e.G2E_ABI_ARTIFACT_PROFILES_V01) == (2, 1, 1, 1, 1, 2, 1)
    delta_policy_schema = (
        ("schema_version", "v0.1"),
        ("policy_version", "delta.observed_policy_version"),
        ("schema_versions", "delta.observed_schema_versions"),
    )
    graph_policy_schema = (
        ("schema_version", "v0.1"),
        ("policy_version", "graph.policy_version"),
        ("schema_versions", "graph.schema_versions"),
    )
    baseline_route_time = (
        ("ct_session_anchor", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.ct_session_anchor"),
        ("freshness_class", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.freshness_class"),
        ("kt_asof", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.kt_asof"),
        ("ttl_seconds", "source_context.baseline_g2c_route_eligibility_artifact.time_envelope.ttl_seconds"),
        ("et_observed_at", "delta.observed_at_utc"),
        ("pt_created_at", "delta.observed_at_utc"),
        ("valid_from", "delta.valid_from_utc"),
        ("valid_to", "delta.valid_to_utc"),
    )
    recomputed_report_time = tuple(
        (
            field_name,
            "recomputed_g2d_execution_bundle.report_artifact.time_envelope."
            + field_name,
        )
        for field_name in (
            "ct_session_anchor",
            "freshness_class",
            "kt_asof",
            "ttl_seconds",
            "et_observed_at",
            "pt_created_at",
            "valid_from",
            "valid_to",
        )
    )
    profiles = {row[0]: row for row in g2e.G2E_ABI_ARTIFACT_PROFILES_V01}
    for artifact_type in (
        "ContinuousDeltaSource",
        "AffectedSetResult",
        "ArtifactInvalidationReport",
        "SelectiveRecomputationPlan",
    ):
        assert profiles[artifact_type][8] == delta_policy_schema
        assert profiles[artifact_type][9] == baseline_route_time
    assert profiles["DependencyGraphIndex"][8] == graph_policy_schema
    assert profiles["DependencyGraphIndex"][9] == baseline_route_time
    for artifact_type in ("PreservationProof", "ContinuousDeltaRuntimeReport"):
        assert profiles[artifact_type][8] == delta_policy_schema
        assert profiles[artifact_type][9] == recomputed_report_time
    profile_text = repr(g2e.G2E_ABI_ARTIFACT_PROFILES_V01).lower()
    assert "appropriate" not in profile_text
    assert "equivalent" not in profile_text
    assert "baseline route envelope plus delta observation/validity times" not in profile_text
    assert "recomputed g2-d report artifact envelope" not in profile_text
    present = (
        "derive_invalidation_report_v01",
        "prove_unaffected_artifact_preservation_v01",
        "build_artifact_invalidation_record_v01",
        "build_invalidation_report_v01",
        "build_preservation_proof_v01",
    )
    assert all(hasattr(g2e, name) for name in present)
    implemented = (
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
    )
    assert all(hasattr(g2e, name) for name in implemented)
    assert not hasattr(g2e, "build_continuous_delta_transition_registry_profile_v01")


def test_e2_exact_public_surface_and_slice_boundary_v01() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    assert len(E2_QUARTET_FUNCTIONS) == 16
    assert len(E2_BEHAVIORAL_FUNCTIONS) == 5
    e2_prefix = QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert public_functions[:45] == e2_prefix
    assert len(public_functions) == 89
    assert g2e.__all__[:65] == TYPE_NAMES + e2_prefix
    assert len(g2e.__all__) == 109
    assert public_functions[45:62] == E3_PUBLIC_FUNCTIONS
    assert public_functions[62:] == E4_PUBLIC_FUNCTIONS
    assert g2e.__all__[82:] == E4_PUBLIC_FUNCTIONS
    assert g2e.CONTINUOUS_DELTA_GRAPH_VERSION_V01 == "v0.1"
    assert g2e.MAX_DEPENDENCY_GRAPH_NODES_V01 == 256
    assert g2e.MAX_DEPENDENCY_GRAPH_EDGES_V01 == 1024
    assert g2e.MAX_AFFECTED_HOPS_V01 == 32
    assert len(E4_PUBLIC_FUNCTIONS) == 27
    for name in E4_PUBLIC_FUNCTIONS:
        assert hasattr(g2e, name)
    assert "source_context" not in inspect.signature(
        g2e.compute_affected_set_v01
    ).parameters
    assert "source_context" not in inspect.signature(
        g2e.validate_affected_set_against_graph_v01
    ).parameters
    addendum_raw = ADDENDUM_PATH.read_bytes()
    assert hashlib.sha256(addendum_raw).hexdigest() == ACCEPTED_ADDENDUM_SHA256
    assert len(addendum_raw) == 81590
    assert addendum_raw.count(b"\n") == 1814
    donor_begin = b"----- BEGIN EXACT V0.1.3 PENDING DONOR BYTES -----\n"
    donor_end = b"----- END EXACT V0.1.3 PENDING DONOR BYTES -----\n"
    historical_begin = b"----- BEGIN EXACT V0.1.2 REPOSITORY BYTES -----\n"
    historical_end = b"----- END EXACT V0.1.2 REPOSITORY BYTES -----\n"
    assert addendum_raw.count(donor_begin) == 1
    assert addendum_raw.count(donor_end) == 1
    assert addendum_raw.count(historical_begin) == 1
    assert addendum_raw.count(historical_end) == 1
    active_prefix, remainder = addendum_raw.split(donor_begin, 1)
    donor_raw, remainder = remainder.split(donor_end, 1)
    between, remainder = remainder.split(historical_begin, 1)
    historical_raw, suffix = remainder.split(historical_end, 1)
    assert suffix == b""
    assert hashlib.sha256(donor_raw).hexdigest() == ACCEPTED_V013_DONOR_SHA256
    assert len(donor_raw) == 27273
    assert donor_raw.count(b"\n") == 562
    assert hashlib.sha256(historical_raw).hexdigest() == (
        ACCEPTED_V012_ADDENDUM_SHA256
    )
    assert len(historical_raw) == 47873
    assert historical_raw.count(b"\n") == 1133
    active_text = active_prefix.decode("utf-8")
    donor_text = donor_raw.decode("utf-8")
    historical_text = historical_raw.decode("utf-8")
    assert "document_revision: v0.1.3" in active_text
    assert "guardian_review_status: ACCEPTED" in active_text
    assert "guardian_review_status: PENDING" not in active_text
    assert f"guardian_accepted_v013_pending_draft_sha256: {ACCEPTED_V013_DONOR_SHA256}" in active_text
    assert "g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D" in active_text
    assert "g2e4_contract_status: ACCEPTED_IMPLEMENTATION_PENDING" in active_text
    assert "g2e4_status: NOT_STARTED_NOT_AUTHORIZED" in active_text
    assert "implementation_authorized: false" in active_text
    assert "implementation_started: false" in active_text
    assert "e4_public_seam_register_sha256: a10be3df58ed7fbf32fcb853c7de93f76eec5b3070120b0f895b27340cf2aed2" in active_text
    assert "e4_two_root_pair_register_sha256: a8a8fd530d95ec4bce8a0faf14044c8b98f53973651cf65784a717d69e02ce33" in active_text
    assert "schemas/continuous_delta_runtime_v01.schema.json` remains byte-frozen" in active_text
    assert "document_status=PENDING_GUARDIAN_REVIEW" in donor_text
    assert "Version 0.1.1 remains controlling for PAC-01 through PAC-08" in historical_text
    assert "v0.1.2 addendum controls PAC-09 through PAC-12" in historical_text
    assert "does not self-authorize implementation" in historical_text
    assert "g2e3_implementation_authorized: false" in historical_text
    assert between.startswith(b"\n")
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    test_names = tuple(
        node.name
        for node in test_tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )
    assert len(test_names) == 68
    assert sum(name.startswith("test_e3_") for name in test_names) == 18
    assert sum(name.startswith("test_e4_") for name in test_names) == 18


def test_e2_four_quartets_identity_plain_data_and_schema_v01() -> None:
    fixture = _e2_fixture()
    values = (
        fixture["dependency_edges"][0],
        fixture["graph"],
        fixture["request"],
        fixture["result"],
    )
    serializers = (
        g2e.delta_dependency_edge_to_plain_data_v01,
        g2e.dependency_graph_index_to_plain_data_v01,
        g2e.affected_set_request_to_plain_data_v01,
        g2e.affected_set_result_to_plain_data_v01,
    )
    rebuilders = (
        g2e.rebuild_delta_dependency_edge_identity_v01,
        g2e.rebuild_dependency_graph_index_identity_v01,
        g2e.rebuild_affected_set_request_identity_v01,
        g2e.rebuild_affected_set_result_identity_v01,
    )
    validators = (
        g2e.validate_delta_dependency_edge_v01,
        g2e.validate_dependency_graph_index_v01,
        g2e.validate_affected_set_request_v01,
        g2e.validate_affected_set_result_v01,
    )
    definitions = _schema()["$defs"]
    for value, serializer, rebuilder, validator in zip(
        values, serializers, rebuilders, validators, strict=True
    ):
        plain_a = serializer(value)
        plain_b = serializer(value)
        identity_name = fields(type(value))[0].name
        assert rebuilder(value) == getattr(value, identity_name)
        assert canonical_json_bytes_v01(plain_a) == canonical_json_bytes_v01(
            plain_b
        )
        assert validator(value).status == "PASS"
        Draft202012Validator(definitions[type(value).__name__]).validate(plain_a)


def test_e2_delta_dependency_edge_structural_mutation_matrix_v01() -> None:
    edge = _e2_fixture()["dependency_edges"][0]
    assert g2e.validate_delta_dependency_edge_v01(edge).status == "PASS"
    mutations = (
        ({"graph_version": "v9.9"}, "g2e_dependency_graph_version_mismatch"),
        (
            {"dependency_artifact_id": edge.dependent_artifact_id},
            "g2e_dependency_edge_self",
        ),
        ({"dependency_field_pointers": ("/~2",)}, "g2e_dependency_edge_invalid"),
        ({"edge_class": "bad class"}, "g2e_dependency_edge_invalid"),
        ({"canonical_order": 0}, "g2e_dependency_graph_ordering_invalid"),
        ({"source_replay_edge_sha256": "x"}, "g2e_dependency_replay_edge_mismatch"),
    )
    for changes, reason in mutations:
        candidate = replace(edge, **changes)
        candidate = replace(
            candidate,
            edge_id=g2e.rebuild_delta_dependency_edge_identity_v01(candidate),
        )
        report = g2e.validate_delta_dependency_edge_v01(candidate)
        assert report.status == "FAIL_CLOSED"
        assert reason in report.reason_codes
    copied = replace(edge, edge_id="g2e_delta_dependency_edge_v01:" + _sha("copy"))
    assert g2e.validate_delta_dependency_edge_v01(copied).reason_codes == (
        "g2e_identity_mismatch",
    )


def test_e2_dependency_graph_index_structural_mutation_matrix_v01() -> None:
    graph = _e2_fixture()["graph"]
    assert g2e.validate_dependency_graph_index_v01(graph).status == "PASS"
    for changes, reason in (
        ({"graph_version": "v9.9"}, "g2e_dependency_graph_version_mismatch"),
        ({"graph_basis_sha256": "x"}, "g2e_dependency_graph_basis_mismatch"),
        ({"node_count": graph.node_count + 1}, "g2e_dependency_graph_bounds_exceeded"),
        ({"edge_count": graph.edge_count + 1}, "g2e_dependency_graph_bounds_exceeded"),
        ({"max_nodes": 255}, "g2e_dependency_graph_bounds_exceeded"),
        ({"max_edges": 1023}, "g2e_dependency_graph_bounds_exceeded"),
        ({"max_hops": 31}, "g2e_dependency_graph_bounds_exceeded"),
        ({"acyclic": False}, "g2e_dependency_graph_bounds_exceeded"),
    ):
        candidate = replace(graph, **changes)
        candidate = replace(
            candidate,
            graph_id=g2e.rebuild_dependency_graph_index_identity_v01(candidate),
        )
        assert reason in g2e.validate_dependency_graph_index_v01(
            candidate
        ).reason_codes


def test_e2_affected_request_and_result_structural_matrix_v01() -> None:
    fixture = _e2_fixture()
    request = fixture["request"]
    result = fixture["result"]
    assert g2e.validate_affected_set_request_v01(request).status == "PASS"
    assert g2e.validate_affected_set_result_v01(result).status == "PASS"
    for changes in (
        {"max_nodes": 255},
        {
            "ordered_changed_field_binding_ids": (),
            "ordered_changed_artifact_binding_ids": (),
        },
    ):
        candidate = replace(request, **changes)
        candidate = replace(
            candidate,
            affected_request_id=g2e.rebuild_affected_set_request_identity_v01(
                candidate
            ),
        )
        assert g2e.validate_affected_set_request_v01(candidate).status == "FAIL_CLOSED"
    for changes in (
        {"complete": False},
        {"minimal": False},
        {"visited_node_count": 0},
        {"maximum_observed_hops": 33},
    ):
        candidate = replace(result, **changes)
        candidate = replace(
            candidate,
            affected_set_id=g2e.rebuild_affected_set_result_identity_v01(candidate),
        )
        assert g2e.validate_affected_set_result_v01(candidate).status == "FAIL_CLOSED"


def test_e2_replay_edge_projection_pre_id_order_and_graph_basis_v01() -> None:
    fixture = _e2_fixture()
    kwargs = {
        "manifest": fixture["manifest"],
        "replay": fixture["replay"],
        "source_artifacts": fixture["baseline"],
        "graph_version": "v0.1",
        "transaction_id": "transaction:g2e:e2",
        "owning_root_id": "root:g2e:e2",
        "domain_id": "TRAVEL_POLICY_INFORMATION",
        "policy_version": "policy:v1",
        "schema_versions": ("v1",),
        "source_history_hash": _sha("e2-history-before"),
    }
    basis_a, edges_a = g2e.project_integrity_replay_dependency_edges_v01(
        **kwargs,
        edge_projection_bindings=fixture["edge_projection_bindings"],
    )
    basis_b, edges_b = g2e.project_integrity_replay_dependency_edges_v01(
        **kwargs,
        edge_projection_bindings=tuple(
            reversed(fixture["edge_projection_bindings"])
        ),
    )
    assert basis_a == basis_b == fixture["graph_basis"]
    assert edges_a == edges_b == fixture["dependency_edges"]
    assert tuple(edge.canonical_order for edge in edges_a) == (1, 2, 3)
    baseline = fixture["baseline"]
    assert tuple(edge.dependent_artifact_id for edge in edges_a) == (
        baseline[1].artifact_id,
        baseline[2].artifact_id,
        baseline[4].artifact_id,
    )
    source_row = fixture["edge_projection_bindings"][-1]
    with pytest.raises(ValueError, match="^g2e_dependency_edge_duplicate$"):
        g2e.project_integrity_replay_dependency_edges_v01(
            **kwargs,
            edge_projection_bindings=fixture["edge_projection_bindings"]
            + (
                (
                    source_row[0],
                    source_row[1],
                    ("/label",),
                    source_row[3],
                ),
            ),
        )


def test_e2_source_replay_edge_continuity_and_pointer_resolution_v01() -> None:
    fixture = _e2_fixture()
    edges = fixture["dependency_edges"]
    assert all(re.fullmatch(r"[0-9a-f]{64}", edge.source_replay_edge_sha256) for edge in edges)
    assert len({edge.source_replay_edge_sha256 for edge in edges}) == 3
    bindings = list(fixture["edge_projection_bindings"])
    bindings[-1] = (
        bindings[-1][0],
        bindings[-1][1],
        ("/missing",),
        bindings[-1][3],
    )
    with pytest.raises(ValueError, match="^g2e_dependency_source_payload_unavailable$"):
        g2e.project_integrity_replay_dependency_edges_v01(
            manifest=fixture["manifest"],
            replay=fixture["replay"],
            source_artifacts=fixture["baseline"],
            graph_version="v0.1",
            transaction_id="transaction:g2e:e2",
            owning_root_id="root:g2e:e2",
            domain_id="TRAVEL_POLICY_INFORMATION",
            policy_version="policy:v1",
            schema_versions=("v1",),
            source_history_hash=_sha("e2-history-before"),
            edge_projection_bindings=tuple(bindings),
        )
    mutated = replace(edges[0], source_replay_edge_sha256=_sha("forged-replay"))
    mutated = replace(
        mutated,
        edge_id=g2e.rebuild_delta_dependency_edge_identity_v01(mutated),
    )
    with pytest.raises(ValueError, match="^g2e_dependency_replay_edge_mismatch$"):
        g2e.build_dependency_graph_index_v01(
            graph_basis_sha256=fixture["graph_basis"],
            graph_version="v0.1",
            manifest=fixture["manifest"],
            replay=fixture["replay"],
            source_artifacts=fixture["baseline"],
            dependency_edges=(mutated, *edges[1:]),
            transaction_id="transaction:g2e:e2",
            owning_root_id="root:g2e:e2",
            domain_id="TRAVEL_POLICY_INFORMATION",
            policy_version="policy:v1",
            schema_versions=("v1",),
            source_history_hash=_sha("e2-history-before"),
            trace_refs=("trace:g2e:e2:graph",),
        )


def test_e2_graph_builder_exact_nodes_edges_counts_and_acyclicity_v01() -> None:
    fixture = _e2_fixture()
    graph = fixture["graph"]
    manifest = fixture["manifest"]
    assert graph.ordered_node_ids == tuple(item.artifact_id for item in manifest.artifacts)
    assert graph.ordered_edge_ids == tuple(
        edge.edge_id for edge in fixture["dependency_edges"]
    )
    assert graph.node_count == 5 and graph.edge_count == 3
    assert (graph.max_nodes, graph.max_edges, graph.max_hops) == (256, 1024, 32)
    assert graph.acyclic is True
    assert graph.graph_id == g2e.rebuild_dependency_graph_index_identity_v01(graph)
    assert g2e.dependency_graph_index_to_plain_data_v01(graph) == (
        g2e.dependency_graph_index_to_plain_data_v01(_e2_fixture()["graph"])
    )


def test_e2_graph_cycle_unknown_self_duplicate_cross_context_and_bounds_v01() -> None:
    fixture = _e2_fixture()
    baseline = fixture["baseline"]
    base_bindings = fixture["edge_projection_bindings"]
    common = {
        "manifest": fixture["manifest"],
        "replay": fixture["replay"],
        "source_artifacts": baseline,
        "graph_version": "v0.1",
        "transaction_id": "transaction:g2e:e2",
        "owning_root_id": "root:g2e:e2",
        "domain_id": "TRAVEL_POLICY_INFORMATION",
        "policy_version": "policy:v1",
        "schema_versions": ("v1",),
        "source_history_hash": _sha("e2-history-before"),
    }
    cases = (
        (
            base_bindings + (("artifact:unknown", baseline[0].artifact_id, (), "EDGE"),),
            "g2e_dependency_edge_unknown_dependent",
        ),
        (
            base_bindings + ((baseline[1].artifact_id, "artifact:unknown", (), "EDGE"),),
            "g2e_dependency_edge_unknown_source",
        ),
        (
            base_bindings + ((baseline[0].artifact_id, baseline[0].artifact_id, (), "EDGE"),),
            "g2e_dependency_edge_self",
        ),
        (base_bindings + (base_bindings[0],), "g2e_dependency_edge_duplicate"),
        (
            base_bindings
            + (
                (
                    base_bindings[-1][0],
                    base_bindings[-1][1],
                    base_bindings[-1][2],
                    "ALTERNATE_CAUSAL_CLASS",
                ),
            ),
            "g2e_dependency_edge_duplicate",
        ),
        (
            base_bindings
            + ((baseline[0].artifact_id, baseline[1].artifact_id, (), "EDGE"),),
            "g2e_dependency_graph_cycle",
        ),
        (
            base_bindings
            + ((baseline[3].artifact_id, baseline[0].artifact_id, (), "EDGE"),),
            "g2e_dependency_edge_unknown_source",
        ),
    )
    for bindings, reason in cases:
        with pytest.raises(ValueError, match="^" + reason + "$"):
            g2e.project_integrity_replay_dependency_edges_v01(
                **common, edge_projection_bindings=bindings
            )
    with pytest.raises(ValueError, match="^g2e_dependency_edge_cross_root$"):
        g2e.project_integrity_replay_dependency_edges_v01(
            **{**common, "owning_root_id": "root:foreign"},
            edge_projection_bindings=base_bindings,
        )
    graph = fixture["graph"]
    oversized = replace(graph, max_nodes=257)
    oversized = replace(
        oversized,
        graph_id=g2e.rebuild_dependency_graph_index_identity_v01(oversized),
    )
    assert "g2e_dependency_graph_bounds_exceeded" in (
        g2e.validate_dependency_graph_index_v01(oversized).reason_codes
    )


def test_e2_dependency_fingerprint_baseline_observed_and_repeated_bytes_v01() -> None:
    fixture = _e2_fixture()
    assert fixture["before"] != fixture["after"]
    for artifacts, policy, history, expected in (
        (fixture["baseline"], "policy:v1", "e2-history-before", fixture["before"]),
        (fixture["observed"], "policy:v2", "e2-history-after", fixture["after"]),
    ):
        rebuilt = g2e.build_dependency_fingerprint_v01(
            profile=fixture["fingerprint_profile"],
            graph=fixture["graph"],
            dependency_edges=fixture["dependency_edges"],
            source_artifacts=artifacts,
            policy_version=policy,
            schema_versions=("v1",),
            source_history_hash=_sha(history),
        )
        assert rebuilt == expected
        assert g2e.validate_dependency_fingerprint_against_sources_v01(
            expected,
            profile=fixture["fingerprint_profile"],
            graph=fixture["graph"],
            dependency_edges=fixture["dependency_edges"],
            source_artifacts=artifacts,
            policy_version=policy,
            schema_versions=("v1",),
            source_history_hash=_sha(history),
        ).status == "PASS"


def test_e2_dependency_fingerprint_role_history_context_and_swap_rejection_v01() -> None:
    fixture = _e2_fixture()
    profile = replace(fixture["fingerprint_profile"], typed_role="OTHER_ROLE")
    profile = replace(
        profile,
        fingerprint_profile_id=g2e.rebuild_dependency_fingerprint_profile_identity_v01(
            profile
        ),
    )
    role_report = g2e.validate_dependency_fingerprint_against_sources_v01(
        fixture["before"],
        profile=profile,
        graph=fixture["graph"],
        dependency_edges=fixture["dependency_edges"],
        source_artifacts=fixture["baseline"],
        policy_version="policy:v1",
        schema_versions=("v1",),
        source_history_hash=_sha("e2-history-before"),
    )
    assert role_report.reason_codes == ("g2e_dependency_fingerprint_role_collision",)
    history_report = g2e.validate_dependency_fingerprint_against_sources_v01(
        fixture["before"],
        profile=fixture["fingerprint_profile"],
        graph=fixture["graph"],
        dependency_edges=fixture["dependency_edges"],
        source_artifacts=fixture["baseline"],
        policy_version="policy:v1",
        schema_versions=("v1",),
        source_history_hash=_sha("substituted-history"),
    )
    assert history_report.reason_codes == ("g2e_dependency_source_history_mismatch",)
    swapped = g2e.validate_dependency_fingerprint_against_sources_v01(
        fixture["before"],
        profile=fixture["fingerprint_profile"],
        graph=fixture["graph"],
        dependency_edges=fixture["dependency_edges"],
        source_artifacts=fixture["observed"],
        policy_version="policy:v2",
        schema_versions=("v1",),
        source_history_hash=_sha("e2-history-after"),
    )
    assert swapped.reason_codes == ("g2e_dependency_fingerprint_mismatch",)


def test_e2_affected_set_direct_transitive_unaffected_and_changed_partition_v01() -> None:
    fixture = _e2_fixture()
    baseline = fixture["baseline"]
    result = fixture["result"]
    assert result.ordered_changed_node_ids == (baseline[0].artifact_id,)
    assert result.ordered_directly_affected_ids == (
        baseline[1].artifact_id,
        baseline[4].artifact_id,
    )
    assert result.ordered_transitively_affected_ids == (baseline[2].artifact_id,)
    assert result.ordered_affected_ids == (
        baseline[1].artifact_id,
        baseline[4].artifact_id,
        baseline[2].artifact_id,
    )
    assert result.ordered_unaffected_ids == (baseline[3].artifact_id,)
    assert baseline[0].artifact_id not in result.ordered_affected_ids
    report = g2e.validate_affected_set_against_graph_v01(
        result, **_e2_context_kwargs(fixture)
    )
    assert report.status == "PASS"


def test_e2_pointer_non_pruning_and_edge_class_non_pruning_v01() -> None:
    pointer_fixture = _e2_fixture()
    artifact_fixture = _e2_fixture(
        source_pointer=(), source_edge_class="NON_PRUNING_CLASS"
    )
    pointer_result = pointer_fixture["result"]
    artifact_result = artifact_fixture["result"]
    for field_name in (
        "ordered_changed_node_ids",
        "ordered_directly_affected_ids",
        "ordered_transitively_affected_ids",
        "ordered_affected_ids",
        "ordered_unaffected_ids",
    ):
        assert getattr(pointer_result, field_name) == getattr(artifact_result, field_name)
    assert pointer_fixture["dependency_edges"][0].dependency_field_pointers
    assert artifact_fixture["dependency_edges"][0].dependency_field_pointers == ()
    assert artifact_fixture["dependency_edges"][0].edge_class == "NON_PRUNING_CLASS"


def test_e2_affected_set_complete_minimal_independent_validation_v01() -> None:
    fixture = _e2_fixture()
    result = fixture["result"]
    baseline = fixture["baseline"]
    omitted = replace(
        result,
        ordered_directly_affected_ids=(baseline[4].artifact_id,),
        ordered_affected_ids=(baseline[4].artifact_id, baseline[2].artifact_id),
        ordered_unaffected_ids=(baseline[1].artifact_id, baseline[3].artifact_id),
        closure_proof_sha256=_sha("omitted-proof"),
        visited_node_count=3,
    )
    omitted = replace(
        omitted,
        affected_set_id=g2e.rebuild_affected_set_result_identity_v01(omitted),
    )
    assert g2e.validate_affected_set_against_graph_v01(
        omitted, **_e2_context_kwargs(fixture)
    ).reason_codes == ("g2e_affected_reachable_omitted",)
    injected = replace(
        result,
        ordered_directly_affected_ids=(
            baseline[1].artifact_id,
            baseline[3].artifact_id,
            baseline[4].artifact_id,
        ),
        ordered_affected_ids=(
            baseline[1].artifact_id,
            baseline[3].artifact_id,
            baseline[4].artifact_id,
            baseline[2].artifact_id,
        ),
        ordered_unaffected_ids=(),
        closure_proof_sha256=_sha("injected-proof"),
        visited_node_count=5,
    )
    injected = replace(
        injected,
        affected_set_id=g2e.rebuild_affected_set_result_identity_v01(injected),
    )
    assert g2e.validate_affected_set_against_graph_v01(
        injected, **_e2_context_kwargs(fixture)
    ).reason_codes == ("g2e_affected_unrelated_injected",)
    reordered = replace(
        result,
        ordered_directly_affected_ids=tuple(
            reversed(result.ordered_directly_affected_ids)
        ),
        ordered_affected_ids=(
            baseline[4].artifact_id,
            baseline[1].artifact_id,
            baseline[2].artifact_id,
        ),
        closure_proof_sha256=_sha("ordering-proof"),
    )
    reordered = replace(
        reordered,
        affected_set_id=g2e.rebuild_affected_set_result_identity_v01(reordered),
    )
    assert g2e.validate_affected_set_against_graph_v01(
        reordered, **_e2_context_kwargs(fixture)
    ).reason_codes == ("g2e_affected_ordering_invalid",)
    forged_proof = replace(result, closure_proof_sha256=_sha("forged-proof"))
    forged_proof = replace(
        forged_proof,
        affected_set_id=g2e.rebuild_affected_set_result_identity_v01(forged_proof),
    )
    assert g2e.validate_affected_set_against_graph_v01(
        forged_proof, **_e2_context_kwargs(fixture)
    ).reason_codes == ("g2e_affected_proof_invalid",)


def test_e2_carrier_closure_missing_injected_duplicate_and_reordered_v01() -> None:
    fixture = _e2_fixture()
    result = fixture["result"]
    base = _e2_context_kwargs(fixture)
    cases = (
        ({"source_bindings": ()}, "g2e_delta_source_binding_set_mismatch"),
        ({"changed_field_bindings": ()}, "g2e_delta_binding_set_mismatch"),
        (
            {"dependency_edges": tuple(reversed(fixture["dependency_edges"]))},
            "g2e_dependency_edge_set_mismatch",
        ),
        (
            {
                "baseline_source_artifacts": fixture["baseline"]
                + (fixture["baseline"][0],)
            },
            "g2e_delta_source_binding_set_mismatch",
        ),
    )
    for changes, reason in cases:
        report = g2e.validate_affected_set_against_graph_v01(
            result, **{**base, **changes}
        )
        assert report.status == "FAIL_CLOSED"
        assert report.reason_codes == (reason,)

    for delta_changes in (
        {
            "valid_from_utc": "2026-08-12T00:00:00+00:00",
            "valid_to_utc": "2026-08-11T00:00:00+00:00",
        },
        {
            "valid_from_utc": "2026-08-11T00:00:00+00:00",
            "valid_to_utc": "2026-08-11T00:00:00+00:00",
        },
        {"observed_at_utc": "2026-08-10T23:59:59+00:00"},
        {"observed_at_utc": "2026-08-12T00:00:00+00:00"},
    ):
        report = g2e.validate_affected_set_against_graph_v01(
            result,
            **_e2_rewired_context(fixture, delta_changes=delta_changes),
        )
        assert report.reason_codes == ("g2e_delta_time_invalid",)

    source_binding = _e2_reseal(
        fixture["source_binding"],
        valid_from_utc="2026-08-11T00:30:00+00:00",
    )
    assert type(source_binding) is g2e.DeltaSourceBindingV01
    changed_field = _e2_reseal(
        fixture["changed_field"],
        source_binding_id=source_binding.source_binding_id,
    )
    changed_artifact = _e2_reseal(
        fixture["changed_artifact"],
        source_binding_id=source_binding.source_binding_id,
    )
    report = g2e.validate_affected_set_against_graph_v01(
        result,
        **_e2_rewired_context(
            fixture,
            source_bindings=(source_binding,),
            changed_field_bindings=(changed_field,),
            changed_artifact_bindings=(changed_artifact,),
        ),
    )
    assert report.reason_codes == ("g2e_delta_time_invalid",)

    for binding_name, changed_fields, changed_artifacts in (
        (
            "field",
            (
                _e2_reseal(
                    fixture["changed_field"],
                    observed_at_utc="2026-08-11T02:00:00+00:00",
                ),
            ),
            (fixture["changed_artifact"],),
        ),
        (
            "artifact",
            (fixture["changed_field"],),
            (
                _e2_reseal(
                    fixture["changed_artifact"],
                    observed_at_utc="2026-08-11T02:00:00+00:00",
                ),
            ),
        ),
    ):
        assert binding_name in {"field", "artifact"}
        report = g2e.validate_affected_set_against_graph_v01(
            result,
            **_e2_rewired_context(
                fixture,
                changed_field_bindings=changed_fields,
                changed_artifact_bindings=changed_artifacts,
            ),
        )
        assert report.reason_codes == ("g2e_delta_time_invalid",)


def test_e2_affected_bounds_hop_node_edge_and_missing_evidence_fail_closed_v01() -> None:
    fixture = _e2_fixture()
    graph = fixture["graph"]
    positions = {
        artifact_id: index for index, artifact_id in enumerate(graph.ordered_node_ids)
    }
    with pytest.raises(ValueError, match="^g2e_affected_hop_bound_exceeded$"):
        g2e._affected_walk_v01(
            changed_nodes=(fixture["baseline"][0].artifact_id,),
            graph=replace(graph, max_hops=1),
            dependency_edges=fixture["dependency_edges"],
            positions=positions,
        )
    with pytest.raises(ValueError, match="^g2e_affected_node_bound_exceeded$"):
        g2e._affected_walk_v01(
            changed_nodes=(fixture["baseline"][0].artifact_id,),
            graph=replace(graph, max_nodes=1),
            dependency_edges=fixture["dependency_edges"],
            positions=positions,
        )
    with pytest.raises(ValueError, match="^g2e_dependency_edge_set_mismatch$"):
        g2e.compute_affected_set_v01(
            **{
                **_e2_context_kwargs(fixture),
                "dependency_edges": fixture["dependency_edges"][:-1],
            }
        )
    edge = fixture["dependency_edges"][0]
    with pytest.raises(ValueError, match="^g2e_dependency_graph_ordering_invalid$"):
        g2e.build_delta_dependency_edge_v01(
            graph_basis_sha256=edge.graph_basis_sha256,
            graph_version=edge.graph_version,
            dependent_artifact_id=edge.dependent_artifact_id,
            dependency_artifact_id=edge.dependency_artifact_id,
            dependency_field_pointers=edge.dependency_field_pointers,
            edge_class=edge.edge_class,
            transaction_id=edge.transaction_id,
            owning_root_id=edge.owning_root_id,
            domain_id=edge.domain_id,
            canonical_order=1025,
            source_replay_edge_sha256=edge.source_replay_edge_sha256,
            trace_refs=edge.trace_refs,
        )

    field_duplicate = _e2_reseal(
        fixture["changed_field"],
        trace_refs=("trace:g2e:e2:field:duplicate",),
    )
    field_conflict = _e2_reseal(
        fixture["changed_field"],
        change_class="FIELD_VALUE_CONFLICT",
        trace_refs=("trace:g2e:e2:field:conflict",),
    )
    artifact_duplicate = _e2_reseal(
        fixture["changed_artifact"],
        trace_refs=("trace:g2e:e2:artifact:duplicate",),
    )
    artifact_conflict = _e2_reseal(
        fixture["changed_artifact"],
        change_class="ARTIFACT_SUCCESSOR_CONFLICT",
        trace_refs=("trace:g2e:e2:artifact:conflict",),
    )
    duplicate_cases = (
        (
            (
                fixture["changed_field"],
                field_duplicate,
            ),
            (fixture["changed_artifact"],),
            "g2e_delta_duplicate_binding",
        ),
        (
            (
                fixture["changed_field"],
                field_conflict,
            ),
            (fixture["changed_artifact"],),
            "g2e_delta_conflicting_duplicate",
        ),
        (
            (fixture["changed_field"],),
            (
                fixture["changed_artifact"],
                artifact_duplicate,
            ),
            "g2e_delta_duplicate_binding",
        ),
        (
            (fixture["changed_field"],),
            (
                fixture["changed_artifact"],
                artifact_conflict,
            ),
            "g2e_delta_conflicting_duplicate",
        ),
    )
    for changed_fields, changed_artifacts, reason in duplicate_cases:
        report = g2e.validate_affected_set_against_graph_v01(
            fixture["result"],
            **_e2_rewired_context(
                fixture,
                changed_field_bindings=changed_fields,
                changed_artifact_bindings=changed_artifacts,
            ),
        )
        assert report.reason_codes == (reason,)


def test_e2_first_four_abi_artifact_instances_and_t01_t02_chain_v01() -> None:
    fixture = _e2_fixture()
    chain_a = _e2_artifact_chain(fixture)
    chain_b = _e2_artifact_chain(fixture)
    proposed, validated, graph_artifact, affected_artifact, t01, t02, _, _ = chain_a
    artifacts = (proposed, validated, graph_artifact, affected_artifact)
    assert all(type(item) is g2e.KernelArtifactV01 for item in artifacts)
    assert all(validate_kernel_artifact_v01(item) == () for item in artifacts)
    assert tuple(item.artifact_type for item in artifacts) == (
        "ContinuousDeltaSource",
        "ContinuousDeltaSource",
        "DependencyGraphIndex",
        "AffectedSetResult",
    )
    assert tuple(item.lifecycle_state for item in artifacts) == (
        "PROPOSED",
        "VALIDATED",
        "VALIDATED",
        "VALIDATED",
    )
    proposed_plain = kernel_artifact_to_plain_dict_v01(proposed)
    validated_plain = kernel_artifact_to_plain_dict_v01(validated)
    graph_plain = kernel_artifact_to_plain_dict_v01(graph_artifact)
    affected_plain = kernel_artifact_to_plain_dict_v01(affected_artifact)
    delta_plain = g2e.world_state_delta_to_plain_data_v01(fixture["delta"])
    graph_source_plain = g2e.dependency_graph_index_to_plain_data_v01(
        fixture["graph"]
    )
    affected_source_plain = g2e.affected_set_result_to_plain_data_v01(
        fixture["result"]
    )
    expected_delta_payload_order = tuple(
        key for key in delta_plain if key not in {"transaction_id", "trace_refs"}
    )
    expected_graph_payload_order = tuple(
        key
        for key in graph_source_plain
        if key not in {"transaction_id", "trace_refs"}
    )
    expected_affected_payload_order = tuple(
        key for key in affected_source_plain if key != "trace_refs"
    )
    proposed_projection = g2e._project_g2e_abi_payload_v01(
        profile_name="delta_source_proposed",
        complete_payload=delta_plain,
    )
    validated_projection = g2e._project_g2e_abi_payload_v01(
        profile_name="delta_source_validated",
        complete_payload=delta_plain,
    )
    graph_projection = g2e._project_g2e_abi_payload_v01(
        profile_name="dependency_graph_validated",
        complete_payload=graph_source_plain,
    )
    affected_projection = g2e._project_g2e_abi_payload_v01(
        profile_name="affected_set_validated",
        complete_payload=affected_source_plain,
    )
    assert tuple(proposed_projection) == expected_delta_payload_order
    assert tuple(validated_projection) == expected_delta_payload_order
    assert tuple(graph_projection) == expected_graph_payload_order
    assert tuple(affected_projection) == expected_affected_payload_order
    assert proposed_plain["payload"] == proposed_projection
    assert validated_plain["payload"] == validated_projection
    assert graph_plain["payload"] == graph_projection
    assert affected_plain["payload"] == affected_projection
    assert canonical_json_bytes_v01(proposed_plain["payload"]) == (
        canonical_json_bytes_v01(validated_plain["payload"])
    )
    reserved_payload_names = {
        field.name for field in fields(g2e.KernelArtifactV01)
    }
    for plain in (
        proposed_plain,
        validated_plain,
        graph_plain,
        affected_plain,
    ):
        assert not reserved_payload_names.intersection(plain["payload"])
    delta = fixture["delta"]
    graph = fixture["graph"]
    result = fixture["result"]
    assert proposed.transaction_id == delta.transaction_id
    assert validated.transaction_id == delta.transaction_id
    assert graph_artifact.transaction_id == graph.transaction_id
    assert affected_artifact.transaction_id == delta.transaction_id
    assert proposed.trace_refs == delta.trace_refs + delta.ordered_source_binding_ids
    assert validated.trace_refs == (
        proposed.artifact_id,
        t01.decision_id,
        *delta.trace_refs,
        *delta.ordered_source_binding_ids,
    )
    assert graph_artifact.trace_refs == graph.trace_refs + (
        graph.source_manifest_id,
        graph.source_replay_id,
    )
    assert affected_artifact.trace_refs == result.trace_refs + (
        t02.decision_id,
        result.delta_id,
        result.graph_id,
    )
    assert proposed.artifact_id != validated.artifact_id
    assert tuple(item.artifact_id for item in artifacts) == tuple(
        item.artifact_id for item in chain_b[:4]
    )
    assert tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in artifacts
    ) == tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in chain_b[:4]
    )

    route, g2d_report = chain_a[6:]
    baseline = fixture["baseline"]
    observed = fixture["observed"]
    for changes in (
        {"transaction_id": "transaction:g2e:e2:mutated"},
        {"trace_refs": ("trace:g2e:e2:delta:mutated",)},
    ):
        mutated_delta = _e2_reseal(delta, **changes)
        assert type(mutated_delta) is g2e.WorldStateDeltaV01
        rebuilt_projection = g2e._project_delta_source_proposed_artifact_v01(
            delta=mutated_delta,
            baseline_route_artifact=route,
            baseline_g2d_report_artifact=g2d_report,
            baseline_source_artifacts=(baseline[0],),
            observed_source_artifacts=(observed[0],),
        )
        assert validate_kernel_artifact_v01(rebuilt_projection) == ()
        assert rebuilt_projection != proposed
        assert rebuilt_projection.artifact_id != proposed.artifact_id
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t01,
        registry=registry,
        source_artifact=proposed,
        target_artifact=validated,
    ) == ()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t02,
        registry=registry,
        source_artifact=validated,
        target_artifact=affected_artifact,
    ) == ()


def test_e2_no_e3_source_context_invalidation_execution_or_facade_v01() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }
    forbidden = {
        "build_selective_recomputation_plan_from_affected_set_v01",
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
    }
    assert forbidden.issubset(public_functions)
    assert kernel.DeltaDependencyEdgeV01 is g2e.DeltaDependencyEdgeV01
    top_level_functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    e2_called_names: set[str] = set()
    for function_name in QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS:
        for node in ast.walk(top_level_functions[function_name]):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    e2_called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    e2_called_names.add(node.func.attr)
    assert not e2_called_names.intersection(E3_PUBLIC_FUNCTIONS)
    defined_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    called_names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called_names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            called_names.add(node.func.attr)
    assert {
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
    }.issubset(defined_names)
    assert "_d4_run_runtime_v02" not in defined_names
    assert "_d4_run_runtime_v02" not in called_names
    imported_modules = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    imported_modules.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not any(
        "demo" in module_name or "runner" in module_name
        for module_name in imported_modules
    )
    assert not called_names.intersection(
        {"provider_call", "model_call", "network_call", "connector_call"}
    )


def _e3_structural_record() -> g2e.ArtifactInvalidationRecordV01:
    return g2e.build_artifact_invalidation_record_v01(
        affected_set_id="g2e_affected_set_result_v01:" + _sha("e3-affected"),
        artifact_id="artifact:g2e:e3:structural",
        artifact_type="SemanticEvidence",
        invalidation_reason_class="SOURCE_FIELD_CHANGED",
        triggering_delta_id="g2e_world_state_delta_v01:" + _sha("e3-delta"),
        triggering_binding_ids=("g2e_changed_field_binding_v01:" + _sha("e3-field"),),
        predecessor_artifact_id="artifact:g2e:e3:structural",
        g2a_packet_relation="NOT_APPLICABLE",
        g2b_reuse_relation="NOT_APPLICABLE",
        g2c_route_relation="ROUTE_CURRENT",
        root_review_required=False,
        trace_refs=("trace:g2e:e3:structural",),
    )


def _e3_structural_report() -> g2e.InvalidationReportV01:
    record = _e3_structural_record()
    return g2e.build_invalidation_report_v01(
        affected_set_id=record.affected_set_id,
        records=(record,),
        ordered_unresolved_artifact_ids=(),
    )


def _e3_structural_proof() -> g2e.PreservationProofV01:
    artifact_sha = _sha("e3-preserved-artifact")
    payload_sha = _sha("e3-preserved-payload")
    return g2e.build_preservation_proof_v01(
        baseline_graph_id="g2e_dependency_graph_index_v01:" + _sha("e3-graph"),
        affected_set_id="g2e_affected_set_result_v01:" + _sha("e3-affected"),
        ordered_preserved_artifact_ids=("artifact:g2e:e3:preserved",),
        ordered_before_artifact_sha256=(artifact_sha,),
        ordered_after_artifact_sha256=(artifact_sha,),
        ordered_before_payload_sha256=(payload_sha,),
        ordered_after_payload_sha256=(payload_sha,),
        ordered_before_identity_ids=("artifact:g2e:e3:preserved",),
        ordered_after_identity_ids=("artifact:g2e:e3:preserved",),
    )


def _e3_transition_decision(
    registry: transition.TransitionRegistryV01,
    rule_id: str,
) -> transition.TransitionDecisionV01:
    rule = next(item for item in registry.rules if item.rule_id == rule_id)
    return transition.lookup_transition_v01(
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


def _e3_artifact_chain(family: dict[str, object]) -> dict[str, object]:
    delta = family["delta"]
    graph = family["graph"]
    affected = family["affected"]
    baseline = family["baseline"]
    observed = family["observed"]
    context = family["context"]
    assert type(delta) is g2e.WorldStateDeltaV01
    assert type(graph) is g2e.DependencyGraphIndexV01
    assert type(affected) is g2e.AffectedSetResultV01
    assert type(context) is g2e.ContinuousDeltaSourceContextV01
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    proposed = g2e._project_delta_source_proposed_artifact_v01(
        delta=delta,
        baseline_route_artifact=context.baseline_g2c_route_eligibility_artifact,
        baseline_g2d_report_artifact=context.baseline_g2d_execution_bundle.report_artifact,
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
    )
    t01 = _e3_transition_decision(registry, "g2e_t01_delta_validate")
    validated = g2e._project_delta_source_validated_artifact_v01(
        delta=delta,
        proposed_source_artifact=proposed,
        t01_decision_id=t01.decision_id,
        baseline_route_artifact=context.baseline_g2c_route_eligibility_artifact,
        baseline_g2d_report_artifact=context.baseline_g2d_execution_bundle.report_artifact,
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
    )
    graph_artifact = g2e._project_dependency_graph_artifact_v01(
        graph=graph,
        delta=delta,
        validated_delta_source_artifact=validated,
        baseline_route_artifact=context.baseline_g2c_route_eligibility_artifact,
        baseline_source_artifacts=baseline,
    )
    t02 = _e3_transition_decision(registry, "g2e_t02_affected_set_derive")
    affected_artifact = g2e._project_affected_set_artifact_v01(
        affected_result=affected,
        delta=delta,
        validated_delta_source_artifact=validated,
        dependency_graph_artifact=graph_artifact,
        baseline_route_artifact=context.baseline_g2c_route_eligibility_artifact,
        t02_decision_id=t02.decision_id,
    )
    return {
        "registry": registry,
        "proposed": proposed,
        "validated": validated,
        "graph": graph_artifact,
        "affected": affected_artifact,
        "t01": t01,
        "t02": t02,
    }


def _e3_invalidation_kwargs(family: dict[str, object]) -> dict[str, object]:
    return {
        "affected_set": family["affected"],
        "delta": family["delta"],
        "source_context": family["context"],
        "source_bindings": (family["source_binding"],),
        "changed_field_bindings": (family["changed_field"],),
        "changed_artifact_bindings": (family["changed_artifact"],),
        "dependency_edges": family["dependency_edges"],
        "dependency_graph": family["graph"],
    }


def test_e3_exact_public_surface_and_slice_boundary_v01() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    assert public_functions[:45] == QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert public_functions[45:62] == E3_PUBLIC_FUNCTIONS
    assert public_functions[62:] == E4_PUBLIC_FUNCTIONS
    assert len(public_functions) == 89
    assert g2e.__all__[:65] == TYPE_NAMES + QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert g2e.__all__[65:82] == E3_PUBLIC_FUNCTIONS
    assert g2e.__all__[82:] == E4_PUBLIC_FUNCTIONS
    assert len(g2e.__all__) == 109
    assert len(g2e.G2E_INVALIDATION_REASON_CLASSES_V01) == 10
    assert g2e.G2E_G2A_PACKET_RELATIONS_V01 == (
        "NOT_APPLICABLE",
        "PACKET_ROOT_REVIEW_REQUIRED",
    )
    assert g2e.G2E_G2B_REUSE_RELATIONS_V01 == (
        "NOT_APPLICABLE",
        "REUSE_CERTIFICATE_STALE",
    )
    assert g2e.G2E_G2C_ROUTE_RELATIONS_V01 == (
        "ROUTE_CURRENT",
        "ROUTE_REVALIDATION_REQUIRED",
    )
    assert all(
        hasattr(g2e, name)
        for name in (
            "build_selective_recomputation_plan_from_affected_set_v01",
            "execute_selective_recomputation_v01",
            "run_continuous_delta_runtime_v01",
        )
    )
    g2b = _e3_g2b_family()
    source_family = _e3_g2d_source_family(g2b)
    source = source_family["source"]
    assert type(source) is g2d.FractalRuntimeSourceContextV02
    assert g2d.validate_fractal_runtime_source_context_v02(source).status == "PASS"
    source_plain = _e3_public_plain(source)
    assert canonical_json_bytes_v01(source_plain) == canonical_json_bytes_v01(
        _e3_public_plain(source)
    )
    assert _e3_observation_digest(
        "G2E3_TEST_ACTUAL_SOURCE_CONTEXT", source
    ) == _e3_observation_digest("G2E3_TEST_ACTUAL_SOURCE_CONTEXT", source)

    g2c_registry, g2d_registry, default_registry = _e3_transition_profiles()
    assert len(
        {
            g2c_registry.registry_id,
            g2d_registry.registry_id,
            default_registry.registry_id,
        }
    ) == 3
    assert source.transition_registry == g2c_registry
    assert transition.validate_execution_mode_transition_registry_profile_v01(
        g2c_registry
    ) == ()
    assert transition.validate_fractal_runtime_transition_registry_profile_v02(
        g2d_registry
    ) == ()
    g2c_registry_plain = (
        transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
            g2c_registry
        )
    )
    g2d_registry_plain = (
        transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
            g2d_registry
        )
    )
    assert _e3_transition_registry_plain(g2c_registry) == g2c_registry_plain
    assert _e3_transition_registry_plain(g2d_registry) == g2d_registry_plain
    assert len(g2c_registry.rules) == 6
    assert len(g2d_registry.rules) == 17
    assert tuple(rule.rule_id for rule in g2c_registry.rules) == (
        "g2c_transition:proposal_to_root_review:v01",
        "g2c_transition:root_accept_to_route:v01",
        "g2c_transition:root_narrow_to_route:v01",
        "g2c_transition:root_reject_record:v01",
        "g2c_transition:root_block_record:v01",
        "g2c_transition:root_needs_user_record:v01",
    )
    assert tuple(rule.rule_id for rule in g2d_registry.rules) == (
        "g2d_t01_route_eligibility_to_topology",
        "g2d_t02_topology_to_pending",
        "g2d_t03_pending_backpressure_defer",
        "g2d_t04_pending_to_ready",
        "g2d_t05_ready_to_running",
        "g2d_t06_running_to_validating",
        "g2d_t07_validating_to_revise",
        "g2d_t08_validating_to_completed",
        "g2d_t09_validating_to_degraded",
        "g2d_t10_validating_to_blocked",
        "g2d_t11_validating_to_needs_user",
        "g2d_t12_validating_to_deadend",
        "g2d_t13_completed_to_parent_return",
        "g2d_t14_degraded_to_parent_return",
        "g2d_t15_blocked_to_parent_return",
        "g2d_t16_needs_user_to_parent_return",
        "g2d_t17_deadend_to_parent_return",
    )
    for registry, registry_plain in (
        (g2c_registry, g2c_registry_plain),
        (g2d_registry, g2d_registry_plain),
    ):
        expected_rule_plain = tuple(
            {
                "rule_id": rule.rule_id,
                "abi_major_version": rule.abi_major_version,
                "source_artifact_type": rule.source_artifact_type,
                "source_lifecycle_state": rule.source_lifecycle_state,
                "actor_role": rule.actor_role,
                "attempted_effect": rule.attempted_effect,
                "target_artifact_type": rule.target_artifact_type,
                "required_guards": list(rule.required_guards),
                "decision": rule.decision,
                "reason_code": rule.reason_code,
                "root_commit_required": rule.root_commit_required,
            }
            for rule in registry.rules
        )
        assert tuple(registry_plain["rules"]) == expected_rule_plain
    assert canonical_json_bytes_v01(g2c_registry_plain) == canonical_json_bytes_v01(
        transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
            g2c_registry
        )
    )
    assert canonical_json_bytes_v01(g2d_registry_plain) == canonical_json_bytes_v01(
        transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
            g2d_registry
        )
    )
    actual_g2c_decisions = (
        source.proposal_transition_decision,
        source.root_route_transition_decision,
    )
    for decision in actual_g2c_decisions:
        assert transition.validate_execution_mode_transition_decision_v01(
            registry=g2c_registry,
            decision=decision,
        ) == ()
        assert transition.rebuild_execution_mode_transition_decision_identity_v01(
            decision
        ) == decision.decision_id
        expected = transition.execution_mode_transition_decision_to_plain_dict_v01(
            registry=g2c_registry,
            decision=decision,
        )
        assert _e3_transition_decision_plain(decision) == expected
        assert canonical_json_bytes_v01(expected) == canonical_json_bytes_v01(
            _e3_transition_decision_plain(decision)
        )

    g2d_lookup_groups: dict[tuple[object, ...], list[str]] = {}
    for rule in g2d_registry.rules:
        lookup_key = (
            rule.abi_major_version,
            rule.source_artifact_type,
            rule.source_lifecycle_state,
            rule.actor_role,
            rule.attempted_effect,
            rule.target_artifact_type,
        )
        g2d_lookup_groups.setdefault(lookup_key, []).append(rule.rule_id)
    duplicate_lookup_groups = tuple(
        tuple(rule_ids)
        for rule_ids in g2d_lookup_groups.values()
        if len(rule_ids) > 1
    )
    assert duplicate_lookup_groups == (
        (
            "g2d_t13_completed_to_parent_return",
            "g2d_t14_degraded_to_parent_return",
            "g2d_t16_needs_user_to_parent_return",
            "g2d_t17_deadend_to_parent_return",
        ),
    )
    duplicate_rules = tuple(
        rule
        for rule in g2d_registry.rules
        if rule.rule_id in duplicate_lookup_groups[0]
    )
    assert len({rule.required_guards for rule in duplicate_rules}) == 4

    g2c_seams = _e3_g2c_serialization_seams()
    assert tuple(g2c_seams) == g2c.SERIALIZED_G2C_TYPES_V01
    router_input = source.router_input
    proposal = source.proposal
    snapshot = router_input.local_routing_snapshot
    mapped_g2c_objects = (
        router_input.bsep_binding,
        router_input.replay_binding,
        router_input.g2a_binding,
        router_input.g2b_binding,
        snapshot.mode_profiles[0],
        snapshot,
        router_input,
        proposal.ordered_feasibility_rows[0],
        proposal,
        source.review_input,
        source.decision,
        source_family["route_report"],
    )
    assert tuple(type(value) for value in mapped_g2c_objects) == (
        g2c.SERIALIZED_G2C_TYPES_V01
    )
    identity_fields = {
        type_name: identity_field
        for type_name, identity_field, _domain, _prefix in (
            g2c.G2C_IDENTITY_PROFILES_V01
        )
    }
    for value in mapped_g2c_objects:
        serializer, rebuilder = g2c_seams[type(value)]
        plain = serializer(value)  # type: ignore[operator]
        assert _e3_public_plain(value) == plain
        assert rebuilder(value) == getattr(  # type: ignore[operator]
            value, identity_fields[type(value).__name__]
        )
        assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
            serializer(value)  # type: ignore[operator]
        )
    public_plain_source = inspect.getsource(_e3_public_plain)
    assert public_plain_source.index("_e3_g2c_serialization_seams") < (
        public_plain_source.index("if is_dataclass(value)")
    )

    default_rule = default_registry.rules[0]
    foreign_decision = transition.lookup_transition_v01(
        registry=default_registry,
        abi_major_version=default_rule.abi_major_version,
        source_artifact_type=default_rule.source_artifact_type,
        source_lifecycle_state=default_rule.source_lifecycle_state,
        actor_role=default_rule.actor_role,
        attempted_effect=default_rule.attempted_effect,
        target_artifact_type=default_rule.target_artifact_type,
        satisfied_guards=default_rule.required_guards,
        root_commit_present=default_rule.root_commit_required,
    )
    assert foreign_decision.matched and foreign_decision.rule_id == default_rule.rule_id
    with pytest.raises(ValueError, match="foreign transition registry"):
        _e3_transition_registry_plain(default_registry)
    with pytest.raises(ValueError, match="foreign transition decision"):
        _e3_transition_decision_plain(foreign_decision)
    decision_observer_tree = ast.parse(
        inspect.getsource(_e3_transition_decision_plain)
    )
    decision_serializer_calls = {
        node.func.attr
        for node in ast.walk(decision_observer_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "transition_decision_to_plain_dict_v01" not in decision_serializer_calls
    registry_observer_tree = ast.parse(
        inspect.getsource(_e3_transition_registry_plain)
    )
    registry_serializer_calls = {
        node.func.attr
        for node in ast.walk(registry_observer_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "transition_registry_to_plain_dict_v01" not in registry_serializer_calls

    assert _e3_observation_members(()) == ((None, ()),)
    assert _e3_observation_members(("first", "second")) == (
        (0, "first"),
        (1, "second"),
    )
    assert _e3_observation_members("scalar") == ((None, "scalar"),)
    empty_tuple_plain = _e3_public_plain(())
    assert empty_tuple_plain == []
    assert canonical_json_bytes_v01(empty_tuple_plain) == canonical_json_bytes_v01([])
    assert _e3_observation_digest("G2E3_TEST_EMPTY_TUPLE", ()) == (
        _e3_observation_digest("G2E3_TEST_EMPTY_TUPLE", ())
    )

    nested_observation = {
        "tuple": (0.66, [True, 1, 1.0]),
        "mapping": {"positive_zero": 0.0, "negative_zero": -0.0},
    }
    assert _e3_public_plain(nested_observation) == {
        "tuple": [0.66, [True, 1, 1.0]],
        "mapping": {"positive_zero": 0.0, "negative_zero": -0.0},
    }
    nested_digest = _e3_observation_digest(
        "G2E3_TEST_NESTED_FINITE_FLOAT", nested_observation
    )
    assert nested_digest == _e3_observation_digest(
        "G2E3_TEST_NESTED_FINITE_FLOAT", nested_observation
    )
    primitive_observations = tuple(
        (
            type(value).__name__,
            canonical_json_bytes_v01(_e3_public_plain(value)),
            _e3_observation_digest("G2E3_TEST_PRIMITIVE", value),
        )
        for value in (True, 1, 1.0)
    )
    assert tuple(row[0] for row in primitive_observations) == (
        "bool",
        "int",
        "float",
    )
    assert len({row[1] for row in primitive_observations}) == 3
    assert len({row[2] for row in primitive_observations}) == 3
    for zero in (0.0, -0.0):
        assert canonical_json_bytes_v01(_e3_public_plain(zero)) == (
            canonical_json_bytes_v01(zero)
        )
        assert _e3_observation_digest("G2E3_TEST_ZERO", zero) == (
            _e3_observation_digest("G2E3_TEST_ZERO", zero)
        )
    assert (
        _e3_observation_digest("G2E3_TEST_ZERO", 0.0)
        == _e3_observation_digest("G2E3_TEST_ZERO", -0.0)
    ) == (
        canonical_json_bytes_v01(0.0) == canonical_json_bytes_v01(-0.0)
    )
    for non_finite in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError, match="non-finite public observation"):
            _e3_public_plain({"nested": (non_finite,)})
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    replay_result_attributes = tuple(
        node.attr
        for node in ast.walk(test_tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "integrity_replay"
    )
    assert "replay_status" in replay_result_attributes
    assert "status" not in replay_result_attributes
    fixture_source = inspect.getsource(e3_baseline_fixture)
    for marker in (
        "G2E3_FOCUSED_BASELINE_PUBLIC_CALL_COMPLETED=1",
        "G2E3_ACCEPTANCE_BASELINE_PUBLIC_CALL_COMPLETED=1",
        "G2E3_FOCUSED_BASELINE_CALL_OBSERVED=1",
        "G2E3_ACCEPTANCE_BASELINE_CALL_OBSERVED=1",
    ):
        assert fixture_source.count(marker) == 1


def test_e3_three_quartets_identity_plain_data_and_schema_v01() -> None:
    values = (
        _e3_structural_record(),
        _e3_structural_report(),
        _e3_structural_proof(),
    )
    serializers = (
        g2e.artifact_invalidation_record_to_plain_data_v01,
        g2e.invalidation_report_to_plain_data_v01,
        g2e.preservation_proof_to_plain_data_v01,
    )
    rebuilders = (
        g2e.rebuild_artifact_invalidation_record_identity_v01,
        g2e.rebuild_invalidation_report_identity_v01,
        g2e.rebuild_preservation_proof_identity_v01,
    )
    validators = (
        g2e.validate_artifact_invalidation_record_v01,
        g2e.validate_invalidation_report_v01,
        g2e.validate_preservation_proof_v01,
    )
    identity_fields = (
        "invalidation_record_id",
        "invalidation_report_id",
        "preservation_proof_id",
    )
    definitions = _schema()["$defs"]
    for value, serializer, rebuilder, validator, identity_field in zip(
        values, serializers, rebuilders, validators, identity_fields, strict=True
    ):
        plain = serializer(value)
        assert validator(value).status == "PASS"
        assert rebuilder(value) == getattr(value, identity_field)
        assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
            serializer(value)
        )
        Draft202012Validator(definitions[type(value).__name__]).validate(plain)


def test_e3_invalidation_record_structural_mutation_matrix_v01() -> None:
    record = _e3_structural_record()
    matrix = (
        (replace(record, invalidation_reason_class="UNKNOWN"), "g2e_invalidation_reason_invalid"),
        (replace(record, deleted=True), "g2e_invalidation_deletion_forbidden"),
        (replace(record, historical_artifact_preserved=False), "g2e_invalidation_history_mutation"),
        (replace(record, predecessor_artifact_id="artifact:other"), "g2e_invalidation_predecessor_mismatch"),
        (replace(record, superseded_by_artifact_id="artifact:successor"), "g2e_invalidation_supersession_mismatch"),
        (replace(record, current_eligible_after=True), "g2e_invalidation_record_invalid"),
    )
    for candidate, reason in matrix:
        assert reason in g2e.validate_artifact_invalidation_record_v01(
            candidate
        ).reason_codes


def test_e3_invalidation_report_structural_mutation_matrix_v01() -> None:
    report = _e3_structural_report()
    assert g2e.validate_invalidation_report_v01(report).status == "PASS"
    matrix = (
        replace(report, ordered_invalidation_record_ids=()),
        replace(report, ordered_historical_artifact_ids=("artifact:other",)),
        replace(report, report_status="FAIL_CLOSED"),
        replace(report, authority_created=True),
        replace(report, ordered_invalidated_artifact_ids=report.ordered_invalidated_artifact_ids * 2),
    )
    for candidate in matrix:
        assert "g2e_invalidation_record_invalid" in (
            g2e.validate_invalidation_report_v01(candidate).reason_codes
        )


def test_e3_preservation_proof_structural_mutation_matrix_v01() -> None:
    proof = _e3_structural_proof()
    assert g2e.validate_preservation_proof_v01(proof).status == "PASS"
    changed = g2e.build_preservation_proof_v01(
        baseline_graph_id=proof.baseline_graph_id,
        affected_set_id=proof.affected_set_id,
        ordered_preserved_artifact_ids=proof.ordered_preserved_artifact_ids,
        ordered_before_artifact_sha256=proof.ordered_before_artifact_sha256,
        ordered_after_artifact_sha256=(_sha("changed-artifact"),),
        ordered_before_payload_sha256=proof.ordered_before_payload_sha256,
        ordered_after_payload_sha256=proof.ordered_after_payload_sha256,
        ordered_before_identity_ids=proof.ordered_before_identity_ids,
        ordered_after_identity_ids=proof.ordered_after_identity_ids,
    )
    assert changed.status == "FAIL_CLOSED"
    assert changed.reason_codes == ("g2e_preserved_artifact_changed",)
    matrix = (
        (replace(proof, before_cache_state_sha256=_sha("cache")), "g2e_preservation_cache_mutation"),
        (replace(proof, mutable_global_write_count=1), "g2e_preservation_cache_mutation"),
        (replace(proof, object_identity_used_as_proof=True), "g2e_preservation_proof_invalid"),
        (replace(proof, proof_sha256=_sha("proof")), "g2e_preservation_proof_invalid"),
    )
    for candidate, reason in matrix:
        assert reason in g2e.validate_preservation_proof_v01(candidate).reason_codes


def test_e3_source_context_exact_carriers_and_public_validation_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    context = family["context"]
    assert type(context) is g2e.ContinuousDeltaSourceContextV01
    report = g2e.validate_continuous_delta_source_context_v01(context)
    assert report.status == "PASS"
    assert context.g2b_writeback_evidence is None
    assert context.post_vv_profile is None
    assert context.gt_profile is None
    for field_name in (
        "g2b_writeback_evidence",
        "post_vv_profile",
        "gt_profile",
    ):
        rejected = g2e.validate_continuous_delta_source_context_v01(
            replace(context, **{field_name: "non-none-sentinel"})
        )
        assert rejected.reason_codes == ("g2e_delta_source_unvalidated",)


def test_e3_source_context_manifest_replay_source_pair_and_baseline_report_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    context = family["context"]
    baseline = family["baseline"]
    observed = family["observed"]
    assert tuple(ref.artifact_id for ref in context.integrity_manifest.artifacts) == tuple(
        artifact.artifact_id for artifact in baseline
    )
    assert context.integrity_replay.replay_status == "PASS"
    assert all(artifact.schema_version == "v1" for artifact in baseline)
    dedicated_ids = {
        context.g2a_packet.packet_identity.packet_id,
        context.g2b_reuse_certificate.certificate_id,
        context.baseline_g2c_route_eligibility_artifact.artifact_id,
        context.baseline_g2d_execution_bundle.report_artifact.artifact_id,
    }
    assert dedicated_ids.isdisjoint(
        artifact.artifact_id for artifact in baseline
    )
    assert len({artifact.artifact_id for artifact in baseline}) == len(baseline)
    assert observed[0].artifact_id != baseline[0].artifact_id
    assert baseline[0].artifact_id in observed[0].parent_refs
    assert tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in observed[1:]
    ) == tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in baseline[1:]
    )
    reordered = replace(context, baseline_source_artifacts=tuple(reversed(baseline)))
    assert g2e.validate_continuous_delta_source_context_v01(reordered).reason_codes == (
        "g2e_delta_source_unvalidated",
    )
    stale_report_id = "frreport_v02:" + _sha("stale")
    stale_source_binding = _e2_reseal(
        family["source_binding"], baseline_report_id=stale_report_id
    )
    assert type(stale_source_binding) is g2e.DeltaSourceBindingV01
    stale_changed_field = _e2_reseal(
        family["changed_field"],
        source_binding_id=stale_source_binding.source_binding_id,
    )
    assert type(stale_changed_field) is g2e.ChangedFieldBindingV01
    stale_changed_artifact = _e2_reseal(
        family["changed_artifact"],
        source_binding_id=stale_source_binding.source_binding_id,
    )
    assert type(stale_changed_artifact) is g2e.ChangedArtifactBindingV01
    stale_delta = _e2_reseal(
        family["delta"],
        baseline_report_id=stale_report_id,
        ordered_source_binding_ids=(stale_source_binding.source_binding_id,),
        ordered_changed_field_binding_ids=(
            stale_changed_field.changed_field_binding_id,
        ),
        ordered_changed_artifact_binding_ids=(
            stale_changed_artifact.changed_artifact_binding_id,
        ),
    )
    assert type(stale_delta) is g2e.WorldStateDeltaV01
    stale_request = g2e.build_affected_set_request_v01(
        delta=stale_delta,
        graph=family["graph"],
        trace_refs=family["request"].trace_refs,
    )
    stale_affected = g2e.compute_affected_set_v01(
        request=stale_request,
        delta=stale_delta,
        graph=family["graph"],
        source_bindings=(stale_source_binding,),
        changed_field_bindings=(stale_changed_field,),
        changed_artifact_bindings=(stale_changed_artifact,),
        dependency_edges=family["dependency_edges"],
        baseline_source_artifacts=baseline,
        observed_source_artifacts=observed,
    )
    assert all(
        validation.status == "PASS"
        for validation in (
            g2e.validate_delta_source_binding_v01(stale_source_binding),
            g2e.validate_changed_field_binding_v01(stale_changed_field),
            g2e.validate_changed_artifact_binding_v01(stale_changed_artifact),
            g2e.validate_world_state_delta_v01(stale_delta),
            g2e.validate_affected_set_request_v01(stale_request),
            g2e.validate_affected_set_against_graph_v01(
                stale_affected,
                request=stale_request,
                delta=stale_delta,
                graph=family["graph"],
                source_bindings=(stale_source_binding,),
                changed_field_bindings=(stale_changed_field,),
                changed_artifact_bindings=(stale_changed_artifact,),
                dependency_edges=family["dependency_edges"],
                baseline_source_artifacts=baseline,
                observed_source_artifacts=observed,
            ),
        )
    )
    assert stale_affected.affected_request_id == stale_request.affected_request_id
    with pytest.raises(ValueError, match="^g2e_delta_baseline_stale$"):
        g2e.derive_invalidation_report_v01(
            affected_set=stale_affected,
            delta=stale_delta,
            source_context=context,
            source_bindings=(stale_source_binding,),
            changed_field_bindings=(stale_changed_field,),
            changed_artifact_bindings=(stale_changed_artifact,),
            dependency_edges=family["dependency_edges"],
            dependency_graph=family["graph"],
        )


def test_e3_source_context_trusted_currentness_and_future_observation_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    context = family["context"]
    snapshot = context.baseline_g2d_execution_bundle.source_context.router_input.local_routing_snapshot
    assert snapshot.evaluation_time_epoch_seconds == _E3_TIME
    assert g2e.validate_continuous_delta_source_context_v01(context).status == "PASS"
    future_envelope = {
        **_e3_time_envelope(),
        "et_observed_at": _E3_VALID_TO_UTC,
        "pt_created_at": _E3_VALID_TO_UTC,
    }
    future = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e3:source:future",
        transaction_id=context.baseline_source_artifacts[0].transaction_id,
        payload={"hold_status": "NEW", "role": "changed-source"},
        parent_refs=(context.baseline_source_artifacts[0].artifact_id,),
        time_envelope=future_envelope,
    )
    candidate = replace(
        context,
        observed_source_artifacts=(future, *context.observed_source_artifacts[1:]),
    )
    assert g2e.validate_continuous_delta_source_context_v01(candidate).reason_codes == (
        "g2e_delta_future_observation",
    )


def test_e3_source_context_route_topology_same_call_boundary_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    context = family["context"]
    replacement_route = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e3:route:substituted",
        transaction_id=context.baseline_g2c_route_eligibility_artifact.transaction_id,
        payload={"role": "substituted-route"},
    )
    route_report = g2e.validate_continuous_delta_source_context_v01(
        replace(context, baseline_g2c_route_eligibility_artifact=replacement_route)
    )
    assert route_report.reason_codes == ("g2e_route_revalidation_required",)
    runtime_source = MODULE_PATH.read_text(encoding="utf-8")
    assert runtime_source.index('return "g2e_route_revalidation_required"') < (
        runtime_source.index('return "g2e_topology_binding_mismatch"')
    )


def test_e3_actual_binding_invalidation_reason_and_order_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    records, report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    assert tuple(record.artifact_id for record in records) == family[
        "affected"
    ].ordered_affected_ids
    assert all(
        record.triggering_binding_ids
        == (
            family["changed_field"].changed_field_binding_id,
            family["changed_artifact"].changed_artifact_binding_id,
        )
        for record in records
    )
    assert records[0].invalidation_reason_class == "SOURCE_ARTIFACT_CHANGED"
    assert report.report_status == "PASS" and report.reason_codes == ()
    contextual = g2e.validate_invalidation_report_against_sources_v01(
        report,
        records=records,
        **_e3_invalidation_kwargs(family),
    )
    assert contextual.status == "PASS"


def test_e3_invalidation_history_predecessor_supersession_and_deletion_law_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture, target_roles=("packet",))
    baseline_bytes = tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in family["baseline"]
    )
    records, _report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    assert all(record.predecessor_artifact_id == record.artifact_id for record in records)
    assert all(record.superseded_by_artifact_id is None for record in records)
    assert all(record.historical_artifact_preserved and not record.deleted for record in records)
    assert baseline_bytes == tuple(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item))
        for item in family["baseline"]
    )


def test_e3_g2a_packet_candidate_root_boundary_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture, target_roles=("packet",))
    records, report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    packet_id = e3_baseline_fixture["g2a"]["packet"].packet_identity.packet_id
    record = next(
        item
        for item in records
        if item.artifact_id == family["roles"]["packet"].artifact_id
    )
    assert record.g2a_packet_relation == "PACKET_ROOT_REVIEW_REQUIRED"
    assert packet_id in record.trace_refs
    assert report.ordered_packet_invalidation_candidate_ids == (packet_id,)
    assert report.reason_codes == ("g2e_invalidation_g2a_root_binding_required",)
    assert report.root_review_required and not report.action_commit_packet_created


def test_e3_g2b_reuse_certificate_stale_history_preserved_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture, target_roles=("certificate",))
    certificate = e3_baseline_fixture["g2b"]["certificate"]
    before = _e3_public_plain(certificate)
    records, report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    record = next(
        item
        for item in records
        if item.artifact_id == family["roles"]["certificate"].artifact_id
    )
    assert record.g2b_reuse_relation == "REUSE_CERTIFICATE_STALE"
    assert certificate.certificate_id in record.trace_refs
    assert report.ordered_stale_reuse_certificate_ids == (certificate.certificate_id,)
    assert report.reason_codes == ("g2e_invalidation_g2b_reuse_still_current",)
    assert before == _e3_public_plain(certificate)
    assert not report.drs_write_created


def test_e3_g2c_route_revalidation_terminal_before_e4_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture, target_roles=("route",))
    records, report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    route_id = family["context"].baseline_g2c_route_eligibility_artifact.artifact_id
    route_record = next(
        item
        for item in records
        if item.artifact_id == family["roles"]["route"].artifact_id
    )
    assert route_record.invalidation_reason_class == "ROUTE_REVALIDATION_REQUIRED"
    assert route_record.g2c_route_relation == "ROUTE_REVALIDATION_REQUIRED"
    assert route_id in route_record.trace_refs
    assert report.report_status == "FAIL_CLOSED"
    assert report.ordered_route_revalidation_ids == (route_id,)
    assert "g2e_route_revalidation_required" in report.reason_codes
    assert hasattr(g2e, "build_selective_recomputation_plan_from_affected_set_v01")


def test_e3_invalidation_report_artifact_and_t03_chain_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    records, report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    chain = _e3_artifact_chain(family)
    proposed = chain["proposed"]
    validated = chain["validated"]
    assert type(proposed) is g2e.KernelArtifactV01
    assert type(validated) is g2e.KernelArtifactV01
    assert validate_kernel_artifact_v01(proposed) == ()
    assert validate_kernel_artifact_v01(validated) == ()

    def expected_ordered_unique(values: tuple[str, ...]) -> tuple[str, ...]:
        ordered: list[str] = []
        for value in values:
            if value not in ordered:
                ordered.append(value)
        return tuple(ordered)

    context = family["context"]
    baseline_ids = tuple(item.artifact_id for item in family["baseline"])
    observed_ids = tuple(item.artifact_id for item in family["observed"])
    route_id = context.baseline_g2c_route_eligibility_artifact.artifact_id
    report_id = context.baseline_g2d_execution_bundle.report_artifact.artifact_id
    source_parent_candidates = (
        route_id,
        report_id,
        *baseline_ids,
        *observed_ids,
    )
    expected_proposed_parents = expected_ordered_unique(source_parent_candidates)
    expected_validated_parents = expected_ordered_unique(
        (proposed.artifact_id, *source_parent_candidates)
    )
    assert proposed.parent_refs == expected_proposed_parents
    assert validated.parent_refs == expected_validated_parents
    assert len(proposed.parent_refs) == len(set(proposed.parent_refs))
    assert len(validated.parent_refs) == len(set(validated.parent_refs))
    assert proposed.parent_refs[:2] == (route_id, report_id)
    assert validated.parent_refs[:3] == (proposed.artifact_id, route_id, report_id)
    assert proposed.parent_refs[2 : 2 + len(baseline_ids)] == baseline_ids
    assert validated.parent_refs[3 : 3 + len(baseline_ids)] == baseline_ids
    assert proposed.parent_refs[2 + len(baseline_ids)] == observed_ids[0]
    assert validated.parent_refs[3 + len(baseline_ids)] == observed_ids[0]
    for unchanged_alias_id in baseline_ids[1:]:
        assert proposed.parent_refs.count(unchanged_alias_id) == 1
        assert validated.parent_refs.count(unchanged_alias_id) == 1
    proposed_plain = kernel_artifact_to_plain_dict_v01(proposed)
    validated_plain = kernel_artifact_to_plain_dict_v01(validated)
    assert canonical_json_bytes_v01(proposed_plain["payload"]) == (
        canonical_json_bytes_v01(validated_plain["payload"])
    )
    profiles = {
        row[0]: row for row in g2e.G2E_ABI_ARTIFACT_INSTANCE_PROFILES_V01
    }
    proposed_profile = profiles["delta_source_proposed"]
    validated_profile = profiles["delta_source_validated"]
    assert proposed.artifact_id.startswith(proposed_profile[6])
    assert validated.artifact_id.startswith(validated_profile[6])
    assert proposed_profile[6] != validated_profile[6]
    assert proposed_profile[7] != validated_profile[7]
    assert proposed.lifecycle_state != validated.lifecycle_state
    assert proposed.parent_refs != validated.parent_refs
    assert proposed.artifact_id != validated.artifact_id
    for chain_name in ("proposed", "validated", "graph", "affected"):
        assert validate_kernel_artifact_v01(chain[chain_name]) == ()
    t03 = _e3_transition_decision(chain["registry"], "g2e_t03_invalidation_derive")
    artifact = g2e._project_invalidation_report_artifact_v01(
        report=report,
        affected_set_artifact=chain["affected"],
        validated_delta_source_artifact=chain["validated"],
        dependency_graph_artifact=chain["graph"],
        baseline_route_artifact=family["context"].baseline_g2c_route_eligibility_artifact,
        delta=family["delta"],
        t03_decision_id=t03.decision_id,
    )
    assert validate_kernel_artifact_v01(artifact) == ()
    assert g2e._validate_invalidation_report_artifact_against_source_v01(
        artifact,
        report=report,
        affected_set_artifact=chain["affected"],
        validated_delta_source_artifact=chain["validated"],
        dependency_graph_artifact=chain["graph"],
        baseline_route_artifact=family["context"].baseline_g2c_route_eligibility_artifact,
        delta=family["delta"],
        t03_decision=t03,
    ) == ()
    assert tuple(record.invalidation_record_id for record in records) == (
        report.ordered_invalidation_record_ids
    )


def test_e3_preservation_no_cache_full_bytes_and_no_object_identity_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture)
    records, _report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    proof = g2e.prove_unaffected_artifact_preservation_v01(
        affected_set=family["affected"],
        invalidation_records=records,
        source_context=family["context"],
        recomputed_g2d_execution_bundle=e3_baseline_fixture["bundle"],
        recomputed_bindings=(),
    )
    assert proof.status == "PASS" and proof.byte_identity_preserved
    assert proof.before_cache_state_sha256 == proof.after_cache_state_sha256
    assert proof.mutable_global_write_count == 0
    assert proof.object_identity_used_as_proof is False
    assert proof.ordered_before_artifact_sha256 == proof.ordered_after_artifact_sha256
    assert proof.ordered_before_payload_sha256 == proof.ordered_after_payload_sha256
    assert proof.ordered_before_identity_ids == proof.ordered_after_identity_ids
    assert g2e.prove_unaffected_artifact_preservation_v01(
        affected_set=family["affected"],
        invalidation_records=records,
        source_context=family["context"],
        recomputed_g2d_execution_bundle=e3_baseline_fixture["bundle"],
        recomputed_bindings=(),
    ) == proof


def test_e3_preservation_mutation_and_in_place_rejection_matrix_v01(
    e3_baseline_fixture: dict[str, object],
) -> None:
    family = _e3_delta_family(e3_baseline_fixture, target_roles=("route",))
    records, _report = g2e.derive_invalidation_report_v01(
        **_e3_invalidation_kwargs(family)
    )
    with pytest.raises(ValueError, match="g2e_recomputation_in_place_forbidden"):
        g2e.prove_unaffected_artifact_preservation_v01(
            affected_set=family["affected"],
            invalidation_records=records,
            source_context=family["context"],
            recomputed_g2d_execution_bundle=e3_baseline_fixture["bundle"],
            recomputed_bindings=(),
        )
    proof = _e3_structural_proof()
    identity_changed = g2e.build_preservation_proof_v01(
        baseline_graph_id=proof.baseline_graph_id,
        affected_set_id=proof.affected_set_id,
        ordered_preserved_artifact_ids=proof.ordered_preserved_artifact_ids,
        ordered_before_artifact_sha256=proof.ordered_before_artifact_sha256,
        ordered_after_artifact_sha256=proof.ordered_after_artifact_sha256,
        ordered_before_payload_sha256=proof.ordered_before_payload_sha256,
        ordered_after_payload_sha256=proof.ordered_after_payload_sha256,
        ordered_before_identity_ids=proof.ordered_before_identity_ids,
        ordered_after_identity_ids=("artifact:g2e:e3:changed",),
    )
    assert identity_changed.reason_codes == ("g2e_preserved_identity_changed",)
    with pytest.raises(ValueError, match="g2e_preservation_proof_invalid"):
        g2e._project_preservation_proof_artifact_v01(
            proof=proof,
            root_accepted_plan_artifact=family["context"].baseline_g2c_route_eligibility_artifact,
            invalidation_report_artifact=family["context"].baseline_g2d_execution_bundle.report_artifact,
            recomputed_g2d_report_artifact=family["context"].baseline_g2d_execution_bundle.report_artifact,
            delta=family["delta"],
            recomputed_g2d_runtime_trace_id=family["context"].baseline_g2d_execution_bundle.runtime_trace.trace_id,
        )


def test_e3_no_e4_execution_root_facade_or_prior_slice_mutation_v01() -> None:
    runtime_source = MODULE_PATH.read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    runtime_tree = ast.parse(runtime_source)
    test_tree = ast.parse(test_source)
    runtime_calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(runtime_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    test_run_calls = [
        node
        for node in ast.walk(test_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run_fractal_runtime_v02"
    ]
    test_run_callers = tuple(
        node.name
        for node in test_tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Attribute)
            and candidate.func.attr == "run_fractal_runtime_v02"
            for candidate in ast.walk(node)
        )
    )
    whole_run_callers = tuple(
        node.name
        for node in runtime_tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Attribute)
            and candidate.func.attr == "run_fractal_runtime_v02"
            for candidate in ast.walk(node)
        )
    )
    assert whole_run_callers == ("_g2e4_execute_whole_run_escalation_v01",)
    assert "_d4_run_runtime_v02" not in runtime_calls
    assert len(test_run_calls) == 2
    assert test_run_callers == (
        "e3_baseline_fixture",
        "e4_full_fractal_baseline_fixture",
    )
    assert hasattr(g2e, "execute_selective_recomputation_v01")
    assert hasattr(g2e, "run_continuous_delta_runtime_v01")
    assert kernel.ContinuousDeltaSourceContextV01 is g2e.ContinuousDeltaSourceContextV01
    e3_nodes = (
        node
        for node in test_tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_e3_")
    )
    assert all(not node.decorator_list for node in e3_nodes)
    for path in (
        ROOT / "hedgehog/kernel/fractal_runtime_v02.py",
        ROOT / "hedgehog/kernel/root_decision_v01.py",
    ):
        assert path.is_file()


def _e4_input_family(
    baseline_fixture: dict[str, object],
    *,
    target_roles: tuple[str, ...] = ("ordinary",),
    full_closure: bool = False,
) -> dict[str, object]:
    family = _e3_delta_family(
        baseline_fixture,
        target_roles=target_roles,
        runtime_seed_projection=(
            None
            if full_closure
            else baseline_fixture["selected_seed_projection"]
        ),
        runtime_seed_projections=(
            baseline_fixture["full_seed_projections"]
            if full_closure
            else ()
        ),
    )
    request = g2e.build_affected_set_request_v01(
        delta=family["delta"],
        graph=family["graph"],
        trace_refs=(family["delta"].delta_id, family["graph"].graph_id),
    )
    affected = g2e.compute_affected_set_v01(
        request=request,
        delta=family["delta"],
        graph=family["graph"],
        source_bindings=(family["source_binding"],),
        changed_field_bindings=(family["changed_field"],),
        changed_artifact_bindings=(family["changed_artifact"],),
        dependency_edges=family["dependency_edges"],
        baseline_source_artifacts=family["baseline"],
        observed_source_artifacts=family["observed"],
    )
    records, report = g2e.derive_invalidation_report_v01(
        affected_set=affected,
        delta=family["delta"],
        source_context=family["context"],
        source_bindings=(family["source_binding"],),
        changed_field_bindings=(family["changed_field"],),
        changed_artifact_bindings=(family["changed_artifact"],),
        dependency_edges=family["dependency_edges"],
        dependency_graph=family["graph"],
    )
    return {
        **family,
        "request": request,
        "affected": affected,
        "invalidation_records": records,
        "invalidation_report": report,
    }


def _e4_plan_from_inputs(inputs: dict[str, object]) -> g2e.SelectiveRecomputationPlanV01:
    return g2e.build_selective_recomputation_plan_from_affected_set_v01(
        delta=inputs["delta"],
        affected_set=inputs["affected"],
        invalidation_records=inputs["invalidation_records"],
        invalidation_report=inputs["invalidation_report"],
        source_context=inputs["context"],
        source_bindings=(inputs["source_binding"],),
        changed_field_bindings=(inputs["changed_field"],),
        changed_artifact_bindings=(inputs["changed_artifact"],),
        dependency_edges=inputs["dependency_edges"],
        dependency_graph=inputs["graph"],
    )


@pytest.fixture(scope="module")
def e4_success_fixture(
    e4_full_fractal_baseline_fixture: dict[str, object],
) -> dict[str, object]:
    inputs = _e4_input_family(e4_full_fractal_baseline_fixture)
    plan = _e4_plan_from_inputs(inputs)
    baseline_bytes = canonical_json_bytes_v01(
        _e3_public_plain(inputs["context"].baseline_g2d_execution_bundle)
    )
    bundle, report = g2e.run_continuous_delta_runtime_v01(
        source_context=inputs["context"],
        source_bindings=(inputs["source_binding"],),
        changed_field_bindings=(inputs["changed_field"],),
        changed_artifact_bindings=(inputs["changed_artifact"],),
        delta=inputs["delta"],
        dependency_edges=inputs["dependency_edges"],
        dependency_graph=inputs["graph"],
    )
    assert report.status == "PASS", report.reason_codes
    assert type(bundle) is g2e.ContinuousDeltaExecutionBundleV01
    assert bundle.recomputation_plan == plan
    assert g2e.validate_continuous_delta_execution_bundle_v01(bundle).status == "PASS"
    assert canonical_json_bytes_v01(
        _e3_public_plain(inputs["context"].baseline_g2d_execution_bundle)
    ) == baseline_bytes
    return {
        "inputs": inputs,
        "plan": plan,
        "bundle": bundle,
        "report": report,
        "baseline_bytes": baseline_bytes,
    }


def _e4_contextual_plan_report(
    value: g2e.SelectiveRecomputationPlanV01,
    inputs: dict[str, object],
) -> g2e.ContinuousDeltaValidationReportV01:
    return g2e.validate_selective_recomputation_plan_against_sources_v01(
        value,
        delta=inputs["delta"],
        affected_set=inputs["affected"],
        invalidation_records=inputs["invalidation_records"],
        invalidation_report=inputs["invalidation_report"],
        source_context=inputs["context"],
        source_bindings=(inputs["source_binding"],),
        changed_field_bindings=(inputs["changed_field"],),
        changed_artifact_bindings=(inputs["changed_artifact"],),
        dependency_edges=inputs["dependency_edges"],
        dependency_graph=inputs["graph"],
    )


def _e4_root_outcome(
    fixture: dict[str, object],
    *,
    phase: str,
    outcome: str,
) -> dict[str, object]:
    bundle = fixture["bundle"]
    inputs = fixture["inputs"]
    assert type(bundle) is g2e.ContinuousDeltaExecutionBundleV01
    if phase == "PLAN":
        candidate = bundle.recomputation_plan
        candidate_plain = g2e.selective_recomputation_plan_to_plain_data_v01(candidate)
        time_source = bundle.plan_proposed_artifact
        route_source = bundle.source_context.baseline_g2c_route_eligibility_artifact
        parent_refs = (
            bundle.plan_proposed_artifact.artifact_id,
            route_source.artifact_id,
            bundle.source_context.baseline_g2d_execution_bundle.report_artifact.artifact_id,
        )
        trace_refs = (
            candidate.recomputation_plan_id,
            bundle.delta.delta_id,
            bundle.affected_result.affected_set_id,
            bundle.invalidation_report.invalidation_report_id,
        )
        prior = {
            "prior_decision": None,
            "prior_decision_id": None,
            "prior_selected_candidate_id": None,
        }
        validator_ids = ("continuous_delta_plan_against_sources_v01",)
    else:
        candidate = bundle.recomputation_result
        candidate_plain = g2e.selective_recomputation_result_to_plain_data_v01(candidate)
        time_source = bundle.recomputed_g2d_execution_bundle.report_artifact
        parent_refs = (
            bundle.plan_root_decision_artifact.artifact_id,
            bundle.plan_accepted_artifact.artifact_id,
            time_source.artifact_id,
            bundle.preservation_proof_artifact.artifact_id,
        )
        trace_refs = (
            bundle.plan_root_decision_result.decision_id,
            candidate.recomputation_result_id,
            bundle.recomputed_g2d_execution_bundle.runtime_report.report_id,
            bundle.preservation_proof.preservation_proof_id,
        )
        prior = {
            "prior_decision": "ACCEPT",
            "prior_decision_id": bundle.plan_root_decision_result.decision_id,
            "prior_selected_candidate_id": bundle.recomputation_plan.recomputation_plan_id,
        }
        validator_ids = (
            "continuous_delta_result_against_plan_v01",
            "fractal_runtime_execution_bundle_v02",
            "continuous_delta_preservation_v01",
        )
    evidence_refs = tuple(
        dict.fromkeys(
            item.validation_report_id
            for item in bundle.g2e_validation_reports
            if item.status == "PASS"
        )
    )[:4]
    return g2e._g2e4_root_review_v01(
        phase=phase,
        request_id=inputs["delta"].request_id,
        candidate_id=(
            candidate.recomputation_plan_id
            if phase == "PLAN"
            else candidate.recomputation_result_id
        ),
        candidate_plain=candidate_plain,
        transaction_id=inputs["delta"].transaction_id,
        target_root_id=inputs["delta"].owning_root_id,
        topology_ref=bundle.recomputed_g2d_execution_bundle.topology.topology_id,
        evidence_refs=evidence_refs,
        validator_ids=validator_ids,
        policy_id=inputs["delta"].observed_policy_version,
        time_source_artifact=time_source,
        root_kernel=inputs["context"].root_kernel,
        artifact_parent_refs=parent_refs,
        artifact_trace_refs=trace_refs,
        prior_root_state=prior,
        requested_outcome=outcome,
    )


def test_e4_exact_public_surface_schema_and_facade_geometry_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    historical = QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS + E3_PUBLIC_FUNCTIONS
    assert len(g2e.CONTINUOUS_DELTA_TYPES_V01) == 20
    assert len(g2e.SERIALIZED_CONTINUOUS_DELTA_TYPES_V01) == 18
    assert len(g2e.RUNTIME_ONLY_CONTINUOUS_DELTA_TYPES_V01) == 2
    assert public_functions[:62] == historical
    assert public_functions[62:] == E4_PUBLIC_FUNCTIONS
    assert len(public_functions) == 89
    assert g2e.__all__[:82] == TYPE_NAMES + historical
    assert g2e.__all__[82:] == E4_PUBLIC_FUNCTIONS
    assert len(g2e.__all__) == 109
    transition_names = (
        "build_continuous_delta_transition_registry_profile_v01",
        "validate_continuous_delta_transition_registry_profile_v01",
        "continuous_delta_transition_registry_profile_to_plain_dict_v01",
        "validate_continuous_delta_transition_decision_v01",
        "continuous_delta_transition_decision_to_plain_dict_v01",
        "rebuild_continuous_delta_transition_decision_identity_v01",
    )
    direct_names = TYPE_NAMES + public_functions + transition_names
    assert len(direct_names) == 115
    for name in TYPE_NAMES + public_functions:
        assert getattr(kernel, name) is getattr(g2e, name)
    for name in transition_names:
        assert getattr(kernel, name) is getattr(transition, name)
    assert len(kernel.__all__) == 19
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert len(schema["$defs"]) == 18
    assert g2e.validate_continuous_delta_execution_bundle_v01(
        e4_success_fixture["bundle"]
    ).status == "PASS"


def test_e4_five_quartets_identity_plain_data_and_schema_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    values = (
        bundle.recomputation_plan,
        bundle.recomputed_bindings[0],
        bundle.recomputation_result,
        bundle.runtime_trace,
        bundle.runtime_report,
    )
    validators = (
        g2e.validate_selective_recomputation_plan_v01,
        g2e.validate_recomputed_artifact_binding_v01,
        g2e.validate_selective_recomputation_result_v01,
        g2e.validate_continuous_delta_runtime_trace_v01,
        g2e.validate_continuous_delta_runtime_report_v01,
    )
    serializers = (
        g2e.selective_recomputation_plan_to_plain_data_v01,
        g2e.recomputed_artifact_binding_to_plain_data_v01,
        g2e.selective_recomputation_result_to_plain_data_v01,
        g2e.continuous_delta_runtime_trace_to_plain_data_v01,
        g2e.continuous_delta_runtime_report_to_plain_data_v01,
    )
    rebuilders = (
        g2e.rebuild_selective_recomputation_plan_identity_v01,
        g2e.rebuild_recomputed_artifact_binding_identity_v01,
        g2e.rebuild_selective_recomputation_result_identity_v01,
        g2e.rebuild_continuous_delta_runtime_trace_identity_v01,
        g2e.rebuild_continuous_delta_runtime_report_identity_v01,
    )
    definitions = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]
    for value, validator, serializer, rebuilder in zip(
        values, validators, serializers, rebuilders, strict=True
    ):
        assert validator(value).status == "PASS"
        plain = serializer(value)
        assert tuple(plain) == tuple(field.name for field in fields(type(value)))
        Draft202012Validator(definitions[type(value).__name__]).validate(plain)
        assert rebuilder(value) == getattr(value, fields(type(value))[0].name)
        invalid = replace(value, **{fields(type(value))[0].name: "invalid"})
        assert validator(invalid).status == "FAIL_CLOSED"


def test_e4_selective_plan_from_affected_set_and_contextual_validation_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    inputs = e4_success_fixture["inputs"]
    plan = e4_success_fixture["plan"]
    assert plan == _e4_plan_from_inputs(inputs)
    assert g2e.validate_selective_recomputation_plan_v01(plan).status == "PASS"
    contextual = _e4_contextual_plan_report(plan, inputs)
    assert contextual.status == "PASS"
    assert contextual.validated_object_id == plan.recomputation_plan_id
    assert plan.plan_status == "PASS"
    assert plan.root_review_required and plan.max_provider_calls == 0
    assert 0 < plan.max_work_items <= 256
    assert 0 < plan.max_queue_entries <= 1024
    bundle = e4_success_fixture["bundle"]
    t02 = bundle.g2e_transition_decisions[1]
    transition_suffix = (
        t02.decision_id,
        inputs["affected"].delta_id,
        inputs["affected"].graph_id,
    )
    expected_affected_trace_refs = (
        *(
            item
            for item in dict.fromkeys(inputs["affected"].trace_refs)
            if item not in transition_suffix
        ),
        *transition_suffix,
    )
    assert (
        bundle.affected_set_artifact.trace_refs
        == expected_affected_trace_refs
    )
    assert len(expected_affected_trace_refs) == len(
        set(expected_affected_trace_refs)
    )
    assert (
        expected_affected_trace_refs.count(inputs["affected"].delta_id)
        == 1
    )
    assert (
        expected_affected_trace_refs.count(inputs["affected"].graph_id)
        == 1
    )
    assert expected_affected_trace_refs[-3:] == transition_suffix
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t02,
        registry=registry,
        source_artifact=bundle.delta_source_artifact,
        target_artifact=bundle.affected_set_artifact,
    ) == ()


def test_e4_selective_plan_mutation_bounds_and_route_fail_closed_v01(
    e4_full_fractal_baseline_fixture: dict[str, object],
    e4_success_fixture: dict[str, object],
) -> None:
    plan = e4_success_fixture["plan"]
    inputs = e4_success_fixture["inputs"]
    over_bound = replace(plan, max_work_items=257)
    assert g2e.validate_selective_recomputation_plan_v01(over_bound).status == "FAIL_CLOSED"
    assert _e4_contextual_plan_report(over_bound, inputs).status == "FAIL_CLOSED"
    copied_trace = replace(plan, trace_refs=(*plan.trace_refs, plan.trace_refs[0]))
    assert g2e.validate_selective_recomputation_plan_v01(copied_trace).status == "FAIL_CLOSED"
    route_inputs = _e4_input_family(
        e4_full_fractal_baseline_fixture,
        target_roles=("route",),
    )
    assert route_inputs["invalidation_report"].report_status == "FAIL_CLOSED"
    assert "g2e_route_revalidation_required" in route_inputs["invalidation_report"].reason_codes
    with pytest.raises(ValueError, match="g2e_route_revalidation_required"):
        _e4_plan_from_inputs(route_inputs)


def test_e4_plan_root_accept_pair_t04_t05_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    t04, t05 = bundle.g2e_transition_decisions[3:5]
    assert bundle.plan_root_decision_result.decision == "ACCEPT"
    assert bundle.plan_root_decision_result.selected_candidate_id == (
        bundle.recomputation_plan.recomputation_plan_id
    )
    assert bundle.plan_root_decision_artifact.artifact_id.startswith(
        "g2e_root_plan_decision_v01:"
    )
    plan_root_payload = kernel_artifact_to_plain_dict_v01(
        bundle.plan_root_decision_artifact
    )["payload"]
    plan_root_plain = root_decision.root_decision_result_to_plain_dict_v01(
        bundle.plan_root_decision_result
    )
    assert "transaction_id" not in plan_root_payload
    assert bundle.plan_root_decision_artifact.transaction_id == (
        plan_root_plain["transaction_id"]
    )
    assert plan_root_payload == {
        key: value
        for key, value in plan_root_plain.items()
        if key != "transaction_id"
    }
    assert transition.validate_continuous_delta_transition_decision_v01(
        t04,
        registry=registry,
        source_artifact=bundle.plan_proposed_artifact,
        target_artifact=bundle.plan_root_decision_artifact,
    ) == ()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t05,
        registry=registry,
        source_artifact=bundle.plan_root_decision_artifact,
        target_artifact=bundle.plan_accepted_artifact,
    ) == ()


def test_e4_plan_root_non_accept_matrix_t06_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    t06 = bundle.g2e_transition_decisions[5]
    outcomes = (
        "BLOCKED_FAIL_CLOSED",
        "NEEDS_USER",
        "NEEDS_MORE_EVIDENCE",
        "DEFER",
        "REJECT",
        "NO_UPDATE",
    )
    for outcome in outcomes:
        review = _e4_root_outcome(e4_success_fixture, phase="PLAN", outcome=outcome)
        assert review["result"].decision == outcome
        assert not review["result"].permission_created
        assert not review["result"].final_output_created
        assert not review["result"].effect_requested
        blocked = g2e._g2e4_project_blocked_plan_artifact_v01(
            plan=bundle.recomputation_plan,
            proposed_artifact=bundle.plan_proposed_artifact,
            root_result=review["result"],
            root_artifact=review["artifact"],
            t06=t06,
            delta=bundle.delta,
            source_context=bundle.source_context,
        )
        assert blocked.lifecycle_state == "BLOCKED_FAIL_CLOSED"
        blocked_payload = kernel_artifact_to_plain_dict_v01(blocked)["payload"]
        plan_plain = g2e.selective_recomputation_plan_to_plain_data_v01(
            bundle.recomputation_plan
        )
        assert "trace_refs" not in blocked_payload
        assert blocked.trace_refs == (
            review["result"].decision_id,
            review["result"].reason_code,
            t06.decision_id,
        )
        assert blocked_payload == {
            **{
                key: value
                for key, value in plan_plain.items()
                if key != "trace_refs"
            },
            "root_decision": review["result"].decision,
            "root_reason_code": review["result"].reason_code,
        }
        assert transition.validate_continuous_delta_transition_decision_v01(
            t06,
            registry=registry,
            source_artifact=review["artifact"],
            target_artifact=blocked,
        ) == ()


def test_e4_observed_work_context_and_minimal_affected_subtree_mapping_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    inputs = e4_success_fixture["inputs"]
    recomputed = bundle.recomputed_g2d_execution_bundle
    context = recomputed.observed_work_context
    assert type(context) is g2d.RuntimeObservedWorkContextV02
    assert context.execution_scope == "SELECTIVE"
    assert g2d.validate_runtime_observed_work_context_v02(context).status == "PASS"
    direct_sources = tuple(
        item
        for binding in bundle.source_bindings
        for item in inputs["baseline"] + inputs["observed"]
        if item.artifact_id
        in {
            binding.baseline_source_artifact_id,
            binding.observed_source_artifact_id,
        }
    )
    assert g2d.validate_runtime_observed_work_context_against_sources_v02(
        context,
        baseline_execution_bundle=inputs["context"].baseline_g2d_execution_bundle,
        direct_source_artifacts=direct_sources,
        supporting_artifacts=(),
        binding_artifacts=context.ordered_binding_artifacts,
    ).status == "PASS"
    binding_payloads = tuple(
        kernel_artifact_to_plain_dict_v01(item)["payload"]
        for item in context.ordered_binding_artifacts
    )
    for payload in binding_payloads:
        change_proof = payload["change_proof"]
        pointers = tuple(change_proof["all_full_artifact_changed_pointers"])
        assert "/payload/hold_status" in pointers
        assert "/trace_refs/0" in pointers
        assert len(pointers) == len(set(pointers))
        assert change_proof["whole_artifact_expanded"] is False
        assert change_proof["whole_payload_expanded"] is False
        envelope_rows = tuple(
            row
            for row in change_proof["consumed_changed_material_rows"]
            if row["payload_pointer"] is None
        )
        assert any(
            row["full_artifact_pointer"] == "/trace_refs/0"
            for row in envelope_rows
        )
    binding_rows = tuple(
        payload["topology_binding"] for payload in binding_payloads
    )
    expected_retained_reports = (
        g2d.validate_fractal_runtime_source_context_v02(
            recomputed.source_context
        ),
        g2d.validate_runtime_topology_source_binding_against_g2c_v02(
            recomputed.source_binding,
            source_context=recomputed.source_context,
        ),
        g2d.validate_runtime_topology_seed_v02(recomputed.topology_seed),
        g2d.validate_runtime_execution_topology_against_sources_v02(
            recomputed.topology,
            source_context=recomputed.source_context,
        ),
    )
    assert recomputed.validation_reports[:4] == expected_retained_reports
    assert tuple(item["node_ref"] for item in binding_rows) == (
        context.ordered_direct_affected_node_ids
    )
    assert context.ordered_execution_node_ids == (
        bundle.recomputation_plan.ordered_work_node_ids
    )
    assert tuple(dict.fromkeys(item["cell_ref"] for item in binding_rows)) == (
        bundle.recomputation_plan.ordered_affected_cell_ids
    )
    baseline = inputs["context"].baseline_g2d_execution_bundle
    selected_cell_id = bundle.recomputation_plan.ordered_affected_cell_ids[0]
    selected_input = next(
        item for item in baseline.cell_inputs if item.cell_id == selected_cell_id
    )
    selected_projection = next(
        artifact
        for artifact in inputs["baseline"]
        if artifact.artifact_id in inputs["affected"].ordered_affected_ids
        and kernel_artifact_to_plain_dict_v01(artifact)["payload"].get(
            "projection_profile_id"
        )
        == "g2e_baseline_runtime_artifact_projection_v01"
    )
    ledger = g2e._g2e4_baseline_runtime_artifact_ledger_v01(baseline)
    selected_row = g2e._g2e4_resolve_runtime_artifact_projection_v01(
        source_artifact=selected_projection,
        ledger=ledger,
    )
    assert selected_row is not None
    selected_seed_artifact = inputs["context"].baseline_g2d_execution_bundle.queue_artifacts[
        inputs["context"].baseline_g2d_execution_bundle.queue_entries.index(
            selected_row["queue_entry"]
        )
    ]
    projection_payload = kernel_artifact_to_plain_dict_v01(selected_projection)[
        "payload"
    ]
    assert selected_projection.parent_refs == (selected_seed_artifact.artifact_id,)
    assert canonical_json_bytes_v01(
        projection_payload["projected_runtime_artifact"]
    ) == canonical_json_bytes_v01(
        kernel_artifact_to_plain_dict_v01(selected_seed_artifact)
    )
    assert projection_payload["projected_runtime_artifact_sha256"] == (
        _e2_artifact_sha(selected_seed_artifact)
    )
    assert selected_row["cell_input"] == selected_input
    assert selected_row["queue_entry"].cell_id == selected_input.cell_id
    assert selected_row["queue_entry"].node_id == selected_input.ordered_node_ids[0]
    assert selected_row["node"].node_id == context.ordered_direct_affected_node_ids[0]
    assert context.ordered_affected_cell_ids == (selected_input.cell_id,)
    assert context.ordered_execution_node_ids == selected_input.ordered_node_ids
    assert 0 < len(context.ordered_execution_node_ids) < len(
        baseline.topology.ordered_node_ids
    )
    derive_source = inspect.getsource(g2e._derive_selective_recomputation_plan_v01)
    assert "role_to_node_kind" not in derive_source
    assert "source_role" not in derive_source
    assert "dependent_role" not in derive_source


def test_e4_selective_execution_affected_only_unaffected_not_executed_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    plan = bundle.recomputation_plan
    recomputed = bundle.recomputed_g2d_execution_bundle
    executed_nodes = plan.ordered_work_node_ids
    assert executed_nodes == plan.ordered_work_node_ids
    baseline_bundle = bundle.source_context.baseline_g2d_execution_bundle
    baseline_node_ids = baseline_bundle.topology.ordered_node_ids
    context = recomputed.observed_work_context
    assert context is not None
    assert context.ordered_execution_node_ids == executed_nodes
    direct_node_ids = context.ordered_direct_affected_node_ids
    assert direct_node_ids
    assert set(direct_node_ids).issubset(executed_nodes)
    node_by_id = {item.node_id: item for item in baseline_bundle.topology_nodes}
    assert tuple(node_by_id[item].node_kind for item in direct_node_ids) == (
        "SEMANTIC_ACTOR",
    )
    assert direct_node_ids != executed_nodes
    unaffected_nodes = tuple(item for item in baseline_node_ids if item not in executed_nodes)
    assert unaffected_nodes
    assert 0 < len(executed_nodes) < len(baseline_node_ids)
    assert not set(unaffected_nodes).intersection(executed_nodes)
    selected_cell_id = plan.ordered_affected_cell_ids[0]
    baseline_child_inputs = tuple(
        item for item in baseline_bundle.cell_inputs if item.parent_cell_id is not None
    )
    assert len(baseline_child_inputs) == 2
    selected_baseline_input = next(
        item for item in baseline_child_inputs if item.cell_id == selected_cell_id
    )
    sibling_input = next(
        item for item in baseline_child_inputs if item.cell_id != selected_cell_id
    )
    recomputed_input_by_cell = {item.cell_id: item for item in recomputed.cell_inputs}
    assert recomputed_input_by_cell[selected_cell_id] != selected_baseline_input
    assert recomputed_input_by_cell[sibling_input.cell_id] == sibling_input
    assert canonical_json_bytes_v01(
        _e3_public_plain(recomputed_input_by_cell[sibling_input.cell_id])
    ) == canonical_json_bytes_v01(_e3_public_plain(sibling_input))
    baseline_sibling_scopes = tuple(
        item
        for item in baseline_bundle.scope_projections
        if item.child_cell_id == sibling_input.cell_id
    )
    candidate_sibling_scopes = tuple(
        item
        for item in recomputed.scope_projections
        if item.child_cell_id == sibling_input.cell_id
    )
    assert len(baseline_sibling_scopes) == 1
    assert candidate_sibling_scopes == baseline_sibling_scopes
    assert canonical_json_bytes_v01(
        _e3_public_plain(candidate_sibling_scopes[0])
    ) == canonical_json_bytes_v01(_e3_public_plain(baseline_sibling_scopes[0]))
    baseline_sibling_queue = tuple(
        (entry, artifact)
        for entry, artifact in zip(
            baseline_bundle.queue_entries,
            baseline_bundle.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == sibling_input.cell_id
    )
    candidate_sibling_queue = tuple(
        (entry, artifact)
        for entry, artifact in zip(
            recomputed.queue_entries,
            recomputed.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == sibling_input.cell_id
    )
    assert baseline_sibling_queue
    assert candidate_sibling_queue == baseline_sibling_queue
    assert tuple(
        (
            item[1].artifact_id,
            _e2_artifact_sha(item[1]),
            _e2_payload_sha(item[1]),
            canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item[1])),
        )
        for item in candidate_sibling_queue
    ) == tuple(
        (
            item[1].artifact_id,
            _e2_artifact_sha(item[1]),
            _e2_payload_sha(item[1]),
            canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(item[1])),
        )
        for item in baseline_sibling_queue
    )
    baseline_result_by_cell = {
        item.cell_id: (item, artifact)
        for item, artifact in zip(
            baseline_bundle.cell_results,
            baseline_bundle.result_artifacts,
            strict=True,
        )
    }
    candidate_result_by_cell = {
        item.cell_id: (item, artifact)
        for item, artifact in zip(
            recomputed.cell_results,
            recomputed.result_artifacts,
            strict=True,
        )
    }
    assert candidate_result_by_cell[sibling_input.cell_id] == (
        baseline_result_by_cell[sibling_input.cell_id]
    )
    assert candidate_result_by_cell[selected_cell_id] != (
        baseline_result_by_cell[selected_cell_id]
    )
    baseline_sibling_result_index = next(
        index
        for index, item in enumerate(baseline_bundle.cell_results)
        if item.cell_id == sibling_input.cell_id
    )
    candidate_sibling_result_index = next(
        index
        for index, item in enumerate(recomputed.cell_results)
        if item.cell_id == sibling_input.cell_id
    )
    assert recomputed.result_proposals[candidate_sibling_result_index] == (
        baseline_bundle.result_proposals[baseline_sibling_result_index]
    )
    assert recomputed.post_vv_reports[candidate_sibling_result_index] == (
        baseline_bundle.post_vv_reports[baseline_sibling_result_index]
    )
    assert recomputed.gt_advisory_reports[candidate_sibling_result_index] == (
        baseline_bundle.gt_advisory_reports[baseline_sibling_result_index]
    )
    for candidate_value, baseline_value in (
        (
            recomputed.result_proposals[candidate_sibling_result_index],
            baseline_bundle.result_proposals[baseline_sibling_result_index],
        ),
        (
            recomputed.post_vv_reports[candidate_sibling_result_index],
            baseline_bundle.post_vv_reports[baseline_sibling_result_index],
        ),
        (
            recomputed.gt_advisory_reports[candidate_sibling_result_index],
            baseline_bundle.gt_advisory_reports[baseline_sibling_result_index],
        ),
    ):
        assert canonical_json_bytes_v01(candidate_value) == canonical_json_bytes_v01(
            baseline_value
        )
    sibling_artifact = candidate_result_by_cell[sibling_input.cell_id][1]
    assert (
        sibling_artifact.artifact_id,
        _e2_artifact_sha(sibling_artifact),
        _e2_payload_sha(sibling_artifact),
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(sibling_artifact)),
    ) == (
        baseline_result_by_cell[sibling_input.cell_id][1].artifact_id,
        _e2_artifact_sha(baseline_result_by_cell[sibling_input.cell_id][1]),
        _e2_payload_sha(baseline_result_by_cell[sibling_input.cell_id][1]),
        canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(
                baseline_result_by_cell[sibling_input.cell_id][1]
            )
        ),
    )
    baseline_sibling_budgets = tuple(
        item for item in baseline_bundle.budgets if item.owning_cell_id == sibling_input.cell_id
    )
    candidate_sibling_budgets = tuple(
        item for item in recomputed.budgets if item.owning_cell_id == sibling_input.cell_id
    )
    assert candidate_sibling_budgets == baseline_sibling_budgets
    sibling_transition_ids = {
        entry.transition_decision_id for entry, _artifact in baseline_sibling_queue
    }
    assert tuple(
        item
        for item in recomputed.transition_decisions
        if item.decision_id in sibling_transition_ids
    ) == tuple(
        item
        for item in baseline_bundle.transition_decisions
        if item.decision_id in sibling_transition_ids
    )
    assert recomputed.revise_observations == baseline_bundle.revise_observations
    assert recomputed.partial_failures == baseline_bundle.partial_failures
    assert recomputed.backpressure_states == baseline_bundle.backpressure_states
    binding_ids = {item.artifact_id for item in context.ordered_binding_artifacts}
    sibling_initial_artifacts = tuple(
        artifact
        for entry, artifact in candidate_sibling_queue
        if entry.predecessor_queue_entry_id is None
    )
    assert sibling_initial_artifacts
    assert all(
        not binding_ids.intersection(artifact.parent_refs)
        for artifact in sibling_initial_artifacts
    )
    sibling_artifact_ids = {
        *(artifact.artifact_id for _entry, artifact in baseline_sibling_queue),
        baseline_result_by_cell[sibling_input.cell_id][1].artifact_id,
    }
    baseline_sibling_causal = tuple(
        item
        for item in baseline_bundle.causal_consumption_refs
        if item.source_artifact_id in sibling_artifact_ids
        or item.downstream_artifact_id in sibling_artifact_ids
    )
    candidate_sibling_causal = tuple(
        item
        for item in recomputed.causal_consumption_refs
        if item.source_artifact_id in sibling_artifact_ids
        or item.downstream_artifact_id in sibling_artifact_ids
    )
    assert baseline_sibling_causal
    assert len(candidate_sibling_causal) == len(baseline_sibling_causal)
    assert recomputed.runtime_trace.trace_id != baseline_bundle.runtime_trace.trace_id

    def queue_artifact_role(
        entry: object,
    ) -> tuple[object, ...]:
        return (
            entry.cell_id,
            entry.node_id,
            entry.state,
            entry.node_instance_sequence,
            entry.snapshot_sequence,
        )

    baseline_queue_artifact_by_role = {
        queue_artifact_role(entry): artifact
        for entry, artifact in zip(
            baseline_bundle.queue_entries,
            baseline_bundle.queue_artifacts,
            strict=True,
        )
    }
    candidate_queue_artifact_by_role = {
        queue_artifact_role(entry): artifact
        for entry, artifact in zip(
            recomputed.queue_entries,
            recomputed.queue_artifacts,
            strict=True,
        )
    }
    assert len(baseline_queue_artifact_by_role) == len(
        baseline_bundle.queue_artifacts
    )
    assert len(candidate_queue_artifact_by_role) == len(
        recomputed.queue_artifacts
    )
    assert set(candidate_queue_artifact_by_role) == set(
        baseline_queue_artifact_by_role
    )

    def result_artifact_role(
        result: object,
    ) -> tuple[object, ...]:
        return (
            result.cell_id,
            result.parent_cell_id,
            result.outcome,
        )

    baseline_result_artifact_by_role = {
        result_artifact_role(result): artifact
        for result, artifact in zip(
            baseline_bundle.cell_results,
            baseline_bundle.result_artifacts,
            strict=True,
        )
    }
    candidate_result_artifact_by_role = {
        result_artifact_role(result): artifact
        for result, artifact in zip(
            recomputed.cell_results,
            recomputed.result_artifacts,
            strict=True,
        )
    }
    assert len(baseline_result_artifact_by_role) == len(
        baseline_bundle.result_artifacts
    )
    assert len(candidate_result_artifact_by_role) == len(
        recomputed.result_artifacts
    )
    assert set(candidate_result_artifact_by_role) == set(
        baseline_result_artifact_by_role
    )

    candidate_to_baseline_artifact_id = {
        candidate_queue_artifact_by_role[role].artifact_id: (
            baseline_queue_artifact_by_role[role].artifact_id
        )
        for role in baseline_queue_artifact_by_role
    }
    candidate_to_baseline_artifact_id.update(
        {
            candidate_result_artifact_by_role[role].artifact_id: (
                baseline_result_artifact_by_role[role].artifact_id
            )
            for role in baseline_result_artifact_by_role
        }
    )
    candidate_to_baseline_artifact_id[
        recomputed.report_artifact.artifact_id
    ] = baseline_bundle.report_artifact.artifact_id
    changed_carrier_ids = {
        candidate_id: baseline_id
        for candidate_id, baseline_id in candidate_to_baseline_artifact_id.items()
        if candidate_id != baseline_id
    }
    assert changed_carrier_ids
    assert not sibling_artifact_ids.intersection(changed_carrier_ids)
    changed_queue_roles = {
        role
        for role in baseline_queue_artifact_by_role
        if candidate_queue_artifact_by_role[role].artifact_id
        != baseline_queue_artifact_by_role[role].artifact_id
    }
    root_cell_id = next(
        item.cell_id
        for item in baseline_bundle.cell_inputs
        if item.parent_cell_id is None
    )
    assert all(
        role[0] in {selected_cell_id, root_cell_id}
        for role in changed_queue_roles
    )
    changed_result_roles = {
        role
        for role in baseline_result_artifact_by_role
        if candidate_result_artifact_by_role[role].artifact_id
        != baseline_result_artifact_by_role[role].artifact_id
    }
    assert all(
        role[0] in {selected_cell_id, root_cell_id}
        for role in changed_result_roles
    )

    def baseline_causal_material(item: object) -> tuple[object, ...]:
        assert item.trace_refs == (
            item.source_artifact_id,
            item.downstream_artifact_id,
            baseline_bundle.runtime_trace.trace_id,
        )
        return (
            item.producer_actor_id,
            item.source_artifact_id,
            item.output_field,
            item.consumer_component,
            item.downstream_artifact_id,
            item.decision_effect,
            item.disposition,
            item.reason_code,
            item.trace_refs,
        )

    def normalized_candidate_causal_material(
        item: object,
    ) -> tuple[object, ...]:
        assert item.trace_refs == (
            item.source_artifact_id,
            item.downstream_artifact_id,
            recomputed.runtime_trace.trace_id,
        )
        source_artifact_id = candidate_to_baseline_artifact_id.get(
            item.source_artifact_id,
            item.source_artifact_id,
        )
        downstream_artifact_id = candidate_to_baseline_artifact_id.get(
            item.downstream_artifact_id,
            item.downstream_artifact_id,
        )
        return (
            item.producer_actor_id,
            source_artifact_id,
            item.output_field,
            item.consumer_component,
            downstream_artifact_id,
            item.decision_effect,
            item.disposition,
            item.reason_code,
            (
                source_artifact_id,
                downstream_artifact_id,
                baseline_bundle.runtime_trace.trace_id,
            ),
        )

    baseline_causal_materials = tuple(
        baseline_causal_material(item)
        for item in baseline_sibling_causal
    )
    candidate_causal_materials = tuple(
        normalized_candidate_causal_material(item)
        for item in candidate_sibling_causal
    )
    assert len(set(baseline_causal_materials)) == len(
        baseline_causal_materials
    )
    assert len(set(candidate_causal_materials)) == len(
        candidate_causal_materials
    )
    assert sorted(candidate_causal_materials) == sorted(
        baseline_causal_materials
    )
    assert any(
        item.source_artifact_id in changed_carrier_ids
        or item.downstream_artifact_id in changed_carrier_ids
        for item in candidate_sibling_causal
    )
    assert all(
        item.decision_effect
        not in {"OBSERVED_WORK_INPUT", "OBSERVED_WORK_CELL_BINDING"}
        for item in candidate_sibling_causal
    )
    assert all(
        item.source_artifact_id not in binding_ids
        and item.downstream_artifact_id not in binding_ids
        and not binding_ids.intersection(item.trace_refs)
        for item in candidate_sibling_causal
    )
    assert canonical_json_bytes_v01(_e3_public_plain(baseline_bundle)) == (
        e4_success_fixture["baseline_bytes"]
    )
    assert g2d.validate_fractal_runtime_execution_bundle_v02(recomputed).status == "PASS"


def test_e4_recomputed_binding_predecessor_and_in_place_rejection_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    assert bundle.recomputed_bindings
    recomputed = bundle.recomputed_g2d_execution_bundle
    baseline = bundle.source_context.baseline_g2d_execution_bundle
    queue_by_id = {item.queue_entry_id: item for item in recomputed.queue_entries}
    result_by_id = {item.result_id: item for item in recomputed.cell_results}
    sibling_cell_id = next(
        item.cell_id
        for item in baseline.cell_inputs
        if item.parent_cell_id is not None
        and item.cell_id not in bundle.recomputation_plan.ordered_affected_cell_ids
    )
    sibling_artifact_ids = {
        artifact.artifact_id
        for entry, artifact in zip(
            baseline.queue_entries,
            baseline.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == sibling_cell_id
    }
    sibling_artifact_ids.add(
        next(
            artifact.artifact_id
            for result, artifact in zip(
                baseline.cell_results,
                baseline.result_artifacts,
                strict=True,
            )
            if result.cell_id == sibling_cell_id
        )
    )
    for binding in bundle.recomputed_bindings:
        assert g2e.validate_recomputed_artifact_binding_v01(binding).status == "PASS"
        assert binding.prior_artifact_id != binding.new_artifact_id
        assert binding.prior_payload_sha256 != binding.new_payload_sha256
        owner_result = result_by_id[binding.g2d_cell_result_ref]
        source_queue = queue_by_id[binding.source_queue_entry_id]
        assert binding.source_cell_id == owner_result.cell_id
        assert source_queue.cell_id == binding.source_cell_id
        assert binding.prior_artifact_id not in sibling_artifact_ids
        assert binding.new_artifact_id not in sibling_artifact_ids
        with pytest.raises(ValueError, match="g2e_recomputation_in_place_forbidden"):
            g2e.build_recomputed_artifact_binding_v01(
                recomputation_plan_id=binding.recomputation_plan_id,
                prior_artifact_id=binding.prior_artifact_id,
                prior_payload_sha256=binding.prior_payload_sha256,
                new_artifact_id=binding.prior_artifact_id,
                new_payload_sha256=binding.prior_payload_sha256,
                predecessor_relation=binding.predecessor_relation,
                supersession_relation=binding.supersession_relation,
                derivation_refs=binding.derivation_refs,
                source_cell_id=binding.source_cell_id,
                source_queue_entry_id=binding.source_queue_entry_id,
                g2d_cell_result_ref=binding.g2d_cell_result_ref,
                g2d_runtime_report_ref=binding.g2d_runtime_report_ref,
                trace_refs=binding.trace_refs,
            )


def test_e4_partial_failure_backpressure_revise_no_progress_v01(
    e4_success_fixture: dict[str, object],
    e4_full_fractal_baseline_fixture: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    success_bundle = e4_success_fixture["bundle"]
    success_recomputed = success_bundle.recomputed_g2d_execution_bundle
    baseline = e4_success_fixture["inputs"][
        "context"
    ].baseline_g2d_execution_bundle
    baseline_bytes = canonical_json_bytes_v01(_e3_public_plain(baseline))
    success_bytes = canonical_json_bytes_v01(_e3_public_plain(success_recomputed))
    assert success_recomputed.revise_observations == ()
    assert success_recomputed.partial_failures == ()
    assert success_recomputed.backpressure_states == ()
    assert success_bundle.recomputation_result.result_status == "PASS"

    captures: dict[str, list[tuple[tuple[object, ...], dict[str, object], object]]] = {}
    originals: dict[tuple[object, str], object] = {}

    def observe(module: object, name: str) -> None:
        original = getattr(module, name)
        originals[(module, name)] = original
        captures.setdefault(name, [])

        def wrapper(*args: object, **kwargs: object) -> object:
            result = original(*args, **kwargs)
            captures[name].append((args, kwargs, result))
            return result

        monkeypatch.setattr(module, name, wrapper)

    for module, name in (
        (g2d, "evaluate_fractal_revise_observation_v02"),
        (g2d, "record_fractal_partial_failure_v02"),
        (g2d, "evaluate_fractal_backpressure_v02"),
        (g2d, "build_fractal_runtime_execution_bundle_v02"),
        (g2e, "build_selective_recomputation_result_v01"),
        (g2e, "validate_selective_recomputation_result_against_plan_v01"),
        (g2e, "build_continuous_delta_runtime_trace_v01"),
        (g2e, "build_continuous_delta_runtime_report_v01"),
        (g2e, "build_continuous_delta_execution_bundle_v01"),
        (g2e, "build_kernel_artifact_v01"),
        (g2e, "build_causal_consumption_ref_v01"),
        (root_decision, "decide_root_v01"),
    ):
        observe(module, name)

    conditional_inputs = _e4_input_family(
        e4_full_fractal_baseline_fixture,
        target_roles=("packet",),
    )
    bundle, report = g2e.run_continuous_delta_runtime_v01(
        source_context=conditional_inputs["context"],
        source_bindings=(conditional_inputs["source_binding"],),
        changed_field_bindings=(conditional_inputs["changed_field"],),
        changed_artifact_bindings=(conditional_inputs["changed_artifact"],),
        delta=conditional_inputs["delta"],
        dependency_edges=conditional_inputs["dependency_edges"],
        dependency_graph=conditional_inputs["graph"],
    )
    expected_reasons = (
        "g2e_recomputation_no_progress",
        "g2e_transition_selective_recomputation_blocked",
    )
    assert bundle is None
    assert report.status == "FAIL_CLOSED"
    assert report.reason_codes == expected_reasons

    g2d_bundles = tuple(
        row[2]
        for row in captures["build_fractal_runtime_execution_bundle_v02"]
        if type(row[2]) is g2d.FractalRuntimeExecutionBundleV02
    )
    assert len(g2d_bundles) == 1
    failure_bundle = g2d_bundles[0]
    assert g2d.validate_fractal_runtime_execution_bundle_v02(
        failure_bundle
    ).status == "PASS"
    revise_observations = failure_bundle.revise_observations
    partial_failures = failure_bundle.partial_failures
    backpressure_states = failure_bundle.backpressure_states
    assert len(revise_observations) == 2
    assert len(partial_failures) == 1
    assert backpressure_states == ()
    positive, deadend = revise_observations
    public_revise_results = tuple(
        row[2]
        for row in captures["evaluate_fractal_revise_observation_v02"]
        if type(row[2]) is g2d.FractalReviseObservationV02
    )
    assert len(public_revise_results) == 4
    assert public_revise_results[0] == public_revise_results[1] == positive
    assert public_revise_results[2] == public_revise_results[3] == deadend
    assert positive.revise_eligible is True
    assert positive.progress_units > 0
    assert positive.derived_terminal_state is None
    assert deadend.revise_eligible is False
    assert deadend.derived_terminal_state == "DEADEND"
    assert deadend.reason_codes == ("g2d_no_progress_deadend",)
    assert all(
        g2d.validate_fractal_revise_observation_v02(item).status == "PASS"
        for item in revise_observations
    )
    deadend_entry = next(
        item
        for item in failure_bundle.queue_entries
        if item.state == "DEADEND"
        and item.node_id
        == next(
            node.node_id
            for node in failure_bundle.topology_nodes
            if node.node_kind == "SEMANTIC_ACTOR"
            and node.node_id
            in next(
                cell.ordered_node_ids
                for cell in failure_bundle.cell_inputs
                if cell.cell_id == deadend.cell_id
            )
        )
    )
    validating_entry = next(
        item
        for item in failure_bundle.queue_entries
        if item.queue_entry_id == deadend_entry.predecessor_queue_entry_id
    )
    assert validating_entry.state == "VALIDATING"
    assert deadend_entry.queue_reason_codes == validating_entry.queue_reason_codes
    assert "g2d_no_progress_deadend" not in validating_entry.queue_reason_codes
    deadend_decision = next(
        item
        for item in failure_bundle.transition_decisions
        if item.decision_id == deadend_entry.transition_decision_id
    )
    assert deadend_decision.rule_id == "g2d_t12_validating_to_deadend"
    assert deadend_decision.decision == "RETURN_TO_ROOT"
    assert deadend_decision.reason_code == "g2d_transition_deadend_recorded"
    assert deadend_entry.cell_budget_id == validating_entry.cell_budget_id
    assert deadend_entry.global_budget_id == validating_entry.global_budget_id

    partial = partial_failures[0]
    assert g2d.validate_fractal_partial_failure_record_v02(partial).status == "PASS"
    assert partial.retry_eligible is False
    assert partial.required_child is True
    assert partial.sibling_independent is True
    assert partial.parent_disposition == "DEADEND"
    failed_child = next(
        item for item in failure_bundle.cell_results if item.result_id == partial.child_result_id
    )
    root_result = failure_bundle.cell_results[-1]
    assert failed_child.outcome == "DEADEND"
    assert root_result.outcome == "DEADEND"
    assert root_result.partial_failure_ids == (partial.partial_failure_id,)
    assert failure_bundle.runtime_trace.revise_observation_ids == tuple(
        item.observation_id for item in revise_observations
    )
    assert failure_bundle.runtime_trace.partial_failure_ids == (
        partial.partial_failure_id,
    )
    assert failure_bundle.runtime_trace.backpressure_state_ids == tuple(
        item.backpressure_id for item in backpressure_states
    )

    public_backpressure_calls = tuple(captures["evaluate_fractal_backpressure_v02"])
    assert len(public_backpressure_calls) == 2
    for (args, kwargs, result), (expected_geometry, expected_latest_count) in zip(
        public_backpressure_calls,
        (
            ((0, 0, 0, 3), 7),
            ((1, 1, 2, 1), 15),
        ),
        strict=True,
    ):
        assert args == ()
        policy = kwargs["policy"]
        global_budget = kwargs["global_budget"]
        queue_entries = kwargs["queue_entries"]
        settled_queue_entries = kwargs["settled_queue_entry_log"]
        assert policy.max_parallelism == 3
        latest_by_key = {
            (item.cell_id, item.node_id): item
            for item in settled_queue_entries
        }
        lawful_latest_frontier = tuple(
            item
            for item in settled_queue_entries
            if latest_by_key[(item.cell_id, item.node_id)] == item
        )
        running_count = sum(item.state == "RUNNING" for item in queue_entries)
        ready_count = sum(item.state == "READY" for item in queue_entries)
        occupied = global_budget.current_parallelism + ready_count
        residual = policy.max_parallelism - occupied
        assert queue_entries == lawful_latest_frontier
        assert len(queue_entries) == expected_latest_count
        assert len(queue_entries) == len(
            {(item.cell_id, item.node_id) for item in queue_entries}
        )
        assert running_count == global_budget.current_parallelism
        assert (running_count, ready_count, occupied, residual) == expected_geometry
        assert occupied + residual == policy.max_parallelism
        assert result is None
    assert "g2d_t03_pending_backpressure_defer" not in tuple(
        item.rule_id for item in failure_bundle.transition_decisions
    )
    assert "g2d_transition_backpressure_deferred" not in tuple(
        item.reason_code for item in failure_bundle.transition_decisions
    )

    results = tuple(
        row[2]
        for row in captures["build_selective_recomputation_result_v01"]
        if type(row[2]) is g2e.SelectiveRecomputationResultV01
    )
    traces = tuple(
        row[2]
        for row in captures["build_continuous_delta_runtime_trace_v01"]
        if type(row[2]) is g2e.ContinuousDeltaRuntimeTraceV01
    )
    reports = tuple(
        row[2]
        for row in captures["build_continuous_delta_runtime_report_v01"]
        if type(row[2]) is g2e.ContinuousDeltaRuntimeReportV01
    )
    assert len(results) == len(traces) == len(reports) == 1
    result = results[0]
    trace = traces[0]
    runtime_report = reports[0]
    assert result.result_status == "FAIL_CLOSED"
    assert result.reason_codes == expected_reasons
    assert result.ordered_partial_failure_ids == (partial.partial_failure_id,)
    assert result.ordered_unresolved_artifact_ids
    assert set(result.ordered_unresolved_artifact_ids).issubset(
        set(conditional_inputs["affected"].ordered_affected_ids)
    )
    assert g2e.validate_selective_recomputation_result_v01(result).status == "PASS"
    contextual_reports = tuple(
        row[2]
        for row in captures[
            "validate_selective_recomputation_result_against_plan_v01"
        ]
    )
    assert contextual_reports[-1].status == "PASS"
    assert g2e.validate_continuous_delta_runtime_trace_v01(trace).status == "PASS"
    assert g2e.validate_continuous_delta_runtime_report_v01(
        runtime_report
    ).status == "PASS"
    assert runtime_report.report_status == "FAIL_CLOSED"
    assert runtime_report.reason_codes == expected_reasons
    assert runtime_report.unresolved_count == len(
        result.ordered_unresolved_artifact_ids
    )
    assert trace.recomputation_result_id == result.recomputation_result_id
    assert "g2e_t10_report_finalize" not in tuple(
        item.rule_id
        for item in g2e._g2e4_transition_decisions_v01()
        if item.decision_id in trace.ordered_transition_decision_ids
    )

    root_results = tuple(
        row[2]
        for row in captures["decide_root_v01"]
        if type(row[2]) is root_decision.RootDecisionResultV01
    )
    assert tuple(item.decision for item in root_results) == (
        "ACCEPT",
        "BLOCKED_FAIL_CLOSED",
    )
    final_root = root_results[-1]
    assert not final_root.permission_created
    assert not final_root.final_output_created
    assert not final_root.effect_requested
    final_root_input = root_decision.root_decision_input_to_plain_dict_v01(
        captures["decide_root_v01"][-1][1]["decision_input"]
    )
    required_root_evidence = set(
        final_root_input["post_vv_bundle"]["required_evidence_refs"]
    )
    assert {
        *(str(item["vv_report_id"]) for item in failure_bundle.post_vv_reports),
        *(str(item["gt_report_id"]) for item in failure_bundle.gt_advisory_reports),
        partial.partial_failure_id,
        *result.ordered_unresolved_artifact_ids,
    }.issubset(required_root_evidence)
    blocked_reports = tuple(
        row[2]
        for row in captures["build_kernel_artifact_v01"]
        if getattr(row[2], "artifact_type", None)
        == "ContinuousDeltaRuntimeReport"
        and getattr(row[2], "lifecycle_state", None) == "BLOCKED_FAIL_CLOSED"
    )
    assert len(blocked_reports) == 1
    blocked_report = blocked_reports[0]
    assert validate_kernel_artifact_v01(blocked_report) == ()
    assert kernel_artifact_to_plain_dict_v01(blocked_report)["payload"] == (
        g2e.continuous_delta_runtime_report_to_plain_data_v01(runtime_report)
    )
    causal_refs = tuple(
        row[2]
        for row in captures["build_causal_consumption_ref_v01"]
        if validate_causal_consumption_ref_v01(row[2]) == ()
    )
    assert causal_refs
    assert any(
        partial.partial_failure_id in item.trace_refs for item in causal_refs
    )
    assert any(
        item.downstream_artifact_id == blocked_report.artifact_id
        and item.disposition == "BLOCKED_BY_GATE"
        for item in causal_refs
    )
    assert captures["build_continuous_delta_execution_bundle_v01"] == []

    contextual_call = captures[
        "validate_selective_recomputation_result_against_plan_v01"
    ][-1]
    contextual_kwargs = contextual_call[1]
    contextual_validator = originals[
        (g2e, "validate_selective_recomputation_result_against_plan_v01")
    ]
    result_builder = originals[(g2e, "build_selective_recomputation_result_v01")]
    result_material = {
        field.name: getattr(result, field.name)
        for field in fields(type(result))
        if field.name != "recomputation_result_id"
    }

    def rebuilt_result(**changes: object) -> object:
        return result_builder(**{**result_material, **changes})

    negative_results = (
        rebuilt_result(ordered_partial_failure_ids=()),
        rebuilt_result(
            ordered_partial_failure_ids=("g2d_partial_failure_v02:foreign",)
        ),
        rebuilt_result(ordered_unresolved_artifact_ids=("artifact:foreign",)),
        rebuilt_result(
            ordered_unresolved_artifact_ids=tuple(
                reversed(result.ordered_unresolved_artifact_ids)
            )
        ),
        rebuilt_result(
            reason_codes=("g2e_recomputation_budget_exceeded", *expected_reasons)
        ),
    )
    assert len(result.ordered_unresolved_artifact_ids) > 1
    with pytest.raises(ValueError, match="g2e_recomputation_result_invalid"):
        rebuilt_result(
            ordered_partial_failure_ids=(
                partial.partial_failure_id,
                partial.partial_failure_id,
            )
        )
    assert all(
        contextual_validator(candidate, **contextual_kwargs).status
        == "FAIL_CLOSED"
        for candidate in negative_results
    )
    with pytest.raises(ValueError):
        rebuilt_result(result_status="PASS", reason_codes=())

    revise_call = captures["evaluate_fractal_revise_observation_v02"][0]
    revise_kwargs = revise_call[1]
    revise_evaluator = originals[(g2d, "evaluate_fractal_revise_observation_v02")]
    selected_input = revise_kwargs["cell_input"]
    sibling_input = next(
        item
        for item in failure_bundle.cell_inputs
        if item.parent_cell_id is not None and item.cell_id != selected_input.cell_id
    )
    for changes, expected_error in (
        ({"cell_input": sibling_input}, "g2d_revise_observation_invalid"),
        (
            {"cell_budget_before": revise_kwargs["global_budget_before"]},
            "g2d_revise_observation_invalid",
        ),
        (
            {"global_budget_before": revise_kwargs["cell_budget_before"]},
            "g2d_revise_observation_invalid",
        ),
        (
            {
                "revision_index": revise_kwargs["queue_entry"].snapshot_sequence
                + 1
            },
            "g2d_revise_observation_invalid",
        ),
        (
            {
                "queue_entry": replace(
                    revise_kwargs["queue_entry"],
                    queue_entry_id="frqueue_v02:foreign",
                )
            },
            "g2d_queue_entry_invalid",
        ),
    ):
        with pytest.raises(ValueError, match=expected_error):
            revise_evaluator(**{**revise_kwargs, **changes})
    assert g2d.validate_fractal_revise_observation_v02(
        replace(deadend, reason_codes=("g2d_revise_progress_positive",))
    ).status == "FAIL_CLOSED"
    assert g2d.validate_fractal_revise_observation_v02(
        replace(deadend, trace_refs=(*deadend.trace_refs[:-1], "trace:foreign"))
    ).status == "FAIL_CLOSED"

    partial_call = captures["record_fractal_partial_failure_v02"][0]
    partial_recorder = originals[(g2d, "record_fractal_partial_failure_v02")]
    with pytest.raises(ValueError, match="g2d_budget_predecessor_invalid"):
        partial_recorder(
            **{
                **partial_call[1],
                "allocated_cell_budget": partial_call[1]["global_budget"],
            }
        )
    successful_child = next(
        item
        for item in success_recomputed.cell_results
        if item.parent_cell_id is not None and item.outcome == "COMPLETED"
    )
    success_parent = next(
        item
        for item in success_recomputed.cell_inputs
        if item.cell_id == successful_child.parent_cell_id
    )
    success_budget_by_id = {
        item.budget_id: item for item in success_recomputed.budgets
    }
    with pytest.raises(ValueError, match="g2d_success_laundering_forbidden"):
        partial_recorder(
            topology=success_recomputed.topology,
            parent_input=success_parent,
            child_result=successful_child,
            failure_stage="CELL_RESULT_PRECONDITIONS",
            reason_codes=("g2d_required_child_failure",),
            source_reason_codes=(),
            evidence_refs=successful_child.evidence_refs,
            allocated_cell_budget=success_budget_by_id[
                successful_child.allocated_cell_budget_id
            ],
            final_cell_budget=success_budget_by_id[
                successful_child.final_cell_budget_id
            ],
            global_budget=success_budget_by_id[successful_child.global_budget_id],
            required_child=True,
            sibling_independent=True,
        )
    final_root_call = captures["decide_root_v01"][-1]
    assert root_decision.validate_root_decision_result_v01(
        kernel=conditional_inputs["context"].root_kernel,
        decision_input=final_root_call[1]["decision_input"],
        result=replace(final_root, decision="ACCEPT"),
    )

    assert canonical_json_bytes_v01(_e3_public_plain(baseline)) == baseline_bytes
    assert canonical_json_bytes_v01(_e3_public_plain(success_recomputed)) == success_bytes
    assert g2d.validate_fractal_runtime_execution_bundle_v02(
        success_recomputed
    ).status == "PASS"


def test_e4_preservation_full_bytes_and_immutable_baseline_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    proof = bundle.preservation_proof
    baseline = bundle.source_context.baseline_g2d_execution_bundle
    sibling_cell_id = next(
        item.cell_id
        for item in baseline.cell_inputs
        if item.parent_cell_id is not None
        and item.cell_id not in bundle.recomputation_plan.ordered_affected_cell_ids
    )
    sibling_artifact_ids = {
        artifact.artifact_id
        for entry, artifact in zip(
            baseline.queue_entries,
            baseline.queue_artifacts,
            strict=True,
        )
        if entry.cell_id == sibling_cell_id
    }
    sibling_artifact_ids.add(
        next(
            artifact.artifact_id
            for result, artifact in zip(
                baseline.cell_results,
                baseline.result_artifacts,
                strict=True,
            )
            if result.cell_id == sibling_cell_id
        )
    )
    assert g2e.validate_preservation_proof_v01(proof).status == "PASS"
    assert proof.byte_identity_preserved
    assert sibling_artifact_ids
    assert sibling_artifact_ids.issubset(proof.ordered_preserved_artifact_ids)
    assert proof.ordered_before_artifact_sha256 == proof.ordered_after_artifact_sha256
    assert proof.ordered_before_payload_sha256 == proof.ordered_after_payload_sha256
    assert proof.ordered_before_identity_ids == proof.ordered_after_identity_ids
    assert proof.before_cache_state_sha256 == proof.after_cache_state_sha256
    assert proof.mutable_global_write_count == 0
    assert proof.object_identity_used_as_proof is False
    assert canonical_json_bytes_v01(
        _e3_public_plain(bundle.source_context.baseline_g2d_execution_bundle)
    ) == e4_success_fixture["baseline_bytes"]


def test_e4_selective_result_against_plan_and_zero_operation_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    report = g2e.validate_selective_recomputation_result_against_plan_v01(
        bundle.recomputation_result,
        plan=bundle.recomputation_plan,
        source_context=bundle.source_context,
        delta_source_proposed_artifact=bundle.delta_source_proposed_artifact,
        delta_source_artifact=bundle.delta_source_artifact,
        dependency_graph_artifact=bundle.dependency_graph_artifact,
        affected_set_artifact=bundle.affected_set_artifact,
        invalidation_report_artifact=bundle.invalidation_report_artifact,
        plan_proposed_artifact=bundle.plan_proposed_artifact,
        plan_root_decision_input=bundle.plan_root_decision_input,
        plan_root_decision_result=bundle.plan_root_decision_result,
        plan_root_decision_artifact=bundle.plan_root_decision_artifact,
        plan_accepted_artifact=bundle.plan_accepted_artifact,
        recomputed_g2d_execution_bundle=bundle.recomputed_g2d_execution_bundle,
        recomputed_bindings=bundle.recomputed_bindings,
        preservation_proof=bundle.preservation_proof,
        preservation_proof_artifact=bundle.preservation_proof_artifact,
        g2e_transition_decisions=bundle.g2e_transition_decisions,
        g2e_causal_consumption_refs=bundle.g2e_causal_consumption_refs,
    )
    assert report.status == "PASS"
    result = bundle.recomputation_result
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
        assert getattr(result, field_name) == 0


def test_e4_final_root_accept_pair_t09_t10_and_anti_cycle_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    t09, t10 = bundle.g2e_transition_decisions[8:10]
    assert bundle.final_root_decision_result.decision == "ACCEPT"
    assert bundle.final_root_decision_result.selected_candidate_id == (
        bundle.recomputation_result.recomputation_result_id
    )
    assert bundle.final_root_decision_artifact.artifact_id.startswith(
        "g2e_root_final_decision_v01:"
    )
    final_root_payload = kernel_artifact_to_plain_dict_v01(
        bundle.final_root_decision_artifact
    )["payload"]
    final_root_plain = root_decision.root_decision_result_to_plain_dict_v01(
        bundle.final_root_decision_result
    )
    assert "transaction_id" not in final_root_payload
    assert bundle.final_root_decision_artifact.transaction_id == (
        final_root_plain["transaction_id"]
    )
    assert final_root_payload == {
        key: value
        for key, value in final_root_plain.items()
        if key != "transaction_id"
    }
    assert transition.validate_continuous_delta_transition_decision_v01(
        t09,
        registry=registry,
        source_artifact=bundle.recomputed_g2d_execution_bundle.report_artifact,
        target_artifact=bundle.final_root_decision_artifact,
    ) == ()
    assert transition.validate_continuous_delta_transition_decision_v01(
        t10,
        registry=registry,
        source_artifact=bundle.final_root_decision_artifact,
        target_artifact=bundle.runtime_report_artifact,
    ) == ()
    assert t10.decision_id not in bundle.runtime_trace.ordered_transition_decision_ids
    assert t10.decision_id not in bundle.runtime_report_artifact.trace_refs
    final_input_plain = root_decision.root_decision_input_to_plain_dict_v01(
        bundle.final_root_decision_input
    )
    assert final_input_plain["prior_root_state"]["prior_decision_id"] == (
        bundle.plan_root_decision_result.decision_id
    )


def test_e4_final_root_non_accept_matrix_fail_closed_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    outcomes = (
        "BLOCKED_FAIL_CLOSED",
        "NEEDS_USER",
        "NEEDS_MORE_EVIDENCE",
        "DEFER",
        "REJECT",
        "NO_UPDATE",
    )
    for outcome in outcomes:
        review = _e4_root_outcome(e4_success_fixture, phase="FINAL", outcome=outcome)
        assert review["result"].decision == outcome
        assert review["artifact"].artifact_id.startswith(
            "g2e_root_final_decision_v01:"
        )
        input_plain = root_decision.root_decision_input_to_plain_dict_v01(
            review["input"]
        )
        assert input_plain["prior_root_state"]["prior_decision_id"] == (
            e4_success_fixture["bundle"].plan_root_decision_result.decision_id
        )
        assert not review["result"].permission_created
        assert not review["result"].final_output_created
        assert not review["result"].effect_requested


def test_e4_trace_report_artifact_transition_and_causal_closure_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    transition_ids = tuple(item.decision_id for item in bundle.g2e_transition_decisions)
    assert len(transition_ids) == 10
    assert tuple(
        item.rule_id for item in bundle.g2e_transition_decisions
    ) == (
        "g2e_t01_delta_validate",
        "g2e_t02_affected_set_derive",
        "g2e_t03_invalidation_derive",
        "g2e_t04_plan_root_review",
        "g2e_t05_plan_root_accept",
        "g2e_t06_plan_root_reject",
        "g2e_t07_selective_recompute",
        "g2e_t08_recompute_block",
        "g2e_t09_parent_return",
        "g2e_t10_report_finalize",
    )
    assert bundle.runtime_trace.ordered_transition_decision_ids == transition_ids[:9]
    assert bundle.runtime_report.trace_id == bundle.runtime_trace.trace_id
    assert bundle.runtime_report_artifact.lifecycle_state == "FINALIZED"
    assert all(
        validate_causal_consumption_ref_v01(item) == ()
        for item in bundle.g2e_causal_consumption_refs
    )
    causal_plain = tuple(
        causal_consumption_ref_to_plain_dict_v01(item)
        for item in bundle.g2e_causal_consumption_refs
    )
    assert len(causal_plain) == len({canonical_json_bytes_v01(item) for item in causal_plain})


def test_e4_complete_execution_bundle_public_validation_v01(
    e4_success_fixture: dict[str, object],
) -> None:
    bundle = e4_success_fixture["bundle"]
    assert len(fields(g2e.ContinuousDeltaExecutionBundleV01)) == 36
    assert len(fields(g2d.FractalRuntimeExecutionBundleV02)) == 28
    assert g2e.validate_continuous_delta_execution_bundle_v01(bundle).status == "PASS"
    rebuilt = g2e.build_continuous_delta_execution_bundle_v01(
        **{field.name: getattr(bundle, field.name) for field in fields(type(bundle))}
    )
    assert rebuilt == bundle
    assert len(
        {
            item.artifact_id
            for item in (
                bundle.delta_source_proposed_artifact,
                bundle.delta_source_artifact,
                bundle.dependency_graph_artifact,
                bundle.affected_set_artifact,
                bundle.invalidation_report_artifact,
                bundle.plan_proposed_artifact,
                bundle.plan_accepted_artifact,
                bundle.preservation_proof_artifact,
                bundle.runtime_report_artifact,
            )
        }
    ) == 9


def test_e4_conditional_whole_run_escalation_and_selective_rejection_v01(
    e4_success_fixture: dict[str, object],
    e4_full_fractal_baseline_fixture: dict[str, object],
) -> None:
    strict_inputs = e4_success_fixture["inputs"]
    strict_plan = e4_success_fixture["plan"]
    baseline = strict_inputs["context"].baseline_g2d_execution_bundle
    full_inputs = _e4_input_family(
        e4_full_fractal_baseline_fixture,
        full_closure=True,
    )
    scope_proof = g2e._g2e4_classify_recomputation_scope_v01(
        baseline=baseline,
        baseline_source_artifacts=full_inputs["context"].baseline_source_artifacts,
        ordered_affected_artifact_ids=full_inputs["affected"].ordered_affected_ids,
    )
    assert scope_proof["classification"] == "FULL_CLOSURE"
    assert scope_proof["ordered_execution_rows"] == scope_proof["baseline_work_rows"]
    assert scope_proof["ordered_affected_cell_ids"] == tuple(
        item.cell_id for item in baseline.cell_inputs
    )
    assert scope_proof["ordered_execution_node_ids"] == (
        baseline.topology.ordered_node_ids
    )
    assert scope_proof["affected_queue_artifact_ids"] == tuple(
        item.artifact_id for item in baseline.queue_artifacts
    )
    assert scope_proof["affected_result_artifact_ids"] == tuple(
        item.artifact_id for item in baseline.result_artifacts
    )
    assert scope_proof["report_artifact_id"] == baseline.report_artifact.artifact_id
    bundle, report = g2e.run_continuous_delta_runtime_v01(
        source_context=full_inputs["context"],
        source_bindings=(full_inputs["source_binding"],),
        changed_field_bindings=(full_inputs["changed_field"],),
        changed_artifact_bindings=(full_inputs["changed_artifact"],),
        delta=full_inputs["delta"],
        dependency_edges=full_inputs["dependency_edges"],
        dependency_graph=full_inputs["graph"],
    )
    assert report.status == "PASS", report.reason_codes
    assert type(bundle) is g2e.ContinuousDeltaExecutionBundleV01
    full_plan = bundle.recomputation_plan
    assert full_plan == g2e.build_selective_recomputation_plan_from_affected_set_v01(
        delta=full_inputs["delta"],
        affected_set=full_inputs["affected"],
        invalidation_records=full_inputs["invalidation_records"],
        invalidation_report=full_inputs["invalidation_report"],
        source_context=full_inputs["context"],
        source_bindings=(full_inputs["source_binding"],),
        changed_field_bindings=(full_inputs["changed_field"],),
        changed_artifact_bindings=(full_inputs["changed_artifact"],),
        dependency_edges=full_inputs["dependency_edges"],
        dependency_graph=full_inputs["graph"],
    )
    whole_bundle = bundle.recomputed_g2d_execution_bundle
    context = whole_bundle.observed_work_context
    reason = "AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK"
    assert context is not None
    assert context.execution_scope == "WHOLE_RUN_ESCALATION"
    assert context.whole_run_escalation_reason == reason
    assert context.whole_run_escalation_policy_id is None
    binding_ids = tuple(
        item.artifact_id for item in context.ordered_binding_artifacts
    )
    assert binding_ids
    assert all(
        kernel_artifact_to_plain_dict_v01(item)["payload"]["execution"]
        == {
            "execution_scope": "WHOLE_RUN_ESCALATION",
            "whole_run_escalation_policy_id": None,
            "whole_run_escalation_reason": reason,
        }
        for item in context.ordered_binding_artifacts
    )
    initial_queue_artifacts = tuple(
        artifact
        for entry, artifact in zip(
            whole_bundle.queue_entries,
            whole_bundle.queue_artifacts,
            strict=True,
        )
        if entry.predecessor_queue_entry_id is None
    )
    assert set(binding_ids).issubset(
        {
            parent
            for artifact in initial_queue_artifacts
            for parent in artifact.parent_refs
        }
    )
    assert all(
        artifact.artifact_id in whole_bundle.runtime_trace.abi_artifact_refs
        for artifact in initial_queue_artifacts
    )
    assert whole_bundle.runtime_trace.trace_id == whole_bundle.runtime_report.runtime_trace_id
    assert whole_bundle.runtime_trace.trace_id in whole_bundle.report_artifact.trace_refs
    report_payload = kernel_artifact_to_plain_dict_v01(
        whole_bundle.report_artifact
    )["payload"]
    assert report_payload["report_id"] == whole_bundle.runtime_report.report_id
    assert whole_bundle.report_artifact.parent_refs == (
        whole_bundle.topology_artifact.artifact_id,
        *(item.artifact_id for item in whole_bundle.result_artifacts),
    )
    assert any(
        whole_bundle.runtime_trace.trace_id in item.trace_refs
        for item in whole_bundle.causal_consumption_refs
    )
    assert whole_bundle.source_context == baseline.source_context
    assert whole_bundle.source_binding == baseline.source_binding
    assert whole_bundle.topology_seed == baseline.topology_seed
    assert whole_bundle.topology_nodes == baseline.topology_nodes
    assert whole_bundle.topology_edges == baseline.topology_edges
    assert whole_bundle.runtime_assignments == baseline.runtime_assignments
    assert whole_bundle.topology == baseline.topology
    assert whole_bundle.topology_artifact == baseline.topology_artifact
    assert g2d.validate_fractal_runtime_execution_bundle_v02(whole_bundle).status == "PASS"

    selective_bundle, selective_report = g2e.execute_selective_recomputation_v01(
        plan=full_plan,
        source_context=strict_inputs["context"],
        source_bindings=(strict_inputs["source_binding"],),
        changed_field_bindings=(strict_inputs["changed_field"],),
        changed_artifact_bindings=(strict_inputs["changed_artifact"],),
        delta=strict_inputs["delta"],
        dependency_edges=strict_inputs["dependency_edges"],
        dependency_graph=strict_inputs["graph"],
        affected_request=strict_inputs["request"],
        affected_result=strict_inputs["affected"],
        invalidation_records=strict_inputs["invalidation_records"],
        invalidation_report=strict_inputs["invalidation_report"],
    )
    assert selective_bundle is None
    assert selective_report.status == "FAIL_CLOSED"

    with pytest.raises(ValueError):
        g2e._g2e4_observed_work_context_v01(
            plan=full_plan,
            source_context=full_inputs["context"],
            source_bindings=(full_inputs["source_binding"],),
            changed_field_bindings=(full_inputs["changed_field"],),
            changed_artifact_bindings=(full_inputs["changed_artifact"],),
            execution_scope="SELECTIVE",
        )
    with pytest.raises(ValueError):
        g2e._g2e4_observed_work_context_v01(
            plan=strict_plan,
            source_context=strict_inputs["context"],
            source_bindings=(strict_inputs["source_binding"],),
            changed_field_bindings=(strict_inputs["changed_field"],),
            changed_artifact_bindings=(strict_inputs["changed_artifact"],),
            execution_scope="WHOLE_RUN_ESCALATION",
            whole_run_escalation_reason=reason,
            whole_run_escalation_policy_id=None,
        )
    for substituted_reason, substituted_policy in (
        ("POLICY_SELECTED_WHOLE_RUN", "policy:unapproved"),
        ("AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK", "policy:unapproved"),
    ):
        with pytest.raises(ValueError):
            g2e._g2e4_observed_work_context_v01(
                plan=full_plan,
                source_context=full_inputs["context"],
                source_bindings=(full_inputs["source_binding"],),
                changed_field_bindings=(full_inputs["changed_field"],),
                changed_artifact_bindings=(full_inputs["changed_artifact"],),
                execution_scope="WHOLE_RUN_ESCALATION",
                whole_run_escalation_reason=substituted_reason,
                whole_run_escalation_policy_id=substituted_policy,
            )

    full_rows = scope_proof["baseline_work_rows"]
    projection_coverage: list[
        tuple[int, tuple[tuple[str, str], ...], str, dict[str, object]]
    ] = []
    full_projections = e4_full_fractal_baseline_fixture[
        "full_seed_projections"
    ]
    for projection_index, _projection in enumerate(full_projections):
        candidate_fixture = {
            **e4_full_fractal_baseline_fixture,
            "full_seed_projections": tuple(
                item
                for index, item in enumerate(full_projections)
                if index != projection_index
            ),
        }
        candidate_inputs = _e4_input_family(candidate_fixture, full_closure=True)
        try:
            candidate_proof = g2e._g2e4_classify_recomputation_scope_v01(
                baseline=baseline,
                baseline_source_artifacts=(
                    candidate_inputs["context"].baseline_source_artifacts
                ),
                ordered_affected_artifact_ids=(
                    candidate_inputs["affected"].ordered_affected_ids
                ),
            )
            candidate_rows = candidate_proof["ordered_execution_rows"]
            candidate_classification = candidate_proof["classification"]
        except ValueError:
            candidate_rows = ()
            candidate_classification = "INVALID"
        uniquely_supported_rows = tuple(
            row for row in full_rows if row not in set(candidate_rows)
        )
        projection_coverage.append(
            (
                projection_index,
                uniquely_supported_rows,
                candidate_classification,
                candidate_inputs,
            )
        )
    assert len(projection_coverage) == len(full_projections)
    selected_omission = next(
        row for row in projection_coverage if row[1]
    )
    _omitted_index, missing_rows, partial_classification, partial_inputs = (
        selected_omission
    )
    assert missing_rows[0] in full_rows
    assert partial_classification in {"STRICT_SUBSET", "INVALID"}
    assert partial_classification != "FULL_CLOSURE"
    partial_bundle, partial_report = g2e.execute_selective_recomputation_v01(
        plan=full_plan,
        source_context=partial_inputs["context"],
        source_bindings=(partial_inputs["source_binding"],),
        changed_field_bindings=(partial_inputs["changed_field"],),
        changed_artifact_bindings=(partial_inputs["changed_artifact"],),
        delta=partial_inputs["delta"],
        dependency_edges=partial_inputs["dependency_edges"],
        dependency_graph=partial_inputs["graph"],
        affected_request=partial_inputs["request"],
        affected_result=partial_inputs["affected"],
        invalidation_records=partial_inputs["invalidation_records"],
        invalidation_report=partial_inputs["invalidation_report"],
    )
    assert partial_bundle is None
    assert partial_report.status == "FAIL_CLOSED"
    foreign_runtime_artifact = _e3_kernel_artifact(
        artifact_id="artifact:g2e:e4:foreign-runtime-work",
        transaction_id=baseline.source_context.router_input.transaction_id,
        payload={"foreign_runtime_work": True},
    )
    foreign_fixture = {
        **e4_full_fractal_baseline_fixture,
        "full_seed_projections": (
            *e4_full_fractal_baseline_fixture["full_seed_projections"],
            _e4_runtime_artifact_projection(foreign_runtime_artifact),
        ),
    }
    foreign_inputs = _e4_input_family(foreign_fixture, full_closure=True)
    foreign_bundle, foreign_report = g2e.execute_selective_recomputation_v01(
        plan=full_plan,
        source_context=foreign_inputs["context"],
        source_bindings=(foreign_inputs["source_binding"],),
        changed_field_bindings=(foreign_inputs["changed_field"],),
        changed_artifact_bindings=(foreign_inputs["changed_artifact"],),
        delta=foreign_inputs["delta"],
        dependency_edges=foreign_inputs["dependency_edges"],
        dependency_graph=foreign_inputs["graph"],
        affected_request=foreign_inputs["request"],
        affected_result=foreign_inputs["affected"],
        invalidation_records=foreign_inputs["invalidation_records"],
        invalidation_report=foreign_inputs["invalidation_report"],
    )
    assert foreign_bundle is None
    assert foreign_report.status == "FAIL_CLOSED"
    forged_plan = replace(
        full_plan,
        ordered_affected_cell_ids=full_plan.ordered_affected_cell_ids[:-1],
    )
    forged_bundle, forged_report = g2e.execute_selective_recomputation_v01(
        plan=forged_plan,
        source_context=full_inputs["context"],
        source_bindings=(full_inputs["source_binding"],),
        changed_field_bindings=(full_inputs["changed_field"],),
        delta=full_inputs["delta"],
        changed_artifact_bindings=(full_inputs["changed_artifact"],),
        dependency_edges=full_inputs["dependency_edges"],
        dependency_graph=full_inputs["graph"],
        affected_request=full_inputs["request"],
        affected_result=full_inputs["affected"],
        invalidation_records=full_inputs["invalidation_records"],
        invalidation_report=full_inputs["invalidation_report"],
    )
    assert forged_bundle is None
    assert forged_report.status == "FAIL_CLOSED"


def test_e4_no_private_g2d_lower_mutation_e5_or_e6_surface_v01() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )
    assert not any("tests" in name or "demo" in name for name in imports)
    g2d_private_refs = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "g2d_runtime"
        and node.attr.startswith("_")
    }
    assert g2d_private_refs == set()
    assert "PlanGraph" not in source
    assert "E5" not in source and "E6" not in source
    assert "living_gauntlet" not in source and "kernel_conformance" not in source
    assert source.count("g2d_runtime.run_fractal_runtime_v02") == 1
    assert len(g2e.PUBLIC_G2E_REASON_CODES_V01) == 88
    assert len(g2e.VALIDATION_TARGETS_V01) == 32
    assert len(g2e.FAILURE_STAGES_V01) == 24
    assert hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest() == (
        "6d2d2c8756ebf261724742ad14294094ee9ce04a28c0498b264164ec585d11f2"
    )
