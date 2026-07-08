from __future__ import annotations

import copy
from pathlib import Path

from demo import run_human_full_wow_v1_2_action_corridor_walkthrough as runner


REQUIRED_SECTIONS = (
    "[HEDGEHOG OS — FULL WOW V1.2 HUMAN ACTION CORRIDOR WALKTHROUGH]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[TIMELINE]",
    "[WHAT THE BUSINESS MODULES SAW]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF BLOCKED AND RANKED]",
    "[WHAT ROOT APPROVED]",
    "[ACTIONCOMMITPACKET BOUNDARY]",
    "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
    "[MOCK RECEIPT BOUNDARY]",
    "[SUPPLIER B AND SHIPMENT SAFETY]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

REQUIRED_COUNTER_VALUES = {
    "local_drs_v0_2_records_evaluated_count": 11,
    "local_drs_v0_2_direct_reuse_allowed_count": 0,
    "avf_v0_2_candidates_evaluated_count": 9,
    "avf_v0_2_action_permission_granted_count": 0,
    "action_commit_packet_v0_2_root_created_model_packet_count": 1,
    "action_commit_packet_v0_2_created_by_root_count": 1,
    "action_commit_packet_v0_2_created_by_llm_count": 0,
    "action_commit_packet_v0_2_created_by_drs_count": 0,
    "action_commit_packet_v0_2_created_by_avf_count": 0,
    "action_commit_packet_v0_2_created_by_gt_lgt_count": 0,
    "mock_bank_sandbox_v0_2_mock_payment_intent_created_count": 1,
    "mock_bank_sandbox_v0_2_mock_payment_consent_created_count": 1,
    "mock_bank_sandbox_v0_2_mock_payment_order_created_count": 1,
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count": 1,
    "mock_bank_sandbox_v0_2_receipt_permission_created_count": 0,
    "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count": 0,
    "mock_bank_sandbox_v0_2_receipt_shipment_release_count": 0,
    "mock_bank_sandbox_v0_2_real_payment_executed_count": 0,
    "mock_bank_sandbox_v0_2_shipment_released_count": 0,
    "real_world_effects_count": 0,
}


def _report() -> dict:
    return runner.collect_human_full_wow_v1_2_action_corridor_walkthrough()


def _rendered() -> str:
    return runner.render_human_full_wow_v1_2_action_corridor_walkthrough(_report())


def test_human_action_corridor_walkthrough_renders_required_sections() -> None:
    report = _report()
    rendered = runner.render_human_full_wow_v1_2_action_corridor_walkthrough(
        report
    )

    assert report["final_status"] == "PASS"
    for section in REQUIRED_SECTIONS:
        assert section in rendered


def test_human_action_corridor_walkthrough_one_screen_summary() -> None:
    rendered = _rendered()

    assert "DRS remembered prior traces but did not decide" in rendered
    assert "AVF hard-masked unsafe routes" in rendered
    assert "Root created one scoped Supplier A ActionCommitPacket model" in rendered
    assert "MockBankSandbox consumed only that scoped Supplier A packet" in rendered
    assert "Receipt is evidence only" in rendered
    assert "Supplier B remained blocked" in rendered
    assert "Shipment remained held" in rendered
    assert "No real bank, real payment, real shipment release, or real-world effect happened" in rendered
    assert "Root remained final authority" in rendered


def test_human_action_corridor_walkthrough_drs_and_avf_story() -> None:
    rendered = _rendered()

    assert "DRS is memory/context only" in rendered
    assert "DRS direct reuse allowed count remains 0" in rendered
    assert "DRS root review required count remains 11" in rendered
    assert "DRS is not truth, authority, permission, or FinalOutput" in rendered
    assert "release_all_and_pay_all was hard-masked" in rendered
    assert "Supplier B payment was hard-masked" in rendered
    assert "Safe candidates may rank but do not grant permission" in rendered
    assert "Top-ranked candidate is not permission" in rendered
    assert "AVF score is not authority" in rendered
    assert "HardMask is not Root" in rendered


def test_human_action_corridor_walkthrough_root_packet_story() -> None:
    rendered = _rendered()

    assert "Root created one scoped Supplier A ActionCommitPacket v0.2 model" in rendered
    assert "Human approval is scoped evidence only" in rendered
    assert "LLM/DRS/AVF/GT-LGT did not create the packet" in rendered
    assert "Supplier A allowed" in rendered
    assert "Supplier B forbidden" in rendered
    assert "Shipment release forbidden" in rendered
    assert "Real bank/supplier/warehouse APIs forbidden" in rendered
    assert "Registry is local proof-only, not authority, not permission" in rendered


def test_human_action_corridor_walkthrough_mockbank_story() -> None:
    rendered = _rendered()

    assert "scope, adapter, expiry, idempotency, amount, creditor, payment slot" in rendered
    assert "mock payment intent, mock consent, and mock payment order" in rendered
    assert "mock receipt evidence" in rendered
    assert "Terminal receipt observation was stored only in local proof-only registry" in rendered
    assert "The corridor is deterministic, not reasoning" in rendered
    assert "No post-Root reasoning restarted" in rendered


def test_human_action_corridor_walkthrough_receipt_boundary() -> None:
    rendered = _rendered()

    assert "Receipt is evidence only" in rendered
    assert "Receipt did not create permission" in rendered
    assert "Receipt did not create future permission" in rendered
    assert "Receipt did not create FinalOutput" in rendered
    assert "Receipt did not authorize Supplier B" in rendered
    assert "Receipt did not release shipment" in rendered
    assert "Receipt did not mutate packet scope" in rendered
    assert "Receipt did not create production DRS record" in rendered


def test_human_action_corridor_walkthrough_counter_table() -> None:
    report = _report()
    rendered = runner.render_human_full_wow_v1_2_action_corridor_walkthrough(
        report
    )

    for key, value in REQUIRED_COUNTER_VALUES.items():
        assert report["counter_table"][key] == value
        assert f"{key}: {value}" in rendered


def test_human_action_corridor_walkthrough_fails_closed_on_effect_counter() -> None:
    source = copy.deepcopy(
        runner.product_trace.collect_full_wow_v1_2_product_trace()
    )
    source["real_world_effects_count"] = 4

    report = runner.collect_human_full_wow_v1_2_action_corridor_walkthrough(
        source_report=source
    )

    assert report["final_status"] == "FAIL_CLOSED"
    assert "real_world_effects_zero" in report["validation_errors"]


def test_human_action_corridor_walkthrough_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")
    forbidden_phrases = (
        "authority " + "flows upward",
        "adapter " + "returns authority",
        "receipt " + "returns authority",
        "bank " + "returns authority",
        "corridor " + "decides",
        "adapter " + "decides",
        "post-Root " + "reasoning restarts",
        "receipt " + "grants permission",
        "receipt " + "releases shipment",
        "human approval " + "directly creates ActionCommitPacket",
    )

    assert "from demo import run_full_wow_v1_2_product_trace as product_trace" in source
    assert "hedgehog.mock_connector_sandbox" not in source
    assert "from hedgehog.action_commit_packet import" not in source
    assert "import hedgehog.action_commit_packet\n" not in source
    assert "google.genai" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "openai" not in source
    assert "subprocess" not in source
    for phrase in forbidden_phrases:
        assert phrase not in source
