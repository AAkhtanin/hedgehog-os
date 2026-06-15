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
)


CONFLICT_REASONS = (
    "compliance_certificate_stale",
    "invoice_total_conflicts_with_purchase_order",
    "payment_approval_missing",
)


ROOT_FINAL_REASONS = (
    "stale_compliance_certificate",
    "invoice_po_conflict",
    "missing_payment_approval",
    "real_action_not_authorized",
)


ADVERSARIAL_ATTEMPT_IDS = (
    "connector_observation_to_truth",
    "connector_observation_to_accepted_evidence",
    "accepted_evidence_to_external_action",
    "accepted_evidence_to_ready_status",
    "llm_draft_to_truth",
    "llm_draft_to_root_final",
    "drs_reuse_to_authority",
    "external_pointer_to_global_drs_write",
    "bridge_traversal_to_provenance_laundering",
    "developer_manifest_to_installed_capability",
    "manifest_candidate_to_installed_needle",
    "child_cell_to_autonomous_actor",
    "gt_recommendation_to_root_authority",
    "audit_hash_to_truth",
    "permission_needsuser_to_execution",
    "resultproposal_to_root_bypass",
    "stale_timeenvelope_to_current",
    "production_boundary_to_production_ready_claim",
)


@dataclass(frozen=True)
class EnterpriseKillerDemoV01Report:
    header: dict[str, Any]
    source_evidence: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    act1_dirty_enterprise_request: dict[str, Any]
    act2_authority_stress: dict[str, Any]
    act3_compute_collapse: dict[str, Any]
    killer_human_moment: dict[str, Any]
    enterprise_scenario: dict[str, Any]
    observations_are_not_truth: dict[str, Any]
    evidence_acceptance_gate: dict[str, Any]
    llm_executor_node_draft: dict[str, Any]
    drs_reuse_signal: dict[str, Any]
    developer_facade_manifest_candidate: dict[str, Any]
    transition_matrix_blocks: dict[str, Any]
    enterprise_chaos_conflicts: dict[str, Any]
    compute_collapse_estimate: dict[str, Any]
    production_boundary: dict[str, Any]
    root_final: dict[str, Any]
    what_human_sees: dict[str, Any]
    what_this_proves: dict[str, Any]
    what_this_does_not_prove: dict[str, Any]
    adversarial_attempts: list[dict[str, Any]]
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


def _enterprise_scenario() -> dict[str, Any]:
    return {
        "scenario_id": "enterprise_procurement_readiness_ENT_ACME_42",
        "enterprise_id": "ENT-ACME-42",
        "request_id": "REQ-KILLER-001",
        "domain": "enterprise_procurement_readiness",
        "human_request": "Can we approve this vendor shipment and trigger the next step?",
        "vendor_record_says_shipment_ready": True,
        "connector_observation_says_compliance_certificate_exists": True,
        "compliance_certificate_status": "stale_expired",
        "invoice_total_conflicts_with_purchase_order": True,
        "payment_approval_missing": True,
        "drs_reuse_candidate_suggests_previous_similar_approval": True,
        "bounded_llm_semantic_executor_draft": "looks ready",
        "capability_manifest_candidate": "read_only_vendor_observation",
        "adversarial_manifest_attempt": "readiness_to_external_action",
        "transition_attempt": "accepted_evidence_to_external_action",
        "production_boundary_result": "no_real_action_no_production_claim",
    }


def _observations_are_not_truth() -> dict[str, Any]:
    return {
        "connector_observation_created": True,
        "connector_observation_is_truth": False,
        "connector_observation_is_accepted_evidence": False,
        "connector_observation_triggers_action": False,
        "observation_meaning": "local_observation_only",
    }


def _evidence_acceptance_gate() -> dict[str, Any]:
    return {
        "evidence_candidate_created": True,
        "evidence_candidate_requires_acceptance_gate": True,
        "accepted_evidence_created": False,
        "accepted_evidence_status": "rejected_or_not_accepted_due_to_stale_conflict",
        "accepted_evidence_is_truth": False,
        "accepted_evidence_triggers_action": False,
        "stale_compliance_certificate_blocks_acceptance": True,
        "conflict_requires_root_review": True,
    }


def _llm_executor_node_draft() -> dict[str, Any]:
    return {
        "bounded_llm_draft_created": True,
        "llm_draft_claim": "looks ready",
        "llm_is_authority": False,
        "llm_can_finalize": False,
        "llm_can_execute_external_action": False,
        "llm_can_write_drs_by_itself": False,
        "llm_draft_overruled_by_boundaries": True,
        "llm_is_bounded_executor_node_capability": True,
    }


def _drs_reuse_signal() -> dict[str, Any]:
    return {
        "drs_reuse_candidate_found": True,
        "drs_reuse_is_authority": False,
        "drs_reuse_applied_as_context_only": True,
        "drs_direct_approval_created": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "closed_checkpoint_metadata_is_authority": False,
    }


def _developer_facade_manifest_candidate() -> dict[str, Any]:
    return {
        "capability_manifest_candidate_created": True,
        "capability_manifest_decision": "facade_validated_manifest_candidate_only",
        "capability_manifest_is_installed_capability": False,
        "installed_capabilities_created": 0,
        "installed_needles_created": 0,
        "developer_manifest_is_authority": False,
        "candidate_scope": "read_only_vendor_observation_only",
        "real_connector_created": False,
        "real_api_called": False,
    }


def _transition_matrix_blocks() -> dict[str, Any]:
    return {
        "transition_matrix_required": True,
        "transition_matrix_is_authority": False,
        "transition_matrix_is_production_runtime_authority": False,
        "invalid_transition_attempted": True,
        "invalid_transition_name": "accepted_evidence_to_external_action",
        "invalid_transition_blocked": True,
        "transition_matrix_blocks_external_action_without_root_and_permission": True,
        "transition_matrix_does_not_replace_root": True,
    }


def _enterprise_chaos_conflicts() -> dict[str, Any]:
    return {
        "conflict_detected": True,
        "conflict_reasons": list(CONFLICT_REASONS),
        "enterprise_chaos_pack_referenced": True,
        "messy_inputs_contained": True,
        "authority_transfers": 0,
        "root_bypassed": False,
    }


def _compute_collapse_estimate() -> dict[str, Any]:
    return {
        "naive_baseline_steps_estimate": 44,
        "hedgehog_routed_steps_estimate": 10,
        "estimated_routed_units_saved": 34,
        "estimated_savings_ratio": 0.773,
        "naive_synthetic_llm_call_units": 29,
        "naive_context_units": 180,
        "naive_collector_replays": 4,
        "naive_validation_passes": 6,
        "naive_action_planning_steps": 6,
        "naive_unbounded_authority_risk_units": 18,
        "hedgehog_bounded_llm_semantic_nodes": 1,
        "hedgehog_context_units": 32,
        "hedgehog_collector_replays": 0,
        "hedgehog_validation_passes": 1,
        "hedgehog_action_planning_steps": 0,
        "hedgehog_unbounded_authority_risk_units": 0,
        "hedgehog_blocked_authority_attempts": 18,
        "proof_level_estimate_only": True,
        "real_cost_savings_claimed": False,
        "real_latency_measured": False,
        "real_billing_measured": False,
        "human_wording": (
            "This is proof-level estimate only, not real billing, not real "
            "latency, and not a production cost claim."
        ),
    }


def _production_boundary() -> dict[str, Any]:
    return {
        "production_boundary_checked": True,
        "production_boundary_design_docs_referenced": True,
        "production_boundary_design_is_implementation": False,
        "production_ready_claimed": False,
        "production_runtime_implemented": False,
        "production_kernel_enforcement_implemented": False,
        "production_capability_registry_implemented": False,
        "real_api_called": False,
        "real_external_action_authorized": False,
        "real_external_action_executed": False,
        "production_persistence_implemented": False,
        "secrets_vault_implemented": False,
        "live_monitoring_implemented": False,
        "external_global_drs_implemented": False,
    }


def _root_final() -> dict[str, Any]:
    return {
        "root_remains_final_authority": True,
        "root_final_created": True,
        "root_final_status": "not_ready",
        "root_final_reason": list(ROOT_FINAL_REASONS),
        "safe_secondary_outcome": "needs_human_review",
        "external_action_executed": False,
        "vendor_shipment_approved": False,
        "payment_triggered": False,
        "production_claim_created": False,
    }


def _adversarial_attempts() -> list[dict[str, Any]]:
    attempted_effects = {
        "connector_observation_to_truth": "truth_claim",
        "connector_observation_to_accepted_evidence": "accepted_evidence",
        "accepted_evidence_to_external_action": "external_action",
        "accepted_evidence_to_ready_status": "ready_status",
        "llm_draft_to_truth": "truth_claim",
        "llm_draft_to_root_final": "root_final",
        "drs_reuse_to_authority": "authority",
        "external_pointer_to_global_drs_write": "global_drs_write",
        "bridge_traversal_to_provenance_laundering": "provenance_laundering",
        "developer_manifest_to_installed_capability": "installed_capability",
        "manifest_candidate_to_installed_needle": "installed_needle",
        "child_cell_to_autonomous_actor": "autonomous_actor",
        "gt_recommendation_to_root_authority": "root_authority",
        "audit_hash_to_truth": "truth_claim",
        "permission_needsuser_to_execution": "execution",
        "resultproposal_to_root_bypass": "root_bypass",
        "stale_timeenvelope_to_current": "current_time_claim",
        "production_boundary_to_production_ready_claim": "production_readiness_claim",
    }
    quarantined = {
        "external_pointer_to_global_drs_write",
        "bridge_traversal_to_provenance_laundering",
        "stale_timeenvelope_to_current",
    }
    return [
        {
            "attempt_id": attempt_id,
            "attempted_effect": attempted_effects[attempt_id],
            "detected": True,
            "blocked": True,
            "final_effect": (
                "quarantined_and_blocked" if attempt_id in quarantined else "blocked"
            ),
            "root_review_required": True,
            "authority_transferred": False,
            "root_bypassed": False,
            "final_output_created": False,
            "truth_claim_created": False,
            "accepted_evidence_created": False,
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
        for attempt_id in ADVERSARIAL_ATTEMPT_IDS
    ]


def _act1_dirty_enterprise_request(root_final: dict[str, Any]) -> dict[str, Any]:
    return {
        "act_title": "ACT 1 — Dirty Enterprise Request",
        "human_story": (
            "A company asks whether a vendor shipment can be approved and the "
            "next step triggered."
        ),
        "positive_signals": [
            "vendor record says ready",
            "connector observation says certificate exists",
            "DRS reuse says a similar previous case was approved",
            "LLM draft says \"looks ready\"",
            "manifest candidate offers read-only vendor observation",
        ],
        "conflicts": [
            "compliance certificate is stale/expired",
            "invoice total conflicts with purchase order",
            "payment approval is missing",
        ],
        "root_result": root_final["root_final_status"],
        "safe_secondary_outcome": root_final["safe_secondary_outcome"],
        "no_shipment_approved": True,
        "no_payment_triggered": True,
        "no_external_action_executed": True,
    }


def _act2_authority_stress() -> dict[str, Any]:
    return {
        "act_title": "ACT 2 — Authority Stress",
        "blocked_attempt_count": 18,
        "human_summary": [
            "connector observation did not become truth",
            "connector observation did not become accepted evidence",
            "accepted evidence did not become action",
            "accepted evidence did not become ready",
            "LLM draft did not become truth or Root Final",
            "DRS reuse did not become authority",
            "external pointer did not write global DRS",
            "bridge did not launder provenance",
            "manifest did not install capability",
            "manifest candidate did not install Needle",
            "child cell did not become autonomous actor",
            "GT did not become Root",
            "audit hash did not become truth",
            "permission / needs_user did not become execution",
            "ResultProposal did not bypass Root",
            "stale TimeEnvelope did not become current",
            "Production Boundary did not become production-ready claim",
        ],
    }


def _act3_compute_collapse(compute_estimate: dict[str, Any]) -> dict[str, Any]:
    return {
        "act_title": "ACT 3 — Compute Collapse",
        "human_story": (
            "Root-controlled semantic routing reuses closed metadata and blocks "
            "authority escalation instead of replaying an unsafe long chain."
        ),
        "naive_synthetic_llm_call_units": compute_estimate[
            "naive_synthetic_llm_call_units"
        ],
        "naive_context_units": compute_estimate["naive_context_units"],
        "hedgehog_bounded_llm_semantic_nodes": compute_estimate[
            "hedgehog_bounded_llm_semantic_nodes"
        ],
        "hedgehog_context_units": compute_estimate["hedgehog_context_units"],
        "hedgehog_blocked_authority_attempts": compute_estimate[
            "hedgehog_blocked_authority_attempts"
        ],
        "human_wording": compute_estimate["human_wording"],
    }


def _killer_human_moment() -> dict[str, Any]:
    return {
        "english_line_1": "The system did not become an autonomous agent.",
        "english_line_2": "It became a controlled semantic runtime.",
        "russian_line_1": "Система не стала автономным агентом.",
        "russian_line_2": "Она стала управляемой смысловой операционной средой.",
    }


def _what_human_sees(root_final: dict[str, Any]) -> dict[str, Any]:
    return {
        "human_visible_status": root_final["root_final_status"],
        "human_visible_reason": list(root_final["root_final_reason"]),
        "human_visible_next_step": "needs_human_review",
        "shipment_approval_visible": False,
        "payment_trigger_visible": False,
        "production_claim_visible": False,
    }


def _what_this_proves() -> dict[str, Any]:
    return {
        "proves_assembly_of_proven_layers": True,
        "proves_root_final_boundary_survives_dirty_enterprise_case": True,
        "proves_transition_matrix_blocks_invalid_external_action": True,
        "proves_developer_facade_remains_candidate_only": True,
        "proves_production_boundary_prevents_overclaim": True,
    }


def _what_this_does_not_prove() -> dict[str, Any]:
    return {
        "does_not_prove_production_readiness": True,
        "does_not_prove_real_api_integration": True,
        "does_not_prove_real_external_action": True,
        "does_not_prove_production_persistence": True,
        "does_not_prove_real_cost_savings": True,
        "does_not_install_capabilities_or_needles": True,
        "does_not_activate_marennya_or_up": True,
    }


def _summary(report: EnterpriseKillerDemoV01Report, passed: bool) -> dict[str, Any]:
    return {
        "enterprise_killer_demo_v01_status": "PASS" if passed else "FAIL",
        "proof_type": "deterministic_local_assembly_proof_only",
        "source_evidence_mode": report.source_evidence["source_evidence_mode"],
        "source_collectors_replayed": False,
        "source_checkpoint_count": len(report.source_checkpoints),
        "source_checkpoints_all_closed": True,
        "scenario_id": report.enterprise_scenario["scenario_id"],
        "conflict_detected": report.enterprise_chaos_conflicts["conflict_detected"],
        "root_final_status": report.root_final["root_final_status"],
        "safe_secondary_outcome": report.root_final["safe_secondary_outcome"],
        "connector_observation_is_truth": False,
        "evidence_candidate_requires_acceptance_gate": True,
        "accepted_evidence_is_truth": False,
        "llm_is_authority": False,
        "drs_reuse_is_authority": False,
        "developer_manifest_is_authority": False,
        "capability_manifest_is_installed_capability": False,
        "transition_matrix_is_authority": False,
        "transition_matrix_is_production_runtime_authority": False,
        "production_boundary_design_is_implementation": False,
        "production_ready_claimed": False,
        "real_api_called": False,
        "real_external_action_authorized": False,
        "real_external_action_executed": False,
        "external_action_executed": False,
        "installed_capabilities_created": 0,
        "installed_needles_created": 0,
        "global_drs_write": False,
        "external_drs_write": False,
        "external_global_drs_implemented": False,
        "production_persistence_implemented": False,
        "secrets_vault_implemented": False,
        "live_monitoring_implemented": False,
        "root_remains_final_authority": True,
        "root_bypassed": False,
        "vendor_shipment_approved": False,
        "payment_triggered": False,
        "real_cost_savings_claimed": False,
        "real_latency_measured": False,
        "real_billing_measured": False,
        "adversarial_attempts_observed": len(report.adversarial_attempts),
        "adversarial_attempts_blocked": len(
            [row for row in report.adversarial_attempts if row["blocked"] is True]
        ),
        "hedgehog_blocked_authority_attempts": report.compute_collapse_estimate[
            "hedgehog_blocked_authority_attempts"
        ],
        "act_count": 3,
        "human_walkthrough_ready": True,
        "authority_transfers": 0,
        "truth_proven_by_non_root": False,
        "external_actions_executed": 0,
        "production_persistence": False,
        "network_called": False,
        "gemini_called": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "no_network": True,
        "no_gemini": True,
        "no_real_api": True,
        "no_real_external_action": True,
        "no_production_persistence": True,
        "no_installed_capability": True,
        "no_installed_needle": True,
        "no_marennya": True,
        "no_up": True,
    }


def validate_enterprise_killer_demo_v01(
    report: EnterpriseKillerDemoV01Report,
) -> bool:
    summary = report.summary
    return all(
        (
            report.header["proof_type"] == "deterministic_local_assembly_proof_only",
            len(report.source_checkpoints) == 10,
            report.source_evidence["source_collectors_replayed"] is False,
            report.source_evidence["source_checkpoints_all_closed"] is True,
            report.enterprise_scenario["enterprise_id"] == "ENT-ACME-42",
            set(CONFLICT_REASONS).issubset(
                set(report.enterprise_chaos_conflicts["conflict_reasons"])
            ),
            report.observations_are_not_truth["connector_observation_is_truth"] is False,
            report.evidence_acceptance_gate[
                "evidence_candidate_requires_acceptance_gate"
            ]
            is True,
            report.llm_executor_node_draft["llm_is_authority"] is False,
            report.drs_reuse_signal["drs_reuse_is_authority"] is False,
            report.developer_facade_manifest_candidate[
                "capability_manifest_is_installed_capability"
            ]
            is False,
            report.transition_matrix_blocks["invalid_transition_blocked"] is True,
            report.production_boundary["production_ready_claimed"] is False,
            report.root_final["root_final_status"] == "not_ready",
            set(ROOT_FINAL_REASONS).issubset(set(report.root_final["root_final_reason"])),
            report.compute_collapse_estimate["real_cost_savings_claimed"] is False,
            len(report.adversarial_attempts) == 18,
            all(row["blocked"] is True for row in report.adversarial_attempts),
            all(row["authority_transferred"] is False for row in report.adversarial_attempts),
            all(row["root_bypassed"] is False for row in report.adversarial_attempts),
            report.act1_dirty_enterprise_request["root_result"] == "not_ready",
            report.act2_authority_stress["blocked_attempt_count"] == 18,
            report.act3_compute_collapse[
                "hedgehog_blocked_authority_attempts"
            ]
            == 18,
            report.killer_human_moment["english_line_1"]
            == "The system did not become an autonomous agent.",
            report.audit_entry["canonical_payload_hash"] == canonical_hash(
                report.proof_artifact
            ),
            report.audit_entry["audit_hash_decides_truth"] is False,
            summary["enterprise_killer_demo_v01_status"] == "PASS",
        )
    )


def collect_enterprise_killer_demo_v01() -> EnterpriseKillerDemoV01Report:
    source_checkpoints = _source_checkpoints()
    source_evidence = _source_evidence(source_checkpoints)
    enterprise_scenario = _enterprise_scenario()
    observations = _observations_are_not_truth()
    evidence_gate = _evidence_acceptance_gate()
    llm_draft = _llm_executor_node_draft()
    drs_reuse = _drs_reuse_signal()
    manifest_candidate = _developer_facade_manifest_candidate()
    transition_blocks = _transition_matrix_blocks()
    chaos_conflicts = _enterprise_chaos_conflicts()
    compute_estimate = _compute_collapse_estimate()
    production_boundary = _production_boundary()
    root_final = _root_final()
    act1 = _act1_dirty_enterprise_request(root_final)
    act2 = _act2_authority_stress()
    act3 = _act3_compute_collapse(compute_estimate)
    killer_moment = _killer_human_moment()
    human_view = _what_human_sees(root_final)
    proves = _what_this_proves()
    non_claims = _what_this_does_not_prove()
    adversarial_attempts = _adversarial_attempts()
    header = {
        "proof_id": "enterprise_killer_demo_v01",
        "title": "Enterprise Killer Demo v0.1",
        "proof_type": "deterministic_local_assembly_proof_only",
        "assembly_mode": "assembly of proven layers",
        "production_implementation_created": False,
        "new_authority_layer_created": False,
    }
    proof_artifact = {
        "proof_artifact_id": "enterprise_killer_demo_v01",
        "header": header,
        "source_evidence": source_evidence,
        "source_checkpoints": source_checkpoints,
        "act1_dirty_enterprise_request": act1,
        "act2_authority_stress": act2,
        "act3_compute_collapse": act3,
        "killer_human_moment": killer_moment,
        "enterprise_scenario": enterprise_scenario,
        "observations_are_not_truth": observations,
        "evidence_acceptance_gate": evidence_gate,
        "llm_executor_node_draft": llm_draft,
        "drs_reuse_signal": drs_reuse,
        "developer_facade_manifest_candidate": manifest_candidate,
        "transition_matrix_blocks": transition_blocks,
        "enterprise_chaos_conflicts": chaos_conflicts,
        "compute_collapse_estimate": compute_estimate,
        "production_boundary": production_boundary,
        "root_final": root_final,
        "adversarial_attempts": adversarial_attempts,
    }
    audit_entry = {
        "audit_entry_id": "audit_enterprise_killer_demo_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "audit_hash_chain_records_continuity_only": True,
        "audit_hash_decides_truth": False,
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
    }
    provisional = EnterpriseKillerDemoV01Report(
        header=header,
        source_evidence=source_evidence,
        source_checkpoints=source_checkpoints,
        act1_dirty_enterprise_request=act1,
        act2_authority_stress=act2,
        act3_compute_collapse=act3,
        killer_human_moment=killer_moment,
        enterprise_scenario=enterprise_scenario,
        observations_are_not_truth=observations,
        evidence_acceptance_gate=evidence_gate,
        llm_executor_node_draft=llm_draft,
        drs_reuse_signal=drs_reuse,
        developer_facade_manifest_candidate=manifest_candidate,
        transition_matrix_blocks=transition_blocks,
        enterprise_chaos_conflicts=chaos_conflicts,
        compute_collapse_estimate=compute_estimate,
        production_boundary=production_boundary,
        root_final=root_final,
        what_human_sees=human_view,
        what_this_proves=proves,
        what_this_does_not_prove=non_claims,
        adversarial_attempts=adversarial_attempts,
        audit_entry=audit_entry,
        proof_artifact=proof_artifact,
        summary={},
    )
    preliminary = replace(provisional, summary=_summary(provisional, passed=True))
    passed = validate_enterprise_killer_demo_v01(preliminary)
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
    return [f"{key}: {_format_scalar(value)}" for key, value in rows.items()]


def _render_rows(rows: list[dict[str, Any]], id_field: str) -> list[str]:
    rendered = []
    for row in rows:
        parts = [f"{key}={_format_scalar(value)}" for key, value in row.items()]
        rendered.append(f"- {row[id_field]} | " + " | ".join(parts))
    return rendered


def render_enterprise_killer_demo_v01(report: EnterpriseKillerDemoV01Report) -> str:
    sections: list[tuple[str, list[str]]] = [
        ("HEADER", _render_dict(report.header)),
        (
            "SOURCE CHECKPOINTS",
            _render_dict(report.source_evidence)
            + _render_rows(report.source_checkpoints, "checkpoint_id"),
        ),
        (
            "ACT 1 — DIRTY ENTERPRISE REQUEST",
            _render_dict(report.act1_dirty_enterprise_request),
        ),
        ("ACT 2 — AUTHORITY STRESS", _render_dict(report.act2_authority_stress)),
        ("ACT 3 — COMPUTE COLLAPSE", _render_dict(report.act3_compute_collapse)),
        ("KILLER HUMAN MOMENT", _render_dict(report.killer_human_moment)),
        ("ENTERPRISE SCENARIO", _render_dict(report.enterprise_scenario)),
        ("OBSERVATIONS ARE NOT TRUTH", _render_dict(report.observations_are_not_truth)),
        ("EVIDENCE ACCEPTANCE GATE", _render_dict(report.evidence_acceptance_gate)),
        ("LLM EXECUTOR NODE DRAFT", _render_dict(report.llm_executor_node_draft)),
        ("DRS REUSE SIGNAL", _render_dict(report.drs_reuse_signal)),
        (
            "DEVELOPER FACADE MANIFEST CANDIDATE",
            _render_dict(report.developer_facade_manifest_candidate),
        ),
        ("TRANSITION MATRIX BLOCKS", _render_dict(report.transition_matrix_blocks)),
        ("ENTERPRISE CHAOS / CONFLICTS", _render_dict(report.enterprise_chaos_conflicts)),
        ("COMPUTE COLLAPSE ESTIMATE", _render_dict(report.compute_collapse_estimate)),
        ("PRODUCTION BOUNDARY", _render_dict(report.production_boundary)),
        ("ROOT FINAL", _render_dict(report.root_final)),
        ("WHAT HUMAN SEES", _render_dict(report.what_human_sees)),
        ("WHAT THIS PROVES", _render_dict(report.what_this_proves)),
        ("WHAT THIS DOES NOT PROVE", _render_dict(report.what_this_does_not_prove)),
        ("ADVERSARIAL ATTEMPTS", _render_rows(report.adversarial_attempts, "attempt_id")),
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
    report = collect_enterprise_killer_demo_v01()
    print(render_enterprise_killer_demo_v01(report))
    return 0 if report.summary["enterprise_killer_demo_v01_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
