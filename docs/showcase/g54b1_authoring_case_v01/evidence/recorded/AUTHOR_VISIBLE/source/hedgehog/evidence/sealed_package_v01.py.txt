"""Domain-neutral safe-file and package-Manifest contracts only.

This module performs no filesystem access, directory creation, archive or
package writing, package discovery, Anchor, anchored verification, Replay,
provider, network, Gemini, clock, or randomness operation. It creates no
authority, permission, or effect and makes no production-certification claim.
Hashes establish declared integrity, not semantic truth.
SELF_CONSISTENT_UNANCHORED is not anchored PASS. Status is derived, never
caller supplied. The Manifest file never hashes or counts itself.
"""

from dataclasses import dataclass as _dataclass
import hashlib as _hashlib
import re as _re
import unicodedata as _unicodedata

from hedgehog.evidence.sealed_evidence_profile_v01 import (
    DomainEvidenceProjectionV01 as _DomainEvidenceProjectionV01,
    EvidenceArtifactRecordV01 as _EvidenceArtifactRecordV01,
    REPOSITORY_ALLOWED_EVIDENCE_CLASSES as _REPOSITORY_ALLOWED_EVIDENCE_CLASSES,
    STATUS_FAIL_CLOSED as _PROFILE_STATUS_FAIL_CLOSED,
    STATUS_PASS as _PROFILE_STATUS_PASS,
    SafeSourceRecordV01 as _SafeSourceRecordV01,
    validate_domain_evidence_projection_v01 as _validate_domain_evidence_projection_v01,
    validate_safe_source_record_v01 as _validate_safe_source_record_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "sealed_package_v01"
PACKAGE_VERSION = "v0.1"
MANIFEST_FILENAME = "sealed_package_manifest_v01.json"

STATUS_SELF_CONSISTENT_UNANCHORED = "SELF_CONSISTENT_UNANCHORED"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
PACKAGE_STATUSES = (
    STATUS_SELF_CONSISTENT_UNANCHORED,
    STATUS_FAIL_CLOSED,
)

_SAFE_FILE_RECORD_DOMAIN = "hedgehog.evidence.safe_file_record.v01"
_PACKAGE_CONTENT_DOMAIN = "hedgehog.evidence.package_content.v01"
_SEALED_PACKAGE_MANIFEST_DOMAIN = (
    "hedgehog.evidence.sealed_package_manifest.v01"
)
_RAW_PRIVATE_EVIDENCE_CLASS = "LIVE_PROVIDER_RAW_PRIVATE"
_CRYPTOGRAPHIC_INTEGRITY_CLASS = "CRYPTOGRAPHIC_INTEGRITY"
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:")
_MEDIA_TYPE = _re.compile(r"^[a-z0-9.+-]+/[a-z0-9.+-]+$")


@_dataclass(frozen=True, slots=True)
class SafeFileRecordV01:
    file_record_id: str
    logical_path: str
    media_type: str
    byte_count: int
    content_sha256: str
    evidence_class: str
    source_record_ids: tuple[str, ...]
    terminal_newline_required: bool
    secret_scan_passed: bool

    def __post_init__(self) -> None:
        if type(self.source_record_ids) is not tuple:
            raise ValueError("safe_file_record_invalid")


@_dataclass(frozen=True, slots=True)
class SealedPackageManifestV01:
    manifest_id: str
    manifest_version: str
    domain_projection_id: str
    programme_identity_id: str
    domain_execution_identity_id: str
    attempt_identity_id: str
    domain_id: str
    package_id: str
    logical_package_ref: str
    safe_file_records: tuple[SafeFileRecordV01, ...]
    artifact_record_ids: tuple[str, ...]
    kernel_manifest_hash: str
    file_count: int
    artifact_count: int
    package_content_hash: str
    packaging_provider_call_count: int
    packaging_network_call_count: int
    packaging_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int
    package_status: str

    def __post_init__(self) -> None:
        if (
            type(self.safe_file_records) is not tuple
            or type(self.artifact_record_ids) is not tuple
        ):
            raise ValueError("sealed_package_manifest_invalid")


def build_safe_file_record_v01(
    *,
    logical_path: str,
    media_type: str,
    content_bytes: bytes,
    evidence_class: str,
    source_record_ids: tuple[str, ...],
    terminal_newline_required: bool,
    secret_scan_passed: bool,
) -> SafeFileRecordV01:
    try:
        if type(content_bytes) is not bytes or not content_bytes:
            raise ValueError("safe_file_record_invalid")
        if type(source_record_ids) is not tuple:
            raise ValueError("safe_file_record_invalid")
        copied_source_ids = tuple(item for item in source_record_ids)
        content_sha256 = _hashlib.sha256(content_bytes).hexdigest()
        provisional = SafeFileRecordV01(
            file_record_id="0" * 64,
            logical_path=logical_path,
            media_type=media_type,
            byte_count=len(content_bytes),
            content_sha256=content_sha256,
            evidence_class=evidence_class,
            source_record_ids=copied_source_ids,
            terminal_newline_required=terminal_newline_required,
            secret_scan_passed=secret_scan_passed,
        )
        result = _replace_file_record_id(
            provisional,
            _safe_file_identity(provisional),
        )
        errors = _safe_file_errors(result, content_bytes=content_bytes)
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_safe_file_reason(error)) from None
    except Exception:
        raise ValueError("sealed_package_unexpected_exception") from None


def validate_safe_file_record_v01(
    result: object,
    *,
    content_bytes: bytes,
) -> tuple[str, ...]:
    try:
        return _safe_file_errors(result, content_bytes=content_bytes)
    except Exception:
        return ("sealed_package_unexpected_exception",)


def safe_file_record_to_plain_dict_v01(
    result: SafeFileRecordV01,
    *,
    content_bytes: bytes,
) -> dict[str, object]:
    try:
        if _safe_file_errors(result, content_bytes=content_bytes):
            raise ValueError
        projected = _safe_file_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("safe_file_record_invalid") from None


def build_sealed_package_manifest_v01(
    *,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_records: tuple[SafeFileRecordV01, ...],
    safe_file_contents: tuple[bytes, ...],
    kernel_manifest_hash: str,
) -> SealedPackageManifestV01:
    try:
        if (
            type(domain_projection) is not _DomainEvidenceProjectionV01
            or _validate_domain_evidence_projection_v01(domain_projection)
        ):
            raise ValueError("sealed_package_manifest_invalid")
        if (
            type(safe_file_records) is not tuple
            or not safe_file_records
            or any(type(item) is not SafeFileRecordV01 for item in safe_file_records)
            or type(safe_file_contents) is not tuple
            or len(safe_file_records) != len(safe_file_contents)
            or any(type(item) is not bytes for item in safe_file_contents)
        ):
            raise ValueError("sealed_package_manifest_invalid")
        copied_files = tuple(item for item in safe_file_records)
        copied_contents = tuple(item for item in safe_file_contents)
        for item, content in zip(copied_files, copied_contents, strict=True):
            file_errors = _safe_file_errors(item, content_bytes=content)
            if file_errors:
                raise ValueError(file_errors[0])
        if not _valid_sha256(kernel_manifest_hash):
            raise ValueError("sealed_package_manifest_invalid")

        projection_programme = domain_projection.programme_identity
        projection_domain = domain_projection.domain_execution_identity
        projection_attempt = domain_projection.attempt_identity
        artifact_record_ids = tuple(
            item.artifact_record_id for item in domain_projection.artifact_records
        )
        package_status = _status_for_projection(domain_projection)
        provisional = SealedPackageManifestV01(
            manifest_id="0" * 64,
            manifest_version=PACKAGE_VERSION,
            domain_projection_id=domain_projection.projection_id,
            programme_identity_id=projection_programme.programme_identity_id,
            domain_execution_identity_id=(
                projection_domain.domain_execution_identity_id
            ),
            attempt_identity_id=projection_attempt.attempt_identity_id,
            domain_id=projection_domain.domain_id,
            package_id=projection_attempt.package_id,
            logical_package_ref=projection_attempt.logical_package_ref,
            safe_file_records=copied_files,
            artifact_record_ids=artifact_record_ids,
            kernel_manifest_hash=kernel_manifest_hash,
            file_count=len(copied_files),
            artifact_count=len(artifact_record_ids),
            package_content_hash=_package_content_hash(copied_files),
            packaging_provider_call_count=0,
            packaging_network_call_count=0,
            packaging_gemini_call_count=0,
            created_authority_count=0,
            created_permission_count=0,
            real_world_effects_count=0,
            package_status=package_status,
        )
        result = _replace_manifest_id(
            provisional,
            _manifest_identity(provisional),
        )
        errors = _manifest_errors(
            result,
            domain_projection=domain_projection,
            safe_file_contents=copied_contents,
        )
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_manifest_reason(error)) from None
    except Exception:
        raise ValueError("sealed_package_unexpected_exception") from None


def validate_sealed_package_manifest_v01(
    result: object,
    *,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
) -> tuple[str, ...]:
    try:
        return _manifest_errors(
            result,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        )
    except Exception:
        return ("sealed_package_unexpected_exception",)


def sealed_package_manifest_to_plain_dict_v01(
    result: SealedPackageManifestV01,
    *,
    domain_projection: _DomainEvidenceProjectionV01,
    safe_file_contents: tuple[bytes, ...],
) -> dict[str, object]:
    try:
        if _manifest_errors(
            result,
            domain_projection=domain_projection,
            safe_file_contents=safe_file_contents,
        ):
            raise ValueError
        projected = _manifest_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("sealed_package_manifest_invalid") from None


def _safe_file_errors(
    result: object,
    *,
    content_bytes: object,
) -> tuple[str, ...]:
    if type(result) is not SafeFileRecordV01:
        return ("safe_file_record_invalid",)
    errors: list[str] = []
    if (
        not _valid_sha256(result.file_record_id)
        or not _logical_path_valid(result.logical_path)
        or not _media_type_valid(result.media_type)
        or not _nonnegative_int(result.byte_count)
        or not _valid_sha256(result.content_sha256)
        or type(result.source_record_ids) is not tuple
        or not result.source_record_ids
        or any(not _valid_sha256(item) for item in result.source_record_ids)
        or type(result.terminal_newline_required) is not bool
        or type(result.secret_scan_passed) is not bool
    ):
        errors.append("safe_file_record_invalid")
    source_ids_valid = (
        type(result.source_record_ids) is tuple
        and all(_valid_sha256(item) for item in result.source_record_ids)
    )
    if source_ids_valid and len(result.source_record_ids) != len(
        set(result.source_record_ids)
    ):
        errors.append("sealed_package_duplicate_identity")
    if result.evidence_class == _RAW_PRIVATE_EVIDENCE_CLASS:
        errors.append("sealed_package_raw_material_forbidden")
    elif (
        type(result.evidence_class) is not str
        or result.evidence_class not in _REPOSITORY_ALLOWED_EVIDENCE_CLASSES
    ):
        errors.append("safe_file_record_invalid")
    if result.secret_scan_passed is not True:
        errors.append("sealed_package_secret_scan_required")
    if _manifest_self_reference(result.logical_path):
        errors.append("sealed_package_manifest_self_reference_forbidden")

    if type(content_bytes) is not bytes or not content_bytes:
        errors.append("safe_file_record_invalid")
    else:
        expected_hash = _hashlib.sha256(content_bytes).hexdigest()
        if (
            result.byte_count != len(content_bytes)
            or type(result.byte_count) is not int
            or result.content_sha256 != expected_hash
        ):
            errors.append("sealed_package_hash_mismatch")
        if result.terminal_newline_required is True and not _valid_text_content(
            content_bytes
        ):
            errors.append("safe_file_record_invalid")

    try:
        expected_identity = _safe_file_identity(result)
        if result.file_record_id != expected_identity:
            errors.append("sealed_package_identity_mismatch")
    except Exception:
        errors.append("safe_file_record_invalid")
    return _dedupe(errors)


def _manifest_errors(
    result: object,
    *,
    domain_projection: object,
    safe_file_contents: object,
) -> tuple[str, ...]:
    if type(result) is not SealedPackageManifestV01:
        return ("sealed_package_manifest_invalid",)
    errors: list[str] = []
    projection_valid = (
        type(domain_projection) is _DomainEvidenceProjectionV01
        and not _validate_domain_evidence_projection_v01(domain_projection)
    )
    if not projection_valid:
        errors.append("sealed_package_manifest_invalid")

    file_tuple_valid = (
        type(result.safe_file_records) is tuple
        and bool(result.safe_file_records)
        and all(type(item) is SafeFileRecordV01 for item in result.safe_file_records)
    )
    content_tuple_valid = (
        type(safe_file_contents) is tuple
        and all(type(item) is bytes for item in safe_file_contents)
        and len(safe_file_contents) == len(result.safe_file_records)
    )
    if not file_tuple_valid or not content_tuple_valid:
        errors.append("sealed_package_manifest_invalid")
    elif file_tuple_valid:
        for item, content in zip(
            result.safe_file_records,
            safe_file_contents,
            strict=True,
        ):
            errors.extend(_safe_file_errors(item, content_bytes=content))

    text_values = (result.domain_id, result.package_id)
    identity_values = (
        result.manifest_id,
        result.domain_projection_id,
        result.programme_identity_id,
        result.domain_execution_identity_id,
        result.attempt_identity_id,
        result.kernel_manifest_hash,
        result.package_content_hash,
    )
    if (
        result.manifest_version != PACKAGE_VERSION
        or any(not _valid_text(item) for item in text_values)
        or not _logical_path_valid(result.logical_package_ref)
        or any(not _valid_sha256(item) for item in identity_values)
        or type(result.artifact_record_ids) is not tuple
        or any(not _valid_sha256(item) for item in result.artifact_record_ids)
        or type(result.package_status) is not str
        or result.package_status not in PACKAGE_STATUSES
    ):
        errors.append("sealed_package_manifest_invalid")

    if file_tuple_valid:
        file_ids = tuple(item.file_record_id for item in result.safe_file_records)
        paths = tuple(item.logical_path for item in result.safe_file_records)
        if all(_valid_sha256(item) for item in file_ids) and len(file_ids) != len(
            set(file_ids)
        ):
            errors.append("sealed_package_duplicate_identity")
        if all(type(item) is str for item in paths):
            if len(paths) != len(set(paths)):
                errors.append("sealed_package_duplicate_identity")
            normalized_paths = tuple(
                _unicodedata.normalize("NFC", item).casefold() for item in paths
            )
            if len(normalized_paths) != len(set(normalized_paths)):
                errors.append("sealed_package_duplicate_identity")
            if any(_manifest_self_reference(item) for item in paths):
                errors.append("sealed_package_manifest_self_reference_forbidden")
            try:
                canonical_paths = tuple(
                    sorted(
                        paths,
                        key=lambda item: item.encode("utf-8", errors="strict"),
                    )
                )
                if paths != canonical_paths:
                    errors.append("sealed_package_order_invalid")
            except UnicodeError:
                errors.append("sealed_package_order_invalid")

    if projection_valid:
        projection = domain_projection
        expected_bindings = (
            projection.projection_id,
            projection.programme_identity.programme_identity_id,
            projection.domain_execution_identity.domain_execution_identity_id,
            projection.attempt_identity.attempt_identity_id,
            projection.domain_execution_identity.domain_id,
            projection.attempt_identity.package_id,
            projection.attempt_identity.logical_package_ref,
        )
        stored_bindings = (
            result.domain_projection_id,
            result.programme_identity_id,
            result.domain_execution_identity_id,
            result.attempt_identity_id,
            result.domain_id,
            result.package_id,
            result.logical_package_ref,
        )
        if stored_bindings != expected_bindings:
            errors.append("sealed_package_identity_mismatch")

        expected_artifact_ids = tuple(
            item.artifact_record_id for item in projection.artifact_records
        )
        if result.artifact_record_ids != expected_artifact_ids:
            if (
                all(_valid_sha256(item) for item in result.artifact_record_ids)
                and
                len(result.artifact_record_ids) == len(expected_artifact_ids)
                and set(result.artifact_record_ids) == set(expected_artifact_ids)
            ):
                errors.append("sealed_package_order_invalid")
            else:
                errors.append("sealed_package_reference_unresolved")
        if all(
            _valid_sha256(item) for item in result.artifact_record_ids
        ) and len(result.artifact_record_ids) != len(
            set(result.artifact_record_ids)
        ):
            errors.append("sealed_package_duplicate_identity")

        if file_tuple_valid:
            projection_source_ids = {
                item.source_record_id for item in projection.source_records
            }
            package_source_items = tuple(
                source_id
                for item in result.safe_file_records
                for source_id in item.source_record_ids
            )
            if all(_valid_sha256(item) for item in package_source_items):
                package_source_ids = set(package_source_items)
                if (
                    not package_source_ids.issubset(projection_source_ids)
                    or package_source_ids != projection_source_ids
                ):
                    errors.append("sealed_package_reference_unresolved")
            else:
                errors.append("sealed_package_reference_unresolved")
        grounded = _kernel_manifest_hash_grounded(
            projection.source_records,
            result.kernel_manifest_hash,
        )
        if not grounded:
            errors.append("sealed_package_reference_unresolved")

        expected_status = _status_for_projection(projection)
        if result.package_status != expected_status:
            errors.append("sealed_package_status_mismatch")

    count_values = (
        result.file_count,
        result.artifact_count,
        result.packaging_provider_call_count,
        result.packaging_network_call_count,
        result.packaging_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.real_world_effects_count,
    )
    if any(not _nonnegative_int(item) for item in count_values):
        errors.append("sealed_package_manifest_invalid")
    if (
        not _nonnegative_int(result.file_count)
        or result.file_count != len(result.safe_file_records)
        or not _nonnegative_int(result.artifact_count)
        or result.artifact_count != len(result.artifact_record_ids)
    ):
        errors.append("sealed_package_manifest_invalid")

    external_counts = (
        result.packaging_provider_call_count,
        result.packaging_network_call_count,
        result.packaging_gemini_call_count,
    )
    if (
        any(not _nonnegative_int(item) for item in external_counts)
        or external_counts != (0, 0, 0)
    ):
        errors.append("sealed_package_external_call_forbidden")
    if (
        not _nonnegative_int(result.created_authority_count)
        or result.created_authority_count != 0
    ):
        errors.append("sealed_package_authority_creation_forbidden")
    if (
        not _nonnegative_int(result.created_permission_count)
        or result.created_permission_count != 0
    ):
        errors.append("sealed_package_permission_creation_forbidden")
    if (
        not _nonnegative_int(result.real_world_effects_count)
        or result.real_world_effects_count != 0
    ):
        errors.append("sealed_package_effect_forbidden")

    if file_tuple_valid:
        expected_content_hash = _package_content_hash(result.safe_file_records)
        if result.package_content_hash != expected_content_hash:
            errors.append("sealed_package_hash_mismatch")
    try:
        expected_manifest_id = _manifest_identity(result)
        if result.manifest_id != expected_manifest_id:
            errors.append("sealed_package_identity_mismatch")
    except Exception:
        errors.append("sealed_package_manifest_invalid")
    return _dedupe(errors)


def _safe_file_plain(
    result: SafeFileRecordV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["file_record_id"] = result.file_record_id
    projected.update(
        {
            "logical_path": result.logical_path,
            "media_type": result.media_type,
            "byte_count": result.byte_count,
            "content_sha256": result.content_sha256,
            "evidence_class": result.evidence_class,
            "source_record_ids": list(result.source_record_ids),
            "terminal_newline_required": result.terminal_newline_required,
            "secret_scan_passed": result.secret_scan_passed,
        }
    )
    return projected


def _manifest_plain(
    result: SealedPackageManifestV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["manifest_id"] = result.manifest_id
    projected.update(
        {
            "manifest_version": result.manifest_version,
            "domain_projection_id": result.domain_projection_id,
            "programme_identity_id": result.programme_identity_id,
            "domain_execution_identity_id": result.domain_execution_identity_id,
            "attempt_identity_id": result.attempt_identity_id,
            "domain_id": result.domain_id,
            "package_id": result.package_id,
            "logical_package_ref": result.logical_package_ref,
            "safe_file_records": [
                _safe_file_plain(item) for item in result.safe_file_records
            ],
            "artifact_record_ids": list(result.artifact_record_ids),
            "kernel_manifest_hash": result.kernel_manifest_hash,
            "file_count": result.file_count,
            "artifact_count": result.artifact_count,
            "package_content_hash": result.package_content_hash,
            "packaging_provider_call_count": result.packaging_provider_call_count,
            "packaging_network_call_count": result.packaging_network_call_count,
            "packaging_gemini_call_count": result.packaging_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "real_world_effects_count": result.real_world_effects_count,
            "package_status": result.package_status,
        }
    )
    return projected


def _safe_file_identity(result: SafeFileRecordV01) -> str:
    return _identity_hash(
        _SAFE_FILE_RECORD_DOMAIN,
        _safe_file_plain(result, include_id=False),
    )


def _package_content_hash(
    safe_file_records: tuple[SafeFileRecordV01, ...],
) -> str:
    payload = [
        _safe_file_plain(item, include_id=False) for item in safe_file_records
    ]
    return _identity_hash(_PACKAGE_CONTENT_DOMAIN, payload)


def _manifest_identity(result: SealedPackageManifestV01) -> str:
    return _identity_hash(
        _SEALED_PACKAGE_MANIFEST_DOMAIN,
        _manifest_plain(result, include_id=False),
    )


def _replace_file_record_id(
    result: SafeFileRecordV01,
    file_record_id: str,
) -> SafeFileRecordV01:
    return SafeFileRecordV01(
        file_record_id=file_record_id,
        logical_path=result.logical_path,
        media_type=result.media_type,
        byte_count=result.byte_count,
        content_sha256=result.content_sha256,
        evidence_class=result.evidence_class,
        source_record_ids=result.source_record_ids,
        terminal_newline_required=result.terminal_newline_required,
        secret_scan_passed=result.secret_scan_passed,
    )


def _replace_manifest_id(
    result: SealedPackageManifestV01,
    manifest_id: str,
) -> SealedPackageManifestV01:
    values = {field: getattr(result, field) for field in result.__slots__}
    values["manifest_id"] = manifest_id
    return SealedPackageManifestV01(**values)


def _status_for_projection(
    domain_projection: _DomainEvidenceProjectionV01,
) -> str:
    if domain_projection.status == _PROFILE_STATUS_PASS:
        return STATUS_SELF_CONSISTENT_UNANCHORED
    if domain_projection.status == _PROFILE_STATUS_FAIL_CLOSED:
        return STATUS_FAIL_CLOSED
    raise ValueError("sealed_package_manifest_invalid")


def _kernel_manifest_hash_grounded(
    source_records: object,
    kernel_manifest_hash: object,
) -> bool:
    if (
        not _valid_sha256(kernel_manifest_hash)
        or type(source_records) is not tuple
    ):
        return False
    return any(
        type(item) is _SafeSourceRecordV01
        and not _validate_safe_source_record_v01(item)
        and item.evidence_class == _CRYPTOGRAPHIC_INTEGRITY_CLASS
        and type(item.trace_refs) is tuple
        and kernel_manifest_hash in item.trace_refs
        and item.secret_scan_passed is True
        and item.contains_raw_prompt is False
        and item.contains_raw_provider_response is False
        and type(item.real_world_effects_count) is int
        and item.real_world_effects_count == 0
        for item in source_records
    )


def _valid_text_content(content_bytes: bytes) -> bool:
    if (
        not content_bytes.endswith(b"\n")
        or content_bytes.endswith(b"\r\n")
        or content_bytes.endswith(b"\n\n")
        or b"\x00" in content_bytes
    ):
        return False
    try:
        content_bytes.decode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return True


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


def _logical_path_valid(value: object) -> bool:
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


def _manifest_self_reference(value: object) -> bool:
    return type(value) is str and value.casefold() == MANIFEST_FILENAME.casefold()


def _media_type_valid(value: object) -> bool:
    return type(value) is str and _MEDIA_TYPE.fullmatch(value) is not None


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


def _stable_safe_file_reason(error: ValueError) -> str:
    allowed = (
        "safe_file_record_invalid",
        "sealed_package_identity_mismatch",
        "sealed_package_hash_mismatch",
        "sealed_package_duplicate_identity",
        "sealed_package_manifest_self_reference_forbidden",
        "sealed_package_raw_material_forbidden",
        "sealed_package_secret_scan_required",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "safe_file_record_invalid"


def _stable_manifest_reason(error: ValueError) -> str:
    allowed = (
        "safe_file_record_invalid",
        "sealed_package_manifest_invalid",
        "sealed_package_identity_mismatch",
        "sealed_package_hash_mismatch",
        "sealed_package_duplicate_identity",
        "sealed_package_order_invalid",
        "sealed_package_reference_unresolved",
        "sealed_package_manifest_self_reference_forbidden",
        "sealed_package_raw_material_forbidden",
        "sealed_package_secret_scan_required",
        "sealed_package_external_call_forbidden",
        "sealed_package_authority_creation_forbidden",
        "sealed_package_permission_creation_forbidden",
        "sealed_package_effect_forbidden",
        "sealed_package_status_mismatch",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "sealed_package_manifest_invalid"
