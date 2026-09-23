"""Domain-neutral sealed Replay evidence contract only.

This contract records supplied deterministic reconstruction evidence; it does
not perform filesystem Replay, semantic, Root-decision, or Corridor reruns,
package discovery, provider, network, Gemini, filesystem, clock, randomness,
signature, signer authentication, Root Attestation, or PKI operations. It
creates no authority, permission, action, receipt, FinalOutput, or effect and
makes no production-certification claim. Hashes establish declared integrity
and continuity, not semantic truth. Replay PASS is derived, never caller
supplied. Replay reconstructs accepted evidence and does not re-execute the
original business process.
"""

from dataclasses import dataclass as _dataclass
import re as _re
import unicodedata as _unicodedata

from hedgehog.evidence.external_anchor_v01 import (
    STATUS_ANCHORED_PASS as _STATUS_ANCHORED_PASS,
    STATUS_EVIDENCE_ONLY as _STATUS_EVIDENCE_ONLY,
    STATUS_FAIL_CLOSED as _ANCHOR_STATUS_FAIL_CLOSED,
    AnchoredPackageVerificationV01 as _AnchoredPackageVerificationV01,
    ExternalAnchorPublicationV01 as _ExternalAnchorPublicationV01,
    validate_anchored_package_verification_v01 as _validate_anchored_package_verification_v01,
    validate_external_anchor_publication_v01 as _validate_external_anchor_publication_v01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    STATUS_FAIL_CLOSED as _PROFILE_STATUS_FAIL_CLOSED,
    STATUS_PASS as _PROFILE_STATUS_PASS,
    DomainEvidenceProjectionV01 as _DomainEvidenceProjectionV01,
    validate_domain_evidence_projection_v01 as _validate_domain_evidence_projection_v01,
)
from hedgehog.evidence.sealed_package_v01 import (
    STATUS_FAIL_CLOSED as _PACKAGE_STATUS_FAIL_CLOSED,
    STATUS_SELF_CONSISTENT_UNANCHORED as _STATUS_SELF_CONSISTENT_UNANCHORED,
    SealedPackageManifestV01 as _SealedPackageManifestV01,
    validate_sealed_package_manifest_v01 as _validate_sealed_package_manifest_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "sealed_replay_evidence_v01"
REPLAY_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
REPLAY_STATUSES = (
    STATUS_PASS,
    STATUS_FAIL_CLOSED,
)

_FILE_ORDER_DOMAIN = "hedgehog.evidence.sealed_replay.file_order.v01"
_ARTIFACT_ORDER_DOMAIN = "hedgehog.evidence.sealed_replay.artifact_order.v01"
_REPLAY_IDENTITY_DOMAIN = "hedgehog.evidence.sealed_replay_evidence.v01"
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:")


@_dataclass(frozen=True, slots=True)
class SealedReplayEvidenceV01:
    replay_id: str
    replay_version: str
    source_manifest_id: str
    reconstructed_manifest_id: str
    anchor_publication_id: str
    anchored_verification_id: str
    source_domain_projection_id: str
    reconstructed_domain_projection_id: str
    domain_id: str
    package_id: str
    logical_package_ref: str
    source_package_content_hash: str
    reconstructed_package_content_hash: str
    source_file_count: int
    reconstructed_file_count: int
    source_artifact_count: int
    reconstructed_artifact_count: int
    source_file_order_hash: str
    reconstructed_file_order_hash: str
    source_artifact_order_hash: str
    reconstructed_artifact_order_hash: str
    integrity_verified: bool
    continuity_verified: bool
    anchor_verified: bool
    semantic_rerun_count: int
    root_decision_rerun_count: int
    corridor_rerun_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    action_created_count: int
    receipt_created_count: int
    final_output_created_count: int
    real_world_effects_count: int
    evidence_refs: tuple[str, ...]
    replay_status: str

    def __post_init__(self) -> None:
        if type(self.evidence_refs) is not tuple:
            raise ValueError("sealed_replay_evidence_invalid")


def build_sealed_replay_evidence_v01(
    *,
    source_manifest: _SealedPackageManifestV01,
    source_domain_projection: _DomainEvidenceProjectionV01,
    source_safe_file_contents: tuple[bytes, ...],
    anchor_publication: _ExternalAnchorPublicationV01,
    anchored_verification: _AnchoredPackageVerificationV01,
    supplied_anchor_publication_id: str,
    reconstructed_manifest: _SealedPackageManifestV01,
    reconstructed_domain_projection: _DomainEvidenceProjectionV01,
    reconstructed_safe_file_contents: tuple[bytes, ...],
    evidence_refs: tuple[str, ...],
) -> SealedReplayEvidenceV01:
    try:
        source_errors = _source_context_errors(
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_safe_file_contents,
            anchor_publication=anchor_publication,
            anchored_verification=anchored_verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        if source_errors:
            raise ValueError(source_errors[0])
        reconstructed_errors = _reconstructed_context_errors(
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
        )
        if reconstructed_errors:
            raise ValueError(reconstructed_errors[0])
        if not _evidence_refs_valid(evidence_refs):
            raise ValueError("sealed_replay_reference_invalid")
        copied_evidence_refs = tuple(item for item in evidence_refs)

        source_file_order_hash = _file_order_hash(source_manifest)
        reconstructed_file_order_hash = _file_order_hash(reconstructed_manifest)
        source_artifact_order_hash = _artifact_order_hash(source_manifest)
        reconstructed_artifact_order_hash = _artifact_order_hash(
            reconstructed_manifest
        )
        integrity_verified = _integrity_verified(
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
        )
        continuity_verified = _continuity_verified(
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_safe_file_contents,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
            source_file_order_hash=source_file_order_hash,
            reconstructed_file_order_hash=reconstructed_file_order_hash,
            source_artifact_order_hash=source_artifact_order_hash,
            reconstructed_artifact_order_hash=reconstructed_artifact_order_hash,
        )
        anchor_verified = _anchor_verified(
            anchor_publication=anchor_publication,
            anchored_verification=anchored_verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        replay_status = _replay_status(
            integrity_verified=integrity_verified,
            continuity_verified=continuity_verified,
            anchor_verified=anchor_verified,
            evidence_refs=copied_evidence_refs,
        )
        provisional = SealedReplayEvidenceV01(
            replay_id="0" * 64,
            replay_version=REPLAY_VERSION,
            source_manifest_id=source_manifest.manifest_id,
            reconstructed_manifest_id=reconstructed_manifest.manifest_id,
            anchor_publication_id=anchor_publication.anchor_publication_id,
            anchored_verification_id=anchored_verification.anchored_verification_id,
            source_domain_projection_id=source_domain_projection.projection_id,
            reconstructed_domain_projection_id=(
                reconstructed_domain_projection.projection_id
            ),
            domain_id=source_manifest.domain_id,
            package_id=source_manifest.package_id,
            logical_package_ref=source_manifest.logical_package_ref,
            source_package_content_hash=source_manifest.package_content_hash,
            reconstructed_package_content_hash=(
                reconstructed_manifest.package_content_hash
            ),
            source_file_count=source_manifest.file_count,
            reconstructed_file_count=reconstructed_manifest.file_count,
            source_artifact_count=source_manifest.artifact_count,
            reconstructed_artifact_count=reconstructed_manifest.artifact_count,
            source_file_order_hash=source_file_order_hash,
            reconstructed_file_order_hash=reconstructed_file_order_hash,
            source_artifact_order_hash=source_artifact_order_hash,
            reconstructed_artifact_order_hash=reconstructed_artifact_order_hash,
            integrity_verified=integrity_verified,
            continuity_verified=continuity_verified,
            anchor_verified=anchor_verified,
            semantic_rerun_count=0,
            root_decision_rerun_count=0,
            corridor_rerun_count=0,
            provider_call_count=0,
            network_call_count=0,
            gemini_call_count=0,
            created_authority_count=0,
            created_permission_count=0,
            action_created_count=0,
            receipt_created_count=0,
            final_output_created_count=0,
            real_world_effects_count=0,
            evidence_refs=copied_evidence_refs,
            replay_status=replay_status,
        )
        result = _replace_replay_id(provisional, _replay_identity(provisional))
        errors = _replay_errors(
            result,
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_safe_file_contents,
            anchor_publication=anchor_publication,
            anchored_verification=anchored_verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
        )
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_replay_reason(error)) from None
    except Exception:
        raise ValueError("sealed_replay_unexpected_exception") from None


def validate_sealed_replay_evidence_v01(
    result: object,
    *,
    source_manifest: _SealedPackageManifestV01,
    source_domain_projection: _DomainEvidenceProjectionV01,
    source_safe_file_contents: tuple[bytes, ...],
    anchor_publication: _ExternalAnchorPublicationV01,
    anchored_verification: _AnchoredPackageVerificationV01,
    supplied_anchor_publication_id: str,
    reconstructed_manifest: _SealedPackageManifestV01,
    reconstructed_domain_projection: _DomainEvidenceProjectionV01,
    reconstructed_safe_file_contents: tuple[bytes, ...],
) -> tuple[str, ...]:
    try:
        return _replay_errors(
            result,
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_safe_file_contents,
            anchor_publication=anchor_publication,
            anchored_verification=anchored_verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
        )
    except Exception:
        return ("sealed_replay_unexpected_exception",)


def sealed_replay_evidence_to_plain_dict_v01(
    result: SealedReplayEvidenceV01,
    *,
    source_manifest: _SealedPackageManifestV01,
    source_domain_projection: _DomainEvidenceProjectionV01,
    source_safe_file_contents: tuple[bytes, ...],
    anchor_publication: _ExternalAnchorPublicationV01,
    anchored_verification: _AnchoredPackageVerificationV01,
    supplied_anchor_publication_id: str,
    reconstructed_manifest: _SealedPackageManifestV01,
    reconstructed_domain_projection: _DomainEvidenceProjectionV01,
    reconstructed_safe_file_contents: tuple[bytes, ...],
) -> dict[str, object]:
    try:
        if _replay_errors(
            result,
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_safe_file_contents,
            anchor_publication=anchor_publication,
            anchored_verification=anchored_verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
        ):
            raise ValueError
        projected = _replay_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("sealed_replay_evidence_invalid") from None


def _replay_errors(
    result: object,
    *,
    source_manifest: object,
    source_domain_projection: object,
    source_safe_file_contents: object,
    anchor_publication: object,
    anchored_verification: object,
    supplied_anchor_publication_id: object,
    reconstructed_manifest: object,
    reconstructed_domain_projection: object,
    reconstructed_safe_file_contents: object,
) -> tuple[str, ...]:
    if type(result) is not SealedReplayEvidenceV01:
        return ("sealed_replay_evidence_invalid",)
    errors: list[str] = []
    source_errors = _source_context_errors(
        source_manifest=source_manifest,
        source_domain_projection=source_domain_projection,
        source_safe_file_contents=source_safe_file_contents,
        anchor_publication=anchor_publication,
        anchored_verification=anchored_verification,
        supplied_anchor_publication_id=supplied_anchor_publication_id,
    )
    reconstructed_errors = _reconstructed_context_errors(
        reconstructed_manifest=reconstructed_manifest,
        reconstructed_domain_projection=reconstructed_domain_projection,
        reconstructed_safe_file_contents=reconstructed_safe_file_contents,
    )
    errors.extend(source_errors)
    errors.extend(reconstructed_errors)

    identity_values = (
        result.replay_id,
        result.source_manifest_id,
        result.reconstructed_manifest_id,
        result.anchor_publication_id,
        result.anchored_verification_id,
        result.source_domain_projection_id,
        result.reconstructed_domain_projection_id,
        result.source_package_content_hash,
        result.reconstructed_package_content_hash,
        result.source_file_order_hash,
        result.reconstructed_file_order_hash,
        result.source_artifact_order_hash,
        result.reconstructed_artifact_order_hash,
    )
    geometry_counts = (
        result.source_file_count,
        result.reconstructed_file_count,
        result.source_artifact_count,
        result.reconstructed_artifact_count,
    )
    bool_values = (
        result.integrity_verified,
        result.continuity_verified,
        result.anchor_verified,
    )
    zero_counts = (
        result.semantic_rerun_count,
        result.root_decision_rerun_count,
        result.corridor_rerun_count,
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.action_created_count,
        result.receipt_created_count,
        result.final_output_created_count,
        result.real_world_effects_count,
    )
    if (
        result.replay_version != REPLAY_VERSION
        or any(not _valid_sha256(item) for item in identity_values)
        or not _valid_text(result.domain_id)
        or not _valid_text(result.package_id)
        or not _logical_ref_valid(result.logical_package_ref)
        or any(not _nonnegative_int(item) for item in geometry_counts)
        or any(type(item) is not bool for item in bool_values)
        or any(not _nonnegative_int(item) for item in zero_counts)
        or type(result.replay_status) is not str
        or result.replay_status not in REPLAY_STATUSES
    ):
        errors.append("sealed_replay_evidence_invalid")
    if not _evidence_refs_valid(result.evidence_refs):
        errors.append("sealed_replay_reference_invalid")

    contexts_valid = not source_errors and not reconstructed_errors
    if contexts_valid:
        source_manifest_typed = source_manifest
        source_projection_typed = source_domain_projection
        reconstructed_manifest_typed = reconstructed_manifest
        reconstructed_projection_typed = reconstructed_domain_projection
        anchor_typed = anchor_publication
        verification_typed = anchored_verification

        if (
            result.source_manifest_id != source_manifest_typed.manifest_id
            or result.reconstructed_manifest_id
            != reconstructed_manifest_typed.manifest_id
            or result.domain_id != source_manifest_typed.domain_id
            or result.package_id != source_manifest_typed.package_id
            or result.logical_package_ref
            != source_manifest_typed.logical_package_ref
        ):
            errors.append("sealed_replay_manifest_binding_mismatch")
        if (
            result.source_domain_projection_id
            != source_projection_typed.projection_id
            or result.reconstructed_domain_projection_id
            != reconstructed_projection_typed.projection_id
        ):
            errors.append("sealed_replay_projection_mismatch")
        if (
            result.anchor_publication_id != anchor_typed.anchor_publication_id
            or result.anchored_verification_id
            != verification_typed.anchored_verification_id
        ):
            errors.append("sealed_replay_anchor_invalid")
        if (
            result.source_package_content_hash
            != source_manifest_typed.package_content_hash
            or result.reconstructed_package_content_hash
            != reconstructed_manifest_typed.package_content_hash
        ):
            errors.append("sealed_replay_hash_mismatch")
        if (
            not _nonnegative_int(result.source_file_count)
            or not _nonnegative_int(result.reconstructed_file_count)
            or result.source_file_count != source_manifest_typed.file_count
            or result.reconstructed_file_count
            != reconstructed_manifest_typed.file_count
        ):
            errors.append("sealed_replay_file_geometry_invalid")
        if (
            not _nonnegative_int(result.source_artifact_count)
            or not _nonnegative_int(result.reconstructed_artifact_count)
            or result.source_artifact_count != source_manifest_typed.artifact_count
            or result.reconstructed_artifact_count
            != reconstructed_manifest_typed.artifact_count
        ):
            errors.append("sealed_replay_artifact_geometry_invalid")

        source_file_order_hash = _file_order_hash(source_manifest_typed)
        reconstructed_file_order_hash = _file_order_hash(
            reconstructed_manifest_typed
        )
        source_artifact_order_hash = _artifact_order_hash(source_manifest_typed)
        reconstructed_artifact_order_hash = _artifact_order_hash(
            reconstructed_manifest_typed
        )
        if (
            result.source_file_order_hash != source_file_order_hash
            or result.reconstructed_file_order_hash
            != reconstructed_file_order_hash
            or result.source_artifact_order_hash != source_artifact_order_hash
            or result.reconstructed_artifact_order_hash
            != reconstructed_artifact_order_hash
        ):
            errors.append("sealed_replay_hash_mismatch")

        expected_integrity = _integrity_verified(
            source_manifest=source_manifest_typed,
            source_domain_projection=source_projection_typed,
            reconstructed_manifest=reconstructed_manifest_typed,
            reconstructed_domain_projection=reconstructed_projection_typed,
        )
        expected_continuity = _continuity_verified(
            source_manifest=source_manifest_typed,
            source_domain_projection=source_projection_typed,
            source_safe_file_contents=source_safe_file_contents,
            reconstructed_manifest=reconstructed_manifest_typed,
            reconstructed_domain_projection=reconstructed_projection_typed,
            reconstructed_safe_file_contents=reconstructed_safe_file_contents,
            source_file_order_hash=source_file_order_hash,
            reconstructed_file_order_hash=reconstructed_file_order_hash,
            source_artifact_order_hash=source_artifact_order_hash,
            reconstructed_artifact_order_hash=reconstructed_artifact_order_hash,
        )
        expected_anchor = _anchor_verified(
            anchor_publication=anchor_typed,
            anchored_verification=verification_typed,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        if result.integrity_verified is not expected_integrity:
            errors.append("sealed_replay_status_mismatch")
        if result.continuity_verified is not expected_continuity:
            errors.append("sealed_replay_status_mismatch")
        if result.anchor_verified is not expected_anchor:
            errors.append("sealed_replay_anchor_invalid")
        expected_status = _replay_status(
            integrity_verified=expected_integrity,
            continuity_verified=expected_continuity,
            anchor_verified=expected_anchor,
            evidence_refs=result.evidence_refs,
        )
        if result.replay_status != expected_status:
            errors.append("sealed_replay_status_mismatch")

    rerun_counts = (
        result.semantic_rerun_count,
        result.root_decision_rerun_count,
        result.corridor_rerun_count,
    )
    if (
        any(not _nonnegative_int(item) for item in rerun_counts)
        or rerun_counts != (0, 0, 0)
    ):
        errors.append("sealed_replay_rerun_forbidden")
    external_counts = (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
    )
    if (
        any(not _nonnegative_int(item) for item in external_counts)
        or external_counts != (0, 0, 0)
    ):
        errors.append("sealed_replay_external_call_forbidden")
    _append_zero_count_error(
        errors,
        result.created_authority_count,
        "sealed_replay_authority_creation_forbidden",
    )
    _append_zero_count_error(
        errors,
        result.created_permission_count,
        "sealed_replay_permission_creation_forbidden",
    )
    _append_zero_count_error(
        errors,
        result.action_created_count,
        "sealed_replay_action_creation_forbidden",
    )
    _append_zero_count_error(
        errors,
        result.receipt_created_count,
        "sealed_replay_receipt_creation_forbidden",
    )
    _append_zero_count_error(
        errors,
        result.final_output_created_count,
        "sealed_replay_final_output_creation_forbidden",
    )
    _append_zero_count_error(
        errors,
        result.real_world_effects_count,
        "sealed_replay_effect_forbidden",
    )
    try:
        if result.replay_id != _replay_identity(result):
            errors.append("sealed_replay_identity_mismatch")
    except Exception:
        errors.append("sealed_replay_evidence_invalid")
    return _dedupe(errors)


def _source_context_errors(
    *,
    source_manifest: object,
    source_domain_projection: object,
    source_safe_file_contents: object,
    anchor_publication: object,
    anchored_verification: object,
    supplied_anchor_publication_id: object,
) -> tuple[str, ...]:
    errors: list[str] = []
    projection_valid = (
        type(source_domain_projection) is _DomainEvidenceProjectionV01
        and not _validate_domain_evidence_projection_v01(
            source_domain_projection
        )
    )
    if not projection_valid:
        errors.append("sealed_replay_projection_mismatch")
    manifest_valid = bool(
        projection_valid
        and type(source_manifest) is _SealedPackageManifestV01
        and type(source_safe_file_contents) is tuple
        and not _validate_sealed_package_manifest_v01(
            source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_safe_file_contents,
        )
    )
    if not manifest_valid:
        errors.append("sealed_replay_manifest_binding_mismatch")
    publication_valid = bool(
        manifest_valid
        and type(anchor_publication) is _ExternalAnchorPublicationV01
        and not _validate_external_anchor_publication_v01(
            anchor_publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_safe_file_contents,
        )
    )
    if not publication_valid:
        errors.append("sealed_replay_anchor_invalid")
    verification_valid = bool(
        publication_valid
        and type(anchored_verification) is _AnchoredPackageVerificationV01
        and not _validate_anchored_package_verification_v01(
            anchored_verification,
            anchor_publication=anchor_publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_safe_file_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
    )
    if not verification_valid:
        errors.append("sealed_replay_anchor_invalid")
    return _dedupe(errors)


def _reconstructed_context_errors(
    *,
    reconstructed_manifest: object,
    reconstructed_domain_projection: object,
    reconstructed_safe_file_contents: object,
) -> tuple[str, ...]:
    errors: list[str] = []
    projection_valid = (
        type(reconstructed_domain_projection) is _DomainEvidenceProjectionV01
        and not _validate_domain_evidence_projection_v01(
            reconstructed_domain_projection
        )
    )
    if not projection_valid:
        errors.append("sealed_replay_projection_mismatch")
    manifest_valid = bool(
        projection_valid
        and type(reconstructed_manifest) is _SealedPackageManifestV01
        and type(reconstructed_safe_file_contents) is tuple
        and not _validate_sealed_package_manifest_v01(
            reconstructed_manifest,
            domain_projection=reconstructed_domain_projection,
            safe_file_contents=reconstructed_safe_file_contents,
        )
    )
    if not manifest_valid:
        errors.append("sealed_replay_manifest_binding_mismatch")
    return _dedupe(errors)


def _integrity_verified(
    *,
    source_manifest: _SealedPackageManifestV01,
    source_domain_projection: _DomainEvidenceProjectionV01,
    reconstructed_manifest: _SealedPackageManifestV01,
    reconstructed_domain_projection: _DomainEvidenceProjectionV01,
) -> bool:
    return bool(
        source_domain_projection.status == _PROFILE_STATUS_PASS
        and reconstructed_domain_projection.status == _PROFILE_STATUS_PASS
        and source_manifest.package_status
        == _STATUS_SELF_CONSISTENT_UNANCHORED
        and reconstructed_manifest.package_status
        == _STATUS_SELF_CONSISTENT_UNANCHORED
    )


def _anchor_verified(
    *,
    anchor_publication: _ExternalAnchorPublicationV01,
    anchored_verification: _AnchoredPackageVerificationV01,
    supplied_anchor_publication_id: object,
) -> bool:
    return bool(
        anchor_publication.anchor_status == _STATUS_EVIDENCE_ONLY
        and anchored_verification.verification_status == _STATUS_ANCHORED_PASS
        and anchored_verification.external_anchor_supplied is True
        and anchored_verification.external_anchor_verified is True
        and anchored_verification.manifest_binding_verified is True
        and anchored_verification.package_binding_verified is True
        and supplied_anchor_publication_id
        == anchor_publication.anchor_publication_id
        and anchored_verification.signature_verified is False
        and anchored_verification.signer_identity_verified is False
        and anchored_verification.root_attestation_verified is False
    )


def _continuity_verified(
    *,
    source_manifest: _SealedPackageManifestV01,
    source_domain_projection: _DomainEvidenceProjectionV01,
    source_safe_file_contents: tuple[bytes, ...],
    reconstructed_manifest: _SealedPackageManifestV01,
    reconstructed_domain_projection: _DomainEvidenceProjectionV01,
    reconstructed_safe_file_contents: tuple[bytes, ...],
    source_file_order_hash: str,
    reconstructed_file_order_hash: str,
    source_artifact_order_hash: str,
    reconstructed_artifact_order_hash: str,
) -> bool:
    return bool(
        source_manifest == reconstructed_manifest
        and source_domain_projection == reconstructed_domain_projection
        and source_safe_file_contents == reconstructed_safe_file_contents
        and source_manifest.manifest_id == reconstructed_manifest.manifest_id
        and source_domain_projection.projection_id
        == reconstructed_domain_projection.projection_id
        and source_manifest.package_content_hash
        == reconstructed_manifest.package_content_hash
        and source_manifest.file_count == reconstructed_manifest.file_count
        and source_manifest.artifact_count
        == reconstructed_manifest.artifact_count
        and source_file_order_hash == reconstructed_file_order_hash
        and source_artifact_order_hash == reconstructed_artifact_order_hash
        and source_manifest.domain_id == reconstructed_manifest.domain_id
        and source_manifest.package_id == reconstructed_manifest.package_id
        and source_manifest.logical_package_ref
        == reconstructed_manifest.logical_package_ref
    )


def _replay_status(
    *,
    integrity_verified: bool,
    continuity_verified: bool,
    anchor_verified: bool,
    evidence_refs: object,
) -> str:
    if (
        integrity_verified is True
        and continuity_verified is True
        and anchor_verified is True
        and _evidence_refs_valid(evidence_refs)
    ):
        return STATUS_PASS
    return STATUS_FAIL_CLOSED


def _file_order_hash(manifest: _SealedPackageManifestV01) -> str:
    entries = [
        {
            "position": position,
            "logical_path": item.logical_path,
            "file_record_id": item.file_record_id,
            "content_sha256": item.content_sha256,
        }
        for position, item in enumerate(manifest.safe_file_records)
    ]
    return _identity_hash(_FILE_ORDER_DOMAIN, entries)


def _artifact_order_hash(manifest: _SealedPackageManifestV01) -> str:
    entries = [
        {
            "position": position,
            "artifact_record_id": artifact_record_id,
        }
        for position, artifact_record_id in enumerate(manifest.artifact_record_ids)
    ]
    return _identity_hash(_ARTIFACT_ORDER_DOMAIN, entries)


def _replay_identity(result: SealedReplayEvidenceV01) -> str:
    return _identity_hash(
        _REPLAY_IDENTITY_DOMAIN,
        _replay_plain(result, include_id=False),
    )


def _replay_plain(
    result: SealedReplayEvidenceV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["replay_id"] = result.replay_id
    projected.update(
        {
            "replay_version": result.replay_version,
            "source_manifest_id": result.source_manifest_id,
            "reconstructed_manifest_id": result.reconstructed_manifest_id,
            "anchor_publication_id": result.anchor_publication_id,
            "anchored_verification_id": result.anchored_verification_id,
            "source_domain_projection_id": result.source_domain_projection_id,
            "reconstructed_domain_projection_id": (
                result.reconstructed_domain_projection_id
            ),
            "domain_id": result.domain_id,
            "package_id": result.package_id,
            "logical_package_ref": result.logical_package_ref,
            "source_package_content_hash": result.source_package_content_hash,
            "reconstructed_package_content_hash": (
                result.reconstructed_package_content_hash
            ),
            "source_file_count": result.source_file_count,
            "reconstructed_file_count": result.reconstructed_file_count,
            "source_artifact_count": result.source_artifact_count,
            "reconstructed_artifact_count": result.reconstructed_artifact_count,
            "source_file_order_hash": result.source_file_order_hash,
            "reconstructed_file_order_hash": result.reconstructed_file_order_hash,
            "source_artifact_order_hash": result.source_artifact_order_hash,
            "reconstructed_artifact_order_hash": (
                result.reconstructed_artifact_order_hash
            ),
            "integrity_verified": result.integrity_verified,
            "continuity_verified": result.continuity_verified,
            "anchor_verified": result.anchor_verified,
            "semantic_rerun_count": result.semantic_rerun_count,
            "root_decision_rerun_count": result.root_decision_rerun_count,
            "corridor_rerun_count": result.corridor_rerun_count,
            "provider_call_count": result.provider_call_count,
            "network_call_count": result.network_call_count,
            "gemini_call_count": result.gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "action_created_count": result.action_created_count,
            "receipt_created_count": result.receipt_created_count,
            "final_output_created_count": result.final_output_created_count,
            "real_world_effects_count": result.real_world_effects_count,
            "evidence_refs": list(result.evidence_refs),
            "replay_status": result.replay_status,
        }
    )
    return projected


def _replace_replay_id(
    result: SealedReplayEvidenceV01,
    replay_id: str,
) -> SealedReplayEvidenceV01:
    values = {field: getattr(result, field) for field in result.__slots__}
    values["replay_id"] = replay_id
    return SealedReplayEvidenceV01(**values)


def _evidence_refs_valid(value: object) -> bool:
    if type(value) is not tuple or not value:
        return False
    if any(not _logical_ref_valid(item) for item in value):
        return False
    return len(set(value)) == len(value)


def _logical_ref_valid(value: object) -> bool:
    if not _valid_text(value) or type(value) is not str:
        return False
    if (
        value.startswith("/")
        or "\\" in value
        or _WINDOWS_DRIVE.match(value) is not None
        or _unicodedata.normalize("NFC", value) != value
    ):
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value or value != value.strip():
        return False
    if any(
        0xD800 <= ord(character) <= 0xDFFF
        or _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        for character in value
    ):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return True


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _append_zero_count_error(
    errors: list[str],
    value: object,
    reason: str,
) -> None:
    if not _nonnegative_int(value) or value != 0:
        errors.append(reason)


def _identity_hash(domain: str, semantic_fields: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(semantic_fields),
    )


def _dedupe(errors: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(errors))


def _stable_replay_reason(error: ValueError) -> str:
    allowed = (
        "sealed_replay_evidence_invalid",
        "sealed_replay_identity_mismatch",
        "sealed_replay_anchor_invalid",
        "sealed_replay_manifest_binding_mismatch",
        "sealed_replay_projection_mismatch",
        "sealed_replay_file_geometry_invalid",
        "sealed_replay_artifact_geometry_invalid",
        "sealed_replay_hash_mismatch",
        "sealed_replay_reference_invalid",
        "sealed_replay_rerun_forbidden",
        "sealed_replay_external_call_forbidden",
        "sealed_replay_authority_creation_forbidden",
        "sealed_replay_permission_creation_forbidden",
        "sealed_replay_action_creation_forbidden",
        "sealed_replay_receipt_creation_forbidden",
        "sealed_replay_final_output_creation_forbidden",
        "sealed_replay_effect_forbidden",
        "sealed_replay_status_mismatch",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "sealed_replay_evidence_invalid"
