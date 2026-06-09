from __future__ import annotations

from demo.run_controlled_root_orchestrator_route_assembly import (
    SCENARIOS,
    collect_controlled_root_orchestrator_route_assembly,
    run_controlled_root_orchestrator_route_assembly,
)


def _report():
    return collect_controlled_root_orchestrator_route_assembly()


def _gates():
    return {row["scenario"]: row for row in _report().matrix_route_gate}


def _proposals():
    return {row["scenario"]: row for row in _report().route_assembly_proposals}


def test_runner_contains_required_sections_and_exact_authority_term():
    output = run_controlled_root_orchestrator_route_assembly()
    for heading in (
        "[CONTROLLED ROOT ORCHESTRATOR ROUTE ASSEMBLY]",
        "[INPUT / MODE]",
        "[ORCHESTRATOR BOUNDED AUTHORITY]",
        "[ROUTE ASSEMBLY PROPOSALS]",
        "[MATRIX GATE / ROUTE GATE]",
        "[AVF / HARDMASK]",
        "[DOWNSTREAM CANONICAL PATH]",
        "[MALICIOUS CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output
    assert "delegated bounded route-assembly authority" in output


def test_orchestrator_has_all_required_positive_route_assembly_capabilities():
    authority = _report().orchestrator_bounded_authority
    for key in (
        "orchestrator_has_bounded_delegated_authority",
        "orchestrator_can_normalize_intent",
        "orchestrator_can_propose_route",
        "orchestrator_can_propose_temporal_query",
        "orchestrator_can_request_drs_retrieval",
        "orchestrator_can_assemble_worldstate",
        "orchestrator_can_propose_candidate_vectors",
        "orchestrator_can_propose_guard_set",
        "orchestrator_can_propose_decomposition_mode",
        "orchestrator_can_propose_attractor_packet_draft",
        "orchestrator_can_recommend_ask_user_or_block",
        "orchestrator_can_recommend_escalation",
    ):
        assert authority[key] is True


def test_orchestrator_has_none_of_the_forbidden_authority():
    authority = _report().orchestrator_bounded_authority
    for key in (
        "orchestrator_is_root",
        "orchestrator_creates_final_output",
        "orchestrator_writes_drs",
        "orchestrator_executes_actions",
        "orchestrator_calls_needles_directly",
        "orchestrator_bypasses_matrix_gate",
        "orchestrator_bypasses_avf",
        "orchestrator_overrides_hardmask",
        "orchestrator_installs_needles",
        "orchestrator_promotes_protocol_candidate",
        "orchestrator_releases_quarantine",
        "orchestrator_mutates_conflict_reports",
        "orchestrator_decides_truth",
        "orchestrator_grants_authority",
    ):
        assert authority[key] is False


def test_all_required_scenario_proposals_are_bounded_and_complete():
    proposals = _proposals()
    assert set(proposals) == set(SCENARIOS)
    for row in proposals.values():
        assert row["proposal_id"]
        assert row["normalized_intent"]
        assert row["temporal_query_proposal_present"] is True
        assert row["worldstate_request_present"] is True
        assert row["drs_retrieval_request_present"] is True
        assert row["candidate_vector_proposal_present"] is True
        assert row["guard_set_proposal_present"] is True
        assert row["attractor_packet_draft_present"] is True
        assert row["proof_only"] is True


def test_root_validates_every_proposal_after_orchestrator():
    for row in _report().matrix_route_gate:
        assert row["root_validates_orchestrator_proposal"] is True
        assert row["matrix_gate_after_orchestrator"] is True
        assert row["route_gate_after_orchestrator"] is True
        assert row["policy_constraints_applied"] is True
        assert row["root_authority_preserved"] is True


def test_safe_warehouse_inventory_route_completes_through_allowed_gate():
    proposal = _proposals()["safe_warehouse_inventory_route"]
    gate = _gates()["safe_warehouse_inventory_route"]
    assert "warehouse" in proposal["normalized_intent"]
    assert gate["gate_status"] == "accepted"
    assert gate["proposal_allowed_to_avf"] is True


def test_forbidden_action_route_is_blocked_before_avf_without_action():
    gate = _gates()["forbidden_action_route_blocked"]
    assert gate["gate_status"] == "blocked"
    assert gate["unsafe_action_claim_blocked"] is True
    assert gate["proposal_allowed_to_avf"] is False
    assert _report().input_mode["real_external_action"] is False


def test_high_confidence_forbidden_vector_is_removed_by_independent_hardmask():
    gate = _gates()["hardmask_beats_orchestrator_confidence"]
    avf = _report().avf_hardmask
    assert gate["forbidden_vectors_blocked_before_avf"] is True
    assert gate["proposal_allowed_to_avf"] is True
    assert avf["orchestrator_manages_avf"] is False
    assert avf["avf_independent_filter_scoring_layer"] is True
    assert avf["hardmask_beats_orchestrator_confidence"] is True
    assert avf["softmask_applied_after_hardmask"] is True


def test_ask_user_preserves_needs_user_without_forced_execution():
    proposal = _proposals()["ask_user_recommendation"]
    gate = _gates()["ask_user_recommendation"]
    assert proposal["ask_user_recommendation"] is True
    assert gate["gate_status"] == "needs_user"
    assert gate["proposal_allowed_to_avf"] is False


def test_decomposition_route_can_reach_bounded_child_cell():
    proposal = _proposals()["decomposition_route_to_child_cell"]
    gate = _gates()["decomposition_route_to_child_cell"]
    downstream = _report().downstream_canonical_path
    assert proposal["decomposition_mode_proposal"] == "bounded_child_cell"
    assert gate["proposal_allowed_to_avf"] is True
    assert downstream["child_cell_bounded_if_used"] is True


def test_direct_needle_call_and_drs_write_attempts_are_rejected():
    gates = _gates()
    needle = gates["direct_needle_call_attempt_rejected"]
    drs = gates["drs_write_attempt_rejected"]
    assert needle["gate_status"] == "rejected"
    assert needle["direct_needle_call_rejected"] is True
    assert needle["proposal_allowed_to_avf"] is False
    assert drs["gate_status"] == "rejected"
    assert drs["orchestrator_drs_write_rejected"] is True
    assert drs["proposal_allowed_to_avf"] is False


def test_malicious_authority_scenario_and_all_claims_are_rejected():
    gate = _gates()["malicious_authority_claims_rejected"]
    malicious = _report().malicious_claims
    assert gate["gate_status"] == "rejected"
    assert gate["invalid_orchestrator_authority_claim_blocked"] is True
    assert gate["proposal_allowed_to_avf"] is False
    assert len(malicious) == 14
    assert all(malicious.values())


def test_orchestrator_proposes_avf_inputs_but_does_not_manage_avf():
    avf = _report().avf_hardmask
    assert avf["orchestrator_can_propose_candidate_vectors"] is True
    assert avf["orchestrator_can_propose_guard_set"] is True
    assert avf["orchestrator_can_propose_attractor_packet_draft"] is True
    assert avf["orchestrator_proposes_avf_inputs"] is True
    assert avf["orchestrator_manages_avf"] is False
    assert avf["avf_after_matrix_gate"] is True
    assert avf["final_attractor_packet_created_by_avf_or_root_controlled_avf_layer"] is True


def test_architect_receives_only_bounded_packet_and_executor_receives_plan_graph():
    avf = _report().avf_hardmask
    downstream = _report().downstream_canonical_path
    assert avf["architect_receives_bounded_attractor_packet"] is True
    assert avf["raw_orchestrator_proposal_not_sent_directly_to_architect"] is True
    assert downstream["architect_receives_bounded_attractor_packet"] is True
    assert downstream["architect_receives_raw_orchestrator_proposal"] is False
    assert downstream["architect_returns_plan_graph"] is True
    assert downstream["executor_receives_plan_graph_not_raw_user_text"] is True
    assert downstream["needleruntime_reached_only_through_root_approved_plan_graph"] is True


def test_existing_canonical_collectors_are_consumed_in_order():
    downstream = _report().downstream_canonical_path
    for key in (
        "matrix_gate_source_status",
        "avf_source_status",
        "architect_source_status",
        "dag_source_status",
        "post_vv_source_status",
        "gt_source_status",
        "root_final_source_status",
        "drs_lifecycle_source_status",
        "conflictcheck_source_status",
        "audit_hash_chain_source_status",
    ):
        assert downstream[key] == "PASS"
    assert downstream["post_vv_reached"] is True
    assert downstream["gt_reached"] is True
    assert downstream["root_final_still_required"] is True
    assert downstream["drs_lifecycle_after_root_final"] is True
    assert downstream["conflictcheck_after_drs_lifecycle"] is True
    assert downstream["audit_hash_chain_after_conflictcheck"] is True


def test_root_and_advisory_authority_boundaries_remain_intact():
    authority = _report().authority_safety
    assert authority["root_sovereign"] is True
    assert authority["root_remains_final_authority"] is True
    assert authority["avf_remains_independent"] is True
    assert authority["hardmask_remains_stronger_than_orchestrator_confidence"] is True
    assert authority["gt_remains_advisory_until_root"] is True
    assert authority["conflictcheck_remains_advisory_until_root"] is True
    assert authority["audit_hash_chain_proves_continuity_not_truth"] is True
    assert authority["production_autonomy_claimed"] is False


def test_no_network_telegram_persistence_actions_or_deferred_systems():
    mode = _report().input_mode
    assert mode == {
        "mode": "deterministic_controlled_root_orchestrator_route_assembly",
        "local_proof_level_only": True,
        "live_network_used": False,
        "telegram_used": False,
        "real_external_action": False,
        "production_persistence": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def test_summary_pass_derives_from_scenarios_sources_and_authority_facts():
    report = _report()
    summary = report.summary
    assert summary["controlled_root_orchestrator_route_assembly_status"] == "PASS"
    assert summary["scenarios_verified"] == len(SCENARIOS) == 8
    assert summary["orchestrator_has_bounded_delegated_authority"] is True
    assert summary["root_validates_orchestrator_proposal"] is True
    assert summary["matrix_gate_after_orchestrator"] is True
    assert summary["avf_after_matrix_gate"] is True
    assert summary["hardmask_beats_orchestrator_confidence"] is True
    assert summary["architect_receives_bounded_attractor_packet"] is True
    assert summary["executor_receives_plan_graph_not_raw_user_text"] is True
    assert summary["root_final_still_required"] is True
    assert summary["drs_lifecycle_after_root_final"] is True
    assert summary["conflictcheck_after_drs_lifecycle"] is True
    assert summary["audit_hash_chain_after_conflictcheck"] is True
    assert summary["malicious_claims_rejected"] == 14
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_controlled_root_orchestrator_docs_sync"] is True
    assert summary["production_autonomy_claimed"] is False
