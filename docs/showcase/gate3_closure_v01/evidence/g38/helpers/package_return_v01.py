#!/usr/bin/env python3
"""Build and reopen-verify the complete regular-file G38 return archive."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


COMMIT = "71e166ccb88b024fd3ca3a25e17da110c6db1a3f"
BASE = "d199199a578c078c913a2381f595549175bd9235"
TREE = "71e0438a4ef8532a3047a6e87061240d5b958a31"


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def _put(files: dict[str, tuple[bytes, int]], name: str, path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError("package source is not a regular file: " + str(path))
    if name in files or not _safe(name):
        raise ValueError("duplicate or unsafe package name: " + name)
    files[name] = path.read_bytes(), path.stat().st_mode & 0o777


def _tree(
    files: dict[str, tuple[bytes, int]],
    root_name: str,
    source: Path,
    *,
    exclude_archives: bool = False,
) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink in package source: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if any(part in {".git", ".venv", "__pycache__", ".pytest_cache"} for part in relative.parts):
            continue
        if exclude_archives and path.name.endswith((".tar.gz", ".zip")):
            continue
        _put(files, f"{root_name}/{relative}", path)


def _add(bundle: tarfile.TarFile, name: str, value: bytes, mode: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    bundle.addfile(info, io.BytesIO(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--reviewed-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    command_results = {}
    for directory in sorted((args.evidence / "commands").glob("[0-9][0-9][0-9][0-9]_*")):
        receipt_path = directory / "receipt.json"
        if not receipt_path.is_file():
            if not directory.name.endswith("_package_verified_return"):
                raise ValueError("unexpected incomplete command: " + directory.name)
            continue
        receipt = json.loads(receipt_path.read_text())
        if receipt["rc"] != 0:
            raise ValueError("failed command cannot enter final package")
        command_results[directory.name] = {
            "elapsed_seconds": receipt["elapsed_seconds"],
            "rc": receipt["rc"],
            "stderr_sha256": receipt["stderr"]["sha256"],
            "stdout_sha256": receipt["stdout"]["sha256"],
        }
    if len(command_results) != 6:
        raise ValueError("final completed command count mismatch")
    finality = {
        "all_six_prepackage_commands_final": True,
        "command_results": command_results,
        "owner_execution_finalizers_complete": True,
        "status": "PASS",
    }
    (args.evidence / "final/PROCESS_AND_COMMAND_FINALITY.json").write_text(
        json.dumps(finality, indent=2, sort_keys=True) + "\n"
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = f"RADIOLARIA_GATE3_G38_OWNER_LANDING_RETURN_{stamp}"
    archive = args.output_dir / (root + ".tar.gz")
    if archive.exists():
        raise ValueError("return archive already exists")
    files: dict[str, tuple[bytes, int]] = {}

    _tree(files, f"{root}/final", args.evidence / "final")
    _tree(files, f"{root}/input_kit", args.evidence / "input_kit")
    _tree(files, f"{root}/historical_recovery", args.evidence / "historical_recovery")
    _tree(files, f"{root}/helpers", args.evidence / "helpers")

    for directory in sorted((args.evidence / "commands").glob("[0-9][0-9][0-9][0-9]_*")):
        if (directory / "receipt.json").is_file():
            _tree(files, f"{root}/commands/{directory.name}", directory)
    _tree(
        files,
        f"{root}/owner_execution",
        args.evidence / "owner_execution",
        exclude_archives=True,
    )
    for name in ("OWNER_PREFLIGHT.json", "G37R_INPUT_VERIFICATION.json"):
        _put(files, f"{root}/{name}", args.evidence / name)

    _put(
        files,
        f"{root}/reviewed_input/owner_landing/g38_owner_landing.py",
        args.reviewed_root / "owner_landing/g38_owner_landing.py",
    )
    payload = args.reviewed_root / "owner_payload"
    for name in (
        "MANIFEST.json",
        "cumulative_d199_to_g37r.patch",
        "incremental_g37_to_g37r.patch",
    ):
        _put(files, f"{root}/reviewed_input/owner_payload/{name}", payload / name)
    _tree(
        files,
        f"{root}/reviewed_input/owner_payload/postimages",
        payload / "postimages",
    )

    inherited = {
        "COST_INTERPRETATION.md": args.reviewed_root / "COST_INTERPRETATION.md",
        "FINAL_SOURCE_LEDGER.json": args.reviewed_root / "FINAL_SOURCE_LEDGER.json",
        "HISTORICAL_HELPER_CUSTODY.json": args.reviewed_root / "HISTORICAL_HELPER_CUSTODY.json",
        "RECORDED_AND_FRESH_COVERAGE.md": args.reviewed_root / "RECORDED_AND_FRESH_COVERAGE.md",
        "SOURCE_IMPACT_BRIDGE.json": args.reviewed_root / "SOURCE_IMPACT_BRIDGE.json",
        "G37_COVERAGE_AND_DOD_MAP.md": args.reviewed_root / "retained_g37/top_level/COVERAGE_AND_DOD_MAP.md",
        "G37_SUPPLIED_VALIDATION_RESULT.json": args.reviewed_root / "supplied_validation_final/RESULT.json",
        "G37R_FOCUSED_TEST_PHASES.jsonl": args.reviewed_root / "focused_test_phases_final.jsonl",
    }
    for name, path in inherited.items():
        _put(files, f"{root}/inherited_g37r/{name}", path)

    metadata = {
        "base": BASE,
        "commit": COMMIT,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "gate3_status": "PENDING_INDEPENDENT_CLOSURE_REVIEW",
        "normal_push": "PASS",
        "remote_readback": "PASS",
        "result": "G38_OWNER_LANDING_COMPLETE_FOR_INDEPENDENT_CLOSURE_REVIEW",
        "tree": TREE,
    }
    files[f"{root}/PACKAGE_METADATA.json"] = (
        (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode(),
        0o644,
    )

    manifest_name = f"{root}/MANIFEST.tsv"
    manifest = b"".join(
        f"{_sha(value)}\t{len(value)}\t{mode:o}\t{name}\n".encode()
        for name, (value, mode) in sorted(files.items())
    )
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as bundle:
        for name, (value, mode) in sorted(files.items()):
            _add(bundle, name, value, mode)
        _add(bundle, manifest_name, manifest, 0o644)

    with gzip.open(archive, "rb") as stream:
        while stream.read(1024 * 1024):
            pass
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or any(not member.isfile() or not _safe(member.name) for member in members):
            raise ValueError("unsafe, duplicate or non-regular return member")
        if set(names) != set(files) | {manifest_name}:
            raise ValueError("return archive coverage mismatch")
        parsed = {}
        for line in bundle.extractfile(manifest_name).read().decode().splitlines():
            expected, size, mode, name = line.split("\t", 3)
            if name in parsed:
                raise ValueError("duplicate return manifest row")
            parsed[name] = expected, int(size), int(mode, 8)
        if set(parsed) != set(files):
            raise ValueError("return manifest coverage mismatch")
        for member in members:
            if member.name == manifest_name:
                continue
            value = bundle.extractfile(member).read()
            if parsed[member.name] != (_sha(value), len(value), member.mode & 0o777):
                raise ValueError("return member identity mismatch: " + member.name)

    raw = archive.read_bytes()
    result = {
        "archive": str(archive),
        "bytes": len(raw),
        "gzip_crc": "PASS",
        "manifest_rows": len(files),
        "regular_members": len(files) + 1,
        "reopen": "PASS",
        "safe_unique_paths": True,
        "sha256": _sha(raw),
    }
    (args.evidence / "RETURN_ARCHIVE.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
