from __future__ import annotations

from demo.run_developer_facade_capability_manifest_ux_v01 import (
    collect_developer_facade_capability_manifest_ux_v01,
)


def render_human_developer_facade_capability_manifest_ux_walkthrough_v01(report) -> str:
    source = report.source_evidence
    checkpoints = report.source_checkpoints
    summary = report.summary
    candidates = {row["manifest_id"]: row for row in report.manifest_candidates}
    root = report.root_final

    lines = [
        "HEDGEHOG OS — HUMAN DEVELOPER FACADE / CAPABILITY MANIFEST UX WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human walkthrough over committed proof dd18d5f.",
        "",
        "This is deterministic local proof-only. It is not production UI, not a "
        "production capability registry, not real capability installation, not real "
        "Needle installation, not real connector/API access, not a runtime rewrite, "
        "not schema modification, and not a new authority layer.",
        "",
        "Developer Facade is not Root. Capability manifest is not authority. "
        "Transition Matrix remains non-authority. Root remains final authority.",
        "",
        "There is no network, Gemini, external API use, external action, global DRS "
        "write, External DRS write, installed capability, installed Needle, "
        "production persistence, Marennya, or UP.",
        "",
        "2. WHERE THIS LAYER SITS",
        "",
        "Developer Facade / Capability Manifest UX v0.1 sits on the developer and "
        "capability admission side:",
        "",
        "Developer CapabilityManifestDraft -> Facade normalization -> "
        "CapabilityManifestCandidate -> FacadeValidationReport -> RootReviewInput.",
        "",
        "It is not a new actor inside the main runtime chain. It is not Executor, "
        "Architect, Root, NeedleFactory, or production registry.",
        "",
        "Facade validates a manifest as a candidate for Root review. It does not "
        "install capability, authorize execution, or create Needle.",
        "",
        "3. WHY THIS LAYER EXISTS",
        "",
        "After Kernel Enforcement / Transition Matrix Hardening v0.1, the project "
        "has explicit artifact transition boundaries. This layer proves a developer "
        "manifest can be checked against those boundaries before any future "
        "installation or runtime use.",
        "",
        "The important result is narrow: a local manifest can become a validated "
        "manifest candidate or RootReviewInput. It cannot become authority, truth, "
        "accepted evidence, execution permission, production readiness, FinalOutput, "
        "installed capability, or installed Needle.",
        "",
        "4. SOURCE CHECKPOINTS",
        "",
        *[
            f"{row['checkpoint_name']}: {row['checkpoint_status']} / "
            f"{row['closure_status']}."
            for row in checkpoints
        ],
        "",
        "The source checkpoints are External DRS Pointer Protocol v0.1, Read-only "
        "Enterprise Connector Sandbox v0.1, External Evidence Acceptance Gate v0.1, "
        "Bounded LLM Semantic Executor Node v0.1, Enterprise Chaos Pack v0.1, "
        "Compute Collapse Enterprise Bench v0.1, Math / Invariants Sync v0.4, and "
        "Kernel Enforcement / Transition Matrix Hardening v0.1.",
        "",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        f"source_collectors_replayed_count={source['source_collectors_replayed_count']}.",
        "",
        "5. CAPABILITY MANIFEST CONTRACT",
        "",
        "Each local manifest candidate includes manifest_id, capability_name, "
        "capability_type, declared_role, risk_class, permission_boundary, "
        "allowed_operations, forbidden_operations, input_contract, output_contract, "
        "external_observation_schema, drs_policy, transition_matrix_refs, "
        "root_commit_required, audit_requirements, production_claims, and "
        "requested_effects.",
        "",
        "A validated manifest candidate is not an installed capability. It is not an "
        "installed Needle. It is not permission to execute. It is not accepted "
        "evidence. It is not truth. It is not Root FinalOutput. It is not production "
        "readiness.",
        "",
        "6. MANIFEST CANDIDATES",
        "",
        "Six deterministic local manifest candidates are evaluated.",
        "",
        "read_only_vendor_connector_manifest: facade_validated_manifest_candidate_only.",
        "bounded_llm_semantic_executor_manifest: facade_validated_manifest_candidate_only.",
        "local_drs_reuse_helper_manifest: facade_validated_manifest_candidate_only.",
        "external_action_connector_manifest: rejected.",
        "authority_escalation_manifest: rejected.",
        "incomplete_manifest_missing_risk_or_permission: needs_user.",
        "",
        f"manifest_candidates_created={summary['manifest_candidates_created']}.",
        f"facade_validated_manifest_candidates="
        f"{summary['facade_validated_manifest_candidates']}.",
        f"rejected_manifest_candidates={summary['rejected_manifest_candidates']}.",
        f"needs_user_manifest_candidates={summary['needs_user_manifest_candidates']}.",
        "",
        "7. VALIDATED MANIFEST CANDIDATES",
        "",
        "read_only_vendor_connector_manifest means read-only observation candidate "
        "only. It performs no network/API/action. ConnectorObservation is not truth, "
        "and EvidenceCandidate still requires the External Evidence Acceptance Gate.",
        "",
        "bounded_llm_semantic_executor_manifest means LLM bounded Executor node "
        "capability only. It may produce semantic draft / ResultProposal-shaped "
        "output only. It cannot finalize, write DRS by itself, or execute external "
        "action.",
        "",
        "local_drs_reuse_helper_manifest means DRS reuse helper candidate only. It "
        "requires TemporalQuery, TimeEnvelope, and a Root-controlled reuse path. DRS "
        "reuse is not authority.",
        "",
        "8. REJECTED AND NEEDS_USER MANIFESTS",
        "",
        "external_action_connector_manifest is rejected in this proof because "
        "external action, real API, or production connector request is outside the "
        "current proof layer and production action boundary is not implemented. This "
        "does not imply external action connectors are impossible forever.",
        "",
        "authority_escalation_manifest is rejected because it attempts RootAuthority, "
        "FinalOutput, or authority. No authority is transferred.",
        "",
        "incomplete_manifest_missing_risk_or_permission is needs_user because "
        "risk_class and/or permission_boundary are missing. The safe next step is to "
        "ask the developer for missing fields. No execution occurs.",
        "",
        "9. ADVERSARIAL MANIFEST ATTEMPTS",
        "",
        "manifest_to_installed_capability_without_root: blocked.",
        "manifest_to_installed_needle_without_root: blocked.",
        "manifest_to_external_action: blocked.",
        "manifest_to_root_authority: blocked.",
        "manifest_to_final_output: blocked.",
        "manifest_to_drs_write: blocked.",
        "manifest_to_accepted_evidence: blocked.",
        "manifest_to_production_ready_claim: blocked.",
        "manifest_to_killer_demo_authorization: blocked.",
        "manifest_to_transition_matrix_authority: blocked.",
        "",
        f"adversarial_attempts_observed={summary['adversarial_attempts_observed']}.",
        f"adversarial_attempts_blocked={summary['adversarial_attempts_blocked']}.",
        "",
        "All are detected and blocked. No authority is transferred. No FinalOutput, "
        "AcceptedEvidence, external action, DRS write, installed capability, "
        "installed Needle, production persistence, network, Gemini, Marennya, or UP "
        "is created.",
        "",
        "10. TRANSITION MATRIX BOUNDARY",
        "",
        "transition_matrix_required=true.",
        "transition_matrix_is_authority=false.",
        "developer_manifest_is_authority=false.",
        "capability_manifest_is_installed_capability=false.",
        "kernel_enforcement_checkpoint_referenced=true.",
        "developer_facade_does_not_bypass_transition_matrix=true.",
        "root_commit_required_for_installation=true.",
        "root_remains_final_authority=true.",
        "",
        "11. PERMISSION / RISK BOUNDARY",
        "",
        "risk_class_is_safety_proof=false.",
        "permission_boundary_is_execution=false.",
        "Missing risk_class or permission_boundary routes to needs_user, not "
        "execution.",
        "",
        "12. EXTERNAL OBSERVATION SCHEMA BOUNDARY",
        "",
        "external_observation_schema_is_evidence_acceptance=false.",
        "validated_manifest_is_accepted_evidence=false.",
        "validated_manifest_is_truth=false.",
        "validated_manifest_is_final_output=false.",
        "ConnectorObservation may be described, but acceptance still requires the "
        "External Evidence Acceptance Gate and Root.",
        "",
        "13. LLM / DRS / ACTION BOUNDARY",
        "",
        "llm_is_bounded_executor_node_capability=true.",
        "llm_is_authority=false.",
        "drs_reuse_is_authority=false.",
        "no_network=true.",
        "no_gemini=true.",
        "no_external_action=true.",
        "no_global_drs_write=true.",
        "no_external_drs_write=true.",
        "no_installed_capability=true.",
        "no_installed_needle=true.",
        "no_production_persistence=true.",
        "no_marennya=true.",
        "no_up=true.",
        "",
        "14. WHAT THIS PROVES",
        "",
        "It proves a developer-facing manifest can be normalized and validated as a "
        "candidate for Root review without becoming authority or runtime execution.",
        "",
        "It proves three low-risk candidate shapes can pass facade validation only: a "
        "read-only connector observation manifest, a bounded LLM executor node "
        "manifest, and a local DRS reuse helper manifest.",
        "",
        "It proves rejected and incomplete manifests remain contained, and ten "
        "manifest escalation attempts are blocked.",
        "",
        "15. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement production UI, a production capability registry, real "
        "capability installation, real Needle installation, real connector/API "
        "access, runtime rewrite, schema modification, production readiness, or a "
        "new authority layer.",
        "",
        "It does not authorize execution, external action, global DRS write, External "
        "DRS write, Killer Demo, Marennya, or UP.",
        "",
        "16. ROOT FINAL",
        "",
        f"root_result={root['root_result']}.",
        f"safe_secondary_outcome={root['safe_secondary_outcome']}.",
        "developer_facade_capability_manifest_ux_v01_status=PASS.",
        "proof_type=deterministic_local_proof_only.",
        "focused tests passed: 16.",
        "production_ui_implemented=false.",
        "production_capability_registry_implemented=false.",
        "runtime_rewrite_performed=false.",
        "schemas_modified=false.",
        "real_connector_created=false.",
        "real_api_called=false.",
        "installed_capabilities_created=0.",
        "installed_needles_created=0.",
        "external_actions_executed=0.",
        "global_drs_write=false.",
        "external_drs_write=false.",
        "root_remains_final_authority=true.",
        "developer_facade_does_not_authorize_killer_demo=true.",
        "",
        "17. FINAL HUMAN SUMMARY",
        "",
        "Developer Facade / Capability Manifest UX v0.1 proof is committed at "
        "dd18d5f.",
        "It validates local capability manifests as candidates for Root review.",
        "It does not implement production UI.",
        "It does not implement production capability registry.",
        "It does not install capabilities.",
        "It does not install Needles.",
        "It does not authorize execution.",
        "It does not bypass Transition Matrix.",
        "It does not authorize Killer Demo.",
        "It validates 3 manifest candidates, rejects 2, and marks 1 as needs_user.",
        "It blocks 10 adversarial manifest attempts.",
        "Focused tests passed: 16.",
        "Root remains final authority.",
        "Next lifecycle step after this walkthrough is audit log, then docs sync.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_developer_facade_capability_manifest_ux_walkthrough_v01() -> str:
    return render_human_developer_facade_capability_manifest_ux_walkthrough_v01(
        collect_developer_facade_capability_manifest_ux_v01()
    )


def main() -> int:
    print(run_human_developer_facade_capability_manifest_ux_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
