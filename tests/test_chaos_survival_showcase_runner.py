from __future__ import annotations

from demo.run_chaos_survival_showcase import collect_chaos_survival_showcase
from demo.run_chaos_survival_showcase import run_chaos_survival_showcase


def test_chaos_survival_showcase_prints_required_sections() -> None:
    output = run_chaos_survival_showcase()

    assert "[CHAOS SURVIVAL SHOWCASE]" in output
    assert "[INPUT MODULES]" in output
    assert "[NEEDLE FAILURE SURVIVAL]" in output
    assert "[DRS ROUTING SURVIVAL]" in output
    assert "[LARGE GRAPH SURVIVAL]" in output
    assert "[DRS LINEAGE SURVIVAL]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_chaos_survival_showcase_represents_all_input_modules() -> None:
    output = run_chaos_survival_showcase()

    assert "needle_runtime_chaos_available: true" in output
    assert "canonical_needle_outcome_trace_available: true" in output
    assert "needle_outcome_drs_routing_available: true" in output
    assert "large_graph_stress_available: true" in output
    assert "drs_graph_proximity_available: true" in output
    assert "modules_composed: 5" in output


def test_needle_failure_survival_is_derived_from_existing_rows() -> None:
    report = collect_chaos_survival_showcase()
    needle = report.needle_failure_survival

    assert needle["scenarios"] == 8
    assert needle["timeout_contained"] is True
    assert needle["invalid_json_quarantined"] is True
    assert needle["schema_validation_failed_quarantined"] is True
    assert needle["unknown_exception_contained"] is True
    assert needle["permission_required_blocked_or_needs_user"] is True
    assert needle["circuit_breaker_blocked"] is True
    assert needle["contract_mismatch_blocked_or_deadend"] is True
    assert needle["success_accepted"] is True
    assert needle["gt_runtime_called_for_needle_outcomes"] is True
    assert needle["needle_created_final_output"] is False
    assert needle["direct_user_answers_from_needle"] == 0
    assert needle["no_unhandled_exceptions"] is True
    assert needle["no_real_external_actions"] is True


def test_drs_routing_survival_preserves_layer_and_reuse_safety() -> None:
    report = collect_chaos_survival_showcase()
    drs = report.drs_routing_survival

    assert drs["local_drs_only"] is True
    assert drs["work_records"] == 1
    assert drs["quarantine_records"] == 3
    assert drs["deadend_records"] == 4
    assert drs["bad_outcomes_written_to_successful_work"] == 0
    assert drs["direct_reuse_unsafe_candidates"] == 0
    assert drs["time_envelope_present_for_all"] is True
    assert drs["provenance_present_for_all"] is True
    assert drs["gt_metadata_present_for_all"] is True
    assert drs["sensitive_terms_absent_for_all"] is True
    assert drs["external_drs_network_implemented"] is False
    assert drs["global_drs_implemented"] is False


def test_large_graph_survival_reports_bounded_graph_behavior() -> None:
    report = collect_chaos_survival_showcase()
    large = report.large_graph_survival

    assert large["normal_graph_completed"] is True
    assert large["wide_graph_parallelism_limited"] is True
    assert large["deep_graph_depth_checked"] is True
    assert large["oversized_graph_blocked"] is True
    assert large["too_many_edges_graph_blocked"] is True
    assert large["cycle_graph_blocked"] is True
    assert large["unknown_dependency_graph_blocked"] is True
    assert large["child_boundary_snapshots_created"] is True
    assert large["gt_candidate_count_bounded"] is True
    assert large["raw_large_graph_not_sent_to_gt"] is True
    assert large["large_graph_gt_runtime_called"] is False
    assert large["large_graph_gt_boundary_mode"] == "bounded_summary_check"
    assert large["executor_created_final_output"] is False
    assert large["root_final_authority_preserved"] is True
    assert large["no_real_external_actions"] is True


def test_drs_lineage_survival_reports_read_only_policy_safe_ranking() -> None:
    report = collect_chaos_survival_showcase()
    lineage = report.drs_lineage_survival

    assert lineage["local_drs_only"] is True
    assert lineage["read_only_ranking_proof"] is True
    assert lineage["records_written"] == 7
    assert lineage["graph_distance_computed_at_query_time"] is True
    assert lineage["static_hops_stored_in_records"] is False
    assert lineage["graph_proximity_formula_applied"] is True
    assert lineage["lineage_affects_ranking"] is True
    assert lineage["graph_proximity_does_not_override_policy"] is True
    assert lineage["quarantine_not_reuse_eligible"] is True
    assert lineage["deadend_not_reuse_eligible"] is True
    assert lineage["direct_reuse_policy_unchanged"] is True
    assert lineage["external_drs_network_implemented"] is False
    assert lineage["global_drs_implemented"] is False


def test_authority_and_safety_summary_remains_bounded() -> None:
    report = collect_chaos_survival_showcase()
    authority = report.authority_safety
    summary = report.summary

    assert authority["root_final_authority_preserved"] is True
    assert authority["executor_created_final_output"] is False
    assert authority["gt_committed_final_output"] is False
    assert authority["needle_created_final_output"] is False
    assert authority["uncontrolled_delegation"] is False
    assert authority["no_real_external_actions"] is True
    assert authority["no_global_drs"] is True
    assert authority["no_external_drs_network"] is True
    assert authority["no_telegram_actions"] is True
    assert authority["no_live_gemini"] is True
    assert authority["no_direct_user_answer_from_needle"] is True

    assert summary["chaos_survival_showcase_status"] == "PASS"
    assert summary["root_authority_survived"] is True
    assert summary["unsafe_reuse_candidates"] == 0
    assert summary["bad_outcomes_written_to_work"] == 0
    assert summary["real_external_actions_executed"] == 0
    assert summary["unhandled_exceptions"] == 0
    assert summary["production_autonomy_claimed"] is False


def test_summary_pass_values_are_derived_from_section_predicates() -> None:
    report = collect_chaos_survival_showcase()
    needle = report.needle_failure_survival
    drs = report.drs_routing_survival
    large = report.large_graph_survival
    lineage = report.drs_lineage_survival
    authority = report.authority_safety
    summary = report.summary

    needle_pass = (
        needle["scenarios"] == 8
        and needle["timeout_contained"]
        and needle["invalid_json_quarantined"]
        and needle["schema_validation_failed_quarantined"]
        and needle["unknown_exception_contained"]
        and needle["permission_required_blocked_or_needs_user"]
        and needle["circuit_breaker_blocked"]
        and needle["contract_mismatch_blocked_or_deadend"]
        and needle["success_accepted"]
        and needle["gt_runtime_called_for_needle_outcomes"]
        and needle["needle_created_final_output"] is False
        and needle["direct_user_answers_from_needle"] == 0
        and needle["no_unhandled_exceptions"]
        and needle["no_real_external_actions"]
    )
    drs_pass = (
        drs["local_drs_only"]
        and drs["work_records"] == 1
        and drs["quarantine_records"] == 3
        and drs["deadend_records"] == 4
        and drs["bad_outcomes_written_to_successful_work"] == 0
        and drs["direct_reuse_unsafe_candidates"] == 0
        and drs["time_envelope_present_for_all"]
        and drs["provenance_present_for_all"]
        and drs["gt_metadata_present_for_all"]
        and drs["sensitive_terms_absent_for_all"]
        and drs["external_drs_network_implemented"] is False
        and drs["global_drs_implemented"] is False
    )
    large_pass = (
        large["normal_graph_completed"]
        and large["wide_graph_parallelism_limited"]
        and large["deep_graph_depth_checked"]
        and large["oversized_graph_blocked"]
        and large["too_many_edges_graph_blocked"]
        and large["cycle_graph_blocked"]
        and large["unknown_dependency_graph_blocked"]
        and large["child_boundary_snapshots_created"]
        and large["gt_candidate_count_bounded"]
        and large["raw_large_graph_not_sent_to_gt"]
        and large["large_graph_gt_runtime_called"] is False
        and large["large_graph_gt_boundary_mode"] == "bounded_summary_check"
        and large["executor_created_final_output"] is False
        and large["root_final_authority_preserved"]
        and large["no_real_external_actions"]
    )
    lineage_pass = (
        lineage["local_drs_only"]
        and lineage["read_only_ranking_proof"]
        and lineage["records_written"] == 7
        and lineage["graph_distance_computed_at_query_time"]
        and lineage["static_hops_stored_in_records"] is False
        and lineage["graph_proximity_formula_applied"]
        and lineage["lineage_affects_ranking"]
        and lineage["graph_proximity_does_not_override_policy"]
        and lineage["quarantine_not_reuse_eligible"]
        and lineage["deadend_not_reuse_eligible"]
        and lineage["direct_reuse_policy_unchanged"]
        and lineage["external_drs_network_implemented"] is False
        and lineage["global_drs_implemented"] is False
    )
    authority_pass = (
        authority["root_final_authority_preserved"]
        and authority["executor_created_final_output"] is False
        and authority["gt_committed_final_output"] is False
        and authority["needle_created_final_output"] is False
        and authority["uncontrolled_delegation"] is False
        and authority["no_real_external_actions"]
        and authority["no_global_drs"]
        and authority["no_external_drs_network"]
        and authority["no_telegram_actions"]
        and authority["no_live_gemini"]
        and authority["no_direct_user_answer_from_needle"]
    )

    assert summary["needle_failure_survival"] == ("PASS" if needle_pass else "FAIL")
    assert summary["drs_routing_survival"] == ("PASS" if drs_pass else "FAIL")
    assert summary["large_graph_survival"] == ("PASS" if large_pass else "FAIL")
    assert summary["drs_lineage_survival"] == ("PASS" if lineage_pass else "FAIL")
    assert summary["chaos_survival_showcase_status"] == (
        "PASS"
        if needle_pass and drs_pass and large_pass and lineage_pass and authority_pass
        else "FAIL"
    )


def test_summary_exception_and_external_action_counts_are_derived() -> None:
    report = collect_chaos_survival_showcase()

    assert report.summary["unhandled_exceptions"] == (
        0
        if report.needle_failure_survival["no_unhandled_exceptions"]
        else "detected"
    )
    assert report.summary["real_external_actions_executed"] == (
        0 if report.authority_safety["no_real_external_actions"] else "detected"
    )


def test_output_contains_required_semantic_lines() -> None:
    output = run_chaos_survival_showcase()

    assert "timeout_contained: true" in output
    assert "invalid_json_quarantined: true" in output
    assert "schema_validation_failed_quarantined: true" in output
    assert "unknown_exception_contained: true" in output
    assert "permission_required_blocked_or_needs_user: true" in output
    assert "circuit_breaker_blocked: true" in output
    assert "bad_outcomes_written_to_successful_work: 0" in output
    assert "direct_reuse_unsafe_candidates: 0" in output
    assert "oversized_graph_blocked: true" in output
    assert "cycle_graph_blocked: true" in output
    assert "unknown_dependency_graph_blocked: true" in output
    assert "graph_proximity_does_not_override_policy: true" in output
    assert "quarantine_not_reuse_eligible: true" in output
    assert "deadend_not_reuse_eligible: true" in output
    assert "no_real_external_actions: true" in output
    assert "no_global_drs: true" in output
    assert "no_external_drs_network: true" in output
    assert "no_live_gemini: true" in output
    assert "no_telegram_actions: true" in output
    assert "production_autonomy_claimed: false" in output


def test_output_has_no_sensitive_terms() -> None:
    output = run_chaos_survival_showcase().lower()

    forbidden = {
        "raw_user_text",
        "api_key",
        "token",
        "secret",
        "password",
        "private_key",
        "passport_number",
        "card_number",
        "cvv",
        "chain of thought",
    }
    for term in forbidden:
        assert term not in output
