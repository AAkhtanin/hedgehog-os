from __future__ import annotations

from pathlib import Path

from demo import run_full_wow_v1_1_final_integrated_rollup as runner


REQUIRED_SOURCE_PATHS = {
    "demo/run_supplier_payment_shipment_release_review_wow_v1_1.py",
    "docs/audit_reports/auditor_supplier_payment_shipment_release_review_wow_v1_1.log",
    "demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py",
    "demo/run_full_semantic_e2e_v01.py",
    "docs/audit_reports/auditor_full_semantic_e2e_wow_v1_1_alignment_v01.log",
    "docs/audit_reports/auditor_full_semantic_e2e_live_evidence_wow_v1_1_coherence_v01.log",
    "docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_bsep_topology_repair_v01.log",
    "docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
    "docs/full_wow_v1_1_final_integrated_rollup_preflight_v01.md",
}

REQUIRED_PHASE_IDS = {
    "phase_1_first_run_not_ready",
    "phase_2_corrected_evidence_drs_writeback_context_only",
    "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
    "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
    "phase_5_mock_bank_sandbox_executes_supplier_a_only",
}

REQUIRED_SECTIONS = (
    "[FULL WOW V1.1 FINAL INTEGRATED ROLLUP]",
    "[SOURCE CHECKPOINTS]",
    "[STATE MACHINE PHASES]",
    "[LIVE GEMINI SEMANTIC LANE]",
    "[BSEP MEMBRANE]",
    "[DRS / CANDIDATE VECTOR / AVF]",
    "[SEMANTIC ARCHITECT AND RUNTIME PLAN ARTIFACTS]",
    "[ROOT / HUMAN / ACTION BOUNDARY]",
    "[MOCK BANK RECEIPT BOUNDARY]",
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
    return runner.collect_full_wow_v1_1_final_integrated_rollup()


def test_final_rollup_returns_pass() -> None:
    report = _report()

    assert report["final_status"] == "PASS"
    assert report["wow_v1_1_final_integrated_rollup_status"] == "PASS"
    assert report["counters"]["final_integrated_rollup_created_count"] == 1
    assert report["wow_completion_claimed"] is True
    assert report["wow_completion_claim_scope"] == "final integrated rollup proof only"


def test_final_rollup_source_inventory_present() -> None:
    report = _report()
    inventory = report["source_inventory"]
    paths = {item["path"] for item in inventory}

    assert REQUIRED_SOURCE_PATHS <= paths
    assert all(item["exists"] is True for item in inventory)
    assert all(item["observed_count"] == 1 for item in inventory)
    for item in inventory:
        assert (runner.PROJECT_ROOT / item["path"]).exists()

    counters = report["counters"]
    assert counters["source_supplier_wow_summary_observed_count"] == 1
    assert counters["source_human_walkthrough_observed_count"] == 1
    assert counters["source_full_e2e_summary_observed_count"] == 1
    assert counters["source_real_gemini_audit_observed_count"] == 1
    assert counters["source_bsep_topology_audit_observed_count"] == 1


def test_final_rollup_state_machine_phases_present() -> None:
    report = _report()
    phases = {item["phase_id"] for item in report["state_machine_phases"]}
    boundaries = report["business_boundaries"]

    assert REQUIRED_PHASE_IDS == phases
    assert boundaries["supplier_B_remains_blocked"] is True
    assert boundaries["shipment_release_remains_held"] is True
    assert boundaries["receipt_evidence_only"] is True


def test_final_rollup_real_gemini_lane_observed_not_rerun() -> None:
    report = _report()
    lane = report["live_gemini_semantic_lane"]

    assert lane["real_gemini_lane_observed_count"] == 1
    assert lane["real_gemini_lane_rerun_count"] == 0
    assert lane["real_gemini_orchestrator_called_count"] == 1
    assert lane["real_gemini_architect_called_count"] == 1
    assert lane["live_model_call_count"] == 2
    assert lane["gemini_called_count_in_closed_run"] == 2
    assert lane["network_used_count_in_closed_run"] == 2
    assert lane["rollup_called_gemini_count"] == 0
    assert lane["rollup_network_used_count"] == 0
    assert lane["rollup_provider_called_count"] == 0
    assert report["counters"]["rollup_called_gemini_count"] == 0
    assert report["counters"]["rollup_network_used_count"] == 0
    assert report["counters"]["rollup_provider_called_count"] == 0


def test_final_rollup_bsep_before_architect_sequence_present() -> None:
    sequence = list(_report()["live_gemini_semantic_lane"]["role_sequence"])
    expected = list(runner.ROLE_SEQUENCE)

    assert sequence == expected
    assert sequence.index("orchestrator_provider_called") < sequence.index(
        "orchestrator_semantics_validated"
    )
    assert sequence.index("orchestrator_semantics_canonicalized") < sequence.index(
        "bsep_built"
    )
    assert sequence.index("bsep_validated") < sequence.index(
        "architect_provider_called"
    )
    assert sequence.index("architect_semantics_validated") < sequence.index(
        "architect_semantics_canonicalized"
    )


def test_final_rollup_semantic_architect_runtime_plangraph_boundary() -> None:
    report = _report()
    boundary = report["semantic_architect_and_runtime_plan_artifacts"]
    authority = report["authority_matrix"]

    assert boundary["semantic_architect_is_provider_output"] is True
    assert boundary["semantic_architect_is_root"] is False
    assert boundary["runtime_owns_plangraph_local_plan_artifacts"] is True
    assert boundary["provider_owns_plangraph"] is False
    assert boundary["plan_graph_is_authority"] is False
    assert "Semantic Architect is not Root." in authority
    assert "PlanGraph is not authority." in authority


def test_final_rollup_no_new_action_or_receipt_or_execution() -> None:
    counters = _report()["counters"]

    assert counters["rollup_created_action_commit_packet_count"] == 0
    assert counters["rollup_created_receipt_count"] == 0
    assert counters["rollup_executed_mock_payment_count"] == 0
    assert counters["rollup_executed_real_payment_count"] == 0
    assert counters["rollup_released_shipment_count"] == 0
    assert counters["rollup_called_bank_supplier_warehouse_api_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_final_rollup_rendered_report_sections() -> None:
    report = _report()
    rendered = runner.render_full_wow_v1_1_final_integrated_rollup(report)

    for section in REQUIRED_SECTIONS:
        assert section in rendered
    assert "FINAL STATUS: PASS" in rendered
    assert "final_integrated_rollup_created_count: 1" in rendered
    assert "rollup_called_gemini_count: 0" in rendered
    assert "rollup_created_action_commit_packet_count: 0" in rendered
    assert "rollup_created_receipt_count: 0" in rendered


def test_final_rollup_non_claims_and_forbidden_overclaims() -> None:
    rendered = runner.render_full_wow_v1_1_final_integrated_rollup(_report())

    assert "not production" in rendered
    assert "not public auditor final package" in rendered
    assert "no real payment" in rendered
    assert "no real shipment release" in rendered
    for left, right in FORBIDDEN_PHRASE_PARTS:
        assert left + right not in rendered


def test_final_rollup_runner_does_not_import_closed_runners() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    assert "run_supplier_payment_shipment_release_review_wow_v1_1 import" not in source
    assert "run_full_semantic_e2e_v01 import" not in source
    assert "google.genai" not in source
    assert "GEMINI_API_KEY" not in source
    assert "GOOGLE_API_KEY" not in source
