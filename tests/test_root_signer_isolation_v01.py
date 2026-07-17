from __future__ import annotations

import ast
import copy
from dataclasses import dataclass, fields, is_dataclass, replace
import inspect
import json
from pathlib import Path
import pickle
import re
from typing import Any, Callable

import cryptography
import pytest

from hedgehog import kernel
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.kernel import root_signer_isolation_v01 as signer


MODULE_PATH = Path(signer.__file__).resolve()
ROOT_ROWS = (
    ("root:client_os_001", "commitment:test:client", "scope:client"),
    ("root:mock_airline_al", "commitment:test:airline", "scope:airline"),
    ("root:mock_bank_a", "commitment:test:bank", "scope:bank"),
)
EXPECTED_PUBLIC_TYPES = {
    "RootSignerCapabilityV01",
    "TrustedRootKeySetV01",
    "RootOwnedCommitmentV01",
    "RootSignatureV01",
    "RootSignatureVerificationResultV01",
}
EXPECTED_PUBLIC_FUNCTIONS = {
    "generate_root_signer_capability_v01",
    "build_trusted_root_key_set_v01",
    "build_root_owned_commitment_v01",
    "sign_root_owned_commitment_v01",
    "verify_root_signature_v01",
    "trusted_root_key_set_to_plain_dict_v01",
    "root_owned_commitment_to_plain_dict_v01",
    "root_signature_to_plain_dict_v01",
    "root_signature_verification_result_to_plain_dict_v01",
}
EXPECTED_SIGNER_EXPORTS = (
    "RootSignerCapabilityV01",
    "TrustedRootKeySetV01",
    "RootOwnedCommitmentV01",
    "RootSignatureV01",
    "RootSignatureVerificationResultV01",
    "generate_root_signer_capability_v01",
    "build_trusted_root_key_set_v01",
    "build_root_owned_commitment_v01",
    "sign_root_owned_commitment_v01",
    "verify_root_signature_v01",
    "trusted_root_key_set_to_plain_dict_v01",
    "root_owned_commitment_to_plain_dict_v01",
    "root_signature_to_plain_dict_v01",
    "root_signature_verification_result_to_plain_dict_v01",
)


@dataclass(frozen=True)
class ConformanceFixture:
    capabilities: tuple[signer.RootSignerCapabilityV01, ...]
    key_set: signer.TrustedRootKeySetV01
    commitments: tuple[signer.RootOwnedCommitmentV01, ...]
    signatures: tuple[signer.RootSignatureV01, ...]


class HostileEquality:
    def __eq__(self, other: object) -> bool:
        raise OSError("hostile caller content")


class HostileIterator:
    def __iter__(self):
        raise OSError("hostile caller content")


class CustomHostileError(Exception):
    pass


def _fixture() -> ConformanceFixture:
    capabilities = tuple(
        signer.generate_root_signer_capability_v01(root_id=row[0])
        for row in ROOT_ROWS
    )
    key_set = signer.build_trusted_root_key_set_v01(
        capabilities=tuple(reversed(capabilities))
    )
    manifest_hash = integrity.domain_separated_sha256_hex_v01(
        domain="test.root_signer.manifest.v01",
        payload=integrity.canonical_json_bytes_v01({"fixture": "signer"}),
    )
    commitments = tuple(
        signer.build_root_owned_commitment_v01(
            commitment_id=row[1],
            transaction_id="txn:test:root_signer:001",
            owner_root_id=row[0],
            commitment_scope=row[2],
            artifact_hash=integrity.domain_separated_sha256_hex_v01(
                domain="test.root_signer.artifact.v01",
                payload=integrity.canonical_json_bytes_v01(
                    {"root_id": row[0]}
                ),
            ),
            manifest_hash=manifest_hash,
            key_id=capability.key_id,
        )
        for row, capability in zip(ROOT_ROWS, capabilities)
    )
    signatures = tuple(
        signer.sign_root_owned_commitment_v01(
            capability=capability,
            trusted_key_set=key_set,
            commitment=commitment,
        )
        for capability, commitment in zip(capabilities, commitments)
    )
    return ConformanceFixture(capabilities, key_set, commitments, signatures)


@pytest.fixture(scope="module")
def conformance() -> ConformanceFixture:
    return _fixture()


def _commitment(
    capability: signer.RootSignerCapabilityV01,
    **overrides: object,
) -> signer.RootOwnedCommitmentV01:
    values: dict[str, object] = {
        "commitment_id": "commitment:test:001",
        "transaction_id": "txn:test:001",
        "owner_root_id": capability.root_id,
        "commitment_scope": "scope:test",
        "artifact_hash": "1" * 64,
        "manifest_hash": "2" * 64,
        "key_id": capability.key_id,
    }
    values.update(overrides)
    return signer.build_root_owned_commitment_v01(**values)  # type: ignore[arg-type]


def _contains_tuple_or_bytes(value: object) -> bool:
    if isinstance(value, (tuple, bytes, bytearray, memoryview)):
        return True
    if isinstance(value, dict):
        return any(
            _contains_tuple_or_bytes(key) or _contains_tuple_or_bytes(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_tuple_or_bytes(item) for item in value)
    return False


def _different_sha256(value: str) -> str:
    replacement = "0" if value[0] != "0" else "1"
    return replacement + value[1:]


def test_exact_public_type_set() -> None:
    observed = {
        name
        for name, value in vars(signer).items()
        if inspect.isclass(value) and not name.startswith("_")
    }
    assert observed == EXPECTED_PUBLIC_TYPES


def test_exact_public_function_set() -> None:
    observed = {
        name
        for name, value in vars(signer).items()
        if inspect.isfunction(value) and not name.startswith("_")
    }
    assert observed == EXPECTED_PUBLIC_FUNCTIONS


@pytest.mark.parametrize(
    ("contract", "expected"),
    (
        (
            signer.TrustedRootKeySetV01,
            (
                "key_set_version",
                "key_set_id",
                "algorithm",
                "root_ids",
                "key_ids",
                "public_key_hexes",
            ),
        ),
        (
            signer.RootOwnedCommitmentV01,
            (
                "commitment_version",
                "commitment_id",
                "transaction_id",
                "owner_root_id",
                "commitment_scope",
                "artifact_hash",
                "manifest_hash",
                "key_id",
            ),
        ),
        (
            signer.RootSignatureV01,
            (
                "signature_version",
                "algorithm",
                "commitment_id",
                "transaction_id",
                "owner_root_id",
                "key_id",
                "commitment_hash",
                "signature_hex",
            ),
        ),
        (
            signer.RootSignatureVerificationResultV01,
            (
                "verification_status",
                "verification_errors",
                "trusted_key_set_verified",
                "commitment_verified",
                "signature_contract_verified",
                "trusted_root_present",
                "key_id_verified",
                "public_key_verified",
                "commitment_hash_verified",
                "signature_verified",
                "root_isolation_verified",
                "owner_root_id",
                "key_id",
                "commitment_hash",
            ),
        ),
    ),
)
def test_exact_frozen_dataclass_field_order(
    contract: type[object], expected: tuple[str, ...]
) -> None:
    assert is_dataclass(contract)
    assert contract.__dataclass_params__.frozen is True
    assert tuple(field.name for field in fields(contract)) == expected


def test_package_preserves_g1a1_all_and_reexports_exact_signer_surface() -> None:
    assert isinstance(kernel.__all__, tuple)
    assert len(kernel.__all__) == 19
    assert all(getattr(kernel, name) is not None for name in kernel.__all__)
    assert all(getattr(kernel, name) is getattr(signer, name) for name in EXPECTED_SIGNER_EXPORTS)
    assert not set(EXPECTED_SIGNER_EXPORTS).intersection(kernel.__all__)


def test_no_private_key_export_or_capability_projection_api() -> None:
    assert not any("private" in name for name in EXPECTED_PUBLIC_FUNCTIONS)
    assert "root_signer_capability_to_plain_dict_v01" not in vars(signer)


def test_cryptography_dependency_version_is_exact() -> None:
    assert cryptography.__version__ == "48.0.0"


def test_algorithm_and_encoding_constants_are_exact() -> None:
    assert signer.ALGORITHM == "Ed25519"
    assert signer.PUBLIC_KEY_ENCODING == "raw_lowercase_hex"
    assert signer.SIGNATURE_ENCODING == "lowercase_hex"


def test_official_ed25519_primitives_are_used() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "Ed25519PrivateKey" in source
    assert "Ed25519PublicKey" in source
    assert "InvalidSignature" in source


@pytest.mark.parametrize("forbidden", ("hmac", "RSA", "ECDSA", "curve25519"))
def test_no_signature_algorithm_substitute(forbidden: str) -> None:
    assert forbidden not in MODULE_PATH.read_text(encoding="utf-8")


def test_factory_creates_exact_opaque_capability() -> None:
    capability = signer.generate_root_signer_capability_v01(root_id="root:test")
    assert type(capability) is signer.RootSignerCapabilityV01
    assert capability.root_id == "root:test"
    assert capability.algorithm == signer.ALGORITHM


def test_direct_capability_construction_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="root_signer_capability_direct_construction_forbidden",
    ):
        signer.RootSignerCapabilityV01()


def test_capability_has_no_dict_and_vars_is_rejected(
    conformance: ConformanceFixture,
) -> None:
    capability = conformance.capabilities[0]
    assert not hasattr(capability, "__dict__")
    with pytest.raises(TypeError):
        vars(capability)


def test_capability_exact_public_properties() -> None:
    properties = {
        name
        for name, value in vars(signer.RootSignerCapabilityV01).items()
        if isinstance(value, property)
    }
    assert properties == {"root_id", "key_id", "algorithm", "public_key_hex"}


@pytest.mark.parametrize("property_name", ("root_id", "key_id", "algorithm", "public_key_hex"))
def test_capability_public_properties_are_immutable(
    conformance: ConformanceFixture, property_name: str
) -> None:
    with pytest.raises(AttributeError, match="root_signer_capability_immutable"):
        setattr(conformance.capabilities[0], property_name, "changed")


def test_capability_repr_is_public_identity_only(
    conformance: ConformanceFixture,
) -> None:
    capability = conformance.capabilities[0]
    rendered = repr(capability)
    assert rendered.startswith("RootSignerCapabilityV01(")
    assert capability.root_id in rendered
    assert capability.key_id in rendered
    assert capability.public_key_hex in rendered
    assert "_private_key" not in rendered
    assert "object at" not in rendered


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_capability_pickle_is_rejected_stably(
    conformance: ConformanceFixture, protocol: int
) -> None:
    with pytest.raises(
        TypeError, match="root_signer_capability_not_serializable"
    ):
        pickle.dumps(conformance.capabilities[0], protocol=protocol)


def test_copy_and_deepcopy_do_not_duplicate_capability(
    conformance: ConformanceFixture,
) -> None:
    capability = conformance.capabilities[0]
    assert copy.copy(capability) is capability
    assert copy.deepcopy(capability) is capability


def test_capability_uses_identity_equality_and_hash(
    conformance: ConformanceFixture,
) -> None:
    first, second = conformance.capabilities[:2]
    assert first == first
    assert first != second
    assert type(hash(first)) is int


def test_source_contains_no_private_key_byte_export() -> None:
    assert "private_bytes" not in MODULE_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("slot", ("_public_key_hex", "_key_id", "_private_key"))
def test_forged_capability_fails_safely(slot: str) -> None:
    capability = signer.generate_root_signer_capability_v01(root_id="root:forged")
    value: object = "0" * 64 if slot != "_private_key" else object()
    object.__setattr__(capability, slot, value)
    with pytest.raises(ValueError, match="signer_capability_invalid"):
        signer.build_trusted_root_key_set_v01(capabilities=(capability,))


@pytest.mark.parametrize("root_id", ("", None, True, 1, "\ud800"))
def test_capability_root_id_validation(root_id: object) -> None:
    with pytest.raises(ValueError, match="signer_root_id_invalid"):
        signer.generate_root_signer_capability_v01(root_id=root_id)  # type: ignore[arg-type]


def test_public_key_and_key_id_shapes(conformance: ConformanceFixture) -> None:
    for capability in conformance.capabilities:
        assert re.fullmatch(r"[0-9a-f]{64}", capability.public_key_hex)
        assert re.fullmatch(r"[0-9a-f]{64}", capability.key_id)


def test_three_capabilities_have_distinct_public_keys_and_key_ids(
    conformance: ConformanceFixture,
) -> None:
    assert len({item.public_key_hex for item in conformance.capabilities}) == 3
    assert len({item.key_id for item in conformance.capabilities}) == 3


def test_changed_root_id_changes_derived_key_id(
    conformance: ConformanceFixture,
) -> None:
    capability = conformance.capabilities[0]
    first = signer._derive_key_id(
        root_id=capability.root_id,
        public_key_hex=capability.public_key_hex,
    )
    second = signer._derive_key_id(
        root_id="root:different",
        public_key_hex=capability.public_key_hex,
    )
    assert first != second


def test_valid_one_root_key_set() -> None:
    capability = signer.generate_root_signer_capability_v01(root_id="root:one")
    key_set = signer.build_trusted_root_key_set_v01(capabilities=(capability,))
    assert key_set.root_ids == ("root:one",)
    assert key_set.key_ids == (capability.key_id,)


def test_valid_three_root_key_set_is_canonically_ordered(
    conformance: ConformanceFixture,
) -> None:
    assert conformance.key_set.root_ids == tuple(
        sorted(item.root_id for item in conformance.capabilities)
    )


def test_key_set_id_is_deterministic_for_identical_public_bindings(
    conformance: ConformanceFixture,
) -> None:
    reversed_set = signer.build_trusted_root_key_set_v01(
        capabilities=tuple(reversed(conformance.capabilities))
    )
    ordered_set = signer.build_trusted_root_key_set_v01(
        capabilities=conformance.capabilities
    )
    assert reversed_set == ordered_set


def test_key_set_rejects_list_input(conformance: ConformanceFixture) -> None:
    with pytest.raises(ValueError, match="trusted_key_set_invalid"):
        signer.build_trusted_root_key_set_v01(
            capabilities=list(conformance.capabilities)  # type: ignore[arg-type]
        )


def test_key_set_rejects_empty_tuple() -> None:
    with pytest.raises(ValueError, match="trusted_key_set_empty"):
        signer.build_trusted_root_key_set_v01(capabilities=())


def test_key_set_rejects_duplicate_root() -> None:
    first = signer.generate_root_signer_capability_v01(root_id="root:duplicate")
    second = signer.generate_root_signer_capability_v01(root_id="root:duplicate")
    with pytest.raises(ValueError, match="trusted_root_duplicate"):
        signer.build_trusted_root_key_set_v01(capabilities=(first, second))


def test_key_set_rejects_duplicate_key_id() -> None:
    first = signer.generate_root_signer_capability_v01(root_id="root:first")
    second = signer.generate_root_signer_capability_v01(root_id="root:second")
    object.__setattr__(second, "_key_id", first.key_id)
    with pytest.raises(ValueError, match="trusted_key_id_duplicate"):
        signer.build_trusted_root_key_set_v01(capabilities=(first, second))


def test_key_set_rejects_duplicate_public_key() -> None:
    first = signer.generate_root_signer_capability_v01(root_id="root:first")
    second = signer.generate_root_signer_capability_v01(root_id="root:second")
    object.__setattr__(second, "_public_key_hex", first.public_key_hex)
    with pytest.raises(ValueError, match="trusted_public_key_duplicate"):
        signer.build_trusted_root_key_set_v01(capabilities=(first, second))


@pytest.mark.parametrize("malformed", (object(), None, "capability"))
def test_key_set_rejects_malformed_capability(malformed: object) -> None:
    with pytest.raises(ValueError, match="signer_capability_invalid"):
        signer.build_trusted_root_key_set_v01(
            capabilities=(malformed,)  # type: ignore[arg-type]
        )


def test_key_set_retains_no_private_object() -> None:
    assert {field.name for field in fields(signer.TrustedRootKeySetV01)} == {
        "key_set_version",
        "key_set_id",
        "algorithm",
        "root_ids",
        "key_ids",
        "public_key_hexes",
    }


def test_key_set_projection_is_json_safe(conformance: ConformanceFixture) -> None:
    projected = signer.trusted_root_key_set_to_plain_dict_v01(conformance.key_set)
    json.dumps(projected, sort_keys=True, allow_nan=False)
    assert _contains_tuple_or_bytes(projected) is False


def test_valid_commitment(conformance: ConformanceFixture) -> None:
    commitment = _commitment(conformance.capabilities[0])
    assert commitment.commitment_version == signer.COMMITMENT_VERSION
    assert commitment.owner_root_id == conformance.capabilities[0].root_id


@pytest.mark.parametrize(
    "field",
    ("commitment_id", "transaction_id", "owner_root_id", "commitment_scope"),
)
@pytest.mark.parametrize("value", ("", None, True, "\ud800"))
def test_commitment_text_field_validation(field: str, value: object) -> None:
    capability = signer.generate_root_signer_capability_v01(root_id="root:text")
    with pytest.raises(ValueError):
        _commitment(capability, **{field: value})


@pytest.mark.parametrize("field", ("artifact_hash", "manifest_hash", "key_id"))
@pytest.mark.parametrize("value", ("bad", "0" * 63, "G" * 64, True, None))
def test_commitment_hash_field_validation(field: str, value: object) -> None:
    capability = signer.generate_root_signer_capability_v01(root_id="root:hash")
    with pytest.raises(ValueError):
        _commitment(capability, **{field: value})


def test_commitment_projection_is_independent(conformance: ConformanceFixture) -> None:
    commitment = conformance.commitments[0]
    first = signer.root_owned_commitment_to_plain_dict_v01(commitment)
    second = signer.root_owned_commitment_to_plain_dict_v01(commitment)
    first.clear()
    assert second == signer.root_owned_commitment_to_plain_dict_v01(commitment)


@pytest.mark.parametrize("index", (0, 1, 2))
def test_each_root_signs_and_verifies_its_own_commitment(
    conformance: ConformanceFixture, index: int
) -> None:
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[index],
        signature=conformance.signatures[index],
    )
    assert result.verification_status == signer.STATUS_PASS
    assert result.signature_verified is True
    assert result.root_isolation_verified is True


@pytest.mark.parametrize("index", (0, 1, 2))
def test_own_signature_shape_and_metadata(
    conformance: ConformanceFixture, index: int
) -> None:
    signature = conformance.signatures[index]
    commitment = conformance.commitments[index]
    assert re.fullmatch(r"[0-9a-f]{128}", signature.signature_hex)
    assert signature.algorithm == signer.ALGORITHM
    assert signature.commitment_id == commitment.commitment_id
    assert signature.transaction_id == commitment.transaction_id
    assert signature.owner_root_id == commitment.owner_root_id
    assert signature.key_id == commitment.key_id


@pytest.mark.parametrize("index", (0, 1, 2))
def test_signing_is_deterministic_for_same_key_and_commitment(
    conformance: ConformanceFixture, index: int
) -> None:
    repeated = signer.sign_root_owned_commitment_v01(
        capability=conformance.capabilities[index],
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[index],
    )
    assert repeated == conformance.signatures[index]


def test_signature_contract_has_no_authority_permission_or_effect_fields() -> None:
    names = {field.name for field in fields(signer.RootSignatureV01)}
    assert not names & {"authority", "permission", "effect", "final_output"}


@pytest.mark.parametrize(
    ("signer_index", "commitment_index"),
    ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)),
)
def test_complete_cross_root_signing_matrix_is_blocked(
    conformance: ConformanceFixture,
    signer_index: int,
    commitment_index: int,
) -> None:
    with pytest.raises(ValueError) as captured:
        signer.sign_root_owned_commitment_v01(
            capability=conformance.capabilities[signer_index],
            trusted_key_set=conformance.key_set,
            commitment=conformance.commitments[commitment_index],
        )
    assert captured.value.args == ("signer_root_mismatch",)
    assert captured.value.__cause__ is None
    assert "hostile" not in str(captured.value)


@pytest.mark.parametrize(
    ("signature_index", "commitment_index"),
    ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)),
)
def test_complete_cross_root_verification_matrix_is_blocked(
    conformance: ConformanceFixture,
    signature_index: int,
    commitment_index: int,
) -> None:
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[commitment_index],
        signature=conformance.signatures[signature_index],
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED
    assert result.root_isolation_verified is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("commitment_version", "v9"),
        ("commitment_id", "commitment:changed"),
        ("transaction_id", "txn:changed"),
        ("owner_root_id", "root:mock_airline_al"),
        ("commitment_scope", "scope:changed"),
        ("artifact_hash", "3" * 64),
        ("manifest_hash", "4" * 64),
        ("key_id", "5" * 64),
    ),
)
def test_each_signed_commitment_field_mutation_fails_closed(
    conformance: ConformanceFixture, field: str, value: object
) -> None:
    changed = replace(conformance.commitments[0], **{field: value})
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=changed,
        signature=conformance.signatures[0],
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("signature_version", "v9"),
        ("algorithm", "other"),
        ("commitment_id", "commitment:changed"),
        ("transaction_id", "txn:changed"),
        ("owner_root_id", "root:mock_airline_al"),
        ("key_id", "5" * 64),
        ("commitment_hash", "6" * 64),
        ("signature_hex", "0" * 128),
    ),
)
def test_each_signature_field_mutation_fails_closed(
    conformance: ConformanceFixture, field: str, value: object
) -> None:
    changed = replace(conformance.signatures[0], **{field: value})
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=changed,
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize(
    "signature_hex",
    ("0", "g" * 128, "0" * 126, "0" * 130, "0" * 128, "1" * 128),
    ids=("odd", "non_hex", "short", "long", "zero", "different"),
)
def test_malformed_or_invalid_signature_bytes_fail_closed(
    conformance: ConformanceFixture, signature_hex: str
) -> None:
    changed = replace(conformance.signatures[0], signature_hex=signature_hex)
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=changed,
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


def test_wrong_trusted_public_key_fails_closed(conformance: ConformanceFixture) -> None:
    public_keys = list(conformance.key_set.public_key_hexes)
    public_keys[0] = "0" * 64
    changed = replace(conformance.key_set, public_key_hexes=tuple(public_keys))
    result = signer.verify_root_signature_v01(
        trusted_key_set=changed,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize(
    ("key_set", "commitment", "signature_value"),
    (
        (object(), "commitment", "signature"),
        ("key_set", object(), "signature"),
        ("key_set", "commitment", object()),
    ),
)
def test_verifier_rejects_wrong_top_level_objects(
    conformance: ConformanceFixture,
    key_set: object,
    commitment: object,
    signature_value: object,
) -> None:
    result = signer.verify_root_signature_v01(
        trusted_key_set=(conformance.key_set if key_set == "key_set" else key_set),
        commitment=(
            conformance.commitments[0]
            if commitment == "commitment"
            else commitment
        ),
        signature=(
            conformance.signatures[0]
            if signature_value == "signature"
            else signature_value
        ),
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("root_ids", []),
        ("key_ids", (HostileEquality(),)),
        ("public_key_hexes", HostileIterator()),
    ),
)
def test_malformed_key_set_nested_values_fail_closed(
    conformance: ConformanceFixture, field: str, value: object
) -> None:
    changed = replace(conformance.key_set, **{field: value})
    result = signer.verify_root_signature_v01(
        trusted_key_set=changed,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED
    assert "hostile caller content" not in repr(result.verification_errors)


@pytest.mark.parametrize("error_type", (OSError, CustomHostileError))
def test_verifier_sanitizes_unexpected_ordinary_exceptions(
    conformance: ConformanceFixture,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
) -> None:
    def fail(**kwargs: object) -> signer.RootSignatureVerificationResultV01:
        raise error_type("hostile caller content")

    monkeypatch.setattr(signer, "_verify_root_signature_impl", fail)
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    assert result.verification_errors == ("root_isolation_failed",)
    assert "hostile caller content" not in repr(result.verification_errors)


@pytest.mark.parametrize("error_type", (KeyboardInterrupt, SystemExit, GeneratorExit))
def test_verifier_does_not_swallow_base_exceptions(
    conformance: ConformanceFixture,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[BaseException],
) -> None:
    def fail(**kwargs: object) -> signer.RootSignatureVerificationResultV01:
        raise error_type()

    monkeypatch.setattr(signer, "_verify_root_signature_impl", fail)
    with pytest.raises(error_type):
        signer.verify_root_signature_v01(
            trusted_key_set=conformance.key_set,
            commitment=conformance.commitments[0],
            signature=conformance.signatures[0],
        )


@pytest.mark.parametrize("index", (0, 1, 2))
def test_unknown_owner_root_fails_closed(
    conformance: ConformanceFixture, index: int
) -> None:
    changed = replace(
        conformance.commitments[index], owner_root_id="root:unknown"
    )
    result = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=changed,
        signature=conformance.signatures[index],
    )
    assert result.verification_status == signer.STATUS_BLOCKED_FAIL_CLOSED


@pytest.mark.parametrize("projection", ("key_set", "commitment", "signature", "result"))
def test_every_valid_projection_is_json_safe_and_independent(
    conformance: ConformanceFixture, projection: str
) -> None:
    verification = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    values: dict[str, tuple[object, Callable[[Any], dict[str, object]]]] = {
        "key_set": (
            conformance.key_set,
            signer.trusted_root_key_set_to_plain_dict_v01,
        ),
        "commitment": (
            conformance.commitments[0],
            signer.root_owned_commitment_to_plain_dict_v01,
        ),
        "signature": (
            conformance.signatures[0],
            signer.root_signature_to_plain_dict_v01,
        ),
        "result": (
            verification,
            signer.root_signature_verification_result_to_plain_dict_v01,
        ),
    }
    source, function = values[projection]
    first = function(source)
    second = function(source)
    assert first == second and first is not second
    assert _contains_tuple_or_bytes(first) is False
    json.dumps(first, sort_keys=True, allow_nan=False)
    first.clear()
    assert function(source) == second


@pytest.mark.parametrize(
    ("function", "value", "reason"),
    (
        (
            signer.trusted_root_key_set_to_plain_dict_v01,
            object(),
            "trusted_key_set_invalid",
        ),
        (
            signer.root_owned_commitment_to_plain_dict_v01,
            object(),
            "commitment_contract_invalid",
        ),
        (
            signer.root_signature_to_plain_dict_v01,
            object(),
            "root_signature_invalid",
        ),
        (
            signer.root_signature_verification_result_to_plain_dict_v01,
            object(),
            "root_signature_verification_result_invalid",
        ),
    ),
)
def test_malformed_projection_has_stable_sanitized_reason(
    function: Callable[[Any], dict[str, object]],
    value: object,
    reason: str,
) -> None:
    with pytest.raises(ValueError) as captured:
        function(value)
    assert captured.value.args == (reason,)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize(
    "case",
    (
        "wrong_version",
        "malformed_set_id",
        "wrong_algorithm",
        "list_root_ids",
        "empty_root_ids",
        "unequal_lengths",
        "duplicate_root",
        "duplicate_key_id",
        "duplicate_public_key",
        "malformed_root",
        "malformed_key_id",
        "malformed_public_key",
        "unsorted_roots",
        "mismatched_derived_key_id",
        "mismatched_key_set_id",
    ),
)
def test_semantically_invalid_key_set_projection_is_rejected(
    conformance: ConformanceFixture,
    case: str,
) -> None:
    key_set = conformance.key_set
    mutations: dict[str, dict[str, object]] = {
        "wrong_version": {"key_set_version": "v9"},
        "malformed_set_id": {"key_set_id": "bad"},
        "wrong_algorithm": {"algorithm": "other"},
        "list_root_ids": {"root_ids": list(key_set.root_ids)},
        "empty_root_ids": {"root_ids": ()},
        "unequal_lengths": {"key_ids": key_set.key_ids[:-1]},
        "duplicate_root": {
            "root_ids": (key_set.root_ids[0], key_set.root_ids[0], key_set.root_ids[2])
        },
        "duplicate_key_id": {
            "key_ids": (key_set.key_ids[0], key_set.key_ids[0], key_set.key_ids[2])
        },
        "duplicate_public_key": {
            "public_key_hexes": (
                key_set.public_key_hexes[0],
                key_set.public_key_hexes[0],
                key_set.public_key_hexes[2],
            )
        },
        "malformed_root": {
            "root_ids": ("", key_set.root_ids[1], key_set.root_ids[2])
        },
        "malformed_key_id": {
            "key_ids": ("bad", key_set.key_ids[1], key_set.key_ids[2])
        },
        "malformed_public_key": {
            "public_key_hexes": (
                "bad",
                key_set.public_key_hexes[1],
                key_set.public_key_hexes[2],
            )
        },
        "unsorted_roots": {"root_ids": tuple(reversed(key_set.root_ids))},
        "mismatched_derived_key_id": {
            "key_ids": (
                _different_sha256(key_set.key_ids[0]),
                key_set.key_ids[1],
                key_set.key_ids[2],
            )
        },
        "mismatched_key_set_id": {
            "key_set_id": _different_sha256(key_set.key_set_id)
        },
    }
    malformed = replace(key_set, **mutations[case])
    with pytest.raises(ValueError) as captured:
        signer.trusted_root_key_set_to_plain_dict_v01(malformed)
    assert captured.value.args == ("trusted_key_set_invalid",)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("commitment_version", "v9"),
        ("commitment_id", ""),
        ("transaction_id", ""),
        ("owner_root_id", ""),
        ("commitment_scope", ""),
        ("owner_root_id", "\ud800"),
        ("artifact_hash", "bad"),
        ("manifest_hash", "bad"),
        ("key_id", "bad"),
    ),
)
def test_semantically_invalid_commitment_projection_is_rejected(
    conformance: ConformanceFixture,
    field_name: str,
    invalid_value: object,
) -> None:
    malformed = replace(
        conformance.commitments[0], **{field_name: invalid_value}
    )
    with pytest.raises(ValueError) as captured:
        signer.root_owned_commitment_to_plain_dict_v01(malformed)
    assert captured.value.args == ("commitment_contract_invalid",)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("signature_version", "v9"),
        ("algorithm", "other"),
        ("commitment_id", ""),
        ("transaction_id", ""),
        ("owner_root_id", ""),
        ("owner_root_id", "\ud800"),
        ("key_id", "bad"),
        ("commitment_hash", "bad"),
        ("signature_hex", "0" * 126),
        ("signature_hex", "0" * 130),
        ("signature_hex", "0" * 127),
        ("signature_hex", "A" * 128),
        ("signature_hex", "z" * 128),
    ),
)
def test_semantically_invalid_signature_projection_is_rejected(
    conformance: ConformanceFixture,
    field_name: str,
    invalid_value: object,
) -> None:
    malformed = replace(conformance.signatures[0], **{field_name: invalid_value})
    with pytest.raises(ValueError) as captured:
        signer.root_signature_to_plain_dict_v01(malformed)
    assert captured.value.args == ("root_signature_invalid",)
    assert captured.value.__cause__ is None


@pytest.mark.parametrize(
    "case",
    (
        "unknown_status",
        "errors_string",
        "error_not_string",
        "duplicate_error",
        "unknown_error",
        "flag_not_bool",
        "pass_false_flag",
        "pass_with_error",
        "blocked_without_error",
        "blocked_signature_verified",
        "blocked_root_isolation_verified",
        "malformed_key_id",
        "malformed_commitment_hash",
        "mixed_empty_identity",
        "surrogate_owner",
    ),
)
def test_semantically_invalid_verification_result_projection_is_rejected(
    conformance: ConformanceFixture,
    case: str,
) -> None:
    valid = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    blocked = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[1],
        signature=conformance.signatures[0],
    )
    mutations: dict[str, signer.RootSignatureVerificationResultV01] = {
        "unknown_status": replace(valid, verification_status="garbage"),
        "errors_string": replace(valid, verification_errors="oops"),  # type: ignore[arg-type]
        "error_not_string": replace(valid, verification_errors=(1,)),  # type: ignore[arg-type]
        "duplicate_error": replace(
            blocked,
            verification_errors=("root_isolation_failed", "root_isolation_failed"),
        ),
        "unknown_error": replace(blocked, verification_errors=("unknown",)),
        "flag_not_bool": replace(valid, signature_verified="yes"),  # type: ignore[arg-type]
        "pass_false_flag": replace(valid, trusted_key_set_verified=False),
        "pass_with_error": replace(valid, verification_errors=("root_isolation_failed",)),
        "blocked_without_error": replace(blocked, verification_errors=()),
        "blocked_signature_verified": replace(blocked, signature_verified=True),
        "blocked_root_isolation_verified": replace(
            blocked, root_isolation_verified=True
        ),
        "malformed_key_id": replace(blocked, key_id="bad"),
        "malformed_commitment_hash": replace(blocked, commitment_hash="bad"),
        "mixed_empty_identity": replace(blocked, key_id=""),
        "surrogate_owner": replace(blocked, owner_root_id="\ud800"),
    }
    with pytest.raises(ValueError) as captured:
        signer.root_signature_verification_result_to_plain_dict_v01(
            mutations[case]
        )
    assert captured.value.args == (
        "root_signature_verification_result_invalid",
    )
    assert captured.value.__cause__ is None


def test_valid_projection_field_surfaces_remain_exact(
    conformance: ConformanceFixture,
) -> None:
    verified = signer.verify_root_signature_v01(
        trusted_key_set=conformance.key_set,
        commitment=conformance.commitments[0],
        signature=conformance.signatures[0],
    )
    assert set(signer.trusted_root_key_set_to_plain_dict_v01(conformance.key_set)) == {
        field.name for field in fields(signer.TrustedRootKeySetV01)
    }
    assert set(
        signer.root_owned_commitment_to_plain_dict_v01(conformance.commitments[0])
    ) == {field.name for field in fields(signer.RootOwnedCommitmentV01)}
    assert set(signer.root_signature_to_plain_dict_v01(conformance.signatures[0])) == {
        field.name for field in fields(signer.RootSignatureV01)
    }
    assert set(signer.root_signature_verification_result_to_plain_dict_v01(verified)) == {
        field.name for field in fields(signer.RootSignatureVerificationResultV01)
    }


def test_static_import_boundary() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(name.startswith(("hedgehog.domains", "demo", "tests")) for name in imports)
    assert not imports & {
        "os",
        "pathlib",
        "tempfile",
        "shutil",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "config",
    }


@pytest.mark.parametrize(
    "token",
    (
        "private_bytes",
        "BEGIN PRIVATE KEY",
        "BEGIN PUBLIC KEY",
        "open(",
        ".read_text(",
        ".read_bytes(",
        ".write_text(",
        ".write_bytes(",
        ".tmp",
        "root:client_os_001",
        "root:mock_airline_al",
        "root:mock_bank_a",
        "Supplier",
        "FinalOutput",
    ),
)
def test_static_forbidden_source_tokens(token: str) -> None:
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_no_module_global_mutable_registry() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assert not isinstance(node.value, (ast.Dict, ast.List, ast.Set))


@pytest.mark.parametrize(
    "function",
    (signer.sign_root_owned_commitment_v01, signer.verify_root_signature_v01),
)
def test_sign_and_verify_accept_no_callback_or_effect_hook(
    function: Callable[..., object],
) -> None:
    parameters = set(inspect.signature(function).parameters)
    assert not parameters & {"callback", "hook", "effect", "provider", "network"}
