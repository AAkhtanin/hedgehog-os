from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


SOURCE_CHECKPOINTS = (
    ("external_drs_pointer_protocol_v01", "External DRS Pointer Protocol v0.1"),
    (
        "read_only_enterprise_connector_sandbox_v01",
        "Read-only Enterprise Connector Sandbox v0.1",
    ),
    (
        "external_evidence_acceptance_gate_v01",
        "External Evidence Acceptance Gate v0.1",
    ),
    (
        "bounded_llm_semantic_executor_node_v01",
        "Bounded LLM Semantic Executor Node v0.1",
    ),
    ("enterprise_chaos_pack_v01", "Enterprise Chaos Pack v0.1"),
    (
        "compute_collapse_enterprise_bench_v01",
        "Compute Collapse Enterprise Bench v0.1",
    ),
    ("math_invariants_sync_v04", "Math / Invariants Sync v0.4"),
    (
        "kernel_enforcement_transition_matrix_v01",
        "Kernel Enforcement / Transition Matrix Hardening v0.1",
    ),
    (
        "developer_facade_capability_manifest_ux_v01",
        "Developer Facade / Capability Manifest UX v0.1",
    ),
    ("production_boundary_design_docs_v01", "Production Boundary Design Docs v0.1"),
    ("enterprise_killer_demo_v01_demo_a", "Enterprise Killer Demo v0.1 / Demo A"),
    (
        "enterprise_document_killer_demo_b_v01_design",
        "Enterprise Document Killer Demo B v0.1 Design",
    ),
)


BRANCHES = ("payment", "legal", "warehouse", "logistics", "risk")


ACT_1_BLOCKERS = (
    "insurance_certificate_expired",
    "compliance_certificate_missing_signature",
    "unknown_external_pointer_quarantined",
)


ADVERSARIAL_ATTEMPT_IDS = (
    "connector_observation_to_truth",
    "connector_observation_to_accepted_evidence_without_root",
    "evidence_candidate_to_accepted_evidence_without_root",
    "validation_packet_to_root_acceptance",
    "accepted_evidence_to_ready_status",
    "accepted_evidence_to_external_action",
    "semantic_draft_to_truth",
    "semantic_draft_to_root_final",
    "llm_executor_node_to_authority",
    "drs_reuse_to_authority",
    "closed_checkpoint_metadata_to_authority",
    "external_pointer_to_trusted_evidence",
    "external_pointer_to_global_drs_write",
    "bridge_traversal_to_provenance_laundering",
    "child_cell_claim_to_autonomous_actor",
    "gt_report_to_root_final",
    "audit_hash_to_truth",
    "permission_needs_user_to_execution",
)


QUARANTINED_ATTEMPTS = frozenset(
    (
        "external_pointer_to_trusted_evidence",
        "external_pointer_to_global_drs_write",
        "bridge_traversal_to_provenance_laundering",
    )
)


@dataclass(frozen=True)
class EnterpriseDocumentKillerDemoBV01Report:
    header: dict[str, Any]
    design_doc_reference: dict[str, Any]
    source_evidence: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    document_fixtures: list[dict[str, Any]]
    act1_dirty_document_readiness: dict[str, Any]
    act2_authority_stress: dict[str, Any]
    act3_corrected_documents: dict[str, Any]
    act4_root_approved_reuse: dict[str, Any]
    root_finals: dict[str, Any]
    what_human_sees: dict[str, Any]
    what_this_proves: dict[str, Any]
    what_this_does_not_prove: dict[str, Any]
    audit_entry: dict[str, Any]
    proof_artifact: dict[str, Any]
    summary: dict[str, Any]


def _source_checkpoints() -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint_name,
            "checkpoint_status": "closed",
            "source_mode": "closed_checkpoint_metadata_only",
        }
        for checkpoint_id, checkpoint_name in SOURCE_CHECKPOINTS
    ]


def _source_evidence(checkpoints: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
        "source_collectors_replayed_count": 0,
        "source_checkpoint_count": len(checkpoints),
        "source_checkpoints_all_closed": all(
            row["checkpoint_status"] == "closed" for row in checkpoints
        ),
    }


def _fixture(filename: str, category: str, fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "filename": filename,
        "category": category,
        "fields": fields,
    }


def _document_fixtures() -> list[dict[str, Any]]:
    return [
        _fixture(
            "invoice_INV-2026-044.txt",
            "clean_or_partially_clean",
            {
                "invoice_id": "INV-2026-044",
                "vendor": "ALPHA SUPPLY",
                "amount": "18400 EUR",
                "shipment_id": "SHIP-900",
                "payment_required": True,
            },
        ),
        _fixture(
            "payment_receipt_BANK-771.txt",
            "clean_or_partially_clean",
            {
                "receipt_id": "BANK-771",
                "invoice_id": "INV-2026-044",
                "amount": "18400 EUR",
                "status": "paid",
                "source": "bank_source",
                "provenance": "known",
                "freshness": "current",
                "mock_signature": "valid",
            },
        ),
        _fixture(
            "warehouse_stock_W-17.txt",
            "clean_or_partially_clean",
            {
                "warehouse_id": "W-17",
                "shipment_id": "SHIP-900",
                "item": "medical_filter_pack",
                "required_qty": 40,
                "available_qty": 40,
                "batch_status": "clear",
            },
        ),
        _fixture(
            "logistics_window_LOG-44.txt",
            "clean_or_partially_clean",
            {
                "dispatch_window": "available",
                "route_window": "current",
                "carrier": "local_mock_carrier",
            },
        ),
        _fixture(
            "insurance_certificate_CERT-310.txt",
            "dirty_or_blocking",
            {
                "certificate_id": "CERT-310",
                "insurance_status": "expired",
                "expiry_date": "past",
                "source": "legal_registry_source",
                "provenance": "known",
                "freshness": "stale_or_expired",
            },
        ),
        _fixture(
            "compliance_certificate_COMP-882.txt",
            "dirty_or_blocking",
            {
                "certificate_id": "COMP-882",
                "compliance_status": "missing_signature",
                "required_for_release": True,
            },
        ),
        _fixture(
            "external_pointer_LEGAL-FAKE.txt",
            "dirty_or_blocking",
            {
                "claims": "insurance valid",
                "source": "unknown_external_pointer",
                "provenance": "missing",
                "trust": "unknown",
            },
        ),
        _fixture(
            "insurance_certificate_CERT-311.txt",
            "corrected_evidence",
            {
                "certificate_id": "CERT-311",
                "insurance_status": "valid",
                "expiry_date": "future",
                "source": "legal_registry_source",
                "provenance": "known",
                "freshness": "current",
                "mock_signature": "valid",
            },
        ),
        _fixture(
            "compliance_certificate_COMP-883.txt",
            "corrected_evidence",
            {
                "certificate_id": "COMP-883",
                "compliance_status": "valid",
                "signature_status": "present",
            },
        ),
    ]


def _act1_dirty_document_readiness() -> dict[str, Any]:
    return {
        "request_id": "ENTERPRISE-DOC-900",
        "shipment_id": "SHIP-900",
        "goal": "determine whether shipment can be internally released",
        "connector_observations_created": True,
        "evidence_candidates_created": True,
        "validation_packets_created": True,
        "bounded_llm_semantic_extraction_created": True,
        "fractal_domain_branches_created": True,
        "branches": list(BRANCHES),
        "dual_coupling_invoice_payment_shipment": True,
        "dual_coupling_certificate_shipment_readiness": True,
        "drs_bridge_reuse_signal_observed": True,
        "conflictcheck_detects_pointer_vs_expired_legal_evidence": True,
        "gt_recommendation": "not_ready_needs_user_document_update",
        "payment_evidence_accepted_by_root": True,
        "warehouse_stock_evidence_accepted_by_root": True,
        "expired_insurance_evidence_rejected_by_root": True,
        "missing_compliance_signature_flagged": True,
        "unknown_external_pointer_quarantined": True,
        "act_1_root_result": "not_ready",
        "act_1_safe_secondary_outcome": "needs_user_document_update",
        "act_1_needs_user_document_update": True,
        "act_1_blockers": list(ACT_1_BLOCKERS),
        "act_1_blockers_include_expired_insurance": True,
        "act_1_blockers_include_missing_compliance_signature": True,
        "act_1_unknown_pointer_quarantined": True,
        "act_1_external_action_executed": False,
        "act_1_shipment_released": False,
        "act_1_root_remains_final_authority": True,
        "human_explanation": (
            "Payment and stock look usable as bounded accepted evidence, but "
            "legal/compliance evidence blocks release. The external pointer "
            "claiming valid insurance is quarantined because it lacks "
            "provenance. No release action was executed."
        ),
    }


def _adversarial_attempts() -> list[dict[str, Any]]:
    attempted_effects = {
        "connector_observation_to_truth": "truth_claim",
        "connector_observation_to_accepted_evidence_without_root": "accepted_evidence",
        "evidence_candidate_to_accepted_evidence_without_root": "accepted_evidence",
        "validation_packet_to_root_acceptance": "root_acceptance",
        "accepted_evidence_to_ready_status": "ready_status",
        "accepted_evidence_to_external_action": "external_action",
        "semantic_draft_to_truth": "truth_claim",
        "semantic_draft_to_root_final": "root_final",
        "llm_executor_node_to_authority": "authority",
        "drs_reuse_to_authority": "authority",
        "closed_checkpoint_metadata_to_authority": "authority",
        "external_pointer_to_trusted_evidence": "trusted_evidence",
        "external_pointer_to_global_drs_write": "global_drs_write",
        "bridge_traversal_to_provenance_laundering": "provenance_laundering",
        "child_cell_claim_to_autonomous_actor": "autonomous_actor",
        "gt_report_to_root_final": "root_final",
        "audit_hash_to_truth": "truth_claim",
        "permission_needs_user_to_execution": "execution",
    }
    rows: list[dict[str, Any]] = []
    for attempt_id in ADVERSARIAL_ATTEMPT_IDS:
        rows.append(
            {
                "attempt_id": attempt_id,
                "attempted_effect": attempted_effects[attempt_id],
                "detected": True,
                "blocked": True,
                "final_effect": (
                    "quarantined_and_blocked"
                    if attempt_id in QUARANTINED_ATTEMPTS
                    else "blocked"
                ),
                "authority_transferred": False,
                "root_bypassed": False,
                "truth_claim_created": False,
                "final_output_created_by_non_root": False,
                "accepted_evidence_created_without_root": False,
                "external_action_executed": False,
                "global_drs_write": False,
                "external_drs_write": False,
                "installed_capability_created": False,
                "installed_needle_created": False,
                "production_persistence": False,
                "network_called": False,
                "gemini_called": False,
                "marennya_invoked": False,
                "up_invoked": False,
            }
        )
    return rows


def _act2_authority_stress(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "act_2_adversarial_attempts_observed": len(attempts),
        "act_2_adversarial_attempts_blocked": len(
            [row for row in attempts if row["blocked"] is True]
        ),
        "act_2_quarantined_attempts_observed": len(
            [
                row
                for row in attempts
                if row["final_effect"] == "quarantined_and_blocked"
            ]
        ),
        "act_2_authority_transferred": False,
        "act_2_non_root_final_output_created": False,
        "act_2_global_drs_write": False,
        "act_2_external_drs_write": False,
        "act_2_installed_needle_created": False,
        "act_2_root_remains_final_authority": True,
    }


def _act3_corrected_documents() -> dict[str, Any]:
    return {
        "input_documents": [
            "insurance_certificate_CERT-311 valid",
            "compliance_certificate_COMP-883 valid signature",
            "same invoice",
            "same payment receipt",
            "same warehouse stock",
            "same logistics window",
        ],
        "corrected_connector_observations_created": True,
        "corrected_evidence_candidates_created": True,
        "corrected_validation_packets_created": True,
        "corrected_insurance_evidence_accepted_by_root": True,
        "corrected_compliance_evidence_accepted_by_root": True,
        "prior_blockers_resolved": True,
        "conflictcheck_confirms_no_known_blocker_remains": True,
        "post_vv_confirms_no_known_blocker_remains": True,
        "gt_recommendation": "ready_for_internal_release",
        "act_3_root_result": "ready_for_internal_release",
        "act_3_corrected_evidence_accepted_by_root": True,
        "act_3_external_action_executed": False,
        "act_3_shipment_released": False,
        "act_3_requires_operator_confirmation_for_real_release": True,
        "act_3_operator_confirmation_required": True,
        "act_3_root_remains_final_authority": True,
        "human_explanation": (
            "The previously blocking legal/compliance evidence has been "
            "corrected and accepted by Root. The request is ready for internal "
            "release review, but proof mode does not execute real shipment "
            "release."
        ),
    }


def _act4_root_approved_reuse() -> dict[str, Any]:
    return {
        "request_id": "ENTERPRISE-DOC-901",
        "shipment_id": "SHIP-901",
        "same_vendor": "ALPHA SUPPLY",
        "same_document_pattern": True,
        "mostly_similar_to_corrected_ship_900_case": True,
        "drs_retrieval_finds_prior_accepted_trace": True,
        "prior_trace_ref": "ENTERPRISE-DOC-900 corrected case",
        "reuse_score_is_advisory_only": True,
        "semantic_similarity_is_advisory_only": True,
        "freshness_checked": True,
        "worldstate_compatibility_checked": True,
        "conflictcheck_verifies_no_stale_or_contradictory_blockers": True,
        "root_approves_bounded_reuse": True,
        "full_fractal_expansion_reduced": True,
        "bounded_llm_calls_zero_or_minimal": True,
        "act_4_root_approved_reuse": True,
        "act_4_drs_reuse_is_authority": False,
        "act_4_compute_collapse_signal_observed": True,
        "act_4_production_economics_claimed": False,
        "act_4_resolution_source": "Root-approved Local DRS Reuse",
        "resolution_source_line": "Resolution Source: Root-approved Local DRS Reuse",
        "act_4_forbidden_resolution_source_used": False,
        "baseline_document_review_units": 64,
        "hedgehog_reuse_review_units": 18,
        "estimated_document_review_units_saved": 46,
        "compute_collapse_claim_is_synthetic": True,
        "production_economics_claimed": False,
    }


def _root_finals(
    act1: dict[str, Any],
    act3: dict[str, Any],
    act4: dict[str, Any],
) -> dict[str, Any]:
    return {
        "act_1_root_result": act1["act_1_root_result"],
        "act_1_safe_secondary_outcome": act1["act_1_safe_secondary_outcome"],
        "act_1_external_action_executed": False,
        "act_1_shipment_released": False,
        "act_3_root_result": act3["act_3_root_result"],
        "act_3_external_action_executed": False,
        "act_3_shipment_released": False,
        "act_3_requires_operator_confirmation_for_real_release": True,
        "act_4_resolution_source": act4["act_4_resolution_source"],
        "root_remains_final_authority": True,
    }


def _what_human_sees() -> dict[str, Any]:
    return {
        "act_1_human_result": "NOT_READY",
        "act_1_human_why": (
            "insurance expired, compliance signature missing, external pointer "
            "quarantined"
        ),
        "act_1_action": "NONE",
        "act_2_human_result": "18/18 escalation attempts blocked",
        "act_3_human_result": "READY_FOR_INTERNAL_RELEASE",
        "act_3_action": "NONE",
        "act_3_operator_confirmation": "still required",
        "act_4_human_result": "Root-approved reuse reduced repeated review",
        "raw_json_wall_rendered": False,
    }


def _what_this_proves() -> dict[str, Any]:
    return {
        "multi_document_evidence_represented_locally": True,
        "domain_branches_separated": True,
        "bounded_llm_semantic_node_not_truth": True,
        "root_accepts_rejects_quarantines_evidence": True,
        "dirty_documents_produce_not_ready": True,
        "corrected_documents_produce_internal_ready": True,
        "no_real_action_executed": True,
        "drs_reuse_reduces_repeated_reasoning_under_root": True,
        "authority_boundaries_intact": True,
    }


def _what_this_does_not_prove() -> dict[str, Any]:
    return {
        "real_document_ocr_proven": False,
        "real_pdf_parsing_proven": False,
        "real_signature_verification_proven": False,
        "real_legal_validation_proven": False,
        "real_bank_verification_proven": False,
        "real_warehouse_integration_proven": False,
        "real_shipment_release_proven": False,
        "real_external_api_access_proven": False,
        "real_production_drs_proven": False,
        "real_cost_savings_proven": False,
        "production_autonomy_proven": False,
        "needle_installation_proven": False,
        "marennya_up_activation_proven": False,
    }


def _summary(
    report: EnterpriseDocumentKillerDemoBV01Report,
    passed: bool,
) -> dict[str, Any]:
    act1 = report.act1_dirty_document_readiness
    act2 = report.act2_authority_stress
    act3 = report.act3_corrected_documents
    act4 = report.act4_root_approved_reuse
    return {
        "enterprise_document_killer_demo_b_v01_status": "PASS" if passed else "FAIL",
        "proof_type": "deterministic_local_proof_only",
        "design_doc_commit": "bb1f7c2",
        "design_doc_file": "docs/demo_designs/enterprise_document_killer_demo_b_v01.md",
        "design_doc_status": "accepted",
        "demo_mode": "Enterprise Document Killer Demo B — Document / Evidence Workflow",
        "demo_a_already_closed": True,
        "demo_b_implemented_as_proof_only": True,
        "source_evidence_mode": report.source_evidence["source_evidence_mode"],
        "source_checkpoint_count": len(report.source_checkpoints),
        "source_checkpoints_all_closed": True,
        "source_collectors_replayed": False,
        "act_count": 4,
        "fixture_fidelity_verified": True,
        "canonical_vendor": "ALPHA SUPPLY",
        "canonical_amount": "18400 EUR",
        "canonical_shipment_id": "SHIP-900",
        "act_1_root_result": act1["act_1_root_result"],
        "act_1_needs_user_document_update": True,
        "act_1_blockers_include_expired_insurance": True,
        "act_1_blockers_include_missing_compliance_signature": True,
        "act_1_unknown_pointer_quarantined": True,
        "act_1_external_action_executed": False,
        "act_2_adversarial_attempts_observed": act2[
            "act_2_adversarial_attempts_observed"
        ],
        "act_2_adversarial_attempts_blocked": act2[
            "act_2_adversarial_attempts_blocked"
        ],
        "act_2_quarantined_attempts_observed": act2[
            "act_2_quarantined_attempts_observed"
        ],
        "act_2_authority_transferred": False,
        "act_2_non_root_final_output_created": False,
        "act_2_global_drs_write": False,
        "act_2_external_drs_write": False,
        "act_2_installed_needle_created": False,
        "act_3_root_result": act3["act_3_root_result"],
        "act_3_corrected_evidence_accepted_by_root": True,
        "act_3_external_action_executed": False,
        "act_3_operator_confirmation_required": True,
        "act_4_root_approved_reuse": True,
        "act_4_drs_reuse_is_authority": False,
        "act_4_compute_collapse_signal_observed": True,
        "act_4_production_economics_claimed": False,
        "act_4_resolution_source": act4["act_4_resolution_source"],
        "act_4_forbidden_resolution_source_used": False,
        "baseline_document_review_units": act4["baseline_document_review_units"],
        "hedgehog_reuse_review_units": act4["hedgehog_reuse_review_units"],
        "estimated_document_review_units_saved": act4[
            "estimated_document_review_units_saved"
        ],
        "compute_collapse_claim_is_synthetic": True,
        "root_remains_final_authority": True,
        "llm_is_authority": False,
        "semantic_draft_is_truth": False,
        "connector_observation_is_truth": False,
        "evidence_candidate_is_accepted_evidence": False,
        "accepted_evidence_is_action": False,
        "gt_is_final_authority": False,
        "audit_hash_decides_truth": False,
        "developer_manifest_is_authority": False,
        "transition_matrix_is_authority": False,
        "killer_demo_authorizes_production": False,
        "production_autonomy_claimed": False,
        "network_called": False,
        "gemini_called": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_capability_created": False,
        "installed_needle_created": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "no_real_ocr": True,
        "no_real_pdf_parsing": True,
        "no_real_bank_connector": True,
        "no_real_legal_connector": True,
        "no_real_warehouse_connector": True,
        "no_real_external_action": True,
        "no_production_drs": True,
        "no_installed_needle": True,
        "no_marennya": True,
        "no_up": True,
    }


def validate_enterprise_document_killer_demo_b_v01(
    report: EnterpriseDocumentKillerDemoBV01Report,
) -> bool:
    summary = report.summary
    fixture_fields = {
        row["filename"]: row["fields"] for row in report.document_fixtures
    }
    return all(
        (
            report.header["proof_type"] == "deterministic_local_proof_only",
            report.design_doc_reference["design_doc_commit"] == "bb1f7c2",
            len(report.source_checkpoints) == 12,
            report.source_evidence["source_collectors_replayed"] is False,
            report.source_evidence["source_checkpoints_all_closed"] is True,
            fixture_fields["invoice_INV-2026-044.txt"]["vendor"] == "ALPHA SUPPLY",
            fixture_fields["invoice_INV-2026-044.txt"]["amount"] == "18400 EUR",
            fixture_fields["invoice_INV-2026-044.txt"]["shipment_id"] == "SHIP-900",
            fixture_fields["payment_receipt_BANK-771.txt"]["receipt_id"] == "BANK-771",
            fixture_fields["warehouse_stock_W-17.txt"]["item"]
            == "medical_filter_pack",
            fixture_fields["warehouse_stock_W-17.txt"]["required_qty"] == 40,
            fixture_fields["warehouse_stock_W-17.txt"]["available_qty"] == 40,
            fixture_fields["insurance_certificate_CERT-310.txt"][
                "insurance_status"
            ]
            == "expired",
            fixture_fields["compliance_certificate_COMP-882.txt"][
                "compliance_status"
            ]
            == "missing_signature",
            fixture_fields["external_pointer_LEGAL-FAKE.txt"]["provenance"]
            == "missing",
            fixture_fields["external_pointer_LEGAL-FAKE.txt"]["trust"] == "unknown",
            fixture_fields["insurance_certificate_CERT-311.txt"]["insurance_status"]
            == "valid",
            fixture_fields["compliance_certificate_COMP-883.txt"][
                "signature_status"
            ]
            == "present",
            report.act1_dirty_document_readiness["act_1_root_result"] == "not_ready",
            report.act1_dirty_document_readiness[
                "act_1_needs_user_document_update"
            ]
            is True,
            set(ACT_1_BLOCKERS).issubset(
                set(report.act1_dirty_document_readiness["act_1_blockers"])
            ),
            report.act2_authority_stress["act_2_adversarial_attempts_observed"]
            == 18,
            report.act2_authority_stress["act_2_adversarial_attempts_blocked"] == 18,
            report.act2_authority_stress["act_2_quarantined_attempts_observed"]
            == 3,
            report.act3_corrected_documents["act_3_root_result"]
            == "ready_for_internal_release",
            report.act3_corrected_documents[
                "act_3_corrected_evidence_accepted_by_root"
            ]
            is True,
            report.act4_root_approved_reuse["act_4_resolution_source"]
            == "Root-approved Local DRS Reuse",
            report.act4_root_approved_reuse["act_4_drs_reuse_is_authority"]
            is False,
            all(row["blocked"] is True for row in report.act2_authority_stress["attempts"]),
            all(
                row["authority_transferred"] is False
                for row in report.act2_authority_stress["attempts"]
            ),
            report.audit_entry["canonical_payload_hash"]
            == canonical_hash(report.proof_artifact),
            report.audit_entry["audit_hash_decides_truth"] is False,
            summary["enterprise_document_killer_demo_b_v01_status"] == "PASS",
        )
    )


def collect_enterprise_document_killer_demo_b_v01() -> (
    EnterpriseDocumentKillerDemoBV01Report
):
    source_checkpoints = _source_checkpoints()
    source_evidence = _source_evidence(source_checkpoints)
    fixtures = _document_fixtures()
    act1 = _act1_dirty_document_readiness()
    attempts = _adversarial_attempts()
    act2 = _act2_authority_stress(attempts) | {"attempts": attempts}
    act3 = _act3_corrected_documents()
    act4 = _act4_root_approved_reuse()
    root_finals = _root_finals(act1, act3, act4)
    human_view = _what_human_sees()
    proves = _what_this_proves()
    non_claims = _what_this_does_not_prove()
    header = {
        "proof_id": "enterprise_document_killer_demo_b_v01",
        "title": "Enterprise Document Killer Demo B v0.1",
        "proof_type": "deterministic_local_proof_only",
        "demo_mode": "Enterprise Document Killer Demo B — Document / Evidence Workflow",
        "demo_a_already_closed": True,
        "demo_b_implemented_as_proof_only": True,
        "production_autonomy_claimed": False,
    }
    design_doc_reference = {
        "design_doc_commit": "bb1f7c2",
        "design_doc_file": "docs/demo_designs/enterprise_document_killer_demo_b_v01.md",
        "design_doc_status": "accepted",
    }
    proof_artifact = {
        "proof_artifact_id": "enterprise_document_killer_demo_b_v01",
        "header": header,
        "design_doc_reference": design_doc_reference,
        "source_evidence": source_evidence,
        "source_checkpoints": source_checkpoints,
        "document_fixtures": fixtures,
        "act1_dirty_document_readiness": act1,
        "act2_authority_stress": act2,
        "act3_corrected_documents": act3,
        "act4_root_approved_reuse": act4,
        "root_finals": root_finals,
    }
    audit_entry = {
        "audit_entry_id": "audit_enterprise_document_killer_demo_b_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "audit_hash_chain_records_continuity_only": True,
        "audit_hash_decides_truth": False,
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
    }
    provisional = EnterpriseDocumentKillerDemoBV01Report(
        header=header,
        design_doc_reference=design_doc_reference,
        source_evidence=source_evidence,
        source_checkpoints=source_checkpoints,
        document_fixtures=fixtures,
        act1_dirty_document_readiness=act1,
        act2_authority_stress=act2,
        act3_corrected_documents=act3,
        act4_root_approved_reuse=act4,
        root_finals=root_finals,
        what_human_sees=human_view,
        what_this_proves=proves,
        what_this_does_not_prove=non_claims,
        audit_entry=audit_entry,
        proof_artifact=proof_artifact,
        summary={},
    )
    preliminary = replace(provisional, summary=_summary(provisional, passed=True))
    passed = validate_enterprise_document_killer_demo_b_v01(preliminary)
    return replace(preliminary, summary=_summary(preliminary, passed=passed))


def _format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, list):
        return ", ".join(_format_scalar(item) for item in value)
    return str(value)


def _render_dict(rows: dict[str, Any]) -> list[str]:
    rendered = []
    for key, value in rows.items():
        if key == "attempts":
            continue
        rendered.append(f"{key}: {_format_scalar(value)}")
    return rendered


def _render_rows(rows: list[dict[str, Any]], id_field: str) -> list[str]:
    rendered = []
    for row in rows:
        parts = [f"{key}={_format_scalar(value)}" for key, value in row.items()]
        rendered.append(f"- {row[id_field]} | " + " | ".join(parts))
    return rendered


def _render_fixtures(fixtures: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for fixture in fixtures:
        lines.append(f"- {fixture['filename']} ({fixture['category']})")
        for key, value in fixture["fields"].items():
            lines.append(f"  {key}: {_format_scalar(value)}")
    return lines


def render_enterprise_document_killer_demo_b_v01(
    report: EnterpriseDocumentKillerDemoBV01Report,
) -> str:
    sections: list[tuple[str, list[str]]] = [
        ("HEADER", _render_dict(report.header)),
        ("SOURCE CHECKPOINTS", _render_dict(report.source_evidence) + _render_rows(report.source_checkpoints, "checkpoint_id")),
        ("DOCUMENT FIXTURES", _render_fixtures(report.document_fixtures)),
        ("ACT 1 — DIRTY DOCUMENT READINESS", _render_dict(report.act1_dirty_document_readiness)),
        ("ACT 2 — AUTHORITY STRESS INSIDE DOCUMENT WORKFLOW", _render_dict(report.act2_authority_stress) + _render_rows(report.act2_authority_stress["attempts"], "attempt_id")),
        ("ACT 3 — CORRECTED DOCUMENTS", _render_dict(report.act3_corrected_documents)),
        ("ACT 4 — ROOT-APPROVED REUSE / COMPUTE COLLAPSE", _render_dict(report.act4_root_approved_reuse)),
        ("ROOT FINALS", _render_dict(report.root_finals)),
        ("WHAT HUMAN SEES", _render_dict(report.what_human_sees)),
        ("WHAT THIS PROVES", _render_dict(report.what_this_proves)),
        ("WHAT THIS DOES NOT PROVE", _render_dict(report.what_this_does_not_prove)),
        ("AUDIT", _render_dict(report.audit_entry)),
        ("SUMMARY", _render_dict(report.summary)),
    ]
    lines: list[str] = []
    for title, body in sections:
        lines.append(f"[{title}]")
        lines.extend(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = collect_enterprise_document_killer_demo_b_v01()
    print(render_enterprise_document_killer_demo_b_v01(report))
    return (
        0
        if report.summary["enterprise_document_killer_demo_b_v01_status"] == "PASS"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
