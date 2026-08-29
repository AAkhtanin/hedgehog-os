from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import textwrap

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = REPOSITORY_ROOT / "tools/check_active_architecture_authority_v01.py"
E5_IMPLEMENTATION_BASIS_COMMIT = "f582701208b603463a03d404aa841c302a8221d6"
G2E_CLASS_A_COMMIT = "7f3c7138b553096252fefee7930f89100d835fcd"
G2E_CLOSURE_BASIS_COMMIT = "6079ddcfe59f582936e7b13af2753a6533117970"
CLASS_A_PATHS = (
    (
        "docs/continuous_delta_runtime_v0_1_"
        "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
    ),
    "release/successor_context_manifest_v01.json",
    "specs/current_architecture_lock_v01.md",
    "specs/document_authority_index_v01.json",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_repository_release_spine_v01.py",
    "tools/check_active_architecture_authority_v01.py",
)
CLASS_B_PATHS = (
    "demo/run_living_gauntlet_v01.py",
    "tests/test_living_gauntlet_v01_runner.py",
    "hedgehog/kernel/conformance_v01.py",
    "demo/run_kernel_conformance_v01.py",
    "tests/test_kernel_conformance_v01_runner.py",
)
CLASS_D_PATHS = (
    "docs/audit_reports/auditor_continuous_delta_runtime_g2_e_v01.log",
    "docs/continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md",
    "AGENTS.md",
    "README.md",
    "release/current_status_overlay_v01.json",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "specs/current_architecture_lock_v01.md",
    "specs/document_authority_index_v01.json",
    "release/successor_context_manifest_v01.json",
    "tools/check_active_architecture_authority_v01.py",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_repository_release_spine_v01.py",
)
COMMITTED_E5_PATHS = (
    "hedgehog/kernel/continuous_delta_runtime_v01.py",
    "tests/test_continuous_delta_runtime_g2_e_v01.py",
    "demo/run_continuous_delta_runtime_g2_e_v01.py",
)
MUTABLE_CONTROL_PATHS = (
    "AGENTS.md",
    "demo/run_kernel_conformance_v01.py",
    "demo/run_living_gauntlet_v01.py",
    "hedgehog/kernel/conformance_v01.py",
    "release/completion_manifest.json",
    "release/current_schema_surface_v01.json",
    "release/integration_seam_index.json",
    "release/retired_architecture_inventory_v01.json",
    "release/successor_context_manifest_v01.json",
    "specs/document_authority_index_v01.json",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
    "tests/test_kernel_conformance_v01_runner.py",
    "tests/test_living_gauntlet_v01_runner.py",
    "tests/test_repository_release_spine_v01.py",
    "tools/check_active_architecture_authority_v01.py",
)
CURRENT_SCHEMA_PATHS = (
    "schemas/common.schema.json",
    "schemas/continuous_delta_runtime_v01.schema.json",
    "schemas/drs_meaning_record_v01.schema.json",
    "schemas/drs_memory_resolution_v01.schema.json",
    "schemas/drs_semantic_address_v01.schema.json",
    "schemas/execution_mode_router_v01.schema.json",
    "schemas/fractal_runtime_v02.schema.json",
    "schemas/gt_report.schema.json",
    "schemas/kernel_artifact_v01.schema.json",
    "schemas/result_proposal.schema.json",
    "schemas/reuse_certificate_v01.schema.json",
    "schemas/semantic_work_v01.schema.json",
    "schemas/time_envelope.schema.json",
    "schemas/vv_report.schema.json",
)
RETIRED_PATHS = (
    "schemas/attractor_packet.schema.json",
    "schemas/plan_graph.schema.json",
    "hedgehog/architect.py",
    "hedgehog/architect_prompt_compiler.py",
    "hedgehog/executor.py",
    "hedgehog/fractal_dag_executor.py",
    "hedgehog/llm_architect.py",
    "hedgehog/root_orchestrator.py",
    "hedgehog/trace_reporter.py",
    "demo/run_all_layers_applied_super_smoke.py",
    "tests/test_all_layers_applied_super_smoke_runner.py",
)
READ_ONLY_CONTROL_PATHS = (
    "README.md",
    "specs/current_architecture_lock_v01.md",
    (
        "docs/continuous_delta_runtime_v0_1_"
        "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
    ),
    "demo/run_full_wow_v1_2_product_trace.py",
    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
    (
        "hedgehog/domains/supplier_water_filter/"
        "sealed_evidence_package_adapter_v01.py"
    ),
    "hedgehog/structured_rationale.py",
    "hedgehog/post_vv.py",
    "hedgehog/gt_validator.py",
    "hedgehog/__init__.py",
    "hedgehog/kernel/__init__.py",
    "hedgehog/kernel/continuous_delta_runtime_v01.py",
    "demo/run_continuous_delta_runtime_g2_e_v01.py",
    "tests/test_continuous_delta_runtime_g2_e_v01.py",
    "tests/test_execution_mode_router_g2_c_v01.py",
    "tests/test_fractal_runtime_g2_d_v02.py",
    "tests/test_continuous_delta_runtime_g2_e_v01.py",
    *CURRENT_SCHEMA_PATHS,
    *RETIRED_PATHS,
)
CONTROL_PATHS = tuple(dict.fromkeys((*MUTABLE_CONTROL_PATHS, *READ_ONLY_CONTROL_PATHS)))
FUTURE_REFERENCE_PATH = (
    "specs/future/quantum/"
    "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
)
FUTURE_REFERENCE_MANIFEST_EXCLUSION = "specs/future/**"


@pytest.fixture
def isolated_control_plane(tmp_path: Path) -> Path:
    subprocess.run(
        ("git", "init", "-q"),
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    real_objects = subprocess.run(
        ("git", "rev-parse", "--path-format=absolute", "--git-path", "objects"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    alternates = tmp_path / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_text(real_objects + "\n", encoding="ascii")
    subprocess.run(
        ("git", "read-tree", E5_IMPLEMENTATION_BASIS_COMMIT),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ("git", "update-ref", "refs/heads/main", E5_IMPLEMENTATION_BASIS_COMMIT),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ("git", "symbolic-ref", "HEAD", "refs/heads/main"),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    tracked = subprocess.run(
        ("git", "ls-files"),
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for offset in range(0, len(tracked), 200):
        subprocess.run(
            ("git", "update-index", "--skip-worktree", "--", *tracked[offset : offset + 200]),
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
    tracked_control = tuple(path for path in CONTROL_PATHS if path in set(tracked))
    subprocess.run(
        ("git", "update-index", "--no-skip-worktree", "--", *tracked_control),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    for relative_path in CLASS_B_PATHS:
        (tmp_path / relative_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ("git", "checkout-index", "--force", "--", *CLASS_B_PATHS),
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    current_control_paths = {
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_repository_release_spine_v01.py",
    }
    for relative_path in CONTROL_PATHS:
        if relative_path in CLASS_B_PATHS:
            continue
        destination = tmp_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative_path in current_control_paths:
            shutil.copyfile(REPOSITORY_ROOT / relative_path, destination)
        else:
            completed = subprocess.run(
                ("git", "show", f"{G2E_CLASS_A_COMMIT}:{relative_path}"),
                cwd=REPOSITORY_ROOT,
                check=True,
                capture_output=True,
            )
            destination.write_bytes(completed.stdout)
    assert _short_status_paths(tmp_path) == set(CLASS_A_PATHS)
    return tmp_path


@pytest.fixture
def isolated_clean_e5_control_plane(isolated_control_plane: Path) -> Path:
    subprocess.run(
        ("git", "add", "--", *CLASS_A_PATHS),
        cwd=isolated_control_plane,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        (
            "git",
            "-c",
            "user.name=Authority Guard Test",
            "-c",
            "user.email=authority-guard-test@example.invalid",
            "commit",
            "-q",
            "-m",
            "isolated Class-A reconciliation",
        ),
        cwd=isolated_control_plane,
        check=True,
        capture_output=True,
        text=True,
    )
    return isolated_control_plane


def _dirty_committed_e5_paths(root: Path, relative_paths: tuple[str, ...]) -> None:
    for index, relative_path in enumerate(relative_paths):
        path = root / relative_path
        path.write_text(
            path.read_text(encoding="utf-8")
            + f"\n# isolated committed-E5 substitution {index}\n",
            encoding="utf-8",
        )


def _short_status_paths(root: Path) -> set[str]:
    completed = subprocess.run(
        ("git", "status", "--short", "--untracked-files=all"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        line[3:]
        for line in completed.stdout.splitlines()
        if len(line) >= 4
    }


def _run_guard(
    root: Path,
    *,
    guard_path: Path = GUARD_PATH,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(guard_path), "--root", str(root)]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def test_clean_worktree_control_plane_passes() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(GUARD_PATH)],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stdout
    dirty_paths = _short_status_paths(REPOSITORY_ROOT)
    if dirty_paths:
        assert dirty_paths == set(CLASS_D_PATHS)
        lifecycle_mode = "G2E_CLOSED_PASS_CANDIDATE"
    else:
        lifecycle_mode = "G2E_CLOSED_PASS_COMMITTED"
    assert completed.stdout == (
        "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"
        "CURRENT_PHASE=POST_E6_SUCCESSOR\n"
        "LIFECYCLE_PHASE=G2E_CLOSED_PASS\n"
        f"LIFECYCLE_MODE={lifecycle_mode}\n"
    )
    assert completed.stderr == ""


def test_forbidden_direct_term_in_temporary_agents_copy_fails(
    isolated_control_plane: Path,
) -> None:
    agents_path = isolated_control_plane / "AGENTS.md"
    forbidden_term = "Plan" + "Graph"
    agents_path.write_text(
        agents_path.read_text(encoding="utf-8") + f"\n{forbidden_term}\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "ACTIVE_ARCHITECTURE_AUTHORITY_V01 FAIL" in completed.stdout
    assert "current_document.forbidden_term:AGENTS.md" in completed.stdout


def test_historical_file_marked_current_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    authority_index["historical_documents"][0]["current_authority"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "historical.current_authority:" in completed.stdout


def test_historical_file_in_source_order_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    historical_path = "specs/human_passport_v0_25.md"
    authority_index["source_of_truth_order"].insert(
        1, f"{historical_path} controls current implementation"
    )
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"historical.in_source_of_truth_order:{historical_path}"
        in completed.stdout
    )


def test_historical_file_in_successor_context_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    historical_path = "specs/human_passport_v0_25.md"
    manifest["always_include"].append(historical_path)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"historical.in_successor_context:{historical_path}" in completed.stdout


def test_noncanonical_historical_alias_in_successor_context_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["always_include"].append("./specs/human_passport_v0_25.md")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.always_include.path" in completed.stdout


def test_active_document_excluded_by_glob_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["exclude_globs"].append("**")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.exclusion_conflict_glob:" in completed.stdout


def test_required_current_classification_missing_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    authority_index["current_operational_documents"] = []
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "authority_index.current_operational_documents.missing:AGENTS.md" in completed.stdout


def test_future_reference_category_missing_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    authority_index.pop("future_reference_documents")
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "authority_index.top_level_shape" in completed.stdout
    assert (
        "authority_index.future_reference_documents.missing:"
        + FUTURE_REFERENCE_PATH
        in completed.stdout
    )


def test_future_reference_marked_current_authority_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = authority_index["future_reference_documents"][0]
    entry["current_authority"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"future_reference.current_authority:{FUTURE_REFERENCE_PATH}" in (
        completed.stdout
    )


def test_future_reference_using_global_architecture_scope_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = authority_index["future_reference_documents"][0]
    entry["authority_scope"] = "current_global_architecture_law"
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"future_reference.authority_scope:{FUTURE_REFERENCE_PATH}" in (
        completed.stdout
    )
    assert f"authority_index.global_scope_not_lock:{FUTURE_REFERENCE_PATH}" in (
        completed.stdout
    )


def test_future_reference_may_not_override_architecture_lock(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = authority_index["future_reference_documents"][0]
    entry["may_override_architecture_lock"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"future_reference.may_override_architecture_lock:{FUTURE_REFERENCE_PATH}"
        in completed.stdout
    )


def test_future_reference_cannot_be_onboarded(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = authority_index["future_reference_documents"][0]
    entry["onboarding_allowed"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"future_reference.onboarding_allowed:{FUTURE_REFERENCE_PATH}" in (
        completed.stdout
    )


def test_future_reference_role_cannot_claim_implementation(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = authority_index["future_reference_documents"][0]
    entry["role"] = "current runtime implementation authority"
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"future_reference.role:{FUTURE_REFERENCE_PATH}" in completed.stdout


def test_future_reference_index_exclusion_missing_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    authority_index["excluded_from_successor_onboarding"].remove(
        FUTURE_REFERENCE_PATH
    )
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "future_reference.index_exclusion_missing" in completed.stdout
    assert f"future_reference.not_index_excluded:{FUTURE_REFERENCE_PATH}" in (
        completed.stdout
    )


def test_future_reference_in_source_of_truth_order_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    authority_index["source_of_truth_order"].append(FUTURE_REFERENCE_PATH)
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"future_reference.in_source_of_truth_order:{FUTURE_REFERENCE_PATH}"
        in completed.stdout
    )


def test_future_reference_manifest_exclusion_missing_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["exclude_globs"].remove(FUTURE_REFERENCE_MANIFEST_EXCLUSION)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.exclude_globs.missing_retired:"
        + FUTURE_REFERENCE_MANIFEST_EXCLUSION
        in completed.stdout
    )


def test_required_retired_family_exclusion_missing_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    retired_path = "hedgehog/mode_router.py"
    manifest["exclude_paths"].remove(retired_path)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"successor_manifest.exclude_paths.missing_retired:{retired_path}"
        in completed.stdout
    )


def test_blocking_repair_reintroduced_while_onboarding_ready_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["onboarding_ready"] is True
    assert manifest["blocking_repairs"] == []
    manifest["blocking_repairs"] = ["S3_ACTIVE_SCHEMA_AND_LEGACY_ISOLATION"]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.blocking_repairs.exact" in completed.stdout
    assert "successor_manifest.ready_with_blocking_repairs" in completed.stdout


def test_onboarding_not_ready_with_no_blocking_repairs_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["blocking_repairs"] == []
    manifest["onboarding_ready"] = False
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.onboarding_ready" in completed.stdout
    assert "successor_manifest.not_ready_without_blocking_repairs" in completed.stdout


def test_successor_manifest_marked_current_authority_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    manifest_entry = next(
        entry
        for entry in authority_index["current_operational_documents"]
        if entry["path"] == "release/successor_context_manifest_v01.json"
    )
    manifest_entry["current_authority"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "authority_index.successor_manifest_has_authority" in completed.stdout


def test_gate_annex_using_global_architecture_scope_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    gate_entry = authority_index["current_technical_annexes"][0]
    gate_path = gate_entry["path"]
    gate_entry["authority_scope"] = "current_global_architecture_law"
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert f"authority_index.global_scope_not_lock:{gate_path}" in completed.stdout
    assert f"authority_index.gate_annex.scope:{gate_path}" in completed.stdout


def test_gate_annex_misclassified_as_operational_authority_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    gate_path = "docs/gate_x_checkpoint_v01.md"
    authority_index["current_operational_documents"].append(
        {
            "path": gate_path,
            "status": "accepted_gate_x_checkpoint",
            "current_authority": True,
            "authority_scope": (
                "operational_instructions_subordinate_to_architecture_lock"
            ),
            "may_override_architecture_lock": False,
            "onboarding_allowed": True,
            "role": "accepted Gate X contract annex",
        }
    )
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"authority_index.current_operational_documents.unexpected:{gate_path}"
        in completed.stdout
    )


def test_document_may_override_architecture_lock_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = (
        isolated_control_plane / "specs/document_authority_index_v01.json"
    )
    authority_index = json.loads(index_path.read_text(encoding="utf-8"))
    agents_entry = authority_index["current_operational_documents"][0]
    agents_entry["may_override_architecture_lock"] = True
    index_path.write_text(
        json.dumps(authority_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "authority_index.may_override_architecture_lock:AGENTS.md"
        in completed.stdout
    )


def test_agents_missing_s3_closure_warning_fails(
    isolated_control_plane: Path,
) -> None:
    agents_path = isolated_control_plane / "AGENTS.md"
    original = agents_path.read_text(encoding="utf-8")
    warning = (
        "S1 document-authority succession, S2 vocabulary\n"
        "repair, and S3 active-schema and retired-subsystem isolation are closed."
    )
    assert warning in original
    agents_path.write_text(
        original.replace(warning, "removed S3 warning"),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "current_document.missing_onboarding_warning:AGENTS.md:s1_s2_s3_closed"
        in completed.stdout
    )


@pytest.mark.parametrize(
    "closed_s2_repair",
    (
        "S2_STRUCTURED_RATIONALE_VOCABULARY_REPAIR",
        "S2_SUPPLIER_ADAPTER_EVENT_VOCABULARY_REPAIR",
    ),
)
def test_closed_s2_blocker_reintroduced_fails(
    isolated_control_plane: Path,
    closed_s2_repair: str,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["blocking_repairs"].append(closed_s2_repair)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.blocking_repairs.exact" in completed.stdout


def test_structured_rationale_positive_residue_reintroduced_fails(
    isolated_control_plane: Path,
) -> None:
    source_path = isolated_control_plane / "hedgehog/structured_rationale.py"
    retired_value = "bounded_" + "plan" + "_" + "graph"
    source_path.write_text(
        source_path.read_text(encoding="utf-8")
        + f'\n_REINTRODUCED = "{retired_value}"\n',
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s2.structured_rationale.retired_positive:0" in completed.stdout


def test_supplier_event_residue_reintroduced_fails(
    isolated_control_plane: Path,
) -> None:
    source_path = (
        isolated_control_plane
        / "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py"
    )
    retired_event = "runtime_" + "plan" + "graph_compiled"
    source_path.write_text(
        source_path.read_text(encoding="utf-8")
        + f'\n_REINTRODUCED_EVENT = "{retired_event}"\n',
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s2.supplier_event.retired:"
        "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py"
        in completed.stdout
    )


@pytest.mark.parametrize("required_term", ("BSEP", "RuntimeExecutionTopology"))
def test_missing_current_architecture_term_fails(
    isolated_control_plane: Path,
    required_term: str,
) -> None:
    agents_path = isolated_control_plane / "AGENTS.md"
    original = agents_path.read_text(encoding="utf-8")
    assert required_term in original
    agents_path.write_text(
        original.replace(required_term, "removed_current_term"),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        f"current_document.missing_term:AGENTS.md:{required_term}"
        in completed.stdout
    )


def test_unexpected_changed_path_fails(isolated_control_plane: Path) -> None:
    unexpected_path = isolated_control_plane / "hedgehog/unexpected_change.py"
    unexpected_path.parent.mkdir(parents=True, exist_ok=True)
    unexpected_path.write_text("unexpected = True\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:hedgehog/unexpected_change.py"
        in completed.stdout
    )


def test_lone_historical_allowlisted_g2b_test_path_is_rejected(
    isolated_control_plane: Path,
) -> None:
    approved_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    approved_path.write_text(
        approved_path.read_text(encoding="utf-8") + "\n# approved dirty path\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:"
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
        in completed.stdout
    )


def test_neighboring_g2b_test_path_is_rejected(
    isolated_control_plane: Path,
) -> None:
    neighboring_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01_extra.py"
    )
    neighboring_path.write_text("unexpected = True\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:"
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01_extra.py"
        in completed.stdout
    )


def test_arbitrary_tests_path_is_rejected(
    isolated_control_plane: Path,
) -> None:
    arbitrary_path = isolated_control_plane / "tests/test_unapproved_s3_path.py"
    arbitrary_path.write_text("unexpected = True\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:tests/test_unapproved_s3_path.py"
        in completed.stdout
    )


def test_approved_g2b_path_plus_unexpected_second_path_is_rejected(
    isolated_control_plane: Path,
) -> None:
    approved_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    approved_path.write_text(
        approved_path.read_text(encoding="utf-8") + "\n# approved dirty path\n",
        encoding="utf-8",
    )
    unexpected_path = isolated_control_plane / "tests/test_second_dirty_path.py"
    unexpected_path.write_text("unexpected = True\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:tests/test_second_dirty_path.py"
        in completed.stdout
    )
    assert (
        "worktree.unexpected_changed_path:"
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
        in completed.stdout
    )


def test_declared_legacy_path_cannot_expand_the_phase_ledger(
    isolated_control_plane: Path,
) -> None:
    approved_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    approved_path.write_text(
        approved_path.read_text(encoding="utf-8") + "\n# legacy path\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:"
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
        in completed.stdout
    )


def test_clean_post_s3_control_plane_passes(
    isolated_clean_e5_control_plane: Path,
) -> None:
    assert _short_status_paths(isolated_clean_e5_control_plane) == set()

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 0, completed.stdout
    assert completed.stdout == "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"
    assert completed.stderr == ""


def test_all_exact_committed_e5_path_substitutions_fail(
    isolated_clean_e5_control_plane: Path,
) -> None:
    _dirty_committed_e5_paths(
        isolated_clean_e5_control_plane,
        COMMITTED_E5_PATHS,
    )
    assert _short_status_paths(isolated_clean_e5_control_plane) == set(
        COMMITTED_E5_PATHS
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    for path in COMMITTED_E5_PATHS:
        assert f"e6.committed_e5.identity:{path}" in completed.stdout


@pytest.mark.parametrize(
    "dirty_paths",
    (
        (COMMITTED_E5_PATHS[0],),
        (COMMITTED_E5_PATHS[1],),
        (COMMITTED_E5_PATHS[2],),
        (COMMITTED_E5_PATHS[0], COMMITTED_E5_PATHS[1]),
        (COMMITTED_E5_PATHS[0], COMMITTED_E5_PATHS[2]),
        (COMMITTED_E5_PATHS[1], COMMITTED_E5_PATHS[2]),
    ),
)
def test_any_one_or_two_committed_e5_path_substitutions_fail(
    isolated_clean_e5_control_plane: Path,
    dirty_paths: tuple[str, ...],
) -> None:
    _dirty_committed_e5_paths(isolated_clean_e5_control_plane, dirty_paths)
    assert _short_status_paths(isolated_clean_e5_control_plane) == set(
        dirty_paths
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    for path in dirty_paths:
        assert f"e6.committed_e5.identity:{path}" in completed.stdout


def test_exact_committed_e5_set_plus_unexpected_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    _dirty_committed_e5_paths(
        isolated_clean_e5_control_plane,
        COMMITTED_E5_PATHS,
    )
    unexpected_path = isolated_clean_e5_control_plane / "unexpected_post_s3.txt"
    unexpected_path.write_text("unexpected\n", encoding="utf-8")

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:unexpected_post_s3.txt"
        in completed.stdout
    )


@pytest.mark.parametrize(
    "unexpected_path",
    (
        "demo/run_continuous_delta_runtime_g2_e_v01_extra.py",
        "hedgehog/kernel/unexpected_post_s3_runtime.py",
        "tests/test_unexpected_post_s3_runtime.py",
    ),
)
def test_neighboring_or_unrelated_runtime_test_path_fails(
    isolated_clean_e5_control_plane: Path,
    unexpected_path: str,
) -> None:
    path = isolated_clean_e5_control_plane / unexpected_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("unexpected = True\n", encoding="utf-8")

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        f"worktree.unexpected_changed_path:{unexpected_path}"
        in completed.stdout
    )


def test_renaming_committed_e5_path_to_unapproved_neighbor_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    source = COMMITTED_E5_PATHS[2]
    destination = "demo/run_continuous_delta_runtime_g2_e_v01_extra.py"
    subprocess.run(
        ("git", "mv", "--", source, destination),
        cwd=isolated_clean_e5_control_plane,
        check=True,
        capture_output=True,
        text=True,
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        f"worktree.unexpected_changed_path:{destination}"
        in completed.stdout
    )


def test_noncanonical_dot_slash_committed_e5_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["committed_e5_basis"]["paths"][0]["path"] == (
        COMMITTED_E5_PATHS[0]
    )
    manifest["committed_e5_basis"]["paths"][0]["path"] = (
        "./" + COMMITTED_E5_PATHS[0]
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.committed_e5_basis.paths[0].path"
        in completed.stdout
    )
    assert (
        "successor_manifest.committed_e5_basis.paths.exact"
        in completed.stdout
    )


def test_dot_slash_unexpected_changed_path_fails_exact_membership() -> None:
    guard_namespace = runpy.run_path(str(GUARD_PATH))
    failures: list[str] = []

    guard_namespace["_validate_changed_paths"](
        {"./unexpected_post_s3.py"},
        COMMITTED_E5_PATHS,
        failures,
    )

    assert failures == [
        "worktree.unexpected_changed_path:./unexpected_post_s3.py"
    ]


def test_removed_manifest_e5_path_cannot_authorize_its_dirt(
    isolated_clean_e5_control_plane: Path,
) -> None:
    removed_path = COMMITTED_E5_PATHS[2]
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["committed_e5_basis"]["paths"] = [
        entry
        for entry in manifest["committed_e5_basis"]["paths"]
        if entry["path"] != removed_path
    ]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _dirty_committed_e5_paths(
        isolated_clean_e5_control_plane,
        (removed_path,),
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.committed_e5_basis.paths.exact"
        in completed.stdout
    )
    assert (
        f"worktree.unexpected_changed_path:{removed_path}"
        in completed.stdout
    )


def test_retired_import_in_allowed_e5_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    runtime_path = isolated_clean_e5_control_plane / COMMITTED_E5_PATHS[0]
    runtime_path.write_text(
        runtime_path.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.E5_RETIRED_IMPORTS:hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_retired_positive_vocabulary_in_allowed_e5_runtime_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    runtime_path = isolated_clean_e5_control_plane / COMMITTED_E5_PATHS[0]
    retired_term = "Plan" + "Graph"
    runtime_path.write_text(
        runtime_path.read_text(encoding="utf-8")
        + f'\n_RETIRED_POSITIVE = "{retired_term}"\n',
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.e5_runtime.retired_positive:"
        + COMMITTED_E5_PATHS[0]
        + ":0"
        in completed.stdout
    )


def test_provider_owned_topology_claim_in_allowed_e5_runtime_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    runtime_path = isolated_clean_e5_control_plane / COMMITTED_E5_PATHS[0]
    runtime_path.write_text(
        runtime_path.read_text(encoding="utf-8")
        + "\n_PROVIDER_OWNED_TOPOLOGY = True\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.e5_runtime.provider_owned_topology:"
        + COMMITTED_E5_PATHS[0]
        in completed.stdout
    )


def test_successor_readiness_false_after_s3_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["blocking_repairs"] == []
    manifest["onboarding_ready"] = False
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.onboarding_ready" in completed.stdout
    assert (
        "successor_manifest.not_ready_without_blocking_repairs"
        in completed.stdout
    )


def test_nonempty_blocking_repairs_under_ready_manifest_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["onboarding_ready"] is True
    manifest["blocking_repairs"] = ["REINTRODUCED_POST_S3_BLOCKER"]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.blocking_repairs.exact" in completed.stdout
    assert "successor_manifest.ready_with_blocking_repairs" in completed.stdout


def test_historical_act_added_to_current_v06_refs_fails(
    isolated_control_plane: Path,
) -> None:
    source_path = isolated_control_plane / "hedgehog/kernel/conformance_v01.py"
    source = source_path.read_text(encoding="utf-8")
    marker = (
        '_V06_CURRENT_ACTIVE_GAUNTLET_REFS = (\n'
        '    "airline_deterministic_transaction_runtime",\n'
    )
    assert marker in source
    source_path.write_text(
        source.replace(
            marker,
            marker + '    "all_layers_invariant_super_smoke",\n',
            1,
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s3.kernel_conformance.old_act_in_current_profile" in completed.stdout


def test_historical_act_removed_from_frozen_v05_profile_fails(
    isolated_control_plane: Path,
) -> None:
    completion_path = isolated_control_plane / "release/completion_manifest.json"
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    historical_refs = completion["kernel_conformance_profiles"]["historical_v0_5"][
        "active_gauntlet_refs"
    ]
    historical_refs.remove("all_layers_invariant_super_smoke")
    completion_path.write_text(
        json.dumps(completion, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s3.release.completion.historical_profile_exact" in completed.stdout


def test_historical_act_id_rebound_to_current_runner_fails(
    isolated_control_plane: Path,
) -> None:
    runner_path = isolated_control_plane / "demo/run_kernel_conformance_v01.py"
    source = runner_path.read_text(encoding="utf-8")
    marker = "_ACT_SOURCES = {\n"
    assert marker in source
    runner_path.write_text(
        source.replace(
            marker,
            marker
            + '    "all_layers_invariant_super_smoke": '
            + '("demo.current_rebind", "collect_current_rebind"),\n',
            1,
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.kernel_conformance_runner.historical_act_rebound"
        in completed.stdout
    )


def test_living_gauntlet_importing_historical_runner_fails(
    isolated_control_plane: Path,
) -> None:
    living_path = isolated_control_plane / "demo/run_living_gauntlet_v01.py"
    living_path.write_text(
        living_path.read_text(encoding="utf-8")
        + "\nimport demo.run_all_layers_applied_super_smoke\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.LIVING_GAUNTLET_RETIRED_IMPORTS:"
        "demo.run_all_layers_applied_super_smoke"
        in completed.stdout
    )


def test_historical_act_marked_current_in_release_index_fails(
    isolated_control_plane: Path,
) -> None:
    completion_path = isolated_control_plane / "release/completion_manifest.json"
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    historical = next(
        record
        for record in completion["evidence_only_references"]
        if record.get("act_id") == "all_layers_invariant_super_smoke"
    )
    current_record = dict(historical)
    current_record["status"] = "ACTIVE"
    completion["active_runtime_acts"].append(current_record)
    completion_path.write_text(
        json.dumps(completion, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s3.release.completion.historical_act_current" in completed.stdout


def test_required_current_claim_mapping_removed_fails(
    isolated_control_plane: Path,
) -> None:
    completion_path = isolated_control_plane / "release/completion_manifest.json"
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    completion["current_regression_claim_mapping"].pop("receipt_evidence_only")
    completion_path.write_text(
        json.dumps(completion, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s3.release.completion.claim_mapping_exact" in completed.stdout


def test_historical_v05_cannot_become_default_profile(
    isolated_control_plane: Path,
) -> None:
    source_path = isolated_control_plane / "hedgehog/kernel/conformance_v01.py"
    source = source_path.read_text(encoding="utf-8")
    current = (
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE = "
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT"
    )
    assert current in source
    source_path.write_text(
        source.replace(
            current,
            "DEFAULT_KERNEL_CONFORMANCE_PROFILE = "
            "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL",
            1,
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.kernel_conformance.profile_exact:DEFAULT_KERNEL_CONFORMANCE_PROFILE"
        in completed.stdout
    )


def test_unregistered_current_act_id_fails(
    isolated_control_plane: Path,
) -> None:
    source_path = isolated_control_plane / "hedgehog/kernel/conformance_v01.py"
    source = source_path.read_text(encoding="utf-8")
    marker = (
        '_V06_CURRENT_ACTIVE_GAUNTLET_REFS = (\n'
        '    "airline_deterministic_transaction_runtime",\n'
    )
    assert marker in source
    source_path.write_text(
        source.replace(
            marker,
            marker + '    "unregistered_current_act",\n',
            1,
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.kernel_conformance.profile_exact:"
        "_V06_CURRENT_ACTIVE_GAUNTLET_REFS"
        in completed.stdout
    )


def test_current_act_reading_historical_pass_log_fails(
    isolated_control_plane: Path,
) -> None:
    living_path = isolated_control_plane / "demo/run_living_gauntlet_v01.py"
    living_path.write_text(
        living_path.read_text(encoding="utf-8")
        + (
            '\n_HISTORICAL_PASS = Path('
            '"docs/audit_reports/historical_gate1.log").read_text()\n'
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "s3.living_gauntlet.historical_pass_consumption" in completed.stdout


def test_retired_schema_added_to_current_schema_surface_fails(
    isolated_control_plane: Path,
) -> None:
    surface_path = (
        isolated_control_plane / "release/current_schema_surface_v01.json"
    )
    surface = json.loads(surface_path.read_text(encoding="utf-8"))
    surface["current_schema_paths"].append("schemas/plan_graph.schema.json")
    surface_path.write_text(
        json.dumps(surface, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.current_schema_surface.retired_schema_current:"
        "schemas/plan_graph.schema.json"
        in completed.stdout
    )


def test_retired_path_included_in_successor_context_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["include_current_gate_sources"].append("hedgehog/root_orchestrator.py")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.exclusion_conflict_path:hedgehog/root_orchestrator.py"
        in completed.stdout
    )


def test_s3_inventory_cannot_claim_global_architecture_authority(
    isolated_control_plane: Path,
) -> None:
    index_path = isolated_control_plane / "specs/document_authority_index_v01.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    inventory_entry = next(
        entry
        for entry in index["current_operational_documents"]
        if entry["path"] == "release/retired_architecture_inventory_v01.json"
    )
    inventory_entry["authority_scope"] = "current_global_architecture_law"
    index_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "authority_index.global_scope_not_lock:"
        "release/retired_architecture_inventory_v01.json"
        in completed.stdout
    )


def test_retired_import_from_current_gate2_test_fails(
    isolated_control_plane: Path,
) -> None:
    gate2_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    gate2_path.write_text(
        gate2_path.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.CURRENT_GATE2_RETIRED_IMPORTS:"
        "hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_transitive_retired_import_from_living_gauntlet_fails(
    isolated_control_plane: Path,
) -> None:
    conformance_runner = (
        isolated_control_plane / "demo/run_kernel_conformance_v01.py"
    )
    conformance_runner.write_text(
        conformance_runner.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.LIVING_GAUNTLET_RETIRED_IMPORTS:"
        "hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_retired_import_from_e5_scope_fails(
    isolated_control_plane: Path,
) -> None:
    e5_path = (
        isolated_control_plane / "hedgehog/kernel/continuous_delta_runtime_v01.py"
    )
    e5_path.write_text(
        e5_path.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.E5_RETIRED_IMPORTS:hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_retired_export_from_current_package_facade_fails(
    isolated_control_plane: Path,
) -> None:
    facade_path = isolated_control_plane / "hedgehog/__init__.py"
    facade_path.write_text(
        facade_path.read_text(encoding="utf-8")
        + "\nfrom hedgehog import root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.package_facade.retired_export:hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_retired_path_removed_from_successor_exclusions_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["exclude_paths"].remove("hedgehog/root_orchestrator.py")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.exclude_paths.missing_s3:hedgehog/root_orchestrator.py"
        in completed.stdout
    )


def test_onboarding_ready_fails_when_current_retired_import_exists(
    isolated_control_plane: Path,
) -> None:
    manifest = json.loads(
        (
            isolated_control_plane / "release/successor_context_manifest_v01.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["onboarding_ready"] is True
    living_path = isolated_control_plane / "demo/run_living_gauntlet_v01.py"
    living_path.write_text(
        living_path.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.LIVING_GAUNTLET_RETIRED_IMPORTS:"
        "hedgehog.root_orchestrator"
        in completed.stdout
    )


def test_historical_retired_import_stays_outside_current_graph_but_dirt_fails(
    isolated_control_plane: Path,
) -> None:
    historical_test = (
        isolated_control_plane / "tests/test_all_layers_applied_super_smoke_runner.py"
    )
    historical_test.write_text(
        historical_test.read_text(encoding="utf-8")
        + "\nimport hedgehog.root_orchestrator\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "worktree.unexpected_changed_path:"
        "tests/test_all_layers_applied_super_smoke_runner.py"
        in completed.stdout
    )
    assert "s3.import_graph." not in completed.stdout


def test_dynamic_retired_import_from_current_gate2_test_fails(
    isolated_control_plane: Path,
) -> None:
    gate2_path = (
        isolated_control_plane
        / "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    gate2_path.write_text(
        gate2_path.read_text(encoding="utf-8")
        + (
            "\nimport importlib\n"
            '_RETIRED_DYNAMIC = importlib.import_module("hedgehog.executor")\n'
        ),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.import_graph.CURRENT_GATE2_RETIRED_IMPORTS:hedgehog.executor"
        in completed.stdout
    )


def test_current_loader_registering_retired_schema_fails(
    isolated_control_plane: Path,
) -> None:
    loader_path = isolated_control_plane / "hedgehog/post_vv.py"
    loader_path.write_text(
        loader_path.read_text(encoding="utf-8")
        + '\n_RETIRED_SCHEMA = "schemas/plan_graph.schema.json"\n',
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.current_schema_surface.retired_registration:"
        "hedgehog/post_vv.py:schemas/plan_graph.schema.json"
        in completed.stdout
    )


def _phase_contract_namespace() -> dict[str, object]:
    return runpy.run_path(str(GUARD_PATH))


def test_exact_pre_e6_reconciled_phase_classifier_passes() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_pre_e6_phase_state_v01"]()

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase == "PRE_E6_RECONCILED"
    assert failures == ()


def test_exact_synthetic_post_e6_successor_phase_classifier_passes() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_post_e6_phase_state_v01"]()

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase == "POST_E6_SUCCESSOR"
    assert failures == ()


@pytest.mark.parametrize(
    ("key", "replacement", "expected_failure"),
    (
        (
            "living_act_ids",
            ("generic_integrity_replay",),
            "e6.phase.pre.living_act_ids",
        ),
        (
            "category_check_ids",
            (),
            "e6.phase.pre.category_check_ids",
        ),
        (
            "negative_probe_ids",
            ("replay_hash_mismatch", "manifest_hash_mismatch"),
            "e6.phase.pre.negative_probe_ids",
        ),
        (
            "runner_current_refs",
            ("airline_deterministic_transaction_runtime",),
            "e6.phase.pre.runner_current_refs",
        ),
        (
            "domain_geometry",
            (),
            "e6.phase.pre.domain_geometry",
        ),
    ),
)
def test_same_version_different_geometry_fails_exactly(
    key: str,
    replacement: object,
    expected_failure: str,
) -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_pre_e6_phase_state_v01"]()
    state[key] = replacement

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert expected_failure in failures


@pytest.mark.parametrize(
    ("versions", "expected_failure"),
    (
        (("v1.5", "v0.6", "v0.5"), "e6.phase.runner_version"),
        (("v1.6", "v0.6", "v0.6"), "e6.phase.version_hybrid"),
        (("v1.5", "v0.7", "v0.7"), "e6.phase.version_hybrid"),
        (("v1.6", "v0.7", "v0.6"), "e6.phase.version_hybrid"),
    ),
)
def test_hybrid_or_regressive_version_geometry_fails(
    versions: tuple[str, str, str],
    expected_failure: str,
) -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_pre_e6_phase_state_v01"]()
    state["living_version"], state["core_version"], state["runner_version"] = (
        versions
    )

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert expected_failure in failures


def test_post_e6_missing_v06_immediate_historical_profile_fails() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_post_e6_phase_state_v01"]()
    state["core_profile_v06_historical"] = None

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert "e6.phase.post.core_profile_v06_historical" in failures


def test_post_e6_erased_v05_evidence_fails() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_post_e6_phase_state_v01"]()
    state["core_profile_v05"] = None
    state["historical_v05_evidence_preserved"] = False

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert "e6.phase.post.core_profile_v05" in failures
    assert "e6.phase.historical_v05_evidence_erased" in failures


def test_historical_all_layers_current_rebinding_fails() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_post_e6_phase_state_v01"]()
    state["historical_all_layers_current"] = True

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert "e6.phase.historical_all_layers_rebound" in failures


def test_focused_test_phase_cannot_lag_source_phase() -> None:
    namespace = _phase_contract_namespace()
    state = namespace["_expected_post_e6_phase_state_v01"]()
    state["focused_test_phase"] = "PRE_E6_RECONCILED"

    phase, failures = namespace["_classify_e6_phase_v01"](state)

    assert phase is None
    assert "e6.phase.post.focused_test_phase" in failures


def test_class_a_and_class_b_path_sets_are_exact_and_disjoint() -> None:
    namespace = _phase_contract_namespace()
    assert namespace["CLASS_A_RECONCILIATION_PATHS"] == frozenset(
        {
            (
                "docs/continuous_delta_runtime_v0_1_"
                "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
            ),
            "specs/current_architecture_lock_v01.md",
            "specs/document_authority_index_v01.json",
            "release/successor_context_manifest_v01.json",
            "tools/check_active_architecture_authority_v01.py",
            "tests/test_active_architecture_authority_v01.py",
            "tests/test_repository_release_spine_v01.py",
        }
    )
    assert namespace["CLASS_B_E6_IMPLEMENTATION_PATHS"] == frozenset(
        {
            "demo/run_living_gauntlet_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "hedgehog/kernel/conformance_v01.py",
            "demo/run_kernel_conformance_v01.py",
            "tests/test_kernel_conformance_v01_runner.py",
        }
    )
    assert not (
        namespace["CLASS_A_RECONCILIATION_PATHS"]
        & namespace["CLASS_B_E6_IMPLEMENTATION_PATHS"]
    )
    assert namespace["G2E_CLASS_D_CLOSURE_PATHS"] == frozenset(CLASS_D_PATHS)
    assert len(namespace["G2E_CLASS_D_CLOSURE_PATHS"]) == 14
    assert not (
        namespace["G2E_CLASS_D_CLOSURE_PATHS"]
        & namespace["CLASS_B_E6_IMPLEMENTATION_PATHS"]
    )

    class_a_and_b = {
        **{
            path: "A" if path.endswith("reconciliation_addendum_v01.md") else "M"
            for path in CLASS_A_PATHS
        },
        **{path: "M" for path in CLASS_B_PATHS},
    }
    class_d_committed = {
        path: (
            "A"
            if path.startswith("docs/audit_reports/")
            or path.endswith("g2_e_checkpoint_v01.md")
            else "M"
        )
        for path in CLASS_D_PATHS
    }
    class_d_worktree = tuple(
        (
            "??" if status == "A" else " M",
            path,
            None,
        )
        for path, status in sorted(class_d_committed.items())
    )
    mode, failures = namespace["_classify_g2e_closure_path_ledger_v01"](
        closure_requested=True,
        head=G2E_CLOSURE_BASIS_COMMIT,
        parent="4c133da11b8bcbd642e1aaa3413ce0a9c357731d",
        branch="main",
        origin_main=G2E_CLOSURE_BASIS_COMMIT,
        subject="Repair G2-E6 post-successor control-plane tests",
        committed_entries=_ledger_entries(class_a_and_b),
        worktree_entries=class_d_worktree,
        closure_commit_entries=(),
    )
    assert mode == "G2E_CLOSED_PASS_CANDIDATE"
    assert failures == ()

    committed_head = "c" * 40
    mode, failures = namespace["_classify_g2e_closure_path_ledger_v01"](
        closure_requested=True,
        head=committed_head,
        parent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=committed_head,
        subject="Close G2-E continuous delta runtime lifecycle",
        committed_entries=_ledger_entries({**class_a_and_b, **class_d_committed}),
        worktree_entries=(),
        closure_commit_entries=_ledger_entries(class_d_committed),
    )
    assert mode == "G2E_CLOSED_PASS_COMMITTED"
    assert failures == ()

    _mode, missing_failures = namespace[
        "_classify_g2e_closure_path_ledger_v01"
    ](
        closure_requested=True,
        head=G2E_CLOSURE_BASIS_COMMIT,
        parent="4c133da11b8bcbd642e1aaa3413ce0a9c357731d",
        branch="main",
        origin_main=G2E_CLOSURE_BASIS_COMMIT,
        subject="Repair G2-E6 post-successor control-plane tests",
        committed_entries=_ledger_entries(class_a_and_b),
        worktree_entries=class_d_worktree[1:],
        closure_commit_entries=(),
    )
    assert any("candidate.worktree.missing" in item for item in missing_failures)

    _mode, extra_failures = namespace[
        "_classify_g2e_closure_path_ledger_v01"
    ](
        closure_requested=True,
        head=G2E_CLOSURE_BASIS_COMMIT,
        parent="4c133da11b8bcbd642e1aaa3413ce0a9c357731d",
        branch="main",
        origin_main=G2E_CLOSURE_BASIS_COMMIT,
        subject="Repair G2-E6 post-successor control-plane tests",
        committed_entries=_ledger_entries(class_a_and_b),
        worktree_entries=(*class_d_worktree, (" M", "unexpected.txt", None)),
        closure_commit_entries=(),
    )
    assert "g2e.closure.candidate.worktree.unexpected:unexpected.txt" in (
        extra_failures
    )


def test_reconciliation_annex_absence_fails_closed(
    isolated_control_plane: Path,
) -> None:
    annex = isolated_control_plane / (
        "docs/continuous_delta_runtime_v0_1_"
        "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
    )
    annex.unlink()

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "e6.class_a.control_surface.missing:" in completed.stdout
    assert "e6.annex.read:FileNotFoundError" in completed.stdout


def test_reconciliation_annex_hash_substitution_fails_closed(
    isolated_control_plane: Path,
) -> None:
    annex = isolated_control_plane / (
        "docs/continuous_delta_runtime_v0_1_"
        "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
    )
    annex.write_text(
        annex.read_text(encoding="ascii") + "\n",
        encoding="ascii",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "e6.class_a.control_surface.identity:"
        "docs/continuous_delta_runtime_v0_1_"
        "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
        in completed.stdout
    )


def test_reconciliation_annex_authority_class_mismatch_fails(
    isolated_control_plane: Path,
) -> None:
    index_path = isolated_control_plane / "specs/document_authority_index_v01.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = next(
        item
        for item in index["current_technical_annexes"]
        if item["path"].endswith("g2_e6_sanitized_basis_reconciliation_addendum_v01.md")
    )
    entry["authority_scope"] = "current_global_architecture_law"
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "e6.class_a.annex_authority_entry.exact" in completed.stdout
    assert "authority_index.global_scope_not_lock:" in completed.stdout


def test_successor_manifest_stale_e5_transplant_fact_fails(
    isolated_control_plane: Path,
) -> None:
    path = isolated_control_plane / "release/successor_context_manifest_v01.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["purpose"] += " deferred_e5_transplant"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "e6.class_a.stale_e5_current_fact:"
        "release/successor_context_manifest_v01.json:deferred_e5_transplant"
        in completed.stdout
    )


@pytest.mark.parametrize(
    ("path", "expected_failure"),
    (
        (
            "release/completion_manifest.json",
            "e6.frozen_predecessor_evidence.identity:"
            "release/completion_manifest.json",
        ),
        (
            "release/integration_seam_index.json",
            "e6.frozen_predecessor_evidence.identity:"
            "release/integration_seam_index.json",
        ),
    ),
)
def test_frozen_predecessor_indexes_cannot_become_current_e6_evidence(
    isolated_control_plane: Path,
    path: str,
    expected_failure: str,
) -> None:
    target = isolated_control_plane / path
    value = json.loads(target.read_text(encoding="utf-8"))
    value["current_e6_execution_evidence"] = True
    target.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert expected_failure in completed.stdout


def _ledger_entries(
    values: dict[str, str],
) -> tuple[tuple[str, str, None], ...]:
    return tuple((status, path, None) for path, status in sorted(values.items()))


def _class_a_worktree_entries() -> tuple[tuple[str, str, None], ...]:
    return tuple(
        (
            "??" if path.endswith("reconciliation_addendum_v01.md") else " M",
            path,
            None,
        )
        for path in sorted(CLASS_A_PATHS)
    )


def _class_b_worktree_entries() -> tuple[tuple[str, str, None], ...]:
    return tuple((" M", path, None) for path in sorted(CLASS_B_PATHS))


@pytest.mark.parametrize(
    ("head", "phase", "committed", "worktree"),
    (
        (
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            _class_a_worktree_entries(),
        ),
        (
            "a" * 40,
            "PRE_E6_RECONCILED",
            _ledger_entries(
                {
                    path: "A" if path.endswith("reconciliation_addendum_v01.md") else "M"
                    for path in CLASS_A_PATHS
                }
            ),
            (),
        ),
        (
            "a" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries(
                {
                    path: "A" if path.endswith("reconciliation_addendum_v01.md") else "M"
                    for path in CLASS_A_PATHS
                }
            ),
            _class_b_worktree_entries(),
        ),
        (
            "b" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries(
                {
                    **{
                        path: "A" if path.endswith("reconciliation_addendum_v01.md") else "M"
                        for path in CLASS_A_PATHS
                    },
                    **{path: "M" for path in CLASS_B_PATHS},
                }
            ),
            (),
        ),
    ),
)
def test_exact_phase_path_ledger_states_pass(
    head: str,
    phase: str,
    committed: tuple[tuple[str, str, None], ...],
    worktree: tuple[tuple[str, str, None], ...],
) -> None:
    namespace = _phase_contract_namespace()
    failures = namespace["_classify_phase_path_ledger_v02"](
        head=head,
        phase=phase,
        committed_entries=committed,
        worktree_entries=worktree,
    )
    assert failures == ()


def _exact_class_a_committed() -> dict[str, str]:
    return {
        path: "A" if path.endswith("reconciliation_addendum_v01.md") else "M"
        for path in CLASS_A_PATHS
    }


@pytest.mark.parametrize(
    ("case_id", "head", "phase", "committed", "worktree", "expected"),
    (
        (
            "class_a_agents",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (*_class_a_worktree_entries(), (" M", "AGENTS.md", None)),
            "worktree.unexpected_changed_path:AGENTS.md",
        ),
        (
            "class_b_agents",
            "a" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries(_exact_class_a_committed()),
            (*_class_b_worktree_entries(), (" M", "AGENTS.md", None)),
            "worktree.unexpected_changed_path:AGENTS.md",
        ),
        (
            "current_schema_extra",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (*_class_a_worktree_entries(), (" M", "release/current_schema_surface_v01.json", None)),
            "worktree.unexpected_changed_path:release/current_schema_surface_v01.json",
        ),
        (
            "retired_inventory_extra",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (*_class_a_worktree_entries(), (" M", "release/retired_architecture_inventory_v01.json", None)),
            "worktree.unexpected_changed_path:release/retired_architecture_inventory_v01.json",
        ),
        (
            "class_a_subset",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            _class_a_worktree_entries()[:-1],
            "e6.path_ledger.worktree_missing:",
        ),
        (
            "cross_class_mix",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (*_class_a_worktree_entries(), _class_b_worktree_entries()[0]),
            "worktree.unexpected_changed_path:",
        ),
        (
            "deletion",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (
                (" D", CLASS_A_PATHS[1], None),
                *tuple(row for row in _class_a_worktree_entries() if row[1] != CLASS_A_PATHS[1]),
            ),
            "e6.path_ledger.worktree_status:",
        ),
        (
            "rename",
            E5_IMPLEMENTATION_BASIS_COMMIT,
            "PRE_E6_RECONCILED",
            (),
            (
                ("R ", CLASS_A_PATHS[1], "release/renamed.json"),
                *tuple(row for row in _class_a_worktree_entries() if row[1] != CLASS_A_PATHS[1]),
            ),
            "e6.path_ledger.worktree.rename_or_copy:",
        ),
        (
            "class_a_dirty_descendant",
            "a" * 40,
            "PRE_E6_RECONCILED",
            _ledger_entries(_exact_class_a_committed()),
            _class_a_worktree_entries(),
            "worktree.unexpected_changed_path:",
        ),
        (
            "class_b_in_pre",
            "a" * 40,
            "PRE_E6_RECONCILED",
            _ledger_entries(_exact_class_a_committed()),
            _class_b_worktree_entries(),
            "worktree.unexpected_changed_path:",
        ),
        (
            "class_a_in_post",
            "a" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries(_exact_class_a_committed()),
            _class_a_worktree_entries(),
            "worktree.unexpected_changed_path:",
        ),
        (
            "clean_extra_commit",
            "b" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries({**_exact_class_a_committed(), **{path: "M" for path in CLASS_B_PATHS}, "AGENTS.md": "M"}),
            (),
            "e6.path_ledger.committed_unexpected:AGENTS.md",
        ),
        (
            "clean_missing_commit",
            "b" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries({**_exact_class_a_committed(), **{path: "M" for path in CLASS_B_PATHS[1:]}}),
            (),
            "e6.path_ledger.committed_missing:",
        ),
        (
            "clean_deleted_commit",
            "b" * 40,
            "POST_E6_SUCCESSOR",
            _ledger_entries({**_exact_class_a_committed(), **{path: "M" for path in CLASS_B_PATHS}, CLASS_B_PATHS[0]: "D"}),
            (),
            "e6.path_ledger.committed_status:",
        ),
        (
            "clean_rename_commit",
            "b" * 40,
            "POST_E6_SUCCESSOR",
            (
                *_ledger_entries({**_exact_class_a_committed(), **{path: "M" for path in CLASS_B_PATHS[1:]}}),
                ("R100", CLASS_B_PATHS[0], "demo/old_living.py"),
            ),
            (),
            "e6.path_ledger.committed.rename_or_copy:",
        ),
    ),
)
def test_phase_path_ledger_rejects_every_partial_or_cross_class_state(
    case_id: str,
    head: str,
    phase: str,
    committed: tuple[tuple[str, str, str | None], ...],
    worktree: tuple[tuple[str, str, str | None], ...],
    expected: str,
) -> None:
    del case_id
    namespace = _phase_contract_namespace()
    failures = namespace["_classify_phase_path_ledger_v02"](
        head=head,
        phase=phase,
        committed_entries=committed,
        worktree_entries=worktree,
    )
    assert any(item.startswith(expected) for item in failures), failures


def _post_contract_source(
    *,
    living: bool,
    transparent_spy: bool = False,
    module_import: bool = False,
) -> str:
    namespace = _phase_contract_namespace()
    function_name = (
        namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
        if living
        else namespace["POST_E6_CONFORMANCE_ACCEPTANCE_TEST"]
    )
    collector = (
        "collect_living_gauntlet_v01"
        if living
        else "collect_kernel_conformance_v01"
    )
    validator = (
        "validate_living_gauntlet_report_v01"
        if living
        else "validate_kernel_conformance_runtime_v01"
    )
    public_module = (
        "demo.run_living_gauntlet_v01"
        if living
        else "demo.run_kernel_conformance_v01"
    )
    fixed_fields = namespace["POST_E6_SHARED_FIXED_REPORT_VALUES"]
    hash_fields = namespace["POST_E6_SHARED_SHA256_FIELDS"]
    byte_fields = namespace["POST_E6_SHARED_BYTE_COUNT_FIELDS"]
    if living:
        geometry_assertions = (
            "    assert report['runner_version'] == 'v1.6'",
            "    assert report['kernel_conformance_profile'] == "
            + repr(namespace["POST_E6_PROFILE_ID"]),
            "    assert report['historical_kernel_conformance_profile'] == "
            + repr(namespace["POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID"]),
            "    assert tuple(row['act_id'] for row in "
            "report['active_act_results']) == "
            + repr(namespace["POST_E6_LIVING_ACT_IDS"]),
        )
    else:
        geometry_assertions = (
            "    assert report.conformance_version == 'v0.7'",
            "    assert report.profile_id == "
            + repr(namespace["POST_E6_PROFILE_ID"]),
            "    assert report.historical_profile_ref == "
            + repr(namespace["POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID"]),
            "    assert tuple(item.category_id for item in "
            "report.category_results) == "
            + repr(
                tuple(
                    item[0]
                    for item in namespace["POST_E6_CATEGORY_CHECK_IDS"]
                )
            ),
            "    assert tuple((item.category_id, item.required_check_ids) "
            "for item in report.category_results) == "
            + repr(namespace["POST_E6_CATEGORY_CHECK_IDS"]),
            "    assert tuple(item.probe_id for item in "
            "report.negative_test_results) == "
            + repr(namespace["POST_E6_NEGATIVE_PROBE_IDS"]),
            "    assert report.active_gauntlet_refs == "
            + repr(namespace["POST_E6_ACTIVE_REFS"]),
            "    assert tuple(item.domain_id for item in "
            "report.domain_results) == "
            + repr(namespace["PRESERVED_DOMAIN_IDS"]),
        )
    access = (
        (lambda field: f"report[{field!r}]")
        if living
        else (lambda field: f"report.{field}")
    )
    setup = ""
    call = collector if not module_import else f"public_runner.{collector}"
    validation_call = (
        validator if not module_import else f"public_runner.{validator}"
    )
    if transparent_spy:
        setup = textwrap.indent(
            f"""calls = []
def counted_collector(*args, **kwargs):
    exact_return = {call}(*args, **kwargs)
    calls.append(exact_return)
    return exact_return
""",
            "    ",
        )
        call = "counted_collector"
    assertions = [
        "    assert validation == ()",
        *(
            f"    assert {access(field)} == {expected!r}"
            for field, expected in fixed_fields
        ),
        f"    assert {access(hash_fields[0])} == {access(hash_fields[1])}",
        *(f"    assert len({access(field)}) == 64" for field in hash_fields),
        *(
            f"    assert set({access(field)}) <= set('0123456789abcdef')"
            for field in hash_fields
        ),
        f"    assert {access(byte_fields[0])} == {access(byte_fields[1])}",
        *(f"    assert {access(field)} > 0" for field in byte_fields),
        *geometry_assertions,
    ]
    import_line = (
        f"from {public_module} import {collector}, {validator}"
        if not module_import
        else f"import {public_module} as public_runner"
    )
    return (
        f"{import_line}\n\n"
        f"def {function_name}():\n"
        f"{setup}"
        f"    report = {call}()\n"
        f"    validation = {validation_call}(report)\n"
        + "\n".join(assertions)
        + "\n"
    )


@pytest.mark.parametrize("living", (True, False))
def test_structurally_valid_future_acceptance_contract_passes(
    tmp_path: Path,
    living: bool,
) -> None:
    path = tmp_path / "future_test.py"
    path.write_text(_post_contract_source(living=living), encoding="utf-8")
    namespace = _phase_contract_namespace()
    assert namespace["_validate_post_e6_test_contract_v02"](
        path, living=living
    ) == ()


@pytest.mark.parametrize("living", (True, False))
def test_transparent_delegating_count_spy_preserves_future_contract(
    tmp_path: Path,
    living: bool,
) -> None:
    path = tmp_path / "future_spy_test.py"
    path.write_text(
        _post_contract_source(living=living, transparent_spy=True),
        encoding="utf-8",
    )
    namespace = _phase_contract_namespace()
    assert namespace["_validate_post_e6_test_contract_v02"](
        path, living=living
    ) == ()


def _aliased_post_contract_source(*, living: bool, transparent_spy: bool = False) -> str:
    namespace = _phase_contract_namespace()
    collector = (
        "collect_living_gauntlet_v01"
        if living
        else "collect_kernel_conformance_v01"
    )
    validator = (
        "validate_living_gauntlet_report_v01"
        if living
        else "validate_kernel_conformance_runtime_v01"
    )
    public_module = (
        "demo.run_living_gauntlet_v01"
        if living
        else "demo.run_kernel_conformance_v01"
    )
    source = _post_contract_source(
        living=living,
        transparent_spy=transparent_spy,
    )
    source = source.replace(
        f"from {public_module} import {collector}, {validator}",
        f"from {public_module} import {collector} as c, {validator} as v",
        1,
    )
    source = source.replace(f"{collector}(", "c(")
    source = source.replace(f"{validator}(", "v(")
    function_name = (
        namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
        if living
        else namespace["POST_E6_CONFORMANCE_ACCEPTANCE_TEST"]
    )
    assert f"def {function_name}():" in source
    return source


@pytest.mark.parametrize("living", (True, False))
@pytest.mark.parametrize(
    "mutation",
    (
        "collector_assign",
        "collector_annassign",
        "collector_namedexpr",
        "collector_augassign",
        "collector_delete",
        "validator_assign",
        "collector_def",
        "collector_async_def",
        "validator_class",
        "positional_only_parameter",
        "positional_parameter",
        "keyword_parameter",
        "vararg_parameter",
        "kwarg_parameter",
        "for_target",
        "comprehension_target",
        "with_target",
        "except_target",
        "module_alias_rebound",
        "module_attribute_replaced",
        "module_subscript_replaced",
        "module_alias_attribute_replaced",
        "module_vars_subscript_replaced",
        "module_dict_updated",
        "module_unknown_escape",
        "transparent_spy_alias_shadowed",
        "transparent_spy_name_rebound",
    ),
)
def test_public_collector_validator_alias_shadowing_fails_closed(
    tmp_path: Path,
    living: bool,
    mutation: str,
) -> None:
    namespace = _phase_contract_namespace()
    function_name = (
        namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
        if living
        else namespace["POST_E6_CONFORMANCE_ACCEPTANCE_TEST"]
    )
    collector = (
        "collect_living_gauntlet_v01"
        if living
        else "collect_kernel_conformance_v01"
    )
    baseline = _aliased_post_contract_source(living=living)
    if mutation in {
        "module_alias_rebound",
        "module_attribute_replaced",
        "module_subscript_replaced",
        "module_alias_attribute_replaced",
        "module_vars_subscript_replaced",
        "module_dict_updated",
        "module_unknown_escape",
    }:
        baseline = _post_contract_source(living=living, module_import=True)
    elif mutation == "transparent_spy_alias_shadowed":
        baseline = _aliased_post_contract_source(
            living=living,
            transparent_spy=True,
        )
    elif mutation == "transparent_spy_name_rebound":
        baseline = _post_contract_source(living=living, transparent_spy=True)
    baseline_path = tmp_path / f"baseline_{living}_{mutation}.py"
    baseline_path.write_text(baseline, encoding="utf-8")
    assert namespace["_validate_post_e6_test_contract_v02"](
        baseline_path, living=living
    ) == ()

    marker = f"def {function_name}():"
    if mutation == "collector_assign":
        source = baseline.replace(marker, marker + "\n    c = lambda: {}", 1)
    elif mutation == "collector_annassign":
        source = baseline.replace(
            marker, marker + "\n    c: object = lambda: {}", 1
        )
    elif mutation == "collector_namedexpr":
        source = baseline.replace(
            marker, marker + "\n    (c := lambda: {})", 1
        )
    elif mutation == "collector_augassign":
        source = baseline.replace(marker, marker + "\n    c += ()", 1)
    elif mutation == "collector_delete":
        source = baseline.replace(marker, marker + "\n    del c", 1)
    elif mutation == "validator_assign":
        source = baseline.replace(marker, marker + "\n    v = lambda report: ()", 1)
    elif mutation == "collector_def":
        source = baseline.replace(marker, marker + "\n    def c():\n        return {}", 1)
    elif mutation == "collector_async_def":
        source = baseline.replace(
            marker, marker + "\n    async def c():\n        return {}", 1
        )
    elif mutation == "validator_class":
        source = baseline.replace(marker, marker + "\n    class v:\n        pass", 1)
    elif mutation == "positional_only_parameter":
        source = baseline.replace(marker, f"def {function_name}(c, /):", 1)
    elif mutation == "positional_parameter":
        source = baseline.replace(marker, f"def {function_name}(c):", 1)
    elif mutation == "keyword_parameter":
        source = baseline.replace(marker, f"def {function_name}(*, v):", 1)
    elif mutation == "vararg_parameter":
        source = baseline.replace(marker, f"def {function_name}(*c):", 1)
    elif mutation == "kwarg_parameter":
        source = baseline.replace(marker, f"def {function_name}(**v):", 1)
    elif mutation == "for_target":
        source = baseline.replace(
            marker, marker + "\n    for c in ():\n        pass", 1
        )
    elif mutation == "comprehension_target":
        source = baseline.replace(marker, marker + "\n    tuple(c for c in ())", 1)
    elif mutation == "with_target":
        source = baseline.replace(
            marker, marker + "\n    with manager() as c:\n        pass", 1
        )
    elif mutation == "except_target":
        source = baseline.replace(
            marker,
            marker
            + "\n    try:\n        pass\n    except Exception as c:\n        pass",
            1,
        )
    elif mutation == "module_alias_rebound":
        source = baseline.replace(
            "\ndef ", "\npublic_runner = fabricated_runner\n\ndef ", 1
        )
    elif mutation == "module_attribute_replaced":
        source = baseline.replace(
            marker,
            marker + f"\n    public_runner.{collector} = lambda: {{}}",
            1,
        )
    elif mutation == "module_subscript_replaced":
        source = baseline.replace(
            marker,
            marker + f"\n    public_runner[{collector!r}] = lambda: {{}}",
            1,
        )
    elif mutation == "module_alias_attribute_replaced":
        source = baseline.replace(
            marker,
            marker
            + f"\n    runner_alias = public_runner\n"
            f"    runner_alias.{collector} = lambda: {{}}",
            1,
        )
    elif mutation == "module_vars_subscript_replaced":
        source = baseline.replace(
            marker,
            marker
            + f"\n    vars(public_runner)[{collector!r}] = lambda: {{}}",
            1,
        )
    elif mutation == "module_dict_updated":
        source = baseline.replace(
            marker,
            marker
            + f"\n    public_runner.__dict__.update("
            f"{{{collector!r}: lambda: {{}}}})",
            1,
        )
    elif mutation == "module_unknown_escape":
        source = baseline.replace(
            marker,
            marker + "\n    mutate_module(public_runner)",
            1,
        )
    elif mutation == "transparent_spy_alias_shadowed":
        source = baseline.replace(
            "        exact_return = c(*args, **kwargs)",
            "        c = lambda *args, **kwargs: {}\n"
            "        exact_return = c(*args, **kwargs)",
            1,
        )
    else:
        source = baseline.replace(
            "    report = counted_collector()",
            "    counted_collector = lambda: {}\n"
            "    report = counted_collector()",
            1,
        )
    hostile_path = tmp_path / f"hostile_{living}_{mutation}.py"
    hostile_path.write_text(source, encoding="utf-8")
    failures = namespace["_validate_post_e6_test_contract_v02"](
        hostile_path, living=living
    )
    assert any(item.endswith(".public_surface_shadowed") for item in failures), (
        mutation,
        failures,
    )


@pytest.mark.parametrize("living", (True, False))
@pytest.mark.parametrize(
    ("mutation", "expected_suffix"),
    (
        ("fixed_literal_self_comparison", ".shared_field_contract:continuous_delta_runtime_execution_count"),
        ("geometry_self_comparison", ".geometry_field_contract:"),
        ("truthy_boolean_packing", ".tautological_assertion"),
        ("valid_proof_or_true", ".nonflat_assertion"),
        ("disconnected_required_field", ".shared_field_contract:continuous_delta_runtime_execution_count"),
        ("disconnected_geometry_wrapper", ".geometry_field_contract:"),
        ("validation_self_instead_of_success", ".validation_success_contract"),
    ),
)
def test_post_e6_assertions_require_operand_linked_actual_return_proof(
    tmp_path: Path,
    living: bool,
    mutation: str,
    expected_suffix: str,
) -> None:
    namespace = _phase_contract_namespace()
    baseline = _post_contract_source(living=living)
    baseline_path = tmp_path / f"assertion_baseline_{living}_{mutation}.py"
    baseline_path.write_text(baseline, encoding="utf-8")
    assert namespace["_validate_post_e6_test_contract_v02"](
        baseline_path, living=living
    ) == ()

    function_name = (
        namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
        if living
        else namespace["POST_E6_CONFORMANCE_ACCEPTANCE_TEST"]
    )
    marker = f"def {function_name}():"
    fixed_access = (
        "report['continuous_delta_runtime_execution_count']"
        if living
        else "report.continuous_delta_runtime_execution_count"
    )
    geometry_line = (
        "    assert report['runner_version'] == 'v1.6'"
        if living
        else "    assert report.conformance_version == 'v0.7'"
    )
    if mutation == "fixed_literal_self_comparison":
        source = baseline.replace(
            f"    assert {fixed_access} == 1",
            "    assert 1 == 1",
            1,
        )
    elif mutation == "geometry_self_comparison":
        literal = "'v1.6'" if living else "'v0.7'"
        source = baseline.replace(
            geometry_line,
            f"    assert {literal} == {literal}",
            1,
        )
    elif mutation == "truthy_boolean_packing":
        source = baseline.replace(
            f"    assert {fixed_access} == 1",
            "    assert 1 == 1 and ('required', 'geometry')",
            1,
        )
    elif mutation == "valid_proof_or_true":
        source = baseline.replace(
            f"    assert {fixed_access} == 1",
            f"    assert {fixed_access} == 1 or True",
            1,
        )
    elif mutation == "disconnected_required_field":
        source = baseline.replace(
            f"    assert {fixed_access} == 1",
            "    assert report['unrelated'] == 1"
            if living
            else "    assert report.unrelated == 1",
            1,
        )
    elif mutation == "disconnected_geometry_wrapper":
        expected = "'v1.6'" if living else "'v0.7'"
        report_access = (
            "report['runner_version']"
            if living
            else "report.conformance_version"
        )
        source = baseline.replace(
            geometry_line,
            f"    assert ({report_access}, {expected})[1] == {expected}",
            1,
        )
    else:
        source = baseline.replace(
            "    assert validation == ()",
            "    assert validation is validation",
            1,
        )
    assert source != baseline
    hostile_path = tmp_path / f"assertion_hostile_{living}_{mutation}.py"
    hostile_path.write_text(source, encoding="utf-8")
    failures = namespace["_validate_post_e6_test_contract_v02"](
        hostile_path, living=living
    )
    assert any(
        expected_suffix in item for item in failures
    ), (mutation, failures)


@pytest.mark.parametrize("living", (True, False))
@pytest.mark.parametrize(
    "mutation",
    (
        "report_reassigned",
        "report_subscript_mutated",
        "report_unknown_escape",
        "validation_reassigned",
    ),
)
def test_post_e6_actual_return_lineage_cannot_be_rebound_or_escaped(
    tmp_path: Path,
    living: bool,
    mutation: str,
) -> None:
    namespace = _phase_contract_namespace()
    baseline = _post_contract_source(living=living)
    baseline_path = tmp_path / f"lineage_baseline_{living}_{mutation}.py"
    baseline_path.write_text(baseline, encoding="utf-8")
    assert namespace["_validate_post_e6_test_contract_v02"](
        baseline_path, living=living
    ) == ()
    validation_line = (
        "    validation = validate_living_gauntlet_report_v01(report)"
        if living
        else "    validation = validate_kernel_conformance_runtime_v01(report)"
    )
    if mutation == "report_reassigned":
        source = baseline.replace(
            validation_line,
            "    report = fabricated_report\n" + validation_line,
            1,
        )
    elif mutation == "report_subscript_mutated":
        source = baseline.replace(
            validation_line,
            "    report['forged'] = True\n" + validation_line,
            1,
        )
    elif mutation == "report_unknown_escape":
        source = baseline.replace(
            validation_line,
            "    mutate_report(report)\n" + validation_line,
            1,
        )
    else:
        source = baseline.replace(
            "    assert validation == ()",
            "    validation = ()\n    assert validation == ()",
            1,
        )
    hostile_path = tmp_path / f"lineage_hostile_{living}_{mutation}.py"
    hostile_path.write_text(source, encoding="utf-8")
    failures = namespace["_validate_post_e6_test_contract_v02"](
        hostile_path, living=living
    )
    assert any(item.endswith(".actual_return_lineage") for item in failures), (
        living,
        mutation,
        failures,
    )


@pytest.mark.parametrize("living", (True, False))
def test_post_e6_expected_module_constant_cannot_be_shadowed(
    tmp_path: Path,
    living: bool,
) -> None:
    namespace = _phase_contract_namespace()
    literal = "'v1.6'" if living else "'v0.7'"
    source = _post_contract_source(living=living).replace(
        f" == {literal}",
        " == EXPECTED_SUCCESSOR_VERSION",
        1,
    )
    source = f"EXPECTED_SUCCESSOR_VERSION = {literal}\n" + source
    baseline_path = tmp_path / f"constant_baseline_{living}.py"
    baseline_path.write_text(source, encoding="utf-8")
    assert namespace["_validate_post_e6_test_contract_v02"](
        baseline_path, living=living
    ) == ()
    hostile = source + "EXPECTED_SUCCESSOR_VERSION = dynamic_version()\n"
    hostile_path = tmp_path / f"constant_hostile_{living}.py"
    hostile_path.write_text(hostile, encoding="utf-8")
    failures = namespace["_validate_post_e6_test_contract_v02"](
        hostile_path, living=living
    )
    assert any(".geometry_field_contract:" in item for item in failures), failures


@pytest.mark.parametrize(
    "mutation",
    (
        "dead_literals_only",
        "no_function",
        "unused_constant",
        "pass_only",
        "assert_true",
        "if_false",
        "after_return",
        "empty_parametrize",
        "skip",
        "xfail",
        "fabricated_report",
        "stubbed_spy",
        "monkeypatch_substitution",
        "patch_substitution",
        "mock_substitution",
        "wrong_public_import",
        "module_fabricated_collector",
        "fabricated_validator",
        "duplicate_collector",
        "duplicate_validator",
        "module_xfail",
        "mutating_spy",
        "missing_collector",
        "missing_validator",
        "missing_actual_return_assertion",
    ),
)
def test_future_acceptance_contract_rejects_dead_or_fabricated_evidence(
    tmp_path: Path,
    mutation: str,
) -> None:
    namespace = _phase_contract_namespace()
    function_name = namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
    valid = _post_contract_source(living=True)
    if mutation == "dead_literals_only":
        source = "def test_old():\n    assert True\n\n" + repr(("v1.6", "continuous_delta_runtime"))
    elif mutation == "no_function":
        source = "VALUE = 'v1.6'\n"
    elif mutation == "unused_constant":
        source = f"def {function_name}():\n    value = 'v1.6'\n    assert value\n"
    elif mutation == "pass_only":
        source = f"def {function_name}():\n    pass\n"
    elif mutation == "assert_true":
        source = valid + "\n"
        source = source.replace("    report =", "    assert True\n    report =", 1)
    elif mutation == "if_false":
        source = f"def {function_name}():\n    if False:\n        report = collect_living_gauntlet_v01()\n"
    elif mutation == "after_return":
        source = valid.replace("    report =", "    return\n    report =", 1)
    elif mutation == "empty_parametrize":
        source = "@pytest.mark.parametrize('value', ())\n" + valid
    elif mutation == "skip":
        source = "@pytest.mark.skip\n" + valid
    elif mutation == "xfail":
        source = "@pytest.mark.xfail\n" + valid
    elif mutation == "fabricated_report":
        source = valid.replace(
            "report = collect_living_gauntlet_v01()", "report = {'status': 'PASS'}"
        )
    elif mutation == "stubbed_spy":
        source = valid.replace(
            "    report = collect_living_gauntlet_v01()\n",
            "    def fake_collector():\n        return {'status': 'PASS'}\n    report = fake_collector()\n",
        )
    elif mutation == "monkeypatch_substitution":
        source = valid.replace(
            "    report =",
            "    monkeypatch.setattr(module, 'collect', lambda: {})\n    report =",
            1,
        )
    elif mutation == "patch_substitution":
        source = valid.replace(
            "    report =",
            "    patched = patch('collector', return_value={})\n    report =",
            1,
        )
    elif mutation == "mock_substitution":
        source = valid.replace(
            "    report =",
            "    replacement = Mock(return_value={})\n    report =",
            1,
        )
    elif mutation == "wrong_public_import":
        source = valid.replace(
            "from demo.run_living_gauntlet_v01 import",
            "from fabricated.runner import",
            1,
        )
    elif mutation == "module_fabricated_collector":
        source = valid.replace(
            "\ndef ",
            "\ncollect_living_gauntlet_v01 = lambda: {'status': 'PASS'}\n\ndef ",
            1,
        )
    elif mutation == "fabricated_validator":
        source = valid.replace(
            "    report =",
            "    def validate_living_gauntlet_report_v01(_report):\n        return ()\n    report =",
            1,
        )
    elif mutation == "duplicate_collector":
        source = valid.replace(
            "    report =",
            "    extra_report = collect_living_gauntlet_v01()\n    report =",
            1,
        )
    elif mutation == "duplicate_validator":
        source = valid.replace(
            "    assert validation == ()",
            "    validate_living_gauntlet_report_v01(report)\n    assert validation == ()",
            1,
        )
    elif mutation == "module_xfail":
        source = "pytestmark = pytest.mark.xfail\n" + valid
    elif mutation == "mutating_spy":
        source = _post_contract_source(living=True, transparent_spy=True).replace(
            "    calls.append(exact_return)",
            "    exact_return = {'status': 'PASS'}",
            1,
        )
    elif mutation == "missing_collector":
        source = valid.replace("report = collect_living_gauntlet_v01()", "report = {}")
    elif mutation == "missing_validator":
        source = valid.replace(
            "    validation = validate_living_gauntlet_report_v01(report)\n", ""
        )
    else:
        source = valid.replace(
            "    assert report['continuous_delta_runtime_execution_count'] == 1",
            "    assert 1 == 1",
            1,
        )
    path = tmp_path / "invalid_future_test.py"
    path.write_text(source, encoding="utf-8")
    failures = namespace["_validate_post_e6_test_contract_v02"](
        path, living=True
    )
    assert failures, mutation


def _critical_extract(
    tmp_path: Path,
    source: str,
    names: frozenset[str],
) -> tuple[dict[str, object], dict[str, ast.AST], tuple[str, ...]]:
    path = tmp_path / "critical.py"
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    failures: list[str] = []
    namespace = _phase_contract_namespace()
    values, nodes, _tree, _source = namespace["_phase_critical_assignments_v02"](
        path, "hostile.critical", names, failures
    )
    return values, nodes, tuple(failures)


@pytest.mark.parametrize(
    "source",
    (
        'RUNNER_VERSION = "v0.7"\nRUNNER_VERSION = os.getenv("VERSION")\n',
        'RUNNER_VERSION = "v0.7"\nRUNNER_VERSION = "v0.7"\n',
        'RUNNER_VERSION = "v0.7"\nif condition:\n    RUNNER_VERSION = "v0.6"\n',
        'RUNNER_VERSION = "v0.7"\nimport os as RUNNER_VERSION\n',
        'RUNNER_VERSION = "v0.7"\nglobals()["RUNNER_VERSION"] = "v0.6"\n',
        'RUNNER_VERSION = "v0.7"\nexec("RUNNER_VERSION = \'v0.6\'")\n',
        'RUNNER_VERSION = "v0.7"\nRUNNER_VERSION += "x"\n',
        'RUNNER_VERSION = "v0.7"\nvalue = (RUNNER_VERSION := "v0.6")\n',
    ),
)
def test_phase_critical_scalar_shadowing_fails(
    tmp_path: Path,
    source: str,
) -> None:
    _values, _nodes, failures = _critical_extract(
        tmp_path, source, frozenset({"RUNNER_VERSION"})
    )
    assert failures


@pytest.mark.parametrize(
    ("name", "good", "bad"),
    (
        ("PROFILE", '"kernel_conformance_v0_7_current"', "dynamic()"),
        ("DEFAULT_PROFILE", "PROFILE", "os.getenv('PROFILE')"),
        ("ACTIVE_IDS", "('a', 'b')", "['a', 'b']"),
        ("ACTIVE_SOURCES", "{'a': ('m', 'f')}", "dict(dynamic())"),
    ),
)
def test_phase_critical_reference_tuple_and_dict_shadowing_fails(
    tmp_path: Path,
    name: str,
    good: str,
    bad: str,
) -> None:
    prefix = 'PROFILE = "kernel_conformance_v0_7_current"\n' if name == "DEFAULT_PROFILE" else ""
    source = f"{prefix}{name} = {good}\nif condition:\n    {name} = {bad}\n"
    _values, _nodes, failures = _critical_extract(
        tmp_path, source, frozenset({name})
    )
    assert failures


MUTABLE_CRITICAL_SURFACES = (
    ("kernel_conformance_runner", "_ACT_SOURCES"),
    ("living_gauntlet", "_ACTIVE_ACT_SOURCES"),
    ("living_gauntlet", "_CURRENT_SEAMS"),
    ("living_gauntlet", "_HISTORICAL_SEAMS"),
)


def test_mutable_phase_critical_surface_census_is_exact() -> None:
    namespace = _phase_contract_namespace()
    specifications = (
        (
            "kernel_conformance",
            REPOSITORY_ROOT / "hedgehog/kernel/conformance_v01.py",
            namespace["CORE_PHASE_CRITICAL_NAMES"],
        ),
        (
            "kernel_conformance_runner",
            REPOSITORY_ROOT / "demo/run_kernel_conformance_v01.py",
            namespace["RUNNER_PHASE_CRITICAL_NAMES"],
        ),
        (
            "living_gauntlet",
            REPOSITORY_ROOT / "demo/run_living_gauntlet_v01.py",
            namespace["LIVING_PHASE_CRITICAL_NAMES"],
        ),
    )
    actual: list[tuple[str, str]] = []
    for label, path, names in specifications:
        failures: list[str] = []
        values, _nodes, _tree, _source = namespace[
            "_phase_critical_assignments_v02"
        ](path, f"census.{label}", names, failures)
        assert failures == []
        actual.extend(
            (label, name)
            for name, value in values.items()
            if type(value) in {dict, list, set}
        )
    assert tuple(sorted(actual)) == tuple(sorted(MUTABLE_CRITICAL_SURFACES))


@pytest.mark.parametrize(("surface", "binding"), MUTABLE_CRITICAL_SURFACES)
@pytest.mark.parametrize(
    "mutation",
    (
        "subscript_assignment",
        "subscript_deletion",
        "update",
        "setdefault",
        "pop",
        "clear",
        "in_place_union",
        "alias_update",
        "bound_method_alias",
        "helper_parameter_mutation",
        "unbound_method_mutation",
        "operator_setitem",
        "unknown_call_escape",
        "shadowed_read_only_name",
        "direct_return_escape",
    ),
)
def test_mutable_phase_critical_bindings_fail_closed(
    tmp_path: Path,
    surface: str,
    binding: str,
    mutation: str,
) -> None:
    del surface
    baseline = f"{binding} = {{'stable': ('module', 'symbol')}}\n"
    _values, _nodes, baseline_failures = _critical_extract(
        tmp_path, baseline, frozenset({binding})
    )
    assert baseline_failures == (), (binding, baseline_failures)
    statements = {
        "subscript_assignment": f"{binding}['evil'] = ('x', 'y')\n",
        "subscript_deletion": f"del {binding}['stable']\n",
        "update": f"{binding}.update({{'evil': ('x', 'y')}})\n",
        "setdefault": f"{binding}.setdefault('evil', ('x', 'y'))\n",
        "pop": f"{binding}.pop('stable')\n",
        "clear": f"{binding}.clear()\n",
        "in_place_union": f"{binding} |= {{'evil': ('x', 'y')}}\n",
        "alias_update": (
            f"alias = {binding}\n"
            "alias.update({'evil': ('x', 'y')})\n"
        ),
        "bound_method_alias": (
            f"mutator = {binding}.update\n"
            "mutator({'evil': ('x', 'y')})\n"
        ),
        "helper_parameter_mutation": (
            "def mutate(value):\n"
            "    value.update({'evil': ('x', 'y')})\n"
            f"mutate({binding})\n"
        ),
        "unbound_method_mutation": (
            f"dict.update({binding}, {{'evil': ('x', 'y')}})\n"
        ),
        "operator_setitem": (
            f"operator.setitem({binding}, 'evil', ('x', 'y'))\n"
        ),
        "unknown_call_escape": f"unknown_mutator({binding})\n",
        "shadowed_read_only_name": (
            "def dict(value):\n"
            "    value.update({'evil': ('x', 'y')})\n"
            f"dict({binding})\n"
        ),
        "direct_return_escape": (
            "def expose():\n"
            f"    return {binding}\n"
            "expose()\n"
        ),
    }
    _values, _nodes, failures = _critical_extract(
        tmp_path,
        baseline + statements[mutation],
        frozenset({binding}),
    )
    assert any(".mutable_" in item for item in failures), (
        binding,
        mutation,
        failures,
    )


def _historical_scan_failures(
    source: str,
    *,
    label: str = "living_gauntlet",
    allowed: frozenset[str] | None = None,
) -> tuple[str, ...]:
    namespace = _phase_contract_namespace()
    if allowed is None:
        allowed = namespace["_historical_module_bindings_v03"](label)
    failures: list[str] = []
    namespace["_validate_historical_non_rebinding_v02"](
        ast.parse(textwrap.dedent(source)),
        label=label,
        allowed_evidence_assignments=allowed,
        failures=failures,
    )
    return tuple(failures)


HISTORICAL_SURFACE_PATHS = {
    "kernel_conformance": REPOSITORY_ROOT / "hedgehog/kernel/conformance_v01.py",
    "kernel_conformance_runner": (
        REPOSITORY_ROOT / "demo/run_kernel_conformance_v01.py"
    ),
    "living_gauntlet": REPOSITORY_ROOT / "demo/run_living_gauntlet_v01.py",
}
HISTORICAL_PRIMARY_BINDINGS = {
    "kernel_conformance": "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS",
    "kernel_conformance_runner": "_V05_HISTORICAL_BASE_ACT_IDS",
    "living_gauntlet": "_HISTORICAL_SEAMS",
}


def _historical_surface_source(label: str, phase: str) -> str:
    path = HISTORICAL_SURFACE_PATHS[label]
    if phase == "PRE_E6_RECONCILED":
        relative_path = path.relative_to(REPOSITORY_ROOT).as_posix()
        completed = subprocess.run(
            (
                "git",
                "show",
                f"{E5_IMPLEMENTATION_BASIS_COMMIT}:{relative_path}",
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout
    source = path.read_text(encoding="utf-8")
    if phase == "POST_E6_SUCCESSOR":
        source += '\n_SYNTHETIC_GUARD_PHASE_V03 = "POST_E6_SUCCESSOR"\n'
    return source


def test_historical_evidence_structural_allowlist_is_exact() -> None:
    namespace = _phase_contract_namespace()
    assert namespace["HISTORICAL_EVIDENCE_STRUCTURAL_ALLOWLIST_V03"] == (
        (
            "kernel_conformance",
            "module",
            "binding:_GATE1_ACTIVE_GAUNTLET_REFS_V01",
        ),
        (
            "kernel_conformance",
            "module",
            "binding:_G2A_ACTIVE_GAUNTLET_REFS_V02",
        ),
        (
            "kernel_conformance",
            "module",
            "binding:_G2B_ACTIVE_GAUNTLET_REFS_V03",
        ),
        (
            "kernel_conformance",
            "module",
            "binding:_G2C_ACTIVE_GAUNTLET_REFS_V04",
        ),
        (
            "kernel_conformance",
            "module",
            "binding:_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS",
        ),
        (
            "kernel_conformance",
            "function:kernel_conformance_profile_metadata_v01",
            "return_field:historical_act_id",
        ),
        (
            "kernel_conformance_runner",
            "module",
            "binding:_V05_HISTORICAL_BASE_ACT_IDS",
        ),
        (
            "living_gauntlet",
            "module",
            "binding:HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05",
        ),
        (
            "living_gauntlet",
            "module",
            "binding:_EVIDENCE_ONLY_ACT_IDS",
        ),
        (
            "living_gauntlet",
            "module",
            "binding:_HISTORICAL_EVIDENCE_ACT_IDS",
        ),
        (
            "living_gauntlet",
            "module",
            "binding:_HISTORICAL_SEAMS",
        ),
        (
            "living_gauntlet",
            "function:_validate_completion_manifest_v01",
            "binding:expected_profiles.historical_v0_5.historical_act_id",
        ),
    )


@pytest.mark.parametrize("label", tuple(HISTORICAL_SURFACE_PATHS))
def test_exact_historical_evidence_fields_remain_inert_and_accepted(
    label: str,
) -> None:
    source = _historical_surface_source(label, "PRE_E6_RECONCILED")
    assert _historical_scan_failures(source, label=label) == ()
    binding = HISTORICAL_PRIMARY_BINDINGS[label]
    inert = source + (
        "\nimport json\n"
        "def _serialize_historical_evidence_v03():\n"
        f"    return json.dumps({binding})\n"
    )
    assert _historical_scan_failures(inert, label=label) == ()


@pytest.mark.parametrize("label", tuple(HISTORICAL_SURFACE_PATHS))
@pytest.mark.parametrize(
    ("mutation", "expected_family"),
    (
        ("direct_execution", ".tainted_import"),
        ("get_execution", ".tainted_import"),
        ("alias_execution", ".tainted_import"),
        ("shadowed_read_only_execution", ".tainted_import"),
        ("current_registry", ".tainted_current_binding"),
        ("arbitrary_historical_field", ".literal_rebound"),
    ),
)
def test_historical_evidence_taint_cannot_reenter_execution(
    label: str,
    mutation: str,
    expected_family: str,
) -> None:
    baseline = _historical_surface_source(label, "PRE_E6_RECONCILED")
    assert _historical_scan_failures(baseline, label=label) == ()
    binding = HISTORICAL_PRIMARY_BINDINGS[label]
    if label == "living_gauntlet":
        direct_extract = (
            f"material = {binding}\n"
            "    module_name, symbol_name = material["
            "'all_layers_invariant_super_smoke_collector']\n"
        )
        get_extract = (
            f"evidence = {{'entry': {binding}}}\n"
            "    material = evidence.get('entry')\n"
            "    module_name, symbol_name = material.get("
            "'all_layers_invariant_super_smoke_collector')\n"
        )
    else:
        direct_extract = (
            f"material = {binding}\n"
            "    module_name = material[-1]\n"
            "    symbol_name = material[-1]\n"
        )
        get_extract = (
            f"evidence = {{'entry': {binding}}}\n"
            "    material = evidence.get('entry')\n"
            "    module_name = material[-1]\n"
            "    symbol_name = material[-1]\n"
        )
    executable_tail = (
        "    legacy = importlib.import_module(module_name)\n"
        "    runner = getattr(legacy, symbol_name)\n"
        "    return runner()\n"
    )
    if mutation == "direct_execution":
        addition = "\ndef _hostile_v03():\n    " + direct_extract + executable_tail
    elif mutation == "get_execution":
        addition = "\ndef _hostile_v03():\n    " + get_extract + executable_tail
    elif mutation == "alias_execution":
        addition = (
            "\ndef _hostile_v03():\n"
            f"    evidence = {binding}\n"
            "    alias = evidence\n"
            "    module_name = alias[-1] if not isinstance(alias, dict) "
            "else alias['all_layers_invariant_super_smoke_collector'][0]\n"
            "    symbol_name = alias[-1] if not isinstance(alias, dict) "
            "else alias['all_layers_invariant_super_smoke_collector'][1]\n"
            + executable_tail
        )
    elif mutation == "shadowed_read_only_execution":
        if label == "living_gauntlet":
            local_extract = (
                "    module_name, symbol_name = value["
                "'all_layers_invariant_super_smoke_collector']\n"
            )
        else:
            local_extract = (
                "    module_name = value[-1]\n"
                "    symbol_name = value[-1]\n"
            )
        addition = (
            "\ndef tuple(value):\n"
            + local_extract
            + executable_tail
            + f"\ntuple({binding})\n"
        )
    elif mutation == "current_registry":
        addition = f"\n_ACTIVE_EXECUTION_REGISTRY = {binding}\n"
    else:
        addition = (
            "\nUNAUTHORIZED_METADATA = {"
            "'historical_act_id': 'all_layers_invariant_super_smoke'}\n"
        )
    failures = _historical_scan_failures(
        baseline + addition,
        label=label,
    )
    assert any(expected_family in item for item in failures), (
        label,
        mutation,
        failures,
    )


def _v04_ast_sha256(source: str) -> str:
    projection = ast.dump(
        ast.parse(source),
        annotate_fields=True,
        include_attributes=False,
    ).encode("utf-8")
    return hashlib.sha256(projection).hexdigest()


def _v04_case(
    *,
    case_id: str,
    family: str,
    production_helper: str,
    surface: str,
    phase: str,
    baseline: str,
    mutated: str,
    expected_failure_family: str,
    living: bool | None = None,
    binding: str | None = None,
) -> dict[str, object]:
    assert baseline != mutated
    return {
        "case_id": case_id,
        "family": family,
        "production_helper": production_helper,
        "surface": surface,
        "phase": phase,
        "accepted_baseline_ast_sha256": _v04_ast_sha256(baseline),
        "mutated_ast_sha256": _v04_ast_sha256(mutated),
        "expected_failure_family": expected_failure_family,
        "baseline": baseline,
        "mutated": mutated,
        "living": living,
        "binding": binding,
    }


def _v04_function_name(living: bool) -> str:
    namespace = _phase_contract_namespace()
    return (
        namespace["POST_E6_LIVING_ACCEPTANCE_TEST"]
        if living
        else namespace["POST_E6_CONFORMANCE_ACCEPTANCE_TEST"]
    )


def _v04_public_names(living: bool) -> tuple[str, str]:
    return (
        (
            "collect_living_gauntlet_v01",
            "validate_living_gauntlet_report_v01",
        )
        if living
        else (
            "collect_kernel_conformance_v01",
            "validate_kernel_conformance_runtime_v01",
        )
    )


def _v04_insert_function_prefix(
    source: str,
    *,
    living: bool,
    statement: str,
) -> str:
    marker = f"def {_v04_function_name(living)}():"
    return source.replace(marker, marker + "\n" + statement, 1)


def _v04_insert_module_block(
    source: str,
    *,
    living: bool,
    block: str,
) -> str:
    marker = f"def {_v04_function_name(living)}():"
    return source.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def _v04_build_focused_cases() -> tuple[dict[str, object], ...]:
    cases: list[dict[str, object]] = []

    for living in (True, False):
        surface = "living" if living else "conformance"
        collector, validator = _v04_public_names(living)
        module_baseline = _post_contract_source(
            living=living, module_import=True
        )
        function_mutations = {
            "module_tuple_subscript_collector": (
                "    runner_alias = (public_runner,)[0]\n"
                f"    runner_alias.{collector} = lambda: {{}}"
            ),
            "module_list_subscript_validator": (
                "    runner_alias = [public_runner][0]\n"
                f"    runner_alias.{validator} = lambda report: ()"
            ),
            "module_boolop_collector": (
                "    runner_alias = public_runner or fabricated_runner\n"
                f"    runner_alias.{collector} = lambda: {{}}"
            ),
            "module_ifexp_validator": (
                "    runner_alias = public_runner if True else fabricated_runner\n"
                f"    runner_alias.{validator} = lambda report: ()"
            ),
            "module_chained_collector": (
                "    wrapped = (public_runner,)\n"
                "    runner_alias = wrapped[0]\n"
                "    chained = runner_alias or public_runner\n"
                f"    chained.{collector} = lambda: {{}}"
            ),
            "module_chained_validator": (
                "    wrapped = [public_runner]\n"
                "    runner_alias = wrapped[0]\n"
                "    chained = runner_alias if True else public_runner\n"
                f"    chained.{validator} = lambda report: ()"
            ),
        }
        for mutation, statement in function_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v04.public.{surface}.{mutation}",
                    family="public_module_provenance",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=module_baseline,
                    mutated=_v04_insert_function_prefix(
                        module_baseline,
                        living=living,
                        statement=statement,
                    ),
                    expected_failure_family=".public_surface_provenance",
                    living=living,
                )
            )

        module_blocks = {
            "module_unrelated_default": (
                "def _prebind(_=public_runner.__dict__.update("
                f"{{{collector!r}: None}})):\n"
                "    return None"
            ),
            "module_function_body": (
                "def _mutate_public_module():\n"
                f"    public_runner.{collector} = lambda: {{}}"
            ),
            "module_async_function_body": (
                "async def _mutate_public_module():\n"
                f"    public_runner.{validator} = lambda report: ()"
            ),
            "module_lambda_body": (
                "_mutate_public_module = lambda: "
                "public_runner.__dict__.update("
                f"{{{collector!r}: None}})"
            ),
            "module_class_body": (
                "class _MutatePublicModule:\n"
                f"    public_runner.{collector} = lambda: {{}}"
            ),
            "module_nested_definition": (
                "def _outer_definition():\n"
                "    def _inner_definition():\n"
                f"        public_runner.{validator} = lambda report: ()"
            ),
            "module_decorator_expression": (
                "def _decorator(value):\n"
                "    return lambda function: function\n\n"
                "@_decorator(public_runner.__dict__.update("
                f"{{{collector!r}: None}}))\n"
                "def _decorated_helper():\n"
                "    return None"
            ),
        }
        for mutation, block in module_blocks.items():
            cases.append(
                _v04_case(
                    case_id=f"v04.public.{surface}.{mutation}",
                    family="public_definition_scope",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=module_baseline,
                    mutated=_v04_insert_module_block(
                        module_baseline,
                        living=living,
                        block=block,
                    ),
                    expected_failure_family=".public_surface_provenance",
                    living=living,
                )
            )

        report_baseline = _post_contract_source(living=living)
        report_mutations = {
            "report_tuple_subscript": (
                "    alias = (report,)[0]\n"
                "    alias.update({'forged': True})\n"
            ),
            "report_list_subscript": (
                "    alias = [report][0]\n"
                "    alias.update({'forged': True})\n"
            ),
            "report_boolop": (
                "    alias = report or {}\n"
                "    alias.update({'forged': True})\n"
            ),
            "report_ifexp": (
                "    alias = report if True else {}\n"
                "    alias.update({'forged': True})\n"
            ),
            "report_return_escape": (
                "    alias = (report,)[0]\n"
                "    return alias\n"
            ),
            "report_container_storage": "    holder = [report]\n",
            "report_unknown_escape": (
                "    alias = (report,)[0]\n"
                "    unknown_sink(alias)\n"
            ),
        }
        for mutation, addition in report_mutations.items():
            mutated = report_baseline.replace(
                "    validation =",
                addition + "    validation =",
                1,
            )
            cases.append(
                _v04_case(
                    case_id=f"v04.actual_return.{surface}.{mutation}",
                    family="actual_return_provenance",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=report_baseline,
                    mutated=mutated,
                    expected_failure_family=".actual_return_lineage",
                    living=living,
                )
            )

        spy_baseline = _post_contract_source(
            living=living, transparent_spy=True
        )
        spy_mutations = {
            "spy_setdefault_append": (
                "exact_return.setdefault('forged', []).append(exact_return)"
            ),
            "spy_report_field_append": (
                "exact_return['forged'].append(exact_return)"
            ),
            "spy_receiver_alias_append": (
                "(calls,)[0].append(exact_return)"
            ),
            "spy_unknown_receiver_append": (
                "unknown_recorder.append(exact_return)"
            ),
        }
        for mutation, replacement in spy_mutations.items():
            mutated = spy_baseline.replace(
                "calls.append(exact_return)", replacement, 1
            )
            cases.append(
                _v04_case(
                    case_id=f"v04.spy.{surface}.{mutation}",
                    family="transparent_spy_provenance",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=spy_baseline,
                    mutated=mutated,
                    expected_failure_family=".collector_missing",
                    living=living,
                )
            )

        fixed_access = (
            "report['continuous_delta_runtime_execution_count']"
            if living
            else "report.continuous_delta_runtime_execution_count"
        )
        tautologies = {
            "report_is_report_only": (
                f"    assert {fixed_access} == 1",
                "    assert report is report",
                ".tautological_assertion",
            ),
            "report_equals_report_only": (
                f"    assert {fixed_access} == 1",
                "    assert report == report",
                ".tautological_assertion",
            ),
            "report_truthiness_only": (
                f"    assert {fixed_access} == 1",
                "    assert report",
                ".tautological_assertion",
            ),
            "validation_truthiness_only": (
                "    assert validation == ()",
                "    assert validation",
                ".validation_success_contract",
            ),
            "validation_identity_only": (
                "    assert validation == ()",
                "    assert validation is validation",
                ".validation_success_contract",
            ),
        }
        for mutation, (old, new, expected) in tautologies.items():
            cases.append(
                _v04_case(
                    case_id=f"v04.assertion.{surface}.{mutation}",
                    family="actual_proof_tautology",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=report_baseline,
                    mutated=report_baseline.replace(old, new, 1),
                    expected_failure_family=expected,
                    living=living,
                )
            )

        proof_forms = {
            "local_assignment": "    {op} = lambda value: 64\n",
            "module_assignment": "{op} = lambda value: 64\n\n",
            "import_alias": "from fabricated import proof as {op}\n\n",
            "parameter": None,
            "function_def": (
                "    def {op}(value):\n        return value\n"
            ),
            "async_function_def": (
                "    async def {op}(value):\n        return value\n"
            ),
            "class_def": "    class {op}:\n        pass\n",
            "lambda_assignment": "    {op} = lambda value: value\n",
            "comprehension_target": "    tuple(0 for {op} in ())\n",
            "with_target": "    with manager() as {op}:\n        pass\n",
            "except_target": (
                "    try:\n        pass\n"
                "    except Exception as {op}:\n        pass\n"
            ),
            "global_declaration": "    global {op}\n",
            "nonlocal_declaration": (
                "    {op} = lambda value: value\n"
                "    def _nested_nonlocal():\n"
                "        nonlocal {op}\n"
                "        return {op}\n"
            ),
            "default_parameter": (
                "    def _default_shadow({op}=lambda value: value):\n"
                "        return {op}\n"
            ),
            "derived_alias": (
                "    replacement = lambda value: value\n"
                "    {op} = (replacement,)[0]\n"
            ),
        }
        for operator in ("len", "set", "tuple"):
            for form, template in proof_forms.items():
                if form == "parameter":
                    marker = f"def {_v04_function_name(living)}():"
                    mutated = report_baseline.replace(
                        marker,
                        f"def {_v04_function_name(living)}({operator}):",
                        1,
                    )
                elif form in {"module_assignment", "import_alias"}:
                    mutated = _v04_insert_module_block(
                        report_baseline,
                        living=living,
                        block=(template or "").format(op=operator),
                    )
                else:
                    mutated = _v04_insert_function_prefix(
                        report_baseline,
                        living=living,
                        statement=(template or "").format(op=operator).rstrip(),
                    )
                cases.append(
                    _v04_case(
                        case_id=(
                            f"v04.assertion_operator.{surface}."
                            f"{operator}.{form}"
                        ),
                        family="assertion_operator_binding",
                        production_helper="_validate_post_e6_test_contract_v02",
                        surface=surface,
                        phase="POST_E6_SUCCESSOR",
                        baseline=report_baseline,
                        mutated=mutated,
                        expected_failure_family=".assertion_operator_shadowed",
                        living=living,
                    )
                )

    for surface, binding in MUTABLE_CRITICAL_SURFACES:
        baseline = f"{binding} = {{'stable': ('module', 'symbol')}}\n"
        wrapper_mutations = {
            "tuple_subscript": f"({binding},)[0]",
            "list_subscript": f"[{binding}][0]",
            "boolop": f"{binding} or {{}}",
            "ifexp": f"{binding} if True else {{}}",
        }
        for mutation, expression in wrapper_mutations.items():
            mutated = (
                baseline
                + f"alias = {expression}\n"
                + "alias.update({'evil': ('x', 'y')})\n"
            )
            cases.append(
                _v04_case(
                    case_id=f"v04.critical.{surface}.{binding}.{mutation}",
                    family="critical_identity_provenance",
                    production_helper="_phase_critical_assignments_v02",
                    surface=surface,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=mutated,
                    expected_failure_family=".mutable_",
                    binding=binding,
                )
            )

    binding = "_ACT_SOURCES"
    baseline = f"{binding} = {{'stable': ('module', 'symbol')}}\n"
    critical_mutations = {
        "safe_name_operator_assignment": (
            "import operator\n"
            "dict = operator.setitem\n"
            f"dict({binding}, 'evil', ('x', 'y'))\n"
        ),
        "safe_name_import_alias": (
            "from operator import setitem as dict\n"
            f"dict({binding}, 'evil', ('x', 'y'))\n"
        ),
        "safe_name_lambda": (
            "dict = lambda value: value.update({'evil': ('x', 'y')})\n"
            f"dict({binding})\n"
        ),
        "safe_name_parameter": (
            "def consume(dict):\n"
            f"    dict({binding})\n"
        ),
        "safe_name_function": (
            "def dict(value):\n"
            "    value.update({'evil': ('x', 'y')})\n"
            f"dict({binding})\n"
        ),
        "safe_name_class": (
            "class dict:\n"
            "    def __init__(self, value):\n"
            "        value.update({'evil': ('x', 'y')})\n"
            f"dict({binding})\n"
        ),
        "safe_name_default": (
            "def consume(dict=lambda value: value.update("
            "{'evil': ('x', 'y')})):\n"
            f"    dict({binding})\n"
        ),
        "safe_name_nested": (
            "def outer():\n"
            "    def dict(value):\n"
            "        value.update({'evil': ('x', 'y')})\n"
            f"    dict({binding})\n"
        ),
        "closure_mutation": (
            "def outer():\n"
            f"    alias = {binding}\n"
            "    def mutate():\n"
            "        alias.update({'evil': ('x', 'y')})\n"
        ),
        "lambda_mutation": (
            f"mutate = lambda: {binding}.update({{'evil': ('x', 'y')}})\n"
        ),
        "class_method_mutation": (
            "class Mutator:\n"
            "    @staticmethod\n"
            "    def run():\n"
            f"        {binding}.update({{'evil': ('x', 'y')}})\n"
        ),
        "async_function_mutation": (
            "async def mutate():\n"
            f"    {binding}.update({{'evil': ('x', 'y')}})\n"
        ),
        "decorator_mutation": (
            "def decorate(value):\n"
            "    return lambda function: function\n"
            f"@decorate({binding}.update({{'evil': ('x', 'y')}}))\n"
            "def decorated():\n"
            "    return None\n"
        ),
        "comprehension_mutation": (
            f"[{binding}.update({{'evil': ('x', 'y')}}) for _ in (0,)]\n"
        ),
        "global_mutation": (
            "def mutate():\n"
            f"    global {binding}\n"
            f"    {binding}.update({{'evil': ('x', 'y')}})\n"
        ),
        "nonlocal_mutation": (
            "def outer():\n"
            f"    alias = {binding}\n"
            "    def mutate():\n"
            "        nonlocal alias\n"
            "        alias.update({'evil': ('x', 'y')})\n"
        ),
    }
    for mutation, addition in critical_mutations.items():
        cases.append(
            _v04_case(
                case_id=f"v04.critical.runner.{mutation}",
                family="critical_scope_or_safe_binding",
                production_helper="_phase_critical_assignments_v02",
                surface="kernel_conformance_runner",
                phase="PRE_AND_POST_HELPER_INVARIANT",
                baseline=baseline,
                mutated=baseline + addition,
                expected_failure_family=".mutable_",
                binding=binding,
            )
        )

    for label in tuple(HISTORICAL_SURFACE_PATHS):
        baseline = _historical_surface_source(label, "PRE_E6_RECONCILED")
        binding = HISTORICAL_PRIMARY_BINDINGS[label]
        imports = "\nimport importlib\nimport json\n"
        if label == "living_gauntlet":
            extraction = (
                "    module_name, symbol_name = material["
                "'all_layers_invariant_super_smoke_collector']\n"
            )
        else:
            extraction = (
                "    module_name = material[-1]\n"
                "    symbol_name = material[-1]\n"
            )
        execution = (
            "    legacy = importlib.import_module(module_name)\n"
            "    runner = getattr(legacy, symbol_name)\n"
            "    return runner()\n"
        )
        serialization_mutations = {
            "serialized_restore": (
                f"    encoded = json.dumps({binding})\n"
                "    material = json.loads(encoded)\n"
            ),
            "serialized_alias_restore": (
                f"    encoded = json.dumps({binding})\n"
                "    restored = json.loads(encoded)\n"
                "    material = restored\n"
            ),
            "serialized_container_restore": (
                f"    encoded = json.dumps({binding})\n"
                "    restored = json.loads(encoded)\n"
                "    wrapper = {'entry': restored}\n"
                "    material = (wrapper,)[0]['entry']\n"
            ),
        }
        for mutation, preparation in serialization_mutations.items():
            addition = (
                imports
                + "\ndef _execute_serialized_history_v04():\n"
                + preparation
                + extraction
                + execution
            )
            cases.append(
                _v04_case(
                    case_id=f"v04.historical.{label}.{mutation}",
                    family="historical_serialization_taint",
                    production_helper="_validate_historical_non_rebinding_v02",
                    surface=label,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + addition,
                    expected_failure_family=".tainted_import",
                )
            )

        safe_rebindings = {
            "safe_assignment": (
                "str = identity\n"
                f"encoded = str({binding})\n"
            ),
            "safe_import_alias": (
                "from fabricated import encode as str\n"
                f"encoded = str({binding})\n"
            ),
            "safe_lambda": (
                "str = lambda value: value\n"
                f"encoded = str({binding})\n"
            ),
            "safe_parameter": (
                "def consume(str):\n"
                f"    return str({binding})\n"
            ),
            "safe_function": (
                "def str(value):\n"
                "    return value\n"
                f"encoded = str({binding})\n"
            ),
            "safe_class": (
                "class str:\n"
                "    pass\n"
                f"encoded = str({binding})\n"
            ),
        }
        for mutation, addition in safe_rebindings.items():
            cases.append(
                _v04_case(
                    case_id=f"v04.historical.{label}.{mutation}",
                    family="historical_safe_binding",
                    production_helper="_validate_historical_non_rebinding_v02",
                    surface=label,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + "\n" + addition,
                    expected_failure_family=".tainted_escape",
                )
            )

        material_expression = (
            f"{binding}['all_layers_invariant_super_smoke_collector']"
            if label == "living_gauntlet"
            else f"{binding}[-1]"
        )
        nested_mutations = {
            "class_scope_execution": (
                "\nimport importlib\n"
                "class RecoverHistory:\n"
                f"    material = {material_expression}\n"
                "    module_name = material[0] if isinstance(material, tuple) else material\n"
                "    symbol_name = material[1] if isinstance(material, tuple) else material\n"
                "    legacy = importlib.import_module(module_name)\n"
                "    result = getattr(legacy, symbol_name)()\n"
            ),
            "lambda_scope_execution": (
                "\nimport importlib\n"
                f"recover = lambda: importlib.import_module({material_expression})\n"
            ),
            "default_scope_execution": (
                "\nimport importlib\n"
                "def recover(_=importlib.import_module("
                f"{material_expression})):\n"
                "    return None\n"
            ),
            "decorator_scope_execution": (
                "\nimport importlib\n"
                "def decorate(value):\n"
                "    return lambda function: function\n"
                "@decorate(importlib.import_module("
                f"{material_expression}))\n"
                "def recover():\n"
                "    return None\n"
            ),
        }
        for mutation, addition in nested_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v04.historical.{label}.{mutation}",
                    family="historical_nested_scope",
                    production_helper="_validate_historical_non_rebinding_v02",
                    surface=label,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + addition,
                    expected_failure_family=".tainted_import",
                )
            )
        cases.append(
            _v04_case(
                case_id=f"v04.historical.{label}.current_registry",
                family="historical_current_binding",
                production_helper="_validate_historical_non_rebinding_v02",
                surface=label,
                phase="PRE_AND_POST_HELPER_INVARIANT",
                baseline=baseline,
                mutated=(
                    baseline
                    + f"\n_ACTIVE_EXECUTION_REGISTRY = {binding}\n"
                ),
                expected_failure_family=".tainted_current_binding",
            )
        )

    case_ids = tuple(str(case["case_id"]) for case in cases)
    assert len(case_ids) == len(set(case_ids))
    semantic_keys = tuple(
        (
            case["production_helper"],
            case["accepted_baseline_ast_sha256"],
            case["mutated_ast_sha256"],
            case["expected_failure_family"],
        )
        for case in cases
    )
    assert len(semantic_keys) == len(set(semantic_keys))
    return tuple(cases)


V04_FOCUSED_CASES = _v04_build_focused_cases()
V04_FOCUSED_CASE_LEDGER_ROWS = tuple(
    {
        key: case[key]
        for key in (
            "case_id",
            "family",
            "production_helper",
            "surface",
            "phase",
            "accepted_baseline_ast_sha256",
            "mutated_ast_sha256",
            "expected_failure_family",
        )
    }
    for case in V04_FOCUSED_CASES
)


def _v05_build_new_focused_cases() -> tuple[dict[str, object], ...]:
    cases: list[dict[str, object]] = []

    for living in (True, False):
        surface = "living" if living else "conformance"
        collector, validator = _v04_public_names(living)
        function_name = _v04_function_name(living)
        module_name = (
            "demo.run_living_gauntlet_v01"
            if living
            else "demo.run_kernel_conformance_v01"
        )
        module_baseline = _post_contract_source(
            living=living, module_import=True
        )
        direct_baseline = _post_contract_source(living=living)

        function_scope_mutations = {
            "lambda_call_module": (
                "    runner_alias = (lambda: public_runner)()\n"
                f"    runner_alias.{collector} = lambda: {{}}"
            ),
            "function_call_module": (
                "    def module_getter():\n"
                "        return public_runner\n"
                "    runner_alias = module_getter()\n"
                f"    runner_alias.{validator} = lambda report: ()"
            ),
        }
        for mutation, statement in function_scope_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.public.{surface}.{mutation}",
                    family="public_scope_normal_form",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=module_baseline,
                    mutated=_v04_insert_function_prefix(
                        module_baseline,
                        living=living,
                        statement=statement,
                    ),
                    expected_failure_family=".semantic_normal_form",
                    living=living,
                )
            )

        module_scope_mutations = {
            "class_storage": (
                "class PublicHolder:\n"
                "    material = public_runner\n"
                f"PublicHolder.material.{collector} = lambda: {{}}"
            ),
            "function_default": (
                "def public_holder(value=public_runner):\n"
                "    return value"
            ),
            "decorator_capture": (
                "def decorate(value):\n"
                "    return lambda function: function\n"
                "@decorate(public_runner)\n"
                "def public_holder():\n"
                "    return None"
            ),
            "parameter_annotation": (
                "def public_holder(value: public_runner):\n"
                "    return value"
            ),
            "return_annotation": (
                "def public_holder() -> public_runner:\n"
                "    return None"
            ),
            "nested_capture": (
                "def outer_public_holder():\n"
                "    def inner_public_holder():\n"
                "        return public_runner\n"
                "    return None"
            ),
            "container_call_chain": (
                "def public_holder():\n"
                "    return {'runner': public_runner}\n"
                "holder = public_holder()\n"
                f"holder['runner'].{validator} = lambda report: ()"
            ),
        }
        for mutation, block in module_scope_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.public.{surface}.{mutation}",
                    family="public_module_provenance",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=module_baseline,
                    mutated=_v04_insert_module_block(
                        module_baseline,
                        living=living,
                        block=block,
                    ),
                    expected_failure_family=".public_binding_escape",
                    living=living,
                )
            )

        namespace_mutations = {
            "globals_subscript_collector": (
                f"globals()[{collector!r}] = lambda: {{}}"
            ),
            "globals_subscript_validator": (
                f"globals()[{validator!r}] = lambda report: ()"
            ),
            "globals_setitem_collector": (
                f"globals().__setitem__({collector!r}, lambda: {{}})"
            ),
            "globals_setitem_validator": (
                f"globals().__setitem__({validator!r}, lambda report: ())"
            ),
            "builtins_globals_collector": (
                "import builtins\n"
                f"builtins.globals().__setitem__({collector!r}, lambda: {{}})"
            ),
            "builtins_globals_validator": (
                "import builtins\n"
                f"builtins.globals().__setitem__({validator!r}, lambda report: ())"
            ),
            "locals_validator": (
                f"locals()[{validator!r}] = lambda report: ()"
            ),
            "vars_collector": f"vars()[{collector!r}] = lambda: {{}}",
            "dunder_builtins_validator": (
                f"__builtins__[{validator!r}] = lambda report: ()"
            ),
            "sys_modules_literal": (
                "import sys\n"
                f"sys.modules[{module_name!r}].{collector} = lambda: {{}}"
            ),
            "sys_modules_derived": (
                "import sys\n"
                f"module_key = {module_name.rsplit('.', 1)[0]!r} + "
                f"{('.' + module_name.rsplit('.', 1)[1])!r}\n"
                f"sys.modules[module_key].{validator} = lambda report: ()"
            ),
            "module_dict": (
                f"public_runner.__dict__[{collector!r}] = lambda: {{}}"
            ),
            "setattr_module": (
                f"setattr(public_runner, {validator!r}, lambda report: ())"
            ),
            "delattr_module": f"delattr(public_runner, {collector!r})",
            "dynamic_import": (
                "import importlib\n"
                f"recovered = importlib.import_module({module_name!r})\n"
                f"recovered.{collector} = lambda: {{}}"
            ),
        }
        for mutation, block in namespace_mutations.items():
            baseline = (
                module_baseline
                if any(
                    marker in mutation
                    for marker in ("module_dict", "setattr", "delattr")
                )
                else direct_baseline
            )
            cases.append(
                _v04_case(
                    case_id=f"v05.namespace.{surface}.{mutation}",
                    family="dynamic_namespace_authority",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=baseline,
                    mutated=_v04_insert_module_block(
                        baseline,
                        living=living,
                        block=block,
                    ),
                    expected_failure_family=(
                        ".public_module_authority"
                        if mutation == "module_dict"
                        else ".dynamic_capability"
                    ),
                    living=living,
                )
            )

        callable_mutations = {
            "collector_code": f"{collector}.__code__ = replacement.__code__",
            "collector_defaults": f"{collector}.__defaults__ = ()",
            "collector_kwdefaults": f"{collector}.__kwdefaults__ = {{}}",
            "validator_code": f"{validator}.__code__ = replacement.__code__",
            "validator_defaults": f"{validator}.__defaults__ = ()",
            "validator_kwdefaults": f"{validator}.__kwdefaults__ = {{}}",
        }
        for mutation, block in callable_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.public_callable.{surface}.{mutation}",
                    family="public_callable_authority",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=direct_baseline,
                    mutated=_v04_insert_module_block(
                        direct_baseline,
                        living=living,
                        block=block,
                    ),
                    expected_failure_family=".dynamic_capability",
                    living=living,
                )
            )

        report_mutations = {
            "class_attribute": (
                "    class Holder:\n"
                "        material = report\n"
                "    leaked = Holder.material\n"
                "    leaked.update({'forged': True})\n"
            ),
            "function_default": (
                "    def holder(value=report):\n"
                "        return value\n"
                "    leaked = holder()\n"
            ),
            "lambda_default": (
                "    holder = lambda value=report: value\n"
                "    leaked = holder()\n"
            ),
            "function_return": (
                "    def holder():\n"
                "        return report\n"
                "    leaked = holder()\n"
            ),
            "lambda_return": (
                "    holder = lambda: report\n"
                "    leaked = holder()\n"
            ),
            "decorator_capture": (
                "    def decorate(value):\n"
                "        return lambda function: function\n"
                "    @decorate(report)\n"
                "    def holder():\n"
                "        return None\n"
            ),
            "annotation_capture": (
                "    def holder(value: report):\n"
                "        return value\n"
            ),
            "dict_storage": (
                "    holder = {}\n"
                "    holder['report'] = report\n"
                "    leaked = holder['report']\n"
            ),
            "list_storage": (
                "    holder = []\n"
                "    holder.append(report)\n"
                "    leaked = holder[0]\n"
            ),
            "object_attribute": (
                "    class Holder:\n"
                "        pass\n"
                "    holder = Holder()\n"
                "    holder.report = report\n"
                "    leaked = holder.report\n"
            ),
            "closure_nonlocal": (
                "    leaked = None\n"
                "    def holder():\n"
                "        nonlocal leaked\n"
                "        leaked = report\n"
            ),
            "generator_carrier": (
                "    holder = (value for value in (report,))\n"
                "    leaked = next(holder)\n"
            ),
            "comprehension_carrier": (
                "    holder = [value for value in (report,)]\n"
                "    leaked = holder[0]\n"
            ),
            "unknown_local_return": (
                "    def holder(value):\n"
                "        return value\n"
                "    leaked = holder(report)\n"
            ),
        }
        for mutation, addition in report_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.actual_return.{surface}.{mutation}",
                    family="actual_return_scope",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=direct_baseline,
                    mutated=direct_baseline.replace(
                        "    validation =",
                        addition + "    validation =",
                        1,
                    ),
                    expected_failure_family=".semantic_normal_form",
                    living=living,
                )
            )

        spy_baseline = _post_contract_source(
            living=living, transparent_spy=True
        )
        spy_mutations = {
            "positional_annotation": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(marker: object, *args, **kwargs):",
            ),
            "keyword_annotation": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(*args, marker: object, **kwargs):",
            ),
            "vararg_annotation": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(*args: object, **kwargs):",
            ),
            "kwarg_annotation": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(*args, **kwargs: object):",
            ),
            "return_annotation": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(*args, **kwargs) -> object:",
            ),
            "default": (
                "def counted_collector(*args, **kwargs):",
                "def counted_collector(marker=None, *args, **kwargs):",
            ),
            "decorator": (
                "    def counted_collector(*args, **kwargs):",
                "    @decorator\n    def counted_collector(*args, **kwargs):",
            ),
            "closure_owner": (
                "    calls = []",
                "    owner = []\n    calls = owner",
            ),
            "class_owner": (
                "    calls = []",
                "    class SpyOwner:\n        calls = []\n    calls = SpyOwner.calls",
            ),
            "recorder_factory": ("calls = []", "calls = make_recorder()"),
            "derived_recorder": (
                "calls.append(exact_return)",
                "(calls,)[0].append(exact_return)",
            ),
            "report_owned_recorder": (
                "calls.append(exact_return)",
                "exact_return.setdefault('calls', []).append(exact_return)",
            ),
        }
        for mutation, (old, new) in spy_mutations.items():
            mutated = spy_baseline.replace(old, new, 1)
            assert mutated != spy_baseline
            cases.append(
                _v04_case(
                    case_id=f"v05.spy.{surface}.{mutation}",
                    family="transparent_spy_definition",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=spy_baseline,
                    mutated=mutated,
                    expected_failure_family=".semantic_normal_form",
                    living=living,
                )
            )

        builtin_mutations = {}
        for operator in ("len", "set", "tuple"):
            builtin_mutations.update(
                {
                    f"{operator}_builtins_attribute": (
                        "import builtins\n"
                        f"builtins.{operator} = replacement"
                    ),
                    f"{operator}_dunder_builtins": (
                        f"__builtins__[{operator!r}] = replacement"
                    ),
                    f"{operator}_sys_modules": (
                        "import sys\n"
                        f"sys.modules['builtins'].{operator} = replacement"
                    ),
                    f"{operator}_module_alias": (
                        "import builtins\n"
                        "builtin_alias = (builtins,)[0]\n"
                        f"builtin_alias.{operator} = replacement"
                    ),
                    f"{operator}_module_dict": (
                        "import builtins\n"
                        f"builtins.__dict__[{operator!r}] = replacement"
                    ),
                    f"{operator}_setter": (
                        "import builtins\n"
                        f"setattr(builtins, {operator!r}, replacement)"
                    ),
                    f"{operator}_restore_after": (
                        "import builtins\n"
                        f"saved = builtins.{operator}\n"
                        f"builtins.{operator} = replacement\n"
                        f"builtins.{operator} = saved"
                    ),
                }
            )
        for mutation, block in builtin_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.assertion_builtin.{surface}.{mutation}",
                    family="assertion_builtin_authority",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=direct_baseline,
                    mutated=_v04_insert_module_block(
                        direct_baseline,
                        living=living,
                        block=block,
                    ),
                    expected_failure_family=".assertion_builtin_authority",
                    living=living,
                )
            )
        restore_after_assertions = _v04_insert_module_block(
            direct_baseline,
            living=living,
            block="import builtins\nsaved_len = builtins.len",
        )
        restore_after_assertions += (
            "    builtins.len = replacement\n"
            "    builtins.len = saved_len\n"
        )
        cases.append(
            _v04_case(
                case_id=(
                    f"v05.assertion_builtin.{surface}."
                    "len_restore_after_assertions"
                ),
                family="assertion_builtin_authority",
                production_helper="_validate_post_e6_test_contract_v02",
                surface=surface,
                phase="POST_E6_SUCCESSOR",
                baseline=direct_baseline,
                mutated=restore_after_assertions,
                expected_failure_family=".assertion_builtin_authority",
                living=living,
            )
        )

        sentinel_public_block = (
            f"import {module_name} as sentinel_module\n"
            f"globals()[{collector!r}] = "
            "lambda: sentinel_module.SENTINEL_REPORT"
        )
        sentinel_public = _v04_case(
            case_id=f"v05.sentinel.{surface}.public_substitution",
            family="synthetic_public_substitution_sentinel",
            production_helper="_validate_post_e6_test_contract_v02",
            surface=surface,
            phase="POST_E6_SUCCESSOR",
            baseline=direct_baseline,
            mutated=(
                _v04_insert_module_block(
                    direct_baseline,
                    living=living,
                    block=sentinel_public_block,
                )
                + f"\nif __name__ == '__main__':\n    {function_name}()\n"
            ),
            expected_failure_family=".dynamic_capability",
            living=living,
        )
        sentinel_public["sentinel_kind"] = "public_substitution"
        cases.append(sentinel_public)

        sentinel_builtin_block = (
            "import builtins\n"
            "builtins.len = lambda value: 64\n"
            "builtins.set = lambda value: frozenset()"
        )
        sentinel_builtin = _v04_case(
            case_id=f"v05.sentinel.{surface}.proof_builtin_replacement",
            family="synthetic_proof_builtin_sentinel",
            production_helper="_validate_post_e6_test_contract_v02",
            surface=surface,
            phase="POST_E6_SUCCESSOR",
            baseline=direct_baseline,
            mutated=(
                _v04_insert_module_block(
                    direct_baseline,
                    living=living,
                    block=sentinel_builtin_block,
                )
                + f"\nif __name__ == '__main__':\n    {function_name}()\n"
            ),
            expected_failure_family=".assertion_builtin_authority",
            living=living,
        )
        sentinel_builtin["sentinel_kind"] = "proof_builtin_replacement"
        cases.append(sentinel_builtin)

    for surface, binding in MUTABLE_CRITICAL_SURFACES:
        baseline = f"{binding} = {{'stable': ('module', 'symbol')}}\n"
        scope_mutations = {
            "lambda_getter": (
                f"getter = lambda: {binding}\n"
                "alias = getter()\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "function_getter": (
                "def getter():\n"
                f"    return {binding}\n"
                "alias = getter()\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "class_attribute": (
                "class Holder:\n"
                f"    material = {binding}\n"
                "alias = Holder.material\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "instance_attribute": (
                "class Holder:\n"
                "    pass\n"
                "holder = Holder()\n"
                f"holder.material = {binding}\n"
                "alias = holder.material\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "function_default": (
                f"def getter(value={binding}):\n"
                "    return value\n"
            ),
            "decorator": (
                "def decorate(value):\n"
                "    return lambda function: function\n"
                f"@decorate({binding})\n"
                "def holder():\n"
                "    return None\n"
            ),
            "annotation": (
                f"def holder(value: {binding}):\n"
                "    return value\n"
            ),
            "closure": (
                "def outer():\n"
                f"    alias = {binding}\n"
                "    def getter():\n"
                "        return alias\n"
            ),
            "method_return": (
                "class Holder:\n"
                "    @staticmethod\n"
                "    def getter():\n"
                f"        return {binding}\n"
            ),
            "generator": (
                f"holder = (value for value in ({binding},))\n"
                "alias = next(holder)\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "container_recovery": (
                "holder = {}\n"
                f"holder['entry'] = {binding}\n"
                "alias = holder['entry']\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "safe_constructor_rebound": (
                "tuple = lambda value: value\n"
                f"alias = tuple({binding})\n"
                "alias.update({'evil': ('x', 'y')})\n"
            ),
            "safe_function_rebound": (
                "def dict(value):\n"
                "    value.update({'evil': ('x', 'y')})\n"
                f"dict({binding})\n"
            ),
            "safe_method_name_rebound": (
                "copy = lambda value: value.update("
                "{'evil': ('x', 'y')})\n"
                f"copy({binding})\n"
            ),
        }
        for mutation, addition in scope_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.critical.{surface}.{binding}.{mutation}",
                    family="critical_return_scope",
                    production_helper="_phase_critical_assignments_v02",
                    surface=surface,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + addition,
                    expected_failure_family={
                        "safe_constructor_rebound": ".mutable_escape",
                        "safe_function_rebound": ".mutable_call",
                        "safe_method_name_rebound": ".mutable_escape",
                    }.get(mutation, ".mutable_scope_escape"),
                    binding=binding,
                )
            )

        namespace_mutations = {
            "globals_subscript": f"globals()[{binding!r}] = {{}}\n",
            "globals_setitem": (
                f"globals().__setitem__({binding!r}, {{}})\n"
            ),
            "builtins_globals": (
                "import builtins\n"
                f"builtins.globals().__setitem__({binding!r}, {{}})\n"
            ),
            "locals_subscript": f"locals()[{binding!r}] = {{}}\n",
            "vars_subscript": f"vars()[{binding!r}] = {{}}\n",
            "sys_modules": (
                "import sys\n"
                f"sys.modules[__name__].__dict__[{binding!r}] = {{}}\n"
            ),
            "module_dict": f"globals().__dict__[{binding!r}] = {{}}\n",
            "setattr_namespace": (
                f"setattr(sys.modules[__name__], {binding!r}, {{}})\n"
            ),
            "delattr_namespace": (
                f"delattr(sys.modules[__name__], {binding!r})\n"
            ),
            "exec_mutation": f"exec({(binding + ' = {}')!r})\n",
            "eval_mutation": f"eval({('globals().__setitem__(' + repr(binding) + ', {})')!r})\n",
        }
        for mutation, addition in namespace_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.critical_namespace.{surface}.{binding}.{mutation}",
                    family="critical_namespace",
                    production_helper="_phase_critical_assignments_v02",
                    surface=surface,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + addition,
                    expected_failure_family=".critical_namespace",
                    binding=binding,
                )
            )

    for label in tuple(HISTORICAL_SURFACE_PATHS):
        baseline = _historical_surface_source(label, "PRE_E6_RECONCILED")
        binding = HISTORICAL_PRIMARY_BINDINGS[label]
        scope_mutations = {
            "container_subscript": (
                "cache = {}\n"
                f"cache['entry'] = {binding}\n"
                "material = cache['entry']\n"
            ),
            "class_attribute": (
                "class HistoricalHolder:\n"
                f"    material = {binding}\n"
            ),
            "instance_attribute": (
                "class HistoricalHolder:\n"
                "    pass\n"
                "holder = HistoricalHolder()\n"
                f"holder.material = {binding}\n"
            ),
            "function_default": (
                f"def historical_holder(value={binding}):\n"
                "    return value\n"
            ),
            "lambda_default": (
                f"historical_holder = lambda value={binding}: value\n"
            ),
            "closure_return": (
                "def historical_outer():\n"
                f"    material = {binding}\n"
                "    def historical_inner():\n"
                "        return material\n"
            ),
            "local_return": (
                "def historical_holder():\n"
                f"    return {binding}\n"
            ),
            "decorator": (
                "def decorate(value):\n"
                "    return lambda function: function\n"
                f"@decorate({binding})\n"
                "def historical_holder():\n"
                "    return None\n"
            ),
            "annotation": (
                f"def historical_holder(value: {binding}):\n"
                "    return value\n"
            ),
        }
        if label == "living_gauntlet":
            scope_mutations["container_subscript"] += (
                "module_name, symbol_name = material["
                "'all_layers_invariant_super_smoke_collector']\n"
            )
        else:
            scope_mutations["container_subscript"] += (
                "module_name = material[-1]\n"
                "symbol_name = material[-1]\n"
            )
        scope_mutations["container_subscript"] += (
            "import importlib\n"
            "legacy = importlib.import_module(module_name)\n"
            "getattr(legacy, symbol_name)()\n"
        )
        for mutation, addition in scope_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.historical_scope.{label}.{mutation}",
                    family="historical_container_scope",
                    production_helper="_validate_historical_non_rebinding_v02",
                    surface=label,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + "\n" + addition,
                    expected_failure_family=".tainted_scope_",
                )
            )

        json_mutations = {
            "dumps_assignment": (
                "import json\njson.dumps = replacement\n"
                f"json.dumps({binding})\n"
            ),
            "loads_assignment": (
                "import json\njson.loads = replacement\n"
                f"json.loads(json.dumps({binding}))\n"
            ),
            "loads_setattr": (
                "import json\nsetattr(json, 'loads', replacement)\n"
                f"json.loads(json.dumps({binding}))\n"
            ),
            "loads_dict": (
                "import json\njson.__dict__['loads'] = replacement\n"
                f"json.loads(json.dumps({binding}))\n"
            ),
            "loads_alias": (
                "import json\ncodec = (json,)[0]\n"
                "codec.loads = replacement\n"
                f"json.loads(json.dumps({binding}))\n"
            ),
            "loads_registry": (
                "import json\nimport sys\n"
                "sys.modules['json'].loads = replacement\n"
                f"json.loads(json.dumps({binding}))\n"
            ),
            "dumps_setattr": (
                "import json\nsetattr(json, 'dumps', replacement)\n"
                f"json.dumps({binding})\n"
            ),
            "dumps_dict": (
                "import json\njson.__dict__['dumps'] = replacement\n"
                f"json.dumps({binding})\n"
            ),
            "dumps_alias": (
                "import json\ncodec = (json,)[0]\n"
                "codec.dumps = replacement\n"
                f"json.dumps({binding})\n"
            ),
            "dumps_registry": (
                "import json\nimport sys\n"
                "sys.modules['json'].dumps = replacement\n"
                f"json.dumps({binding})\n"
            ),
            "nested_binding": (
                "import json\n"
                "def encode(json):\n"
                f"    return json.dumps({binding})\n"
            ),
        }
        for mutation, addition in json_mutations.items():
            cases.append(
                _v04_case(
                    case_id=f"v05.historical_json.{label}.{mutation}",
                    family="historical_safe_call_authority",
                    production_helper="_validate_historical_non_rebinding_v02",
                    surface=label,
                    phase="PRE_AND_POST_HELPER_INVARIANT",
                    baseline=baseline,
                    mutated=baseline + "\n" + addition,
                    expected_failure_family=(
                        ".json_authority"
                        if mutation != "nested_binding"
                        else ".tainted_escape"
                    ),
                )
            )

    case_ids = tuple(str(case["case_id"]) for case in cases)
    assert len(case_ids) == len(set(case_ids))
    semantic_keys = tuple(
        (
            case["production_helper"],
            case["accepted_baseline_ast_sha256"],
            case["mutated_ast_sha256"],
            case["expected_failure_family"],
        )
        for case in cases
    )
    assert len(semantic_keys) == len(set(semantic_keys))
    return tuple(cases)


V05_NEW_FOCUSED_CASES = _v05_build_new_focused_cases()
V05_FOCUSED_CASES = (*V04_FOCUSED_CASES, *V05_NEW_FOCUSED_CASES)
V05_FOCUSED_CASE_LEDGER_ROWS = tuple(
    {
        key: case[key]
        for key in (
            "case_id",
            "family",
            "production_helper",
            "surface",
            "phase",
            "accepted_baseline_ast_sha256",
            "mutated_ast_sha256",
            "expected_failure_family",
        )
    }
    for case in V05_FOCUSED_CASES
)
FOCUSED_CASE_LEDGER_COLUMNS = (
    "case_id",
    "family",
    "production_helper",
    "surface",
    "phase",
    "accepted_baseline_ast_sha256",
    "mutated_ast_sha256",
    "expected_failure_family",
)
V04_FOCUSED_CASE_LEDGER_SHA256 = (
    "38f22031a6f40cad150061ebee90cba9531b3367f5c11c1d7b54dae6a1e0840a"
)


def _focused_case_ledger_bytes(
    rows: tuple[dict[str, object], ...],
) -> bytes:
    lines = ["\t".join(FOCUSED_CASE_LEDGER_COLUMNS)]
    lines.extend(
        "\t".join(str(row[column]) for column in FOCUSED_CASE_LEDGER_COLUMNS)
        for row in rows
    )
    return ("\n".join(lines) + "\n").encode("ascii")


V05_FOCUSED_CASE_LEDGER_SHA256 = (
    "a91cf04744f74d20681412c0643bf74d114461154ff3c44f141a9d61939df5f2"
)


def _v06_build_new_focused_cases() -> tuple[dict[str, object], ...]:
    cases: list[dict[str, object]] = []
    assertion_tail_mutations = (
        ("counted_collector_reinvocation", "assert counted_collector() is report"),
        ("calls_clear", "assert calls.clear() is None"),
        ("calls_pop", "assert calls.pop() is report"),
        ("report_clear_via_recorder", "assert calls[0].clear() is None"),
        (
            "calls_setitem",
            "assert calls.__setitem__(0, {}) is None",
        ),
    )
    for living in (True, False):
        surface = "living" if living else "conformance"
        baseline = _post_contract_source(
            living=living,
            transparent_spy=True,
        )
        for mutation, assertion in assertion_tail_mutations:
            cases.append(
                _v04_case(
                    case_id=f"v06.assertion_tail.{surface}.{mutation}",
                    family="assertion_tail_exact",
                    production_helper="_validate_post_e6_test_contract_v02",
                    surface=surface,
                    phase="POST_E6_SUCCESSOR",
                    baseline=baseline,
                    mutated=baseline.rstrip() + f"\n    {assertion}\n",
                    expected_failure_family=(
                        ".semantic_normal_form:assertion_tail"
                    ),
                    living=living,
                )
            )
    assert len(cases) == 10
    return tuple(cases)


V06_NEW_FOCUSED_CASES = _v06_build_new_focused_cases()
V06_FOCUSED_CASES = (*V05_FOCUSED_CASES, *V06_NEW_FOCUSED_CASES)
V06_FOCUSED_CASE_LEDGER_ROWS = tuple(
    {
        column: case[column]
        for column in FOCUSED_CASE_LEDGER_COLUMNS
    }
    for case in V06_FOCUSED_CASES
)


def test_v05_focused_case_ledger_is_source_derived_and_unique() -> None:
    assert len(V04_FOCUSED_CASE_LEDGER_ROWS) == 222
    assert hashlib.sha256(
        _focused_case_ledger_bytes(V04_FOCUSED_CASE_LEDGER_ROWS)
    ).hexdigest() == V04_FOCUSED_CASE_LEDGER_SHA256
    assert V05_FOCUSED_CASE_LEDGER_ROWS[:222] == V04_FOCUSED_CASE_LEDGER_ROWS
    assert len(V05_FOCUSED_CASES) == len(V05_FOCUSED_CASE_LEDGER_ROWS)
    assert {
        str(row["production_helper"])
        for row in V05_FOCUSED_CASE_LEDGER_ROWS
    } == {
        "_validate_post_e6_test_contract_v02",
        "_phase_critical_assignments_v02",
        "_validate_historical_non_rebinding_v02",
    }
    case_ids = tuple(
        str(row["case_id"]) for row in V05_FOCUSED_CASE_LEDGER_ROWS
    )
    assert len(case_ids) == len(set(case_ids))
    semantic_keys = tuple(
        (
            str(row["production_helper"]),
            str(row["accepted_baseline_ast_sha256"]),
            str(row["mutated_ast_sha256"]),
            str(row["expected_failure_family"]),
        )
        for row in V05_FOCUSED_CASE_LEDGER_ROWS
    )
    assert len(semantic_keys) == len(set(semantic_keys))
    for case, row in zip(
        V05_FOCUSED_CASES,
        V05_FOCUSED_CASE_LEDGER_ROWS,
        strict=True,
    ):
        assert _v04_ast_sha256(str(case["baseline"])) == row[
            "accepted_baseline_ast_sha256"
        ]
        assert _v04_ast_sha256(str(case["mutated"])) == row[
            "mutated_ast_sha256"
        ]


def test_v06_focused_case_ledger_preserves_v05_and_is_unique() -> None:
    assert len(V05_FOCUSED_CASE_LEDGER_ROWS) == 542
    assert hashlib.sha256(
        _focused_case_ledger_bytes(V05_FOCUSED_CASE_LEDGER_ROWS)
    ).hexdigest() == V05_FOCUSED_CASE_LEDGER_SHA256
    assert V06_FOCUSED_CASE_LEDGER_ROWS[:542] == V05_FOCUSED_CASE_LEDGER_ROWS
    assert len(V06_NEW_FOCUSED_CASES) == 10
    assert len(V06_FOCUSED_CASES) == 552
    assert len(V06_FOCUSED_CASE_LEDGER_ROWS) == 552
    assert {
        str(row["production_helper"])
        for row in V06_FOCUSED_CASE_LEDGER_ROWS
    } == {
        "_validate_post_e6_test_contract_v02",
        "_phase_critical_assignments_v02",
        "_validate_historical_non_rebinding_v02",
    }
    case_ids = tuple(
        str(row["case_id"])
        for row in V06_FOCUSED_CASE_LEDGER_ROWS
    )
    assert len(case_ids) == len(set(case_ids)) == 552
    semantic_keys = tuple(
        (
            str(row["production_helper"]),
            str(row["accepted_baseline_ast_sha256"]),
            str(row["mutated_ast_sha256"]),
            str(row["expected_failure_family"]),
        )
        for row in V06_FOCUSED_CASE_LEDGER_ROWS
    )
    assert len(semantic_keys) == len(set(semantic_keys)) == 552
    for case, row in zip(
        V06_FOCUSED_CASES,
        V06_FOCUSED_CASE_LEDGER_ROWS,
        strict=True,
    ):
        assert _v04_ast_sha256(str(case["baseline"])) == row[
            "accepted_baseline_ast_sha256"
        ]
        assert _v04_ast_sha256(str(case["mutated"])) == row[
            "mutated_ast_sha256"
        ]


def _v05_synthetic_report_source(
    *,
    living: bool,
    marker_path: Path,
    malformed_hash: bool,
) -> str:
    namespace = _phase_contract_namespace()
    values = {
        field: expected
        for field, expected in namespace["POST_E6_SHARED_FIXED_REPORT_VALUES"]
    }
    digest = "x" if malformed_hash else "0" * 64
    for field in namespace["POST_E6_SHARED_SHA256_FIELDS"]:
        values[field] = digest
    for field in namespace["POST_E6_SHARED_BYTE_COUNT_FIELDS"]:
        values[field] = 1
    if living:
        values.update(
            {
                "runner_version": "v1.6",
                "kernel_conformance_profile": namespace["POST_E6_PROFILE_ID"],
                "historical_kernel_conformance_profile": namespace[
                    "POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID"
                ],
                "active_act_results": [
                    {"act_id": act_id}
                    for act_id in namespace["POST_E6_LIVING_ACT_IDS"]
                ],
            }
        )
        report_source = repr(values)
        collector = "collect_living_gauntlet_v01"
        validator = "validate_living_gauntlet_report_v01"
    else:
        keyword_rows = [
            f"{key}={value!r}" for key, value in values.items()
        ]
        keyword_rows.extend(
            (
                "conformance_version='v0.7'",
                f"profile_id={namespace['POST_E6_PROFILE_ID']!r}",
                "historical_profile_ref="
                + repr(namespace["POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID"]),
                "category_results=("
                + ",".join(
                    "NS(category_id="
                    + repr(category_id)
                    + ", required_check_ids="
                    + repr(check_ids)
                    + ")"
                    for category_id, check_ids in namespace[
                        "POST_E6_CATEGORY_CHECK_IDS"
                    ]
                )
                + ",)",
                "negative_test_results=("
                + ",".join(
                    f"NS(probe_id={probe_id!r})"
                    for probe_id in namespace["POST_E6_NEGATIVE_PROBE_IDS"]
                )
                + ",)",
                f"active_gauntlet_refs={namespace['POST_E6_ACTIVE_REFS']!r}",
                "domain_results=("
                + ",".join(
                    f"NS(domain_id={domain_id!r})"
                    for domain_id in namespace["PRESERVED_DOMAIN_IDS"]
                )
                + ",)",
            )
        )
        report_source = "NS(" + ",".join(keyword_rows) + ")"
        collector = "collect_kernel_conformance_v01"
        validator = "validate_kernel_conformance_runtime_v01"
    collector_receipt = (
        "    print('SYNTHETIC_ORIGINAL_COLLECTOR_CALLED')\n"
        if malformed_hash
        else f"    Path({str(marker_path)!r}).write_text('called', encoding='ascii')\n"
    )
    path_import = "" if malformed_hash else "from pathlib import Path\n"
    return (
        path_import
        + "from types import SimpleNamespace as NS\n"
        f"SENTINEL_REPORT = {report_source}\n"
        f"def {collector}():\n"
        f"{collector_receipt}"
        "    return SENTINEL_REPORT\n"
        f"def {validator}(report):\n"
        "    return ()\n"
    )


def _run_v05_executable_sentinel(
    tmp_path: Path,
    case: dict[str, object],
) -> None:
    living = bool(case["living"])
    module_relative = (
        Path("demo/run_living_gauntlet_v01.py")
        if living
        else Path("demo/run_kernel_conformance_v01.py")
    )
    module_path = tmp_path / module_relative
    module_path.parent.mkdir(parents=True, exist_ok=True)
    (module_path.parent / "__init__.py").write_text("", encoding="ascii")
    marker = tmp_path / "original_collector_called.txt"
    kind = str(case["sentinel_kind"])
    module_path.write_text(
        _v05_synthetic_report_source(
            living=living,
            marker_path=marker,
            malformed_hash=kind == "proof_builtin_replacement",
        ),
        encoding="utf-8",
    )
    script = tmp_path / "sentinel_acceptance.py"
    script.write_text(str(case["mutated"]), encoding="utf-8")
    completed = subprocess.run(
        (sys.executable, str(script)),
        cwd=tmp_path,
        env={
            **os.environ,
            "PYTHONPATH": str(tmp_path),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, (
        case["case_id"],
        completed.stdout,
        completed.stderr,
    )
    if kind == "public_substitution":
        assert not marker.exists(), case["case_id"]
    else:
        assert completed.stdout == "SYNTHETIC_ORIGINAL_COLLECTOR_CALLED\n"


@pytest.mark.parametrize(
    "case",
    V04_FOCUSED_CASES,
    ids=tuple(str(case["case_id"]) for case in V04_FOCUSED_CASES),
)
def test_v04_focused_provenance_case(
    tmp_path: Path,
    case: dict[str, object],
) -> None:
    namespace = _phase_contract_namespace()

    def evaluate(source: str) -> tuple[str, ...]:
        helper = case["production_helper"]
        if helper == "_validate_post_e6_test_contract_v02":
            path = tmp_path / "post_contract.py"
            path.write_text(source, encoding="utf-8")
            return namespace[helper](path, living=case["living"])
        if helper == "_phase_critical_assignments_v02":
            _values, _nodes, failures = _critical_extract(
                tmp_path,
                source,
                frozenset({str(case["binding"])}),
            )
            return failures
        assert helper == "_validate_historical_non_rebinding_v02"
        return _historical_scan_failures(
            source,
            label=str(case["surface"]),
        )

    baseline = str(case["baseline"])
    mutated = str(case["mutated"])
    assert evaluate(baseline) == (), case["case_id"]
    failures = evaluate(mutated)
    assert any(
        str(case["expected_failure_family"]) in failure
        for failure in failures
    ), (case["case_id"], failures)
    assert evaluate(baseline) == (), case["case_id"]


@pytest.mark.parametrize(
    "case",
    V05_NEW_FOCUSED_CASES,
    ids=tuple(str(case["case_id"]) for case in V05_NEW_FOCUSED_CASES),
)
def test_v05_focused_semantic_normal_form_case(
    tmp_path: Path,
    case: dict[str, object],
) -> None:
    namespace = _phase_contract_namespace()

    def evaluate(source: str) -> tuple[str, ...]:
        helper = case["production_helper"]
        if helper == "_validate_post_e6_test_contract_v02":
            path = tmp_path / "post_contract.py"
            path.write_text(source, encoding="utf-8")
            return namespace[helper](path, living=case["living"])
        if helper == "_phase_critical_assignments_v02":
            _values, _nodes, failures = _critical_extract(
                tmp_path,
                source,
                frozenset({str(case["binding"])}),
            )
            return failures
        assert helper == "_validate_historical_non_rebinding_v02"
        return _historical_scan_failures(
            source,
            label=str(case["surface"]),
        )

    baseline = str(case["baseline"])
    mutated = str(case["mutated"])
    assert evaluate(baseline) == (), case["case_id"]
    failures = evaluate(mutated)
    assert any(
        str(case["expected_failure_family"]) in failure
        for failure in failures
    ), (case["case_id"], failures)
    assert evaluate(baseline) == (), case["case_id"]
    if case.get("sentinel_kind") is not None:
        _run_v05_executable_sentinel(tmp_path, case)


@pytest.mark.parametrize(
    "case",
    V06_NEW_FOCUSED_CASES,
    ids=tuple(str(case["case_id"]) for case in V06_NEW_FOCUSED_CASES),
)
def test_v06_assertion_tail_normal_form_case(
    tmp_path: Path,
    case: dict[str, object],
) -> None:
    namespace = _phase_contract_namespace()
    helper = namespace["_validate_post_e6_test_contract_v02"]
    assert Path(helper.__code__.co_filename).resolve() == GUARD_PATH
    path = tmp_path / "post_contract.py"
    baseline = str(case["baseline"])
    path.write_text(baseline, encoding="utf-8")
    assert helper(path, living=case["living"]) == (), case["case_id"]
    path.write_text(str(case["mutated"]), encoding="utf-8")
    failures = helper(path, living=case["living"])
    assert any(
        str(case["expected_failure_family"]) in failure
        for failure in failures
    ), (case["case_id"], failures)
    path.write_text(baseline, encoding="utf-8")
    assert helper(path, living=case["living"]) == (), case["case_id"]


@pytest.mark.parametrize("living", (True, False))
def test_v04_positive_public_module_and_independent_spy_provenance(
    tmp_path: Path,
    living: bool,
) -> None:
    namespace = _phase_contract_namespace()
    for index, source in enumerate(
        (
            _post_contract_source(living=living, module_import=True),
            _post_contract_source(living=living, transparent_spy=True),
        )
    ):
        path = tmp_path / f"positive_{living}_{index}.py"
        path.write_text(source, encoding="utf-8")
        assert namespace["_validate_post_e6_test_contract_v02"](
            path, living=living
        ) == ()


@pytest.mark.parametrize("label", tuple(HISTORICAL_SURFACE_PATHS))
def test_v04_serialized_historical_evidence_may_return_inertly(
    label: str,
) -> None:
    baseline = _historical_surface_source(label, "PRE_E6_RECONCILED")
    binding = HISTORICAL_PRIMARY_BINDINGS[label]
    source = baseline + (
        "\nimport json\n"
        "def serialize_inert_history_v04():\n"
        f"    encoded = json.dumps({binding})\n"
        "    return encoded\n"
    )
    assert _historical_scan_failures(source, label=label) == ()


@pytest.mark.parametrize("living", (True, False))
@pytest.mark.parametrize("operator", ("len", "set", "tuple"))
def test_v05_unrelated_nested_scope_preserves_post_builtin_authority(
    tmp_path: Path,
    living: bool,
    operator: str,
) -> None:
    baseline = _post_contract_source(living=living)
    source = _v04_insert_module_block(
        baseline,
        living=living,
        block=(
            f"def unrelated_scope({operator}):\n"
            f"    return {operator}"
        ),
    )
    path = tmp_path / "scope_separated_post_contract.py"
    path.write_text(source, encoding="utf-8")
    namespace = _phase_contract_namespace()
    assert namespace["_validate_post_e6_test_contract_v02"](
        path, living=living
    ) == ()


@pytest.mark.parametrize(("surface", "binding"), MUTABLE_CRITICAL_SURFACES)
def test_v05_unrelated_nested_scope_preserves_critical_builtin_authority(
    tmp_path: Path,
    surface: str,
    binding: str,
) -> None:
    del surface
    source = (
        f"{binding} = {{'stable': ('module', 'symbol')}}\n"
        "def unrelated_scope(tuple):\n"
        "    return tuple\n"
        f"keys = tuple({binding})\n"
    )
    _values, _nodes, failures = _critical_extract(
        tmp_path, source, frozenset({binding})
    )
    assert failures == ()


@pytest.mark.parametrize("label", tuple(HISTORICAL_SURFACE_PATHS))
@pytest.mark.parametrize("shadow_form", ("parameter", "import", "alias"))
def test_v05_unrelated_nested_scope_preserves_outer_json_authority(
    label: str,
    shadow_form: str,
) -> None:
    baseline = _historical_surface_source(label, "PRE_E6_RECONCILED")
    binding = HISTORICAL_PRIMARY_BINDINGS[label]
    if shadow_form == "parameter":
        unrelated = "def unrelated_scope(dumps):\n    return dumps\n"
    elif shadow_form == "import":
        unrelated = (
            "def unrelated_scope():\n"
            "    import fabricated as dumps\n"
            "    return dumps\n"
        )
    else:
        unrelated = (
            "def unrelated_scope():\n"
            "    dumps = object()\n"
            "    return dumps\n"
        )
    json_import = "" if "import json\n" in baseline else "import json\n"
    source = baseline + (
        "\n"
        + json_import
        + unrelated
        + "def serialize_outer_history_v05():\n"
        + f"    encoded = json.dumps({binding})\n"
        + "    print(encoded)\n"
        + "    return encoded\n"
    )
    assert _historical_scan_failures(source, label=label) == ()


@pytest.mark.parametrize(
    "source",
    (
        'CURRENT = ("all_layers_invariant_super_smoke",)\n',
        'CURRENT = ["all_layers_invariant_super_smoke"]\n',
        'CURRENT_SOURCES = {"all_layers_invariant_super_smoke": ("m", "f")}\n',
        'CURRENT_SEAMS = {"x": ("demo.run_all_layers_applied_super_smoke", "f")}\n',
        'import demo.run_all_layers_applied_super_smoke\n',
        'from demo import run_all_layers_applied_super_smoke as historical\n',
        'from demo.run_all_layers_applied_super_smoke import collect_all_layers_applied_super_smoke\n',
        'importlib.import_module("demo.run_all_layers_applied_super_smoke")\n',
        'MODULE = "demo.run_all_layers_" + "applied_super_smoke"\nimportlib.import_module(MODULE)\n',
        'alias = collect_all_layers_applied_super_smoke\n',
        'collect_all_layers_applied_super_smoke()\n',
        'legacy.collect_all_layers_applied_super_smoke()\n',
    ),
)
@pytest.mark.parametrize(
    "label",
    ("living_gauntlet", "kernel_conformance", "kernel_conformance_runner"),
)
def test_historical_runner_cannot_reenter_any_post_source(
    source: str,
    label: str,
) -> None:
    assert _historical_scan_failures(source, label=label)


def _write_alternate(tmp_path: Path) -> None:
    real_objects = subprocess.run(
        ("git", "rev-parse", "--path-format=absolute", "--git-path", "objects"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    path = tmp_path / ".git/objects/info/alternates"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(real_objects + "\n", encoding="ascii")


def _basis_failures(root: Path) -> tuple[str, ...]:
    namespace = _phase_contract_namespace()
    failures: list[str] = []
    namespace["_validate_e5_basis_ancestry_v02"](root, failures)
    return tuple(failures)


def test_basis_equal_to_head_passes(isolated_control_plane: Path) -> None:
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=isolated_control_plane,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head == E5_IMPLEMENTATION_BASIS_COMMIT
    assert _basis_failures(isolated_control_plane) == ()


def test_local_basis_descendant_passes(
    isolated_clean_e5_control_plane: Path,
) -> None:
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=isolated_clean_e5_control_plane,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head != E5_IMPLEMENTATION_BASIS_COMMIT
    assert _basis_failures(isolated_clean_e5_control_plane) == ()


def test_missing_basis_object_without_origin_fails(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    (tmp_path / "x").write_text("x\n", encoding="ascii")
    subprocess.run(("git", "add", "x"), cwd=tmp_path, check=True)
    subprocess.run(
        (
            "git", "-c", "user.name=Guard", "-c",
            "user.email=guard@example.invalid", "commit", "-q", "-m", "root",
        ),
        cwd=tmp_path,
        check=True,
    )
    assert _basis_failures(tmp_path) == ("e6.committed_e5.basis_object_missing",)


def test_present_basis_on_non_descendant_head_fails(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    _write_alternate(tmp_path)
    empty_tree = subprocess.run(
        ("git", "mktree"), cwd=tmp_path, input=b"", check=True, capture_output=True
    ).stdout.decode("ascii").strip()
    environment = dict(os.environ)
    environment.update(
        {
            "GIT_AUTHOR_NAME": "Guard",
            "GIT_AUTHOR_EMAIL": "guard@example.invalid",
            "GIT_COMMITTER_NAME": "Guard",
            "GIT_COMMITTER_EMAIL": "guard@example.invalid",
        }
    )
    commit = subprocess.run(
        ("git", "commit-tree", empty_tree, "-m", "unrelated"),
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    ).stdout.strip()
    subprocess.run(("git", "update-ref", "refs/heads/main", commit), cwd=tmp_path, check=True)
    subprocess.run(("git", "symbolic-ref", "HEAD", "refs/heads/main"), cwd=tmp_path, check=True)
    assert _basis_failures(tmp_path) == ("e6.committed_e5.basis_not_ancestor",)


def test_present_basis_with_missing_head_and_git_error_fail(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(("git", "init", "-q"), cwd=repository, check=True)
    _write_alternate(repository)
    assert _basis_failures(repository) == (
        "e6.committed_e5.ancestry_indeterminate:exit_128",
    )
    not_repository = tmp_path / "not_repository"
    not_repository.mkdir()
    assert _basis_failures(not_repository) == (
        "e6.committed_e5.git_object:exit_128",
    )
