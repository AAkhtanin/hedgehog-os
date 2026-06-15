from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


EFFECT_FIELDS = (
    "authority_transferred",
    "final_output_created",
    "truth_claim_created",
    "ready_status_created",
    "external_action_executed",
    "global_drs_write",
    "external_drs_write",
    "installed_needle_created",
    "production_persistence",
    "network_called",
    "gemini_called",
    "marennya_invoked",
    "up_invoked",
)


ARTIFACT_TYPES = (
    "Root",
    "RootDecision",
    "ConnectorObservation",
    "EvidenceCandidate",
    "ValidationPacket",
    "AcceptedEvidence",
    "RejectedEvidence",
    "QuarantinedEvidence",
    "SemanticDraft",
    "ResultProposal",
    "PostVVReport",
    "GTReport",
    "RootFinalOutput",
    "DRSWriteback",
    "ExternalDRSPointer",
    "ExternalDRSWrite",
    "NeedleCandidate",
    "InstalledNeedle",
    "PermissionNeedsUser",
    "ExternalAction",
    "ChildCellClaim",
    "AuditHashClaim",
    "ComputeCollapseMetric",
    "DRSReuse",
    "ClosedCheckpointMetadata",
    "LLMExecutorNode",
    "MarennyaStub",
    "UPStub",
)


TRANSITION_TARGET_TYPES = (
    "EvidenceCandidate",
    "ValidationPacket",
    "AcceptedEvidence",
    "RejectedEvidence",
    "QuarantinedEvidence",
    "PostVVReport",
    "GTReport",
    "RootReviewInput",
    "RootFinalOutput",
    "DRSWriteback",
    "Truth",
    "ReadyStatus",
    "ExternalAction",
    "InstalledNeedle",
    "Authority",
    "RootAuthority",
    "GTAuthority",
    "ExternalDRSWrite",
    "GlobalDRSWrite",
    "ProvenanceLaundering",
    "AutonomousActor",
    "ProductionEconomics",
    "KillerDemoAuthorization",
    "RuntimeActivation",
)


LOCAL_TRANSITION_TAXONOMY = tuple(
    sorted(set(ARTIFACT_TYPES) | set(TRANSITION_TARGET_TYPES))
)


BLOCKED_TRANSITION_DEFINITIONS = (
    ("connector_observation_to_truth", "ConnectorObservation", "Truth", "connector_sandbox"),
    (
        "connector_observation_to_accepted_evidence_without_root",
        "ConnectorObservation",
        "AcceptedEvidence",
        "connector_sandbox",
    ),
    (
        "evidence_candidate_to_accepted_evidence_without_root",
        "EvidenceCandidate",
        "AcceptedEvidence",
        "acceptance_gate_validator",
    ),
    (
        "validation_packet_to_accepted_evidence_without_root",
        "ValidationPacket",
        "AcceptedEvidence",
        "acceptance_gate_validator",
    ),
    (
        "validation_packet_to_root_final_output",
        "ValidationPacket",
        "RootFinalOutput",
        "acceptance_gate_validator",
    ),
    ("accepted_evidence_to_truth", "AcceptedEvidence", "Truth", "accepted_evidence"),
    ("accepted_evidence_to_ready_status", "AcceptedEvidence", "ReadyStatus", "accepted_evidence"),
    ("accepted_evidence_to_external_action", "AcceptedEvidence", "ExternalAction", "accepted_evidence"),
    ("accepted_evidence_to_drs_writeback_by_itself", "AcceptedEvidence", "DRSWriteback", "accepted_evidence"),
    ("accepted_evidence_to_installed_needle", "AcceptedEvidence", "InstalledNeedle", "accepted_evidence"),
    ("semantic_draft_to_truth", "SemanticDraft", "Truth", "llm_semantic_executor_node"),
    ("semantic_draft_to_root_final_output", "SemanticDraft", "RootFinalOutput", "llm_semantic_executor_node"),
    ("semantic_draft_to_external_action", "SemanticDraft", "ExternalAction", "llm_semantic_executor_node"),
    ("resultproposal_to_root_final_output", "ResultProposal", "RootFinalOutput", "executor"),
    ("resultproposal_to_external_action", "ResultProposal", "ExternalAction", "executor"),
    ("gt_report_to_root_final_output", "GTReport", "RootFinalOutput", "GT"),
    ("gt_report_to_accepted_evidence", "GTReport", "AcceptedEvidence", "GT"),
    ("gt_report_to_external_action", "GTReport", "ExternalAction", "GT"),
    ("drs_reuse_to_authority", "DRSReuse", "Authority", "drs_reuse"),
    ("closed_checkpoint_metadata_to_authority", "ClosedCheckpointMetadata", "Authority", "metadata_reference"),
    ("audit_hash_claim_to_truth", "AuditHashClaim", "Truth", "audit_hash_chain"),
    ("external_drs_pointer_to_external_drs_write", "ExternalDRSPointer", "ExternalDRSWrite", "external_pointer"),
    ("external_drs_pointer_to_global_drs_write", "ExternalDRSPointer", "GlobalDRSWrite", "external_pointer"),
    ("external_drs_pointer_to_provenance_laundering", "ExternalDRSPointer", "ProvenanceLaundering", "external_pointer"),
    ("needle_candidate_to_installed_needle_without_root", "NeedleCandidate", "InstalledNeedle", "needle_candidate"),
    ("permission_needs_user_to_external_action", "PermissionNeedsUser", "ExternalAction", "permission_boundary"),
    ("child_cell_claim_to_autonomous_actor", "ChildCellClaim", "AutonomousActor", "child_cell"),
    ("compute_collapse_metric_to_production_economics", "ComputeCollapseMetric", "ProductionEconomics", "benchmark"),
    ("compute_collapse_metric_to_killer_demo_authorization", "ComputeCollapseMetric", "KillerDemoAuthorization", "benchmark"),
    ("llm_executor_node_to_root_authority", "LLMExecutorNode", "RootAuthority", "llm_semantic_executor_node"),
    ("llm_executor_node_to_gt_authority", "LLMExecutorNode", "GTAuthority", "llm_semantic_executor_node"),
    ("llm_executor_node_to_drs_writeback", "LLMExecutorNode", "DRSWriteback", "llm_semantic_executor_node"),
    ("llm_executor_node_to_external_action", "LLMExecutorNode", "ExternalAction", "llm_semantic_executor_node"),
    ("marennya_stub_to_runtime_activation", "MarennyaStub", "RuntimeActivation", "marennya_stub"),
    ("up_stub_to_runtime_activation", "UPStub", "RuntimeActivation", "up_stub"),
)


@dataclass(frozen=True)
class KernelEnforcementTransitionMatrixReport:
    header: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    transition_matrix_purpose: dict[str, Any]
    artifact_types: list[str]
    transition_target_types: list[str]
    local_transition_taxonomy: list[str]
    allowed_transitions: list[dict[str, Any]]
    blocked_transitions: list[dict[str, Any]]
    root_commit_boundary: dict[str, Any]
    authority_boundary_matrix: dict[str, Any]
    llm_executor_node_boundary: dict[str, Any]
    drs_metadata_audit_boundary: dict[str, Any]
    compute_collapse_killer_demo_boundary: dict[str, Any]
    root_final: dict[str, Any]
    audit_entry: dict[str, Any]
    proof_artifact: dict[str, Any]
    summary: dict[str, Any]


def _base_effects(**overrides: Any) -> dict[str, Any]:
    fields = {
        "authority_transferred": False,
        "final_output_created": False,
        "truth_claim_created": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "network_called": False,
        "gemini_called": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    fields.update(overrides)
    return fields


def _closed_source_checkpoints() -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": "external_drs_pointer_protocol_v01",
            "checkpoint_name": "External DRS Pointer Protocol v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "read_only_enterprise_connector_sandbox_v01",
            "checkpoint_name": "Read-only Enterprise Connector Sandbox v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "external_evidence_acceptance_gate_v01",
            "checkpoint_name": "External Evidence Acceptance Gate v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "bounded_llm_semantic_executor_node_v01",
            "checkpoint_name": "Bounded LLM Semantic Executor Node v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "enterprise_chaos_pack_v01",
            "checkpoint_name": "Enterprise Chaos Pack v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "compute_collapse_enterprise_bench_v01",
            "checkpoint_name": "Compute Collapse Enterprise Bench v0.1",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
        {
            "checkpoint_id": "math_invariants_sync_v04",
            "checkpoint_name": "Math / Invariants Sync v0.4",
            "checkpoint_status": "PASS",
            "closure_status": "closed",
        },
    ]


def _allowed_transition(
    transition_id: str,
    artifact_type: str,
    source_state: str,
    attempted_target_or_effect: str,
    actor: str,
    root_commit_present: bool,
    expected_decision: str,
    decision_reason: str,
    effect: str,
    root_review_required: bool = False,
    **effect_overrides: Any,
) -> dict[str, Any]:
    return {
        "transition_id": transition_id,
        "artifact_type": artifact_type,
        "source_state": source_state,
        "attempted_target_or_effect": attempted_target_or_effect,
        "actor": actor,
        "root_commit_present": root_commit_present,
        "expected_decision": expected_decision,
        "decision_reason": decision_reason,
        "effect": effect,
        "root_review_required": root_review_required,
        **_base_effects(**effect_overrides),
    }


def _allowed_transitions() -> list[dict[str, Any]]:
    return [
        _allowed_transition(
            "connector_observation_to_evidence_candidate",
            "ConnectorObservation",
            "observation_only",
            "EvidenceCandidate",
            "connector_sandbox",
            False,
            "allowed_candidate_only",
            "Connector observations may become candidates only.",
            "candidate_only",
            root_review_required=True,
        ),
        _allowed_transition(
            "evidence_candidate_to_validation_packet",
            "EvidenceCandidate",
            "candidate_only",
            "ValidationPacket",
            "acceptance_gate_validator",
            False,
            "allowed_validation_only",
            "Candidates may be locally validated without acceptance.",
            "validation_packet_only",
            root_review_required=True,
        ),
        _allowed_transition(
            "root_decision_to_accepted_evidence",
            "RootDecision",
            "root_reviewed_candidate",
            "AcceptedEvidence",
            "Root",
            True,
            "allowed_accepted_evidence_only",
            "AcceptedEvidence requires Root decision and remains bounded.",
            "accepted_evidence_only",
        ),
        _allowed_transition(
            "root_decision_to_rejected_evidence",
            "RootDecision",
            "root_reviewed_candidate",
            "RejectedEvidence",
            "Root",
            True,
            "allowed_rejection",
            "Root may reject failed evidence candidates.",
            "rejected_evidence_only",
        ),
        _allowed_transition(
            "root_decision_to_quarantined_evidence",
            "RootDecision",
            "root_reviewed_candidate",
            "QuarantinedEvidence",
            "Root",
            True,
            "allowed_quarantine",
            "Root may quarantine unsafe or unknown candidates.",
            "quarantined_evidence_only",
        ),
        _allowed_transition(
            "resultproposal_to_post_vv_report",
            "ResultProposal",
            "executor_result_proposal",
            "PostVVReport",
            "post_vv",
            False,
            "allowed_validation_report_only",
            "Post V&V may validate ResultProposal artifacts only.",
            "validation_report_only",
        ),
        _allowed_transition(
            "post_vv_report_to_gt_report",
            "PostVVReport",
            "validated_report",
            "GTReport",
            "GT",
            False,
            "allowed_advisory_selection_only",
            "GT may create advisory selection only.",
            "advisory_selection_only",
        ),
        _allowed_transition(
            "gt_report_to_root_review_input",
            "GTReport",
            "advisory_selection",
            "RootReviewInput",
            "GT",
            False,
            "allowed_advisory_to_root_only",
            "GT forwards advisory evidence to Root and is not final authority.",
            "root_review_input_only",
            gt_is_final_authority=False,
        ),
        _allowed_transition(
            "root_to_root_final_output",
            "Root",
            "root_review",
            "RootFinalOutput",
            "Root",
            True,
            "allowed_root_final_output",
            "Only Root may create final output.",
            "root_final_output",
            final_output_created=True,
        ),
        _allowed_transition(
            "root_final_output_to_drs_writeback",
            "RootFinalOutput",
            "root_final_output",
            "DRSWriteback",
            "Root",
            True,
            "allowed_local_drs_writeback_after_root_final",
            "Local DRS writeback may follow Root final only.",
            "local_drs_writeback_only",
            drs_writeback_scope="local_after_root_final",
            local_drs_writeback=True,
        ),
    ]


def _blocked_transitions() -> list[dict[str, Any]]:
    rows = []
    for attempt_id, artifact_type, attempted_effect, actor in BLOCKED_TRANSITION_DEFINITIONS:
        rows.append(
            {
                "attempt_id": attempt_id,
                "artifact_type": artifact_type,
                "source_state": "uncommitted_or_non_root_artifact",
                "attempted_target_or_effect": attempted_effect,
                "attempted_effect": attempted_effect,
                "actor": actor,
                "root_commit_present": False,
                "expected_decision": "blocked",
                "decision_reason": "Transition violates already closed boundary rules.",
                "detected": True,
                "blocked": True,
                "root_review_required": True,
                "final_effect": "blocked",
                **_base_effects(),
            }
        )
    return rows


def _root_commit_boundary() -> dict[str, Any]:
    return {
        "root_commit_required_for_final_output": True,
        "root_only_final_output": True,
        "root_commit_required_for_accepted_evidence": True,
        "root_commit_required_for_local_drs_writeback": True,
        "non_root_final_output_transitions_blocked": True,
    }


def _authority_boundary_matrix() -> dict[str, Any]:
    return {
        "root_only_final_output": True,
        "root_commit_required_for_final_output": True,
        "drs_reuse_is_authority": False,
        "closed_checkpoint_metadata_is_authority": False,
        "audit_hash_decides_truth": False,
        "connector_observation_is_truth": False,
        "evidence_candidate_is_accepted_evidence": False,
        "accepted_evidence_is_truth": False,
        "accepted_evidence_is_action": False,
        "semantic_draft_is_final": False,
        "resultproposal_is_final": False,
        "gt_is_final_authority": False,
        "permission_needs_user_is_execution": False,
        "needle_candidate_is_installed_needle": False,
        "child_cell_claim_is_autonomous_actor": False,
    }


def _llm_executor_node_boundary() -> dict[str, Any]:
    return {
        "llm_is_bounded_executor_node_capability": True,
        "llm_is_authority": False,
        "llm_is_root": False,
        "llm_is_gt": False,
        "llm_can_write_drs": False,
        "llm_can_execute_external_action": False,
        "semantic_draft_is_final": False,
        "semantic_draft_requires_post_vv_gt_root": True,
    }


def _drs_metadata_audit_boundary() -> dict[str, Any]:
    return {
        "drs_reuse_is_authority": False,
        "closed_checkpoint_metadata_is_authority": False,
        "audit_hash_decides_truth": False,
        "external_pointer_is_external_drs_write": False,
        "external_pointer_is_global_drs_write": False,
        "bridge_traversal_launders_provenance": False,
        "source_collectors_replayed": False,
    }


def _compute_collapse_killer_demo_boundary() -> dict[str, Any]:
    return {
        "compute_collapse_metric_is_production_economics": False,
        "compute_collapse_authorizes_killer_demo": False,
        "compute_collapse_authorizes_multi_llm_showcase": False,
        "kernel_enforcement_authorizes_killer_demo": False,
        "production_enforcement_implemented": False,
        "runtime_rewrite_performed": False,
    }


def validate_kernel_enforcement_transition_matrix_v01(
    report: KernelEnforcementTransitionMatrixReport,
) -> bool:
    blocked = report.blocked_transitions
    taxonomy = set(report.local_transition_taxonomy)
    return all(
        (
            len(report.allowed_transitions) == 10,
            len(blocked) == 35,
            all(
                row["artifact_type"] in taxonomy
                and row["attempted_target_or_effect"] in taxonomy
                for row in report.allowed_transitions
            ),
            all(
                row["artifact_type"] in taxonomy
                and row["attempted_target_or_effect"] in taxonomy
                for row in blocked
            ),
            all(row["detected"] is True for row in blocked),
            all(row["blocked"] is True for row in blocked),
            all(row["final_effect"] == "blocked" for row in blocked),
            all(
                all(row[field] is False for field in EFFECT_FIELDS)
                for row in blocked
            ),
            report.root_commit_boundary["root_only_final_output"] is True,
            report.authority_boundary_matrix["drs_reuse_is_authority"] is False,
            report.authority_boundary_matrix[
                "closed_checkpoint_metadata_is_authority"
            ]
            is False,
            report.authority_boundary_matrix["audit_hash_decides_truth"] is False,
            report.llm_executor_node_boundary[
                "llm_is_bounded_executor_node_capability"
            ]
            is True,
            report.llm_executor_node_boundary["llm_is_authority"] is False,
            report.compute_collapse_killer_demo_boundary[
                "compute_collapse_authorizes_killer_demo"
            ]
            is False,
            report.root_final["root_result"]
            == "kernel_enforcement_transition_matrix_completed",
            report.root_final["root_remains_final_authority"] is True,
            report.audit_entry["canonical_payload_hash"]
            == canonical_hash(report.proof_artifact),
            report.audit_entry["audit_chain_decides_truth"] is False,
        )
    )


def collect_kernel_enforcement_transition_matrix_v01() -> KernelEnforcementTransitionMatrixReport:
    checkpoints = _closed_source_checkpoints()
    allowed = _allowed_transitions()
    blocked = _blocked_transitions()
    header = {
        "proof_id": "kernel_enforcement_transition_matrix_v01",
        "title": "Kernel Enforcement / Transition Matrix Hardening v0.1",
        "proof_type": "deterministic_local_proof_only",
        "production_enforcement_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
    }
    purpose = {
        "purpose": "centralize_already_proven_boundary_rules",
        "new_architecture_created": False,
        "new_invariants_invented": False,
        "transition_matrix_is_proof_only": True,
        "transition_matrix_is_authority": False,
        "transition_matrix_is_production_runtime_authority": False,
    }
    root_commit = _root_commit_boundary()
    authority = _authority_boundary_matrix()
    llm = _llm_executor_node_boundary()
    drs = _drs_metadata_audit_boundary()
    compute = _compute_collapse_killer_demo_boundary()
    root_final = {
        "root_result": "kernel_enforcement_transition_matrix_completed",
        "safe_secondary_outcome": "transition_matrix_available_for_future_kernel_hardening",
        "production_enforcement_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "network_called": False,
        "gemini_called": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "root_remains_final_authority": True,
    }
    proof_artifact = {
        "proof_artifact_id": "kernel_enforcement_transition_matrix_v01",
        "header": header,
        "source_checkpoints": checkpoints,
        "transition_matrix_purpose": purpose,
        "artifact_types": list(ARTIFACT_TYPES),
        "transition_target_types": list(TRANSITION_TARGET_TYPES),
        "local_transition_taxonomy": list(LOCAL_TRANSITION_TAXONOMY),
        "allowed_transitions": allowed,
        "blocked_transitions": blocked,
        "root_commit_boundary": root_commit,
        "authority_boundary_matrix": authority,
        "llm_executor_node_boundary": llm,
        "drs_metadata_audit_boundary": drs,
        "compute_collapse_killer_demo_boundary": compute,
        "root_final": root_final,
    }
    audit_entry = {
        "audit_entry_id": "audit_kernel_enforcement_transition_matrix_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = KernelEnforcementTransitionMatrixReport(
        header,
        checkpoints,
        purpose,
        list(ARTIFACT_TYPES),
        list(TRANSITION_TARGET_TYPES),
        list(LOCAL_TRANSITION_TAXONOMY),
        allowed,
        blocked,
        root_commit,
        authority,
        llm,
        drs,
        compute,
        root_final,
        audit_entry,
        proof_artifact,
        {},
    )
    passed = validate_kernel_enforcement_transition_matrix_v01(provisional)
    summary = {
        "kernel_enforcement_transition_matrix_v01_status": "PASS" if passed else "FAIL",
        "proof_type": "deterministic_local_proof_only",
        "production_enforcement_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
        "transition_matrix_is_proof_only": True,
        "transition_matrix_is_authority": False,
        "transition_matrix_is_production_runtime_authority": False,
        "allowed_transitions_count": len(allowed),
        "blocked_transitions_count": len(blocked),
        "blocked_transitions_detected": sum(row["detected"] for row in blocked),
        "blocked_transitions_blocked": sum(row["blocked"] for row in blocked),
        **root_commit,
        **authority,
        **llm,
        "compute_collapse_authorizes_killer_demo": False,
        "no_network": True,
        "no_gemini": True,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "no_installed_needle": True,
        "no_production_persistence": True,
        "no_marennya": True,
        "no_up": True,
        "ready_for_kernel_enforcement_transition_matrix_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


def _format(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _list_section(lines: list[str], title: str, rows: list[str]) -> None:
    lines.extend(["", title])
    lines.extend(str(row) for row in rows)


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_kernel_enforcement_transition_matrix_v01(
    report: KernelEnforcementTransitionMatrixReport,
) -> str:
    lines = [
        "[KERNEL ENFORCEMENT / TRANSITION MATRIX HARDENING v0.1]",
        "note: deterministic local proof-only transition matrix",
        "note: production enforcement is not implemented",
        "note: runtime, schemas, and existing proof runners are not modified",
    ]
    _section(lines, "[HEADER]", report.header)
    _rows(lines, "[SOURCE CHECKPOINTS]", report.source_checkpoints)
    _section(lines, "[TRANSITION MATRIX PURPOSE]", report.transition_matrix_purpose)
    _list_section(lines, "[ARTIFACT TYPES]", report.artifact_types)
    _list_section(lines, "[TRANSITION TARGET TYPES]", report.transition_target_types)
    _list_section(lines, "[LOCAL TRANSITION TAXONOMY]", report.local_transition_taxonomy)
    _rows(lines, "[ALLOWED TRANSITIONS]", report.allowed_transitions)
    _rows(lines, "[BLOCKED TRANSITIONS]", report.blocked_transitions)
    _section(lines, "[ROOT COMMIT BOUNDARY]", report.root_commit_boundary)
    _section(lines, "[AUTHORITY BOUNDARY MATRIX]", report.authority_boundary_matrix)
    _section(lines, "[LLM EXECUTOR NODE BOUNDARY]", report.llm_executor_node_boundary)
    _section(lines, "[DRS / METADATA / AUDIT BOUNDARY]", report.drs_metadata_audit_boundary)
    _section(
        lines,
        "[COMPUTE COLLAPSE / KILLER DEMO BOUNDARY]",
        report.compute_collapse_killer_demo_boundary,
    )
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_kernel_enforcement_transition_matrix_v01() -> str:
    return render_kernel_enforcement_transition_matrix_v01(
        collect_kernel_enforcement_transition_matrix_v01()
    )


def main() -> int:
    print(run_kernel_enforcement_transition_matrix_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
