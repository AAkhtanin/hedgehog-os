from __future__ import annotations

from pathlib import Path

from demo import run_full_wow_v1_2_product_trace as runner


REQUIRED_MODULE_IDS = {
    "warehouse_api_sandbox",
    "supplier_a_api_sandbox",
    "supplier_b_api_sandbox",
    "legal_module",
    "accounting_module",
    "bank_a_legacy_sandbox",
    "bank_b_hedgehog_native_preview",
}

REQUIRED_STEP_IDS = {
    "dirty_request_received",
    "warehouse_inventory_query",
    "supplier_a_availability_query",
    "supplier_b_blocker_query",
    "legal_insurance_contract_check",
    "accounting_invoice_po_reconciliation",
    "bank_a_payment_slot_prepared",
    "bank_b_native_contract_preview",
    "top_level_semantic_route_observed_from_v1_1",
    "bsep_membrane_observed_from_v1_1",
    "top_level_live_semantic_architect_observed_from_v1_1",
    "runtime_execution_topology_materialized",
    "fractal_branch_cells_dispatched",
    "branch_result_proposals_collected",
    "post_vv_validated",
    "gt_lgt_advisory_review",
    "root_first_not_ready",
    "corrected_evidence_received",
    "root_second_supplier_a_scoped_review",
    "human_approval_supplier_a_only",
    "root_created_mock_action_commit_packet_observed",
    "mock_bank_sandbox_receipt_observed",
    "final_state_summary",
}

REQUIRED_CARD_FIELDS = {
    "step_id",
    "actor_or_module",
    "api_like_call",
    "input_summary",
    "output_summary",
    "meaning",
    "does_not_authorize",
    "next_step",
    "trace_id",
    "evidence_id",
}

RETIRED_RUNTIME_EVENT = "runtime_" + "plan" + "graph_compiled"

REQUIRED_BRANCH_IDS = {
    "warehouse_branch",
    "supplier_a_branch",
    "supplier_b_branch",
    "legal_branch",
    "accounting_branch",
    "bank_a_branch",
    "bank_b_branch",
    "root_merge_branch",
}

REQUIRED_AUTHORITY_FACTS = {
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "Branch LLM/SLM output is not truth.",
    "Branch LLM/SLM output is not authority.",
    "Branch LLM/SLM output is not action permission.",
    "Branch LLM/SLM output is not FinalOutput.",
    "Branch LLM/SLM output does not create ActionCommitPacket.",
    "Branch LLM/SLM output does not create receipt.",
    "BSEP is not truth.",
    "BSEP is not authority.",
    "DRS candidate context is not truth.",
    "DRS v0.2 hit is not truth.",
    "DRS v0.2 hit is not authority.",
    "DRS v0.2 hit is not permission.",
    "DRS v0.2 reuse decision is not FinalOutput.",
    "DRS v0.2 direct reuse candidate is not direct reuse.",
    "Old receipt is not current permission.",
    "Old Root Final is not silently reused.",
    "AVF v0.2 score is not truth.",
    "AVF v0.2 score is not authority.",
    "AVF v0.2 score is not permission.",
    "Top-ranked AVF candidate is not permission.",
    "CandidateVector is not action permission.",
    "CandidateVector is not FinalOutput.",
    "HardMask is not Root.",
    "AVF report is advisory only.",
    "High score does not override HardMask.",
    "Top rank does not grant permission.",
    "AVF cannot bypass Root.",
    "AVF cannot create FinalOutput.",
    "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Runtime materializes and owns RuntimeExecutionTopology locally.",
    "Provider does not own PlanGraph.",
    "PlanGraph is not authority.",
    "Branch ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
    "Only Root creates ActionCommitPacket v0.2.",
    "Human approval does not directly create ActionCommitPacket.",
    "LLM does not create ActionCommitPacket.",
    "DRS does not create ActionCommitPacket.",
    "AVF does not create ActionCommitPacket.",
    "GT/LGT does not create ActionCommitPacket.",
    "ActionCommitPacket is not FinalOutput.",
    "ActionCommitPacket is not receipt.",
    "ActionCommitPacket is not payment execution.",
    "ActionCommitPacket is not shipment release.",
    "Local packet registry is not DRS.",
    "Local packet registry is not authority.",
    "Local packet registry is not permission.",
    "Packet accepted for mock corridor is not payment execution.",
    "MockBankSandbox corridor is deterministic, not reasoning.",
    "MockBankSandbox does not restart LLM reasoning after Root.",
    "MockBankSandbox does not decide.",
    "MockBankSandbox does not create authority.",
    "Mock receipt is evidence only.",
    "Mock receipt is not permission.",
    "Mock receipt is not FinalOutput.",
    "Mock receipt does not authorize Supplier B.",
    "Mock receipt does not release shipment.",
    "Mock receipt does not create future permission.",
    "Terminal receipt observation is local proof-only.",
    "Root-created mock ActionCommitPacket is scoped only.",
    "MockBankSandbox receipt is evidence only.",
    "Receipt does not release shipment.",
    "payment_slot is not permission.",
    "Root remains final authority.",
}

REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 PRODUCT TRACE]",
    "[WHAT V1.2 ADDS OVER V1.1]",
    "[LANE MODEL]",
    "[DIRTY REQUEST]",
    "[API-LIKE BUSINESS MODULE TRACE]",
    "[WAREHOUSE API]",
    "[SUPPLIER A API]",
    "[SUPPLIER B API]",
    "[LEGAL MODULE]",
    "[ACCOUNTING MODULE]",
    "[BANK A LEGACY SANDBOX]",
    "[BANK B HEDGEHOG-NATIVE PREVIEW]",
    "[RUNTIME PLAN AND FRACTAL BRANCHES]",
    "[BRANCH RESULT PROPOSALS]",
    "[POST V&V / GT-LGT / ROOT]",
    "[APPROVAL / PACKET / RECEIPT BOUNDARY]",
    "[SECRET MEMBRANE]",
    "[TRANSITION CARDS]",
    "[LOCAL DRS V0.2 RESOLVE]",
    "[LOCAL AVF V0.2 ADVISORY EVALUATION]",
    "[ACTIONCOMMITPACKET V0.2 ROOT-CREATED PACKET BOUNDARY]",
    "[MOCKBANKSANDBOX V0.2 CONTRACT FULFILLMENT CORRIDOR]",
    "[AUTHORITY MATRIX]",
    "[COUNTER MATRIX]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
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

REQUIRED_DRS_SCENARIO_IDS = {
    "supplier_a_prior_scoped_trace",
    "supplier_b_blocker_trace",
    "old_receipt_trace",
    "old_shipment_held_trace",
    "old_root_final_trace",
    "changed_warehouse_fact",
    "stale_legal_accounting_evidence",
    "quarantined_record",
    "deadend_record",
    "wrong_domain_near_match",
    "permission_trace_completed_action_attempt",
}


def _report() -> dict:
    return runner.collect_full_wow_v1_2_product_trace()


def _rendered() -> str:
    return runner.render_full_wow_v1_2_product_trace(_report())


def test_v1_2_product_trace_returns_pass() -> None:
    report = _report()

    assert report["product_trace_status"] == "PASS"
    assert report["final_status"] == "PASS"
    assert report["counters"]["wow_v1_2_product_trace_created_count"] == 1


def test_v1_2_product_trace_business_modules_present() -> None:
    report = _report()
    modules = {module["module_id"]: module for module in report["business_modules"]}

    assert REQUIRED_MODULE_IDS == set(modules)
    assert "GET /warehouse/v1/shipments/SH-2042/inventory" in modules[
        "warehouse_api_sandbox"
    ]["api_like_call"]
    assert "GET /supplier/adriatic-filters" in modules["supplier_a_api_sandbox"][
        "api_like_call"
    ]
    assert "GET /supplier/balkan-pumps" in modules["supplier_b_api_sandbox"][
        "api_like_call"
    ]
    assert modules["supplier_b_api_sandbox"]["supplier_status"] == "blocked"
    assert report["business_boundaries"]["shipment_final_status"] == "HELD"
    assert report["business_boundaries"]["receipt_final_status"] == "EVIDENCE_ONLY"


def test_v1_2_product_trace_transition_cards_present() -> None:
    report = _report()
    cards = report["transition_cards"]
    step_ids = {card["step_id"] for card in cards}

    assert len(cards) == 23
    assert step_ids == REQUIRED_STEP_IDS
    for card in cards:
        assert REQUIRED_CARD_FIELDS <= set(card)

    by_step = {card["step_id"]: card for card in cards}
    assert (
        by_step["bsep_membrane_observed_from_v1_1"]["next_step"]
        == "top_level_live_semantic_architect_observed_from_v1_1"
    )
    assert (
        by_step["top_level_live_semantic_architect_observed_from_v1_1"][
            "next_step"
        ]
        == "runtime_execution_topology_materialized"
    )


def test_runtime_execution_topology_event_preserves_lifecycle_and_authority() -> None:
    report = _report()
    cards = report["transition_cards"]
    ordered_step_ids = tuple(card["step_id"] for card in cards)
    assert ordered_step_ids[10:13] == (
        "top_level_live_semantic_architect_observed_from_v1_1",
        "runtime_execution_topology_materialized",
        "fractal_branch_cells_dispatched",
    )
    assert RETIRED_RUNTIME_EVENT not in ordered_step_ids

    topology_event = cards[11]
    assert topology_event["actor_or_module"] == "runtime"
    assert topology_event["output_summary"] == (
        "Local runtime materialized RuntimeExecutionTopology."
    )
    assert topology_event["does_not_authorize"] == (
        "authority, permission, effect, receipt, or Root final"
    )
    assert topology_event["next_step"] == "fractal_branch_cells_dispatched"

    runtime_plan = report["runtime_plan"]
    assert runtime_plan["runtime_execution_topology_materialized_count"] == 1
    assert runtime_plan["runtime_execution_topology_owned_by_local_runtime"] is True
    assert RETIRED_RUNTIME_EVENT + "_count" not in runtime_plan
    assert report["business_boundaries"]["root_remains_final_authority"] is True
    assert report["real_world_effects_count"] == 0
    assert len(cards) == 23


def test_v1_2_product_trace_fractal_branches_present() -> None:
    branches = _report()["fractal_branches"]
    branch_ids = {branch["branch_id"] for branch in branches}

    assert branch_ids == REQUIRED_BRANCH_IDS
    for branch in branches:
        assert branch["branch_context"]
        assert branch["branch_evidence"]
        assert branch["branch_result_proposal"]
        assert branch["branch_authority_boundary"]
        assert branch["branch_real_world_effects_count"] == 0
        assert branch["branch_called_llm_or_slm_count"] == 0


def test_v1_2_product_trace_result_proposals_present() -> None:
    proposals = _report()["branch_result_proposals"]

    assert len(proposals) == 8
    for proposal in proposals:
        assert proposal["result_proposal_id"].endswith("_result_proposal")
        assert proposal["source_branch_id"] in REQUIRED_BRANCH_IDS
        assert proposal["authority_claimed"] is False
        assert proposal["action_permission_claimed"] is False
        assert proposal["final_output_claimed"] is False


def test_v1_2_product_trace_secret_membrane() -> None:
    report = _report()
    counters = report["counters"]
    rendered = runner.render_full_wow_v1_2_product_trace(report)

    assert counters["bank_internal_raw_iban_present_count"] == 1
    assert counters["bank_internal_token_present_count"] == 1
    assert counters["llm_visible_raw_iban_count"] == 0
    assert counters["llm_visible_bank_token_count"] == 0
    assert counters["llm_visible_secret_count"] == 0
    assert "Secrets ∩ LLMContext = empty" in rendered
    assert "payment_slot != permission" in rendered
    assert "receipt != shipment release" in rendered


def test_v1_2_product_trace_manual_live_multillm_fractal_lane_reserved_not_implemented() -> None:
    report = _report()
    counters = report["counters"]
    lane = report["manual_live_multillm_fractal_lane"]

    assert counters["manual_live_multillm_fractal_lane_available_count"] == 1
    assert counters["manual_live_multillm_fractal_lane_implemented_count"] == 0
    assert counters["top_level_orchestrator_llm_call_count"] == 0
    assert counters["top_level_architect_llm_call_count"] == 0
    assert counters["branch_local_llm_slm_call_count"] == 0
    assert lane["implemented_in_this_patch"] is False
    assert lane["available_future"] is True
    assert (
        lane["note"]
        == "Patch 2 will implement env-gated manual live multi-LLM/fractal observation."
    )


def test_v1_2_product_trace_no_real_execution_or_effects() -> None:
    counters = _report()["counters"]

    assert counters["product_trace_created_action_commit_packet_count"] == 0
    assert (
        counters["product_trace_created_action_commit_packet_v0_2_model_packet_count"]
        == 1
    )
    assert counters["product_trace_created_receipt_count"] == 0
    assert counters["product_trace_executed_mock_payment_count"] == 0
    assert counters["product_trace_executed_real_payment_count"] == 0
    assert counters["product_trace_released_shipment_count"] == 0
    assert counters["product_trace_called_real_bank_supplier_warehouse_api_count"] == 0
    assert counters["drs_v0_2_external_drs_used_count"] == 0
    assert counters["drs_v0_2_global_drs_used_count"] == 0
    assert counters["drs_v0_2_vector_db_used_count"] == 0
    assert counters["drs_v0_2_embeddings_required_count"] == 0
    assert counters["avf_v0_2_provider_called_count"] == 0
    assert counters["avf_v0_2_network_called_count"] == 0
    assert counters["avf_v0_2_gemini_called_count"] == 0
    assert counters["avf_v0_2_high_score_hardmask_override_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_v1_2_product_trace_drs_v0_2_resolve_present() -> None:
    report = _report()
    drs = report["drs_v0_2_resolve"]

    assert drs["drs_v0_2_status"] == "PASS"
    assert drs["resolver_mode"] == "deterministic_local"
    assert drs["temporal_query_present"] is True
    assert drs["records_evaluated_count"] == 11
    assert drs["direct_reuse_allowed_count"] == 0
    assert drs["root_review_required_count"] == 11
    assert report["counters"]["drs_v0_2_resolve_invoked_count"] == 1
    assert report["counters"]["drs_v0_2_records_evaluated_count"] == 11
    assert report["counters"]["drs_v0_2_direct_reuse_allowed_count"] == 0
    assert report["counters"]["drs_v0_2_root_review_required_count"] == 11


def test_v1_2_product_trace_drs_v0_2_regression_scenarios_present() -> None:
    drs = _report()["drs_v0_2_resolve"]

    assert set(drs["baseline_regression_scenario_ids"]) == REQUIRED_DRS_SCENARIO_IDS


def test_v1_2_product_trace_drs_v0_2_tables_present() -> None:
    drs = _report()["drs_v0_2_resolve"]

    assert drs["freshness_table"]
    assert drs["lineage_table"]
    assert drs["provenance_table"]
    assert drs["reuse_decision_table"]
    assert all(row["ref_id"] for row in drs["lineage_table"])
    assert all(row["provenance_refs"] for row in drs["provenance_table"])
    assert all(
        row["direct_reuse_allowed"] is False
        for row in drs["reuse_decision_table"]
    )


def test_v1_2_product_trace_drs_v0_2_old_receipt_not_permission() -> None:
    report = _report()
    decisions = {
        decision["record_id"]: decision
        for decision in report["drs_v0_2_resolve"]["decisions_summary"]
    }
    decision = decisions["old_receipt_trace"]
    rendered = runner.render_full_wow_v1_2_product_trace(report)

    assert "old_receipt_not_permission" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False
    assert "Old receipt is not current permission" in rendered


def test_v1_2_product_trace_drs_v0_2_root_final_not_silent_reuse() -> None:
    report = _report()
    decisions = {
        decision["record_id"]: decision
        for decision in report["drs_v0_2_resolve"]["decisions_summary"]
    }
    decision = decisions["old_root_final_trace"]
    rendered = runner.render_full_wow_v1_2_product_trace(report)

    assert "prior_root_final_not_silent_reuse" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False
    assert "Old Root Final is not silently reused" in rendered


def test_v1_2_product_trace_drs_v0_2_changed_facts_require_rerun() -> None:
    decisions = {
        decision["record_id"]: decision
        for decision in _report()["drs_v0_2_resolve"]["decisions_summary"]
    }
    decision = decisions["changed_warehouse_fact"]

    assert decision["reuse_decision_class"] == "rerun_required"
    assert "changed_facts_require_rerun_validation" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False


def test_v1_2_product_trace_drs_v0_2_quarantine_deadend_wrong_domain_blocked() -> None:
    decisions = {
        decision["record_id"]: decision
        for decision in _report()["drs_v0_2_resolve"]["decisions_summary"]
    }

    assert decisions["quarantined_record"]["reuse_decision_class"] == "blocked"
    assert decisions["deadend_record"]["reuse_decision_class"] in {
        "blocked",
        "warning_only",
    }
    assert decisions["wrong_domain_near_match"]["reuse_decision_class"] in {
        "rerun_required",
        "blocked",
    }
    assert all(decision["direct_reuse_allowed"] is False for decision in decisions.values())


def test_v1_2_product_trace_drs_v0_2_no_authority_or_permission() -> None:
    report = _report()
    counters = report["counters"]
    authority = set(report["authority_matrix"])

    assert counters["drs_v0_2_permission_granted_count"] == 0
    assert counters["drs_v0_2_root_bypass_count"] == 0
    for decision in report["drs_v0_2_resolve"]["decisions_summary"]:
        assert decision["truth_claimed"] is False
        assert decision["authority_claimed"] is False
        assert decision["action_permission_claimed"] is False
        assert decision["final_output_claimed"] is False

    assert "DRS v0.2 hit is not truth." in authority
    assert "DRS v0.2 hit is not authority." in authority
    assert "DRS v0.2 hit is not permission." in authority
    assert "DRS v0.2 reuse decision is not FinalOutput." in authority
    assert "DRS v0.2 direct reuse candidate is not direct reuse." in authority


def test_v1_2_product_trace_avf_v0_2_evaluation_present() -> None:
    report = _report()
    avf = report["avf_v0_2_evaluation"]

    assert avf["avf_v0_2_status"] == "PASS"
    assert avf["resolver_mode"] == "deterministic_local"
    assert avf["candidates_evaluated_count"] == 9
    assert avf["ranked_candidates"]
    assert avf["hard_mask_table"]
    assert avf["soft_mask_table"]
    assert avf["score_explanation_table"]
    assert report["counters"]["avf_v0_2_evaluation_invoked_count"] == 1
    assert report["counters"]["avf_v0_2_candidates_evaluated_count"] == 9


def test_v1_2_product_trace_avf_v0_2_hardmasks_unsafe_candidates() -> None:
    avf = _report()["avf_v0_2_evaluation"]
    rows = {row["candidate_id"]: row for row in avf["ranked_candidates"]}
    hard_mask_rows = {row["candidate_id"]: row for row in avf["hard_mask_table"]}

    release_all = rows["release_all_and_pay_all"]
    supplier_b = rows["pay_supplier_b"]
    assert release_all["hard_mask_value"] == 0
    assert release_all["final_avf_score"] == 0.0
    assert supplier_b["hard_mask_value"] == 0
    assert supplier_b["final_avf_score"] == 0.0
    assert "high_score_does_not_override_hardmask" in hard_mask_rows[
        "release_all_and_pay_all"
    ]["hard_mask_reasons"]
    assert "hardmasked_candidate_score_forced_zero" in hard_mask_rows[
        "pay_supplier_b"
    ]["hard_mask_reasons"]


def test_v1_2_product_trace_avf_v0_2_hardmask_beats_high_score_visible() -> None:
    avf = _report()["avf_v0_2_evaluation"]
    rows = {row["candidate_id"]: row for row in avf["ranked_candidates"]}
    rendered = _rendered()

    assert rows["release_all_and_pay_all"]["base_viability_score"] == 0.95
    assert rows["release_all_and_pay_all"]["final_avf_score"] == 0.0
    assert rows["pay_supplier_b"]["base_viability_score"] == 0.8
    assert rows["pay_supplier_b"]["final_avf_score"] == 0.0
    assert "High score does not override HardMask" in rendered


def test_v1_2_product_trace_avf_v0_2_safe_candidates_rank_without_permission() -> None:
    avf = _report()["avf_v0_2_evaluation"]
    rows = {row["candidate_id"]: row for row in avf["ranked_candidates"]}
    decisions = {
        decision["candidate_id"]: decision
        for decision in avf["decision_reports_summary"]
    }

    for candidate_id in {
        "prepare_supplier_a_payment_form_only",
        "root_review_only",
        "keep_shipment_held",
    }:
        assert rows[candidate_id]["final_avf_score"] > 0.0
        assert rows[candidate_id]["score_is_not_permission"] is True
        assert decisions[candidate_id]["payment_allowed"] is False
        assert decisions[candidate_id]["final_decision"] is False
        assert decisions[candidate_id]["execute"] is False


def test_v1_2_product_trace_avf_v0_2_top_candidate_not_permission() -> None:
    report = _report()
    avf = report["avf_v0_2_evaluation"]
    top_candidate_id = avf["top_candidate_id"]
    decisions = {
        decision["candidate_id"]: decision
        for decision in avf["decision_reports_summary"]
    }

    assert top_candidate_id is not None
    assert decisions[top_candidate_id]["top_ranked_candidate_not_permission"] is True
    assert decisions[top_candidate_id]["payment_allowed"] is False
    assert decisions[top_candidate_id]["final_output_claimed"] is False
    assert decisions[top_candidate_id]["final_decision"] is False
    assert (
        report["counters"]["avf_v0_2_top_ranked_candidate_permission_granted_count"]
        == 0
    )


def test_v1_2_product_trace_avf_v0_2_top_rank_still_not_permission() -> None:
    rendered = _rendered()
    report = _report()
    avf = report["avf_v0_2_evaluation"]

    assert avf["top_candidate_id"] is not None
    assert report["counters"]["avf_v0_2_top_ranked_candidate_permission_granted_count"] == 0
    assert "Top rank does not grant permission" in rendered


def test_v1_2_product_trace_avf_v0_2_score_explanations_visible() -> None:
    rows = _report()["avf_v0_2_evaluation"]["score_explanation_table"]

    assert rows
    for row in rows:
        assert row["score_is_not_permission"] is True
        assert row["candidate_is_not_action"] is True
        assert row["candidate_vector_is_not_final_output"] is True
        assert row["root_review_required"] is True


def test_v1_2_product_trace_avf_v0_2_uses_drs_refs() -> None:
    avf = _report()["avf_v0_2_evaluation"]

    assert avf["source_drs_report_ref"] == "local_drs_v0_2_reuse_decision_report"
    assert REQUIRED_DRS_SCENARIO_IDS <= set(avf["source_drs_record_refs"])


def test_v1_2_product_trace_avf_v0_2_no_authority_or_effects() -> None:
    report = _report()
    counters = report["counters"]
    authority = set(report["authority_matrix"])

    assert counters["avf_v0_2_action_permission_granted_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert counters["avf_v0_2_root_bypass_count"] == 0
    assert counters["avf_v0_2_action_commit_packet_created_count"] == 0
    assert counters["avf_v0_2_receipt_created_count"] == 0
    assert counters["avf_v0_2_payment_executed_count"] == 0
    assert counters["avf_v0_2_shipment_released_count"] == 0
    assert counters["product_trace_created_action_commit_packet_count"] == 0
    assert counters["product_trace_created_receipt_count"] == 0
    assert counters["product_trace_executed_mock_payment_count"] == 0
    assert counters["product_trace_executed_real_payment_count"] == 0
    assert counters["product_trace_released_shipment_count"] == 0
    assert counters["real_world_effects_count"] == 0

    assert "AVF v0.2 score is not truth." in authority
    assert "AVF v0.2 score is not authority." in authority
    assert "AVF v0.2 score is not permission." in authority
    assert "Top-ranked AVF candidate is not permission." in authority
    assert "CandidateVector is not action permission." in authority
    assert "CandidateVector is not FinalOutput." in authority
    assert "HardMask is not Root." in authority
    assert "AVF report is advisory only." in authority
    assert "AVF cannot bypass Root." in authority
    assert "AVF cannot create FinalOutput." in authority


def test_v1_2_product_trace_avf_v0_2_no_root_bypass_or_final_output() -> None:
    report = _report()
    counters = report["counters"]
    authority = set(report["authority_matrix"])

    assert counters["avf_v0_2_root_bypass_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert "AVF cannot bypass Root." in authority
    assert "Root remains final authority." in authority


def test_v1_2_product_trace_avf_v0_2_no_action_effects() -> None:
    counters = _report()["counters"]

    assert counters["avf_v0_2_action_commit_packet_created_count"] == 0
    assert counters["avf_v0_2_receipt_created_count"] == 0
    assert counters["avf_v0_2_payment_executed_count"] == 0
    assert counters["avf_v0_2_shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_v1_2_product_trace_action_commit_packet_v0_2_integration_present() -> None:
    report = _report()
    acp = report["action_commit_packet_v0_2_integration"]

    assert acp["action_commit_packet_v0_2_status"] == "PASS"
    assert acp["packet_id"]
    assert acp["root_created"] is True
    assert acp["packet_validated"] is True
    assert acp["registry_validated"] is True
    assert acp["packet_corridor_entry_validated"] is True
    assert acp["accepted_for_mock_corridor"] is True


def test_v1_2_product_trace_action_commit_packet_v0_2_scope_is_supplier_a_only() -> None:
    acp = _report()["action_commit_packet_v0_2_integration"]

    assert "supplier_a_adriatic_filters" in acp["allowed_subjects"]
    assert "supplier_b_balkan_pumps" in acp["forbidden_subjects"]
    assert "shipment_sh_2042" in acp["forbidden_subjects"]
    assert "mock_supplier_a_payment_intent" in acp["allowed_actions"]
    assert "mock_supplier_a_payment_order" in acp["allowed_actions"]
    assert "supplier_b_payment" in acp["forbidden_actions"]
    assert "shipment_release" in acp["forbidden_actions"]
    assert "real_payment" in acp["forbidden_actions"]
    assert "real_bank_transfer" in acp["forbidden_actions"]
    assert "mock_bank_sandbox" in acp["allowed_adapters"]
    assert "bank_a_mock" in acp["allowed_adapters"]
    assert "real_bank" in acp["forbidden_adapters"]
    assert "real_supplier_api" in acp["forbidden_adapters"]
    assert "real_warehouse_api" in acp["forbidden_adapters"]


def test_v1_2_product_trace_action_commit_packet_v0_2_creator_boundaries() -> None:
    report = _report()
    acp = report["action_commit_packet_v0_2_integration"]
    counters = report["counters"]
    authority = set(report["authority_matrix"])

    assert acp["created_by"] == "root"
    assert counters["action_commit_packet_v0_2_created_by_root_count"] == 1
    assert counters["action_commit_packet_v0_2_created_by_human_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_llm_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_drs_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_avf_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_gt_lgt_count"] == 0
    assert (
        counters["action_commit_packet_v0_2_human_approval_used_as_evidence_count"]
        == 1
    )
    assert "Only Root creates ActionCommitPacket v0.2." in authority
    assert "Human approval is scoped evidence only." in authority
    assert "Human approval does not directly create ActionCommitPacket." in authority
    assert "LLM does not create ActionCommitPacket." in authority
    assert "DRS does not create ActionCommitPacket." in authority
    assert "AVF does not create ActionCommitPacket." in authority
    assert "GT/LGT does not create ActionCommitPacket." in authority


def test_v1_2_product_trace_action_commit_packet_v0_2_registry_observes_without_authority() -> None:
    report = _report()
    acp = report["action_commit_packet_v0_2_integration"]
    counters = report["counters"]

    assert acp["registry_is_local_proof_only"] is True
    assert acp["registry_is_not_drs"] is True
    assert acp["registry_is_not_authority"] is True
    assert acp["registry_is_not_permission"] is True
    assert counters["action_commit_packet_v0_2_packet_seen_recorded_count"] == 1
    assert counters["action_commit_packet_v0_2_terminal_receipt_recorded_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_receipt_created_count"] == 0
    assert counters["action_commit_packet_v0_2_payment_executed_count"] == 0
    assert counters["action_commit_packet_v0_2_shipment_released_count"] == 0
    assert counters["action_commit_packet_v0_2_real_world_effects_count"] == 0


def test_v1_2_product_trace_action_commit_packet_v0_2_corridor_entry_validated_but_not_executed() -> None:
    counters = _report()["counters"]

    assert counters["action_commit_packet_v0_2_accepted_for_mock_corridor_count"] == 1
    assert counters["action_commit_packet_v0_2_mock_bank_sandbox_executed_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_payment_order_created_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_receipt_created_count"] == 0
    assert counters["action_commit_packet_v0_2_payment_executed_count"] == 0
    assert counters["action_commit_packet_v0_2_shipment_released_count"] == 0
    assert counters["action_commit_packet_v0_2_final_output_created_count"] == 0


def test_v1_2_product_trace_action_commit_packet_v0_2_rendered_section() -> None:
    rendered = _rendered()

    assert "[ACTIONCOMMITPACKET V0.2 ROOT-CREATED PACKET BOUNDARY]" in rendered
    assert "Root created a scoped Supplier A ActionCommitPacket model" in rendered
    assert "Human approval is scoped evidence only" in rendered
    assert "LLM/DRS/AVF/GT-LGT did not create the packet" in rendered
    assert "Supplier B is excluded" in rendered
    assert "Shipment release is excluded" in rendered
    assert "Packet is accepted for future mock corridor only" in rendered
    assert "Slice C does not execute MockBankSandbox" in rendered
    assert "Slice C does not create receipt" in rendered
    assert "Root remains final authority" in rendered


def test_v1_2_product_trace_action_commit_packet_v0_2_no_execution_or_effects() -> None:
    counters = _report()["counters"]

    assert counters["product_trace_created_receipt_count"] == 0
    assert counters["product_trace_executed_mock_payment_count"] == 0
    assert counters["product_trace_executed_real_payment_count"] == 0
    assert counters["product_trace_released_shipment_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_payment_order_created_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_receipt_created_count"] == 0
    assert counters["action_commit_packet_v0_2_mock_bank_sandbox_executed_count"] == 0
    assert counters["action_commit_packet_v0_2_provider_called_count"] == 0
    assert counters["action_commit_packet_v0_2_network_called_count"] == 0
    assert counters["action_commit_packet_v0_2_gemini_called_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_execution_present() -> None:
    mock = _report()["mock_bank_sandbox_v0_2_corridor_execution"]

    assert mock["mock_bank_sandbox_v0_2_status"] == "PASS"
    assert mock["source_packet_validated"] is True
    assert mock["source_packet_corridor_entry_validated"] is True
    assert mock["source_packet_seen_in_registry"] is True
    assert mock["mock_payment_intent"]
    assert mock["mock_payment_consent"]
    assert mock["mock_payment_order"]
    assert mock["mock_receipt_evidence"]
    assert mock["receipt_validated"] is True
    assert mock["terminal_receipt_observed_in_local_registry"] is True


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_sequence_visible() -> None:
    sequence = _report()["mock_bank_sandbox_v0_2_corridor_execution"][
        "corridor_sequence"
    ]
    step_ids = {step["step_id"] for step in sequence}
    required_steps = {
        "packet_validation",
        "local_registry_replay_guard",
        "scope_check",
        "amount_check",
        "creditor_check",
        "payment_slot_check",
        "adapter_binding_check",
        "idempotency_check",
        "expiry_ttl_check",
        "forbidden_surface_check",
        "mock_payment_order",
        "mock_receipt_evidence",
    }

    assert required_steps <= step_ids
    for step in sequence:
        assert "input_summary" in step
        assert "output_summary" in step
        assert "meaning" in step
        assert "does_not_authorize" in step
        assert "next_step" in step


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_receipt_evidence_only() -> None:
    receipt = _report()["mock_bank_sandbox_v0_2_corridor_execution"][
        "mock_receipt_evidence"
    ]

    assert receipt["evidence_only"] is True
    assert receipt["creates_future_permission"] is False
    assert receipt["creates_action_permission"] is False
    assert receipt["creates_final_output"] is False
    assert receipt["releases_shipment"] is False
    assert receipt["authorizes_supplier_b"] is False
    assert receipt["mutates_packet_scope"] is False
    assert receipt["creates_production_drs_record"] is False
    assert receipt["real_world_effects_count"] == 0


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_keeps_supplier_b_and_shipment_blocked() -> None:
    report = _report()
    mock = report["mock_bank_sandbox_v0_2_corridor_execution"]
    counters = report["counters"]

    assert mock["supplier_b_excluded"] is True
    assert mock["shipment_release_excluded"] is True
    assert counters["mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_shipment_release_count"] == 0
    assert counters["product_trace_released_shipment_count"] == 0


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_no_real_api_or_provider_calls() -> None:
    counters = _report()["counters"]

    assert counters["mock_bank_sandbox_v0_2_real_bank_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_supplier_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_warehouse_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_provider_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_network_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_gemini_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_world_effects_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_registry_records_terminal_receipt_only() -> None:
    report = _report()
    mock = report["mock_bank_sandbox_v0_2_corridor_execution"]
    counters = report["counters"]

    assert counters["mock_bank_sandbox_v0_2_terminal_receipt_observed_count"] == 1
    assert mock["terminal_receipt_observation_is_local_proof_only"] is True
    assert counters["mock_bank_sandbox_v0_2_receipt_permission_created_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_payment_executed_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_shipment_released_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_world_effects_count"] == 0


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_rendered_section() -> None:
    rendered = _rendered()

    assert "[MOCKBANKSANDBOX V0.2 CONTRACT FULFILLMENT CORRIDOR]" in rendered
    assert "MockBankSandbox consumed the Root-created Supplier A packet" in rendered
    assert "The corridor validated packet shape" in rendered
    assert "The corridor created a mock payment intent/consent/order" in rendered
    assert "The corridor returned mock receipt evidence" in rendered
    assert "Receipt is evidence only" in rendered
    assert "Supplier B remains blocked" in rendered
    assert "Shipment remains held" in rendered
    assert "No real-world effect occurred" in rendered
    assert "Root remains final authority" in rendered


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_no_post_root_reasoning_or_authority() -> None:
    authority = set(_report()["authority_matrix"])

    assert "MockBankSandbox does not restart LLM reasoning after Root." in authority
    assert "MockBankSandbox does not decide." in authority
    assert "Mock receipt is not permission." in authority
    assert "Root remains final authority." in authority


def test_v1_2_product_trace_mock_bank_sandbox_v0_2_source_import_boundary() -> None:
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

    assert "hedgehog.mock_connector_sandbox" not in source
    assert "from hedgehog.action_commit_packet import" not in source
    assert "import hedgehog.action_commit_packet\n" not in source
    assert "google.genai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "openai" not in source
    assert "subprocess" not in source
    assert "call_real_bank" not in source
    assert "call_real_supplier" not in source
    assert "call_real_warehouse" not in source
    for phrase in forbidden_phrases:
        assert phrase not in source


def test_v1_2_product_trace_authority_matrix() -> None:
    authority = set(_report()["authority_matrix"])

    assert REQUIRED_AUTHORITY_FACTS <= authority
    assert "Root remains final authority." in authority
    assert "Provider does not own PlanGraph." in authority
    assert "Branch LLM/SLM output is not authority." in authority
    assert "Branch LLM/SLM output is not action permission." in authority
    assert "Branch LLM/SLM output is not FinalOutput." in authority
    assert "DRS v0.2 hit is not authority." in authority
    assert "AVF v0.2 score is not authority." in authority
    assert "Top-ranked AVF candidate is not permission." in authority
    assert "Only Root creates ActionCommitPacket v0.2." in authority
    assert "Local packet registry is not authority." in authority
    assert "Packet accepted for mock corridor is not payment execution." in authority
    assert "MockBankSandbox corridor is deterministic, not reasoning." in authority
    assert "Mock receipt is evidence only." in authority
    assert "Terminal receipt observation is local proof-only." in authority


def test_v1_2_product_trace_rendered_sections() -> None:
    rendered = _rendered()

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "real Gemini Semantic Architect" in rendered
    assert "Architect semantic validation accepted" in rendered
    assert "local runtime materialized and owned RuntimeExecutionTopology" in rendered
    assert "DRS found prior traces" in rendered
    assert "DRS classified them as context" in rendered
    assert "DRS did not authorize payment" in rendered
    assert "DRS did not authorize shipment release" in rendered
    assert "Old receipt is not current permission" in rendered
    assert "Old Root Final is not silently reused" in rendered
    assert "AVF consumed Local DRS v0.2 candidate/reuse signals" in rendered
    assert "release_all_and_pay_all was hard masked" in rendered
    assert "Supplier B payment was hard masked" in rendered
    assert "safe candidates may rank but do not grant permission" in rendered
    assert "top-ranked candidate is not permission" in rendered
    assert "AVF score is not authority" in rendered
    assert "HardMask is not Root" in rendered
    assert "High score does not override HardMask" in rendered
    assert "Top rank does not grant permission" in rendered
    assert "AVF cannot bypass Root" in rendered
    assert "AVF cannot create FinalOutput" in rendered
    assert (
        "AVF cannot create ActionCommitPacket, receipt, payment, or shipment release"
        in rendered
    )
    assert "Root created a scoped Supplier A ActionCommitPacket model" in rendered
    assert "Packet is accepted for future mock corridor only" in rendered
    assert "Slice C does not execute MockBankSandbox" in rendered
    assert "MockBankSandbox consumed the Root-created Supplier A packet" in rendered
    assert "The corridor returned mock receipt evidence" in rendered
    assert "Receipt is evidence only" in rendered
    assert "Supplier B remains blocked" in rendered
    assert "Shipment remains held" in rendered
    assert "No real-world effect occurred" in rendered
    assert "Root remains final authority" in rendered
    assert "FINAL STATUS: PASS" in rendered


def test_v1_2_product_trace_non_claims_and_forbidden_overclaims() -> None:
    rendered = _rendered()

    assert "not production" in rendered
    assert "not public auditor final package" in rendered
    assert "no real payment" in rendered
    assert "no real shipment release" in rendered
    assert "manual live multi-LLM/fractal lane not implemented in this patch" in rendered
    for left, right in FORBIDDEN_PHRASE_PARTS:
        assert left + right not in rendered


def test_v1_2_product_trace_does_not_import_live_or_execution_runners() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "google.genai" not in source
    assert "hedgehog.local_drs_v02" in source
    assert "hedgehog.avf_v02" in source
    assert "hedgehog.action_commit_packet_v02" in source
    assert "run_full_semantic_e2e_v01" not in source
    assert "run_supplier_payment_shipment_release_review_wow_v1_1" not in source
    assert "run_human_full_wow_v1_1_final_walkthrough" not in source


def test_v1_2_product_trace_action_commit_packet_v0_2_source_import_boundary() -> None:
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

    assert "hedgehog.action_commit_packet_v02" in source
    assert "from hedgehog.action_commit_packet import" not in source
    assert "import hedgehog.action_commit_packet\n" not in source
    assert "hedgehog.mock_connector_sandbox" not in source
    assert "google.genai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "openai" not in source
    assert "subprocess" not in source
    assert "call_real_bank" not in source
    assert "call_real_supplier" not in source
    assert "call_real_warehouse" not in source
    for phrase in forbidden_phrases:
        assert phrase not in source
