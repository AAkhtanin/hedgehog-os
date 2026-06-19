from __future__ import annotations

from demo.run_compromised_upstream_pack_v01 import (
    SCENARIO_IDS,
    main,
    render_report,
    run_all_scenarios,
)


def _report():
    return run_all_scenarios()


def _scenario(scenario_id: str):
    return _report()["scenario_results_by_id"][scenario_id]


def _pressure(scenario_id: str):
    return _report()["upstream_pressure_results_by_id"][scenario_id]


def test_run_all_scenarios_returns_structured_pass_report():
    report = _report()
    counters = report["aggregate_counters"]
    assert report["status"] == "PASS"
    assert counters["scenarios_total"] == 6
    assert counters["scenarios_passed"] == counters["scenarios_total"]
    assert set(report["scenario_results_by_id"]) == set(SCENARIO_IDS)
    assert set(report["upstream_pressure_results_by_id"]) == set(SCENARIO_IDS)
    assert all(row["status"] == "PASS" for row in report["scenarios"])


def test_required_authority_boundary_counters_remain_zero():
    counters = _report()["aggregate_counters"]
    assert counters["direct_ready_allowed_count"] == 0
    assert counters["direct_reuse_allowed_count"] == 0
    assert counters["action_permission_granted_count"] == 0
    assert counters["source_truth_claimed_count"] == 0
    assert counters["schema_validity_truth_claimed_count"] == 0
    assert counters["signed_source_truth_claimed_count"] == 0
    assert counters["pointer_trust_claimed_count"] == 0
    assert counters["evidence_candidate_authority_claimed_count"] == 0
    assert counters["validation_packet_authority_claimed_count"] == 0
    assert counters["accepted_evidence_action_permission_claimed_count"] == 0
    assert counters["conflictcheck_authority_count"] == 0
    assert counters["gt_authority_count"] == 0
    assert counters["root_final_authority_preserved_count"] == counters["scenarios_total"]


def test_required_non_activation_counters_remain_zero():
    counters = _report()["aggregate_counters"]
    assert counters["production_connector_used_count"] == 0
    assert counters["production_drs_used_count"] == 0
    assert counters["external_drs_used_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["negative_trace_implemented_count"] == 0
    assert counters["auto_governance_implemented_count"] == 0
    assert counters["manifest_hardening_implemented_count"] == 0
    assert counters["transition_matrix_mutated_count"] == 0
    assert counters["marennya_activated_count"] == 0
    assert counters["up_activated_count"] == 0


def test_compromised_bank_source_cannot_create_truth():
    row = _scenario("compromised_bank_source_cannot_create_truth")
    pressure = _pressure("compromised_bank_source_cannot_create_truth")
    assert row["actual_query_state"] == "blocked_or_review_required"
    assert row["actual_final_status"] == "needs_root_review"
    assert row["actual_direct_ready_allowed"] is False
    assert pressure["source_truth_claimed"] is False
    assert pressure["schema_validity_truth_claimed"] is False
    assert "compromised_source_not_truth" in row["reason_codes"]


def test_stale_legal_source_signed_looking_forces_review():
    row = _scenario("stale_legal_source_signed_looking_forces_review")
    pressure = _pressure("stale_legal_source_signed_looking_forces_review")
    assert row["actual_query_state"] == "stale_source_review_required"
    assert row["actual_direct_ready_allowed"] is False
    assert pressure["signed_source_truth_claimed"] is False
    assert pressure["validation_packet_authority_claimed"] is False
    assert "stale_signed_source_requires_review" in row["reason_codes"]


def test_warehouse_source_contradiction_blocks_ready():
    row = _scenario("warehouse_source_contradiction_blocks_ready")
    pressure = _pressure("warehouse_source_contradiction_blocks_ready")
    assert row["actual_final_status"] == "not_ready"
    assert row["actual_direct_ready_allowed"] is False
    assert pressure["conflictcheck_advisory_only"] is True
    assert "conflict_detected" in row["reason_codes"]
    assert "conflicting_warehouse_provenance_blocks_ready" in row["reason_codes"]


def test_external_pointer_trust_laundering_rejected():
    row = _scenario("external_pointer_trust_laundering_rejected")
    pressure = _pressure("external_pointer_trust_laundering_rejected")
    assert row["actual_final_status"] == "blocked"
    assert pressure["pointer_trust_claimed"] is False
    assert pressure["external_drs_used"] is False
    assert pressure["production_drs_used"] is False
    assert "external_pointer_trust_laundering_rejected" in row["reason_codes"]


def test_accepted_evidence_from_compromised_source_is_not_action_permission():
    row = _scenario("accepted_evidence_from_compromised_source_is_not_action_permission")
    pressure = _pressure("accepted_evidence_from_compromised_source_is_not_action_permission")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_action_permission_granted"] is False
    assert pressure["evidence_candidate_authority_claimed"] is False
    assert pressure["accepted_evidence_action_permission_claimed"] is False
    assert "accepted_evidence_not_action_permission" in row["reason_codes"]


def test_root_final_authority_preserved_under_compromised_upstream_pressure():
    row = _scenario("root_final_authority_preserved_under_compromised_upstream_pressure")
    pressure = _pressure("root_final_authority_preserved_under_compromised_upstream_pressure")
    assert row["actual_direct_ready_allowed"] is False
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_action_permission_granted"] is False
    assert row["root_final_authority_preserved"] is True
    assert pressure["root_final_authority_preserved"] is True
    assert pressure["production_connector_used"] is False
    assert pressure["network_used"] is False
    assert "root_final_authority_preserved_under_compromised_upstream_pressure" in row["reason_codes"]


def test_report_output_contains_compact_rule_counters_and_sections():
    output = render_report()
    assert "HEDGEHOG OS — COMPROMISED UPSTREAM PACK v0.1" in output
    assert "compromised upstream source is not truth" in output
    assert "signed-looking source is not truth" in output
    assert "external pointer is not trust" in output
    assert "schema-valid upstream content is not semantic truth" in output
    assert "ValidationPacket is not Root acceptance" in output
    assert "EvidenceCandidate is candidate-only before Root" in output
    assert "AcceptedEvidence is bounded evidence, not future action permission" in output
    assert "ConflictCheck remains advisory" in output
    assert "GT remains advisory" in output
    assert "Root remains final authority" in output
    assert "Scenario table:" in output
    assert "Aggregate counters:" in output
    assert "direct_ready_allowed_count: 0" in output
    assert "source_truth_claimed_count: 0" in output
    assert "root_final_authority_preserved_count: 6" in output
    assert "Authority boundary summary:" in output
    assert "Limitations:" in output
    assert "FINAL STATUS: PASS" in output


def test_main_exits_successfully(capsys):
    assert main() == 0
    captured = capsys.readouterr()
    assert "FINAL STATUS: PASS" in captured.out
