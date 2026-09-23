"""Pure in-memory Root signer-isolation conformance for the neutral kernel.

This conformance-only, domain-neutral kernel primitive uses ephemeral test-only
signer capabilities. It performs no file I/O, key persistence, provider or
network access, domain imports, authority or permission creation, or effects.
A signature proves possession of one test key for one bound commitment only;
it does not prove truth, create Root authority, provide production identity,
implement Airline Root Attestation, or implement PKI.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
import re as _re

from cryptography.exceptions import InvalidSignature as _InvalidSignature
from cryptography.hazmat.primitives import serialization as _serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey as _Ed25519PrivateKey,
    Ed25519PublicKey as _Ed25519PublicKey,
)

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "kernel_root_signer_isolation_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1a2"
ROOT_SIGNER_VERSION = "v0.1"
KEY_SET_VERSION = "v0.1"
COMMITMENT_VERSION = "v0.1"
SIGNATURE_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

ALGORITHM = "Ed25519"
PUBLIC_KEY_ENCODING = "raw_lowercase_hex"
SIGNATURE_ENCODING = "lowercase_hex"

KEY_ID_DOMAIN = "hedgehog.kernel.root_key_id.v01"
KEY_SET_DOMAIN = "hedgehog.kernel.trusted_root_key_set.v01"
COMMITMENT_DOMAIN = "hedgehog.kernel.root_commitment.v01"

_SHA256_HEX = _re.compile(r"^[0-9a-f]{64}$")
_SIGNATURE_HEX = _re.compile(r"^[0-9a-f]{128}$")
_CAPABILITY_FACTORY_TOKEN = object()
_SIGNING_ERROR_REASONS = (
    "signer_capability_invalid",
    "trusted_key_set_invalid",
    "commitment_contract_invalid",
    "signer_root_mismatch",
    "signer_key_mismatch",
    "signer_not_trusted",
    "signer_public_key_mismatch",
    "signature_generation_failed",
)
_VERIFICATION_ERROR_REASONS = (
    "trusted_key_set_invalid",
    "commitment_contract_invalid",
    "signature_contract_invalid",
    "trusted_root_missing",
    "signature_owner_root_mismatch",
    "signature_key_id_mismatch",
    "trusted_key_id_mismatch",
    "trusted_public_key_invalid",
    "commitment_hash_mismatch",
    "signature_verification_failed",
    "root_isolation_failed",
)


class RootSignerCapabilityV01:
    """Opaque process-local holder for one ephemeral test signing key."""

    __slots__ = (
        "_algorithm",
        "_key_id",
        "_private_key",
        "_public_key_hex",
        "_root_id",
    )

    def __new__(cls, *args: object, **kwargs: object) -> RootSignerCapabilityV01:
        if not args or args[0] is not _CAPABILITY_FACTORY_TOKEN:
            raise TypeError("root_signer_capability_direct_construction_forbidden")
        return super().__new__(cls)

    def __init__(
        self,
        factory_token: object,
        *,
        root_id: str,
        key_id: str,
        public_key_hex: str,
        private_key: _Ed25519PrivateKey,
    ) -> None:
        if factory_token is not _CAPABILITY_FACTORY_TOKEN:
            raise TypeError("root_signer_capability_direct_construction_forbidden")
        object.__setattr__(self, "_root_id", root_id)
        object.__setattr__(self, "_key_id", key_id)
        object.__setattr__(self, "_algorithm", ALGORITHM)
        object.__setattr__(self, "_public_key_hex", public_key_hex)
        object.__setattr__(self, "_private_key", private_key)

    @property
    def root_id(self) -> str:
        return self._root_id

    @property
    def key_id(self) -> str:
        return self._key_id

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @property
    def public_key_hex(self) -> str:
        return self._public_key_hex

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("root_signer_capability_immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("root_signer_capability_immutable")

    def __repr__(self) -> str:
        return (
            "RootSignerCapabilityV01("
            f"root_id={self._root_id!r}, "
            f"key_id={self._key_id!r}, "
            f"algorithm={self._algorithm!r}, "
            f"public_key_hex={self._public_key_hex!r})"
        )

    def __copy__(self) -> RootSignerCapabilityV01:
        return self

    def __deepcopy__(self, memo: dict[int, object]) -> RootSignerCapabilityV01:
        return self

    def __reduce__(self) -> object:
        raise TypeError("root_signer_capability_not_serializable")

    def __reduce_ex__(self, protocol: int) -> object:
        raise TypeError("root_signer_capability_not_serializable")

    def __getstate__(self) -> object:
        raise TypeError("root_signer_capability_not_serializable")


@_dataclass(frozen=True)
class TrustedRootKeySetV01:
    key_set_version: str
    key_set_id: str
    algorithm: str
    root_ids: tuple[str, ...]
    key_ids: tuple[str, ...]
    public_key_hexes: tuple[str, ...]


@_dataclass(frozen=True)
class RootOwnedCommitmentV01:
    commitment_version: str
    commitment_id: str
    transaction_id: str
    owner_root_id: str
    commitment_scope: str
    artifact_hash: str
    manifest_hash: str
    key_id: str


@_dataclass(frozen=True)
class RootSignatureV01:
    signature_version: str
    algorithm: str
    commitment_id: str
    transaction_id: str
    owner_root_id: str
    key_id: str
    commitment_hash: str
    signature_hex: str


@_dataclass(frozen=True)
class RootSignatureVerificationResultV01:
    verification_status: str
    verification_errors: tuple[str, ...]
    trusted_key_set_verified: bool
    commitment_verified: bool
    signature_contract_verified: bool
    trusted_root_present: bool
    key_id_verified: bool
    public_key_verified: bool
    commitment_hash_verified: bool
    signature_verified: bool
    root_isolation_verified: bool
    owner_root_id: str
    key_id: str
    commitment_hash: str


def generate_root_signer_capability_v01(
    *,
    root_id: str,
) -> RootSignerCapabilityV01:
    if not _valid_nonempty_string(root_id):
        raise ValueError("signer_root_id_invalid")
    try:
        private_key = _Ed25519PrivateKey.generate()
        public_key_hex = _raw_public_key_hex(private_key)
        key_id = _derive_key_id(root_id=root_id, public_key_hex=public_key_hex)
        return RootSignerCapabilityV01(
            _CAPABILITY_FACTORY_TOKEN,
            root_id=root_id,
            key_id=key_id,
            public_key_hex=public_key_hex,
            private_key=private_key,
        )
    except Exception:
        raise ValueError("signer_capability_invalid") from None


def build_trusted_root_key_set_v01(
    *,
    capabilities: tuple[RootSignerCapabilityV01, ...],
) -> TrustedRootKeySetV01:
    try:
        if type(capabilities) is not tuple:
            raise ValueError("trusted_key_set_invalid")
        if not capabilities:
            raise ValueError("trusted_key_set_empty")
        if any(type(item) is not RootSignerCapabilityV01 for item in capabilities):
            raise ValueError("signer_capability_invalid")
        rows = tuple(
            (item.root_id, item.key_id, item.public_key_hex)
            for item in capabilities
        )
        if any(not _valid_nonempty_string(row[0]) for row in rows):
            raise ValueError("signer_root_id_invalid")
        if _has_duplicate(tuple(row[0] for row in rows)):
            raise ValueError("trusted_root_duplicate")
        if _has_duplicate(tuple(row[1] for row in rows)):
            raise ValueError("trusted_key_id_duplicate")
        if _has_duplicate(tuple(row[2] for row in rows)):
            raise ValueError("trusted_public_key_duplicate")
        for capability in capabilities:
            _require_capability_coherent(capability)
        ordered = tuple(sorted(rows, key=lambda row: row[0]))
        key_set_id = _derive_key_set_id(ordered)
        return TrustedRootKeySetV01(
            key_set_version=KEY_SET_VERSION,
            key_set_id=key_set_id,
            algorithm=ALGORITHM,
            root_ids=tuple(row[0] for row in ordered),
            key_ids=tuple(row[1] for row in ordered),
            public_key_hexes=tuple(row[2] for row in ordered),
        )
    except ValueError as exc:
        if _known_reason(exc, (
            "signer_capability_invalid",
            "signer_root_id_invalid",
            "trusted_key_set_empty",
            "trusted_key_set_invalid",
            "trusted_root_duplicate",
            "trusted_key_id_duplicate",
            "trusted_public_key_duplicate",
        )):
            raise ValueError(exc.args[0]) from None
        raise ValueError("trusted_key_set_invalid") from None
    except Exception:
        raise ValueError("trusted_key_set_invalid") from None


def build_root_owned_commitment_v01(
    *,
    commitment_id: str,
    transaction_id: str,
    owner_root_id: str,
    commitment_scope: str,
    artifact_hash: str,
    manifest_hash: str,
    key_id: str,
) -> RootOwnedCommitmentV01:
    commitment = RootOwnedCommitmentV01(
        commitment_version=COMMITMENT_VERSION,
        commitment_id=commitment_id,
        transaction_id=transaction_id,
        owner_root_id=owner_root_id,
        commitment_scope=commitment_scope,
        artifact_hash=artifact_hash,
        manifest_hash=manifest_hash,
        key_id=key_id,
    )
    reason = _commitment_invalid_reason(commitment)
    if reason is not None:
        raise ValueError(reason)
    return commitment


def sign_root_owned_commitment_v01(
    *,
    capability: RootSignerCapabilityV01,
    trusted_key_set: TrustedRootKeySetV01,
    commitment: RootOwnedCommitmentV01,
) -> RootSignatureV01:
    try:
        _require_capability_coherent(capability)
        if not _trusted_key_set_valid(trusted_key_set):
            raise ValueError("trusted_key_set_invalid")
        if _commitment_invalid_reason(commitment) is not None:
            raise ValueError("commitment_contract_invalid")
        if capability.root_id != commitment.owner_root_id:
            raise ValueError("signer_root_mismatch")
        if capability.key_id != commitment.key_id:
            raise ValueError("signer_key_mismatch")
        if commitment.owner_root_id not in trusted_key_set.root_ids:
            raise ValueError("signer_not_trusted")
        index = trusted_key_set.root_ids.index(commitment.owner_root_id)
        if trusted_key_set.key_ids[index] != capability.key_id:
            raise ValueError("signer_not_trusted")
        if trusted_key_set.public_key_hexes[index] != capability.public_key_hex:
            raise ValueError("signer_public_key_mismatch")
        commitment_hash = _derive_commitment_hash(commitment)
        signature = capability._private_key.sign(bytes.fromhex(commitment_hash))
        signature_hex = signature.hex()
        if not _valid_signature_hex(signature_hex):
            raise ValueError("signature_generation_failed")
        return RootSignatureV01(
            signature_version=SIGNATURE_VERSION,
            algorithm=ALGORITHM,
            commitment_id=commitment.commitment_id,
            transaction_id=commitment.transaction_id,
            owner_root_id=commitment.owner_root_id,
            key_id=commitment.key_id,
            commitment_hash=commitment_hash,
            signature_hex=signature_hex,
        )
    except ValueError as exc:
        if _known_reason(exc, _SIGNING_ERROR_REASONS):
            raise ValueError(exc.args[0]) from None
        raise ValueError("signature_generation_failed") from None
    except Exception:
        raise ValueError("signature_generation_failed") from None


def verify_root_signature_v01(
    *,
    trusted_key_set: object,
    commitment: object,
    signature: object,
) -> RootSignatureVerificationResultV01:
    try:
        return _verify_root_signature_impl(
            trusted_key_set=trusted_key_set,
            commitment=commitment,
            signature=signature,
        )
    except Exception:
        return _verification_failure(("root_isolation_failed",))


def trusted_root_key_set_to_plain_dict_v01(
    key_set: TrustedRootKeySetV01,
) -> dict[str, object]:
    try:
        if not _trusted_key_set_valid(key_set):
            raise ValueError("trusted_key_set_invalid")
        projected: dict[str, object] = {
            "key_set_version": key_set.key_set_version,
            "key_set_id": key_set.key_set_id,
            "algorithm": key_set.algorithm,
            "root_ids": list(key_set.root_ids),
            "key_ids": list(key_set.key_ids),
            "public_key_hexes": list(key_set.public_key_hexes),
        }
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("trusted_key_set_invalid") from None


def root_owned_commitment_to_plain_dict_v01(
    commitment: RootOwnedCommitmentV01,
) -> dict[str, object]:
    try:
        if _commitment_invalid_reason(commitment) is not None:
            raise ValueError("commitment_contract_invalid")
        projected = _commitment_plain(commitment)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("commitment_contract_invalid") from None


def root_signature_to_plain_dict_v01(
    signature: RootSignatureV01,
) -> dict[str, object]:
    try:
        if not _signature_contract_valid(signature):
            raise ValueError("root_signature_invalid")
        projected: dict[str, object] = {
            "signature_version": signature.signature_version,
            "algorithm": signature.algorithm,
            "commitment_id": signature.commitment_id,
            "transaction_id": signature.transaction_id,
            "owner_root_id": signature.owner_root_id,
            "key_id": signature.key_id,
            "commitment_hash": signature.commitment_hash,
            "signature_hex": signature.signature_hex,
        }
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("root_signature_invalid") from None


def root_signature_verification_result_to_plain_dict_v01(
    result: RootSignatureVerificationResultV01,
) -> dict[str, object]:
    try:
        if not _verification_result_valid(result):
            raise ValueError("root_signature_verification_result_invalid")
        projected: dict[str, object] = {
            "verification_status": result.verification_status,
            "verification_errors": list(result.verification_errors),
            "trusted_key_set_verified": result.trusted_key_set_verified,
            "commitment_verified": result.commitment_verified,
            "signature_contract_verified": result.signature_contract_verified,
            "trusted_root_present": result.trusted_root_present,
            "key_id_verified": result.key_id_verified,
            "public_key_verified": result.public_key_verified,
            "commitment_hash_verified": result.commitment_hash_verified,
            "signature_verified": result.signature_verified,
            "root_isolation_verified": result.root_isolation_verified,
            "owner_root_id": result.owner_root_id,
            "key_id": result.key_id,
            "commitment_hash": result.commitment_hash,
        }
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("root_signature_verification_result_invalid") from None


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _valid_nonempty_string(value: object) -> bool:
    return type(value) is str and bool(value) and not _contains_surrogate(value)


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _SHA256_HEX.fullmatch(value) is not None


def _valid_public_key_hex(value: object) -> bool:
    return _valid_sha256(value)


def _valid_signature_hex(value: object) -> bool:
    return type(value) is str and _SIGNATURE_HEX.fullmatch(value) is not None


def _known_reason(error: ValueError, allowed: tuple[str, ...]) -> bool:
    return bool(
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    )


def _has_duplicate(values: tuple[str, ...]) -> bool:
    return len(values) != len(set(values))


def _raw_public_key_hex(private_key: _Ed25519PrivateKey) -> str:
    return private_key.public_key().public_bytes(
        encoding=_serialization.Encoding.Raw,
        format=_serialization.PublicFormat.Raw,
    ).hex()


def _key_id_material(*, root_id: str, public_key_hex: str) -> dict[str, str]:
    return {
        "algorithm": ALGORITHM,
        "root_id": root_id,
        "public_key_hex": public_key_hex,
    }


def _derive_key_id(*, root_id: str, public_key_hex: str) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=KEY_ID_DOMAIN,
        payload=_canonical_json_bytes_v01(
            _key_id_material(root_id=root_id, public_key_hex=public_key_hex)
        ),
    )


def _key_set_material(
    rows: tuple[tuple[str, str, str], ...],
) -> dict[str, object]:
    return {
        "key_set_version": KEY_SET_VERSION,
        "algorithm": ALGORITHM,
        "bindings": [
            {
                "root_id": root_id,
                "key_id": key_id,
                "public_key_hex": public_key_hex,
            }
            for root_id, key_id, public_key_hex in rows
        ],
    }


def _derive_key_set_id(rows: tuple[tuple[str, str, str], ...]) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=KEY_SET_DOMAIN,
        payload=_canonical_json_bytes_v01(_key_set_material(rows)),
    )


def _require_capability_coherent(capability: object) -> None:
    if type(capability) is not RootSignerCapabilityV01:
        raise ValueError("signer_capability_invalid")
    if not _valid_nonempty_string(capability.root_id):
        raise ValueError("signer_capability_invalid")
    if capability.algorithm != ALGORITHM:
        raise ValueError("signer_capability_invalid")
    if not _valid_public_key_hex(capability.public_key_hex):
        raise ValueError("signer_capability_invalid")
    if not _valid_sha256(capability.key_id):
        raise ValueError("signer_capability_invalid")
    if not isinstance(capability._private_key, _Ed25519PrivateKey):
        raise ValueError("signer_capability_invalid")
    try:
        recomputed_public = _raw_public_key_hex(capability._private_key)
        recomputed_key_id = _derive_key_id(
            root_id=capability.root_id,
            public_key_hex=recomputed_public,
        )
    except Exception:
        raise ValueError("signer_capability_invalid") from None
    if recomputed_public != capability.public_key_hex:
        raise ValueError("signer_capability_invalid")
    if recomputed_key_id != capability.key_id:
        raise ValueError("signer_capability_invalid")


def _trusted_key_set_valid(key_set: object) -> bool:
    if type(key_set) is not TrustedRootKeySetV01:
        return False
    if (
        type(key_set.key_set_version) is not str
        or key_set.key_set_version != KEY_SET_VERSION
        or type(key_set.key_set_id) is not str
        or not _valid_sha256(key_set.key_set_id)
        or type(key_set.algorithm) is not str
        or key_set.algorithm != ALGORITHM
    ):
        return False
    tuples = (key_set.root_ids, key_set.key_ids, key_set.public_key_hexes)
    if any(type(value) is not tuple or not value for value in tuples):
        return False
    if len({len(value) for value in tuples}) != 1:
        return False
    if any(not _valid_nonempty_string(value) for value in key_set.root_ids):
        return False
    if any(not _valid_sha256(value) for value in key_set.key_ids):
        return False
    if any(not _valid_public_key_hex(value) for value in key_set.public_key_hexes):
        return False
    if tuple(sorted(key_set.root_ids)) != key_set.root_ids:
        return False
    if any(_has_duplicate(value) for value in tuples):
        return False
    rows = tuple(zip(key_set.root_ids, key_set.key_ids, key_set.public_key_hexes))
    if any(
        _derive_key_id(root_id=root_id, public_key_hex=public_key_hex) != key_id
        for root_id, key_id, public_key_hex in rows
    ):
        return False
    return _derive_key_set_id(rows) == key_set.key_set_id


def _commitment_invalid_reason(commitment: object) -> str | None:
    if type(commitment) is not RootOwnedCommitmentV01:
        return "commitment_contract_invalid"
    if (
        type(commitment.commitment_version) is not str
        or commitment.commitment_version != COMMITMENT_VERSION
    ):
        return "commitment_contract_invalid"
    checks = (
        (commitment.commitment_id, "commitment_id_invalid"),
        (commitment.transaction_id, "transaction_id_invalid"),
        (commitment.owner_root_id, "owner_root_id_invalid"),
        (commitment.commitment_scope, "commitment_scope_invalid"),
    )
    for value, reason in checks:
        if not _valid_nonempty_string(value):
            return reason
    if not _valid_sha256(commitment.artifact_hash):
        return "artifact_hash_invalid"
    if not _valid_sha256(commitment.manifest_hash):
        return "manifest_hash_invalid"
    if not _valid_sha256(commitment.key_id):
        return "commitment_key_id_invalid"
    return None


def _commitment_plain(commitment: RootOwnedCommitmentV01) -> dict[str, object]:
    return {
        "commitment_version": commitment.commitment_version,
        "commitment_id": commitment.commitment_id,
        "transaction_id": commitment.transaction_id,
        "owner_root_id": commitment.owner_root_id,
        "commitment_scope": commitment.commitment_scope,
        "artifact_hash": commitment.artifact_hash,
        "manifest_hash": commitment.manifest_hash,
        "key_id": commitment.key_id,
    }


def _derive_commitment_hash(commitment: RootOwnedCommitmentV01) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=COMMITMENT_DOMAIN,
        payload=_canonical_json_bytes_v01(_commitment_plain(commitment)),
    )


def _signature_contract_valid(signature: object) -> bool:
    if type(signature) is not RootSignatureV01:
        return False
    if (
        type(signature.signature_version) is not str
        or signature.signature_version != SIGNATURE_VERSION
        or type(signature.algorithm) is not str
        or signature.algorithm != ALGORITHM
    ):
        return False
    for value in (
        signature.commitment_id,
        signature.transaction_id,
        signature.owner_root_id,
    ):
        if not _valid_nonempty_string(value):
            return False
    return bool(
        _valid_sha256(signature.key_id)
        and _valid_sha256(signature.commitment_hash)
        and _valid_signature_hex(signature.signature_hex)
    )


def _verification_result_valid(result: object) -> bool:
    if type(result) is not RootSignatureVerificationResultV01:
        return False
    if result.verification_status not in {
        STATUS_PASS,
        STATUS_BLOCKED_FAIL_CLOSED,
    }:
        return False
    errors = result.verification_errors
    if (
        type(errors) is not tuple
        or any(not _valid_nonempty_string(error) for error in errors)
        or len(errors) != len(set(errors))
        or any(error not in _VERIFICATION_ERROR_REASONS for error in errors)
    ):
        return False
    flags = (
        result.trusted_key_set_verified,
        result.commitment_verified,
        result.signature_contract_verified,
        result.trusted_root_present,
        result.key_id_verified,
        result.public_key_verified,
        result.commitment_hash_verified,
        result.signature_verified,
        result.root_isolation_verified,
    )
    if any(type(flag) is not bool for flag in flags):
        return False
    if type(result.owner_root_id) is not str or _contains_surrogate(
        result.owner_root_id
    ):
        return False
    if type(result.key_id) is not str or type(result.commitment_hash) is not str:
        return False
    if result.verification_status == STATUS_PASS:
        return bool(
            errors == ()
            and all(flags)
            and _valid_nonempty_string(result.owner_root_id)
            and _valid_sha256(result.key_id)
            and _valid_sha256(result.commitment_hash)
        )
    if (
        not errors
        or result.signature_verified
        or result.root_isolation_verified
    ):
        return False
    early_failure = (
        result.owner_root_id == ""
        and result.key_id == ""
        and result.commitment_hash == ""
    )
    post_contract_failure = bool(
        _valid_nonempty_string(result.owner_root_id)
        and _valid_sha256(result.key_id)
        and _valid_sha256(result.commitment_hash)
    )
    return early_failure or post_contract_failure


def _verify_root_signature_impl(
    *,
    trusted_key_set: object,
    commitment: object,
    signature: object,
) -> RootSignatureVerificationResultV01:
    key_set_valid = _trusted_key_set_valid(trusted_key_set)
    commitment_valid = _commitment_invalid_reason(commitment) is None
    signature_valid = _signature_contract_valid(signature)
    errors: list[str] = []
    if not key_set_valid:
        errors.append("trusted_key_set_invalid")
    if not commitment_valid:
        errors.append("commitment_contract_invalid")
    if not signature_valid:
        errors.append("signature_contract_invalid")
    if not (key_set_valid and commitment_valid and signature_valid):
        return _verification_failure(
            tuple(errors),
            trusted_key_set_verified=key_set_valid,
            commitment_verified=commitment_valid,
            signature_contract_verified=signature_valid,
        )

    key_set = trusted_key_set
    owned_commitment = commitment
    root_signature = signature
    trusted_root_present = owned_commitment.owner_root_id in key_set.root_ids
    if not trusted_root_present:
        errors.append("trusted_root_missing")

    signature_owner_matches = (
        root_signature.owner_root_id == owned_commitment.owner_root_id
    )
    if not signature_owner_matches:
        errors.append("signature_owner_root_mismatch")
    signature_key_matches = root_signature.key_id == owned_commitment.key_id
    if not signature_key_matches:
        errors.append("signature_key_id_mismatch")
    metadata_matches = bool(
        root_signature.commitment_id == owned_commitment.commitment_id
        and root_signature.transaction_id == owned_commitment.transaction_id
    )
    if not metadata_matches:
        errors.append("signature_contract_invalid")

    trusted_key_matches = False
    public_key_verified = False
    public_key: _Ed25519PublicKey | None = None
    if trusted_root_present:
        index = key_set.root_ids.index(owned_commitment.owner_root_id)
        trusted_key_id = key_set.key_ids[index]
        trusted_public_key_hex = key_set.public_key_hexes[index]
        trusted_key_matches = trusted_key_id == owned_commitment.key_id
        if not trusted_key_matches:
            errors.append("trusted_key_id_mismatch")
        try:
            derived_key_id = _derive_key_id(
                root_id=owned_commitment.owner_root_id,
                public_key_hex=trusted_public_key_hex,
            )
            public_key = _Ed25519PublicKey.from_public_bytes(
                bytes.fromhex(trusted_public_key_hex)
            )
            public_key_verified = derived_key_id == trusted_key_id
        except Exception:
            public_key_verified = False
        if not public_key_verified:
            errors.append("trusted_public_key_invalid")

    recomputed_commitment_hash = _derive_commitment_hash(owned_commitment)
    commitment_hash_verified = (
        root_signature.commitment_hash == recomputed_commitment_hash
    )
    if not commitment_hash_verified:
        errors.append("commitment_hash_mismatch")

    signature_verified = False
    if (
        public_key is not None
        and public_key_verified
        and signature_owner_matches
        and signature_key_matches
        and trusted_key_matches
        and metadata_matches
        and commitment_hash_verified
    ):
        try:
            public_key.verify(
                bytes.fromhex(root_signature.signature_hex),
                bytes.fromhex(recomputed_commitment_hash),
            )
            signature_verified = True
        except _InvalidSignature:
            errors.append("signature_verification_failed")
        except Exception:
            errors.append("signature_verification_failed")

    root_isolation_verified = bool(
        trusted_root_present
        and signature_owner_matches
        and signature_key_matches
        and trusted_key_matches
        and public_key_verified
        and metadata_matches
        and commitment_hash_verified
        and signature_verified
    )
    if not root_isolation_verified:
        errors.append("root_isolation_failed")
    unique_errors = tuple(dict.fromkeys(errors))
    return RootSignatureVerificationResultV01(
        verification_status=(
            STATUS_PASS if not unique_errors else STATUS_BLOCKED_FAIL_CLOSED
        ),
        verification_errors=unique_errors,
        trusted_key_set_verified=True,
        commitment_verified=True,
        signature_contract_verified=True,
        trusted_root_present=trusted_root_present,
        key_id_verified=bool(signature_key_matches and trusted_key_matches),
        public_key_verified=public_key_verified,
        commitment_hash_verified=commitment_hash_verified,
        signature_verified=signature_verified,
        root_isolation_verified=root_isolation_verified,
        owner_root_id=owned_commitment.owner_root_id,
        key_id=owned_commitment.key_id,
        commitment_hash=recomputed_commitment_hash,
    )


def _verification_failure(
    errors: tuple[str, ...],
    *,
    trusted_key_set_verified: bool = False,
    commitment_verified: bool = False,
    signature_contract_verified: bool = False,
) -> RootSignatureVerificationResultV01:
    return RootSignatureVerificationResultV01(
        verification_status=STATUS_BLOCKED_FAIL_CLOSED,
        verification_errors=tuple(dict.fromkeys(errors)),
        trusted_key_set_verified=trusted_key_set_verified,
        commitment_verified=commitment_verified,
        signature_contract_verified=signature_contract_verified,
        trusted_root_present=False,
        key_id_verified=False,
        public_key_verified=False,
        commitment_hash_verified=False,
        signature_verified=False,
        root_isolation_verified=False,
        owner_root_id="",
        key_id="",
        commitment_hash="",
    )
