from __future__ import annotations

from demo.run_long_lived_drs_ttl_aging_stress_v01 import (
    SCENARIO_IDS,
    run_all_scenarios,
)


def _report():
    return run_all_scenarios()


def _scenario(scenario_id: str):
    return _report()["scenario_results_by_id"][scenario_id]


def test_run_all_scenarios_returns_structured_pass_report():
    report = _report()
    counters = report["aggregate_counters"]
    assert report["status"] == "PASS"
    assert counters["scenarios_total"] == 25
    assert counters["scenarios_passed"] == counters["scenarios_total"]
    assert set(report["scenario_results_by_id"]) == set(SCENARIO_IDS)
    assert all(row["status"] == "PASS" for row in report["scenarios"])


def test_required_zero_risk_counters_remain_zero():
    counters = _report()["aggregate_counters"]
    assert counters["root_final_authority_preserved_count"] == counters["scenarios_total"]
    assert counters["unbounded_graph_traversal_used_count"] == 0
    assert counters["reuse_boost_hard_gate_overrides_count"] == 0
    assert counters["unaccepted_supersession_count"] == 0
    assert counters["accepted_evidence_action_permission_count"] == 0
    assert counters["production_drs_used_count"] == 0
    assert counters["external_drs_used_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["marennya_activated_count"] == 0
    assert counters["up_activated_count"] == 0


def test_missing_time_envelope_rejected_blocks_direct_reuse():
    row = _scenario("missing_time_envelope_rejected")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_time_gate"
    assert row["actual_reuse_decision_class"] == "blocked"
    assert "missing_time_envelope" in row["reason_codes"]


def test_drs_query_without_temporal_query_rejected_blocks_direct_reuse():
    row = _scenario("drs_query_without_temporal_query_rejected")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_time_gate"
    assert row["actual_reuse_decision_class"] == "blocked"
    assert "missing_temporal_query" in row["reason_codes"]


def test_expired_time_envelope_blocks_direct_reuse():
    row = _scenario("expired_time_envelope_blocks_direct_reuse")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_time_gate"
    assert "expired_ttl" in row["reason_codes"]


def test_fresh_ingestion_old_source_observed_at_blocks_freshness():
    row = _scenario("fresh_ingestion_old_source_observed_at_blocks_freshness")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_time_gate"
    assert "fresh_ingestion_old_source" in row["reason_codes"]


def test_historical_as_of_selects_old_record_as_historical_replay():
    row = _scenario("historical_as_of_selects_old_record")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_reuse_decision_class"] == "historical_replay"
    assert "historical_as_of" in row["reason_codes"]


def test_quarantine_proximity_blocks_reuse():
    row = _scenario("quarantine_proximity_blocks_reuse")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_quarantine_proximity"
    assert row["actual_reuse_decision_class"] == "blocked"
    assert "quarantine_proximity" in row["reason_codes"]


def test_deadend_proximity_blocks_route_and_direct_reuse():
    row = _scenario("deadend_proximity_blocks_route")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_deadend_proximity"
    assert row["actual_reuse_decision_class"] == "blocked"
    assert "deadend_proximity" in row["reason_codes"]


def test_reuse_frequency_cannot_override_staleness():
    row = _scenario("reuse_frequency_cannot_override_staleness")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_reuse_decision_class"] == "context_only"
    assert "reuse_frequency_not_authority" in row["reason_codes"]


def test_accepted_evidence_not_future_action_permission():
    row = _scenario("accepted_evidence_not_future_action_permission")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "rerun_required"
    assert row["actual_reuse_decision_class"] == "partial_reuse_then_validation"
    assert "accepted_evidence_not_action_permission" in row["reason_codes"]


def test_root_shortcut_required_for_any_direct_final_reuse():
    candidate = _scenario("fresh_record_direct_reuse_candidate_but_root_required")
    approved = _scenario("root_shortcut_required_for_any_direct_final_reuse")
    assert candidate["actual_direct_reuse_allowed"] is False
    assert "root_shortcut_required" in candidate["reason_codes"]
    assert approved["actual_direct_reuse_allowed"] is True
    assert approved["actual_reuse_decision_class"] == "direct_final_reuse"
    assert "root_shortcut_required" in approved["reason_codes"]


def test_supersession_requires_root_accepted_trustworthy_new_record():
    row = _scenario("supersession_requires_root_accepted_trustworthy_new_record")
    counters = _report()["aggregate_counters"]
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_reuse_decision_class"] == "warning_only"
    assert "supersession_requires_root_accepted_trustworthy_new_record" in row["reason_codes"]
    assert counters["unaccepted_supersession_count"] == 0


def test_fresh_unaccepted_observation_cannot_supersede_work():
    row = _scenario("fresh_unaccepted_observation_cannot_supersede_work")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_reuse_decision_class"] == "warning_only"
    assert "fresh_unaccepted_observation_cannot_supersede_work" in row["reason_codes"]


def test_quarantine_proximity_computation_is_bounded():
    row = _scenario("quarantine_proximity_computation_is_bounded")
    counters = _report()["aggregate_counters"]
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_quarantine_proximity"
    assert "bounded_proximity" in row["reason_codes"]
    assert counters["unbounded_graph_traversal_used_count"] == 0


def test_quarantine_taint_does_not_cascade_to_whole_graph():
    row = _scenario("quarantine_taint_does_not_cascade_to_whole_graph")
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_quarantine_proximity"
    assert "bounded_taint" in row["reason_codes"]


def test_reuse_boost_cannot_override_hard_gates():
    row = _scenario("reuse_boost_cannot_override_hard_gates")
    counters = _report()["aggregate_counters"]
    assert row["actual_direct_reuse_allowed"] is False
    assert row["actual_query_state"] == "blocked_by_time_gate"
    assert "reuse_boost_cannot_override_hard_gates" in row["reason_codes"]
    assert counters["reuse_boost_hard_gate_overrides_count"] == 0


def test_no_production_or_external_capabilities_are_used():
    limitations = _report()["limitations"]
    assert limitations["production_drs_used"] is False
    assert limitations["external_drs_used"] is False
    assert limitations["real_connector_used"] is False
    assert limitations["network_used"] is False
    assert limitations["gemini_used"] is False
    assert limitations["marennya_activated"] is False
    assert limitations["up_activated"] is False
    assert limitations["schemas_modified"] is False
    assert limitations["runtime_modified"] is False


def test_compact_rule_and_root_authority_are_reported():
    report = _report()
    compact_rule = report["compact_rule"]
    assert "Memory may survive." in compact_rule
    assert "Authority does not survive through memory." in compact_rule
    assert "Root remains final authority." in compact_rule
    assert report["authority_preservation_summary"]["root_remains_final_authority"] is True
