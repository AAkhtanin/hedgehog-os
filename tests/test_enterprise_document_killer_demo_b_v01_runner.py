from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_enterprise_document_killer_demo_b_v01 import (
    ADVERSARIAL_ATTEMPT_IDS,
    collect_enterprise_document_killer_demo_b_v01,
    render_enterprise_document_killer_demo_b_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_enterprise_document_killer_demo_b_v01()


@pytest.fixture(scope="module")
def rendered(report):
    return render_enterprise_document_killer_demo_b_v01(report)


@pytest.fixture(scope="module")
def fixtures(report):
    return {row["filename"]: row["fields"] for row in report.document_fixtures}


def test_rendered_output_contains_required_sections(rendered):
    for section in (
        "[HEADER]",
        "[SOURCE CHECKPOINTS]",
        "[DOCUMENT FIXTURES]",
        "[ACT 1 — DIRTY DOCUMENT READINESS]",
        "[ACT 2 — AUTHORITY STRESS INSIDE DOCUMENT WORKFLOW]",
        "[ACT 3 — CORRECTED DOCUMENTS]",
        "[ACT 4 — ROOT-APPROVED REUSE / COMPUTE COLLAPSE]",
        "[ROOT FINALS]",
        "[WHAT HUMAN SEES]",
        "[WHAT THIS PROVES]",
        "[WHAT THIS DOES NOT PROVE]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert section in rendered


def test_rendered_output_contains_positive_grep_terms(rendered):
    for expected in (
        "Enterprise Document Killer Demo B v0.1",
        "enterprise_document_killer_demo_b_v01_status: PASS",
        "deterministic_local_proof_only",
        "bb1f7c2",
        "ALPHA SUPPLY",
        "18400 EUR",
        "SHIP-900",
        "BANK-771",
        "medical_filter_pack",
        "required_qty: 40",
        "available_qty: 40",
        "CERT-310",
        "insurance_status: expired",
        "COMP-882",
        "missing_signature",
        "LEGAL-FAKE",
        "provenance: missing",
        "trust: unknown",
        "CERT-311",
        "insurance_status: valid",
        "COMP-883",
        "signature_status: present",
        "ACT 1",
        "ACT 2",
        "ACT 3",
        "ACT 4",
        "act_1_root_result: not_ready",
        "needs_user_document_update",
        "act_2_adversarial_attempts_observed: 18",
        "act_2_adversarial_attempts_blocked: 18",
        "act_3_root_result: ready_for_internal_release",
        "act_4_resolution_source: Root-approved Local DRS Reuse",
        "act_4_drs_reuse_is_authority: false",
        "production_autonomy_claimed: false",
        "no_real_ocr: true",
        "no_real_pdf_parsing: true",
        "no_real_external_action: true",
    ):
        assert expected in rendered


def test_status_proof_type_and_design_doc_reference(report):
    summary = report.summary
    assert summary["enterprise_document_killer_demo_b_v01_status"] == "PASS"
    assert summary["proof_type"] == "deterministic_local_proof_only"
    assert summary["design_doc_commit"] == "bb1f7c2"
    assert (
        summary["design_doc_file"]
        == "docs/demo_designs/enterprise_document_killer_demo_b_v01.md"
    )
    assert report.design_doc_reference["design_doc_status"] == "accepted"


def test_source_checkpoints_are_closed_metadata_only(report):
    assert report.source_evidence["source_evidence_mode"] == (
        "closed_checkpoint_metadata_only"
    )
    assert report.source_evidence["source_collectors_replayed"] is False
    assert report.source_evidence["source_checkpoint_count"] == 12
    assert report.source_evidence["source_checkpoints_all_closed"] is True
    assert len(report.source_checkpoints) == 12
    assert all(row["checkpoint_status"] == "closed" for row in report.source_checkpoints)


def test_source_checkpoint_names_include_demo_a_and_design(report):
    names = {row["checkpoint_name"] for row in report.source_checkpoints}
    assert "Enterprise Killer Demo v0.1 / Demo A" in names
    assert "Enterprise Document Killer Demo B v0.1 Design" in names


def test_invoice_fixture_matches_canonical_values(fixtures):
    invoice = fixtures["invoice_INV-2026-044.txt"]
    assert invoice["invoice_id"] == "INV-2026-044"
    assert invoice["vendor"] == "ALPHA SUPPLY"
    assert invoice["amount"] == "18400 EUR"
    assert invoice["shipment_id"] == "SHIP-900"
    assert invoice["payment_required"] is True


def test_payment_receipt_fixture_matches_canonical_values(fixtures):
    payment = fixtures["payment_receipt_BANK-771.txt"]
    assert payment["receipt_id"] == "BANK-771"
    assert payment["invoice_id"] == "INV-2026-044"
    assert payment["amount"] == "18400 EUR"
    assert payment["status"] == "paid"
    assert payment["source"] == "bank_source"
    assert payment["provenance"] == "known"
    assert payment["freshness"] == "current"
    assert payment["mock_signature"] == "valid"


def test_warehouse_fixture_matches_canonical_values(fixtures):
    stock = fixtures["warehouse_stock_W-17.txt"]
    assert stock["warehouse_id"] == "W-17"
    assert stock["shipment_id"] == "SHIP-900"
    assert stock["item"] == "medical_filter_pack"
    assert stock["required_qty"] == 40
    assert stock["available_qty"] == 40
    assert stock["batch_status"] == "clear"


def test_logistics_fixture_matches_canonical_values(fixtures):
    logistics = fixtures["logistics_window_LOG-44.txt"]
    assert logistics["dispatch_window"] == "available"
    assert logistics["route_window"] == "current"
    assert logistics["carrier"] == "local_mock_carrier"


def test_dirty_insurance_fixture_matches_canonical_values(fixtures):
    insurance = fixtures["insurance_certificate_CERT-310.txt"]
    assert insurance["certificate_id"] == "CERT-310"
    assert insurance["insurance_status"] == "expired"
    assert insurance["expiry_date"] == "past"
    assert insurance["source"] == "legal_registry_source"
    assert insurance["provenance"] == "known"
    assert insurance["freshness"] == "stale_or_expired"


def test_dirty_compliance_fixture_matches_canonical_values(fixtures):
    compliance = fixtures["compliance_certificate_COMP-882.txt"]
    assert compliance["certificate_id"] == "COMP-882"
    assert compliance["compliance_status"] == "missing_signature"
    assert compliance["required_for_release"] is True


def test_unknown_external_pointer_fixture_matches_canonical_values(fixtures):
    pointer = fixtures["external_pointer_LEGAL-FAKE.txt"]
    assert pointer["claims"] == "insurance valid"
    assert pointer["source"] == "unknown_external_pointer"
    assert pointer["provenance"] == "missing"
    assert pointer["trust"] == "unknown"


def test_corrected_insurance_fixture_matches_canonical_values(fixtures):
    insurance = fixtures["insurance_certificate_CERT-311.txt"]
    assert insurance["certificate_id"] == "CERT-311"
    assert insurance["insurance_status"] == "valid"
    assert insurance["expiry_date"] == "future"
    assert insurance["source"] == "legal_registry_source"
    assert insurance["provenance"] == "known"
    assert insurance["freshness"] == "current"
    assert insurance["mock_signature"] == "valid"


def test_corrected_compliance_fixture_matches_canonical_values(fixtures):
    compliance = fixtures["compliance_certificate_COMP-883.txt"]
    assert compliance["certificate_id"] == "COMP-883"
    assert compliance["compliance_status"] == "valid"
    assert compliance["signature_status"] == "present"


def test_stale_invented_fixture_values_are_absent(rendered):
    stale_values = (
        "AC" + "ME Industrial Supply",
        "18" + "4500",
        "U" + "SD",
        "payment_status" + ": received",
        "stock_status" + ": reserved",
        "item_count" + ": complete",
        "pickup_window" + ": deterministic_mock_window",
    )
    for stale in stale_values:
        assert stale not in rendered


def test_act_1_flow_flags(report):
    act1 = report.act1_dirty_document_readiness
    assert act1["request_id"] == "ENTERPRISE-DOC-900"
    assert act1["shipment_id"] == "SHIP-900"
    assert act1["connector_observations_created"] is True
    assert act1["evidence_candidates_created"] is True
    assert act1["validation_packets_created"] is True
    assert act1["bounded_llm_semantic_extraction_created"] is True
    assert act1["fractal_domain_branches_created"] is True
    assert act1["branches"] == ["payment", "legal", "warehouse", "logistics", "risk"]


def test_act_1_coupling_conflict_and_gt(report):
    act1 = report.act1_dirty_document_readiness
    assert act1["dual_coupling_invoice_payment_shipment"] is True
    assert act1["dual_coupling_certificate_shipment_readiness"] is True
    assert act1["drs_bridge_reuse_signal_observed"] is True
    assert (
        act1["conflictcheck_detects_pointer_vs_expired_legal_evidence"] is True
    )
    assert act1["gt_recommendation"] == "not_ready_needs_user_document_update"


def test_act_1_evidence_decisions(report):
    act1 = report.act1_dirty_document_readiness
    assert act1["payment_evidence_accepted_by_root"] is True
    assert act1["warehouse_stock_evidence_accepted_by_root"] is True
    assert act1["expired_insurance_evidence_rejected_by_root"] is True
    assert act1["missing_compliance_signature_flagged"] is True
    assert act1["unknown_external_pointer_quarantined"] is True


def test_act_1_root_final_and_blockers(report):
    act1 = report.act1_dirty_document_readiness
    assert act1["act_1_root_result"] == "not_ready"
    assert act1["act_1_safe_secondary_outcome"] == "needs_user_document_update"
    assert act1["act_1_needs_user_document_update"] is True
    assert "insurance_certificate_expired" in act1["act_1_blockers"]
    assert "compliance_certificate_missing_signature" in act1["act_1_blockers"]
    assert "unknown_external_pointer_quarantined" in act1["act_1_blockers"]
    assert act1["act_1_external_action_executed"] is False
    assert act1["act_1_shipment_released"] is False
    assert act1["act_1_root_remains_final_authority"] is True


def test_act_1_human_explanation_is_safe(report):
    explanation = report.act1_dirty_document_readiness["human_explanation"]
    assert "Payment and stock look usable" in explanation
    assert "legal/compliance evidence blocks release" in explanation
    assert "lacks provenance" in explanation
    assert "No release action was executed" in explanation


def test_act_2_counts(report):
    act2 = report.act2_authority_stress
    assert act2["act_2_adversarial_attempts_observed"] == 18
    assert act2["act_2_adversarial_attempts_blocked"] == 18
    assert act2["act_2_quarantined_attempts_observed"] == 3


def test_all_18_attempt_ids_are_present(report):
    assert [row["attempt_id"] for row in report.act2_authority_stress["attempts"]] == list(
        ADVERSARIAL_ATTEMPT_IDS
    )


def test_quarantined_attempts_are_marked(report):
    attempts = {
        row["attempt_id"]: row for row in report.act2_authority_stress["attempts"]
    }
    for attempt_id in (
        "external_pointer_to_trusted_evidence",
        "external_pointer_to_global_drs_write",
        "bridge_traversal_to_provenance_laundering",
    ):
        assert attempts[attempt_id]["final_effect"] == "quarantined_and_blocked"


def test_all_adversarial_attempts_are_detected_and_blocked(report):
    attempts = report.act2_authority_stress["attempts"]
    assert all(row["detected"] is True for row in attempts)
    assert all(row["blocked"] is True for row in attempts)


def test_adversarial_attempts_create_no_illegal_effects(report):
    for row in report.act2_authority_stress["attempts"]:
        for field in (
            "authority_transferred",
            "root_bypassed",
            "truth_claim_created",
            "final_output_created_by_non_root",
            "accepted_evidence_created_without_root",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_capability_created",
            "installed_needle_created",
            "production_persistence",
            "network_called",
            "gemini_called",
            "marennya_invoked",
            "up_invoked",
        ):
            assert row[field] is False


def test_act_2_summary_boundaries(report):
    act2 = report.act2_authority_stress
    assert act2["act_2_authority_transferred"] is False
    assert act2["act_2_non_root_final_output_created"] is False
    assert act2["act_2_global_drs_write"] is False
    assert act2["act_2_external_drs_write"] is False
    assert act2["act_2_installed_needle_created"] is False
    assert act2["act_2_root_remains_final_authority"] is True


def test_act_3_corrected_evidence_flow(report):
    act3 = report.act3_corrected_documents
    assert act3["corrected_connector_observations_created"] is True
    assert act3["corrected_evidence_candidates_created"] is True
    assert act3["corrected_validation_packets_created"] is True
    assert act3["corrected_insurance_evidence_accepted_by_root"] is True
    assert act3["corrected_compliance_evidence_accepted_by_root"] is True
    assert act3["prior_blockers_resolved"] is True


def test_act_3_ready_for_internal_release_without_action(report):
    act3 = report.act3_corrected_documents
    assert act3["conflictcheck_confirms_no_known_blocker_remains"] is True
    assert act3["post_vv_confirms_no_known_blocker_remains"] is True
    assert act3["gt_recommendation"] == "ready_for_internal_release"
    assert act3["act_3_root_result"] == "ready_for_internal_release"
    assert act3["act_3_corrected_evidence_accepted_by_root"] is True
    assert act3["act_3_external_action_executed"] is False
    assert act3["act_3_shipment_released"] is False
    assert act3["act_3_requires_operator_confirmation_for_real_release"] is True
    assert act3["act_3_operator_confirmation_required"] is True


def test_act_3_human_explanation_is_safe(report):
    explanation = report.act3_corrected_documents["human_explanation"]
    assert "corrected and accepted by Root" in explanation
    assert "ready for internal release review" in explanation
    assert "does not execute real shipment release" in explanation


def test_act_4_root_approved_reuse_flow(report):
    act4 = report.act4_root_approved_reuse
    assert act4["request_id"] == "ENTERPRISE-DOC-901"
    assert act4["shipment_id"] == "SHIP-901"
    assert act4["same_vendor"] == "ALPHA SUPPLY"
    assert act4["same_document_pattern"] is True
    assert act4["drs_retrieval_finds_prior_accepted_trace"] is True
    assert act4["prior_trace_ref"] == "ENTERPRISE-DOC-900 corrected case"
    assert act4["root_approves_bounded_reuse"] is True


def test_act_4_drs_reuse_is_advisory_and_not_authority(report):
    act4 = report.act4_root_approved_reuse
    assert act4["reuse_score_is_advisory_only"] is True
    assert act4["semantic_similarity_is_advisory_only"] is True
    assert act4["freshness_checked"] is True
    assert act4["worldstate_compatibility_checked"] is True
    assert act4["conflictcheck_verifies_no_stale_or_contradictory_blockers"] is True
    assert act4["act_4_drs_reuse_is_authority"] is False


def test_act_4_resolution_source_is_root_approved(rendered, report):
    act4 = report.act4_root_approved_reuse
    assert act4["act_4_resolution_source"] == "Root-approved Local DRS Reuse"
    assert act4["resolution_source_line"] == (
        "Resolution Source: Root-approved Local DRS Reuse"
    )
    assert act4["act_4_forbidden_resolution_source_used"] is False
    forbidden = "Resolution Source: " + "Local DRS " + "Authority"
    assert forbidden not in rendered


def test_act_4_compute_collapse_is_synthetic_only(report):
    act4 = report.act4_root_approved_reuse
    assert act4["full_fractal_expansion_reduced"] is True
    assert act4["bounded_llm_calls_zero_or_minimal"] is True
    assert act4["baseline_document_review_units"] == 64
    assert act4["hedgehog_reuse_review_units"] == 18
    assert act4["estimated_document_review_units_saved"] == 46
    assert act4["act_4_compute_collapse_signal_observed"] is True
    assert act4["compute_collapse_claim_is_synthetic"] is True
    assert act4["production_economics_claimed"] is False


def test_root_finals_are_human_readable_and_safe(report):
    finals = report.root_finals
    assert finals["act_1_root_result"] == "not_ready"
    assert finals["act_1_safe_secondary_outcome"] == "needs_user_document_update"
    assert finals["act_3_root_result"] == "ready_for_internal_release"
    assert finals["act_4_resolution_source"] == "Root-approved Local DRS Reuse"
    assert finals["root_remains_final_authority"] is True
    assert finals["act_1_external_action_executed"] is False
    assert finals["act_3_external_action_executed"] is False


def test_what_human_sees_is_business_readable(report):
    human = report.what_human_sees
    assert human["act_1_human_result"] == "NOT_READY"
    assert "insurance expired" in human["act_1_human_why"]
    assert human["act_1_action"] == "NONE"
    assert human["act_2_human_result"] == "18/18 escalation attempts blocked"
    assert human["act_3_human_result"] == "READY_FOR_INTERNAL_RELEASE"
    assert human["act_3_action"] == "NONE"
    assert human["raw_json_wall_rendered"] is False


def test_future_proof_claims_are_bounded(report):
    proves = report.what_this_proves
    assert proves["multi_document_evidence_represented_locally"] is True
    assert proves["domain_branches_separated"] is True
    assert proves["bounded_llm_semantic_node_not_truth"] is True
    assert proves["root_accepts_rejects_quarantines_evidence"] is True
    assert proves["dirty_documents_produce_not_ready"] is True
    assert proves["corrected_documents_produce_internal_ready"] is True
    assert proves["no_real_action_executed"] is True
    assert proves["drs_reuse_reduces_repeated_reasoning_under_root"] is True
    assert proves["authority_boundaries_intact"] is True


def test_non_claims_remain_false(report):
    non_claims = report.what_this_does_not_prove
    for field in (
        "real_document_ocr_proven",
        "real_pdf_parsing_proven",
        "real_signature_verification_proven",
        "real_legal_validation_proven",
        "real_bank_verification_proven",
        "real_warehouse_integration_proven",
        "real_shipment_release_proven",
        "real_external_api_access_proven",
        "real_production_drs_proven",
        "real_cost_savings_proven",
        "production_autonomy_proven",
        "needle_installation_proven",
        "marennya_up_activation_proven",
    ):
        assert non_claims[field] is False


def test_global_invariant_false_flags_are_safe(report):
    summary = report.summary
    for field in (
        "llm_is_authority",
        "semantic_draft_is_truth",
        "connector_observation_is_truth",
        "evidence_candidate_is_accepted_evidence",
        "accepted_evidence_is_action",
        "gt_is_final_authority",
        "audit_hash_decides_truth",
        "developer_manifest_is_authority",
        "transition_matrix_is_authority",
        "killer_demo_authorizes_production",
        "production_autonomy_claimed",
        "network_called",
        "gemini_called",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_capability_created",
        "installed_needle_created",
        "marennya_invoked",
        "up_invoked",
    ):
        assert summary[field] is False


def test_global_positive_guardrails_are_true(report):
    summary = report.summary
    assert summary["root_remains_final_authority"] is True
    assert summary["no_real_ocr"] is True
    assert summary["no_real_pdf_parsing"] is True
    assert summary["no_real_bank_connector"] is True
    assert summary["no_real_legal_connector"] is True
    assert summary["no_real_warehouse_connector"] is True
    assert summary["no_real_external_action"] is True
    assert summary["no_production_drs"] is True
    assert summary["no_installed_needle"] is True
    assert summary["no_marennya"] is True
    assert summary["no_up"] is True


def test_summary_fixture_fidelity(report):
    summary = report.summary
    assert summary["fixture_fidelity_verified"] is True
    assert summary["canonical_vendor"] == "ALPHA SUPPLY"
    assert summary["canonical_amount"] == "18400 EUR"
    assert summary["canonical_shipment_id"] == "SHIP-900"


def test_rendered_output_avoids_raw_json_walls(rendered):
    assert not rendered.lstrip().startswith("{")
    assert "{'" not in rendered
    assert '": {' not in rendered


def test_audit_hash_matches_canonical_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["audit_hash_chain_records_continuity_only"] is True
    assert report.audit_entry["audit_hash_decides_truth"] is False
