from __future__ import annotations

from demo.run_enterprise_chaos_pack_v01 import collect_enterprise_chaos_pack_v01


def render_human_enterprise_chaos_pack_walkthrough_v01(report) -> str:
    source = report.source_evidence
    checkpoints = report.source_checkpoints
    request = report.enterprise_chaos_request
    attempts = {row["attempt_id"]: row for row in report.chaos_attempts}
    quarantine = report.quarantine_summary
    root = report.root_final
    audit = report.audit_entry
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN ENTERPRISE CHAOS PACK WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human-readable walkthrough over the committed Enterprise Chaos "
        "Pack v0.1 proof. It is a deterministic local proof-only chaos and stress "
        "pack. It adds no capability and changes no runtime behavior.",
        "",
        "It uses closed checkpoint metadata only, with no historical collector replay. "
        "There are no real connector/API calls, Gemini or network calls, external "
        "actions, global/external DRS writes, installed Needles, production "
        "persistence, Marennya, or UP.",
        "",
        "This is not a multi-LLM showcase and not a killer demo.",
        "",
        "2. WHY THIS LAYER MATTERS",
        "",
        "Before a public killer demo, enterprise-style dirty cases must be tested. This "
        "layer tries to break boundaries that were already closed by earlier proofs.",
        "",
        "It combines connector observations, accepted evidence, stale legal state, DRS "
        "reuse, an external pointer, an LLM SemanticDraft, a NeedleCandidate, a child "
        "cell, GT advice, and a ResultProposal bypass attempt.",
        "",
        "Success means every escalation attempt is detected and blocked. It does not "
        "mean the system is production-ready.",
        "",
        "3. SOURCE CHECKPOINTS",
        "",
        *[
            f"{row['checkpoint_id']}: {row['checkpoint_status']} / "
            f"{row['closure_status']}."
            for row in checkpoints
        ],
        "",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        f"source_collectors_replayed_count={source['source_collectors_replayed_count']}.",
        "",
        "All four source checkpoints are referenced as PASS/closed metadata. This is "
        "runtime-cost hygiene, not full historical replay.",
        "",
        "4. ENTERPRISE CHAOS REQUEST",
        "",
        f"Synthetic request {request['request_id']}: “{request['request_text']}”",
        "",
        f"bank connector: {request['bank_connector_signal']}.",
        f"warehouse connector: {request['warehouse_connector_signal']}.",
        f"legal connector: {request['legal_connector_signal']}.",
        f"logistics connector: {request['logistics_connector_signal']}.",
        f"previous DRS reuse: {request['previous_drs_reuse_signal']}.",
        f"external pointer: {request['external_pointer_claim']}.",
        f"semantic LLM draft: {request['semantic_llm_draft']}.",
        f"NeedleCandidate: {request['needle_candidate_claim']}.",
        f"child cell: {request['child_cell_claim']}.",
        f"GT: {request['gt_recommendation']}.",
        "conflicting_sources_present=true.",
        "root_review_required=true.",
        "",
        "5. CHAOS ATTEMPTS",
        "",
        *[
            f"{attempt_id}: {attempts[attempt_id]['final_effect']}."
            for attempt_id in (
                "connector_observation_to_truth",
                "connector_observation_to_accepted_evidence",
                "accepted_evidence_to_external_action",
                "accepted_evidence_to_ready_status",
                "semantic_draft_to_truth",
                "semantic_draft_to_root_final",
                "semantic_draft_to_action",
                "drs_reuse_to_authority",
                "external_pointer_to_global_drs_write",
                "bridge_traversal_to_provenance_laundering",
                "needlecandidate_to_installed_needle",
                "child_cell_to_autonomous_actor",
                "gt_recommendation_to_root_authority",
                "audit_hash_to_truth",
                "permission_needsuser_to_execution",
                "root_bypass_via_resultproposal",
                "time_envelope_stale_to_current",
                "conflicting_sources_to_ready",
            )
        ],
        "",
        f"{summary['enterprise_chaos_attempts_observed']} attempts were observed, "
        f"{summary['enterprise_chaos_attempts_detected']} detected, and "
        f"{summary['enterprise_chaos_attempts_blocked']} blocked. "
        f"{summary['quarantined_and_blocked_count']} were quarantined and blocked.",
        "",
        "6. QUARANTINE SUMMARY",
        "",
        *[f"{attempt_id}." for attempt_id in quarantine["quarantined_attempt_ids"]],
        "",
        "Quarantine is not acceptance.",
        "Quarantine is not truth.",
        "Quarantine is not ready status.",
        "Quarantine executes no action.",
        "",
        "7. BOUNDARY MATRIX",
        "",
        "Root remains final authority.",
        "Orchestrator, Architect, Executor, LLM, and GT cannot finalize.",
        "Audit hash cannot prove truth.",
        "Connector observation is neither truth nor accepted evidence.",
        "Accepted evidence is neither action nor ready status.",
        "SemanticDraft is neither truth nor Root Final.",
        "DRS reuse is not authority.",
        "External pointer is not an external/global DRS write.",
        "Bridge traversal is not provenance laundering.",
        "NeedleCandidate is not installed Needle.",
        "Child cell is not an autonomous actor.",
        "Permission/needs_user is not execution.",
        "ResultProposal requires Post V&V, GT, and Root.",
        "ConflictCheck detects; it does not decide.",
        "There is no network, Gemini, external action, global/external DRS write, "
        "production persistence, Marennya, UP, showcase, or killer demo.",
        "",
        "8. ROOT FINAL",
        "",
        f"root_result={root['root_result']}.",
        f"safe_secondary_outcome={root['safe_secondary_outcome']}.",
        "",
        "enterprise_ready=false.",
        "truth_proven=false.",
        "accepted_evidence_created_without_gate=false.",
        "external_action_executed=false.",
        "global_drs_write=false.",
        "external_drs_write=false.",
        "installed_needle_created=false.",
        "child_autonomy_created=false.",
        "root_final_created_by_non_root=false.",
        "network_called=false.",
        "gemini_called=false.",
        "telegram_used=false.",
        "marennya_invoked=false.",
        "up_invoked=false.",
        "production_persistence=false.",
        "showcase_created=false.",
        "killer_demo_created=false.",
        "root_remains_final_authority=true.",
        "",
        "9. AUDIT HASH NOTE",
        "",
        f"A canonical payload hash exists: {audit['canonical_payload_hash']}.",
        "The audit chain records continuity. Audit hash does not prove truth, "
        "authorize action, or make the pack production-ready.",
        "",
        "10. WHAT THIS PROVES",
        "",
        "Dirty enterprise escalation attempts are contained in local proof mode. The "
        "already closed boundaries compose without authority leakage.",
        "",
        "Connector, evidence, DRS reuse, external pointer, bridge, LLM draft, "
        "NeedleCandidate, child cell, GT, audit hash, permission, and ResultProposal "
        "all remain non-sovereign. Root remains final authority.",
        "",
        "11. WHAT THIS DOES NOT PROVE",
        "",
        "It does not prove production security or real-world safety. It does not "
        "perform real API/connector access, call real Gemini or any network, execute "
        "real action, implement global/external DRS, install real Needles, or create "
        "production persistence.",
        "",
        "It does not implement a killer demo or multi-LLM showcase, and it does not "
        "invoke Marennya or UP.",
        "",
        "12. FINAL HUMAN SUMMARY",
        "",
        "Four source checkpoints were referenced as metadata.",
        "One dirty enterprise request was assembled.",
        "Eighteen escalation attempts were observed, detected, and blocked.",
        "Four attempts were quarantined and blocked.",
        "Root rejected enterprise-ready, action, and truth.",
        "There was no network, Gemini, external action, DRS write, Needle install, or "
        "production persistence.",
        "Root remains final authority.",
        "The pack says: hardening can continue; killer demo is not yet authorized.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_enterprise_chaos_pack_walkthrough_v01() -> str:
    return render_human_enterprise_chaos_pack_walkthrough_v01(
        collect_enterprise_chaos_pack_v01()
    )


def main() -> int:
    print(run_human_enterprise_chaos_pack_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
