from __future__ import annotations

import ast
from dataclasses import replace
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / "repomix.handoff.config.json"
GENERATOR_PATH = REPOSITORY_ROOT / "tools/generate_repomix_handoff_v01.py"
DOCUMENTATION_PATH = REPOSITORY_ROOT / "docs/repomix_handoff_reproducibility_v01.md"
OUTPUT_ROOT = REPOSITORY_ROOT / "_audit_exports"

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
PROFILE_INCLUDES = {
    PROFILE_ORDER[0]: (
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
    PROFILE_ORDER[1]: ("hedgehog/**", "schemas/**", "contracts/**"),
    PROFILE_ORDER[2]: (
        "docs/**/*.md",
        "docs/**/*.txt",
        "docs/**/*.yaml",
        "docs/**/*.yml",
    ),
    PROFILE_ORDER[3]: ("demo/**",),
    PROFILE_ORDER[4]: ("tests/**",),
    PROFILE_ORDER[5]: ("docs/audit_reports/**", "docs/evidence/**"),
    PROFILE_ORDER[6]: (
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
    PROFILE_ORDER[7]: (
        "specs/**",
        "release/**",
        "policies/**",
        "needles/**",
        "fixtures/**",
    ),
}
R_H1_AUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log"
)
R_H1_CHECKPOINT_PATH = (
    "docs/clean_clone_licensing_release_spine_reconciliation_r_h1_"
    "checkpoint_v01.md"
)
G2_A_AUDIT_LOG_PATH = (
    "docs/audit_reports/"
    "auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log"
)
G2_B_AUDIT_LOG_PATH = (
    "docs/audit_reports/"
    "auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log"
)
CURRENT_R_H1C_PATHS = {
    "repomix.handoff.config.json",
    "tools/generate_repomix_handoff_v01.py",
    "docs/repomix_handoff_reproducibility_v01.md",
    "tests/test_repomix_handoff_reproducibility_v01.py",
}


def _load_generator():
    spec = importlib.util.spec_from_file_location("r_h1c_generator", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = _load_generator()


def _config() -> dict[str, object]:
    value = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _run_generator(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (sys.executable, str(GENERATOR_PATH), *arguments),
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def _git_status() -> bytes:
    return subprocess.run(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        shell=False,
    ).stdout


def _tree_snapshot(path: Path) -> tuple[tuple[str, str], ...]:
    if not path.exists():
        return ()
    return tuple(
        sorted(
            (
                item.relative_to(path).as_posix(),
                hashlib.sha256(item.read_bytes()).hexdigest()
                if item.is_file() and not item.is_symlink()
                else "NON_FILE",
            )
            for item in path.rglob("*")
        )
    )


def _identity(clean: bool = True):
    entries = () if clean else ("?? untracked",)
    return GENERATOR.RepositoryIdentity("main", "a" * 40, "a" * 40, entries, True)


def _generate_synthetic_handoff(tmp_path: Path, handoff_id: str = "valid-handoff"):
    config = _config()
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    output_root = repository_root / "_audit_exports"
    captured: list[tuple[str, dict[str, object]]] = []

    def fake_runner(profile, native_path, output_path, _binary):
        native = json.loads(native_path.read_text(encoding="utf-8"))
        captured.append((profile["profile_id"], native))
        output_path.write_text(
            f"# {profile['profile_id']}\n",
            encoding="utf-8",
            newline="\n",
        )

    final = GENERATOR.transactional_generate(
        config,
        _identity(),
        "/local/fake/repomix",
        "repomix 1.2.3",
        handoff_id,
        profile_runner=fake_runner,
        repository_root=repository_root,
        output_root=output_root,
        config_path=CONFIG_PATH,
        generator_path=GENERATOR_PATH,
    )
    return config, output_root, final, captured


def test_config_schema_order_profiles_and_outputs_are_exact() -> None:
    config = _config()
    GENERATOR.validate_config(config)
    assert tuple(config) == GENERATOR.TOP_LEVEL_KEYS
    assert config["schema_version"] == "v0.1"
    assert config["config_role"] == (
        "hedgehog_repository_owned_repomix_handoff_manifest"
    )
    assert config["generated_output_root"] == "_audit_exports"
    assert tuple(config["output_order"]) == OUTPUT_ORDER
    assert tuple(config["profile_order"]) == PROFILE_ORDER
    assert len(set(config["output_order"])) == len(OUTPUT_ORDER)
    assert all(not Path(name).is_absolute() for name in config["output_order"])
    assert all(".." not in Path(name).parts for name in config["output_order"])

    profiles = config["profiles"]
    assert tuple(profile["profile_id"] for profile in profiles) == PROFILE_ORDER
    assert tuple(profile["output_name"] for profile in profiles) == OUTPUT_ORDER[1:9]
    for profile in profiles:
        assert tuple(profile) == (
            "profile_id",
            "output_name",
            "include_patterns",
            "public_safe_audit_profile",
            "allows_committed_log_suffix",
        )
        assert tuple(profile["include_patterns"]) == PROFILE_INCLUDES[
            profile["profile_id"]
        ]


def test_exclusion_and_public_safe_audit_log_contract_is_exact() -> None:
    config = _config()
    assert tuple(config["global_exclude_patterns"]) == GLOBAL_EXCLUDE_PATTERNS
    assert "_audit_exports/**" in config["global_exclude_patterns"]
    assert "logs/**" in config["global_exclude_patterns"]
    assert "data/logs/**" in config["global_exclude_patterns"]
    assert "**/*.log" not in config["global_exclude_patterns"]
    assert "**/*secret*" not in config["global_exclude_patterns"]
    assert "**/*credential*" not in config["global_exclude_patterns"]
    assert config["repomix_policy"]["security_check"] is True

    audit_profiles = [
        profile
        for profile in config["profiles"]
        if profile["public_safe_audit_profile"]
        or profile["allows_committed_log_suffix"]
    ]
    assert [profile["profile_id"] for profile in audit_profiles] == [PROFILE_ORDER[5]]
    assert audit_profiles[0]["include_patterns"] == [
        "docs/audit_reports/**",
        "docs/evidence/**",
    ]
    assert all("docs/**" not in profile["include_patterns"] for profile in config["profiles"])


def test_real_g2_a_g2_b_audit_log_overlap_is_owned_only_by_profile_05() -> None:
    config = _config()
    profiles = {profile["profile_id"]: profile for profile in config["profiles"]}
    completed = subprocess.run(
        (
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.log",
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        shell=False,
    )
    repository_logs = {
        raw.decode("utf-8") for raw in completed.stdout.split(b"\0") if raw
    }
    required_logs = {G2_A_AUDIT_LOG_PATH, G2_B_AUDIT_LOG_PATH}
    assert required_logs <= repository_logs

    profile_05 = profiles[PROFILE_ORDER[5]]
    profile_06 = profiles[PROFILE_ORDER[6]]
    for path in required_logs:
        assert any(
            GENERATOR._pattern_matches(path, pattern)
            for pattern in profile_06["include_patterns"]
        )
        profile_06_excludes = GENERATOR.effective_profile_exclude_patterns(
            profile_06, config
        )
        assert "**/*.log" in profile_06_excludes
        assert any(
            GENERATOR._pattern_matches(path, pattern)
            for pattern in profile_06_excludes
        )

        assert any(
            GENERATOR._pattern_matches(path, pattern)
            for pattern in profile_05["include_patterns"]
        )
        profile_05_excludes = GENERATOR.effective_profile_exclude_patterns(
            profile_05, config
        )
        assert "**/*.log" not in profile_05_excludes
        assert not any(
            GENERATOR._pattern_matches(path, pattern)
            for pattern in profile_05_excludes
        )

    assert profile_06["allows_committed_log_suffix"] is False
    assert profile_05["allows_committed_log_suffix"] is True
    for profile in config["profiles"]:
        native = GENERATOR.build_native_repomix_config(
            profile,
            f"_audit_exports/.sample.tmp-1/{profile['output_name']}",
            config,
        )
        custom_patterns = native["ignore"]["customPatterns"]
        if profile["allows_committed_log_suffix"]:
            assert profile["profile_id"] == PROFILE_ORDER[5]
            assert custom_patterns == list(GLOBAL_EXCLUDE_PATTERNS)
        else:
            assert custom_patterns == [*GLOBAL_EXCLUDE_PATTERNS, "**/*.log"]


def test_profile_coverage_contains_each_required_surface() -> None:
    config = _config()
    profiles = {profile["profile_id"]: profile for profile in config["profiles"]}
    assert "tools/**" in profiles[PROFILE_ORDER[0]]["include_patterns"]
    assert "repomix.handoff.config.json" in profiles[PROFILE_ORDER[0]]["include_patterns"]
    assert "docs/repomix_handoff_reproducibility_v01.md" in profiles[PROFILE_ORDER[0]][
        "include_patterns"
    ]
    assert profiles[PROFILE_ORDER[4]]["include_patterns"] == ["tests/**"]
    assert "release/**" in profiles[PROFILE_ORDER[7]]["include_patterns"]

    mappings = {item["path"]: item for item in config["r_h1_artifact_mappings"]}
    inventory = set(GENERATOR.repository_python_inventory())
    assert CURRENT_R_H1C_PATHS <= inventory
    for path in CURRENT_R_H1C_PATHS:
        assert path in mappings
        assert mappings[path]["required_when_present"] is True
    GENERATOR.validate_artifact_coverage(config)

    obligations = config["planned_artifact_obligations"]
    assert obligations == [
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
    ]
    for obligation in obligations:
        assert obligation["path"] in mappings
        if (REPOSITORY_ROOT / obligation["path"]).exists():
            assert obligation["profile_id"] in mappings[obligation["path"]]["profile_ids"]


def test_planned_obligation_status_is_basis_metadata_not_current_presence(
    monkeypatch,
) -> None:
    config = _config()
    inventory = GENERATOR.repository_python_inventory()
    planned_paths = tuple(
        obligation["path"] for obligation in config["planned_artifact_obligations"]
    )
    assert all(
        obligation["current_status"] == "NOT_YET_PRESENT"
        for obligation in config["planned_artifact_obligations"]
    )
    monkeypatch.setattr(
        GENERATOR,
        "repository_python_inventory",
        lambda _repository_root=REPOSITORY_ROOT: inventory + planned_paths,
    )
    GENERATOR.validate_artifact_coverage(config)

    broken = json.loads(json.dumps(config))
    audit_mapping = next(
        mapping
        for mapping in broken["r_h1_artifact_mappings"]
        if mapping["path"] == R_H1_AUDIT_PATH
    )
    audit_mapping["profile_ids"] = []
    with pytest.raises(GENERATOR.HandoffError, match="lacks required profile mapping"):
        GENERATOR.validate_artifact_coverage(broken)


def test_generated_output_root_is_ignored_and_untracked() -> None:
    config = _config()
    GENERATOR.validate_generated_output_git_policy(config)
    ignored = subprocess.run(
        ("git", "check-ignore", "-q", "_audit_exports/example"),
        cwd=REPOSITORY_ROOT,
        check=False,
        shell=False,
    )
    assert ignored.returncode == 0
    tracked = subprocess.run(
        ("git", "ls-files", "-z", "--", "_audit_exports"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        shell=False,
    )
    assert tracked.stdout == b""


def test_generator_uses_standard_library_and_read_only_command_geometry() -> None:
    tree = ast.parse(GENERATOR_PATH.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.partition(".")[0])
    assert imported_roots <= set(sys.stdlib_module_names) | {"__future__"}
    assert not imported_roots & {
        "requests",
        "httpx",
        "urllib",
        "socket",
        "ftplib",
        "paramiko",
        "boto",
        "boto3",
        "google",
    }

    subprocess_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert subprocess_calls
    for call in subprocess_calls:
        shell_keywords = [keyword for keyword in call.keywords if keyword.arg == "shell"]
        assert len(shell_keywords) == 1
        assert isinstance(shell_keywords[0].value, ast.Constant)
        assert shell_keywords[0].value.value is False

    assert GENERATOR.READ_ONLY_GIT_SUBCOMMANDS == {
        "rev-parse",
        "status",
        "ls-files",
        "check-ignore",
    }
    assert not GENERATOR.READ_ONLY_GIT_SUBCOMMANDS & GENERATOR.MUTATING_GIT_SUBCOMMANDS
    runner_source = inspect.getsource(GENERATOR._default_profile_runner)
    assert '"--config"' in runner_source
    assert "--remote" not in runner_source
    assert "--no-security-check" not in runner_source
    assert "shell=True" not in GENERATOR_PATH.read_text(encoding="utf-8")
    assert "input.processors" not in inspect.getsource(GENERATOR.build_native_repomix_config)


def test_native_repomix_config_shape_is_fully_specified() -> None:
    config = _config()
    profile = config["profiles"][0]
    native = GENERATOR.build_native_repomix_config(
        profile,
        "_audit_exports/.sample.tmp-1/00_repo_governance_and_metadata.md",
        config,
    )
    assert native == {
        "input": {"maxFileSize": 50000000},
        "output": {
            "filePath": "_audit_exports/.sample.tmp-1/00_repo_governance_and_metadata.md",
            "style": "markdown",
            "filePathStyle": "cwd-relative",
            "parsableStyle": False,
            "compress": False,
            "headerText": None,
            "instructionFilePath": None,
            "fileSummary": True,
            "directoryStructure": True,
            "files": True,
            "removeComments": False,
            "removeEmptyLines": False,
            "showLineNumbers": False,
            "copyToClipboard": False,
            "includeEmptyDirectories": False,
            "includeFullDirectoryStructure": False,
            "git": {
                "sortByChanges": False,
                "sortByChangesMaxCommits": 100,
                "includeDiffs": False,
                "includeLogs": False,
                "includeLogsCount": 50,
            },
        },
        "include": list(PROFILE_INCLUDES[PROFILE_ORDER[0]]),
        "ignore": {
            "useGitignore": True,
            "useDotIgnore": True,
            "useDefaultPatterns": True,
            "customPatterns": [*GLOBAL_EXCLUDE_PATTERNS, "**/*.log"],
        },
        "security": {"enableSecurityCheck": True},
        "tokenCount": {"encoding": "o200k_base"},
    }


def test_repository_state_validation_is_phase_independent() -> None:
    clean_identity = _identity(clean=True)
    dirty_identity = _identity(clean=False)
    ahead_identity = replace(
        clean_identity,
        head="b" * 40,
        origin_main="a" * 40,
    )

    GENERATOR.validate_repository_state(
        clean_identity,
        mode="dry-run",
        allow_dirty_diagnostic=False,
    )
    GENERATOR.validate_repository_state(
        clean_identity,
        mode="dry-run",
        allow_dirty_diagnostic=True,
    )
    GENERATOR.validate_repository_state(
        clean_identity,
        mode="generate",
        allow_dirty_diagnostic=False,
    )
    with pytest.raises(GENERATOR.HandoffError, match="Worktree must be clean"):
        GENERATOR.validate_repository_state(
            dirty_identity,
            mode="dry-run",
            allow_dirty_diagnostic=False,
        )
    GENERATOR.validate_repository_state(
        dirty_identity,
        mode="dry-run",
        allow_dirty_diagnostic=True,
    )

    GENERATOR.validate_repository_state(
        ahead_identity,
        mode="dry-run",
        allow_dirty_diagnostic=False,
    )
    GENERATOR.validate_repository_state(
        ahead_identity,
        mode="dry-run",
        allow_dirty_diagnostic=True,
    )
    GENERATOR.validate_repository_state(
        ahead_identity,
        mode="verify",
        allow_dirty_diagnostic=False,
    )
    with pytest.raises(
        GENERATOR.HandoffError,
        match="HEAD must equal origin/main for generation",
    ):
        GENERATOR.validate_repository_state(
            ahead_identity,
            mode="generate",
            allow_dirty_diagnostic=False,
        )

    for mode in ("generate", "verify"):
        with pytest.raises(
            GENERATOR.HandoffError,
            match="valid only with --dry-run",
        ):
            GENERATOR.validate_repository_state(
                clean_identity,
                mode=mode,
                allow_dirty_diagnostic=True,
            )


def test_dry_validate_reports_clean_and_dirty_states_without_writes(
    monkeypatch,
    capsys,
) -> None:
    status_before = _git_status()
    output_before = _tree_snapshot(OUTPUT_ROOT)
    real_identity = GENERATOR.collect_repository_identity()
    simulated = {
        "identity": replace(
            real_identity,
            dirty_entries=(),
            staging_empty=True,
        )
    }

    def collect_simulated_identity(_repository_root=REPOSITORY_ROOT):
        return simulated["identity"]

    monkeypatch.setattr(
        GENERATOR,
        "collect_repository_identity",
        collect_simulated_identity,
    )

    GENERATOR.dry_validate(
        _config(),
        repomix_binary="/definitely/not/installed/repomix",
        allow_dirty_diagnostic=False,
    )
    assert capsys.readouterr().out.splitlines() == [
        "STATIC_VALIDATION=PASS",
        "DIRTY_DIAGNOSTIC_ONLY=false",
        "WORKTREE_CLEAN=true",
        "REPOMIX_AVAILABLE=false",
        "REAL_GENERATION_AVAILABLE=false",
        "GENERATION_PERFORMED=false",
    ]

    simulated["identity"] = replace(
        real_identity,
        dirty_entries=(" M tests/simulated_dirty_state.py",),
        staging_empty=True,
    )
    GENERATOR.dry_validate(
        _config(),
        repomix_binary="/definitely/not/installed/repomix",
        allow_dirty_diagnostic=True,
    )
    assert capsys.readouterr().out.splitlines() == [
        "STATIC_VALIDATION=PASS",
        "DIRTY_DIAGNOSTIC_ONLY=true",
        "WORKTREE_CLEAN=false",
        "REPOMIX_AVAILABLE=false",
        "REAL_GENERATION_AVAILABLE=false",
        "GENERATION_PERFORMED=false",
    ]

    with pytest.raises(GENERATOR.HandoffError, match="Worktree must be clean"):
        GENERATOR.dry_validate(
            _config(),
            repomix_binary="/definitely/not/installed/repomix",
            allow_dirty_diagnostic=False,
        )
    assert _git_status() == status_before
    assert _tree_snapshot(OUTPUT_ROOT) == output_before


def test_cli_dry_run_matches_actual_repository_phase_and_is_read_only() -> None:
    status_before = _git_status()
    output_before = _tree_snapshot(OUTPUT_ROOT)
    actual_worktree_clean = not bool(status_before)

    diagnostic = _run_generator(
        "--dry-run",
        "--allow-dirty-diagnostic",
        "--repomix-bin",
        "/definitely/not/installed/repomix",
    )
    assert diagnostic.returncode == 0, diagnostic.stderr
    assert "STATIC_VALIDATION=PASS" in diagnostic.stdout
    assert "DIRTY_DIAGNOSTIC_ONLY=true" in diagnostic.stdout
    assert (
        f"WORKTREE_CLEAN={str(actual_worktree_clean).lower()}"
        in diagnostic.stdout
    )
    assert "REPOMIX_AVAILABLE=false" in diagnostic.stdout
    assert "REAL_GENERATION_AVAILABLE=false" in diagnostic.stdout
    assert "GENERATION_PERFORMED=false" in diagnostic.stdout

    ordinary = _run_generator(
        "--dry-run",
        "--repomix-bin",
        "/definitely/not/installed/repomix",
    )
    if actual_worktree_clean:
        assert ordinary.returncode == 0, ordinary.stderr
        assert "STATIC_VALIDATION=PASS" in ordinary.stdout
        assert "DIRTY_DIAGNOSTIC_ONLY=false" in ordinary.stdout
        assert "WORKTREE_CLEAN=true" in ordinary.stdout
        assert "REPOMIX_AVAILABLE=false" in ordinary.stdout
        assert "REAL_GENERATION_AVAILABLE=false" in ordinary.stdout
        assert "GENERATION_PERFORMED=false" in ordinary.stdout
    else:
        assert ordinary.returncode != 0
        assert "Worktree must be clean" in ordinary.stderr
        assert "GENERATION_PERFORMED=false" in ordinary.stderr

    assert _git_status() == status_before
    assert _tree_snapshot(OUTPUT_ROOT) == output_before


def test_unavailable_repomix_generate_fails_before_output(monkeypatch, capsys) -> None:
    status_before = _git_status()
    output_before = _tree_snapshot(OUTPUT_ROOT)
    synchronized_identity = _identity(clean=True)

    def collect_synchronized_identity(_repository_root=REPOSITORY_ROOT):
        return synchronized_identity

    monkeypatch.setattr(
        GENERATOR,
        "collect_repository_identity",
        collect_synchronized_identity,
    )
    result = GENERATOR.main(
        (
            "--generate",
            "--repomix-bin",
            "/definitely/not/installed/repomix",
        )
    )
    captured = capsys.readouterr()
    assert result != 0
    assert "Repomix unavailable" in captured.err
    assert "GENERATION_PERFORMED=false" in captured.err
    assert "HEAD must equal origin/main" not in captured.err
    assert _git_status() == status_before
    assert _tree_snapshot(OUTPUT_ROOT) == output_before


def test_transactional_generation_order_metadata_and_checksums(tmp_path: Path) -> None:
    config, output_root, final, captured = _generate_synthetic_handoff(tmp_path)
    assert final == output_root / "valid-handoff"
    assert tuple(profile_id for profile_id, _native in captured) == PROFILE_ORDER
    assert {path.name for path in final.iterdir()} == set(OUTPUT_ORDER)
    assert not list(final.glob(".repomix-*.json"))
    assert GENERATOR.verify_generated_directory(final, config, output_root=output_root)

    head_lines = (final / OUTPUT_ORDER[0]).read_text(encoding="utf-8").splitlines()
    assert tuple(line.split("=", 1)[0] for line in head_lines) == GENERATOR.HEAD_FIELD_ORDER
    head = dict(line.split("=", 1) for line in head_lines)
    assert head["PROFILE_ORDER"] == ",".join(PROFILE_ORDER)
    assert head["OUTPUT_ORDER"] == ",".join(OUTPUT_ORDER)
    assert head["REPOMIX_VERSION"] == "repomix 1.2.3"
    assert "TIMESTAMP" not in head
    assert "HOSTNAME" not in head
    assert "USERNAME" not in head

    checksum_lines = (final / "SHA256SUMS").read_text(encoding="ascii").splitlines()
    assert len(checksum_lines) == 9
    assert tuple(line[66:] for line in checksum_lines) == OUTPUT_ORDER[:-1]
    assert all(line[64:66] == "  " for line in checksum_lines)
    assert "SHA256SUMS" not in tuple(line[66:] for line in checksum_lines)
    for (profile_id, native), expected_output in zip(captured, OUTPUT_ORDER[1:9], strict=True):
        assert profile_id in PROFILE_ORDER
        assert native["output"]["filePath"].endswith(f"/{expected_output}")
        assert native["security"] == {"enableSecurityCheck": True}
        expected_excludes = list(GLOBAL_EXCLUDE_PATTERNS)
        if profile_id != PROFILE_ORDER[5]:
            expected_excludes.append("**/*.log")
        assert native["ignore"]["customPatterns"] == expected_excludes


def test_transaction_failure_cleans_up_and_existing_final_is_preserved(tmp_path: Path) -> None:
    config = _config()
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    output_root = repository_root / "_audit_exports"
    call_count = 0

    def failing_runner(profile, _native, output_path, _binary):
        nonlocal call_count
        call_count += 1
        output_path.write_text(profile["profile_id"], encoding="utf-8")
        if call_count == 3:
            raise GENERATOR.HandoffError("injected profile failure")

    with pytest.raises(GENERATOR.HandoffError, match="injected profile failure"):
        GENERATOR.transactional_generate(
            config,
            _identity(),
            "/local/fake/repomix",
            "repomix 1.2.3",
            "failed-handoff",
            profile_runner=failing_runner,
            repository_root=repository_root,
            output_root=output_root,
            config_path=CONFIG_PATH,
            generator_path=GENERATOR_PATH,
        )
    assert not (output_root / "failed-handoff").exists()
    assert not list(output_root.glob(".failed-handoff.tmp-*")) if output_root.exists() else True
    assert not list(output_root.rglob("SHA256SUMS")) if output_root.exists() else True

    output_root.mkdir(exist_ok=True)
    existing = output_root / "existing-handoff"
    existing.mkdir()
    marker = existing / "owner-data"
    marker.write_text("preserve\n", encoding="utf-8")
    with pytest.raises(GENERATOR.HandoffError, match="already exists"):
        GENERATOR.transactional_generate(
            config,
            _identity(),
            "/local/fake/repomix",
            "repomix 1.2.3",
            "existing-handoff",
            profile_runner=failing_runner,
            repository_root=repository_root,
            output_root=output_root,
            config_path=CONFIG_PATH,
            generator_path=GENERATOR_PATH,
        )
    assert marker.read_text(encoding="utf-8") == "preserve\n"


def test_verification_rejects_every_malformed_output_geometry(tmp_path: Path) -> None:
    config, output_root, valid, _captured = _generate_synthetic_handoff(tmp_path)
    assert GENERATOR.verify_generated_directory(valid, config, output_root=output_root)

    def clone(name: str) -> Path:
        target = output_root / name
        shutil.copytree(valid, target)
        return target

    malformed: list[Path] = []

    missing = clone("missing")
    (missing / OUTPUT_ORDER[1]).unlink()
    malformed.append(missing)

    extra = clone("extra")
    (extra / "unexpected.txt").write_text("extra\n", encoding="utf-8")
    malformed.append(extra)

    renamed = clone("renamed")
    (renamed / OUTPUT_ORDER[1]).rename(renamed / "renamed.md")
    malformed.append(renamed)

    reordered = clone("reordered")
    lines = (reordered / "SHA256SUMS").read_text(encoding="ascii").splitlines(True)
    lines[0], lines[1] = lines[1], lines[0]
    (reordered / "SHA256SUMS").write_text("".join(lines), encoding="ascii", newline="\n")
    malformed.append(reordered)

    uppercase = clone("uppercase")
    checksum = (uppercase / "SHA256SUMS").read_text(encoding="ascii")
    (uppercase / "SHA256SUMS").write_text(
        checksum[:64].upper() + checksum[64:], encoding="ascii", newline="\n"
    )
    malformed.append(uppercase)

    one_space = clone("one-space")
    checksum = (one_space / "SHA256SUMS").read_text(encoding="ascii")
    (one_space / "SHA256SUMS").write_text(
        checksum.replace("  ", " ", 1), encoding="ascii", newline="\n"
    )
    malformed.append(one_space)

    three_spaces = clone("three-spaces")
    checksum = (three_spaces / "SHA256SUMS").read_text(encoding="ascii")
    (three_spaces / "SHA256SUMS").write_text(
        checksum.replace("  ", "   ", 1), encoding="ascii", newline="\n"
    )
    malformed.append(three_spaces)

    no_lf = clone("no-terminal-lf")
    checksum = (no_lf / "SHA256SUMS").read_bytes()
    (no_lf / "SHA256SUMS").write_bytes(checksum.rstrip(b"\n"))
    malformed.append(no_lf)

    altered = clone("altered")
    (altered / OUTPUT_ORDER[1]).write_text("altered\n", encoding="utf-8")
    malformed.append(altered)

    self_entry = clone("self-entry")
    lines = (self_entry / "SHA256SUMS").read_text(encoding="ascii").splitlines(True)
    lines[-1] = f"{'0' * 64}  SHA256SUMS\n"
    (self_entry / "SHA256SUMS").write_text("".join(lines), encoding="ascii", newline="\n")
    malformed.append(self_entry)

    symlinked = clone("symlinked")
    victim = symlinked / OUTPUT_ORDER[1]
    victim.unlink()
    victim.symlink_to(valid / OUTPUT_ORDER[1])
    malformed.append(symlinked)

    for directory in malformed:
        with pytest.raises(GENERATOR.HandoffError):
            GENERATOR.verify_generated_directory(directory, config, output_root=output_root)


def test_cli_mode_rules_and_handoff_identifier_are_fail_closed() -> None:
    assert GENERATOR.HANDOFF_ID_PATTERN.fullmatch("hedgehog-handoff-deadbeef1234")
    for invalid in ("", "../escape", ".hidden", "with space", "x" * 129):
        assert GENERATOR.HANDOFF_ID_PATTERN.fullmatch(invalid) is None

    invalid_dirty = _run_generator("--verify", "_audit_exports/example", "--allow-dirty-diagnostic")
    assert invalid_dirty.returncode == 2
    invalid_id = _run_generator("--dry-run", "--handoff-id", "not-allowed")
    assert invalid_id.returncode == 2


def test_external_roadmaps_are_custody_only_and_never_generated() -> None:
    config = _config()
    companions = config["external_companion_documents"]
    assert companions == [
        {
            "document_name": (
                "hedgehog_deeptech_completion_roadmap_v3_1_gate_based_guardian.md"
            ),
            "custody": "OWNER_SUPPLIED_EXTERNAL",
            "generator_action": "DO_NOT_FABRICATE",
        },
        {
            "document_name": "hedgehog_deeptech_completion_master_roadmap_v2_1.md",
            "custody": "OWNER_SUPPLIED_EXTERNAL",
            "generator_action": "DO_NOT_FABRICATE",
        },
    ]
    companion_names = {item["document_name"] for item in companions}
    assert not companion_names & set(config["output_order"])
    for profile in config["profiles"]:
        assert not companion_names & set(profile["include_patterns"])
    assert companion_names <= set(GENERATOR.EXTERNAL_COMPANION_DOCUMENTS)


def test_documentation_records_private_non_authority_and_exact_commands() -> None:
    text = DOCUMENTATION_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert text.startswith("# Repomix Handoff Reproducibility v0.1\n")
    for required in (
        "private engineering handoff tooling",
        "not a public release",
        "not a native Repomix auto-discovery configuration",
        "At the R-H1C implementation boundary, R-H1 was "
        "`IMPLEMENTATION_IN_PROGRESS`, Gate 2 was `NOT_CLOSED`, and G2-C was "
        "`NEXT / NOT_STARTED` and `NOT_AUTHORIZED`.",
        "Current status is recorded by `release/current_status_overlay_v01.json`, "
        "`release/current_limitations.md`, accepted audits/checkpoints, `AGENTS.md`, "
        "and owner instruction.",
        "`current_status: NOT_YET_PRESENT` is status captured at the R-H1C "
        "implementation basis",
        "Every validation derives actual current presence from Git's "
        "cached-plus-untracked, non-ignored inventory.",
        "Byte-identical reproduction requires the same branch identity, full HEAD "
        "commit, `origin/main` identity, clean generation state, handoff manifest "
        "bytes, generator bytes, and exact Repomix version.",
        "profile-local `**/*.log` exclusion",
        "--dry-run",
        "--allow-dirty-diagnostic",
        "--generate",
        "--handoff-id hedgehog-handoff-<identifier>",
        "--verify _audit_exports/<handoff-id>",
        "OWNER_SUPPLIED_EXTERNAL",
    ):
        assert required in normalized
    assert (
        "R-H1 remains `IMPLEMENTATION_IN_PROGRESS`. Gate 2 remains `NOT_CLOSED`. "
        "G2-C remains `NEXT / NOT_STARTED` and `NOT_AUTHORIZED`."
    ) not in normalized
    assert "npx" not in text.lower()
    assert "pip install" not in text.lower()
