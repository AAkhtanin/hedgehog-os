"""Inert orchestration contracts and direct observer controls, not collector PASS."""
import ast
import copy
import json
import subprocess
import sys

import pytest

from demo import run_gate6_reference_v01 as reference
from tools import run_gate6_football_reference_v01 as football
from tests.test_gate6_reference_conformance_v01 import observe_entry_counts, observer_sentinel


def test_plan_retains_independent_owners_and_model():
    plan = reference.inspect_plan()
    assert len(plan["rows"]) == 11
    assert plan["declared_total_top_level"]["E5"] == 2
    assert plan["declared_total_top_level"]["D5"] == 2
    assert plan["declared_total_top_level"]["G36"] == 2
    assert all(row["supplied_collector_calls"] == 0 for row in plan["rows"])
    assert next(row for row in plan["rows"] if row["id"] == "MODEL")["state"] == "NOT_AUTHORIZED_NOT_RUN"
    assert len(plan["football_cases"]) == 16
    assert not plan["runtime_observed"]


def test_dispatch_recorder_preserves_ownership_not_runtime_acceptance():
    calls = []
    def recorder(name):
        calls.append(name)
        return object()
    result = reference.invoke_selected(["LIVING_G36", "CONFORMANCE_G36", "G35", "G4", "G51", "G52"], recorder)
    assert calls == list(result)
    assert result["LIVING_G36"] is not result["CONFORMANCE_G36"]
    assert len(calls) == 6


@pytest.mark.parametrize("names", [[], ["G4", "G4"], ["MODEL"], ["UNKNOWN"]])
def test_bad_execution_selection_refuses_without_dispatch(names):
    calls = []
    with pytest.raises(ValueError):
        reference.invoke_selected(names, calls.append)
    assert calls == []


def test_readiness_missing_failed_stale_and_subset():
    plan = reference.inspect_plan()
    assert reference.readiness(plan, {})["status"] == "INCOMPLETE"
    receipts = {row["id"]: dict(status="PASS", source=row["source"], source_closure=plan["source_closure"]) for row in plan["rows"]}
    receipts["FOOTBALL"]["cases"] = ["main", "revoked_source"]
    receipt = reference.readiness(plan, receipts)
    assert "FOOTBALL_INCOMPLETE_16" in receipt["reasons"]
    assert any(x.startswith("MODEL_ARTIFACT_REFUSED") for x in receipt["reasons"])
    assert any(x.startswith("G4_ARTIFACT_REFUSED") for x in receipt["reasons"])
    changed = copy.deepcopy(receipts)
    changed["G4"]["source"]["sha256"] = "0" * 64
    changed["G51"]["status"] = "FAIL"
    reasons = reference.readiness(plan, changed)["reasons"]
    assert "G4_STALE_SOURCE" in reasons and "G51_MISSING_FAILED_OR_NOT_RUN" in reasons
    changed = copy.deepcopy(receipts)
    changed["G4"]["source_closure"]["hedgehog/gate4_reference_runtime_v01.py"]["sha256"] = "0" * 64
    assert "G4_STALE_SOURCE" in reference.readiness(plan, changed)["reasons"]
    assert not receipt["gate6_closed"] and receipt["source_admission"] == "NOT_PERFORMED"


def test_observer_counts_and_cleans_exception():
    assert sys.getprofile() is None
    with pytest.raises(ValueError, match="^controlled_exception$"):
        with observe_entry_counts(dict(sentinel=observer_sentinel)) as counts:
            observer_sentinel()
            raise ValueError("controlled_exception")
    assert counts == dict(sentinel=1) and sys.getprofile() is None


def test_observer_refuses_existing_hook_without_losing_it():
    previous = sys.getprofile()
    def existing(frame, event, arg):
        return None
    try:
        sys.setprofile(existing)
        with pytest.raises(RuntimeError, match="^g6_observer_conflicting_profile$"):
            with observe_entry_counts(dict(sentinel=observer_sentinel)):
                pytest.fail("conflicting observer entered")
        assert sys.getprofile() is existing
    finally:
        sys.setprofile(previous)


def test_observer_python311_syntax_and_no_monitoring_dependency():
    tree = ast.parse((reference.ROOT / "tests/test_gate6_reference_conformance_v01.py").read_text(), feature_version=(3, 11))
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "observe_entry_counts")
    assert not any(isinstance(n, ast.Attribute) and n.attr == "monitoring" for n in ast.walk(helper))


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/../b", "a//b", "./a"])
def test_bridge_recovery_paths_refuse(name):
    with pytest.raises(ValueError, match="^unsafe_path$"):
        football.safe_path(name)


def test_bridge_explicit_endpoint_no_remote_fallback(tmp_path):
    with pytest.raises(ValueError, match="^explicit_local_docker_endpoint$"):
        football.docker_prefix(sys.executable, "tcp://example.invalid:2375", tmp_path)


def test_bridge_changed_prepared_source_refuses(tmp_path):
    (tmp_path / "input").write_text("before")
    football.save(tmp_path / "freeze.json", dict(files={"input": football.pin(tmp_path / "input")["sha256"]}))
    (tmp_path / "input").write_text("after")
    with pytest.raises(ValueError, match="^prepared_source_changed:input$"):
        football.check_prepared(tmp_path)


def complete_direct_record():
    return dict(collected=list(reference.DIRECT_NODE_IDS), exitstatus=0, deselected=[], collection_errors=[],
        phases=[dict(nodeid=n, when=w, outcome="passed", wasxfail=None) for n in reference.DIRECT_NODE_IDS for w in ("setup", "call", "teardown")])


@pytest.mark.parametrize("mutation", ["short", "substitute", "duplicate", "skip", "xfail", "missing-phase", "error", "deselect"])
def test_direct_exact_completeness_controls(mutation):
    record = complete_direct_record()
    assert reference.direct_result(record) == "PASS"
    if mutation == "short": record["collected"].pop()
    elif mutation == "substitute": record["collected"][-1] += "-substitute"
    elif mutation == "duplicate": record["collected"][-1] = record["collected"][0]
    elif mutation == "skip": record["phases"][1]["outcome"] = "skipped"
    elif mutation == "xfail": record["phases"][1]["wasxfail"] = "expected"
    elif mutation == "missing-phase": record["phases"].pop()
    elif mutation == "error": record["collection_errors"] = ["failed_collection"]
    else: record["deselected"] = [record["collected"][0]]
    assert reference.direct_result(record) != "PASS"


def test_direct_selection_parameter_id_and_safe_subset():
    nodes = list(reference.DIRECT_NODE_IDS)
    selected = next(n for n in nodes if "[" in n)
    assert reference.validate_direct_selection([selected]) == [selected]
    for bad in ([selected, selected], [selected + "foreign"], [selected.split("[")[0]],
                ["tests/test_repository_release_spine_v01.py::test_any"], ["--pyargs"], ["tests/../test_any.py::test_a"]):
        with pytest.raises(ValueError): reference.validate_direct_selection(bad)


@pytest.mark.parametrize("mutation", ["missing", "changed", "profile", "input", "escape"])
def test_readiness_rereads_artifacts_and_input(tmp_path, mutation):
    plan = reference.inspect_plan()
    folder = tmp_path / "output"; folder.mkdir()
    source = tmp_path / "scenario"; source.mkdir(); (source / "fixture.json").write_text('{"value":1}')
    options = {"scenario_dir": str(source)}
    reference.save(folder / "PROFILE.json", dict(profile="G51", base=reference.BASE))
    reference.save(folder / "result.json", {"status":"PASS"})
    record = dict(profile="G51", base=reference.BASE, source_closure=plan["source_closure"],
        input_closure=reference.input_closure(options), explicit_inputs=options,
        output_directory=str(folder), output_files=reference.saved_files(folder))
    reference.verify_artifacts(record, "G51", plan)
    if mutation == "missing": (folder / "result.json").unlink()
    elif mutation == "changed": (folder / "result.json").write_text("changed")
    elif mutation == "profile": record["profile"] = "G52"
    elif mutation == "input": (source / "fixture.json").write_text('{"value":2}')
    else: record["output_files"]["../escape"] = record["output_files"]["result.json"]
    with pytest.raises((ValueError, OSError)):
        reference.verify_artifacts(record, "G51", plan)


@pytest.mark.parametrize("backend", ["available", "python311_fallback"])
def test_collection_nested_owners_and_supplied_zero(backend, monkeypatch):
    if backend == "python311_fallback":
        monkeypatch.setattr(sys, "monitoring", None, raising=False)
    def d5(): return 7
    def e5(): return d5()
    def g36_inner(): return 8
    def g36(): return g36_inner()
    functions = {"D5": d5, "E5": e5, "G36": g36, "G36:inner": g36_inner}
    with reference.observe_calls(functions) as actual:
        assert e5() == 7 and d5() == 7 and g36() == 8
    assert actual["direct_owners"] == dict(sentinel=1, E5=1, D5=1, G36=1)
    assert actual["nested"] == dict(D5=1, G36=1)
    assert actual["counts"]["D5"] == 2 and actual["sentinel_live"] and actual["restored"]
    with reference.observe_calls(functions) as supplied:
        assert 7+8 == 15
    assert supplied["counts"] == dict(sentinel=1)
    assert supplied["children"] == "UNOBSERVED_NOT_ZERO"
    def fails(): raise RuntimeError("observed-target")
    with reference.observe_calls({"G36": fails, "G36:inner": g36_inner}) as exceptional:
        with pytest.raises(RuntimeError, match="observed-target"): fails()
        assert g36_inner() == 8
    assert exceptional["direct_owners"]["G36"] == 2 and not exceptional["nested"]


def test_readiness_rereads_external_football_artifacts(tmp_path):
    plan = reference.inspect_plan()
    folder = tmp_path / "output"; folder.mkdir()
    work = tmp_path / "work"; work.mkdir()
    external = work / "SUPERVISOR_EVIDENCE"; external.mkdir()
    capture = external / "actual.json"; capture.write_text('{"actual":1}')
    reference.save(folder / "PROFILE.json", dict(profile="FOOTBALL", base=reference.BASE))
    options = dict(work=str(work))
    record = dict(profile="FOOTBALL", base=reference.BASE, source_closure=plan["source_closure"],
                  input_closure=reference.input_closure(options), explicit_inputs=options,
                  output_directory=str(folder), output_files=reference.saved_files(folder),
                  external_output_files=reference.saved_files(external))
    reference.verify_artifacts(record, "FOOTBALL", plan)
    capture.write_text('{"actual":2}')
    with pytest.raises(ValueError, match="football_external_changed"):
        reference.verify_artifacts(record, "FOOTBALL", plan)
    capture.unlink()
    with pytest.raises((OSError, ValueError)):
        reference.verify_artifacts(record, "FOOTBALL", plan)


def test_collection_observer_exception_and_conflict():
    with pytest.raises(RuntimeError, match="sentinel-error"):
        with reference.observe_calls({}) as observed:
            raise RuntimeError("sentinel-error")
    assert observed["restored"] and sys.getprofile() is None
    def old(frame, event, arg): return None
    try:
        sys.setprofile(old)
        with pytest.raises(ValueError, match="observer_conflict"):
            with reference.observe_calls({}): pytest.fail("entered")
        assert sys.getprofile() is old
    finally:
        sys.setprofile(None)
    if getattr(sys, "monitoring", None) is not None:
        sys.monitoring.use_tool_id(4, "foreign-test-tool")
        try:
            with pytest.raises(ValueError, match="observer_monitoring_conflict"):
                with reference.observe_calls({}): pytest.fail("entered")
            assert sys.monitoring.get_tool(4) == "foreign-test-tool"
        finally:
            sys.monitoring.free_tool_id(4)


@pytest.mark.parametrize("failure", ["none", "ambiguous-create", "wait", "kill", "remove", "foreign"])
def test_football_lifecycle_cleanup_command_doubles(tmp_path, failure, record_property):
    name = "radiolaria-g6a3-controlled-test"
    receipt = dict(container_name=name, container_removed=False, cli_reaped=False,
                   create_attempted=True, error="create_timeout" if failure == "ambiguous-create" else None)
    commands = []
    def cli(args):
        commands.append(args)
        if args[0] == "inspect":
            return json.dumps([dict(Id="controlled-container-id", Name="/"+name,
                Config=dict(Image=football.IMAGE, Labels={"radiolaria.g6a3.task": name if failure != "foreign" else "unrelated"}),
                State=dict(Running=True))]).encode()
        if args[0] == failure:
            raise subprocess.TimeoutExpired(args, 30)
        if args[0] == "rm" and failure == "remove":
            raise subprocess.CalledProcessError(1, args)
        return b""
    football.finalize_case(receipt, tmp_path, dict(stdout=b"output", stderr=b"error"), None, cli)
    recorded = json.loads((tmp_path / "receipt.json").read_bytes())
    assert (tmp_path / "stdout.txt").read_bytes() == b"output"
    assert recorded["cli_reaped"]
    if failure == "foreign":
        assert commands == [["inspect", name]] and not recorded["container_removed"]
    else:
        assert [c[0] for c in commands] == ["inspect", "kill", "wait", "rm"]
    assert (recorded["terminal_status"] == "COMPLETE") == (failure == "none")
    assert (recorded["error"] == "create_timeout") == (failure == "ambiguous-create")
    record_property("LIFECYCLE_COMMAND_DOUBLES_NOT_NATIVE", json.dumps(dict(commands=commands, receipt=recorded)))


def test_football_cli_wait_failure_still_reaps_and_flushes(tmp_path):
    class Process:
        stdout = None; stderr = None
        def __init__(self): self.waits = 0; self.killed = False
        def poll(self): return None
        def terminate(self): pass
        def kill(self): self.killed = True
        def wait(self, timeout):
            self.waits += 1
            if self.waits == 1: raise subprocess.TimeoutExpired("controlled", timeout)
            return -9
    proc = Process(); name = "controlled-owned"
    receipt = dict(container_name=name, container_removed=False, cli_reaped=False, error="primary_failure")
    def cli(args):
        if args[0] == "inspect":
            return json.dumps([dict(Id="id", Name="/"+name, Config=dict(Image=football.IMAGE, Labels={"radiolaria.g6a3.task":name}), State=dict(Running=False))]).encode()
        return b""
    football.finalize_case(receipt, tmp_path, dict(stdout=b"partial", stderr=b""), proc, cli)
    assert proc.killed and receipt["cli_reaped"] and receipt["container_removed"]
    assert receipt["cleanup_errors"][0]["step"] == "cli_wait"
    assert receipt["terminal_status"] == "INCOMPLETE" and receipt["error"] == "primary_failure"
