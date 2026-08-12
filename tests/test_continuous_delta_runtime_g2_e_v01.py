from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path
import re
import types
from typing import get_args, get_origin, get_type_hints

from jsonschema import Draft202012Validator, ValidationError
import pytest

import hedgehog.kernel as kernel
import hedgehog.kernel.continuous_delta_runtime_v01 as g2e
import hedgehog.kernel.transition_registry_v01 as transition
from hedgehog.kernel.abi_v01 import (
    build_kernel_artifact_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
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
    "b3a6c9c7b3687f18bd3c6739c096e7486a4f6505dc9dd49ecc5e1ecd8a4a49f1"
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
    assert public_functions == QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert g2e.__all__ == TYPE_NAMES + QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert len(g2e.PUBLIC_G2E_REASON_CODES_V01) == 88
    assert len(g2e.VALIDATION_TARGETS_V01) == 32
    assert len(g2e.FAILURE_STAGES_V01) == 24
    assert g2e.VALIDATION_STATUSES_V01 == ("PASS", "FAIL_CLOSED")
    assert not imports.intersection(
        {"os", "pathlib", "time", "random", "socket", "requests", "subprocess"}
    )
    assert not any("tests" in item or "demo" in item for item in imports)
    assert not hasattr(kernel, "WorldStateDeltaV01")
    global_names = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    assert not any("CACHE" in name for name in global_names)


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
    assert not hasattr(g2e, "build_continuous_delta_source_context_v01")
    assert not hasattr(g2e, "validate_continuous_delta_source_context_v01")
    assert not hasattr(g2e, "build_continuous_delta_execution_bundle_v01")
    assert not hasattr(g2e, "validate_continuous_delta_execution_bundle_v01")


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
    forbidden = (
        "derive_invalidation_report_v01",
        "prove_unaffected_artifact_preservation_v01",
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
        "build_continuous_delta_transition_registry_profile_v01",
    )
    assert all(not hasattr(g2e, name) for name in forbidden)


def test_e2_exact_public_surface_and_slice_boundary_v01() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    assert len(E2_QUARTET_FUNCTIONS) == 16
    assert len(E2_BEHAVIORAL_FUNCTIONS) == 5
    assert public_functions == QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert len(public_functions) == 45
    assert g2e.__all__ == TYPE_NAMES + QUARTET_FUNCTIONS + E2_PUBLIC_FUNCTIONS
    assert len(g2e.__all__) == 65
    assert g2e.CONTINUOUS_DELTA_GRAPH_VERSION_V01 == "v0.1"
    assert g2e.MAX_DEPENDENCY_GRAPH_NODES_V01 == 256
    assert g2e.MAX_DEPENDENCY_GRAPH_EDGES_V01 == 1024
    assert g2e.MAX_AFFECTED_HOPS_V01 == 32
    for name in (
        "derive_invalidation_report_v01",
        "prove_unaffected_artifact_preservation_v01",
        "build_continuous_delta_source_context_v01",
        "build_selective_recomputation_plan_from_affected_set_v01",
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
    ):
        assert not hasattr(g2e, name)
    assert "source_context" not in inspect.signature(
        g2e.compute_affected_set_v01
    ).parameters
    assert "source_context" not in inspect.signature(
        g2e.validate_affected_set_against_graph_v01
    ).parameters
    addendum_text = ADDENDUM_PATH.read_text(encoding="utf-8")
    assert "document_revision: v0.1.1" in addendum_text
    assert "guardian_review_status: ACCEPTED" in addendum_text
    assert "PENDING_REVIEW" not in addendum_text
    assert hashlib.sha256(ADDENDUM_PATH.read_bytes()).hexdigest() == (
        ACCEPTED_ADDENDUM_SHA256
    )
    assert "g2e2_repair_authorized: false" in addendum_text
    assert "g2e2_repair_started: false" in addendum_text
    assert "does not self-authorize repair" in addendum_text
    assert "Only separate owner repair\nauthorization may resume G2-E2" in (
        addendum_text
    )


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
        "build_continuous_delta_source_context_v01",
        "validate_continuous_delta_source_context_v01",
        "derive_invalidation_report_v01",
        "prove_unaffected_artifact_preservation_v01",
        "build_selective_recomputation_plan_from_affected_set_v01",
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
    }
    assert not public_functions.intersection(forbidden)
    assert not hasattr(kernel, "DeltaDependencyEdgeV01")
    assert "hedgehog.kernel.fractal_runtime_v02 import (" not in source
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
    forbidden_execution_seams = {
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
        "_d4_run_runtime_v02",
    }
    assert not defined_names.intersection(forbidden_execution_seams)
    assert not called_names.intersection(forbidden_execution_seams)
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
    assert not any(
        name.startswith("run_") or "runner" in name for name in called_names
    )
    assert not called_names.intersection(
        {"provider_call", "model_call", "network_call", "connector_call"}
    )
