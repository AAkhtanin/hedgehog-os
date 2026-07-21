"""Deterministic filesystem seam for disposable external Anchor evidence.

This runner validates an explicit frozen package and writes one EVIDENCE_ONLY
publication. It performs no Git operation, anchored verification, Replay,
provider call, business action, or effect.
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
    STATUS_EVIDENCE_ONLY,
    ExternalAnchorPublicationV01,
    build_external_anchor_publication_v01,
    external_anchor_publication_to_plain_dict_v01,
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
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


MODULE_ID = "run_sealed_evidence_anchor_v01"
FIXTURE_DOMAINS = ("airline", "supplier_water_filter")
RUNNER_STATUS_FAIL_CLOSED = "FAIL_CLOSED"

_RUNNER_REASON = "sealed_evidence_anchor_runner_invalid"
_CLEANUP_REASON = "sealed_evidence_anchor_runner_cleanup_failed"
_MAX_SAFE_CONTENT_BYTES = 16 * 1024 * 1024
_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")
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
class SealedEvidenceAnchorRunResultV01:
    domain: str
    anchor_publication: ExternalAnchorPublicationV01
    fixture_disposable: bool
    summary: _Mapping[str, object]


def run_sealed_evidence_anchor_v01(
    *,
    expected_domain: str,
    package_directory: str | _Path,
    domain_projection: DomainEvidenceProjectionV01,
    manifest: SealedPackageManifestV01,
    ordered_safe_contents: tuple[bytes, ...],
    publication_base_head: str,
    anchor_output_file: str | _Path,
    fixture_disposable: bool,
) -> SealedEvidenceAnchorRunResultV01:
    output_owner: _OwnedOutput | None = None
    try:
        if (
            type(expected_domain) is not str
            or expected_domain not in FIXTURE_DOMAINS
            or type(domain_projection) is not DomainEvidenceProjectionV01
            or validate_domain_evidence_projection_v01(domain_projection)
            or type(manifest) is not SealedPackageManifestV01
            or manifest.domain_id != expected_domain
            or domain_projection.domain_execution_identity.domain_id
            != expected_domain
            or type(ordered_safe_contents) is not tuple
            or any(type(item) is not bytes for item in ordered_safe_contents)
            or type(publication_base_head) is not str
            or _HEAD.fullmatch(publication_base_head) is None
            or type(fixture_disposable) is not bool
            or fixture_disposable
            is not _projection_is_disposable_fixture(domain_projection)
        ):
            raise ValueError
        package = _existing_package_directory(package_directory)
        output = _absent_output_file(anchor_output_file, forbidden_root=package)
        before = _snapshot_package_bytes(package, manifest)
        reread = _validate_package(
            package=package,
            domain_projection=domain_projection,
            manifest=manifest,
            ordered_safe_contents=ordered_safe_contents,
        )
        publication = build_external_anchor_publication_v01(
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=reread,
            publication_base_head=publication_base_head,
        )
        if (
            validate_external_anchor_publication_v01(
                publication,
                manifest=manifest,
                domain_projection=domain_projection,
                safe_file_contents=reread,
            )
            or publication.anchor_status != STATUS_EVIDENCE_ONLY
        ):
            raise ValueError
        plain = external_anchor_publication_to_plain_dict_v01(
            publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=reread,
        )
        output_bytes = canonical_json_bytes_v01(plain) + b"\n"
        output_owner = _write_canonical_output(output, output_bytes, plain)
        if _snapshot_package_bytes(package, manifest) != before:
            raise ValueError
        summary = _MappingProxyType(
            {
                "anchor_publication_id": publication.anchor_publication_id,
                "anchor_status": publication.anchor_status,
                "anchored_pass_claimed": publication.anchored_pass_claimed,
                "domain": expected_domain,
                "external_anchor_supplied_at_publication": (
                    publication.external_anchor_supplied_at_publication
                ),
                "external_anchor_verified_at_publication": (
                    publication.external_anchor_verified_at_publication
                ),
                "fixture_disposable": fixture_disposable,
                "manifest_id": publication.manifest_id,
                "publication_gemini_call_count": 0,
                "publication_network_call_count": 0,
                "publication_provider_call_count": 0,
                "real_world_effects_count": 0,
            }
        )
        result = SealedEvidenceAnchorRunResultV01(
            domain=expected_domain,
            anchor_publication=publication,
            fixture_disposable=fixture_disposable,
            summary=summary,
        )
        if _snapshot_package_bytes(package, manifest) != before:
            raise ValueError
        _release_owned_output(
            output_owner,
            package=package,
            manifest=manifest,
            expected_package_snapshot=before,
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


def _validate_package(
    *,
    package: _Path,
    domain_projection: DomainEvidenceProjectionV01,
    manifest: SealedPackageManifestV01,
    ordered_safe_contents: tuple[bytes, ...],
) -> tuple[bytes, ...]:
    if len(ordered_safe_contents) != manifest.file_count:
        raise ValueError
    snapshot = _snapshot_package_bytes(package, manifest)
    observed = {path: content for path, _identity_value, content in snapshot[2]}
    reread: list[bytes] = []
    for record, supplied in zip(
        manifest.safe_file_records,
        ordered_safe_contents,
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
        manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
    ):
        raise ValueError
    manifest_plain = sealed_package_manifest_to_plain_dict_v01(
        manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
    )
    manifest_bytes = observed[MANIFEST_FILENAME]
    if manifest_bytes != canonical_json_bytes_v01(manifest_plain) + b"\n":
        raise ValueError
    if _strict_json(manifest_bytes) != manifest_plain:
        raise ValueError
    return contents


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
    if not content.endswith(b"\n") or content.endswith(b"\n\n"):
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


def _existing_package_directory(value: object) -> _Path:
    if type(value) is not str and not isinstance(value, _Path):
        raise ValueError
    path = _Path(value)
    if not path.is_absolute():
        raise ValueError
    descriptor = _open_absolute_directory(path)
    _close_proven(descriptor)
    return path


def _absent_output_file(value: object, *, forbidden_root: _Path) -> _Path:
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
        file_identities, directories = _inventory_at(root_fd, expected)
        entries = tuple(
            (
                logical_path,
                file_identities[logical_path],
                _read_relative_file(
                    root_fd,
                    logical_path,
                    expected_identity=file_identities[logical_path],
                    expected_directories=directories,
                )[1],
            )
            for logical_path in sorted(expected, key=lambda value: value.encode("utf-8"))
        )
        final_files, final_directories = _inventory_at(root_fd, expected)
        if (
            final_files != file_identities
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
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL
        if hasattr(_os, "O_NOFOLLOW"):
            flags |= _os.O_NOFOLLOW
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
    flags = _os.O_RDONLY
    if hasattr(_os, "O_DIRECTORY"):
        flags |= _os.O_DIRECTORY
    if hasattr(_os, "O_NOFOLLOW"):
        flags |= _os.O_NOFOLLOW
    return flags


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
    flags = _os.O_RDONLY | (getattr(_os, "O_NOFOLLOW", 0))
    descriptor = _os.open(name, flags, dir_fd=parent_fd)
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
    parent_fd = _open_absolute_directory(path.parent)
    try:
        return _read_name_at(parent_fd, path.name, expected_size=expected_size)[1]
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
) -> None:
    if _snapshot_package_bytes(package, manifest) != expected_package_snapshot:
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
        parser.add_argument("--publication-base-head", required=True)
        parser.add_argument("--anchor-output", required=True)
        args = parser.parse_args(argv)
        if not args.fixture:
            raise ValueError
        package = _existing_package_directory(args.package)
        projection, manifest, contents = _fixture_context(
            domain=args.domain,
            execution_head=args.execution_head,
            package=package,
        )
        result = run_sealed_evidence_anchor_v01(
            expected_domain=args.domain,
            package_directory=package,
            domain_projection=projection,
            manifest=manifest,
            ordered_safe_contents=contents,
            publication_base_head=args.publication_base_head,
            anchor_output_file=args.anchor_output,
            fixture_disposable=True,
        )
        _sys.stdout.write(_safe_json_line(result.summary) + "\n")
        return 0
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
