"""Deterministic filesystem seam for anchored sealed Replay evidence.

The runner reconstructs typed package evidence from explicit filesystem bytes,
validates an explicit Anchor identity, and records continuity. It does not
rerun semantics, Roots, Corridors, providers, business actions, or effects.
"""

import argparse as _argparse
from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import errno as _errno
import hashlib as _hashlib
import json as _json
import math as _math
import os as _os
from pathlib import Path as _Path
import re as _re
import stat as _stat
import sys as _sys
from types import MappingProxyType as _MappingProxyType
import unicodedata as _unicodedata

_RAW_CLOSE = _os.close
_RAW_FSTAT = _os.fstat

from hedgehog.evidence.external_anchor_v01 import (
    STATUS_ANCHORED_PASS,
    ExternalAnchorPublicationV01,
    AnchoredPackageVerificationV01,
    build_anchored_package_verification_v01,
    build_external_anchor_publication_v01,
    anchored_package_verification_to_plain_dict_v01,
    external_anchor_publication_to_plain_dict_v01,
    validate_anchored_package_verification_v01,
    validate_external_anchor_publication_v01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    DomainEvidenceProjectionV01,
    build_domain_evidence_projection_v01,
    build_domain_execution_identity_v01,
    build_evidence_artifact_record_v01,
    build_live_attempt_identity_v01,
    build_programme_evidence_identity_v01,
    build_safe_source_record_v01,
    validate_domain_evidence_projection_v01,
)
from hedgehog.evidence.sealed_package_v01 import (
    MANIFEST_FILENAME,
    SafeFileRecordV01,
    SealedPackageManifestV01,
    build_safe_file_record_v01,
    build_sealed_package_manifest_v01,
    sealed_package_manifest_to_plain_dict_v01,
    validate_safe_file_record_v01,
    validate_sealed_package_manifest_v01,
)
from hedgehog.evidence.sealed_replay_evidence_v01 import (
    STATUS_PASS,
    SealedReplayEvidenceV01,
    build_sealed_replay_evidence_v01,
    sealed_replay_evidence_to_plain_dict_v01,
    validate_sealed_replay_evidence_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


MODULE_ID = "run_sealed_evidence_replay_v01"
FIXTURE_DOMAINS = ("airline", "supplier_water_filter")
RUNNER_STATUS_FAIL_CLOSED = "FAIL_CLOSED"

_RUNNER_REASON = "sealed_evidence_replay_runner_invalid"
_CLEANUP_REASON = "sealed_evidence_replay_runner_cleanup_failed"
_MAX_SAFE_CONTENT_BYTES = 16 * 1024 * 1024
_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")
_SHA256 = _re.compile(r"^[0-9a-f]{64}$")
_SCHEMA_KEY = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SENSITIVE_ASSIGNMENT = _re.compile(
    r"(?:^|[^a-z0-9_])(?:api_key|private_key|password|passphrase|client_secret|"
    r"secret_value|access_token|refresh_token|bearer_token|auth_token|"
    r"credentials?)\s*[:=]",
    _re.IGNORECASE,
)
_AUTHORIZATION_CREDENTIAL = _re.compile(
    r"(?:^|[^a-z0-9_])authorization\s*[:=]\s*(?:bearer|basic|token|private|secret)\b",
    _re.IGNORECASE,
)
_ABSOLUTE_PATH = _re.compile(r"(?:^|[\s:=,;|()\[\]{}\"'`])/(?!/)[^\s]+")
_WINDOWS_PATH = _re.compile(r"(?:^|[\s:=,;|()\[\]{}\"'`])[A-Za-z]:[\\/]")
_UNC_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])(?:\\\\|//)[^\\/\s]+[\\/][^\s]+"
)
_SAFE_ATTESTATIONS = {
    "containsrawprompt": False,
    "containsrawproviderresponse": False,
    "rawpromptincluded": False,
    "rawproviderresponseincluded": False,
    "secretscanpassed": True,
}
_SAFE_ATTESTATION_KEYS = {
    "containsrawprompt": "contains_raw_prompt",
    "containsrawproviderresponse": "contains_raw_provider_response",
    "rawpromptincluded": "raw_prompt_included",
    "rawproviderresponseincluded": "raw_provider_response_included",
    "secretscanpassed": "secret_scan_passed",
}
_FORBIDDEN_KEY_TOKENS = (
    "rawprompt",
    "prompttext",
    "rawresponse",
    "providerresponse",
    "apikey",
    "privatekey",
    "credential",
    "password",
    "passphrase",
    "secretvalue",
    "accesstoken",
    "refreshtoken",
    "bearertoken",
    "authtoken",
    "clientsecret",
    "authorizationheader",
    "rawusertext",
    "banksecret",
)


class _CleanupFailure(Exception):
    pass


@_dataclass(slots=True)
class _OwnedOutput:
    parent_fd: int
    name: str
    identity: tuple[int, int]
    expected_bytes: bytes


class _SanitizedArgumentParser(_argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        raise ValueError

    def exit(self, status: int = 0, message: str | None = None) -> None:
        del status, message
        raise ValueError


@_dataclass(frozen=True, slots=True)
class SealedEvidenceReplayRunResultV01:
    domain: str
    anchor_publication: ExternalAnchorPublicationV01
    anchored_verification: AnchoredPackageVerificationV01
    reconstructed_manifest: SealedPackageManifestV01
    replay_evidence: SealedReplayEvidenceV01
    fixture_disposable: bool
    summary: _Mapping[str, object]


def run_sealed_evidence_replay_v01(
    *,
    expected_domain: str,
    package_directory: str | _Path,
    source_domain_projection: DomainEvidenceProjectionV01,
    source_manifest: SealedPackageManifestV01,
    source_safe_file_contents: tuple[bytes, ...],
    anchor_file: str | _Path,
    supplied_anchor_publication_id: str,
    reconstructed_domain_projection: DomainEvidenceProjectionV01,
    replay_output_file: str | _Path,
    evidence_refs: tuple[str, ...],
    fixture_disposable: bool,
) -> SealedEvidenceReplayRunResultV01:
    output_owner: _OwnedOutput | None = None
    try:
        if (
            type(expected_domain) is not str
            or expected_domain not in FIXTURE_DOMAINS
            or type(source_domain_projection) is not DomainEvidenceProjectionV01
            or validate_domain_evidence_projection_v01(source_domain_projection)
            or type(reconstructed_domain_projection) is not DomainEvidenceProjectionV01
            or validate_domain_evidence_projection_v01(reconstructed_domain_projection)
            or type(source_manifest) is not SealedPackageManifestV01
            or source_manifest.domain_id != expected_domain
            or source_domain_projection.domain_execution_identity.domain_id
            != expected_domain
            or reconstructed_domain_projection.domain_execution_identity.domain_id
            != expected_domain
            or type(source_safe_file_contents) is not tuple
            or any(type(item) is not bytes for item in source_safe_file_contents)
            or type(supplied_anchor_publication_id) is not str
            or _SHA256.fullmatch(supplied_anchor_publication_id) is None
            or type(evidence_refs) is not tuple
            or not evidence_refs
            or type(fixture_disposable) is not bool
            or fixture_disposable
            is not _projection_is_disposable_fixture(source_domain_projection)
        ):
            raise ValueError
        package = _existing_directory(package_directory)
        anchor_path = _existing_regular_file(anchor_file)
        output = _absent_output_file(
            replay_output_file,
            forbidden_root=package,
            forbidden_file=anchor_path,
        )
        package_before = _snapshot_package_bytes(package, source_manifest)
        anchor_before = _snapshot_regular_file(anchor_path)
        source_contents = _validate_source_package(
            package=package,
            source_domain_projection=source_domain_projection,
            source_manifest=source_manifest,
            supplied_contents=source_safe_file_contents,
        )
        anchor_plain = _strict_json(anchor_before[1])
        if type(anchor_plain) is not dict:
            raise ValueError
        publication_base_head = anchor_plain.get("publication_base_head")
        if type(publication_base_head) is not str or _HEAD.fullmatch(
            publication_base_head
        ) is None:
            raise ValueError
        publication = build_external_anchor_publication_v01(
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_contents,
            publication_base_head=publication_base_head,
        )
        expected_anchor_plain = external_anchor_publication_to_plain_dict_v01(
            publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_contents,
        )
        if (
            anchor_plain != expected_anchor_plain
            or anchor_before[1] != canonical_json_bytes_v01(expected_anchor_plain) + b"\n"
            or validate_external_anchor_publication_v01(
                publication,
                manifest=source_manifest,
                domain_projection=source_domain_projection,
                safe_file_contents=source_contents,
            )
        ):
            raise ValueError
        reconstructed_records, reconstructed_contents = _rebuild_records(
            package=package,
            source_manifest=source_manifest,
        )
        reconstructed_manifest = build_sealed_package_manifest_v01(
            domain_projection=reconstructed_domain_projection,
            safe_file_records=reconstructed_records,
            safe_file_contents=reconstructed_contents,
            kernel_manifest_hash=source_manifest.kernel_manifest_hash,
        )
        if validate_sealed_package_manifest_v01(
            reconstructed_manifest,
            domain_projection=reconstructed_domain_projection,
            safe_file_contents=reconstructed_contents,
        ):
            raise ValueError
        verification = build_anchored_package_verification_v01(
            anchor_publication=publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        if validate_anchored_package_verification_v01(
            verification,
            anchor_publication=publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        ):
            raise ValueError
        replay = build_sealed_replay_evidence_v01(
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_contents,
            evidence_refs=evidence_refs,
        )
        if validate_sealed_replay_evidence_v01(
            replay,
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_contents,
        ):
            raise ValueError
        verification_plain = anchored_package_verification_to_plain_dict_v01(
            verification,
            anchor_publication=publication,
            manifest=source_manifest,
            domain_projection=source_domain_projection,
            safe_file_contents=source_contents,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
        )
        replay_plain = sealed_replay_evidence_to_plain_dict_v01(
            replay,
            source_manifest=source_manifest,
            source_domain_projection=source_domain_projection,
            source_safe_file_contents=source_contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=reconstructed_domain_projection,
            reconstructed_safe_file_contents=reconstructed_contents,
        )
        envelope = {
            "anchored_verification": verification_plain,
            "fixture_disposable": fixture_disposable,
            "replay_evidence": replay_plain,
        }
        if (
            _snapshot_package_bytes(package, source_manifest) != package_before
            or _snapshot_regular_file(anchor_path, expected_size=len(anchor_before[1]))
            != anchor_before
        ):
            raise ValueError
        output_bytes = canonical_json_bytes_v01(envelope) + b"\n"
        output_owner = _write_canonical_output(output, output_bytes, envelope)
        if _snapshot_package_bytes(package, source_manifest) != package_before:
            raise ValueError
        if (
            _snapshot_regular_file(anchor_path, expected_size=len(anchor_before[1]))
            != anchor_before
        ):
            raise ValueError
        summary = _MappingProxyType(
            {
                "anchor_verified": replay.anchor_verified,
                "anchored_verification_id": verification.anchored_verification_id,
                "continuity_verified": replay.continuity_verified,
                "domain": expected_domain,
                "fixture_disposable": fixture_disposable,
                "integrity_verified": replay.integrity_verified,
                "real_world_effects_count": replay.real_world_effects_count,
                "replay_id": replay.replay_id,
                "replay_status": replay.replay_status,
                "verification_status": verification.verification_status,
            }
        )
        result = SealedEvidenceReplayRunResultV01(
            domain=expected_domain,
            anchor_publication=publication,
            anchored_verification=verification,
            reconstructed_manifest=reconstructed_manifest,
            replay_evidence=replay,
            fixture_disposable=fixture_disposable,
            summary=summary,
        )
        if (
            _snapshot_package_bytes(package, source_manifest) != package_before
            or _snapshot_regular_file(anchor_path, expected_size=len(anchor_before[1]))
            != anchor_before
        ):
            raise ValueError
        _release_owned_output(
            output_owner,
            package=package,
            manifest=source_manifest,
            expected_package_snapshot=package_before,
            anchor_path=anchor_path,
            expected_anchor_snapshot=anchor_before,
        )
        output_owner = None
        return result
    except Exception as error:
        cleanup_failed = isinstance(error, _CleanupFailure)
        if output_owner is not None:
            try:
                _cleanup_owned_output(output_owner)
            except _CleanupFailure:
                cleanup_failed = True
        if cleanup_failed:
            raise ValueError(_CLEANUP_REASON) from None
        raise ValueError(_RUNNER_REASON) from None


def _validate_source_package(
    *,
    package: _Path,
    source_domain_projection: DomainEvidenceProjectionV01,
    source_manifest: SealedPackageManifestV01,
    supplied_contents: tuple[bytes, ...],
) -> tuple[bytes, ...]:
    if len(supplied_contents) != source_manifest.file_count:
        raise ValueError
    snapshot = _snapshot_package_bytes(package, source_manifest)
    observed = {path: content for path, _identity_value, content in snapshot[2]}
    reread = []
    for record, supplied in zip(
        source_manifest.safe_file_records,
        supplied_contents,
        strict=True,
    ):
        content = observed[record.logical_path]
        if len(content) != len(supplied):
            raise ValueError
        _scan_content(content, record)
        if content != supplied or validate_safe_file_record_v01(record, content_bytes=content):
            raise ValueError
        reread.append(content)
    contents = tuple(reread)
    if validate_sealed_package_manifest_v01(
        source_manifest,
        domain_projection=source_domain_projection,
        safe_file_contents=contents,
    ):
        raise ValueError
    manifest_plain = sealed_package_manifest_to_plain_dict_v01(
        source_manifest,
        domain_projection=source_domain_projection,
        safe_file_contents=contents,
    )
    manifest_bytes = observed[MANIFEST_FILENAME]
    if (
        manifest_bytes != canonical_json_bytes_v01(manifest_plain) + b"\n"
        or _strict_json(manifest_bytes) != manifest_plain
    ):
        raise ValueError
    return contents


def _rebuild_records(
    *,
    package: _Path,
    source_manifest: SealedPackageManifestV01,
) -> tuple[tuple[SafeFileRecordV01, ...], tuple[bytes, ...]]:
    snapshot = _snapshot_package_bytes(package, source_manifest)
    observed = {path: content for path, _identity_value, content in snapshot[2]}
    records = []
    contents = []
    for source_record in source_manifest.safe_file_records:
        content = observed[source_record.logical_path]
        _scan_content(content, source_record)
        rebuilt = build_safe_file_record_v01(
            logical_path=source_record.logical_path,
            media_type=source_record.media_type,
            content_bytes=content,
            evidence_class=source_record.evidence_class,
            source_record_ids=source_record.source_record_ids,
            terminal_newline_required=source_record.terminal_newline_required,
            secret_scan_passed=True,
        )
        if validate_safe_file_record_v01(rebuilt, content_bytes=content):
            raise ValueError
        records.append(rebuilt)
        contents.append(content)
    return tuple(records), tuple(contents)


def _scan_content(content: bytes, record: SafeFileRecordV01) -> None:
    if (
        type(content) is not bytes
        or not content
        or len(content) > _MAX_SAFE_CONTENT_BYTES
        or b"\x00" in content
        or b"\r" in content
    ):
        raise ValueError
    if content.startswith(b"\xef\xbb\xbf"):
        raise ValueError
    text = content.decode("utf-8", errors="strict")
    if record.terminal_newline_required and (
        not content.endswith(b"\n") or content.endswith(b"\n\n")
    ):
        raise ValueError
    if record.media_type == "application/json":
        parsed = _strict_json(content)
        _inspect_safe_json(parsed)
        if canonical_json_bytes_v01(parsed) + b"\n" != content:
            raise ValueError
    else:
        _inspect_public_text(text, allow_lf=True)


def _inspect_safe_json(value: object) -> None:
    if type(value) is dict:
        for key, item in value.items():
            _inspect_json_key(key, item)
            _inspect_safe_json(item)
        return
    if type(value) is list:
        for item in value:
            _inspect_safe_json(item)
        return
    if type(value) is str:
        _inspect_public_text(value)
        return
    if type(value) is float:
        if not _math.isfinite(value):
            raise ValueError
        return
    if type(value) in (int, bool) or value is None:
        return
    raise ValueError


def _inspect_json_key(key: object, value: object) -> None:
    if type(key) is not str or _SCHEMA_KEY.fullmatch(key) is None:
        raise ValueError
    normalized = _unicodedata.normalize("NFKC", key).casefold()
    token = "".join(character for character in normalized if character.isalnum())
    if token in _SAFE_ATTESTATIONS:
        if key != _SAFE_ATTESTATION_KEYS[token]:
            raise ValueError
        if type(value) is not bool or value is not _SAFE_ATTESTATIONS[token]:
            raise ValueError
        return
    _inspect_public_text(key)
    if token in ("authorization", "token", "secret") or any(
        forbidden in token for forbidden in _FORBIDDEN_KEY_TOKENS
    ):
        raise ValueError


def _inspect_public_text(value: str, *, allow_lf: bool = False) -> None:
    normalized = _unicodedata.normalize("NFKC", value).casefold()
    if (
        type(value) is not str
        or _unicodedata.normalize("NFC", value) != value
        or any(
            _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
            and not (allow_lf and character == "\n")
            for character in value
        )
        or "file://" in value.casefold()
        or "traceback" in value.casefold()
        or _ABSOLUTE_PATH.search(value)
        or _WINDOWS_PATH.search(value)
        or _UNC_PATH.search(value)
        or _re.search(r"\b0x[0-9a-f]{6,}\b", value, _re.IGNORECASE)
        or _re.search(r"<[^>\r\n]*\bobject at 0x[0-9a-f]+>", value, _re.IGNORECASE)
        or _SENSITIVE_ASSIGNMENT.search(normalized)
        or _AUTHORIZATION_CREDENTIAL.search(normalized)
        or _contains_sensitive_material(normalized)
    ):
        raise ValueError


def _contains_sensitive_material(normalized: str) -> bool:
    compact = "".join(character for character in normalized if character.isalnum())
    if "beginprivatekey" in compact or "beginrsaprivatekey" in compact:
        return True
    tokens = (
        "rawprompt",
        "rawproviderresponse",
        "providerresponse",
        "privatekey",
        "apikey",
        "password",
        "passphrase",
        "accesstoken",
        "clientsecret",
        "credential",
        "secretvalue",
        "refreshtoken",
        "bearertoken",
        "authtoken",
    )
    assignment = _re.compile(
        r"(?:raw[\W_]*prompt|raw[\W_]*provider[\W_]*response|provider[\W_]*response|"
        r"private[\W_]*key|api[\W_]*key|password|passphrase|access[\W_]*token|"
        r"refresh[\W_]*token|bearer[\W_]*token|auth[\W_]*token|"
        r"client[\W_]*secret|secret[\W_]*value|credentials?)\s*[:=]"
    )
    authorization = _re.compile(
        r"authorization\s*[:=]\s*(?:bearer|basic|token|private|secret)\b"
    )
    return bool(
        assignment.search(normalized)
        or authorization.search(normalized)
        or any(token in compact for token in tokens)
    )


def _strict_json(content: bytes) -> object:
    if type(content) is not bytes or not content.endswith(b"\n") or content.endswith(b"\n\n"):
        raise ValueError

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def invalid(_value: str) -> object:
        raise ValueError

    try:
        return _json.loads(
            content[:-1].decode("utf-8", errors="strict"),
            object_pairs_hook=pairs,
            parse_constant=invalid,
        )
    except Exception:
        raise ValueError from None


def _existing_directory(value: object) -> _Path:
    if type(value) is not str and not isinstance(value, _Path):
        raise ValueError
    path = _Path(value)
    if not path.is_absolute():
        raise ValueError
    descriptor = _open_absolute_directory(path)
    _close_proven(descriptor)
    return path


def _existing_regular_file(value: object) -> _Path:
    if type(value) is not str and not isinstance(value, _Path):
        raise ValueError
    path = _Path(value)
    if not path.is_absolute():
        raise ValueError
    _snapshot_regular_file(path)
    return path


def _absent_output_file(
    value: object,
    *,
    forbidden_root: _Path,
    forbidden_file: _Path,
) -> _Path:
    if type(value) is not str and not isinstance(value, _Path):
        raise ValueError
    path = _Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError
    parent_fd = _open_absolute_directory(path.parent)
    try:
        try:
            _os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError
    finally:
        _close_proven(parent_fd)
    if path.parent == forbidden_root or forbidden_root in path.parent.parents:
        raise ValueError
    if path == forbidden_file:
        raise ValueError
    return path


def _snapshot_package_bytes(
    package: _Path,
    manifest: SealedPackageManifestV01,
) -> tuple[
    tuple[int, int],
    tuple[tuple[str, tuple[int, int]], ...],
    tuple[tuple[str, tuple[int, int], bytes], ...],
]:
    expected = {MANIFEST_FILENAME, *(item.logical_path for item in manifest.safe_file_records)}
    root_fd = _open_absolute_directory(package)
    try:
        root_identity = _identity(_os.fstat(root_fd))
        files, directories = _inventory_at(root_fd, expected)
        entries = tuple(
            (
                logical_path,
                files[logical_path],
                _read_relative_file(
                    root_fd,
                    logical_path,
                    expected_identity=files[logical_path],
                    expected_directories=directories,
                )[1],
            )
            for logical_path in sorted(expected, key=lambda value: value.encode("utf-8"))
        )
        final_files, final_directories = _inventory_at(root_fd, expected)
        if (
            final_files != files
            or final_directories != directories
            or _identity(_os.fstat(root_fd)) != root_identity
        ):
            raise ValueError
        return (
            root_identity,
            tuple(sorted(directories.items(), key=lambda item: item[0].encode("utf-8"))),
            entries,
        )
    finally:
        _close_proven(root_fd)


def _require_regular_file(path: _Path) -> None:
    _safe_read_regular(path)


def _write_canonical_output(
    path: _Path,
    content: bytes,
    expected_plain: dict[str, object],
) -> _OwnedOutput:
    parent_fd = _open_absolute_directory(path.parent)
    descriptor = -1
    owner: _OwnedOutput | None = None
    try:
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL | getattr(_os, "O_NOFOLLOW", 0)
        descriptor = _os.open(path.name, flags, 0o600, dir_fd=parent_fd)
        identity = _owned_file_identity(descriptor, parent_fd, path.name)
        owner = _OwnedOutput(parent_fd, path.name, identity, bytes(content))
        position = 0
        while position < len(content):
            written = _os.write(descriptor, content[position:])
            if type(written) is not int or written <= 0:
                raise ValueError
            position += written
        _os.fsync(descriptor)
        _close_proven(descriptor)
        descriptor = -1
        reread_identity, reread = _read_name_at(
            parent_fd,
            path.name,
            expected_size=len(content),
            expected_identity=identity,
        )
        if reread_identity != identity or reread != content or _strict_json(reread) != expected_plain:
            raise ValueError
        return owner
    except Exception as error:
        cleanup_failed = isinstance(error, _CleanupFailure)
        if descriptor >= 0:
            try:
                _close_proven(descriptor)
            except _CleanupFailure:
                cleanup_failed = True
        if owner is not None:
            try:
                _cleanup_owned_output(owner)
            except _CleanupFailure:
                cleanup_failed = True
        else:
            try:
                _close_proven(parent_fd)
            except _CleanupFailure:
                cleanup_failed = True
        if cleanup_failed:
            raise _CleanupFailure from None
        raise


def _directory_flags() -> int:
    return _os.O_RDONLY | getattr(_os, "O_DIRECTORY", 0) | getattr(_os, "O_NOFOLLOW", 0)


def _close_proven(descriptor: int) -> None:
    try:
        _os.close(descriptor)
    except Exception:
        pass
    try:
        _os.fstat(descriptor)
    except OSError as error:
        if error.errno == _errno.EBADF:
            return
        raise _CleanupFailure from None
    try:
        _RAW_CLOSE(descriptor)
    except Exception:
        raise _CleanupFailure from None
    try:
        _os.fstat(descriptor)
    except OSError as error:
        if error.errno == _errno.EBADF:
            return
    raise _CleanupFailure


def _open_absolute_directory(path: _Path) -> int:
    if not path.is_absolute():
        raise ValueError
    descriptor = _os.open(path.anchor, _directory_flags())
    try:
        for component in path.parts[1:]:
            child = _os.open(component, _directory_flags(), dir_fd=descriptor)
            try:
                if not _stat.S_ISDIR(_os.fstat(child).st_mode):
                    raise ValueError
                _close_proven(descriptor)
            except Exception as error:
                try:
                    _close_proven(child)
                except _CleanupFailure:
                    raise _CleanupFailure from None
                raise error
            descriptor = child
        if not _stat.S_ISDIR(_os.fstat(descriptor).st_mode):
            raise ValueError
        return descriptor
    except Exception:
        _close_proven(descriptor)
        raise


def _duplicate_directory(descriptor: int) -> int:
    duplicate = _os.dup(descriptor)
    try:
        if not _stat.S_ISDIR(_os.fstat(duplicate).st_mode):
            raise ValueError
        return duplicate
    except Exception:
        _close_proven(duplicate)
        raise


def _identity(status: _os.stat_result) -> tuple[int, int]:
    return status.st_dev, status.st_ino


def _descriptor_status(descriptor: int) -> _os.stat_result:
    try:
        return _os.fstat(descriptor)
    except Exception:
        try:
            return _RAW_FSTAT(descriptor)
        except Exception:
            raise _CleanupFailure from None


def _owned_file_identity(descriptor: int, parent_fd: int, name: str) -> tuple[int, int]:
    opened = _descriptor_status(descriptor)
    if not _stat.S_ISREG(opened.st_mode):
        raise _CleanupFailure
    identity = _identity(opened)
    entry = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not _stat.S_ISREG(entry.st_mode) or _identity(entry) != identity:
        raise _CleanupFailure
    return identity


def _open_relative_directory(
    root_fd: int,
    components: tuple[str, ...],
    *,
    expected_directories: dict[str, tuple[int, int]] | None = None,
) -> int:
    descriptor = _duplicate_directory(root_fd)
    prefix: list[str] = []
    try:
        for component in components:
            prefix.append(component)
            child = _os.open(component, _directory_flags(), dir_fd=descriptor)
            try:
                opened = _os.fstat(child)
                entry = _os.stat(component, dir_fd=descriptor, follow_symlinks=False)
                expected = None if expected_directories is None else expected_directories.get(
                    "/".join(prefix)
                )
                if (
                    not _stat.S_ISDIR(opened.st_mode)
                    or not _stat.S_ISDIR(entry.st_mode)
                    or _identity(opened) != _identity(entry)
                    or (expected_directories is not None and _identity(opened) != expected)
                ):
                    raise ValueError
                _close_proven(descriptor)
            except Exception as error:
                try:
                    _close_proven(child)
                except _CleanupFailure:
                    raise _CleanupFailure from None
                raise error
            descriptor = child
        return descriptor
    except Exception:
        _close_proven(descriptor)
        raise


def _read_name_at(
    parent_fd: int,
    name: str,
    *,
    expected_size: int | None = None,
    expected_identity: tuple[int, int] | None = None,
) -> tuple[tuple[int, int], bytes]:
    before = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not _stat.S_ISREG(before.st_mode):
        raise ValueError
    descriptor = _os.open(name, _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0), dir_fd=parent_fd)
    try:
        opened = _os.fstat(descriptor)
        identity = _identity(opened)
        limit = opened.st_size if expected_size is None else expected_size
        if (
            not _stat.S_ISREG(opened.st_mode)
            or identity != _identity(before)
            or (expected_identity is not None and identity != expected_identity)
            or type(limit) is not int
            or limit < 0
            or limit > _MAX_SAFE_CONTENT_BYTES
            or opened.st_size != limit
        ):
            raise ValueError
        chunks: list[bytes] = []
        total = 0
        while total < limit:
            chunk = _os.read(descriptor, min(65536, limit - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if _os.read(descriptor, 1) or total != limit:
            raise ValueError
        after = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _identity(after) != identity or after.st_size != total:
            raise ValueError
        result = b"".join(chunks)
        _close_proven(descriptor)
        descriptor = -1
        return identity, result
    finally:
        if descriptor >= 0:
            _close_proven(descriptor)


def _read_relative_file(
    root_fd: int,
    logical_path: str,
    *,
    expected_identity: tuple[int, int] | None = None,
    expected_directories: dict[str, tuple[int, int]] | None = None,
) -> tuple[tuple[int, int], bytes]:
    parts = logical_path.split("/")
    parent_fd = _open_relative_directory(
        root_fd,
        tuple(parts[:-1]),
        expected_directories=expected_directories,
    )
    try:
        return _read_name_at(parent_fd, parts[-1], expected_identity=expected_identity)
    finally:
        _close_proven(parent_fd)


def _safe_read_regular(path: _Path, *, expected_size: int | None = None) -> bytes:
    if not path.is_absolute():
        raise ValueError
    return _snapshot_regular_file(path, expected_size=expected_size)[1]


def _snapshot_regular_file(
    path: _Path,
    *,
    expected_size: int | None = None,
) -> tuple[tuple[int, int], bytes]:
    parent_fd = _open_absolute_directory(path.parent)
    try:
        return _read_name_at(parent_fd, path.name, expected_size=expected_size)
    finally:
        _close_proven(parent_fd)


def _inventory_at(
    root_fd: int,
    expected_files: set[str],
) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
    expected_directories: set[str] = set()
    for logical_path in expected_files:
        parts = logical_path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            expected_directories.add("/".join(parts[:index]))
    observed_files: set[str] = set()
    observed_directories: set[str] = set()
    files: dict[str, tuple[int, int]] = {}
    directories: dict[str, tuple[int, int]] = {}

    def visit(directory_fd: int, prefix: str) -> None:
        with _os.scandir(directory_fd) as entries:
            ordered = sorted(entries, key=lambda entry: entry.name.encode("utf-8"))
        for entry in ordered:
            relative = f"{prefix}/{entry.name}" if prefix else entry.name
            status = entry.stat(follow_symlinks=False)
            if _stat.S_ISDIR(status.st_mode):
                if relative not in expected_directories:
                    raise ValueError
                observed_directories.add(relative)
                directories[relative] = _identity(status)
                child = _os.open(entry.name, _directory_flags(), dir_fd=directory_fd)
                try:
                    if _identity(_os.fstat(child)) != _identity(status):
                        raise ValueError
                    visit(child, relative)
                finally:
                    _close_proven(child)
            elif _stat.S_ISREG(status.st_mode):
                if relative not in expected_files:
                    raise ValueError
                observed_files.add(relative)
                files[relative] = _identity(status)
            else:
                raise ValueError

    visit(root_fd, "")
    if observed_files != expected_files or observed_directories != expected_directories:
        raise ValueError
    return files, directories


def _cleanup_owned_output(owner: _OwnedOutput) -> None:
    failed = False
    try:
        status = _os.stat(owner.name, dir_fd=owner.parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        status = None
    except Exception:
        failed = True
        status = None
    if status is not None:
        if not _stat.S_ISREG(status.st_mode) or _identity(status) != owner.identity:
            failed = True
        else:
            try:
                _os.unlink(owner.name, dir_fd=owner.parent_fd)
            except Exception:
                failed = True
            else:
                try:
                    _os.stat(owner.name, dir_fd=owner.parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                except Exception:
                    failed = True
                else:
                    failed = True
    try:
        _close_proven(owner.parent_fd)
    except _CleanupFailure:
        failed = True
    if failed:
        raise _CleanupFailure


def _release_owned_output(
    owner: _OwnedOutput,
    *,
    package: _Path,
    manifest: SealedPackageManifestV01,
    expected_package_snapshot: object,
    anchor_path: _Path,
    expected_anchor_snapshot: tuple[tuple[int, int], bytes],
) -> None:
    if (
        _snapshot_package_bytes(package, manifest) != expected_package_snapshot
        or _snapshot_regular_file(
            anchor_path,
            expected_size=len(expected_anchor_snapshot[1]),
        )
        != expected_anchor_snapshot
    ):
        raise ValueError
    identity, content = _read_name_at(
        owner.parent_fd,
        owner.name,
        expected_size=len(owner.expected_bytes),
        expected_identity=owner.identity,
    )
    if (
        identity != owner.identity
        or content != owner.expected_bytes
        or _strict_json(content) != _strict_json(owner.expected_bytes)
    ):
        raise ValueError
    _close_proven(owner.parent_fd)


def _fixture_context(
    *,
    domain: str,
    execution_head: str,
    package: _Path,
) -> tuple[DomainEvidenceProjectionV01, SealedPackageManifestV01, tuple[bytes, ...]]:
    if domain not in FIXTURE_DOMAINS or _HEAD.fullmatch(execution_head) is None:
        raise ValueError
    kernel_hash = _hashlib.sha256(
        canonical_json_bytes_v01(
            {
                "domain": domain,
                "execution_head": execution_head,
                "fixture_class": "disposable_r1",
            }
        )
    ).hexdigest()
    programme = build_programme_evidence_identity_v01(
        programme_id="two_domain_all_real_sealed_evidence_program_v01",
        programme_version="v0.1",
    )
    identity = build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=domain,
        execution_head=execution_head,
        source_task_id=f"fixture:{domain}:sealed-evidence",
        run_id=f"fixture:{domain}:run-v01",
        report_id=f"fixture:{domain}:report-v01",
    )
    attempt = build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=identity,
        attempt_number=1,
        package_id=f"fixture:{domain}:package-v01",
        logical_package_ref=f"fixtures/{domain}/sealed_package_v01",
        output_directory_ref=f"fixtures/{domain}/sealed_package_v01/output",
        provider_mode="deterministic_fixture",
        model_id="none",
        expected_actor_count=1,
        provider_call_budget=0,
    )
    source = build_safe_source_record_v01(
        source_id=f"fixture:{domain}:kernel-integrity",
        source_type=f"{domain}_fixture_kernel_integrity",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        canonical_projection={
            "domain": domain,
            "fixture_disposable": True,
            "kernel_manifest_hash": kernel_hash,
        },
        media_type="application/json",
        trace_refs=(kernel_hash, f"fixture:{domain}:integrity"),
        contains_raw_prompt=False,
        contains_raw_provider_response=False,
        secret_scan_passed=True,
        observed_provider_call_count=0,
        observed_network_call_count=0,
        observed_gemini_call_count=0,
        real_world_effects_count=0,
    )
    artifact = build_evidence_artifact_record_v01(
        artifact_id=f"fixture:{domain}:kernel-manifest",
        artifact_type="fixture_kernel_manifest",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,),
        canonical_projection={"domain": domain, "kernel_manifest_hash": kernel_hash},
        authority_class="evidence_only",
        owner_root_id=None,
        trace_refs=(kernel_hash,),
        created_authority_count=0,
        created_permission_count=0,
        real_world_effects_count=0,
    )
    projection = build_domain_evidence_projection_v01(
        programme_identity=programme,
        domain_execution_identity=identity,
        attempt_identity=attempt,
        source_records=(source,),
        artifact_records=(artifact,),
        kernel_artifact_refs=(),
        causal_consumption_refs=(),
        evidence_refs=(f"fixture:{domain}:evidence",),
        limitation_refs=(
            "limitation:disposable_fixture_only",
            "limitation:not_official_domain_evidence",
        ),
    )
    logical_path = f"evidence/01-{source.source_type}.json"
    content = _safe_read_regular(package / logical_path)
    record = build_safe_file_record_v01(
        logical_path=logical_path,
        media_type="application/json",
        content_bytes=content,
        evidence_class=source.evidence_class,
        source_record_ids=(source.source_record_id,),
        terminal_newline_required=True,
        secret_scan_passed=True,
    )
    manifest = build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=(record,),
        safe_file_contents=(content,),
        kernel_manifest_hash=kernel_hash,
    )
    return projection, manifest, (content,)


def _projection_is_disposable_fixture(
    projection: DomainEvidenceProjectionV01,
) -> bool:
    try:
        return projection == _expected_fixture_projection(
            projection.domain_execution_identity.domain_id,
            projection.domain_execution_identity.execution_head,
        )
    except Exception:
        return False


def _expected_fixture_projection(
    domain: str,
    execution_head: str,
) -> DomainEvidenceProjectionV01:
    if domain not in FIXTURE_DOMAINS or _HEAD.fullmatch(execution_head) is None:
        raise ValueError
    kernel_hash = _hashlib.sha256(
        canonical_json_bytes_v01(
            {
                "domain": domain,
                "execution_head": execution_head,
                "fixture_class": "disposable_r1",
            }
        )
    ).hexdigest()
    programme = build_programme_evidence_identity_v01(
        programme_id="two_domain_all_real_sealed_evidence_program_v01",
        programme_version="v0.1",
    )
    identity = build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=domain,
        execution_head=execution_head,
        source_task_id=f"fixture:{domain}:sealed-evidence",
        run_id=f"fixture:{domain}:run-v01",
        report_id=f"fixture:{domain}:report-v01",
    )
    attempt = build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=identity,
        attempt_number=1,
        package_id=f"fixture:{domain}:package-v01",
        logical_package_ref=f"fixtures/{domain}/sealed_package_v01",
        output_directory_ref=f"fixtures/{domain}/sealed_package_v01/output",
        provider_mode="deterministic_fixture",
        model_id="none",
        expected_actor_count=1,
        provider_call_budget=0,
    )
    source = build_safe_source_record_v01(
        source_id=f"fixture:{domain}:kernel-integrity",
        source_type=f"{domain}_fixture_kernel_integrity",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        canonical_projection={
            "domain": domain,
            "fixture_disposable": True,
            "kernel_manifest_hash": kernel_hash,
        },
        media_type="application/json",
        trace_refs=(kernel_hash, f"fixture:{domain}:integrity"),
        contains_raw_prompt=False,
        contains_raw_provider_response=False,
        secret_scan_passed=True,
        observed_provider_call_count=0,
        observed_network_call_count=0,
        observed_gemini_call_count=0,
        real_world_effects_count=0,
    )
    artifact = build_evidence_artifact_record_v01(
        artifact_id=f"fixture:{domain}:kernel-manifest",
        artifact_type="fixture_kernel_manifest",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,),
        canonical_projection={"domain": domain, "kernel_manifest_hash": kernel_hash},
        authority_class="evidence_only",
        owner_root_id=None,
        trace_refs=(kernel_hash,),
        created_authority_count=0,
        created_permission_count=0,
        real_world_effects_count=0,
    )
    return build_domain_evidence_projection_v01(
        programme_identity=programme,
        domain_execution_identity=identity,
        attempt_identity=attempt,
        source_records=(source,),
        artifact_records=(artifact,),
        kernel_artifact_refs=(),
        causal_consumption_refs=(),
        evidence_refs=(f"fixture:{domain}:evidence",),
        limitation_refs=(
            "limitation:disposable_fixture_only",
            "limitation:not_official_domain_evidence",
        ),
    )


def _safe_json_line(value: _Mapping[str, object]) -> str:
    return canonical_json_bytes_v01(dict(value)).decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        parser = _SanitizedArgumentParser(add_help=False)
        parser.add_argument("--fixture", action="store_true")
        parser.add_argument("--domain", choices=FIXTURE_DOMAINS, required=True)
        parser.add_argument("--execution-head", required=True)
        parser.add_argument("--package", required=True)
        parser.add_argument("--anchor", required=True)
        parser.add_argument("--supplied-anchor-id", required=True)
        parser.add_argument("--replay-output", required=True)
        parser.add_argument("--evidence-ref", action="append", required=True)
        args = parser.parse_args(argv)
        if not args.fixture:
            raise ValueError
        package = _existing_directory(args.package)
        projection, manifest, contents = _fixture_context(
            domain=args.domain,
            execution_head=args.execution_head,
            package=package,
        )
        result = run_sealed_evidence_replay_v01(
            expected_domain=args.domain,
            package_directory=package,
            source_domain_projection=projection,
            source_manifest=manifest,
            source_safe_file_contents=contents,
            anchor_file=args.anchor,
            supplied_anchor_publication_id=args.supplied_anchor_id,
            reconstructed_domain_projection=projection,
            replay_output_file=args.replay_output,
            evidence_refs=tuple(args.evidence_ref),
            fixture_disposable=True,
        )
        _sys.stdout.write(_safe_json_line(result.summary) + "\n")
        return 0 if (
            result.anchored_verification.verification_status
            == STATUS_ANCHORED_PASS
            and result.replay_evidence.replay_status == STATUS_PASS
        ) else 3
    except Exception as error:
        reason = (
            _CLEANUP_REASON
            if type(error) is ValueError and error.args == (_CLEANUP_REASON,)
            else _RUNNER_REASON
        )
        _sys.stdout.write(
            _safe_json_line(
                {"reason": reason, "status": RUNNER_STATUS_FAIL_CLOSED}
            )
            + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
