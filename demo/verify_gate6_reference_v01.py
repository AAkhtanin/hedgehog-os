"""Finite Gate6 mixed-basis evidence reader. Default mode imports no runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "docs/gate6_reference_v01"
ORIGINAL = "859c863fa40000dfcd6759685f3b0083f0e040b777df19e5393154fc9ac0f288"
REVIEWED = "73f5fe75dee04bb54c629c148bc48b98516765776649b100d108884e5cf7115b"
ADAPTER = "hedgehog/domains/testflix/outcome_feedback_adapter_v01.py"
TEST = "tests/test_gate6_g35_request_projection_v01.py"
COMPAT = "hedgehog/drs_g2b_compatibility_v01.py"
NEW_CODE = {"demo/run_gate6_retained_obligations_v01.py", "tests/test_gate6_retained_obligations_v01.py",
            "tests/test_gate6_drs_generated_id_screen_v01.py", "demo/verify_gate6_reference_v01.py",
            "tests/test_gate6_reference_package_v01.py"}
PROFILES = {"DIRECT", "G35", "LIVING_G36", "CONFORMANCE_G36", "G51", "G52", "G4", "G44_RECORDED", "G5_RECORDED", "FOOTBALL", "MODEL"}
ROWS = ({f"C{i:02}" for i in range(1, 7)} | {f"A{i:02}" for i in range(1, 11)} |
        {f"N1-{i:02}" for i in range(1, 21)} | {f"N4-{i:02}" for i in range(1, 16)} |
        {f"D{i:02}" for i in range(1, 16)} | {"BASE", "START", "IDENTITY", "MODEL", "FINAL", "O-ARCH", "CLOSURE"})
WORKERS = ("G35", "LIVING_G36", "CONFORMANCE_G36", "G51", "G52", "G4_original", "G4_successor",
           "G44_original", "G44_successor", "G5_original", "FOOTBALL", "MODEL", "RETAINED_OBLIGATIONS")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "duplicate_json_key:" + key)
            value[key] = item
        return value
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def relative(name):
    require(isinstance(name, str) and bool(name), "relative_path_required")
    p = PurePosixPath(name)
    require(not p.is_absolute() and str(p) == name and all(x not in ("", ".", "..") for x in name.split("/")), "unsafe_path:" + name)
    return p


def checked_file(root, name, pin, *, git_mode=None):
    path = Path(root) / relative(name)
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink:" + name)
    mode = path.stat().st_mode
    require(stat.S_ISREG(mode), "regular_file_required:" + name)
    data = path.read_bytes()
    require(len(data) == pin["bytes"] and sha(data) == pin["sha256"], "file_pin:" + name)
    if git_mode:
        require(git_mode in ("100644", "100755"), "git_mode")
        require((bool(mode & 0o111)) == (git_mode == "100755"), "executable_mode:" + name)
        require(not mode & 0o7000, "special_mode:" + name)
    return data


def unique_rows(rows, field, expected, reason):
    keys = [row[field] for row in rows]
    require(len(keys) == len(set(keys)) and set(keys) == expected, reason)


def validate_protocol(machine, matrix, original, reviewed):
    require(machine["protocol"] == "TWO_FRESH_NINE_RETAINED", "not_same_freeze_eleven")
    require(machine["historical_G6A4"] == "INCOMPLETE", "historical_failure_promoted")
    require(machine["final_package_review"] == machine["owner_source_admission"] == "PENDING", "unearned_admission")
    require(sha(canonical(original)) == ORIGINAL and sha(canonical(reviewed)) == REVIEWED, "executed_source_basis")
    require(set(reviewed) - set(original) == {TEST} and set(original) - set(reviewed) == set(), "closure_delta")
    require([k for k in original if original[k] != reviewed[k]] == [ADAPTER], "runtime_delta")
    unique_rows(machine["profiles"], "profile", PROFILES, "profile_inventory")
    for row in machine["profiles"]:
        fresh = row["profile"] in ("DIRECT", "G35")
        require(row["execution_basis"] == (REVIEWED if fresh else ORIGINAL), "profile_source_substitution:" + row["profile"])
        require(row["class"] == ("FRESH_G6A4R" if fresh else "RETAINED_G6A4_REVALIDATED"), "profile_class")
        require(row["primary"] and row["checks"], "primary_evidence_required")
    unique_rows(matrix["rows"], "id", ROWS, "matrix_inventory")
    for row in matrix["rows"]:
        require(row["obligation"] and row["binding"] and row["limitations"], "unbound_matrix_row:" + row["id"])
        require(row["disposition"] in ("SATISFIED_BOUNDED_REFERENCE", "APPROVED_DEFERMENT", "G6B_ONLY", "PENDING_SOURCE_ADMISSION", "REMAINING_TECHNICAL"), "matrix_disposition")
    for name in ("N1-18", "N1-19", "N4-12", "N4-13"):
        require(next(r for r in matrix["rows"] if r["id"] == name)["disposition"] == "APPROVED_DEFERMENT", "deferred_promoted")
    require(machine["finite_successor"]["historical_G6A5R"] == "INCOMPLETE" and
            machine["finite_successor"]["consumer"] == "RETAINED_OBLIGATIONS", "finite_successor_protocol")
    for name in ("N1-05", "N4-04", "N4-05", "N4-07"):
        row = next(r for r in matrix["rows"] if r["id"] == name)
        require(row["disposition"] == "SATISFIED_BOUNDED_REFERENCE" and
                any(b.get("consumer") == "RETAINED_OBLIGATIONS" for b in row["binding"]), "finite_row_binding")


def source_views(index, original, reviewed, current):
    old, successor = index["historical_source_view"], index["reviewed_source_view"]
    require(set(successor) == set(old) | {TEST} and TEST not in old, "historical_view_inventory")
    require({p for p in old if old[p] != successor[p]} == {ADAPTER}, "historical_view_delta")
    for view, closure in ((old, original), (successor, reviewed)):
        for rel, pin in closure.items():
            require(rel in view and all(view[rel][k] == pin[k] for k in ("bytes", "sha256")), "historical_view_pin:" + rel)
        require(view[COMPAT]["path"] != COMPAT and view[COMPAT] == old[COMPAT], "required_compatibility_preimage")
    require(set(current) == set(reviewed) | NEW_CODE, "current_closure_inventory")
    require({p for p in reviewed if current[p] != reviewed[p]} == {COMPAT}, "current_runtime_delta")
    require(current[COMPAT]["sha256"] != original[COMPAT]["sha256"], "current_compatibility_required")
    return old, successor


def inspect(root=ROOT, manifest_pin=None):
    root = Path(root).resolve()
    folder = root / PACKAGE
    body = (folder / "MANIFEST.json").read_bytes()
    require(manifest_pin is None or sha(body) == manifest_pin, "external_manifest_pin")
    manifest = read(folder / "MANIFEST.json")
    require(set(manifest) == {"schema", "files"} and manifest["schema"] == "gate6_package_manifest_v01", "manifest_shape")
    names = [r["path"] for r in manifest["files"]]
    require(len(names) == len(set(names)), "manifest_duplicate")
    for row in manifest["files"]:
        require(set(row) == {"path", "type", "git_mode", "bytes", "sha256"} and row["type"] == "regular", "manifest_row_shape")
        checked_file(root, row["path"], row, git_mode=row["git_mode"])
    actual = {str(p.relative_to(root)) for p in folder.rglob("*") if p.is_file() or p.is_symlink()}
    actual.remove(PACKAGE + "/MANIFEST.json")
    require({p for p in names if p.startswith(PACKAGE + "/")} == actual, "closed_package_coverage")
    require("demo/verify_gate6_reference_v01.py" in names and "tests/test_gate6_reference_package_v01.py" in names, "package_code_inventory")
    index = read(folder / "evidence_index.json")
    require(index["schema"] == "gate6_finite_resources_v01", "resource_schema")
    for key, row in index["resources"].items():
        relative(key)
        checked_file(root, row["path"], row)
    def resource(key):
        require(key in index["resources"], "missing_resource:" + key)
        return read(root / index["resources"][key]["path"])
    original = resource("r/original_source_closure.json")
    reviewed = resource("r/source_closure.json")
    machine = read(folder / "machine_manifest.json")
    matrix = read(folder / "acceptance_matrix.json")
    validate_protocol(machine, matrix, original, reviewed)
    current = read(folder / "current_source_closure.json")
    old_view, reviewed_view = source_views(index, original, reviewed, current)
    for view in (old_view, reviewed_view):
        for rel, pin in view.items():
            relative(rel)
            checked_file(root, pin["path"], pin, git_mode=pin["git_mode"])
    for rel, pin in current.items():
        checked_file(root, rel, pin)
    for rel, pin in resource("r/final_postimage_ledger.json").items():
        checked_file(root, rel, pin, git_mode="100755" if pin["mode"] & 0o111 else "100644")
    for rel, pin in index["historical_source_view"].items():
        relative(rel)
        checked_file(root, pin["path"], pin, git_mode=pin["git_mode"])
    for profile in machine["profiles"]:
        for key in profile["primary"] + profile["checks"]:
            require(key in index["resources"], "profile_resource:" + key)
    for row in matrix["rows"]:
        for binding in row["binding"]:
            if "resource" in binding:
                require(binding["resource"] in index["resources"], "matrix_resource:" + row["id"])
                if "expected" in binding or "pointer" in binding:
                    value = resource(binding["resource"])
                    for part in binding.get("pointer", []):
                        value = value[part]
                    require(value == binding["expected"], "matrix_witness:" + row["id"])
                if "case_ids" in binding:
                    phases = resource(binding["resource"])["phases"]
                    for node in binding["case_ids"]:
                        selected = [p for p in phases if p["nodeid"] == node]
                        require(len(selected) == 3 and {p["when"] for p in selected} == {"setup", "call", "teardown"}
                                and all(p["outcome"] == "passed" for p in selected), "matrix_case:" + node)
            if "path" in binding:
                require((root / relative(binding["path"])).is_file(), "matrix_source:" + row["id"])
    for profile in ("DIRECT", "G35"):
        receipt = resource("r/fresh/" + profile + "/receipts.json")[profile]
        require(receipt["status"] == "PASS", "fresh_receipt_status")
        require(sha(canonical(receipt["source_closure"])) == REVIEWED, "fresh_receipt_closure")
    return dict(status="PASS_FINITE_MIXED_BASIS_REFERENCE_PACKAGE", mode="DATA_ONLY",
        trust="EXTERNAL_MANIFEST_PIN_MATCHED" if manifest_pin else "SELF_CONSISTENCY_ONLY",
        profiles=11, fresh_profiles=2, retained_profiles=9, rows=73, original_closure=ORIGINAL,
        reviewed_closure=REVIEWED, files=len(names), resources=len(index["resources"]),
        current_closure=sha(canonical(current)), finite_rows=4,
        remaining_technical=[r["id"] for r in matrix["rows"] if r["disposition"] == "REMAINING_TECHNICAL"],
        admission="PENDING", gate6="NOT_CLOSED", runtime_imports=False)


def materialize(root, output, index):
    dest = output / "resources"
    for key, row in index["resources"].items():
        path = dest / relative(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(checked_file(root, row["path"], row))
        path.chmod(row["historical_mode"])
    original = output / "original_source"
    for rel, row in index["historical_source_view"].items():
        path = original / relative(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(checked_file(root, row["path"], row))
        path.chmod(0o755 if row["git_mode"] == "100755" else 0o644)
    reviewed = output / "reviewed_source"
    for rel, row in index["reviewed_source_view"].items():
        path = reviewed / relative(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(checked_file(root, row["path"], row))
        path.chmod(0o755 if row["git_mode"] == "100755" else 0o644)
    return dest, original, reviewed


def environment(root):
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TMPDIR") if k in os.environ}
    env.update(PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return env


def model_replay_result(value, prior):
    """Separate real replay value/code pins from run-specific observer receipts."""
    require(set(value) == set(prior) == {"result", "observation", "status"}, "model_replay_shape")
    require(value["status"] == prior["status"] == "PURE_REPLAY_COMPLETE" and value["result"] == prior["result"], "model_replay_parity")
    observed = value["observation"]
    require(observed["sentinel_live"] and observed["restored"] and observed["counts"] == {"sentinel": 1}, "model_replay_operations")
    def pins(record):
        return {key: {k: v for k, v in pin.items() if k != "file"} for key, pin in record["identities"].items()}
    require(pins(observed) == pins(prior["observation"]), "model_replay_code_pins")
    return dict(status=value["status"], result=value["result"], observed_calls=observed["counts"], code_pins=pins(observed))


def worker(name, source, resources, output):
    """Closed pure dispatch. These imports occur only in explicit supplied mode."""
    require(name in WORKERS, "unknown_pure_worker")
    sys.path.insert(0, str(source))
    from demo import run_gate6_reference_v01 as composer
    from tools import run_gate6_model_contrast_v01 as model
    counts = dict(network=0, subprocess=0)
    def audit(event, args):
        if event in ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname"):
            counts["network"] += 1
            raise RuntimeError("network_forbidden_in_pure_reader")
        if event in ("subprocess.Popen", "os.system", "os.posix_spawn"):
            counts["subprocess"] += 1
            require(name == "G5_original" and event == "subprocess.Popen", "undeclared_pure_child")
    sys.addaudithook(audit)
    a, r = resources / "a", resources / "r"
    def execute():
        if name == "RETAINED_OBLIGATIONS":
            from demo import run_gate6_retained_obligations_v01 as finite
            def consume():
                return {family:check(finite.decode(read(source/PACKAGE/"evidence/retained_obligations"/family/"witness.json")))
                        for family,check in finite.CHECKS.items()}
            observed = finite.observed(output, "pure", finite.pure_functions(), consume)
            finite.check_counts(observed["observation"], {})
            return observed["value"]
        if name == "G35":
            from hedgehog import outcome_feedback_report_v01 as reports
            d = r / "fresh/G35/G35/native"
            value, sources, baseline = read(d/"report.json"), read(d/"sources.json"), read(d/"independent_baseline.json")
            errors = reports.validate_supplied_report_v01(value, sources=sources, baseline=baseline)
            require(not errors, "G35:" + repr(errors))
            result = reports.replay_v01(report=value, sources=sources, baseline=baseline)
            require(composer.plain(result) == read(r/"fresh/G35/G35/supplied_replay.json"), "G35_replay_parity")
            return dict(errors=errors, replay=result)
        if name in ("LIVING_G36", "CONFORMANCE_G36"):
            value = read(a / f"campaign/{name}/{name}/full_return.json")
            if name == "LIVING_G36":
                from demo.run_living_gauntlet_v01 import validate_living_g36_v01
                errors = validate_living_g36_v01(value, registration_root=source)
            else:
                from hedgehog.gate4_reference_release_v01 import decode_conformance_v01
                from demo.run_kernel_conformance_v01 import validate_kernel_conformance_g36_v01
                errors = validate_kernel_conformance_g36_v01(dict(value, legacy=decode_conformance_v01(value["legacy"])))
            require(not errors, name + ":" + repr(errors))
            return dict(errors=errors)
        if name in ("G51", "G52"):
            folder = a / f"campaign/{name}/{name}"
            if name == "G51":
                from hedgehog.external_drs.gate5_supplied_v01 import verify_capture as verify
            else:
                from hedgehog.external_drs.gate5_lifecycle_supplied_v01 import verify
            result = verify(folder/"native", read(folder/"local_test_expected.json"), source)
            require(composer.plain(result) == read(folder/"supplied.json"), "supplied_parity:" + name)
            return result
        if name.startswith("G4_"):
            from hedgehog import gate4_reference_evidence_v01 as evidence
            folder = a / "campaign/G4/G4"
            prior = read(folder/"supplied_1.json")
            result = (evidence.verify_package_v01(package=folder/"package", trust=read(folder/"local_test_trust.json"))
                      if name.endswith("original") else evidence.validate_saved_story_v01(folder/"package/story"))
            require(result == (prior if name.endswith("original") else prior["result"]), "G4_parity")
            return result
        if name.startswith("G44_"):
            from hedgehog import gate4_reference_release_v01 as release, gate4_reference_evidence_v01 as evidence
            folder = resources / "repo/docs/showcase/gate4_reference_v01/evidence/g44"
            parents, package = folder/"parents", folder/"portable_publication_final"
            trust = read(folder/"TEST_SUPPLIED_PIN_FINAL.json")
            pin = "109c37f42ca220782971991c63f40037041d5c4548997fa1ab11262c578c81cd"
            prior = read(a/"campaign/G44_RECORDED/G44_RECORDED/supplied.json")
            if name.endswith("original"):
                result = release.validate_release_v01(parent_directory=parents, parent_pin=pin, package=package, trust=trust, root=source)
                require(result == prior, "G44_original_parity")
            else:
                require(ADAPTER not in read(parents/"MANIFEST.json")["source_impact"]["unchanged"], "G44_impact")
                result = dict(registration=release.validate_registration_v01(source),
                    parent=release.validate_parents_v01(directory=parents, expected_manifest_sha256=pin, root=source),
                    result=evidence.validate_saved_story_v01(package/"story"))
                require(result == dict(registration=prior["registration"], parent=prior["parent"], result=prior["g4"]["result"]), "G44_successor_parity")
            return result
        if name == "G5_original":
            from demo import verify_gate5_reference_v01 as verifier
            sys.argv = [str(source/"demo/verify_gate5_reference_v01.py"), "--output", str(output/"g5")]
            verifier.main()
            result = read(output/"g5/canonical_result.json")
            require(result == read(r/"retained/G5_original/native/canonical_result.json"), "G5_reconciled_parity")
            return result
        if name == "FOOTBALL":
            from tools import run_gate6_football_reference_v01 as bridge
            results = {}
            for case in bridge.CASES:
                values = []
                for ordinal in (1, 2):
                    value = bridge.supplied(resources/"football", case)
                    require(composer.plain(value) == read(r/f"retained/FOOTBALL/{case}_supplied_{ordinal}.json"), "football_parity:" + case)
                    values.append(value)
                results[case] = values
            require(not any(k.startswith("candidate_domain") for k in sys.modules), "candidate_import")
            return results
        if name == "MODEL":
            results = {}
            for label, folder in (("LIVE", a/"campaign/MODEL/MODEL"), ("CONTROLLED", a/"recorded/g6a3/evidence/model_controlled_final")):
                model.pure_replay(folder/"sealed.json", read(folder/"summary.json")["manifest_hash"], output/(label+".json"))
                value = read(output/(label+".json"))
                results[label] = model_replay_result(value, read(r/f"retained/MODEL/{label}_replay.json"))
            return results
        raise ValueError("closed_dispatch")

    functions = dict(composer.collection_functions(), **model.native_functions(),
                     G35=composer.module("demo.gate3_scenario_packs_v01").collect_pack_v01)
    try:
        if name in ("MODEL", "RETAINED_OBLIGATIONS"):
            result = execute()  # Existing consumer owns its monitoring scope.
        else:
            with composer.observe_calls(functions, output=output/"observation.json", phase="pure:"+name) as observed:
                result = execute()
            require(observed["sentinel_live"] and observed["restored"] and not any(v for k,v in observed["counts"].items() if k != "sentinel"), "collector_called")
        require(counts["network"] == 0 and counts["subprocess"] == (2 if name == "G5_original" else 0), "pure_operations")
        origins = {}
        for key, module in tuple(sys.modules.items()):
            file = getattr(module, "__file__", None)
            if not file or not key.startswith(("hedgehog.", "demo.", "tools.")) or not file.endswith(".py"):
                continue
            path = Path(file).resolve()
            if path.is_relative_to(source):
                rel = str(path.relative_to(source))
            else:
                allowed = resources/"football/AUTHOR_VISIBLE/source"
                require(name == "FOOTBALL" and path.is_relative_to(allowed), "undeclared_import:"+key)
                rel = str(path.relative_to(allowed))
                require(path.read_bytes() == (source/rel).read_bytes(), "nonidentical_historical_import:"+key)
            origins[key] = dict(relative_source=rel, sha256=sha(path.read_bytes()))
        save(output/"imports.json", origins)
        save(output/"result.json", composer.plain(result))
    finally:
        save(output/"audit.json", dict(counts=counts, scope="CURRENT_PROCESS; G5 two existing pure children retain their own receipts and observations"))


def supplied(root, output, manifest_pin=None):
    result = inspect(root, manifest_pin)
    index = read(root/PACKAGE/"evidence_index.json")
    resources, original, reviewed = materialize(root, output, index)
    results = {}
    for name in WORKERS:
        folder = output/name
        folder.mkdir()
        source = root if name == "RETAINED_OBLIGATIONS" else original if name.endswith("original") else reviewed
        argv = [sys.executable, "-B", str(root/"demo/verify_gate6_reference_v01.py"), "--worker", name,
                "--source-view", str(source), "--resources", str(resources), "--output", str(folder)]
        start = time.monotonic()
        with (folder/"stdout").open("wb") as stdout, (folder/"stderr").open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=source, env=environment(source), stdout=stdout, stderr=stderr)
            save(folder/"process.json", dict(pid=process.pid, argv=argv, cwd=str(source), started=time.time()))
            rc = process.wait()
        save(folder/"receipt.json", dict(rc=rc, reaped=True, seconds=time.monotonic()-start,
             streams={n:dict(bytes=(folder/n).stat().st_size, sha256=sha((folder/n).read_bytes())) for n in ("stdout","stderr")}))
        require(rc == 0, "pure_worker_refused:"+name+"; see raw stderr")
        results[name] = read(folder/"result.json")
        print(json.dumps(dict(phase=name, status="PASS", seconds=time.monotonic()-start)), flush=True)
    save(output/"canonical_result.json", dict(classification=result["status"], results=results,
        original_closure=ORIGINAL, reviewed_closure=REVIEWED, authority="EVIDENCE_NOT_RESTORED_AUTHORITY", admission="PENDING"))
    return dict(result, mode="EXISTING_PURE_CONSUMERS", pure_workers=len(WORKERS), historical_G5_pure_children=2)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("inspect", "supplied"), default="inspect")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--worker", choices=WORKERS, help=argparse.SUPPRESS)
    parser.add_argument("--source-view", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--resources", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    require(not output.is_relative_to(ROOT), "external_output_required")
    if args.worker:
        require(args.source_view and args.resources and output.is_dir(), "worker_explicit_inputs")
        worker(args.worker, args.source_view.resolve(), args.resources.resolve(), output)
        return 0
    output.mkdir(parents=True, exist_ok=False)
    result = supplied(ROOT, output, args.manifest_sha256) if args.mode == "supplied" else inspect(ROOT, args.manifest_sha256)
    save(output/"result.json", result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
