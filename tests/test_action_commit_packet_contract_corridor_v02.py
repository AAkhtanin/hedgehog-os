from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import hedgehog.action_commit_packet_v02 as acp


def _packet(**overrides: object) -> acp.ActionCommitPacketV02:
    packet = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    if not overrides:
        return packet
    return replace(packet, **overrides)


def _scope(**overrides: object) -> acp.PermissionScopeV02:
    values = {
        "allowed_subjects": (acp.SUBJECT_SUPPLIER_A,),
        "forbidden_subjects": (
            acp.SUBJECT_SUPPLIER_B,
            acp.SUBJECT_SHIPMENT_SH_2042,
        ),
        "allowed_actions": (
            acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT,
            acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
        ),
        "forbidden_actions": (
            acp.ACTION_SUPPLIER_B_PAYMENT,
            acp.ACTION_SHIPMENT_RELEASE,
            acp.ACTION_REAL_PAYMENT,
            acp.ACTION_REAL_BANK_TRANSFER,
        ),
        "allowed_adapters": (
            acp.ADAPTER_MOCK_BANK_SANDBOX,
            acp.ADAPTER_BANK_A_MOCK,
        ),
        "forbidden_adapters": (
            acp.ADAPTER_REAL_BANK,
            acp.ADAPTER_REAL_SUPPLIER_API,
            acp.ADAPTER_REAL_WAREHOUSE_API,
        ),
        "payment_slot_ref": "payment_slot:bank_a_mock:inv_2042",
        "creditor_ref": acp.SUBJECT_SUPPLIER_A,
        "amount": "1250.00",
        "currency": "EUR",
    }
    values.update(overrides)
    return acp.PermissionScopeV02(**values)


def _step(
    packet: acp.ActionCommitPacketV02 | None = None,
    **overrides: object,
) -> acp.CorridorStepV01:
    packet = packet or _packet()
    step = acp.build_supplier_a_corridor_step_fixture_v01(packet)
    if not overrides:
        return step
    return replace(step, **overrides)


def _receipt(
    packet: acp.ActionCommitPacketV02 | None = None,
    **overrides: object,
) -> acp.MockReceiptEvidenceV01:
    packet = packet or _packet()
    receipt = acp.build_supplier_a_mock_receipt_evidence_fixture_v01(packet)
    if not overrides:
        return receipt
    return replace(receipt, **overrides)


def test_supplier_a_mock_packet_fixture_validates() -> None:
    packet = _packet()
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is True
    assert reasons == ()
    assert packet.root_created is True
    assert acp.SUBJECT_SUPPLIER_A in packet.scope.allowed_subjects
    assert acp.SUBJECT_SUPPLIER_B in packet.scope.forbidden_subjects
    assert acp.ACTION_SHIPMENT_RELEASE in packet.scope.forbidden_actions
    assert acp.ADAPTER_REAL_BANK in packet.scope.forbidden_adapters
    assert packet.receipt_evidence_only is True
    assert packet.real_world_effects_allowed is False


def test_packet_without_root_rejected() -> None:
    packet = _packet(created_by="semantic_actor", root_created=False)
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is False
    assert acp.REASON_ROOT_ONLY_PACKET_CREATION_REQUIRED in reasons


def test_human_approval_is_evidence_not_packet_creator() -> None:
    missing_ref = _packet(human_approval_ref="")
    valid_missing, reasons_missing = acp.validate_action_commit_packet_v02(missing_ref)

    human_created = _packet(created_by="human_approval_gate")
    valid_human, reasons_human = acp.validate_action_commit_packet_v02(human_created)

    assert valid_missing is False
    assert acp.REASON_MISSING_HUMAN_APPROVAL_REF in reasons_missing
    assert valid_human is False
    assert acp.REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY in reasons_human
    assert acp.REASON_ROOT_ONLY_PACKET_CREATION_REQUIRED in reasons_human


def test_packet_without_scope_ttl_or_idempotency_rejected() -> None:
    missing_scope = _packet(
        scope=_scope(
            allowed_subjects=(),
            allowed_actions=(),
            allowed_adapters=(),
            payment_slot_ref="",
        ),
    )
    invalid_ttl = _packet(ttl=replace(_packet().ttl, ttl_seconds=0))
    missing_idempotency = _packet(idempotency=replace(_packet().idempotency, key=""))

    for packet, reason in (
        (missing_scope, acp.REASON_MISSING_SCOPE),
        (invalid_ttl, acp.REASON_INVALID_TTL),
        (missing_idempotency, acp.REASON_MISSING_IDEMPOTENCY_KEY),
    ):
        valid, reasons = acp.validate_action_commit_packet_v02(packet)
        assert valid is False
        assert reason in reasons


def test_supplier_b_scope_rejected() -> None:
    packet = _packet(
        scope=_scope(
            allowed_subjects=(acp.SUBJECT_SUPPLIER_A, acp.SUBJECT_SUPPLIER_B),
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is False
    assert acp.REASON_SUPPLIER_B_SCOPE_FORBIDDEN in reasons


def test_shipment_release_scope_rejected() -> None:
    packet = _packet(
        scope=_scope(
            allowed_actions=(
                acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
                acp.ACTION_SHIPMENT_RELEASE,
            ),
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is False
    assert acp.REASON_SHIPMENT_RELEASE_FORBIDDEN in reasons


def test_real_bank_or_real_api_adapter_rejected() -> None:
    cases = (
        (
            _packet(scope=_scope(allowed_adapters=(acp.ADAPTER_REAL_BANK,))),
            acp.REASON_REAL_BANK_ADAPTER_FORBIDDEN,
        ),
        (
            _packet(scope=_scope(allowed_adapters=(acp.ADAPTER_REAL_SUPPLIER_API,))),
            acp.REASON_REAL_SUPPLIER_API_FORBIDDEN,
        ),
        (
            _packet(scope=_scope(allowed_adapters=(acp.ADAPTER_REAL_WAREHOUSE_API,))),
            acp.REASON_REAL_WAREHOUSE_API_FORBIDDEN,
        ),
    )

    for packet, reason in cases:
        valid, reasons = acp.validate_action_commit_packet_v02(packet)
        assert valid is False
        assert reason in reasons


def test_packet_adapter_binding_must_be_allowed_by_scope() -> None:
    packet = _packet(
        adapter_binding=replace(_packet().adapter_binding, adapter_id="unknown_mock_adapter"),
    )
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is False
    assert acp.REASON_ADAPTER_BINDING_NOT_ALLOWED_BY_PACKET in reasons

    real_adapter_packet = _packet(
        adapter_binding=replace(
            _packet().adapter_binding,
            adapter_id=acp.ADAPTER_REAL_BANK,
            real_adapter=True,
        ),
    )
    valid_real, reasons_real = acp.validate_action_commit_packet_v02(real_adapter_packet)

    assert valid_real is False
    assert acp.REASON_REAL_BANK_ADAPTER_FORBIDDEN in reasons_real


def test_real_world_effects_allowed_rejected() -> None:
    packet = _packet(real_world_effects_allowed=True)
    valid, reasons = acp.validate_action_commit_packet_v02(packet)

    assert valid is False
    assert acp.REASON_REAL_WORLD_EFFECTS_FORBIDDEN in reasons


def test_corridor_no_post_root_reasoning() -> None:
    corridor = acp.ContractFulfillmentCorridorV01(
        corridor_id="corridor:supplier_a_mock",
        packet_id=_packet().packet_id,
    )
    valid, reasons = acp.validate_corridor_no_post_root_reasoning_v01(corridor)

    llm_corridor = replace(corridor, post_root_llm_reasoning_allowed=True)
    restarted_corridor = replace(corridor, reasoning_restarted_after_root=True)

    valid_llm, reasons_llm = acp.validate_corridor_no_post_root_reasoning_v01(
        llm_corridor,
    )
    valid_restart, reasons_restart = acp.validate_corridor_no_post_root_reasoning_v01(
        restarted_corridor,
    )

    assert valid is True
    assert reasons == ()
    assert valid_llm is False
    assert acp.REASON_NO_POST_ROOT_LLM_REASONING in reasons_llm
    assert valid_restart is False
    assert acp.REASON_REASONING_DOES_NOT_RESTART_AFTER_ROOT in reasons_restart


def test_corridor_step_child_allowed_subset_required() -> None:
    report = acp.validate_corridor_step_against_packet_v01(
        _packet(),
        _step(allowed_subjects=(acp.SUBJECT_SUPPLIER_A, acp.SUBJECT_SUPPLIER_B)),
    )

    assert report.validation_status == acp.STATUS_FAIL_CLOSED
    assert report.return_to_root_required is True
    assert acp.REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT in report.reason_codes
    assert acp.REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT in report.reason_codes


def test_corridor_step_parent_packet_id_must_match_packet() -> None:
    report = acp.validate_corridor_step_against_packet_v01(
        _packet(),
        _step(parent_packet_id="wrong_packet"),
    )

    assert report.validation_status == acp.STATUS_FAIL_CLOSED
    assert report.return_to_root_required is True
    assert acp.REASON_CHILD_PARENT_PACKET_ID_MISMATCH in report.reason_codes


def test_corridor_step_child_forbidden_must_include_parent_forbidden() -> None:
    report = acp.validate_corridor_step_against_packet_v01(
        _packet(),
        _step(
            forbidden_subjects=(acp.SUBJECT_SHIPMENT_SH_2042,),
            forbidden_actions=(acp.ACTION_SHIPMENT_RELEASE,),
        ),
    )

    assert report.validation_status == acp.STATUS_FAIL_CLOSED
    assert (
        acp.REASON_CHILD_FORBIDDEN_DOES_NOT_INCLUDE_PARENT_FORBIDDEN
        in report.reason_codes
    )


def test_corridor_step_ttl_adapter_amount_creditor_payment_slot_idempotency_must_match() -> None:
    packet = _packet()
    cases = (
        (_step(packet, ttl_seconds=packet.ttl.ttl_seconds + 1), acp.REASON_CHILD_TTL_EXCEEDS_PARENT_TTL),
        (_step(packet, adapter_id=acp.ADAPTER_REAL_BANK), acp.REASON_CHILD_ADAPTER_NOT_ALLOWED_BY_PACKET),
        (_step(packet, amount="999.00"), acp.REASON_CHILD_AMOUNT_MISMATCH),
        (_step(packet, creditor_ref="wrong_creditor"), acp.REASON_CHILD_CREDITOR_MISMATCH),
        (_step(packet, payment_slot_ref="wrong_slot"), acp.REASON_CHILD_PAYMENT_SLOT_MISMATCH),
        (_step(packet, idempotency_key="wrong_key"), acp.REASON_CHILD_IDEMPOTENCY_MISMATCH),
    )

    for step, reason in cases:
        report = acp.validate_corridor_step_against_packet_v01(packet, step)
        assert report.validation_status == acp.STATUS_FAIL_CLOSED
        assert report.return_to_root_required is True
        assert reason in report.reason_codes


def test_corridor_step_cannot_create_permission_final_output_or_real_effects() -> None:
    packet = _packet()
    cases = (
        _step(packet, creates_permission=True),
        _step(packet, creates_final_output=True),
        _step(packet, releases_shipment=True),
        _step(packet, executes_real_payment=True),
        _step(packet, calls_real_api=True),
    )

    for step in cases:
        report = acp.validate_corridor_step_against_packet_v01(packet, step)
        assert report.validation_status == acp.STATUS_FAIL_CLOSED
        assert report.return_to_root_required is True
        assert report.authority_expanded is True


def test_receipt_evidence_fixture_validates() -> None:
    packet = _packet()
    receipt = _receipt(packet)
    valid, reasons = acp.validate_mock_receipt_evidence_v01(packet, receipt)

    assert valid is True
    assert reasons == ()
    assert receipt.evidence_only is True
    assert receipt.creates_future_permission is False
    assert receipt.creates_action_permission is False
    assert receipt.creates_final_output is False
    assert receipt.releases_shipment is False
    assert receipt.real_world_effects_count == 0


def test_receipt_wrong_packet_or_adapter_rejected() -> None:
    packet = _packet()
    cases = (
        (_receipt(packet, packet_id="wrong_packet"), acp.REASON_RECEIPT_WRONG_PACKET_ID),
        (_receipt(packet, adapter_id=acp.ADAPTER_REAL_BANK), acp.REASON_RECEIPT_WRONG_ADAPTER),
    )

    for receipt, reason in cases:
        valid, reasons = acp.validate_mock_receipt_evidence_v01(packet, receipt)
        assert valid is False
        assert reason in reasons


def test_receipt_supplier_b_or_shipment_leakage_rejected() -> None:
    packet = _packet()
    cases = (
        (_receipt(packet, subject=acp.SUBJECT_SUPPLIER_B), acp.REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B),
        (_receipt(packet, releases_shipment=True), acp.REASON_RECEIPT_CANNOT_RELEASE_SHIPMENT),
        (_receipt(packet, authorizes_supplier_b=True), acp.REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B),
    )

    for receipt, reason in cases:
        valid, reasons = acp.validate_mock_receipt_evidence_v01(packet, receipt)
        assert valid is False
        assert reason in reasons


def test_receipt_cannot_create_future_permission_or_final_output() -> None:
    packet = _packet()
    cases = (
        (
            _receipt(packet, creates_future_permission=True),
            acp.REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION,
        ),
        (
            _receipt(packet, creates_action_permission=True),
            acp.REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION,
        ),
        (_receipt(packet, creates_final_output=True), acp.REASON_NO_EXPANSION_AFTER_ROOT),
        (_receipt(packet, mutates_packet_scope=True), acp.REASON_NO_EXPANSION_AFTER_ROOT),
        (
            _receipt(packet, creates_production_drs_record=True),
            acp.REASON_NO_EXPANSION_AFTER_ROOT,
        ),
    )

    for receipt, reason in cases:
        valid, reasons = acp.validate_mock_receipt_evidence_v01(packet, receipt)
        assert valid is False
        assert reason in reasons


def test_receipt_rejected_when_source_packet_invalid() -> None:
    expired_packet = _packet(ttl=replace(_packet().ttl, expired=True))
    supplier_b_packet = _packet(
        scope=_scope(
            allowed_subjects=(acp.SUBJECT_SUPPLIER_A, acp.SUBJECT_SUPPLIER_B),
        ),
    )
    adapter_binding_packet = _packet(
        adapter_binding=replace(
            _packet().adapter_binding,
            adapter_id="unknown_mock_adapter",
        ),
    )
    cases = (
        (expired_packet, acp.REASON_EXPIRED_PACKET),
        (supplier_b_packet, acp.REASON_SUPPLIER_B_SCOPE_FORBIDDEN),
        (
            adapter_binding_packet,
            acp.REASON_ADAPTER_BINDING_NOT_ALLOWED_BY_PACKET,
        ),
    )

    for packet, reason in cases:
        valid, reasons = acp.validate_mock_receipt_evidence_v01(
            packet,
            _receipt(packet),
        )
        assert valid is False
        assert reason in reasons


def test_duplicate_packet_and_idempotency_rejected() -> None:
    duplicate_packet = _packet(
        idempotency=replace(_packet().idempotency, duplicate_packet_id=True),
    )
    duplicate_key = _packet(
        idempotency=replace(
            _packet().idempotency,
            duplicate_idempotency_key=True,
            terminal_receipt_already_exists=True,
        ),
    )

    valid_packet, reasons_packet = acp.validate_action_commit_packet_v02(
        duplicate_packet,
    )
    valid_key, reasons_key = acp.validate_action_commit_packet_v02(duplicate_key)

    assert valid_packet is False
    assert acp.REASON_DUPLICATE_PACKET_ID in reasons_packet
    assert valid_key is False
    assert acp.REASON_DUPLICATE_IDEMPOTENCY_KEY in reasons_key


def test_llm_avf_drs_gt_lgt_cannot_create_action_commit_packet() -> None:
    cases = (
        ("llm_actor", acp.REASON_LLM_CANNOT_CREATE_ACTION_COMMIT_PACKET),
        ("avf", acp.REASON_AVF_CANNOT_CREATE_ACTION_COMMIT_PACKET),
        ("drs", acp.REASON_DRS_CANNOT_CREATE_ACTION_COMMIT_PACKET),
        ("gt_lgt", acp.REASON_GT_LGT_CANNOT_CREATE_ACTION_COMMIT_PACKET),
    )

    for created_by, expected_reason in cases:
        valid, reasons = acp.validate_action_commit_packet_v02(
            _packet(created_by=created_by),
        )
        assert valid is False
        assert acp.REASON_ROOT_ONLY_PACKET_CREATION_REQUIRED in reasons
        assert expected_reason in reasons


def test_source_import_boundary() -> None:
    source = Path("hedgehog/action_commit_packet_v02.py").read_text()

    disallowed_imports = (
        "google.genai",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "run_full_wow",
        "run_full_semantic",
        "MockBankSandbox",
        "import real_bank",
        "import real_supplier",
        "import real_warehouse",
        "call_real_bank",
        "call_real_supplier",
        "call_real_warehouse",
        "production " + "ready",
        "public auditor " + "ready",
    )
    for marker in disallowed_imports:
        assert marker not in source


def test_forbidden_phrases_absent() -> None:
    combined_source = "\n".join(
        (
            Path("hedgehog/action_commit_packet_v02.py").read_text(),
            Path("tests/test_action_commit_packet_contract_corridor_v02.py").read_text(),
        ),
    )
    forbidden = (
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

    for phrase in forbidden:
        assert phrase not in combined_source
