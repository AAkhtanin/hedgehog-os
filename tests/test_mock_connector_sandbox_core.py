from __future__ import annotations

import inspect
import json

import pytest

from hedgehog.action_commit_packet import build_mock_action_commit_packet
from hedgehog.mock_connector_sandbox import MOCK_CONNECTOR_SANDBOX_ADAPTERS
from hedgehog.mock_connector_sandbox import MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS
from hedgehog.mock_connector_sandbox import MOCK_EXECUTION_EVIDENCE_REQUIRED_FIELDS
from hedgehog.mock_connector_sandbox import MOCK_RECEIPT_BASE_REQUIRED_FIELDS
from hedgehog.mock_connector_sandbox import build_mock_connector_execution_evidence
from hedgehog.mock_connector_sandbox import fake_bank_adapter_v0
from hedgehog.mock_connector_sandbox import fake_supplier_adapter_v0
from hedgehog.mock_connector_sandbox import fake_warehouse_adapter_v0
from hedgehog.mock_connector_sandbox import mock_connector_sandbox_context_default
from hedgehog.mock_connector_sandbox import mock_execution_validation_context_default
from hedgehog.mock_connector_sandbox import run_mock_connector_sandbox
from hedgehog.mock_connector_sandbox import validate_mock_connector_execution_evidence
from hedgehog.mock_connector_sandbox import validate_mock_connector_sandbox_packet
from hedgehog.mock_connector_sandbox import validate_mock_receipt


SCENARIO_TIME = "2026-06-22T12:00:00+00:00"


def _root_boundary() -> dict:
    return {
        "created_by": "root_boundary",
        "decision": "ready_for_mock_action",
        "root_reviewed": True,
        "reason": "Root approves mock-only action attempt packet creation",
        "blockers_checked": {
            "legal_hold_clear": True,
            "stock_available_or_mock_reservable": True,
            "post_vv_passed": True,
            "gt_lgt_reviewed": True,
        },
        "root_reviewed_semantic_outcome": {
            "outcome_id": "root_outcome:full_semantic_e2e_supplier_payment_v01",
        },
    }


def _post_vv_context() -> dict:
    return {
        "implementation": "hedgehog.post_vv.validate_result_proposals",
        "vv_report_count": 1,
        "finalizes": False,
    }


def _gt_lgt_context() -> dict:
    return {
        "implementation": "hedgehog.gt_validator.validate_gt",
        "gt_report_id": "gt_report:full_semantic_e2e_supplier_payment_v01",
        "decision": "accept",
        "finalizes": False,
    }


def _valid_packet() -> dict:
    return build_mock_action_commit_packet(
        root_boundary=_root_boundary(),
        post_vv_context=_post_vv_context(),
        gt_lgt_context=_gt_lgt_context(),
    )


def _adapter_context(packet: dict) -> dict:
    return {
        "business_subject": packet["business_subject"],
        "supplier_payment_context_summary": {
            "mock_ready_fixture": True,
            "legal_hold_present": False,
            "water_filter_shortage": False,
        },
    }


def _valid_receipts(packet: dict) -> tuple[dict, dict, dict]:
    context = _adapter_context(packet)
    return (
        fake_bank_adapter_v0(packet, SCENARIO_TIME, context),
        fake_supplier_adapter_v0(packet, SCENARIO_TIME, context),
        fake_warehouse_adapter_v0(packet, SCENARIO_TIME, context),
    )


def _packet_context() -> dict:
    return {
        "packet_created": True,
        "validation": {"accepted": True, "reasons": ()},
    }


def _supplier_context() -> dict:
    return {
        "mock_ready_fixture": True,
        "legal_hold_present": False,
        "water_filter_shortage": False,
    }


def test_default_contexts_are_inactive() -> None:
    sandbox_context = mock_connector_sandbox_context_default(
        scenario_time=SCENARIO_TIME,
    )
    validation_context = mock_execution_validation_context_default()

    assert sandbox_context["invoked"] is False
    assert sandbox_context["completed"] is False
    assert sandbox_context["denied"] is False
    assert sandbox_context["packet_validated"] is False
    assert sandbox_context["Root remains final authority"] is True
    assert validation_context["validated"] is False
    assert validation_context["accepted"] is False


def test_fake_adapter_receipt_shapes_are_mock_only() -> None:
    packet = _valid_packet()
    bank, supplier, warehouse = _valid_receipts(packet)

    assert bank["receipt_type"] == "mock_bank_payment_review_receipt"
    assert supplier["receipt_type"] == "mock_supplier_confirmation_receipt"
    assert warehouse["receipt_type"] == "mock_warehouse_reservation_receipt"
    for receipt in (bank, supplier, warehouse):
        assert set(MOCK_RECEIPT_BASE_REQUIRED_FIELDS).issubset(receipt)
        assert receipt["mock_only"] is True
        assert receipt["real_world_effects_allowed"] is False
    assert bank["bank_api_called"] is False
    assert bank["payment_executed"] is False
    assert supplier["supplier_api_called"] is False
    assert warehouse["warehouse_api_called"] is False
    assert warehouse["shipment_released"] is False


def test_valid_receipts_are_accepted() -> None:
    packet = _valid_packet()

    for receipt in _valid_receipts(packet):
        validation = validate_mock_receipt(receipt, packet, SCENARIO_TIME)
        assert validation["accepted"] is True
        assert validation["reasons"] == ()


@pytest.mark.parametrize(
    ("adapter_name", "field"),
    (
        ("fake_bank_adapter_v0", "bank_api_called"),
        ("fake_supplier_adapter_v0", "supplier_api_called"),
        ("fake_warehouse_adapter_v0", "inventory_reserved"),
    ),
)
def test_missing_false_or_exact_receipt_fields_are_rejected(
    adapter_name: str,
    field: str,
) -> None:
    packet = _valid_packet()
    receipt_by_adapter = {
        receipt["adapter_name"]: receipt for receipt in _valid_receipts(packet)
    }
    receipt = dict(receipt_by_adapter[adapter_name])
    receipt.pop(field)

    validation = validate_mock_receipt(receipt, packet, SCENARIO_TIME)

    assert validation["accepted"] is False
    assert (
        f"missing_required_receipt_field:{adapter_name}:{field}"
        in validation["reasons"]
    )


@pytest.mark.parametrize(
    ("adapter_name", "field", "reason"),
    (
        (
            "fake_bank_adapter_v0",
            "bank_api_called",
            "receipt_real_action_forbidden:bank_api_called",
        ),
        (
            "fake_bank_adapter_v0",
            "payment_executed",
            "receipt_real_action_forbidden:payment_executed",
        ),
        (
            "fake_warehouse_adapter_v0",
            "warehouse_api_called",
            "receipt_real_action_forbidden:warehouse_api_called",
        ),
        (
            "fake_warehouse_adapter_v0",
            "shipment_released",
            "receipt_real_action_forbidden:shipment_released",
        ),
    ),
)
def test_receipt_real_action_claims_are_rejected(
    adapter_name: str,
    field: str,
    reason: str,
) -> None:
    packet = _valid_packet()
    receipt_by_adapter = {
        receipt["adapter_name"]: receipt for receipt in _valid_receipts(packet)
    }
    receipt = dict(receipt_by_adapter[adapter_name])
    receipt[field] = True

    validation = validate_mock_receipt(receipt, packet, SCENARIO_TIME)

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


def test_valid_execution_evidence_is_accepted() -> None:
    packet = _valid_packet()
    receipts = _valid_receipts(packet)
    evidence = build_mock_connector_execution_evidence(
        packet,
        receipts,
        SCENARIO_TIME,
    )
    validation = validate_mock_connector_execution_evidence(
        evidence,
        packet,
        SCENARIO_TIME,
    )

    assert set(MOCK_EXECUTION_EVIDENCE_REQUIRED_FIELDS).issubset(evidence)
    assert validation["accepted"] is True
    assert evidence["receipt_count"] == 3
    assert evidence["adapter_names"] == MOCK_CONNECTOR_SANDBOX_ADAPTERS
    assert evidence["real_connector_called"] is False
    assert evidence["payment_executed"] is False
    assert evidence["shipment_released"] is False


def test_execution_evidence_missing_required_fields_is_rejected() -> None:
    packet = _valid_packet()
    evidence = build_mock_connector_execution_evidence(
        packet,
        _valid_receipts(packet),
        SCENARIO_TIME,
    )
    removed_fields = (
        "source_root_outcome_id",
        "business_subject",
        "connector_sandbox_completed",
        "root_final_authority_preserved",
    )
    for field in removed_fields:
        evidence.pop(field)

    validation = validate_mock_connector_execution_evidence(
        evidence,
        packet,
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    for field in removed_fields:
        assert (
            f"missing_required_execution_evidence_field:{field}"
            in validation["reasons"]
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("source_packet_id", "wrong_packet", "execution_evidence_source_packet_mismatch"),
        (
            "source_root_outcome_id",
            "root_outcome:wrong",
            "execution_evidence_source_root_outcome_mismatch",
        ),
        (
            "packet_expires_at",
            "2026-06-22T14:00:00+00:00",
            "execution_evidence_packet_expiry_mismatch",
        ),
        (
            "scenario_time",
            "2026-06-22T12:30:00+00:00",
            "execution_evidence_scenario_time_mismatch",
        ),
    ),
)
def test_execution_evidence_mismatches_are_rejected(
    field: str,
    value: str,
    reason: str,
) -> None:
    packet = _valid_packet()
    evidence = build_mock_connector_execution_evidence(
        packet,
        _valid_receipts(packet),
        SCENARIO_TIME,
    )
    evidence[field] = value

    validation = validate_mock_connector_execution_evidence(
        evidence,
        packet,
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert reason in validation["reasons"]


def test_expired_packet_is_rejected_before_adapters_run() -> None:
    packet = _valid_packet()
    packet["expires_at"] = "2026-06-22T11:59:59+00:00"
    calls: list[str] = []

    def counted_adapter(packet, scenario_time, context):
        calls.append("called")
        return fake_bank_adapter_v0(packet, scenario_time, context)

    packet_validation = validate_mock_connector_sandbox_packet(
        packet,
        _root_boundary(),
        SCENARIO_TIME,
    )
    result = run_mock_connector_sandbox(
        gate_enabled=True,
        root_boundary=_root_boundary(),
        action_commit_packet_context=_packet_context(),
        action_commit_packet=packet,
        supplier_context=_supplier_context(),
        scenario_time=SCENARIO_TIME,
        adapter_functions={
            "fake_bank_adapter_v0": counted_adapter,
            "fake_supplier_adapter_v0": counted_adapter,
            "fake_warehouse_adapter_v0": counted_adapter,
        },
    )

    assert packet_validation["accepted"] is False
    assert "packet_expired_at_scenario_time" in packet_validation["reasons"]
    assert result["fail_closed"] is True
    assert result["mock_connector_sandbox_context"]["counters"][
        "mock_connector_sandbox_packet_expired_count"
    ] == 1
    assert calls == []


@pytest.mark.parametrize("created_by", ("gemini", "orchestrator", "architect", "executor"))
def test_non_root_created_packet_is_rejected_before_adapters(created_by: str) -> None:
    packet = _valid_packet()
    packet["created_by"] = created_by

    validation = validate_mock_connector_sandbox_packet(
        packet,
        _root_boundary(),
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert "packet_must_be_root_created" in validation["reasons"]


def test_real_world_effects_allowed_packet_is_rejected_before_adapters() -> None:
    packet = _valid_packet()
    packet["real_world_effects_allowed"] = True

    validation = validate_mock_connector_sandbox_packet(
        packet,
        _root_boundary(),
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert "packet_real_world_effects_forbidden" in validation["reasons"]


def test_unknown_adapter_is_rejected_before_adapters() -> None:
    packet = _valid_packet()
    packet["allowed_future_adapters"] = (
        *packet["allowed_future_adapters"],
        "fake_unknown_adapter_v0",
    )

    validation = validate_mock_connector_sandbox_packet(
        packet,
        _root_boundary(),
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert "unknown_adapter" in validation["reasons"]


def test_missing_receipt_object_is_rejected() -> None:
    packet = _valid_packet()
    receipts = _valid_receipts(packet)[:2]
    evidence = build_mock_connector_execution_evidence(
        packet,
        receipts,
        SCENARIO_TIME,
    )

    validation = validate_mock_connector_execution_evidence(
        evidence,
        packet,
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert "missing_receipt" in validation["reasons"]


def test_duplicate_receipt_is_rejected() -> None:
    packet = _valid_packet()
    bank, _supplier, warehouse = _valid_receipts(packet)
    receipts = (bank, dict(bank), warehouse)
    evidence = build_mock_connector_execution_evidence(
        packet,
        receipts,
        SCENARIO_TIME,
    )

    validation = validate_mock_connector_execution_evidence(
        evidence,
        packet,
        SCENARIO_TIME,
    )

    assert validation["accepted"] is False
    assert "duplicate_receipt" in validation["reasons"]


def test_mock_connector_sandbox_core_has_no_network_or_sensitive_markers() -> None:
    import hedgehog.mock_connector_sandbox as sandbox

    source = inspect.getsource(sandbox)
    for forbidden in ("requests", "httpx", "urllib", "socket", "subprocess", "os.system"):
        assert forbidden not in source

    packet = _valid_packet()
    receipts = _valid_receipts(packet)
    evidence = build_mock_connector_execution_evidence(
        packet,
        receipts,
        SCENARIO_TIME,
    )
    artifacts = json.dumps(
        {
            "receipts": receipts,
            "execution_evidence": evidence,
        },
        sort_keys=True,
    ).lower()
    for forbidden in MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS:
        assert forbidden not in artifacts
