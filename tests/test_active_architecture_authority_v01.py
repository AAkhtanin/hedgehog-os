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
G2E_CLOSURE_COMMIT = "282e319241946b34987b2533d95ed514c3d884c1"
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
G2F_CLASS_A_PATHS = (
    "docs/consolidated_gate2_gauntlet_g2_f_preflight_v01.md",
    "specs/current_architecture_lock_v01.md",
    "specs/document_authority_index_v01.json",
    "release/successor_context_manifest_v01.json",
    "tools/check_active_architecture_authority_v01.py",
    "tests/test_active_architecture_authority_v01.py",
    "tests/test_repository_release_spine_v01.py",
)
G2F_IMPLEMENTATION_PATHS = (
    "demo/run_consolidated_gate2_gauntlet_g2_f_v01.py",
    "tests/test_consolidated_gate2_gauntlet_g2_f_v01.py",
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


G2F_PREFLIGHT_PATH = "docs/consolidated_gate2_gauntlet_g2_f_preflight_v01.md"
G2F_CLOSURE_BASIS = "90cb073695bf8c5f5a2673c7aba84b6615719b37"
G2F_CLOSURE_MAINTENANCE = "5d6fd6d98f3412a1d999bfe84101cabe39301573"
G2F_CLOSURE_ADDS = (
    "docs/audit_reports/auditor_consolidated_gate2_gauntlet_g2_f_v01.log",
    "docs/consolidated_gate2_gauntlet_g2_f_checkpoint_v01.md",
)
G2F_CLOSURE_PATHS = tuple(sorted((*G2F_CLOSURE_ADDS, *(p for p in CLASS_D_PATHS if p not in CLASS_D_PATHS[:2]))))


U1_CONTRACT_BASIS = "19de35c3b77725c4763b33cbac5c42118fd3c382"
U1_CONTRACT_DOC = "docs/common_action_and_dynamic_composition_contract_v01.md"
U1_CONTRACT_PATHS = tuple(sorted((U1_CONTRACT_DOC, "AGENTS.md", "README.md", "specs/current_architecture_lock_v01.md", "specs/document_authority_index_v01.json", "release/successor_context_manifest_v01.json", "tools/check_active_architecture_authority_v01.py", "tests/test_active_architecture_authority_v01.py", "tests/test_repository_release_spine_v01.py")))


def _expected_g2f_landing_stdout_v01(root: Path) -> str:
    """Independent expectation from Git facts, never from guard output/mode."""
    def git(*args: str) -> str:
        return subprocess.check_output(("git", *args), cwd=root, text=True).strip()

    basis = "779641d1a2e1c256c8232655d02124b66e3657b3"
    original = "c3f2cd379bcebc71e46e83f44aee0b68d76ae5ce"
    head, parent, grandparent = (git("rev-parse", r) for r in ("HEAD", "HEAD^", "HEAD^^"))
    origin = git("rev-parse", "refs/remotes/origin/main")
    assert git("branch", "--show-current") == "main"
    assert len(git("rev-list", "--parents", "-n", "1", "HEAD").split()) == 2
    raw = subprocess.check_output(("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"), cwd=root)
    status = dict((item[3:].decode(), item[:2].decode()) for item in raw.split(b"\0") if item)
    controls = {path: "M" for path in G2F_CLASS_A_PATHS}
    candidate = {path: "??" for path in G2F_IMPLEMENTATION_PATHS}
    ledger = dict(line.split("\t")[::-1] for line in git("diff", "--no-renames", "--name-status", "HEAD^", "HEAD").splitlines())
    prepush = False
    closure_ledger = {p: "A" if p in G2F_CLOSURE_ADDS else "M" for p in G2F_CLOSURE_PATHS}
    overlay = json.loads((root / "release/current_status_overlay_v01.json").read_text())
    if "ephemeral_workspace_admission_v01" in overlay:
        actions = overlay["ephemeral_workspace_admission_v01"]["path_actions"]
        base = "e42d37fa98dfec7110b8cf75b1aceaa614f461be"
        if head == base:
            assert parent == "54e32dbcc0e4d68431ec2b9428eac965f88ee47c" and origin == base
            unstaged = {p: "??" if op == "A" else " M" for p, op in actions.items()}
            staged = {p: op + " " for p, op in actions.items()}
            assert status in (unstaged, staged)
            phase = "EWS_ADMISSION_CANDIDATE_UNSTAGED" if status == unstaged else "EWS_ADMISSION_CANDIDATE_STAGED"
        else:
            assert parent == base and not status and ledger == actions and origin in (base, head)
            phase = "EWS_IMPLEMENTATION_ADMITTED_COMMITTED"
        return "G2F_PHASE=G2F_CLOSED_PASS_COMMITTED\nUNIVERSALITY_PHASE=U4_IMPLEMENTATION_ADMITTED_COMMITTED\nTESTFLIX_PHASE=TESTFLIX_IMPLEMENTATION_ADMITTED_COMMITTED\nEPHEMERAL_WORKSPACE_PHASE=" + phase + "\n"
    if "testflix_admission_v11" in overlay:
        metadata = overlay["testflix_admission_v11"]
        actions = metadata["path_actions"]
        basis_l = "54e32dbcc0e4d68431ec2b9428eac965f88ee47c"
        if head == basis_l:
            assert parent == "20d16af823ed4af94dc0a342c731aef81e8a23de" and origin == basis_l
            unstaged = {p: "??" if op == "A" else " M" for p, op in actions.items()}
            staged = {p: op + " " for p, op in actions.items()}
            assert status in (unstaged, staged)
            phase = "TESTFLIX_ADMISSION_CANDIDATE_UNSTAGED" if status == unstaged else "TESTFLIX_ADMISSION_CANDIDATE_STAGED"
        else:
            assert parent == basis_l and not status and ledger == actions and origin in (basis_l, head)
            phase = "TESTFLIX_IMPLEMENTATION_ADMITTED_COMMITTED"
        return "G2F_PHASE=G2F_CLOSED_PASS_COMMITTED\nUNIVERSALITY_PHASE=U4_IMPLEMENTATION_ADMITTED_COMMITTED\nTESTFLIX_PHASE=" + phase + "\n"
    if (root / "docs/common_action_and_dynamic_composition_checkpoint_v01.md").exists():
        metadata = json.loads((root / "release/current_status_overlay_v01.json").read_text())["universality_admission_v01"]
        actions = metadata["path_actions"]
        h = "20d16af823ed4af94dc0a342c731aef81e8a23de"
        if head == h:
            assert parent == U1_CONTRACT_BASIS and origin == h
            unstaged = {p: "??" if op == "A" else " M" for p,op in actions.items()}
            staged = {p: op + " " for p,op in actions.items()}
            assert status in (unstaged, staged)
            phase = "U4_ADMISSION_CANDIDATE_UNSTAGED" if status == unstaged else "U4_ADMISSION_CANDIDATE_STAGED"
        else:
            assert parent == h and not status and ledger == actions and origin in (h,head)
            phase = "U4_IMPLEMENTATION_ADMITTED_COMMITTED"
        return "G2F_PHASE=G2F_CLOSED_PASS_COMMITTED\nUNIVERSALITY_PHASE=" + phase + "\n"
    if (root / U1_CONTRACT_DOC).exists():
        exact_delta = {p: "A" if p == U1_CONTRACT_DOC else "M" for p in U1_CONTRACT_PATHS}
        if head == U1_CONTRACT_BASIS:
            assert parent == G2F_CLOSURE_BASIS and origin == head
            unstaged = {p: "??" if p == U1_CONTRACT_DOC else " M" for p in U1_CONTRACT_PATHS}
            staged = {p: "A " if p == U1_CONTRACT_DOC else "M " for p in U1_CONTRACT_PATHS}
            assert status in (unstaged, staged)
            u1_phase = "U1_CONTRACT_CANDIDATE_UNSTAGED" if status == unstaged else "U1_CONTRACT_CANDIDATE_STAGED"
        else:
            assert parent == U1_CONTRACT_BASIS and not status
            assert ledger == exact_delta and origin in (parent, head)
            u1_phase = "U1_CONTRACT_COMMITTED"
        return "G2F_PHASE=G2F_CLOSED_PASS_COMMITTED\n" + f"UNIVERSALITY_PHASE={u1_phase}\n"
    if head == G2F_CLOSURE_BASIS and status:
        assert parent == G2F_CLOSURE_MAINTENANCE and grandparent == basis
        assert status == {p: "??" if p in G2F_CLOSURE_ADDS else " M" for p in G2F_CLOSURE_PATHS}
        assert ledger == {p: "A" for p in G2F_IMPLEMENTATION_PATHS}
        phase = "G2F_CLOSURE_CANDIDATE"
    elif parent == G2F_CLOSURE_BASIS:
        assert grandparent == G2F_CLOSURE_MAINTENANCE and not status
        assert ledger == closure_ledger
        phase = "G2F_CLOSED_PASS_COMMITTED"
        prepush = True
    elif head == basis and status == {**{p: " M" for p in controls}, **candidate}:
        assert ledger == controls
        phase = "G2F_LANDING_MAINTENANCE_CANDIDATE"
    elif parent == basis and ledger == controls:
        assert status == candidate
        phase = "G2F_LANDING_MAINTENANCE_COMMITTED"
        prepush = True
    elif status == candidate:
        assert parent == original and ledger == controls
        phase = "G2F_IMPLEMENTATION_CANDIDATE"
    elif not status and ledger == {p: "A" for p in G2F_IMPLEMENTATION_PATHS}:
        previous = dict(line.split("\t")[::-1] for line in git("diff", "--no-renames", "--name-status", "HEAD^^", "HEAD^").splitlines())
        assert previous == controls
        assert grandparent in {basis, original}
        phase = "G2F_IMPLEMENTATION_COMMITTED"
        prepush = grandparent == basis
    elif not status and parent == original:
        assert ledger == controls
        phase = "G2F_CLASS_A_181_ROW_RECONCILIATION_COMMITTED"
    else:
        assert not status and head == original
        phase = "G2F_ORIGINAL_CLASS_A_COMMITTED_SUPERSEDED"
    assert origin == head or (prepush and origin == parent)
    return f"G2F_PHASE={phase}\n"


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
    g2f_output = ""
    if (REPOSITORY_ROOT / "docs/common_action_and_dynamic_composition_checkpoint_v01.md").exists() or dirty_paths == set(U1_CONTRACT_PATHS) or dirty_paths == set(G2F_CLOSURE_PATHS) or dirty_paths & set(G2F_IMPLEMENTATION_PATHS) or (
        not dirty_paths and (REPOSITORY_ROOT / G2F_PREFLIGHT_PATH).exists()
    ):
        lifecycle_mode = "G2E_CLOSED_PASS_COMMITTED"
        g2f_output = _expected_g2f_landing_stdout_v01(REPOSITORY_ROOT)
    elif dirty_paths == set(G2F_CLASS_A_PATHS):
        lifecycle_mode = "G2E_CLOSED_PASS_COMMITTED"
        g2f_output = (
            "G2F_PHASE="
            "G2F_CLASS_A_181_ROW_RECONCILIATION_CANDIDATE\n"
        )
    elif dirty_paths:
        assert dirty_paths == set(CLASS_D_PATHS)
        lifecycle_mode = "G2E_CLOSED_PASS_CANDIDATE"
    else:
        lifecycle_mode = "G2E_CLOSED_PASS_COMMITTED"
    assert completed.stdout == (
        "ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS\n"
        "CURRENT_PHASE=POST_E6_SUCCESSOR\n"
        "LIFECYCLE_PHASE=G2E_CLOSED_PASS\n"
        f"LIFECYCLE_MODE={lifecycle_mode}\n"
        f"{g2f_output}"
    )
    assert completed.stderr == ""


def test_g2f_landing_exact_transition_ledger_contract() -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    classify = namespace["_classify_g2f_path_ledger_v01"]
    basis = "779641d1a2e1c256c8232655d02124b66e3657b3"
    original = "c3f2cd379bcebc71e46e83f44aee0b68d76ae5ce"
    # Abstract ledger inputs only: these are not claimed owner commit IDs.
    maintenance, implementation = "a" * 40, "b" * 40
    controls = tuple(("M", p, None) for p in sorted(G2F_CLASS_A_PATHS))
    files = tuple(("??", p, None) for p in sorted(G2F_IMPLEMENTATION_PATHS))
    adds = tuple(("A", p, None) for p in sorted(G2F_IMPLEMENTATION_PATHS))
    original_ledger = tuple(("A" if p == G2F_PREFLIGHT_PATH else "M", p, None) for p in sorted(G2F_CLASS_A_PATHS))
    for head, parent, grandparent, origin, worktree, commit, previous, expected in (
        (basis, original, G2E_CLOSURE_COMMIT, basis, files, controls, original_ledger, "G2F_IMPLEMENTATION_CANDIDATE"),
        (basis, original, G2E_CLOSURE_COMMIT, basis, tuple((" M", p, None) for p in sorted(G2F_CLASS_A_PATHS)) + files, controls, original_ledger, "G2F_LANDING_MAINTENANCE_CANDIDATE"),
        (maintenance, basis, original, basis, files, controls, controls, "G2F_LANDING_MAINTENANCE_COMMITTED"),
        (maintenance, basis, original, maintenance, files, controls, controls, "G2F_LANDING_MAINTENANCE_COMMITTED"),
        (implementation, maintenance, basis, maintenance, (), adds, controls, "G2F_IMPLEMENTATION_COMMITTED"),
        (implementation, maintenance, basis, implementation, (), adds, controls, "G2F_IMPLEMENTATION_COMMITTED"),
    ):
        mode, failures = classify(requested=True, head=head, parent=parent, grandparent=grandparent, branch="main", origin_main=origin, worktree_entries=worktree, head_commit_entries=commit, parent_commit_entries=previous)
        assert mode == expected
        assert failures == ()


def test_g2f_landing_transition_neighbors_fail_closed() -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    classify = namespace["_classify_g2f_path_ledger_v01"]
    controls = tuple(("M", p, None) for p in sorted(G2F_CLASS_A_PATHS))
    adds = tuple(("A", p, None) for p in sorted(G2F_IMPLEMENTATION_PATHS))
    clean = dict(requested=True, head="b" * 40, parent="a" * 40, grandparent="779641d1a2e1c256c8232655d02124b66e3657b3", branch="main", origin_main="a" * 40, worktree_entries=(), head_commit_entries=adds, parent_commit_entries=controls)
    mutations = (
        {"branch": "foreign"}, {"origin_main": "f" * 40},
        {"origin_main": clean["grandparent"]}, {"parent_count": 2},
        {"parent_parent_count": 2}, {"grandparent": "e" * 40},
        {"head_commit_entries": adds[:-1]},
        {"head_commit_entries": adds + (("M", "AGENTS.md", None),)},
        {"head_commit_entries": (("M", adds[0][1], None), adds[1])},
        {"head_commit_entries": (("R100", adds[0][1], "old.py"), adds[1])},
        {"parent_commit_entries": controls[:-1]},
        {"worktree_entries": (("??", "extra.txt", None),)},
        {"worktree_entries": (("M ", "AGENTS.md", None),)},
    )
    assert classify(**clean)[1] == ()
    for mutation in mutations:
        assert classify(**{**clean, **mutation})[1], mutation
    # Preserve the older recognized pushed topology, but do not grant it the
    # new sequence's pre-push allowance without a maintenance predecessor.
    legacy = {**clean, "parent": clean["grandparent"], "grandparent": "c3f2cd379bcebc71e46e83f44aee0b68d76ae5ce", "origin_main": clean["head"]}
    assert classify(**legacy)[1] == ()
    assert "g2f.implementation_committed.origin_main" in classify(**{**legacy, "origin_main": legacy["parent"]})[1]


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


def test_class_a_and_class_b_path_sets_are_exact_and_disjoint(
    tmp_path: Path,
) -> None:
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

    assert namespace["G2F_CLASS_A_PATHS"] == frozenset(G2F_CLASS_A_PATHS)
    assert namespace["G2F_IMPLEMENTATION_PATHS"] == frozenset(
        G2F_IMPLEMENTATION_PATHS
    )
    assert len(namespace["G2F_CLASS_A_PATHS"]) == 7
    assert len(namespace["G2F_IMPLEMENTATION_PATHS"]) == 2
    assert len(namespace["G2F_CLOSURE_PATHS"]) == 14
    assert len(namespace["G2F_CLOSURE_OVERLAP_PATHS"]) == 6
    assert not (
        namespace["G2F_IMPLEMENTATION_PATHS"]
        & namespace["G2F_CLASS_A_PATHS"]
    )

    original_class_a_commit = namespace["G2F_ORIGINAL_CLASS_A_COMMIT"]
    original_class_a_parent = namespace["G2F_ORIGINAL_CLASS_A_PARENT"]
    original_class_a_committed = {
        path: "A" if path.endswith("g2_f_preflight_v01.md") else "M"
        for path in G2F_CLASS_A_PATHS
    }
    repair_candidate = tuple(
        (" M", path, None) for path in sorted(G2F_CLASS_A_PATHS)
    )
    repair_committed = {path: "M" for path in G2F_CLASS_A_PATHS}
    g2f_classifier = namespace["_classify_g2f_path_ledger_v01"]

    mode, failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert mode == "G2F_ORIGINAL_CLASS_A_COMMITTED_SUPERSEDED"
    assert failures == ()

    mode, failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=repair_candidate,
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert mode == "G2F_CLASS_A_181_ROW_RECONCILIATION_CANDIDATE"
    assert failures == ()

    _mode, missing_failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=repair_candidate[1:],
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert any(
        "class_a_181_reconciliation_candidate.worktree.missing" in item
        for item in missing_failures
    )

    _mode, extra_failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=(*repair_candidate, ("??", "unexpected.txt", None)),
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert (
        "g2f.class_a_181_reconciliation_candidate.worktree.unexpected:unexpected.txt"
        in extra_failures
    )

    staged_repair = list(repair_candidate)
    staged_repair[0] = ("M ", staged_repair[0][1], None)
    _mode, staged_failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=tuple(staged_repair),
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert any(
        "class_a_181_reconciliation_candidate.worktree.status" in item
        for item in staged_failures
    )

    _mode, premature_implementation_failures = g2f_classifier(
        requested=True,
        head=original_class_a_commit,
        parent=original_class_a_parent,
        grandparent=G2E_CLOSURE_BASIS_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        worktree_entries=(
            *repair_candidate,
            *(("??", path, None) for path in G2F_IMPLEMENTATION_PATHS),
        ),
        head_commit_entries=_ledger_entries(original_class_a_committed),
        parent_commit_entries=(),
    )
    assert any(
        "class_a_181_reconciliation_candidate.worktree.unexpected" in item
        for item in premature_implementation_failures
    )

    repair_commit = "a" * 40
    mode, failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert mode == "G2F_CLASS_A_181_ROW_RECONCILIATION_COMMITTED"
    assert failures == ()

    _mode, repair_commit_missing = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(dict(list(repair_committed.items())[1:])),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert any(
        "class_a_181_reconciliation_committed.commit.missing" in item
        for item in repair_commit_missing
    )

    _mode, repair_commit_extra = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=(),
        head_commit_entries=(*_ledger_entries(repair_committed), ("M", "extra.txt", None)),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert (
        "g2f.class_a_181_reconciliation_committed.commit.unexpected:extra.txt"
        in repair_commit_extra
    )

    implementation_candidate = tuple(
        ("??", path, None) for path in sorted(G2F_IMPLEMENTATION_PATHS)
    )
    mode, failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=implementation_candidate,
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert mode == "G2F_IMPLEMENTATION_CANDIDATE"
    assert failures == ()

    _mode, missing_failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=implementation_candidate[1:],
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert any("implementation_candidate.worktree.missing" in item for item in missing_failures)

    _mode, extra_failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=(*implementation_candidate, ("??", "extra.py", None)),
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert "g2f.implementation_candidate.worktree.unexpected:extra.py" in extra_failures

    direct_implementation_commit = "d" * 40
    _mode, direct_implementation_failures = g2f_classifier(
        requested=True,
        head=direct_implementation_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=direct_implementation_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(
            {path: "A" for path in G2F_IMPLEMENTATION_PATHS}
        ),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert any(
        "class_a_181_reconciliation_committed.commit" in item
        for item in direct_implementation_failures
    )

    implementation_commit = "b" * 40
    mode, failures = g2f_classifier(
        requested=True,
        head=implementation_commit,
        parent=repair_commit,
        grandparent=original_class_a_commit,
        branch="main",
        origin_main=implementation_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(
            {path: "A" for path in G2F_IMPLEMENTATION_PATHS}
        ),
        parent_commit_entries=_ledger_entries(repair_committed),
    )
    assert mode == "G2F_IMPLEMENTATION_COMMITTED"
    assert failures == ()

    third_descendant = "c" * 40
    mode, failures = g2f_classifier(
        requested=True,
        head=third_descendant,
        parent=implementation_commit,
        grandparent=repair_commit,
        branch="main",
        origin_main=third_descendant,
        worktree_entries=(),
        head_commit_entries=(),
        parent_commit_entries=_ledger_entries(
            {path: "A" for path in G2F_IMPLEMENTATION_PATHS}
        ),
    )
    assert mode == "G2F_INVALID"
    assert "g2f.unrecognized_descendant_or_basis_not_exact" in failures

    _mode, merge_failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main=repair_commit,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
        parent_count=2,
    )
    assert "g2f.merge_or_parent_count:2" in merge_failures

    _mode, wrong_origin_failures = g2f_classifier(
        requested=True,
        head=repair_commit,
        parent=original_class_a_commit,
        grandparent=original_class_a_parent,
        branch="main",
        origin_main="f" * 40,
        worktree_entries=(),
        head_commit_entries=_ledger_entries(repair_committed),
        parent_commit_entries=_ledger_entries(original_class_a_committed),
    )
    assert "g2f.class_a_181_reconciliation_successor.origin_main" in (
        wrong_origin_failures
    )

    closure_classifier = namespace["_classify_g2e_closure_path_ledger_v01"]
    _mode, unapproved_ignore_failures = closure_classifier(
        closure_requested=True,
        head=original_class_a_commit,
        parent=G2E_CLOSURE_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        subject="Prepare G2-F Class A",
        committed_entries=_ledger_entries(
            {
                **class_a_and_b,
                **class_d_committed,
                **original_class_a_committed,
            }
        ),
        worktree_entries=(),
        closure_commit_entries=_ledger_entries(class_d_committed),
        g2e_closure_ancestor=True,
        g2f_topology_passed=False,
    )
    assert any(
        "g2e.closure.committed.cumulative.unexpected" in item
        for item in unapproved_ignore_failures
    )
    _mode, approved_ignore_failures = closure_classifier(
        closure_requested=True,
        head=original_class_a_commit,
        parent=G2E_CLOSURE_COMMIT,
        branch="main",
        origin_main=original_class_a_commit,
        subject="Prepare G2-F Class A",
        committed_entries=_ledger_entries(
            {
                **class_a_and_b,
                **class_d_committed,
                **original_class_a_committed,
            }
        ),
        worktree_entries=(),
        closure_commit_entries=_ledger_entries(class_d_committed),
        g2e_closure_ancestor=True,
        g2f_topology_passed=True,
    )
    assert approved_ignore_failures == ()

    missing_preflight_root = tmp_path / "removed_preflight"
    missing_preflight_root.mkdir()
    missing_preflight_failures: list[str] = []
    namespace["_validate_g2f_class_a_contract_v01"](
        missing_preflight_root,
        {},
        {},
        missing_preflight_failures,
        g2f_active=True,
    )
    assert any(
        item.startswith("g2f.class_a.preflight.read:")
        for item in missing_preflight_failures
    )

    preflight = (REPOSITORY_ROOT / G2F_CLASS_A_PATHS[0]).read_text(
        encoding="utf-8"
    )
    construction_rows = [
        line
        for line in preflight.splitlines()
        if len(line) > 4 and line[:3].isdigit() and line[3] == "|"
    ]
    assert len(construction_rows) == 181
    assert [row[:4] for row in construction_rows] == [
        f"{index:03d}|" for index in range(1, 182)
    ]

    def ledger_failures(source: str) -> tuple[str, ...]:
        observed: list[str] = []
        namespace["_validate_g2f_class_a_ledger_v13"](source, observed)
        return tuple(observed)

    row_lines = {int(row[:3]): row for row in construction_rows}
    deleted_row_failures = ledger_failures(
        preflight.replace(row_lines[27] + "\n", "", 1)
    )
    assert "g2f.class_a.preflight.construction_ledger.count:180" in (
        deleted_row_failures
    )

    added_row_failures = ledger_failures(
        preflight.replace(
            row_lines[181] + "\n",
            row_lines[181] + "\n" + row_lines[181].replace("181|", "182|", 1) + "\n",
            1,
        )
    )
    assert "g2f.class_a.preflight.construction_ledger.count:182" in (
        added_row_failures
    )

    reordered_row_failures = ledger_failures(
        preflight.replace(
            row_lines[27] + "\n" + row_lines[28] + "\n",
            row_lines[28] + "\n" + row_lines[27] + "\n",
            1,
        )
    )
    assert "g2f.class_a.preflight.construction_ledger.order" in (
        reordered_row_failures
    )

    producer_substitution_failures = ledger_failures(
        preflight.replace(
            row_lines[70],
            row_lines[70].replace(
                ":ActionCommitPacketV02|",
                ":build_supplier_a_mock_action_commit_packet_fixture_v02|",
                1,
            ),
            1,
        )
    )
    assert "g2f.class_a.preflight.row_070.exact" in (
        producer_substitution_failures
    )

    expected_row_083 = (
        "083|ROOT|packet_authorization_root_candidate_projection|"
        "hedgehog/action_commit_packet_v02.py:"
        "build_root_decision_candidate_projection_v01|"
        "validate_root_decision_candidate_projection_v01+"
        "validate_supplier_root_context_coherence_v01"
    )
    assert row_lines[83] == expected_row_083
    row_083_missing_context_failures = ledger_failures(
        preflight.replace(
            row_lines[83],
            row_lines[83].replace(
                "+validate_supplier_root_context_coherence_v01",
                "",
                1,
            ),
            1,
        )
    )
    assert "g2f.class_a.preflight.row_083.exact" in (
        row_083_missing_context_failures
    )
    row_083_extra_validator_failures = ledger_failures(
        preflight.replace(
            row_lines[83],
            row_lines[83] + "+validate_root_decision_result_v01",
            1,
        )
    )
    assert "g2f.class_a.preflight.row_083.exact" in (
        row_083_extra_validator_failures
    )

    row_099_fixture_failures = ledger_failures(
        preflight.replace(
            row_lines[99],
            row_lines[99].replace(
                ":CorridorStepV01|",
                ":build_supplier_a_corridor_step_fixture_v01|",
                1,
            ),
            1,
        )
    )
    assert "g2f.class_a.preflight.row_099.exact" in row_099_fixture_failures

    row_099_context_failures = ledger_failures(
        preflight.replace(
            row_lines[99],
            row_lines[99].replace(
                "validate_action_packet_present_eligibility_inspection_v01(enclosing_validator_at_row103)",
                "NONE",
                1,
            ),
            1,
        )
    )
    assert "g2f.class_a.preflight.row_099.exact" in row_099_context_failures

    validator_weakening_failures = ledger_failures(
        preflight.replace(
            row_lines[138],
            row_lines[138].replace(
                "+validate_revocation_root_context_coherence_v01",
                "",
                1,
            ),
            1,
        )
    )
    assert "g2f.class_a.preflight.row_138.exact" in (
        validator_weakening_failures
    )
    preflight_lines = set(preflight.splitlines())
    for marker in (
        "SHARED_REQUEST_ID=transaction:g2f:gate2:v01",
        "PARENT_MULTIROOT_CORRELATION_ID=transaction:g2f:gate2:v01",
        "CLIENT_LOCAL_TRANSACTION_ID=CLIENT_DRS_QUERY_ID",
        "SUPPLIER_LOCAL_TRANSACTION_ID=SUPPLIER_DRS_QUERY_ID",
        "ROOT_LOCAL_TRANSACTION_CARDINALITY=2",
        "PARENT_CORRELATION_CARDINALITY=1",
        "REQUEST_TO_PARENT_CORRELATION=SAME_TOKEN_DISTINCT_FIELD_ROLES",
        "PARENT_TOKEN_USED_AS_G2C_TRANSACTION=false",
    ):
        assert marker in preflight_lines
    assert "ROOT_SET=(root:g2f:client,root:g2f:supplier)" in preflight
    assert "PACKET_OWNER_ROOT=root:g2f:supplier" in preflight
    assert "DELTA_AFFECTED_ROOT_SET=(root:g2f:supplier)" in preflight
    assert (
        "THREAD_STATUS=V13R1_FULL_VALIDATOR_CLOSURE_REPAIRED_CANDIDATE"
        in preflight
    )
    assert "Row 083 binds rows 075, 081 and 082" in preflight
    assert (
        "supplier Root-context\nvalidation through "
        "`validate_supplier_root_context_coherence_v01`"
        in preflight
    )
    assert "MISSING_RUNTIME_SEAM=false" in preflight
    assert "OPEN_QUESTIONS=NONE" in preflight
    assert "24-node focused suite" in preflight
    assert "direct canonical report receipt" in preflight
    for marker in (
        "PUBLIC_CONSTRUCTION_LEDGER_ROWS=181",
        "CONSTRUCTION_LEDGER_CONSECUTIVE=true",
        "CURRENT_CLASS_A_POSTIMAGES_RECONCILED=true",
        "DIRECT_DECIDE_ROOT_RECEIPT_COUNT=8",
        "DIRECT_DECIDE_ROOT_LOGICAL_ROW_COUNT=7",
        "PRODUCER_BASIS_SHA256=f78aedd408138603d78f249178e171c48b0338e7aa331293f0832cbb27815b0d",
        "V12R6_FULL_CORRIDOR_EXTERNAL_PROOF_STATUS=DIRECT_AUTHORITY_FOR_V13_RECONCILIATION",
        "V13_INPUT_ARCHIVE_SHA256=854583db82779dea15aec2abff29944cc46e015a71234fcf61185f0fc2c1e6e7",
        "V13_OWNER_READINESS_STATUS=SUPERSEDED_BY_V13R1_VALIDATOR_CLOSURE",
        "V13R1_VALIDATOR_CLOSURE_STATUS=FULL_181_ROW_EXPECTED_SIDE_RECONSTRUCTED_CANDIDATE",
        "ROOT_LOCAL_RUNTIME_INVOCATIONS_EXPLICIT=2",
        "ROOT_LOCAL_G2B_FAMILY_COUNT=2",
        "ROOT_LOCAL_G2C_LANE_COUNT=2",
        "DISTINCT_ROOT_LOCAL_QUERY_TRANSACTIONS=2",
        "SHARED_REQUEST_COUNT=1",
        "PARENT_MULTIROOT_CORRELATION_COUNT=1",
        "PACKET_AUTHORIZATION_CHAIN_EXACT=true",
        "NONEXISTENT_CURRENT_G2F_VALIDATOR_REFERENCES=0",
        "STALE_PACKET_AUTHORIZATION_CONTRIBUTION_REUSE=false",
        "STALE_PACKET_AUTHORIZATION_DECISION_REUSE=false",
        "STALE_INVALIDATION_ROOT_DECISION_REUSE=false",
        "UNBOUND_LITERAL_INVALIDATION_EVIDENCE=false",
        "STALE_REVOCATION_ROOT_INPUT_REUSE=false",
        "STALE_REVOCATION_ROOT_RESULT_REUSE=false",
        "STALE_SUCCESSOR_ROOT_PROJECTION_REUSE=false",
        "STALE_SUPERSESSION_ROOT_PROJECTION_REUSE=false",
        "STALE_ORIGINAL_PACKET_TRANSITION_EVENT_REUSE=false",
        "STALE_REVOCATION_TRANSITION_EVENT_REUSE=false",
        "STALE_SUCCESSOR_ACTIVATION_EVENT_REUSE=false",
        "STALE_SUCCESSOR_DISPOSITION_EVENT_REUSE=false",
        "STALE_PREDECESSOR_SUPERSESSION_EVENT_REUSE=false",
        "REVOCATION_BOUND_TO_G2E_INVALIDATION=true",
        "FUTURE_G2F_REPORT_VALIDATOR_REQUIRED",
    ):
        assert marker in preflight
    expected_first_24 = (
        "semantic_address",
        "drs_time_envelope",
        "drs_authority_envelope",
        "meaning_record",
        "informational_temporal_query",
        "informational_candidate_evaluation",
        "legacy_local_drs_projection",
        "memory_descent_budget",
        "retrieval_plan",
        "resolution_candidate",
        "ranked_candidates",
        "root_kernel_for_informational_reuse",
        "semantic_work_request_for_reuse",
        "reuse_evidence_binding",
        "normalized_reuse_claim",
        "reuse_actor_contribution",
        "component_trust_profiles",
        "reuse_root_review_packet",
        "reuse_root_decision_input",
        "reuse_root_decision",
        "root_shortcut_projection",
        "reuse_certificate",
        "resolution_report",
        "existing_shortcut_use_validation",
    )
    assert tuple(row.split("|")[2] for row in construction_rows[:24]) == (
        expected_first_24
    )
    assert "G2F_cross_stage_validator" not in preflight
    for artifact in (
        "packet_authorization_actor_contribution",
        "packet_authorization_root_decision_input",
        "packet_authorization_root_decision_result",
        "invalidation_acceptance_actor_contribution",
        "invalidation_acceptance_root_decision_input",
        "invalidation_acceptance_root_decision_result",
        "revocation_review_root_decision_input",
        "revocation_review_root_decision_result",
        "revocation_review_root_candidate_projection",
        "successor_authorization_root_decision_input",
        "successor_authorization_root_decision_result",
        "successor_authorization_root_candidate_projection",
        "supersession_review_root_decision_input",
        "supersession_review_root_decision_result",
        "supersession_review_root_candidate_projection",
        "original_activation_transition_event",
        "original_queue_transition_event",
        "original_pending_transition_event",
        "fresh_revocation_transition_event",
        "successor_activation_transition_event",
        "successor_activation_disposition_event",
        "predecessor_supersession_transition_event",
    ):
        assert sum(f"|{artifact}|" in row for row in construction_rows) == 1
    closure_section = preflight.split("### Audit and closure", 1)[1]
    for stale_hash in (
        "649a32ffbf623436fe0ad38d16173b7dcf6c3851f8b3aa07c89438d926f7069a",
        "f9a8dae2bce0da087ea37232e55ca55eaea07bbf55b5ea8412b8d308006600ba",
        "baf0da8f89a1908862532810cdf346359212bdac9b1cb7d73bb64fabc4015a93",
        "77114107f4fed8b262a4a9db79a0e53e9d9d236a2212d89d7204305ebbf61056",
        "0fe4ab13426d6775645c5557bd5ba41fb17681a36beeb80d69cdf84ff972fce3",
        "a27e490cdbdc30ddb1dd4e87b63d932b012ef40100993859fcf4e30bd140ba3a",
    ):
        assert stale_hash not in closure_section
    assert closure_section.count(
        "RECONCILED_CLASS_A_COMMITTED_POSTIMAGE_TO_BE_BOUND_EXACTLY_BEFORE_CLOSURE"
    ) == 6

    authority_index = json.loads(
        (REPOSITORY_ROOT / "specs/document_authority_index_v01.json").read_text(
            encoding="utf-8"
        )
    )
    preflight_entries = [
        entry
        for entry in authority_index["current_technical_annexes"]
        if entry["path"] == G2F_CLASS_A_PATHS[0]
    ]
    assert len(preflight_entries) == 1
    assert preflight_entries[0]["status"] == (
        "accepted_g2f_v13r1_full_validator_closure_candidate"
    )
    assert preflight_entries[0]["authority_scope"] == "named_gate_contract_only"
    assert preflight_entries[0]["may_override_architecture_lock"] is False

    manifest = json.loads(
        (REPOSITORY_ROOT / "release/successor_context_manifest_v01.json").read_text(
            encoding="utf-8"
        )
    )
    succession = manifest["g2f_class_a_succession"]
    assert succession["basis_head"] == original_class_a_commit
    assert succession["original_class_a_basis_head"] == original_class_a_parent
    assert succession["original_class_a_commit"] == original_class_a_commit
    assert succession["reconciliation_basis_head"] == original_class_a_commit
    assert {entry["path"] for entry in succession["original_class_a_paths"]} == set(
        G2F_CLASS_A_PATHS
    )
    assert {
        entry["path"]: entry["action"]
        for entry in succession["original_class_a_paths"]
    } == {
        path: "ADD" if path == G2F_CLASS_A_PATHS[0] else "MODIFY"
        for path in G2F_CLASS_A_PATHS
    }
    assert succession["reconciliation_path_count"] == 7
    assert {
        entry["path"]: entry["action"]
        for entry in succession["reconciliation_paths"]
    } == {path: "MODIFY" for path in G2F_CLASS_A_PATHS}
    assert {
        entry["path"] for entry in succession["future_implementation_paths"]
    } == set(G2F_IMPLEMENTATION_PATHS)
    assert len(succession["future_closure_paths"]) == 14
    assert succession["implementation_authorization"] == (
        "NOT_AUTHORIZED_PENDING_OWNER_RECONCILIATION_COMMIT_AND_SEPARATE_REAUTHORIZATION"
    )
    assert succession["owner_commit_boundaries"] == [
        "ORIGINAL_CLASS_A_COMMIT_PROVENANCE",
        "CLASS_A_181_ROW_RECONCILIATION_EXACT_SEVEN_MODIFY_PATHS",
        "FUTURE_IMPLEMENTATION_EXACT_TWO_ADD_PATHS",
        "FUTURE_CLOSURE_EXACT_FOURTEEN_PATHS",
    ]
    assert succession["runtime_implementation_performed"] is False
    assert succession["repository_g2f_lifecycle_status"] == (
        "G2F_CLASS_A_181_ROW_RECONCILIATION_CANDIDATE"
    )
    assert succession["g2f_status"] == "NOT_CLOSED"
    assert succession["gate2_status"] == "NOT_CLOSED"
    assert succession["preflight_status"] == (
        "CLASS_A_181_ROW_RECONCILIATION_CANDIDATE"
    )
    assert succession["class_a_status"] == (
        "V13R1_CANDIDATE_PENDING_OWNER_REVIEW"
    )
    assert succession["classification"] == "ORCHESTRATION_AND_ACCEPTANCE_ONLY"
    assert succession["public_construction_ledger_rows"] == 181
    assert succession["construction_ledger_consecutive"] is True
    assert succession["current_class_a_postimages_reconciled"] is True
    assert succession["v12r3_reconciliation_readiness_status"] == (
        "SUPERSEDED_BY_V12R4"
    )
    assert succession["v12r5_reconciliation_readiness_status"] == "SUPERSEDED"
    assert succession["v12r5_reconciliation_readiness_scope"] == (
        "ONLY_TERMINAL_READINESS"
    )
    assert succession["v12r5_full_byte_corridor_statement_coverage_status"] == (
        "NOT_PROVEN"
    )
    assert succession["v12r6_full_corridor_external_proof_status"] == (
        "DIRECT_AUTHORITY_FOR_V13_RECONCILIATION"
    )
    assert succession["v12r6_full_corridor_external_proof_scope"] == (
        "NO_IMPLEMENTATION_OR_RECONCILIATION_AUTHORITY"
    )
    assert succession["v12r6_total_executed_negative_regression_count"] == 315
    assert succession["v13_input_archive_sha256"] == (
        "854583db82779dea15aec2abff29944cc46e015a71234fcf61185f0fc2c1e6e7"
    )
    assert succession["v13_owner_readiness_status"] == (
        "SUPERSEDED_BY_V13R1_VALIDATOR_CLOSURE"
    )
    assert succession["v13r1_validator_closure_status"] == (
        "FULL_181_ROW_EXPECTED_SIDE_RECONSTRUCTED_CANDIDATE"
    )

    preflight_hostile_root = tmp_path / "preflight_contract_hostiles"
    (preflight_hostile_root / "docs").mkdir(parents=True)

    def preflight_contract_failures(source: str) -> tuple[str, ...]:
        (preflight_hostile_root / G2F_CLASS_A_PATHS[0]).write_text(
            source,
            encoding="utf-8",
        )
        observed: list[str] = []
        namespace["_validate_g2f_class_a_contract_v01"](
            preflight_hostile_root,
            authority_index,
            manifest,
            observed,
            g2f_active=True,
        )
        return tuple(observed)

    row_129_binding_failures = preflight_contract_failures(
        preflight.replace("ROW129_ROOT_DECISION_REF=None", "ROW129_ROOT_DECISION_REF=forged", 1)
    )
    assert (
        "g2f.class_a.preflight.marker:ROW129_ROOT_DECISION_REF=None"
        in row_129_binding_failures
    )

    row_173_source_failures = preflight_contract_failures(
        preflight.replace(
            "ROW173_AUTHORIZED_CANONICAL_SOURCE=ROW154",
            "ROW173_AUTHORIZED_CANONICAL_SOURCE=ROW145",
            1,
        )
    )
    assert (
        "g2f.class_a.preflight.marker:ROW173_AUTHORIZED_CANONICAL_SOURCE=ROW154"
        in row_173_source_failures
    )

    branch_parent_failures = preflight_contract_failures(
        preflight.replace(
            "LIFECYCLE_BRANCH_MODEL=TWO_INDEPENDENT_PROOF_BRANCHES_FROM_ROW098_PENDING_BASELINE",
            "LIFECYCLE_BRANCH_MODEL=REVOCATION_FEEDS_SUPERSESSION",
            1,
        )
    )
    assert any(
        item.startswith("g2f.class_a.preflight.marker:LIFECYCLE_BRANCH_MODEL=")
        for item in branch_parent_failures
    )

    stale_basis_failures = preflight_contract_failures(
        preflight.replace(
            "f78aedd408138603d78f249178e171c48b0338e7aa331293f0832cbb27815b0d",
            "3550b55766bc57975bf0f5c4c865d8be6c6c90e8461b8208f9b2f0753e57eebd",
        )
    )
    assert any(
        item.startswith("g2f.class_a.preflight.forbidden_active:3550b557")
        for item in stale_basis_failures
    )

    v12r3_readiness_failures = preflight_contract_failures(
        preflight.replace(
            "V12R3_RECONCILIATION_READINESS_STATUS=SUPERSEDED_BY_V12R4",
            "V12R3_RECONCILIATION_READINESS_STATUS=DIRECT_AUTHORITY",
            1,
        )
    )
    assert "g2f.class_a.preflight.status:V12R3_RECONCILIATION_READINESS_STATUS" in (
        v12r3_readiness_failures
    )

    v12r5_readiness_failures = preflight_contract_failures(
        preflight.replace(
            "V12R5_RECONCILIATION_READINESS_STATUS=SUPERSEDED",
            "V12R5_RECONCILIATION_READINESS_STATUS=DIRECT_AUTHORITY",
            1,
        )
    )
    assert "g2f.class_a.preflight.status:V12R5_RECONCILIATION_READINESS_STATUS" in (
        v12r5_readiness_failures
    )

    v12r6_identity_failures = preflight_contract_failures(
        preflight.replace(
            "78fd785e707fc6d198878a566b49ba6dad0e47d2e0efd0bc8c812b78d33334d4",
            "0" * 64,
        )
    )
    assert any(
        item.startswith("g2f.class_a.preflight.marker:V12R6_EVIDENCE_ARCHIVE_SHA256=")
        for item in v12r6_identity_failures
    )

    status_overclaim_failures = preflight_contract_failures(
        preflight.replace("G2F_STATUS=NOT_CLOSED", "G2F_STATUS=CLOSED_PASS", 1)
    )
    assert "g2f.class_a.preflight.status:G2F_STATUS" in status_overclaim_failures

    runner_lines = [
        "from __future__ import annotations",
        "import json",
        "import hedgehog.reuse_certificate_v01 as reuse",
        "import hedgehog.drs_memory_resolution_v01 as drs",
        "import hedgehog.kernel.execution_mode_router_v01 as router",
        "import hedgehog.kernel.multiroot_v01 as multiroot",
        "import hedgehog.kernel.fractal_runtime_v02 as fractal",
        "import hedgehog.kernel.semantic_work_v01 as semantic",
        "import hedgehog.kernel.root_decision_v01 as root_decision",
        "import hedgehog.action_commit_packet_v02 as packet",
        "import hedgehog.kernel.continuous_delta_runtime_v01 as delta",
        "",
        "def collect_consolidated_gate2_gauntlet_g2_f_v01():",
        "    shortcut = reuse.validate_existing_root_shortcut_decision_v01(object(), object(), object(), object())",
        "    action_rejection = drs.evaluate_drs_candidate_v01(object(), object(), object())",
        "    client_route = router.route_execution_mode_v01(object(), object())",
        "    supplier_route = router.route_execution_mode_v01(object(), object())",
        "    client_review = router.review_execution_mode_proposal_v01(object(), object(), object(), object(), object(), object())",
        "    supplier_review = router.review_execution_mode_proposal_v01(object(), object(), object(), object(), object(), object())",
        "    outcome = multiroot.build_transaction_outcome_envelope_v01(transaction_id='transaction:g2f:gate2:v01', expected_root_ids=('root:g2f:client', 'root:g2f:supplier'), root_decisions=(client_review, supplier_review), cross_root_evidence_refs=())",
        "    outcome_errors = multiroot.validate_transaction_outcome_envelope_v01(outcome)",
        "    outcome_validation = multiroot.validate_multiroot_v01(outcome)",
        "    client_runtime = fractal.run_fractal_runtime_v02(source_context=client_route)",
        "    supplier_runtime = fractal.run_fractal_runtime_v02(source_context=supplier_route)",
    ]
    for index in range(7):
        runner_lines.append(
            f"    request_{index} = semantic.build_semantic_work_request_v01(request_id='request:{index}', transaction_id='transaction:g2f:gate2:v01', target_root_id='root:g2f:supplier', runtime_topology_ref='candidate:{index}', bounded_context_refs=(), permitted_actor_ids=(), permitted_contribution_modes=(), requested_subjects=(), required_evidence_classes=(), forbidden_claims=())"
        )
        runner_lines.append(
            f"    evidence_{index} = semantic.build_evidence_binding_v01(binding_id='binding:{index}', semantic_work_request=request_{index}, evidence_items=())"
        )
        runner_lines.append(
            f"    claim_{index} = semantic.build_normalized_claim_v01(claim_id='claim:{index}', semantic_work_request=request_{index}, evidence_binding=evidence_{index}, candidate_id='candidate:{index}')"
        )
        runner_lines.append(
            f"    contribution_{index} = semantic.build_actor_contribution_v01(contribution_id='contribution:{index}', actor_id='actor:g2f', semantic_work_request=request_{index}, normalized_claim=claim_{index}, evidence_binding=evidence_{index})"
        )
        runner_lines.append(
            f"    review_packet_{index} = semantic.build_root_review_packet_from_contributions_v01(packet_id='review:{index}', semantic_work_request=request_{index}, contributions=(contribution_{index},))"
        )
    for index in range(7):
        runner_lines.append(
            f"    decision_input_{index} = root_decision.build_root_decision_input_v01(transaction_id='transaction:g2f:gate2:v01', target_root_id='root:g2f:supplier', root_review_packet=review_packet_{index}, post_vv_bundle=object(), gt_advisory=object(), policy_state=object(), permission_state=object(), temporal_state=object(), conflict_state=object(), prior_root_state=object())"
        )
        runner_lines.append(
            f"    decision_{index} = root_decision.decide_root_v01(kernel=object(), decision_input=decision_input_{index})"
        )
    for index in range(4):
        runner_lines.append(
            f"    projection_{index} = packet.build_root_decision_candidate_projection_v01(candidate_kind='PACKET_AUTHORIZATION', projected_candidate_id='candidate:{index}', root_decision_kernel=object(), root_decision_input=decision_input_{index}, root_decision_result=decision_{index})"
        )
    runner_lines.extend(
        [
            "    packet_0 = packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(canonical_projection=object(), root_decision_projection=projection_0)",
            "    packet_1 = packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(canonical_projection=object(), root_decision_projection=projection_2)",
            "    registry_0 = packet.record_action_packet_genesis_v01(object(), root_bound_genesis=packet_0, action_packet_transition_registry_profile=object())",
            "    registry_1 = packet.record_action_packet_genesis_v01(registry_0, root_bound_genesis=packet_1, action_packet_transition_registry_profile=object())",
        ]
    )
    for index in range(8):
        runner_lines.append(
            f"    event_{index} = packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=object(), transition_rule_id='event:{index}', packet_id='packet:{index}', idempotency_key='key', previous_transition_event_id=None, owning_local_root_id='root:g2f:supplier', root_decision_ref='decision', transition_evidence_bindings=(), dependency_set_candidate_fingerprint='fingerprint', temporal_authority_fingerprint='temporal', evaluation_time={index}, evaluation_time_source='deterministic', evaluation_context_id='g2f', execution_attempt_identity=None, receipt_ref=None)"
        )
    runner_lines.extend(
        [
            "    registry_2 = packet.activate_action_packet_lifecycle_v01(registry_1, packet_id='packet:0', transition_event=event_0, disposition_event=object(), action_packet_transition_registry_profile=object())",
            "    registry_3 = packet.append_action_packet_lifecycle_transition_v01(registry_2, packet_id='packet:0', transition_event=event_1, action_packet_transition_registry_profile=object())",
            "    registry_4 = packet.append_action_packet_lifecycle_transition_v01(registry_3, packet_id='packet:0', transition_event=event_2, action_packet_transition_registry_profile=object())",
            "    registry_5 = packet.append_action_packet_lifecycle_transition_v01(registry_4, packet_id='packet:1', transition_event=event_6, action_packet_transition_registry_profile=object())",
            "    registry_6 = packet.append_action_packet_lifecycle_transition_v01(registry_5, packet_id='packet:1', transition_event=event_7, action_packet_transition_registry_profile=object())",
            "    pending = packet.inspect_action_packet_present_eligibility_v01(registry_4, packet_id='packet:0', corridor=object(), corridor_step=object(), current_dependency_observations=(), logical_time_bridge=object(), evaluation_time=1, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    changed = delta.run_continuous_delta_runtime_v01(source_context=object(), source_bindings=(), changed_field_bindings=(), changed_artifact_bindings=(), delta=object(), dependency_edges=(), dependency_graph=object())",
            "    preliminary = packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref='preliminary', packet_id='packet:0', dependency_id='dependency', invalidation_class='DEPENDENCY_CHANGED', evidence_ref='evidence', evidence_sha256='0' * 64, observed_status='CHANGED', time_envelope_id='time', freshness_policy_id='fresh', owning_local_root_id='root:g2f:supplier', accepted_by_local_root_id='root:g2f:supplier', authority_effect='DETERMINISTIC_BLOCK', evaluation_time=1, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    revocation_evidence = packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref='g2e', packet_id='packet:0', dependency_id='dependency', invalidation_class='ROOT_REVOCATION', evidence_ref='binding', evidence_sha256='1' * 64, observed_status='ACCEPTED', time_envelope_id='time', freshness_policy_id='fresh', owning_local_root_id='root:g2f:supplier', accepted_by_local_root_id='root:g2f:supplier', acceptance_root_decision_id='2' * 64, acceptance_root_decision_hash='3' * 64, authority_effect='ROOT_REVOCATION', root_decision_ref='2' * 64, evaluation_time=2, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    supersession_evidence = packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref='g2e', packet_id='packet:0', dependency_id='dependency', invalidation_class='ROOT_SUPERSESSION', evidence_ref='binding', evidence_sha256='4' * 64, observed_status='ACCEPTED', time_envelope_id='time', freshness_policy_id='fresh', owning_local_root_id='root:g2f:supplier', accepted_by_local_root_id='root:g2f:supplier', acceptance_root_decision_id='5' * 64, acceptance_root_decision_hash='6' * 64, authority_effect='ROOT_SUPERSESSION', root_decision_ref='5' * 64, evaluation_time=3, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    revoked = packet.record_action_packet_revocation_v01(registry_4, packet_id='packet:0', revocation_candidate=object(), revocation_root_projection=projection_1, accepted_revocation_binding=object(), invalidation_evidence=revocation_evidence, transition_event=event_3, action_packet_transition_registry_profile=object())",
            "    revoked_present = packet.inspect_action_packet_present_eligibility_v01(revoked, packet_id='packet:0', corridor=object(), corridor_step=object(), current_dependency_observations=(), logical_time_bridge=object(), evaluation_time=2, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    superseded = packet.record_action_packet_supersession_v01(registry_6, predecessor_packet_id='packet:0', successor_packet_id='packet:1', supersession_candidate=object(), supersession_root_projection=projection_3, accepted_supersession_binding=object(), invalidation_evidence=supersession_evidence, successor_activation_event=event_4, disposition_event=object(), action_packet_transition_registry_profile=object(), predecessor_supersession_event=event_5)",
            "    replay = packet.replay_action_packet_lifecycle_history_v01(superseded, packet_id='packet:0')",
            "    rejected_present = packet.inspect_action_packet_present_eligibility_v01(superseded, packet_id='packet:0', corridor=object(), corridor_step=object(), current_dependency_observations=(), logical_time_bridge=object(), evaluation_time=3, evaluation_time_source='deterministic', evaluation_context_id='g2f')",
            "    report = {'transaction_id': 'transaction:g2f:gate2:v01', 'root_decisions': (client_review, supplier_review), 'shortcut': shortcut, 'action_rejection': action_rejection, 'outcome_errors': outcome_errors, 'outcome_validation': outcome_validation, 'runtime': (client_runtime, supplier_runtime), 'pending': pending, 'delta': changed, 'preliminary_invalidation': preliminary, 'revoked_present': revoked_present, 'replay': replay, 'rejected_present': rejected_present}",
            "    if not validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):",
            "        raise ValueError('g2f_report_invalid')",
            "    return report",
            "",
            "def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):",
            "    return isinstance(report, dict) and report.get('transaction_id') == 'transaction:g2f:gate2:v01' and len(report.get('root_decisions', ())) == 2",
            "",
            "def consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report):",
            "    return {'transaction_id': report['transaction_id'], 'root_count': len(report['root_decisions'])}",
            "",
            "def render_consolidated_gate2_gauntlet_g2_f_v01(report):",
            "    return json.dumps(consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report), sort_keys=True, separators=(',', ':')) + '\\n'",
            "",
            "def main():",
            "    report = collect_consolidated_gate2_gauntlet_g2_f_v01()",
            "    if not validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):",
            "        return 1",
            "    print(render_consolidated_gate2_gauntlet_g2_f_v01(report), end='')",
            "    return 0",
            "",
        ]
    )
    positive_runner = "\n".join(runner_lines)
    test_lines = [
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner",
        "",
    ]
    for index, test_id in enumerate(namespace["G2F_FOCUSED_TEST_IDS"]):
        test_lines.extend(
            [
                f"def test_{test_id}():",
                "    report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()",
                (
                    "    assert runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)"
                    if index == 0
                    else "    assert report['transaction_id'] == 'transaction:g2f:gate2:v01'"
                ),
                "",
            ]
        )
    positive_tests = "\n".join(test_lines)

    future_root = tmp_path / "future_contract"
    runner_path = future_root / G2F_IMPLEMENTATION_PATHS[0]
    test_path = future_root / G2F_IMPLEMENTATION_PATHS[1]
    runner_path.parent.mkdir(parents=True)
    test_path.parent.mkdir(parents=True)
    future_validator = namespace[
        "_validate_g2f_future_implementation_contract_v01"
    ]

    def validate_sources(runner_source: str, test_source: str) -> tuple[str, ...]:
        runner_path.write_text(runner_source, encoding="utf-8")
        test_path.write_text(test_source, encoding="utf-8")
        observed: list[str] = []
        future_validator(future_root, observed)
        return tuple(observed)

    assert validate_sources(positive_runner, positive_tests) == ()

    unused_fixture_tests = positive_tests.replace(
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n\n",
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n"
        "import pytest\n\n"
        "@pytest.fixture\n"
        "def unrelated_fixture():\n"
        "    return 'unused ordinary fixture'\n\n",
        1,
    )
    assert validate_sources(positive_runner, unused_fixture_tests) == ()

    first_test_id = namespace["G2F_FOCUSED_TEST_IDS"][0]
    first_positive_test = (
        f"def test_{first_test_id}():\n"
        "    report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()\n"
        "    assert runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n"
    )
    fixture_substitution_test = (
        f"def test_{first_test_id}(report_fixture):\n"
        "    report = report_fixture\n"
        "    assert runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n"
    )
    fixture_substitution_tests = positive_tests.replace(
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n\n",
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n"
        "import pytest\n\n"
        "@pytest.fixture\n"
        "def report_fixture():\n"
        "    return {\n"
        "        'transaction_id': 'transaction:g2f:gate2:v01',\n"
        "        'root_decisions': (object(), object()),\n"
        "    }\n\n"
        "def decoy_actual_dataflow():\n"
        "    report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()\n"
        "    return runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n\n",
        1,
    ).replace(
        first_positive_test,
        fixture_substitution_test,
        1,
    )
    fixture_failures = validate_sources(
        positive_runner,
        fixture_substitution_tests,
    )
    assert (
        "g2f.implementation.tests.fixture_substitution:report_fixture"
        in fixture_failures
    )
    assert "g2f.implementation.tests.actual_public_dataflow" in fixture_failures

    duplicate_failures = validate_sources(
        positive_runner + "\ndef main():\n    return 0\n",
        positive_tests,
    )
    assert any("public_surface.duplicate:main" in item for item in duplicate_failures)

    validator_start = (
        "def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):\n"
        "    return isinstance(report, dict) and report.get('transaction_id') == "
        "'transaction:g2f:gate2:v01' and len(report.get('root_decisions', ())) == 2\n"
    )
    direct_recursion_runner = positive_runner.replace(
        validator_start,
        "def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):\n"
        "    return validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n",
        1,
    )
    direct_recursion_failures = validate_sources(
        direct_recursion_runner,
        positive_tests,
    )
    assert (
        "g2f.implementation.call_graph.self_recursion:"
        "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
        in direct_recursion_failures
    )

    mutual_recursion_runner = positive_runner.replace(
        "def consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report):\n"
        "    return {'transaction_id': report['transaction_id'], 'root_count': len(report['root_decisions'])}\n",
        "def consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report):\n"
        "    return render_consolidated_gate2_gauntlet_g2_f_v01(report)\n",
        1,
    ).replace(
        "def render_consolidated_gate2_gauntlet_g2_f_v01(report):\n"
        "    return json.dumps(consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report), sort_keys=True, separators=(',', ':')) + '\\n'\n",
        "def render_consolidated_gate2_gauntlet_g2_f_v01(report):\n"
        "    return consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report)\n",
        1,
    )
    mutual_recursion_failures = validate_sources(
        mutual_recursion_runner,
        positive_tests,
    )
    assert any(
        item.startswith("g2f.implementation.call_graph.nontrivial_scc:")
        for item in mutual_recursion_failures
    )

    validator_collector_runner = positive_runner.replace(
        validator_start,
        "def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):\n"
        "    return bool(collect_consolidated_gate2_gauntlet_g2_f_v01())\n",
        1,
    )
    validator_collector_failures = validate_sources(
        validator_collector_runner,
        positive_tests,
    )
    assert (
        "g2f.implementation.call_graph.collector_reachable:"
        "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
        in validator_collector_failures
    )

    private_runner = positive_runner.replace(
        "def collect_consolidated_gate2_gauntlet_g2_f_v01():\n",
        "def _private_source():\n    return object()\n\n"
        "def collect_consolidated_gate2_gauntlet_g2_f_v01():\n"
        "    _private_source()\n",
        1,
    )
    private_failures = validate_sources(private_runner, positive_tests)
    assert any("extra_helper:_private_source" in item for item in private_failures)
    assert any("private_attribute_call:_private_source" in item for item in private_failures)

    cache_runner = positive_runner.replace(
        "import json\n",
        "import json\nfrom functools import lru_cache as memoize\n",
        1,
    ).replace(
        "def collect_consolidated_gate2_gauntlet_g2_f_v01():\n",
        "@memoize(maxsize=1)\ndef collect_consolidated_gate2_gauntlet_g2_f_v01():\n",
        1,
    )
    cache_failures = validate_sources(cache_runner, positive_tests)
    assert any("process_cache_decorator:memoize" in item for item in cache_failures)

    fabricated_runner = positive_runner.replace(
        "import hedgehog.drs_memory_resolution_v01 as drs\n",
        "import hedgehog.drs_memory_resolution_v01 as drs\n"
        "import demo.run_living_gauntlet_v01 as living_aggregate\n",
        1,
    ).replace(
        "    shortcut = reuse.validate_existing_root_shortcut_decision_v01",
        "    aggregate = living_aggregate.collect_living_gauntlet_v01()\n"
        "    shortcut = reuse.validate_existing_root_shortcut_decision_v01",
        1,
    ).replace(
        validator_start,
        "def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):\n"
        "    return True\n",
        1,
    )
    fabricated_failures = validate_sources(fabricated_runner, positive_tests)
    assert any("aggregate_or_future_call" in item for item in fabricated_failures)
    assert any(
        "constant_validator_without_report" in item
        for item in fabricated_failures
    )

    tautology_tests = positive_tests.replace(
        "    assert runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n",
        "    assert True\n"
        "    assert runner.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)\n",
        1,
    )
    tautology_failures = validate_sources(positive_runner, tautology_tests)
    assert "g2f.implementation.tests.tautological_assertion" in tautology_failures

    mock_tests = positive_tests.replace(
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n",
        "from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as runner\n"
        "from unittest.mock import patch as substitute\n",
        1,
    ).replace(
        "    report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()\n",
        "    with substitute('demo.run_consolidated_gate2_gauntlet_g2_f_v01.collect_consolidated_gate2_gauntlet_g2_f_v01'):\n"
        "        report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()\n",
        1,
    )
    mock_failures = validate_sources(positive_runner, mock_tests)
    assert "g2f.implementation.tests.substitution_or_skip" in mock_failures

    extra_tests = positive_tests + (
        "\nclass TestExtraSurface:\n"
        "    def test_extra_surface(self):\n"
        "        report = runner.collect_consolidated_gate2_gauntlet_g2_f_v01()\n"
        "        assert report['transaction_id'] == 'transaction:g2f:gate2:v01'\n"
    )
    extra_failures = validate_sources(positive_runner, extra_tests)
    assert any("tests.test_class:TestExtraSurface" in item for item in extra_failures)

    overclaim_failures = validate_sources(
        positive_runner + "\nGATE2_STATUS=CLOSED_PASS\n",
        positive_tests,
    )
    assert any("status_overclaim" in item for item in overclaim_failures)


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


def test_g2f_closure_exact_single_successor_and_neighbors() -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    classify = namespace["_classify_g2f_path_ledger_v01"]
    entries = lambda mapping: tuple((status, path, None) for path, status in sorted(mapping.items()))
    closure = {p: "A" if p in G2F_CLOSURE_ADDS else "M" for p in G2F_CLOSURE_PATHS}
    candidate = {p: "??" if p in G2F_CLOSURE_ADDS else " M" for p in G2F_CLOSURE_PATHS}
    implementation = {p: "A" for p in G2F_IMPLEMENTATION_PATHS}
    maintenance = {p: "M" for p in G2F_CLASS_A_PATHS}
    p1 = dict(requested=True, head=G2F_CLOSURE_BASIS, parent=G2F_CLOSURE_MAINTENANCE,
              grandparent="779641d1a2e1c256c8232655d02124b66e3657b3", branch="main",
              origin_main=G2F_CLOSURE_BASIS, worktree_entries=entries(candidate),
              head_commit_entries=entries(implementation), parent_commit_entries=entries(maintenance))
    assert classify(**p1) == ("G2F_CLOSURE_CANDIDATE", ())
    # Abstract identifier only; real synthetic commits are exercised externally.
    p2 = {**p1, "head": "abstract-closure-child", "parent": G2F_CLOSURE_BASIS,
          "grandparent": G2F_CLOSURE_MAINTENANCE, "worktree_entries": (),
          "head_commit_entries": entries(closure), "parent_commit_entries": entries(implementation)}
    assert classify(**p2) == ("G2F_CLOSED_PASS_COMMITTED", ())
    assert classify(**{**p2, "origin_main": p2["head"]}) == ("G2F_CLOSED_PASS_COMMITTED", ())
    for path in G2F_CLOSURE_PATHS:
        assert classify(**{**p1, "worktree_entries": entries({p:s for p,s in candidate.items() if p != path})})[1]
        wrong = dict(closure); wrong[path] = "M" if closure[path] == "A" else "A"
        assert classify(**{**p2, "head_commit_entries": entries(wrong)})[1]
    for base, changes in (
        (p1, {"origin_main": G2F_CLOSURE_MAINTENANCE}),
        (p1, {"worktree_entries": entries({**candidate, "extra.txt": "??"})}),
        (p1, {"worktree_entries": entries({**candidate, "AGENTS.md": "M "})}),
        (p1, {"branch": "foreign"}),
        (p2, {"origin_main": "foreign-origin"}),
        (p2, {"parent_count": 2}),
        (p2, {"parent_parent_count": 2}),
        (p2, {"parent": "extra-generation", "grandparent": G2F_CLOSURE_BASIS}),
        (p2, {"head_commit_entries": (*entries(closure), ("R100", "renamed.md", "AGENTS.md"))}),
    ):
        assert classify(**{**base, **changes})[1], changes
    assert set(namespace["G2F_CLOSURE_PREDECESSORS_V01"]) == set(G2F_CLOSURE_PATHS) - set(G2F_CLOSURE_ADDS)
    assert namespace["G2F_CLOSURE_ADDS_V01"] == frozenset(G2F_CLOSURE_ADDS)


def test_g2f_closure_document_identity_and_claim_boundaries(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    validate = namespace["_validate_g2f_closure_surfaces_v01"]
    index = json.loads((REPOSITORY_ROOT / "specs/document_authority_index_v01.json").read_text())
    manifest = json.loads((REPOSITORY_ROOT / "release/successor_context_manifest_v01.json").read_text())
    for path in G2F_CLOSURE_PATHS:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPOSITORY_ROOT / path, target)
    failures = []
    validate(tmp_path, index, manifest, failures)
    assert failures == []
    for path in G2F_CLOSURE_ADDS:
        target = tmp_path / path
        original = target.read_bytes()
        target.write_bytes(original + b"tampered audit boundary\n")
        failures = []
        validate(tmp_path, index, manifest, failures)
        assert f"g2f.closure.document_identity:{path}" in failures
        target.write_bytes(original)
    changed = deepcopy(manifest)
    changed["g2f_closure_transition"]["real_world_effects_count"] = 1
    failures = []
    validate(tmp_path, index, changed, failures)
    assert "g2f.closure.metadata:successor_manifest" in failures
    changed = deepcopy(manifest)
    changed["always_include"].append(G2F_CLOSURE_ADDS[0])
    failures = []
    validate(tmp_path, index, changed, failures)
    assert "g2f.closure.onboarding:always_include" in failures
    target = tmp_path / "README.md"
    target.write_text(target.read_text() + "\nPRODUCTION_READINESS_STATUS=CLAIMED\n")
    failures = []
    validate(tmp_path, index, manifest, failures)
    assert "g2f.closure.overclaim:README.md" in failures


def test_u1_contract_exact_ledger_states_and_neighbors() -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    classify = namespace["_classify_u1_contract_ledger_v01"]
    unstaged = {p: "??" if p == U1_CONTRACT_DOC else " M" for p in U1_CONTRACT_PATHS}
    staged = {p: "A " if p == U1_CONTRACT_DOC else "M " for p in U1_CONTRACT_PATHS}
    delta = {p: "A" if p == U1_CONTRACT_DOC else "M" for p in U1_CONTRACT_PATHS}
    child = "abstract-contract-child"
    candidate = dict(head=U1_CONTRACT_BASIS, parents=(G2F_CLOSURE_BASIS,), branch="main", origin=U1_CONTRACT_BASIS, worktree=unstaged, committed={})
    committed = dict(head=child, parents=(U1_CONTRACT_BASIS,), branch="main", origin=U1_CONTRACT_BASIS, worktree={}, committed=delta)
    for inputs, expected in (
        (candidate, "U1_CONTRACT_CANDIDATE_UNSTAGED"),
        ({**candidate, "worktree": staged}, "U1_CONTRACT_CANDIDATE_STAGED"),
        (committed, "U1_CONTRACT_COMMITTED"),
        ({**committed, "origin": child}, "U1_CONTRACT_COMMITTED"),
    ):
        assert classify(**inputs) == (expected, ())
    for baseline, mutation, reason in (
        (candidate, {"origin": "foreign"}, "u1.candidate.origin"),
        (candidate, {"branch": "foreign"}, "u1.branch"),
        (candidate, {"parents": ("foreign",)}, "u1.basis.parent"),
        (candidate, {"worktree": dict(list(unstaged.items())[1:])}, "u1.candidate.exact_entire_ledger"),
        (candidate, {"worktree": {**unstaged, "extra.md": "??"}}, "u1.candidate.exact_entire_ledger"),
        (candidate, {"worktree": {**unstaged, "AGENTS.md": "M "}}, "u1.candidate.exact_entire_ledger"),
        (candidate, {"worktree": {**staged, "AGENTS.md": "MM"}}, "u1.candidate.exact_entire_ledger"),
        (committed, {"parents": (U1_CONTRACT_BASIS, "foreign")}, "u1.exact_single_parent_successor"),
        (committed, {"parents": (child,)}, "u1.exact_single_parent_successor"),
        (committed, {"origin": "foreign"}, "u1.committed.origin"),
        (committed, {"committed": {**delta, "README.md": "A"}}, "u1.committed.exact_delta"),
        (committed, {"worktree": {"AGENTS.md": " M"}}, "u1.committed.clean"),
    ):
        assert reason in classify(**{**baseline, **mutation})[1], mutation


def test_u1_contract_current_metadata_and_frozen_c_provenance(tmp_path: Path) -> None:
    historical_root = _u4_historical_contract_root(tmp_path)
    namespace = runpy.run_path(str(GUARD_PATH))
    index = json.loads((historical_root / "specs/document_authority_index_v01.json").read_text())
    manifest = json.loads((historical_root / "release/successor_context_manifest_v01.json").read_text())
    failures: list[str] = []
    namespace["_validate_u1_contract_surfaces_v01"](historical_root, index, manifest, failures)
    assert failures == []
    contract = manifest["u1_contract_transition"]
    assert contract["runtime_implementation"] == "NOT_IMPLEMENTED"
    assert contract["implementation_authorized"] is False
    assert contract["u1_u2_u3_acceptance"] == "NOT_CLAIMED"
    assert contract["u0_role"] == "CONTROL" and contract["u0_consumer"] == "SCRATCH_PROTOTYPE"
    for path in ("release/current_schema_surface_v01.json", "release/integration_seam_index.json", "release/integration_seam_index.md", *G2F_IMPLEMENTATION_PATHS):
        original = subprocess.check_output(("git", "show", f"{U1_CONTRACT_BASIS}:{path}"), cwd=REPOSITORY_ROOT)
        assert (historical_root / path).read_bytes() == original
    for field, value in (("runtime_implementation", "COMPLETE"), ("implementation_authorized", True), ("active_schema_registration", True), ("committed_phase", "U2_ACCEPTED")):
        changed = deepcopy(manifest)
        changed["u1_contract_transition"][field] = value
        failures = []
        namespace["_validate_u1_contract_surfaces_v01"](historical_root, index, changed, failures)
        assert "u1.metadata.exact_contract_only:release/successor_context_manifest_v01.json" in failures


def test_u1_contract_real_index_and_source_boundary(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    def git(*args: str) -> bytes:
        return subprocess.check_output(("git", *args), cwd=tmp_path, stderr=subprocess.PIPE)
    git("init", "-q", "-b", "main")
    object_store = Path(subprocess.check_output(("git", "rev-parse", "--path-format=absolute", "--git-path", "objects"), cwd=REPOSITORY_ROOT, text=True).strip())
    # SYNTHETIC_TEST_ONLY: independent objects, no owner index/refs or runtime.
    shutil.copytree(object_store, tmp_path / ".git/objects", dirs_exist_ok=True, copy_function=shutil.copyfile)
    assert not (tmp_path / ".git/objects/info/alternates").exists()
    git("update-ref", "refs/heads/main", U1_CONTRACT_BASIS)
    git("update-ref", "refs/remotes/origin/main", U1_CONTRACT_BASIS)
    git("read-tree", U1_CONTRACT_BASIS)
    git("checkout-index", "--all")
    for path in U1_CONTRACT_PATHS:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(subprocess.check_output(("git", "show", "20d16af823ed4af94dc0a342c731aef81e8a23de:" + path), cwd=REPOSITORY_ROOT))
    def check() -> tuple[str | None, list[str]]:
        failures: list[str] = []
        phase = namespace["_validate_u1_contract_topology_v01"](tmp_path, failures)
        return phase, failures
    assert check() == ("U1_CONTRACT_CANDIDATE_UNSTAGED", [])
    document = tmp_path / U1_CONTRACT_DOC
    original = document.read_bytes()
    document.write_bytes(original + b"\nChanged contract\n")
    assert "u1.contract.identity" in check()[1]
    document.write_bytes(original)
    frozen = tmp_path / "release/current_schema_surface_v01.json"
    original_frozen = frozen.read_bytes()
    frozen.write_bytes(original_frozen + b"\n")
    assert "u1.frozen_source:release/current_schema_surface_v01.json" in check()[1]
    frozen.write_bytes(original_frozen)
    git("add", "--", *U1_CONTRACT_PATHS)
    assert check() == ("U1_CONTRACT_CANDIDATE_STAGED", [])
    document.write_bytes(original + b"\n")
    assert "u1.index.content_mode_or_worktree_disagreement" in check()[1]
    document.write_bytes(original)
    git("update-index", "--assume-unchanged", "--", "AGENTS.md")
    assert "u1.index.flags" in check()[1]
    git("update-index", "--no-assume-unchanged", "--", "AGENTS.md")
    git("update-index", "--chmod=+x", "--", "AGENTS.md")
    assert "u1.index.content_mode_or_worktree_disagreement" in check()[1]
    git("update-index", "--chmod=-x", "--", "AGENTS.md")
    (tmp_path / ".git/MERGE_HEAD").write_text(U1_CONTRACT_BASIS + "\n")
    assert "u1.active_operation:MERGE_HEAD" in check()[1]
    (tmp_path / ".git/MERGE_HEAD").unlink()
    assert check() == ("U1_CONTRACT_CANDIDATE_STAGED", [])


def _u4_historical_contract_root(tmp_path: Path) -> Path:
    """Exact H materialization for unchanged historical contract obligations."""
    import shutil
    import subprocess
    root = tmp_path / "historical_H"
    root.mkdir()
    subprocess.run(("git", "init", "-q", "-b", "main"), cwd=root, check=True)
    objects = Path(subprocess.check_output(("git", "rev-parse", "--path-format=absolute", "--git-path", "objects"), cwd=REPOSITORY_ROOT, text=True).strip())
    shutil.copytree(objects, root / ".git/objects", dirs_exist_ok=True, copy_function=shutil.copyfile)
    assert not (root / ".git/objects/info/alternates").exists()
    h = "20d16af823ed4af94dc0a342c731aef81e8a23de"
    for args in (("update-ref", "refs/heads/main", h), ("update-ref", "refs/remotes/origin/main", h), ("read-tree", h), ("checkout-index", "--all")):
        subprocess.run(("git", *args), cwd=root, check=True)
    return root


def test_u4_admission_exact_current_states_and_neighbors(tmp_path) -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    actions = namespace["U4_PATH_ACTIONS_V01"]
    h = "20d16af823ed4af94dc0a342c731aef81e8a23de"
    classify = namespace["_classify_u4_ledger_v01"]
    source = dict(head=h, parents=(U1_CONTRACT_BASIS,), origin=h, branch="main",
                  status={p: "??" if op == "A" else " M" for p, op in actions.items()}, delta={})
    staged = {**source, "status": {p: op + " " for p, op in actions.items()}}
    committed = {**source, "head": "abstract-test-only-child", "parents": (h,), "status": {}, "delta": actions}
    for state, phase in ((source, "U4_ADMISSION_CANDIDATE_UNSTAGED"), (staged, "U4_ADMISSION_CANDIDATE_STAGED"), (committed, "U4_IMPLEMENTATION_ADMITTED_COMMITTED"), ({**committed, "origin": committed["head"]}, "U4_IMPLEMENTATION_ADMITTED_COMMITTED")):
        assert classify(**state) == (phase, ())
    for state, change in ((source, {"branch": "foreign"}), (source, {"origin": "foreign"}), (source, {"parents": (h,)}), (source, {"status": dict(list(source["status"].items())[1:])}), (source, {"status": {**source["status"], "foreign.txt": "??"}}), (staged, {"status": {**staged["status"], "AGENTS.md": "MM"}}), (committed, {"parents": (h,h)}), (committed, {"origin": "foreign"}), (committed, {"delta": {**actions, "AGENTS.md": "A"}}), (committed, {"parents": (committed["head"],)})):
        assert classify(**{**state, **change})[1]
    failures = []
    root = _testflix_historical_L_root_v11(tmp_path) if namespace["_testflix_requested_v11"](REPOSITORY_ROOT) else REPOSITORY_ROOT
    assert namespace["_validate_u4_admission_v01"](root, failures) in {"U4_ADMISSION_CANDIDATE_UNSTAGED", "U4_ADMISSION_CANDIDATE_STAGED", "U4_IMPLEMENTATION_ADMITTED_COMMITTED"}
    assert failures == []


def test_u4_admission_source_identity_projection_is_exact() -> None:
    namespace = runpy.run_path(str(GUARD_PATH))
    pins = namespace["U4_SOURCE_IDENTITIES_V01"]
    digest = namespace["_u4_source_digest_v01"]
    assert len(pins) == 48
    for path, expected in pins.items():
        body = subprocess.check_output(("git", "show", "54e32dbcc0e4d68431ec2b9428eac965f88ee47c:" + path), cwd=REPOSITORY_ROOT) if namespace["_testflix_requested_v11"](REPOSITORY_ROOT) else (REPOSITORY_ROOT / path).read_bytes()
        assert digest(path, body) == expected
        if path.endswith(".py"):
            changed = body + b"\nU4_UNAUTHORIZED_EXTRA = 1\n"
        else:
            changed = body + b"\nUNAUTHORIZED_EXTRA\n"
        assert digest(path, changed) != expected


def test_u4_self_digest_uses_stable_original_utf8_bytes() -> None:
    digest = runpy.run_path(str(GUARD_PATH))["_u4_source_digest_v01"]
    path = "tools/check_active_architecture_authority_v01.py"
    body = ('# stable byte oracle\nU4_SOURCE_IDENTITIES_V01 = {"label": "caf\u00e9", "' + path + '": "' + 'a' * 64 + '", "other.py": "' + 'b' * 64 + '"}\nVALUE = 7  # retained\n').encode("utf-8")
    expected = "8331c4d822d97cdfde2bff511feb69bf69fd02ed1d56af3786d1bc30d78057a2"
    assert digest(path, body) == expected
    assert digest(path, bytes(bytearray(body))) == expected
    assert digest(path, body.replace(b'a' * 64, b'c' * 64)) == expected
    for changed in (
        body.replace(b'b' * 64, b'd' * 64),
        body.replace(b'VALUE = 7', b'VALUE = 8'),
        body.replace(b'# retained', b'# retained differently'),
        body.replace(b' = {', b'  = {'),
        body + b'\n',
    ):
        assert digest(path, changed) != expected
    assert digest("other.py", body) == hashlib.sha256(body).hexdigest()


def test_u4_self_digest_rejects_ambiguous_or_malformed_literal() -> None:
    digest = runpy.run_path(str(GUARD_PATH))["_u4_source_digest_v01"]
    path = "tools/check_active_architecture_authority_v01.py"
    entry = repr(path).encode() + b": '" + b'a' * 64 + b"'"
    body = b'U4_SOURCE_IDENTITIES_V01 = {' + entry + b'}\n'
    assert digest(path, body) == hashlib.sha256(b'U4_SOURCE_IDENTITIES_V01 = {' + repr(path).encode() + b': "SELF_DIGEST_EXCLUDED_V01"}\n').hexdigest()
    malformed = (
        b'OTHER = {}\n',
        b'U4_SOURCE_IDENTITIES_V01 = {}\n',
        body + body,
        body.replace(entry, entry + b', ' + entry),
        body.replace(b'a' * 64, b'a' * 63),
        body.replace(b'a' * 64, b'A' * 64),
        body.replace(b"'" + b'a' * 64 + b"'", b'None'),
        body.replace(b"'" + b'a' * 64 + b"'", b"'" + b'a' * 32 + b"' '" + b'a' * 32 + b"'"),
        body.replace(b"'" + b'a' * 64 + b"'", b"r'" + b'a' * 64 + b"'"),
        body.replace(b"'" + b'a' * 64 + b"'", b"'''" + b'a' * 64 + b"'''"),
        body.replace(b' = {', b': dict = {'),
        body.replace(b' = {', b' = ALIAS = {'),
        body.replace(b' = {', b' = {**OTHER, '),
        body + b'U4_SOURCE_IDENTITIES_V01 += {}\n',
        body + b'U4_SOURCE_IDENTITIES_V01, alias = ({}, {})\n',
    )
    for changed in malformed:
        with pytest.raises(ValueError, match="self identity projection"):
            digest(path, changed)
    assert digest(path, body) == digest(path, bytes(bytearray(body)))


def _testflix_historical_L_root_v11(tmp_path):
    root = _u4_historical_contract_root(tmp_path)
    basis = "54e32dbcc0e4d68431ec2b9428eac965f88ee47c"
    for args in (("update-ref", "refs/heads/main", basis), ("update-ref", "refs/remotes/origin/main", basis),
                 ("read-tree", basis), ("checkout-index", "--all", "--force")):
        subprocess.run(("git", *args), cwd=root, check=True)
    return root


def test_testflix_admission_states_and_exact_neighbors_v11():
    namespace = runpy.run_path(str(GUARD_PATH))
    actions = namespace["TESTFLIX_PATH_ACTIONS_V11"]
    classify = namespace["_classify_testflix_ledger_v11"]
    basis = namespace["TESTFLIX_L_V11"]
    before = dict(head=basis, parents=(namespace["U4_H_V01"],), origin=basis, branch="main",
        status={p: "??" if op == "A" else " M" for p,op in actions.items()}, delta={})
    staged = {**before, "status": {p:op + " " for p,op in actions.items()}}
    committed = {**before, "head":"abstract-local-successor", "parents":(basis,), "status":{}, "delta":actions}
    for state,phase in ((before,"TESTFLIX_ADMISSION_CANDIDATE_UNSTAGED"),
        (staged,"TESTFLIX_ADMISSION_CANDIDATE_STAGED"), (committed,"TESTFLIX_IMPLEMENTATION_ADMITTED_COMMITTED"),
        ({**committed,"origin":committed["head"]},"TESTFLIX_IMPLEMENTATION_ADMITTED_COMMITTED")):
        assert classify(**state)==(phase,())
    for state,change in ((before,{"branch":"foreign"}), (before,{"origin":"foreign"}),
        (before,{"parents":(basis,)}), (before,{"status":dict(list(before["status"].items())[1:])}),
        (before,{"status":{**before["status"],"foreign.txt":"??"}}),
        (staged,{"status":{**staged["status"],"AGENTS.md":"MM"}}),
        (committed,{"parents":(basis,basis)}), (committed,{"origin":"foreign"}),
        (committed,{"delta":{**actions,"AGENTS.md":"A"}}), (committed,{"parents":(committed["head"],)})):
        assert classify(**{**state,**change})[1]


def test_testflix_exact_sources_and_stable_projection_v11():
    namespace = runpy.run_path(str(GUARD_PATH))
    digest = namespace["_testflix_source_digest_v11"]
    pins = namespace["TESTFLIX_SOURCE_IDENTITIES_V11"]
    assert len(pins)==51 and set(pins)==set(namespace["TESTFLIX_PATH_ACTIONS_V11"])
    for path,expected in pins.items():
        body=subprocess.check_output(("git", "show", namespace["EWS_BASE_V01"]+":"+path), cwd=REPOSITORY_ROOT) if namespace["_ews_requested_v01"](REPOSITORY_ROOT) else (REPOSITORY_ROOT/path).read_bytes()
        assert digest(path,body)==expected
        assert digest(path,body+b"\n# Unapproved extra bytes\n")!=expected
    path="tools/check_active_architecture_authority_v01.py"
    body=('TESTFLIX_SOURCE_IDENTITIES_V11 = {"label": "caf\u00e9", "'+path+'": "'+'a'*64+'", "other": "'+'b'*64+'"}\nVALUE=3\n').encode()
    expected=hashlib.sha256(body.replace(('"'+'a'*64+'"').encode(),b'"SELF_DIGEST_EXCLUDED_V11"')).hexdigest()
    assert digest(path,body)==expected==digest(path,bytes(bytearray(body)))
    assert digest(path,body.replace(b'a'*64,b'c'*64))==expected
    assert digest(path,body.replace(b'b'*64,b'd'*64))!=expected
    for bad in (body+body, body.replace(b'a'*64,b'a'*63),body.replace(b'a'*64,b'A'*64),
        body.replace(b' = {',b': dict = {'),body.replace(b' = {',b' = ALIAS = {'),
        body+b'TESTFLIX_SOURCE_IDENTITIES_V11 += {}\n'):
        with pytest.raises(ValueError,match='self identity projection'):
            digest(path,bad)


def test_testflix_current_public_guard_v11():
    result=_run_guard(REPOSITORY_ROOT)
    assert result.returncode==0,result.stdout+result.stderr
    expected=_expected_g2f_landing_stdout_v01(REPOSITORY_ROOT)
    assert result.stdout.endswith(expected)
    assert result.stderr==''


def test_testflix_living_registration_source_and_schema_v11(tmp_path):
    import importlib.util
    namespace = runpy.run_path(str(GUARD_PATH))
    if namespace["_ews_requested_v01"](REPOSITORY_ROOT):
        historical = tmp_path / "historical_source"
        historical.mkdir()
        source_root = _ews_isolated_base_v01(historical)
    else:
        source_root = REPOSITORY_ROOT
    source=source_root/'demo/run_living_gauntlet_v01.py'
    spec=importlib.util.spec_from_file_location('testflix_living_registration_probe_v11',source)
    living=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=living
    try:
        spec.loader.exec_module(living)
        block,errors=living._current_registration_v01(source_root)
        assert errors==() and len(block['rows'])==9
        assert block['basis']==living._TESTFLIX_L_V11
        assert all(row['authority']=='EVIDENCE_ONLY' and row['effect_access']=='NONE' for row in block['rows'])
        root=_testflix_historical_L_root_v11(tmp_path)
        paths=(*living._TESTFLIX_FROZEN_SOURCES_V11,*living._U4_BASE_IDENTITIES,
            'release/current_schema_surface_v01.json','release/current_status_overlay_v01.json')
        for path in paths:
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((source_root/path).read_bytes())
        overlay_path=root/'release/current_status_overlay_v01.json'
        original=json.loads(overlay_path.read_text())
        assert living._current_registration_v01(root)==(block,())
        for mutation in ('missing','extra','duplicate','module','symbol','authority','source','pass'):
            changed=deepcopy(original);record=changed[living._TESTFLIX_REGISTRATION_KEY_V11]
            if mutation=='missing':record['rows'].pop()
            elif mutation in ('extra','duplicate'):record['rows'].append(deepcopy(record['rows'][0]))
            elif mutation=='module':record['rows'][0]['producer']='foreign.module:execute'
            elif mutation=='symbol':record['rows'][0]['producer']='hedgehog.action_commit_packet_v02:foreign'
            elif mutation=='authority':record['rows'][0]['authority']='ROOT'
            elif mutation=='source':record['rows'][0]['source_sha256']='0'*64
            else:record['status']='PASS'
            overlay_path.write_text(json.dumps(changed)+'\n')
            assert 'registration_exact_block' in living._current_registration_v01(root)[1],mutation
        overlay_path.write_text(json.dumps(original)+'\n')
        schema_path=root/'release/current_schema_surface_v01.json'
        schema=json.loads(schema_path.read_text());schema['current_schema_paths'].append('schemas/retired/foreign.json')
        schema_path.write_text(json.dumps(schema)+'\n')
        assert 'registration_schema_inventory' in living._current_registration_v01(root)[1]
        schema_path.write_bytes((source_root/'release/current_schema_surface_v01.json').read_bytes())
        host=root/'hedgehog/work_execution_host_v01.py';body=host.read_bytes();host.write_bytes(body+b'\nUNAPPROVED=True\n')
        assert 'registration_source:hedgehog/work_execution_host_v01.py' in living._current_registration_v01(root)[1]
        host.write_bytes(body)
        assert living._current_registration_v01(root)==(block,())
    finally:
        sys.modules.pop(spec.name,None)


def _ews_isolated_base_v01(tmp_path):
    """Own Git objects/worktree; no shared branch or owner index mutations."""
    root = _testflix_historical_L_root_v11(tmp_path)
    base = "e42d37fa98dfec7110b8cf75b1aceaa614f461be"
    for args in (("update-ref", "refs/heads/main", base),
                 ("update-ref", "refs/remotes/origin/main", base),
                 ("read-tree", base), ("checkout-index", "--all", "--force")):
        subprocess.run(("git", *args), cwd=root, check=True)
    return root


def test_ews_admission_real_git_states_and_hostile_neighbors_v01(tmp_path):
    import os
    import shutil
    namespace = runpy.run_path(str(GUARD_PATH))
    root = _ews_isolated_base_v01(tmp_path)
    actions = namespace["EWS_PATH_ACTIONS_V01"]
    base = namespace["EWS_BASE_V01"]
    for path in actions:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPOSITORY_ROOT / path, target)
        assert target.stat().st_ino != (REPOSITORY_ROOT / path).stat().st_ino

    def git(*args, **kwargs):
        return subprocess.check_output(("git", *args), cwd=root, **kwargs).decode().strip()

    def check(expected=None, reason=None):
        failures = []
        phase = namespace["_validate_ephemeral_workspace_admission_v01"](root, failures)
        if reason:
            assert reason in failures, (reason, failures)
            assert namespace["collect_failures"](root)
        else:
            assert not failures, failures
            assert phase == expected
            result = _run_guard(root)
            assert result.returncode == 0, result.stdout + result.stderr
            assert "EPHEMERAL_WORKSPACE_PHASE=" + expected in result.stdout
        return failures

    unstaged = "EWS_ADMISSION_CANDIDATE_UNSTAGED"
    staged = "EWS_ADMISSION_CANDIDATE_STAGED"
    committed = "EWS_IMPLEMENTATION_ADMITTED_COMMITTED"
    check(unstaged)
    path = "hedgehog/action_commit_packet_v02.py"
    file = root / path
    original = file.read_bytes()
    file.write_bytes(original + b"\n# Unapproved bytes\n")
    check(reason="ews.source_identity:" + path)
    file.write_bytes(original)
    file.chmod(0o755)
    check(reason="ews.mode_or_lf:" + path)
    file.chmod(0o644)
    file.unlink()
    check(reason="ews.file_type:" + path)
    file.symlink_to(REPOSITORY_ROOT / path)
    check(reason="ews.file_type:" + path)
    file.unlink()
    file.write_bytes(original)
    extra = root / "foreign_landing.txt"
    extra.write_text("Unapproved path\n")
    check(reason="ews.candidate.exact_ledger")
    extra.unlink()
    metadata_path = root / "release/current_status_overlay_v01.json"
    raw = metadata_path.read_bytes()
    metadata = json.loads(raw)
    metadata["ephemeral_workspace_admission_v01"]["authority"] = "ROOT"
    metadata_path.write_text(json.dumps(metadata) + "\n")
    check(reason="ews.admission_metadata")
    metadata_path.write_bytes(raw)
    git("add", "--", path)
    check(reason="ews.candidate.exact_ledger")
    git("read-tree", base)
    git("update-index", "--assume-unchanged", "README.md")
    check(reason="ews.index.flags")
    git("update-index", "--no-assume-unchanged", "README.md")
    git("update-index", "--skip-worktree", "README.md")
    check(reason="ews.index.hidden_flags")
    git("update-index", "--no-skip-worktree", "README.md")
    parent = namespace["EWS_BASE_PARENT_V01"]
    git("update-ref", "refs/remotes/origin/main", parent)
    check(reason="ews.candidate.basis_origin")
    git("update-ref", "refs/remotes/origin/main", base)
    git("update-ref", "refs/heads/main", parent)
    check(reason="ews.exact_immediate_L_child")
    git("update-ref", "refs/heads/main", base)
    check(unstaged)
    git("add", "--", *sorted(actions))
    check(staged)
    tree = git("write-tree")
    env = dict(os.environ, GIT_AUTHOR_NAME="Isolated admission fixture",
               GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Isolated admission fixture",
               GIT_COMMITTER_EMAIL="fixture@example.invalid")
    child = git("commit-tree", tree, "-p", base, "-m", namespace["EWS_COMMIT_MESSAGE_V01"], env=env)
    git("update-ref", "refs/heads/main", child)
    check(committed)
    git("update-ref", "refs/remotes/origin/main", child)
    check(committed)
    foreign = git("commit-tree", tree, "-p", base, "-m", "Isolated foreign sibling", env=env)
    git("update-ref", "refs/remotes/origin/main", foreign)
    check(reason="ews.committed.origin")
    git("update-ref", "refs/remotes/origin/main", child)
    generation = git("commit-tree", tree, "-p", child, "-m", "Isolated extra generation", env=env)
    git("update-ref", "refs/heads/main", generation)
    check(reason="ews.exact_immediate_L_child")
    merge = git("commit-tree", tree, "-p", base, "-p", foreign, "-m", "Isolated merge", env=env)
    git("update-ref", "refs/heads/main", merge)
    check(reason="ews.exact_immediate_L_child")
    git("update-ref", "refs/heads/main", child)
    check(committed)


def test_ews_exact_sources_projection_and_audit_lanes_v01():
    import tomllib
    namespace = runpy.run_path(str(GUARD_PATH))
    pins = namespace["EWS_SOURCE_IDENTITIES_V01"]
    digest = namespace["_ews_source_digest_v01"]
    assert len(pins) == 65
    assert len(namespace["EWS_IMPLEMENTATION_IDENTITIES_V01"]) == 27
    for path, expected in pins.items():
        body = (REPOSITORY_ROOT / path).read_bytes()
        assert digest(path, body) == expected, path
        assert digest(path, body + b"\n# Changed input\n") != expected
    guard = "tools/check_active_architecture_authority_v01.py"
    body = ('EWS_SOURCE_IDENTITIES_V01 = {"'+guard+'": "'+'a'*64+'", "other": "'+'b'*64+'"}\n').encode()
    assert digest(guard, body) == digest(guard, body.replace(b'a'*64, b'c'*64))
    assert digest(guard, body) != digest(guard, body.replace(b'b'*64, b'c'*64))
    with pytest.raises(ValueError):
        digest(guard, body + body)
    config = tomllib.loads((REPOSITORY_ROOT / "pyproject.toml").read_text())
    previous = tomllib.loads(subprocess.check_output(("git", "show", namespace["EWS_BASE_V01"]+":pyproject.toml"), cwd=REPOSITORY_ROOT).decode())
    options = config["tool"]["pytest"]["ini_options"]
    assert options.pop("addopts") == ["--ignore=tests/test_ephemeral_workspace_evidence_v01.py", "--ignore=tests/test_ephemeral_workspace_adversarial_v01.py"]
    assert config == previous
