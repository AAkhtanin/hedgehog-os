"""Airline A2 local packageability and separated publication orchestrator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from demo import run_sealed_evidence_package_v01 as package_runner
from demo import run_sealed_evidence_anchor_v01 as anchor_runner
from demo import run_sealed_evidence_replay_v01 as replay_runner
from demo import run_two_domain_airline_all_real_program_v01 as a1_runner
from hedgehog.domains.airline import sealed_evidence_a2_binding_v01 as binding
from hedgehog.domains.airline import sealed_evidence_package_adapter_v01 as adapter


STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
LOCAL_GATE_TOKEN = "ATTEMPT_04_LOCAL_PACKAGEABILITY_GATE=PASS"
REASON_INVALID = "airline_a2_seal_runner_invalid"
OFFICIAL_ANCHOR_OUTPUT = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
    "airline_crypto_anchor_v01.json"
)
OFFICIAL_REPLAY_OUTPUT = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
    "airline_replay_report_v01.json"
)
AUTHORIZED_IMPLEMENTATION_PATHS = (
    "demo/run_tri_party_airline_live_semantic_lane_v01.py",
    "tests/test_tri_party_airline_live_semantic_lane_v01_runner.py",
    "demo/run_two_domain_airline_all_real_program_v01.py",
    "tests/test_two_domain_airline_all_real_program_v01_runner.py",
    "demo/run_sealed_evidence_package_v01.py",
    "tests/test_sealed_evidence_package_v01_runner.py",
    "hedgehog/domains/airline/sealed_evidence_a2_binding_v01.py",
    "tests/test_airline_sealed_evidence_a2_binding_v01.py",
    "demo/run_two_domain_airline_a2_seal_v01.py",
    "tests/test_two_domain_airline_a2_seal_v01_runner.py",
    "hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py",
    "tests/test_airline_sealed_evidence_package_adapter_v01.py",
)
IMPLEMENTATION_CONTENT_DOMAIN = (
    b"hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1\0"
)


class _CliFailure(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise _CliFailure


@dataclass(frozen=True, slots=True)
class AirlineA2LocalPackageabilityResultV01:
    status: str
    callbacks: str
    collector_corridor_ledger_crypto: str
    outbound_provider_network_gemini_effects: str
    hydrate_adapter_package: str
    canonical_package_index_writes: str
    package_anchor_replay_publication: str
    repository_output_count: int
    residue_count: int
    corridor_sha256: str
    corridor_sha256_equality: bool
    adapter_result_id: str
    manifest_id: str
    package_content_hash: str


def airline_a2_local_packageability_result_to_plain_dict_v01(
    result: AirlineA2LocalPackageabilityResultV01,
) -> dict[str, object]:
    if type(result) is not AirlineA2LocalPackageabilityResultV01:
        raise _CliFailure
    return {
        "ANCHOR_REPLAY": result.package_anchor_replay_publication,
        "CALLBACKS": result.callbacks,
        "CANONICAL_PACKAGE_INDEX_WRITES": result.canonical_package_index_writes,
        "COLLECTOR_CORRIDOR_LEDGER_CRYPTO": result.collector_corridor_ledger_crypto,
        "HYDRATE_ADAPTER_PACKAGE": result.hydrate_adapter_package,
        "OUTBOUND_PROVIDER_NETWORK_GEMINI_EFFECTS": (
            result.outbound_provider_network_gemini_effects
        ),
        "REPOSITORY_OUTPUT": result.repository_output_count,
        "RESIDUE": result.residue_count,
        "adapter_result_id": result.adapter_result_id,
        "corridor_sha256": result.corridor_sha256,
        "corridor_sha256_equality": result.corridor_sha256_equality,
        "manifest_id": result.manifest_id,
        "package_content_hash": result.package_content_hash,
        "status": result.status,
    }


def _local_packageability_result_from_plain_v01(
    plain: object,
) -> AirlineA2LocalPackageabilityResultV01:
    if type(plain) is not dict:
        raise _CliFailure
    expected = {
        "ANCHOR_REPLAY",
        "CALLBACKS",
        "CANONICAL_PACKAGE_INDEX_WRITES",
        "COLLECTOR_CORRIDOR_LEDGER_CRYPTO",
        "HYDRATE_ADAPTER_PACKAGE",
        "OUTBOUND_PROVIDER_NETWORK_GEMINI_EFFECTS",
        "REPOSITORY_OUTPUT",
        "RESIDUE",
        "adapter_result_id",
        "corridor_sha256",
        "corridor_sha256_equality",
        "manifest_id",
        "package_content_hash",
        "status",
    }
    if set(plain) != expected:
        raise _CliFailure
    result = AirlineA2LocalPackageabilityResultV01(
        status=plain["status"],
        callbacks=plain["CALLBACKS"],
        collector_corridor_ledger_crypto=plain["COLLECTOR_CORRIDOR_LEDGER_CRYPTO"],
        outbound_provider_network_gemini_effects=(
            plain["OUTBOUND_PROVIDER_NETWORK_GEMINI_EFFECTS"]
        ),
        hydrate_adapter_package=plain["HYDRATE_ADAPTER_PACKAGE"],
        canonical_package_index_writes=plain["CANONICAL_PACKAGE_INDEX_WRITES"],
        package_anchor_replay_publication=plain["ANCHOR_REPLAY"],
        repository_output_count=plain["REPOSITORY_OUTPUT"],
        residue_count=plain["RESIDUE"],
        corridor_sha256=plain["corridor_sha256"],
        corridor_sha256_equality=plain["corridor_sha256_equality"],
        adapter_result_id=plain["adapter_result_id"],
        manifest_id=plain["manifest_id"],
        package_content_hash=plain["package_content_hash"],
    )
    if (
        result.status != STATUS_PASS
        or result.callbacks != "12/12/12"
        or result.collector_corridor_ledger_crypto != "1/1/1/1"
        or result.outbound_provider_network_gemini_effects != "0/0/0/0"
        or result.hydrate_adapter_package != "1/1/1"
        or result.canonical_package_index_writes != "0/0"
        or result.package_anchor_replay_publication != "0/0/0"
        or result.repository_output_count != 0
        or result.residue_count != 0
        or result.corridor_sha256_equality is not True
        or any(
            type(value) is not str or len(value) != 64
            for value in (
                result.corridor_sha256,
                result.adapter_result_id,
                result.manifest_id,
                result.package_content_hash,
            )
        )
    ):
        raise _CliFailure
    return result


def _read_regular_file(path: Path, *, maximum: int = 16_000_000) -> bytes:
    if not isinstance(path, Path) or not path.is_absolute() or not path.name:
        raise _CliFailure
    directory_fd, _ = binding._open_absolute_directory(path.parent)
    try:
        return binding._read_leaf(directory_fd, path.name, maximum)
    except (OSError, TypeError, ValueError):
        raise _CliFailure from None
    finally:
        os.close(directory_fd)


def implementation_content_sha256_v01(repository_root: Path) -> str:
    digest = hashlib.sha256()
    digest.update(IMPLEMENTATION_CONTENT_DOMAIN)
    for logical_name in AUTHORIZED_IMPLEMENTATION_PATHS:
        content = _read_regular_file(repository_root / logical_name)
        name_bytes = logical_name.encode("ascii")
        digest.update(name_bytes)
        digest.update(b"\0")
        digest.update(str(len(content)).encode("ascii"))
        digest.update(b"\0")
        digest.update(content)
    return digest.hexdigest()


def _git(repository_root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=repository_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise _CliFailure
    return completed.stdout.strip()


def _ascii_positive_int(value: str) -> int:
    if (
        type(value) is not str
        or not value.isascii()
        or not value.isdecimal()
        or value.startswith("0")
    ):
        raise _CliFailure
    result = int(value)
    if result <= 0:
        raise _CliFailure
    return result


def _require_repository_root(path: Path) -> None:
    if (
        not path.is_absolute()
        or str(path) != os.path.normpath(str(path))
    ):
        raise _CliFailure
    descriptor, _ = binding._open_absolute_directory(path)
    os.close(descriptor)


def _require_git_head(
    repository_root: Path,
    expected_head: str,
    *,
    clean: bool,
) -> None:
    if (
        binding.LOWER_HEAD.fullmatch(expected_head) is None
        or _git(repository_root, "rev-parse", "HEAD") != expected_head
        or _git(repository_root, "rev-parse", "origin/main") != expected_head
        or (clean and _git(repository_root, "status", "--porcelain", "--untracked-files=all"))
    ):
        raise _CliFailure


_MODE_DESTINATIONS = frozenset(
    (
        "local_packageability",
        "package",
        "anchor",
        "replay",
        "_local_process_a",
        "_local_process_b",
    )
)


def _reject_cross_mode_arguments(
    args: argparse.Namespace,
    *,
    allowed: frozenset[str],
) -> None:
    for name, value in vars(args).items():
        if name in _MODE_DESTINATIONS or name in allowed:
            continue
        if value is not None and value is not False:
            raise _CliFailure


def _write_owned_json(path: Path, plain: dict[str, object]) -> None:
    content = binding.canonical_json_line_v01(plain)
    parent_fd, _ = binding._open_absolute_directory(path.parent)
    fd = -1
    identity: tuple[int, int] | None = None
    try:
        try:
            os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _CliFailure
        fd = os.open(
            path.name,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        opened = os.fstat(fd)
        identity = (opened.st_dev, opened.st_ino)
        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != identity
            or stat.S_IMODE(opened.st_mode) != 0o600
        ):
            raise _CliFailure
        offset = 0
        while offset < len(content):
            written = os.write(fd, content[offset:])
            if written <= 0:
                raise _CliFailure
            offset += written
        os.fsync(fd)
        os.close(fd)
        fd = -1
        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != identity
            or stat.S_IMODE(entry.st_mode) != 0o600
            or binding._read_leaf(parent_fd, path.name, len(content)) != content
        ):
            raise _CliFailure
    except Exception:
        if fd >= 0:
            os.close(fd)
        if identity is not None:
            try:
                entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                if (entry.st_dev, entry.st_ino) == identity and stat.S_ISREG(
                    entry.st_mode
                ):
                    os.unlink(path.name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
        raise _CliFailure from None
    finally:
        os.close(parent_fd)


def _create_owned_directory(path: Path) -> tuple[int, int]:
    if not path.is_absolute() or not path.name:
        raise _CliFailure
    parent_fd, _ = binding._open_absolute_directory(path.parent)
    directory_fd = -1
    try:
        try:
            os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _CliFailure
        os.mkdir(path.name, 0o700, dir_fd=parent_fd)
        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        directory_fd = os.open(
            path.name,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(directory_fd)
        identity = (opened.st_dev, opened.st_ino)
        if (
            not stat.S_ISDIR(entry.st_mode)
            or identity != (entry.st_dev, entry.st_ino)
            or stat.S_IMODE(opened.st_mode) != 0o700
        ):
            raise _CliFailure
        return identity
    except Exception:
        raise _CliFailure from None
    finally:
        if directory_fd >= 0:
            os.close(directory_fd)
        os.close(parent_fd)


def _process_a(
    *,
    repository_root: Path,
    temporary_root: Path,
    synthetic_predecessor_root: Path,
    attempt_output: Path,
    safe_report_output: Path,
    process_result_output: Path,
    gate_phase: str,
    verified_head: str,
    implementation_digest: str,
) -> None:
    if (
        not repository_root.is_absolute()
        or synthetic_predecessor_root != temporary_root / "synthetic-predecessors"
        or attempt_output != temporary_root / "attempt-04"
        or safe_report_output
        != temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME
        or process_result_output != temporary_root / "process-a-result-v01.json"
    ):
        raise _CliFailure
    _create_owned_directory(synthetic_predecessor_root)
    attempt = attempt_output
    safe_report = safe_report_output
    original_sleep = a1_runner._lane.time.sleep
    a1_runner._lane.time.sleep = lambda seconds: None
    try:
        result = a1_runner.run_two_domain_airline_all_real_program_v01(
            execution_mode=a1_runner.MODE_REAL,
            attempt_number=4,
            private_output_directory=attempt,
            injected_provider=a1_runner._build_injected_provider_v01(),
            injected_safe_report_output=safe_report,
            prior_accepted_attempt_03_id=a1_runner._ATTEMPT_03_ID,
            transitive_failed_attempt_02_id=a1_runner._ATTEMPT_02_ID,
            transitive_failed_attempt_01_id=a1_runner._PRIOR_ATTEMPT_ID,
            owner_reviewed_attempt_04=True,
            _local_packageability_injection=True,
            _local_verified_head=verified_head,
        )
    finally:
        a1_runner._lane.time.sleep = original_sleep
    if result.final_status != STATUS_PASS:
        raise _CliFailure
    identity_bytes = _read_regular_file(attempt / a1_runner.ATTEMPT_IDENTITY_FILE)
    inventory_bytes = _read_regular_file(attempt / a1_runner.PRIVATE_INVENTORY_FILE)
    gate_bytes = _read_regular_file(attempt / a1_runner.GENERATION_GATE_FILE)
    inventory = json.loads(inventory_bytes)
    row = next(
        item
        for item in inventory["ordered_files"]
        if item["logical_ref"] == a1_runner._lane.CORRIDOR_REPORT_FILE
    )
    safe_report_bytes = _read_regular_file(safe_report)
    safe_plain = json.loads(safe_report_bytes)
    safe_plain["validation_errors"] = tuple(safe_plain["validation_errors"])
    safe_execution = adapter.build_airline_safe_execution_projection_v01(safe_plain)
    process_result = binding.build_airline_a2_local_process_a_result_v01(
        gate_phase=gate_phase,
        verified_head_token=verified_head,
        implementation_content_sha256=implementation_digest,
        attempt_id=result.attempt_id,
        execution_head=result.execution_head,
        attempt_identity_sha256=hashlib.sha256(identity_bytes).hexdigest(),
        private_inventory_sha256=hashlib.sha256(inventory_bytes).hexdigest(),
        private_inventory_digest=result.private_inventory_digest,
        generation_gate_sha256=hashlib.sha256(gate_bytes).hexdigest(),
        corridor_archive_sha256=row["sha256"],
        corridor_archive_byte_count=row["byte_count"],
        safe_report_sha256=result.safe_report_sha256,
        safe_report_byte_count=len(safe_report_bytes),
        safe_execution_id=safe_execution.safe_execution_id,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        semantic_actor_call_count=12,
        causal_actor_call_count=5,
        generic_actor_call_count=7,
        duplicate_actor_call_count=0,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        outbound_provider_sdk_call_count=0,
        outbound_network_call_count=0,
        outbound_gemini_call_count=0,
        real_world_effects_count=0,
    )
    _write_owned_json(
        process_result_output,
        binding.airline_a2_local_process_a_result_to_plain_dict_v01(process_result),
    )


def _process_b(
    *,
    repository_root: Path,
    temporary_root: Path,
    attempt_directory: Path,
    safe_report_path: Path,
    process_a_result_path: Path,
    package_root: Path,
    gate_phase: str,
    verified_head: str,
    implementation_digest: str,
) -> AirlineA2LocalPackageabilityResultV01:
    if (
        not repository_root.is_absolute()
        or attempt_directory != temporary_root / "attempt-04"
        or safe_report_path
        != temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME
        or process_a_result_path != temporary_root / "process-a-result-v01.json"
        or package_root != temporary_root / "local-package"
    ):
        raise _CliFailure
    result_plain = json.loads(
        _read_regular_file(process_a_result_path)
    )
    process_result = binding.airline_a2_local_process_a_result_from_plain_dict_v01(
        result_plain
    )
    if (
        process_result.gate_phase != gate_phase
        or process_result.verified_head_token != verified_head
        or process_result.implementation_content_sha256 != implementation_digest
    ):
        raise _CliFailure
    attempt = attempt_directory
    safe_report = safe_report_path
    (
        source,
        safe_execution,
        ledger_source_bundle,
        crypto_result,
        replay_input,
        replay_report,
        kernel_result,
    ) = binding.load_airline_a2_local_nonpublication_source_v01(
        repository_root=repository_root,
        attempt_directory=attempt,
        safe_report_path=safe_report,
        expected_attempt_id=process_result.attempt_id,
        expected_execution_head=process_result.execution_head,
        expected_attempt_identity_sha256=process_result.attempt_identity_sha256,
        expected_private_inventory_sha256=process_result.private_inventory_sha256,
        expected_private_inventory_digest=process_result.private_inventory_digest,
        expected_generation_gate_sha256=process_result.generation_gate_sha256,
        expected_corridor_archive_sha256=process_result.corridor_archive_sha256,
        expected_corridor_archive_byte_count=process_result.corridor_archive_byte_count,
        expected_safe_report_sha256=process_result.safe_report_sha256,
        expected_safe_report_byte_count=process_result.safe_report_byte_count,
        expected_safe_execution_id=process_result.safe_execution_id,
        implementation_content_sha256=process_result.implementation_content_sha256,
    )
    if gate_phase == binding.GATE_PHASE_PRECOMMIT:
        invocation = binding.build_airline_a2_local_precommit_package_invocation_v01(
            base_head=verified_head,
            implementation_content_sha256=implementation_digest,
            local_source_identity_id=source.source_identity_id,
        )
    else:
        invocation = binding.build_airline_a2_local_committed_package_invocation_v01(
            committed_head=verified_head,
            origin_main_head=verified_head,
            implementation_content_sha256=implementation_digest,
            local_source_identity_id=source.source_identity_id,
        )
    ordered_source_files = tuple(
        (name, _read_regular_file(attempt / "raw_attempt" / name))
        for name in binding.crypto_collector.REQUIRED_SOURCE_FILE_REFS
    )
    material = binding.build_airline_a2_package_material_v01(
        source=source,
        package_invocation=invocation,
        safe_report_bytes=_read_regular_file(safe_report),
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        ledger_item=replay_input.ledger_item,
        crypto_collection_result=crypto_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_result,
        ordered_source_files=ordered_source_files,
    )
    source_ids = tuple(
        item.source_record_id
        for item in material.domain_projection.source_records
    )
    selections = (
        (source_ids[0],),
        (source_ids[0], source_ids[4], source_ids[5]),
        source_ids,
        source_ids,
    )
    members = tuple(
        package_runner.SafeMemberInputV01(
            logical_path=path,
            media_type="application/json",
            content_bytes=content,
            evidence_class="EXECUTED_DETERMINISTIC_RUNTIME",
            source_record_ids=selected,
            terminal_newline_required=True,
        )
        for path, content, selected in zip(
            binding._MEMBER_PATHS,
            material.member_contents,
            selections,
            strict=True,
        )
    )
    package_result = package_runner.run_sealed_evidence_package_v01(
        domain="airline",
        domain_projection=material.domain_projection,
        kernel_manifest_hash=kernel_result.kernel_manifest.manifest_hash,
        safe_members=members,
        output_directory=package_root,
        fixture_disposable=False,
    )
    if (
        package_result.manifest.manifest_id != material.manifest.manifest_id
        or package_result.manifest.package_content_hash
        != material.manifest.package_content_hash
    ):
        raise _CliFailure
    return AirlineA2LocalPackageabilityResultV01(
        status=STATUS_PASS,
        callbacks="12/12/12",
        collector_corridor_ledger_crypto="1/1/1/1",
        outbound_provider_network_gemini_effects="0/0/0/0",
        hydrate_adapter_package="1/1/1",
        canonical_package_index_writes="0/0",
        package_anchor_replay_publication="0/0/0",
        repository_output_count=0,
        residue_count=0,
        adapter_result_id=material.adapter_result_id,
        corridor_sha256=source.corridor_archive_sha256,
        corridor_sha256_equality=True,
        manifest_id=material.manifest.manifest_id,
        package_content_hash=material.manifest.package_content_hash,
    )


def _remove_owned_tree_contents(directory_fd: int) -> None:
    for name in sorted(os.listdir(directory_fd)):
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISREG(entry.st_mode):
            os.unlink(name, dir_fd=directory_fd)
            continue
        if not stat.S_ISDIR(entry.st_mode):
            raise _CliFailure
        child_fd = os.open(
            name,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        try:
            opened = os.fstat(child_fd)
            if (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino):
                raise _CliFailure
            _remove_owned_tree_contents(child_fd)
        finally:
            os.close(child_fd)
        current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != (entry.st_dev, entry.st_ino):
            raise _CliFailure
        os.rmdir(name, dir_fd=directory_fd)


def _cleanup_owned_root(root: Path, expected_identity: tuple[int, int]) -> None:
    parent_fd, _ = binding._open_absolute_directory(root.parent)
    directory_fd = -1
    try:
        entry = os.stat(root.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISDIR(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != expected_identity
        ):
            raise _CliFailure
        directory_fd = os.open(
            root.name,
            os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(directory_fd)
        if (opened.st_dev, opened.st_ino) != expected_identity:
            raise _CliFailure
        _remove_owned_tree_contents(directory_fd)
        os.close(directory_fd)
        directory_fd = -1
        current = os.stat(root.name, dir_fd=parent_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != expected_identity:
            raise _CliFailure
        os.rmdir(root.name, dir_fd=parent_fd)
    finally:
        if directory_fd >= 0:
            os.close(directory_fd)
        os.close(parent_fd)


def _cleanup_owned_file(path: Path, expected_identity: tuple[int, int]) -> None:
    parent_fd, _ = binding._open_absolute_directory(path.parent)
    try:
        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != expected_identity
        ):
            raise _CliFailure
        os.unlink(path.name, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _official_members(
    material: binding.AirlineA2PackageMaterialV01,
) -> tuple[package_runner.SafeMemberInputV01, ...]:
    return tuple(
        package_runner.SafeMemberInputV01(
            logical_path=record.logical_path,
            media_type=record.media_type,
            content_bytes=content,
            evidence_class=record.evidence_class,
            source_record_ids=record.source_record_ids,
            terminal_newline_required=record.terminal_newline_required,
        )
        for record, content in zip(
            material.safe_file_records,
            material.member_contents,
            strict=True,
        )
    )


def _run_official_package(args: argparse.Namespace) -> dict[str, object]:
    repository_root = Path(args.repository_root)
    _require_repository_root(repository_root)
    _require_git_head(
        repository_root,
        args.publication_base_head,
        clean=True,
    )
    package_root = Path(args.package_root)
    index_path = Path(args.package_index_output)
    if (
        package_root != repository_root / binding.OFFICIAL_PACKAGE_ROOT
        or index_path != repository_root / binding.OFFICIAL_PACKAGE_INDEX
        or package_root.exists()
        or package_root.is_symlink()
        or index_path.exists()
        or index_path.is_symlink()
    ):
        raise _CliFailure
    loaded = binding.load_airline_a2_official_accepted_source_v01(
        repository_root=repository_root,
        accepted_attempt_directory=Path(args.accepted_attempt_directory),
        safe_report_path=Path(args.safe_report),
        generation_audit_path=Path(args.generation_audit),
        expected_attempt_id=args.accepted_attempt_id,
        expected_execution_head=args.execution_head,
        expected_publication_base_head=args.publication_base_head,
        expected_attempt_identity_sha256=args.expected_attempt_identity_sha256,
        expected_private_inventory_sha256=args.expected_private_inventory_sha256,
        expected_private_inventory_digest=args.expected_private_inventory_digest,
        expected_generation_gate_sha256=args.expected_generation_gate_sha256,
        expected_corridor_archive_sha256=args.expected_corridor_archive_sha256,
        expected_corridor_archive_byte_count=args.expected_corridor_archive_byte_count,
        expected_safe_report_sha256=args.expected_safe_report_sha256,
        expected_safe_report_byte_count=args.expected_safe_report_byte_count,
        expected_safe_execution_id=args.expected_safe_execution_id,
        expected_generation_audit_sha256=args.expected_generation_audit_sha256,
    )
    (
        source,
        safe_execution,
        ledger_source_bundle,
        crypto_result,
        replay_input,
        replay_report,
        kernel_result,
    ) = loaded
    invocation = binding.build_airline_a2_official_package_invocation_v01(
        official_source_identity_id=source.source_identity_id,
        implementation_head=source.execution_head,
        publication_base_head=args.publication_base_head,
    )
    raw_root = Path(args.accepted_attempt_directory) / "raw_attempt"
    ordered_source_files = tuple(
        (name, _read_regular_file(raw_root / name))
        for name in binding.crypto_collector.REQUIRED_SOURCE_FILE_REFS
    )
    material = binding.build_airline_a2_package_material_v01(
        source=source,
        package_invocation=invocation,
        safe_report_bytes=_read_regular_file(Path(args.safe_report)),
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        ledger_item=replay_input.ledger_item,
        crypto_collection_result=crypto_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_result,
        ordered_source_files=ordered_source_files,
    )
    package_identity: tuple[int, int] | None = None
    index_identity: tuple[int, int] | None = None
    try:
        package_result = package_runner.run_sealed_evidence_package_v01(
            domain="airline",
            domain_projection=material.domain_projection,
            kernel_manifest_hash=kernel_result.kernel_manifest.manifest_hash,
            safe_members=_official_members(material),
            output_directory=package_root,
            fixture_disposable=False,
        )
        status = os.lstat(package_root)
        package_identity = (status.st_dev, status.st_ino)
        manifest_bytes = _read_regular_file(
            package_root / binding.sealed_package.MANIFEST_FILENAME
        )
        index = binding.build_airline_a2_safe_package_index_v01(
            source=source,
            package_invocation=invocation,
            member_03_typed_context_id=material.typed_context_id,
            member_04_adapter_projection_id=material.adapter_projection_id,
            adapter_result=material.adapter_result,
            domain_projection=material.domain_projection,
            safe_file_records=material.safe_file_records,
            manifest=package_result.manifest,
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
            manifest_byte_count=len(manifest_bytes),
        )
        _write_owned_json(
            index_path,
            binding.airline_a2_safe_package_index_to_plain_dict_v01(index),
        )
        status = os.lstat(index_path)
        index_identity = (status.st_dev, status.st_ino)
        binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=index_path,
        )
        return {
            "final_status": STATUS_PASS,
            "index_id": index.index_id,
            "manifest_id": package_result.manifest.manifest_id,
            "package_content_hash": package_result.manifest.package_content_hash,
            "package_status": package_result.manifest.package_status,
            "provider_network_gemini_effects": "0/0/0/0",
        }
    except Exception:
        if index_identity is not None:
            _cleanup_owned_file(index_path, index_identity)
        if package_identity is not None:
            _cleanup_owned_root(package_root, package_identity)
        raise _CliFailure from None


def _run_anchor(args: argparse.Namespace) -> dict[str, object]:
    repository_root = Path(args.repository_root)
    _require_repository_root(repository_root)
    _require_git_head(
        repository_root,
        args.publication_base_head,
        clean=False,
    )
    package_root = Path(args.package_root)
    package_index = Path(args.package_index)
    anchor_output = Path(args.anchor_output)
    expected_dirty = {
        f"?? {binding.OFFICIAL_PACKAGE_INDEX}",
        *(f"?? {binding.OFFICIAL_PACKAGE_ROOT}/{name}" for name in (
            "evidence/01-airline-safe-execution-report-v01.json",
            "evidence/02-airline-source-lineage-v01.json",
            "evidence/03-airline-a2-typed-context-v01.json",
            "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
            binding.sealed_package.MANIFEST_FILENAME,
        )),
    }
    observed_dirty = frozenset(
        _git(
            repository_root,
            "status",
            "--porcelain",
            "--untracked-files=all",
        ).splitlines()
    )
    if (
        package_root != repository_root / binding.OFFICIAL_PACKAGE_ROOT
        or package_index != repository_root / binding.OFFICIAL_PACKAGE_INDEX
        or anchor_output != repository_root / OFFICIAL_ANCHOR_OUTPUT
        or anchor_output.exists()
        or anchor_output.is_symlink()
        or observed_dirty != expected_dirty
    ):
        raise _CliFailure
    index, _, domain_projection, manifest, contents = (
        binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
    )
    publication = anchor_runner.build_external_anchor_publication_v01(
        manifest=manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
        publication_base_head=args.publication_base_head,
    )
    if (
        anchor_runner.validate_external_anchor_publication_v01(
            publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=contents,
        )
        or publication.anchor_status != "EVIDENCE_ONLY"
    ):
        raise _CliFailure
    plain = anchor_runner.external_anchor_publication_to_plain_dict_v01(
        publication,
        manifest=manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
    )
    _write_owned_json(anchor_output, plain)
    anchor_entry = os.lstat(anchor_output)
    anchor_identity = (anchor_entry.st_dev, anchor_entry.st_ino)
    try:
        if binding._strict_json_bytes(_read_regular_file(anchor_output)) != plain:
            raise _CliFailure
        after = binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
        if after[0] != index or after[2:] != (domain_projection, manifest, contents):
            raise _CliFailure
    except Exception:
        _cleanup_owned_file(anchor_output, anchor_identity)
        raise _CliFailure from None
    return {
        "anchor_publication_id": publication.anchor_publication_id,
        "anchor_status": publication.anchor_status,
        "final_status": STATUS_PASS,
        "provider_network_gemini_effects": "0/0/0/0",
    }


def _run_replay(args: argparse.Namespace) -> dict[str, object]:
    repository_root = Path(args.repository_root)
    _require_repository_root(repository_root)
    _require_git_head(repository_root, args.p1_head, clean=True)
    package_root = Path(args.package_root)
    package_index = Path(args.package_index)
    anchor_file = Path(args.anchor_file)
    replay_output = Path(args.replay_output)
    if (
        package_root != repository_root / binding.OFFICIAL_PACKAGE_ROOT
        or package_index != repository_root / binding.OFFICIAL_PACKAGE_INDEX
        or anchor_file != repository_root / OFFICIAL_ANCHOR_OUTPUT
        or replay_output != repository_root / OFFICIAL_REPLAY_OUTPUT
        or replay_output.exists()
        or replay_output.is_symlink()
    ):
        raise _CliFailure
    index, _, domain_projection, manifest, contents = (
        binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
    )
    anchor_bytes = _read_regular_file(anchor_file)
    publication = binding._hydrate_dataclass(
        anchor_runner.ExternalAnchorPublicationV01,
        binding._strict_json_bytes(anchor_bytes),
    )
    if anchor_runner.validate_external_anchor_publication_v01(
        publication,
        manifest=manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
    ):
        raise _CliFailure
    reconstructed_manifest = replay_runner.build_sealed_package_manifest_v01(
        domain_projection=domain_projection,
        safe_file_records=manifest.safe_file_records,
        safe_file_contents=contents,
        kernel_manifest_hash=manifest.kernel_manifest_hash,
    )
    verification = replay_runner.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=domain_projection,
        safe_file_contents=contents,
        supplied_anchor_publication_id=args.supplied_anchor_publication_id,
    )
    replay = replay_runner.build_sealed_replay_evidence_v01(
        source_manifest=manifest,
        source_domain_projection=domain_projection,
        source_safe_file_contents=contents,
        anchor_publication=publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=args.supplied_anchor_publication_id,
        reconstructed_manifest=reconstructed_manifest,
        reconstructed_domain_projection=domain_projection,
        reconstructed_safe_file_contents=contents,
        evidence_refs=(index.index_id, manifest.manifest_id),
    )
    if (
        replay_runner.validate_anchored_package_verification_v01(
            verification,
            anchor_publication=publication,
            manifest=manifest,
            domain_projection=domain_projection,
            safe_file_contents=contents,
            supplied_anchor_publication_id=args.supplied_anchor_publication_id,
        )
        or replay_runner.validate_sealed_replay_evidence_v01(
            replay,
            source_manifest=manifest,
            source_domain_projection=domain_projection,
            source_safe_file_contents=contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=args.supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=domain_projection,
            reconstructed_safe_file_contents=contents,
        )
        or verification.verification_status != "ANCHORED_PASS"
        or replay.replay_status != STATUS_PASS
    ):
        raise _CliFailure
    envelope = {
        "anchored_verification": (
            replay_runner.anchored_package_verification_to_plain_dict_v01(
                verification,
                anchor_publication=publication,
                manifest=manifest,
                domain_projection=domain_projection,
                safe_file_contents=contents,
                supplied_anchor_publication_id=args.supplied_anchor_publication_id,
            )
        ),
        "fixture_disposable": False,
        "replay_evidence": replay_runner.sealed_replay_evidence_to_plain_dict_v01(
            replay,
            source_manifest=manifest,
            source_domain_projection=domain_projection,
            source_safe_file_contents=contents,
            anchor_publication=publication,
            anchored_verification=verification,
            supplied_anchor_publication_id=args.supplied_anchor_publication_id,
            reconstructed_manifest=reconstructed_manifest,
            reconstructed_domain_projection=domain_projection,
            reconstructed_safe_file_contents=contents,
        ),
    }
    _write_owned_json(replay_output, envelope)
    replay_entry = os.lstat(replay_output)
    replay_identity = (replay_entry.st_dev, replay_entry.st_ino)
    try:
        if (
            binding._strict_json_bytes(_read_regular_file(replay_output)) != envelope
            or _read_regular_file(anchor_file) != anchor_bytes
        ):
            raise _CliFailure
        after = binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
        if after[0] != index or after[2:] != (domain_projection, manifest, contents):
            raise _CliFailure
    except Exception:
        _cleanup_owned_file(replay_output, replay_identity)
        raise _CliFailure from None
    return {
        "final_status": STATUS_PASS,
        "provider_network_gemini_effects": "0/0/0/0",
        "replay_id": replay.replay_id,
        "replay_status": replay.replay_status,
    }


def run_airline_a2_local_packageability_v01(
    *,
    gate_phase: str,
    temporary_root: Path,
    implementation_content_sha256: str,
    verified_head: str,
    repository_root: Path,
) -> AirlineA2LocalPackageabilityResultV01:
    _require_repository_root(repository_root)
    if gate_phase not in (binding.GATE_PHASE_PRECOMMIT, binding.GATE_PHASE_COMMITTED):
        raise _CliFailure
    if (
        not temporary_root.is_absolute()
        or str(temporary_root) != os.path.normpath(str(temporary_root))
        or os.path.commonpath((str(repository_root), str(temporary_root)))
        == str(repository_root)
        or temporary_root.exists()
        or temporary_root.is_symlink()
    ):
        raise _CliFailure
    if implementation_content_sha256_v01(repository_root) != implementation_content_sha256:
        raise _CliFailure
    if _git(repository_root, "rev-parse", "HEAD") != verified_head:
        raise _CliFailure
    if gate_phase == binding.GATE_PHASE_COMMITTED:
        if _git(repository_root, "rev-parse", "origin/main") != verified_head:
            raise _CliFailure
        if _git(repository_root, "status", "--porcelain"):
            raise _CliFailure
    owned_root_identity = _create_owned_directory(temporary_root)
    common = (
        sys.executable,
        "-m",
        "demo.run_two_domain_airline_a2_seal_v01",
    )
    try:
        process_a = subprocess.run(
            (*common, "--_local-process-a", "--gate-phase", gate_phase,
             "--repository-root", str(repository_root),
             "--temporary-root", str(temporary_root),
             "--synthetic-predecessor-root", str(temporary_root / "synthetic-predecessors"),
             "--attempt-output", str(temporary_root / "attempt-04"),
             "--safe-report-output", str(temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME),
             "--implementation-content-sha256", implementation_content_sha256,
             *(('--base-head', verified_head) if gate_phase == binding.GATE_PHASE_PRECOMMIT else ('--committed-head', verified_head)),
             "--process-result-output", str(temporary_root / "process-a-result-v01.json")),
            cwd=repository_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if process_a.returncode != 0 or process_a.stdout or process_a.stderr:
            raise _CliFailure
        process_b = subprocess.run(
            (*common, "--_local-process-b", "--gate-phase", gate_phase,
             "--repository-root", str(repository_root),
             "--temporary-root", str(temporary_root),
             "--attempt-directory", str(temporary_root / "attempt-04"),
             "--safe-report", str(temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME),
             "--process-a-result", str(temporary_root / "process-a-result-v01.json"),
             "--implementation-content-sha256", implementation_content_sha256,
             *(('--base-head', verified_head) if gate_phase == binding.GATE_PHASE_PRECOMMIT else ('--committed-head', verified_head)),
             "--package-root", str(temporary_root / "local-package")),
            cwd=repository_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if process_b.returncode != 0 or process_b.stderr:
            raise _CliFailure
        return _local_packageability_result_from_plain_v01(json.loads(process_b.stdout))
    finally:
        _cleanup_owned_root(temporary_root, owned_root_identity)


def _parser() -> _Parser:
    parser = _Parser(add_help=False, allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local-packageability", action="store_true")
    mode.add_argument("--package", action="store_true")
    mode.add_argument("--anchor", action="store_true")
    mode.add_argument("--replay", action="store_true")
    mode.add_argument("--_local-process-a", action="store_true")
    mode.add_argument("--_local-process-b", action="store_true")
    parser.add_argument("--gate-phase")
    parser.add_argument("--temporary-root")
    parser.add_argument("--implementation-content-sha256")
    parser.add_argument("--base-head")
    parser.add_argument("--committed-head")
    parser.add_argument("--repository-root")
    parser.add_argument("--synthetic-predecessor-root")
    parser.add_argument("--attempt-output")
    parser.add_argument("--safe-report-output")
    parser.add_argument("--process-result-output")
    parser.add_argument("--attempt-directory")
    parser.add_argument("--safe-report")
    parser.add_argument("--process-a-result")
    parser.add_argument("--package-root")
    parser.add_argument("--publication-base-head")
    parser.add_argument("--accepted-attempt-directory")
    parser.add_argument("--accepted-attempt-id")
    parser.add_argument("--execution-head")
    parser.add_argument("--expected-attempt-identity-sha256")
    parser.add_argument("--expected-private-inventory-sha256")
    parser.add_argument("--expected-private-inventory-digest")
    parser.add_argument("--expected-generation-gate-sha256")
    parser.add_argument("--expected-corridor-archive-sha256")
    parser.add_argument(
        "--expected-corridor-archive-byte-count",
        type=_ascii_positive_int,
    )
    parser.add_argument("--expected-safe-report-sha256")
    parser.add_argument(
        "--expected-safe-report-byte-count",
        type=_ascii_positive_int,
    )
    parser.add_argument("--expected-safe-execution-id")
    parser.add_argument("--generation-audit")
    parser.add_argument("--expected-generation-audit-sha256")
    parser.add_argument("--package-index-output")
    parser.add_argument("--package-index")
    parser.add_argument("--anchor-output")
    parser.add_argument("--p1-head")
    parser.add_argument("--anchor-file")
    parser.add_argument("--supplied-anchor-publication-id")
    parser.add_argument("--replay-output")
    return parser


def _reject_duplicates(argv: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for token in argv:
        if token.startswith("--"):
            option = token.split("=", 1)[0]
            if option in seen:
                raise _CliFailure
            seen.add(option)


def main(argv: list[str] | None = None) -> int:
    try:
        raw = tuple(sys.argv[1:] if argv is None else argv)
        _reject_duplicates(raw)
        args = _parser().parse_args(raw)
        if not args.repository_root:
            raise _CliFailure
        repository_root = Path(args.repository_root)
        _require_repository_root(repository_root)
        if args._local_process_a or args._local_process_b:
            internal_allowed = {
                "gate_phase",
                "temporary_root",
                "implementation_content_sha256",
                "base_head",
                "committed_head",
                "repository_root",
            }
            internal_allowed.update(
                (
                    "synthetic_predecessor_root",
                    "attempt_output",
                    "safe_report_output",
                    "process_result_output",
                )
                if args._local_process_a
                else (
                    "attempt_directory",
                    "safe_report",
                    "process_a_result",
                    "package_root",
                )
            )
            _reject_cross_mode_arguments(
                args,
                allowed=frozenset(internal_allowed),
            )
            if args.gate_phase == binding.GATE_PHASE_PRECOMMIT:
                if not args.base_head or args.committed_head:
                    raise _CliFailure
                head = args.base_head
            elif args.gate_phase == binding.GATE_PHASE_COMMITTED:
                if not args.committed_head or args.base_head:
                    raise _CliFailure
                head = args.committed_head
            else:
                raise _CliFailure
            common_values = (
                args.temporary_root,
                args.implementation_content_sha256,
            )
            if not all(common_values):
                raise _CliFailure
            if args._local_process_a:
                if not all(
                    (
                        args.synthetic_predecessor_root,
                        args.attempt_output,
                        args.safe_report_output,
                        args.process_result_output,
                    )
                ) or any(
                    value is not None
                    for value in (
                        args.attempt_directory,
                        args.safe_report,
                        args.process_a_result,
                        args.package_root,
                    )
                ):
                    raise _CliFailure
                _process_a(
                    repository_root=repository_root,
                    temporary_root=Path(args.temporary_root),
                    synthetic_predecessor_root=Path(args.synthetic_predecessor_root),
                    attempt_output=Path(args.attempt_output),
                    safe_report_output=Path(args.safe_report_output),
                    process_result_output=Path(args.process_result_output),
                    gate_phase=args.gate_phase,
                    verified_head=head,
                    implementation_digest=args.implementation_content_sha256,
                )
            else:
                if not all(
                    (
                        args.attempt_directory,
                        args.safe_report,
                        args.process_a_result,
                        args.package_root,
                    )
                ) or any(
                    value is not None
                    for value in (
                        args.synthetic_predecessor_root,
                        args.attempt_output,
                        args.safe_report_output,
                        args.process_result_output,
                    )
                ):
                    raise _CliFailure
                result = _process_b(
                    repository_root=repository_root,
                    temporary_root=Path(args.temporary_root),
                    attempt_directory=Path(args.attempt_directory),
                    safe_report_path=Path(args.safe_report),
                    process_a_result_path=Path(args.process_a_result),
                    package_root=Path(args.package_root),
                    gate_phase=args.gate_phase,
                    verified_head=head,
                    implementation_digest=args.implementation_content_sha256,
                )
                print(
                    json.dumps(
                        airline_a2_local_packageability_result_to_plain_dict_v01(
                            result
                        ),
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
            return 0
        if args.package:
            _reject_cross_mode_arguments(
                args,
                allowed=frozenset(
                    (
                        "repository_root",
                        "publication_base_head",
                        "accepted_attempt_directory",
                        "accepted_attempt_id",
                        "execution_head",
                        "expected_attempt_identity_sha256",
                        "expected_private_inventory_sha256",
                        "expected_private_inventory_digest",
                        "expected_generation_gate_sha256",
                        "expected_corridor_archive_sha256",
                        "expected_corridor_archive_byte_count",
                        "safe_report",
                        "expected_safe_report_sha256",
                        "expected_safe_report_byte_count",
                        "expected_safe_execution_id",
                        "generation_audit",
                        "expected_generation_audit_sha256",
                        "package_root",
                        "package_index_output",
                    )
                ),
            )
            required = (
                args.publication_base_head,
                args.accepted_attempt_directory,
                args.accepted_attempt_id,
                args.execution_head,
                args.expected_attempt_identity_sha256,
                args.expected_private_inventory_sha256,
                args.expected_private_inventory_digest,
                args.expected_generation_gate_sha256,
                args.expected_corridor_archive_sha256,
                args.expected_corridor_archive_byte_count,
                args.safe_report,
                args.expected_safe_report_sha256,
                args.expected_safe_report_byte_count,
                args.expected_safe_execution_id,
                args.generation_audit,
                args.expected_generation_audit_sha256,
                args.package_root,
                args.package_index_output,
            )
            if not all(required):
                raise _CliFailure
            print(
                json.dumps(
                    _run_official_package(args),
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            return 0
        if args.anchor:
            _reject_cross_mode_arguments(
                args,
                allowed=frozenset(
                    (
                        "repository_root",
                        "package_root",
                        "package_index",
                        "publication_base_head",
                        "anchor_output",
                    )
                ),
            )
            if not all(
                (
                    args.package_root,
                    args.package_index,
                    args.publication_base_head,
                    args.anchor_output,
                )
            ):
                raise _CliFailure
            print(
                json.dumps(_run_anchor(args), sort_keys=True, separators=(",", ":"))
            )
            return 0
        if args.replay:
            _reject_cross_mode_arguments(
                args,
                allowed=frozenset(
                    (
                        "repository_root",
                        "p1_head",
                        "package_root",
                        "package_index",
                        "anchor_file",
                        "supplied_anchor_publication_id",
                        "replay_output",
                    )
                ),
            )
            if not all(
                (
                    args.p1_head,
                    args.package_root,
                    args.package_index,
                    args.anchor_file,
                    args.supplied_anchor_publication_id,
                    args.replay_output,
                )
            ):
                raise _CliFailure
            print(
                json.dumps(_run_replay(args), sort_keys=True, separators=(",", ":"))
            )
            return 0
        if not args.local_packageability:
            raise _CliFailure
        _reject_cross_mode_arguments(
            args,
            allowed=frozenset(
                (
                    "repository_root",
                    "gate_phase",
                    "temporary_root",
                    "implementation_content_sha256",
                    "base_head",
                    "committed_head",
                )
            ),
        )
        if any(
            value is not None
            for value in (
                args.synthetic_predecessor_root,
                args.attempt_output,
                args.safe_report_output,
                args.process_result_output,
                args.attempt_directory,
                args.safe_report,
                args.process_a_result,
                args.package_root,
                args.publication_base_head,
                args.accepted_attempt_directory,
                args.accepted_attempt_id,
                args.execution_head,
                args.expected_attempt_identity_sha256,
                args.expected_private_inventory_sha256,
                args.expected_private_inventory_digest,
                args.expected_generation_gate_sha256,
                args.expected_corridor_archive_sha256,
                args.expected_corridor_archive_byte_count,
                args.expected_safe_report_sha256,
                args.expected_safe_report_byte_count,
                args.expected_safe_execution_id,
                args.generation_audit,
                args.expected_generation_audit_sha256,
                args.package_index_output,
                args.package_index,
                args.anchor_output,
                args.p1_head,
                args.anchor_file,
                args.supplied_anchor_publication_id,
                args.replay_output,
            )
        ):
            raise _CliFailure
        if args.gate_phase == binding.GATE_PHASE_PRECOMMIT:
            if not args.base_head or args.committed_head:
                raise _CliFailure
            head = args.base_head
        elif args.gate_phase == binding.GATE_PHASE_COMMITTED:
            if not args.committed_head or args.base_head:
                raise _CliFailure
            head = args.committed_head
        else:
            raise _CliFailure
        if not args.temporary_root or not args.implementation_content_sha256:
            raise _CliFailure
        result = run_airline_a2_local_packageability_v01(
            gate_phase=args.gate_phase,
            temporary_root=Path(args.temporary_root),
            implementation_content_sha256=args.implementation_content_sha256,
            verified_head=head,
            repository_root=repository_root,
        )
        print(
            json.dumps(
                airline_a2_local_packageability_result_to_plain_dict_v01(result),
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        print(LOCAL_GATE_TOKEN)
        return 0
    except Exception:
        print(json.dumps({"final_status": STATUS_FAIL_CLOSED, "reason_code": REASON_INVALID}, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
