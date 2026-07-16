"""Explicit read-only filesystem runner for Airline sealed-trace Replay.

This performs deterministic sealed-trace reconstruction, not transaction
re-execution. It performs no package discovery, semantic or Corridor rerun,
Ledger or Crypto recollection, direct B2b verification, direct timeline build,
or direct pure-Replay verification. It runs exactly one Ledger audit and one
C1 collection, calls no provider/network/Gemini, creates no authority,
permission, action, packet, receipt, or FinalOutput, and has no real-world
effect or Root Attestation. Output remains outside the sealed package. This is
Airline-domain integration, not universal Hedgehog OS core.
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence

from demo import run_airline_transaction_artifact_ledger_audit_v01 as ledger_audit
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_collector_v01 as replay_collector
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "run_airline_sealed_trace_replay_v01"
SLICE_ID = "airline_sealed_trace_replay_v01_slice_c2"
STATUS_PASS = replay_contracts.STATUS_PASS
STATUS_FAIL_CLOSED = replay_contracts.STATUS_FAIL_CLOSED

CRITICAL_FILE_REFS = crypto_contracts.REQUIRED_SOURCE_FILE_REFS + (
    replay_contracts.MANIFEST_ARTIFACT_REF,
    replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
)

ANCHOR_DOCUMENT_FIELD_NAMES = (
    "anchor_active_only_when_committed",
    "anchor_document_id",
    "anchor_version",
    "anchored_pass_claimed",
    "canonicalization_profile_id",
    "chain_tail_hash",
    "document_status",
    "expected_manifest_core_hash",
    "external_anchor_supplied_at_publication",
    "external_anchor_verified_at_publication",
    "hash_algorithm",
    "hash_encoding",
    "ledger_id",
    "manifest_artifact_ref",
    "next_gate",
    "package_generation_base_head",
    "publication_slice",
    "real_world_effects_count",
    "replay_allowed",
    "signature_mode",
    "signature_verified",
    "source_package_hash",
    "source_package_ref",
    "source_package_relpath",
    "transaction_id",
    "verification_artifact_ref",
    "verification_status_at_publication",
)

REASON_PACKAGE_DIRECTORY_INVALID = "replay_runner_package_directory_invalid"
REASON_PACKAGE_DIRECTORY_SYMLINK = "replay_runner_package_directory_symlink"
REASON_CRITICAL_FILE_MISSING = "replay_runner_critical_file_missing"
REASON_CRITICAL_FILE_SYMLINK = "replay_runner_critical_file_symlink"
REASON_CRITICAL_FILE_NOT_REGULAR = "replay_runner_critical_file_not_regular"
REASON_CRITICAL_FILE_UNREADABLE = "replay_runner_critical_file_unreadable"
REASON_PACKAGE_SNAPSHOT_BUILD_FAILED = "replay_runner_package_snapshot_build_failed"
REASON_ANCHOR_PATH_INVALID = "replay_runner_anchor_path_invalid"
REASON_ANCHOR_PATH_SYMLINK = "replay_runner_anchor_path_symlink"
REASON_ANCHOR_NOT_REGULAR = "replay_runner_anchor_not_regular"
REASON_ANCHOR_UNREADABLE = "replay_runner_anchor_unreadable"
REASON_ANCHOR_PARSE_FAILED = "replay_runner_anchor_parse_failed"
REASON_ANCHOR_FIELD_MISMATCH = "replay_runner_anchor_field_mismatch"
REASON_ANCHOR_CONTRACT_MISMATCH = "replay_runner_anchor_contract_mismatch"
REASON_ANCHOR_INSIDE_PACKAGE = "replay_runner_anchor_inside_package"
REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH = "replay_runner_anchor_package_identity_mismatch"
REASON_LEDGER_AUDIT_FAILED = "replay_runner_ledger_audit_failed"
REASON_LEDGER_AUDIT_REPORT_INVALID = "replay_runner_ledger_audit_report_invalid"
REASON_ACCEPTED_AUDIT_BUILD_FAILED = "replay_runner_accepted_audit_build_failed"
REASON_REPLAY_COLLECTION_FAILED = "replay_runner_collection_failed"
REASON_OUTPUT_PATH_INVALID = "replay_runner_output_path_invalid"
REASON_OUTPUT_INSIDE_PACKAGE = "replay_runner_output_inside_package"
REASON_OUTPUT_PARENT_INVALID = "replay_runner_output_parent_invalid"
REASON_OUTPUT_ALREADY_EXISTS = "replay_runner_output_already_exists"
REASON_OUTPUT_SYMLINK = "replay_runner_output_symlink"
REASON_OUTPUT_SERIALIZATION_FAILED = "replay_runner_output_serialization_failed"
REASON_OUTPUT_OPEN_FAILED = "replay_runner_output_open_failed"
REASON_OUTPUT_WRITE_FAILED = "replay_runner_output_write_failed"
REASON_OUTPUT_CLOSE_FAILED = "replay_runner_output_close_failed"
REASON_OUTPUT_REREAD_FAILED = "replay_runner_output_reread_failed"
REASON_OUTPUT_CONTENT_MISMATCH = "replay_runner_output_content_mismatch"
REASON_OUTPUT_CLEANUP_FAILED = "replay_runner_output_cleanup_failed"

REPLAY_RUNNER_REASON_ALLOWLIST = (
    REASON_PACKAGE_DIRECTORY_INVALID,
    REASON_PACKAGE_DIRECTORY_SYMLINK,
    REASON_CRITICAL_FILE_MISSING,
    REASON_CRITICAL_FILE_SYMLINK,
    REASON_CRITICAL_FILE_NOT_REGULAR,
    REASON_CRITICAL_FILE_UNREADABLE,
    REASON_PACKAGE_SNAPSHOT_BUILD_FAILED,
    REASON_ANCHOR_PATH_INVALID,
    REASON_ANCHOR_PATH_SYMLINK,
    REASON_ANCHOR_NOT_REGULAR,
    REASON_ANCHOR_UNREADABLE,
    REASON_ANCHOR_PARSE_FAILED,
    REASON_ANCHOR_FIELD_MISMATCH,
    REASON_ANCHOR_CONTRACT_MISMATCH,
    REASON_ANCHOR_INSIDE_PACKAGE,
    REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH,
    REASON_LEDGER_AUDIT_FAILED,
    REASON_LEDGER_AUDIT_REPORT_INVALID,
    REASON_ACCEPTED_AUDIT_BUILD_FAILED,
    REASON_REPLAY_COLLECTION_FAILED,
    REASON_OUTPUT_PATH_INVALID,
    REASON_OUTPUT_INSIDE_PACKAGE,
    REASON_OUTPUT_PARENT_INVALID,
    REASON_OUTPUT_ALREADY_EXISTS,
    REASON_OUTPUT_SYMLINK,
    REASON_OUTPUT_SERIALIZATION_FAILED,
    REASON_OUTPUT_OPEN_FAILED,
    REASON_OUTPUT_WRITE_FAILED,
    REASON_OUTPUT_CLOSE_FAILED,
    REASON_OUTPUT_REREAD_FAILED,
    REASON_OUTPUT_CONTENT_MISMATCH,
    REASON_OUTPUT_CLEANUP_FAILED,
)

_REPORT_ZERO_COUNTER_FIELDS = (
    "transaction_rerun_count",
    "semantic_rerun_count",
    "corridor_rerun_count",
    "ledger_recollection_count",
    "crypto_collection_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "replay_created_authority_count",
    "replay_created_permission_count",
    "replay_created_action_count",
    "replay_created_packet_count",
    "replay_created_receipt_count",
    "replay_created_final_output_count",
    "real_world_effects_count",
)


class _ReplayRunnerCliArgumentError(Exception):
    pass


class _ReplayRunnerArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _ReplayRunnerCliArgumentError() from None


@dataclass(frozen=True)
class _InvocationOwnedOutputV01:
    st_dev: int
    st_ino: int


def _raise(reason: str) -> None:
    actual = reason if reason in REPLAY_RUNNER_REASON_ALLOWLIST else REASON_REPLAY_COLLECTION_FAILED
    raise ValueError(actual) from None


def _stable_reason(error: Exception, fallback: str) -> str:
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in REPLAY_RUNNER_REASON_ALLOWLIST
    ):
        return error.args[0]
    return fallback


def _path_input(value: object, reason: str) -> Path:
    if not (type(value) is str or isinstance(value, Path)):
        _raise(reason)
    text = str(value)
    if not text or "\x00" in text:
        _raise(reason)
    return Path(text)


def _inside(path: Path, package_dir: Path) -> bool:
    return path == package_dir or package_dir in path.parents


def _package_directory(value: object) -> Path:
    path = _path_input(value, REASON_PACKAGE_DIRECTORY_INVALID)
    try:
        mode = path.lstat().st_mode
    except OSError:
        _raise(REASON_PACKAGE_DIRECTORY_INVALID)
    if stat.S_ISLNK(mode):
        _raise(REASON_PACKAGE_DIRECTORY_SYMLINK)
    if not stat.S_ISDIR(mode):
        _raise(REASON_PACKAGE_DIRECTORY_INVALID)
    try:
        return path.resolve(strict=True)
    except OSError:
        _raise(REASON_PACKAGE_DIRECTORY_INVALID)


def _open_readonly(path: Path, flags: int) -> int:
    return os.open(path, flags)


def _read_fd_chunk(fd: int, size: int) -> bytes:
    return os.read(fd, size)


def _close_read_fd(fd: int) -> None:
    os.close(fd)


def _raw_close_fd(fd: int) -> None:
    os.close(fd)


def _fd_is_closed(fd: int) -> bool:
    try:
        os.fstat(fd)
    except OSError as error:
        return error.errno == errno.EBADF
    except Exception:
        return False
    return False


def _close_fd_proven(
    fd: int,
    close_seam: object,
    raw_close_seam: object,
) -> bool:
    try:
        close_seam(fd)  # type: ignore[operator]
    except Exception:
        pass
    if _fd_is_closed(fd):
        return True
    try:
        raw_close_seam(fd)  # type: ignore[operator]
    except OSError as error:
        return error.errno == errno.EBADF
    except Exception:
        return False
    return _fd_is_closed(fd)


def _read_exact_regular_file(
    path: Path,
    *,
    missing_reason: str,
    symlink_reason: str,
    not_regular_reason: str,
    unreadable_reason: str,
) -> bytes:
    try:
        before = path.lstat()
    except FileNotFoundError:
        _raise(missing_reason)
    except OSError:
        _raise(unreadable_reason)
    if stat.S_ISLNK(before.st_mode):
        _raise(symlink_reason)
    if not stat.S_ISREG(before.st_mode):
        _raise(not_regular_reason)

    flags = os.O_RDONLY
    nofollow_available = hasattr(os, "O_NOFOLLOW")
    if nofollow_available:
        flags |= os.O_NOFOLLOW
    fd: int | None = None
    read_succeeded = False
    exact_bytes = b""
    try:
        opened_fd = _open_readonly(path, flags)
        if type(opened_fd) is not int or opened_fd < 0:
            _raise(unreadable_reason)
        fd = opened_fd
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            _raise(not_regular_reason)
        if (
            before.st_dev != opened.st_dev
            or before.st_ino != opened.st_ino
        ):
            _raise(symlink_reason)
        chunks: list[bytes] = []
        while True:
            chunk = _read_fd_chunk(fd, 65536)
            if type(chunk) is not bytes:
                _raise(unreadable_reason)
            if not chunk:
                break
            chunks.append(chunk)
        after = path.lstat()
        if (
            stat.S_ISLNK(after.st_mode)
            or not stat.S_ISREG(after.st_mode)
            or after.st_dev != opened.st_dev
            or after.st_ino != opened.st_ino
        ):
            _raise(symlink_reason)
        exact_bytes = b"".join(chunks)
        read_succeeded = True
    except FileNotFoundError:
        _raise(missing_reason)
    except ValueError:
        raise
    except OSError as error:
        if error.errno in (errno.ELOOP,):
            _raise(symlink_reason)
        if error.errno == errno.ENOENT:
            _raise(missing_reason)
        _raise(unreadable_reason)
    except Exception:
        _raise(unreadable_reason)
    finally:
        if fd is not None and not _close_fd_proven(
            fd,
            _close_read_fd,
            _raw_close_fd,
        ):
            read_succeeded = False
    if not read_succeeded:
        _raise(unreadable_reason)
    return exact_bytes


def _read_critical_files(package_dir: Path) -> tuple[tuple[str, bytes], ...]:
    rows: list[tuple[str, bytes]] = []
    for relative_ref in CRITICAL_FILE_REFS:
        path = package_dir / relative_ref
        rows.append((
            relative_ref,
            _read_exact_regular_file(
                path,
                missing_reason=REASON_CRITICAL_FILE_MISSING,
                symlink_reason=REASON_CRITICAL_FILE_SYMLINK,
                not_regular_reason=REASON_CRITICAL_FILE_NOT_REGULAR,
                unreadable_reason=REASON_CRITICAL_FILE_UNREADABLE,
            ),
        ))
    return tuple(rows)


def _anchor_bytes(value: object, package_dir: Path) -> tuple[Path, bytes]:
    path = _path_input(value, REASON_ANCHOR_PATH_INVALID)
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        _raise(REASON_ANCHOR_PATH_INVALID)
    except OSError:
        _raise(REASON_ANCHOR_UNREADABLE)
    if stat.S_ISLNK(mode):
        _raise(REASON_ANCHOR_PATH_SYMLINK)
    if not stat.S_ISREG(mode):
        _raise(REASON_ANCHOR_NOT_REGULAR)
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        _raise(REASON_ANCHOR_PATH_INVALID)
    if _inside(resolved, package_dir):
        _raise(REASON_ANCHOR_INSIDE_PACKAGE)
    return resolved, _read_exact_regular_file(
        path,
        missing_reason=REASON_ANCHOR_PATH_INVALID,
        symlink_reason=REASON_ANCHOR_PATH_SYMLINK,
        not_regular_reason=REASON_ANCHOR_NOT_REGULAR,
        unreadable_reason=REASON_ANCHOR_UNREADABLE,
    )


def _output_target(value: object, package_dir: Path) -> Path:
    path = _path_input(value, REASON_OUTPUT_PATH_INVALID)
    try:
        mode = path.lstat().st_mode
    except NotADirectoryError:
        _raise(REASON_OUTPUT_PARENT_INVALID)
    except FileNotFoundError:
        mode = None
    except OSError:
        _raise(REASON_OUTPUT_PATH_INVALID)
    if mode is not None:
        if stat.S_ISLNK(mode):
            _raise(REASON_OUTPUT_SYMLINK)
        _raise(REASON_OUTPUT_ALREADY_EXISTS)
    parent = path.parent
    try:
        parent_mode = parent.lstat().st_mode
    except OSError:
        _raise(REASON_OUTPUT_PARENT_INVALID)
    if stat.S_ISLNK(parent_mode) or not stat.S_ISDIR(parent_mode):
        _raise(REASON_OUTPUT_PARENT_INVALID)
    try:
        resolved_parent = parent.resolve(strict=True)
    except OSError:
        _raise(REASON_OUTPUT_PARENT_INVALID)
    resolved = resolved_parent / path.name
    if _inside(resolved_parent, package_dir) or _inside(resolved, package_dir):
        _raise(REASON_OUTPUT_INSIDE_PACKAGE)
    return resolved


def _valid_hex_head(value: object) -> bool:
    return (
        type(value) is str
        and 7 <= len(value) <= 40
        and all(character in "0123456789abcdef" for character in value)
    )


def _parse_anchor(raw: bytes) -> dict[str, object]:
    try:
        anchor = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(raw)
    except Exception:
        _raise(REASON_ANCHOR_PARSE_FAILED)
    if frozenset(anchor) != frozenset(ANCHOR_DOCUMENT_FIELD_NAMES):
        _raise(REASON_ANCHOR_FIELD_MISMATCH)
    relpath = anchor["source_package_relpath"]
    relparts = relpath.split("/") if type(relpath) is str else ()
    relpath_valid = bool(
        type(relpath) is str
        and relpath
        and not PurePosixPath(relpath).is_absolute()
        and relparts
        and all(part not in ("", ".", "..") for part in relparts)
        and PurePosixPath(relpath).name == anchor["source_package_ref"]
    )
    hashes_valid = all(
        crypto_contracts.validate_sha256_hex_v01(anchor[name]).validation_status
        == STATUS_PASS
        for name in (
            "expected_manifest_core_hash",
            "chain_tail_hash",
            "source_package_hash",
        )
    )
    contract_valid = (
        anchor["anchor_document_id"] == "airline_crypto_artifact_seal_anchor_v01"
        and anchor["anchor_version"] == "v0.1"
        and anchor["document_status"] == "ANCHOR_PUBLICATION"
        and anchor["anchor_active_only_when_committed"] is True
        and anchor["anchored_pass_claimed"] is False
        and anchor["canonicalization_profile_id"] == crypto_contracts.CANONICALIZATION_PROFILE_ID
        and anchor["hash_algorithm"] == crypto_contracts.HASH_ALGORITHM
        and anchor["hash_encoding"] == crypto_contracts.HASH_ENCODING
        and hashes_valid
        and crypto_contracts.validate_airline_crypto_source_package_ref_v01(
            anchor["source_package_ref"]
        ).validation_status == STATUS_PASS
        and type(anchor["transaction_id"]) is str
        and bool(anchor["transaction_id"])
        and type(anchor["ledger_id"]) is str
        and bool(anchor["ledger_id"])
        and anchor["manifest_artifact_ref"] == replay_contracts.MANIFEST_ARTIFACT_REF
        and anchor["verification_artifact_ref"] == replay_contracts.STORED_VERIFICATION_ARTIFACT_REF
        and anchor["publication_slice"] == "airline_crypto_artifact_seal_v01_slice_e1"
        and anchor["next_gate"] == "airline_crypto_artifact_seal_v01_slice_e2_anchored_audit"
        and anchor["verification_status_at_publication"] == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        and anchor["external_anchor_supplied_at_publication"] is False
        and anchor["external_anchor_verified_at_publication"] is False
        and anchor["signature_mode"] == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
        and anchor["signature_verified"] is False
        and type(anchor["real_world_effects_count"]) is int
        and anchor["real_world_effects_count"] == 0
        and anchor["replay_allowed"] is False
        and relpath_valid
        and _valid_hex_head(anchor["package_generation_base_head"])
    )
    if not contract_valid:
        _raise(REASON_ANCHOR_CONTRACT_MISMATCH)
    return anchor


def _snapshot(
    rows: tuple[tuple[str, bytes], ...],
    source_package_ref: str,
) -> replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
    try:
        snapshot = replay_contracts.build_airline_sealed_trace_replay_package_snapshot_v01(
            source_package_ref=source_package_ref,
            ordered_source_files=rows[:9],
            manifest_artifact_ref=replay_contracts.MANIFEST_ARTIFACT_REF,
            manifest_bytes=rows[9][1],
            stored_verification_artifact_ref=replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
            stored_verification_bytes=rows[10][1],
        )
        valid = replay_contracts.validate_airline_sealed_trace_replay_package_snapshot_v01(
            snapshot
        ).validation_status == STATUS_PASS
    except Exception:
        valid = False
        snapshot = None
    if not valid:
        _raise(REASON_PACKAGE_SNAPSHOT_BUILD_FAILED)
    return snapshot


def _prebind(anchor: Mapping[str, object], manifest_bytes: bytes, package_dir: Path) -> None:
    try:
        manifest = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(manifest_bytes)
    except Exception:
        _raise(REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH)
    if frozenset(manifest) != frozenset(("manifest_core", "manifest_core_hash", "signature")):
        _raise(REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH)
    core = manifest.get("manifest_core")
    if type(core) is not dict:
        _raise(REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH)
    if not (
        package_dir.name == anchor["source_package_ref"]
        and anchor["source_package_ref"] == core.get("source_package_ref")
        and anchor["transaction_id"] == core.get("transaction_id")
        and anchor["ledger_id"] == core.get("ledger_id")
        and anchor["expected_manifest_core_hash"] == manifest["manifest_core_hash"]
        and anchor["source_package_hash"] == core.get("source_package_hash")
        and anchor["chain_tail_hash"] == core.get("chain_tail_hash")
    ):
        _raise(REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH)


def _audit_valid(report: object, package_dir: Path) -> bool:
    try:
        return bool(
            type(report) is ledger_audit.AirlineTransactionArtifactLedgerAuditReportV01
            and report.final_status == ledger_audit.PASS
            and Path(report.source_artifact_dir).resolve(strict=True) == package_dir
            and report.required_source_files == crypto_contracts.REQUIRED_SOURCE_FILE_REFS
            and type(report.files_read_count) is int
            and report.files_read_count == 9
            and report.validation_errors == ()
            and report.stored_validation_status == STATUS_PASS
            and report.stored_validation_errors == ()
            and (report.actual_entry_count, report.actual_dependency_edge_count, report.actual_root_final_count) == (19, 29, 3)
            and (report.client_root_final_count, report.airline_root_final_count, report.bank_root_final_count) == (1, 1, 1)
            and all(type(getattr(report, name)) is bool and getattr(report, name) is True for name in crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS)
            and all(type(getattr(report, name)) is int and getattr(report, name) == 0 for name in ledger_audit.ZERO_COUNTER_FIELDS)
            and type(report.timeline_rows) is tuple
            and len(report.timeline_rows) == 19
            and tuple(row.ledger_index for row in report.timeline_rows) == tuple(range(19))
            and tuple(row.artifact_type for row in report.timeline_rows) == ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
        )
    except Exception:
        return False


def _accepted_audit(report: object) -> crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    try:
        values = {name: getattr(report, name) for name in crypto_collector.ACCEPTED_AUDIT_FIELD_NAMES}
        accepted = crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(**values)
        valid = crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
            accepted
        ).validation_status == STATUS_PASS
    except Exception:
        valid = False
        accepted = None
    if not valid:
        _raise(REASON_ACCEPTED_AUDIT_BUILD_FAILED)
    return accepted


def _report_valid(report: object, anchor: Mapping[str, object]) -> bool:
    try:
        return bool(
            type(report) is replay_contracts.AirlineSealedTraceReplayReportV01
            and replay_contracts.validate_airline_sealed_trace_replay_report_v01(report).validation_status == STATUS_PASS
            and report.replay_status == STATUS_PASS
            and report.source_package_ref == anchor["source_package_ref"]
            and report.transaction_id == anchor["transaction_id"]
            and report.ledger_id == anchor["ledger_id"]
            and report.manifest_core_hash == anchor["expected_manifest_core_hash"]
            and report.expected_manifest_core_hash == anchor["expected_manifest_core_hash"]
            and report.stored_verification_status == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            and report.fresh_anchored_verification_status == STATUS_PASS
            and report.external_anchor_supplied is True
            and report.external_anchor_verified is True
            and report.signature_mode == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and report.signature_verified is False
            and report.source_bytes_unchanged is True
            and report.critical_package_bytes_unchanged is True
            and (report.ledger_entry_count, report.dependency_edge_count, report.root_final_count) == (19, 29, 3)
            and report.timeline_row_count == 19
            and (report.source_file_count, report.critical_package_file_count) == (9, 11)
            and report.ledger_audit_count == 1
            and report.anchored_verification_count == 1
            and report.post_replay_snapshot_provider_call_count == 1
            and report.root_attestation_required is False
            and report.root_attestation_present is False
            and all(type(getattr(report, name)) is int and getattr(report, name) == 0 for name in _REPORT_ZERO_COUNTER_FIELDS)
        )
    except Exception:
        return False


def _serialize_plain_report(plain: dict[str, object]) -> bytes:
    return json.dumps(
        plain,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def _parse_output_document(raw: bytes) -> dict[str, object]:
    return crypto_contracts.parse_airline_crypto_json_object_bytes_v01(raw)


def _serialize_report(report: replay_contracts.AirlineSealedTraceReplayReportV01) -> tuple[dict[str, object], bytes]:
    try:
        if replay_contracts.validate_airline_sealed_trace_replay_report_v01(report).validation_status != STATUS_PASS:
            _raise(REASON_OUTPUT_SERIALIZATION_FAILED)
        plain = replay_contracts.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
        raw = _serialize_plain_report(plain)
        parsed = _parse_output_document(raw)
        valid = raw.endswith(b"\n") and not raw.endswith(b"\n\n") and parsed == plain
    except Exception:
        valid = False
        plain = {}
        raw = b""
    if not valid:
        _raise(REASON_OUTPUT_SERIALIZATION_FAILED)
    return plain, raw


def _exclusive_open(path: Path) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path, flags, 0o600)


def _write_output(fd: int, raw: bytes) -> int:
    return os.write(fd, raw)


def _flush_output(fd: int) -> None:
    os.fsync(fd)


def _close_output(fd: int) -> None:
    os.close(fd)


def _raw_close_output(fd: int) -> None:
    os.close(fd)


def _output_ownership_from_fd(fd: int) -> _InvocationOwnedOutputV01:
    opened = os.fstat(fd)
    if (
        not stat.S_ISREG(opened.st_mode)
        or type(opened.st_dev) is not int
        or type(opened.st_ino) is not int
    ):
        raise OSError(errno.EINVAL, "invalid owned output")
    return _InvocationOwnedOutputV01(
        st_dev=opened.st_dev,
        st_ino=opened.st_ino,
    )


def _owned_output_path_matches(
    path: Path,
    ownership: _InvocationOwnedOutputV01,
) -> bool:
    try:
        observed = path.lstat()
    except Exception:
        return False
    return bool(
        stat.S_ISREG(observed.st_mode)
        and not stat.S_ISLNK(observed.st_mode)
        and observed.st_dev == ownership.st_dev
        and observed.st_ino == ownership.st_ino
    )


def _open_owned_output_for_read(
    path: Path,
    ownership: _InvocationOwnedOutputV01,
) -> int:
    if not _owned_output_path_matches(path, ownership):
        raise OSError(errno.ESTALE, "owned output path mismatch")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    opened = os.fstat(fd)
    if (
        not stat.S_ISREG(opened.st_mode)
        or opened.st_dev != ownership.st_dev
        or opened.st_ino != ownership.st_ino
    ):
        os.close(fd)
        raise OSError(errno.ESTALE, "owned output identity mismatch")
    return fd


def _reread_output(
    path: Path,
    ownership: _InvocationOwnedOutputV01,
) -> bytes:
    fd: int | None = None
    succeeded = False
    chunks: list[bytes] = []
    try:
        fd = _open_owned_output_for_read(path, ownership)
        while True:
            chunk = _read_fd_chunk(fd, 65536)
            if type(chunk) is not bytes:
                raise OSError(errno.EIO, "malformed reread")
            if not chunk:
                break
            chunks.append(chunk)
        if not _owned_output_path_matches(path, ownership):
            raise OSError(errno.ESTALE, "owned output replaced")
        succeeded = True
    finally:
        if fd is not None and not _close_fd_proven(
            fd,
            _close_read_fd,
            _raw_close_fd,
        ):
            succeeded = False
    if not succeeded:
        raise OSError(errno.EIO, "owned output reread failed")
    return b"".join(chunks)


def _unlink_owned_output(
    path: Path,
    ownership: _InvocationOwnedOutputV01,
) -> None:
    if not _owned_output_path_matches(path, ownership):
        raise OSError(errno.ESTALE, "owned output path mismatch")
    os.unlink(path)


def _close_owned_output(fd: int) -> bool:
    return _close_fd_proven(fd, _close_output, _raw_close_output)


def _cleanup_owned_output(
    path: Path,
    fd: int | None,
    ownership: _InvocationOwnedOutputV01,
) -> bool:
    descriptor_closed = fd is None or _close_owned_output(fd)
    if not descriptor_closed:
        return False
    try:
        _unlink_owned_output(path, ownership)
        return True
    except Exception:
        return False


def _fail_owned_output(
    path: Path,
    fd: int | None,
    ownership: _InvocationOwnedOutputV01,
    reason: str,
) -> None:
    if not _cleanup_owned_output(path, fd, ownership):
        _raise(REASON_OUTPUT_CLEANUP_FAILED)
    _raise(reason)


def _write_report(path: Path, plain: dict[str, object], raw: bytes) -> None:
    fd: int | None = None
    ownership: _InvocationOwnedOutputV01 | None = None
    try:
        fd = _exclusive_open(path)
    except OSError as error:
        if error.errno == errno.EEXIST:
            _raise(REASON_OUTPUT_ALREADY_EXISTS)
        _raise(REASON_OUTPUT_OPEN_FAILED)
    try:
        ownership = _output_ownership_from_fd(fd)
    except Exception:
        if not _close_owned_output(fd):
            _raise(REASON_OUTPUT_CLEANUP_FAILED)
        _raise(REASON_OUTPUT_CLEANUP_FAILED)
    try:
        written = _write_output(fd, raw)
    except Exception:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_WRITE_FAILED,
        )
    if type(written) is not int or written != len(raw):
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_WRITE_FAILED,
        )
    try:
        _flush_output(fd)
    except Exception:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_WRITE_FAILED,
        )
    try:
        _close_output(fd)
    except Exception:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_CLOSE_FAILED,
        )
    if not _fd_is_closed(fd):
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_CLOSE_FAILED,
        )
    fd = None
    try:
        reread = _reread_output(path, ownership)
    except Exception:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_REREAD_FAILED,
        )
    if type(reread) is not bytes or reread != raw:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_CONTENT_MISMATCH,
        )
    try:
        parsed = _parse_output_document(reread)
    except Exception:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_CONTENT_MISMATCH,
        )
    if parsed != plain:
        _fail_owned_output(
            path,
            fd,
            ownership,
            REASON_OUTPUT_CONTENT_MISMATCH,
        )


def _run_impl(
    *,
    package_dir: object,
    anchor_path: object,
    output_path: object,
) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    package = _package_directory(package_dir)
    _, frozen_anchor_bytes = _anchor_bytes(anchor_path, package)
    output = _output_target(output_path, package)
    anchor = _parse_anchor(frozen_anchor_bytes)
    initial_rows = _read_critical_files(package)
    initial_snapshot = _snapshot(initial_rows, anchor["source_package_ref"])
    _prebind(anchor, initial_rows[9][1], package)

    audit_failed = False
    try:
        audit_report = ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01(
            artifact_dir=package,
            env={},
        )
    except Exception:
        audit_failed = True
        audit_report = None
    if audit_failed:
        _raise(REASON_LEDGER_AUDIT_FAILED)
    if not _audit_valid(audit_report, package):
        _raise(REASON_LEDGER_AUDIT_REPORT_INVALID)
    accepted = _accepted_audit(audit_report)

    def post_snapshot_provider() -> object:
        return _snapshot(
            _read_critical_files(package),
            anchor["source_package_ref"],
        )

    collection_failed = False
    try:
        report = replay_collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01(
            package_snapshot=initial_snapshot,
            accepted_ledger_audit=accepted,
            expected_manifest_core_hash=anchor["expected_manifest_core_hash"],
            post_replay_snapshot_provider=post_snapshot_provider,
        )
    except Exception:
        collection_failed = True
        report = None
    if collection_failed or not _report_valid(report, anchor):
        _raise(REASON_REPLAY_COLLECTION_FAILED)
    plain, raw = _serialize_report(report)
    _write_report(output, plain, raw)
    return report


def run_airline_sealed_trace_replay_v01(
    *,
    package_dir: str | Path,
    anchor_path: str | Path,
    output_path: str | Path,
) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    reason = REASON_REPLAY_COLLECTION_FAILED
    try:
        return _run_impl(
            package_dir=package_dir,
            anchor_path=anchor_path,
            output_path=output_path,
        )
    except Exception as error:
        reason = _stable_reason(error, REASON_REPLAY_COLLECTION_FAILED)
    _raise(reason)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _ReplayRunnerArgumentParser()
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--anchor-path", required=True)
    parser.add_argument("--output-path", required=True)
    try:
        args = parser.parse_args(argv)
    except _ReplayRunnerCliArgumentError:
        print(REASON_REPLAY_COLLECTION_FAILED)
        return 1
    except Exception:
        print(REASON_REPLAY_COLLECTION_FAILED)
        return 1
    try:
        report = run_airline_sealed_trace_replay_v01(
            package_dir=args.package_dir,
            anchor_path=args.anchor_path,
            output_path=args.output_path,
        )
    except ValueError as error:
        print(_stable_reason(error, REASON_REPLAY_COLLECTION_FAILED))
        return 1
    print(json.dumps({
        "replay_status": report.replay_status,
        "replay_id": report.replay_id,
        "transaction_id": report.transaction_id,
        "ledger_id": report.ledger_id,
        "timeline_row_count": report.timeline_row_count,
        "critical_package_file_count": report.critical_package_file_count,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
