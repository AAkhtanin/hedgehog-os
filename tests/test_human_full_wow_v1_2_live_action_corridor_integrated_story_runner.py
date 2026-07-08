from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from demo import run_human_full_wow_v1_2_live_action_corridor_integrated_story as runner


REAL_ARTIFACT_DIR = (
    ".tmp/full_wow_v1_2_manual_live_multillm_fractal_action_corridor/"
    "full_wow_v1_2_manual_live_multillm_fractal_action_corridor_real_20260708_180020"
)

REQUIRED_SECTIONS = (
    "[HEDGEHOG OS — FULL WOW V1.2 LIVE ACTION CORRIDOR INTEGRATED STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF REAL SEMANTIC ACTORS]",
    "[TIMELINE FROM REQUEST TO RECEIPT EVIDENCE]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF HARD-MASKED AND RANKED]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP CARRIED]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH ACTORS RETURNED]",
    "[WHAT ROOT DID]",
    "[ACTIONCOMMITPACKET BOUNDARY]",
    "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
    "[MOCK RECEIPT BOUNDARY]",
    "[SUPPLIER B AND SHIPMENT SAFETY]",
    "[BANK A VS BANK B POSITIONING]",
    "[WHY THIS IS READY FOR FUTURE CRYPTOGRAPHY]",
    "[ARTIFACT EVIDENCE MAP]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

ROLES = (
    "top_level_orchestrator_llm",
    "top_level_semantic_architect_llm",
    "legal_clause_semantic_extractor",
    "accounting_mismatch_semantic_explainer",
    "supplier_b_unstructured_note_interpreter",
    "bank_policy_semantic_reviewer",
)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _counters() -> dict[str, int]:
    counters = {key: 0 for key in runner.COUNTER_KEYS}
    counters.update(
        {
            "semantic_actor_call_count": 6,
            "real_provider_call_count": 6,
            "gemini_called_count": 6,
            "network_used_count": 6,
            "local_drs_v0_2_records_evaluated_count": 11,
            "local_drs_v0_2_direct_reuse_allowed_count": 0,
            "local_drs_v0_2_root_review_required_count": 11,
            "avf_v0_2_candidates_evaluated_count": 9,
            "action_commit_packet_v0_2_root_created_model_packet_count": 1,
            "action_commit_packet_v0_2_created_by_root_count": 1,
            "mock_bank_sandbox_v0_2_corridor_invoked_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_intent_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_consent_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_payment_order_created_count": 1,
            "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count": 1,
            "mock_bank_sandbox_v0_2_terminal_receipt_observed_count": 1,
        }
    )
    counters["mock_bank_sandbox_v0_2_provider_called_count"] = 0
    counters["mock_bank_sandbox_v0_2_network_called_count"] = 0
    counters["mock_bank_sandbox_v0_2_gemini_called_count"] = 0
    return counters


def _summary() -> dict[str, Any]:
    return {
        "final_status": "PASS",
        "stage_status": "PASS",
        "provider_mode": "real_provider",
        "model": "gemini-2.5-flash",
        "counters": _counters(),
        "semantic_actor_calls": tuple(
            {
                "role": role,
                "provider_mode": "real_provider",
                "validation_status": "PASS",
            }
            for role in ROLES
        ),
        "action_commit_packet_v0_2_integration": {
            "status": "PASS",
            "packet_id": "acp_v02:supplier_a_mock_payment:inv_2042",
            "allowed_subjects": ("supplier_a_adriatic_filters",),
        },
        "mock_bank_sandbox_v0_2_corridor_execution": {
            "status": "PASS",
            "source_packet_id": "acp_v02:supplier_a_mock_payment:inv_2042",
        },
    }


def _validation(proposal_id: str) -> dict[str, Any]:
    return {
        "accepted": True,
        "canonical": {
            "proposal_id": proposal_id,
            "suggested_route": "supplier_payment_shipment_review_v1_2",
            "evidence_needed": (
                "warehouse inventory",
                "supplier availability and blockers",
            ),
            "required_guards": (
                "BSEP validation",
                "Root final authority",
            ),
            "result_proposal_summary": (
                "Supplier A may proceed only to scoped review. Supplier B remains blocked."
            ),
            "semantic_summary": "Branch semantic observation remains advisory.",
        },
        "errors": [],
    }


def _fixture_dir(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    for file_name in runner.REQUIRED_JSON_FILES:
        _write_json(artifact_dir / file_name, {})

    _write_json(artifact_dir / "summary.json", _summary())
    _write_json(
        artifact_dir / "secret_scan.json",
        {"files_scanned": 47, "matched_markers": [], "passed": True},
    )
    _write_json(
        artifact_dir / "local_drs_v0_2_resolve_report.json",
        {
            "records_evaluated_count": 11,
            "direct_reuse_allowed_count": 0,
            "root_review_required_count": 11,
        },
    )
    _write_json(
        artifact_dir / "avf_v0_2_evaluation_report.json",
        {
            "candidates_evaluated_count": 9,
            "top_candidate_id": "block_supplier_b_and_hold_shipment",
        },
    )
    _write_json(
        artifact_dir / "top_level_orchestrator_validation.json",
        _validation("orchestrator-semantic-wow-v1-2-001"),
    )
    _write_json(
        artifact_dir / "top_level_architect_validation.json",
        _validation("architect-semantic-wow-v1-2-001"),
    )
    for file_name in (
        "branch_legal_validation.json",
        "branch_accounting_validation.json",
        "branch_supplier_b_validation.json",
        "branch_bank_policy_validation.json",
    ):
        _write_json(artifact_dir / file_name, _validation(file_name))
    (artifact_dir / "top_level_orchestrator_raw_response.txt").write_text(
        "raw_response text should stay hidden",
        encoding="utf-8",
    )
    return artifact_dir


def _collect(artifact_dir: Path) -> dict[str, Any]:
    return runner.collect_human_full_wow_v1_2_live_action_corridor_integrated_story(
        env={runner.ARTIFACT_DIR_ENV: str(artifact_dir)}
    )


def _render(artifact_dir: Path) -> str:
    return runner.render_human_full_wow_v1_2_live_action_corridor_integrated_story(
        _collect(artifact_dir)
    )


def test_live_action_corridor_story_default_skipped_closed() -> None:
    report = runner.collect_human_full_wow_v1_2_live_action_corridor_integrated_story(
        env={}
    )

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["story_status"] == "SKIPPED_CLOSED"
    assert "artifact_dir_missing" in report["validation_errors"]


def test_live_action_corridor_story_real_artifact_pass_if_present() -> None:
    artifact_dir = Path(REAL_ARTIFACT_DIR)
    if not artifact_dir.exists():
        pytest.skip("real PASS artifact directory is not present")

    report = _collect(artifact_dir)
    rendered = runner.render_human_full_wow_v1_2_live_action_corridor_integrated_story(
        report
    )

    assert report["final_status"] == "PASS"
    for section in REQUIRED_SECTIONS:
        assert section in rendered


def test_live_action_corridor_story_required_sections(tmp_path: Path) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    for section in REQUIRED_SECTIONS:
        assert section in rendered


def test_live_action_corridor_story_semantic_actors(tmp_path: Path) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    for role in ROLES:
        assert role in rendered
    assert "real_provider" in rendered
    assert "advisory semantic evidence only" in rendered


def test_live_action_corridor_story_drs_avf_root_packet_corridor(
    tmp_path: Path,
) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    assert "DRS is not truth/authority/permission/FinalOutput" in rendered
    assert "AVF score is not authority" in rendered
    assert "Root created one scoped Supplier A ActionCommitPacket model" in rendered
    assert "MockBankSandbox consumed validated Root-created Supplier A packet" in rendered
    assert "Receipt is evidence only" in rendered


def test_live_action_corridor_story_supplier_b_and_shipment_safety(
    tmp_path: Path,
) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    assert "Supplier B remained blocked" in rendered
    assert "Shipment remained held" in rendered
    assert "does not leak permission to Supplier B" in rendered
    assert "does not release SH-2042" in rendered


def test_live_action_corridor_story_crypto_readiness_not_crypto_claim(
    tmp_path: Path,
) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    assert "future crypto-ready only in the limited artifact-set sense" in rendered
    assert "Current run is not cryptographically sealed" in rendered
    assert "No cryptographic proof layer is claimed here" in rendered


def test_live_action_corridor_story_fail_closed_on_effect_counter(
    tmp_path: Path,
) -> None:
    artifact_dir = _fixture_dir(tmp_path)
    summary = _summary()
    summary["counters"]["real_world_effects_count"] = 1
    _write_json(artifact_dir / "summary.json", summary)

    report = _collect(artifact_dir)

    assert report["final_status"] == "FAIL_CLOSED"
    assert "real_world_effects_zero" in report["validation_errors"]


def test_live_action_corridor_story_fail_closed_on_missing_secret_scan(
    tmp_path: Path,
) -> None:
    artifact_dir = _fixture_dir(tmp_path)
    _write_json(
        artifact_dir / "secret_scan.json",
        {"files_scanned": 47, "matched_markers": ["sandbox_token_abc"], "passed": False},
    )

    report = _collect(artifact_dir)

    assert report["final_status"] == "FAIL_CLOSED"
    assert "secret_scan_passed" in report["validation_errors"]


def test_live_action_corridor_story_no_raw_response_output_by_default(
    tmp_path: Path,
) -> None:
    rendered = _render(_fixture_dir(tmp_path))

    assert "raw_response text should stay hidden" not in rendered
    assert "top_level_orchestrator_raw_response.txt" not in rendered


def test_live_action_corridor_story_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")
    forbidden_phrases = (
        "authority " + "flows upward",
        "adapter " + "returns authority",
        "receipt " + "returns authority",
        "bank " + "returns authority",
        "corridor " + "decides",
        "adapter " + "decides",
        "post-Root " + "reasoning restarts",
        "receipt " + "grants permission",
        "receipt " + "releases shipment",
        "human approval " + "directly creates ActionCommitPacket",
    )

    assert "google.genai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "openai" not in source
    assert "subprocess" not in source
    assert "hedgehog.mock_connector_sandbox" not in source
    assert "from hedgehog.action_commit_packet import" not in source
    assert "generate_content" not in source
    for phrase in forbidden_phrases:
        assert phrase not in source
