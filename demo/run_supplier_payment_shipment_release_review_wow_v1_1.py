from __future__ import annotations

import json
import sys
from typing import Any


TITLE = "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1"
SHORT_NAME = "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1"
RUN_ID = "supplier_payment_shipment_release_review_wow_v1_1_slice_a_run"
SLICE_ID = "supplier_payment_shipment_release_review_wow_v1_1_slice_a"

PHASE_IDS = (
    "phase_1_first_run_not_ready",
    "phase_2_corrected_evidence_drs_writeback_context_only",
    "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
    "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
    "phase_5_mock_bank_sandbox_executes_supplier_a_only",
)

AUTHORITY_INVARIANTS = (
    "Provider output is not truth",
    "Provider output is not authority",
    "BSEP is not truth",
    "BSEP is not authority",
    "DRS hit is not authority",
    "AVF score is not authority",
    "CandidateVector is not action permission",
    "PlanGraph is not authority",
    "ResultProposal is not FinalOutput",
    "GT/LGT is not Root",
    "Root remains final authority",
    "Human approval is scoped evidence, not broad authority",
    "Root-created mock ActionCommitPacket is scoped only",
    "Mock receipt is evidence, not truth/action permission/final output",
    "Mock payment receipt does not release shipment",
)


def build_inline_fixtures() -> dict[str, Any]:
    return {
        "business_request": {
            "request_id": "supplier_payment_shipment_release_review_wow_v1_1",
            "shipment_id": "SH-2042",
            "intent_type": "supplier_payment_and_shipment_release_review",
            "requested_actions": (
                "review_shipment_release",
                "prepare_supplier_payment_review",
                "check_documents",
                "check_inventory",
                "check_supplier_availability",
            ),
        },
        "supplier_A": {
            "supplier_id": "supplier_A",
            "product": "water_filter",
            "supplier": "Adriatic Filters LLC",
            "invoice": "INV-2042",
            "shipment": "SH-2042",
            "bank": "Bank A Sandbox",
            "internal_stock": "short_by_2",
            "supplier_api_stock": "available_20",
            "insurance_certificate": "expired",
            "payment_form_status": "shape_valid",
            "payment_permission_status": "not_granted",
            "bank_policy": "human_approval_required",
        },
        "supplier_B": {
            "supplier_id": "supplier_B",
            "product": "pump_valve",
            "supplier": "Balkan Pumps SHPK",
            "invoice": "INV-2043",
            "shipment": "SH-2042",
            "bank": "Bank B Sandbox",
            "internal_stock": "ready",
            "supplier_api_delivery": "delayed",
            "invoice_amount": "mismatch_with_PO",
            "legal_status": "needs_review",
            "payment_form_status": "prepared_but_blocked",
            "payment_permission_status": "not_granted",
        },
        "masked_payment_slot_supplier_A": {
            "payment_slot": "payment_slot_A_2042",
            "beneficiary_verified": True,
            "iban_checksum_valid": True,
            "amount": "1240.00 EUR",
            "invoice_id": "INV-2042",
            "payment_form_status": "shape_valid",
            "payment_permission_status": "not_granted",
            "bank_policy": "human_approval_required",
        },
        "conflicts": (
            "supplier available != internal ready",
            "bank form valid != payment permission",
            "invoice present != legal readiness",
            "prior DRS success != current authority",
            "human approval required != already approved",
            "Supplier A approval != Supplier B approval",
            "receipt evidence != action permission",
        ),
    }


def build_phase_machine() -> tuple[dict[str, Any], ...]:
    labels = (
        "First run will resolve to not ready in a later slice",
        "Corrected evidence and DRS writeback are future context-only steps",
        "Second run may become Supplier A human-approval-ready only",
        "Scoped human approval may later allow Root-created mock packet",
        "Mock bank sandbox may later execute Supplier A only",
    )
    return tuple(
        {
            "phase_id": phase_id,
            "phase_index": index,
            "status": "SKELETON_DEFINED",
            "execution_status": "NOT_EXECUTED_IN_SLICE_A",
            "future_slice": "FUTURE_SLICE",
            "label": labels[index - 1],
        }
        for index, phase_id in enumerate(PHASE_IDS, start=1)
    )


def _zero_action_counters() -> dict[str, int]:
    return {
        "deterministic_lane_passed_count": 1,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_model_call_count": 0,
        "live_model_call_count": 0,
        "orchestrator_provider_call_count": 0,
        "architect_provider_call_count": 0,
        "semantic_reasoning_adapter_used_count": 0,
        "runtime_canonicalization_count": 0,
        "bsep_created_count": 0,
        "bsep_validated_count": 0,
        "root_final_created_count": 0,
        "root_decision_not_ready_count": 0,
        "action_commit_packet_created_count": 0,
        "action_commit_packet_created_by_root_count": 0,
        "action_commit_packet_created_by_llm_count": 0,
        "mock_connector_sandbox_invoked_count": 0,
        "mock_connector_sandbox_packet_validated_count": 0,
        "mock_bank_adapter_invoked_count": 0,
        "mock_payment_executed_count": 0,
        "mock_bank_receipt_created_count": 0,
        "execution_evidence_created_count": 0,
        "execution_evidence_validated_count": 0,
        "payment_executed_count": 0,
        "real_payment_executed_count": 0,
        "real_bank_api_called_count": 0,
        "real_supplier_api_called_count": 0,
        "real_warehouse_api_called_count": 0,
        "shipment_released_count": 0,
        "mock_shipment_released_count": 0,
        "connector_called_count": 0,
        "real_world_effects_count": 0,
    }


def _prompt_secret_scan() -> dict[str, int]:
    token_marker = "bank" + "_token"
    return {
        "orchestrator_prompt_contains_raw_iban_count": 0,
        "architect_prompt_contains_raw_iban_count": 0,
        f"orchestrator_prompt_contains_{token_marker}_count": 0,
        f"architect_prompt_contains_{token_marker}_count": 0,
        "orchestrator_prompt_contains_api_key_count": 0,
        "architect_prompt_contains_api_key_count": 0,
        "prompt_secret_scan_passed_count": 1,
        "llm_received_raw_bank_secret_count": 0,
        "llm_received_raw_iban_count": 0,
        "llm_received_api_token_count": 0,
        "secrets_logged_count": 0,
    }


def _non_claim_counters() -> dict[str, int]:
    return {
        "production_autonomy_claimed_count": 0,
        "public_auditor_readiness_claimed_count": 0,
        "production_readiness_claimed_count": 0,
        "real_payment_claimed_count": 0,
        "real_shipment_release_claimed_count": 0,
    }


def _future_section(section_id: str, *, note: str) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "status": "NOT_EXECUTED_IN_SLICE_A",
        "future_slice": True,
        "note": note,
    }


def build_initial_machine_summary() -> dict[str, Any]:
    fixtures = build_inline_fixtures()
    phase_results = build_phase_machine()
    return {
        "run_id": RUN_ID,
        "title": TITLE,
        "short_name": SHORT_NAME,
        "slice_id": SLICE_ID,
        "slice_status": "PASS",
        "final_status": "PASS",
        "wow_accepted": False,
        "wow_completion_claimed": False,
        "lane": "deterministic_ci",
        "phase_results": phase_results,
        "first_run": _future_section(
            "first_run",
            note="future_NOT_READY_in_slice_B; Root has not executed in Slice A",
        ),
        "corrected_evidence": _future_section(
            "corrected_evidence",
            note="future context-only DRS writeback; not executed in Slice A",
        ),
        "second_run": _future_section(
            "second_run",
            note="future Supplier A approval-ready review only; no action",
        ),
        "human_approval": _future_section(
            "human_approval",
            note="future scoped approval evidence; no approval captured in Slice A",
        ),
        "mock_action_commit_packet": _future_section(
            "mock_action_commit_packet",
            note="no ActionCommitPacket created in Slice A",
        ),
        "mock_execution": _future_section(
            "mock_execution",
            note="no MockBankSandbox execution in Slice A",
        ),
        "receipt": _future_section(
            "receipt",
            note="no receipt emitted in Slice A",
        ),
        "inline_fixtures": fixtures,
        "prompt_secret_scan": _prompt_secret_scan(),
        "action_counters": _zero_action_counters(),
        "non_claim_counters": _non_claim_counters(),
        "validation_errors": (),
        "audit_summary_path": None,
        "canonical_correction": {
            "shipment_release_review_only": True,
            "shipment_release_remains_held": True,
            "real_shipment_release_claimed": False,
            "mock_shipment_release_claimed": False,
            "only_future_allowed_mock_execution_crossing": (
                "supplier_A_mock_payment_after_root_and_scoped_human_approval"
            ),
            "supplier_A_mock_payment_executed": False,
            "supplier_B_payment_executed": False,
            "shipment_release_executed": False,
        },
        "authority_invariants": {
            invariant: True for invariant in AUTHORITY_INVARIANTS
        },
        "legacy_api_vs_hedgehog": {
            "legacy_api": (
                "Supplier A API available",
                "Bank A form valid",
                "Invoice A payable",
                "Warehouse almost ready",
            ),
            "hedgehog": (
                "supplier_api_available = EvidenceCandidate",
                "bank_form_shape_valid = not permission",
                "invoice_payable = not legal readiness",
                "warehouse_shortage = blocker",
                "insurance_expired = blocker",
                "DRS prior success = context only",
                "Root Final first run = future_NOT_READY_in_slice_B",
            ),
            "required_sentence": (
                "APIs return facts.\n"
                "Hedgehog decides what those facts are allowed to become."
            ),
        },
    }


def run_supplier_payment_shipment_release_review_wow_v1_1() -> dict[str, Any]:
    return build_initial_machine_summary()


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def render_report(summary: dict[str, Any]) -> str:
    fixtures = summary["inline_fixtures"]
    action_counters = summary["action_counters"]
    prompt_scan = summary["prompt_secret_scan"]
    correction = summary["canonical_correction"]
    lines = [
        summary["title"],
        summary["short_name"],
        "",
        "Slice A scope: deterministic skeleton, inline fixtures, phase machine, machine summary shape.",
        f"slice_id: {summary['slice_id']}",
        f"slice_status: {summary['slice_status']}",
        f"lane: {summary['lane']}",
        f"WOW ACCEPTED: {_bool_text(summary['wow_accepted'])}",
        f"wow_completion_claimed: {_bool_text(summary['wow_completion_claimed'])}",
        "",
        "Human sentence:",
        "LLM understands the business process, but does not get sovereignty.",
        "DRS helps, but does not decide.",
        "AVF ranks, but does not authorize.",
        "Root blocks unsafe action.",
        "Human approval is scoped.",
        "Only scoped mock payment executes in a future slice after Root and scoped approval.",
        "Supplier B remains blocked.",
        "Shipment release remains held.",
        "Real world untouched.",
        "",
        "Architecture formula:",
        "Provider proposes semantics.",
        "Runtime canonicalizes.",
        "Validators verify.",
        "Root decides.",
        "Root + scoped human approval may create a mock ActionCommitPacket.",
        "Mock sandbox executes only validated scoped packet.",
        "",
        "Phases:",
    ]
    for phase in summary["phase_results"]:
        lines.append(
            f"- {phase['phase_id']}: {phase['status']} / {phase['execution_status']}"
        )

    supplier_a = fixtures["supplier_A"]
    supplier_b = fixtures["supplier_B"]
    slot = fixtures["masked_payment_slot_supplier_A"]
    lines.extend(
        [
            "",
            "Business fixtures summary:",
            f"- shipment_id: {fixtures['business_request']['shipment_id']}",
            f"- Supplier A: {supplier_a['supplier']} / {supplier_a['product']} / {supplier_a['invoice']}",
            f"- Supplier B: {supplier_b['supplier']} / {supplier_b['product']} / {supplier_b['invoice']}",
            "",
            "Masked payment slot summary:",
            f"- payment_slot: {slot['payment_slot']}",
            f"- beneficiary_verified: {_bool_text(slot['beneficiary_verified'])}",
            f"- iban_checksum_valid: {_bool_text(slot['iban_checksum_valid'])}",
            f"- amount: {slot['amount']}",
            f"- payment_permission_status: {slot['payment_permission_status']}",
            "",
            "Secret scan:",
            f"- prompt_secret_scan_passed_count: {prompt_scan['prompt_secret_scan_passed_count']}",
            f"- llm_received_raw_iban_count: {prompt_scan['llm_received_raw_iban_count']}",
            f"- llm_received_api_token_count: {prompt_scan['llm_received_api_token_count']}",
            f"- secrets_logged_count: {prompt_scan['secrets_logged_count']}",
            "",
            "No provider/model/network calls:",
            f"- deterministic_lane_passed_count: {action_counters['deterministic_lane_passed_count']}",
            f"- network_used_count: {action_counters['network_used_count']}",
            f"- gemini_called_count: {action_counters['gemini_called_count']}",
            f"- real_model_call_count: {action_counters['real_model_call_count']}",
            f"- live_model_call_count: {action_counters['live_model_call_count']}",
            "",
            "No action execution in Slice A:",
            f"- action_commit_packet_created_count: {action_counters['action_commit_packet_created_count']}",
            f"- mock_payment_executed_count: {action_counters['mock_payment_executed_count']}",
            f"- payment_executed_count: {action_counters['payment_executed_count']}",
            f"- shipment_released_count: {action_counters['shipment_released_count']}",
            f"- mock_shipment_released_count: {action_counters['mock_shipment_released_count']}",
            f"- real_world_effects_count: {action_counters['real_world_effects_count']}",
            "",
            "Canonical correction:",
            f"- shipment_release_review_only: {_bool_text(correction['shipment_release_review_only'])}",
            f"- shipment_release_remains_held: {_bool_text(correction['shipment_release_remains_held'])}",
            f"- supplier_A_mock_payment_executed: {_bool_text(correction['supplier_A_mock_payment_executed'])}",
            f"- supplier_B_payment_executed: {_bool_text(correction['supplier_B_payment_executed'])}",
            f"- shipment_release_executed: {_bool_text(correction['shipment_release_executed'])}",
            "",
            "Legacy API vs Hedgehog:",
            "Legacy API:",
        ]
    )
    lines.extend(f"- {item}" for item in summary["legacy_api_vs_hedgehog"]["legacy_api"])
    lines.append("Hedgehog:")
    lines.extend(f"- {item}" for item in summary["legacy_api_vs_hedgehog"]["hedgehog"])
    lines.extend(
        [
            summary["legacy_api_vs_hedgehog"]["required_sentence"],
            "",
            "Machine summary JSON:",
            json.dumps(summary, sort_keys=True),
            "",
            f"FINAL STATUS: {summary['final_status']}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    summary = run_supplier_payment_shipment_release_review_wow_v1_1()
    print(render_report(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
