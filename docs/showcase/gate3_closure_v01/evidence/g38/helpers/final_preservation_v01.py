#!/usr/bin/env python3
"""Confirm final G38 owner, evidence and historical-helper preservation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


COMMIT = "71e166ccb88b024fd3ca3a25e17da110c6db1a3f"
BASE = "d199199a578c078c913a2381f595549175bd9235"
TREE = "71e0438a4ef8532a3047a6e87061240d5b958a31"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(owner: Path, *args: str) -> str:
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(("git", *args), cwd=owner, env=environment).decode().strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    command_results = {}
    incomplete = []
    current_wrapper = []
    for directory in sorted((args.evidence / "commands").glob("[0-9][0-9][0-9][0-9]_*")):
        receipt_path = directory / "receipt.json"
        if not receipt_path.is_file():
            if directory.name.endswith("_final_preservation"):
                current_wrapper.append(directory.name)
            else:
                incomplete.append(directory.name)
            continue
        receipt = json.loads(receipt_path.read_text())
        command_results[directory.name] = {
            "elapsed_seconds": receipt["elapsed_seconds"],
            "rc": receipt["rc"],
            "stderr_sha256": receipt["stderr"]["sha256"],
            "stdout_sha256": receipt["stdout"]["sha256"],
        }
    if (
        incomplete
        or len(current_wrapper) != 1
        or not command_results
        or any(row["rc"] for row in command_results.values())
    ):
        raise ValueError("incomplete or failed G38 command evidence")

    recovery = json.loads((args.evidence / "final/RECOVERY_STATUS.json").read_text())
    for expected, row in recovery["recovered"].items():
        path = args.evidence / row["path"]
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing historical helper evidence")
        if path.stat().st_size != row["bytes"] or _sha(path) != expected:
            raise ValueError("historical helper identity mismatch")
    if recovery["executed_by_g38"] is not False or len(recovery["unresolved"]) != 2:
        raise ValueError("historical helper classification mismatch")

    owner = {
        "branch": _git(args.owner, "branch", "--show-current"),
        "commit": _git(args.owner, "rev-parse", "HEAD"),
        "parent": _git(args.owner, "rev-parse", "HEAD^"),
        "remote_commit": _git(args.owner, "rev-parse", "refs/remotes/origin/main"),
        "staging_empty": not _git(args.owner, "diff", "--cached", "--name-only"),
        "status_clean": not _git(args.owner, "status", "--porcelain=v1", "-uall"),
        "tree": _git(args.owner, "rev-parse", "HEAD^{tree}"),
    }
    if owner != {
        "branch": "main",
        "commit": COMMIT,
        "parent": BASE,
        "remote_commit": COMMIT,
        "staging_empty": True,
        "status_clean": True,
        "tree": TREE,
    }:
        raise ValueError("final owner preservation mismatch")

    execution_results = tuple((args.evidence / "owner_execution").rglob("result.json"))
    if len(execution_results) != 1:
        raise ValueError("owner execution result count mismatch")
    execution = json.loads(execution_results[0].read_text())
    if (
        execution.get("status") != "PASS"
        or execution.get("commit") != COMMIT
        or not execution.get("finalizers_complete")
        or not execution.get("commit_performed")
        or not execution.get("push_performed")
    ):
        raise ValueError("owner execution finality mismatch")

    result = {
        "all_prior_recorded_commands_final": True,
        "command_results": command_results,
        "current_wrapper_receipt_pending": current_wrapper[0],
        "gate3_status": "PENDING_INDEPENDENT_CLOSURE_REVIEW",
        "historical_helpers": {
            "executed_by_g38": False,
            "recovered_exact": len(recovery["recovered"]),
            "unresolved_failed_or_superseded": len(recovery["unresolved"]),
        },
        "new_runtime_collections": 0,
        "owner": owner,
        "provider_model_calls": 0,
        "real_effects": 0,
        "status": "PASS",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (args.evidence / "final/COMMAND_RESULTS.json").write_text(
        json.dumps(command_results, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
