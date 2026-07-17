"""Pure in-memory, domain-neutral, deterministic integrity and Replay core.

The module performs no provider or network access, no file I/O, and no domain
imports. It proves declared integrity and continuity only: not truth,
authority, permission, or execution. Replay reconstructs accepted evidence and
does not rerun semantics, transactions, corridors, collectors, or effects.
"""

from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass, is_dataclass as _is_dataclass
import hashlib as _hashlib
import json as _json
import math as _math
import re as _re


MODULE_ID = "kernel_integrity_replay_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1a1"
INTEGRITY_REPLAY_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_SELF_CONSISTENT_UNANCHORED = "SELF_CONSISTENT_UNANCHORED"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

HASH_ALGORITHM = "SHA-256"
HASH_ENCODING = "lowercase_hex"
CANONICALIZATION_PROFILE_ID = "hedgehog_kernel_json_c14n_v01"
SEAL_PROFILE_ID = "hedgehog_kernel_integrity_replay_v01"
MANIFEST_VERSION = "v0.1"
SUPPORTED_ARTIFACT_SCHEMA_VERSION = "v1"

_HASH_PREFIX = b"HEDGEHOG_KERNEL_V01\x00"
_SHA256_HEX = _re.compile(r"^[0-9a-f]{64}$")
_JSON_NORMALIZATION_ERROR_REASONS = (
    "json_cycle_invalid",
    "json_dataclass_requires_projection",
    "json_mapping_duplicate_key",
    "json_mapping_invalid",
    "json_mapping_key_invalid",
    "json_non_finite_number",
    "json_unicode_surrogate_invalid",
    "json_value_type_invalid",
)


@_dataclass(frozen=True)
class CanonicalArtifactRefV01:
    artifact_id: str
    artifact_type: str
    schema_version: str
    transaction_id: str
    owner_root_id: str
    authority_class: str
    lifecycle_state: str
    payload_hash: str


@_dataclass(frozen=True)
class ArtifactDependencyEdgeV01:
    artifact_id: str
    depends_on_artifact_id: str


@_dataclass(frozen=True)
class RootOwnershipBindingV01:
    artifact_id: str
    owner_root_id: str


@_dataclass(frozen=True)
class EvidenceClassBindingV01:
    artifact_id: str
    evidence_class: str


@_dataclass(frozen=True)
class AuthorityClassBindingV01:
    artifact_id: str
    authority_class: str


@_dataclass(frozen=True)
class SealProfileV01:
    profile_id: str
    manifest_version: str
    artifact_schema_version: str
    canonicalization_profile_id: str
    hash_algorithm: str
    hash_encoding: str
    payload_domain: str
    manifest_domain: str
    replay_domain: str
    timeline_order_required: bool


@_dataclass(frozen=True)
class ArtifactManifestV01:
    manifest_version: str
    transaction_id: str
    seal_profile: SealProfileV01
    artifacts: tuple[CanonicalArtifactRefV01, ...]
    dependency_edges: tuple[ArtifactDependencyEdgeV01, ...]
    root_ownership_bindings: tuple[RootOwnershipBindingV01, ...]
    evidence_class_bindings: tuple[EvidenceClassBindingV01, ...]
    authority_class_bindings: tuple[AuthorityClassBindingV01, ...]
    artifact_count: int
    dependency_edge_count: int
    root_ownership_binding_count: int
    evidence_class_binding_count: int
    authority_class_binding_count: int
    manifest_hash: str

    def __post_init__(self) -> None:
        _require_typed_tuple(self.artifacts, CanonicalArtifactRefV01)
        _require_typed_tuple(self.dependency_edges, ArtifactDependencyEdgeV01)
        _require_typed_tuple(
            self.root_ownership_bindings,
            RootOwnershipBindingV01,
        )
        _require_typed_tuple(
            self.evidence_class_bindings,
            EvidenceClassBindingV01,
        )
        _require_typed_tuple(
            self.authority_class_bindings,
            AuthorityClassBindingV01,
        )


@_dataclass(frozen=True)
class SealVerificationResultV01:
    verification_status: str
    verification_errors: tuple[str, ...]
    profile_verified: bool
    canonicalization_verified: bool
    artifact_ids_unique: bool
    artifact_order_verified: bool
    payload_hashes_verified: bool
    dependencies_verified: bool
    root_ownership_verified: bool
    evidence_classes_verified: bool
    authority_classes_verified: bool
    manifest_hash_verified: bool
    expected_manifest_hash_supplied: bool
    expected_manifest_hash_verified: bool
    artifact_count: int
    dependency_edge_count: int
    recomputed_manifest_hash: str

    def __post_init__(self) -> None:
        _require_string_tuple(self.verification_errors)


@_dataclass(frozen=True)
class ReplayVerificationResultV01:
    replay_status: str
    replay_errors: tuple[str, ...]
    replay_id: str
    manifest_hash: str
    manifest_verification_status: str
    artifact_count: int
    dependency_edge_count: int
    reconstructed_artifact_ids: tuple[str, ...]
    reconstructed_artifact_types: tuple[str, ...]
    reconstructed_owner_root_ids: tuple[str, ...]
    reconstructed_dependency_counts: tuple[int, ...]
    reconstructed_dependency_edges: tuple[ArtifactDependencyEdgeV01, ...]
    integrity_verified: bool
    continuity_verified: bool
    root_ownership_verified: bool
    evidence_classes_verified: bool
    authority_classes_verified: bool
    provider_call_count: int
    network_call_count: int
    semantic_rerun_count: int
    transaction_rerun_count: int
    corridor_rerun_count: int
    ledger_recollection_count: int
    crypto_recollection_count: int
    root_decision_created_count: int
    authority_created_count: int
    permission_created_count: int
    action_created_count: int
    action_commit_packet_created_count: int
    receipt_created_count: int
    final_output_created_count: int
    real_world_effects_count: int

    def __post_init__(self) -> None:
        _require_string_tuple(self.replay_errors)
        _require_string_tuple(self.reconstructed_artifact_ids)
        _require_string_tuple(self.reconstructed_artifact_types)
        _require_string_tuple(self.reconstructed_owner_root_ids)
        if type(self.reconstructed_dependency_counts) is not tuple or any(
            type(value) is not int for value in self.reconstructed_dependency_counts
        ):
            raise ValueError("replay_dependency_counts_invalid")
        _require_typed_tuple(
            self.reconstructed_dependency_edges,
            ArtifactDependencyEdgeV01,
        )


def build_default_seal_profile_v01(
    *,
    timeline_order_required: bool = True,
) -> SealProfileV01:
    if type(timeline_order_required) is not bool:
        raise ValueError("seal_profile_invalid")
    return SealProfileV01(
        profile_id=SEAL_PROFILE_ID,
        manifest_version=MANIFEST_VERSION,
        artifact_schema_version=SUPPORTED_ARTIFACT_SCHEMA_VERSION,
        canonicalization_profile_id=CANONICALIZATION_PROFILE_ID,
        hash_algorithm=HASH_ALGORITHM,
        hash_encoding=HASH_ENCODING,
        payload_domain="hedgehog.kernel.payload.v01",
        manifest_domain="hedgehog.kernel.manifest.v01",
        replay_domain="hedgehog.kernel.replay.v01",
        timeline_order_required=timeline_order_required,
    )


def canonical_json_bytes_v01(value: object) -> bytes:
    try:
        normalized = _normalize_json_value(value, set())
    except ValueError as exc:
        if _is_known_json_normalization_error(exc):
            raise
        raise ValueError("canonical_json_value_invalid") from None
    except Exception:
        raise ValueError("canonical_json_value_invalid") from None

    try:
        text = _json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return text.encode("utf-8", errors="strict")
    except Exception:
        raise ValueError("canonical_json_value_invalid") from None


def domain_separated_sha256_hex_v01(
    *,
    domain: str,
    payload: bytes,
) -> str:
    if type(domain) is not str or not domain:
        raise ValueError("hash_domain_invalid")
    try:
        domain_bytes = domain.encode("ascii", errors="strict")
    except UnicodeError as exc:
        raise ValueError("hash_domain_invalid") from exc
    if type(payload) is not bytes:
        raise ValueError("hash_payload_invalid")
    material = (
        _HASH_PREFIX
        + len(domain_bytes).to_bytes(4, "big")
        + domain_bytes
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return _hashlib.sha256(material).hexdigest()


def build_canonical_artifact_ref_v01(
    *,
    artifact_id: str,
    artifact_type: str,
    schema_version: str,
    transaction_id: str,
    owner_root_id: str,
    authority_class: str,
    lifecycle_state: str,
    payload: object,
    profile: SealProfileV01,
) -> CanonicalArtifactRefV01:
    _require_valid_profile(profile)
    for value in (
        artifact_id,
        artifact_type,
        transaction_id,
        owner_root_id,
        authority_class,
        lifecycle_state,
    ):
        if not _valid_nonempty_string(value):
            raise ValueError("artifact_ref_invalid")
    if (
        type(schema_version) is not str
        or schema_version != SUPPORTED_ARTIFACT_SCHEMA_VERSION
    ):
        raise ValueError("artifact_schema_unknown")
    payload_hash = domain_separated_sha256_hex_v01(
        domain=profile.payload_domain,
        payload=canonical_json_bytes_v01(payload),
    )
    return CanonicalArtifactRefV01(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        schema_version=schema_version,
        transaction_id=transaction_id,
        owner_root_id=owner_root_id,
        authority_class=authority_class,
        lifecycle_state=lifecycle_state,
        payload_hash=payload_hash,
    )


def build_artifact_manifest_v01(
    *,
    transaction_id: str,
    profile: SealProfileV01,
    artifacts: tuple[CanonicalArtifactRefV01, ...],
    dependency_edges: tuple[ArtifactDependencyEdgeV01, ...],
    root_ownership_bindings: tuple[RootOwnershipBindingV01, ...],
    evidence_class_bindings: tuple[EvidenceClassBindingV01, ...],
    authority_class_bindings: tuple[AuthorityClassBindingV01, ...],
) -> ArtifactManifestV01:
    _require_valid_profile(profile)
    if not _valid_nonempty_string(transaction_id):
        raise ValueError("manifest_contract_invalid")
    _require_typed_tuple(artifacts, CanonicalArtifactRefV01)
    if not artifacts:
        raise ValueError("manifest_contract_invalid")
    _require_typed_tuple(dependency_edges, ArtifactDependencyEdgeV01)
    _require_typed_tuple(root_ownership_bindings, RootOwnershipBindingV01)
    _require_typed_tuple(evidence_class_bindings, EvidenceClassBindingV01)
    _require_typed_tuple(authority_class_bindings, AuthorityClassBindingV01)

    for artifact in artifacts:
        _require_valid_artifact_ref(artifact)
        if artifact.transaction_id != transaction_id:
            raise ValueError("artifact_transaction_mismatch")
    artifact_ids = tuple(artifact.artifact_id for artifact in artifacts)
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError("artifact_id_duplicate")

    position = {artifact_id: index for index, artifact_id in enumerate(artifact_ids)}
    canonical_roots = _canonicalize_root_bindings(
        artifacts,
        root_ownership_bindings,
        position,
    )
    canonical_evidence = _canonicalize_evidence_bindings(
        artifacts,
        evidence_class_bindings,
        position,
    )
    canonical_authority = _canonicalize_authority_bindings(
        artifacts,
        authority_class_bindings,
        position,
    )
    canonical_edges = _canonicalize_dependency_edges(
        dependency_edges,
        position,
        profile.timeline_order_required,
    )
    _require_acyclic(artifact_ids, canonical_edges)

    counts = (
        len(artifacts),
        len(canonical_edges),
        len(canonical_roots),
        len(canonical_evidence),
        len(canonical_authority),
    )
    core = _manifest_core_plain(
        manifest_version=MANIFEST_VERSION,
        transaction_id=transaction_id,
        seal_profile=profile,
        artifacts=artifacts,
        dependency_edges=canonical_edges,
        root_ownership_bindings=canonical_roots,
        evidence_class_bindings=canonical_evidence,
        authority_class_bindings=canonical_authority,
        counts=counts,
    )
    manifest_hash = domain_separated_sha256_hex_v01(
        domain=profile.manifest_domain,
        payload=canonical_json_bytes_v01(core),
    )
    return ArtifactManifestV01(
        manifest_version=MANIFEST_VERSION,
        transaction_id=transaction_id,
        seal_profile=profile,
        artifacts=artifacts,
        dependency_edges=canonical_edges,
        root_ownership_bindings=canonical_roots,
        evidence_class_bindings=canonical_evidence,
        authority_class_bindings=canonical_authority,
        artifact_count=counts[0],
        dependency_edge_count=counts[1],
        root_ownership_binding_count=counts[2],
        evidence_class_binding_count=counts[3],
        authority_class_binding_count=counts[4],
        manifest_hash=manifest_hash,
    )


def verify_artifact_manifest_v01(
    *,
    manifest: object,
    payload_rows: object,
    expected_manifest_hash: object = None,
) -> SealVerificationResultV01:
    expected_supplied = expected_manifest_hash is not None
    try:
        return _verify_artifact_manifest_impl(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=expected_manifest_hash,
        )
    except Exception:
        return _seal_failure(
            ("manifest_contract_invalid",),
            expected_manifest_hash_supplied=expected_supplied,
        )


def verify_artifact_replay_v01(
    *,
    manifest: object,
    payload_rows: object,
    expected_manifest_hash: object,
) -> ReplayVerificationResultV01:
    try:
        if expected_manifest_hash is None:
            return _replay_failure(
                errors=("replay_expected_manifest_hash_required",),
                manifest=manifest,
                manifest_status=STATUS_BLOCKED_FAIL_CLOSED,
            )
        verification = verify_artifact_manifest_v01(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=expected_manifest_hash,
        )
        if verification.verification_status != STATUS_PASS:
            return _replay_failure(
                errors=("replay_manifest_verification_failed",),
                manifest=manifest,
                manifest_status=verification.verification_status,
            )
        if type(manifest) is not ArtifactManifestV01:
            return _replay_failure(
                errors=("replay_manifest_verification_failed",),
                manifest=manifest,
                manifest_status=verification.verification_status,
            )
        artifact_ids = tuple(item.artifact_id for item in manifest.artifacts)
        artifact_types = tuple(item.artifact_type for item in manifest.artifacts)
        owners = tuple(item.owner_root_id for item in manifest.artifacts)
        dependency_counts = tuple(
            sum(edge.artifact_id == artifact_id for edge in manifest.dependency_edges)
            for artifact_id in artifact_ids
        )
        replay_material = {
            "manifest_hash": manifest.manifest_hash,
            "artifact_ids": list(artifact_ids),
            "dependency_edges": [
                _dependency_edge_plain(edge) for edge in manifest.dependency_edges
            ],
        }
        replay_id = domain_separated_sha256_hex_v01(
            domain=manifest.seal_profile.replay_domain,
            payload=canonical_json_bytes_v01(replay_material),
        )
        return ReplayVerificationResultV01(
            replay_status=STATUS_PASS,
            replay_errors=(),
            replay_id=replay_id,
            manifest_hash=manifest.manifest_hash,
            manifest_verification_status=verification.verification_status,
            artifact_count=len(artifact_ids),
            dependency_edge_count=len(manifest.dependency_edges),
            reconstructed_artifact_ids=artifact_ids,
            reconstructed_artifact_types=artifact_types,
            reconstructed_owner_root_ids=owners,
            reconstructed_dependency_counts=dependency_counts,
            reconstructed_dependency_edges=manifest.dependency_edges,
            integrity_verified=True,
            continuity_verified=True,
            root_ownership_verified=True,
            evidence_classes_verified=True,
            authority_classes_verified=True,
            provider_call_count=0,
            network_call_count=0,
            semantic_rerun_count=0,
            transaction_rerun_count=0,
            corridor_rerun_count=0,
            ledger_recollection_count=0,
            crypto_recollection_count=0,
            root_decision_created_count=0,
            authority_created_count=0,
            permission_created_count=0,
            action_created_count=0,
            action_commit_packet_created_count=0,
            receipt_created_count=0,
            final_output_created_count=0,
            real_world_effects_count=0,
        )
    except Exception:
        return _replay_failure(
            errors=("replay_manifest_verification_failed",),
            manifest=manifest,
            manifest_status=STATUS_BLOCKED_FAIL_CLOSED,
        )


def artifact_manifest_to_plain_dict_v01(
    manifest: ArtifactManifestV01,
) -> dict[str, object]:
    try:
        if type(manifest) is not ArtifactManifestV01:
            raise ValueError("manifest_contract_invalid")
        projected = _manifest_core_plain(
            manifest_version=manifest.manifest_version,
            transaction_id=manifest.transaction_id,
            seal_profile=manifest.seal_profile,
            artifacts=manifest.artifacts,
            dependency_edges=manifest.dependency_edges,
            root_ownership_bindings=manifest.root_ownership_bindings,
            evidence_class_bindings=manifest.evidence_class_bindings,
            authority_class_bindings=manifest.authority_class_bindings,
            counts=(
                manifest.artifact_count,
                manifest.dependency_edge_count,
                manifest.root_ownership_binding_count,
                manifest.evidence_class_binding_count,
                manifest.authority_class_binding_count,
            ),
        )
        projected["manifest_hash"] = manifest.manifest_hash
        canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("manifest_contract_invalid") from None


def seal_verification_result_to_plain_dict_v01(
    result: SealVerificationResultV01,
) -> dict[str, object]:
    try:
        if type(result) is not SealVerificationResultV01:
            raise ValueError("seal_verification_result_invalid")
        projected = {
            "verification_status": result.verification_status,
            "verification_errors": list(result.verification_errors),
            "profile_verified": result.profile_verified,
            "canonicalization_verified": result.canonicalization_verified,
            "artifact_ids_unique": result.artifact_ids_unique,
            "artifact_order_verified": result.artifact_order_verified,
            "payload_hashes_verified": result.payload_hashes_verified,
            "dependencies_verified": result.dependencies_verified,
            "root_ownership_verified": result.root_ownership_verified,
            "evidence_classes_verified": result.evidence_classes_verified,
            "authority_classes_verified": result.authority_classes_verified,
            "manifest_hash_verified": result.manifest_hash_verified,
            "expected_manifest_hash_supplied": (
                result.expected_manifest_hash_supplied
            ),
            "expected_manifest_hash_verified": (
                result.expected_manifest_hash_verified
            ),
            "artifact_count": result.artifact_count,
            "dependency_edge_count": result.dependency_edge_count,
            "recomputed_manifest_hash": result.recomputed_manifest_hash,
        }
        canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("seal_verification_result_invalid") from None


def replay_verification_result_to_plain_dict_v01(
    result: ReplayVerificationResultV01,
) -> dict[str, object]:
    try:
        if type(result) is not ReplayVerificationResultV01:
            raise ValueError("replay_verification_result_invalid")
        projected = {
            "replay_status": result.replay_status,
            "replay_errors": list(result.replay_errors),
            "replay_id": result.replay_id,
            "manifest_hash": result.manifest_hash,
            "manifest_verification_status": result.manifest_verification_status,
            "artifact_count": result.artifact_count,
            "dependency_edge_count": result.dependency_edge_count,
            "reconstructed_artifact_ids": list(
                result.reconstructed_artifact_ids
            ),
            "reconstructed_artifact_types": list(
                result.reconstructed_artifact_types
            ),
            "reconstructed_owner_root_ids": list(
                result.reconstructed_owner_root_ids
            ),
            "reconstructed_dependency_counts": list(
                result.reconstructed_dependency_counts
            ),
            "reconstructed_dependency_edges": [
                _dependency_edge_plain(edge)
                for edge in result.reconstructed_dependency_edges
            ],
            "integrity_verified": result.integrity_verified,
            "continuity_verified": result.continuity_verified,
            "root_ownership_verified": result.root_ownership_verified,
            "evidence_classes_verified": result.evidence_classes_verified,
            "authority_classes_verified": result.authority_classes_verified,
            "provider_call_count": result.provider_call_count,
            "network_call_count": result.network_call_count,
            "semantic_rerun_count": result.semantic_rerun_count,
            "transaction_rerun_count": result.transaction_rerun_count,
            "corridor_rerun_count": result.corridor_rerun_count,
            "ledger_recollection_count": result.ledger_recollection_count,
            "crypto_recollection_count": result.crypto_recollection_count,
            "root_decision_created_count": result.root_decision_created_count,
            "authority_created_count": result.authority_created_count,
            "permission_created_count": result.permission_created_count,
            "action_created_count": result.action_created_count,
            "action_commit_packet_created_count": (
                result.action_commit_packet_created_count
            ),
            "receipt_created_count": result.receipt_created_count,
            "final_output_created_count": result.final_output_created_count,
            "real_world_effects_count": result.real_world_effects_count,
        }
        canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("replay_verification_result_invalid") from None


def _require_typed_tuple(value: object, item_type: type[object]) -> None:
    if type(value) is not tuple or any(type(item) is not item_type for item in value):
        raise ValueError("manifest_contract_invalid")


def _require_string_tuple(value: object) -> None:
    if type(value) is not tuple or any(type(item) is not str for item in value):
        raise ValueError("result_contract_invalid")


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _valid_nonempty_string(value: object) -> bool:
    return type(value) is str and bool(value) and not _contains_surrogate(value)


def _is_known_json_normalization_error(error: ValueError) -> bool:
    return bool(
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in _JSON_NORMALIZATION_ERROR_REASONS
    )


def _normalize_json_value(value: object, active_ids: set[int]) -> object:
    if value is None or type(value) is bool or type(value) is int:
        return value
    if type(value) is float:
        if not _math.isfinite(value):
            raise ValueError("json_non_finite_number")
        return value
    if type(value) is str:
        if _contains_surrogate(value):
            raise ValueError("json_unicode_surrogate_invalid")
        return value
    if type(value) in (bytes, bytearray, memoryview, set, frozenset):
        raise ValueError("json_value_type_invalid")
    if _is_dataclass(value) and not isinstance(value, type):
        raise ValueError("json_dataclass_requires_projection")
    if type(value) in (tuple, list):
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError("json_cycle_invalid")
        active_ids.add(value_id)
        try:
            return [_normalize_json_value(item, active_ids) for item in value]
        finally:
            active_ids.remove(value_id)
    if isinstance(value, _Mapping):
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError("json_cycle_invalid")
        active_ids.add(value_id)
        try:
            output: dict[str, object] = {}
            for key, item in value.items():
                if type(key) is not str or _contains_surrogate(key):
                    raise ValueError("json_mapping_key_invalid")
                if key in output:
                    raise ValueError("json_mapping_duplicate_key")
                output[key] = _normalize_json_value(item, active_ids)
            return output
        except ValueError as exc:
            if _is_known_json_normalization_error(exc):
                raise
            raise ValueError("json_mapping_invalid") from None
        except Exception:
            raise ValueError("json_mapping_invalid") from None
        finally:
            active_ids.remove(value_id)
    raise ValueError("json_value_type_invalid")


def _profile_flags(profile: object) -> tuple[bool, bool]:
    if type(profile) is not SealProfileV01:
        return False, False
    text_fields = (
        profile.profile_id,
        profile.manifest_version,
        profile.artifact_schema_version,
        profile.canonicalization_profile_id,
        profile.hash_algorithm,
        profile.hash_encoding,
        profile.payload_domain,
        profile.manifest_domain,
        profile.replay_domain,
    )
    if any(type(value) is not str for value in text_fields):
        return False, False
    if type(profile.timeline_order_required) is not bool:
        return False, False
    canonicalization = (
        profile.canonicalization_profile_id == CANONICALIZATION_PROFILE_ID
    )
    fixed = (
        profile.profile_id == SEAL_PROFILE_ID
        and profile.manifest_version == MANIFEST_VERSION
        and profile.artifact_schema_version == SUPPORTED_ARTIFACT_SCHEMA_VERSION
        and profile.hash_algorithm == HASH_ALGORITHM
        and profile.hash_encoding == HASH_ENCODING
        and profile.payload_domain == "hedgehog.kernel.payload.v01"
        and profile.manifest_domain == "hedgehog.kernel.manifest.v01"
        and profile.replay_domain == "hedgehog.kernel.replay.v01"
    )
    return fixed, canonicalization


def _require_valid_profile(profile: object) -> None:
    fixed, canonicalization = _profile_flags(profile)
    if not canonicalization:
        raise ValueError("canonicalization_profile_invalid")
    if not fixed:
        raise ValueError("seal_profile_invalid")


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _SHA256_HEX.fullmatch(value) is not None


def _require_valid_artifact_ref(artifact: object) -> None:
    if type(artifact) is not CanonicalArtifactRefV01:
        raise ValueError("artifact_ref_invalid")
    for value in (
        artifact.artifact_id,
        artifact.artifact_type,
        artifact.transaction_id,
        artifact.owner_root_id,
        artifact.authority_class,
        artifact.lifecycle_state,
    ):
        if not _valid_nonempty_string(value):
            raise ValueError("artifact_ref_invalid")
    if (
        type(artifact.schema_version) is not str
        or artifact.schema_version != SUPPORTED_ARTIFACT_SCHEMA_VERSION
    ):
        raise ValueError("artifact_schema_unknown")
    if not _valid_sha256(artifact.payload_hash):
        raise ValueError("artifact_ref_invalid")


def _binding_map(
    bindings: tuple[object, ...],
    binding_type: type[object],
    value_field: str,
    mismatch_reason: str,
) -> dict[str, str]:
    output: dict[str, str] = {}
    for binding in bindings:
        if type(binding) is not binding_type:
            raise ValueError(mismatch_reason)
        artifact_id = getattr(binding, "artifact_id", None)
        value = getattr(binding, value_field, None)
        if not _valid_nonempty_string(artifact_id) or not _valid_nonempty_string(value):
            raise ValueError(mismatch_reason)
        if artifact_id in output:
            raise ValueError(mismatch_reason)
        output[artifact_id] = value
    return output


def _canonicalize_root_bindings(
    artifacts: tuple[CanonicalArtifactRefV01, ...],
    bindings: tuple[RootOwnershipBindingV01, ...],
    position: dict[str, int],
) -> tuple[RootOwnershipBindingV01, ...]:
    values = _binding_map(
        bindings,
        RootOwnershipBindingV01,
        "owner_root_id",
        "root_ownership_binding_mismatch",
    )
    expected = {artifact.artifact_id: artifact.owner_root_id for artifact in artifacts}
    if values != expected:
        raise ValueError("root_ownership_binding_mismatch")
    return tuple(sorted(bindings, key=lambda item: position[item.artifact_id]))


def _canonicalize_evidence_bindings(
    artifacts: tuple[CanonicalArtifactRefV01, ...],
    bindings: tuple[EvidenceClassBindingV01, ...],
    position: dict[str, int],
) -> tuple[EvidenceClassBindingV01, ...]:
    values = _binding_map(
        bindings,
        EvidenceClassBindingV01,
        "evidence_class",
        "evidence_class_binding_mismatch",
    )
    if set(values) != {artifact.artifact_id for artifact in artifacts}:
        raise ValueError("evidence_class_binding_mismatch")
    return tuple(sorted(bindings, key=lambda item: position[item.artifact_id]))


def _canonicalize_authority_bindings(
    artifacts: tuple[CanonicalArtifactRefV01, ...],
    bindings: tuple[AuthorityClassBindingV01, ...],
    position: dict[str, int],
) -> tuple[AuthorityClassBindingV01, ...]:
    values = _binding_map(
        bindings,
        AuthorityClassBindingV01,
        "authority_class",
        "authority_class_binding_mismatch",
    )
    expected = {artifact.artifact_id: artifact.authority_class for artifact in artifacts}
    if values != expected:
        raise ValueError("authority_class_binding_mismatch")
    return tuple(sorted(bindings, key=lambda item: position[item.artifact_id]))


def _canonicalize_dependency_edges(
    edges: tuple[ArtifactDependencyEdgeV01, ...],
    position: dict[str, int],
    timeline_order_required: bool,
) -> tuple[ArtifactDependencyEdgeV01, ...]:
    pairs: list[tuple[str, str]] = []
    for edge in edges:
        if type(edge) is not ArtifactDependencyEdgeV01:
            raise ValueError("dependency_edge_invalid")
        if not _valid_nonempty_string(edge.artifact_id) or not _valid_nonempty_string(
            edge.depends_on_artifact_id
        ):
            raise ValueError("dependency_edge_invalid")
        pair = (edge.artifact_id, edge.depends_on_artifact_id)
        if pair in pairs:
            raise ValueError("dependency_edge_duplicate")
        pairs.append(pair)
        if edge.artifact_id == edge.depends_on_artifact_id:
            raise ValueError("dependency_edge_invalid")
        if edge.artifact_id not in position or edge.depends_on_artifact_id not in position:
            raise ValueError("dependency_edge_invalid")
        if timeline_order_required and position[edge.depends_on_artifact_id] >= position[
            edge.artifact_id
        ]:
            raise ValueError("dependency_forward_not_allowed")
    return tuple(
        sorted(
            edges,
            key=lambda edge: (
                position[edge.artifact_id],
                position[edge.depends_on_artifact_id],
                edge.artifact_id,
                edge.depends_on_artifact_id,
            ),
        )
    )


def _require_acyclic(
    artifact_ids: tuple[str, ...],
    edges: tuple[ArtifactDependencyEdgeV01, ...],
) -> None:
    dependencies = {
        artifact_id: tuple(
            edge.depends_on_artifact_id
            for edge in edges
            if edge.artifact_id == artifact_id
        )
        for artifact_id in artifact_ids
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str) -> None:
        if artifact_id in visiting:
            raise ValueError("dependency_cycle")
        if artifact_id in visited:
            return
        visiting.add(artifact_id)
        for dependency in dependencies[artifact_id]:
            visit(dependency)
        visiting.remove(artifact_id)
        visited.add(artifact_id)

    for artifact_id in artifact_ids:
        visit(artifact_id)


def _profile_plain(profile: SealProfileV01) -> dict[str, object]:
    return {
        "profile_id": profile.profile_id,
        "manifest_version": profile.manifest_version,
        "artifact_schema_version": profile.artifact_schema_version,
        "canonicalization_profile_id": profile.canonicalization_profile_id,
        "hash_algorithm": profile.hash_algorithm,
        "hash_encoding": profile.hash_encoding,
        "payload_domain": profile.payload_domain,
        "manifest_domain": profile.manifest_domain,
        "replay_domain": profile.replay_domain,
        "timeline_order_required": profile.timeline_order_required,
    }


def _artifact_plain(artifact: CanonicalArtifactRefV01) -> dict[str, object]:
    return {
        "artifact_id": artifact.artifact_id,
        "artifact_type": artifact.artifact_type,
        "schema_version": artifact.schema_version,
        "transaction_id": artifact.transaction_id,
        "owner_root_id": artifact.owner_root_id,
        "authority_class": artifact.authority_class,
        "lifecycle_state": artifact.lifecycle_state,
        "payload_hash": artifact.payload_hash,
    }


def _dependency_edge_plain(edge: ArtifactDependencyEdgeV01) -> dict[str, object]:
    return {
        "artifact_id": edge.artifact_id,
        "depends_on_artifact_id": edge.depends_on_artifact_id,
    }


def _root_binding_plain(binding: RootOwnershipBindingV01) -> dict[str, object]:
    return {
        "artifact_id": binding.artifact_id,
        "owner_root_id": binding.owner_root_id,
    }


def _evidence_binding_plain(
    binding: EvidenceClassBindingV01,
) -> dict[str, object]:
    return {
        "artifact_id": binding.artifact_id,
        "evidence_class": binding.evidence_class,
    }


def _authority_binding_plain(
    binding: AuthorityClassBindingV01,
) -> dict[str, object]:
    return {
        "artifact_id": binding.artifact_id,
        "authority_class": binding.authority_class,
    }


def _manifest_core_plain(
    *,
    manifest_version: str,
    transaction_id: str,
    seal_profile: SealProfileV01,
    artifacts: tuple[CanonicalArtifactRefV01, ...],
    dependency_edges: tuple[ArtifactDependencyEdgeV01, ...],
    root_ownership_bindings: tuple[RootOwnershipBindingV01, ...],
    evidence_class_bindings: tuple[EvidenceClassBindingV01, ...],
    authority_class_bindings: tuple[AuthorityClassBindingV01, ...],
    counts: tuple[int, int, int, int, int],
) -> dict[str, object]:
    return {
        "manifest_version": manifest_version,
        "transaction_id": transaction_id,
        "seal_profile": _profile_plain(seal_profile),
        "artifacts": [_artifact_plain(item) for item in artifacts],
        "dependency_edges": [
            _dependency_edge_plain(item) for item in dependency_edges
        ],
        "root_ownership_bindings": [
            _root_binding_plain(item) for item in root_ownership_bindings
        ],
        "evidence_class_bindings": [
            _evidence_binding_plain(item) for item in evidence_class_bindings
        ],
        "authority_class_bindings": [
            _authority_binding_plain(item) for item in authority_class_bindings
        ],
        "artifact_count": counts[0],
        "dependency_edge_count": counts[1],
        "root_ownership_binding_count": counts[2],
        "evidence_class_binding_count": counts[3],
        "authority_class_binding_count": counts[4],
    }


def _verify_artifact_manifest_impl(
    *,
    manifest: object,
    payload_rows: object,
    expected_manifest_hash: object,
) -> SealVerificationResultV01:
    if type(manifest) is not ArtifactManifestV01:
        return _seal_failure(
            ("manifest_contract_invalid",),
            expected_manifest_hash_supplied=(expected_manifest_hash is not None),
        )
    errors: list[str] = []
    fixed_profile, canonicalization = _profile_flags(manifest.seal_profile)
    if not fixed_profile:
        errors.append("seal_profile_invalid")
    if not canonicalization:
        errors.append("canonicalization_profile_invalid")
    if manifest.manifest_version != MANIFEST_VERSION:
        errors.append("manifest_contract_invalid")

    artifacts_valid = True
    artifact_ids: tuple[str, ...] = ()
    try:
        _require_typed_tuple(manifest.artifacts, CanonicalArtifactRefV01)
        artifact_ids = tuple(item.artifact_id for item in manifest.artifacts)
        for artifact in manifest.artifacts:
            _require_valid_artifact_ref(artifact)
            if artifact.transaction_id != manifest.transaction_id:
                errors.append("artifact_transaction_mismatch")
        if any(
            artifact.schema_version != SUPPORTED_ARTIFACT_SCHEMA_VERSION
            for artifact in manifest.artifacts
        ):
            errors.append("artifact_schema_unknown")
    except ValueError as exc:
        errors.append(_safe_reason(exc, "artifact_ref_invalid"))
        artifacts_valid = False
    artifact_ids_unique = bool(
        artifacts_valid
        and artifact_ids
        and len(artifact_ids) == len(set(artifact_ids))
    )
    if artifacts_valid and not artifact_ids_unique:
        errors.append("artifact_id_duplicate")

    rows_valid, payload_ids, payload_values = _normalize_payload_rows(payload_rows)
    if not rows_valid:
        errors.append("payload_rows_invalid")
    payload_match = rows_valid and payload_ids == artifact_ids
    if rows_valid and not payload_match:
        errors.append("payload_rows_mismatch")

    payload_hashes_verified = False
    if fixed_profile and canonicalization and artifacts_valid and payload_match:
        computed: list[str] = []
        try:
            for payload in payload_values:
                computed.append(
                    domain_separated_sha256_hex_v01(
                        domain=manifest.seal_profile.payload_domain,
                        payload=canonical_json_bytes_v01(payload),
                    )
                )
            payload_hashes_verified = tuple(computed) == tuple(
                item.payload_hash for item in manifest.artifacts
            )
        except ValueError:
            errors.append("payload_rows_invalid")
        if not payload_hashes_verified and "payload_rows_invalid" not in errors:
            errors.append("payload_hash_mismatch")

    rebuilt: ArtifactManifestV01 | None = None
    if fixed_profile and canonicalization and artifacts_valid and artifact_ids_unique:
        try:
            rebuilt = build_artifact_manifest_v01(
                transaction_id=manifest.transaction_id,
                profile=manifest.seal_profile,
                artifacts=manifest.artifacts,
                dependency_edges=manifest.dependency_edges,
                root_ownership_bindings=manifest.root_ownership_bindings,
                evidence_class_bindings=manifest.evidence_class_bindings,
                authority_class_bindings=manifest.authority_class_bindings,
            )
        except ValueError as exc:
            errors.append(_safe_reason(exc, "manifest_contract_invalid"))

    dependencies_verified = bool(
        rebuilt is not None and rebuilt.dependency_edges == manifest.dependency_edges
    )
    root_verified = bool(
        rebuilt is not None
        and rebuilt.root_ownership_bindings == manifest.root_ownership_bindings
    )
    evidence_verified = bool(
        rebuilt is not None
        and rebuilt.evidence_class_bindings == manifest.evidence_class_bindings
    )
    authority_verified = bool(
        rebuilt is not None
        and rebuilt.authority_class_bindings == manifest.authority_class_bindings
    )
    if rebuilt is not None:
        derived_counts_match = (
            type(manifest.artifact_count) is int
            and manifest.artifact_count == rebuilt.artifact_count
            and type(manifest.dependency_edge_count) is int
            and manifest.dependency_edge_count == rebuilt.dependency_edge_count
            and type(manifest.root_ownership_binding_count) is int
            and manifest.root_ownership_binding_count
            == rebuilt.root_ownership_binding_count
            and type(manifest.evidence_class_binding_count) is int
            and manifest.evidence_class_binding_count
            == rebuilt.evidence_class_binding_count
            and type(manifest.authority_class_binding_count) is int
            and manifest.authority_class_binding_count
            == rebuilt.authority_class_binding_count
        )
        if not derived_counts_match:
            errors.append("manifest_derived_count_mismatch")
    else:
        derived_counts_match = False

    recomputed_hash = rebuilt.manifest_hash if rebuilt is not None else ""
    manifest_hash_verified = bool(
        rebuilt is not None
        and _valid_sha256(manifest.manifest_hash)
        and manifest.manifest_hash == recomputed_hash
    )
    if rebuilt is not None and not manifest_hash_verified:
        errors.append("manifest_hash_mismatch")

    expected_supplied = expected_manifest_hash is not None
    expected_verified = False
    if expected_supplied:
        if not _valid_sha256(expected_manifest_hash):
            errors.append("expected_manifest_hash_invalid")
        elif expected_manifest_hash != recomputed_hash:
            errors.append("expected_manifest_hash_mismatch")
        else:
            expected_verified = True

    artifact_order_verified = bool(payload_match and dependencies_verified)
    errors = list(dict.fromkeys(errors))
    internal_ok = bool(
        fixed_profile
        and canonicalization
        and artifact_ids_unique
        and artifact_order_verified
        and payload_hashes_verified
        and dependencies_verified
        and root_verified
        and evidence_verified
        and authority_verified
        and derived_counts_match
        and manifest_hash_verified
    )
    if not internal_ok and not errors:
        errors.append("manifest_contract_invalid")
    status = (
        STATUS_PASS
        if internal_ok and expected_supplied and expected_verified and not errors
        else STATUS_SELF_CONSISTENT_UNANCHORED
        if internal_ok and not expected_supplied and not errors
        else STATUS_BLOCKED_FAIL_CLOSED
    )
    return SealVerificationResultV01(
        verification_status=status,
        verification_errors=tuple(errors),
        profile_verified=fixed_profile,
        canonicalization_verified=canonicalization,
        artifact_ids_unique=artifact_ids_unique,
        artifact_order_verified=artifact_order_verified,
        payload_hashes_verified=payload_hashes_verified,
        dependencies_verified=dependencies_verified,
        root_ownership_verified=root_verified,
        evidence_classes_verified=evidence_verified,
        authority_classes_verified=authority_verified,
        manifest_hash_verified=manifest_hash_verified,
        expected_manifest_hash_supplied=expected_supplied,
        expected_manifest_hash_verified=expected_verified,
        artifact_count=len(artifact_ids) if artifacts_valid else 0,
        dependency_edge_count=(
            len(manifest.dependency_edges)
            if type(manifest.dependency_edges) is tuple
            else 0
        ),
        recomputed_manifest_hash=recomputed_hash,
    )


def _normalize_payload_rows(
    payload_rows: object,
) -> tuple[bool, tuple[str, ...], tuple[object, ...]]:
    if type(payload_rows) is not tuple:
        return False, (), ()
    ids: list[str] = []
    values: list[object] = []
    for row in payload_rows:
        if type(row) is not tuple or len(row) != 2:
            return False, (), ()
        artifact_id, payload = row
        if not _valid_nonempty_string(artifact_id) or artifact_id in ids:
            return False, (), ()
        ids.append(artifact_id)
        values.append(payload)
    return True, tuple(ids), tuple(values)


def _safe_reason(error: ValueError, fallback: str) -> str:
    value = str(error)
    allowed = (
        "seal_profile_invalid",
        "canonicalization_profile_invalid",
        "manifest_contract_invalid",
        "artifact_ref_invalid",
        "artifact_id_duplicate",
        "artifact_transaction_mismatch",
        "artifact_schema_unknown",
        "dependency_edge_invalid",
        "dependency_edge_duplicate",
        "dependency_forward_not_allowed",
        "dependency_cycle",
        "root_ownership_binding_mismatch",
        "evidence_class_binding_mismatch",
        "authority_class_binding_mismatch",
    )
    return value if value in allowed else fallback


def _seal_failure(
    errors: tuple[str, ...],
    *,
    expected_manifest_hash_supplied: bool,
) -> SealVerificationResultV01:
    return SealVerificationResultV01(
        verification_status=STATUS_BLOCKED_FAIL_CLOSED,
        verification_errors=tuple(dict.fromkeys(errors)),
        profile_verified=False,
        canonicalization_verified=False,
        artifact_ids_unique=False,
        artifact_order_verified=False,
        payload_hashes_verified=False,
        dependencies_verified=False,
        root_ownership_verified=False,
        evidence_classes_verified=False,
        authority_classes_verified=False,
        manifest_hash_verified=False,
        expected_manifest_hash_supplied=expected_manifest_hash_supplied,
        expected_manifest_hash_verified=False,
        artifact_count=0,
        dependency_edge_count=0,
        recomputed_manifest_hash="",
    )


def _replay_failure(
    *,
    errors: tuple[str, ...],
    manifest: object,
    manifest_status: str,
) -> ReplayVerificationResultV01:
    manifest_hash = (
        manifest.manifest_hash
        if type(manifest) is ArtifactManifestV01
        and _valid_sha256(manifest.manifest_hash)
        else ""
    )
    return ReplayVerificationResultV01(
        replay_status=STATUS_BLOCKED_FAIL_CLOSED,
        replay_errors=tuple(dict.fromkeys(errors)),
        replay_id="",
        manifest_hash=manifest_hash,
        manifest_verification_status=manifest_status,
        artifact_count=0,
        dependency_edge_count=0,
        reconstructed_artifact_ids=(),
        reconstructed_artifact_types=(),
        reconstructed_owner_root_ids=(),
        reconstructed_dependency_counts=(),
        reconstructed_dependency_edges=(),
        integrity_verified=False,
        continuity_verified=False,
        root_ownership_verified=False,
        evidence_classes_verified=False,
        authority_classes_verified=False,
        provider_call_count=0,
        network_call_count=0,
        semantic_rerun_count=0,
        transaction_rerun_count=0,
        corridor_rerun_count=0,
        ledger_recollection_count=0,
        crypto_recollection_count=0,
        root_decision_created_count=0,
        authority_created_count=0,
        permission_created_count=0,
        action_created_count=0,
        action_commit_packet_created_count=0,
        receipt_created_count=0,
        final_output_created_count=0,
        real_world_effects_count=0,
    )
