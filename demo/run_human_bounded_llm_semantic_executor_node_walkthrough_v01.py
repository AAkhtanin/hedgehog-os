from __future__ import annotations

from demo.run_bounded_llm_semantic_executor_node_v01 import (
    collect_bounded_llm_semantic_executor_node_v01,
)


def render_human_bounded_llm_semantic_executor_node_walkthrough_v01(report) -> str:
    source = report.source_evidence
    graph = report.plan_graph
    node_input = report.executor_semantic_node_input
    envelope = report.bounded_llm_call_envelope
    draft = report.semantic_draft
    proposal = report.semantic_draft_result_proposal
    gt = report.gt_semantic_advisory
    root = report.root_semantic_final
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN BOUNDED LLM SEMANTIC EXECUTOR NODE WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Bounded LLM Semantic "
        "Executor Node v0.1 proof. It is a deterministic local proof-only Executor-node "
        "capability using a mock LLM.",
        "",
        "There is no real Gemini call, network, tools, connector/API access, DRS write, "
        "external action, installed Needle, Marennya, UP, or production persistence.",
        "",
        "2. WHY THIS LAYER MATTERS",
        "",
        "After External Evidence Acceptance Gate, accepted evidence exists as bounded "
        "input. This layer proves that an LLM can help produce a semantic explanation "
        "inside an Executor node.",
        "",
        "It does not become a new subject or authority layer. That correction protects "
        "the passport geometry.",
        "",
        "3. CANONICAL GEOMETRY",
        "",
        "Root -> Orchestrator -> AVF / AttractorPacket -> Architect -> PlanGraph -> "
        "Executor -> llm_semantic_executor_node -> SemanticDraftResultProposal -> "
        "Post V&V -> GT -> Root Final.",
        "",
        "There is no LLM layer between Architect and Executor. There is no new global "
        "actor, global Gemini authority, global LLM agent authority, or post-Architect semantic authority. The LLM is only "
        "an executor_node_capability.",
        "",
        "Architect creates PlanGraph before LLM execution. Executor runs "
        "llm_semantic_summary_node. The mock LLM output becomes SemanticDraft, and "
        "Executor wraps it as SemanticDraftResultProposal. Post V&V, GT, and Root "
        "remain mandatory.",
        "",
        "4. SOURCE EVIDENCE MODE",
        "",
        "The prior External Evidence Acceptance Gate checkpoint is referenced as "
        "closed checkpoint metadata.",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        "",
        "This is targeted proof runtime hygiene, not full historical replay.",
        "",
        "5. PLAN GRAPH",
        "",
        f"Architect created PlanGraph {graph['plan_graph_id']} with four nodes:",
        "inspect_accepted_bank_payment_evidence.",
        "inspect_accepted_warehouse_stock_evidence.",
        "llm_semantic_summary_node.",
        "produce_readiness_explanation_candidate.",
        "",
        "PlanGraph exists before LLM execution. The LLM did not create or modify the "
        "PlanGraph, add or delete nodes, or route execution.",
        "",
        "6. EXECUTOR SEMANTIC NODE INPUT",
        "",
        f"Executor node id: {node_input['executor_node_id']}.",
        f"Input scope: {node_input['input_scope']}.",
        "Inputs: accepted_bank_payment_evidence and accepted_warehouse_stock_evidence.",
        "Raw connector observations are not included.",
        "Raw secrets are not included.",
        "The Executor boundary is valid.",
        "",
        "7. BOUNDED LLM CALL ENVELOPE",
        "",
        f"llm_provider={envelope['llm_provider']}.",
        f"llm_role={envelope['llm_role']}.",
        "bounded=true.",
        "proof_only=true.",
        "network_called=false.",
        "gemini_called=false.",
        "tools_allowed=false.",
        "connector_access_allowed=false.",
        "drs_write_allowed=false.",
        "external_action_allowed=false.",
        "plan_modification_allowed=false.",
        "root_final_allowed=false.",
        f"output_schema={envelope['output_schema']}.",
        "",
        "8. SEMANTIC DRAFT",
        "",
        "The mock LLM produces SemanticDraft only.",
        f"Semantic summary: {draft['semantic_summary']}",
        "Risk hints: accepted_evidence_is_not_truth and "
        "accepted_evidence_is_non_executable.",
        "Missing context: no final readiness decision has been made by Root.",
        f"confidence_label={draft['confidence_label']}.",
        "",
        "SemanticDraft is not truth, ready status, external action, DRS write, Needle, "
        "or Root final. SemanticDraft did not modify PlanGraph.",
        "",
        "9. RESULT PROPOSAL",
        "",
        f"Executor wraps SemanticDraft into {proposal['proposal_id']}.",
        f"proposal_type={proposal['proposal_type']}.",
        "completed=true.",
        "safe_for_post_vv=true.",
        "requires_post_vv=true.",
        "requires_gt=true.",
        "requires_root_final=true.",
        "",
        "The proposal is still not truth, ready status, action, DRS write, Needle, or "
        "Root final.",
        "",
        "10. POST V&V",
        "",
        "Post V&V passes because the schema and evidence scope are valid and there is "
        "no truth claim, ready claim, action claim, DRS write claim, Needle claim, plan "
        "modification, or Root final claim.",
        "",
        "11. GT",
        "",
        f"GT recommends {gt['gt_recommendation']}.",
        "GT is advisory only. GT cannot finalize, mark truth, mark ready, execute "
        "action, write DRS, or install a Needle.",
        "",
        "12. ROOT FINAL",
        "",
        f"root_result={root['root_result']}.",
        f"safe_secondary_outcome={root['safe_secondary_outcome']}.",
        "semantic_explanation_candidate_created=true.",
        "",
        "truth_proven=false.",
        "ready_status_created=false.",
        "external_action_executed=false.",
        "global_drs_write=false.",
        "external_drs_write=false.",
        "installed_needle_created=false.",
        "plan_modified_by_llm=false.",
        "root_final_created_by_llm=false.",
        "llm_is_global_actor=false.",
        "llm_is_orchestrator=false.",
        "llm_is_architect=false.",
        "llm_is_executor_node_capability=true.",
        "network_called=false.",
        "gemini_called=false.",
        "root_remains_final_authority=true.",
        "",
        "13. BOUNDARY MATRIX",
        "",
        "LLM is not Root, Orchestrator, Architect, GT, or Post V&V.",
        "LLM is Executor node capability.",
        "LLM does not create or modify PlanGraph.",
        "LLM does not route.",
        "LLM does not accept evidence.",
        "LLM does not prove truth.",
        "LLM does not create ready status.",
        "LLM does not execute action.",
        "LLM does not write DRS.",
        "LLM does not install Needle.",
        "LLM output is SemanticDraft only.",
        "SemanticDraft is not final result.",
        "ResultProposal requires Post V&V, GT, and Root.",
        "Root remains final authority.",
        "",
        "14. NINE ADVERSARIAL ATTEMPTS",
        "",
        f"adversary_llm_to_root_final: {attempts['adversary_llm_to_root_final']['final_effect']}.",
        f"adversary_llm_to_plan_modification: {attempts['adversary_llm_to_plan_modification']['final_effect']}.",
        f"adversary_llm_to_truth_claim: {attempts['adversary_llm_to_truth_claim']['final_effect']}.",
        f"adversary_llm_to_ready_status: {attempts['adversary_llm_to_ready_status']['final_effect']}.",
        f"adversary_llm_to_external_action: {attempts['adversary_llm_to_external_action']['final_effect']}.",
        f"adversary_llm_to_drs_write: {attempts['adversary_llm_to_drs_write']['final_effect']}.",
        f"adversary_llm_to_installed_needle: {attempts['adversary_llm_to_installed_needle']['final_effect']}.",
        f"adversary_llm_to_connector_access: {attempts['adversary_llm_to_connector_access']['final_effect']}.",
        f"adversary_llm_to_role_escalation: {attempts['adversary_llm_to_role_escalation']['final_effect']}.",
        "",
        f"{summary['adversarial_attempts_observed']} attempts were observed and "
        f"{summary['adversarial_attempts_blocked']} were blocked. There was no "
        "authority transfer, plan modification, Root final by LLM, network, or Gemini.",
        "",
        "15. WHAT THIS PROVES",
        "",
        "An LLM can safely sit inside Executor as a bounded semantic-node capability. "
        "Accepted evidence can be summarized semantically without becoming truth or "
        "action.",
        "",
        "LLM output can become ResultProposal only. The Post V&V, GT, and Root chain "
        "remains mandatory. Passport geometry survives.",
        "",
        "16. WHAT THIS DOES NOT PROVE",
        "",
        "It does not call real Gemini, implement live LLM mode or multi-LLM smoke, "
        "create a new actor, or give LLM authority.",
        "",
        "It does not create truth, ready status, action, DRS write, Needle, production "
        "persistence, or invoke Marennya or UP.",
        "",
        "17. FINAL HUMAN SUMMARY",
        "",
        "Architect created a four-node PlanGraph.",
        "Executor ran one bounded mock LLM semantic node.",
        "LLM produced SemanticDraft only.",
        "Executor wrapped it as ResultProposal.",
        "Post V&V passed.",
        "GT advised.",
        "Root accepted explanation candidate only.",
        "Nine escalation attempts were blocked.",
        "LLM is not Root, Orchestrator, Architect, GT, or Post V&V.",
        "LLM is only Executor node capability.",
        "Root remains final authority.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_bounded_llm_semantic_executor_node_walkthrough_v01() -> str:
    return render_human_bounded_llm_semantic_executor_node_walkthrough_v01(
        collect_bounded_llm_semantic_executor_node_v01()
    )


def main() -> int:
    print(run_human_bounded_llm_semantic_executor_node_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
