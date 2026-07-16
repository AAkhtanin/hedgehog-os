from __future__ import annotations

import ast
import errno
import json
import os
import shutil
import stat
import traceback
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from demo import run_airline_sealed_trace_replay_v01 as runner
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts
from tests import test_tri_party_airline_live_semantic_lane_v01_runner as live_helpers


MODULE_PATH = "demo/run_airline_sealed_trace_replay_v01.py"


@dataclass(frozen=True)
class RunnerFixture:
    package_dir: Path
    anchor_path: Path
    anchor: dict[str, object]
    manifest: dict[str, object]
    initial_bytes: tuple[tuple[str, bytes], ...]


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _generate_fixture(root: Path, offer: str) -> RunnerFixture:
    package_dir = root / f"airline_replay_c2_{offer}"
    package_dir.mkdir()
    constraints = (
        live_helpers.binding.build_client_constraints_preference_a_v01()
        if offer == "a"
        else live_helpers.binding.build_client_constraints_preference_b_v01()
    )
    live_report = live_helpers._crypto_report_for_preference(
        constraints,
        package_dir,
    )
    assert live_report["final_status"] == runner.STATUS_PASS
    manifest = json.loads(
        (package_dir / replay_contracts.MANIFEST_ARTIFACT_REF).read_text(),
    )
    core = manifest["manifest_core"]
    anchor = {
        "anchor_active_only_when_committed": True,
        "anchor_document_id": "airline_crypto_artifact_seal_anchor_v01",
        "anchor_version": "v0.1",
        "anchored_pass_claimed": False,
        "canonicalization_profile_id": crypto_contracts.CANONICALIZATION_PROFILE_ID,
        "chain_tail_hash": core["chain_tail_hash"],
        "document_status": "ANCHOR_PUBLICATION",
        "expected_manifest_core_hash": manifest["manifest_core_hash"],
        "external_anchor_supplied_at_publication": False,
        "external_anchor_verified_at_publication": False,
        "hash_algorithm": crypto_contracts.HASH_ALGORITHM,
        "hash_encoding": crypto_contracts.HASH_ENCODING,
        "ledger_id": core["ledger_id"],
        "manifest_artifact_ref": replay_contracts.MANIFEST_ARTIFACT_REF,
        "next_gate": "airline_crypto_artifact_seal_v01_slice_e2_anchored_audit",
        "package_generation_base_head": "0000000",
        "publication_slice": "airline_crypto_artifact_seal_v01_slice_e1",
        "real_world_effects_count": 0,
        "replay_allowed": False,
        "signature_mode": crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER,
        "signature_verified": False,
        "source_package_hash": core["source_package_hash"],
        "source_package_ref": core["source_package_ref"],
        "source_package_relpath": f"fixtures/{core['source_package_ref']}",
        "transaction_id": core["transaction_id"],
        "verification_artifact_ref": replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
        "verification_status_at_publication": crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED,
    }
    anchor_path = root / f"anchor_{offer}.json"
    anchor_path.write_bytes(_json_bytes(anchor))
    initial_bytes = tuple(
        (name, (package_dir / name).read_bytes())
        for name in runner.CRITICAL_FILE_REFS
    )
    return RunnerFixture(
        package_dir=package_dir,
        anchor_path=anchor_path,
        anchor=anchor,
        manifest=manifest,
        initial_bytes=initial_bytes,
    )


@pytest.fixture(scope="module")
def packages(tmp_path_factory: pytest.TempPathFactory) -> tuple[RunnerFixture, RunnerFixture]:
    root = tmp_path_factory.mktemp("airline_replay_c2")
    return _generate_fixture(root, "a"), _generate_fixture(root, "b")


def _run(fixture: RunnerFixture, output: Path) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    return runner.run_airline_sealed_trace_replay_v01(
        package_dir=fixture.package_dir,
        anchor_path=fixture.anchor_path,
        output_path=output,
    )


def _runner_argv(
    fixture: RunnerFixture,
    output: Path,
) -> tuple[str, ...]:
    return (
        "--package-dir",
        str(fixture.package_dir),
        "--anchor-path",
        str(fixture.anchor_path),
        "--output-path",
        str(output),
    )


def _assert_reason(reason: str, action: object) -> ValueError:
    with pytest.raises(ValueError) as captured:
        action()  # type: ignore[operator]
    error = captured.value
    assert type(error) is ValueError
    assert error.args == (reason,)
    assert error.__cause__ is None
    assert error.__context__ is None
    return error


def _copy_package(fixture: RunnerFixture, root: Path, name: str) -> Path:
    target = root / name
    shutil.copytree(fixture.package_dir, target)
    return target


def _anchor_for_package(fixture: RunnerFixture, package: Path, path: Path) -> Path:
    anchor = dict(fixture.anchor)
    anchor["source_package_ref"] = package.name
    anchor["source_package_relpath"] = f"fixtures/{package.name}"
    manifest_path = package / replay_contracts.MANIFEST_ARTIFACT_REF
    manifest = json.loads(manifest_path.read_text())
    manifest["manifest_core"]["source_package_ref"] = package.name
    # Renaming an already sealed package is intentionally not a valid fixture.
    path.write_bytes(_json_bytes(anchor))
    return path


def test_exact_constant_surfaces() -> None:
    assert runner.MODULE_ID == "run_airline_sealed_trace_replay_v01"
    assert runner.SLICE_ID == "airline_sealed_trace_replay_v01_slice_c2"
    assert type(runner.CRITICAL_FILE_REFS) is tuple
    assert runner.CRITICAL_FILE_REFS[:9] == crypto_contracts.REQUIRED_SOURCE_FILE_REFS
    assert runner.CRITICAL_FILE_REFS[-2:] == (
        replay_contracts.MANIFEST_ARTIFACT_REF,
        replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
    )
    assert len(runner.CRITICAL_FILE_REFS) == len(set(runner.CRITICAL_FILE_REFS)) == 11
    assert len(runner.ANCHOR_DOCUMENT_FIELD_NAMES) == 27
    assert len(runner.REPLAY_RUNNER_REASON_ALLOWLIST) == 32
    assert len(set(runner.REPLAY_RUNNER_REASON_ALLOWLIST)) == 32


@pytest.mark.parametrize("index", (0, 1))
def test_offer_runner_pass_and_external_output(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    index: int,
) -> None:
    fixture = packages[index]
    output = tmp_path / f"replay_{index}.json"
    report = _run(fixture, output)
    plain = replay_contracts.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
    raw = output.read_bytes()
    assert report.replay_status == runner.STATUS_PASS
    assert report.source_package_ref == fixture.anchor["source_package_ref"]
    assert report.transaction_id == fixture.anchor["transaction_id"]
    assert report.ledger_id == fixture.anchor["ledger_id"]
    assert report.manifest_core_hash == fixture.anchor["expected_manifest_core_hash"]
    assert report.expected_manifest_core_hash == fixture.anchor["expected_manifest_core_hash"]
    assert (report.ledger_entry_count, report.dependency_edge_count, report.root_final_count) == (19, 29, 3)
    assert (report.source_file_count, report.critical_package_file_count) == (9, 11)
    assert report.timeline_row_count == 19
    assert report.ledger_audit_count == 1
    assert report.anchored_verification_count == 1
    assert report.post_replay_snapshot_provider_call_count == 1
    assert report.stored_verification_status == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    assert report.fresh_anchored_verification_status == runner.STATUS_PASS
    assert report.signature_verified is False
    assert report.root_attestation_required is False
    assert report.root_attestation_present is False
    assert output.parent != fixture.package_dir
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert raw == _json_bytes(plain) + b"\n"
    assert crypto_contracts.parse_airline_crypto_json_object_bytes_v01(raw) == plain
    assert stat.S_IMODE(output.stat().st_mode) & ~0o600 == 0
    assert tuple((name, (fixture.package_dir / name).read_bytes()) for name in runner.CRITICAL_FILE_REFS) == fixture.initial_bytes


@pytest.mark.parametrize("sequence", ((0, 1, 0), (1, 0, 1)))
def test_offer_isolation_and_repeat_equality(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    sequence: tuple[int, ...],
) -> None:
    reports = tuple(
        _run(packages[index], tmp_path / f"result_{position}.json")
        for position, index in enumerate(sequence)
    )
    assert reports[0] == reports[2]
    assert reports[0] != reports[1]


def test_exact_audit_and_collection_call_counts(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counts = {"audit": 0, "collection": 0}
    original_audit = runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01
    original_collection = runner.replay_collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01

    def audit(*args: object, **kwargs: object) -> object:
        counts["audit"] += 1
        return original_audit(*args, **kwargs)

    def collection(*args: object, **kwargs: object) -> object:
        counts["collection"] += 1
        return original_collection(*args, **kwargs)

    monkeypatch.setattr(runner.ledger_audit, "collect_airline_transaction_artifact_ledger_audit_v01", audit)
    monkeypatch.setattr(runner.replay_collector, "collect_airline_sealed_trace_replay_from_package_snapshot_v01", collection)
    assert _run(packages[0], tmp_path / "calls.json").replay_status == runner.STATUS_PASS
    assert counts == {"audit": 1, "collection": 1}


def test_accepted_audit_bridge_is_exact(packages: tuple[RunnerFixture, RunnerFixture]) -> None:
    fixture = packages[0]
    report = runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01(
        artifact_dir=fixture.package_dir,
        env={},
    )
    accepted = runner._accepted_audit(report)
    assert type(accepted) is crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
    assert all(getattr(accepted, name) == getattr(report, name) for name in crypto_collector.ACCEPTED_AUDIT_FIELD_NAMES)
    assert crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(accepted).validation_status == runner.STATUS_PASS


def test_cli_success_is_safe_summary(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = packages[0]
    status = runner.main((
        "--package-dir", str(fixture.package_dir),
        "--anchor-path", str(fixture.anchor_path),
        "--output-path", str(tmp_path / "cli.json"),
    ))
    printed = json.loads(capsys.readouterr().out)
    assert status == 0
    assert tuple(sorted(printed)) == tuple(sorted((
        "replay_status", "replay_id", "transaction_id", "ledger_id",
        "timeline_row_count", "critical_package_file_count",
    )))


@pytest.mark.parametrize(
    "argv",
    (
        (),
        ("--package-dir", "package", "--anchor-path", "anchor"),
        ("--unknown", "value"),
        ("--package-dir",),
    ),
)
def test_cli_parse_failures_are_stable_and_silent(
    argv: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = runner.main(argv)
    captured = capsys.readouterr()
    assert status == 1
    assert captured.out == runner.REASON_REPLAY_COLLECTION_FAILED + "\n"
    assert captured.err == ""
    assert "usage:" not in captured.out.lower()
    assert all(fragment not in captured.out for fragment in argv)


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("package", runner.REASON_PACKAGE_DIRECTORY_INVALID),
        ("anchor", runner.REASON_ANCHOR_PATH_INVALID),
        ("output", runner.REASON_OUTPUT_PATH_INVALID),
    ),
)
def test_cli_empty_paths_are_stable(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    field: str,
    reason: str,
) -> None:
    fixture = packages[0]
    values = {
        "package": str(fixture.package_dir),
        "anchor": str(fixture.anchor_path),
        "output": str(tmp_path / "empty-path.json"),
    }
    values[field] = ""
    status = runner.main((
        "--package-dir",
        values["package"],
        "--anchor-path",
        values["anchor"],
        "--output-path",
        values["output"],
    ))
    captured = capsys.readouterr()
    assert status == 1
    assert captured.out == reason + "\n"
    assert captured.err == ""


@pytest.mark.parametrize("relative_ref", runner.CRITICAL_FILE_REFS)
def test_each_missing_critical_file_fails_closed(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    relative_ref: str,
) -> None:
    fixture = packages[0]
    package = _copy_package(fixture, tmp_path, fixture.package_dir.name)
    (package / relative_ref).unlink()
    _assert_reason(
        runner.REASON_CRITICAL_FILE_MISSING,
        lambda: runner.run_airline_sealed_trace_replay_v01(
            package_dir=package,
            anchor_path=fixture.anchor_path,
            output_path=tmp_path / "missing.json",
        ),
    )


def test_package_path_guards(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
) -> None:
    fixture = packages[0]
    _assert_reason(runner.REASON_PACKAGE_DIRECTORY_INVALID, lambda: _run(replace(fixture, package_dir=tmp_path / "missing"), tmp_path / "a.json"))
    file_path = tmp_path / "file"; file_path.write_text("x")
    _assert_reason(runner.REASON_PACKAGE_DIRECTORY_INVALID, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=file_path, anchor_path=fixture.anchor_path, output_path=tmp_path / "b.json"))
    link = tmp_path / "link"; link.symlink_to(fixture.package_dir, target_is_directory=True)
    _assert_reason(runner.REASON_PACKAGE_DIRECTORY_SYMLINK, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=link, anchor_path=fixture.anchor_path, output_path=tmp_path / "c.json"))


@pytest.mark.parametrize(
    ("kind", "reason"),
    (
        ("symlink", runner.REASON_CRITICAL_FILE_SYMLINK),
        ("dangling", runner.REASON_CRITICAL_FILE_SYMLINK),
        ("directory", runner.REASON_CRITICAL_FILE_NOT_REGULAR),
        ("unreadable", runner.REASON_CRITICAL_FILE_UNREADABLE),
    ),
)
def test_critical_file_type_and_read_guards(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    reason: str,
) -> None:
    fixture = packages[0]
    package = _copy_package(fixture, tmp_path, fixture.package_dir.name)
    target = package / crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0]
    target.unlink()
    if kind == "symlink":
        target.symlink_to(package / crypto_contracts.REQUIRED_SOURCE_FILE_REFS[1])
    elif kind == "dangling":
        target.symlink_to(tmp_path / "missing-critical-target")
    elif kind == "directory":
        target.mkdir()
    else:
        target.write_bytes(b"unreadable")
        original_open = runner._open_readonly

        def unreadable_open(path: Path, flags: int) -> int:
            if path == target:
                raise PermissionError("API_KEY=TOP_SECRET")
            return original_open(path, flags)

        monkeypatch.setattr(runner, "_open_readonly", unreadable_open)
    _assert_reason(
        reason,
        lambda: runner.run_airline_sealed_trace_replay_v01(
            package_dir=package,
            anchor_path=fixture.anchor_path,
            output_path=tmp_path / f"{kind}.json",
        ),
    )


def test_critical_file_swap_to_symlink_is_rejected_before_target_read(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = packages[0]
    package = _copy_package(fixture, tmp_path, fixture.package_dir.name)
    critical_path = package / crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0]
    symlink_target = tmp_path / "secret-target"
    symlink_target.write_bytes(b"API_KEY=TOP_SECRET")
    original_open = runner._open_readonly
    original_read = runner._read_fd_chunk
    target_fd: int | None = None
    target_read = False

    def swapping_open(path: Path, flags: int) -> int:
        nonlocal target_fd
        if path == critical_path:
            critical_path.unlink()
            critical_path.symlink_to(symlink_target)
        fd = original_open(path, flags)
        if path == critical_path:
            target_fd = fd
        return fd

    def observed_read(fd: int, size: int) -> bytes:
        nonlocal target_read
        if fd == target_fd:
            target_read = True
        return original_read(fd, size)

    monkeypatch.setattr(runner, "_open_readonly", swapping_open)
    monkeypatch.setattr(runner, "_read_fd_chunk", observed_read)
    _assert_reason(
        runner.REASON_CRITICAL_FILE_SYMLINK,
        lambda: runner.run_airline_sealed_trace_replay_v01(
            package_dir=package,
            anchor_path=fixture.anchor_path,
            output_path=tmp_path / "swap.json",
        ),
    )
    assert target_read is False


def test_read_descriptor_closes_after_ordinary_failure(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = packages[0]
    package = _copy_package(fixture, tmp_path, fixture.package_dir.name)
    target = package / crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0]
    original_open = runner._open_readonly
    original_close = runner._close_read_fd
    target_fd: int | None = None
    closed: list[int] = []

    def observed_open(path: Path, flags: int) -> int:
        nonlocal target_fd
        fd = original_open(path, flags)
        if path == target:
            target_fd = fd
        return fd

    def failed_read(fd: int, size: int) -> bytes:
        if fd == target_fd:
            raise OSError("API_KEY=TOP_SECRET")
        return os.read(fd, size)

    def observed_close(fd: int) -> None:
        closed.append(fd)
        original_close(fd)

    monkeypatch.setattr(runner, "_open_readonly", observed_open)
    monkeypatch.setattr(runner, "_read_fd_chunk", failed_read)
    monkeypatch.setattr(runner, "_close_read_fd", observed_close)
    _assert_reason(
        runner.REASON_CRITICAL_FILE_UNREADABLE,
        lambda: runner.run_airline_sealed_trace_replay_v01(
            package_dir=package,
            anchor_path=fixture.anchor_path,
            output_path=tmp_path / "read-failure.json",
        ),
    )
    assert target_fd is not None
    assert target_fd in closed
    with pytest.raises(OSError):
        os.fstat(target_fd)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("expected_manifest_core_hash", "0" * 64),
        ("source_package_ref", "wrong-package"),
        ("transaction_id", "wrong-transaction"),
        ("ledger_id", "wrong-ledger"),
        ("source_package_hash", "0" * 64),
        ("chain_tail_hash", "0" * 64),
        ("manifest_artifact_ref", "wrong.json"),
        ("verification_artifact_ref", "wrong.json"),
        ("signature_verified", True),
        ("anchored_pass_claimed", True),
        ("replay_allowed", True),
        ("source_package_relpath", "/absolute/package"),
        ("source_package_relpath", "../package"),
        ("source_package_relpath", "fixtures/wrong"),
    ),
)
def test_anchor_contract_and_binding_mutations_fail_before_audit(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    fixture = packages[0]
    anchor = dict(fixture.anchor); anchor[field] = value
    path = tmp_path / "anchor.json"; path.write_bytes(_json_bytes(anchor))
    calls = 0
    def audit(*args: object, **kwargs: object) -> object:
        nonlocal calls; calls += 1; return object()
    monkeypatch.setattr(runner.ledger_audit, "collect_airline_transaction_artifact_ledger_audit_v01", audit)
    error = _assert_reason(
        runner.REASON_ANCHOR_CONTRACT_MISMATCH if field in {
            "manifest_artifact_ref", "verification_artifact_ref", "signature_verified",
            "anchored_pass_claimed", "replay_allowed", "source_package_ref",
            "source_package_relpath",
        } else runner.REASON_ANCHOR_PACKAGE_IDENTITY_MISMATCH,
        lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=path, output_path=tmp_path / "out.json"),
    )
    assert calls == 0
    assert "API_KEY" not in "".join(traceback.format_exception(error))


@pytest.mark.parametrize("raw", (b"\xff", b"\xef\xbb\xbf{}", b"{", b'{"x":1,"x":2}'))
def test_anchor_parse_failures_are_stable(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    raw: bytes,
) -> None:
    path = tmp_path / "bad_anchor.json"; path.write_bytes(raw)
    _assert_reason(runner.REASON_ANCHOR_PARSE_FAILED, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=packages[0].package_dir, anchor_path=path, output_path=tmp_path / "out.json"))


def test_anchor_path_guards(packages: tuple[RunnerFixture, RunnerFixture], tmp_path: Path) -> None:
    fixture = packages[0]
    _assert_reason(runner.REASON_ANCHOR_PATH_INVALID, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=tmp_path / "missing", output_path=tmp_path / "a.json"))
    link = tmp_path / "anchor_link"; link.symlink_to(fixture.anchor_path)
    _assert_reason(runner.REASON_ANCHOR_PATH_SYMLINK, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=link, output_path=tmp_path / "b.json"))
    dangling = tmp_path / "dangling_anchor"; dangling.symlink_to(tmp_path / "missing-anchor")
    _assert_reason(runner.REASON_ANCHOR_PATH_SYMLINK, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=dangling, output_path=tmp_path / "d.json"))
    directory = tmp_path / "anchor_directory"; directory.mkdir()
    _assert_reason(runner.REASON_ANCHOR_NOT_REGULAR, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=directory, output_path=tmp_path / "e.json"))
    inside = fixture.package_dir / "anchor.json"; inside.write_bytes(fixture.anchor_path.read_bytes())
    _assert_reason(runner.REASON_ANCHOR_INSIDE_PACKAGE, lambda: runner.run_airline_sealed_trace_replay_v01(package_dir=fixture.package_dir, anchor_path=inside, output_path=tmp_path / "c.json"))


def test_anchor_unreadable_descriptor_failure(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = packages[0]
    original_open = runner._open_readonly

    def unreadable_open(path: Path, flags: int) -> int:
        if path == fixture.anchor_path:
            raise PermissionError("API_KEY=TOP_SECRET")
        return original_open(path, flags)

    monkeypatch.setattr(runner, "_open_readonly", unreadable_open)
    _assert_reason(
        runner.REASON_ANCHOR_UNREADABLE,
        lambda: _run(fixture, tmp_path / "anchor-unreadable.json"),
    )


def test_audit_exception_is_stable_and_short_circuits(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection_calls = 0
    def audit(*args: object, **kwargs: object) -> object:
        raise RuntimeError("API_KEY=TOP_SECRET")
    def collection(*args: object, **kwargs: object) -> object:
        nonlocal collection_calls; collection_calls += 1; return object()
    monkeypatch.setattr(runner.ledger_audit, "collect_airline_transaction_artifact_ledger_audit_v01", audit)
    monkeypatch.setattr(runner.replay_collector, "collect_airline_sealed_trace_replay_from_package_snapshot_v01", collection)
    error = _assert_reason(runner.REASON_LEDGER_AUDIT_FAILED, lambda: _run(packages[0], tmp_path / "out.json"))
    assert collection_calls == 0
    assert "TOP_SECRET" not in "".join(traceback.format_exception(error))


@pytest.mark.parametrize("change", ({"final_status": runner.STATUS_FAIL_CLOSED}, {"files_read_count": 8}, {"artifact_ids_unique": False}, {"semantic_rerun_count": 1}, {"timeline_rows": ()}))
def test_invalid_audit_report_stops_before_collection(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, object],
) -> None:
    fixture = packages[0]
    valid = runner.ledger_audit.collect_airline_transaction_artifact_ledger_audit_v01(artifact_dir=fixture.package_dir, env={})
    monkeypatch.setattr(runner.ledger_audit, "collect_airline_transaction_artifact_ledger_audit_v01", lambda **kwargs: replace(valid, **change))
    calls = 0
    def collection(*args: object, **kwargs: object) -> object:
        nonlocal calls; calls += 1; return object()
    monkeypatch.setattr(runner.replay_collector, "collect_airline_sealed_trace_replay_from_package_snapshot_v01", collection)
    _assert_reason(runner.REASON_LEDGER_AUDIT_REPORT_INVALID, lambda: _run(fixture, tmp_path / "out.json"))
    assert calls == 0


def test_collection_exception_is_sanitized(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runner.replay_collector, "collect_airline_sealed_trace_replay_from_package_snapshot_v01", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("API_KEY=TOP_SECRET")))
    error = _assert_reason(runner.REASON_REPLAY_COLLECTION_FAILED, lambda: _run(packages[0], tmp_path / "out.json"))
    assert "TOP_SECRET" not in "".join(traceback.format_exception(error))


@pytest.mark.parametrize(
    "result_kind",
    (
        "wrong_type",
        "fail_closed",
        "foreign_package",
        "wrong_manifest_hash",
    ),
)
def test_invalid_collection_results_fail_closed(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    result_kind: str,
) -> None:
    fixture = packages[0]
    if result_kind == "wrong_type":
        result: object = object()
    elif result_kind == "fail_closed":
        from tests import test_airline_sealed_trace_replay_v01 as replay_helpers

        replay_fixture = replay_helpers._fixture(ledger_contracts.OFFER_A_ID)
        result = replay_helpers._run(
            replay_fixture.replay_input,
            critical_package_bytes_unchanged=False,
        )
        assert result.replay_status == runner.STATUS_FAIL_CLOSED
    elif result_kind == "foreign_package":
        result = _run(packages[1], tmp_path / "foreign-seed.json")
        assert result.source_package_ref != fixture.anchor["source_package_ref"]
    else:
        from tests import test_airline_sealed_trace_replay_collector_v01 as collector_helpers

        collector_fixture = collector_helpers._fixture(
            ledger_contracts.OFFER_A_ID,
            package_ref=str(fixture.anchor["source_package_ref"]),
            source_variant="foreign-source-bytes",
        )
        result = collector_helpers._collect(collector_fixture)
        assert result.source_package_ref == fixture.anchor["source_package_ref"]
        assert result.manifest_core_hash != fixture.anchor["expected_manifest_core_hash"]

    calls = 0

    def collection(**kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return result

    monkeypatch.setattr(
        runner.replay_collector,
        "collect_airline_sealed_trace_replay_from_package_snapshot_v01",
        collection,
    )
    output = tmp_path / f"{result_kind}.json"
    _assert_reason(
        runner.REASON_REPLAY_COLLECTION_FAILED,
        lambda: _run(fixture, output),
    )
    assert calls == 1
    assert not output.exists()


@pytest.mark.parametrize(
    "relative_ref",
    (
        crypto_contracts.REQUIRED_SOURCE_FILE_REFS[1],
        replay_contracts.MANIFEST_ARTIFACT_REF,
        replay_contracts.STORED_VERIFICATION_ARTIFACT_REF,
    ),
)
def test_post_snapshot_mutation_maps_to_collection_failure(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    relative_ref: str,
) -> None:
    fixture = packages[0]
    original = runner.replay_collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01
    def collection(**kwargs: object) -> object:
        path = fixture.package_dir / relative_ref
        path.write_bytes(path.read_bytes() + b" ")
        return original(**kwargs)
    monkeypatch.setattr(runner.replay_collector, "collect_airline_sealed_trace_replay_from_package_snapshot_v01", collection)
    try:
        _assert_reason(runner.REASON_REPLAY_COLLECTION_FAILED, lambda: _run(fixture, tmp_path / "out.json"))
    finally:
        for name, raw in fixture.initial_bytes:
            (fixture.package_dir / name).write_bytes(raw)


def test_output_pre_guards_do_not_modify_existing(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
) -> None:
    fixture = packages[0]
    existing = tmp_path / "existing.json"; existing.write_bytes(b"user")
    _assert_reason(runner.REASON_OUTPUT_ALREADY_EXISTS, lambda: _run(fixture, existing))
    assert existing.read_bytes() == b"user"
    link = tmp_path / "link.json"; link.symlink_to(tmp_path / "missing-target")
    _assert_reason(runner.REASON_OUTPUT_SYMLINK, lambda: _run(fixture, link))
    _assert_reason(runner.REASON_OUTPUT_INSIDE_PACKAGE, lambda: _run(fixture, fixture.package_dir / "report.json"))


@pytest.mark.parametrize("parent_kind", ("missing", "file", "symlink"))
def test_output_parent_guards(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    parent_kind: str,
) -> None:
    fixture = packages[0]
    parent = tmp_path / f"{parent_kind}-parent"
    if parent_kind == "file":
        parent.write_bytes(b"user")
    elif parent_kind == "symlink":
        target = tmp_path / "real-parent"
        target.mkdir()
        parent.symlink_to(target, target_is_directory=True)
    _assert_reason(
        runner.REASON_OUTPUT_PARENT_INVALID,
        lambda: _run(fixture, parent / "report.json"),
    )


def test_serialization_failure_is_stable(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        runner,
        "_serialize_plain_report",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("API_KEY=TOP_SECRET")
        ),
    )
    output = tmp_path / "serialization.json"
    error = _assert_reason(
        runner.REASON_OUTPUT_SERIALIZATION_FAILED,
        lambda: _run(packages[0], output),
    )
    assert "TOP_SECRET" not in "".join(traceback.format_exception(error))
    assert not output.exists()


@pytest.mark.parametrize(
    ("error_number", "reason"),
    (
        (errno.EACCES, runner.REASON_OUTPUT_OPEN_FAILED),
        (errno.EEXIST, runner.REASON_OUTPUT_ALREADY_EXISTS),
    ),
)
def test_exclusive_open_failures(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
    reason: str,
) -> None:
    output = tmp_path / f"open-{error_number}.json"

    def failed_open(path: Path) -> int:
        if error_number == errno.EEXIST:
            path.write_bytes(b"race-user")
        raise OSError(error_number, "API_KEY=TOP_SECRET")

    monkeypatch.setattr(runner, "_exclusive_open", failed_open)
    error = _assert_reason(reason, lambda: _run(packages[0], output))
    assert "TOP_SECRET" not in "".join(traceback.format_exception(error))
    if error_number == errno.EEXIST:
        assert output.read_bytes() == b"race-user"
    else:
        assert not output.exists()


@pytest.mark.parametrize(
    ("seam", "replacement", "reason"),
    (
        ("_write_output", lambda fd, raw: len(raw) - 1, runner.REASON_OUTPUT_WRITE_FAILED),
        ("_write_output", lambda fd, raw: (_ for _ in ()).throw(OSError("API_KEY=TOP_SECRET")), runner.REASON_OUTPUT_WRITE_FAILED),
        ("_flush_output", lambda fd: (_ for _ in ()).throw(OSError("flush")), runner.REASON_OUTPUT_WRITE_FAILED),
        ("_close_output", lambda fd: (_ for _ in ()).throw(OSError("close")), runner.REASON_OUTPUT_CLOSE_FAILED),
        ("_reread_output", lambda path, ownership: (_ for _ in ()).throw(OSError("reread")), runner.REASON_OUTPUT_REREAD_FAILED),
        ("_reread_output", lambda path, ownership: b"{}\n", runner.REASON_OUTPUT_CONTENT_MISMATCH),
    ),
)
def test_writer_failures_cleanup_owned_output(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    seam: str,
    replacement: object,
    reason: str,
) -> None:
    output = tmp_path / "fault.json"
    monkeypatch.setattr(runner, seam, replacement)
    _assert_reason(reason, lambda: _run(packages[0], output))
    assert not output.exists() and not output.is_symlink()


def test_cleanup_failure_has_separate_reason(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "cleanup.json"
    monkeypatch.setattr(runner, "_write_output", lambda fd, raw: 0)
    monkeypatch.setattr(runner, "_unlink_owned_output", lambda path, ownership: (_ for _ in ()).throw(OSError("cleanup")))
    _assert_reason(runner.REASON_OUTPUT_CLEANUP_FAILED, lambda: _run(packages[0], output))


def test_path_replacement_during_write_never_unlinks_user_file(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "replacement.json"
    moved = tmp_path / "invocation-owned-partial.json"
    replacement_bytes = b"user-owned-replacement"

    def replace_during_write(fd: int, raw: bytes) -> int:
        os.write(fd, b"partial")
        output.rename(moved)
        output.write_bytes(replacement_bytes)
        return 0

    monkeypatch.setattr(runner, "_write_output", replace_during_write)
    try:
        _assert_reason(
            runner.REASON_OUTPUT_CLEANUP_FAILED,
            lambda: _run(packages[0], output),
        )
        assert output.read_bytes() == replacement_bytes
        assert moved.read_bytes() == b"partial"
    finally:
        if output.exists() or output.is_symlink():
            output.unlink()
        if moved.exists() or moved.is_symlink():
            moved.unlink()


@pytest.mark.parametrize("replacement_kind", ("regular", "symlink"))
def test_post_close_replacement_is_not_accepted_or_deleted(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement_kind: str,
) -> None:
    output = tmp_path / f"post-close-{replacement_kind}.json"
    moved = tmp_path / f"post-close-owned-{replacement_kind}.json"
    user_target = tmp_path / f"user-target-{replacement_kind}.json"
    original_reread = runner._reread_output

    def replace_before_reread(
        path: Path,
        ownership: runner._InvocationOwnedOutputV01,
    ) -> bytes:
        path.rename(moved)
        if replacement_kind == "regular":
            path.write_bytes(moved.read_bytes())
        else:
            user_target.write_bytes(b"user-target")
            path.symlink_to(user_target)
        return original_reread(path, ownership)

    monkeypatch.setattr(runner, "_reread_output", replace_before_reread)
    try:
        _assert_reason(
            runner.REASON_OUTPUT_CLEANUP_FAILED,
            lambda: _run(packages[0], output),
        )
        assert moved.exists()
        if replacement_kind == "regular":
            assert output.read_bytes() == moved.read_bytes()
        else:
            assert output.is_symlink()
            assert user_target.read_bytes() == b"user-target"
    finally:
        if output.exists() or output.is_symlink():
            output.unlink()
        if moved.exists() or moved.is_symlink():
            moved.unlink()
        if user_target.exists() or user_target.is_symlink():
            user_target.unlink()


def test_owned_path_missing_before_cleanup_is_cleanup_failure(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "missing-owned-path.json"

    def unlink_during_write(fd: int, raw: bytes) -> int:
        output.unlink()
        os.write(fd, b"partial")
        return 0

    monkeypatch.setattr(runner, "_write_output", unlink_during_write)
    _assert_reason(
        runner.REASON_OUTPUT_CLEANUP_FAILED,
        lambda: _run(packages[0], output),
    )
    assert not output.exists()


def test_close_failure_uses_raw_close_fallback_and_cleans_owned_file(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "raw-close-fallback.json"
    raw_close_calls = 0
    original_raw_close = runner._raw_close_output

    def failed_close(fd: int) -> None:
        raise OSError("close seam failed")

    def observed_raw_close(fd: int) -> None:
        nonlocal raw_close_calls
        raw_close_calls += 1
        original_raw_close(fd)

    monkeypatch.setattr(runner, "_close_output", failed_close)
    monkeypatch.setattr(runner, "_raw_close_output", observed_raw_close)
    _assert_reason(
        runner.REASON_OUTPUT_CLOSE_FAILED,
        lambda: _run(packages[0], output),
    )
    assert raw_close_calls == 1
    assert not output.exists()


def test_close_noop_is_detected_and_raw_fallback_cleans_owned_file(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "noop-close.json"
    raw_close_calls = 0
    original_raw_close = runner._raw_close_output

    def observed_raw_close(fd: int) -> None:
        nonlocal raw_close_calls
        raw_close_calls += 1
        original_raw_close(fd)

    monkeypatch.setattr(runner, "_close_output", lambda fd: None)
    monkeypatch.setattr(runner, "_raw_close_output", observed_raw_close)
    _assert_reason(
        runner.REASON_OUTPUT_CLOSE_FAILED,
        lambda: _run(packages[0], output),
    )
    assert raw_close_calls == 1
    assert not output.exists()


def test_normal_and_fallback_close_failure_is_cleanup_failure(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "unclosed.json"
    captured_fd: int | None = None
    original_exclusive_open = runner._exclusive_open

    def observed_open(path: Path) -> int:
        nonlocal captured_fd
        captured_fd = original_exclusive_open(path)
        return captured_fd

    monkeypatch.setattr(runner, "_exclusive_open", observed_open)
    monkeypatch.setattr(
        runner,
        "_close_output",
        lambda fd: (_ for _ in ()).throw(OSError("normal close failed")),
    )
    monkeypatch.setattr(
        runner,
        "_raw_close_output",
        lambda fd: (_ for _ in ()).throw(OSError("raw close failed")),
    )
    try:
        _assert_reason(
            runner.REASON_OUTPUT_CLEANUP_FAILED,
            lambda: _run(packages[0], output),
        )
        assert output.exists()
    finally:
        if captured_fd is not None:
            try:
                os.close(captured_fd)
            except OSError:
                pass
        if output.exists() or output.is_symlink():
            output.unlink()


@pytest.mark.parametrize("parse_result", ("raise", "mismatch"))
def test_written_output_parse_failures_cleanup_owned_file(
    packages: tuple[RunnerFixture, RunnerFixture],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    parse_result: str,
) -> None:
    output = tmp_path / f"parse-failure-{parse_result}.json"
    original_parse = runner._parse_output_document
    parse_calls = 0

    def parse_output(raw: bytes) -> dict[str, object]:
        nonlocal parse_calls
        parse_calls += 1
        if parse_calls == 1:
            return original_parse(raw)
        if parse_result == "raise":
            raise ValueError("API_KEY=TOP_SECRET")
        return {}

    monkeypatch.setattr(runner, "_parse_output_document", parse_output)
    error = _assert_reason(
        runner.REASON_OUTPUT_CONTENT_MISMATCH,
        lambda: _run(packages[0], output),
    )
    if parse_result == "raise":
        assert "TOP_SECRET" not in "".join(traceback.format_exception(error))
    assert parse_calls == 2
    assert not output.exists()


def test_static_runner_boundary() -> None:
    source = Path(MODULE_PATH).read_text()
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    forbidden_import_fragments = (
        "run_tri_party_airline_live_semantic_lane_v01",
        "transaction_artifact_ledger_collector",
        "requests", "urllib", "socket", "subprocess", "provider",
        "root_artifact_attestation",
    )
    assert all(not any(fragment in name for fragment in forbidden_import_fragments) for name in imports)
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert calls.count("collect_airline_transaction_artifact_ledger_audit_v01") == 1
    assert calls.count("collect_airline_sealed_trace_replay_from_package_snapshot_v01") == 1
    assert calls.count("verify_airline_crypto_artifact_seal_v01") == 0
    assert calls.count("build_airline_sealed_trace_replay_timeline_v01") == 0
    assert calls.count("verify_airline_sealed_trace_replay_v01") == 0
    for token in (
        ".glob(",
        ".rglob(",
        ".read_bytes(",
        ".tmp/",
        "asdict",
        "eval(",
        "exec(",
        "pickle",
    ):
        assert token not in source
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set))
