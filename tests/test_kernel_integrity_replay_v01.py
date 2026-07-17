from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
import inspect
import json
import math
from pathlib import Path
import re
from typing import Any, Callable

import pytest

from hedgehog import kernel
from hedgehog.kernel import integrity_replay_v01 as core


MODULE_PATH = Path(core.__file__).resolve()
PUBLIC_DATACLASSES = (
    core.CanonicalArtifactRefV01,
    core.ArtifactDependencyEdgeV01,
    core.RootOwnershipBindingV01,
    core.EvidenceClassBindingV01,
    core.AuthorityClassBindingV01,
    core.SealProfileV01,
    core.ArtifactManifestV01,
    core.SealVerificationResultV01,
    core.ReplayVerificationResultV01,
)
EXPECTED_PUBLIC_FUNCTIONS = {
    "artifact_manifest_to_plain_dict_v01",
    "build_artifact_manifest_v01",
    "build_canonical_artifact_ref_v01",
    "build_default_seal_profile_v01",
    "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01",
    "replay_verification_result_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01",
}
EXPECTED_ALL = (
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
REPLAY_ZERO_FIELDS = (
    "provider_call_count",
    "network_call_count",
    "semantic_rerun_count",
    "transaction_rerun_count",
    "corridor_rerun_count",
    "ledger_recollection_count",
    "crypto_recollection_count",
    "root_decision_created_count",
    "authority_created_count",
    "permission_created_count",
    "action_created_count",
    "action_commit_packet_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
)


@dataclass(frozen=True)
class Fixture:
    manifest: core.ArtifactManifestV01
    payload_rows: tuple[tuple[str, object], ...]


class HostileInputError(Exception):
    pass


class RaisingItemsMapping(Mapping[str, object]):
    def __init__(self, error_type: type[Exception]) -> None:
        self._error_type = error_type

    def __getitem__(self, key: str) -> object:
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self) -> int:
        return 0

    def items(self):
        raise self._error_type("hostile caller text")


class DuplicateItemsMapping(Mapping[str, object]):
    def __getitem__(self, key: str) -> object:
        if key == "duplicate":
            return 2
        raise KeyError(key)

    def __iter__(self):
        return iter(("duplicate",))

    def __len__(self) -> int:
        return 1

    def items(self):
        return (("duplicate", 1), ("duplicate", 2))


class RaisingEquality:
    def __init__(self, error_type: type[Exception] = RuntimeError) -> None:
        self._error_type = error_type

    def __eq__(self, other: object) -> bool:
        raise self._error_type("hostile caller text")

    def __hash__(self) -> int:
        raise self._error_type("hostile caller text")


def _fixture(kind: str = "linear", *, ordered: bool = True) -> Fixture:
    profile = core.build_default_seal_profile_v01(
        timeline_order_required=ordered
    )
    if kind == "linear":
        transaction_id = "txn:test:linear"
        rows = (
            ("test:scope", "scope", "root:a", "ROOT_OWNED", "VALIDATED", "CONTEXT", {"n": 0}),
            ("test:evidence", "evidence", "root:a", "ADVISORY", "VALIDATED", "EVIDENCE", {"n": 1}),
            ("test:decision", "decision", "root:a", "ROOT_OWNED", "ROOT_ACCEPTED", "DECISION", {"n": 2}),
            ("test:final", "final", "root:b", "ROOT_OWNED", "FINALIZED", "FINAL", {"n": 3}),
        )
        edges = (
            core.ArtifactDependencyEdgeV01("test:evidence", "test:scope"),
            core.ArtifactDependencyEdgeV01("test:decision", "test:evidence"),
            core.ArtifactDependencyEdgeV01("test:final", "test:decision"),
        )
    else:
        transaction_id = "txn:test:fanout"
        rows = (
            ("test:fan:scope", "scope", "root:a", "ROOT_OWNED", "VALIDATED", "CONTEXT", {"n": 0}),
            ("test:fan:left", "branch", "root:a", "ADVISORY", "VALIDATED", "BRANCH", {"n": 1}),
            ("test:fan:right", "branch", "root:b", "ADVISORY", "VALIDATED", "BRANCH", {"n": 2}),
            ("test:fan:review", "review", "root:a", "ADVISORY", "ROOT_REVIEWED", "REVIEW", {"n": 3}),
            ("test:fan:final_a", "final", "root:a", "ROOT_OWNED", "FINALIZED", "FINAL", {"n": 4}),
            ("test:fan:final_b", "final", "root:b", "ROOT_OWNED", "FINALIZED", "FINAL", {"n": 5}),
        )
        edges = (
            core.ArtifactDependencyEdgeV01("test:fan:final_b", "test:fan:review"),
            core.ArtifactDependencyEdgeV01("test:fan:review", "test:fan:right"),
            core.ArtifactDependencyEdgeV01("test:fan:left", "test:fan:scope"),
            core.ArtifactDependencyEdgeV01("test:fan:final_a", "test:fan:review"),
            core.ArtifactDependencyEdgeV01("test:fan:right", "test:fan:scope"),
            core.ArtifactDependencyEdgeV01("test:fan:review", "test:fan:left"),
        )
    payload_rows = tuple((row[0], row[6]) for row in rows)
    artifacts = tuple(
        core.build_canonical_artifact_ref_v01(
            artifact_id=row[0],
            artifact_type=row[1],
            schema_version="v1",
            transaction_id=transaction_id,
            owner_root_id=row[2],
            authority_class=row[3],
            lifecycle_state=row[4],
            payload=row[6],
            profile=profile,
        )
        for row in rows
    )
    manifest = core.build_artifact_manifest_v01(
        transaction_id=transaction_id,
        profile=profile,
        artifacts=artifacts,
        dependency_edges=edges,
        root_ownership_bindings=tuple(
            core.RootOwnershipBindingV01(row[0], row[2]) for row in reversed(rows)
        ),
        evidence_class_bindings=tuple(
            core.EvidenceClassBindingV01(row[0], row[5]) for row in reversed(rows)
        ),
        authority_class_bindings=tuple(
            core.AuthorityClassBindingV01(row[0], row[3]) for row in reversed(rows)
        ),
    )
    return Fixture(manifest, payload_rows)


@pytest.fixture(scope="module")
def linear() -> Fixture:
    return _fixture("linear")


@pytest.fixture(scope="module")
def fanout() -> Fixture:
    return _fixture("fanout")


@pytest.mark.parametrize(
    ("contract", "expected"),
    (
        (core.CanonicalArtifactRefV01, ("artifact_id", "artifact_type", "schema_version", "transaction_id", "owner_root_id", "authority_class", "lifecycle_state", "payload_hash")),
        (core.ArtifactDependencyEdgeV01, ("artifact_id", "depends_on_artifact_id")),
        (core.RootOwnershipBindingV01, ("artifact_id", "owner_root_id")),
        (core.EvidenceClassBindingV01, ("artifact_id", "evidence_class")),
        (core.AuthorityClassBindingV01, ("artifact_id", "authority_class")),
        (core.SealProfileV01, ("profile_id", "manifest_version", "artifact_schema_version", "canonicalization_profile_id", "hash_algorithm", "hash_encoding", "payload_domain", "manifest_domain", "replay_domain", "timeline_order_required")),
        (core.ArtifactManifestV01, ("manifest_version", "transaction_id", "seal_profile", "artifacts", "dependency_edges", "root_ownership_bindings", "evidence_class_bindings", "authority_class_bindings", "artifact_count", "dependency_edge_count", "root_ownership_binding_count", "evidence_class_binding_count", "authority_class_binding_count", "manifest_hash")),
        (core.SealVerificationResultV01, ("verification_status", "verification_errors", "profile_verified", "canonicalization_verified", "artifact_ids_unique", "artifact_order_verified", "payload_hashes_verified", "dependencies_verified", "root_ownership_verified", "evidence_classes_verified", "authority_classes_verified", "manifest_hash_verified", "expected_manifest_hash_supplied", "expected_manifest_hash_verified", "artifact_count", "dependency_edge_count", "recomputed_manifest_hash")),
        (core.ReplayVerificationResultV01, ("replay_status", "replay_errors", "replay_id", "manifest_hash", "manifest_verification_status", "artifact_count", "dependency_edge_count", "reconstructed_artifact_ids", "reconstructed_artifact_types", "reconstructed_owner_root_ids", "reconstructed_dependency_counts", "reconstructed_dependency_edges", "integrity_verified", "continuity_verified", "root_ownership_verified", "evidence_classes_verified", "authority_classes_verified", "provider_call_count", "network_call_count", "semantic_rerun_count", "transaction_rerun_count", "corridor_rerun_count", "ledger_recollection_count", "crypto_recollection_count", "root_decision_created_count", "authority_created_count", "permission_created_count", "action_created_count", "action_commit_packet_created_count", "receipt_created_count", "final_output_created_count", "real_world_effects_count")),
    ),
)
def test_exact_dataclass_field_order(contract: type[object], expected: tuple[str, ...]) -> None:
    assert tuple(field.name for field in fields(contract)) == expected


@pytest.mark.parametrize("contract", PUBLIC_DATACLASSES)
def test_public_dataclasses_are_frozen(contract: type[object]) -> None:
    assert is_dataclass(contract)
    assert contract.__dataclass_params__.frozen is True


def test_exact_public_function_set() -> None:
    functions = {
        name
        for name, value in vars(core).items()
        if inspect.isfunction(value) and not name.startswith("_")
    }
    assert functions == EXPECTED_PUBLIC_FUNCTIONS


def test_exact_kernel_package_all() -> None:
    assert kernel.__all__ == EXPECTED_ALL
    assert all(getattr(kernel, name) is not None for name in EXPECTED_ALL)


def test_module_identity_constants_are_exact() -> None:
    assert core.MODULE_ID == "kernel_integrity_replay_v01"
    assert core.SLICE_ID == "domain_neutral_reference_kernel_gate1_g1a1"
    assert core.INTEGRITY_REPLAY_VERSION == "v0.1"


def test_canonical_json_orders_keys_and_is_compact() -> None:
    assert core.canonical_json_bytes_v01({"z": 1, "a": 2}) == b'{"a":2,"z":1}'


def test_canonical_json_is_utf8_and_unicode_stable() -> None:
    expected = '{"text":"Tiranë"}'.encode()
    assert core.canonical_json_bytes_v01({"text": "Tiranë"}) == expected


def test_list_and_tuple_are_canonically_equivalent() -> None:
    assert core.canonical_json_bytes_v01([1, {"a": 2}]) == core.canonical_json_bytes_v01((1, {"a": 2}))


def test_nested_canonical_json_is_deterministic() -> None:
    value = {"outer": ({"b": 2, "a": 1}, True, None)}
    assert core.canonical_json_bytes_v01(value) == core.canonical_json_bytes_v01(value)


@pytest.mark.parametrize("value", [0.0, -0.0, 1.25, -7.5])
def test_finite_float_is_accepted(value: float) -> None:
    assert core.canonical_json_bytes_v01(value)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_float_is_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="json_non_finite_number"):
        core.canonical_json_bytes_v01(value)


@pytest.mark.parametrize("value", [b"x", bytearray(b"x"), memoryview(b"x"), {1}, frozenset({1})])
def test_forbidden_json_container_types_are_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="json_value_type_invalid"):
        core.canonical_json_bytes_v01(value)


def test_non_string_mapping_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="json_mapping_key_invalid"):
        core.canonical_json_bytes_v01({1: "x"})


def test_arbitrary_object_is_rejected() -> None:
    with pytest.raises(ValueError, match="json_value_type_invalid"):
        core.canonical_json_bytes_v01(object())


def test_dataclass_requires_explicit_projection(linear: Fixture) -> None:
    with pytest.raises(ValueError, match="json_dataclass_requires_projection"):
        core.canonical_json_bytes_v01(linear.manifest)


@pytest.mark.parametrize("value", ["\ud800", "x\udfff", {"\ud800": 1}])
def test_invalid_unicode_surrogate_is_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="json_.*invalid"):
        core.canonical_json_bytes_v01(value)


def test_canonical_bytes_have_no_bom_or_terminal_newline() -> None:
    value = core.canonical_json_bytes_v01({"a": 1})
    assert not value.startswith(b"\xef\xbb\xbf")
    assert not value.endswith(b"\n")


def test_bool_remains_valid_json_payload() -> None:
    assert core.canonical_json_bytes_v01(True) == b"true"


def test_cyclic_json_values_are_rejected() -> None:
    value: list[object] = []
    value.append(value)
    with pytest.raises(ValueError, match="json_cycle_invalid"):
        core.canonical_json_bytes_v01(value)


def test_custom_mapping_with_string_keys_is_accepted() -> None:
    class CustomMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            return {"a": 1}[key]

        def __iter__(self):
            return iter(("a",))

        def __len__(self) -> int:
            return 1

    assert core.canonical_json_bytes_v01(CustomMapping()) == b'{"a":1}'


def test_hostile_custom_mapping_cannot_leak_mapping_exception() -> None:
    class HostileMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            raise KeyError(key)

        def __iter__(self):
            return iter(("a",))

        def __len__(self) -> int:
            return 1

    with pytest.raises(ValueError) as captured:
        core.canonical_json_bytes_v01(HostileMapping())
    assert captured.value.args == ("json_mapping_invalid",)
    assert captured.value.__cause__ is None


def test_hash_is_lowercase_64_hex_and_deterministic() -> None:
    first = core.domain_separated_sha256_hex_v01(domain="alpha", payload=b"x")
    second = core.domain_separated_sha256_hex_v01(domain="alpha", payload=b"x")
    assert first == second
    assert re.fullmatch(r"[0-9a-f]{64}", first)


def test_different_hash_domains_differ() -> None:
    assert core.domain_separated_sha256_hex_v01(domain="a", payload=b"x") != core.domain_separated_sha256_hex_v01(domain="b", payload=b"x")


def test_hash_length_prefix_blocks_boundary_ambiguity() -> None:
    assert core.domain_separated_sha256_hex_v01(domain="ab", payload=b"c") != core.domain_separated_sha256_hex_v01(domain="a", payload=b"bc")


@pytest.mark.parametrize("domain", ["", "é", 1, True])
def test_invalid_hash_domain_is_rejected(domain: object) -> None:
    with pytest.raises(ValueError, match="hash_domain_invalid"):
        core.domain_separated_sha256_hex_v01(domain=domain, payload=b"x")  # type: ignore[arg-type]


@pytest.mark.parametrize("payload", [bytearray(b"x"), memoryview(b"x"), "x", None])
def test_hash_payload_requires_exact_bytes(payload: object) -> None:
    with pytest.raises(ValueError, match="hash_payload_invalid"):
        core.domain_separated_sha256_hex_v01(domain="a", payload=payload)  # type: ignore[arg-type]


@pytest.mark.parametrize("kind", ["linear", "fanout"])
def test_valid_manifests_construct(kind: str) -> None:
    fixture = _fixture(kind)
    assert fixture.manifest.artifact_count == len(fixture.payload_rows)
    assert re.fullmatch(r"[0-9a-f]{64}", fixture.manifest.manifest_hash)


def test_declared_artifact_order_is_preserved(linear: Fixture) -> None:
    assert tuple(item.artifact_id for item in linear.manifest.artifacts) == tuple(row[0] for row in linear.payload_rows)


def test_edge_order_is_canonicalized(fanout: Fixture) -> None:
    positions = {item.artifact_id: index for index, item in enumerate(fanout.manifest.artifacts)}
    keys = [(positions[e.artifact_id], positions[e.depends_on_artifact_id]) for e in fanout.manifest.dependency_edges]
    assert keys == sorted(keys)


@pytest.mark.parametrize("field", ["root_ownership_bindings", "evidence_class_bindings", "authority_class_bindings"])
def test_binding_order_is_canonicalized(fanout: Fixture, field: str) -> None:
    bindings = getattr(fanout.manifest, field)
    assert tuple(item.artifact_id for item in bindings) == tuple(item.artifact_id for item in fanout.manifest.artifacts)


def test_artifact_does_not_retain_input_payload() -> None:
    payload = {"nested": [1]}
    profile = core.build_default_seal_profile_v01()
    artifact = core.build_canonical_artifact_ref_v01(artifact_id="a", artifact_type="t", schema_version="v1", transaction_id="tx", owner_root_id="r", authority_class="A", lifecycle_state="L", payload=payload, profile=profile)
    payload["nested"].append(2)
    assert not hasattr(artifact, "payload")


def _build_with(linear: Fixture, **changes: object) -> core.ArtifactManifestV01:
    values = {
        "transaction_id": linear.manifest.transaction_id,
        "profile": linear.manifest.seal_profile,
        "artifacts": linear.manifest.artifacts,
        "dependency_edges": linear.manifest.dependency_edges,
        "root_ownership_bindings": linear.manifest.root_ownership_bindings,
        "evidence_class_bindings": linear.manifest.evidence_class_bindings,
        "authority_class_bindings": linear.manifest.authority_class_bindings,
    }
    values.update(changes)
    return core.build_artifact_manifest_v01(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("change", "reason"),
    (
        ({"transaction_id": ""}, "manifest_contract_invalid"),
        ({"artifacts": ()}, "manifest_contract_invalid"),
        ({"artifacts": "bad"}, "manifest_contract_invalid"),
    ),
)
def test_manifest_builder_rejects_malformed_surface(linear: Fixture, change: dict[str, object], reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        _build_with(linear, **change)


def test_duplicate_artifact_is_rejected(linear: Fixture) -> None:
    with pytest.raises(ValueError, match="artifact_id_duplicate"):
        _build_with(linear, artifacts=linear.manifest.artifacts + (linear.manifest.artifacts[0],))


@pytest.mark.parametrize("field", ["artifact_id", "artifact_type", "transaction_id", "owner_root_id", "authority_class", "lifecycle_state"])
def test_empty_artifact_string_field_is_rejected(linear: Fixture, field: str) -> None:
    artifact = replace(linear.manifest.artifacts[0], **{field: ""})
    with pytest.raises(ValueError):
        _build_with(linear, artifacts=(artifact, *linear.manifest.artifacts[1:]))


def test_artifact_transaction_mismatch_is_rejected(linear: Fixture) -> None:
    artifact = replace(linear.manifest.artifacts[0], transaction_id="other")
    with pytest.raises(ValueError, match="artifact_transaction_mismatch"):
        _build_with(linear, artifacts=(artifact, *linear.manifest.artifacts[1:]))


def test_unknown_schema_is_rejected(linear: Fixture) -> None:
    artifact = replace(linear.manifest.artifacts[0], schema_version="v2")
    with pytest.raises(ValueError, match="artifact_schema_unknown"):
        _build_with(linear, artifacts=(artifact, *linear.manifest.artifacts[1:]))


def test_malformed_payload_hash_is_rejected(linear: Fixture) -> None:
    artifact = replace(linear.manifest.artifacts[0], payload_hash="0" * 63)
    with pytest.raises(ValueError, match="artifact_ref_invalid"):
        _build_with(linear, artifacts=(artifact, *linear.manifest.artifacts[1:]))


@pytest.mark.parametrize("binding_field", ["root_ownership_bindings", "evidence_class_bindings", "authority_class_bindings"])
@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate"])
def test_missing_extra_duplicate_bindings_are_rejected(linear: Fixture, binding_field: str, mutation: str) -> None:
    values = getattr(linear.manifest, binding_field)
    if mutation == "missing":
        changed = values[:-1]
    elif mutation == "extra":
        changed = values + (values[-1].__class__("unknown", getattr(values[-1], fields(values[-1])[-1].name)),)
    else:
        changed = values + (values[-1],)
    with pytest.raises(ValueError):
        _build_with(linear, **{binding_field: changed})


def test_root_binding_mismatch_is_rejected(linear: Fixture) -> None:
    changed = (replace(linear.manifest.root_ownership_bindings[0], owner_root_id="root:x"), *linear.manifest.root_ownership_bindings[1:])
    with pytest.raises(ValueError, match="root_ownership_binding_mismatch"):
        _build_with(linear, root_ownership_bindings=changed)


def test_authority_binding_mismatch_is_rejected(linear: Fixture) -> None:
    changed = (replace(linear.manifest.authority_class_bindings[0], authority_class="OTHER"), *linear.manifest.authority_class_bindings[1:])
    with pytest.raises(ValueError, match="authority_class_binding_mismatch"):
        _build_with(linear, authority_class_bindings=changed)


def test_empty_evidence_class_is_rejected(linear: Fixture) -> None:
    changed = (replace(linear.manifest.evidence_class_bindings[0], evidence_class=""), *linear.manifest.evidence_class_bindings[1:])
    with pytest.raises(ValueError, match="evidence_class_binding_mismatch"):
        _build_with(linear, evidence_class_bindings=changed)


def test_duplicate_dependency_edge_is_rejected(linear: Fixture) -> None:
    with pytest.raises(ValueError, match="dependency_edge_duplicate"):
        _build_with(linear, dependency_edges=linear.manifest.dependency_edges + (linear.manifest.dependency_edges[0],))


@pytest.mark.parametrize("edge", [core.ArtifactDependencyEdgeV01("test:scope", "test:scope"), core.ArtifactDependencyEdgeV01("unknown", "test:scope"), core.ArtifactDependencyEdgeV01("test:evidence", "unknown")])
def test_invalid_dependency_endpoint_is_rejected(linear: Fixture, edge: core.ArtifactDependencyEdgeV01) -> None:
    with pytest.raises(ValueError, match="dependency_edge_invalid"):
        _build_with(linear, dependency_edges=(edge,))


def test_cycle_is_rejected_when_timeline_order_is_disabled() -> None:
    fixture = _fixture("linear", ordered=False)
    edges = (
        core.ArtifactDependencyEdgeV01("test:scope", "test:evidence"),
        core.ArtifactDependencyEdgeV01("test:evidence", "test:scope"),
    )
    with pytest.raises(ValueError, match="dependency_cycle"):
        _build_with(fixture, dependency_edges=edges)


def test_forward_dependency_is_rejected_when_ordered(linear: Fixture) -> None:
    edge = core.ArtifactDependencyEdgeV01("test:scope", "test:evidence")
    with pytest.raises(ValueError, match="dependency_forward_not_allowed"):
        _build_with(linear, dependency_edges=(edge,))


def test_forward_acyclic_dependency_is_allowed_when_unordered() -> None:
    fixture = _fixture("linear", ordered=False)
    manifest = _build_with(fixture, dependency_edges=(core.ArtifactDependencyEdgeV01("test:scope", "test:evidence"),))
    assert manifest.dependency_edge_count == 1


@pytest.mark.parametrize("kind", ["linear", "fanout"])
def test_no_expected_hash_is_self_consistent_unanchored(kind: str) -> None:
    fixture = _fixture(kind)
    report = core.verify_artifact_manifest_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows)
    assert report.verification_status == core.STATUS_SELF_CONSISTENT_UNANCHORED
    assert report.verification_errors == ()
    assert report.expected_manifest_hash_supplied is False


@pytest.mark.parametrize("kind", ["linear", "fanout"])
def test_matching_expected_hash_passes(kind: str) -> None:
    fixture = _fixture(kind)
    report = core.verify_artifact_manifest_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows, expected_manifest_hash=fixture.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_PASS
    assert report.expected_manifest_hash_verified is True


@pytest.mark.parametrize("expected", ["bad", "0" * 63, "G" * 64, True, b"x"])
def test_malformed_expected_hash_fails_closed(linear: Fixture, expected: object) -> None:
    report = core.verify_artifact_manifest_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=expected)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "expected_manifest_hash_invalid" in report.verification_errors


def test_mismatching_expected_hash_fails_closed(linear: Fixture) -> None:
    report = core.verify_artifact_manifest_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash="0" * 64)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "expected_manifest_hash_mismatch" in report.verification_errors


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("profile_id", "other", "seal_profile_invalid"),
        ("manifest_version", "v9", "seal_profile_invalid"),
        ("artifact_schema_version", "v9", "seal_profile_invalid"),
        ("canonicalization_profile_id", "other", "canonicalization_profile_invalid"),
        ("hash_algorithm", "OTHER", "seal_profile_invalid"),
        ("hash_encoding", "OTHER", "seal_profile_invalid"),
        ("payload_domain", "other", "seal_profile_invalid"),
        ("manifest_domain", "other", "seal_profile_invalid"),
        ("replay_domain", "other", "seal_profile_invalid"),
        ("timeline_order_required", 1, "seal_profile_invalid"),
    ),
)
def test_each_fixed_profile_mutation_fails_closed(linear: Fixture, field: str, value: object, reason: str) -> None:
    changed = replace(linear.manifest, seal_profile=replace(linear.manifest.seal_profile, **{field: value}))
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert reason in report.verification_errors


@pytest.mark.parametrize("payload_rows", [[], (("bad",),), (("test:scope", {}), ("test:scope", {})), (("unknown", {}),)])
def test_malformed_payload_rows_fail_closed(linear: Fixture, payload_rows: object) -> None:
    report = core.verify_artifact_manifest_v01(manifest=linear.manifest, payload_rows=payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert any(reason.startswith("payload_rows_") for reason in report.verification_errors)


def test_changed_payload_fails_closed(linear: Fixture) -> None:
    rows = ((linear.payload_rows[0][0], {"n": 99}), *linear.payload_rows[1:])
    report = core.verify_artifact_manifest_v01(manifest=linear.manifest, payload_rows=rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "payload_hash_mismatch" in report.verification_errors


@pytest.mark.parametrize("field", ["artifact_count", "dependency_edge_count", "root_ownership_binding_count", "evidence_class_binding_count", "authority_class_binding_count"])
@pytest.mark.parametrize("value", [999, True])
def test_each_manifest_count_mutation_fails_closed(linear: Fixture, field: str, value: object) -> None:
    changed = replace(linear.manifest, **{field: value})
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "manifest_derived_count_mismatch" in report.verification_errors


def test_tampered_manifest_hash_fails_closed(linear: Fixture) -> None:
    changed = replace(linear.manifest, manifest_hash="0" * 64)
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "manifest_hash_mismatch" in report.verification_errors


@pytest.mark.parametrize("field", ["artifact_id", "artifact_type", "schema_version", "transaction_id", "owner_root_id", "authority_class", "lifecycle_state", "payload_hash"])
def test_each_artifact_field_mutation_fails_closed(linear: Fixture, field: str) -> None:
    values = {
        "artifact_id": "test:changed",
        "artifact_type": "changed",
        "schema_version": "v2",
        "transaction_id": "txn:changed",
        "owner_root_id": "root:changed",
        "authority_class": "CHANGED",
        "lifecycle_state": "CHANGED",
        "payload_hash": "0" * 64,
    }
    artifact = replace(linear.manifest.artifacts[0], **{field: values[field]})
    changed = replace(linear.manifest, artifacts=(artifact, *linear.manifest.artifacts[1:]))
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize("binding_field", ["root_ownership_bindings", "evidence_class_bindings", "authority_class_bindings"])
def test_each_binding_class_mutation_fails_closed(linear: Fixture, binding_field: str) -> None:
    bindings = getattr(linear.manifest, binding_field)
    last_field = fields(bindings[0])[-1].name
    changed_binding = replace(bindings[0], **{last_field: "CHANGED"})
    changed = replace(linear.manifest, **{binding_field: (changed_binding, *bindings[1:])})
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize("field", ["artifact_id", "depends_on_artifact_id"])
def test_each_dependency_edge_field_mutation_fails_closed(linear: Fixture, field: str) -> None:
    edge = replace(linear.manifest.dependency_edges[0], **{field: "unknown"})
    changed = replace(linear.manifest, dependency_edges=(edge, *linear.manifest.dependency_edges[1:]))
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED


def test_artifact_order_mutation_fails_closed(linear: Fixture) -> None:
    changed = replace(linear.manifest, artifacts=tuple(reversed(linear.manifest.artifacts)))
    report = core.verify_artifact_manifest_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize("value", [None, {}, [], object(), "bad"])
def test_verifier_malformed_inputs_return_results(value: object) -> None:
    report = core.verify_artifact_manifest_v01(manifest=value, payload_rows=value, expected_manifest_hash=value)
    assert isinstance(report, core.SealVerificationResultV01)
    assert report.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert not any("object at" in reason for reason in report.verification_errors)


@pytest.mark.parametrize("kind", ["linear", "fanout"])
def test_valid_replay_passes_and_reconstructs(kind: str) -> None:
    fixture = _fixture(kind)
    replay = core.verify_artifact_replay_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows, expected_manifest_hash=fixture.manifest.manifest_hash)
    assert replay.replay_status == core.STATUS_PASS
    assert replay.reconstructed_artifact_ids == tuple(row[0] for row in fixture.payload_rows)
    assert replay.reconstructed_artifact_types == tuple(item.artifact_type for item in fixture.manifest.artifacts)
    assert replay.reconstructed_owner_root_ids == tuple(item.owner_root_id for item in fixture.manifest.artifacts)
    assert replay.reconstructed_dependency_edges == fixture.manifest.dependency_edges


def test_replay_dependency_counts_are_exact(fanout: Fixture) -> None:
    replay = core.verify_artifact_replay_v01(manifest=fanout.manifest, payload_rows=fanout.payload_rows, expected_manifest_hash=fanout.manifest.manifest_hash)
    assert replay.reconstructed_dependency_counts == (0, 1, 1, 2, 1, 1)


def test_replay_id_is_deterministic(linear: Fixture) -> None:
    first = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    second = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert first.replay_id == second.replay_id
    assert re.fullmatch(r"[0-9a-f]{64}", first.replay_id)


def test_replay_requires_expected_hash(linear: Fixture) -> None:
    replay = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=None)
    assert replay.replay_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert replay.replay_errors == ("replay_expected_manifest_hash_required",)


@pytest.mark.parametrize("expected", ["bad", "0" * 64, True])
def test_bad_expected_hash_blocks_replay(linear: Fixture, expected: object) -> None:
    replay = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=expected)
    assert replay.replay_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert replay.replay_errors == ("replay_manifest_verification_failed",)


def test_changed_payload_blocks_replay(linear: Fixture) -> None:
    rows = ((linear.payload_rows[0][0], {"changed": True}), *linear.payload_rows[1:])
    replay = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert replay.replay_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert replay.reconstructed_artifact_ids == ()
    assert replay.artifact_count == 0


def test_changed_manifest_blocks_replay(linear: Fixture) -> None:
    changed = replace(linear.manifest, manifest_hash="0" * 64)
    replay = core.verify_artifact_replay_v01(manifest=changed, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert replay.replay_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert replay.integrity_verified is False


@pytest.mark.parametrize("field", REPLAY_ZERO_FIELDS)
def test_every_replay_counter_is_zero(linear: Fixture, field: str) -> None:
    replay = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert getattr(replay, field) == 0
    assert type(getattr(replay, field)) is int


def test_replay_does_not_mutate_inputs(linear: Fixture) -> None:
    before_manifest = core.artifact_manifest_to_plain_dict_v01(linear.manifest)
    before_payloads = core.canonical_json_bytes_v01(linear.payload_rows)
    core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    assert core.artifact_manifest_to_plain_dict_v01(linear.manifest) == before_manifest
    assert core.canonical_json_bytes_v01(linear.payload_rows) == before_payloads


def test_nested_manifest_tuples_are_immutable(linear: Fixture) -> None:
    assert type(linear.manifest.artifacts) is tuple
    assert type(linear.manifest.dependency_edges) is tuple
    with pytest.raises(Exception):
        linear.manifest.artifacts[0].artifact_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("projection", ["manifest", "seal", "replay"])
def test_public_projections_are_json_safe_and_independent(linear: Fixture, projection: str) -> None:
    seal = core.verify_artifact_manifest_v01(manifest=linear.manifest, payload_rows=linear.payload_rows)
    replay = core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash)
    source: object
    function: Callable[[Any], dict[str, object]]
    if projection == "manifest":
        source, function = linear.manifest, core.artifact_manifest_to_plain_dict_v01
    elif projection == "seal":
        source, function = seal, core.seal_verification_result_to_plain_dict_v01
    else:
        source, function = replay, core.replay_verification_result_to_plain_dict_v01
    first = function(source)
    second = function(source)
    assert first == second and first is not second
    json.dumps(first, sort_keys=True, allow_nan=False)
    first.clear()
    assert function(source) == second


def test_projection_contains_no_tuple_or_bytes(linear: Fixture) -> None:
    value = core.replay_verification_result_to_plain_dict_v01(core.verify_artifact_replay_v01(manifest=linear.manifest, payload_rows=linear.payload_rows, expected_manifest_hash=linear.manifest.manifest_hash))

    def forbidden(item: object) -> bool:
        if isinstance(item, (tuple, bytes, bytearray, memoryview)):
            return True
        if isinstance(item, dict):
            return any(forbidden(key) or forbidden(value) for key, value in item.items())
        if isinstance(item, list):
            return any(forbidden(child) for child in item)
        return False

    assert forbidden(value) is False


def test_static_import_boundary_is_domain_neutral() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(name.startswith("hedgehog") for name in imported)
    assert not any(name.startswith(("demo", "tests")) for name in imported)
    assert not imported & {"cryptography", "pathlib", "os", "sys", "subprocess", "tempfile", "shutil", "importlib", "requests", "socket", "urllib"}


@pytest.mark.parametrize("token", ["hedgehog.domains", "gemini", "requests", "socket", "urllib", ".tmp", "Airline", "Supplier", "Water Filter"])
def test_static_forbidden_tokens_are_absent(token: str) -> None:
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_static_no_file_io_or_package_discovery() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for token in ("open(", ".read_text(", ".read_bytes(", ".write_text(", ".write_bytes(", ".glob(", ".rglob(", "os.walk"):
        assert token not in source


def test_static_no_module_level_mutable_registry() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            assert not isinstance(value, (ast.Dict, ast.List, ast.Set))


def test_replay_accepts_no_callback_or_effect_hook() -> None:
    signature = inspect.signature(core.verify_artifact_replay_v01)
    assert tuple(signature.parameters) == ("manifest", "payload_rows", "expected_manifest_hash")


def test_plain_projection_functions_are_explicit_not_reflection_dumps() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "asdict" not in source
    assert "__dict__" not in source


@pytest.mark.parametrize(
    "error_type",
    (OSError, HostileInputError),
    ids=("oserror", "custom_exception"),
)
def test_mapping_items_ordinary_exception_is_sanitized(
    error_type: type[Exception],
) -> None:
    with pytest.raises(ValueError) as captured:
        core.canonical_json_bytes_v01(RaisingItemsMapping(error_type))
    assert captured.value.args == ("json_mapping_invalid",)
    assert captured.value.__cause__ is None
    assert "hostile caller text" not in str(captured.value)


def test_sanitized_canonicalization_exception_has_no_cause() -> None:
    with pytest.raises(ValueError) as captured:
        core.canonical_json_bytes_v01(RaisingItemsMapping(OSError))
    assert captured.value.args == ("json_mapping_invalid",)
    assert captured.value.__cause__ is None


def test_mapping_items_duplicate_string_key_is_rejected() -> None:
    with pytest.raises(ValueError) as captured:
        core.canonical_json_bytes_v01(DuplicateItemsMapping())
    assert captured.value.args == ("json_mapping_duplicate_key",)
    assert captured.value.__cause__ is None


def test_huge_integer_has_stable_canonicalization_reason() -> None:
    with pytest.raises(ValueError) as captured:
        core.canonical_json_bytes_v01(10**10000)
    assert captured.value.args == ("canonical_json_value_invalid",)
    assert captured.value.__cause__ is None
    assert "Exceeds" not in str(captured.value)


@pytest.mark.parametrize(
    "error_type",
    (OSError, HostileInputError),
    ids=("oserror", "custom_exception"),
)
def test_hostile_payload_mapping_fails_manifest_verification_closed(
    linear: Fixture,
    error_type: type[Exception],
) -> None:
    payload_rows = (
        (linear.payload_rows[0][0], RaisingItemsMapping(error_type)),
        *linear.payload_rows[1:],
    )
    result = core.verify_artifact_manifest_v01(
        manifest=linear.manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=linear.manifest.manifest_hash,
    )
    assert result.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert result.verification_errors == ("payload_rows_invalid",)
    assert "hostile caller text" not in repr(result.verification_errors)


@pytest.mark.parametrize("error_type", (RuntimeError, OSError))
def test_hostile_profile_equality_fails_manifest_verification_closed(
    linear: Fixture,
    error_type: type[Exception],
) -> None:
    profile = replace(
        linear.manifest.seal_profile,
        profile_id=RaisingEquality(error_type),
    )
    result = core.verify_artifact_manifest_v01(
        manifest=replace(linear.manifest, seal_profile=profile),
        payload_rows=linear.payload_rows,
        expected_manifest_hash=linear.manifest.manifest_hash,
    )
    assert result.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert "seal_profile_invalid" in result.verification_errors
    assert "hostile caller text" not in repr(result.verification_errors)


@pytest.mark.parametrize("error_type", (RuntimeError, OSError))
def test_hostile_profile_equality_fails_replay_closed(
    linear: Fixture,
    error_type: type[Exception],
) -> None:
    profile = replace(
        linear.manifest.seal_profile,
        replay_domain=RaisingEquality(error_type),
    )
    result = core.verify_artifact_replay_v01(
        manifest=replace(linear.manifest, seal_profile=profile),
        payload_rows=linear.payload_rows,
        expected_manifest_hash=linear.manifest.manifest_hash,
    )
    assert result.replay_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert result.replay_errors == ("replay_manifest_verification_failed",)
    assert "hostile caller text" not in repr(result.replay_errors)


@pytest.mark.parametrize(
    "artifact_id",
    ([], {}, RaisingEquality(RuntimeError)),
    ids=("list", "mapping", "hostile_hash_and_equality"),
)
def test_unhashable_or_hostile_artifact_id_has_stable_builder_failure(
    linear: Fixture,
    artifact_id: object,
) -> None:
    artifact = replace(linear.manifest.artifacts[0], artifact_id=artifact_id)
    with pytest.raises(ValueError) as captured:
        _build_with(
            linear,
            artifacts=(artifact, *linear.manifest.artifacts[1:]),
        )
    assert captured.value.args == ("artifact_ref_invalid",)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize(
    "schema_version",
    (None, [], {}, RaisingEquality(OSError)),
    ids=("none", "list", "mapping", "hostile_equality"),
)
def test_non_string_schema_version_has_stable_builder_failure(
    linear: Fixture,
    schema_version: object,
) -> None:
    artifact = linear.manifest.artifacts[0]
    with pytest.raises(ValueError) as captured:
        core.build_canonical_artifact_ref_v01(
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            schema_version=schema_version,
            transaction_id=artifact.transaction_id,
            owner_root_id=artifact.owner_root_id,
            authority_class=artifact.authority_class,
            lifecycle_state=artifact.lifecycle_state,
            payload=linear.payload_rows[0][1],
            profile=linear.manifest.seal_profile,
        )
    assert captured.value.args == ("artifact_schema_unknown",)
    assert captured.value.__cause__ is None


def test_malformed_manifest_projection_has_stable_failure(linear: Fixture) -> None:
    malformed = replace(linear.manifest, seal_profile=object())
    with pytest.raises(ValueError) as captured:
        core.artifact_manifest_to_plain_dict_v01(malformed)
    assert captured.value.args == ("manifest_contract_invalid",)
    assert captured.value.__cause__ is None


def test_malformed_seal_result_projection_has_stable_failure(linear: Fixture) -> None:
    result = core.verify_artifact_manifest_v01(
        manifest=linear.manifest,
        payload_rows=linear.payload_rows,
    )
    malformed = replace(result, verification_status=object())
    with pytest.raises(ValueError) as captured:
        core.seal_verification_result_to_plain_dict_v01(malformed)
    assert captured.value.args == ("seal_verification_result_invalid",)
    assert captured.value.__cause__ is None


def test_malformed_replay_result_projection_has_stable_failure(
    linear: Fixture,
) -> None:
    result = core.verify_artifact_replay_v01(
        manifest=linear.manifest,
        payload_rows=linear.payload_rows,
        expected_manifest_hash=linear.manifest.manifest_hash,
    )
    malformed = replace(result, replay_status=object())
    with pytest.raises(ValueError) as captured:
        core.replay_verification_result_to_plain_dict_v01(malformed)
    assert captured.value.args == ("replay_verification_result_invalid",)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize("expected_hash", (None, "explicitly-supplied"))
def test_early_manifest_failure_preserves_expected_hash_supplied_fact(
    expected_hash: object,
) -> None:
    result = core.verify_artifact_manifest_v01(
        manifest=object(),
        payload_rows=(),
        expected_manifest_hash=expected_hash,
    )
    assert result.verification_status == core.STATUS_BLOCKED_FAIL_CLOSED
    assert result.expected_manifest_hash_supplied is (expected_hash is not None)
    assert result.expected_manifest_hash_verified is False


@pytest.mark.parametrize(
    ("fixture_id", "identity_field", "expected"),
    (
        (
            "linear",
            "manifest_hash",
            "997439edf41e4d9a0498efd6442c5386a3f699ed9bcac79a8e318364b547b953",
        ),
        (
            "linear",
            "replay_id",
            "f9594a4c9ce0ad4e9de645be2c683764d5c04244ce6537a544809040ff3d28bc",
        ),
        (
            "fanout",
            "manifest_hash",
            "ee2195f9f51ea70e3968fdb15522600ec8bf96dca5589d4e08ae7b1053e6f41b",
        ),
        (
            "fanout",
            "replay_id",
            "0b325075ea8db57afd2d492444b6513486974498c5b076f526421bab4d4b5665",
        ),
    ),
)
def test_living_fixture_deterministic_identity_is_frozen(
    fixture_id: str,
    identity_field: str,
    expected: str,
) -> None:
    from demo import run_living_gauntlet_v01 as living

    records = living._collect_generic_integrity_replay_fixture_records_v01()
    record = next(row for row in records if row["fixture_id"] == fixture_id)
    source = record["manifest"] if identity_field == "manifest_hash" else record["replay"]
    assert getattr(source, identity_field) == expected


def test_unexpected_manifest_boundary_exception_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(**kwargs: object) -> core.SealVerificationResultV01:
        raise OSError("hostile caller text")

    monkeypatch.setattr(core, "_verify_artifact_manifest_impl", fail)
    result = core.verify_artifact_manifest_v01(
        manifest=object(),
        payload_rows=(),
        expected_manifest_hash="explicit",
    )
    assert result.verification_errors == ("manifest_contract_invalid",)
    assert result.expected_manifest_hash_supplied is True


def test_unexpected_replay_boundary_exception_is_sanitized(
    linear: Fixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(**kwargs: object) -> core.SealVerificationResultV01:
        raise HostileInputError("hostile caller text")

    monkeypatch.setattr(core, "verify_artifact_manifest_v01", fail)
    result = core.verify_artifact_replay_v01(
        manifest=linear.manifest,
        payload_rows=linear.payload_rows,
        expected_manifest_hash=linear.manifest.manifest_hash,
    )
    assert result.replay_errors == ("replay_manifest_verification_failed",)


@pytest.mark.parametrize("error_type", (KeyboardInterrupt, SystemExit, GeneratorExit))
def test_canonicalization_does_not_catch_base_exceptions(
    error_type: type[BaseException],
) -> None:
    class RaisingBaseMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            raise KeyError(key)

        def __iter__(self):
            return iter(())

        def __len__(self) -> int:
            return 0

        def items(self):
            raise error_type()

    with pytest.raises(error_type):
        core.canonical_json_bytes_v01(RaisingBaseMapping())
