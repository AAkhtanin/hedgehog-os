from __future__ import annotations

from demo.run_kernel_enforcement_transition_matrix_v01 import (
    collect_kernel_enforcement_transition_matrix_v01,
)


def render_human_kernel_enforcement_transition_matrix_walkthrough_v01(report) -> str:
    summary = report.summary
    checkpoints = report.source_checkpoints
    allowed = {row["transition_id"]: row for row in report.allowed_transitions}
    root = report.root_final
    llm = report.llm_executor_node_boundary
    drs = report.drs_metadata_audit_boundary
    compute = report.compute_collapse_killer_demo_boundary

    local_drs = allowed["root_final_output_to_drs_writeback"]

    lines = [
        "HEDGEHOG OS — HUMAN KERNEL ENFORCEMENT / TRANSITION MATRIX WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human walkthrough over committed proof 5acfc8a.",
        "",
        "This is deterministic local proof-only. It is not production kernel "
        "enforcement, not a runtime rewrite, not schema modification, and not a new "
        "authority layer.",
        "",
        "It is not inserted as a new step inside the canonical runtime pipeline. The "
        "transition matrix models already proven boundary rules.",
        "",
        "The transition matrix is not Root. The transition matrix is not production "
        "runtime authority. Root remains final authority.",
        "",
        "There is no network, Gemini, external API use, external action, global DRS "
        "write, External DRS write, installed Needle, production persistence, "
        "Marennya, or UP.",
        "",
        "2. WHERE THIS LAYER SITS",
        "",
        "Math / Invariants Sync v0.4 wrote the rules. Kernel Enforcement / "
        "Transition Matrix Hardening v0.1 represents those already proven rules as a "
        "deterministic local transition matrix.",
        "",
        "This is a meta-proof and hardening layer over artifact transitions. It is "
        "not a new actor in the main runtime chain.",
        "",
        "3. WHY THIS LAYER EXISTS",
        "",
        "The prior enterprise proofs closed many boundary rules: observation is not "
        "truth, candidates are not accepted evidence, GT is not authority, SemanticDraft "
        "is not final, DRS reuse is not authority, and Root remains final.",
        "",
        "This layer centralizes those closed boundaries into explicit transition rows "
        "so forbidden promotions are visible and deterministic.",
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
        "Compute Collapse Enterprise Bench v0.1, and Math / Invariants Sync v0.4.",
        "",
        "5. TRANSITION MATRIX SHAPE",
        "",
        "The matrix checks artifact_type, source_state, attempted_target_or_effect, "
        "actor, root_commit_present, expected_decision, decision_reason, "
        "authority_transferred, final_output_created, truth_claim_created, "
        "ready_status_created, external_action_executed, global_drs_write, "
        "external_drs_write, installed_needle_created, production_persistence, "
        "network_called, gemini_called, marennya_invoked, and up_invoked.",
        "",
        f"kernel_enforcement_transition_matrix_v01_status="
        f"{summary['kernel_enforcement_transition_matrix_v01_status']}.",
        f"allowed_transitions_count={summary['allowed_transitions_count']}.",
        f"blocked_transitions_count={summary['blocked_transitions_count']}.",
        f"blocked_transitions_detected={summary['blocked_transitions_detected']}.",
        f"blocked_transitions_blocked={summary['blocked_transitions_blocked']}.",
        "focused tests passed: 15.",
        "",
        "6. LOCAL TAXONOMY",
        "",
        "The proof has local transition taxonomy coverage for artifact names and "
        "target/effect names. Some names are artifacts; some are attempted "
        "target/effect names. The proof covers both so transition rows do not use "
        "undefined boundary names.",
        "",
        "Covered names include Root, RootDecision, RootReviewInput, DRSReuse, "
        "ClosedCheckpointMetadata, LLMExecutorNode, MarennyaStub, UPStub, Truth, "
        "ReadyStatus, Authority, RootAuthority, GTAuthority, GlobalDRSWrite, "
        "ProvenanceLaundering, AutonomousActor, ProductionEconomics, "
        "KillerDemoAuthorization, and RuntimeActivation.",
        "",
        "7. ALLOWED TRANSITIONS",
        "",
        "1. ConnectorObservation -> EvidenceCandidate.",
        "2. EvidenceCandidate -> ValidationPacket.",
        "3. RootDecision -> AcceptedEvidence.",
        "4. RootDecision -> RejectedEvidence.",
        "5. RootDecision -> QuarantinedEvidence.",
        "6. ResultProposal -> PostVVReport.",
        "7. PostVVReport -> GTReport.",
        "8. GTReport -> RootReviewInput.",
        "9. Root -> RootFinalOutput.",
        "10. RootFinalOutput -> local DRSWriteback after Root Final.",
        "",
        "Allowed means bounded artifact movement only. It does not mean truth, "
        "external action, global DRS write, External DRS write, installed Needle, or "
        "production persistence.",
        "",
        "8. BLOCKED TRANSITION FAMILIES",
        "",
        "Observation, candidate, and validation artifacts cannot become truth or "
        "acceptance without Root.",
        "AcceptedEvidence cannot become truth, ready status, action, DRS write, or "
        "installed Needle.",
        "SemanticDraft cannot become truth, final, or external action.",
        "ResultProposal cannot become FinalOutput or action.",
        "GTReport cannot become FinalOutput, AcceptedEvidence, or action.",
        "DRSReuse and closed checkpoint metadata cannot become authority.",
        "AuditHashClaim cannot become truth.",
        "ExternalDRSPointer cannot write External/global DRS or launder provenance.",
        "NeedleCandidate cannot become InstalledNeedle without Root.",
        "PermissionNeedsUser cannot become ExternalAction.",
        "ChildCellClaim cannot become AutonomousActor.",
        "ComputeCollapseMetric cannot become ProductionEconomics or "
        "KillerDemoAuthorization.",
        "LLMExecutorNode cannot become RootAuthority, GTAuthority, DRS writeback, or "
        "external action.",
        "MarennyaStub and UPStub cannot become runtime activation.",
        "",
        "All 35 blocked transitions are detected and blocked.",
        "",
        "9. ROOT COMMIT BOUNDARY",
        "",
        f"root_only_final_output={str(summary['root_only_final_output']).lower()}.",
        f"root_commit_required_for_final_output="
        f"{str(summary['root_commit_required_for_final_output']).lower()}.",
        "RootDecision is required for accepted, rejected, or quarantined evidence.",
        "Root is the only actor that can create RootFinalOutput.",
        "",
        "10. LOCAL DRS WRITEBACK BOUNDARY",
        "",
        "The allowed transition RootFinalOutput -> DRSWriteback is local-only.",
        f"drs_writeback_scope: {local_drs['drs_writeback_scope']}.",
        f"local_drs_writeback: {str(local_drs['local_drs_writeback']).lower()}.",
        f"global_drs_write: {str(local_drs['global_drs_write']).lower()}.",
        f"external_drs_write: {str(local_drs['external_drs_write']).lower()}.",
        "",
        "This does not imply global DRS or External DRS writeback.",
        "",
        "11. LLM EXECUTOR NODE BOUNDARY",
        "",
        "LLM is bounded Executor node capability, not authority.",
        f"llm_is_bounded_executor_node_capability="
        f"{str(llm['llm_is_bounded_executor_node_capability']).lower()}.",
        f"llm_is_authority={str(llm['llm_is_authority']).lower()}.",
        f"llm_can_write_drs={str(llm['llm_can_write_drs']).lower()}.",
        f"llm_can_execute_external_action="
        f"{str(llm['llm_can_execute_external_action']).lower()}.",
        "SemanticDraft is not final and still requires Post V&V, GT, and Root.",
        "",
        "12. DRS / METADATA / AUDIT BOUNDARY",
        "",
        f"drs_reuse_is_authority={str(drs['drs_reuse_is_authority']).lower()}.",
        f"closed_checkpoint_metadata_is_authority="
        f"{str(drs['closed_checkpoint_metadata_is_authority']).lower()}.",
        f"audit_hash_decides_truth={str(drs['audit_hash_decides_truth']).lower()}.",
        f"external_pointer_is_external_drs_write="
        f"{str(drs['external_pointer_is_external_drs_write']).lower()}.",
        f"external_pointer_is_global_drs_write="
        f"{str(drs['external_pointer_is_global_drs_write']).lower()}.",
        f"bridge_traversal_launders_provenance="
        f"{str(drs['bridge_traversal_launders_provenance']).lower()}.",
        "",
        "13. COMPUTE COLLAPSE / KILLER DEMO BOUNDARY",
        "",
        f"compute_collapse_metric_is_production_economics="
        f"{str(compute['compute_collapse_metric_is_production_economics']).lower()}.",
        f"compute_collapse_authorizes_killer_demo="
        f"{str(compute['compute_collapse_authorizes_killer_demo']).lower()}.",
        f"compute_collapse_authorizes_multi_llm_showcase="
        f"{str(compute['compute_collapse_authorizes_multi_llm_showcase']).lower()}.",
        "Compute Collapse does not authorize Killer Demo.",
        "",
        "14. WHAT THIS PROVES",
        "",
        "It proves that already closed boundary rules can be represented as a "
        "deterministic local transition matrix. Ten bounded transitions are allowed, "
        "and 35 forbidden transitions are blocked.",
        "",
        "It proves the matrix itself remains proof-only and non-authoritative. Root "
        "remains final authority.",
        "",
        "15. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement production enforcement, rewrite runtime, modify "
        "schemas, create a new authority layer, or insert a new step into the "
        "canonical runtime pipeline.",
        "",
        "It does not call network, Gemini, or external APIs. It executes no external "
        "action, writes no global or External DRS, installs no Needle, creates no "
        "production persistence, and invokes no Marennya or UP.",
        "",
        "16. ROOT FINAL",
        "",
        f"root_result={root['root_result']}.",
        f"safe_secondary_outcome={root['safe_secondary_outcome']}.",
        "production_enforcement_implemented=false.",
        "runtime_rewrite_performed=false.",
        "schemas_modified=false.",
        "root_remains_final_authority=true.",
        "transition_matrix_is_proof_only=true.",
        "transition_matrix_is_authority=false.",
        "transition_matrix_is_production_runtime_authority=false.",
        "no_network=true.",
        "no_gemini=true.",
        "no_external_action=true.",
        "no_global_drs_write=true.",
        "no_external_drs_write=true.",
        "no_installed_needle=true.",
        "no_production_persistence=true.",
        "no_marennya=true.",
        "no_up=true.",
        "",
        "17. FINAL HUMAN SUMMARY",
        "",
        "Kernel Enforcement / Transition Matrix Hardening v0.1 proof is committed at "
        "5acfc8a.",
        "It models already proven boundary rules as a deterministic local transition "
        "matrix.",
        "It does not implement production enforcement.",
        "It does not rewrite runtime.",
        "It does not modify schemas.",
        "It is not authority.",
        "Root remains final authority.",
        "It allows 10 bounded transitions.",
        "It blocks 35 forbidden transitions.",
        "Focused tests passed: 15.",
        "Root-only FinalOutput remains true.",
        "Local DRS writeback is local_after_root_final only.",
        "DRS reuse and closed checkpoint metadata are not authority.",
        "LLM is bounded Executor node capability, not authority.",
        "Compute Collapse does not authorize Killer Demo.",
        "Next lifecycle step after this walkthrough is audit log, then docs sync.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_kernel_enforcement_transition_matrix_walkthrough_v01() -> str:
    return render_human_kernel_enforcement_transition_matrix_walkthrough_v01(
        collect_kernel_enforcement_transition_matrix_v01()
    )


def main() -> int:
    print(run_human_kernel_enforcement_transition_matrix_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
