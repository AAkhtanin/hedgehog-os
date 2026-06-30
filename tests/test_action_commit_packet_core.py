from __future__ import annotations

import pytest

from hedgehog.action_commit_packet import (
    ACTION_COMMIT_PACKET_ALLOWED_ACTION_KINDS,
)
from hedgehog.action_commit_packet import (
    ACTION_COMMIT_PACKET_FORBIDDEN_FIELDS,
)
from hedgehog.action_commit_packet import (
    ACTION_COMMIT_PACKET_REQUIRED_FAKE_ADAPTERS,
)
from hedgehog.action_commit_packet import (
    ACTION_COMMIT_PACKET_REQUIRED_FORBIDDEN_REAL_ADAPTERS,
)
from hedgehog.action_commit_packet import action_commit_packet_default
from hedgehog.action_commit_packet import build_mock_action_commit_packet
from hedgehog.action_commit_packet import root_mock_approval_context_default
from hedgehog.action_commit_packet import validate_action_commit_packet
from hedgehog.action_commit_packet import validate_root_mock_approval_preconditions


def _root_boundary(
    decision: str = "ready_for_mock_action",
    outcome_id: str = "root_outcome:full_semantic_e2e_supplier_payment_v01",
) -> dict:
    return {
        "created_by": "root_boundary",
        "decision": decision,
        "root_reviewed": True,
        "reason": "Root approves mock-only action attempt packet creation",
        "blockers_checked": {
            "legal_hold_clear": decision == "ready_for_mock_action",
            "stock_available_or_mock_reservable": decision == "ready_for_mock_action",
            "post_vv_passed": True,
            "gt_lgt_reviewed": True,
        },
        "root_reviewed_semantic_outcome": {
            "outcome_id": outcome_id,
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


def test_default_contexts_are_inactive() -> None:
    packet_context = action_commit_packet_default()
    approval_context = root_mock_approval_context_default()

    assert packet_context["packet_created"] is False
    assert packet_context["connector_executed"] is False
    assert packet_context["mock_receipt_created"] is False
    assert packet_context["execution_evidence_created"] is False
    assert approval_context["invoked"] is False
    assert approval_context["approval_granted"] is False
    assert approval_context["approval_denied"] is False
    assert approval_context["Root remains final authority"] is True


def test_valid_mock_action_commit_packet_is_accepted() -> None:
    packet = _valid_packet()
    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert packet["packet_type"] == "mock_action_commit_packet"
    assert packet["created_by"] == "root_mock_approval_gate"
    assert packet["mock_only"] is True
    assert packet["real_world_effects_allowed"] is False
    assert packet["action_scope"] == "local_mock_connector_sandbox"
    assert set(ACTION_COMMIT_PACKET_REQUIRED_FAKE_ADAPTERS).issubset(
        set(packet["allowed_future_adapters"])
    )
    assert set(ACTION_COMMIT_PACKET_REQUIRED_FORBIDDEN_REAL_ADAPTERS).issubset(
        set(packet["forbidden_real_adapters"])
    )
    assert set(ACTION_COMMIT_PACKET_ALLOWED_ACTION_KINDS) == set(
        packet["allowed_action_kinds"]
    )
    assert {"post_vv", "gt_lgt", "root"}.issubset(packet["validator_receipts"])
    assert validation["accepted"] is True
    assert validation["reasons"] == ()


def test_build_packet_identity_is_derived_from_root_outcome_id() -> None:
    root_boundary = _root_boundary(outcome_id="root_outcome:custom_core_identity_v01")
    packet = build_mock_action_commit_packet(
        root_boundary=root_boundary,
        post_vv_context=_post_vv_context(),
        gt_lgt_context=_gt_lgt_context(),
        business_subject="CUSTOM-SUBJECT",
    )
    validation = validate_action_commit_packet(packet, root_boundary=root_boundary)

    assert (
        packet["packet_id"]
        == "mock_action_commit_packet:root_outcome:custom_core_identity_v01"
    )
    assert packet["source_root_outcome_id"] == "root_outcome:custom_core_identity_v01"
    assert (
        packet["idempotency_key"]
        == "idem:mock_action_commit_packet:root_outcome:custom_core_identity_v01"
    )
    assert packet["business_subject"] == "CUSTOM-SUBJECT"
    assert validation["accepted"] is True


def test_not_ready_root_boundary_is_rejected() -> None:
    packet = _valid_packet()
    packet["source_root_decision"] = "not_ready"
    root_boundary = _root_boundary(decision="not_ready")

    validation = validate_action_commit_packet(packet, root_boundary=root_boundary)

    assert validation["accepted"] is False
    assert "root_decision_not_ready_for_mock_action" in validation["reasons"]


def test_missing_required_fields_are_rejected() -> None:
    packet = _valid_packet()
    removed_fields = (
        "packet_id",
        "source_root_outcome_id",
        "action_scope",
        "validator_receipts",
        "trace_refs",
        "idempotency_key",
        "expires_at",
    )
    for field in removed_fields:
        packet.pop(field)

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    for field in removed_fields:
        assert f"missing_required_field:{field}" in validation["reasons"]


@pytest.mark.parametrize("created_by", ("bounded_gemini_orchestrator", "gemini"))
def test_packet_from_gemini_is_rejected(created_by: str) -> None:
    packet = _valid_packet()
    packet["created_by"] = created_by

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    assert "packet_created_by_must_be_root_mock_approval_gate" in validation["reasons"]


def test_source_root_decision_mismatch_is_rejected() -> None:
    packet = _valid_packet()
    packet["source_root_decision"] = "not_ready"

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    assert "source_root_decision_must_match_root_boundary" in validation["reasons"]


def test_source_root_outcome_id_mismatch_is_rejected() -> None:
    packet = _valid_packet()
    packet["source_root_outcome_id"] = "root_outcome:wrong"

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    assert "source_root_outcome_id_must_match_root_boundary" in validation["reasons"]


@pytest.mark.parametrize(
    "field",
    (
        "connector_called",
        "payment_executed",
        "shipment_released",
        "bank_api_called",
        "gemini_created_packet",
    ),
)
def test_forbidden_fields_are_rejected(field: str) -> None:
    assert field in ACTION_COMMIT_PACKET_FORBIDDEN_FIELDS
    packet = _valid_packet()
    packet[field] = True

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    assert f"forbidden_packet_field:{field}" in validation["reasons"]


def test_unsupported_action_kind_is_rejected() -> None:
    packet = _valid_packet()
    packet["allowed_action_kinds"] = (
        *packet["allowed_action_kinds"],
        "unsupported_action",
    )

    validation = validate_action_commit_packet(packet, root_boundary=_root_boundary())

    assert validation["accepted"] is False
    assert "unsupported_action_kind" in validation["reasons"]


def test_validator_receipts_cannot_finalize() -> None:
    post_packet = _valid_packet()
    post_packet["validator_receipts"]["post_vv"]["finalizes"] = True
    gt_packet = _valid_packet()
    gt_packet["validator_receipts"]["gt_lgt"]["finalizes"] = True
    root_packet = _valid_packet()
    root_packet["validator_receipts"]["root"]["decision"] = "not_ready"

    post_validation = validate_action_commit_packet(
        post_packet,
        root_boundary=_root_boundary(),
    )
    gt_validation = validate_action_commit_packet(
        gt_packet,
        root_boundary=_root_boundary(),
    )
    root_validation = validate_action_commit_packet(
        root_packet,
        root_boundary=_root_boundary(),
    )

    assert post_validation["accepted"] is False
    assert "post_vv_receipt_must_not_finalize" in post_validation["reasons"]
    assert gt_validation["accepted"] is False
    assert "gt_lgt_receipt_must_not_finalize" in gt_validation["reasons"]
    assert root_validation["accepted"] is False
    assert (
        "root_receipt_decision_must_be_ready_for_mock_action"
        in root_validation["reasons"]
    )


def test_root_mock_approval_preconditions_report_blockers() -> None:
    validation = validate_root_mock_approval_preconditions(
        root_boundary=_root_boundary(decision="not_ready"),
        post_vv_context=_post_vv_context(),
        gt_lgt_context=_gt_lgt_context(),
    )

    assert validation["accepted"] is False
    assert "root_decision_not_ready_for_mock_action" in validation["reasons"]
    assert "legal_hold_not_clear" in validation["reasons"]
    assert "stock_not_available_or_mock_reservable" in validation["reasons"]
