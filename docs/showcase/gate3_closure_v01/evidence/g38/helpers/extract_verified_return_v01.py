#!/usr/bin/env python3
"""Verify and safely extract the exact reviewed G37R return archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--bytes", type=int, required=True)
    parser.add_argument("--members", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()

    archive_value = args.archive.read_bytes()
    if len(archive_value) != args.bytes or _sha(archive_value) != args.sha256:
        raise ValueError("archive identity mismatch")
    if not args.output.is_dir() or any(args.output.iterdir()):
        raise ValueError("extraction directory is not empty")

    with tarfile.open(args.archive, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [member.name for member in members]
        if len(members) != args.members or len(names) != len(set(names)):
            raise ValueError("archive member count or uniqueness mismatch")
        prefix = args.prefix.rstrip("/") + "/"
        for member in members:
            path = PurePosixPath(member.name)
            if (
                not member.isfile()
                or path.is_absolute()
                or ".." in path.parts
                or not member.name.startswith(prefix)
            ):
                raise ValueError("unsafe archive member: " + member.name)

        manifest_name = prefix + "MANIFEST.tsv"
        if names.count(manifest_name) != 1:
            raise ValueError("archive manifest missing or duplicated")
        manifest_value = bundle.extractfile(manifest_name).read()
        rows = {}
        for line in manifest_value.decode().splitlines():
            expected_hash, expected_size, expected_mode, name = line.split("\t", 3)
            if name in rows:
                raise ValueError("duplicate manifest row: " + name)
            rows[name] = (
                expected_hash,
                int(expected_size),
                int(expected_mode, 8),
            )
        if len(rows) != args.rows or set(rows) != set(names) - {manifest_name}:
            raise ValueError("archive manifest coverage mismatch")

        verified = {}
        for member in members:
            value = bundle.extractfile(member).read()
            if member.name != manifest_name:
                observed = (_sha(value), len(value), member.mode & 0o777)
                if observed != rows[member.name]:
                    raise ValueError("archive member mismatch: " + member.name)
            target = args.output.joinpath(*PurePosixPath(member.name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
            target.chmod(member.mode & 0o777)
            verified[member.name] = {
                "bytes": len(value),
                "mode": f"{member.mode & 0o777:04o}",
                "sha256": _sha(value),
            }

    result = {
        "archive": str(args.archive),
        "bytes": len(archive_value),
        "gzip_crc": "PASS",
        "manifest_rows": len(rows),
        "prefix": args.prefix,
        "regular_members": len(verified),
        "safe_unique_paths": True,
        "sha256": _sha(archive_value),
        "status": "PASS",
    }
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
