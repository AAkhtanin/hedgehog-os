from __future__ import annotations

import json
import hashlib
import os
import shutil
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

import pytest

from demo import run_two_domain_airline_a2_seal_v01 as runner
from hedgehog.domains.airline import sealed_evidence_a2_binding_v01 as binding


def test_implementation_digest_is_deterministic() -> None:
    first = runner.implementation_content_sha256_v01(Path.cwd())
    second = runner.implementation_content_sha256_v01(Path.cwd())
    assert first == second
    assert len(first) == 64


def test_implementation_digest_matches_independent_twelve_path_oracle() -> None:
    digest = hashlib.sha256()
    digest.update(
        b"hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1\0"
    )
    expected_order = (
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
    assert runner.AUTHORIZED_IMPLEMENTATION_PATHS == expected_order
    for logical_name in expected_order:
        content = (Path.cwd() / logical_name).read_bytes()
        digest.update(logical_name.encode("ascii"))
        digest.update(b"\0")
        digest.update(str(len(content)).encode("ascii"))
        digest.update(b"\0")
        digest.update(content)
    assert runner.implementation_content_sha256_v01(Path.cwd()) == digest.hexdigest()


def _local_result() -> runner.AirlineA2LocalPackageabilityResultV01:
    return runner.AirlineA2LocalPackageabilityResultV01(
        status="PASS",
        callbacks="12/12/12",
        collector_corridor_ledger_crypto="1/1/1/1",
        outbound_provider_network_gemini_effects="0/0/0/0",
        hydrate_adapter_package="1/1/1",
        canonical_package_index_writes="0/0",
        package_anchor_replay_publication="0/0/0",
        repository_output_count=0,
        residue_count=0,
        corridor_sha256="1" * 64,
        corridor_sha256_equality=True,
        adapter_result_id="2" * 64,
        manifest_id="3" * 64,
        package_content_hash="4" * 64,
    )


def test_local_result_is_immutable_and_canonical() -> None:
    result = _local_result()
    with pytest.raises(FrozenInstanceError):
        result.status = "FAIL_CLOSED"
    assert runner._local_packageability_result_from_plain_v01(
        runner.airline_a2_local_packageability_result_to_plain_dict_v01(result)
    ) == result


@pytest.mark.parametrize(
    "argv",
    (
        (),
        ("--local-packageability",),
        ("--package",),
        ("--anchor",),
        ("--replay",),
        ("--local-packageability", "--gate-phase", "unknown"),
        ("--local-packageability", "--gate-phase", "precommit", "--base-head", "x", "--base-head", "x"),
    ),
)
def test_invalid_cli_is_one_sanitized_line(
    argv: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert runner.main(list(argv)) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out)["final_status"] == "FAIL_CLOSED"
    assert "Traceback" not in captured.out


def test_precommit_and_committed_head_flags_are_disjoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        runner,
        "run_airline_a2_local_packageability_v01",
        lambda **_: _local_result(),
    )
    digest = runner.implementation_content_sha256_v01(Path.cwd())
    common = [
        "--local-packageability",
        "--repository-root",
        str(Path.cwd()),
        "--temporary-root",
        str(tmp_path / "root"),
        "--implementation-content-sha256",
        digest,
    ]
    assert runner.main([*common, "--gate-phase", "precommit", "--base-head", "2" * 40]) == 0
    assert runner.LOCAL_GATE_TOKEN in capsys.readouterr().out
    assert runner.main([*common, "--gate-phase", "committed-head", "--committed-head", "2" * 40]) == 0
    assert runner.LOCAL_GATE_TOKEN in capsys.readouterr().out


def test_process_failure_is_fail_closed_and_sanitized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runner, "implementation_content_sha256_v01", lambda _: "1" * 64)
    monkeypatch.setattr(runner, "_git", lambda *_: "2" * 40)
    calls = []

    def failed(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=2, stdout="", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", failed)
    with pytest.raises(Exception):
        runner.run_airline_a2_local_packageability_v01(
            gate_phase="precommit",
            temporary_root=tmp_path / "owned",
            implementation_content_sha256="1" * 64,
            verified_head="2" * 40,
            repository_root=Path.cwd(),
        )
    assert len(calls) == 1
    assert not (tmp_path / "owned").exists()


def test_real_two_fresh_process_precommit_gate_has_zero_residue(tmp_path: Path) -> None:
    repository_root = Path.cwd()
    digest = runner.implementation_content_sha256_v01(repository_root)
    result = runner.run_airline_a2_local_packageability_v01(
        gate_phase="precommit",
        temporary_root=tmp_path / "owned-gate",
        implementation_content_sha256=digest,
        verified_head=runner._git(repository_root, "rev-parse", "HEAD"),
        repository_root=repository_root,
    )
    assert result == runner._local_packageability_result_from_plain_v01(
        runner.airline_a2_local_packageability_result_to_plain_dict_v01(result)
    )
    assert result.callbacks == "12/12/12"
    assert result.collector_corridor_ledger_crypto == "1/1/1/1"
    assert result.outbound_provider_network_gemini_effects == "0/0/0/0"
    assert result.hydrate_adapter_package == "1/1/1"
    assert result.package_anchor_replay_publication == "0/0/0"
    assert result.repository_output_count == 0
    assert result.residue_count == 0
    assert not (tmp_path / "owned-gate").exists()


@pytest.mark.parametrize(
    "argv",
    (
        ("--internal-process-a",),
        ("--internal-process-b",),
        ("--_local-process-a",),
        ("--_local-process-b",),
        (
            "--local-packageability",
            "--repository-root",
            "/tmp/repo",
            "--repository-root=/tmp/repo",
        ),
        ("--local-pack",),
    ),
)
def test_internal_and_abbreviated_cli_attacks_fail_closed(
    argv: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert runner.main(list(argv)) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    assert "Traceback" not in captured.out


@pytest.mark.parametrize("token", ("0", "01", "+1", "-1", "١", "１"))
def test_official_byte_counts_require_positive_canonical_ascii(
    token: str,
) -> None:
    with pytest.raises(Exception):
        runner._parser().parse_args(
            (
                "--package",
                "--expected-safe-report-byte-count",
                token,
            )
        )


def test_owned_json_write_is_exclusive_and_cleans_short_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "owned.json"
    target.write_bytes(b"foreign\n")
    with pytest.raises(Exception):
        runner._write_owned_json(target, {"status": "PASS"})
    assert runner._read_regular_file(target) == b"foreign\n"
    target.unlink()
    monkeypatch.setattr(runner.os, "write", lambda *_args: 0)
    with pytest.raises(Exception):
        runner._write_owned_json(target, {"status": "PASS"})
    assert not target.exists()


def test_owned_directory_rejects_symlink_without_touching_target(
    tmp_path: Path,
) -> None:
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    target = tmp_path / "owned"
    target.symlink_to(attacker, target_is_directory=True)
    with pytest.raises(Exception):
        runner._create_owned_directory(target)
    assert target.is_symlink()
    assert tuple(attacker.iterdir()) == ()


@pytest.mark.parametrize(
    "argv",
    (
        ("--package", "--gate-phase", "precommit"),
        ("--anchor", "--accepted-attempt-id", "x"),
        ("--replay", "--publication-base-head", "1" * 40),
        ("--local-packageability", "--package-index", "/tmp/index"),
    ),
)
def test_owner_modes_reject_cross_mode_options_before_dispatch(
    argv: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert runner.main([*argv, "--repository-root", str(Path.cwd())]) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1


def _create_process_a_attempt(tmp_path: Path) -> SimpleNamespace:
    repository_root = Path.cwd()
    temporary_root = tmp_path / "process-a-owned"
    runner._create_owned_directory(temporary_root)
    digest = runner.implementation_content_sha256_v01(repository_root)
    head = runner._git(repository_root, "rev-parse", "HEAD")
    runner._process_a(
        repository_root=repository_root,
        temporary_root=temporary_root,
        synthetic_predecessor_root=temporary_root / "synthetic-predecessors",
        attempt_output=temporary_root / "attempt-04",
        safe_report_output=temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME,
        process_result_output=temporary_root / "process-a-result-v01.json",
        gate_phase=binding.GATE_PHASE_PRECOMMIT,
        verified_head=head,
        implementation_digest=digest,
    )
    process_result = binding.airline_a2_local_process_a_result_from_plain_dict_v01(
        json.loads(
            runner._read_regular_file(
                temporary_root / "process-a-result-v01.json"
            )
        )
    )
    return SimpleNamespace(
        repository_root=repository_root,
        temporary_root=temporary_root,
        attempt=temporary_root / "attempt-04",
        safe_report=temporary_root / binding.LOCAL_SAFE_REPORT_LOGICAL_NAME,
        process_result=process_result,
        digest=digest,
        head=head,
    )


def _load_local_process_a(source: SimpleNamespace) -> tuple[object, ...]:
    result = source.process_result
    return binding.load_airline_a2_local_nonpublication_source_v01(
        repository_root=source.repository_root,
        attempt_directory=source.attempt,
        safe_report_path=source.safe_report,
        expected_attempt_id=result.attempt_id,
        expected_execution_head=result.execution_head,
        expected_attempt_identity_sha256=result.attempt_identity_sha256,
        expected_private_inventory_sha256=result.private_inventory_sha256,
        expected_private_inventory_digest=result.private_inventory_digest,
        expected_generation_gate_sha256=result.generation_gate_sha256,
        expected_corridor_archive_sha256=result.corridor_archive_sha256,
        expected_corridor_archive_byte_count=result.corridor_archive_byte_count,
        expected_safe_report_sha256=result.safe_report_sha256,
        expected_safe_report_byte_count=result.safe_report_byte_count,
        expected_safe_execution_id=result.safe_execution_id,
        implementation_content_sha256=result.implementation_content_sha256,
    )


def test_loader_hydrates_all_six_inputs_without_opening_forbidden_bodies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _create_process_a_attempt(tmp_path)
    opened: list[str] = []
    original = binding._read_leaf

    def observed(directory_fd: int, leaf: str, maximum: int = 8_000_000) -> bytes:
        opened.append(leaf)
        return original(directory_fd, leaf, maximum)

    monkeypatch.setattr(binding, "_read_leaf", observed)
    loaded = _load_local_process_a(source)
    assert len(loaded) == 7
    assert loaded[0].source_variant == binding.SOURCE_LOCAL
    assert loaded[1].safe_execution_id == source.process_result.safe_execution_id
    corridor_accepted, corridor_errors = (
        binding.corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(
            loaded[2].corridor_report
        )
    )
    assert corridor_accepted is True
    assert corridor_errors == ()
    assert loaded[2].corridor_report.transaction_id == loaded[4].ledger_item.transaction_id
    assert not any(
        leaf.endswith(("_prompt.txt", "_raw_response.txt", "_extracted_json_candidate.json"))
        for leaf in opened
    )


@pytest.mark.parametrize("attack", ("extra", "symlink", "fifo", "directory", "truncate", "metadata_mode"))
def test_local_loader_rejects_complete_inventory_attacks(
    tmp_path: Path,
    attack: str,
) -> None:
    source = _create_process_a_attempt(tmp_path)
    copy_root = tmp_path / f"copy-{attack}"
    shutil.copytree(source.attempt, copy_root, copy_function=shutil.copy2)
    raw_root = copy_root / "raw_attempt"
    inventory = json.loads(
        runner._read_regular_file(copy_root / "private_inventory_v01.json")
    )
    selected = set(binding._A2_SELECTED_RAW_FILES)
    unselected = next(
        row["logical_ref"]
        for row in inventory["ordered_files"]
        if row["logical_ref"] not in selected
    )
    target = raw_root / unselected
    if attack == "extra":
        (raw_root / "unexpected.json").write_text("{}\n", encoding="utf-8")
    elif attack == "symlink":
        target.unlink()
        target.symlink_to(raw_root / "summary.json")
    elif attack == "fifo":
        target.unlink()
        os.mkfifo(target, 0o600)
    elif attack == "directory":
        target.unlink()
        target.mkdir()
    elif attack == "truncate":
        corridor = raw_root / binding.CORRIDOR_ARCHIVE_LOGICAL_NAME.removeprefix(
            "raw_attempt/"
        )
        corridor.write_bytes(runner._read_regular_file(corridor)[:-1])
    else:
        os.chmod(copy_root / "attempt_identity_v01.json", 0o644)
    source.attempt = copy_root
    with pytest.raises(ValueError):
        _load_local_process_a(source)


def test_process_b_rejects_cross_file_process_a_result_mismatch(
    tmp_path: Path,
) -> None:
    source = _create_process_a_attempt(tmp_path)
    wrong = binding.build_airline_a2_local_process_a_result_v01(
        **{
            key: value
            for key, value in binding.airline_a2_local_process_a_result_to_plain_dict_v01(
                source.process_result
            ).items()
            if key not in {"result_id", "result_version", "corridor_archive_sha256", "corridor_archive_logical_name", "safe_report_logical_name", "final_status", "validation_errors"}
        },
        corridor_archive_sha256="f" * 64,
    )
    process_result_path = source.temporary_root / "process-a-result-v01.json"
    process_result_path.write_bytes(
        binding.canonical_json_line_v01(
            binding.airline_a2_local_process_a_result_to_plain_dict_v01(wrong)
        )
    )
    with pytest.raises(Exception):
        runner._process_b(
            repository_root=source.repository_root,
            temporary_root=source.temporary_root,
            attempt_directory=source.attempt,
            safe_report_path=source.safe_report,
            process_a_result_path=process_result_path,
            package_root=source.temporary_root / "local-package",
            gate_phase=binding.GATE_PHASE_PRECOMMIT,
            verified_head=source.head,
            implementation_digest=source.digest,
        )
    assert not (source.temporary_root / "local-package").exists()


def test_synthetic_official_package_anchor_replay_modes_and_disk_mutations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _create_process_a_attempt(tmp_path)
    gate_path = source.attempt / "generation_gate_v01.json"
    gate = json.loads(runner._read_regular_file(gate_path))
    gate.update(
        {
            "actual_external_operation_status": "VERIFIED",
            "actual_gemini_call_count": 12,
            "actual_network_call_count": 12,
            "actual_provider_call_count": 12,
            "live_collection_performed": True,
            "official_evidence_eligible": True,
        }
    )
    gate_bytes = binding.canonical_json_line_v01(gate)
    gate_path.write_bytes(gate_bytes)
    os.chmod(gate_path, 0o600)

    repository_root = tmp_path / "synthetic-repository"
    repository_root.mkdir(mode=0o700)
    safe_report = repository_root / (
        "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
        "airline_safe_execution_report_attempt_04_v01.json"
    )
    generation_audit = repository_root / (
        "docs/audit_reports/"
        "auditor_two_domain_airline_all_real_generation_attempt_04_v01.log"
    )
    safe_report.parent.mkdir(parents=True)
    generation_audit.parent.mkdir(parents=True)
    safe_bytes = runner._read_regular_file(source.safe_report)
    safe_report.write_bytes(safe_bytes)
    audit_bytes = (
        b"audit_status=CLOSED_PASS\n"
        b"audit_disposition="
        b"ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE\n"
    )
    generation_audit.write_bytes(audit_bytes)

    def committed_bytes(root: Path, head: str, relative: str) -> bytes:
        assert root == repository_root
        assert head == source.head
        return runner._read_regular_file(root / relative)

    monkeypatch.setattr(binding, "_git_committed_file_bytes", committed_bytes)
    monkeypatch.setattr(runner, "_require_git_head", lambda *_args, **_kwargs: None)
    package_root = repository_root / binding.OFFICIAL_PACKAGE_ROOT
    package_index = repository_root / binding.OFFICIAL_PACKAGE_INDEX
    package_args = SimpleNamespace(
        repository_root=str(repository_root),
        package_root=str(package_root),
        package_index_output=str(package_index),
        publication_base_head=source.head,
        accepted_attempt_directory=str(source.attempt),
        accepted_attempt_id=source.process_result.attempt_id,
        execution_head=source.process_result.execution_head,
        expected_attempt_identity_sha256=(
            source.process_result.attempt_identity_sha256
        ),
        expected_private_inventory_sha256=(
            source.process_result.private_inventory_sha256
        ),
        expected_private_inventory_digest=(
            source.process_result.private_inventory_digest
        ),
        expected_generation_gate_sha256=hashlib.sha256(gate_bytes).hexdigest(),
        expected_corridor_archive_sha256=(
            source.process_result.corridor_archive_sha256
        ),
        expected_corridor_archive_byte_count=(
            source.process_result.corridor_archive_byte_count
        ),
        safe_report=str(safe_report),
        expected_safe_report_sha256=hashlib.sha256(safe_bytes).hexdigest(),
        expected_safe_report_byte_count=len(safe_bytes),
        expected_safe_execution_id=source.process_result.safe_execution_id,
        generation_audit=str(generation_audit),
        expected_generation_audit_sha256=hashlib.sha256(audit_bytes).hexdigest(),
    )
    package_summary = runner._run_official_package(package_args)
    assert package_summary["final_status"] == "PASS"
    loaded = binding.load_airline_a2_official_package_v01(
        package_root=package_root,
        package_index_path=package_index,
    )
    assert loaded[0].package_status == "SELF_CONSISTENT_UNANCHORED"

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
    monkeypatch.setattr(
        runner,
        "_git",
        lambda _root, *arguments: (
            "\n".join(sorted(expected_dirty))
            if arguments and arguments[0] == "status"
            else source.head
        ),
    )
    anchor_output = repository_root / runner.OFFICIAL_ANCHOR_OUTPUT
    anchor_summary = runner._run_anchor(
        SimpleNamespace(
            repository_root=str(repository_root),
            package_root=str(package_root),
            package_index=str(package_index),
            publication_base_head=source.head,
            anchor_output=str(anchor_output),
        )
    )
    assert anchor_summary["final_status"] == "PASS"
    replay_output = repository_root / runner.OFFICIAL_REPLAY_OUTPUT
    replay_summary = runner._run_replay(
        SimpleNamespace(
            repository_root=str(repository_root),
            p1_head=source.head,
            package_root=str(package_root),
            package_index=str(package_index),
            anchor_file=str(anchor_output),
            supplied_anchor_publication_id=anchor_summary["anchor_publication_id"],
            replay_output=str(replay_output),
        )
    )
    assert replay_summary["final_status"] == "PASS"

    index_bytes = runner._read_regular_file(package_index)
    package_index.write_bytes(index_bytes + b" ")
    with pytest.raises(ValueError):
        binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
    package_index.write_bytes(index_bytes)
    member_03 = package_root / binding._MEMBER_PATHS[2]
    member_03_bytes = runner._read_regular_file(member_03)
    member_03.write_bytes(member_03_bytes + b" ")
    with pytest.raises(ValueError):
        binding.load_airline_a2_official_package_v01(
            package_root=package_root,
            package_index_path=package_index,
        )
