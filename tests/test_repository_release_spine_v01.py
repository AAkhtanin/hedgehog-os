from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPOSITORY_ROOT / "AGENTS.md"
README_PATH = REPOSITORY_ROOT / "README.md"
MANIFEST_PATH = REPOSITORY_ROOT / "specs/machine_manifest_v0_25.json"
OVERLAY_PATH = REPOSITORY_ROOT / "release/current_status_overlay_v01.json"
CLAIM_INDEX_PATH = REPOSITORY_ROOT / "release/claim_to_evidence_index.md"
LIMITATIONS_PATH = REPOSITORY_ROOT / "release/current_limitations.md"
NOTES_PATH = REPOSITORY_ROOT / "release/current_release_notes.md"

ACCEPTED_PRE_R_H1_BASE_COMMIT = (
    "3785d67e9d33adf145a3f6f60981abf38767b25d"
)
ACCEPTED_PREFLIGHT_COMMIT = "df6b4904594a84519a3056e77d2af5a9eb743185"
ACCEPTED_MANIFEST_SHA256 = (
    "880cc7066e6aedbd9157bf860dcfec7836c8d9f7fb61b92e4262d30b6801aa66"
)

README_BEGIN_MARKER = "<!-- BEGIN HEDGEHOG CURRENT ENGINEERING BOUNDARY -->"
README_END_MARKER = "<!-- END HEDGEHOG CURRENT ENGINEERING BOUNDARY -->"
AGENTS_BEGIN_MARKER = (
    "Current checkpoint: R-H1 Clean-Clone, Licensing, and Release-Spine "
    "Reconciliation CLOSED_PASS."
)
AGENTS_CURRENT_BEGIN_MARKER = (
    "Current checkpoint: G2-C ExecutionModeRouter CLOSED_PASS."
)
AGENTS_END_MARKER = "## Root-centered capability geometry"

G2C_ACCEPTED_PREFLIGHT_COMMIT = (
    "4b33c8106dbb3d7b50596630cd9dcdcf3f84cfac"
)
G2C_ACCEPTED_PREFLIGHT_PATH = (
    "docs/execution_mode_router_g2_c_preflight_v01.md"
)
G2C_ACCEPTED_PREFLIGHT_SHA256 = (
    "5bea2e49a6a5ff1c80df526a142329e7e218558f64c77be0a2f64294f2673077"
)
G2C_IMPLEMENTATION_BASIS_COMMIT = (
    "27a866ca06a331b4169c56abac9a460334d75539"
)
G2C_AUDIT_COMMIT = "72854bcdc85d19e9c6a6636f9a7eedd1929f03cb"
G2C_AUDIT_COMMIT_BASELINE = G2C_AUDIT_COMMIT
G2C_AUDIT_PATH = (
    "docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log"
)
G2C_AUDIT_SHA256 = (
    "3f6aab5c26b486a463174a6d57a22097b8eee2dcd314433b27462117b21d73d5"
)
G2C_CHECKPOINT_PATH = "docs/execution_mode_router_g2_c_checkpoint_v01.md"
G2C_CLOSURE_CLAIM_ID = "claim_g2c_execution_mode_router_closed_pass"
G2C_CLOSURE_CLAIM_WORDING = (
    "Gate 2 slice G2-C ExecutionModeRouter is CLOSED_PASS."
)

G2C_CLOSURE_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/execution_mode_router_g2_c_checkpoint_v01.md",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "release/current_status_overlay_v01.json",
    "specs/machine_manifest_v0_25.json",
    "tests/test_repository_release_spine_v01.py",
)

PROTECTED_PATHS_AT_G2C_AUDIT = (
    "specs/human_passport_v0_25.md",
    "release/completion_manifest.json",
    "release/integration_seam_index.json",
    "release/integration_seam_index.md",
    "release/one_command_gauntlet.md",
    "pyproject.toml",
    "LICENSE",
    "COMMERCIAL-LICENSING.md",
)

FROZEN_EVIDENCE = {
    "completion_manifest": {
        "path": "release/completion_manifest.json",
        "sha256": (
            "02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466"
        ),
        "classification": "FROZEN_EVIDENCE",
    },
    "integration_seam_index": {
        "path": "release/integration_seam_index.json",
        "sha256": (
            "c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231"
        ),
        "classification": "FROZEN_EVIDENCE",
    },
}

IN_PROGRESS_BOUNDARY = {
    "profile_version": "v0.1",
    "boundary_id": "current_engineering_boundary_v01",
    "accepted_pre_r_h1_base_commit": ACCEPTED_PRE_R_H1_BASE_COMMIT,
    "preflight_commit": ACCEPTED_PREFLIGHT_COMMIT,
    "implementation_basis_commit": None,
    "audit_commit": None,
    "closure_commit_identity": None,
    "workstream_id": "R-H1",
    "workstream_status": "IMPLEMENTATION_IN_PROGRESS",
    "implementation_was_explicitly_authorized": True,
    "implementation_open": True,
    "closure_claimed": False,
    "independent_audit_passed": False,
    "gate1_status": "CLOSED_PASS",
    "two_domain_status": "CLOSED_PASS",
    "g2a_status": "CLOSED_PASS",
    "g2b_status": "CLOSED_PASS",
    "gate2_status": "NOT_CLOSED",
    "g2c_status": "NEXT_NOT_STARTED",
    "g2c_implementation_authorized": False,
    "public_release_claimed": False,
    "rc2_claimed": False,
    "production_readiness_claimed": False,
    "production_security_certification_claimed": False,
    "accepted_pre_r_h1_checkpoint": (
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_"
        "checkpoint_v01.md"
    ),
    "accepted_pre_r_h1_audit": (
        "docs/audit_reports/auditor_drs_semantic_address_space_"
        "reuse_certificate_g2_b_v01.log"
    ),
    "r_h1_audit_path": None,
    "r_h1_checkpoint_path": None,
    "historical_nested_objects_are_current_queue_authority": False,
}

CLOSURE_TRANSITION_FIELDS = {
    "workstream_status",
    "implementation_open",
    "closure_claimed",
    "independent_audit_passed",
    "implementation_basis_commit",
    "audit_commit",
    "closure_commit_identity",
    "r_h1_audit_path",
    "r_h1_checkpoint_path",
}

CLAIM_IDS = (
    "claim_gate1_domain_neutral_reference_kernel_closed_pass",
    "claim_two_domain_all_real_sealed_evidence_program_closed_pass",
    "claim_g2a_actionpacket_lifecycle_kill_switch_closed_pass",
    "claim_g2b_drs_semantic_address_reuse_certificate_closed_pass",
)

R_H1_CLOSURE_CLAIM_ID = (
    "claim_r_h1_clean_clone_licensing_release_spine_reconciliation_"
    "closed_pass"
)
R_H1_AUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log"
)
R_H1_CHECKPOINT_PATH = (
    "docs/"
    "clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md"
)
R_H1_CLOSURE_TEST_PATHS = (
    "tests/test_repository_maintenance_contract_v01.py",
    "tests/test_repository_release_spine_v01.py",
    "tests/test_repomix_handoff_reproducibility_v01.py",
)
R_H1_CLOSURE_CLAIM_WORDING = (
    "The R-H1 Clean-Clone, Licensing, and Release-Spine Reconciliation "
    "workstream is CLOSED_PASS."
)

CLAIM_EVIDENCE_PATHS = {
    CLAIM_IDS[0]: (
        "tests/test_kernel_conformance_v01_runner.py",
        "demo/run_kernel_conformance_v01.py",
        "docs/audit_reports/auditor_domain_neutral_reference_kernel_gate1_v01.log",
        "docs/domain_neutral_reference_kernel_gate1_checkpoint_v01.md",
    ),
    CLAIM_IDS[1]: (
        "tests/test_two_domain_airline_all_real_program_v01_runner.py",
        "tests/test_two_domain_supplier_water_filter_program_v01_runner.py",
        "docs/audit_reports/auditor_two_domain_all_real_sealed_evidence_program_v01.log",
        "docs/two_domain_all_real_sealed_evidence_program_v01_checkpoint.md",
    ),
    CLAIM_IDS[2]: (
        "tests/test_action_commit_packet_lifecycle_g2_a_v01.py",
        "demo/run_action_commit_packet_lifecycle_g2_a_v01.py",
        "docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log",
        "docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md",
    ),
    CLAIM_IDS[3]: (
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log",
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md",
    ),
}

RELEASE_SPINE_PATHS = (
    "release/claim_to_evidence_index.md",
    "release/integration_seam_index.md",
    "release/one_command_gauntlet.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _nested_mapping_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            key
            for nested in value.values()
            for key in _nested_mapping_keys(nested)
        }
    if isinstance(value, list):
        return {
            key
            for nested in value
            for key in _nested_mapping_keys(nested)
        }
    return set()


def _git_show(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ("git", "show", f"{commit}:{path}"),
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
    )
    assert completed.returncode == 0, (
        "unsupported non-Git/source-archive validation: required Git object "
        f"{commit}:{path} is unavailable; stderr="
        f"{completed.stderr.decode('utf-8', errors='replace')}"
    )
    return completed.stdout


def _current_boundary() -> dict[str, object]:
    manifest = _read_json(MANIFEST_PATH)
    checkpoint = manifest["current_checkpoint_status"]
    assert isinstance(checkpoint, dict)
    boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    return boundary


def _readme_block(raw: bytes) -> bytes:
    begin = README_BEGIN_MARKER.encode("utf-8")
    end = README_END_MARKER.encode("utf-8")
    assert raw.count(begin) == 1
    assert raw.count(end) == 1
    begin_offset = raw.index(begin)
    end_offset = raw.index(end)
    assert begin_offset < end_offset
    assert begin not in raw[begin_offset + len(begin) : end_offset]
    return raw[begin_offset : end_offset + len(end)]


def _readme_without_block(raw: bytes) -> bytes:
    block = _readme_block(raw)
    return raw.replace(block, b"", 1)


def _agents_block(raw: bytes) -> bytes:
    starts = tuple(
        marker.encode("utf-8")
        for marker in (AGENTS_BEGIN_MARKER, AGENTS_CURRENT_BEGIN_MARKER)
        if marker.encode("utf-8") in raw
    )
    end = AGENTS_END_MARKER.encode("utf-8")
    assert len(starts) == 1
    assert raw.count(starts[0]) == 1
    assert raw.count(end) == 1
    begin_offset = raw.index(starts[0])
    end_offset = raw.index(end)
    assert begin_offset < end_offset
    return raw[begin_offset:end_offset]


def _agents_without_block(raw: bytes) -> bytes:
    block = _agents_block(raw)
    return raw.replace(block, b"", 1)


def _revert_g2c_boundary_transition(
    document: dict[str, object],
    *,
    overlay: bool,
) -> dict[str, object]:
    reverted = copy.deepcopy(document)
    if overlay:
        boundary = reverted["current_engineering_boundary"]
    else:
        checkpoint = reverted["current_checkpoint_status"]
        assert isinstance(checkpoint, dict)
        boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    boundary["g2c_status"] = "NEXT_NOT_STARTED"
    boundary["g2c_implementation_authorized"] = False
    return reverted


def _assert_exactly_once(text: str, required: tuple[str, ...]) -> None:
    for value in required:
        assert text.count(value) == 1, value


def _assert_absent(text: str, forbidden: tuple[str, ...]) -> None:
    for value in forbidden:
        assert value not in text, value


def _assert_closed_boundary(boundary: dict[str, object]) -> None:
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY)
    assert re.fullmatch(r"[0-9a-f]{40}", boundary["implementation_basis_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", boundary["audit_commit"])
    assert boundary["closure_commit_identity"] == "NOT_SELF_RECORDED"
    assert boundary["workstream_status"] == "CLOSED_PASS"
    assert boundary["implementation_was_explicitly_authorized"] is True
    assert boundary["implementation_open"] is False
    assert boundary["closure_claimed"] is True
    assert boundary["independent_audit_passed"] is True
    assert boundary["r_h1_audit_path"] == R_H1_AUDIT_PATH
    assert boundary["r_h1_checkpoint_path"] == R_H1_CHECKPOINT_PATH
    assert boundary["g2c_status"] == "CLOSED_PASS"
    assert boundary["g2c_implementation_authorized"] is True

    basis_commit = boundary["implementation_basis_commit"]
    assert isinstance(basis_commit, str)
    basis_manifest = json.loads(
        _git_show(basis_commit, "specs/machine_manifest_v0_25.json")
    )
    basis_boundary = basis_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    assert basis_boundary == IN_PROGRESS_BOUNDARY
    r_h1_closure_boundary = copy.deepcopy(boundary)
    r_h1_closure_boundary["g2c_status"] = "NEXT_NOT_STARTED"
    r_h1_closure_boundary["g2c_implementation_authorized"] = False
    changed_fields = {
        key
        for key in r_h1_closure_boundary
        if r_h1_closure_boundary[key] != basis_boundary[key]
    }
    assert changed_fields == CLOSURE_TRANSITION_FIELDS


def test_manifest_baseline_is_preserved_by_one_add_only_boundary() -> None:
    baseline_bytes = _git_show(
        ACCEPTED_PRE_R_H1_BASE_COMMIT,
        "specs/machine_manifest_v0_25.json",
    )
    assert _sha256_bytes(baseline_bytes) == ACCEPTED_MANIFEST_SHA256
    baseline = json.loads(baseline_bytes)
    current = _read_json(MANIFEST_PATH)

    checkpoint = current["current_checkpoint_status"]
    assert isinstance(checkpoint, dict)
    assert tuple(checkpoint).count("current_engineering_boundary_v01") == 1
    boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY)

    current_without_boundary = copy.deepcopy(current)
    removed = current_without_boundary["current_checkpoint_status"].pop(
        "current_engineering_boundary_v01"
    )
    assert removed == boundary
    assert current_without_boundary == baseline
    assert checkpoint["metadata_sync_only"] is True
    assert checkpoint["manifest_does_not_override_human_passport"] is True


def test_g2c_manifest_transition_is_exactly_two_children() -> None:
    audit_manifest = json.loads(
        _git_show(G2C_AUDIT_COMMIT_BASELINE, MANIFEST_PATH.relative_to(
            REPOSITORY_ROOT
        ).as_posix())
    )
    current_manifest = _read_json(MANIFEST_PATH)
    audit_boundary = audit_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    current_boundary = current_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    assert isinstance(audit_boundary, dict)
    assert isinstance(current_boundary, dict)
    assert set(current_boundary) == set(audit_boundary)
    assert audit_boundary["g2c_status"] == "NEXT_NOT_STARTED"
    assert audit_boundary["g2c_implementation_authorized"] is False
    assert current_boundary["g2c_status"] == "CLOSED_PASS"
    assert current_boundary["g2c_implementation_authorized"] is True
    assert _revert_g2c_boundary_transition(
        current_manifest,
        overlay=False,
    ) == audit_manifest


def test_current_boundary_has_exact_supported_lifecycle_geometry() -> None:
    boundary = _current_boundary()
    status = boundary["workstream_status"]
    assert status in {"IMPLEMENTATION_IN_PROGRESS", "CLOSED_PASS"}
    assert status != "PREFLIGHT_ONLY"

    if status == "IMPLEMENTATION_IN_PROGRESS":
        assert boundary == IN_PROGRESS_BOUNDARY
    else:
        _assert_closed_boundary(boundary)


def test_readme_current_boundary_install_and_license_are_bounded() -> None:
    raw = README_PATH.read_bytes()
    text = raw.decode("utf-8")
    block = _readme_block(raw).decode("utf-8")
    boundary = _current_boundary()

    common_lines = {
        "workstream_id: R-H1",
        "implementation_was_explicitly_authorized: true",
        f"accepted_pre_r_h1_base_commit: {ACCEPTED_PRE_R_H1_BASE_COMMIT}",
        f"preflight_commit: {ACCEPTED_PREFLIGHT_COMMIT}",
        "gate1_status: CLOSED_PASS",
        "two_domain_status: CLOSED_PASS",
        "g2a_status: CLOSED_PASS",
        "g2b_status: CLOSED_PASS",
        "gate2_status: NOT_CLOSED",
        "g2c_status: CLOSED_PASS",
        "g2c_implementation_authorized: true",
        f"g2c_preflight_commit: {G2C_ACCEPTED_PREFLIGHT_COMMIT}",
        f"g2c_implementation_basis_commit: {G2C_IMPLEMENTATION_BASIS_COMMIT}",
        f"g2c_audit_commit: {G2C_AUDIT_COMMIT}",
        "g2c_closure_commit_identity: NOT_SELF_RECORDED",
        "g2d_status: NEXT_NOT_STARTED",
        "g2d_implementation_authorized: false",
        "g2d_implementation_started: false",
        "public_release_claimed: false",
        "rc2_claimed: false",
        "production_readiness_claimed: false",
        "production_security_certification_claimed: false",
    }
    for line in common_lines:
        assert line in block

    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        _assert_exactly_once(block, (
            "workstream_status: IMPLEMENTATION_IN_PROGRESS",
            "implementation_open: true",
            "closure_claimed: false",
            "independent_audit_passed: false",
            "implementation_basis_commit: NOT_YET_SYNCHRONIZED",
            "audit_commit: NOT_YET_SYNCHRONIZED",
            "closure_commit_identity: NOT_APPLICABLE",
            "R-H1 independent audit synchronized for closure: `false`",
            "R-H1 checkpoint: `NOT_YET_PRESENT`",
            "R-H1 is not closed",
        ))
        _assert_absent(block, (
            "workstream_status: CLOSED_PASS",
            "implementation_open: false",
            "closure_claimed: true",
            "independent_audit_passed: true",
            "closure_commit_identity: NOT_SELF_RECORDED",
            "R-H1 independent audit synchronized for closure: `true`",
            "R-H1 is `CLOSED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        _assert_exactly_once(block, (
            "workstream_status: CLOSED_PASS",
            "implementation_open: false",
            "closure_claimed: true",
            "independent_audit_passed: true",
            f"implementation_basis_commit: {boundary['implementation_basis_commit']}",
            f"audit_commit: {boundary['audit_commit']}",
            "\nclosure_commit_identity: NOT_SELF_RECORDED\n",
            "R-H1 independent audit synchronized for closure: `true`",
            f"R-H1 audit: `{R_H1_AUDIT_PATH}`",
            f"R-H1 checkpoint: `{R_H1_CHECKPOINT_PATH}`",
            "R-H1 is `CLOSED_PASS`",
            "G2-C ExecutionModeRouter are `CLOSED_PASS`",
            "G2-D is `NEXT / NOT_STARTED` and `NOT_AUTHORIZED`",
            f"[Accepted G2-C preflight]({G2C_ACCEPTED_PREFLIGHT_PATH})",
            f"[G2-C independent audit]({G2C_AUDIT_PATH})",
            f"[G2-C checkpoint]({G2C_CHECKPOINT_PATH})",
        ))
        assert block.count(R_H1_AUDIT_PATH) == 1
        assert block.count(R_H1_CHECKPOINT_PATH) == 1
        _assert_absent(block, (
            "workstream_status: IMPLEMENTATION_IN_PROGRESS",
            "implementation_open: true",
            "closure_claimed: false",
            "independent_audit_passed: false",
            "implementation_basis_commit: NOT_YET_SYNCHRONIZED",
            "audit_commit: NOT_YET_SYNCHRONIZED",
            "closure_commit_identity: NOT_APPLICABLE",
            "R-H1 independent audit synchronized for closure: `false`",
            "R-H1 checkpoint: `NOT_YET_PRESENT`",
            "R-H1 is not closed",
        ))

        audit_readme = _git_show(G2C_AUDIT_COMMIT_BASELINE, "README.md")
        assert _readme_without_block(raw) == _readme_without_block(audit_readme)

    for path in RELEASE_SPINE_PATHS:
        assert path in block
    assert (
        "docs/clean_clone_licensing_release_spine_reconciliation_r_h1_"
        "preflight_v01.md"
    ) in block
    assert "G2-C is in development" not in block
    assert "G2-C is `NEXT / NOT_STARTED`" not in block
    assert "g2c_status: NEXT_NOT_STARTED" not in block
    assert "g2c_implementation_authorized: false" not in block

    assert "python3 -m venv .venv" in text
    assert ".venv/bin/python -m pip install -e ." in text
    assert ".venv/bin/python -m pip check" in text
    assert ".venv/bin/python -m demo.run_kernel_conformance_v01" in text
    assert ".venv/bin/python -m demo.run_living_gauntlet_v01" in text
    assert "This README section does not" in text
    assert "itself claim an external clean-clone result" in text
    assert "release/current_limitations.md" in text

    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    assert project["license"] == "AGPL-3.0-only"
    assert project["license-files"] == ["LICENSE"]
    assert "`AGPL-3.0-only`" in text
    assert "[LICENSE](LICENSE)" in text
    assert "[COMMERCIAL-LICENSING.md](COMMERCIAL-LICENSING.md)" in text
    assert "non-granting" in text
    assert "informational policy notice" in text
    assert "not a granted license" in text


def test_agents_g2c_closure_block_is_exactly_bounded() -> None:
    raw = AGENTS_PATH.read_bytes()
    block = _agents_block(raw).decode("utf-8")
    audit_agents = _git_show(G2C_AUDIT_COMMIT_BASELINE, "AGENTS.md")
    assert _agents_without_block(raw) == _agents_without_block(audit_agents)
    _assert_exactly_once(block, (
        AGENTS_CURRENT_BEGIN_MARKER,
        f"Accepted G2-C preflight commit: `{G2C_ACCEPTED_PREFLIGHT_COMMIT}`",
        f"Accepted G2-C preflight path: `{G2C_ACCEPTED_PREFLIGHT_PATH}`",
        f"G2-C implementation basis: `{G2C_IMPLEMENTATION_BASIS_COMMIT}`",
        f"G2-C audit commit: `{G2C_AUDIT_COMMIT}`",
        f"G2-C audit: `{G2C_AUDIT_PATH}`",
        f"G2-C checkpoint: `{G2C_CHECKPOINT_PATH}`",
        "Closure commit identity: `NOT_SELF_RECORDED`",
        "R-H1 status: `CLOSED_PASS`",
        "G2-A: `CLOSED_PASS`",
        "G2-B: `CLOSED_PASS`",
        "G2-C: `CLOSED_PASS`",
        "Gate 2: `NOT_CLOSED`",
        "G2-D: `NEXT / NOT_STARTED`",
        "G2-D implementation: `NOT_AUTHORIZED`",
        "G2-D implementation started: `false`",
        "Public release: `NOT_CLAIMED`",
        "RC2: `NOT_CLAIMED`",
        "Production readiness: `NOT_CLAIMED`",
        "Production security certification: `NOT_CLAIMED`",
        "Real-world effects remain zero",
    ))
    _assert_absent(block, (
        "G2-C: `NEXT / NOT_STARTED`",
        "G2-C implementation: `NOT_AUTHORIZED`",
        "read-only G2-C inventory",
        "No G2-C slice names",
    ))


def test_current_status_overlay_is_exact_and_non_authoritative() -> None:
    overlay = _read_json(OVERLAY_PATH)
    assert tuple(overlay) == (
        "profile_version",
        "overlay_id",
        "overlay_role",
        "current_engineering_boundary",
        "frozen_evidence",
        "does_not_override",
        "release_spine_paths",
    )
    assert overlay["profile_version"] == "v0.1"
    assert overlay["overlay_id"] == "current_status_overlay_v01"
    assert overlay["overlay_role"] == {
        "metadata_only": True,
        "is_authority": False,
        "is_root_decision": False,
        "is_completion_certificate": False,
        "replaces_historical_evidence": False,
        "is_gate2_closure_manifest": False,
        "is_public_release_declaration": False,
    }
    assert overlay["current_engineering_boundary"] == _current_boundary()
    assert overlay["frozen_evidence"] == FROZEN_EVIDENCE
    assert overlay["does_not_override"] == [
        "owner_instruction",
        "AGENTS.md",
        "accepted_checkpoints",
        "accepted_audits",
        "specs/human_passport_v0_25.md",
    ]
    assert overlay["release_spine_paths"] == list(RELEASE_SPINE_PATHS)
    assert "implementation_authorized" not in _nested_mapping_keys(overlay)
    assert "head" not in overlay["current_engineering_boundary"]
    boundary = overlay["current_engineering_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["g2c_status"] == "CLOSED_PASS"
    assert boundary["g2c_implementation_authorized"] is True

    audit_overlay = json.loads(
        _git_show(G2C_AUDIT_COMMIT_BASELINE, "release/current_status_overlay_v01.json")
    )
    audit_boundary = audit_overlay["current_engineering_boundary"]
    assert isinstance(audit_boundary, dict)
    assert audit_boundary["g2c_status"] == "NEXT_NOT_STARTED"
    assert audit_boundary["g2c_implementation_authorized"] is False
    assert _revert_g2c_boundary_transition(
        overlay,
        overlay=True,
    ) == audit_overlay


def test_frozen_gate1_release_evidence_hashes_are_exact() -> None:
    for evidence in FROZEN_EVIDENCE.values():
        path = REPOSITORY_ROOT / evidence["path"]
        assert path.is_file()
        assert _sha256_bytes(path.read_bytes()) == evidence["sha256"]


def test_release_spine_roles_claims_and_commands_are_bounded() -> None:
    for path in RELEASE_SPINE_PATHS:
        assert (REPOSITORY_ROOT / path).is_file()

    claim_text = CLAIM_INDEX_PATH.read_text(encoding="utf-8")
    observed_claim_ids = tuple(re.findall(r"\bclaim_[a-z0-9_]+\b", claim_text))
    boundary = _current_boundary()
    claim_normalized = " ".join(claim_text.split())
    for required in (
        "At the R-H1A implementation boundary, R-H1 was "
        "`IMPLEMENTATION_IN_PROGRESS`.",
        "Limitation at that boundary: R-H1 as a whole remained "
        "`IMPLEMENTATION_IN_PROGRESS`; no accepted R-H1 audit and checkpoint "
        "had yet been synchronized into R-H1 closure status.",
    ):
        assert required in claim_normalized
    _assert_absent(claim_normalized, (
        "Workstream: R-H1, `IMPLEMENTATION_IN_PROGRESS`.",
        "R-H1 as a whole remains `IMPLEMENTATION_IN_PROGRESS`",
    ))
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert observed_claim_ids == CLAIM_IDS
        assert R_H1_CLOSURE_CLAIM_ID not in claim_text
        assert (
            "R-H1A Maintenance Implementation Evidence - Not a Closure Claim"
            in claim_text
        )
    else:
        assert observed_claim_ids == CLAIM_IDS + (
            R_H1_CLOSURE_CLAIM_ID,
            G2C_CLOSURE_CLAIM_ID,
        )
        closure_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {R_H1_CLOSURE_CLAIM_ID} |" in line
        )
        assert R_H1_CLOSURE_CLAIM_WORDING in closure_row
        assert "CLOSED_PASS" in closure_row
        for path in (
            *R_H1_CLOSURE_TEST_PATHS,
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ):
            assert path in closure_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "does not close Gate 2",
            "does not start or authorize G2-C",
            "does not declare a public release",
            "does not declare RC2",
            "does not claim production readiness",
            "does not claim production security certification",
        ):
            assert limitation in closure_row
        g2c_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2C_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2C_CLOSURE_CLAIM_WORDING in g2c_row
        assert "CLOSED_PASS" in g2c_row
        for path in (
            "tests/test_execution_mode_router_g2_c_v01.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "tests/test_repository_release_spine_v01.py",
            "demo/run_execution_mode_router_g2_c_v01.py",
            "demo/run_living_gauntlet_v01.py",
            "demo/run_kernel_conformance_v01.py",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
        ):
            assert path in g2c_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "does not close Gate 2",
            "does not start or authorize G2-D",
            "does not declare a public release",
            "does not declare RC2",
            "does not claim production readiness",
            "does not claim production security certification",
            "creates no topology or real-world effect",
        ):
            assert limitation in g2c_row
    for claim_id, paths in CLAIM_EVIDENCE_PATHS.items():
        row = next(
            line for line in claim_text.splitlines() if f"| {claim_id} |" in line
        )
        assert "CLOSED_PASS" in row
        assert "Limitation" not in row
        for path in paths:
            assert path in row
            assert (REPOSITORY_ROOT / path).exists()
    assert "233 passed" in claim_text
    assert "R-H1A is not an independent audit" in claim_text

    seam_text = (REPOSITORY_ROOT / "release/integration_seam_index.md").read_text(
        encoding="utf-8"
    )
    seam_normalized = " ".join(seam_text.split())
    assert "release/integration_seam_index.json" in seam_text
    assert FROZEN_EVIDENCE["integration_seam_index"]["sha256"] in seam_text
    assert "not a final Gate-2 seam inventory" in seam_text
    assert seam_text.count("| r_h1_") == 8
    assert seam_text.count("IMPLEMENTATION_IN_PROGRESS") >= 9
    assert "R-H1B implementation-basis maintenance" in seam_normalized
    assert "row statuses are basis evidence" in seam_normalized
    assert "not the mutable current R-H1 lifecycle authority" in seam_normalized

    gauntlet_text = (REPOSITORY_ROOT / "release/one_command_gauntlet.md").read_text(
        encoding="utf-8"
    )
    command_blocks = re.findall(r"```bash\n(.*?)```", gauntlet_text, flags=re.DOTALL)
    assert len(command_blocks) == 2
    execution_command = command_blocks[1]
    assert execution_command.count("demo.run_kernel_conformance_v01") == 1
    assert execution_command.count("demo.run_living_gauntlet_v01") == 1
    assert "&&" in execution_command
    for forbidden in ("--live", "gemini", "provider", "telegram", "connector"):
        assert forbidden not in execution_command.lower()
    assert "NOT_YET_COMPLETED" not in gauntlet_text
    assert "release/current_limitations.md" in gauntlet_text
    assert "accepted R-H1 audit/checkpoint" in gauntlet_text

    limitations = (REPOSITORY_ROOT / "release/current_limitations.md").read_text(
        encoding="utf-8"
    )
    limitations_normalized = " ".join(limitations.split())
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        for required in (
            "R-H1 is `IMPLEMENTATION_IN_PROGRESS`",
            "R-H1 independent audit is not yet synchronized into accepted "
            "closure status",
            "External clean-clone validation is not yet synchronized into "
            "accepted R-H1 closure status",
            "Gate 2 is `NOT_CLOSED`",
            "G2-C is `NEXT / NOT_STARTED`",
            "G2-C implementation is `NOT_AUTHORIZED`",
            "Public release is `NOT_CLAIMED`",
            "RC2 is `NOT_CLAIMED`",
            "Production readiness is `NOT_CLAIMED`",
            "Production security certification is `NOT_CLAIMED`",
            "Standalone wheel completeness is `NOT_CLAIMED`",
        ):
            assert required in limitations_normalized
        _assert_absent(limitations, (
            "R-H1 is `CLOSED_PASS`",
            "External clean-clone validation is `ACCEPTED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        for required in (
            "R-H1 is `CLOSED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
            "External clean-clone validation is `ACCEPTED_PASS` for the "
            "audited implementation basis",
            "G2-C is `CLOSED_PASS`",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
            "Gate 2 remains `NOT_CLOSED`",
            "G2-D is `NEXT / NOT_STARTED`",
            "G2-D implementation remains `NOT_AUTHORIZED`",
            "Public release remains `NOT_CLAIMED`",
            "RC2 remains `NOT_CLAIMED`",
            "Production readiness remains `NOT_CLAIMED`",
            "Production security certification remains `NOT_CLAIMED`",
            "No real-world effect is claimed",
            "No RuntimeExecutionTopology was created by G2-C",
            "metadata-only and non-authoritative",
            "frozen Gate-1 evidence",
        ):
            assert required in limitations_normalized
        _assert_absent(limitations, (
            "IMPLEMENTATION_IN_PROGRESS",
            "NOT_YET_PRESENT",
            "NOT_YET_SYNCHRONIZED",
            "not yet synchronized",
            "not yet completed",
            "NOT_YET_COMPLETED",
            "G2-C remains `NEXT / NOT_STARTED`",
            "G2-C implementation remains `NOT_AUTHORIZED`",
        ))

    notes = (REPOSITORY_ROOT / "release/current_release_notes.md").read_text(
        encoding="utf-8"
    )
    assert notes.startswith("# Current Engineering Notes\n")
    assert "not a public release announcement" in notes
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert "R-H1 remains `IMPLEMENTATION_IN_PROGRESS`" in notes
        assert (
            "At the R-H1B implementation boundary, R-H1C, R-H1D1, and R-H1D2 "
            "had not started"
        ) in " ".join(notes.split())
        assert "This R-H1B implementation note does not itself claim" in notes
        _assert_absent(notes, (
            "R-H1 is `CLOSED_PASS`",
            "External clean-clone validation: `ACCEPTED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        for required in (
            "R-H1 is `CLOSED_PASS`",
            f"implementation_basis_commit: {boundary['implementation_basis_commit']}",
            f"audit_commit: {boundary['audit_commit']}",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
            "External clean-clone validation: `ACCEPTED_PASS`",
            f"Accepted G2-C preflight commit:\n  `{G2C_ACCEPTED_PREFLIGHT_COMMIT}`",
            f"G2-C implementation basis commit:\n  `{G2C_IMPLEMENTATION_BASIS_COMMIT}`",
            f"G2-C audit commit:\n  `{G2C_AUDIT_COMMIT}`",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
            "G2-C closure_commit_identity: `NOT_SELF_RECORDED`",
            "G2-C is `CLOSED_PASS`",
            "Gate 2 remains `NOT_CLOSED`",
            "G2-D is `NEXT / NOT_STARTED` and `NOT_AUTHORIZED`",
            "G2-D implementation started: `false`",
            "No implementation repair occurred during the independent audit or this",
            "except the single\n  release-spine closure test",
            "Public release remains `NOT_CLAIMED`",
            "RC2 remains `NOT_CLAIMED`",
            "Production readiness remains `NOT_CLAIMED`",
            "Production security certification remains `NOT_CLAIMED`",
            "Real-world effects remain zero",
        ):
            assert required in notes
        _assert_absent(notes, (
            "IMPLEMENTATION_IN_PROGRESS",
            "This R-H1B implementation note does not itself claim",
            "R-H1C, R-H1D1, and R-H1D2 had not started",
            "not yet synchronized",
            "NOT_YET_PRESENT",
            "NOT_YET_COMPLETED",
            "G2-C remains `NEXT / NOT_STARTED`",
            "read-only G2-C inventory",
        ))
    assert "Gate 2 remains `NOT_CLOSED`" in notes
    assert "G2-C is `CLOSED_PASS`" in notes
    assert "G2-D is `NEXT / NOT_STARTED` and `NOT_AUTHORIZED`" in notes


def test_current_surfaces_preserve_status_and_licensing_nonclaims() -> None:
    current_text = "\n".join((
        _readme_block(README_PATH.read_bytes()).decode("utf-8"),
        _agents_block(AGENTS_PATH.read_bytes()).decode("utf-8"),
        CLAIM_INDEX_PATH.read_text(encoding="utf-8"),
        LIMITATIONS_PATH.read_text(encoding="utf-8"),
        NOTES_PATH.read_text(encoding="utf-8"),
        (REPOSITORY_ROOT / G2C_CHECKPOINT_PATH).read_text(encoding="utf-8"),
        json.dumps(_read_json(OVERLAY_PATH), sort_keys=True),
    ))
    lowered = current_text.lower()

    assert "g2-c is in development" not in lowered
    assert "functional equivalents are licensed" not in lowered
    for affirmative_claim in (
        "title is established",
        "relicensing authority is established",
        "patent clearance is complete",
        "legal review is complete",
    ):
        assert affirmative_claim not in lowered

    boundary = _current_boundary()
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert "R-H1 is `IMPLEMENTATION_IN_PROGRESS`" in current_text
        assert "R-H1 remains `IMPLEMENTATION_IN_PROGRESS`" in current_text
        assert "Gate 2 is `NOT_CLOSED`" in current_text
        assert "G2-C is `NEXT / NOT_STARTED`" in current_text
    else:
        assert "R-H1 is `CLOSED_PASS`" in current_text
        assert "Gate 2 remains `NOT_CLOSED`" in current_text
        assert "G2-C is `CLOSED_PASS`" in current_text
        assert "G2-D is `NEXT / NOT_STARTED`" in current_text
        assert "G2-D implementation remains `NOT_AUTHORIZED`" in current_text
        _assert_absent(current_text, (
            "G2-C remains `NEXT / NOT_STARTED`",
            "G2-C is `NEXT / NOT_STARTED`",
            "G2-C implementation remains `NOT_AUTHORIZED`",
            '"g2c_status": "NEXT_NOT_STARTED"',
            '"g2c_implementation_authorized": false',
        ))


def test_g2c_checkpoint_metadata_scope_and_nonclaims_are_exact() -> None:
    checkpoint_path = REPOSITORY_ROOT / G2C_CHECKPOINT_PATH
    assert checkpoint_path.is_file()
    text = checkpoint_path.read_text(encoding="utf-8")
    required_sections = tuple(f"## {index}. " for index in range(1, 9))
    offsets = tuple(text.index(section) for section in required_sections)
    assert offsets == tuple(sorted(offsets))
    _assert_exactly_once(text, (
        "document_status: CHECKPOINT",
        "checkpoint_id: execution_mode_router_g2_c_v01",
        "checkpoint_status: CLOSED_PASS",
        "gate_id: gate2_g2c_execution_mode_router",
        "gate_slice: G2-C",
        "closure_date: 2026-08-03",
        f"accepted_preflight_commit:\n{G2C_ACCEPTED_PREFLIGHT_COMMIT}",
        f"accepted_preflight_path:\n{G2C_ACCEPTED_PREFLIGHT_PATH}",
        f"accepted_preflight_sha256:\n{G2C_ACCEPTED_PREFLIGHT_SHA256}",
        f"implementation_basis_commit:\n{G2C_IMPLEMENTATION_BASIS_COMMIT}",
        f"audit_commit:\n{G2C_AUDIT_COMMIT}",
        f"audit_path:\n{G2C_AUDIT_PATH}",
        f"audit_sha256:\n{G2C_AUDIT_SHA256}",
        "closure_commit_identity: NOT_SELF_RECORDED",
        "G2-C status: `CLOSED_PASS`",
        "Gate 2 status: `NOT_CLOSED`",
        "G2-D status: `NEXT / NOT_STARTED`",
        "G2-D implementation authorized: `false`",
        "G2-D implementation started: `false`",
        "Human Passport changed: `false`",
        "Public release: `NOT_CLAIMED`",
        "RC2: `NOT_CLAIMED`",
        "Production readiness: `NOT_CLAIMED`",
        "Production security certification: `NOT_CLAIMED`",
        "Publication before Gate 6 closure and separate owner approval: not allowed",
        "Real-world effects: `0`",
    ))
    for path in G2C_CLOSURE_PATHS:
        assert f"`{path}`" in text
    for commit in (
        G2C_ACCEPTED_PREFLIGHT_COMMIT,
        "664bf5c0496d69e8a29dc0dc667f8c009a936222",
        "e0c13919222b40a21b0ed0662c1144a5971209af",
        "80090cfed292346f1bef3a93e2c6d46b45686f83",
        "87fbae934192498a13362f76e9d4af3cd288475b",
        "1782ad40ec64f3c1a1d3960628208110d2c54a57",
        G2C_IMPLEMENTATION_BASIS_COMMIT,
        G2C_AUDIT_COMMIT,
    ):
        assert commit in text
    for required in (
        "Total G2-C types: `13`",
        "Total public G2-C functions: `74`",
        "Public G2-C reasons: `100`",
        "Direct package G2-C attributes: `87`",
        "Canonical domains: `2`",
        "Canonical scenarios: `10`",
        "Exact pipeline order: `17` steps",
        "RuntimeExecutionTopology created by G2-C: `false`",
        "C5 targeted tests: `139 passed`",
        "Complete Router: `392 passed`",
        "Complete Transition: `237 passed`",
        "C5 focused: `4038 passed`",
        "C6 targeted: `13 passed`",
        "Complete Living: `569 passed`",
        "Complete Conformance: `310 passed`",
        "Exact cumulative: `4917 passed`",
        FROZEN_EVIDENCE["completion_manifest"]["sha256"],
        FROZEN_EVIDENCE["integration_seam_index"]["sha256"],
    ):
        assert required in text


def test_g2c_preflight_audit_and_protected_bytes_are_exact() -> None:
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2C_ACCEPTED_PREFLIGHT_PATH).read_bytes()
    ) == G2C_ACCEPTED_PREFLIGHT_SHA256
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2C_AUDIT_PATH).read_bytes()
    ) == G2C_AUDIT_SHA256
    for path in PROTECTED_PATHS_AT_G2C_AUDIT:
        current = (REPOSITORY_ROOT / path).read_bytes()
        assert current == _git_show(G2C_AUDIT_COMMIT_BASELINE, path), path


def test_g2c_closure_git_scope_is_exactly_nine_paths() -> None:
    completed = subprocess.run(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    observed: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        status = line[:2]
        path = line[3:]
        assert " -> " not in path
        observed[path] = status
    assert tuple(sorted(observed)) == G2C_CLOSURE_PATHS
    assert observed[G2C_CHECKPOINT_PATH] == "??"
    for path in G2C_CLOSURE_PATHS:
        if path != G2C_CHECKPOINT_PATH:
            assert observed[path] == " M"
