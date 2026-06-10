from __future__ import annotations

import pytest

from demo.run_all_layers_applied_super_smoke import (
    collect_all_layers_applied_super_smoke,
    render_all_layers_applied_super_smoke,
)
from demo.run_audit_hash_chain import canonical_hash


@pytest.fixture(scope="module")
def report():
    return collect_all_layers_applied_super_smoke()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_all_layers_applied_super_smoke(report)
    for heading in (
        "[ALL-LAYERS APPLIED SUPER-SMOKE]",
        "[INPUT / MODE]",
        "[SOURCE EVIDENCE]",
        "[LAYER MATRIX]",
        "[AUTHORITY MATRIX]",
        "[BOUNDARY MATRIX]",
        "[ROOT FINAL]",
        "[AUDIT ENTRY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.super_smoke_source_evidence.values()) == {"PASS"}


def test_eight_layer_matrix_rows_exist(report):
    assert len(report.super_smoke_layer_matrix) == 8
    assert all(row["observed"] is True for row in report.super_smoke_layer_matrix)
    assert all(
        row["root_authority_preserved"] is True
        for row in report.super_smoke_layer_matrix
    )


def test_authority_matrix_preserves_root_only_final_authority(report):
    authority = _by_id(report.super_smoke_authority_matrix, "authority_id")
    assert authority["Root"]["final_authority"] is True
    for actor in (
        "DRS retrieval",
        "ReuseScore",
        "GT",
        "ConflictCheck",
        "Audit/hash-chain",
        "NeedleCandidate",
    ):
        assert authority[actor]["final_authority"] is False


def test_permission_approval_is_not_completed_action(report):
    authority = _by_id(report.super_smoke_authority_matrix, "authority_id")
    assert authority["Permission approval"]["completed_action"] is False


def test_root_final_observes_all_layers_without_autonomy(report):
    root_final = report.super_smoke_root_final
    assert root_final["root_decision"] == "all_layers_observed_no_autonomy"
    assert root_final["root_final_authority_preserved"] is True
    assert root_final["system_ready_for_external_drs"] is False
    assert root_final["system_ready_for_marennya"] is False
    assert root_final["system_ready_for_up"] is False


def test_no_real_external_actions_or_production_persistence(report):
    boundary = _by_id(report.super_smoke_boundary_matrix, "boundary_id")[
        "non_production_boundary"
    ]
    assert boundary["no_real_external_action"] is True
    assert boundary["no_completed_dispatch"] is True
    assert boundary["no_completed_restock"] is True
    assert boundary["no_completed_certificate_submission"] is True
    assert boundary["no_direct_ready_override"] is True
    assert boundary["production_persistence"] is False


def test_no_candidate_or_installed_needle_created_by_super_smoke(report):
    boundary = _by_id(report.super_smoke_boundary_matrix, "boundary_id")[
        "non_production_boundary"
    ]
    assert boundary["protocol_candidate_created"] is False
    assert boundary["needle_candidate_created_by_super_smoke"] is False
    assert boundary["installed_needle_created"] is False


def test_no_external_system_or_deferred_layer_invoked(report):
    boundary = _by_id(report.super_smoke_boundary_matrix, "boundary_id")[
        "non_production_boundary"
    ]
    for key in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
        "global_drs_write",
        "external_drs_write",
    ):
        assert boundary[key] is False


def test_audit_hash_matches_super_smoke_proof_artifact(report):
    audit = report.super_smoke_audit_entry
    assert audit["canonical_payload_hash"] == canonical_hash(
        report.super_smoke_proof_artifact
    )
    assert audit["audit_chain_decides_truth"] is False


def test_boundary_matrix_preserves_applied_semantics(report):
    boundaries = _by_id(report.super_smoke_boundary_matrix, "boundary_id")
    assert boundaries["warehouse_not_ready_preserved"]["observed_outcome"] == (
        "not_ready"
    )
    assert boundaries["certificate_not_ready_preserved"]["observed_outcome"] == (
        "not_ready"
    )
    assert boundaries["adversarial_drs_reuse_blocked"]["attacks_blocked"] == 8
    assert boundaries["audit_proves_continuity_not_truth"][
        "audit_chain_decides_truth"
    ] is False


def test_summary_pass_and_ready_for_auditor_review(report):
    summary = report.summary
    assert summary["all_layers_applied_super_smoke_status"] == "PASS"
    assert summary["layers_observed"] == 8
    assert summary["source_statuses_all_pass"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["adversarial_drs_reuse_blocked"] is True
    assert summary["needle_candidate_created_by_super_smoke"] is False
    assert summary["installed_needle_created"] is False
    assert summary["production_autonomy_claimed"] is False
    assert summary["ready_for_auditor_review"] is True
