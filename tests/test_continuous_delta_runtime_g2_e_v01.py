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
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/continuous_delta_runtime_v01.py"
SCHEMA_PATH = ROOT / "schemas/continuous_delta_runtime_v01.schema.json"
PREFLIGHT_PATH = ROOT / "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md"

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
    assert public_functions == QUARTET_FUNCTIONS
    assert g2e.__all__ == TYPE_NAMES + QUARTET_FUNCTIONS
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
    assert not hasattr(g2e, "build_dependency_fingerprint_v01")


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
        "project_integrity_replay_dependency_edges_v01",
        "compute_affected_set_v01",
        "derive_invalidation_report_v01",
        "prove_unaffected_artifact_preservation_v01",
        "execute_selective_recomputation_v01",
        "run_continuous_delta_runtime_v01",
        "build_continuous_delta_transition_registry_profile_v01",
    )
    assert all(not hasattr(g2e, name) for name in forbidden)
