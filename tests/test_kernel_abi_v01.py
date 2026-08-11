from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
import pytest

import hedgehog.kernel as kernel
import hedgehog.kernel.abi_v01 as abi
from demo.run_living_gauntlet_v01 import (
    _build_causal_consumption_fixture_v01,
    _build_kernel_abi_fixture_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY_ROOT / "schemas/kernel_artifact_v01.schema.json"
MODULE_PATH = REPOSITORY_ROOT / "hedgehog/kernel/abi_v01.py"

COMMITTED_ALL = (
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

PUBLIC_FUNCTIONS = (
    "build_kernel_artifact_v01",
    "validate_kernel_artifact_v01",
    "validate_kernel_artifact_bundle_v01",
    "kernel_artifact_to_plain_dict_v01",
    "kernel_artifacts_to_plain_list_v01",
    "kernel_artifact_to_canonical_ref_v01",
    "build_causal_consumption_ref_v01",
    "validate_causal_consumption_ref_v01",
    "validate_causal_consumption_bundle_v01",
    "validate_causal_counterfactual_v01",
    "causal_consumption_ref_to_plain_dict_v01",
    "causal_consumption_refs_to_plain_list_v01",
)
ACTION_PACKET_PUBLIC_FUNCTIONS = (
    "build_action_packet_lifecycle_profile_v01",
    "validate_action_packet_lifecycle_profile_v01",
    "action_packet_lifecycle_profile_to_plain_dict_v01",
)

ARTIFACT_FIELDS = (
    "abi_version",
    "artifact_id",
    "artifact_type",
    "schema_version",
    "transaction_id",
    "owner_root_id",
    "source_component",
    "authority_class",
    "lifecycle_state",
    "payload",
    "trace_refs",
    "parent_refs",
    "time_envelope",
)

CAUSAL_FIELDS = (
    "producer_actor_id",
    "source_artifact_id",
    "output_field",
    "consumer_component",
    "downstream_artifact_id",
    "decision_effect",
    "disposition",
    "reason_code",
    "trace_refs",
)


def _time_envelope(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "pt_created_at": "2026-01-01T00:00:00+00:00",
        "kt_asof": "2026-01-01T00:00:00+00:00",
        "et_observed_at": None,
        "ct_session_anchor": "session:test:abi:001",
        "ttl_seconds": 3600,
        "freshness_class": "static",
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_to": "2026-01-01T01:00:00+00:00",
    }
    value.update(overrides)
    return value


def _artifact(**overrides: object) -> abi.KernelArtifactV01:
    values: dict[str, object] = {
        "abi_version": "v1.0",
        "artifact_id": "artifact:test:abi:001",
        "artifact_type": "SemanticEvidence",
        "schema_version": "v1",
        "transaction_id": "txn:test:abi:001",
        "owner_root_id": "root:alpha",
        "source_component": "deterministic_runtime",
        "authority_class": "EVIDENCE_ONLY",
        "lifecycle_state": "VALIDATED",
        "payload": {"value": {"items": [1, True, None]}},
        "trace_refs": ("trace:test:abi:001",),
        "parent_refs": (),
        "time_envelope": _time_envelope(),
    }
    values.update(overrides)
    return abi.build_kernel_artifact_v01(**values)


def _rebuild_artifact(
    artifact: abi.KernelArtifactV01, **overrides: object
) -> abi.KernelArtifactV01:
    values = abi.kernel_artifact_to_plain_dict_v01(artifact)
    values.update(overrides)
    if "trace_refs" not in overrides:
        values["trace_refs"] = tuple(values["trace_refs"])
    if "parent_refs" not in overrides:
        values["parent_refs"] = tuple(values["parent_refs"])
    return abi.build_kernel_artifact_v01(**values)


def _causal_ref(**overrides: object) -> abi.CausalConsumptionRefV01:
    values: dict[str, object] = {
        "producer_actor_id": "actor:test:001",
        "source_artifact_id": "artifact:test:source",
        "output_field": "/value",
        "consumer_component": "deterministic_runtime",
        "downstream_artifact_id": "artifact:test:downstream",
        "decision_effect": "effect:test:projection",
        "disposition": "USED",
        "reason_code": "used:projection",
        "trace_refs": ("trace:test:causal:001",),
    }
    values.update(overrides)
    return abi.build_causal_consumption_ref_v01(**values)


def _schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _contains_tuple_or_private(value: object) -> bool:
    if isinstance(value, tuple) or type(value).__name__ == "_FrozenJSONObject":
        return True
    if isinstance(value, list):
        return any(_contains_tuple_or_private(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_tuple_or_private(item) for item in value.values())
    return False


class StatefulMapping(Mapping[str, object]):
    def __init__(self) -> None:
        self.items_calls = 0

    def __getitem__(self, key: str) -> object:
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self) -> int:
        return 1

    def items(self):
        self.items_calls += 1
        return (("value", self.items_calls),)


class RowsMapping(Mapping[str, object]):
    def __init__(self, rows: object) -> None:
        self.rows = rows

    def __getitem__(self, key: str) -> object:
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self) -> int:
        return 1

    def items(self):
        return self.rows


class RaisingMapping(RowsMapping):
    def items(self):
        raise OSError("CALLER_PAYLOAD_SECRET")


class StringSubclass(str):
    pass


class CallerException(Exception):
    pass


class HostileIdentity:
    def __eq__(self, other: object) -> bool:
        raise RuntimeError("CALLER_EQUALITY_SECRET")

    def __hash__(self) -> int:
        raise CallerException("CALLER_HASH_SECRET")


class CustomRaisingMapping(RowsMapping):
    def items(self):
        raise CallerException("CALLER_MAPPING_SECRET")


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("MODULE_ID", "kernel_abi_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1b2"),
        ("KERNEL_ABI_VERSION", "v1.0"),
        ("KERNEL_ABI_MAJOR_VERSION", 1),
        ("KERNEL_ABI_MINOR_VERSION", 0),
        ("SUPPORTED_ABI_VERSIONS", ("v1.0",)),
        ("STATUS_PASS", "PASS"),
        ("STATUS_BLOCKED_FAIL_CLOSED", "BLOCKED_FAIL_CLOSED"),
    ),
)
def test_module_identity(name: str, value: object) -> None:
    assert getattr(abi, name) == value


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        (
            "AUTHORITY_CLASSES",
            ("ROOT_OWNED", "ROOT_AUTHORIZED", "ADVISORY", "EVIDENCE_ONLY", "NON_AUTHORITY"),
        ),
        (
            "LIFECYCLE_STATES",
            (
                "PROPOSED",
                "VALIDATED",
                "ROOT_REVIEWED",
                "ROOT_ACCEPTED",
                "ROOT_REJECTED",
                "BLOCKED_FAIL_CLOSED",
                "EXECUTED_MOCK",
                "RECEIPT_RECORDED",
                "FINALIZED",
            ),
        ),
        (
            "ARTIFACT_TYPES",
            (
                "OrchestratorRouteProposal",
                "RootAcceptedRoute",
                "BSEPPacket",
                "BSEPProjection",
                "SemanticArchitectProposal",
                "RuntimeExecutionTopology",
                "ActorContribution",
                "SemanticEvidence",
                "ValidatedEvidence",
                "ResultProposal",
                "PostVVReport",
                "GTAdvisoryReport",
                "RootOwnedIntent",
                "RootDecision",
                "ExecutionRequest",
                "EvidenceReceipt",
                "RootFinal",
                "CrossRootEvidenceRef",
                "TransactionOutcomeEnvelope",
                "CausalConsumptionRef",
                "ExecutionModeProposal",
                "RootExecutionModeDecision",
                "ExecutionModeRouteEligibility",
                "FractalCellQueueEntry",
                "FractalCellResult",
                "FractalRuntimeReport",
                "ContinuousDeltaSource",
                "DependencyGraphIndex",
                "AffectedSetResult",
                "ArtifactInvalidationReport",
                "PreservationProof",
                "SelectiveRecomputationPlan",
                "ContinuousDeltaRuntimeReport",
            ),
        ),
        (
            "CAUSAL_DISPOSITIONS",
            ("USED", "REJECTED", "IGNORED_WITH_REASON", "BLOCKED_BY_GATE"),
        ),
    ),
)
def test_exact_constant_tuples(name: str, expected: tuple[str, ...]) -> None:
    value = getattr(abi, name)
    assert type(value) is tuple
    assert value == expected


@pytest.mark.parametrize(
    ("record", "expected_fields"),
    ((abi.KernelArtifactV01, ARTIFACT_FIELDS), (abi.CausalConsumptionRefV01, CAUSAL_FIELDS)),
)
def test_exact_frozen_dataclass_surfaces(record: type, expected_fields: tuple[str, ...]) -> None:
    assert is_dataclass(record)
    assert record.__dataclass_params__.frozen is True
    assert tuple(field.name for field in fields(record)) == expected_fields


def test_exact_public_function_surface() -> None:
    actual = tuple(
        name
        for name, value in vars(abi).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == abi.__name__
    )
    assert actual == (
        *ACTION_PACKET_PUBLIC_FUNCTIONS,
        *PUBLIC_FUNCTIONS,
    )


@pytest.mark.parametrize("name", ("KernelArtifactV01", "CausalConsumptionRefV01", *PUBLIC_FUNCTIONS))
def test_package_direct_attributes(name: str) -> None:
    assert getattr(kernel, name) is getattr(abi, name)


def test_package_all_remains_accepted_legacy_surface() -> None:
    assert kernel.__all__ == COMMITTED_ALL
    assert not set(PUBLIC_FUNCTIONS).intersection(kernel.__all__)


def test_action_packet_lifecycle_profile_is_explicit_and_exact() -> None:
    profile = abi.build_action_packet_lifecycle_profile_v01()
    assert tuple(field.name for field in fields(type(profile))) == (
        "profile_id",
        "abi_family",
        "transition_registry_family",
        "lifecycle_states",
    )
    assert profile.profile_id == "action_packet_lifecycle_profile_v01"
    assert profile.abi_family == "hedgehog_kernel_abi"
    assert profile.transition_registry_family == "TransitionRegistryV01"
    assert profile.lifecycle_states == (
        "CREATED",
        "ROOT_AUTHORIZED",
        "QUEUED",
        "PENDING_FULFILLMENT",
        "FULFILLED_MOCK",
        "RECEIPT_RECEIVED",
        "FAILED",
        "BLOCKED",
        "EXPIRED",
        "REVOKED",
        "SUPERSEDED",
    )
    assert abi.validate_action_packet_lifecycle_profile_v01(profile) == ()
    assert abi.action_packet_lifecycle_profile_to_plain_dict_v01(profile) == {
        "profile_id": "action_packet_lifecycle_profile_v01",
        "abi_family": "hedgehog_kernel_abi",
        "transition_registry_family": "TransitionRegistryV01",
        "lifecycle_states": list(profile.lifecycle_states),
    }


@pytest.mark.parametrize(
    "lifecycle_states",
    (
        list(abi.ACTION_PACKET_LIFECYCLE_STATES_V01),
        tuple(reversed(abi.ACTION_PACKET_LIFECYCLE_STATES_V01)),
        abi.ACTION_PACKET_LIFECYCLE_STATES_V01[:-1],
        (*abi.ACTION_PACKET_LIFECYCLE_STATES_V01, "UNKNOWN"),
        (
            "PROPOSED",
            *abi.ACTION_PACKET_LIFECYCLE_STATES_V01[1:],
        ),
        (
            abi.ACTION_PACKET_LIFECYCLE_STATES_V01[0],
            *abi.ACTION_PACKET_LIFECYCLE_STATES_V01,
        ),
    ),
)
def test_action_packet_lifecycle_profile_rejects_state_drift(
    lifecycle_states: object,
) -> None:
    profile = abi.build_action_packet_lifecycle_profile_v01()
    forged = replace(profile, lifecycle_states=lifecycle_states)
    assert abi.validate_action_packet_lifecycle_profile_v01(forged)


def test_action_packet_lifecycle_profile_validator_is_total() -> None:
    class EqualString(str):
        def __eq__(self, other: object) -> bool:
            return True

    profile = abi.build_action_packet_lifecycle_profile_v01()
    malformed = (
        None,
        object(),
        replace(profile, profile_id=EqualString(profile.profile_id)),
        replace(
            profile,
            lifecycle_states=(
                EqualString("CREATED"),
                *profile.lifecycle_states[1:],
            ),
        ),
    )
    for value in malformed:
        errors = abi.validate_action_packet_lifecycle_profile_v01(value)
        assert errors
        assert all(type(reason) is str and reason for reason in errors)


def test_legacy_abi_vector_remains_exact() -> None:
    assert abi.KERNEL_ABI_VERSION == "v1.0"
    assert abi.KERNEL_ABI_MAJOR_VERSION == 1
    assert abi.KERNEL_ABI_MINOR_VERSION == 0
    assert abi.SUPPORTED_ABI_VERSIONS == ("v1.0",)
    assert abi.LIFECYCLE_STATES == (
        "PROPOSED",
        "VALIDATED",
        "ROOT_REVIEWED",
        "ROOT_ACCEPTED",
        "ROOT_REJECTED",
        "BLOCKED_FAIL_CLOSED",
        "EXECUTED_MOCK",
        "RECEIPT_RECORDED",
        "FINALIZED",
    )
    assert tuple(field.name for field in fields(abi.KernelArtifactV01)) == (
        "abi_version",
        "artifact_id",
        "artifact_type",
        "schema_version",
        "transaction_id",
        "owner_root_id",
        "source_component",
        "authority_class",
        "lifecycle_state",
        "payload",
        "trace_refs",
        "parent_refs",
        "time_envelope",
    )
    artifact = _artifact()
    assert abi.validate_kernel_artifact_v01(artifact) == ()
    assert canonical_json_bytes_v01(
        abi.kernel_artifact_to_plain_dict_v01(artifact)
    ) == canonical_json_bytes_v01(
        abi.kernel_artifact_to_plain_dict_v01(_artifact())
    )


@pytest.mark.parametrize(
    ("value", "reason"),
    (
        (None, "abi_version_invalid"),
        (StringSubclass("v1.0"), "abi_version_invalid"),
        ("", "abi_version_invalid"),
        ("v1", "abi_version_invalid"),
        ("1.0", "abi_version_invalid"),
        ("v-1.0", "abi_version_invalid"),
        ("v2.0", "abi_major_version_unknown"),
        ("v1.1", "abi_minor_version_unsupported"),
        ("v999999999999999999999.0", "abi_major_version_unknown"),
    ),
)
def test_abi_version_matrix(value: object, reason: str) -> None:
    with pytest.raises(ValueError, match=f"^{reason}$") as caught:
        _artifact(abi_version=value)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("artifact_type", abi.ARTIFACT_TYPES)
def test_all_artifact_families_construct_and_validate(artifact_type: str) -> None:
    artifact = _artifact(artifact_type=artifact_type)
    assert abi.validate_kernel_artifact_v01(artifact) == ()


@pytest.mark.parametrize("authority_class", abi.AUTHORITY_CLASSES)
@pytest.mark.parametrize("lifecycle_state", abi.LIFECYCLE_STATES)
def test_authority_and_lifecycle_are_independent(
    authority_class: str, lifecycle_state: str
) -> None:
    artifact = _artifact(
        authority_class=authority_class, lifecycle_state=lifecycle_state
    )
    assert artifact.authority_class == authority_class
    assert artifact.lifecycle_state == lifecycle_state
    assert abi.validate_kernel_artifact_v01(artifact) == ()


@pytest.mark.parametrize(
    "payload",
    (
        None,
        True,
        False,
        0,
        1.25,
        "unicode-value",
        [],
        [1, {"nested": [False]}],
        {},
        {"nested": {"array": [1, 2]}},
    ),
)
def test_json_payload_positive_matrix(payload: object) -> None:
    artifact = _artifact(payload=payload)
    assert abi.validate_kernel_artifact_v01(artifact) == ()


@pytest.mark.parametrize(
    "field",
    ("artifact_id", "transaction_id", "owner_root_id", "source_component"),
)
@pytest.mark.parametrize("bad_value", (None, "", StringSubclass("value"), "\ud800"))
def test_identifier_rejection_matrix(field: str, bad_value: object) -> None:
    expected = {
        "artifact_id": "artifact_id_invalid",
        "transaction_id": "transaction_id_invalid",
        "owner_root_id": "owner_root_id_invalid",
        "source_component": "source_component_invalid",
    }[field]
    with pytest.raises(ValueError, match=f"^{expected}$"):
        _artifact(**{field: bad_value})


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("artifact_type", "UnknownArtifact", "artifact_type_unknown"),
        ("artifact_type", StringSubclass("SemanticEvidence"), "artifact_type_unknown"),
        ("schema_version", "1", "schema_version_invalid"),
        ("schema_version", "v1.", "schema_version_invalid"),
        ("authority_class", "ROOT", "authority_class_unknown"),
        ("lifecycle_state", "REVOKED", "lifecycle_state_unknown"),
    ),
)
def test_enum_and_schema_rejection(field: str, value: object, reason: str) -> None:
    with pytest.raises(ValueError, match=f"^{reason}$"):
        _artifact(**{field: value})


@pytest.mark.parametrize("reserved", ARTIFACT_FIELDS)
def test_every_envelope_field_is_reserved_in_payload(reserved: str) -> None:
    with pytest.raises(ValueError, match="^payload_reserved_field$"):
        _artifact(payload={reserved: "override"})


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("trace_refs", [], "trace_refs_invalid"),
        ("trace_refs", (), "trace_refs_invalid"),
        ("trace_refs", ("",), "trace_refs_invalid"),
        ("trace_refs", ("trace:a", "trace:a"), "trace_refs_invalid"),
        ("trace_refs", (StringSubclass("trace:a"),), "trace_refs_invalid"),
        ("parent_refs", [], "parent_refs_invalid"),
        ("parent_refs", ("",), "parent_refs_invalid"),
        ("parent_refs", ("parent:a", "parent:a"), "parent_refs_invalid"),
        ("parent_refs", (StringSubclass("parent:a"),), "parent_refs_invalid"),
        ("parent_refs", ("artifact:test:abi:001",), "parent_refs_invalid"),
    ),
)
def test_trace_and_parent_ref_rejections(field: str, value: object, reason: str) -> None:
    with pytest.raises(ValueError, match=f"^{reason}$"):
        _artifact(**{field: value})


@pytest.mark.parametrize("freshness", ("static", "slow_changing", "normal", "fast_changing", "real_time"))
def test_all_time_freshness_classes(freshness: str) -> None:
    assert _artifact(time_envelope=_time_envelope(freshness_class=freshness))


@pytest.mark.parametrize(
    "overrides",
    (
        {"et_observed_at": "2026-01-01T00:30:00+00:00"},
        {"valid_from": None},
        {"valid_to": None},
        {"ttl_seconds": 0},
    ),
)
def test_time_envelope_optional_and_boundary_values(overrides: dict[str, object]) -> None:
    assert _artifact(time_envelope=_time_envelope(**overrides))


@pytest.mark.parametrize(
    "missing",
    (
        "pt_created_at",
        "kt_asof",
        "et_observed_at",
        "ct_session_anchor",
        "ttl_seconds",
        "freshness_class",
        "valid_from",
        "valid_to",
    ),
)
def test_time_envelope_requires_every_field(missing: str) -> None:
    value = _time_envelope()
    del value[missing]
    with pytest.raises(ValueError, match="^time_envelope_invalid$"):
        _artifact(time_envelope=value)


@pytest.mark.parametrize(
    "value",
    (
        {**_time_envelope(), "extra": True},
        _time_envelope(pt_created_at="2026-01-01T00:00:00"),
        _time_envelope(kt_asof="not-time"),
        _time_envelope(ttl_seconds=True),
        _time_envelope(ttl_seconds=-1),
        _time_envelope(freshness_class="unknown"),
        _time_envelope(valid_from="2026-01-02T00:00:00+00:00"),
        RaisingMapping(()),
    ),
)
def test_time_envelope_negative_matrix(value: object) -> None:
    with pytest.raises(ValueError, match="^time_envelope_invalid$") as caught:
        _artifact(time_envelope=value)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize(
    "payload",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
        b"bytes",
        bytearray(b"bytes"),
        memoryview(b"bytes"),
        {"set": {1}},
        frozenset({1}),
        object(),
        RowsMapping((("a", 1), ("a", 2))),
        RowsMapping((("a", 1, 2),)),
        RaisingMapping(()),
    ),
)
def test_payload_negative_matrix(payload: object) -> None:
    with pytest.raises(ValueError, match="^payload_invalid$") as caught:
        _artifact(payload=payload)
    assert caught.value.__cause__ is None
    assert "CALLER_PAYLOAD_SECRET" not in str(caught.value)


@pytest.mark.parametrize("payload", (RaisingMapping(()), CustomRaisingMapping(())))
def test_mapping_exceptions_are_sanitized(payload: object) -> None:
    with pytest.raises(ValueError, match="^payload_invalid$") as caught:
        _artifact(payload=payload)
    assert caught.value.__cause__ is None
    assert "SECRET" not in str(caught.value)


def test_payload_mapping_consumed_once_and_snapshot_owned() -> None:
    payload = StatefulMapping()
    artifact = _artifact(payload=payload)
    assert payload.items_calls == 1
    assert abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"] == {"value": 1}


def test_payload_caller_mutation_isolated() -> None:
    nested = [1, {"state": "before"}]
    payload = {"nested": nested}
    artifact = _artifact(payload=payload)
    nested[1]["state"] = "after"
    payload["extra"] = True
    assert abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"] == {
        "nested": [1, {"state": "before"}]
    }


def test_payload_cycle_rejected() -> None:
    value: list[object] = []
    value.append(value)
    with pytest.raises(ValueError, match="^payload_invalid$"):
        _artifact(payload=value)


@pytest.mark.parametrize(
    "forged",
    (
        abi._FrozenJSONObject((("b", 1), ("a", 2))),
        abi._FrozenJSONObject((("a", 1), ("a", 2))),
        abi._FrozenJSONObject([("a", 1)]),
        abi._FrozenJSONObject(((1, "bad"),)),
        abi._FrozenJSONObject((("a", object()),)),
    ),
)
def test_forged_frozen_payload_rejected(forged: object) -> None:
    malformed = replace(_artifact(), payload=forged)
    assert "payload_invalid" in abi.validate_kernel_artifact_v01(malformed)
    with pytest.raises(ValueError, match="^kernel_artifact_invalid$"):
        abi.kernel_artifact_to_plain_dict_v01(malformed)


@pytest.mark.parametrize("field", ARTIFACT_FIELDS)
def test_manual_artifact_field_mutation_fails(field: str) -> None:
    artifact = _artifact()
    malformed = replace(artifact, **{field: object()})
    assert abi.validate_kernel_artifact_v01(malformed)


def test_artifact_validator_does_not_swallow_base_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def interrupt(_value: object) -> tuple[str, ...]:
        raise KeyboardInterrupt

    monkeypatch.setattr(abi, "_kernel_artifact_errors", interrupt)
    with pytest.raises(KeyboardInterrupt):
        abi.validate_kernel_artifact_v01(_artifact())


@pytest.mark.parametrize("field", ("artifact_id", "transaction_id", "owner_root_id"))
def test_artifact_hostile_equality_and_hash_never_escape(field: str) -> None:
    malformed = replace(_artifact(), **{field: HostileIdentity()})
    errors = abi.validate_kernel_artifact_bundle_v01(artifacts=(malformed,))
    assert errors
    assert all("SECRET" not in reason for reason in errors)


def test_six_artifact_fixture_bundle_and_order() -> None:
    artifacts = _build_kernel_abi_fixture_v01()
    ids = tuple(item.artifact_id for item in artifacts)
    assert len(artifacts) == 6
    assert abi.validate_kernel_artifact_bundle_v01(artifacts=artifacts) == ()
    assert tuple(row["artifact_id"] for row in abi.kernel_artifacts_to_plain_list_v01(artifacts)) == ids


@pytest.mark.parametrize("bad", ([], (), object(), (_artifact(), object())))
def test_artifact_bundle_shape_rejections(bad: object) -> None:
    assert abi.validate_kernel_artifact_bundle_v01(artifacts=bad)


def test_artifact_bundle_duplicate_id() -> None:
    artifact = _artifact()
    assert "artifact_id_duplicate" in abi.validate_kernel_artifact_bundle_v01(
        artifacts=(artifact, artifact)
    )


def test_artifact_bundle_transaction_mismatch() -> None:
    first = _artifact(artifact_id="artifact:a")
    second = _artifact(artifact_id="artifact:b", transaction_id="txn:other")
    assert "artifact_transaction_mismatch" in abi.validate_kernel_artifact_bundle_v01(
        artifacts=(first, second)
    )


def test_artifact_bundle_unknown_parent() -> None:
    artifact = _artifact(parent_refs=("artifact:missing",))
    assert "parent_ref_unknown" in abi.validate_kernel_artifact_bundle_v01(
        artifacts=(artifact,)
    )


def test_artifact_bundle_self_parent_reason() -> None:
    artifact = _artifact()
    malformed = replace(artifact, parent_refs=(artifact.artifact_id,))
    errors = abi.validate_kernel_artifact_bundle_v01(artifacts=(malformed,))
    assert "parent_ref_self" in errors


def test_artifact_bundle_duplicate_parent_edge_reason() -> None:
    parent = _artifact(artifact_id="artifact:parent")
    child = _artifact(artifact_id="artifact:child")
    malformed = replace(child, parent_refs=(parent.artifact_id, parent.artifact_id))
    errors = abi.validate_kernel_artifact_bundle_v01(artifacts=(parent, malformed))
    assert "parent_edge_duplicate" in errors


@pytest.mark.parametrize("cycle_size", (2, 3))
def test_artifact_bundle_cycle_detection(cycle_size: int) -> None:
    ids = tuple(f"artifact:cycle:{index}" for index in range(cycle_size))
    artifacts = tuple(
        _artifact(artifact_id=artifact_id, parent_refs=(ids[(index + 1) % cycle_size],))
        for index, artifact_id in enumerate(ids)
    )
    assert "parent_graph_cycle" in abi.validate_kernel_artifact_bundle_v01(
        artifacts=artifacts
    )


def test_fan_in_and_fan_out_lineage_are_valid() -> None:
    root = _artifact(artifact_id="artifact:root")
    left = _artifact(artifact_id="artifact:left", parent_refs=(root.artifact_id,))
    right = _artifact(artifact_id="artifact:right", parent_refs=(root.artifact_id,))
    join = _artifact(
        artifact_id="artifact:join", parent_refs=(left.artifact_id, right.artifact_id)
    )
    assert abi.validate_kernel_artifact_bundle_v01(
        artifacts=(join, right, root, left)
    ) == ()


@pytest.mark.parametrize("index", range(6))
def test_canonical_ref_bridge_preserves_fields(index: int) -> None:
    artifact = _build_kernel_abi_fixture_v01()[index]
    ref = abi.kernel_artifact_to_canonical_ref_v01(artifact)
    for field in (
        "artifact_id",
        "artifact_type",
        "schema_version",
        "transaction_id",
        "owner_root_id",
        "authority_class",
        "lifecycle_state",
    ):
        assert getattr(ref, field) == getattr(artifact, field)
    assert len(ref.payload_hash) == 64
    assert ref.payload_hash == ref.payload_hash.lower()
    assert ref == abi.kernel_artifact_to_canonical_ref_v01(artifact)


def test_canonical_ref_payload_hash_changes_only_with_payload_input() -> None:
    artifact = _artifact()
    changed = _rebuild_artifact(artifact, payload={"value": "changed"})
    assert abi.kernel_artifact_to_canonical_ref_v01(artifact).payload_hash != abi.kernel_artifact_to_canonical_ref_v01(changed).payload_hash


def test_canonical_ref_conversion_failure_is_stable() -> None:
    with pytest.raises(ValueError, match="^canonical_artifact_ref_conversion_failed$") as caught:
        abi.kernel_artifact_to_canonical_ref_v01(replace(_artifact(), payload=object()))
    assert caught.value.__cause__ is None


@pytest.mark.parametrize(
    ("disposition", "reason"),
    (
        ("USED", "used:projection"),
        ("REJECTED", "rejected:validation"),
        ("IGNORED_WITH_REASON", "ignored:metadata"),
        ("BLOCKED_BY_GATE", "gate:closed"),
    ),
)
def test_all_causal_dispositions_construct(disposition: str, reason: str) -> None:
    causal_ref = _causal_ref(disposition=disposition, reason_code=reason)
    assert abi.validate_causal_consumption_ref_v01(causal_ref) == ()


@pytest.mark.parametrize(
    "pointer",
    (
        "/value",
        "/details/readiness",
        "/items/0/value",
        "/items/-",
        "/items/01",
        "/a~0b",
        "/a~1b",
        "/",
    ),
)
def test_valid_json_pointer_shapes(pointer: str) -> None:
    assert _causal_ref(output_field=pointer)


@pytest.mark.parametrize(
    "pointer",
        (
            "",
            "value",
            "/bad~",
            "/bad~2",
        "/\ud800",
        None,
        StringSubclass("/value"),
    ),
)
def test_invalid_json_pointer_shapes(pointer: object) -> None:
    with pytest.raises(ValueError, match="^causal_output_field_invalid$"):
        _causal_ref(output_field=pointer)


@pytest.mark.parametrize(
    ("disposition", "reason"),
    (
        ("USED", "rejected:no"),
        ("REJECTED", "used:no"),
        ("IGNORED_WITH_REASON", "gate:no"),
        ("BLOCKED_BY_GATE", "ignored:no"),
    ),
)
def test_causal_reason_prefix_must_match_disposition(
    disposition: str, reason: str
) -> None:
    with pytest.raises(ValueError, match="^causal_reason_disposition_mismatch$"):
        _causal_ref(disposition=disposition, reason_code=reason)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("producer_actor_id", "", "causal_consumption_ref_invalid"),
        ("source_artifact_id", None, "causal_consumption_ref_invalid"),
        ("consumer_component", "", "causal_consumption_ref_invalid"),
        ("downstream_artifact_id", "", "causal_consumption_ref_invalid"),
        ("decision_effect", "", "causal_consumption_ref_invalid"),
        ("disposition", "UNKNOWN", "causal_disposition_unknown"),
        ("disposition", StringSubclass("USED"), "causal_disposition_unknown"),
        ("reason_code", "", "causal_reason_required"),
        ("trace_refs", [], "causal_trace_refs_invalid"),
        ("trace_refs", ("trace:a", "trace:a"), "causal_trace_refs_invalid"),
    ),
)
def test_causal_ref_field_rejections(field: str, value: object, reason: str) -> None:
    with pytest.raises(ValueError, match=f"^{reason}$") as caught:
        _causal_ref(**{field: value})
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("field", ("source_artifact_id", "disposition", "reason_code"))
def test_causal_hostile_equality_and_hash_never_escape(field: str) -> None:
    malformed = replace(_causal_ref(), **{field: HostileIdentity()})
    errors = abi.validate_causal_consumption_ref_v01(malformed)
    assert errors
    assert all("SECRET" not in reason for reason in errors)


def test_causal_validator_does_not_swallow_base_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    causal_ref = _causal_ref()

    def interrupt(_value: object) -> tuple[str, ...]:
        raise GeneratorExit

    monkeypatch.setattr(abi, "_causal_ref_errors", interrupt)
    with pytest.raises(GeneratorExit):
        abi.validate_causal_consumption_ref_v01(causal_ref)


def test_complete_causal_bundle_validates() -> None:
    artifacts, refs, _cases = _build_causal_consumption_fixture_v01()
    assert len(artifacts) == 8
    assert len(refs) == 4
    assert abi.validate_causal_consumption_bundle_v01(
        artifacts=artifacts, causal_refs=refs
    ) == ()


@pytest.mark.parametrize("which", ("artifacts_list", "refs_list", "empty_refs"))
def test_causal_bundle_shape_rejections(which: str) -> None:
    artifacts, refs, _cases = _build_causal_consumption_fixture_v01()
    values: dict[str, object] = {"artifacts": artifacts, "causal_refs": refs}
    if which == "artifacts_list":
        values["artifacts"] = list(artifacts)
    elif which == "refs_list":
        values["causal_refs"] = list(refs)
    else:
        values["causal_refs"] = ()
    assert abi.validate_causal_consumption_bundle_v01(**values) == (
        "causal_bundle_invalid",
    )


def test_causal_bundle_duplicate_ref() -> None:
    artifacts, refs, _cases = _build_causal_consumption_fixture_v01()
    errors = abi.validate_causal_consumption_bundle_v01(
        artifacts=artifacts, causal_refs=(*refs, refs[0])
    )
    assert "causal_ref_duplicate" in errors


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        ("missing_source", "causal_source_artifact_missing"),
        ("missing_downstream", "causal_downstream_artifact_missing"),
        ("consumer", "causal_consumer_mismatch"),
        ("parent", "causal_parent_binding_missing"),
        ("pointer", "causal_output_field_missing"),
        ("transaction", "causal_transaction_mismatch"),
    ),
)
def test_causal_bundle_binding_mutations(mutation: str, reason: str) -> None:
    artifacts, refs, _cases = _build_causal_consumption_fixture_v01()
    causal_ref = refs[0]
    mutated_artifacts = artifacts
    mutated_ref = causal_ref
    if mutation == "missing_source":
        mutated_artifacts = tuple(item for item in artifacts if item.artifact_id != causal_ref.source_artifact_id)
    elif mutation == "missing_downstream":
        mutated_artifacts = tuple(item for item in artifacts if item.artifact_id != causal_ref.downstream_artifact_id)
    elif mutation == "consumer":
        mutated_ref = replace(causal_ref, consumer_component="other")
    elif mutation == "parent":
        mutated_artifacts = tuple(
            _rebuild_artifact(item, parent_refs=()) if item.artifact_id == causal_ref.downstream_artifact_id else item
            for item in artifacts
        )
    elif mutation == "pointer":
        mutated_ref = replace(causal_ref, output_field="/missing")
    else:
        mutated_artifacts = tuple(
            _rebuild_artifact(item, transaction_id="txn:other") if item.artifact_id == causal_ref.downstream_artifact_id else item
            for item in artifacts
        )
    errors = abi.validate_causal_consumption_bundle_v01(
        artifacts=mutated_artifacts,
        causal_refs=(mutated_ref, *refs[1:]),
    )
    assert reason in errors


@pytest.mark.parametrize("case_index", range(4))
def test_positive_counterfactual_for_every_disposition(case_index: int) -> None:
    _artifacts, _refs, cases = _build_causal_consumption_fixture_v01()
    case = cases[case_index]
    assert abi.validate_causal_counterfactual_v01(
        causal_ref=case[0],
        baseline_source_artifact=case[1],
        mutated_source_artifact=case[2],
        baseline_downstream_artifact=case[3],
        mutated_downstream_artifact=case[4],
        baseline_authority_state=case[5],
        mutated_authority_state=case[6],
    ) == ()


def _counterfactual(case: tuple[object, ...], **overrides: object) -> tuple[str, ...]:
    names = (
        "causal_ref",
        "baseline_source_artifact",
        "mutated_source_artifact",
        "baseline_downstream_artifact",
        "mutated_downstream_artifact",
        "baseline_authority_state",
        "mutated_authority_state",
    )
    values = dict(zip(names, case, strict=True))
    values.update(overrides)
    return abi.validate_causal_counterfactual_v01(**values)


def test_used_requires_source_mutation() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    assert "causal_source_mutation_missing" in _counterfactual(
        case, mutated_source_artifact=case[1]
    )


def test_used_requires_downstream_change() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    assert "causal_used_influence_missing" in _counterfactual(
        case, mutated_downstream_artifact=case[3]
    )


def test_rejected_requires_authority_preservation() -> None:
    case = _build_causal_consumption_fixture_v01()[2][1]
    assert _counterfactual(case, mutated_authority_state={"accepted": "changed"}) == (
        "causal_rejected_authority_changed",
    )


def test_ignored_requires_downstream_and_authority_preservation_in_order() -> None:
    cases = _build_causal_consumption_fixture_v01()[2]
    ignored = cases[2]
    used = cases[0]
    errors = _counterfactual(
        ignored,
        mutated_downstream_artifact=used[4],
        mutated_authority_state={"accepted": "changed"},
    )
    assert errors == (
        "causal_downstream_binding_mismatch",
        "causal_ignored_downstream_changed",
        "causal_ignored_authority_changed",
    )


def test_blocked_requires_authority_preservation() -> None:
    case = _build_causal_consumption_fixture_v01()[2][3]
    assert _counterfactual(case, mutated_authority_state={"accepted": "changed"}) == (
        "causal_blocked_authority_changed",
    )


@pytest.mark.parametrize("binding", ("source", "downstream"))
def test_counterfactual_artifact_bindings(binding: str) -> None:
    cases = _build_causal_consumption_fixture_v01()[2]
    case = cases[0]
    replacement = cases[1][1] if binding == "source" else cases[1][3]
    key = "baseline_source_artifact" if binding == "source" else "baseline_downstream_artifact"
    expected = "causal_source_binding_mismatch" if binding == "source" else "causal_downstream_binding_mismatch"
    assert expected in _counterfactual(case, **{key: replacement})


def test_counterfactual_malformed_authority_state_fails_closed() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    assert _counterfactual(case, mutated_authority_state=object()) == (
        "causal_counterfactual_invalid",
    )


@pytest.mark.parametrize("index", range(6))
def test_artifact_projections_are_json_safe_and_independent(index: int) -> None:
    artifact = _build_kernel_abi_fixture_v01()[index]
    first = abi.kernel_artifact_to_plain_dict_v01(artifact)
    second = abi.kernel_artifact_to_plain_dict_v01(artifact)
    assert first == second
    assert not _contains_tuple_or_private(first)
    canonical_json_bytes_v01(first)
    first["payload"] = {"mutated": True}
    assert second == abi.kernel_artifact_to_plain_dict_v01(artifact)


@pytest.mark.parametrize("index", range(4))
def test_causal_projections_are_json_safe_and_independent(index: int) -> None:
    causal_ref = _build_causal_consumption_fixture_v01()[1][index]
    first = abi.causal_consumption_ref_to_plain_dict_v01(causal_ref)
    second = abi.causal_consumption_ref_to_plain_dict_v01(causal_ref)
    assert first == second
    assert not _contains_tuple_or_private(first)
    canonical_json_bytes_v01(first)
    first["trace_refs"].append("trace:mutated")
    assert second == abi.causal_consumption_ref_to_plain_dict_v01(causal_ref)


def test_projection_helpers_reject_malformed_exact_dataclasses() -> None:
    with pytest.raises(ValueError, match="^kernel_artifact_invalid$"):
        abi.kernel_artifact_to_plain_dict_v01(replace(_artifact(), payload=object()))
    with pytest.raises(ValueError, match="^causal_consumption_ref_invalid$"):
        abi.causal_consumption_ref_to_plain_dict_v01(replace(_causal_ref(), disposition="bad"))


def test_list_projection_helpers_reject_non_tuples() -> None:
    with pytest.raises(ValueError, match="^artifact_bundle_invalid$"):
        abi.kernel_artifacts_to_plain_list_v01([_artifact()])
    with pytest.raises(ValueError, match="^causal_bundle_invalid$"):
        abi.causal_consumption_refs_to_plain_list_v01([_causal_ref()])


def test_schema_is_draft_2020_12_and_strict() -> None:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$ref"] == "#/$defs/kernelArtifact"
    assert "causalConsumptionRef" in schema["$defs"]
    assert "http" not in json.dumps(schema["$defs"])


@pytest.mark.parametrize("artifact_type", abi.ARTIFACT_TYPES)
def test_schema_validates_every_artifact_family(artifact_type: str) -> None:
    projection = abi.kernel_artifact_to_plain_dict_v01(_artifact(artifact_type=artifact_type))
    Draft202012Validator(_schema()).validate(projection)


@pytest.mark.parametrize("field", ARTIFACT_FIELDS)
def test_schema_rejects_each_required_field_deletion(field: str) -> None:
    projection = abi.kernel_artifact_to_plain_dict_v01(_artifact())
    del projection[field]
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema()).validate(projection)


def test_schema_rejects_extra_envelope_field() -> None:
    projection = abi.kernel_artifact_to_plain_dict_v01(_artifact())
    projection["extra"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema()).validate(projection)


@pytest.mark.parametrize("index", range(4))
def test_schema_local_causal_definition(index: int) -> None:
    schema = _schema()
    causal_schema = {
        "$schema": schema["$schema"],
        "$ref": "#/$defs/causalConsumptionRef",
        "$defs": schema["$defs"],
    }
    projection = abi.causal_consumption_ref_to_plain_dict_v01(
        _build_causal_consumption_fixture_v01()[1][index]
    )
    Draft202012Validator(causal_schema).validate(projection)


def test_schema_can_accept_reserved_payload_but_semantic_validator_rejects_it() -> None:
    projection = abi.kernel_artifact_to_plain_dict_v01(_artifact())
    projection["payload"] = {"authority_class": "ROOT_OWNED"}
    Draft202012Validator(_schema()).validate(projection)
    with pytest.raises(ValueError, match="^payload_reserved_field$"):
        _artifact(payload=projection["payload"])


def test_schema_version_pattern_is_broader_than_supported_abi_semantics() -> None:
    projection = abi.kernel_artifact_to_plain_dict_v01(_artifact())
    projection["abi_version"] = "v1.1"
    Draft202012Validator(_schema()).validate(projection)
    assert abi.validate_kernel_artifact_v01(
        replace(_artifact(), abi_version="v1.1")
    ) == ("abi_minor_version_unsupported",)


@pytest.mark.parametrize(
    "forbidden",
    ("REVOKED", "SUPERSEDED", "EXPIRED", "KILLED", "ROLLED_BACK"),
)
def test_gate2_lifecycle_states_are_absent(forbidden: str) -> None:
    assert forbidden not in abi.LIFECYCLE_STATES


@pytest.mark.parametrize(
    "forbidden_name",
    (
        "resolve_json_pointer_v01",
        "transition_artifact_v01",
        "register_transition_v01",
        "create_root_decision_v01",
        "create_permission_v01",
        "execute_effect_v01",
    ),
)
def test_forbidden_public_apis_absent(forbidden_name: str) -> None:
    assert not hasattr(abi, forbidden_name)


def test_static_import_boundary() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden_prefixes = (
        "cryptography",
        "hedgehog.domains",
        "hedgehog.kernel.trust_model_v01",
        "hedgehog.kernel.semantic_work_v01",
        "hedgehog.kernel.root_signer_isolation_v01",
        "demo",
        "tests",
        "jsonschema",
        "os",
        "pathlib",
        "tempfile",
        "shutil",
        "subprocess",
        "socket",
        "requests",
        "urllib",
    )
    assert not any(name.startswith(forbidden_prefixes) for name in imported)


@pytest.mark.parametrize("name", ("open", "read", "write", "getenv", "environ", "callback", "effect_hook"))
def test_static_effect_and_io_calls_absent(name: str) -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert name not in called_names
    assert name not in attributes


@pytest.mark.parametrize("token", ("Airline", "Supplier", "Water Filter", ".tmp", "RootDecisionV01", "EffectCapabilityV01", "TransitionRuleV01"))
def test_static_domain_and_future_contract_tokens_absent(token: str) -> None:
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_counterfactual_rejects_unrelated_source_payload_mutation() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    mutated_source = _rebuild_artifact(
        case[2],
        payload={"recommendation": "candidate:beta", "unrelated": True},
    )
    assert "causal_source_binding_mismatch" in _counterfactual(
        case, mutated_source_artifact=mutated_source
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authority_class", "NON_AUTHORITY"),
        ("lifecycle_state", "PROPOSED"),
        ("owner_root_id", "root:other"),
        ("source_component", "drs"),
        ("trace_refs", ("trace:mutated",)),
        ("parent_refs", ("artifact:unrelated:parent",)),
        (
            "time_envelope",
            _time_envelope(pt_created_at="2026-01-01T00:00:01+00:00"),
        ),
    ),
)
def test_counterfactual_rejects_source_envelope_mutation(
    field: str, value: object
) -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    mutated_source = _rebuild_artifact(case[2], **{field: value})
    assert "causal_source_binding_mismatch" in _counterfactual(
        case, mutated_source_artifact=mutated_source
    )


def test_counterfactual_rejects_consumer_mismatch() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    causal_ref = replace(case[0], consumer_component="other_consumer")
    assert "causal_downstream_binding_mismatch" in _counterfactual(
        case, causal_ref=causal_ref
    )


@pytest.mark.parametrize("which", ("baseline", "mutated"))
def test_counterfactual_rejects_missing_downstream_parent(which: str) -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    key = (
        "baseline_downstream_artifact"
        if which == "baseline"
        else "mutated_downstream_artifact"
    )
    original = case[3] if which == "baseline" else case[4]
    downstream = _rebuild_artifact(original, parent_refs=())
    assert "causal_downstream_binding_mismatch" in _counterfactual(
        case, **{key: downstream}
    )


def test_counterfactual_rejects_source_downstream_identity_collapse() -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    source_id = case[1].artifact_id
    causal_ref = replace(case[0], downstream_artifact_id=source_id)
    baseline_downstream = _rebuild_artifact(
        case[3], artifact_id=source_id, parent_refs=()
    )
    mutated_downstream = _rebuild_artifact(
        case[4], artifact_id=source_id, parent_refs=()
    )
    assert "causal_downstream_binding_mismatch" in _counterfactual(
        case,
        causal_ref=causal_ref,
        baseline_downstream_artifact=baseline_downstream,
        mutated_downstream_artifact=mutated_downstream,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authority_class", "ROOT_OWNED"),
        ("lifecycle_state", "ROOT_ACCEPTED"),
        (
            "time_envelope",
            _time_envelope(kt_asof="2026-01-01T00:00:01+00:00"),
        ),
    ),
)
def test_used_rejects_downstream_envelope_only_mutation(
    field: str, value: object
) -> None:
    case = _build_causal_consumption_fixture_v01()[2][0]
    mutated_downstream = _rebuild_artifact(case[3], **{field: value})
    errors = _counterfactual(
        case, mutated_downstream_artifact=mutated_downstream
    )
    assert "causal_downstream_binding_mismatch" in errors
    assert "causal_used_influence_missing" in errors


@pytest.mark.parametrize(
    ("case_index", "field", "value"),
    (
        (1, "authority_class", "ROOT_OWNED"),
        (1, "lifecycle_state", "ROOT_ACCEPTED"),
        (3, "authority_class", "ROOT_OWNED"),
        (3, "lifecycle_state", "ROOT_ACCEPTED"),
        (2, "owner_root_id", "root:other"),
    ),
)
def test_non_used_dispositions_reject_downstream_envelope_escalation(
    case_index: int, field: str, value: str
) -> None:
    case = _build_causal_consumption_fixture_v01()[2][case_index]
    mutated_downstream = _rebuild_artifact(case[4], **{field: value})
    assert "causal_downstream_binding_mismatch" in _counterfactual(
        case, mutated_downstream_artifact=mutated_downstream
    )


@pytest.mark.parametrize(
    ("disposition", "reason_code"),
    (
        ("USED", "used:"),
        ("REJECTED", "rejected:"),
        ("IGNORED_WITH_REASON", "ignored:"),
        ("BLOCKED_BY_GATE", "gate:"),
        ("USED", "used:   "),
        ("REJECTED", "rejected:\t"),
        ("IGNORED_WITH_REASON", "ignored:   "),
        ("BLOCKED_BY_GATE", "gate:\n"),
    ),
)
def test_reason_code_requires_non_whitespace_suffix(
    disposition: str, reason_code: str
) -> None:
    with pytest.raises(
        ValueError, match="^causal_reason_disposition_mismatch$"
    ) as caught:
        _causal_ref(disposition=disposition, reason_code=reason_code)
    assert caught.value.__cause__ is None


def _pointer_bundle_errors(payload: object, pointer: str) -> tuple[str, ...]:
    source = _artifact(
        artifact_id="artifact:pointer:source",
        payload=payload,
    )
    downstream = _artifact(
        artifact_id="artifact:pointer:downstream",
        source_component="deterministic_runtime",
        parent_refs=(source.artifact_id,),
    )
    causal_ref = _causal_ref(
        source_artifact_id=source.artifact_id,
        downstream_artifact_id=downstream.artifact_id,
        output_field=pointer,
    )
    return abi.validate_causal_consumption_bundle_v01(
        artifacts=(source, downstream), causal_refs=(causal_ref,)
    )


@pytest.mark.parametrize(
    ("payload", "pointer"),
    (
        ({"01": "x"}, "/01"),
        ({"٠": "x"}, "/٠"),
        ({"items": ["x"]}, "/items/0"),
    ),
)
def test_pointer_resolves_exact_object_keys_and_ascii_array_index(
    payload: object, pointer: str
) -> None:
    assert _pointer_bundle_errors(payload, pointer) == ()


@pytest.mark.parametrize("pointer", ("/items/01", "/items/٠", "/items/-"))
def test_pointer_rejects_noncanonical_array_index(pointer: str) -> None:
    assert "causal_output_field_missing" in _pointer_bundle_errors(
        {"items": ["x"]}, pointer
    )


@pytest.mark.parametrize(
    "timestamp",
    (
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:00:00+00:00",
        "2026-01-01T00:00:00.123456+05:30",
    ),
)
def test_runtime_accepted_timestamp_also_passes_schema(timestamp: str) -> None:
    artifact = _artifact(
        time_envelope=_time_envelope(
            pt_created_at=timestamp,
            kt_asof=timestamp,
            valid_from=timestamp,
            valid_to=timestamp,
        )
    )
    projection = abi.kernel_artifact_to_plain_dict_v01(artifact)
    Draft202012Validator(_schema()).validate(projection)


def test_runtime_and_schema_timestamp_patterns_are_identical() -> None:
    assert _schema()["$defs"]["awareTimestamp"]["pattern"] == (
        abi._AWARE_TIMESTAMP_PATTERN.pattern
    )


@pytest.mark.parametrize(
    "timestamp",
    (
        "2026-01-01 00:00:00+00:00",
        "2026-01-01t00:00:00+00:00",
        "2026-01-01T00:00:00z",
        "2026-01-01T00:00:00+0530",
        "2026-01-01T00:00:00+05",
        "2026-01-01T00:00:00+05:30:15",
        "2026-01-01T00:00:00",
        "2026-13-01T00:00:00+00:00",
        "2026-01-01T25:00:00+00:00",
        "2026-01-01T00:00:00+24:00",
    ),
)
def test_runtime_rejects_timestamp_outside_exact_grammar(timestamp: str) -> None:
    with pytest.raises(ValueError, match="^time_envelope_invalid$"):
        _artifact(time_envelope=_time_envelope(pt_created_at=timestamp))


@pytest.mark.parametrize("case_index", range(4))
def test_original_counterfactual_fixtures_remain_valid(case_index: int) -> None:
    case = _build_causal_consumption_fixture_v01()[2][case_index]
    assert _counterfactual(case) == ()


@pytest.mark.parametrize(
    ("fixture_name", "expected"),
    (
        (
            "abi",
            "6fd9515a203f14db5cb2f2a5d51ab2d2d1567646dcb663e8b1707415b42988c7",
        ),
        (
            "causal",
            "34dc1f9ed3c95e7592e3f83d2f15681e3303f997d3402b6878d407501c2d15d4",
        ),
    ),
)
def test_fixture_projection_hashes_remain_unchanged(
    fixture_name: str, expected: str
) -> None:
    if fixture_name == "abi":
        projection = abi.kernel_artifacts_to_plain_list_v01(
            _build_kernel_abi_fixture_v01()
        )
    else:
        projection = abi.causal_consumption_refs_to_plain_list_v01(
            _build_causal_consumption_fixture_v01()[1]
        )
    assert hashlib.sha256(canonical_json_bytes_v01(projection)).hexdigest() == expected


def test_g2c1_artifact_type_append_preserves_historical_prefix() -> None:
    historical = (
        "OrchestratorRouteProposal",
        "RootAcceptedRoute",
        "BSEPPacket",
        "BSEPProjection",
        "SemanticArchitectProposal",
        "RuntimeExecutionTopology",
        "ActorContribution",
        "SemanticEvidence",
        "ValidatedEvidence",
        "ResultProposal",
        "PostVVReport",
        "GTAdvisoryReport",
        "RootOwnedIntent",
        "RootDecision",
        "ExecutionRequest",
        "EvidenceReceipt",
        "RootFinal",
        "CrossRootEvidenceRef",
        "TransactionOutcomeEnvelope",
        "CausalConsumptionRef",
    )
    suffix = (
        "ExecutionModeProposal",
        "RootExecutionModeDecision",
        "ExecutionModeRouteEligibility",
    )
    assert abi.ARTIFACT_TYPES[: len(historical)] == historical
    assert abi.ARTIFACT_TYPES[len(historical) : len(historical) + len(suffix)] == suffix
    assert tuple(_schema()["$defs"]["artifactType"]["enum"][: len(historical)]) == historical
    assert tuple(
        _schema()["$defs"]["artifactType"]["enum"][
            len(historical) : len(historical) + len(suffix)
        ]
    ) == suffix


@pytest.mark.parametrize(
    "artifact_type",
    (
        "ExecutionModeProposal",
        "RootExecutionModeDecision",
        "ExecutionModeRouteEligibility",
    ),
)
def test_g2c1_artifact_literals_use_unchanged_generic_v1_envelope(
    artifact_type: str,
) -> None:
    artifact = _artifact(artifact_type=artifact_type)
    assert artifact.abi_version == "v1.0"
    assert abi.validate_kernel_artifact_v01(artifact) == ()
    projection = abi.kernel_artifact_to_plain_dict_v01(artifact)
    Draft202012Validator(_schema()).validate(projection)
    assert projection["payload"] == {"value": {"items": [1, True, None]}}
    assert projection["time_envelope"] == _time_envelope()


def test_g2c1_abi_append_contains_no_router_import_or_orchestration() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = []
    function_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.append(node.name)
    assert not any("execution_mode_router_v01" in item for item in imports)
    assert not any("execution_mode" in item for item in function_names)


def test_g2d2_artifact_type_append_and_generic_envelope() -> None:
    historical = (
        "OrchestratorRouteProposal", "RootAcceptedRoute", "BSEPPacket",
        "BSEPProjection", "SemanticArchitectProposal",
        "RuntimeExecutionTopology", "ActorContribution", "SemanticEvidence",
        "ValidatedEvidence", "ResultProposal", "PostVVReport",
        "GTAdvisoryReport", "RootOwnedIntent", "RootDecision",
        "ExecutionRequest", "EvidenceReceipt", "RootFinal",
        "CrossRootEvidenceRef", "TransactionOutcomeEnvelope",
        "CausalConsumptionRef", "ExecutionModeProposal",
        "RootExecutionModeDecision", "ExecutionModeRouteEligibility",
    )
    suffix = (
        "FractalCellQueueEntry", "FractalCellResult", "FractalRuntimeReport",
    )
    assert abi.ARTIFACT_TYPES[: len(historical)] == historical
    assert abi.ARTIFACT_TYPES[len(historical) : len(historical) + len(suffix)] == suffix
    schema_types = tuple(_schema()["$defs"]["artifactType"]["enum"])
    assert schema_types[: len(historical)] == historical
    assert schema_types[len(historical) : len(historical) + len(suffix)] == suffix
    assert abi.ARTIFACT_TYPES.count("RuntimeExecutionTopology") == 1
    for artifact_type in suffix:
        artifact = _artifact(artifact_type=artifact_type)
        assert abi.validate_kernel_artifact_v01(artifact) == ()
        Draft202012Validator(_schema()).validate(
            abi.kernel_artifact_to_plain_dict_v01(artifact)
        )

    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
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
    assert "hedgehog.kernel.fractal_runtime_v02" not in imports


def test_g2e_artifact_type_literals_append_after_historical_prefix_v01() -> None:
    historical = (
        "OrchestratorRouteProposal", "RootAcceptedRoute", "BSEPPacket",
        "BSEPProjection", "SemanticArchitectProposal",
        "RuntimeExecutionTopology", "ActorContribution", "SemanticEvidence",
        "ValidatedEvidence", "ResultProposal", "PostVVReport",
        "GTAdvisoryReport", "RootOwnedIntent", "RootDecision",
        "ExecutionRequest", "EvidenceReceipt", "RootFinal",
        "CrossRootEvidenceRef", "TransactionOutcomeEnvelope",
        "CausalConsumptionRef", "ExecutionModeProposal",
        "RootExecutionModeDecision", "ExecutionModeRouteEligibility",
        "FractalCellQueueEntry", "FractalCellResult", "FractalRuntimeReport",
    )
    additions = (
        "ContinuousDeltaSource",
        "DependencyGraphIndex",
        "AffectedSetResult",
        "ArtifactInvalidationReport",
        "PreservationProof",
        "SelectiveRecomputationPlan",
        "ContinuousDeltaRuntimeReport",
    )
    schema_types = tuple(_schema()["$defs"]["artifactType"]["enum"])
    assert abi.ARTIFACT_TYPES[: len(historical)] == historical
    assert abi.ARTIFACT_TYPES[len(historical) :] == additions
    assert schema_types[: len(historical)] == historical
    assert schema_types[len(historical) :] == additions
    assert len(abi.ARTIFACT_TYPES) == len(set(abi.ARTIFACT_TYPES))


def test_g2e_kernel_artifact_schema_literals_and_unknown_rejection_v01() -> None:
    additions = (
        "ContinuousDeltaSource",
        "DependencyGraphIndex",
        "AffectedSetResult",
        "ArtifactInvalidationReport",
        "PreservationProof",
        "SelectiveRecomputationPlan",
        "ContinuousDeltaRuntimeReport",
    )
    schema = _schema()
    for artifact_type in additions:
        artifact = _artifact(
            artifact_id="artifact:g2e:" + artifact_type,
            artifact_type=artifact_type,
            authority_class="NON_AUTHORITY",
            lifecycle_state="VALIDATED",
        )
        assert abi.validate_kernel_artifact_v01(artifact) == ()
        Draft202012Validator(schema).validate(
            abi.kernel_artifact_to_plain_dict_v01(artifact)
        )
        assert artifact.authority_class == "NON_AUTHORITY"
    for unknown in (
        "ContinuousDeltaSourceUnknown",
        "continuousDeltaSource",
        "ContinuousDeltaSource ",
    ):
        with pytest.raises(ValueError, match="^artifact_type_unknown$"):
            _artifact(artifact_type=unknown)
        invalid = abi.kernel_artifact_to_plain_dict_v01(_artifact())
        invalid["artifact_type"] = unknown
        with pytest.raises(ValidationError):
            Draft202012Validator(schema).validate(invalid)
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not any("continuous_delta" in name or "g2e" in name for name in public_names)
