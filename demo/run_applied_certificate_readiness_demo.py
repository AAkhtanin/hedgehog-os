from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
)
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_root_orchestrator_route_assembly import (
    collect_controlled_root_orchestrator_route_assembly,
)
from demo.run_dag_executor_from_valid_plan_graph import (
    collect_dag_executor_from_valid_plan_graph,
)
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_gt_from_validation_report import collect_gt_from_validation_report
from demo.run_post_vv_from_result_proposal import (
    collect_post_vv_from_result_proposal,
)
from demo.run_root_final_from_gt_decision import collect_root_final_from_gt_decision


USER_TASK = (
    "Create a proof-level readiness certificate for application APP-77. Check "
    "local document state, detect missing or expired documents, reject invalid "
    "ready claims, and produce a Root-final summary. Do not submit anything "
    "externally."
)
REQUIRED_DOCUMENTS = [
    "passport_scan",
    "residency_proof",
    "insurance_certificate",
    "payment_receipt",
]
LOCAL_DOCUMENTS = {
    "passport_scan": {"status": "present", "expiry_status": "valid"},
    "residency_proof": {"status": "present", "expiry_status": "valid"},
    "insurance_certificate": {"status": "present", "expiry_status": "expired"},
    "payment_receipt": {"status": "missing", "expiry_status": "not_applicable"},
}


@dataclass(frozen=True)
class AppliedCertificateReadinessReport:
    input_mode: dict[str, Any]
    user_event: dict[str, Any]
    worldstate: dict[str, Any]
    drs_retrieval: dict[str, Any]
    controlled_route_assembly: dict[str, Any]
    matrix_route_gate: dict[str, Any]
    avf_attractor_packet: dict[str, Any]
    applied_certificate_plan_graph: dict[str, Any]
    document_check_results: dict[str, Any]
    architect_plan: dict[str, Any]
    dag_execution: dict[str, Any]
    result_proposals: list[dict[str, Any]]
    applied_validation_rows: list[dict[str, Any]]
    post_vv: dict[str, Any]
    applied_gt_selection: dict[str, Any]
    gt: dict[str, Any]
    root_final: dict[str, Any]
    applied_drs_lifecycle_records: list[dict[str, Any]]
    drs_lifecycle: dict[str, Any]
    applied_conflict_reports: list[dict[str, Any]]
    conflictcheck: dict[str, Any]
    applied_artifact: dict[str, Any]
    applied_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    malicious_unsafe_claims: dict[str, bool]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _row_map(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _worldstate() -> dict[str, Any]:
    return {
        "application_id": "APP-77",
        "certificate_request_id": "CERT-310",
        "requested_certificate_type": "travel_document_readiness",
        "required_documents": REQUIRED_DOCUMENTS,
        "local_documents": LOCAL_DOCUMENTS,
        "blocking_items": {
            "insurance_certificate": "expired",
            "payment_receipt": "missing",
        },
        "freshness_status": "current_for_demo",
        "assumptions": [
            "local-only data",
            "no external submission",
            "proof-level certificate only",
        ],
        "worldstate_assembled": True,
        "worldstate_source": "deterministic_local_fixture",
    }


def _plan_graph() -> dict[str, Any]:
    return {
        "plan_graph_id": "applied_certificate_plan_graph_APP77_CERT310",
        "source": "bounded_attractor_packet",
        "raw_user_text_received": False,
        "nodes": [
            {"node_id": "document_presence_check_node", "node_kind": "atomic"},
            {"node_id": "document_expiry_check_node", "node_kind": "atomic"},
            {
                "node_id": "readiness_certificate_draft_node",
                "node_kind": "non_atomic",
            },
            {"node_id": "no_external_submission_guard_node", "node_kind": "guard"},
        ],
        "edges": [
            {
                "from": "document_presence_check_node",
                "to": "readiness_certificate_draft_node",
            },
            {
                "from": "document_expiry_check_node",
                "to": "readiness_certificate_draft_node",
            },
            {
                "from": "no_external_submission_guard_node",
                "to": "readiness_certificate_draft_node",
            },
        ],
        "contract_valid": True,
    }


def _document_check_results() -> dict[str, Any]:
    return {
        "document_presence_check_result": {
            "passport_scan": "present",
            "residency_proof": "present",
            "insurance_certificate": "present",
            "payment_receipt": "missing",
        },
        "document_expiry_check_result": {
            "passport_scan": "valid",
            "residency_proof": "valid",
            "insurance_certificate": "expired",
            "payment_receipt": "not_applicable",
        },
        "readiness_certificate_draft_result": {
            "certificate_readiness": "not_ready",
            "blocking_reasons": [
                "insurance_certificate expired",
                "payment_receipt missing",
            ],
        },
        "no_external_submission_guard_result": {
            "no_external_submission_executed": True,
            "external_submission_blocked": True,
        },
    }


def _result_proposals() -> list[dict[str, Any]]:
    return [
        {
            "result_proposal_id": "completed_not_ready_certificate",
            "status": "completed",
            "certificate_readiness": "not_ready",
            "blocking_reasons": [
                "insurance_certificate expired",
                "payment_receipt missing",
            ],
            "safe_for_root_final": True,
            "final_output_claim": False,
        },
        {
            "result_proposal_id": "invalid_ready_certificate",
            "status": "rejected",
            "certificate_readiness": "ready",
            "reason": (
                "contradicts expired insurance_certificate and missing "
                "payment_receipt"
            ),
            "safe_for_root_final": False,
            "final_output_claim": False,
        },
        {
            "result_proposal_id": "needs_user_document_update",
            "status": "needs_user",
            "certificate_readiness": "not_ready",
            "reason": (
                "payment_receipt missing and insurance_certificate expired"
            ),
            "safe_for_root_final": True,
            "final_output_claim": False,
        },
    ]


def _validation_rows() -> list[dict[str, Any]]:
    return [
        {
            "result_proposal_id": "completed_not_ready_certificate",
            "validation_status": "accepted",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "safety_valid": True,
            "consistency_valid": True,
            "reason": "matches missing and expired local documents",
        },
        {
            "result_proposal_id": "invalid_ready_certificate",
            "validation_status": "rejected",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "safety_valid": False,
            "consistency_valid": False,
            "reason": (
                "contradicts insurance_certificate expired and "
                "payment_receipt missing"
            ),
        },
        {
            "result_proposal_id": "needs_user_document_update",
            "validation_status": "needs_user_valid",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "safety_valid": True,
            "consistency_valid": True,
            "reason": "document update required before submission",
        },
    ]


def _gt_selection() -> dict[str, Any]:
    return {
        "selected_result_proposal_id": "completed_not_ready_certificate",
        "secondary_result_proposal_id": "needs_user_document_update",
        "rejected_result_proposal_ids": ["invalid_ready_certificate"],
        "selection_reason": (
            "not_ready matches local evidence; needs_user remains a secondary "
            "operational recommendation"
        ),
        "gt_is_not_truth_proof": True,
    }


def _lifecycle_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "certificate_experience_record_APP77_CERT310",
            "record_type": "experience_record",
            "experience_status": "completed_not_ready",
            "source_result_proposal_id": "completed_not_ready_certificate",
            "root_authorized_writeback": True,
            "proof_only": True,
        },
        {
            "record_id": "certificate_reuse_candidate_APP77_CERT310",
            "record_type": "reuse_candidate",
            "source_experience_record_id": (
                "certificate_experience_record_APP77_CERT310"
            ),
            "proof_only": True,
        },
        {
            "record_id": "certificate_invalid_ready_quarantine_APP77_CERT310",
            "record_type": "quarantine",
            "source_result_proposal_id": "invalid_ready_certificate",
            "quarantine_reason": "ready claim contradicts missing/expired documents",
            "proof_only": True,
        },
        {
            "record_id": "certificate_external_submission_deadend_APP77_CERT310",
            "record_type": "deadend",
            "deadend_reason": "external submission is outside proof boundary",
            "proof_only": True,
        },
    ]


def _conflict_reports() -> list[dict[str, Any]]:
    return [
        {
            "conflict_report_id": (
                "conflict_invalid_ready_vs_missing_expired_docs_APP77_CERT310"
            ),
            "conflict_type": "missing_or_expired_docs_vs_ready_certificate",
            "left_source": (
                "worldstate.insurance_certificate=expired + "
                "payment_receipt=missing"
            ),
            "right_source": (
                "invalid_ready_certificate.certificate_readiness=ready"
            ),
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": "no_conflict_completed_not_ready_APP77_CERT310",
            "conflict_type": "no_conflict",
            "left_source": (
                "worldstate.insurance_certificate=expired + "
                "payment_receipt=missing"
            ),
            "right_source": (
                "completed_not_ready_certificate.certificate_readiness=not_ready"
            ),
            "conflict_detected": False,
            "root_review_required": False,
            "conflictcheck_is_authority": False,
        },
    ]


def _malicious_claims() -> dict[str, bool]:
    claims = (
        "ready_certificate_despite_missing_or_expired_docs",
        "external_submission_executed",
        "orchestrator_created_final_output",
        "orchestrator_wrote_drs",
        "avf_bypassed",
        "hardmask_overridden",
        "conflictcheck_decided_truth",
        "audit_chain_decided_truth",
        "protocol_candidate_created",
        "needle_candidate_created",
        "production_persistence_created",
        "global_or_external_drs_write",
        "marennya_or_up_invoked",
        "needleforge_invoked",
    )
    return {f"{claim}_rejected": True for claim in claims}


def validate_applied_certificate_report_consistency(
    report: AppliedCertificateReadinessReport,
) -> bool:
    node_ids = {
        node["node_id"]
        for node in report.applied_certificate_plan_graph.get("nodes", [])
    }
    validations = _row_map(report.applied_validation_rows, "result_proposal_id")
    lifecycle = _row_map(report.applied_drs_lifecycle_records, "record_id")
    conflicts = _row_map(report.applied_conflict_reports, "conflict_report_id")
    required_nodes = {
        "document_presence_check_node",
        "document_expiry_check_node",
        "readiness_certificate_draft_node",
        "no_external_submission_guard_node",
    }
    required_records = {
        "certificate_experience_record_APP77_CERT310": "experience_record",
        "certificate_reuse_candidate_APP77_CERT310": "reuse_candidate",
        "certificate_invalid_ready_quarantine_APP77_CERT310": "quarantine",
        "certificate_external_submission_deadend_APP77_CERT310": "deadend",
    }
    conflict = conflicts.get(
        "conflict_invalid_ready_vs_missing_expired_docs_APP77_CERT310", {}
    )
    no_conflict = conflicts.get(
        "no_conflict_completed_not_ready_APP77_CERT310", {}
    )
    audit = report.applied_audit_entry
    return all(
        (
            required_nodes.issubset(node_ids),
            report.applied_certificate_plan_graph.get("contract_valid") is True,
            report.document_check_results.get(
                "document_presence_check_result", {}
            ).get("payment_receipt")
            == "missing",
            report.document_check_results.get(
                "document_expiry_check_result", {}
            ).get("insurance_certificate")
            == "expired",
            report.document_check_results.get(
                "readiness_certificate_draft_result", {}
            ).get("certificate_readiness")
            == "not_ready",
            validations.get("completed_not_ready_certificate", {}).get(
                "validation_status"
            )
            == "accepted",
            validations.get("invalid_ready_certificate", {}).get(
                "validation_status"
            )
            == "rejected",
            validations.get("needs_user_document_update", {}).get(
                "validation_status"
            )
            == "needs_user_valid",
            report.applied_gt_selection.get("selected_result_proposal_id")
            == "completed_not_ready_certificate",
            report.applied_gt_selection.get("secondary_result_proposal_id")
            == "needs_user_document_update",
            report.root_final.get("certificate_readiness") == "not_ready",
            all(
                lifecycle.get(record_id, {}).get("record_type") == record_type
                for record_id, record_type in required_records.items()
            ),
            conflict.get("conflict_type")
            == "missing_or_expired_docs_vs_ready_certificate",
            conflict.get("conflict_detected") is True,
            no_conflict.get("conflict_detected") is False,
            audit.get("audit_entry_id") == "audit_applied_certificate_APP77_CERT310",
            audit.get("canonical_payload_hash")
            == canonical_hash(report.applied_artifact),
            audit.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            report.drs_lifecycle.get("protocol_candidate_created") is False,
            report.drs_lifecycle.get("needle_candidate_created") is False,
            report.drs_lifecycle.get("installed_needle_created") is False,
            report.authority_safety.get("root_remains_final_authority") is True,
            report.authority_safety.get("production_autonomy_claimed") is False,
        )
    )


def collect_applied_certificate_readiness_demo() -> AppliedCertificateReadinessReport:
    route_source = collect_controlled_root_orchestrator_route_assembly()
    avf_source = collect_avf_attractor_from_accepted_matrix()
    architect_source = collect_architect_from_bounded_attractor_packet()
    dag_source = collect_dag_executor_from_valid_plan_graph()
    post_source = collect_post_vv_from_result_proposal()
    gt_source = collect_gt_from_validation_report()
    root_source = collect_root_final_from_gt_decision()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    worldstate = _worldstate()
    plan_graph = _plan_graph()
    checks = _document_check_results()
    proposals = _result_proposals()
    validations = _validation_rows()
    validation_by_id = _row_map(validations, "result_proposal_id")
    gt_selection = _gt_selection()
    lifecycle_records = _lifecycle_records()
    lifecycle_by_id = _row_map(lifecycle_records, "record_id")
    conflict_reports = _conflict_reports()
    conflict_by_id = _row_map(conflict_reports, "conflict_report_id")
    malicious = _malicious_claims()

    input_mode = {
        "mode": "deterministic_applied_certificate_readiness_demo",
        "local_proof_level_only": True,
        "live_network_used": False,
        "telegram_used": False,
        "real_external_action": False,
        "production_persistence": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "needleforge_invoked": False,
    }
    user_event = {
        "event_id": "certificate_event_APP77_CERT310",
        "user_task": USER_TASK,
        "application_id": "APP-77",
        "certificate_request_id": "CERT-310",
        "requested_certificate_type": "travel_document_readiness",
        "proof_only": True,
    }
    drs_retrieval = {
        "drs_retrieval_requested": True,
        "drs_retrieval_scope": "local_proof_only",
        "retrieved_records_count": 4,
        "retrieved_context_types": [
            "previous_document_readiness_pattern",
            "previous_expired_document_deadend",
            "previous_invalid_ready_conflict",
            "previous_local_document_check_reuse_candidate",
        ],
        "retrieved_context_applied": True,
        "no_global_or_external_drs_used": True,
    }
    controlled = {
        "controlled_route_assembly_source_status": route_source.summary[
            "controlled_root_orchestrator_route_assembly_status"
        ],
        "orchestrator_has_bounded_delegated_authority": route_source.summary[
            "orchestrator_has_bounded_delegated_authority"
        ],
        "orchestrator_proposes_avf_inputs": route_source.avf_hardmask[
            "orchestrator_proposes_avf_inputs"
        ],
        "orchestrator_manages_avf": False,
        "orchestrator_is_root": False,
        "orchestrator_writes_drs": False,
        "orchestrator_creates_final_output": False,
        "orchestrator_executes_actions": False,
    }
    gate = {
        "root_validates_orchestrator_proposal": route_source.summary[
            "root_validates_orchestrator_proposal"
        ],
        "matrix_gate_after_orchestrator": route_source.summary[
            "matrix_gate_after_orchestrator"
        ],
        "route_gate_after_orchestrator": True,
        "policy_constraints_applied": True,
        "invalid_ready_claim_blocked": bool(worldstate["blocking_items"]),
        "external_submission_blocked": True,
        "proposal_allowed_to_avf": True,
    }
    avf = {
        "avf_source_status": avf_source.summary["avf_attractor_from_accepted_matrix_status"],
        "avf_after_matrix_gate": route_source.summary["avf_after_matrix_gate"],
        "avf_independent_filter_scoring_layer": route_source.avf_hardmask[
            "avf_independent_filter_scoring_layer"
        ],
        "hardmask_beats_orchestrator_confidence": route_source.summary[
            "hardmask_beats_orchestrator_confidence"
        ],
        "missing_expired_document_vector_preserved": True,
        "false_ready_vector_blocked": True,
        "external_submission_vector_blocked": True,
        "attractor_packet_created": avf_source.summary["attractor_packets_created"] > 0,
        "architect_receives_bounded_attractor_packet": True,
    }
    node_ids = {node["node_id"] for node in plan_graph["nodes"]}
    architect = {
        "architect_source_status": architect_source.summary[
            "architect_from_bounded_attractor_packet_status"
        ],
        "architect_receives_bounded_attractor_packet": True,
        "architect_receives_raw_user_text": False,
        "plan_graph_created": True,
        "required_plan_nodes_present": {
            "document_presence_check_node",
            "document_expiry_check_node",
            "readiness_certificate_draft_node",
            "no_external_submission_guard_node",
        }.issubset(node_ids),
        "plan_graph_contract_valid": plan_graph["contract_valid"],
    }
    dag = {
        "dag_source_status": dag_source.summary["dag_executor_from_valid_plan_graph_status"],
        "executor_receives_plan_graph_not_raw_user_text": dag_source.summary[
            "executor_receives_only_validated_plan_graph_nodes"
        ]
        and dag_source.summary["raw_user_intent_blocked"],
        "document_presence_check_completed": (
            checks["document_presence_check_result"]["payment_receipt"] == "missing"
        ),
        "document_expiry_check_completed": (
            checks["document_expiry_check_result"]["insurance_certificate"]
            == "expired"
        ),
        "invalid_ready_result_blocked": (
            checks["readiness_certificate_draft_result"]["certificate_readiness"]
            == "not_ready"
        ),
        "no_external_submission_executed": checks[
            "no_external_submission_guard_result"
        ]["no_external_submission_executed"],
        "node_results_created": len(checks),
    }
    post_vv = {
        "post_vv_source_status": post_source.summary["post_vv_from_result_proposal_status"],
        "post_vv_reached": True,
        "completed_not_ready_certificate_valid": validation_by_id[
            "completed_not_ready_certificate"
        ]["validation_status"]
        == "accepted",
        "invalid_ready_certificate_rejected": validation_by_id[
            "invalid_ready_certificate"
        ]["validation_status"]
        == "rejected",
        "needs_user_document_update_valid": validation_by_id[
            "needs_user_document_update"
        ]["validation_status"]
        == "needs_user_valid",
    }
    gt = {
        "gt_source_status": gt_source.summary["gt_from_validation_report_status"],
        "gt_reached": True,
        "gt_is_not_truth_proof": gt_selection["gt_is_not_truth_proof"],
        "selected_result_proposal_id": gt_selection["selected_result_proposal_id"],
        "secondary_result_proposal_id": gt_selection["secondary_result_proposal_id"],
        "rejected_result_proposal_ids": gt_selection["rejected_result_proposal_ids"],
    }
    root_final = {
        "root_final_source_status": root_source.summary["root_final_from_gt_decision_status"],
        "root_final_created": True,
        "root_created_final_output": True,
        "root_is_only_final_output_authority": root_source.summary[
            "root_is_only_final_output_authority"
        ],
        "certificate_readiness": "not_ready",
        "blocking_reasons": [
            "insurance_certificate expired",
            "payment_receipt missing",
        ],
        "ready_documents": ["passport_scan", "residency_proof"],
        "invalid_ready_claim_rejected": True,
        "recommended_next_step": (
            "ask_user_to_upload_payment_receipt_and_refresh_insurance_certificate"
        ),
        "no_external_submission_executed": True,
        "proof_level_certificate_only": True,
    }
    lifecycle = {
        "drs_lifecycle_source_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "drs_lifecycle_after_root_final": True,
        "experience_record_created": lifecycle_by_id[
            "certificate_experience_record_APP77_CERT310"
        ]["record_type"]
        == "experience_record",
        "reuse_candidate_created": lifecycle_by_id[
            "certificate_reuse_candidate_APP77_CERT310"
        ]["record_type"]
        == "reuse_candidate",
        "quarantine_record_created": lifecycle_by_id[
            "certificate_invalid_ready_quarantine_APP77_CERT310"
        ]["record_type"]
        == "quarantine",
        "deadend_record_created": lifecycle_by_id[
            "certificate_external_submission_deadend_APP77_CERT310"
        ]["record_type"]
        == "deadend",
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "root_authorized_writeback": lifecycle_source.summary[
            "root_remains_commit_authority"
        ],
    }
    conflict = {
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "conflictcheck_after_drs_lifecycle": conflict_source.summary[
            "source_drs_lifecycle_status"
        ]
        == "PASS",
        "invalid_ready_conflict_detected": conflict_by_id[
            "conflict_invalid_ready_vs_missing_expired_docs_APP77_CERT310"
        ]["conflict_detected"],
        "completed_not_ready_no_conflict": not conflict_by_id[
            "no_conflict_completed_not_ready_APP77_CERT310"
        ]["conflict_detected"],
        "conflictcheck_is_authority": False,
    }
    applied_artifact = {
        "artifact_id": "applied_certificate_artifact_APP77_CERT310",
        "worldstate": worldstate,
        "applied_certificate_plan_graph": plan_graph,
        "document_check_results": checks,
        "result_proposals": proposals,
        "applied_validation_rows": validations,
        "applied_gt_selection": gt_selection,
        "root_final": root_final,
        "applied_drs_lifecycle_records": lifecycle_records,
        "applied_conflict_reports": conflict_reports,
    }
    applied_audit_entry = {
        "audit_entry_id": "audit_applied_certificate_APP77_CERT310",
        "entry_type": "applied_certificate_readiness_artifact",
        "source_artifact_type": "AppliedCertificateReadinessArtifact",
        "source_artifact_id": "applied_certificate_artifact_APP77_CERT310",
        "canonical_payload_hash": canonical_hash(applied_artifact),
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "audit_chain_decides_truth": False,
    }
    audit = {
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
        "audit_hash_chain_after_conflictcheck": audit_source.source_reports[
            "conflictcheck_status"
        ]
        == "PASS",
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "applied_audit_entry_created": bool(applied_audit_entry),
        "applied_artifact_hash_linked": (
            applied_audit_entry["canonical_payload_hash"]
            == canonical_hash(applied_artifact)
        ),
        "hash_chain_proves_continuity_not_truth": True,
        "production_persistence": False,
    }
    authority = {
        "root_sovereign": True,
        "orchestrator_has_bounded_delegated_authority": controlled[
            "orchestrator_has_bounded_delegated_authority"
        ],
        "orchestrator_is_root": False,
        "orchestrator_writes_drs": False,
        "orchestrator_creates_final_output": False,
        "avf_remains_independent": avf["avf_independent_filter_scoring_layer"],
        "hardmask_remains_stronger_than_orchestrator_confidence": avf[
            "hardmask_beats_orchestrator_confidence"
        ],
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "audit_hash_chain_proves_continuity_not_truth": True,
        "root_remains_final_authority": root_final[
            "root_is_only_final_output_authority"
        ],
        "production_autonomy_claimed": False,
    }
    provisional = AppliedCertificateReadinessReport(
        input_mode=input_mode,
        user_event=user_event,
        worldstate=worldstate,
        drs_retrieval=drs_retrieval,
        controlled_route_assembly=controlled,
        matrix_route_gate=gate,
        avf_attractor_packet=avf,
        applied_certificate_plan_graph=plan_graph,
        document_check_results=checks,
        architect_plan=architect,
        dag_execution=dag,
        result_proposals=proposals,
        applied_validation_rows=validations,
        post_vv=post_vv,
        applied_gt_selection=gt_selection,
        gt=gt,
        root_final=root_final,
        applied_drs_lifecycle_records=lifecycle_records,
        drs_lifecycle=lifecycle,
        applied_conflict_reports=conflict_reports,
        conflictcheck=conflict,
        applied_artifact=applied_artifact,
        applied_audit_entry=applied_audit_entry,
        audit_hash_chain=audit,
        malicious_unsafe_claims=malicious,
        authority_safety=authority,
        summary={},
    )
    source_statuses = (
        controlled["controlled_route_assembly_source_status"],
        avf["avf_source_status"],
        architect["architect_source_status"],
        dag["dag_source_status"],
        post_vv["post_vv_source_status"],
        gt["gt_source_status"],
        root_final["root_final_source_status"],
        lifecycle["drs_lifecycle_source_status"],
        conflict["conflictcheck_source_status"],
        audit["audit_hash_chain_source_status"],
    )
    pass_facts = (
        all(status == "PASS" for status in source_statuses)
        and validate_applied_certificate_report_consistency(provisional)
        and all(malicious.values())
        and input_mode["live_network_used"] is False
        and input_mode["real_external_action"] is False
        and lifecycle["protocol_candidate_created"] is False
        and lifecycle["needle_candidate_created"] is False
    )
    return replace(
        provisional,
        summary={
            "applied_certificate_readiness_demo_status": (
                "PASS" if pass_facts else "FAIL"
            ),
            "application_id": "APP-77",
            "certificate_request_id": "CERT-310",
            "certificate_readiness": root_final["certificate_readiness"],
            "blocking_reasons": root_final["blocking_reasons"],
            "invalid_ready_certificate_rejected": post_vv[
                "invalid_ready_certificate_rejected"
            ],
            "no_external_submission_executed": root_final[
                "no_external_submission_executed"
            ],
            "protocol_candidate_created": lifecycle["protocol_candidate_created"],
            "needle_candidate_created": lifecycle["needle_candidate_created"],
            "applied_audit_entry_created": audit["applied_audit_entry_created"],
            "explicit_applied_artifacts_consistent": (
                validate_applied_certificate_report_consistency(provisional)
            ),
            "malicious_claims_rejected": sum(malicious.values()),
            "root_remains_final_authority": authority["root_remains_final_authority"],
            "ready_for_applied_certificate_docs_sync": pass_facts,
            "production_autonomy_claimed": False,
        },
    )


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_applied_certificate_readiness_demo(
    report: AppliedCertificateReadinessReport,
) -> str:
    lines = [
        "[APPLIED CERTIFICATE READINESS DEMO]",
        "note: deterministic applied certificate/document readiness proof",
        "note: local proof-level only; no external submission or production persistence",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[USER EVENT]", report.user_event)
    _section(lines, "[WORLDSTATE]", report.worldstate)
    _section(lines, "[DRS RETRIEVAL]", report.drs_retrieval)
    _section(lines, "[CONTROLLED ROUTE ASSEMBLY]", report.controlled_route_assembly)
    _section(lines, "[MATRIX GATE / ROUTE GATE]", report.matrix_route_gate)
    _section(lines, "[AVF / ATTRACTOR PACKET]", report.avf_attractor_packet)
    _section(lines, "[APPLIED PLAN GRAPH]", report.applied_certificate_plan_graph)
    _section(lines, "[DOCUMENT CHECK RESULTS]", report.document_check_results)
    _section(lines, "[ARCHITECT / PLAN]", report.architect_plan)
    _section(lines, "[DAG / EXECUTION]", report.dag_execution)
    _rows(lines, "[RESULT PROPOSALS]", report.result_proposals)
    _rows(lines, "[APPLIED VALIDATION ROWS]", report.applied_validation_rows)
    _section(lines, "[POST V&V]", report.post_vv)
    _section(lines, "[APPLIED GT SELECTION]", report.applied_gt_selection)
    _section(lines, "[GT]", report.gt)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _rows(
        lines,
        "[APPLIED DRS LIFECYCLE RECORDS]",
        report.applied_drs_lifecycle_records,
    )
    _section(lines, "[DRS LIFECYCLE]", report.drs_lifecycle)
    _rows(lines, "[APPLIED CONFLICT REPORTS]", report.applied_conflict_reports)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck)
    _section(lines, "[APPLIED AUDIT ENTRY]", report.applied_audit_entry)
    _section(lines, "[AUDIT HASH-CHAIN]", report.audit_hash_chain)
    _section(lines, "[MALICIOUS / UNSAFE CLAIMS]", report.malicious_unsafe_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_applied_certificate_readiness_demo() -> str:
    return render_applied_certificate_readiness_demo(
        collect_applied_certificate_readiness_demo()
    )


def main() -> int:
    print(run_applied_certificate_readiness_demo(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
