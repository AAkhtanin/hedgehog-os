#!/usr/bin/env python3
"""Independent read-only verification for the completed G37R return."""

from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path, PurePosixPath
import tarfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("sha256")
    parser.add_argument("bytes", type=int)
    parser.add_argument("members", type=int)
    parser.add_argument("rows", type=int)
    args = parser.parse_args()
    raw = args.archive.read_bytes()
    assert len(raw) == args.bytes
    assert hashlib.sha256(raw).hexdigest() == args.sha256
    with gzip.open(args.archive, "rb") as stream:
        while stream.read(1024 * 1024):
            pass
    with tarfile.open(args.archive, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [member.name for member in members]
        assert len(members) == args.members == len(set(names))
        assert all(
            member.isfile()
            and not PurePosixPath(member.name).is_absolute()
            and ".." not in PurePosixPath(member.name).parts
            for member in members
        )
        manifests = [name for name in names if name.endswith("/MANIFEST.tsv")]
        assert len(manifests) == 1
        rows = {}
        for line in bundle.extractfile(manifests[0]).read().decode().splitlines():
            expected, size, mode, name = line.split("\t", 3)
            assert name not in rows
            rows[name] = expected, int(size), int(mode, 8)
        assert len(rows) == args.rows
        assert set(rows) == set(names) - set(manifests)
        for member in members:
            if member.name == manifests[0]:
                continue
            value = bundle.extractfile(member).read()
            assert rows[member.name] == (
                hashlib.sha256(value).hexdigest(),
                len(value),
                member.mode & 0o777,
            )
        assert any(name.endswith("/owner_payload/MANIFEST.json") for name in names)
        assert any(name.endswith("/FINAL_REPORT.md") for name in names)
    print(
        f"PASS sha256={args.sha256} bytes={args.bytes} "
        f"regular_members={args.members} manifest_rows={args.rows} gzip_crc=PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
