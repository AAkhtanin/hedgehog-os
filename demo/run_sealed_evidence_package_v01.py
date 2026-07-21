"""Deterministic filesystem seam for disposable sealed-evidence packages.

The runner accepts validated typed evidence and explicit safe members. It does
not collect domain evidence, call providers, discover packages, publish an
Anchor, perform Replay, or execute business actions or effects.
"""

import argparse as _argparse
from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import errno as _errno
import hashlib as _hashlib
import json as _json
import math as _math
import os as _os
from pathlib import Path as _Path, PurePosixPath as _PurePosixPath
import re as _re
import stat as _stat
import sys as _sys
from types import MappingProxyType as _MappingProxyType
import unicodedata as _unicodedata

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
    STATUS_SELF_CONSISTENT_UNANCHORED,
    SafeFileRecordV01,
    SealedPackageManifestV01,
    build_safe_file_record_v01,
    build_sealed_package_manifest_v01,
    sealed_package_manifest_to_plain_dict_v01,
    validate_safe_file_record_v01,
    validate_sealed_package_manifest_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


MODULE_ID = "run_sealed_evidence_package_v01"
FIXTURE_DOMAINS = ("airline", "supplier_water_filter")
RUNNER_STATUS_FAIL_CLOSED = "FAIL_CLOSED"

_RUNNER_REASON = "sealed_evidence_package_runner_invalid"
_CLEANUP_REASON = "sealed_evidence_package_runner_cleanup_failed"
_MAX_SAFE_CONTENT_BYTES = 16 * 1024 * 1024
_RAW_CLOSE = _os.close
_RAW_FSTAT = _os.fstat
_SHA256 = _re.compile(r"^[0-9a-f]{64}$")
_SCHEMA_KEY = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:[\\/]")
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
_ABSOLUTE_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])/(?!/)[^\s]+"
)
_WINDOWS_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])[A-Za-z]:[\\/]"
)
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


class _SanitizedArgumentParser(_argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        raise ValueError

    def exit(self, status: int = 0, message: str | None = None) -> None:
        del status, message
        raise ValueError


@_dataclass(slots=True)
class _OwnedPackage:
    parent_fd: int
    root_fd: int
    root_name: str
    root_identity: tuple[int, int]
    files: dict[str, tuple[int, int]]
    directories: dict[str, tuple[int, int]]

@_dataclass(frozen=True, slots=True)
class SafeMemberInputV01:
    logical_path: str
    media_type: str
    content_bytes: bytes
    evidence_class: str
    source_record_ids: tuple[str, ...]
    terminal_newline_required: bool


@_dataclass(frozen=True, slots=True)
class DisposableFixtureContextV01:
    domain: str
    domain_projection: DomainEvidenceProjectionV01
    kernel_manifest_hash: str
    safe_members: tuple[SafeMemberInputV01, ...]


@_dataclass(frozen=True, slots=True)
class SealedEvidencePackageRunResultV01:
    domain: str
    manifest: SealedPackageManifestV01
    safe_file_records: tuple[SafeFileRecordV01, ...]
    safe_file_contents: tuple[bytes, ...]
    fixture_disposable: bool
    summary: _Mapping[str, object]


def build_disposable_fixture_context_v01(
    *,
    domain: str,
    execution_head: str,
) -> DisposableFixtureContextV01:
    try:
        if domain not in FIXTURE_DOMAINS or type(domain) is not str:
            raise ValueError
        if type(execution_head) is not str or not _re.fullmatch(
            r"[0-9a-f]{7,40}", execution_head
        ):
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
        domain_identity = build_domain_execution_identity_v01(
            programme_identity=programme,
            domain_id=domain,
            execution_head=execution_head,
            source_task_id=f"fixture:{domain}:sealed-evidence",
            run_id=f"fixture:{domain}:run-v01",
            report_id=f"fixture:{domain}:report-v01",
        )
        attempt = build_live_attempt_identity_v01(
            programme_identity=programme,
            domain_execution_identity=domain_identity,
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
            canonical_projection={
                "domain": domain,
                "kernel_manifest_hash": kernel_hash,
            },
            authority_class="evidence_only",
            owner_root_id=None,
            trace_refs=(kernel_hash,),
            created_authority_count=0,
            created_permission_count=0,
            real_world_effects_count=0,
        )
        projection = build_domain_evidence_projection_v01(
            programme_identity=programme,
            domain_execution_identity=domain_identity,
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
        if validate_domain_evidence_projection_v01(projection):
            raise ValueError
        members = _fixture_members(projection)
        return DisposableFixtureContextV01(
            domain=domain,
            domain_projection=projection,
            kernel_manifest_hash=kernel_hash,
            safe_members=members,
        )
    except Exception:
        raise ValueError(_RUNNER_REASON) from None


def run_sealed_evidence_package_v01(
    *,
    domain: str,
    domain_projection: DomainEvidenceProjectionV01,
    kernel_manifest_hash: str,
    safe_members: tuple[SafeMemberInputV01, ...],
    output_directory: str | _Path,
    fixture_disposable: bool,
) -> SealedEvidencePackageRunResultV01:
    output: _Path | None = None
    owner: _OwnedPackage | None = None
    try:
        if (
            type(domain) is not str
            or domain not in FIXTURE_DOMAINS
            or type(domain_projection) is not DomainEvidenceProjectionV01
            or validate_domain_evidence_projection_v01(domain_projection)
            or domain_projection.domain_execution_identity.domain_id != domain
            or type(kernel_manifest_hash) is not str
            or _SHA256.fullmatch(kernel_manifest_hash) is None
            or type(safe_members) is not tuple
            or not safe_members
            or any(type(item) is not SafeMemberInputV01 for item in safe_members)
            or type(fixture_disposable) is not bool
            or fixture_disposable
            is not _projection_is_disposable_fixture(domain_projection)
        ):
            raise ValueError
        output = _absent_output_directory(output_directory)
        _validate_member_inventory(safe_members)
        records: list[SafeFileRecordV01] = []
        contents: list[bytes] = []
        for member in safe_members:
            _scan_safe_content(
                member.content_bytes,
                media_type=member.media_type,
                terminal_newline_required=member.terminal_newline_required,
            )
            record = build_safe_file_record_v01(
                logical_path=member.logical_path,
                media_type=member.media_type,
                content_bytes=member.content_bytes,
                evidence_class=member.evidence_class,
                source_record_ids=member.source_record_ids,
                terminal_newline_required=member.terminal_newline_required,
                secret_scan_passed=True,
            )
            if validate_safe_file_record_v01(
                record,
                content_bytes=member.content_bytes,
            ):
                raise ValueError
            records.append(record)
            contents.append(bytes(member.content_bytes))
        record_tuple = tuple(records)
        content_tuple = tuple(contents)
        manifest = build_sealed_package_manifest_v01(
            domain_projection=domain_projection,
            safe_file_records=record_tuple,
            safe_file_contents=content_tuple,
            kernel_manifest_hash=kernel_manifest_hash,
        )
        if (
            validate_sealed_package_manifest_v01(
                manifest,
                domain_projection=domain_projection,
                safe_file_contents=content_tuple,
            )
            or manifest.package_status != STATUS_SELF_CONSISTENT_UNANCHORED
        ):
            raise ValueError
        manifest_plain = sealed_package_manifest_to_plain_dict_v01(
            manifest,
            domain_projection=domain_projection,
            safe_file_contents=content_tuple,
        )
        owner = _create_owned_package(output)
        for member in safe_members:
            _write_package_file(owner, member.logical_path, member.content_bytes)
        manifest_bytes = canonical_json_bytes_v01(manifest_plain) + b"\n"
        _write_package_file(owner, MANIFEST_FILENAME, manifest_bytes)
        _validate_package_directory(
            package_directory=output,
            domain_projection=domain_projection,
            manifest=manifest,
            ordered_safe_contents=content_tuple,
            owned_package=owner,
        )
        summary = _MappingProxyType(
            {
                "artifact_count": manifest.artifact_count,
                "domain": domain,
                "file_count": manifest.file_count,
                "fixture_disposable": fixture_disposable,
                "manifest_id": manifest.manifest_id,
                "package_content_hash": manifest.package_content_hash,
                "package_status": manifest.package_status,
                "packaging_gemini_call_count": 0,
                "packaging_network_call_count": 0,
                "packaging_provider_call_count": 0,
                "real_world_effects_count": 0,
            }
        )
        result = SealedEvidencePackageRunResultV01(
            domain=domain,
            manifest=manifest,
            safe_file_records=record_tuple,
            safe_file_contents=content_tuple,
            fixture_disposable=fixture_disposable,
            summary=summary,
        )
        _release_owned_package(
            owner,
            package_directory=output,
            domain_projection=domain_projection,
            manifest=manifest,
            ordered_safe_contents=content_tuple,
        )
        owner = None
        return result
    except Exception as error:
        cleanup_failed = isinstance(error, _CleanupFailure)
        if owner is not None:
            try:
                _cleanup_owned_package(owner)
            except _CleanupFailure:
                cleanup_failed = True
        if cleanup_failed:
            raise ValueError(_CLEANUP_REASON) from None
        raise ValueError(_RUNNER_REASON) from None


def _fixture_members(
    projection: DomainEvidenceProjectionV01,
) -> tuple[SafeMemberInputV01, ...]:
    result = []
    for index, source in enumerate(projection.source_records, start=1):
        content = canonical_json_bytes_v01(
            {"source_record_id": source.source_record_id}
        ) + b"\n"
        result.append(
            SafeMemberInputV01(
                logical_path=f"evidence/{index:02d}-{source.source_type}.json",
                media_type="application/json",
                content_bytes=content,
                evidence_class=source.evidence_class,
                source_record_ids=(source.source_record_id,),
                terminal_newline_required=True,
            )
        )
    return tuple(result)


def _validate_member_inventory(members: tuple[SafeMemberInputV01, ...]) -> None:
    paths = tuple(item.logical_path for item in members)
    if paths != tuple(sorted(paths, key=lambda value: value.encode("utf-8"))):
        raise ValueError
    if len(paths) != len(set(paths)) or len(paths) != len(
        {value.casefold() for value in paths}
    ):
        raise ValueError
    normalized = tuple(_unicodedata.normalize("NFC", value) for value in paths)
    if normalized != paths or len(normalized) != len(set(normalized)):
        raise ValueError
    for path in paths:
        _validate_logical_path(path)


def _validate_logical_path(value: object) -> None:
    if (
        type(value) is not str
        or not value
        or value == MANIFEST_FILENAME
        or value.casefold() == MANIFEST_FILENAME.casefold()
        or value.startswith(("/", "\\", "//"))
        or _WINDOWS_DRIVE.match(value)
        or "\\" in value
        or _unicodedata.normalize("NFC", value) != value
    ):
        raise ValueError
    parts = value.split("/")
    if any(not part or part in (".", "..") for part in parts):
        raise ValueError
    if _PurePosixPath(value).is_absolute():
        raise ValueError


def _scan_safe_content(
    value: object,
    *,
    media_type: str,
    terminal_newline_required: bool,
) -> None:
    if (
        type(value) is not bytes
        or not value
        or len(value) > _MAX_SAFE_CONTENT_BYTES
        or type(media_type) is not str
    ):
        raise ValueError
    if b"\x00" in value or value.startswith(b"\xef\xbb\xbf") or b"\r" in value:
        raise ValueError
    text = None
    try:
        text = value.decode("utf-8", errors="strict")
    except UnicodeError:
        raise ValueError from None
    if terminal_newline_required:
        if not value.endswith(b"\n") or value.endswith(b"\n\n"):
            raise ValueError
    if media_type == "application/json":
        if not value.endswith(b"\n") or text is None:
            raise ValueError
        parsed = _strict_json_loads(text[:-1])
        _inspect_safe_json(parsed)
        if canonical_json_bytes_v01(parsed) + b"\n" != value:
            raise ValueError
    elif text is not None:
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
    token = _canonical_token(key)
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


def _canonical_token(value: str) -> str:
    normalized = _unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _inspect_public_text(value: str, *, allow_lf: bool = False) -> None:
    normalized = _unicodedata.normalize("NFKC", value).casefold()
    if (
        type(value) is not str
        or _unicodedata.normalize("NFC", value) != value
        or any(
            (
                _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
                and not (allow_lf and character == "\n")
            )
            for character in value
        )
        or _unsafe_text(value)
        or _contains_sensitive_material(normalized)
    ):
        raise ValueError


def _unsafe_text(value: str) -> bool:
    folded = value.casefold()
    security_text = _unicodedata.normalize("NFKC", value)
    return bool(
        "file://" in folded
        or "traceback" in folded
        or _ABSOLUTE_PATH.search(value)
        or _WINDOWS_PATH.search(value)
        or _UNC_PATH.search(value)
        or _re.search(r"\b0x[0-9a-f]{6,}\b", value, _re.IGNORECASE)
        or _re.search(r"<[^>\r\n]*\bobject at 0x[0-9a-f]+>", value, _re.IGNORECASE)
        or _SENSITIVE_ASSIGNMENT.search(security_text)
        or _AUTHORIZATION_CREDENTIAL.search(security_text)
    )


def _contains_sensitive_material(normalized: str) -> bool:
    compact = _canonical_token(normalized)
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


def _strict_json_loads(value: str) -> object:
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                raise ValueError
            result[key] = item
        return result

    def invalid_constant(_value: str) -> object:
        raise ValueError

    try:
        return _json.loads(
            value,
            object_pairs_hook=pairs,
            parse_constant=invalid_constant,
        )
    except (TypeError, ValueError, _json.JSONDecodeError):
        raise ValueError from None


def _absent_output_directory(value: object) -> _Path:
    if type(value) is not str and not isinstance(value, _Path):
        raise ValueError
    path = _Path(value)
    if not path.is_absolute() or ".." in path.parts or _os.path.lexists(path):
        raise ValueError
    parent_fd = _open_absolute_directory(path.parent)
    _close_proven(parent_fd)
    return path


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
        if not _stat.S_ISDIR(_os.fstat(descriptor).st_mode):
            raise ValueError
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


def _owned_entry_identity(
    descriptor: int,
    parent_fd: int,
    name: str,
    *,
    directory: bool,
    expected_identity: tuple[int, int] | None = None,
) -> tuple[int, int]:
    opened = _descriptor_status(descriptor)
    valid_type = _stat.S_ISDIR(opened.st_mode) if directory else _stat.S_ISREG(opened.st_mode)
    if not valid_type:
        raise _CleanupFailure
    identity = _identity(opened)
    entry = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    entry_type = _stat.S_ISDIR(entry.st_mode) if directory else _stat.S_ISREG(entry.st_mode)
    if (
        not entry_type
        or _identity(entry) != identity
        or (expected_identity is not None and identity != expected_identity)
    ):
        raise _CleanupFailure
    return identity


def _create_owned_package(path: _Path) -> _OwnedPackage:
    parent_fd = _open_absolute_directory(path.parent)
    root_fd = -1
    identity: tuple[int, int] | None = None
    created = False
    try:
        try:
            _os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError
        _os.mkdir(path.name, 0o700, dir_fd=parent_fd)
        created = True
        root_fd = _os.open(path.name, _directory_flags(), dir_fd=parent_fd)
        identity = _owned_entry_identity(
            root_fd,
            parent_fd,
            path.name,
            directory=True,
        )
        return _OwnedPackage(
            parent_fd=parent_fd,
            root_fd=root_fd,
            root_name=path.name,
            root_identity=identity,
            files={},
            directories={},
        )
    except Exception as error:
        cleanup_failed = isinstance(error, _CleanupFailure)
        if root_fd >= 0:
            try:
                _close_proven(root_fd)
            except _CleanupFailure:
                cleanup_failed = True
        if identity is not None:
            try:
                _rmdir_name_owned(parent_fd, path.name, identity)
            except _CleanupFailure:
                cleanup_failed = True
        elif created:
            cleanup_failed = True
        try:
            _close_proven(parent_fd)
        except _CleanupFailure:
            cleanup_failed = True
        if cleanup_failed:
            raise _CleanupFailure from None
        raise error


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


def _ensure_owned_parent(owner: _OwnedPackage, logical_path: str) -> tuple[int, str]:
    if logical_path != MANIFEST_FILENAME:
        _validate_logical_path(logical_path)
    parts = logical_path.split("/")
    descriptor = _duplicate_directory(owner.root_fd)
    prefix: list[str] = []
    try:
        for component in parts[:-1]:
            prefix.append(component)
            relative = "/".join(prefix)
            if relative not in owner.directories:
                _os.mkdir(component, 0o700, dir_fd=descriptor)
                child = _os.open(component, _directory_flags(), dir_fd=descriptor)
            else:
                child = _os.open(component, _directory_flags(), dir_fd=descriptor)
            try:
                if relative not in owner.directories:
                    owner.directories[relative] = _owned_entry_identity(
                        child,
                        descriptor,
                        component,
                        directory=True,
                    )
                _owned_entry_identity(
                    child,
                    descriptor,
                    component,
                    directory=True,
                    expected_identity=owner.directories[relative],
                )
                _close_proven(descriptor)
            except Exception as error:
                try:
                    _close_proven(child)
                except _CleanupFailure:
                    raise _CleanupFailure from None
                raise error
            descriptor = child
        return descriptor, parts[-1]
    except Exception:
        _close_proven(descriptor)
        raise


def _write_package_file(owner: _OwnedPackage, logical_path: str, content: bytes) -> None:
    parent_fd, name = _ensure_owned_parent(owner, logical_path)
    descriptor = -1
    identity: tuple[int, int] | None = None
    try:
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL
        if hasattr(_os, "O_NOFOLLOW"):
            flags |= _os.O_NOFOLLOW
        descriptor = _os.open(name, flags, 0o600, dir_fd=parent_fd)
        identity = _owned_entry_identity(
            descriptor,
            parent_fd,
            name,
            directory=False,
        )
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
            name,
            expected_size=len(content),
            expected_identity=identity,
        )
        if reread_identity != identity or reread != content:
            raise ValueError
        owner.files[logical_path] = identity
    except Exception as error:
        cleanup_failed = isinstance(error, _CleanupFailure)
        if descriptor >= 0:
            try:
                _close_proven(descriptor)
            except _CleanupFailure:
                cleanup_failed = True
        if identity is not None:
            try:
                _unlink_name_owned(parent_fd, name, identity)
            except _CleanupFailure:
                cleanup_failed = True
        else:
            cleanup_failed = True
        try:
            _close_proven(parent_fd)
        except _CleanupFailure:
            cleanup_failed = True
        if cleanup_failed:
            raise _CleanupFailure from None
        raise error
    _close_proven(parent_fd)


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
    flags = _os.O_RDONLY
    if hasattr(_os, "O_NOFOLLOW"):
        flags |= _os.O_NOFOLLOW
    descriptor = _os.open(name, flags, dir_fd=parent_fd)
    try:
        opened = _os.fstat(descriptor)
        identity = _identity(opened)
        limit = expected_size if expected_size is not None else opened.st_size
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
        while True:
            chunk = _os.read(descriptor, min(65536, limit - total + 1))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                raise ValueError
        after = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _identity(after) != identity or after.st_size != total:
            raise ValueError
        result = b"".join(chunks)
        if len(result) != limit:
            raise ValueError
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
    expected_size: int | None = None,
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
        return _read_name_at(
            parent_fd,
            parts[-1],
            expected_size=expected_size,
            expected_identity=expected_identity,
        )
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


def _expected_directories(expected_files: set[str]) -> set[str]:
    result: set[str] = set()
    for logical_path in expected_files:
        parts = logical_path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            result.add("/".join(parts[:index]))
    return result


def _inventory_at(
    root_fd: int,
    expected_files: set[str],
) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]]]:
    expected_directories = _expected_directories(expected_files)
    observed_files: set[str] = set()
    observed_directories: set[str] = set()

    file_identities: dict[str, tuple[int, int]] = {}
    directory_identities: dict[str, tuple[int, int]] = {}

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
                directory_identities[relative] = _identity(status)
                child_fd = _os.open(entry.name, _directory_flags(), dir_fd=directory_fd)
                try:
                    if _identity(_os.fstat(child_fd)) != _identity(status):
                        raise ValueError
                    visit(child_fd, relative)
                finally:
                    _close_proven(child_fd)
            elif _stat.S_ISREG(status.st_mode):
                if relative not in expected_files:
                    raise ValueError
                observed_files.add(relative)
                file_identities[relative] = _identity(status)
            else:
                raise ValueError

    visit(root_fd, "")
    if observed_files != expected_files or observed_directories != expected_directories:
        raise ValueError
    return file_identities, directory_identities


def _unlink_name_owned(parent_fd: int, name: str, identity: tuple[int, int]) -> None:
    try:
        status = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not _stat.S_ISREG(status.st_mode) or (status.st_dev, status.st_ino) != identity:
        raise _CleanupFailure
    try:
        _os.unlink(name, dir_fd=parent_fd)
    except Exception:
        raise _CleanupFailure from None
    try:
        _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except Exception:
        raise _CleanupFailure from None
    raise _CleanupFailure


def _rmdir_name_owned(parent_fd: int, name: str, identity: tuple[int, int]) -> None:
    try:
        status = _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not _stat.S_ISDIR(status.st_mode) or (status.st_dev, status.st_ino) != identity:
        raise _CleanupFailure
    try:
        _os.rmdir(name, dir_fd=parent_fd)
    except OSError:
        raise _CleanupFailure from None
    try:
        _os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except Exception:
        raise _CleanupFailure from None
    raise _CleanupFailure


def _cleanup_owned_package(owner: _OwnedPackage) -> None:
    failed = False
    try:
        opened = _os.fstat(owner.root_fd)
        if not _stat.S_ISDIR(opened.st_mode) or _identity(opened) != owner.root_identity:
            raise _CleanupFailure
    except OSError as error:
        if error.errno != _errno.EBADF:
            raise _CleanupFailure from None
        try:
            owner.root_fd = _os.open(
                owner.root_name,
                _directory_flags(),
                dir_fd=owner.parent_fd,
            )
            opened = _os.fstat(owner.root_fd)
            if _identity(opened) != owner.root_identity:
                raise _CleanupFailure
        except Exception:
            raise _CleanupFailure from None
    for logical_path, identity in reversed(tuple(owner.files.items())):
        try:
            parts = logical_path.split("/")
            parent_fd = _open_relative_directory(
                owner.root_fd,
                tuple(parts[:-1]),
                expected_directories=owner.directories,
            )
            try:
                _unlink_name_owned(parent_fd, parts[-1], identity)
            finally:
                _close_proven(parent_fd)
        except _CleanupFailure:
            failed = True
        except Exception:
            failed = True
    for logical_path, identity in sorted(
        owner.directories.items(),
        key=lambda item: item[0].count("/"),
        reverse=True,
    ):
        try:
            parts = logical_path.split("/")
            parent_fd = _open_relative_directory(
                owner.root_fd,
                tuple(parts[:-1]),
                expected_directories=owner.directories,
            )
            try:
                _rmdir_name_owned(parent_fd, parts[-1], identity)
            finally:
                _close_proven(parent_fd)
        except _CleanupFailure:
            failed = True
        except Exception:
            failed = True
    try:
        _close_proven(owner.root_fd)
    except _CleanupFailure:
        failed = True
    try:
        _rmdir_name_owned(owner.parent_fd, owner.root_name, owner.root_identity)
    except _CleanupFailure:
        failed = True
    try:
        _close_proven(owner.parent_fd)
    except _CleanupFailure:
        failed = True
    if failed:
        raise _CleanupFailure


def _release_owned_package(
    owner: _OwnedPackage,
    *,
    package_directory: _Path,
    domain_projection: DomainEvidenceProjectionV01,
    manifest: SealedPackageManifestV01,
    ordered_safe_contents: tuple[bytes, ...],
) -> None:
    _validate_package_directory(
        package_directory=package_directory,
        domain_projection=domain_projection,
        manifest=manifest,
        ordered_safe_contents=ordered_safe_contents,
        owned_package=owner,
    )
    status = _os.stat(owner.root_name, dir_fd=owner.parent_fd, follow_symlinks=False)
    opened = _os.fstat(owner.root_fd)
    if (
        not _stat.S_ISDIR(status.st_mode)
        or not _stat.S_ISDIR(opened.st_mode)
        or _identity(status) != owner.root_identity
        or _identity(opened) != owner.root_identity
    ):
        raise _CleanupFailure
    _close_proven(owner.root_fd)
    _close_proven(owner.parent_fd)


def _validate_package_directory(
    *,
    package_directory: _Path,
    domain_projection: DomainEvidenceProjectionV01,
    manifest: SealedPackageManifestV01,
    ordered_safe_contents: tuple[bytes, ...],
    owned_package: _OwnedPackage | None = None,
) -> tuple[bytes, ...]:
    if not package_directory.is_absolute():
        raise ValueError
    expected = {MANIFEST_FILENAME, *(item.logical_path for item in manifest.safe_file_records)}
    root_fd = (
        _duplicate_directory(owned_package.root_fd)
        if owned_package is not None
        else _open_absolute_directory(package_directory)
    )
    try:
        root_identity = _identity(_os.fstat(root_fd))
        file_identities, directory_identities = _inventory_at(root_fd, expected)
        if owned_package is not None:
            root_entry = _os.stat(
                owned_package.root_name,
                dir_fd=owned_package.parent_fd,
                follow_symlinks=False,
            )
            if (
                root_identity != owned_package.root_identity
                or _identity(root_entry) != owned_package.root_identity
                or file_identities != owned_package.files
                or directory_identities != owned_package.directories
            ):
                raise ValueError
        reread: list[bytes] = []
        for record, supplied in zip(
            manifest.safe_file_records,
            ordered_safe_contents,
            strict=True,
        ):
            identity, content = _read_relative_file(
                root_fd,
                record.logical_path,
                expected_size=len(supplied),
                expected_identity=file_identities[record.logical_path],
                expected_directories=directory_identities,
            )
            if identity != file_identities[record.logical_path]:
                raise ValueError
            _scan_safe_content(
                content,
                media_type=record.media_type,
                terminal_newline_required=record.terminal_newline_required,
            )
            if content != supplied or validate_safe_file_record_v01(
                record,
                content_bytes=content,
            ):
                raise ValueError
            reread.append(content)
        content_tuple = tuple(reread)
        if validate_sealed_package_manifest_v01(
            manifest,
            domain_projection=domain_projection,
            safe_file_contents=content_tuple,
        ):
            raise ValueError
        manifest_plain = sealed_package_manifest_to_plain_dict_v01(
            manifest,
            domain_projection=domain_projection,
            safe_file_contents=content_tuple,
        )
        expected_manifest_bytes = canonical_json_bytes_v01(manifest_plain) + b"\n"
        manifest_identity, manifest_bytes = _read_relative_file(
            root_fd,
            MANIFEST_FILENAME,
            expected_size=len(expected_manifest_bytes),
            expected_identity=file_identities[MANIFEST_FILENAME],
            expected_directories=directory_identities,
        )
        if manifest_identity != file_identities[MANIFEST_FILENAME]:
            raise ValueError
        if (
            manifest_bytes != expected_manifest_bytes
            or _strict_json_loads(manifest_bytes.decode("utf-8")[:-1])
            != manifest_plain
        ):
            raise ValueError
        final_files, final_directories = _inventory_at(root_fd, expected)
        if final_files != file_identities or final_directories != directory_identities:
            raise ValueError
        return content_tuple
    finally:
        _close_proven(root_fd)


def _projection_is_disposable_fixture(
    projection: DomainEvidenceProjectionV01,
) -> bool:
    try:
        expected = build_disposable_fixture_context_v01(
            domain=projection.domain_execution_identity.domain_id,
            execution_head=projection.domain_execution_identity.execution_head,
        ).domain_projection
        return projection == expected
    except Exception:
        return False


def _safe_json_line(value: _Mapping[str, object]) -> str:
    return canonical_json_bytes_v01(dict(value)).decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        parser = _SanitizedArgumentParser(add_help=False)
        parser.add_argument("--fixture", action="store_true")
        parser.add_argument("--domain", choices=FIXTURE_DOMAINS, required=True)
        parser.add_argument("--execution-head", required=True)
        parser.add_argument("--output", required=True)
        args = parser.parse_args(argv)
        if not args.fixture:
            raise ValueError
        context = build_disposable_fixture_context_v01(
            domain=args.domain,
            execution_head=args.execution_head,
        )
        result = run_sealed_evidence_package_v01(
            domain=context.domain,
            domain_projection=context.domain_projection,
            kernel_manifest_hash=context.kernel_manifest_hash,
            safe_members=context.safe_members,
            output_directory=args.output,
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
        failure = {"reason": reason, "status": RUNNER_STATUS_FAIL_CLOSED}
        _sys.stdout.write(_safe_json_line(failure) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
