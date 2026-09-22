#!/usr/bin/env python3
"""Capture and enforce the exact G38 owner landing preconditions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


BASE = "d199199a578c078c913a2381f595549175bd9235"
BASE_PARENT = "2f328be634247be11bc18a3b22a919f393d6ed1d"
BASE_TREE = "26d63912117a2324cc7e711407be33123f55ab81"
ARCHIVE_SHA256 = "ad24dc58ae05784694ee83ae75affc44c3c0058b442faa31add77d3c2f8ee1e9"
SCRIPT_SHA256 = "e0f8928c370738641e46141b1e0e091b43fa85767116473f0779b04b79cf4047"
PAYLOAD_SHA256 = "2e4b8a60fef5f335998f03e204c552735f4689b329710c33b374d530082ac31f"
EXPECTED_REMOTE_URLS = {
    "https://github.com/AAkhtanin/hedgehog-os",
    "https://github.com/AAkhtanin/hedgehog-os.git",
    "git@github.com:AAkhtanin/hedgehog-os.git",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(owner: Path, *args: str) -> bytes:
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(("git", *args), cwd=owner, env=environment)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    status = _git(args.owner, "status", "--porcelain=v1", "-uall").decode()
    staged = _git(args.owner, "diff", "--cached", "--name-only").decode()
    fetch_urls = _git(args.owner, "remote", "get-url", "--all", "origin").decode().splitlines()
    push_urls = _git(
        args.owner, "remote", "get-url", "--push", "--all", "origin"
    ).decode().splitlines()
    remote_main = _git(
        args.owner, "ls-remote", "origin", "refs/heads/main"
    ).decode().split()
    tracked_rows = [
        row
        for row in _git(args.owner, "ls-tree", "-rz", BASE).split(b"\0")
        if row
    ]
    result = {
        "archive": {
            "bytes": args.archive.stat().st_size,
            "sha256": _sha(args.archive),
        },
        "owner": {
            "branch": _git(args.owner, "branch", "--show-current").decode().strip(),
            "fetch_urls": fetch_urls,
            "head": _git(args.owner, "rev-parse", "HEAD").decode().strip(),
            "index_sha256": _sha(args.owner / ".git/index"),
            "parent": _git(args.owner, "rev-parse", "HEAD^").decode().strip(),
            "push_urls": push_urls,
            "remote_main": remote_main,
            "staging_empty": not staged,
            "status_clean": not status,
            "tracked_rows": len(tracked_rows),
            "tree": _git(args.owner, "rev-parse", "HEAD^{tree}").decode().strip(),
        },
        "payload_manifest": {
            "bytes": args.payload.stat().st_size,
            "sha256": _sha(args.payload),
        },
        "script": {
            "bytes": args.script.stat().st_size,
            "sha256": _sha(args.script),
        },
        "status": "PASS",
    }
    owner = result["owner"]
    if result["archive"] != {"bytes": 19193417, "sha256": ARCHIVE_SHA256}:
        raise ValueError("review archive identity mismatch")
    if result["script"] != {"bytes": 22305, "sha256": SCRIPT_SHA256}:
        raise ValueError("owner script identity mismatch")
    if result["payload_manifest"] != {"bytes": 17122, "sha256": PAYLOAD_SHA256}:
        raise ValueError("owner payload identity mismatch")
    if (
        owner["branch"] != "main"
        or owner["head"] != BASE
        or owner["parent"] != BASE_PARENT
        or owner["tree"] != BASE_TREE
        or not owner["status_clean"]
        or not owner["staging_empty"]
        or owner["tracked_rows"] != 1095
    ):
        raise ValueError("owner basis or cleanliness mismatch")
    if not fetch_urls or not push_urls:
        raise ValueError("owner remote URL is missing")
    if any(value not in EXPECTED_REMOTE_URLS for value in fetch_urls + push_urls):
        raise ValueError("owner remote URL mismatch")
    if remote_main != [BASE, "refs/heads/main"]:
        raise ValueError("remote main mismatch")

    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
