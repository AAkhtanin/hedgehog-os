from __future__ import annotations

from typing import Any, Iterable, Mapping


ACTION_COMMIT_PACKET_ALLOWED_ACTION_KINDS = (
    "mock_supplier_payment_review",
    "mock_shipment_reservation_review",
)

ACTION_COMMIT_PACKET_FORBIDDEN_ACTION_KINDS = (
    "real_payment",
    "real_shipment_release",
    "bank_api_call",
    "supplier_api_call",
    "warehouse_api_call",
    "connector_execution",
)

ACTION_COMMIT_PACKET_FORBIDDEN_FIELDS = frozenset(
    {
        "real_payment_executed",
        "real_shipment_released",
        "bank_api_called",
        "warehouse_api_called",
        "supplier_api_called",
        "connector_called",
        "connector_command",
        "payment_executed",
        "shipment_released",
        "final_output_created_by_packet",
        "authority_claimed_by_packet",
        "gemini_created_packet",
    }
)

ACTION_COMMIT_PACKET_REQUIRED_FIELDS = (
    "packet_type",
    "packet_id",
    "created_by",
    "source_root_outcome_id",
    "source_root_decision",
    "business_subject",
    "action_scope",
    "mock_only",
    "real_world_effects_allowed",
    "allowed_action_kinds",
    "forbidden_action_kinds",
    "allowed_future_adapters",
    "forbidden_real_adapters",
    "root_reviewed",
    "root_approved",
    "approval_reason",
    "blockers_checked",
    "validator_receipts",
    "trace_refs",
    "idempotency_key",
    "expires_at",
    "root_final_authority_preserved",
)

ACTION_COMMIT_PACKET_REQUIRED_FAKE_ADAPTERS = (
    "fake_bank_adapter_v0",
    "fake_supplier_adapter_v0",
    "fake_warehouse_adapter_v0",
)

ACTION_COMMIT_PACKET_REQUIRED_FORBIDDEN_REAL_ADAPTERS = (
    "bank_api",
    "supplier_api",
    "warehouse_api",
)

ACTION_COMMIT_PACKET_COUNTER_KEYS = (
    "root_mock_approval_gate_invoked_count",
    "root_mock_approval_granted_count",
    "root_mock_approval_denied_count",
    "root_mock_approval_blocked_by_legal_hold_count",
    "root_mock_approval_blocked_by_stock_shortage_count",
    "action_commit_packet_created_count",
    "mock_action_commit_packet_created_count",
    "action_commit_packet_created_by_root_count",
    "action_commit_packet_created_by_gemini_count",
    "action_commit_packet_created_before_root_count",
    "action_commit_packet_rejected_count",
    "action_commit_packet_mock_only_count",
    "action_commit_packet_real_world_effects_allowed_count",
    "action_commit_packet_used_as_final_output_count",
    "action_commit_packet_executed_connector_count",
    "fake_bank_connector_called_count",
    "fake_supplier_connector_called_count",
    "fake_warehouse_connector_called_count",
    "real_bank_api_called_count",
    "real_supplier_api_called_count",
    "real_warehouse_api_called_count",
    "mock_receipt_created_count",
    "execution_evidence_created_count",
)


def _contains_text(value: Any, forbidden: str) -> bool:
    if isinstance(value, str):
        return forbidden in value
    if isinstance(value, Mapping):
        return any(
            _contains_text(key, forbidden) or _contains_text(item, forbidden)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_text(item, forbidden) for item in value)
    return False


def root_mock_approval_context_default(
    counter_keys: Iterable[str] = ACTION_COMMIT_PACKET_COUNTER_KEYS,
) -> dict[str, Any]:
    return {
        "layer": "Root Mock Approval Gate",
        "gate_enabled": False,
        "invoked": False,
        "approval_granted": False,
        "approval_denied": False,
        "denial_reasons": (),
        "root_decision": None,
        "root_boundary_required": True,
        "created_after_root_boundary": False,
        "legal_hold_clear": False,
        "stock_available_or_mock_reservable": False,
        "post_vv_passed": False,
        "gt_lgt_reviewed": False,
        "Root remains final authority": True,
        "counters": {key: 0 for key in counter_keys},
    }


def action_commit_packet_default() -> dict[str, Any]:
    return {
        "packet_created": False,
        "packet": None,
        "validation": {
            "accepted": False,
            "reasons": (),
        },
        "mock_only": False,
        "real_world_effects_allowed": False,
        "connector_executed": False,
        "mock_receipt_created": False,
        "execution_evidence_created": False,
    }


def build_mock_action_commit_packet(
    *,
    root_boundary: Mapping[str, Any],
    post_vv_context: Mapping[str, Any],
    gt_lgt_context: Mapping[str, Any],
    business_subject: str = "SH-2042 / INV-2042",
    expires_at: str = "2026-06-22T13:00:00+00:00",
) -> dict[str, Any]:
    root_artifact = root_boundary["root_reviewed_semantic_outcome"]
    root_outcome_id = root_artifact["outcome_id"]
    packet_id = f"mock_action_commit_packet:{root_outcome_id}"
    idempotency_key = f"idem:mock_action_commit_packet:{root_outcome_id}"
    return {
        "packet_type": "mock_action_commit_packet",
        "packet_id": packet_id,
        "created_by": "root_mock_approval_gate",
        "source_root_outcome_id": root_outcome_id,
        "source_root_decision": root_boundary["decision"],
        "business_subject": business_subject,
        "action_scope": "local_mock_connector_sandbox",
        "mock_only": True,
        "real_world_effects_allowed": False,
        "allowed_action_kinds": ACTION_COMMIT_PACKET_ALLOWED_ACTION_KINDS,
        "forbidden_action_kinds": ACTION_COMMIT_PACKET_FORBIDDEN_ACTION_KINDS,
        "allowed_future_adapters": ACTION_COMMIT_PACKET_REQUIRED_FAKE_ADAPTERS,
        "forbidden_real_adapters": (
            ACTION_COMMIT_PACKET_REQUIRED_FORBIDDEN_REAL_ADAPTERS
        ),
        "root_reviewed": True,
        "root_approved": True,
        "approval_reason": root_boundary["reason"],
        "blockers_checked": {
            "legal_hold_clear": True,
            "stock_available_or_mock_reservable": True,
            "post_vv_passed": post_vv_context["vv_report_count"] > 0,
            "gt_lgt_reviewed": bool(gt_lgt_context["gt_report_id"]),
        },
        "validator_receipts": {
            "post_vv": {
                "implementation": post_vv_context["implementation"],
                "vv_report_count": post_vv_context["vv_report_count"],
                "finalizes": post_vv_context["finalizes"],
            },
            "gt_lgt": {
                "implementation": gt_lgt_context["implementation"],
                "gt_report_id": gt_lgt_context["gt_report_id"],
                "decision": gt_lgt_context["decision"],
                "finalizes": gt_lgt_context["finalizes"],
            },
            "root": {
                "created_by": root_boundary["created_by"],
                "decision": root_boundary["decision"],
                "root_reviewed": root_boundary["root_reviewed"],
            },
        },
        "trace_refs": (
            {
                "trace_id": "trace:full_semantic_e2e_action_commit_packet_v01",
                "span_id": "root_mock_approval_gate",
                "kind": "mock_action_commit_packet_candidate",
            },
        ),
        "idempotency_key": idempotency_key,
        "expires_at": expires_at,
        "root_final_authority_preserved": True,
    }


def validate_root_mock_approval_preconditions(
    *,
    root_boundary: Mapping[str, Any],
    post_vv_context: Mapping[str, Any],
    gt_lgt_context: Mapping[str, Any],
) -> dict[str, Any]:
    legal_hold_clear = bool(
        (root_boundary.get("blockers_checked") or {}).get("legal_hold_clear")
    )
    stock_available_or_mock_reservable = bool(
        (root_boundary.get("blockers_checked") or {}).get(
            "stock_available_or_mock_reservable"
        )
    )
    post_vv_passed = post_vv_context["vv_report_count"] > 0
    gt_lgt_reviewed = bool(gt_lgt_context["gt_report_id"])

    reasons: list[str] = []
    if root_boundary.get("decision") != "ready_for_mock_action":
        reasons.append("root_decision_not_ready_for_mock_action")
    if not legal_hold_clear:
        reasons.append("legal_hold_not_clear")
    if not stock_available_or_mock_reservable:
        reasons.append("stock_not_available_or_mock_reservable")
    if not post_vv_passed:
        reasons.append("post_vv_required")
    if not gt_lgt_reviewed:
        reasons.append("gt_lgt_required")

    return {
        "accepted": not reasons,
        "reasons": tuple(reasons),
        "root_decision": root_boundary.get("decision"),
        "created_after_root_boundary": bool(root_boundary.get("root_reviewed")),
        "legal_hold_clear": legal_hold_clear,
        "stock_available_or_mock_reservable": stock_available_or_mock_reservable,
        "post_vv_passed": post_vv_passed,
        "gt_lgt_reviewed": gt_lgt_reviewed,
    }


def validate_action_commit_packet(
    packet: Mapping[str, Any],
    *,
    root_boundary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    for field in ACTION_COMMIT_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            reasons.append(f"missing_required_field:{field}")

    if not root_boundary or not root_boundary.get("root_reviewed"):
        reasons.append("root_boundary_required")
    root_decision = root_boundary.get("decision") if root_boundary else None
    if root_decision != "ready_for_mock_action":
        reasons.append("root_decision_not_ready_for_mock_action")
    root_artifact = (
        root_boundary.get("root_reviewed_semantic_outcome") if root_boundary else {}
    ) or {}
    root_outcome_id = root_artifact.get("outcome_id")
    if not root_outcome_id:
        reasons.append("root_outcome_id_required")
    else:
        expected_packet_id = f"mock_action_commit_packet:{root_outcome_id}"
        expected_idempotency_key = f"idem:mock_action_commit_packet:{root_outcome_id}"
        if packet.get("packet_id") != expected_packet_id:
            reasons.append("packet_id_must_derive_from_root_outcome_id")
        if packet.get("idempotency_key") != expected_idempotency_key:
            reasons.append("idempotency_key_must_derive_from_root_outcome_id")
    if packet.get("source_root_decision") != root_decision:
        reasons.append("source_root_decision_must_match_root_boundary")
    if packet.get("source_root_outcome_id") != root_outcome_id:
        reasons.append("source_root_outcome_id_must_match_root_boundary")
    if packet.get("packet_type") != "mock_action_commit_packet":
        reasons.append("packet_type_must_be_mock_action_commit_packet")
    if packet.get("created_by") != "root_mock_approval_gate":
        reasons.append("packet_created_by_must_be_root_mock_approval_gate")
    if packet.get("action_scope") != "local_mock_connector_sandbox":
        reasons.append("action_scope_must_be_local_mock_connector_sandbox")
    if packet.get("mock_only") is not True:
        reasons.append("mock_only_must_be_true")
    if packet.get("real_world_effects_allowed") is not False:
        reasons.append("real_world_effects_must_be_false")
    if packet.get("root_reviewed") is not True or packet.get("root_approved") is not True:
        reasons.append("root_review_and_approval_required")
    if packet.get("root_final_authority_preserved") is not True:
        reasons.append("root_final_authority_must_be_preserved")

    allowed_action_kinds = set(ACTION_COMMIT_PACKET_ALLOWED_ACTION_KINDS)
    requested_kinds = set(packet.get("allowed_action_kinds", ()))
    if not requested_kinds or not requested_kinds.issubset(allowed_action_kinds):
        reasons.append("unsupported_action_kind")
    forbidden_action_kinds = set(packet.get("forbidden_action_kinds", ()))
    if not set(ACTION_COMMIT_PACKET_FORBIDDEN_ACTION_KINDS).issubset(
        forbidden_action_kinds
    ):
        reasons.append("forbidden_action_kinds_incomplete")
    allowed_future_adapters = tuple(packet.get("allowed_future_adapters", ()))
    if not set(ACTION_COMMIT_PACKET_REQUIRED_FAKE_ADAPTERS).issubset(
        set(allowed_future_adapters)
    ):
        reasons.append("allowed_future_adapters_must_be_fake_only")
    real_adapter_markers = ("bank_api", "supplier_api", "warehouse_api")
    if any(
        marker in str(adapter)
        for adapter in allowed_future_adapters
        for marker in real_adapter_markers
    ):
        reasons.append("real_adapter_forbidden_in_allowed_future_adapters")
    forbidden_real_adapters = set(packet.get("forbidden_real_adapters", ()))
    if not set(ACTION_COMMIT_PACKET_REQUIRED_FORBIDDEN_REAL_ADAPTERS).issubset(
        forbidden_real_adapters
    ):
        reasons.append("forbidden_real_adapters_incomplete")

    blockers = packet.get("blockers_checked") or {}
    for blocker in (
        "legal_hold_clear",
        "stock_available_or_mock_reservable",
        "post_vv_passed",
        "gt_lgt_reviewed",
    ):
        if blockers.get(blocker) is not True:
            reasons.append(f"blocker_check_failed:{blocker}")

    validator_receipts = packet.get("validator_receipts") or {}
    for receipt in ("post_vv", "gt_lgt", "root"):
        if receipt not in validator_receipts:
            reasons.append(f"validator_receipt_missing:{receipt}")
    if (validator_receipts.get("post_vv") or {}).get("finalizes") is not False:
        reasons.append("post_vv_receipt_must_not_finalize")
    if (validator_receipts.get("gt_lgt") or {}).get("finalizes") is not False:
        reasons.append("gt_lgt_receipt_must_not_finalize")
    if (
        (validator_receipts.get("root") or {}).get("decision")
        != "ready_for_mock_action"
    ):
        reasons.append("root_receipt_decision_must_be_ready_for_mock_action")

    present_forbidden = [
        key
        for key in ACTION_COMMIT_PACKET_FORBIDDEN_FIELDS
        if key in packet
    ]
    if present_forbidden:
        reasons.extend(f"forbidden_packet_field:{key}" for key in present_forbidden)
    if _contains_text(packet, "connector_command"):
        reasons.append("connector_command_forbidden")
    if _contains_text(packet, "payment_executed"):
        reasons.append("payment_execution_field_forbidden")
    if _contains_text(packet, "shipment_released"):
        reasons.append("shipment_release_field_forbidden")
    if _contains_text(packet, "FinalOutput"):
        reasons.append("packet_must_not_create_final_output")

    return {
        "accepted": not reasons,
        "reasons": tuple(reasons),
    }
