"""Offline EWS4 package boundaries over one real accepted completed export.

No Work, D, E, Workspace, browser, provider, or live effect is run. Supplied
matching pins below are TEST_SUPPLIED_PIN, never independent lead acceptance.
"""
import copy
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest


GUARD_POINTS = (
    ("hedgehog.domains.ephemeral_workspace.semantic_roles_v01", "ControlledProvider.respond"),
    ("hedgehog.domains.ephemeral_workspace.semantic_adapter_v01", "CapturedProvider.respond"),
    ("hedgehog.domains.ephemeral_workspace.semantic_adapter_v01", "LiveProvider.respond"),
    ("hedgehog.domains.ephemeral_workspace.semantic_adapter_v01", "collect"),
    ("hedgehog.domains.ephemeral_workspace.kernel_adapter_v01", "CurrentSource.__init__"),
    ("hedgehog.domains.ephemeral_workspace.kernel_adapter_v01", "CurrentSource.sample"),
    ("hedgehog.domains.ephemeral_workspace.kernel_adapter_v01", "root_review"),
    ("hedgehog.domains.ephemeral_workspace.kernel_adapter_v01", "materialize"),
    ("hedgehog.domains.ephemeral_workspace.kernel_adapter_v01", "dispatch"),
    ("hedgehog.kernel.root_decision_v01", "decide_root_v01"),
    ("hedgehog.work_execution_host_v01", "build_root_work_execution_host_v01"),
    ("hedgehog.work_execution_host_v01", "dispatch_current_action_v01"),
    ("hedgehog.work_execution_host_v01", "execute_admitted_pure_work_v01"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "collect"),
    ("hedgehog.domains.ephemeral_workspace.capability_registry_v01", "execute_compile_v01"),
    ("hedgehog.domains.ephemeral_workspace.capability_registry_v01", "execute_contract_v01"),
    ("hedgehog.domains.ephemeral_workspace.capability_registry_v01", "execute_media_contract_v01"),
    ("hedgehog.domains.ephemeral_workspace.capability_registry_v01", "execute_command_v01"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.__init__"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.command"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.execute_effect"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.approve"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.prepare_media"),
    ("hedgehog.domains.ephemeral_workspace.session_runtime_v01", "Workspace.withdraw_audio"),
    ("hedgehog.domains.ephemeral_workspace.local_services_v01", "Service.__init__"),
    ("hedgehog.domains.ephemeral_workspace.local_services_v01", "Service.rpc"),
    ("hedgehog.domains.ephemeral_workspace.local_services_v01", "worker"),
    ("hedgehog.kernel.fractal_runtime_v02", "run_fractal_runtime_v02"),
    ("hedgehog.kernel.continuous_delta_runtime_v01", "run_continuous_delta_runtime_v01"),
    ("hedgehog.kernel.effect_firewall_v01", "authorize_effect_request_v01"),
    ("hedgehog.kernel.effect_firewall_v01", "execute_mock_effect_v01"),
    ("hedgehog.kernel.effect_firewall_v01", "execute_bound_effect_v01"),
    ("hedgehog.action_commit_packet_v02", "build_native_root_bound_action_commit_packet_v01"),
    ("hedgehog.kernel.effect_firewall_v01", "bind_native_action_authorization_v01"),
    ("subprocess", "Popen"),
    ("os", "system"),
    ("socket", "create_connection"),
    ("socket", "getaddrinfo"),
    ("socket", "socket.connect"),
    ("socket", "socket.connect_ex"),
    ("socket", "socket.bind"),
    ("socket", "socket.sendto"),
    ("urllib.request", "urlopen"),
    ("urllib.request", "OpenerDirector.open"),
    ("http.client", "HTTPConnection.connect"),
    ("http.client", "HTTPSConnection.connect"),
)


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


class _ObservedRows(list):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def append(self, value):
        super().append(value)
        self.flush()

    def flush(self):
        self.path.write_bytes(_json_bytes({
            "schema": "ews4_test_observed_no_call_guards_v01", "rows": self,
            "pin_scope": "TEST_SUPPLIED_PIN", "independent_lead_acceptance": False,
            "validator_replacements": 0}))


def _loaded_source_map(candidate, ledger_path):
    """Observe actual imported file bindings and check candidate postimage pins."""
    adapter = importlib.import_module("hedgehog.domains.ephemeral_workspace.sealed_evidence_v01")
    cli = importlib.import_module("demo.run_ephemeral_workspace_evidence_v01")
    modules = [adapter, cli, adapter.abi, adapter.integrity, adapter.profile,
               adapter.package, adapter.anchor, adapter.replay,
               importlib.import_module("hedgehog.context_packets"),
               importlib.import_module("hedgehog.structured_rationale"),
               importlib.import_module("hedgehog.semantic_reasoning_adapter"),
               importlib.import_module("hedgehog.kernel.execution_mode_router_v01")]
    ledger = {row["path"]: row for row in json.loads(ledger_path.read_bytes())}
    observed = []
    for module in modules:
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(candidate)
        relative = path.relative_to(candidate).as_posix()
        body = path.read_bytes()
        entry = {"module": module.__name__, "loaded_file": str(path),
                 "relative_path": relative, "sha256": _sha(body), "bytes": len(body),
                 "inside_candidate": True, "candidate_ledger_match": None}
        if relative in ledger:
            assert _sha(body) == ledger[relative]["sha256"]
            assert len(body) == ledger[relative]["bytes"]
            entry["candidate_ledger_match"] = True
        observed.append(entry)
    test_path = Path(__file__).resolve()
    relative = test_path.relative_to(candidate).as_posix()
    test_bytes = test_path.read_bytes()
    assert _sha(test_bytes) == ledger[relative]["sha256"]
    assert len(test_bytes) == ledger[relative]["bytes"]
    observed.append({"module": "executed_test_module", "loaded_file": str(test_path),
                     "relative_path": relative, "sha256": _sha(test_bytes),
                     "bytes": len(test_bytes), "inside_candidate": True,
                     "candidate_ledger_match": True})
    assert all(next(row for row in observed if row["module"] == name)[
        "candidate_ledger_match"] is True for name in (adapter.__name__, cli.__name__))
    return {"scope": "actual_imported_source_files", "rows": observed,
            "source_ledger_sha256": _sha(ledger_path.read_bytes()),
            "pure_common_validators_replaced": False}


@contextmanager
def _runtime_guard(label, rows):
    """Count and deny actual live entry points; never replace a validator."""
    started = time.monotonic()
    resolved = []
    for module_name, attribute in GUARD_POINTS:
        target = importlib.import_module(module_name)
        pieces = attribute.split(".")
        for piece in pieces[:-1]:
            target = getattr(target, piece)
        getattr(target, pieces[-1])  # Missing instrumentation is a test failure.
        resolved.append((target, pieces[-1], module_name + "." + attribute))
    counts = {name: 0 for _, _, name in resolved}
    counts["sidecar.selection_json.write_open"] = 0
    original_open = io.open

    def forbidden(name):
        def deny(*args, **kwargs):
            counts[name] += 1
            raise AssertionError("offline_replay_forbidden_call:" + name)
        return deny

    def guard_open(file, mode="r", *args, **kwargs):
        if (isinstance(file, (str, bytes, os.PathLike))
                and Path(os.fsdecode(file)).name == "selection.json"
                and any(flag in mode for flag in "wax+")):
            return forbidden("sidecar.selection_json.write_open")(file, mode)
        return original_open(file, mode, *args, **kwargs)

    with pytest.MonkeyPatch.context() as patch:
        for target, name, full_name in resolved:
            patch.setattr(target, name, forbidden(full_name))
        patch.setattr(io, "open", guard_open)
        try:
            yield counts
        finally:
            rows.append({"scenario": label, "observed_attempts": dict(counts),
                         "instrumentation_installed": True, "seconds": time.monotonic() - started,
                         "all_observed_attempts_zero": not any(counts.values())})
            assert not any(counts.values()), counts


@pytest.fixture(scope="session")
def real_package():
    required = ("EWS4_INPUT_ROOT", "EWS4_SOURCE_LEDGER", "EWS4_EXECUTION_HEAD", "EWS4_TEST_EVIDENCE",
                "EWS4R_SUPPLEMENTAL_PROOF_ROOT", "EWS4R_SUPPLEMENTAL_MANIFEST_SHA256")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.fail("real accepted export requires: " + ", ".join(missing))
    evidence = Path(os.environ["EWS4_TEST_EVIDENCE"])
    evidence.mkdir(parents=True, exist_ok=True)
    root = evidence / "export_material"
    root.mkdir(exist_ok=False)
    observations = _ObservedRows(evidence / "observed_no_call_guards.json")
    with _runtime_guard("single_real_export", observations):
        adapter = importlib.import_module(
            "hedgehog.domains.ephemeral_workspace.sealed_evidence_v01")
        source_map = _loaded_source_map(Path(__file__).resolve().parents[1],
            Path(os.environ["EWS4_SOURCE_LEDGER"]))
        (evidence / "source_consumer_map.json").write_bytes(_json_bytes(source_map))
        cli = importlib.import_module("demo.run_ephemeral_workspace_evidence_v01")
        arguments = ["export", "--input-root", os.environ["EWS4_INPUT_ROOT"],
            "--output-dir", str(root / "package"),
            "--execution-head", os.environ["EWS4_EXECUTION_HEAD"],
            "--source-ledger", os.environ["EWS4_SOURCE_LEDGER"],
            "--supplemental-proof-root", os.environ["EWS4R_SUPPLEMENTAL_PROOF_ROOT"],
            "--expected-supplemental-manifest-sha256", os.environ["EWS4R_SUPPLEMENTAL_MANIFEST_SHA256"]]
        output_buffer = io.BytesIO()
        output_stream = io.TextIOWrapper(output_buffer, encoding="utf-8")
        errors = io.StringIO()
        (evidence / "single_export_cli_command.json").write_bytes(_json_bytes({
            "entrypoint": "demo.run_ephemeral_workspace_evidence_v01.main",
            "argv": arguments, "execution_scope": "in_process_under_pytest_and_actual_no_call_guards",
            "one_real_export": True}))
        started = time.monotonic()
        with redirect_stdout(output_stream), redirect_stderr(errors):
            exit_code = cli.main(arguments)
        output_stream.flush()
        output = output_buffer.getvalue()
        output_stream.detach()
        (evidence / "single_export_cli_stdout.json").write_bytes(output)
        (evidence / "single_export_cli_stderr.log").write_text(errors.getvalue(), encoding="utf-8")
        (evidence / "single_export_cli_exit.json").write_bytes(_json_bytes({
            "exit_code": exit_code, "seconds": time.monotonic() - started,
            "stdout_sha256": _sha(output), "stderr_sha256": _sha(errors.getvalue().encode())}))
        assert exit_code == 0, output.decode("utf-8")
        report = json.loads(output)
    publication = root / "detached_publication.json"
    publication.write_bytes(_json_bytes(report["publication"]))
    pin = report["publication"]["anchor_publication_id"]
    assert isinstance(pin, str) and len(pin) == 64
    value = {"adapter": adapter, "path": root / "package",
             "report": report, "publication_path": publication, "pin": pin,
             "observations": observations, "evidence": evidence}
    (evidence / "single_export_report.json").write_bytes(_json_bytes(report))
    try:
        yield value
    finally:
        (evidence / "observed_no_call_guards.json").write_bytes(_json_bytes({
            "schema": "ews4_test_observed_no_call_guards_v01", "rows": observations,
            "pin_scope": "TEST_SUPPLIED_PIN", "independent_lead_acceptance": False,
            "validator_replacements": 0}))


def _clone(real_package, tmp_path):
    target = tmp_path / "package"
    shutil.copytree(real_package["path"], target)
    return target


def _checked_inventory(path):
    path = Path(path)
    if path.is_symlink():
        return [{"path": "PACKAGE_ROOT", "kind": "symlink",
                 "target_text_sha256": _sha(os.readlink(path).encode())}]
    if path.is_file():
        body = path.read_bytes()
        return [{"path": "PACKAGE_FILE", "kind": "regular", "bytes": len(body), "sha256": _sha(body)}]
    result = []
    for entry in sorted(path.iterdir()):
        if entry.is_symlink():
            result.append({"path": entry.name, "kind": "symlink",
                           "target_text_sha256": _sha(os.readlink(entry).encode())})
        elif entry.is_file():
            body = entry.read_bytes()
            result.append({"path": entry.name, "kind": "regular", "bytes": len(body), "sha256": _sha(body)})
        else:
            result.append({"path": entry.name, "kind": "directory"})
    return result


def _save_result(real_package, label, result):
    directory = real_package["evidence"] / "verification_results"
    directory.mkdir(exist_ok=True)
    encoded = _json_bytes(result)
    filename = "%03d_%s.json" % (len(list(directory.iterdir())) + 1, _sha(label.encode())[:12])
    (directory / filename).write_bytes(encoded)
    publication = result.get("publication", {})
    row = {"result_file": "verification_results/" + filename,
           "result_bytes": len(encoded), "result_sha256": _sha(encoded),
           "result_status": result.get("status"),
           "computed_publication_id": publication.get("anchor_publication_id"),
           "pin_scope": "TEST_SUPPLIED_PIN", "independent_lead_acceptance": False}
    real_package["observations"][-1].update(row)
    real_package["observations"].flush()


def _verify(real_package, path, label, **kwargs):
    checked = _checked_inventory(path)
    try:
        with _runtime_guard(label, real_package["observations"]):
            result = real_package["adapter"].verify_package(path, **kwargs)
    finally:
        row = real_package["observations"][-1]
        row.update(checked_inventory=checked, expected_anchor=kwargs.get("expected_anchor"),
                   require_anchor=kwargs.get("require_anchor", False), pin_scope="TEST_SUPPLIED_PIN")
        if kwargs.get("publication_path") is not None:
            row["detached_publication_sha256"] = _sha(Path(kwargs["publication_path"]).read_bytes())
        real_package["observations"].flush()
    _save_result(real_package, label, result)
    return result


def _reject(real_package, path, label, **kwargs):
    with pytest.raises(ValueError) as caught:
        _verify(real_package, path, label, **kwargs)
    reason = str(caught.value)
    assert reason and "offline_replay_forbidden_call" not in reason
    real_package["observations"][-1]["rejection_reason"] = reason
    real_package["observations"].flush()
    return reason


def _public_file(package):
    return sorted(path for path in package.glob("*.json")
                  if path.name not in {"sealed_package_manifest_v01.json",
                                       "kernel_integrity_v01.json"})[0]


def test_real_export_is_evidence_only_and_unanchored(real_package):
    report = _verify(real_package, real_package["path"], "unanchored_reopen")
    assert real_package["report"]["publication"]["anchor_status"] == "EVIDENCE_ONLY"
    assert real_package["report"]["publication"]["external_anchor_supplied_at_publication"] is False
    assert real_package["report"]["publication"]["external_anchor_verified_at_publication"] is False
    assert report["status"] == "SELF_CONSISTENT_UNANCHORED"
    assert report["sealed_replay"] is None and report["anchor_verification"] is None
    graph = real_package["report"]["private_original_graph_verification"]
    assert graph["baseline_artifacts"] == 83 and graph["retained_artifacts"] == 156
    assert graph["baseline_unchanged_in_retained"] is True
    assert graph["scope"] == "ORIGINAL_ABI_GRAPHS_AND_SEPARATE_PRIVATE_AGGREGATE_WRAPPERS"
    assert graph["native_canonical_reference_status"] == "UNSUPPORTED_NATIVE_SCHEMA"
    assert graph["original_native_manifest_pass_claimed"] is False
    for name, count in (("baseline_private_audit", 83), ("retained_private_audit", 156)):
        audit = graph[name]
        assert audit["native_artifact_count"] == count
        assert audit["native_abi_bundle_status"] == "PASS"
        assert audit["native_abi_bundle_errors"] == []
        assert audit["native_canonical_reference_status"] == "UNSUPPORTED_NATIVE_SCHEMA"
        assert audit["original_native_manifest_pass_claimed"] is False
        schema_rows = audit["native_schema_conversion"]
        assert sum(row["artifact_count"] for row in schema_rows) == count
        assert all(row["converted_count"] + row["unsupported_count"] == row["artifact_count"]
                   for row in schema_rows)
        refusals = audit["native_conversion_refusals"]
        assert len(refusals) == sum(row["unsupported_count"] for row in schema_rows) > 0
        assert all(row["reason"] == "canonical_artifact_ref_conversion_failed" for row in refusals)
        assert audit["private_aggregate_wrapper_count"] == 1
        assert audit["private_aggregate_manifest_scope"] == (
            "ONE_NEW_EVIDENCE_ONLY_WRAPPER_CONTAINING_UNCHANGED_NATIVE_GRAPH")
        assert audit["private_aggregate_seal"]["verification_status"] == "PASS"
        assert audit["private_aggregate_seal"]["artifact_count"] == 1
        assert audit["private_aggregate_replay"]["replay_status"] == "PASS"
        assert audit["private_aggregate_replay"]["artifact_count"] == 1
    projection = real_package["report"]["domain_projection"]
    assert projection["status"] == "PASS"
    attempt = projection["attempt_identity"]
    assert attempt["provider_mode"] == "deterministic_fixture"
    assert attempt["expected_actor_count"] == 3 and attempt["provider_call_budget"] == 0
    assert all(projection[key] == 0 for key in (
        "source_provider_call_count", "source_network_call_count", "source_gemini_call_count",
        "projection_provider_call_count", "projection_network_call_count", "projection_gemini_call_count",
        "created_authority_count", "created_permission_count", "real_world_effects_count"))


def test_explicit_matching_test_pin_reopens(real_package):
    report = _verify(real_package, real_package["path"], "matching_test_pin",
                     publication_path=real_package["publication_path"],
                     expected_anchor=real_package["pin"], require_anchor=True)
    assert report["status"] == "ANCHORED_PASS"
    anchored = report["anchor_verification"]
    assert anchored["verification_status"] == "ANCHORED_PASS"
    assert anchored["external_anchor_verified"] is True
    assert all(anchored[key] is False for key in (
        "signature_verified", "signer_identity_verified", "root_attestation_verified"))
    replayed = report["sealed_replay"]
    assert replayed["replay_status"] == "PASS"
    assert all(replayed[key] is True for key in (
        "integrity_verified", "continuity_verified", "anchor_verified"))
    assert replayed["source_file_count"] == replayed["reconstructed_file_count"] == 17
    assert replayed["source_artifact_count"] == replayed["reconstructed_artifact_count"] == 16
    for stem in ("manifest_id", "domain_projection_id", "package_content_hash",
                 "file_order_hash", "artifact_order_hash"):
        assert replayed["source_" + stem] == replayed["reconstructed_" + stem]
    assert all(replayed[key] == 0 for key in (
        "semantic_rerun_count", "root_decision_rerun_count", "corridor_rerun_count",
        "provider_call_count", "network_call_count", "gemini_call_count",
        "created_authority_count", "created_permission_count", "action_created_count",
        "receipt_created_count", "final_output_created_count", "real_world_effects_count"))


@pytest.mark.parametrize("pin", [None, "0" * 64, "wrong", "A" * 64])
def test_required_missing_wrong_or_malformed_pin_rejects(real_package, pin):
    _reject(real_package, real_package["path"], "required_pin_" + str(pin),
            publication_path=real_package["publication_path"],
            expected_anchor=pin, require_anchor=True)


@pytest.mark.parametrize("attack", ["corrupt", "missing", "extra", "truncated",
                                      "duplicate_key", "malformed", "symlink"])
def test_filesystem_and_json_attacks_fail_closed(real_package, tmp_path, attack):
    package = _clone(real_package, tmp_path)
    target = _public_file(package)
    if attack == "corrupt":
        target.write_bytes(target.read_bytes().replace(b":", b": ", 1))
    elif attack == "missing":
        target.unlink()
    elif attack == "extra":
        (package / "unexpected.json").write_bytes(b"{}\n")
    elif attack == "truncated":
        target.write_bytes(target.read_bytes()[:-7])
    elif attack == "duplicate_key":
        body = target.read_bytes()
        key = next(iter(json.loads(body)))
        duplicate = json.dumps(key).encode() + b":null,"
        target.write_bytes(b"{" + duplicate + body.lstrip()[1:])
    elif attack == "malformed":
        target.write_bytes(b"{not-json}\n")
    elif attack == "symlink":
        original = tmp_path / "outside.json"
        original.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(original)
    _reject(real_package, package, "filesystem_" + attack)


@pytest.mark.parametrize("unsafe_path", ["../outside.json", "/absolute.json",
                                          "nested/../../outside.json", "C:\\outside.json"])
def test_manifest_unsafe_paths_fail_closed(real_package, tmp_path, unsafe_path):
    package = _clone(real_package, tmp_path)
    path = package / "sealed_package_manifest_v01.json"
    value = json.loads(path.read_bytes())
    value["safe_file_records"][0]["logical_path"] = unsafe_path
    path.write_bytes(_json_bytes(value))
    _reject(real_package, package, "unsafe_manifest_path")


CHILD_REOPEN = r"""import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
spec = importlib.util.spec_from_file_location("ews4_test_guard", sys.argv[2])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows = module._ObservedRows(Path(sys.argv[6]).with_name("fresh_process_guards.json"))
with module._runtime_guard("fresh_process_matching_test_pin", rows):
    source_map = module._loaded_source_map(Path(sys.argv[1]), Path(sys.argv[7]))
    Path(sys.argv[6]).with_name("fresh_process_source_consumer_map.json").write_bytes(
        module._json_bytes(source_map))
    from hedgehog.domains.ephemeral_workspace import sealed_evidence_v01 as adapter
    def forbidden_export(*args, **kwargs):
        raise AssertionError("fresh_reopen_must_not_export")
    adapter.export_package = forbidden_export
    result = adapter.verify_package(Path(sys.argv[3]), publication_path=Path(sys.argv[4]),
                                    expected_anchor=sys.argv[5], require_anchor=True)
Path(sys.argv[6]).write_bytes(module._json_bytes({"report": result, "guards": rows,
    "process_identity": "fresh_python_process", "pin_scope": "TEST_SUPPLIED_PIN",
    "source_consumer_map": source_map}))
"""


def test_fresh_process_reopens_saved_bytes_without_export_or_live_calls(real_package):
    evidence = real_package["evidence"]
    helper = evidence / "fresh_process_reopen_v01.py"
    helper.write_text(CHILD_REOPEN, encoding="utf-8")
    result_path = evidence / "fresh_process_reopen_result.json"
    test_path = Path(__file__).resolve()
    candidate = test_path.parents[1]
    command = [sys.executable, "-I", "-B", str(helper), str(candidate), str(test_path),
               str(real_package["path"]), str(real_package["publication_path"]),
               real_package["pin"], str(result_path), os.environ["EWS4_SOURCE_LEDGER"]]
    started = time.monotonic()
    run = subprocess.run(command, capture_output=True, timeout=180, check=False,
                         env={"PATH": os.environ.get("PATH", ""),
                              "PYTHONDONTWRITEBYTECODE": "1"})
    (evidence / "fresh_process_stdout.log").write_bytes(run.stdout)
    (evidence / "fresh_process_stderr.log").write_bytes(run.stderr)
    (evidence / "fresh_process_command.json").write_bytes(_json_bytes({
        "argv": command, "environment": {"PATH": os.environ.get("PATH", ""),
        "PYTHONDONTWRITEBYTECODE": "1"}, "exit_code": run.returncode,
        "seconds": time.monotonic() - started, "helper_sha256": _sha(helper.read_bytes()),
        "test_source_sha256": _sha(test_path.read_bytes())}))
    assert run.returncode == 0, run.stderr.decode("utf-8", errors="replace")
    result = json.loads(result_path.read_bytes())
    assert result["report"]["status"] == "ANCHORED_PASS"
    assert result["guards"] and all(row["all_observed_attempts_zero"]
                                    for row in result["guards"])


@pytest.mark.parametrize("kind", ["archive", "root_symlink", "nested_symlink"])
def test_unsupported_archive_and_symlink_containers_reject(real_package, tmp_path, kind):
    if kind == "archive":
        import tarfile
        package = tmp_path / "package.tar.gz"
        with tarfile.open(package, "w:gz") as archive:
            for path in sorted(real_package["path"].iterdir()):
                archive.add(path, arcname=path.name, recursive=False)
    elif kind == "root_symlink":
        package = tmp_path / "linked_package"
        package.symlink_to(real_package["path"], target_is_directory=True)
    else:
        package = _clone(real_package, tmp_path)
        (package / "linked_extra_directory").symlink_to(tmp_path, target_is_directory=True)
    _reject(real_package, package, "unsupported_container_" + kind)


@pytest.mark.parametrize("pin", [None, "0" * 64])
def test_cli_requested_anchor_failure_returns_nonzero(real_package, capsys, pin):
    cli = importlib.import_module("demo.run_ephemeral_workspace_evidence_v01")
    arguments = ["replay", "--package-dir", str(real_package["path"]),
                 "--publication", str(real_package["publication_path"]), "--require-anchor"]
    if pin is not None:
        arguments += ["--expected-anchor", pin]
    with _runtime_guard("cli_failed_requested_anchor", real_package["observations"]):
        status = cli.main(arguments)
    assert status != 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "FAIL_CLOSED"
    assert output["errors"]
    real_package["observations"][-1]["expected_anchor"] = pin
    _save_result(real_package, "cli_failed_requested_anchor", output)


def test_cli_report_cannot_modify_checked_package(real_package, capsys):
    cli = importlib.import_module("demo.run_ephemeral_workspace_evidence_v01")
    target = real_package["path"] / "verification_report.json"
    with _runtime_guard("cli_report_inside_package", real_package["observations"]):
        status = cli.main(["replay", "--package-dir", str(real_package["path"]),
                           "--report", str(target)])
    assert status != 0 and not target.exists()
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "FAIL_CLOSED"
    _save_result(real_package, "cli_report_inside_package", output)



def _documents(real_package):
    adapter = real_package["adapter"]
    return {name: json.loads((real_package["path"] / name).read_bytes())[
            "payload"]["safe_document"] for name in adapter.REQUIRED_DOCUMENTS}


def test_coherent_substitution_reseals_but_cannot_keep_original_pin(real_package, tmp_path):
    documents = _documents(real_package)
    final = documents["final_safe_execution_report_v01.json"]["summary"]
    final["candidate_commit_status"] = "UNCOMMITTED_TEST_SUBSTITUTE_NOT_OWNER_HEAD"
    substituted = tmp_path / "substituted"
    with _runtime_guard("coherent_substitution_common_reseal", real_package["observations"]):
        changed = real_package["adapter"]._write_package(documents, substituted)
    _save_result(real_package, "coherent_substitution_common_reseal", changed)
    assert changed["status"] == "SELF_CONSISTENT_UNANCHORED"
    replacement_pin = changed["publication"]["anchor_publication_id"]
    assert replacement_pin != real_package["pin"]
    accepted = _verify(real_package, substituted, "substitute_matching_test_pin",
                       expected_anchor=replacement_pin, require_anchor=True)
    assert accepted["status"] == "ANCHORED_PASS"
    assert accepted["sealed_replay"]["replay_status"] == "PASS"
    reason = _reject(real_package, substituted, "substitute_original_pin",
                     expected_anchor=real_package["pin"], require_anchor=True)
    assert reason == "external_anchor_mismatch"
    real_package["observations"][-1].update(
        original_test_pin=real_package["pin"], substituted_test_pin=replacement_pin,
        coherent_substitute_self_consistent=True)


@pytest.mark.parametrize("field", ["source_record", "source_artifact"])
def test_changed_original_source_binding_cannot_keep_original_pin(real_package, tmp_path, field):
    documents = _documents(real_package)
    binding = documents["final_safe_execution_report_v01.json"]["source_binding"]
    if field == "source_record":
        row = next(item for item in binding["source_records"]
                   if item["path"] == "browser_run_01/native_final/semantic_safe.json")
        original = row["sha256"]
        row["sha256"] = "0" * 64 if original != "0" * 64 else "1" * 64
    else:
        row = binding["source_artifacts"][0]
        original = row["source_payload_sha256"]
        row["source_payload_sha256"] = "0" * 64 if original != "0" * 64 else "1" * 64
    with _runtime_guard("inconsistent_original_binding_" + field,
                        real_package["observations"]):
        with pytest.raises(ValueError, match="source_provenance_binding_mismatch") as caught:
            real_package["adapter"]._write_package(documents, tmp_path / "inconsistent_binding")
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        mutation={"scope": "final_document_only", "source_kind": field,
                  "original_digest": original, "changed_digest": "0" * 64 if original != "0" * 64 else "1" * 64})
    real_package["observations"].flush()
    assert not (tmp_path / "inconsistent_binding").exists()
    # Make the substitution coherent across every derivative before resealing.
    for document in documents.values():
        document["source_binding"]["source_records"] = copy.deepcopy(binding["source_records"])
        document["source_binding"]["source_artifacts"] = copy.deepcopy(binding["source_artifacts"])
    altered = tmp_path / "altered_source_binding"
    with _runtime_guard("changed_original_binding_reseal_" + field,
                        real_package["observations"]):
        changed = real_package["adapter"]._write_package(documents, altered)
    _save_result(real_package, "changed_original_binding_reseal_" + field, changed)
    assert changed["publication"]["anchor_publication_id"] != real_package["pin"]
    reason = _reject(real_package, altered, "changed_original_binding_original_pin_" + field,
                     expected_anchor=real_package["pin"], require_anchor=True)
    assert reason == "external_anchor_mismatch"
    real_package["observations"][-1]["substituted_publication_id"] = changed["publication"]["anchor_publication_id"]
    real_package["observations"].flush()


@pytest.mark.parametrize("filename,key", [
    ("sidecar_write_receipt_safe_v01.json", "sidecar_sha256"),
    ("runtime_execution_topology_safe_v01.json", "retained_result_sha256"),
    ("runtime_execution_topology_safe_v01.json", "consumed_binding_sha256"),
    ("workspace_lease_safe_v01.json", "old_packet_sha256"),
])
def test_valid_json_domain_claim_mismatch_cannot_be_resealed(real_package, tmp_path, filename, key):
    documents = _documents(real_package)
    previous = documents[filename]["summary"][key]
    documents[filename]["summary"][key] = "0" * 64 if previous != "0" * 64 else "1" * 64
    # Parsing remains valid; genuine domain and common construction must refuse.
    documents = json.loads(_json_bytes(documents))
    with _runtime_guard("semantic_claim_mismatch_" + key, real_package["observations"]):
        with pytest.raises(ValueError, match="cross_document_claim_mismatch") as caught:
            real_package["adapter"]._write_package(documents, tmp_path / "invalid_claim")
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        mutation={"document": filename, "field": key, "original": previous,
                  "changed": documents[filename]["summary"][key], "json_valid": True})
    real_package["observations"].flush()
    assert not (tmp_path / "invalid_claim").exists()


def test_manifest_covered_extra_file_still_rejected(real_package, tmp_path):
    from hedgehog.evidence import sealed_package_v01 as common
    documents = _documents(real_package)
    with _runtime_guard("covered_extra_common_construction", real_package["observations"]):
        files, context, _, _ = real_package["adapter"]._assemble(documents)
        extra = b"{\"scope\":\"TEST_ONLY_EVIDENCE\"}\n"
        record = common.build_safe_file_record_v01(
            logical_path="zz_unexpected.json", media_type="application/json", content_bytes=extra,
            evidence_class="EXECUTED_DETERMINISTIC_RUNTIME",
            source_record_ids=(context["domain_projection"].source_records[0].source_record_id,),
            terminal_newline_required=True, secret_scan_passed=True)
        records = tuple(sorted((*context["manifest"].safe_file_records, record),
                               key=lambda item: item.logical_path.encode("utf-8")))
        files[record.logical_path] = extra
        contents = tuple(files[item.logical_path] for item in records)
        changed = common.build_sealed_package_manifest_v01(
            domain_projection=context["domain_projection"], safe_file_records=records,
            safe_file_contents=contents, kernel_manifest_hash=context["manifest"].kernel_manifest_hash)
        assert changed.package_status == "SELF_CONSISTENT_UNANCHORED"
        assert not common.validate_sealed_package_manifest_v01(
            changed, domain_projection=context["domain_projection"], safe_file_contents=contents)
        manifest_plain = common.sealed_package_manifest_to_plain_dict_v01(
            changed, domain_projection=context["domain_projection"], safe_file_contents=contents)
    package = _clone(real_package, tmp_path)
    (package / "zz_unexpected.json").write_bytes(extra)
    (package / "sealed_package_manifest_v01.json").write_bytes(_json_bytes(manifest_plain))
    reason = _reject(real_package, package, "manifest_covered_extra")
    assert reason == "package_file_coverage_mismatch"


@pytest.mark.parametrize("attack", ["parent_ref", "payload_digest", "private_field", "escaped_text"])
def test_artifact_references_and_decoded_private_values_reject(real_package, tmp_path, attack):
    package = _clone(real_package, tmp_path)
    target = package / "final_safe_execution_report_v01.json"
    row = json.loads(target.read_bytes())
    if attack == "parent_ref":
        row["parent_refs"] = ["ews4:safe_projection:missing_parent"]
    elif attack == "payload_digest":
        row["artifact_id"] = "ews4:safe_projection:" + "0" * 64
    elif attack == "private_field":
        row["payload"]["safe_document"]["summary"]["nonce"] = "test-private-value"
    else:
        # The source remains ASCII; the tested JSON decoder must inspect escapes.
        row["payload"]["safe_document"]["summary"]["test_value"] = chr(0x0410)
    target.write_bytes(_json_bytes(row))
    _reject(real_package, package, "artifact_" + attack)


# The original EWS4 ID is supplied by the lead for the old bytes only.
REVIEWED_OLD_EWS4_PIN = "15fa80ecfc85c18ea5bec7dc03355a95a07c61734598fc89e02834d8103ac26d"
NATIVE_BSEP_SOURCE = "browser_run_01/native_common_return/D_baseline.json"
NATIVE_BSEP_SHA256 = "247912e13f057e147104d60a660f24f548f7f965a2329eefc5b6282d399c3ed1"


def test_reviewed_old_pin_rejects_corrected_package(real_package):
    assert real_package["pin"] != REVIEWED_OLD_EWS4_PIN
    reason = _reject(real_package, real_package["path"], "reviewed_old_pin_changed_content",
                     publication_path=real_package["publication_path"],
                     expected_anchor=REVIEWED_OLD_EWS4_PIN, require_anchor=True)
    assert reason == "external_anchor_mismatch"
    real_package["observations"][-1].update(
        supplied_pin_provenance="LEAD_REVIEWED_OLD_EWS4_ID_FROM_PROMPT",
        verification_purpose="NEGATIVE_TEST_ON_CORRECTED_BYTES",
        new_independent_pin="PENDING_REVIEW")
    real_package["observations"].flush()


def test_native_bsep_projection_binds_exact_dto_and_public_validator(real_package):
    document = _documents(real_package)["bsep_safe_projection_v01.json"]
    native = document["summary"]["native_bsep"]
    assert native["projection_kind"] == "NATIVE_DTO_SAFE_DERIVATIVE"
    assert native["canonical_native_dto_sha256"] == NATIVE_BSEP_SHA256
    assert native["source_file"] == NATIVE_BSEP_SOURCE
    assert native["source_file_sha256"] == "67eff98a00873b68690ce691d9a7b5145bbf7f8802c82e2251b852b79e597d32"
    assert native["packet_pointer"] == "/source_context/g2c_source_context/bsep_packet"
    assert native["binding_pointer"] == "/source_context/router_input/bsep_binding"
    assert native["packet_type"] == "BoundedSemanticEvidencePacket"
    assert native["schema_version"] == "bounded_semantic_evidence_packet_v0.1"
    assert native["offline_validation"]["packet_accepted"] is True
    assert native["offline_validation"]["packet_reasons"] == []
    assert native["authority_boundary_flags"]["authority_claimed"] is False
    assert native["authority_boundary_flags"]["action_permission_claimed"] is False
    assert "compiled_contract_summary" in document["summary"]
    with _runtime_guard("native_bsep_public_subset_validation", real_package["observations"]):
        real_package["adapter"]._validate_native_bsep_projection(native)
    real_package["observations"][-1].update(source_file=NATIVE_BSEP_SOURCE,
        canonical_native_dto_sha256=NATIVE_BSEP_SHA256,
        private_native_packet_published=False)
    real_package["observations"].flush()


@pytest.mark.parametrize("attack", ["missing_packet", "missing_binding", "packet_type",
    "schema", "source_role", "authority", "binding_digest", "binding_role"])
def test_native_bsep_source_and_binding_negatives(real_package, attack):
    # Private native input is read only; neither original nor altered DTO is emitted.
    data = (Path(os.environ["EWS4_INPUT_ROOT"]) / NATIVE_BSEP_SOURCE).read_bytes()
    assert _sha(data) == "67eff98a00873b68690ce691d9a7b5145bbf7f8802c82e2251b852b79e597d32"
    base = json.loads(data)
    context = base["source_context"]
    packet = context["g2c_source_context"]["bsep_packet"]
    binding = context["router_input"]["bsep_binding"]
    if attack == "missing_packet":
        del context["g2c_source_context"]["bsep_packet"]
    elif attack == "missing_binding":
        del context["router_input"]["bsep_binding"]
    elif attack == "packet_type":
        packet["packet_type"] = "UntrustedReplacementPacket"
    elif attack == "schema":
        packet["schema_version"] = "unsupported_test_schema"
    elif attack == "source_role":
        packet["source_role"] = "unexpected_role"
    elif attack == "authority":
        packet["authority_claimed"] = True
    elif attack == "binding_digest":
        binding["source_packet_sha256"] = "0" * 64
    else:
        binding["target_role"] = "unexpected_role"
    with _runtime_guard("native_bsep_source_" + attack, real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            real_package["adapter"]._native_bsep_projection(base)
    reason = str(caught.value)
    assert reason in {"native_bsep_missing_packet_or_binding", "native_bsep_dto_invalid",
                     "native_bsep_binding_mismatch", "native_bsep_source_digest_mismatch"}
    real_package["observations"][-1].update(rejection_reason=reason,
        mutation={"kind": attack, "source_file": NATIVE_BSEP_SOURCE,
                  "original_sha256": _sha(data), "private_dto_emitted": False})
    real_package["observations"].flush()


@pytest.mark.parametrize("attack", ["role", "authority", "source_pointer", "source_digest"])
def test_native_bsep_public_claim_changes_cannot_reseal(real_package, tmp_path, attack):
    documents = _documents(real_package)
    native = documents["bsep_safe_projection_v01.json"]["summary"]["native_bsep"]
    if attack == "role":
        native["target_role"] = "unexpected_role"
    elif attack == "authority":
        native["authority_boundary_flags"]["authority_claimed"] = True
    elif attack == "source_pointer":
        native["packet_pointer"] = "/source_context/unrelated_packet"
    else:
        native["canonical_native_dto_sha256"] = "0" * 64
    with _runtime_guard("native_bsep_projection_" + attack, real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            real_package["adapter"]._write_package(documents, tmp_path / "altered_bsep")
    assert str(caught.value) == "native_bsep_projection_mismatch"
    assert not (tmp_path / "altered_bsep").exists()
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        mutation={"kind": attack, "scope": "valid_json_safe_bsep_projection"})
    real_package["observations"].flush()


@pytest.mark.parametrize("attack,expected", [
    ("missing_path", "candidate_source_ledger_scope_invalid"),
    ("unexpected_path", "candidate_source_ledger_scope_invalid"),
    ("changed_frozen_source", "frozen_predecessor_source_changed"),
])
def test_exact_27_path_ledger_rejects_scope_or_frozen_source_changes(real_package, tmp_path, attack, expected):
    original_path = Path(os.environ["EWS4_SOURCE_LEDGER"])
    rows = json.loads(original_path.read_bytes())
    assert len(rows) == 27
    root = tmp_path / "altered_source_review"
    root.mkdir()
    for row in rows:
        target = root / row["source_object"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((original_path.parent / row["source_object"]).read_bytes())
    if attack == "missing_path":
        rows.pop()
    elif attack == "unexpected_path":
        row = next(item for item in rows if item["path"] == "tests/test_ephemeral_workspace_adversarial_v01.py")
        row["path"] = "tests/unlisted_boundary_test.py"
    else:
        row = next(item for item in rows if item["path"] == "hedgehog/domains/ephemeral_workspace/semantic_roles_v01.py")
        body = (root / row["source_object"]).read_bytes() + b"\n# Controlled negative source mutation.\n"
        row.update(bytes=len(body), sha256=_sha(body), source_object="source_objects/" + _sha(body))
        (root / row["source_object"]).write_bytes(body)
    path = root / "source_ledger.json"
    path.write_bytes(_json_bytes(rows))
    with _runtime_guard("ledger_" + attack, real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            real_package["adapter"]._source_ledger(path)
    assert str(caught.value) == expected
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        mutation={"kind": attack, "source_ledger_sha256": _sha(path.read_bytes()),
                  "actual_candidate_changed": False, "row_count": len(rows)})
    real_package["observations"].flush()



def _load_current_supplement(real_package, root, expected):
    documents = _documents(real_package)
    final = documents["final_safe_execution_report_v01.json"]
    return real_package["adapter"]._load_supplemental_proof(root, expected,
        source_ledger_rows=json.loads(Path(os.environ["EWS4_SOURCE_LEDGER"]).read_bytes()),
        principal_sources=real_package["report"]["source_records"],
        principal_facts=final["summary"]["facts"])


def test_supplemental_manifest_requires_explicit_matching_digest(real_package):
    with _runtime_guard("supplemental_wrong_caller_digest", real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            _load_current_supplement(real_package,
                Path(os.environ["EWS4R_SUPPLEMENTAL_PROOF_ROOT"]), "0" * 64)
    assert str(caught.value) == "supplemental_manifest_mismatch"
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        expected_manifest="0" * 64, pin_scope="CONTROLLED_SUPPLEMENTAL_INPUT_NEGATIVE")
    real_package["observations"].flush()


@pytest.mark.parametrize("attack", ["bound_file_bytes", "coverage_classification", "recorded_observation"])
def test_supplemental_coverage_and_execution_bindings_reject_changes(real_package, tmp_path, attack):
    root = tmp_path / "supplemental_negative"
    shutil.copytree(Path(os.environ["EWS4R_SUPPLEMENTAL_PROOF_ROOT"]), root)
    manifest_path = root / "MANIFEST.json"
    original_manifest = manifest_path.read_bytes()
    manifest = json.loads(original_manifest)
    plan_path = root / "coverage_plan.json"
    plan = json.loads(plan_path.read_bytes())
    row = next(item for item in plan["rows"] if item["requirement"] == "EW-A01")
    if attack == "bound_file_bytes":
        plan_path.write_bytes(plan_path.read_bytes() + b" ")
        expected = _sha(original_manifest)
    else:
        if attack == "coverage_classification":
            row["classification"] = "CARRIED_PRIOR_EVIDENCE"
            plan_path.write_bytes(_json_bytes(plan))
            changed = "coverage_plan.json"
        else:
            changed = row["proof_refs"]["observation"]
            observation_path = root / changed
            observation = json.loads(observation_path.read_bytes())
            observation["observed_sink_attempts"]["source_read_attempts"] = 1
            observation_path.write_bytes(_json_bytes(observation))
        entry = next(item for item in manifest if item["path"] == changed)
        data = (root / changed).read_bytes()
        entry.update(bytes=len(data), sha256=_sha(data))
        manifest_path.write_bytes(_json_bytes(manifest))
        expected = _sha(manifest_path.read_bytes())
    with _runtime_guard("supplemental_" + attack, real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            _load_current_supplement(real_package, root, expected)
    reason = str(caught.value)
    if attack == "bound_file_bytes":
        assert reason == "supplemental_file_digest_mismatch"
    elif attack == "coverage_classification":
        assert reason == "supplemental_coverage_scope_invalid"
    else:
        assert reason in {"supplemental_observation_mismatch", "supplemental_source_binding_mismatch",
            "supplemental_execution_record_binding_mismatch", "supplemental_receipt_binding_mismatch"}
    real_package["observations"][-1].update(rejection_reason=reason,
        mutation={"kind": attack, "expected_manifest_sha256": expected,
                  "original_manifest_sha256": _sha(original_manifest),
                  "principal_and_genuine_supplement_unchanged": True})
    real_package["observations"].flush()


@pytest.mark.parametrize("attack", ["failed_call_phase", "nonzero_source_access"])
def test_public_coverage_claims_cannot_be_resealed_by_updating_summary_hash(real_package, tmp_path, attack):
    documents = _documents(real_package)
    coverage = documents["adversarial_matrix_v01.json"]["summary"]
    row = next(item for item in coverage["coverage"] if item["requirement"] == "EW-A01")
    if attack == "failed_call_phase":
        row["call_phase"]["outcome"] = "failed"
    else:
        row["observed_proof"]["observed_sink_attempts"]["source_read_attempts"] = 1
    # Keep the summary digest coherent so this reaches the semantic proof guard.
    documents["final_safe_execution_report_v01.json"]["summary"]["supplemental_proof_binding"]["safe_coverage_sha256"] = real_package["adapter"]._digest(coverage)
    with _runtime_guard("public_coverage_" + attack, real_package["observations"]):
        with pytest.raises(ValueError) as caught:
            real_package["adapter"]._write_package(documents, tmp_path / "changed_coverage")
    assert str(caught.value) == "supplemental_projection_mismatch"
    assert not (tmp_path / "changed_coverage").exists()
    real_package["observations"][-1].update(rejection_reason=str(caught.value),
        mutation={"kind": attack, "requirement": "EW-A01", "summary_digest_recomputed": True,
                  "source_evidence_unchanged": True})
    real_package["observations"].flush()
