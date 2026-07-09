from __future__ import annotations

from pathlib import Path

from demo import run_non_action_direct_reuse_positive_control_v01 as runner
from hedgehog import non_action_reuse_positive_control as reuse


REQUIRED_COUNTERS = {
    "scenarios_total": 6,
    "scenarios_passed": 6,
    "direct_reuse_allowed_count": 1,
    "non_action_direct_reuse_allowed_count": 1,
    "root_shortcut_allowed_count": 1,
    "root_final_from_reuse_created_count": 1,
    "architect_skipped_for_safe_informational_reuse_count": 1,
    "executor_skipped_for_safe_informational_reuse_count": 1,
    "heavy_pipeline_skipped_count": 1,
    "payment_direct_reuse_allowed_count": 0,
    "shipment_direct_reuse_allowed_count": 0,
    "ticket_purchase_direct_reuse_allowed_count": 0,
    "action_permission_granted_count": 0,
    "action_commit_packet_created_count": 0,
    "receipt_created_count": 0,
    "payment_executed_count": 0,
    "shipment_released_count": 0,
    "ticket_issued_count": 0,
    "avf_score_used_as_authority_count": 0,
    "drs_hit_used_as_authority_count": 0,
    "reuse_gate_used_as_root_count": 0,
    "root_bypass_count": 0,
    "provider_called_count": 0,
    "network_used_count": 0,
    "gemini_called_count": 0,
    "real_world_effects_count": 0,
    "root_final_authority_preserved_count": 6,
}


def _report() -> dict[str, object]:
    return runner.collect_non_action_direct_reuse_positive_control_v01()


def _scenario(report: dict[str, object], candidate_class: str) -> dict[str, object]:
    for row in report["scenario_table"]:
        if row["candidate_class"] == candidate_class:
            return row
    raise AssertionError(f"missing scenario row: {candidate_class}")


def test_runner_collects_pass_report() -> None:
    report = _report()

    assert report["final_status"] == reuse.STATUS_PASS
    assert report["model_report"]["final_status"] == reuse.STATUS_PASS
    assert report["model_report"]["scenarios_total"] == 6
    assert report["model_report"]["scenarios_passed"] == 6
    assert report["validation_errors"] == ()


def test_runner_positive_informational_reuse_story() -> None:
    report = _report()
    positive = report["positive_control"]
    artifacts = report["informational_artifacts"]

    assert positive["direct_reuse_allowed"] is True
    assert positive["root_shortcut_allowed"] is True
    assert positive["root_final_from_reuse_created"] is True
    assert len(artifacts) == 1
    artifact = artifacts[0]
    assert artifact["created_by"] == "root"
    assert artifact["root_created"] is True
    assert artifact["action_permission_granted"] is False
    assert artifact["payment_permission_created"] is False
    assert artifact["shipment_permission_created"] is False
    assert artifact["ticket_permission_created"] is False
    assert artifact["receipt_created"] is False
    assert artifact["real_world_effects_count"] == 0


def test_runner_negative_action_like_controls() -> None:
    report = _report()
    negative = report["negative_controls"]

    assert negative["payment_direct_reuse_allowed"] is False
    assert negative["shipment_direct_reuse_allowed"] is False
    assert negative["ticket_purchase_direct_reuse_allowed"] is False
    assert negative["action_permission_granted"] is False
    assert negative["action_commit_packet_created"] is False
    assert negative["receipt_created"] is False
    assert negative["real_world_effects_count"] == 0


def test_runner_scenario_table_contains_required_scenarios() -> None:
    report = _report()
    rows = report["scenario_table"]
    candidate_classes = {row["candidate_class"] for row in rows}

    assert len(rows) == 6
    assert candidate_classes == set(runner.REQUIRED_SCENARIOS)
    stale = _scenario(report, reuse.CANDIDATE_STALE_POLICY_SUMMARY_CONTEXT_ONLY)
    high_score = _scenario(report, reuse.CANDIDATE_HIGH_SCORE_WITHOUT_ROOT_SHORTCUT)
    assert stale["decision_class"] == reuse.DECISION_CONTEXT_ONLY
    assert high_score["decision_class"] == reuse.DECISION_BLOCKED
    assert high_score["root_shortcut_allowed"] is False


def test_runner_counters_match_required_shape() -> None:
    report = _report()
    counters = report["counters"]

    for key, expected in REQUIRED_COUNTERS.items():
        assert counters[key] == expected


def test_renderer_contains_required_sections_and_human_meaning() -> None:
    rendered = runner.render_non_action_direct_reuse_positive_control_v01(_report())
    required_sections = (
        "[NON-ACTION DIRECT REUSE POSITIVE CONTROL V0.1]",
        "[WHAT THIS PROVES]",
        "[POSITIVE INFORMATIONAL REUSE]",
        "[NEGATIVE ACTION-LIKE REUSE CONTROLS]",
        "[ROOT SHORTCUT GATE]",
        "[SCENARIO TABLE]",
        "[COUNTER TABLE]",
        "[AUTHORITY BOUNDARIES]",
        "[NON-CLAIMS]",
        "[NEXT GATE]",
        "[FINAL STATUS]",
    )

    for section in required_sections:
        assert section in rendered
    assert "Hedgehog OS can reuse memory to answer a safe informational question" in rendered
    assert "Direct reuse saves compute; it does not transfer authority." in rendered
    assert "Root remains final authority" in rendered


def test_runner_no_provider_network_gemini_or_effects() -> None:
    report = _report()
    counters = report["counters"]

    assert counters["provider_called_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["ticket_issued_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_runner_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text()

    assert "non_action_reuse_positive_control" in source
    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "import hedgehog.action_commit_packet" not in source
    assert "from hedgehog.action_commit_packet" not in source
    assert "import hedgehog.mock_connector_sandbox" not in source
    assert "from hedgehog.mock_connector_sandbox" not in source
    assert "run_full_wow" not in source
    assert "manual_live" not in source
    for left, right in (
        ("direct reuse grants", " permission"),
        ("DRS", " decides"),
        ("reuse score is", " authority"),
        ("semantic similarity is", " authority"),
        ("old receipt grants", " permission"),
        ("old quote grants", " ticket"),
        ("receipt grants", " permission"),
        ("ticket receipt grants", " permission"),
        ("ActionCommitPacket created", " by reuse"),
    ):
        assert left + right not in source


def test_audit_log_exists_and_records_pass() -> None:
    audit = Path(
        "docs/audit_reports/auditor_non_action_direct_reuse_positive_control_v01.log",
    ).read_text()

    assert "audit_status: PASS" in audit
    assert "finding_runner_final_status_pass: PASS" in audit
    assert "finding_airline_not_started: PASS" in audit
