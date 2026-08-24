from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = REPOSITORY_ROOT / "tools/check_active_architecture_authority_v01.py"
CONTROL_PATHS = (
    "AGENTS.md",
    "README.md",
    "demo/run_full_wow_v1_2_product_trace.py",
    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
    (
        "hedgehog/domains/supplier_water_filter/"
        "sealed_evidence_package_adapter_v01.py"
    ),
    "hedgehog/structured_rationale.py",
    "specs/current_architecture_lock_v01.md",
    "specs/document_authority_index_v01.json",
    "release/successor_context_manifest_v01.json",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_full_wow_v1_2_product_trace_runner.py",
    "tests/test_repository_release_spine_v01.py",
    "tests/test_semantic_reasoning_adapter_core.py",
    "tests/test_structured_rationale_core.py",
    "tests/test_supplier_water_filter_kernel_adapter_v01.py",
    (
        "tests/"
        "test_supplier_water_filter_sealed_evidence_package_adapter_v01.py"
    ),
    "tools/check_active_architecture_authority_v01.py",
)
READ_ONLY_CONTROL_PATHS = (
    "README.md",
    "specs/current_architecture_lock_v01.md",
)
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


def _run_guard(root: Path) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(GUARD_PATH), "--root", str(root)]
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


def test_onboarding_ready_true_with_blocking_repairs_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["blocking_repairs"]
    manifest["onboarding_ready"] = True
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.onboarding_ready" in completed.stdout


def test_blocking_repairs_removed_while_onboarding_not_ready_fails(
    isolated_control_plane: Path,
) -> None:
    manifest_path = (
        isolated_control_plane / "release/successor_context_manifest_v01.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["onboarding_ready"] is False
    manifest["blocking_repairs"] = []
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert "successor_manifest.blocking_repairs.exact" in completed.stdout


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


def test_agents_missing_s3_warning_fails(
    isolated_control_plane: Path,
) -> None:
    agents_path = isolated_control_plane / "AGENTS.md"
    original = agents_path.read_text(encoding="utf-8")
    warning = "`S3_ACTIVE_SCHEMA_AND_LEGACY_ISOLATION` remains blocking."
    assert warning in original
    agents_path.write_text(
        original.replace(warning, "removed S3 warning"),
        encoding="utf-8",
    )

    completed = _run_guard(isolated_control_plane)

    assert completed.returncode == 1
    assert (
        "current_document.missing_onboarding_warning:AGENTS.md:s3_blocking"
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
