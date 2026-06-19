from __future__ import annotations

from demo.run_drs_lineage_provenance_pressure_v01 import (
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
    return _report()["lineage_pressure_results_by_id"][scenario_id]


def test_run_all_scenarios_returns_structured_pass_report():
    report = _report()
    counters = report["aggregate_counters"]
    assert report["status"] == "PASS"
    assert counters["scenarios_total"] == 10
    assert counters["scenarios_passed"] == counters["scenarios_total"]
    assert set(report["scenario_results_by_id"]) == set(SCENARIO_IDS)
    assert set(report["lineage_pressure_results_by_id"]) == set(SCENARIO_IDS)
    assert all(row["status"] == "PASS" for row in report["scenarios"])


def test_required_authority_boundary_counters_remain_zero():
    counters = _report()["aggregate_counters"]
    assert counters["lineage_decides_count"] == 0
    assert counters["provenance_truth_claimed_count"] == 0
    assert counters["audit_hash_truth_claimed_count"] == 0
    assert counters["bridge_authority_transfer_count"] == 0
    assert counters["quarantine_global_taint_count"] == 0
    assert counters["deadend_global_taint_count"] == 0
    assert counters["conflictcheck_authority_count"] == 0
    assert counters["gt_authority_count"] == 0
    assert counters["root_final_authority_preserved_count"] == counters["scenarios_total"]
    assert counters["production_drs_used_count"] == 0
    assert counters["external_drs_used_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["marennya_activated_count"] == 0
    assert counters["up_activated_count"] == 0


def test_trace_derived_from_trace_informs_only():
    row = _scenario("trace_derived_from_trace_informs_only")
    pressure = _pressure("trace_derived_from_trace_informs_only")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "context_only"
    assert "lineage_informs_only" in row["reason_codes"]
    assert pressure["lineage_informs"] is True
    assert pressure["lineage_decides"] is False


def test_reuse_candidate_derived_from_old_accepted_evidence_requires_review():
    row = _scenario("reuse_candidate_derived_from_old_accepted_evidence_requires_review")
    pressure = _pressure("reuse_candidate_derived_from_old_accepted_evidence_requires_review")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "rerun_required"
    assert pressure["root_review_required"] is True
    assert "accepted_evidence_ancestry_not_action_permission" in row["reason_codes"]


def test_bridge_traversal_across_domain_informs_only():
    row = _scenario("bridge_traversal_across_domain_informs_only")
    pressure = _pressure("bridge_traversal_across_domain_informs_only")
    assert row["actual_direct_reuse_allowed"] is False
    assert pressure["bridge_transfers_authority"] is False
    assert "bridge_informs_only" in row["reason_codes"]


def test_quarantine_near_reuse_candidate_warns_or_blocks():
    row = _scenario("quarantine_near_reuse_candidate_warns_or_blocks")
    pressure = _pressure("quarantine_near_reuse_candidate_warns_or_blocks")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_quarantine_proximity"
    assert pressure["quarantine_global_taint"] is False
    assert "quarantine_proximity_bounded" in row["reason_codes"]


def test_deadend_near_reuse_candidate_warns_or_blocks():
    row = _scenario("deadend_near_reuse_candidate_warns_or_blocks")
    pressure = _pressure("deadend_near_reuse_candidate_warns_or_blocks")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_deadend_proximity"
    assert pressure["deadend_global_taint"] is False
    assert "deadend_proximity_bounded" in row["reason_codes"]


def test_conflicting_provenance_blocks_direct_reuse():
    row = _scenario("conflicting_provenance_blocks_direct_reuse")
    pressure = _pressure("conflicting_provenance_blocks_direct_reuse")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_conflicting_provenance"
    assert pressure["conflictcheck_advisory_only"] is True
    assert "conflictcheck_advisory_root_required" in row["reason_codes"]


def test_trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize():
    row = _scenario("trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "supersession_review_required"
    assert "supersession_review_required" in row["reason_codes"]


def test_audit_hash_continuity_does_not_create_truth():
    row = _scenario("audit_hash_continuity_does_not_create_truth")
    pressure = _pressure("audit_hash_continuity_does_not_create_truth")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "audit_continuity_only"
    assert pressure["audit_hash_truth_claimed"] is False
    assert "audit_hash_continuity_not_truth" in row["reason_codes"]


def test_high_reuse_lineage_does_not_create_authority():
    row = _scenario("high_reuse_lineage_does_not_create_authority")
    pressure = _pressure("high_reuse_lineage_does_not_create_authority")
    assert row["actual_direct_reuse_allowed"] is False
    assert pressure["lineage_decides"] is False
    assert "popularity_not_authority" in row["reason_codes"]


def test_root_final_authority_preserved_across_lineage_pressure():
    row = _scenario("root_final_authority_preserved_across_lineage_pressure")
    pressure = _pressure("root_final_authority_preserved_across_lineage_pressure")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["root_final_authority_preserved"] is True
    assert pressure["root_final_authority_preserved"] is True
    assert "root_final_authority_preserved" in row["reason_codes"]


def test_report_output_contains_compact_rule_and_sections():
    output = render_report()
    assert "HEDGEHOG OS — DRS LINEAGE / PROVENANCE PRESSURE v0.1" in output
    assert "lineage informs" in output
    assert "lineage does not decide" in output
    assert "provenance does not become truth" in output
    assert "audit/hash-chain proves continuity, not truth" in output
    assert "accepted evidence ancestry is not future action permission" in output
    assert "bridge traversal is not authority transfer" in output
    assert "quarantine/deadend proximity is bounded" in output
    assert "ConflictCheck remains advisory" in output
    assert "GT remains advisory" in output
    assert "Root remains final authority" in output
    assert "Scenario table:" in output
    assert "Aggregate counters:" in output
    assert "Authority boundary summary:" in output
    assert "Limitations:" in output
    assert "FINAL STATUS: PASS" in output


def test_main_exits_successfully(capsys):
    assert main() == 0
    captured = capsys.readouterr()
    assert "FINAL STATUS: PASS" in captured.out
