"""Domain-neutral Anchor publication and anchored verification contracts only.

This module performs no filesystem or Git operation, predicts no future
commit, writes or discovers no package, and performs no Replay, provider,
network, Gemini, clock, randomness, signature, signer authentication, Root
Attestation, or PKI operation. It creates no authority, permission, or effect
and makes no production-certification claim. Hashes establish declared
integrity, not semantic truth. EVIDENCE_ONLY publication is not ANCHORED_PASS.
ANCHORED_PASS is derived only from an independently supplied matching Anchor;
status is derived and never caller supplied.
publication_base_head is explicit committed-base metadata independent of the
live attempt execution_head; external Git provenance belongs to the later
filesystem runner and audit.
"""

from dataclasses import dataclass as _dataclass
import re as _re
import unicodedata as _unicodedata

from hedgehog.evidence.sealed_evidence_profile_v01 import (
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


MODULE_ID = "external_anchor_v01"
ANCHOR_VERSION = "v0.1"
VERIFICATION_VERSION = "v0.1"

STATUS_EVIDENCE_ONLY = "EVIDENCE_ONLY"
STATUS_ANCHORED_PASS = "ANCHORED_PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

ANCHOR_PUBLICATION_STATUSES = (
    STATUS_EVIDENCE_ONLY,
    STATUS_FAIL_CLOSED,
)
ANCHORED_VERIFICATION_STATUSES = (
    STATUS_ANCHORED_PASS,
    STATUS_FAIL_CLOSED,
)

_EXTERNAL_ANCHOR_PUBLICATION_DOMAIN = (
    "hedgehog.evidence.external_anchor_publication.v01"
)
_ANCHORED_PACKAGE_VERIFICATION_DOMAIN = (
    "hedgehog.evidence.anchored_package_verification.v01"
)
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_EXECUTION_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:")


@_dataclass(frozen=True, slots=True)
class ExternalAnchorPublicationV01:
    anchor_publication_id: str
    anchor_version: str
    manifest_id: str
    domain_projection_id: str
    programme_identity_id: str
    domain_execution_identity_id: str
    attempt_identity_id: str
    domain_id: str
    package_id: str
    logical_package_ref: str
    package_content_hash: str
    kernel_manifest_hash: str
    publication_base_head: str
    external_anchor_supplied_at_publication: bool
    external_anchor_verified_at_publication: bool
    anchored_pass_claimed: bool
    publication_provider_call_count: int
    publication_network_call_count: int
    publication_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int
    anchor_status: str


@_dataclass(frozen=True, slots=True)
class AnchoredPackageVerificationV01:
    anchored_verification_id: str
    verification_version: str
    anchor_publication_id: str
    manifest_id: str
    domain_projection_id: str
    programme_identity_id: str
    domain_execution_identity_id: str
    attempt_identity_id: str
    domain_id: str
    package_id: str
    logical_package_ref: str
    package_content_hash: str
    kernel_manifest_hash: str
    publication_base_head: str
    supplied_anchor_publication_id: str
    external_anchor_supplied: bool
    external_anchor_verified: bool
    manifest_binding_verified: bool
    package_binding_verified: bool
    signature_verified: bool
    signer_identity_verified: bool
    root_attestation_verified: bool
    verification_provider_call_count: int
    verification_network_call_count: int
    verification_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int
    verification_status: str


def build_external_anchor_publication_v01(
    *,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
    publication_base_head: str,
) -> ExternalAnchorPublicationV01:
    try:
        if not _anchor_context_valid(
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        ):
            raise ValueError("external_anchor_publication_invalid")
        if not _valid_execution_head(publication_base_head):
            raise ValueError("external_anchor_publication_invalid")
        provisional = ExternalAnchorPublicationV01(
            anchor_publication_id="0" * 64,
            anchor_version=ANCHOR_VERSION,
            manifest_id=manifest.manifest_id,
            domain_projection_id=manifest.domain_projection_id,
            programme_identity_id=manifest.programme_identity_id,
            domain_execution_identity_id=manifest.domain_execution_identity_id,
            attempt_identity_id=manifest.attempt_identity_id,
            domain_id=manifest.domain_id,
            package_id=manifest.package_id,
            logical_package_ref=manifest.logical_package_ref,
            package_content_hash=manifest.package_content_hash,
            kernel_manifest_hash=manifest.kernel_manifest_hash,
            publication_base_head=publication_base_head,
            external_anchor_supplied_at_publication=False,
            external_anchor_verified_at_publication=False,
            anchored_pass_claimed=False,
            publication_provider_call_count=0,
            publication_network_call_count=0,
            publication_gemini_call_count=0,
            created_authority_count=0,
            created_permission_count=0,
            real_world_effects_count=0,
            anchor_status=_publication_status(manifest),
        )
        result = _replace_publication_id(
            provisional,
            _publication_identity(provisional),
        )
        errors = _publication_errors(
            result,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        )
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_publication_reason(error)) from None
    except Exception:
        raise ValueError("external_anchor_unexpected_exception") from None


def validate_external_anchor_publication_v01(
    result: object,
    *,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
) -> tuple[str, ...]:
    try:
        return _publication_errors(
            result,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        )
    except Exception:
        return ("external_anchor_unexpected_exception",)


def external_anchor_publication_to_plain_dict_v01(
    result: ExternalAnchorPublicationV01,
    *,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
) -> dict[str, object]:
    try:
        if _publication_errors(
            result,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        ):
            raise ValueError
        projected = _publication_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("external_anchor_publication_invalid") from None


def build_anchored_package_verification_v01(
    *,
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
    supplied_anchor_publication_id: str,
) -> AnchoredPackageVerificationV01:
    try:
        if not _valid_sha256(supplied_anchor_publication_id):
            raise ValueError("anchored_package_verification_invalid")
        if _publication_errors(
            anchor_publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        ):
            raise ValueError("anchored_package_verification_invalid")
        expected_publication_id = _publication_identity(anchor_publication)
        manifest_binding = _manifest_binding_matches(anchor_publication, manifest)
        package_binding = _package_binding_matches(anchor_publication, manifest)
        external_verified = (
            supplied_anchor_publication_id == expected_publication_id
        )
        verification_status = _verification_status(
            anchor_publication=anchor_publication,
            manifest=manifest,
            external_anchor_verified=external_verified,
            manifest_binding_verified=manifest_binding,
            package_binding_verified=package_binding,
        )
        provisional = AnchoredPackageVerificationV01(
            anchored_verification_id="0" * 64,
            verification_version=VERIFICATION_VERSION,
            anchor_publication_id=anchor_publication.anchor_publication_id,
            manifest_id=manifest.manifest_id,
            domain_projection_id=manifest.domain_projection_id,
            programme_identity_id=manifest.programme_identity_id,
            domain_execution_identity_id=manifest.domain_execution_identity_id,
            attempt_identity_id=manifest.attempt_identity_id,
            domain_id=manifest.domain_id,
            package_id=manifest.package_id,
            logical_package_ref=manifest.logical_package_ref,
            package_content_hash=manifest.package_content_hash,
            kernel_manifest_hash=manifest.kernel_manifest_hash,
            publication_base_head=anchor_publication.publication_base_head,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            external_anchor_supplied=True,
            external_anchor_verified=external_verified,
            manifest_binding_verified=manifest_binding,
            package_binding_verified=package_binding,
            signature_verified=False,
            signer_identity_verified=False,
            root_attestation_verified=False,
            verification_provider_call_count=0,
            verification_network_call_count=0,
            verification_gemini_call_count=0,
            created_authority_count=0,
            created_permission_count=0,
            real_world_effects_count=0,
            verification_status=verification_status,
        )
        result = _replace_verification_id(
            provisional,
            _verification_identity(provisional),
        )
        errors = _verification_errors(
            result,
            anchor_publication=anchor_publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_verification_reason(error)) from None
    except Exception:
        raise ValueError("external_anchor_unexpected_exception") from None


def validate_anchored_package_verification_v01(
    result: object,
    *,
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
    supplied_anchor_publication_id: str,
) -> tuple[str, ...]:
    try:
        return _verification_errors(
            result,
            anchor_publication=anchor_publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
    except Exception:
        return ("external_anchor_unexpected_exception",)


def anchored_package_verification_to_plain_dict_v01(
    result: AnchoredPackageVerificationV01,
    *,
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
    supplied_anchor_publication_id: str,
) -> dict[str, object]:
    try:
        if _verification_errors(
            result,
            anchor_publication=anchor_publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        ):
            raise ValueError
        projected = _verification_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("anchored_package_verification_invalid") from None


def _publication_errors(
    result: object,
    *,
    manifest: object,
    domain_projection: object,
    safe_file_contents: object,
) -> tuple[str, ...]:
    if type(result) is not ExternalAnchorPublicationV01:
        return ("external_anchor_publication_invalid",)
    errors: list[str] = []
    context_valid = _anchor_context_valid(
        manifest=manifest,
        domain_projection=domain_projection,
        safe_file_contents=safe_file_contents,
    )
    if not context_valid:
        errors.append("external_anchor_publication_invalid")

    identity_values = (
        result.anchor_publication_id,
        result.manifest_id,
        result.domain_projection_id,
        result.programme_identity_id,
        result.domain_execution_identity_id,
        result.attempt_identity_id,
        result.package_content_hash,
        result.kernel_manifest_hash,
    )
    bool_values = (
        result.external_anchor_supplied_at_publication,
        result.external_anchor_verified_at_publication,
        result.anchored_pass_claimed,
    )
    count_values = (
        result.publication_provider_call_count,
        result.publication_network_call_count,
        result.publication_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.real_world_effects_count,
    )
    if (
        result.anchor_version != ANCHOR_VERSION
        or any(not _valid_sha256(item) for item in identity_values)
        or not _valid_text(result.domain_id)
        or not _valid_text(result.package_id)
        or not _logical_ref_valid(result.logical_package_ref)
        or not _valid_execution_head(result.publication_base_head)
        or any(type(item) is not bool for item in bool_values)
        or any(not _nonnegative_int(item) for item in count_values)
        or type(result.anchor_status) is not str
        or result.anchor_status not in ANCHOR_PUBLICATION_STATUSES
    ):
        errors.append("external_anchor_publication_invalid")

    if context_valid:
        expected_bindings = (
            manifest.manifest_id,
            manifest.domain_projection_id,
            manifest.programme_identity_id,
            manifest.domain_execution_identity_id,
            manifest.attempt_identity_id,
            manifest.domain_id,
            manifest.package_id,
            manifest.logical_package_ref,
            manifest.package_content_hash,
            manifest.kernel_manifest_hash,
        )
        stored_bindings = (
            result.manifest_id,
            result.domain_projection_id,
            result.programme_identity_id,
            result.domain_execution_identity_id,
            result.attempt_identity_id,
            result.domain_id,
            result.package_id,
            result.logical_package_ref,
            result.package_content_hash,
            result.kernel_manifest_hash,
        )
        if stored_bindings != expected_bindings:
            errors.append("external_anchor_binding_mismatch")
        expected_status = _publication_status(manifest)
        if result.anchor_status != expected_status:
            errors.append("external_anchor_status_mismatch")

    if bool_values != (False, False, False):
        errors.append("external_anchor_binding_mismatch")
    external_counts = (
        result.publication_provider_call_count,
        result.publication_network_call_count,
        result.publication_gemini_call_count,
    )
    if (
        any(not _nonnegative_int(item) for item in external_counts)
        or external_counts != (0, 0, 0)
    ):
        errors.append("external_anchor_external_call_forbidden")
    if (
        not _nonnegative_int(result.created_authority_count)
        or result.created_authority_count != 0
    ):
        errors.append("external_anchor_authority_creation_forbidden")
    if (
        not _nonnegative_int(result.created_permission_count)
        or result.created_permission_count != 0
    ):
        errors.append("external_anchor_permission_creation_forbidden")
    if (
        not _nonnegative_int(result.real_world_effects_count)
        or result.real_world_effects_count != 0
    ):
        errors.append("external_anchor_effect_forbidden")
    try:
        expected_id = _publication_identity(result)
        if result.anchor_publication_id != expected_id:
            errors.append("external_anchor_identity_mismatch")
    except Exception:
        errors.append("external_anchor_publication_invalid")
    return _dedupe(errors)


def _verification_errors(
    result: object,
    *,
    anchor_publication: object,
    manifest: object,
    domain_projection: object,
    safe_file_contents: object,
    supplied_anchor_publication_id: object,
) -> tuple[str, ...]:
    if type(result) is not AnchoredPackageVerificationV01:
        return ("anchored_package_verification_invalid",)
    errors: list[str] = []
    supplied_valid = _valid_sha256(supplied_anchor_publication_id)
    publication_valid = (
        type(anchor_publication) is ExternalAnchorPublicationV01
        and not _publication_errors(
            anchor_publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        )
    )
    if not supplied_valid or not publication_valid:
        errors.append("anchored_package_verification_invalid")

    identity_values = (
        result.anchored_verification_id,
        result.anchor_publication_id,
        result.manifest_id,
        result.domain_projection_id,
        result.programme_identity_id,
        result.domain_execution_identity_id,
        result.attempt_identity_id,
        result.package_content_hash,
        result.kernel_manifest_hash,
        result.supplied_anchor_publication_id,
    )
    bool_values = (
        result.external_anchor_supplied,
        result.external_anchor_verified,
        result.manifest_binding_verified,
        result.package_binding_verified,
        result.signature_verified,
        result.signer_identity_verified,
        result.root_attestation_verified,
    )
    count_values = (
        result.verification_provider_call_count,
        result.verification_network_call_count,
        result.verification_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.real_world_effects_count,
    )
    if (
        result.verification_version != VERIFICATION_VERSION
        or any(not _valid_sha256(item) for item in identity_values)
        or not _valid_text(result.domain_id)
        or not _valid_text(result.package_id)
        or not _logical_ref_valid(result.logical_package_ref)
        or not _valid_execution_head(result.publication_base_head)
        or any(type(item) is not bool for item in bool_values)
        or any(not _nonnegative_int(item) for item in count_values)
        or type(result.verification_status) is not str
        or result.verification_status not in ANCHORED_VERIFICATION_STATUSES
    ):
        errors.append("anchored_package_verification_invalid")

    if supplied_valid and result.supplied_anchor_publication_id != supplied_anchor_publication_id:
        errors.append("external_anchor_supplied_mismatch")

    if publication_valid:
        expected_bindings = (
            anchor_publication.anchor_publication_id,
            manifest.manifest_id,
            manifest.domain_projection_id,
            manifest.programme_identity_id,
            manifest.domain_execution_identity_id,
            manifest.attempt_identity_id,
            manifest.domain_id,
            manifest.package_id,
            manifest.logical_package_ref,
            manifest.package_content_hash,
            manifest.kernel_manifest_hash,
            anchor_publication.publication_base_head,
        )
        stored_bindings = (
            result.anchor_publication_id,
            result.manifest_id,
            result.domain_projection_id,
            result.programme_identity_id,
            result.domain_execution_identity_id,
            result.attempt_identity_id,
            result.domain_id,
            result.package_id,
            result.logical_package_ref,
            result.package_content_hash,
            result.kernel_manifest_hash,
            result.publication_base_head,
        )
        if stored_bindings != expected_bindings:
            errors.append("external_anchor_binding_mismatch")

        expected_publication_id = _publication_identity(anchor_publication)
        expected_manifest_binding = _manifest_binding_matches(
            anchor_publication,
            manifest,
        )
        expected_package_binding = _package_binding_matches(
            anchor_publication,
            manifest,
        )
        expected_external_verified = (
            supplied_valid
            and supplied_anchor_publication_id == expected_publication_id
        )
        expected_bools = (
            True,
            expected_external_verified,
            expected_manifest_binding,
            expected_package_binding,
            False,
            False,
            False,
        )
        if bool_values != expected_bools:
            errors.append("external_anchor_binding_mismatch")
        expected_status = _verification_status(
            anchor_publication=anchor_publication,
            manifest=manifest,
            external_anchor_verified=expected_external_verified,
            manifest_binding_verified=expected_manifest_binding,
            package_binding_verified=expected_package_binding,
        )
        if result.verification_status != expected_status:
            errors.append("external_anchor_status_mismatch")

    if result.signature_verified is not False:
        errors.append("external_anchor_signature_claim_forbidden")
    if result.signer_identity_verified is not False:
        errors.append("external_anchor_signer_identity_claim_forbidden")
    if result.root_attestation_verified is not False:
        errors.append("external_anchor_root_attestation_claim_forbidden")

    external_counts = (
        result.verification_provider_call_count,
        result.verification_network_call_count,
        result.verification_gemini_call_count,
    )
    if (
        any(not _nonnegative_int(item) for item in external_counts)
        or external_counts != (0, 0, 0)
    ):
        errors.append("external_anchor_external_call_forbidden")
    if (
        not _nonnegative_int(result.created_authority_count)
        or result.created_authority_count != 0
    ):
        errors.append("external_anchor_authority_creation_forbidden")
    if (
        not _nonnegative_int(result.created_permission_count)
        or result.created_permission_count != 0
    ):
        errors.append("external_anchor_permission_creation_forbidden")
    if (
        not _nonnegative_int(result.real_world_effects_count)
        or result.real_world_effects_count != 0
    ):
        errors.append("external_anchor_effect_forbidden")
    try:
        expected_id = _verification_identity(result)
        if result.anchored_verification_id != expected_id:
            errors.append("external_anchor_identity_mismatch")
    except Exception:
        errors.append("anchored_package_verification_invalid")
    return _dedupe(errors)


def _anchor_context_valid(
    *,
    manifest: object,
    domain_projection: object,
    safe_file_contents: object,
) -> bool:
    return bool(
        type(manifest) is _SealedPackageManifestV01
        and type(domain_projection) is _DomainEvidenceProjectionV01
        and type(safe_file_contents) is tuple
        and not _validate_domain_evidence_projection_v01(domain_projection)
        and not _validate_sealed_package_manifest_v01(
            manifest,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        )
    )


def _publication_status(manifest: _SealedPackageManifestV01) -> str:
    if manifest.package_status == _STATUS_SELF_CONSISTENT_UNANCHORED:
        return STATUS_EVIDENCE_ONLY
    if manifest.package_status == _PACKAGE_STATUS_FAIL_CLOSED:
        return STATUS_FAIL_CLOSED
    raise ValueError("external_anchor_publication_invalid")


def _verification_status(
    *,
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
    external_anchor_verified: bool,
    manifest_binding_verified: bool,
    package_binding_verified: bool,
) -> str:
    if (
        manifest.package_status == _STATUS_SELF_CONSISTENT_UNANCHORED
        and anchor_publication.anchor_status == STATUS_EVIDENCE_ONLY
        and external_anchor_verified
        and manifest_binding_verified
        and package_binding_verified
    ):
        return STATUS_ANCHORED_PASS
    return STATUS_FAIL_CLOSED


def _manifest_binding_matches(
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
) -> bool:
    return (
        anchor_publication.manifest_id,
        anchor_publication.domain_projection_id,
        anchor_publication.programme_identity_id,
        anchor_publication.domain_execution_identity_id,
        anchor_publication.attempt_identity_id,
        anchor_publication.domain_id,
    ) == (
        manifest.manifest_id,
        manifest.domain_projection_id,
        manifest.programme_identity_id,
        manifest.domain_execution_identity_id,
        manifest.attempt_identity_id,
        manifest.domain_id,
    )


def _package_binding_matches(
    anchor_publication: ExternalAnchorPublicationV01,
    manifest: _SealedPackageManifestV01,
) -> bool:
    return (
        anchor_publication.package_id,
        anchor_publication.logical_package_ref,
        anchor_publication.package_content_hash,
        anchor_publication.kernel_manifest_hash,
    ) == (
        manifest.package_id,
        manifest.logical_package_ref,
        manifest.package_content_hash,
        manifest.kernel_manifest_hash,
    )


def _publication_plain(
    result: ExternalAnchorPublicationV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["anchor_publication_id"] = result.anchor_publication_id
    projected.update(
        {
            "anchor_version": result.anchor_version,
            "manifest_id": result.manifest_id,
            "domain_projection_id": result.domain_projection_id,
            "programme_identity_id": result.programme_identity_id,
            "domain_execution_identity_id": result.domain_execution_identity_id,
            "attempt_identity_id": result.attempt_identity_id,
            "domain_id": result.domain_id,
            "package_id": result.package_id,
            "logical_package_ref": result.logical_package_ref,
            "package_content_hash": result.package_content_hash,
            "kernel_manifest_hash": result.kernel_manifest_hash,
            "publication_base_head": result.publication_base_head,
            "external_anchor_supplied_at_publication": (
                result.external_anchor_supplied_at_publication
            ),
            "external_anchor_verified_at_publication": (
                result.external_anchor_verified_at_publication
            ),
            "anchored_pass_claimed": result.anchored_pass_claimed,
            "publication_provider_call_count": result.publication_provider_call_count,
            "publication_network_call_count": result.publication_network_call_count,
            "publication_gemini_call_count": result.publication_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "real_world_effects_count": result.real_world_effects_count,
            "anchor_status": result.anchor_status,
        }
    )
    return projected


def _verification_plain(
    result: AnchoredPackageVerificationV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["anchored_verification_id"] = result.anchored_verification_id
    projected.update(
        {
            "verification_version": result.verification_version,
            "anchor_publication_id": result.anchor_publication_id,
            "manifest_id": result.manifest_id,
            "domain_projection_id": result.domain_projection_id,
            "programme_identity_id": result.programme_identity_id,
            "domain_execution_identity_id": result.domain_execution_identity_id,
            "attempt_identity_id": result.attempt_identity_id,
            "domain_id": result.domain_id,
            "package_id": result.package_id,
            "logical_package_ref": result.logical_package_ref,
            "package_content_hash": result.package_content_hash,
            "kernel_manifest_hash": result.kernel_manifest_hash,
            "publication_base_head": result.publication_base_head,
            "supplied_anchor_publication_id": result.supplied_anchor_publication_id,
            "external_anchor_supplied": result.external_anchor_supplied,
            "external_anchor_verified": result.external_anchor_verified,
            "manifest_binding_verified": result.manifest_binding_verified,
            "package_binding_verified": result.package_binding_verified,
            "signature_verified": result.signature_verified,
            "signer_identity_verified": result.signer_identity_verified,
            "root_attestation_verified": result.root_attestation_verified,
            "verification_provider_call_count": (
                result.verification_provider_call_count
            ),
            "verification_network_call_count": result.verification_network_call_count,
            "verification_gemini_call_count": result.verification_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "real_world_effects_count": result.real_world_effects_count,
            "verification_status": result.verification_status,
        }
    )
    return projected


def _publication_identity(result: ExternalAnchorPublicationV01) -> str:
    return _identity_hash(
        _EXTERNAL_ANCHOR_PUBLICATION_DOMAIN,
        _publication_plain(result, include_id=False),
    )


def _verification_identity(result: AnchoredPackageVerificationV01) -> str:
    return _identity_hash(
        _ANCHORED_PACKAGE_VERIFICATION_DOMAIN,
        _verification_plain(result, include_id=False),
    )


def _replace_publication_id(
    result: ExternalAnchorPublicationV01,
    anchor_publication_id: str,
) -> ExternalAnchorPublicationV01:
    values = {field: getattr(result, field) for field in result.__slots__}
    values["anchor_publication_id"] = anchor_publication_id
    return ExternalAnchorPublicationV01(**values)


def _replace_verification_id(
    result: AnchoredPackageVerificationV01,
    anchored_verification_id: str,
) -> AnchoredPackageVerificationV01:
    values = {field: getattr(result, field) for field in result.__slots__}
    values["anchored_verification_id"] = anchored_verification_id
    return AnchoredPackageVerificationV01(**values)


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
    parts = value.split("/")
    return all(item not in ("", ".", "..") for item in parts)


def _valid_execution_head(value: object) -> bool:
    return type(value) is str and _EXECUTION_HEAD.fullmatch(value) is not None


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _identity_hash(domain: str, semantic_fields: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(semantic_fields),
    )


def _dedupe(errors: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(errors))


def _stable_publication_reason(error: ValueError) -> str:
    allowed = (
        "external_anchor_publication_invalid",
        "external_anchor_identity_mismatch",
        "external_anchor_binding_mismatch",
        "external_anchor_status_mismatch",
        "external_anchor_external_call_forbidden",
        "external_anchor_authority_creation_forbidden",
        "external_anchor_permission_creation_forbidden",
        "external_anchor_effect_forbidden",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "external_anchor_publication_invalid"


def _stable_verification_reason(error: ValueError) -> str:
    allowed = (
        "anchored_package_verification_invalid",
        "external_anchor_identity_mismatch",
        "external_anchor_binding_mismatch",
        "external_anchor_supplied_mismatch",
        "external_anchor_status_mismatch",
        "external_anchor_external_call_forbidden",
        "external_anchor_signature_claim_forbidden",
        "external_anchor_signer_identity_claim_forbidden",
        "external_anchor_root_attestation_claim_forbidden",
        "external_anchor_authority_creation_forbidden",
        "external_anchor_permission_creation_forbidden",
        "external_anchor_effect_forbidden",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "anchored_package_verification_invalid"
