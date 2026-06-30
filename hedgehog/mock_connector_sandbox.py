from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from hedgehog.action_commit_packet import validate_action_commit_packet


MOCK_CONNECTOR_SANDBOX_ADAPTERS = (
    "fake_bank_adapter_v0",
    "fake_supplier_adapter_v0",
    "fake_warehouse_adapter_v0",
)

MOCK_CONNECTOR_SANDBOX_COUNTER_KEYS = (
    "mock_connector_sandbox_invoked_count",
    "mock_connector_sandbox_completed_count",
    "mock_connector_sandbox_denied_count",
    "mock_connector_sandbox_requires_packet_count",
    "mock_connector_sandbox_packet_validated_count",
    "mock_connector_sandbox_packet_expired_count",
    "mock_connector_sandbox_rejected_count",
    "mock_connector_sandbox_real_world_effects_blocked_count",
    "mock_connector_sandbox_unknown_adapter_blocked_count",
    "mock_connector_sandbox_duplicate_receipt_blocked_count",
    "mock_connector_sandbox_missing_receipt_blocked_count",
    "mock_connector_receipts_created_count",
    "mock_bank_receipt_created_count",
    "mock_supplier_receipt_created_count",
    "mock_warehouse_receipt_created_count",
    "fake_bank_adapter_invoked_count",
    "fake_supplier_adapter_invoked_count",
    "fake_warehouse_adapter_invoked_count",
    "execution_evidence_validated_count",
    "root_mock_execution_summary_created_count",
)

MOCK_CONNECTOR_SANDBOX_SHARED_COUNTER_KEYS = (
    "fake_bank_connector_called_count",
    "fake_supplier_connector_called_count",
    "fake_warehouse_connector_called_count",
    "mock_receipt_created_count",
    "execution_evidence_created_count",
)

MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS = (
    "api_key",
    "secret",
    "token",
    "password",
    ".tmp",
)

MOCK_RECEIPT_BASE_REQUIRED_FIELDS = (
    "receipt_type",
    "adapter_name",
    "source_packet_id",
    "idempotency_key",
    "business_subject",
    "scenario_time",
    "mock_only",
    "real_world_effects_allowed",
    "status",
    "evidence_kind",
)

MOCK_BANK_RECEIPT_REQUIRED_FIELDS = (
    "bank_api_called",
    "payment_executed",
    "amount_moved",
)

MOCK_SUPPLIER_RECEIPT_REQUIRED_FIELDS = (
    "supplier_api_called",
    "supplier_order_created",
)

MOCK_WAREHOUSE_RECEIPT_REQUIRED_FIELDS = (
    "warehouse_api_called",
    "shipment_released",
    "inventory_reserved",
)

MOCK_EXECUTION_EVIDENCE_REQUIRED_FIELDS = (
    "evidence_type",
    "evidence_id",
    "created_by",
    "source_packet_id",
    "source_root_outcome_id",
    "business_subject",
    "mock_only",
    "real_world_effects_allowed",
    "adapter_receipts",
    "receipt_count",
    "adapter_names",
    "scenario_time",
    "packet_expires_at",
    "packet_not_expired_at_scenario_time",
    "connector_sandbox_completed",
    "real_connector_called",
    "payment_executed",
    "shipment_released",
    "root_final_authority_preserved",
)

AdapterFunction = Callable[[Mapping[str, Any], str, Mapping[str, Any]], Mapping[str, Any] | None]
EvidenceBuilder = Callable[
    [Mapping[str, Any], tuple[Mapping[str, Any], ...], str],
    Mapping[str, Any],
]
ReceiptValidator = Callable[[Mapping[str, Any] | None, Mapping[str, Any], str], Mapping[str, Any]]
EvidenceValidator = Callable[[Mapping[str, Any], Mapping[str, Any], str], Mapping[str, Any]]


def validate_mock_connector_adapter_registry(
    adapter_functions: Mapping[str, AdapterFunction] | None,
) -> dict[str, Any]:
    if adapter_functions is None:
        return {
            "accepted": True,
            "reasons": (),
            "missing_adapters": (),
            "invalid_adapters": (),
        }

    reasons: list[str] = []
    missing_adapters: list[str] = []
    invalid_adapters: list[str] = []
    for adapter_name in MOCK_CONNECTOR_SANDBOX_ADAPTERS:
        if adapter_name not in adapter_functions:
            missing_adapters.append(adapter_name)
            reasons.append(
                f"mock_connector_sandbox_missing_adapter_function:{adapter_name}"
            )
            continue
        if not callable(adapter_functions[adapter_name]):
            invalid_adapters.append(adapter_name)
            reasons.append(
                f"mock_connector_sandbox_invalid_adapter_function:{adapter_name}"
            )

    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
        "missing_adapters": tuple(missing_adapters),
        "invalid_adapters": tuple(invalid_adapters),
    }


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


def mock_connector_sandbox_zero_counters(
    counter_keys: Iterable[str] = MOCK_CONNECTOR_SANDBOX_COUNTER_KEYS,
    shared_counter_keys: Iterable[str] = MOCK_CONNECTOR_SANDBOX_SHARED_COUNTER_KEYS,
) -> dict[str, int]:
    return {key: 0 for key in (*tuple(counter_keys), *tuple(shared_counter_keys))}


def mock_connector_sandbox_context_default(
    *,
    scenario_time: str = "2026-06-22T12:00:00+00:00",
    counter_keys: Iterable[str] = MOCK_CONNECTOR_SANDBOX_COUNTER_KEYS,
    shared_counter_keys: Iterable[str] = MOCK_CONNECTOR_SANDBOX_SHARED_COUNTER_KEYS,
) -> dict[str, Any]:
    return {
        "layer": "Mock Connector Sandbox",
        "gate_enabled": False,
        "invoked": False,
        "completed": False,
        "denied": False,
        "denial_reasons": (),
        "packet_validated": False,
        "scenario_time": scenario_time,
        "adapter_names": (),
        "receipt_count": 0,
        "real_connector_called": False,
        "payment_executed": False,
        "shipment_released": False,
        "Root remains final authority": True,
        "counters": mock_connector_sandbox_zero_counters(
            counter_keys,
            shared_counter_keys,
        ),
    }


def mock_execution_validation_context_default() -> dict[str, Any]:
    return {
        "validated": False,
        "accepted": False,
        "reasons": (),
        "missing_receipt_blocked": False,
        "duplicate_receipt_blocked": False,
        "unknown_adapter_blocked": False,
        "real_world_effects_blocked": False,
    }


def fake_bank_adapter_v0(
    packet: Mapping[str, Any],
    scenario_time: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "receipt_type": "mock_bank_payment_review_receipt",
        "adapter_name": "fake_bank_adapter_v0",
        "source_packet_id": packet["packet_id"],
        "idempotency_key": packet["idempotency_key"],
        "business_subject": context.get("business_subject", packet["business_subject"]),
        "scenario_time": scenario_time,
        "mock_only": True,
        "real_world_effects_allowed": False,
        "bank_api_called": False,
        "payment_executed": False,
        "amount_moved": 0,
        "status": "mock_payment_review_recorded",
        "evidence_kind": "mock_receipt",
    }


def fake_supplier_adapter_v0(
    packet: Mapping[str, Any],
    scenario_time: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "receipt_type": "mock_supplier_confirmation_receipt",
        "adapter_name": "fake_supplier_adapter_v0",
        "source_packet_id": packet["packet_id"],
        "idempotency_key": packet["idempotency_key"],
        "business_subject": context.get("business_subject", packet["business_subject"]),
        "scenario_time": scenario_time,
        "mock_only": True,
        "real_world_effects_allowed": False,
        "supplier_api_called": False,
        "supplier_order_created": False,
        "status": "mock_supplier_review_recorded",
        "evidence_kind": "mock_receipt",
    }


def fake_warehouse_adapter_v0(
    packet: Mapping[str, Any],
    scenario_time: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "receipt_type": "mock_warehouse_reservation_receipt",
        "adapter_name": "fake_warehouse_adapter_v0",
        "source_packet_id": packet["packet_id"],
        "idempotency_key": packet["idempotency_key"],
        "business_subject": context.get("business_subject", packet["business_subject"]),
        "scenario_time": scenario_time,
        "mock_only": True,
        "real_world_effects_allowed": False,
        "warehouse_api_called": False,
        "shipment_released": False,
        "inventory_reserved": "mock_reserved_only",
        "status": "mock_reservation_review_recorded",
        "evidence_kind": "mock_receipt",
    }


def validate_mock_connector_sandbox_packet(
    packet: Mapping[str, Any] | None,
    root_boundary: Mapping[str, Any],
    scenario_time: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    if not packet:
        reasons.append("mock_connector_sandbox_requires_valid_action_commit_packet")
        return {"accepted": False, "reasons": tuple(reasons)}

    packet_validation = validate_action_commit_packet(
        packet,
        root_boundary=root_boundary,
    )
    if not packet_validation["accepted"]:
        reasons.append("mock_connector_sandbox_requires_valid_action_commit_packet")
        reasons.extend(packet_validation["reasons"])
    if packet.get("created_by") != "root_mock_approval_gate":
        reasons.append("packet_must_be_root_created")
    if packet.get("mock_only") is not True:
        reasons.append("packet_mock_only_required")
    if packet.get("real_world_effects_allowed") is not False:
        reasons.append("packet_real_world_effects_forbidden")
    if scenario_time > str(packet.get("expires_at", "")):
        reasons.append("packet_expired_at_scenario_time")
    adapter_names = tuple(packet.get("allowed_future_adapters", ()))
    if set(adapter_names) != set(MOCK_CONNECTOR_SANDBOX_ADAPTERS):
        reasons.append("unknown_adapter")
    if any(
        _contains_text(packet, marker)
        for marker in MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS
    ):
        reasons.append("secret_or_tmp_marker_forbidden")

    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
    }


def validate_mock_receipt(
    receipt: Mapping[str, Any] | None,
    packet: Mapping[str, Any],
    scenario_time: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    if not receipt:
        return {"accepted": False, "reasons": ("missing_receipt",)}
    adapter_name = receipt.get("adapter_name")
    adapter_label = str(adapter_name or "unknown")
    for field in MOCK_RECEIPT_BASE_REQUIRED_FIELDS:
        if field not in receipt:
            reasons.append(
                f"missing_required_receipt_field:{adapter_label}:{field}"
            )
    if adapter_name not in MOCK_CONNECTOR_SANDBOX_ADAPTERS:
        reasons.append("unknown_adapter")
    if receipt.get("source_packet_id") != packet.get("packet_id"):
        reasons.append("receipt_source_packet_id_mismatch")
    if receipt.get("idempotency_key") != packet.get("idempotency_key"):
        reasons.append("receipt_idempotency_key_mismatch")
    if receipt.get("business_subject") != packet.get("business_subject"):
        reasons.append("receipt_business_subject_mismatch")
    if receipt.get("scenario_time") != scenario_time:
        reasons.append("receipt_scenario_time_mismatch")
    if receipt.get("mock_only") is not True:
        reasons.append("receipt_mock_only_required")
    if receipt.get("real_world_effects_allowed") is not False:
        reasons.append("receipt_real_world_effects_forbidden")
    if receipt.get("evidence_kind") != "mock_receipt":
        reasons.append("receipt_evidence_kind_invalid")

    if adapter_name == "fake_bank_adapter_v0":
        for field in MOCK_BANK_RECEIPT_REQUIRED_FIELDS:
            if field not in receipt:
                reasons.append(
                    f"missing_required_receipt_field:{adapter_label}:{field}"
                )
        if receipt.get("receipt_type") != "mock_bank_payment_review_receipt":
            reasons.append("bank_receipt_type_invalid")
        if receipt.get("bank_api_called") is not False:
            reasons.append("receipt_real_action_forbidden:bank_api_called")
        if receipt.get("payment_executed") is not False:
            reasons.append("receipt_real_action_forbidden:payment_executed")
        if receipt.get("amount_moved") != 0:
            reasons.append("bank_receipt_amount_moved_must_be_zero")
        if receipt.get("status") != "mock_payment_review_recorded":
            reasons.append("bank_receipt_status_invalid")
    elif adapter_name == "fake_supplier_adapter_v0":
        for field in MOCK_SUPPLIER_RECEIPT_REQUIRED_FIELDS:
            if field not in receipt:
                reasons.append(
                    f"missing_required_receipt_field:{adapter_label}:{field}"
                )
        if receipt.get("receipt_type") != "mock_supplier_confirmation_receipt":
            reasons.append("supplier_receipt_type_invalid")
        if receipt.get("supplier_api_called") is not False:
            reasons.append("receipt_real_action_forbidden:supplier_api_called")
        if receipt.get("supplier_order_created") is not False:
            reasons.append("receipt_real_action_forbidden:supplier_order_created")
        if receipt.get("status") != "mock_supplier_review_recorded":
            reasons.append("supplier_receipt_status_invalid")
    elif adapter_name == "fake_warehouse_adapter_v0":
        for field in MOCK_WAREHOUSE_RECEIPT_REQUIRED_FIELDS:
            if field not in receipt:
                reasons.append(
                    f"missing_required_receipt_field:{adapter_label}:{field}"
                )
        if receipt.get("receipt_type") != "mock_warehouse_reservation_receipt":
            reasons.append("warehouse_receipt_type_invalid")
        if receipt.get("warehouse_api_called") is not False:
            reasons.append("receipt_real_action_forbidden:warehouse_api_called")
        if receipt.get("shipment_released") is not False:
            reasons.append("receipt_real_action_forbidden:shipment_released")
        if receipt.get("inventory_reserved") != "mock_reserved_only":
            reasons.append("warehouse_receipt_inventory_reserved_invalid")
        if receipt.get("status") != "mock_reservation_review_recorded":
            reasons.append("warehouse_receipt_status_invalid")
    if any(
        _contains_text(receipt, marker)
        for marker in MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS
    ):
        reasons.append("secret_or_tmp_marker_forbidden")
    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
    }


def build_mock_connector_execution_evidence(
    packet: Mapping[str, Any],
    receipts: tuple[Mapping[str, Any], ...],
    scenario_time: str,
) -> dict[str, Any]:
    return {
        "evidence_type": "mock_connector_execution_evidence",
        "evidence_id": f"mock_connector_execution_evidence:{packet['packet_id']}",
        "created_by": "mock_connector_sandbox",
        "source_packet_id": packet["packet_id"],
        "source_root_outcome_id": packet["source_root_outcome_id"],
        "business_subject": packet["business_subject"],
        "mock_only": True,
        "real_world_effects_allowed": False,
        "adapter_receipts": receipts,
        "receipt_count": len(receipts),
        "adapter_names": tuple(receipt.get("adapter_name") for receipt in receipts),
        "scenario_time": scenario_time,
        "packet_expires_at": packet["expires_at"],
        "packet_not_expired_at_scenario_time": scenario_time <= packet["expires_at"],
        "connector_sandbox_completed": True,
        "real_connector_called": False,
        "payment_executed": False,
        "shipment_released": False,
        "root_final_authority_preserved": True,
    }


def validate_mock_connector_execution_evidence(
    evidence: Mapping[str, Any],
    packet: Mapping[str, Any],
    scenario_time: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    receipts = tuple(evidence.get("adapter_receipts", ()))
    adapter_names = tuple(evidence.get("adapter_names", ()))
    expected_adapters = set(MOCK_CONNECTOR_SANDBOX_ADAPTERS)
    adapter_set = set(adapter_names)

    for field in MOCK_EXECUTION_EVIDENCE_REQUIRED_FIELDS:
        if field not in evidence:
            reasons.append(f"missing_required_execution_evidence_field:{field}")
    if evidence.get("evidence_type") != "mock_connector_execution_evidence":
        reasons.append("execution_evidence_type_invalid")
    if evidence.get("created_by") != "mock_connector_sandbox":
        reasons.append("execution_evidence_creator_invalid")
    if evidence.get("source_packet_id") != packet.get("packet_id"):
        reasons.append("execution_evidence_source_packet_mismatch")
    if evidence.get("source_root_outcome_id") != packet.get("source_root_outcome_id"):
        reasons.append("execution_evidence_source_root_outcome_mismatch")
    if evidence.get("business_subject") != packet.get("business_subject"):
        reasons.append("execution_evidence_business_subject_mismatch")
    if evidence.get("packet_expires_at") != packet.get("expires_at"):
        reasons.append("execution_evidence_packet_expiry_mismatch")
    if evidence.get("scenario_time") != scenario_time:
        reasons.append("execution_evidence_scenario_time_mismatch")
    if evidence.get("mock_only") is not True:
        reasons.append("execution_evidence_mock_only_required")
    if evidence.get("real_world_effects_allowed") is not False:
        reasons.append("execution_evidence_real_world_effects_forbidden")
    if evidence.get("packet_not_expired_at_scenario_time") is not True:
        reasons.append("packet_expired_at_scenario_time")
    if evidence.get("connector_sandbox_completed") is not True:
        reasons.append("execution_evidence_connector_sandbox_completed_required")
    if evidence.get("real_connector_called") is not False:
        reasons.append("real_connector_marker_forbidden")
    if evidence.get("payment_executed") is not False:
        reasons.append("payment_execution_forbidden")
    if evidence.get("shipment_released") is not False:
        reasons.append("shipment_release_forbidden")
    if evidence.get("root_final_authority_preserved") is not True:
        reasons.append("execution_evidence_root_final_authority_required")
    if len(adapter_names) != len(set(adapter_names)):
        reasons.append("duplicate_receipt")
    if adapter_names != MOCK_CONNECTOR_SANDBOX_ADAPTERS:
        reasons.append("adapter_names_must_match_mock_connector_sandbox_adapters")
    if adapter_set != expected_adapters:
        if not expected_adapters.issubset(adapter_set):
            reasons.append("missing_receipt")
        if adapter_set - expected_adapters:
            reasons.append("unknown_adapter")
    if evidence.get("receipt_count") != len(MOCK_CONNECTOR_SANDBOX_ADAPTERS):
        reasons.append("missing_receipt")

    for receipt in receipts:
        receipt_validation = validate_mock_receipt(receipt, packet, scenario_time)
        if not receipt_validation["accepted"]:
            reasons.extend(receipt_validation["reasons"])
    if any(
        _contains_text(evidence, marker)
        for marker in MOCK_CONNECTOR_SANDBOX_SECRET_MARKERS
    ):
        reasons.append("secret_or_tmp_marker_forbidden")

    return {
        "accepted": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
    }


def root_mock_execution_summary(
    packet: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "summary_type": "root_mock_execution_summary",
        "created_by": "root_mock_execution_summary_boundary",
        "source_packet_id": packet["packet_id"],
        "source_execution_evidence_id": evidence["evidence_id"],
        "business_subject": packet["business_subject"],
        "receipt_count": evidence["receipt_count"],
        "mock_only": True,
        "real_world_effects_allowed": False,
        "real_actions_executed": False,
        "payment_executed": False,
        "shipment_released": False,
        "connector_called": False,
        "root_final_authority_preserved": True,
        "decision": "mock_execution_recorded",
        "reason": (
            "local fake connector receipts recorded; no real-world action occurred"
        ),
    }


def sandbox_failure_result(
    sandbox_context: dict[str, Any],
    validation_context: dict[str, Any],
    counters: dict[str, int],
    reasons: tuple[str, ...],
) -> dict[str, Any]:
    counters["mock_connector_sandbox_denied_count"] = 1
    counters["mock_connector_sandbox_rejected_count"] = 1
    if "mock_connector_sandbox_requires_valid_action_commit_packet" in reasons:
        counters["mock_connector_sandbox_requires_packet_count"] = 1
    if "packet_expired_at_scenario_time" in reasons:
        counters["mock_connector_sandbox_packet_expired_count"] = 1
    if any("real_world_effects" in reason for reason in reasons):
        counters["mock_connector_sandbox_real_world_effects_blocked_count"] = 1
    if "unknown_adapter" in reasons:
        counters["mock_connector_sandbox_unknown_adapter_blocked_count"] = 1
    if "duplicate_receipt" in reasons:
        counters["mock_connector_sandbox_duplicate_receipt_blocked_count"] = 1
    if "missing_receipt" in reasons or any(
        reason.startswith("missing_required_receipt_field:")
        or reason.startswith("missing_required_execution_evidence_field:")
        for reason in reasons
    ):
        counters["mock_connector_sandbox_missing_receipt_blocked_count"] = 1
    sandbox_context.update(
        {
            "denied": True,
            "denial_reasons": reasons,
            "counters": counters,
        }
    )
    validation_context.update(
        {
            "validated": True,
            "accepted": False,
            "reasons": reasons,
            "missing_receipt_blocked": "missing_receipt" in reasons
            or any(
                reason.startswith("missing_required_receipt_field:")
                or reason.startswith("missing_required_execution_evidence_field:")
                for reason in reasons
            ),
            "duplicate_receipt_blocked": "duplicate_receipt" in reasons,
            "unknown_adapter_blocked": "unknown_adapter" in reasons,
            "real_world_effects_blocked": any(
                "real_world_effects" in reason for reason in reasons
            ),
        }
    )
    return {
        "mock_connector_sandbox_context": sandbox_context,
        "mock_connector_receipts": (),
        "execution_evidence": {},
        "mock_execution_validation_context": validation_context,
        "root_mock_execution_summary_context": {},
        "fail_closed": True,
        "validation_errors": reasons,
    }


def run_mock_connector_sandbox(
    *,
    gate_enabled: bool,
    root_boundary: Mapping[str, Any],
    action_commit_packet_context: Mapping[str, Any],
    action_commit_packet: Mapping[str, Any] | None,
    supplier_context: Mapping[str, Any],
    scenario_time: str,
    create_root_summary: bool = True,
    adapter_functions: Mapping[str, AdapterFunction] | None = None,
    evidence_builder: EvidenceBuilder = build_mock_connector_execution_evidence,
    evidence_validator: EvidenceValidator = validate_mock_connector_execution_evidence,
) -> dict[str, Any]:
    sandbox_context = mock_connector_sandbox_context_default(
        scenario_time=scenario_time,
    )
    validation_context = mock_execution_validation_context_default()
    if not gate_enabled:
        return {
            "mock_connector_sandbox_context": sandbox_context,
            "mock_connector_receipts": (),
            "execution_evidence": {},
            "mock_execution_validation_context": validation_context,
            "root_mock_execution_summary_context": {},
            "fail_closed": False,
            "validation_errors": (),
        }

    counters = mock_connector_sandbox_zero_counters()
    counters["mock_connector_sandbox_invoked_count"] = 1
    sandbox_context.update(
        {
            "gate_enabled": True,
            "invoked": True,
            "scenario_time": scenario_time,
        }
    )
    packet = dict(action_commit_packet or {})
    packet_accepted = (
        action_commit_packet_context.get("packet_created") is True
        and (action_commit_packet_context.get("validation") or {}).get("accepted")
        is True
        and bool(packet)
    )
    if not packet_accepted:
        reasons = ("mock_connector_sandbox_requires_valid_action_commit_packet",)
        return sandbox_failure_result(
            sandbox_context,
            validation_context,
            counters,
            reasons,
        )

    packet_validation = validate_mock_connector_sandbox_packet(
        packet,
        root_boundary,
        scenario_time,
    )
    if not packet_validation["accepted"]:
        return sandbox_failure_result(
            sandbox_context,
            validation_context,
            counters,
            tuple(packet_validation["reasons"]),
        )

    counters["mock_connector_sandbox_packet_validated_count"] = 1
    adapter_registry_validation = validate_mock_connector_adapter_registry(
        adapter_functions,
    )
    if not adapter_registry_validation["accepted"]:
        return sandbox_failure_result(
            sandbox_context,
            validation_context,
            counters,
            tuple(adapter_registry_validation["reasons"]),
        )

    context = {
        "business_subject": packet["business_subject"],
        "supplier_payment_context_summary": {
            "mock_ready_fixture": bool(supplier_context.get("mock_ready_fixture")),
            "legal_hold_present": bool(supplier_context.get("legal_hold_present")),
            "water_filter_shortage": bool(supplier_context.get("water_filter_shortage")),
        },
    }
    adapters = dict(
        adapter_functions
        or {
            "fake_bank_adapter_v0": fake_bank_adapter_v0,
            "fake_supplier_adapter_v0": fake_supplier_adapter_v0,
            "fake_warehouse_adapter_v0": fake_warehouse_adapter_v0,
        }
    )
    receipts: list[Mapping[str, Any]] = []
    for adapter_name in MOCK_CONNECTOR_SANDBOX_ADAPTERS:
        counters[f"{adapter_name.removesuffix('_v0')}_invoked_count"] = 1
        receipt = adapters[adapter_name](packet, scenario_time, context)
        if receipt:
            receipts.append(receipt)

    receipt_tuple = tuple(receipts)
    evidence = dict(evidence_builder(packet, receipt_tuple, scenario_time))
    evidence_validation = evidence_validator(evidence, packet, scenario_time)
    if not evidence_validation["accepted"]:
        return sandbox_failure_result(
            sandbox_context,
            validation_context,
            counters,
            tuple(evidence_validation["reasons"]),
        )

    counters["mock_connector_sandbox_completed_count"] = 1
    counters["fake_bank_connector_called_count"] = 1
    counters["fake_supplier_connector_called_count"] = 1
    counters["fake_warehouse_connector_called_count"] = 1
    counters["mock_bank_receipt_created_count"] = 1
    counters["mock_supplier_receipt_created_count"] = 1
    counters["mock_warehouse_receipt_created_count"] = 1
    counters["mock_connector_receipts_created_count"] = 3
    counters["mock_receipt_created_count"] = 3
    counters["execution_evidence_created_count"] = 1
    counters["execution_evidence_validated_count"] = 1
    summary = {}
    if create_root_summary:
        counters["root_mock_execution_summary_created_count"] = 1
        summary = root_mock_execution_summary(packet, evidence)
    sandbox_context.update(
        {
            "completed": True,
            "packet_validated": True,
            "adapter_names": evidence["adapter_names"],
            "receipt_count": evidence["receipt_count"],
            "counters": counters,
        }
    )
    validation_context.update(
        {
            "validated": True,
            "accepted": True,
            "reasons": (),
            "execution_evidence_validated": True,
        }
    )
    return {
        "mock_connector_sandbox_context": sandbox_context,
        "mock_connector_receipts": receipt_tuple,
        "execution_evidence": evidence,
        "mock_execution_validation_context": validation_context,
        "root_mock_execution_summary_context": summary,
        "fail_closed": False,
        "validation_errors": (),
    }
