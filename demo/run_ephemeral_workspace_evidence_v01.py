"""Export frozen EWS3R2 evidence or independently replay a saved safe directory.

No Workspace, provider, Host or device operation is part of either command.
An expected publication ID must be supplied explicitly for anchored replay.
Archives are deliberately unsupported; extract and independently verify the
review archive before passing its public_safe_package directory.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys

from hedgehog.domains.ephemeral_workspace.sealed_evidence_v01 import (
    export_package,
    verify_package,
)


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export", help="Project a verified frozen input return")
    export.add_argument("--input-root", required=True, type=Path)
    export.add_argument("--output-dir", required=True, type=Path)
    export.add_argument("--execution-head", required=True)
    export.add_argument("--source-ledger", required=True, type=Path)
    export.add_argument("--expected-input-manifest-sha256")
    export.add_argument("--supplemental-proof-root", required=True, type=Path)
    export.add_argument("--expected-supplemental-manifest-sha256", required=True)
    replay = commands.add_parser("replay", help="Independently reopen a safe package directory")
    replay.add_argument("--package-dir", required=True, type=Path)
    replay.add_argument("--publication", type=Path)
    replay.add_argument("--expected-anchor", help="Publication ID supplied outside the checked package")
    replay.add_argument("--require-anchor", action="store_true")
    replay.add_argument("--report", type=Path, help="Create a new verification report outside the package")
    return parser


def _write_report(path, data, package_directory):
    # A report is the only optional replay write; never mutate the checked package.
    absolute = path.absolute()
    package = package_directory.resolve()
    if absolute.resolve().is_relative_to(package):
        raise ValueError("ews4_report_inside_package")
    for parent in (absolute.parent, *absolute.parents):
        if parent.is_symlink():
            raise ValueError("ews4_report_symlink_path")
    if not absolute.parent.is_dir():
        raise ValueError("ews4_report_parent_missing")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)


def main(argv=None):
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "export":
            result = export_package(
                arguments.input_root,
                arguments.output_dir,
                execution_head=arguments.execution_head,
                source_ledger_path=arguments.source_ledger,
                expected_input_manifest_sha256=arguments.expected_input_manifest_sha256,
                supplemental_proof_root=arguments.supplemental_proof_root,
                expected_supplemental_manifest_sha256=arguments.expected_supplemental_manifest_sha256,
            )
        else:
            result = verify_package(
                arguments.package_dir,
                publication_path=arguments.publication,
                expected_anchor=arguments.expected_anchor,
                require_anchor=arguments.require_anchor,
            )
        encoded = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")
        if arguments.command == "replay" and arguments.report is not None:
            _write_report(arguments.report, encoded, arguments.package_dir)
        sys.stdout.buffer.write(encoded)
        failed = result.get("status") not in {
            "PASS", "SELF_CONSISTENT_UNANCHORED", "ANCHORED_PASS"
        }
        if arguments.command == "replay" and (
            arguments.require_anchor or arguments.expected_anchor is not None
        ):
            failed = failed or result.get("status") != "ANCHORED_PASS"
        return 1 if failed else 0
    except (ValueError, OSError) as error:
        reason = str(error)
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", reason):
            reason = "ews4_filesystem_error" if isinstance(error, OSError) else "ews4_verification_rejected"
        result = {"status": "FAIL_CLOSED", "errors": [reason]}
        sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
