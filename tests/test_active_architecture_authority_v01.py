from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = REPOSITORY_ROOT / "tools/check_active_architecture_authority_v01.py"
DEFERRED_E5_PATHS = (
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
    for relative_path in CONTROL_PATHS:
        source = REPOSITORY_ROOT / relative_path
        destination = tmp_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    subprocess.run(
        ("git", "init", "-q"),
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    exclude_path = tmp_path / ".git/info/exclude"
    exclude_path.write_text(
        exclude_path.read_text(encoding="utf-8")
        + "\n"
        + "\n".join(READ_ONLY_CONTROL_PATHS)
        + "\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def isolated_clean_e5_control_plane(isolated_control_plane: Path) -> Path:
    deferred_demo = isolated_control_plane / DEFERRED_E5_PATHS[2]
    deferred_demo.parent.mkdir(parents=True, exist_ok=True)
    deferred_demo.write_text(
        "# Isolated deferred-E5 demo placeholder.\n",
        encoding="utf-8",
    )
    subprocess.run(
        ("git", "add", "-f", "--", "."),
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
            "isolated control-plane baseline",
        ),
        cwd=isolated_control_plane,
        check=True,
        capture_output=True,
        text=True,
    )
    return isolated_control_plane


def _dirty_deferred_e5_paths(root: Path, relative_paths: tuple[str, ...]) -> None:
    for index, relative_path in enumerate(relative_paths):
        path = root / relative_path
        path.write_text(
            path.read_text(encoding="utf-8")
            + f"\n# isolated deferred-E5 dirt {index}\n",
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
    assert completed.stdout == "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"
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


def test_exact_approved_g2b_test_path_is_accepted(
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

    assert completed.returncode == 0, completed.stdout
    assert completed.stdout == "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"


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
        not in completed.stdout
    )


def test_removing_exact_g2b_path_from_allowlist_while_dirty_fails(
    isolated_control_plane: Path,
) -> None:
    local_guard = (
        isolated_control_plane / "tools/check_active_architecture_authority_v01.py"
    )
    guard_source = local_guard.read_text(encoding="utf-8")
    allowlist_entry = (
        '        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",\n'
    )
    assert allowlist_entry in guard_source
    local_guard.write_text(
        guard_source.replace(allowlist_entry, "", 1),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane, guard_path=local_guard)

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


def test_all_exact_deferred_e5_paths_may_be_dirty(
    isolated_clean_e5_control_plane: Path,
) -> None:
    _dirty_deferred_e5_paths(
        isolated_clean_e5_control_plane,
        DEFERRED_E5_PATHS,
    )
    assert _short_status_paths(isolated_clean_e5_control_plane) == set(
        DEFERRED_E5_PATHS
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 0, completed.stdout
    assert completed.stdout == "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"


@pytest.mark.parametrize(
    "dirty_paths",
    (
        (DEFERRED_E5_PATHS[0],),
        (DEFERRED_E5_PATHS[1],),
        (DEFERRED_E5_PATHS[2],),
        (DEFERRED_E5_PATHS[0], DEFERRED_E5_PATHS[1]),
        (DEFERRED_E5_PATHS[0], DEFERRED_E5_PATHS[2]),
        (DEFERRED_E5_PATHS[1], DEFERRED_E5_PATHS[2]),
    ),
)
def test_any_one_or_two_exact_deferred_e5_paths_may_be_dirty(
    isolated_clean_e5_control_plane: Path,
    dirty_paths: tuple[str, ...],
) -> None:
    _dirty_deferred_e5_paths(isolated_clean_e5_control_plane, dirty_paths)
    assert _short_status_paths(isolated_clean_e5_control_plane) == set(
        dirty_paths
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 0, completed.stdout
    assert completed.stdout == "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"


def test_exact_deferred_e5_set_plus_unexpected_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    _dirty_deferred_e5_paths(
        isolated_clean_e5_control_plane,
        DEFERRED_E5_PATHS,
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


def test_renaming_deferred_e5_path_to_unapproved_neighbor_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    source = DEFERRED_E5_PATHS[2]
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


def test_noncanonical_dot_slash_deferred_e5_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["deferred_e5_transplant"][0]["path"] == (
        DEFERRED_E5_PATHS[0]
    )
    manifest["deferred_e5_transplant"][0]["path"] = (
        "./" + DEFERRED_E5_PATHS[0]
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.deferred_e5_transplant[0].path"
        in completed.stdout
    )
    assert (
        "successor_manifest.deferred_e5_transplant.paths"
        in completed.stdout
    )


def test_dot_slash_unexpected_changed_path_fails_exact_membership() -> None:
    guard_namespace = runpy.run_path(str(GUARD_PATH))
    failures: list[str] = []

    guard_namespace["_validate_changed_paths"](
        {"./unexpected_post_s3.py"},
        DEFERRED_E5_PATHS,
        failures,
    )

    assert failures == [
        "worktree.unexpected_changed_path:./unexpected_post_s3.py"
    ]


def test_removed_manifest_e5_path_cannot_authorize_its_dirt(
    isolated_clean_e5_control_plane: Path,
) -> None:
    removed_path = DEFERRED_E5_PATHS[2]
    manifest_path = (
        isolated_clean_e5_control_plane
        / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["deferred_e5_transplant"] = [
        entry
        for entry in manifest["deferred_e5_transplant"]
        if entry["path"] != removed_path
    ]
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _dirty_deferred_e5_paths(
        isolated_clean_e5_control_plane,
        (removed_path,),
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "successor_manifest.deferred_e5_transplant.paths"
        in completed.stdout
    )
    assert (
        f"worktree.unexpected_changed_path:{removed_path}"
        in completed.stdout
    )


def test_retired_import_in_allowed_e5_path_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    runtime_path = isolated_clean_e5_control_plane / DEFERRED_E5_PATHS[0]
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
    runtime_path = isolated_clean_e5_control_plane / DEFERRED_E5_PATHS[0]
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
        + DEFERRED_E5_PATHS[0]
        + ":0"
        in completed.stdout
    )


def test_provider_owned_topology_claim_in_allowed_e5_runtime_fails(
    isolated_clean_e5_control_plane: Path,
) -> None:
    runtime_path = isolated_clean_e5_control_plane / DEFERRED_E5_PATHS[0]
    runtime_path.write_text(
        runtime_path.read_text(encoding="utf-8")
        + "\n_PROVIDER_OWNED_TOPOLOGY = True\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_clean_e5_control_plane)

    assert completed.returncode == 1
    assert (
        "s3.e5_runtime.provider_owned_topology:"
        + DEFERRED_E5_PATHS[0]
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


def test_historical_retired_import_outside_successor_scope_is_allowed(
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

    assert completed.returncode == 0, completed.stdout


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
