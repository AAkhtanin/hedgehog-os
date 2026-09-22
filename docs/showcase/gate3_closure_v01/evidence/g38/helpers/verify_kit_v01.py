#!/usr/bin/env python3
"""Verify the extracted G38 instruction kit against its closed manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    expected = {row["path"]: row for row in manifest["files"]}
    actual = {
        str(path.relative_to(args.root)): path
        for path in args.root.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if set(actual) != set(expected):
        raise ValueError("kit manifest coverage mismatch")

    verified = {}
    for relative, row in sorted(expected.items()):
        path = actual[relative]
        metadata = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise ValueError("kit member is not a regular file: " + relative)
        value = path.read_bytes()
        observed = {
            "bytes": len(value),
            "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
            "sha256": hashlib.sha256(value).hexdigest(),
        }
        if observed != {key: row[key] for key in observed}:
            raise ValueError("kit member mismatch: " + relative)
        verified[relative] = observed

    result = {
        "files": verified,
        "format": manifest["format"],
        "manifest_rows": len(expected),
        "status": "PASS",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
