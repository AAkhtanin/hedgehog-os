#!/usr/bin/env python3
"""Run one bounded command and preserve source-bound raw evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def _utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        raise SystemExit("command required")

    serial = len(tuple(args.evidence.glob("[0-9][0-9][0-9][0-9]_*"))) + 1
    command_dir = args.evidence / f"{serial:04d}_{args.label}"
    command_dir.mkdir(parents=True, exist_ok=False)
    sources = {}
    for raw in args.source:
        path = Path(raw)
        if not path.is_absolute():
            path = args.cwd / path
        sources[str(path)] = {
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
    environment = {
        key: os.environ[key]
        for key in ("PATH", "PYTHONPATH", "PYTHONPYCACHEPREFIX")
        if key in os.environ
    }
    started = _utc()
    started_ns = time.time_ns()
    (command_dir / "argv.json").write_text(
        json.dumps(
            {
                "argv": command,
                "cwd": str(args.cwd),
                "environment": environment,
                "label": args.label,
                "sources": sources,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (command_dir / "phases.jsonl").write_text(
        json.dumps({"event": "START", "label": args.label, "time": started}) + "\n"
    )
    with (command_dir / "stdout.raw").open("wb") as stdout, (
        command_dir / "stderr.raw"
    ).open("wb") as stderr:
        process = subprocess.Popen(command, cwd=args.cwd, stdout=stdout, stderr=stderr)
        (command_dir / "started.json").write_text(
            json.dumps(
                {
                    "argv": command,
                    "cwd": str(args.cwd),
                    "label": args.label,
                    "pid": process.pid,
                    "started_at": started,
                    "started_ns": started_ns,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        while process.poll() is None:
            with (command_dir / "heartbeats.jsonl").open("a") as heartbeat:
                heartbeat.write(
                    json.dumps(
                        {
                            "event": "HEARTBEAT",
                            "elapsed_seconds": (time.time_ns() - started_ns) / 1e9,
                            "pid": process.pid,
                            "time": _utc(),
                        }
                    )
                    + "\n"
                )
            time.sleep(1.0)
        rc = process.wait()
    ended = _utc()
    elapsed = (time.time_ns() - started_ns) / 1e9
    event = {"event": "END", "label": args.label, "rc": rc, "time": ended}
    with (command_dir / "phases.jsonl").open("a") as phases:
        phases.write(json.dumps(event) + "\n")
    receipt = {
        "argv": command,
        "cwd": str(args.cwd),
        "elapsed_seconds": elapsed,
        "ended_at": ended,
        "label": args.label,
        "rc": rc,
        "sources": sources,
        "started_at": started,
        "stderr": {
            "bytes": (command_dir / "stderr.raw").stat().st_size,
            "sha256": _sha256(command_dir / "stderr.raw"),
        },
        "stdout": {
            "bytes": (command_dir / "stdout.raw").stat().st_size,
            "sha256": _sha256(command_dir / "stdout.raw"),
        },
    }
    (command_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(command_dir)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
