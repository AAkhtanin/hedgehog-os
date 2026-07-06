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
    "runtime_plangraph_compiled",
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
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Runtime owns PlanGraph/local plan artifacts.",
    "Provider does not own PlanGraph.",
    "PlanGraph is not authority.",
    "Branch ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
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
        == "runtime_plangraph_compiled"
    )


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
    assert counters["product_trace_created_receipt_count"] == 0
    assert counters["product_trace_executed_mock_payment_count"] == 0
    assert counters["product_trace_executed_real_payment_count"] == 0
    assert counters["product_trace_released_shipment_count"] == 0
    assert counters["product_trace_called_real_bank_supplier_warehouse_api_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_v1_2_product_trace_authority_matrix() -> None:
    authority = set(_report()["authority_matrix"])

    assert REQUIRED_AUTHORITY_FACTS <= authority
    assert "Root remains final authority." in authority
    assert "Provider does not own PlanGraph." in authority
    assert "Branch LLM/SLM output is not authority." in authority
    assert "Branch LLM/SLM output is not action permission." in authority
    assert "Branch LLM/SLM output is not FinalOutput." in authority


def test_v1_2_product_trace_rendered_sections() -> None:
    rendered = _rendered()

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "real Gemini Semantic Architect" in rendered
    assert "Architect semantic validation accepted" in rendered
    assert "runtime retained PlanGraph ownership" in rendered
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
    assert "run_full_semantic_e2e_v01" not in source
    assert "run_supplier_payment_shipment_release_review_wow_v1_1" not in source
    assert "run_human_full_wow_v1_1_final_walkthrough" not in source
