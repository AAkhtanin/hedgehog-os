#!/usr/bin/env python3
"""Verify the exact landed G38 commit and independent remote readback."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


BASE = "d199199a578c078c913a2381f595549175bd9235"
BASE_TREE = "26d63912117a2324cc7e711407be33123f55ab81"
FINAL_TREE = "71e0438a4ef8532a3047a6e87061240d5b958a31"
EXPECTED_REMOTE_URLS = {
    "https://github.com/AAkhtanin/hedgehog-os",
    "https://github.com/AAkhtanin/hedgehog-os.git",
    "git@github.com:AAkhtanin/hedgehog-os.git",
}


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _blob(value: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(value)).encode() + b"\0" + value).hexdigest()


def _git(owner: Path, *args: str) -> bytes:
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(("git", *args), cwd=owner, env=environment)


def _tree(owner: Path, ref: str) -> dict[str, tuple[str, str]]:
    result = {}
    for row in _git(owner, "ls-tree", "-rz", ref).split(b"\0"):
        if not row:
            continue
        metadata, encoded = row.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        name = encoded.decode()
        if kind != "blob" or mode not in {"100644", "100755"} or name in result:
            raise ValueError("unsupported final tree entry")
        result[name] = mode, oid
    return result


def _name_status(owner: Path, base: str, commit: str) -> dict[str, str]:
    value = _git(
        owner,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "--no-renames",
        "-r",
        base,
        commit,
    ).decode()
    result = {}
    for line in value.splitlines():
        action, name = line.split("\t", 1)
        if action not in {"A", "M"} or name in result:
            raise ValueError("unexpected final name-status")
        result[name] = action
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--outer-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--paths", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.payload / "MANIFEST.json").read_text())
    identities = manifest["source_identities"]
    actions = {name: row["action"] for name, row in identities.items()}
    commit = _git(args.owner, "rev-parse", "HEAD").decode().strip()
    parents = _git(args.owner, "rev-list", "--parents", "-n", "1", commit).decode().split()
    if len(parents) != 2 or parents[1] != BASE:
        raise ValueError("final commit is not a sole-parent child of the accepted base")
    if _git(args.owner, "rev-parse", "HEAD^{tree}").decode().strip() != FINAL_TREE:
        raise ValueError("final local tree mismatch")
    if _git(args.owner, "rev-parse", f"{BASE}^{{tree}}").decode().strip() != BASE_TREE:
        raise ValueError("base tree mismatch")
    if _git(args.owner, "branch", "--show-current").decode().strip() != "main":
        raise ValueError("owner branch mismatch")
    if _git(args.owner, "status", "--porcelain=v1", "-uall"):
        raise ValueError("final owner is not clean")
    if _git(args.owner, "diff", "--cached", "--name-only"):
        raise ValueError("final staging is not empty")
    if _git(args.owner, "write-tree").decode().strip() != FINAL_TREE:
        raise ValueError("final index tree mismatch")

    observed_actions = _name_status(args.owner, BASE, commit)
    if observed_actions != actions or len(actions) != 59:
        raise ValueError("final changed-path ledger mismatch")
    base_tree = _tree(args.owner, BASE)
    final_tree = _tree(args.owner, commit)
    protected = sorted(set(base_tree) - set(actions))
    if len(base_tree) != 1095 or len(final_tree) != 1135 or len(protected) != 1076:
        raise ValueError("tracked or protected inventory count mismatch")
    if any(final_tree.get(name) != base_tree[name] for name in protected):
        raise ValueError("protected baseline path changed")

    verified_sources = {}
    for name, record in sorted(identities.items()):
        path = args.owner / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("landed source is not a regular file: " + name)
        value = path.read_bytes()
        mode = path.stat().st_mode & 0o777
        git_mode = "100755" if mode & 0o111 else "100644"
        observed = {
            "action": record["action"],
            "bytes": len(value),
            "git_blob": _blob(value),
            "mode": oct(mode),
            "sha256": _sha(value),
        }
        expected = {key: record[key] for key in observed}
        if observed != expected or final_tree.get(name) != (git_mode, record["git_blob"]):
            raise ValueError("landed source identity mismatch: " + name)
        verified_sources[name] = observed

    tracked_remote = _git(args.owner, "rev-parse", "refs/remotes/origin/main").decode().strip()
    remote_parent = _git(args.owner, "rev-parse", "refs/remotes/origin/main^").decode().strip()
    remote_tree = _git(args.owner, "rev-parse", "refs/remotes/origin/main^{tree}").decode().strip()
    remote_row = _git(args.owner, "ls-remote", "origin", "refs/heads/main").decode().split()
    fetch_urls = _git(args.owner, "remote", "get-url", "--all", "origin").decode().splitlines()
    push_urls = _git(
        args.owner, "remote", "get-url", "--push", "--all", "origin"
    ).decode().splitlines()
    if (
        tracked_remote != commit
        or remote_parent != BASE
        or remote_tree != FINAL_TREE
        or remote_row != [commit, "refs/heads/main"]
        or any(value not in EXPECTED_REMOTE_URLS for value in fetch_urls + push_urls)
    ):
        raise ValueError("remote readback mismatch")

    result = json.loads((args.journal / "result.json").read_text())
    outer = json.loads(args.outer_receipt.read_text())
    command_rows = [json.loads(line) for line in (args.journal / "commands.jsonl").read_text().splitlines()]
    pytest_rows = [(index, row) for index, row in enumerate(command_rows, 1) if "pytest" in row["argv"]]
    if len(pytest_rows) != 1:
        raise ValueError("expected one postcommit pytest command")
    pytest_index, pytest_row = pytest_rows[0]
    pytest_output = (args.journal / f"{pytest_index:03d}.stdout.bin").read_text()
    match = re.search(r"(\d+) passed in ([0-9.]+)s", pytest_output)
    if not match or int(match.group(1)) != 12 or pytest_row["returncode"] != 0:
        raise ValueError("postcommit pytest result mismatch")
    if (
        result.get("status") != "PASS"
        or result.get("commit") != commit
        or not result.get("commit_performed")
        or not result.get("push_performed")
        or result.get("final_stage") != "NORMAL_PUSH_AND_READBACK"
        or not result.get("finalizers_complete")
        or outer.get("rc") != 0
    ):
        raise ValueError("landing result or outer receipt mismatch")

    changed_lines = [f"{actions[name]}\t{name}\n" for name in sorted(actions)]
    args.paths.write_text("".join(changed_lines))
    ledger = {
        "base": BASE,
        "base_tree": BASE_TREE,
        "commit": commit,
        "final_tree": FINAL_TREE,
        "protected_paths": len(protected),
        "source_identities": verified_sources,
    }
    args.ledger.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    verification = {
        "branch": "main",
        "changed_paths": len(actions),
        "commit": commit,
        "commit_message": _git(args.owner, "show", "-s", "--format=%s", commit).decode().strip(),
        "fetch_urls": fetch_urls,
        "final_tree": FINAL_TREE,
        "index_tree": FINAL_TREE,
        "outer_elapsed_seconds": outer["elapsed_seconds"],
        "parent": BASE,
        "postcommit_tests": {
            "count": int(match.group(1)),
            "elapsed_seconds": float(match.group(2)),
            "result": "PASS",
        },
        "protected_paths": len(protected),
        "push_urls": push_urls,
        "remote_commit": tracked_remote,
        "remote_parent": remote_parent,
        "remote_tree": remote_tree,
        "source_paths": len(verified_sources),
        "staging_empty": True,
        "status": "PASS",
        "status_clean": True,
        "tracked_paths": len(final_tree),
    }
    args.output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verification, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
