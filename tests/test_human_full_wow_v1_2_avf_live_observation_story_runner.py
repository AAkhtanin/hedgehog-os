from __future__ import annotations

import json
from pathlib import Path

import pytest

from demo import run_human_full_wow_v1_2_avf_live_observation_story as runner


REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 + DRS V0.2 + AVF V0.2 LIVE HUMAN STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF SEMANTIC ACTORS]",
    "[TIMELINE]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF HARD-MASKED]",
    "[WHAT AVF RANKED WITHOUT AUTHORIZING]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP DID]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH-LOCAL ACTORS DID]",
    "[WHAT ROOT DID]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[ARTIFACT EVIDENCE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

REAL_ARTIFACT_DIR = Path(
    ".tmp/full_wow_v1_2_manual_live_multillm_fractal_avf_v02/"
    "full_wow_v1_2_manual_live_multillm_fractal_avf_v02_real_20260707_191053"
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _summary(counters_override: dict[str, int] | None = None) -> dict:
    counters = {
        "semantic_actor_call_count": 6,
        "real_provider_call_count": 6,
        "fake_provider_call_count": 0,
        "network_used_count": 6,
        "gemini_called_count": 6,
        "top_level_orchestrator_llm_call_count": 1,
        "top_level_architect_llm_call_count": 1,
        "branch_local_llm_slm_call_count": 4,
        "local_drs_v0_2_resolve_invoked_count": 1,
        "local_drs_v0_2_records_evaluated_count": 11,
        "local_drs_v0_2_direct_reuse_allowed_count": 0,
        "local_drs_v0_2_root_review_required_count": 11,
        "avf_v0_2_evaluation_invoked_count": 1,
        "avf_v0_2_candidates_evaluated_count": 9,
        "avf_v0_2_top_ranked_candidate_permission_granted_count": 0,
        "avf_v0_2_action_permission_granted_count": 0,
        "avf_v0_2_final_output_created_count": 0,
        "avf_v0_2_root_bypass_count": 0,
        "bsep_created_count": 1,
        "bsep_validated_count": 1,
        "root_final_boundary_evaluated_count": 1,
        "action_commit_packet_created_count": 0,
        "receipt_created_count": 0,
        "mock_payment_executed_count": 0,
        "real_payment_executed_count": 0,
        "shipment_released_count": 0,
        "real_world_effects_count": 0,
    }
    if counters_override:
        counters.update(counters_override)
    return {
        "run_id": "full_wow_v1_2_manual_live_multillm_fractal_avf_v02_real_fixture",
        "report_id": "fixture_report",
        "final_status": "PASS",
        "stage_status": "PASS",
        "provider_mode": "real_provider",
        "model": "gemini-2.5-flash",
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "counters": counters,
    }


def _validation(canonical: dict | None = None) -> dict:
    return {"accepted": True, "errors": [], "canonical": canonical or {}}


def _orchestrator_canonical() -> dict:
    return {
        "proposal_id": "orchestrator-semantic-wow-v1-2-001",
        "suggested_route": "supplier_payment_shipment_review_v1_2",
        "evidence_needed": [
            "warehouse inventory",
            "supplier availability and blockers",
            "legal insurance and contract status",
            "accounting invoice and PO reconciliation",
            "bank payment slot and policy preview",
        ],
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
    }


def _architect_canonical() -> dict:
    return {
        "proposal_id": "architect-semantic-wow-v1-2-001",
        "root_recommendation": "needs_more_evidence",
        "result_proposal_summary": (
            "Supplier A may proceed only to scoped review. Supplier B remains "
            "blocked. Shipment release remains held. Receipt remains evidence only."
        ),
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "root_bypass_claimed": False,
    }


def _branch_canonical(branch_id: str) -> dict:
    return {
        "source_branch_id": branch_id,
        "recommended_branch_status": "accepted_for_parent_review",
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "receipt_claimed": False,
        "payment_execution_claimed": False,
        "shipment_release_claimed": False,
    }


def _write_fixture(
    tmp_path: Path,
    *,
    counters_override: dict[str, int] | None = None,
    secret_scan: dict | None = None,
    omit_file: str | None = None,
) -> Path:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    files: dict[str, object] = {
        "summary.json": _summary(counters_override),
        "secret_scan.json": secret_scan
        or {"passed": True, "matched_markers": [], "files_scanned": 36},
        "local_drs_v0_2_resolve_report.json": {
            "local_drs_v0_2_status": "PASS",
            "records_evaluated_count": 11,
            "direct_reuse_allowed_count": 0,
            "root_review_required_count": 11,
        },
        "local_drs_v0_2_freshness_table.json": {"rows": []},
        "local_drs_v0_2_lineage_table.json": {"rows": []},
        "local_drs_v0_2_provenance_table.json": {"rows": []},
        "local_drs_v0_2_reuse_decision_table.json": {"rows": []},
        "local_drs_v0_2_writeback_candidate.json": {
            "local_proof_audit_only": True,
            "production_persisted": False,
            "persisted_to_global_drs": False,
        },
        "avf_v0_2_evaluation_report.json": {
            "avf_v0_2_status": "PASS",
            "candidates_evaluated_count": 9,
            "hard_masked_count": 2,
            "unmasked_count": 7,
            "top_candidate_id": "block_supplier_b_and_hold_shipment",
            "top_candidate_score": 0.85,
        },
        "avf_v0_2_ranked_candidates.json": {"rows": []},
        "avf_v0_2_hard_mask_table.json": {"rows": []},
        "avf_v0_2_soft_mask_table.json": {"rows": []},
        "avf_v0_2_score_explanation_table.json": {"rows": []},
        "bsep_packet.json": {
            "local_drs_v0_2_resolve_invoked": True,
            "avf_v0_2_evaluation_invoked": True,
            "raw_drs_tables_included": False,
            "raw_avf_tables_included": False,
            "raw_user_text_included": False,
            "raw_provider_text_included": False,
            "raw_bank_secrets_included": False,
        },
        "top_level_orchestrator_validation.json": _validation(
            _orchestrator_canonical()
        ),
        "bsep_validation.json": {"accepted": True, "errors": []},
        "top_level_architect_validation.json": _validation(_architect_canonical()),
        "branch_legal_validation.json": _validation(_branch_canonical("legal_branch")),
        "branch_accounting_validation.json": _validation(
            _branch_canonical("accounting_branch")
        ),
        "branch_supplier_b_validation.json": _validation(
            _branch_canonical("supplier_b_branch")
        ),
        "branch_bank_policy_validation.json": _validation(
            _branch_canonical("bank_b_branch")
        ),
    }
    for name, payload in files.items():
        if name != omit_file:
            _write_json(artifact_dir / name, payload)
    if omit_file != "summary.log":
        (artifact_dir / "summary.log").write_text(
            "FINAL STATUS: PASS\nraw_response text exists only in raw artifacts\n",
            encoding="utf-8",
        )
    for name in runner.RAW_RESPONSE_FILES:
        (artifact_dir / name).write_text(
            "RAW_PROVIDER_RESPONSE_SHOULD_NOT_RENDER", encoding="utf-8"
        )
    return artifact_dir


def test_human_avf_live_story_default_skipped_closed() -> None:
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(env={})

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["story_status"] == "SKIPPED_CLOSED"
    assert report["provider_called_count"] == 0
    assert report["network_called_by_renderer_count"] == 0
    assert report["gemini_called_by_renderer_count"] == 0
    assert report["counter_table"]["action_commit_packet_created_count"] == 0
    assert report["counter_table"]["real_world_effects_count"] == 0


def test_human_avf_live_story_pass_fixture_renders_required_sections(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(tmp_path)
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )
    rendered = runner.render_human_full_wow_v1_2_avf_live_observation_story(report)

    assert report["final_status"] == "PASS"
    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "FINAL STATUS: PASS" in rendered


def test_human_avf_live_story_validates_drs_and_avf_counters(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(tmp_path)
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["validation_errors"] == []
    assert report["counter_table"]["local_drs_v0_2_records_evaluated_count"] == 11
    assert report["counter_table"]["local_drs_v0_2_direct_reuse_allowed_count"] == 0
    assert report["counter_table"]["local_drs_v0_2_root_review_required_count"] == 11
    assert report["counter_table"]["avf_v0_2_candidates_evaluated_count"] == 9
    assert report["counter_table"][
        "avf_v0_2_top_ranked_candidate_permission_granted_count"
    ] == 0


def test_human_avf_live_story_explains_drs_memory(tmp_path: Path) -> None:
    rendered = runner.render_human_full_wow_v1_2_avf_live_observation_story(
        runner.collect_human_full_wow_v1_2_avf_live_observation_story(
            artifact_dir=_write_fixture(tmp_path)
        )
    )

    assert "Supplier A prior trace was context only" in rendered
    assert "Supplier B blocker" in rendered
    assert "old receipt was not current permission" in rendered
    assert "old Root Final was not silently reused" in rendered
    assert "DRS writeback after Root was local proof/audit only" in rendered


def test_human_avf_live_story_explains_avf_pressure(tmp_path: Path) -> None:
    rendered = runner.render_human_full_wow_v1_2_avf_live_observation_story(
        runner.collect_human_full_wow_v1_2_avf_live_observation_story(
            artifact_dir=_write_fixture(tmp_path)
        )
    )

    assert "release_all_and_pay_all was hard-masked" in rendered
    assert "Supplier B payment was hard-masked" in rendered
    assert "old receipt as permission was hard-masked" in rendered
    assert "old Root Final as current decision was hard-masked" in rendered
    assert "Top rank did not grant permission" in rendered
    assert "AVF score is not authority" in rendered
    assert "HardMask is not Root" in rendered


def test_human_avf_live_story_uses_validated_semantic_outputs_not_raw_responses(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(tmp_path)
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )
    rendered = runner.render_human_full_wow_v1_2_avf_live_observation_story(report)
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "Orchestrator suggested route" in rendered
    assert "Architect recommendation" in rendered
    assert "legal_branch" in rendered
    assert "RAW_PROVIDER_RESPONSE_SHOULD_NOT_RENDER" not in rendered
    assert "raw_provider_response_rendered" in source


def test_human_avf_live_story_fails_closed_on_secret_scan_failure(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(
        tmp_path,
        secret_scan={"passed": False, "matched_markers": ["blocked_marker"]},
    )
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["failure_reason"] == "artifact_semantic_validation_failed"
    assert "secret_scan failed or matched markers" in report["validation_errors"]


def test_human_avf_live_story_fails_closed_on_effect_counter_nonzero(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(
        tmp_path, counters_override={"real_world_effects_count": 1}
    )
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert any("real_world_effects_count" in error for error in report["validation_errors"])


def test_human_avf_live_story_fails_closed_on_avf_permission_counter_nonzero(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(
        tmp_path, counters_override={"avf_v0_2_action_permission_granted_count": 1}
    )
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert any(
        "avf_v0_2_action_permission_granted_count" in error
        for error in report["validation_errors"]
    )


def test_human_avf_live_story_fails_closed_on_missing_required_artifact(
    tmp_path: Path,
) -> None:
    artifact_dir = _write_fixture(tmp_path, omit_file="avf_v0_2_evaluation_report.json")
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["failure_reason"] == "artifact_validation_failed"
    assert "avf_v0_2_evaluation_report.json: missing" in report["validation_errors"]


def test_human_avf_live_story_artifact_files_observed_only(tmp_path: Path) -> None:
    artifact_dir = _write_fixture(tmp_path)
    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=artifact_dir
    )

    assert report["artifact_files_observed_only"] is True
    assert report["provider_called_count"] == 0
    assert report["network_called_by_renderer_count"] == 0
    assert report["gemini_called_by_renderer_count"] == 0
    assert report["counter_table"]["action_commit_packet_created_count"] == 0
    assert report["counter_table"]["receipt_created_count"] == 0


def test_human_avf_live_story_optional_real_artifact_path_if_present() -> None:
    if not REAL_ARTIFACT_DIR.exists():
        pytest.skip("real AVF live observation artifact dir is not present locally")

    report = runner.collect_human_full_wow_v1_2_avf_live_observation_story(
        artifact_dir=REAL_ARTIFACT_DIR
    )
    rendered = runner.render_human_full_wow_v1_2_avf_live_observation_story(report)

    assert report["final_status"] == "PASS"
    assert "FINAL STATUS: PASS" in rendered
    assert "release_all_and_pay_all was hard-masked" in rendered


def test_human_avf_live_story_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "google.genai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "openai" not in source
    assert "subprocess" not in source
    assert "run_full_wow_v1_2_manual_live_multillm_fractal_trace" not in source
    assert "import ActionCommitPacket" not in source
    assert "from hedgehog.action" not in source
    assert "import MockBankSandbox" not in source
    assert "real_bank" not in source
    assert "real_supplier" not in source
    assert "real_warehouse" not in source
    for marker in (
        "FAKE-IBAN" + "-AL-0000-2042-SECRET",
        "sandbox" + "_token_abc",
        "beneficiary" + "_iban",
        "raw_" + "iban_value",
        "GEMINI" + "_API_KEY",
        "GOOGLE" + "_API_KEY",
    ):
        assert marker not in source
