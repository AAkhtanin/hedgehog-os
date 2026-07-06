from __future__ import annotations

import json
from pathlib import Path

from demo import run_human_full_wow_v1_2_live_fractal_story as runner


REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 LIVE FRACTAL HUMAN STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF SEMANTIC ACTORS]",
    "[TIMELINE]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP DID]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH-LOCAL ACTORS DID]",
    "[WHAT THE FRACTAL PART MEANS]",
    "[WHAT THE BANK PART MEANS]",
    "[WHAT ROOT DID]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

VALIDATION_FILES = (
    "top_level_orchestrator_validation.json",
    "bsep_validation.json",
    "top_level_architect_validation.json",
    "branch_legal_validation.json",
    "branch_accounting_validation.json",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_validation.json",
)

FORBIDDEN_PHRASE_PARTS = (
    ("production", " ready"),
    ("public WOW", " ready"),
    ("public auditor", " ready"),
    ("real payment", " executed"),
    ("real shipment", " released"),
    ("Gemini creates", " ActionCommitPacket"),
    ("Gemini creates", " receipt"),
    ("receipt proves", " truth"),
    ("receipt grants", " permission"),
    ("receipt creates", " FinalOutput"),
    ("real_world_effects_count: ", "1"),
)

SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "raw_iban_value",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _valid_summary(final_status: str = "PASS") -> dict:
    return {
        "final_status": final_status,
        "stage_status": final_status,
        "provider_mode": "real_provider",
        "model": "gemini-2.5-flash",
        "run_id": "fixture_manual_live_multillm_fractal_run",
        "report_id": "fixture_manual_live_multillm_fractal_report",
        "counters": {
            "semantic_actor_call_count": 6,
            "real_provider_call_count": 6,
            "network_used_count": 6,
            "gemini_called_count": 6,
            "top_level_orchestrator_llm_call_count": 1,
            "top_level_architect_llm_call_count": 1,
            "branch_local_llm_slm_call_count": 4,
            "bsep_created_count": 1,
            "bsep_validated_count": 1,
            "architect_received_bsep_context_count": 1,
            "runtime_plangraph_compiled_count": 1,
            "fractal_branch_cells_created_count": 8,
            "branch_result_proposals_created_count": 8,
            "post_vv_validated_count": 1,
            "gt_lgt_advisory_review_count": 1,
            "root_final_boundary_evaluated_count": 1,
            "action_commit_packet_created_count": 0,
            "receipt_created_count": 0,
            "mock_payment_executed_count": 0,
            "real_payment_executed_count": 0,
            "shipment_released_count": 0,
            "real_world_effects_count": 0,
        },
        "post_vv_gt_root": {
            "supplier_b_final_status": "BLOCKED",
            "shipment_final_status": "HELD",
            "receipt_final_status": "EVIDENCE_ONLY",
            "root_remains_final_authority": True,
        },
    }


def _write_fixture_artifact_dir(tmp_path: Path, *, final_status: str = "PASS") -> Path:
    artifact_dir = tmp_path / "artifact_dir"
    artifact_dir.mkdir()
    _write_json(artifact_dir / "summary.json", _valid_summary(final_status))
    _write_json(
        artifact_dir / "secret_scan.json",
        {"passed": True, "matched_markers": [], "files_scanned": 9},
    )
    for file_name in VALIDATION_FILES:
        _write_json(artifact_dir / file_name, {"accepted": True, "errors": []})
    return artifact_dir


def _rendered_from_fixture(tmp_path: Path) -> str:
    artifact_dir = _write_fixture_artifact_dir(tmp_path)
    report = runner.collect_human_full_wow_v1_2_live_fractal_story(artifact_dir=artifact_dir)
    return runner.render_human_full_wow_v1_2_live_fractal_story(report)


def test_story_renderer_default_skipped_closed() -> None:
    report = runner.collect_human_full_wow_v1_2_live_fractal_story(env={})

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["story_status"] == "SKIPPED_CLOSED"
    assert report["skip_reason"] == "artifact_dir_not_provided"
    assert report["provider_called_count"] == 0
    assert report["network_called_by_renderer_count"] == 0
    assert report["gemini_called_by_renderer_count"] == 0
    assert report["counters"]["real_world_effects_count"] == 0


def test_story_renderer_pass_from_fixture_artifact_dir(tmp_path: Path) -> None:
    artifact_dir = _write_fixture_artifact_dir(tmp_path)
    report = runner.collect_human_full_wow_v1_2_live_fractal_story(artifact_dir=artifact_dir)

    assert report["final_status"] == "PASS"
    assert report["story_status"] == "PASS"
    assert report["provider_mode"] == "real_provider"
    assert report["source_artifact_dir"] == str(artifact_dir)
    assert report["counters"]["semantic_actor_call_count"] == 6
    assert report["counters"]["bsep_created_count"] == 1
    assert report["counters"]["root_final_boundary_evaluated_count"] == 1
    assert report["counters"]["real_world_effects_count"] == 0


def test_story_renderer_required_sections(tmp_path: Path) -> None:
    rendered = _rendered_from_fixture(tmp_path)

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "FINAL STATUS: PASS" in rendered


def test_story_renderer_human_semantics_visible(tmp_path: Path) -> None:
    rendered = _rendered_from_fixture(tmp_path)

    for marker in (
        "Six semantic actors",
        "Orchestrator understood the business route",
        "BSEP was created after Orchestrator validation",
        "BSEP was validated before Architect",
        "Architect received BSEP-derived bounded context",
        "Runtime retained PlanGraph ownership",
        "Fractal branch cells",
        "Branch ResultProposals are not FinalOutput",
        "Root remained final authority",
    ):
        assert marker in rendered


def test_story_renderer_bank_secret_boundary(tmp_path: Path) -> None:
    rendered = _rendered_from_fixture(tmp_path)

    assert "payment_slot != permission" in rendered
    assert "receipt != truth" in rendered
    assert "receipt != shipment release" in rendered
    assert "raw bank secret/token/IBAN did not enter LLM context" in rendered
    for marker in SECRET_MARKERS:
        assert marker not in rendered


def test_story_renderer_missing_summary_fails_closed(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact_dir"
    artifact_dir.mkdir()

    report = runner.collect_human_full_wow_v1_2_live_fractal_story(artifact_dir=artifact_dir)

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["failure_reason"] == "missing_summary_json"
    for key in (
        "action_commit_packet_created_count",
        "receipt_created_count",
        "mock_payment_executed_count",
        "real_payment_executed_count",
        "shipment_released_count",
        "real_world_effects_count",
    ):
        assert report["counters"][key] == 0


def test_story_renderer_validation_failure_fails_closed(tmp_path: Path) -> None:
    artifact_dir = _write_fixture_artifact_dir(tmp_path)
    _write_json(
        artifact_dir / "branch_legal_validation.json",
        {"accepted": False, "errors": ["safe fixture validation failure"]},
    )

    report = runner.collect_human_full_wow_v1_2_live_fractal_story(artifact_dir=artifact_dir)
    rendered = runner.render_human_full_wow_v1_2_live_fractal_story(report)

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["failure_reason"] == "validation_artifact_not_accepted"
    assert "Safe validation failure section" in rendered
    assert "branch_legal_validation.json: accepted_not_true" in rendered
    assert "raw provider response" not in rendered


def test_story_renderer_does_not_import_or_call_provider() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "google.genai" not in source
    assert "run_full_wow_v1_2_manual_live_multillm_fractal_trace" not in source
    assert "run_full_semantic_e2e_v01" not in source
    assert "_raw_response.txt" not in source
    assert "artifact_files_observed_only" in source


def test_story_renderer_forbidden_overclaims(tmp_path: Path) -> None:
    rendered = _rendered_from_fixture(tmp_path)

    for left, right in FORBIDDEN_PHRASE_PARTS:
        assert left + right not in rendered
