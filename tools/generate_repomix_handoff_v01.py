"""Deterministic, local-only Repomix handoff generation for R-H1C.

``repomix.handoff.config.json`` is a Hedgehog repository manifest, not a
native Repomix auto-discovery configuration. Native configurations are created
only inside a transactional ``_audit_exports`` directory during generation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / "repomix.handoff.config.json"
GENERATOR_PATH = Path(__file__).resolve()

READ_ONLY_GIT_SUBCOMMANDS = frozenset(
    {"rev-parse", "status", "ls-files", "check-ignore"}
)
MUTATING_GIT_SUBCOMMANDS = frozenset(
    {
        "add",
        "commit",
        "push",
        "pull",
        "checkout",
        "switch",
        "merge",
        "rebase",
        "reset",
        "clean",
        "restore",
        "tag",
        "fetch",
    }
)
HANDOFF_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")

TOP_LEVEL_KEYS = (
    "schema_version",
    "config_role",
    "generated_output_root",
    "repository_policy",
    "repomix_policy",
    "output_order",
    "profile_order",
    "global_exclude_patterns",
    "external_companion_documents",
    "profiles",
    "r_h1_artifact_mappings",
    "planned_artifact_obligations",
    "checksum_policy",
)
OUTPUT_ORDER = (
    "00_head_and_origin.txt",
    "00_repo_governance_and_metadata.md",
    "01_hedgehog_kernel_and_contracts.md",
    "02_docs_specs_checkpoints_and_roadmaps.md",
    "03_demo_runners_and_fixtures.md",
    "04_tests_and_test_fixtures.md",
    "05_audit_logs_and_public_safe_evidence.md",
    "06_current_g2a_g2b_focus.md",
    "07_passport_release_and_root_contract_data.md",
    "SHA256SUMS",
)
PROFILE_ORDER = (
    "00_repo_governance_and_metadata",
    "01_hedgehog_kernel_and_contracts",
    "02_docs_specs_checkpoints_and_roadmaps",
    "03_demo_runners_and_fixtures",
    "04_tests_and_test_fixtures",
    "05_audit_logs_and_public_safe_evidence",
    "06_current_g2a_g2b_focus",
    "07_passport_release_and_root_contract_data",
)
GLOBAL_EXCLUDE_PATTERNS = (
    ".git/**",
    ".venv/**",
    "venv/**",
    ".tmp/**",
    "_audit_exports/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    ".pytest_cache/**",
    ".mypy_cache/**",
    ".ruff_cache/**",
    "htmlcov/**",
    ".coverage",
    "coverage.xml",
    "node_modules/**",
    "dist/**",
    "build/**",
    ".DS_Store",
    ".idea/**",
    ".vscode/**",
    ".codex/**",
    "repomix-output.*",
    "config.py",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "logs/**",
    "data/logs/**",
    "data/drs/**/*.json",
    "credentials/**",
    "secrets/**",
    ".secrets/**",
    "private_keys/**",
    "signing_material/**",
    "provider_raw_outputs/**",
    "**/*.pem",
    "**/*.key",
    "**/*.p12",
    "**/*.pfx",
    "**/*.sqlite",
    "**/*.sqlite3",
    "**/*.db",
    "**/*.pptx",
    "**/*.pdf",
    "**/*.png",
    "**/*.jpg",
    "**/*.jpeg",
    "**/*.gif",
    "**/*.webp",
    "**/*.zip",
    "**/*.tar",
    "**/*.gz",
    "**/*.7z",
)
NON_AUDIT_PROFILE_LOCAL_EXCLUDE_PATTERNS = ("**/*.log",)
PROFILE_INCLUDES = {
    "00_repo_governance_and_metadata": (
        ".gitignore",
        ".gitattributes",
        "AGENTS.md",
        "README*",
        "LICENSE*",
        "COMMERCIAL-LICENSING.md",
        "CHANGELOG*",
        "CONTRIBUTING*",
        "SECURITY*",
        "*.toml",
        "requirements*.txt",
        "pytest.ini",
        "setup.cfg",
        "setup.py",
        "tox.ini",
        "Makefile",
        "Dockerfile*",
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        ".github/**",
        "scripts/**",
        "tools/**",
        "repomix.handoff.config.json",
        "docs/repomix_handoff_reproducibility_v01.md",
    ),
    "01_hedgehog_kernel_and_contracts": (
        "hedgehog/**",
        "schemas/**",
        "contracts/**",
    ),
    "02_docs_specs_checkpoints_and_roadmaps": (
        "docs/**/*.md",
        "docs/**/*.txt",
        "docs/**/*.yaml",
        "docs/**/*.yml",
    ),
    "03_demo_runners_and_fixtures": ("demo/**",),
    "04_tests_and_test_fixtures": ("tests/**",),
    "05_audit_logs_and_public_safe_evidence": (
        "docs/audit_reports/**",
        "docs/evidence/**",
    ),
    "06_current_g2a_g2b_focus": (
        "AGENTS.md",
        "docs/**/*g2_a*",
        "docs/**/*g2_b*",
        "docs/**/*g2-a*",
        "docs/**/*g2-b*",
        "docs/**/*action_commit_packet*",
        "docs/**/*semantic_address*",
        "docs/**/*reuse_certificate*",
        "hedgehog/kernel/**",
        "demo/**/*g2_a*",
        "demo/**/*g2_b*",
        "demo/**/*g2-a*",
        "demo/**/*g2-b*",
        "demo/run_living_gauntlet_v01.py",
        "demo/run_kernel_conformance_v01.py",
        "tests/**/*g2_a*",
        "tests/**/*g2_b*",
        "tests/**/*g2-a*",
        "tests/**/*g2-b*",
        "tests/test_living_gauntlet_v01_runner.py",
        "tests/test_kernel_conformance_v01_runner.py",
    ),
    "07_passport_release_and_root_contract_data": (
        "specs/**",
        "release/**",
        "policies/**",
        "needles/**",
        "fixtures/**",
    ),
}
PROFILE_OUTPUTS = dict(zip(PROFILE_ORDER, OUTPUT_ORDER[1:9], strict=True))
EXTERNAL_COMPANION_DOCUMENTS = (
    "hedgehog_deeptech_completion_roadmap_v3_1_gate_based_guardian.md",
    "hedgehog_deeptech_completion_master_roadmap_v2_1.md",
)
R_H1_AUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log"
)
R_H1_CHECKPOINT_PATH = (
    "docs/clean_clone_licensing_release_spine_reconciliation_r_h1_"
    "checkpoint_v01.md"
)
R_H1_ARTIFACT_MAPPINGS = (
    ("AGENTS.md", (PROFILE_ORDER[0], PROFILE_ORDER[6])),
    ("README.md", (PROFILE_ORDER[0],)),
    ("pyproject.toml", (PROFILE_ORDER[0],)),
    ("LICENSE", (PROFILE_ORDER[0],)),
    ("COMMERCIAL-LICENSING.md", (PROFILE_ORDER[0],)),
    ("repomix.handoff.config.json", (PROFILE_ORDER[0],)),
    ("tools/generate_repomix_handoff_v01.py", (PROFILE_ORDER[0],)),
    (
        "docs/repomix_handoff_reproducibility_v01.md",
        (PROFILE_ORDER[0], PROFILE_ORDER[2]),
    ),
    (
        "docs/clean_clone_licensing_release_spine_reconciliation_r_h1_"
        "preflight_v01.md",
        (PROFILE_ORDER[2],),
    ),
    (R_H1_CHECKPOINT_PATH, (PROFILE_ORDER[2],)),
    ("tests/test_repository_maintenance_contract_v01.py", (PROFILE_ORDER[4],)),
    ("tests/test_repository_release_spine_v01.py", (PROFILE_ORDER[4],)),
    (
        "tests/test_repomix_handoff_reproducibility_v01.py",
        (PROFILE_ORDER[4],),
    ),
    (R_H1_AUDIT_PATH, (PROFILE_ORDER[5],)),
    ("specs/machine_manifest_v0_25.json", (PROFILE_ORDER[7],)),
    ("release/current_status_overlay_v01.json", (PROFILE_ORDER[7],)),
    ("release/claim_to_evidence_index.md", (PROFILE_ORDER[7],)),
    ("release/integration_seam_index.md", (PROFILE_ORDER[7],)),
    ("release/one_command_gauntlet.md", (PROFILE_ORDER[7],)),
    ("release/current_limitations.md", (PROFILE_ORDER[7],)),
    ("release/current_release_notes.md", (PROFILE_ORDER[7],)),
    ("release/completion_manifest.json", (PROFILE_ORDER[7],)),
    ("release/integration_seam_index.json", (PROFILE_ORDER[7],)),
)
HEAD_FIELD_ORDER = (
    "HANDOFF_SCHEMA_VERSION",
    "BRANCH",
    "HEAD",
    "ORIGIN_MAIN",
    "HEAD_EQUALS_ORIGIN_MAIN",
    "WORKTREE_CLEAN",
    "REPOMIX_VERSION",
    "CONFIG_SHA256",
    "GENERATOR_SHA256",
    "PROFILE_ORDER",
    "OUTPUT_ORDER",
    "EXTERNAL_COMPANION_DOCUMENT_1",
    "EXTERNAL_COMPANION_DOCUMENT_2",
    "EXTERNAL_COMPANION_CUSTODY",
    "EXTERNAL_COMPANION_GENERATOR_ACTION",
)


class HandoffError(RuntimeError):
    """A fail-closed handoff contract violation."""


@dataclass(frozen=True)
class RepositoryIdentity:
    branch: str
    head: str
    origin_main: str
    dirty_entries: tuple[str, ...]
    staging_empty: bool

    @property
    def head_equals_origin_main(self) -> bool:
        return self.head == self.origin_main

    @property
    def worktree_clean(self) -> bool:
        return not self.dirty_entries


@dataclass(frozen=True)
class RepomixDiscovery:
    available: bool
    executable: str | None
    version: str
    reason: str


ProfileRunner = Callable[[Mapping[str, object], Path, Path, str], None]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_command(
    arguments: Sequence[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        tuple(arguments),
        cwd=cwd,
        check=False,
        capture_output=True,
        shell=False,
    )


def run_git(
    subcommand: str,
    *arguments: str,
    repository_root: Path = REPOSITORY_ROOT,
) -> subprocess.CompletedProcess[bytes]:
    if subcommand not in READ_ONLY_GIT_SUBCOMMANDS:
        raise HandoffError(f"Git subcommand is not read-only allowlisted: {subcommand}")
    return _run_command(("git", subcommand, *arguments), cwd=repository_root)


def _decode_output(completed: subprocess.CompletedProcess[bytes], label: str) -> str:
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise HandoffError(f"{label} failed with exit {completed.returncode}: {stderr}")
    return completed.stdout.decode("utf-8").strip()


def load_config(path: Path = CONFIG_PATH) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HandoffError(f"Cannot load handoff manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HandoffError("Handoff manifest top level must be an object")
    return value


def _require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise HandoffError(f"Invalid {label}: expected {expected!r}, got {actual!r}")


def _safe_relative_path(value: str, label: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value in {"", "."}:
        raise HandoffError(f"Unsafe {label}: {value!r}")


def _pattern_matches(path: str, pattern: str) -> bool:
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if "/**/" in pattern:
        return fnmatch.fnmatchcase(path, pattern.replace("/**/", "/"))
    return False


def effective_profile_exclude_patterns(
    profile: Mapping[str, object],
    config: Mapping[str, object],
) -> tuple[str, ...]:
    global_patterns = tuple(config["global_exclude_patterns"])
    allows_logs = profile["allows_committed_log_suffix"]
    if allows_logs is True:
        return global_patterns
    if allows_logs is False:
        return global_patterns + NON_AUDIT_PROFILE_LOCAL_EXCLUDE_PATTERNS
    raise HandoffError("allows_committed_log_suffix must be a boolean")


def validate_config(config: Mapping[str, object]) -> None:
    _require_equal(tuple(config), TOP_LEVEL_KEYS, "top-level key order")
    _require_equal(config["schema_version"], "v0.1", "schema_version")
    _require_equal(
        config["config_role"],
        "hedgehog_repository_owned_repomix_handoff_manifest",
        "config_role",
    )
    _require_equal(config["generated_output_root"], "_audit_exports", "output root")
    _require_equal(
        config["repository_policy"],
        {
            "require_git_checkout": True,
            "require_clean_worktree_for_generation": True,
            "require_head_equals_origin_main_for_generation": True,
            "allow_dirty_diagnostic_only": True,
            "generated_outputs_tracked": False,
            "network_allowed": False,
            "installation_allowed": False,
            "stage_commit_push_allowed": False,
            "writes_outside_generated_output_root_allowed": False,
        },
        "repository_policy",
    )
    _require_equal(
        config["repomix_policy"],
        {
            "binary_default": "repomix",
            "style": "markdown",
            "file_path_style": "cwd-relative",
            "parsable_style": False,
            "compress": False,
            "file_summary": True,
            "directory_structure": True,
            "files": True,
            "remove_comments": False,
            "remove_empty_lines": False,
            "show_line_numbers": False,
            "copy_to_clipboard": False,
            "include_empty_directories": False,
            "include_full_directory_structure": False,
            "git_sort_by_changes": False,
            "git_include_diffs": False,
            "git_include_logs": False,
            "security_check": True,
            "use_gitignore": True,
            "use_dot_ignore": True,
            "use_default_patterns": True,
            "token_count_encoding": "o200k_base",
            "capture_version": True,
            "exact_version_required_for_byte_reproduction": True,
            "remote_mode_allowed": False,
            "installation_allowed": False,
            "npx_allowed": False,
        },
        "repomix_policy",
    )
    _require_equal(tuple(config["output_order"]), OUTPUT_ORDER, "output_order")
    _require_equal(tuple(config["profile_order"]), PROFILE_ORDER, "profile_order")
    _require_equal(
        tuple(config["global_exclude_patterns"]),
        GLOBAL_EXCLUDE_PATTERNS,
        "global_exclude_patterns",
    )
    if "**/*.log" in config["global_exclude_patterns"]:
        raise HandoffError("A global recursive .log exclusion is prohibited")
    for unsafe in ("**/*secret*", "**/*credential*"):
        if unsafe in config["global_exclude_patterns"]:
            raise HandoffError(f"Broad name-based exclusion is prohibited: {unsafe}")

    companions = config["external_companion_documents"]
    _require_equal(
        companions,
        [
            {
                "document_name": EXTERNAL_COMPANION_DOCUMENTS[0],
                "custody": "OWNER_SUPPLIED_EXTERNAL",
                "generator_action": "DO_NOT_FABRICATE",
            },
            {
                "document_name": EXTERNAL_COMPANION_DOCUMENTS[1],
                "custody": "OWNER_SUPPLIED_EXTERNAL",
                "generator_action": "DO_NOT_FABRICATE",
            },
        ],
        "external_companion_documents",
    )

    profiles = config["profiles"]
    if not isinstance(profiles, list):
        raise HandoffError("profiles must be an array")
    _require_equal(
        tuple(profile["profile_id"] for profile in profiles),
        PROFILE_ORDER,
        "profile array order",
    )
    for profile in profiles:
        _require_equal(
            tuple(profile),
            (
                "profile_id",
                "output_name",
                "include_patterns",
                "public_safe_audit_profile",
                "allows_committed_log_suffix",
            ),
            f"profile keys for {profile.get('profile_id')}",
        )
        profile_id = profile["profile_id"]
        _require_equal(
            profile["output_name"], PROFILE_OUTPUTS[profile_id], f"output for {profile_id}"
        )
        _require_equal(
            tuple(profile["include_patterns"]),
            PROFILE_INCLUDES[profile_id],
            f"include patterns for {profile_id}",
        )
        is_audit = profile_id == "05_audit_logs_and_public_safe_evidence"
        _require_equal(
            profile["public_safe_audit_profile"], is_audit, f"audit role for {profile_id}"
        )
        _require_equal(
            profile["allows_committed_log_suffix"], is_audit, f"log role for {profile_id}"
        )
        if "docs/**" in profile["include_patterns"]:
            raise HandoffError("The exact broad docs/** include is prohibited")

    mappings = config["r_h1_artifact_mappings"]
    _require_equal(
        tuple(
            (mapping["path"], tuple(mapping["profile_ids"]))
            for mapping in mappings
        ),
        R_H1_ARTIFACT_MAPPINGS,
        "R-H1 artifact mappings",
    )
    for mapping in mappings:
        _require_equal(
            tuple(mapping), ("path", "profile_ids", "required_when_present"),
            f"mapping keys for {mapping.get('path')}",
        )
        _require_equal(mapping["required_when_present"], True, "mapping requirement")
        _safe_relative_path(mapping["path"], "mapped artifact path")
        for profile_id in mapping["profile_ids"]:
            if profile_id not in PROFILE_ORDER:
                raise HandoffError(f"Unknown mapped profile: {profile_id}")
            if not any(
                _pattern_matches(mapping["path"], pattern)
                for pattern in PROFILE_INCLUDES[profile_id]
            ):
                raise HandoffError(
                    f"Mapped path {mapping['path']} is not covered by {profile_id}"
                )

    _require_equal(
        config["planned_artifact_obligations"],
        [
            {
                "path": R_H1_AUDIT_PATH,
                "owner_slice": "R-H1D1",
                "profile_id": PROFILE_ORDER[5],
                "current_status": "NOT_YET_PRESENT",
                "required_when_present": True,
                "required_after_r_h1_closure": True,
            },
            {
                "path": R_H1_CHECKPOINT_PATH,
                "owner_slice": "R-H1D2",
                "profile_id": PROFILE_ORDER[2],
                "current_status": "NOT_YET_PRESENT",
                "required_when_present": True,
                "required_after_r_h1_closure": True,
            },
        ],
        "planned artifact obligations",
    )
    _require_equal(
        config["checksum_policy"],
        {
            "algorithm": "sha256",
            "output_name": "SHA256SUMS",
            "entry_format": "{sha256}  {filename}\n",
            "include_checksum_file_itself": False,
            "ordered_inputs": list(OUTPUT_ORDER[:-1]),
        },
        "checksum_policy",
    )
    if len(set(OUTPUT_ORDER)) != len(OUTPUT_ORDER):
        raise HandoffError("Duplicate output name")
    for output_name in OUTPUT_ORDER:
        _safe_relative_path(output_name, "output name")
        if len(Path(output_name).parts) != 1:
            raise HandoffError(f"Output must be a filename: {output_name}")


def repository_python_inventory(
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[str, ...]:
    completed = run_git(
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        repository_root=repository_root,
    )
    if completed.returncode != 0:
        raise HandoffError("Unable to inventory cached and untracked repository paths")
    return tuple(
        path.decode("utf-8")
        for path in completed.stdout.split(b"\0")
        if path
    )


def validate_artifact_coverage(
    config: Mapping[str, object],
    repository_root: Path = REPOSITORY_ROOT,
) -> None:
    inventory = set(repository_python_inventory(repository_root))
    obligation_paths = {
        obligation["path"] for obligation in config["planned_artifact_obligations"]
    }
    mappings = {mapping["path"]: mapping for mapping in config["r_h1_artifact_mappings"]}
    for path, _profile_ids in R_H1_ARTIFACT_MAPPINGS:
        if path not in inventory and path not in obligation_paths:
            raise HandoffError(f"Required current R-H1 artifact is missing: {path}")
    for obligation in config["planned_artifact_obligations"]:
        path = obligation["path"]
        mapping = mappings.get(path)
        if mapping is None or obligation["profile_id"] not in mapping["profile_ids"]:
            raise HandoffError(f"Planned artifact lacks required profile mapping: {path}")
        if path in inventory and not mapping["required_when_present"]:
            raise HandoffError(f"Present planned artifact is not mandatory: {path}")


def validate_generated_output_git_policy(
    config: Mapping[str, object],
    repository_root: Path = REPOSITORY_ROOT,
) -> None:
    output_root = config["generated_output_root"]
    ignored = run_git(
        "check-ignore",
        "-q",
        f"{output_root}/example",
        repository_root=repository_root,
    )
    if ignored.returncode != 0:
        raise HandoffError(f"Generated output root is not ignored: {output_root}")
    tracked = run_git(
        "ls-files", "-z", "--", output_root, repository_root=repository_root
    )
    if tracked.returncode != 0 or tracked.stdout:
        raise HandoffError(f"Generated output root contains tracked paths: {output_root}")


def collect_repository_identity(
    repository_root: Path = REPOSITORY_ROOT,
) -> RepositoryIdentity:
    branch = _decode_output(
        run_git("rev-parse", "--abbrev-ref", "HEAD", repository_root=repository_root),
        "branch discovery",
    )
    head = _decode_output(
        run_git("rev-parse", "HEAD", repository_root=repository_root), "HEAD discovery"
    )
    origin_main = _decode_output(
        run_git("rev-parse", "origin/main", repository_root=repository_root),
        "origin/main discovery",
    )
    status = run_git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        repository_root=repository_root,
    )
    if status.returncode != 0:
        raise HandoffError("Unable to collect Git porcelain status")
    entries = tuple(
        line.decode("utf-8", errors="strict")
        for line in status.stdout.splitlines()
        if line
    )
    staging_empty = all(line.startswith("??") or line.startswith(" ") for line in entries)
    return RepositoryIdentity(branch, head, origin_main, entries, staging_empty)


def validate_repository_state(
    identity: RepositoryIdentity,
    *,
    mode: str,
    allow_dirty_diagnostic: bool = False,
) -> None:
    if not identity.branch or identity.branch == "HEAD":
        raise HandoffError("A named Git branch is required")
    if mode not in {"dry-run", "generate", "verify"}:
        raise HandoffError(f"Unknown mode: {mode}")
    if allow_dirty_diagnostic and mode != "dry-run":
        raise HandoffError("--allow-dirty-diagnostic is valid only with --dry-run")
    if not identity.worktree_clean and not allow_dirty_diagnostic:
        raise HandoffError("Worktree must be clean")
    if mode in {"generate", "verify"} and not identity.staging_empty:
        raise HandoffError("Staging must be empty")
    if mode == "generate" and not identity.head_equals_origin_main:
        raise HandoffError("HEAD must equal origin/main for generation")


def discover_repomix(binary: str, repository_root: Path = REPOSITORY_ROOT) -> RepomixDiscovery:
    candidate: str | None
    if os.sep in binary or (os.altsep and os.altsep in binary):
        path = Path(binary).expanduser()
        candidate = str(path) if path.is_file() and os.access(path, os.X_OK) else None
    else:
        candidate = shutil.which(binary)
    if candidate is None:
        return RepomixDiscovery(False, None, "UNAVAILABLE", f"not found: {binary}")
    try:
        completed = _run_command((candidate, "--version"), cwd=repository_root)
    except OSError as exc:
        return RepomixDiscovery(False, None, "UNAVAILABLE", str(exc))
    if completed.returncode != 0:
        reason = completed.stderr.decode("utf-8", errors="replace").strip()
        return RepomixDiscovery(False, None, "UNAVAILABLE", reason or "--version failed")
    version = completed.stdout.decode("utf-8", errors="strict").strip()
    if not version or "\n" in version or "\r" in version:
        return RepomixDiscovery(False, None, "UNAVAILABLE", "version must be one line")
    return RepomixDiscovery(True, candidate, version, "available")


def build_output_plan(config: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    profiles = config["profiles"]
    return tuple((profile["profile_id"], profile["output_name"]) for profile in profiles)


def build_native_repomix_config(
    profile: Mapping[str, object],
    output_path: str,
    config: Mapping[str, object],
) -> dict[str, object]:
    _safe_relative_path(output_path, "transactional Repomix output path")
    policy = config["repomix_policy"]
    return {
        "input": {"maxFileSize": 50000000},
        "output": {
            "filePath": output_path,
            "style": policy["style"],
            "filePathStyle": policy["file_path_style"],
            "parsableStyle": policy["parsable_style"],
            "compress": policy["compress"],
            "headerText": None,
            "instructionFilePath": None,
            "fileSummary": policy["file_summary"],
            "directoryStructure": policy["directory_structure"],
            "files": policy["files"],
            "removeComments": policy["remove_comments"],
            "removeEmptyLines": policy["remove_empty_lines"],
            "showLineNumbers": policy["show_line_numbers"],
            "copyToClipboard": policy["copy_to_clipboard"],
            "includeEmptyDirectories": policy["include_empty_directories"],
            "includeFullDirectoryStructure": policy["include_full_directory_structure"],
            "git": {
                "sortByChanges": policy["git_sort_by_changes"],
                "sortByChangesMaxCommits": 100,
                "includeDiffs": policy["git_include_diffs"],
                "includeLogs": policy["git_include_logs"],
                "includeLogsCount": 50,
            },
        },
        "include": list(profile["include_patterns"]),
        "ignore": {
            "useGitignore": policy["use_gitignore"],
            "useDotIgnore": policy["use_dot_ignore"],
            "useDefaultPatterns": policy["use_default_patterns"],
            "customPatterns": list(
                effective_profile_exclude_patterns(profile, config)
            ),
        },
        "security": {"enableSecurityCheck": policy["security_check"]},
        "tokenCount": {"encoding": policy["token_count_encoding"]},
    }


def _head_and_origin_bytes(
    identity: RepositoryIdentity,
    config: Mapping[str, object],
    repomix_version: str,
    *,
    config_path: Path = CONFIG_PATH,
    generator_path: Path = GENERATOR_PATH,
) -> bytes:
    values = {
        "HANDOFF_SCHEMA_VERSION": config["schema_version"],
        "BRANCH": identity.branch,
        "HEAD": identity.head,
        "ORIGIN_MAIN": identity.origin_main,
        "HEAD_EQUALS_ORIGIN_MAIN": str(identity.head_equals_origin_main).lower(),
        "WORKTREE_CLEAN": str(identity.worktree_clean).lower(),
        "REPOMIX_VERSION": repomix_version,
        "CONFIG_SHA256": _sha256(config_path),
        "GENERATOR_SHA256": _sha256(generator_path),
        "PROFILE_ORDER": ",".join(config["profile_order"]),
        "OUTPUT_ORDER": ",".join(config["output_order"]),
        "EXTERNAL_COMPANION_DOCUMENT_1": EXTERNAL_COMPANION_DOCUMENTS[0],
        "EXTERNAL_COMPANION_DOCUMENT_2": EXTERNAL_COMPANION_DOCUMENTS[1],
        "EXTERNAL_COMPANION_CUSTODY": "OWNER_SUPPLIED_EXTERNAL",
        "EXTERNAL_COMPANION_GENERATOR_ACTION": "DO_NOT_FABRICATE",
    }
    return "".join(f"{key}={values[key]}\n" for key in HEAD_FIELD_ORDER).encode("utf-8")


def _default_profile_runner(
    _profile: Mapping[str, object],
    native_config_path: Path,
    _output_path: Path,
    repomix_binary: str,
) -> None:
    completed = _run_command(
        (repomix_binary, "--config", str(native_config_path)),
        cwd=REPOSITORY_ROOT,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise HandoffError(f"Repomix profile generation failed: {stderr}")


def _require_directory_under_output_root(path: Path, output_root: Path) -> Path:
    if output_root.is_symlink() or path.is_symlink():
        raise HandoffError("Symlinked output roots or handoff directories are prohibited")
    resolved_root = output_root.resolve()
    resolved_path = path.resolve()
    if resolved_path.parent != resolved_root:
        raise HandoffError("Handoff directory must be a direct child of _audit_exports")
    return resolved_path


def _verify_exact_files(directory: Path, expected_names: Sequence[str]) -> None:
    if not directory.is_dir() or directory.is_symlink():
        raise HandoffError(f"Handoff path is not a real directory: {directory}")
    children = tuple(directory.iterdir())
    if any(child.is_symlink() or not child.is_file() for child in children):
        raise HandoffError("Handoff directory contains a symlink or non-file entry")
    names = tuple(sorted(child.name for child in children))
    if names != tuple(sorted(expected_names)):
        raise HandoffError(
            f"Handoff output set mismatch: expected {sorted(expected_names)}, got {list(names)}"
        )


def create_sha256sums(directory: Path, config: Mapping[str, object]) -> Path:
    policy = config["checksum_policy"]
    lines = []
    for filename in policy["ordered_inputs"]:
        path = directory / filename
        if not path.is_file() or path.is_symlink():
            raise HandoffError(f"Cannot checksum missing or unsafe output: {filename}")
        lines.append(f"{_sha256(path)}  {filename}\n")
    output = directory / policy["output_name"]
    if output.exists():
        raise HandoffError("SHA256SUMS already exists")
    output.write_bytes("".join(lines).encode("ascii"))
    return output


def _parse_head_and_origin(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw or b"\0" in raw:
        raise HandoffError("00_head_and_origin.txt text integrity failed")
    lines = raw.decode("utf-8").splitlines()
    keys = tuple(line.partition("=")[0] for line in lines)
    if keys != HEAD_FIELD_ORDER or any("=" not in line for line in lines):
        raise HandoffError("00_head_and_origin.txt field order mismatch")
    return dict(line.split("=", 1) for line in lines)


def verify_generated_directory(
    directory: Path,
    config: Mapping[str, object],
    *,
    output_root: Path | None = None,
) -> dict[str, str]:
    root = output_root or (REPOSITORY_ROOT / config["generated_output_root"])
    resolved = _require_directory_under_output_root(directory, root)
    _verify_exact_files(resolved, config["output_order"])

    checksum_path = resolved / config["checksum_policy"]["output_name"]
    raw = checksum_path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw or b"\0" in raw:
        raise HandoffError("SHA256SUMS must be NUL/CR-free and LF-terminated")
    try:
        lines = raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise HandoffError("SHA256SUMS must be ASCII") from exc
    expected_inputs = tuple(config["checksum_policy"]["ordered_inputs"])
    if len(lines) != len(expected_inputs):
        raise HandoffError("SHA256SUMS entry count mismatch")
    for line, expected_name in zip(lines, expected_inputs, strict=True):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)\n", line)
        if match is None:
            raise HandoffError(f"Malformed checksum line: {line!r}")
        digest, filename = match.groups()
        if filename != expected_name or filename == checksum_path.name:
            raise HandoffError("SHA256SUMS ordering or self-entry violation")
        if _sha256(resolved / filename) != digest:
            raise HandoffError(f"Checksum mismatch: {filename}")

    head = _parse_head_and_origin(resolved / "00_head_and_origin.txt")
    if head["PROFILE_ORDER"] != ",".join(config["profile_order"]):
        raise HandoffError("Generated PROFILE_ORDER does not match current config")
    if head["OUTPUT_ORDER"] != ",".join(config["output_order"]):
        raise HandoffError("Generated OUTPUT_ORDER does not match current config")
    return head


def transactional_generate(
    config: Mapping[str, object],
    identity: RepositoryIdentity,
    repomix_binary: str,
    repomix_version: str,
    handoff_id: str,
    *,
    profile_runner: ProfileRunner | None = None,
    repository_root: Path = REPOSITORY_ROOT,
    output_root: Path | None = None,
    config_path: Path = CONFIG_PATH,
    generator_path: Path = GENERATOR_PATH,
) -> Path:
    if HANDOFF_ID_PATTERN.fullmatch(handoff_id) is None:
        raise HandoffError(f"Invalid handoff ID: {handoff_id!r}")
    root = output_root or (repository_root / config["generated_output_root"])
    if root.name != config["generated_output_root"] or root.is_symlink():
        raise HandoffError("Generation output root must be a real _audit_exports directory")
    final_directory = root / handoff_id
    transaction = root / f".{handoff_id}.tmp-{os.getpid()}"
    if final_directory.exists() or transaction.exists():
        raise HandoffError("Final or transactional handoff directory already exists")

    root_created = not root.exists()
    runner = profile_runner or _default_profile_runner
    try:
        root.mkdir(parents=False, exist_ok=True)
        transaction.mkdir()
        (transaction / "00_head_and_origin.txt").write_bytes(
            _head_and_origin_bytes(
                identity,
                config,
                repomix_version,
                config_path=config_path,
                generator_path=generator_path,
            )
        )
        for profile in config["profiles"]:
            output_path = transaction / profile["output_name"]
            relative_output = output_path.relative_to(repository_root).as_posix()
            native_config = build_native_repomix_config(profile, relative_output, config)
            native_path = transaction / f".repomix-{profile['profile_id']}.json"
            native_path.write_text(
                json.dumps(native_config, indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            try:
                runner(profile, native_path, output_path, repomix_binary)
            finally:
                native_path.unlink(missing_ok=True)

        _verify_exact_files(transaction, config["output_order"][:-1])
        create_sha256sums(transaction, config)
        verify_generated_directory(transaction, config, output_root=root)
        transaction.rename(final_directory)
        return final_directory
    except Exception:
        if transaction.exists() and not transaction.is_symlink():
            shutil.rmtree(transaction)
        if root_created and root.exists() and not any(root.iterdir()):
            root.rmdir()
        raise


def dry_validate(
    config: Mapping[str, object],
    *,
    repomix_binary: str,
    allow_dirty_diagnostic: bool,
    repository_root: Path = REPOSITORY_ROOT,
) -> RepomixDiscovery:
    validate_config(config)
    validate_artifact_coverage(config, repository_root)
    validate_generated_output_git_policy(config, repository_root)
    identity = collect_repository_identity(repository_root)
    validate_repository_state(
        identity,
        mode="dry-run",
        allow_dirty_diagnostic=allow_dirty_diagnostic,
    )
    discovery = discover_repomix(repomix_binary, repository_root)
    print("STATIC_VALIDATION=PASS")
    print(f"DIRTY_DIAGNOSTIC_ONLY={str(bool(allow_dirty_diagnostic)).lower()}")
    print(f"WORKTREE_CLEAN={str(identity.worktree_clean).lower()}")
    print(f"REPOMIX_AVAILABLE={str(discovery.available).lower()}")
    print(f"REAL_GENERATION_AVAILABLE={str(discovery.available and identity.worktree_clean).lower()}")
    print("GENERATION_PERFORMED=false")
    return discovery


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--generate", action="store_true")
    modes.add_argument("--verify", metavar="HANDOFF_DIRECTORY")
    parser.add_argument("--allow-dirty-diagnostic", action="store_true")
    parser.add_argument("--repomix-bin")
    parser.add_argument("--handoff-id")
    return parser


def _validate_cli_arguments(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.allow_dirty_diagnostic and not args.dry_run:
        parser.error("--allow-dirty-diagnostic is valid only with --dry-run")
    if args.handoff_id and not args.generate:
        parser.error("--handoff-id is valid only with --generate")


def main(arguments: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(arguments)
    _validate_cli_arguments(parser, args)
    try:
        config = load_config()
        validate_config(config)
        repomix_binary = args.repomix_bin or config["repomix_policy"]["binary_default"]
        if args.dry_run:
            dry_validate(
                config,
                repomix_binary=repomix_binary,
                allow_dirty_diagnostic=args.allow_dirty_diagnostic,
            )
            return 0

        validate_artifact_coverage(config)
        validate_generated_output_git_policy(config)
        identity = collect_repository_identity()
        mode = "generate" if args.generate else "verify"
        validate_repository_state(identity, mode=mode)
        if args.verify:
            verify_generated_directory(Path(args.verify), config)
            print("VERIFICATION=PASS")
            print("GENERATION_PERFORMED=false")
            return 0

        discovery = discover_repomix(repomix_binary)
        if not discovery.available or discovery.executable is None:
            raise HandoffError(f"Repomix unavailable: {discovery.reason}")
        handoff_id = args.handoff_id or f"hedgehog-handoff-{identity.head[:12]}"
        final_path = transactional_generate(
            config,
            identity,
            discovery.executable,
            discovery.version,
            handoff_id,
        )
        print("GENERATION=PASS")
        print(f"HANDOFF_DIRECTORY={final_path.relative_to(REPOSITORY_ROOT).as_posix()}")
        print("GENERATION_PERFORMED=true")
        return 0
    except HandoffError as exc:
        print(f"ERROR={exc}", file=sys.stderr)
        print("GENERATION_PERFORMED=false", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
