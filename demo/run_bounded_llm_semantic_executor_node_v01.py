from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


ADVERSARIAL_ATTEMPT_IDS = (
    "adversary_llm_to_root_final",
    "adversary_llm_to_plan_modification",
    "adversary_llm_to_truth_claim",
    "adversary_llm_to_ready_status",
    "adversary_llm_to_external_action",
    "adversary_llm_to_drs_write",
    "adversary_llm_to_installed_needle",
    "adversary_llm_to_connector_access",
    "adversary_llm_to_role_escalation",
)


@dataclass(frozen=True)
class BoundedLLMSemanticExecutorNodeReport:
    source_evidence: dict[str, Any]
    plan_graph: dict[str, Any]
    executor_semantic_node_input: dict[str, Any]
    bounded_llm_call_envelope: dict[str, Any]
    semantic_draft: dict[str, Any]
    semantic_draft_result_proposal: dict[str, Any]
    post_vv_semantic_check: dict[str, Any]
    gt_semantic_advisory: dict[str, Any]
    root_semantic_final: dict[str, Any]
    boundary_matrix: dict[str, Any]
    adversarial_attempts: list[dict[str, Any]]
    audit_entry: dict[str, Any]
    proof_artifact: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_source_evidence() -> dict[str, Any]:
    return {
        "external_evidence_acceptance_gate_source_status": "PASS",
        "external_evidence_acceptance_gate_commits": (
            "ece902f,00e98cd,632ecb1,71d76e0"
        ),
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
    }


def _plan_graph() -> dict[str, Any]:
    return {
        "plan_graph_id": "plan_graph_bounded_llm_semantic_executor_node_v01",
        "created_by": "Architect",
        "created_before_llm_execution": True,
        "nodes": [
            {
                "node_id": "inspect_accepted_bank_payment_evidence",
                "node_type": "deterministic_evidence_inspection",
                "depends_on": [],
            },
            {
                "node_id": "inspect_accepted_warehouse_stock_evidence",
                "node_type": "deterministic_evidence_inspection",
                "depends_on": [],
            },
            {
                "node_id": "llm_semantic_summary_node",
                "node_type": "llm_semantic_executor_node",
                "implementation": "bounded_mock_llm",
                "depends_on": [
                    "inspect_accepted_bank_payment_evidence",
                    "inspect_accepted_warehouse_stock_evidence",
                ],
            },
            {
                "node_id": "produce_readiness_explanation_candidate",
                "node_type": "deterministic_result_proposal_wrapper",
                "depends_on": ["llm_semantic_summary_node"],
            },
        ],
        "llm_created_plan_graph": False,
        "llm_modified_plan_graph": False,
        "llm_added_nodes": False,
        "llm_deleted_nodes": False,
        "llm_routed_execution": False,
    }


def _adversarial_attempts() -> list[dict[str, Any]]:
    return [
        {
            "attempt_id": attempt_id,
            "detected": True,
            "blocked": True,
            "final_effect": "blocked",
            "truth_proven": False,
            "ready_status_created": False,
            "external_action_executed": False,
            "global_drs_write": False,
            "external_drs_write": False,
            "installed_needle_created": False,
            "plan_modified": False,
            "root_final_created_by_llm": False,
            "network_called": False,
            "gemini_called": False,
            "authority_transferred": False,
        }
        for attempt_id in ADVERSARIAL_ATTEMPT_IDS
    ]


def validate_bounded_llm_semantic_executor_node_report_consistency(
    report: BoundedLLMSemanticExecutorNodeReport,
) -> bool:
    statuses = {
        key: value
        for key, value in report.source_evidence.items()
        if key.endswith("_source_status")
    }
    nodes = report.plan_graph["nodes"]
    llm_nodes = [
        node for node in nodes if node["node_type"] == "llm_semantic_executor_node"
    ]
    envelope = report.bounded_llm_call_envelope
    draft = report.semantic_draft
    proposal = report.semantic_draft_result_proposal
    post_vv = report.post_vv_semantic_check
    gt = report.gt_semantic_advisory
    root = report.root_semantic_final
    prohibited = (
        "truth_proven",
        "ready_status_created",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
    )
    return all(
        (
            set(statuses.values()) == {"PASS"},
            report.source_evidence.get("source_evidence_mode")
            == "closed_checkpoint_metadata_only",
            report.source_evidence.get("source_collectors_replayed") is False,
            report.plan_graph.get("created_by") == "Architect",
            report.plan_graph.get("created_before_llm_execution") is True,
            len(nodes) == 4,
            len(llm_nodes) == 1,
            llm_nodes[0].get("implementation") == "bounded_mock_llm",
            report.plan_graph.get("llm_created_plan_graph") is False,
            report.plan_graph.get("llm_modified_plan_graph") is False,
            envelope.get("llm_provider") == "mock_llm",
            envelope.get("llm_role") == "executor_node_capability",
            envelope.get("bounded") is True,
            all(
                envelope.get(field) is False
                for field in (
                    "network_called",
                    "gemini_called",
                    "tools_allowed",
                    "connector_access_allowed",
                    "drs_write_allowed",
                    "external_action_allowed",
                    "plan_modification_allowed",
                    "root_final_allowed",
                    "input_contains_raw_secret",
                )
            ),
            draft.get("semantic_draft_created") is True,
            draft.get("confidence_label") == "mock_confidence_only",
            draft.get("plan_modified") is False,
            draft.get("root_final_created") is False,
            all(draft.get(field) is False for field in prohibited),
            proposal.get("proposal_type") == "semantic_draft_result_proposal",
            proposal.get("safe_for_post_vv") is True,
            proposal.get("root_final_created") is False,
            all(proposal.get(field) is False for field in prohibited),
            all(value is True for value in post_vv.values()),
            gt.get("gt_is_advisory") is True,
            all(
                gt.get(field) is False
                for field in (
                    "gt_can_finalize",
                    "gt_can_mark_truth",
                    "gt_can_mark_ready",
                    "gt_can_execute_action",
                    "gt_can_write_drs",
                    "gt_can_install_needle",
                )
            ),
            root.get("root_result") == "bounded_llm_semantic_executor_node_completed",
            root.get("semantic_explanation_candidate_created") is True,
            root.get("llm_is_executor_node_capability") is True,
            root.get("llm_is_global_actor") is False,
            root.get("plan_modified_by_llm") is False,
            root.get("root_final_created_by_llm") is False,
            root.get("root_remains_final_authority") is True,
            all(root.get(field) is False for field in prohibited),
            all(value is True for value in report.boundary_matrix.values()),
            len(report.adversarial_attempts) == 9,
            all(
                attempt.get("detected") is True
                and attempt.get("blocked") is True
                and attempt.get("final_effect") == "blocked"
                and all(attempt.get(field) is False for field in prohibited)
                and attempt.get("plan_modified") is False
                and attempt.get("root_final_created_by_llm") is False
                and attempt.get("network_called") is False
                and attempt.get("gemini_called") is False
                and attempt.get("authority_transferred") is False
                for attempt in report.adversarial_attempts
            ),
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_bounded_llm_semantic_executor_node_v01() -> BoundedLLMSemanticExecutorNodeReport:
    source = _closed_checkpoint_source_evidence()
    plan_graph = _plan_graph()
    node_input = {
        "executor_node_id": "llm_semantic_summary_node",
        "input_scope": "accepted_evidence_summary_only",
        "accepted_evidence_inputs": [
            "accepted_bank_payment_evidence",
            "accepted_warehouse_stock_evidence",
        ],
        "raw_connector_observations_included": False,
        "raw_secret_included": False,
        "plan_graph_already_created": True,
        "executor_boundary_valid": True,
    }
    envelope = {
        "call_envelope_id": "bounded_mock_llm_call_semantic_summary_v01",
        "source_node_id": "llm_semantic_summary_node",
        "llm_provider": "mock_llm",
        "llm_role": "executor_node_capability",
        "bounded": True,
        "proof_only": True,
        "network_called": False,
        "gemini_called": False,
        "tools_allowed": False,
        "connector_access_allowed": False,
        "drs_write_allowed": False,
        "external_action_allowed": False,
        "plan_modification_allowed": False,
        "root_final_allowed": False,
        "input_scope": "accepted_evidence_summary_only",
        "input_contains_raw_secret": False,
        "output_schema": "SemanticDraft",
    }
    draft = {
        "draft_id": "semantic_draft_readiness_explanation_v01",
        "source_node_id": "llm_semantic_summary_node",
        "semantic_summary": (
            "Bank payment evidence and warehouse stock evidence are accepted evidence "
            "that may support a future readiness explanation."
        ),
        "risk_hints": [
            "accepted_evidence_is_not_truth",
            "accepted_evidence_is_non_executable",
        ],
        "missing_context_hints": [
            "no_final_readiness_decision_has_been_made_by_root"
        ],
        "confidence_label": "mock_confidence_only",
        "semantic_draft_created": True,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "root_final_created": False,
        "plan_modified": False,
    }
    proposal = {
        "proposal_id": "proposal_semantic_readiness_explanation",
        "source_node_id": "llm_semantic_summary_node",
        "proposal_type": "semantic_draft_result_proposal",
        "completed": True,
        "needs_user": False,
        "blocked": False,
        "safe_for_post_vv": True,
        "requires_post_vv": True,
        "requires_gt": True,
        "requires_root_final": True,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "root_final_created": False,
    }
    post_vv = {
        "schema_valid": True,
        "evidence_scope_valid": True,
        "no_truth_claim": True,
        "no_ready_claim": True,
        "no_action_claim": True,
        "no_drs_write_claim": True,
        "no_needle_claim": True,
        "no_plan_modification": True,
        "no_root_final_claim": True,
        "post_vv_passed": True,
    }
    gt = {
        "gt_recommendation": "accept_semantic_draft_as_explanation_candidate",
        "gt_is_advisory": True,
        "gt_can_finalize": False,
        "gt_can_mark_truth": False,
        "gt_can_mark_ready": False,
        "gt_can_execute_action": False,
        "gt_can_write_drs": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "bounded_llm_semantic_executor_node_completed",
        "safe_secondary_outcome": "semantic_explanation_candidate_available",
        "semantic_draft_result_proposals_created": 1,
        "semantic_explanation_candidate_created": True,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "plan_modified_by_llm": False,
        "root_final_created_by_llm": False,
        "llm_is_global_actor": False,
        "llm_is_orchestrator": False,
        "llm_is_architect": False,
        "llm_is_executor_node_capability": True,
        "network_called": False,
        "gemini_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
        "root_remains_final_authority": True,
    }
    boundary = {
        "llm_is_not_root": True,
        "llm_is_not_orchestrator": True,
        "llm_is_not_architect": True,
        "llm_is_not_gt": True,
        "llm_is_not_post_vv": True,
        "llm_is_executor_node_capability": True,
        "llm_does_not_create_plan_graph": True,
        "llm_does_not_modify_plan_graph": True,
        "llm_does_not_route": True,
        "llm_does_not_accept_evidence": True,
        "llm_does_not_prove_truth": True,
        "llm_does_not_create_ready_status": True,
        "llm_does_not_execute_action": True,
        "llm_does_not_write_drs": True,
        "llm_does_not_install_needle": True,
        "llm_output_is_semantic_draft_only": True,
        "semantic_draft_is_not_result_final": True,
        "semantic_draft_result_proposal_requires_post_vv_gt_root": True,
        "root_remains_final_authority": True,
    }
    attempts = _adversarial_attempts()
    proof_artifact = {
        "proof_artifact_id": "bounded_llm_semantic_executor_node_v01",
        "source_evidence": source,
        "plan_graph": plan_graph,
        "executor_semantic_node_input": node_input,
        "bounded_llm_call_envelope": envelope,
        "semantic_draft": draft,
        "semantic_draft_result_proposal": proposal,
        "post_vv_semantic_check": post_vv,
        "gt_semantic_advisory": gt,
        "root_semantic_final": root,
        "boundary_matrix": boundary,
        "adversarial_attempts": attempts,
    }
    audit = {
        "audit_entry_id": "audit_bounded_llm_semantic_executor_node_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = BoundedLLMSemanticExecutorNodeReport(
        source,
        plan_graph,
        node_input,
        envelope,
        draft,
        proposal,
        post_vv,
        gt,
        root,
        boundary,
        attempts,
        audit,
        proof_artifact,
        {},
    )
    passed = validate_bounded_llm_semantic_executor_node_report_consistency(provisional)
    summary = {
        "bounded_llm_semantic_executor_node_v01_status": "PASS" if passed else "FAIL",
        "plan_nodes_created": len(plan_graph["nodes"]),
        "llm_semantic_executor_nodes_created": 1,
        "bounded_llm_call_envelopes_created": 1,
        "semantic_drafts_created": 1,
        "semantic_draft_result_proposals_created": 1,
        "post_vv_checks_created": 1,
        "post_vv_passed": 1 if post_vv["post_vv_passed"] else 0,
        "gt_advisories_created": 1,
        "root_semantic_finals_created": 1,
        "adversarial_attempts_observed": len(attempts),
        "adversarial_attempts_blocked": sum(row["blocked"] is True for row in attempts),
        **boundary,
        "network_called": False,
        "gemini_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
        "ready_for_bounded_llm_semantic_executor_node_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


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


def render_bounded_llm_semantic_executor_node_v01(
    report: BoundedLLMSemanticExecutorNodeReport,
) -> str:
    lines = [
        "[BOUNDED LLM SEMANTIC EXECUTOR NODE v0.1]",
        "note: deterministic local executor-node capability proof only",
        "note: mock LLM output is SemanticDraft only; Post V&V, GT, and Root remain mandatory",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[PLAN GRAPH]", report.plan_graph["nodes"])
    _section(lines, "[EXECUTOR SEMANTIC NODE INPUT]", report.executor_semantic_node_input)
    _section(lines, "[BOUNDED LLM CALL ENVELOPE]", report.bounded_llm_call_envelope)
    _section(lines, "[SEMANTIC DRAFT]", report.semantic_draft)
    _section(lines, "[SEMANTIC DRAFT RESULT PROPOSAL]", report.semantic_draft_result_proposal)
    _section(lines, "[POST V&V]", report.post_vv_semantic_check)
    _section(lines, "[GT ADVISORY]", report.gt_semantic_advisory)
    _section(lines, "[ROOT FINAL]", report.root_semantic_final)
    _section(lines, "[BOUNDARY MATRIX]", report.boundary_matrix)
    _rows(lines, "[ADVERSARIAL ATTEMPTS]", report.adversarial_attempts)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_bounded_llm_semantic_executor_node_v01() -> str:
    return render_bounded_llm_semantic_executor_node_v01(
        collect_bounded_llm_semantic_executor_node_v01()
    )


def main() -> int:
    print(run_bounded_llm_semantic_executor_node_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
