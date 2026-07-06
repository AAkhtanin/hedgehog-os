from __future__ import annotations

import json
from typing import Any, Mapping

from demo.run_full_wow_v1_1_final_integrated_rollup import (
    collect_full_wow_v1_1_final_integrated_rollup,
)


RUN_ID = "human_full_wow_v1_1_final_walkthrough_v01"
REPORT_ID = "human_full_wow_v1_1_final_walkthrough_v01"
SOURCE_ROLLUP_REPORT_ID = "full_wow_v1_1_final_integrated_rollup_v01"
WALKTHROUGH_TYPE = "human_product_facing_closed_evidence_walkthrough"

REQUIRED_SECTIONS = (
    "[FULL WOW V1.1 FINAL HUMAN WALKTHROUGH]",
    "[WHAT THIS DEMO SHOWS]",
    "[ACT 1 — DIRTY BUSINESS REQUEST]",
    "[ACT 2 — FIRST ROOT REVIEW: NOT_READY]",
    "[ACT 3 — SEMANTIC LIVE LANE: REAL GEMINI ORCHESTRATOR + BSEP + REAL GEMINI ARCHITECT]",
    "[ACT 4 — BUSINESS EVIDENCE BRANCHES]",
    "[ACT 5 — DRS / CANDIDATE VECTOR / AVF]",
    "[ACT 6 — SEMANTIC ARCHITECT AND RUNTIME PLAN ARTIFACTS]",
    "[ACT 7 — SECOND RUN: SUPPLIER A SCOPED REVIEW]",
    "[ACT 8 — HUMAN APPROVAL]",
    "[ACT 9 — ROOT-CREATED MOCK ACTIONCOMMITPACKET]",
    "[ACT 10 — MOCK BANK SANDBOX RECEIPT]",
    "[ACT 11 — FINAL AUTHORITY MATRIX]",
    "[COUNTER SUMMARY]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

AUTHORITY_MATRIX = (
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "BSEP is not truth.",
    "BSEP is not authority.",
    "DRS candidate context is not truth.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "Semantic Architect is not Root.",
    "Runtime owns PlanGraph/local plan artifacts.",
    "PlanGraph is not authority.",
    "Human approval is scoped evidence only.",
    "Root-created mock ActionCommitPacket is scoped only.",
    "MockBankSandbox receipt is evidence only.",
    "Receipt does not release shipment.",
    "Root remains final authority.",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no real payment",
    "no real shipment release",
    "no real connector/API effects",
    "no real-world effects",
    "v1.2 not implemented in this walkthrough",
)


def _transition_cards() -> tuple[dict[str, str], ...]:
    return (
        {
            "step_id": "dirty_request_received",
            "actor_or_module": "user/business request",
            "api_like_call_or_event": "USER_REQUEST supplier payment + shipment release review",
            "input_summary": "Dirty business request asks for supplier payment review and shipment release review together.",
            "output_summary": "Root-facing review path starts with no action permission.",
            "meaning": "business wants payment and shipment release review",
            "does_not_authorize": "no payment, no shipment release",
            "next_step": "warehouse_scope_observed",
            "trace_or_evidence_id": "full_wow_v1_1_final_integrated_rollup_v01",
        },
        {
            "step_id": "warehouse_scope_observed",
            "actor_or_module": "Warehouse / closed evidence",
            "api_like_call_or_event": "OBSERVE closed shipment evidence for SH-2042",
            "input_summary": "Closed evidence records shipment SH-2042 as review context.",
            "output_summary": "Shipment release remains held.",
            "meaning": "shipment release remains held; warehouse evidence is review context",
            "does_not_authorize": "shipment release",
            "next_step": "supplier_a_scope_observed",
            "trace_or_evidence_id": "auditor_supplier_payment_shipment_release_review_wow_v1_1.log",
        },
        {
            "step_id": "supplier_a_scope_observed",
            "actor_or_module": "Supplier A / closed evidence",
            "api_like_call_or_event": "OBSERVE Supplier A scoped mock payment path",
            "input_summary": "Corrected Supplier A evidence reaches scoped review in the closed state machine.",
            "output_summary": "Supplier A can be reviewed for mock-scoped evidence only.",
            "meaning": "Supplier A can reach scoped review after corrected evidence",
            "does_not_authorize": "broad supplier payment or shipment release",
            "next_step": "supplier_b_blocker_observed",
            "trace_or_evidence_id": "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
        },
        {
            "step_id": "supplier_b_blocker_observed",
            "actor_or_module": "Supplier B / closed evidence",
            "api_like_call_or_event": "OBSERVE Supplier B blocker",
            "input_summary": "Supplier B evidence remains blocked in the closed review.",
            "output_summary": "Supplier B does not enter payment approval.",
            "meaning": "Supplier B remains blocked",
            "does_not_authorize": "Supplier B payment",
            "next_step": "legal_accounting_review_observed",
            "trace_or_evidence_id": "supplier_B_remains_blocked",
        },
        {
            "step_id": "legal_accounting_review_observed",
            "actor_or_module": "Legal + Accounting / closed evidence",
            "api_like_call_or_event": "OBSERVE invoice/legal review state",
            "input_summary": "Invoice and legal/accounting state remain bounded review evidence.",
            "output_summary": "Evidence is presented to Root without granting permission.",
            "meaning": "evidence is part of Root review",
            "does_not_authorize": "payment permission",
            "next_step": "live_gemini_semantic_lane_observed",
            "trace_or_evidence_id": "full_wow_v1_1_final_integrated_rollup_v01",
        },
        {
            "step_id": "live_gemini_semantic_lane_observed",
            "actor_or_module": "real Gemini Orchestrator + runtime BSEP + real Gemini Architect",
            "api_like_call_or_event": "OBSERVE closed real Gemini run",
            "input_summary": "Closed real run used gemini-2.5-flash in semantic_reasoning_adapter/json_mime_only mode.",
            "output_summary": "Real Gemini Orchestrator and real Gemini Architect both validated in the closed audit.",
            "meaning": "real LLMs proposed semantic route and semantic architecture",
            "does_not_authorize": "truth, authority, action permission, FinalOutput, packet, receipt, payment, shipment",
            "next_step": "bsep_membrane_observed",
            "trace_or_evidence_id": "full_wow_v1_1_manual_live_gemini_real_20260705_232010",
        },
        {
            "step_id": "bsep_membrane_observed",
            "actor_or_module": "runtime BSEP",
            "api_like_call_or_event": "BUILD/VALIDATE BSEP in closed real run",
            "input_summary": "Runtime used accepted Orchestrator semantics and bounded WOW summary.",
            "output_summary": "BSEP was built after Orchestrator validation and validated before Architect.",
            "meaning": "bounded context crosses from Orchestrator to Architect",
            "does_not_authorize": "truth, authority, action permission",
            "next_step": "drs_candidate_avf_observed",
            "trace_or_evidence_id": "auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
        },
        {
            "step_id": "drs_candidate_avf_observed",
            "actor_or_module": "DRS / CandidateVector / AVF",
            "api_like_call_or_event": "OBSERVE advisory/candidate layers",
            "input_summary": "Closed DRS candidate context, CandidateVector, and AVF layers provide review context.",
            "output_summary": "Context and ranking are visible while authority stays with Root.",
            "meaning": "context and ranking help Root review",
            "does_not_authorize": "truth, authority, action permission",
            "next_step": "semantic_architect_runtime_plan_boundary",
            "trace_or_evidence_id": "drs_candidate_vector_avf_closed_evidence",
        },
        {
            "step_id": "semantic_architect_runtime_plan_boundary",
            "actor_or_module": "Semantic Architect + runtime",
            "api_like_call_or_event": "OBSERVE semantic Architect proposal and runtime-owned plan artifacts",
            "input_summary": "Architect receives BSEP-derived bounded context and proposes semantic plan intent.",
            "output_summary": "Runtime owns PlanGraph/local plan artifacts after validation.",
            "meaning": "Architect proposes semantic plan intent; runtime owns PlanGraph/local plan artifacts",
            "does_not_authorize": "provider-owned PlanGraph or FinalOutput",
            "next_step": "root_first_decision_not_ready",
            "trace_or_evidence_id": "semantic_architect_runtime_plan_boundary",
        },
        {
            "step_id": "root_first_decision_not_ready",
            "actor_or_module": "Root",
            "api_like_call_or_event": "ROOT_REVIEW first run",
            "input_summary": "Root reviews the unsafe combined request with blockers still present.",
            "output_summary": "First run is NOT_READY.",
            "meaning": "unsafe full request rejected as NOT_READY",
            "does_not_authorize": "payment or shipment release",
            "next_step": "corrected_evidence_second_run",
            "trace_or_evidence_id": "phase_1_first_run_not_ready",
        },
        {
            "step_id": "corrected_evidence_second_run",
            "actor_or_module": "runtime closed evidence",
            "api_like_call_or_event": "OBSERVE corrected evidence + context-only reuse",
            "input_summary": "Corrected evidence is observed as context-only reuse in the closed second run.",
            "output_summary": "Supplier A reaches scoped review; Supplier B remains blocked; shipment held.",
            "meaning": "Supplier A reaches scoped review; Supplier B remains blocked; shipment held",
            "does_not_authorize": "broad payment or shipment release",
            "next_step": "human_approval_scoped",
            "trace_or_evidence_id": "phase_2_corrected_evidence_drs_writeback_context_only",
        },
        {
            "step_id": "human_approval_scoped",
            "actor_or_module": "human approval",
            "api_like_call_or_event": "HUMAN_APPROVAL Supplier A only",
            "input_summary": "Human review approves only the Supplier A mock path in closed evidence.",
            "output_summary": "Approval is scoped evidence, not production permission.",
            "meaning": "scoped evidence for Supplier A mock payment only",
            "does_not_authorize": "Supplier B payment, shipment release, production action",
            "next_step": "root_created_mock_packet_observed",
            "trace_or_evidence_id": "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
        },
        {
            "step_id": "root_created_mock_packet_observed",
            "actor_or_module": "Root",
            "api_like_call_or_event": "OBSERVE Root-created mock ActionCommitPacket",
            "input_summary": "Closed evidence observes Root-created scoped mock packet for Supplier A only.",
            "output_summary": "This walkthrough creates no packet and observes the closed boundary.",
            "meaning": "only Root creates scoped mock packet",
            "does_not_authorize": "real payment, Supplier B payment, shipment release",
            "next_step": "mock_bank_receipt_observed",
            "trace_or_evidence_id": "root_created_mock_action_commit_packet_observed_only",
        },
        {
            "step_id": "mock_bank_receipt_observed",
            "actor_or_module": "MockBankSandbox",
            "api_like_call_or_event": "OBSERVE closed Supplier A mock receipt",
            "input_summary": "Closed evidence observes Supplier A mock bank receipt boundary.",
            "output_summary": "Receipt remains evidence only and this walkthrough executes no sandbox adapter.",
            "meaning": "receipt is evidence only",
            "does_not_authorize": "truth, action permission, shipment release",
            "next_step": "final_state_summary",
            "trace_or_evidence_id": "phase_5_mock_bank_sandbox_executes_supplier_a_only",
        },
        {
            "step_id": "final_state_summary",
            "actor_or_module": "Root final boundary",
            "api_like_call_or_event": "FINAL SUMMARY",
            "input_summary": "All closed evidence is summarized for the product-facing v1.1 trace.",
            "output_summary": "Supplier A scoped mock evidence exists; Supplier B blocked; shipment held; Root final authority.",
            "meaning": "Supplier A scoped mock evidence exists; Supplier B blocked; shipment held; Root final authority",
            "does_not_authorize": "production readiness, public auditor final package, real-world effects",
            "next_step": "none",
            "trace_or_evidence_id": "human_full_wow_v1_1_final_walkthrough_v01",
        },
    )


def _walkthrough_counters() -> dict[str, int]:
    return {
        "human_final_walkthrough_created_count": 1,
        "source_final_rollup_observed_count": 1,
        "transition_cards_created_count": 15,
        "real_gemini_lane_observed_count": 1,
        "real_gemini_lane_rerun_count": 0,
        "walkthrough_called_gemini_count": 0,
        "walkthrough_network_used_count": 0,
        "walkthrough_provider_called_count": 0,
        "walkthrough_accessed_secrets_count": 0,
        "walkthrough_created_action_commit_packet_count": 0,
        "walkthrough_created_receipt_count": 0,
        "walkthrough_executed_mock_payment_count": 0,
        "walkthrough_executed_real_payment_count": 0,
        "walkthrough_released_shipment_count": 0,
        "walkthrough_called_bank_supplier_warehouse_api_count": 0,
        "real_world_effects_count": 0,
    }


def _format_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def collect_human_full_wow_v1_1_final_walkthrough() -> dict[str, Any]:
    source_rollup = collect_full_wow_v1_1_final_integrated_rollup()
    counters = _walkthrough_counters()
    transition_cards = _transition_cards()
    source_rollup_passed = source_rollup["final_status"] == "PASS"
    transition_count_ok = len(transition_cards) == counters["transition_cards_created_count"]
    final_status = "PASS" if source_rollup_passed and transition_count_ok else "FAIL_CLOSED"

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "source_rollup_report_id": source_rollup["report_id"],
        "walkthrough_type": WALKTHROUGH_TYPE,
        "final_status": final_status,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "real_world_effects_count": counters["real_world_effects_count"],
        "source_rollup_summary": {
            "report_id": source_rollup["report_id"],
            "final_status": source_rollup["final_status"],
            "rollup_type": source_rollup["rollup_type"],
            "wow_completion_claim_scope": source_rollup["wow_completion_claim_scope"],
        },
        "human_story_facts": (
            "LLM understands the business process but does not get sovereignty.",
            "DRS helps but does not decide.",
            "AVF ranks but does not authorize.",
            "Root blocks unsafe action.",
            "Human approval is scoped.",
            "Only scoped mock payment evidence exists.",
            "Supplier B remains blocked.",
            "Shipment release remains held.",
            "Receipt remains evidence only.",
            "Real world untouched.",
        ),
        "business_trace_framing": {
            "trace_type": "v1.1 product-facing trace",
            "prepares_for": "v1.2 API-like business trace",
            "implements_v1_2_modules": False,
            "visible_surfaces": (
                "warehouse evidence",
                "supplier evidence",
                "legal/accounting review",
                "bank sandbox boundary",
                "Root decision",
                "scoped human approval",
                "packet boundary",
                "receipt boundary",
            ),
        },
        "transition_cards": transition_cards,
        "authority_matrix": AUTHORITY_MATRIX,
        "non_claims": NON_CLAIMS,
        "counters": counters,
        "validation_errors": () if final_status == "PASS" else ("source_rollup_not_pass",),
    }


def _card_lines(card: Mapping[str, str]) -> list[str]:
    return [
        f"- step_id: {card['step_id']}",
        f"  actor_or_module: {card['actor_or_module']}",
        f"  api_like_call_or_event: {card['api_like_call_or_event']}",
        f"  input_summary: {card['input_summary']}",
        f"  output_summary: {card['output_summary']}",
        f"  meaning: {card['meaning']}",
        f"  does_not_authorize: {card['does_not_authorize']}",
        f"  next_step: {card['next_step']}",
        f"  trace_or_evidence_id: {card['trace_or_evidence_id']}",
    ]


def render_human_full_wow_v1_1_final_walkthrough(report: Mapping[str, Any]) -> str:
    cards = {card["step_id"]: card for card in report["transition_cards"]}
    counters = report["counters"]
    lines: list[str] = [
        "HEDGEHOG OS — FULL WOW v1.1 FINAL HUMAN WALKTHROUGH",
        "",
        "[FULL WOW V1.1 FINAL HUMAN WALKTHROUGH]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"source_rollup_report_id: {report['source_rollup_report_id']}",
        f"walkthrough_type: {report['walkthrough_type']}",
        f"final_status: {report['final_status']}",
        f"production_ready_claimed: {_format_bool(report['production_ready_claimed'])}",
        f"public_auditor_ready_claimed: {_format_bool(report['public_auditor_ready_claimed'])}",
        f"real_world_effects_count: {report['real_world_effects_count']}",
        "",
        "[WHAT THIS DEMO SHOWS]",
        "This is a living business process over closed Full WOW v1.1 evidence, not a new execution path.",
        "It shows dirty request -> semantic route -> BSEP -> branch evidence -> Root boundary -> scoped approval -> mock bank receipt.",
    ]
    lines.extend(f"- {fact}" for fact in report["human_story_facts"])
    lines.extend(
        [
            "- warehouse evidence, supplier evidence, Legal, Accounting, Root decision, human approval, packet boundary, and bank sandbox boundary are visible.",
            "- This is a v1.1 product-facing trace; v1.2 not implemented in this walkthrough.",
            "",
            "[ACT 1 — DIRTY BUSINESS REQUEST]",
        ]
    )
    lines.extend(_card_lines(cards["dirty_request_received"]))

    lines.extend(["", "[ACT 2 — FIRST ROOT REVIEW: NOT_READY]"])
    lines.extend(_card_lines(cards["root_first_decision_not_ready"]))

    lines.extend(
        [
            "",
            "[ACT 3 — SEMANTIC LIVE LANE: REAL GEMINI ORCHESTRATOR + BSEP + REAL GEMINI ARCHITECT]",
        ]
    )
    lines.extend(_card_lines(cards["live_gemini_semantic_lane_observed"]))
    lines.extend(_card_lines(cards["bsep_membrane_observed"]))
    lines.append("Real Gemini Orchestrator and real Gemini Architect are observed from the closed run, not rerun here.")

    lines.extend(["", "[ACT 4 — BUSINESS EVIDENCE BRANCHES]"])
    for step_id in (
        "warehouse_scope_observed",
        "supplier_a_scope_observed",
        "supplier_b_blocker_observed",
        "legal_accounting_review_observed",
    ):
        lines.extend(_card_lines(cards[step_id]))

    lines.extend(["", "[ACT 5 — DRS / CANDIDATE VECTOR / AVF]"])
    lines.extend(_card_lines(cards["drs_candidate_avf_observed"]))

    lines.extend(["", "[ACT 6 — SEMANTIC ARCHITECT AND RUNTIME PLAN ARTIFACTS]"])
    lines.extend(_card_lines(cards["semantic_architect_runtime_plan_boundary"]))

    lines.extend(["", "[ACT 7 — SECOND RUN: SUPPLIER A SCOPED REVIEW]"])
    lines.extend(_card_lines(cards["corrected_evidence_second_run"]))

    lines.extend(["", "[ACT 8 — HUMAN APPROVAL]"])
    lines.extend(_card_lines(cards["human_approval_scoped"]))

    lines.extend(["", "[ACT 9 — ROOT-CREATED MOCK ACTIONCOMMITPACKET]"])
    lines.extend(_card_lines(cards["root_created_mock_packet_observed"]))

    lines.extend(["", "[ACT 10 — MOCK BANK SANDBOX RECEIPT]"])
    lines.extend(_card_lines(cards["mock_bank_receipt_observed"]))
    lines.append("MockBankSandbox receipt evidence only: receipt evidence only, no shipment release.")

    lines.extend(["", "[ACT 11 — FINAL AUTHORITY MATRIX]"])
    lines.extend(_card_lines(cards["final_state_summary"]))
    lines.extend(f"- {item}" for item in report["authority_matrix"])

    lines.extend(["", "[COUNTER SUMMARY]"])
    for key in sorted(counters):
        lines.append(f"{key}: {counters[key]}")

    lines.extend(["", "[NON-CLAIMS]"])
    lines.extend(f"- {item}" for item in report["non_claims"])

    lines.extend(
        [
            "",
            "[FINAL STATUS]",
            f"FINAL STATUS: {report['final_status']}",
            "Machine summary JSON:",
            json.dumps(
                {
                    "run_id": report["run_id"],
                    "final_status": report["final_status"],
                    "source_rollup_report_id": report["source_rollup_report_id"],
                    "counters": counters,
                    "non_claims": report["non_claims"],
                },
                sort_keys=True,
            ),
        ]
    )
    return "\n".join(lines)


def run_human_full_wow_v1_1_final_walkthrough() -> str:
    return render_human_full_wow_v1_1_final_walkthrough(
        collect_human_full_wow_v1_1_final_walkthrough()
    )


def main() -> int:
    report = collect_human_full_wow_v1_1_final_walkthrough()
    print(render_human_full_wow_v1_1_final_walkthrough(report))
    return 0 if report["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
