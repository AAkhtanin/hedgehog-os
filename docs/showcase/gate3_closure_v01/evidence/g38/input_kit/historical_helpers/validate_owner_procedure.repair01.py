#!/usr/bin/env python3
"""Exercise the unexecuted G38 owner procedure against disposable local remotes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


BASE = "d199199a578c078c913a2381f595549175bd9235"
FINAL_TREE = "71e0438a4ef8532a3047a6e87061240d5b958a31"


def _run(cwd: Path, *argv: str, check: bool = True):
    return subprocess.run(argv, cwd=cwd, check=check, capture_output=True)


def _git(cwd: Path, *argv: str) -> str:
    return _run(cwd, "git", *argv).stdout.decode().strip()


def _clone_fixture(remote: Path, destination: Path) -> None:
    _run(destination.parent, "git", "clone", str(remote), str(destination))
    _git(destination, "config", "user.name", "G37R fixture")
    _git(destination, "config", "user.email", "fixture@example.invalid")
    canonical = "https://github.com/AAkhtanin/hedgehog-os.git"
    _git(destination, "remote", "set-url", "origin", canonical)
    _git(destination, "config", f"url.{remote.as_uri()}.insteadOf", canonical)
    if _git(destination, "rev-parse", "HEAD") != BASE:
        raise RuntimeError("fixture HEAD mismatch")


def _invoke(
    *,
    script: Path,
    owner: Path,
    payload: Path,
    python: Path,
    output: Path,
    execute: bool,
) -> dict[str, object]:
    argv = [
        str(python),
        "-B",
        str(script),
        "--payload-dir",
        str(payload),
        "--owner",
        str(owner),
        "--python",
        str(python),
        "--output",
        str(output),
        "--fixture-mode",
    ]
    if execute:
        argv.append("--execute")
    completed = subprocess.run(argv, check=False, capture_output=True)
    output.mkdir(parents=True, exist_ok=True)
    (output / "invocation.stdout.bin").write_bytes(completed.stdout)
    (output / "invocation.stderr.bin").write_bytes(completed.stderr)
    result_files = sorted(output.glob("g38_*/result.json"))
    result = json.loads(result_files[-1].read_text()) if result_files else None
    return {
        "argv": argv,
        "returncode": completed.returncode,
        "result": result,
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    with tempfile.TemporaryDirectory(prefix="g37r_owner_procedure_", dir="/private/tmp") as raw:
        temporary = Path(raw)
        remote = temporary / "origin.git"
        _run(temporary, "git", "clone", "--bare", str(args.repository), str(remote))
        _run(temporary, "git", "--git-dir", str(remote), "update-ref", "refs/heads/main", BASE)
        _run(temporary, "git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/main")

        no_execute_owner = temporary / "no_execute_owner"
        _clone_fixture(remote, no_execute_owner)
        no_execute = _invoke(
            script=args.script,
            owner=no_execute_owner,
            payload=args.payload,
            python=args.python,
            output=args.output / "no_execute",
            execute=False,
        )
        if no_execute["returncode"] == 0:
            raise RuntimeError("procedure ran without explicit --execute")

        hidden_owner = temporary / "hidden_owner"
        _clone_fixture(remote, hidden_owner)
        _git(hidden_owner, "update-index", "--assume-unchanged", "AGENTS.md")
        hidden = _invoke(
            script=args.script,
            owner=hidden_owner,
            payload=args.payload,
            python=args.python,
            output=args.output / "hidden_flag_refusal",
            execute=True,
        )
        if (
            hidden["returncode"] == 0
            or hidden["result"] is None
            or hidden["result"]["status"] != "FAIL"
            or "hidden or nonstandard index flag" not in hidden["result"]["error"]
        ):
            raise RuntimeError("hidden index flag was not refused")

        ignored_owner = temporary / "ignored_owner"
        _clone_fixture(remote, ignored_owner)
        addition = next(
            relative
            for relative, record in json.loads(
                (args.payload / "MANIFEST.json").read_text()
            )["source_identities"].items()
            if record["action"] == "A"
        )
        info_exclude = Path(_git(ignored_owner, "rev-parse", "--git-path", "info/exclude"))
        if not info_exclude.is_absolute():
            info_exclude = ignored_owner / info_exclude
        with info_exclude.open("a") as stream:
            stream.write("/" + addition + "\n")
        collision = ignored_owner / addition
        collision.parent.mkdir(parents=True, exist_ok=True)
        collision.write_text("ignored collision\n")
        if _git(ignored_owner, "status", "--porcelain=v1", "-uall"):
            raise RuntimeError("ignored fixture is unexpectedly visible")
        ignored = _invoke(
            script=args.script,
            owner=ignored_owner,
            payload=args.payload,
            python=args.python,
            output=args.output / "ignored_collision_refusal",
            execute=True,
        )
        if (
            ignored["returncode"] == 0
            or ignored["result"] is None
            or ignored["result"]["status"] != "FAIL"
            or "addition collides with an existing path" not in ignored["result"]["error"]
        ):
            raise RuntimeError("ignored collision was not refused")

        success_owner = temporary / "success_owner"
        _clone_fixture(remote, success_owner)
        success = _invoke(
            script=args.script,
            owner=success_owner,
            payload=args.payload,
            python=args.python,
            output=args.output / "success",
            execute=True,
        )
        if (
            success["returncode"] != 0
            or success["result"] is None
            or success["result"]["status"] != "PASS"
        ):
            raise RuntimeError(f"successful fixture failed: {success!r}")
        commit = _git(success_owner, "rev-parse", "HEAD")
        if (
            _git(success_owner, "rev-parse", "HEAD^") != BASE
            or _git(success_owner, "rev-parse", "HEAD^{tree}") != FINAL_TREE
            or _git(success_owner, "status", "--porcelain=v1", "-uall")
        ):
            raise RuntimeError("successful fixture final state mismatch")
        remote_main = _run(
            temporary,
            "git",
            "--git-dir",
            str(remote),
            "rev-parse",
            "refs/heads/main",
        ).stdout.decode().strip()
        if remote_main != commit:
            raise RuntimeError("local remote readback mismatch")

    summary = {
        "final_tree": FINAL_TREE,
        "hidden_flag_refusal": hidden,
        "ignored_collision_refusal": ignored,
        "no_execute_refusal": no_execute,
        "normal_push_readback": "PASS_LOCAL_DISPOSABLE_REMOTE",
        "real_owner_invoked": False,
        "real_remote_invoked": False,
        "success": success,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
