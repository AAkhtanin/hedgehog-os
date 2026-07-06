from __future__ import annotations

from pathlib import Path

from demo import run_human_full_wow_v1_1_final_walkthrough as runner


REQUIRED_STEP_IDS = {
    "dirty_request_received",
    "warehouse_scope_observed",
    "supplier_a_scope_observed",
    "supplier_b_blocker_observed",
    "legal_accounting_review_observed",
    "live_gemini_semantic_lane_observed",
    "bsep_membrane_observed",
    "drs_candidate_avf_observed",
    "semantic_architect_runtime_plan_boundary",
    "root_first_decision_not_ready",
    "corrected_evidence_second_run",
    "human_approval_scoped",
    "root_created_mock_packet_observed",
    "mock_bank_receipt_observed",
    "final_state_summary",
}

REQUIRED_CARD_FIELDS = {
    "step_id",
    "actor_or_module",
    "api_like_call_or_event",
    "input_summary",
    "output_summary",
    "meaning",
    "does_not_authorize",
    "next_step",
    "trace_or_evidence_id",
}

REQUIRED_SECTIONS = (
    "[FULL WOW V1.1 FINAL HUMAN WALKTHROUGH]",
    "[WHAT THIS DEMO SHOWS]",
    "[ACT 1 — DIRTY BUSINESS REQUEST]",
    "[ACT 2 — FIRST ROOT REVIEW: NOT_READY]",
    "[ACT 3 — SEMANTIC LIVE LANE: REAL GEMINI ORCHESTRATOR + BSEP + REAL GEMINI ARCHITECT]",
    "[ACT 4 — BUSINESS EVIDENCE BRANCHES]",
    "[ACT 5 — DRS / CANDIDATE VECTOR / AVF]",
    "[ACT 6 — SEMANTIC ARCHITECT AND RUNTIME PLAN ARTIFACTS]",
    "[ACT 7 — SECOND RUN: SUPPLIER A SCOPED REVIEW]",
    "[ACT 8 — HUMAN APPROVAL]",
    "[ACT 9 — ROOT-CREATED MOCK ACTIONCOMMITPACKET]",
    "[ACT 10 — MOCK BANK SANDBOX RECEIPT]",
    "[ACT 11 — FINAL AUTHORITY MATRIX]",
    "[COUNTER SUMMARY]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

REQUIRED_AUTHORITY_FACTS = {
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "BSEP is not truth.",
    "BSEP is not authority.",
    "DRS candidate context is not truth.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Semantic Architect is not Root.",
    "Runtime owns PlanGraph/local plan artifacts.",
    "PlanGraph is not authority.",
    "Human approval is scoped evidence only.",
    "Root-created mock ActionCommitPacket is scoped only.",
    "MockBankSandbox receipt is evidence only.",
    "Receipt does not release shipment.",
    "Root remains final authority.",
}

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
    ("v1.2 ", "implemented"),
    ("real_world_effects_count: ", "1"),
)


def _report() -> dict:
    return runner.collect_human_full_wow_v1_1_final_walkthrough()


def _rendered() -> str:
    return runner.render_human_full_wow_v1_1_final_walkthrough(_report())


def test_human_final_walkthrough_returns_pass() -> None:
    report = _report()

    assert report["final_status"] == "PASS"
    assert report["counters"]["human_final_walkthrough_created_count"] == 1
    assert report["counters"]["source_final_rollup_observed_count"] == 1
    assert report["source_rollup_report_id"] == "full_wow_v1_1_final_integrated_rollup_v01"


def test_human_final_walkthrough_transition_cards_present() -> None:
    report = _report()
    cards = report["transition_cards"]
    step_ids = {card["step_id"] for card in cards}

    assert len(cards) == 15
    assert step_ids == REQUIRED_STEP_IDS
    assert report["counters"]["transition_cards_created_count"] == 15
    for card in cards:
        assert REQUIRED_CARD_FIELDS <= set(card)


def test_human_final_walkthrough_business_story_visible() -> None:
    rendered = _rendered()

    for marker in (
        "DIRTY BUSINESS REQUEST",
        "Warehouse",
        "Supplier A",
        "Supplier B",
        "Legal",
        "Accounting",
        "real Gemini Orchestrator",
        "BSEP",
        "real Gemini Architect",
        "Root",
        "human approval",
        "ActionCommitPacket",
        "MockBankSandbox",
        "receipt evidence only",
    ):
        assert marker in rendered


def test_human_final_walkthrough_real_gemini_observed_not_rerun() -> None:
    counters = _report()["counters"]

    assert counters["real_gemini_lane_observed_count"] == 1
    assert counters["real_gemini_lane_rerun_count"] == 0
    assert counters["walkthrough_called_gemini_count"] == 0
    assert counters["walkthrough_network_used_count"] == 0
    assert counters["walkthrough_provider_called_count"] == 0


def test_human_final_walkthrough_no_execution_or_effects() -> None:
    counters = _report()["counters"]

    assert counters["walkthrough_created_action_commit_packet_count"] == 0
    assert counters["walkthrough_created_receipt_count"] == 0
    assert counters["walkthrough_executed_mock_payment_count"] == 0
    assert counters["walkthrough_executed_real_payment_count"] == 0
    assert counters["walkthrough_released_shipment_count"] == 0
    assert counters["walkthrough_called_bank_supplier_warehouse_api_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_human_final_walkthrough_authority_matrix() -> None:
    report = _report()
    authority = set(report["authority_matrix"])

    assert REQUIRED_AUTHORITY_FACTS <= authority
    assert "Root remains final authority." in authority
    assert "Receipt does not release shipment." in authority
    assert "Runtime owns PlanGraph/local plan artifacts." in authority


def test_human_final_walkthrough_non_claims_and_forbidden_overclaims() -> None:
    rendered = _rendered()

    assert "not production" in rendered
    assert "not public auditor final package" in rendered
    assert "no real payment" in rendered
    assert "no real shipment release" in rendered
    assert "v1.2 not implemented" in rendered
    for left, right in FORBIDDEN_PHRASE_PARTS:
        assert left + right not in rendered


def test_human_final_walkthrough_rendered_sections() -> None:
    rendered = _rendered()

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "FINAL STATUS: PASS" in rendered


def test_human_final_walkthrough_does_not_import_execution_runners() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "run_supplier_payment_shipment_release_review_wow_v1_1" not in source
    assert "run_full_semantic_e2e_v01" not in source
    assert "google.genai" not in source
    assert "run_full_wow_v1_1_final_integrated_rollup" in source
