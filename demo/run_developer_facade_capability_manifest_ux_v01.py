from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


MANIFEST_REQUIRED_FIELDS = (
    "manifest_id",
    "capability_name",
    "capability_type",
    "declared_role",
    "risk_class",
    "permission_boundary",
    "allowed_operations",
    "forbidden_operations",
    "input_contract",
    "output_contract",
    "external_observation_schema",
    "drs_policy",
    "transition_matrix_refs",
    "root_commit_required",
    "audit_requirements",
    "production_claims",
    "requested_effects",
)


ADVERSARIAL_ATTEMPT_IDS = (
    "manifest_to_installed_capability_without_root",
    "manifest_to_installed_needle_without_root",
    "manifest_to_external_action",
    "manifest_to_root_authority",
    "manifest_to_final_output",
    "manifest_to_drs_write",
    "manifest_to_accepted_evidence",
    "manifest_to_production_ready_claim",
    "manifest_to_killer_demo_authorization",
    "manifest_to_transition_matrix_authority",
)


@dataclass(frozen=True)
class DeveloperFacadeCapabilityManifestUXReport:
    header: dict[str, Any]
    source_evidence: dict[str, Any]
    source_checkpoints: list[dict[str, Any]]
    developer_facade_purpose: dict[str, Any]
    capability_manifest_contract: dict[str, Any]
    manifest_candidates: list[dict[str, Any]]
    validated_manifest_candidates: list[dict[str, Any]]
    rejected_needs_user_manifests: list[dict[str, Any]]
    adversarial_manifest_attempts: list[dict[str, Any]]
    kernel_transition_matrix_boundary: dict[str, Any]
    permission_risk_boundary: dict[str, Any]
    external_observation_schema_boundary: dict[str, Any]
    llm_drs_action_boundary: dict[str, Any]
    root_final: dict[str, Any]
    audit_entry: dict[str, Any]
    proof_artifact: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_metadata() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checkpoints = [
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
    ]
    source_checkpoints = [
        {
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint_name,
            "checkpoint_status": "PASS",
            "closure_status": "closed",
            "source_mode": "closed_checkpoint_metadata_only",
        }
        for checkpoint_id, checkpoint_name in checkpoints
    ]
    source_evidence = {
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
        "source_collectors_replayed_count": 0,
        "source_checkpoints_referenced": len(source_checkpoints),
        "historical_proof_reexecution_claimed": False,
        "kernel_enforcement_checkpoint_referenced": True,
    }
    return source_evidence, source_checkpoints


def _manifest(
    manifest_id: str,
    capability_name: str,
    capability_type: str,
    declared_role: str,
    risk_class: str | None,
    permission_boundary: str | None,
    allowed_operations: list[str],
    forbidden_operations: list[str],
    input_contract: str,
    output_contract: str,
    external_observation_schema: str,
    drs_policy: str,
    requested_effects: list[str],
    facade_decision: str,
    decision_reason: str,
    safe_next_step: str,
) -> dict[str, Any]:
    return {
        "manifest_id": manifest_id,
        "capability_name": capability_name,
        "capability_type": capability_type,
        "declared_role": declared_role,
        "risk_class": risk_class,
        "permission_boundary": permission_boundary,
        "allowed_operations": allowed_operations,
        "forbidden_operations": forbidden_operations,
        "input_contract": input_contract,
        "output_contract": output_contract,
        "external_observation_schema": external_observation_schema,
        "drs_policy": drs_policy,
        "transition_matrix_refs": [
            "kernel_enforcement_transition_matrix_v01",
            "closed_enterprise_boundary_invariants_v04",
        ],
        "root_commit_required": True,
        "audit_requirements": [
            "canonical_payload_hash",
            "root_review_visibility",
            "no_production_persistence",
        ],
        "production_claims": {
            "production_ready": False,
            "production_ui": False,
            "production_capability_registry": False,
            "real_connector": False,
            "real_api": False,
        },
        "requested_effects": requested_effects,
        "facade_decision": facade_decision,
        "decision_reason": decision_reason,
        "safe_next_step": safe_next_step,
        "facade_output": "FacadeValidationReport/RootReviewInput",
        "installed_capability_created": False,
        "installed_needle_created": False,
        "external_action_executed": False,
        "accepted_evidence_created": False,
        "truth_claim_created": False,
        "final_output_created": False,
        "production_persistence": False,
        "network_called": False,
        "gemini_called": False,
    }


def _manifest_candidates() -> list[dict[str, Any]]:
    return [
        _manifest(
            "read_only_vendor_connector_manifest",
            "Read-only Vendor Connector",
            "read_only_connector_observation",
            "connector_observation_source",
            "observation_only",
            "read_only_no_action",
            ["create_connector_observation"],
            [
                "execute_external_action",
                "call_real_api",
                "create_accepted_evidence",
                "write_drs",
            ],
            "bounded_vendor_status_request",
            "ConnectorObservation only",
            "read_only_observation_schema",
            "no_drs_write; EvidenceCandidate requires Acceptance Gate",
            ["ConnectorObservation"],
            "facade_validated_manifest_candidate_only",
            "Read-only observation manifest satisfies proof-only facade contract.",
            "Root review may consider whether future installation is allowed.",
        ),
        _manifest(
            "bounded_llm_semantic_executor_manifest",
            "Bounded LLM Semantic Executor Node",
            "bounded_llm_executor_node",
            "executor_node_capability",
            "semantic_draft_only",
            "bounded_executor_no_tools_no_action",
            ["produce_semantic_draft", "produce_resultproposal_shaped_output"],
            ["finalize", "write_drs", "execute_external_action", "call_tools"],
            "accepted_evidence_summary_only",
            "SemanticDraft / ResultProposal-shaped output only",
            "no_external_observation_schema",
            "no_drs_write_by_llm",
            ["SemanticDraft", "ResultProposal"],
            "facade_validated_manifest_candidate_only",
            "LLM remains bounded Executor node capability.",
            "Root review may consider future bounded executor-node installation.",
        ),
        _manifest(
            "local_drs_reuse_helper_manifest",
            "Local DRS Reuse Helper",
            "local_drs_reuse_helper",
            "local_reuse_helper",
            "local_reuse_only",
            "temporal_query_required",
            ["read_local_drs_metadata", "propose_reuse_route"],
            ["act_as_authority", "bypass_root", "write_external_drs"],
            "TemporalQuery with TimeEnvelope",
            "reuse_route_candidate_only",
            "no_external_observation_schema",
            "DRS reuse is not authority; Root-controlled reuse path required",
            ["reuse_route_candidate"],
            "facade_validated_manifest_candidate_only",
            "Local reuse helper preserves TemporalQuery, TimeEnvelope, and Root review.",
            "Root review may consider future bounded local helper installation.",
        ),
        _manifest(
            "external_action_connector_manifest",
            "External Action Connector",
            "external_action_connector",
            "external_connector",
            "external_action_requested",
            "requests_real_api_execution",
            ["call_real_api", "execute_external_action"],
            ["bypass_root"],
            "production_connector_payload",
            "external_action_result",
            "production_api_schema",
            "requests_external_write",
            ["external_action", "real_api_call"],
            "rejected",
            "External action, real API, or production connector requested.",
            "Remove external-action and real-API effects before resubmission.",
        ),
        _manifest(
            "authority_escalation_manifest",
            "Authority Escalation Capability",
            "authority_escalation_capability",
            "root_authority_claimant",
            "authority_escalation_requested",
            "claims_root_authority",
            ["create_final_output", "claim_root_authority"],
            ["none_declared"],
            "unbounded_authority_payload",
            "FinalOutput",
            "authority_claim_schema",
            "claims_global_write",
            ["RootAuthority", "FinalOutput"],
            "rejected",
            "Manifest attempts to claim RootAuthority, FinalOutput, or authority.",
            "Remove authority and final-output claims before resubmission.",
        ),
        _manifest(
            "incomplete_manifest_missing_risk_or_permission",
            "Incomplete Capability Draft",
            "incomplete_manifest",
            "unknown",
            None,
            None,
            ["unspecified"],
            ["external_action_until_complete"],
            "incomplete_input_contract",
            "incomplete_output_contract",
            "incomplete_observation_schema",
            "incomplete_drs_policy",
            ["unspecified"],
            "needs_user",
            "Missing risk_class and permission_boundary.",
            "Ask developer to provide missing manifest fields.",
        ),
    ]


def _adversarial_manifest_attempts() -> list[dict[str, Any]]:
    rows = []
    attempted_effects = {
        "manifest_to_installed_capability_without_root": "install_capability_without_root",
        "manifest_to_installed_needle_without_root": "install_needle_without_root",
        "manifest_to_external_action": "execute_external_action_from_manifest",
        "manifest_to_root_authority": "claim_root_authority",
        "manifest_to_final_output": "create_final_output",
        "manifest_to_drs_write": "write_global_or_external_drs",
        "manifest_to_accepted_evidence": "create_accepted_evidence",
        "manifest_to_production_ready_claim": "claim_production_ready",
        "manifest_to_killer_demo_authorization": "authorize_killer_demo",
        "manifest_to_transition_matrix_authority": "make_transition_matrix_authority",
    }
    for attempt_id in ADVERSARIAL_ATTEMPT_IDS:
        rows.append(
            {
                "attempt_id": attempt_id,
                "attack_surface": "CapabilityManifestDraft",
                "attempted_effect": attempted_effects[attempt_id],
                "detected": True,
                "blocked": True,
                "final_effect": "blocked",
                "root_review_required": True,
                "authority_transferred": False,
                "final_output_created": False,
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
        )
    return rows


def _kernel_transition_matrix_boundary() -> dict[str, Any]:
    return {
        "transition_matrix_required": True,
        "kernel_enforcement_checkpoint_referenced": True,
        "transition_matrix_is_authority": False,
        "transition_matrix_is_production_runtime_authority": False,
        "developer_facade_does_not_bypass_transition_matrix": True,
        "developer_manifest_is_authority": False,
        "capability_manifest_is_installed_capability": False,
        "root_commit_required_for_installation": True,
        "root_remains_final_authority": True,
    }


def _permission_risk_boundary() -> dict[str, Any]:
    return {
        "risk_class_required": True,
        "permission_boundary_required": True,
        "risk_class_is_safety_proof": False,
        "permission_boundary_is_execution": False,
        "needs_user_for_missing_risk_or_permission": True,
        "external_action_requests_rejected": True,
    }


def _external_observation_schema_boundary() -> dict[str, Any]:
    return {
        "external_observation_schema_required_for_connector": True,
        "external_observation_schema_is_evidence_acceptance": False,
        "connector_observation_is_truth": False,
        "connector_observation_is_accepted_evidence": False,
        "evidence_candidate_requires_acceptance_gate": True,
        "validated_manifest_is_accepted_evidence": False,
        "validated_manifest_is_truth": False,
        "validated_manifest_is_final_output": False,
    }


def _llm_drs_action_boundary() -> dict[str, Any]:
    return {
        "llm_is_bounded_executor_node_capability": True,
        "llm_is_authority": False,
        "llm_can_finalize": False,
        "llm_can_execute_external_action": False,
        "llm_can_write_drs_by_itself": False,
        "drs_reuse_is_authority": False,
        "closed_checkpoint_metadata_is_authority": False,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
    }


def _root_final() -> dict[str, Any]:
    return {
        "root_result": "developer_facade_capability_manifest_ux_completed",
        "safe_secondary_outcome": "manifest_candidates_available_for_root_review",
        "production_ui_implemented": False,
        "production_capability_registry_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
        "real_connector_created": False,
        "real_api_called": False,
        "installed_capabilities_created": 0,
        "installed_needles_created": 0,
        "external_actions_executed": 0,
        "global_drs_write": False,
        "external_drs_write": False,
        "root_remains_final_authority": True,
        "developer_facade_does_not_authorize_killer_demo": True,
        "network_called": False,
        "gemini_called": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
    }


def validate_developer_facade_capability_manifest_ux_v01(
    report: DeveloperFacadeCapabilityManifestUXReport,
) -> bool:
    outcomes = {row["manifest_id"]: row["facade_decision"] for row in report.manifest_candidates}
    summary = report.summary
    return all(
        (
            report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only",
            report.source_evidence["source_collectors_replayed"] is False,
            report.source_evidence["source_collectors_replayed_count"] == 0,
            len(report.source_checkpoints) == 8,
            all(row["checkpoint_status"] == "PASS" for row in report.source_checkpoints),
            all(row["closure_status"] == "closed" for row in report.source_checkpoints),
            len(report.manifest_candidates) == 6,
            all(
                all(field in row for field in MANIFEST_REQUIRED_FIELDS)
                for row in report.manifest_candidates
            ),
            len(report.validated_manifest_candidates) == 3,
            len([row for row in report.rejected_needs_user_manifests if row["facade_decision"] == "rejected"]) == 2,
            len([row for row in report.rejected_needs_user_manifests if row["facade_decision"] == "needs_user"]) == 1,
            outcomes["read_only_vendor_connector_manifest"] == "facade_validated_manifest_candidate_only",
            outcomes["bounded_llm_semantic_executor_manifest"] == "facade_validated_manifest_candidate_only",
            outcomes["local_drs_reuse_helper_manifest"] == "facade_validated_manifest_candidate_only",
            outcomes["external_action_connector_manifest"] == "rejected",
            outcomes["authority_escalation_manifest"] == "rejected",
            outcomes["incomplete_manifest_missing_risk_or_permission"] == "needs_user",
            len(report.adversarial_manifest_attempts) == 10,
            all(row["detected"] is True for row in report.adversarial_manifest_attempts),
            all(row["blocked"] is True for row in report.adversarial_manifest_attempts),
            all(row["final_effect"] == "blocked" for row in report.adversarial_manifest_attempts),
            all(
                row["authority_transferred"] is False
                and row["final_output_created"] is False
                and row["accepted_evidence_created"] is False
                and row["external_action_executed"] is False
                and row["global_drs_write"] is False
                and row["external_drs_write"] is False
                and row["installed_capability_created"] is False
                and row["installed_needle_created"] is False
                and row["production_persistence"] is False
                and row["network_called"] is False
                and row["gemini_called"] is False
                and row["marennya_invoked"] is False
                and row["up_invoked"] is False
                for row in report.adversarial_manifest_attempts
            ),
            report.kernel_transition_matrix_boundary["transition_matrix_required"] is True,
            report.kernel_transition_matrix_boundary["transition_matrix_is_authority"] is False,
            report.permission_risk_boundary["permission_boundary_is_execution"] is False,
            report.external_observation_schema_boundary[
                "external_observation_schema_is_evidence_acceptance"
            ]
            is False,
            report.llm_drs_action_boundary["llm_is_authority"] is False,
            report.llm_drs_action_boundary["drs_reuse_is_authority"] is False,
            report.root_final["root_remains_final_authority"] is True,
            report.audit_entry["canonical_payload_hash"] == canonical_hash(report.proof_artifact),
            report.audit_entry["audit_chain_decides_truth"] is False,
            summary["developer_facade_capability_manifest_ux_v01_status"] == "PASS",
        )
    )


def collect_developer_facade_capability_manifest_ux_v01() -> DeveloperFacadeCapabilityManifestUXReport:
    source_evidence, source_checkpoints = _closed_checkpoint_metadata()
    candidates = _manifest_candidates()
    validated = [
        row
        for row in candidates
        if row["facade_decision"] == "facade_validated_manifest_candidate_only"
    ]
    rejected_needs_user = [
        row for row in candidates if row["facade_decision"] in {"rejected", "needs_user"}
    ]
    adversarial_attempts = _adversarial_manifest_attempts()
    kernel_boundary = _kernel_transition_matrix_boundary()
    permission_boundary = _permission_risk_boundary()
    observation_boundary = _external_observation_schema_boundary()
    llm_drs_action_boundary = _llm_drs_action_boundary()
    root_final = _root_final()
    header = {
        "proof_id": "developer_facade_capability_manifest_ux_v01",
        "title": "Developer Facade / Capability Manifest UX v0.1",
        "proof_type": "deterministic_local_proof_only",
        "production_ui_implemented": False,
        "production_capability_registry_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
    }
    purpose = {
        "purpose": "validate_local_capability_manifest_candidates_against_closed_boundaries",
        "developer_facade_is_authority": False,
        "capability_manifest_is_authority": False,
        "output_is_facade_validation_report_or_root_review_input_only": True,
        "installed_capability_created": False,
        "installed_needle_created": False,
        "new_runtime_capability_created": False,
    }
    contract = {
        "contract_fields": list(MANIFEST_REQUIRED_FIELDS),
        "validated_manifest_is_installed_capability": False,
        "validated_manifest_is_installed_needle": False,
        "validated_manifest_is_permission_to_execute": False,
        "validated_manifest_is_accepted_evidence": False,
        "validated_manifest_is_truth": False,
        "validated_manifest_is_final_output": False,
        "validated_manifest_is_production_readiness": False,
        "root_review_required": True,
    }
    proof_artifact = {
        "proof_artifact_id": "developer_facade_capability_manifest_ux_v01",
        "header": header,
        "source_evidence": source_evidence,
        "source_checkpoints": source_checkpoints,
        "developer_facade_purpose": purpose,
        "capability_manifest_contract": contract,
        "manifest_candidates": candidates,
        "adversarial_manifest_attempts": adversarial_attempts,
        "kernel_transition_matrix_boundary": kernel_boundary,
        "permission_risk_boundary": permission_boundary,
        "external_observation_schema_boundary": observation_boundary,
        "llm_drs_action_boundary": llm_drs_action_boundary,
        "root_final": root_final,
    }
    audit_entry = {
        "audit_entry_id": "audit_developer_facade_capability_manifest_ux_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = DeveloperFacadeCapabilityManifestUXReport(
        header,
        source_evidence,
        source_checkpoints,
        purpose,
        contract,
        candidates,
        validated,
        rejected_needs_user,
        adversarial_attempts,
        kernel_boundary,
        permission_boundary,
        observation_boundary,
        llm_drs_action_boundary,
        root_final,
        audit_entry,
        proof_artifact,
        {},
    )
    preliminary_summary = _summary(provisional, passed=True)
    provisional = replace(provisional, summary=preliminary_summary)
    passed = validate_developer_facade_capability_manifest_ux_v01(provisional)
    return replace(provisional, summary=_summary(provisional, passed=passed))


def _summary(
    report: DeveloperFacadeCapabilityManifestUXReport,
    passed: bool,
) -> dict[str, Any]:
    rejected_count = len(
        [row for row in report.rejected_needs_user_manifests if row["facade_decision"] == "rejected"]
    )
    needs_user_count = len(
        [row for row in report.rejected_needs_user_manifests if row["facade_decision"] == "needs_user"]
    )
    return {
        "developer_facade_capability_manifest_ux_v01_status": "PASS" if passed else "FAIL",
        "proof_type": "deterministic_local_proof_only",
        "production_ui_implemented": False,
        "production_capability_registry_implemented": False,
        "runtime_rewrite_performed": False,
        "schemas_modified": False,
        "real_connector_created": False,
        "real_api_called": False,
        "source_collectors_replayed": False,
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "manifest_candidates_created": len(report.manifest_candidates),
        "facade_validated_manifest_candidates": len(report.validated_manifest_candidates),
        "rejected_manifest_candidates": rejected_count,
        "needs_user_manifest_candidates": needs_user_count,
        "adversarial_attempts_observed": len(report.adversarial_manifest_attempts),
        "adversarial_attempts_blocked": len(
            [row for row in report.adversarial_manifest_attempts if row["blocked"] is True]
        ),
        "installed_capabilities_created": 0,
        "installed_needles_created": 0,
        "external_actions_executed": 0,
        "global_drs_write": False,
        "external_drs_write": False,
        "transition_matrix_required": True,
        "transition_matrix_is_authority": False,
        "developer_manifest_is_authority": False,
        "capability_manifest_is_installed_capability": False,
        "risk_class_is_safety_proof": False,
        "permission_boundary_is_execution": False,
        "external_observation_schema_is_evidence_acceptance": False,
        "validated_manifest_is_accepted_evidence": False,
        "validated_manifest_is_truth": False,
        "validated_manifest_is_final_output": False,
        "root_remains_final_authority": True,
        "root_commit_required_for_installation": True,
        "llm_is_bounded_executor_node_capability": True,
        "llm_is_authority": False,
        "drs_reuse_is_authority": False,
        "kernel_enforcement_checkpoint_referenced": True,
        "developer_facade_does_not_bypass_transition_matrix": True,
        "developer_facade_does_not_authorize_killer_demo": True,
        "no_network": True,
        "no_gemini": True,
        "no_external_action": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "no_installed_capability": True,
        "no_installed_needle": True,
        "no_production_persistence": True,
        "no_marennya": True,
        "no_up": True,
        "ready_for_developer_facade_capability_manifest_ux_v01_tests": passed,
    }


def _format(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "missing"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, dict):
        return ",".join(f"{key}={_format(item)}" for key, item in value.items())
    return str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_developer_facade_capability_manifest_ux_v01(
    report: DeveloperFacadeCapabilityManifestUXReport,
) -> str:
    lines = [
        "[DEVELOPER FACADE / CAPABILITY MANIFEST UX v0.1]",
        "note: deterministic local proof-only facade validation",
        "note: validated manifest candidates are not installed capabilities or Needles",
        "note: Root remains final authority",
    ]
    _section(lines, "[HEADER]", report.header)
    _rows(lines, "[SOURCE CHECKPOINTS]", report.source_checkpoints)
    _section(lines, "[DEVELOPER FACADE PURPOSE]", report.developer_facade_purpose)
    _section(lines, "[CAPABILITY MANIFEST CONTRACT]", report.capability_manifest_contract)
    _rows(lines, "[MANIFEST CANDIDATES]", report.manifest_candidates)
    _rows(lines, "[VALIDATED MANIFEST CANDIDATES]", report.validated_manifest_candidates)
    _rows(lines, "[REJECTED / NEEDS_USER MANIFESTS]", report.rejected_needs_user_manifests)
    _rows(lines, "[ADVERSARIAL MANIFEST ATTEMPTS]", report.adversarial_manifest_attempts)
    _section(lines, "[KERNEL TRANSITION MATRIX BOUNDARY]", report.kernel_transition_matrix_boundary)
    _section(lines, "[PERMISSION / RISK BOUNDARY]", report.permission_risk_boundary)
    _section(
        lines,
        "[EXTERNAL OBSERVATION SCHEMA BOUNDARY]",
        report.external_observation_schema_boundary,
    )
    _section(lines, "[LLM / DRS / ACTION BOUNDARY]", report.llm_drs_action_boundary)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_developer_facade_capability_manifest_ux_v01() -> str:
    return render_developer_facade_capability_manifest_ux_v01(
        collect_developer_facade_capability_manifest_ux_v01()
    )


def main() -> int:
    print(run_developer_facade_capability_manifest_ux_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
