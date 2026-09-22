#!/usr/bin/env python3
"""Apply a reviewed G37R return to owner, verify, commit and normally push.

G37R only prepares and tests this procedure. Running it against the real owner
requires a separate explicit G3-8 instruction and an independently reviewed
return-archive SHA-256.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import traceback


BASE = "d199199a578c078c913a2381f595549175bd9235"
BASE_PARENT = "2f328be634247be11bc18a3b22a919f393d6ed1d"
BASE_TREE = "26d63912117a2324cc7e711407be33123f55ab81"
FINAL_TREE = "71e0438a4ef8532a3047a6e87061240d5b958a31"
GUARD = "tools/check_active_architecture_authority_v01.py"
EXPECTED_REMOTE_URLS = {
    "https://github.com/AAkhtanin/hedgehog-os",
    "https://github.com/AAkhtanin/hedgehog-os.git",
    "git@github.com:AAkhtanin/hedgehog-os.git",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def blob(value: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(value)).encode() + b"\0" + value
    ).hexdigest()


class Journal:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=False)
        self.counter = 0
        self.stage = "INITIALIZING"
        self.rows: list[dict[str, object]] = []

    def set_stage(self, stage: str) -> None:
        self.stage = stage
        row = {"at": utc_now(), "stage": stage}
        self.rows.append(row)
        with (self.directory / "phases.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")

    def run(
        self,
        argv: tuple[str, ...],
        *,
        cwd: Path,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        self.counter += 1
        stem = f"{self.counter:03d}"
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
        )
        (self.directory / f"{stem}.stdout.bin").write_bytes(completed.stdout)
        (self.directory / f"{stem}.stderr.bin").write_bytes(completed.stderr)
        row = {
            "argv": list(argv),
            "cwd": str(cwd),
            "returncode": completed.returncode,
            "stage": self.stage,
            "stderr_bytes": len(completed.stderr),
            "stderr_sha256": digest(completed.stderr),
            "stdout_bytes": len(completed.stdout),
            "stdout_sha256": digest(completed.stdout),
        }
        self.rows.append(row)
        with (self.directory / "commands.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
        if check and completed.returncode:
            raise RuntimeError(
                f"command failed at {self.stage}: {argv!r}, rc={completed.returncode}"
            )
        return completed


def safe_relative(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def verify_return_archive(archive: Path, expected_sha256: str) -> Path:
    raw = archive.read_bytes()
    if digest(raw) != expected_sha256:
        raise ValueError("return archive SHA-256 mismatch")
    temporary = Path(tempfile.mkdtemp(prefix="g38_reviewed_return_", dir="/private/tmp"))
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise ValueError("duplicate archive member")
        if any(
            not member.isfile() or not safe_relative(member.name)
            for member in members
        ):
            raise ValueError("archive must contain safe regular files only")
        manifests = [name for name in names if name.endswith("/MANIFEST.tsv")]
        if len(manifests) != 1:
            raise ValueError("exactly one return manifest is required")
        manifest_member = bundle.getmember(manifests[0])
        manifest_raw = bundle.extractfile(manifest_member).read()
        rows = {}
        for line in manifest_raw.decode("utf-8").splitlines():
            expected, size, mode, name = line.split("\t", 3)
            if name in rows:
                raise ValueError("duplicate manifest row")
            rows[name] = (expected, int(size), int(mode, 8))
        expected_names = set(names) - {manifests[0]}
        if set(rows) != expected_names:
            raise ValueError("return manifest coverage mismatch")
        for member in members:
            if member.name == manifests[0]:
                continue
            value = bundle.extractfile(member).read()
            if rows[member.name] != (digest(value), len(value), member.mode & 0o777):
                raise ValueError("return manifest identity mismatch: " + member.name)
        for member in members:
            target = temporary / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.extractfile(member).read())
            os.chmod(target, member.mode & 0o777)
    payloads = list(temporary.rglob("owner_payload/MANIFEST.json"))
    if len(payloads) != 1:
        raise ValueError("exactly one owner payload is required")
    return payloads[0].parent


def verify_payload(payload: Path) -> dict[str, object]:
    manifest = json.loads((payload / "MANIFEST.json").read_text(encoding="utf-8"))
    if (
        manifest["basis"] != BASE
        or manifest["basis_parent"] != BASE_PARENT
        or manifest["basis_tree"] != BASE_TREE
        or manifest["final_tree"] != FINAL_TREE
        or manifest["path_count"] != 59
        or manifest["addition_count"] != 40
        or manifest["modification_count"] != 19
        or manifest["protected_count"] != 1076
    ):
        raise ValueError("owner payload basis or inventory mismatch")
    for key in ("cumulative_patch", "incremental_patch"):
        record = manifest[key]
        value = (payload / record["path"]).read_bytes()
        if len(value) != record["bytes"] or digest(value) != record["sha256"]:
            raise ValueError("owner payload patch mismatch: " + key)
    identities = manifest["source_identities"]
    if len(identities) != 59:
        raise ValueError("owner payload source inventory mismatch")
    for relative, record in identities.items():
        if not safe_relative(relative):
            raise ValueError("unsafe payload path")
        path = payload / "postimages" / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing regular postimage: " + relative)
        value = path.read_bytes()
        mode = path.stat().st_mode & 0o777
        if (
            len(value) != record["bytes"]
            or digest(value) != record["sha256"]
            or blob(value) != record["git_blob"]
            or mode != int(record["mode"], 8)
        ):
            raise ValueError("postimage identity mismatch: " + relative)
    return manifest


def git_output(journal: Journal, owner: Path, *args: str) -> str:
    return journal.run(("git", *args), cwd=owner).stdout.decode().strip()


def assert_no_operation_state(journal: Journal, owner: Path) -> None:
    for marker in (
        "MERGE_HEAD",
        "REBASE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_LOG",
        "rebase-merge",
        "rebase-apply",
        "sequencer",
        "index.lock",
        "HEAD.lock",
        "packed-refs.lock",
    ):
        value = git_output(journal, owner, "rev-parse", "--git-path", marker)
        path = Path(value)
        if not path.is_absolute():
            path = owner / path
        if path.exists():
            raise RuntimeError("active Git operation or lock: " + marker)


def baseline_inventory(journal: Journal, owner: Path) -> dict[str, tuple[str, str]]:
    raw = journal.run(("git", "ls-tree", "-rz", BASE), cwd=owner).stdout
    result = {}
    for row in raw.split(b"\0"):
        if not row:
            continue
        metadata, encoded = row.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        relative = encoded.decode()
        if kind != "blob" or mode not in {"100644", "100755"} or relative in result:
            raise RuntimeError("unsupported or duplicate baseline entry")
        result[relative] = (mode, oid)
    if len(result) != 1095:
        raise RuntimeError("baseline tracked inventory mismatch")
    return result


def assert_no_symlink_ancestor(owner: Path, target: Path) -> None:
    current = target
    while current != owner:
        if current.is_symlink():
            raise RuntimeError("symlink in owner target path: " + str(target))
        current = current.parent
    if current != owner or owner.is_symlink():
        raise RuntimeError("owner target escapes exact root")


def verify_preapply_worktree(
    journal: Journal,
    owner: Path,
    actions: dict[str, str],
) -> None:
    inventory = baseline_inventory(journal, owner)
    for relative, (mode, oid) in inventory.items():
        target = owner / relative
        assert_no_symlink_ancestor(owner, target)
        if not target.is_file() or target.is_symlink():
            raise RuntimeError("baseline path is not a regular file: " + relative)
        value = target.read_bytes()
        actual_mode = "100755" if target.stat().st_mode & 0o111 else "100644"
        if blob(value) != oid or actual_mode != mode:
            raise RuntimeError("baseline bytes or mode mismatch: " + relative)

    visible = journal.run(("git", "ls-files", "-v", "-z"), cwd=owner).stdout
    rows = [row for row in visible.split(b"\0") if row]
    if len(rows) != 1095 or any(not row.startswith(b"H ") for row in rows):
        raise RuntimeError("hidden or nonstandard index flag")
    debug = journal.run(("git", "ls-files", "--debug"), cwd=owner).stdout
    flags = re.findall(rb"flags: ([0-9a-fA-F]+)", debug)
    if len(flags) != 1095 or any(int(value, 16) != 0 for value in flags):
        raise RuntimeError("index debug flags are not zero")

    for relative, action in actions.items():
        target = owner / relative
        assert_no_symlink_ancestor(owner, target)
        if action == "A":
            if target.exists() or target.is_symlink():
                raise RuntimeError("addition collides with an existing path: " + relative)
            ignored = journal.run(
                ("git", "check-ignore", "--no-index", "-q", "--", relative),
                cwd=owner,
                check=False,
            )
            if ignored.returncode == 0:
                raise RuntimeError("addition collides with an ignored path: " + relative)
            if ignored.returncode != 1:
                raise RuntimeError("unable to classify ignored addition: " + relative)


def parse_name_status(value: str) -> dict[str, str]:
    result = {}
    for line in value.splitlines():
        if not line:
            continue
        action, name = line.split("\t", 1)
        if action not in {"A", "M"} or name in result:
            raise ValueError("unexpected name-status entry")
        result[name] = action
    return result


def exact_unstaged(journal: Journal, owner: Path, actions: dict[str, str]) -> None:
    modifications = parse_name_status(
        git_output(journal, owner, "diff", "--name-status", "--no-renames")
    )
    additions = {
        name: "A"
        for name in git_output(
            journal, owner, "ls-files", "--others", "--exclude-standard"
        ).splitlines()
        if name
    }
    if modifications | additions != actions or set(modifications) & set(additions):
        raise RuntimeError("unstaged proposal is not the exact reviewed ledger")
    if git_output(journal, owner, "diff", "--cached", "--name-only"):
        raise RuntimeError("index is not empty before staging")


def exact_staged(journal: Journal, owner: Path, actions: dict[str, str]) -> None:
    staged = parse_name_status(
        git_output(
            journal,
            owner,
            "diff",
            "--cached",
            "--name-status",
            "--no-renames",
            BASE,
        )
    )
    if staged != actions:
        raise RuntimeError("staged proposal is not the exact reviewed ledger")
    if git_output(journal, owner, "diff", "--name-only"):
        raise RuntimeError("worktree differs from staged proposal")


def guard(journal: Journal, owner: Path, python: Path, expected: str) -> None:
    completed = journal.run(
        (str(python), "-B", GUARD, "--root", str(owner)), cwd=owner
    )
    output = completed.stdout.decode()
    if "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS" not in output:
        raise RuntimeError("authority guard did not pass")
    if f"G37_PHASE={expected}" not in output:
        raise RuntimeError("authority guard phase mismatch")


def execution_archive(journal: Journal, output: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = output / f"RADIOLARIA_GATE3_G38_OWNER_EXECUTION_{stamp}.tar.gz"
    files = sorted(path for path in journal.directory.rglob("*") if path.is_file())
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as bundle:
        for path in files:
            bundle.add(path, arcname=path.relative_to(journal.directory))
    return archive


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    source = result.add_mutually_exclusive_group(required=True)
    source.add_argument("--archive", type=Path)
    source.add_argument("--payload-dir", type=Path)
    result.add_argument("--archive-sha256")
    result.add_argument("--owner", type=Path, required=True)
    result.add_argument("--python", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument(
        "--commit-message", default="Complete Gate 3 frozen release admission"
    )
    result.add_argument("--execute", action="store_true")
    result.add_argument("--fixture-mode", action="store_true")
    return result


def main(arguments: list[str] | None = None) -> int:
    args = parser().parse_args(arguments)
    if not args.execute:
        raise SystemExit("--execute is required; G37 preparation never implies execution")
    owner = args.owner.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    journal = Journal(output / ("g38_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    started = utc_now()
    result: dict[str, object] = {
        "started_at": started,
        "owner": str(owner),
        "fixture_mode": args.fixture_mode,
        "commit_performed": False,
        "push_performed": False,
        "status": "RUNNING",
    }
    returncode = 1
    try:
        journal.set_stage("VERIFY_INPUT")
        if args.archive:
            if not args.archive_sha256:
                raise ValueError("--archive-sha256 is required with --archive")
            payload = verify_return_archive(
                args.archive.resolve(), args.archive_sha256
            )
        else:
            if not args.fixture_mode:
                raise ValueError("--payload-dir is restricted to fixture mode")
            payload = args.payload_dir.resolve()
        manifest = verify_payload(payload)
        actions = {
            relative: record["action"]
            for relative, record in manifest["source_identities"].items()
        }

        journal.set_stage("VERIFY_OWNER")
        if args.fixture_mode:
            if not str(owner).startswith(("/private/tmp/", "/tmp/")):
                raise RuntimeError("fixture owner must be under a temporary root")
        elif owner != Path("/Users/admin/Projects/hedgehog-os"):
            raise RuntimeError("normal execution is restricted to the exact owner path")
        if git_output(journal, owner, "branch", "--show-current") != "main":
            raise RuntimeError("owner branch is not main")
        if git_output(journal, owner, "rev-parse", "HEAD") != BASE:
            raise RuntimeError("owner HEAD mismatch")
        if git_output(journal, owner, "rev-parse", "HEAD^") != BASE_PARENT:
            raise RuntimeError("owner parent mismatch")
        if git_output(journal, owner, "rev-parse", "HEAD^{tree}") != BASE_TREE:
            raise RuntimeError("owner tree mismatch")
        if git_output(journal, owner, "rev-parse", "refs/remotes/origin/main") != BASE:
            raise RuntimeError("owner origin/main mismatch")
        remote = git_output(journal, owner, "config", "--get", "remote.origin.url")
        if not args.fixture_mode and remote not in EXPECTED_REMOTE_URLS:
            raise RuntimeError("owner remote URL mismatch")
        if git_output(journal, owner, "status", "--porcelain=v1", "-uall"):
            raise RuntimeError("owner is not clean")
        if git_output(journal, owner, "write-tree") != BASE_TREE:
            raise RuntimeError("owner index tree mismatch")
        assert_no_operation_state(journal, owner)
        verify_preapply_worktree(journal, owner, actions)
        remote_row = git_output(
            journal, owner, "ls-remote", "origin", "refs/heads/main"
        ).split()
        if remote_row != [BASE, "refs/heads/main"]:
            raise RuntimeError("pre-apply remote main mismatch")

        journal.set_stage("APPLY_POSTIMAGES")
        for relative, record in manifest["source_identities"].items():
            source_path = payload / "postimages" / relative
            target = owner / relative
            assert_no_symlink_ancestor(owner, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source_path.read_bytes())
            os.chmod(target, int(record["mode"], 8))
        exact_unstaged(journal, owner, actions)
        journal.run(("git", "diff", "--check"), cwd=owner)
        guard(journal, owner, args.python, "G37_FROZEN_RELEASE_PROPOSAL_UNSTAGED")

        journal.set_stage("STAGE_EXACT_PROPOSAL")
        journal.run(("git", "add", "--", *sorted(actions)), cwd=owner)
        exact_staged(journal, owner, actions)
        journal.run(("git", "diff", "--cached", "--check"), cwd=owner)
        guard(journal, owner, args.python, "G37_FROZEN_RELEASE_PROPOSAL_STAGED")
        if git_output(journal, owner, "write-tree") != FINAL_TREE:
            raise RuntimeError("staged final tree mismatch")

        journal.set_stage("COMMIT")
        journal.run(("git", "commit", "-m", args.commit_message), cwd=owner)
        commit = git_output(journal, owner, "rev-parse", "HEAD")
        result["commit"] = commit
        result["commit_performed"] = True
        if git_output(journal, owner, "rev-parse", "HEAD^") != BASE:
            raise RuntimeError("committed parent mismatch")
        if git_output(journal, owner, "rev-parse", "HEAD^{tree}") != FINAL_TREE:
            raise RuntimeError("committed tree mismatch")
        guard(journal, owner, args.python, "G37_FROZEN_RELEASE_COMMITTED")

        journal.set_stage("POSTCOMMIT_CHECKS")
        environment = dict(
            os.environ,
            PYTHONDONTWRITEBYTECODE="1",
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            PYTHONPATH=str(owner),
        )
        journal.run(
            (
                str(args.python),
                "-B",
                "-m",
                "pytest",
                "-q",
                "tests/test_active_architecture_authority_v01.py::test_g37_clean_sole_parent_child_classification_v01",
                "tests/test_active_architecture_authority_v01.py::test_g37_current_registration_complete_negative_matrix_v01",
                "tests/test_repository_release_spine_v01.py::test_g37_binder_has_final_precedence_v01",
                "tests/test_repository_release_spine_v01.py::test_g37_current_registration_pins_actual_release_files_v01",
                "tests/test_gate3_mechanism_registration_v01.py",
            ),
            cwd=owner,
            env=environment,
        )
        if git_output(journal, owner, "status", "--porcelain=v1", "-uall"):
            raise RuntimeError("postcommit owner is not clean")

        journal.set_stage("NORMAL_PUSH_AND_READBACK")
        journal.run(("git", "push", "origin", "HEAD:main"), cwd=owner)
        result["push_performed"] = True
        journal.run(("git", "fetch", "origin", "main"), cwd=owner)
        if git_output(journal, owner, "rev-parse", "refs/remotes/origin/main") != commit:
            raise RuntimeError("fetched remote commit mismatch")
        remote_row = git_output(
            journal, owner, "ls-remote", "origin", "refs/heads/main"
        ).split()
        if remote_row != [commit, "refs/heads/main"]:
            raise RuntimeError("independent remote readback mismatch")
        if git_output(journal, owner, "status", "--porcelain=v1", "-uall"):
            raise RuntimeError("final owner is not clean")
        result["status"] = "PASS"
        returncode = 0
    except Exception as exc:
        result["status"] = "FAIL"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
    finally:
        result["finished_at"] = utc_now()
        result["final_stage"] = journal.stage
        result["commands"] = journal.counter
        result["finalizers_complete"] = True
        (journal.directory / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        archive = execution_archive(journal, output)
        print(
            json.dumps(
                {
                    "execution_archive": str(archive),
                    "result": result["status"],
                    "stage": journal.stage,
                },
                sort_keys=True,
            )
        )
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
