"""Bounded Git/source proofs; no runtime collectors or owner writes."""

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "reviewed_transition_under_test", ROOT / "tools/reviewed_repository_transition_v01.py"
)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


@pytest.mark.parametrize("body,reason", [
    (b'{"x":1,"x":2}', "JSON_DUPLICATE_KEY:x"),
    (b'{"x":NaN}', "JSON_NONFINITE:NaN"),
    (b'{', "JSON_MALFORMED"),
])
def test_review_strict_json_refuses_v01(body, reason):
    with pytest.raises(REVIEW.Refusal, match=reason):
        REVIEW.strict_json(body)


@pytest.mark.parametrize("value", ["../a", "/a", "a//b", "a/./b", "a/.git/config", "a\\b"])
def test_review_unsafe_path_refuses_v01(value):
    assert not REVIEW._relative(value)


def test_review_context_not_inferred_from_candidate_v01(monkeypatch, tmp_path):
    monkeypatch.delenv(REVIEW.CONTEXT_ENV, raising=False)
    root = tmp_path / "no_review_context"
    subprocess.run(
        ("git", "clone", "--shared", "--no-checkout", "--quiet", str(ROOT), str(root)),
        check=True,
    )
    _git(root, "config", "remote.origin.url", "https://github.com/AAkhtanin/hedgehog-os")
    _git(root, "read-tree", "--reset", "-u", REVIEW.ACCEPTED["commit"])
    _git(root, "update-ref", "refs/heads/main", REVIEW.ACCEPTED["commit"])
    _git(root, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(root, "update-ref", "refs/remotes/origin/main", REVIEW.ACCEPTED["commit"])
    assert REVIEW.resolve_context(root) is None
    assert REVIEW.validate_transition(root)["errors"] == ["REVIEW_CONTEXT_REQUIRED"]


@pytest.mark.parametrize("mode", [0o400, 0o600, 0o644])
def test_review_private_repository_modes_match_git_v01(tmp_path, mode):
    root = (tmp_path / "mode_repository").resolve()
    subprocess.run(("git", "init", "--quiet", str(root)), check=True)
    file = root / "sample.txt"
    body = b"Unchanged repository evidence\n"
    file.write_bytes(body)
    file.chmod(mode)
    _git(root, "add", "--", "sample.txt")
    git_mode, git_oid, stage = _git(root, "ls-files", "--stage").split()[:3]
    found, oid = REVIEW._current_file(root, "sample.txt")
    assert found == {"type": "regular", "mode": "100644", "bytes": len(body),
                     "sha256": hashlib.sha256(body).hexdigest()}
    assert (git_mode, git_oid, stage) == (b"100644", oid.encode(), b"0")
    assert file.stat().st_mode & 0o7777 == mode


def test_review_repository_mode_boundaries_v01(tmp_path):
    root = tmp_path.resolve()
    file = root / "sample.txt"
    file.write_bytes(b"Reviewed bytes\n")
    file.chmod(0o644)
    normal, normal_oid = REVIEW._current_file(root, file.name)
    file.chmod(0o755)
    executable, _ = REVIEW._current_file(root, file.name)
    assert executable["mode"] == "100755"
    assert executable != normal
    file.chmod(0o644)
    file.write_bytes(b"Changed bytes\n")
    changed, changed_oid = REVIEW._current_file(root, file.name)
    assert changed["sha256"] != normal["sha256"] and changed_oid != normal_oid
    for mode in (0o666, 0o4644):
        file.chmod(mode)
        with pytest.raises(REVIEW.Refusal, match="CURRENT_FILE:sample.txt:MODE"):
            REVIEW._current_file(root, file.name)
    file.chmod(0o400)
    with pytest.raises(REVIEW.Refusal, match="EXTERNAL:MODE"):
        REVIEW._read_regular(file, "EXTERNAL")
    file.chmod(0o600)
    assert REVIEW._read_regular(file, "EXTERNAL") == b"Changed bytes\n"
    link = root / "link.txt"
    link.symlink_to(file)
    with pytest.raises(REVIEW.Refusal, match="CURRENT_FILE:link.txt:SYMLINK"):
        REVIEW._current_file(root, link.name)


def _record(name, **values):
    document = dict(event=name, monotonic=time.monotonic(), **values)
    print(json.dumps(document, sort_keys=True), flush=True)
    destination = os.environ.get("R1_PROOF_DIRECTORY")
    if destination:
        folder = Path(destination)
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "proof.jsonl").open("a") as output:
            output.write(json.dumps(document, sort_keys=True) + "\n")


def _git(root, *args):
    return subprocess.check_output(("git", "--no-optional-locks", "-C", str(root), *args))


def _write_json(file, value):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _file_identity(file):
    body = file.read_bytes()
    return {"type": "regular", "mode": "100755" if file.stat().st_mode & 0o111 else "100644",
            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}


def _context(root, directory, kind, paths, previous=None):
    base = {"commit": _git(root, "rev-parse", "HEAD").decode().strip(),
            "tree": _git(root, "rev-parse", "HEAD^{tree}").decode().strip()}
    rows = []
    tracked = set(_git(root, "ls-tree", "-r", "--name-only", "HEAD").decode().splitlines())
    for name in sorted(paths):
        pre = None
        if name in tracked:
            body = _git(root, "show", "HEAD:" + name)
            mode = _git(root, "ls-tree", "HEAD", "--", name).split()[0].decode()
            pre = {"type": "regular", "mode": mode, "bytes": len(body),
                   "sha256": hashlib.sha256(body).hexdigest()}
        rows.append({"path": name, "action": "M" if pre else "A", "pre": pre,
                     "post": _file_identity(root / name)})
    namespaces = sorted({"/".join(p.split("/")[:3]) for p in paths if p.startswith("docs/showcase/")})
    policy = REVIEW.policy_identity(root)
    shared = dict(schema=REVIEW.VERSION, repository=REVIEW.REPOSITORY, policy_id=policy,
                  kind=kind, accepted_basis=REVIEW.ACCEPTED, base=base, previous=previous)
    manifest = dict(shared, governed_namespaces=namespaces,
                    commit_message="Disposable " + kind + " source fixture", ledger=rows)
    manifest_file = directory / "manifest.json"
    _write_json(manifest_file, manifest)
    context = dict(shared, manifest={"path": str(manifest_file),
                   "sha256": hashlib.sha256(manifest_file.read_bytes()).hexdigest()},
                   state="PREPARED", finalized=None, purpose="DISPOSABLE_TEST_ONLY")
    context_file = directory / "context.json"
    _write_json(context_file, context)
    return context_file


def _check(root, context):
    result = REVIEW.validate_transition(root, context)
    _record("EVALUATE", context=str(context), **result)
    return result


def _public(root, context, phase):
    env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1")
    env.pop(REVIEW.CONTEXT_ENV, None)
    if context:
        env[REVIEW.CONTEXT_ENV] = str(context)
    commands = [
        (sys.executable, "-B", str(root / "tools/check_active_architecture_authority_v01.py"), "--root", str(root)),
        (sys.executable, "-B", "-c", "import runpy; m=runpy.run_path(" +
         repr(str(root / "tests/test_repository_release_spine_v01.py")) +
         "); print('BINDER=' + m['G2E4_V0310_ACTIVE_BYTES_BINDING']); "
         "m['test_g37_current_registration_pins_actual_release_files_v01']()"),
    ]
    for index, argv in enumerate(commands):
        started = time.monotonic()
        process = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True)
        _record("PUBLIC_GUARD" if index == 0 else "ACTUAL_BINDER", argv=argv,
                cwd=str(root), rc=process.returncode, elapsed=time.monotonic()-started,
                stdout=process.stdout, stderr=process.stderr, phase=phase)
        assert process.returncode == 0, process.stdout + process.stderr
        if index == 0:
            assert "G37_PHASE=" + phase in process.stdout
            assert "GATE3_STATUS=CLOSED_PASS" not in process.stdout
        else:
            assert "BINDER=EXACT_G37_WITH_HISTORICAL_TESTFLIX_E_PAIR" in process.stdout


@pytest.fixture(scope="module")
def reviewed_git_fixture(tmp_path_factory):
    outer = tmp_path_factory.mktemp("r1_source_proof").resolve()
    root = outer / "repository"
    # A local object-backed disposable repository, never the owner index.
    subprocess.run(("git", "clone", "--shared", "--no-checkout", "--quiet", str(ROOT), str(root)), check=True)
    _git(root, "config", "remote.origin.url", "https://github.com/AAkhtanin/hedgehog-os")
    _git(root, "read-tree", "--reset", "-u", REVIEW.ACCEPTED["commit"])
    _git(root, "update-ref", "refs/heads/main", REVIEW.ACCEPTED["commit"])
    _git(root, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(root, "update-ref", "refs/remotes/origin/main", REVIEW.ACCEPTED["commit"])
    old_guard = runpy.run_path(str(root / "tools/check_active_architecture_authority_v01.py"))
    guard = runpy.run_path(str(ROOT / "tools/check_active_architecture_authority_v01.py"))
    for current in (old_guard, guard):
        errors = []
        assert current["_validate_g37_frozen_release_admission_v01"](root, errors) == "G37_FROZEN_RELEASE_COMMITTED"
        assert errors == []
    protected = root / "hedgehog/kernel/root_decision_v01.py"
    body = protected.read_bytes()
    try:
        protected.write_bytes(body + b"\n# Disposable historical refusal\n")
        for current in (old_guard, guard):
            errors = []
            current["_validate_g37_frozen_release_admission_v01"](root, errors)
            assert "g37.frozen_source:hedgehog/kernel/root_decision_v01.py" in errors
    finally:
        protected.write_bytes(body)
    _record("HISTORICAL_REAL_GIT", positive="PASS", protected_refusal="PASS",
            source_commit=REVIEW.ACCEPTED["commit"])
    paths = set(REVIEW.BOOTSTRAP_PATHS)
    paths.update(file.relative_to(ROOT).as_posix() for file in (ROOT / REVIEW.SEALED_CAPSULE).rglob("*") if file.is_file())
    for name in paths:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    context = _context(root, outer / "bootstrap", "BOOTSTRAP", paths)
    _record("FIXTURE_READY", root=str(root), context=str(context), controls=sorted(REVIEW.BOOTSTRAP_PATHS))
    return root, outer, context


def test_review_bootstrap_public_guard_and_binder_v01(reviewed_git_fixture):
    root, _, context = reviewed_git_fixture
    result = _check(root, context)
    assert result["errors"] == []
    assert result["phase"] == "REVIEWED_BOOTSTRAP_PREPARED_UNSTAGED"
    _public(root, context, result["phase"])


@pytest.mark.parametrize("case,reason", [
    ("payload", "POSTIMAGE_IDENTITY:"),
    ("protected", "PROTECTED_SOURCE:hedgehog/kernel/root_decision_v01.py"),
    ("work", "PROTECTED_IDENTITY:hedgehog/kernel/work_composition_v01.py"),
    ("registration", "PROTECTED_IDENTITY:release/completion_manifest.json"),
    ("metadata", "METADATA_COHERENCE:"),
    ("extra", "CURRENT_TRACKED_UNTRACKED_INVENTORY"),
    ("ignored", "GOVERNED_NAMESPACE_EXTRA_OR_MISSING:"),
    ("mode", "CURRENT_FILE:README.md:MODE"),
    ("symlink", "CURRENT_FILE:"),
    ("partial_index", "EXACT_PROPOSAL_STATUS"),
    ("mixed_index", "STATUS_UNSUPPORTED_OR_MIXED"),
    ("flags", "INDEX_HIDDEN_FLAGS"),
    ("lock", "GIT_OPERATION:index.lock"),
    ("closure_null", "CLOSURE_RECORD_SHAPE"),
    ("closure_missing", "CLOSURE_RECORD:UNREADABLE"),
])
def test_review_current_state_refusals_v01(reviewed_git_fixture, case, reason):
    root, _, context = reviewed_git_fixture
    names = {
        "payload": "docs/repository_transition_admission_v01.md",
        "protected": "hedgehog/kernel/root_decision_v01.py",
        "work": "hedgehog/kernel/work_composition_v01.py",
        "registration": "release/completion_manifest.json",
        "metadata": "release/current_status_overlay_v01.json",
        "mode": "README.md", "symlink": "README.md",
        "closure_null": REVIEW.SEALED_CAPSULE + "/CLOSURE_ACCEPTANCE.json",
        "closure_missing": REVIEW.SEALED_CAPSULE + "/CLOSURE_ACCEPTANCE.json",
    }
    # Payload uses a non-policy navigation file, so failure reaches postimage checks.
    names["payload"] = "README.md"
    target = root / names[case] if case in names else None
    original = target.read_bytes() if target else None
    mode = target.stat().st_mode & 0o777 if target else None
    extra = None
    exclude = root / ".git/info/exclude"
    exclude_body = exclude.read_bytes()
    try:
        if case in ("payload", "protected", "work", "registration"):
            target.write_bytes(original + b"\n")
        elif case == "metadata":
            data = json.loads(original)
            data.pop("gate3_g37_current_registration_v01")
            _write_json(target, data)
        elif case in ("extra", "ignored"):
            extra = root / (REVIEW.SEALED_CAPSULE + "/unreported.txt" if case == "ignored" else "unexpected.txt")
            extra.write_text("Unreviewed fixture data\n")
            if case == "ignored":
                exclude.write_bytes(exclude_body + b"\nunreported.txt\n")
        elif case == "mode":
            target.chmod(0o666)
        elif case == "symlink":
            target.unlink()
            target.symlink_to(root / "AGENTS.md")
        elif case in ("partial_index", "mixed_index"):
            _git(root, "add", "--", "README.md")
            if case == "mixed_index":
                (root / "README.md").write_bytes((root / "README.md").read_bytes() + b"\n")
        elif case == "flags":
            _git(root, "update-index", "--assume-unchanged", "README.md")
        elif case == "lock":
            extra = root / ".git/index.lock"
            extra.write_text("Disposable operation lock\n")
        elif case == "closure_null":
            target.write_text("null\n")
        elif case == "closure_missing":
            target.unlink()
        result = _check(root, context)
        assert any(error.startswith(reason) for error in result["errors"]), result
    finally:
        if extra:
            extra.unlink()
        exclude.write_bytes(exclude_body)
        if target:
            if target.is_symlink():
                target.unlink()
            target.write_bytes(original)
            target.chmod(mode)
        if case == "mixed_index":
            (root / "README.md").write_bytes((ROOT / "README.md").read_bytes())
        if case in ("partial_index", "mixed_index"):
            _git(root, "read-tree", REVIEW.ACCEPTED["commit"])
        if case == "flags":
            _git(root, "update-index", "--no-assume-unchanged", "README.md")


@pytest.mark.parametrize("case,reason", [
    ("missing", "REVIEW_CONTEXT_REQUIRED"), ("wrong_pin", "MANIFEST_PIN"),
    ("policy", "CONTEXT_MANIFEST_MISMATCH:policy_id"),
    ("kind", "CONTEXT_MANIFEST_MISMATCH:kind"),
    ("malformed", "JSON_MALFORMED"), ("duplicate", "JSON_DUPLICATE_KEY:schema"),
    ("unknown", "MANIFEST_SHAPE"), ("unsafe", "LEDGER_UNSAFE_PATH"),
    ("duplicate_path", "LEDGER_DUPLICATE_PATH"), ("type", "FILE_IDENTITY_VALUE"),
    ("action", "LEDGER_UNSUPPORTED_ACTION"), ("mode", "FILE_IDENTITY_VALUE"),
    ("base", "REVIEWED_BASE_TREE"), ("finalized", "FINALIZED_TIP_MISMATCH"),
    ("conflict", "REVIEW_CONTEXT_CONFLICT"), ("context_symlink", "REVIEW_CONTEXT_FILE:SYMLINK"),
])
def test_review_context_and_manifest_refusals_v01(reviewed_git_fixture, tmp_path, case, reason):
    root, _, genuine = reviewed_git_fixture
    document = json.loads(genuine.read_bytes())
    original_manifest = Path(document["manifest"]["path"]).read_bytes()
    manifest = json.loads(original_manifest)
    context = tmp_path.resolve() / "context.json"
    manifest_file = tmp_path.resolve() / "manifest.json"
    _write_json(manifest_file, manifest)
    document["manifest"]["path"] = str(manifest_file)
    if case == "missing":
        context = None
    elif case == "wrong_pin":
        document["manifest"]["sha256"] = "0" * 64
    elif case == "policy":
        document["policy_id"] = "0" * 64
    elif case == "kind":
        document["kind"] = "ENGINEERING"
    elif case == "malformed":
        manifest_file.write_bytes(b"{")
    elif case == "duplicate":
        manifest_file.write_bytes(b'{"schema":1,' + original_manifest.lstrip()[1:])
    elif case == "unknown":
        manifest["unknown"] = True
    elif case in ("unsafe", "duplicate_path", "type", "action", "mode"):
        if case == "unsafe": manifest["ledger"][0]["path"] = "../outside"
        if case == "duplicate_path": manifest["ledger"].append(manifest["ledger"][0])
        if case == "type": manifest["ledger"][0]["post"]["type"] = "symlink"
        if case == "action": manifest["ledger"][0]["action"] = "D"
        if case == "mode": manifest["ledger"][0]["post"]["mode"] = "120000"
    elif case == "base":
        document["base"]["tree"] = "0" * 40
        manifest["base"] = document["base"]
    elif case == "finalized":
        document["state"] = "FINALIZED"
        document["finalized"] = document["base"]
    elif case == "conflict":
        document["purpose"] = "INDEPENDENT_REVIEW"
    if case in ("unknown", "unsafe", "duplicate_path", "type", "action", "mode", "base"):
        _write_json(manifest_file, manifest)
    if case != "wrong_pin":
        document["manifest"]["sha256"] = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
    if context:
        _write_json(context, document)
    local = root / ".git" / REVIEW.CONTEXT_LOCAL
    try:
        if case == "conflict":
            _write_json(local, json.loads(genuine.read_bytes()))
        if case == "context_symlink":
            context.unlink()
            context.symlink_to(genuine)
        result = _check(root, context)
        assert reason in result["errors"], result
    finally:
        if local.exists(): local.unlink()


def _commit_fixture(root, context):
    document = json.loads(context.read_bytes())
    manifest = json.loads(Path(document["manifest"]["path"]).read_bytes())
    tree = _git(root, "write-tree").decode().strip()
    env = dict(os.environ, GIT_AUTHOR_NAME="R1 disposable fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="R1 disposable fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    commit = subprocess.check_output(("git", "commit-tree", tree, "-p", document["base"]["commit"],
                                      "-m", manifest["commit_message"]), cwd=root, env=env).decode().strip()
    _git(root, "update-ref", "refs/heads/main", commit)
    return {"commit": commit, "tree": tree}


def _finalize_fixture(root, context, tip):
    old = context.read_bytes()
    prior = context.with_suffix(".prepared.json")
    prior.write_bytes(old)
    document = json.loads(old)
    document.update(state="FINALIZED", finalized=tip)
    temporary = context.with_suffix(".tmp")
    _write_json(temporary, document)
    os.replace(temporary, context)
    assert prior.read_bytes() == old
    _git(root, "update-ref", "refs/remotes/origin/main", tip["commit"])
    return dict(tip, policy_id=document["policy_id"], manifest_sha256=document["manifest"]["sha256"])


def test_review_sequential_publications_and_engineering_v01(reviewed_git_fixture):
    root, outer, context = reviewed_git_fixture
    unchanged_policy = {name: (root / name).read_bytes() for name in REVIEW.POLICY_PATHS}
    for label in ("BOOTSTRAP", "A", "B", "ENGINEERING"):
        if label != "BOOTSTRAP":
            if label == "ENGINEERING":
                name = "tests/r1_inert_future_source_fixture.py"
                (root / name).write_text('"""Unexecuted future engineering fixture."""\nVALUE = 1\n')
                paths = {name}
                kind = "ENGINEERING"
            else:
                name = "docs/showcase/r1_fixture_" + label.lower() + "_v01/README.md"
                (root / name).parent.mkdir(parents=True)
                (root / name).write_text("# Disposable publication " + label + "\n")
                readme = root / "README.md"
                readme.write_bytes(readme.read_bytes() + ("[Publication " + label + "](" + name + ")\n").encode())
                paths = {name, "README.md"}
                kind = "DOCUMENTATION"
            context = _context(root, outer / label, kind, paths, previous)
            assert "REVIEW_CONTEXT_REQUIRED" in _check(root, None)["errors"]
            if label == "ENGINEERING":
                wrong = json.loads(context.read_bytes())
                wrong_manifest_file = outer / label / "documentation_manifest.json"
                wrong_manifest = json.loads(Path(wrong["manifest"]["path"]).read_bytes())
                wrong_manifest["kind"] = wrong["kind"] = "DOCUMENTATION"
                _write_json(wrong_manifest_file, wrong_manifest)
                wrong["manifest"] = {"path": str(wrong_manifest_file), "sha256": hashlib.sha256(wrong_manifest_file.read_bytes()).hexdigest()}
                wrong_context = outer / label / "documentation_context.json"
                _write_json(wrong_context, wrong)
                assert "DOCUMENTATION_CAPSULE_REQUIRED" in _check(root, wrong_context)["errors"]
                guard = root / REVIEW.POLICY_PATHS[0]
                body = guard.read_bytes()
                try:
                    guard.write_bytes(body + b"\n")
                    assert "POLICY_IDENTITY" in _check(root, context)["errors"]
                finally: guard.write_bytes(body)
        data = json.loads(context.read_bytes())
        manifest = json.loads(Path(data["manifest"]["path"]).read_bytes())
        kind = data["kind"]
        for state in ("PREPARED_UNSTAGED", "PREPARED_STAGED", "PREPARED_COMMITTED"):
            if state == "PREPARED_STAGED":
                _git(root, "add", "--", *(row["path"] for row in manifest["ledger"]))
            if state == "PREPARED_COMMITTED":
                tip = _commit_fixture(root, context)
            result = _check(root, context)
            expected = "REVIEWED_" + kind + "_" + state
            assert result["errors"] == [] and result["phase"] == expected, result
            _public(root, context, expected)
        # Same frozen PREPARED input remains valid after commit, before finalization.
        assert _check(root, context)["phase"] == "REVIEWED_" + kind + "_PREPARED_COMMITTED"
        previous = _finalize_fixture(root, context, tip)
        assert _check(root, context)["phase"] == "REVIEWED_" + kind + "_FINALIZED"
        assert {name: (root / name).read_bytes() for name in REVIEW.POLICY_PATHS} == unchanged_policy
        _record("FINALIZED_FIXTURE", label=label, tip=tip, unchanged_enforcement=True,
                remote_publication="NOT_CHECKED", context=str(context))
def _g6b_test_payload():
    row = REVIEW.identity(b"Final documentation\n", "100644")
    return [dict(path="README.md", action="M", pre=REVIEW.identity(b"Old\n", "100644"), post=row),
            dict(path=REVIEW.G6B_NAMESPACE + "/README.md", action="A", pre=None, post=row)]


def test_g6b_payload_closed_shape_v01():
    rows = _g6b_test_payload()
    assert set(REVIEW._g6b_payload_shape_v01(rows)) == {r["path"] for r in rows}


@pytest.mark.parametrize("mutation", ["namespace", "duplicate", "casefold", "mode", "preimage", "missing", "unknown"])
def test_g6b_payload_refuses_v01(mutation):
    rows = _g6b_test_payload()
    if mutation == "namespace": rows[1]["path"] = "docs/showcase/other_v01/README.md"
    elif mutation == "duplicate": rows.append(dict(rows[1]))
    elif mutation == "casefold": rows.append(dict(rows[1], path=rows[1]["path"].upper()))
    elif mutation == "mode": rows[1]["post"] = dict(rows[1]["post"], mode="100755")
    elif mutation == "preimage": rows[1]["pre"] = rows[0]["pre"]
    elif mutation == "missing": rows.pop(0)
    elif mutation == "unknown": rows[0]["trusted"] = True
    with pytest.raises(REVIEW.Refusal):
        REVIEW._g6b_payload_shape_v01(rows)


def test_g6b_exact_exception_requires_installed_tip_and_full_binding_v01():
    import copy
    tip = {"commit": "1" * 40, "tree": "2" * 40}
    bridge = dict(schema=REVIEW.G6B_BRIDGE_VERSION, verified_maintenance_tip=tip,
                  new_policy_id="3" * 64, manifest_sha256="4" * 64,
                  publication_ledger=_g6b_test_payload())
    manifest = dict(kind="DOCUMENTATION", base=tip,
                    previous=dict(tip, policy_id="3" * 64, manifest_sha256="4" * 64),
                    governed_namespaces=[REVIEW.G6B_NAMESPACE], ledger=bridge["publication_ledger"])
    assert REVIEW._g6b_exact_publication_v01(manifest, bridge)
    assert not REVIEW._g6b_exact_publication_v01(manifest, None)
    for key, changed in (("kind", "ENGINEERING"), ("base", dict(tip, commit="5" * 40)),
                         ("previous", dict(manifest["previous"], manifest_sha256="6" * 64)),
                         ("governed_namespaces", ["docs/showcase/other_v01"]), ("ledger", [])):
        value = copy.deepcopy(manifest)
        value[key] = changed
        assert not REVIEW._g6b_exact_publication_v01(value, bridge)
    assert not REVIEW._g6b_exact_publication_v01(manifest, dict(bridge, verified_maintenance_tip=None))


def test_entry_payload_is_exact_not_general_v02():
    for payload in (None, [], _g6b_test_payload(), _g6b_test_payload() * 5):
        with pytest.raises(REVIEW.Refusal, match="ENTRY_EXACT_PUBLICATION_PAYLOAD"):
            REVIEW._entry_payload_v02(payload)


def test_entry_exception_requires_same_installed_tip_and_complete_payload_v02():
    import copy
    tip = dict(commit="a" * 40, tree="b" * 40)
    bridge = dict(schema=REVIEW.ENTRY_BRIDGE_VERSION, verified_maintenance_tip=tip,
                  new_policy_id="c" * 64, manifest_sha256="d" * 64,
                  publication_ledger=[{"exact": "payload already checked at bridge boundary"}])
    manifest = dict(kind="DOCUMENTATION", base=tip,
                    previous=dict(tip, policy_id=bridge["new_policy_id"], manifest_sha256=bridge["manifest_sha256"]),
                    governed_namespaces=[REVIEW.ENTRY_NAMESPACE], ledger=bridge["publication_ledger"],
                    commit_message=REVIEW.ENTRY_PUBLICATION_MESSAGE)
    assert REVIEW._entry_exact_publication_v02(manifest, bridge)
    assert not REVIEW._entry_exact_publication_v02(manifest, None)
    for key, bad in (("kind", "ENGINEERING"), ("base", REVIEW.ENTRY_BASE),
                     ("previous", {}), ("governed_namespaces", [REVIEW.G6B_NAMESPACE]),
                     ("ledger", []), ("commit_message", "Another publication")):
        value = copy.deepcopy(manifest)
        value[key] = bad
        assert not REVIEW._entry_exact_publication_v02(value, bridge)
    assert not REVIEW._entry_exact_publication_v02(manifest, dict(bridge, verified_maintenance_tip=None))
    assert not REVIEW._entry_exact_publication_v02(manifest, dict(bridge, schema=REVIEW.G6B_BRIDGE_VERSION))
    assert not REVIEW._g6b_exact_publication_v01(manifest, bridge)


def test_entry_wrong_historical_basis_refuses_before_git_v02(tmp_path):
    bridge = dict.fromkeys(("schema", "repository", "base", "predecessor_context_utf8",
        "predecessor_manifest_utf8", "prior_installation_utf8", "old_enforcement", "new_enforcement",
        "old_policy_id", "new_policy_id", "manifest_sha256", "ledger", "old_registries",
        "new_registries", "commit_message", "publication_ledger"))
    bridge.update(schema=REVIEW.ENTRY_BRIDGE_VERSION, repository=REVIEW.REPOSITORY,
                  base=REVIEW.G6B_BASE, old_policy_id=REVIEW.ENTRY_OLD_POLICY)
    with pytest.raises(REVIEW.Refusal, match="ENTRY_FIXED_BASIS"):
        REVIEW._entry_maintenance_v02(tmp_path, {}, {}, bridge)
