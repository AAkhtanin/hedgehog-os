"""Portable exact accepted-program bridge. No authoring or source admission.

Recovered code has a finite pinned allowlist. Only the reviewed worker/observer,
outer flags function and pure per-case examiners are executable dependencies.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import selectors
import shutil
import subprocess
import sys
import tarfile
import time
import uuid

BASE = "b6d11f5fcb619a10e877bbaaf6770881be315f16"
IMAGE = "sha256:f07e68671249ccaffda9529b14593c191ff9664a8b43b27f6b16570623f63a97"
PINS = {
    "material.tar.gz": "bdf308e48cc3ce1b233b3b506c76c7444b706db95549ad91501c3b01e00cf518",
    "member_index.json": "b3a313c5a2b6555c611e5efeeb9d10ffabe2d2e9af499f08f273ff34aa1c17c3",
    "proof_input_freeze.json": "af4bf61cdee29e37fbb237f392cedfc37b44346a3be9ce4bb452d9f8624143b9",
}
RECIPE_PINS = {"Dockerfile": "75b97091648e2b15ef0230536d4b25d0719403b43e190d40d55041da44977561",
               "requirements.lock": "053fe39d61c89d4bb9306454aa470633b167dee560bba5d80530c02802beff2f"}
CASES = ("main", "low_budget", "missing_BOOK", "missing_history", "release_denied",
         "revoked_source", "foreign_audience", "revision_conflict", "same_key_changed",
         "permuted_main", "variation_feedback", "second_team", "long_overlap", "occupancy",
         "continuation", "variation_final_reserved")
RUNNER = ("action_runner_g54d.py", "observer_g54d.py", "process_filter.py", "image.lock.json", "evaluate_g54d.py")
ORACLE = ("examiner.py", "examiner_g54c_v01.py", "examiner_g54d_core_v01.py",
          "examiner_g54d_v01.py", "boundary_g54d_v01.py", "action_profile_g54c2_v01.py",
          "selection_and_release_g54d_v01.py")
PURE = ("review_finds.py", "review_flow.py", "check_refusal_binding_d1.py")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "regular_file_required:" + str(path))
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def safe_path(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(x not in ("", ".", "..") for x in name.split("/")), "unsafe_path")
    return p


def source_inventory(root):
    base = Path(root) / "docs/gate5_reference_evidence_v01"
    for name, digest in PINS.items():
        require(pin(base / name)["sha256"] == digest, "installed_evidence_pin:" + name)
    rows = read(base / "member_index.json")["members"]["g54d1"]
    wanted = {}
    for name in rows:
        if name.startswith("AUTHOR_VISIBLE/source/") or name.startswith("AUTHOR_VISIBLE/example/"):
            wanted[name] = "Exact approved closed source/import dependency; compared to installed equivalent"
        if name.startswith("RUNTIME_INPUTS/attempt_04/") and name.endswith("/input.json"):
            case = name.split("/")[2]
            if case in {x + "_repr" for x in CASES}:
                wanted[name] = "Exact accepted case input; not executed by discovery"
    for name in [*("DEPLOYMENT_G54D/" + x for x in RUNNER),
                 *("EXAMINER_PRIVATE/" + x for x in ORACLE), *PURE,
                 "AUTHOR_TRIAL/attempt_04/source_review.json", "AUTHOR_VISIBLE/DEPENDENCIES.json",
                 "AUTHOR_VISIBLE/EXECUTION_CONTRACT.md", "AUTHOR_VISIBLE/MANIFEST.json"]:
        require(name in rows, "recovery_member_missing:" + name)
        wanted[name] = "Pinned reviewed runner, examiner, review or execution contract"
    return base, rows, wanted


def prepare(root, work, recipe):
    root, work, recipe = Path(root).resolve(), Path(work).resolve(), Path(recipe).resolve()
    require(work != root and root not in work.parents, "external_work_required")
    require(not work.exists(), "fresh_work_required")
    base, rows, wanted = source_inventory(root)
    for name, digest in RECIPE_PINS.items():
        require(pin(recipe / name)["sha256"] == digest, "recipe_pin:" + name)
    work.mkdir(parents=True)
    ledger = []
    with tarfile.open(base / "material.tar.gz") as tf:
        entries = tf.getmembers()
        blobs = {m.name.split("/")[-1]: m for m in entries if m.isfile()}
        require(len(blobs) == len(entries), "blob_inventory_regular_unique")
        for name, reason in sorted(wanted.items()):
            safe_path(name)
            row = rows[name]
            storage = row["storage"]
            if "repository" in storage:
                data = (root / safe_path(storage["repository"])).read_bytes()
            else:
                data = tf.extractfile(blobs[storage["blob"]]).read()
            require(len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], "member_pin:" + name)
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            current = None
            if name.startswith("AUTHOR_VISIBLE/source/"):
                rel = name.removeprefix("AUTHOR_VISIBLE/source/")
                current = pin(root / rel)
                require(current == pin(target), "accepted_runtime_differs:" + rel)
            ledger.append(dict(path=name, **pin(target), recovery=dict(archive="g54d1", member=name, storage=storage), reason=reason, installed_equivalent=current))
    candidate = root / "hedgehog/domains/football_pitch_booking/pack_v01"
    review = read(work / "AUTHOR_TRIAL/attempt_04/source_review.json")
    require(review["status"] == "APPROVED_FOR_DECLARED_CONFINED_EXECUTION", "exact_candidate_review_required")
    actual = {str(p.relative_to(candidate)): pin(p)["sha256"] for p in candidate.rglob("*") if p.is_file()}
    require(not any(p.is_symlink() for p in candidate.rglob("*")) and actual == review["files"], "accepted_candidate_identity")
    shutil.copytree(candidate, work / "candidate")
    for name in RECIPE_PINS:
        (work / "recipe").mkdir(exist_ok=True)
        shutil.copyfile(recipe / name, work / "recipe" / name)
    save(work / "dependency_closure.json", dict(base=BASE, inputs=PINS, files=ledger,
        candidate=actual, recipe=RECIPE_PINS, historical_scripts_not_executed=["supplied_check_d1.py"],
        scope="Exact accepted code and pure per-case consumers; whole-16 supplied aggregate remains pending"))
    save(work / "freeze.json", dict(files={str(p.relative_to(work)): pin(p)["sha256"] for p in work.rglob("*") if p.is_file()}))
    (work / "SUPERVISOR_EVIDENCE").mkdir()
    return dict(status="PREPARED_NOT_EXECUTED", work=str(work), recovered=len(ledger), author_calls=0)


def check_prepared(work):
    work = Path(work).resolve()
    freeze = read(work / "freeze.json")
    for name, digest in freeze["files"].items():
        require(pin(work / safe_path(name))["sha256"] == digest, "prepared_source_changed:" + name)
    require(read(work / "DEPLOYMENT_G54D/image.lock.json")["image_id"] == IMAGE, "image_lock")
    return freeze


def command_environment():
    # HOME is inherited unchanged; no credentials or provider configuration forwarded.
    value = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TMPDIR") if k in os.environ}
    value.update(PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return value


def docker_prefix(executable, endpoint, config):
    require(Path(executable).is_absolute() and Path(executable).is_file(), "explicit_docker_executable")
    require(endpoint.startswith("unix:///"), "explicit_local_docker_endpoint")
    config = Path(config).resolve()
    require(config.is_dir(), "explicit_docker_config")
    return [str(executable), "--config", str(config), "--host", endpoint]


def check_configuration(value):
    hc, cfg = value["HostConfig"], value["Config"]
    require(hc["NetworkMode"] == "none" and hc["ReadonlyRootfs"] and not hc["Privileged"], "network_readonly")
    require(hc["IpcMode"] == "private" and not hc["PidMode"] and not hc["PortBindings"], "ipc_ports")
    require(hc["CapDrop"] == ["ALL"] and hc["PidsLimit"] == 16 and cfg["User"] == "65532:65532", "user_caps_pids")
    require(any(x.split(":")[0] == "no-new-privileges" for x in hc["SecurityOpt"]), "no_new_privileges")
    require(hc["Memory"] == hc["MemorySwap"] == 512 * 1024**2 and hc["NanoCpus"] == 10**9, "resource_bounds")
    require(all(not m["RW"] for m in value["Mounts"]) and {m["Destination"] for m in value["Mounts"]} == {"/approved", "/runner", "/inputs", "/candidate"}, "readonly_mounts")
    require(cfg["Image"] == IMAGE and cfg["Entrypoint"] == ["python"], "exact_worker_image")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finalize_case(receipt, folder, streams, proc, cli):
    """Independent bounded cleanup steps, including ambiguous create outcomes."""
    receipt.setdefault("cleanup_errors", [])
    def attempt(label, fn):
        try:
            return fn()
        except BaseException as error:
            receipt["cleanup_errors"].append(dict(step=label, type=type(error).__name__, detail=str(error)[:1000]))
            return None
    name = receipt["container_name"]
    cfg = attempt("inspect_exact_name", lambda: json.loads(cli(["inspect", name]))[0])
    owned = (isinstance(cfg, dict) and cfg.get("Name") == "/" + name and
             cfg.get("Config", {}).get("Labels", {}).get("radiolaria.g6a3.task") == name and
             cfg.get("Config", {}).get("Image") == IMAGE and bool(cfg.get("Id")))
    receipt["cleanup_identity_confirmed"] = owned
    if owned:
        identifier = cfg["Id"]
        receipt["container_id"] = identifier
        if cfg.get("State", {}).get("Running"):
            attempt("container_kill", lambda: cli(["kill", identifier]))
        attempt("container_wait", lambda: cli(["wait", identifier]))
        removed = attempt("container_remove", lambda: cli(["rm", "-f", identifier]))
        receipt["container_removed"] = removed is not None
    else:
        receipt["container_state"] = "UNKNOWN_UNCONFIRMED_NOT_REMOVED"
    if proc is not None:
        if proc.poll() is None:
            attempt("cli_terminate", proc.terminate)
        rc = attempt("cli_wait", lambda: proc.wait(timeout=15))
        if rc is None:
            attempt("cli_kill", proc.kill)
            rc = attempt("cli_reap", lambda: proc.wait(timeout=15))
        receipt["cli_reaped"] = rc is not None
        receipt["rc"] = rc
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                attempt("stream_close", stream.close)
    else:
        receipt["cli_reaped"] = True
    for label, body in streams.items():
        attempt("flush_" + label, lambda label=label, body=body: (folder / (label + ".txt")).write_bytes(body))
    receipt["cleanup_complete"] = bool(receipt["container_removed"] and receipt["cli_reaped"] and not receipt["cleanup_errors"])
    receipt["terminal_status"] = "COMPLETE" if receipt["cleanup_complete"] and not receipt.get("error") else "INCOMPLETE"
    receipt["end"] = time.time()
    # The final write is attempted even when every preceding cleanup command failed.
    save(folder / "receipt.json", receipt)


def execute_case(work, case, *, docker, endpoint, config):
    require(case in CASES, "unknown_case")
    work = Path(work).resolve()
    freeze = check_prepared(work)
    prefix = docker_prefix(docker, endpoint, config)
    env = command_environment()
    def cli(args):
        return subprocess.check_output(prefix + args, env=env, timeout=30)
    image = json.loads(cli(["image", "inspect", IMAGE]))[0]
    require(image["Id"] == IMAGE and image["Architecture"] == "arm64" and image["Os"] == "linux", "exact_existing_image_required")
    # The unchanged flags function is parameterized only by its path locator.
    outer = load_module("g6_pinned_outer", work / "DEPLOYMENT_G54D/evaluate_g54d.py")
    outer.WORK = work
    folder = work / "SUPERVISOR_EVIDENCE" / case
    folder.mkdir(exist_ok=False)
    inputs = work / "RUNTIME_INPUTS/attempt_04" / (case + "_repr")
    candidate = work / "candidate"
    name = "radiolaria-g6a3-" + uuid.uuid4().hex
    args = outer.flags(IMAGE, "candidate", name, inputs, candidate)
    require(args[0] == "create", "pinned_create_command")
    args[1:1] = ["--label", "radiolaria.g6a3.task=" + name]
    receipt = dict(classification="ACCEPTED_PROGRAM_REEXECUTION", case=case, author_calls=0,
        source_pins=freeze["files"], freeze_path="freeze.json", inputs={label + "/" + str(p.relative_to(base)): pin(p)["sha256"]
            for label, base in (("inputs", inputs), ("candidate", candidate)) for p in base.rglob("*") if p.is_file()},
        started=time.time(), container_name=name, create_attempted=False, argv=prefix + args, environment=env, rc=None, cli_reaped=False, container_removed=False,
        wall_limit_seconds=90, limit_basis="Exact accepted outer/worker 90s and per-child CPU30/35, unchanged")
    save(folder / "image.json", image)
    save(folder / "receipt.json", receipt)
    proc = None
    began = time.monotonic()
    streams = {"stdout": bytearray(), "stderr": bytearray()}
    try:
        receipt["create_attempted"] = True
        save(folder / "receipt.json", receipt)
        cli(args)
        cfg = json.loads(cli(["inspect", name]))[0]
        save(folder / "configuration.json", cfg)
        check_configuration(cfg)  # before any candidate import
        proc = subprocess.Popen(prefix + ["start", "-a", name], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        receipt["cli_pid"] = proc.pid
        select = selectors.DefaultSelector()
        for stream, label in ((proc.stdout, "stdout"), (proc.stderr, "stderr")):
            select.register(stream, selectors.EVENT_READ, label)
        try:
            last = 0
            while select.get_map():
                elapsed = time.monotonic() - began
                if elapsed - last >= 5:
                    with (folder / "heartbeat.jsonl").open("a") as f:
                        f.write(json.dumps(dict(elapsed=elapsed, pid=proc.pid, container=name)) + "\n")
                    last = elapsed
                require(elapsed < 90, "WALL_LIMIT")
                for key, _ in select.select(1):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        select.unregister(key.fileobj)
                    else:
                        streams[key.data].extend(chunk)
                        require(len(streams[key.data]) <= (16 if key.data == "stdout" else 2) * 1024**2, "STREAM_LIMIT")
            receipt["rc"] = proc.wait(timeout=15)
            receipt["cli_reaped"] = True
        finally:
            select.close()
        save(folder / "final_state.json", json.loads(cli(["inspect", name]))[0]["State"])
        require(receipt["rc"] == 0, "worker_exit_nonzero")
        payload = json.loads(streams["stdout"])
        parent = payload["parent_receipt"]
        save(folder / "trusted_parent_receipt.json", parent)
        require(not parent["limit_error"] and all(x["exit_code"] == 0 and x["reaped"] for x in parent["waits"]), "worker_incomplete")
        blob = base64.b64decode(payload["evidence_targz_base64"], validate=True)
        require(len(blob) <= 12 * 1024**2, "capture_bound")
        (folder / "worker_evidence.tar.gz").write_bytes(blob)
        with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
            members = tf.getmembers()
            require(len({m.name for m in members}) == len(members) and sum(m.size for m in members) <= 64 * 1024**2, "capture_inventory")
            for m in members:
                require(m.isfile(), "capture_regular_only")
                p = folder / "worker" / safe_path(m.name)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(tf.extractfile(m).read())
    except BaseException as exc:
        receipt["error"] = type(exc).__name__ + ":" + str(exc)
        raise
    finally:
        receipt["seconds"] = time.monotonic() - began
        finalize_case(receipt, folder, streams, proc, cli)
    require(receipt["cleanup_complete"], "cleanup_incomplete")
    return dict(status="NATIVE_COMPLETE_SUPPLIED_PENDING", folder=str(folder), seconds=receipt["seconds"])


def supplied(work, case):
    """Exact per-case oracle; deliberately not the historical full16/live wrapper."""
    work = Path(work).resolve()
    check_prepared(work)
    require(case in CASES and not any(x.startswith("candidate_domain") for x in sys.modules), "pure_consumer_scope")
    sys.path.insert(0, str(work))
    from review_flow import examine
    from check_refusal_binding_d1 import verify
    from hedgehog.kernel import root_decision_v01 as roots, effect_firewall_v01 as firewall
    from hedgehog import work_execution_host_v01 as host
    def sentinel():
        return None
    functions = {roots.decide_root_v01: "root", host.dispatch_current_action_v01: "dispatch",
                 host.execute_admitted_pure_work_v01: "work", firewall.execute_bound_effect_v01: "effect", sentinel: "sentinel"}
    codes = {f.__code__: name for f, name in functions.items()}
    counts = dict.fromkeys(codes.values(), 0)
    previous = sys.getprofile()
    require(previous is None, "observer_conflict")
    def observed(frame, event, arg):
        if event == "call" and frame.f_code in codes:
            counts[codes[frame.f_code]] += 1
    try:
        sys.setprofile(observed)
        sentinel()
        folder = work / "SUPERVISOR_EVIDENCE" / case
        result = examine(folder, case)
        refusal = verify(folder) if case == "revoked_source" else None
    finally:
        sys.setprofile(previous)
    require(counts["sentinel"] == 1 and not any(v for k, v in counts.items() if k != "sentinel"), "supplied_execution")
    require(not any(x.startswith("candidate_domain") for x in sys.modules), "candidate_imported")
    return dict(status="PASS_PER_CASE_PURE", result=result, refusal=refusal, observed_calls=counts,
                aggregate_16="NOT_COMPLETED", authority="CAPTURE_IS_EVIDENCE_NOT_RESTORED_HOST")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "prepare", "preflight", "execute", "supplied"), nargs="?", default="inspect")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--work", type=Path)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--docker")
    parser.add_argument("--endpoint")
    parser.add_argument("--docker-config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "inspect":
        _, rows, wanted = source_inventory(args.root)
        result = dict(status="DATA_ONLY", cases=CASES, dependencies={p: dict(reason=v, sha256=rows[p]["sha256"]) for p, v in wanted.items()}, recipe=RECIPE_PINS, image=IMAGE, author_calls=0)
    elif args.mode == "prepare":
        require(args.work is not None and args.recipe is not None, "work_and_recipe_required")
        result = prepare(args.root, args.work, args.recipe)
    elif args.mode == "preflight":
        require(args.work is not None, "work_required")
        result = dict(status="SOURCE_INPUT_PREFLIGHT_ONLY", freeze=check_prepared(args.work), container_started=False)
    elif args.mode == "execute":
        require(all((args.work, args.case, args.docker, args.endpoint, args.docker_config)), "explicit_execution_inputs_required")
        result = execute_case(args.work, args.case, docker=args.docker, endpoint=args.endpoint, config=args.docker_config)
    else:
        require(args.work is not None and args.case is not None, "work_case_required")
        result = supplied(args.work, args.case)
    if args.output:
        save(args.output, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
