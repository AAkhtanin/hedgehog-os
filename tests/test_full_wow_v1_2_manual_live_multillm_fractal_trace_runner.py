from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any, Mapping

from demo import run_full_wow_v1_2_manual_live_multillm_fractal_trace as runner


ENABLED_ENV = {runner.ENABLE_ENV: "1"}

REQUIRED_SEQUENCE_SUBSET = (
    "local_drs_v0_2_resolve_invoked",
    "avf_v0_2_evaluation_invoked",
    "top_level_orchestrator_provider_called",
    "top_level_orchestrator_semantics_validated",
    "bsep_created",
    "bsep_validated",
    "top_level_architect_provider_called",
    "top_level_architect_semantics_validated",
    "runtime_plangraph_compiled",
    "fractal_branch_cells_created",
    "branch_result_proposals_merged",
    "post_vv_validated",
    "gt_lgt_advisory_reviewed",
    "root_final_boundary_evaluated",
    "action_commit_packet_v0_2_integration_invoked",
    "action_commit_packet_v0_2_packet_validated",
    "action_commit_packet_v0_2_registry_validated",
    "action_commit_packet_v0_2_corridor_entry_validated",
    "action_commit_packet_v0_2_packet_seen_recorded",
    "mock_bank_sandbox_v0_2_corridor_invoked",
    "mock_bank_sandbox_v0_2_mock_payment_intent_created",
    "mock_bank_sandbox_v0_2_mock_payment_consent_created",
    "mock_bank_sandbox_v0_2_mock_payment_order_created",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created",
    "mock_bank_sandbox_v0_2_receipt_validated",
    "mock_bank_sandbox_v0_2_terminal_receipt_observed",
)

REQUIRED_ARTIFACTS = {
    "summary.json",
    "summary.log",
    "secret_scan.json",
    "local_drs_v0_2_resolve_report.json",
    "local_drs_v0_2_freshness_table.json",
    "local_drs_v0_2_lineage_table.json",
    "local_drs_v0_2_provenance_table.json",
    "local_drs_v0_2_reuse_decision_table.json",
    "local_drs_v0_2_writeback_candidate.json",
    "avf_v0_2_evaluation_report.json",
    "avf_v0_2_ranked_candidates.json",
    "avf_v0_2_hard_mask_table.json",
    "avf_v0_2_soft_mask_table.json",
    "avf_v0_2_score_explanation_table.json",
    "top_level_orchestrator_prompt.txt",
    "top_level_orchestrator_raw_response.txt",
    "top_level_orchestrator_extracted_json_candidate.json",
    "top_level_orchestrator_validation.json",
    "bsep_packet.json",
    "bsep_validation.json",
    "top_level_architect_prompt.txt",
    "top_level_architect_raw_response.txt",
    "top_level_architect_extracted_json_candidate.json",
    "top_level_architect_validation.json",
    "branch_legal_prompt.txt",
    "branch_legal_raw_response.txt",
    "branch_legal_validation.json",
    "branch_accounting_prompt.txt",
    "branch_accounting_raw_response.txt",
    "branch_accounting_validation.json",
    "branch_supplier_b_prompt.txt",
    "branch_supplier_b_raw_response.txt",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_prompt.txt",
    "branch_bank_policy_raw_response.txt",
    "branch_bank_policy_validation.json",
    "action_commit_packet_v0_2_integration.json",
    "action_commit_packet_v0_2_packet_validation.json",
    "action_commit_packet_v0_2_registry_validation.json",
    "action_commit_packet_v0_2_corridor_entry_validation.json",
    "mock_bank_sandbox_v0_2_corridor_execution.json",
    "mock_bank_sandbox_v0_2_corridor_sequence.json",
    "mock_bank_sandbox_v0_2_mock_payment_intent.json",
    "mock_bank_sandbox_v0_2_mock_payment_consent.json",
    "mock_bank_sandbox_v0_2_mock_payment_order.json",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence.json",
    "mock_bank_sandbox_v0_2_receipt_validation.json",
}

REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 MANUAL LIVE MULTI-LLM FRACTAL TRACE]",
    "[LANE STATUS]",
    "[SEMANTIC ACTOR CALLS]",
    "[LOCAL DRS V0.2 LIVE OBSERVATION]",
    "[LOCAL AVF V0.2 LIVE OBSERVATION]",
    "[TOP-LEVEL ORCHESTRATOR]",
    "[BSEP MEMBRANE]",
    "[TOP-LEVEL SEMANTIC ARCHITECT]",
    "[RUNTIME PLAN AND FRACTAL CELLS]",
    "[BRANCH-LOCAL LLM/SLM ACTORS]",
    "[BRANCH RESULT PROPOSALS]",
    "[POST V&V / GT-LGT / ROOT]",
    "[ACTIONCOMMITPACKET V0.2 LIVE OBSERVATION]",
    "[MOCKBANKSANDBOX V0.2 LIVE CONTRACT CORRIDOR OBSERVATION]",
    "[SECRET MEMBRANE]",
    "[AUTHORITY MATRIX]",
    "[COUNTER MATRIX]",
    "[ARTIFACTS]",
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

SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "raw_iban_value",
    "GEMINI_API_KEY" + "=",
    "GOOGLE_API_KEY" + "=",
    "GOOGLE_GEMINI_API_KEY" + "=",
)

REQUIRED_DRS_SCENARIOS = {
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

REQUIRED_AVF_CANDIDATES = {
    "release_all_and_pay_all",
    "pay_supplier_a_only",
    "pay_supplier_b",
    "prepare_supplier_a_payment_form_only",
    "request_fresh_warehouse_validation",
    "request_fresh_legal_accounting_validation",
    "keep_shipment_held",
    "root_review_only",
    "block_supplier_b_and_hold_shipment",
}


def _final_json_skeleton(prompt: str) -> dict[str, Any]:
    marker = "JSON skeleton:\n"
    assert marker in prompt
    suffix = prompt.split(marker, 1)[1]
    return json.loads(suffix)


def _assert_no_text_after_skeleton(prompt: str) -> None:
    marker = "JSON skeleton:\n"
    suffix = prompt.split(marker, 1)[1]
    json.loads(suffix)


def _orchestrator_payload() -> dict[str, Any]:
    return {
        "proposal_id": "orch-semantic-wow-v1-2-001",
        "suggested_route": "supplier_payment_shipment_review_v1_2",
        "selected_branch_ids": list(runner.BRANCH_IDS),
        "required_guards": ["BSEP", "Post V&V", "Root final authority"],
        "route_reasoning": [
            "Route business module evidence through bounded semantic review."
        ],
        "evidence_needed": ["warehouse", "supplier", "legal", "accounting", "bank"],
        "uncertainty_notes": ["Provider semantics remain candidate-only."],
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "root_review_required": True,
    }


def _architect_payload() -> dict[str, Any]:
    return {
        "proposal_id": "architect-semantic-wow-v1-2-001",
        "source_route_id": "orch-semantic-wow-v1-2-001",
        "selected_branch_ids": list(runner.BRANCH_IDS),
        "root_recommendation": "needs_more_evidence",
        "result_proposal_summary": "Supplier B remains blocked, shipment held, Supplier A scoped review stays Root-controlled.",
        "required_validators": ["semantic proposal", "branch proposal", "Root"],
        "plan_shape_reasoning": [
            "Runtime builds local plan artifacts after validation."
        ],
        "branch_intent_reasoning": [
            "Branches gather bounded business evidence for Root."
        ],
        "executor_constraint_reasoning": [
            "No executor is authorized by provider output."
        ],
        "forbidden_surface_reasoning": [
            "Payment, shipment release, packet, and receipt remain outside provider authority."
        ],
        "validator_coverage_reasoning": [
            "Semantic, BSEP, branch, Post V&V, GT/LGT, and Root checks apply."
        ],
        "return_to_root_reasoning": [
            "Provider semantics return to Root for final boundary."
        ],
        "authority_boundary_reasoning": [
            "Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides."
        ],
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "root_bypass_claimed": False,
    }


def _branch_payload(role: str, branch_id: str) -> dict[str, Any]:
    return {
        "branch_semantic_proposal_id": f"{role}-semantic-001",
        "source_branch_id": branch_id,
        "semantic_summary": f"{branch_id} semantic observation remains advisory.",
        "evidence_interpretation": "Evidence supports bounded Root review only.",
        "uncertainty_notes": ["Manual live observation does not create authority."],
        "recommended_branch_status": "accepted_for_parent_review",
        "return_to_parent_reasoning": "Branch returns to parent/root boundary.",
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "action_commit_packet_claimed": False,
        "receipt_claimed": False,
        "payment_execution_claimed": False,
        "shipment_release_claimed": False,
    }


def _fake_provider(
    role: str, _prompt: str, context: Mapping[str, Any]
) -> str:
    if role == "top_level_orchestrator_llm":
        return json.dumps(_orchestrator_payload())
    if role == "top_level_semantic_architect_llm":
        return json.dumps(_architect_payload())
    return json.dumps(_branch_payload(role, str(context["source_branch_id"])))


def _invalid_branch_provider(
    role: str, prompt: str, context: Mapping[str, Any]
) -> str:
    payload = json.loads(_fake_provider(role, prompt, context))
    if role == "legal_clause_semantic_extractor":
        payload["authority_claimed"] = True
    return json.dumps(payload)


def _invalid_orchestrator_provider(
    role: str, _prompt: str, context: Mapping[str, Any]
) -> str:
    if role == "top_level_orchestrator_llm":
        return json.dumps({"proposal_id": "missing-required-fields"})
    return _fake_provider(role, _prompt, context)


def _pass_report() -> dict[str, Any]:
    return runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=_fake_provider
    )


def test_manual_live_multillm_orchestrator_prompt_has_exact_final_skeleton() -> None:
    prompt = runner._build_orchestrator_prompt()
    skeleton = _final_json_skeleton(prompt)

    assert "OUTPUT_SHAPE_CONTRACT" in prompt
    assert set(skeleton) == runner.ORCHESTRATOR_REQUIRED_FIELDS
    assert skeleton["truth_claimed"] is False
    assert skeleton["authority_claimed"] is False
    assert skeleton["action_permission_claimed"] is False
    assert skeleton["final_output_claimed"] is False
    assert skeleton["connector_command_claimed"] is False
    assert skeleton["drs_write_claimed"] is False
    assert skeleton["plan_graph_claimed"] is False
    assert skeleton["bypass_root_claimed"] is False
    assert skeleton["root_review_required"] is True
    assert isinstance(skeleton["selected_branch_ids"], list)
    _assert_no_text_after_skeleton(prompt)


def test_manual_live_multillm_architect_prompt_has_exact_final_skeleton() -> None:
    bsep = runner._build_bsep(_orchestrator_payload())
    prompt = runner._build_architect_prompt(bsep)
    skeleton = _final_json_skeleton(prompt)

    assert "OUTPUT_SHAPE_CONTRACT" in prompt
    assert set(skeleton) == runner.ARCHITECT_REQUIRED_FIELDS
    for field in (
        "truth_claimed",
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
        "connector_command_claimed",
        "drs_write_claimed",
        "root_bypass_claimed",
    ):
        assert skeleton[field] is False
    assert isinstance(skeleton["selected_branch_ids"], list)
    _assert_no_text_after_skeleton(prompt)


def test_manual_live_multillm_branch_prompt_has_exact_final_skeleton() -> None:
    prompt = runner._build_branch_prompt(
        "legal_clause_semantic_extractor", "legal_branch"
    )
    skeleton = _final_json_skeleton(prompt)

    assert "OUTPUT_SHAPE_CONTRACT" in prompt
    assert set(skeleton) == runner.BRANCH_SEMANTIC_REQUIRED_FIELDS
    for field in (
        "truth_claimed",
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
        "connector_command_claimed",
        "action_commit_packet_claimed",
        "receipt_claimed",
        "payment_execution_claimed",
        "shipment_release_claimed",
    ):
        assert skeleton[field] is False
    assert skeleton["source_branch_id"] == "legal_branch"
    _assert_no_text_after_skeleton(prompt)


def test_manual_live_multillm_fractal_default_skipped_closed() -> None:
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={}
    )

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["stage_status"] == "SKIPPED_CLOSED"
    assert report["counters"]["manual_live_multillm_fractal_lane_enabled_count"] == 0
    assert all(value == 0 for value in report["counters"].values())


def test_manual_live_drs_v0_2_default_skipped_closed() -> None:
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={}
    )
    counters = report["counters"]

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert counters["manual_live_drs_v0_2_observation_enabled_count"] == 0
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 0
    assert counters["local_drs_v0_2_records_evaluated_count"] == 0
    assert counters["local_drs_v0_2_direct_reuse_allowed_count"] == 0
    assert counters["local_drs_v0_2_root_review_required_count"] == 0
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_manual_live_avf_v0_2_default_skipped_closed() -> None:
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={}
    )
    counters = report["counters"]

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert counters["manual_live_drs_v0_2_observation_enabled_count"] == 0
    assert counters["manual_live_avf_v0_2_observation_enabled_count"] == 0
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 0
    assert counters["avf_v0_2_evaluation_invoked_count"] == 0
    assert counters["avf_v0_2_candidates_evaluated_count"] == 0
    assert counters["avf_v0_2_action_permission_granted_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_live_lane_action_corridor_default_skipped_closed() -> None:
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={}
    )
    counters = report["counters"]

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["action_commit_packet_v0_2_integration"]["status"] == "not_run"
    assert report["mock_bank_sandbox_v0_2_corridor_execution"]["status"] == "not_run"
    assert counters["action_commit_packet_v0_2_integration_invoked_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_corridor_invoked_count"] == 0


def test_manual_live_multillm_fractal_fake_provider_returns_pass() -> None:
    report = _pass_report()
    counters = report["counters"]

    assert report["final_status"] == "PASS"
    assert report["stage_status"] == "PASS"
    assert counters["semantic_actor_call_count"] == 6
    assert counters["fake_provider_call_count"] == 6
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0


def test_live_lane_action_corridor_fake_provider_pass() -> None:
    report = _pass_report()
    counters = report["counters"]

    assert report["final_status"] == "PASS"
    assert counters["semantic_actor_call_count"] == 6
    assert counters["fake_provider_call_count"] == 6
    assert counters["real_provider_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert report["action_commit_packet_v0_2_integration"]["status"] == "PASS"
    assert report["mock_bank_sandbox_v0_2_corridor_execution"]["status"] == "PASS"
    assert counters["action_commit_packet_v0_2_integration_invoked_count"] == 1
    assert counters["action_commit_packet_v0_2_root_created_model_packet_count"] == 1
    assert counters["action_commit_packet_v0_2_packet_corridor_entry_validated_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_corridor_invoked_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_provider_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_network_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_gemini_called_count"] == 0


def test_manual_live_drs_v0_2_fake_provider_pass_observes_drs() -> None:
    report = _pass_report()
    counters = report["counters"]

    assert report["final_status"] == "PASS"
    assert report["local_drs_v0_2_observation"]["local_drs_v0_2_status"] == "PASS"
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 1
    assert counters["local_drs_v0_2_records_evaluated_count"] == 11
    assert counters["local_drs_v0_2_direct_reuse_allowed_count"] == 0
    assert counters["local_drs_v0_2_root_review_required_count"] == 11
    assert counters["semantic_actor_call_count"] == 6
    assert counters["fake_provider_call_count"] == 6
    assert counters["root_final_boundary_evaluated_count"] == 1


def test_manual_live_avf_v0_2_fake_provider_pass_observes_avf() -> None:
    report = _pass_report()
    counters = report["counters"]

    assert report["final_status"] == "PASS"
    assert report["avf_v0_2_observation"]["avf_v0_2_status"] == "PASS"
    assert counters["avf_v0_2_evaluation_invoked_count"] == 1
    assert counters["avf_v0_2_candidates_evaluated_count"] == 9
    assert counters["avf_v0_2_top_ranked_candidate_permission_granted_count"] == 0
    assert counters["avf_v0_2_action_permission_granted_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert counters["avf_v0_2_action_commit_packet_created_count"] == 0
    assert counters["avf_v0_2_receipt_created_count"] == 0
    assert counters["avf_v0_2_payment_executed_count"] == 0
    assert counters["avf_v0_2_shipment_released_count"] == 0
    assert counters["avf_v0_2_root_bypass_count"] == 0
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 1
    assert counters["semantic_actor_call_count"] == 6
    assert counters["fake_provider_call_count"] == 6
    assert counters["root_final_boundary_evaluated_count"] == 1


def test_manual_live_avf_v0_2_candidate_observations_visible() -> None:
    observation = _pass_report()["avf_v0_2_observation"]
    rows = {
        row["candidate_id"]: row
        for row in observation["ranked_candidates"]
    }
    decisions = {
        row["candidate_id"]: row
        for row in observation["decision_reports_summary"]
    }

    assert set(rows) == REQUIRED_AVF_CANDIDATES
    assert observation["candidate_observations"]["release_all_and_pay_all"][
        "hard_masked"
    ] is True
    assert rows["release_all_and_pay_all"]["final_avf_score"] == 0.0
    assert observation["candidate_observations"]["pay_supplier_b"][
        "hard_masked"
    ] is True
    assert rows["pay_supplier_b"]["final_avf_score"] == 0.0
    for candidate_id in (
        "prepare_supplier_a_payment_form_only",
        "request_fresh_warehouse_validation",
        "request_fresh_legal_accounting_validation",
        "keep_shipment_held",
        "root_review_only",
        "block_supplier_b_and_hold_shipment",
    ):
        assert rows[candidate_id]["final_avf_score"] >= 0.0
        assert decisions[candidate_id]["approved"] is False
        assert decisions[candidate_id]["execute"] is False
        assert decisions[candidate_id]["payment_allowed"] is False
        assert decisions[candidate_id]["shipment_release_allowed"] is False
        assert decisions[candidate_id]["final_decision"] is False


def test_manual_live_avf_v0_2_top_ranked_candidate_not_permission() -> None:
    report = _pass_report()
    observation = report["avf_v0_2_observation"]
    top_id = observation["top_candidate_id"]
    decisions = {
        row["candidate_id"]: row
        for row in observation["decision_reports_summary"]
    }

    assert top_id is not None
    assert report["counters"]["avf_v0_2_top_ranked_candidate_permission_granted_count"] == 0
    assert decisions[top_id]["approved"] is False
    assert decisions[top_id]["execute"] is False
    assert decisions[top_id]["payment_allowed"] is False
    assert decisions[top_id]["shipment_release_allowed"] is False
    assert decisions[top_id]["final_decision"] is False


def test_manual_live_drs_v0_2_regression_scenarios_visible() -> None:
    observation = _pass_report()["local_drs_v0_2_observation"]

    assert set(observation["baseline_regression_scenario_ids"]) == REQUIRED_DRS_SCENARIOS
    assert set(observation["decisions_summary"]) == REQUIRED_DRS_SCENARIOS


def test_manual_live_drs_v0_2_old_receipt_not_permission() -> None:
    report = _pass_report()
    decision = report["local_drs_v0_2_observation"]["decisions_summary"][
        "old_receipt_trace"
    ]
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )

    assert "old_receipt_not_permission" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False
    assert "old receipt is not current permission" in rendered


def test_manual_live_drs_v0_2_old_root_final_not_silent_reuse() -> None:
    report = _pass_report()
    decision = report["local_drs_v0_2_observation"]["decisions_summary"][
        "old_root_final_trace"
    ]
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )

    assert "prior_root_final_not_silent_reuse" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False
    assert "old Root Final is not silently reused" in rendered


def test_manual_live_drs_v0_2_changed_facts_require_rerun() -> None:
    decision = _pass_report()["local_drs_v0_2_observation"]["decisions_summary"][
        "changed_warehouse_fact"
    ]

    assert decision["reuse_decision_class"] == "rerun_required"
    assert "changed_facts_require_rerun_validation" in decision["reason_codes"]
    assert decision["direct_reuse_allowed"] is False


def test_manual_live_drs_v0_2_quarantine_deadend_wrong_domain_permission_trace() -> None:
    decisions = _pass_report()["local_drs_v0_2_observation"]["decisions_summary"]

    assert decisions["quarantined_record"]["reuse_decision_class"] == "blocked"
    assert decisions["deadend_record"]["reuse_decision_class"] in {
        "blocked",
        "warning_only",
    }
    assert decisions["wrong_domain_near_match"]["reuse_decision_class"] in {
        "rerun_required",
        "blocked",
    }
    assert decisions["permission_trace_completed_action_attempt"][
        "reuse_decision_class"
    ] in {"rerun_required", "blocked"}
    for decision in decisions.values():
        assert decision["direct_reuse_allowed"] is False


def test_manual_live_drs_v0_2_orchestrator_prompt_has_bounded_drs_context() -> None:
    prompts: list[str] = []

    def capturing_provider(
        role: str, prompt: str, context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            prompts.append(prompt)
        return _fake_provider(role, prompt, context)

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=capturing_provider
    )
    prompt = prompts[0]

    assert report["final_status"] == "PASS"
    assert "local_drs_v0_2_bounded_context" in prompt
    assert '"direct_reuse_allowed_count": 0' in prompt
    assert '"root_review_required_count": 11' in prompt
    assert "Local DRS v0.2 context is advisory context only." in prompt
    assert "DRS v0.2 is not truth." in prompt
    assert "DRS v0.2 is not authority." in prompt
    assert "DRS v0.2 is not permission." in prompt
    assert "DRS hit is context only." in prompt
    for marker in SECRET_MARKERS:
        assert marker not in prompt
    assert "raw_iban_value" not in prompt
    assert "sandbox_token_abc" not in prompt
    assert "DRS grants" + " permission" not in prompt


def test_manual_live_avf_v0_2_orchestrator_prompt_has_bounded_avf_drs_context() -> None:
    prompts: list[str] = []

    def capturing_provider(
        role: str, prompt: str, context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            prompts.append(prompt)
        return _fake_provider(role, prompt, context)

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=capturing_provider
    )
    prompt = prompts[0]

    assert report["final_status"] == "PASS"
    assert "local_drs_v0_2_bounded_context" in prompt
    assert "avf_v0_2_bounded_context" in prompt
    assert '"direct_reuse_allowed_count": 0' in prompt
    assert '"root_review_required_count": 11' in prompt
    assert '"candidates_evaluated_count": 9' in prompt
    assert "release_all_and_pay_all" in prompt
    assert "pay_supplier_b" in prompt
    assert "Top-ranked AVF candidate is not permission." in prompt
    assert "AVF score is not authority." in prompt
    assert "HardMask is not Root." in prompt
    for raw_key in (
        "ranked_candidates",
        "hard_mask_table",
        "soft_mask_table",
        "score_explanation_table",
        "freshness_table",
        "lineage_table",
        "provenance_table",
        "reuse_decision_table",
    ):
        assert raw_key not in prompt
    for marker in SECRET_MARKERS:
        assert marker not in prompt
    assert "raw_iban_value" not in prompt
    assert "sandbox_token_abc" not in prompt
    assert "AVF grants" + " permission" not in prompt


def test_manual_live_drs_v0_2_bsep_contains_bounded_drs_context() -> None:
    report = _pass_report()
    bsep = report["bsep_packet"]
    bsep_text = json.dumps(bsep, sort_keys=True)

    assert report["bsep_validation"]["accepted"] is True
    assert bsep["local_drs_v0_2_resolve_invoked"] is True
    assert bsep["local_drs_v0_2_bounded_context"][
        "direct_reuse_allowed_count"
    ] == 0
    assert bsep["local_drs_v0_2_bounded_context"][
        "root_review_required_count"
    ] == 11
    assert bsep["raw_drs_authority_included"] is False
    assert bsep["raw_user_text_included"] is False
    assert bsep["raw_provider_text_included"] is False
    assert bsep["raw_bank_secrets_included"] is False
    for marker in SECRET_MARKERS:
        assert marker not in bsep_text


def test_manual_live_avf_v0_2_bsep_contains_bounded_avf_drs_context() -> None:
    report = _pass_report()
    bsep = report["bsep_packet"]
    bsep_text = json.dumps(bsep, sort_keys=True)

    assert report["bsep_validation"]["accepted"] is True
    assert bsep["local_drs_v0_2_resolve_invoked"] is True
    assert bsep["avf_v0_2_evaluation_invoked"] is True
    assert bsep["local_drs_v0_2_bounded_context"][
        "direct_reuse_allowed_count"
    ] == 0
    assert bsep["local_drs_v0_2_bounded_context"][
        "root_review_required_count"
    ] == 11
    avf_context = bsep["avf_v0_2_bounded_context"]
    assert avf_context["candidates_evaluated_count"] == 9
    assert avf_context["candidate_observations"]["release_all_and_pay_all"][
        "hard_masked"
    ] is True
    assert avf_context["candidate_observations"]["pay_supplier_b"][
        "hard_masked"
    ] is True
    assert "top-ranked AVF candidate is not permission." in bsep[
        "bounded_business_context"
    ]
    assert "AVF score is not authority." in bsep["bounded_business_context"]
    assert bsep["raw_avf_tables_included"] is False
    assert bsep["raw_drs_tables_included"] is False
    assert bsep["raw_user_text_included"] is False
    assert bsep["raw_provider_text_included"] is False
    assert bsep["raw_bank_secrets_included"] is False
    for raw_key in (
        "ranked_candidates",
        "hard_mask_table",
        "soft_mask_table",
        "score_explanation_table",
        "freshness_table",
        "lineage_table",
        "provenance_table",
        "reuse_decision_table",
    ):
        assert raw_key not in bsep_text
    for marker in SECRET_MARKERS:
        assert marker not in bsep_text


def test_live_lane_action_corridor_bsep_does_not_include_raw_action_tables() -> None:
    report = _pass_report()
    bsep = report["bsep_packet"]
    bsep_text = json.dumps(bsep, sort_keys=True)

    assert report["final_status"] == "PASS"
    assert bsep["raw_drs_tables_included"] is False
    assert bsep["raw_avf_tables_included"] is False
    assert bsep["raw_bank_secrets_included"] is False
    assert bsep["action_permission_included"] is False
    assert bsep["final_output_included"] is False
    for raw_key in (
        "ActionCommitPacketV02",
        "MockReceiptEvidenceV01",
        "mock_payment_order",
        "mock_receipt_evidence",
        "terminal_receipt_packet_ids",
        "used_idempotency_keys",
        "action_commit_packet_v0_2_integration",
        "mock_bank_sandbox_v0_2_corridor_execution",
    ):
        assert raw_key not in bsep_text
    for marker in SECRET_MARKERS:
        assert marker not in bsep_text


def test_manual_live_drs_v0_2_bsep_contains_resolve_invoked_true() -> None:
    bsep = _pass_report()["bsep_packet"]

    assert bsep["local_drs_v0_2_resolve_invoked"] is True


def test_manual_live_drs_v0_2_bsep_contains_direct_reuse_zero() -> None:
    bsep = _pass_report()["bsep_packet"]

    assert bsep["local_drs_v0_2_bounded_context"][
        "direct_reuse_allowed_count"
    ] == 0


def test_manual_live_drs_v0_2_bsep_contains_root_review_required_count() -> None:
    bsep = _pass_report()["bsep_packet"]

    assert bsep["local_drs_v0_2_bounded_context"][
        "root_review_required_count"
    ] == 11


def test_manual_live_drs_v0_2_bsep_does_not_contain_raw_drs_tables() -> None:
    bsep_text = json.dumps(_pass_report()["bsep_packet"], sort_keys=True)

    for raw_key in (
        "freshness_table",
        "lineage_table",
        "provenance_table",
        "reuse_decision_table",
        "physical_time",
        "knowledge_time",
        "source_observed_at",
        "system_ingested_at",
        "artifact_refs",
        "validation_refs",
    ):
        assert raw_key not in bsep_text


def test_manual_live_drs_v0_2_bsep_does_not_contain_drs_authority() -> None:
    bsep = _pass_report()["bsep_packet"]
    bsep_text = json.dumps(bsep, sort_keys=True)

    assert bsep["raw_drs_authority_included"] is False
    for forbidden in (
        "raw_drs_authority_included true",
        "DRS grants" + " permission",
        "DRS" + " decides",
        "DRS is" + " authority",
        "DRS hit is" + " truth",
        "Root" + " bypass",
    ):
        assert forbidden not in bsep_text


def test_manual_live_drs_v0_2_writeback_candidate_after_root() -> None:
    report = _pass_report()
    counters = report["counters"]
    candidate = report["local_drs_v0_2_writeback_candidate"]

    assert candidate["source_root_boundary_evaluated"] is True
    assert candidate["direct_reuse_allowed"] is False
    assert candidate["future_permission_created"] is False
    assert candidate["local_proof_audit_only"] is True
    assert candidate["payment_executed"] is False
    assert candidate["shipment_released"] is False
    assert candidate["receipt_created"] is False
    assert candidate["action_commit_packet_created"] is False
    assert candidate["production_persisted"] is False
    assert candidate["persisted_to_global_drs"] is False
    assert counters["local_drs_v0_2_writeback_candidate_created_count"] == 1
    assert counters["local_drs_v0_2_writeback_persisted_count"] == 0
    assert counters["local_drs_v0_2_writeback_local_proof_only_count"] == 1


def test_manual_live_drs_writeback_candidate_cannot_create_action_permission() -> None:
    candidate = dict(_pass_report()["local_drs_v0_2_writeback_candidate"])
    candidate["action_permission_created"] = True

    validation = runner.validate_local_drs_v0_2_writeback_candidate(candidate)

    assert validation["accepted"] is False
    assert "required_false_field:action_permission_created" in validation["errors"]


def test_manual_live_drs_writeback_candidate_cannot_create_final_output() -> None:
    candidate = dict(_pass_report()["local_drs_v0_2_writeback_candidate"])
    candidate["final_output_created_by_drs"] = True

    validation = runner.validate_local_drs_v0_2_writeback_candidate(candidate)

    assert validation["accepted"] is False
    assert "required_false_field:final_output_created_by_drs" in validation["errors"]


def test_manual_live_drs_writeback_candidate_cannot_persist_production_record() -> None:
    candidate = dict(_pass_report()["local_drs_v0_2_writeback_candidate"])
    candidate["production_persisted"] = True
    candidate["persisted_to_global_drs"] = True

    validation = runner.validate_local_drs_v0_2_writeback_candidate(candidate)

    assert validation["accepted"] is False
    assert "required_false_field:production_persisted" in validation["errors"]
    assert "required_false_field:persisted_to_global_drs" in validation["errors"]


def test_manual_live_drs_writeback_candidate_before_root_rejected() -> None:
    report = _pass_report()
    candidate = dict(report["local_drs_v0_2_writeback_candidate"])
    candidate["source_root_boundary_evaluated"] = False

    validation = runner.validate_local_drs_v0_2_writeback_candidate(candidate)

    assert report["counters"]["root_final_boundary_evaluated_count"] == 1
    assert report["counters"]["local_drs_v0_2_writeback_candidate_created_count"] == 1
    assert validation["accepted"] is False
    assert "required_true_field:source_root_boundary_evaluated" in validation["errors"]


def test_manual_live_multillm_fractal_role_sequence() -> None:
    sequence = _pass_report()["pipeline_sequence"]
    positions = [sequence.index(item) for item in REQUIRED_SEQUENCE_SUBSET]

    assert positions == sorted(positions)


def test_live_lane_action_corridor_sequence_order() -> None:
    sequence = _pass_report()["pipeline_sequence"]

    assert sequence.index("local_drs_v0_2_resolve_invoked") < sequence.index(
        "avf_v0_2_evaluation_invoked"
    )
    assert sequence.index("avf_v0_2_evaluation_invoked") < sequence.index(
        "top_level_orchestrator_provider_called"
    )
    assert sequence.index("root_final_boundary_evaluated") < sequence.index(
        "action_commit_packet_v0_2_integration_invoked"
    )
    assert sequence.index(
        "action_commit_packet_v0_2_packet_seen_recorded"
    ) < sequence.index("mock_bank_sandbox_v0_2_corridor_invoked")
    assert sequence.index(
        "mock_bank_sandbox_v0_2_mock_payment_order_created"
    ) < sequence.index("mock_bank_sandbox_v0_2_mock_receipt_evidence_created")


def test_manual_live_multillm_fractal_bsep_before_architect() -> None:
    report = _pass_report()
    counters = report["counters"]
    sequence = report["pipeline_sequence"]

    assert counters["bsep_created_count"] == 1
    assert counters["bsep_validated_count"] == 1
    assert counters["architect_called_before_bsep_validation_count"] == 0
    assert counters["architect_received_bsep_context_count"] == 1
    assert sequence.index("bsep_validated") < sequence.index(
        "top_level_architect_provider_called"
    )


def test_manual_live_multillm_fractal_branch_actors_present() -> None:
    report = _pass_report()
    branches = {branch["branch_id"]: branch for branch in report["fractal_branches"]}

    assert report["counters"]["branch_local_llm_slm_call_count"] == 4
    for branch_id in (
        "legal_branch",
        "accounting_branch",
        "supplier_b_branch",
        "bank_b_branch",
    ):
        output = branches[branch_id]["branch_semantic_actor_output"]
        assert output is not None
        assert output["truth_claimed"] is False
        assert output["authority_claimed"] is False
        assert output["action_permission_claimed"] is False
        assert output["final_output_claimed"] is False
        assert output["action_commit_packet_claimed"] is False
        assert output["receipt_claimed"] is False
        assert output["payment_execution_claimed"] is False
        assert output["shipment_release_claimed"] is False


def test_manual_live_multillm_fractal_runtime_owns_plangraph() -> None:
    counters = _pass_report()["counters"]

    assert counters["runtime_plangraph_compiled_count"] == 1
    assert counters["provider_owned_plangraph_count"] == 0
    assert counters["provider_nodes_edges_executor_assignments_accepted_count"] == 0


def test_manual_live_multillm_fractal_secret_membrane() -> None:
    report = _pass_report()
    counters = report["counters"]
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )

    assert counters["llm_visible_raw_iban_count"] == 0
    assert counters["llm_visible_bank_token_count"] == 0
    assert counters["llm_visible_secret_count"] == 0
    assert report["secret_membrane"]["prompt_secret_scan_passed"] is True
    assert report["secret_membrane"]["artifact_secret_scan_passed"] is True
    assert "Secrets ∩ LLMContext = empty" in rendered


def test_manual_live_multillm_fractal_no_execution_or_effects() -> None:
    counters = _pass_report()["counters"]

    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_live_lane_action_commit_packet_boundaries() -> None:
    report = _pass_report()
    counters = report["counters"]
    packet = report["action_commit_packet_v0_2_integration"]

    assert packet["status"] == "PASS"
    assert packet["created_by"] == "root"
    assert packet["root_created"] is True
    assert packet["human_approval_is_scoped_evidence_only"] is True
    assert counters["action_commit_packet_v0_2_created_by_root_count"] == 1
    assert counters["action_commit_packet_v0_2_created_by_human_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_llm_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_drs_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_avf_count"] == 0
    assert counters["action_commit_packet_v0_2_created_by_gt_lgt_count"] == 0
    assert "supplier_a_adriatic_filters" in packet["allowed_subjects"]
    assert "supplier_b_balkan_pumps" in packet["forbidden_subjects"]
    assert "shipment_sh_2042" in packet["forbidden_subjects"]
    assert "real_bank" in packet["forbidden_adapters"]
    assert "real_supplier_api" in packet["forbidden_adapters"]
    assert "real_warehouse_api" in packet["forbidden_adapters"]
    assert packet["registry_is_local_proof_only"] is True
    assert packet["registry_is_not_drs"] is True
    assert packet["registry_is_not_authority"] is True
    assert packet["registry_is_not_permission"] is True


def test_live_lane_mock_bank_corridor_boundaries() -> None:
    report = _pass_report()
    counters = report["counters"]
    corridor = report["mock_bank_sandbox_v0_2_corridor_execution"]
    receipt = corridor["mock_receipt_evidence"]

    assert corridor["status"] == "PASS"
    assert counters["mock_bank_sandbox_v0_2_mock_payment_intent_created_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_mock_payment_consent_created_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_mock_payment_order_created_count"] == 1
    assert counters["mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count"] == 1
    assert receipt["evidence_only"] is True
    assert counters["mock_bank_sandbox_v0_2_receipt_permission_created_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_future_permission_created_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_final_output_created_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_shipment_release_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_receipt_production_drs_write_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_bank_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_supplier_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_warehouse_api_called_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_payment_executed_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_shipment_released_count"] == 0
    assert counters["mock_bank_sandbox_v0_2_real_world_effects_count"] == 0


def test_manual_live_drs_v0_2_no_real_execution_or_effects() -> None:
    counters = _pass_report()["counters"]

    assert counters["local_drs_v0_2_permission_granted_count"] == 0
    assert counters["local_drs_v0_2_external_drs_used_count"] == 0
    assert counters["local_drs_v0_2_global_drs_used_count"] == 0
    assert counters["local_drs_v0_2_vector_db_used_count"] == 0
    assert counters["local_drs_v0_2_embeddings_required_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_manual_live_avf_v0_2_no_real_execution_or_effects() -> None:
    counters = _pass_report()["counters"]

    assert counters["avf_v0_2_action_permission_granted_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert counters["avf_v0_2_action_commit_packet_created_count"] == 0
    assert counters["avf_v0_2_receipt_created_count"] == 0
    assert counters["avf_v0_2_payment_executed_count"] == 0
    assert counters["avf_v0_2_shipment_released_count"] == 0
    assert counters["avf_v0_2_root_bypass_count"] == 0
    assert counters["avf_v0_2_provider_called_count"] == 0
    assert counters["avf_v0_2_network_called_count"] == 0
    assert counters["avf_v0_2_gemini_called_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_manual_live_drs_v0_2_no_new_semantic_actor() -> None:
    report = _pass_report()
    roles = {call["role"] for call in report["semantic_actor_calls"]}

    assert report["counters"]["semantic_actor_call_count"] == 6
    assert report["counters"]["branch_local_llm_slm_call_count"] == 4
    assert not any("drs" in role.lower() for role in roles)


def test_manual_live_avf_v0_2_no_new_semantic_actor() -> None:
    report = _pass_report()
    roles = {call["role"] for call in report["semantic_actor_calls"]}

    assert report["counters"]["semantic_actor_call_count"] == 6
    assert report["counters"]["branch_local_llm_slm_call_count"] == 4
    assert not any("avf" in role.lower() for role in roles)


def test_live_lane_action_corridor_no_new_semantic_actor() -> None:
    report = _pass_report()
    roles = {call["role"] for call in report["semantic_actor_calls"]}

    assert report["counters"]["semantic_actor_call_count"] == 6
    assert "action_commit_packet_actor" not in roles
    assert "mock_bank_sandbox_actor" not in roles
    assert "bank_b_hedgehog_native_actor" not in roles
    assert not any("action_commit_packet" in role for role in roles)
    assert not any("mock_bank_sandbox" in role for role in roles)


def test_manual_live_drs_v0_2_no_authority_or_permission() -> None:
    report = _pass_report()
    counters = report["counters"]
    matrix = report["authority_matrix"]
    decisions = report["local_drs_v0_2_observation"]["reuse_decision_table"]

    assert counters["local_drs_v0_2_permission_granted_count"] == 0
    assert counters["local_drs_v0_2_root_bypass_count"] == 0
    for row in decisions:
        assert row["truth_claimed"] is False
        assert row["authority_claimed"] is False
        assert row["action_permission_claimed"] is False
        assert row["final_output_claimed"] is False
    for fact in (
        "DRS v0.2 is not truth.",
        "DRS v0.2 is not authority.",
        "DRS v0.2 is not permission.",
        "DRS hit is context only.",
        "DRS v0.2 reuse decision is not FinalOutput.",
        "DRS v0.2 direct reuse candidate is not direct reuse.",
        "old receipt is not current permission.",
        "old Root Final is not silently reused.",
        "permission trace cannot become completed action.",
        "ReuseScore is not Root.",
        "Semantic similarity is not authority.",
        "DRS writeback after Root is local proof/audit only.",
        "Root remains final authority.",
    ):
        assert fact in matrix


def test_manual_live_avf_v0_2_no_authority_or_permission() -> None:
    report = _pass_report()
    counters = report["counters"]
    matrix = report["authority_matrix"]
    decisions = report["avf_v0_2_observation"]["decision_reports_summary"]

    assert counters["avf_v0_2_action_permission_granted_count"] == 0
    assert counters["avf_v0_2_final_output_created_count"] == 0
    assert counters["avf_v0_2_root_bypass_count"] == 0
    for row in decisions:
        explanation = row["score_explanation"]
        assert explanation["truth_claimed"] is False
        assert explanation["authority_claimed"] is False
        assert explanation["action_permission_claimed"] is False
        assert explanation["final_output_claimed"] is False
        assert row["approved"] is False
        assert row["execute"] is False
        assert row["payment_allowed"] is False
        assert row["shipment_release_allowed"] is False
        assert row["final_decision"] is False
    for fact in (
        "AVF v0.2 is not truth.",
        "AVF v0.2 is not authority.",
        "AVF v0.2 is not permission.",
        "AVF score is not Root.",
        "Top-ranked AVF candidate is not permission.",
        "CandidateVector is not action permission.",
        "CandidateVector is not FinalOutput.",
        "HardMask is not Root.",
        "High score does not override HardMask.",
        "Top rank does not override HardMask.",
        "Safe rank remains advisory.",
        "AVF cannot bypass Root.",
        "AVF cannot create FinalOutput.",
        "AVF cannot create ActionCommitPacket.",
        "AVF cannot create receipt.",
        "AVF cannot execute payment.",
        "AVF cannot release shipment.",
        "Root remains final authority.",
    ):
        assert fact in matrix


def test_live_lane_action_corridor_no_post_root_reasoning_or_authority() -> None:
    matrix = _pass_report()["authority_matrix"]

    assert "No post-Root reasoning restart." in matrix
    assert "MockBankSandbox does not decide." in matrix
    assert "MockBankSandbox does not create authority." in matrix
    assert "Mock receipt is not permission." in matrix
    assert "Root remains final authority." in matrix


def test_manual_live_multillm_fractal_invalid_branch_actor_fails_closed() -> None:
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=_invalid_branch_provider
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert counters["semantic_actor_call_count"] == 3
    assert counters["fake_provider_call_count"] == 3
    assert counters["branch_local_llm_slm_call_count"] == 1
    assert counters["root_final_boundary_evaluated_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_manual_live_multillm_fractal_provider_exception_fails_closed() -> None:
    def raising_provider(
        role: str, _prompt: str, _context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            raise RuntimeError("provider unavailable with hidden details")
        return json.dumps(_branch_payload(role, "unused"))

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=raising_provider
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["stage_status"] == "FAIL_CLOSED"
    assert report["skip_reason"] == "provider_call_failed:top_level_orchestrator_llm"
    assert counters["semantic_actor_call_count"] == 1
    assert counters["fake_provider_call_count"] == 1
    assert counters["root_final_boundary_evaluated_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_manual_live_multillm_fractal_real_provider_exception_fails_closed_without_network(
    monkeypatch: Any,
) -> None:
    dummy_key = "DUMMY_TEST_KEY_SHOULD_NOT_RENDER"

    def raising_real_provider(*_args: Any, **_kwargs: Any) -> str:
        raise RuntimeError("real provider unavailable with hidden details")

    monkeypatch.setattr(runner, "_call_real_provider", raising_real_provider)
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={runner.ENABLE_ENV: "1", "GEMINI_API_KEY": dummy_key},
        provider=None,
    )
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["stage_status"] == "FAIL_CLOSED"
    assert report["skip_reason"] == "provider_call_failed:top_level_orchestrator_llm"
    assert counters["semantic_actor_call_count"] == 1
    assert counters["real_provider_call_count"] == 1
    assert counters["network_used_count"] == 1
    assert counters["gemini_called_count"] == 1
    assert counters["root_final_boundary_evaluated_count"] == 0
    assert dummy_key not in rendered


def test_config_key_detection_accepts_env_google_gemini_key() -> None:
    env = {runner.ENABLE_ENV: "1", "GOOGLE_GEMINI_API_KEY": "test-key"}

    assert runner._live_gemini_config_available(env) is True
    assert (
        runner._config_value_from_env_or_config(
            env,
            "GOOGLE_GEMINI_API_KEY",
        )
        == "test-key"
    )


def test_config_key_detection_accepts_config_module(monkeypatch: Any) -> None:
    config_module = SimpleNamespace()
    setattr(config_module, "GOOGLE_API_KEY", "test-config-key")
    monkeypatch.setitem(sys.modules, "config", config_module)
    env = {runner.ENABLE_ENV: "1"}

    assert runner._live_gemini_config_available(env) is True
    assert (
        runner._config_value_from_env_or_config(
            env,
            "GOOGLE_API_KEY",
        )
        == "test-config-key"
    )


def test_missing_key_still_skips_closed_when_no_env_and_no_config(
    monkeypatch: Any,
) -> None:
    monkeypatch.setitem(sys.modules, "config", SimpleNamespace())
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={runner.ENABLE_ENV: "1"},
        provider=None,
    )

    assert report["final_status"] == "SKIPPED_CLOSED"
    assert report["provider_mode"] == "missing_key"
    assert "Gemini key missing" in report["skip_reason"]
    assert report["provider_error_kind"] == "missing_gemini_api_key"
    assert report["provider_error_sanitized"] == "missing_gemini_api_key"
    assert report["counters"]["real_provider_call_count"] == 0
    assert report["counters"]["network_used_count"] == 0
    assert report["counters"]["gemini_called_count"] == 0


def test_provider_failure_reports_sanitized_error_kind(monkeypatch: Any) -> None:
    def raising_real_provider(*_args: Any, **_kwargs: Any) -> str:
        raise RuntimeError("boom SECRET test-key should not leak")

    monkeypatch.setattr(runner, "_call_real_provider", raising_real_provider)
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={runner.ENABLE_ENV: "1", "GOOGLE_API_KEY": "test-key"},
        provider=None,
    )
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )
    report_json = json.dumps(report, sort_keys=True)

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["failed_role"] == "top_level_orchestrator_llm"
    assert report["failed_stage"] == "provider_call"
    assert report["provider_error_kind"] == "RuntimeError"
    assert report["provider_error_sanitized"]
    assert "test-key" not in rendered
    assert "test-key" not in report_json
    for marker in SECRET_MARKERS:
        assert marker not in rendered
        assert marker not in report_json


def test_manual_live_multillm_orchestrator_validation_failure_writes_artifacts(
    tmp_path: Path,
) -> None:
    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=_invalid_orchestrator_provider
    )
    counters = report["counters"]
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["skip_reason"] == "orchestrator_validation_failed"
    assert counters["semantic_actor_call_count"] == 1
    assert counters["fake_provider_call_count"] == 1
    assert counters["top_level_orchestrator_llm_call_count"] == 1
    assert counters["bsep_created_count"] == 0
    assert counters["root_final_boundary_evaluated_count"] == 0
    assert report["artifacts"]["artifact_capture_enabled"] is True
    assert "validation_errors" in rendered
    assert "missing_required_field" in rendered
    for artifact_name in (
        "summary.json",
        "summary.log",
        "secret_scan.json",
        "top_level_orchestrator_prompt.txt",
        "top_level_orchestrator_raw_response.txt",
        "top_level_orchestrator_extracted_json_candidate.json",
        "top_level_orchestrator_validation.json",
    ):
        assert (tmp_path / artifact_name).exists()
    json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    json.loads((tmp_path / "secret_scan.json").read_text(encoding="utf-8"))


def test_manual_live_multillm_provider_exception_failure_writes_artifacts(
    tmp_path: Path,
) -> None:
    unsafe_exception_text = "UNSAFE_EXCEPTION_DETAIL"

    def raising_provider(
        role: str, _prompt: str, _context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            raise RuntimeError(unsafe_exception_text)
        return json.dumps(_branch_payload(role, "unused"))

    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=raising_provider
    )
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        report
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert report["skip_reason"] == "provider_call_failed:top_level_orchestrator_llm"
    assert counters["semantic_actor_call_count"] == 1
    assert counters["fake_provider_call_count"] == 1
    assert counters["root_final_boundary_evaluated_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["mock_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0
    assert report["artifacts"]["artifact_capture_enabled"] is True
    assert unsafe_exception_text not in rendered
    for artifact_name in (
        "summary.json",
        "summary.log",
        "secret_scan.json",
        "top_level_orchestrator_prompt.txt",
        "top_level_orchestrator_raw_response.txt",
        "top_level_orchestrator_extracted_json_candidate.json",
        "top_level_orchestrator_validation.json",
    ):
        assert (tmp_path / artifact_name).exists()
    assert unsafe_exception_text not in (tmp_path / "summary.log").read_text(
        encoding="utf-8"
    )
    json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    json.loads((tmp_path / "secret_scan.json").read_text(encoding="utf-8"))


def test_manual_live_multillm_fractal_artifacts_written_with_fake_provider(
    tmp_path: Path,
) -> None:
    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=_fake_provider
    )

    assert report["final_status"] == "PASS"
    assert REQUIRED_ARTIFACTS <= {path.name for path in tmp_path.iterdir()}
    json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    for artifact_name in (
        "local_drs_v0_2_resolve_report.json",
        "local_drs_v0_2_freshness_table.json",
        "local_drs_v0_2_lineage_table.json",
        "local_drs_v0_2_provenance_table.json",
        "local_drs_v0_2_reuse_decision_table.json",
        "local_drs_v0_2_writeback_candidate.json",
        "avf_v0_2_evaluation_report.json",
        "avf_v0_2_ranked_candidates.json",
        "avf_v0_2_hard_mask_table.json",
        "avf_v0_2_soft_mask_table.json",
        "avf_v0_2_score_explanation_table.json",
    ):
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))
    secret_scan = json.loads(
        (tmp_path / "secret_scan.json").read_text(encoding="utf-8")
    )
    assert secret_scan["passed"] is True
    for path in tmp_path.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in SECRET_MARKERS:
                assert marker not in text


def test_live_lane_action_corridor_artifacts_written(tmp_path: Path) -> None:
    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=_fake_provider
    )
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))

    action_artifacts = {
        "action_commit_packet_v0_2_integration.json",
        "action_commit_packet_v0_2_packet_validation.json",
        "action_commit_packet_v0_2_registry_validation.json",
        "action_commit_packet_v0_2_corridor_entry_validation.json",
        "mock_bank_sandbox_v0_2_corridor_execution.json",
        "mock_bank_sandbox_v0_2_corridor_sequence.json",
        "mock_bank_sandbox_v0_2_mock_payment_intent.json",
        "mock_bank_sandbox_v0_2_mock_payment_consent.json",
        "mock_bank_sandbox_v0_2_mock_payment_order.json",
        "mock_bank_sandbox_v0_2_mock_receipt_evidence.json",
        "mock_bank_sandbox_v0_2_receipt_validation.json",
    }

    assert report["final_status"] == "PASS"
    assert action_artifacts <= {path.name for path in tmp_path.iterdir()}
    assert action_artifacts <= set(summary["artifacts"]["written_files"])
    for artifact_name in action_artifacts:
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))
    execution = json.loads(
        (tmp_path / "mock_bank_sandbox_v0_2_corridor_execution.json").read_text(
            encoding="utf-8"
        )
    )
    assert execution["status"] == "PASS"
    assert execution["receipt_evidence_only"] is True


def test_manual_live_drs_v0_2_artifacts_written(tmp_path: Path) -> None:
    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=_fake_provider
    )
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    resolve_report = json.loads(
        (tmp_path / "local_drs_v0_2_resolve_report.json").read_text(
            encoding="utf-8"
        )
    )
    secret_scan = json.loads(
        (tmp_path / "secret_scan.json").read_text(encoding="utf-8")
    )

    assert report["final_status"] == "PASS"
    assert summary["final_status"] == "PASS"
    assert resolve_report["local_drs_v0_2_status"] == "PASS"
    assert resolve_report["records_evaluated_count"] == 11
    assert secret_scan["passed"] is True
    for path in tmp_path.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in SECRET_MARKERS:
                assert marker not in text


def test_manual_live_avf_v0_2_artifacts_written(tmp_path: Path) -> None:
    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}

    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=_fake_provider
    )
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    avf_report = json.loads(
        (tmp_path / "avf_v0_2_evaluation_report.json").read_text(
            encoding="utf-8"
        )
    )
    secret_scan = json.loads(
        (tmp_path / "secret_scan.json").read_text(encoding="utf-8")
    )

    assert report["final_status"] == "PASS"
    assert summary["final_status"] == "PASS"
    assert avf_report["avf_v0_2_status"] == "PASS"
    assert avf_report["candidates_evaluated_count"] == 9
    assert secret_scan["passed"] is True
    for artifact_name in (
        "avf_v0_2_evaluation_report.json",
        "avf_v0_2_ranked_candidates.json",
        "avf_v0_2_hard_mask_table.json",
        "avf_v0_2_soft_mask_table.json",
        "avf_v0_2_score_explanation_table.json",
        "local_drs_v0_2_resolve_report.json",
        "local_drs_v0_2_reuse_decision_table.json",
    ):
        assert (tmp_path / artifact_name).exists()
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))
    for path in tmp_path.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in SECRET_MARKERS:
                assert marker not in text


def test_manual_live_drs_v0_2_fail_closed_writes_available_drs_artifacts(
    tmp_path: Path,
) -> None:
    def raising_provider(
        role: str, _prompt: str, _context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            raise RuntimeError("hidden provider detail")
        return json.dumps(_branch_payload(role, "unused"))

    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=raising_provider
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 1
    assert counters["local_drs_v0_2_records_evaluated_count"] == 11
    assert counters["local_drs_v0_2_writeback_candidate_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["real_world_effects_count"] == 0
    for artifact_name in (
        "local_drs_v0_2_resolve_report.json",
        "local_drs_v0_2_freshness_table.json",
        "local_drs_v0_2_lineage_table.json",
        "local_drs_v0_2_provenance_table.json",
        "local_drs_v0_2_reuse_decision_table.json",
    ):
        assert (tmp_path / artifact_name).exists()
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))
    writeback = json.loads(
        (tmp_path / "local_drs_v0_2_writeback_candidate.json").read_text(
            encoding="utf-8"
        )
    )
    assert writeback["status"] == "not_run"


def test_manual_live_avf_v0_2_fail_closed_writes_available_avf_artifacts(
    tmp_path: Path,
) -> None:
    def raising_provider(
        role: str, _prompt: str, _context: Mapping[str, Any]
    ) -> str:
        if role == "top_level_orchestrator_llm":
            raise RuntimeError("hidden provider detail")
        return json.dumps(_branch_payload(role, "unused"))

    env = {**ENABLED_ENV, runner.ARTIFACT_DIR_ENV: str(tmp_path)}
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env, provider=raising_provider
    )
    counters = report["counters"]

    assert report["final_status"] == "FAIL_CLOSED"
    assert counters["local_drs_v0_2_resolve_invoked_count"] == 1
    assert counters["avf_v0_2_evaluation_invoked_count"] == 1
    assert counters["avf_v0_2_candidates_evaluated_count"] == 9
    assert counters["local_drs_v0_2_writeback_candidate_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["receipt_created_count"] == 0
    assert counters["real_world_effects_count"] == 0
    for artifact_name in (
        "local_drs_v0_2_resolve_report.json",
        "local_drs_v0_2_reuse_decision_table.json",
        "avf_v0_2_evaluation_report.json",
        "avf_v0_2_ranked_candidates.json",
        "avf_v0_2_hard_mask_table.json",
        "avf_v0_2_soft_mask_table.json",
        "avf_v0_2_score_explanation_table.json",
    ):
        assert (tmp_path / artifact_name).exists()
        json.loads((tmp_path / artifact_name).read_text(encoding="utf-8"))
    writeback = json.loads(
        (tmp_path / "local_drs_v0_2_writeback_candidate.json").read_text(
            encoding="utf-8"
        )
    )
    assert writeback["status"] == "not_run"


def test_manual_live_multillm_fractal_rendered_sections() -> None:
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        _pass_report()
    )

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "FINAL STATUS: PASS" in rendered
    assert "DRS v0.2 read/resolve ran before Orchestrator." in rendered
    assert "DRS classified records as context/warning/rerun/blocked." in rendered
    assert "DRS did not authorize payment." in rendered
    assert "DRS did not authorize shipment release." in rendered
    assert "old receipt is not current permission." in rendered
    assert "old Root Final is not silently reused." in rendered
    assert "AVF v0.2 ran after Local DRS v0.2 and before Orchestrator." in rendered
    assert "AVF consumed Local DRS v0.2 candidate/reuse/risk signals." in rendered
    assert "release_all_and_pay_all was hard-masked." in rendered
    assert "Supplier B payment was hard-masked." in rendered
    assert "safe candidates may rank but do not grant permission." in rendered
    assert "top-ranked candidate is not permission." in rendered
    assert "AVF score is not authority." in rendered
    assert "HardMask is not Root." in rendered
    assert "AVF cannot bypass Root." in rendered
    assert "Root remains final authority." in rendered


def test_live_lane_action_corridor_rendered_sections() -> None:
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        _pass_report()
    )

    assert "[ACTIONCOMMITPACKET V0.2 LIVE OBSERVATION]" in rendered
    assert "[MOCKBANKSANDBOX V0.2 LIVE CONTRACT CORRIDOR OBSERVATION]" in rendered
    assert "Root created one scoped Supplier A ActionCommitPacket model." in rendered
    assert "Human approval is scoped evidence only." in rendered
    assert "LLM/DRS/AVF/GT-LGT did not create the packet." in rendered
    assert "Supplier B is excluded." in rendered
    assert "Shipment release is excluded." in rendered
    assert "MockBankSandbox consumed the scoped packet." in rendered
    assert "The corridor created mock intent/consent/order." in rendered
    assert "The corridor returned mock receipt evidence." in rendered
    assert "Receipt is evidence only." in rendered
    assert "Receipt did not create permission." in rendered
    assert "Receipt did not authorize Supplier B." in rendered
    assert "Receipt did not release shipment." in rendered
    assert "Root remains final authority." in rendered
    assert "No real-world effect occurred." in rendered


def test_manual_live_multillm_fractal_forbidden_overclaims() -> None:
    rendered = runner.render_full_wow_v1_2_manual_live_multillm_fractal_trace(
        _pass_report()
    )

    for left, right in FORBIDDEN_PHRASE_PARTS:
        assert left + right not in rendered


def test_manual_live_multillm_fractal_does_not_call_real_provider_in_tests(
    monkeypatch: Any,
) -> None:
    calls: list[str] = []

    def forbidden_real_provider(*_args: Any, **_kwargs: Any) -> str:
        calls.append("called")
        raise AssertionError("real provider must not be called in tests")

    monkeypatch.setattr(runner, "_call_real_provider", forbidden_real_provider)
    report = runner.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=ENABLED_ENV, provider=_fake_provider
    )
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert report["final_status"] == "PASS"
    assert calls == []
    assert "GEMINI_API_KEY" in source
    assert "GOOGLE_API_KEY" in source
    assert "_config_value_from_env_or_config" in source
    assert "_live_gemini_config_available" in source
    assert "GOOGLE_GEMINI_API_KEY" in source
    assert "if provider is None and not (" not in source


def test_live_lane_action_corridor_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "from hedgehog.local_drs_v02 import" in source
    assert "from hedgehog.avf_v02 import" in source
    assert "from hedgehog.action_commit_packet_v02 import" in source
    assert "run_full_wow_v1_2_product_trace" not in source
    assert "run_full_semantic_e2e_v01" not in source
    assert "run_supplier_payment_shipment_release_review_wow_v1_1" not in source
    assert "import ActionCommitPacket" not in source
    assert "from hedgehog.action_commit_packet import" not in source
    assert "hedgehog.mock_connector_sandbox" not in source
    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "call_real_bank" not in source
    assert "call_real_supplier" not in source
    assert "call_real_warehouse" not in source
    assert "airline" not in source.lower()
    assert "privacy" not in source.lower()
    for left, right in (
        ("authority flows", " upward"),
        ("adapter returns", " authority"),
        ("receipt returns", " authority"),
        ("bank returns", " authority"),
        ("corridor", " decides"),
        ("adapter", " decides"),
        ("post-Root reasoning", " restarts"),
        ("receipt grants", " permission"),
        ("receipt releases", " shipment"),
        ("human approval directly creates", " ActionCommitPacket"),
    ):
        forbidden = left + right
        assert forbidden not in source
